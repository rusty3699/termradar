"""OpenSky Network aircraft provider."""

from __future__ import annotations

import logging
import math
from typing import Any

import httpx

from termradar.core.models import Aircraft

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://opensky-network.org/api/states/all"
_DEFAULT_TIMEOUT = 15.0
_METERS_TO_FEET = 3.28084
_MS_TO_KNOTS = 1.94384


class AircraftProviderError(Exception):
    """Raised when the aircraft provider fails."""


class OpenSkyAircraftProvider:
    """Fetch live aircraft states from the OpenSky Network REST API."""

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

    def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> list[Aircraft]:
        """Return aircraft within a bounding box approximating *radius_km*."""
        lamin, lomin, lamax, lomax = _bounding_box(latitude, longitude, radius_km)
        params = {
            "lamin": lamin,
            "lomin": lomin,
            "lamax": lamax,
            "lomax": lomax,
        }

        try:
            if self._client is not None:
                response = self._client.get(self._base_url, params=params, timeout=self._timeout)
            else:
                with httpx.Client() as client:
                    response = client.get(self._base_url, params=params, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            raise AircraftProviderError("Aircraft provider request timed out") from exc
        except httpx.HTTPError as exc:
            raise AircraftProviderError(f"Aircraft provider network error: {exc}") from exc

        if response.status_code != 200:
            raise AircraftProviderError(f"Aircraft provider returned HTTP {response.status_code}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise AircraftProviderError("Malformed aircraft provider response") from exc

        return _parse_states(payload)

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()


def _bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float,
) -> tuple[float, float, float, float]:
    """Approximate a square bounding box for a circular search radius."""
    lat_delta = radius_km / 111.0
    cos_lat = math.cos(math.radians(latitude))
    lon_delta = radius_km / (111.0 * cos_lat) if cos_lat > 1e-6 else radius_km / 111.0
    return (
        latitude - lat_delta,
        longitude - lon_delta,
        latitude + lat_delta,
        longitude + lon_delta,
    )


def _parse_states(payload: Any) -> list[Aircraft]:
    if not isinstance(payload, dict):
        raise AircraftProviderError("Unexpected aircraft response structure")

    states = payload.get("states")
    if states is None:
        return []
    if not isinstance(states, list):
        raise AircraftProviderError("Unexpected aircraft states format")

    aircraft: list[Aircraft] = []
    for state in states:
        parsed = _parse_state(state)
        if parsed is not None:
            aircraft.append(parsed)
    return aircraft


def _parse_state(state: Any) -> Aircraft | None:
    if not isinstance(state, list) or len(state) < 17:
        return None

    icao24 = state[0]
    if not icao24:
        return None

    latitude = state[6]
    longitude = state[5]
    if latitude is None or longitude is None:
        return None

    callsign_raw = state[1]
    if isinstance(callsign_raw, str) and callsign_raw.strip():
        callsign = callsign_raw.strip()
    else:
        callsign = None

    altitude_m = state[7] if state[7] is not None else state[13]
    altitude_ft = altitude_m * _METERS_TO_FEET if altitude_m is not None else None

    velocity = state[9]
    ground_speed_knots = velocity * _MS_TO_KNOTS if velocity is not None else None

    track = state[10]
    track_deg = float(track) if track is not None else None

    return Aircraft(
        hex_id=str(icao24),
        callsign=callsign,
        latitude=float(latitude),
        longitude=float(longitude),
        altitude_ft=altitude_ft,
        ground_speed_knots=ground_speed_knots,
        track_deg=track_deg,
    )
