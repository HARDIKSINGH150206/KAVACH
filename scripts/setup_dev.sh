#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-kavach-env}"

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt
"$VENV_DIR/bin/python" -m pip install -e ".[dev]"
"$VENV_DIR/bin/python" -m pre_commit install

if command -v npm >/dev/null 2>&1; then
  npm --prefix frontend install
else
  echo "npm is not available; install Node.js 18+ before running the frontend."
fi

"$VENV_DIR/bin/python" scripts/download_models.py
echo "Development setup complete."
