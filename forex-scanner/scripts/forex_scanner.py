#!/usr/bin/env python
"""
Command-line helper that wraps the shared forex scanner utilities.
"""

from __future__ import annotations

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from python.forex_scanner import main as forex_main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(forex_main())

