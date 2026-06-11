
import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "../data/processed/wrestling.db"
)

df = pd.read_csv(
    "../data/raw/wrestlers_api.csv"
)

df.to_sql(
    "wrestlers",
    conn,
    if_exists="replace",
    index=False
)

conn.execute("""
CREATE INDEX IF NOT EXISTS idx_wrestler_name
ON wrestlers(name)
""")

conn.commit()

conn.close()