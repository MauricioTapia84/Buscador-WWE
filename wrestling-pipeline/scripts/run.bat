@echo off
echo ===============================================
echo 🧹 Limpiando red y contenedores zombies...
echo ===============================================
docker compose down --remove-orphans

echo ===============================================
echo 🚀 Levantando Base de Datos (PostgreSQL)...
echo ===============================================
docker compose up -d db

echo ⏳ Esperando unos segundos a que la BD inicie...
timeout /t 5 /nobreak > nul

echo.
echo ===============================================
echo 🛠️ Ejecutando Pipeline ETL...
echo ===============================================
docker compose run --rm etl-runner python etl/main.py

echo.
echo ===============================================
echo 🧠 Entrenando Modelo de Machine Learning...
echo ===============================================
docker compose run --rm etl-runner python models/train.py

echo.
echo ===============================================
echo 🌐 Levantando API y Dashboard...
echo ===============================================
docker compose up -d api dashboard

echo.
echo ✅ ¡Sistema ejecutandose exitosamente!
echo 👉 Dashboard: http://localhost:8501
echo 👉 API Docs: http://localhost:8000/docs
echo Para detener los servicios usa: docker compose down
pause
