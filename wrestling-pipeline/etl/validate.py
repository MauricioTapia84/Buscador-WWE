import json
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from typing import Tuple


def _write_report(report: dict, path: str):
    with open(path, "w", encoding="utf8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def validate_wrestlers(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Validate wrestlers dataframe and return (validated_df, report).

    Report contains counts and list of errors (if any).
    """
    schema = DataFrameSchema(
        {
            "name": Column(pa.String, Check(lambda s: s.str.len() > 0), nullable=False),
            "height_cm": Column(pa.Float, nullable=True),
            "weight_kg": Column(pa.Float, nullable=True),
            "nationality": Column(pa.String, nullable=True),
            "description": Column(pa.String, nullable=True),
            "debut_year": Column(pa.Int, Check(lambda v: (v > 1800) & (v <= 2100)), nullable=True),
        },
        coerce=True,
    )
    try:
        validated = schema.validate(df, lazy=True)
        report = {"rows": len(df), "errors": [], "status": "ok"}
    except pa.errors.SchemaErrors as e:
        validated = e.failure_cases
        report = {
            "rows": len(df),
            "errors": e.failure_cases.to_dict(orient="records"),
            "status": "failed",
        }
    return validated, report


def validate_champions(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    schema = DataFrameSchema(
        {
            "title": Column(pa.String, nullable=False),
            "holder": Column(pa.String, nullable=False),
            "won_date": Column(pa.DateTime, nullable=True),
            "reign_days": Column(pa.Int, Check(lambda v: v >= 0), nullable=True),
        },
        coerce=True,
    )
    try:
        validated = schema.validate(df, lazy=True)
        report = {"rows": len(df), "errors": [], "status": "ok"}
    except pa.errors.SchemaErrors as e:
        validated = e.failure_cases
        report = {"rows": len(df), "errors": e.failure_cases.to_dict(orient="records"), "status": "failed"}
    return validated, report


def validate_and_report(wrestlers_df: pd.DataFrame = None, champions_df: pd.DataFrame = None, out_prefix: str = "validation_report") -> dict:
    reports = {}
    if wrestlers_df is not None:
        _, r = validate_wrestlers(wrestlers_df)
        reports["wrestlers"] = r
        _write_report(r, f"{out_prefix}_wrestlers.json")
    if champions_df is not None:
        _, r = validate_champions(champions_df)
        reports["champions"] = r
        _write_report(r, f"{out_prefix}_champions.json")
    return reports


__all__ = ["validate_wrestlers", "validate_champions", "validate_and_report"]

from pydantic import BaseModel

class Wrestler(BaseModel):

    name: str

    height: str | None = None

    weight: str | None = None


def validate_wrestler(data):

    try:
        Wrestler(**data)
        return True

    except Exception as e:

        print(e)

        return False
