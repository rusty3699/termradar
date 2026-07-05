# TermRadar

**See what's flying above you.**

TermRadar is an open-source live aircraft radar for your terminal, with Raspberry Pi and small-display support planned.

One radar engine powers multiple displays — terminal today, hardware displays tomorrow.

## Available now

- **Polished terminal UI** — radar visualization, nearest-aircraft panel, aircraft table
- **Live refresh loop** — automatic updates with configurable interval
- **Core radar engine** — fetch, normalize, filter, sort, and enrich aircraft
- **Free-text geocoding** — enter a place name (e.g. `Baner, Pune`) via Nominatim/OpenStreetMap
- **Location onboarding** — first-run CLI setup with candidate selection
- **Persistent config** — saved coordinates and radar settings
- **Live aircraft data** — OpenSky Network provider
- **Route enrichment** — adsb.lol route lookup with in-memory cache
- **CLI overrides** — temporary `--location`, `--radius`, and `--refresh` for a single run
- **`termradar` CLI** — installable entry point

## Planned

- Raspberry Pi TFT fullscreen renderer
- OLED displays
- Local ADS-B sources (RTL-SDR, `readsb`, `dump1090`)
- Alerts and overhead mode
- Telegram bot
- Web UI

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full plan.

## Installation

### From source (development)

```bash
git clone https://github.com/rusty3699/termradar.git
cd termradar
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### From PyPI

PyPI publication is prepared but not yet released. Once published:

```bash
pip install termradar
```

Until then, install from source as shown above.

## Usage

```bash
termradar
```

On first run you will be prompted for a location, search radius, and refresh interval. Subsequent runs reuse saved configuration and start the live radar display.

```bash
termradar --radius 25
termradar --refresh 10
termradar --location "Baner, Pune"
termradar --reset-location
termradar --help
```

CLI overrides apply to the **current run only** and do not change saved configuration.

Press **Ctrl+C** to exit cleanly.

### Example output

Representative terminal layout (actual styling uses Rich panels):

```text
╭──────────────────── TERMRADAR ────────────────────╮
│ Dadar, Mumbai                    LIVE ● 12:42:07   │
│                                                    │
│ RADAR                    NEAREST AIRCRAFT          │
│      N                     6E221                   │
│  .---+---.                 IndiGo                   │
│  |   + ✈ |                 DEL → BOM               │
│  '---+---+                 Distance: 4.2 km        │
│      S                     Altitude: 8,350 ft      │
│                                                    │
│ 3 aircraft within 15 km | Refresh: 5 seconds       │
╰────────────────────────────────────────────────────╯
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

## Architecture

```text
GeocodingProvider
        ↓
     Location

AircraftProvider
        ↓
   RadarEngine ◄──── RouteProvider
        ↓
   RadarSnapshot
        ↓
 TerminalRenderer
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup, testing, linting, and packaging commands.

## Data providers

See [docs/DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md) for API details, attribution, and limits.

## License

MIT — see [LICENSE](LICENSE).
