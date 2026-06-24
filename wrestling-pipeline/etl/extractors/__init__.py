"""Extractor subpackage for the Wrestling Pipeline ETL."""

from .kaggle import read_kaggle_tables, extract_from_sqlite, save_matches_csv, normalize_matches_df
from .thesportsdb import extract_all as extract_wrestlers_from_thesportsdb, fetch_wrestlers_by_name, run_and_save, run_and_save_with_images
from .wikipedia import extract_wikipedia_pages

__all__ = [
    "read_kaggle_tables",
    "extract_from_sqlite",
    "save_matches_csv",
    "normalize_matches_df",
    "extract_wrestlers_from_thesportsdb",
    "fetch_wrestlers_by_name",
    "run_and_save",
    "run_and_save_with_images",
    "extract_wikipedia_pages",
]
