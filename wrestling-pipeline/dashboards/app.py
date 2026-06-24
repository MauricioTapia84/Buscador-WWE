import pandas as pd
import streamlit as st

from data_client import fetch_health, fetch_titles, fetch_wrestlers, get_api_url

st.set_page_config(
    page_title="WrestlingData Explorer",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(196, 30, 58, 0.15), transparent 30%),
            linear-gradient(135deg, #f7f2e8 0%, #efe4d1 100%);
    }
    .hero {
        padding: 1.5rem 1.75rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #111111 0%, #8f1d2c 100%);
        color: #fff8ef;
        box-shadow: 0 18px 40px rgba(17, 17, 17, 0.14);
    }
    .hero h1, .hero p {
        color: inherit;
    }
    .pill {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 248, 239, 0.14);
        border: 1px solid rgba(255, 248, 239, 0.22);
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

health, health_error = fetch_health()
wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

st.markdown(
    f"""
    <section class="hero">
        <h1>WrestlingData Explorer</h1>
        <p>Buscador de leyendas WWE con vistas diferenciadas para fanaticos, periodistas y perfil tecnico.</p>
        <div class="pill">API local esperada en: {get_api_url()}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, center, right = st.columns(3)
left.metric("Luchadores visibles", len(wrestlers))
center.metric("Titulos visibles", len(titles))
right.metric("Estado API", "Conectada" if health else "Sin respuesta")

if health_error:
    st.warning(
        "No se pudo consultar `/health`. El dashboard queda listo igual, "
        "pero necesitas levantar la API local o integrar los archivos de `main`."
    )

if wrestlers_error and titles_error:
    st.info(
        "Las vistas siguen disponibles, pero mostraran estados vacios hasta que la API responda."
    )

st.markdown("### Vistas disponibles")
st.markdown(
    """
    - `Fanatico`: busqueda rapida por nombre usando `/search`.
    - `Periodista`: metricas exploratorias y descarga CSV de lo que entregue la API.
    - `Desarrollador`: conectividad, payloads y chequeos de integracion.
    """
)

preview_col, notes_col = st.columns([1.2, 1])

with preview_col:
    st.markdown("### Vista rapida")
    if wrestlers:
        st.dataframe(pd.DataFrame(wrestlers), use_container_width=True, hide_index=True)
    else:
        st.caption("Todavia no hay luchadores disponibles desde la API.")

with notes_col:
    st.markdown("### Estado del rol C")
    st.markdown(
        """
        - Investigacion Wikipedia API documentada en `docs/`.
        - CSV inicial manual de campeones disponible en `data/raw/`.
        - Arquitectura publicada en Mermaid.
        - Dashboard preparado para API local y Docker.
        """
    )
