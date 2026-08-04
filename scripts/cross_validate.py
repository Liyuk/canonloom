#!/usr/bin/env python3
"""Cross-validate two independent JSON review reports."""
import sys
from canonloom_tools import main

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["cross-validate"]:
        args = args[1:]
    raise SystemExit(main(["cross-validate", *args]))
