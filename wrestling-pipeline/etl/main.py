
import logging
from logging_config import configure_logging

from extract_thesportsdb import get_wrestler
from extract_wikipedia import extract_wikipedia_pages
from extract_kaggle import extract_from_sqlite
from transform import clean_wrestlers, clean_champions
from load import load_data
from validate import validate_and_report


def run_pipeline(sample_names=None, out_prefix: str = "validation_report"):
    configure_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting pipeline", extra={"etl_stage": "start"})

    # Simple extraction: call external APIs for a list of sample names
    if sample_names is None:
        sample_names = ["Undertaker", "John_Cena", "Roman_Reigns"]

    logger.info("Extrayendo datos", extra={"etl_stage": "extract"})
    wrestlers_list = []
    for name in sample_names:
        w = get_wrestler(name)
        if w:
            wrestlers_list.append(w)

    wrestlers_df = None
    if wrestlers_list:
        import pandas as pd

        wrestlers_df = pd.DataFrame(wrestlers_list)

    # Also try to extract any local sqlite source (kaggle / provided DB)
    try:
        matches_df = extract_from_sqlite()
        logger.info("Extracted matches", extra={"rows": len(matches_df)})
    except Exception:
        matches_df = None

    logger.info("Transformando datos", extra={"etl_stage": "transform"})
    if wrestlers_df is not None:
        wrestlers_df = clean_wrestlers(wrestlers_df)
    champions_df = None
    try:
        champions_raw = None
        # attempt to read champions file if exists
        import os
        import pandas as pd

        champions_path = os.path.join("..", "data", "raw", "champions.csv")
        if os.path.exists(champions_path):
            champions_raw = pd.read_csv(champions_path)
    except Exception:
        champions_raw = None

    if champions_raw is not None:
        champions_df = clean_champions(champions_raw)

    logger.info("Validando datos", extra={"etl_stage": "validate"})
    reports = validate_and_report(wrestlers_df=wrestlers_df, champions_df=champions_df, out_prefix=out_prefix)
    logger.info("Validation reports", extra={"reports": reports})

    logger.info("Cargando datos", extra={"etl_stage": "load"})
    load_data(wrestlers_df=wrestlers_df, champions_df=champions_df)

    logger.info("ETL completado", extra={"etl_stage": "done"})


if __name__ == "__main__":
    run_pipeline()