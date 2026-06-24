"""Extractor subpackage for the Wrestling Pipeline ETL."""

from .kaggle import read_kaggle_tables, extract_from_sqlite, save_matches_csv, normalize_matches_df
from .thesportsdb import extract_all as extract_wrestlers_from_thesportsdb, fetch_wrestlers_by_name, get_wrestler, run_and_save, run_and_save_with_images
from .wikipedia import extract_wikipedia_pages, extract_from_wikipedia_urls, extract_wwe_champions_page, enrich_wrestlers, enrich_events, run_and_save as run_wikipedia_save

__all__ = [
    "read_kaggle_tables",
    "extract_from_sqlite",
    "save_matches_csv",
    "normalize_matches_df",
    "extract_wrestlers_from_thesportsdb",
    "fetch_wrestlers_by_name",
    "get_wrestler",
    "run_and_save",
    "run_and_save_with_images",
    "extract_wikipedia_pages",
    "extract_from_wikipedia_urls",
    "extract_wwe_champions_page",
    "enrich_wrestlers",
    "enrich_events",
    "run_wikipedia_save",
]
