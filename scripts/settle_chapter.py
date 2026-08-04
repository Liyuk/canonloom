#!/usr/bin/env python3
"""Perform the mechanical part of S6 after explicit author approval."""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote an explicitly approved draft to manuscript")
    parser.add_argument("--root", default=".")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--source", default=None)
    parser.add_argument("--target", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    source = root / (args.source or f"drafts/{args.work_id}.revised.md")
    target = root / (args.target or f"manuscript/{args.work_id}.md")
    approval_path = root / f"tasks/{args.work_id}.approval.json"
    trace_path = root / f"traces/{args.work_id}.settlement.json"
    try:
        source = source.resolve()
        target = target.resolve()
        source.relative_to(root)
        target.relative_to(root)
    except ValueError as exc:
        raise SystemExit("source/target must remain inside the project root") from exc
    config_path = root / "canonloom.json"
    if not config_path.exists():
        raise SystemExit("canonloom.json missing")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("work_id") != args.work_id or config.get("stage_id") != "S6":
        raise SystemExit("settlement requires the current work_id to have passed gate S6")
    if not source.exists():
        raise SystemExit(f"source draft missing: {source}")
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    source_ref = str(source.relative_to(root))
    if approval.get("work_id") not in {None, args.work_id} or approval.get("approved_artifact") not in {None, source_ref} or approval.get("approval") != "AUTHOR_APPROVED" or approval.get("action") != "approve_settlement":
        raise SystemExit("explicit AUTHOR_APPROVED/approve_settlement is required")
    if not trace_path.exists():
        raise SystemExit(f"settlement trace missing: {trace_path}")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    if trace.get("work_id") not in {None, args.work_id} or trace.get("source_draft") not in {None, source_ref}:
        raise SystemExit("settlement trace does not match the approved work or source draft")
    if target.exists():
        if target.read_bytes() == source.read_bytes():
            print(json.dumps({"tool": "settle_chapter", "work_id": args.work_id, "status": "ALREADY_SETTLED", "target": str(target.relative_to(root))}, ensure_ascii=False, indent=2))
            return 0
        raise SystemExit(f"target already exists with different content: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from canonloom_tools import build_index
        build_index(root, root / "index/chapter-index.json")
        index_status = "UPDATED"
    except Exception as exc:
        index_status = f"FAILED: {exc}"
    state_report = None
    state_mode = config.get("narrative_state", {}).get("mode", "optional")
    if state_mode != "disabled":
        try:
            from narrative_state import collect
            state_report = collect(root)
            if state_mode == "required" and state_report.get("status") != "OK":
                raise SystemExit("required narrative state is invalid; settlement aborted")
        except ImportError:
            if state_mode == "required":
                raise SystemExit("required narrative state tool is unavailable")
    report = {"tool": "settle_chapter", "work_id": args.work_id, "settled_at": now(), "source": str(source.relative_to(root)), "target": str(target.relative_to(root)), "approval": str(approval_path.relative_to(root)), "canon_promotion": "NONE", "index_status": index_status, "narrative_state_status": state_report.get("status") if state_report else "DISABLED", "state_promotion": "AUTHOR_APPROVAL_REQUIRED" if state_report else "NONE"}
    log = root / "logs/repairs" / f"settlement-{args.work_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
