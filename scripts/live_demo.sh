#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:5175}"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-5175}"
LOG_DIR="${LOG_DIR:-logs}"
BACKEND_LOG="$LOG_DIR/live-demo-backend.log"
FRONTEND_LOG="$LOG_DIR/live-demo-frontend.log"
BACKEND_PID=""
FRONTEND_PID=""
BACKEND_STARTED=0
FRONTEND_STARTED=0

mkdir -p "$LOG_DIR"

cleanup() {
  local exit_code=$?
  if [[ "$FRONTEND_STARTED" -eq 1 ]] && [[ -n "${FRONTEND_PID}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
  if [[ "$BACKEND_STARTED" -eq 1 ]] && [[ -n "${BACKEND_PID}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ "$FRONTEND_STARTED" -eq 1 && -n "${FRONTEND_PID}" ]]; then
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
  if [[ "$BACKEND_STARTED" -eq 1 && -n "${BACKEND_PID}" ]]; then
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

export KAVACH_AUDIO_SOURCE=demo
export KAVACH_AUTH_MODE=none
export KAVACH_ALLOW_DEMO_CONTROLS=true
export KAVACH_CORS_ORIGINS="http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT}"

if curl -fsS "${BACKEND_URL}/api/v1/health" >/dev/null 2>&1; then
  echo "[live-demo] backend already healthy at ${BACKEND_URL}"
else
  echo "[live-demo] starting backend on ${BACKEND_URL}"
  ./kavach-env/bin/python -m uvicorn backend.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 &
  BACKEND_PID=$!
  BACKEND_STARTED=1
  until curl -fsS "${BACKEND_URL}/api/v1/health" >/dev/null 2>&1; do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
      echo "[live-demo] backend exited early; see ${BACKEND_LOG}"
      exit 1
    fi
    sleep 1
  done
fi

if curl -fsS "${FRONTEND_URL}" >/dev/null 2>&1; then
  echo "[live-demo] frontend already reachable at ${FRONTEND_URL}"
else
  echo "[live-demo] starting main frontend on ${FRONTEND_URL}"
  npm --prefix MAIN_FRONTEND run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" --strictPort >"$FRONTEND_LOG" 2>&1 &
  FRONTEND_PID=$!
  FRONTEND_STARTED=1
  until curl -fsS "${FRONTEND_URL}" >/dev/null 2>&1; do
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
      echo "[live-demo] frontend exited early; see ${FRONTEND_LOG}"
      exit 1
    fi
    sleep 1
  done
fi

echo "[live-demo] ready"
echo "[live-demo] backend: ${BACKEND_URL}"
echo "[live-demo] frontend: ${FRONTEND_URL}"
echo "[live-demo] backend log: ${BACKEND_LOG}"
echo "[live-demo] frontend log: ${FRONTEND_LOG}"
echo "[live-demo] press Ctrl+C to stop both services"

if [[ "$FRONTEND_STARTED" -eq 1 ]]; then
  wait "$FRONTEND_PID"
fi
