# Architecture

> **One radar engine. Multiple displays.**

The core produces a `RadarSnapshot` on each scan. Renderers draw it; they never fetch data or call external APIs.

## Data flow

```text
GeocodingProvider          (setup / location override only)
        ↓
     Location  (+ timezone)
        ↓
AircraftProvider           (every scan - default: adsb.lol)
        ↓
   RadarEngine  ◄──── CachedRouteProvider ──► AdsbDbRouteProvider
        ↓
   RadarSnapshot
        ↓
   RadarSession  →  TerminalView  →  TerminalRenderer
        ↓
   Terminal output (Rich live UI)
```

A future `FullscreenRenderer` (Phase 3, Raspberry Pi) will consume the same `RadarSnapshot`.

## Scan pipeline

```text
RadarEngine.scan()
  → fetch aircraft (AdsblolAircraftProvider by default)
  → distance_km() + bearing_deg() from radar center
  → filter by radius, sort nearest-first
  → enrich nearest N aircraft (ADSBDB with callsign fallback, cached, rate-limited)
  → infer airline from ICAO callsign prefix when still unknown
  → RadarSnapshot
```

Geocoding and timezone resolution run only during onboarding, `--reset-location`, or `--location` - **not** on refresh.

## Live display loop

```text
RadarSession
  → engine.scan()
  → build TerminalView (location, snapshot, errors, terminal size)
  → TerminalRenderer.render()
  → sleep(refresh_seconds)    # default 5 s, minimum 5 s
```

`RadarSession` owns the loop and keeps the last good snapshot when a scan fails (stale mode). `TerminalRenderer` is stateless per frame.

## Terminal UI layout

Wide terminals (≥ 72 columns): radar panel left, aircraft panel right.

**Radar panel**

| Symbol | Meaning |
|--------|---------|
| `+` | Your location (radar center) |
| Outer dotted ring | Search radius |
| Inner dotted ring | Half of search radius |
| `1`–`5` | Top five nearest aircraft (matches nearby list) |
| `✈` | Other aircraft in range |
| `N` `E` `S` `W` | Compass |

Markers use collision offsets when the ideal grid cell is occupied (ring dot, center, or another marker).

**Nearby aircraft panel**

- **CLOSEST** - full detail for nearest aircraft (callsign, airline, route, distance, bearing, speed, altitude)
- **NEARBY** - compact top-five list: rank, callsign, distance, compass direction

Narrow terminals fall back to a compact aircraft table.

## Package layout

```text
src/termradar/
├── cli.py                     # Entry point, onboarding, provider wiring
├── session.py                 # Live refresh loop
├── core/
│   ├── engine.py              # Scan orchestration
│   ├── models.py              # Location, Aircraft, RadarSnapshot, …
│   ├── limits.py              # Rate-limit constants
│   ├── rate_limit.py          # Rolling minute limiter
│   ├── airline.py             # ICAO prefix → airline inference
│   ├── distance.py / bearing.py
│   ├── location.py / timezone.py
│   └── …
├── providers/
│   ├── geocoding.py           # Nominatim
│   ├── aircraft.py            # adsb.lol + OpenSky
│   ├── adsbdb.py              # ADSBDB enrichment
│   └── routes.py              # CachedRouteProvider, adsb.lol routeset
├── config/storage.py          # TOML load/save, validation
└── renderers/
    ├── formatting.py          # Display strings
    ├── bearing_display.py     # Compass labels
    ├── location_display.py    # Short location header
    ├── radar_coords.py        # Polar → grid
    ├── radar_canvas.py        # ASCII radar + markers
    ├── terminal_ui.py         # Rich layout
    ├── terminal_view.py       # Per-frame view model
    └── time_display.py        # Local time in location timezone
```

## Boundaries

| Layer | Does | Does not |
|-------|------|----------|
| Providers | HTTP, parsing, caching, rate limiting | Display, geometry |
| `RadarEngine` | Fetch, filter, sort, enrich | Terminal drawing |
| `CachedRouteProvider` | TTL cache + 30/min cap | Aircraft positions |
| `TerminalRenderer` | Layout, radar, formatting | API calls |
| `radar_to_grid()` | Bearing/distance → grid cell | Fetch or enrich |

## Error handling

| Failure | Behaviour |
|---------|-----------|
| Aircraft provider down | Error state; last snapshot shown as stale if available |
| ADSBDB miss / 404 | Aircraft shown; airline may come from callsign prefix |
| Enrichment rate limit | Skip remaining lookups this scan; retry later |
| Missing altitude / route | Graceful fallbacks (`-`, `Unknown airline`, `Route unavailable`) |
| Ctrl+C | Clean exit |

## Configuration

Stored at `~/.config/termradar/config.toml` (platformdirs).

| Key | Default | Notes |
|-----|---------|-------|
| `location.*` | - | Set during onboarding |
| `radar.radius_km` | 15 | 1–250 km |
| `radar.refresh_seconds` | 5 | 5–300; values &lt; 5 upgraded on load |

CLI overrides (`--location`, `--radius`, `--refresh`, `--aircraft-provider`, `--enrichment-limit`) apply to the current run only unless `--reset-location` re-saves config.

## Internal limits and caching

See [DATA_PROVIDERS.md](DATA_PROVIDERS.md) for full detail. Summary:

- **Refresh:** 5 s default and minimum → one adsb.lol request per cycle
- **Enrichment:** 30 ADSBDB requests/minute max, 10 nearest aircraft per scan, 12 h / 30 min cache
- **Geocoding:** 1 Nominatim request/second, setup only
