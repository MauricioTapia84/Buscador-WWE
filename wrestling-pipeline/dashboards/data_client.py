import os
from typing import Any

import requests
import streamlit as st

DEFAULT_API_URL = "http://localhost:8000"


def get_api_url() -> str:
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


def _request_json(path: str, params: dict[str, Any] | None = None) -> tuple[Any, str | None]:
    url = f"{get_api_url()}{path}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "WrestlingDataExplorerDashboard/1.0",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


@st.cache_data(ttl=30)
def fetch_health() -> tuple[dict[str, Any] | None, str | None]:
    data, error = _request_json("/health")
    if isinstance(data, dict):
        return data, None
    return None, error


@st.cache_data(ttl=30)
def fetch_wrestlers() -> tuple[list[dict[str, Any]], str | None]:
    data, error = _request_json("/wrestlers")
    if isinstance(data, list):
        return data, None
    return [], error


@st.cache_data(ttl=30)
def fetch_titles() -> tuple[list[dict[str, Any]], str | None]:
    data, error = _request_json("/titles")
    if isinstance(data, list):
        return data, None
    return [], error


@st.cache_data(ttl=15)
def search_catalog(term: str) -> tuple[dict[str, Any] | None, str | None]:
    if not term.strip():
        return {"wrestlers": [], "titles": []}, None
    data, error = _request_json("/search", params={"q": term.strip()})
    if isinstance(data, dict):
        return data, None
    return None, error

