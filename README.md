# Wrestling Pipeline

Instrucciones rápidas para levantar el stack localmente (Rol B - API + Docker).

Prerequisitos:

- Docker y docker-compose instalados
- Copiar el archivo de variables de entorno: crea `.env` en la carpeta `wrestling-pipeline/` con las variables mostradas abajo

Ejemplo mínimo de `.env`:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling

Levantar docker (Solo para terminal):

```Shell
sudo systemctl start docker
sudo systemctl enable docker
```

Levantar servicios:

```bash
cd wrestling-pipeline
docker compose -f docker/docker-compose.yml up --build
```

Orquestación oficial (recomendada): usar el script `scripts/run_local.sh` desde `wrestling-pipeline/`.
Este script realiza:

- `docker compose build` y `docker compose up -d`
- Ejecuta la secuencia ETL dentro del contenedor `etl-runner` (TheSportsDB, Kaggle extractor, normalize)
- Espera la salud de la API y abre el dashboard

Ejecutar orquestación completa:

```bash
cd wrestling-pipeline
./scripts/run_local.sh
```

Requisitos y notas:

- Asegúrate de tener `Docker` y `docker-compose` instalados.
- Crea un `.env` en `wrestling-pipeline/` con las variables (ej. `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
- Para usar tu propia API key de TheSportsDB, añade `THESPORTSDB_API_KEY` en `.env` (si no se provee, usa la clave pública por defecto `3`).
- Para usar tu propia API key de TheSportsDB, añade `THESPORTSDB_API_KEY` en `.env` (si no se provee, usa la clave pública por defecto `3`).
  Ejemplo (archivo `wrestling-pipeline/.env`):

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
THESPORTSDB_API_KEY=3
```

- Los datos procesados se montan en `wrestling-pipeline/data` y son compartidos entre ETL, API y dashboard.

Probar API:

- Abrir http://localhost:8000/wrestlers
- Abrir http://localhost:8000/titles

Notas:

- El servicio `etl-runner` está configurado con `restart: 'no'` para correr una vez y terminar.
- Si necesitas ver logs del ETL: `docker compose -f docker/docker-compose.yml logs etl-runner`.

### Credenciales de Administrador:

Para activar el modo administrador en la interfaz web, introduce la siguiente contraseña en cualquiera de los buscadores de luchadores:
`K#9vLp$2mQx@7nRf!4Zd`
