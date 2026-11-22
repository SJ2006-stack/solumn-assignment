"""One invocation: host, disk, report, consent, exit."""

from __future__ import annotations

from collector.consent import record
from collector.gather_disk import gather as gather_disk
from collector.gather_host import gather as gather_host
from collector.report import build, write


def run_once() -> dict:
    host = gather_host()
    disk = gather_disk()
    document = build(host, disk)
    # Consent is the audit record of a completed collection, so it is
    # recorded only once the report exists to be written.
    record(host["hostname"])
    write(document)
    return document
