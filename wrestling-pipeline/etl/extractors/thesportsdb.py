import json
import logging
import os
import shutil
import time
from hashlib import sha1
from typing import List, Optional

try:
    from rapidfuzz import fuzz, process
    _HAS_RAPIDFUZZ = True
except ImportError:
    fuzz = None
    process = None
    _HAS_RAPIDFUZZ = False

import pandas as pd
import requests

try:
    from ..name_utils import clean_name, normalize_name_columns, slugify_name
    from ..utils.retry_utils import requests_get_with_retry
except ImportError:
    from name_utils import clean_name, normalize_name_columns, slugify_name
    from utils.retry_utils import requests_get_with_retry

API_BASE = "https://www.thesportsdb.com/api/v1/json"
CACHE_DIR = os.path.join("data", "raw", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{sha1(key.encode()).hexdigest()}.json")


def _cache_get(key: str):
    import sys
    if "pytest" in sys.modules:
        return None
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _cache_set(key: str, value):
    import sys
    if "pytest" in sys.modules:
        return
    path = _cache_path(key)
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(value, handle)
    except Exception:
        pass


def _is_strict_name_match(query: str, candidate: str) -> bool:
    query_slug = slugify_name(query)
    candidate_slug = slugify_name(candidate)
    if not query_slug or not candidate_slug:
        return False
    if query_slug == candidate_slug:
        return True

    query_tokens = {token for token in query_slug.split() if len(token) > 1}
    candidate_tokens = set(candidate_slug.split())
    return len(query_tokens) >= 2 and query_tokens.issubset(candidate_tokens)


def _search_cached_players(query: str) -> list[dict]:
    if not os.path.exists(CACHE_DIR):
        return []

    best_player = None
    best_score = 0.0
    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(CACHE_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            continue

        if not isinstance(payload, list):
            continue

        for player in payload:
            if not isinstance(player, dict) or not clean_name(player.get("strPlayer")):
                continue
            if not (
                _is_strict_name_match(query, player.get("strPlayer"))
                or _is_strict_name_match(query, player.get("strRealName"))
            ):
                continue
            score = _player_match_score(query, player)
            if score > best_score:
                best_player = player
                best_score = score

    if best_player and best_score >= 500:
        return [best_player]
    return []


def _api_key() -> str:
    return os.getenv("THESPORTSDB_API_KEY", "3")


def fetch_wrestlers_by_name(name_query: str) -> list[dict]:
    query = clean_name(name_query)
    if not query:
        return []

    key = f"searchplayers:{query}"
    cached = _cache_get(key)
    if cached is not None:
        best_cached = _pick_best_player(query, cached)
        if best_cached:
            return [best_cached]

    cached_scan = _search_cached_players(query)
    if cached_scan:
        _cache_set(key, cached_scan)
        return cached_scan

    logger = logging.getLogger("etl.extract_thesportsdb")
    url = f"{API_BASE}/{_api_key()}/searchplayers.php?p={requests.utils.quote(query)}"

    try:
        response = requests_get_with_retry(url, timeout=10)
        data = response.json() or {}
        players = data.get("player") or []
        time.sleep(0.15)
    except Exception as exc:
        logger.warning("fetch failed", extra={"error": str(exc), "query_name": query})
        players = []

    if not players and " " in query:
        for token in [part for part in query.split(" ") if part][:2]:
            try:
                token_url = f"{API_BASE}/{_api_key()}/searchplayers.php?p={requests.utils.quote(token)}"
                response = requests_get_with_retry(token_url, timeout=8)
                data = response.json() or {}
                players = data.get("player") or []
                if players:
                    break
            except Exception:
                continue

    _cache_set(key, players)
    return players


def fetch_players_by_team(team_id: str) -> list[dict]:
    key = f"lookup_team:{team_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    url = f"{API_BASE}/{_api_key()}/lookup_all_players.php?id={requests.utils.quote(str(team_id))}"
    logger = logging.getLogger("etl.extract_thesportsdb")

    try:
        response = requests_get_with_retry(url, timeout=12)
        data = response.json() or {}
        players = data.get("player") or []
        time.sleep(0.15)
    except Exception as exc:
        logger.warning("fetch team failed", extra={"error": str(exc), "team_id": team_id})
        players = []

    _cache_set(key, players)
    return players


def search_teams_by_name(name_query: str) -> list[dict]:
    query = clean_name(name_query)
    if not query:
        return []

    key = f"searchteams:{query}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    url = f"{API_BASE}/{_api_key()}/searchteams.php?t={requests.utils.quote(query)}"
    logger = logging.getLogger("etl.extract_thesportsdb")

    try:
        response = requests_get_with_retry(url, timeout=12)
        data = response.json() or {}
        teams = data.get("teams") or []
        time.sleep(0.15)
    except Exception as exc:
        logger.warning("team search failed", extra={"error": str(exc), "query": query})
        teams = []

    _cache_set(key, teams)
    return teams


def search_teams_by_league(league_name: str) -> list[dict]:
    league = clean_name(league_name)
    if not league:
        return []

    key = f"searchteams_league:{league}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    url = f"{API_BASE}/{_api_key()}/search_all_teams.php?l={requests.utils.quote(league)}"
    logger = logging.getLogger("etl.extract_thesportsdb")

    try:
        response = requests_get_with_retry(url, timeout=12)
        data = response.json() or {}
        teams = data.get("teams") or []
        time.sleep(0.15)
    except Exception as exc:
        logger.warning("league team search failed", extra={"error": str(exc), "league": league})
        teams = []

    _cache_set(key, teams)
    return teams


def _pick_best_team(query: str, teams: list[dict]) -> dict | None:
    if not teams:
        return None

    lowered = query.lower()
    for team in teams:
        if clean_name(team.get("strTeam")).lower() == lowered:
            return team

    if _HAS_RAPIDFUZZ:
        options = [clean_name(team.get("strTeam")) for team in teams]
        match = process.extractOne(query, options, scorer=fuzz.WRatio)
        if match and match[1] >= 75:
            for team in teams:
                if clean_name(team.get("strTeam")) == match[0]:
                    return team

    return teams[0]


def _player_match_score(query: str, player: dict) -> float:
    player_name = clean_name(player.get("strPlayer"))
    real_name = clean_name(player.get("strRealName"))
    team_name = clean_name(player.get("strTeam"))
    sport = clean_name(player.get("strSport")).lower()
    position = clean_name(player.get("strPosition")).lower()

    query_slug = slugify_name(query)
    player_slug = slugify_name(player_name)
    real_slug = slugify_name(real_name)

    score = 0.0
    if player_slug and query_slug:
        score += 100 * (player_slug == query_slug)
        score += 50 * (player_slug in query_slug or query_slug in player_slug)
    if real_slug and query_slug:
        score += 40 * (real_slug == query_slug)
    if team_name:
        score += 10 if query_slug in slugify_name(team_name) else 0
    if sport:
        score += 5 if 'wrestling' in sport else 0
    if position:
        score += 3 if 'wrest' in position else 0
    return float(score)


def _pick_best_player(query: str, players: list[dict]) -> dict | None:
    if not players:
        return None
    if len(players) == 1:
        return players[0]
    if _HAS_RAPIDFUZZ:
        options = [clean_name(p.get("strPlayer")) for p in players if clean_name(p.get("strPlayer"))]
        match = process.extractOne(query, options, scorer=fuzz.WRatio)
        if match and match[1] >= 75:
            for p in players:
                if clean_name(p.get("strPlayer")) == match[0]:
                    return p
    return players[0]


def extract_all(sample_names: Optional[List[str]] = None) -> pd.DataFrame:
    rows = []
    if not sample_names:
        return pd.DataFrame(rows)

    logger = logging.getLogger("etl.extract_thesportsdb")
    for name in sample_names:
        players = fetch_wrestlers_by_name(name)
        for p in players:
            try:
                rows.append({
                    "id": p.get("idPlayer"),
                    "name": p.get("strPlayer") or name,
                    "real_name": p.get("strRealName"),
                    "promotion": p.get("strTeam"),
                    "height": p.get("strHeight"),
                    "weight": p.get("strWeight"),
                    "date_born": p.get("dateBorn"),
                    "nationality": p.get("strNationality"),
                    "debut": p.get("strDebut"),
                    "retired": p.get("strRetired"),
                    "image_url": p.get("strThumb") or p.get("strRender"),
                    "image_large": p.get("strImage"),
                    "team": p.get("strTeam"),
                    "description": p.get("strDescriptionEN"),
                    "source": "thesportsdb",
                })
            except Exception as exc:
                logger.debug("skipping player record", extra={"error": str(exc), "player": p})
    return pd.DataFrame(rows)


def extract_players_for_team_names(team_names: List[str]) -> pd.DataFrame:
    rows = []
    logger = logging.getLogger("etl.extract_thesportsdb")
    for team_name in team_names:
        teams = search_teams_by_name(team_name)
        if not teams:
            continue
        best_team = _pick_best_team(team_name, teams)
        if not best_team:
            continue
        team_id = best_team.get("idTeam")
        if not team_id:
            continue
        players = fetch_players_by_team(team_id)
        for p in players:
            try:
                rows.append({
                    "id": p.get("idPlayer"),
                    "name": p.get("strPlayer"),
                    "real_name": p.get("strRealName"),
                    "promotion": p.get("strTeam") or best_team.get("strTeam"),
                    "height": p.get("strHeight"),
                    "weight": p.get("strWeight"),
                    "date_born": p.get("dateBorn"),
                    "nationality": p.get("strNationality"),
                    "debut": p.get("strDebut"),
                    "retired": p.get("strRetired"),
                    "image_url": p.get("strThumb") or p.get("strRender"),
                    "image_large": p.get("strImage"),
                    "team": p.get("strTeam") or best_team.get("strTeam"),
                    "description": p.get("strDescriptionEN"),
                    "source": "thesportsdb",
                })
            except Exception as exc:
                logger.debug("skipping player record", extra={"error": str(exc), "player": p})
    return pd.DataFrame(rows)


def get_wrestler(name_query: str) -> dict | None:
    players = fetch_wrestlers_by_name(name_query)
    if not players:
        return None
    p = players[0]
    return {
        "id": p.get("idPlayer"),
        "name": p.get("strPlayer") or name_query,
        "real_name": p.get("strRealName"),
        "promotion": p.get("strTeam"),
        "height": p.get("strHeight"),
        "weight": p.get("strWeight"),
        "date_born": p.get("dateBorn"),
        "nationality": p.get("strNationality"),
        "debut": p.get("strDebut"),
        "retired": p.get("strRetired"),
        "image_url": p.get("strThumb") or p.get("strRender"),
        "image_large": p.get("strImage"),
        "team": p.get("strTeam"),
        "description": p.get("strDescriptionEN"),
        "source": "thesportsdb",
    }


def run_and_save(sample_names: List[str], out_dir: str = "../data/processed"):
    df = extract_all(sample_names)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "wrestlers_thesportsdb.csv")
    parquet_path = os.path.join(out_dir, "wrestlers_thesportsdb.parquet")
    try:
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
    except Exception:
        df.to_csv(csv_path, index=False)

    try:
        meta = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "rows": len(df),
            "source": "thesportsdb",
        }
        with open(os.path.join(out_dir, "wrestlers_thesportsdb_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f)
    except Exception:
        pass


def run_and_save_with_images(sample_names: List[str], out_dir: str = "../data/processed", images_dir: str = "../data/processed/images"):
    df = extract_all(sample_names)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    for i, row in df.iterrows():
        img_url = row.get("image_url")
        if not img_url:
            continue
        try:
            response = requests_get_with_retry(img_url, timeout=10)
            if response and response.status_code == 200:
                ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
                filename = f"{row.get('id') or i}{ext}"
                path = os.path.join(images_dir, filename)
                with open(path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                df.at[i, 'image_path'] = path
        except Exception:
            continue
    run_and_save(sample_names, out_dir=out_dir)
