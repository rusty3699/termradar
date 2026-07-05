"""Route enrichment providers and rate-limited cache."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from termradar.core.limits import (
    ENRICHMENT_FAILURE_TTL_SECONDS,
    ENRICHMENT_REQUESTS_PER_MINUTE,
    ENRICHMENT_SUCCESS_TTL_SECONDS,
)
from termradar.core.models import RouteInfo
from termradar.core.rate_limit import MinuteRateLimiter

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.adsb.lol/api/0/routeset"
_DEFAULT_TIMEOUT = 10.0


@dataclass(slots=True)
class _CacheEntry:
    result: RouteInfo | None
    expires_at: float


class CachedRouteProvider:
    """Wrap a route provider with TTL cache and enrichment rate limits."""

    def __init__(
        self,
        provider: RouteLookup,
        *,
        requests_per_minute: int = ENRICHMENT_REQUESTS_PER_MINUTE,
        success_ttl_seconds: float = ENRICHMENT_SUCCESS_TTL_SECONDS,
        failure_ttl_seconds: float = ENRICHMENT_FAILURE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        rate_limiter: MinuteRateLimiter | None = None,
    ) -> None:
        self._provider = provider
        self._success_ttl_seconds = success_ttl_seconds
        self._failure_ttl_seconds = failure_ttl_seconds
        self._clock = clock
        self._cache: dict[str, _CacheEntry] = {}
        self._rate_limiter = rate_limiter or MinuteRateLimiter(
            requests_per_minute,
            clock=clock,
        )

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        key = callsign.strip().upper()
        if not key:
            return None

        cached = self._cache.get(key)
        if cached is not None and cached.expires_at > self._clock():
            return cached.result

        if not self._rate_limiter.allow():
            logger.debug("Enrichment rate limit reached; skipping %s", key)
            return None

        try:
            result = self._provider.lookup_route(key, hex_id=hex_id)
        except Exception:
            logger.exception("Route lookup failed for %s", key)
            result = None

        ttl = self._success_ttl_seconds if result is not None else self._failure_ttl_seconds
        self._cache[key] = _CacheEntry(
            result=result,
            expires_at=self._clock() + ttl,
        )
        return result

    def clear(self) -> None:
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


class RouteLookup:
    """Protocol-like base for route lookup implementations."""

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        raise NotImplementedError


class AdsbLolRouteProvider(RouteLookup):
    """Look up flight routes via the adsb.lol routeset API."""

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None

    def lookup_route(self, callsign: str, *, hex_id: str | None = None) -> RouteInfo | None:
        callsign = callsign.strip().upper()
        if not callsign:
            return None

        try:
            if self._client is not None:
                response = self._client.post(
                    self._base_url,
                    json=[callsign],
                    timeout=self._timeout,
                )
            else:
                with httpx.Client() as client:
                    response = client.post(
                        self._base_url,
                        json=[callsign],
                        timeout=self._timeout,
                    )
        except httpx.HTTPError:
            logger.warning("Route lookup network error for %s", callsign)
            return None

        if response.status_code not in (200, 201):
            logger.warning(
                "Route lookup HTTP %s for %s",
                response.status_code,
                callsign,
            )
            return None

        payload = _decode_route_response(response, callsign)
        if payload is None:
            return None

        return _parse_route_payload(payload, callsign)

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()


def _decode_route_response(response: httpx.Response, callsign: str) -> Any | None:
    """Decode a routeset response body.

    adsb.lol commonly returns HTTP 201 with an empty body when no route exists.
    That is expected and should not be logged as an error.
    """
    if not response.content or not response.text.strip():
        logger.debug("No route data for %s", callsign)
        return None

    try:
        return response.json()
    except ValueError:
        logger.warning(
            "Unexpected non-JSON route response for %s (%d bytes)",
            callsign,
            len(response.content),
        )
        return None


def _parse_route_payload(payload: Any, callsign: str) -> RouteInfo | None:
    if isinstance(payload, dict):
        for key in ("routes", "data", "results"):
            nested = payload.get(key)
            if isinstance(nested, list):
                payload = nested
                break
        else:
            return _parse_route_item(payload) if payload else None

    if not isinstance(payload, list) or not payload:
        return None

    for item in payload:
        if not isinstance(item, dict):
            continue
        item_callsign = item.get("callsign") or item.get("flight")
        if item_callsign and str(item_callsign).strip().upper() != callsign:
            continue
        return _parse_route_item(item)

    first = payload[0]
    if isinstance(first, dict):
        return _parse_route_item(first)
    return None


def _parse_route_item(item: dict[str, Any]) -> RouteInfo | None:
    origin = _first_str(item, "origin", "departure", "dep", "from")
    destination = _first_str(item, "destination", "arrival", "arr", "to")

    airport_codes = item.get("_airport_codes_iata") or item.get("airport_codes")
    if isinstance(airport_codes, str) and "-" in airport_codes:
        parts = airport_codes.split("-", 1)
        origin = origin or parts[0] or None
        destination = destination or (parts[1] if len(parts) > 1 else None) or None

    airline = _first_str(item, "airline", "airline_iata", "operator")

    if not any((origin, destination, airline)):
        return None

    return RouteInfo(origin=origin, destination=destination, airline=airline)


def _first_str(item: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None
