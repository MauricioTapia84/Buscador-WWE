import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página (Debe ser la primera línea de Streamlit)
st.set_page_config(
    page_title="WrestlingData Explorer",
    page_icon="🤼",
    layout="wide"
)

# API base URL (en Docker, el servicio se llama `api`)
API_URL = os.getenv("API_URL", "http://api:8000")

# Título Principal
st.title("🤼 WrestlingData Explorer: Buscador de Leyendas")
st.subheader("Bienvenidos al pipeline de datos y buscador inteligente de la WWE")

st.markdown("""
---
### ¡Hola! Elige tu perfil en la barra lateral izquierda para comenzar:
* **👤 Fanático:** Explora la biografía, títulos y combates de tus luchadores favoritos.
* **📰 Periodista:** Accede a estadísticas clave, gráficos de tendencias y tablas descargables.
* **💻 Desarrollador:** Revisa el estado del pipeline ETL, logs de ejecución y validaciones.
""")

# --- Visual tweaks (CSS) - only aesthetics ---
st.markdown(
        """
        <style>
        /* Page background and main container */
        .stApp {
            background-color: #0f1720;
            color: #e6eef6;
            font-family: 'Inter', system-ui, sans-serif;
        }
        /* Card-like container */
        .main-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            padding: 1.2rem 1.6rem;
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(2,6,23,0.6);
            margin-bottom: 1rem;
        }
        /* Sidebar adjustments */
        .css-1d391kg {padding-top: 1rem;} /* streamlit class for sidebar spacing (may vary) */
        /* Headings */
        h1, h2, h3 { color: #f8fafc; }
        /* Table header background */
        .stDataFrame table thead th { background: rgba(255,255,255,0.03); }
        /* Info box style */
        .stAlert { border-left: 4px solid #2563eb; background: rgba(37,99,235,0.04); }
        </style>
        """,
        unsafe_allow_html=True,
)

st.info("💡 Consejo: Usa el menú de la izquierda para navegar de forma interactiva entre las distintas vistas.")


@st.cache_data
def fetch_lists():
    try:
        w = requests.get(f"{API_URL}/wrestlers", timeout=3).json()
    except Exception:
        w = []
    try:
        t = requests.get(f"{API_URL}/titles", timeout=3).json()
    except Exception:
        t = []
    return w, t


wrestlers, titles = fetch_lists()

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if not wrestlers and not titles:
        st.warning("No se pudo conectar a la API. Revisa `API_URL` y que el servicio `api` esté levantado.")

    col1, col2 = st.columns([2, 1])
    with col1:
        if wrestlers:
            dfw = pd.DataFrame(wrestlers)
            st.subheader("Wrestlers")
            # Use Plotly table for improved styling
            figw = go.Figure(data=[go.Table(
                header=dict(values=list(dfw.columns), fill_color='rgba(255,255,255,0.04)', align='left'),
                cells=dict(values=[dfw[col] for col in dfw.columns], fill_color='rgba(255,255,255,0.01)', align='left')
            )])
            figw.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=200)
            st.plotly_chart(figw, use_container_width=True)

        if titles:
            dft = pd.DataFrame(titles)
            st.subheader("Titles")
            figt = go.Figure(data=[go.Table(
                header=dict(values=list(dft.columns), fill_color='rgba(255,255,255,0.04)', align='left'),
                cells=dict(values=[dft[col] for col in dft.columns], fill_color='rgba(255,255,255,0.01)', align='left')
            )])
            figt.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=200)
            st.plotly_chart(figt, use_container_width=True)

    with col2:
        st.subheader("Acceso rápido")
        st.write("- Usa la caja de búsqueda para buscar luchadores o títulos.")
        st.write("- Exporta tablas desde la interfaz de la API.")
        # Simple summary card
        with st.container():
            st.markdown("""
            <div style='background: rgba(255,255,255,0.02); padding:12px; border-radius:8px; margin-top:8px;'>
            <h4 style='margin:0; color:#f8fafc;'>Resumen</h4>
            <p style='margin:4px 0 0 0; color:#cfe6ff;'>Wrestlers: <strong>{}</strong></p>
            <p style='margin:2px 0 0 0; color:#cfe6ff;'>Titles: <strong>{}</strong></p>
            </div>
            """.format(len(wrestlers) if wrestlers else 0, len(titles) if titles else 0), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Search box that uses API /search
q = st.text_input("Buscar luchador o título:")
if q:
    try:
        res = requests.get(f"{API_URL}/search", params={"q": q}, timeout=3).json()
        st.subheader("Resultados - Wrestlers")
        st.write(res.get("wrestlers", []))
        st.subheader("Resultados - Titles")
        st.write(res.get("titles", []))
    except Exception:
        st.error("Error conectando con la API de búsqueda.")
