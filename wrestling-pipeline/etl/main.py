
import logging
from logging_config import configure_logging

from extract_thesportsdb import *
from extract_wikipedia import *
from extract_kaggle import *
from transform import *
from load import *


def run_pipeline():
    configure_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting pipeline")

    logger.info("Extrayendo datos...")
    # Ejecutar extractores

    logger.info("Transformando datos...")
    clean_wrestlers()
    clean_champions()

    logger.info("Cargando datos...")

    logger.info("ETL completado")


if __name__ == "__main__":
    run_pipeline()