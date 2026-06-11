import streamlit as st

st.title("💻 Panel Técnico (Desarrollador)")
st.subheader("Estado actual del Pipeline ETL y logs del sistema")

# Contenedores para la data que te pasará el Rol A más adelante
st.metric(label="Estado del último ETL", value="Pendiente", delta="Semana 1")

st.code("""
# Espacio reservado para mostrar el log rotatorio (logging)
# Aquí se imprimirán las validaciones de Pydantic
""", language="bash")
