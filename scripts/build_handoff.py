#!/usr/bin/env python3
"""Portable handoff entry point; equivalent to `canonloom handoff`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from canonloom_tools import main


if __name__ == "__main__":
    raise SystemExit(main(["handoff", *sys.argv[1:]]))
