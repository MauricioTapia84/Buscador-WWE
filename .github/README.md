# Wrestling Pipeline

Guía real para levantar el stack local con Docker, ETL, API y dashboard.

## Prerrequisitos

- Docker instalado
- `docker compose` disponible
  - si además tienes `docker-compose`, el script también lo soporta
- Crear `wrestling-pipeline/.env`

## `.env` mínimo

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
THESPORTSDB_API_KEY=3
```

## Flujo recomendado

```bash
cd wrestling-pipeline
./scripts/run_local.sh
```

Ese script hace esto:

1. baja contenedores anteriores del proyecto,
2. reconstruye imágenes,
3. levanta `db`, `api`, `dashboard` y `etl-runner`,
4. ejecuta el ETL dentro de `etl-runner`,
5. espera la salud de la API,
6. deja el dashboard disponible.

## Levantar manualmente

```bash
cd wrestling-pipeline
docker compose -f docker/docker-compose.yml up --build -d
```

Luego puedes revisar:

```bash
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs api
docker compose -f docker/docker-compose.yml logs dashboard
docker compose -f docker/docker-compose.yml logs etl-runner
```

## URLs correctas

- Dashboard: http://localhost:8501
- API health: http://localhost:8000/health
- API wrestlers: http://localhost:8000/wrestlers
- API titles: http://localhost:8000/titles

## Nota importante de red Docker

Dentro del contenedor de Streamlit, la API no debe consultarse con `http://localhost:8000`.

La URL correcta dentro de Docker es:

```text
http://api:8000
```

Por eso el servicio `dashboard` inyecta:

```env
API_URL=http://api:8000
```

## ETL

- `etl-runner` está configurado con `restart: 'no'`
- su comportamiento esperado es correr una vez y terminar
- no debe quedarse `Up` indefinidamente para que la app funcione

Los datos procesados quedan compartidos en:

- `wrestling-pipeline/data`

## Modo administrador

Para habilitar el perfil de desarrollador / analista, ingresa esta clave en el buscador:

```text
K#9vLp$2mQx@7nRf!4Zd
```
