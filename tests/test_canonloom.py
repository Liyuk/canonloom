import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "canonloom.py"


class CanonLoomCliTests(unittest.TestCase):
    def run_cli(self, project, *args):
        return subprocess.run([sys.executable, str(CLI), "--root", str(project), *args], text=True, capture_output=True)

    def test_init_and_diagnose(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            result = subprocess.run([sys.executable, str(CLI), "init", str(project), "--name", "smoke"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(self.run_cli(project, "diagnose").returncode, 0)
            self.assertEqual(self.run_cli(project, "idea", "--input", "一个关于选择的故事").returncode, 0)

    def test_gate_requires_order_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            self.assertNotEqual(self.run_cli(project, "gate", "S1", "--work-id", "chapter-001").returncode, 0)
            self.assertNotEqual(self.run_cli(project, "gate", "S0", "--work-id", "chapter-001").returncode, 0)
            for path in ("plan/chapter-contracts/chapter-001.json", "workspace/selections/chapter-001.json", "workspace/context-packages/chapter-001.json"):
                target = project / path
                target.parent.mkdir(parents=True, exist_ok=True)
                payload = {"id": "chapter-001", "objective": "make a choice", "viewpoint": "observer", "time": "day", "location": "place", "required_changes": [], "exit_state": "new state"} if path.startswith("plan/") else ({"selected_option": "option-a", "selection_status": "AUTHOR_CONFIRMED", "author_confirmed": True} if path.startswith("workspace/selections/") else {"schema_version": "0.2", "context_id": "context-chapter-001", "work_id": "chapter-001", "included_files": [], "selection_reason": "test", "compiled_at": "2026-01-01T00:00:00Z", "included_sources": [], "provenance": []})
                target.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "gate", "S0", "--work-id", "chapter-001").returncode, 0)
            status = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            self.assertEqual(status["stage_id"], "S0")
            self.assertNotEqual(self.run_cli(project, "gate", "S2", "--work-id", "chapter-001").returncode, 0)

    def test_route_is_author_facing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            result = self.run_cli(project, "route", "我想先拆书分析参考作品")
            self.assertEqual(result.returncode, 0)
            self.assertIn("ROUTE: reference", result.stdout)

    def test_repair_restores_safe_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            (project / "tasks/current.md").unlink()
            (project / "reviews").rmdir()
            preview = self.run_cli(project, "repair", "--dry-run")
            self.assertEqual(preview.returncode, 0)
            self.assertIn("would_create_directory", preview.stdout)
            repaired = self.run_cli(project, "repair")
            self.assertEqual(repaired.returncode, 0)
            self.assertEqual(self.run_cli(project, "diagnose").returncode, 0)
            self.assertTrue(list((project / "logs/repairs").glob("repair-*.json")))

    def test_production_tools_run_on_generic_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            contract = project / "plan/chapter-contracts/chapter-001.json"
            contract.write_text(json.dumps({
                "id": "chapter-001", "objective": "make a decision", "viewpoint": "observer",
                "time": "day", "location": "place", "required_changes": ["decision"],
                "exit_state": "a new question", "beats": [{"id": "B1", "goal": "decision"}],
            }), encoding="utf-8")
            draft = project / "drafts/chapter-001.md"
            draft.write_text("# Chapter\n\nThe observer makes a decision.\n", encoding="utf-8")
            result = self.run_cli(project, "beats", str(contract))
            self.assertEqual(result.returncode, 0)
            result = self.run_cli(project, "validate", str(draft), "--contract", str(contract), "--level", "quick")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(self.run_cli(project, "context", str(contract)).returncode, 0)
            self.assertEqual(self.run_cli(project, "index").returncode, 0)
            query = self.run_cli(project, "query", "decision")
            self.assertEqual(query.returncode, 0)
            self.assertEqual(self.run_cli(project, "stats").returncode, 0)

    def test_retry_preserves_state_and_reopens_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            result = self.run_cli(project, "retry", "S0", "--work-id", "chapter-001", "--reason", "new validation pass")
            self.assertEqual(result.returncode, 0)
            data = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            self.assertIsNone(data["stage_id"])
            self.assertEqual(data["work_id"], "chapter-001")
            self.assertTrue(list((project / "runs/chapter-001").glob("*/manifest.json")))
            self.assertEqual(self.run_cli(project, "record", "--stage", "S0", "--input-tokens", "10", "--output-tokens", "5").returncode, 0)

    def test_handoff_provenance_and_rich_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            chapter = project / "manuscript/chapter-001.md"
            chapter.write_text("---\nchapter_id: chapter-001\ntitle: 选择\nviewpoint: 观察者\nlocation: 城门\ncharacters: [甲、乙]\n---\n\n正文。\n", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "index").returncode, 0)
            index = json.loads((project / "index/chapter-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["schema_version"], "0.2")
            self.assertEqual(index["chapters"][0]["characters"], ["甲", "乙"])
            contract = project / "plan/chapter-contracts/chapter-001.json"
            contract.write_text("{}", encoding="utf-8")
            source = project / "canon/entities/observer.md"
            source.write_text("# 观察者\n\n已知事实。\n", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "context", str(contract)).returncode, 0)
            package = json.loads((project / "workspace/context-packages/context-package.json").read_text(encoding="utf-8"))
            self.assertTrue(package["provenance"])
            self.assertIn("memory/narrative-state/events.jsonl", package["included_files"])
            self.assertEqual(self.run_cli(project, "handoff", "--work-id", "chapter-001").returncode, 0)
            self.assertTrue((project / "handoffs/chapter-001.json").exists())
            handoff = json.loads((project / "handoffs/chapter-001.json").read_text(encoding="utf-8"))
            self.assertEqual(handoff["schema_version"], "0.2")

    def test_settlement_requires_s6_and_matching_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            source = project / "drafts/chapter-001.revised.md"
            source.write_text("draft\n", encoding="utf-8")
            (project / "tasks/chapter-001.approval.json").write_text(json.dumps({"approval": "AUTHOR_APPROVED", "action": "approve_settlement", "work_id": "chapter-001", "approved_artifact": "drafts/chapter-001.revised.md"}), encoding="utf-8")
            (project / "traces/chapter-001.settlement.json").write_text(json.dumps({"work_id": "chapter-001", "source_draft": "drafts/chapter-001.revised.md"}), encoding="utf-8")
            blocked = subprocess.run([sys.executable, str(ROOT / "scripts/settle_chapter.py"), "--root", str(project), "--work-id", "chapter-001"], text=True, capture_output=True)
            self.assertNotEqual(blocked.returncode, 0)
            data = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            data.update({"work_id": "chapter-001", "stage_id": "S6"})
            (project / "canonloom.json").write_text(json.dumps(data), encoding="utf-8")
            settled = subprocess.run([sys.executable, str(ROOT / "scripts/settle_chapter.py"), "--root", str(project), "--work-id", "chapter-001"], text=True, capture_output=True)
            self.assertEqual(settled.returncode, 0)
            self.assertTrue((project / "manuscript/chapter-001.md").exists())
            settlement = json.loads(settled.stdout)
            self.assertEqual(settlement["index_status"], "UPDATED")
            self.assertEqual(settlement["state_promotion"], "AUTHOR_APPROVAL_REQUIRED")
            self.assertTrue((project / "index/chapter-index.json").exists())

    def test_s6_gate_creates_settlement_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            data = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            data.update({"work_id": "chapter-001", "stage_id": "S5b"})
            (project / "canonloom.json").write_text(json.dumps(data), encoding="utf-8")
            (project / "tasks/chapter-001.approval.json").write_text(json.dumps({
                "approval": "AUTHOR_APPROVED", "action": "approve_settlement",
                "work_id": "chapter-001", "approved_artifact": "drafts/chapter-001.revised.md"
            }), encoding="utf-8")
            result = self.run_cli(project, "gate", "S6", "--work-id", "chapter-001")
            self.assertEqual(result.returncode, 0)
            trace = json.loads((project / "traces/chapter-001.settlement.json").read_text(encoding="utf-8"))
            self.assertEqual(trace["status"], "READY_FOR_SETTLEMENT")

    def test_gate_rejects_empty_review_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            contract = {"id": "chapter-001", "objective": "choose", "viewpoint": "observer", "time": "day", "location": "place", "required_changes": [], "exit_state": "changed"}
            (project / "plan/chapter-contracts/chapter-001.json").write_text(json.dumps(contract), encoding="utf-8")
            (project / "workspace/selections/chapter-001.json").write_text(json.dumps({"selected_option": "option-a", "selection_status": "AUTHOR_CONFIRMED", "author_confirmed": True}), encoding="utf-8")
            (project / "workspace/context-packages/chapter-001.json").write_text(json.dumps({"schema_version": "0.2", "context_id": "context-chapter-001", "work_id": "chapter-001", "included_files": [], "selection_reason": "test", "compiled_at": "2026-01-01T00:00:00Z", "included_sources": [], "provenance": []}), encoding="utf-8")
            self.assertEqual(self.run_cli(project, "gate", "S0", "--work-id", "chapter-001").returncode, 0)
            (project / "drafts/chapter-001.md").write_text("draft", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "gate", "S1", "--work-id", "chapter-001").returncode, 0)
            (project / "reviews/chapter-001.quick.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
            self.assertNotEqual(self.run_cli(project, "gate", "S2", "--work-id", "chapter-001").returncode, 0)

    def test_retry_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            config = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            config["workflow"]["max_retry_per_stage"] = 1
            (project / "canonloom.json").write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(self.run_cli(project, "retry", "S0", "--work-id", "chapter-001").returncode, 0)
            self.assertNotEqual(self.run_cli(project, "retry", "S0", "--work-id", "chapter-001").returncode, 0)

    def test_artifact_check_is_available_without_jsonschema(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            self.assertEqual(self.run_cli(project, "artifact-check", "project-config", str(project / "canonloom.json")).returncode, 0)
            bad = project / "bad.json"
            bad.write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
            self.assertNotEqual(self.run_cli(project, "artifact-check", "finding-report", str(bad)).returncode, 0)

    def test_init_creates_author_and_ai_setup_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            result = subprocess.run([sys.executable, str(CLI), "init", str(project), "--name", "Sample Story", "--genre", "都市神秘", "--audience", "成人读者", "--pov", "close-third", "--tone", "冷静,潮湿", "--chapter-min", "3000"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            author = json.loads((project / "intent/author-setup.json").read_text(encoding="utf-8"))
            ai = json.loads((project / "intent/ai-recognition.json").read_text(encoding="utf-8"))
            self.assertEqual(author["genre"], "都市神秘")
            self.assertEqual(author["tone"], ["冷静", "潮湿"])
            self.assertFalse(author["author_confirmed"])
            self.assertEqual(ai["status"], "PENDING")
            self.assertEqual(self.run_cli(project, "artifact-check", "author-setup", str(project / "intent/author-setup.json")).returncode, 0)

    def test_version_and_english_task_output(self):
        version = subprocess.run([sys.executable, str(CLI), "--version"], text=True, capture_output=True)
        self.assertEqual(version.returncode, 0)
        expected_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(f"canonloom {expected_version}", version.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            result = subprocess.run([sys.executable, str(CLI), "init", str(project), "--name", "English Story", "--language", "en-US", "--genre", "mystery", "--audience", "adult", "--pov", "close-third"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(self.run_cli(project, "setup", "--confirm").returncode, 0)
            self.assertEqual(self.run_cli(project, "idea", "--input", "an unreliable witness").returncode, 0)
            task = (project / "tasks/current.md").read_text(encoding="utf-8")
            self.assertIn("LANGUAGE: en", task)
            self.assertIn("Start ideation", task)

    def test_cli_surface_hides_advanced_tools_but_keeps_index(self):
        help_result = subprocess.run([sys.executable, str(CLI), "--help"], text=True, capture_output=True)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("advanced", help_result.stdout)
        self.assertNotIn("==SUPPRESS==", help_result.stdout)
        self.assertNotIn("cross-validate", help_result.stdout)
        advanced = subprocess.run([sys.executable, str(CLI), "advanced"], text=True, capture_output=True)
        self.assertEqual(advanced.returncode, 0)
        self.assertIn("cross-validate", advanced.stdout)

    def test_optional_narrative_state_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project), "--name", "State Story"], check=True)
            self.assertEqual(self.run_cli(project, "state", "validate").returncode, 0)
            event = project / "memory/narrative-state/events.jsonl"
            event.write_text(json.dumps({
                "event_id": "E-001", "chapter_id": "chapter-001", "source_ref": "drafts/chapter-001.md",
                "subject": "protagonist", "action": "discovers", "object": "sealed letter",
                "status": "PROPOSED"
            }) + "\n", encoding="utf-8")
            report = self.run_cli(project, "state", "report")
            self.assertEqual(report.returncode, 0)
            self.assertIn('"events": 1', report.stdout)
            (project / "memory/narrative-state/reveals.json").write_text('{"reveals": [{"setup_id": "S-001", "status": "OPEN", "reader_knows": false, "protagonist_knows": false}]}\n', encoding="utf-8")
            self.assertEqual(self.run_cli(project, "state", "validate").returncode, 0)

    def test_s0_rejects_malformed_contract_and_upgrade_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            contract = project / "plan/chapter-contracts/chapter-001.json"
            contract.write_text(json.dumps({
                "id": "chapter-001", "objective": "choose", "viewpoint": "observer",
                "time": "day", "location": "place", "required_changes": [],
                "exit_state": "changed", "causal_change": {}
            }), encoding="utf-8")
            (project / "workspace/selections/chapter-001.json").write_text(json.dumps({"selected_option": "a"}), encoding="utf-8")
            (project / "workspace/context-packages/chapter-001.json").write_text(json.dumps({
                "schema_version": "0.2", "context_id": "context-chapter-001", "work_id": "chapter-001",
                "included_files": [], "selection_reason": "test", "compiled_at": "now",
                "included_sources": [], "provenance": []
            }), encoding="utf-8")
            self.assertNotEqual(self.run_cli(project, "gate", "S0", "--work-id", "chapter-001").returncode, 0)
            self.assertEqual(self.run_cli(project, "upgrade", "--dry-run").returncode, 0)

    def test_s5_requires_independent_review_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "story"
            subprocess.run([sys.executable, str(CLI), "init", str(project)], check=True)
            data = json.loads((project / "canonloom.json").read_text(encoding="utf-8"))
            data.update({"work_id": "chapter-001", "stage_id": "S4"})
            (project / "canonloom.json").write_text(json.dumps(data), encoding="utf-8")
            (project / "reviews/chapter-001.independent.json").write_text(json.dumps({"status": "PASS", "findings": []}), encoding="utf-8")
            blocked = self.run_cli(project, "gate", "S5", "--work-id", "chapter-001")
            self.assertNotEqual(blocked.returncode, 0)
            report = {"status": "PASS", "findings": [], "review_id": "review-independent", "reviewer_mode": "same_model_adversarial_pass", "run_id": "run-independent", "source_sha256": "abc"}
            (project / "reviews/chapter-001.independent.json").write_text(json.dumps(report), encoding="utf-8")
            self.assertEqual(self.run_cli(project, "gate", "S5", "--work-id", "chapter-001").returncode, 0)


if __name__ == "__main__":
    unittest.main()
