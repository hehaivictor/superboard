from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SELECTOR_PATH = ROOT / "scripts" / "seat_view_selector.py"
selector_spec = importlib.util.spec_from_file_location("seat_view_selector", SELECTOR_PATH)
seat_view_selector = importlib.util.module_from_spec(selector_spec)
sys.modules["seat_view_selector"] = seat_view_selector

RUNNER_PATH = ROOT / "scripts" / "super_board_run.py"
runner_spec = importlib.util.spec_from_file_location("super_board_run", RUNNER_PATH)
super_board_run = importlib.util.module_from_spec(runner_spec)
assert runner_spec.loader is not None
sys.modules["super_board_run"] = super_board_run
runner_spec.loader.exec_module(super_board_run)


class SeatViewSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        if selector_spec.loader is None:
            self.fail("seat_view_selector module is missing")
        selector_spec.loader.exec_module(seat_view_selector)

    def test_selects_one_representative_per_standing_committee(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        input_path = ROOT / "tests" / "fixtures" / "ontology" / "pricing_strategy.md"
        text = input_path.read_text(encoding="utf-8")
        record = super_board_run.build_record(input_path, text, modes["deep_board_review"])

        selected = record["selected_seats"]
        committees = {seat["committee"] for seat in selected}

        self.assertGreaterEqual(len(selected), 7)
        self.assertLessEqual(len(selected), 10)
        self.assertEqual(set(seat_view_selector.STANDING_COMMITTEES), committees)
        for seat in selected:
            self.assertTrue(seat["display_name"])
            self.assertTrue(seat["selection_reason"])
            self.assertTrue(seat["evidence_basis"])
            self.assertTrue(seat["counter_signal"])

    def test_ai_material_triggers_altman_specialist(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        text = "# AI Agent 平台\n\n目标：构建智能体生态、模型调用、插件平台和企业 AI 工作流。"
        record = super_board_run.build_record(ROOT / "inline-input.md", text, modes["deep_board_review"])

        selected_ids = {seat["persona_id"] for seat in record["selected_seats"]}

        self.assertIn("sam-altman", selected_ids)


if __name__ == "__main__":
    unittest.main()
