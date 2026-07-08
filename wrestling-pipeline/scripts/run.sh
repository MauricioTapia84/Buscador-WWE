#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==============================================="
echo "🧹 Limpiando red y contenedores zombies previos..."
echo "==============================================="
docker compose down --remove-orphans

echo "==============================================="
echo "🚀 Levantando Base de Datos (PostgreSQL)..."
echo "==============================================="
docker compose up -d db

echo "⏳ Esperando 5 segundos a que la base de datos inicie correctamente..."
sleep 5

echo ""
echo "==============================================="
echo "🛠️  Ejecutando Pipeline ETL (Extracción y Limpieza)..."
echo "==============================================="
docker compose run --rm etl-runner python etl/main.py

echo ""
echo "==============================================="
echo "🧠 Entrenando Modelo de Machine Learning..."
echo "==============================================="
docker compose run --rm etl-runner python models/train.py

echo ""
echo "==============================================="
echo "🌐 Levantando API y Dashboard..."
echo "==============================================="
docker compose up -d api dashboard

echo ""
echo "✅ ¡Sistema ejecutándose exitosamente!"
echo "👉 Revisa el Dashboard en: http://localhost:8501"
echo "👉 Documentación de la API en: http://localhost:8000/docs"
echo "Para detener los servicios usa: docker compose down"
