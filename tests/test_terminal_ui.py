"""Tests for terminal UI renderer."""

from datetime import UTC, datetime

from termradar.core.models import Aircraft, Location, RadarSnapshot
from termradar.renderers.terminal_ui import TerminalRenderer
from termradar.renderers.terminal_view import TerminalView


def _view(**kwargs) -> TerminalView:
    defaults = {
        "location_name": "Dadar, Mumbai",
        "radius_km": 15.0,
        "refresh_seconds": 5,
        "terminal_width": 80,
        "terminal_height": 24,
    }
    defaults.update(kwargs)
    return TerminalView(**defaults)


def test_no_aircraft_state():
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=(),
        scanned_at=datetime(2026, 1, 1, 12, 42, 7, tzinfo=UTC),
    )
    renderer = TerminalRenderer()
    text = renderer.render_text(_view(snapshot=snapshot, last_updated=snapshot.scanned_at))
    assert "No aircraft currently detected" in text
    assert "15 km" in text


def test_nearest_aircraft_panel():
    ac = Aircraft(
        hex_id="a",
        callsign="6E221",
        latitude=19.0,
        longitude=72.0,
        distance_km=4.2,
        bearing_deg=72.0,
        altitude_ft=8350.0,
        ground_speed_knots=287.0,
        airline="IndiGo",
        origin="DEL",
        destination="BOM",
    )
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=(ac,),
        scanned_at=datetime(2026, 1, 1, 12, 42, 7, tzinfo=UTC),
    )
    renderer = TerminalRenderer()
    text = renderer.render_text(_view(snapshot=snapshot, last_updated=snapshot.scanned_at))
    assert "6E221" in text
    assert "IndiGo" in text
    assert "DEL" in text
    assert "BOM" in text
    assert "4.2 km away" in text
    assert "ENE · 72°" in text
    assert "CLOSEST" in text
    assert "NEARBY" in text
    assert "1  6E221" in text or "1  6E221 " in text


def test_nearby_list_shows_top_five():
    aircraft = tuple(
        Aircraft(
            hex_id=f"ac{i}",
            callsign=f"FLT{i}",
            latitude=19.0 + i * 0.01,
            longitude=72.0,
            distance_km=4.0 + i,
            bearing_deg=float(i * 30),
        )
        for i in range(6)
    )
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=aircraft,
    )
    text = TerminalRenderer().render_text(_view(snapshot=snapshot))
    assert "NEARBY" in text
    assert "1  FLT0" in text
    assert "5  FLT4" in text
    assert "FLT5" not in text


def test_missing_metadata_graceful():
    ac = Aircraft(
        hex_id="abc",
        latitude=19.0,
        longitude=72.0,
        distance_km=4.2,
        bearing_deg=10.0,
    )
    snapshot = RadarSnapshot(
        location=Location("q", "Test", 0.0, 0.0),
        radius_km=15.0,
        aircraft=(ac,),
    )
    text = TerminalRenderer().render_text(_view(snapshot=snapshot))
    assert "ABC" in text or "UNKNOWN" in text.upper()
    assert "None" not in text


def test_error_state():
    text = TerminalRenderer().render_text(
        _view(
            snapshot=None,
            aircraft_error="Aircraft data temporarily unavailable.",
            last_updated=datetime(2026, 1, 1, 12, 41, 57, tzinfo=UTC),
        )
    )
    assert "unavailable" in text.lower()


def test_footer_summary():
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=10.0,
        aircraft=(),
    )
    text = TerminalRenderer().render_text(
        _view(snapshot=snapshot, refresh_seconds=5, radius_km=10.0)
    )
    assert "0 aircraft nearby" in text
    assert "radius 10 km" in text
    assert "refresh 5s" in text


def test_compact_layout_for_narrow_terminal():
    snapshot = RadarSnapshot(
        location=Location("q", "Dadar, Mumbai", 19.0, 72.0),
        radius_km=15.0,
        aircraft=(
            Aircraft(
                hex_id="a",
                callsign="6E221",
                latitude=19.0,
                longitude=72.0,
                distance_km=4.2,
                altitude_ft=8350.0,
            ),
        ),
    )
    text = TerminalRenderer().render_text(
        _view(snapshot=snapshot, terminal_width=40, terminal_height=20)
    )
    assert "6E221" in text
    assert "4.2" in text
    assert "km" in text
