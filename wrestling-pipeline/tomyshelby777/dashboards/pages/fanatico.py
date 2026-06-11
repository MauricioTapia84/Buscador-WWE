import streamlit as st

st.title("👤 Panel del Fanático (Entretención)")
st.subheader("Explora la historia de tus luchadores favoritos")

# Ejemplo de la interacción solicitada en la rúbrica
search_term = st.text_input("Ingresa el nombre de un luchador (ej. Brock Lesnar, The Undertaker):", "")

if search_term:
    st.write(f"### Resultados para: {search_term}")
    # Aquí se conectará con la API (FastAPI) en las próximas semanas
    st.warning("⚠️ Conexión con FastAPI pendiente para la Semana 2.")