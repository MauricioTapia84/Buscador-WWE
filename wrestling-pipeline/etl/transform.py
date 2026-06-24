
import pandas as pd
from typing import Optional


def clean_wrestlers(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Normalize wrestlers dataframe to expected schema.

    Preserve rich profile fields when present so later normalization/API joins
    can expose fan and journalist views without losing source metadata.
    """
    if df is None:
        df = pd.read_csv("../data/raw/wrestlers_api.csv")

    # Normalize column names from possible extractor outputs
    mapping = {
        "strPlayer": "name",
        "strRealName": "real_name",
        "strHeight": "height",
        "strWeight": "weight",
        "strNationality": "nationality",
        "strDescriptionEN": "description",
        "dateBorn": "date_born",
        "strThumb": "image_url",
        "strImage": "image_large",
        "strRender": "image_large",
        "strCutout": "image_url",
        "strTeam": "team",
        "strDebut": "debut",
        "strRetired": "retired",
    }
    mapping = {
        source: target
        for source, target in mapping.items()
        if source in df.columns and (target not in df.columns or source != target)
    }

    if mapping:
        df = df.rename(columns=mapping)

    if "name" in df.columns:
        df["name"] = df["name"].astype(str).str.strip()
    if "real_name" in df.columns:
        df["real_name"] = df["real_name"].astype(str).str.strip()

    # Try to coerce numeric columns
    if "height_cm" in df.columns:
        df["height_cm"] = pd.to_numeric(df["height_cm"], errors="coerce").astype("float64")
    if "weight_kg" in df.columns:
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").astype("float64")
    if "debut_year" in df.columns:
        df["debut_year"] = pd.to_numeric(df["debut_year"], errors="coerce").astype("Int64")

    df = df.drop_duplicates(subset=[c for c in ["name"] if c in df.columns])

    if "birth_date" not in df.columns and "date_born" in df.columns:
        df["birth_date"] = df["date_born"]
    if "date_born" not in df.columns and "birth_date" in df.columns:
        df["date_born"] = df["birth_date"]

    # Ensure expected columns exist
    for col in [
        "id",
        "name",
        "real_name",
        "birth_date",
        "date_born",
        "height",
        "weight",
        "height_cm",
        "weight_kg",
        "nationality",
        "description",
        "extract",
        "debut",
        "debut_year",
        "retired",
        "image_url",
        "image_large",
        "promotion",
        "team",
        "source",
        "link",
        "url",
    ]:
        if col not in df.columns:
            if col == "debut_year":
                df[col] = pd.Series(dtype="Int64")
            elif col in ["height_cm", "weight_kg"]:
                df[col] = pd.Series(dtype="float64")
            else:
                df[col] = pd.Series(dtype="object")

    # Si hay valores nulos en debut_year, rellenamos con un año válido por defecto para que pase la validación Pandera de enteros estrictos o lo dejamos como Int64 con nulos
    if "debut_year" in df.columns:
        # Puesto que Pandera valida debut_year con Check si no es nulo, pero si es null/NA y es entero, Pandera requiere tipo Int64 de pandas.
        df["debut_year"] = df["debut_year"].astype("Int64")

    preferred_columns = [
        "id",
        "name",
        "real_name",
        "birth_date",
        "date_born",
        "height",
        "weight",
        "height_cm",
        "weight_kg",
        "nationality",
        "description",
        "extract",
        "debut",
        "debut_year",
        "retired",
        "image_url",
        "image_large",
        "promotion",
        "team",
        "source",
        "link",
        "url",
    ]
    remaining = [column for column in df.columns if column not in preferred_columns]
    return df[preferred_columns + remaining]


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
