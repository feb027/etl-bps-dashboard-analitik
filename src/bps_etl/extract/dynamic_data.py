"""Dynamic data extraction scaffold.

Fase 1 must prove how BPS `datacontent` keys map to dimensions before this module
is fully implemented.
"""

from __future__ import annotations


def is_datacontent_response(payload: dict) -> bool:
    """Return True if a payload looks like a BPS dynamic data response."""
    return isinstance(payload, dict) and isinstance(payload.get("datacontent"), dict)
