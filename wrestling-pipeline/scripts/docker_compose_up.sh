#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
PROJECT_NAME="wrestling-pipeline"
COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.yml"
ENV_FILE="$ROOT_DIR/.env"

echo "Root: $ROOT_DIR"

# Ensure .env exists
if [ ! -f "$ENV_FILE" ]; then
  echo ".env not found in $ROOT_DIR — creating with default values (change them as needed)."
  cat > "$ENV_FILE" <<EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
EOF
  echo "Created $ENV_FILE"
fi

# Check for optional dashboard requirements file
DASH_REQ="$ROOT_DIR/dashboards/requirements.txt"
if [ ! -f "$DASH_REQ" ]; then
  echo "Warning: dashboard requirements not found at $DASH_REQ. The dashboard build may fail."
fi

# Run docker compose build and up
echo "Running: docker compose -f $COMPOSE_FILE up --build -d"
docker compose -f "$COMPOSE_FILE" up --build -d

# Check etl-runner status after startup
echo "Inspecting etl-runner container status..."
ETL_CONTAINER=$(docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" ps -q etl-runner || true)
if [ -n "$ETL_CONTAINER" ]; then
  for i in $(seq 1 10); do
    STATUS=$(docker inspect -f '{{.State.Status}}' "$ETL_CONTAINER")
    if [ "$STATUS" = "running" ] || [ "$STATUS" = "exited" ]; then
      break
    fi
    sleep 1
  done
  STATUS=$(docker inspect -f '{{.State.Status}}' "$ETL_CONTAINER")
  EXIT_CODE=$(docker inspect -f '{{.State.ExitCode}}' "$ETL_CONTAINER")
  if [ "$STATUS" = "running" ]; then
    echo "ETL container is still running. Monitor logs for progress."
  elif [ "$STATUS" = "exited" ]; then
    if [ "$EXIT_CODE" -eq 0 ]; then
      echo "ETL container exited successfully (code 0)."
    else
      echo "ETL container exited with error code $EXIT_CODE. Showing last logs..."
      docker compose -f "$COMPOSE_FILE" logs --tail 100 etl-runner || true
    fi
  else
    echo "ETL container status: $STATUS (exit code: $EXIT_CODE)."
  fi
else
  echo "Warning: could not find etl-runner container id."
fi

# Show status
echo "Services status:"
docker compose -f "$COMPOSE_FILE" ps

# Health check for API
API_HEALTH_OK=0
if "$ROOT_DIR/scripts/wait-for.sh" http://localhost:8000/health 15 >/dev/null 2>&1; then
  API_HEALTH_OK=1
elif "$ROOT_DIR/scripts/wait-for.sh" http://localhost:8000/api/health 30 >/dev/null 2>&1; then
  API_HEALTH_OK=1
fi
if [ $API_HEALTH_OK -eq 1 ]; then
  echo "API health check passed."
else
  echo "Warning: API health check failed at both /health and /api/health."
fi

# Tail logs for api and etl-runner
echo "Showing last 200 lines of logs for api and etl-runner"
docker compose -f "$COMPOSE_FILE" logs --tail 200 api etl-runner || true

echo "Done. Use 'docker compose -f $COMPOSE_FILE logs -f <service>' to follow logs." 
