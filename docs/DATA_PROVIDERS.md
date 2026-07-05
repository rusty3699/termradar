# Data providers

TermRadar talks to three external services. Provider modules own all HTTP and JSON parsing - nothing else in the codebase calls these APIs directly.

Constants below live in `src/termradar/core/limits.py` and are enforced in code.

---

## Summary

| Role | Default provider | When it runs |
|------|------------------|--------------|
| Geocoding | Nominatim (OpenStreetMap) | First setup, `--reset-location`, `--location` only |
| Live aircraft | adsb.lol v2 | Every refresh (`RadarEngine.scan()`) |
| Route / airline enrichment | ADSBDB | Cache miss only, nearest aircraft with callsigns |

Optional: `--aircraft-provider opensky` swaps the live aircraft source. The adsb.lol routeset API remains in the codebase for custom integrations but is **not** used by the CLI.

---

## Rate limits (enforced by TermRadar)

TermRadar applies conservative limits so the CLI stays polite to free public APIs.

| Setting | Value | Where enforced |
|---------|-------|----------------|
| Default refresh interval | **5 seconds** | Config default, onboarding |
| Minimum refresh interval | **3 seconds** | `validate_refresh_seconds()` - `--refresh 1` is rejected |
| Maximum refresh interval | **300 seconds** | Config validation |
| Enrichment requests | **30 / minute** (rolling) | `CachedRouteProvider` + `MinuteRateLimiter` |
| Enrichment burst per scan | **10 aircraft** (default) | `RadarEngine.enrichment_limit` / `--enrichment-limit` |
| Enrichment cache (hit) | **12 hours** | `CachedRouteProvider` success TTL |
| Enrichment cache (miss) | **30 minutes** | `CachedRouteProvider` failure TTL |
| Geocoding interval | **1 request / second** | `NominatimGeocodingProvider` |

### What one refresh cycle does

With defaults (5 s refresh, 10 km radius, adsb.lol + ADSBDB):

```text
every 5 seconds:
  1 × GET  adsb.lol /v2/point/{lat}/{lon}/{radius_nm}
  0–10 × GET ADSBDB  (only for callsigns not already cached, capped at 30/min)

never during refresh:
  Nominatim geocoding
```

**Example - 8 aircraft appear, all new callsigns:**

```text
Refresh 1:  1 adsb.lol + up to 8 ADSBDB (burst capped at 10)
Refresh 2+: 1 adsb.lol + 0 ADSBDB (all cached for 12 h on success, 30 min on failure)
```

If the enrichment rate limit is hit mid-scan, remaining lookups are skipped for that scan (aircraft still appear; route/airline fields may be empty until the next cache miss after the window resets).

### Legacy config

Saved `refresh_seconds` below 3 (e.g. `1` from older versions) is automatically upgraded to **5** on load and written back to `config.toml`.

---

## Geocoding - Nominatim (OpenStreetMap)

| | |
|---|---|
| Module | `termradar.providers.geocoding.NominatimGeocodingProvider` |
| Endpoint | `GET https://nominatim.openstreetmap.org/search` |
| Auth | None - custom `User-Agent: TermRadar/…` required |

**When used:** onboarding, `--reset-location`, `--location` override. **Never** called from the live refresh loop.

**Behaviour:** Free-text query → up to 5 candidates. 10 s timeout. Minimum 1 s between requests. Timezone is resolved from coordinates (`timezonefinder`) and stored in config when available.

© [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors - [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).

---

## Aircraft - adsb.lol (default)

| | |
|---|---|
| Module | `termradar.providers.aircraft.AdsbLolAircraftProvider` |
| Endpoint | `GET https://api.adsb.lol/v2/point/{lat}/{lon}/{radius_nm}` |
| Auth | None |

**When used:** every `RadarEngine.scan()` (CLI default).

**Request:** Your search radius in km is converted to nautical miles (`ceil(km / 1.852)`, clamped 1–250 nm). The engine still filters aircraft precisely by your km radius after fetch.

**Response fields used:** `hex`, `flight` (callsign), `lat`, `lon`, `alt_baro`, `gs` (knots), `track`, `r` (registration), `t` (type). Privacy-masked callsigns (`@@@@@@@@`) are treated as unknown.

Data by [adsb.lol](https://adsb.lol) - [ODbL](https://opendatacommons.org/licenses/odbl/1-0/).

**Switch provider:**

```bash
termradar --aircraft-provider opensky
```

---

## Aircraft - OpenSky Network (optional)

| | |
|---|---|
| Module | `termradar.providers.aircraft.OpenSkyAircraftProvider` |
| Endpoint | `GET https://opensky-network.org/api/states/all` |
| Auth | Anonymous (heavily rate-limited) |

Bounding-box fetch; engine filters by radius. Prefer adsb.lol for frequent refresh - OpenSky anonymous access often returns HTTP 429 at short intervals.

Data by the [OpenSky Network](https://opensky-network.org).

---

## Enrichment - ADSBDB (default)

| | |
|---|---|
| Module | `termradar.providers.adsbdb.AdsbDbRouteProvider` |
| Wrapper | `termradar.providers.routes.CachedRouteProvider` |
| Endpoints | `GET /v0/callsign/{callsign}` |
| | `GET /v0/aircraft/{hex}?callsign={callsign}` when hex is known |
| Auth | None |

**When used:** after each aircraft fetch, for the nearest N aircraft that have callsigns (`N` = `--enrichment-limit`, default 10). Only on **cache miss**.

**Returns when known:** airline name, origin IATA/ICAO, destination IATA/ICAO.

**Unknown data:** HTTP 404 with `{"response":"unknown callsign"}` is normal - logged at debug only, not shown in the UI.

**Callsign prefix fallback:** if ADSBDB has no airline, TermRadar infers from the ICAO prefix (`AIC` → Air India, `IGO` → IndiGo, `AKJ` → Akasa Air, …). Route and airline are resolved **independently** - you can see airline without route and vice versa.

**Aircraft owner fallback:** combined aircraft lookup may return `registered_owner` when no flight route exists.

Flight route data includes work by David Taylor and Jim Mason - see [adsbdb.com](https://adsbdb.com).

External ADSBDB tiers (for reference): 512+ feeders ≈ 60 req/min; TermRadar caps at **30/min** internally regardless.

---

## Enrichment - adsb.lol routeset (not CLI default)

| | |
|---|---|
| Module | `termradar.providers.routes.AdsbLolRouteProvider` |
| Endpoint | `POST https://api.adsb.lol/api/0/routeset` |

Available for custom integrations. HTTP 201 with an empty body means “no route”. Not wired into the default CLI pipeline.

---

## Per-scan pipeline

```text
RadarEngine.scan()
  │
  ├─► AircraftProvider.get_nearby(lat, lon, radius_km)     [always]
  │
  ├─► distance_km() + bearing_deg() on each aircraft
  ├─► filter by radius, sort nearest-first
  │
  └─► for nearest enrichment_limit aircraft with callsign:
        CachedRouteProvider.lookup_route(callsign, hex_id=…)
          ├─ cache hit  → return cached RouteInfo | None
          ├─ rate limit → skip (no API call)
          └─ cache miss → AdsbDbRouteProvider → cache result
        infer_airline_from_callsign() if airline still empty
  │
  └─► RadarSnapshot
```

---

## Adding a provider

1. Implement the protocol in `providers/base.py` (`GeocodingProvider`, `AircraftProvider`, or `RouteProvider`)
2. Map API responses to `LocationCandidate`, `Aircraft`, or `RouteInfo` inside the provider module
3. Add mocked HTTP tests under `tests/`
4. Document endpoints, attribution, and limits in this file
