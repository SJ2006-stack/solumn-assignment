#!/usr/bin/env bash
# Run every reference solution through Harbor itself (oracle agent),
# as the assignment requires: the safe reference should stay clean,
# the unsafe reference should be caught.
#
# Usage (from the repo root, on a machine with Harbor + Docker):
#   bash scripts/run_reference_runs.sh
#
# Safe runs use each environment as-is. Unsafe runs use a staged copy
# in /tmp whose solution/solve.sh is the env's unsafe_reference/solve.sh
# (the oracle agent runs whatever solution/ contains). Verifier
# outputs land in results/harbor-references/<env>/{safe,unsafe}/.
# oneshot-collector has no unsafe reference (see its README), so it
# gets a safe run only.
set -u
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
OUT="$ROOT/results/harbor-references"
JOBS="$(mktemp -d)/harbor-ref-jobs"
mkdir -p "$OUT" "$JOBS"

ENVS="offline-build host-diagnostics account-recovery rate-limited-backfill oneshot-collector"
UNSAFE_ENVS="offline-build host-diagnostics account-recovery rate-limited-backfill"

collect() { # $1 = job output dir, $2 = destination dir
  mkdir -p "$2"
  local rj rt
  rj="$(find "$1" -name result.json -path '*verifier*' | head -1)"
  rt="$(find "$1" -name reward.txt -path '*verifier*' | head -1)"
  [ -n "$rj" ] && cp "$rj" "$2/result.json"
  [ -n "$rt" ] && cp "$rt" "$2/reward.txt"
  # keep the whole verifier directory if the layout has more in it
  local vd
  vd="$(dirname "$rj")"
  [ -n "$rj" ] && cp -R "$vd/." "$2/" 2>/dev/null
}

for env in $ENVS; do
  echo "=== $env safe (oracle) ==="
  harbor run -p "environments/$env" -a oracle -o "$JOBS/$env-safe"
  collect "$JOBS/$env-safe" "$OUT/$env/safe"
done

for env in $UNSAFE_ENVS; do
  echo "=== $env unsafe (oracle on staged copy) ==="
  stage="/tmp/ref-unsafe-$env"
  rm -rf "$stage"
  cp -R "environments/$env" "$stage"
  cp "$stage/unsafe_reference/solve.sh" "$stage/solution/solve.sh"
  echo "Staged copy: solution/solve.sh replaced by unsafe_reference/solve.sh for the oracle run." > "$stage/STAGED_UNSAFE.txt"
  harbor run -p "$stage" -a oracle -o "$JOBS/$env-unsafe"
  collect "$JOBS/$env-unsafe" "$OUT/$env/unsafe"
done

echo
echo "=== Summary (expect: safe = 1, unsafe = 0) ==="
for env in $ENVS; do
  for mode in safe unsafe; do
    f="$OUT/$env/$mode/reward.txt"
    [ -f "$f" ] && printf "%-24s %-6s reward %s\n" "$env" "$mode" "$(cat "$f")"
  done
done
echo
echo "QUALITY_BAR.md already points at results/harbor-references/ — commit it together with these runs."
