"""Central radar scan pipeline."""

from __future__ import annotations

import logging
from dataclasses import replace

from termradar.core.airline import infer_airline_from_callsign
from termradar.core.bearing import bearing_deg
from termradar.core.distance import distance_km
from termradar.core.models import Aircraft, Location, RadarSnapshot
from termradar.providers.base import AircraftProvider, RouteProvider

logger = logging.getLogger(__name__)


class RadarEngineError(Exception):
    """Raised when a radar scan cannot complete due to provider failure."""


class RadarEngine:
    """Orchestrate fetch, geometry, filtering, sorting, and enrichment."""

    def __init__(
        self,
        aircraft_provider: AircraftProvider,
        route_provider: RouteProvider,
        location: Location,
        radius_km: float,
        enrichment_limit: int = 10,
    ) -> None:
        if radius_km <= 0:
            raise ValueError("radius_km must be positive")
        if enrichment_limit < 0:
            raise ValueError("enrichment_limit must be non-negative")

        self._aircraft_provider = aircraft_provider
        self._route_provider = route_provider
        self._location = location
        self._radius_km = radius_km
        self._enrichment_limit = enrichment_limit

    @property
    def location(self) -> Location:
        return self._location

    @property
    def radius_km(self) -> float:
        return self._radius_km

    @property
    def enrichment_limit(self) -> int:
        return self._enrichment_limit

    def scan(self) -> RadarSnapshot:
        """Run a full radar scan and return a normalized snapshot."""
        try:
            raw_aircraft = self._aircraft_provider.get_nearby(
                self._location.latitude,
                self._location.longitude,
                self._radius_km,
            )
        except Exception as exc:
            raise RadarEngineError(f"Aircraft fetch failed: {exc}") from exc

        processed = self._apply_geometry(raw_aircraft)
        filtered = [
            ac
            for ac in processed
            if ac.distance_km is not None and ac.distance_km <= self._radius_km
        ]
        filtered.sort(key=lambda ac: ac.distance_km if ac.distance_km is not None else float("inf"))

        enriched = self._enrich(filtered)

        return RadarSnapshot(
            location=self._location,
            radius_km=self._radius_km,
            aircraft=tuple(enriched),
        )

    def _apply_geometry(self, aircraft: list[Aircraft]) -> list[Aircraft]:
        result: list[Aircraft] = []
        for ac in aircraft:
            dist = distance_km(
                self._location.latitude,
                self._location.longitude,
                ac.latitude,
                ac.longitude,
            )
            bear = bearing_deg(
                self._location.latitude,
                self._location.longitude,
                ac.latitude,
                ac.longitude,
            )
            result.append(
                replace(
                    ac,
                    distance_km=dist,
                    bearing_deg=bear,
                )
            )
        return result

    def _enrich(self, aircraft: list[Aircraft]) -> list[Aircraft]:
        if self._enrichment_limit == 0:
            return aircraft

        enriched: list[Aircraft] = []
        for index, ac in enumerate(aircraft):
            if index < self._enrichment_limit and ac.callsign:
                enriched.append(self._enrich_one(ac))
            else:
                enriched.append(ac)
        return enriched

    def _enrich_one(self, aircraft: Aircraft) -> Aircraft:
        assert aircraft.callsign is not None
        origin = aircraft.origin
        destination = aircraft.destination
        airline = aircraft.airline

        try:
            route = self._route_provider.lookup_route(
                aircraft.callsign,
                hex_id=aircraft.hex_id,
            )
        except Exception:
            logger.exception("Route enrichment failed for %s", aircraft.callsign)
            route = None

        if route is not None:
            origin = route.origin or origin
            destination = route.destination or destination
            airline = route.airline or airline

        if not airline:
            airline = infer_airline_from_callsign(aircraft.callsign)

        unchanged = (
            origin == aircraft.origin
            and destination == aircraft.destination
            and airline == aircraft.airline
        )
        if unchanged:
            return aircraft

        return replace(
            aircraft,
            origin=origin,
            destination=destination,
            airline=airline,
        )
