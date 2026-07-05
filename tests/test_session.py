"""Tests for live radar session orchestration."""

from fakes import FakeAircraftProvider, FakeRouteProvider, make_location
from termradar.core.engine import RadarEngine
from termradar.core.models import Aircraft
from termradar.session import RadarSession


def _engine(aircraft=None, error=None) -> RadarEngine:
    return RadarEngine(
        aircraft_provider=FakeAircraftProvider(aircraft or [], error=error),
        route_provider=FakeRouteProvider(),
        location=make_location(),
        radius_km=15.0,
    )


def test_scan_once_success():
    ac = Aircraft(hex_id="a", latitude=19.02, longitude=72.85, callsign="IGO1")
    session = RadarSession(
        _engine([ac]),
        refresh_seconds=5,
        terminal_size=lambda: (80, 24),
    )
    view = session.scan_once()
    assert view.snapshot is not None
    assert view.snapshot.count == 1
    assert view.is_live
    assert view.aircraft_error is None


def test_scan_once_provider_failure_without_stale():
    session = RadarSession(
        _engine(error=RuntimeError("down")),
        refresh_seconds=5,
        terminal_size=lambda: (80, 24),
    )
    view = session.scan_once()
    assert view.snapshot is None
    assert view.aircraft_error is not None


def test_scan_once_preserves_stale_snapshot():
    ac = Aircraft(hex_id="a", latitude=19.02, longitude=72.85)
    good_engine = RadarEngine(
        FakeAircraftProvider([ac]),
        FakeRouteProvider(),
        make_location(),
        radius_km=15.0,
    )
    session = RadarSession(
        good_engine,
        refresh_seconds=5,
        terminal_size=lambda: (80, 24),
    )
    session.scan_once()

    bad_engine = RadarEngine(
        FakeAircraftProvider(error=RuntimeError("down")),
        FakeRouteProvider(),
        make_location(),
        radius_km=15.0,
    )
    session._engine = bad_engine
    view = session.scan_once()
    assert view.is_stale
    assert view.snapshot is not None
    assert view.snapshot.count == 1


def test_run_loop_uses_sleep_mock():
    ac = Aircraft(hex_id="a", latitude=19.02, longitude=72.85)
    sleeps: list[float] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        raise KeyboardInterrupt

    session = RadarSession(
        _engine([ac]),
        refresh_seconds=7,
        sleep=sleep,
        terminal_size=lambda: (80, 24),
    )

    from rich.console import Console

    console = Console(force_terminal=False, width=80)
    session.run(console)
    assert sleeps == [7]


def test_run_loop_clears_console_before_live():
    from unittest.mock import MagicMock, patch

    ac = Aircraft(hex_id="a", latitude=19.02, longitude=72.85)
    session = RadarSession(
        _engine([ac]),
        refresh_seconds=1,
        sleep=lambda _s: None,
        terminal_size=lambda: (80, 24),
    )

    tracking = MagicMock()
    live_instance = MagicMock()
    live_instance.update.side_effect = KeyboardInterrupt

    with patch("rich.live.Live", return_value=live_instance) as mock_live:
        mock_live.return_value.__enter__.return_value = live_instance
        session.run(tracking)

    tracking.clear.assert_called_once()
