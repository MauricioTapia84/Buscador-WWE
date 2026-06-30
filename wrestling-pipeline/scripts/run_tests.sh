#!/bin/bash
set -e

echo "==============================================="
echo "🧪 Ejecutando Pruebas Unitarias..."
echo "==============================================="
docker compose run --rm etl-runner pytest

echo ""
echo "✅ ¡Pruebas finalizadas!"
