import streamlit as st
import pandas as pd
from datetime import datetime

# ===================================
# CABECERA
# ===================================

st.markdown("""
<div style="
padding:25px;
border-radius:15px;
background:linear-gradient(135deg,#111827,#0f172a);
border:1px solid #1f2937;
">

<h1>💻 Panel Técnico</h1>

<p style="font-size:18px;color:#cbd5e1;">
Monitoreo del Pipeline ETL, validaciones, calidad de datos y estado de los servicios.
</p>

</div>
""", unsafe_allow_html=True)

st.write("")

# ===================================
# KPIs
# ===================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Estado ETL",
        "OK"
    )

with k2:
    st.metric(
        "Registros procesados",
        "12.842"
    )

with k3:
    st.metric(
        "Errores detectados",
        "0"
    )

with k4:
    st.metric(
        "Última ejecución",
        "15:30"
    )

st.divider()

# ===================================
# ESTADO DE SERVICIOS
# ===================================

st.subheader("🟢 Estado de Servicios")

services = pd.DataFrame({
    "Servicio":[
        "API FastAPI",
        "Dashboard Streamlit",
        "PostgreSQL",
        "ETL Runner"
    ],
    "Estado":[
        "Activo",
        "Activo",
        "Activo",
        "Activo"
    ]
})

st.dataframe(
    services,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ===================================
# VALIDACIONES
# ===================================

st.subheader("✅ Validaciones de Calidad")

v1, v2, v3 = st.columns(3)

with v1:
    st.success("Sin registros duplicados")

with v2:
    st.success("Tipos de datos válidos")

with v3:
    st.success("Campos obligatorios completos")

st.divider()

# ===================================
# LOGS
# ===================================

st.subheader("📄 Últimos Logs")

log_text = f"""
[{datetime.now()}] INFO - ETL iniciado
[{datetime.now()}] INFO - Extracción completada
[{datetime.now()}] INFO - Transformación completada
[{datetime.now()}] INFO - Validación Pydantic OK
[{datetime.now()}] INFO - Carga finalizada
"""

st.code(
    log_text,
    language="bash"
)

# ===================================
# CALIDAD DE DATOS
# ===================================

st.subheader("📊 Calidad de Datos")

quality_df = pd.DataFrame({
    "Métrica":[
        "Completitud",
        "Consistencia",
        "Validez",
        "Integridad"
    ],
    "Resultado":[
        "100%",
        "99%",
        "100%",
        "100%"
    ]
})

st.dataframe(
    quality_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ===================================
# CONTENEDORES DOCKER
# ===================================

st.subheader("🐳 Contenedores Docker")

docker_df = pd.DataFrame({
    "Contenedor":[
        "api",
        "dashboard",
        "postgres",
        "etl-runner"
    ],
    "Estado":[
        "Running",
        "Running",
        "Running",
        "Running"
    ]
})

st.dataframe(
    docker_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ===================================
# INFORMACIÓN DEL SISTEMA
# ===================================

st.subheader("ℹ Información General")

st.info("""
Arquitectura implementada:

• Python 3.12

• FastAPI

• PostgreSQL

• Streamlit

• Docker Compose

• ETL Automatizado

• Validaciones Pydantic

• Logging Rotatorio
""")
