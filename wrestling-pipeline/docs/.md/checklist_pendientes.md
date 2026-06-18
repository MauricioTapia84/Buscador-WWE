# Checklist de tareas pendientes — WrestlingData Explorer

## Resumen

Checklist generado a partir de la pauta de evaluación y el estado actual del repo.

---

## 1) Pipeline ETL (20%)

- [ ] Añadir logging estructurado en `etl/` (format JSON, niveles).
- [ ] Implementar reintentos y manejo de fallos por etapa (extract/transform/load).
- [ ] Generar reportes de calidad (CSV/HTML) tras cada ejecución.

**Completados (migrados / removidos de la checklist):**

- **Validaciones:** Se consolidaron y mejoraron las validaciones en `etl/validate.py` (Pandera). Archivo: [wrestling-pipeline/etl/validate.py](wrestling-pipeline/etl/validate.py)
- **Pruebas ETL:** Se añadieron tests unitarios para `transform`, `validate` y `load`. Archivo: [wrestling-pipeline/tests/test_etl.py](wrestling-pipeline/tests/test_etl.py)
- **CI ETL:** Se creó workflow para ejecutar tests ETL en GitHub Actions. Archivo: [.github/workflows/etl-ci.yml](.github/workflows/etl-ci.yml)

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
