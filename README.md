# TermRadar

**See what's flying above you - without leaving your terminal.**

![TermRadar live demo](https://raw.githubusercontent.com/rusty3699/termradar/main/docs/assets/demo-quick.gif)

TermRadar is a lightweight live aircraft radar for developers, programmers, and aviation enthusiasts.

You're coding, you hear an aircraft overhead, or spot something from the window. Instead of opening a browser or reaching for a flight-tracking app, open a terminal and run:

```bash
termradar
```

You get a live radar centered on your location: nearby callsigns, distance, bearing, speed, altitude, and route info when available. Use it for the quick answer, then jump to another tracker when you want deeper details.

> **One radar engine. Multiple displays.**

The core is display-agnostic. Today: a polished terminal UI. Planned: Raspberry Pi fullscreen and small displays.

## Quick start

```bash
pip install termradar
termradar
```

From source:

```bash
git clone https://github.com/rusty3699/termradar.git
cd termradar
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
termradar
```

First run: enter a location, pick a geocoding result, set radius and refresh. Later runs reuse saved settings. Press **Ctrl+C** to exit.

Config: `~/.config/termradar/config.toml` (Linux).

## What you get

| Available now | Planned |
|---------------|---------|
| Live terminal radar (default 5 s refresh) | Raspberry Pi fullscreen display |
| Numbered radar markers + top-five nearby list | OLED / e-paper displays |
| Closest-aircraft detail panel | Local ADS-B receivers |
| adsb.lol live aircraft (default) | Alerts and notifications |
| ADSBDB route/airline enrichment | Web UI |
| Nominatim geocoding, local timezone | |
| OpenSky via `--aircraft-provider opensky` | |

**Requirements:** Python 3.11+, network access. Works on Linux, macOS, Windows, and Raspberry Pi.

## Usage

```bash
termradar --location "Baner, Pune"      # temporary location (this run only)
termradar --radius 25                   # search radius in km
termradar --refresh 10                  # refresh interval (min 3 s)
termradar --aircraft-provider opensky   # OpenSky instead of adsb.lol
termradar --enrichment-limit 10         # max aircraft to enrich per scan
termradar --reset-location              # re-run setup
termradar --version
termradar --help
```

| Setting | Default | Allowed |
|---------|---------|---------|
| Refresh | 5 s | 3-300 s |
| Radius | 15 km | 1-250 km |
| Aircraft source | adsb.lol | `adsblol` or `opensky` |
| Enrichment | 10 nearest | `--enrichment-limit` |

Rate limits and provider details: [docs/DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md)

## How it works

```text
each refresh (every 5 s by default):
  1. Fetch aircraft near you          → adsb.lol
  2. Distance and bearing from you
  3. Enrich nearest (cache miss only) → ADSBDB
  4. Draw radar + aircraft panels

setup only (not each refresh):
  Geocoding → Nominatim
```

**Data sources:** [adsb.lol](https://adsb.lol) (aircraft), [ADSBDB](https://adsbdb.com) (routes/airlines), [Nominatim](https://www.openstreetmap.org) (geocoding)

## Documentation

| Doc | What it covers |
|-----|----------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design, UI layout, code boundaries |
| [DATA_PROVIDERS.md](docs/DATA_PROVIDERS.md) | APIs, rate limits, caching |
| [ROADMAP.md](docs/ROADMAP.md) | What's next |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Tests, lint, packaging |

## License

MIT - see [LICENSE](LICENSE).

---

Made with <3 Anish
