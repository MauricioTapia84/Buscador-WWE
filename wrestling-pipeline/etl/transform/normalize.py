import logging
import os
import json
from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz, process


def _best_match(name, choices, score_cutoff=85):
    if not name or not choices:
        return None, 0
    try:
        match = process.extractOne(name, choices, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    except Exception:
        return None, 0
    if match:
        return match[0], match[1]
    return None, 0


def normalize_wrestlers(processed_dir="data/processed"):
    ts_path = os.path.join(processed_dir, "wrestlers_thesportsdb.csv")
    wiki_path = os.path.join(processed_dir, "wrestlers_extracted.csv")
    out_csv = os.path.join(processed_dir, "wrestlers.csv")
    out_parquet = os.path.join(processed_dir, "wrestlers.parquet")

    frames = []
    if os.path.exists(ts_path):
        frames.append(pd.read_csv(ts_path))
    if os.path.exists(wiki_path):
        frames.append(pd.read_csv(wiki_path))

    if not frames:
        pd.DataFrame().to_csv(out_csv, index=False)
        return

    df = pd.concat(frames, ignore_index=True, sort=False).fillna("")

    names = df['name'].fillna('').astype(str).str.strip().tolist()
    unique_names = []
    groups = {}
    score_cutoff = int(os.getenv('WRESTLER_DEDUPE_SCORE', '88'))
    merge_count = 0
    seen_count = 0
    for i, name in enumerate(names):
        if not name:
            continue
        seen_count += 1
        best, score = _best_match(name, unique_names, score_cutoff=score_cutoff)
        if best is None:
            unique_names.append(name)
            groups[name] = [i]
        else:
            merge_count += 1
            groups[best].append(i)

    records = []
    for canonical, idxs in groups.items():
        merged = {}
        for idx in idxs:
            row = df.iloc[idx].to_dict()
            for k, v in row.items():
                if pd.isna(v) or v == "":
                    continue
                if k not in merged or not merged.get(k):
                    merged[k] = v
        merged['canonical_name'] = canonical
        records.append(merged)

    out_df = pd.DataFrame(records)
    out_df.drop(columns=[c for c in out_df.columns if c.endswith("_key")], inplace=True, errors='ignore')

    meta = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'source_files': [os.path.basename(p) for p in [ts_path, wiki_path] if os.path.exists(p)],
        'rows_input': int(len(df)),
        'unique_before': int(seen_count),
        'unique_after': int(len(out_df)),
        'merges_performed': int(merge_count),
        'score_cutoff': int(score_cutoff),
    }
    out_df.to_csv(out_csv, index=False)
    try:
        out_df.to_parquet(out_parquet, index=False)
    except Exception:
        pass

    try:
        with open(os.path.join(processed_dir, 'wrestlers_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f)
    except Exception:
        logging.getLogger('etl.normalize').warning('Failed to write metadata', extra={})


def normalize_matches(processed_dir="data/processed", raw_dir="data/raw"):
    matches_in = os.path.join(processed_dir, "matches_normalized.csv")
    if os.path.exists(matches_in):
        df = pd.read_csv(matches_in)
    else:
        alt = os.path.join(raw_dir, "matches.csv")
        if os.path.exists(alt):
            df = pd.read_csv(alt)
        else:
            pd.DataFrame().to_csv(os.path.join(processed_dir, "matches.csv"), index=False)
            return

    date_cols = [c for c in df.columns if "date" in c.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.date
        except Exception:
            df[col] = pd.NaT

    rows_before = len(df)
    if 'winner' in df.columns and 'loser' in df.columns:
        df = df[~(df['winner'].isna() & df['loser'].isna())]
    rows_after = len(df)

    out_csv = os.path.join(processed_dir, "matches.csv")
    out_parquet = os.path.join(processed_dir, "matches.parquet")
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parquet, index=False)
    except Exception:
        pass

    try:
        meta = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'rows': int(len(df)),
            'rows_before_validation': int(rows_before),
            'rows_after_validation': int(rows_after),
        }
        with open(os.path.join(processed_dir, 'matches_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f)
    except Exception:
        logging.getLogger('etl.normalize').warning('Failed to write matches metadata', extra={})


if __name__ == '__main__':
    normalize_wrestlers()
    normalize_matches()
