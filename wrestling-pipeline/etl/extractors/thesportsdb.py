import json
import logging
import os
import shutil
import time
from hashlib import sha1
from typing import List, Optional

import pandas as pd
import requests
try:
    from rapidfuzz import fuzz, process
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False

from ..utils.retry_utils import requests_get_with_retry

API_BASE = "https://www.thesportsdb.com/api/v1/json"
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


def _best_match(name: str, choices: List[str], score_cutoff: int = 85):
    if not name or not choices or not _HAS_RAPIDFUZZ:
        return None, 0
    try:
        match = process.extractOne(name, choices, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
        if match:
            return match[0], match[1]
    except Exception:
        pass
    return None, 0


def fetch_wrestlers_by_name(name_query: str) -> List[dict]:
    key = f"searchplayers:{name_query}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    api_key = os.getenv("THESPORTSDB_API_KEY", "3")
    url = f"{API_BASE}/{api_key}/searchplayers.php?p={requests.utils.quote(name_query)}"
    try:
        resp = requests_get_with_retry(url, timeout=10)
        resp.raise_for_status()
        data = resp.json() or {}
        players = data.get("player") or []
    except Exception as exc:
        logging.getLogger("etl.extract_thesportsdb").warning("fetch failed", extra={"error": str(exc), "name": name_query})
        players = []

    if not players and ' ' in name_query:
        for token in [t for t in name_query.split(' ') if t][:2]:
            try:
                url = f"{API_BASE}/{api_key}/searchplayers.php?p={requests.utils.quote(token)}"
                resp = requests_get_with_retry(url, timeout=8)
                resp.raise_for_status()
                players = (resp.json() or {}).get("player") or []
                if players:
                    break
            except Exception:
                continue

    _cache_set(key, players)
    return players


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
