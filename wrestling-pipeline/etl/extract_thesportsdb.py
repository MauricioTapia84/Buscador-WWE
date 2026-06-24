import os
from typing import List

try:
    from etl.extractors.thesportsdb import extract_all, fetch_wrestlers_by_name, fetch_players_by_team, search_teams_by_name, search_teams_by_league, get_wrestler, run_and_save, run_and_save_with_images, extract_players_for_team_names
except ImportError:
    from extractors.thesportsdb import extract_all, fetch_wrestlers_by_name, fetch_players_by_team, search_teams_by_name, search_teams_by_league, get_wrestler, run_and_save, run_and_save_with_images, extract_players_for_team_names

__all__ = [
    "extract_all",
    "fetch_wrestlers_by_name",
    "fetch_players_by_team",
    "search_teams_by_name",
    "search_teams_by_league",
    "get_wrestler",
    "run_and_save",
    "run_and_save_with_images",
    "extract_players_for_team_names",
]


if __name__ == '__main__':
    sample = [name.strip() for name in os.getenv("SAMPLE_NAMES", "").split(",") if name.strip()]
    run_and_save(sample)
