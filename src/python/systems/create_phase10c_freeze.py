"""Create the Sol-accepted Phase 10C governance-futures freeze manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
SOURCE_COMMIT = "4541e6dd036ccc51534827ba1c6a791fd37d0145"
ACCEPTED_DATE = "2026-09-07"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}


def canonical_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def artifact(rel: str, role: str) -> tuple[str, dict[str, object]]:
    path = ROOT / rel
    raw = path.read_bytes()
    data = canonical_text(raw) if path.suffix.lower() in TEXT_SUFFIXES else raw
    return rel, {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "role": role}


def role_for(rel: str) -> str:
    if rel.endswith("_sources.md"):
        return "source report"
    if rel.endswith("_assumptions.md"):
        return "assumptions and scope report"
    if rel.endswith("_consistency.md"):
        return "scenario consistency report"
    if rel.endswith("_findings.md"):
        return "findings report"
    if rel.endswith("_worldbuilding.md"):
        return "speculative implications report"
    if rel.endswith("_qa.md"):
        return "QA report"
    if rel.endswith("_independent_review.md"):
        return "final independent-review record"
    if rel.endswith(".png"):
        return "map or figure raster"
    if rel.endswith(".svg"):
        return "map or figure vector"
    if rel.endswith("_manifest.json"):
        return "scenario artifact manifest"
    if rel.endswith("_artifact_check.json"):
        return "machine validation result"
    if rel.endswith("comparison.csv"):
        return "scenario comparison table"
    if rel.endswith("_sources.csv"):
        return "scenario source registry"
    return "scenario state table"


def main() -> None:
    working_rel = "reports/governance_scenario_manifest.json"
    working = json.loads((ROOT / working_rel).read_text(encoding="utf-8"))
    assert working["phase"] == "10C"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == {
        "scenario_assumptions": 48,
        "actor_states": 120,
        "authority_states": 90,
        "dependency_states": 150,
        "coordination_states": 84,
        "uncertainty_states": 96,
        "comparison_rows": 6,
    }

    artifacts: dict[str, dict[str, object]] = {}
    for rel in working["artifacts"]:
        artifacts[rel] = artifact(rel, role_for(rel))[1]
    for rel in (working_rel, "reports/governance_scenario_artifact_check.json"):
        artifacts[rel] = artifact(rel, role_for(rel))[1]

    payload: dict[str, object] = {
        "accepted_phase": "10C",
        "baseline": "Governance Futures, 2050 / 2075",
        "status": "ACCEPTED / FROZEN",
        "accepted_by": "Sol explicit acceptance decision supplied for this run",
        "accepted_date": ACCEPTED_DATE,
        "source_commit": SOURCE_COMMIT,
        "acceptance_basis": "Sol formally accepted and froze the validated Phase 10C scenario package after the fresh independent review passed with no blocking findings, with Phase 10A/10B and Phase 1–9 freeze integrity preserved.",
        "counts": {
            "scenario_assumptions": 48,
            "actor_states": 120,
            "authority_states": 90,
            "dependency_states": 150,
            "coordination_states": 84,
            "uncertainty_states": 96,
            "scenario_sources": 19,
            "comparison_rows": 6,
        },
        "artifacts": artifacts,
        "protected_inputs": working["protected_inputs"],
    }
    target = REPORTS / "phase10c_governance_futures_freeze_manifest.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "created", "path": str(target), "artifacts": len(artifacts), "source_commit": SOURCE_COMMIT}))


if __name__ == "__main__":
    main()
