"""Tests for location timezone resolution."""

from termradar.core.location import ensure_location_timezone
from termradar.core.models import Location
from termradar.core.timezone import resolve_timezone


def test_resolve_timezone_mumbai():
    tz = resolve_timezone(19.02, 72.85)
    assert tz == "Asia/Kolkata"


def test_ensure_location_timezone_populates_missing():
    location = Location(
        query="test",
        display_name="Mumbai",
        latitude=19.02,
        longitude=72.85,
    )
    updated = ensure_location_timezone(location)
    assert updated.timezone == "Asia/Kolkata"
