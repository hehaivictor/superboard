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


class PersonaGraphGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graphs = persona_graph_loader.load_persona_graphs(ROOT)

    def test_high_impact_personas_have_counterweights(self) -> None:
        for persona_id in ["peter-thiel", "elon-musk", "mao-zedong", "sun-tzu", "laozi"]:
            graph = self.graphs[persona_id]
            contract = graph["ontology_contract"]
            self.assertGreaterEqual(len(contract["dangerous_when"]), 1, persona_id)
            self.assertGreaterEqual(len(contract["requires_counterweight_from"]), 1, persona_id)
            self.assertGreaterEqual(len(contract["must_be_checked_by"]), 1, persona_id)

    def test_expression_patterns_do_not_enable_impersonation(self) -> None:
        for persona_id, graph in self.graphs.items():
            forbidden = graph["ontology_contract"]["forbidden_actions"]
            self.assertIn("claim_to_be_real_person", forbidden, persona_id)
            self.assertIn("fabricate_private_memory", forbidden, persona_id)
            for pattern in graph["expression_patterns"]:
                self.assertNotIn("第一人称冒充", pattern["usage_boundary"], persona_id)

    def test_philosophy_personas_have_modern_boundary(self) -> None:
        for persona_id in ["laozi", "confucius", "wang-yangming"]:
            boundaries = " ".join(item["description"] for item in self.graphs[persona_id]["boundaries"])
            self.assertIn("现代", boundaries, persona_id)
            self.assertIn("商业证据", boundaries, persona_id)


if __name__ == "__main__":
    unittest.main()
