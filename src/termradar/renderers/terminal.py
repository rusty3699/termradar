"""Terminal text output — legacy single-scan helper and re-exports."""

from __future__ import annotations

from termradar.core.models import RadarSnapshot
from termradar.renderers.terminal_ui import TerminalRenderer
from termradar.renderers.terminal_view import TerminalView

__all__ = [
    "TerminalRenderer",
    "TerminalView",
    "render_snapshot",
]


def render_snapshot(snapshot: RadarSnapshot) -> str:
    """Format a radar snapshot as plain text (legacy helper)."""
    renderer = TerminalRenderer()
    view = TerminalView(
        location_name=snapshot.location.display_name,
        radius_km=snapshot.radius_km,
        refresh_seconds=5,
        snapshot=snapshot,
        last_updated=snapshot.scanned_at,
        timezone=snapshot.location.timezone,
    )
    return renderer.render_text(view)
