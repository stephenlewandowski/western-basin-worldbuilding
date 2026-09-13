#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 16A."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

FINAL_MANIFEST = "reports/phase16a_integrated_basin_dynamics_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase16a_manifest.json"
ARTIFACT_CHECK = "reports/phase16a_artifact_check.json"
R_RESULT = "reports/phase16a_r_validation_result.json"
REVIEW = "reports/phase16a_independent_review.md"
INITIAL_REVIEW = "reports/phase16a_independent_review_initial.md"
SECOND_REVIEW = "reports/phase16a_independent_review_second_failed.md"
THIRD_REVIEW = "reports/phase16a_independent_review_third_failed.md"
PHASE14A_FINAL = "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
PHASE14B_FINAL = "reports/phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
PHASE15A_FINAL = "reports/phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
PHASE15B_FINAL = "reports/phase15b_technology_convergence_futures_freeze_manifest.json"
SOURCE_COMMIT = "9daad68c44af9259f42837b2c90af8c8d98fb0f9"
WORKING_SOURCE_COMMIT = "038669819731b2206f74a078f6b652ebafacb007"
EXPECTED_PRIOR_ENTRIES = 593
EXPECTED_PRIOR_UNIQUE = 584
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".txt", ".yml", ".yaml", ".svg", ".toml"}

WORKING_ARTIFACTS = [
    "metadata/basin_dynamics_vocabulary.yml",
    "docs/phase_briefs/phase16_integrated_basin_dynamics.md",
    "docs/phase_briefs/phase16a_integrated_basin_dynamics_framework_propagation_rules.md",
    "docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md",
    "data/processed/integration/stressor_catalog.csv",
    "data/processed/integration/propagation_relationships.csv",
    "data/processed/integration/propagation_rules.csv",
    "data/processed/integration/adaptation_response_catalog.csv",
    "data/processed/integration/technology_modifier_catalog.csv",
    "data/processed/integration/feedback_coupling_inventory.csv",
    "data/processed/integration/system_stressor_matrix.csv",
    "data/processed/integration/phase16b_candidate_stress_tests.csv",
    "outputs/figures/western_basin_stress_propagation_architecture.png",
    "outputs/figures/western_basin_stress_propagation_architecture.svg",
    "reports/phase16a_integrated_basin_dynamics.md",
    "reports/phase16a_propagation_framework.md",
    "reports/phase16a_candidate_stress_tests.md",
    "reports/phase16a_qa.md",
    INITIAL_REVIEW,
    SECOND_REVIEW,
    "src/python/systems/build_phase16a_dynamics.py",
    "src/python/systems/validate_phase16a_dynamics.py",
    "src/R/systems/validate_phase16a_dynamics.R",
]
FREEZE_VALIDATORS = [
    "src/python/systems/validate_phase16a_freeze.py",
    "src/R/systems/validate_phase16a_freeze.R",
]
EXPECTED_WORKING_ARTIFACTS = sorted(WORKING_ARTIFACTS)
EXPECTED_FINAL_ARTIFACTS = sorted(
    WORKING_ARTIFACTS
    + [
        WORKING_MANIFEST,
        ARTIFACT_CHECK,
        R_RESULT,
        REVIEW,
        THIRD_REVIEW,
        *FREEZE_VALIDATORS,
    ]
)
STATUS_SURFACES = (
    "PROJECT_STATUS.md",
    "docs/canon_status.md",
    "reports/current_phase_handoff.md",
    "README.md",
    "reports/README.md",
    "docs/agent_workflow.md",
    "CHANGELOG.md",
)
EVIDENCE = {
    "OBSERVED_DOCUMENTED",
    "DERIVED_CALCULATED",
    "INFERRED",
    "CONTEXT_REUSED",
    "SCENARIO_ASSUMPTION",
    "SCENARIO_STATE",
    "UNRESOLVED",
    "NONCANONICAL_HOLD",
}
CELLS = {"DIRECT", "INDIRECT", "SCENARIO-CONDITIONED", "NO CURRENT DEFENSIBLE PATH", "NOT ASSESSED"}
REMOVED_RULE_IDS = {
    "RULE-16A-003",
    "RULE-16A-004",
    "RULE-16A-013",
    "RULE-16A-032",
    "RULE-16A-035",
    "RULE-16A-038",
}
COMPATIBLE_OUTPUTS = {
    "OBSERVED_DOCUMENTED": {"OBSERVED_DOCUMENTED", "INFERRED", "CONTEXT_REUSED"},
    "INFERRED": {"INFERRED", "CONTEXT_REUSED"},
    "CONTEXT_REUSED": {"INFERRED", "CONTEXT_REUSED"},
    "SCENARIO_STATE": {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"},
    "SCENARIO_ASSUMPTION": {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"},
}
EXPECTED_COUNTS = {
    "stressors": 24,
    "relationships": 36,
    "rules": 32,
    "responses": 13,
    "technology_modifiers": 11,
    "feedback": 10,
    "matrix_cells": 312,
    "candidates": 6,
    "phase14a_protected_artifacts": 24,
    "phase14b_protected_artifacts": 23,
    "phase15a_protected_artifacts": 30,
    "phase15b_protected_artifacts": 28,
    "prior_freeze_entries": 593,
    "prior_freeze_unique_paths": 584,
}
TABLE_SCHEMAS = {
    "stressor_catalog.csv": {"stressor_id", "stressor_class", "label", "initial_system_id", "initial_effect", "evidence_class", "source_lineage", "baseline_or_scenario", "notes"},
    "propagation_relationships.csv": {"relationship_id", "source_system_id", "target_system_id", "relationship_class", "propagation_mechanism", "evidence_class", "direct_or_inferred", "baseline_or_scenario", "relationship_basis", "source_artifact", "source_relationship_id", "source_id", "source_lineage", "limitation", "spatial_character", "temporal_character", "reversibility", "uncertainty", "suitable_for_stress_test_propagation", "notes"},
    "propagation_rules.csv": {"rule_id", "stage", "stressor_id", "chain_parent_rule_id", "chain_relation_type", "source_system_id", "source_state_or_effect", "initial_or_prior_effect", "relationship_id", "relationship_class", "target_system_id", "propagation_mechanism", "evidence_class", "lineage_evidence_class", "application_fit", "direct_or_inferred", "baseline_or_scenario", "enabling_condition", "limiting_condition", "temporal_character", "spatial_character", "reversibility", "technology_modifier", "governance_modifier", "response_option", "second_order_effect", "uncertainty", "source_lineage", "notes"},
    "adaptation_response_catalog.csv": {"response_id", "response_mechanism", "applies_to", "enabling_condition", "limiting_condition", "evidence_class", "source_lineage", "adaptation_capacity_boundary", "notes"},
    "technology_modifier_catalog.csv": {"technology_modifier_id", "technology_family_or_regime", "phase15_technology_or_regime_id", "modifier_effect", "evidence_class", "optional_condition", "effects_allowed", "source_lineage", "notes"},
    "feedback_coupling_inventory.csv": {"feedback_id", "coupling_pair", "feedback_class", "evidence_basis", "plausible_interaction", "boundary", "numeric_gain_or_stability_claim", "notes"},
    "system_stressor_matrix.csv": {"stressor_id", "system_id", "pathway_cell", "basis", "is_severity_measure", "is_risk_or_vulnerability_score", "notes"},
    "phase16b_candidate_stress_tests.csv": {"candidate_id", "label", "stressor_ids", "system_ids", "selection_basis", "phase16a_rule_inputs", "status", "boundary", "executed"},
}


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(root: Path, relative: str) -> tuple[list[str], list[dict[str, str]]]:
    with (root / relative).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_candidates(path: Path) -> list[tuple[str, int]]:
    raw = path.read_bytes()
    candidates = [(digest(raw), len(raw))]
    if path.suffix.lower() in TEXT_SUFFIXES:
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.extend(((digest(normalized), len(normalized)), (digest(crlf), len(crlf))))
    return list(dict.fromkeys(candidates))


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(entries, dict), "manifest artifact collection is not an object"
    return entries


def verify_hash(root: Path, relative: str, metadata: dict[str, Any] | str) -> str:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing protected artifact: {relative}"
    expected = metadata if isinstance(metadata, str) else str(metadata["sha256"])
    expected_bytes = None if isinstance(metadata, str) else metadata.get("bytes")
    for actual_hash, actual_bytes in portable_candidates(path):
        if actual_hash == expected and (expected_bytes is None or int(expected_bytes) == actual_bytes):
            return "exact" if actual_hash == digest(path.read_bytes()) else "newline-normalized"
    raise AssertionError(f"hash/byte mismatch: {relative}")


def verify_manifest(root: Path, relative: str, expected_count: int, expected_inventory: list[str] | None = None) -> dict[str, int]:
    payload = load_json(root, relative)
    entries = artifact_entries(payload)
    assert len(entries) == expected_count, f"{relative}: artifact count {len(entries)}"
    if expected_inventory is not None:
        assert set(entries) == set(expected_inventory) and len(entries) == len(expected_inventory), f"{relative}: artifact inventory differs"
    exact = 0
    normalized = 0
    for path, metadata in entries.items():
        if verify_hash(root, path, metadata) == "exact":
            exact += 1
        else:
            normalized += 1
    return {"entries": len(entries), "exact": exact, "newline_normalized": normalized}


def endpoint_pair_matches(actual_source: str, actual_target: str, expected_source: str, expected_target: str, explicitly_undirected: bool = False) -> bool:
    ordered = (actual_source, actual_target) == (expected_source, expected_target)
    reversed_allowed = explicitly_undirected and (actual_source, actual_target) == (expected_target, expected_source)
    return ordered or reversed_allowed


def architecture_lookup(root: Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load((root / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    interfaces = payload.get("architecture", {}).get("interfaces", [])
    assert isinstance(interfaces, list) and interfaces, "Phase 14 architecture interfaces"
    lookup: dict[str, dict[str, Any]] = {}
    for interface in interfaces:
        assert isinstance(interface, list) and len(interface) == 4, ("Phase 14 architecture interface schema", interface)
        source, target, interface_type, status = (str(value) for value in interface)
        lineage = f"metadata/atlas_systems.yml#architecture.interfaces:{source}>{target}"
        assert lineage not in lookup, ("duplicate Phase 14 architecture lineage", lineage)
        lookup[lineage] = {
            "source": source,
            "target": target,
            "explicitly_undirected": any(str(value).strip().lower() in {"undirected", "bidirectional"} for value in (interface_type, status)),
        }
    return lookup


def direct_lineage_evidence(lineage: str, direct: dict[str, dict[str, str]], interfaces: dict[str, dict[str, str]], dependencies: dict[str, dict[str, str]], states: dict[str, dict[str, str]], dep_states: dict[str, dict[str, str]], governance: dict[str, dict[str, str]]) -> str | None:
    if "#AR-" in lineage:
        row = direct.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TSI-" in lineage:
        row = interfaces.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TDEP-" in lineage:
        row = dependencies.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TSS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in states else None
    if "#TDS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in dep_states else None
    if "#TGS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in governance else None
    return None


def verify_relationships(root: Path, rows: list[dict[str, str]], system_ids: set[str], relationship_classes: set[str]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    assert len(rows) == 36 and len({row["relationship_id"] for row in rows}) == 36
    assert all(row["source_system_id"] in system_ids and row["target_system_id"] in system_ids for row in rows)
    assert {row["relationship_class"] for row in rows} <= relationship_classes
    assert {row["evidence_class"] for row in rows} <= EVIDENCE
    assert all(row["source_lineage"] and row["source_artifact"] for row in rows)
    expected_status = {"OBSERVED_DOCUMENTED": "direct", "INFERRED": "inferred", "CONTEXT_REUSED": "inferred", "SCENARIO_STATE": "scenario-conditioned"}
    assert all(expected_status.get(row["evidence_class"], row["direct_or_inferred"]) == row["direct_or_inferred"] for row in rows)
    assert all(row["relationship_class"] != "co-location" and row["relationship_basis"] != "co-location" for row in rows)
    assert all(row["suitable_for_stress_test_propagation"] == "QUALITATIVE_ONLY" for row in rows)

    direct = {row["atlas_relationship_id"]: row for _, row in [read_csv(root, "data/processed/integration/atlas_dependency_crosswalk.csv")] for row in row}
    interfaces = {row["interface_id"]: row for _, row in [read_csv(root, "data/processed/integration/technology_system_interfaces.csv")] for row in row}
    dependencies = {row["dependency_id"]: row for _, row in [read_csv(root, "data/processed/integration/technology_dependencies.csv")] for row in row}
    states = {row["state_id"]: row for _, row in [read_csv(root, "data/processed/scenarios/technology_system_states.csv")] for row in row}
    dep_states = {row["dependency_state_id"]: row for _, row in [read_csv(root, "data/processed/scenarios/technology_dependency_states.csv")] for row in row}
    governance = {row["governance_state_id"]: row for _, row in [read_csv(root, "data/processed/scenarios/technology_governance_states.csv")] for row in row}
    architecture = architecture_lookup(root)

    for row in rows:
        lineage = row["source_lineage"]
        if "#AR-" in lineage:
            source = direct.get(lineage.split("#", 1)[1])
            assert source and source["source_system_id"] == row["source_system_id"] and source["target_system_id"] == row["target_system_id"] and source["normalized_relationship_class"] == row["relationship_class"], row["relationship_id"]
        elif "#TDS-" in lineage:
            source = dep_states.get(lineage.split("#", 1)[1])
            assert source and row["baseline_or_scenario"] == "scenario-conditioned" and row["evidence_class"] == "SCENARIO_STATE", row["relationship_id"]
            undirected = source.get("directionality", "").strip().lower() in {"undirected", "bidirectional"}
            assert endpoint_pair_matches(row["source_system_id"], row["target_system_id"], source["system_a"], source["system_b"], undirected), row["relationship_id"]
        elif lineage.startswith("metadata/atlas_systems.yml#architecture.interfaces:"):
            source = architecture.get(lineage)
            assert source and endpoint_pair_matches(row["source_system_id"], row["target_system_id"], source["source"], source["target"], source["explicitly_undirected"]), row["relationship_id"]
        else:
            raise AssertionError(f"unresolved relationship lineage: {row['relationship_id']}")
    return direct, interfaces, dependencies, states, dep_states, governance


def verify_rules(rows: list[dict[str, str]], stressors: list[dict[str, str]], relationships: list[dict[str, str]], responses: list[dict[str, str]]) -> None:
    assert len(rows) == 32 and len({row["rule_id"] for row in rows}) == 32
    assert not ({row["rule_id"] for row in rows} & REMOVED_RULE_IDS)
    stressor_by_id = {row["stressor_id"]: row for row in stressors}
    relationship_by_id = {row["relationship_id"]: row for row in relationships}
    rule_by_id = {row["rule_id"]: row for row in rows}
    response_ids = {row["response_id"] for row in responses}
    assert all(row["stressor_id"] in stressor_by_id and row["relationship_id"] in relationship_by_id and row["response_option"] in response_ids for row in rows)
    assert all(row["source_system_id"] and row["target_system_id"] and row["stage"] in {"1", "2"} for row in rows)
    assert all(row["source_lineage"] and row["enabling_condition"] and row["limiting_condition"] and row["uncertainty"] for row in rows)
    assert all(row["baseline_or_scenario"] in {"baseline", "scenario-conditioned"} for row in rows)
    rule_order = {row["rule_id"]: index for index, row in enumerate(rows)}
    expected_status = {"OBSERVED_DOCUMENTED": "direct", "INFERRED": "inferred", "CONTEXT_REUSED": "inferred", "SCENARIO_STATE": "scenario-conditioned"}

    for index, row in enumerate(rows):
        relationship = relationship_by_id[row["relationship_id"]]
        stressor = stressor_by_id[row["stressor_id"]]
        for field in ("source_system_id", "target_system_id", "relationship_class", "propagation_mechanism", "source_lineage"):
            assert row[field] == relationship[field], (row["rule_id"], field)
        assert row["lineage_evidence_class"] == relationship["evidence_class"]
        assert row["evidence_class"] in COMPATIBLE_OUTPUTS.get(relationship["evidence_class"], set()), row["rule_id"]
        if row["evidence_class"] in expected_status:
            assert row["direct_or_inferred"] == expected_status[row["evidence_class"]], row["rule_id"]
        if row["evidence_class"] == "OBSERVED_DOCUMENTED":
            assert relationship["evidence_class"] == "OBSERVED_DOCUMENTED" and row["application_fit"] == "EXACT_SOURCE_APPLICATION", row["rule_id"]
        if row["evidence_class"] == "INFERRED" and relationship["evidence_class"] == "OBSERVED_DOCUMENTED":
            assert row["application_fit"].startswith("QUALIFIED_INFERENCE") and "inferred" in (row["enabling_condition"] + " " + row["limiting_condition"]).lower(), row["rule_id"]
        if row["baseline_or_scenario"] == "scenario-conditioned":
            assert relationship["evidence_class"] == "SCENARIO_STATE" and row["evidence_class"] in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}, row["rule_id"]
        else:
            assert relationship["evidence_class"] != "SCENARIO_STATE" and row["evidence_class"] not in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}, row["rule_id"]
        stage = int(row["stage"])
        if stage == 1:
            assert row["source_system_id"] == stressor["initial_system_id"] and not row["chain_parent_rule_id"] and row["chain_relation_type"] == "parallel_initial_branch", row["rule_id"]
        else:
            parent = rule_by_id.get(row["chain_parent_rule_id"])
            assert parent and rule_order[row["chain_parent_rule_id"]] < index and parent["stressor_id"] == row["stressor_id"] and int(parent["stage"]) == stage - 1 and parent["target_system_id"] == row["source_system_id"] and row["chain_relation_type"] == "sequential", row["rule_id"]


def verify_responses(rows: list[dict[str, str]], direct: dict[str, dict[str, str]], interfaces: dict[str, dict[str, str]], dependencies: dict[str, dict[str, str]], states: dict[str, dict[str, str]], dep_states: dict[str, dict[str, str]], governance: dict[str, dict[str, str]]) -> None:
    assert len(rows) == 13 and len({row["response_id"] for row in rows}) == 13
    assert {row["evidence_class"] for row in rows} <= EVIDENCE
    assert all(any(term in row["adaptation_capacity_boundary"].lower() for term in ("not", "option", "without guaranteeing", "indeterminate")) for row in rows)
    for row in rows:
        source_evidence = direct_lineage_evidence(row["source_lineage"], direct, interfaces, dependencies, states, dep_states, governance)
        assert source_evidence is not None and row["evidence_class"] in COMPATIBLE_OUTPUTS.get(source_evidence, set()), row["response_id"]
        assert not (row["evidence_class"] == "OBSERVED_DOCUMENTED" and source_evidence != "OBSERVED_DOCUMENTED"), row["response_id"]


def technology_lineage_errors(row: dict[str, str], nodes: dict[str, dict[str, str]], interfaces: dict[str, dict[str, str]], dependencies: dict[str, dict[str, str]], states: dict[str, dict[str, str]], dep_states: dict[str, dict[str, str]], governance: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    modifier = row["technology_modifier_id"]
    family = row["technology_family_or_regime"]
    technology_id = row["phase15_technology_or_regime_id"]
    lineage = row["source_lineage"]
    if technology_id.startswith("REGIME-"):
        if family != technology_id:
            errors.append(f"{modifier}: regime family/id mismatch")
        expected = f"-{technology_id[-1]}"
        if not any(expected in ref for ref in re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage)):
            errors.append(f"{modifier}: regime lineage does not match scenario")
        return errors
    node = nodes.get(technology_id)
    if not node:
        return [f"{modifier}: missing Phase 15A technology node"]
    if family != node["technology_family"]:
        errors.append(f"{modifier}: declared family differs from Phase 15A node family")
    matched_phase15a = False
    for ref in re.findall(r"(?:TSI|TDEP|TECH)-[A-Z0-9-]+", lineage):
        if ref.startswith("TSI-"):
            source = interfaces.get(ref)
            if not source or source["technology_id"] != technology_id:
                errors.append(f"{modifier}: Phase 15A interface lineage mismatch")
            else:
                matched_phase15a = True
        elif ref.startswith("TDEP-"):
            source = dependencies.get(ref)
            if not source or source["technology_id"] != technology_id:
                errors.append(f"{modifier}: Phase 15A dependency lineage mismatch")
            else:
                matched_phase15a = True
        elif ref.startswith("TECH-"):
            if ref != technology_id:
                errors.append(f"{modifier}: Phase 15A technology ID lineage mismatch")
            else:
                matched_phase15a = True
    if not matched_phase15a:
        errors.append(f"{modifier}: no matching Phase 15A identity lineage")
    phase15b = {**states, **dep_states, **governance}
    refs = re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage)
    if not refs:
        errors.append(f"{modifier}: no Phase 15B lineage")
    for ref in refs:
        source = phase15b.get(ref)
        if not source:
            errors.append(f"{modifier}: missing Phase 15B lineage {ref}")
        elif family not in set(source.get("technology_family", "").split(";")):
            errors.append(f"{modifier}: Phase 15B family mismatch {ref}")
    return errors


def png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", path
    return int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")


def verify_package(root: Path) -> dict[str, Any]:
    ontology = yaml.safe_load((root / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology["systems"]}
    assert len(system_ids) == 13
    vocabulary = yaml.safe_load((root / "metadata/basin_dynamics_vocabulary.yml").read_text(encoding="utf-8"))
    relationship_vocabulary = yaml.safe_load((root / "metadata/atlas_relationship_vocabulary.yml").read_text(encoding="utf-8"))
    relationship_classes = {row["class_id"] for row in relationship_vocabulary["normalized_relationship_classes"]}
    assert set(vocabulary["evidence_classes"]) == EVIDENCE

    frames: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    for filename, schema in TABLE_SCHEMAS.items():
        fields, rows = read_csv(root, f"data/processed/integration/{filename}")
        assert set(fields) == schema, filename
        assert rows, filename
        frames[filename] = (fields, rows)

    stressors = frames["stressor_catalog.csv"][1]
    relationships = frames["propagation_relationships.csv"][1]
    rules = frames["propagation_rules.csv"][1]
    responses = frames["adaptation_response_catalog.csv"][1]
    technology = frames["technology_modifier_catalog.csv"][1]
    feedback = frames["feedback_coupling_inventory.csv"][1]
    matrix = frames["system_stressor_matrix.csv"][1]
    candidates = frames["phase16b_candidate_stress_tests.csv"][1]

    assert len(stressors) == 24 and len({row["stressor_id"] for row in stressors}) == 24
    assert all(row["initial_system_id"] in system_ids and row["stressor_class"] in {item["class_id"] for item in vocabulary["stressor_classes"]} and row["evidence_class"] in EVIDENCE and row["source_lineage"] for row in stressors)
    direct, interfaces, dependencies, states, dep_states, governance = verify_relationships(root, relationships, system_ids, relationship_classes)
    verify_rules(rules, stressors, relationships, responses)
    verify_responses(responses, direct, interfaces, dependencies, states, dep_states, governance)

    phase15a_nodes = {row["technology_id"]: row for _, row in [read_csv(root, "data/processed/analysis/technology_system_nodes.csv")] for row in row}
    modifier_errors = [error for row in technology for error in technology_lineage_errors(row, phase15a_nodes, interfaces, dependencies, states, dep_states, governance)]
    assert len(technology) == 11 and len({row["technology_modifier_id"] for row in technology}) == 11
    assert not modifier_errors, modifier_errors
    assert {row["evidence_class"] for row in technology} <= EVIDENCE
    assert all("not automatically protective" in row["notes"].lower() for row in technology)

    assert len(feedback) == 10 and len({row["feedback_id"] for row in feedback}) == 10
    assert {row["feedback_class"] for row in feedback} <= {"documented", "inferred", "scenario-conditioned", "not currently supported"}
    assert all(row["numeric_gain_or_stability_claim"] == "false" and ("not" in row["boundary"].lower() or "no " in row["boundary"].lower()) for row in feedback)

    assert len(matrix) == 312 and len({(row["stressor_id"], row["system_id"]) for row in matrix}) == 312
    stressor_ids = {row["stressor_id"] for row in stressors}
    assert all(row["stressor_id"] in stressor_ids and row["system_id"] in system_ids and row["pathway_cell"] in CELLS for row in matrix)
    assert all(row["is_severity_measure"] == "false" and row["is_risk_or_vulnerability_score"] == "false" and "ranked systems" not in row["notes"].lower() and "summed rows" not in row["notes"].lower() for row in matrix)
    matrix_by_key = {(row["stressor_id"], row["system_id"]): row for row in matrix}
    scenario_targets = {(row["stressor_id"], row["target_system_id"]) for row in rules if row["baseline_or_scenario"] == "scenario-conditioned"}
    for stressor in stressors:
        for system_id in system_ids:
            row = matrix_by_key[(stressor["stressor_id"], system_id)]
            if stressor["baseline_or_scenario"] != "BASELINE":
                assert row["pathway_cell"] != "DIRECT"
                if system_id == stressor["initial_system_id"]:
                    assert row["pathway_cell"] == "SCENARIO-CONDITIONED"
            if row["pathway_cell"] == "SCENARIO-CONDITIONED" and system_id != stressor["initial_system_id"]:
                assert (stressor["stressor_id"], system_id) in scenario_targets
            if stressor["baseline_or_scenario"] == "BASELINE" and system_id == stressor["initial_system_id"]:
                assert row["pathway_cell"] == "DIRECT"

    assert len(candidates) == 6 and len({row["candidate_id"] for row in candidates}) == 6
    assert all(row["status"] == "APPROVED SCOPE / NOT IMPLEMENTED" and row["executed"] == "false" and all(item in stressor_ids for item in row["stressor_ids"].split(";")) and all(item in system_ids for item in row["system_ids"].split(";")) for row in candidates)

    all_text = " ".join(" ".join(row.values()) for _, rows in frames.values() for row in rows).lower()
    forbidden_fields = {"risk_score", "resilience_score", "vulnerability_score", "connectivity_score", "severity_score", "probability_estimate", "incidence_rate", "outbreak_probability", "health_outcome_forecast"}
    fields = set().union(*(set(fields) for fields, _ in frames.values()))
    assert not fields.intersection(forbidden_fields)
    assert not re.search(r"(?:score|probability|risk|vulnerability|resilience)\s*[:=]\s*[-+]?\d", all_text)
    assert not re.search(r"(?:cases?|incidence|deaths?|hospitalizations?|illness)\s*[:=]\s*\d", all_text)
    assert all(term in all_text for term in ("no pathogen engineering", "high-level only", "no operational attack"))

    svg = root / "outputs/figures/western_basin_stress_propagation_architecture.svg"
    ET.parse(svg)
    svg_text = svg.read_text(encoding="utf-8").lower()
    assert all(term.lower() in svg_text for term in ("Western Basin Stress Propagation Architecture", "STRESSOR", "SYSTEM EFFECT", "DEPENDENCY / INTERFACE", "PROPAGATION", "RESPONSE / ADAPTATION", "SECOND-ORDER EFFECT", "direct / documented", "inferred", "scenario-conditioned", "option ≠ capacity ≠ success"))
    png = root / "outputs/figures/western_basin_stress_propagation_architecture.png"
    dimensions = png_dimensions(png)
    assert dimensions == (2259, 1214) and png.stat().st_size > 10000

    builder_text = (root / "src/python/systems/build_phase16a_dynamics.py").read_text(encoding="utf-8")
    python_text = (root / "src/python/systems/validate_phase16a_dynamics.py").read_text(encoding="utf-8")
    r_text = (root / "src/R/systems/validate_phase16a_dynamics.R").read_text(encoding="utf-8")
    assert "def assert_lineage_endpoint_compatibility" in builder_text and "def endpoint_pair_matches" in builder_text
    assert "def endpoint_pair_matches" in python_text and "def endpoint_compatibility_error" in python_text
    assert "endpoint_compatible <- function" in r_text and "endpoint_compatibility_error <- function" in r_text

    return {
        "stressors": len(stressors),
        "relationships": len(relationships),
        "rules": len(rules),
        "responses": len(responses),
        "technology_modifiers": len(technology),
        "feedback": len(feedback),
        "matrix_cells": len(matrix),
        "candidates": len(candidates),
        "figure_dimensions": list(dimensions),
        "propagation_chain_invariants": "passed",
        "evidence_inheritance": "passed",
        "technology_lineage": "passed",
        "endpoint_lineage": "passed",
    }


def verify_review_lineage(root: Path) -> dict[str, Any]:
    def verdict(relative: str) -> tuple[str, dict[str, Any]]:
        text = (root / relative).read_text(encoding="utf-8")
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
        assert match, f"review JSON block missing: {relative}"
        return text, json.loads(match.group(1))

    final_text, final = verdict(REVIEW)
    assert "deleg_9fa57f45" in final_text and final.get("passed") is True
    required_arrays = ("security_concerns", "logic_errors", "provenance_errors", "propagation_errors", "causal_boundary_errors", "feedback_errors", "evidence_classification_errors", "technology_modifier_errors", "biosecurity_boundary_errors", "canon_boundary_errors")
    assert all(final.get(key) == [] for key in required_arrays)
    preserved = {}
    for relative, review_id in ((INITIAL_REVIEW, "deleg_ec4d7c55"), (SECOND_REVIEW, None), (THIRD_REVIEW, "deleg_703e15ec")):
        text, data = verdict(relative)
        assert data.get("passed") is False, relative
        if review_id is not None:
            assert review_id in text, relative
        preserved[relative] = {"passed": False, "review_id": review_id or "endpoint-compatibility failed review"}
    return {"final_review_id": "deleg_9fa57f45", "final_passed": True, "blocking_arrays_empty": True, "preserved": preserved}


def prior_freeze_integrity(root: Path) -> dict[str, Any]:
    entries = 0
    protected: set[str] = set()
    manifests = []
    final_name = Path(FINAL_MANIFEST).name
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        manifests.append(path.name)
        for relative, metadata in artifact_entries(load_json(root, f"reports/{path.name}")).items():
            entries += 1
            normalized = relative.replace("\\", "/")
            protected.add(normalized)
            verify_hash(root, normalized, metadata)
    assert entries == EXPECTED_PRIOR_ENTRIES and len(protected) == EXPECTED_PRIOR_UNIQUE, (entries, len(protected))
    return {"manifest_count": len(manifests), "entries": entries, "unique_paths": len(protected), "protected_paths": sorted(protected)}


def changed_paths(root: Path) -> set[str]:
    tracked = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True)
    untracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"], text=True)
    return {line.replace("\\", "/") for line in (tracked + untracked).splitlines() if line}


def verify_status_surfaces(root: Path) -> None:
    required = ("phase 16a", "accepted / frozen", Path(FINAL_MANIFEST).name, "phase 16b", "approved scope / not implemented", "phase 17", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag")
    for relative in STATUS_SURFACES:
        text = (root / relative).read_text(encoding="utf-8").lower()
        assert all(term in text for term in required), relative
        assert "phase 14" in text and "complete" in text and "phase 15" in text and "frozen" in text, relative


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "16A"
    assert final["baseline"] == "Integrated Basin Dynamics Framework & Propagation Rules"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-13"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == EXPECTED_COUNTS
    assert final["qualitative_only"] is True and final["no_composite_scores"] is True and final["no_phase16b_execution"] is True
    assert final["phase16b_status"] == "APPROVED SCOPE / NOT IMPLEMENTED" and final["phase17_status"] == "NOT IMPLEMENTED"
    assert final["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert final["deferred_maintenance_preserved"] == ["Phase 6B manifest status wording mismatch", "Phase 3A missing manifest status", "Phase 2A superseded legacy worktree"]
    assert final["release_created"] is False and final["tag_created"] is False
    assert final["final_manifest_path"] == FINAL_MANIFEST
    assert FINAL_MANIFEST not in artifact_entries(final)
    final_result = verify_manifest(root, FINAL_MANIFEST, len(EXPECTED_FINAL_ARTIFACTS), EXPECTED_FINAL_ARTIFACTS)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "16A" and working["status"] == "implemented_validated_pending_sol_acceptance" and working["source_commit"] == WORKING_SOURCE_COMMIT
    assert working["counts"] == {"stressors": 24, "relationships": 36, "rules": 32, "responses": 13, "technology_modifiers": 11, "feedback": 10, "matrix": 312, "candidates": 6}
    working_result = verify_manifest(root, WORKING_MANIFEST, len(EXPECTED_WORKING_ARTIFACTS), EXPECTED_WORKING_ARTIFACTS)

    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["phase"] == "16A" and artifact_check["passed"] is True and artifact_check["errors"] == []
    assert artifact_check["counts"]["prior_freeze_entries"] == EXPECTED_PRIOR_ENTRIES and artifact_check["counts"]["prior_freeze_unique_paths"] == EXPECTED_PRIOR_UNIQUE
    for key in ("rule_source_target_and_evidence_fit", "rule_chain_continuity", "response_evidence_inheritance", "technology_modifier_lineage_identity", "matrix_scenario_precedence"):
        assert artifact_check["checks"][key]["passed"] is True, key
    r_result = load_json(root, R_RESULT)
    assert r_result["phase"] == "16A" and r_result["passed"] is True

    phase14a = load_json(root, PHASE14A_FINAL)
    phase14b = load_json(root, PHASE14B_FINAL)
    phase15a = load_json(root, PHASE15A_FINAL)
    phase15b = load_json(root, PHASE15B_FINAL)
    assert phase14a["accepted_phase"] == "14A" and phase14a["status"] == "ACCEPTED / FROZEN"
    assert phase14b["accepted_phase"] == "14B" and phase14b["status"] == "ACCEPTED / FROZEN" and phase14b["phase14_overall_status"] == "COMPLETE / ACCEPTED / FROZEN"
    assert phase15a["accepted_phase"] == "15A" and phase15a["status"] == "ACCEPTED / FROZEN"
    assert phase15b["accepted_phase"] == "15B" and phase15b["status"] == "ACCEPTED / FROZEN" and phase15b["phase15_overall_status"] == "COMPLETE / ACCEPTED / FROZEN"
    phase14a_result = verify_manifest(root, PHASE14A_FINAL, 24)
    phase14b_result = verify_manifest(root, PHASE14B_FINAL, 23)
    phase15a_result = verify_manifest(root, PHASE15A_FINAL, 30)
    phase15b_result = verify_manifest(root, PHASE15B_FINAL, 28)

    package = verify_package(root)
    prior = prior_freeze_integrity(root)
    changed = changed_paths(root)
    prior_paths = set(prior["protected_paths"])
    assert not changed.intersection(prior_paths), sorted(changed.intersection(prior_paths))
    package_paths = set(EXPECTED_WORKING_ARTIFACTS + [WORKING_MANIFEST, ARTIFACT_CHECK, R_RESULT, REVIEW, INITIAL_REVIEW, SECOND_REVIEW, THIRD_REVIEW])
    package_changes = changed.intersection(package_paths)
    assert not package_changes, sorted(package_changes)
    allowed = set(STATUS_SURFACES) | {FINAL_MANIFEST} | set(FREEZE_VALIDATORS)
    assert changed <= allowed, sorted(changed - allowed)
    assert not any("phase16b" in path.lower() or "phase17" in path.lower() for path in changed)

    review = verify_review_lineage(root)
    verify_status_surfaces(root)
    print(json.dumps({
        "status": "passed",
        "phase": "16A",
        "final_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": {"path": WORKING_MANIFEST, **working_result},
        "package": package,
        "phase14_integrity": {"phase14a": phase14a_result, "phase14b": phase14b_result},
        "phase15_integrity": {"phase15a": phase15a_result, "phase15b": phase15b_result},
        "prior_freeze_integrity": {key: value for key, value in prior.items() if key != "protected_paths"},
        "review_lineage": review,
        "changed_paths_from_source_commit": sorted(changed),
        "release_created": False,
        "tag_created": False,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
