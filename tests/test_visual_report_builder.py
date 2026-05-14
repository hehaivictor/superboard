from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = ROOT / "scripts" / "super_board_run.py"
runner_spec = importlib.util.spec_from_file_location("super_board_run", RUNNER_PATH)
super_board_run = importlib.util.module_from_spec(runner_spec)
assert runner_spec.loader is not None
sys.modules["super_board_run"] = super_board_run
runner_spec.loader.exec_module(super_board_run)

VISUAL_PATH = ROOT / "scripts" / "visual_report_builder.py"
visual_spec = importlib.util.spec_from_file_location("visual_report_builder", VISUAL_PATH)
visual_report_builder = importlib.util.module_from_spec(visual_spec)
assert visual_spec.loader is not None
sys.modules["visual_report_builder"] = visual_report_builder
visual_spec.loader.exec_module(visual_report_builder)

SERVER_PATH = ROOT / "web" / "server.py"
server_spec = importlib.util.spec_from_file_location("super_board_server", SERVER_PATH)
super_board_server = importlib.util.module_from_spec(server_spec)
assert server_spec.loader is not None
server_spec.loader.exec_module(super_board_server)


class VisualReportBuilderTests(unittest.TestCase):
    def build_pricing_payload(self) -> tuple[dict[str, object], str]:
        modes = super_board_run.load_modes(ROOT)
        input_path = ROOT / "tests" / "fixtures" / "ontology" / "pricing_strategy.md"
        text = input_path.read_text(encoding="utf-8")
        record = super_board_run.build_record(input_path, text, modes["deep_board_review"])
        board_memo = super_board_run.build_board_memo(input_path, text, modes["deep_board_review"], record)
        record["board_memo"] = board_memo
        return record, board_memo

    def test_visual_report_schema_is_registered(self) -> None:
        schema = json.loads((ROOT / "schemas" / "visual_report.schema.json").read_text(encoding="utf-8"))

        for field in [
            "hero",
            "seat_view_cards",
            "decision_cards",
            "committee_cards",
            "ontology_cards",
            "evidence_cards",
            "insight_cards",
            "roadmap",
            "appendix_sections",
        ]:
            self.assertIn(field, schema["required"])
            self.assertIn(field, schema["properties"])

    def test_build_visual_report_reuses_existing_record_content(self) -> None:
        record, board_memo = self.build_pricing_payload()

        report = visual_report_builder.build_visual_report(record, board_memo)

        self.assertEqual(record["decision_id"], report["hero"]["decision_id"])
        self.assertGreaterEqual(len(report["seat_view_cards"]), 7)
        self.assertGreaterEqual(len(report["decision_cards"]), 4)
        self.assertGreaterEqual(len(report["committee_cards"]), 7)
        self.assertGreaterEqual(len(report["ontology_cards"]), 4)
        self.assertGreaterEqual(len(report["evidence_cards"]), 1)
        self.assertGreaterEqual(len(report["insight_cards"]), 3)
        self.assertEqual([30, 60, 90], [item["day"] for item in report["roadmap"]])

    def test_ai_insights_are_traceable_and_do_not_claim_external_facts(self) -> None:
        record, board_memo = self.build_pricing_payload()

        report = visual_report_builder.build_visual_report(record, board_memo)

        for insight in report["insight_cards"]:
            self.assertIn("source_fields", insight)
            self.assertGreaterEqual(len(insight["source_fields"]), 1)
            self.assertNotIn("外部调研显示", insight["body"])
            self.assertNotIn("行业数据显示", insight["body"])

    def test_visual_markdown_contains_card_sections(self) -> None:
        record, board_memo = self.build_pricing_payload()
        report = visual_report_builder.build_visual_report(record, board_memo)

        markdown = visual_report_builder.render_visual_report_markdown(report)

        self.assertIn("# 视觉版董事会建议书", markdown)
        self.assertIn("## 本次参与席位", markdown)
        self.assertIn("## 决策摘要卡片", markdown)
        self.assertIn("## AI 洞察", markdown)
        self.assertIn("## 本体规则卡片", markdown)

    def test_web_preview_payload_exposes_visual_report(self) -> None:
        payload = super_board_server.build_preview_payload(
            "# 定价策略\n\n目标：验证企业版定价、竞品价格、客户支付意愿、毛利、获客成本和销售激励。",
            "deep_board_review",
            None,
        )

        self.assertIn("visual_report", payload)
        self.assertIn("visual_report_markdown", payload)
        self.assertIn("AI 洞察", payload["visual_report_markdown"])


if __name__ == "__main__":
    unittest.main()
