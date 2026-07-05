"""TermRadar command-line interface."""

from __future__ import annotations

import argparse
import sys

from termradar.config.storage import (
    AppConfig,
    ConfigError,
    RadarSettings,
    load_config,
    save_config,
    validate_radius_km,
)
from termradar.core.engine import RadarEngine
from termradar.core.models import Location
from termradar.providers.aircraft import OpenSkyAircraftProvider
from termradar.providers.geocoding import GeocodingError, NominatimGeocodingProvider
from termradar.providers.routes import AdsbLolRouteProvider, CachedRouteProvider
from termradar.renderers.terminal import render_snapshot

_DEFAULT_RADIUS_KM = 15.0
_DEFAULT_ENRICHMENT_LIMIT = 10


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``termradar`` CLI."""
    args = _parse_args(argv)

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    if args.reset_location or config.location is None:
        config = _run_onboarding(config)

    if config.location is None:
        print("No location configured. Exiting.", file=sys.stderr)
        return 1

    radius_km = validate_radius_km(args.radius_km or config.radar.radius_km)

    route_provider = CachedRouteProvider(AdsbLolRouteProvider())
    engine = RadarEngine(
        aircraft_provider=OpenSkyAircraftProvider(),
        route_provider=route_provider,
        location=config.location,
        radius_km=radius_km,
        enrichment_limit=args.enrichment_limit,
    )

    try:
        snapshot = engine.scan()
    except Exception as exc:
        print(f"Scan failed: {exc}", file=sys.stderr)
        return 1

    print(render_snapshot(snapshot))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="termradar",
        description="Live aircraft radar for your terminal",
    )
    parser.add_argument(
        "--radius-km",
        type=float,
        default=None,
        help="Search radius in kilometres (overrides saved config)",
    )
    parser.add_argument(
        "--enrichment-limit",
        type=int,
        default=_DEFAULT_ENRICHMENT_LIMIT,
        help="Maximum number of nearest aircraft to enrich with route data",
    )
    parser.add_argument(
        "--reset-location",
        action="store_true",
        help="Re-run location onboarding",
    )
    return parser.parse_args(argv)


def _run_onboarding(config: AppConfig) -> AppConfig:
    print("✈ Welcome to TermRadar")
    print()
    print("Where should we center your radar?")
    print()

    query = _prompt("Location: ").strip()
    if not query:
        print("Location cannot be empty.", file=sys.stderr)
        return config

    geocoder = NominatimGeocodingProvider()
    try:
        candidates = geocoder.search(query)
    except GeocodingError as exc:
        print(f"Geocoding failed: {exc}", file=sys.stderr)
        return config

    if not candidates:
        print(f"No results found for {query!r}.", file=sys.stderr)
        return config

    selected = _choose_candidate(candidates)
    if selected is None:
        return config

    radius_input = _prompt(f"Search radius [{_DEFAULT_RADIUS_KM:.0f} km]: ").strip()
    try:
        radius_km = validate_radius_km(float(radius_input)) if radius_input else _DEFAULT_RADIUS_KM
    except (ConfigError, ValueError):
        print(f"Invalid radius, using {_DEFAULT_RADIUS_KM:.0f} km.")
        radius_km = _DEFAULT_RADIUS_KM

    location = Location(
        query=query,
        display_name=selected.display_name,
        latitude=selected.latitude,
        longitude=selected.longitude,
    )

    config.location = location
    config.radar = RadarSettings(radius_km=radius_km, refresh_seconds=config.radar.refresh_seconds)
    save_config(config)
    print()
    print(f"Saved location: {location.display_name}")
    print()
    return config


def _choose_candidate(candidates: list) -> object | None:
    if len(candidates) == 1:
        print(f"1. {candidates[0].display_name}")
        choice = _prompt("Choose [1]: ").strip()
        if choice and choice != "1":
            print("Invalid choice.", file=sys.stderr)
            return None
        return candidates[0]

    for index, candidate in enumerate(candidates, start=1):
        print(f"{index}. {candidate.display_name}")

    while True:
        choice = _prompt("Choose [1]: ").strip() or "1"
        try:
            selected_index = int(choice)
        except ValueError:
            print("Enter a number.", file=sys.stderr)
            continue
        if 1 <= selected_index <= len(candidates):
            return candidates[selected_index - 1]
        print(f"Choose between 1 and {len(candidates)}.", file=sys.stderr)


def _prompt(message: str) -> str:
    try:
        return input(message)
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(130) from None
