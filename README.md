# TermRadar

**See what's flying above you.**

TermRadar is a live aircraft radar for your terminal. Enter a place name, and it shows nearby flights on a live-updating radar display with distance, altitude, speed, and route information when available.

> **One radar engine. Multiple displays.**

The core engine is display-agnostic. Today: a polished terminal UI. Planned: Raspberry Pi fullscreen and small displays.

## Features

| Available now | Planned |
|---------------|---------|
| Live terminal radar with refresh loop | Raspberry Pi fullscreen display |
| ASCII radar plot + nearest-aircraft panel | OLED / e-paper displays |
| Free-text location geocoding | Local ADS-B receivers |
| OpenSky live aircraft data | Alerts and notifications |
| Route enrichment (when available) | Web UI |

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full plan.

## Requirements

- Python 3.11+
- Network access (aircraft and geocoding APIs)

Works on Linux, macOS, Windows, and Raspberry Pi (terminal mode).

## Install

**From source** (recommended until PyPI release):

```bash
git clone https://github.com/rusty3699/termradar.git
cd termradar
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
termradar
```

First run: enter a location (e.g. `Dadar East Hindu Colony`), pick a geocoding result, set radius and refresh interval.

Later runs reuse saved settings. Press **Ctrl+C** to exit.

```bash
termradar --location "Baner, Pune"   # temporary location (this run only)
termradar --radius 25               # temporary radius (km)
termradar --refresh 10              # temporary refresh interval (seconds)
termradar --reset-location          # re-run setup and save new config
termradar --help
```

Config is stored at `~/.config/termradar/config.toml` (Linux).

## Example

```text
╭──────────────────── TERMRADAR ────────────────────╮
│ Hindu Colony, Mumbai              LIVE ● 12:42:07 │
│                                                   │
│  RADAR                   NEAREST AIRCRAFT         │
│       N                    IGO6224                │
│   ..... ✈ .....            Distance: 8.5 km       │
│  W    +     E              Altitude: 12,400 ft   │
│       S                                           │
│                                                   │
│ 3 aircraft within 15 km | Refresh: 5 seconds      │
╰───────────────────────────────────────────────────╯
```

## Architecture

```text
Geocoding → Location → RadarEngine ← RouteProvider → RadarSnapshot → TerminalRenderer
```

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Documentation

| Doc | Description |
|-----|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and boundaries |
| [ROADMAP.md](docs/ROADMAP.md) | Phases and future work |
| [DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md) | APIs, limits, attribution |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Setup, tests, packaging |

## Data sources

- **Aircraft:** [OpenSky Network](https://opensky-network.org)
- **Geocoding:** [OpenStreetMap](https://www.openstreetmap.org) / Nominatim
- **Routes:** [adsb.lol](https://adsb.lol) (best-effort enrichment)

## License

MIT — see [LICENSE](LICENSE).
