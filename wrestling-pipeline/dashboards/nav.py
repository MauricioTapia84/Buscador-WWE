import streamlit as st
from pathlib import Path


def render_sidebar():
    if "role" not in st.session_state:
        st.session_state["role"] = "usuario"

    if "page" not in st.session_state:
        st.session_state["page"] = "/"

    with st.sidebar:
        # Top small header showing current page (capitalized first letter)
        page = st.session_state.get("page", "/")
        # Map page path to display label
        page_label = {
            "/": "home",
            "/fanatico": "fanatico",
            "/periodista": "periodista",
            "/desarrollador": "desarrollador",
        }.get(page, "home")

        # Capitalize first letter
        page_label = page_label.capitalize()

        st.markdown(f"### {page_label}")

        # Show only role-dependent navigation
        if st.session_state.get("role") == "administrador":
            if st.button("🔧 Desarrollador"):
                st.session_state["page"] = "/desarrollador"
                st.experimental_rerun()
        elif st.session_state.get("role") == "periodista":
            if st.button("📊 Periodista"):
                st.session_state["page"] = "/periodista"
                st.experimental_rerun()
        else:
            # Default usuario / fanatico
            if st.button("👤 Fanático"):
                st.session_state["page"] = "/fanatico"
                st.experimental_rerun()

        st.markdown("---")
        # Admin toggle / helper info
        if st.session_state.get("role") == "administrador":
            if st.button("🔴 Salir de Admin", key="logout_btn_helper"):
                st.session_state["role"] = "usuario"
                st.experimental_rerun()
        else:
            st.markdown("👤 Modo Usuario — ingresa la clave en el buscador para activar Admin")


def data_path():
    # Resolve data folder relative to dashboards location
    base = Path(__file__).parents[1]
    return base / "data" / "processed"
