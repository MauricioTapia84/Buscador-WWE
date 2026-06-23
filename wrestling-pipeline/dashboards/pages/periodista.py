import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

# =========================================
# CARGAR CSS GLOBAL
# =========================================

assets = Path(__file__).parent.parent / "assets"
if (assets / "style.css").exists():
    with open(assets / "style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# =========================================
# CONTROL DE ACCESO & MENÚ DINÁMICO
# =========================================
if "role" not in st.session_state:
    st.session_state["role"] = "usuario"

# Ocultar la página de desarrollador si no es administrador
if st.session_state["role"] != "administrador":
    st.markdown(
        """
        <style>
        a[href*="desarrollador"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar navigation and admin control (replaces top menu)
# Sidebar is defined centrally in `home.py`; pages should not recreate it.

st.write("")

# ==========================
# CABECERA
# ==========================

st.markdown("""
<div style="
padding:25px;
border-radius:15px;
background:linear-gradient(135deg,#111827,#0f172a);
border:1px solid #1f2937;
">

<h1>📰 Panel del Periodista</h1>

<p style="font-size:18px;color:#cbd5e1;">
Análisis de campeonatos, tendencias históricas y estadísticas clave de la WWE.
</p>

</div>
""", unsafe_allow_html=True)

st.write("")

# ==========================
# KPIs
# ==========================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Campeones históricos",
        125
    )

with k2:
    st.metric(
        "Títulos registrados",
        42
    )

with k3:
    st.metric(
        "Reinados analizados",
        685
    )

with k4:
    st.metric(
        "Combates históricos",
        "12.4K"
    )

st.divider()

# ==========================
# DATOS DE EJEMPLO
# ==========================

df_champions = pd.DataFrame({
    "Año":[2019,2020,2021,2022,2023,2024,2025],
    "Campeones":[12,15,14,18,20,17,19]
})

# ==========================
# GRÁFICO 1
# ==========================

st.subheader("📈 Evolución de campeones por año")

fig = px.line(
    df_champions,
    x="Año",
    y="Campeones",
    markers=True
)

fig.update_layout(
    template="plotly_dark",
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================
# DOS COLUMNAS
# ==========================

c1, c2 = st.columns(2)

with c1:

    st.subheader("🏆 Duelos más repetidos")

    df_rivalries = pd.DataFrame({
        "Rivalidad":[
            "Cena vs Orton",
            "Rock vs Austin",
            "Undertaker vs Kane",
            "Triple H vs HBK",
            "Roman vs Brock"
        ],
        "Combates":[
            21,
            18,
            15,
            14,
            12
        ]
    })

    fig2 = px.bar(
        df_rivalries,
        x="Rivalidad",
        y="Combates"
    )

    fig2.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

with c2:

    st.subheader("⏱ Duración promedio de reinados")

    df_reigns = pd.DataFrame({
        "Título":[
            "WWE Championship",
            "World Heavyweight",
            "Intercontinental",
            "United States",
            "Tag Team"
        ],
        "Días":[
            210,
            165,
            122,
            97,
            88
        ]
    })

    fig3 = px.pie(
        df_reigns,
        names="Título",
        values="Días"
    )

    fig3.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

st.divider()

# ==========================
# TABLA
# ==========================

st.subheader("📋 Tabla histórica de campeones")

historic_df = pd.DataFrame({
    "Luchador":[
        "John Cena",
        "Triple H",
        "Roman Reigns",
        "The Rock",
        "Undertaker"
    ],
    "Títulos Mundiales":[
        16,
        14,
        6,
        10,
        7
    ]
})

st.dataframe(
    historic_df,
    use_container_width=True,
    hide_index=True
)

# ==========================
# EXPORTACIÓN
# ==========================

csv = historic_df.to_csv(index=False)

st.download_button(
    label="📥 Descargar estadísticas CSV",
    data=csv,
    file_name="estadisticas_wwe.csv",
    mime="text/csv"
)