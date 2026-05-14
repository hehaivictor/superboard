from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIONS_PATH = ROOT / "scripts" / "persona_actions.py"
actions_spec = importlib.util.spec_from_file_location("persona_actions", ACTIONS_PATH)
persona_actions = importlib.util.module_from_spec(actions_spec)
assert actions_spec.loader is not None
sys.modules["persona_actions"] = persona_actions
actions_spec.loader.exec_module(persona_actions)

LOADER_PATH = ROOT / "scripts" / "persona_graph_loader.py"
loader_spec = importlib.util.spec_from_file_location("persona_graph_loader", LOADER_PATH)
persona_graph_loader = importlib.util.module_from_spec(loader_spec)
assert loader_spec.loader is not None
sys.modules["persona_graph_loader"] = persona_graph_loader
loader_spec.loader.exec_module(persona_graph_loader)


class PersonaActionsTests(unittest.TestCase):
    def test_explain_selection_returns_traceable_action_result(self) -> None:
        graph = persona_graph_loader.load_persona_graphs(ROOT)["peter-thiel"]

        result = persona_actions.explain_selection(graph, ["非共识", "垄断"])

        self.assertEqual("ExplainSelection", result["action"])
        self.assertEqual("peter-thiel", result["persona_id"])
        self.assertTrue(result["claim_id"])
        self.assertTrue(result["model_id"])
        self.assertTrue(result["source_ids"])
        self.assertTrue(result["boundary_id"])
        self.assertTrue(result["counter_test_id"])

    def test_generate_counter_test_uses_graph_boundary(self) -> None:
        graph = persona_graph_loader.load_persona_graphs(ROOT)["warren-buffett"]

        result = persona_actions.generate_counter_test(graph, "定价与客户支付意愿")

        self.assertEqual("GenerateCounterTest", result["action"])
        self.assertIn("反证", result["body"])
        self.assertTrue(result["counter_test_id"])


if __name__ == "__main__":
    unittest.main()
