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
# CARGAR CSS GLOBAL
# =========================================
assets = Path(__file__).parent.parent / "assets"
if (assets / "style.css").exists():
    with open(assets / "style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# =========================================
# CONTROL DE ACCESO & MENÚ DINÁMICO
# =========================================
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

# Sidebar navigation and admin control (replaces top menu)
# Sidebar is defined centrally in `home.py`; pages should not recreate it.

st.write("")

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
# CABECERA DEL BUSCADOR
# =========================================
st.markdown("""
<div class="hero" style="padding: 40px; margin-bottom: 20px;">
    <h1>🔍 Buscador de Leyendas WWE</h1>
    <p style="font-size: 16px; color: #cbd5e1;">
        Encuentra perfiles de tus luchadores favoritos, revisa biografías, peso, altura y detalles de los campeonatos de forma interactiva.
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("🔎 Búsqueda Global")

search_term = st.text_input(
    "Buscar luchador o campeonato",
    placeholder="Ej: The Undertaker"
)

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

if search_term:
    if search_term.strip() == "K#9vLp$2mQx@7nRf!4Zd":
        st.session_state["role"] = "administrador"
        st.success("🔓 ¡Modo Administrador activado!")
        st.experimental_rerun()
    result = search_wrestlers(search_term)
    st.success(f"Mostrando resultados para: {search_term}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>🤼 Wrestlers</h3>", unsafe_allow_html=True)
        wrestlers_list = result.get("wrestlers", [])
        if wrestlers_list:
            for w in wrestlers_list:
                st.markdown(render_wrestler_card(w), unsafe_allow_html=True)
        else:
            st.info("No se encontraron luchadores.")

    with col2:
        st.markdown("<h3>🏆 Titles</h3>", unsafe_allow_html=True)
        titles_list = result.get("titles", [])
        if titles_list:
            for t in titles_list:
                st.markdown(render_title_card(t), unsafe_allow_html=True)
        else:
            st.info("No se encontraron campeonatos.")
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

