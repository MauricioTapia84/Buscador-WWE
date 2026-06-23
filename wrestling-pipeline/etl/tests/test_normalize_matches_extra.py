import pandas as pd
from etl.extract_kaggle import normalize_matches_df

def test_normalize_extra_mapping():
    df = pd.DataFrame([
        {'Blue': 'A', 'Red': 'B', 'Date': '2020-01-01', 'TitleOnLine': 1},
        {'Competitor1': 'C', 'Competitor2': 'D', 'Match Date': '2020-02-02'}
    ])
    out = normalize_matches_df(df)
    assert 'winner' in out.columns
    assert 'loser' in out.columns
    assert pd.api.types.is_bool_dtype(out['title_on_line']) or out['title_on_line'].notna().all()
