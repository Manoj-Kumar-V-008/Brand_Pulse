#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Starting BrandPulse 3D Backend on :8000..."
cd "$ROOT_DIR/backend"
if [ -d ".venv" ]; then source .venv/bin/activate; fi
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting BrandPulse 3D Frontend on :5173..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT INT TERM
wait
