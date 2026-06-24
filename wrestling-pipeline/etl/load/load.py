import sqlite3
from typing import Optional

import pandas as pd

from ..utils.retry_utils import retry_on_exception


@retry_on_exception(attempts=3)
def load_data(wrestlers_df: Optional[pd.DataFrame] = None, champions_df: Optional[pd.DataFrame] = None, db_path: str = "../data/processed/wrestling.db"):
    conn = sqlite3.connect(db_path)
    try:
        if wrestlers_df is not None:
            wrestlers_df.to_sql("wrestlers", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wrestler_name ON wrestlers(name)")

        if champions_df is not None:
            champions_df.to_sql("champions", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_champion_title ON champions(title)")

        conn.commit()
    finally:
        conn.close()


__all__ = ["load_data"]
