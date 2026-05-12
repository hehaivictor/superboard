from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_skill.py"
spec = importlib.util.spec_from_file_location("validate_skill", VALIDATOR_PATH)
validate_skill = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["validate_skill"] = validate_skill
spec.loader.exec_module(validate_skill)

RUNNER_PATH = ROOT / "scripts" / "super_board_run.py"
runner_spec = importlib.util.spec_from_file_location("super_board_run", RUNNER_PATH)
super_board_run = importlib.util.module_from_spec(runner_spec)
assert runner_spec.loader is not None
sys.modules["super_board_run"] = super_board_run
runner_spec.loader.exec_module(super_board_run)

SERVER_PATH = ROOT / "web" / "server.py"
server_spec = importlib.util.spec_from_file_location("super_board_server", SERVER_PATH)
super_board_server = importlib.util.module_from_spec(server_spec)
assert server_spec.loader is not None
server_spec.loader.exec_module(super_board_server)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_persona(name: str = "Example") -> str:
    sections = [f"# {name}"]
    for field in validate_skill.REQUIRED_PERSONA_FIELDS:
        sections.append(f"## {field}\n\n- content")
    return "\n\n".join(sections) + "\n"


class ValidateSkillTests(unittest.TestCase):
    def test_default_skill_passes(self) -> None:
        issues = validate_skill.validate(ROOT)
        self.assertEqual([], issues)

    def test_missing_persona_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in validate_skill.REQUIRED_FILES:
                write(root / relative, "content\n")
            write(
                root / "boards/default-board.yaml",
                "\n".join(
                    [
                        "committees:",
                        "  - id: test",
                        "    personas:",
                        "      - missing-persona",
                    ]
                ),
            )

            issues = validate_skill.validate(root)

        self.assertTrue(
            any(issue.path == "personas/missing-persona.md" and "does not exist" in issue.message for issue in issues)
        )

    def test_missing_required_field_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in validate_skill.REQUIRED_FILES:
                write(root / relative, "content\n")
            write(
                root / "boards/default-board.yaml",
                "\n".join(
                    [
                        "committees:",
                        "  - id: test",
                        "    personas:",
                        "      - incomplete-persona",
                    ]
                ),
            )
            persona = minimal_persona().replace("## red_flags\n\n- content\n\n", "")
            write(root / "personas/incomplete-persona.md", persona)

            issues = validate_skill.validate(root)

        self.assertTrue(
            any(issue.path == "personas/incomplete-persona.md" and "red_flags" in issue.message for issue in issues)
        )

    def test_deep_output_examples_have_required_sections(self) -> None:
        for relative in validate_skill.DEEP_OUTPUTS:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for section in validate_skill.REQUIRED_BOARD_MEMO_SECTIONS:
                self.assertIn(f"## {section}", text, relative)
            for marker in ["反证", "失败路径", "决策条件", "30 / 60 / 90"]:
                self.assertIn(marker, text, relative)
            self.assertGreaterEqual(text.count("```mermaid"), validate_skill.REQUIRED_MERMAID_BLOCKS, relative)

    def test_board_template_contains_required_mermaid_blocks(self) -> None:
        text = (ROOT / "templates/board-memo.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("```mermaid"), validate_skill.REQUIRED_MERMAID_BLOCKS)
        for section in ["Evidence Packet", "Assumption Ledger", "Decision Log Entry"]:
            self.assertIn(f"## {section}", text)

    def test_required_modes_exist_and_have_unique_ids(self) -> None:
        mode_ids = []
        for mode_id in validate_skill.REQUIRED_MODE_IDS:
            path = ROOT / "boards" / "modes" / f"{mode_id}.yaml"
            self.assertTrue(path.is_file(), mode_id)
            fields = validate_skill.parse_simple_yaml_fields(path)
            self.assertEqual(mode_id, fields.get("mode_id"))
            for field in validate_skill.REQUIRED_MODE_FIELDS:
                self.assertIn(field, fields, mode_id)
            mode_ids.append(fields["mode_id"])
        self.assertEqual(len(mode_ids), len(set(mode_ids)))

    def test_schema_files_are_valid_json_and_declare_required_fields(self) -> None:
        for relative in validate_skill.REQUIRED_SCHEMA_FILES:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertIn("$schema", payload, relative)
            self.assertEqual("object", payload["type"], relative)
            self.assertGreater(len(payload["required"]), 0, relative)

    def test_cli_dry_run_generates_prompt_bundle_and_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "bundle.md"
            record_path = Path(tmp) / "record.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "super_board_run.py"),
                    "--input",
                    str(ROOT / "examples" / "product-requirement.md"),
                    "--mode",
                    "deep_board_review",
                    "--output",
                    str(output_path),
                    "--record",
                    str(record_path),
                    "--dry-run",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            bundle = output_path.read_text(encoding="utf-8")
            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertIn("超级董事会提示包", bundle)
            self.assertEqual("deep_board_review", record["mode_id"])
            for field in ["decision_id", "created_at", "input_type", "assumptions", "evidence_packets"]:
                self.assertIn(field, record)

    def test_runner_builds_material_pack_source_links_and_review_run(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        text = "# 多文件审议\n\n目标：验证来源块进入提示包。\n\n风险：模型输出缺少证据引用。"
        material_pack = {
            "pack_id": "pack-test",
            "title": "自定义材料包",
            "files": [{"file_id": "file-001", "name": "a.md", "size": 42, "type": "markdown", "status": "read"}],
            "source_blocks": [
                {
                    "block_id": "src-001",
                    "file_id": "file-001",
                    "source_file": "a.md",
                    "text": "目标：验证来源块进入提示包。",
                }
            ],
            "warnings": [],
        }

        record = super_board_run.build_record(
            ROOT / "examples" / "product-requirement.md",
            text,
            modes["synthetic_user_panel"],
            material_pack,
        )
        bundle = super_board_run.build_prompt_bundle(
            ROOT / "examples" / "product-requirement.md",
            text,
            modes["synthetic_user_panel"],
            record,
        )
        memo = super_board_run.build_board_memo(
            ROOT / "examples" / "product-requirement.md",
            text,
            modes["synthetic_user_panel"],
            record,
        )

        self.assertEqual("synthetic_user_panel", record["mode_id"])
        self.assertEqual("自定义材料包", record["material_pack"]["title"])
        self.assertEqual("src-001", record["evidence_packets"][0]["source_block_id"])
        self.assertIn("review_run", record)
        self.assertGreaterEqual(len(record["review_run"]["stages"]), 6)
        self.assertIn("## 来源块", bundle)
        self.assertIn("src-001 · a.md", bundle)
        self.assertIn("等待模型", bundle)
        self.assertIn("# 《董事会建议书》：自定义材料包", memo)
        self.assertIn("## 证据包", memo)
        self.assertIn("未调用外部模型", memo)
        self.assertIn("src-001 · a.md", memo)

    def test_followup_script_generates_checkpoint_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            record_path = Path(tmp) / "record.json"
            output_path = Path(tmp) / "followup.md"
            record_path.write_text(
                json.dumps(
                    {
                        "decision_id": "SB-test",
                        "title": "测试决策",
                        "mode_id": "deep_board_review",
                        "decision": "Pending",
                        "assumptions": [{"assumption": "用户愿意试用"}],
                        "evidence_packets": [{"claim": "已生成本地记录"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "super_board_followup.py"),
                    "--record",
                    str(record_path),
                    "--checkpoint",
                    "30",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Super Board Follow-up Prompt", content)
            self.assertIn("30 天", content)

    def test_records_are_ignored_except_gitkeep(self) -> None:
        ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("records/*", ignore_text)
        self.assertIn("!records/.gitkeep", ignore_text)
        self.assertIn("!records/README.md", ignore_text)
        self.assertIn("calibration/events.jsonl", ignore_text)

    def test_record_export_markdown_localizes_mode_and_decision(self) -> None:
        markdown = super_board_server.render_record_markdown(
            {
                "decision_id": "SB-test",
                "title": "测试记录",
                "mode_id": "synthetic_user_panel",
                "decision": "Pending",
                "evidence_packets": [],
                "assumptions": [],
                "action_items": [],
            }
        )

        self.assertIn("用户模拟委员会", markdown)
        self.assertIn("待判断", markdown)
        self.assertNotIn("synthetic_user_panel", markdown)

    def test_custom_personas_have_full_nuwa_artifacts(self) -> None:
        custom_personas = validate_skill.parse_custom_personas(ROOT / "sources/awesome-persona-skills.yaml")
        self.assertEqual(17, len(custom_personas))
        for persona_id in custom_personas:
            artifact_root = ROOT / "nuwa_distillations" / persona_id
            for relative in validate_skill.REQUIRED_NUWA_RESEARCH_FILES:
                self.assertTrue((artifact_root / relative).is_file(), f"{persona_id}: {relative}")

    def test_replaced_functional_personas_are_not_referenced(self) -> None:
        issues = validate_skill.validate(ROOT)
        self.assertFalse(
            any("replaced functional persona" in issue.message for issue in issues),
            [issue for issue in issues if "replaced functional persona" in issue.message],
        )


if __name__ == "__main__":
    unittest.main()
