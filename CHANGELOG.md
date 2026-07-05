# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Route provider treats adsb.lol HTTP 201 empty responses as "no route" without warning spam
- Live terminal display clears screen before rendering to avoid duplicate TERMRADAR headers

## [0.2.0] - 2026-07-05

### Added

- Polished terminal UI with Rich panels, radar visualization, and nearest-aircraft panel
- Aircraft table with graceful handling of missing callsign, altitude, speed, route, and airline
- Testable `radar_to_grid()` coordinate mapping and ASCII radar canvas
- Live refresh loop via `RadarSession` with configurable interval
- CLI overrides: `--location`, `--radius` / `--radius-km`, `--refresh` (current run only)
- Improved first-run onboarding with refresh interval prompt
- Compact layout fallback for narrow terminals
- Stale snapshot display when aircraft provider temporarily fails
- PyPI-ready project metadata and local wheel build validation

### Changed

- `termradar` now runs a live refresh loop instead of a single scan
- Route provider accepts HTTP 201 responses from adsb.lol
- Version bumped to 0.2.0

### Dependencies

- Added `rich` for terminal layout and live display

## [0.1.0] - 2026-07-05

### Added

- Initial Phase 1 package foundation with `src/` layout
- Core domain models, `RadarEngine.scan()`, providers, config, CLI, and tests

[Unreleased]: https://github.com/rusty3699/termradar/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/rusty3699/termradar/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rusty3699/termradar/releases/tag/v0.1.0
