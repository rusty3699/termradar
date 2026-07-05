"""ASCII radar canvas drawing."""

from __future__ import annotations

from termradar.core.models import Aircraft, RadarSnapshot
from termradar.renderers.radar_coords import GridPoint, radar_to_grid

_CENTER_CHAR = "+"
_AIRCRAFT_CHAR = "✈"
_MARKER_CHARS = frozenset("123456789✈")

_NEARBY_LIST_SIZE = 5

# Try original cell first, then nearby offsets for collision avoidance.
_PLACEMENT_OFFSETS: tuple[tuple[int, int], ...] = (
    (0, 0),
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (-1, 1),
    (1, -1),
    (-1, -1),
    (2, 0),
    (-2, 0),
    (0, 2),
    (0, -2),
)


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

    _draw_ring(grid, width, height, radius_fraction=1.0)
    _draw_ring(grid, width, height, radius_fraction=0.5)

    reserved = _reserved_cells(width, height)
    occupied: set[GridPoint] = set()

    ranks = {
        ac.hex_id: rank for rank, ac in enumerate(snapshot.aircraft[:_NEARBY_LIST_SIZE], start=1)
    }

    ranked = [ac for ac in snapshot.aircraft if ac.hex_id in ranks]
    ranked.sort(key=lambda ac: ranks[ac.hex_id])

    others = [ac for ac in snapshot.aircraft if ac.hex_id not in ranks]

    for ac in ranked:
        _place_aircraft_marker(
            grid,
            ac,
            str(ranks[ac.hex_id]),
            snapshot.radius_km,
            width,
            height,
            reserved,
            occupied,
        )

    for ac in others:
        _place_aircraft_marker(
            grid,
            ac,
            _AIRCRAFT_CHAR,
            snapshot.radius_km,
            width,
            height,
            reserved,
            occupied,
        )

    lines = ["".join(row) for row in grid]
    return _add_cardinals(lines, width, height)


def _place_aircraft_marker(
    grid: list[list[str]],
    aircraft: Aircraft,
    marker: str,
    radius_km: float,
    width: int,
    height: int,
    reserved: set[GridPoint],
    occupied: set[GridPoint],
) -> None:
    if aircraft.distance_km is None or aircraft.bearing_deg is None:
        return

    ideal = radar_to_grid(
        aircraft.distance_km,
        aircraft.bearing_deg,
        radius_km,
        width,
        height,
    )
    if ideal is None:
        return

    for dc, dr in _PLACEMENT_OFFSETS:
        point = GridPoint(ideal.col + dc, ideal.row + dr)
        if not _can_place_marker(grid, point, reserved, occupied, width, height):
            continue
        grid[point.row][point.col] = marker
        occupied.add(point)
        return


def _can_place_marker(
    grid: list[list[str]],
    point: GridPoint,
    reserved: set[GridPoint],
    occupied: set[GridPoint],
    width: int,
    height: int,
) -> bool:
    if point in reserved or point in occupied:
        return False
    if not (0 <= point.col < width and 0 <= point.row < height):
        return False
    char = grid[point.row][point.col]
    if char in _MARKER_CHARS:
        return False
    return char in {" ", "."}


def _reserved_cells(width: int, height: int) -> set[GridPoint]:
    cx = width // 2
    cy = height // 2
    reserved = {GridPoint(cx, cy)}
    if height >= 3:
        reserved.add(GridPoint(cx, 0))
        reserved.add(GridPoint(cx, height - 1))
    if width >= 3:
        reserved.add(GridPoint(0, cy))
        reserved.add(GridPoint(width - 1, cy))
    return reserved


def _empty_grid(width: int, height: int) -> list[list[str]]:
    return [[" " for _ in range(width)] for _ in range(height)]


def _draw_ring(
    grid: list[list[str]],
    width: int,
    height: int,
    *,
    radius_fraction: float,
) -> None:
    cx = width // 2
    cy = height // 2
    rx = max(1, (width - 1) // 2 - 1) * radius_fraction
    ry = max(1, (height - 1) // 2 - 1) * radius_fraction
    tolerance = 0.12 if radius_fraction >= 0.99 else 0.10

    for col in range(width):
        for row in range(height):
            if grid[row][col] not in {" ", "."}:
                continue
            nx = (col - cx) / rx if rx else 0.0
            ny = (row - cy) / ry if ry else 0.0
            dist = nx * nx + ny * ny
            if (1.0 - tolerance) <= dist <= (1.0 + tolerance):
                grid[row][col] = "."


def _add_cardinals(lines: list[str], width: int, height: int) -> list[str]:
    cx = width // 2
    result = list(lines)
    if height >= 3:
        top = list(result[0])
        top[cx] = "N"
        if height > 3 and result[1][cx] == ".":
            row_below = list(result[1])
            row_below[cx] = " "
            result[1] = "".join(row_below)
        result[0] = "".join(top)

        bottom = list(result[-1])
        bottom[cx] = "S"
        if height > 3 and result[-2][cx] == ".":
            row_above = list(result[-2])
            row_above[cx] = " "
            result[-2] = "".join(row_above)
        result[-1] = "".join(bottom)

    if width >= 3:
        mid = height // 2
        row = list(result[mid])
        if row[1] == ".":
            row[1] = " "
        row[0] = "W"
        if row[-2] == ".":
            row[-2] = " "
        row[-1] = "E"
        result[mid] = "".join(row)
    return result
