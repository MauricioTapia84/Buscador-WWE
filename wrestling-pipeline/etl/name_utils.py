import re
import unicodedata
from typing import Iterable

import pandas as pd


def clean_name(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def slugify_name(value) -> str:
    text = clean_name(value)
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9 ]+", " ", ascii_text)
    ascii_text = re.sub(r"\s+", " ", ascii_text).strip()
    return ascii_text


def normalize_name_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        out[column] = out[column].map(clean_name)
        out[f"{column}_slug"] = out[column].map(slugify_name)
    return out


def first_non_empty(*values):
    for value in values:
        if value is None:
            continue
        if isinstance(value, float) and pd.isna(value):
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None
