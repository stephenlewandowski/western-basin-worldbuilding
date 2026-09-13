"""Independent deterministic validator for the Phase 16A package."""
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
REPORTS = ROOT / "reports"
FIGURES = ROOT / "outputs/figures"
METADATA = ROOT / "metadata"
SCENARIOS = ROOT / "data/processed/scenarios"
SYSTEMS = METADATA / "atlas_systems.yml"
BASE_SHA = "038669819731b2206f74a078f6b652ebafacb007"
ARCHITECTURE_LINEAGE_PREFIX = "metadata/atlas_systems.yml#architecture.interfaces:"

PHASE14A = REPORTS / "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
PHASE14B = REPORTS / "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
PHASE15A = REPORTS / "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
PHASE15B = REPORTS / "phase15b_technology_convergence_futures_freeze_manifest.json"
PHASE15A_NODES = ROOT / "data/processed/analysis/technology_system_nodes.csv"
MANIFEST = REPORTS / "phase16a_manifest.json"
CHECK = REPORTS / "phase16a_artifact_check.json"
REVIEW = REPORTS / "phase16a_independent_review.md"

FILES = {
    "stressor_catalog.csv": (INTEGRATION / "stressor_catalog.csv", {"stressor_id", "stressor_class", "label", "initial_system_id", "initial_effect", "evidence_class", "source_lineage", "baseline_or_scenario", "notes"}),
    "propagation_relationships.csv": (INTEGRATION / "propagation_relationships.csv", {"relationship_id", "source_system_id", "target_system_id", "relationship_class", "propagation_mechanism", "evidence_class", "direct_or_inferred", "baseline_or_scenario", "relationship_basis", "source_artifact", "source_relationship_id", "source_id", "source_lineage", "limitation", "spatial_character", "temporal_character", "reversibility", "uncertainty", "suitable_for_stress_test_propagation", "notes"}),
    "propagation_rules.csv": (INTEGRATION / "propagation_rules.csv", {"rule_id", "stage", "stressor_id", "chain_parent_rule_id", "chain_relation_type", "source_system_id", "source_state_or_effect", "initial_or_prior_effect", "relationship_id", "relationship_class", "target_system_id", "propagation_mechanism", "evidence_class", "lineage_evidence_class", "application_fit", "direct_or_inferred", "baseline_or_scenario", "enabling_condition", "limiting_condition", "temporal_character", "spatial_character", "reversibility", "technology_modifier", "governance_modifier", "response_option", "second_order_effect", "uncertainty", "source_lineage", "notes"}),
    "adaptation_response_catalog.csv": (INTEGRATION / "adaptation_response_catalog.csv", {"response_id", "response_mechanism", "applies_to", "enabling_condition", "limiting_condition", "evidence_class", "source_lineage", "adaptation_capacity_boundary", "notes"}),
    "technology_modifier_catalog.csv": (INTEGRATION / "technology_modifier_catalog.csv", {"technology_modifier_id", "technology_family_or_regime", "phase15_technology_or_regime_id", "modifier_effect", "evidence_class", "optional_condition", "effects_allowed", "source_lineage", "notes"}),
    "feedback_coupling_inventory.csv": (INTEGRATION / "feedback_coupling_inventory.csv", {"feedback_id", "coupling_pair", "feedback_class", "evidence_basis", "plausible_interaction", "boundary", "numeric_gain_or_stability_claim", "notes"}),
    "system_stressor_matrix.csv": (INTEGRATION / "system_stressor_matrix.csv", {"stressor_id", "system_id", "pathway_cell", "basis", "is_severity_measure", "is_risk_or_vulnerability_score", "notes"}),
    "phase16b_candidate_stress_tests.csv": (INTEGRATION / "phase16b_candidate_stress_tests.csv", {"candidate_id", "label", "stressor_ids", "system_ids", "selection_basis", "phase16a_rule_inputs", "status", "boundary", "executed"}),
}
EVIDENCE = {"OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD"}
CELLS = {"DIRECT", "INDIRECT", "SCENARIO-CONDITIONED", "NO CURRENT DEFENSIBLE PATH", "NOT ASSESSED"}
REMOVED_RULE_IDS = {"RULE-16A-003", "RULE-16A-004", "RULE-16A-013", "RULE-16A-032", "RULE-16A-035", "RULE-16A-038"}
COMPATIBLE_OUTPUTS = {
    "OBSERVED_DOCUMENTED": {"OBSERVED_DOCUMENTED", "INFERRED", "CONTEXT_REUSED"},
    "INFERRED": {"INFERRED", "CONTEXT_REUSED"},
    "CONTEXT_REUSED": {"INFERRED", "CONTEXT_REUSED"},
    "SCENARIO_STATE": {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"},
    "SCENARIO_ASSUMPTION": {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    assert path.is_file() and path.stat().st_size > 0, path
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def endpoint_pair_matches(
    actual_source: str,
    actual_target: str,
    expected_source: str,
    expected_target: str,
    *,
    explicitly_undirected: bool = False,
) -> bool:
    ordered = (actual_source, actual_target) == (expected_source, expected_target)
    reversed_allowed = explicitly_undirected and (actual_source, actual_target) == (expected_target, expected_source)
    return ordered or reversed_allowed


def endpoint_compatibility_error(
    relationship_id: str,
    actual_source: str,
    actual_target: str,
    expected_source: str,
    expected_target: str,
    *,
    lineage_kind: str,
    source_endpoint_field: str,
    target_endpoint_field: str,
    explicitly_undirected: bool = False,
) -> str | None:
    if endpoint_pair_matches(
        actual_source,
        actual_target,
        expected_source,
        expected_target,
        explicitly_undirected=explicitly_undirected,
    ):
        return None
    allowance = "; reversed orientation is allowed only by an explicit undirected source declaration" if not explicitly_undirected else "; the explicit undirected declaration did not match either orientation"
    return (
        f"{relationship_id}: {lineage_kind} endpoint mismatch: "
        f"Phase 16A source_system_id={actual_source!r}, target_system_id={actual_target!r}; "
        f"frozen {source_endpoint_field}={expected_source!r}, {target_endpoint_field}={expected_target!r}{allowance}"
    )


def architecture_interface_lookup(ontology: dict[str, Any]) -> dict[str, dict[str, object]]:
    interfaces = ontology.get("architecture", {}).get("interfaces", [])
    assert isinstance(interfaces, list) and interfaces, "Phase 14 architecture interfaces"
    lookup: dict[str, dict[str, object]] = {}
    for interface in interfaces:
        assert isinstance(interface, list) and len(interface) == 4, ("Phase 14 architecture interface schema", interface)
        source, target, interface_type, status = (str(value) for value in interface)
        lineage = f"{ARCHITECTURE_LINEAGE_PREFIX}{source}>{target}"
        assert lineage not in lookup, ("duplicate Phase 14 architecture lineage", lineage)
        lookup[lineage] = {
            "source_system_id": source,
            "target_system_id": target,
            "interface_type": interface_type,
            "status": status,
            "explicitly_undirected": any(str(value).strip().lower() in {"undirected", "bidirectional"} for value in (interface_type, status)),
        }
    return lookup


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def hash_matches(path: Path, expected: str) -> bool:
    return digest(path) == expected or hashlib.sha256(normalized(path.read_bytes())).hexdigest() == expected


def lineage_evidence_class(
    lineage: str,
    direct_crosswalk: dict[str, dict[str, str]],
    phase15a_interfaces: dict[str, dict[str, str]],
    phase15a_dependencies: dict[str, dict[str, str]],
    phase15b_states: dict[str, dict[str, str]],
    phase15b_dependencies: dict[str, dict[str, str]],
    phase15b_governance: dict[str, dict[str, str]],
) -> str | None:
    if "#AR-" in lineage:
        row = direct_crosswalk.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TSI-" in lineage:
        row = phase15a_interfaces.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TDEP-" in lineage:
        row = phase15a_dependencies.get(lineage.split("#", 1)[1])
        return row["evidence_class"] if row else None
    if "#TDS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in phase15b_dependencies else None
    if "#TSS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in phase15b_states else None
    if "#TGS-" in lineage:
        return "SCENARIO_STATE" if lineage.split("#", 1)[1] in phase15b_governance else None
    return None


def technology_lineage_errors(
    row: dict[str, str],
    phase15a_nodes: dict[str, dict[str, str]],
    phase15a_interfaces: dict[str, dict[str, str]],
    phase15a_dependencies: dict[str, dict[str, str]],
    phase15b_states: dict[str, dict[str, str]],
    phase15b_dependencies: dict[str, dict[str, str]],
    phase15b_governance: dict[str, dict[str, str]],
) -> list[str]:
    errors: list[str] = []
    family = row["technology_family_or_regime"]
    technology_id = row["phase15_technology_or_regime_id"]
    lineage = row["source_lineage"]
    if technology_id.startswith("REGIME-"):
        if family != technology_id:
            errors.append(row["technology_modifier_id"] + ": regime family/id mismatch")
        expected = f"-{technology_id[-1]}"
        if not any(expected in ref for ref in re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage)):
            errors.append(row["technology_modifier_id"] + ": regime lineage does not match scenario")
        return errors
    node = phase15a_nodes.get(technology_id)
    if not node:
        errors.append(row["technology_modifier_id"] + ": missing Phase 15A technology node")
        return errors
    if family != node["technology_family"]:
        errors.append(row["technology_modifier_id"] + ": declared family differs from Phase 15A node family")
    phase15a_refs = re.findall(r"(?:TSI|TDEP|TECH)-[A-Z0-9-]+", lineage)
    matched_phase15a = False
    for ref in phase15a_refs:
        if ref.startswith("TSI-"):
            source = phase15a_interfaces.get(ref)
            if not source or source["technology_id"] != technology_id:
                errors.append(row["technology_modifier_id"] + ": Phase 15A interface lineage mismatch")
            else:
                matched_phase15a = True
        elif ref.startswith("TDEP-"):
            source = phase15a_dependencies.get(ref)
            if not source or source["technology_id"] != technology_id:
                errors.append(row["technology_modifier_id"] + ": Phase 15A dependency lineage mismatch")
            else:
                matched_phase15a = True
        elif ref.startswith("TECH-"):
            if ref != technology_id:
                errors.append(row["technology_modifier_id"] + ": Phase 15A technology ID lineage mismatch")
            else:
                matched_phase15a = True
    if not matched_phase15a:
        errors.append(row["technology_modifier_id"] + ": no matching Phase 15A identity lineage")
    phase15b = {**phase15b_states, **phase15b_dependencies, **phase15b_governance}
    phase15b_refs = re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage)
    if not phase15b_refs:
        errors.append(row["technology_modifier_id"] + ": no Phase 15B lineage")
    for ref in phase15b_refs:
        source = phase15b.get(ref)
        if not source:
            errors.append(row["technology_modifier_id"] + ": missing Phase 15B lineage " + ref)
        elif family not in set(source.get("technology_family", "").split(";")):
            errors.append(row["technology_modifier_id"] + ": Phase 15B family mismatch " + ref)
    return errors


def manifest_entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(value, dict)
    return value


def verify_freeze(path: Path, phase: str, count: int) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload.get("accepted_phase") == phase, path
    assert payload.get("status") == "ACCEPTED / FROZEN", path
    entries = manifest_entries(payload)
    assert len(entries) == count, (path, len(entries))
    protected: set[str] = set()
    for relative, value in entries.items():
        expected = value if isinstance(value, str) else str(value.get("sha256", ""))
        target = ROOT / relative
        assert target.is_file() and hash_matches(target, expected), (path.name, relative)
        protected.add(relative.replace("\\", "/"))
    return protected


def prior_integrity() -> tuple[int, set[str]]:
    total = 0
    paths: set[str] = set()
    for path in sorted(REPORTS.glob("*freeze_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, value in manifest_entries(payload).items():
            expected = value if isinstance(value, str) else str(value.get("sha256", ""))
            target = ROOT / relative
            assert target.is_file() and hash_matches(target, expected), (path.name, relative)
            total += 1
            paths.add(relative.replace("\\", "/"))
    return total, paths


def main() -> int:
    require_review = "--require-review" in sys.argv
    checks: dict[str, dict[str, object]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    phase14a_paths = verify_freeze(PHASE14A, "14A", 24)
    phase14b_paths = verify_freeze(PHASE14B, "14B", 23)
    phase15a_paths = verify_freeze(PHASE15A, "15A", 30)
    phase15b_paths = verify_freeze(PHASE15B, "15B", 28)
    prior_total, prior_paths = prior_integrity()
    changed = {line.replace("\\", "/") for line in subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines()}
    protected = prior_paths | phase14a_paths | phase14b_paths | phase15a_paths | phase15b_paths
    check("expected_starting_sha", subprocess.check_output(["git", "-C", str(ROOT), "merge-base", "HEAD", BASE_SHA], text=True).strip() == BASE_SHA, BASE_SHA)
    check("phase14_overall_status", json.loads(PHASE14B.read_text(encoding="utf-8")).get("phase14_overall_status") == "COMPLETE / ACCEPTED / FROZEN", "Phase 14")
    check("phase15_overall_status", json.loads(PHASE15B.read_text(encoding="utf-8")).get("phase15_overall_status") == "COMPLETE / ACCEPTED / FROZEN", "Phase 15")
    check("freeze_artifact_counts", (len(phase14a_paths), len(phase14b_paths), len(phase15a_paths), len(phase15b_paths)) == (24, 23, 30, 28), (len(phase14a_paths), len(phase14b_paths), len(phase15a_paths), len(phase15b_paths)))
    check("prior_freeze_integrity", prior_total == 593 and len(prior_paths) == 584, {"entries": prior_total, "unique_paths": len(prior_paths)})
    check("no_frozen_artifact_modified", not changed.intersection(protected), sorted(changed.intersection(protected)))
    allowed_phase16b = {"docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md", "data/processed/integration/phase16b_candidate_stress_tests.csv"}
    phase16b_changes = {path for path in changed if "phase16b" in path.lower()}
    check("phase16b_candidate_only", phase16b_changes <= allowed_phase16b, sorted(phase16b_changes - allowed_phase16b))
    check("phase17_absent", not any("phase17" in path.lower() for path in changed), sorted(path for path in changed if "phase17" in path.lower()))
    check("no_release_or_tag", not any("release" in path.lower() or "/tags/" in path.lower() for path in changed), "release/tag out of scope")

    ontology = yaml.safe_load(SYSTEMS.read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology["systems"]}
    architecture_interfaces = architecture_interface_lookup(ontology)
    assert len(system_ids) == 13
    relationship_vocab = yaml.safe_load((METADATA / "atlas_relationship_vocabulary.yml").read_text(encoding="utf-8"))
    relationship_classes = {row["class_id"] for row in relationship_vocab["normalized_relationship_classes"]}
    vocabulary = yaml.safe_load((METADATA / "basin_dynamics_vocabulary.yml").read_text(encoding="utf-8"))
    check("phase14_system_ontology", len(system_ids) == 13, sorted(system_ids))
    check("relationship_vocabulary_loaded", len(relationship_classes) >= 12, sorted(relationship_classes))
    check("evidence_vocabulary_loaded", set(vocabulary["evidence_classes"]) == EVIDENCE, vocabulary["evidence_classes"])

    frames: dict[str, list[dict[str, str]]] = {}
    for name, (path, expected) in FILES.items():
        frame = read_csv(path)
        frames[name] = frame
        check(f"schema_{name}", set(frame[0]) == expected, sorted(set(frame[0]) ^ expected))
        check(f"nonempty_{name}", bool(frame), len(frame))

    stressors = frames["stressor_catalog.csv"]
    relationships = frames["propagation_relationships.csv"]
    rules = frames["propagation_rules.csv"]
    responses = frames["adaptation_response_catalog.csv"]
    technology = frames["technology_modifier_catalog.csv"]
    feedback = frames["feedback_coupling_inventory.csv"]
    matrix = frames["system_stressor_matrix.csv"]
    candidates = frames["phase16b_candidate_stress_tests.csv"]
    stressor_ids = {row["stressor_id"] for row in stressors}
    relationship_ids = {row["relationship_id"] for row in relationships}
    response_ids = {row["response_id"] for row in responses}
    technology_ids = {row["technology_modifier_id"] for row in technology}
    allowed_stressor_classes = {row["class_id"] for row in vocabulary["stressor_classes"]}
    check("stressor_ids_unique", len(stressor_ids) == len(stressors), len(stressors))
    check("stressor_classes_resolve", {row["stressor_class"] for row in stressors} <= allowed_stressor_classes, sorted({row["stressor_class"] for row in stressors} - allowed_stressor_classes))
    check("stressor_systems_resolve", all(row["initial_system_id"] in system_ids for row in stressors), "initial system")
    check("stressor_evidence_resolve", {row["evidence_class"] for row in stressors} <= EVIDENCE, sorted({row["evidence_class"] for row in stressors} - EVIDENCE))
    check("stressor_lineage_present", all(row["source_lineage"] for row in stressors), "stressor lineage")

    direct_crosswalk = {row["atlas_relationship_id"]: row for row in read_csv(INTEGRATION / "atlas_dependency_crosswalk.csv")}
    phase15a_interfaces = {row["interface_id"]: row for row in read_csv(INTEGRATION / "technology_system_interfaces.csv")}
    phase15a_dependencies = {row["dependency_id"]: row for row in read_csv(INTEGRATION / "technology_dependencies.csv")}
    phase15b_states = {row["state_id"]: row for row in read_csv(SCENARIOS / "technology_system_states.csv")}
    phase15b_dependencies = {row["dependency_state_id"]: row for row in read_csv(SCENARIOS / "technology_dependency_states.csv")}
    phase15b_governance = {row["governance_state_id"]: row for row in read_csv(SCENARIOS / "technology_governance_states.csv")}
    scenario_state_ids = set(phase15b_dependencies)
    check("relationship_ids_unique", len(relationship_ids) == len(relationships), len(relationships))
    check("relationship_endpoints_resolve", all(row["source_system_id"] in system_ids and row["target_system_id"] in system_ids for row in relationships), "relationship endpoints")
    check("relationship_classes_resolve", {row["relationship_class"] for row in relationships} <= relationship_classes, sorted({row["relationship_class"] for row in relationships} - relationship_classes))
    check("relationship_evidence_resolve", {row["evidence_class"] for row in relationships} <= EVIDENCE, sorted({row["evidence_class"] for row in relationships} - EVIDENCE))
    check("relationship_lineage_present", all(row["source_lineage"] and row["source_artifact"] for row in relationships), "relationship lineage")
    lineage_errors: list[str] = []
    for row in relationships:
        lineage = row["source_lineage"]
        if "#AR-" in lineage:
            key = lineage.split("#", 1)[1]
            base = direct_crosswalk.get(key)
            if not base or base["source_system_id"] != row["source_system_id"] or base["target_system_id"] != row["target_system_id"] or base["normalized_relationship_class"] != row["relationship_class"]:
                lineage_errors.append(row["relationship_id"])
        elif "#TDS-" in lineage:
            key = lineage.split("#", 1)[1]
            base = phase15b_dependencies.get(key)
            if base is None:
                lineage_errors.append(f"{row['relationship_id']}: missing Phase 15B TDS lineage {key}")
            else:
                if row["baseline_or_scenario"] != "scenario-conditioned" or row["evidence_class"] != "SCENARIO_STATE":
                    lineage_errors.append(row["relationship_id"] + ": Phase 15B scenario status/evidence mismatch")
                endpoint_error = endpoint_compatibility_error(
                    row["relationship_id"],
                    row["source_system_id"],
                    row["target_system_id"],
                    base["system_a"],
                    base["system_b"],
                    lineage_kind="Phase 15B scenario dependency",
                    source_endpoint_field="system_a",
                    target_endpoint_field="system_b",
                    explicitly_undirected=base.get("directionality", "").strip().lower() in {"undirected", "bidirectional"},
                )
                if endpoint_error:
                    lineage_errors.append(endpoint_error)
        elif lineage.startswith(ARCHITECTURE_LINEAGE_PREFIX):
            base = architecture_interfaces.get(lineage)
            if base is None:
                lineage_errors.append(f"{row['relationship_id']}: missing Phase 14 architecture lineage {lineage}")
            else:
                endpoint_error = endpoint_compatibility_error(
                    row["relationship_id"],
                    row["source_system_id"],
                    row["target_system_id"],
                    str(base["source_system_id"]),
                    str(base["target_system_id"]),
                    lineage_kind="Phase 14 conceptual architecture",
                    source_endpoint_field="interfaces[0]",
                    target_endpoint_field="interfaces[1]",
                    explicitly_undirected=bool(base["explicitly_undirected"]),
                )
                if endpoint_error:
                    lineage_errors.append(endpoint_error)
        else:
            lineage_errors.append(row["relationship_id"])
    check("relationship_lineage_resolves", not lineage_errors, lineage_errors)
    relationship_status_errors = []
    for row in relationships:
        expected = {"OBSERVED_DOCUMENTED": "direct", "INFERRED": "inferred", "CONTEXT_REUSED": "inferred", "SCENARIO_STATE": "scenario-conditioned"}.get(row["evidence_class"])
        if expected and row["direct_or_inferred"] != expected:
            relationship_status_errors.append(row["relationship_id"])
    check("relationship_evidence_status_alignment", not relationship_status_errors, relationship_status_errors)
    check("no_colocation_relationships", not any(row["relationship_class"] == "co-location" or row["relationship_basis"] == "co-location" for row in relationships), "co-location is not propagation")
    check("stress_test_qualitative_only", all(row["suitable_for_stress_test_propagation"] == "QUALITATIVE_ONLY" for row in relationships), "relationship use")

    check("rule_ids_unique", len({row["rule_id"] for row in rules}) == len(rules), len(rules))
    check("removed_unsupported_rules_absent", not ({row["rule_id"] for row in rules} & REMOVED_RULE_IDS), sorted({row["rule_id"] for row in rules} & REMOVED_RULE_IDS))
    check("rule_stressor_resolution", all(row["stressor_id"] in stressor_ids for row in rules), "rule stressors")
    check("rule_relationship_resolution", all(row["relationship_id"] in relationship_ids for row in rules), "rule relationships")
    check("rule_response_resolution", all(row["response_option"] in response_ids for row in rules), "rule responses")
    check("rule_endpoints_resolution", all(row["source_system_id"] in system_ids and row["target_system_id"] in system_ids for row in rules), "rule endpoints")
    check("rule_stages_bounded", {int(row["stage"]) for row in rules} <= {1, 2}, sorted({row["stage"] for row in rules}))
    check("rule_required_lineage", all(row["source_lineage"] and row["enabling_condition"] and row["limiting_condition"] and row["uncertainty"] for row in rules), "rule lineage/conditions")
    check("scenario_rules_explicit", all(row["baseline_or_scenario"] == "scenario-conditioned" or row["baseline_or_scenario"] == "baseline" for row in rules), sorted({row["baseline_or_scenario"] for row in rules}))
    check("documented_inferred_distinction", all(row["direct_or_inferred"] in {"direct", "inferred", "scenario-conditioned"} for row in relationships + rules), "direct/inferred")
    stressor_by_id = {row["stressor_id"]: row for row in stressors}
    relationship_by_id = {row["relationship_id"]: row for row in relationships}
    rule_by_id = {row["rule_id"]: row for row in rules}
    rule_order = {row["rule_id"]: index for index, row in enumerate(rules)}
    rule_lineage_errors = []
    rule_chain_errors = []
    for index, row in enumerate(rules):
        relationship = relationship_by_id.get(row["relationship_id"])
        stressor = stressor_by_id.get(row["stressor_id"])
        if not relationship or not stressor:
            continue
        if any(row[field] != relationship[field] for field in ("source_system_id", "target_system_id", "relationship_class", "propagation_mechanism", "source_lineage")):
            rule_lineage_errors.append(row["rule_id"] + ": relationship orientation or lineage mismatch")
        if row["lineage_evidence_class"] != relationship["evidence_class"]:
            rule_lineage_errors.append(row["rule_id"] + ": lineage evidence mismatch")
        source_evidence = relationship["evidence_class"]
        if row["evidence_class"] not in COMPATIBLE_OUTPUTS.get(source_evidence, set()):
            rule_lineage_errors.append(row["rule_id"] + ": application evidence stronger than source lineage")
        expected_status = {"OBSERVED_DOCUMENTED": "direct", "INFERRED": "inferred", "CONTEXT_REUSED": "inferred", "SCENARIO_STATE": "scenario-conditioned"}.get(row["evidence_class"])
        if expected_status and row["direct_or_inferred"] != expected_status:
            rule_lineage_errors.append(row["rule_id"] + ": direct/inferred status mismatch")
        if row["evidence_class"] == "OBSERVED_DOCUMENTED" and (source_evidence != "OBSERVED_DOCUMENTED" or row["application_fit"] != "EXACT_SOURCE_APPLICATION"):
            rule_lineage_errors.append(row["rule_id"] + ": undocumented or non-exact application marked observed")
        if row["evidence_class"] == "INFERRED" and source_evidence == "OBSERVED_DOCUMENTED":
            if not row["application_fit"].startswith("QUALIFIED_INFERENCE") or "inferred" not in (row["enabling_condition"] + " " + row["limiting_condition"]).lower():
                rule_lineage_errors.append(row["rule_id"] + ": qualified inference limitation missing")
        if row["baseline_or_scenario"] == "scenario-conditioned":
            if source_evidence != "SCENARIO_STATE" or row["evidence_class"] not in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}:
                rule_lineage_errors.append(row["rule_id"] + ": scenario evidence/status mismatch")
        elif source_evidence == "SCENARIO_STATE" or row["evidence_class"] in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}:
            rule_lineage_errors.append(row["rule_id"] + ": scenario evidence used as baseline")
        stage = int(row["stage"])
        if stage == 1:
            if row["source_system_id"] != stressor["initial_system_id"] or row["chain_parent_rule_id"] or row["chain_relation_type"] != "parallel_initial_branch":
                rule_chain_errors.append(row["rule_id"] + ": invalid initial branch")
        else:
            parent = rule_by_id.get(row["chain_parent_rule_id"])
            if (not parent or rule_order[row["chain_parent_rule_id"]] >= index
                    or parent["stressor_id"] != row["stressor_id"]
                    or int(parent["stage"]) != stage - 1
                    or parent["target_system_id"] != row["source_system_id"]
                    or row["chain_relation_type"] != "sequential"):
                rule_chain_errors.append(row["rule_id"] + ": missing or invalid preceding parent")
    check("rule_source_target_and_evidence_fit", not rule_lineage_errors, rule_lineage_errors)
    check("rule_chain_continuity", not rule_chain_errors, rule_chain_errors)
    check("no_unsupported_causal_claim_fields", not any(row.get("relationship_class", "") == "causation" or row.get("propagation_mechanism", "") == "causation" for row in relationships + rules), "causation class")

    check("response_ids_unique", len(response_ids) == len(responses), len(responses))
    check("response_evidence_resolve", {row["evidence_class"] for row in responses} <= EVIDENCE, sorted({row["evidence_class"] for row in responses} - EVIDENCE))
    check("response_boundaries", all(any(term in row["adaptation_capacity_boundary"].lower() for term in ("not", "option", "without guaranteeing", "indeterminate")) for row in responses), "response capacity boundaries")
    response_lineage_errors = []
    for row in responses:
        source_evidence = lineage_evidence_class(row["source_lineage"], direct_crosswalk, phase15a_interfaces, phase15a_dependencies, phase15b_states, phase15b_dependencies, phase15b_governance)
        if source_evidence is None or row["evidence_class"] not in COMPATIBLE_OUTPUTS.get(source_evidence, set()):
            response_lineage_errors.append(row["response_id"] + ": response evidence stronger than source lineage or unresolved source")
        if row["evidence_class"] == "OBSERVED_DOCUMENTED" and source_evidence != "OBSERVED_DOCUMENTED":
            response_lineage_errors.append(row["response_id"] + ": observed response lacks documented source")
    check("response_evidence_inheritance", not response_lineage_errors, response_lineage_errors)
    check("technology_modifier_ids_unique", len(technology_ids) == len(technology), len(technology))
    phase15a_node_rows = read_csv(PHASE15A_NODES)
    phase15a_node_map = {row["technology_id"]: row for row in phase15a_node_rows}
    phase15a_technology_ids = set(phase15a_node_map)
    check("technology_modifier_resolution", all(row["phase15_technology_or_regime_id"].startswith("REGIME-") or row["phase15_technology_or_regime_id"] in phase15a_technology_ids for row in technology), "Phase 15 technology IDs")
    check("technology_modifier_evidence", {row["evidence_class"] for row in technology} <= EVIDENCE, sorted({row["evidence_class"] for row in technology} - EVIDENCE))
    modifier_lineage_errors = [error for row in technology for error in technology_lineage_errors(row, phase15a_node_map, phase15a_interfaces, phase15a_dependencies, phase15b_states, phase15b_dependencies, phase15b_governance)]
    check("technology_modifier_lineage_identity", not modifier_lineage_errors, modifier_lineage_errors)
    check("technology_not_automatically_protective", all("not automatically protective" in row["notes"].lower() for row in technology), "technology boundary")

    check("feedback_ids_unique", len({row["feedback_id"] for row in feedback}) == len(feedback), len(feedback))
    check("feedback_classes", {row["feedback_class"] for row in feedback} <= {"documented", "inferred", "scenario-conditioned", "not currently supported"}, sorted({row["feedback_class"] for row in feedback}))
    check("feedback_no_gain", all(row["numeric_gain_or_stability_claim"] == "false" for row in feedback), "feedback gain")
    check("feedback_boundary", all("not" in row["boundary"].lower() or "no " in row["boundary"].lower() for row in feedback), "feedback boundary")

    expected_matrix = len(stressors) * len(system_ids)
    check("matrix_shape", len(matrix) == expected_matrix and len({(row["stressor_id"], row["system_id"]) for row in matrix}) == expected_matrix, {"rows": len(matrix), "expected": expected_matrix})
    check("matrix_refs", all(row["stressor_id"] in stressor_ids and row["system_id"] in system_ids for row in matrix), "matrix refs")
    check("matrix_cells", {row["pathway_cell"] for row in matrix} <= CELLS, sorted({row["pathway_cell"] for row in matrix} - CELLS))
    check("matrix_not_score", all(row["is_severity_measure"] == "false" and row["is_risk_or_vulnerability_score"] == "false" for row in matrix), "matrix score flags")
    check("matrix_not_ranked", all("ranked systems" not in row["notes"].lower() and "summed rows" not in row["notes"].lower() for row in matrix), "matrix ranking")
    matrix_by_key = {(row["stressor_id"], row["system_id"]): row for row in matrix}
    scenario_targets = {(row["stressor_id"], row["target_system_id"]) for row in rules if row["baseline_or_scenario"] == "scenario-conditioned"}
    matrix_precedence_errors = []
    for stressor in stressors:
        for system_id in system_ids:
            row = matrix_by_key[(stressor["stressor_id"], system_id)]
            key = (stressor["stressor_id"], system_id)
            if stressor["baseline_or_scenario"] != "BASELINE" and system_id == stressor["initial_system_id"] and row["pathway_cell"] != "SCENARIO-CONDITIONED":
                matrix_precedence_errors.append(f"{key}: scenario initial system is not scenario-conditioned")
            if stressor["baseline_or_scenario"] != "BASELINE" and row["pathway_cell"] == "DIRECT":
                matrix_precedence_errors.append(f"{key}: scenario stressor has baseline direct cell")
            if row["pathway_cell"] == "SCENARIO-CONDITIONED" and system_id != stressor["initial_system_id"] and key not in scenario_targets:
                matrix_precedence_errors.append(f"{key}: scenario cell lacks scenario rule")
            if stressor["baseline_or_scenario"] == "BASELINE" and system_id == stressor["initial_system_id"] and row["pathway_cell"] != "DIRECT":
                matrix_precedence_errors.append(f"{key}: baseline initial system is not direct")
    check("matrix_scenario_precedence", not matrix_precedence_errors, matrix_precedence_errors)

    check("candidate_count", len(candidates) == 6 and len({row["candidate_id"] for row in candidates}) == 6, len(candidates))
    check("candidate_status", all(row["status"] == "APPROVED SCOPE / NOT IMPLEMENTED" and row["executed"] == "false" for row in candidates), "candidate execution")
    check("candidate_stressor_refs", all(all(item in stressor_ids for item in row["stressor_ids"].split(";")) for row in candidates), "candidate stressors")
    check("candidate_system_refs", all(all(item in system_ids for item in row["system_ids"].split(";")) for row in candidates), "candidate systems")

    all_text = " ".join(" ".join(row.values()) for frame in frames.values() for row in frame).lower()
    forbidden_fields = {"risk_score", "resilience_score", "vulnerability_score", "connectivity_score", "severity_score", "probability_estimate", "incidence_rate", "outbreak_probability", "health_outcome_forecast"}
    fields = set().union(*(set(frame[0]) for frame in frames.values()))
    check("no_forbidden_numeric_fields", not fields.intersection(forbidden_fields), sorted(fields.intersection(forbidden_fields)))
    check("no_numeric_probability_or_score", not re.search(r"(?:score|probability|risk|vulnerability|resilience)\s*[:=]\s*[-+]?\d", all_text), "numeric score/probability")
    check("no_health_forecast", not re.search(r"(?:cases?|incidence|deaths?|hospitalizations?|illness)\s*[:=]\s*\d", all_text), "numeric health outcome")
    check("biosecurity_high_level", all(term in all_text for term in ("no pathogen engineering", "high-level only", "no operational attack")), "biosecurity detail")

    for name, required in {
        "western_basin_stress_propagation_architecture.svg": ("Western Basin Stress Propagation Architecture", "STRESSOR", "SYSTEM EFFECT", "DEPENDENCY / INTERFACE", "PROPAGATION", "RESPONSE / ADAPTATION", "SECOND-ORDER EFFECT", "direct / documented", "inferred", "scenario-conditioned", "option ≠ capacity ≠ success"),
    }.items():
        path = FIGURES / name
        try:
            ET.parse(path)
            text = path.read_text(encoding="utf-8")
            check(f"figure_svg_{name}", all(term.lower() in text.lower() for term in required), {"bytes": path.stat().st_size, "required": required})
        except Exception as exc:
            check(f"figure_svg_{name}", False, str(exc))
    png = FIGURES / "western_basin_stress_propagation_architecture.png"
    try:
        with Image.open(png) as image:
            image.verify()
            dimensions = (image.width, image.height)
        check("figure_png", dimensions[0] >= 1200 and dimensions[1] >= 600 and png.stat().st_size > 10000, {"bytes": png.stat().st_size, "dimensions": dimensions})
    except Exception as exc:
        check("figure_png", False, str(exc))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("working_manifest_identity", manifest.get("phase") == "16A" and manifest.get("status") == "implemented_validated_pending_sol_acceptance" and manifest.get("source_commit") == BASE_SHA, {key: manifest.get(key) for key in ("phase", "status", "source_commit")})
    manifest_errors = []
    for relative, value in manifest_entries(manifest).items():
        expected = value if isinstance(value, str) else str(value.get("sha256", ""))
        target = ROOT / relative
        if not target.is_file() or not expected or not hash_matches(target, expected):
            manifest_errors.append(relative)
    check("working_manifest_artifacts", not manifest_errors, manifest_errors)
    check("manifest_phase16b_not_executed", manifest.get("phase16b_status") == "APPROVED SCOPE / NOT IMPLEMENTED" and manifest.get("no_phase16b_execution") is True, "Phase 16B")
    check("manifest_phase17_absent", manifest.get("phase17_status") == "NOT IMPLEMENTED", "Phase 17")

    if require_review:
        check("independent_review_exists", REVIEW.is_file(), str(REVIEW))
        if REVIEW.is_file():
            review = REVIEW.read_text(encoding="utf-8").lower()
            required = ['"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"propagation_errors": []', '"causal_boundary_errors": []', '"feedback_errors": []', '"evidence_classification_errors": []', '"technology_modifier_errors": []', '"biosecurity_boundary_errors": []', '"canon_boundary_errors": []']
            check("independent_review_passed", all(term in review for term in required), "review arrays")

    result = {"phase": "16A", "passed": not errors, "checks": checks, "counts": {"stressors": len(stressors), "relationships": len(relationships), "rules": len(rules), "responses": len(responses), "technology_modifiers": len(technology), "feedback": len(feedback), "matrix_cells": len(matrix), "candidates": len(candidates), "phase14a_protected_artifacts": len(phase14a_paths), "phase14b_protected_artifacts": len(phase14b_paths), "phase15a_protected_artifacts": len(phase15a_paths), "phase15b_protected_artifacts": len(phase15b_paths), "prior_freeze_entries": prior_total, "prior_freeze_unique_paths": len(prior_paths)}, "errors": errors}
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "16A", "passed": result["passed"], "counts": result["counts"], "errors": errors}, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
