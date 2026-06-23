import os
import requests
import pandas as pd
import json
from hashlib import sha1
import logging
try:
    from rapidfuzz import fuzz, process
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False
import shutil
from retry_utils import requests_get_with_retry

API_BASE = "https://www.thesportsdb.com/api/v1/json"
CACHE_DIR = os.path.join("data", "raw", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_get(key: str):
    path = os.path.join(CACHE_DIR, f"{sha1(key.encode()).hexdigest()}.json")
    if os.path.exists(path):
        import os
        import requests
        import pandas as pd
        import json
        from hashlib import sha1
        import logging
        import shutil
        import time
        from datetime import datetime
        from retry_utils import requests_get_with_retry

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


        def fetch_wrestlers_by_name(name_query: str):
            """Search TheSportsDB for a person by name. Uses a simple file cache to avoid repeated requests.
            Returns list of dicts (may be empty)."""
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
                # polite pause to avoid hitting rate limits when called in bulk
                time.sleep(0.15)
            except Exception as e:
                logging.getLogger("etl.extract_thesportsdb").warning("fetch failed", extra={"error": str(e), "name": name_query})
                players = []

            # If empty, try tokenized fallback searches (first/last name)
            if not players and ' ' in name_query:
                parts = [p for p in name_query.split(' ') if p]
                for token in parts[:2]:
                    try:
                        url2 = f"{API_BASE}/{os.getenv('THESPORTSDB_API_KEY','3')}/searchplayers.php?p={requests.utils.quote(token)}"
                        r2 = requests_get_with_retry(url2, timeout=8)
                        r2.raise_for_status()
                        data2 = r2.json() or {}
                        players = data2.get('player') or []
                        if players:
                            break
                    except Exception:
                        continue
            _cache_set(key, players)
            return players


        def fetch_players_by_team(team_id: str):
            """Lookup all players for a given team id using lookup_all_players.php endpoint.
            Returns list of player dicts or empty list."""
            key = f"lookup_team:{team_id}"
            cached = _cache_get(key)
            if cached is not None:
                return cached
            api_key = os.getenv("THESPORTSDB_API_KEY", "3")
            url = f"{API_BASE}/{api_key}/lookup_all_players.php?id={requests.utils.quote(str(team_id))}"
            try:
                resp = requests_get_with_retry(url, timeout=12)
                resp.raise_for_status()
                data = resp.json() or {}
                players = data.get("player") or []
                time.sleep(0.15)
            except Exception as e:
                logging.getLogger("etl.extract_thesportsdb").warning("fetch team failed", extra={"error": str(e), "team_id": team_id})
                players = []
            _cache_set(key, players)
            return players


        def search_teams_by_name(name_query: str):
            """Search for teams by name and return a list of team dicts (idTeam, strTeam).
            Uses caching to avoid repeated requests."""
            key = f"searchteams:{name_query}"
            cached = _cache_get(key)
            if cached is not None:
                return cached
            api_key = os.getenv("THESPORTSDB_API_KEY", "3")
            url = f"{API_BASE}/{api_key}/searchteams.php?t={requests.utils.quote(name_query)}"
            try:
                resp = requests_get_with_retry(url, timeout=10)
                resp.raise_for_status()
                data = resp.json() or {}
                teams = data.get("teams") or []
                time.sleep(0.15)
            except Exception as e:
                logging.getLogger("etl.extract_thesportsdb").warning("team search failed", extra={"error": str(e), "query": name_query})
                teams = []
            _cache_set(key, teams)
            return teams


        def search_teams_by_league(league_name: str):
            """Search teams by league name using search_all_teams.php?l=<league>.
            Returns list of team dicts."""
            key = f"searchteams_league:{league_name}"
            cached = _cache_get(key)
            if cached is not None:
                return cached
            api_key = os.getenv("THESPORTSDB_API_KEY", "3")
            url = f"{API_BASE}/{api_key}/search_all_teams.php?l={requests.utils.quote(league_name)}"
            try:
                resp = requests_get_with_retry(url, timeout=12)
                resp.raise_for_status()
                data = resp.json() or {}
                teams = data.get("teams") or []
                time.sleep(0.15)
            except Exception as e:
                logging.getLogger("etl.extract_thesportsdb").warning("league team search failed", extra={"error": str(e), "league": league_name})
                teams = []
            _cache_set(key, teams)
            return teams


        def extract_players_for_team_names(team_names: list):
            """Given a list of team name strings, discover matching team IDs and extract all players for each discovered team.
            Returns combined DataFrame of players (may be empty)."""
            rows = []
            for tn in team_names:
                teams = search_teams_by_name(tn)
                # prefer exact matches on name when available
                chosen = None
                for t in teams:
                    if t.get('strTeam') and t.get('strTeam').lower() == tn.lower():
                        chosen = t
                        break
                # if not exact, try fuzzy match (if available)
                if not chosen and _HAS_RAPIDFUZZ and teams:
                    choices = {t.get('strTeam') or '': t for t in teams}
                    best = process.extractOne(tn, list(choices.keys()), scorer=fuzz.WRatio)
                    if best and best[1] >= 75:
                        chosen = choices.get(best[0])
                if not chosen and teams:
                    chosen = teams[0]
                if not chosen:
                    continue
                team_id = chosen.get('idTeam')
                if not team_id:
                    continue
                players = fetch_players_by_team(team_id)
                for p in players:
                    try:
                        rows.append({
                            "id": p.get("idPlayer") or None,
                            "name": p.get("strPlayer") or None,
                            "team": chosen.get('strTeam') or None,
                            "team_id": team_id,
                            "image_url": p.get("strThumb") or None,
                            "source": "thesportsdb",
                        })
                    except Exception:
                        continue
            return pd.DataFrame(rows)


        def extract_all(sample_names: list = None) -> pd.DataFrame:
            """Extract wrestlers metadata from TheSportsDB for a list of sample names.
            If sample_names is None, returns empty DataFrame (safe default).
            The function stores only metadata and thumbnail URLs; image download is optional and left to downstream jobs."""
            rows = []
            if not sample_names:
                return pd.DataFrame(rows)
            logger = logging.getLogger("etl.extract_thesportsdb")
            # process in chunks to avoid long blocking and be polite to API
            for n in sample_names:
                players = fetch_wrestlers_by_name(n)
                if not players:
                    continue
                for p in players:
                    try:
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
                            "image_large": p.get("strImage") or None,
                            "team": p.get("strTeam") or None,
                            "description": p.get("strDescriptionEN") or None,
                            "source": "thesportsdb",
                        })
                    except Exception as e:
                        logger.debug("skipping player record", extra={"error": str(e), "player": p})
            return pd.DataFrame(rows)


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
            # write metadata
            try:
                meta = {
                    'generated_at': datetime.utcnow().isoformat() + 'Z',
                    'rows': len(df),
                    'source': 'thesportsdb'
                }
                with open(os.path.join(out_dir, 'wrestlers_thesportsdb_metadata.json'), 'w', encoding='utf-8') as f:
                    json.dump(meta, f)
            except Exception:
                pass


        def run_and_save_with_images(sample_names: list, out_dir: str = "../data/processed", images_dir: str = "../data/processed/images"):
            df = extract_all(sample_names)
            os.makedirs(out_dir, exist_ok=True)
            os.makedirs(images_dir, exist_ok=True)
            for i, row in df.iterrows():
                img_url = row.get("image_url")
                if img_url:
                    try:
                        r = requests_get_with_retry(img_url, timeout=10)
                        if r and r.status_code == 200:
                            ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
                            fname = f"{row.get('id') or i}{ext}"
                            path = os.path.join(images_dir, fname)
                            with open(path, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                            df.at[i, 'image_path'] = path
                    except Exception:
                        continue
            run_and_save(sample_names, out_dir=out_dir)


        if __name__ == "__main__":
            sample = ["The Undertaker", "John Cena", "Roman Reigns", "Seth Rollins", "Cody Rhodes"]
            run_and_save(sample)
