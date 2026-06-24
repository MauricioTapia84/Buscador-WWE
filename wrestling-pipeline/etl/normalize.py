import os
import pandas as pd
from datetime import datetime
from rapidfuzz import process, fuzz


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
    # read sources
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

    # dedupe using rapidfuzz: build choices list
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
        # merge rows for these indexes
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
    out_df.drop(columns=[c for c in out_df.columns if c.endswith("_key")], inplace=True, errors="ignore")

    # add metadata
    meta = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'source_files': [os.path.basename(p) for p in [ts_path, wiki_path] if os.path.exists(p)],
        'rows_input': int(len(df)),
        'unique_before': int(seen_count),
        'unique_after': int(len(out_df)),
        'merges_performed': int(merge_count),
        'score_cutoff': int(score_cutoff)
    }
    out_df.to_csv(out_csv, index=False)
    try:
        out_df.to_parquet(out_parquet, index=False)
    except Exception:
        pass
    # write metadata file
    try:
        import json
        with open(os.path.join(processed_dir, 'wrestlers_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f)
    except Exception:
        pass

    # Basic validation of metadata: ensure at least one source file exists
    try:
        if not meta['source_files']:
            logging.getLogger('etl.normalize').warning('No source files found when normalizing wrestlers')
    except Exception:
        pass


def normalize_matches(processed_dir="data/processed", raw_dir="data/raw"):
    matches_in = os.path.join(processed_dir, "matches_normalized.csv")
    if not os.path.exists(matches_in):
        # try raw
        alt = os.path.join(raw_dir, "matches.csv")
        if os.path.exists(alt):
            df = pd.read_csv(alt)
        else:
            pd.DataFrame().to_csv(os.path.join(processed_dir, "matches.csv"), index=False)
            return
    else:
        df = pd.read_csv(matches_in)

    # normalize date columns with better heuristics
    date_cols = [c for c in df.columns if "date" in c.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            # keep timezone-naive date where possible
            df[col] = df[col].dt.date
        except Exception:
            df[col] = pd.NaT

    # metadata and validation
    rows_before = len(df)
    # drop rows with no competitors
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
    # metadata
    try:
        import json
        meta = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'rows': int(len(df)),
            'rows_before_validation': int(rows_before),
            'rows_after_validation': int(rows_after)
        }
        with open(os.path.join(processed_dir, 'matches_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f)
    except Exception:
        pass


if __name__ == '__main__':
    normalize_wrestlers()
    normalize_matches()
import os
import pandas as pd
import unicodedata
import re
from difflib import get_close_matches


def slug(name: str) -> str:
    if not isinstance(name, str):
        return ""
    s = unicodedata.normalize('NFKD', name)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def unify_wrestlers(processed_dir="data/processed", out_dir="data/processed"):
    # Read sources
    ts_file = os.path.join(processed_dir, "wrestlers_thesportsdb.csv")
    wiki_file = os.path.join(processed_dir, "wrestlers_enriched.csv")

    dfs = []
    if os.path.exists(ts_file):
        dfs.append(('thesportsdb', pd.read_csv(ts_file).assign(source='thesportsdb')))
    if os.path.exists(wiki_file):
        dfs.append(('wikipedia', pd.read_csv(wiki_file).assign(source='wikipedia')))

    if not dfs:
        return

    all_rows = pd.concat([df for _, df in dfs], ignore_index=True, sort=False)
    all_rows['slug'] = all_rows['name'].fillna('').apply(slug)

    # Build canonical list by slug matching and fuzzy fallback
    canonical = {}
    for idx, row in all_rows.iterrows():
        s = row['slug']
        if not s:
            continue
        if s in canonical:
            canonical[s].append(row.to_dict())
        else:
            # try fuzzy match
            keys = list(canonical.keys())
            match = get_close_matches(s, keys, n=1, cutoff=0.9)
            if match:
                canonical[match[0]].append(row.to_dict())
            else:
                canonical[s] = [row.to_dict()]

    rows = []
    for k, members in canonical.items():
        merged = {}
        merged['name'] = members[0].get('name')
        merged['slug'] = k
        # prefer thesportsdb fields if present
        for m in members:
            for field in ['real_name', 'promotion', 'height', 'weight', 'date_born', 'nationality', 'debut', 'retired', 'image_url', 'description']:
                if field not in merged or not merged.get(field):
                    merged[field] = m.get(field) or merged.get(field)
        rows.append(merged)

    out_df = pd.DataFrame(rows)
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, 'wrestlers.csv')
    out_parquet = os.path.join(out_dir, 'wrestlers.parquet')
    out_df.to_csv(out_csv, index=False)
    try:
        out_df.to_parquet(out_parquet, index=False)
    except Exception:
        pass


def main():
    unify_wrestlers()


if __name__ == '__main__':
    main()
