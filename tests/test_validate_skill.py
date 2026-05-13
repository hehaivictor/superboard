from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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

AUDIT_PATH = ROOT / "scripts" / "audit_board_memo.py"
audit_spec = importlib.util.spec_from_file_location("audit_board_memo", AUDIT_PATH)
audit_board_memo = importlib.util.module_from_spec(audit_spec)
assert audit_spec.loader is not None
sys.modules["audit_board_memo"] = audit_board_memo
audit_spec.loader.exec_module(audit_board_memo)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_persona(name: str = "Example") -> str:
    sections = [f"# {name}"]
    for field in validate_skill.REQUIRED_PERSONA_FIELDS:
        sections.append(f"## {field}\n\n- content")
    return "\n\n".join(sections) + "\n"


class FakeStreamingResponse:
    def __init__(self, lines: list[str]) -> None:
        self._lines = [line.encode("utf-8") for line in lines]
        self._index = 0

    def readline(self) -> bytes:
        if self._index >= len(self._lines):
            return b""
        line = self._lines[self._index]
        self._index += 1
        return line


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
                self.assertTrue(validate_skill.has_board_memo_section(text, section), f"{relative}: {section}")
            for marker in ["反证", "失败路径", "决策条件", "30 / 60 / 90"]:
                self.assertIn(marker, text, relative)
            self.assertGreaterEqual(text.count("```mermaid"), validate_skill.REQUIRED_MERMAID_BLOCKS, relative)

    def test_board_template_contains_required_mermaid_blocks(self) -> None:
        text = (ROOT / "templates/board-memo.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("```mermaid"), validate_skill.REQUIRED_MERMAID_BLOCKS)
        for section in ["附录 A：证据包", "附录 B：待验证假设", "附录 D：决策记录"]:
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
        self.assertIn("文件数量：1", bundle)
        self.assertIn("来源块数量：1", bundle)
        self.assertIn("来源块是材料文件拆分后的可引用文本片段，不代表不同文件", bundle)
        self.assertIn("src-001 · a.md", bundle)
        self.assertIn("等待模型", bundle)
        self.assertIn("# 《董事会建议书》：自定义材料包", memo)
        self.assertIn("1 个材料文件，共拆分为 1 个可引用来源块", memo)
        self.assertIn("来源块是同一文件的文本片段，不代表不同文件", memo)
        self.assertIn("## 附录 A：证据包", memo)
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
        self.assertIn(".super-board-model.json", ignore_text)

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

    def test_model_config_reports_missing_key_without_exposing_secret(self) -> None:
        with patch.dict("os.environ", {}, clear=True), patch.object(super_board_server, "MODEL_CONFIG_PATH", ROOT / "missing-model-config.json"):
            config = super_board_server.model_config()
            public = super_board_server.public_model_config()

        self.assertFalse(config["configured"])
        self.assertIn("SUPER_BOARD_LLM_API_KEY 或 OPENAI_API_KEY", config["missing"])
        self.assertNotIn("api_key", public)

    def test_model_generation_payload_attaches_model_memo_metadata(self) -> None:
        payload = super_board_server.build_preview_payload(
            "# 模型生成测试\n\n目标：确认模型生成覆盖本地草案。",
            "deep_board_review",
            None,
        )
        attached = super_board_server.attach_model_memo(
            payload,
            "# 《董事会建议书》：模型生成测试\n\n模型正文",
            {
                "model": "test-model",
                "base_url": "http://127.0.0.1:9999/v1",
            },
        )

        self.assertEqual("model", attached["generated_by"])
        self.assertEqual("# 《董事会建议书》：模型生成测试\n\n模型正文", attached["board_memo"])
        self.assertEqual("test-model", attached["generation"]["model"])
        self.assertEqual(attached["board_memo"], attached["record"]["board_memo"])

    def test_preview_payload_exposes_ontology_rule_hits(self) -> None:
        payload = super_board_server.build_preview_payload(
            "# 定价策略\n\n目标：验证企业版定价、竞品价格、客户支付意愿、毛利、获客成本和销售激励。",
            "deep_board_review",
            None,
        )

        self.assertIn("ontology_rule_hits", payload)
        self.assertIn("ontology_trace", payload)
        self.assertIn("committee_rule_matrix", payload)
        self.assertGreaterEqual(len(payload["ontology_rule_hits"]), 1)

    def test_preview_payload_exposes_visual_report(self) -> None:
        payload = super_board_server.build_preview_payload(
            "# 定价策略\n\n目标：验证企业版定价、竞品价格、客户支付意愿、毛利、获客成本和销售激励。",
            "deep_board_review",
            None,
        )

        self.assertIn("visual_report", payload)
        self.assertIn("visual_report_markdown", payload)
        self.assertIn("视觉版董事会建议书", payload["visual_report_markdown"])

    def test_streaming_completion_reports_length_finish_reason(self) -> None:
        response = FakeStreamingResponse(
            [
                'data: {"choices":[{"delta":{"content":"# 《董事会建议书》"},"finish_reason":null}]}\n',
                'data: {"choices":[{"delta":{"content":"\\n\\n## 输入类型与审议范围"},"finish_reason":null}]}\n',
                'data: {"choices":[{"delta":{},"finish_reason":"length"}]}\n',
                "data: [DONE]\n",
            ]
        )

        text, finish_reason = super_board_server.read_streaming_chat_completion(response)

        self.assertIn("输入类型与审议范围", text)
        self.assertEqual("length", finish_reason)

    def test_model_generation_rejects_incomplete_board_memo(self) -> None:
        incomplete = "# 《董事会建议书》\n\n## 输入类型与审议范围\n\n只有报告开头。"
        complete = "\n\n".join(
            [
                "# 《董事会建议书》：完整报告",
                "## 一页结论\n\n- 当前建议：推进。",
                "## 输入材料与审议范围\n\n材料已拆解为来源块。",
                "## Go / No-Go / Pivot 建议\n\n- 推进：证据充分。",
                "## 核心判断依据\n\n- 判断：证据链完整。",
                "## 五个委员会意见\n\n- 商业委员会：支持。\n- 创业委员会：支持。\n- 投资委员会：支持。\n- 咨询委员会：支持。\n- 产品委员会：支持。",
                "## 跨委员会共识与关键分歧\n\n**强共识**\n\n- 共识：先验证付费意愿。\n\n**关键分歧**\n\n- 分歧：进入节奏。",
                "## 最大机会、最大风险与反证路径\n\n- 最大机会：获得高价值客户。\n- 最大风险：付费意愿不足。\n- 最强反证：客户拒绝为诊断付费。\n- 失败路径 1：需求不存在。",
                "## 30 / 60 / 90 天行动计划\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 附录 A：证据包\n\n- E1：来源块。",
                "## 附录 B：待验证假设\n\n- H1：客户愿意付费。",
                "## 附录 C：Persona 关键意见摘要\n\n- Persona：观点。",
                "## 附录 D：决策记录\n\n- 决策编号：SB-test。",
            ]
        )

        self.assertFalse(super_board_server.board_memo_is_complete(incomplete))
        self.assertTrue(super_board_server.board_memo_is_complete(complete))

    def test_board_memo_with_empty_core_sections_is_not_complete(self) -> None:
        content_missing = "\n\n".join(
            [
                "# 《董事会建议书》：缺内容报告",
                "## 一页结论\n\n- 当前建议：推进。",
                "## 输入材料与审议范围\n\n材料已拆解。",
                "## Go / No-Go / Pivot 建议\n\n- 推进：满足条件。",
                "## 核心判断依据\n\n- 判断：需要证据。",
                "## 五个委员会意见\n\n- 商业委员会：支持。",
                "## 跨委员会共识与关键分歧",
                "## 最大机会、最大风险与反证路径\n\n### 3. 反证路径\n\n- 只输出了反证路径。",
                "## 30 / 60 / 90 天行动计划\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 附录 A：证据包\n\n- E1：来源块。",
                "## 附录 B：待验证假设\n\n- H1：客户愿意付费。",
                "## 附录 C：Persona 关键意见摘要\n\n- Persona：观点。",
                "## 附录 D：决策记录\n\n- 决策编号：SB-test。",
            ]
        )

        self.assertEqual([], super_board_server.board_memo_missing_markers(content_missing))
        self.assertFalse(super_board_server.board_memo_is_complete(content_missing))
        issues = super_board_server.board_memo_quality_issues(content_missing)
        self.assertTrue(any("跨委员会共识与关键分歧" in issue for issue in issues))
        self.assertTrue(any("最大机会、最大风险与反证路径" in issue for issue in issues))

    def test_board_memo_with_dangling_subsection_is_not_complete(self) -> None:
        dangling = "\n\n".join(
            [
                "# 《董事会建议书》：残句报告",
                "## 一页结论\n\n- 当前建议：推进。",
                "## 输入材料与审议范围\n\n材料已拆解。",
                "## Go / No-Go / Pivot 建议\n\n- 推进：满足条件。",
                "## 核心判断依据\n\n- 判断：需要证据。",
                "## 五个委员会意见\n\n- 商业委员会：支持。\n- 创业委员会：支持。\n- 投资委员会：支持。\n- 咨询委员会：支持。\n- 产品委员会：支持。",
                (
                    "## 跨委员会共识与关键分歧\n\n"
                    "### 1. 强共识\n\n- 共识：先验证付费意愿。\n\n"
                    "### 2. 关键分歧\n\n- 分歧：进入节奏。\n\n"
                    "### 3. 分歧解决原则\n\n为"
                ),
                "## 最大机会、最大风险与反证路径\n\n- 最大机会：获得高价值客户。\n- 最大风险：付费意愿不足。\n- 最强反证：客户拒绝为诊断付费。\n- 失败路径 1：需求不存在。",
                "## 30 / 60 / 90 天行动计划\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 附录 A：证据包\n\n- E1：来源块。",
                "## 附录 B：待验证假设\n\n- H1：客户愿意付费。",
                "## 附录 C：Persona 关键意见摘要\n\n- Persona：观点。",
                "## 附录 D：决策记录\n\n- 决策编号：SB-test。",
            ]
        )

        self.assertEqual([], super_board_server.board_memo_missing_markers(dangling))
        self.assertFalse(super_board_server.board_memo_is_complete(dangling))
        issues = super_board_server.board_memo_quality_issues(dangling)
        self.assertTrue(any("分歧解决原则" in issue for issue in issues), issues)

    def test_call_model_rejects_content_incomplete_board_memo(self) -> None:
        content_missing = "\n\n".join(
            [
                "# 《董事会建议书》：缺内容报告",
                "## 一页结论\n\n- 当前建议：推进。",
                "## 输入材料与审议范围\n\n材料已拆解。",
                "## Go / No-Go / Pivot 建议\n\n- 推进：满足条件。",
                "## 核心判断依据\n\n- 判断：需要证据。",
                "## 五个委员会意见\n\n- 商业委员会：支持。",
                "## 跨委员会共识与关键分歧",
                "## 最大机会、最大风险与反证路径\n\n### 3. 反证路径\n\n- 只输出了反证路径。",
                "## 30 / 60 / 90 天行动计划\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 附录 A：证据包\n\n- E1：来源块。",
                "## 附录 B：待验证假设\n\n- H1：客户愿意付费。",
                "## 附录 C：Persona 关键意见摘要\n\n- Persona：观点。",
                "## 附录 D：决策记录\n\n- 决策编号：SB-test。",
            ]
        )

        with patch.object(super_board_server, "call_streaming_chat_completion", return_value=(content_missing, "stop")):
            with self.assertRaises(RuntimeError) as context:
                super_board_server.call_model(
                    "prompt",
                    {
                        "model": "test-model",
                        "base_url": "http://127.0.0.1:9999/v1",
                        "temperature": 0,
                        "max_tokens": 1000,
                        "timeout": 1,
                        "continuations": 0,
                    },
                )

        self.assertIn("内容问题", str(context.exception))
        self.assertIn("跨委员会共识与关键分歧", str(context.exception))

    def test_merge_model_parts_replaces_empty_sections_with_completed_continuation(self) -> None:
        first_part = "\n\n".join(
            [
                "# 《董事会建议书》：续写合并测试",
                "## 跨委员会共识与关键分歧",
                "## 最大机会、最大风险与反证路径\n\n### 3. 反证路径\n\n- 只有反证路径。",
            ]
        )
        continuation = "\n\n".join(
            [
                "## 跨委员会共识与关键分歧\n\n**强共识**\n\n- 共识：先验证付费意愿。\n\n**关键分歧**\n\n- 分歧：是否先服务化交付。",
                "## 最大机会、最大风险与反证路径\n\n- 最大机会：沉淀可复用方案。\n- 最大风险：客户不愿付费。\n- 最强反证：客户只愿免费咨询。\n- 失败路径 1：无法复用交付。",
            ]
        )

        merged = super_board_server.merge_model_parts([first_part, continuation])

        self.assertIn("共识：先验证付费意愿", merged)
        self.assertIn("最大机会：沉淀可复用方案", merged)
        self.assertNotIn("只有反证路径", merged)

    def test_numbered_chinese_headings_count_as_required_sections(self) -> None:
        numbered = "\n\n".join(
            [
                "# 《董事会建议书》",
                "## 一、输入材料与审议范围\n\n材料范围完整。",
                "## 二、一句话结论\n\n- 当前建议：推进。",
                "## 三、Go / No-Go / Pivot 建议\n\n- 推进：满足证据条件。",
                "## 四、核心判断依据\n\n- 判断：证据链可验证。",
                "## 五、五个委员会意见\n\n- 商业委员会：支持。\n- 创业委员会：支持。\n- 投资委员会：支持。\n- 咨询委员会：支持。\n- 产品委员会：支持。",
                "## 六、跨委员会共识与关键分歧\n\n**强共识**\n\n- 共识：优先验证客户付费。\n\n**关键分歧**\n\n- 分歧：先诊断还是先服务包。",
                "## 七、最大机会、最大风险与反证路径\n\n- 最大机会：沉淀可复用交付。\n- 最大风险：客户不愿付费。\n- 最强反证：客户只接受免费咨询。\n- 失败路径 1：服务无法复用。",
                "## 八、30 / 60 / 90 天行动计划\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 九、附录 A：证据包\n\n- E1：来源块。",
                "## 十、附录 B：待验证假设\n\n- H1：客户愿意付费。",
                "## 十一、附录 C：Persona 关键意见摘要\n\n- Persona：观点。",
                "## 十二、附录 D：决策记录\n\n- 决策编号：SB-test。",
            ]
        )

        self.assertEqual([], super_board_server.board_memo_missing_markers(numbered))
        self.assertTrue(super_board_server.board_memo_is_complete(numbered))

    def test_duplicate_restart_after_decision_record_is_detected(self) -> None:
        duplicated = "\n\n".join(
            [
                "# 《董事会建议书》",
                "## 十三、最终董事会建议",
                "## 十四、决策记录条目",
                "| 字段 | 内容 |",
                "## 十五、人物附录：委员会审议角色画像",
                "## 输入类型与审议范围",
                "## 一句话结论",
            ]
        )

        self.assertTrue(super_board_server.board_memo_has_duplicate_restart(duplicated))

    def test_merge_model_parts_drops_duplicate_restart_sections(self) -> None:
        first_part = "\n\n".join(
            [
                "# 《董事会建议书》",
                "## 输入类型与审议范围",
                "原始范围",
                "## 一句话结论",
                "原始结论",
                "## 十四、决策记录条目",
                "原始记录",
            ]
        )
        continuation = "\n\n".join(
            [
                "## 输入类型与审议范围",
                "重复范围",
                "## 核心判断",
                "新增判断",
            ]
        )

        merged = super_board_server.merge_model_parts([first_part, continuation])

        self.assertIn("原始范围", merged)
        self.assertNotIn("重复范围", merged)
        self.assertIn("新增判断", merged)

    def test_audit_script_flags_exported_duplicate_restart(self) -> None:
        duplicated = "\n\n".join(
            [
                "# 《董事会建议书》",
                "## 十三、最终董事会建议",
                "## 十四、决策记录条目",
                "记录",
                "## 十五、人物附录：委员会审议角色画像",
                "附录",
                "## 输入类型与审议范围",
                "重复开始",
            ]
        )

        issues = audit_board_memo.audit_text(duplicated)

        self.assertTrue(any(issue["code"] == "duplicate_restart" for issue in issues))

    def test_h1_numbered_sections_and_h2_template_restart_are_duplicate(self) -> None:
        duplicated = "\n\n".join(
            [
                "# 《董事会建议书》",
                "# 1. 输入材料结构化拆解",
                "第一套范围。",
                "# 3. 证据包",
                "第一套证据。",
                "# 4. 假设账本",
                "第一套假设。",
                "# 10. 决策记录条目",
                "第一套记录。",
                "## 输入类型与审议范围",
                "第二套范围。",
                "## 证据包",
                "第二套证据。",
                "## 假设账本",
                "第二套假设。",
            ]
        )

        issues = audit_board_memo.audit_text(duplicated)

        self.assertTrue(super_board_server.board_memo_has_duplicate_restart(duplicated))
        self.assertTrue(any(issue["code"] == "duplicate_restart" for issue in issues))

    def test_merge_model_parts_drops_h1_h2_duplicate_restart_sections(self) -> None:
        first_part = "\n\n".join(
            [
                "# 《董事会建议书》",
                "# 1. 输入材料结构化拆解",
                "原始范围",
                "# 3. 证据包",
                "原始证据",
                "# 10. 决策记录条目",
                "原始记录",
            ]
        )
        continuation = "\n\n".join(
            [
                "## 输入类型与审议范围",
                "重复范围",
                "## 证据包",
                "重复证据",
                "## 核心判断",
                "新增判断",
            ]
        )

        merged = super_board_server.merge_model_parts([first_part, continuation])

        self.assertIn("原始范围", merged)
        self.assertIn("原始证据", merged)
        self.assertNotIn("重复范围", merged)
        self.assertNotIn("重复证据", merged)
        self.assertIn("新增判断", merged)

    def test_call_model_continues_when_stream_finishes_by_length(self) -> None:
        first_part = "# 《董事会建议书》\n\n## 输入类型与审议范围\n\n开头内容。"
        second_part = "\n\n".join(
            [
                "## 一句话结论\n\n- 当前建议：推进。",
                "## Go / No-Go / Pivot 建议\n\n- 推进：满足证据条件。",
                "## 核心判断\n\n- 判断：证据链可验证。",
                "## 各委员会结论\n\n- 商业委员会：支持。\n- 创业委员会：支持。\n- 投资委员会：支持。\n- 咨询委员会：支持。\n- 产品委员会：支持。",
                "## 跨委员会共识\n\n**强共识**\n\n- 共识：先验证付费意愿。\n\n**关键分歧**\n\n- 分歧：先诊断还是先服务包。",
                "## 最大机会\n\n- 最大机会：沉淀可复用方案。\n- 最大风险：客户不愿付费。\n- 最强反证：客户只愿免费咨询。\n- 失败路径 1：无法复用交付。",
                "## 建议行动清单\n\n- 30 天：验证。\n- 60 天：复盘。\n- 90 天：决策。",
                "## 证据包\n\n- E1：来源块。",
                "## 假设账本\n\n- H1：客户愿意付费。",
                "## 附录：各 Persona 关键意见摘要\n\n- Persona：观点。",
                "## 决策记录条目\n\n- 决策编号：SB-test。",
            ]
        )

        with patch.object(
            super_board_server,
            "call_streaming_chat_completion",
            side_effect=[(first_part, "length"), (second_part, "stop")],
        ) as fake_call:
            memo = super_board_server.call_model(
                "prompt",
                {
                    "model": "test-model",
                    "base_url": "http://127.0.0.1:9999/v1",
                    "api_key": "test-key",
                    "temperature": 0.2,
                    "max_tokens": 6000,
                    "timeout": 1,
                    "continuations": 1,
                },
            )

        self.assertIn("## 决策记录条目", memo)
        self.assertEqual(2, fake_call.call_count)

    def test_custom_personas_have_full_nuwa_artifacts(self) -> None:
        custom_personas = validate_skill.parse_custom_personas(ROOT / "sources/awesome-persona-skills.yaml")
        self.assertEqual(21, len(custom_personas))
        for persona_id in ["peter-drucker", "rita-mcgrath", "richard-rumelt", "roger-martin"]:
            self.assertIn(persona_id, custom_personas)
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
