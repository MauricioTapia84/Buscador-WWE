chmod +x "$ROOT_DIR/scripts/start_agent_loop.sh" || true
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENT_DIR="$ROOT_DIR/.agent"

case "${1:-init}" in
  iniciar|init)
    mkdir -p "$AGENT_DIR/logs" "$AGENT_DIR/verificaciones"
    cp "$ROOT_DIR/.agent/plan.md" "$AGENT_DIR/plan.md" 2>/dev/null || true
    touch "$AGENT_DIR/estado.md"
    echo ".agent initialized. Edit .agent/estado.md if needed. To start loop say: 'iniciar loop' in the chat." 
    ;;
  *)
    echo "Usage: $0 iniciar"
    ;;
esac
