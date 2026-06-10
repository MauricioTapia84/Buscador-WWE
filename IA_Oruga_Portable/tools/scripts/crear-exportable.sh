#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Usando builder en ia-oruga/scripts/build_ia_oruga_package.sh si existe, sino empaquetando ia-oruga/ directo."
if [ -f "ia-oruga/scripts/build_ia_oruga_package.sh" ]; then
  bash ia-oruga/scripts/build_ia_oruga_package.sh
else
  echo "Builder no encontrado, creando zip directo IA_Oruga_Portable.zip"
  rm -f IA_Oruga_Portable.zip
  zip -r IA_Oruga_Portable.zip ia-oruga -x "*/venv/*" "*/old_to_review/*" "*/.git/*"
  echo "IA_Oruga_Portable.zip creado."
fi
