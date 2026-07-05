"""Configuration loading and persistence."""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w
from platformdirs import user_config_dir

from termradar.core.limits import (
    LIVE_REFRESH_DEFAULT_SECONDS,
    LIVE_REFRESH_MAX_SECONDS,
    LIVE_REFRESH_MIN_SECONDS,
)
from termradar.core.location import ensure_location_timezone
from termradar.core.models import Location

logger = logging.getLogger(__name__)

_APP_NAME = "termradar"
_DEFAULT_RADIUS_KM = 15.0
_DEFAULT_REFRESH_SECONDS = LIVE_REFRESH_DEFAULT_SECONDS
_MIN_RADIUS_KM = 1.0
_MAX_RADIUS_KM = 250.0
_MIN_REFRESH_SECONDS = LIVE_REFRESH_MIN_SECONDS
_MAX_REFRESH_SECONDS = LIVE_REFRESH_MAX_SECONDS


class ConfigError(Exception):
    """Raised when configuration cannot be loaded or validated."""


@dataclass(slots=True)
class RadarSettings:
    radius_km: float = _DEFAULT_RADIUS_KM
    refresh_seconds: int = _DEFAULT_REFRESH_SECONDS


@dataclass(slots=True)
class AppConfig:
    location: Location | None = None
    radar: RadarSettings = field(default_factory=RadarSettings)


def config_path() -> Path:
    """Return the platform-appropriate config file path."""
    return Path(user_config_dir(_APP_NAME)) / "config.toml"


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from disk, returning defaults for a missing file."""
    path = path or config_path()
    if not path.exists():
        return AppConfig()

    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        logger.warning("Could not read config at %s: %s", path, exc)
        raise ConfigError(f"Corrupted or unreadable config: {path}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Config root must be a table")

    location = _parse_location(data.get("location"))
    radar = _parse_radar(data.get("radar"))
    config = AppConfig(location=location, radar=radar)
    _migrate_legacy_refresh(path, data, config)
    return config


def save_config(config: AppConfig, path: Path | None = None) -> None:
    """Persist configuration to disk."""
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data: dict = {
        "radar": {
            "radius_km": config.radar.radius_km,
            "refresh_seconds": config.radar.refresh_seconds,
        }
    }

    if config.location is not None:
        data["location"] = {
            "query": config.location.query,
            "display_name": config.location.display_name,
            "latitude": config.location.latitude,
            "longitude": config.location.longitude,
        }
        if config.location.timezone:
            data["location"]["timezone"] = config.location.timezone

    with path.open("wb") as fh:
        tomli_w.dump(data, fh)


def validate_radius_km(value: float) -> float:
    """Validate and return a radar search radius in kilometres."""
    if not (_MIN_RADIUS_KM <= value <= _MAX_RADIUS_KM):
        raise ConfigError(
            f"radius_km must be between {_MIN_RADIUS_KM} and {_MAX_RADIUS_KM}, got {value}"
        )
    return value


def validate_refresh_seconds(value: int) -> int:
    """Validate and return a refresh interval in seconds."""
    if value < _MIN_REFRESH_SECONDS:
        raise ConfigError(f"refresh interval must be at least {_MIN_REFRESH_SECONDS} seconds.")
    if value > _MAX_REFRESH_SECONDS:
        raise ConfigError(
            f"refresh_seconds must be between {_MIN_REFRESH_SECONDS} "
            f"and {_MAX_REFRESH_SECONDS}, got {value}"
        )
    return value


def _migrate_legacy_refresh(path: Path, data: dict, config: AppConfig) -> None:
    """Persist an upgraded refresh interval when an old config used a value below the minimum."""
    radar_data = data.get("radar")
    if not isinstance(radar_data, dict) or "refresh_seconds" not in radar_data:
        return
    try:
        saved = int(radar_data["refresh_seconds"])
    except (TypeError, ValueError):
        return
    if saved < _MIN_REFRESH_SECONDS:
        save_config(config, path)


def _parse_location(data: object) -> Location | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ConfigError("[location] must be a table")

    try:
        query = str(data["query"])
        display_name = str(data["display_name"])
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError("Incomplete [location] section") from exc

    if not (-90.0 <= latitude <= 90.0):
        raise ConfigError(f"Invalid latitude: {latitude}")
    if not (-180.0 <= longitude <= 180.0):
        raise ConfigError(f"Invalid longitude: {longitude}")

    timezone = data.get("timezone")
    timezone_str = str(timezone).strip() if timezone else None

    location = Location(
        query=query,
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_str,
    )
    return ensure_location_timezone(location)


def _parse_radar(data: object) -> RadarSettings:
    if data is None:
        return RadarSettings()
    if not isinstance(data, dict):
        raise ConfigError("[radar] must be a table")

    radius = _DEFAULT_RADIUS_KM
    refresh = _DEFAULT_REFRESH_SECONDS

    if "radius_km" in data:
        try:
            radius = validate_radius_km(float(data["radius_km"]))
        except (TypeError, ValueError) as exc:
            raise ConfigError("Invalid radius_km in [radar]") from exc

    if "refresh_seconds" in data:
        try:
            refresh = _coerce_refresh_seconds(int(data["refresh_seconds"]))
        except (TypeError, ValueError) as exc:
            raise ConfigError("Invalid refresh_seconds in [radar]") from exc

    return RadarSettings(radius_km=radius, refresh_seconds=refresh)


def _coerce_refresh_seconds(value: int) -> int:
    """Load saved refresh values, upgrading legacy intervals below the minimum."""
    if value < _MIN_REFRESH_SECONDS:
        logger.warning(
            "Saved refresh_seconds=%s is below the minimum %s; using %s instead",
            value,
            _MIN_REFRESH_SECONDS,
            _DEFAULT_REFRESH_SECONDS,
        )
        return _DEFAULT_REFRESH_SECONDS
    if value > _MAX_REFRESH_SECONDS:
        raise ConfigError(
            f"refresh_seconds must be between {_MIN_REFRESH_SECONDS} "
            f"and {_MAX_REFRESH_SECONDS}, got {value}"
        )
    return value
