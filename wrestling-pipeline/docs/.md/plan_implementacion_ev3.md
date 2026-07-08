# Plan de implementación para mejorar Wrestling Pipeline

Este plan describe los pasos para convertir `wrestling-pipeline` en un proyecto de ciencia de datos completo con EDA, datos reproducibles y un modelo básico de predicción de campeones.

## Objetivo

Crear un pipeline de datos que use los tres orígenes de datos existentes (TheSportsDB, Wikipedia, Kaggle), provea un flujo ETL ordenado en carpetas internas, genere artefactos en `data/processed` y presente:

- análisis exploratorio de datos (EDA)
- visualizaciones claras en el dashboard
- modelo simple de predicción de campeones

## 1. Reorganización del ETL

### 1.1 Estructura de carpetas

El ETL deberá ordenarse en subpaquetes internos:

- `etl/extractors/`
  - `kaggle.py`
  - `thesportsdb.py`
  - `wikipedia.py`
- `etl/transform/`
  - `clean.py`
  - `normalize.py`
- `etl/load/`
  - `load.py`
- `etl/validate/`
  - `validate.py`
- `etl/utils/`
  - `logging_config.py`
  - `retry_utils.py`
- `etl/__init__.py`
  - Exporta las funciones principales y mantiene compatibilidad con tests existentes.

### 1.2 Flujo ETL organizado

1. `run_etl.py` o `main.py` ejecuta el flujo completo.
2. `extractors/` lee los tres orígenes:
   - `extractors/thesportsdb.py` — extrae datos de TheSportsDB.
   - `extractors/wikipedia.py` — extrae biografías y metadatos de Wikipedia.
   - `extractors/kaggle.py` — lee CSV o SQLite local de Kaggle.
3. `transform/clean.py` normaliza columnas y valores.
4. `transform/normalize.py` unifica fuentes y genera outputs finales.
5. `load/load.py` guarda en SQLite/CSV.
6. `validate/validate.py` crea reportes JSON/CSV/HTML.

## 2. Uso de los tres orígenes de datos

### 2.1 TheSportsDB

- Usar el extractor actual para obtener datos de luchadores por nombre.
- Guardar en `data/raw` y/o `data/processed`:
  - `wrestlers_thesportsdb.csv`
  - `wrestlers_thesportsdb_metadata.json`

### 2.2 Wikipedia

- Extraer descripciones y fechas clave.
- Guardar en `data/raw` y/o `data/processed`:
  - `wikipedia_summary.csv`
  - `wrestlers_enriched.csv`

### 2.3 Kaggle

- Leer los ficheros disponibles en `data/raw`:
  - `wrestlers.csv`
  - `matches.csv`
  - `titles.csv`
- Normalizar los datos de matches y títulos.

## 3. Artefactos finales

El ETL deberá generar al menos:

- `data/processed/wrestlers.csv`
- `data/processed/matches.csv`
- `data/processed/titles_extracted.csv`
- `data/processed/wrestlers.parquet`
- `data/processed/matches.parquet`
- `data/processed/champions.parquet` (si aplica)
- `data/processed/*.json` metadata

## 4. Análisis exploratorio de datos (EDA)

### 4.1 Notebook recomendado

Crear `notebooks/eda_wrestling.ipynb` con:

- Carga de datos desde `data/processed`
- Estadísticas descriptivas:
  - conteo de luchadores, matches, títulos
  - medias y desviaciones de `height_cm`, `weight_kg`, `debut_year`
- Visualizaciones:
  - histograma de altura/peso
  - boxplot por nacionalidad
  - gráfico de títulos por luchador
  - timeline de cantidad de títulos por año
- Insights:
  - mayores campeones
  - tendencias de duración de reinados
  - correlaciones entre experiencia y títulos

### 4.2 Dashboard EDA

Agregar una nueva sección al dashboard con:

- histogramas y gráficos de distribución
- barchart de títulos por luchador
- línea temporal de `won_date`
- cuadro de resumen de métricas clave

## 5. Predicción de campeones

### 5.1 Generación de features

Crear `models/feature_engineering.py` con componentes como:

- `experience_years = current_year - debut_year`
- `title_count` (cantidad de títulos históricos)
- `avg_reign_days`
- `weight_class` categórica
- `win_rate` o `matches_played` si existen datos de combates

### 5.2 Entrenamiento de modelo

Crear `models/train_models.py` que:

- use `scikit-learn`
- entrene un `RandomForestClassifier` o `LogisticRegression`
- genere un output de probabilidades de ser campeón
- guarde el modelo en `models/champion_model.joblib`
- exporte `models/predictions.csv`

### 5.3 Integración en dashboard

Agregar panel de predicción con:

- top 5 luchadores probables campeones
- precisión del modelo
- feature importances

## 6. Documentación y orden

### 6.1 Archivos nuevos en `docs/`

- `docs/plan_implementacion.md` — plan general y etapas.
- `docs/guia_despliegue.md` — pasos para ejecutar y generar datos.
- `docs/manual_usuario.md` — cómo usar el dashboard y qué ver.

### 6.2 Organización final

- `etl/` ordenado en subpaquetes internos
- `models/` para features y entrenamiento
- `notebooks/` para EDA
- `docs/` con plan y despliegue
- `data/raw/` y `data/processed/` separados

## 7. Pasos concretos de implementación

1. Reorganizar `etl/` en subpaquetes internos.
2. Añadir `etl/extractors/*.py`, `etl/transform/*.py`, `etl/load/*.py`, `etl/validate/*.py`, `etl/utils/*.py`.
3. Actualizar `run_etl.py`, `main.py` y tests a la nueva estructura.
4. Añadir `models/feature_engineering.py` y `models/train_models.py`.
5. Crear `notebooks/eda_wrestling.ipynb`.
6. Extender `dashboards/home.py` con EDA y predicción.
7. Documentar el plan y el despliegue en `docs/`.

## 8. Criterios de éxito

- El ETL lee los tres orígenes de datos.
- El pipeline produce datos procesados y metadatos claros.
- El modelo predice campeones con features razonables.
- El dashboard muestra EDA y tendencias.
- La documentación en `docs/` es suficiente para que otro estudiante reproduzca el trabajo.
