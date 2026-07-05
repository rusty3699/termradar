"""Tests for configuration storage."""

from pathlib import Path

import pytest

from termradar.config.storage import (
    AppConfig,
    ConfigError,
    RadarSettings,
    load_config,
    save_config,
    validate_radius_km,
    validate_refresh_seconds,
)
from termradar.core.models import Location


def test_missing_config_returns_defaults(tmp_path: Path):
    path = tmp_path / "config.toml"
    config = load_config(path)
    assert config.location is None
    assert config.radar.radius_km == 15.0
    assert config.radar.refresh_seconds == 5


def test_save_and_load_roundtrip(tmp_path: Path):
    path = tmp_path / "config.toml"
    config = AppConfig(
        location=Location(
            query="Dadar, Mumbai",
            display_name="Dadar, Mumbai, Maharashtra, India",
            latitude=19.0178,
            longitude=72.8478,
        ),
        radar=RadarSettings(radius_km=20.0, refresh_seconds=10),
    )
    save_config(config, path)
    loaded = load_config(path)
    assert loaded.location is not None
    assert loaded.location.latitude == pytest.approx(19.0178)
    assert loaded.radar.radius_km == 20.0
    assert loaded.radar.refresh_seconds == 10


def test_corrupted_config_raises(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text("not valid {{{ toml", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_incomplete_location_raises(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text('[location]\nquery = "test"\n', encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_validate_radius_km():
    assert validate_radius_km(15.0) == 15.0
    with pytest.raises(ConfigError):
        validate_radius_km(0.5)
    with pytest.raises(ConfigError):
        validate_radius_km(500.0)


def test_validate_refresh_seconds():
    assert validate_refresh_seconds(5) == 5
    with pytest.raises(ConfigError):
        validate_refresh_seconds(0)
    with pytest.raises(ConfigError):
        validate_refresh_seconds(1000)
