"""Create the final Sol-acceptance freeze manifests for Phase 10A and 10B."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
SOURCE_COMMIT = "e1f233cc89e3694d2f08dfd81fde6f9194f57a65"
ACCEPTED_DATE = "2026-09-04"
REVIEW_RECORDS = [
    "reports/governance_independent_review.md",
    "reports/governance_post_correction_independent_review.md",
    "reports/governance_additional_post_correction_independent_review.md",
]


def artifact(rel: str, role: str) -> tuple[str, dict[str, object]]:
    path = ROOT / rel
    data = path.read_bytes()
    return rel, {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "role": role}


def source_artifacts(working_name: str, extra: list[tuple[str, str]]) -> dict[str, dict[str, object]]:
    working = json.loads((REPORTS / working_name).read_text(encoding="utf-8"))
    artifacts: dict[str, dict[str, object]] = {}
    for rel, metadata in working["artifacts"].items():
        role = "Phase 10 analytical artifact"
        if rel.endswith("_sources.md"):
            role = "source report"
        elif rel.endswith("_assumptions.md"):
            role = "assumptions and scope report"
        elif rel.endswith("_findings.md"):
            role = "findings report"
        elif rel.endswith("_qa.md"):
            role = "QA report"
        elif rel.endswith(".png"):
            role = "map raster"
        elif rel.endswith(".svg"):
            role = "map vector"
        artifacts[rel] = artifact(rel, role)[1]
    for rel, role in extra:
        artifacts[rel] = artifact(rel, role)[1]
    return artifacts


def manifest(phase: str, baseline: str, counts: dict[str, int], artifacts: dict[str, dict[str, object]]) -> dict[str, object]:
    return {
        "accepted_phase": phase,
        "baseline": baseline,
        "status": "ACCEPTED / FROZEN",
        "accepted_by": "Sol explicit acceptance decision supplied for this run",
        "accepted_date": ACCEPTED_DATE,
        "source_commit": SOURCE_COMMIT,
        "acceptance_basis": "Sol formally accepted the corrected and finalized Phase 10A/10B package after Python validation, independent R validation, strict provenance/citation checks, Phase 1–9 immutability validation, clean Git/LFS checks, and passed post-correction independent reviews.",
        "counts": counts,
        "artifacts": artifacts,
    }


def write_manifest(rel: str, payload: dict[str, object]) -> None:
    (ROOT / rel).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    review_extra = [(rel, "independent review record") for rel in REVIEW_RECORDS]
    a_artifacts = source_artifacts(
        "governance_baseline_manifest.json",
        [("reports/governance_baseline_artifact_check.json", "machine validation result"), *review_extra],
    )
    a_payload = manifest(
        "10A",
        "Governance & Jurisdiction Baseline, 2026",
        {"actors": 40, "authorities": 100, "relationships": 100, "sources": 48, "uncertainties": 16},
        a_artifacts,
    )
    a_rel = "reports/phase10a_governance_jurisdiction_freeze_manifest.json"
    write_manifest(a_rel, a_payload)

    a_path = ROOT / a_rel
    a_data = a_path.read_bytes()
    b_artifacts = source_artifacts(
        "governance_dependency_manifest.json",
        [("reports/governance_dependency_artifact_check.json", "machine validation result"), *review_extra],
    )
    b_payload = manifest(
        "10B",
        "Cross-System Authority, Dependencies & Coordination, 2026",
        {"dependency_register": 25, "dependency_edges": 25, "coordination_mechanisms": 14, "matrix_rows": 10, "sources_reused": 48},
        b_artifacts,
    )
    b_payload["phase10a_freeze_manifest"] = {
        "path": a_rel,
        "sha256": hashlib.sha256(a_data).hexdigest(),
        "bytes": len(a_data),
    }
    write_manifest("reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", b_payload)
    print(json.dumps({"status": "created", "phase10a_artifacts": len(a_artifacts), "phase10b_artifacts": len(b_artifacts)}))


if __name__ == "__main__":
    main()
