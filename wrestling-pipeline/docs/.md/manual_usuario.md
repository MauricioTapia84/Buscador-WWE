# Manual de Usuario

## Contenido
- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Paso 1: Ejecutar el pipeline ETL](#paso-1-ejecutar-el-pipeline-etl)
- [Paso 2: Revisar artefactos generados](#paso-2-revisar-artefactos-generados)
- [Paso 3: Consultar la API](#paso-3-consultar-la-api)
- [Paso 4: Usar el dashboard](#paso-4-usar-el-dashboard)
- [Solución de problemas](#solución-de-problemas)
- [Comandos útiles](#comandos-útiles)

## Introducción
Este documento describe cómo usar el proyecto Wrestling Pipeline desde la ejecución del ETL hasta la consulta del dashboard.

## Requisitos
- Docker instalado.
- Docker Compose instalado.
- Repositorio clonado y abierto en `wrestling-pipeline/`.
- Opcional: `THESPORTSDB_API_KEY` para obtener datos reales desde TheSportsDB.

## Paso 1: Ejecutar el pipeline ETL
1. Abre una terminal en `wrestling-pipeline/`.
2. Ejecuta:
   ```bash
   ./scripts/docker_compose_up.sh
   ```
3. El script construye servicios, levanta la base de datos y ejecuta el ETL.
4. Al terminar, valida el estado del contenedor `etl-runner` y la salud de la API.

## Paso 2: Revisar artefactos generados
Los datos procesados se generan en `wrestling-pipeline/data/processed`.

Archivos esperados:
- `wrestlers.csv`
- `titles.csv`
- `matches.csv`

Si no se generan, revisa los logs del contenedor `etl-runner` y el estado de los servicios con `docker compose ps`.

## Paso 3: Consultar la API
La API expone los datos consolidados del ETL.

Endpoints principales:
- `GET /wrestlers`
- `GET /titles`
- `GET /matches`
- `GET /search?q=<term>`

Ejemplo rápido:
```bash
curl http://localhost:8000/wrestlers
```

## Paso 4: Usar el dashboard
El dashboard consume datos reales desde la API.

Perfiles disponibles:
- Fanático
- Periodista
- Desarrollador / Analista

Recomendación:
1. Accede al dashboard en el navegador.
2. Selecciona un perfil.
3. Navega por los reportes y tarjetas de datos.

## Solución de problemas
- Si la API no responde, espera unos segundos y vuelve a intentar.
- Si el ETL falla, revisa:
  - `docker compose -f docker/docker-compose.yml logs etl-runner`
  - `docker compose ps`
- Comprueba que `data/processed` tenga los CSV generados.

## Comandos útiles
- Ejecutar tests: `./scripts/run_tests.sh`
- Ver logs del ETL: `docker compose -f docker/docker-compose.yml logs etl-runner`
- Revisar servicios: `docker compose -f docker/docker-compose.yml ps`
