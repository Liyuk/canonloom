#!/usr/bin/env python3
"""Compute generic chapter/draft/manuscript statistics."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["stats"]:
        args = args[1:]
    raise SystemExit(main(["stats", *args]))
