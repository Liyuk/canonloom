#!/usr/bin/env python3
"""Compile a bounded context package from a chapter contract."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["context"]:
        args = args[1:]
    raise SystemExit(main(["context", *args]))
