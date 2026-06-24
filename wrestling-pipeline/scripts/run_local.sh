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

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  COMPOSE_CMD=(docker compose)
fi

"${COMPOSE_CMD[@]}" -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" down || true
docker network rm wrestling-pipeline_default 2>/dev/null || true

echo "Building and starting services..."
"${COMPOSE_CMD[@]}" -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" build
"${COMPOSE_CMD[@]}" -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" up -d

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
# Run ETL as a one-shot container. The service is designed to exit after finishing.
ETL_CMD="python -u /app/run_etl.py --verbose"
"${COMPOSE_CMD[@]}" -p "$PROJECT_NAME" -f "$DOCKER_COMPOSE_FILE" run --rm etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"

echo "Waiting for API to be healthy..."
# Try known health paths: /health and /api/health
if ./scripts/wait-for.sh http://localhost:8000/health 15; then
  true
elif ./scripts/wait-for.sh http://localhost:8000/api/health 45; then
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

echo "Services started. Use '${COMPOSE_CMD[*]} -p $PROJECT_NAME -f $DOCKER_COMPOSE_FILE logs -f' to follow logs."
