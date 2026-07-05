"""Provider-independent domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class Location:
    """A resolved geographic point used as the radar center."""

    query: str
    display_name: str
    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class LocationCandidate:
    """A geocoding search result awaiting user selection."""

    display_name: str
    latitude: float
    longitude: float


@dataclass(slots=True)
class RouteInfo:
    """Flight route metadata for a callsign."""

    origin: str | None = None
    destination: str | None = None
    airline: str | None = None


@dataclass(slots=True)
class Aircraft:
    """Normalized aircraft state independent of any external API."""

    hex_id: str
    latitude: float
    longitude: float
    callsign: str | None = None
    altitude_ft: float | None = None
    ground_speed_knots: float | None = None
    track_deg: float | None = None
    distance_km: float | None = None
    bearing_deg: float | None = None
    registration: str | None = None
    aircraft_type: str | None = None
    airline: str | None = None
    origin: str | None = None
    destination: str | None = None


@dataclass(frozen=True, slots=True)
class RadarSnapshot:
    """Immutable result of a single radar scan."""

    location: Location
    radius_km: float
    aircraft: tuple[Aircraft, ...]
    scanned_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def count(self) -> int:
        return len(self.aircraft)

    @property
    def nearest(self) -> Aircraft | None:
        return self.aircraft[0] if self.aircraft else None
