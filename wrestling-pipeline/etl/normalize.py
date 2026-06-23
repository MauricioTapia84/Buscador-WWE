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
