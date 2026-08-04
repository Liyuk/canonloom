#!/usr/bin/env python3
"""Measure CanonLoom's deterministic local-tool overhead.

This intentionally does not call a model. It measures the Python side of the
workflow so model token and latency estimates remain separate and honest.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure CanonLoom deterministic tool overhead")
    parser.add_argument("--root", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    tool = Path(__file__).with_name("canonloom_tools.py")
    commands = [
        ("beats", [sys.executable, str(tool), "beats", args.contract, "--root", str(root)]),
        ("validate_quick", [sys.executable, str(tool), "validate", args.chapter, "--contract", args.contract, "--root", str(root), "--level", "quick"]),
        ("validate_strict", [sys.executable, str(tool), "validate", args.chapter, "--contract", args.contract, "--root", str(root), "--level", "strict"]),
        ("index", [sys.executable, str(tool), "index", "--root", str(root)]),
        ("style", [sys.executable, str(tool), "style", str(root / args.chapter)]),
        ("stats", [sys.executable, str(tool), "stats", "--root", str(root)]),
    ]
    results = []
    for name, command in commands:
        started = time.perf_counter()
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        results.append({"name": name, "returncode": completed.returncode, "latency_ms": elapsed, "stdout_bytes": len(completed.stdout.encode()), "stderr": completed.stderr[-500:]})
    report = {"schema_version": "0.1", "tool": "benchmark_overhead", "generated_at": now(), "root": str(root), "model_calls": 0, "token_measurement": "not applicable: local deterministic tools only", "total_latency_ms": round(sum(item["latency_ms"] for item in results), 2), "commands": results}
    output = Path(args.output).expanduser() if args.output else root / "reviews" / "benchmark-overhead.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(item["returncode"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
