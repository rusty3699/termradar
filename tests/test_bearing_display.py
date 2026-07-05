"""Tests for compass bearing display."""

from termradar.renderers.bearing_display import bearing_to_compass, format_bearing_compass


def test_bearing_to_compass():
    assert bearing_to_compass(14) == "NNE"
    assert bearing_to_compass(72) == "ENE"
    assert bearing_to_compass(180) == "S"
    assert bearing_to_compass(245) == "WSW"


def test_format_bearing_compass():
    assert format_bearing_compass(14) == "NNE · 14°"
    assert format_bearing_compass(None) == "—"
