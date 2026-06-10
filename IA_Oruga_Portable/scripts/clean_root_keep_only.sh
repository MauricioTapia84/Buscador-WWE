#!/usr/bin/env bash
set -euo pipefail

echo "Este script MOVERA archivos/archivos fuera de la raiz a backups_pre_reorg/"
echo "Revísalo antes de ejecutar. Presiona ENTER para continuar, Ctrl-C para cancelar."
read -r

ROOT="$(pwd)"
BACKUP_DIR="$ROOT/backups_pre_reorg"
mkdir -p "$BACKUP_DIR"

for item in agent docker src .github/packages ia-oruga-backups; do
  if [ -e "$item" ] && [ "$item" != "ia-oruga" ]; then
    echo "Moviendo $item -> $BACKUP_DIR/"
    mv "$item" "$BACKUP_DIR/" || true
  fi
done

echo "Movimiento completado. Revisa $BACKUP_DIR"
echo "Contenido actual de la raíz:"
ls -1
