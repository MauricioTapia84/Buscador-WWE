import json
import logging
import os
from datetime import datetime, timezone

import pandas as pd

try:
    from rapidfuzz import fuzz, process
except Exception:  # pragma: no cover
    fuzz = None
    process = None

try:
    from name_utils import clean_name, normalize_name_columns, slugify_name, first_non_empty
    from roster_targets import is_target_name, load_target_slugs
except ImportError:
    from etl.name_utils import clean_name, normalize_name_columns, slugify_name, first_non_empty
    from etl.roster_targets import is_target_name, load_target_slugs


LOGGER = logging.getLogger("etl.normalize")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_csv_if_exists(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def _target_slugs(processed_dir: str | None = None) -> set[str]:
    if processed_dir:
        target_file = os.path.join(processed_dir, "target_wrestlers.txt")
        if os.path.exists(target_file):
            return load_target_slugs(target_file)
    return set()


def _fuzzy_group_key(name: str, existing: list[str], score_cutoff: int) -> str | None:
    if not name or not existing or process is None or fuzz is None:
        return None
    match = process.extractOne(name, existing, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    if not match:
        return None
    return match[0]


def normalize_wrestlers(processed_dir="data/processed"):
    source_paths = [
        ("thesportsdb", os.path.join(processed_dir, "wrestlers_thesportsdb.csv")),
        ("wikipedia", os.path.join(processed_dir, "wrestlers_enriched.csv")),
        ("catalog", os.path.join(processed_dir, "wrestlers_extracted.csv")),
    ]
    frames = []
    for source_name, path in source_paths:
        frame = _read_csv_if_exists(path)
        if frame.empty:
            continue
        frame = frame.copy()
        frame["source"] = frame.get("source", source_name)
        if "name" not in frame.columns and "title" in frame.columns:
            frame["name"] = frame["title"]
        frames.append(frame)

    out_csv = os.path.join(processed_dir, "wrestlers.csv")
    out_parquet = os.path.join(processed_dir, "wrestlers.parquet")

    if not frames:
        pd.DataFrame().to_csv(out_csv, index=False)
        return

    df = pd.concat(frames, ignore_index=True, sort=False)
    df = normalize_name_columns(df, ["name", "real_name"])
    df = df[df["name_slug"].astype(str).str.len() > 0].copy()
    target_slugs = _target_slugs(processed_dir)
    if target_slugs:
        df = df[df["name"].apply(lambda value: is_target_name(value, target_slugs))].copy()

    score_cutoff = int(os.getenv("WRESTLER_DEDUPE_SCORE", "88"))
    groups: dict[str, list[int]] = {}
    canonical_display: dict[str, str] = {}
    merge_count = 0

    for idx, row in df.iterrows():
        key = row.get("name_slug", "")
        display_name = clean_name(row.get("name"))
        if not key:
            continue

        matched_key = None
        if key not in groups:
            matched_key = _fuzzy_group_key(display_name, list(canonical_display.values()), score_cutoff)
        if matched_key:
            for existing_key, existing_display in canonical_display.items():
                if existing_display == matched_key:
                    key = existing_key
                    merge_count += 1
                    break

        groups.setdefault(key, []).append(idx)
        canonical_display.setdefault(key, display_name or key)

    records = []
    for key, indexes in groups.items():
        group = df.loc[indexes].copy()
        group["source_rank"] = group["source"].map({"thesportsdb": 0, "wikipedia": 1, "catalog": 2}).fillna(9)
        group = group.sort_values(["source_rank"])

        merged = {
            "canonical_name": canonical_display.get(key) or clean_name(group.iloc[0].get("name")),
            "name_slug": key,
        }

        for column in group.columns:
            if column in {"source_rank"}:
                continue
            merged[column] = first_non_empty(*group[column].tolist())

        merged["name"] = first_non_empty(merged.get("canonical_name"), merged.get("name"))
        merged["biography"] = first_non_empty(merged.get("description"), merged.get("extract"))
        records.append(merged)

    if records:
        out_df = pd.DataFrame(records).sort_values(["canonical_name", "name_slug"], na_position="last")
    else:
        out_df = pd.DataFrame(columns=["canonical_name", "name_slug"])
    out_df.to_csv(out_csv, index=False)
    try:
        out_df.to_parquet(out_parquet, index=False)
    except Exception:
        pass

    meta = {
        "generated_at": _utc_now_iso(),
        "source_files": [os.path.basename(path) for _, path in source_paths if os.path.exists(path)],
        "rows_input": int(len(df)),
        "unique_before": int(df["name_slug"].nunique()),
        "unique_after": int(len(out_df)),
        "merges_performed": int(merge_count),
        "score_cutoff": int(score_cutoff),
    }
    with open(os.path.join(processed_dir, "wrestlers_metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle)


def normalize_matches(processed_dir="data/processed", raw_dir="data/raw"):
    processed_path = os.path.join(processed_dir, "matches_normalized.csv")
    raw_path = os.path.join(raw_dir, "matches.csv")

    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path)
    elif os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
    else:
        pd.DataFrame().to_csv(os.path.join(processed_dir, "matches.csv"), index=False)
        return

    rename_map = {
        "Winner": "winner",
        "Loser": "loser",
        "Event": "event_name",
        "EventDate": "event_date",
        "MatchType": "match_type",
        "TitleOnLine": "title_on_line",
    }
    df = df.rename(columns={src: dst for src, dst in rename_map.items() if src in df.columns and dst not in df.columns})
    df = normalize_name_columns(df, ["winner", "loser"])
    for column in [col for col in df.columns if "date" in col.lower()]:
        try:
            df[column] = pd.to_datetime(df[column], errors="coerce")
        except Exception:
            df[column] = pd.NaT

    rows_before = len(df)
    if "winner" in df.columns and "loser" in df.columns:
        df = df[(df["winner_slug"] != "") | (df["loser_slug"] != "")]
    rows_after = len(df)

    out_csv = os.path.join(processed_dir, "matches.csv")
    out_parquet = os.path.join(processed_dir, "matches.parquet")
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parquet, index=False)
    except Exception:
        pass

    meta = {
        "generated_at": _utc_now_iso(),
        "rows": int(len(df)),
        "rows_before_validation": int(rows_before),
        "rows_after_validation": int(rows_after),
    }
    with open(os.path.join(processed_dir, "matches_metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle)


def normalize_titles(processed_dir="data/processed", raw_dir="data/raw"):
    processed_titles = _read_csv_if_exists(os.path.join(processed_dir, "titles_extracted.csv"))
    raw_reigns = _read_csv_if_exists(os.path.join(raw_dir, "reigns.csv"))
    raw_champion_history = _read_csv_if_exists(os.path.join(raw_dir, "wwe_champions_initial.csv"))
    raw_matches = _read_csv_if_exists(os.path.join(raw_dir, "matches.csv"))
    raw_kaggle_titles = _read_csv_if_exists(os.path.join(raw_dir, "titles.csv"))
    raw_wrestlers = _read_csv_if_exists(os.path.join(raw_dir, "wrestlers.csv"))

    frames = []
    target_slugs = _target_slugs(processed_dir)

    if not raw_reigns.empty:
        frame = raw_reigns.copy()
        frame = frame.rename(
            columns={
                "title_name": "title",
                "champion_name": "holder",
                "start_date": "won_date",
            }
        )
        frames.append(frame)

    if not raw_champion_history.empty:
        history = raw_champion_history.copy()
        history["title"] = "WWE Championship"
        history = history.rename(
            columns={
                "champion": "holder",
                "date_won": "won_date",
                "event": "event_name",
                "days_held": "reign_days",
            }
        )
        history["start_date"] = history.get("won_date")
        history["champion_name"] = history.get("holder")
        frames.append(history)

    if not processed_titles.empty:
        titles = processed_titles.copy()
        titles["champion_name"] = titles.get("holder")
        titles["start_date"] = titles.get("won_date")
        frames.append(titles)

    if not raw_matches.empty and not raw_kaggle_titles.empty and not raw_wrestlers.empty:
        matches = raw_matches.copy()
        if "title_change" in matches.columns:
            title_change = pd.to_numeric(matches["title_change"], errors="coerce").fillna(0)
            matches = matches[title_change == 1].copy()
        else:
            matches = pd.DataFrame()

        if not matches.empty:
            titles_lookup = raw_kaggle_titles.rename(columns={"id": "title_id", "name": "title"})
            wrestlers_lookup = raw_wrestlers.rename(columns={"id": "winner_id", "name": "holder"})
            matches = matches.merge(titles_lookup[["title_id", "title"]], on="title_id", how="left")
            matches = matches.merge(wrestlers_lookup[["winner_id", "holder"]], on="winner_id", how="left")
            matches = matches.dropna(subset=["title", "holder"]).copy()

            if not matches.empty:
                matches["title"] = matches["title"].astype(str).str.strip()
                matches["holder"] = matches["holder"].astype(str).str.strip()
                matches = matches[(matches["title"] != "") & (matches["holder"] != "")]

                if not matches.empty:
                    matches["champion_name"] = matches["holder"]
                    matches["event_name"] = matches.get("event_name")
                    if "event_name" not in matches.columns or matches["event_name"].isna().all():
                        matches["event_name"] = matches.get("card_id").map(
                            lambda value: f"Card #{int(value)}" if pd.notna(value) else None
                        )
                    matches["notes"] = "Reconstruido desde Kaggle matches.csv (title_change=1)"
                    matches["reign_days"] = pd.NA
                    matches["days_recognized"] = pd.NA
                    matches["won_date"] = pd.NaT
                    matches["start_date"] = pd.NaT
                    matches["overall_reign"] = pd.NA
                    matches["champion_reign_number"] = pd.NA
                    if "card_id" in matches.columns:
                        matches["source_order"] = pd.to_numeric(matches["card_id"], errors="coerce")
                    elif "id" in matches.columns:
                        matches["source_order"] = pd.to_numeric(matches["id"], errors="coerce")
                    else:
                        matches["source_order"] = pd.NA

                    kaggle_reigns = matches[
                        [
                            column
                            for column in [
                                "title",
                                "holder",
                                "champion_name",
                                "won_date",
                                "start_date",
                                "reign_days",
                                "days_recognized",
                                "event_name",
                                "notes",
                                "source_order",
                            ]
                            if column in matches.columns
                        ]
                    ].copy()
                    frames.append(kaggle_reigns)

    out_csv = os.path.join(processed_dir, "titles.csv")
    out_parquet = os.path.join(processed_dir, "titles.parquet")

    if not frames:
        pd.DataFrame().to_csv(out_csv, index=False)
        return

    df = pd.concat(frames, ignore_index=True, sort=False)
    df = normalize_name_columns(df, ["holder", "champion_name"])
    if target_slugs and not df.empty:
        df = df[df["holder"].apply(lambda value: is_target_name(value, target_slugs))].copy()

    if "title" not in df.columns and "name" in df.columns:
        df["title"] = df["name"]

    for column in ["won_date", "start_date", "end_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    if "reign_days" in df.columns:
        df["reign_days"] = pd.to_numeric(df["reign_days"], errors="coerce")
    if "days_recognized" in df.columns:
        df["days_recognized"] = pd.to_numeric(df["days_recognized"], errors="coerce")

    dedupe_columns = [column for column in ["title", "holder_slug", "won_date", "event_name", "source_order"] if column in df.columns]
    if dedupe_columns:
        df = df.drop_duplicates(subset=dedupe_columns)

    sort_columns = [column for column in ["title", "won_date", "start_date", "source_order"] if column in df.columns]
    if sort_columns:
        df = df.sort_values(sort_columns, na_position="last").reset_index(drop=True)

    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parquet, index=False)
    except Exception:
        pass


def slug(name: str) -> str:
    return slugify_name(name)


def unify_wrestlers(processed_dir="data/processed", out_dir="data/processed"):
    normalize_wrestlers(processed_dir=processed_dir)


def main():
    unify_wrestlers()


if __name__ == "__main__":
    main()
