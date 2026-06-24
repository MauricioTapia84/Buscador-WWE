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
    page_icon="W",
    layout="wide",
)

ensure_session_state()
hide_native_page_nav()

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(185, 28, 28, 0.15), transparent 28%),
            linear-gradient(135deg, #f8f4ec 0%, #eadfce 100%);
    }
    .hero-shell {
        padding: 1.8rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #111827 0%, #991b1b 100%);
        color: #fff7ed;
        box-shadow: 0 20px 40px rgba(17, 24, 39, 0.15);
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
    </style>
    """,
    unsafe_allow_html=True,
)

health, health_error = fetch_health()
wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

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

top_a, top_b, top_c = st.columns(3)
top_a.metric("API", "OK" if health else "Sin respuesta")
top_b.metric("Admin", "Habilitado" if st.session_state.get("admin_unlocked") else "Desactivado")
top_c.metric("Datos enriquecidos", "Sí" if wrestlers and titles else "Parcial")

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
