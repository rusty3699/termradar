"""ADSBDB route and airline enrichment provider."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import httpx

from termradar.core.models import RouteInfo
from termradar.providers.routes import RouteLookup

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.adsbdb.com"
_DEFAULT_TIMEOUT = 10.0
_USER_AGENT = "TermRadar/0.2.0 (https://github.com/rusty3699/termradar)"


class AdsbDbRouteProvider(RouteLookup):
    """Look up routes and airline metadata via the ADSBDB API."""

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        callsign = callsign.strip().upper()
        if not callsign:
            return None

        if hex_id:
            path = f"/v0/aircraft/{quote(hex_id.strip().upper())}?callsign={quote(callsign)}"
        else:
            path = f"/v0/callsign/{quote(callsign)}"

        try:
            response = self._request(path)
        except httpx.HTTPError:
            logger.warning("ADSBDB network error for %s", callsign)
            return None

        if response.status_code in (200, 404):
            payload = _try_parse_json(response)
            if payload is None:
                if response.status_code == 404:
                    logger.debug("ADSBDB no data for %s", callsign)
                else:
                    logger.warning("ADSBDB malformed JSON for %s", callsign)
                return None
            return _parse_adsbdb_payload(payload)

        logger.warning("ADSBDB HTTP %s for %s", response.status_code, callsign)
        return None

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()

    def _request(self, path: str) -> httpx.Response:
        url = f"{self._base_url}{path}"
        headers = {"User-Agent": _USER_AGENT, "Accept": "application/json"}
        if self._client is not None:
            return self._client.get(url, headers=headers, timeout=self._timeout)
        with httpx.Client() as client:
            return client.get(url, headers=headers, timeout=self._timeout)


def _try_parse_json(response: httpx.Response) -> Any | None:
    try:
        return response.json()
    except ValueError:
        return None


def _parse_adsbdb_payload(payload: Any) -> RouteInfo | None:
    if not isinstance(payload, dict):
        return None

    response = payload.get("response")
    if isinstance(response, str):
        return None
    if not isinstance(response, dict):
        return None

    route_info = _parse_flightroute(response.get("flightroute"))
    if route_info is not None:
        return route_info

    aircraft = response.get("aircraft")
    if isinstance(aircraft, dict):
        owner = _first_str(aircraft, "registered_owner")
        if owner:
            return RouteInfo(airline=owner)
    return None


def _parse_flightroute(flightroute: Any) -> RouteInfo | None:
    if not isinstance(flightroute, dict):
        return None

    origin = _parse_airport(flightroute.get("origin"))
    destination = _parse_airport(flightroute.get("destination"))

    airline_data = flightroute.get("airline")
    airline = None
    if isinstance(airline_data, dict):
        airline = _first_str(airline_data, "name")

    if not any((origin, destination, airline)):
        return None

    return RouteInfo(origin=origin, destination=destination, airline=airline)


def _parse_airport(airport: Any) -> str | None:
    if not isinstance(airport, dict):
        return None
    return _first_str(airport, "iata_code", "icao_code")


def _first_str(item: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None
