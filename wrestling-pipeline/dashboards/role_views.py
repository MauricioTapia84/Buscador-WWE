import ast
import html
from pathlib import Path
import re
from textwrap import dedent
import unicodedata

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_client import fetch_health, search_catalog, predict_champion, fetch_clean_stats

ADMIN_SECRET = "K#9vLp$2mQx@7nRf!4Zd"


def hide_native_page_nav():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_session_state():
    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False
    if "selected_role" not in st.session_state:
        st.session_state["selected_role"] = "Fanático"


def available_roles():
    roles = ["Fanático", "Periodista"]
    if st.session_state.get("admin_unlocked"):
        roles.append("Desarrollador / Analista")
    return roles


def apply_secret(search_term: str):
    if search_term.strip() == ADMIN_SECRET:
        st.session_state["admin_unlocked"] = True
        return True
    return False


def render_role_selector():
    roles = available_roles()
    current = st.session_state.get("selected_role", roles[0])
    if current not in roles:
        current = roles[0]
    widget_key = "selected_role_widget"
    widget_value = st.session_state.get(widget_key, current)
    if widget_value not in roles:
        widget_value = current
        st.session_state[widget_key] = current
    index = roles.index(widget_value)
    selected_role = st.radio(
        "Perfil",
        roles,
        index=index,
        horizontal=True,
        key=widget_key,
    )
    st.session_state["selected_role"] = selected_role
    return selected_role


def _search_results(search_term: str, wrestlers: list[dict]):
    if not search_term.strip() or search_term.strip() == ADMIN_SECRET:
        return wrestlers, None
    payload, error = search_catalog(search_term)
    if payload and payload.get("wrestlers"):
        return payload["wrestlers"], error

    lowered = search_term.lower().strip()
    local = [
        wrestler
        for wrestler in wrestlers
        if lowered in str(wrestler.get("artist_name") or wrestler.get("name") or "").lower()
    ]
    return local, error


def _format_value(value, fallback="No disponible"):
    if value is None:
        return fallback
    if isinstance(value, float) and pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _coerce_numeric(value) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_metric_value(value, *, decimals: int | None = None, fallback: str = "N/D") -> str:
    number = _coerce_numeric(value)
    if number is None:
        return fallback
    if decimals is None:
        if float(number).is_integer():
            return str(int(number))
        return f"{number:.1f}"
    return f"{number:.{decimals}f}"


def _win_rate_percent(value) -> float | None:
    number = _coerce_numeric(value)
    if number is None:
        return None
    return number * 100.0 if 0 <= number <= 1 else number


def _format_win_rate(value, *, decimals: int = 1, fallback: str = "N/D") -> str:
    percent = _win_rate_percent(value)
    if percent is None:
        return fallback
    return f"{percent:.{decimals}f}%"


def _parse_embedded_object(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return value
        return parsed
    return value


def _coerce_mapping(value) -> dict:
    parsed = _parse_embedded_object(value)
    return parsed if isinstance(parsed, dict) else {}


def _candidate_names(wrestler: dict) -> list[str]:
    names = []
    for field in ["artist_name", "canonical_name", "name", "display_name", "name_slug"]:
        value = wrestler.get(field)
        if value and str(value).strip():
            names.append(str(value).strip())
    return names


def _normalize_analytics_payload(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return {}

    wins = payload.get("wins", payload.get("total_wins", 0))
    losses = payload.get("losses", payload.get("total_losses", 0))
    total_matches = payload.get("total_matches", 0)
    return {
        "total_matches": total_matches,
        "wins": wins,
        "losses": losses,
        "win_rate": payload.get("win_rate", 0.0),
        "most_common_match_type": payload.get("most_common_match_type"),
        "data_available": payload.get("data_available", True),
        "source": payload.get("source") or "wrestling_clean.csv",
        "reason": payload.get("reason") or "Métricas consolidadas desde el dataset histórico unificado.",
        "active_years": payload.get("active_years") or payload.get("career_years") or payload.get("experiencia_anos"),
    }


def _resolve_historical_record(wrestler: dict) -> tuple[dict | None, list[dict], str | None]:
    stats_list, err = fetch_clean_stats()
    if err:
        return None, [], err
    if not stats_list:
        return None, [], None

    matched_stat = None
    for candidate in _candidate_names(wrestler):
        matched_stat = _find_matching_stat(candidate, stats_list)
        if matched_stat:
            break
    return matched_stat, stats_list, None


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def _find_matching_stat(name: str, stats_list: list[dict]) -> dict | None:
    normalized_name = _normalize_text(name)
    if not normalized_name:
        return None

    # Exact match on name variants
    for stat in stats_list:
        for field in ["artist_name", "name", "canonical_name"]:
            if _normalize_text(stat.get(field)) == normalized_name:
                return stat

    # Partial or fuzzy-like contains match
    for stat in stats_list:
        for field in ["artist_name", "name", "canonical_name"]:
            value = _normalize_text(stat.get(field))
            if value and (normalized_name in value or value in normalized_name):
                return stat

    return None


def _safe_date_label(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _build_history_frame(history) -> pd.DataFrame:
    history = _parse_embedded_object(history)
    if not isinstance(history, list):
        return pd.DataFrame()
    valid_history = [item for item in history if isinstance(item, dict)]
    return pd.DataFrame(valid_history) if valid_history else pd.DataFrame()


def _history_days(history_df: pd.DataFrame) -> int:
    total_days = history_df["days_recognized"].dropna().sum() if "days_recognized" in history_df.columns else 0
    if not total_days and "reign_days" in history_df.columns:
        total_days = history_df["reign_days"].dropna().sum()
    return int(total_days) if pd.notna(total_days) else 0


def _render_periodista_styles():
    st.markdown(
        """
        <style>
        .press-hero {
            padding: 24px 26px;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(17,24,39,0.98), rgba(127,29,29,0.95));
            color: #fff7ed;
            box-shadow: 0 22px 48px rgba(15, 23, 42, 0.16);
            border: 1px solid rgba(255,255,255,0.08);
            margin: 12px 0 18px;
        }
        .press-kicker {
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #fca5a5;
            margin-bottom: 10px;
            font-weight: 800;
        }
        .press-title {
            font-size: 34px;
            line-height: 1.1;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .press-subtitle {
            font-size: 15px;
            line-height: 1.7;
            color: rgba(255,247,237,0.84);
            max-width: 860px;
        }
        .press-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }
        .press-badge {
            padding: 9px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            font-size: 13px;
            color: #fff7ed;
        }
        .brief-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(15,23,42,0.08);
            border-radius: 20px;
            padding: 18px 18px 16px;
            box-shadow: 0 12px 28px rgba(15,23,42,0.06);
            min-height: 190px;
        }
        .brief-card .eyebrow {
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #991b1b;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .brief-card .headline {
            font-size: 22px;
            line-height: 1.2;
            color: #111827;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .brief-card .copy {
            font-size: 14px;
            line-height: 1.7;
            color: #334155;
        }
        .timeline-card {
            padding: 18px;
            border-radius: 20px;
            background: #ffffff;
            border: 1px solid rgba(15,23,42,0.08);
            box-shadow: 0 12px 32px rgba(15,23,42,0.06);
            margin-bottom: 16px;
        }
        .timeline-card .index {
            font-size: 12px;
            color: #64748b;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .timeline-card .title {
            font-size: 20px;
            color: #111827;
            font-weight: 800;
            margin: 6px 0 8px;
        }
        .timeline-card .meta {
            font-size: 14px;
            color: #334155;
            line-height: 1.7;
        }
        .section-note {
            color: #475569;
            font-size: 14px;
            margin-bottom: 12px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.7);
            border: 1px solid rgba(15,23,42,0.08);
            border-radius: 999px;
            padding: 10px 16px;
            color: #334155;
            font-weight: 700;
        }
        .stTabs [aria-selected="true"] {
            background: #991b1b !important;
            color: #fff7ed !important;
            border-color: #991b1b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _plot_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font={"color": "#111827"},
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.22,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 12, "color": "#334155"},
            "title": {"text": ""},
        },
    )
    return fig


def _slugify_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9 ]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def _parse_height_cm(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value)
    metric_match = re.search(r"(\d+(?:\.\d+)?)\s*cm\b", text.lower())
    if metric_match:
        return float(metric_match.group(1))
    meter_match = re.search(r"(\d+(?:\.\d+)?)\s*m\b", text.lower())
    if meter_match:
        return round(float(meter_match.group(1)) * 100, 1)
    feet_match = re.search(r"(\d+)\s*ft\s*(\d+)?\s*in", text.lower())
    if feet_match:
        feet = int(feet_match.group(1))
        inches = int(feet_match.group(2) or 0)
        return round((feet * 12 + inches) * 2.54, 1)
    return None


def _parse_weight_kg(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value)
    kg_match = re.search(r"(\d+(?:\.\d+)?)\s*kg\b", text.lower())
    if kg_match:
        return float(kg_match.group(1))
    lb_match = re.search(r"(\d+(?:\.\d+)?)\s*lb\b", text.lower())
    if lb_match:
        return round(float(lb_match.group(1)) * 0.45359237, 1)
    return None


def _parse_year(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return int(parsed.year)


def _render_analyst_styles():
    st.markdown(
        """
        <style>
        .lab-hero {
            padding: 22px 24px;
            border-radius: 24px;
            background: linear-gradient(135deg, #111827 0%, #7f1d1d 60%, #b45309 100%);
            color: #fff7ed;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 48px rgba(15,23,42,0.14);
            margin: 12px 0 18px;
        }
        .lab-kicker {
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #fed7aa;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .lab-title {
            font-size: 32px;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 8px;
        }
        .lab-copy {
            color: rgba(255,247,237,0.86);
            font-size: 15px;
            line-height: 1.7;
            max-width: 880px;
        }
        .lab-note {
            color: #475569;
            font-size: 14px;
            margin-bottom: 12px;
        }
        .freak-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(15,23,42,0.08);
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 12px 28px rgba(15,23,42,0.06);
            min-height: 142px;
        }
        .freak-card .label {
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #9a3412;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .freak-card .value {
            font-size: 26px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 8px;
        }
        .freak-card .meta {
            font-size: 14px;
            color: #334155;
            line-height: 1.65;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_history_card_styles():
    st.markdown(
        """
        <style>
        .history-card {
            margin-top: 14px;
            padding: 24px;
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
            border: 1px solid rgba(15,23,42,0.08);
            box-shadow: 0 18px 40px rgba(15,23,42,0.08);
        }
        .history-card__top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 18px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .history-card__identity {
            display: flex;
            align-items: center;
            gap: 18px;
            min-width: 0;
        }
        .history-card__avatar {
            width: 72px;
            height: 72px;
            border-radius: 22px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, #111827, #991b1b);
            color: #fff7ed;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 0.04em;
            flex: 0 0 72px;
        }
        .history-card__eyebrow {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #991b1b;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .history-card__name {
            font-size: 32px;
            line-height: 1.05;
            color: #111827;
            font-weight: 900;
            margin-bottom: 10px;
        }
        .history-card__meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .history-card__meta span {
            padding: 9px 12px;
            border-radius: 999px;
            background: #fff7ed;
            border: 1px solid rgba(180,83,9,0.16);
            color: #7c2d12;
            font-size: 13px;
            font-weight: 600;
        }
        .history-card__badges {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            min-width: min(320px, 100%);
        }
        .history-card__badge {
            padding: 16px 18px;
            border-radius: 20px;
            background: linear-gradient(135deg, #fffaf5, #ffffff);
            border: 1px solid rgba(15,23,42,0.08);
        }
        .history-card__badge-label {
            display: block;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .history-card__badge-value {
            font-size: 28px;
            line-height: 1;
            color: #991b1b;
            font-weight: 900;
        }
        .history-card__stats {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }
        .history-card__stat {
            padding: 18px;
            border-radius: 20px;
            background: #ffffff;
            border: 1px solid rgba(15,23,42,0.06);
        }
        .history-card__stat-label {
            display: block;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .history-card__stat-value {
            display: block;
            font-size: 30px;
            line-height: 1;
            color: #111827;
            font-weight: 900;
            margin-bottom: 8px;
        }
        .history-card__stat-copy {
            font-size: 13px;
            line-height: 1.6;
            color: #475569;
        }
        .history-card__context {
            padding: 16px 18px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(219,234,254,0.65), rgba(224,231,255,0.8));
            border: 1px solid rgba(59,130,246,0.12);
        }
        .history-card__context-label {
            display: block;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #1d4ed8;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .history-card__context-copy {
            font-size: 14px;
            line-height: 1.7;
            color: #1e3a8a;
        }
        @media (max-width: 980px) {
            .history-card__stats {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .history-card__badges {
                grid-template-columns: 1fr;
                width: 100%;
            }
        }
        @media (max-width: 640px) {
            .history-card {
                padding: 18px;
            }
            .history-card__identity {
                align-items: flex-start;
            }
            .history-card__name {
                font-size: 26px;
            }
            .history-card__stats {
                grid-template-columns: 1fr;
            }
            .history-card__avatar {
                width: 58px;
                height: 58px;
                border-radius: 18px;
                font-size: 22px;
                flex-basis: 58px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_profile_summary_styles():
    st.markdown(
        """
        <style>
        .summary-intro-card {
            margin: 12px 0 14px;
            padding: 18px 20px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(248,250,252,0.98));
            border: 1px solid rgba(15,23,42,0.08);
            box-shadow: 0 16px 34px rgba(15,23,42,0.07);
        }
        .summary-intro-card__eyebrow {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            font-weight: 800;
            color: #9a3412;
            margin-bottom: 8px;
        }
        .summary-intro-card__title {
            font-size: 30px;
            line-height: 1.1;
            font-weight: 900;
            color: #111827;
            margin-bottom: 10px;
        }
        .summary-intro-card__copy {
            font-size: 14px;
            line-height: 1.75;
            color: #475569;
            max-width: 940px;
        }
        .summary-shell {
            margin-top: 12px;
            padding: 22px;
            border-radius: 24px;
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(15,23,42,0.08);
            box-shadow: 0 18px 40px rgba(15,23,42,0.08);
        }
        .summary-shell__name {
            font-size: 26px;
            line-height: 1.1;
            font-weight: 900;
            color: #111827;
            margin-bottom: 16px;
        }
        .summary-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 14px;
        }
        .summary-grid-2 {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 14px;
        }
        .summary-card {
            padding: 16px 18px;
            border-radius: 18px;
            background: linear-gradient(180deg, #ffffff 0%, #fffaf5 100%);
            border: 1px solid rgba(15,23,42,0.08);
        }
        .summary-card--meta {
            min-height: 84px;
        }
        .summary-card__label {
            display: block;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .summary-card__value {
            display: block;
            font-size: 16px;
            line-height: 1.45;
            color: #1f2937;
            font-weight: 700;
        }
        .summary-card__metric {
            display: block;
            font-size: 18px;
            line-height: 1;
            color: #991b1b;
            font-weight: 900;
            margin-bottom: 6px;
        }
        .summary-card__big {
            display: block;
            font-size: 32px;
            line-height: 1;
            color: #111827;
            font-weight: 900;
            margin-bottom: 10px;
        }
        .summary-card__copy {
            font-size: 13px;
            line-height: 1.6;
            color: #475569;
        }
        .summary-context {
            margin-top: 4px;
            padding: 16px 18px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(219,234,254,0.55), rgba(224,231,255,0.78));
            border: 1px solid rgba(59,130,246,0.12);
        }
        .summary-context__title {
            display: block;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #1d4ed8;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .summary-context__copy {
            font-size: 14px;
            line-height: 1.7;
            color: #1e3a8a;
        }
        @media (max-width: 980px) {
            .summary-grid-4 {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 640px) {
            .summary-intro-card__title {
                font-size: 24px;
            }
            .summary-shell {
                padding: 18px;
            }
            .summary-grid-4,
            .summary-grid-2 {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_summary_intro(title: str, copy: str, *, eyebrow: str):
    _render_profile_summary_styles()
    st.markdown(
        f"""
        <section class="summary-intro-card">
            <div class="summary-intro-card__eyebrow">{html.escape(eyebrow)}</div>
            <div class="summary-intro-card__title">{html.escape(title)}</div>
            <div class="summary-intro-card__copy">{html.escape(copy)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _build_roster_frame(wrestlers: list[dict]) -> pd.DataFrame:
    rows = []
    for wrestler in wrestlers or []:
        history = _build_history_frame(wrestler.get("title_history"))
        total_days = _history_days(history) if not history.empty else 0
        dominant_title = None
        dominant_era = None
        avg_reign_days = None
        first_reign_year = None
        if not history.empty:
            if "title" in history.columns and history["title"].notna().any():
                dominant_title = history["title"].fillna("Sin título").value_counts().idxmax()
            if "era" in history.columns and history["era"].notna().any():
                dominant_era = history["era"].dropna().astype(str).value_counts().idxmax()
            duration = history["days_recognized"] if "days_recognized" in history.columns else pd.Series(dtype="float64")
            if duration.dropna().empty and "reign_days" in history.columns:
                duration = history["reign_days"]
            if not duration.dropna().empty:
                avg_reign_days = float(duration.dropna().mean())
            if "start_date" in history.columns:
                first_reign_year = _parse_year(history["start_date"].dropna().min() if history["start_date"].notna().any() else None)
        rows.append(
            {
                "artist_name": wrestler.get("artist_name") or wrestler.get("name"),
                "name": wrestler.get("name") or wrestler.get("artist_name"),
                "name_slug": _slugify_text(wrestler.get("artist_name") or wrestler.get("name")),
                "height": wrestler.get("height"),
                "weight": wrestler.get("weight"),
                "height_cm": _parse_height_cm(wrestler.get("height")),
                "weight_kg": _parse_weight_kg(wrestler.get("weight")),
                "birth_year": _parse_year(wrestler.get("birth_date") or wrestler.get("date_born")),
                "titles_won": int(wrestler.get("titles_won") or 0),
                "reign_count": len(history),
                "total_reign_days": total_days,
                "avg_reign_days": avg_reign_days,
                "dominant_title": dominant_title or "Sin título visible",
                "dominant_era": dominant_era or "Sin era",
                "first_reign_year": first_reign_year,
            }
        )
    return pd.DataFrame(rows)


def _build_titles_frame(titles: list[dict]) -> pd.DataFrame:
    rows = []
    for entry in titles or []:
        holder = entry.get("holder") or entry.get("champion_name") or entry.get("artist_name") or entry.get("name")
        start_date = entry.get("start_date") or entry.get("won_date") or entry.get("event_date")
        start_year = _parse_year(start_date)
        reign_days = entry.get("days_recognized")
        if reign_days in [None, ""] or (isinstance(reign_days, float) and pd.isna(reign_days)):
            reign_days = entry.get("reign_days")
        rows.append(
            {
                "title": entry.get("title") or "Sin título",
                "holder": holder,
                "holder_slug": _slugify_text(holder),
                "era": entry.get("era") or "Sin era",
                "start_date": pd.to_datetime(start_date, errors="coerce"),
                "start_year": start_year,
                "decade": int(start_year // 10 * 10) if start_year else None,
                "reign_days": pd.to_numeric(reign_days, errors="coerce"),
                "event_name": entry.get("event_name"),
            }
        )
    return pd.DataFrame(rows)


def _metric_card_html(label: str, value, icon: str, accent: str, subtitle: str | None = None) -> str:
    has_value = value not in [None, ""] and not (isinstance(value, float) and pd.isna(value))
    display_value = str(value) if has_value else "--"
    display_subtitle = subtitle if has_value else "(Dato no disponible)"
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid rgba(36,52,71,0.10);
        border-radius:18px;
        padding:18px 18px 16px;
        box-shadow:0 14px 28px rgba(36,52,71,0.06);
        min-height:138px;
    ">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <div style="font-size:13px;font-weight:700;color:#6b7280;">{label}</div>
            <div style="width:36px;height:36px;border-radius:12px;background:{accent};display:grid;place-items:center;color:#fff7ed;font-size:18px;">{icon}</div>
        </div>
        <div style="font-size:34px;line-height:1;font-weight:900;color:#5a1620;margin-bottom:8px;">{display_value}</div>
        <div style="font-size:12px;color:#64748b;">{display_subtitle or ''}</div>
    </div>
    """


def _profile_card_html(wrestler: dict, condensed: bool = False) -> str:
    name = _format_value(wrestler.get("artist_name") or wrestler.get("name"), "Sin nombre")
    birth_date = _format_value(wrestler.get("birth_date") or wrestler.get("date_born"))
    height = _format_value(wrestler.get("height"), "--")
    weight = _format_value(wrestler.get("weight"), "--")
    bio = _format_value(wrestler.get("biography") or wrestler.get("description") or wrestler.get("extract"))
    if condensed and bio != "No disponible" and len(bio) > 260:
        bio = bio[:257].rstrip() + "..."
    image_url = wrestler.get("image_url") or wrestler.get("image_large") or wrestler.get("image_path")
    history = wrestler.get("title_history") or []
    if not isinstance(history, list):
        history = []
    valid_history = [item for item in history if isinstance(item, dict)]
    reign_count = len(valid_history)
    title_count = len({item.get("title") for item in valid_history if item.get("title")})
    photo_block = (
        f'<div style="display:flex;align-items:center;justify-content:center;min-height:360px;max-height:460px;padding:18px;border-radius:22px;background:#ffffff;border:1px solid rgba(36,52,71,0.08);overflow:hidden;">'
        f'<img src="{image_url}" alt="{name}" style="width:100%;max-height:420px;object-fit:contain;object-position:center;border-radius:16px;" />'
        f'</div>'
        if image_url
        else '<div style="height:320px;border-radius:22px;background:linear-gradient(135deg,#243447,#7b1e2b);display:flex;align-items:center;justify-content:center;color:#fff7ed;font-size:42px;font-weight:900;">WWE</div>'
    )
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid rgba(36,52,71,0.10);
        border-radius:24px;
        box-shadow:0 18px 38px rgba(36,52,71,0.08);
        padding:22px;
        margin-top:10px;
    ">
        <div style="display:grid;grid-template-columns:minmax(260px,0.8fr) minmax(0,1.2fr);gap:24px;align-items:start;">
            <div>{photo_block}</div>
            <div>
                <div style="font-size:15px;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:#7b1e2b;margin-bottom:8px;">Perfil unificado</div>
                <div style="font-size:40px;line-height:1.05;font-weight:900;color:#243447;margin-bottom:12px;">{name}</div>
                <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:16px;">
                    <div style="padding:14px;border-radius:16px;background:#f9f5ef;border:1px solid rgba(36,52,71,0.08);">
                        <div style="font-size:12px;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Fecha de nacimiento</div>
                        <div style="font-size:22px;color:#243447;font-weight:800;margin-top:6px;">{birth_date}</div>
                    </div>
                    <div style="padding:14px;border-radius:16px;background:#f9f5ef;border:1px solid rgba(36,52,71,0.08);">
                        <div style="font-size:12px;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Medidas</div>
                        <div style="font-size:20px;color:#243447;font-weight:800;margin-top:6px;">{height} · {weight}</div>
                    </div>
                </div>
                <div style="font-size:20px;font-weight:800;color:#243447;margin-bottom:8px;">Biografía</div>
                <div style="font-size:14px;line-height:1.8;color:#334155;margin-bottom:18px;">{bio}</div>
                <div style="font-size:20px;font-weight:800;color:#243447;margin-bottom:10px;">Curiosidades</div>
                <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;">
                    <div style="padding:14px;border-radius:16px;background:#fcfaf7;border:1px solid rgba(36,52,71,0.08);">
                        <div style="font-size:12px;color:#6b7280;font-weight:700;text-transform:uppercase;">Reinados visibles</div>
                        <div style="font-size:28px;font-weight:900;color:#7b1e2b;margin-top:6px;">{reign_count}</div>
                    </div>
                    <div style="padding:14px;border-radius:16px;background:#fcfaf7;border:1px solid rgba(36,52,71,0.08);">
                        <div style="font-size:12px;color:#6b7280;font-weight:700;text-transform:uppercase;">Títulos referenciados</div>
                        <div style="font-size:28px;font-weight:900;color:#7b1e2b;margin-top:6px;">{title_count}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def _analytics_payload_html(wrestler: dict, analytics: dict) -> str:
    total_matches = analytics.get("total_matches", 0)
    wins = analytics.get("wins", 0)
    losses = analytics.get("losses", 0)
    win_rate = analytics.get("win_rate", 0.0)
    common_type = _format_value(analytics.get("most_common_match_type"))
    reason = _format_value(analytics.get("reason"), "Sin información adicional")
    source = _format_value(analytics.get("source"), "N/A")
    return f"""
<div class="result-card-body">
    <div>
        <div class="section-title">Palmarés y logros</div>
        <div class="result-list">
            <div class="result-item"><strong>Total de combates</strong><span>{_format_metric_value(total_matches, fallback='--')}</span></div>
            <div class="result-item"><strong>Victorias</strong><span>{_format_metric_value(wins, fallback='--')}</span></div>
            <div class="result-item"><strong>Derrotas</strong><span>{_format_metric_value(losses, fallback='--')}</span></div>
            <div class="result-item"><strong>Tipo de combate más común</strong><span>{common_type}</span></div>
        </div>
    </div>
    <div>
        <div class="section-title">Contexto</div>
        <div class="notice-box">Fuente: {source}<br>{reason}<br>Win rate: {_format_win_rate(win_rate, decimals=2, fallback='--')}</div>
        <div class="section-title">Luchador</div>
        <div class="result-item"><strong>Nombre</strong><span>{_format_value(wrestler.get('artist_name') or wrestler.get('name'))}</span></div>
    </div>
</div>
"""


def _comparison_dumbbell_figure(
    *,
    title: str,
    selected_value,
    average_value,
    unit: str,
    selected_label: str = "Personaje",
    average_label: str = "Promedio visible",
    decimals: int = 1,
    colors: tuple[str, str] = ("#7b1e2b", "#243447"),
):
    selected_number = _coerce_numeric(selected_value)
    average_number = _coerce_numeric(average_value)
    if selected_number is None or average_number is None:
        return None

    formatter = (
        (lambda value: f"{value:.0f} {unit}".strip())
        if decimals == 0 else
        (lambda value: f"{value:.{decimals}f} {unit}".strip())
    )

    minimum = min(selected_number, average_number)
    maximum = max(selected_number, average_number)
    span = maximum - minimum
    padding = max(span * 0.35, abs(maximum) * 0.08, 1.0)
    x_start = minimum - padding
    x_end = maximum + padding
    delta = selected_number - average_number
    delta_label = (
        f"{delta:+.{decimals}f} {unit}".strip()
        if decimals > 0 else
        f"{delta:+.0f} {unit}".strip()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[average_number, selected_number],
            y=[0, 0],
            mode="lines",
            line={"color": "#cbd5e1", "width": 10},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[average_number],
            y=[0],
            mode="markers+text",
            marker={"size": 20, "color": colors[1], "line": {"width": 2, "color": "#ffffff"}},
            text=[formatter(average_number)],
            textposition="bottom center",
            textfont={"size": 13, "color": "#334155"},
            name=average_label,
            hovertemplate=f"{average_label}: %{{text}}<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[selected_number],
            y=[0],
            mode="markers+text",
            marker={"size": 22, "color": colors[0], "line": {"width": 2, "color": "#ffffff"}},
            text=[formatter(selected_number)],
            textposition="top center",
            textfont={"size": 13, "color": "#111827"},
            name=selected_label,
            hovertemplate=f"{selected_label}: %{{text}}<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=(selected_number + average_number) / 2,
        y=0.22,
        text=f"Diferencia: {delta_label}",
        showarrow=False,
        font={"size": 13, "color": "#475569"},
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        borderpad=6,
    )
    fig.update_yaxes(
        visible=False,
        range=[-0.45, 0.45],
        fixedrange=True,
    )
    fig.update_xaxes(
        title=unit or "valor",
        range=[x_start, x_end],
        zeroline=False,
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        tickfont={"color": "#64748b"},
    )
    fig.update_layout(
        title={"text": title, "font": {"size": 16, "color": "#111827"}},
        margin={"l": 20, "r": 20, "t": 70, "b": 35},
    )
    _plot_layout(fig, height=220)
    return fig


def _render_analytics_card(wrestler: dict, analytics: dict):
    _render_profile_summary_styles()
    analytics = _normalize_analytics_payload(analytics)
    wins = analytics.get("wins", 0)
    losses = analytics.get("losses", 0)
    total_matches = analytics.get("total_matches", 0)
    win_rate = analytics.get("win_rate", 0.0)
    most_common_match_type = analytics.get("most_common_match_type")
    source = analytics.get("source") or "N/A"
    reason = analytics.get("reason") or "Sin información adicional"
    debut_reference = wrestler.get("debut") or wrestler.get("debut_year") or analytics.get("active_years") or analytics.get("career_years")
    name = wrestler.get("artist_name") or wrestler.get("name") or "Sin nombre"
    height = _format_value(wrestler.get("height"), "N/D")
    weight = _format_value(wrestler.get("weight"), "N/D")
    history = _build_history_frame(wrestler.get("title_history"))
    reign_count = len(history) if not history.empty else int(wrestler.get("titles_won") or 0)
    distinct_titles = 0
    if not history.empty and "title" in history.columns:
        distinct_titles = int(history["title"].fillna("Sin título").nunique())
    meta_cards = [
        ("Medidas", f"📏 {height}"),
        ("Peso", f"⚖️ {weight}"),
        ("Debut / actividad", f"📅 {_format_value(debut_reference, 'N/D')}"),
        ("Tipo de combate", f"🥊 {_format_value(most_common_match_type)}"),
    ]
    badge_cards = [
        ("Reinados visibles", _format_metric_value(reign_count, fallback="N/D")),
        ("Títulos distintos", _format_metric_value(distinct_titles, fallback="N/D")),
    ]
    performance_cards = [
        ("Combates", _format_metric_value(total_matches), "Historial competitivo agregado visible."),
        ("Victorias", _format_metric_value(wins), "Combates ganados identificados en la base."),
        ("Derrotas", _format_metric_value(losses), "Combates perdidos identificados en la base."),
        ("Win rate", _format_win_rate(win_rate), "Proporción de victorias sobre combates registrados."),
    ]
    meta_html = "".join(
        f"""
        <div class="summary-card summary-card--meta">
            <span class="summary-card__label">{html.escape(label)}</span>
            <span class="summary-card__value">{html.escape(value)}</span>
        </div>
        """
        for label, value in meta_cards
    )
    badge_html = "".join(
        f"""
        <div class="summary-card">
            <span class="summary-card__label">{html.escape(label)}</span>
            <span class="summary-card__metric">{html.escape(value)}</span>
        </div>
        """
        for label, value in badge_cards
    )
    performance_html = "".join(
        f"""
        <div class="summary-card">
            <span class="summary-card__label">{html.escape(label)}</span>
            <span class="summary-card__big">{html.escape(value)}</span>
            <div class="summary-card__copy">{html.escape(copy)}</div>
        </div>
        """
        for label, value, copy in performance_cards
    )
    st.markdown(
        f"""
        <section class="summary-shell">
            <div class="summary-shell__name">{html.escape(name)}</div>
            <div class="summary-grid-4">{meta_html}</div>
            <div class="summary-grid-2">{badge_html}</div>
            <div class="summary-grid-4">{performance_html}</div>
            <div class="summary-context">
                <span class="summary-context__title">Fuente y alcance</span>
                <div class="summary-context__copy">Fuente: {html.escape(str(source))}. {html.escape(str(reason))}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _pick_wrestler(search_term: str, wrestlers: list[dict], label: str):
    filtered, error = _search_results(search_term, wrestlers)
    options = filtered or wrestlers
    options = sorted(
        options,
        key=lambda wrestler: (
            -int(bool(wrestler.get("image_url") or wrestler.get("image_large"))),
            -int(bool(wrestler.get("biography") or wrestler.get("description") or wrestler.get("extract"))),
            -int(bool(wrestler.get("birth_date") or wrestler.get("date_born") or wrestler.get("real_name"))),
            -int(wrestler.get("titles_won", 0) or 0),
            str(wrestler.get("artist_name") or wrestler.get("name") or ""),
        ),
    )
    if not options:
        return None, error

    labels = [w.get("artist_name") or w.get("canonical_name") or w.get("name") or "Sin nombre" for w in options]
    index = 0
    if search_term.strip() and search_term.strip() != ADMIN_SECRET:
        for idx, text in enumerate(labels):
            if search_term.lower() in text.lower():
                index = idx
                break

    selected_label = st.selectbox(label, labels, index=index)
    selected = next((item for item, name in zip(options, labels) if name == selected_label), options[0])
    return selected, error


def _render_historical_profile_score_ui(wrestler: dict):
    matched_stat, stats_list, err = _resolve_historical_record(wrestler)
    if err:
        st.warning(f"No se pudieron cargar las estadísticas históricas del modelo: {err}")
        return
    if not stats_list:
        st.info("No hay datos históricos suficientes para clasificar el perfil del luchador. Verifica que `/stats` devuelva registros.")
        return

    candidate_names = _candidate_names(wrestler)
    if not candidate_names:
        st.info("No hay datos históricos suficientes para clasificar el perfil del luchador.")
        return

    if not matched_stat:
        st.info(
            "No hay datos históricos suficientes para clasificar el perfil del luchador. "
            f"Nombres consultados: {', '.join(candidate_names[:3])}"
        )
        return

    st.markdown("---")
    health_info, health_error = fetch_health()
    model_name = health_info.get('model_name') if health_info else None
    model_f1 = health_info.get('model_f1') if health_info else None

    st.markdown("### 🧪 Score Histórico de Perfil Campeón (Machine Learning)")
    st.markdown(
        "Este módulo compara el desempeño histórico agregado del luchador con el patrón aprendido a partir de campeones históricos del dataset. "
        "No representa una predicción futura ni una probabilidad real de ganar un título hoy."
    )
    if model_name:
        st.caption(f"Modelo activo: {model_name} • F1 estimado: {model_f1:.3f}")
    else:
        st.caption("Modelo activo: no disponible. La clasificación usará el endpoint `/predict`.")

    # Show clean KPI cards using glassmorphism styling
    st.markdown(
        """
        <style>
        .kpi-glass {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            color: #fff;
        }
        .kpi-glass .kpi-value {
            font-size: 28px;
            font-weight: 900;
            color: #eab308; /* Gold accent */
            margin-bottom: 5px;
        }
        .kpi-glass .kpi-label {
            font-size: 14px;
            font-weight: 600;
            color: #d1d5db;
            text-transform: uppercase;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    t_wins = matched_stat.get("total_wins", 0)
    t_losses = matched_stat.get("total_losses", 0)
    t_matches = matched_stat.get("total_matches", 0)
    w_rate = matched_stat.get("win_rate", 0)

    # We wrap them in a dark container for contrast
    st.markdown('<div style="background: linear-gradient(135deg, #1f2937, #7f1d1d); padding: 20px; border-radius: 20px;">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-glass"><div class="kpi-value">{_format_metric_value(t_matches)}</div><div class="kpi-label">Combates</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-glass"><div class="kpi-value">{_format_metric_value(t_wins)}</div><div class="kpi-label">Victorias</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-glass"><div class="kpi-value">{_format_metric_value(t_losses)}</div><div class="kpi-label">Derrotas</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-glass"><div class="kpi-value">{_format_win_rate(w_rate)}</div><div class="kpi-label">Win Rate</div></div>', unsafe_allow_html=True)

    if t_matches < 10:
        st.warning("Datos de combate limitados: menos de 10 combates registrados. La clasificación histórica puede ser menos confiable.")

    st.markdown("#### Variables que alimentan el modelo histórico")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Combates", _format_metric_value(t_matches))
    metric_cols[1].metric("Victorias", _format_metric_value(t_wins))
    metric_cols[2].metric("Derrotas", _format_metric_value(t_losses))
    metric_cols[3].metric("Win rate", _format_win_rate(w_rate))

    cohort_df = pd.DataFrame(stats_list)
    if not cohort_df.empty:
        if "es_campeon" in cohort_df.columns:
            champion_mask = pd.to_numeric(cohort_df["es_campeon"], errors="coerce").fillna(0).astype(int) == 1
        elif "is_champion" in cohort_df.columns:
            champion_mask = pd.to_numeric(cohort_df["is_champion"], errors="coerce").fillna(0).astype(int) == 1
        else:
            champion_mask = pd.to_numeric(cohort_df.get("total_titles", 0), errors="coerce").fillna(0) > 0

        champion_group = cohort_df[champion_mask].copy()
        non_champion_group = cohort_df[~champion_mask].copy()

        def _mean_value(frame: pd.DataFrame, column: str):
            if frame.empty or column not in frame.columns:
                return None
            series = pd.to_numeric(frame[column], errors="coerce").dropna()
            return None if series.empty else float(series.mean())

        comparison_rows = [
            {
                "Métrica": "Combates",
                "Luchador seleccionado": _format_metric_value(t_matches),
                "Promedio campeones históricos": _format_metric_value(_mean_value(champion_group, "total_matches")),
                "Promedio no campeones": _format_metric_value(_mean_value(non_champion_group, "total_matches")),
            },
            {
                "Métrica": "Victorias",
                "Luchador seleccionado": _format_metric_value(t_wins),
                "Promedio campeones históricos": _format_metric_value(_mean_value(champion_group, "total_wins")),
                "Promedio no campeones": _format_metric_value(_mean_value(non_champion_group, "total_wins")),
            },
            {
                "Métrica": "Derrotas",
                "Luchador seleccionado": _format_metric_value(t_losses),
                "Promedio campeones históricos": _format_metric_value(_mean_value(champion_group, "total_losses")),
                "Promedio no campeones": _format_metric_value(_mean_value(non_champion_group, "total_losses")),
            },
            {
                "Métrica": "Win rate",
                "Luchador seleccionado": _format_win_rate(w_rate),
                "Promedio campeones históricos": _format_win_rate(_mean_value(champion_group, "win_rate")),
                "Promedio no campeones": _format_win_rate(_mean_value(non_champion_group, "win_rate")),
            },
        ]

        st.markdown("#### ¿Con qué se compara exactamente?")
        st.markdown(
            "Cuando presionas el botón, la API toma estas cuatro variables del luchador y las contrasta contra patrones aprendidos en el dataset histórico: "
            f"`{len(champion_group)}` perfiles con registro de campeonato y `{len(non_champion_group)}` perfiles sin campeonato."
        )
        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
        st.caption("Importante: estos promedios son solo una referencia visual. El modelo no compara únicamente contra el promedio; aprende una frontera usando todos los casos históricos.")

    st.markdown(
        '<div style="padding:18px;border-radius:18px;background:#f3f4f6;border:1px solid #d1d5db;margin-top:14px;">'
        '<strong>Interpretación rápida:</strong> El score sube cuando las cuatro variables del luchador se parecen al grupo histórico de campeones que el modelo vio al entrenar. '
        'No está evaluando actualidad, roster vigente ni contexto reciente. La comparación ocurre al presionar el botón.'
        '</div>',
        unsafe_allow_html=True,
    )

    button_key = f"historical_profile_score_{_slugify_text(wrestler.get('artist_name') or wrestler.get('name'))}"
    if st.button("✨ Comparar Contra el Patrón Histórico", key=button_key):
        with st.spinner("Analizando historial..."):
            pred_data, error = predict_champion(t_wins, t_losses, t_matches, w_rate)

        if error or not pred_data:
            st.error(f"Error al conectar con el modelo: {error}")
        else:
            prob = float(pred_data.get("probability_percent", 0.0))
            pred = int(pred_data.get("is_champion_prediction", 0))
            label = "Perfil alineado con campeones históricos" if pred == 1 else "Perfil menos alineado con campeones históricos"
            interpretation = (
                "Alta similitud con campeones históricos" if prob >= 70
                else "Similitud moderada con campeones históricos" if prob >= 40
                else "Similitud baja con campeones históricos"
            )

            st.markdown(f"**Clasificación final:** {label}")
            st.markdown(f"**Interpretación:** {interpretation}")
            st.caption(
                "Lectura recomendada: un 100% significa que, para estas cuatro variables, el perfil cae muy cerca del patrón histórico de campeones aprendido por el modelo. "
                "No significa 100% de probabilidad real de volver a ganar un título."
            )
            st.markdown(
                """
                <div style="padding:16px 18px;border-radius:18px;background:#fff7ed;border:1px solid rgba(180,83,9,0.18);margin-top:10px;">
                    <strong>Cómo leer el score:</strong><br/>
                    100%: el perfil cae muy lejos del lado campeón y el modelo casi no tiene dudas.<br/>
                    50%: el perfil queda cerca de la frontera entre campeón y no campeón; hay señales mixtas.<br/>
                    0%: el perfil se parece mucho más al grupo histórico sin campeonatos.
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prob,
                title = {'text': "Score Histórico", 'font': {'size': 20, 'color': '#111827'}},
                number = {'suffix': "%", 'font': {'color': '#111827', 'size': 44}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#64748b"},
                    'bar': {'color': "#2563eb"},
                    'bgcolor': "rgba(243, 244, 246, 1)",
                    'borderwidth': 1,
                    'bordercolor': "#cbd5e1",
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(148, 163, 184, 0.35)"},
                        {'range': [40, 70], 'color': "rgba(59, 130, 246, 0.28)"},
                        {'range': [70, 100], 'color': "rgba(37, 99, 235, 0.2)"}],
                }
            ))
            fig.update_layout(paper_bgcolor="rgba(255,255,255,0.98)", plot_bgcolor="rgba(255,255,255,0.98)", font={'color': "#111827"}, height=350)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_fanatico_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.subheader("Perfil Fanático")
    st.caption("Ficha visual, biografía y datos curiosos del personaje.")

    wrestler, error = _pick_wrestler(search_term, wrestlers, "Selecciona un luchador")
    if error:
        st.warning(f"La búsqueda remota devolvió un problema: {error}")
    if not wrestler:
        st.info("No hay luchadores disponibles todavía.")
        return
    st.markdown(_profile_card_html(wrestler, condensed=False), unsafe_allow_html=True)
    matched_stat, _, stats_error = _resolve_historical_record(wrestler)
    analytics = _normalize_analytics_payload(matched_stat) if matched_stat else _coerce_mapping(wrestler.get("analytics"))
    if stats_error:
        st.warning(f"No se pudieron resolver las métricas históricas consolidadas: {stats_error}")
    if analytics:
        _render_summary_intro(
            "Rendimiento visible en la base",
            "Resumen factual del historial competitivo disponible para este personaje.",
            eyebrow="Lectura factual",
        )
        _render_analytics_card(wrestler, analytics)



def render_periodista_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.subheader("Perfil Periodista")
    st.caption("Cronología de reinados y eventos exactos asociados al luchador.")
    _render_periodista_styles()

    wrestler, error = _pick_wrestler(search_term, wrestlers, "Selecciona un luchador para revisar su historial")
    if error:
        st.warning(f"La búsqueda remota devolvió un problema: {error}")
    if not wrestler:
        st.info("No hay luchadores disponibles todavía.")
        return

    matched_stat, _, stats_error = _resolve_historical_record(wrestler)
    analytics = _normalize_analytics_payload(matched_stat) if matched_stat else _coerce_mapping(wrestler.get("analytics"))
    _render_summary_intro(
        "Resumen histórico del luchador",
        "Esta ficha resume hechos registrados en la base: combates, victorias, derrotas, win rate histórico y contexto competitivo. Aquí priorizamos evidencia y trazabilidad por encima de la inferencia.",
        eyebrow="Ficha periodística",
    )
    if analytics:
        _render_analytics_card(wrestler, analytics)
    else:
        st.info("No hay métricas competitivas consolidadas para este luchador en los datos actuales.")
    if stats_error:
        st.warning(f"No se pudieron resolver las métricas históricas consolidadas: {stats_error}")
    st.markdown(
        '<div class="section-note">Nota metodológica: los reinados enlazados dependen de la coincidencia entre múltiples fuentes. '
        'Un luchador puede tener historial competitivo visible aunque su cronología titular aún no esté completamente resuelta.</div>',
        unsafe_allow_html=True,
    )

    history_df = _build_history_frame(wrestler.get("title_history"))
    if history_df.empty:
        st.info("Este luchador no tiene reinados enlazados en los datos actuales.")
        return

    for column in ["start_date", "end_date", "won_date", "event_date"]:
        if column in history_df.columns:
            history_df[column] = pd.to_datetime(history_df[column], errors="coerce")
    if "days_recognized" in history_df.columns:
        history_df["days_recognized"] = pd.to_numeric(history_df["days_recognized"], errors="coerce")
    if "reign_days" in history_df.columns:
        history_df["reign_days"] = pd.to_numeric(history_df["reign_days"], errors="coerce")

    eras = []
    if "era" in history_df.columns:
        eras = sorted({str(value).strip() for value in history_df["era"].dropna() if str(value).strip()})
    artist_name = wrestler.get("artist_name") or wrestler.get("name") or "Sin nombre"
    first_reign = _safe_date_label(
        history_df["start_date"].min() if "start_date" in history_df.columns and history_df["start_date"].notna().any() else None
    )
    last_reign = _safe_date_label(
        history_df["end_date"].max() if "end_date" in history_df.columns and history_df["end_date"].notna().any() else None
    )
    latest_event = _format_value(history_df["event_name"].dropna().iloc[-1] if history_df["event_name"].notna().any() else None)
    total_days = _history_days(history_df)
    title_focus = history_df["title"].fillna("Sin título").value_counts().idxmax() if "title" in history_df.columns else "Sin título"
    reign_records = (
        history_df.sort_values("start_date", na_position="last").to_dict(orient="records")
        if "start_date" in history_df.columns
        else history_df.to_dict(orient="records")
    )

    st.markdown(
        f"""
        <section class="press-hero">
            <div class="press-kicker">Desk Periodista</div>
            <div class="press-title">{artist_name}</div>
            <div class="press-subtitle">
                Cronología editorial de reinados, cambios de manos y contexto histórico. Esta vista prioriza lectura narrativa y secuencia temporal sobre el dump tabular.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    top_a, top_b, top_c, top_d = st.columns(4)
    top_a.metric("Reinados registrados", len(history_df))
    top_b.metric("Primer reinado", _format_value(first_reign))
    top_c.metric("Último evento", latest_event)
    top_d.metric("Días reconocidos", total_days)

    summary_tab,titles_tab, data_tab = st.tabs(["Resumen", "Campeonatos", "Datos"])

    with summary_tab:
        lead_a, lead_b = st.columns([1.15, 0.85])
        with lead_a:
            st.markdown("### Lectura rápida")
            st.markdown(
                '<div class="section-note">Los hitos más útiles para una lectura editorial del personaje y su impacto titular.</div>',
                unsafe_allow_html=True,
            )
            for idx, reign in enumerate(reign_records[:4]):
                start_date = reign.get("start_date")
                end_date = reign.get("end_date")
                period_parts = []
                if pd.notna(start_date):
                    period_parts.append(start_date.date().isoformat())
                if pd.notna(end_date):
                    period_parts.append(end_date.date().isoformat())
                period = " a ".join(period_parts) if period_parts else "Fecha no disponible"
                st.markdown(
                    f"""
                    <div class="brief-card" style="margin-bottom:14px;">
                        <div class="eyebrow">Momento clave #{idx + 1}</div>
                        <div class="headline">{_format_value(reign.get("title"))}</div>
                        <div class="copy">
                            <strong>Periodo:</strong> {period}<br/>
                            <strong>Evento:</strong> {_format_value(reign.get("event_name"))}<br/>
                            <strong>Capturó el título ante:</strong> {_format_value(reign.get("defeated_for_title"))}<br/>
                            <strong>Cedió el título a:</strong> {_format_value(reign.get("lost_title_to"))}<br/>
                            <strong>Nota editorial:</strong> {_format_value(reign.get("notes"), "Sin notas adicionales")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with lead_b:
            st.markdown("### Contexto histórico")
            top_titles = history_df["title"].fillna("Sin título").value_counts().head(3).index.tolist() if "title" in history_df.columns else []
            context_blocks = [
                ("Campeonato dominante", _format_value(title_focus), "Título con más apariciones en la cronología visible."),
                ("Último evento registrado", latest_event, "Último cambio o defensa con evento identificado en la fuente."),
                ("Eras cubiertas", _format_value(", ".join(eras), "Sin clasificar"), "Segmentación histórica disponible desde la API enriquecida."),
                ("Top campeonatos", _format_value(", ".join(top_titles), "Sin títulos"), "Los campeonatos más repetidos del perfil."),
            ]
            for label, value, copy in context_blocks:
                st.markdown(
                    f"""
                    <div class="brief-card" style="margin-bottom:14px;">
                        <div class="eyebrow">{label}</div>
                        <div class="headline" style="font-size:20px;">{value}</div>
                        <div class="copy">{copy}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with titles_tab:
        st.markdown("### Distribución por campeonato")
        st.markdown(
            '<div class="section-note">Lectura comparativa del peso de cada campeonato dentro del historial visible del luchador.</div>',
            unsafe_allow_html=True,
        )
        
        # --- GRÁFICOS ---
        chart_a, chart_b = st.columns(2)
        counts = history_df["title"].fillna("Sin título").value_counts().reset_index()
        counts.columns = ["title", "reigns"]
        
        with chart_a:
            fig = px.bar(
                counts.sort_values("reigns", ascending=True),
                x="reigns",
                y="title",
                orientation="h",
                color="reigns",
                color_continuous_scale=["#fcd34d", "#b45309", "#991b1b"],
                title="Reinados por campeonato",
            )
            fig.update_yaxes(title="")
            _plot_layout(fig, height=380)
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_b:
            duration_source = history_df["days_recognized"] if "days_recognized" in history_df.columns else pd.Series(dtype="float64")
            if duration_source.dropna().empty and "reign_days" in history_df.columns:
                duration_source = history_df["reign_days"]
            duration_by_title = history_df.assign(duration=duration_source.fillna(0)).groupby("title", dropna=False, as_index=False)["duration"].sum()
            duration_by_title["title"] = duration_by_title["title"].fillna("Sin título")
            duration_fig = px.bar(
                duration_by_title.sort_values("duration", ascending=True),
                x="duration",
                y="title",
                orientation="h",
                color="duration",
                color_continuous_scale=["#fde68a", "#92400e", "#7f1d1d"],
                title="Días acumulados por campeonato",
            )
            duration_fig.update_yaxes(title="")
            _plot_layout(duration_fig, height=380)
            st.plotly_chart(duration_fig, use_container_width=True)
        
        if eras:
            era_counts = history_df["era"].fillna("Sin clasificar").value_counts().reset_index()
            era_counts.columns = ["era", "count"]
            era_fig = px.bar(era_counts, x="era", y="count", color="era", title="Distribución por era")
            era_fig.update_layout(showlegend=False)
            _plot_layout(era_fig, height=320)
            st.plotly_chart(era_fig, use_container_width=True)

        # --- SEPARADOR VISUAL ---
        st.markdown("---")
        st.markdown("### 📋 Detalle de reinados")
        st.markdown(
            '<div class="section-note">Fichas narrativas de cada cambio de manos: título, oponentes y número de reinado.</div>',
            unsafe_allow_html=True,
        )

        # --- TABLA DE REINADOS (en lugar de tarjetas) ---
        # Ordenar reinados (más antiguo primero)
        sorted_reigns = sorted(
            reign_records,
            key=lambda x: (
                x.get("start_date") if pd.notna(x.get("start_date")) else pd.Timestamp.max
            ),
            reverse=False
        )

    # Construir lista de datos para la tabla
    table_data = []
    for idx, reign in enumerate(sorted_reigns):
        reign_number = idx + 1
        table_data.append({
            "N°": reign_number,
            "Título": _format_value(reign.get("title")),
            "Venció a": _format_value(reign.get("defeated_for_title")),
            "Lo perdió ante": _format_value(reign.get("lost_title_to")),
        })

    # Convertir a DataFrame y mostrar como tabla
    table_df = pd.DataFrame(table_data)
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "N°": st.column_config.NumberColumn("N°", width="small"),
            "Título": st.column_config.TextColumn("Título", width="medium"),
            "Venció a": st.column_config.TextColumn("Venció a", width="medium"),
            "Lo perdió ante": st.column_config.TextColumn("Lo perdió ante", width="medium"),
        }
    )    
                
    with data_tab:
        st.markdown("### Tabla cronológica")
        st.markdown(
            '<div class="section-note">Vista tabular para contraste y verificación de fechas, eventos, inferencias y notas de fuente.</div>',
            unsafe_allow_html=True,
        )
        timeline = history_df.copy()
        for column in ["start_date", "end_date", "won_date", "event_date"]:
            if column in timeline.columns:
                timeline[column] = pd.to_datetime(timeline[column], errors="coerce")
                if pd.api.types.is_datetime64_any_dtype(timeline[column]):
                    timeline[column] = timeline[column].dt.strftime("%Y-%m-%d")
                else:
                    timeline[column] = timeline[column].astype(str)
        keep = [
            column
            for column in [
                "title",
                "overall_reign",
                "champion_reign_number",
                "start_date",
                "end_date",
                "end_date_inferred",
                "event_name",
                "location",
                "reign_days",
                "days_recognized",
                "era",
                "defeated_for_title",
                "lost_title_to",
                "notes",
            ]
            if column in timeline.columns
        ]
        st.dataframe(timeline[keep], use_container_width=True, hide_index=True)
        with st.expander("Notas de interpretación"):
            st.write("Si `end_date_inferred` aparece activo, la fecha de cierre fue estimada usando el siguiente cambio de manos del mismo campeonato.")


def render_developer_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.title("Perfil Desarrollador / Analista")
    st.caption("Explorador analítico del roster: distribuciones, comparativas generales y KPIs individuales.")
    _render_analyst_styles()

    if not st.session_state.get("admin_unlocked"):
        st.error("Acceso restringido. Ingresa la clave de administrador en el buscador para habilitar esta vista.")
        return

    roster_df = _build_roster_frame(wrestlers)
    titles_df = _build_titles_frame(titles)
    if roster_df.empty:
        st.info("No hay luchadores disponibles todavía.")
        return

    st.markdown(
        """
        <section class="lab-hero">
            <div class="lab-kicker">Analytics Lab</div>
            <div class="lab-title">Distribuciones físicas, reinados y comparativas del roster</div>
            <div class="lab-copy">
                Esta vista mezcla el catálogo enriquecido de luchadores con la cronología de campeonatos para detectar patrones de altura, peso, duración de reinados y outliers por era o campeonato.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    title_choices = sorted([value for value in titles_df.get("title", pd.Series(dtype="object")).dropna().unique().tolist() if str(value).strip()])
    era_choices = sorted([value for value in titles_df.get("era", pd.Series(dtype="object")).dropna().unique().tolist() if str(value).strip()])
    year_candidates = sorted([int(value) for value in titles_df.get("start_year", pd.Series(dtype="float64")).dropna().tolist()])
    year_min = year_candidates[0] if year_candidates else None
    year_max = year_candidates[-1] if year_candidates else None

    with st.expander("Filtros analíticos", expanded=True):
        filter_a, filter_b, filter_c = st.columns(3)
        with filter_a:
            selected_titles = st.multiselect("Campeonato", title_choices, default=[])
        with filter_b:
            selected_eras = st.multiselect("Era", era_choices, default=[])
        with filter_c:
            measurements_only = st.checkbox("Solo perfiles con altura o peso", value=True)
        if year_min is not None and year_max is not None:
            selected_years = st.slider("Rango de años", min_value=year_min, max_value=year_max, value=(year_min, year_max))
        else:
            selected_years = None

    filtered_titles = titles_df.copy()
    if not filtered_titles.empty:
        if selected_titles:
            filtered_titles = filtered_titles[filtered_titles["title"].isin(selected_titles)]
        if selected_eras:
            filtered_titles = filtered_titles[filtered_titles["era"].isin(selected_eras)]
        if selected_years:
            filtered_titles = filtered_titles[
                filtered_titles["start_year"].between(selected_years[0], selected_years[1], inclusive="both")
            ]

    year_filter_active = bool(selected_years and year_min is not None and year_max is not None and selected_years != (year_min, year_max))
    title_filters_active = bool(selected_titles or selected_eras or year_filter_active)
    if title_filters_active and not filtered_titles.empty:
        eligible_slugs = set(filtered_titles["holder_slug"].dropna().tolist())
        filtered_roster = roster_df[roster_df["name_slug"].isin(eligible_slugs)].copy()
    elif title_filters_active and filtered_titles.empty:
        filtered_roster = roster_df.iloc[0:0].copy()
    else:
        filtered_roster = roster_df.copy()

    if measurements_only:
        filtered_roster = filtered_roster[
            filtered_roster["height_cm"].notna() | filtered_roster["weight_kg"].notna()
        ].copy()

    if filtered_roster.empty:
        st.warning("Los filtros actuales dejaron la vista sin luchadores comparables.")
        return

    merged_titles = filtered_titles.merge(
        roster_df[["name_slug", "artist_name", "height_cm", "weight_kg", "dominant_title", "dominant_era"]],
        left_on="holder_slug",
        right_on="name_slug",
        how="left",
    ) if not filtered_titles.empty else pd.DataFrame()

    avg_height = filtered_roster["height_cm"].dropna().mean()
    avg_weight = filtered_roster["weight_kg"].dropna().mean()
    avg_reign = filtered_titles["reign_days"].dropna().mean() if not filtered_titles.empty else None
    top_title = (
        filtered_titles["title"].fillna("Sin título").value_counts().idxmax()
        if not filtered_titles.empty and filtered_titles["title"].notna().any()
        else "Sin datos"
    )

    kpi_a, kpi_b, kpi_c, kpi_d, kpi_e = st.columns(5)
    kpi_a.metric("Luchadores visibles", int(len(filtered_roster)))
    kpi_b.metric("Altura media", f"{avg_height:.1f} cm" if pd.notna(avg_height) else "N/D")
    kpi_c.metric("Peso medio", f"{avg_weight:.1f} kg" if pd.notna(avg_weight) else "N/D")
    kpi_d.metric("Duración media de reinado", f"{avg_reign:.0f} días" if pd.notna(avg_reign) else "N/D")
    kpi_e.metric("Campeonato dominante", _format_value(top_title))

    dist_tab, compare_tab, individual_tab = st.tabs(["Distribución", "Comparativas", "Perfil individual"])

    with dist_tab:
        st.markdown("### Distribución física del roster")
        st.markdown(
            '<div class="lab-note">Aquí importa la dispersión general del roster filtrado, no un solo luchador. El objetivo es ver densidad, outliers y agrupamientos físicos.</div>',
            unsafe_allow_html=True,
        )
        scatter_df = filtered_roster.dropna(subset=["height_cm", "weight_kg"]).copy()
        if not scatter_df.empty:

            group_field = "dominant_title" if scatter_df["dominant_title"].nunique() > 1 else "dominant_era"
            box_left, box_right = st.columns(2)
            with box_left:
                height_box = px.box(
                    scatter_df,
                    x=group_field,
                    y="height_cm",
                    color=group_field,
                    title=f"Altura por {group_field.replace('_', ' ')}",
                    color_discrete_sequence=["#7b1e2b", "#243447", "#b45309", "#2f855a"],
                )
                height_box.update_layout(showlegend=False)
                _plot_layout(height_box, height=360)
                st.plotly_chart(height_box, use_container_width=True)
            with box_right:
                weight_box = px.box(
                    scatter_df,
                    x=group_field,
                    y="weight_kg",
                    color=group_field,
                    title=f"Peso por {group_field.replace('_', ' ')}",
                    color_discrete_sequence=["#2f855a", "#243447", "#7b1e2b", "#b45309"],
                )
                weight_box.update_layout(showlegend=False)
                _plot_layout(weight_box, height=360)
                st.plotly_chart(weight_box, use_container_width=True)

    with compare_tab:
        st.markdown("### Comparativas históricas")
        st.markdown(
            '<div class="lab-note">Estas comparativas cruzan medidas físicas con reinados visibles para responder cómo cambia el perfil del campeón según periodo o cinturón.</div>',
            unsafe_allow_html=True,
        )

        if not merged_titles.empty:
            compare_field = "title" if merged_titles["title"].nunique() > 1 else ("era" if merged_titles["era"].nunique() > 1 else "decade")
            grouped = merged_titles.groupby(compare_field, dropna=False, as_index=False).agg(
                avg_height_cm=("height_cm", "mean"),
                avg_weight_kg=("weight_kg", "mean"),
                avg_reign_days=("reign_days", "mean"),
                reigns=("holder", "count"),
            )
            compare_left, compare_right = st.columns(2)
            with compare_left:
                height_compare = px.bar(
                    grouped.sort_values("avg_height_cm", ascending=True),
                    x="avg_height_cm",
                    y=compare_field,
                    orientation="h",
                    color="avg_height_cm",
                    color_continuous_scale=["#fde68a", "#d97706", "#7f1d1d"],
                    title=f"Altura media por {compare_field}",
                )
                height_compare.update_yaxes(title="")
                _plot_layout(height_compare, height=360)
                st.plotly_chart(height_compare, use_container_width=True)
            with compare_right:
                weight_compare = px.bar(
                    grouped.sort_values("avg_weight_kg", ascending=True),
                    x="avg_weight_kg",
                    y=compare_field,
                    orientation="h",
                    color="avg_weight_kg",
                    color_continuous_scale=["#fdba74", "#b45309", "#7c2d12"],
                    title=f"Peso medio por {compare_field}",
                )
                weight_compare.update_yaxes(title="")
                _plot_layout(weight_compare, height=360)
                st.plotly_chart(weight_compare, use_container_width=True)

            duration_fig = px.bar(
                grouped.sort_values("avg_reign_days", ascending=True),
                x="avg_reign_days",
                y=compare_field,
                orientation="h",
                color="reigns",
                color_continuous_scale=["#e2e8f0", "#94a3b8", "#334155"],
                title=f"Duración media de reinado por {compare_field}",
            )
            duration_fig.update_yaxes(title="")
            _plot_layout(duration_fig, height=360)
            st.plotly_chart(duration_fig, use_container_width=True)

            decade_stats = merged_titles.dropna(subset=["decade"]).groupby("decade", as_index=False).agg(
                avg_height_cm=("height_cm", "mean"),
                avg_weight_kg=("weight_kg", "mean"),
                avg_reign_days=("reign_days", "mean"),
                reigns=("holder", "count"),
            )
            
            if merged_titles["title"].nunique() > 1 and merged_titles["decade"].dropna().nunique() > 1:
                heatmap = (
                    merged_titles.pivot_table(index="title", columns="decade", values="holder", aggfunc="count", fill_value=0)
                    .reset_index()
                )
                heatmap_fig = px.imshow(
                    heatmap.set_index("title"),
                    aspect="auto",
                    color_continuous_scale=["#fff7ed", "#fdba74", "#991b1b"],
                    title="Frecuencia de reinados por campeonato y década",
                )
                _plot_layout(heatmap_fig, height=340)
                st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.info("No hay suficientes reinados filtrados para construir comparativas históricas.")

    with individual_tab:
        st.markdown("### Perfil individual con contexto agregado")
        filtered_names = set(filtered_roster["name_slug"].tolist())
        wrestler_pool = [item for item in wrestlers if _slugify_text(item.get("artist_name") or item.get("name")) in filtered_names] or wrestlers
        wrestler, error = _pick_wrestler(search_term, wrestler_pool, "Selecciona un luchador para revisar métricas")
        if error:
            st.warning(f"La búsqueda remota devolvió un problema: {error}")
        if not wrestler:
            st.info("No hay luchadores disponibles todavía.")
            return

        analytics = _coerce_mapping(wrestler.get("analytics"))
        analytics_available = bool(analytics.get("data_available"))
        if not analytics_available and analytics.get("reason"):
            st.warning(analytics["reason"])

        selected_slug = _slugify_text(wrestler.get("artist_name") or wrestler.get("name"))
        selected_row = filtered_roster[filtered_roster["name_slug"] == selected_slug].head(1)
        selected_height = selected_row["height_cm"].iloc[0] if not selected_row.empty else None
        selected_weight = selected_row["weight_kg"].iloc[0] if not selected_row.empty else None
        selected_reign_days = selected_row["total_reign_days"].iloc[0] if not selected_row.empty else None
        visible_reign_average = filtered_roster["total_reign_days"].mean() if filtered_roster["total_reign_days"].notna().any() else None
        height_delta = selected_height - avg_height if pd.notna(avg_height) and pd.notna(selected_height) else None
        weight_delta = selected_weight - avg_weight if pd.notna(avg_weight) and pd.notna(selected_weight) else None
        reign_delta = selected_reign_days - visible_reign_average if pd.notna(visible_reign_average) and selected_reign_days is not None else None

        freak_a, freak_b, freak_c = st.columns(3)
        freak_cards = [
            (
                "Altura vs promedio",
                f"{selected_height:.1f} cm" if pd.notna(selected_height) else "N/D",
                f"{height_delta:+.1f} cm frente al promedio visible." if height_delta is not None else "Sin altura suficiente para comparar.",
            ),
            (
                "Peso vs promedio",
                f"{selected_weight:.1f} kg" if pd.notna(selected_weight) else "N/D",
                f"{weight_delta:+.1f} kg frente al promedio visible." if weight_delta is not None else "Sin peso suficiente para comparar.",
            ),
            (
                "Reinado acumulado",
                f"{int(selected_reign_days)} días" if selected_reign_days is not None else "N/D",
                f"{reign_delta:+.0f} días respecto del promedio del grupo." if reign_delta is not None else "Sin reinados suficientes para comparar.",
            ),
        ]
        for column, (label, value, meta) in zip([freak_a, freak_b, freak_c], freak_cards):
            with column:
                st.markdown(
                    f"""
                    <div class="freak-card">
                        <div class="label">{label}</div>
                        <div class="value">{value}</div>
                        <div class="meta">{meta}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### Comparación directa contra el promedio visible")
        st.caption("Cada gráfico muestra dos puntos: el luchador seleccionado y el promedio del grupo filtrado. La línea entre ambos hace visible incluso una diferencia pequeña.")
        height_fig = _comparison_dumbbell_figure(
            title="Altura: personaje vs promedio visible",
            selected_value=selected_height,
            average_value=avg_height,
            unit="cm",
            decimals=1,
            colors=("#7b1e2b", "#94a3b8"),
        )
        weight_fig = _comparison_dumbbell_figure(
            title="Peso: personaje vs promedio visible",
            selected_value=selected_weight,
            average_value=avg_weight,
            unit="kg",
            decimals=1,
            colors=("#b45309", "#334155"),
        )
        reign_fig = _comparison_dumbbell_figure(
            title="Reinado acumulado: personaje vs promedio visible",
            selected_value=selected_reign_days,
            average_value=visible_reign_average,
            unit="días",
            decimals=0,
            colors=("#1d4ed8", "#94a3b8"),
        )
        compare_left, compare_center, compare_right = st.columns(3)
        with compare_left:
            if height_fig is not None:
                st.plotly_chart(height_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No hay altura suficiente para comparar a este luchador con el promedio visible.")
        with compare_center:
            if weight_fig is not None:
                st.plotly_chart(weight_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No hay peso suficiente para comparar a este luchador con el promedio visible.")
        with compare_right:
            if reign_fig is not None:
                st.plotly_chart(reign_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No hay reinados suficientes para comparar a este luchador con el promedio visible.")

        _render_historical_profile_score_ui(wrestler)

        history = _build_history_frame(wrestler.get("title_history"))
        if not history.empty and "title" in history.columns:
            counts = history["title"].fillna("Sin título").value_counts().reset_index()
            counts.columns = ["title", "count"]
            pie = px.pie(
                counts,
                names="title",
                values="count",
                title="Distribución de títulos visibles",
                color_discrete_sequence=["#7b1e2b", "#243447", "#2f855a", "#b45309", "#8b5e3c"],
            )
            _plot_layout(pie, height=320)
            pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(pie, use_container_width=True)

        st.markdown("### Perfil unificado")
        st.markdown(_profile_card_html(wrestler, condensed=True), unsafe_allow_html=True)
        with st.expander("Ver Payload HTML Crudo"):
            st.code(_analytics_payload_html(wrestler, analytics), language="html")
