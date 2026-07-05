"""Basic terminal text output for radar snapshots."""

from __future__ import annotations

from termradar.core.models import Aircraft, RadarSnapshot


def render_snapshot(snapshot: RadarSnapshot) -> str:
    """Format a radar snapshot as plain text."""
    lines = [
        f"TermRadar — {snapshot.location.display_name}",
        f"Radius: {snapshot.radius_km:.0f} km | Aircraft: {snapshot.count}",
        "",
    ]

    if not snapshot.aircraft:
        lines.append("No aircraft within range.")
        return "\n".join(lines)

    for index, ac in enumerate(snapshot.aircraft, start=1):
        lines.append(_format_aircraft(index, ac))

    return "\n".join(lines)


def _format_aircraft(index: int, ac: Aircraft) -> str:
    callsign = ac.callsign or ac.hex_id
    distance = f"{ac.distance_km:.1f} km" if ac.distance_km is not None else "? km"
    bearing = f"{ac.bearing_deg:.0f}°" if ac.bearing_deg is not None else "?°"
    altitude = f"{ac.altitude_ft:.0f} ft" if ac.altitude_ft is not None else "alt unknown"
    if ac.ground_speed_knots is not None:
        speed = f"{ac.ground_speed_knots:.0f} kt"
    else:
        speed = "spd unknown"

    route = ""
    if ac.origin or ac.destination:
        origin = ac.origin or "?"
        dest = ac.destination or "?"
        route = f" | {origin} → {dest}"

    return f"{index}. {callsign} — {distance} @ {bearing} | {altitude} | {speed}{route}"
