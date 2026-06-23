import streamlit as st
from pathlib import Path


def render_sidebar():
    if "role" not in st.session_state:
        st.session_state["role"] = "usuario"

    if "page" not in st.session_state:
        st.session_state["page"] = "/"

    with st.sidebar:
        st.markdown("### Navegación")
        if st.button("🏠 Dashboard"):
            st.session_state["page"] = "/"
            st.experimental_rerun()
        if st.button("👤 Fanático"):
            st.session_state["page"] = "/fanatico"
            st.experimental_rerun()
        if st.button("📊 Periodista"):
            st.session_state["page"] = "/periodista"
            st.experimental_rerun()
        if st.session_state.get("role") == "administrador":
            if st.button("💻 Desarrollador"):
                st.session_state["page"] = "/desarrollador"
                st.experimental_rerun()
        st.markdown("---")
        if st.session_state.get("role") == "administrador":
            if st.button("🔴 Salir de Admin", key="logout_btn_helper"):
                st.session_state["role"] = "usuario"
                st.experimental_rerun()
        else:
            st.markdown("👤 Modo Usuario (Ingresa la clave en el buscador para modo Admin)")


def data_path():
    # Resolve data folder relative to dashboards location
    base = Path(__file__).parents[1]
    return base / "data" / "processed"
