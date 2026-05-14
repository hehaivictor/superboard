from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMPILER_PATH = ROOT / "scripts" / "compile_persona_prompt.py"
compiler_spec = importlib.util.spec_from_file_location("compile_persona_prompt", COMPILER_PATH)
compile_persona_prompt = importlib.util.module_from_spec(compiler_spec)
assert compiler_spec.loader is not None
sys.modules["compile_persona_prompt"] = compile_persona_prompt
compiler_spec.loader.exec_module(compile_persona_prompt)

LOADER_PATH = ROOT / "scripts" / "persona_graph_loader.py"
loader_spec = importlib.util.spec_from_file_location("persona_graph_loader", LOADER_PATH)
persona_graph_loader = importlib.util.module_from_spec(loader_spec)
assert loader_spec.loader is not None
sys.modules["persona_graph_loader"] = persona_graph_loader
loader_spec.loader.exec_module(persona_graph_loader)


class CompilePersonaPromptTests(unittest.TestCase):
    def test_compiles_bounded_prompt_fragment_from_graph_refs(self) -> None:
        graph = persona_graph_loader.load_persona_graphs(ROOT)["warren-buffett"]
        rule = graph["decision_rules"][0]

        fragment = compile_persona_prompt.compile_persona_fragment(
            graph,
            {
                "claim_id": rule["claim_id"],
                "model_id": rule["model_id"],
                "source_ids": rule["source_ids"],
                "boundary_id": rule["boundary_id"],
                "counter_test_id": rule["counter_test_id"],
            },
        )

        self.assertIn("沃伦·巴菲特", fragment)
        self.assertIn(rule["claim_id"], fragment)
        self.assertIn(rule["model_id"], fragment)
        self.assertIn("身份边界", fragment)
        self.assertNotIn("I am Warren Buffett", fragment)
        self.assertLess(len(fragment), 2200)


if __name__ == "__main__":
    unittest.main()
