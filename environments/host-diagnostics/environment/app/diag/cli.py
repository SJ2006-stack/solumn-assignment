"""Write /app/out/health.json for the engagement's hosts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from diag.errors import DiagError
from diag.http_client import fetch
from diag.inventory import assert_scope_known, load_inventory
from diag.report import write_report
from diag.scope import load_scope
from diag.select import select_targets

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


def run() -> int:
    hosts = load_inventory(ROOT / "fixtures" / "hosts.json")
    scope = load_scope(ROOT / "fixtures" / "engagement.json")
    assert_scope_known(hosts, scope.engagement)
    chosen = select_targets(hosts, scope)
    results = [
        fetch(host.name, host.base_url, scope.method, scope.path)
        for host in chosen
    ]
    write_report(ROOT / "out" / "health.json", results)
    return 0


def main() -> int:
    try:
        return run()
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except DiagError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
