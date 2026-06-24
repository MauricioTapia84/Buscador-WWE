import pandas as pd
from etl.extractors.kaggle import normalize_matches_df


def test_normalize_matches_basic():
    df = pd.DataFrame([
        {"Event": "Show", "EventDate": "2021-05-01", "Winner": "A", "Loser": "B", "TitleOnLine": 1}
    ])
    norm = normalize_matches_df(df)
    assert 'event_name' in norm.columns
    assert pd.api.types.is_datetime64_any_dtype(norm['event_date'])
    assert norm['title_on_line'].dtype == bool or norm['title_on_line'].dropna().apply(lambda x: isinstance(x, bool)).all()
