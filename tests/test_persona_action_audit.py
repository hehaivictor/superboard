from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

AUDIT_PATH = ROOT / "scripts" / "persona_action_audit.py"
audit_spec = importlib.util.spec_from_file_location("persona_action_audit", AUDIT_PATH)
persona_action_audit = importlib.util.module_from_spec(audit_spec)
assert audit_spec.loader is not None
sys.modules["persona_action_audit"] = persona_action_audit
audit_spec.loader.exec_module(persona_action_audit)


class PersonaActionAuditTests(unittest.TestCase):
    def test_action_audit_entry_contains_governance_fields(self) -> None:
        entry = persona_action_audit.make_audit_entry(
            persona_id="peter-thiel",
            action="ExplainSelection",
            input_summary="非共识定价方案",
            output_summary="需要证明独占路径",
            evidence_refs=["source_001"],
            boundary_refs=["boundary_001"],
            counterweight_refs=["charlie-munger"],
        )

        self.assertEqual("peter-thiel", entry["persona_id"])
        self.assertEqual("ExplainSelection", entry["action"])
        self.assertTrue(entry["audit_id"].startswith("audit-"))
        self.assertEqual(["source_001"], entry["evidence_refs"])
        self.assertEqual(["boundary_001"], entry["boundary_refs"])
        self.assertEqual(["charlie-munger"], entry["counterweight_refs"])


if __name__ == "__main__":
    unittest.main()
