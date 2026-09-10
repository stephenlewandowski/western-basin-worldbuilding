#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 7C."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SOURCE_COMMIT = "39d9c97ebab0dad736188a320dc037a602e5f594"
FINAL_MANIFEST = "reports/phase7c_environmental_health_futures_freeze_manifest.json"
SIBLING_FINAL_MANIFEST = "reports/phase7b_exposure_dependencies_controls_freeze_manifest.json"
WORKING_MANIFEST = "reports/environmental_health_scenario_manifest.json"
ARTIFACT_CHECK = "reports/environmental_health_scenario_artifact_check.json"
STRICT_CHECK = "reports/phase7c_strict_provenance_check.json"
PHASE7A_MANIFEST = "reports/phase7a_exposure_environmental_health_freeze_manifest.json"
REVIEW_INITIAL = "reports/phase7c_exposure_futures_independent_review_initial.md"
REVIEW_FINAL = "reports/phase7c_exposure_futures_independent_review.md"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".txt", ".yaml", ".yml", ".toml", ".svg"}
EXPECTED_PRIOR_ENTRIES = 435
EXPECTED_PRIOR_UNIQUE = 426
EXPECTED_PACKAGE_ARTIFACTS = (
    "data/processed/scenarios/environmental_health_scenario_assumptions.csv",
    "data/processed/scenarios/exposure_nodes_scenario.csv",
    "data/processed/scenarios/exposure_edges_scenario.csv",
    "data/processed/scenarios/exposure_controls_scenario.csv",
    "data/processed/scenarios/exposure_uncertainty_scenario.csv",
    "outputs/figures/environmental_health_scenarios_comparison.csv",
    "outputs/figures/environmental_health_scenarios_comparison.png",
    "outputs/maps/systems/25_environmental_health_futures_2050.png",
    "outputs/maps/systems/25_environmental_health_futures_2050.svg",
    "outputs/maps/systems/25b_environmental_health_futures_2075.png",
    "outputs/maps/systems/25b_environmental_health_futures_2075.svg",
    "reports/environmental_health_scenario_sources.md",
    "reports/environmental_health_scenario_assumptions.md",
    "reports/environmental_health_scenario_consistency.md",
    "reports/environmental_health_future_worldbuilding.md",
    "reports/environmental_health_scenario_qa.md",
    "reports/phase7c_citation_ledger.json",
    "reports/phase7c_strict_provenance.md",
    STRICT_CHECK,
    "src/python/systems/build_environmental_health_futures.py",
    "src/python/systems/validate_environmental_health_futures.py",
    "src/R/systems/validate_environmental_health_futures.R",
    WORKING_MANIFEST,
    ARTIFACT_CHECK,
    REVIEW_INITIAL,
    REVIEW_FINAL,
    "docs/phase_briefs/phase7c_environmental_health_futures.md",
    "src/python/systems/validate_phase7c_freeze.py",
    "src/R/systems/validate_phase7c_freeze.R",
)


def canonical_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("artifacts", payload.get("files", {}))


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_hash(root: Path, relative: str, expected: dict[str, Any] | str) -> str:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing artifact: {relative}"
    expected_hash = expected if isinstance(expected, str) else str(expected["sha256"])
    expected_bytes = None if isinstance(expected, str) else expected.get("bytes")
    raw = path.read_bytes()
    candidates = [(sha256(raw), len(raw), "exact")]
    if path.suffix.lower() in TEXT_SUFFIXES:
        normalized = canonical_text(raw)
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.extend(
            [
                (sha256(normalized), len(normalized), "newline-normalized"),
                (sha256(crlf), len(crlf), "newline-normalized"),
            ]
        )
    for digest, size, mode in candidates:
        if digest == expected_hash and (expected_bytes is None or int(expected_bytes) == size):
            return mode
    raise AssertionError(f"hash/byte mismatch: {relative}")


def verify_artifacts(root: Path, payload: dict[str, Any], label: str, expected: tuple[str, ...] | None = None, count: int | None = None) -> dict[str, int]:
    artifacts = artifact_entries(payload)
    assert artifacts, f"{label}: no artifacts"
    if expected is not None:
        assert tuple(artifacts) == expected, f"{label}: artifact inventory"
    if count is not None:
        assert len(artifacts) == count, f"{label}: artifact count"
    exact = 0
    normalized = 0
    for relative, metadata in artifacts.items():
        mode = verify_hash(root, relative, metadata)
        if mode == "exact":
            exact += 1
        else:
            normalized += 1
    return {"entries": len(artifacts), "exact": exact, "newline_normalized": normalized}


def read_csv(root: Path, relative: str) -> list[dict[str, str]]:
    with (root / relative).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, relative
    return rows


def check_png(root: Path, relative: str) -> None:
    data = (root / relative).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", relative
    assert len(data) > 100, relative
    assert data[12:16] == b"IHDR", relative
    width, height = struct.unpack(">II", data[16:24])
    assert width > 0 and height > 0, relative


def check_svg(root: Path, relative: str, required: tuple[str, ...]) -> None:
    parsed = ET.parse(root / relative)
    text = " ".join(parsed.getroot().itertext())
    for term in required:
        assert term in text, (relative, term)


def verify_phase7a(root: Path) -> dict[str, int]:
    manifest = load_json(root, PHASE7A_MANIFEST)
    assert manifest["accepted_phase"] == "7A"
    assert manifest["status"] == "ACCEPTED / FROZEN"
    assert manifest["counts"] == {
        "nodes": 20,
        "edges": 20,
        "pathway_register": 5,
        "monitoring_matrix_rows": 5,
        "evidence_crosswalk": 10,
        "uncertainty_register": 13,
    }
    return verify_artifacts(root, manifest, "Phase 7A final freeze manifest")


def verify_phase7b(root: Path) -> dict[str, int]:
    manifest = load_json(root, SIBLING_FINAL_MANIFEST)
    assert manifest["accepted_phase"] == "7B"
    assert manifest["status"] == "ACCEPTED / FROZEN"
    assert manifest["counts"] == {
        "dependency_edges": 20,
        "controls": 7,
        "evidence_rows": 5,
        "matrix_semantic_shape": [5, 10],
        "matrix_stored_shape": [5, 11],
    }
    result = verify_artifacts(root, manifest, "Phase 7B final freeze manifest", count=24)
    assert manifest["phase7a_immutable"] is True
    return result


def verify_package(root: Path) -> dict[str, Any]:
    assumptions = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[0])
    nodes = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[1])
    edges = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[2])
    controls = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[3])
    uncertainty = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[4])
    comparison = read_csv(root, EXPECTED_PACKAGE_ARTIFACTS[5])
    assert (len(assumptions), len(nodes), len(edges), len(controls), len(uncertainty), len(comparison)) == (36, 30, 30, 30, 30, 6)
    assert {row["scenario_id"] for row in assumptions} == {"A", "B", "C"}
    assert {row["scenario_year"] for row in assumptions} == {"2050", "2075"}
    expected_family = {
        "P-01": "Drinking Water / HAB",
        "P-02": "Ambient Air",
        "P-03": "Soil / Groundwater / Legacy Contamination",
        "P-04": "Food / Fish / Recreational Water",
        "P-05": "Heat",
    }
    expected_control = {
        "Drinking Water / HAB": "CTL-001",
        "Ambient Air": "CTL-003",
        "Soil / Groundwater / Legacy Contamination": "CTL-004",
        "Food / Fish / Recreational Water": "CTL-005",
        "Heat": "CTL-007",
    }
    assert all(row["pathway_family"] == expected_family[row["baseline_object_id"]] and row["uncertainty"] == "moderate" for row in nodes + edges)
    assert all(row["pathway_family"] == expected_family[row["baseline_object_id"]] and row["uncertainty"] == "moderate" for row in edges)
    assert all(row["baseline_control_id"] == expected_control[row["pathway_family"]] and row["uncertainty"] == "moderate" for row in controls)
    assert all(row["uncertainty"] == "moderate" for row in uncertainty)
    assert all(row["pathway_family"] == "All pathways" and row["change_type"] == "scenario_comparison" and row["assumption_id"].endswith("-06") and row["uncertainty"] in {"high", "moderate", "low"} for row in comparison)
    assumption_ids = {row["assumption_id"] for row in assumptions}
    assert all(row["assumption_id"] in assumption_ids for rows in (nodes, edges, controls, uncertainty, comparison) for row in rows)
    assert all(row["reality_status"] == "fictional" for row in nodes)
    for relative, required in (
        ("outputs/maps/systems/25_environmental_health_futures_2050.svg", ("ENVIRONMENTAL HEALTH FUTURES", "2050")),
        ("outputs/maps/systems/25b_environmental_health_futures_2075.svg", ("ENVIRONMENTAL HEALTH FUTURES", "2075")),
    ):
        check_svg(root, relative, required)
    check_png(root, "outputs/maps/systems/25_environmental_health_futures_2050.png")
    check_png(root, "outputs/maps/systems/25b_environmental_health_futures_2075.png")
    return {
        "assumptions": 36,
        "scenario_nodes": 30,
        "scenario_edges": 30,
        "control_states": 30,
        "uncertainty_states": 30,
        "comparison_rows": 6,
    }


def verify_working_manifest(root: Path) -> dict[str, int]:
    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "7C"
    assert working["counts"] == {
        "assumptions": 36,
        "scenario_nodes": 30,
        "scenario_edges": 30,
        "control_states": 30,
        "uncertainty_states": 30,
        "comparison_rows": 6,
    }
    return verify_artifacts(root, working, "Phase 7C working manifest", EXPECTED_PACKAGE_ARTIFACTS[:11])


def verify_review(root: Path) -> dict[str, bool]:
    initial = (root / REVIEW_INITIAL).read_text(encoding="utf-8")
    assert '"passed": false' in initial
    final = (root / REVIEW_FINAL).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", final, flags=re.S)
    assert match, "final review JSON missing"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in ("security_concerns", "logic_errors", "provenance_errors", "scenario_boundary_errors", "exposure_boundary_errors", "spatial_scale_errors", "schema_errors"):
        assert verdict.get(key) == [], key
    return {"passed": True, "blocking_arrays_empty": True, "initial_review_preserved": True, "final_review_preserved": True}


def verify_artifact_check(root: Path) -> None:
    check = load_json(root, ARTIFACT_CHECK)
    assert check == {
        "status": "passed",
        "phase": "7C",
        "assumptions": 36,
        "scenario_nodes": 30,
        "scenario_edges": 30,
        "control_states": 30,
        "uncertainty_states": 30,
        "comparison_rows": 6,
        "maps_25_25b_valid": True,
        "qualitative_only": True,
        "baseline_separation": True,
    }
    strict = load_json(root, STRICT_CHECK)
    assert strict["status"] == "passed" and strict["phase"] == "7C"
    assert strict["working_manifest_hashes_match"] is True
    assert strict["unsupported_exact_health_outcome_claims"] is False
    assert strict["unsupported_future_exposure_predictions"] is False
    assert strict["unsupported_risk_scoring"] is False


def verify_prior_system(root: Path) -> dict[str, int]:
    excluded = {Path(FINAL_MANIFEST).name, Path(SIBLING_FINAL_MANIFEST).name}
    protected: set[str] = set()
    entries = 0
    manifests = []
    for path in sorted((root / "reports").glob("phase*_freeze_manifest.json")):
        if path.name in excluded:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        manifests.append(path.name)
        for relative, metadata in artifact_entries(payload).items():
            verify_hash(root, relative, metadata)
            protected.add(relative)
            entries += 1
    assert len(manifests) == 29, len(manifests)
    assert entries == EXPECTED_PRIOR_ENTRIES, entries
    assert len(protected) == EXPECTED_PRIOR_UNIQUE, len(protected)
    changed = set(subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return {"manifest_count": len(manifests), "entries": entries, "unique": len(protected)}


def verify_status_surfaces(root: Path) -> None:
    terms = {
        "PROJECT_STATUS.md": (
            "## phase 7b — accepted / frozen",
            "## phase 7c — accepted / frozen",
            FINAL_MANIFEST.lower(),
            SIBLING_FINAL_MANIFEST.lower(),
            "active phase: **none**",
            "phase 14 is not implemented",
            "next approved planning target",
            "great black swamp",
            "hold",
            "noncanonical",
            "intake-coordinate discrepancy",
            "unresolved",
        ),
        "docs/canon_status.md": (
            "phase 7b is **accepted / frozen**",
            "phase 7c is **accepted / frozen**",
            FINAL_MANIFEST.lower(),
            SIBLING_FINAL_MANIFEST.lower(),
            "active phase: **none**",
            "phase 14 is not implemented",
            "next approved planning target",
            "great black swamp",
            "hold",
            "noncanonical",
            "intake-coordinate discrepancy",
            "unresolved",
        ),
        "reports/current_phase_handoff.md": (
            "## phase 7b/7c final acceptance / freeze handoff",
            "phase 7b: **accepted / frozen**",
            "phase 7c: **accepted / frozen**",
            FINAL_MANIFEST.lower(),
            SIBLING_FINAL_MANIFEST.lower(),
            "active phase: **none**",
            "phase 14 is not implemented",
            "next approved planning target",
            "great black swamp",
            "hold",
            "noncanonical",
            "intake-coordinate discrepancy",
            "unresolved",
        ),
        "README.md": (
            "phase 7b is **accepted / frozen**",
            "phase 7c is **accepted / frozen**",
            FINAL_MANIFEST.lower(),
            SIBLING_FINAL_MANIFEST.lower(),
            "phase 14 is not implemented",
        ),
        "reports/README.md": (
            "phase 7b is **accepted / frozen**",
            "phase 7c is **accepted / frozen**",
            Path(FINAL_MANIFEST).name.lower(),
            Path(SIBLING_FINAL_MANIFEST).name.lower(),
        ),
        "CHANGELOG.md": (
            "sol formally accepted and froze phase 7b",
            "sol formally accepted and froze phase 7c",
            FINAL_MANIFEST.lower(),
            SIBLING_FINAL_MANIFEST.lower(),
            "active phase is none",
            "phase 14 is not implemented",
        ),
        "docs/phase_briefs/phase7b_exposure_dependencies_controls.md": (
            "status: accepted / frozen",
            "phase7b_exposure_dependencies_controls_freeze_manifest.json",
        ),
        "docs/phase_briefs/phase7c_environmental_health_futures.md": (
            "status: accepted / frozen",
            FINAL_MANIFEST.lower(),
        ),
    }
    for relative, required in terms.items():
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in required:
            assert term in text, (relative, term)


def verify_no_phase14(root: Path) -> None:
    for base in (root / "data/processed", root / "outputs/maps/systems", root / "src/python/systems", root / "src/R/systems"):
        for path in base.rglob("*"):
            if path.is_file():
                name = path.name.lower()
                assert "phase14" not in name and "phase_14" not in name, str(path)
                assert not name.startswith("44_"), str(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]
    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "7C"
    assert final["baseline"] == "Environmental Health Futures, 2050 / 2075"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-10"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == {
        "assumptions": 36,
        "scenario_nodes": 30,
        "scenario_edges": 30,
        "control_states": 30,
        "uncertainty_states": 30,
        "comparison_rows": 6,
    }
    assert final["phase7a_freeze_manifest"]["path"] == PHASE7A_MANIFEST
    assert final["phase7b_freeze_manifest"]["path"] == SIBLING_FINAL_MANIFEST
    assert final["protected_inputs"] == [PHASE7A_MANIFEST, SIBLING_FINAL_MANIFEST]
    assert final["phase7a_7b_immutable"] is True
    assert final["phase14_implemented"] is False
    assert final["qualitative_only"] is True
    assert final["unsupported_future_exposure_predictions"] is False
    assert final["unsupported_future_health_outcomes"] is False
    assert final["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    assert final["deferred_maintenance_preserved"] == [
        "Phase 6B manifest status wording mismatch",
        "Phase 3A missing manifest status",
        "Phase 2A legacy worktree superseded cleanup candidate",
    ]
    final_result = verify_artifacts(root, final, "Phase 7C final freeze manifest", EXPECTED_PACKAGE_ARTIFACTS)
    working_result = verify_working_manifest(root)
    verify_artifact_check(root)
    phase7a_result = verify_phase7a(root)
    phase7b_result = verify_phase7b(root)
    package = verify_package(root)
    prior = verify_prior_system(root)
    review = verify_review(root)
    verify_status_surfaces(root)
    verify_no_phase14(root)
    result = {
        "status": "passed",
        "phase": "7C",
        "freeze_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": working_result,
        "package": package,
        "phase7a_integrity": phase7a_result,
        "phase7b_integrity": phase7b_result,
        "prior_system_immutability": prior,
        "review_history": review,
        "active_holds_preserved": True,
        "deferred_maintenance_preserved": True,
        "phase14_not_implemented": True,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
