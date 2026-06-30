#!/bin/bash
set -e

echo "==============================================="
echo "🏗️  Construyendo imágenes de Docker (Linux/macOS)..."
echo "==============================================="
docker compose build --no-cache

echo ""
echo "✅ Compilación de imágenes finalizada exitosamente."
echo "👉 Ahora puedes ejecutar ./scripts/run.sh para iniciar el proyecto."
