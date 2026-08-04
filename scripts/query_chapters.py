#!/usr/bin/env python3
"""Query the portable CanonLoom chapter index."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["query"]:
        args = args[1:]
    raise SystemExit(main(["query", *args]))
