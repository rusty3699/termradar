# Roadmap

## Phase 1 — Core engine and package foundation ✅

- [x] Installable `src/` package layout
- [x] Domain models (`Location`, `Aircraft`, `RadarSnapshot`, …)
- [x] Haversine distance and bearing calculations
- [x] Nominatim geocoding with candidate selection
- [x] Persistent TOML configuration
- [x] OpenSky aircraft provider
- [x] adsb.lol route enrichment with cache
- [x] `RadarEngine.scan()` pipeline
- [x] Basic CLI onboarding and text output
- [x] Mocked unit tests (no internet required)
- [x] Documentation

## Phase 2 — Terminal radar UI

- [ ] Animated ASCII / Unicode radar display
- [ ] Continuous refresh loop using `refresh_seconds`
- [ ] Compass rose and aircraft markers
- [ ] Keyboard controls (quit, change radius)
- [ ] Richer terminal formatting (colors, tables)

## Phase 3 — Raspberry Pi displays

- [ ] TFT display renderer
- [ ] OLED display renderer
- [ ] GPIO button input
- [ ] systemd service unit
- [ ] Low-power / headless operation

## Phase 4 — Extended platforms

- [ ] Pygame visual radar
- [ ] Telegram bot renderer
- [ ] Web UI
- [ ] Additional aircraft / route providers
- [ ] Optional authentication for rate-limited APIs

## Non-goals (for now)

- ADS-B receiver hardware integration (dump1090 direct feed)
- Flight tracking history / playback
- Multi-user / cloud hosting
