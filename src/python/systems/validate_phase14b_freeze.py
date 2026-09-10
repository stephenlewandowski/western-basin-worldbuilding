#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 14B."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

FINAL_MANIFEST = "reports/phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase14b_manifest.json"
ARTIFACT_CHECK = "reports/phase14b_artifact_check.json"
REVIEW = "reports/phase14b_independent_review.md"
INITIAL_REVIEW = "reports/phase14b_independent_review_initial.md"
R_RESULT = "reports/phase14b_r_validation_result.json"
A14A_FINAL = "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
SOURCE_COMMIT = "adac6c5dc072b1a61a1474c5f6dad74c5e65278f"
EXPECTED_PRIOR_ENTRIES = 512
EXPECTED_PRIOR_UNIQUE = 503
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yml", ".yaml", ".svg", ".toml"}
EXPECTED_REGISTRY_FORMATS = {"CSV": 81, "GeoJSON": 2, "GeoPackage": 16, "JSON": 1, "PNG": 55, "SVG": 55, "YAML": 3}
EXPECTED_COUNTS = {
    "registry_entries": 213,
    "relationship_rows": 367,
    "endpoint_role_rows": 36,
    "dependency_rows": 761,
    "joinability_rows": 78,
    "population_total": 520,
    "population_inferred": 468,
    "population_context_reused": 52,
    "phase14a_endpoint_occurrences": 36,
    "phase14a_exact": 0,
    "phase14a_system_level": 34,
    "phase14a_retained_conceptual": 2,
    "phase14a_unresolved": 0,
}
EXPECTED_FINAL_ARTIFACTS = sorted(
    [
        "data/processed/integration/atlas_dependency_crosswalk.csv",
        "data/processed/integration/endpoint_role_crosswalk.csv",
        "data/processed/integration/relationship_normalization_crosswalk.csv",
        "data/processed/integration/system_joinability_matrix.csv",
        "metadata/atlas_layers.yml",
        "metadata/atlas_relationship_vocabulary.yml",
        "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png",
        "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg",
        ARTIFACT_CHECK,
        "reports/phase14b_atlas_layer_registry.md",
        "reports/phase14b_build_summary.json",
        "reports/phase14b_dependency_integration.md",
        REVIEW,
        INITIAL_REVIEW,
        "reports/phase14b_integration_qa.md",
        R_RESULT,
        "reports/phase14b_relationship_normalization.md",
        "src/R/systems/validate_phase14b_integration.R",
        "src/python/systems/build_phase14b_integration.py",
        "src/python/systems/validate_phase14b_integration.py",
        WORKING_MANIFEST,
        "src/python/systems/validate_phase14b_freeze.py",
        "src/R/systems/validate_phase14b_freeze.R",
    ]
)
BLOCKING_REVIEW_ARRAYS = (
    "security_concerns",
    "logic_errors",
    "provenance_errors",
    "registry_errors",
    "relationship_normalization_errors",
    "identity_errors",
    "evidence_classification_errors",
    "joinability_errors",
    "canon_boundary_errors",
)
VALID_ENDPOINT_ROLES = {
    "physical asset",
    "geographic unit",
    "system node",
    "institutional actor",
    "ecological entity",
    "population/settlement entity",
    "monitoring/surveillance interface",
    "generalized external interface",
    "conceptual interface",
    "scenario-only entity",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_candidates(path: Path) -> list[tuple[str, int]]:
    raw = path.read_bytes()
    candidates = [(digest(raw), len(raw))]
    if path.suffix in TEXT_SUFFIXES:
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.extend(((digest(normalized), len(normalized)), (digest(crlf), len(crlf))))
    return candidates


def verify_hash(root: Path, relative: str, expected: dict[str, Any] | str) -> None:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing protected artifact: {relative}"
    expected_hash = expected if isinstance(expected, str) else str(expected["sha256"])
    expected_bytes = None if isinstance(expected, str) else expected.get("bytes")
    for actual_hash, actual_bytes in portable_candidates(path):
        if actual_hash == expected_hash and (expected_bytes is None or int(expected_bytes) == actual_bytes):
            return
    raise AssertionError(f"hash/byte mismatch: {relative}")


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(value, dict), "manifest artifact collection is not an object"
    return value


def verify_manifest(root: Path, relative: str, expected_count: int, expected_inventory: list[str] | None = None) -> dict[str, int]:
    payload = load_json(root, relative)
    entries = artifact_entries(payload)
    assert len(entries) == expected_count, f"{relative}: artifact count {len(entries)}"
    if expected_inventory is not None:
        assert list(entries) == expected_inventory, f"{relative}: artifact inventory differs"
    exact = 0
    normalized = 0
    for path, metadata in entries.items():
        raw_hash = digest((root / path).read_bytes()) if (root / path).is_file() else ""
        verify_hash(root, path, metadata)
        if isinstance(metadata, str) or raw_hash == metadata.get("sha256"):
            exact += 1
        else:
            normalized += 1
    return {"entries": len(entries), "exact": exact, "newline_normalized": normalized}


def review_verdict(root: Path, relative: str) -> dict[str, Any]:
    text = (root / relative).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, f"review JSON block missing: {relative}"
    return json.loads(match.group(1))


def verify_review_lineage(root: Path) -> dict[str, Any]:
    final = review_verdict(root, REVIEW)
    assert final.get("passed") is True
    for key in BLOCKING_REVIEW_ARRAYS:
        assert final.get(key) == [], f"{REVIEW}: {key}"
    initial = review_verdict(root, INITIAL_REVIEW)
    assert initial.get("passed") is False
    return {"final_passed": True, "final_review_id": "deleg_9df50f46", "initial_passed": False, "initial_review_id": "deleg_1c35baf2"}


def prior_freeze_integrity(root: Path) -> dict[str, Any]:
    entries = 0
    protected: set[str] = set()
    manifests = []
    errors: list[str] = []
    final_name = Path(FINAL_MANIFEST).name
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        manifests.append(path.name)
        payload = load_json(root, f"reports/{path.name}")
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
    return {"manifest_count": len(manifests), "entries": entries, "unique_paths": len(protected), "errors": errors, "protected_paths": sorted(protected)}


def changed_paths(root: Path) -> set[str]:
    output = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True)
    return {line.replace("\\", "/") for line in output.splitlines() if line}


def verify_package(root: Path) -> dict[str, Any]:
    ontology = yaml.safe_load((root / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    systems = {item["system_id"] for item in ontology["systems"]}
    layers = yaml.safe_load((root / "metadata/atlas_layers.yml").read_text(encoding="utf-8"))["layer_registry"]
    formats = dict(Counter(row["physical_format"] for row in layers))
    assert len(systems) == 13
    assert len(layers) == EXPECTED_COUNTS["registry_entries"]
    assert formats == EXPECTED_REGISTRY_FORMATS, formats
    assert all(row["system_id"] in systems and (root / row["source_artifact"]).is_file() for row in layers)

    rel_fields, relationships = read_csv(root / "data/processed/integration/relationship_normalization_crosswalk.csv")
    _, inventory = read_csv(root / "data/processed/integration/relationship_taxonomy_inventory.csv")
    assert len(relationships) == len(inventory) == EXPECTED_COUNTS["relationship_rows"]
    assert len({row["atlas_normalization_id"] for row in relationships}) == len(relationships)
    assert {
        (row["local_taxonomy_id"], row["source_artifact"], row["local_field"], row["local_term"])
        for row in relationships
    } == {
        (row["taxonomy_id"], row["source_artifact"], row["local_field"], row["local_term"])
        for row in inventory
    }
    assert all(row["information_loss_or_caveat"] for row in relationships)
    energy = {row["local_term"].lower(): row["normalized_relationship_class"] for row in relationships if row["source_phase"] == "3"}
    expected_energy = {
        "generation_grid_interface": "energy flow",
        "regional_grid_interface": "energy flow",
        "bidirectional_storage_interface": "energy flow",
        "electricity": "operational dependency",
        "grid_serves_load": "operational dependency",
        "grid_serves_planned_compute": "operational dependency",
        "cooling_water": "operational dependency",
        "storage_support": "operational dependency",
        "communications": "information / observation",
        "fuel": "material flow",
        "weather": "ecological relationship",
    }
    assert {term: energy.get(term) for term in expected_energy} == expected_energy

    _, endpoints = read_csv(root / "data/processed/integration/endpoint_role_crosswalk.csv")
    assert len(endpoints) == EXPECTED_COUNTS["endpoint_role_rows"]
    assert set(row["endpoint_role"] for row in endpoints).issubset(VALID_ENDPOINT_ROLES)
    assert Counter(row["inherited_mapping_status"] for row in endpoints) == Counter({"resolved_system_level": 34, "retained_conceptual": 2})
    assert all(row["conceptual_endpoint_preserved"] == "yes" and row["role_mapping_status"] == "normalized_role_only" for row in endpoints)

    dep_fields, dependencies = read_csv(root / "data/processed/integration/atlas_dependency_crosswalk.csv")
    required = {"atlas_relationship_id", "source_phase", "source_artifact", "local_relationship_id", "source_system_id", "target_system_id", "evidence_class", "source_id", "spatial_scale", "temporal_basis", "scenario_status", "Atlas_use", "caveat"}
    assert required.issubset(dep_fields)
    assert len(dependencies) == EXPECTED_COUNTS["dependency_rows"]
    assert len({row["atlas_relationship_id"] for row in dependencies}) == len(dependencies)
    assert all(row["source_id"] and row["scenario_status"] == "BASELINE_DEPENDENCY" and row["caveat"] for row in dependencies)
    assert all(row["source_system_id"] in systems and row["target_system_id"] in systems for row in dependencies if row["source_system_id"] and row["target_system_id"])
    population = [row for row in dependencies if row["source_phase"] == "11B"]
    assert len(population) == EXPECTED_COUNTS["population_total"]
    assert sum(row["evidence_class"] == "INFERRED" for row in population) == EXPECTED_COUNTS["population_inferred"]
    assert sum(row["evidence_class"] == "CONTEXT_REUSED" for row in population) == EXPECTED_COUNTS["population_context_reused"]
    assert all("QUALITATIVE_STRESS_TEST_ONLY" in row["Atlas_use"] and "NO_QUANTITATIVE_AGGREGATION" in row["Atlas_use"] for row in population)

    matrix_fields, matrix = read_csv(root / "data/processed/integration/system_joinability_matrix.csv")
    boolean_fields = ("direct_exact_identity_join", "system_level_conceptual_join", "dependency_relationship_join", "spatial_colocation_only", "scenario_layer_reference", "scenario_only_link", "no_defensible_current_join")
    assert len(matrix) == EXPECTED_COUNTS["joinability_rows"]
    assert all(row[field] in {"YES", "NO"} for row in matrix for field in boolean_fields)
    assert all(row["spatial_colocation_only"] == "NO" and "co-location is not treated as causation" in row["caveat"].lower() for row in matrix)
    assert all(row["scenario_only_link"] == "NO" or row["dependency_relationship_join"] == "NO" for row in matrix)
    assert not any(field.lower() in {"score", "connectivity_score", "risk_score", "composite_risk_score"} for field in matrix_fields)

    svg = root / "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg"
    ET.parse(svg)
    svg_text = svg.read_text(encoding="utf-8")
    assert all(term in svg_text for term in ("Cross-System Joinability / Dependency Architecture", "Exact/entity-level", "System-level conceptual", "Inferred relationship", "Scenario-only relationship", "not a geographic map", "co-location"))
    png = (root / "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png").read_bytes()
    dimensions = (int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")) if png[:8] == b"\x89PNG\r\n\x1a\n" else ()
    assert dimensions[0] >= 1000 and dimensions[1] >= 500
    return {"registry_entries": len(layers), "registry_formats": formats, "relationship_rows": len(relationships), "endpoint_role_rows": len(endpoints), "dependency_rows": len(dependencies), "joinability_rows": len(matrix), "population_total": len(population), "population_inferred": sum(row["evidence_class"] == "INFERRED" for row in population), "population_context_reused": sum(row["evidence_class"] == "CONTEXT_REUSED" for row in population), "figure_dimensions": list(dimensions)}


def verify_status(root: Path) -> None:
    surfaces = ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")
    required = ("phase 14b", "accepted / frozen", Path(FINAL_MANIFEST).name, "phase 15", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "no release or tag")
    for relative in surfaces:
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in required:
            assert term.lower() in text, f"{relative}: missing {term}"
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        assert "phase 14" in text and "complete" in text, f"{relative}: Phase 14 overall completion missing"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "14B"
    assert final["baseline"] == "Atlas Layer Registry & Cross-System Dependency Normalization"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["registry_formats"] == EXPECTED_REGISTRY_FORMATS
    assert final["energy_taxonomy"] == {"energy_flow": 3, "operational_dependency": 5, "information_control": 1, "fuel_material_input": True, "weather_ecological_context": True}
    assert final["phase14a_endpoint_disposition"] == {"exact": 0, "system_level": 34, "retained_conceptual": 2, "unresolved": 0}
    assert final["population_high_inference"] == {"total": 520, "inferred": 468, "reused_context": 52, "quantitative_aggregation_allowed": False}
    assert final["joinability_matrix"] == {"pairs": 78, "exact_cross_system_joins": 0, "system_level_conceptual_joins": 29, "dependency_joins": 29, "scenario_layer_references": 9, "exclusive_scenario_only_links": 0, "colocation_only_joins": 0, "without_selected_defensible_current_join": 49, "metadata_only": True}
    assert final["phase14_overall_status"] == "COMPLETE / ACCEPTED / FROZEN"
    assert final["phase15_implemented"] is False and final["release_created"] is False and final["tag_created"] is False
    assert final["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert final["deferred_maintenance_preserved"] == ["Phase 6B manifest status wording mismatch", "Phase 3A missing manifest status", "Phase 2A superseded legacy worktree"]
    assert final["final_manifest_path"] == FINAL_MANIFEST
    verify_hash(root, final["phase14a_final_manifest"]["path"], final["phase14a_final_manifest"])
    final_result = verify_manifest(root, FINAL_MANIFEST, len(EXPECTED_FINAL_ARTIFACTS), EXPECTED_FINAL_ARTIFACTS)
    assert FINAL_MANIFEST not in artifact_entries(final)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "14B" and working["status"] == "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE"
    working_result = verify_manifest(root, WORKING_MANIFEST, len(artifact_entries(working)))
    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["passed"] is True and artifact_check["errors"] == []
    assert artifact_check["counts"]["registry_entries"] == EXPECTED_COUNTS["registry_entries"]
    assert artifact_check["counts"]["relationship_rows"] == EXPECTED_COUNTS["relationship_rows"]
    assert artifact_check["counts"]["dependency_rows"] == EXPECTED_COUNTS["dependency_rows"]
    assert artifact_check["counts"]["joinability_rows"] == EXPECTED_COUNTS["joinability_rows"]
    assert load_json(root, R_RESULT) == {"phase": "14B", "passed": True, "failure_count": 0, "failures": []}

    package = verify_package(root)
    prior = prior_freeze_integrity(root)
    prior_protected = set(prior.pop("protected_paths"))
    a14a = load_json(root, A14A_FINAL)
    assert a14a["accepted_phase"] == "14A" and a14a["status"] == "ACCEPTED / FROZEN"
    assert a14a["counts"]["identity_rows"] == 456 and a14a["counts"]["relationship_rows"] == 367
    verify_manifest(root, A14A_FINAL, 24)
    review = verify_review_lineage(root)
    changed = changed_paths(root)
    assert "metadata/systems.yml" not in changed
    assert not any(path.lower().endswith(".gpkg") for path in changed)
    assert not any("phase15" in path.lower() for path in changed)
    assert not (changed & prior_protected), sorted(changed & prior_protected)
    verify_status(root)

    print(json.dumps({"status": "passed", "phase": "14B", "final_manifest": {"path": FINAL_MANIFEST, **final_result}, "working_manifest": {"path": WORKING_MANIFEST, **working_result}, "package": package, "phase14a_and_prior_freeze_integrity": prior, "review_lineage": review, "changed_paths": len(changed), "phase15_implemented": False, "release_created": False, "tag_created": False}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
