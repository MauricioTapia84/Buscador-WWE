import os
import re
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, FastAPI, HTTPException

app = FastAPI(title="WrestlingData API")
router = APIRouter()


def _default_data_root() -> Path:
    candidates = [
        Path("/app/data"),
        Path(__file__).resolve().parents[1] / "data",
        Path(__file__).resolve().parent / "data",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


DATA_ROOT = _default_data_root()
DEFAULT_PROCESSED_DIR = DATA_ROOT / "processed"
DEFAULT_RAW_DIR = DATA_ROOT / "raw"
PROCESSED_DIR = Path(os.getenv("DATA_PROCESSED_DIR", str(DEFAULT_PROCESSED_DIR)))
RAW_DIR = Path(os.getenv("DATA_RAW_DIR", str(DEFAULT_RAW_DIR)))


def _default_analytics(*, data_available: bool, reason: str | None = None) -> dict:
    return {
        "total_matches": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0.0,
        "most_common_match_type": None,
        "data_available": data_available,
        "source": "matches.csv",
        "reason": reason,
    }


def _slugify(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9 ]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def _clean_value(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    try:
        missing = pd.isna(value)
        if isinstance(missing, bool) and missing:
            return None
    except Exception:
        pass
    return value


def _first_non_empty(*values):
    for value in values:
        cleaned = _clean_value(value)
        if cleaned is None:
            continue
        if isinstance(cleaned, str) and not cleaned.strip():
            continue
        return cleaned
    return None


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _read_catalog(candidates: list[str]) -> pd.DataFrame:
    for candidate in candidates:
        df = _read_csv(PROCESSED_DIR / candidate)
        if not df.empty:
            return df
    return pd.DataFrame()


def _read_wrestler_catalog_sources() -> pd.DataFrame:
    frames = []
    candidates = [
        ("catalog", "wrestlers.csv"),
        ("thesportsdb", "wrestlers_thesportsdb.csv"),
        ("wikipedia", "wrestlers_enriched.csv"),
        ("extracted", "wrestlers_extracted.csv"),
    ]
    for source_name, candidate in candidates:
        frame = _read_csv(PROCESSED_DIR / candidate)
        if frame.empty:
            continue
        frame = frame.copy()
        if "source" in frame.columns:
            frame["source"] = frame["source"].fillna(source_name)
        else:
            frame["source"] = source_name
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


def _normalize_wrestlers_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "canonical_name" not in out.columns:
        out["canonical_name"] = out.get("name")
    if "name" not in out.columns:
        out["name"] = out.get("canonical_name")
    if "name_slug" not in out.columns:
        out["name_slug"] = out["name"].map(_slugify)
    else:
        out["name_slug"] = out["name_slug"].fillna(out["name"]).map(_slugify)
    out["display_name"] = out["canonical_name"].fillna(out["name"])
    if "biography" in out.columns:
        out["bio"] = out["biography"]
    elif "description" in out.columns:
        out["bio"] = out["description"]
    else:
        out["bio"] = None
    if "extract" in out.columns and "bio" in out.columns:
        out["bio"] = out["bio"].fillna(out["extract"])
    return out


def _normalize_titles_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "holder" not in out.columns and "champion_name" in out.columns:
        out["holder"] = out["champion_name"]
    if "champion_name" not in out.columns and "holder" in out.columns:
        out["champion_name"] = out["holder"]
    if "holder_slug" not in out.columns:
        out["holder_slug"] = out["holder"].map(_slugify)
    else:
        out["holder_slug"] = out["holder_slug"].fillna(out["holder"]).map(_slugify)
    for column in ["won_date", "start_date", "end_date"]:
        if column in out.columns:
            out[column] = pd.to_datetime(out[column], errors="coerce")
    return out


def _enrich_titles_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = _normalize_titles_frame(df)
    if out.empty:
        return out

    if "title_slug" not in out.columns:
        out["title_slug"] = out.get("title", pd.Series(dtype="object")).map(_slugify)
    else:
        out["title_slug"] = out["title_slug"].fillna(out.get("title")).map(_slugify)

    if "event_date" not in out.columns:
        if "start_date" in out.columns:
            out["event_date"] = out["start_date"]
        elif "won_date" in out.columns:
            out["event_date"] = out["won_date"]
        else:
            out["event_date"] = pd.NaT

    sort_columns = [
        column
        for column in ["title_slug", "start_date", "won_date", "overall_reign", "champion_reign_number"]
        if column in out.columns
    ]
    if sort_columns:
        out = out.sort_values(sort_columns, na_position="last").reset_index(drop=True)

    if "overall_reign" not in out.columns:
        out["overall_reign"] = pd.NA
    if "champion_reign_number" not in out.columns:
        out["champion_reign_number"] = pd.NA

    for title_slug, indexes in out.groupby("title_slug", dropna=False).groups.items():
        if not title_slug:
            continue
        title_indexes = list(indexes)
        previous_holders = out.loc[title_indexes, "holder"].shift(1)
        next_holders = out.loc[title_indexes, "holder"].shift(-1)
        next_starts = out.loc[title_indexes, "start_date"].shift(-1) if "start_date" in out.columns else pd.Series(index=title_indexes, dtype="datetime64[ns]")
        inferred_end = out.loc[title_indexes, "end_date"].copy() if "end_date" in out.columns else pd.Series(index=title_indexes, dtype="datetime64[ns]")

        if "end_date" not in out.columns:
            out["end_date"] = pd.NaT
        end_missing = out.loc[title_indexes, "end_date"].isna()
        inferred_end = out.loc[title_indexes, "end_date"].where(~end_missing, next_starts)
        out.loc[title_indexes, "end_date"] = inferred_end
        out.loc[title_indexes, "end_date_inferred"] = end_missing & next_starts.notna()
        out.loc[title_indexes, "previous_champion"] = previous_holders.values
        out.loc[title_indexes, "next_champion"] = next_holders.values
        out.loc[title_indexes, "defeated_for_title"] = previous_holders.values
        out.loc[title_indexes, "lost_title_to"] = next_holders.values
        out.loc[title_indexes, "title_lineage_position"] = range(1, len(title_indexes) + 1)

    if "end_date_inferred" not in out.columns:
        out["end_date_inferred"] = False

    return out


def _normalize_matches_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    rename_map = {
        "Winner": "winner",
        "Loser": "loser",
        "MatchType": "match_type",
        "Event": "event_name",
        "EventDate": "event_date",
    }
    out = out.rename(columns={src: dst for src, dst in rename_map.items() if src in out.columns and dst not in out.columns})
    if "winner" not in out.columns:
        out["winner"] = None
    if "loser" not in out.columns:
        out["loser"] = None
    if "winner_slug" not in out.columns:
        out["winner_slug"] = out["winner"].map(_slugify)
    else:
        out["winner_slug"] = out["winner_slug"].fillna(out["winner"]).map(_slugify)
    if "loser_slug" not in out.columns:
        out["loser_slug"] = out["loser"].map(_slugify)
    else:
        out["loser_slug"] = out["loser_slug"].fillna(out["loser"]).map(_slugify)
    return out


def _serialize_records(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    records = []
    for record in df.to_dict(orient="records"):
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                cleaned[key] = None if pd.isna(value) else value.date().isoformat()
            else:
                cleaned[key] = _clean_value(value)
        records.append(cleaned)
    return records


def _load_wrestlers() -> pd.DataFrame:
    base = _read_wrestler_catalog_sources()
    titles = _load_titles()
    matches = _load_matches()

    wrestlers = _normalize_wrestlers_frame(base)
    if not wrestlers.empty:
        wrestler_rows = []
        source_rank = {"thesportsdb": 0, "wikipedia": 1, "catalog": 2, "extracted": 3}
        for slug, group in wrestlers.groupby("name_slug", dropna=False):
            if not slug:
                continue
            ordered = group.assign(
                source_rank=group["source"].map(source_rank).fillna(9)
            ).sort_values("source_rank")
            merged = {"name_slug": slug}
            for column in ordered.columns:
                if column == "source_rank":
                    continue
                merged[column] = _first_non_empty(*ordered[column].tolist())
            wrestler_rows.append(merged)
        wrestlers = pd.DataFrame(wrestler_rows) if wrestler_rows else pd.DataFrame()

    existing_slugs = set(wrestlers.get("name_slug", pd.Series(dtype="object")).dropna().tolist()) if not wrestlers.empty else set()

    supplemental_rows = []
    if not titles.empty:
        titles = _normalize_titles_frame(titles)
        for holder, holder_slug in titles[["holder", "holder_slug"]].drop_duplicates().itertuples(index=False):
            if holder_slug and holder_slug not in existing_slugs:
                supplemental_rows.append({"name": holder, "canonical_name": holder, "name_slug": holder_slug})
                existing_slugs.add(holder_slug)

    if not matches.empty:
        matches = _normalize_matches_frame(matches)
        for column in [("winner", "winner_slug"), ("loser", "loser_slug")]:
            source_col, slug_col = column
            if source_col not in matches.columns:
                continue
            for name, slug in matches[[source_col, slug_col]].drop_duplicates().itertuples(index=False):
                if slug and slug not in existing_slugs:
                    supplemental_rows.append({"name": name, "canonical_name": name, "name_slug": slug})
                    existing_slugs.add(slug)

    if supplemental_rows:
        wrestlers = pd.concat([wrestlers, pd.DataFrame(supplemental_rows)], ignore_index=True, sort=False)

    title_history = {}
    if not titles.empty:
        titles = _enrich_titles_frame(titles)
        for slug, group in titles.groupby("holder_slug", dropna=False):
            if not slug:
                continue
            sort_column = "start_date" if "start_date" in group.columns else "won_date" if "won_date" in group.columns else None
            ordered = group.sort_values(sort_column, na_position="last") if sort_column else group
            title_history[slug] = _serialize_records(
                ordered[
                    [
                        column
                        for column in [
                            "title",
                            "title_slug",
                            "champion_name",
                            "start_date",
                            "end_date",
                            "end_date_inferred",
                            "event_name",
                            "event_date",
                            "won_date",
                            "location",
                            "reign_days",
                            "days_recognized",
                            "era",
                            "notes",
                            "overall_reign",
                            "champion_reign_number",
                            "previous_champion",
                            "next_champion",
                            "defeated_for_title",
                            "lost_title_to",
                            "title_lineage_position",
                        ]
                        if column in ordered.columns
                    ]
                ]
            )

    stats_by_slug = {}
    matches_available = not matches.empty
    if not matches.empty:
        matches = _normalize_matches_frame(matches)
        wins = matches[matches["winner_slug"] != ""].groupby("winner_slug").size().to_dict()
        losses = matches[matches["loser_slug"] != ""].groupby("loser_slug").size().to_dict()

        stipulations = {}
        if "match_type" in matches.columns:
            for slug, group in matches.groupby("winner_slug"):
                if slug:
                    most_common = group["match_type"].dropna().astype(str).str.strip()
                    if not most_common.empty:
                        stipulations.setdefault(slug, most_common.mode().iloc[0])
            for slug, group in matches.groupby("loser_slug"):
                if slug and slug not in stipulations:
                    most_common = group["match_type"].dropna().astype(str).str.strip()
                    if not most_common.empty:
                        stipulations[slug] = most_common.mode().iloc[0]

        all_slugs = set(wins) | set(losses)
        for slug in all_slugs:
            total_wins = int(wins.get(slug, 0))
            total_losses = int(losses.get(slug, 0))
            total_matches = total_wins + total_losses
            stats_by_slug[slug] = {
                "total_matches": total_matches,
                "wins": total_wins,
                "losses": total_losses,
                "win_rate": round((total_wins / total_matches) * 100, 2) if total_matches else 0.0,
                "most_common_match_type": stipulations.get(slug),
                "data_available": True,
                "source": "matches.csv",
                "reason": None,
            }

    records = []
    for record in _serialize_records(wrestlers):
        slug = record.get("name_slug") or _slugify(record.get("name"))
        if matches_available:
            stats = stats_by_slug.get(slug, _default_analytics(data_available=True))
        else:
            stats = _default_analytics(
                data_available=False,
                reason="No se encontró un dataset de combates en data/raw, por eso no se pudieron calcular métricas Kaggle.",
            )
        history = title_history.get(slug, [])
        record["artist_name"] = record.get("canonical_name") or record.get("name")
        record["biography"] = record.get("bio") or record.get("description") or record.get("extract")
        record["birth_date"] = record.get("birth_date") or record.get("date_born")
        record["title_history"] = history
        record["titles_won"] = len(history)
        record["analytics"] = stats
        records.append(record)

    return pd.DataFrame(records)


def _load_titles() -> pd.DataFrame:
    return _read_catalog(["titles.csv", "titles_extracted.csv"])


def _load_matches() -> pd.DataFrame:
    return _read_catalog(["matches.csv", "matches_normalized.csv"])


@router.get("/wrestlers")
def list_wrestlers(source: Optional[str] = None):
    wrestlers = _load_wrestlers()
    if source and not wrestlers.empty and "source" in wrestlers.columns:
        wrestlers = wrestlers[wrestlers["source"].astype(str).str.lower() == source.lower()]
    return _serialize_records(wrestlers)


@router.get("/titles")
def list_titles():
    titles = _enrich_titles_frame(_load_titles())
    wrestlers = _load_wrestlers()
    if titles.empty:
        return []

    if not wrestlers.empty:
        enrich_columns = [
            column
            for column in ["name_slug", "artist_name", "real_name", "image_url", "biography", "height", "weight", "birth_date"]
            if column in wrestlers.columns
        ]
        titles = titles.merge(
            wrestlers[enrich_columns].rename(columns={"name_slug": "holder_slug"}),
            on="holder_slug",
            how="left",
        )

    return _serialize_records(titles)


@router.get("/wrestlers/{wrestler_id}")
def get_wrestler(wrestler_id: int):
    for wrestler in list_wrestlers():
        if str(wrestler.get("id")) == str(wrestler_id):
            return wrestler
    raise HTTPException(status_code=404, detail="Wrestler not found")


@router.get("/titles/{title_id}")
def get_title(title_id: int):
    for title in list_titles():
        if str(title.get("id")) == str(title_id):
            return title
    raise HTTPException(status_code=404, detail="Title not found")


@router.get("/search")
def search(q: Optional[str] = None):
    if not q:
        return {"wrestlers": list_wrestlers(), "titles": list_titles()}

    query = q.lower().strip()
    wrestler_hits = []
    for wrestler in list_wrestlers():
        searchable = " ".join(
            str(wrestler.get(field, "") or "")
            for field in ["artist_name", "canonical_name", "name", "real_name", "name_slug"]
        ).lower()
        if query in searchable:
            wrestler_hits.append(wrestler)

    title_hits = []
    for title in list_titles():
        searchable = " ".join(
            str(title.get(field, "") or "")
            for field in ["title", "holder", "champion_name", "event_name"]
        ).lower()
        if query in searchable:
            title_hits.append(title)

    return {"wrestlers": wrestler_hits, "titles": title_hits}


@router.get("/matches")
def list_matches():
    return _serialize_records(_normalize_matches_frame(_load_matches()))


@router.get("/health")
def health():
    return {
        "status": "ok",
        "processed_dir": str(PROCESSED_DIR),
        "raw_dir": str(RAW_DIR),
    }

from pydantic import BaseModel
import joblib

class PredictRequest(BaseModel):
    total_wins: float
    total_losses: float
    total_matches: float
    win_rate: float

@router.post("/predict")
def predict_champion(req: PredictRequest):
    model_path = _default_data_root().parent / "models" / "champion_predictor.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=503, detail="El modelo no ha sido entrenado aún.")
    
    model = joblib.load(model_path)
    X = pd.DataFrame([req.dict()])
    
    prob = model.predict_proba(X)[0][1] if hasattr(model, 'predict_proba') else 0.0
    pred = model.predict(X)[0]
    
    return {
        "is_champion_prediction": int(pred),
        "probability_percent": round(prob * 100, 2)
    }

@router.get("/stats")
def get_clean_stats():
    # Return the clean unified dataset created by unify.py
    path = PROCESSED_DIR / "wrestling_clean.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    return df.to_dict(orient="records")

app.include_router(router)
