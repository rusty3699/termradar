"""Tests for radar coordinate mapping."""

from termradar.renderers.radar_coords import radar_to_grid


def test_north_at_edge():
    point = radar_to_grid(15.0, 0.0, 15.0, 21, 15)
    assert point is not None
    assert point.col == 10
    assert point.row < 7


def test_south_at_edge():
    point = radar_to_grid(15.0, 180.0, 15.0, 21, 15)
    assert point is not None
    assert point.row > 7


def test_east_at_edge():
    point = radar_to_grid(15.0, 90.0, 15.0, 21, 15)
    assert point is not None
    assert point.col > 10


def test_west_at_edge():
    point = radar_to_grid(15.0, 270.0, 15.0, 21, 15)
    assert point is not None
    assert point.col < 10


def test_near_center():
    point = radar_to_grid(0.5, 45.0, 15.0, 21, 15)
    assert point is not None
    assert abs(point.col - 10) <= 2
    assert abs(point.row - 7) <= 2


def test_out_of_radius_excluded():
    assert radar_to_grid(20.0, 90.0, 15.0, 21, 15) is None


def test_zero_radius_invalid():
    assert radar_to_grid(1.0, 0.0, 0.0, 21, 15) is None


def test_small_dimensions():
    point = radar_to_grid(5.0, 0.0, 15.0, 11, 9)
    assert point is not None


def test_too_small_grid():
    assert radar_to_grid(5.0, 0.0, 15.0, 2, 2) is None


def test_bearing_wraps():
    north_a = radar_to_grid(10.0, 0.0, 15.0, 21, 15)
    north_b = radar_to_grid(10.0, 360.0, 15.0, 21, 15)
    assert north_a == north_b


def test_output_within_bounds():
    point = radar_to_grid(12.0, 123.0, 15.0, 21, 15)
    assert point is not None
    assert 0 <= point.col < 21
    assert 0 <= point.row < 15
