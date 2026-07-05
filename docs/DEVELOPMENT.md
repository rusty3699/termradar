# Development

## Requirements

- Python 3.11+
- Linux, macOS, or Windows

## Environment setup

```bash
cd termradar
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Install dependencies

```bash
pip install -e ".[dev]"
```

Runtime dependencies: `httpx`, `platformdirs`, `tomli-w`.

Dev dependencies: `pytest`, `pytest-cov`, `ruff`.

## Run CLI

```bash
termradar
termradar --radius-km 25
termradar --reset-location
termradar --enrichment-limit 5
```

Equivalent module invocation:

```bash
python -m termradar
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
ruff format --check src tests   # CI-style check only
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

Or point tests at a temporary path via `load_config(path)` / `save_config(config, path)`.

Never commit user config or real coordinates to the repository.
