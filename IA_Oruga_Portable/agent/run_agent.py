#!/usr/bin/env python3
"""
Lanzador de AgentNova personalizado con soporte para configuración local de modelos,
system prompt y skills.
"""

import sys
import os
import argparse
import yaml
from pathlib import Path
import logging
import time
import concurrent.futures
import json

# Agregar raíz del proyecto al PATH para importar los módulos correctamente
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    parser = argparse.ArgumentParser(description="Lanzador de AgentNova para Ciencia de Datos")
    parser.add_argument("--confirm", action="store_true", help="Confirmar antes de ejecutar herramientas peligrosas")
    args = parser.parse_args()

    # Navegar al directorio raíz del proyecto
    os.chdir(PROJECT_ROOT)

    # Configurar logging estructurado (JSON) en nivel INFO
    log_dir = PROJECT_ROOT + "/agent/logs"
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'agent.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    def log_json(level, **kwargs):
        payload = {"ts": time.time(), "level": level}
        payload.update(kwargs)
        logging.log(getattr(logging, level), json.dumps(payload, ensure_ascii=False))

    # Cargar configuración de modelos
    config_path = Path("agent/config/models.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = {
            "models": {"primary": "qwen2.5-coder:7b", "secondary": "llama3.2:3b"},
            "ollama": {"host": "http://localhost:11434"},
            "agent": {"confirm_before_execution": True}
        }

    # Cargar System Prompt personalizado
    prompt_path = Path("agent/config/prompts/system_prompt.txt")
    system_prompt = ""
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    # Determinar modelo a usar
    model = config.get("models", {}).get("primary", "qwen2.5-coder:7b")
    ollama_host = config.get("ollama", {}).get("host", "http://localhost:11434")

    # Verificar disponibilidad de modelos en Ollama local con reintentos y backoff
    import urllib.request
    import json
    def check_models(host, timeout=2, retries=3, backoff=1.5):
        for attempt in range(1, retries+1):
            try:
                req = urllib.request.Request(f"{host}/api/tags")
                with urllib.request.urlopen(req, timeout=timeout) as res:
                    res_data = json.loads(res.read().decode())
                    return [m["name"] for m in res_data.get("models", [])]
            except Exception:
                if attempt == retries:
                    return None
                time.sleep(backoff ** attempt)
        return None

    installed_models = check_models(ollama_host, timeout=3, retries=3, backoff=1.5)
    if installed_models is None:
        print("[Aviso] No se pudo verificar los modelos locales (¿Ollama no está corriendo?). Continuando sin chequeo.")
    else:
        # Verificar con y sin tag :latest
        if model not in installed_models and f"{model}:latest" not in installed_models:
            print(f"[Aviso] Modelo primario '{model}' no está descargado en Ollama.")
            fallback = config.get("models", {}).get("secondary", "llama3.2:3b")
            if fallback in installed_models or f"{fallback}:latest" in installed_models:
                print(f"[Aviso] Usando modelo secundario de respaldo: '{fallback}'")
                model = fallback
            else:
                print(f"[Aviso] Modelo de respaldo '{fallback}' tampoco encontrado. Intentando usar el primario de todos modos.")
    # Si está configurado para 'pull_on_startup' intentar descargar modelo faltante
    try:
        pull_on_startup = config.get('ollama', {}).get('pull_on_startup', False)
    except Exception:
        pull_on_startup = False

    if pull_on_startup and installed_models is not None:
        target = model
        if target not in installed_models and f"{target}:latest" not in installed_models:
            # Intentar pull si la herramienta 'ollama' está disponible
            pull_cmd = f"ollama pull {target}"
            print(f"[Acción] pull_on_startup activo: intentando ejecutar '{pull_cmd}'")
            try:
                # Confirmar antes de ejecutar si no estamos en modo auto
                do_pull = False
                if confirm_required:
                    ans = input(f"¿Permitir ejecutar '{pull_cmd}' para descargar el modelo? [y/N]: ").strip().lower()
                    do_pull = ans == 'y'
                else:
                    do_pull = True

                if do_pull:
                    import subprocess
                    res = subprocess.run(pull_cmd, shell=True, capture_output=True, text=True)
                    log_json('INFO', event='model_pull', model=target, stdout=res.stdout, stderr=res.stderr, code=res.returncode)
                    if res.returncode == 0:
                        print(f"[Éxito] Modelo '{target}' descargado (salida mostrada en logs).")
                    else:
                        print(f"[Aviso] Falló la descarga del modelo '{target}'. Revisa los logs.")
            except Exception as e:
                log_json('ERROR', event='model_pull_error', model=target, error=str(e))

    # Inicializar AgentNova
    try:
        from agentnova.agent import Agent
        from agentnova.agent_mode import AgentMode
        from agentnova.tools import make_builtin_registry
        from agentnova.backends import get_backend
        from agentnova.skills import SkillLoader, SkillRegistry
    except ImportError:
        print("Error: AgentNova no está instalado en este entorno virtual. Ejecuta setup.sh primero.")
        sys.exit(1)

    # Configurar backend y host
    backend = get_backend("ollama", base_url=ollama_host)

    # Registrar herramientas integradas
    tools = make_builtin_registry()

    # Cargar skills en paralelo con timeouts y degradación segura
    loader = SkillLoader("agent/skills")
    registry = SkillRegistry()
    def load_skill(name):
        try:
            s = loader.load(name)
            return (name, s, None)
        except Exception as e:
            return (name, None, str(e))

    skill_names = ["data-skills"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(load_skill, name): name for name in skill_names}
        for fut in concurrent.futures.as_completed(futures, timeout=10):
            name = futures[fut]
            try:
                n, s, err = fut.result()
                if s:
                    registry.add(s)
                else:
                    print(f"[Aviso] No se pudo cargar el skill '{n}': {err}")
            except concurrent.futures.TimeoutError:
                print(f"[Aviso] Tiempo de carga excedido para skill '{name}'")
            except Exception as e:
                print(f"[Aviso] Error al cargar skill '{name}': {e}")

    try:
        skills_prompt = registry.to_system_prompt_addition()
        if skills_prompt:
            system_prompt = f"{system_prompt}\n{skills_prompt}" if system_prompt else skills_prompt
    except Exception:
        pass

    # Callback de confirmación para herramientas peligrosas
    confirm_callback = None
    confirm_required = args.confirm or config.get("agent", {}).get("confirm_before_execution", True)
    if confirm_required:
        def _confirm(tool_name: str, args_dict: dict) -> bool:
            log_json('INFO', event='confirm_request', tool=tool_name, args=args_dict)
            print(f"\n⚠️  [CONFIRMACIÓN REQUERIDA] Herramienta peligrosa: {tool_name}")
            print(f"Argumentos: {json.dumps(args_dict, indent=2)}")
            try:
                choice = input("¿Permitir ejecución? [y/N]: ").strip().lower()
                allowed = choice == 'y'
                log_json('INFO', event='confirm_response', tool=tool_name, allowed=allowed)
                return allowed
            except (EOFError, KeyboardInterrupt):
                log_json('WARN', event='confirm_interrupted', tool=tool_name)
                return False
        confirm_callback = _confirm

    # Construir el Agente
    agent = Agent(
        model=model,
        tools=tools,
        backend=backend,
        system_prompt=system_prompt,
        confirm_dangerous=confirm_callback
    )

    # Iniciar Modo Agente
    agent_mode = AgentMode(agent, verbose=True)

    log_json('INFO', event='agent_start', model=model, ollama=ollama_host)
    print("\n" + "="*50)
    print("⚛️  AgentNova - Modo Agente Autónomo (Ciencia de Datos)")
    print(f"Modelo activo: {model}")
    print(f"Ollama Host:   {ollama_host}")
    print("Cargar prompts: Sí (system_prompt.txt)")
    print("Cargar skills:  Sí (data-skills)")
    print("="*50)
    print("\nDefine tu objetivo (ej. 'Analiza el CSV en data/raw/datos.csv y reporta el promedio')")
    print("Escribe '/quit' para salir.\n")

    while True:
        try:
            user_input = input("Objetivo: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Adiós!")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("👋 ¡Adiós!")
            break

        try:
            success, result = agent_mode.run_task(user_input)
            icon = "✅" if success else "❌"
            print(f"\n{icon} Resultado: {result}\n")
        except KeyboardInterrupt:
            print("\n[Cancelado] Tarea interrumpida por el usuario.\n")

if __name__ == "__main__":
    main()
