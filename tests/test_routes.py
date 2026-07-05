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


def test_route_lookup_empty_201_body_returns_none_quietly():
    """adsb.lol returns HTTP 201 with empty body when route is unknown."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, content=b"")

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("IGO6224") is None


def test_route_lookup_whitespace_body_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, content=b"   \n")

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    assert provider.lookup_route("KAC303") is None


def test_route_lookup_invalid_json_with_body_warns(caplog):
    import logging

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    with caplog.at_level(logging.WARNING):
        assert provider.lookup_route("AXB1247") is None
    assert any("non-JSON" in record.message for record in caplog.records)


def test_route_lookup_dict_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "routes": [
                    {"callsign": "IGO123", "_airport_codes_iata": "BOM-DEL", "airline": "IndiGo"}
                ]
            },
        )

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("IGO123")
    assert route is not None
    assert route.origin == "BOM"


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


def test_route_lookup_accepts_http_201():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json=[{"callsign": "IGO123", "_airport_codes_iata": "BOM-DEL"}],
        )

    provider = AdsbLolRouteProvider(client=_mock_client(handler))
    route = provider.lookup_route("IGO123")
    assert route is not None
    assert route.origin == "BOM"


def test_cached_route_provider_rate_limited_without_network_call():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            200,
            json=[{"callsign": "IGO123", "_airport_codes_iata": "BOM-DEL"}],
        )

    inner = AdsbLolRouteProvider(client=_mock_client(handler))
    clock = {"now": 0.0}
    cached = CachedRouteProvider(
        inner,
        requests_per_minute=1,
        clock=lambda: clock["now"],
    )

    assert cached.lookup_route("IGO123") is not None
    assert cached.lookup_route("IGO456") is None
    assert call_count == 1
