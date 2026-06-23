#!/usr/bin/env bash
set -euo pipefail

# Build and run services with docker-compose, wait for health endpoints and open dashboard
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Building and starting services..."
# Ensure clean network and containers before starting
echo "Stopping any existing compose services and removing network..."
docker-compose down || true
docker network rm wrestling-pipeline_default 2>/dev/null || true

echo "Building and starting services..."
docker-compose build
docker-compose up -d

echo "Running ETL extractors inside etl-runner container..."
# Run the ETL sequence inside the etl-runner container: thesportsdb, kaggle, normalize
ETL_CMD="python -u /app/extract_thesportsdb.py && python -u /app/extract_kaggle.py && python -u /app/normalize.py"
docker-compose run --rm etl-runner bash -lc "$ETL_CMD" || echo "ETL extractor failed (see logs)"

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
    xdg-open http://localhost:8050 || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser http://localhost:8050 || true
  else
    echo "Dashboard URL: http://localhost:8050"
  fi
else
  echo "Dashboard not reachable at http://localhost:8050 — it may not be included in docker-compose."
fi

echo "Services started. Use 'docker-compose logs -f' to follow logs."
