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

README assets are generated with [VHS](https://github.com/charmbracelet/vhs). VHS needs `ttyd`, `ffmpeg`, and Chromium on your `PATH`.

| Asset | Tape | What it shows |
|-------|------|---------------|
| `demo-quick.gif` | `docs/assets/demo-quick.tape` | Short live radar session (existing venv) |
| `demo-setup.gif` | `docs/assets/demo-setup.tape` | Full install, deps, first-run setup, live radar |
| `termradar.png` | — | Static screenshot (export from a live session) |

```bash
# install VHS (see https://github.com/charmbracelet/vhs#installation)
vhs docs/assets/demo-quick.tape
vhs docs/assets/demo-setup.tape
```

Regenerate GIFs after changing a tape, then commit the updated files.

The README embeds images with absolute `raw.githubusercontent.com` URLs so they render on GitHub (public repo) and PyPI:

```markdown
![TermRadar live demo](https://raw.githubusercontent.com/rusty3699/termradar/main/docs/assets/demo-quick.gif)
![Install and first-run setup](https://raw.githubusercontent.com/rusty3699/termradar/main/docs/assets/demo-setup.gif)
```

Edit a tape to change terminal size, typing speed, or how long the live UI stays on screen before exit. The setup tape uses a temp venv under `/tmp/termradar-demo-venv` and clears config under `/tmp/termradar-vhs-config`.

## Lint and format

```bash
ruff check src tests
ruff format src tests
ruff format --check src tests
```

## Build and validate wheel

```bash
python -m build
pip install dist/termradar-0.3.2-py3-none-any.whl
termradar --help
termradar --version
python -c "import termradar; print(termradar.__version__)"
```

Remove older wheels from `dist/` before installing if multiple versions are present.

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
