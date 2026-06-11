#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR"

# Create venv if missing
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# Activate
# shellcheck source=/dev/null
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest requests

echo "==> Running API test suite"

# Run tests and capture exit code
python -m pytest -q
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "\n✅ All tests passed (exit code: $EXIT_CODE)."
else
  echo "\n❌ Some tests failed (exit code: $EXIT_CODE)."
  echo "To inspect failures run: python -m pytest -q -k "" or view the detailed output above."
fi

exit $EXIT_CODE
