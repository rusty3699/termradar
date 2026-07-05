# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/rusty3699/termradar/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/rusty3699/termradar/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rusty3699/termradar/releases/tag/v0.1.0
