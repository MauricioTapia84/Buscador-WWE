import os
import tempfile
import pandas as pd

from etl.transform import clean_wrestlers, clean_champions
from etl.validate import validate_wrestlers, validate_champions
from etl.load import load_data


def test_clean_wrestlers_and_validate_ok():
    df = pd.DataFrame(
        [
            {"name": "Alice", "height_cm": 180, "weight_kg": 90, "nationality": "US", "description": "desc", "debut_year": 2005},
            {"name": "Bob", "height_cm": 175, "weight_kg": 85, "nationality": "UK", "description": "desc2", "debut_year": 2010},
        ]
    )
    cleaned = clean_wrestlers(df)
    validated, report = validate_wrestlers(cleaned)
    assert report["status"] == "ok"


def test_validate_wrestlers_fails_on_bad_data():
    df = pd.DataFrame([
        {"name": "", "height_cm": "not_a_number", "weight_kg": -10, "debut_year": 1500}
    ])
    cleaned = clean_wrestlers(df)
    validated, report = validate_wrestlers(cleaned)
    assert report["status"] == "failed"


def test_load_writes_sqlite_tables(tmp_path):
    wrestlers = pd.DataFrame([
        {"name": "Alice", "height_cm": 180, "weight_kg": 90, "nationality": "US", "description": "desc", "debut_year": 2005}
    ])
    champions = pd.DataFrame([
        {"title": "World", "holder": "Alice", "won_date": pd.NaT, "reign_days": 10}
    ])

    db_path = str(tmp_path / "test_wrestling.db")
    load_data(wrestlers_df=wrestlers, champions_df=champions, db_path=db_path)

    import sqlite3

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wrestlers'")
    assert cur.fetchone() is not None
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='champions'")
    assert cur.fetchone() is not None
    conn.close()
