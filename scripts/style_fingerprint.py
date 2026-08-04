#!/usr/bin/env python3
"""Compute portable style metrics without persisting story content."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["style", *__import__("sys").argv[1:]]))
