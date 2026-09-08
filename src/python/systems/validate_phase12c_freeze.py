#!/usr/bin/env python3
"""Independent freeze-boundary validation for the accepted Phase 12C package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "scenario_assumptions": 36,
    "vector_states": 36,
    "habitat_states": 48,
    "surveillance_states": 30,
    "dependency_states": 168,
    "uncertainty_states": 60,
    "scenario_sources": 28,
    "comparison_rows": 6,
}
EXPECTED_PRIOR_ENTRIES = 298
EXPECTED_PRIOR_UNIQUE = 293
PHASE12A_MANIFEST = "reports/phase12a_vector_ecology_freeze_manifest.json"
PHASE12B_MANIFEST = "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json"
PHASE12C_MANIFEST = "reports/phase12c_vector_ecology_futures_freeze_manifest.json"
WORKING_MANIFEST = "reports/vector_ecology_future_manifest.json"
ARTIFACT_CHECK = "reports/vector_ecology_future_artifact_check.json"

TEXT_SUFFIXES = {
    ".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yaml", ".yml", ".toml",
    ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".svg", ".xml",
}


def load_json(root: Path, rel: str) -> dict[str, Any]:
    with (root / rel).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def raw_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_digest(data: bytes) -> str:
    return raw_digest(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))


def verify_hash(root: Path, rel: str, expected: dict[str, Any] | str) -> str:
    path = root / rel
    assert path.is_file(), f"missing protected artifact: {rel}"
    data = path.read_bytes()
    if isinstance(expected, str):
        expected_hash = expected
        expected_bytes = None
    else:
        expected_hash = expected.get("sha256")
        expected_bytes = expected.get("bytes")
    raw_hash = raw_digest(data)
    if raw_hash == expected_hash and (expected_bytes is None or len(data) == expected_bytes):
        return "exact"
    if path.suffix in TEXT_SUFFIXES and normalized_digest(data) == expected_hash:
        normalized_len = len(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
        assert expected_bytes in (None, len(data), normalized_len), f"byte mismatch: {rel}"
        return "newline-normalized"
    raise AssertionError(f"hash/byte mismatch: {rel}")


def verify_artifacts(root: Path, manifest: dict[str, Any], label: str) -> dict[str, int]:
    exact = 0
    normalized = 0
    artifacts = manifest.get("artifacts", {})
    assert artifacts, f"{label}: no artifacts"
    for rel, expected in artifacts.items():
        mode = verify_hash(root, rel, expected)
        if mode == "exact":
            exact += 1
        else:
            normalized += 1
    return {"entries": len(artifacts), "exact": exact, "newline_normalized": normalized}


def prior_manifests(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name not in {Path(PHASE12A_MANIFEST).name, Path(PHASE12B_MANIFEST).name, Path(PHASE12C_MANIFEST).name}:
            found.append(path)
    return found


def verify_prior_system(root: Path) -> dict[str, int]:
    manifests = prior_manifests(root)
    entries: list[str] = []
    normalized = 0
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        for rel, expected in data.get("artifacts", data.get("files", {})).items():
            entries.append(rel)
            if verify_hash(root, rel, expected) == "newline-normalized":
                normalized += 1
    unique = len(set(entries))
    assert len(entries) == EXPECTED_PRIOR_ENTRIES, len(entries)
    assert unique == EXPECTED_PRIOR_UNIQUE, unique
    return {
        "manifest_count": len(manifests),
        "entries": len(entries),
        "unique": unique,
        "newline_normalized": normalized,
    }


def review_verdict(root: Path) -> dict[str, Any]:
    text = (root / "reports/vector_ecology_future_independent_review.md").read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "final Phase 12C review JSON block missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    blocking = (
        "security_concerns", "logic_errors", "provenance_errors", "ecological_errors",
        "scenario_boundary_errors", "spatial_scale_errors", "health_boundary_errors",
    )
    for key in blocking:
        assert verdict.get(key) == [], key
    assert (root / "reports/vector_ecology_future_independent_review_initial.md").is_file()
    return {"passed": True, "blocking_arrays_empty": True, "initial_review_preserved": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None, help="repository root")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    freeze = load_json(root, PHASE12C_MANIFEST)
    assert freeze["accepted_phase"] == "12C"
    assert freeze["status"] == "ACCEPTED / FROZEN"
    assert freeze["protected_inputs"] == [PHASE12A_MANIFEST, PHASE12B_MANIFEST, WORKING_MANIFEST]
    assert freeze["phase12a_12b_immutable"] is True
    assert freeze["phase1_11_immutable"] is True
    assert freeze["phase13_implemented"] is False
    assert freeze["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    assert freeze["counts"] == EXPECTED_COUNTS
    freeze_result = verify_artifacts(root, freeze, "Phase 12C final freeze manifest")

    working = load_json(root, WORKING_MANIFEST)
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["counts"] == EXPECTED_COUNTS
    working_result = verify_artifacts(root, working, "Phase 12C working manifest")

    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["status"] == "passed"
    for key, expected in EXPECTED_COUNTS.items():
        assert artifact_check[key] == expected, key
    assert artifact_check["prior_phase1_11_manifest_entries"] == EXPECTED_PRIOR_ENTRIES
    assert artifact_check["prior_phase1_11_unique_protected_artifacts"] == EXPECTED_PRIOR_UNIQUE
    assert artifact_check["phase12a_12b_freeze_integrity"] is True
    assert artifact_check["phase12a_12b_immutable"] is True
    assert artifact_check["active_holds_preserved"] is True
    assert artifact_check["independent_review_passed"] is True

    phase12a = load_json(root, PHASE12A_MANIFEST)
    phase12b = load_json(root, PHASE12B_MANIFEST)
    assert phase12a["status"] == "ACCEPTED / FROZEN"
    assert phase12b["status"] == "ACCEPTED / FROZEN"
    a_result = verify_artifacts(root, phase12a, "Phase 12A final freeze manifest")
    b_result = verify_artifacts(root, phase12b, "Phase 12B final freeze manifest")
    assert phase12b["phase12a_freeze_manifest"]["path"] == PHASE12A_MANIFEST
    assert verify_hash(root, PHASE12A_MANIFEST, phase12b["phase12a_freeze_manifest"]) in {"exact", "newline-normalized"}

    prior_result = verify_prior_system(root)
    review = review_verdict(root)
    forbidden = [p for p in freeze["artifacts"] if "phase13" in p.lower()]
    assert not forbidden

    result = {
        "status": "passed",
        "phase": "12C",
        "freeze_manifest": {"path": PHASE12C_MANIFEST, **freeze_result},
        "working_manifest": working_result,
        "phase12a": a_result,
        "phase12b": b_result,
        "prior_phase1_11": prior_result,
        "review": review,
        "counts": EXPECTED_COUNTS,
        "phase12a_12b_immutable": True,
        "active_holds_preserved": True,
        "phase13_implemented": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
