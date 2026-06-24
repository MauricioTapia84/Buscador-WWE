import os
import pandas as pd
from etl.extractors.kaggle import read_kaggle_tables
from etl.extractors.thesportsdb import extract_all
from bs4 import BeautifulSoup

from etl.extractors.wikipedia import (
    _clean_measurement,
    _extract_birth_date,
    _extract_infobox,
    _infobox_lookup,
    enrich_wrestlers_from_titles,
)


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


def test_enrich_wrestlers_from_titles_merges_summary_and_infobox(monkeypatch):
    monkeypatch.setattr(
        "etl.extractors.wikipedia.extract_wikipedia_pages",
        lambda titles: pd.DataFrame(
            [
                {
                    "title": "Bruno Sammartino",
                    "name": "Bruno Sammartino",
                    "extract": "WWE Hall of Famer",
                    "url": "https://en.wikipedia.org/wiki/Bruno_Sammartino",
                    "name_slug": "bruno sammartino",
                }
            ]
        ),
    )
    monkeypatch.setattr(
        "etl.extractors.wikipedia.enrich_wrestlers",
        lambda df: pd.DataFrame(
            [
                {
                    "name": "Bruno Sammartino",
                    "link": "https://en.wikipedia.org/wiki/Bruno_Sammartino",
                    "real_name": "Bruno Leopoldo Francesco Sammartino",
                    "birth_date": "1935-10-06",
                    "height": "188 cm",
                    "weight": "118 kg",
                    "debut": "1959",
                    "name_slug": "bruno sammartino",
                    "real_name_slug": "bruno leopoldo francesco sammartino",
                }
            ]
        ),
    )

    df = enrich_wrestlers_from_titles(["Bruno Sammartino"])
    assert not df.empty
    first = df.iloc[0].to_dict()
    assert first["name"] == "Bruno Sammartino"
    assert first["extract"] == "WWE Hall of Famer"
    assert first["real_name"] == "Bruno Leopoldo Francesco Sammartino"
    assert first["birth_date"] == "1935-10-06"


def test_wikipedia_infobox_aliases_handle_billed_height_weight_and_born():
    soup = BeautifulSoup(
        """
        <table class="infobox">
            <tr><th>Born</th><td>Terry Gene Bollea (1963-08-11) August 11, 1953 Augusta, Georgia, U.S.</td></tr>
            <tr><th>Billed height</th><td>6 ft 7 in [1]</td></tr>
            <tr><th>Billed weight</th><td>302 lb [2]</td></tr>
        </table>
        """,
        "html.parser",
    )
    info = _extract_infobox(soup)

    assert _extract_birth_date(_infobox_lookup(info, "born", contains=("born",))) == "1963-08-11"
    assert _clean_measurement(_infobox_lookup(info, "height", "billed height", contains=("height",))) == "6 ft 7 in"
    assert _clean_measurement(_infobox_lookup(info, "weight", "billed weight", contains=("weight",))) == "302 lb"
