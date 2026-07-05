"""View model passed from CLI orchestration to the terminal renderer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from termradar.core.models import RadarSnapshot


@dataclass(slots=True)
class TerminalView:
    """Display state for one terminal frame."""

    location_name: str
    radius_km: float
    refresh_seconds: int
    snapshot: RadarSnapshot | None = None
    aircraft_error: str | None = None
    last_updated: datetime | None = None
    is_stale: bool = False
    terminal_width: int = 80
    terminal_height: int = 24

    @property
    def aircraft_count(self) -> int:
        if self.snapshot is None:
            return 0
        return self.snapshot.count

    @property
    def is_live(self) -> bool:
        return self.aircraft_error is None and self.snapshot is not None
