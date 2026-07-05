"""Tests for domain models."""

from datetime import UTC, datetime

from termradar.core.models import Aircraft, Location, RadarSnapshot


def test_aircraft_optional_fields_default_to_none():
    ac = Aircraft(hex_id="abc", latitude=1.0, longitude=2.0)
    assert ac.callsign is None
    assert ac.altitude_ft is None
    assert ac.origin is None
    assert ac.destination is None
    assert ac.airline is None


def test_radar_snapshot_nearest():
    location = Location("q", "display", 0.0, 0.0)
    near = Aircraft(hex_id="a", latitude=0.01, longitude=0.0, distance_km=1.0)
    far = Aircraft(hex_id="b", latitude=0.1, longitude=0.0, distance_km=10.0)
    snapshot = RadarSnapshot(location=location, radius_km=15.0, aircraft=(near, far))
    assert snapshot.count == 2
    assert snapshot.nearest is near


def test_radar_snapshot_empty():
    location = Location("q", "display", 0.0, 0.0)
    snapshot = RadarSnapshot(location=location, radius_km=15.0, aircraft=())
    assert snapshot.count == 0
    assert snapshot.nearest is None


def test_radar_snapshot_has_timestamp():
    location = Location("q", "display", 0.0, 0.0)
    ts = datetime(2026, 1, 1, tzinfo=UTC)
    snapshot = RadarSnapshot(location=location, radius_km=15.0, aircraft=(), scanned_at=ts)
    assert snapshot.scanned_at == ts
