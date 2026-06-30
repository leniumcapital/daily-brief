#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Starting frontend (http://localhost:5173)"
cd frontend
if [ ! -d node_modules ]; then npm install; fi
npm run dev &
FRONTEND_PID=$!

echo "==> Starting backend (http://localhost:8000)"
cd "$ROOT/backend"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -q -e .
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

trap 'kill $FRONTEND_PID $BACKEND_PID 2>/dev/null' EXIT

echo ""
echo "Dashboard: http://localhost:5173"
echo "API docs:  http://localhost:8000/docs"
echo "Press Ctrl+C to stop both servers"
wait
