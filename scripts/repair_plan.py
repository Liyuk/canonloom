#!/usr/bin/env python3
"""Turn validator findings into an explicit, non-destructive repair plan."""
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an auditable repair plan from a review JSON")
    parser.add_argument("report")
    parser.add_argument("--output")
    args = parser.parse_args()
    data = json.loads(Path(args.report).read_text(encoding="utf-8"))
    findings = data.get("findings", data.get("issues", []))
    plan = {"tool": "repair_plan", "source": args.report, "policy": "Do not edit canon or promote state; author approval remains required.", "steps": [{"order": i, "finding_id": item.get("id", f"finding-{i}"), "severity": item.get("severity", "ADVISORY"), "instruction": item.get("fix", "Review this finding manually"), "status": "pending"} for i, item in enumerate(findings, 1)]}
    text = json.dumps(plan, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
