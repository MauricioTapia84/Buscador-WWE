import pandas as pd
import streamlit as st

from data_client import search_catalog

st.title("Panel Fanatico")
st.caption("Explora luchadores y titulos desde la API local.")

query = st.text_input(
    "Busca un luchador o titulo",
    placeholder="Ejemplo: Undertaker, Cena, Championship",
)

if not query:
    st.info("Escribe un nombre para consultar el endpoint `/search`.")
else:
    results, error = search_catalog(query)
    if error or not results:
        st.error(
            "No fue posible consultar la busqueda. Verifica que la API local este arriba."
        )
    else:
        wrestlers = results.get("wrestlers", [])
        titles = results.get("titles", [])

        summary_a, summary_b = st.columns(2)
        summary_a.metric("Luchadores encontrados", len(wrestlers))
        summary_b.metric("Titulos encontrados", len(titles))

        st.markdown("### Resultados")
        if wrestlers:
            st.subheader("Luchadores")
            st.dataframe(
                pd.DataFrame(wrestlers),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("La API no devolvio luchadores para esta busqueda.")

        if titles:
            st.subheader("Titulos")
            st.dataframe(
                pd.DataFrame(titles),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("La API no devolvio titulos para esta busqueda.")

st.divider()
st.markdown(
    """
    ### Interaccion esperada en la entrega
    Cuando el ETL y la API esten completos, esta vista podra mostrar:
    - biografia y datos fisicos del luchador
    - titulos ganados y reinados
    - combates memorables y eventos asociados
    """
)

