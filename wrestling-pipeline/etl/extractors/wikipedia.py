from typing import List

import logging
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

from ..utils.retry_utils import requests_get_with_retry


def extract_wikipedia_pages(titles: List[str]) -> pd.DataFrame:
    logger = logging.getLogger("etl.extract_wikipedia")
    rows = []
    for title in titles or []:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            resp = requests_get_with_retry(url, timeout=5)
            data = resp.json()
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page")
            rows.append({
                "title": data.get("title"),
                "extract": data.get("extract"),
                "url": page_url,
            })
            logger.info("wikipedia: fetched page", extra={"title": title, "url": page_url})
        except Exception as exc:
            logger.warning("wikipedia: failed to fetch", extra={"title": title, "error": str(exc)})
            rows.append({"title": title, "extract": None, "url": None})
    return pd.DataFrame(rows)
