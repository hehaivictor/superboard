from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PersonaGraphSchemaTests(unittest.TestCase):
    def test_persona_graph_schema_declares_required_ontology_objects(self) -> None:
        schema = json.loads((ROOT / "ontology/schemas/persona_graph.schema.json").read_text(encoding="utf-8"))

        required = set(schema["required"])
        for field in [
            "person",
            "ontology_contract",
            "sources",
            "claims",
            "mental_models",
            "heuristics",
            "historical_decisions",
            "episodes",
            "expression_patterns",
            "boundaries",
            "contradictions",
            "actions",
            "relations",
            "representative_viewpoints",
            "evidence_graph",
            "model_comparisons",
            "action_audit",
            "eval_cases",
            "ontology_updates",
            "version_log",
        ]:
            self.assertIn(field, required)
            self.assertIn(field, schema["properties"])

    def test_supporting_schemas_exist(self) -> None:
        for relative in [
            "ontology/schemas/persona_source.schema.json",
            "ontology/schemas/persona_eval_case.schema.json",
            "ontology/schemas/persona_relation.schema.json",
        ]:
            schema = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual("object", schema["type"], relative)
            self.assertIn("required", schema, relative)
            self.assertIn("properties", schema, relative)


if __name__ == "__main__":
    unittest.main()
