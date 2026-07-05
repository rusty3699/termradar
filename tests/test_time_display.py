"""Tests for local time display."""

from datetime import UTC, datetime

from termradar.renderers.time_display import format_local_time


def test_format_local_time_mumbai():
    utc = datetime(2026, 7, 5, 7, 4, 0, tzinfo=UTC)
    text = format_local_time(utc, "Asia/Kolkata")
    assert text.startswith("12:34:00")
    assert "IST" in text


def test_format_local_time_none():
    assert format_local_time(None, "Asia/Kolkata") == "—"


def test_format_local_time_without_timezone_uses_system():
    utc = datetime(2026, 7, 5, 12, 0, 0, tzinfo=UTC)
    text = format_local_time(utc, None)
    assert ":" in text
