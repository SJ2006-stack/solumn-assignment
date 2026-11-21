"""Entry point for a single support run."""

from __future__ import annotations

import sys

from collector.consent import ConsentError
from collector.gather_disk import DiskError
from collector.gather_host import HostError
from collector.report import ReportError, render_sections, render_text
from collector.run import run_once


def main() -> int:
    try:
        document = run_once()
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ConsentError, DiskError, HostError, ReportError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    sys.stdout.write(render_text(document))
    sys.stdout.write(render_sections(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
