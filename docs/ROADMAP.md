# Roadmap

## Phase 1 - Core Engine

**Status: Completed**

- [x] Package layout, domain models, geometry
- [x] Geocoding, aircraft and route providers
- [x] `RadarEngine.scan()`, config storage, CLI foundation
- [x] Tests and documentation

## Phase 2 - Terminal MVP

**Status: Completed**

- [x] Live terminal UI (Rich panels, radar plot, nearest-aircraft panel)
- [x] Live refresh loop, CLI overrides, error/stale states
- [x] PyPI-ready packaging, 97 tests, documentation

---

## Phase 3 - Raspberry Pi Fullscreen and TFT Display Support

**Status: Planned**

The goal of Phase 3 is to extend TermRadar from a terminal-only experience into a graphical Raspberry Pi display application without duplicating or changing the existing radar engine.

The central architecture remains:

```text
Aircraft Provider
        ↓
   RadarEngine
        ↓
   RadarSnapshot
        ↓
   Renderer Layer
      ├── TerminalRenderer
      └── FullscreenRenderer
                 ↓
         Raspberry Pi Display
```

The Raspberry Pi display must consume the same `RadarSnapshot` already used by the terminal renderer.

No Raspberry Pi renderer should independently:

* fetch aircraft data;
* perform geocoding;
* call route enrichment APIs;
* calculate distance;
* calculate bearing;
* filter aircraft;
* sort aircraft.

The core rule remains:

> One radar engine. Multiple displays.

### Objectives

Phase 3 should add a graphical fullscreen display mode suitable for Raspberry Pi systems connected to:

* HDMI displays;
* DSI displays;
* small TFT screens;
* other framebuffer-backed displays where supported.

The first Raspberry Pi implementation should focus on a generic fullscreen graphical renderer rather than device-specific GPIO display drivers.

### Planned CLI Experience

Terminal mode should continue to work normally:

```bash
termradar
```

or explicitly:

```bash
termradar --display terminal
```

Fullscreen mode should be available through:

```bash
termradar --display fullscreen
```

Graphical dependencies should remain optional.

A possible installation flow is:

```bash
pip install "termradar[fullscreen]"
```

The default installation:

```bash
pip install termradar
```

should remain lightweight and terminal-focused.

### Fullscreen Renderer

Add a graphical renderer that displays:

* radar visualization;
* current location;
* current time;
* live/stale data status;
* aircraft count;
* configured radius;
* nearest aircraft callsign;
* airline information where available;
* route information where available;
* distance;
* altitude;
* speed;
* bearing.

Example conceptual layout:

```text
┌──────────────────────────────────────────────┐
│ TERMRADAR                        12:42:07     │
│ Dadar, Mumbai                     LIVE ●     │
│                                              │
│              N                               │
│         .-----------.      CLOSEST           │
│       .'    ✈      '.                        │
│      /               \     6E221             │
│  W  |      +     ✈    | E   IndiGo           │
│      \               /     DEL → BOM         │
│       '.    ✈      .'      4.2 km            │
│         '-----------'      8,350 ft          │
│              S                               │
│                                              │
│ 3 AIRCRAFT IN RANGE              RADIUS 15KM │
└──────────────────────────────────────────────┘
```

The exact layout may vary based on screen size.

### Display Scaling

The fullscreen renderer should not assume one fixed resolution.

Layout calculations should support reasonable scaling across common small-display sizes.

The renderer should handle:

* different aspect ratios;
* different resolutions;
* resized development windows;
* reduced information density on smaller screens.

Display-specific coordinate conversion should remain inside renderer-related code.

Conceptually:

```text
distance_km
+
bearing_deg
        ↓
screen coordinate mapping
        ↓
graphical radar position
```

### Graphical Framework

Use a lightweight graphical framework suitable for Raspberry Pi and desktop development.

A likely option is:

```text
pygame-ce
```

or another clearly justified lightweight alternative.

The renderer should be testable on a normal Linux, macOS, or Windows development environment where practical.

Raspberry Pi hardware should not be required for most automated tests.

### Refresh Architecture

The graphical frame rate and aircraft refresh rate must remain separate.

Conceptually:

```text
Graphics rendering
30–60 FPS or event-driven redraw
        │
        │ separate from
        ▼
Aircraft data refresh
every configured N seconds
```

TermRadar must not request aircraft data every graphical frame.

The display loop should:

1. process display events;
2. render the latest available `RadarSnapshot`;
3. periodically request a fresh snapshot;
4. replace or update the displayed data;
5. preserve responsive display behavior.

If synchronous network calls cause visible freezes, introduce only the minimum concurrency needed to keep the UI responsive.

Avoid unnecessary architectural complexity.

### Display Mode Selection

Add renderer selection through configuration or CLI.

Example:

```bash
termradar --display terminal
```

```bash
termradar --display fullscreen
```

The renderer selection architecture should make future additions possible:

```text
terminal
fullscreen
ssd1306
sh1106
eink
web
```

Only `terminal` and `fullscreen` are in scope for this phase.

### Optional Dependencies

Do not make graphical packages mandatory for terminal users.

Use package extras or equivalent dependency separation.

Conceptually:

```toml
[project.optional-dependencies]

fullscreen = [
    "pygame-ce",
]
```

Terminal users should still be able to install:

```bash
pip install termradar
```

without unnecessary graphical or Raspberry Pi dependencies.

### Raspberry Pi Compatibility

The first Raspberry Pi phase should avoid hard-coded assumptions such as:

```text
/dev/fb0
/home/pi
specific GPIO pins
one exact TFT controller
one fixed resolution
```

Where hardware-specific configuration is necessary, it should be:

* configurable;
* detected where possible;
* clearly documented.

Phase 3 focuses on fullscreen display support.

Direct drivers for displays such as SSD1306, SH1106, Waveshare, and e-paper panels belong to later phases.

### Raspberry Pi Documentation

Create or maintain:

```text
docs/RASPBERRY_PI.md
```

Document:

* supported or tested Raspberry Pi versions;
* operating-system assumptions;
* Python version requirements;
* installation steps;
* virtual environment setup;
* fullscreen dependency installation;
* running TermRadar manually;
* configuring location and radar settings;
* troubleshooting display issues;
* launching fullscreen mode;
* known untested hardware combinations.

Documentation must distinguish clearly between:

```text
Tested
Expected to work
Planned
Not yet verified
```

Do not claim hardware support that has not been validated.

### Automatic Startup

After fullscreen mode works reliably, document optional startup through `systemd`.

Conceptual flow:

```text
Raspberry Pi boots
        ↓
network becomes available
        ↓
TermRadar service starts
        ↓
fullscreen renderer launches
        ↓
radar refresh continues automatically
```

Provide an example service configuration.

Do not hard-code user-specific paths.

Document how users should adapt:

* username;
* virtual environment path;
* TermRadar executable path;
* graphical display environment;
* working directory.

Automatic service installation should not occur without explicit user action.

### Display Lifecycle

The fullscreen renderer should shut down cleanly.

Handle:

* Ctrl+C;
* graphical window close events;
* renderer cleanup;
* application shutdown;
* recoverable provider failures.

The application should not leave graphical resources or terminal state corrupted after exit.

### Error and Empty States

The graphical renderer should provide appropriate visual states for:

* no nearby aircraft;
* aircraft provider unavailable;
* stale snapshot;
* route information unavailable;
* invalid configuration.

Examples:

```text
NO AIRCRAFT DETECTED
WITHIN 15 KM
```

or:

```text
DATA TEMPORARILY UNAVAILABLE

Showing last known aircraft data
Last update: 12:41:57
```

The graphical renderer should preserve the same graceful degradation principles as the terminal renderer.

### Testing

Automated tests should cover display-independent graphical logic where practical.

At minimum:

* renderer selection;
* `--display` CLI parsing;
* invalid display mode;
* radar-to-screen coordinate mapping;
* cardinal direction mapping;
* resolution scaling;
* layout calculations;
* aircraft near center;
* aircraft near radius edge;
* overlapping aircraft;
* empty snapshot rendering logic.

The default test suite should not require:

* physical Raspberry Pi hardware;
* a TFT display;
* GPIO;
* an active display server where avoidable.

Graphical logic should be separated from hardware initialization where practical.

### Documentation Updates

Phase 3 implementation should update:

```text
README.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/DEVELOPMENT.md
docs/RASPBERRY_PI.md
CHANGELOG.md
```

The README should clearly show the two supported modes once Phase 3 is complete:

```text
Terminal mode
Fullscreen mode
```

The architecture documentation should reflect:

```text
AircraftProvider
        ↓
RadarEngine
        ↓
RadarSnapshot
        ↓
Renderer Interface
   ┌──────────┴───────────┐
   ↓                      ↓
TerminalRenderer    FullscreenRenderer
                           ↓
                     Raspberry Pi
```

### Phase 3 Definition of Done

Phase 3 is complete when:

* [ ] Existing terminal mode still works unchanged.
* [ ] `termradar --display terminal` works.
* [ ] `termradar --display fullscreen` works.
* [ ] The fullscreen renderer consumes `RadarSnapshot`.
* [ ] No aircraft API logic exists inside the fullscreen renderer.
* [ ] No route API logic exists inside the fullscreen renderer.
* [ ] No distance or bearing calculation is duplicated in the fullscreen renderer.
* [ ] Graphical dependencies are optional.
* [ ] Radar aircraft positions are mapped correctly to screen coordinates.
* [ ] Cardinal directions are correct.
* [ ] Nearest-aircraft details are displayed.
* [ ] Aircraft count and radius are displayed.
* [ ] Empty-airspace state works.
* [ ] Provider-failure state works.
* [ ] Stale-data state is understandable.
* [ ] Graphical refresh and aircraft refresh are separated.
* [ ] Display exit is clean.
* [ ] Layout scales reasonably across supported resolutions.
* [ ] Automated tests do not require Raspberry Pi hardware.
* [ ] Raspberry Pi installation documentation exists.
* [ ] Optional `systemd` startup documentation exists.
* [ ] Existing tests continue to pass.
* [ ] Linting passes.
* [ ] Formatting checks pass.
* [ ] Documentation matches actual implementation.
* [ ] CHANGELOG is updated.

### Out of Scope for Phase 3

The following should remain outside this phase:

* SSD1306 OLED support;
* SH1106 OLED support;
* direct GPIO display control;
* Waveshare-specific display drivers;
* e-paper support;
* Telegram display commands;
* RTL-SDR integration;
* local `readsb` provider;
* local `dump1090` provider;
* alert notifications;
* aircraft tracking commands;
* web dashboard.

These should be handled in later phases after the fullscreen Raspberry Pi renderer is stable.

### Expected Outcome

At the end of Phase 3, TermRadar should support two first-class experiences:

```text
Desktop / Server / SSH
        ↓
TerminalRenderer
```

and:

```text
Raspberry Pi
        ↓
FullscreenRenderer
        ↓
TFT / HDMI / DSI display
```

Both modes must use the same:

```text
providers
geocoding
configuration
RadarEngine
RadarSnapshot
route enrichment
filtering
sorting
caching
```

Only the display layer should differ.

---

## Phase 4 - OLED Displays

**Status: Planned**

- SSD1306 / SH1106 renderers
- Minimal single-aircraft layouts
- GPIO button input (where applicable)

## Phase 5 - Local ADS-B Sources

**Status: Planned**

- RTL-SDR, `readsb`, `dump1090` feed providers
- Local receiver as alternative aircraft source

## Phase 6 - Alerts and Integrations

**Status: Planned**

- Overhead aircraft alerts
- Telegram bot
- Web UI
