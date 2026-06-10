#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN=$(which python3 || true)
if [ -z "$PYTHON_BIN" ]; then
  echo "python3 not found"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating venv..."
  $PYTHON_BIN -m venv venv
else
  echo "venv already exists"
fi

VENV_PY="$ROOT/venv/bin/python"
echo "Using venv python: $VENV_PY"

# Upgrade pip and basic tools
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

# Install backend requirements if present
if [ -f "backend/requirements_extraction.txt" ]; then
  echo "Installing backend requirements..."
  "$VENV_PY" -m pip install -r backend/requirements_extraction.txt || echo "[WARN] failed to install backend requirements"
fi

# Install backend in editable mode
if [ -d "backend" ]; then
  echo "Installing backend in editable mode..."
  "$VENV_PY" -m pip install -e backend
else
  echo "No backend directory found"
fi

echo "Setup dev completed. Activate with: source venv/bin/activate"
