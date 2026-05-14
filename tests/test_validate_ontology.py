from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

VALIDATOR_PATH = ROOT / "scripts" / "validate_ontology.py"
validator_spec = importlib.util.spec_from_file_location("validate_ontology", VALIDATOR_PATH)
validate_ontology = importlib.util.module_from_spec(validator_spec)
assert validator_spec.loader is not None
sys.modules["validate_ontology"] = validate_ontology
validator_spec.loader.exec_module(validate_ontology)

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


class OntologyValidationTests(unittest.TestCase):
    def test_default_ontology_passes(self) -> None:
        issues = validate_ontology.validate(ROOT)
        self.assertEqual([], issues)

    def test_core_board_has_exactly_twenty_one_core_personas(self) -> None:
        board = validate_ontology.load_json_or_yaml(ROOT / "boards" / "default-board.yaml")
        core_ids = validate_ontology.core_persona_ids(board)

        self.assertEqual(validate_ontology.EXPECTED_CORE_PERSONA_IDS, core_ids)

    def test_each_core_persona_has_required_rule_depth(self) -> None:
        personas = validate_ontology.load_persona_ontologies(ROOT)

        for persona_id in validate_ontology.EXPECTED_CORE_PERSONA_IDS:
            persona = personas[persona_id]
            self.assertEqual("core", persona["ontology_level"], persona_id)
            self.assertTrue(str(persona["display_name"]).strip(), persona_id)
            self.assertTrue(str(persona["english_name"]).strip(), persona_id)
            self.assertIn("activation", persona, persona_id)
            self.assertIn("representative_viewpoints", persona, persona_id)
            self.assertIn("evidence_thresholds", persona, persona_id)
            self.assertIn("counter_tests", persona, persona_id)
            self.assertIn("misuse_guardrails", persona, persona_id)
            self.assertGreaterEqual(len(persona["concepts"]), 5, persona_id)
            self.assertGreaterEqual(len(persona["decision_rules"]), 5, persona_id)
            for rule in persona["decision_rules"]:
                self.assertGreaterEqual(len(rule["evidence_required"]), 1, rule["rule_id"])
                self.assertGreaterEqual(len(rule["counter_tests"]), 1, rule["rule_id"])
                self.assertGreaterEqual(len(rule["confidence_boundary"]), 1, rule["rule_id"])

    def test_triggered_specialists_are_not_core_voters(self) -> None:
        board = validate_ontology.load_json_or_yaml(ROOT / "boards" / "default-board.yaml")
        core_ids = set(validate_ontology.core_persona_ids(board))
        specialist_ids = set(validate_ontology.triggered_specialist_ids(board))
        archive_ids = set(validate_ontology.distilled_archive_ids(board))

        self.assertTrue({"sam-altman", "naval-ravikant", "elon-musk", "mao-zedong", "david-ogilvy"}.issubset(specialist_ids))
        self.assertFalse(core_ids & specialist_ids)
        self.assertFalse(core_ids & archive_ids)

    def test_invalid_rule_without_counter_test_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ontology/personas").mkdir(parents=True)
            (root / "boards").mkdir(parents=True)
            (root / "boards/default-board.yaml").write_text(
                json.dumps(
                    {
                        "core_board": {"business": ["bad-persona"]},
                        "triggered_specialists": {},
                        "distilled_archive": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "ontology/personas/bad-persona.yaml").write_text(
                json.dumps(
                    {
                        "persona_id": "bad-persona",
                        "name": "Bad Persona",
                        "committee": "business",
                        "ontology_level": "core",
                        "source_quality": "high",
                        "version": 1,
                        "concepts": ["a", "b", "c", "d", "e"],
                        "decision_rules": [
                            {
                                "rule_id": "bad_rule",
                                "description": "missing counter test",
                                "triggers": ["pricing"],
                                "positive_signals": ["signal"],
                                "red_flags": ["risk"],
                                "evidence_required": ["evidence"],
                                "counter_tests": [],
                                "confidence_boundary": ["boundary"],
                            }
                        ],
                        "failure_modes": ["failure"],
                        "confidence_boundary": ["boundary"],
                        "source_map": [{"source": "x", "type": "book"}],
                        "case_map": [{"case": "x", "lesson": "y"}],
                        "not_for": ["z"],
                        "calibration_notes": ["none"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            issues = validate_ontology.validate(root)

        self.assertTrue(any("counter_tests" in issue.message for issue in issues))

    def test_pricing_fixture_hits_expected_core_rules(self) -> None:
        text = (ROOT / "tests/fixtures/ontology/pricing_strategy.md").read_text(encoding="utf-8")
        trace = ontology_matcher.match_ontology_trace(ROOT, text)
        hit_ids = {(hit["persona_id"], hit["rule_id"]) for hit in trace}

        self.assertIn(("warren-buffett", "buffett_moat_cashflow_quality"), hit_ids)
        self.assertIn(("michael-porter", "porter_competitive_positioning"), hit_ids)
        self.assertIn(("sun-tzu", "sun_tzu_advantage_positioning"), hit_ids)
        self.assertIn(("charlie-munger", "munger_incentive_misalignment"), hit_ids)
        self.assertNotIn(("sam-altman", "altman_ai_scaling"), hit_ids)

    def test_runner_record_contains_ontology_rule_hits(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        text = (ROOT / "tests/fixtures/ontology/pricing_strategy.md").read_text(encoding="utf-8")
        record = super_board_run.build_record(
            ROOT / "tests/fixtures/ontology/pricing_strategy.md",
            text,
            modes["deep_board_review"],
        )

        self.assertIn("ontology_trace", record)
        self.assertIn("ontology_rule_hits", record)
        self.assertIn("selected_seats", record)
        self.assertIn("seat_viewpoints", record)
        self.assertIn("seat_selection_trace", record)
        self.assertGreaterEqual(len(record["ontology_rule_hits"]), 4)
        self.assertGreaterEqual(len(record["selected_seats"]), 7)

    def test_decision_record_schema_declares_ontology_fields(self) -> None:
        schema = json.loads((ROOT / "schemas" / "decision_record.schema.json").read_text(encoding="utf-8"))

        for field in ["ontology_trace", "ontology_rule_hits", "committee_rule_matrix", "triggered_specialists", "selected_seats", "seat_viewpoints", "seat_selection_trace"]:
            self.assertIn(field, schema["required"])
            self.assertIn(field, schema["properties"])

    def test_followup_prompt_includes_ontology_rule_hits(self) -> None:
        modes = super_board_run.load_modes(ROOT)
        text = (ROOT / "tests/fixtures/ontology/pricing_strategy.md").read_text(encoding="utf-8")
        record = super_board_run.build_record(
            ROOT / "tests/fixtures/ontology/pricing_strategy.md",
            text,
            modes["deep_board_review"],
        )

        followup_path = ROOT / "scripts" / "super_board_followup.py"
        spec = importlib.util.spec_from_file_location("super_board_followup", followup_path)
        followup = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(followup)
        content = followup.render_followup(record, 30)

        self.assertIn("本体规则命中", content)
        self.assertIn("buffett_moat_cashflow_quality", content)
        self.assertIn("反证", content)


if __name__ == "__main__":
    unittest.main()
