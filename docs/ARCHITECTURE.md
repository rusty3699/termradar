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
     Renderer
```

### Geocoding (setup only)

Geocoding runs during first-run onboarding, explicit location changes (`--reset-location`), or future config commands — **not** on every radar refresh.

```text
user query → geocoder search → candidates → user selection → saved coordinates
```

### Radar scan pipeline

```text
Location input (from config)
      ↓
AircraftProvider.get_nearby()
      ↓
Normalized Aircraft models
      ↓
distance_km() + bearing_deg()
      ↓
Radius filtering
      ↓
Nearest-first sorting
      ↓
Route enrichment (limited count, cached)
      ↓
RadarSnapshot
```

## Package layout

```text
src/termradar/
├── cli.py              # CLI entry point and onboarding
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
    └── terminal.py     # Basic text output
```

## Abstractions

| Protocol | Responsibility |
|----------|----------------|
| `GeocodingProvider` | Free-text place → `LocationCandidate` list |
| `AircraftProvider` | Lat/lon/radius → normalized `Aircraft` list |
| `RouteProvider` | Callsign → `RouteInfo` or `None` |

External API JSON never leaves provider modules. The engine operates only on normalized models.

## Enrichment limit

`RadarEngine` accepts an `enrichment_limit` parameter (default 10). Only the nearest N aircraft with callsigns are enriched. Renderers or CLI flags choose the limit — the engine does not embed display-specific defaults beyond its constructor argument.

## Error semantics

| Failure | Behaviour |
|---------|-----------|
| Aircraft provider down | `RadarEngineError` raised; scan aborts |
| Route lookup fails | Aircraft returned without route fields |
| Missing callsign/altitude | Aircraft still included in snapshot |
| Geocoding failure | Onboarding reports error; no config saved |

## Configuration

Persistent TOML config via `platformdirs`. Validated on load. Corrupted files raise `ConfigError`.
