"""Polished terminal UI using Rich."""

from __future__ import annotations

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from termradar.renderers.bearing_display import bearing_to_compass, format_bearing_compass
from termradar.renderers.formatting import (
    format_airline,
    format_altitude_ft,
    format_callsign,
    format_distance_km,
    format_route,
    format_speed_knots,
    format_table_row,
)
from termradar.renderers.location_display import shorten_location_name
from termradar.renderers.radar_canvas import build_radar_canvas
from termradar.renderers.terminal_view import TerminalView
from termradar.renderers.time_display import format_local_time

_MIN_RADAR_WIDTH = 50
_MIN_RADAR_HEIGHT = 18
_NEARBY_LIST_SIZE = 5


class TerminalRenderer:
    """Render ``TerminalView`` objects for live terminal display."""

    def render(self, view: TerminalView) -> RenderableType:
        if view.terminal_width < _MIN_RADAR_WIDTH:
            return Panel(self._compact_layout(view), title="TERMRADAR", border_style="cyan")
        return Panel(self._full_layout(view), title="TERMRADAR", border_style="cyan")

    def render_text(self, view: TerminalView) -> str:
        """Plain-text rendering for tests without ANSI codes."""
        from rich.console import Console

        console = Console(width=view.terminal_width, record=True, force_terminal=False)
        console.print(self.render(view))
        return console.export_text()

    def _display_location(self, view: TerminalView) -> str:
        return shorten_location_name(view.location_name, view.location_query)

    def _full_layout(self, view: TerminalView) -> RenderableType:
        header = self._build_header(view)
        if view.terminal_width >= 72:
            body = Table.grid(expand=True)
            body.add_column(ratio=3)
            body.add_column(ratio=2)
            body.add_row(self._build_radar_panel(view), self._build_aircraft_panel(view))
            summary = self._build_summary(view)
            return Group(header, "", body, "", summary)
        return Group(
            header,
            "",
            self._build_radar_panel(view),
            "",
            self._build_aircraft_panel(view),
            "",
            self._build_summary(view),
        )

    def _compact_layout(self, view: TerminalView) -> RenderableType:
        lines = [
            self._location_line(view),
            self._status_line(view),
            "",
            self._build_aircraft_table(view),
            "",
            self._build_summary_text(view),
        ]
        return Text("\n".join(lines))

    def _build_header(self, view: TerminalView) -> Text:
        time_str = format_local_time(view.last_updated, view.timezone)
        status = "LIVE ●" if view.is_live else "DATA UNAVAILABLE"
        if view.is_stale:
            status = "STALE ●"
        header = Text()
        header.append(f"{self._display_location(view)}\n", style="bold")
        header.append(f"{status} ", style="bold green" if view.is_live else "bold yellow")
        header.append(time_str)
        if view.aircraft_error and not view.is_live:
            header.append(f"\n{view.aircraft_error}", style="yellow")
        return header

    def _build_radar_panel(self, view: TerminalView) -> Panel:
        if view.snapshot is None:
            content = Text("Aircraft data temporarily unavailable.", style="yellow")
        elif view.snapshot.count == 0:
            content = Text(
                f"No aircraft currently detected within {view.radius_km:.0f} km.",
                style="dim",
            )
        else:
            radar_w = min(31, max(15, view.terminal_width // 3))
            radar_h = min(15, max(9, view.terminal_height // 2))
            lines = build_radar_canvas(view.snapshot, width=radar_w, height=radar_h)
            content = Text("\n".join(lines), justify="center")
        return Panel(content, title="RADAR", border_style="blue")

    def _build_aircraft_panel(self, view: TerminalView) -> Panel:
        if view.snapshot is None or view.snapshot.nearest is None:
            if view.snapshot is not None and view.snapshot.count == 0:
                text = Text(
                    f"No aircraft currently detected\nwithin {view.radius_km:.0f} km.",
                    style="dim",
                )
            else:
                text = Text("No aircraft data available.", style="dim")
            return Panel(text, title="NEARBY AIRCRAFT", border_style="green")

        ac = view.snapshot.nearest
        content = Text()
        content.append("CLOSEST\n", style="bold")
        content.append(f"{format_callsign(ac)}\n\n", style="bold cyan")
        content.append(f"{format_airline(ac)}\n")
        content.append(f"{format_route(ac)}\n\n")
        content.append(_format_closest_metrics(ac))

        nearby = view.snapshot.aircraft[:_NEARBY_LIST_SIZE]
        if nearby:
            content.append("\n\n")
            content.append("NEARBY\n", style="bold")
            for rank, listed in enumerate(nearby, start=1):
                line = _format_nearby_line(rank, listed) + "\n"
                if rank == 1:
                    content.append(line, style="bold")
                else:
                    content.append(line)

        return Panel(content, title="NEARBY AIRCRAFT", border_style="green")

    def _build_nearest_panel(self, view: TerminalView) -> Panel:
        """Backward-compatible alias for tests."""
        return self._build_aircraft_panel(view)

    def _build_aircraft_table(self, view: TerminalView) -> str:
        table = Table(
            title=f"TermRadar — {self._display_location(view)}",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold",
        )
        table.add_column("CALLSIGN")
        table.add_column("DISTANCE")
        table.add_column("ALTITUDE")
        table.add_column("SPEED")
        table.add_column("ROUTE")

        if view.snapshot is None:
            table.add_row("—", "—", "—", "—", "—")
            from rich.console import Console

            console = Console(record=True, width=view.terminal_width, force_terminal=False)
            console.print(table)
            return console.export_text()

        if not view.snapshot.aircraft:
            table.add_row("—", "—", "—", "—", "No aircraft in range")
        else:
            for ac in view.snapshot.aircraft[:10]:
                table.add_row(*format_table_row(ac))

        from rich.console import Console

        console = Console(record=True, width=view.terminal_width, force_terminal=False)
        console.print(table)
        return console.export_text()

    def _build_summary(self, view: TerminalView) -> Text:
        return Text(self._build_summary_text(view))

    def _build_summary_text(self, view: TerminalView) -> str:
        count = view.aircraft_count
        aircraft_text = "1 aircraft nearby" if count == 1 else f"{count} aircraft nearby"
        refresh = _format_refresh_interval(view.refresh_seconds)
        parts = [
            aircraft_text,
            f"radius {view.radius_km:.0f} km",
            f"refresh {refresh}",
        ]
        if view.last_updated and (view.aircraft_error or view.is_stale):
            parts.append(f"last update {format_local_time(view.last_updated, view.timezone)}")
        if view.aircraft_error and view.is_stale:
            parts.append("retrying on next refresh")
        return "  •  ".join(parts)

    def _location_line(self, view: TerminalView) -> str:
        return f"TERMRADAR — {self._display_location(view)}"

    def _status_line(self, view: TerminalView) -> str:
        updated = format_local_time(view.last_updated, view.timezone)
        if view.is_live:
            return f"LIVE ● {updated}"
        return f"DATA UNAVAILABLE — Last update: {updated}"


def _format_refresh_interval(seconds: int) -> str:
    if seconds == 1:
        return "1s"
    return f"{seconds}s"


def _format_closest_metrics(ac) -> str:
    distance = format_distance_km(ac.distance_km)
    away = f"{distance} away" if distance != "—" else "Distance unknown"
    altitude = format_altitude_ft(ac.altitude_ft)
    parts = [
        part
        for part in (
            away,
            format_bearing_compass(ac.bearing_deg),
            format_speed_knots(ac.ground_speed_knots),
            altitude if altitude not in ("—", "ground") else None,
        )
        if part
    ]
    return " · ".join(parts)


def _format_nearby_line(rank: int, ac) -> str:
    callsign = format_callsign(ac)
    distance = format_distance_km(ac.distance_km)
    compass = "—" if ac.bearing_deg is None else bearing_to_compass(ac.bearing_deg)
    return f"{rank}  {callsign:<8}  {distance:>7}  {compass}"
