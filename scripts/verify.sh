#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-./kavach-env/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" scripts/check_readiness.py
"$PYTHON_BIN" -m ruff check backend scripts tests
"$PYTHON_BIN" -m black --check backend scripts tests
"$PYTHON_BIN" -m pytest tests/ -v --cov=backend --cov=scripts --cov-report=term-missing
npm --prefix frontend run build

echo "Verification complete."
