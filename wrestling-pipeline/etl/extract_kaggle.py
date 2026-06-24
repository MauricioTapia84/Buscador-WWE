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
]


if __name__ == '__main__':
    import pandas as pd

    db = os.path.join('..', 'data', 'raw', 'wwe_matches.sqlite')
    if os.path.exists(db):
        df = extract_from_sqlite(db_path=db, limit=10000)
    else:
        csvp = os.path.join('..', 'data', 'raw', 'matches.csv')
        if os.path.exists(csvp):
            df = pd.read_csv(csvp)
        else:
            df = pd.DataFrame()

    save_matches_csv(df)
    out_proc = os.path.join('..', 'data', 'processed')
    os.makedirs(out_proc, exist_ok=True)

    if df.empty:
        pd.DataFrame().to_csv(os.path.join(out_proc, 'matches_normalized.csv'), index=False)
    else:
        norm = normalize_matches_df(df)
        matches_out = os.path.join(out_proc, 'matches_normalized.csv')
        try:
            norm.to_csv(matches_out, index=False)
            try:
                norm.to_parquet(os.path.join(out_proc, 'matches_normalized.parquet'), index=False)
            except Exception:
                pass
        except Exception:
            pass
