# Data providers

Providers are pluggable. External API JSON never leaves provider modules.

## Geocoding — Nominatim (OpenStreetMap)

| | |
|---|---|
| Module | `termradar.providers.geocoding.NominatimGeocodingProvider` |
| Endpoint | `https://nominatim.openstreetmap.org/search` |
| When used | Onboarding, `--reset-location`, `--location` only |
| Auth | None (custom User-Agent required) |

Accepts free-text queries (`Mumbai`, `400014`, `Dadar East Hindu Colony`). Returns up to 5 candidates. 10 s timeout, no retries.

© [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors. See [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).

---

## Aircraft — OpenSky Network

| | |
|---|---|
| Module | `termradar.providers.aircraft.OpenSkyAircraftProvider` |
| Endpoint | `https://opensky-network.org/api/states/all` |
| When used | Every `RadarEngine.scan()` |
| Auth | Anonymous (rate-limited) |

Sends a bounding box; the engine filters precisely by radius. Altitude and callsign may be missing.

Data by the [OpenSky Network](https://opensky-network.org).

---

## Routes — adsb.lol

| | |
|---|---|
| Module | `termradar.providers.routes.AdsbLolRouteProvider` |
| Endpoint | `https://api.adsb.lol/api/0/routeset` |
| When used | Enrichment for nearest N aircraft with callsigns |
| Auth | None |

POST JSON array of callsigns. HTTP 201 with empty body means no route — handled silently. Results cached in-memory for the session.

Route data is best-effort. Many callsigns return no route.

---

## Caching and refresh

```text
each refresh → RadarEngine.scan()
             → aircraft fetch (always)
             → route lookup only for uncached callsigns (up to enrichment_limit)
```

Default enrichment limit: 10 (CLI: `--enrichment-limit`).

---

## Adding a provider

1. Implement the protocol in `providers/base.py`
2. Map API responses to core models inside the provider
3. Add mocked HTTP tests
4. Document here with attribution and limits
