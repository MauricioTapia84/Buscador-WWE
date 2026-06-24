import os
import sqlite3
import logging
from typing import Optional

import pandas as pd


def read_kaggle_tables(raw_folder: str = "data/raw") -> dict:
    """Read common Kaggle CSVs if present in `raw_folder` and return a dict of DataFrames."""
    res = {}
    candidates = {
        "matches": ["matches.csv", "Matches.csv", "matches_raw.csv"],
        "titles": ["titles.csv", "Titles.csv"],
        "wrestlers": ["wrestlers.csv", "Wrestlers.csv"],
    }
    for key, names in candidates.items():
        df = pd.DataFrame()
        for name in names:
            path = os.path.join(raw_folder, name)
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    break
                except Exception:
                    df = pd.DataFrame()
        res[key] = df
    return res


def extract_from_sqlite(db_path: str = "../data/raw/wwe_matches.sqlite", limit: int = 1000) -> pd.DataFrame:
    logger = logging.getLogger("etl.extract_kaggle")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"SQLite database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        table_name = None
        for candidate in ["Matches", "matches", "MATCHES"]:
            if candidate in tables:
                table_name = candidate
                break
        table_name = table_name or (tables[0] if tables else None)
        if table_name is None:
            raise ValueError("No table found in SQLite database")

        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        logger.info("Extracted SQLite table", extra={"table": table_name, "rows": len(df)})
        return df
    finally:
        conn.close()


def save_matches_csv(df: pd.DataFrame, out_path: str = "../data/raw/matches.csv"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)


def normalize_matches_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    col_map = {
        'Event': 'event_name',
        'EventName': 'event_name',
        'MatchEvent': 'event_name',
        'Date': 'event_date',
        'Match Date': 'event_date',
        'EventDate': 'event_date',
        'Winner': 'winner',
        'Loser': 'loser',
        'Home': 'winner',
        'Away': 'loser',
        'Competitor1': 'winner',
        'Competitor2': 'loser',
        'TitleOnLine': 'title_on_line',
        'Result': 'result',
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    if 'winner' in df.columns and 'loser' in df.columns:
        df = df[~(df['winner'].isna() & df['loser'].isna())]

    return df
