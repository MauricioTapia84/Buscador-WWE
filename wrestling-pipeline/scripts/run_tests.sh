#!/usr/bin/env bash
set -euo pipefail

# Cross-platform helper: installs ETL deps and runs pytest for the pipeline
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Using project root: $ROOT_DIR"

python3 -m pip install --upgrade pip
if [ -f "$ROOT_DIR/wrestling-pipeline/etl/requirements.txt" ]; then
  python3 -m pip install -r "$ROOT_DIR/wrestling-pipeline/etl/requirements.txt"
fi
if [ -f "$ROOT_DIR/requirements.txt" ]; then
  python3 -m pip install -r "$ROOT_DIR/requirements.txt" || true
fi

echo "Running pytest..."
python3 -m pytest -q "$ROOT_DIR/wrestling-pipeline/tests"
