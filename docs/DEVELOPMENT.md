# Development

## Requirements

- Python 3.11+
- Linux, macOS, or Windows

## Clone repository

```bash
git clone https://github.com/rusty3699/termradar.git
cd termradar
```

## Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

## Install development dependencies

```bash
pip install -e ".[dev]"
```

Runtime dependencies: `httpx`, `platformdirs`, `rich`, `tomli-w`.

Dev dependencies: `build`, `pytest`, `pytest-cov`, `ruff`.

## Run TermRadar locally

```bash
termradar
python -m termradar
termradar --radius 25 --refresh 10
termradar --location "Baner, Pune"
termradar --reset-location
termradar --help
```

## Run tests

```bash
pytest
pytest -v
pytest --cov=termradar --cov-report=term-missing
```

All default tests use mocked HTTP — no internet required.

## Lint

```bash
ruff check src tests
```

## Format

```bash
ruff format src tests
ruff format --check src tests
```

## Build package

```bash
python -m build
```

Produces `dist/termradar-*.tar.gz` (sdist) and `dist/termradar-*.whl` (wheel).

## Install local wheel (clean validation)

```bash
python -m venv /tmp/termradar-clean
source /tmp/termradar-clean/bin/activate
pip install dist/termradar-*.whl
termradar --help
python -c "import termradar; print(termradar.__version__)"
deactivate
```

## Project layout

```text
src/termradar/     # Package source
tests/             # pytest suite
docs/              # Documentation
pyproject.toml     # Build, deps, tool config
```

## Config during development

User config is written to the platform config directory (e.g. `~/.config/termradar/config.toml`). To test onboarding repeatedly:

```bash
termradar --reset-location
```

Never commit user config or real coordinates to the repository.

## Renderer development notes

- Test pure helpers in `renderers/formatting.py` and `renderers/radar_coords.py`
- Use `TerminalRenderer.render_text()` for layout tests without brittle ANSI snapshots
- Do not call providers from renderer code
