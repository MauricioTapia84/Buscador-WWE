# Wrestling Data Explorer

Proyecto de análisis de lucha libre profesional construido sobre un pipeline ETL, una API en FastAPI, un dashboard en Streamlit y un modelo de machine learning orientado a **clasificación histórica comparativa**.

## Estado actual del proyecto

Hoy el proyecto hace esto:

- extrae, limpia y unifica datos de luchadores, campeonatos y combates,
- expone esos datos mediante una API local,
- los visualiza en un dashboard con perfiles de usuario,
- calcula un **score histórico de perfil campeón** usando machine learning.

Importante:

- el modelo **no predice el próximo campeón de WWE**,
- el modelo **no hace una predicción futura real**,
- el modelo compara el perfil histórico agregado de un luchador con patrones de campeones históricos del dataset.

## Arquitectura

El proyecto vive principalmente dentro de `wrestling-pipeline/`.

Componentes principales:

- `etl/`: extracción, limpieza, unificación y generación del dataset procesado.
- `api/`: API FastAPI que expone luchadores, títulos, combates, salud del servicio y score histórico.
- `dashboards/`: dashboard Streamlit con perfiles `Fanático`, `Periodista` y `Desarrollador / Analista`.
- `models/`: entrenamiento, evaluación y artefactos del modelo.
- `data/processed/`: CSV y artefactos procesados consumidos por la API y el dashboard.

## Modelo de machine learning

El modelo actual:

- algoritmo: `LogisticRegression`
- variables: `total_wins`, `total_losses`, `total_matches`, `win_rate`
- objetivo: clasificar si un perfil se parece al grupo histórico con campeonato visible

Métricas disponibles en `wrestling-pipeline/models/evaluation_report.json`:

- `accuracy`: `0.946`
- `f1_score`: `0.544`
- `roc_auc`: `0.953`

Documento explicativo simple del modelo:

- [modelo_historico_explicado.md](modelo_historico_explicado.md)

## Dashboard

La aplicación tiene tres perfiles:

- `Fanático`: ficha visual del luchador, biografía y rendimiento visible en la base.
- `Periodista`: resumen histórico del luchador, cronología editorial y datos de reinados.
- `Desarrollador / Analista`: comparativas físicas, distribuciones, score histórico y vistas más técnicas.

Acceso al modo analista:

- ingresa la clave `K#9vLp$2mQx@7nRf!4Zd` en el buscador del dashboard.

## Requisitos

- Docker
- Docker Compose

Opcional:

- una API key válida para TheSportsDB si quieres refrescar extracción externa real

## Configuración

Archivo base:

- `wrestling-pipeline/.env`

Ejemplo mínimo:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
THESPORTSDB_API_KEY=3
```

## Formas de levantar el proyecto

### Opción rápida: usar datos ya procesados

Levanta API, dashboard y base de datos usando los artefactos que ya existen en `data/processed`:

```bash
docker compose -f wrestling-pipeline/docker-compose.yml up -d --build api dashboard db
```

Accesos:

- dashboard: `http://localhost:8501`
- API docs: `http://localhost:8000/docs`
- health: `http://localhost:8000/health`

### Opción completa: refrescar ETL, entrenar modelo y levantar todo

```bash
cd wrestling-pipeline
./scripts/run.sh
```

Ese script hace:

1. baja contenedores previos,
2. levanta PostgreSQL,
3. ejecuta el ETL,
4. entrena el modelo,
5. levanta API y dashboard.

### Comandos manuales equivalentes

Desde `wrestling-pipeline/`:

```bash
docker compose up -d db
docker compose run --rm etl-runner python etl/main.py
docker compose run --rm etl-runner python models/train.py
docker compose up -d api dashboard
```

## Endpoints principales

La API actual expone:

- `GET /health`
- `GET /wrestlers`
- `GET /wrestlers/{wrestler_id}`
- `GET /titles`
- `GET /titles/{title_id}`
- `GET /matches`
- `GET /search?q=<texto>`
- `GET /stats`
- `POST /predict`

Notas importantes:

- `/stats` entrega el dataset histórico consolidado que se usa como referencia factual.
- `/predict` devuelve el score histórico calculado por el modelo.
- ese score debe leerse como **afinidad histórica con perfiles campeones**, no como pronóstico real del futuro.

## Artefactos esperados

Outputs relevantes dentro de `wrestling-pipeline/data/processed`:

- `wrestlers.csv`
- `titles.csv`
- `matches.csv`
- `wrestling_clean.csv`

Artefactos del modelo:

- `wrestling-pipeline/models/champion_predictor.pkl`
- `wrestling-pipeline/models/evaluation_report.json`

## Tests

Desde `wrestling-pipeline/`:

```bash
./scripts/run_tests.sh
```

## Logs y mantenimiento

Ver estado de servicios:

```bash
docker compose -f wrestling-pipeline/docker-compose.yml ps
```

Ver logs del dashboard:

```bash
docker compose -f wrestling-pipeline/docker-compose.yml logs -f dashboard
```

Ver logs de la API:

```bash
docker compose -f wrestling-pipeline/docker-compose.yml logs -f api
```

Detener stack:

```bash
docker compose -f wrestling-pipeline/docker-compose.yml down
```

## Limitaciones conocidas

- el dataset es histórico, por lo que puede incluir luchadores retirados, fallecidos o no vigentes,
- el modelo no considera actualidad, storylines, popularidad ni contexto reciente,
- el score histórico puede saturarse en casos extremos como John Cena o The Undertaker,
- la coincidencia entre fuentes puede dejar algunos reinados o relaciones incompletas aunque el perfil competitivo sí exista.

## Documentación adicional

- [manual_usuario.md](wrestling-pipeline/docs/.md/manual_usuario.md)
- [documentacion_tecnica.md](wrestling-pipeline/docs/.md/documentacion_tecnica.md)
- [api_documentation.md](wrestling-pipeline/docs/.md/api_documentation.md)
- [ARCHITECTURE.md](wrestling-pipeline/docs/.md/ARCHITECTURE.md)
- [diagrama_arquitectura.md](wrestling-pipeline/docs/diagrama_arquitectura.md)
