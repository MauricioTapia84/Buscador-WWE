# Checklist de tareas pendientes — WrestlingData Explorer

## Resumen

Checklist generado a partir de la pauta de evaluación y el estado actual del repo.

---

## 1) Pipeline ETL (20%)

- [x] Añadir logging estructurado en `etl/` (format JSON, niveles).
- [x] Implementar reintentos y manejo de fallos por etapa (extract/transform/load).
- [x] Generar reportes de calidad (CSV/HTML) tras cada ejecución.

**Completados (migrados / removidos de la checklist):**

- **Validaciones:** Se consolidaron y mejoraron las validaciones en `etl/validate.py` (Pandera). Archivo: [wrestling-pipeline/etl/validate.py](wrestling-pipeline/etl/validate.py)
- **Pruebas ETL:** Se añadieron tests unitarios para `transform`, `validate` y `load`. Archivo: [wrestling-pipeline/tests/test_etl.py](wrestling-pipeline/tests/test_etl.py)
- **CI ETL:** Se creó workflow para ejecutar tests ETL en GitHub Actions. Archivo: [.github/workflows/etl-ci.yml](.github/workflows/etl-ci.yml)
 - **Logging estructurado:** Se añadió `etl/logging_config.py` con formateador JSON y se instrumentaron los extractores (`extract_wikipedia.py`, `extract_thesportsdb.py`, `extract_kaggle.py`).
 - **Reintentos:** Se añadió `etl/retry_utils.py` y se aplicaron reintentos en llamadas a request, extracción sqlite y carga a BD.
 - **Reportes de calidad:** `validate._write_report` ahora emite JSON, CSV y HTML de los reportes de validación.

## 1.1) Fuentes de datos y datos de ejemplo (status)

- Observación: Actualmente la app contiene 2 luchadores y 2 títulos (datos posiblemente estáticos/de prueba) visibles en la interfaz/dashboard.
- Objetivo: Reemplazar esos datos estáticos por datos reales combinando las 3 fuentes previstas: TheSportsDB (API REST, imágenes y metadatos), fuentes web HTML (historia y biografías) y el dataset de Kaggle (luchas, títulos adicionales, resultados).

Tareas propuestas:

- [ ] Auditar el código para localizar el origen actual de los datos de ejemplo (frontend/api/static) y confirmar archivos con los 2 luchadores/2 títulos.
- [ ] Implementar extractor `etl/extract_thesportsdb.py` para obtener luchadores, metadata e imágenes desde TheSportsDB (API REST). (pendiente)
- [ ] Implementar extractor `etl/extract_wikipedia.py` o mejorar el existente para scrapear páginas HTML con historia y palmarés. (pendiente)
- [ ] Implementar extractor `etl/extract_kaggle.py` para consumir el dataset local/descargado de Kaggle y unir tablas de luchas y títulos. (pendiente)
- [ ] Definir y documentar la lógica de fusión/score de entidades (cómo reconciliar nombres/aliases entre fuentes). (pendiente)
- [ ] Actualizar `dashboards/` y `api/` para consumir la tabla procesada `data/processed/wrestlers.parquet` y `titles.parquet` en vez de datos estáticos. (pendiente)
- [ ] Añadir pruebas de integración que validen que al ejecutar ETL completo se generen >10 luchadores y >5 títulos (ejemplo de sanity check). (pendiente)

Notas: Puedo preparar los extractores y la lógica de matching; antes de ejecutar cambios destructivos, pediré confirmación para crear PR con los extractores y las dependencias necesarios.

## 2) Documentación técnica (20%)

- [ ] Generar `swagger.json` / OpenAPI para la `API` en `api/`.
- [ ] Documentar contratos de datos (schemas) en `docs/`.
- [ ] Añadir ejemplos de uso y tutorial paso-a-paso en `docs/guia_despliegue.md`.
- [ ] Completar `docs/.md/acta_proyecto.md` con la conversión del `.docx`.
- [ ] Añadir `CONTRIBUTING.md` y `RELEASE.md`.

## 3) Dashboard interactivo (25%)

- [ ] Añadir gráficos interactivos con Plotly en `dashboards/`.
- [ ] Incluir datos de ejemplo en `data/processed/sample_*` para demo.
- [ ] Crear tests de integración que validen endpoints consumidos por la UI.
- [ ] Mejorar mensajes y manejo de errores en `dashboards/app.py`.

## 4) Uso profesional de Git (15%)

- [ ] Publicar evidencia de PRs/branches/reviews en GitHub (enlaces en `repo/` o `docs/`).
- [ ] Añadir `CONTRIBUTING.md` con convención de ramas y PRs.
- [ ] Crear tags/releases y changelog (CHANGELOG.md).

## 5) Docker y despliegue (20%)

- [ ] Añadir `.env.example` con variables necesarias.
- [ ] Añadir healthchecks en `docker-compose.yml` y `Dockerfile.*`.
- [ ] Implementar espera dependiente (wait-for) para servicios en `docker-compose`.
- [ ] Crear workflow CI que construya y haga smoke tests de `docker-compose`.

## 6) Testing y CI

- [ ] Añadir GitHub Actions que ejecuten: lint, tests (api+etl), build Docker.
- [ ] Configurar badge(s) en `README.md` para estado de CI.

## 7) Presentación / Demo

- [ ] Preparar `data/processed/demo_dataset.csv` y script de generación rápida.
- [ ] Preparar guion de demo (15 minutos) y capturas/recording.

## 8) Tareas menores / limpieza

- [ ] Añadir `.env` a `.gitignore` y dejar `.env.example` en repo.
- [ ] Revisar dependencias en `requirements.txt` y fijar versiones.
- [ ] Ejecutar `black`/`flake8` o formateador elegido y documentar estilo.

---

Archivo generado automáticamente por el asistente. Si quieres, puedo crear PRs con los cambios mínimos para arrancar (por ejemplo: `.env.example`, workflow CI básico, o `swagger.json`).
