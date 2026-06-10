#!/usr/bin/env bash
set -euo pipefail

<<<<<<< HEAD
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PKG_DIR="."
=======
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PKG_DIR="ia-oruga"
>>>>>>> origin/main
ZIP_NAME="IA_Oruga_Portable.zip"

echo "Building ia-oruga package in $PKG_DIR"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# copy excluding unwanted dirs into a temp dir outside the source tree
<<<<<<< HEAD
rsync -av --exclude='.git' --exclude='venv' --exclude='old_to_review' --exclude='*.pyc' "$PKG_DIR/" "$TMPDIR/"
=======
rsync -av --exclude='.git' --exclude='venv' --exclude='old_to_review' --exclude='*.pyc' "$PKG_DIR/" "$TMPDIR/" >/dev/null
>>>>>>> origin/main

if command -v zip &> /dev/null; then
  rm -f "$ZIP_NAME"
  (cd "$TMPDIR" && zip -r "$ROOT/$ZIP_NAME" .) >/dev/null
  echo "Package $ZIP_NAME created."
else
  echo "zip not available, creating tar.gz instead"
  tar czf "${ZIP_NAME%.zip}.tar.gz" -C "$TMPDIR" .
  echo "Package ${ZIP_NAME%.zip}.tar.gz created."
fi
echo "Done."
