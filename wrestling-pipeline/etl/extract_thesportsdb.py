
import requests
import pandas as pd

def get_wrestler(name):
    url = f"https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p={name}"

    response = requests.get(url)
    data = response.json()

    if not data["player"]:
        return None

    wrestler = data["player"][0]

    return {
        "name": wrestler["strPlayer"],
        "height": wrestler["strHeight"],
        "weight": wrestler["strWeight"],
        "nationality": wrestler["strNationality"],
        "description": wrestler["strDescriptionEN"]
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
