"""ASCII radar canvas drawing."""

from __future__ import annotations

from termradar.core.models import RadarSnapshot
from termradar.renderers.radar_coords import GridPoint, radar_to_grid

_CENTER_CHAR = "+"
_AIRCRAFT_CHAR = "✈"


def build_radar_canvas(
    snapshot: RadarSnapshot,
    width: int = 31,
    height: int = 15,
) -> list[str]:
    """Return radar canvas lines with aircraft markers."""
    width = max(11, width)
    height = max(9, height)

    grid = _empty_grid(width, height)
    center = GridPoint(col=width // 2, row=height // 2)
    grid[center.row][center.col] = _CENTER_CHAR

    _draw_ring(grid, width, height)

    occupied: set[GridPoint] = {center}
    for ac in snapshot.aircraft:
        if ac.distance_km is None or ac.bearing_deg is None:
            continue
        point = radar_to_grid(
            ac.distance_km,
            ac.bearing_deg,
            snapshot.radius_km,
            width,
            height,
        )
        if point is None or point == center:
            continue
        if point in occupied:
            continue
        if _is_structural(grid, point):
            continue
        grid[point.row][point.col] = _AIRCRAFT_CHAR
        occupied.add(point)

    lines = ["".join(row) for row in grid]
    return _add_cardinals(lines, width, height)


def _empty_grid(width: int, height: int) -> list[list[str]]:
    return [[" " for _ in range(width)] for _ in range(height)]


def _draw_ring(grid: list[list[str]], width: int, height: int) -> None:
    cx = width // 2
    cy = height // 2
    rx = max(1, (width - 1) // 2 - 1)
    ry = max(1, (height - 1) // 2 - 1)

    for col in range(width):
        for row in range(height):
            if grid[row][col] != " ":
                continue
            nx = (col - cx) / rx if rx else 0.0
            ny = (row - cy) / ry if ry else 0.0
            dist = nx * nx + ny * ny
            if 0.85 <= dist <= 1.15:
                grid[row][col] = "."


def _is_structural(grid: list[list[str]], point: GridPoint) -> bool:
    char = grid[point.row][point.col]
    return char in {".", "'", "-", _CENTER_CHAR}


def _add_cardinals(lines: list[str], width: int, height: int) -> list[str]:
    cx = width // 2
    result = list(lines)
    if height >= 3:
        row = [c for c in result[0]]
        row[cx] = "N"
        result[0] = "".join(row)
        row = [c for c in result[-1]]
        row[cx] = "S"
        result[-1] = "".join(row)
    if width >= 3:
        mid = height // 2
        row = list(result[mid])
        row[0] = "W"
        row[-1] = "E"
        result[mid] = "".join(row)
    return result
