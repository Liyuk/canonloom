#!/usr/bin/env python3
"""Query the portable CanonLoom chapter index."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["query", *__import__("sys").argv[1:]]))
