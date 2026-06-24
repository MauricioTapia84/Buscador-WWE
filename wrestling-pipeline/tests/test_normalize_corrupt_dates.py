import pandas as pd
from etl.extract_kaggle import normalize_matches_df


def test_corrupt_dates_and_variants():
    df = pd.DataFrame([
        {'Blue': 'A', 'Red': 'B', 'Date': '01/02/2020', 'TitleOnLine': '1'},
        {'Competitor1': 'C', 'Competitor2': 'D', 'EventName': 'Show', 'EventDate': 'not a date'},
        {'Winner': None, 'Loser': None, 'DateOfMatch': '2020-03-03'}
    ])
    out = normalize_matches_df(df)
    assert 'winner' in out.columns and 'loser' in out.columns
    # first row date parse ok
    assert out.iloc[0]['event_date_parse_ok'] is True
    # second row unparseable
    assert out.iloc[1]['event_date_parse_ok'] is False
    # third row should be dropped (no competitors)
    assert len(out) == 2
