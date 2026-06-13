import io

import pandas as pd
import streamlit as st

from data_client import fetch_titles, fetch_wrestlers

st.title("Panel Periodista")
st.caption("Metricas rapidas y tablas descargables para exploracion editorial.")

wrestlers, wrestlers_error = fetch_wrestlers()
titles, titles_error = fetch_titles()

if wrestlers_error and titles_error:
    st.warning("La API local no respondio. Esta vista quedara activa cuando integres `main` o levantes la API.")
else:
    wrestlers_df = pd.DataFrame(wrestlers)
    titles_df = pd.DataFrame(titles)

    m1, m2, m3 = st.columns(3)
    m1.metric("Registros de luchadores", len(wrestlers_df))
    m2.metric("Registros de titulos", len(titles_df))
    m3.metric("Titulares unicos", titles_df["holder"].nunique() if "holder" in titles_df else 0)

    if not titles_df.empty and "holder" in titles_df:
        holder_counts = (
            titles_df["holder"]
            .value_counts()
            .rename_axis("holder")
            .reset_index(name="titles_count")
        )
        st.subheader("Titulos por holder")
        st.bar_chart(holder_counts.set_index("holder"))
        st.dataframe(holder_counts, use_container_width=True, hide_index=True)

    if not wrestlers_df.empty and "weight_class" in wrestlers_df:
        class_counts = (
            wrestlers_df["weight_class"]
            .value_counts()
            .rename_axis("weight_class")
            .reset_index(name="count")
        )
        st.subheader("Distribucion por weight class")
        st.bar_chart(class_counts.set_index("weight_class"))

    combined_frames = []
    if not wrestlers_df.empty:
        wrestlers_export = wrestlers_df.copy()
        wrestlers_export.insert(0, "dataset", "wrestlers")
        combined_frames.append(wrestlers_export)
    if not titles_df.empty:
        titles_export = titles_df.copy()
        titles_export.insert(0, "dataset", "titles")
        combined_frames.append(titles_export)

    if combined_frames:
        export_df = pd.concat(combined_frames, ignore_index=True, sort=False)
        buffer = io.StringIO()
        export_df.to_csv(buffer, index=False)
        st.download_button(
            "Descargar snapshot CSV",
            buffer.getvalue().encode("utf-8"),
            file_name="wrestlingdata_snapshot.csv",
            mime="text/csv",
        )

    st.subheader("Notas para prensa")
    st.markdown(
        """
        - Esta vista ya consume la API local.
        - Las metricas creceran cuando el rol A conecte campeones y combates reales.
        - La descarga actual sirve como evidencia funcional para la defensa.
        """
    )

