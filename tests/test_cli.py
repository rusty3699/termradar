"""Tests for CLI argument parsing and validation."""

import pytest

from termradar.cli import _parse_args
from termradar.config.storage import (
    ConfigError,
    validate_radius_km,
    validate_refresh_seconds,
)


def test_help_flag():
    with pytest.raises(SystemExit) as exc:
        _parse_args(["--help"])
    assert exc.value.code == 0


def test_location_override_flag():
    args = _parse_args(["--location", "Baner, Pune"])
    assert args.location == "Baner, Pune"


def test_radius_override_flag():
    args = _parse_args(["--radius", "25"])
    assert args.radius == 25.0


def test_radius_km_alias():
    args = _parse_args(["--radius-km", "30"])
    assert args.radius == 30.0


def test_refresh_override_flag():
    args = _parse_args(["--refresh", "10"])
    assert args.refresh == 10


def test_invalid_negative_radius():
    with pytest.raises(ConfigError):
        validate_radius_km(-1)


def test_invalid_zero_radius():
    with pytest.raises(ConfigError):
        validate_radius_km(0)


def test_invalid_refresh_interval():
    with pytest.raises(ConfigError):
        validate_refresh_seconds(0)
