"""Live radar refresh orchestration."""

from __future__ import annotations

import shutil
import time
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from termradar.core.engine import RadarEngine, RadarEngineError
from termradar.core.models import Location, RadarSnapshot
from termradar.renderers.terminal_ui import TerminalRenderer
from termradar.renderers.terminal_view import TerminalView

if TYPE_CHECKING:
    from rich.console import Console


class RadarSession:
    """Run repeated radar scans and drive the terminal renderer."""

    def __init__(
        self,
        engine: RadarEngine,
        *,
        refresh_seconds: int,
        renderer: TerminalRenderer | None = None,
        sleep: Callable[[float], None] = time.sleep,
        terminal_size: Callable[[], tuple[int, int]] | None = None,
    ) -> None:
        self._engine = engine
        self._refresh_seconds = refresh_seconds
        self._renderer = renderer or TerminalRenderer()
        self._sleep = sleep
        self._terminal_size = terminal_size or _default_terminal_size
        self._last_snapshot: RadarSnapshot | None = None
        self._last_updated: datetime | None = None
        self._last_error: str | None = None

    @property
    def refresh_seconds(self) -> int:
        return self._refresh_seconds

    @property
    def location(self) -> Location:
        return self._engine.location

    def scan_once(self) -> TerminalView:
        """Perform one scan and return the display view."""
        width, height = self._terminal_size()
        try:
            snapshot = self._engine.scan()
            self._last_snapshot = snapshot
            self._last_updated = snapshot.scanned_at
            self._last_error = None
            return self._build_view(
                snapshot,
                error=None,
                is_stale=False,
                width=width,
                height=height,
            )
        except RadarEngineError as exc:
            self._last_error = "Aircraft data temporarily unavailable."
            is_stale = self._last_snapshot is not None
            return self._build_view(
                self._last_snapshot,
                error=str(exc) if not is_stale else self._last_error,
                is_stale=is_stale,
                width=width,
                height=height,
            )

    def run(self, console: Console) -> None:
        """Run the live refresh loop until interrupted."""
        from rich.live import Live

        console.clear()
        with Live(
            console=console,
            refresh_per_second=4,
            screen=False,
            transient=False,
        ) as live:
            try:
                while True:
                    view = self.scan_once()
                    live.update(self._renderer.render(view))
                    self._sleep(self._refresh_seconds)
            except KeyboardInterrupt:
                pass

    def _build_view(
        self,
        snapshot: RadarSnapshot | None,
        *,
        error: str | None,
        is_stale: bool,
        width: int,
        height: int,
    ) -> TerminalView:
        location_name = (
            snapshot.location.display_name
            if snapshot is not None
            else self._engine.location.display_name
        )
        timezone = (
            snapshot.location.timezone if snapshot is not None else self._engine.location.timezone
        )
        location_query = (
            snapshot.location.query if snapshot is not None else self._engine.location.query
        )
        radius_km = snapshot.radius_km if snapshot is not None else self._engine.radius_km
        return TerminalView(
            location_name=location_name,
            radius_km=radius_km,
            refresh_seconds=self._refresh_seconds,
            timezone=timezone,
            location_query=location_query,
            snapshot=snapshot,
            aircraft_error=error,
            last_updated=self._last_updated,
            is_stale=is_stale,
            terminal_width=width,
            terminal_height=height,
        )


def _default_terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines
