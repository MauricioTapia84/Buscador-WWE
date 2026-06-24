"""ETL helpers for Wikipedia extraction.

This module intentionally avoids any network call at import time so tests and
local tooling can import its helpers safely.
"""

import os
import re
import time
from typing import List
from urllib.parse import urljoin
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser

try:
    from ..name_utils import clean_name, normalize_name_columns
    from ..utils.retry_utils import requests_get_with_retry
except ImportError:
    from name_utils import clean_name, normalize_name_columns
    from utils.retry_utils import requests_get_with_retry

BASE = "https://en.wikipedia.org"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
PAGE_HTML_URL = "https://en.wikipedia.org/api/rest_v1/page/html/{page_title}"


def _page_token(title: str) -> str:
    text = clean_name(title).replace(" ", "_")
    return quote(text, safe="_()'!,.-")


def _extract_infobox(soup: BeautifulSoup) -> dict:
    info = {}
    table = soup.find("table", {"class": lambda cls: cls and "infobox" in cls})
    if not table:
        return info
    for row in table.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue
        key = clean_name(header.get_text(" ", strip=True)).lower()
        info[key] = clean_name(value.get_text(" ", strip=True))
    return info


def _infobox_lookup(info: dict, *aliases: str, contains: tuple[str, ...] = ()) -> str | None:
    for alias in aliases:
        value = info.get(alias)
        if value:
            return value
    for key, value in info.items():
        if not value:
            continue
        if any(token in key for token in contains):
            return value
    return None


def _extract_birth_date(value: str | None) -> str | None:
    if not value:
        return None
    iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", value)
    if iso_match:
        return iso_match.group(1)
    human_match = re.search(r"\b([A-Z][a-z]+ \d{1,2}, \d{4})\b", value)
    if human_match:
        try:
            return parser.parse(human_match.group(1)).date().isoformat()
        except Exception:
            return human_match.group(1)
    return clean_name(value)


def _clean_measurement(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = clean_name(value)
    cleaned = re.sub(r"\[\s*\d+\s*\]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;")
    return cleaned or None


def extract_wikipedia_pages(titles: List[str]) -> pd.DataFrame:
    rows = []
    for title in titles or []:
        page_token = _page_token(title)
        if not page_token:
            continue
        url = SUMMARY_URL.format(title=page_token)
        try:
            response = requests_get_with_retry(url, timeout=5)
            data = response.json()
            page_title = clean_name(data.get("title"))
            if not page_title:
                continue
            rows.append(
                {
                    "title": page_title,
                    "name": page_title,
                    "extract": data.get("extract"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                }
            )
        except Exception:
            continue

    if not rows:
        return pd.DataFrame(columns=["title", "name", "extract", "url", "name_slug"])
    return normalize_name_columns(pd.DataFrame(rows), ["name"])


def extract_from_wikipedia_urls(urls: List[str]) -> pd.DataFrame:
    rows = []
    for url in urls or []:
        try:
            response = requests_get_with_retry(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraph = soup.find("p")
            text = clean_name(paragraph.get_text(" ", strip=True) if paragraph else "")
            title = clean_name(soup.title.get_text(" ", strip=True).replace(" - Wikipedia", "")) if soup.title else ""
            rows.append({"url": url, "title": title, "name": title, "text_snippet": text})
        except Exception:
            rows.append({"url": url, "title": "", "name": "", "text_snippet": ""})

    if not rows:
        return pd.DataFrame(columns=["url", "title", "name", "text_snippet", "name_slug"])
    return normalize_name_columns(pd.DataFrame(rows), ["name"])


def extract_wwe_champions_page(page_title: str = "List_of_WWE_Champions") -> dict[str, pd.DataFrame]:
    response = requests_get_with_retry(PAGE_HTML_URL.format(page_title=_page_token(page_title)), timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    titles = []
    reigns = []
    wrestlers = {}
    events = {}

    for table in soup.find_all("table"):
        caption = table.find("caption")
        title_name = clean_name(caption.get_text(" ", strip=True) if caption else "")
        if not title_name:
            previous = table.find_previous(lambda tag: tag.name in ["h2", "h3"])
            title_name = clean_name(previous.get_text(" ", strip=True) if previous else "")
        if not title_name:
            title_name = "Unknown title"

        title_id = re.sub(r"\W+", "_", title_name).strip("_").lower()
        if title_id not in {item["id"] for item in titles}:
            titles.append({"id": title_id, "name": title_name})

        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all(["td", "th"])
            if not cols:
                continue

            champion_cell = cols[0]
            champion_name = clean_name(champion_cell.get_text(" ", strip=True))
            champion_link = None
            champion_anchor = champion_cell.find("a", href=True)
            if champion_anchor:
                champion_link = urljoin(BASE, champion_anchor["href"])
                wrestlers[champion_link] = {"name": champion_name, "link": champion_link}

            details_text = clean_name(cols[1].get_text(" ", strip=True)) if len(cols) > 1 else ""
            dates = re.findall(r"([A-Za-z]+ \d{1,2}, \d{4})", details_text)
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

            event_name = None
            event_link = None
            if len(cols) > 1:
                event_anchor = cols[1].find("a", href=True)
                if event_anchor and event_anchor["href"].startswith("/wiki/"):
                    event_name = clean_name(event_anchor.get_text(" ", strip=True))
                    event_link = urljoin(BASE, event_anchor["href"])
                    events[event_link] = {"name": event_name, "link": event_link}

            reigns.append(
                {
                    "title_id": title_id,
                    "title_name": title_name,
                    "champion_name": champion_name,
                    "champion_link": champion_link,
                    "start_date": start_date,
                    "end_date": end_date,
                    "event_name": event_name,
                    "event_link": event_link,
                    "raw": details_text,
                }
            )
            time.sleep(0.01)

    titles_df = pd.DataFrame(titles)
    reigns_df = normalize_name_columns(pd.DataFrame(reigns), ["champion_name"])
    wrestlers_df = normalize_name_columns(pd.DataFrame(wrestlers.values()), ["name"]) if wrestlers else pd.DataFrame()
    events_df = pd.DataFrame(events.values()) if events else pd.DataFrame()
    return {"titles": titles_df, "reigns": reigns_df, "wrestlers": wrestlers_df, "events": events_df}


def enrich_wrestlers(wrestlers_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, wrestler in wrestlers_df.iterrows():
        link = wrestler.get("link")
        item = {"name": clean_name(wrestler.get("name")), "link": link}
        if not link:
            rows.append(item)
            continue
        try:
            response = requests_get_with_retry(link, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            info = _extract_infobox(soup)
            item["real_name"] = info.get("real name") or info.get("birth name")
            item["birth_date"] = _extract_birth_date(
                _infobox_lookup(info, "born", "date of birth", contains=("born",))
            )
            item["height"] = _clean_measurement(
                _infobox_lookup(
                    info,
                    "height",
                    "billed height",
                    "announced height",
                    contains=("height",),
                )
            )
            item["weight"] = _clean_measurement(
                _infobox_lookup(
                    info,
                    "weight",
                    "billed weight",
                    "announced weight",
                    contains=("weight",),
                )
            )
            item["debut"] = _clean_measurement(_infobox_lookup(info, "debut", contains=("debut",)))
        except Exception:
            pass
        rows.append(item)
        time.sleep(0.1)

    if not rows:
        return pd.DataFrame()
    return normalize_name_columns(pd.DataFrame(rows), ["name", "real_name"])


def enrich_events(events_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, event in events_df.iterrows():
        link = event.get("link")
        item = {"name": clean_name(event.get("name")), "link": link}
        if not link:
            rows.append(item)
            continue
        try:
            response = requests_get_with_retry(link, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            info = _extract_infobox(soup)
            item["date"] = info.get("date") or info.get("date -")
            item["location"] = info.get("location") or info.get("venue")
        except Exception:
            pass
        rows.append(item)
        time.sleep(0.1)

    return pd.DataFrame(rows)


def enrich_wrestlers_from_titles(titles: List[str]) -> pd.DataFrame:
    """Build wrestler profiles from Wikipedia page summaries + infobox scraping.

    This is the integration point the ETL needs: given wrestler names, fetch
    their page summary for biography/extract and then scrape the page infobox
    for structured fields such as real name, birth date, height and weight.
    """
    pages = extract_wikipedia_pages(titles)
    if pages.empty:
        return pd.DataFrame(
            columns=[
                "name",
                "title",
                "extract",
                "url",
                "link",
                "real_name",
                "birth_date",
                "height",
                "weight",
                "debut",
                "source",
                "name_slug",
                "real_name_slug",
            ]
        )

    profile_input = pages[["name", "url"]].rename(columns={"url": "link"})
    structured = enrich_wrestlers(profile_input)
    if structured.empty:
        merged = pages.copy()
    else:
        merged = pages.merge(
            structured.drop(columns=["link"], errors="ignore"),
            on=[column for column in ["name", "name_slug"] if column in pages.columns and column in structured.columns],
            how="left",
        )
        if "link" not in merged.columns:
            merged["link"] = pages["url"]

    merged["source"] = "wikipedia"
    return normalize_name_columns(merged, ["name", "real_name"])


def run_and_save(out_raw: str = "../data/raw", out_processed: str = "../data/processed"):
    os.makedirs(out_raw, exist_ok=True)
    os.makedirs(out_processed, exist_ok=True)

    extracted = extract_wwe_champions_page()
    extracted["titles"].to_csv(os.path.join(out_raw, "titles.csv"), index=False)
    extracted["reigns"].to_csv(os.path.join(out_raw, "reigns.csv"), index=False)
    extracted["wrestlers"].to_csv(os.path.join(out_raw, "wrestlers_minimal.csv"), index=False)
    extracted["events"].to_csv(os.path.join(out_raw, "events_minimal.csv"), index=False)

    wrestlers_enriched = enrich_wrestlers(extracted["wrestlers"])
    events_enriched = enrich_events(extracted["events"])
    wrestlers_enriched.to_csv(os.path.join(out_processed, "wrestlers_enriched.csv"), index=False)
    events_enriched.to_csv(os.path.join(out_processed, "events_enriched.csv"), index=False)
