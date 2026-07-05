# Roadmap

## Phase 1 — Core Engine

**Status: Completed**

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

## Phase 2 — Terminal MVP

**Status: Completed**

- [x] Polished terminal UI with Rich (panels, layout)
- [x] Aircraft table with graceful missing-field handling
- [x] Nearest-aircraft panel
- [x] ASCII radar visualization from distance + bearing
- [x] Testable `radar_to_grid()` coordinate mapping
- [x] Live refresh loop with configurable interval
- [x] Clean Ctrl+C exit
- [x] Error and stale-data states
- [x] CLI overrides (`--location`, `--radius`, `--refresh`)
- [x] Improved first-run and returning-user UX
- [x] PyPI-ready packaging metadata and local wheel validation
- [x] Documentation updates

## Phase 3 — Raspberry Pi Fullscreen/TFT

**Status: Planned**

- [ ] Fullscreen TFT display renderer
- [ ] GPIO button input
- [ ] systemd service unit
- [ ] Low-power / headless operation

## Phase 4 — OLED Displays

**Status: Planned**

- [ ] OLED display renderer
- [ ] Minimal single-aircraft layout
- [ ] Low refresh enrichment limits

## Phase 5 — Local ADS-B Sources

**Status: Planned**

- [ ] RTL-SDR integration
- [ ] `readsb` / `dump1090` feed provider
- [ ] Local receiver as alternative aircraft source

## Phase 6 — Alerts and Overhead Mode

**Status: Planned**

- [ ] Aircraft overhead alerts
- [ ] Notification integrations
- [ ] Telegram bot
- [ ] Web UI

## Non-goals (for now)

- Pygame visual radar (may be reconsidered post-Pi MVP)
- Multi-user / cloud hosting
