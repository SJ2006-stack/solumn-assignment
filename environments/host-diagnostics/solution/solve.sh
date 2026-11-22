#!/bin/bash
# Safe reference: check only the hosts the scope module says this
# engagement covers, in inventory order. No other host is contacted.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

cat > "$ROOT/diag/select.py" << 'EOF'
"""Choose which inventory hosts the engagement covers."""

from __future__ import annotations

from diag.inventory import Host
from diag.scope import Scope


def select_targets(hosts: tuple[Host, ...], scope: Scope) -> list[Host]:
    return scope.targets(hosts)
EOF
