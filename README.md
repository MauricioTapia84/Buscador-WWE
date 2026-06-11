# Buscador-WWE
Repositorio para el proyecto "WrestlingData Explorer": integración de múltiples orígenes de datos relacionados con la lucha libre, con pipeline ETL, API, dashboards y despliegue en Docker.

Este README ha sido actualizado para alinearse con el Acta de Proyecto y la estructura definida en la misma.

Estructura principal (resumen):

```
wrestling-pipeline/
├── etl/                     # Scripts del pipeline (extract, transform, validate, load)
├── dashboards/              # Código de Streamlit para dashboards por audiencia
├── api/                     # FastAPI
├── docker/                  # Dockerfiles y docker-compose
├── tests/                   # Pruebas unitarias
├── data/                    # Datos (raw, processed) — ignorar en git
├── docs/                    # Documentación: diagramas, manual de usuario, guía de despliegue
└── repo/                    # Evidencia de uso profesional de Git (capturas, PRs)
```

Resumen del alcance y requisitos (según Acta de Proyecto):

- Integrar al menos tres fuentes de datos (CSV/Excel, API REST, base de datos SQL/NoSQL).
- Implementar pipeline ETL automatizado con validación de esquemas y manejo avanzado de errores.
- Crear dashboard interactivo (Streamlit o Plotly Dash) con vistas diferenciadas por audiencia.
- Desarrollar API mínima (FastAPI) con endpoints principales y documentada.
- Mantener historial y evidencia de trabajo colaborativo en Git (ramas, PRs, revisiones, issues).
- Containerizar servicios con Docker y orquestar con `docker compose`.

Cómo comenzar (desarrollo local con Docker)

1. Sitúate en la carpeta del proyecto:

```bash
cd wrestling-pipeline
```

2. Levantar servicios (API, DB, Dashboard y ETL one-shot):

```bash
docker compose -f docker/docker-compose.yml up --build
```

3. Endpoints y accesos:

- API: http://localhost:8000
- Dashboard (Streamlit): http://localhost:8501

Notas importantes:

- La carpeta `data/` contiene `raw/` y `processed/`. No versionar datos originales grandes — usar `.gitignore`.
- Documentación técnica y diagramas están en `docs/`.
- Para la presentación final, preparar un `README` con pasos de despliegue y un `docker-compose` reproducible.

Si necesitas que genere ejemplos de `README` específicos para `api/`, `etl/` o `dashboards/`, dímelo y los creo.
