from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LOADER_PATH = ROOT / "scripts" / "ontology_loader.py"
loader_spec = importlib.util.spec_from_file_location("ontology_loader", LOADER_PATH)
ontology_loader = importlib.util.module_from_spec(loader_spec)
assert loader_spec.loader is not None
sys.modules["ontology_loader"] = ontology_loader
loader_spec.loader.exec_module(ontology_loader)

RUNNER_PATH = ROOT / "scripts" / "super_board_run.py"
runner_spec = importlib.util.spec_from_file_location("super_board_run", RUNNER_PATH)
super_board_run = importlib.util.module_from_spec(runner_spec)
assert runner_spec.loader is not None
sys.modules["super_board_run"] = super_board_run
runner_spec.loader.exec_module(super_board_run)


ASCII_NAME_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")


class PersonaDisplayNameTests(unittest.TestCase):
    def test_visible_personas_have_chinese_display_names(self) -> None:
        board = ontology_loader.load_json_or_yaml(ROOT / "boards" / "default-board.yaml")
        visible_ids = set(ontology_loader.core_persona_ids(board)) | set(ontology_loader.triggered_specialist_ids(board))
        personas = ontology_loader.load_persona_ontologies(ROOT)

        for persona_id in visible_ids:
            self.assertIn(persona_id, personas)
            display_name = str(personas[persona_id].get("display_name", ""))
            self.assertTrue(display_name.strip(), persona_id)
            self.assertFalse(ASCII_NAME_PATTERN.search(display_name), f"{persona_id}: {display_name}")

    def test_local_board_memo_uses_chinese_persona_names(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        input_path = ROOT / "tests" / "fixtures" / "ontology" / "pricing_strategy.md"
        text = input_path.read_text(encoding="utf-8")
        record = super_board_run.build_record(input_path, text, modes["deep_board_review"])
        board_memo = super_board_run.build_board_memo(input_path, text, modes["deep_board_review"], record)

        self.assertIn("本次审议席位", board_memo)
        self.assertIn("席位代表观点", board_memo)
        self.assertNotRegex(board_memo, ASCII_NAME_PATTERN)
        self.assertIn("沃伦·巴菲特", board_memo)


if __name__ == "__main__":
    unittest.main()
