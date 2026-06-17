
import sqlite3
import pandas as pd
from retry_utils import requests_get_with_retry

def extract_from_sqlite(db_path="../data/raw/wwe_matches.sqlite", limit=1000):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT *
    FROM Matches
    LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def save_matches_csv(df, out_path="../data/raw/matches.csv"):
    df.to_csv(out_path, index=False)


if __name__ == '__main__':
    df = extract_from_sqlite()
    save_matches_csv(df)
