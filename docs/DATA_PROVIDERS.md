# Data providers

TermRadar uses pluggable providers so data sources can be swapped without touching the radar engine.

## Geocoding — Nominatim (OpenStreetMap)

| | |
|---|---|
| **Module** | `termradar.providers.geocoding.NominatimGeocodingProvider` |
| **Endpoint** | `https://nominatim.openstreetmap.org/search` |
| **When used** | First-run setup, `--reset-location` only |
| **Auth** | None (custom User-Agent required) |

### Behaviour

- Accepts free-text queries (`Mumbai`, `Baner, Pune`, `Pune Airport`)
- Returns up to 5 `LocationCandidate` results
- 10 s HTTP timeout; no automatic retries
- Raises `GeocodingError` on network failure, timeout, or malformed response

### Attribution

© [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors. Nominatim [usage policy](https://operations.osmfoundation.org/policies/nominatim/) applies — avoid bulk geocoding; TermRadar geocodes only during setup.

---

## Aircraft — OpenSky Network

| | |
|---|---|
| **Module** | `termradar.providers.aircraft.OpenSkyAircraftProvider` |
| **Endpoint** | `https://opensky-network.org/api/states/all` |
| **When used** | Every `RadarEngine.scan()` |
| **Auth** | None for anonymous access (rate-limited) |

### Field mapping

| OpenSky state index | Aircraft field |
|---------------------|----------------|
| `[0]` icao24 | `hex_id` |
| `[1]` callsign | `callsign` (stripped) |
| `[6]` latitude | `latitude` |
| `[5]` longitude | `longitude` |
| `[7]` baro_altitude (m) | `altitude_ft` |
| `[9]` velocity (m/s) | `ground_speed_knots` |
| `[10]` true_track | `track_deg` |

A bounding box approximating the search radius is sent to the API; precise radius filtering happens in the engine.

### Known limits

- Anonymous API rate limits apply
- Coverage depends on OpenSky feeder network density
- Altitude may be missing for some aircraft
- Callsigns may be empty or stale

### Attribution

Data provided by the [OpenSky Network](https://opensky-network.org).

---

## Route enrichment — adsb.lol

| | |
|---|---|
| **Module** | `termradar.providers.routes.AdsbLolRouteProvider` |
| **Endpoint** | `https://api.adsb.lol/api/0/routeset` |
| **When used** | During scan for nearest N aircraft with callsigns |
| **Auth** | None |

### Behaviour

- POST JSON array of callsigns
- Parses `_airport_codes_iata` (e.g. `BOM-DEL`) into origin/destination
- Returns `None` on failure — scan continues
- Wrapped by `CachedRouteProvider` to avoid repeat lookups

### Caching

```text
callsign → cache hit? → return cached RouteInfo
                ↓ miss
           route API → store → return
```

In-memory cache for Phase 1. Cache key is uppercased callsign. Failed lookups (`None`) are cached too.

### Enrichment limit

Configurable via `RadarEngine(enrichment_limit=…)` or CLI `--enrichment-limit`. Suggested defaults by display (chosen by caller, not engine):

| Display | Suggested limit |
|---------|-----------------|
| OLED | 1 |
| TFT | 5 |
| Terminal | 10 |
| Web | higher |

### Known limits

- Route data may be incomplete or outdated
- Not all callsigns have route information
- API availability not guaranteed

---

## Abstraction rationale

Providers isolate:

- URL construction and HTTP details
- Unit conversion (metres → feet, m/s → knots)
- Null / missing field handling
- API-specific JSON parsing

The engine sees only normalized `Aircraft` and `RouteInfo` objects. Tests mock HTTP at the provider boundary — no live network calls in CI.

## Adding a provider

1. Implement the relevant protocol in `termradar.providers.base`
2. Map external responses to core models inside the provider module
3. Add mocked HTTP tests
4. Document the source here with attribution and limits
