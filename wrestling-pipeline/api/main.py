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


_cached_wrestlers_df = None
_cached_wrestlers_records = None
_cached_titles_records = None
_cached_matches_records = None
_last_mtimes = {}


def _get_processed_files_mtimes() -> dict[str, float]:
    files = [
        "wrestlers.csv",
        "wrestlers_thesportsdb.csv",
        "wrestlers_enriched.csv",
        "wrestlers_extracted.csv",
        "titles.csv",
        "titles_extracted.csv",
        "matches.csv",
        "matches_normalized.csv",
    ]
    mtimes = {}
    for filename in files:
        path = PROCESSED_DIR / filename
        if path.exists():
            mtimes[filename] = os.path.getmtime(path)
        else:
            mtimes[filename] = 0.0
    return mtimes


def _check_and_refresh_cache():
    global _cached_wrestlers_df, _cached_wrestlers_records, _cached_titles_records, _cached_matches_records, _last_mtimes
    current_mtimes = _get_processed_files_mtimes()
    if _cached_wrestlers_df is None or current_mtimes != _last_mtimes:
        _cached_wrestlers_df = None
        _cached_wrestlers_records = None
        _cached_titles_records = None
        _cached_matches_records = None
        _last_mtimes = current_mtimes


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
        return pd.read_csv(path, low_memory=False)
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
    global _cached_wrestlers_df
    _check_and_refresh_cache()
    if _cached_wrestlers_df is not None:
        return _cached_wrestlers_df

    base = _read_wrestler_catalog_sources()
    titles = _load_titles()
    matches = _load_matches()

    wrestlers = _normalize_wrestlers_frame(base)
    if not wrestlers.empty:
        source_rank = {"thesportsdb": 0, "wikipedia": 1, "catalog": 2, "extracted": 3}
        wrestlers = wrestlers.copy()
        for col in wrestlers.columns:
            if wrestlers[col].dtype == object:
                wrestlers[col] = wrestlers[col].apply(lambda x: None if (isinstance(x, str) and not x.strip()) else _clean_value(x))

        wrestlers["source_rank"] = wrestlers["source"].map(source_rank).fillna(9)
        wrestlers = wrestlers.sort_values("source_rank")
        wrestlers = wrestlers.groupby("name_slug", as_index=False).first()

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
        titles = _normalize_titles_frame(titles)
        for slug, group in titles.groupby("holder_slug", dropna=False):
            if not slug:
                continue
            sort_column = "start_date" if "start_date" in group.columns else "won_date" if "won_date" in group.columns else None
            ordered = group.sort_values(sort_column, na_position="last") if sort_column else group
            title_history[slug] = _serialize_records(
                ordered[
                    [column for column in ["title", "champion_name", "start_date", "end_date", "event_name", "won_date", "reign_days"] if column in ordered.columns]
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
            winners_filtered = matches[matches["winner_slug"].notna() & (matches["winner_slug"] != "") & matches["match_type"].notna()]
            if not winners_filtered.empty:
                winner_counts = winners_filtered.groupby(["winner_slug", "match_type"]).size().reset_index(name="count")
                winner_modes = winner_counts.sort_values("count", ascending=False).drop_duplicates("winner_slug")
                stipulations = dict(zip(winner_modes["winner_slug"], winner_modes["match_type"]))

            losers_filtered = matches[matches["loser_slug"].notna() & (matches["loser_slug"] != "") & matches["match_type"].notna()]
            if not losers_filtered.empty:
                loser_counts = losers_filtered.groupby(["loser_slug", "match_type"]).size().reset_index(name="count")
                loser_modes = loser_counts.sort_values("count", ascending=False).drop_duplicates("loser_slug")
                for slug, mtype in zip(loser_modes["loser_slug"], loser_modes["match_type"]):
                    stipulations.setdefault(slug, mtype)

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

    _cached_wrestlers_df = pd.DataFrame(records)
    return _cached_wrestlers_df


def _load_titles() -> pd.DataFrame:
    return _read_catalog(["titles.csv", "titles_extracted.csv"])


def _load_matches() -> pd.DataFrame:
    return _read_catalog(["matches.csv", "matches_normalized.csv"])


@router.get("/wrestlers")
def list_wrestlers(source: Optional[str] = None):
    global _cached_wrestlers_records
    _check_and_refresh_cache()
    if _cached_wrestlers_records is None:
        wrestlers = _load_wrestlers()
        _cached_wrestlers_records = _serialize_records(wrestlers)

    records = _cached_wrestlers_records
    if source:
        records = [r for r in records if str(r.get("source", "")).lower() == source.lower()]
    return records


@router.get("/titles")
def list_titles():
    global _cached_titles_records
    _check_and_refresh_cache()
    if _cached_titles_records is None:
        titles_df = _normalize_titles_frame(_load_titles())
        wrestlers_df = _load_wrestlers()
        if not titles_df.empty and not wrestlers_df.empty:
            enrich_columns = [
                column
                for column in ["name_slug", "artist_name", "real_name", "image_url", "biography", "height", "weight", "birth_date"]
                if column in wrestlers_df.columns
            ]
            titles_df = titles_df.merge(
                wrestlers_df[enrich_columns].rename(columns={"name_slug": "holder_slug"}),
                on="holder_slug",
                how="left",
            )
        _cached_titles_records = _serialize_records(titles_df)
    return _cached_titles_records


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
    global _cached_matches_records
    _check_and_refresh_cache()
    if _cached_matches_records is None:
        _cached_matches_records = _serialize_records(_normalize_matches_frame(_load_matches()))
    return _cached_matches_records


@router.get("/health")
def health():
    return {
        "status": "ok",
        "processed_dir": str(PROCESSED_DIR),
        "raw_dir": str(RAW_DIR),
    }


app.include_router(router)
