"""ETL: extracción desde Wikipedia (simple implementación usando la API de Wikipedia)."""
import logging
import requests
import pandas as pd
from retry_utils import requests_get_with_retry
import os


def extract_wikipedia_pages(titles):
    logger = logging.getLogger("etl.extract_wikipedia")
    results = []
    for title in titles:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            resp = requests_get_with_retry(url, timeout=5)
            data = resp.json()
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page")
            results.append({
                "title": data.get("title"),
                "extract": data.get("extract"),
                "url": page_url,
            })
            logger.info("wikipedia: fetched page", extra={"etl_stage": "extract", "source": "wikipedia", "title": title, "url": page_url})
        except Exception as e:
            logger.warning("wikipedia: failed to fetch", extra={"etl_stage": "extract", "source": "wikipedia", "title": title, "error": str(e)})
            continue
    return pd.DataFrame(results)


if __name__ == '__main__':
    sample = ["Undertaker", "John_Cena", "Roman_Reigns"]
    df = extract_wikipedia_pages(sample)
    out_dir = os.path.join("..", "data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "wikipedia_summary.csv"), index=False)
