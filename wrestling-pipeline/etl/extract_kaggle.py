import os
import pandas as pd

def read_kaggle_tables(raw_folder: str = "data/raw") -> dict:
    """Read common Kaggle CSVs if present in `raw_folder` and return a dict of DataFrames.
    This is a best-effort loader and will not raise if files are absent."""
    res = {}
    paths = {
        "matches": os.path.join(raw_folder, "matches.csv"),
        "titles": os.path.join(raw_folder, "titles.csv"),
        "wrestlers": os.path.join(raw_folder, "wrestlers.csv"),
    }
    for k, p in paths.items():
        if os.path.exists(p):
            try:
                res[k] = pd.read_csv(p)
            except Exception:
                res[k] = pd.DataFrame()
        else:
            res[k] = pd.DataFrame()
    return res

import sqlite3
import pandas as pd
import logging
from retry_utils import retry_on_exception


@retry_on_exception(attempts=3)
def extract_from_sqlite(db_path="../data/raw/wwe_matches.sqlite", limit=1000):
    logger = logging.getLogger("etl.extract_kaggle")
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT *
        FROM Matches
        LIMIT {limit}
        """
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
    df = extract_from_sqlite()
    save_matches_csv(df)

    # Normalize and export processed files
    out_proc = os.path.join("..", "data", "processed")
    os.makedirs(out_proc, exist_ok=True)

    try:
        # Basic normalization: map expected columns to standard names
        norm = df.rename(columns={
            'Event': 'event_name',
            'EventDate': 'event_date',
            'Winner': 'winner',
            'Loser': 'loser',
            'MatchType': 'match_type',
            'TitleOnLine': 'title_on_line',
            'Result': 'result'
        })
    except Exception:
        norm = df.copy()

    matches_out = os.path.join(out_proc, 'matches_normalized.csv')
    events_out = os.path.join(out_proc, 'events_normalized.csv')

    try:
        norm.to_csv(matches_out, index=False)
    except Exception:
        pass

    # Try to extract events table if present
    try:
        events = pd.read_csv(os.path.join('..', 'data', 'raw', 'events.csv'))
        events.rename(columns={
            'Name': 'event_name',
            'Date': 'event_date'
        }, inplace=True)
        events.to_csv(events_out, index=False)
    except Exception:
        # no events file
        pd.DataFrame().to_csv(events_out, index=False)
