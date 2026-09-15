#!/usr/bin/env python3
"""Authoritative validator for the Phase 16B compound stress-test package.

This validator intentionally reads the frozen Phase 16A/15A/15B artifacts as
source data.  It rejects new rule IDs, endpoint reversals, stronger evidence,
scenario erasure, unsupported continuation, scores, forecasts, and canonical
Atlas/story claims.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = ROOT / "data/processed/integration"
SCENARIOS = ROOT / "data/processed/scenarios"
ANALYSIS = ROOT / "data/processed/analysis"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "outputs/figures"
SYSTEMS_PATH = ROOT / "metadata/atlas_systems.yml"
SYSTEMS_SOURCE = "metadata/atlas_systems.yml"

BASE_SHA = "9308127065112d0c01c294e954ae87f44e39af3f"
PHASE16A_FREEZE = REPORTS / "phase16a_integrated_basin_dynamics_freeze_manifest.json"
PHASE14A_FREEZE = REPORTS / "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
PHASE14B_FREEZE = REPORTS / "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
PHASE15A_FREEZE = REPORTS / "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
PHASE15B_FREEZE = REPORTS / "phase15b_technology_convergence_futures_freeze_manifest.json"
MANIFEST = REPORTS / "phase16b_manifest.json"
CHECK = REPORTS / "phase16b_artifact_check.json"
REVIEW = REPORTS / "phase16b_independent_review.md"

OUTPUTS = {
    "definitions": (INTEGRATION / "phase16b_stress_test_definitions.csv", {"test_id", "candidate_id", "test_class", "label", "stressor_ids", "stressor_initial_system_ids", "phase16a_rule_inputs", "implementation_status", "fan_out_semantics", "selection_basis", "boundary", "notes"}),
    "stages": (INTEGRATION / "phase16b_chain_stages.csv", {"stage_id", "test_id", "branch_id", "stage", "stage_status", "phase16a_stressor_id", "stressor_initial_system_id", "phase16a_rule_id", "phase16a_chain_parent_rule_id", "stage_parent_id", "chain_relation_type", "source_system_id", "target_system_id", "phase16a_relationship_id", "relationship_class", "propagation_mechanism", "stressor_evidence_class", "evidence_class", "lineage_evidence_class", "application_fit", "direct_or_inferred", "baseline_or_scenario", "scenario_state_ids", "scenario_condition", "source_state_or_effect", "system_effect", "technology_modifier_ids", "governance_modifier", "phase16a_response_id", "response_mechanism", "second_order_effect", "uncertainty", "source_lineage", "response_capacity_boundary", "notes"}),
    "terminations": (INTEGRATION / "phase16b_chain_terminations.csv", {"termination_id", "test_id", "branch_id", "phase16a_stressor_id", "initial_system_id", "last_stage_id", "last_stage", "last_target_system_id", "baseline_or_scenario", "scenario_condition", "termination_status", "termination_basis", "continuation_check", "defensible_branch_termination", "notes"}),
    "system_states": (INTEGRATION / "phase16b_system_states.csv", {"state_id", "test_id", "branch_id", "stage_id", "stage", "position", "system_id", "state_descriptor", "evidence_class", "baseline_or_scenario", "scenario_state_ids", "phase16a_rule_id", "source_lineage", "notes"}),
    "responses": (INTEGRATION / "phase16b_response_adaptation_states.csv", {"response_state_id", "test_id", "branch_id", "stage_id", "stage", "phase16a_rule_id", "phase16a_response_id", "response_mechanism", "response_evidence_class", "adaptation_state", "enabling_condition", "limiting_condition", "capacity_boundary", "source_lineage", "scenario_condition", "notes"}),
    "regimes": (INTEGRATION / "phase16b_regime_effects.csv", {"regime_effect_id", "test_id", "regime_id", "scenario_id", "horizon", "scenario_family", "phase16a_technology_modifier_id", "phase16a_rule_ids", "phase15_modifier_lineage_ids", "phase15_anchor_state_ids", "phase15_state_evidence_class", "observability_effect", "coupling_effect", "dependency_effect", "redundancy_effect", "coordination_effect", "substitution_effect", "governance_friction_effect", "digital_dependence_effect", "phase16a_allowed_effects", "relationship_status", "uncertainty", "source_lineage", "notes"}),
    "uncertainties": (INTEGRATION / "phase16b_uncertainties.csv", {"uncertainty_id", "test_id", "uncertainty_domain", "subject", "uncertainty_level", "phase16a_rule_ids", "what_is_unknown", "what_is_not_inferred", "scenario_condition", "source_lineage", "notes"}),
    "comparison": (INTEGRATION / "phase16b_cross_test_comparison.csv", {"test_id", "label", "principal_stressor_count", "branch_count", "stage_count", "system_state_observations", "response_adaptation_states", "termination_count", "scenario_conditioned_stage_count", "fan_out_summary", "cross_system_interfaces", "regime_a_finding", "regime_b_finding", "regime_c_finding", "comparison_boundary", "source_basis"}),
    "hooks": (INTEGRATION / "phase16b_narrative_hooks.csv", {"hook_id", "test_id", "test_label", "system_place_setting", "operational_decision_point", "human_institutional_role", "observable_sign_of_strain", "adaptation_response_moment", "scientific_lineage", "status", "canon_boundary", "notes"}),
}

EXPECTED_TESTS = (
    "P16B-CAND-001",
    "P16B-CAND-002",
    "P16B-CAND-003",
    "P16B-CAND-004",
)
RESERVE_TESTS = ("P16B-CAND-005", "P16B-CAND-006")
EXPECTED_BRANCHES: dict[str, list[tuple[str, str, list[str]]]] = {
    "P16B-CAND-001": [
        ("P16B-001-HEAT", "STRESS-HEAT-EXTREME", ["RULE-16A-001"]),
        ("P16B-001-LOW-FLOW", "STRESS-LOW-FLOW-DROUGHT", ["RULE-16A-005", "RULE-16A-006"]),
        ("P16B-001-GRID", "STRESS-ELECTRIC-GRID", ["RULE-16A-016"]),
    ],
    "P16B-CAND-002": [
        ("P16B-002-HAB", "STRESS-HAB-WATER-QUALITY", ["RULE-16A-012"]),
        ("P16B-002-TREATMENT-ENERGY", "STRESS-WATER-TREATMENT", ["RULE-16A-014"]),
        ("P16B-002-TREATMENT-DISEASE", "STRESS-WATER-TREATMENT", ["RULE-16A-015"]),
    ],
    "P16B-CAND-003": [
        ("P16B-003-TRANSPORT", "STRESS-TRANSPORT-FREIGHT", ["RULE-16A-019"]),
        ("P16B-003-CRITICAL-MATERIAL", "STRESS-CRITICAL-MATERIAL", []),
        ("P16B-003-FUEL", "STRESS-FUEL-CONSTRAINT", ["RULE-16A-020"]),
        ("P16B-003-FEEDSTOCK", "STRESS-INDUSTRIAL-FEEDSTOCK", []),
    ],
    "P16B-CAND-004": [
        ("P16B-004-INFECTIOUS-DATA", "STRESS-INFECTIOUS-PRESSURE", ["RULE-16A-022"]),
        ("P16B-004-INFECTIOUS-GOVERNANCE", "STRESS-INFECTIOUS-PRESSURE", ["RULE-16A-023"]),
        ("P16B-004-SURVEILLANCE", "STRESS-SURVEILLANCE-STRAIN", ["RULE-16A-026"]),
        ("P16B-004-PRIVACY", "STRESS-DATA-PRIVACY", ["RULE-16A-033"]),
    ],
}
REGIME_MODIFIERS = {"A": "TM-16A-009", "B": "TM-16A-010", "C": "TM-16A-011"}
REGIME_FAMILIES = {
    "A": "Coordinated Technological Adaptation",
    "B": "Uneven Networked Modernization",
    "C": "High Capability / High Friction Basin",
}
REGIME_AXIS_FIELDS = (
    "observability_effect", "coupling_effect", "dependency_effect", "redundancy_effect",
    "coordination_effect", "substitution_effect", "governance_friction_effect", "digital_dependence_effect",
)
TERMINATION_STATUS = "TERMINATED — NO DEFENSIBLE CURRENT PATH"
SCENARIO_REF_RE = re.compile(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+")
FORBIDDEN_FIELDS = {
    "risk_score", "resilience_score", "vulnerability_score", "severity_score", "connectivity_score",
    "probability", "probability_estimate", "economic_loss_forecast", "health_outcome_forecast",
    "incidence_rate", "outbreak_probability", "forecast_value",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    assert path.is_file() and path.stat().st_size > 0, path
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


SYSTEM_ID_TOKEN_RE = re.compile(r"SYS-[A-Z0-9]+(?:-[A-Z0-9]+)*")
SYSTEM_IDENTIFIER_FIELDS = {
    "system_id",
    "system_ids",
    "initial_system_id",
    "source_system_id",
    "target_system_id",
    "source_system",
    "target_system",
    "stressor_initial_system_id",
    "stressor_initial_system_ids",
    "last_target_system_id",
}
OPTIONAL_SYSTEM_IDENTIFIER_FIELDS = {"last_target_system_id"}


def load_authoritative_system_ids(path: Path = SYSTEMS_PATH) -> frozenset[str]:
    try:
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError("file is missing or empty")
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(
            f"authoritative system registry cannot be loaded: path={path}; "
            f"source={SYSTEMS_SOURCE}; error={error}"
        ) from error
    if not isinstance(payload, dict) or not isinstance(payload.get("systems"), list) or not payload["systems"]:
        raise RuntimeError(
            "authoritative system registry is empty or malformed: "
            f"path={path}; source={SYSTEMS_SOURCE}"
        )
    ids: list[str] = []
    for index, record in enumerate(payload["systems"], start=1):
        if not isinstance(record, dict):
            raise RuntimeError(
                "authoritative system registry contains a non-record entry: "
                f"record_index={index}; path={path}; source={SYSTEMS_SOURCE}"
            )
        missing = object()
        raw_system_id = record.get("system_id", missing)
        if raw_system_id is missing:
            raise RuntimeError(
                "authoritative system registry record is missing system ID: "
                f"record_index={index}; path={path}; source={SYSTEMS_SOURCE}"
            )
        if type(raw_system_id) is not str:
            raise RuntimeError(
                "authoritative system registry system ID must be a YAML string: "
                f"record_index={index}; raw_type={type(raw_system_id).__name__}; "
                f"path={path}; source={SYSTEMS_SOURCE}"
            )
        if not raw_system_id:
            raise RuntimeError(
                "authoritative system registry contains a blank system ID: "
                f"record_index={index}; path={path}; source={SYSTEMS_SOURCE}"
            )
        if not raw_system_id.strip():
            raise RuntimeError(
                "authoritative system registry contains a whitespace-only system ID: "
                f"record_index={index}; path={path}; source={SYSTEMS_SOURCE}"
            )
        if raw_system_id != raw_system_id.strip():
            raise RuntimeError(
                "authoritative system registry system ID has leading or trailing whitespace: "
                f"record_index={index}; path={path}; source={SYSTEMS_SOURCE}"
            )
        ids.append(raw_system_id)
    duplicates = sorted({system_id for system_id in ids if ids.count(system_id) > 1})
    if duplicates:
        raise RuntimeError(
            "authoritative system registry contains duplicate IDs: "
            f"record_ids={duplicates}; path={path}; source={SYSTEMS_SOURCE}"
        )
    return frozenset(ids)


def system_membership_errors(
    rows: list[dict[str, str]],
    record_id_field: str,
    system_ids: frozenset[str],
) -> list[str]:
    errors: list[str] = []
    for row in rows:
        record_id = str(row.get(record_id_field, "<missing>"))
        selected_fields = [
            field
            for field in row
            if field in SYSTEM_IDENTIFIER_FIELDS
            or field.endswith("_system_id")
            or field.endswith("_system_ids")
        ]
        for field in selected_fields:
            raw_value = str(row.get(field, ""))
            values = raw_value.split(";") if field.endswith("_system_ids") or field == "system_ids" else [raw_value]
            if not raw_value and field in OPTIONAL_SYSTEM_IDENTIFIER_FIELDS:
                values = []
            for value in values:
                value = value.strip()
                if not value and field in OPTIONAL_SYSTEM_IDENTIFIER_FIELDS:
                    continue
                if not value or value not in system_ids:
                    errors.append(
                        f"record_id={record_id}; field={field}; invalid_system_id={value or '<blank>'}; "
                        f"authoritative_registry={SYSTEMS_SOURCE}"
                    )
        for field, value in row.items():
            for system_id in SYSTEM_ID_TOKEN_RE.findall(str(value)):
                if system_id not in system_ids:
                    errors.append(
                        f"record_id={record_id}; field={field}; invalid_system_id={system_id}; "
                        f"authoritative_registry={SYSTEMS_SOURCE}"
                    )
    return list(dict.fromkeys(errors))


def read_output(name: str) -> list[dict[str, str]]:
    path, expected = OUTPUTS[name]
    rows = read_csv(path)
    assert rows, path
    assert set(rows[0]) == expected, (name, sorted(set(rows[0]) ^ expected))
    return rows


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_hash_matches(path: Path, expected: str) -> bool:
    raw = path.read_bytes()
    if sha256(raw) == expected:
        return True
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(normalized) == expected


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(entries, dict)
    return entries


def verify_freeze(path: Path, phase: str, count: int) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload.get("accepted_phase") == phase, path
    assert payload.get("status") == "ACCEPTED / FROZEN", path
    entries = artifact_entries(payload)
    assert len(entries) == count, (path, len(entries))
    paths: set[str] = set()
    for relative, value in entries.items():
        expected = value if isinstance(value, str) else str(value["sha256"])
        target = ROOT / relative
        assert target.is_file() and portable_hash_matches(target, expected), (path.name, relative)
        paths.add(relative.replace("\\", "/"))
    return paths


def prior_integrity() -> tuple[int, set[str]]:
    total = 0
    paths: set[str] = set()
    manifests = sorted(REPORTS.glob("*freeze_manifest.json"))
    assert manifests, "freeze manifests"
    for path in manifests:
        for relative, value in artifact_entries(json.loads(path.read_text(encoding="utf-8"))).items():
            expected = value if isinstance(value, str) else str(value["sha256"])
            target = ROOT / relative
            assert target.is_file() and portable_hash_matches(target, expected), (path.name, relative)
            total += 1
            paths.add(relative.replace("\\", "/"))
    return total, paths


def changed_paths() -> set[str]:
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True)
    untracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"], text=True)
    return {line.replace("\\", "/") for line in (tracked + untracked).splitlines() if line}


def split_ids(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def lineage_refs(value: str) -> list[str]:
    return unique(SCENARIO_REF_RE.findall(value))


def expected_rule_ids(test_id: str) -> list[str]:
    return [rule_id for _, _, rule_ids in EXPECTED_BRANCHES[test_id] for rule_id in rule_ids]


def exact_stage_rule_fields(stage: dict[str, str], rule: dict[str, str], stressor: dict[str, str], relationship: dict[str, str], response: dict[str, str]) -> list[str]:
    mismatches = []
    expected = {
        "phase16a_stressor_id": rule["stressor_id"],
        "stressor_initial_system_id": stressor["initial_system_id"],
        "phase16a_chain_parent_rule_id": rule["chain_parent_rule_id"],
        "chain_relation_type": rule["chain_relation_type"],
        "source_system_id": rule["source_system_id"],
        "target_system_id": rule["target_system_id"],
        "phase16a_relationship_id": rule["relationship_id"],
        "relationship_class": relationship["relationship_class"],
        "propagation_mechanism": relationship["propagation_mechanism"],
        "stressor_evidence_class": stressor["evidence_class"],
        "evidence_class": rule["evidence_class"],
        "lineage_evidence_class": relationship["evidence_class"],
        "application_fit": rule["application_fit"],
        "direct_or_inferred": rule["direct_or_inferred"],
        "baseline_or_scenario": rule["baseline_or_scenario"],
        "source_state_or_effect": rule["source_state_or_effect"],
        "system_effect": rule["initial_or_prior_effect"],
        "technology_modifier_ids": rule["technology_modifier"],
        "governance_modifier": rule["governance_modifier"],
        "phase16a_response_id": rule["response_option"],
        "response_mechanism": response["response_mechanism"],
        "second_order_effect": rule["second_order_effect"],
        "uncertainty": rule["uncertainty"],
        "source_lineage": rule["source_lineage"],
        "response_capacity_boundary": response["adaptation_capacity_boundary"],
    }
    for field, value in expected.items():
        if stage[field] != value:
            mismatches.append(field)
    expected_refs = lineage_refs(rule["source_lineage"])
    if split_ids(stage["scenario_state_ids"]) != expected_refs:
        mismatches.append("scenario_state_ids")
    expected_status = "SCENARIO-CONDITIONED OPTIONAL STAGE" if rule["baseline_or_scenario"] == "scenario-conditioned" else "SELECTED QUALITATIVE STAGE"
    if stage["stage_status"] != expected_status:
        mismatches.append("stage_status")
    if stage["scenario_condition"] != (
        f"Phase 15B state reference(s) {stage['scenario_state_ids']}; not a baseline path"
        if expected_refs else "baseline Phase 16A rule application; no future scenario state is asserted"
    ):
        mismatches.append("scenario_condition")
    return mismatches


REVIEW_REQUIRED_FIELDS = (
    "passed", "security_concerns", "logic_errors", "provenance_errors", "chain_errors",
    "propagation_errors", "evidence_classification_errors", "scenario_boundary_errors",
    "technology_modifier_errors", "biosecurity_boundary_errors", "atlas_bridge_errors",
    "canon_boundary_errors", "suggestions", "summary",
)
REVIEW_BLOCKING_ARRAY_FIELDS = tuple(field for field in REVIEW_REQUIRED_FIELDS if field not in {"passed", "suggestions", "summary"})


def review_ok() -> tuple[bool, str]:
    if not REVIEW.is_file():
        return False, "review record absent"
    text = REVIEW.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if not match:
        return False, "review JSON block absent"
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return False, f"review JSON invalid: {exc.msg}"
    if not isinstance(payload, dict) or set(payload) != set(REVIEW_REQUIRED_FIELDS):
        return False, "review schema is not the current Phase 16B schema"
    if type(payload["passed"]) is not bool:
        return False, "review passed must be boolean"
    for field in REVIEW_BLOCKING_ARRAY_FIELDS + ("suggestions",):
        value = payload[field]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            return False, f"review field {field} must be an array of strings"
    if not isinstance(payload["summary"], str) or not payload["summary"].strip():
        return False, "review summary must be a nonempty string"
    blocking = [key for key in REVIEW_BLOCKING_ARRAY_FIELDS if payload[key]]
    if payload["passed"] is not True:
        return False, "review passed is not true"
    if blocking:
        return False, f"passed:true with non-empty blocking arrays: {blocking}"
    return True, "passed:true; complete schema; all blocking arrays empty"


def main() -> int:
    require_review = "--require-review" in sys.argv
    checks: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: Any) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    phase16a_paths = verify_freeze(PHASE16A_FREEZE, "16A", 30)
    phase14a_paths = verify_freeze(PHASE14A_FREEZE, "14A", 24)
    phase14b_paths = verify_freeze(PHASE14B_FREEZE, "14B", 23)
    phase15a_paths = verify_freeze(PHASE15A_FREEZE, "15A", 30)
    phase15b_paths = verify_freeze(PHASE15B_FREEZE, "15B", 28)
    prior_total, prior_paths = prior_integrity()
    changed = changed_paths()
    protected = prior_paths | phase16a_paths | phase14a_paths | phase14b_paths | phase15a_paths | phase15b_paths
    check("expected_starting_sha", subprocess.check_output(["git", "-C", str(ROOT), "merge-base", "HEAD", BASE_SHA], text=True).strip() == BASE_SHA, BASE_SHA)
    check("phase16a_accepted_frozen", json.loads(PHASE16A_FREEZE.read_text(encoding="utf-8")).get("status") == "ACCEPTED / FROZEN", "Phase 16A")
    phase14b_manifest = json.loads(PHASE14B_FREEZE.read_text(encoding="utf-8"))
    phase15b_manifest = json.loads(PHASE15B_FREEZE.read_text(encoding="utf-8"))
    check("phase14_overall_status", phase14b_manifest.get("phase14_overall_status") == "COMPLETE / ACCEPTED / FROZEN", phase14b_manifest.get("phase14_overall_status"))
    check("phase15_overall_status", phase15b_manifest.get("phase15_overall_status") == "COMPLETE / ACCEPTED / FROZEN", phase15b_manifest.get("phase15_overall_status"))
    check("prior_freeze_integrity", prior_total == 623 and len(prior_paths) == 614, {"entries": prior_total, "unique_paths": len(prior_paths)})
    check("no_prior_frozen_artifact_modified", not changed.intersection(protected), sorted(changed.intersection(protected)))
    check("phase16a_package_unchanged", not changed.intersection(phase16a_paths), sorted(changed.intersection(phase16a_paths)))
    check("phase17_not_implemented", not any("phase17" in path.lower() for path in changed), sorted(path for path in changed if "phase17" in path.lower()))
    check("no_release_or_tag", not any("release" in path.lower() or "/tags/" in path.lower() for path in changed), "release/tag out of scope")

    system_ids = load_authoritative_system_ids()
    check("phase14_system_ontology", len(system_ids) == 13, sorted(system_ids))
    phase16a_stressors = {row["stressor_id"]: row for row in read_csv(INTEGRATION / "stressor_catalog.csv")}
    phase16a_rules = {row["rule_id"]: row for row in read_csv(INTEGRATION / "propagation_rules.csv")}
    phase16a_relationships = {row["relationship_id"]: row for row in read_csv(INTEGRATION / "propagation_relationships.csv")}
    phase16a_responses = {row["response_id"]: row for row in read_csv(INTEGRATION / "adaptation_response_catalog.csv")}
    phase16a_modifiers = {row["technology_modifier_id"]: row for row in read_csv(INTEGRATION / "technology_modifier_catalog.csv")}
    phase15_states = {row["state_id"]: row for row in read_csv(SCENARIOS / "technology_system_states.csv")}
    phase15_dependencies = {row["dependency_state_id"]: row for row in read_csv(SCENARIOS / "technology_dependency_states.csv")}
    phase15_governance = {row["governance_state_id"]: row for row in read_csv(SCENARIOS / "technology_governance_states.csv")}

    frames = {name: read_output(name) for name in OUTPUTS}
    definitions = frames["definitions"]
    stages = frames["stages"]
    terminations = frames["terminations"]
    state_rows = frames["system_states"]
    response_rows = frames["responses"]
    regime_rows = frames["regimes"]
    uncertainty_rows = frames["uncertainties"]
    comparison_rows = frames["comparison"]
    hook_rows = frames["hooks"]

    definition_map = {row["test_id"]: row for row in definitions}
    check("definition_count_and_ids", len(definitions) == 6 and len(definition_map) == 6 and set(definition_map) == set(EXPECTED_TESTS + RESERVE_TESTS), len(definitions))
    check("exactly_four_principal_tests", {row["test_id"] for row in definitions if row["test_class"] == "PRINCIPAL"} == set(EXPECTED_TESTS), sorted(row["test_id"] for row in definitions if row["test_class"] == "PRINCIPAL"))
    check("two_reserve_tests_unimplemented", {row["test_id"] for row in definitions if row["test_class"] == "RESERVE"} == set(RESERVE_TESTS) and all(row["implementation_status"] == "RESERVE / UNIMPLEMENTED" for row in definitions if row["test_class"] == "RESERVE"), "reserve status")
    definition_errors = []
    candidate_rows = {row["candidate_id"]: row for row in read_csv(INTEGRATION / "phase16b_candidate_stress_tests.csv")}
    for row in definitions:
        candidate = candidate_rows.get(row["candidate_id"])
        if not candidate or row["test_id"] != row["candidate_id"]:
            definition_errors.append(row["test_id"])
            continue
        if row["stressor_ids"] != candidate["stressor_ids"] or row["phase16a_rule_inputs"] != candidate["phase16a_rule_inputs"]:
            definition_errors.append(row["test_id"] + ": candidate lineage")
        stressor_ids = split_ids(row["stressor_ids"])
        if not stressor_ids or any(item not in phase16a_stressors for item in stressor_ids):
            definition_errors.append(row["test_id"] + ": stressor resolution")
        else:
            expected_initial = unique([phase16a_stressors[item]["initial_system_id"] for item in stressor_ids])
            if split_ids(row["stressor_initial_system_ids"]) != expected_initial:
                definition_errors.append(row["test_id"] + ": initial systems")
        if not row["fan_out_semantics"].startswith("parallel initial branches"):
            definition_errors.append(row["test_id"] + ": fan-out")
    check("definition_lineage_and_initial_systems", not definition_errors, definition_errors)
    check("reserve_source_rows_unchanged_semantics", all(candidate_rows[item]["status"] == "APPROVED SCOPE / NOT IMPLEMENTED" and candidate_rows[item]["executed"] == "false" for item in RESERVE_TESTS), "Phase 16A candidates 005/006")

    selected_rule_ids = {
        rule_id
        for test_id in EXPECTED_TESTS
        for _, _, rule_ids in EXPECTED_BRANCHES[test_id]
        for rule_id in rule_ids
    }
    selected_rule_rows = [phase16a_rules[rule_id] for rule_id in sorted(selected_rule_ids)]
    selected_relationship_ids = {row["relationship_id"] for row in selected_rule_rows}
    selected_relationship_rows = [
        phase16a_relationships[relationship_id]
        for relationship_id in sorted(selected_relationship_ids)
    ]
    membership_errors: list[str] = []
    membership_errors.extend(system_membership_errors(list(phase16a_stressors.values()), "stressor_id", system_ids))
    membership_errors.extend(system_membership_errors(list(candidate_rows.values()), "candidate_id", system_ids))
    membership_errors.extend(system_membership_errors(selected_rule_rows, "rule_id", system_ids))
    membership_errors.extend(system_membership_errors(selected_relationship_rows, "relationship_id", system_ids))
    output_record_fields = {
        "definitions": "test_id",
        "stages": "stage_id",
        "terminations": "termination_id",
        "system_states": "state_id",
        "responses": "response_state_id",
        "regimes": "regime_effect_id",
        "uncertainties": "uncertainty_id",
        "comparison": "test_id",
        "hooks": "hook_id",
    }
    for output_name, record_id_field in output_record_fields.items():
        membership_errors.extend(system_membership_errors(frames[output_name], record_id_field, system_ids))
    check("authoritative_system_membership", not membership_errors, membership_errors)

    stage_map = {row["stage_id"]: row for row in stages}
    check("chain_stage_count", len(stages) == 13 and len(stage_map) == 13, len(stages))
    stage_errors = []
    for test_id in EXPECTED_TESTS:
        actual_rule_ids = [row["phase16a_rule_id"] for row in stages if row["test_id"] == test_id]
        check(f"stage_rule_set_{test_id}", actual_rule_ids == expected_rule_ids(test_id), actual_rule_ids)
    check("no_reserve_stages", not any(row["test_id"] in RESERVE_TESTS for row in stages), sorted({row["test_id"] for row in stages if row["test_id"] in RESERVE_TESTS}))
    for row in stages:
        rule = phase16a_rules.get(row["phase16a_rule_id"])
        stressor = phase16a_stressors.get(row["phase16a_stressor_id"])
        relationship = phase16a_relationships.get(row["phase16a_relationship_id"])
        response = phase16a_responses.get(row["phase16a_response_id"])
        if not rule or not stressor or not relationship or not response:
            stage_errors.append(row["stage_id"] + ": unresolved Phase 16A source")
            continue
        if row["test_id"] not in EXPECTED_TESTS or row["phase16a_stressor_id"] != rule["stressor_id"]:
            stage_errors.append(row["stage_id"] + ": test/stressor")
        stage_errors.extend(f"{row['stage_id']}: {field}" for field in exact_stage_rule_fields(row, rule, stressor, relationship, response))
        for modifier_id in split_ids(row["technology_modifier_ids"]):
            if modifier_id != "NONE" and modifier_id not in phase16a_modifiers:
                stage_errors.append(row["stage_id"] + ": technology modifier " + modifier_id)
        if row["baseline_or_scenario"] == "scenario-conditioned":
            refs = split_ids(row["scenario_state_ids"])
            if not refs or any(ref not in phase15_dependencies and ref not in phase15_states and ref not in phase15_governance for ref in refs):
                stage_errors.append(row["stage_id"] + ": scenario state resolution")
            if row["evidence_class"] not in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}:
                stage_errors.append(row["stage_id"] + ": scenario evidence")
        elif row["scenario_state_ids"] or row["evidence_class"] in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}:
            stage_errors.append(row["stage_id"] + ": scenario leakage")
    check("stage_source_relationship_response_resolution", not stage_errors, stage_errors)

    branch_errors = []
    expected_branch_keys = set()
    for test_id, branches in EXPECTED_BRANCHES.items():
        actual = {row["branch_id"]: row for row in stages if row["test_id"] == test_id}
        for branch_id, stressor_id, rule_ids in branches:
            expected_branch_keys.add((test_id, branch_id))
            rows = sorted([row for row in stages if row["test_id"] == test_id and row["branch_id"] == branch_id], key=lambda item: int(item["stage"]))
            if [row["phase16a_rule_id"] for row in rows] != rule_ids:
                if rule_ids or rows:
                    branch_errors.append(branch_id + ": stage/rule sequence")
            if rows:
                for index, row in enumerate(rows):
                    if row["phase16a_stressor_id"] != stressor_id:
                        branch_errors.append(branch_id + ": stressor branch")
                    if index == 0:
                        if row["chain_relation_type"] != "parallel_initial_branch" or row["stage_parent_id"]:
                            branch_errors.append(branch_id + ": initial fan-out")
                    else:
                        parent = rows[index - 1]
                        if row["chain_relation_type"] != "sequential" or row["stage_parent_id"] != parent["stage_id"] or row["phase16a_chain_parent_rule_id"] != parent["phase16a_rule_id"] or parent["target_system_id"] != row["source_system_id"] or int(row["stage"]) != int(parent["stage"]) + 1:
                            branch_errors.append(branch_id + ": sequential continuity")
            elif rule_ids:
                branch_errors.append(branch_id + ": missing selected stage")
    stage_branch_keys = {(row["test_id"], row["branch_id"]) for row in stages}
    check("explicit_fan_out_and_chain_continuity", not branch_errors and stage_branch_keys <= expected_branch_keys, branch_errors)
    check("no_unsupported_propagation", set(row["phase16a_rule_id"] for row in stages) <= set(phase16a_rules) and all(row["phase16a_rule_id"] in expected_rule_ids(row["test_id"]) for row in stages), "all stages are selected frozen rules")
    check("endpoint_direction", all(row["source_system_id"] == phase16a_relationships[row["phase16a_relationship_id"]]["source_system_id"] and row["target_system_id"] == phase16a_relationships[row["phase16a_relationship_id"]]["target_system_id"] for row in stages), "ordered source -> target")

    termination_map = {(row["test_id"], row["branch_id"]): row for row in terminations}
    expected_termination_keys = {(test_id, branch_id) for test_id, branches in EXPECTED_BRANCHES.items() for branch_id, _, _ in branches}
    termination_errors = []
    response_stage_ids = {row["stage_id"] for row in response_rows}
    check("termination_row_count", len(terminations) == 14 and set(termination_map) == expected_termination_keys, {"rows": len(terminations), "expected": len(expected_termination_keys)})
    for test_id, branches in EXPECTED_BRANCHES.items():
        for branch_id, stressor_id, rule_ids in branches:
            row = termination_map.get((test_id, branch_id))
            if not row:
                termination_errors.append(branch_id + ": missing termination")
                continue
            expected_stages = [stage for stage in stages if stage["test_id"] == test_id and stage["branch_id"] == branch_id]
            expected_stages.sort(key=lambda item: int(item["stage"]))
            last = expected_stages[-1] if expected_stages else None
            expected = {
                "phase16a_stressor_id": stressor_id,
                "initial_system_id": phase16a_stressors[stressor_id]["initial_system_id"],
                "last_stage_id": last["stage_id"] if last else "",
                "last_stage": last["stage"] if last else "0",
                "last_target_system_id": last["target_system_id"] if last else "",
                "termination_status": TERMINATION_STATUS,
                "defensible_branch_termination": "true",
            }
            for field, value in expected.items():
                if row[field] != value:
                    termination_errors.append(branch_id + ": " + field)
            if last:
                valid_continuations = [
                    rule_id
                    for rule_id, candidate in phase16a_rules.items()
                    if (
                        candidate["stressor_id"] == stressor_id
                        and candidate["chain_parent_rule_id"] == last["phase16a_rule_id"]
                        and candidate["chain_relation_type"] == "sequential"
                        and candidate["source_system_id"] == last["target_system_id"]
                        and int(candidate["stage"]) == int(last["stage"]) + 1
                    )
                ]
                if valid_continuations:
                    termination_errors.append(branch_id + ": valid unused continuation " + ";".join(valid_continuations))
                if last["stage_id"] not in response_stage_ids:
                    termination_errors.append(branch_id + ": final response/adaptation state missing")
            else:
                unselected_rules = [rule_id for rule_id, candidate in phase16a_rules.items() if candidate["stressor_id"] == stressor_id]
                if unselected_rules:
                    termination_errors.append(branch_id + ": unselected Phase 16A rule " + ";".join(unselected_rules))
            if not row["continuation_check"] or "Phase 16A" not in row["continuation_check"] or "rule" not in row["continuation_check"] or not row["notes"]:
                termination_errors.append(branch_id + ": termination basis")
            if not last and row["termination_basis"] != "NO_PHASE16A_RULE_FOR_STRESSOR":
                termination_errors.append(branch_id + ": no-rule basis")
            if last and row["termination_basis"] != "NO_LATER_PHASE16A_RULE_FOR_SAME_STRESSOR_AND_TARGET":
                termination_errors.append(branch_id + ": continuation basis")
    check("defensible_branch_termination", not termination_errors, termination_errors)

    state_errors = []
    states_by_stage: dict[str, list[dict[str, str]]] = {}
    for row in state_rows:
        states_by_stage.setdefault(row["stage_id"], []).append(row)
        stage = stage_map.get(row["stage_id"])
        if not stage or row["test_id"] != stage["test_id"] or row["branch_id"] != stage["branch_id"] or row["phase16a_rule_id"] != stage["phase16a_rule_id"] or row["stage"] != stage["stage"] or row["evidence_class"] != stage["evidence_class"] or row["baseline_or_scenario"] != stage["baseline_or_scenario"] or row["scenario_state_ids"] != stage["scenario_state_ids"] or row["source_lineage"] != stage["source_lineage"]:
            state_errors.append(row["state_id"] + ": stage lineage")
        elif row["position"] == "source":
            if row["system_id"] != stage["source_system_id"] or row["state_descriptor"] != stage["source_state_or_effect"]:
                state_errors.append(row["state_id"] + ": source state")
        elif row["position"] == "target":
            if row["system_id"] != stage["target_system_id"] or row["state_descriptor"] != stage["system_effect"]:
                state_errors.append(row["state_id"] + ": target state")
        else:
            state_errors.append(row["state_id"] + ": position")
    check("system_state_count_and_resolution", len(state_rows) == 26 and all(len(states_by_stage.get(stage_id, [])) == 2 for stage_id in stage_map), state_errors)

    response_errors = []
    response_by_stage = {row["stage_id"]: row for row in response_rows}
    for row in response_rows:
        stage = stage_map.get(row["stage_id"])
        response = phase16a_responses.get(row["phase16a_response_id"])
        if not stage or not response or row["phase16a_rule_id"] != stage["phase16a_rule_id"] or row["phase16a_response_id"] != stage["phase16a_response_id"]:
            response_errors.append(row["response_state_id"] + ": rule/response resolution")
            continue
        expected = {
            "test_id": stage["test_id"], "branch_id": stage["branch_id"], "stage": stage["stage"],
            "response_mechanism": response["response_mechanism"], "response_evidence_class": response["evidence_class"],
            "enabling_condition": response["enabling_condition"], "limiting_condition": response["limiting_condition"],
            "capacity_boundary": response["adaptation_capacity_boundary"], "source_lineage": response["source_lineage"],
            "scenario_condition": stage["scenario_condition"],
        }
        response_errors.extend(row["response_state_id"] + ": " + field for field, value in expected.items() if row[field] != value)
        if "OPTION IDENTIFIED" not in row["adaptation_state"] or "INDETERMINATE" not in row["adaptation_state"] or "not guaranteed" not in row["notes"].lower():
            response_errors.append(row["response_state_id"] + ": option boundary")
    check("response_adaptation_count_and_resolution", len(response_rows) == 13 and set(response_by_stage) == set(stage_map) and not response_errors, response_errors)
    check("evidence_inheritance", all(row["evidence_class"] == phase16a_rules[row["phase16a_rule_id"]]["evidence_class"] and row["lineage_evidence_class"] == phase16a_relationships[row["phase16a_relationship_id"]]["evidence_class"] for row in stages), "stage evidence copied from frozen rule/relationship")

    modifier_errors = []
    for row in regime_rows:
        regime = row["regime_id"]
        scenario_id = row["scenario_id"]
        modifier_id = REGIME_MODIFIERS.get(regime)
        modifier = phase16a_modifiers.get(modifier_id or "")
        if regime not in REGIME_MODIFIERS or row["test_id"] not in EXPECTED_TESTS or scenario_id != f"{regime}{row['horizon']}" or row["scenario_family"] != REGIME_FAMILIES.get(regime):
            modifier_errors.append(row["regime_effect_id"] + ": regime identity")
            continue
        if row["phase16a_technology_modifier_id"] != modifier_id or not modifier:
            modifier_errors.append(row["regime_effect_id"] + ": Phase 16A modifier")
            continue
        expected_modifier_refs = lineage_refs(modifier["source_lineage"])
        if split_ids(row["phase15_modifier_lineage_ids"]) != expected_modifier_refs:
            modifier_errors.append(row["regime_effect_id"] + ": modifier lineage refs")
        expected_anchor = [f"TSS-{scenario_id}-01", f"TDS-{scenario_id}-01", f"TGS-{scenario_id}-01"]
        if split_ids(row["phase15_anchor_state_ids"]) != expected_anchor or any(ref not in phase15_states and ref not in phase15_dependencies and ref not in phase15_governance for ref in expected_anchor):
            modifier_errors.append(row["regime_effect_id"] + ": Phase 15 anchors")
        if row["phase15_state_evidence_class"] != "SCENARIO_STATE" or row["phase16a_rule_ids"] != ";".join(expected_rule_ids(row["test_id"])):
            modifier_errors.append(row["regime_effect_id"] + ": linked rules/evidence")
        if row["phase16a_allowed_effects"] != modifier["effects_allowed"]:
            modifier_errors.append(row["regime_effect_id"] + ": allowed effects")
        if any(not row[field] for field in REGIME_AXIS_FIELDS) or "NO NEW PROPAGATION PATHWAY" not in row["relationship_status"] or "not automatically protective" not in row["notes"].lower() or "ranking" not in row["notes"].lower():
            modifier_errors.append(row["regime_effect_id"] + ": regime boundary")
        if any(ref not in row["source_lineage"] for ref in expected_anchor) or modifier_id not in row["source_lineage"]:
            modifier_errors.append(row["regime_effect_id"] + ": source lineage")
    check("technology_modifier_resolution_and_regime_count", len(regime_rows) == 24 and len({row["regime_effect_id"] for row in regime_rows}) == 24 and len({(row["test_id"], row["regime_id"], row["horizon"]) for row in regime_rows}) == 24 and not modifier_errors, modifier_errors)
    check("technology_effects_are_allowed", all(all(term in row["phase16a_allowed_effects"] for term in ({"A": ("reduce propagation", "improve coordination", "increase observability"), "B": ("create substitution options", "increase coupling", "shift workforce requirements"), "C": ("increase observability", "increase coupling", "create governance / trust friction", "create cyber / digital exposure")}[row["regime_id"]])) for row in regime_rows), "Phase 16A allowed effect vocabulary")

    uncertainty_errors = []
    for row in uncertainty_rows:
        if row["test_id"] not in EXPECTED_TESTS or not row["phase16a_rule_ids"] or split_ids(row["phase16a_rule_ids"]) != unique([stage["phase16a_rule_id"] for stage in stages if stage["test_id"] == row["test_id"]]):
            uncertainty_errors.append(row["uncertainty_id"] + ": rule basis")
        if any(not row[field] for field in ("uncertainty_domain", "subject", "uncertainty_level", "what_is_unknown", "what_is_not_inferred", "source_lineage", "notes")) or "not converted into a probability" not in row["notes"]:
            uncertainty_errors.append(row["uncertainty_id"] + ": explicit uncertainty")
    check("uncertainty_resolution", len(uncertainty_rows) == 4 and {row["test_id"] for row in uncertainty_rows} == set(EXPECTED_TESTS) and not uncertainty_errors, uncertainty_errors)

    comparison_errors = []
    comparison_map = {row["test_id"]: row for row in comparison_rows}
    for test_id in EXPECTED_TESTS:
        row = comparison_map.get(test_id)
        test_stages = [stage for stage in stages if stage["test_id"] == test_id]
        test_terms = [term for term in terminations if term["test_id"] == test_id]
        if not row:
            comparison_errors.append(test_id + ": missing comparison")
            continue
        expected = {
            "principal_stressor_count": str(len(split_ids(definition_map[test_id]["stressor_ids"]))),
            "branch_count": str(len(test_terms)), "stage_count": str(len(test_stages)),
            "system_state_observations": str(len([state for state in state_rows if state["test_id"] == test_id])),
            "response_adaptation_states": str(len([response for response in response_rows if response["test_id"] == test_id])),
            "termination_count": str(len(test_terms)),
            "scenario_conditioned_stage_count": str(sum(stage["baseline_or_scenario"] == "scenario-conditioned" for stage in test_stages)),
        }
        comparison_errors.extend(test_id + ": " + field for field, value in expected.items() if row[field] != value)
        if any(term not in row["comparison_boundary"].lower() for term in ("qualitative", "no regime ranking", "probability")):
            comparison_errors.append(test_id + ": comparison boundary")
    check("cross_test_comparison", len(comparison_rows) == 4 and set(comparison_map) == set(EXPECTED_TESTS) and not comparison_errors, comparison_errors)

    hook_errors = []
    hook_map = {row["test_id"]: row for row in hook_rows}
    for test_id in EXPECTED_TESTS:
        row = hook_map.get(test_id)
        if not row:
            hook_errors.append(test_id + ": missing hook")
            continue
        if row["status"] != "NONCANONICAL / FUTURE ATLAS HOOK" or "not a character" not in row["canon_boundary"].lower() or "story canon" not in row["canon_boundary"].lower() or "fiction" not in row["canon_boundary"].lower():
            hook_errors.append(test_id + ": noncanonical status")
        rule_ids = [stage["phase16a_rule_id"] for stage in stages if stage["test_id"] == test_id]
        if any(rule_id not in row["scientific_lineage"] for rule_id in rule_ids) or any(not row[field] for field in ("system_place_setting", "operational_decision_point", "human_institutional_role", "observable_sign_of_strain", "adaptation_response_moment", "scientific_lineage")):
            hook_errors.append(test_id + ": hook fields/lineage")
        if "coordinate" in row["system_place_setting"].lower() and "no intake coordinate" not in row["system_place_setting"].lower():
            hook_errors.append(test_id + ": coordinate boundary")
    check("narrative_hooks_noncanonical", len(hook_rows) == 4 and set(hook_map) == set(EXPECTED_TESTS) and not hook_errors, hook_errors)

    all_csv_text = " ".join(" ".join(row.values()) for frame in frames.values() for row in frame).lower()
    all_report_text = " ".join(path.read_text(encoding="utf-8") for path in (REPORTS / "phase16b_compound_cross_system_stress_tests.md", REPORTS / "phase16b_qa.md", REPORTS / "phase16b_provenance_lineage.md", REPORTS / "phase16b_scenario_comparison.md", REPORTS / "phase16b_narrative_hooks.md")).lower()
    all_text = all_csv_text + " " + all_report_text
    fields = set().union(*(set(row) for frame in frames.values() for row in frame))
    check("no_forbidden_score_probability_forecast_fields", not fields.intersection(FORBIDDEN_FIELDS), sorted(fields.intersection(FORBIDDEN_FIELDS)))
    check("no_numeric_score_probability_forecast_claim", not re.search(r"(?:score|probability|forecast|risk|vulnerability|resilience|severity)\s*[:=]\s*[-+]?\d", all_text), "numeric prohibited claim")
    check("no_numeric_health_outcome_claim", not re.search(r"(?:cases?|incidence|deaths?|hospitalizations?|illness|dose)\s*[:=]\s*[-+]?\d", all_text), "numeric health claim")
    check("qualitative_boundary_language", all(term in all_text for term in ("propagation ≠ probability", "dependency ≠ guaranteed failure", "response option ≠ successful response", "ai recommendation ≠ authority")), "scientific boundaries")
    check("biosecurity_high_level", all(term in all_text for term in ("no pathogen engineering", "high-level only", "no operational attack")) and not re.search(r"(?:pathogen engineering method|transmission optimization procedure|evasion method instructions|laboratory procedure for harm)", all_text), "biosecurity boundary")
    check("no_phase17_content", "phase 17" in all_text and "not implemented" in all_text, "Phase 17 status")

    figure_terms = {
        "phase16b_compound_stress_propagation.svg": ("Compound Stress Propagation", "QUALITATIVE", "NON-GEOGRAPHIC", "COMPOUND STRESSORS", "INITIAL SYSTEM EFFECT", "SELECTED PHASE 16A STAGES", "RESPONSE / ADAPTATION", "TERMINATED", "NO DEFENSIBLE", "Fan-out"),
        "phase16b_technology_regime_effects.svg": ("Technology-Regime Effects on Propagation", "A — Coordinated Technological Adaptation", "B — Uneven Networked Modernization", "C — High Capability / High Friction Basin", "modifier only; no new path", "No regime creates a propagation pathway", "NON-PROPORTIONAL", "non-ranked"),
    }
    for filename, terms in figure_terms.items():
        path = FIGURES / filename
        try:
            ET.parse(path)
            figure_text = path.read_text(encoding="utf-8")
            check("figure_svg_" + filename, all(term.lower() in figure_text.lower() for term in terms), {"bytes": path.stat().st_size, "required": terms})
        except Exception as exc:
            check("figure_svg_" + filename, False, str(exc))
    for filename in ("phase16b_compound_stress_propagation.png", "phase16b_technology_regime_effects.png"):
        path = FIGURES / filename
        try:
            with Image.open(path) as image:
                image.verify()
                dimensions = (image.width, image.height)
            check("figure_png_" + filename, dimensions[0] >= 1200 and dimensions[1] >= 600 and path.stat().st_size > 10000, {"bytes": path.stat().st_size, "dimensions": dimensions})
        except Exception as exc:
            check("figure_png_" + filename, False, str(exc))
    geometry_qa_text = (REPORTS / "phase16b_qa.md").read_text(encoding="utf-8")
    geometry_terms = (
        "Deterministic technology-regime geometry QA",
        "data_top > header_bottom + minimum_gap",
        "all 0 card-rectangle overlaps detected",
        "all four stress-test labels remain inside column 0",
        "B text enters C=False",
        "C text outside its figure/card=False",
    )
    check("figure_geometry_qa_metadata", all(term in geometry_qa_text for term in geometry_terms), [term for term in geometry_terms if term not in geometry_qa_text])

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_artifacts = artifact_entries(manifest)
    check("working_manifest_identity", manifest.get("phase") == "16B" and manifest.get("status") == "implemented_validated_pending_sol_acceptance" and manifest.get("source_commit") == BASE_SHA, {key: manifest.get(key) for key in ("phase", "status", "source_commit")})
    check("working_manifest_counts", manifest.get("principal_test_count") == 4 and manifest.get("reserve_test_count") == 2 and manifest.get("counts", {}).get("chain_stages") == 13 and manifest.get("counts", {}).get("branches") == 14, manifest.get("counts"))
    manifest_errors = []
    for relative, value in manifest_artifacts.items():
        expected = value if isinstance(value, str) else str(value["sha256"])
        path = ROOT / relative
        if not path.is_file() or not portable_hash_matches(path, expected):
            manifest_errors.append(relative)
    check("working_manifest_artifacts", not manifest_errors, manifest_errors)
    check("working_manifest_scope", len(manifest_artifacts) == 22 and all("phase16b" in relative.lower() or relative.startswith("outputs/figures/phase16b") or relative.startswith("src/python/systems/validate_phase16b") or relative.startswith("src/R/systems/validate_phase16b") for relative in manifest_artifacts), sorted(manifest_artifacts))

    status_files = (ROOT / "PROJECT_STATUS.md", ROOT / "docs/canon_status.md", ROOT / "reports/README.md", ROOT / "README.md", ROOT / "docs/agent_workflow.md", ROOT / "CHANGELOG.md", ROOT / "reports/current_phase_handoff.md")
    status_text = "\n".join(path.read_text(encoding="utf-8") for path in status_files).lower()
    status_terms = ("phase 16b", "phase 16a", "accepted / frozen", "phase 15", "phase 14", "phase 17", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag")
    status_variants = (
        "implemented / deterministically validated / awaiting independent review",
        "implemented / deterministically validated / atlas-registry contract corrected / awaiting fresh independent review",
        "implemented / validated / integrated / awaiting sol acceptance",
    )
    missing_status_terms = [term for term in status_terms if term not in status_text]
    if not any(variant in status_text for variant in status_variants):
        missing_status_terms.append("Phase 16B implemented/deterministically validated status")
    check("status_surfaces", not missing_status_terms, missing_status_terms)

    if require_review:
        ok, detail = review_ok()
        check("independent_review_passed", ok, detail)
    else:
        check("independent_review_optional", True, "use --require-review for final gate")

    counts = {
        "principal_tests": len(EXPECTED_TESTS),
        "reserve_tests": len(RESERVE_TESTS),
        "chain_stages": len(stages),
        "branches": len(terminations),
        "system_state_observations": len(state_rows),
        "response_adaptation_states": len(response_rows),
        "regime_effect_rows": len(regime_rows),
        "uncertainty_rows": len(uncertainty_rows),
        "comparison_rows": len(comparison_rows),
        "narrative_hooks": len(hook_rows),
        "scenario_conditioned_stages": sum(row["baseline_or_scenario"] == "scenario-conditioned" for row in stages),
        "terminated_branches": sum(row["termination_status"] == TERMINATION_STATUS for row in terminations),
        "phase16a_protected_artifacts": len(phase16a_paths),
        "phase14a_protected_artifacts": len(phase14a_paths),
        "phase14b_protected_artifacts": len(phase14b_paths),
        "phase15a_protected_artifacts": len(phase15a_paths),
        "phase15b_protected_artifacts": len(phase15b_paths),
        "prior_freeze_entries": prior_total,
        "prior_freeze_unique_paths": len(prior_paths),
    }
    result = {"phase": "16B", "passed": not errors, "checks": checks, "counts": counts, "errors": errors}
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "16B", "passed": result["passed"], "counts": counts, "errors": errors}, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
