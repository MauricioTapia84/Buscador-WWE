import streamlit as st

from data_client import fetch_health, fetch_titles, fetch_wrestlers, get_api_url
from role_views import (
    apply_secret,
    ensure_session_state,
    hide_native_page_nav,
    render_developer_view,
    render_fanatico_view,
    render_periodista_view,
    render_role_selector,
)

st.set_page_config(
    page_title="Wrestling Data Explorer",
    layout="wide",
)

ensure_session_state()
hide_native_page_nav()

st.markdown(
    """
    <style>
    :root {
        --brand-ink: #121827;
        --brand-surface: #f2f4f7;
        --brand-surface-strong: #e2e5eb;
        --brand-border: #cbd5e1;
        --brand-muted: #475569;
        --brand-primary: #334155;
        --brand-secondary: #1f2937;
        --brand-accent: #2563eb;
        --brand-success: #16a34a;
        --brand-warning: #d97706;
        --brand-error: #b91c1c;
    }
    .stApp {
        background: linear-gradient(180deg, #edf2f7 0%, #e2e8f0 100%);
    }
    .stApp a.header-anchor,
    .stApp [data-testid="stHeaderActionElements"],
    .stApp [data-testid="StyledLinkIconContainer"],
    .stApp a[href^="#"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebar"] * {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .css-1outpf7, .css-1lcbmhc, [data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
        padding-left: 0 !important;
    }
    .hero-shell {
        padding: 1.75rem;
        border-radius: 24px;
        background: #1f2937;
        color: #f8fafc;
        box-shadow: 0 24px 48px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(148, 163, 184, 0.24);
    }
    .hero-shell h1,
    .hero-shell p {
        color: #f8fafc;
    }
    .status-pill {
        display: inline-block;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.22);
        margin-right: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.92rem;
        color: #dbeafe;
    }
    div[role="radiogroup"] {
        display: inline-flex;
        gap: 0 !important;
        padding: 6px;
        border-radius: 16px;
        background: rgba(255,255,255,0.95);
        border: 1px solid var(--brand-border);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
        margin-top: 0.4rem;
        margin-bottom: 1.8rem;
    }
    div[role="radiogroup"] > label {
        margin: 0 !important;
        padding: 0.7rem 1.15rem !important;
        border-radius: 12px;
        min-height: auto !important;
        transition: all 0.18s ease;
        color: var(--brand-muted) !important;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(148, 163, 184, 0.12);
    }
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #1d4ed8, #0f172a);
        color: #ffffff !important;
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.18);
    }
    div[role="radiogroup"] p {
        margin: 0 !important;
        font-weight: 700 !important;
        color: inherit !important;
    }
    [data-testid="stPlotlyChart"] {
        background: #ffffff;
        border: 1px solid var(--brand-border);
        border-radius: 18px;
        padding: 0.75rem 0.75rem 0.35rem;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
    }
    [data-testid="stDataFrame"] {
        background: #ffffff;
        border: 1px solid var(--brand-border) !important;
        border-radius: 18px !important;
        padding: 0.5rem;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
    }
    div[data-testid="stExpander"] {
        background: #f8fafc;
        border: 1px solid var(--brand-border);
        border-radius: 16px;
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
    }
    [data-testid="stTextInput"] {
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stRadio"] {
        margin-top: 0 !important;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 12px;
    }
    .status-card {
        background: #ffffff;
        border: 1px solid var(--brand-border);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 18px 34px rgba(15, 23, 42, 0.08);
    }
    .status-card .label {
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 10px;
    }
    .status-card .value {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 2rem;
        font-weight: 900;
        color: #111827;
    }
    .section-note {
        color: #475569;
        font-size: 0.96rem;
        margin-top: 0.8rem;
    }
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        display: inline-block;
        flex: 0 0 12px;
    }
    .status-green { color: #16a34a !important; }
    .status-gray { color: #475569 !important; }
    .status-red { color: #d97706 !important; }
    @media (max-width: 900px) {
        .status-grid { grid-template-columns: 1fr; }
    }
    [data-testid="stMetricValue"] { color: #111827 !important; }
    [data-testid="stMetricLabel"] { color: #475569 !important; }
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > div {
        border-radius: 14px !important;
        border-color: var(--brand-border) !important;
        background: rgba(255,255,255,0.94) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

health, health_error = fetch_health()
wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()


def _status_card(label: str, value: str, tone: str) -> str:
    tone_class = {
        "green": "status-green",
        "gray": "status-gray",
        "red": "status-red",
    }.get(tone, "status-gray")
    dot_color = {
        "green": "#2ECC71",
        "gray": "#7F8C8D",
        "red": "#d97706",
    }.get(tone, "#7F8C8D")
    return f"""
    <div class="status-card">
        <div class="label">{label}</div>
        <div class="value {tone_class}">
            <span class="status-dot" style="background:{dot_color};"></span>
            <span>{value}</span>
        </div>
    </div>
    """

st.markdown(
    f"""
    <section class="hero-shell">
        <h1>Wrestling Data Explorer</h1>
        <p>Explora luchadores, campeonatos y predicciones con claridad, sin necesidad de conocimientos técnicos.</p>
        <div class="status-pill">API local: {get_api_url()}</div>
        <div class="status-pill">Luchadores cargados: {len(wrestlers)}</div>
        <div class="status-pill">Reinados disponibles: {len(titles)}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="status-grid">
        {_status_card("API", "OK" if health else "Sin respuesta", "green" if health else "red")}
        {_status_card("Admin", "Habilitado" if st.session_state.get("admin_unlocked") else "Desactivado", "green" if st.session_state.get("admin_unlocked") else "gray")}
        {_status_card("Datos enriquecidos", "Sí" if wrestlers and titles else "Parcial", "green" if wrestlers and titles else "red")}
    </div>
    """,
    unsafe_allow_html=True,
)

if health_error:
    st.warning(f"No se pudo validar `/health`: {health_error}")
if wrestlers_error:
    st.warning(f"No se pudo obtener `/wrestlers`: {wrestlers_error}")
if titles_error:
    st.warning(f"No se pudo obtener `/titles`: {titles_error}")

search_term = st.text_input(
    "Buscador / clave de administrador",
    placeholder="Ej: The Undertaker o la clave de administrador",
)

if search_term and apply_secret(search_term):
    st.success("Modo administrador habilitado para la sesión actual.")

selected_role = render_role_selector()

if selected_role == "Fanático":
    render_fanatico_view(search_term, wrestlers, titles)
elif selected_role == "Periodista":
    render_periodista_view(search_term, wrestlers, titles)
else:
    render_developer_view(search_term, wrestlers, titles)
