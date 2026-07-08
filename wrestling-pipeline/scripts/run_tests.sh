#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==============================================="
echo "🧪 Ejecutando Pruebas Unitarias..."
echo "==============================================="
docker compose run --rm etl-runner pytest

echo ""
echo "✅ ¡Pruebas finalizadas!"
