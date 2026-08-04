#!/usr/bin/env python3
"""Cross-validate two independent JSON review reports."""
from canonloom_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["cross-validate", *__import__("sys").argv[1:]]))
