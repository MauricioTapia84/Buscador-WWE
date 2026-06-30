import os

try:
    from etl.extractors.kaggle import read_kaggle_tables, extract_from_sqlite, save_matches_csv, normalize_matches_df
except ImportError:
    from extractors.kaggle import read_kaggle_tables, extract_from_sqlite, save_matches_csv, normalize_matches_df

__all__ = [
    "read_kaggle_tables",
    "extract_from_sqlite",
    "save_matches_csv",
    "normalize_matches_df",
    "extract_all_sqlite",
]

def extract_all_sqlite(raw_dir: str):
    import pandas as pd
    import sqlite3
    import os

    os.makedirs(raw_dir, exist_ok=True)

    # Check for any sqlite file in raw_dir
    db_path = None
    db_candidates = ["wwe_matches.sqlite", "wwe_db.sqlite", "matches.sqlite", "matches.db"]
    for db_name in db_candidates:
        p = os.path.join(raw_dir, db_name)
        if os.path.exists(p):
            db_path = p
            break
    if not db_path:
        # Fallback: scan for any .sqlite or .db file
        for f in os.listdir(raw_dir) if os.path.exists(raw_dir) else []:
            if f.endswith(".sqlite") or f.endswith(".db"):
                db_path = os.path.join(raw_dir, f)
                break

    if db_path and os.path.exists(db_path):
        try:
            print(f"SQLite found: {db_path}. Extracting all tables to raw folder...")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cur.fetchall()]

            # 1. Matches
            for tbl_name in ["Matches", "matches", "MATCHES"]:
                if tbl_name in tables:
                    df_matches = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                    save_matches_csv(df_matches, out_path=os.path.join(raw_dir, "matches.csv"))
                    print(f"Extracted matches table from SQLite to raw/matches.csv ({len(df_matches)} rows)")
                    
                    # Normalize matches to processed folder
                    norm = normalize_matches_df(df_matches)
                    out_proc = os.path.join(raw_dir, '..', 'processed')
                    os.makedirs(out_proc, exist_ok=True)
                    norm.to_csv(os.path.join(out_proc, 'matches_normalized.csv'), index=False)
                    try:
                        norm.to_parquet(os.path.join(out_proc, 'matches_normalized.parquet'), index=False)
                    except Exception:
                        pass
                    break

            # 2. Wrestlers
            for tbl_name in ["Wrestlers", "wrestlers", "WRESTLERS"]:
                if tbl_name in tables:
                    df_wrestlers = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                    df_wrestlers.to_csv(os.path.join(raw_dir, "wrestlers.csv"), index=False)
                    print(f"Extracted wrestlers table from SQLite to raw/wrestlers.csv ({len(df_wrestlers)} rows)")
                    break

            # 3. Belts / Titles
            for tbl_name in ["Belts", "belts", "BELTS", "Titles", "titles", "TITLES"]:
                if tbl_name in tables:
                    df_titles = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                    df_titles.to_csv(os.path.join(raw_dir, "titles.csv"), index=False)
                    print(f"Extracted titles/belts table from SQLite to raw/titles.csv ({len(df_titles)} rows)")
                    break

            conn.close()
        except Exception as e:
            print(f"Error extracting from SQLite: {e}")
    else:
        # Fallback to matches.csv if no SQLite is found
        csvp = os.path.join(raw_dir, 'matches.csv')
        if os.path.exists(csvp):
            try:
                df = pd.read_csv(csvp)
                out_proc = os.path.join(raw_dir, '..', 'processed')
                os.makedirs(out_proc, exist_ok=True)
                norm = normalize_matches_df(df)
                norm.to_csv(os.path.join(out_proc, 'matches_normalized.csv'), index=False)
                print(f"Processed local raw/matches.csv ({len(norm)} normalized rows)")
            except Exception as e:
                print(f"Error processing raw/matches.csv: {e}")
        else:
            print("No SQLite database or matches.csv found in raw folder.")

if __name__ == '__main__':
    raw_dir = os.path.join('data', 'raw')
    extract_all_sqlite(raw_dir)
