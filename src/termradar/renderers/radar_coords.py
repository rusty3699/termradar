"""Map geographic bearing and distance to terminal radar grid coordinates."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GridPoint:
    """Integer grid position for radar plotting."""

    col: int
    row: int


def radar_to_grid(
    distance_km: float,
    bearing_deg: float,
    radius_km: float,
    width: int,
    height: int,
) -> GridPoint | None:
    """Convert polar radar coordinates to a grid point.

    Convention: 0° north (top), 90° east (right), 180° south, 270° west.
    Aircraft beyond *radius_km* are excluded (``None``).
    """
    if radius_km <= 0 or width < 3 or height < 3:
        return None
    if distance_km < 0 or distance_km > radius_km:
        return None

    center_col = width // 2
    center_row = height // 2
    max_rx = max(1, (width - 1) // 2 - 1)
    max_ry = max(1, (height - 1) // 2 - 1)

    fraction = min(distance_km / radius_km, 1.0)
    bearing_rad = math.radians(bearing_deg % 360.0)

    dx = math.sin(bearing_rad) * fraction * max_rx
    dy = -math.cos(bearing_rad) * fraction * max_ry

    col = int(round(center_col + dx))
    row = int(round(center_row + dy))

    col = max(0, min(width - 1, col))
    row = max(0, min(height - 1, row))
    return GridPoint(col=col, row=row)


def plot_aircraft_positions(
    aircraft: list[tuple[float, float]],
    radius_km: float,
    width: int,
    height: int,
) -> list[GridPoint]:
    """Map ``(distance_km, bearing_deg)`` pairs to grid points, skipping invalid."""
    points: list[GridPoint] = []
    for distance_km, bearing_deg in aircraft:
        point = radar_to_grid(distance_km, bearing_deg, radius_km, width, height)
        if point is not None:
            points.append(point)
    return points
