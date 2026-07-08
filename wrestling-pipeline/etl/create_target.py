import pandas as pd


def create_champion_target(df: pd.DataFrame, window_months: int = 3) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if 'won_date' in out.columns:
        out['won_date'] = pd.to_datetime(out['won_date'], errors='coerce')

    if 'start_date' in out.columns and 'won_date' not in out.columns:
        out['won_date'] = pd.to_datetime(out['start_date'], errors='coerce')

    if 'total_titles' not in out.columns and 'title_change' in out.columns:
        out['total_titles'] = out.groupby('winner_id')['title_change'].transform('sum').fillna(0)

    out['es_campeon'] = (out.get('total_titles', 0) > 0).astype(int)
    out['championship_probability'] = 0.0

    if 'win_rate' in out.columns:
        wins = out.get('total_wins', 0).astype(float).fillna(0.0)
        titles = out.get('total_titles', 0).astype(float).fillna(0.0)
        out['championship_probability'] = (
            (out['win_rate'].fillna(0.0) * 0.7)
            + (titles / (wins + 1) * 0.3)
        ).clip(0.0, 1.0) * 100.0

    return out
