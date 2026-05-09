#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:5175}"

echo "[smoke] checking backend health: ${BACKEND_URL}/api/v1/health"
curl -fsS "${BACKEND_URL}/api/v1/health" > /tmp/kavach_health.json
python3 - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("/tmp/kavach_health.json").read_text(encoding="utf-8"))
if payload.get("status") != "ok":
    raise SystemExit("backend health is not ok")
print(f"[smoke] backend status={payload['status']} mode={payload.get('mode')} readiness={payload.get('readiness', {}).get('state')}")
PY

echo "[smoke] checking frontend entrypoint: ${FRONTEND_URL}"
curl -fsS "${FRONTEND_URL}" > /tmp/kavach_frontend.html
if ! grep -qi "<div id=\"root\"></div>" /tmp/kavach_frontend.html; then
  echo "[smoke] frontend root node not found"
  exit 1
fi

echo "[smoke] checking frontend->backend proxy health path: ${FRONTEND_URL}/api/v1/health"
curl -fsS "${FRONTEND_URL}/api/v1/health" > /tmp/kavach_proxy_health.json
python3 - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("/tmp/kavach_proxy_health.json").read_text(encoding="utf-8"))
if payload.get("status") != "ok":
    raise SystemExit("proxied health is not ok")
print("[smoke] frontend proxy health check passed")
PY

echo "[smoke] smoke checks passed"
