import sqlite3
import os
import pandas as pd


def create_sample_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame([
        {"Event": "Sample Show", "EventDate": "2020-01-01", "Winner": "A", "Loser": "B", "MatchType": "Singles", "TitleOnLine": False, "Result": "A defeated B"}
    ])
    df.to_sql('Matches', conn, index=False, if_exists='replace')
    conn.close()


def test_extract_from_sqlite_integration(tmp_path):
    db = tmp_path / "sample.sqlite"
    create_sample_sqlite(str(db))
    # run extractor main path
    from extract_kaggle import extract_from_sqlite
    df = extract_from_sqlite(db_path=str(db), limit=10)
    assert not df.empty
    assert 'Event' in df.columns
