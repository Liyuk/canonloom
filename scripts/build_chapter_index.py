#!/usr/bin/env python3
"""Build a portable Markdown chapter index."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["index", *__import__("sys").argv[1:]]))
