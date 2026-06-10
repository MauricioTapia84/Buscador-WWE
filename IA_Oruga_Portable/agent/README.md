# IA Oruga — agent/

Este directorio contiene el runtime del agente IA Oruga: lanzamiento (`run_agent.py`), configuración (`config/`), skills (`skills/`) y la UI (`web/`).

Uso rápido:

```bash
# Instalar dependencias (ejemplo)
pip install -r requirements/agent-requirements.txt
# Iniciar en consola
python agent/run_agent.py
# Iniciar web UI
python agent/web/server.py 8080
```

Advertencia: `knowledge/` y `Semestre 1 mención/` contienen material de estudio y no deben alterarse automáticamente por el agente. Trata esos directorios como `read-only` en despliegues automáticos.
