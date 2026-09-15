#!/usr/bin/env python3
"""Independent final-freeze validator for the accepted Phase 16B package.

This validator is deliberately separate from the Phase 16B package validator.
It verifies the final acceptance boundary, prior freeze integrity, review
lineage, registry membership, and the no-drift/no-later-phase boundary without
rebuilding or rewriting any artifact.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
INTEGRATION = ROOT / "data/processed/integration"
FIGURES = ROOT / "outputs/figures"

FINAL_MANIFEST = "reports/phase16b_compound_stress_tests_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase16b_manifest.json"
ARTIFACT_CHECK = "reports/phase16b_artifact_check.json"
R_RESULT = "reports/phase16b_r_validation_result.json"
REVIEW = "reports/phase16b_independent_review.md"
FAILED_REVIEWS = [
    "reports/phase16b_independent_review_initial.md",
    "reports/phase16b_independent_review_second_failed.md",
    "reports/phase16b_independent_review_third_failed.md",
    "reports/phase16b_independent_review_fourth_failed.md",
    "reports/phase16b_independent_review_fifth_failed.md",
]
FREEZE_VALIDATORS = [
    "src/python/systems/validate_phase16b_freeze.py",
    "src/R/systems/validate_phase16b_freeze.R",
]
SOURCE_COMMIT = "d19f1cd8bca54b0f0ee56343818e6978ca55db47"
WORKING_SOURCE_COMMIT = "9308127065112d0c01c294e954ae87f44e39af3f"
EXPECTED_PRIOR_ENTRIES = 623
EXPECTED_PRIOR_UNIQUE = 614
EXPECTED_SYSTEM_IDS = {
    "SYS-BIOGEOCHEMISTRY",
    "SYS-CLIMATE",
    "SYS-DATA",
    "SYS-ECOLOGY",
    "SYS-ENERGY",
    "SYS-EXPOSURE",
    "SYS-FREIGHT",
    "SYS-GOVERNANCE",
    "SYS-INFECTIOUS-DISEASE",
    "SYS-MATERIALS",
    "SYS-POPULATION",
    "SYS-VECTOR-ECOLOGY",
    "SYS-WATER",
}
EXPECTED_COUNTS = {
    "principal_tests": 4,
    "reserve_tests": 2,
    "chain_stages": 13,
    "branches": 14,
    "system_state_observations": 26,
    "response_adaptation_states": 13,
    "regime_effect_rows": 24,
    "uncertainty_rows": 4,
    "comparison_rows": 4,
    "narrative_hooks": 4,
    "scenario_conditioned_stages": 2,
    "terminated_branches": 14,
    "phase16a_protected_artifacts": 30,
    "phase14a_protected_artifacts": 24,
    "phase14b_protected_artifacts": 23,
    "phase15a_protected_artifacts": 30,
    "phase15b_protected_artifacts": 28,
    "prior_freeze_entries": 623,
    "prior_freeze_unique_paths": 614,
}
EXPECTED_TESTS = {
    "P16B-CAND-001",
    "P16B-CAND-002",
    "P16B-CAND-003",
    "P16B-CAND-004",
}
RESERVE_TESTS = {"P16B-CAND-005", "P16B-CAND-006"}
WORKING_ARTIFACTS = [
    "data/processed/integration/phase16b_stress_test_definitions.csv",
    "data/processed/integration/phase16b_chain_stages.csv",
    "data/processed/integration/phase16b_chain_terminations.csv",
    "data/processed/integration/phase16b_system_states.csv",
    "data/processed/integration/phase16b_response_adaptation_states.csv",
    "data/processed/integration/phase16b_regime_effects.csv",
    "data/processed/integration/phase16b_uncertainties.csv",
    "data/processed/integration/phase16b_cross_test_comparison.csv",
    "data/processed/integration/phase16b_narrative_hooks.csv",
    "outputs/figures/phase16b_compound_stress_propagation.png",
    "outputs/figures/phase16b_compound_stress_propagation.svg",
    "outputs/figures/phase16b_technology_regime_effects.png",
    "outputs/figures/phase16b_technology_regime_effects.svg",
    "reports/phase16b_compound_cross_system_stress_tests.md",
    "reports/phase16b_qa.md",
    "reports/phase16b_provenance_lineage.md",
    "reports/phase16b_scenario_comparison.md",
    "reports/phase16b_narrative_hooks.md",
    REVIEW,
    "src/python/systems/build_phase16b_stress_tests.py",
    "src/python/systems/validate_phase16b_stress_tests.py",
    "src/R/systems/validate_phase16b_stress_tests.R",
]
FINAL_ARTIFACTS = sorted(
    WORKING_ARTIFACTS
    + [WORKING_MANIFEST, ARTIFACT_CHECK, R_RESULT, *FAILED_REVIEWS, *FREEZE_VALIDATORS]
)
STATUS_SURFACES = [
    "PROJECT_STATUS.md",
    "docs/canon_status.md",
    "reports/current_phase_handoff.md",
    "README.md",
    "reports/README.md",
    "docs/agent_workflow.md",
    "CHANGELOG.md",
]
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".txt", ".yml", ".yaml", ".svg", ".toml"}
BLOCKING_REVIEW_FIELDS = [
    "security_concerns",
    "logic_errors",
    "provenance_errors",
    "chain_errors",
    "propagation_errors",
    "evidence_classification_errors",
    "scenario_boundary_errors",
    "technology_modifier_errors",
    "biosecurity_boundary_errors",
    "atlas_bridge_errors",
    "canon_boundary_errors",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(relative: str) -> dict[str, Any]:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        fail(f"JSON object required: {relative}")
    return value


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("artifacts", payload.get("files"))
    if not isinstance(entries, dict):
        fail("manifest artifact collection is not an object")
    return entries


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def portable_candidates(path: Path) -> list[tuple[str, int]]:
    raw = path.read_bytes()
    candidates = [(digest(raw), len(raw))]
    if path.suffix.lower() in TEXT_SUFFIXES:
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.extend(((digest(normalized), len(normalized)), (digest(crlf), len(crlf))))
    return list(dict.fromkeys(candidates))


def verify_entry(relative: str, metadata: Any) -> None:
    path = ROOT / relative
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"missing protected artifact: {relative}")
    if isinstance(metadata, str):
        expected_hash = metadata
        expected_bytes = None
    elif isinstance(metadata, dict) and isinstance(metadata.get("sha256"), str):
        expected_hash = metadata["sha256"]
        expected_bytes = metadata.get("bytes")
    else:
        fail(f"malformed artifact metadata: {relative}")
    for actual_hash, actual_bytes in portable_candidates(path):
        if actual_hash == expected_hash and (expected_bytes is None or int(expected_bytes) == actual_bytes):
            return
    fail(f"hash/byte mismatch: {relative}")


def verify_manifest(relative: str, expected_paths: list[str] | None = None, expected_count: int | None = None) -> dict[str, Any]:
    payload = load_json(relative)
    entries = artifact_entries(payload)
    if expected_count is not None and len(entries) != expected_count:
        fail(f"{relative}: expected {expected_count} artifacts, found {len(entries)}")
    if expected_paths is not None and (set(entries) != set(expected_paths) or len(entries) != len(expected_paths)):
        fail(f"{relative}: artifact inventory differs")
    for path, metadata in entries.items():
        verify_entry(path.replace("\\", "/"), metadata)
    return payload


def read_csv(relative: str) -> tuple[list[str], list[dict[str, str]]]:
    with (ROOT / relative).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def split_ids(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def review_payload(relative: str) -> tuple[str, dict[str, Any]]:
    text = (ROOT / relative).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if not match:
        fail(f"review JSON block missing: {relative}")
    payload = json.loads(match.group(1))
    if not isinstance(payload, dict):
        fail(f"review JSON object required: {relative}")
    return text, payload


def verify_final_review() -> None:
    text, payload = review_payload(REVIEW)
    expected_fields = {"passed", *BLOCKING_REVIEW_FIELDS, "suggestions", "summary"}
    if set(payload) != expected_fields:
        fail("final review schema differs from the current Phase 16B contract")
    if type(payload.get("passed")) is not bool or payload["passed"] is not True:
        fail("final review is not passed:true")
    for field in (*BLOCKING_REVIEW_FIELDS, "suggestions"):
        if not isinstance(payload.get(field), list) or not all(isinstance(item, str) for item in payload[field]):
            fail(f"final review field is not an array of strings: {field}")
        if field in BLOCKING_REVIEW_FIELDS and payload[field]:
            fail(f"final review blocking array is nonempty: {field}")
    if not isinstance(payload.get("summary"), str) or not payload["summary"].strip():
        fail("final review summary is empty")
    summary = payload["summary"].lower()
    if "five preserved failed-review records" not in summary or "623 entries" not in summary:
        fail("final review summary does not preserve the recorded closure evidence")


def verify_failed_lineage() -> None:
    required_findings = [
        ("Figure readability failure", "logic_errors"),
        ("R --require-review review-array parsing", "logic_errors"),
        ("rendered card-layout defect", "logic_errors"),
        ("initial_system_id is a valid Phase 16A/Atlas system", "chain_errors"),
        ("system_id: null", "atlas_bridge_errors"),
    ]
    hashes: set[str] = set()
    for relative, (finding, field) in zip(FAILED_REVIEWS, required_findings):
        text, payload = review_payload(relative)
        if payload.get("passed") is not False:
            fail(f"failed review is not preserved as passed:false: {relative}")
        if not isinstance(payload.get(field), list) or not any(finding in item for item in payload[field]):
            fail(f"expected preserved finding missing: {relative}")
        hashes.add(digest(text.encode("utf-8")))
    if len(hashes) != len(FAILED_REVIEWS):
        fail("failed review records are not distinct")


def registry_system_ids() -> set[str]:
    payload = yaml.safe_load((ROOT / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    records = payload.get("systems") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        fail("authoritative registry systems collection is missing")
    values: list[str] = []
    for record in records:
        if not isinstance(record, dict) or "system_id" not in record:
            fail("authoritative registry contains a malformed system record")
        raw = record["system_id"]
        if not isinstance(raw, str) or not raw or raw != raw.strip() or not raw.strip() or raw.lower() in {"null", "none", "~"}:
            fail(f"registry system_id is not a validated string: {raw!r}")
        values.append(raw)
    if len(values) != 13 or len(set(values)) != 13 or set(values) != EXPECTED_SYSTEM_IDS:
        fail(f"authoritative registry vocabulary mismatch: {values}")
    return set(values)


def verify_registry_membership(system_ids: set[str]) -> None:
    paths = [
        "data/processed/integration/phase16b_stress_test_definitions.csv",
        "data/processed/integration/phase16b_chain_stages.csv",
        "data/processed/integration/phase16b_chain_terminations.csv",
        "data/processed/integration/phase16b_system_states.csv",
        "data/processed/integration/phase16b_response_adaptation_states.csv",
        "data/processed/integration/phase16b_regime_effects.csv",
        "data/processed/integration/phase16b_cross_test_comparison.csv",
        "data/processed/integration/phase16b_narrative_hooks.csv",
    ]
    system_fields = {"source_system_id", "target_system_id", "system_id", "initial_system_id", "stressor_initial_system_id"}
    for relative in paths:
        _, rows = read_csv(relative)
        for index, row in enumerate(rows, start=2):
            for field, value in row.items():
                values = split_ids(value) if field in {"stressor_initial_system_ids", "system_ids"} else [value] if field in system_fields else []
                for candidate in values:
                    if not candidate or candidate not in system_ids:
                        fail(f"registry membership failure: {relative}:{index}:{field}={candidate!r}")


def verify_package(system_ids: set[str]) -> dict[str, int]:
    paths = {
        "definitions": "data/processed/integration/phase16b_stress_test_definitions.csv",
        "stages": "data/processed/integration/phase16b_chain_stages.csv",
        "terminations": "data/processed/integration/phase16b_chain_terminations.csv",
        "states": "data/processed/integration/phase16b_system_states.csv",
        "responses": "data/processed/integration/phase16b_response_adaptation_states.csv",
        "regimes": "data/processed/integration/phase16b_regime_effects.csv",
        "uncertainties": "data/processed/integration/phase16b_uncertainties.csv",
        "comparison": "data/processed/integration/phase16b_cross_test_comparison.csv",
        "hooks": "data/processed/integration/phase16b_narrative_hooks.csv",
    }
    frames = {name: read_csv(path)[1] for name, path in paths.items()}
    expected_rows = {"definitions": 6, "stages": 13, "terminations": 14, "states": 26, "responses": 13, "regimes": 24, "uncertainties": 4, "comparison": 4, "hooks": 4}
    for name, expected in expected_rows.items():
        if len(frames[name]) != expected:
            fail(f"Phase 16B {name} count: {len(frames[name])}")
    definitions = {row["test_id"]: row for row in frames["definitions"]}
    if set(definitions) != EXPECTED_TESTS | RESERVE_TESTS:
        fail("principal/reserve definition IDs differ")
    if {key for key, row in definitions.items() if row["test_class"] == "PRINCIPAL"} != EXPECTED_TESTS:
        fail("principal test count or IDs differ")
    if any(row["implementation_status"] != "RESERVE / UNIMPLEMENTED" for key, row in definitions.items() if key in RESERVE_TESTS):
        fail("reserve test status changed")
    stages = frames["stages"]
    stage_by_id = {row["stage_id"]: row for row in stages}
    if len(stage_by_id) != 13:
        fail("duplicate stage IDs")
    rules = {row["rule_id"]: row for row in read_csv("data/processed/integration/propagation_rules.csv")[1]}
    relationships = {row["relationship_id"]: row for row in read_csv("data/processed/integration/propagation_relationships.csv")[1]}
    for row in stages:
        rule = rules.get(row["phase16a_rule_id"])
        if not rule:
            fail(f"unresolved Phase 16A rule: {row['stage_id']}")
        relationship = relationships.get(row["phase16a_relationship_id"])
        if not relationship:
            fail(f"unresolved Phase 16A relationship: {row['stage_id']}")
        for field in ("source_system_id", "target_system_id", "relationship_class", "propagation_mechanism"):
            if row[field] != rule[field] or row[field] != relationship[field]:
                fail(f"lineage mismatch at {row['stage_id']}:{field}")
        if row["evidence_class"] != rule["evidence_class"] or row["lineage_evidence_class"] != relationship["evidence_class"]:
            fail(f"evidence inheritance mismatch at {row['stage_id']}")
        if row["stage"] == "1":
            if row["chain_relation_type"] != "parallel_initial_branch" or row["stage_parent_id"]:
                fail(f"invalid initial fan-out at {row['stage_id']}")
            if row["source_system_id"] != row["stressor_initial_system_id"]:
                fail(f"initial system mismatch at {row['stage_id']}")
        else:
            parent = stage_by_id.get(row["stage_parent_id"])
            if not parent or row["chain_relation_type"] != "sequential" or parent["target_system_id"] != row["source_system_id"] or int(row["stage"]) != int(parent["stage"]) + 1 or row["phase16a_chain_parent_rule_id"] != parent["phase16a_rule_id"]:
                fail(f"chain continuity mismatch at {row['stage_id']}")
    if any(row["test_id"] in RESERVE_TESTS for row in stages):
        fail("reserve candidate has generated stage")
    terminations = frames["terminations"]
    if any(row["termination_status"] != "TERMINATED — NO DEFENSIBLE CURRENT PATH" or row["defensible_branch_termination"] != "true" for row in terminations):
        fail("termination boundary changed")
    if any(row["status"] != "NONCANONICAL / FUTURE ATLAS HOOK" for row in frames["hooks"]):
        fail("Atlas hook status changed")
    if any("score" in key.lower() or "probability" in key.lower() or "forecast" in key.lower() for row in [*frames["definitions"], *frames["stages"], *frames["states"], *frames["responses"], *frames["regimes"], *frames["uncertainties"], *frames["comparison"], *frames["hooks"]] for key in row):
        fail("forbidden score/probability/forecast field present")
    return {
        "principal_tests": 4,
        "reserve_tests": 2,
        "chain_stages": 13,
        "branches": 14,
        "system_state_observations": 26,
        "response_adaptation_states": 13,
        "regime_effect_rows": 24,
        "uncertainty_rows": 4,
        "comparison_rows": 4,
        "narrative_hooks": 4,
        "scenario_conditioned_stages": sum(row["baseline_or_scenario"] == "scenario-conditioned" for row in stages),
        "terminated_branches": sum(row["termination_status"] == "TERMINATED — NO DEFENSIBLE CURRENT PATH" for row in terminations),
    }


def prior_inventory() -> tuple[int, set[str]]:
    entries = 0
    protected: set[str] = set()
    final_name = Path(FINAL_MANIFEST).name
    for path in sorted(REPORTS.glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in artifact_entries(payload).items():
            normalized = relative.replace("\\", "/")
            entries += 1
            protected.add(normalized)
            verify_entry(normalized, metadata)
    if entries != EXPECTED_PRIOR_ENTRIES or len(protected) != EXPECTED_PRIOR_UNIQUE:
        fail(f"prior freeze inventory is {entries}/{len(protected)}, expected {EXPECTED_PRIOR_ENTRIES}/{EXPECTED_PRIOR_UNIQUE}")
    return entries, protected


def changed_paths() -> set[str]:
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True)
    untracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"], text=True)
    return {line.replace("\\", "/") for line in (tracked + untracked).splitlines() if line}


def verify_figures() -> None:
    expected_dimensions = {
        "phase16b_compound_stress_propagation.png": (2268, 1422),
        "phase16b_technology_regime_effects.png": (4356, 3276),
    }
    for name, dimensions in expected_dimensions.items():
        raw = (FIGURES / name).read_bytes()
        if raw[:8] != b"\x89PNG\r\n\x1a\n" or tuple(int.from_bytes(raw[index:index + 4], "big") for index in (16, 20)) != dimensions:
            fail(f"PNG figure integrity: {name}")
    required = {
        "phase16b_compound_stress_propagation.svg": ("Compound Stress Propagation", "QUALITATIVE", "NON-GEOGRAPHIC", "TERMINATED", "NO DEFENSIBLE"),
        "phase16b_technology_regime_effects.svg": ("Technology-Regime Effects on Propagation", "A — Coordinated Technological Adaptation", "B — Uneven Networked Modernization", "C — High Capability / High Friction Basin", "NON-PROPORTIONAL", "non-ranked"),
    }
    for name, terms in required.items():
        path = FIGURES / name
        ET.parse(path)
        text = path.read_text(encoding="utf-8")
        if any(term.lower() not in text.lower() for term in terms):
            fail(f"SVG figure labels: {name}")
    qa = (REPORTS / "phase16b_qa.md").read_text(encoding="utf-8")
    for term in ("data_top > header_bottom + minimum_gap", "all 0 card-rectangle overlaps detected", "B text enters C=False", "C text outside its figure/card=False"):
        if term not in qa:
            fail(f"figure geometry QA metadata missing: {term}")


def verify_status_surfaces() -> None:
    required = (
        "phase 16b",
        "accepted / frozen",
        "phase 16 overall",
        "complete / accepted / frozen",
        "phase 17",
        "not implemented",
        "active phase",
        "none",
        "great black swamp",
        "hold",
        "toledo intake-coordinate discrepancy",
        "unresolved",
        "phase 6b",
        "phase 3a",
        "phase 2a",
        "no release or tag",
        Path(FINAL_MANIFEST).name,
    )
    for relative in STATUS_SURFACES:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        missing = [term for term in required if term not in text]
        if missing:
            fail(f"status surface {relative} missing: {missing}")


def verify_prior_phase_manifests() -> None:
    expected = {
        "reports/phase16a_integrated_basin_dynamics_freeze_manifest.json": ("16A", 30),
        "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json": ("14A", 24),
        "reports/phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json": ("14B", 23),
        "reports/phase15a_technology_strategic_systems_baseline_freeze_manifest.json": ("15A", 30),
        "reports/phase15b_technology_convergence_futures_freeze_manifest.json": ("15B", 28),
    }
    for relative, (phase, count) in expected.items():
        payload = verify_manifest(relative, expected_count=count)
        if payload.get("accepted_phase") != phase or payload.get("status") != "ACCEPTED / FROZEN":
            fail(f"prior manifest status: {relative}")


def main() -> int:
    final = load_json(FINAL_MANIFEST)
    if final.get("accepted_phase") != "16B" or final.get("baseline") != "Compound Cross-System Stress Tests" or final.get("status") != "ACCEPTED / FROZEN":
        fail("final Phase 16B manifest identity/status")
    if final.get("accepted_by") != "Sol explicit acceptance decision supplied for this run" or final.get("source_commit") != SOURCE_COMMIT:
        fail("final Phase 16B acceptance authority/source commit")
    if final.get("qualitative_only") is not True or final.get("no_composite_scores") is not True or final.get("no_new_phase16a_propagation_rules") is not True:
        fail("final Phase 16B qualitative boundary")
    if final.get("phase16a_status") != "ACCEPTED / FROZEN" or final.get("phase15_status") != "COMPLETE / ACCEPTED / FROZEN" or final.get("phase14_status") != "COMPLETE / ACCEPTED / FROZEN" or final.get("phase17_status") != "NOT IMPLEMENTED":
        fail("final Phase 16B adjacent-phase status")
    if final.get("counts") != EXPECTED_COUNTS:
        fail(f"final Phase 16B counts differ: {final.get('counts')}")
    if final.get("active_holds_preserved") != {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}:
        fail("active holds changed")
    if final.get("deferred_maintenance_preserved") != ["Phase 6B manifest-status wording mismatch", "Phase 3A missing manifest status", "Phase 2A superseded legacy worktree"]:
        fail("deferred maintenance changed")
    if final.get("release_created") is not False or final.get("tag_created") is not False or final.get("final_manifest_path") != FINAL_MANIFEST:
        fail("release/tag/final-manifest boundary changed")
    if FINAL_MANIFEST in artifact_entries(final):
        fail("final manifest self-inclusion")
    final_result = verify_manifest(FINAL_MANIFEST, expected_paths=FINAL_ARTIFACTS, expected_count=len(FINAL_ARTIFACTS))

    working = verify_manifest(WORKING_MANIFEST, expected_paths=WORKING_ARTIFACTS, expected_count=len(WORKING_ARTIFACTS))
    if working.get("phase") != "16B" or working.get("status") != "implemented_validated_pending_sol_acceptance" or working.get("source_commit") != WORKING_SOURCE_COMMIT:
        fail("working manifest identity changed")
    check = load_json(ARTIFACT_CHECK)
    if check.get("phase") != "16B" or check.get("passed") is not True or check.get("errors") != [] or check.get("counts") != EXPECTED_COUNTS:
        fail("Phase 16B artifact check is not the accepted passed result")
    r_result = load_json(R_RESULT)
    if r_result.get("phase") != "16B" or r_result.get("passed") is not True or r_result.get("counts") != EXPECTED_COUNTS or r_result.get("errors") != []:
        fail("Phase 16B R result is not the accepted passed result")

    verify_final_review()
    verify_failed_lineage()
    system_ids = registry_system_ids()
    verify_registry_membership(system_ids)
    package_counts = verify_package(system_ids)
    verify_figures()
    verify_prior_phase_manifests()
    prior_entries, prior_paths = prior_inventory()

    changed = changed_paths()
    allowed = set(STATUS_SURFACES) | {FINAL_MANIFEST, *FREEZE_VALIDATORS}
    if changed - allowed:
        fail(f"unexpected post-integration changes: {sorted(changed - allowed)}")
    if changed.intersection(prior_paths):
        fail(f"previously frozen artifact changed: {sorted(changed.intersection(prior_paths))}")
    if any("phase17" in path.lower() for path in changed):
        fail("Phase 17 content changed during freeze")
    verify_status_surfaces()

    output = {
        "status": "passed",
        "phase": "16B",
        "final_manifest": {"path": FINAL_MANIFEST, "entries": len(final_result["artifacts"])},
        "package_counts": package_counts,
        "review": {"passed": True, "blocking_arrays_empty": True, "failed_lineage_records": len(FAILED_REVIEWS)},
        "registry_systems": len(system_ids),
        "phase16a_phase14_phase15_integrity": "passed",
        "prior_freeze_integrity": {"entries": prior_entries, "unique_paths": len(prior_paths)},
        "changed_paths": sorted(changed),
        "release_created": False,
        "tag_created": False,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
