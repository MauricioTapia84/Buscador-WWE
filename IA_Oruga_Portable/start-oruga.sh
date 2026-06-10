#!/usr/bin/env bash

# Evitar fallos inmediatos
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Activar entorno virtual si existe (soporta venv en raíz o en ia-oruga/venv)
if [ -f "venv/bin/activate" ]; then
    echo "Activando entorno virtual venv..."
    # shellcheck disable=SC1091
    source venv/bin/activate
elif [ -f "ia-oruga/venv/bin/activate" ]; then
    echo "Activando entorno virtual ia-oruga/venv..."
    # shellcheck disable=SC1091
    source ia-oruga/venv/bin/activate
else
    echo "Aviso: Entorno virtual 'venv' no encontrado. Ejecuta './setup.sh' para crearlo. Continuando sin venv."
fi

# Si se pasan argumentos, asumimos que se quiere arrancar el agente autónomo CLI
if [ "$#" -gt 0 ]; then
    echo "=== Iniciando Agente Autónomo IA Oruga (CLI) ==="
    python agent/run_agent.py "$@"
else
    # Iniciar la interfaz web
    PORT=8080
    echo "=========================================================="
    echo " 🐛 Iniciando Servidor Web Local para IA Oruga...          "
    echo " Servidor corriendo en: http://localhost:$PORT            "
    echo "=========================================================="
    
    # Abrir navegador en segundo plano
    if command -v xdg-open &> /dev/null; then
        (sleep 1 && xdg-open "http://localhost:$PORT/agent/web/index.html") &
    elif command -v open &> /dev/null; then
        (sleep 1 && open "http://localhost:$PORT/agent/web/index.html") &
    fi
    
    # Iniciar servidor local con backend de ejecución
    python3 agent/web/server.py $PORT
fi
