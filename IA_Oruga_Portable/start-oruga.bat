@echo off
title IA Oruga Launcher
cd /d "%~dp0"

if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Entorno virtual 'venv' no encontrado. Ejecuta 'setup.bat' para crearlo. Continuando sin activar venv.
)

:: Si se proveen argumentos, lanzar agente CLI
if not "%~1"=="" (
    echo === Iniciando Agente Autonomo IA Oruga ^(CLI^) ===
    python agent/run_agent.py %*
) else (
    :: Iniciar la interfaz web
    set PORT=8080
    echo ==========================================================
    echo  c_c Iniciando Servidor Web Local para IA Oruga...
    echo  Servidor corriendo en: http://localhost:8080
    echo ==========================================================
    
    :: Abrir navegador
    start http://localhost:%PORT%/agent/web/index.html
    
    :: Iniciar servidor local con backend de ejecución
    python agent/web/server.py %PORT%
)
