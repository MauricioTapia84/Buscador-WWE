import re
from typing import Optional

import numpy as np
import pandas as pd

MISSING_VALUES = {
    'unknown', 'n/a', 'na', 'none', 'sin datos', 'sin valor', 'sin info',
    'not available', '-', '--', '?', 'none.', 'n/a.', 'nan'
}


def _normalize_missing(value: Optional[str]) -> Optional[pd.NA]:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str):
        text = value.strip().lower()
        if text == "" or text in MISSING_VALUES:
            return pd.NA
    return value


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Estándar básico de limpieza para el dataframe crudo."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df = df.replace(r'^[\s\t\n\r]*$', pd.NA, regex=True)
    df = df.applymap(_normalize_missing)

    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].astype(str).str.strip().replace({'nan': pd.NA})

    if 'id' in df.columns:
        df['id'] = pd.to_numeric(df['id'], errors='coerce')

    return df


def dedupe_dataframe(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """Elimina duplicados exactos y mantiene la primera aparición."""
    if df is None or df.empty:
        return pd.DataFrame()
    subset = [col for col in subset if col in df.columns]
    if not subset:
        return df.drop_duplicates()
    return df.drop_duplicates(subset=subset)
