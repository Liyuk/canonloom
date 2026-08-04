#!/usr/bin/env python3
"""Compute generic chapter/draft/manuscript statistics."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["stats", *__import__("sys").argv[1:]]))
