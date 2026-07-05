"""Tests for RadarEngine."""

from fakes import FakeAircraftProvider, FakeRouteProvider, make_aircraft, make_location
from termradar.core.engine import RadarEngine, RadarEngineError
from termradar.core.models import RouteInfo


def test_scan_empty_result():
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=15.0,
    )
    snapshot = engine.scan()
    assert snapshot.count == 0
    assert snapshot.nearest is None


def test_scan_filters_by_radius():
    inside = make_aircraft(hex_id="in", latitude=19.02, longitude=72.85)
    outside = make_aircraft(hex_id="out", latitude=20.5, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([inside, outside]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=15.0,
    )
    snapshot = engine.scan()
    assert snapshot.count == 1
    assert snapshot.aircraft[0].hex_id == "in"


def test_scan_sorts_nearest_first():
    far = make_aircraft(hex_id="far", latitude=19.15, longitude=72.85)
    near = make_aircraft(hex_id="near", latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([far, near]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=50.0,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].hex_id == "near"
    assert snapshot.aircraft[1].hex_id == "far"
    assert snapshot.aircraft[0].distance_km < snapshot.aircraft[1].distance_km


def test_scan_sets_distance_and_bearing():
    ac = make_aircraft(latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=50.0,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].distance_km is not None
    assert snapshot.aircraft[0].bearing_deg is not None


def test_scan_missing_callsign_still_works():
    ac = make_aircraft(callsign=None, latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=5,
    )
    snapshot = engine.scan()
    assert snapshot.count == 1
    assert snapshot.aircraft[0].origin is None


def test_scan_missing_altitude_still_works():
    ac = make_aircraft(altitude_ft=None, latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=50.0,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].altitude_ft is None


def test_scan_route_enrichment():
    ac = make_aircraft(callsign="IGO123", latitude=19.02, longitude=72.85)
    route_info = RouteInfo(origin="BOM", destination="DEL", airline="IndiGo")
    routes = FakeRouteProvider({"IGO123": route_info})
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=routes,
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.aircraft[0].origin == "BOM"
    assert snapshot.aircraft[0].destination == "DEL"
    assert snapshot.aircraft[0].airline == "IndiGo"


def test_scan_route_failure_does_not_break_scan():
    ac = make_aircraft(callsign="IGO123", latitude=19.02, longitude=72.85)
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider([ac]),
        route_provider=FakeRouteProvider(fail=True),
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=1,
    )
    snapshot = engine.scan()
    assert snapshot.count == 1
    assert snapshot.aircraft[0].origin is None


def test_enrichment_limit():
    aircraft = [
        make_aircraft(
            hex_id=f"ac{i}",
            callsign=f"FLT{i}",
            latitude=19.02 + i * 0.001,
            longitude=72.85,
        )
        for i in range(5)
    ]
    routes = FakeRouteProvider(
        {f"FLT{i}": RouteInfo(origin="AAA", destination="BBB") for i in range(2)}
    )
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider(aircraft),
        route_provider=routes,
        location=make_location(),
        radius_km=50.0,
        enrichment_limit=2,
    )
    snapshot = engine.scan()
    enriched = [ac for ac in snapshot.aircraft if ac.origin == "AAA"]
    assert len(enriched) == 2
    assert len(routes.calls) == 2


def test_provider_failure_raises_radar_engine_error():
    engine = RadarEngine(
        aircraft_provider=FakeAircraftProvider(error=RuntimeError("network down")),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=15.0,
    )
    try:
        engine.scan()
        raised = False
    except RadarEngineError:
        raised = True
    assert raised
