import os
import pandas as pd
from etl.extractors.kaggle import read_kaggle_tables
from etl.extractors.thesportsdb import extract_all


def test_read_kaggle_tables_no_files(tmp_path, monkeypatch):
    data = read_kaggle_tables(raw_folder=str(tmp_path))
    assert isinstance(data, dict)
    assert all(isinstance(v, pd.DataFrame) for v in data.values())


def test_extract_thesportsdb_sample(monkeypatch):
    # simulate network by monkeypatching fetch_wrestlers_by_name
    from etl.extractors.thesportsdb import fetch_wrestlers_by_name

    monkeypatch.setattr('etl.extractors.thesportsdb.fetch_wrestlers_by_name', lambda name: [
        {"idPlayer": "1", "strPlayer": name, "strDescriptionEN": "desc"}
    ])
    df = extract_all(["Test Wrestler"])
    assert not df.empty
    assert 'name' in df.columns
