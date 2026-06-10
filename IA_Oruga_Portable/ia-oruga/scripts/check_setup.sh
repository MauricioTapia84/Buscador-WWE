#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Comprobando entorno virtual..."
if [ -f "$ROOT/venv/bin/activate" ] || [ -f "$ROOT/../venv/bin/activate" ]; then
    echo "-> venv presente"
else
    echo "-> venv NO encontrado"
    exit 2
fi

echo "Comprobando instalación editable del backend..."
# Preferir el python del venv si existe
if [ -f "$ROOT/venv/bin/python" ]; then
    PYTHON="$ROOT/venv/bin/python"
elif [ -f "$ROOT/../venv/bin/python" ]; then
    PYTHON="$ROOT/../venv/bin/python"
else
    PYTHON="python"
fi

"$PYTHON" - <<PY
import importlib,sys
try:
    importlib.import_module('study_system')
    print('-> backend importable (study_system)')
except Exception as e:
    print('-> backend NO importable:', e)
    sys.exit(3)
PY

echo "Comprobaciones completadas OK."
