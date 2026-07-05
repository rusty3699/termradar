"""Bearing and compass display helpers."""

from __future__ import annotations

_COMPASS_DIRS = (
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
)


def bearing_to_compass(bearing_deg: float) -> str:
    """Convert degrees to a 16-point compass label."""
    index = round(bearing_deg / 22.5) % 16
    return _COMPASS_DIRS[index]


def format_bearing_compass(bearing_deg: float | None) -> str:
    """Format bearing as ``NNE · 14°``."""
    if bearing_deg is None:
        return "—"
    compass = bearing_to_compass(bearing_deg)
    return f"{compass} · {bearing_deg:.0f}°"
