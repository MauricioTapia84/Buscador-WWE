import streamlit as st

st.title("📰 Panel del Periodista (Contenido y Prensa)")
st.subheader("Tendencias, palmarés y datos históricos descargables")

# Marcador de posición para las métricas requeridas
st.markdown("""
A la brevedad aquí podrás visualizar:
* **Evolución de campeones por año.**
* **Gráfico de duelos más repetidos.**
* **Duración promedio de reinados.**
""")

# Botón simulado de descarga
st.button("Descargar datos en CSV (Simulado)")