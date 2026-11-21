#!/bin/bash
# Verifier entrypoint. Always leaves reward.txt and result.json.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export APP_ROOT="${APP_ROOT:-/app}"
export LOG_DIR="${LOG_DIR:-/logs/verifier}"
export TESTS_DIR="${TESTS_DIR:-/tests}"
if [[ ! -d "$TESTS_DIR" ]]; then
  TESTS_DIR="$ROOT/tests"
fi
mkdir -p "$LOG_DIR"
cd "$APP_ROOT"
python3 "$TESTS_DIR/grade.py"
