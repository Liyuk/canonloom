#!/usr/bin/env python3
"""Compatibility entry point for the generic CanonLoom chapter validator."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["validate", *__import__("sys").argv[1:]]))
