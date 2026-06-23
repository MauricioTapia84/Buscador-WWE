# Ejecutar tests dentro de Docker — Instrucciones rápidas

Objetivo: proporcionar pasos reproducibles para ejecutar la suite de tests del subproyecto `wrestling-pipeline` dentro de un contenedor Docker aislado, y diagnosticar/mitigar errores comunes de red (por ejemplo: "Network ... needs to be recreated").

Ubicaciones relevantes:
- Script de tests: `wrestling-pipeline/scripts/run_tests.sh`
- Compose de tests: `wrestling-pipeline/docker/docker-compose.test.yml`

Pasos recomendados (no destructivos):

1) Ejecutar desde el repo (no requiere privilegios mayores):
```bash
cd wrestling-pipeline/scripts
./run_tests.sh
```

2) Si aparece error de red tipo "needs to be recreated" o "option ... has changed":
- Inspecciona redes de test existentes:
  ```bash
  docker network ls | grep wrestling_pipeline_test || true
  ```
- Inspecciona la red problemática (reemplaza NAME):
  ```bash
  docker network inspect NAME
  docker ps --filter network=NAME --format 'table {{.ID}}\t{{.Names}}\t{{.Image}}'
  ```

3) Limpieza segura (si confirmas que los contenedores listados son temporales de tests):
```bash
# Detener y eliminar contenedores temporales (reemplaza IDs/nombres según tu salida)
docker stop <id-or-name> && docker rm <id-or-name>
# Eliminar las redes huérfanas
docker network rm NAME
``` 
Si no estás seguro, NO elimines contenedores que pertenezcan a proyectos en producción.

4) Alternativa no destructiva (script actualizado):
- El script `run_tests.sh` ya crea un proyecto de compose con nombre único `wrestling_pipeline_test_<timestamp>` y usa un `docker-compose.test.yml` que NO mapea el puerto Postgres al host. Esto evita la mayoría de conflictos de puertos.

5) Reinicio si persiste el problema:
- Reiniciar el demonio Docker suele resolver metadatos de red corruptos:
  ```bash
  sudo systemctl restart docker
  # o reinicia Docker Desktop desde su UI
  ```

6) Mitigación adicional (opcional): forzar red manual y usar `docker run`:
- Si quieres evitar por completo las redes creadas por Compose, crea una red aleatoria y pásala a `docker-compose` mediante la variable `COMPOSE_PROJECT_NAME` o ejecuta `docker run --network <network>` para correr contenedores de tests con `pytest`.

Notas para agentes AI:
- Antes de borrar cualquier recurso, verifica la propiedad del contenedor (labels: `com.docker.compose.project`) y confirma con el usuario.
- Prefiere soluciones que no requieran reinicios manuales del host cuando sea posible.

Fin.
