import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Wrestling Data Explorer",
    page_icon="🏆",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://api:8000")

# =====================================
# CARGAR CSS
# =====================================

assets = Path(__file__).parent / "assets"

with open(assets / "style.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =====================================
# API
# =====================================

@st.cache_data
def fetch_lists():

    try:
        wrestlers = requests.get(
            f"{API_URL}/wrestlers",
            timeout=3
        ).json()

    except Exception:
        wrestlers = []

    try:
        titles = requests.get(
            f"{API_URL}/titles",
            timeout=3
        ).json()

    except Exception:
        titles = []

    return wrestlers, titles


wrestlers, titles = fetch_lists()

# =====================================
# HERO
# =====================================

st.markdown(
    """
    <div class="hero">
        <h1>🏆 Wrestling Data Explorer</h1>
        <h2>Buscador de Leyendas WWE</h2>
        <p>
            Explora luchadores, campeonatos, estadísticas
            y monitorea el pipeline ETL desde una sola plataforma.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================
# MENÚ SUPERIOR
# =====================================

st.markdown(
    """
    <div class="top-menu">
        🏠 Dashboard &nbsp;&nbsp;&nbsp;
        👤 Fanático &nbsp;&nbsp;&nbsp;
        📊 Periodista &nbsp;&nbsp;&nbsp;
        💻 Desarrollador
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================
# KPIs
# =====================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>🤼 Wrestlers</h3>
        <h1>{len(wrestlers)}</h1>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>🏆 Titles</h3>
        <h1>{len(titles)}</h1>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="kpi-card">
        <h3>🌐 API</h3>
        <h1>Online</h1>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="kpi-card">
        <h3>⚙️ Pipeline</h3>
        <h1>Activo</h1>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# PERFILES
# =====================================

st.markdown("<br>", unsafe_allow_html=True)

st.subheader("Selecciona tu perfil")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="profile-card">
        <h2>⭐ Fanático</h2>
        <p>
            Explora biografías, títulos,
            rivalidades y combates históricos.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="profile-card">
        <h2>📊 Periodista</h2>
        <p>
            Analiza estadísticas,
            rankings y tendencias.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="profile-card">
        <h2>💻 Desarrollador</h2>
        <p>
            Revisa ETL,
            validaciones y monitoreo técnico.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =====================================
# BUSCADOR
# =====================================

st.subheader("🔎 Búsqueda Global")

q = st.text_input(
    "Buscar luchador o campeonato"
)

if q:

    try:

        res = requests.get(
            f"{API_URL}/search",
            params={"q": q},
            timeout=3
        ).json()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🤼 Wrestlers")
            st.write(res.get("wrestlers", []))

        with col2:
            st.subheader("🏆 Titles")
            st.write(res.get("titles", []))

    except Exception:

        st.error(
            "No fue posible conectar con la API."
        )

# =====================================
# RESUMEN VISUAL
# =====================================

st.subheader("📈 Resumen General")

chart_df = pd.DataFrame({
    "Categoría": [
        "Wrestlers",
        "Titles"
    ],
    "Cantidad": [
        len(wrestlers),
        len(titles)
    ]
})

fig = px.bar(
    chart_df,
    x="Categoría",
    y="Cantidad",
    text="Cantidad"
)

fig.update_layout(
    template="plotly_dark",
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# TABLAS
# =====================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🤼 Wrestlers")

    if wrestlers:

        dfw = pd.DataFrame(wrestlers)

        st.dataframe(
            dfw,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No hay datos de wrestlers."
        )

with col2:

    st.subheader("🏆 Titles")

    if titles:

        dft = pd.DataFrame(titles)

        st.dataframe(
            dft,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No hay datos de títulos."
        )

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "Wrestling Data Explorer © 2026 | ETL + FastAPI + PostgreSQL + Streamlit"
)