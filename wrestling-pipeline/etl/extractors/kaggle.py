import logging
import os
import sqlite3
from typing import Optional

import pandas as pd

try:
    from ..utils.retry_utils import retry_on_exception
    from ..name_utils import normalize_name_columns
except ImportError:
    from utils.retry_utils import retry_on_exception
    from name_utils import normalize_name_columns


def read_kaggle_tables(raw_folder: str = "data/raw") -> dict:
    """Read common Kaggle CSVs or SQLite tables if present in `raw_folder` and return a dict of DataFrames."""
    res = {}
    candidates = {
        "matches": ["matches.csv", "Matches.csv", "matches_raw.csv"],
        "titles": ["titles.csv", "Titles.csv"],
        "wrestlers": ["wrestlers.csv", "Wrestlers.csv"],
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
        
    # Load from CSVs first
    for k, p in paths.items():
        if p and os.path.exists(p):
            try:
                res[k] = pd.read_csv(p)
                for col in [c for c in res[k].columns if 'date' in c.lower()]:
                    try:
                        res[k][col] = pd.to_datetime(res[k][col], errors='coerce')
                    except Exception:
                        pass
            except Exception:
                res[k] = pd.DataFrame()
        else:
            res[k] = pd.DataFrame()

    # Also try to extract from SQLite if present
    db_candidates = ["wwe_matches.sqlite", "wwe_db.sqlite", "matches.sqlite", "matches.db"]
    sqlite_path = None
    if os.path.exists(raw_folder):
        for db_name in db_candidates:
            p = os.path.join(raw_folder, db_name)
            if os.path.exists(p):
                sqlite_path = p
                break
                
        if not sqlite_path:
            # Fallback: scan raw_folder for any .sqlite or .db file
            try:
                for f in os.listdir(raw_folder):
                    if f.endswith(".sqlite") or f.endswith(".db"):
                        sqlite_path = os.path.join(raw_folder, f)
                        break
            except Exception:
                pass

    if sqlite_path:
        try:
            conn = sqlite3.connect(sqlite_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cur.fetchall()]
            
            # Matches table
            if res.get("matches") is None or res["matches"].empty:
                for tbl_name in ["Matches", "matches", "MATCHES"]:
                    if tbl_name in tables:
                        res["matches"] = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                        break
            
            # Wrestlers table
            if res.get("wrestlers") is None or res["wrestlers"].empty:
                for tbl_name in ["Wrestlers", "wrestlers", "WRESTLERS"]:
                    if tbl_name in tables:
                        res["wrestlers"] = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                        break

            # Belts / Titles table
            if res.get("titles") is None or res["titles"].empty:
                for tbl_name in ["Belts", "belts", "BELTS", "Titles", "titles", "TITLES"]:
                    if tbl_name in tables:
                        res["titles"] = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
                        break
            conn.close()
        except Exception:
            pass

    return res


@retry_on_exception(attempts=3)
def extract_from_sqlite(db_path: str = "data/raw/wwe_matches.sqlite", limit: int = 1000) -> pd.DataFrame:
    logger = logging.getLogger("etl.extract_kaggle")
    try:
        conn = sqlite3.connect(db_path)
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


def save_matches_csv(df: pd.DataFrame, out_path: str = "data/raw/matches.csv"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)


if __name__ == '__main__':
    db = os.path.join('data', 'raw', 'wwe_matches.sqlite')
    if os.path.exists(db):
        df = extract_from_sqlite(db_path=db, limit=10000)
    else:
        csvp = os.path.join('data', 'raw', 'matches.csv')
        if os.path.exists(csvp):
            df = pd.read_csv(csvp)
        else:
            df = pd.DataFrame()

    save_matches_csv(df)
    out_proc = os.path.join('data', 'processed')
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
    df = df.copy()

    # Coalesce event_date
    date_cols = ['EventDate', 'Date', 'Match Date', 'DateOfMatch', 'event_date']
    found_date_cols = [c for c in date_cols if c in df.columns]
    if found_date_cols:
        df['event_date'] = df[found_date_cols].bfill(axis=1).iloc[:, 0]
        for c in found_date_cols:
            if c != 'event_date':
                df.drop(columns=[c], inplace=True, errors='ignore')

    # Coalesce event_name
    name_cols = ['Event', 'EventName', 'MatchEvent', 'event_name']
    found_name_cols = [c for c in name_cols if c in df.columns]
    if found_name_cols:
        df['event_name'] = df[found_name_cols].bfill(axis=1).iloc[:, 0]
        for c in found_name_cols:
            if c != 'event_name':
                df.drop(columns=[c], inplace=True, errors='ignore')

    # Coalesce winner
    winner_cols = ['Winner', 'Blue', 'Competitor1', 'Home', 'winner']
    found_winner_cols = [c for c in winner_cols if c in df.columns]
    if found_winner_cols:
        df['winner'] = df[found_winner_cols].bfill(axis=1).iloc[:, 0]
        for c in found_winner_cols:
            if c != 'winner':
                df.drop(columns=[c], inplace=True, errors='ignore')

    # Coalesce loser
    loser_cols = ['Loser', 'Red', 'Competitor2', 'Away', 'loser']
    found_loser_cols = [c for c in loser_cols if c in df.columns]
    if found_loser_cols:
        df['loser'] = df[found_loser_cols].bfill(axis=1).iloc[:, 0]
        for c in found_loser_cols:
            if c != 'loser':
                df.drop(columns=[c], inplace=True, errors='ignore')

    # Coalesce title_on_line
    title_cols = ['TitleOnLine', 'title', 'title_on_line']
    found_title_cols = [c for c in title_cols if c in df.columns]
    if found_title_cols:
        df['title_on_line'] = df[found_title_cols].bfill(axis=1).iloc[:, 0]
        for c in found_title_cols:
            if c != 'title_on_line':
                df.drop(columns=[c], inplace=True, errors='ignore')

    # Coalesce match_type
    type_cols = ['MatchType', 'match_type']
    found_type_cols = [c for c in type_cols if c in df.columns]
    if found_type_cols:
        df['match_type'] = df[found_type_cols].bfill(axis=1).iloc[:, 0]
        for c in found_type_cols:
            if c != 'match_type':
                df.drop(columns=[c], inplace=True, errors='ignore')

    if 'title_on_line' in df.columns:
        df['title_on_line'] = df['title_on_line'].fillna(False)

    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce', dayfirst=False)

    for col in df.columns:
        vals = df[col].dropna().unique()
        str_vals = [str(v).lower().strip().split('.')[0] for v in vals] # handle floats like 1.0 or 0.0
        if len(str_vals) > 0 and all(s in ['0', '1', 'true', 'false'] for s in str_vals):
            def _map_bool(x):
                if pd.isna(x):
                    return x
                sx = str(x).lower().strip().split('.')[0]
                if sx in ['1', 'true']:
                    return True
                if sx in ['0', 'false']:
                    return False
                return x
            df[col] = df[col].map(_map_bool)

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    df = normalize_name_columns(df, ["winner", "loser"])

    if 'winner' in df.columns and 'loser' in df.columns:
        before = len(df)
        winner_empty = df['winner'].isna() | (df['winner'] == '') | (df['winner'].astype(str).str.lower() == 'nan')
        loser_empty = df['loser'].isna() | (df['loser'] == '') | (df['loser'].astype(str).str.lower() == 'nan')
        df = df[~(winner_empty & loser_empty)]
        after = len(df)
        if after < before:
            logging.getLogger('etl.extract_kaggle').info('Dropped empty matches', extra={'dropped': before-after})

    if 'event_date' in df.columns:
        df['event_date_parse_ok'] = ~df['event_date'].isna()
        n_bad = int((~df['event_date_parse_ok']).sum())
        if n_bad:
            logging.getLogger('etl.extract_kaggle').warning('Unparseable dates found', extra={'count': n_bad})

    return df
