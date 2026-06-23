# Wrestling Pipeline

Instrucciones rápidas para levantar el stack localmente (Rol B - API + Docker).

Prerequisitos:
- Docker y docker-compose instalados
- Copiar el archivo de variables de entorno: crea `.env` en la carpeta `wrestling-pipeline/` con las variables mostradas abajo

Ejemplo mínimo de `.env`:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling

Levantar servicios:

```bash
cd wrestling-pipeline
docker compose -f docker/docker-compose.yml up --build
```

Probar API:

- Abrir http://localhost:8000/wrestlers
- Abrir http://localhost:8000/titles

Notas:
- El servicio `etl-runner` está configurado con `restart: 'no'` para correr una vez y terminar.
- Si necesitas ver logs del ETL: `docker compose -f docker/docker-compose.yml logs etl-runner`.

### Credenciales de Administrador:
Para activar el modo administrador en la interfaz web, introduce la siguiente contraseña en cualquiera de los buscadores de luchadores:
`K#9vLp$2mQx@7nRf!4Zd`
