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
        --brand-burgundy: #7b1e2b;
        --brand-burgundy-deep: #5a1620;
        --brand-ink: #243447;
        --brand-sand: #f7f1e7;
        --brand-card: #ffffff;
        --brand-border: #e8ddd1;
        --brand-success: #2f855a;
        --brand-muted: #6b7280;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(123, 30, 43, 0.12), transparent 28%),
            linear-gradient(135deg, #f7f2e9 0%, #eadfce 100%);
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
        padding: 1.8rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #263445 0%, #7b1e2b 100%);
        color: #fff7ed;
        box-shadow: 0 20px 40px rgba(36, 52, 71, 0.16);
        border: 1px solid rgba(255, 247, 237, 0.16);
    }
    .hero-shell h1, .hero-shell p {
        color: inherit;
    }
    .status-pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 247, 237, 0.12);
        border: 1px solid rgba(255, 247, 237, 0.18);
        margin-right: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    div[role="radiogroup"] {
        display: inline-flex;
        gap: 0 !important;
        padding: 6px;
        border-radius: 16px;
        background: rgba(255,255,255,0.88);
        border: 1px solid var(--brand-border);
        box-shadow: 0 10px 24px rgba(36, 52, 71, 0.08);
        margin-top: 0.4rem;
        margin-bottom: 1.8rem;
    }
    div[role="radiogroup"] > label {
        margin: 0 !important;
        padding: 0.68rem 1.15rem !important;
        border-radius: 12px;
        min-height: auto !important;
        transition: all 0.2s ease;
        color: var(--brand-muted) !important;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(123, 30, 43, 0.08);
    }
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, var(--brand-burgundy), var(--brand-burgundy-deep));
        color: #FFFFFF !important;
        box-shadow: 0 10px 22px rgba(123, 30, 43, 0.22);
    }
    div[role="radiogroup"] > label:has(input:checked) p,
    div[role="radiogroup"] > label:has(input:checked) span,
    div[role="radiogroup"] > label:has(input:checked) div {
        color: #FFFFFF !important;
    }
    div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    div[role="radiogroup"] p {
        margin: 0 !important;
        font-weight: 700 !important;
        color: inherit !important;
    }
    [data-testid="stPlotlyChart"] {
        background: var(--brand-card);
        border: 1px solid var(--brand-border);
        border-radius: 18px;
        padding: 0.75rem 0.75rem 0.35rem;
        box-shadow: 0 12px 30px rgba(36, 52, 71, 0.06);
    }
    [data-testid="stDataFrame"] {
        background: var(--brand-card);
        border: 1px solid var(--brand-border) !important;
        border-radius: 18px !important;
        padding: 0.4rem;
        box-shadow: 0 12px 30px rgba(36, 52, 71, 0.06);
    }
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid var(--brand-border);
        border-radius: 16px;
        box-shadow: 0 12px 26px rgba(36, 52, 71, 0.05);
    }
    [data-testid="stTextInput"] {
        margin-bottom: 0.35rem !important;
    }
    [data-testid="stRadio"] {
        margin-top: 0 !important;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 10px;
    }
    .status-card {
        background: #ffffff;
        border: 1px solid var(--brand-border);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 14px 28px rgba(36, 52, 71, 0.06);
    }
    .status-card .label {
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 8px;
    }
    .status-card .value {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 32px;
        font-weight: 900;
        color: var(--brand-ink);
    }
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        display: inline-block;
        flex: 0 0 12px;
    }
    .status-green {
        color: #2ECC71 !important;
    }
    .status-gray {
        color: #7F8C8D !important;
    }
    .status-red {
        color: #d97706 !important;
    }
    @media (max-width: 900px) {
        .status-grid {
            grid-template-columns: 1fr;
        }
    }
    .profile-view-title {
        margin-top: 1.1rem;
        margin-bottom: 0.2rem;
        color: var(--brand-burgundy-deep);
        font-weight: 900;
    }
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricDelta"] > div,
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"],
    label,
    p,
    li,
    h1,
    h2,
    h3 {
        color: #212121;
    }
    [data-testid="stMetricValue"] {
        color: #212121 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #424242 !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > div {
        border-radius: 14px !important;
        border-color: var(--brand-border) !important;
        background: rgba(255,255,255,0.92) !important;
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
        <h1>WWE Dashboard</h1>
        <p>Una sola entidad unificada para perfiles fanáticos, periodistas y analistas.</p>
        <div class="status-pill">API: {get_api_url()}</div>
        <div class="status-pill">Luchadores: {len(wrestlers)}</div>
        <div class="status-pill">Reinados: {len(titles)}</div>
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
