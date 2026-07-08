"""ETL package initializer.

This file makes the `etl` directory importable as a package for tests and CI.
"""

from . import extract_thesportsdb
from . import extract_thesportsdb
from .extractors import (
    read_kaggle_tables,
    extract_from_sqlite,
    normalize_matches_df,
    extract_wrestlers_from_thesportsdb,
    extract_wikipedia_pages,
)
from .transform import clean_wrestlers, clean_champions, normalize_wrestlers, normalize_matches
from .load import load_data
from .validate import validate_and_report
from .utils import configure_logging, requests_get_with_retry, retry_on_exception

__all__ = [
    "read_kaggle_tables",
    "extract_from_sqlite",
    "normalize_matches_df",
    "extract_wrestlers_from_thesportsdb",
    "extract_wikipedia_pages",
    "extract_thesportsdb",
    "clean_wrestlers",
    "clean_champions",
    "normalize_wrestlers",
    "normalize_matches",
    "load_data",
    "validate_and_report",
    "configure_logging",
    "requests_get_with_retry",
    "retry_on_exception",
]
