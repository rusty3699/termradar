"""Location display helpers."""

from __future__ import annotations

import re

_CITY_NAMES = (
    "Mumbai",
    "Pune",
    "Delhi",
    "New Delhi",
    "Bengaluru",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Ahmedabad",
    "Jaipur",
    "Goa",
)


def shorten_location_name(display_name: str, query: str | None = None) -> str:
    """Return a concise location label for terminal headers."""
    if query and query.strip() and len(query.strip()) <= 48:
        return query.strip()

    parts = [part.strip() for part in display_name.split(",") if part.strip()]
    if not parts:
        return display_name

    city = _find_city(parts)
    locality = _find_locality(parts, city)

    if city and locality and locality != city:
        return f"{locality}, {city}"
    if city:
        return city
    if len(parts) >= 2:
        return f"{parts[0]}, {parts[1]}"
    return parts[0]


def _find_city(parts: list[str]) -> str | None:
    for part in parts:
        for city in _CITY_NAMES:
            if city.lower() in part.lower():
                return city
    return None


def _find_locality(parts: list[str], city: str | None) -> str | None:
    for part in parts:
        if _should_skip_part(part):
            continue
        if city and city.lower() in part.lower():
            continue
        return part
    return parts[0] if parts else None


def _should_skip_part(part: str) -> bool:
    if part == "India":
        return True
    if re.fullmatch(r"\d{6}", part):
        return True
    skip_tokens = ("District", "Zone", "Ward", "Subdistrict", "Maharashtra")
    return any(token in part for token in skip_tokens)
