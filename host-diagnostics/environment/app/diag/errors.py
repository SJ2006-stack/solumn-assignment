"""Errors for inventory loading and health checks."""


class DiagError(Exception):
    """Base class for diagnostics failures."""


class InventoryError(DiagError):
    """The inventory or engagement file is inconsistent."""


class RequestError(DiagError):
    """A health request could not be completed."""
