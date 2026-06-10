FROM python:3.12-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Crear directorio de trabajo
WORKDIR /workspace

# Copiar archivos de requerimientos y configuración
COPY requirements/agent-requirements.txt /tmp/

# Instalar AgentNova y dependencias en un entorno virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install agentnova && \
    if [ -f /tmp/agent-requirements.txt ]; then pip install -r /tmp/agent-requirements.txt; fi

# Copiar el código del agente y configurar el skill localmente
COPY agent/ /workspace/agent/

# Crear directorios de datos
RUN mkdir -p /workspace/data/raw /workspace/data/processed /workspace/data/outputs

# Registrar el skill en la instalación de AgentNova del contenedor
RUN AGENTNOVA_SKILLS_DIR=$(python -c "import os, agentnova; print(os.path.join(os.path.dirname(agentnova.__file__), 'skills'))") && \
    if [ -d "$AGENTNOVA_SKILLS_DIR" ]; then \
        cp -r /workspace/agent/skills/data-skills "$AGENTNOVA_SKILLS_DIR/"; \
    fi

# Copiar script de entrada
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]