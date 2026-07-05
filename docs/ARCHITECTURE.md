# Architecture

TermRadar follows a single principle:

> **One radar engine. Multiple displays.**

The renderer never participates in data fetching, geocoding, or enrichment. The engine never knows about display hardware or UI frameworks.

## Data flow

```text
GeocodingProvider
        ↓
     Location
        ↓
AircraftProvider
        ↓
   RadarEngine ◄──── RouteProvider
        ↓
   RadarSnapshot
        ↓
 TerminalRenderer
        ↓
 Terminal output
```

Future Pi and OLED renderers consume the same `RadarSnapshot`.

### Geocoding (setup only)

Geocoding runs during first-run onboarding, `--reset-location`, or `--location` override — **not** on every radar refresh.

```text
user query → geocoder search → candidates → user selection → saved coordinates
```

### Radar scan pipeline

```text
Saved location
      ↓
RadarEngine.scan()
      ↓
Normalized Aircraft models
      ↓
distance_km() + bearing_deg()   [engine]
      ↓
Radius filtering + sorting      [engine]
      ↓
Route enrichment (cached)       [engine + RouteProvider]
      ↓
RadarSnapshot
      ↓
TerminalRenderer
```

### Live refresh orchestration

```text
CLI / RadarSession
      ↓
loop: engine.scan() → TerminalView → TerminalRenderer → terminal
      ↓
sleep(refresh_seconds)
```

`RadarSession` owns the refresh loop. The renderer is stateless and receives a `TerminalView` each frame.

## Package layout

```text
src/termradar/
├── cli.py              # Argument parsing, onboarding, session startup
├── session.py          # Live refresh loop orchestration
├── core/
│   ├── models.py       # Location, Aircraft, RadarSnapshot, …
│   ├── distance.py     # Haversine distance
│   ├── bearing.py      # Initial bearing
│   └── engine.py       # RadarEngine.scan()
├── providers/
│   ├── base.py         # Protocol definitions
│   ├── geocoding.py    # NominatimGeocodingProvider
│   ├── aircraft.py     # OpenSkyAircraftProvider
│   └── routes.py       # AdsbLolRouteProvider + CachedRouteProvider
├── config/
│   └── storage.py      # TOML config load/save/validate
└── renderers/
    ├── formatting.py   # Pure display formatters
    ├── radar_coords.py # bearing/distance → grid coordinates
    ├── radar_canvas.py # ASCII radar drawing
    ├── terminal_ui.py  # Rich terminal layout
    └── terminal_view.py# View model for one frame
```

## Responsibility boundaries

| Component | Responsibility |
|-----------|----------------|
| `GeocodingProvider` | Free-text place → `LocationCandidate` list |
| `AircraftProvider` | Lat/lon/radius → normalized `Aircraft` list |
| `RouteProvider` | Callsign → `RouteInfo` or `None` |
| `RadarEngine` | Fetch, geometry, filter, sort, enrich |
| `CachedRouteProvider` | In-memory route lookup cache |
| `RadarSession` | Refresh loop, error/stale state, terminal sizing |
| `TerminalRenderer` | Layout, radar plot, panels, tables |
| `radar_to_grid()` | Polar → terminal grid (renderer utility) |

The renderer must **not** call providers, compute Haversine distance, or filter by radius.

## Terminal radar coordinates

`radar_to_grid()` maps engine-provided `distance_km` and `bearing_deg` to grid cells:

```text
0° north  → top of grid
90° east  → right
180° south → bottom
270° west → left
```

Distance is normalized against configured `radius_km`. Aircraft beyond radius are excluded from the plot.

## Error semantics

| Failure | Behaviour |
|---------|-----------|
| Aircraft provider down | Show error; preserve last snapshot as stale if available |
| Route lookup fails | Aircraft shown without route fields |
| Missing callsign/altitude | Graceful display fallbacks (`—`, `Unknown`) |
| Geocoding failure | Onboarding reports error; no config saved |
| Ctrl+C | Clean exit, no traceback |

## Configuration flow

```text
first run / --reset-location → onboarding → save config.toml
returning user             → load config → start session
--location / --radius / --refresh → override for current run only
```

## Cache behavior

Route enrichment uses `CachedRouteProvider`. Cache persists for the CLI process lifetime. Route lookups are not repeated for the same callsign across refresh cycles within one session.

`enrichment_limit` on `RadarEngine` caps how many nearest aircraft are enriched per scan.
