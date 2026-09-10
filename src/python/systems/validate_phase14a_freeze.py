#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 14A."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

FINAL_MANIFEST = "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase14a_manifest.json"
ARTIFACT_CHECK = "reports/phase14a_artifact_check.json"
REVIEW = "reports/phase14a_independent_review.md"
SOURCE_COMMIT = "d89a80f6dd883f2cc9d89e3c89396e1b5f468700"
EXPECTED_PRIOR_ENTRIES = 488
EXPECTED_PRIOR_UNIQUE = 479
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yaml", ".yml", ".svg", ".toml"}
EXPECTED_COUNTS = {
    "systems": 13,
    "identity_rows": 456,
    "endpoint_rows": 36,
    "conceptual_dependency_rows": 25,
    "total_dependencies": 36,
    "resolved_exact": 0,
    "resolved_system_level": 34,
    "retained_conceptual": 2,
    "unresolved": 0,
    "relationship_rows": 367,
    "evidence_classes": 8,
    "evidence_mappings": 17,
    "figure": {
        "systems": 13,
        "interfaces": 12,
        "png": "outputs/figures/western_basin_systems_architecture.png",
        "svg": "outputs/figures/western_basin_systems_architecture.svg",
    },
}
BASE_ARTIFACTS = [
    "metadata/atlas_systems.yml",
    "metadata/atlas_evidence_vocabulary.yml",
    "docs/phase_briefs/phase14_systems_atlas_integration.md",
    "docs/phase_briefs/phase14a_common_systems_ontology_identity_evidence_crosswalk.md",
    "docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md",
    "data/processed/integration/system_identity_crosswalk.csv",
    "data/processed/integration/external_endpoint_crosswalk.csv",
    "data/processed/integration/relationship_taxonomy_inventory.csv",
    "outputs/figures/western_basin_systems_architecture.png",
    "outputs/figures/western_basin_systems_architecture.svg",
    "reports/phase14a_systems_ontology.md",
    "reports/phase14a_identity_crosswalk.md",
    "reports/phase14a_evidence_crosswalk.md",
    "reports/phase14a_relationship_taxonomy.md",
    "reports/phase14a_integration_qa.md",
    "reports/phase14a_build_summary.json",
    "src/python/systems/build_phase14a_integration.py",
    "src/python/systems/validate_phase14a_integration.py",
    "src/R/systems/validate_phase14a_integration.R",
]
EXPECTED_WORKING_ARTIFACTS = sorted(BASE_ARTIFACTS)
EXPECTED_FINAL_ARTIFACTS = EXPECTED_WORKING_ARTIFACTS + [
    ARTIFACT_CHECK,
    REVIEW,
    WORKING_MANIFEST,
    "src/python/systems/validate_phase14a_freeze.py",
    "src/R/systems/validate_phase14a_freeze.R",
]
BLOCKING_REVIEW_ARRAYS = (
    "security_concerns",
    "logic_errors",
    "provenance_errors",
    "ontology_errors",
    "identity_errors",
    "evidence_classification_errors",
    "relationship_taxonomy_errors",
    "canon_boundary_errors",
)


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("artifacts", payload.get("files", {}))
    if not isinstance(entries, dict):
        raise AssertionError("manifest artifact collection is not an object")
    return entries


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_hashes(data: bytes) -> tuple[tuple[str, int], ...]:
    normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = normalized.replace(b"\n", b"\r\n")
    return ((digest(data), len(data)), (digest(normalized), len(normalized)), (digest(crlf), len(crlf)))


def verify_hash(root: Path, relative: str, expected: dict[str, Any] | str) -> str:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing protected artifact: {relative}"
    expected_hash = expected if isinstance(expected, str) else str(expected["sha256"])
    expected_bytes = None if isinstance(expected, str) else expected.get("bytes")
    candidates = portable_hashes(path.read_bytes()) if path.suffix in TEXT_SUFFIXES else ((digest(path.read_bytes()), path.stat().st_size),)
    for candidate_hash, candidate_bytes in candidates:
        if candidate_hash == expected_hash and (expected_bytes is None or int(expected_bytes) == candidate_bytes):
            return "exact" if candidate_hash == digest(path.read_bytes()) else "newline-normalized"
    raise AssertionError(f"hash/byte mismatch: {relative}")


def verify_manifest(root: Path, relative: str, expected_count: int, expected_inventory: list[str] | None = None) -> dict[str, int]:
    payload = load_json(root, relative)
    entries = artifact_entries(payload)
    assert len(entries) == expected_count, f"{relative}: artifact count {len(entries)}"
    if expected_inventory is not None:
        assert list(entries) == expected_inventory, f"{relative}: artifact inventory differs"
    exact = 0
    normalized = 0
    for path, metadata in entries.items():
        if verify_hash(root, path, metadata) == "exact":
            exact += 1
        else:
            normalized += 1
    return {"entries": len(entries), "exact": exact, "newline_normalized": normalized}


def verify_prior_freezes(root: Path) -> dict[str, int]:
    final_name = Path(FINAL_MANIFEST).name
    entries = 0
    protected: set[str] = set()
    errors: list[str] = []
    manifests = []
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        manifests.append(path.name)
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in artifact_entries(payload).items():
            entries += 1
            protected.add(relative)
            try:
                verify_hash(root, relative, metadata)
            except AssertionError as exc:
                errors.append(str(exc))
    assert not errors, errors[:10]
    assert entries == EXPECTED_PRIOR_ENTRIES, entries
    assert len(protected) == EXPECTED_PRIOR_UNIQUE, len(protected)
    changed = set(subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return {"manifest_count": len(manifests), "entries": entries, "unique": len(protected)}


def verify_review(root: Path) -> dict[str, Any]:
    text = (root / REVIEW).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "Phase 14A review JSON block missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in BLOCKING_REVIEW_ARRAYS:
        assert verdict.get(key) == [], key
    return {"passed": True, "blocking_arrays_empty": True, "review_id": "deleg_aa6daf99"}


def require_terms(root: Path, relative: str, terms: tuple[str, ...]) -> None:
    text = (root / relative).read_text(encoding="utf-8").lower()
    for term in terms:
        assert term.lower() in text, f"status surface {relative}: missing {term}"


def verify_status_surfaces(root: Path) -> None:
    common = (
        "phase 14a",
        "accepted / frozen",
        FINAL_MANIFEST,
        "active phase",
        "phase 14b",
        "approved scope / not implemented",
        "phase 15",
        "not implemented",
        "great black swamp",
        "hold",
        "toledo intake-coordinate discrepancy",
        "unresolved",
        "phase 6b",
        "phase 3a",
        "phase 2a",
        "no release or tag",
    )
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md"):
        require_terms(root, relative, common)


def verify_scope(root: Path) -> None:
    changed = set(subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert "metadata/systems.yml" not in changed
    assert not any(path.endswith(".gpkg") for path in changed)
    forbidden = [
        path for path in changed
        if ("phase14b" in path.lower() and path != "docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md")
        or "phase15" in path.lower()
    ]
    assert not forbidden, forbidden
    assert not any(path.startswith("data/processed/integration/atlas_layer") for path in changed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]
    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "14A"
    assert final["baseline"] == "Common Systems Ontology, Identity & Evidence Crosswalk"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-10"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["phase1_13_immutable"] is True
    assert final["phase14b_implemented"] is False
    assert final["phase15_implemented"] is False
    assert final["release_created"] is False
    assert final["tag_created"] is False
    assert final["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    assert final["deferred_maintenance_preserved"] == [
        "Phase 6B manifest status wording mismatch",
        "Phase 3A missing manifest status",
        "Phase 2A superseded legacy worktree",
    ]
    assert FINAL_MANIFEST not in artifact_entries(final)
    final_result = verify_manifest(root, FINAL_MANIFEST, len(EXPECTED_FINAL_ARTIFACTS), EXPECTED_FINAL_ARTIFACTS)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "14A"
    assert working["status"] == "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE"
    assert working["counts"] == EXPECTED_COUNTS
    working_result = verify_manifest(root, WORKING_MANIFEST, len(EXPECTED_WORKING_ARTIFACTS), EXPECTED_WORKING_ARTIFACTS)

    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["passed"] is True
    assert artifact_check["counts"]["systems"] == 13
    assert artifact_check["counts"]["identity_rows"] == 456
    assert artifact_check["counts"]["endpoint_rows"] == 36
    assert artifact_check["counts"]["relationship_rows"] == 367
    assert artifact_check["counts"]["evidence_classes"] == 8
    assert artifact_check["counts"]["system_level_resolved"] == 34
    assert artifact_check["counts"]["retained_conceptual"] == 2
    assert artifact_check["counts"]["unresolved"] == 0

    prior = verify_prior_freezes(root)
    review = verify_review(root)
    verify_status_surfaces(root)
    verify_scope(root)

    print(json.dumps({
        "status": "passed",
        "phase": "14A",
        "freeze_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": {"path": WORKING_MANIFEST, **working_result},
        "prior_system_immutability": prior,
        "review": review,
        "counts": EXPECTED_COUNTS,
        "active_holds_preserved": True,
        "deferred_maintenance_preserved": True,
        "phase14b_implemented": False,
        "phase15_implemented": False,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
