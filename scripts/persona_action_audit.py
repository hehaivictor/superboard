#!/usr/bin/env python3
"""Build auditable records for persona graph actions."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


def stable_audit_id(persona_id: str, action: str, input_summary: str) -> str:
    digest = hashlib.sha1(f"{persona_id}|{action}|{input_summary}".encode("utf-8")).hexdigest()[:10]
    return f"audit-{digest}"


def make_audit_entry(
    persona_id: str,
    action: str,
    input_summary: str,
    output_summary: str,
    evidence_refs: list[str],
    boundary_refs: list[str],
    counterweight_refs: list[str],
) -> dict[str, Any]:
    return {
        "audit_id": stable_audit_id(persona_id, action, input_summary),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "persona_id": persona_id,
        "action": action,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "evidence_refs": evidence_refs,
        "boundary_refs": boundary_refs,
        "counterweight_refs": counterweight_refs,
    }
