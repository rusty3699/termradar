# TermRadar

**See what's flying above you.**

TermRadar is a live aircraft radar for your terminal. Enter a place name, and it shows nearby flights on a live-updating radar with distance, bearing, speed, altitude, and route information when available.

> **One radar engine. Multiple displays.**

The core engine is display-agnostic. Today: a polished terminal UI. Planned: Raspberry Pi fullscreen and small displays.

## Features

| Available now | Planned |
|---------------|---------|
| Live terminal radar (default 5 s refresh) | Raspberry Pi fullscreen display |
| Numbered radar markers + top-five nearby list | OLED / e-paper displays |
| Closest-aircraft detail panel | Local ADS-B receivers |
| adsb.lol live aircraft (default) | Alerts and notifications |
| ADSBDB route/airline enrichment | Web UI |
| Nominatim geocoding, local timezone | |
| OpenSky aircraft via `--aircraft-provider opensky` | |

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

**First run:** enter a location (e.g. `Dadar East, Mumbai`), pick a geocoding result, set radius and refresh interval.

**Later runs:** reuse saved settings. Press **Ctrl+C** to exit.

### CLI options

```bash
termradar --location "Baner, Pune"      # temporary location (this run only)
termradar --radius 25                   # search radius in km (this run only)
termradar --refresh 10                  # refresh interval in seconds (min 3)
termradar --aircraft-provider opensky   # use OpenSky instead of adsb.lol
termradar --enrichment-limit 10         # max aircraft to enrich per scan (default 10)
termradar --reset-location              # re-run setup and save new config
termradar --version
termradar --help
```

### Defaults and limits

| Setting | Default | Allowed |
|---------|---------|---------|
| Refresh interval | 5 s | 3–300 s |
| Search radius | 15 km | 1–250 km |
| Aircraft provider | adsb.lol | `adsblol` or `opensky` |
| Enrichment per scan | 10 nearest | `--enrichment-limit` |
| ADSBDB rate cap | 30 requests/min | enforced internally |

Config file: `~/.config/termradar/config.toml` (Linux). Saved refresh values below 3 s are upgraded to 5 s automatically.

Details: [docs/DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md)

## Example

```text
╭──────────────────── TERMRADAR ────────────────────╮
│ Dadar East, Mumbai                LIVE ● 13:18:10 │
│                                                   │
│  RADAR                   NEARBY AIRCRAFT            │
│       N                    CLOSEST                  │
│   ..... 1 .....            AKJ128E                  │
│  W    +     E              Akasa Air                │
│       2                    Route unavailable      │
│                            8.3 km away · N · 1 kt │
│                            NEARBY                   │
│                            1  AKJ128E   8.3 km  N │
│                            2  AIC5TN   11.6 km NE │
│                                                   │
│ 2 aircraft nearby • radius 15 km • refresh 5s     │
╰───────────────────────────────────────────────────╯
```

**Radar symbols:** `+` your location · outer ring = search radius · inner ring = half radius · `1`–`5` = top five nearest (same numbers as the nearby list) · `✈` = other aircraft

## How it works

```text
each refresh (every 5 s by default):
  1. Fetch live aircraft near your location     → adsb.lol
  2. Compute distance and bearing from you
  3. Enrich nearest aircraft (cache miss only)  → ADSBDB
  4. Draw radar + aircraft panels

location setup only (not each refresh):
  Geocoding → Nominatim
```

**Data sources**

- **Aircraft:** [adsb.lol](https://adsb.lol) (default) or [OpenSky](https://opensky-network.org) via `--aircraft-provider opensky`
- **Routes / airlines:** [ADSBDB](https://adsbdb.com) + ICAO callsign prefix inference
- **Geocoding:** [OpenStreetMap](https://www.openstreetmap.org) / Nominatim

## Documentation

| Doc | Description |
|-----|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, UI layout, boundaries |
| [DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md) | APIs, rate limits, caching, attribution |
| [ROADMAP.md](docs/ROADMAP.md) | Phases and future work |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Setup, tests, packaging |

## License

MIT — see [LICENSE](LICENSE).

---

Made with <3 Anish
