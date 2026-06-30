
import logging
try:
    from utils.logging_config import configure_logging
    from extract_thesportsdb import get_wrestler
    from extract_wikipedia import extract_wikipedia_pages
    from extract_kaggle import extract_from_sqlite
    from transform import clean_wrestlers, clean_champions
    from load import load_data
    from validate import validate_and_report
except ImportError:
    from etl.utils.logging_config import configure_logging
    from etl.extract_thesportsdb import get_wrestler
    from etl.extract_wikipedia import extract_wikipedia_pages
    from etl.extract_kaggle import extract_from_sqlite
    from etl.transform import clean_wrestlers, clean_champions
    from etl.load import load_data
    from etl.validate import validate_and_report


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
    try:
        from unify import run_unification
        run_unification()
        logger.info("Unificación finalizada con éxito.")
    except Exception as e:
        logger.error(f"Error en unificación: {e}")

    logger.info("ETL completado", extra={"etl_stage": "done"})


if __name__ == "__main__":
    run_pipeline()
