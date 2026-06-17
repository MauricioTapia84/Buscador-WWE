
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
    if not players:
        return None
    wrestler = players[0]
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

    pd.DataFrame(results).to_csv(
        "../data/raw/wrestlers_api.csv",
        index=False
    )
