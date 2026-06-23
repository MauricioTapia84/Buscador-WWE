import os
import requests
import pandas as pd
import json
from hashlib import sha1

API_BASE = "https://www.thesportsdb.com/api/v1/json/3"
CACHE_DIR = os.path.join("data", "raw", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_get(key: str):
    path = os.path.join(CACHE_DIR, f"{sha1(key.encode()).hexdigest()}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _cache_set(key: str, value):
    path = os.path.join(CACHE_DIR, f"{sha1(key.encode()).hexdigest()}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f)
    except Exception:
        pass


def fetch_wrestlers_by_name(name_query: str):
    """Search TheSportsDB for a person by name. Uses a simple file cache to avoid repeated requests.
    Returns list of dicts (may be empty)."""
    key = f"searchplayers:{name_query}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    url = f"{API_BASE}/searchplayers.php?p={requests.utils.quote(name_query)}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json() or {}
    players = data.get("player", [])
    _cache_set(key, players)
    return players


def extract_all(sample_names: list = None) -> pd.DataFrame:
    """Extract wrestlers metadata from TheSportsDB for a list of sample names.
    If sample_names is None, returns empty DataFrame (safe default).
    The function stores only metadata and thumbnail URLs; image download is optional and left to downstream jobs."""
    rows = []
    if not sample_names:
        return pd.DataFrame(rows)
    for n in sample_names:
        try:
            players = fetch_wrestlers_by_name(n)
            for p in players:
                rows.append({
                    "id": p.get("idPlayer") or None,
                    "name": p.get("strPlayer") or n,
                    "real_name": p.get("strRealName") or None,
                    "promotion": p.get("strTeam") or None,
                    "height": p.get("strHeight") or None,
                    "weight": p.get("strWeight") or None,
                    "date_born": p.get("dateBorn") or None,
                    "nationality": p.get("strNationality") or None,
                    "debut": p.get("strDebut") or None,
                    "retired": p.get("strRetired") or None,
                    "image_url": p.get("strThumb") or p.get("strRender") or None,
                    "description": p.get("strDescriptionEN") or None,
                    "source": "thesportsdb",
                })
        except Exception:
            continue
    return pd.DataFrame(rows)

import logging
import urllib.parse
from retry_utils import requests_get_with_retry

def get_wrestler(name):
    logger = logging.getLogger("etl.extract_thesportsdb")
    api_key = os.getenv("THESPORTSDB_API_KEY", "3")
    q = urllib.parse.quote_plus(name)
    url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/searchplayers.php?p={q}"

    try:
        response = requests_get_with_retry(url, timeout=5)
        data = response.json()
    except Exception as e:
        logger.warning("thesportsdb: request failed", extra={"etl_stage": "extract", "source": "thesportsdb", "name": name, "error": str(e)})
        return None
    players = data.get("player")
    if not players:
        logger.info("thesportsdb: no player found", extra={"etl_stage": "extract", "source": "thesportsdb", "name": name})
        return None
    wrestler = players[0]
    logger.info("thesportsdb: player found", extra={"etl_stage": "extract", "source": "thesportsdb", "name": name})
    return {
        "name": wrestler.get("strPlayer"),
        "height": wrestler.get("strHeight"),
        "weight": wrestler.get("strWeight"),
        "nationality": wrestler.get("strNationality"),
        "description": wrestler.get("strDescriptionEN"),
    }
def run_and_save(sample_names: list, out_dir: str = "../data/processed"):
    df = extract_all(sample_names)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "wrestlers_thesportsdb.csv")
    parquet_path = os.path.join(out_dir, "wrestlers_thesportsdb.parquet")
    try:
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
    except Exception:
        # fallback: write only csv
        df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    sample = ["The Undertaker", "John Cena", "Roman Reigns", "Seth Rollins", "Cody Rhodes"]
    run_and_save(sample)
