import os
import logging
from pathlib import Path

import pandas as pd

from .extract_kaggle import read_kaggle_tables
from .clean import clean_dataframe, dedupe_dataframe
from .impute import impute_wrestler_stats
from .feature_engineering import engineer_features
from .create_target import create_champion_target
from .transform.clean import clean_wrestlers, clean_champions

LOGGER = logging.getLogger("etl.unify_sources")


def _load_raw_sources(raw_dir: str) -> dict[str, pd.DataFrame]:
    LOGGER.info("Cargando fuentes crudas desde raw", extra={"raw_dir": raw_dir})
    raw = read_kaggle_tables(raw_folder=raw_dir)

    raw_wrestlers = raw.get('wrestlers', pd.DataFrame())
    raw_matches = raw.get('matches', pd.DataFrame())
    raw_titles = raw.get('titles', pd.DataFrame())

    if raw_wrestlers.empty:
        fallback = Path(raw_dir) / 'wrestlers.csv'
        if fallback.exists():
            raw_wrestlers = pd.read_csv(fallback)

    if raw_matches.empty:
        fallback = Path(raw_dir) / 'matches.csv'
        if fallback.exists():
            raw_matches = pd.read_csv(fallback)

    if raw_titles.empty:
        fallback = Path(raw_dir) / 'titles.csv'
        if fallback.exists():
            raw_titles = pd.read_csv(fallback)

    return {
        'wrestlers': raw_wrestlers,
        'matches': raw_matches,
        'titles': raw_titles,
    }


def _build_clean_wrestlers(raw_wrestlers: pd.DataFrame, processed_dir: str) -> pd.DataFrame:
    if raw_wrestlers.empty:
        return pd.DataFrame()

    cleaned = clean_wrestlers(raw_wrestlers)
    cleaned = clean_dataframe(cleaned)
    cleaned = dedupe_dataframe(cleaned, subset=['name', 'name_slug'])
    cleaned = impute_wrestler_stats(cleaned)
    cleaned.to_csv(os.path.join(processed_dir, 'wrestlers_cleaned.csv'), index=False)
    return cleaned


def _build_clean_titles(raw_titles: pd.DataFrame, processed_dir: str) -> pd.DataFrame:
    if raw_titles.empty:
        return pd.DataFrame()

    cleaned = clean_champions(raw_titles)
    cleaned = clean_dataframe(cleaned)
    cleaned.to_csv(os.path.join(processed_dir, 'titles_cleaned.csv'), index=False)
    return cleaned


def _build_clean_matches(raw_matches: pd.DataFrame, processed_dir: str) -> pd.DataFrame:
    if raw_matches.empty:
        return pd.DataFrame()

    cleaned = clean_dataframe(raw_matches)
    cleaned.to_csv(os.path.join(processed_dir, 'matches_cleaned.csv'), index=False)
    return cleaned


def _join_sources(wrestlers: pd.DataFrame, matches: pd.DataFrame, titles: pd.DataFrame) -> pd.DataFrame:
    if wrestlers.empty:
        return pd.DataFrame()

    enriched = wrestlers.copy()

    if 'id' in enriched.columns:
        enriched['id'] = pd.to_numeric(enriched['id'], errors='coerce')

    if not matches.empty and 'winner_id' in matches.columns:
        matches['winner_id'] = pd.to_numeric(matches['winner_id'], errors='coerce')
        wins = matches.groupby('winner_id').size().rename('total_wins')
        losses = matches.groupby('loser_id').size().rename('total_losses')
        enriched = enriched.merge(wins, left_on='id', right_index=True, how='left')
        enriched = enriched.merge(losses, left_on='id', right_index=True, how='left')
        enriched['total_wins'] = enriched['total_wins'].fillna(0)
        enriched['total_losses'] = enriched['total_losses'].fillna(0)
        enriched['total_matches'] = enriched['total_wins'] + enriched['total_losses']
        enriched['win_rate'] = enriched.apply(
            lambda row: row['total_wins'] / row['total_matches'] if row['total_matches'] > 0 else 0.0,
            axis=1,
        )

    champion_counts = pd.Series(0, index=enriched.index, name='total_titles')

    if not titles.empty and 'holder' in titles.columns:
        title_champion_counts = titles.groupby('holder').size().rename('total_titles')
        enriched = enriched.merge(title_champion_counts, left_on='name', right_index=True, how='left')
        enriched['total_titles'] = enriched['total_titles'].fillna(0)
    else:
        enriched['total_titles'] = 0

    if not matches.empty and 'title_change' in matches.columns and 'winner_id' in matches.columns:
        title_change_counts = matches[matches['title_change'] == 1].groupby('winner_id').size().rename('total_titles_match')
        enriched = enriched.merge(title_change_counts, left_on='id', right_index=True, how='left')
        enriched['total_titles_match'] = enriched['total_titles_match'].fillna(0)
        enriched['total_titles'] = enriched['total_titles'] + enriched['total_titles_match']
        enriched.drop(columns=['total_titles_match'], inplace=True)

    enriched['total_matches'] = enriched.get('total_matches', 0).fillna(0)
    enriched['win_rate'] = enriched.get('win_rate', 0.0).fillna(0.0)

    enriched = create_champion_target(enriched)
    enriched = engineer_features(enriched)
    return enriched


def run_unification(raw_dir: str = 'data/raw', processed_dir: str = 'data/processed') -> None:
    os.makedirs(processed_dir, exist_ok=True)
    sources = _load_raw_sources(raw_dir)
    wrestlers = _build_clean_wrestlers(sources['wrestlers'], processed_dir)
    matches = _build_clean_matches(sources['matches'], processed_dir)
    titles = _build_clean_titles(sources['titles'], processed_dir)

    final = _join_sources(wrestlers, matches, titles)
    final_path = os.path.join(processed_dir, 'wrestling_clean.csv')
    final.to_csv(final_path, index=False)
    LOGGER.info('Wrote unified dataset', extra={'path': final_path, 'rows': len(final)})

    if not matches.empty:
        matches.to_csv(os.path.join(processed_dir, 'matches_cleaned.csv'), index=False)
    if not titles.empty:
        titles.to_csv(os.path.join(processed_dir, 'titles_cleaned.csv'), index=False)
