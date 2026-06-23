#!/usr/bin/env bash
set -euo pipefail

# Build and run services with docker-compose, wait for health endpoints and open dashboard
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
cd "$ROOT_DIR"

echo "Building and starting services..."
# Ensure clean network and containers before starting
echo "Stopping any existing compose services and removing network..."
DOCKER_COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.yml"
# Use consistent project name to reuse existing containers
PROJECT_NAME="wrestling-pipeline"
docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" down || true
docker network rm wrestling-pipeline_default 2>/dev/null || true

echo "Building and starting services..."
docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" build
docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" up -d

# Check if ports are free (8000 API, 8501 Dashboard)
for PORT in 8000 8501; do
  if ss -ltn | awk '{print $4}' | grep -E ":${PORT}$" >/dev/null 2>&1; then
    echo "Warning: port ${PORT} appears in use. This may cause docker to fail binding."
  fi
done

# Ensure data folder exists and has permissive permissions for containers
DATA_DIR="$ROOT_DIR/data"
mkdir -p "$DATA_DIR"
chmod 0775 "$DATA_DIR"
chown $(id -u):$(id -g) "$DATA_DIR" || true

echo "Running ETL extractors inside existing etl-runner container..."
# Run ETL: prefer exec into the running etl-runner service to keep single compose project
ETL_CMD="python -u /app/run_etl.py --verbose"
if docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" ps | grep etl-runner | grep Up >/dev/null 2>&1; then
  docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" exec -T etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"
else
  echo "etl-runner not running; starting the service and retrying"
  docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" up -d etl-runner || true
  # give it a moment to start
  sleep 2
  docker-compose -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" exec -T etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"
fi

echo "Waiting for API to be healthy..."
# Try known health paths: /health and /api/health
if ./scripts/wait-for.sh http://localhost:8000/health 15; then
  true
elif ./scripts/wait-for.sh http://localhost:8000/api/health 45; then
  true
else
  echo "Warning: API health check failed at both /health and /api/health"
fi

echo "Attempting to open dashboard (if available at localhost:8050)..."
if curl -fsS http://localhost:8050/ >/dev/null 2>&1; then
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

echo "Services started. Use 'docker-compose logs -f' to follow logs."
