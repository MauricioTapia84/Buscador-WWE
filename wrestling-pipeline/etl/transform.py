
import pandas as pd
from typing import Optional


def clean_wrestlers(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Normalize wrestlers dataframe to expected schema.

    Expected columns after cleaning: name, height_cm, weight_kg, nationality, description, debut_year
    """
    if df is None:
        df = pd.read_csv("../data/raw/wrestlers_api.csv")

    # Normalize column names from possible extractor outputs
    mapping = {}
    if "strPlayer" in df.columns:
        mapping["strPlayer"] = "name"
    if "name" in df.columns:
        mapping["name"] = "name"
    if "strHeight" in df.columns:
        mapping["strHeight"] = "height_cm"
    if "height" in df.columns:
        mapping["height"] = "height_cm"
    if "strWeight" in df.columns:
        mapping["strWeight"] = "weight_kg"
    if "weight" in df.columns:
        mapping["weight"] = "weight_kg"
    if "strNationality" in df.columns:
        mapping["strNationality"] = "nationality"
    if "nationality" in df.columns:
        mapping["nationality"] = "nationality"
    if "strDescriptionEN" in df.columns:
        mapping["strDescriptionEN"] = "description"

    if mapping:
        df = df.rename(columns=mapping)

    if "name" in df.columns:
        df["name"] = df["name"].astype(str).str.strip()

    # Try to coerce numeric columns
    if "height_cm" in df.columns:
        df["height_cm"] = pd.to_numeric(df["height_cm"], errors="coerce")
    if "weight_kg" in df.columns:
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce")

    df = df.drop_duplicates(subset=[c for c in ["name"] if c in df.columns])

    # Ensure expected columns exist
    for col in ["name", "height_cm", "weight_kg", "nationality", "description", "debut_year"]:
        if col not in df.columns:
            df[col] = pd.NA

    return df[
        ["name", "height_cm", "weight_kg", "nationality", "description", "debut_year"]
    ]


def clean_champions(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Normalize champions dataframe to expected schema: title, holder, won_date, reign_days"""
    if df is None:
        df = pd.read_csv("../data/raw/champions.csv")

    mapping = {}
    if "champion" in df.columns:
        mapping["champion"] = "title"
    if "holder" in df.columns:
        mapping["holder"] = "holder"
    if "current_holder" in df.columns:
        mapping["current_holder"] = "holder"
    if "won_date" in df.columns:
        mapping["won_date"] = "won_date"
    if "reign_days" in df.columns:
        mapping["reign_days"] = "reign_days"

    if mapping:
        df = df.rename(columns=mapping)

    if "title" in df.columns:
        df["title"] = df["title"].astype(str).str.strip()
    if "holder" in df.columns:
        df["holder"] = df["holder"].astype(str).str.strip()

    # Coerce numeric/date types
    if "reign_days" in df.columns:
        df["reign_days"] = pd.to_numeric(df["reign_days"], errors="coerce")
    if "won_date" in df.columns:
        df["won_date"] = pd.to_datetime(df["won_date"], errors="coerce")

    df = df.drop_duplicates(subset=[c for c in ["title", "holder"] if c in df.columns])

    for col in ["title", "holder", "won_date", "reign_days"]:
        if col not in df.columns:
            df[col] = pd.NA

    return df[["title", "holder", "won_date", "reign_days"]]
