# Documentación Técnica

## Contenido
- [Visión general](#visión-general)
- [Arquitectura](#arquitectura)
- [ETL](#etl)
- [API](#api)
- [Dashboard](#dashboard)
- [Despliegue](#despliegue)
- [Pruebas](#pruebas)
- [Archivos clave](#archivos-clave)

## Visión general
Wrestling Pipeline es una solución de datos para extraer, normalizar y exponer información de lucha libre. El proyecto comprende un pipeline ETL, una API REST y un dashboard.

## Arquitectura
La arquitectura se divide en tres capas principales:

1. Orígenes de datos
2. Pipeline ETL
3. Consumo por API y dashboard

Los datos se extraen desde TheSportsDB, Wikipedia y fuentes CSV/Kaggle. Luego se normalizan y se escriben en `data/processed`.

## ETL
### Extracción
Los extractores se encuentran en `etl/extractors/`.

Orígenes soportados:
- TheSportsDB
- Wikipedia
- Kaggle / CSV
- Datos históricos del repositorio

### Normalización
La limpieza y normalización se realizan en `etl/transform/`.

Se unifican:
- nombres de columnas
- formatos de fecha
- valores vacíos
- nombres y slugs

### Consolidación
Los archivos finales se escriben en:
- `data/processed/wrestlers.csv`
- `data/processed/titles.csv`
- `data/processed/matches.csv`

### Validación
El proyecto incluye validaciones de datos y reportes de calidad. Los datos se revisan antes y después de la normalización.

## API
La API está implementada en `api/main.py`.

Endpoints principales:
- `GET /wrestlers`
- `GET /titles`
- `GET /matches`
- `GET /wrestlers/{wrestler_id}`
- `GET /titles/{title_id}`
- `GET /search?q=<term>`
- `GET /health`

La API lee CSV procesados desde `/app/data/processed` y devuelve JSON limpio.

## Dashboard
El dashboard consume la API para presentar:
- perfiles de fanáticos
- tarjetas de luchadores
- reportes de títulos
- análisis de combates

## Despliegue
Se recomienda desplegar con Docker Compose usando `docker/docker-compose.yml`.

Servicios:
- `api`
- `dashboard`
- `db`
- `etl-runner`

## Pruebas
Los tests están en `tests/`.

Para ejecutar localmente:
```bash
python3 -m pytest -v tests
```

Para ejecutar con el script:
```bash
./scripts/run_tests.sh
```

## Archivos clave
- `etl/run_etl.py`
- `api/main.py`
- `docker/docker-compose.yml`
- `scripts/docker_compose_up.sh`
- `data/processed/wrestlers.csv`
- `data/processed/titles.csv`
- `data/processed/matches.csv`
