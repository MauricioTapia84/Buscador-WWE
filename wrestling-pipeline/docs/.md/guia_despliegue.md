# Guía de despliegue

## Contenido
- [Prerequisitos](#prerequisitos)
- [Configuración](#configuración)
- [Despliegue local](#despliegue-local)
- [Verificación](#verificación)
- [Archivos generados](#archivos-generados)
- [Pruebas](#pruebas)

## Prerequisitos
- Docker instalado.
- Docker Compose instalado.
- Repositorio clonado y accesible en `wrestling-pipeline/`.
- Opcional: variable de entorno `THESPORTSDB_API_KEY` para datos reales.

## Configuración
Crea un archivo `.env` en `wrestling-pipeline/` con:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
THESPORTSDB_API_KEY=tu_api_key_aqui
```

## Despliegue local
Desde `wrestling-pipeline/` ejecuta el script principal:

```bash
./scripts/docker_compose_up.sh
```

El script realiza:
- construcción de imágenes Docker
- levantado de `db`, `api`, `dashboard` y `etl-runner`
- ejecución del pipeline ETL
- validación de la salud de la API

Si necesitas levantar solo el stack sin el ETL automático, usa:

```bash
docker compose -f docker/docker-compose.yml up --build
```

## Verificación
Comprueba los servicios activos:

```bash
docker compose -f docker/docker-compose.yml ps
```

Comprueba la salud de la API:

```bash
curl http://localhost:8000/health
```

## Archivos generados
Los resultados del pipeline se encuentran en:
- `wrestling-pipeline/data/processed/wrestlers.csv`
- `wrestling-pipeline/data/processed/titles.csv`
- `wrestling-pipeline/data/processed/matches.csv`

Revisa también los logs del ETL con:

```bash
docker compose -f docker/docker-compose.yml logs etl-runner
```

## Pruebas
Ejecuta el suite de tests con:

```bash
./scripts/run_tests.sh
```

O bien directamente con pytest:

```bash
python3 -m pytest -v tests
```
