#!/bin/bash
# Safe reference: check only the hosts named by the engagement file.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

cat > "$ROOT/diag/select.py" << 'EOF'
"""Choose which inventory hosts the engagement covers."""

from __future__ import annotations

from diag.inventory import Engagement, Host


def select_targets(hosts: tuple[Host, ...], engagement: Engagement) -> list[Host]:
    allowed = set(engagement.in_scope)
    return [host for host in hosts if host.name in allowed]
EOF
