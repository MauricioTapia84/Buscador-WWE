import json

import streamlit as st

from data_client import fetch_health, fetch_titles, fetch_wrestlers, get_api_url

st.title("Panel Desarrollador")
st.caption("Monitoreo basico de conectividad y estructura de payloads.")

health, health_error = fetch_health()
wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

st.code(
    f"API_URL={get_api_url()}",
    language="bash",
)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Health", "OK" if health else "ERROR")
col_b.metric("Wrestlers payload", len(wrestlers))
col_c.metric("Titles payload", len(titles))

if health:
    st.success("La API local respondio correctamente al endpoint `/health`.")
else:
    st.error("No hubo respuesta valida de `/health`.")

if health_error or wrestlers_error or titles_error:
    st.markdown("### Diagnostico rapido")
    if health_error:
        st.write(f"- `/health`: {health_error}")
    if wrestlers_error:
        st.write(f"- `/wrestlers`: {wrestlers_error}")
    if titles_error:
        st.write(f"- `/titles`: {titles_error}")

    st.info(
        "Si estas trabajando solo en esta rama, todavia te falta integrar la API que ya existe en `main`."
    )

payload_col, checklist_col = st.columns([1.2, 1])

with payload_col:
    st.markdown("### Payload de health")
    st.code(json.dumps(health or {"status": "unavailable"}, indent=2), language="json")

    st.markdown("### Ejemplo de payload de wrestlers")
    sample_wrestler = wrestlers[0] if wrestlers else {"id": None, "name": "pending"}
    st.code(json.dumps(sample_wrestler, indent=2), language="json")

with checklist_col:
    st.markdown("### Checklist de integracion")
    st.markdown(
        """
        - API local levantada en puerto `8000`
        - variable `API_URL` configurada si usas Docker
        - endpoints `/wrestlers`, `/titles`, `/search`, `/health`
        - ETL publicando datos reales en lugar de mocks
        """
    )

