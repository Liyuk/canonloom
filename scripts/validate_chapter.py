#!/usr/bin/env python3
"""Compatibility entry point for the generic CanonLoom chapter validator."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["validate"]:
        args = args[1:]
    raise SystemExit(main(["validate", *args]))
