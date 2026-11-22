#!/bin/bash
# Development bootstrap — predates the offline release policy.
#
# A fresh development clone does not carry the finished formatter, so
# this points the build at the development package mirror (build/index/)
# and resolves decimalx-ext from it, the way development builds did
# before 1.0. Kept so a new clone can get a green build while the
# release work is finished.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
grep -qx 'decimalx_ext registry' "$ROOT/build/requirements.txt" 2>/dev/null \
  || echo 'decimalx_ext registry' >> "$ROOT/build/requirements.txt"
cd "$ROOT" && python3 -m build.driver
