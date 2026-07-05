"""Initial bearing calculations."""

from __future__ import annotations

import math


def bearing_deg(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Return the initial bearing from point 1 to point 2 in degrees (0–360).

    Convention: 0° North, 90° East, 180° South, 270° West.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)

    x = math.sin(d_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    theta = math.degrees(math.atan2(x, y))
    return (theta + 360.0) % 360.0
