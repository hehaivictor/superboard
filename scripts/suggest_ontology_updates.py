#!/usr/bin/env python3
"""Suggest persona ontology update candidates from a decision record."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def suggest_updates(record: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for hit in record.get("ontology_rule_hits", []) if isinstance(record.get("ontology_rule_hits"), list) else []:
        if not isinstance(hit, dict):
            continue
        missing = hit.get("missing_evidence", [])
        if missing:
            candidates.append(
                {
                    "update_id": f"update-{hit.get('persona_id', 'unknown')}-{hit.get('rule_id', 'rule')}",
                    "persona_id": hit.get("persona_id", ""),
                    "rule_id": hit.get("rule_id", ""),
                    "status": "weakened",
                    "reason": "本次审议存在未补齐证据，复盘后需要判断该规则是否应降权或补证据。",
                    "missing_evidence": missing,
                }
            )
    return candidates


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: suggest_ontology_updates.py <record.json>", file=sys.stderr)
        return 2
    record = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    print(json.dumps(suggest_updates(record), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
