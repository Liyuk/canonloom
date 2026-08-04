#!/usr/bin/env python3
"""Compile a bounded context package from a chapter contract."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["context", *__import__("sys").argv[1:]]))
