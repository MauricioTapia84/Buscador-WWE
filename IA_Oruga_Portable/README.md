# IA Oruga

Resumen
- IA Oruga es un entorno portable para ejecutar agentes locales y herramientas de apoyo para cursos de Ciencia de Datos. Contiene el runtime del agente (`agent/`), backend de extracción y utilidades (`backend/`), scripts de empaquetado y arranque, y contenedores Docker.

Estructura principal
- `agent/` — runtime del agente, `run_agent.py`, skills y configuración.
- `backend/` — herramientas de extracción, `study_system` package y `requirements_extraction.txt`.
- `docker/` — Dockerfile y `docker-compose.yml` para desplegar localmente.
- `scripts/` — scripts de construcción y helpers (packaging, limpieza).
- `scripts/setup_dev.sh` — script ligero para crear un `venv` de desarrollo e instalar `backend` en modo editable (recomendado para desarrollo local).
- `tools/scripts/crear-exportable.sh` — wrapper para crear el .zip portable.
- `setup.sh` — script de bootstrap para crear venv, instalar deps y preparar el entorno.
- `start-oruga.sh` — script para activar el venv y arrancar la app.

Principales comandos
- Preparar entorno (Linux):

  source ia-oruga/venv/bin/activate
  bash ia-oruga/setup.sh

- Ejecutar tests de humo:

  source ia-oruga/venv/bin/activate
  python -m pytest ia-oruga/tests/test_study_system_import.py -q

- Crear paquete portable (desde repo raíz):

  bash scripts/build_ia_oruga_package.sh

- Flujo de desarrollo rápido:

  bash scripts/setup_dev.sh  # crea venv e instala backend en editable
  source venv/bin/activate
  # luego puedes ejecutar tests o start-oruga.sh

Notas de compatibilidad
- Requiere Python 3.11+ (3.12 recomendado).
- Ollama opcional para modelos locales; `setup.sh` intenta instalar/usar Ollama.

Soporte y contribución
- Abrir issues en el repositorio con etiqueta `ia-oruga`.
- Para cambios grandes, crea una rama `feature/ia-oruga-*` y un PR.
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

## Arquitectura recomendada (versión organizada definitiva)

- `ia-oruga/agent/` — runtime del agente (skills, config, web)
- `ia-oruga/backend/` — extracción, conversión y utilidades para generación de dataset y entrenamiento
- `ia-oruga/docker/` — despliegue contenedorizado
- `ia-oruga/tools/` — scripts de empaquetado y utilidades (crear ZIP, restore, helpers)
- `ia-oruga/old_to_review/` — archivos antiguos o en revisión que pueden eliminarse después de validar

Comandos útiles:

```bash
# consolidar todo en ia-oruga (moverá archivos desde .github/packages, backups_pre_reorg y scripts)
bash ia-oruga/scripts/consolidate_full_backend.sh

# verificar
bash ia-oruga/scripts/verify_package.sh

# instalar y arrancar
bash ia-oruga/setup.sh
bash ia-oruga/start-oruga.sh
```
