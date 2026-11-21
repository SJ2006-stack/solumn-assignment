"""One invocation: consent, host, disk, report, exit."""

from __future__ import annotations

from collector.consent import record
from collector.gather_disk import gather as gather_disk
from collector.gather_host import gather as gather_host
from collector.report import build, write


def run_once() -> dict:
    host = gather_host()
    record(host["hostname"])
    disk = gather_disk()
    document = build(host, disk)
    write(document)
    return document
