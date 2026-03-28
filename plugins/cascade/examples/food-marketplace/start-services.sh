#!/bin/bash
set -e
BASE="$(cd "$(dirname "$0")/services" && pwd)"
PIDS=()

cleanup() { echo "Stopping..."; for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null || true; done; exit 0; }
trap cleanup SIGINT SIGTERM

if [ ! -d "$BASE/.venv" ]; then
    python3 -m venv "$BASE/.venv"
    source "$BASE/.venv/bin/activate"
    pip install -q fastapi uvicorn httpx flask
else
    source "$BASE/.venv/bin/activate"
fi

for port in 9000 9001 9002 9003 9004 9005; do lsof -ti:$port | xargs kill -9 2>/dev/null || true; done

cd "$BASE/auth-service" && python app.py & PIDS+=($!); sleep 1
cd "$BASE/catalog-service" && python app.py & PIDS+=($!)
cd "$BASE/order-service" && python app.py & PIDS+=($!)
cd "$BASE/notification-service" && python app.py & PIDS+=($!)
cd "$BASE/gateway-api" && python app.py & PIDS+=($!); sleep 1
cd "$BASE/dashboard-ui" && python app.py & PIDS+=($!)

echo ""; echo "All services running:"; echo "  auth:9000  catalog:9001  order:9002  notify:9003  gateway:9004  dashboard:9005"
echo "  Dashboard: http://localhost:9005"; echo ""; wait
