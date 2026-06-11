
import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "../data/raw/wwe_matches.sqlite"
)

query = """
SELECT *
FROM Matches
LIMIT 1000
"""

df = pd.read_sql_query(query, conn)

df.to_csv(
    "../data/raw/matches.csv",
    index=False
)

conn.close()