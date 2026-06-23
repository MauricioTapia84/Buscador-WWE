import os
import requests
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import textwrap
from pathlib import Path

st.set_page_config(
    page_title="Wrestling Data Explorer - Fanático",
    page_icon="👤",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://api:8000")

# =========================================
# DATA
# =========================================

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

@st.cache_data
def search_wrestlers(query: str):
    try:
        response = requests.get(
            f"{API_URL}/search",
            params={"q": query},
            timeout=3
        )
        return response.json()
    except Exception:
        return {}

wrestlers, titles = fetch_lists()

# =========================================
# LAYOUT PRINCIPAL
# =========================================

main_html = textwrap.dedent(f"""
    <div class="dashboard-layout">

        <div class="sidebar-panel">
            <div class="logo">WWE DATA</div>
            <div class="menu">
                <div class="menu-item">🏠 Dashboard</div>
                <div class="menu-item active">👤 Fanático</div>
                <div class="menu-item">📊 Periodista</div>
                <div class="menu-item">💻 Desarrollador</div>
                <div class="menu-item">⚙ Configuración</div>
            </div>
        </div>

        <div class="main-panel">
            <div class="hero">
                <div class="hero-left">
                    <div class="badge">🏆 WWE Analytics Platform</div>
                    <h1>Wrestling Data Explorer</h1>
                    <h2>Buscador Inteligente de Leyendas WWE</h2>
                    <p>
                        Explora luchadores, campeonatos, estadísticas históricas
                        y monitorea el pipeline ETL desde una plataforma moderna
                        diseñada para fanáticos, periodistas y desarrolladores.
                    </p>
                    <div class="hero-buttons">
                        <div class="btn btn-primary">🔍 Explorar</div>
                        <div class="btn btn-secondary">📊 Estadísticas</div>
                    </div>
                </div>
                <div class="hero-right">
                    <div class="stat-card">
                        <div class="stat-icon">🤼</div>
                        <div class="stat-number">{len(wrestlers)}</div>
                        <div class="stat-label">Wrestlers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-number">{len(titles)}</div>
                        <div class="stat-label">Títulos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🌐</div>
                        <div class="stat-number">Online</div>
                        <div class="stat-label">API</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⚙️</div>
                        <div class="stat-number">Activo</div>
                        <div class="stat-label">Pipeline</div>
                    </div>
                </div>
            </div>

            <div class="kpis">
                <div class="kpi">
                    <div class="kpi-title">Combates Registrados</div>
                    <div class="kpi-value">4,523</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Eventos</div>
                    <div class="kpi-value">320</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Años de Historia</div>
                    <div class="kpi-value">40+</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Disponibilidad</div>
                    <div class="kpi-value">99%</div>
                </div>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>⭐ Fanático</h3>
                    <p>
                        Descubre biografías, rivalidades, campeonatos
                        y momentos históricos.
                    </p>
                </div>
                <div class="card">
                    <h3>📊 Periodista</h3>
                    <p>
                        Analiza estadísticas, rankings, reinados
                        y tendencias históricas.
                    </p>
                </div>
                <div class="card">
                    <h3>💻 Desarrollador</h3>
                    <p>
                        Monitorea ETL, API, logs, validaciones
                        y calidad de datos.
                    </p>
                </div>
            </div>
        </div>
    </div>
"""
)

assets = Path(__file__).parent.parent / "assets"

page_css = ""
if assets.exists():
    try:
        with open(assets / "style.css", encoding="utf-8") as f:
            page_css = f.read()
    except Exception:
        page_css = ""

components.html(
    f"""
    <style>
    {page_css}
    </style>
    {main_html.strip()}
    """,
    height=820,
)

st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🔎 Búsqueda Global")

search_term = st.text_input(
    "Buscar luchador o campeonato",
    placeholder="Ej: The Undertaker"
)

if search_term:
    result = search_wrestlers(search_term)
    st.success(f"Mostrando resultados para: {search_term}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Wrestling_ring.jpg/640px-Wrestling_ring.jpg",
            use_container_width=True
        )

    with col2:
        st.markdown(
            f"""
            ### {search_term}

            **Nombre completo:** {result.get('name', 'The Undertaker')}

            **Altura:** {result.get('height', '2.08 m')}

            **Peso:** {result.get('weight', '140 kg')}

            **Debut:** {result.get('debut', '1990')}

            **Estado:** {result.get('status', 'Retirado')}

            **Alias:** {result.get('alias', 'The Deadman')}
            """,
        )

    st.divider()
    st.subheader("🏆 Palmarés")

    titles_df = pd.DataFrame({
        "Título": [
            "WWE Championship",
            "World Heavyweight Championship",
            "Tag Team Championship"
        ],
        "Veces": [4, 3, 6]
    })

    st.dataframe(
        titles_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🔥 Logros destacados")
    st.markdown(
        """
        - Récord histórico en WrestleMania.
        - Miembro del Salón de la Fama WWE.
        - Más de tres décadas de carrera.
        - Uno de los personajes más icónicos de la lucha libre.
        """
    )
else:
    st.info("Ingresa un nombre para comenzar la búsqueda.")

st.divider()

st.subheader("⭐ Leyendas populares")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.button("The Undertaker")
with c2:
    st.button("John Cena")
with c3:
    st.button("Triple H")
with c4:
    st.button("The Rock")

