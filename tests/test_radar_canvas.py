"""Tests for radar canvas rendering."""

from datetime import UTC, datetime

from termradar.core.models import Aircraft, Location, RadarSnapshot
from termradar.renderers.radar_canvas import build_radar_canvas


def _snapshot(aircraft: tuple[Aircraft, ...], radius_km: float = 15.0) -> RadarSnapshot:
    return RadarSnapshot(
        location=Location("q", "Test", 19.0, 72.0),
        radius_km=radius_km,
        aircraft=aircraft,
        scanned_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    )


def test_empty_snapshot_renders_center():
    lines = build_radar_canvas(_snapshot(()), width=21, height=11)
    joined = "\n".join(lines)
    assert "+" in joined
    assert "N" in joined
    assert "✈" not in joined


def test_single_aircraft_marker():
    ac = Aircraft(
        hex_id="a",
        latitude=19.1,
        longitude=72.0,
        distance_km=10.0,
        bearing_deg=0.0,
    )
    lines = build_radar_canvas(_snapshot((ac,)), width=21, height=11)
    assert any("1" in line for line in lines)


def test_out_of_radius_not_plotted():
    ac = Aircraft(
        hex_id="a",
        latitude=20.0,
        longitude=72.0,
        distance_km=20.0,
        bearing_deg=90.0,
    )
    lines = build_radar_canvas(_snapshot((ac,), radius_km=15.0), width=21, height=11)
    assert "✈" not in "\n".join(lines)


def test_overlapping_aircraft_do_not_crash():
    aircraft = tuple(
        Aircraft(
            hex_id=f"a{i}",
            latitude=19.0,
            longitude=72.0,
            distance_km=5.0,
            bearing_deg=0.0,
        )
        for i in range(5)
    )
    lines = build_radar_canvas(_snapshot(aircraft), width=21, height=11)
    assert len(lines) == 11
    joined = "\n".join(lines)
    for marker in ("1", "2", "3", "4", "5"):
        assert marker in joined


def test_cardinals_are_not_adjacent_to_ring_dots():
    lines = build_radar_canvas(_snapshot(()), width=31, height=15)
    mid = lines[len(lines) // 2]
    assert mid.startswith("W ")
    assert mid.endswith(" E")


def test_top_five_aircraft_use_numbered_markers():
    aircraft = tuple(
        Aircraft(
            hex_id=f"a{i}",
            latitude=19.0 + i * 0.05,
            longitude=72.0,
            distance_km=float(i + 1),
            bearing_deg=45.0 + i * 20,
        )
        for i in range(3)
    )
    lines = build_radar_canvas(_snapshot(aircraft), width=31, height=15)
    joined = "\n".join(lines)
    assert "1" in joined
    assert "2" in joined
    assert "3" in joined


def test_marker_placed_on_ring_dot_cell():
    """Aircraft mapped to a ring dot should still receive a visible marker."""
    ac = Aircraft(
        hex_id="a1",
        latitude=19.1,
        longitude=72.0,
        distance_km=7.5,
        bearing_deg=0.0,
    )
    lines = build_radar_canvas(_snapshot((ac,)), width=31, height=15)
    assert any("1" in line for line in lines)


def test_all_top_five_markers_visible_when_clustered():
    aircraft = tuple(
        Aircraft(
            hex_id=f"a{i}",
            latitude=19.0,
            longitude=72.0,
            distance_km=8.0 + i * 0.5,
            bearing_deg=2.0 + i * 3.0,
        )
        for i in range(5)
    )
    lines = build_radar_canvas(_snapshot(aircraft), width=31, height=15)
    joined = "\n".join(lines)
    for marker in ("1", "2", "3", "4", "5"):
        assert marker in joined


def test_center_mapped_aircraft_uses_offset():
    ac = Aircraft(
        hex_id="a1",
        latitude=19.0,
        longitude=72.0,
        distance_km=0.1,
        bearing_deg=0.0,
    )
    lines = build_radar_canvas(_snapshot((ac,)), width=31, height=15)
    assert any("1" in line for line in lines)
    mid = lines[len(lines) // 2]
    assert "+" in mid
