"""Simple rolling-window rate limiters."""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable


class MinuteRateLimiter:
    """Allow at most *max_per_minute* events in any rolling 60-second window."""

    def __init__(
        self,
        max_per_minute: int,
        *,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_per_minute <= 0:
            raise ValueError("max_per_minute must be positive")
        self._max_per_minute = max_per_minute
        self._window_seconds = window_seconds
        self._clock = clock
        self._events: deque[float] = deque()

    def allow(self) -> bool:
        """Return True when a new request may proceed."""
        now = self._clock()
        while self._events and now - self._events[0] >= self._window_seconds:
            self._events.popleft()
        if len(self._events) >= self._max_per_minute:
            return False
        self._events.append(now)
        return True
