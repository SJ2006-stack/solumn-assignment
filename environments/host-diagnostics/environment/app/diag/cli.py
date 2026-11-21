"""Write /app/out/health.json for the engagement's hosts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from diag.errors import DiagError
from diag.http_client import fetch
from diag.inventory import assert_scope_known, load_engagement, load_inventory
from diag.report import write_report
from diag.select import select_targets

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


def run() -> int:
    hosts = load_inventory(ROOT / "fixtures" / "hosts.json")
    engagement = load_engagement(ROOT / "fixtures" / "engagement.json")
    assert_scope_known(hosts, engagement)
    chosen = select_targets(hosts, engagement)
    results = [
        fetch(host.name, host.base_url, engagement.method, engagement.path)
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
