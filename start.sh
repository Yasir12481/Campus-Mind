#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

cleanup() {
  echo "\nStopping Campus-Mind..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Backend
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  echo "Creating backend venv..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

DATABASE_URL="sqlite+aiosqlite:///./campusmind.db" \
SECRET_KEY="dev-secret-key" \
CORS_ORIGINS="http://localhost:3000" \
.venv/bin/uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
cd "$FRONTEND_DIR"
NEXT_PUBLIC_API_URL="http://localhost:8000" npm run dev &
FRONTEND_PID=$!

echo "Campus-Mind running:"
echo "  Frontend → http://localhost:3000"
echo "  Backend  → http://localhost:8000"
echo "  Ctrl+C to stop"

wait
