import os
from typing import List

try:
    from etl.extractors import thesportsdb as _impl
    from etl.extractors.thesportsdb import extract_all, fetch_wrestlers_by_name, fetch_players_by_team, search_teams_by_name, search_teams_by_league, extract_players_for_team_names, run_and_save, run_and_save_with_images
    from etl.utils.retry_utils import requests_get_with_retry
except ImportError:
    from extractors import thesportsdb as _impl
    from extractors.thesportsdb import extract_all, fetch_wrestlers_by_name, fetch_players_by_team, search_teams_by_name, search_teams_by_league, extract_players_for_team_names, run_and_save, run_and_save_with_images
    from utils.retry_utils import requests_get_with_retry


def get_wrestler(name_query: str):
    if not hasattr(_impl, 'requests_get_with_retry'):
        _impl.requests_get_with_retry = requests_get_with_retry
    payload = _impl.get_wrestler(name_query)
    if not payload:
        return None
    return {
        "id": payload.get("id") or payload.get("idPlayer"),
        "name": payload.get("name") or payload.get("strPlayer") or name_query,
        "height": payload.get("height") or payload.get("strHeight"),
        "weight": payload.get("weight") or payload.get("strWeight"),
        "nationality": payload.get("nationality") or payload.get("strNationality"),
        "description": payload.get("description") or payload.get("strDescriptionEN"),
    }

__all__ = [
    "extract_all",
    "fetch_wrestlers_by_name",
    "fetch_players_by_team",
    "search_teams_by_name",
    "search_teams_by_league",
    "get_wrestler",
    "run_and_save",
    "run_and_save_with_images",
    "requests_get_with_retry",
]


if __name__ == '__main__':
    sample = [name.strip() for name in os.getenv("SAMPLE_NAMES", "").split(",") if name.strip()]
    run_and_save(sample)
