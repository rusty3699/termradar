"""Nominatim (OpenStreetMap) geocoding provider."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode

import httpx

from termradar.core.limits import GEOCODING_MIN_INTERVAL_SECONDS
from termradar.core.models import LocationCandidate

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://nominatim.openstreetmap.org/search"
_DEFAULT_USER_AGENT = "TermRadar/0.2.0 (https://github.com/rusty3699/termradar)"
_DEFAULT_TIMEOUT = 10.0


class GeocodingError(Exception):
    """Raised when geocoding fails due to network or API issues."""


class NominatimGeocodingProvider:
    """Geocode free-text locations via the Nominatim API."""

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        user_agent: str = _DEFAULT_USER_AGENT,
        timeout: float = _DEFAULT_TIMEOUT,
        min_interval_seconds: float = GEOCODING_MIN_INTERVAL_SECONDS,
        client: httpx.Client | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._base_url = base_url
        self._user_agent = user_agent
        self._timeout = timeout
        self._min_interval_seconds = min_interval_seconds
        self._client = client
        self._owns_client = client is None
        self._clock = clock
        self._sleep = sleep
        self._last_request_at: float | None = None

    def search(self, query: str) -> list[LocationCandidate]:
        """Return location candidates for *query*."""
        query = query.strip()
        if not query:
            return []

        self._wait_for_rate_limit()
        params = urlencode(
            {
                "q": query,
                "format": "json",
                "limit": "5",
                "addressdetails": "0",
            }
        )
        url = f"{self._base_url}?{params}"
        headers = {"User-Agent": self._user_agent}

        try:
            if self._client is not None:
                response = self._client.get(url, headers=headers, timeout=self._timeout)
            else:
                with httpx.Client() as client:
                    response = client.get(url, headers=headers, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            raise GeocodingError(f"Geocoding request timed out for {query!r}") from exc
        except httpx.HTTPError as exc:
            raise GeocodingError(f"Geocoding network error for {query!r}: {exc}") from exc

        if response.status_code != 200:
            raise GeocodingError(
                f"Geocoding API returned HTTP {response.status_code} for {query!r}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise GeocodingError(f"Malformed geocoding response for {query!r}") from exc

        if not isinstance(payload, list):
            raise GeocodingError(f"Unexpected geocoding response type for {query!r}")

        candidates: list[LocationCandidate] = []
        for item in payload:
            candidate = _parse_candidate(item)
            if candidate is not None:
                candidates.append(candidate)
        return candidates

    def _wait_for_rate_limit(self) -> None:
        if self._min_interval_seconds <= 0:
            return
        now = self._clock()
        if self._last_request_at is not None:
            elapsed = now - self._last_request_at
            if elapsed < self._min_interval_seconds:
                self._sleep(self._min_interval_seconds - elapsed)
                now = self._clock()
        self._last_request_at = now

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()

    def __enter__(self) -> NominatimGeocodingProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _parse_candidate(item: Any) -> LocationCandidate | None:
    if not isinstance(item, dict):
        return None
    try:
        display_name = str(item["display_name"])
        latitude = float(item["lat"])
        longitude = float(item["lon"])
    except (KeyError, TypeError, ValueError):
        logger.debug("Skipping malformed geocoding candidate: %r", item)
        return None
    return LocationCandidate(
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
    )
