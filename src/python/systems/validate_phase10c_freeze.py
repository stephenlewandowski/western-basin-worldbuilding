"""Independently validate the accepted Phase 10C freeze boundary."""
from __future__ import annotations

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
SOURCE_COMMIT = "4541e6dd036ccc51534827ba1c6a791fd37d0145"
FINAL = REPORTS / "phase10c_governance_futures_freeze_manifest.json"
PHASE10A = REPORTS / "phase10a_governance_jurisdiction_freeze_manifest.json"
PHASE10B = REPORTS / "phase10b_governance_dependencies_coordination_freeze_manifest.json"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}
EXPECTED_COUNTS = {
    "scenario_assumptions": 48,
    "actor_states": 120,
    "authority_states": 90,
    "dependency_states": 150,
    "coordination_states": 84,
    "uncertainty_states": 96,
    "scenario_sources": 19,
    "comparison_rows": 6,
}
EXPECTED_SCENARIO_ARTIFACTS = {
    "data/processed/scenarios/governance_scenario_assumptions.csv",
    "data/processed/scenarios/governance_actor_states_scenario.csv",
    "data/processed/scenarios/governance_authority_states_scenario.csv",
    "data/processed/scenarios/governance_dependency_states_scenario.csv",
    "data/processed/scenarios/governance_coordination_states_scenario.csv",
    "data/processed/scenarios/governance_uncertainty_states_scenario.csv",
    "data/processed/analysis/governance_scenario_sources.csv",
    "outputs/figures/governance_scenario_comparison.csv",
    "outputs/figures/governance_scenario_comparison.png",
    "outputs/figures/governance_scenario_comparison.svg",
    "outputs/maps/systems/34_governance_futures_2050.png",
    "outputs/maps/systems/34_governance_futures_2050.svg",
    "outputs/maps/systems/34b_governance_futures_2075.png",
    "outputs/maps/systems/34b_governance_futures_2075.svg",
    "reports/governance_scenario_sources.md",
    "reports/governance_scenario_assumptions.md",
    "reports/governance_scenario_consistency.md",
    "reports/governance_scenario_findings.md",
    "reports/governance_scenario_worldbuilding.md",
    "reports/governance_scenario_qa.md",
    "reports/governance_scenario_independent_review.md",
}
FINAL_EXTRA = {"reports/governance_scenario_manifest.json", "reports/governance_scenario_artifact_check.json"}
PHASE10A_ARTIFACTS = {
    "data/processed/analysis/governance_actors.csv",
    "data/processed/analysis/governance_authorities.csv",
    "data/processed/networks/governance_relationships.csv",
    "data/processed/analysis/governance_sources.csv",
    "data/processed/analysis/governance_uncertainty_register.csv",
    "outputs/maps/systems/32_governance_jurisdiction_2026.png",
    "outputs/maps/systems/32_governance_jurisdiction_2026.svg",
    "reports/governance_baseline_sources.md",
    "reports/governance_baseline_assumptions.md",
    "reports/governance_baseline_findings.md",
    "reports/governance_baseline_qa.md",
    "reports/governance_baseline_artifact_check.json",
    "reports/governance_independent_review.md",
    "reports/governance_post_correction_independent_review.md",
    "reports/governance_additional_post_correction_independent_review.md",
}
PHASE10B_ARTIFACTS = {
    "data/processed/analysis/governance_dependency_register.csv",
    "data/processed/analysis/governance_coordination_mechanisms.csv",
    "data/processed/analysis/governance_dependency_matrix.csv",
    "data/processed/networks/governance_dependency_edges.csv",
    "data/processed/analysis/governance_sources.csv",
    "outputs/maps/systems/33_cross_system_governance_dependencies_2026.png",
    "outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg",
    "reports/governance_dependency_sources.md",
    "reports/governance_dependency_assumptions.md",
    "reports/governance_dependency_findings.md",
    "reports/governance_dependency_qa.md",
    "reports/governance_dependency_artifact_check.json",
    "reports/governance_independent_review.md",
    "reports/governance_post_correction_independent_review.md",
    "reports/governance_additional_post_correction_independent_review.md",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def source_blob(rel: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SOURCE_COMMIT}:{rel}"])


def portable_match(rel: str, expected: str) -> bool:
    path = ROOT / rel
    actual = path.read_bytes()
    if sha256(actual) == expected:
        return True
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    accepted = source_blob(rel)
    if canonical(actual) != canonical(accepted):
        return False
    return expected in {sha256(accepted), sha256(accepted.replace(b"\n", b"\r\n"))}


def manifest_artifacts(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("artifacts", payload.get("files", {}))


def verify_manifest(path: Path, phase: str, baseline: str, expected_artifacts: set[str], counts: dict[str, int]) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["accepted_phase"] == phase
    assert payload["baseline"] == baseline
    assert payload["status"] == "ACCEPTED / FROZEN"
    assert payload["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert payload["source_commit"] == "e1f233cc89e3694d2f08dfd81fde6f9194f57a65"
    assert payload["counts"] == counts
    artifacts = payload["artifacts"]
    assert set(artifacts) == expected_artifacts
    for rel, meta in artifacts.items():
        assert set(meta) == {"sha256", "bytes", "role"}, rel
        path_rel = ROOT / rel
        assert path_rel.exists(), rel
        assert portable_match(rel, str(meta["sha256"])), rel
        assert str(meta["role"])
    return len(artifacts)


def verify_phase10ab() -> tuple[int, int]:
    a = verify_manifest(
        PHASE10A,
        "10A",
        "Governance & Jurisdiction Baseline, 2026",
        PHASE10A_ARTIFACTS,
        {"actors": 40, "authorities": 100, "relationships": 100, "sources": 48, "uncertainties": 16},
    )
    b = verify_manifest(
        PHASE10B,
        "10B",
        "Cross-System Authority, Dependencies & Coordination, 2026",
        PHASE10B_ARTIFACTS,
        {"dependency_register": 25, "dependency_edges": 25, "coordination_mechanisms": 14, "matrix_rows": 10, "sources_reused": 48},
    )
    b_payload = json.loads(PHASE10B.read_text(encoding="utf-8"))
    assert b_payload["phase10a_freeze_manifest"]["path"] == "reports/phase10a_governance_jurisdiction_freeze_manifest.json"
    assert b_payload["phase10a_freeze_manifest"]["sha256"] == sha256(PHASE10A.read_bytes())
    assert b_payload["phase10a_freeze_manifest"]["bytes"] == PHASE10A.stat().st_size
    return a + b, len(PHASE10A_ARTIFACTS | PHASE10B_ARTIFACTS)


def verify_prior_freezes(phase10_paths: set[str]) -> tuple[int, int]:
    prior_paths: set[str] = set()
    total = 0
    newline_only = 0
    current = {
        "phase10a_governance_jurisdiction_freeze_manifest.json",
        "phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "phase10c_governance_futures_freeze_manifest.json",
    }
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if path.name in current:
            continue
        for rel, meta in manifest_artifacts(path).items():
            artifact = ROOT / rel
            assert artifact.exists(), rel
            expected = str(meta["sha256"] if isinstance(meta, dict) else meta)
            before = sha256(artifact.read_bytes())
            assert portable_match(rel, expected), rel
            if before != expected:
                newline_only += 1
            assert rel not in prior_paths, f"prior artifact assigned twice: {rel}"
            assert rel not in phase10_paths, f"prior/Phase 10 overlap: {rel}"
            prior_paths.add(rel)
            total += 1
    assert total == 196, total
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not changed.intersection(prior_paths), sorted(changed.intersection(prior_paths))
    return total, newline_only


def verify_review_and_docs() -> None:
    review = (REPORTS / "governance_scenario_independent_review.md").read_text(encoding="utf-8")
    review_lower = review.lower()
    assert '"passed": true' in review_lower
    for key in ("security_concerns", "logic_errors", "provenance_errors", "scenario_boundary_errors", "authority_classification_errors"):
        assert f'"{key}": []' in review_lower
    required = (
        "PROJECT_STATUS.md",
        "docs/canon_status.md",
        "docs/agent_workflow.md",
        "docs/phase_briefs/phase10a_governance_jurisdiction_baseline.md",
        "docs/phase_briefs/phase10b_governance_dependencies_coordination.md",
        "docs/phase_briefs/phase10c_governance_futures.md",
        "reports/current_phase_handoff.md",
        "README.md",
        "CHANGELOG.md",
        "reports/README.md",
    )
    for rel in required:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "phase 10c" in text and "accepted / frozen" in text, rel
    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "active phase: **none**" in text or "active phase: none" in text, rel
        assert "next analytical phase" in text and "not approved" in text, rel
    for rel in ("docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, rel
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, rel
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not any("phase11" in rel.lower() for rel in changed)


def verify_maps() -> None:
    for base, required in (("34_governance_futures_2050", "map 34"), ("34b_governance_futures_2075", "map 34b")):
        png = ROOT / f"outputs/maps/systems/{base}.png"
        svg = ROOT / f"outputs/maps/systems/{base}.svg"
        with Image.open(png) as image:
            image.verify()
        text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        for term in (required, "integrated basin", "federated / networked", "fragmented / contested", "not jurisdiction boundaries", "ai recommendation"):
            assert term in text, (base, term)
        if base.startswith("34b"):
            assert "2075 mature/diverged" in text


def main() -> None:
    final = json.loads(FINAL.read_text(encoding="utf-8"))
    assert final["accepted_phase"] == "10C"
    assert final["baseline"] == "Governance Futures, 2050 / 2075"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-07"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    final_artifacts = set(final["artifacts"])
    assert final_artifacts == EXPECTED_SCENARIO_ARTIFACTS | FINAL_EXTRA
    for rel, meta in final["artifacts"].items():
        assert set(meta) == {"sha256", "bytes", "role"}, rel
        assert (ROOT / rel).exists(), rel
        assert portable_match(rel, str(meta["sha256"])), rel
        assert int(meta["bytes"]) > 0
    assert final["protected_inputs"] == [
        "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
        "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
        "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
        "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
    ]
    phase10_entries, phase10_unique = verify_phase10ab()
    prior, newline_only = verify_prior_freezes(final_artifacts | PHASE10A_ARTIFACTS | PHASE10B_ARTIFACTS)
    verify_review_and_docs()
    verify_maps()
    result = {
        "status": "passed",
        "phase": "10C",
        "phase10c_freeze_manifest": FINAL.relative_to(ROOT).as_posix(),
        "phase10c_protected_artifacts": len(final_artifacts),
        "phase10a_10b_manifest_entries": phase10_entries,
        "phase10a_10b_unique_artifacts": phase10_unique,
        "prior_phase1_9_protected_artifacts": prior,
        "prior_newline_only_matches": newline_only,
        "scenario_counts": EXPECTED_COUNTS,
        "working_manifest_validated": True,
        "independent_review_passed_and_blocker_free": True,
        "phase10a_10b_integrity": True,
        "phase1_9_immutability": True,
        "maps_34_34b_valid": True,
        "holds_preserved": True,
        "phase11_absent": True,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
