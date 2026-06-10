@echo off
REM Comprobaciones post-setup para Windows
echo Comprobando venv...
if exist "%~dp0\..\venv\Scripts\activate.bat" (
  echo -> venv presente
) else (
  echo -> venv NO encontrado
  exit /b 2
)

echo Comprobando import de backend (study_system)...
python - <<PY
import importlib,sys
try:
    importlib.import_module('study_system')
    print('-> backend importable (study_system)')
except Exception as e:
    print('-> backend NO importable:', e)
    sys.exit(3)
PY

echo Comprobaciones completadas OK.
