import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path
import importlib.util

# Load nav helper via file path to avoid package import issues in Streamlit
nav_path = Path(__file__).parent / "nav.py"
spec = importlib.util.spec_from_file_location("dashboards.nav", str(nav_path))
if spec and spec.loader:
    nav = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nav)
else:
    raise ImportError(f"Could not load nav helper from {nav_path}")

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
# INICIALIZAR ROL
# =====================================
if "role" not in st.session_state:
    st.session_state["role"] = "usuario"

# Ocultar la página de desarrollador si no es administrador
if st.session_state["role"] != "administrador":
    st.markdown(
        """
        <style>
        a[href*="desarrollador"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================
# SIDEBAR: centralizada en helper
# =====================================
nav.render_sidebar()

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
# UTILS DE RENDER
# =====================================

def render_wrestler_card(w):
    name = w.get("name", "N/A")
    height = f"{w.get('height_cm')} cm" if w.get('height_cm') else "N/A"
    weight = f"{w.get('weight_kg')} kg" if w.get('weight_kg') else "N/A"
    nat = w.get("nationality") or "Desconocido"
    debut = w.get("debut_year") or "N/A"
    desc = w.get("description") or "Sin descripción disponible."
    
    nat_lower = str(nat).lower()
    flag = "🇺🇸"
    if "mex" in nat_lower:
        flag = "🇲🇽"
    elif "can" in nat_lower:
        flag = "🇨🇦"
    elif "jpn" in nat_lower or "jap" in nat_lower:
        flag = "🇯🇵"
    elif "gbr" in nat_lower or "uk" in nat_lower or "ing" in nat_lower:
        flag = "🇬🇧"
    elif "descon" in nat_lower or not nat or nat == "Desconocido":
        flag = "🤼"
        
    return f"""
    <div class="result-card">
        <div class="result-card-header">
            <div class="wrestler-info">
                <div class="avatar-placeholder">{flag}</div>
                <div>
                    <div class="wrestler-name">{name}</div>
                    <div class="wrestler-meta">
                        <span>📏 {height}</span>
                        <span>⚖️ {weight}</span>
                        <span>🏛️ {nat}</span>
                        <span>📅 Debut: {debut}</span>
                    </div>
                </div>
            </div>
            <div>
                <span class="badge-title">🤼 Wrestler</span>
            </div>
        </div>
        <div class="result-card-body" style="grid-template-columns: 1fr;">
            <div>
                <div class="section-title">📝 Biografía / Descripción</div>
                <p style="color: #cbd5e1; line-height: 1.6; font-size: 14px;">{desc}</p>
            </div>
        </div>
    </div>
    """

def render_title_card(t):
    title = t.get("title") or t.get("name") or "N/A"
    holder = t.get("holder") or "Vacante"
    won_date = t.get("won_date") or "N/A"
    reign_days = t.get("reign_days")
    reign_str = f"{reign_days} días" if reign_days is not None else "N/A"
    
    return f"""
    <div class="result-card">
        <div class="result-card-header">
            <div class="wrestler-info">
                <div class="avatar-placeholder">🏆</div>
                <div>
                    <div class="wrestler-name">{title}</div>
                    <div class="wrestler-meta">
                        <span>👑 Campeón: <strong>{holder}</strong></span>
                        <span>📅 Ganado: {won_date}</span>
                        <span>⏱️ Reinado: {reign_str}</span>
                    </div>
                </div>
            </div>
            <div>
                <span class="badge-title" style="background: #ef444420; color: #ef4444; border-color: #ef444440;">🏆 Campeonato</span>
            </div>
        </div>
    </div>
    """

# =====================================
# BUSCADOR
# =====================================

st.subheader("🔎 Búsqueda Global")

q = st.text_input(
    "Buscar luchador o campeonato"
)

if q:
    if q.strip() == "K#9vLp$2mQx@7nRf!4Zd":
        st.session_state["role"] = "administrador"
        st.success("🔓 ¡Modo Administrador activado!")
        st.experimental_rerun()
    try:
        res = requests.get(
            f"{API_URL}/search",
            params={"q": q},
            timeout=3
        ).json()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h3>🤼 Wrestlers</h3>", unsafe_allow_html=True)
            wrestlers_list = res.get("wrestlers", [])
            if wrestlers_list:
                for w in wrestlers_list:
                    st.markdown(render_wrestler_card(w), unsafe_allow_html=True)
            else:
                st.info("No se encontraron luchadores.")

        with col2:
            st.markdown("<h3>🏆 Titles</h3>", unsafe_allow_html=True)
            titles_list = res.get("titles", [])
            if titles_list:
                for t in titles_list:
                    st.markdown(render_title_card(t), unsafe_allow_html=True)
            else:
                st.info("No se encontraron campeonatos.")

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

# =====================================
# DATOS VIA API: wrestlers y matches
# =====================================
st.subheader("📚 Datos ETL (API)")
cols = st.columns(2)
with cols[0]:
    st.markdown("**Wrestlers (unificados - API)**")
    try:
        resp = requests.get(f"{API_URL}/wrestlers?source=all", timeout=5)
        if resp.status_code == 200:
            wdata = resp.json()
            if wdata:
                dfw = pd.DataFrame(wdata)
                st.dataframe(dfw.head(200), use_container_width=True)
            else:
                st.info("No hay wrestlers disponibles vía API.")
        else:
            st.error(f"API /wrestlers responded {resp.status_code}")
    except Exception as e:
        st.error(f"Error consultando API /wrestlers: {e}")

with cols[1]:
    st.markdown("**Matches (normalizados - API)**")
    try:
        resp = requests.get(f"{API_URL}/matches", timeout=5)
        if resp.status_code == 200:
            mdata = resp.json()
            if mdata:
                dfm = pd.DataFrame(mdata)
                st.dataframe(dfm.head(200), use_container_width=True)
            else:
                st.info("No hay matches disponibles vía API.")
        else:
            st.error(f"API /matches responded {resp.status_code}")
    except Exception as e:
        st.error(f"Error consultando API /matches: {e}")