import os
import tempfile
import pandas as pd

from etl.transform import clean_wrestlers, clean_champions
from etl.transform.normalize import normalize_titles
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


def test_normalize_titles_reconstructs_reigns_from_kaggle_matches(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    pd.DataFrame(
        [
            {"id": 1, "name": "WWE Championship"},
            {"id": 2, "name": "World Heavyweight Championship"},
        ]
    ).to_csv(raw_dir / "titles.csv", index=False)

    pd.DataFrame(
        [
            {"id": 10, "name": "John Cena"},
            {"id": 11, "name": "Triple H"},
            {"id": 12, "name": "Random Indy Wrestler"},
        ]
    ).to_csv(raw_dir / "wrestlers.csv", index=False)

    pd.DataFrame(
        [
            {"id": 100, "card_id": 500, "winner_id": 10, "title_id": 1, "title_change": 1},
            {"id": 101, "card_id": 501, "winner_id": 11, "title_id": 2, "title_change": 1},
            {"id": 102, "card_id": 502, "winner_id": 12, "title_id": 1, "title_change": 1},
            {"id": 103, "card_id": 503, "winner_id": 10, "title_id": 1, "title_change": 0},
        ]
    ).to_csv(raw_dir / "matches.csv", index=False)

    normalize_titles(processed_dir=str(processed_dir), raw_dir=str(raw_dir))

    out = pd.read_csv(processed_dir / "titles.csv")
    assert len(out) == 2
    assert set(out["holder"]) == {"John Cena", "Triple H"}
    assert set(out["title"]) == {"WWE Championship", "World Heavyweight Championship"}
    assert out["event_name"].tolist() == ["Card #500", "Card #501"]
