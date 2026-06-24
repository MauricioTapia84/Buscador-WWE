import streamlit as st

from data_client import fetch_titles, fetch_wrestlers
from role_views import apply_secret, ensure_session_state, hide_native_page_nav, render_fanatico_view

st.set_page_config(page_title="WWE Dashboard | Fanático", page_icon="W", layout="wide")
ensure_session_state()
hide_native_page_nav()

st.title("Perfil Fanático")
search_term = st.text_input(
    "Buscar luchador o ingresar clave de administrador",
    placeholder="Ej: Cody Rhodes",
)

if search_term and apply_secret(search_term):
    st.success("Modo administrador habilitado para la sesión actual.")

wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

if wrestlers_error:
    st.warning(f"No se pudo obtener `/wrestlers`: {wrestlers_error}")
if titles_error:
    st.warning(f"No se pudo obtener `/titles`: {titles_error}")

render_fanatico_view(search_term, wrestlers, titles)
