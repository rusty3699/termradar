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

**Runtime deps:** `httpx`, `platformdirs`, `rich`, `tomli-w`

**Dev deps:** `build`, `pytest`, `pytest-cov`, `ruff`

## Run locally

```bash
termradar
termradar --location "Baner, Pune" --radius 25 --refresh 10
termradar --reset-location
```

## Test

```bash
pytest
pytest -v
pytest --cov=termradar --cov-report=term-missing
```

All tests use mocked HTTP — no network required.

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
python -c "import termradar; print(termradar.__version__)"
```

## Project layout

```text
src/termradar/    Package source
tests/            pytest suite
docs/             Documentation
```

## Notes

- User config: `~/.config/termradar/config.toml` — never commit
- Test helpers: `renderers/formatting.py`, `renderers/radar_coords.py`
- Use `TerminalRenderer.render_text()` for layout tests without brittle ANSI snapshots
- Do not call providers from renderer code
