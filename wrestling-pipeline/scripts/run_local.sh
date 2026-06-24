#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
DOCKER_COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.yml"
PROJECT_NAME="wrestling-pipeline"

if command -v docker compose >/dev/null 2>&1; then
  DC_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
else
  echo "Error: neither docker compose nor docker-compose is installed."
  exit 1
fi

echo "Building and starting services..."
echo "Stopping any existing compose services and removing network..."
$DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" down --remove-orphans || true
docker network rm "${PROJECT_NAME}_default" 2>/dev/null || true

for PORT in 8000 8501; do
  if ss -ltn | awk '{print $4}' | grep -E ":${PORT}$" >/dev/null 2>&1; then
    echo "Error: port ${PORT} is already in use. Stop the process using it before retrying."
    ss -ltn | grep -E ":${PORT}$" || true
    exit 1
  fi
done

echo "Building services..."
$DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" build
$DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" up -d

DATA_DIR="$ROOT_DIR/data"
mkdir -p "$DATA_DIR"
chmod 0775 "$DATA_DIR"
chown "$(id -u):$(id -g)" "$DATA_DIR" || true

echo "Running ETL extractors inside existing etl-runner container..."
ETL_CMD="python -u /app/run_etl.py --verbose"
if $DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" ps | grep etl-runner | grep Up >/dev/null 2>&1; then
  $DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" exec -T etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"
else
  echo "etl-runner not running; starting the service and retrying"
  $DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" up -d etl-runner || true
  sleep 2
  $DC_CMD -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" exec -T etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"
fi

echo "Waiting for API to be healthy..."
if ./scripts/wait-for.sh http://localhost:8000/health 15 || ./scripts/wait-for.sh http://localhost:8000/api/health 45; then
  true
else
  echo "Warning: API health check failed at both /health and /api/health"
fi

echo "Attempting to open dashboard (if available at localhost:8501)..."
if curl -fsS http://localhost:8501/ >/dev/null 2>&1; then
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:8501 || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser http://localhost:8501 || true
  else
    echo "Dashboard URL: http://localhost:8501"
  fi
else
  echo "Dashboard not reachable at http://localhost:8501 — it may not be included in docker-compose."
fi

echo "Services started. Use '$DC_CMD -p \"$PROJECT_NAME\" -f \"$DOCKER_COMPOSE_FILE\" logs -f <service>' to follow logs."
