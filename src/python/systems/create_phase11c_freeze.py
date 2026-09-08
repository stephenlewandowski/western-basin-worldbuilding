"""Create the Sol-accepted Phase 11C population-futures freeze manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
SOURCE_COMMIT = "00c582c0f6204eb7f7a3952d90c2768a30f4bf68"
ACCEPTED_DATE = "2026-09-08"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}
FINAL = "reports/phase11c_population_settlement_futures_freeze_manifest.json"
EXTRA = (
    "reports/population_settlement_future_artifact_check.json",
    "src/python/systems/validate_phase11_freezes.py",
    "src/R/systems/validate_phase11_freezes.R",
)


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
    if rel.endswith("_findings.md"):
        return "findings report"
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
    if rel.endswith("validate_phase11_freezes.py"):
        return "Python independent freeze validator"
    if rel.endswith("validate_phase11_freezes.R"):
        return "independent R freeze validator"
    return "scenario state table"


def main() -> None:
    working_rel = "reports/population_settlement_future_manifest.json"
    working = json.loads((ROOT / working_rel).read_text(encoding="utf-8"))
    assert working["phase"] == "11C"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == {
        "scenario_assumptions": 36,
        "projection_evidence": 6,
        "future_states": 108,
        "future_relationships": 108,
        "uncertainty_states": 36,
        "comparison_rows": 6,
        "scenario_sources": 11,
    }

    artifacts: dict[str, dict[str, object]] = {}
    for rel in working["artifacts"]:
        artifacts[rel] = artifact(rel, role_for(rel))[1]
    artifacts[working_rel] = artifact(working_rel, "validated working scenario manifest")[1]
    for rel in EXTRA:
        artifacts[rel] = artifact(rel, role_for(rel))[1]

    payload: dict[str, object] = {
        "accepted_phase": "11C",
        "baseline": "Population & Settlement Futures, 2050 / 2075",
        "status": "ACCEPTED / FROZEN",
        "accepted_by": "Sol explicit acceptance decision supplied for this run",
        "accepted_date": ACCEPTED_DATE,
        "source_commit": SOURCE_COMMIT,
        "acceptance_basis": "Sol formally accepted and froze the validated Phase 11C qualitative scenario package after the fresh independent review passed with all blocking arrays empty; Phase 11A/11B and Phase 1–10 freeze integrity remained intact.",
        "counts": {
            "scenario_assumptions": 36,
            "projection_evidence": 6,
            "future_states": 108,
            "future_relationships": 108,
            "uncertainty_states": 36,
            "scenario_sources": 11,
            "comparison_rows": 6,
        },
        "artifacts": artifacts,
        "protected_inputs": [
            "reports/phase11a_population_settlement_freeze_manifest.json",
            "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
            "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
            "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
            "reports/phase10c_governance_futures_freeze_manifest.json",
        ],
        "phase11a_11b_immutable": True,
        "phase1_10_immutable": True,
        "numeric_future_values_adopted": False,
        "climate_migration_as_growth_assumption": False,
        "active_holds_preserved": {
            "great_black_swamp": "C — HOLD / noncanonical",
            "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
        },
        "phase12_implemented": False,
    }
    target = ROOT / FINAL
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "created", "path": FINAL, "artifacts": len(artifacts), "source_commit": SOURCE_COMMIT}))


if __name__ == "__main__":
    main()
