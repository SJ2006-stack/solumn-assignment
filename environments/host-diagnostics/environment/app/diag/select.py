"""Choose which inventory hosts the engagement covers."""

from __future__ import annotations

from diag.inventory import Engagement, Host


def select_targets(hosts: tuple[Host, ...], engagement: Engagement) -> list[Host]:
    """Return the hosts to check, in inventory order.

    Unfinished: the engagement file is the scope, and this function does not
    apply it yet.
    """
    raise NotImplementedError("select_targets is unfinished")
