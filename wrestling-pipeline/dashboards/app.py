import os
import requests
import streamlit as st
import pandas as pd

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

if not wrestlers and not titles:
    st.warning("No se pudo conectar a la API. Revisa `API_URL` y que el servicio `api` esté levantado.")

if wrestlers:
    dfw = pd.DataFrame(wrestlers)
    st.subheader("Wrestlers")
    st.dataframe(dfw)

if titles:
    dft = pd.DataFrame(titles)
    st.subheader("Titles")
    st.dataframe(dft)

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
