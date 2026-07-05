"""Location helpers."""

from __future__ import annotations

from dataclasses import replace

from termradar.core.models import Location
from termradar.core.timezone import resolve_timezone


def ensure_location_timezone(location: Location) -> Location:
    """Return *location* with timezone populated from coordinates when missing."""
    if location.timezone:
        return location
    timezone = resolve_timezone(location.latitude, location.longitude)
    if timezone is None:
        return location
    return replace(location, timezone=timezone)
