"""Tests for ADSBDB enrichment provider."""

import httpx

from termradar.providers.adsbdb import AdsbDbRouteProvider


def _mock_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def _sample_flightroute():
    return {
        "response": {
            "flightroute": {
                "callsign": "IGO251V",
                "airline": {
                    "name": "IndiGo Airlines",
                    "icao": "IGO",
                    "iata": "6E",
                },
                "origin": {
                    "iata_code": "AMD",
                    "icao_code": "VAAH",
                },
                "destination": {
                    "iata_code": "BOM",
                    "icao_code": "VABB",
                },
            }
        }
    }


def test_callsign_lookup_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/v0/callsign/IGO251V")
        return httpx.Response(200, json=_sample_flightroute())

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("IGO251V")
    assert route is not None
    assert route.airline == "IndiGo Airlines"
    assert route.origin == "AMD"
    assert route.destination == "BOM"


def test_combined_aircraft_and_callsign_lookup():
    callsign_requested = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal callsign_requested
        if request.url.path.endswith("/v0/callsign/IGO251V"):
            callsign_requested = True
        assert "/v0/aircraft/80161A" in request.url.path
        assert "callsign=IGO251V" in str(request.url)
        return httpx.Response(200, json=_sample_flightroute())

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("IGO251V", hex_id="80161a")
    assert route is not None
    assert route.origin == "AMD"
    assert not callsign_requested


def test_unknown_callsign_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "unknown callsign"})

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("SDG163") is None


def test_unknown_callsign_http_404_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"response": "unknown callsign"})

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("AIC7AB") is None


def test_unknown_aircraft_hex_falls_back_to_callsign_route():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v0/aircraft/801524" in request.url.path:
            return httpx.Response(200, json={"response": "unknown aircraft"})
        assert request.url.path.endswith("/v0/callsign/AKJ1141")
        return httpx.Response(
            200,
            json={
                "response": {
                    "flightroute": {
                        "callsign": "AKJ1141",
                        "airline": {"name": "Akasa Air"},
                        "origin": {"iata_code": "CCU"},
                        "destination": {"iata_code": "BOM"},
                    }
                }
            },
        )

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("AKJ1141", hex_id="801524")
    assert route is not None
    assert route.origin == "CCU"
    assert route.destination == "BOM"
    assert route.airline == "Akasa Air"


def test_aircraft_owner_fallback_enriched_by_callsign_route():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v0/aircraft/A3A834" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "response": {
                        "aircraft": {
                            "mode_s": "A3A834",
                            "registration": "N33480",
                            "registered_owner": "CERVA AIR LLC",
                        }
                    }
                },
            )
        assert request.url.path.endswith("/v0/callsign/N33480")
        return httpx.Response(
            200,
            json={
                "response": {
                    "flightroute": {
                        "callsign": "N33480",
                        "airline": {"name": "CERVA AIR LLC"},
                        "origin": {"iata_code": "LAX"},
                        "destination": {"iata_code": "SFO"},
                    }
                }
            },
        )

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("N33480", hex_id="A3A834")
    assert route is not None
    assert route.origin == "LAX"
    assert route.destination == "SFO"
    assert route.airline == "CERVA AIR LLC"


def test_aircraft_owner_fallback():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v0/aircraft/" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "response": {
                        "aircraft": {
                            "mode_s": "A3A834",
                            "registration": "N33480",
                            "registered_owner": "CERVA AIR LLC",
                        }
                    }
                },
            )
        return httpx.Response(200, json={"response": "unknown callsign"})

    provider = AdsbDbRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("N33480", hex_id="A3A834")
    assert route is not None
    assert route.airline == "CERVA AIR LLC"
    assert route.origin is None
