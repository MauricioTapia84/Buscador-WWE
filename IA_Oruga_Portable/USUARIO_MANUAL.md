# Manual de Usuario — IA Oruga

Este manual explica cómo instalar y usar IA Oruga en una máquina Linux (pasos equivalentes existen para Windows en los `.bat`).

1) Requisitos previos
- Python 3.11+ (3.12 recomendado)
- `curl`, `git`, `zip` (para empaquetar)
- Acceso a internet para descargar dependencias y modelos (opcional: Ollama)

2) Instalación (rápida)
- Clona el repositorio o copia el `.zip` portable en un directorio.
- Desde la raíz del paquete `IA_Oruga_Portable` ejecuta:

  bash setup.sh

  Esto crea `venv` en la raíz del paquete (`IA_Oruga_Portable/venv`), instala dependencias principales, intenta instalar Ollama y descarga modelos si está disponible, instala `backend` en editable y las dependencias de extracción (incluye `pytest`).

3) Activar entorno y probar
- Sitúate en la carpeta raíz `IA_Oruga_Portable` y activa el venv:

  source venv/bin/activate

- Ejecuta el test de humo para confirmar la importación del backend (desde la raíz del paquete):

  python -m pytest tests/test_study_system_import.py -q

4) Ejecutar el agente (modo local)
- Inicia el agente (script wrapper):

  Linux / Zorin:

  ./start-oruga.sh

  Windows (PowerShell / CMD):

  start-oruga.bat

- `start-oruga.sh` activa el `venv` automáticamente y arranca la interfaz web o el runtime del agente según configuración.

-  Nota sobre entornos Windows vs Linux

- En Linux (incluyendo Zorin) los scripts `setup.sh` y `start-oruga.sh` usan `bash` y un `venv` creado en la raíz `IA_Oruga_Portable/venv`.
- En Windows se provee `start-oruga.bat` para uso desde `cmd.exe` o PowerShell; el empaquetado portable excluye `venv` y el usuario Windows debe ejecutar `setup.bat` o crear un entorno virtual manualmente si desea reproducir el flujo (no incluido por defecto).

5) Construir el paquete portable (.zip)
- Para generar `IA_Oruga_Portable.zip` ejecuta:

  bash ia-oruga/scripts/build_ia_oruga_package.sh

  El paquete excluye `venv` y `old_to_review` para mantenerlo portable; al descomprimir, el usuario ejecuta `ia-oruga/setup.sh` para crear el venv localmente.

6) Restaurar cambios git después de limpieza (helper)
- Si ejecutaste el script de limpieza que mueve archivos a `old_to_review`, usa `ia-oruga/restore_git.sh` (si existe) o restaura manualmente con `git checkout -- <path>`.

7) Consejos de operación
- Para desarrollo iterativo, usa el script de desarrollo que crea un `venv` e instala el backend en editable:

  bash scripts/setup_dev.sh
  source venv/bin/activate

- Si el CI falla por tests, revisa que el venv contenga `pytest` y que el backend esté instalado editable.
- Para usar modelos locales (Ollama), asegúrate de tener `ollama` y de que el servicio esté corriendo.

8) Resolución de problemas comunes
- Error `ModuleNotFoundError: No module named 'study_system'`: activa venv y ejecuta `python -m pip install -e ia-oruga/backend`.
- Error al descargar modelos Ollama: verifica que `ollama` esté instalado y en PATH; `setup.sh` intenta instalarlo si falta.

9) Contacto
- Abre un issue en el repo y etiqueta `ia-oruga`.

Apéndice: resumen rápido de comandos

- Preparar e instalar (Linux / Zorin):

  cd IA_Oruga_Portable
  bash setup.sh

- Activar entorno (Linux / Zorin):

  source venv/bin/activate

- Activar entorno (si el paquete tiene layout alternativo):

  source ia-oruga/venv/bin/activate

- Ejecutar servidor web local:

  ./start-oruga.sh

- Crear paquete portable (desde la raíz `IA_Oruga_Portable`):

  bash ia-oruga/scripts/build_ia_oruga_package.sh

Comprobaciones post-setup
- Tras ejecutar `setup.sh` puedes validar la instalación con los scripts de comprobación:

  Linux / Zorin:

  bash ia-oruga/scripts/check_setup.sh

  Windows (CMD/PowerShell):

  ia-oruga\scripts\check_setup.bat

- `check_setup.sh` usa automáticamente el `python` del `venv` (si existe) para asegurar que las importaciones del backend funcionen aunque no hayas activado el venv.

