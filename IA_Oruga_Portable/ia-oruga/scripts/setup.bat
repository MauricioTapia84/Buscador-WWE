@echo off
REM setup.bat - réplica básica de setup.sh para Windows (CMD/PowerShell)
SETLOCAL ENABLEDELAYEDEXPANSION

echo Creando entorno virtual en %%~dp0\..\venv
python -m venv "%~dp0\..\venv"
if ERRORLEVEL 1 (
  echo Error creando el venv. Asegúrate de tener Python instalado y en PATH.
  exit /b 1
)

echo Activando venv y actualizando pip
call "%~dp0\..\venv\Scripts\activate.bat"
python -m pip install --upgrade pip setuptools wheel

echo Instalando dependencias principales
if exist "%~dp0\..\backend\requirements_extraction.txt" (
  pip install -r "%~dp0\..\backend\requirements_extraction.txt"
) else (
  echo No se encontró backend/requirements_extraction.txt, omitiendo.
)

echo Instalando paquete backend en editable (si aplica)
if exist "%~dp0\..\backend\setup.py" (
  pip install -e "%~dp0\..\backend"
) else (
  echo No se encontró setup.py en backend; por favor añade pyproject.toml o setup.py para instalación editable.
)

echo Comprobaciones post-setup...
call "%~dp0\check_setup.bat"

echo Listo.
ENDLOCAL
