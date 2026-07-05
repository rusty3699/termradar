"""Tests for callsign airline inference."""

from fakes import FakeAircraftProvider, FakeRouteProvider, make_aircraft, make_location
from termradar.core.airline import infer_airline_from_callsign
from termradar.core.engine import RadarEngine
from termradar.core.models import RouteInfo


def test_infer_airline_from_callsign_prefixes():
    assert infer_airline_from_callsign("AIC8MZ") == "Air India"
    assert infer_airline_from_callsign("IGO6224") == "IndiGo"
    assert infer_airline_from_callsign("AKJ903U") == "Akasa Air"
    assert infer_airline_from_callsign("XYZ123") is None
    assert infer_airline_from_callsign(None) is None


def test_enrichment_uses_callsign_airline_when_route_missing():
    ac = make_aircraft(callsign="AIC8MZ", latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].airline == "Air India"
    assert snapshot.aircraft[0].origin is None
    assert snapshot.aircraft[0].destination is None


def test_enrichment_uses_callsign_airline_when_route_lookup_fails():
    ac = make_aircraft(callsign="IGO123", latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(fail=True),
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].airline == "IndiGo"
    assert snapshot.aircraft[0].origin is None


def test_enrichment_route_airline_takes_precedence_over_callsign():
    ac = make_aircraft(callsign="IGO123", latitude=19.02, longitude=72.85)
    routes = FakeRouteProvider(
        {"IGO123": RouteInfo(origin="BOM", destination="DEL", airline="IndiGo Cargo")}
    )
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=routes,
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].airline == "IndiGo Cargo"
    assert snapshot.aircraft[0].origin == "BOM"


def test_enrichment_route_without_airline_uses_callsign():
    ac = make_aircraft(callsign="AKJ903U", latitude=19.02, longitude=72.85)
    routes = FakeRouteProvider({"AKJ903U": RouteInfo(origin="BOM", destination="BLR")})
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=routes,
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].airline == "Akasa Air"
    assert snapshot.aircraft[0].origin == "BOM"
    assert snapshot.aircraft[0].destination == "BLR"
