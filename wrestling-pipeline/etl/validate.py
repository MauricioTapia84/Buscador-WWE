import json
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from typing import Tuple


def _write_report(report: dict, path: str):
    # Write JSON
    with open(path, "w", encoding="utf8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # If there are error records, write a CSV
    csv_path = path.replace('.json', '.csv')
    try:
        if report.get('errors'):
            import pandas as _pd

            df_err = _pd.DataFrame(report['errors'])
            df_err.to_csv(csv_path, index=False, encoding='utf-8')
        else:
            # write a small CSV summary
            with open(csv_path, 'w', encoding='utf8') as _f:
                _f.write('rows,status,errors_count\n')
                _f.write(f"{report.get('rows',0)},{report.get('status','')},0\n")
    except Exception:
        # best-effort: don't fail reporting
        pass

    # Write simple HTML report
    html_path = path.replace('.json', '.html')
    try:
        with open(html_path, 'w', encoding='utf8') as hf:
            hf.write(f"<html><head><meta charset='utf-8'><title>Validation report</title></head><body>")
            hf.write(f"<h1>Validation report</h1><p>rows: {report.get('rows',0)}</p>")
            hf.write(f"<p>status: {report.get('status','')}</p>")
            if report.get('errors'):
                import pandas as _pd

                df_err = _pd.DataFrame(report['errors'])
                hf.write(df_err.to_html(index=False, escape=True))
            else:
                hf.write('<p>No errors</p>')
            hf.write('</body></html>')
    except Exception:
        pass


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
            "debut_year": Column(pa.Float, Check(lambda v: (v > 1800) & (v <= 2100)), nullable=True),
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
