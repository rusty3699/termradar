"""Tests for aircraft provider."""

import httpx
import pytest

from termradar.providers.aircraft import AircraftProviderError, OpenSkyAircraftProvider


def _mock_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def _sample_state(
    icao="abc123",
    callsign="IGO123 ",
    lon=72.85,
    lat=19.02,
    baro_alt=10668.0,
    velocity=230.0,
    track=90.0,
):
    return [
        icao,
        callsign,
        "India",
        None,
        None,
        lon,
        lat,
        baro_alt,
        False,
        velocity,
        track,
        None,
        None,
        None,
        None,
        False,
        0,
    ]


def test_parse_full_state():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"time": 1, "states": [_sample_state()]})

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    aircraft = provider.get_nearby(19.0, 72.8, 50.0)
    assert len(aircraft) == 1
    ac = aircraft[0]
    assert ac.hex_id == "abc123"
    assert ac.callsign == "IGO123"
    assert ac.latitude == pytest.approx(19.02)
    assert ac.longitude == pytest.approx(72.85)
    assert ac.altitude_ft == pytest.approx(10668.0 * 3.28084, rel=0.01)
    assert ac.ground_speed_knots == pytest.approx(230.0 * 1.94384, rel=0.01)
    assert ac.track_deg == pytest.approx(90.0)


def test_parse_missing_callsign_and_altitude():
    state = _sample_state(callsign=None, baro_alt=None)
    state[13] = None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"time": 1, "states": [state]})

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    aircraft = provider.get_nearby(19.0, 72.8, 50.0)
    assert aircraft[0].callsign is None
    assert aircraft[0].altitude_ft is None


def test_parse_skips_missing_position():
    state = _sample_state(lat=None, lon=None)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"time": 1, "states": [state]})

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    aircraft = provider.get_nearby(19.0, 72.8, 50.0)
    assert aircraft == []


def test_empty_states():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"time": 1, "states": None})

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    aircraft = provider.get_nearby(19.0, 72.8, 50.0)
    assert aircraft == []


def test_malformed_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json="not json")

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    with pytest.raises(AircraftProviderError):
        provider.get_nearby(19.0, 72.8, 50.0)


def test_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={})

    provider = OpenSkyAircraftProvider(client=_mock_client(handler))
    with pytest.raises(AircraftProviderError, match="500"):
        provider.get_nearby(19.0, 72.8, 50.0)
