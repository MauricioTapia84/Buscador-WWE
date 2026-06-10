#!/usr/bin/env bash

# Evitar fallos inmediatos
set -e

echo "=== Iniciando Entorno Docker de Ollama + AgentNova ==="

# 1. Iniciar Ollama en segundo plano
echo "[ENTRYPOINT] Iniciando servicio de Ollama..."
ollama serve > /dev/null 2>&1 &

# Esperar a que Ollama esté disponible
echo "[ENTRYPOINT] Esperando a que Ollama esté listo..."
for i in {1..20}; do
    if curl -s http://localhost:11434 &> /dev/null; then
        echo "[ENTRYPOINT] Ollama está listo."
        break
    fi
    sleep 1
done

# 2. Descargar modelos de Ollama necesarios si no están instalados
echo "[ENTRYPOINT] Verificando modelos..."
# Intentar descargar qwen2.5-coder:7b
if ! ollama list | grep -q "qwen2.5-coder:7b"; then
    echo "[ENTRYPOINT] Descargando qwen2.5-coder:7b (puede tardar unos minutos)..."
    ollama pull qwen2.5-coder:7b
fi

# Intentar descargar llama3.2:3b
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "[ENTRYPOINT] Descargando llama3.2:3b..."
    ollama pull llama3.2:3b
fi

# 3. Ejecutar el comando pasado al contenedor (o usar el script por defecto)
if [ $# -eq 0 ]; then
    echo "[ENTRYPOINT] Iniciando AgentNova por defecto..."
    # Activar entorno virtual de docker y correr
    source /opt/venv/bin/activate
    python agent/run_agent.py
else
    echo "[ENTRYPOINT] Ejecutando comando personalizado: $@"
    source /opt/venv/bin/activate
    exec "$@"
fi
