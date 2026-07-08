import pandas as pd
import numpy as np
import os
import logging
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("etl.unify")

def load_data(raw_dir: str):
    logger.info("Cargando datos crudos desde Kaggle")
    matches = pd.read_csv(os.path.join(raw_dir, 'matches.csv'))
    titles = pd.read_csv(os.path.join(raw_dir, 'titles.csv'))
    wrestlers = pd.read_csv(os.path.join(raw_dir, 'wrestlers.csv'))
    return matches, titles, wrestlers

def transform_data(matches, titles, wrestlers):
    logger.info("Aplicando transformaciones avanzadas de Pandas")
    
    # Estandarización de nombres
    wrestlers['name'] = wrestlers['name'].str.strip().str.title()
    
    # Manejo de nulos básicos
    matches['title_id'] = matches['title_id'].fillna(0).astype(int)
    matches['title_change'] = matches['title_change'].fillna(0).astype(int)
    
    # Feature Engineering: Victorias por luchador
    logger.info("Calculando historial de victorias (Agrupaciones)")
    wins = matches.groupby('winner_id').size().reset_index(name='total_wins')
    wins = wins.rename(columns={'winner_id': 'id'})
    
    # Feature Engineering: Derrotas por luchador
    losses = matches.groupby('loser_id').size().reset_index(name='total_losses')
    losses = losses.rename(columns={'loser_id': 'id'})
    
    # Combinar historial
    stats = pd.merge(wrestlers, wins, on='id', how='left')
    stats = pd.merge(stats, losses, on='id', how='left')
    stats['total_wins'] = stats['total_wins'].fillna(0)
    stats['total_losses'] = stats['total_losses'].fillna(0)
    stats['total_matches'] = stats['total_wins'] + stats['total_losses']
    
    # Feature Engineering: Ratio de victorias
    stats['win_rate'] = np.where(stats['total_matches'] > 0, stats['total_wins'] / stats['total_matches'], 0)
    
    # Feature Engineering: Campeonatos ganados
    logger.info("Calculando campeonatos obtenidos (Vectorización)")
    championship_matches = matches[matches['title_change'] == 1]
    title_wins = championship_matches.groupby('winner_id').size().reset_index(name='total_titles')
    title_wins = title_wins.rename(columns={'winner_id': 'id'})
    
    stats = pd.merge(stats, title_wins, on='id', how='left')
    stats['total_titles'] = stats['total_titles'].fillna(0)
    
    # Variable Objetivo para ML: ¿Ha sido campeón o será campeón?
    stats['is_champion'] = (stats['total_titles'] > 0).astype(int)
    
    return stats

def run_unification():
    raw_dir = os.path.join('data', 'raw')
    processed_dir = os.path.join('data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    matches, titles, wrestlers = load_data(raw_dir)
    stats = transform_data(matches, titles, wrestlers)
    
    out_path = os.path.join(processed_dir, 'wrestling_clean.csv')
    stats.to_csv(out_path, index=False)
    logger.info(f"Dataset unificado guardado en: {out_path} con {len(stats)} registros")
    
if __name__ == '__main__':
    run_unification()
