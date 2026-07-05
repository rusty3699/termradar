"""Tests for aircraft provider."""

import httpx
import pytest

from termradar.providers.aircraft import (
    AdsbLolAircraftProvider,
    AircraftProviderError,
    OpenSkyAircraftProvider,
    _radius_km_to_nm,
)


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


def _adsb_lol_item(**overrides):
    item = {
        "hex": "80161a",
        "type": "adsb_icao",
        "flight": "IGO251V ",
        "r": "VT-ABC",
        "t": "A320",
        "alt_baro": 1925,
        "gs": 136.0,
        "track": 72.5,
        "lat": 19.02,
        "lon": 72.85,
    }
    item.update(overrides)
    return item


def test_adsb_lol_parse_full_item():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/6")
        return httpx.Response(200, json={"ac": [_adsb_lol_item()], "total": 1})

    provider = AdsbLolAircraftProvider(client=_mock_client(handler))
    aircraft = provider.get_nearby(19.0, 72.8, 10.0)
    assert len(aircraft) == 1
    ac = aircraft[0]
    assert ac.hex_id == "80161a"
    assert ac.callsign == "IGO251V"
    assert ac.altitude_ft == pytest.approx(1925.0)
    assert ac.ground_speed_knots == pytest.approx(136.0)
    assert ac.track_deg == pytest.approx(72.5)
    assert ac.registration == "VT-ABC"
    assert ac.aircraft_type == "A320"


def test_adsb_lol_masks_privacy_callsign_and_ground_altitude():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"ac": [_adsb_lol_item(flight="@@@@@@@@", alt_baro="ground", gs=0.5)]},
        )

    provider = AdsbLolAircraftProvider(client=_mock_client(handler))
    ac = provider.get_nearby(19.0, 72.8, 10.0)[0]
    assert ac.callsign is None
    assert ac.altitude_ft is None


def test_adsb_lol_empty_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ac": [], "total": 0})

    provider = AdsbLolAircraftProvider(client=_mock_client(handler))
    assert provider.get_nearby(19.0, 72.8, 10.0) == []


def test_adsb_lol_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={})

    provider = AdsbLolAircraftProvider(client=_mock_client(handler))
    with pytest.raises(AircraftProviderError, match="429"):
        provider.get_nearby(19.0, 72.8, 10.0)


def test_radius_km_to_nm():
    assert _radius_km_to_nm(10.0) == 6
    assert _radius_km_to_nm(1.0) == 1
    assert _radius_km_to_nm(500.0) == 250
