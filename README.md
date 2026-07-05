# TermRadar

**Live aircraft radar for your terminal and Raspberry Pi.**

TermRadar shows nearby aircraft on a map centered on your location. One radar engine powers multiple display backends — terminal today, hardware displays tomorrow.

## Available (Phase 1)

- **Core radar engine** — fetch, normalize, filter, sort, and enrich aircraft
- **Free-text geocoding** — enter a place name (e.g. `Baner, Pune`) via Nominatim/OpenStreetMap
- **Location onboarding** — first-run CLI setup with candidate selection
- **Persistent config** — saved coordinates and radar settings (platform-appropriate path)
- **Live aircraft data** — OpenSky Network provider
- **Route enrichment** — adsb.lol route lookup with in-memory cache
- **Terminal output** — basic text listing of nearby aircraft
- **`termradar` CLI** — installable entry point

```bash
pip install -e ".[dev]"
termradar
```

## Planned

- Animated terminal radar UI
- Continuous refresh loop
- Raspberry Pi TFT / OLED displays
- Pygame visual radar
- GPIO hardware buttons
- Telegram bot
- Web UI

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full plan.

## Quick start

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run first-time setup and a scan
termradar
```

On first run you will be prompted for a location and search radius. Subsequent runs reuse saved configuration.

```bash
# Override radius for a single scan
termradar --radius-km 25

# Re-run location onboarding
termradar --reset-location
```

## Configuration

Config is stored at a platform-appropriate path (e.g. `~/.config/termradar/config.toml` on Linux):

```toml
[location]
query = "Dadar, Mumbai"
display_name = "Dadar, Mumbai, Maharashtra, India"
latitude = 19.0178
longitude = 72.8478

[radar]
radius_km = 15
refresh_seconds = 5
```

User config is never committed to this repository.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup, testing, and linting commands.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Data providers

See [docs/DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md) for API details, attribution, and limits.

## License

MIT — see [LICENSE](LICENSE).
