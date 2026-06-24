#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
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

# Show status
echo "Services status:"
docker compose -f "$COMPOSE_FILE" ps

# Tail logs for api and etl-runner
echo "Showing last 200 lines of logs for api and etl-runner"
docker compose -f "$COMPOSE_FILE" logs --tail 200 api etl-runner || true

echo "Done. Use 'docker compose -f $COMPOSE_FILE logs -f <service>' to follow logs." 
