# Architecture

> **One radar engine. Multiple displays.**

Renderers consume `RadarSnapshot`. They never fetch aircraft data, geocode, enrich routes, or compute distance/bearing.

## Data flow

```text
GeocodingProvider          (setup only)
        ↓
     Location
        ↓
AircraftProvider
        ↓
   RadarEngine  ◄──── RouteProvider
        ↓
   RadarSnapshot
        ↓
   Renderer layer
        ↓
   Terminal output
```

A future `FullscreenRenderer` (Phase 3) will consume the same `RadarSnapshot`.

## Scan pipeline

```text
RadarEngine.scan()
  → fetch aircraft (provider)
  → distance_km() + bearing_deg()
  → filter by radius, sort nearest-first
  → enrich routes (cached, limited count)
  → RadarSnapshot
```

Geocoding runs only during onboarding, `--reset-location`, or `--location` override — not on refresh.

## Live display loop

```text
RadarSession
  → engine.scan()
  → TerminalView
  → TerminalRenderer.render()
  → sleep(refresh_seconds)
```

`RadarSession` owns the refresh loop. `TerminalRenderer` is stateless per frame.

## Package layout

```text
src/termradar/
├── cli.py                 # CLI and onboarding
├── session.py             # Live refresh orchestration
├── core/                  # Models, engine, geometry
├── providers/             # Geocoding, aircraft, routes
├── config/                # TOML persistence
└── renderers/
    ├── formatting.py      # Display formatters
    ├── radar_coords.py    # Polar → grid mapping
    ├── radar_canvas.py    # ASCII radar
    ├── terminal_ui.py     # Rich layout
    └── terminal_view.py   # Per-frame view model
```

## Boundaries

| Layer | Does | Does not |
|-------|------|----------|
| Providers | HTTP, parsing, unit conversion | Display logic |
| `RadarEngine` | Fetch, geometry, filter, sort, enrich | Terminal drawing |
| `TerminalRenderer` | Layout, radar plot, formatting | API calls, Haversine |
| `radar_to_grid()` | Map bearing/distance to grid cells | Filter or sort aircraft |

## Error handling

| Failure | Behaviour |
|---------|-----------|
| Aircraft provider down | Error UI; keep last snapshot as stale if available |
| Route lookup fails | Aircraft shown without route fields |
| Missing metadata | Graceful fallbacks (`—`, `Unknown`) |
| Ctrl+C | Clean exit |

## Configuration

```text
first run / --reset-location  →  save config.toml
termradar                     →  load config, start session
--location / --radius / --refresh  →  override for current run only
```

Route cache is in-memory for the CLI process lifetime. Enrichment is capped by `enrichment_limit` (default 10).
