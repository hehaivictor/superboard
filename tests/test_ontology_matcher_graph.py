from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MATCHER_PATH = ROOT / "scripts" / "ontology_matcher.py"
matcher_spec = importlib.util.spec_from_file_location("ontology_matcher", MATCHER_PATH)
ontology_matcher = importlib.util.module_from_spec(matcher_spec)
assert matcher_spec.loader is not None
sys.modules["ontology_matcher"] = ontology_matcher
matcher_spec.loader.exec_module(ontology_matcher)

RUNNER_PATH = ROOT / "scripts" / "super_board_run.py"
runner_spec = importlib.util.spec_from_file_location("super_board_run", RUNNER_PATH)
super_board_run = importlib.util.module_from_spec(runner_spec)
assert runner_spec.loader is not None
sys.modules["super_board_run"] = super_board_run
runner_spec.loader.exec_module(super_board_run)


class OntologyMatcherGraphTests(unittest.TestCase):
    def test_rule_hits_include_persona_graph_references(self) -> None:
        text = (ROOT / "tests/fixtures/ontology/pricing_strategy.md").read_text(encoding="utf-8")

        trace = ontology_matcher.match_ontology_trace(ROOT, text)

        self.assertGreaterEqual(len(trace), 4)
        for hit in trace:
            for field in [
                "claim_id",
                "model_id",
                "source_ids",
                "boundary_id",
                "counter_test_id",
                "relation_ids",
                "governance_checks",
            ]:
                self.assertIn(field, hit)
                self.assertTrue(hit[field], field)

    def test_runner_record_contains_persona_graph_refs(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        input_path = ROOT / "tests/fixtures/ontology/pricing_strategy.md"
        text = input_path.read_text(encoding="utf-8")

        record = super_board_run.build_record(input_path, text, modes["deep_board_review"])

        self.assertIn("persona_graph_refs", record)
        self.assertIn("model_comparisons", record)
        self.assertIn("action_audit", record)
        self.assertIn("governance_checks", record)
        self.assertGreaterEqual(len(record["persona_graph_refs"]), 7)

    def test_prompt_bundle_contains_bounded_persona_graph_fragments(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        input_path = ROOT / "tests/fixtures/ontology/pricing_strategy.md"
        text = input_path.read_text(encoding="utf-8")
        record = super_board_run.build_record(input_path, text, modes["deep_board_review"])

        prompt = super_board_run.build_prompt_bundle(input_path, text, modes["deep_board_review"], record)

        self.assertIn("人物本体图谱片段", prompt)
        self.assertIn("身份边界", prompt)
        self.assertIn("claim_id", prompt)
        self.assertNotIn("I am Warren Buffett", prompt)


if __name__ == "__main__":
    unittest.main()
