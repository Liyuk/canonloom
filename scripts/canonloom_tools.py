#!/usr/bin/env python3
"""Dependency-free, story-agnostic production tools for CanonLoom.

These tools deliberately operate on contracts and Markdown files. They do not
call a model and they never promote content to canon.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEVERITIES = {"BLOCKER", "MAJOR", "MINOR", "ADVISORY"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))


def sentence_count(text: str) -> int:
    return max(1, len(re.findall(r"[^。！？!?；;]+[。！？!?；;]?", text)))


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}, text
    data: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip("\"'")
        if value.startswith("[") and value.endswith("]"):
            value = [item.strip().strip("\"'") for item in re.split(r"[,、]", value[1:-1]) if item.strip()]
        data[key.strip()] = value
    return data, parts[2].lstrip("\n")


def finding(fid: str, severity: str, category: str, location: str, evidence: str, issue: str, fix: str, source_refs: list[str] | None = None) -> dict[str, Any]:
    return {"id": fid, "severity": severity, "category": category, "location": location,
            "evidence": evidence[:240], "issue": issue, "fix": fix, "status": "open", "source_refs": source_refs or []}


def validate_chapter(chapter_path: Path, contract_path: Path | None = None, level: str = "quick", root: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    if not chapter_path.exists():
        findings.append(finding("FILE_MISSING", "BLOCKER", "format", str(chapter_path), "", "章节文件不存在", "确认输入路径"))
        return {"tool": "validate_chapter", "level": level, "status": "BLOCKED", "findings": findings}
    text = read_text(chapter_path)
    front, body = parse_frontmatter(text)
    contract = load_json(contract_path, {}) if contract_path else {}
    project_root = root or (contract_path.parent.parent.parent if contract_path else chapter_path.parent)
    style_path = project_root / "intent/style-profile.json"
    style = load_json(style_path, {}) if style_path.exists() else {}
    if not body.strip():
        findings.append(finding("BODY_EMPTY", "BLOCKER", "format", str(chapter_path), "", "正文为空", "补充正文后重新检查"))
    if "## 正文" in body:
        body = body.split("## 正文", 1)[1]
    chars = cjk_count(body)
    dialogue_matches = re.findall(r"“([^”]*)”|「([^」]*)」|『([^』]*)』", body)
    dialogue_text = "".join(part for match in dialogue_matches for part in match if part)
    dialogue_ratio = cjk_count(dialogue_text) / max(1, chars)
    min_chars = int(contract.get("min_chars", contract.get("word_target_min", 0)) or 0)
    max_chars = int(contract.get("max_chars", contract.get("word_target_max", 0)) or 0)
    if min_chars and chars < min_chars:
        findings.append(finding("LENGTH_SHORT", "MAJOR", "format", str(chapter_path), f"CJK={chars}, minimum={min_chars}", "正文低于契约长度", "补足契约要求的内容"))
    if max_chars and chars > max_chars:
            findings.append(finding("LENGTH_LONG", "MAJOR", "format", str(chapter_path), f"CJK={chars}, maximum={max_chars}", "正文超过契约长度", "压缩或拆分超出的内容"))
    dialogue_policy = style.get("dialogue", {})
    ratio_min = float(contract.get("dialogue_ratio_min", dialogue_policy.get("min_ratio", 0)) or 0)
    ratio_max = float(contract.get("dialogue_ratio_max", dialogue_policy.get("max_ratio", 0)) or 0)
    if ratio_max and dialogue_ratio > ratio_max:
        findings.append(finding("DIALOGUE_RATIO_HIGH", "MAJOR", "prose", str(chapter_path), f"dialogue_ratio={dialogue_ratio:.4f}, maximum={ratio_max:.4f}", "对白比例超过本章契约上限", "压缩重复确认，保留改变行动、关系或信息差的对白"))
    if ratio_min and dialogue_ratio < ratio_min:
        findings.append(finding("DIALOGUE_RATIO_LOW", "ADVISORY", "prose", str(chapter_path), f"dialogue_ratio={dialogue_ratio:.4f}, minimum={ratio_min:.4f}", "对白比例低于本章契约基线", "确认角色立场是否需要通过对白呈现"))
    surface = style.get("surface", {})
    style_refs = [str(style_path.relative_to(project_root))] if style_path.exists() else []
    for token in contract.get("forbidden_changes", []) + contract.get("forbidden_terms", []) + surface.get("forbidden_terms", []):
        if str(token) and str(token) in body:
            findings.append(finding("FORBIDDEN_CONTENT", "BLOCKER", "canon", str(chapter_path), str(token), f"出现禁止内容：{token}", "删除或提交作者决策", style_refs))
    for punctuation in contract.get("forbidden_punctuation", []) + surface.get("forbidden_punctuation", ["—"]):
        count = body.count(str(punctuation))
        if count:
            findings.append(finding("FORBIDDEN_PUNCTUATION", "MINOR", "prose", str(chapter_path), f"{punctuation} x {count}", "出现禁用标点", "按项目风格替换", style_refs))
    required = list(contract.get("required_changes", []))
    beats = list(contract.get("beats", []))
    for idx, item in enumerate(required + beats, 1):
        label = item if isinstance(item, str) else item.get("id", item.get("goal", f"beat-{idx}"))
        if isinstance(item, dict):
            label = item.get("required_text", item.get("goal", label))
        if label and str(label) not in body:
            findings.append(finding(f"BEAT_{idx:02d}_MISSING", "MAJOR", "structure", str(chapter_path), str(label), "契约要求的变化/Beat 未在正文留下可见证据", "补写、调整契约，或记录作者决策"))
    if level == "strict":
        for match in re.finditer(r"(?m)^\s*(?:上一章|下一章|作者|本章将|读者)[:：]", body):
            findings.append(finding("FOURTH_WALL", "MINOR", "prose", f"line {body[:match.start()].count(chr(10)) + 1}", match.group(0), "疑似出现作者侧/章节说明语句", "确认是否符合项目风格"))
        max_long = int(style.get("rhythm", {}).get("max_long_sentence_cjk") or 120)
        long_sentences = [s for s in re.split(r"[。！？!?]", body) if cjk_count(s) > max_long]
        if long_sentences:
            findings.append(finding("SENTENCE_LONG", "ADVISORY", "prose", str(chapter_path), long_sentences[0], "存在超长句", "按语义需要拆分"))
    rhythm = style.get("rhythm", {})
    avg_sentence = chars / max(1, sentence_count(body))
    paragraphs = [p for p in body.split("\n\n") if p.strip()]
    avg_paragraph = chars / max(1, len(paragraphs))
    if rhythm.get("min_avg_sentence_cjk") is not None and avg_sentence < float(rhythm["min_avg_sentence_cjk"]):
        findings.append(finding("RHYTHM_SENTENCE_SHORT", "ADVISORY", "prose", str(chapter_path), f"avg_sentence_cjk={avg_sentence:.2f}", "平均句长低于风格档案下限", "确认是否需要增加动作、感官或因果连接", style_refs))
    if rhythm.get("max_avg_sentence_cjk") is not None and avg_sentence > float(rhythm["max_avg_sentence_cjk"]):
        findings.append(finding("RHYTHM_SENTENCE_LONG", "ADVISORY", "prose", str(chapter_path), f"avg_sentence_cjk={avg_sentence:.2f}", "平均句长高于风格档案上限", "拆分过长表达或增加段落转折", style_refs))
    if rhythm.get("min_avg_paragraph_cjk") is not None and avg_paragraph < float(rhythm["min_avg_paragraph_cjk"]):
        findings.append(finding("RHYTHM_PARAGRAPH_SHORT", "ADVISORY", "prose", str(chapter_path), f"avg_paragraph_cjk={avg_paragraph:.2f}", "平均段落长度低于风格档案下限", "确认碎片化段落是否具有节奏功能", style_refs))
    if rhythm.get("max_avg_paragraph_cjk") is not None and avg_paragraph > float(rhythm["max_avg_paragraph_cjk"]):
        findings.append(finding("RHYTHM_PARAGRAPH_LONG", "ADVISORY", "prose", str(chapter_path), f"avg_paragraph_cjk={avg_paragraph:.2f}", "平均段落长度高于风格档案上限", "检查信息块和视角转折", style_refs))
    blockers = sum(1 for item in findings if item["severity"] in {"BLOCKER", "MAJOR"})
    return {"tool": "validate_chapter", "level": level, "chapter_file": str(chapter_path),
            "style_profile_ref": str(style_path.relative_to(project_root)) if style_path.exists() else None,
            "metrics": {"cjk_chars": chars, "sentences": sentence_count(body), "paragraphs": len(paragraphs), "avg_sentence_cjk": round(avg_sentence, 2), "avg_paragraph_cjk": round(avg_paragraph, 2), "dialogue_cjk_chars": cjk_count(dialogue_text), "dialogue_ratio": round(dialogue_ratio, 4)},
            "status": "PASS" if blockers == 0 else "NEEDS_REPAIR", "findings": findings}


def beats_validate(contract_path: Path, chapter_path: Path | None = None) -> dict[str, Any]:
    contract = load_json(contract_path, {})
    beats = contract.get("beats", contract.get("required_changes", []))
    issues = []
    if not beats:
        issues.append(finding("BEATS_EMPTY", "MAJOR", "structure", str(contract_path), "", "章契没有 beats 或 required_changes", "补充可执行的 Beat/变化"))
    for idx, beat in enumerate(beats, 1):
        if isinstance(beat, str) and not beat.strip():
            issues.append(finding(f"BEAT_{idx:02d}_EMPTY", "MAJOR", "structure", str(contract_path), "", "存在空 Beat", "补充目标、冲突或结果"))
        if isinstance(beat, dict) and not (beat.get("goal") or beat.get("objective") or beat.get("required_text")):
            issues.append(finding(f"BEAT_{idx:02d}_UNDERSPECIFIED", "MAJOR", "structure", str(contract_path), json.dumps(beat, ensure_ascii=False), "Beat 缺少可执行目标", "补充 goal/objective/required_text"))
    result = {"tool": "beat_validator", "contract": str(contract_path), "beat_count": len(beats), "status": "PASS" if not issues else "NEEDS_REPAIR", "findings": issues}
    if chapter_path:
        result["chapter_check"] = validate_chapter(chapter_path, contract_path, "quick")
    return result


def chapter_records(root: Path) -> list[dict[str, Any]]:
    candidates = []
    for path in sorted(set(root.glob("drafts/**/*.md")) | set(root.glob("manuscript/**/*.md"))):
        text = read_text(path)
        front, body = parse_frontmatter(text)
        number = front.get("chapter_id") or front.get("chapter") or (re.search(r"(?:chapter|Ch|第)\s*0*(\d+)", path.stem, re.I) or [None, None])[1]
        relative = str(path.relative_to(root))
        candidates.append({"id": str(number or path.stem), "title": front.get("title", path.stem), "file": relative, "cjk_chars": cjk_count(body), "text": body,
                           "viewpoint": front.get("viewpoint", ""), "location": front.get("location", ""),
                           "story_time": front.get("story_time", ""), "characters": front.get("characters", []),
                           "open_loops": front.get("open_loops", []), "contract": front.get("contract", "")})
    priority = lambda item: (0 if item["file"].startswith("manuscript/") else 1 if ".revised" in item["file"] else 2, item["file"])
    selected: dict[str, dict[str, Any]] = {}
    for item in candidates:
        if item["id"] not in selected or priority(item) < priority(selected[item["id"]]):
            selected[item["id"]] = item
    return sorted(selected.values(), key=lambda item: item["id"])


def build_index(root: Path, output: Path | None = None) -> dict[str, Any]:
    records = chapter_records(root)
    stop = set("的了和是我你他她它在有与也就都而及一个没有这那为以不人中上到从将着对并" )
    for record in records:
        chars = [c for c in record["text"] if "\u3400" <= c <= "\u9fff" and c not in stop]
        record["keywords"] = dict(Counter(chars).most_common(20))
        path = root / record["file"]
        record["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        record.pop("text", None)
    result = {"schema_version": "0.2", "generated_at": now(), "chapter_count": len(records), "chapters": records}
    save_json(output or root / "index/chapter-index.json", result)
    return result


def query_index(root: Path, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    index = load_json(root / "index/chapter-index.json") or build_index(root)
    query_chars = Counter(c for c in query if "\u3400" <= c <= "\u9fff")
    scored = []
    for record in index.get("chapters", []):
        keywords = record.get("keywords", {})
        overlap = sum(min(count, int(keywords.get(char, 0))) for char, count in query_chars.items())
        score = overlap / max(1, sum(query_chars.values()))
        scored.append({"id": record["id"], "title": record["title"], "file": record["file"], "score": round(score, 4), "cjk_chars": record["cjk_chars"]})
    return sorted(scored, key=lambda item: (-item["score"], item["id"]))[:top_k]


def compile_context(root: Path, contract_path: Path, selection_path: Path | None = None, output: Path | None = None) -> dict[str, Any]:
    contract = load_json(contract_path, {})
    selection = load_json(selection_path, {}) if selection_path else {}
    included = []
    seen = set()
    config = load_json(root / "canonloom.json", {})
    context_policy = config.get("context", {})
    style_policy = config.get("style_profile", {})

    def add_path(path: Path, reason: str, authority: str = "canon") -> None:
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
            return
        relative = str(path.relative_to(root))
        if relative in seen:
            return
        seen.add(relative)
        included.append({"path": relative, "reason": reason, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size, "authority": authority})

    for directory in ("canon/entities", "canon/rules", "canon/timeline", "canon/sources"):
        for path in sorted((root / directory).glob("**/*")) if (root / directory).exists() else []:
            add_path(path, "bounded canon context", "reference" if directory == "canon/sources" else "canon")
    for reference in contract.get("evidence_refs", []) + selection.get("files", []):
        candidate = root / reference
        if candidate.exists():
            add_path(candidate, "explicit contract/selection evidence", "reference" if "source" in reference else "canon")
    work_id = str(contract.get("id", contract_path.stem))
    if context_policy.get("include_handoff", True):
        handoff = root / "handoffs" / f"{work_id}.json"
        if handoff.exists():
            add_path(handoff, "current stage handoff", "workflow")
    if context_policy.get("include_previous_chapter") and selection.get("previous_chapter"):
        previous = root / selection["previous_chapter"]
        if previous.exists():
            add_path(previous, "explicit previous chapter", "manuscript")
    if not context_policy.get("exclude_unapproved_memory", True):
        for path in sorted((root / "memory/draft").glob("**/*")) if (root / "memory/draft").exists() else []:
            add_path(path, "draft memory allowed by project policy", "candidate")
    style_ref = style_policy.get("ref", "intent/style-profile.json")
    style_path = root / style_ref
    if style_path.exists():
        add_path(style_path, "project style profile", "policy")
    contract_ref = str(contract_path.relative_to(root) if contract_path.is_relative_to(root) else contract_path)
    package = {"schema_version": "0.2", "context_id": f"context-{contract.get('id', contract_path.stem)}", "work_id": str(contract.get("id", contract_path.stem)), "generated_at": now(), "compiled_at": now(), "contract_ref": contract_ref, "style_profile_ref": style_ref, "selection": selection, "selection_reason": "contract, style profile, and bounded canon directories", "contract": contract, "included_files": [item["path"] for item in included], "excluded_files": [], "source_versions": {item["path"]: item["sha256"] for item in included}, "included_sources": included, "provenance": included, "retrieval_policy": "Only explicitly selected and bounded project evidence is included."}
    save_json(output or root / "workspace/context-packages/context-package.json", package)
    return package


def cross_validate(first_path: Path, second_path: Path, output: Path | None = None) -> dict[str, Any]:
    first = load_json(first_path, {})
    second = load_json(second_path, {})
    a = first.get("findings", first.get("issues", []))
    b = second.get("findings", second.get("issues", []))
    pairs = []
    used_right = set()
    for left in a:
        for right_index, right in enumerate(b):
            if right_index in used_right:
                continue
            ltext = json.dumps(left, ensure_ascii=False)
            rtext = json.dumps(right, ensure_ascii=False)
            common = set(re.findall(r"[\u4e00-\u9fffA-Za-z]{2,}", ltext)) & set(re.findall(r"[\u4e00-\u9fffA-Za-z]{2,}", rtext))
            same_severity = left.get("severity", "ADVISORY") == right.get("severity", "ADVISORY")
            if left.get("id") == right.get("id") or (len(common) >= 2 and same_severity):
                used_right.add(right_index)
                pairs.append({"left": left.get("id"), "right": right.get("id"), "agreement": "matched", "severity_agreement": same_severity, "shared_terms": sorted(common)[:12]})
                break
    unmatched_left = [item.get("id") for item in a if item.get("id") not in {pair["left"] for pair in pairs}]
    unmatched_right = [item.get("id") for index, item in enumerate(b) if index not in used_right]
    status = "AGREEMENT" if not unmatched_left and not unmatched_right else "DISAGREEMENT"
    result = {"tool": "cross_validate", "generated_at": now(), "first": str(first_path), "second": str(second_path), "matched": len(pairs), "first_count": len(a), "second_count": len(b), "status": status, "matches": pairs, "unmatched_first": unmatched_left, "unmatched_second": unmatched_right}
    if output:
        save_json(output, result)
    return result


def style_metrics(paths: list[Path]) -> dict[str, Any]:
    text = "\n".join(parse_frontmatter(read_text(path))[1] for path in paths)
    sentences = sentence_count(text)
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    dialogue_matches = re.findall(r"“([^”]*)”|「([^」]*)」|『([^』]*)』", text)
    dialogue = "".join(part for match in dialogue_matches for part in match if part)
    total = cjk_count(text)
    return {"tool": "style_fingerprint", "generated_at": now(), "files": [str(p) for p in paths], "metrics": {"cjk_chars": total, "sentences": sentences, "paragraphs": paragraphs, "avg_sentence_cjk": round(total / sentences, 2), "dialogue_cjk_chars": cjk_count(dialogue), "dialogue_ratio": round(cjk_count(dialogue) / max(1, total), 4), "punctuation_density": round(len(re.findall(r"[，。！？；：,.!?;:]", text)) / max(1, total), 4)}}


def stats(root: Path) -> dict[str, Any]:
    records = chapter_records(root)
    return {"tool": "arc_stats", "generated_at": now(), "chapter_count": len(records), "total_cjk_chars": sum(item["cjk_chars"] for item in records), "draft_count": sum(item["file"].startswith("drafts/") for item in records), "manuscript_count": sum(item["file"].startswith("manuscript/") for item in records)}


def normalize_report(report_path: Path, adapter_warning: bool = False) -> dict[str, Any]:
    data = load_json(report_path, {})
    severity_map = {"S1": "BLOCKER", "S2": "MAJOR", "S3": "MINOR", "S4": "ADVISORY"}
    normalized = []
    for i, item in enumerate(data.get("findings", data.get("issues", [])), 1):
        severity = severity_map.get(item.get("severity"), item.get("severity", "ADVISORY"))
        category = item.get("category", "information")
        if category not in {"structure", "character", "prose", "continuity", "causal", "canon", "information", "format", "reader_promise"}:
            category = "information"
        normalized.append({"id": item.get("id", f"ADAPTER_{i:02d}"), "severity": severity if severity in SEVERITIES else "ADVISORY", "category": category, "location": str(item.get("location", report_path)), "evidence": str(item.get("evidence", item.get("message", "")))[:240], "issue": item.get("issue", item.get("message", "兼容性报告中的问题")), "fix": item.get("fix", item.get("suggestion", "由作者或 Agent 判断是否处理")), "status": item.get("status", "open"), "source_refs": item.get("source_refs", [str(report_path)]), "adapter_warning": adapter_warning, "source_tool": data.get("tool", data.get("source_tool", "legacy-adapter"))})
    result = {"schema_version": "0.1", "tool": "normalize_findings", "generated_at": now(), "source": str(report_path), "status": data.get("status", "COMPLETED"), "findings": normalized}
    return result


def repair_plan(report_path: Path) -> dict[str, Any]:
    data = load_json(report_path, {})
    findings = data.get("findings", data.get("issues", []))
    severity_map = {"S1": "BLOCKER", "S2": "MAJOR", "S3": "MINOR", "S4": "ADVISORY"}
    return {"tool": "repair_plan", "source": str(report_path), "policy": "Do not edit canon or promote state; author approval remains required.", "steps": [{"order": i, "finding_id": item.get("id", f"finding-{i}"), "severity": severity_map.get(item.get("severity"), item.get("severity", "ADVISORY")), "instruction": item.get("fix", item.get("message", "Review this finding manually")), "source_refs": item.get("source_refs", [str(report_path)]), "status": "pending"} for i, item in enumerate(findings, 1)]}


def build_handoff(root: Path, work_id: str, source_stage: str, status: str, next_action: str, approval: str, files: list[str], reports: list[str], risks: list[str], output: Path | None = None) -> dict[str, Any]:
    if source_stage not in {"S0", "S1", "S2", "S3", "S4", "S5", "S5b", "S6"}:
        raise ValueError("invalid source_stage")
    if status not in {"READY", "BLOCKED", "NEEDS_REVIEW", "FAILED"}:
        raise ValueError("invalid handoff status")
    if approval not in {"NONE", "AUTHOR_PENDING", "AUTHOR_APPROVED", "AUTHOR_REJECTED"}:
        raise ValueError("invalid handoff approval")
    result = {"schema_version": "0.2", "generated_at": now(), "work_id": work_id, "source_stage": source_stage, "status": status, "current_files": files, "latest_reports": reports, "next_action": next_action, "preserved_risks": risks, "approval": approval}
    save_json(output or root / "handoffs" / f"{work_id}.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CanonLoom generic production tools")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate"); p.add_argument("chapter"); p.add_argument("--contract"); p.add_argument("--root", default="."); p.add_argument("--level", choices=["quick", "strict"], default="quick"); p.add_argument("--output")
    p = sub.add_parser("beats"); p.add_argument("contract"); p.add_argument("--chapter"); p.add_argument("--root", default="."); p.add_argument("--output")
    p = sub.add_parser("index"); p.add_argument("--root", default="."); p.add_argument("--output")
    p = sub.add_parser("query"); p.add_argument("query"); p.add_argument("--root", default="."); p.add_argument("--top-k", type=int, default=5)
    p = sub.add_parser("context"); p.add_argument("contract"); p.add_argument("--root", default="."); p.add_argument("--selection"); p.add_argument("--output")
    p = sub.add_parser("cross-validate"); p.add_argument("first"); p.add_argument("second"); p.add_argument("--output")
    p = sub.add_parser("style"); p.add_argument("files", nargs="+")
    p = sub.add_parser("stats"); p.add_argument("--root", default=".")
    p = sub.add_parser("repair-plan"); p.add_argument("report"); p.add_argument("--output")
    p = sub.add_parser("normalize-findings"); p.add_argument("report"); p.add_argument("--adapter-warning", action="store_true"); p.add_argument("--output")
    p = sub.add_parser("handoff"); p.add_argument("--root", default="."); p.add_argument("--work-id", required=True); p.add_argument("--source-stage", default="S0"); p.add_argument("--status", default="READY"); p.add_argument("--next-action", default="continue"); p.add_argument("--approval", default="PENDING"); p.add_argument("--files", nargs="*", default=[]); p.add_argument("--reports", nargs="*", default=[]); p.add_argument("--risk", nargs="*", default=[]); p.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "validate":
        root = Path(args.root)
        result = validate_chapter(Path(args.chapter) if Path(args.chapter).is_absolute() else root / args.chapter, (Path(args.contract) if Path(args.contract).is_absolute() else root / args.contract) if args.contract else None, args.level, root)
        if args.output:
            save_json(Path(args.output) if Path(args.output).is_absolute() else root / args.output, result)
    elif args.command == "beats":
        root = Path(args.root)
        contract = Path(args.contract) if Path(args.contract).is_absolute() else root / args.contract
        chapter = (Path(args.chapter) if Path(args.chapter).is_absolute() else root / args.chapter) if args.chapter else None
        result = beats_validate(contract, chapter)
        if args.output:
            save_json(Path(args.output) if Path(args.output).is_absolute() else root / args.output, result)
    elif args.command == "index": result = build_index(Path(args.root), Path(args.output) if args.output else None)
    elif args.command == "query": result = {"query": args.query, "results": query_index(Path(args.root), args.query, args.top_k)}
    elif args.command == "context":
        root = Path(args.root)
        contract = Path(args.contract) if Path(args.contract).is_absolute() else root / args.contract
        selection = (Path(args.selection) if Path(args.selection).is_absolute() else root / args.selection) if args.selection else None
        output = (Path(args.output) if Path(args.output).is_absolute() else root / args.output) if args.output else None
        result = compile_context(root, contract, selection, output)
    elif args.command == "cross-validate": result = cross_validate(Path(args.first), Path(args.second), Path(args.output) if args.output else None)
    elif args.command == "style": result = style_metrics([Path(item) for item in args.files])
    elif args.command == "stats": result = stats(Path(args.root))
    elif args.command == "normalize-findings":
        result = normalize_report(Path(args.report), args.adapter_warning)
        if args.output:
            save_json(Path(args.output), result)
    elif args.command == "handoff":
        root = Path(args.root)
        output = Path(args.output) if args.output and Path(args.output).is_absolute() else root / args.output if args.output else None
        result = build_handoff(root, args.work_id, args.source_stage, args.status, args.next_action, args.approval, args.files, args.reports, args.risk, output)
    else:
        result = repair_plan(Path(args.report))
        if args.output:
            save_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"NEEDS_REPAIR", "BLOCKED", "DISAGREEMENT"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
