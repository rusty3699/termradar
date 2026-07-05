"""Allow running as ``python -m termradar``."""

from termradar.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
