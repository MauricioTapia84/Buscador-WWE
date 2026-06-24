import os
import logging
import pandas as pd

from etl.utils import configure_logging
from etl.extractors import extract_from_sqlite, extract_wrestlers_from_thesportsdb, extract_wikipedia_pages
from etl.transform import clean_wrestlers, clean_champions
from etl.load import load_data
from etl.validate import validate_and_report


def run_pipeline(sample_names=None, out_prefix: str = "validation_report"):
    configure_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting pipeline", extra={"etl_stage": "start"})

    if sample_names is None:
        sample_names = ["Undertaker", "John_Cena", "Roman_Reigns"]

    logger.info("Extrayendo datos", extra={"etl_stage": "extract"})
    wrestlers_list = []
    for name in sample_names:
        wrestlers_df = extract_wrestlers_from_thesportsdb([name])
        if not wrestlers_df.empty:
            wrestlers_list.append(wrestlers_df)

    if wrestlers_list:
        wrestlers_df = pd.concat(wrestlers_list, ignore_index=True, sort=False)
        wrestlers_df = clean_wrestlers(wrestlers_df)
    else:
        wrestlers_df = None

    try:
        matches_df = extract_from_sqlite()
        logger.info("Extracted matches", extra={"rows": len(matches_df)})
    except Exception:
        matches_df = None

    champions_df = None
    champions_path = os.path.join("..", "data", "raw", "champions.csv")
    if os.path.exists(champions_path):
        champions_raw = pd.read_csv(champions_path)
        champions_df = clean_champions(champions_raw)

    logger.info("Validando datos", extra={"etl_stage": "validate"})
    reports = validate_and_report(wrestlers_df=wrestlers_df, champions_df=champions_df, out_prefix=out_prefix)
    logger.info("Validation reports", extra={"reports": reports})

    logger.info("Cargando datos", extra={"etl_stage": "load"})
    load_data(wrestlers_df=wrestlers_df, champions_df=champions_df)

    logger.info("ETL completado", extra={"etl_stage": "done"})


if __name__ == "__main__":
    run_pipeline()
