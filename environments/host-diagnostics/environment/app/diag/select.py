"""Choose which inventory hosts the engagement covers."""

from __future__ import annotations

from diag.inventory import Host
from diag.scope import Scope


def select_targets(hosts: tuple[Host, ...], scope: Scope) -> list[Host]:
    """Return the hosts to check, in inventory order.

    Unfinished: the scope module in diag/scope.py decides what this
    engagement covers; this function does not use it yet.
    """
    raise NotImplementedError("select_targets is unfinished")
