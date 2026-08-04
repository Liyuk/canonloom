#!/usr/bin/env python3
"""Small, dependency-free checks for CanonLoom workflow artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from canonloom import STAGE_REQUIREMENTS, STAGE_NEXT
except ImportError:  # pragma: no cover - direct embedding fallback
    STAGE_REQUIREMENTS = {stage: () for stage in ("S0", "S1", "S2", "S3", "S4", "S5", "S5b", "S6")}
    STAGE_NEXT = {"S0": "S1", "S1": "S2", "S2": "S3", "S3": "S4", "S4": "S5", "S5": "S5b", "S5b": "S6", "S6": "STOP"}

STAGES = set(STAGE_REQUIREMENTS)
NEXT = STAGES | {"HUMAN_DECISION", "STOP"}
STATUSES = {"COMPLETED", "BLOCKED", "NEEDS_REVIEW", "FAILED", "NOT_RUN"}
ALLOWED_TRANSITIONS = {
    "S0": {"S1", "HUMAN_DECISION", "STOP"},
    "S1": {"S2", "STOP"},
    "S2": {"S3", "S4", "STOP"},
    "S3": {"S4", "S3", "HUMAN_DECISION", "STOP"},
    "S4": {"S5", "S3", "HUMAN_DECISION", "STOP"},
    "S5": {"S5b", "S3", "HUMAN_DECISION", "STOP"},
    "S5b": {"S6", "S3", "HUMAN_DECISION", "STOP"},
    "S6": {"S6", "STOP"},
}
REQUIRED_LOG_FIELDS = {
    "workflow_id", "work_id", "run_id", "stage_id", "status",
    "actual_changes", "preserved_risks", "open_loops", "next_stage",
}


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def check_log(path: Path) -> list[str]:
    data = load(path)
    errors = []
    missing = REQUIRED_LOG_FIELDS - data.keys()
    if missing:
        errors.append(f"missing stage-log fields: {', '.join(sorted(missing))}")
    if data.get("stage_id") not in STAGES:
        errors.append(f"invalid stage_id: {data.get('stage_id')}")
    if data.get("status") not in STATUSES:
        errors.append(f"invalid status: {data.get('status')}")
    if data.get("next_stage") not in NEXT:
        errors.append(f"invalid next_stage: {data.get('next_stage')}")
    for key in ("actual_changes", "preserved_risks", "open_loops"):
        if not isinstance(data.get(key), str) or not data.get(key).strip():
            errors.append(f"{key} must be a non-empty string")
    return errors


def check_transition(source: str, target: str) -> list[str]:
    if source not in STAGES:
        return [f"invalid source stage: {source}"]
    if target not in NEXT:
        return [f"invalid target stage: {target}"]
    if target not in ALLOWED_TRANSITIONS[source]:
        return [f"transition not allowed: {source} -> {target}"]
    return []


def check_boundary(stage: str, paths: list[str]) -> list[str]:
    rules = {
        "S0": ("plan/", "workspace/", "reviews/", "traces/"),
        "S1": ("drafts/", "traces/"),
        "S2": ("reviews/", "traces/"),
        "S3": ("drafts/", "reviews/", "traces/"),
        "S4": ("reviews/", "traces/"),
        "S5": ("reviews/", "traces/"),
        "S5b": ("reviews/", "traces/"),
        "S6": ("manuscript/", "memory/", "reviews/", "traces/", "index/", "handoffs/"),
    }
    if stage not in rules:
        return [f"invalid stage: {stage}"]
    errors = []
    for raw in paths:
        normalized = raw.lstrip("./")
        if not any(normalized.startswith(prefix) for prefix in rules[stage]):
            errors.append(f"{stage} cannot write: {raw}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    log = sub.add_parser("stage-log")
    log.add_argument("path", type=Path)

    transition = sub.add_parser("transition")
    transition.add_argument("source")
    transition.add_argument("target")

    boundary = sub.add_parser("boundary")
    boundary.add_argument("stage")
    boundary.add_argument("paths", nargs="+")

    args = parser.parse_args()
    if args.command == "stage-log":
        errors = check_log(args.path)
    elif args.command == "transition":
        errors = check_transition(args.source, args.target)
    else:
        errors = check_boundary(args.stage, args.paths)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
