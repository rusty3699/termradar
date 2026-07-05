"""TermRadar command-line interface."""

from __future__ import annotations

import argparse
from contextlib import suppress

from rich.console import Console

from termradar.config.storage import (
    AppConfig,
    ConfigError,
    RadarSettings,
    load_config,
    save_config,
    validate_radius_km,
    validate_refresh_seconds,
)
from termradar.core.engine import RadarEngine
from termradar.core.models import Location
from termradar.providers.aircraft import OpenSkyAircraftProvider
from termradar.providers.geocoding import GeocodingError, NominatimGeocodingProvider
from termradar.providers.routes import AdsbLolRouteProvider, CachedRouteProvider
from termradar.session import RadarSession

_DEFAULT_RADIUS_KM = 15.0
_DEFAULT_REFRESH_SECONDS = 5
_DEFAULT_ENRICHMENT_LIMIT = 10


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``termradar`` CLI."""
    args = _parse_args(argv)
    console = Console()

    try:
        config = load_config()
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        console.print("Run [bold]termradar --reset-location[/bold] to reconfigure.")
        return 1

    if args.reset_location or config.location is None:
        config = _run_onboarding(config, console)
        if config.location is None:
            console.print("[red]No location configured. Exiting.[/red]")
            return 1

    location = config.location
    assert location is not None

    if args.location:
        override = _resolve_location_override(args.location, console)
        if override is None:
            return 1
        location = override

    try:
        radius_km = validate_radius_km(
            args.radius if args.radius is not None else config.radar.radius_km
        )
        refresh_seconds = validate_refresh_seconds(
            args.refresh if args.refresh is not None else config.radar.refresh_seconds
        )
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1

    route_provider = CachedRouteProvider(AdsbLolRouteProvider())
    engine = RadarEngine(
        aircraft_provider=OpenSkyAircraftProvider(),
        route_provider=route_provider,
        location=location,
        radius_km=radius_km,
        enrichment_limit=args.enrichment_limit,
    )

    session = RadarSession(engine, refresh_seconds=refresh_seconds)
    with suppress(KeyboardInterrupt):
        session.run(console)

    console.print("\n[dim]TermRadar stopped.[/dim]")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="termradar",
        description="Live aircraft radar for your terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See what's flying above you.",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=None,
        metavar="TEXT",
        help="Temporary radar location override (does not change saved config)",
    )
    parser.add_argument(
        "--radius",
        "--radius-km",
        type=float,
        dest="radius",
        default=None,
        metavar="KM",
        help="Search radius in kilometres for this run only",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Refresh interval in seconds for this run only",
    )
    parser.add_argument(
        "--enrichment-limit",
        type=int,
        default=_DEFAULT_ENRICHMENT_LIMIT,
        help="Maximum nearest aircraft to enrich with route data",
    )
    parser.add_argument(
        "--reset-location",
        action="store_true",
        help="Re-run location onboarding and update saved config",
    )
    return parser.parse_args(argv)


def _run_onboarding(config: AppConfig, console: Console) -> AppConfig:
    console.print("[bold cyan]✈ Welcome to TermRadar[/bold cyan]")
    console.print()
    console.print("See what's flying above you.")
    console.print()
    console.print("Where should we center your radar?")
    console.print()

    query = _prompt("Location: ").strip()
    if not query:
        console.print("[red]Location cannot be empty.[/red]")
        return config

    console.print("\n[dim]Searching for locations...[/dim]")
    geocoder = NominatimGeocodingProvider()
    try:
        candidates = geocoder.search(query)
    except GeocodingError as exc:
        console.print(f"[red]Geocoding failed:[/red] {exc}")
        return config

    if not candidates:
        console.print(f"[red]No results found for {query!r}.[/red]")
        return config

    selected = _choose_candidate(candidates, console)
    if selected is None:
        return config

    radius_input = _prompt(f"Search radius [{_DEFAULT_RADIUS_KM:.0f} km]: ").strip()
    try:
        radius_km = validate_radius_km(float(radius_input)) if radius_input else _DEFAULT_RADIUS_KM
    except (ConfigError, ValueError):
        console.print(f"[yellow]Invalid radius, using {_DEFAULT_RADIUS_KM:.0f} km.[/yellow]")
        radius_km = _DEFAULT_RADIUS_KM

    refresh_input = _prompt(f"Refresh interval [{_DEFAULT_REFRESH_SECONDS} seconds]: ").strip()
    try:
        refresh_seconds = (
            validate_refresh_seconds(int(refresh_input))
            if refresh_input
            else _DEFAULT_REFRESH_SECONDS
        )
    except (ConfigError, ValueError):
        console.print(
            f"[yellow]Invalid refresh interval, using {_DEFAULT_REFRESH_SECONDS} seconds.[/yellow]"
        )
        refresh_seconds = _DEFAULT_REFRESH_SECONDS

    location = Location(
        query=query,
        display_name=selected.display_name,
        latitude=selected.latitude,
        longitude=selected.longitude,
    )

    config.location = location
    config.radar = RadarSettings(radius_km=radius_km, refresh_seconds=refresh_seconds)
    save_config(config)
    console.print()
    console.print("[green]Configuration saved.[/green]")
    console.print()
    console.print("[bold]Starting radar...[/bold]")
    console.print()
    return config


def _resolve_location_override(query: str, console: Console) -> Location | None:
    console.print(f"[dim]Resolving temporary location: {query}[/dim]")
    geocoder = NominatimGeocodingProvider()
    try:
        candidates = geocoder.search(query)
    except GeocodingError as exc:
        console.print(f"[red]Geocoding failed:[/red] {exc}")
        return None

    if not candidates:
        console.print(f"[red]No results found for {query!r}.[/red]")
        return None

    if len(candidates) == 1:
        selected = candidates[0]
    else:
        selected = _choose_candidate(candidates, console)
        if selected is None:
            return None

    return Location(
        query=query,
        display_name=selected.display_name,
        latitude=selected.latitude,
        longitude=selected.longitude,
    )


def _choose_candidate(candidates: list, console: Console) -> object | None:
    if len(candidates) == 1:
        console.print(f"1. {candidates[0].display_name}")
        choice = _prompt("Choose [1]: ").strip()
        if choice and choice != "1":
            console.print("[red]Invalid choice.[/red]")
            return None
        return candidates[0]

    for index, candidate in enumerate(candidates, start=1):
        console.print(f"{index}. {candidate.display_name}")

    while True:
        choice = _prompt("Choose [1]: ").strip() or "1"
        try:
            selected_index = int(choice)
        except ValueError:
            console.print("[red]Enter a number.[/red]")
            continue
        if 1 <= selected_index <= len(candidates):
            return candidates[selected_index - 1]
        console.print(f"[red]Choose between 1 and {len(candidates)}.[/red]")


def _prompt(message: str) -> str:
    try:
        return input(message)
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(130) from None
