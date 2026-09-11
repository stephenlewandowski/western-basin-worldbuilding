#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 15A."""
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

FINAL_MANIFEST = "reports/phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase15a_manifest.json"
ARTIFACT_CHECK = "reports/phase15a_artifact_check.json"
R_RESULT = "reports/phase15a_r_validation_result.json"
REVIEW = "reports/phase15a_independent_review.md"
INITIAL_REVIEW = "reports/phase15a_independent_review_initial.md"
SECOND_REVIEW = "reports/phase15a_independent_review_second_failed.md"
THIRD_REVIEW = "reports/phase15a_independent_review_third_failed.md"
PRIOR_PASS_REVIEW = "reports/phase15a_independent_review_prior_pass.md"
A14A_FINAL = "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
A14B_FINAL = "reports/phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
SOURCE_COMMIT = "87e877dc33372195a549cab5654fd6b6e6de64e9"
EXPECTED_PRIOR_ENTRIES = 535
EXPECTED_PRIOR_UNIQUE = 526
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yml", ".yaml", ".svg", ".toml"}

WORKING_ARTIFACTS = [
    "data/processed/analysis/technology_sources.csv",
    "data/processed/analysis/technology_system_nodes.csv",
    "data/processed/analysis/technology_system_observations.csv",
    "data/processed/analysis/technology_uncertainties.csv",
    "data/processed/integration/technology_dependencies.csv",
    "data/processed/integration/technology_system_interfaces.csv",
    "docs/phase_briefs/phase15_technology_strategic_systems_convergence.md",
    "docs/phase_briefs/phase15a_technology_strategic_systems_baseline_2026.md",
    "docs/phase_briefs/phase15b_technology_convergence_futures.md",
    "metadata/technology_vocabulary.yml",
    "outputs/figures/technology_system_convergence_architecture_2026.png",
    "outputs/figures/technology_system_convergence_architecture_2026.svg",
    ARTIFACT_CHECK,
    "reports/phase15a_biosecurity_lens.md",
    REVIEW,
    INITIAL_REVIEW,
    PRIOR_PASS_REVIEW,
    SECOND_REVIEW,
    THIRD_REVIEW,
    "reports/phase15a_provenance_check.md",
    R_RESULT,
    "reports/phase15a_technology_interfaces.md",
    "reports/phase15a_technology_qa.md",
    "reports/phase15a_technology_systems_baseline.md",
    "src/R/systems/validate_phase15a_technology.R",
    "src/python/systems/build_phase15a_technology.py",
    "src/python/systems/validate_phase15a_technology.py",
]
FREEZE_VALIDATORS = [
    "src/python/systems/validate_phase15a_freeze.py",
    "src/R/systems/validate_phase15a_freeze.R",
]
FINAL_ARTIFACTS = sorted(WORKING_ARTIFACTS + FREEZE_VALIDATORS)

FAMILIES = {
    "AI / ADVANCED COMPUTE / AUTOMATION",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS",
    "CYBERSECURITY / DIGITAL RESILIENCE",
    "ADVANCED ENERGY",
    "ADVANCED MATERIALS / MANUFACTURING",
    "QUANTUM TECHNOLOGIES",
    "BIOTECHNOLOGY / GENETIC ENGINEERING",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
}
STATUSES = {"established", "commercially emerging", "demonstration / pilot", "research-stage", "speculative / long-horizon"}
RELEVANCE = {"current", "emerging", "speculative"}
EXPECTED_COUNTS = {
    "technology_families": 8,
    "technology_records": 18,
    "observations": 21,
    "interfaces": 44,
    "dependencies": 32,
    "uncertainties": 8,
    "sources": 33,
    "dependency_classes": 11,
    "phase14_system_coverage": 13,
}
EXPECTED_MATURITY = {"established": 5, "commercially emerging": 7, "demonstration / pilot": 3, "research-stage": 3}
EXPECTED_CURRENT = {"current": 3, "emerging": 12, "speculative": 3}
EXPECTED_NODE_RELEVANCE = {"current": 3, "emerging": 9, "speculative": 6}
EXPECTED_INTERFACE_RELEVANCE = {"current": 12, "emerging": 23, "speculative": 9}
BLOCKING_REVIEW_ARRAYS = (
    "security_concerns",
    "logic_errors",
    "provenance_errors",
    "technology_maturity_errors",
    "regional_relevance_errors",
    "ontology_interface_errors",
    "governance_boundary_errors",
    "biosecurity_boundary_errors",
    "canon_boundary_errors",
)


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
        verify_hash(root, path, metadata)
        if isinstance(metadata, str) or digest((root / path).read_bytes()) == metadata.get("sha256"):
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
    final_text = (root / REVIEW).read_text(encoding="utf-8")
    assert "deleg_486838c1" in final_text
    final = review_verdict(root, REVIEW)
    assert final.get("passed") is True
    for key in BLOCKING_REVIEW_ARRAYS:
        assert final.get(key) == [], f"{REVIEW}: {key}"
    expected_lineage = {
        INITIAL_REVIEW: ("deleg_ae5f3c71", False),
        SECOND_REVIEW: ("deleg_6cca1617", False),
        THIRD_REVIEW: ("deleg_16255f91", False),
        PRIOR_PASS_REVIEW: ("deleg_4cd21ddf", True),
    }
    records = {}
    for relative, (review_id, passed) in expected_lineage.items():
        text = (root / relative).read_text(encoding="utf-8")
        assert review_id in text, f"review lineage ID missing: {review_id}"
        verdict = review_verdict(root, relative)
        assert verdict.get("passed") is passed, f"review lineage verdict: {relative}"
        records[relative] = {"review_id": review_id, "passed": passed}
    return {"final_review_id": "deleg_486838c1", "final_passed": True, "preserved": records}


def prior_freeze_integrity(root: Path) -> dict[str, Any]:
    entries = 0
    protected: set[str] = set()
    errors: list[str] = []
    final_name = Path(FINAL_MANIFEST).name
    manifests = []
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        manifests.append(path.name)
        payload = load_json(root, f"reports/{path.name}")
        for relative, metadata in artifact_entries(payload).items():
            entries += 1
            protected.add(relative.replace("\\", "/"))
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
    vocabulary = yaml.safe_load((root / "metadata/technology_vocabulary.yml").read_text(encoding="utf-8"))
    ontology = yaml.safe_load((root / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology.get("systems", [])}
    assert len(system_ids) == 13
    assert set(vocabulary.get("technology_families", [])) == FAMILIES
    assert set(vocabulary.get("technology_status", [])) == STATUSES
    assert set(vocabulary.get("regional_relevance", [])) == RELEVANCE

    source_fields, sources = read_csv(root / "data/processed/analysis/technology_sources.csv")
    source_ids = {row["source_id"] for row in sources}
    assert len(sources) == EXPECTED_COUNTS["sources"] and len(source_ids) == len(sources)
    assert all(row["retrieval_url"] and row["retrieval_date"] for row in sources)
    assert all((row["source_scope"] == "regional_system_context" and row["url"].startswith("repo://")) or (row["source_scope"] == "general_technology_capability" and row["url"].startswith("https://")) for row in sources)
    assert all(row["regional_deployment_supported"].lower() == "no" for row in sources)

    node_fields, nodes = read_csv(root / "data/processed/analysis/technology_system_nodes.csv")
    node_ids = {row["technology_id"] for row in nodes}
    assert len(nodes) == EXPECTED_COUNTS["technology_records"] and len(node_ids) == len(nodes)
    assert {row["technology_family"] for row in nodes} == FAMILIES
    assert set(row["technology_status"] for row in nodes) <= STATUSES
    assert set(row["current_or_emerging"] for row in nodes) == RELEVANCE
    assert set(row["regional_relevance"] for row in nodes) == RELEVANCE
    assert all(row["source_id"] in source_ids and row["regional_evidence_source_id"] in source_ids for row in nodes)
    assert Counter(row["technology_status"] for row in nodes) == EXPECTED_MATURITY
    assert Counter(row["current_or_emerging"] for row in nodes) == EXPECTED_CURRENT
    assert Counter(row["regional_relevance"] for row in nodes) == EXPECTED_NODE_RELEVANCE

    _, observations = read_csv(root / "data/processed/analysis/technology_system_observations.csv")
    assert len(observations) == EXPECTED_COUNTS["observations"]
    assert len({row["observation_id"] for row in observations}) == len(observations)
    assert all(row["technology_id"] in node_ids and row["source_id"] in source_ids and row["regional_evidence_source_id"] in source_ids for row in observations)

    _, uncertainties = read_csv(root / "data/processed/analysis/technology_uncertainties.csv")
    assert len(uncertainties) == EXPECTED_COUNTS["uncertainties"]
    assert all(row["uncertainty_status"] == "open" and row["technology_id"] in node_ids and row["affected_system_id"] in system_ids and row["source_id"] in source_ids for row in uncertainties)

    interface_fields, interfaces = read_csv(root / "data/processed/integration/technology_system_interfaces.csv")
    assert len(interfaces) == EXPECTED_COUNTS["interfaces"]
    assert len({row["interface_id"] for row in interfaces}) == len(interfaces)
    target_ids = {row["target_system_id"] for row in interfaces}
    assert target_ids == system_ids
    assert all(not row["source_system_id"] and row["technology_id"] in node_ids and row["evidence_class"] == "INFERRED" and row["source_id"] in source_ids for row in interfaces)
    assert Counter(row["regional_relevance"] for row in interfaces) == EXPECTED_INTERFACE_RELEVANCE
    node_by_id = {row["technology_id"]: row for row in nodes}
    assert all(row["current_or_emerging"] == node_by_id[row["technology_id"]]["current_or_emerging"] and row["regional_relevance"] == node_by_id[row["technology_id"]]["regional_relevance"] for row in interfaces)

    dependency_fields, dependencies = read_csv(root / "data/processed/integration/technology_dependencies.csv")
    assert len(dependencies) == EXPECTED_COUNTS["dependencies"]
    assert len({row["dependency_id"] for row in dependencies}) == len(dependencies)
    assert len({row["dependency_class"] for row in dependencies}) == EXPECTED_COUNTS["dependency_classes"]
    assert all(row["technology_id"] in node_ids and row["affected_system_id"] in system_ids and row["technology_status"] == node_by_id[row["technology_id"]]["technology_status"] for row in dependencies)
    all_fields = {field.lower() for field in source_fields + node_fields + interface_fields + dependency_fields}
    assert not any(any(term in field for term in ("score", "probability", "capacity_score", "performance_score", "resilience_score")) for field in all_fields)

    biosecurity = (root / "reports/phase15a_biosecurity_lens.md").read_text(encoding="utf-8")
    for term in ("Detection", "Attribution uncertainty", "Laboratory/diagnostic capacity", "Biological monitoring", "Supply-chain resilience", "Food/agricultural resilience", "Dual-use governance", "coordination", "public communication", "response capacity", "no pathogen engineering"):
        assert term.lower() in biosecurity.lower(), term
    provenance = (root / "reports/phase15a_provenance_check.md").read_text(encoding="utf-8")
    assert all(f"[{index}]" in provenance for index in range(1, 18)) and "## Sources" in provenance

    svg = root / "outputs/figures/technology_system_convergence_architecture_2026.svg"
    ET.parse(svg)
    svg_text = svg.read_text(encoding="utf-8")
    for term in ("Technology", "Established/current interface", "Emerging interface", "Speculative/long-horizon interface", "G = governance/data dependency", "not deployment", "not a geographic map"):
        assert term in svg_text, term
    png = (root / "outputs/figures/technology_system_convergence_architecture_2026.png").read_bytes()
    dimensions = (int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")) if png[:8] == b"\x89PNG\r\n\x1a\n" else ()
    assert dimensions[0] >= 1200 and dimensions[1] >= 500
    return {
        "technology_families": len(FAMILIES),
        "technology_records": len(nodes),
        "observations": len(observations),
        "interfaces": len(interfaces),
        "dependencies": len(dependencies),
        "uncertainties": len(uncertainties),
        "sources": len(sources),
        "dependency_classes": len({row["dependency_class"] for row in dependencies}),
        "phase14_system_coverage": len(target_ids),
        "maturity_counts": dict(Counter(row["technology_status"] for row in nodes)),
        "current_or_emerging_counts": dict(Counter(row["current_or_emerging"] for row in nodes)),
        "node_regional_relevance_counts": dict(Counter(row["regional_relevance"] for row in nodes)),
        "interface_regional_relevance_counts": dict(Counter(row["regional_relevance"] for row in interfaces)),
        "figure_dimensions": list(dimensions),
    }


def verify_status(root: Path) -> None:
    surfaces = ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")
    required = ("phase 15a", "accepted / frozen", Path(FINAL_MANIFEST).name, "phase 15b", "approved scope / not implemented", "phase 16", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "no release or tag")
    for relative in surfaces:
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in required:
            assert term in text, f"{relative}: missing {term}"
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        assert "phase 14" in text and "complete" in text, f"{relative}: Phase 14 overall completion missing"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "15A"
    assert final["baseline"] == "Technology & Strategic-Systems Baseline and Interfaces, 2026"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["maturity_counts"] == EXPECTED_MATURITY
    assert final["current_or_emerging_counts"] == EXPECTED_CURRENT
    assert final["node_regional_relevance_counts"] == EXPECTED_NODE_RELEVANCE
    assert final["interface_regional_relevance_counts"] == EXPECTED_INTERFACE_RELEVANCE
    assert final["phase14_system_coverage"] == 13
    assert final["interfaces_are_inferred"] is True
    assert final["no_new_phase14_ontology_members"] is True
    assert final["qualitative_dependencies_only"] is True
    assert final["release_created"] is False and final["tag_created"] is False
    assert final["phase15b_status"] == "APPROVED SCOPE / NOT IMPLEMENTED"
    assert final["phase16_status"] == "NOT IMPLEMENTED"
    assert final["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert final["deferred_maintenance_preserved"] == ["Phase 6B manifest status wording mismatch", "Phase 3A missing manifest status", "Phase 2A superseded legacy worktree"]
    assert final["final_manifest_path"] == FINAL_MANIFEST
    assert FINAL_MANIFEST not in artifact_entries(final)
    final_result = verify_manifest(root, FINAL_MANIFEST, len(FINAL_ARTIFACTS), FINAL_ARTIFACTS)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "15A" and working["status"] == "generated_working_package"
    working_result = verify_manifest(root, WORKING_MANIFEST, len(WORKING_ARTIFACTS), sorted(WORKING_ARTIFACTS))
    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["phase"] == "15A" and artifact_check["passed"] is True and artifact_check["errors"] == []
    assert artifact_check["counts"]["prior_freeze_entries"] == EXPECTED_PRIOR_ENTRIES
    assert artifact_check["counts"]["prior_freeze_unique_paths"] == EXPECTED_PRIOR_UNIQUE
    assert load_json(root, R_RESULT) == {"phase": "15A", "passed": True, "failure_count": 0, "failures": []}

    package = verify_package(root)
    assert package["maturity_counts"] == EXPECTED_MATURITY
    assert package["current_or_emerging_counts"] == EXPECTED_CURRENT
    assert package["node_regional_relevance_counts"] == EXPECTED_NODE_RELEVANCE
    assert package["interface_regional_relevance_counts"] == EXPECTED_INTERFACE_RELEVANCE

    a14a = load_json(root, A14A_FINAL)
    a14b = load_json(root, A14B_FINAL)
    assert a14a["accepted_phase"] == "14A" and a14a["status"] == "ACCEPTED / FROZEN"
    assert a14b["accepted_phase"] == "14B" and a14b["status"] == "ACCEPTED / FROZEN"
    a14a_result = verify_manifest(root, A14A_FINAL, 24)
    a14b_result = verify_manifest(root, A14B_FINAL, 23)

    prior = prior_freeze_integrity(root)
    protected = set(prior["protected_paths"])
    changed = changed_paths(root)
    assert not (changed & protected), sorted(changed & protected)
    assert "metadata/atlas_systems.yml" not in changed and "metadata/atlas_layers.yml" not in changed
    assert not any(path.lower().endswith(".gpkg") for path in changed)
    assert not any("phase16" in path.lower() for path in changed if not path.startswith("docs/phase_briefs/"))
    assert not any("phase15b" in path.lower() for path in changed if not path.startswith("docs/phase_briefs/"))
    assert not any(("scenario" in path.lower() or "future" in path.lower()) for path in changed if path.startswith(("data/", "outputs/")))

    review = verify_review_lineage(root)
    verify_status(root)
    print(json.dumps({
        "status": "passed",
        "phase": "15A",
        "final_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": {"path": WORKING_MANIFEST, **working_result},
        "package": package,
        "phase14": {"phase14a": a14a_result, "phase14b": a14b_result},
        "prior_freeze_integrity": {key: value for key, value in prior.items() if key != "protected_paths"},
        "review_lineage": review,
        "changed_paths_from_source_commit": len(changed),
        "release_created": False,
        "tag_created": False,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
