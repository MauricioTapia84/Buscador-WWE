@echo off
echo ===============================================
echo 🏗️ Construyendo imagenes de Docker (Windows)...
echo ===============================================
docker compose build --no-cache
echo.
echo ✅ Compilacion finalizada exitosamente.
echo 👉 Ahora puedes ejecutar scripts\run.bat para iniciar el proyecto.
pause
