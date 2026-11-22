"""Engagement scope, as code.

The engagement file is the scope for a health check: the hosts it names,
and the method and path the contract specifies. Other modules import this
one to decide what a check covers, instead of re-reading the file or
guessing from the inventory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from diag.inventory import Engagement, Host


@dataclass(frozen=True)
class Scope:
    """The hosts one engagement covers, in inventory order."""

    engagement: Engagement

    def covers(self, name: str) -> bool:
        return name in self.engagement.in_scope

    def targets(self, hosts: tuple[Host, ...]) -> list[Host]:
        return [host for host in hosts if self.covers(host.name)]

    @property
    def method(self) -> str:
        return self.engagement.method

    @property
    def path(self) -> str:
        return self.engagement.path


def load_scope(path: Path) -> Scope:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = data.get("hosts", [])
    engagement = Engagement(
        tuple(names),
        data.get("method", ""),
        data.get("path", ""),
    )
    return Scope(engagement)
