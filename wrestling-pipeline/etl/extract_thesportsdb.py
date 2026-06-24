import json
import logging
import os
import shutil
import time
from datetime import datetime
from hashlib import sha1

import pandas as pd
import requests

try:
    from rapidfuzz import fuzz, process
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False

try:
    from retry_utils import requests_get_with_retry
    from name_utils import clean_name, normalize_name_columns, slugify_name
except ImportError:
    from etl.retry_utils import requests_get_with_retry
    from etl.name_utils import clean_name, normalize_name_columns, slugify_name

API_BASE = "https://www.thesportsdb.com/api/v1/json"
CACHE_DIR = os.path.join("data", "raw", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{sha1(key.encode()).hexdigest()}.json")


def _cache_get(key: str):
    if os.getenv("PYTEST_CURRENT_TEST"):
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
    if os.getenv("PYTEST_CURRENT_TEST"):
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
        response = requests_get_with_retry(url, timeout=10)
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
    if player_slug == query_slug:
        score += 1000
    elif player_slug and query_slug and query_slug in player_slug:
        score += 300

    if real_slug == query_slug:
        score += 700
    elif real_slug and query_slug and query_slug in real_slug:
        score += 150

    if sport == "fighting":
        score += 75
    if position == "wrestler":
        score += 50
    if "wwe" in team_name.lower():
        score += 40

    try:
        score += float(player.get("relevance") or 0)
    except Exception:
        pass

    if _HAS_RAPIDFUZZ and player_name:
        score += float(fuzz.WRatio(query, player_name))
        if real_name:
            score += float(fuzz.WRatio(query, real_name)) * 0.5

    return score


def _pick_best_player(query: str, players: list[dict]) -> dict | None:
    if not players:
        return None

    query_slug = slugify_name(query)
    exact_matches = [
        player
        for player in players
        if slugify_name(player.get("strPlayer")) == query_slug
    ]
    if exact_matches:
        players = exact_matches

    fighting_players = [
        player
        for player in players
        if clean_name(player.get("strSport")).lower() == "fighting"
        or clean_name(player.get("strPosition")).lower() == "wrestler"
    ]
    if fighting_players:
        players = fighting_players

    best = max(players, key=lambda player: _player_match_score(query, player))
    if _is_strict_name_match(query, best.get("strPlayer")) or _is_strict_name_match(query, best.get("strRealName")):
        return best

    query_slug = slugify_name(query)
    player_slug = slugify_name(best.get("strPlayer"))
    if query_slug and " " not in query_slug and query_slug in player_slug:
        return best

    if _HAS_RAPIDFUZZ:
        player_name = clean_name(best.get("strPlayer"))
        real_name = clean_name(best.get("strRealName"))
        best_ratio = max(
            float(fuzz.WRatio(query, player_name)) if player_name else 0.0,
            float(fuzz.WRatio(query, real_name)) if real_name else 0.0,
        )
        if best_ratio >= 93 and clean_name(best.get("strSport")).lower() == "fighting":
            return best

    return None


def extract_players_for_team_names(team_names: list[str]) -> pd.DataFrame:
    rows = []
    for team_name in team_names or []:
        teams = search_teams_by_name(team_name)
        chosen = _pick_best_team(clean_name(team_name), teams)
        if not chosen or not chosen.get("idTeam"):
            continue

        for player in fetch_players_by_team(chosen["idTeam"]):
            rows.append(
                {
                    "id": player.get("idPlayer") or None,
                    "name": clean_name(player.get("strPlayer")),
                    "team": clean_name(chosen.get("strTeam")),
                    "team_id": chosen.get("idTeam"),
                    "image_url": player.get("strThumb") or None,
                    "source": "thesportsdb",
                }
            )

    if not rows:
        return pd.DataFrame(columns=["id", "name", "team", "team_id", "image_url", "source", "name_slug"])
    return normalize_name_columns(pd.DataFrame(rows), ["name"])


def extract_all(sample_names: list[str] | None = None) -> pd.DataFrame:
    if not sample_names:
        return pd.DataFrame()

    rows = []
    logger = logging.getLogger("etl.extract_thesportsdb")

    for name in sample_names:
        players = fetch_wrestlers_by_name(name)
        if not players:
            continue

        player = _pick_best_player(name, players)
        if not player:
            continue

        try:
            rows.append(
                {
                    "id": player.get("idPlayer") or None,
                    "name": clean_name(player.get("strPlayer") or name),
                    "real_name": clean_name(player.get("strRealName")),
                    "promotion": clean_name(player.get("strTeam")),
                    "height": player.get("strHeight") or None,
                    "weight": player.get("strWeight") or None,
                    "date_born": player.get("dateBorn") or None,
                    "nationality": clean_name(player.get("strNationality")),
                    "debut": clean_name(player.get("strDebut")),
                    "retired": clean_name(player.get("strRetired")),
                    "image_url": player.get("strThumb") or player.get("strCutout") or player.get("strRender") or None,
                    "image_large": player.get("strImage") or player.get("strPoster") or None,
                    "team": clean_name(player.get("strTeam")),
                    "description": player.get("strDescriptionEN") or None,
                    "source": "thesportsdb",
                }
            )
        except Exception as exc:
            logger.debug("skipping player record", extra={"error": str(exc), "player": player})

    if not rows:
        return pd.DataFrame()
    return normalize_name_columns(pd.DataFrame(rows), ["name", "real_name"])


def get_wrestler(name_query: str) -> dict | None:
    df = extract_all([name_query])
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def run_and_save(sample_names: list[str], out_dir: str = "../data/processed"):
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
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "rows": len(df),
            "source": "thesportsdb",
        }
        with open(os.path.join(out_dir, "wrestlers_thesportsdb_metadata.json"), "w", encoding="utf-8") as handle:
            json.dump(meta, handle)
    except Exception:
        pass


def run_and_save_with_images(
    sample_names: list[str],
    out_dir: str = "../data/processed",
    images_dir: str = "../data/processed/images",
):
    df = extract_all(sample_names)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for idx, row in df.iterrows():
        image_url = row.get("image_url")
        if not image_url:
            continue
        try:
            response = requests_get_with_retry(image_url, timeout=10, stream=True)
            if response.status_code != 200:
                continue
            extension = os.path.splitext(image_url)[1].split("?")[0] or ".jpg"
            filename = f"{row.get('id') or idx}{extension}"
            image_path = os.path.join(images_dir, filename)
            with open(image_path, "wb") as handle:
                shutil.copyfileobj(response.raw, handle)
            df.at[idx, "image_path"] = image_path
        except Exception:
            continue

    run_and_save(sample_names, out_dir=out_dir)


if __name__ == "__main__":
    sample = ["The Undertaker", "John Cena", "Roman Reigns", "Seth Rollins", "Cody Rhodes"]
    run_and_save(sample)
