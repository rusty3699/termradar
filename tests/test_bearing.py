"""Tests for bearing calculations."""

import pytest

from termradar.core.bearing import bearing_deg


def test_bearing_north():
    # Point directly north
    b = bearing_deg(0.0, 0.0, 1.0, 0.0)
    assert b == pytest.approx(0.0, abs=0.1)


def test_bearing_south():
    b = bearing_deg(1.0, 0.0, 0.0, 0.0)
    assert b == pytest.approx(180.0, abs=0.1)


def test_bearing_east():
    b = bearing_deg(0.0, 0.0, 0.0, 1.0)
    assert b == pytest.approx(90.0, abs=0.1)


def test_bearing_west():
    b = bearing_deg(0.0, 1.0, 0.0, 0.0)
    assert b == pytest.approx(270.0, abs=0.1)


def test_bearing_range():
    b = bearing_deg(19.0, 72.0, 18.5, 73.0)
    assert 0.0 <= b < 360.0


def test_same_point_bearing():
    # atan2(0,0) is undefined; implementation should still return a value in range
    b = bearing_deg(10.0, 20.0, 10.0, 20.0)
    assert 0.0 <= b < 360.0
