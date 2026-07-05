"""Display time formatting for terminal output."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


def format_local_time(value: datetime | None, timezone_name: str | None = None) -> str:
    """Format *value* in the radar location timezone when available."""
    if value is None:
        return "—"

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)

    if timezone_name:
        try:
            local = value.astimezone(ZoneInfo(timezone_name))
            abbrev = local.tzname()
            base = local.strftime("%H:%M:%S")
            if abbrev:
                return f"{base} {abbrev}"
            return base
        except Exception:
            pass

    local = value.astimezone()
    abbrev = local.tzname()
    base = local.strftime("%H:%M:%S")
    if abbrev:
        return f"{base} {abbrev}"
    return base
