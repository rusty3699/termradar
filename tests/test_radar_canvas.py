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
    assert any("✈" in line for line in lines)


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
