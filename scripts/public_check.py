#!/usr/bin/env python3
"""Small dependency-free pre-publication scan for common accidental secrets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}
TEXT_SUFFIXES = {".md", ".json", ".py", ".sh", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai-style-key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("google-style-key", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("slack-token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{20,}")),
    ("absolute-user-path", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/")),
]


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.startswith(".env") and path.name != ".env.example":
            yield path, "env-file"
        elif path.suffix.lower() in TEXT_SUFFIXES:
            yield path, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a repository before public release")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    findings = []
    for path, special in iter_files(root):
        if special:
            findings.append((path, special, "private environment file"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append((path, name, f"line {text[:match.start()].count(chr(10)) + 1}"))
    if findings:
        print("PUBLIC CHECK: FINDINGS")
        for path, kind, detail in findings:
            print(f"- {path.relative_to(root)}: {kind} ({detail})")
        return 1
    print("PUBLIC CHECK: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
