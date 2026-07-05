"""Tests for display formatting helpers."""

from termradar.core.models import Aircraft
from termradar.renderers.formatting import (
    format_airline,
    format_altitude_ft,
    format_bearing_deg,
    format_callsign,
    format_distance_km,
    format_route,
    format_speed_knots,
    format_table_row,
)


def _aircraft(**kwargs) -> Aircraft:
    defaults = {"hex_id": "abc123", "latitude": 1.0, "longitude": 2.0}
    defaults.update(kwargs)
    return Aircraft(**defaults)


def test_format_callsign_missing():
    assert format_callsign(_aircraft(callsign=None)) == "ABC123"


def test_format_callsign_present():
    assert format_callsign(_aircraft(callsign=" 6E221 ")) == "6E221"


def test_format_missing_altitude_and_speed():
    ac = _aircraft(altitude_ft=None, ground_speed_knots=None)
    assert format_altitude_ft(ac.altitude_ft) == "—"
    assert format_altitude_ft(-175.0) == "ground"
    assert format_speed_knots(ac.ground_speed_knots) == "—"


def test_format_route_unavailable():
    assert format_route(_aircraft()) == "Route unavailable"


def test_format_route_present():
    ac = _aircraft(origin="DEL", destination="BOM")
    assert format_route(ac) == "DEL → BOM"


def test_format_airline_unknown():
    assert format_airline(_aircraft()) == "Unknown airline"


def test_format_airline_shortens_common_suffixes():
    ac = _aircraft(airline="IndiGo Airlines")
    assert format_airline(ac) == "IndiGo"
    ac = _aircraft(airline="British Airways")
    assert format_airline(ac) == "British Airways"


def test_format_table_row():
    ac = _aircraft(
        callsign="6E221",
        distance_km=4.2,
        altitude_ft=8350.0,
        ground_speed_knots=287.0,
        origin="DEL",
        destination="BOM",
    )
    assert format_table_row(ac) == ("6E221", "4.2 km", "8,350 ft", "287 kt", "DEL → BOM")


def test_no_none_in_formatted_output():
    ac = _aircraft(callsign=None, altitude_ft=None, ground_speed_knots=None)
    values = [
        format_callsign(ac),
        format_distance_km(ac.distance_km),
        format_altitude_ft(ac.altitude_ft),
        format_speed_knots(ac.ground_speed_knots),
        format_bearing_deg(ac.bearing_deg),
        format_route(ac),
        format_airline(ac),
    ]
    for value in values:
        assert "None" not in value
        assert "nan" not in value.lower()
