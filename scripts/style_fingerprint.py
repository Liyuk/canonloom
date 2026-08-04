#!/usr/bin/env python3
"""Compute portable style metrics without persisting story content."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["style"]:
        args = args[1:]
    raise SystemExit(main(["style", *args]))
