import streamlit as st

from data_client import fetch_titles, fetch_wrestlers
from role_views import ensure_session_state, hide_native_page_nav, render_developer_view

st.set_page_config(page_title="WWE Dashboard | Desarrollador", layout="wide")
ensure_session_state()
hide_native_page_nav()

st.title("Perfil Desarrollador / Analista")
search_term = st.text_input(
    "Buscar luchador con métricas avanzadas",
    placeholder="Ej: Seth Rollins",
)

wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

if wrestlers_error:
    st.warning(f"No se pudo obtener `/wrestlers`: {wrestlers_error}")
if titles_error:
    st.warning(f"No se pudo obtener `/titles`: {titles_error}")

render_developer_view(search_term, wrestlers, titles)
