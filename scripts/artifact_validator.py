#!/usr/bin/env python3
"""Dependency-free protocol checks for CanonLoom JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SEVERITIES = {"BLOCKER", "MAJOR", "MINOR", "ADVISORY"}
STAGES = {"S0", "S1", "S2", "S3", "S4", "S5", "S5b", "S6"}


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"errors": [f"invalid JSON: {exc}"]}
    return value if isinstance(value, dict) else {"errors": ["root must be an object"]}


def check_artifact(kind: str, path: Path) -> list[str]:
    data = load(path)
    errors = list(data.pop("errors", []))
    if kind == "context":
        required = {"schema_version", "context_id", "work_id", "included_files", "selection_reason", "compiled_at", "included_sources", "provenance"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.2": errors.append("schema_version must be 0.2")
        if not isinstance(data.get("included_files"), list): errors.append("included_files must be an array")
        if not isinstance(data.get("provenance"), list): errors.append("provenance must be an array")
    elif kind == "handoff":
        required = {"schema_version", "generated_at", "work_id", "source_stage", "status", "current_files", "next_action", "approval"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.2": errors.append("schema_version must be 0.2")
        if data.get("source_stage") not in STAGES: errors.append("invalid source_stage")
        if data.get("status") not in {"READY", "BLOCKED", "NEEDS_REVIEW", "FAILED"}: errors.append("invalid status")
        if data.get("approval") not in {"NONE", "AUTHOR_PENDING", "AUTHOR_APPROVED", "AUTHOR_REJECTED"}: errors.append("invalid approval")
    elif kind == "finding-report":
        findings = data.get("findings")
        if not isinstance(findings, list):
            errors.append("findings must be an array")
        else:
            required = {"id", "severity", "category", "location", "evidence", "issue", "fix", "status"}
            for index, finding in enumerate(findings):
                if not isinstance(finding, dict):
                    errors.append(f"finding[{index}] must be an object")
                    continue
                errors += [f"finding[{index}] missing field: {key}" for key in sorted(required - finding.keys())]
                if finding.get("severity") not in SEVERITIES: errors.append(f"finding[{index}] invalid severity")
    elif kind == "stage-log":
        required = {"workflow_id", "work_id", "run_id", "stage_id", "status", "actual_changes", "preserved_risks", "open_loops", "next_stage"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("stage_id") not in STAGES: errors.append("invalid stage_id")
    elif kind == "project-config":
        required = {"schema_version", "project_id", "phase", "mode", "next_action", "updated_at"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.2": errors.append("schema_version must be 0.2")
    elif kind == "style-profile":
        required = {"schema_version", "profile_id", "name", "narrative", "rhythm", "dialogue", "surface", "review_questions"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.1": errors.append("schema_version must be 0.1")
        if not isinstance(data.get("review_questions"), list): errors.append("review_questions must be an array")
    elif kind == "author-setup":
        required = {"schema_version", "project_title", "author_confirmed"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.1": errors.append("schema_version must be 0.1")
        if not isinstance(data.get("author_confirmed"), bool): errors.append("author_confirmed must be boolean")
    elif kind == "ai-recognition":
        required = {"schema_version", "status", "source_refs", "extracted", "unresolved_questions"}
        errors += [f"missing field: {key}" for key in sorted(required - data.keys())]
        if data.get("schema_version") != "0.1": errors.append("schema_version must be 0.1")
        if data.get("status") not in {"PENDING", "PROPOSED", "AUTHOR_CONFIRMED", "REJECTED"}: errors.append("invalid status")
    else:
        errors.append(f"unknown artifact type: {kind}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["context", "handoff", "finding-report", "stage-log", "project-config", "style-profile", "author-setup", "ai-recognition"])
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    errors = check_artifact(args.kind, args.path)
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
