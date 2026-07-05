Output docs/assets/demo-setup.gif

Set Shell bash
Set Width 1500
Set Height 950
Set FontSize 20
Set CursorBlink false

Env XDG_CONFIG_HOME "/tmp/termradar-vhs-config"


# ==================================================
# Hidden preparation
# ==================================================

Hide

Type "rm -rf /tmp/termradar-vhs-config /tmp/termradar-demo-venv"
Enter
Sleep 2s

Type "python3 -m venv /tmp/termradar-demo-venv && echo VENV_READY"
Enter
Wait+Screen@300s /VENV_READY/

Type "source /tmp/termradar-demo-venv/bin/activate"
Enter
Sleep 2s

Type "pip install httpx platformdirs rich timezonefinder tomli-w && echo DEPS_READY"
Enter
Wait+Screen@900s /DEPS_READY/

Type "clear"
Enter
Sleep 2s


# ==================================================
# Visible demo starts
# ==================================================

Show

# Activate clean environment
Type@220ms "source /tmp/termradar-demo-venv/bin/activate"
Sleep 3s
Enter
Sleep 4s


# ==================================================
# PyPI installation
# ==================================================

Type@240ms "pip install --no-deps termradar && echo INSTALL_COMPLETE"
Sleep 3s
Enter

# Show the beginning of pip install
Sleep 4s

# Hide the boring middle of installation
Hide

Wait+Screen@300s /INSTALL_COMPLETE/

# Resume recording at completed installation state
Show

Sleep 5s


# ==================================================
# Launch TermRadar
# ==================================================

Type@260ms "termradar"
Sleep 4s
Enter

Wait+Screen@60s /Location:/

# Let user read welcome screen
Sleep 5s


# ==================================================
# Location
# ==================================================

Type@240ms "Andheri, Mumbai"
Sleep 3s
Enter

Wait+Screen@90s /Choose \[1\]:/

# Let location choices stay visible
Sleep 6s


# ==================================================
# Select Andheri East
# ==================================================

Type@350ms "2"
Sleep 3s
Enter


# ==================================================
# Search radius
# ==================================================

Wait+Screen@60s /Search radius/

Sleep 4s

Type@350ms "10"
Sleep 3s
Enter


# ==================================================
# Refresh interval
# ==================================================

Wait+Screen@60s /Refresh interval/

Sleep 4s

Type@350ms "5"
Sleep 3s
Enter


# ==================================================
# Live radar
# ==================================================

Wait+Screen@120s /TERMRADAR/

# Keep radar visible long enough to understand it
Sleep 20s

Ctrl+C
Sleep 4s


# ==================================================
# Hidden cleanup
# ==================================================

Hide

Type "rm -rf /tmp/termradar-vhs-config /tmp/termradar-demo-venv"
Enter
Sleep 2s