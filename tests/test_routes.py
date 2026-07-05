"""Tests for route provider and cache."""

import httpx

from termradar.providers.routes import AdsbLolRouteProvider, CachedRouteProvider


def _mock_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_route_lookup_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "callsign": "IGO123",
                    "_airport_codes_iata": "BOM-DEL",
                    "airline": "IndiGo",
                }
            ],
        )

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("IGO123")
    assert route is not None
    assert route.origin == "BOM"
    assert route.destination == "DEL"
    assert route.airline == "IndiGo"


def test_route_lookup_unknown_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("UNKNOWN") is None


def test_route_lookup_network_error_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("IGO123") is None


def test_cached_route_provider_hits_cache():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            200,
            json=[{"callsign": "IGO123", "_airport_codes_iata": "BOM-DEL"}],
        )

    inner = AdsbLolRouteProvider(client=_mock_client(handler))
    cached = CachedRouteProvider(inner)

    first = cached.lookup_route("IGO123")
    second = cached.lookup_route("IGO123")

    assert first == second
    assert first is not None
    assert first.origin == "BOM"
    assert call_count == 1
    assert cached.size == 1


def test_cached_route_provider_caches_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    inner = AdsbLolRouteProvider(client=_mock_client(handler))
    cached = CachedRouteProvider(inner)

    assert cached.lookup_route("NOPE") is None
    assert cached.lookup_route("NOPE") is None
    assert cached.size == 1
