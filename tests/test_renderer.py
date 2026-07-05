"""Tests for terminal renderer."""

from termradar.core.models import Aircraft, Location, RadarSnapshot
from termradar.renderers.terminal import render_snapshot


def test_render_empty_snapshot():
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=(),
    )
    text = render_snapshot(snapshot)
    assert "No aircraft within range" in text
    assert "Dadar, Mumbai" in text


def test_render_with_aircraft():
    ac = Aircraft(
        hex_id="abc",
        callsign="IGO123",
        latitude=19.02,
        longitude=72.85,
        distance_km=5.2,
        bearing_deg=45.0,
        altitude_ft=35000.0,
        ground_speed_knots=420.0,
        origin="BOM",
        destination="DEL",
    )
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=(ac,),
    )
    text = render_snapshot(snapshot)
    assert "IGO123" in text
    assert "BOM" in text
    assert "DEL" in text
