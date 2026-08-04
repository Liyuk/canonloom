#!/usr/bin/env python3
"""Compatibility entry point for CanonLoom Beat/contract validation."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["beats", *__import__("sys").argv[1:]]))
