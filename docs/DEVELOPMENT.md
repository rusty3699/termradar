# Development

## Setup

```bash
git clone https://github.com/rusty3699/termradar.git
cd termradar
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Requirements:** Python 3.11+

**Runtime deps:** `httpx`, `platformdirs`, `rich`, `timezonefinder`, `tomli-w`

**Dev deps:** `build`, `pytest`, `pytest-cov`, `ruff`

## Run locally

```bash
termradar
termradar --location "Andheri, Mumbai" --radius 25 --refresh 10
termradar --aircraft-provider opensky    # optional; rate-limited
termradar --reset-location
termradar --version
```

Refresh must be **≥ 5 seconds** (`termradar.core.limits.LIVE_REFRESH_MIN_SECONDS`).

## Test

```bash
pytest
pytest -v
pytest --cov=termradar --cov-report=term-missing
```

All tests use mocked HTTP - no network required for the suite.

Key test areas:

| Area | Tests |
|------|-------|
| Providers | `test_aircraft.py`, `test_adsbdb.py`, `test_routes.py`, `test_geocoding.py` |
| Engine / enrichment | `test_engine.py`, `test_airline.py` |
| UI / radar | `test_terminal_ui.py`, `test_radar_canvas.py`, `test_radar_coords.py` |
| Config / limits | `test_config.py`, `test_rate_limit.py` |

Use `TerminalRenderer.render_text()` for layout tests without brittle ANSI snapshots.

## Demo recording

The README demo GIF is generated with [VHS](https://github.com/charmbracelet/vhs). VHS needs `ttyd`, `ffmpeg`, and Chromium on your `PATH`.

```bash
# install VHS (see https://github.com/charmbracelet/vhs#installation)
vhs docs/assets/demo-quick.tape
```

Source tape: `docs/assets/demo-quick.tape` → output: `docs/assets/demo-quick.gif`

Edit the tape to change terminal size, typing speed, or how long the live UI stays on screen before exit.

## Lint and format

```bash
ruff check src tests
ruff format src tests
ruff format --check src tests
```

## Build and validate wheel

```bash
python -m build
pip install dist/termradar-*.whl
termradar --help
termradar --version
python -c "import termradar; print(termradar.__version__)"
```

## Project layout

```text
src/termradar/       Package source
tests/               pytest suite (fakes in tests/fakes.py)
docs/                Architecture, providers, roadmap
```

## Rate-limit constants

Defined in `src/termradar/core/limits.py`:

```python
LIVE_REFRESH_DEFAULT_SECONDS = 5
LIVE_REFRESH_MIN_SECONDS = 5
ENRICHMENT_REQUESTS_PER_MINUTE = 30
ENRICHMENT_MAX_BURST = 10
ENRICHMENT_SUCCESS_TTL_SECONDS = 43_200   # 12 h
ENRICHMENT_FAILURE_TTL_SECONDS = 1_800    # 30 min
GEOCODING_MIN_INTERVAL_SECONDS = 1.0
```

Change these in one place; `config/storage.py`, `cli.py`, and `CachedRouteProvider` import from there.

## Notes

- User config: `~/.config/termradar/config.toml` - never commit
- Do not call providers from renderer code
- Provider JSON must not leak outside `providers/`
- ADSBDB 404 / unknown callsign is expected - handle quietly at debug level
