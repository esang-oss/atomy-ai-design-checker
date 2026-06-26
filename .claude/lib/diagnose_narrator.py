"""Narrate diagnosis findings with a rule fallback."""
from __future__ import annotations

from typing import Any


_SEV = {"high": 0, "medium": 1, "low": 2}


def _rule_order(findings: list[Any]) -> list[Any]:
    return sorted(
        findings,
        key=lambda f: (_SEV.get(f.severity, 3), f.category, f.rule_id, f.evidence_ref),
    )


def _try_llm(model: Any) -> dict | None:
    """Placeholder for optional local/cloud narration. Current slice is rule-only."""
    return None


def narrate(model: Any) -> dict:
    try:
        llm = _try_llm(model)
    except Exception:
        llm = None
    if llm and len(llm.get("ordered", [])) == len(model.findings):
        return {"ordered": llm["ordered"], "narrative": llm["narrative"], "engine": "llm"}
    ordered = _rule_order(model.findings)
    counts = model.counts
    narrative = (
        f"청소 {counts.get('cleanup', 0)} · "
        f"다음할일 {counts.get('next_action', 0)} · "
        f"효율 {counts.get('efficiency', 0)}"
    )
    return {"ordered": ordered, "narrative": narrative, "engine": "rule"}
