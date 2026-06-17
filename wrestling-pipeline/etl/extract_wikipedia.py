"""ETL: extracción desde Wikipedia (simple implementation usando la API de Wikipedia)."""
import requests
import pandas as pd
from retry_utils import requests_get_with_retry


def extract_wikipedia_pages(titles):
    results = []
    for title in titles:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            resp = requests_get_with_retry(url, timeout=5)
            data = resp.json()
            results.append({
                "title": data.get("title"),
                "extract": data.get("extract"),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page")
            })
        except Exception:
            continue
    return pd.DataFrame(results)


if __name__ == '__main__':
    sample = ["Undertaker", "John_Cena", "Roman_Reigns"]
    df = extract_wikipedia_pages(sample)
    df.to_csv("../data/raw/wikipedia_summary.csv", index=False)
