# Wrestling Pipeline

Este repositorio contiene el proyecto de datos y dashboard de lucha libre basado en un pipeline ETL, una API y un dashboard.

## Documentación disponible

- `wrestling-pipeline/docs/.md/manual_usuario.md`
- `wrestling-pipeline/docs/.md/documentacion_tecnica.md`
- `wrestling-pipeline/docs/.md/api_documentation.md`
- `wrestling-pipeline/docs/.md/guia_despliegue.md`
- `wrestling-pipeline/docs/.md/ARCHITECTURE.md`
- `wrestling-pipeline/docs/.md/informe_final.md`
- `wrestling-pipeline/docs/.md/diagrama_arquitectura.svg`
- `wrestling-pipeline/docs/diagrama_arquitectura.png`

## Requisitos

- Docker
- Docker Compose
- Clonar el repositorio y colocar el proyecto en una carpeta accesible.

## Configuración mínima

Crear el archivo `wrestling-pipeline/.env` con al menos:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
THESPORTSDB_API_KEY=3
```

## Levantar el proyecto

Desde `wrestling-pipeline/`:

```bash
./scripts/run_local.sh
```

Este script realiza:

- construcción de los servicios Docker
- levantado del stack
- ejecución del pipeline ETL dentro del contenedor `etl-runner`
- verificación de salud del API

## Probar la API

- `http://localhost:8000/wrestlers`
- `http://localhost:8000/titles`
- `http://localhost:8000/matches`

## Comprobar los datos procesados

Los outputs esperados se generan en `wrestling-pipeline/data/processed`:

- `wrestlers.csv`
- `titles.csv`
- `matches.csv`

## Ejecutar tests

Desde `wrestling-pipeline/`:

```bash
./scripts/run_tests.sh
```

## Notas

- Si necesitas ver los logs del ETL: `docker compose -f docker/docker-compose.yml logs etl-runner`.
- El dashboard consume datos reales desde la API y no inventa información.

Modo administrador

Para habilitar el perfil de desarrollador / analista, ingresa esta clave en el buscador:

```text
K#9vLp$2mQx@7nRf!4Zd
```
