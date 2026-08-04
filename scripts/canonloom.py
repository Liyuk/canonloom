#!/usr/bin/env python3
"""CanonLoom's small, command-driven author interface.

This CLI manages files and workflow state. It does not call an LLM or provide a GUI.
An agent reads the task artifact created by these commands and performs the creative work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path


CONFIG = "canonloom.json"
SCHEMA_VERSION = "0.2"
REPOSITORY_VERSION = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip() if (Path(__file__).resolve().parents[1] / "VERSION").exists() else "0.0.0-dev"

AUTHOR_COMMANDS = ("init", "status", "setup", "idea", "reference", "import", "planning", "work", "characters", "world", "research", "revision", "review", "continue", "route", "diagnose", "state", "repair", "upgrade")
ADVANCED_COMMANDS = ("retry", "validate", "beats", "index", "query", "context", "cross-validate", "style", "stats", "repair-plan", "normalize-findings", "handoff", "artifact-check", "record", "settle", "gate", "benchmark")

DIRS = [
    "intent", "canon/entities", "canon/rules", "canon/timeline", "canon/sources",
    "plan/volumes", "plan/arcs", "plan/chapter-contracts",
    "workspace/options", "workspace/selections", "workspace/context-packages",
    "drafts", "reviews", "manuscript", "memory/active", "memory/draft",
    "memory/archive", "memory/narrative-state", "issues", "index", "logs/workflows", "logs/repairs", "runs", "handoffs", "traces", "tasks",
]

TASK_TEXT = {
    "setup": "完成项目初始化：先读取 intent/author-setup.json，由作者确认题材、受众、视角、文风方向、内容边界和篇章目标；再读取 intent/ai-recognition.json，把已有材料中的人物、世界、线索和可迁移技法写成候选提案。AI 只能写候选区，不能直接晋升 canon；作者确认后再进入 idea/planning。",
    "idea": "开始创意：请读取当前任务文件，帮助作者明确创作意图，并生成 2–5 个候选方向。不要写入 canon。",
    "reference": "开始拆书：请分析指定参考材料的结构、节奏、人物机制和读者效果，只输出可迁移的抽象技法，不复制原文。",
    "import": "开始导入：请盘点已有稿件，提取带来源的事实候选、时间线、人物和开放循环，等待作者确认后再晋升。",
    "planning": "开始规划：请从项目意图和当前状态开始，按项目→卷→篇章→章契→Beat逐层规划，不要跳过上层决策。",
    "work": "开始工作：请读取当前状态和任务，判断下一阶段，只处理一个明确工作单元并写入阶段产物。",
    "characters": "开始人物校准：请读取人物目标、关系、当前卷次和上一阶段状态，检查动机与选择是否一致，只提出候选调整，等待作者确认。",
    "world": "开始世界推演：请读取世界规则、当前状态和事件边界，生成可审计的分支与状态快照，不直接写入 canon。",
    "research": "开始资料核验：请记录来源、事实、适用边界和不确定性，只生成研究卡，不把外部资料直接当作故事事实。",
    "revision": "开始修订：请读取当前草稿和问题清单，按影响优先级修复，并保留变更说明，不新增未经批准的 canon。",
    "review": "开始审查：请按指定层级生成带证据的 findings；审查者不能直接批准稿件或修改 canon。",
    "benchmark": "开始对标拆解：请只分析合法参考材料的可迁移结构、节奏和读者机制，并记录相似性风险，不复制原文。",
    "continue": "继续工作：请读取 canonloom.json、tasks/current.md 和最新阶段日志，执行 NEXT_ACTION 指定的下一步；遇到阻断就停止并报告。",
}

TASK_TEXT_EN = {
    "setup": "Complete project initialization: read intent/author-setup.json for author-confirmed genre, audience, viewpoint, tone, boundaries, and chapter goals; then read intent/ai-recognition.json and record candidate characters, world elements, clues, and transferable techniques from the available material. AI may write proposals only and must not promote them to canon; wait for author confirmation before idea/planning.",
    "idea": "Start ideation: read the current task and help the author clarify intent, then produce 2–5 candidate directions. Do not write to canon.",
    "reference": "Start reference analysis: analyze structure, pacing, character mechanisms, and reader effects from the provided material. Output only transferable abstract techniques and do not copy text.",
    "import": "Start import inventory: inspect existing manuscripts and extract source-linked candidate facts, timelines, characters, and open loops. Wait for author confirmation before promotion.",
    "planning": "Start planning: move through project → volume → arc → chapter contract → beats. Do not skip an upper-level decision.",
    "work": "Start work: read the current state and task, determine the next stage, process one explicit work unit, and write its stage artifacts.",
    "characters": "Start character calibration: read character goals, relationships, current arc, and previous stage state. Check motivation and choice consistency, propose changes, and wait for author confirmation.",
    "world": "Start world simulation: read rules, current state, and event boundaries. Generate auditable branches and state snapshots; do not write directly to canon.",
    "research": "Start research verification: record sources, facts, scope, and uncertainty. Create research cards and do not treat external material as story fact.",
    "revision": "Start revision: read the draft and findings, repair in impact order, and preserve a change note. Do not add unapproved canon.",
    "review": "Start review: produce evidence-backed findings at the requested level. The reviewer cannot approve the draft or modify canon.",
    "benchmark": "Start comparative analysis: extract transferable structure, pacing, and reader mechanisms from lawful reference material and record similarity risks. Do not copy text.",
    "continue": "Continue work: read canonloom.json, tasks/current.md, and the latest stage log. Execute the next_action specified by the project; stop and report if blocked.",
}

STAGE_REQUIREMENTS = {
    "S0": ("plan/chapter-contracts/{work_id}.json", "workspace/selections/{work_id}.json", "workspace/context-packages/{work_id}.json"),
    "S1": ("drafts/{work_id}.md",),
    "S2": ("reviews/{work_id}.quick.json",),
    "S3": ("drafts/{work_id}.revised.md", "reviews/{work_id}.repair.json"),
    "S4": ("reviews/{work_id}.strict.json",),
    "S5": ("reviews/{work_id}.independent.json",),
    "S5b": ("reviews/{work_id}.cross-validation.json",),
    # S6 creates the settlement trace after validating author approval. Requiring
    # the trace here would make the gate and settle_chapter mutually dependent.
    "S6": ("tasks/{work_id}.approval.json",),
}

STAGE_NEXT = {"S0": "S1", "S1": "S2", "S2": "S3", "S3": "S4", "S4": "S5", "S5": "S5b", "S5b": "S6", "S6": "STOP"}
STAGE_PREVIOUS = {"S0": None, "S1": "S0", "S2": "S1", "S3": "S2", "S4": "S3", "S5": "S4", "S5b": "S5", "S6": "S5b"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value.strip().lower()).strip("-")
    return value or "canonloom-project"


def config_path(root: Path) -> Path:
    return root / CONFIG


def default_sections() -> dict:
    return {
        "workflow": {
            "stage_order": list(STAGE_REQUIREMENTS),
            "require_author_approval_for_settlement": True,
            "allow_canon_write_before_s6": False,
            "max_retry_per_stage": 2,
            "retry_requires_new_run": True,
            "review_strategy": "single_model_python",
            "require_review_provenance": True,
            "require_independent_review_run": True,
        },
        "quality": {
            "chapter_length": {"min_cjk": 10000, "max_cjk": 14000},
            "dialogue_ratio": {"min": 0.08, "max": 0.16},
            "severity_policy": {"BLOCKER": "stop", "MAJOR": "repair_before_next_stage", "MINOR": "review", "ADVISORY": "inform"},
        },
        "context": {"include_handoff": True, "include_previous_chapter": True, "include_research": True, "include_narrative_state": True, "require_provenance": True, "exclude_unapproved_memory": True},
        "style_profile": {"ref": "intent/style-profile.json", "deterministic_checks": True, "human_review_required": True},
        "setup": {"status": "AUTHOR_INPUT_REQUIRED", "author_config_ref": "intent/author-setup.json", "ai_recognition_ref": "intent/ai-recognition.json", "author_fields": ["project_title", "genre", "audience", "pov", "tone", "content_boundaries"], "ai_write_targets": ["intent/ai-recognition.json", "memory/draft/", "workspace/options/"]},
        "language_policy": {"protocol": "en", "agent_instructions": "bilingual", "project_content": "author_setup", "human_review": "project_content"},
        "narrative_state": {"mode": "optional", "events_ref": "memory/narrative-state/events.jsonl", "knowledge_ref": "memory/narrative-state/knowledge.jsonl", "reveals_ref": "memory/narrative-state/reveals.json", "policy_ref": "memory/narrative-state/state-policy.json"},
        "runtime": {"primary": "codex", "reviewer": "same_model", "strategy": "single_model_python", "record_model_metadata": True},
        "budget": {"record_input_tokens": True, "record_output_tokens": True, "record_latency": True, "record_retries": True},
    }


def merge_defaults(data: dict) -> dict:
    for key, value in default_sections().items():
        if key not in data:
            data[key] = value
        elif isinstance(value, dict):
            for child, child_value in value.items():
                if child not in data[key]:
                    data[key][child] = child_value
    data["schema_version"] = SCHEMA_VERSION
    return data


def run_manifest_path(root: Path, data: dict) -> Path | None:
    path = data.get("run_path")
    return root / path / "manifest.json" if path else None


def update_run(root: Path, event: dict) -> None:
    data = read_config(root)
    path = run_manifest_path(root, data)
    if not path or not path.exists():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.setdefault("events", []).append({"at": now(), **event})
    metrics = manifest.setdefault("metrics", {})
    for key in ("input_tokens", "output_tokens", "latency_ms", "retries", "tool_calls"):
        metrics[key] = metrics.get(key, 0) + int(event.get(key, 0) or 0)
    if event.get("run_status") in {"COMPLETED", "FAILED"}:
        manifest["status"] = event["run_status"]
    write_json(path, manifest)


def start_run(root: Path, work_id: str, stage: str, reason: str = "", kind: str = "work") -> tuple[str, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"{stamp}-{slug(work_id)}"
    data = read_config(root)
    run_dir = root / "runs" / slug(work_id) / run_id
    manifest = {"schema_version": "0.1", "run_id": run_id, "work_id": work_id, "started_at": now(), "status": "RUNNING", "kind": kind, "start_stage": stage, "reason": reason, "mode": data.get("mode"), "strategy": data.get("runtime", {}).get("strategy", "single_model_python"), "metrics": {"input_tokens": 0, "output_tokens": 0, "latency_ms": 0, "retries": 0, "tool_calls": 0}, "events": []}
    write_json(run_dir / "manifest.json", manifest)
    data["run_id"] = run_id
    data["run_path"] = str(run_dir.relative_to(root))
    write_json(config_path(root), data)
    return run_id, run_dir


def read_config(root: Path) -> dict:
    path = config_path(root)
    if not path.exists():
        raise SystemExit(f"未找到 {CONFIG}。先运行：canonloom init")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{CONFIG} 不是有效 JSON：{exc}") from exc
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def task_text_for(root: Path, command: str) -> str:
    setup_path = root / "intent/author-setup.json"
    if setup_path.exists():
        try:
            language = json.loads(setup_path.read_text(encoding="utf-8")).get("language", "zh-CN")
            if str(language).lower().startswith("en"):
                return TASK_TEXT_EN.get(command, TASK_TEXT[command])
        except (OSError, json.JSONDecodeError):
            pass
    return TASK_TEXT[command]


def write_task(root: Path, command: str, extra: str = "") -> None:
    language = "en" if task_text_for(root, command) == TASK_TEXT_EN.get(command) else "zh-CN"
    text = f"# CanonLoom Task\n\nCOMMAND: {command}\nLANGUAGE: {language}\nCREATED_AT: {now()}\n\n## Agent instruction\n\n{task_text_for(root, command)}\n"
    if extra:
        text += f"\n## User input\n\n{extra}\n"
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / "tasks/current.md").write_text(text, encoding="utf-8")


def required_dirs_missing(root: Path) -> list[str]:
    return [directory for directory in DIRS if not (root / directory).is_dir()]


def collect_diagnosis(root: Path) -> dict:
    issues = []
    config = root / CONFIG
    if not config.exists():
        issues.append({"id": "CONFIG_MISSING", "severity": "BLOCKER", "repairable": False, "message": f"未找到 {CONFIG}"})
        return {"status": "BLOCKED", "issues": issues}
    try:
        data = read_config(root)
    except SystemExit as exc:
        issues.append({"id": "CONFIG_INVALID", "severity": "BLOCKER", "repairable": False, "message": str(exc)})
        return {"status": "BLOCKED", "issues": issues}
    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append({"id": "CONFIG_SCHEMA", "severity": "MAJOR", "repairable": data.get("schema_version") == "0.1", "message": f"schema_version 应为 {SCHEMA_VERSION}"})
    for directory in required_dirs_missing(root):
        issues.append({"id": "DIR_MISSING", "severity": "MAJOR", "repairable": True, "path": directory, "message": f"缺少目录：{directory}"})
    if not (root / "tasks/current.md").is_file():
        issues.append({"id": "TASK_MISSING", "severity": "MINOR", "repairable": True, "path": "tasks/current.md", "message": "缺少当前任务文件"})
    for field in ("project_id", "phase", "mode", "work_id", "stage_id", "next_action", "updated_at"):
        if field not in data:
            issues.append({"id": "CONFIG_FIELD_MISSING", "severity": "MAJOR", "repairable": True, "field": field, "message": f"配置缺少字段：{field}"})
    return {"status": "OK" if not issues else "NEEDS_REPAIR", "issues": issues}


def write_repair_log(root: Path, report: dict) -> Path:
    path = root / "logs" / "repairs" / f"repair-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    write_json(path, report)
    return path


def write_stage_trace(root: Path, data: dict, work_id: str, stage: str) -> None:
    trace = {"workflow_id": data.get("project_id", "canonloom"), "work_id": work_id, "run_id": data.get("run_id", "NONE"), "stage_id": stage, "status": "COMPLETED", "actual_changes": f"gate {stage} passed", "preserved_risks": "NONE", "open_loops": "UNCHANGED", "next_stage": STAGE_NEXT[stage]}
    write_json(root / f"traces/{work_id}.{stage}.json", trace)


def set_phase(root: Path, phase: str, command: str, work_id: str | None = None) -> dict:
    data = read_config(root)
    if work_id is not None and work_id != data.get("work_id"):
        data["stage_id"] = None
    data["phase"] = phase
    data["work_id"] = work_id if work_id is not None else data.get("work_id")
    data["next_action"] = command
    data["updated_at"] = now()
    write_json(config_path(root), data)
    return data


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    existing = config_path(root).exists()
    for directory in DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)
    if not existing:
        data = {
            "schema_version": SCHEMA_VERSION,
            "project_id": slug(args.name or root.name),
            "phase": "uninitialized",
            "mode": args.mode,
            "work_id": None,
            "stage_id": None,
            "next_action": "setup",
            "updated_at": now(),
        }
        data = merge_defaults(data)
        write_json(config_path(root), data)
    elif json.loads(config_path(root).read_text(encoding="utf-8")).get("schema_version") != SCHEMA_VERSION:
        write_json(config_path(root), merge_defaults(json.loads(config_path(root).read_text(encoding="utf-8"))))
    else:
        existing_data = json.loads(config_path(root).read_text(encoding="utf-8"))
        if "setup" not in existing_data:
            write_json(config_path(root), merge_defaults(existing_data))
    (root / "intent/author-intent.md").touch(exist_ok=True)
    (root / "intent/review-policy.md").touch(exist_ok=True)
    style_path = root / "intent/style-profile.json"
    if not style_path.exists():
        template = Path(__file__).resolve().parents[1] / "templates/style-profile.json"
        write_json(style_path, json.loads(template.read_text(encoding="utf-8")))
    for name in ("author-setup.json", "ai-recognition.json"):
        target = root / "intent" / name
        if not target.exists():
            template = Path(__file__).resolve().parents[1] / "templates" / name
            write_json(target, json.loads(template.read_text(encoding="utf-8")))
    state_policy = root / "memory/narrative-state/state-policy.json"
    if not state_policy.exists():
        template = Path(__file__).resolve().parents[1] / "templates/narrative-state-policy.json"
        write_json(state_policy, json.loads(template.read_text(encoding="utf-8")))
    for name in ("events.jsonl", "knowledge.jsonl", "reveals.json"):
        target = root / "memory/narrative-state" / name
        if not target.exists():
            target.write_text("{\"reveals\": []}\n" if name == "reveals.json" else "", encoding="utf-8")
    author_setup = root / "intent/author-setup.json"
    setup_data = json.loads(author_setup.read_text(encoding="utf-8"))
    if any(getattr(args, key, None) for key in ("genre", "audience", "pov", "tone", "language", "chapter_min", "chapter_max")) or args.name or not setup_data.get("project_title"):
        setup_data["project_title"] = args.name or setup_data.get("project_title", "") or root.name
        for key in ("genre", "audience", "pov", "language"):
            value = getattr(args, key, None)
            if value:
                setup_data[key] = value
        if args.tone:
            setup_data["tone"] = [item.strip() for item in args.tone.split(",") if item.strip()]
        if args.chapter_min is not None:
            setup_data["chapter_length"]["min_cjk"] = args.chapter_min
        if args.chapter_max is not None:
            setup_data["chapter_length"]["max_cjk"] = args.chapter_max
        write_json(author_setup, setup_data)
    if not (root / "tasks/current.md").exists():
        write_task(root, "setup")
    print(f"CanonLoom 项目已准备：{root}")
    print("下一步：canonloom setup")
    return 0


def require_root(args: argparse.Namespace) -> Path:
    return Path(args.root).expanduser().resolve()


def cmd_status(args: argparse.Namespace) -> int:
    root = require_root(args)
    data = read_config(root)
    print(f"PROJECT: {data.get('project_id')}")
    print(f"PHASE: {data.get('phase')}")
    print(f"MODE: {data.get('mode')}")
    print(f"WORK_ID: {data.get('work_id') or 'NONE'}")
    print(f"STAGE_ID: {data.get('stage_id') or 'NONE'}")
    print(f"NEXT_ACTION: {data.get('next_action')}")
    task = root / "tasks/current.md"
    print(f"TASK_FILE: {'present' if task.exists() else 'missing'}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    root = require_root(args)
    commands = {
        "setup": ("uninitialized", "setup"),
        "idea": ("idea", "idea"),
        "reference": ("analysis", "reference"),
        "import": ("import", "import"),
        "planning": ("planning", "planning"),
        "work": ("production", "work"),
        "characters": ("planning", "characters"),
        "world": ("simulation", "world"),
        "research": ("research", "research"),
        "revision": ("revision", "revision"),
        "review": ("review", "review"),
        "benchmark": ("analysis", "benchmark"),
    }
    phase, command = commands[args.kind]
    work_id = slug(args.work_id) if args.work_id else None
    if command == "setup" and getattr(args, "confirm", False):
        setup_path = root / "intent/author-setup.json"
        setup_data = json.loads(setup_path.read_text(encoding="utf-8")) if setup_path.exists() else {}
        if not setup_data.get("project_title"):
            print("ERROR: author-setup.json 缺少 project_title，不能确认初始化", file=sys.stderr)
            return 1
        setup_data["author_confirmed"] = True
        setup_data["confirmed_at"] = now()
        write_json(setup_path, setup_data)
        data = read_config(root)
        data.setdefault("setup", {})["status"] = "AUTHOR_CONFIRMED"
        data["next_action"] = "idea"
        data["updated_at"] = now()
        write_json(config_path(root), data)
        write_task(root, "idea", "作者已确认初始化配置；请开始创意产生。")
        print("AUTHOR_SETUP_CONFIRMED")
        return 0
    if command in {"planning", "work", "characters", "world", "research", "revision", "review"}:
        setup_path = root / "intent/author-setup.json"
        setup_data = json.loads(setup_path.read_text(encoding="utf-8")) if setup_path.exists() else {}
        if setup_data.get("author_confirmed") is not True:
            print("ERROR: 请先完成并确认初始化配置：canonloom setup --confirm", file=sys.stderr)
            return 1
    set_phase(root, phase, command, work_id)
    if command == "work" and work_id:
        start_run(root, work_id, "S0", args.input or "开始新的工作运行")
    write_task(root, command, args.input or "")
    print(TASK_TEXT[command])
    print("任务文件：tasks/current.md")
    return 0


def cmd_continue(args: argparse.Namespace) -> int:
    root = require_root(args)
    data = read_config(root)
    command = data.get("next_action") or "work"
    if command not in TASK_TEXT:
        command = "work"
    write_task(root, "continue", f"当前 next_action: {command}")
    print(TASK_TEXT["continue"])
    print(f"当前建议动作：canonloom {command}")
    return 0


def cmd_retry(args: argparse.Namespace) -> int:
    root = require_root(args)
    data = read_config(root)
    work_id = args.work_id or data.get("work_id")
    if not work_id:
        print("ERROR: retry 需要 work_id", file=sys.stderr)
        return 1
    stage = "S5b" if args.stage.lower() == "s5b" else args.stage.upper()
    if stage not in STAGE_REQUIREMENTS:
        print(f"ERROR: 未知重试阶段：{stage}", file=sys.stderr)
        return 1
    max_retries = int(data.get("workflow", {}).get("max_retry_per_stage", 2) or 2)
    existing_retries = 0
    for manifest_path in (root / "runs" / slug(work_id)).glob("*/manifest.json") if (root / "runs" / slug(work_id)).exists() else []:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            existing_retries += int(manifest.get("kind") == "retry" and manifest.get("start_stage") == stage)
        except (OSError, json.JSONDecodeError):
            continue
    if existing_retries >= max_retries:
        print(f"ERROR: {stage} 已达到最大重试次数 {max_retries}，需要人工决策或调整 workflow.max_retry_per_stage", file=sys.stderr)
        return 1
    run_id, run_dir = start_run(root, work_id, stage, args.reason or "作者/审查要求重新验证", kind="retry")
    data = read_config(root)
    data["work_id"] = work_id
    data["phase"] = "production"
    data["stage_id"] = STAGE_PREVIOUS[stage]
    data["next_action"] = stage
    data["updated_at"] = now()
    write_json(config_path(root), data)
    update_run(root, {"stage": stage, "status": "STARTED", "retries": 1})
    write_task(root, "continue", f"重试 {stage}；原因：{args.reason or '作者/审查要求重新验证'}。保留旧产物，生成新的阶段日志，不删除历史。")
    print(f"RETRY_READY: {stage}")
    print(f"RUN_ID: {run_id}")
    print(f"下一步：canonloom gate {stage} --work-id {work_id}")
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    text = (args.text or "").lower()
    if any(word in text for word in ("人物校准", "人物弧", "角色动机")):
        target = "characters"
    elif any(word in text for word in ("世界推演", "沙盘", "世界规则")):
        target = "world"
    elif any(word in text for word in ("资料核验", "研究", "来源")):
        target = "research"
    elif any(word in text for word in ("修订", "改稿", "润色")):
        target = "revision"
    elif any(word in text for word in ("审查", "审阅", "质量检查")):
        target = "review"
    elif any(word in text for word in ("对标", "拆书", "参考", "分析作品", "拆解")):
        target = "benchmark" if "对标" in text else "reference"
    elif any(word in text for word in ("导入", "旧稿", "已有小说", "续写原稿")):
        target = "import"
    elif any(word in text for word in ("卷", "篇章", "章契", "大纲", "规划")):
        target = "planning"
    elif any(word in text for word in ("继续", "下一章", "开始工作", "写作")):
        target = "work"
    else:
        target = "idea"
    print(f"ROUTE: {target}")
    print(TASK_TEXT[target])
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    root = require_root(args)
    report = collect_diagnosis(root)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"DIAGNOSIS: {report['status']}")
        for issue in report["issues"]:
            suffix = " [可修复]" if issue.get("repairable") else " [需人工处理]"
            print(f"- {issue['id']}: {issue['message']}{suffix}")
    return 0 if report["status"] == "OK" else 1


def cmd_state(args: argparse.Namespace) -> int:
    from narrative_state import main as state_main
    return state_main([args.action, "--root", args.root])


def cmd_repair(args: argparse.Namespace) -> int:
    root = require_root(args)
    before = collect_diagnosis(root)
    actions = []
    blocked = []
    if before["status"] == "BLOCKED":
        blocked = before["issues"]
    else:
        data = read_config(root)
        defaults = {
            "project_id": slug(root.name), "phase": "uninitialized", "mode": "standard",
            "work_id": None, "stage_id": None, "next_action": "setup", "updated_at": now(),
        }
        if data.get("schema_version") != SCHEMA_VERSION:
            actions.append({"action": "migrate_config", "from": data.get("schema_version"), "to": SCHEMA_VERSION})
            data = merge_defaults(data)
        for field, value in defaults.items():
            if field not in data:
                data[field] = value
                actions.append({"action": "add_config_field", "field": field})
        if not args.dry_run:
            for directory in required_dirs_missing(root):
                (root / directory).mkdir(parents=True, exist_ok=True)
                actions.append({"action": "create_directory", "path": directory})
            if not (root / "tasks/current.md").is_file():
                command = data.get("next_action") if data.get("next_action") in TASK_TEXT else "work"
                write_task(root, command, "由 canonloom repair 自动恢复；请先确认当前状态。")
                actions.append({"action": "create_task", "path": "tasks/current.md", "command": command})
            style_path = root / "intent/style-profile.json"
            if not style_path.exists():
                template = Path(__file__).resolve().parents[1] / "templates/style-profile.json"
                write_json(style_path, json.loads(template.read_text(encoding="utf-8")))
                actions.append({"action": "create_style_profile", "path": "intent/style-profile.json"})
            for name in ("author-setup.json", "ai-recognition.json"):
                target = root / "intent" / name
                if not target.exists():
                    template = Path(__file__).resolve().parents[1] / "templates" / name
                    write_json(target, json.loads(template.read_text(encoding="utf-8")))
                    actions.append({"action": "create_setup_artifact", "path": f"intent/{name}"})
            state_policy = root / "memory/narrative-state/state-policy.json"
            if not state_policy.exists():
                template = Path(__file__).resolve().parents[1] / "templates/narrative-state-policy.json"
                write_json(state_policy, json.loads(template.read_text(encoding="utf-8")))
                actions.append({"action": "create_narrative_state_policy", "path": "memory/narrative-state/state-policy.json"})
            for name in ("events.jsonl", "knowledge.jsonl", "reveals.json"):
                target = root / "memory/narrative-state" / name
                if not target.exists():
                    target.write_text("{\"reveals\": []}\n" if name == "reveals.json" else "", encoding="utf-8")
                    actions.append({"action": "create_narrative_state_artifact", "path": f"memory/narrative-state/{name}"})
            write_json(config_path(root), data)
        else:
            actions.extend({"action": "would_add_config_field", "field": field} for field in defaults if field not in read_config(root))
            actions.extend({"action": "would_create_directory", "path": directory} for directory in required_dirs_missing(root))
            if not (root / "tasks/current.md").is_file():
                actions.append({"action": "would_create_task", "path": "tasks/current.md"})
    report = {"schema_version": SCHEMA_VERSION, "created_at": now(), "dry_run": bool(args.dry_run), "before": before, "actions": actions, "blocked": blocked}
    if not args.dry_run:
        path = write_repair_log(root, report)
        after = collect_diagnosis(root)
        report["after"] = after
        write_json(path, report)
        print(f"REPAIR_LOG: {path.relative_to(root)}")
        print(f"REPAIR: {after['status']}")
        return 0 if after["status"] == "OK" else 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not blocked else 1


def cmd_upgrade(args: argparse.Namespace) -> int:
    """Upgrade an existing project using only safe structure migrations."""
    return cmd_repair(args)


def cmd_advanced(args: argparse.Namespace) -> int:
    print("AUTHOR COMMANDS")
    print("  " + " ".join(AUTHOR_COMMANDS))
    print("\nAGENT / MAINTAINER COMMANDS")
    print("  " + " ".join(ADVANCED_COMMANDS))
    print("\n说明：高级命令仍然可直接运行；普通作者通常只需要 Author Commands。")
    print("详细说明：docs/production-tools.md")
    return 0


def cmd_tool(args: argparse.Namespace) -> int:
    from canonloom_tools import main as tools_main
    tool_args = list(args.tool_args)
    started = time.perf_counter()
    if args.tool_name in {"validate", "beats", "index", "query", "context", "stats", "handoff"} and "--root" not in tool_args:
        tool_args.extend(["--root", args.root])
    code = tools_main([args.tool_name, *tool_args])
    try:
        update_run(require_root(args), {"tool_calls": 1, "latency_ms": round((time.perf_counter() - started) * 1000), "tool": args.tool_name, "status": "COMPLETED" if code == 0 else "FAILED"})
    except SystemExit:
        pass
    return code


def cmd_record(args: argparse.Namespace) -> int:
    root = require_root(args)
    if any(value < 0 for value in (args.input_tokens, args.output_tokens, args.latency_ms, args.retries)):
        print("ERROR: token、延迟和重试次数不能为负数", file=sys.stderr)
        return 1
    data = read_config(root)
    if not run_manifest_path(root, data) or not run_manifest_path(root, data).exists():
        print("ERROR: 当前没有活动 run。先运行 retry 或创建工作 run。", file=sys.stderr)
        return 1
    update_run(root, {"stage": args.stage, "model": args.model, "provider": args.provider, "input_tokens": args.input_tokens, "output_tokens": args.output_tokens, "latency_ms": args.latency_ms, "retries": args.retries, "status": "COMPLETED", "note": args.note or ""})
    print("RUN_EVENT_RECORDED")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    from canonloom_tools import build_handoff
    root = require_root(args)
    if args.status not in {"READY", "BLOCKED", "NEEDS_REVIEW", "FAILED"} or args.approval not in {"NONE", "AUTHOR_PENDING", "AUTHOR_APPROVED", "AUTHOR_REJECTED"}:
        print("ERROR: handoff status/approval 不符合协议", file=sys.stderr)
        return 1
    output = Path(args.output).expanduser().resolve() if args.output else None
    if output:
        try:
            output.relative_to(root)
        except ValueError:
            print("ERROR: handoff output 必须位于项目根目录内", file=sys.stderr)
            return 1
    result = build_handoff(root, args.work_id, args.source_stage, args.status, args.next_action, args.approval, args.files, args.reports, args.risk, output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_artifact_check(args: argparse.Namespace) -> int:
    from artifact_validator import check_artifact
    path = Path(args.path).expanduser().resolve()
    errors = check_artifact(args.kind, path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    root = require_root(args)
    data = read_config(root)
    work_id = args.work_id or data.get("work_id")
    if not work_id:
        print("ERROR: 没有 work_id。先运行：canonloom work --work-id chapter-001", file=sys.stderr)
        return 1
    data["work_id"] = work_id
    stage = "S5b" if args.stage.lower() == "s5b" else args.stage.upper()
    if stage not in STAGE_REQUIREMENTS:
        print(f"ERROR: 未知阶段：{stage}", file=sys.stderr)
        return 1
    previous = STAGE_PREVIOUS[stage]
    current = data.get("stage_id")
    if previous is not None and current != previous:
        print(f"GATE {stage}: BLOCKED")
        print(f"必须先通过 {previous}；当前记录阶段为 {current or 'NONE'}")
        data["next_action"] = f"gate:{previous}" if current is None else STAGE_NEXT.get(current, f"gate:{previous}")
        data["updated_at"] = now()
        write_json(config_path(root), data)
        return 1
    missing = []
    for template in STAGE_REQUIREMENTS[stage]:
        path = root / template.format(work_id=work_id)
        if not path.exists():
            missing.append(str(path.relative_to(root)))
    if missing:
        print(f"GATE {stage}: BLOCKED")
        print("缺少产物：")
        for item in missing:
            print(f"- {item}")
        data["next_action"] = f"produce:{stage}"
        data["updated_at"] = now()
        write_json(config_path(root), data)
        return 1

    from artifact_validator import check_artifact

    def artifact_errors(kind: str, path: Path) -> list[str]:
        return check_artifact(kind, path)

    if stage == "S0":
        checks = [
            ("chapter-contract", root / f"plan/chapter-contracts/{work_id}.json"),
            ("selection", root / f"workspace/selections/{work_id}.json"),
            ("context", root / f"workspace/context-packages/{work_id}.json"),
        ]
        for kind, path in checks:
            errors = artifact_errors(kind, path)
            if errors:
                print(f"GATE S0: BLOCKED\n{kind} 协议校验失败：")
                for error in errors:
                    print(f"- {error}")
                data["next_action"] = "repair:S0"
                data["updated_at"] = now()
                write_json(config_path(root), data)
                return 1
        if data.get("narrative_state", {}).get("mode", "optional") == "required":
            from narrative_state import collect
            state_result = collect(root)
            if state_result.get("status") != "OK":
                print("GATE S0: BLOCKED\nrequired narrative state 校验失败：")
                for error in state_result.get("errors", []):
                    print(f"- {error}")
                return 1

    if stage in {"S2", "S4", "S5"}:
        report_path = root / f"reviews/{work_id}.{'quick' if stage == 'S2' else 'strict' if stage == 'S4' else 'independent'}.json"
        errors = artifact_errors("finding-report", report_path)
        if errors:
            print(f"GATE {stage}: BLOCKED\n审查报告协议校验失败：")
            for error in errors:
                print(f"- {error}")
            return 1
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") not in {"PASS", "COMPLETED", "AGREEMENT"}:
            print(f"GATE {stage}: BLOCKED\n审查报告状态不是通过状态：{report.get('status')}")
            return 1
        if stage == "S4" and data.get("narrative_state", {}).get("mode", "optional") == "required":
            from narrative_state import collect
            state_result = collect(root)
            if state_result.get("status") != "OK":
                print("GATE S4: BLOCKED\nrequired narrative state 校验失败：")
                for error in state_result.get("errors", []):
                    print(f"- {error}")
                return 1
        if stage == "S5" and data.get("workflow", {}).get("require_review_provenance", True):
            required = {"review_id", "reviewer_mode", "run_id", "source_sha256"}
            missing_provenance = sorted(required - report.keys())
            if missing_provenance:
                print("GATE S5: BLOCKED\n独立审查缺少 provenance：")
                for field in missing_provenance:
                    print(f"- {field}")
                return 1
            strict_path = root / f"reviews/{work_id}.strict.json"
            if strict_path.exists():
                strict = json.loads(strict_path.read_text(encoding="utf-8"))
                if report.get("review_id") == strict.get("review_id") or report.get("run_id") == strict.get("run_id"):
                    print("GATE S5: BLOCKED\n独立审查不能复用 Strict 的 review_id 或 run_id")
                    return 1

    if stage == "S0":
        contract_path = root / f"plan/chapter-contracts/{work_id}.json"
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"GATE S0: BLOCKED\n章契无效：{exc}")
            return 1
        required_contract = {"id", "objective", "viewpoint", "time", "location", "required_changes", "exit_state"}
        if not required_contract.issubset(contract) or contract.get("id") != work_id:
            print("GATE S0: BLOCKED\n章契缺少必需字段或 id 与 work_id 不一致")
            return 1
    if stage == "S1":
        draft_path = root / f"drafts/{work_id}.md"
        if not draft_path.read_text(encoding="utf-8").strip():
            print("GATE S1: BLOCKED\n草稿为空")
            return 1

    json_artifacts = {
        "S2": root / f"reviews/{work_id}.quick.json",
        "S4": root / f"reviews/{work_id}.strict.json",
        "S5": root / f"reviews/{work_id}.independent.json",
        "S5b": root / f"reviews/{work_id}.cross-validation.json",
    }
    if stage in json_artifacts:
        try:
            report = json.loads(json_artifacts[stage].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"GATE {stage}: BLOCKED\n审查产物不是有效 JSON：{exc}")
            return 1
        if stage != "S5b" and "findings" not in report:
            print(f"GATE {stage}: BLOCKED\n审查报告缺少 findings 数组")
            return 1
        if stage == "S5b" and not {"status", "matched", "first_count", "second_count", "matches", "unmatched_first", "unmatched_second"}.issubset(report):
            print("GATE S5b: BLOCKED\n交叉验证报告缺少完整匹配字段")
            return 1
        findings = report.get("findings", [])
        if stage != "S5b" and (not isinstance(findings, list) or any(not isinstance(item, dict) or not {"id", "severity", "category", "location", "evidence", "issue", "fix", "status"}.issubset(item) or item.get("severity") not in {"BLOCKER", "MAJOR", "MINOR", "ADVISORY"} for item in findings)):
            print(f"GATE {stage}: BLOCKED\n审查报告包含不符合 Finding 协议的条目")
            return 1
        if stage == "S4" and (report.get("status") not in {"PASS", "COMPLETED", "AGREEMENT"} or any(item.get("severity") in {"BLOCKER", "MAJOR"} and item.get("status") not in {"fixed", "accepted_risk", "rejected"} for item in findings)):
            print(f"GATE {stage}: BLOCKED")
            print("Strict 检查未通过，必须回到 S3 修复")
            data["next_action"] = "S3"
            data["updated_at"] = now()
            write_json(config_path(root), data)
            return 1
        if stage == "S5b" and report.get("status") == "DISAGREEMENT":
            print(f"GATE {stage}: BLOCKED")
            print("交叉验证存在分歧，必须进入 HUMAN_DECISION")
            data["next_action"] = "HUMAN_DECISION"
            data["updated_at"] = now()
            write_json(config_path(root), data)
            return 1
        if stage == "S5b":
            first = str(report.get("first", ""))
            second = str(report.get("second", ""))
            if not first or not second or first == second:
                print("GATE S5b: BLOCKED\n交叉验证必须引用两份不同的审查报告")
                return 1

    if stage == "S6":
        approval_path = root / f"tasks/{work_id}.approval.json"
        try:
            approval = json.loads(approval_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"GATE S6: BLOCKED\n批准文件无效：{exc}")
            return 1
        expected_source = f"drafts/{work_id}.revised.md"
        if approval.get("work_id") not in {None, work_id} or approval.get("approved_artifact") not in {None, expected_source} or approval.get("approval") != "AUTHOR_APPROVED" or approval.get("action") != "approve_settlement":
            print("GATE S6: BLOCKED")
            print("S6 必须批准当前 work_id 对应的 revised draft，并使用 action=approve_settlement")
            return 1
        trace_path = root / f"traces/{work_id}.settlement.json"
        write_json(trace_path, {
            "schema_version": "0.1",
            "work_id": work_id,
            "stage_id": "S6",
            "status": "READY_FOR_SETTLEMENT",
            "source_draft": expected_source,
            "approval_ref": str(approval_path.relative_to(root)),
            "created_at": now(),
            "canon_promotion": "NONE",
        })

    data["phase"] = "settlement" if stage == "S6" else "production"
    data["stage_id"] = stage
    data["next_action"] = STAGE_NEXT[stage]
    data["updated_at"] = now()
    write_json(config_path(root), data)
    write_stage_trace(root, data, work_id, stage)
    update_run(root, {"stage": stage, "status": "PASSED", "run_status": "COMPLETED" if stage == "S6" else None})
    print(f"GATE {stage}: PASSED")
    print(f"NEXT: {STAGE_NEXT[stage]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="canonloom", description="CanonLoom 无 GUI、命令驱动的长篇小说工作流")
    parser.add_argument("--version", action="version", version=f"canonloom {REPOSITORY_VERSION}")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    init = sub.add_parser("init", help="初始化或补齐项目目录")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--name")
    init.add_argument("--mode", choices=["economy", "standard", "deep"], default="standard")
    init.add_argument("--genre")
    init.add_argument("--audience")
    init.add_argument("--language", default="zh-CN")
    init.add_argument("--pov")
    init.add_argument("--tone", help="逗号分隔的语气关键词")
    init.add_argument("--chapter-min", type=int)
    init.add_argument("--chapter-max", type=int)
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status", help="查看当前阶段和下一步")
    status.set_defaults(func=cmd_status)

    for name, help_text in (("setup", "完成项目初始化"), ("idea", "开始创意"), ("reference", "开始拆书"), ("import", "导入已有稿件"), ("planning", "开始项目/卷章规划"), ("work", "开始工作"), ("characters", "人物校准"), ("world", "世界推演"), ("research", "资料核验"), ("revision", "开始修订"), ("review", "开始审查"), ("benchmark", "对标拆解")):
        item = sub.add_parser(name, help=argparse.SUPPRESS if name in ADVANCED_COMMANDS else help_text)
        item.add_argument("--work-id")
        item.add_argument("--input", help="补充任务说明")
        if name == "setup":
            item.add_argument("--confirm", action="store_true", help="作者确认 author-setup.json")
        item.set_defaults(func=cmd_start, kind=name)

    cont = sub.add_parser("continue", help="继续当前工作")
    cont.set_defaults(func=cmd_continue)
    retry = sub.add_parser("retry", help=argparse.SUPPRESS)
    retry.add_argument("stage", choices=sorted(STAGE_REQUIREMENTS))
    retry.add_argument("--work-id")
    retry.add_argument("--reason")
    retry.set_defaults(func=cmd_retry)
    route = sub.add_parser("route", help="根据自然语言判断工作流")
    route.add_argument("text")
    route.set_defaults(func=cmd_route)
    diagnose = sub.add_parser("diagnose", help="检查项目结构和任务文件")
    diagnose.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    diagnose.set_defaults(func=cmd_diagnose)
    state = sub.add_parser("state", help="检查或汇总可选的叙事状态层")
    state.add_argument("action", choices=["validate", "report"])
    state.set_defaults(func=cmd_state)
    repair = sub.add_parser("repair", help="修复白名单内的项目结构问题")
    repair.add_argument("--dry-run", action="store_true", help="只显示拟执行的修复")
    repair.set_defaults(func=cmd_repair)

    upgrade = sub.add_parser("upgrade", help="将旧项目补齐到当前协议结构")
    upgrade.add_argument("--dry-run", action="store_true")
    upgrade.set_defaults(func=cmd_upgrade)
    advanced = sub.add_parser("advanced", help="查看 Agent 和维护工具")
    advanced.set_defaults(func=cmd_advanced)
    for name, help_text in (
        ("validate", "校验章节草稿"), ("beats", "校验章契和 Beat"),
        ("index", "构建章节索引"), ("query", "检索相关章节"),
        ("context", "编译最小上下文包"), ("cross-validate", "交叉验证两份审查报告"),
        ("style", "计算风格指标"), ("stats", "统计章节与稿件"),
        ("repair-plan", "从审查报告生成修复计划"), ("normalize-findings", "将旧审查输出统一为 Finding"),
    ):
        item = sub.add_parser(name, help=argparse.SUPPRESS)
        item.add_argument("tool_args", nargs=argparse.REMAINDER)
        item.set_defaults(func=cmd_tool, tool_name=name)
    handoff = sub.add_parser("handoff", help=argparse.SUPPRESS)
    handoff.add_argument("--work-id", required=True)
    handoff.add_argument("--source-stage", default="S0")
    handoff.add_argument("--status", default="READY")
    handoff.add_argument("--next-action", default="continue")
    handoff.add_argument("--approval", default="AUTHOR_PENDING")
    handoff.add_argument("--files", nargs="*", default=[])
    handoff.add_argument("--reports", nargs="*", default=[])
    handoff.add_argument("--risk", nargs="*", default=[])
    handoff.add_argument("--output")
    handoff.set_defaults(func=cmd_handoff)
    artifact = sub.add_parser("artifact-check", help=argparse.SUPPRESS)
    artifact.add_argument("kind", choices=["context", "handoff", "finding-report", "stage-log", "project-config", "style-profile", "author-setup", "ai-recognition"])
    artifact.add_argument("path")
    artifact.set_defaults(func=cmd_artifact_check)
    record = sub.add_parser("record", help=argparse.SUPPRESS)
    record.add_argument("--stage", default="runtime")
    record.add_argument("--model", default="unknown")
    record.add_argument("--provider", default="unknown")
    record.add_argument("--input-tokens", type=int, default=0)
    record.add_argument("--output-tokens", type=int, default=0)
    record.add_argument("--latency-ms", type=int, default=0)
    record.add_argument("--retries", type=int, default=0)
    record.add_argument("--note")
    record.set_defaults(func=cmd_record)
    settle = sub.add_parser("settle", help=argparse.SUPPRESS)
    settle.add_argument("--work-id", required=True)
    settle.add_argument("--source")
    settle.add_argument("--target")
    settle.set_defaults(func=lambda args: __import__("subprocess").run([sys.executable, str(Path(__file__).with_name("settle_chapter.py")), "--root", args.root, "--work-id", args.work_id] + (["--source", args.source] if args.source else []) + (["--target", args.target] if args.target else []), check=False).returncode)
    gate = sub.add_parser("gate", help=argparse.SUPPRESS)
    gate.add_argument("stage", choices=sorted(STAGE_REQUIREMENTS))
    gate.add_argument("--work-id")
    gate.set_defaults(func=cmd_gate)
    # argparse renders SUPPRESS literally for subparser choices; remove the
    # advanced pseudo-actions from the public help while keeping the commands
    # fully callable for agents and maintainers.
    sub._choices_actions = [action for action in sub._choices_actions if action.dest not in ADVANCED_COMMANDS]
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        raise SystemExit(args.func(args))
    except BrokenPipeError:
        raise SystemExit(0)
