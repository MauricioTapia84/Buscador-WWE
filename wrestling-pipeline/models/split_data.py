import pandas as pd
from sklearn.model_selection import train_test_split


def split_dataset(df: pd.DataFrame, target: str = 'es_campeon', test_size: float = 0.2, random_state: int = 42):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.Series(dtype='int'), pd.Series(dtype='int')

    X = df.drop(columns=[target], errors='ignore')
    y = df[target] if target in df.columns else pd.Series(dtype='int')
    if y.nunique() > 1:
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
