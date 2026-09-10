#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 13C."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "assumptions": 36,
    "transmission_states": 36,
    "surveillance_states": 36,
    "response_states": 36,
    "dependency_states": 36,
    "uncertainty_states": 36,
    "scenario_sources": 33,
    "comparison_rows": 6,
}
EXPECTED_PRIOR_ENTRIES = 358
EXPECTED_PRIOR_UNIQUE = 351
SOURCE_COMMIT = "c746e361e052e979227e40140c6d923557911524"
FINAL_MANIFEST = "reports/phase13c_infectious_disease_futures_freeze_manifest.json"
WORKING_MANIFEST = "reports/infectious_disease_scenario_manifest.json"
ARTIFACT_CHECK = "reports/infectious_disease_scenario_artifact_check.json"
PHASE13A_MANIFEST = "reports/phase13a_infectious_disease_freeze_manifest.json"
PHASE13B_MANIFEST = "reports/phase13b_infectious_disease_dependencies_freeze_manifest.json"
REVIEW = "reports/infectious_disease_scenario_independent_review.md"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yaml", ".yml", ".toml", ".svg"}
REVIEWS = (REVIEW,)
WORKING_ARTIFACTS = (
    "data/processed/scenarios/infectious_disease_scenario_assumptions.csv",
    "data/processed/scenarios/infectious_disease_transmission_states_scenario.csv",
    "data/processed/scenarios/infectious_disease_surveillance_states_scenario.csv",
    "data/processed/scenarios/infectious_disease_response_states_scenario.csv",
    "data/processed/scenarios/infectious_disease_dependency_states_scenario.csv",
    "data/processed/scenarios/infectious_disease_uncertainty_states_scenario.csv",
    "data/processed/analysis/infectious_disease_scenario_sources.csv",
    "outputs/figures/infectious_disease_scenario_comparison.csv",
    "outputs/maps/systems/43_infectious_disease_system_futures_2050.png",
    "outputs/maps/systems/43_infectious_disease_system_futures_2050.svg",
    "outputs/maps/systems/43b_infectious_disease_system_futures_2075.png",
    "outputs/maps/systems/43b_infectious_disease_system_futures_2075.svg",
    "outputs/figures/infectious_disease_scenario_comparison.png",
    "outputs/figures/infectious_disease_scenario_comparison.svg",
    "reports/infectious_disease_scenario_sources.md",
    "reports/infectious_disease_scenario_assumptions.md",
    "reports/infectious_disease_scenario_findings.md",
    "reports/infectious_disease_scenario_qa.md",
    "reports/phase13c_citation_ledger.json",
    "src/python/systems/build_infectious_disease_futures.py",
    "src/python/systems/validate_infectious_disease_futures.py",
    "src/R/systems/validate_infectious_disease_futures.R",
    ARTIFACT_CHECK,
    REVIEW,
)
EXPECTED_FINAL_ARTIFACTS = WORKING_ARTIFACTS + (
    WORKING_MANIFEST,
    "docs/phase_briefs/phase13c_infectious_disease_futures.md",
    "src/python/systems/validate_phase13c_freeze.py",
    "src/R/systems/validate_phase13c_freeze.R",
)


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("artifacts", payload.get("files", {}))


def canonical(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hash(root: Path, relative: str, expected: dict[str, Any] | str) -> str:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing protected artifact: {relative}"
    expected_hash = expected if isinstance(expected, str) else str(expected["sha256"])
    expected_bytes = None if isinstance(expected, str) else expected.get("bytes")
    raw = path.read_bytes()
    candidates = [(sha256(raw), len(raw), "exact")]
    if path.suffix in TEXT_SUFFIXES:
        normalized = canonical(raw)
        candidates.extend(
            [
                (sha256(normalized), len(normalized), "newline-normalized"),
                (sha256(normalized.replace(b"\n", b"\r\n")), len(normalized.replace(b"\n", b"\r\n")), "newline-normalized"),
            ]
        )
    for digest, size, mode in candidates:
        if digest == expected_hash and (expected_bytes is None or int(expected_bytes) == size):
            return mode
    raise AssertionError(f"hash/byte mismatch: {relative}")


def verify_artifacts(root: Path, payload: dict[str, Any], label: str, expected_count: int | None = None) -> dict[str, int]:
    artifacts = artifact_entries(payload)
    assert artifacts, f"{label}: no artifacts"
    if expected_count is not None:
        assert len(artifacts) == expected_count, f"{label}: artifact count {len(artifacts)}"
    exact = 0
    normalized = 0
    for relative, expected in artifacts.items():
        mode = verify_hash(root, relative, expected)
        if mode == "exact":
            exact += 1
        else:
            normalized += 1
    return {"entries": len(artifacts), "exact": exact, "newline_normalized": normalized}


def verify_prior_system(root: Path) -> dict[str, int]:
    excluded = {Path(FINAL_MANIFEST).name, Path(PHASE13A_MANIFEST).name, Path(PHASE13B_MANIFEST).name}
    expected_hashes: dict[str, str] = {}
    protected: set[str] = set()
    entries = 0
    manifests = []
    for path in sorted((root / "reports").glob("phase*_freeze_manifest.json")):
        if path.name in excluded:
            continue
        manifests.append(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in artifact_entries(payload).items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if relative in expected_hashes:
                assert expected_hashes[relative] == expected, f"conflicting prior hash: {relative}"
            expected_hashes[relative] = expected
            verify_hash(root, relative, expected)
            protected.add(relative)
            entries += 1
    assert entries == EXPECTED_PRIOR_ENTRIES, entries
    assert len(protected) == EXPECTED_PRIOR_UNIQUE, len(protected)
    changed = set(subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return {"manifest_count": len(manifests), "entries": entries, "unique": len(protected)}


def verify_review(root: Path) -> dict[str, bool]:
    for relative in REVIEWS:
        assert (root / relative).is_file() and (root / relative).stat().st_size > 0, relative
    text = (root / REVIEW).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "final independent-review JSON block missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in (
        "security_concerns", "logic_errors", "provenance_errors", "epidemiological_errors",
        "scenario_boundary_errors", "surveillance_errors", "spatial_scale_errors", "health_boundary_errors",
    ):
        assert verdict.get(key) == [], key
    return {"passed": True, "blocking_arrays_empty": True, "review_preserved": True}


def verify_working_package(root: Path) -> dict[str, int]:
    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "13C"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == EXPECTED_COUNTS
    assert working["phase13a_13b_accepted_frozen"] is True
    assert working["phase1_12_immutable"] is True
    assert working["phase14_implemented"] is False
    assert list(artifact_entries(working)) == list(WORKING_ARTIFACTS)
    result = verify_artifacts(root, working, "Phase 13C working manifest", len(WORKING_ARTIFACTS))
    assert working["phase13a_freeze_manifest"]["path"] == PHASE13A_MANIFEST
    assert working["phase13b_freeze_manifest"]["path"] == PHASE13B_MANIFEST
    verify_hash(root, PHASE13A_MANIFEST, working["phase13a_freeze_manifest"])
    verify_hash(root, PHASE13B_MANIFEST, working["phase13b_freeze_manifest"])
    return result


def verify_artifact_check(root: Path) -> None:
    check = load_json(root, ARTIFACT_CHECK)
    assert check["status"] == "passed"
    for key, expected in EXPECTED_COUNTS.items():
        assert check[key] == expected, key
    assert check["phase13a_13b_freeze_integrity"] is True
    assert check["prior_freeze_manifest_entries_checked"] == EXPECTED_PRIOR_ENTRIES
    assert check["prior_unique_protected_artifacts_checked"] == EXPECTED_PRIOR_UNIQUE
    assert check["phase13a_artifacts_checked"] == 25
    assert check["phase13b_artifacts_checked"] == 24
    assert check["manifest_artifacts_checked"] == len(WORKING_ARTIFACTS)
    assert check["active_holds_preserved"] is True
    assert check["deferred_maintenance_preserved"] is True
    assert check["phase14_not_implemented"] is True
    assert check["review_present"] is True


def verify_no_phase14(root: Path) -> None:
    for base in (root / "data/processed", root / "outputs/maps/systems", root / "src/python/systems", root / "src/R/systems"):
        for path in base.rglob("*"):
            if path.is_file():
                name = path.name.lower()
                assert "phase14" not in name and "phase_14" not in name, str(path)
                assert not name.startswith(("44_",)), str(path)


def require_terms(root: Path, relative: str, terms: tuple[str, ...]) -> None:
    text = (root / relative).read_text(encoding="utf-8").lower()
    for term in terms:
        assert term in text, (relative, term)


def verify_status_surfaces(root: Path) -> None:
    require_terms(root, "PROJECT_STATUS.md", (
        "## phase 13c — accepted / frozen", FINAL_MANIFEST.lower(),
        "active phase: **none**", "next analytical phase: **not approved**",
        "phase 14 is not implemented", "great black swamp", "hold", "noncanonical",
        "intake-coordinate discrepancy", "unresolved",
    ))
    require_terms(root, "docs/canon_status.md", (
        "phase 13c is **accepted / frozen**", FINAL_MANIFEST.lower(),
        "active phase: **none**", "next analytical phase: **not approved**",
        "phase 14 is not implemented", "great black swamp", "hold", "noncanonical",
        "intake-coordinate discrepancy", "unresolved",
    ))
    require_terms(root, "reports/current_phase_handoff.md", (
        "## phase 13c final acceptance / freeze handoff", "phase 13c **accepted / frozen**",
        FINAL_MANIFEST.lower(), "active phase: **none**", "next analytical phase: **not approved**",
        "phase 14 is not implemented", "great black swamp", "hold", "noncanonical",
        "intake-coordinate discrepancy", "unresolved",
    ))
    require_terms(root, "README.md", (
        "phase 13c is **accepted / frozen**", FINAL_MANIFEST.lower(),
        "phase 13c python freeze validator", "phase 13c independent r freeze validator",
    ))
    require_terms(root, "CHANGELOG.md", (
        "sol formally accepted and froze phase 13c", FINAL_MANIFEST.lower(),
        "active phase is none", "next analytical phase is not approved",
    ))
    require_terms(root, "docs/phase_briefs/phase13c_infectious_disease_futures.md", (
        "status: approved scope / not implemented", "phase 13c", "2050", "2075",
        "great black swamp", "toledo intake-coordinate discrepancy",
    ))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "13C"
    assert final["baseline"] == "Infectious Disease System Futures, 2050 / 2075"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-10"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["phase13a_freeze_manifest"]["path"] == PHASE13A_MANIFEST
    assert final["phase13b_freeze_manifest"]["path"] == PHASE13B_MANIFEST
    assert final["protected_inputs"] == [PHASE13A_MANIFEST, PHASE13B_MANIFEST, WORKING_MANIFEST]
    assert final["phase13a_13b_accepted_frozen"] is True
    assert final["phase1_12_immutable"] is True
    assert final["phase14_implemented"] is False
    for key in ("numeric_future_values_adopted", "future_case_counts", "future_incidence_forecast", "outbreak_probability", "disease_burden_forecast", "individual_risk_model", "vulnerability_ej_scoring", "unsupported_local_downscaling"):
        assert final[key] is False, key
    assert final["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    assert final["deferred_maintenance_preserved"] == [
        "Phase 6B manifest status wording mismatch",
        "Phase 3A missing manifest status",
    ]
    assert list(artifact_entries(final)) == list(EXPECTED_FINAL_ARTIFACTS)
    assert FINAL_MANIFEST not in artifact_entries(final)
    final_result = verify_artifacts(root, final, "Phase 13C final freeze manifest", len(EXPECTED_FINAL_ARTIFACTS))

    working_result = verify_working_package(root)
    verify_artifact_check(root)
    phase13a = load_json(root, PHASE13A_MANIFEST)
    phase13b = load_json(root, PHASE13B_MANIFEST)
    assert phase13a["status"] == "ACCEPTED / FROZEN"
    assert phase13b["status"] == "ACCEPTED / FROZEN"
    phase13a_result = verify_artifacts(root, phase13a, "Phase 13A final freeze manifest", 25)
    phase13b_result = verify_artifacts(root, phase13b, "Phase 13B final freeze manifest", 24)
    prior = verify_prior_system(root)
    review = verify_review(root)
    verify_no_phase14(root)
    verify_status_surfaces(root)

    result = {
        "status": "passed",
        "phase": "13C",
        "freeze_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": working_result,
        "phase13a_integrity": {"final_artifacts": phase13a_result["entries"]},
        "phase13b_integrity": {"final_artifacts": phase13b_result["entries"]},
        "prior_system_immutability": prior,
        "review_history": review,
        "counts": EXPECTED_COUNTS,
        "active_holds_preserved": True,
        "deferred_maintenance_preserved": True,
        "phase14_not_implemented": True,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
