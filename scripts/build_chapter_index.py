#!/usr/bin/env python3
"""Build a portable Markdown chapter index."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["index"]:
        args = args[1:]
    raise SystemExit(main(["index", *args]))
