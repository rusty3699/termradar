"""Tests for rate limiters."""

from termradar.core.rate_limit import MinuteRateLimiter


def test_minute_rate_limiter_blocks_after_max():
    clock = {"now": 0.0}

    def monotonic() -> float:
        return clock["now"]

    limiter = MinuteRateLimiter(2, clock=monotonic)
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False

    clock["now"] = 61.0
    assert limiter.allow() is True
