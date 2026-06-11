import streamlit as st

# Configuración de la página (Debe ser la primera línea de Streamlit)
st.set_page_config(
    page_title="WrestlingData Explorer",
    page_icon="🤼",
    layout="wide"
)

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