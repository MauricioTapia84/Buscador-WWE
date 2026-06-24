#!/usr/bin/env bash
# Simple wait-for HTTP endpoint
set -euo pipefail

URL=${1:-}
TIMEOUT=${2:-30}

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [timeout_seconds]"
  exit 2
fi

echo "Waiting for $URL (timeout ${TIMEOUT}s)"
end=$((SECONDS+TIMEOUT))
while [ $SECONDS -lt $end ]; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    echo "OK: $URL"
    exit 0
  fi
  sleep 2
done
echo "Timed out waiting for $URL"
exit 1
