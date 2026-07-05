"""Provider protocol definitions."""

from __future__ import annotations

from typing import Protocol

from termradar.core.models import Aircraft, LocationCandidate, RouteInfo


class GeocodingProvider(Protocol):
    """Resolve free-text place names to geographic coordinates."""

    def search(self, query: str) -> list[LocationCandidate]:
        """Return ranked location candidates for *query*."""
        ...


class AircraftProvider(Protocol):
    """Fetch nearby aircraft for a geographic area."""

    def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> list[Aircraft]:
        """Return aircraft within *radius_km* of the given point."""
        ...


class RouteProvider(Protocol):
    """Look up route metadata for a flight callsign."""

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        """Return route info for *callsign*, or ``None`` if unknown."""
        ...
