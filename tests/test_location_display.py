"""Tests for location display shortening."""

from termradar.renderers.location_display import shorten_location_name


def test_shorten_uses_query_when_present():
    long_name = (
        "Hindu Colony, Dadar Hindu Colony, Matunga East, F/N Ward, "
        "Mumbai Zone 2, Mumbai City District, Maharashtra, 400014, India"
    )
    assert shorten_location_name(long_name, "Dadar East, Mumbai") == "Dadar East, Mumbai"


def test_shorten_long_geocoder_name():
    long_name = (
        "Hindu Colony, Dadar Hindu Colony, Matunga East, F/N Ward, "
        "Mumbai Zone 2, Mumbai City District, Maharashtra, 400014, India"
    )
    assert shorten_location_name(long_name) == "Hindu Colony, Mumbai"
