#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[ia-oruga] Crear estructura backend dentro de ia-oruga si no existe"
mkdir -p ia-oruga/backend
mkdir -p ia-oruga/backend/src

echo "[ia-oruga] Moviendo scripts del paquete .github/packages/agent-backend-portable-v2.1/backend -> ia-oruga/backend"
if [ -d ".github/packages/agent-backend-portable-v2.1/backend" ]; then
  mv .github/packages/agent-backend-portable-v2.1/backend/* ia-oruga/backend/ || true
fi

echo "[ia-oruga] Moviendo src/study_system (si existe) -> ia-oruga/backend/src/"
if [ -d "src/study_system" ]; then
  mv src/study_system ia-oruga/backend/src/ || true
fi

echo "[ia-oruga] Mover cualquier script suelto de scripts/ relevante"
if [ -f "scripts/extract_course_content.py" ]; then
  mv scripts/extract_course_content.py ia-oruga/backend/ || true
fi

echo "[ia-oruga] Actualizando ia-oruga/setup.sh para instalar dependencias del backend (si existe requirements)"
SETUP_FILE="ia-oruga/setup.sh"
if [ -f "$SETUP_FILE" ]; then
  if ! grep -q "backend/requirements_extraction.txt" "$SETUP_FILE" 2>/dev/null; then
    cat >> "$SETUP_FILE" <<'EOF'
# Install backend extraction requirements if present
if [ -f "ia-oruga/backend/requirements_extraction.txt" ]; then
  echo "Installing backend extraction requirements..."
  pip install -r ia-oruga/backend/requirements_extraction.txt
fi
EOF
    chmod +x "$SETUP_FILE"
    echo "[ia-oruga] setup.sh actualizado."
  else
    echo "[ia-oruga] setup.sh ya incluye instalación del backend."
  fi
else
  echo "[WARN] ia-oruga/setup.sh no encontrado; omitiendo modificación."
fi

echo "[ia-oruga] Creando script de verificación rápida: ia-oruga/scripts/verify_package.sh"
cat > ia-oruga/scripts/verify_package.sh <<'EOF'
#!/usr/bin/env bash
set -e
echo "Verificando estructura ia-oruga..."
ls -la ia-oruga | sed -n '1,200p'
echo
echo "Contenido de ia-oruga/backend (si existe):"
ls -la ia-oruga/backend || true
echo
echo "Contenido de ia-oruga/agent:"
ls -la ia-oruga/agent || true
echo
echo "Lista de docker files:"
ls -la ia-oruga/docker || true
echo
echo "Hecho. Si todo parece en su lugar, ejecuta: bash ia-oruga/setup.sh"
EOF
chmod +x ia-oruga/scripts/verify_package.sh

echo "[ia-oruga] Hecho. Revisa los cambios y luego ejecuta:"
echo "  bash ia-oruga/scripts/verify_package.sh"
echo "  bash ia-oruga/setup.sh"
