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
