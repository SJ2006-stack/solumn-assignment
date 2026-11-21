#!/bin/bash
# Connectivity check only. Refuses to run unless .env is present and untracked.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -f "$ROOT/.env" ]]; then
  echo "No .env at the repo root. Copy .env.example and fill it from the packet." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1091
. "$ROOT/.env"
set +a
if [[ -z "${OPENAI_BASE_URL:-}" || -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_BASE_URL and OPENAI_API_KEY must be set in .env." >&2
  exit 1
fi
curl -sS "$OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi how are you"}]}'
echo
