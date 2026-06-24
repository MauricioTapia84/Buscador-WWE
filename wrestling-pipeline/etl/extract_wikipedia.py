import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser

BASE = "https://en.wikipedia.org"
URL = "https://en.wikipedia.org/api/rest_v1/page/html/List_of_WWE_Champions"

resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

def clean_text(el):
    return el.get_text(" ", strip=True)

titles = []
reigns = []
wrestlers = {}
events = {}

tables = soup.find_all("table")

for table in tables:
    # try to get a title name from preceding heading or caption
    title_name = None
    caption = table.find("caption")
    if caption:
        title_name = clean_text(caption)
    else:
        prev = table.find_previous(lambda tag: tag.name in ["h2", "h3"])
        if prev:
            title_name = clean_text(prev)
    if not title_name:
        title_name = "unknown"

    title_id = re.sub(r"\W+", "_", title_name).strip("_").lower()
    if title_id not in [t["id"] for t in titles]:
        titles.append({"id": title_id, "name": title_name})

    rows = table.find_all("tr")
    for row in rows[1:]:
        cols = row.find_all(["td", "th"]) or []
        if len(cols) < 1:
            continue

        champ_cell = cols[0]
        champ_name = clean_text(champ_cell)
        a = champ_cell.find("a", href=True)
        champ_link = urljoin(BASE, a["href"]) if a else None
        if champ_link and champ_link not in wrestlers:
            wrestlers[champ_link] = {"name": champ_name, "link": champ_link}

        # default raw reign info
        reign_raw = clean_text(cols[1]) if len(cols) > 1 else ""

        # attempt to extract dates from the cell text
        dates = re.findall(r"([A-Za-z]+ \d{1,2}, \d{4})", reign_raw)
        start_date = None
        end_date = None
        try:
            if len(dates) >= 1:
                start_date = parser.parse(dates[0]).date().isoformat()
            if len(dates) >= 2:
                end_date = parser.parse(dates[1]).date().isoformat()
        except Exception:
            start_date = None
            end_date = None

        # find event link if exists inside the cell (first link that looks like an event)
        event_link = None
        event_name = None
        if len(cols) > 1:
            ev_a = cols[1].find("a", href=True)
            if ev_a and ev_a["href"].startswith("/wiki/"):
                event_link = urljoin(BASE, ev_a["href"])
                event_name = clean_text(ev_a)
                if event_link not in events:
                    events[event_link] = {"name": event_name, "link": event_link}

        reign = {
            "title_id": title_id,
            "title_name": title_name,
            "champion_name": champ_name,
            "champion_link": champ_link,
            "start_date": start_date,
            "end_date": end_date,
            "event_name": event_name,
            "event_link": event_link,
            "raw": reign_raw,
        }
        reigns.append(reign)

        # be polite with requests if we later enrich
        time.sleep(0.01)

# Persist outputs
out_dir = "../data/raw"
pd.DataFrame(titles).to_csv(f"{out_dir}/titles.csv", index=False)
pd.DataFrame(reigns).to_csv(f"{out_dir}/reigns.csv", index=False)

# wrestlers and events as lists
w_list = [{"name": v["name"], "link": k} for k, v in wrestlers.items()]
e_list = [{"name": v["name"], "link": k} for k, v in events.items()]
pd.DataFrame(w_list).to_csv(f"{out_dir}/wrestlers_minimal.csv", index=False)
pd.DataFrame(e_list).to_csv(f"{out_dir}/events_minimal.csv", index=False)

print(f"Extracted {len(titles)} titles, {len(reigns)} reigns, {len(w_list)} wrestlers, {len(e_list)} events")

# --- Enrichment: follow wrestler and event links to get infobox / event meta
processed_dir = "../data/processed"

def extract_infobox(soup):
    info = {}
    table = soup.find("table", {"class": lambda c: c and "infobox" in c})
    if not table:
        return info
    for row in table.find_all("tr"):
        header = row.find("th")
        val = row.find("td")
        if not header or not val:
            continue
        key = header.get_text(" ", strip=True).lower()
        value = val.get_text(" ", strip=True)
        info[key] = value
    return info

def enrich_wrestlers(w_list):
    enriched = []
    for w in w_list:
        link = w.get("link")
        item = {"name": w.get("name"), "link": link}
        if not link:
            enriched.append(item)
            continue
        try:
            r = requests.get(link, timeout=10)
            r.raise_for_status()
            s = BeautifulSoup(r.text, "html.parser")
            info = extract_infobox(s)
            # map some common fields
            item["real_name"] = info.get("real name") or info.get("birth name")
            item["birth_date"] = info.get("born") or info.get("date of birth")
            item["height"] = info.get("height")
            item["weight"] = info.get("weight")
            item["debut"] = info.get("debut")
        except Exception:
            pass
        enriched.append(item)
        time.sleep(0.1)
    return enriched

def enrich_events(e_list):
    enriched = []
    for e in e_list:
        link = e.get("link")
        item = {"name": e.get("name"), "link": link}
        if not link:
            enriched.append(item)
            continue
        try:
            r = requests.get(link, timeout=10)
            r.raise_for_status()
            s = BeautifulSoup(r.text, "html.parser")
            # try to find date in infobox or first paragraphs
            info = extract_infobox(s)
            item["date"] = info.get("date") or info.get("date \u2013") or None
            # venue or location
            item["location"] = info.get("location") or info.get("venue")
            if not item.get("date"):
                # fallback: search first paragraph for a YYYY pattern
                p = s.find("p")
                if p:
                    m = re.search(r"([A-Za-z]+ \d{1,2}, \d{4})", p.get_text())
                    if m:
                        item["date"] = m.group(1)
        except Exception:
            pass
        enriched.append(item)
        time.sleep(0.1)
    return enriched

en_w = enrich_wrestlers(w_list)
en_e = enrich_events(e_list)

pd.DataFrame(en_w).to_csv(f"{processed_dir}/wrestlers_enriched.csv", index=False)
pd.DataFrame(en_e).to_csv(f"{processed_dir}/events_enriched.csv", index=False)

print(f"Enriched {len(en_w)} wrestlers and {len(en_e)} events")
import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_from_wikipedia_urls(urls: list) -> pd.DataFrame:
    """Scrape basic biography paragraphs from given Wikipedia (or HTML) URLs.
    Returns DataFrame with columns: url, text_snippet"""
    rows = []
    for u in urls or []:
        try:
            r = requests.get(u, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            p = soup.find("p")
            text = p.get_text().strip() if p else ""
            rows.append({"url": u, "text_snippet": text})
        except Exception:
            rows.append({"url": u, "text_snippet": ""})
    return pd.DataFrame(rows)
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
