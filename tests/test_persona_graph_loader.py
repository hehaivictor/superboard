from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LOADER_PATH = ROOT / "scripts" / "persona_graph_loader.py"
loader_spec = importlib.util.spec_from_file_location("persona_graph_loader", LOADER_PATH)
persona_graph_loader = importlib.util.module_from_spec(loader_spec)
assert loader_spec.loader is not None
sys.modules["persona_graph_loader"] = persona_graph_loader
loader_spec.loader.exec_module(persona_graph_loader)

VALIDATOR_PATH = ROOT / "scripts" / "validate_persona_graph.py"
validator_spec = importlib.util.spec_from_file_location("validate_persona_graph", VALIDATOR_PATH)
validate_persona_graph = importlib.util.module_from_spec(validator_spec)
assert validator_spec.loader is not None
sys.modules["validate_persona_graph"] = validate_persona_graph
validator_spec.loader.exec_module(validate_persona_graph)


class PersonaGraphLoaderTests(unittest.TestCase):
    def test_loads_all_persona_graphs(self) -> None:
        graphs = persona_graph_loader.load_persona_graphs(ROOT)

        self.assertEqual(37, len(graphs))
        for persona_id, graph in graphs.items():
            self.assertEqual(persona_id, graph["person"]["persona_id"])
            self.assertTrue(str(graph["person"]["display_name"]).strip())
            self.assertFalse(any(ch.isascii() and ch.isalpha() for ch in graph["person"]["display_name"]))

    def test_default_graphs_pass_validation(self) -> None:
        issues = validate_persona_graph.validate(ROOT)

        self.assertEqual([], issues)

    def test_each_graph_has_minimum_decision_depth(self) -> None:
        graphs = persona_graph_loader.load_persona_graphs(ROOT)

        for persona_id, graph in graphs.items():
            self.assertGreaterEqual(len(graph["claims"]), 5, persona_id)
            self.assertGreaterEqual(len(graph["mental_models"]) + len(graph["heuristics"]), 5, persona_id)
            self.assertGreaterEqual(len(graph["decision_rules"]), 5, persona_id)
            self.assertGreaterEqual(len(graph["historical_decisions"]), 3, persona_id)
            self.assertGreaterEqual(len(graph["episodes"]), 3, persona_id)
            self.assertGreaterEqual(len(graph["boundaries"]), 3, persona_id)
            self.assertGreaterEqual(len(graph["eval_cases"]), 3, persona_id)
            self.assertGreaterEqual(len(graph["relations"]), 5, persona_id)

    def test_relations_reference_existing_objects(self) -> None:
        graphs = persona_graph_loader.load_persona_graphs(ROOT)

        for persona_id, graph in graphs.items():
            object_ids = persona_graph_loader.graph_object_ids(graph)
            for relation in graph["relations"]:
                self.assertIn(relation["subject"], object_ids, persona_id)
                self.assertIn(relation["object"], object_ids, persona_id)


if __name__ == "__main__":
    unittest.main()
