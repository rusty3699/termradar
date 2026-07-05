"""Tests for geocoding provider."""

import httpx
import pytest

from termradar.providers.geocoding import GeocodingError, NominatimGeocodingProvider


def _mock_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_geocoding_one_result():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "display_name": "Baner, Pune, Maharashtra, India",
                    "lat": "18.5600",
                    "lon": "73.7800",
                }
            ],
        )

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    results = provider.search("Baner, Pune")
    assert len(results) == 1
    assert results[0].display_name == "Baner, Pune, Maharashtra, India"
    assert results[0].latitude == pytest.approx(18.56)
    assert results[0].longitude == pytest.approx(73.78)


def test_geocoding_multiple_results():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {"display_name": "Mumbai, Maharashtra, India", "lat": "19.0760", "lon": "72.8777"},
                {"display_name": "Mumbai, Florida, USA", "lat": "27.90", "lon": "-82.50"},
            ],
        )

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    results = provider.search("Mumbai")
    assert len(results) == 2


def test_geocoding_no_results():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    results = provider.search("Nowhereville XYZ")
    assert results == []


def test_geocoding_malformed_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": "not a list"})

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    with pytest.raises(GeocodingError):
        provider.search("Mumbai")


def test_geocoding_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    with pytest.raises(GeocodingError, match="timed out"):
        provider.search("Mumbai")


def test_geocoding_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json=[])

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    with pytest.raises(GeocodingError, match="503"):
        provider.search("Mumbai")


def test_geocoding_sends_user_agent():
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["ua"] = request.headers.get("User-Agent", "")
        return httpx.Response(200, json=[])

    provider = NominatimGeocodingProvider(
        client=_mock_client(handler),
        min_interval_seconds=0,
    )
    provider.search("Pune")
    assert "TermRadar" in seen["ua"]
