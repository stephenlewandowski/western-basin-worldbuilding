#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 13B."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "dependency_register": 36,
    "dependency_edges": 36,
    "matrix_rows": 6,
    "evidence_crosswalk": 36,
    "sources": 33,
    "uncertainties": 14,
}
EXPECTED_PRIOR_ENTRIES = 358
EXPECTED_PRIOR_UNIQUE = 351
SOURCE_COMMIT = "cd974019ddf6b5cae8ee98138cb917de343b009b"
FINAL_MANIFEST = "reports/phase13b_infectious_disease_dependencies_freeze_manifest.json"
WORKING_MANIFEST = "reports/infectious_disease_dependency_manifest.json"
ARTIFACT_CHECK = "reports/infectious_disease_dependency_artifact_check.json"
PHASE13A_MANIFEST = "reports/phase13a_infectious_disease_freeze_manifest.json"
PHASE13A_REVIEW = "reports/infectious_disease_independent_review.md"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yaml", ".yml", ".toml", ".svg"}
REVIEWS = (
    "reports/infectious_disease_dependency_independent_review_initial.md",
    "reports/infectious_disease_dependency_independent_review_second.md",
    "reports/infectious_disease_dependency_independent_review.md",
)
EXPECTED_FINAL_ARTIFACTS = (
    "data/processed/analysis/infectious_disease_dependency_register.csv",
    "data/processed/networks/infectious_disease_dependency_edges.csv",
    "data/processed/analysis/infectious_disease_dependency_matrix.csv",
    "data/processed/analysis/infectious_disease_evidence_crosswalk.csv",
    "data/processed/analysis/infectious_disease_dependency_sources.csv",
    "data/processed/analysis/infectious_disease_dependency_uncertainties.csv",
    "outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.png",
    "outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.svg",
    "reports/infectious_disease_dependency_sources.md",
    "reports/infectious_disease_dependency_assumptions.md",
    "reports/infectious_disease_dependency_findings.md",
    "reports/infectious_disease_dependency_qa.md",
    "reports/phase13b_citation_ledger.json",
    "src/python/systems/build_infectious_disease_dependencies.py",
    "src/python/systems/validate_infectious_disease_dependencies.py",
    "src/R/systems/validate_infectious_disease_dependencies.R",
    "reports/infectious_disease_dependency_manifest.json",
    "reports/infectious_disease_dependency_artifact_check.json",
    "reports/infectious_disease_dependency_independent_review_initial.md",
    "reports/infectious_disease_dependency_independent_review_second.md",
    "reports/infectious_disease_dependency_independent_review.md",
    "docs/phase_briefs/phase13b_infectious_disease_dependencies.md",
    "src/python/systems/validate_phase13b_freeze.py",
    "src/R/systems/validate_phase13b_freeze.R",
)


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    normalized = canonical(raw)
    crlf = normalized.replace(b"\n", b"\r\n")
    candidates = (
        (sha256(raw), len(raw), "exact"),
        (sha256(normalized), len(normalized), "newline-normalized"),
        (sha256(crlf), len(crlf), "newline-normalized"),
    )
    for digest, size, mode in candidates:
        if digest == expected_hash and (expected_bytes is None or int(expected_bytes) == size):
            return mode
    raise AssertionError(f"hash/byte mismatch: {relative}")


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("artifacts", payload.get("files", {}))


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
    expected_hashes: dict[str, str] = {}
    protected: set[str] = set()
    entries = 0
    manifests = []
    for path in sorted((root / "reports").glob("phase*_freeze_manifest.json")):
        if path.name in {
            Path(FINAL_MANIFEST).name,
            Path(PHASE13A_MANIFEST).name,
        }:
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


def verify_phase13a(root: Path) -> dict[str, Any]:
    manifest = load_json(root, PHASE13A_MANIFEST)
    assert manifest["status"] == "ACCEPTED / FROZEN"
    assert manifest["accepted_phase"] == "13A"
    assert manifest["counts"] == {
        "nodes": 38,
        "relationships": 40,
        "observations": 25,
        "surveillance_records": 17,
        "sources": 27,
        "uncertainties": 18,
    }
    assert manifest["phase1_12_immutable"] is True
    assert manifest["phase13b_implemented"] is False
    assert manifest["phase13c_implemented"] is False
    result = verify_artifacts(root, manifest, "Phase 13A final freeze manifest", 25)
    review_text = (root / PHASE13A_REVIEW).read_text(encoding="utf-8")
    assert '"passed": true' in review_text
    assert '"security_concerns": []' in review_text
    return result


def verify_working_package(root: Path) -> dict[str, int]:
    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "13B"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == EXPECTED_COUNTS
    assert working["phase13a_accepted_frozen"] is True
    assert working["phase1_12_immutable"] is True
    assert working["phase13c_implemented"] is False
    result = verify_artifacts(root, working, "Phase 13B working manifest", 18)
    assert working["phase13a_freeze_manifest"]["path"] == PHASE13A_MANIFEST
    verify_hash(root, PHASE13A_MANIFEST, working["phase13a_freeze_manifest"])
    return result


def verify_artifact_check(root: Path) -> None:
    check = load_json(root, ARTIFACT_CHECK)
    assert check["status"] == "passed"
    for key, expected in EXPECTED_COUNTS.items():
        assert check[key] == expected, key
    assert check["phase13a_freeze_artifacts_checked"] == 25
    assert check["prior_freeze_manifest_entries_checked"] == EXPECTED_PRIOR_ENTRIES
    assert check["prior_unique_protected_artifacts_checked"] == EXPECTED_PRIOR_UNIQUE
    assert check["manifest_artifacts_checked"] == 18
    assert check["phase13a_accepted_frozen"] is True
    assert check["phase1_12_immutable"] is True
    assert check["phase13a_immutable"] is True
    assert check["phase13c_not_implemented"] is True
    assert check["phase14_not_implemented"] is True


def verify_reviews(root: Path) -> dict[str, bool]:
    for relative in REVIEWS:
        assert (root / relative).is_file() and (root / relative).stat().st_size > 0, relative
    text = (root / REVIEWS[-1]).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "final independent-review JSON block missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in (
        "security_concerns", "logic_errors", "provenance_errors", "epidemiological_errors",
        "dependency_errors", "surveillance_errors", "spatial_scale_errors", "health_boundary_errors",
    ):
        assert verdict.get(key) == [], key
    return {"passed": True, "initial_review_preserved": True, "second_review_preserved": True, "final_review_preserved": True}


def verify_no_later_phase(root: Path) -> None:
    for base in (root / "data/processed", root / "outputs/maps/systems", root / "src/python/systems", root / "src/R/systems"):
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root)).replace("\\", "/").lower()
            name = path.name.lower()
            assert "phase13c" not in relative and "phase14" not in relative, relative
            assert "infectious_disease_futures" not in name, relative
            assert not name.startswith(("43_", "44_")), relative


def verify_status_surfaces(root: Path) -> None:
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in ("phase 13a", "accepted / frozen", "phase 13b", "not implemented", "phase 13c", "active phase", "none", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"):
            assert term in text, (relative, term)
    # The Phase 13B brief is a protected Phase 13A input and is checked by the Phase 13A manifest.
    handoff = (root / "reports/current_phase_handoff.md").read_text(encoding="utf-8").lower()
    marker = handoff.rfind("## phase 13b final acceptance / freeze handoff")
    assert marker >= 0
    current = handoff[marker:]
    assert ("phase 13b **accepted / frozen**" in current or "phase 13b: **accepted / frozen**" in current)
    assert ("phase 13c **approved scope / not implemented**" in current or "phase 13c: **approved scope / not implemented**" in current)
    assert "active phase **none**" in current or "active phase: **none**" in current


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "13B"
    assert final["baseline"] == "Environmental & Human-System Transmission Dependencies, 2026"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-10"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["phase13a_freeze_manifest"]["path"] == PHASE13A_MANIFEST
    assert final["phase13a_accepted_frozen"] is True
    assert final["phase1_12_immutable"] is True
    assert final["phase13c_implemented"] is False
    assert final["phase14_implemented"] is False
    assert final["composite_disease_risk_index"] is False
    assert final["individual_case_or_risk_map"] is False
    assert final["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    assert final["deferred_maintenance_preserved"] == [
        "Phase 6B manifest status wording mismatch",
        "Phase 3A missing manifest status",
    ]
    final_result = verify_artifacts(root, final, "Phase 13B final freeze manifest", len(EXPECTED_FINAL_ARTIFACTS))
    assert tuple(artifact_entries(final)) == EXPECTED_FINAL_ARTIFACTS

    working_result = verify_working_package(root)
    verify_artifact_check(root)
    phase13a_result = verify_phase13a(root)
    prior = verify_prior_system(root)
    review = verify_reviews(root)
    verify_no_later_phase(root)
    verify_status_surfaces(root)

    result = {
        "status": "passed",
        "phase": "13B",
        "freeze_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": working_result,
        "phase13a_integrity": {"final_artifacts": phase13a_result["entries"]},
        "prior_system_immutability": prior,
        "review_history": review,
        "counts": EXPECTED_COUNTS,
        "active_holds_preserved": True,
        "deferred_maintenance_preserved": True,
        "phase13c_14_not_implemented": True,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
