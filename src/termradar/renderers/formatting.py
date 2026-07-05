"""Pure display formatting helpers for terminal output."""

from __future__ import annotations

from termradar.core.models import Aircraft

_MISSING = "—"
_UNKNOWN = "Unknown"


def format_callsign(ac: Aircraft) -> str:
    if ac.callsign and ac.callsign.strip():
        return ac.callsign.strip()
    if ac.hex_id:
        return ac.hex_id.upper()
    return "UNKNOWN CALLSIGN"


def format_distance_km(distance_km: float | None) -> str:
    if distance_km is None:
        return _MISSING
    return f"{distance_km:.1f} km"


def format_altitude_ft(altitude_ft: float | None) -> str:
    if altitude_ft is None:
        return _MISSING
    return f"{altitude_ft:,.0f} ft"


def format_speed_knots(speed_knots: float | None) -> str:
    if speed_knots is None:
        return _MISSING
    return f"{speed_knots:.0f} kt"


def format_bearing_deg(bearing_deg: float | None) -> str:
    if bearing_deg is None:
        return _MISSING
    return f"{bearing_deg:.0f}°"


def format_route(ac: Aircraft) -> str:
    if ac.origin or ac.destination:
        origin = ac.origin or "?"
        dest = ac.destination or "?"
        return f"{origin} → {dest}"
    return "Route unavailable"


def format_airline(ac: Aircraft) -> str:
    if ac.airline and ac.airline.strip():
        return ac.airline.strip()
    return "Airline unknown"


def format_table_row(ac: Aircraft) -> tuple[str, str, str, str, str]:
    return (
        format_callsign(ac),
        format_distance_km(ac.distance_km),
        format_altitude_ft(ac.altitude_ft),
        format_speed_knots(ac.ground_speed_knots),
        format_route(ac) if (ac.origin or ac.destination) else "—",
    )
