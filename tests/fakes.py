"""Shared test doubles and factories."""

from __future__ import annotations

from termradar.core.models import Aircraft, Location, RouteInfo


def make_location(**overrides) -> Location:
    defaults = {
        "query": "Dadar, Mumbai",
        "display_name": "Dadar, Mumbai, Maharashtra, India",
        "latitude": 19.0178,
        "longitude": 72.8478,
    }
    defaults.update(overrides)
    return Location(**defaults)


def make_aircraft(**overrides) -> Aircraft:
    defaults = {
        "hex_id": "abc123",
        "latitude": 19.05,
        "longitude": 72.85,
        "callsign": "IGO123",
        "altitude_ft": 35000.0,
        "ground_speed_knots": 450.0,
        "track_deg": 90.0,
    }
    defaults.update(overrides)
    return Aircraft(**defaults)


class FakeAircraftProvider:
    def __init__(self, aircraft: list[Aircraft] | None = None, *, error: Exception | None = None):
        self._aircraft = aircraft or []
        self._error = error

    def get_nearby(self, latitude: float, longitude: float, radius_km: float) -> list[Aircraft]:
        if self._error:
            raise self._error
        return list(self._aircraft)


class FakeRouteProvider:
    def __init__(self, routes: dict[str, RouteInfo | None] | None = None, *, fail: bool = False):
        self._routes = routes or {}
        self._fail = fail
        self.calls: list[str] = []

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        self.calls.append(callsign)
        if self._fail:
            raise RuntimeError("route provider down")
        return self._routes.get(callsign.upper())
