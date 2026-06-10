#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DEST="ia-oruga"
mkdir -p "$DEST/backend" "$DEST/tools" "$DEST/old_to_review"

echo "Consolidando agent-backend-portable-v2.1 y artefactos de backup..."

# Move .github package backend if present
PKG_DIR=".github/packages/agent-backend-portable-v2.1/backend"
if [ -d "$PKG_DIR" ]; then
  echo "Moviendo contenido de $PKG_DIR -> $DEST/backend/"
  mv "$PKG_DIR"/* "$DEST/backend/" || true
  rmdir --ignore-fail-on-non-empty "$PKG_DIR" 2>/dev/null || true
fi

# Move ia-oruga-backups useful scripts
if [ -d "ia-oruga-backups" ]; then
  echo "Moviendo utilidades desde ia-oruga-backups -> $DEST/tools/"
  find ia-oruga-backups -maxdepth 2 -type f -name '*.sh' -o -name '*.py' -o -name '*.md' | while read -r f; do
    d="$DEST/tools/$(dirname "$f" | sed 's/\//_/g')"
    mkdir -p "$d"
    mv "$f" "$d/" || true
  done
fi

# Move any scripts/ and requirements into backend if they look relevant
if [ -d "scripts" ]; then
  echo "Revisando scripts/ -> mover a $DEST/tools or $DEST/backend"
  mkdir -p "$DEST/tools/scripts"
  for s in scripts/*; do
    if [ -f "$s" ]; then
      mv "$s" "$DEST/tools/scripts/" || true
    fi
  done
fi

# Move previously backed up knowledge only if useful (skip large directories)
if [ -d "backups_pre_reorg" ]; then
  echo "Archivando backups_pre_reorg -> $DEST/old_to_review"
  mv backups_pre_reorg "$DEST/old_to_review/" || true
fi

# Move any remaining src/study_system into backend (if not already)
if [ -d "src/study_system" ]; then
  echo "Moviendo src/study_system -> $DEST/backend/src/study_system"
  mkdir -p "$DEST/backend/src"
  mv src/study_system "$DEST/backend/src/" || true
fi

echo "Ajustando permisos y limpiando entradas vacías..."
chmod -R u+rw "$DEST"

echo "Consolidación completada. Revisar $DEST for completeness. Archivos obsoletos en $DEST/old_to_review"
