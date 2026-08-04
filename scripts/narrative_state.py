#!/usr/bin/env python3
"""Optional narrative-state checks for events, knowledge, and reveals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EVENT_REQUIRED = {"event_id", "chapter_id", "subject", "action", "object", "status"}
KNOWLEDGE_REQUIRED = {"knowledge_id", "holder", "proposition", "status"}
EVENT_STATUSES = {"PROPOSED", "CONFIRMED", "REJECTED"}
REVEAL_STATUSES = {"OPEN", "PARTIAL", "PAID_OFF", "ABANDONED"}


def load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records, errors = [], []
    if not path.exists():
        return records, [f"missing: {path}"]
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name}:{line_no}: record must be an object")
            continue
        records.append(value)
    return records, errors


def load_reveals(path: Path) -> tuple[list[dict], list[str]]:
    if not path.exists():
        return [], [f"missing: {path}"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"{path.name}: invalid JSON: {exc}"]
    if isinstance(value, list):
        return value, []
    if isinstance(value, dict) and isinstance(value.get("reveals"), list):
        return value["reveals"], []
    return [], [f"{path.name}: expected an array or an object with reveals[]"]


def validate_records(records: list[dict], required: set[str], statuses: set[str], id_key: str, label: str) -> list[str]:
    errors = []
    seen = set()
    for index, record in enumerate(records, 1):
        missing = required - record.keys()
        errors.extend(f"{label}[{index}] missing field: {key}" for key in sorted(missing))
        record_id = record.get(id_key)
        if record_id in seen:
            errors.append(f"{label}[{index}] duplicate {id_key}: {record_id}")
        if record_id:
            seen.add(record_id)
        if record.get("status") not in statuses:
            errors.append(f"{label}[{index}] invalid status: {record.get('status')}")
    return errors


def collect(root: Path) -> dict:
    state = root / "memory/narrative-state"
    events, errors = load_jsonl(state / "events.jsonl")
    knowledge, knowledge_errors = load_jsonl(state / "knowledge.jsonl")
    reveals, reveal_errors = load_reveals(state / "reveals.json")
    errors += knowledge_errors + reveal_errors
    errors += validate_records(events, EVENT_REQUIRED, EVENT_STATUSES, "event_id", "events")
    errors += validate_records(knowledge, KNOWLEDGE_REQUIRED, EVENT_STATUSES, "knowledge_id", "knowledge")
    errors += validate_records(reveals, {"setup_id", "status", "reader_knows", "protagonist_knows"}, REVEAL_STATUSES, "setup_id", "reveals")
    for record in events + knowledge:
        if record.get("status") in {"CONFIRMED"} and not record.get("source_ref"):
            errors.append(f"{record.get('event_id') or record.get('knowledge_id')}: confirmed record requires source_ref")
    return {
        "tool": "narrative_state",
        "root": str(root),
        "status": "OK" if not errors else "NEEDS_REPAIR",
        "counts": {"events": len(events), "knowledge": len(knowledge), "reveals": len(reveals)},
        "open_reveals": [item.get("setup_id") for item in reveals if item.get("status") in {"OPEN", "PARTIAL"}],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["validate", "report"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    result = collect(Path(args.root).expanduser().resolve())
    if args.action == "report":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"NARRATIVE STATE: {result['status']}")
        print(json.dumps({"counts": result["counts"], "errors": result["errors"]}, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
