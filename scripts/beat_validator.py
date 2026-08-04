#!/usr/bin/env python3
"""Compatibility entry point for CanonLoom Beat/contract validation."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["beats"]:
        args = args[1:]
    raise SystemExit(main(["beats", *args]))
