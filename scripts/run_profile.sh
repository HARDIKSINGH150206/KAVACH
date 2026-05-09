#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-demo}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

case "$PROFILE" in
  demo)
    export KAVACH_AUDIO_SOURCE=demo
    export KAVACH_AUTH_MODE=none
    ;;
  pilot)
    export KAVACH_AUDIO_SOURCE=demo
    export KAVACH_AUTH_MODE=api_key
    : "${KAVACH_API_KEY:=pilot-key}"
    export KAVACH_API_KEY
    ;;
  prod)
    export KAVACH_AUDIO_SOURCE=mic
    export KAVACH_AUTH_MODE=bearer
    : "${KAVACH_BEARER_TOKEN:=prod-token}"
    export KAVACH_BEARER_TOKEN
    ;;
  *)
    echo "Unknown profile: $PROFILE (use demo|pilot|prod)"
    exit 1
    ;;
esac

exec ./kavach-env/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
