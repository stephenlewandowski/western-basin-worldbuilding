#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 13A."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "nodes": 38,
    "relationships": 40,
    "observations": 25,
    "surveillance_records": 17,
    "sources": 27,
    "uncertainties": 18,
}
EXPECTED_PRIOR_ENTRIES = 358
EXPECTED_PRIOR_UNIQUE = 351
SOURCE_COMMIT = "c07be966e5058e299be21d181754920e41e5321b"
WORKING_MANIFEST = "reports/infectious_disease_baseline_manifest.json"
FINAL_MANIFEST = "reports/phase13a_infectious_disease_freeze_manifest.json"
ARTIFACT_CHECK = "reports/infectious_disease_artifact_check.json"
PHASE12_MANIFESTS = {
    "12A": "reports/phase12a_vector_ecology_freeze_manifest.json",
    "12B": "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
    "12C": "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
}
TEXT_SUFFIXES = {
    ".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yaml", ".yml", ".toml", ".svg",
}
REVIEW = "reports/infectious_disease_independent_review.md"
INITIAL_REVIEW = "reports/infectious_disease_independent_review_initial.md"


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
    candidates = [(sha256(raw), len(raw), "exact"), (sha256(normalized), len(normalized), "newline-normalized")]
    if path.suffix in TEXT_SUFFIXES:
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.append((sha256(crlf), len(crlf), "newline-normalized"))
    for digest, size, mode in candidates:
        if digest == expected_hash and (expected_bytes is None or int(expected_bytes) == size or (path.suffix in TEXT_SUFFIXES and int(expected_bytes) in {len(raw), len(normalized), len(crlf)})):
            return mode
    raise AssertionError(f"hash/byte mismatch: {relative}")


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("artifacts", payload.get("files", {}))


def verify_artifacts(root: Path, payload: dict[str, Any], label: str, expected_count: int | None = None) -> dict[str, int]:
    artifacts = artifact_entries(payload)
    assert artifacts, f"{label}: no artifacts"
    if expected_count is not None:
        assert len(artifacts) == expected_count, f"{label}: artifact count"
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
        if path.name == Path(FINAL_MANIFEST).name:
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
    text = (root / REVIEW).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "final independent-review JSON block missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    blocking = (
        "security_concerns", "logic_errors", "provenance_errors", "epidemiological_errors",
        "surveillance_errors", "spatial_scale_errors", "health_boundary_errors",
    )
    for key in blocking:
        assert verdict.get(key) == [], key
    assert (root / INITIAL_REVIEW).is_file()
    return {"passed": True, "blocking_arrays_empty": True, "initial_review_preserved": True}


def verify_no_later_phase(root: Path) -> None:
    for base in (root / "data/processed", root / "outputs/maps/systems", root / "src/python/systems", root / "src/R/systems"):
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root)).replace("\\", "/").lower()
            name = path.name.lower()
            assert "phase13b" not in relative and "phase13c" not in relative, relative
            assert "infectious_disease_dependencies" not in name and "infectious_disease_futures" not in name, relative
            assert not name.startswith(("42_", "43_")), relative


def verify_status_surfaces(root: Path) -> None:
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in ("phase 13a", "accepted / frozen", "phase 13b", "not implemented", "phase 13c", "active phase", "none", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"):
            assert term in text, (relative, term)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "13A"
    assert final["baseline"] == "Infectious Disease System Baseline, 2026"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-09"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["protected_inputs"] == list(PHASE12_MANIFESTS.values())
    assert final["phase12abc_accepted_frozen"] is True
    assert final["phase1_12_immutable"] is True
    assert final["phase13b_implemented"] is False and final["phase13c_implemented"] is False
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
    final_result = verify_artifacts(root, final, "Phase 13A final freeze manifest", 25)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "13A"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == EXPECTED_COUNTS
    assert working["phase12abc_accepted_frozen"] is True
    assert working["phase1_12_immutable"] is True
    working_result = verify_artifacts(root, working, "Phase 13A working manifest", 21)

    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["status"] == "passed"
    for key, expected in EXPECTED_COUNTS.items():
        assert artifact_check[key] == expected, key
    assert artifact_check["prior_freeze_manifest_entries_checked"] == EXPECTED_PRIOR_ENTRIES
    assert artifact_check["prior_unique_protected_artifacts_checked"] == EXPECTED_PRIOR_UNIQUE
    assert artifact_check["phase12abc_accepted_frozen"] is True
    assert artifact_check["active_holds_preserved"] is True

    phase12_results: dict[str, dict[str, int]] = {}
    for phase, relative in PHASE12_MANIFESTS.items():
        manifest = load_json(root, relative)
        assert manifest["status"] == "ACCEPTED / FROZEN"
        phase12_results[phase] = verify_artifacts(root, manifest, f"Phase {phase} final freeze manifest", {"12A": 17, "12B": 15, "12C": 28}[phase])
    phase12b = load_json(root, PHASE12_MANIFESTS["12B"])
    phase12a = load_json(root, PHASE12_MANIFESTS["12A"])
    assert phase12b["phase12a_freeze_manifest"]["path"] == PHASE12_MANIFESTS["12A"]
    verify_hash(root, PHASE12_MANIFESTS["12A"], phase12b["phase12a_freeze_manifest"])
    assert phase12a["status"] == "ACCEPTED / FROZEN"
    phase12c = load_json(root, PHASE12_MANIFESTS["12C"])
    assert phase12c["phase12a_12b_immutable"] is True
    assert phase12c["phase13_implemented"] is False

    prior = verify_prior_system(root)
    review = verify_review(root)
    verify_no_later_phase(root)
    verify_status_surfaces(root)

    result = {
        "status": "passed",
        "phase": "13A",
        "freeze_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": working_result,
        "phase12_integrity": phase12_results,
        "prior_phase1_12": prior,
        "review": review,
        "counts": EXPECTED_COUNTS,
        "active_holds_preserved": True,
        "deferred_maintenance_preserved": True,
        "phase13b_13c_not_implemented": True,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
