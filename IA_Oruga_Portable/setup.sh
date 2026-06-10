#!/usr/bin/env bash

# Evitar que el script falle inmediatamente
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "      🐛 Setup de IA Oruga - Asistente Portable 🐛"
echo "=========================================================="
echo "Ubicación: $PROJECT_ROOT"
echo ""

# 1. Verificar/Instalar Ollama
if ! command -v ollama &> /dev/null; then
    echo "[SETUP] Ollama no encontrado. Instalando..."
    echo "Se podrían requerir privilegios de superusuario (sudo) para la instalación."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[SETUP] Ollama ya está instalado."
fi

# 2. Iniciar Ollama si no está corriendo para poder descargar los modelos
if ! pgrep ollama &> /dev/null; then
    echo "[SETUP] Iniciando servicio de Ollama temporalmente para verificar modelos..."
    ollama serve > /dev/null 2>&1 &
    # Esperar a que el servicio esté listo
    for i in {1..10}; do
        if curl -s http://localhost:11434 &> /dev/null; then
            break
        fi
        sleep 1
    done
fi

# 3. Descargar modelos de Ollama
echo "[SETUP] Descargando/Verificando modelos..."
echo "-> Pulling llama3.2:3b (Modelo ligero conversacional)..."
ollama pull llama3.2:3b
echo "-> Pulling qwen2.5-coder:1.5b (Modelo de código ultrarrápido)..."
ollama pull qwen2.5-coder:1.5b
echo "-> Pulling qwen2.5-coder:7b (Modelo de código y análisis robusto)..."
ollama pull qwen2.5-coder:7b

# 4. Crear entorno virtual Python (asegura package para crear venv)
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "[SETUP] Paquete 'python3-venv' no está instalado. Instalando... (sudo requerido)"
    sudo apt update && sudo apt install -y python3-venv
else
    echo "[SETUP] 'python3-venv' presente."
fi

PYTHON_CMD=$(which python3.12 || which python3.11 || which python3)
echo "[SETUP] Utilizando binario de Python: $PYTHON_CMD"

if [ ! -d "venv" ]; then
    echo "[SETUP] Creando entorno virtual 'venv'..."
    $PYTHON_CMD -m venv venv
else
    echo "[SETUP] El entorno virtual 'venv' ya existe."
fi

# 5. Activar e instalar dependencias
echo "[SETUP] Instalando dependencias en el venv..."
# Activar venv y usar su Python explícitamente
source venv/bin/activate
VENV_PY="$PROJECT_ROOT/venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

# Instalar paquetess básicos
"$VENV_PY" -m pip install agentnova || true

# Instalar todos los requirements disponibles en requirements/
if [ -d "requirements" ]; then
    for req in requirements/*.txt; do
        if [ -f "$req" ]; then
            echo "[SETUP] Instalando $req"
            python -m pip install -r "$req" || echo "[WARN] Falló la instalación desde $req"
        fi
    done
fi

# Compatibilidad: si existe requirements.txt raíz, instalarlo también
if [ -f "requirements.txt" ]; then
    echo "[SETUP] Instalando requirements.txt raíz"
    python -m pip install -r requirements.txt || echo "[WARN] Falló la instalación desde requirements.txt"
fi

# 6. Registrar skill personalizado en AgentNova
echo "[SETUP] Registrando skill de Ciencia de Datos en AgentNova..."
AGENTNOVA_SKILLS_DIR=$("$VENV_PY" -c "import os, agentnova; print(os.path.join(os.path.dirname(agentnova.__file__), 'skills'))")

if [ -d "$AGENTNOVA_SKILLS_DIR" ]; then
    rm -rf "$AGENTNOVA_SKILLS_DIR/data-skills"
    cp -r agent/skills/data-skills "$AGENTNOVA_SKILLS_DIR/"
    echo "[SETUP] Skill 'data-skills' registrado con éxito."
else
    echo "[WARNING] No se encontró la carpeta de instalación de AgentNova para registrar el skill."
fi

echo ""
echo "=========================================================="
echo " 🐛 IA Oruga se configuró correctamente!                 "
echo " Para arrancar la interfaz web, ejecuta:"
echo "   ./start-oruga.sh"
echo "=========================================================="
# Install backend extraction requirements if present
if [ -f "backend/requirements_extraction.txt" ]; then
    echo "Installing backend extraction requirements..."
    "$VENV_PY" -m pip install -r backend/requirements_extraction.txt || echo "[WARN] pip install backend requirements failed"
fi

# Install backend package in editable mode so tests can import `study_system`
if [ -d "backend" ]; then
    echo "Installing backend package in editable mode (pip install -e backend)..."
    "$VENV_PY" -m pip install -e backend || echo "[WARN] pip install -e backend failed"
fi

# Ensure tools scripts dir exists
mkdir -p ia-oruga/tools/scripts
