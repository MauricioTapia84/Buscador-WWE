#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OUT="../IA_Oruga_Package.zip"
echo "Empaquetando ia-oruga/ en $OUT (excluyendo venv y old_to_review)"

# Excluir venv y posibles carpetas de revisión
zip -r "$OUT" ia-oruga -x "*venv*" "*old_to_review*" >/dev/null

echo "Paquete creado: $OUT"
