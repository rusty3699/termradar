# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-07-05

### Fixed

- README demo GIF uses an absolute URL so it renders on PyPI

## [0.3.1] - 2026-07-05

### Changed

- PyPI package metadata: author, keywords, and documentation URL

## [0.3.0] - 2026-07-05

### Added

- adsb.lol v2 as default live aircraft provider (`--aircraft-provider opensky` for OpenSky)
- ADSBDB enrichment for routes and airlines (replaces adsb.lol routeset in CLI)
- ICAO callsign prefix airline inference when enrichment has no airline
- Top-five nearby aircraft list with numbered radar markers (`1`–`5`)
- Rate limits: 5 s min / 5 s default refresh, 30 ADSBDB req/min, enrichment TTL cache
- Nominatim 1 req/s throttle; legacy `refresh_seconds < 5` auto-upgraded on load
- Local time display via `timezonefinder` and optional `timezone` in config
- README demo GIF and VHS tape (`docs/assets/demo-quick.*`)

### Changed

- Right panel: **CLOSEST** detail + **NEARBY** compact list (title: NEARBY AIRCRAFT)
- Radar marker collision handling (offsets when on ring dots or overlapping)
- Airline display shortens trailing ` Airlines` / ` Air Lines`
- Documentation overhaul for providers, internal limits, and usage
- README quick start includes `pip install termradar`
- Provider User-Agent strings track package `__version__`

### Fixed

- OpenSky HTTP 429 at aggressive refresh (adsb.lol default + minimum 5 s refresh)
- ADSBDB HTTP 404 logged as debug, not terminal warning
- ADSBDB route lookup falls back to callsign endpoint when aircraft hex lookup misses
- Aircraft markers skipped on ring dots

### Dependencies

- Added `timezonefinder` for coordinate → timezone lookup

## [0.2.0] - 2026-07-05

### Added

- Live terminal UI with Rich panels, radar visualization, and nearest-aircraft panel
- `RadarSession` live refresh loop with configurable interval
- CLI overrides: `--location`, `--radius` / `--radius-km`, `--refresh` (current run only)
- Testable `radar_to_grid()` coordinate mapping and ASCII radar canvas
- Graceful handling of missing aircraft metadata in the UI
- Stale snapshot display when aircraft provider temporarily fails
- PyPI-ready project metadata and local wheel build validation

### Changed

- `termradar` runs a live refresh loop instead of a single scan
- Route provider accepts HTTP 201 responses from adsb.lol
- Improved first-run onboarding with refresh interval prompt

### Fixed

- Empty adsb.lol route responses (HTTP 201, no body) no longer log false "malformed" warnings
- Terminal display clears screen before Live render to avoid duplicate headers

### Dependencies

- Added `rich` for terminal layout and live display

## [0.1.0] - 2026-07-05

### Added

- Core radar engine, providers, config storage, CLI, and tests

[Unreleased]: https://github.com/rusty3699/termradar/compare/v0.3.2...HEAD
[0.3.2]: https://github.com/rusty3699/termradar/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/rusty3699/termradar/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/rusty3699/termradar/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rusty3699/termradar/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rusty3699/termradar/releases/tag/v0.1.0
