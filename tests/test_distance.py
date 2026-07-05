"""Tests for distance calculations."""

import math

import pytest

from termradar.core.distance import distance_km


def test_same_coordinates_zero_distance():
    assert distance_km(19.0, 72.0, 19.0, 72.0) == pytest.approx(0.0, abs=1e-9)


def test_known_distance_mumbai_pune():
    # Mumbai (~19.076) to Pune (~18.520) ≈ 120 km
    d = distance_km(19.0760, 72.8777, 18.5204, 73.8567)
    assert d == pytest.approx(120.0, rel=0.05)


def test_one_degree_latitude_approx_111_km():
    d = distance_km(0.0, 0.0, 1.0, 0.0)
    assert d == pytest.approx(111.0, rel=0.02)


def test_symmetry():
    a = distance_km(10.0, 20.0, 30.0, 40.0)
    b = distance_km(30.0, 40.0, 10.0, 20.0)
    assert a == pytest.approx(b)


def test_returns_non_negative():
    d = distance_km(-33.0, 151.0, 40.0, -74.0)
    assert d >= 0
    assert not math.isnan(d)
