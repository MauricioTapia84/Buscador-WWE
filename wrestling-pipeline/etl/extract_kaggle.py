import os
import pandas as pd
import logging

try:
    from retry_utils import retry_on_exception
    from name_utils import normalize_name_columns
except ImportError:
    from etl.retry_utils import retry_on_exception
    from etl.name_utils import normalize_name_columns

def read_kaggle_tables(raw_folder: str = "data/raw") -> dict:
    """Read common Kaggle CSVs if present in `raw_folder` and return a dict of DataFrames.
    This is a best-effort loader and will not raise if files are absent."""
    res = {}
    # support multiple common filenames and case variations
    candidates = {
        "matches": ["matches.csv", "Matches.csv", "matches_raw.csv"],
        "titles": ["titles.csv", "Titles.csv"],
        "wrestlers": ["wrestlers.csv", "Wrestlers.csv"]
    }
    paths = {}
    for k, names in candidates.items():
        found = None
        for n in names:
            p = os.path.join(raw_folder, n)
            if os.path.exists(p):
                found = p
                break
        paths[k] = found
    for k, p in paths.items():
        if p and os.path.exists(p):
            try:
                res[k] = pd.read_csv(p)
                # normalize simple date columns if present
                for col in [c for c in res[k].columns if 'date' in c.lower()]:
                    try:
                        res[k][col] = pd.to_datetime(res[k][col], errors='coerce')
                    except Exception:
                        pass
            except Exception:
                res[k] = pd.DataFrame()
        else:
            res[k] = pd.DataFrame()
    return res

import sqlite3
import tempfile
import os


@retry_on_exception(attempts=3)
def extract_from_sqlite(db_path="../data/raw/wwe_matches.sqlite", limit=1000):
    logger = logging.getLogger("etl.extract_kaggle")
    try:
        conn = sqlite3.connect(db_path)
        # attempt to discover table names that may differ
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        tbl = None
        for candidate in ['Matches', 'matches', 'MATCHES']:
            if candidate in tables:
                tbl = candidate
                break
        if tbl is None and tables:
            tbl = tables[0]
        query = f"SELECT * FROM {tbl} LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info("sqlite: extracted matches", extra={"etl_stage": "extract", "source": "sqlite", "rows": len(df)})
        return df
    except Exception as e:
        logger.warning("sqlite: extract failed", extra={"etl_stage": "extract", "source": "sqlite", "error": str(e)})
        raise


def save_matches_csv(df, out_path="../data/raw/matches.csv"):
    df.to_csv(out_path, index=False)



if __name__ == '__main__':
    # prefer sqlite if exists
    db = os.path.join('..', 'data', 'raw', 'wwe_matches.sqlite')
    if os.path.exists(db):
        df = extract_from_sqlite(db_path=db, limit=10000)
    else:
        # try raw CSV
        csvp = os.path.join('..', 'data', 'raw', 'matches.csv')
        if os.path.exists(csvp):
            df = pd.read_csv(csvp)
        else:
            df = pd.DataFrame()

    save_matches_csv(df)

    # Normalize and export processed files
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


def normalize_matches_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common Kaggle/SQLite matches dataframe to expected columns and types."""
    df = df.copy()
    # initial mapping heuristics
    col_map = {
        'Event': 'event_name',
        'EventDate': 'event_date',
        'Winner': 'winner',
        'Loser': 'loser',
        'MatchType': 'match_type',
        'TitleOnLine': 'title_on_line',
        'Result': 'result'
    }
    extra_map = {
        'Blue': 'winner',
        'Red': 'loser',
        'Competitor1': 'winner',
        'Competitor2': 'loser',
        'Date': 'event_date',
        'Match Date': 'event_date',
        'title': 'title_on_line',
        'EventName': 'event_name',
        'MatchEvent': 'event_name'
    }
    for k, v in {**col_map, **extra_map}.items():
        if k in df.columns and v not in df.columns:
            df.rename(columns={k: v}, inplace=True)

    # additional heuristics for common variants
    for c in ['Event', 'EventName', 'MatchEvent', 'event']:
        if c in df.columns and 'event_name' not in df.columns:
            df.rename(columns={c: 'event_name'}, inplace=True)
    for c in ['EventDate', 'Date', 'Match Date', 'DateOfMatch', 'event_date']:
        if c in df.columns and 'event_date' not in df.columns:
            df.rename(columns={c: 'event_date'}, inplace=True)
    for c in ['Winner', 'Blue', 'Competitor1', 'Home']:
        if c in df.columns and 'winner' not in df.columns:
            df.rename(columns={c: 'winner'}, inplace=True)
    for c in ['Loser', 'Red', 'Competitor2', 'Away']:
        if c in df.columns and 'loser' not in df.columns:
            df.rename(columns={c: 'loser'}, inplace=True)

    # parse dates with coercion; keep parse flag
    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce', dayfirst=False)

    # normalize booleans across likely boolean cols
    for col in df.columns:
        vals = df[col].dropna().unique()
        str_vals = [str(v).lower() for v in vals]
        if len(str_vals) > 0 and all(s in ['0','1','true','false'] or s.isdigit() for s in str_vals):
            def _map_bool(x):
                if pd.isna(x):
                    return x
                sx = str(x).lower()
                if sx in ['1','true']:
                    return True
                if sx in ['0','false']:
                    return False
                return x
            df[col] = df[col].map(_map_bool)

    # clean whitespace in string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    df = normalize_name_columns(df, ["winner", "loser"])

    # basic validation: drop rows with no competitors
    if 'winner' in df.columns and 'loser' in df.columns:
        before = len(df)
        df = df[~(df['winner'].isna() & df['loser'].isna())]
        after = len(df)
        if after < before:
            logging.getLogger('etl.extract_kaggle').info('Dropped empty matches', extra={'dropped': before-after})

    # flag rows with unparseable dates for later inspection
    if 'event_date' in df.columns:
        df['event_date_parse_ok'] = ~df['event_date'].isna()
        n_bad = int((~df['event_date_parse_ok']).sum())
        if n_bad:
            logging.getLogger('etl.extract_kaggle').warning('Unparseable dates found', extra={'count': n_bad})

    return df
