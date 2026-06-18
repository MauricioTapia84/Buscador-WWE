
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
