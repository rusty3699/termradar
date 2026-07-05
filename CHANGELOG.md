# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial Phase 1 package foundation with `src/` layout
- Core domain models: `Location`, `LocationCandidate`, `Aircraft`, `RouteInfo`, `RadarSnapshot`
- Haversine `distance_km()` and `bearing_deg()` utilities with unit tests
- `GeocodingProvider` protocol and `NominatimGeocodingProvider` (OpenStreetMap)
- `AircraftProvider` protocol and `OpenSkyAircraftProvider`
- `RouteProvider` protocol, `AdsbLolRouteProvider`, and `CachedRouteProvider`
- `RadarEngine.scan()` pipeline: fetch, geometry, filter, sort, enrich
- TOML configuration storage with validation (`platformdirs`)
- `termradar` CLI with first-run location onboarding
- Basic terminal text renderer
- Comprehensive mocked test suite (no internet required)
- Documentation: README, ARCHITECTURE, ROADMAP, DATA_PROVIDERS, DEVELOPMENT

## [0.1.0] - 2026-07-05

### Added

- Project scaffold and MIT license

[Unreleased]: https://github.com/termradar/termradar/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/termradar/termradar/releases/tag/v0.1.0
