
import pandas as pd
from retry_utils import requests_get_with_retry



def get_wrestler(name):
    url = f"https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p={name}"

    try:
        response = requests_get_with_retry(url, timeout=5)
        data = response.json()
    except Exception:
        return None
    players = data.get("player")
    import logging
    import pandas as pd
    from retry_utils import requests_get_with_retry
    import os
    import urllib.parse


    def get_wrestler(name):
        logger = logging.getLogger("etl.extract_thesportsdb")
        api_key = os.getenv("THESPORTSDB_API_KEY", "123")
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


    if __name__ == "__main__":
        wrestlers = ["Undertaker", "John Cena", "Roman Reigns"]

        results = []

        for w in wrestlers:
            data = get_wrestler(w)

            if data:
                results.append(data)

        out_dir = os.path.join("..", "data", "raw")
        os.makedirs(out_dir, exist_ok=True)
        pd.DataFrame(results).to_csv(os.path.join(out_dir, "wrestlers_api.csv"), index=False)
