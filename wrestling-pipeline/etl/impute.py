import pandas as pd


def _fill_by_group_mean(df: pd.DataFrame, col: str, group_cols: list[str]) -> pd.Series:
    if col not in df.columns:
        return pd.Series(dtype='float64')
    groups = df.groupby(group_cols)[col].transform('mean')
    return df[col].fillna(groups)


def impute_wrestler_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if 'height_cm' in out.columns:
        out['height_cm'] = pd.to_numeric(out['height_cm'], errors='coerce')
        out['height_cm'] = out['height_cm'].fillna(_fill_by_group_mean(out, 'height_cm', ['nationality']))

    if 'weight_kg' in out.columns:
        out['weight_kg'] = pd.to_numeric(out['weight_kg'], errors='coerce')
        out['weight_kg'] = out['weight_kg'].fillna(_fill_by_group_mean(out, 'weight_kg', ['nationality']))

    if 'birth_date' in out.columns:
        out['birth_date'] = pd.to_datetime(out['birth_date'], errors='coerce')

    if 'era' in out.columns:
        out['era'] = out['era'].fillna('Sin clasificar')

    return out
