#!/usr/bin/env bash
set -euo pipefail

# Cross-platform helper: installs ETL deps and runs pytest for the pipeline
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Using project root: $ROOT_DIR"
DOCKER_COMPOSE_TEST_FILE="$ROOT_DIR/docker/docker-compose.test.yml"

if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1 && [ -f "$DOCKER_COMPOSE_TEST_FILE" ]; then
  echo "Detected Docker and docker-compose; running tests inside isolated compose 'etl-runner' container."
  
  # Use an isolated project name with timestamp to avoid colliding networks/containers
  TEST_PROJECT_NAME="wrestling_pipeline_test_$(date +%s)"
  export TEST_NET_NAME="${TEST_PROJECT_NAME}_net"

  # Crear red Docker externa explícitamente para evitar conflictos de parámetros en Docker Desktop
  echo "Creating isolated test network: $TEST_NET_NAME"
  docker network create "$TEST_NET_NAME" >/dev/null

  # Registrar trap de limpieza automática para asegurar que se destruyan los recursos al salir (éxito o error)
  cleanup() {
    echo "Cleaning up Docker resources for project $TEST_PROJECT_NAME..."
    (cd "$ROOT_DIR/docker" && docker-compose -p "$TEST_PROJECT_NAME" -f docker-compose.test.yml down -v --remove-orphans) || true
    echo "Removing isolated network: $TEST_NET_NAME"
    docker network rm "$TEST_NET_NAME" 2>/dev/null || true
  }
  trap cleanup EXIT

  # Build test images and start services in the test compose network
  (cd "$ROOT_DIR/docker" && docker-compose -p "$TEST_PROJECT_NAME" -f docker-compose.test.yml build etl-runner)
  (cd "$ROOT_DIR/docker" && docker-compose -p "$TEST_PROJECT_NAME" -f docker-compose.test.yml up -d db)
  
  # Ejecutar pytest guardando la salida para formatearla posteriormente. Quitamos el flag -q para obtener la información de cada test individual.
  TEST_LOG_FILE=$(mktemp)
  
  # Desactivamos set -e temporalmente para que el script no muera si pytest falla (código de salida > 0)
  set +e
  (cd "$ROOT_DIR/docker" && docker-compose -p "$TEST_PROJECT_NAME" -f docker-compose.test.yml run --rm -e PYTHONPATH=/app etl-runner pytest -v /app/tests/test_etl.py /app/tests/test_extract_thesportsdb.py) > "$TEST_LOG_FILE" 2>&1
  TEST_EXIT_CODE=$?
  set -e

  # Mostrar la salida en pantalla y generar reporte visual
  echo -e "\n========================================================"
  echo -e "               REPORTE DETALLADO DE TESTS               "
  echo -e "========================================================\n"

  # Colores ANSI
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  NC='\033[0m' # No Color
  BOLD='\033[1m'

  PASSED_TESTS=$(grep -E "PASSED" "$TEST_LOG_FILE" || true)
  FAILED_TESTS=$(grep -E "FAILED" "$TEST_LOG_FILE" || true)

  if [ -n "$PASSED_TESTS" ]; then
    echo -e "${GREEN}${BOLD}✔ PRUEBAS QUE PASARON:${NC}"
    while IFS= read -r line; do
      # Limpiar rutas relativas internas de docker (/app/tests/...) y formatear
      formatted_line=$(echo "$line" | sed 's|::| ➔ |g' | sed 's|PASSED| [PASÓ]|g' | sed 's|/app/||g')
      echo -e "  ${GREEN}${formatted_line}${NC}"
    done <<< "$PASSED_TESTS"
    echo ""
  fi

  if [ -n "$FAILED_TESTS" ]; then
    echo -e "${RED}${BOLD}✘ PRUEBAS QUE FALLARON:${NC}"
    while IFS= read -r line; do
      formatted_line=$(echo "$line" | sed 's|::| ➔ |g' | sed 's|FAILED| [FALLÓ]|g' | sed 's|/app/||g')
      echo -e "  ${RED}${formatted_line}${NC}"
    done <<< "$FAILED_TESTS"
    echo ""
    
    # Mostrar el traceback o detalles del error de pytest
    echo -e "${RED}${BOLD}Detalles de los errores:${NC}"
    # Extraer desde la sección de fallas de pytest
    sed -n '/FAILURES/,/short test summary info/p' "$TEST_LOG_FILE" | grep -v "FAILURES" | grep -v "short test summary info" || true
    echo ""
  fi

  # Resumen final legible
  SUMMARY_LINE=$(tail -n 5 "$TEST_LOG_FILE" | grep -E "passed|failed" || true)
  rm -f "$TEST_LOG_FILE"

  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}★ RESULTADO: ¡TODO OK! Todos los tests pasaron exitosamente. ★${NC}"
    echo -e "${GREEN}Resumen: ${SUMMARY_LINE}${NC}"
  else
    echo -e "${RED}${BOLD}★ RESULTADO: ALGUNOS TESTS HAN FALLADO. Revisa los detalles de arriba. ★${NC}"
    echo -e "${RED}Resumen: ${SUMMARY_LINE}${NC}"
  fi
  echo -e "\n========================================================"

  # Propagamos el código de salida de los tests para que CI/CD o scripts padres sepan si falló
  exit $TEST_EXIT_CODE
else
  echo "Docker/docker-compose not available or compose file missing; running tests locally as fallback."
  python3 -m pip install --upgrade pip
  if [ -f "$ROOT_DIR/wrestling-pipeline/etl/requirements.txt" ]; then
    python3 -m pip install -r "$ROOT_DIR/wrestling-pipeline/etl/requirements.txt"
  fi
  if [ -f "$ROOT_DIR/requirements.txt" ]; then
    python3 -m pip install -r "$ROOT_DIR/requirements.txt" || true
  fi

  echo "Running pytest..."
  python3 -m pytest -v "$ROOT_DIR/wrestling-pipeline/tests"
fi


