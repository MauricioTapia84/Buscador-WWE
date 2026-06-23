# Arquitectura y Manual Técnico — Wrestling Pipeline

Este documento describe la arquitectura del proyecto *Buscador-WWE* (carpeta `wrestling-pipeline`), detalla los flujos de datos desde la extracción al dashboard, los archivos intermedios, los requisitos que deben cumplirse y cómo ejecutar/desplegar la aplicación localmente y en CI.

## Resumen general

- Propósito: normalizar/centralizar datos de lucha libre (TheSportsDB, Wikipedia, Kaggle) y exponerlos mediante una API y un dashboard para consumidores (UI, dashboards, integraciones).
- Componentes principales:
  - ETL (`wrestling-pipeline/etl`): extractores, transformaciones, normalización y escritor de artefactos (CSV/Parquet + metadatos).
  - API (`wrestling-pipeline/api`): FastAPI que sirve los CSV producidos y proporciona endpoints para `wrestlers`, `matches`, `titles` y `search`.
  - Dashboard (`wrestling-pipeline/dashboards`): aplicación front (Streamlit / Dash) que consume la API o archivos procesados para presentar la información.
  - Orquestación/Contenedores: `wrestling-pipeline/docker/docker-compose.yml`, `scripts/run_local.sh` y `scripts/run_tests.sh` para ejecutar todo en Docker.

## Requisitos que deben cumplirse

1. Extracciones correctas:
   - Cada extractor debe devolver datos con columnas mínimas esperadas (por ejemplo, para `wrestlers`: `id`/`name`/`image_url`/`bio` donde aplique).
   - Las llamadas HTTP deben usar caching local en `etl/cache/` para evitar sobrecarga y permitir pruebas deterministas.
   - Las credenciales/apikeys (ej. `THESPORTSDB_API_KEY`) deben estar definidas en el entorno o en `wrestling-pipeline/.env` (no versionar secrets).

2. Normalización y calidad:
   - Fechas deben parsearse con `pd.to_datetime(..., errors='coerce')` y validarse; si fallan, registrarlas en metadata.
   - Dedupe de `wrestlers` controlado por `WRESTLER_DEDUPE_SCORE` (variable de entorno), con registro de merges realizados en `wrestlers_metadata.json`.
   - Filtrado de matchs sin competidores y verificación de columnas obligatorias antes de publicar.

3. Artefactos de salida:
   - Carpeta común compartida: `wrestling-pipeline/data` (montada en contenedores como `/app/data`).
   - ETL produce en `data/processed` al menos:
     - `wrestlers.csv` y `wrestlers.parquet` (+ `wrestlers_metadata.json`)
     - `matches.csv` o `matches_normalized.csv` y `matches.parquet` (+ `matches_metadata.json`)
     - `titles_extracted.csv` si aplica
   - Los archivos deben incluir esquemas simples (nombres de columnas con tipos compatibles con pandas/JSON).

4. API y Dashboard:
   - La API lee los CSV en `/app/data/processed` y expone endpoints:
     - `GET /wrestlers` (opcional `source` query param)
     - `GET /matches`
     - `GET /titles`
     - `GET /search?q=...`
     - `GET /health`
   - El Dashboard puede consumir directamente la API (recomendado) o leer los archivos montados.

5. Tests y CI:
   - Todos los tests unitarios del ETL y mocking de endpoints externos deben ejecutarse en contenedores en CI.
   - Scripts obligatorios para orquestación local:
     - `scripts/run_local.sh` + `scripts/run_local.ps1` para lanzar servicios y ejecutar ETL.
     - `scripts/run_tests.sh` + `scripts/run_tests.ps1` para ejecutar los tests (preferiblemente dentro de Docker usando `docker/docker-compose.test.yml`).
   - CI workflow incluido: `/.github/workflows/etl-run-and-upload.yml` que construye la imagen ETL, ejecuta el ETL y sube `etl-output` como artifact.

## Flujo de datos — paso a paso

1. Extracción (ETL extracts):
   - Extractores en `wrestling-pipeline/etl`:
     - `extract_thesportsdb.py`: consulta TheSportsDB (usar `THESPORTSDB_API_KEY`), guarda respuestas y construye `wrestlers_thesportsdb.csv` en `data/processed` o cache.
     - `extract_wikipedia.py` / `extract_kaggle.py`: obtienen datos de Wikipedia/Kaggle y generan `wrestlers_enriched.csv`, `matches_normalized.csv`, etc.
   - Archivos intermedios (raw) pueden guardarse en `data/raw` y cache de respuestas en `etl/cache`.

2. Transformación y normalización:
   - Script `normalize.py` toma `wrestlers_thesportsdb.csv`, `wrestlers_enriched.csv` y otras fuentes y:
     - Une fuentes, aplica dedupe (rapidfuzz), genera `wrestlers.csv` y `wrestlers.parquet`.
     - Normaliza fechas y campos en `matches_normalized.csv` -> `matches.csv`/`.parquet`.
     - Genera metadata JSON con `generated_at`, filas antes/después, merges realizados y `score_cutoff`.

3. Almacenamiento final:
   - Carpeta compartida `wrestling-pipeline/data/processed` contiene los CSV/Parquet resultantes y los archivos `*_metadata.json`.
   - En contenedor, esa carpeta está en `/app/data/processed`.

4. API y consumo por dashboard:
   - `wrestling-pipeline/api` (FastAPI) implementa lectura segura de CSV (`_read_csv_safe`) y devuelve JSON listo para la UI.
   - El Dashboard (`wrestling-pipeline/dashboards`) carga datos usando la API o leyendo `../data/processed` cuando corre en contenedor.
   - La UI presenta filtros (roles, búsqueda) y se basa en las colas/archivos normalizados.

5. Orquestación y despliegue local:
   - `wrestling-pipeline/docker/docker-compose.yml` define servicios: `db`, `api`, `dashboard`, `etl-runner`.
   - Uso recomendado: ejecutar `wrestling-pipeline/scripts/run_local.sh` que:
     - Construye imágenes, levanta servicios, crea/asegura permisos de `data/` y ejecuta la secuencia ETL dentro de `etl-runner`.
   - Los tests se orquestan mediante `wrestling-pipeline/scripts/run_tests.sh`, que usa `docker/docker-compose.test.yml` para levantar una red aislada y ejecutar pytest dentro del contenedor `etl-runner`.

## Archivos clave (ubicaciones y propósito)

- `wrestling-pipeline/etl/` — Código ETL y utilidades
  - `extract_thesportsdb.py`, `extract_kaggle.py`, `extract_wikipedia.py` — extractores
  - `normalize.py` — normalización, dedupe y escritura final + metadata
  - `run_etl.py` — orquestador ETL (llama a extractores + normalize)
  - `requirements.txt` — dependencias Python del ETL

- `wrestling-pipeline/api/` — API
  - `main.py` — endpoints FastAPI
  - `Dockerfile.api` — imagen para despliegue

- `wrestling-pipeline/dashboards/` — UI del dashboard
  - `app.py`, `pages/` — pantallas y componentes
  - `Dockerfile.dashboard`

- `wrestling-pipeline/docker/` — archivos compose
  - `docker-compose.yml` — orquestador local (dev)
  - `docker-compose.test.yml` — orquestador para tests aislados

- `wrestling-pipeline/data/` — datos persistentes (montaje entre host y contenedores)
  - `raw/` — datos sin procesar (opcional)
  - `processed/` — CSV/Parquet finales y `*_metadata.json`

- `wrestling-pipeline/scripts/` — scripts de conveniencia
  - `run_local.sh` / `run_local.ps1` — build + up + ejecutar ETL + abrir dashboard
  - `run_tests.sh` / `run_tests.ps1` — ejecutar tests (preferible dentro de Docker)
  - `wait-for.sh` — helper para health checks

## Reglas operacionales y checklist previo a despliegue

- Antes de ejecutar `run_local.sh`:
  - Definir `THESPORTSDB_API_KEY` en `wrestling-pipeline/.env` o en el entorno.
  - Verificar que `docker` y `docker-compose` están instalados y que tienes permisos para crear redes/volúmenes.

- Validaciones dentro del ETL (debe ocurrir automáticamente):
  - Cada extractor devuelve archivo con encabezados esperados.
  - `normalize.py` genera metadata JSON y no falla al serializar Parquet (si falla pyarrow, debe seguir generando CSV y metadata).
  - `wrestlers_metadata.json` incluye: `generated_at`, `source_files`, `rows_input`, `unique_before`, `unique_after`, `merges_performed`, `score_cutoff`.
  - `matches_metadata.json` incluye: `generated_at`, `rows`, `rows_before_validation`, `rows_after_validation`.

- Pruebas: todos los tests bajo `wrestling-pipeline/etl/tests` deben ejecutarse y pasar en CI.

## Cómo funciona la aplicación (runtime)

- Despliegue local con `run_local.sh`:
 1. Construye imágenes para `api`, `dashboard`, `etl-runner`.
 2. Levanta `db` (Postgres) y los servicios vinculados.
 3. Ejecuta el ETL dentro de `etl-runner` generando los archivos en `data/processed`.
 4. API lee esos archivos y los sirve en `/wrestlers`, `/matches`.
 5. Dashboard consume la API y presenta la UI.

- Despliegue en CI/CD:
  - Pipeline debe construir la imagen ETL, ejecutar `run_etl.py` en un contenedor y subir los artefactos resultantes (CSV/Parquet/metadata) para su inspección.

## Buenas prácticas y recomendaciones

- Versionar el esquema de salida (por ejemplo `schema:v1`) en los archivos `*_metadata.json` para manejar cambios futuros.
- Mantener los secretos fuera del repo y documentar los secretos necesarios en `README.md` para desarrolladores.
- Añadir pruebas de integración que arranquen `api` y prueben `/wrestlers` y `/matches` usando archivos procesados de ejemplo.
- Registrar logs de ETL con niveles `INFO/DEBUG/ERROR` y capturar métricas (tiempo, filas procesadas) en metadata.

## Comandos útiles

- Levantar todo localmente (Linux/mac):
```
cd wrestling-pipeline
./scripts/run_local.sh
```

- Ejecutar tests orquestados (Linux/mac):
```
cd wrestling-pipeline
./scripts/run_tests.sh
```

- Ejecutar solo el ETL dentro del contenedor (sin levantar todo):
```
cd wrestling-pipeline

docker-compose -f docker/docker-compose.yml run --rm etl-runner bash -lc "python /app/run_etl.py --out /app/data/processed"
```

- Ejecutar API localmente (sin Docker) para desarrollo:
```
pip install -r wrestling-pipeline/api/requirements.txt
uvicorn wrestling-pipeline.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Diagramas y ejemplos

### Diagrama de alto nivel (Mermaid)

```mermaid
flowchart TD
  subgraph ETL
    A[TheSportsDB / Wikipedia / Kaggle] --> B[Extractors (extract_*.py)]
    B --> C[Raw files (data/raw) & cache]
    C --> D[Normalize (normalize.py)]
    D --> E[data/processed (CSV/Parquet) + metadata.json]
  end

  subgraph Infra
    E --> API[FastAPI (/app/data/processed)]
    API --> Dashboard[Dashboard (Streamlit/Dash)]
    DB[(Postgres)]
  end

  ETL --> DB
  API --> DB
```

### Ejemplo de `wrestlers_metadata.json`

```json
{
  "generated_at": "2026-06-23T12:34:56Z",
  "source_files": ["wrestlers_thesportsdb.csv","wrestlers_enriched.csv"],
  "rows_input": 1200,
  "unique_before": 1200,
  "unique_after": 1100,
  "merges_performed": 150,
  "score_cutoff": 88
}
```

### Ejemplo de `matches_metadata.json`

```json
{
  "generated_at": "2026-06-23T12:35:10Z",
  "rows": 3450,
  "rows_before_validation": 3500,
  "rows_after_validation": 3450
}
```

### Ejemplo de CSV (primeras líneas de `wrestlers.csv`)

```csv
id,name,canonical_name,image_url,nationality,date_born
1,John Doe,John Doe,https://...,USA,1985-01-01
2,Jon Doe,John Doe,https://...,USA,1985-01-01
3,Jane Smith,Jane Smith,https://...,CAN,1990-05-10
```

## Contacto y mantenimiento

- Mantener actualizadas dependencias en `wrestling-pipeline/etl/requirements.txt` y en `api`/`dashboards`.
- Añadir tests cuando se modifiquen extractores o el esquema de salida.

---

Este documento es el manual técnico vivo del pipeline. Si quieres, puedo generar una versión HTML o agregar más diagramas detallados por extractor.
