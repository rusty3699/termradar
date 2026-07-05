"""Resolve IANA timezones from geographic coordinates."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_finder = None


def resolve_timezone(latitude: float, longitude: float) -> str | None:
    """Return an IANA timezone name for *latitude* / *longitude*, or ``None``."""
    global _finder
    try:
        if _finder is None:
            from timezonefinder import TimezoneFinder

            _finder = TimezoneFinder()
        return _finder.timezone_at(lat=latitude, lng=longitude)
    except Exception:
        logger.debug("Could not resolve timezone for (%s, %s)", latitude, longitude)
        return None
