
import logging
import os
import sys

# Ensure the repository root is importable when running `python etl/main.py`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from utils.logging_config import configure_logging
    from etl.unify_sources import run_unification
except ImportError:
    from etl.utils.logging_config import configure_logging
    from etl.unify_sources import run_unification


def run_pipeline(out_prefix: str = "validation_report"):
    configure_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting ETL pipeline", extra={"etl_stage": "start"})

    raw_dir = os.getenv("DATA_RAW", "data/raw")
    processed_dir = os.getenv("DATA_PROCESSED", "data/processed")
    os.makedirs(processed_dir, exist_ok=True)

    logger.info("Running source unification", extra={"raw_dir": raw_dir, "processed_dir": processed_dir})
    try:
        run_unification(raw_dir=raw_dir, processed_dir=processed_dir)
        logger.info("Unificación finalizada con éxito.")
    except Exception:
        logger.exception("Error en unificación")

    logger.info("ETL completado", extra={"etl_stage": "done"})


if __name__ == "__main__":
    run_pipeline()
