#!/usr/bin/env python3
"""Build the additive Phase 16B compound cross-system stress-test package.

The builder applies only selected, already accepted Phase 16A rules.  It does
not create propagation rules, quantitative scores, probabilities, forecasts,
health outcomes, geographic layers, or Phase 17 content.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import textwrap
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import yaml

ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = ROOT / "data/processed/integration"
SCENARIOS = ROOT / "data/processed/scenarios"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
BASE_SHA = "9308127065112d0c01c294e954ae87f44e39af3f"

STRESSORS = INTEGRATION / "stressor_catalog.csv"
RULES = INTEGRATION / "propagation_rules.csv"
RESPONSES = INTEGRATION / "adaptation_response_catalog.csv"
MODIFIERS = INTEGRATION / "technology_modifier_catalog.csv"
CANDIDATES = INTEGRATION / "phase16b_candidate_stress_tests.csv"
PHASE15_SYSTEM_STATES = SCENARIOS / "technology_system_states.csv"
PHASE15_DEPENDENCY_STATES = SCENARIOS / "technology_dependency_states.csv"
PHASE15_GOVERNANCE_STATES = SCENARIOS / "technology_governance_states.csv"
VOCABULARY = ROOT / "metadata/basin_dynamics_vocabulary.yml"
SYSTEMS_PATH = ROOT / "metadata/atlas_systems.yml"
SYSTEMS_SOURCE = "metadata/atlas_systems.yml"

DEFINITIONS = INTEGRATION / "phase16b_stress_test_definitions.csv"
CHAIN_STAGES = INTEGRATION / "phase16b_chain_stages.csv"
TERMINATIONS = INTEGRATION / "phase16b_chain_terminations.csv"
SYSTEM_STATE_ROWS = INTEGRATION / "phase16b_system_states.csv"
RESPONSE_STATE_ROWS = INTEGRATION / "phase16b_response_adaptation_states.csv"
REGIME_EFFECTS = INTEGRATION / "phase16b_regime_effects.csv"
UNCERTAINTIES = INTEGRATION / "phase16b_uncertainties.csv"
COMPARISON = INTEGRATION / "phase16b_cross_test_comparison.csv"
NARRATIVE_HOOKS = INTEGRATION / "phase16b_narrative_hooks.csv"

FIGURE_ONE_PNG = FIGURES / "phase16b_compound_stress_propagation.png"
FIGURE_ONE_SVG = FIGURES / "phase16b_compound_stress_propagation.svg"
FIGURE_TWO_PNG = FIGURES / "phase16b_technology_regime_effects.png"
FIGURE_TWO_SVG = FIGURES / "phase16b_technology_regime_effects.svg"

REPORT_MAIN = REPORTS / "phase16b_compound_cross_system_stress_tests.md"
REPORT_QA = REPORTS / "phase16b_qa.md"
REPORT_PROVENANCE = REPORTS / "phase16b_provenance_lineage.md"
REPORT_COMPARISON = REPORTS / "phase16b_scenario_comparison.md"
REPORT_HOOKS = REPORTS / "phase16b_narrative_hooks.md"
MANIFEST = REPORTS / "phase16b_manifest.json"

IMPLEMENTED = (
    "P16B-CAND-001",
    "P16B-CAND-002",
    "P16B-CAND-003",
    "P16B-CAND-004",
)
RESERVE = ("P16B-CAND-005", "P16B-CAND-006")
REGIMES = OrderedDict(
    (
        (
            "A",
            {
                "family": "Coordinated Technological Adaptation",
                "modifier_id": "TM-16A-009",
                "scenario_2050": "A2050",
                "modifier_lineage_terms": ("TSS-A2050-01", "TDS-A2050-01"),
                "allowed_effects": (
                    "reduce propagation",
                    "improve coordination",
                    "increase observability",
                ),
                "axes": {
                    "observability": "may increase observability in selected interfaces",
                    "coupling": "compute, energy, data, and maintenance coupling remains visible",
                    "dependency": "may reduce or delay selected pathway effects without removing dependency",
                    "redundancy": "selected redundancy or substitution options remain scenario-qualified",
                    "coordination": "may improve coordination while human authority remains required",
                    "substitution": "may create selected substitution options without proving continuity",
                    "governance_friction": "governance friction and stewardship requirements remain visible",
                    "digital_dependence": "digital dependence remains visible where observation or compute is used",
                },
            },
        ),
        (
            "B",
            {
                "family": "Uneven Networked Modernization",
                "modifier_id": "TM-16A-010",
                "scenario_2050": "B2050",
                "modifier_lineage_terms": ("TSS-B2050-01", "TDS-B2050-01"),
                "allowed_effects": (
                    "create substitution options",
                    "increase coupling",
                    "shift workforce requirements",
                ),
                "axes": {
                    "observability": "observability may be redistributed across strong and weak interfaces",
                    "coupling": "coupling may increase at bridges, duplication points, and negotiated interfaces",
                    "dependency": "dependency may be redistributed without a guaranteed continuity result",
                    "redundancy": "duplication or alternate options may be uneven; they are not immunity",
                    "coordination": "coordination remains uneven and may require negotiation across interfaces",
                    "substitution": "may create uneven substitution options with qualified access",
                    "governance_friction": "interoperability, trust, and workforce friction may persist",
                    "digital_dependence": "digital dependence may be redistributed rather than removed",
                },
            },
        ),
        (
            "C",
            {
                "family": "High Capability / High Friction Basin",
                "modifier_id": "TM-16A-011",
                "scenario_2050": "C2050",
                "modifier_lineage_terms": ("TSS-C2050-01", "TDS-C2050-01"),
                "allowed_effects": (
                    "increase observability",
                    "increase coupling",
                    "create governance / trust friction",
                    "create cyber / digital exposure",
                ),
                "axes": {
                    "observability": "capability may increase observability at selected nodes without guaranteeing interpretation",
                    "coupling": "coupling may increase across energy, data, maintenance, and governance seams",
                    "dependency": "selected dependencies may become more consequential without implying collapse",
                    "redundancy": "technical options may coexist with brittle maintenance and replacement capacity",
                    "coordination": "coordination may be delayed or contested at high-friction interfaces",
                    "substitution": "selected alternatives may exist without proving access or continuity",
                    "governance_friction": "governance and trust friction may increase while authority remains human",
                    "digital_dependence": "digital exposure and dependence may increase where capability is tightly coupled",
                },
            },
        ),
    )
)
HORIZONS = (2050, 2075)

TEST_PLAN: dict[str, list[dict[str, object]]] = {
    "P16B-CAND-001": [
        {"branch_id": "P16B-001-HEAT", "stressor_id": "STRESS-HEAT-EXTREME", "rule_ids": ["RULE-16A-001"]},
        {"branch_id": "P16B-001-LOW-FLOW", "stressor_id": "STRESS-LOW-FLOW-DROUGHT", "rule_ids": ["RULE-16A-005", "RULE-16A-006"]},
        {"branch_id": "P16B-001-GRID", "stressor_id": "STRESS-ELECTRIC-GRID", "rule_ids": ["RULE-16A-016"]},
    ],
    "P16B-CAND-002": [
        {"branch_id": "P16B-002-HAB", "stressor_id": "STRESS-HAB-WATER-QUALITY", "rule_ids": ["RULE-16A-012"]},
        {"branch_id": "P16B-002-TREATMENT-ENERGY", "stressor_id": "STRESS-WATER-TREATMENT", "rule_ids": ["RULE-16A-014"]},
        {"branch_id": "P16B-002-TREATMENT-DISEASE", "stressor_id": "STRESS-WATER-TREATMENT", "rule_ids": ["RULE-16A-015"]},
    ],
    "P16B-CAND-003": [
        {"branch_id": "P16B-003-TRANSPORT", "stressor_id": "STRESS-TRANSPORT-FREIGHT", "rule_ids": ["RULE-16A-019"]},
        {"branch_id": "P16B-003-CRITICAL-MATERIAL", "stressor_id": "STRESS-CRITICAL-MATERIAL", "rule_ids": []},
        {"branch_id": "P16B-003-FUEL", "stressor_id": "STRESS-FUEL-CONSTRAINT", "rule_ids": ["RULE-16A-020"]},
        {"branch_id": "P16B-003-FEEDSTOCK", "stressor_id": "STRESS-INDUSTRIAL-FEEDSTOCK", "rule_ids": []},
    ],
    "P16B-CAND-004": [
        {"branch_id": "P16B-004-INFECTIOUS-DATA", "stressor_id": "STRESS-INFECTIOUS-PRESSURE", "rule_ids": ["RULE-16A-022"]},
        {"branch_id": "P16B-004-INFECTIOUS-GOVERNANCE", "stressor_id": "STRESS-INFECTIOUS-PRESSURE", "rule_ids": ["RULE-16A-023"]},
        {"branch_id": "P16B-004-SURVEILLANCE", "stressor_id": "STRESS-SURVEILLANCE-STRAIN", "rule_ids": ["RULE-16A-026"]},
        {"branch_id": "P16B-004-PRIVACY", "stressor_id": "STRESS-DATA-PRIVACY", "rule_ids": ["RULE-16A-033"]},
    ],
}

HOOK_COPY = {
    "P16B-CAND-001": {
        "setting": "Generalized Maumee–western Lake Erie water / energy interface; no intake coordinate or facility geometry is selected",
        "decision": "Operators and coordinating institutions consider qualitative water observation, conservation, load-shifting, or distributed-operation options",
        "role": "Water-system and energy-system operators with public observation and coordination institutions",
        "sign": "Timing pressure, delayed coordination, or less-comparable water and energy observations across interfaces",
        "moment": "A response option is considered while the branch remains conditional and success is not assumed",
    },
    "P16B-CAND-002": {
        "setting": "Generalized nutrient–water-quality, receiving-water, and water-treatment interface in the western Lake Erie system",
        "decision": "Institutions review water-quality observations and treatment coordination without converting pressure into treatment failure or illness",
        "role": "Water operators, environmental observers, public-health/data stewards, and coordinating institutions",
        "sign": "Observation, treatment-coordination, or communication timing becomes less aligned",
        "moment": "Increased monitoring or institutional coordination is considered as an option, not a guaranteed control result",
    },
    "P16B-CAND-003": {
        "setting": "Generalized materials–freight–industrial-energy interface around regional production and logistics systems; no corridor polygon or route is asserted",
        "decision": "Industrial and logistics institutions consider alternate interfaces, supply substitution, or workforce options without forecasting production",
        "role": "Freight, materials, industrial-energy, workforce, and coordination institutions",
        "sign": "Input qualification, freight timing, energy coordination, or maintenance requirements become less aligned",
        "moment": "An alternate routing or substitution option is reviewed while access and continuity remain indeterminate",
    },
    "P16B-CAND-004": {
        "setting": "Generalized infectious-disease surveillance, diagnostic, data-stewardship, and governance interface across public-health programs",
        "decision": "Public-health and data institutions review monitoring, manual fallback, privacy-preserving access, and coordination options",
        "role": "Public-health, laboratory, surveillance, data-stewardship, governance, and aggregate workforce institutions",
        "sign": "Reporting, diagnostic interpretation, data access, or coordination timing becomes delayed or less interoperable",
        "moment": "A high-level detection or coordination response is considered without asserting incidence, transmission, or illness",
    },
}

CSV_SCHEMAS = {
    "definitions": [
        "test_id", "candidate_id", "test_class", "label", "stressor_ids", "stressor_initial_system_ids",
        "phase16a_rule_inputs", "implementation_status", "fan_out_semantics", "selection_basis", "boundary", "notes",
    ],
    "stages": [
        "stage_id", "test_id", "branch_id", "stage", "stage_status", "phase16a_stressor_id",
        "stressor_initial_system_id", "phase16a_rule_id", "phase16a_chain_parent_rule_id", "stage_parent_id",
        "chain_relation_type", "source_system_id", "target_system_id", "phase16a_relationship_id", "relationship_class",
        "propagation_mechanism", "stressor_evidence_class", "evidence_class", "lineage_evidence_class", "application_fit",
        "direct_or_inferred", "baseline_or_scenario", "scenario_state_ids", "scenario_condition", "source_state_or_effect",
        "system_effect", "technology_modifier_ids", "governance_modifier", "phase16a_response_id", "response_mechanism",
        "second_order_effect", "uncertainty", "source_lineage", "response_capacity_boundary", "notes",
    ],
    "terminations": [
        "termination_id", "test_id", "branch_id", "phase16a_stressor_id", "initial_system_id", "last_stage_id",
        "last_stage", "last_target_system_id", "baseline_or_scenario", "scenario_condition", "termination_status",
        "termination_basis", "continuation_check", "defensible_branch_termination", "notes",
    ],
    "system_states": [
        "state_id", "test_id", "branch_id", "stage_id", "stage", "position", "system_id", "state_descriptor",
        "evidence_class", "baseline_or_scenario", "scenario_state_ids", "phase16a_rule_id", "source_lineage", "notes",
    ],
    "responses": [
        "response_state_id", "test_id", "branch_id", "stage_id", "stage", "phase16a_rule_id", "phase16a_response_id",
        "response_mechanism", "response_evidence_class", "adaptation_state", "enabling_condition", "limiting_condition",
        "capacity_boundary", "source_lineage", "scenario_condition", "notes",
    ],
    "regimes": [
        "regime_effect_id", "test_id", "regime_id", "scenario_id", "horizon", "scenario_family",
        "phase16a_technology_modifier_id", "phase16a_rule_ids", "phase15_modifier_lineage_ids", "phase15_anchor_state_ids",
        "phase15_state_evidence_class", "observability_effect", "coupling_effect", "dependency_effect", "redundancy_effect",
        "coordination_effect", "substitution_effect", "governance_friction_effect", "digital_dependence_effect",
        "phase16a_allowed_effects", "relationship_status", "uncertainty", "source_lineage", "notes",
    ],
    "uncertainties": [
        "uncertainty_id", "test_id", "uncertainty_domain", "subject", "uncertainty_level", "phase16a_rule_ids",
        "what_is_unknown", "what_is_not_inferred", "scenario_condition", "source_lineage", "notes",
    ],
    "comparison": [
        "test_id", "label", "principal_stressor_count", "branch_count", "stage_count", "system_state_observations",
        "response_adaptation_states", "termination_count", "scenario_conditioned_stage_count", "fan_out_summary",
        "cross_system_interfaces", "regime_a_finding", "regime_b_finding", "regime_c_finding", "comparison_boundary",
        "source_basis",
    ],
    "hooks": [
        "hook_id", "test_id", "test_label", "system_place_setting", "operational_decision_point", "human_institutional_role",
        "observable_sign_of_strain", "adaptation_response_moment", "scientific_lineage", "status", "canon_boundary", "notes",
    ],
}


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


def load_system_registry(path: Path = SYSTEMS_PATH) -> dict[str, dict[str, object]]:
    """Load the authoritative frozen Atlas system vocabulary.

    Phase 16B must never carry a copied system list.  The Phase 14A Atlas
    ontology is the source of truth for every explicit Atlas system ID used by
    this package.
    """
    try:
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError("file is missing or empty")
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(
            f"authoritative system registry cannot be loaded: path={path}; "
            f"source={SYSTEMS_SOURCE}; error={error}"
        ) from error

    if not isinstance(payload, dict) or not isinstance(payload.get("systems"), list):
        raise RuntimeError(
            "authoritative system registry cannot be loaded: "
            f"path={path}; source={SYSTEMS_SOURCE}; missing systems list"
        )
    records = payload["systems"]
    if not records:
        raise RuntimeError(
            "authoritative system registry is empty: "
            f"path={path}; source={SYSTEMS_SOURCE}"
        )

    loaded: dict[str, dict[str, object]] = {}
    for index, record in enumerate(records, start=1):
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
        system_id = raw_system_id
        if system_id in loaded:
            raise RuntimeError(
                "authoritative system registry contains duplicate system ID: "
                f"record_id={system_id}; record_index={index}; path={path}; "
                f"source={SYSTEMS_SOURCE}"
            )
        loaded[system_id] = record
    if not loaded:
        raise RuntimeError(
            "authoritative system registry is empty after loading: "
            f"path={path}; source={SYSTEMS_SOURCE}"
        )
    return loaded


SYSTEMS = load_system_registry()


def _authoritative_systems(systems: dict[str, dict[str, object]] | None = None) -> dict[str, dict[str, object]]:
    registry = SYSTEMS if systems is None else systems
    if not isinstance(registry, dict) or not registry:
        raise RuntimeError(
            "authoritative system registry is empty at validation time: "
            f"source={SYSTEMS_SOURCE}"
        )
    if len(registry) != len(set(registry)):
        raise RuntimeError(
            "authoritative system registry has duplicate IDs at validation time: "
            f"source={SYSTEMS_SOURCE}"
        )
    return registry


def _system_membership_error(record_id: str, field: str, system_id: str) -> AssertionError:
    return AssertionError(
        "Phase 16B system membership invariant failed: "
        f"record_id={record_id}; field={field}; invalid_system_id={system_id}; "
        f"authoritative_registry={SYSTEMS_SOURCE}"
    )


def _validate_system_id(
    *,
    record_id: str,
    field: str,
    system_id: str,
    systems: dict[str, dict[str, object]] | None = None,
    allow_blank: bool = False,
) -> None:
    registry = _authoritative_systems(systems)
    value = str(system_id).strip()
    if not value and allow_blank:
        return
    if not value or value not in registry:
        raise _system_membership_error(record_id, field, value or "<blank>")


def _validate_system_row(
    record_id: str,
    row: dict[str, object],
    *,
    systems: dict[str, dict[str, object]] | None = None,
    fields: tuple[str, ...] | None = None,
) -> None:
    registry = _authoritative_systems(systems)
    selected_fields = fields or tuple(
        field
        for field in row
        if field in SYSTEM_IDENTIFIER_FIELDS
        or field.endswith("_system_id")
        or field.endswith("_system_ids")
    )
    for field in selected_fields:
        if field not in row:
            continue
        raw_value = str(row.get(field, ""))
        values = raw_value.split(";") if field.endswith("_system_ids") or field == "system_ids" else [raw_value]
        if not raw_value and field in OPTIONAL_SYSTEM_IDENTIFIER_FIELDS:
            values = []
        for value in values:
            _validate_system_id(
                record_id=record_id,
                field=field,
                system_id=value,
                systems=registry,
                allow_blank=field in OPTIONAL_SYSTEM_IDENTIFIER_FIELDS,
            )

    # Validate explicit Atlas tokens in lineage/interface fields without
    # treating EXT-/REF- reference concepts or ordinary prose as system IDs.
    for field, value in row.items():
        for system_id in SYSTEM_ID_TOKEN_RE.findall(str(value)):
            _validate_system_id(
                record_id=record_id,
                field=field,
                system_id=system_id,
                systems=registry,
            )


def _validate_system_rows(
    rows: Iterable[dict[str, object]],
    record_id_field: str,
    *,
    systems: dict[str, dict[str, object]] | None = None,
) -> None:
    for row in rows:
        record_id = str(row.get(record_id_field, "<missing>"))
        _validate_system_row(record_id, row, systems=systems)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_rows = []
    for row in rows:
        if set(row) != set(columns):
            raise AssertionError((path, sorted(set(row) ^ set(columns))))
        normalized_rows.append({column: str(row[column]) for column in columns})
    if not normalized_rows:
        raise AssertionError(f"empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized_rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.rstrip("\n") + "\n")


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    write_text(path, "\n".join(line.rstrip(" \t") for line in text.splitlines()))


def dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def refs_from_lineage(lineage: str, prefixes: tuple[str, ...] = ("TSS", "TDS", "TGS")) -> list[str]:
    expression = r"(?:" + "|".join(prefixes) + r")-[A-Z0-9-]+"
    return dedupe(re.findall(expression, lineage))


def source_rows() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    stressors = {row["stressor_id"]: row for row in read_csv(STRESSORS)}
    rules = {row["rule_id"]: row for row in read_csv(RULES)}
    responses = {row["response_id"]: row for row in read_csv(RESPONSES)}
    modifiers = {row["technology_modifier_id"]: row for row in read_csv(MODIFIERS)}
    _validate_system_rows(stressors.values(), "stressor_id")
    return stressors, rules, responses, modifiers


def build_definitions(candidate_rows: dict[str, dict[str, str]], stressor_map: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate_id in (*IMPLEMENTED, *RESERVE):
        candidate = candidate_rows[candidate_id]
        _validate_system_row(candidate_id, candidate, fields=("system_ids",))
        stressor_ids = candidate["stressor_ids"].split(";")
        for stressor_id in stressor_ids:
            _validate_system_row(stressor_id, stressor_map[stressor_id], fields=("initial_system_id",))
        initial_systems = dedupe(stressor_map[item]["initial_system_id"] for item in stressor_ids)
        implemented = candidate_id in IMPLEMENTED
        rows.append(
            {
                "test_id": candidate_id,
                "candidate_id": candidate_id,
                "test_class": "PRINCIPAL" if implemented else "RESERVE",
                "label": candidate["label"],
                "stressor_ids": candidate["stressor_ids"],
                "stressor_initial_system_ids": ";".join(initial_systems),
                "phase16a_rule_inputs": candidate["phase16a_rule_inputs"],
                "implementation_status": "IMPLEMENTED / QUALITATIVE" if implemented else "RESERVE / UNIMPLEMENTED",
                "fan_out_semantics": "parallel initial branches; compound stressors are not chained into a new rule",
                "selection_basis": candidate["selection_basis"],
                "boundary": candidate["boundary"],
                "notes": (
                    "Only selected Phase 16A rule applications are represented; no unsupported continuation is fabricated."
                    if implemented
                    else "Retained from the Phase 16A candidate registry; no Phase 16B stage, state, response, or regime result is generated."
                ),
            }
        )
    return rows


def _chain_invariant_error(
    *,
    stress_test_id: str,
    branch_id: str,
    stage: object,
    rule_id: str,
    parent_id: str,
    actual_endpoints: tuple[object, object] | None,
    expected_endpoints: tuple[object, object] | None,
    detail: str,
) -> AssertionError:
    def endpoint_text(endpoints: tuple[object, object] | None) -> str:
        if endpoints is None:
            return "<unresolved>"
        return f"{endpoints[0]} -> {endpoints[1]}"

    return AssertionError(
        "Phase 16B chain invariant failed: "
        f"stress_test_id={stress_test_id}; branch_id={branch_id}; stage={stage}; "
        f"rule_id={rule_id}; parent_id={parent_id or '<none>'}; "
        f"actual_endpoints={endpoint_text(actual_endpoints)}; "
        f"expected_endpoints={endpoint_text(expected_endpoints)}; {detail}"
    )


def build_stages(
    stressors: dict[str, dict[str, str]],
    rules: dict[str, dict[str, str]],
    responses: dict[str, dict[str, str]],
    relationships: dict[str, dict[str, str]] | None = None,
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    """Build selected stages only after enforcing Phase 16A chain invariants.

    The optional relationship map keeps the in-memory builder probe interface
    backwards-compatible while allowing callers to supply an isolated source
    snapshot.  No invalid selection is repaired or emitted.
    """
    if relationships is None:
        relationships = {
            row["relationship_id"]: row
            for row in read_csv(INTEGRATION / "propagation_relationships.csv")
        }

    rows: list[dict[str, object]] = []
    by_branch: dict[str, list[dict[str, object]]] = {}
    branch_context: dict[str, tuple[str, str]] = {}

    for test_id in IMPLEMENTED:
        for branch in TEST_PLAN[test_id]:
            branch_id = str(branch["branch_id"])
            stressor_id = str(branch["stressor_id"])
            rule_ids = [str(item) for item in branch["rule_ids"]]
            if branch_id in branch_context:
                raise _chain_invariant_error(
                    stress_test_id=test_id,
                    branch_id=branch_id,
                    stage="branch-plan",
                    rule_id=rule_ids[0] if rule_ids else "<none>",
                    parent_id="",
                    actual_endpoints=None,
                    expected_endpoints=None,
                    detail=(
                        "branch ID is reused across test/stressor contexts; "
                        f"existing_context={branch_context[branch_id]}"
                    ),
                )
            branch_context[branch_id] = (test_id, stressor_id)
            by_branch[branch_id] = []

            for sequence_index, rule_id in enumerate(rule_ids, start=1):
                parent = by_branch[branch_id][-1] if sequence_index > 1 else None
                parent_id = str(parent["stage_id"]) if parent else ""
                rule = rules.get(rule_id)
                stressor = stressors.get(stressor_id)
                actual_endpoints = (
                    (rule.get("source_system_id", "<missing>"), rule.get("target_system_id", "<missing>"))
                    if rule
                    else None
                )
                expected_source = (
                    stressor.get("initial_system_id", "<missing>")
                    if sequence_index == 1 and stressor
                    else str(parent["target_system_id"])
                    if parent
                    else "<missing>"
                )
                relationship = relationships.get(str(rule.get("relationship_id", ""))) if rule else None
                expected_endpoints = (
                    (expected_source, relationship["target_system_id"])
                    if relationship
                    else (expected_source, rule.get("target_system_id", "<missing>"))
                    if rule
                    else None
                )

                if rule is None:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=sequence_index,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=expected_endpoints,
                        detail="selected Phase 16A rule does not resolve",
                    )
                if stressor is None:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=sequence_index,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=expected_endpoints,
                        detail=f"selected Phase 16A stressor does not resolve: stressor_id={stressor_id}",
                    )
                if relationship is None:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=sequence_index,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=expected_endpoints,
                        detail=(
                            "selected Phase 16A relationship does not resolve: "
                            f"relationship_id={rule.get('relationship_id', '')}"
                        ),
                    )

                _validate_system_row(stressor_id, stressor, fields=("initial_system_id",))
                _validate_system_row(rule_id, rule, fields=("source_system_id", "target_system_id"))
                _validate_system_row(
                    str(rule["relationship_id"]),
                    relationship,
                    fields=("source_system_id", "target_system_id"),
                )

                try:
                    stage_number = int(str(rule["stage"]))
                except (KeyError, TypeError, ValueError) as error:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=rule.get("stage", sequence_index),
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=expected_endpoints,
                        detail="Phase 16A stage number is not an integer",
                    ) from error

                if rule["stressor_id"] != stressor_id:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=stage_number,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=expected_endpoints,
                        detail=(
                            "selected rule belongs to a different stressor/path context: "
                            f"rule_stressor_id={rule['stressor_id']}; selected_stressor_id={stressor_id}"
                        ),
                    )

                if sequence_index == 1:
                    if stage_number != 1:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="stage-1 selection must have stage number 1",
                        )
                    if rule["source_system_id"] != stressor["initial_system_id"]:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=(stressor["initial_system_id"], relationship["target_system_id"]),
                            detail="stage-1 rule source does not equal the stressor's accepted Phase 16A initial system",
                        )
                    if rule["chain_relation_type"] != "parallel_initial_branch":
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="stage-1 selection must be an explicit parallel_initial_branch",
                        )
                    if rule["chain_parent_rule_id"] or parent_id:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="stage-1 selection must not carry a parent stage or parent rule",
                        )
                else:
                    if parent is None:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="later-stage selection has no preceding stage in the same branch",
                        )
                    if parent["test_id"] != test_id or parent["branch_id"] != branch_id:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="parent stage does not belong to the same test and branch",
                        )
                    parent_rule_id = str(parent["phase16a_rule_id"])
                    parent_rule = rules.get(parent_rule_id)
                    if parent_rule is None or parent_rule.get("stressor_id") != stressor_id:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail=(
                                "parent rule is missing or belongs to another stressor/path context: "
                                f"parent_rule_id={parent_rule_id}"
                            ),
                        )
                    if rule["chain_relation_type"] != "sequential":
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="later-stage selection must use the sequential relation type",
                        )
                    if rule["chain_parent_rule_id"] != parent_rule_id:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail=(
                                "selected rule does not name the actual preceding parent rule: "
                                f"expected_parent_rule_id={parent_rule_id}; actual_parent_rule_id={rule['chain_parent_rule_id']}"
                            ),
                        )
                    try:
                        parent_stage_number = int(str(parent["stage"]))
                    except (KeyError, TypeError, ValueError) as error:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=expected_endpoints,
                            detail="preceding parent stage number is not an integer",
                        ) from error
                    if stage_number != parent_stage_number + 1:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=(str(parent["target_system_id"]), relationship["target_system_id"]),
                            detail=(
                                "later-stage number is not consecutive: "
                                f"expected_stage={parent_stage_number + 1}"
                            ),
                        )
                    if rule["source_system_id"] != parent["target_system_id"]:
                        raise _chain_invariant_error(
                            stress_test_id=test_id,
                            branch_id=branch_id,
                            stage=stage_number,
                            rule_id=rule_id,
                            parent_id=parent_id,
                            actual_endpoints=actual_endpoints,
                            expected_endpoints=(str(parent["target_system_id"]), relationship["target_system_id"]),
                            detail=(
                                "later-stage source does not equal the actual preceding parent target: "
                                f"parent_target={parent['target_system_id']}"
                            ),
                        )

                relationship_endpoints = (relationship["source_system_id"], relationship["target_system_id"])
                if (rule["source_system_id"], rule["target_system_id"]) != relationship_endpoints:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=stage_number,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=relationship_endpoints,
                        detail=(
                            "selected Phase 16A rule endpoints do not match the relationship endpoints; "
                            "directionality must remain source -> target"
                        ),
                    )

                response_id = str(rule.get("response_option", ""))
                response = responses.get(response_id)
                if response is None:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=stage_number,
                        rule_id=rule_id,
                        parent_id=parent_id,
                        actual_endpoints=actual_endpoints,
                        expected_endpoints=relationship_endpoints,
                        detail=f"selected Phase 16A response does not resolve: response_id={response_id}",
                    )

                scenario_ids = ";".join(refs_from_lineage(rule["source_lineage"], ("TDS", "TSS", "TGS")))
                stage_id = f"{test_id}-{branch_id}-STAGE-{sequence_index:02d}"
                parent_stage_id = str(parent["stage_id"]) if parent else ""
                row = {
                    "stage_id": stage_id,
                    "test_id": test_id,
                    "branch_id": branch_id,
                    "stage": rule["stage"],
                    "stage_status": "SCENARIO-CONDITIONED OPTIONAL STAGE" if rule["baseline_or_scenario"] == "scenario-conditioned" else "SELECTED QUALITATIVE STAGE",
                    "phase16a_stressor_id": stressor_id,
                    "stressor_initial_system_id": stressor["initial_system_id"],
                    "phase16a_rule_id": rule_id,
                    "phase16a_chain_parent_rule_id": rule["chain_parent_rule_id"],
                    "stage_parent_id": parent_stage_id,
                    "chain_relation_type": rule["chain_relation_type"],
                    "source_system_id": rule["source_system_id"],
                    "target_system_id": rule["target_system_id"],
                    "phase16a_relationship_id": rule["relationship_id"],
                    "relationship_class": rule["relationship_class"],
                    "propagation_mechanism": rule["propagation_mechanism"],
                    "stressor_evidence_class": stressor["evidence_class"],
                    "evidence_class": rule["evidence_class"],
                    "lineage_evidence_class": rule["lineage_evidence_class"],
                    "application_fit": rule["application_fit"],
                    "direct_or_inferred": rule["direct_or_inferred"],
                    "baseline_or_scenario": rule["baseline_or_scenario"],
                    "scenario_state_ids": scenario_ids,
                    "scenario_condition": (
                        f"Phase 15B state reference(s) {scenario_ids}; not a baseline path"
                        if scenario_ids
                        else "baseline Phase 16A rule application; no future scenario state is asserted"
                    ),
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
                    "notes": "Stage uses the exact frozen Phase 16A rule; fan-out remains parallel and no cross-stressor continuation is inferred.",
                }

                emitted_endpoints = (row["source_system_id"], row["target_system_id"])
                if emitted_endpoints != relationship_endpoints:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=stage_number,
                        rule_id=rule_id,
                        parent_id=parent_stage_id,
                        actual_endpoints=emitted_endpoints,
                        expected_endpoints=relationship_endpoints,
                        detail="emitted stage endpoints do not preserve the selected Phase 16A relationship direction",
                    )
                if sequence_index > 1 and row["stage_parent_id"] != parent_stage_id:
                    raise _chain_invariant_error(
                        stress_test_id=test_id,
                        branch_id=branch_id,
                        stage=stage_number,
                        rule_id=rule_id,
                        parent_id=parent_stage_id,
                        actual_endpoints=emitted_endpoints,
                        expected_endpoints=(str(parent["target_system_id"]), relationship["target_system_id"]),
                        detail="emitted stage parent does not identify the actual preceding stage",
                    )
                rows.append(row)
                by_branch[branch_id].append(row)
    _validate_system_rows(rows, "stage_id")
    return rows, by_branch


def build_terminations(
    stressors: dict[str, dict[str, str]],
    rules: dict[str, dict[str, str]],
    by_branch: dict[str, list[dict[str, object]]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for test_id in IMPLEMENTED:
        for branch in TEST_PLAN[test_id]:
            branch_id = str(branch["branch_id"])
            stressor_id = str(branch["stressor_id"])
            _validate_system_row(
                stressor_id,
                stressors[stressor_id],
                systems=systems,
                fields=("initial_system_id",),
            )
            stages = by_branch[branch_id]
            last = stages[-1] if stages else None
            if last:
                valid_continuations = [
                    rule_id
                    for rule_id, rule in rules.items()
                    if (
                        rule["stressor_id"] == stressor_id
                        and rule["chain_parent_rule_id"] == str(last["phase16a_rule_id"])
                        and rule["chain_relation_type"] == "sequential"
                        and rule["source_system_id"] == str(last["target_system_id"])
                        and int(rule["stage"]) == int(last["stage"]) + 1
                    )
                ]
                if valid_continuations:
                    raise AssertionError((branch_id, "defensible continuation exists", valid_continuations))
            else:
                valid_continuations = [rule_id for rule_id, rule in rules.items() if rule["stressor_id"] == stressor_id]
                if valid_continuations:
                    raise AssertionError((branch_id, "unselected Phase 16A rule exists", valid_continuations))
            scenario_condition = str(last["scenario_condition"]) if last else "No Phase 16A scenario or baseline stage is selected for this stressor."
            baseline_or_scenario = str(last["baseline_or_scenario"]) if last else "baseline stressor with no selected current path"
            if last:
                basis = "NO_LATER_PHASE16A_RULE_FOR_SAME_STRESSOR_AND_TARGET"
                continuation = "The selected branch was checked for a later Phase 16A rule for the same stressor beginning at the preceding target system; no defensible continuation is selected."
            else:
                basis = "NO_PHASE16A_RULE_FOR_STRESSOR"
                continuation = "The stressor has a valid Phase 16A initial system, but no defensible Phase 16A propagation rule is selected for this stressor; no stage is fabricated."
            rows.append(
                {
                    "termination_id": f"TERM-16B-{len(rows) + 1:03d}",
                    "test_id": test_id,
                    "branch_id": branch_id,
                    "phase16a_stressor_id": stressor_id,
                    "initial_system_id": stressors[stressor_id]["initial_system_id"],
                    "last_stage_id": str(last["stage_id"]) if last else "",
                    "last_stage": str(last["stage"]) if last else "0",
                    "last_target_system_id": str(last["target_system_id"]) if last else "",
                    "baseline_or_scenario": baseline_or_scenario,
                    "scenario_condition": scenario_condition,
                    "termination_status": "TERMINATED — NO DEFENSIBLE CURRENT PATH",
                    "termination_basis": basis,
                    "continuation_check": continuation,
                    "defensible_branch_termination": "true",
                    "notes": "Missing continuation is retained as a valid analytical result; termination is not a failure score or probability statement.",
                }
            )
    _validate_system_rows(rows, "termination_id", systems=systems)
    return rows


def build_system_states(
    stages: list[dict[str, object]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for stage in stages:
        for position, system_key, descriptor_key in (
            ("source", "source_system_id", "source_state_or_effect"),
            ("target", "target_system_id", "system_effect"),
        ):
            rows.append(
                {
                    "state_id": f"STATE-16B-{len(rows) + 1:03d}",
                    "test_id": stage["test_id"],
                    "branch_id": stage["branch_id"],
                    "stage_id": stage["stage_id"],
                    "stage": stage["stage"],
                    "position": position,
                    "system_id": stage[system_key],
                    "state_descriptor": stage[descriptor_key],
                    "evidence_class": stage["evidence_class"],
                    "baseline_or_scenario": stage["baseline_or_scenario"],
                    "scenario_state_ids": stage["scenario_state_ids"],
                    "phase16a_rule_id": stage["phase16a_rule_id"],
                    "source_lineage": stage["source_lineage"],
                    "notes": "Applied qualitative system state copied from the selected Phase 16A rule; descriptor is not a score, forecast, or failure claim.",
                }
            )
    _validate_system_rows(rows, "state_id", systems=systems)
    return rows


def build_response_states(
    stages: list[dict[str, object]],
    responses: dict[str, dict[str, str]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for stage in stages:
        response = responses[str(stage["phase16a_response_id"])]
        rows.append(
            {
                "response_state_id": f"RESPONSE-16B-{len(rows) + 1:03d}",
                "test_id": stage["test_id"],
                "branch_id": stage["branch_id"],
                "stage_id": stage["stage_id"],
                "stage": stage["stage"],
                "phase16a_rule_id": stage["phase16a_rule_id"],
                "phase16a_response_id": stage["phase16a_response_id"],
                "response_mechanism": response["response_mechanism"],
                "response_evidence_class": response["evidence_class"],
                "adaptation_state": "OPTION IDENTIFIED — CAPACITY AND SUCCESS REMAIN INDETERMINATE",
                "enabling_condition": response["enabling_condition"],
                "limiting_condition": response["limiting_condition"],
                "capacity_boundary": response["adaptation_capacity_boundary"],
                "source_lineage": response["source_lineage"],
                "scenario_condition": stage["scenario_condition"],
                "notes": "Response/adaptation is an option attached to the frozen rule; it is not guaranteed action, capacity, benefit, or outcome.",
            }
        )
    _validate_system_rows(rows, "response_state_id", systems=systems)
    return rows


def build_regime_effects(
    stages: list[dict[str, object]],
    modifiers: dict[str, dict[str, str]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rules_by_test: dict[str, list[str]] = {test_id: [] for test_id in IMPLEMENTED}
    for stage in stages:
        rules_by_test[str(stage["test_id"])].append(str(stage["phase16a_rule_id"]))
    rows: list[dict[str, object]] = []
    for test_id in IMPLEMENTED:
        for regime_id, meta in REGIMES.items():
            modifier_id = str(meta["modifier_id"])
            modifier = modifiers[modifier_id]
            modifier_lineage = ";".join(refs_from_lineage(modifier["source_lineage"]))
            for horizon in HORIZONS:
                scenario_id = f"{regime_id}{horizon}"
                anchor_ids = ";".join(
                    (f"TSS-{scenario_id}-01", f"TDS-{scenario_id}-01", f"TGS-{scenario_id}-01")
                )
                axes = meta["axes"]
                rows.append(
                    {
                        "regime_effect_id": f"REGIME-EFFECT-16B-{len(rows) + 1:03d}",
                        "test_id": test_id,
                        "regime_id": regime_id,
                        "scenario_id": scenario_id,
                        "horizon": horizon,
                        "scenario_family": meta["family"],
                        "phase16a_technology_modifier_id": modifier_id,
                        "phase16a_rule_ids": ";".join(rules_by_test[test_id]),
                        "phase15_modifier_lineage_ids": modifier_lineage,
                        "phase15_anchor_state_ids": anchor_ids,
                        "phase15_state_evidence_class": "SCENARIO_STATE",
                        "observability_effect": axes["observability"],
                        "coupling_effect": axes["coupling"],
                        "dependency_effect": axes["dependency"],
                        "redundancy_effect": axes["redundancy"],
                        "coordination_effect": axes["coordination"],
                        "substitution_effect": axes["substitution"],
                        "governance_friction_effect": axes["governance_friction"],
                        "digital_dependence_effect": axes["digital_dependence"],
                        "phase16a_allowed_effects": "; ".join(meta["allowed_effects"]),
                        "relationship_status": "NO NEW PROPAGATION PATHWAY — REGIME MODIFIER ONLY",
                        "uncertainty": "Scenario-conditioned qualitative effect; horizon-specific deployment, capacity, adoption, and successful adaptation remain unknown.",
                        "source_lineage": f"Phase 16A {modifier_id}; {modifier['source_lineage']}; Phase 15B anchor states {anchor_ids}",
                        "notes": "A/B/C are compared without ranking. The 2075 anchor is context for the frozen regime family; it does not create a new propagation rule or horizon-specific technology guarantee. Technology is not automatically protective.",
                    }
                )
    _validate_system_rows(rows, "regime_effect_id", systems=systems)
    return rows


def build_uncertainties(
    stages: list[dict[str, object]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    by_test: dict[str, list[dict[str, object]]] = {test_id: [] for test_id in IMPLEMENTED}
    for stage in stages:
        by_test[str(stage["test_id"])].append(stage)
    specs = {
        "P16B-CAND-001": (
            "compound timing and operating context",
            "heat, low-flow, and grid conditions can co-occur in the selected qualitative test, but event timing, duration, local operating conditions, and any cross-branch interaction are unresolved",
            "no joint probability, heat-health outcome, outage probability, capacity value, or guaranteed failure is inferred",
        ),
        "P16B-CAND-002": (
            "water-quality and treatment interface",
            "the relationship between water-quality pressure, treatment operations, observation timing, and governance coordination is not resolved at facility scale",
            "no bloom magnitude, treatment failure, contamination, exposure, dose, illness, or treatment-effect estimate is inferred",
        ),
        "P16B-CAND-003": (
            "material, freight, and energy interface",
            "input qualification, generalized freight access, industrial energy conditions, workforce requirements, and substitution timing are unresolved",
            "no exact route, shipment quantity, contract, production value, market forecast, or economic-loss forecast is inferred",
        ),
        "P16B-CAND-004": (
            "surveillance and data-governance interface",
            "diagnostic and reporting timeliness, data access, stewardship rules, coordination, and aggregate workforce conditions are unresolved",
            "no incidence, transmission, outbreak probability, disease burden, individual data, exposure, dose, or illness is inferred",
        ),
    }
    rows = []
    for test_id in IMPLEMENTED:
        subject, unknown, not_inferred = specs[test_id]
        test_stages = by_test[test_id]
        rule_ids = dedupe(str(stage["phase16a_rule_id"]) for stage in test_stages)
        lineages = dedupe(str(stage["source_lineage"]) for stage in test_stages)
        scenario_ids = dedupe(str(stage["scenario_state_ids"]) for stage in test_stages for _ in (0,))
        rows.append(
            {
                "uncertainty_id": f"UNCERTAINTY-16B-{len(rows) + 1:03d}",
                "test_id": test_id,
                "uncertainty_domain": subject,
                "subject": "selected Phase 16A chain application and optional regime comparison",
                "uncertainty_level": "material and explicitly retained",
                "phase16a_rule_ids": ";".join(rule_ids),
                "what_is_unknown": unknown,
                "what_is_not_inferred": not_inferred,
                "scenario_condition": "; ".join(scenario_ids) if scenario_ids else "baseline branches remain separate from scenario-conditioned optional branches",
                "source_lineage": "; ".join(lineages),
                "notes": "Uncertainty is not converted into a probability, severity, vulnerability, resilience, or risk score; unknown is not low or absent.",
            }
        )
    _validate_system_rows(rows, "uncertainty_id", systems=systems)
    return rows


def build_comparison(
    definitions: list[dict[str, object]],
    stages: list[dict[str, object]],
    terminations: list[dict[str, object]],
    state_rows: list[dict[str, object]],
    response_rows: list[dict[str, object]],
    regime_rows: list[dict[str, object]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    labels = {str(row["test_id"]): str(row["label"]) for row in definitions}
    implemented_defs = {str(row["test_id"]): row for row in definitions if row["test_class"] == "PRINCIPAL"}
    rows = []
    for test_id in IMPLEMENTED:
        test_stages = [row for row in stages if row["test_id"] == test_id]
        test_terms = [row for row in terminations if row["test_id"] == test_id]
        test_states = [row for row in state_rows if row["test_id"] == test_id]
        test_responses = [row for row in response_rows if row["test_id"] == test_id]
        test_regimes = {str(row["regime_id"]): row for row in regime_rows if row["test_id"] == test_id and str(row["horizon"]) == "2050"}
        rows.append(
            {
                "test_id": test_id,
                "label": labels[test_id],
                "principal_stressor_count": len(str(implemented_defs[test_id]["stressor_ids"]).split(";")),
                "branch_count": len(test_terms),
                "stage_count": len(test_stages),
                "system_state_observations": len(test_states),
                "response_adaptation_states": len(test_responses),
                "termination_count": len(test_terms),
                "scenario_conditioned_stage_count": sum(row["baseline_or_scenario"] == "scenario-conditioned" for row in test_stages),
                "fan_out_summary": "parallel initial branches; stage-2 continuation appears only where the exact Phase 16A parent target permits it",
                "cross_system_interfaces": "; ".join(dedupe(f"{row['source_system_id']}->{row['target_system_id']}" for row in test_stages)),
                "regime_a_finding": str(test_regimes["A"]["observability_effect"]) + "; " + str(test_regimes["A"]["coordination_effect"]),
                "regime_b_finding": str(test_regimes["B"]["observability_effect"]) + "; " + str(test_regimes["B"]["coupling_effect"]),
                "regime_c_finding": str(test_regimes["C"]["observability_effect"]) + "; " + str(test_regimes["C"]["governance_friction_effect"]),
                "comparison_boundary": "Qualitative comparison only; no regime ranking, score, probability, forecast, or successful-adaptation claim.",
                "source_basis": "; ".join(dedupe(str(row["source_lineage"]) for row in test_stages)) + "; Phase 15B regime anchors",
            }
        )
    _validate_system_rows(rows, "test_id", systems=systems)
    return rows


def build_hooks(
    definitions: list[dict[str, object]],
    stages: list[dict[str, object]],
    systems: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    labels = {str(row["test_id"]): str(row["label"]) for row in definitions}
    rows = []
    for test_id in IMPLEMENTED:
        test_stages = [row for row in stages if row["test_id"] == test_id]
        # The comprehension above intentionally produces a list of lists; flatten it
        # deterministically before writing the bridge row.
        flat_lineage = []
        for row in test_stages:
            flat_lineage.extend((str(row["phase16a_rule_id"]), str(row["phase16a_relationship_id"]), str(row["source_lineage"])))
        copy = HOOK_COPY[test_id]
        rows.append(
            {
                "hook_id": f"HOOK-16B-{len(rows) + 1:03d}",
                "test_id": test_id,
                "test_label": labels[test_id],
                "system_place_setting": copy["setting"],
                "operational_decision_point": copy["decision"],
                "human_institutional_role": copy["role"],
                "observable_sign_of_strain": copy["sign"],
                "adaptation_response_moment": copy["moment"],
                "scientific_lineage": "; ".join(dedupe(flat_lineage)),
                "status": "NONCANONICAL / FUTURE ATLAS HOOK",
                "canon_boundary": "Derivative bridge only; not a character, fiction, future story canon, geographic claim, or accepted scientific baseline.",
                "notes": "Later Atlas use must retain the source rule, evidence class, scenario condition, and uncertainty boundary.",
            }
        )
    _validate_system_rows(rows, "hook_id", systems=systems)
    return rows


def build_figures(definitions: list[dict[str, object]], stages: list[dict[str, object]], terminations: list[dict[str, object]], regime_rows: list[dict[str, object]]) -> dict[str, object]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "western-basin-phase16b"
    plt.rcParams["font.family"] = "DejaVu Sans"

    colors = {"A": "#2f7f73", "B": "#b47b32", "C": "#a04f55"}
    test_colors = ["#34699a", "#758e4f", "#8a5a83", "#b2643b"]

    fig, ax = plt.subplots(figsize=(16, 10), dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#f7f4ed")
    ax.set_facecolor("#f7f4ed")
    ax.text(0.02, 0.965, "Compound Stress Propagation", fontsize=24, fontweight="bold", color="#243746", va="top")
    ax.text(0.02, 0.925, "QUALITATIVE / NON-GEOGRAPHIC / NON-PROPORTIONAL — stage links reuse frozen Phase 16A rules", fontsize=10.5, color="#4b5d67", va="top")
    ax.text(0.02, 0.895, "Fan-out = parallel initial branches; termination records a missing defensible continuation, not a score or probability", fontsize=9.5, color="#4b5d67", va="top")
    headers = [(0.03, 0.18, "COMPOUND STRESSORS"), (0.27, 0.19, "INITIAL SYSTEM EFFECT"), (0.51, 0.20, "SELECTED PHASE 16A STAGES"), (0.76, 0.19, "RESPONSE / ADAPTATION"), (0.91, 0.07, "ENDPOINT")]
    for x, width, text in headers:
        ax.text(x, 0.855, text, fontsize=8.3, fontweight="bold", color="#243746", va="center")
    definitions_by_id = {str(row["test_id"]): row for row in definitions}
    for i, test_id in enumerate(IMPLEMENTED):
        y = 0.76 - i * 0.17
        base = test_colors[i]
        row = definitions_by_id[test_id]
        for x, width, _ in headers:
            ax.add_patch(FancyBboxPatch((x, y - 0.045), width, 0.09, boxstyle="round,pad=0.008,rounding_size=0.012", linewidth=0.8, edgecolor=base, facecolor="#fffdf8"))
        ax.text(0.04, y + 0.018, str(row["label"]).replace(" + ", "\n+ "), fontsize=7.4, color="#243746", va="center", wrap=True)
        branches = [branch for branch in TEST_PLAN[test_id]]
        ax.text(0.28, y + 0.018, "\n".join(f"{branch['stressor_id'].replace('STRESS-', '')}" for branch in branches), fontsize=6.9, color="#243746", va="center")
        selected = [stage for stage in stages if stage["test_id"] == test_id]
        stage_text = "\n".join(f"S{stage['stage']}: {stage['phase16a_rule_id']}\n{stage['source_system_id']} → {stage['target_system_id']}" for stage in selected)
        ax.text(0.525, y + 0.018, stage_text, fontsize=6.8, color="#243746", va="center")
        response_text = "\n".join(f"{stage['response_mechanism']} ({stage['phase16a_response_id']})" for stage in selected)
        ax.text(0.775, y + 0.018, response_text, fontsize=6.8, color="#243746", va="center")
        ax.text(0.917, y + 0.018, "TERMINATED\nNO DEFENSIBLE\nCURRENT PATH", fontsize=6.3, color="#7d3f3f", ha="center", va="center", fontweight="bold")
        for x1, x2 in ((0.21, 0.265), (0.47, 0.505), (0.72, 0.75), (0.86, 0.905)):
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops={"arrowstyle": "->", "lw": 1.0, "color": base})
    ax.text(0.02, 0.055, "Boundary: propagation ≠ probability; dependency ≠ guaranteed failure; response option ≠ successful response; contamination ≠ exposure ≠ dose ≠ illness.", fontsize=8.7, color="#4b5d67", va="bottom")
    ax.text(0.02, 0.028, "No Phase 17 content. The bridge is an analytical derivative for later Atlas review, not story canon.", fontsize=8.7, color="#4b5d67", va="bottom")
    for path in (FIGURE_ONE_PNG, FIGURE_ONE_SVG):
        fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    strip_trailing_whitespace(FIGURE_ONE_SVG)
    plt.close(fig)

    # Use top-down coordinates for this table so the separation rule is explicit
    # and auditable.  The four stress-test rows are never drawn in the header
    # band, and every card owns its text block.
    canvas_width = 24.0
    canvas_height = 18.0
    label_x = 0.70
    label_width = 4.40
    column_gap = 0.45
    regime_width = 5.70
    columns = {
        "0": (label_x, label_width),
        "A": (label_x + label_width + column_gap, regime_width),
        "B": (label_x + label_width + column_gap + regime_width + column_gap, regime_width),
        "C": (label_x + label_width + column_gap + regime_width + column_gap + regime_width + column_gap, regime_width),
    }
    header_top = 2.55
    header_height = 1.15
    header_bottom = header_top + header_height
    minimum_gap = 0.40
    data_top = 4.20
    row_height = 2.75
    row_gap = 0.45
    data_bottom = data_top + (len(IMPLEMENTED) * row_height) + ((len(IMPLEMENTED) - 1) * row_gap)
    assert data_top > header_bottom + minimum_gap, (data_top, header_bottom, minimum_gap)
    assert data_bottom < canvas_height, (data_bottom, canvas_height)
    assert columns["C"][0] + columns["C"][1] < canvas_width, columns

    fig, ax = plt.subplots(figsize=(24, 18), dpi=180)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(canvas_height, 0)
    ax.axis("off")
    fig.patch.set_facecolor("#f7f4ed")
    ax.set_facecolor("#f7f4ed")

    def wrap_block(value: object, width: int) -> str:
        return textwrap.fill(
            " ".join(str(value).split()),
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )

    def rect(x: float, top: float, width: float, height: float) -> tuple[float, float, float, float]:
        return (x, top, x + width, top + height)

    def rect_inside(inner: tuple[float, float, float, float], outer: tuple[float, float, float, float], name: str) -> None:
        assert inner[0] >= outer[0] and inner[1] >= outer[1] and inner[2] <= outer[2] and inner[3] <= outer[3], (name, inner, outer)

    def rects_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
        return first[0] < second[2] and second[0] < first[2] and first[1] < second[3] and second[1] < first[3]

    frame_rect = rect(0, 0, canvas_width, canvas_height)
    frame_texts: list[tuple[str, object]] = []
    card_texts: list[tuple[str, object, tuple[float, float, float, float]]] = []
    all_cards: list[tuple[str, tuple[float, float, float, float]]] = []

    title = ax.text(0.70, 0.55, "Technology-Regime Effects on Propagation", fontsize=25, fontweight="bold", color="#243746", va="top")
    frame_texts.append(("title", title))
    subtitle_one = ax.text(
        0.70,
        1.35,
        wrap_block("A / B / C are qualitative alternatives, not rankings. Regime modifiers alter observability, coupling, dependency, redundancy, coordination, substitution, or friction only where Phase 16A permits.", 150),
        fontsize=10.4,
        color="#4b5d67",
        va="top",
        linespacing=1.2,
    )
    frame_texts.append(("subtitle_one", subtitle_one))
    subtitle_two = ax.text(
        0.70,
        1.95,
        wrap_block("No regime creates a propagation pathway; scenario state, deployment, adoption, capacity, and successful adaptation remain unresolved.", 150),
        fontsize=10.4,
        color="#4b5d67",
        va="top",
        linespacing=1.2,
    )
    frame_texts.append(("subtitle_two", subtitle_two))

    header_rects = {
        column_id: rect(x, header_top, width, header_height)
        for column_id, (x, width) in columns.items()
    }
    for column_id, header_rect in header_rects.items():
        rect_inside(header_rect, rect(columns[column_id][0], 0, columns[column_id][1], canvas_height), f"header {column_id}")
        all_cards.append((f"header {column_id}", header_rect))
    ax.add_patch(FancyBboxPatch((columns["0"][0], header_top), columns["0"][1], header_height, boxstyle="round,pad=0.08,rounding_size=0.12", linewidth=0.9, edgecolor="#5d6d76", facecolor="#e8eeeb"))
    label_header = ax.text(
        columns["0"][0] + columns["0"][1] / 2,
        header_top + header_height / 2,
        wrap_block("STRESS TESTS", 18),
        fontsize=11.0,
        fontweight="bold",
        color="#243746",
        ha="center",
        va="center",
        linespacing=1.15,
    )
    card_texts.append(("header stress tests", label_header, header_rects["0"]))
    for regime_id in ("A", "B", "C"):
        x, width = columns[regime_id]
        ax.add_patch(FancyBboxPatch((x, header_top), width, header_height, boxstyle="round,pad=0.08,rounding_size=0.12", linewidth=1.0, edgecolor=colors[regime_id], facecolor=colors[regime_id], alpha=0.92))
        family_header = ax.text(
            x + width / 2,
            header_top + header_height / 2,
            wrap_block(f"{regime_id} — {REGIMES[regime_id]['family']}", 52),
            fontsize=11.0,
            fontweight="bold",
            color="white",
            ha="center",
            va="center",
            linespacing=1.15,
        )
        card_texts.append((f"header {regime_id}", family_header, header_rects[regime_id]))

    definitions_by_id = {str(row["test_id"]): row for row in definitions}
    regime_by_key = {
        (str(row["test_id"]), str(row["regime_id"]), str(row["horizon"])): row
        for row in regime_rows
    }
    label_wrap_width = 38
    body_wrap_width = 48
    body_line_spacing = 1.22
    for i, test_id in enumerate(IMPLEMENTED):
        top = data_top + i * (row_height + row_gap)
        row_label = str(definitions_by_id[test_id]["label"])
        label_rect = rect(columns["0"][0], top, columns["0"][1], row_height)
        all_cards.append((f"data label {test_id}", label_rect))
        ax.add_patch(FancyBboxPatch((columns["0"][0], top), columns["0"][1], row_height, boxstyle="round,pad=0.08,rounding_size=0.12", linewidth=0.9, edgecolor=test_colors[i], facecolor="#fffdf8"))
        label_text = ax.text(
            columns["0"][0] + 0.20,
            top + row_height / 2,
            wrap_block(row_label, label_wrap_width),
            fontsize=10.2,
            color="#243746",
            va="center",
            linespacing=1.18,
            clip_on=True,
        )
        card_texts.append((f"stress-test label {test_id}", label_text, label_rect))
        for regime_id in ("A", "B", "C"):
            x, width = columns[regime_id]
            card_rect = rect(x, top, width, row_height)
            all_cards.append((f"data {test_id} {regime_id}", card_rect))
            ax.add_patch(FancyBboxPatch((x, top), width, row_height, boxstyle="round,pad=0.08,rounding_size=0.12", linewidth=0.9, edgecolor=colors[regime_id], facecolor="#fffdf8"))
            row = regime_by_key[(test_id, regime_id, "2050")]
            tm_text = ax.text(
                x + 0.20,
                top + 0.22,
                f"TM {row['phase16a_technology_modifier_id']}",
                fontsize=10.0,
                color=colors[regime_id],
                fontweight="bold",
                va="top",
                clip_on=True,
            )
            card_texts.append((f"modifier {test_id} {regime_id}", tm_text, card_rect))
            body = "\n".join(
                (
                    wrap_block(f"OBSERVABILITY: {row['observability_effect']}", body_wrap_width),
                    wrap_block(f"COUPLING: {row['coupling_effect']}", body_wrap_width),
                    wrap_block(f"COORDINATION: {row['coordination_effect']}", body_wrap_width),
                    wrap_block("PATH: modifier only; no new path", body_wrap_width),
                )
            )
            body_text = ax.text(
                x + 0.20,
                top + 0.60,
                body,
                fontsize=9.0,
                color="#243746",
                va="top",
                linespacing=body_line_spacing,
                clip_on=True,
            )
            card_texts.append((f"effects {test_id} {regime_id}", body_text, card_rect))

    footer_one = ax.text(
        0.70,
        17.05,
        wrap_block("Technology may modify observability, coupling, dependency, redundancy, coordination, substitution, governance friction, or digital dependence; it is not automatically protective.", 150),
        fontsize=9.2,
        color="#4b5d67",
        va="top",
        linespacing=1.2,
    )
    frame_texts.append(("footer_one", footer_one))
    footer_two = ax.text(
        0.70,
        17.55,
        wrap_block("AI recommendation ≠ authority. Surveillance signal ≠ incidence. Adaptation ≠ elimination of stress. NON-GEOGRAPHIC / QUALITATIVE / NON-PROPORTIONAL / NON-RANKED.", 150),
        fontsize=9.2,
        color="#4b5d67",
        va="top",
        linespacing=1.2,
    )
    frame_texts.append(("footer_two", footer_two))

    # Rectangular-grid QA: all cards stay in their assigned columns, all cards
    # are disjoint, and the header band is separated from every data row.
    for name, card in all_cards:
        column_id = "0" if name.startswith(("header 0", "data label")) else next((regime for regime in ("A", "B", "C") if f" {regime}" in name), "0")
        column_rect = rect(columns[column_id][0], 0, columns[column_id][1], canvas_height)
        rect_inside(card, column_rect, name)
    for index, (first_name, first) in enumerate(all_cards):
        for second_name, second in all_cards[index + 1 :]:
            assert not rects_overlap(first, second), (first_name, second_name, first, second)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def data_bbox(artist: object) -> tuple[float, float, float, float]:
        display_bbox = artist.get_window_extent(renderer=renderer)
        points = ax.transData.inverted().transform(((display_bbox.x0, display_bbox.y0), (display_bbox.x1, display_bbox.y1)))
        return (float(min(points[:, 0])), float(min(points[:, 1])), float(max(points[:, 0])), float(max(points[:, 1])))

    rendered_card_texts: dict[str, tuple[float, float, float, float]] = {}
    for name, artist, card in card_texts:
        bbox = data_bbox(artist)
        padding = 0.10
        assert bbox[0] >= card[0] + padding and bbox[1] >= card[1] + padding and bbox[2] <= card[2] - padding and bbox[3] <= card[3] - padding, (name, bbox, card)
        rendered_card_texts[name] = bbox
    for name, artist in frame_texts:
        bbox = data_bbox(artist)
        assert bbox[0] >= frame_rect[0] + 0.05 and bbox[1] >= frame_rect[1] + 0.05 and bbox[2] <= frame_rect[2] - 0.05 and bbox[3] <= frame_rect[3] - 0.05, (name, bbox, frame_rect)

    b_text_enters_c = any(name.endswith(" B") and bbox[2] > columns["C"][0] for name, bbox in rendered_card_texts.items())
    c_text_outside_card = any(name.endswith(" C") and bbox[2] > columns["C"][0] + columns["C"][1] - 0.10 for name, bbox in rendered_card_texts.items())
    assert not b_text_enters_c, sorted(name for name, bbox in rendered_card_texts.items() if name.endswith(" B") and bbox[2] > columns["C"][0])
    assert not c_text_outside_card, sorted(name for name, bbox in rendered_card_texts.items() if name.endswith(" C") and bbox[2] > columns["C"][0] + columns["C"][1] - 0.10)

    for path in (FIGURE_TWO_PNG, FIGURE_TWO_SVG):
        fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    strip_trailing_whitespace(FIGURE_TWO_SVG)
    plt.close(fig)

    return {
        "header_top": header_top,
        "header_height": header_height,
        "header_bottom": header_bottom,
        "minimum_gap": minimum_gap,
        "data_top": data_top,
        "row_height": row_height,
        "row_gap": row_gap,
        "data_bottom": data_bottom,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "columns": {key: {"x": value[0], "width": value[1]} for key, value in columns.items()},
        "header_data_separation_passed": data_top > header_bottom + minimum_gap,
        "column_containment_passed": True,
        "card_overlap_count": 0,
        "stress_test_labels_inside_column": True,
        "wrapped_text_blocks_inside_cards": len(card_texts),
        "b_text_enters_c": False,
        "c_text_outside_figure_or_card": False,
    }


def build_reports(
    definitions: list[dict[str, object]],
    stages: list[dict[str, object]],
    terminations: list[dict[str, object]],
    states: list[dict[str, object]],
    responses: list[dict[str, object]],
    regimes: list[dict[str, object]],
    uncertainties: list[dict[str, object]],
    comparison: list[dict[str, object]],
    hooks: list[dict[str, object]],
    figure_geometry: dict[str, object],
) -> None:
    stage_counts = Counter(str(row["test_id"]) for row in stages)
    branch_counts = Counter(str(row["test_id"]) for row in terminations)
    scenario_counts = Counter(str(row["test_id"]) for row in stages if row["baseline_or_scenario"] == "scenario-conditioned")
    lines = [
        "# Phase 16B — Compound Cross-System Stress Tests",
        "",
        "## Status",
        "",
        "Phase 16B is **IMPLEMENTED / DETERMINISTICALLY VALIDATED / AWAITING INDEPENDENT REVIEW** in the additive working package; it is not integrated and has not been accepted. Phase 16A remains **ACCEPTED / FROZEN** and is the only propagation-rule framework used here. Phase 17 remains **NOT IMPLEMENTED**.",
        "",
        "FACT: Four principal tests are implemented as qualitative applications of selected frozen Phase 16A rules. Two additional Phase 16A candidates remain reserve / unimplemented.",
        "",
        "INFERENCE: A compound test places bounded stressors in one analytical context. It does not create a new cross-stressor edge, a probability, or a guaranteed joint event.",
        "",
        "SCENARIO: A/B/C regime rows reuse frozen Phase 15B state references as optional technology-regime modifiers. They are not rankings, forecasts, deployments, or new propagation paths.",
        "",
        "## Package counts",
        "",
        f"- Principal tests: **{len([row for row in definitions if row['test_class'] == 'PRINCIPAL'])}**",
        f"- Reserve tests: **{len([row for row in definitions if row['test_class'] == 'RESERVE'])}**",
        f"- Propagation stage rows: **{len(stages)}**",
        f"- Branches / termination rows: **{len(terminations)}**",
        f"- System-state observations: **{len(states)}** (two positions per propagation stage)",
        f"- Response/adaptation states: **{len(responses)}**",
        f"- A/B/C × horizon regime-effect rows: **{len(regimes)}**",
        f"- Uncertainty rows: **{len(uncertainties)}**",
        f"- Cross-test comparison rows: **{len(comparison)}**",
        f"- Noncanonical Atlas hooks: **{len(hooks)}**",
        "",
        "Counts are structural inventory counts, not scores or measures of severity, risk, resilience, vulnerability, probability, or outcome.",
        "",
        "## Principal and reserve tests",
        "",
        "| Test | Class | Status | Stressors | Phase 16A rule inputs |",
        "|---|---|---|---|---|",
    ]
    for row in definitions:
        lines.append(f"| `{row['test_id']}` | {row['test_class']} | {row['implementation_status']} | {row['label']} | `{row['phase16a_rule_inputs']}` |")
    lines.extend(
        [
            "",
            "The reserve rows remain in `phase16b_stress_test_definitions.csv` only as reserve / unimplemented inventory. No stage or regime result is generated for them.",
            "",
            "## Propagation chains and fan-out",
            "",
            "Every stage row carries its exact Phase 16A stressor, rule, relationship, evidence class, response, source lineage, and optional technology modifier IDs. Stage 1 rows are parallel initial branches. Later stages require the exact preceding target and same-stressor parent relationship. The only selected stage-2 continuation is the low-flow branch in principal test 001.",
            "",
            "| Test | Stage rows | Branches | Scenario-conditioned stages | Termination result |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in comparison:
        lines.append(f"| `{row['test_id']}` | {row['stage_count']} | {row['branch_count']} | {row['scenario_conditioned_stage_count']} | {row['termination_count']} × TERMINATED — NO DEFENSIBLE CURRENT PATH |")
    lines.extend(
        [
            "",
            "Fan-out is not sequential propagation. Compound stressors are retained as co-occurring test inputs; no unsupported rule is invented to join branches. `TERMINATED — NO DEFENSIBLE CURRENT PATH` is a valid result when the frozen Phase 16A vocabulary does not support a continuation.",
            "",
            "## System states and responses",
            "",
            "System-state rows copy the source and target descriptors from each selected Phase 16A rule. Response/adaptation rows copy the referenced Phase 16A response mechanism, enabling condition, limiting condition, evidence class, and capacity boundary. An option is not a successful response.",
            "",
            "## Technology-regime comparison",
            "",
            "The A/B/C regime effects are qualitative and non-ranked:",
            "",
            "- **A — Coordinated Technological Adaptation:** selected interfaces may gain observability and coordination or selected buffering/substitution options, while energy, compute, data, maintenance, and human-authority dependencies remain visible.",
            "- **B — Uneven Networked Modernization:** observability, substitution, duplication, and workforce requirements may be redistributed across strong and weak interfaces; coupling and negotiation friction remain uneven.",
            "- **C — High Capability / High Friction Basin:** capability and observability may increase at selected nodes while coupling, governance/trust friction, cyber/digital exposure, and brittle maintenance dependencies remain visible without implying collapse.",
            "",
            "No regime creates a propagation pathway unsupported by Phase 16A. The regime table retains the exact Phase 16A technology modifier IDs and frozen Phase 15B state references.",
            "",
            "## Uncertainty and scientific boundaries",
            "",
            "The package does not create risk, resilience, vulnerability, severity, or connectivity scores; probabilities; economic-loss forecasts; health-outcome forecasts; or epidemiological predictions. Boundary shorthand: propagation ≠ probability; dependency ≠ guaranteed failure; response option ≠ successful response; AI recommendation ≠ authority. Co-location is not causation. Contamination, exposure, dose, and illness remain distinct. Surveillance signal is not incidence.",
            "",
            "Biosecurity remains high-level only: governance, surveillance, diagnostics, data stewardship, public-health coordination, workforce continuity, and resilience interfaces. No pathogen engineering; no operational attack; no transmission optimization; no evasion; no laboratory procedure; and no harmful-biology detail is represented.",
            "",
            "## Noncanonical / future Atlas bridge",
            "",
            "Each principal test has one explicitly labeled `NONCANONICAL / FUTURE ATLAS HOOK` row. These rows provide a generalized system/place setting, operational decision point, human/institutional role, observable sign of strain, response moment, and scientific lineage only. They create no characters, fiction, future story canon, geography, or baseline fact.",
            "",
            "## Protected project state",
            "",
            "Phase 16A is **ACCEPTED / FROZEN**. Phase 15 is **COMPLETE / ACCEPTED / FROZEN**. Phase 14 is **COMPLETE / ACCEPTED / FROZEN**. Great Black Swamp remains **C — HOLD / noncanonical**. The Toledo intake-coordinate discrepancy remains **UNRESOLVED**. Deferred Phase 6B manifest-status wording, Phase 3A missing manifest status, and Phase 2A superseded legacy-worktree maintenance remain deferred.",
            "",
            "No release or tag was created.",
        ]
    )
    write_text(REPORT_MAIN, "\n".join(lines))

    qa_lines = [
        "# Phase 16B QA — Compound Cross-System Stress Tests",
        "",
        "## Required deterministic checks",
        "",
        "- Exactly four principal tests are implemented; candidates 005 and 006 remain `RESERVE / UNIMPLEMENTED` with no generated stages or regime results.",
        "- Each stressor resolves to the frozen Phase 16A stressor catalog and has a valid initial system.",
        "- The builder loads the authoritative Atlas system vocabulary from `metadata/atlas_systems.yml`; duplicate, empty, unavailable, or noncanonical system IDs fail with record and field context.",
        "- Each stage resolves to an existing Phase 16A rule, relationship, response, and optional technology modifier; no Phase 16B rule is created.",
        "- Stage-1 initial systems match the stressor initial system and use parallel fan-out. Later stages match the exact preceding target and same-stressor Phase 16A parent.",
        "- Relationship source/target direction, relationship class, mechanism, lineage, application evidence, and scenario status are copied without reversal or strengthening.",
        "- Scenario-conditioned stages retain their Phase 15B state references and are never represented as baseline direct paths.",
        "- Every branch terminates explicitly. A missing continuation is recorded as `TERMINATED — NO DEFENSIBLE CURRENT PATH` rather than being forced.",
        "- System-state descriptors and response/adaptation states resolve to their selected Phase 16A stage/rule/response source.",
        "- Regime rows resolve to Phase 16A technology modifiers and frozen Phase 15B scenario state records; regime effects cannot create a new propagation pathway.",
        "- Evidence inheritance, source lineage, uncertainty, response capacity boundaries, and active scenario conditions remain machine-readable.",
        "- No score, probability, forecast, economic-loss forecast, health-outcome forecast, dose, illness, or unsupported causal field is present.",
        "- Infectious-disease and biosecurity content remains high-level only; no pathogen engineering; no operational attack detail; no transmission optimization; no evasion method; and no laboratory procedure is represented.",
        "- Narrative hooks are explicitly `NONCANONICAL / FUTURE ATLAS HOOK` and contain no characters or story canon.",
        "- Phase 16A, Phase 15A/15B, Phase 14A/14B, and all prior freeze-manifest artifacts remain unchanged.",
        "",
        "## Figure QA intent",
        "",
        "- `phase16b_compound_stress_propagation.png/.svg` is qualitative, non-geographic, non-proportional, and shows the four tests, fan-out, selected stage links, response/adaptation, and defensible branch termination.",
        "- `phase16b_technology_regime_effects.png/.svg` shows A/B/C qualitative modifier effects without ranking, scoring, or new propagation edges.",
        "- SVG text remains inspectable; PNG dimensions and signatures are machine-checked.",
        "",
        "## Deterministic technology-regime geometry QA",
        "",
        f"- Header row: top={figure_geometry['header_top']:.2f}, height={figure_geometry['header_height']:.2f}, bottom={figure_geometry['header_bottom']:.2f}; first data row top={figure_geometry['data_top']:.2f}; minimum gap={figure_geometry['minimum_gap']:.2f}; `data_top > header_bottom + minimum_gap` is asserted.",
        f"- Grid: dedicated column 0 plus A/B/C columns; row height={figure_geometry['row_height']:.2f}; row gap={figure_geometry['row_gap']:.2f}; all {figure_geometry['card_overlap_count']} card-rectangle overlaps detected.",
        f"- Containment: {figure_geometry['wrapped_text_blocks_inside_cards']} wrapped card text blocks passed rendered bounding-box checks; all four stress-test labels remain inside column 0; B text enters C={figure_geometry['b_text_enters_c']}; C text outside its figure/card={figure_geometry['c_text_outside_figure_or_card']}.",
        "",
        "## Validation commands",
        "",
        "- `python src/python/systems/build_phase16b_stress_tests.py`",
        "- `python src/python/systems/validate_phase16b_stress_tests.py`",
        "- `Rscript src/R/systems/validate_phase16b_stress_tests.R`",
        "- Independent review is not part of this checkpoint; use `--require-review` only after a valid final passed review record exists at `reports/phase16b_independent_review.md`.",
        "- `npm run test`",
        "- `npm run build`",
        "- `git diff --check`",
    ]
    write_text(REPORT_QA, "\n".join(qa_lines))

    provenance_lines = [
        "# Phase 16B Provenance and Lineage",
        "",
        "## Result model",
        "",
        "Every propagation stage is a derived application of an accepted Phase 16A rule. The package does not introduce a new propagation relationship or mechanism. The source rule supplies the stressor, relationship, endpoints, mechanism, application evidence, lineage evidence, scenario condition, response, uncertainty, and optional Phase 15 technology modifier.",
        "",
        "## Frozen lineage layers",
        "",
        "- Phase 16A stressor, relationship, rule, response, and technology-modifier catalogs are read-only inputs.",
        "- Phase 14 relationship direction and evidence lineage remain inherited through the Phase 16A relationship and rule records.",
        "- Phase 15A/15B technology lineage is inherited through the Phase 16A technology-modifier catalog and the Phase 15B state anchors in the regime table.",
        "- Scenario-conditioned Phase 16A rules retain their `SCENARIO_STATE` evidence and Phase 15B state IDs; they do not become baseline direct paths.",
        "- Response rows retain the Phase 16A response catalog source lineage and capacity boundary; response option does not imply successful response.",
        "",
        "## Evidence classification",
        "",
        "`OBSERVED_DOCUMENTED`, `INFERRED`, and `SCENARIO_STATE` remain distinct in the stage table. A derived stage cannot be stronger than the selected Phase 16A rule or its underlying relationship. Current-path absence is represented by an explicit termination row, not by a fabricated inferred edge.",
        "",
        "## A/B/C regime layer",
        "",
        "Regime rows cite `TM-16A-009`, `TM-16A-010`, or `TM-16A-011`, then resolve the modifier's Phase 15B lineage and representative 2050/2075 state anchors. The table is an optional scenario modifier layer; it does not change chain topology. The three regimes are compared without ranking.",
        "",
        "## Uncertainty and negative scope",
        "",
        "The package leaves event coincidence, duration, local operating conditions, access, capacity, governance, diagnostic timeliness, exposure, dose, illness, incidence, transmission, and economic consequences unresolved where Phase 16A does not support them. No numeric risk, resilience, vulnerability, severity, probability, forecast, economic-loss, or health-outcome field is created.",
        "",
        "Biosecurity is high-level only: surveillance, diagnostics, data stewardship, public-health governance, communication, workforce continuity, and resilience. No pathogen engineering; no operational attack; no transmission optimization; no evasion; and no laboratory procedure is modeled.",
        "",
        "## Holds",
        "",
        "Great Black Swamp remains `C — HOLD / noncanonical`; the Toledo intake-coordinate discrepancy remains `UNRESOLVED`; deferred Phase 6B/3A/2A maintenance is unchanged.",
    ]
    stage_by_id = {str(row["stage_id"]): row for row in stages}
    response_stage_ids = {str(row["stage_id"]) for row in responses}
    audit_rows = []
    for term in terminations:
        stage = stage_by_id.get(str(term["last_stage_id"]))
        if stage:
            final_stage = f"stage {stage['stage']} / {stage['phase16a_rule_id']}"
            final_target = str(term["last_target_system_id"])
            continuation = "NONE — no valid same-stressor sequential Phase 16A rule begins at the final target"
            response_state = "PRESENT" if str(stage["stage_id"]) in response_stage_ids else "MISSING"
        else:
            final_stage = "no selected stage"
            final_target = "—"
            continuation = "NONE — no Phase 16A rule exists for the stressor"
            response_state = "NOT APPLICABLE"
        audit_rows.append(
            f"| `{term['branch_id']}` | {final_stage} | `{final_target}` | {continuation} | {response_state} | PASS |"
        )
    provenance_lines.extend(
        [
            "",
            "## Branch termination audit",
            "",
            "The builder checked every Phase 16B branch against the complete frozen Phase 16A rule catalog. For staged branches, the check required no unused sequential rule with the same stressor, the final selected rule as parent, the final target as source, and the next stage number. For stressors with no selected stage, the check required no Phase 16A rule for that stressor. Rule, relationship, endpoint, and response lookups were resolved before this termination disposition; every staged final row has a response/adaptation state. No termination is caused by lookup failure, endpoint reversal, unresolved rule lineage, or suppressed parallel fan-out.",
            "",
            "| Branch | Final selected stage | Final target | Valid unused continuation | Final response state | Audit |",
            "|---|---|---|---|---|---|",
            *audit_rows,
        ]
    )
    write_text(REPORT_PROVENANCE, "\n".join(provenance_lines))

    comparison_lines = [
        "# Phase 16B A/B/C Scenario Comparison",
        "",
        "This comparison is a qualitative scenario-conditioned reading of the three frozen Phase 15B regimes. It does not rank A/B/C and does not calculate a score, probability, forecast, or successful-adaptation result.",
        "",
        "| Test | A — Coordinated Technological Adaptation | B — Uneven Networked Modernization | C — High Capability / High Friction Basin |",
        "|---|---|---|---|",
    ]
    for row in comparison:
        comparison_lines.append(f"| {row['label']} | {row['regime_a_finding']} | {row['regime_b_finding']} | {row['regime_c_finding']} |")
    comparison_lines.extend(
        [
            "",
            "A may buffer selected interfaces through coordination, observability, and qualified substitution options while retaining dependencies. B may redistribute observability, coupling, and substitution across uneven nodes. C may combine high capability with greater coupling, governance/trust friction, and digital exposure at selected seams. None creates a Phase 16A propagation pathway or guarantees continuity.",
            "",
            "2050 and 2075 rows use the frozen Phase 15B state identifiers as regime/horizon context. The 2075 rows preserve wider structural uncertainty; they are not a precision increase or automatic intensification.",
            "",
            "AI recommendation remains advisory; sensing remains distinct from enforcement; surveillance signal remains distinct from incidence; adaptation remains distinct from elimination of stress.",
        ]
    )
    write_text(REPORT_COMPARISON, "\n".join(comparison_lines))

    hook_lines = [
        "# Phase 16B Narrative-Hook Bridge",
        "",
        "The following rows are a small derivative bridge for later Atlas work. They are not fiction, characters, future story canon, geographic facts, or accepted baseline changes.",
        "",
        "| Test | Setting | Decision point | Role | Sign of strain | Response moment | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in hooks:
        hook_lines.append(f"| {row['test_label']} | {row['system_place_setting']} | {row['operational_decision_point']} | {row['human_institutional_role']} | {row['observable_sign_of_strain']} | {row['adaptation_response_moment']} | **{row['status']}** |")
    hook_lines.extend(
        [
            "",
            "Every row retains scientific lineage in `data/processed/integration/phase16b_narrative_hooks.csv`. No character, dialogue, plot, future event, exact facility, intake coordinate, route, or story canon is established.",
        ]
    )
    write_text(REPORT_HOOKS, "\n".join(hook_lines))


def build_manifest(counts: dict[str, int]) -> None:
    artifacts = [
        DEFINITIONS,
        CHAIN_STAGES,
        TERMINATIONS,
        SYSTEM_STATE_ROWS,
        RESPONSE_STATE_ROWS,
        REGIME_EFFECTS,
        UNCERTAINTIES,
        COMPARISON,
        NARRATIVE_HOOKS,
        FIGURE_ONE_PNG,
        FIGURE_ONE_SVG,
        FIGURE_TWO_PNG,
        FIGURE_TWO_SVG,
        REPORT_MAIN,
        REPORT_QA,
        REPORT_PROVENANCE,
        REPORT_COMPARISON,
        REPORT_HOOKS,
        ROOT / "src/python/systems/build_phase16b_stress_tests.py",
        ROOT / "src/python/systems/validate_phase16b_stress_tests.py",
        ROOT / "src/R/systems/validate_phase16b_stress_tests.R",
    ]
    entries = OrderedDict()
    for path in artifacts:
        relative = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        entries[relative] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "role": "Phase 16B working package artifact",
        }
    payload = {
        "phase": "16B",
        "status": "implemented_deterministically_validated_awaiting_independent_review",
        "source_commit": BASE_SHA,
        "scope": "Compound Cross-System Stress Tests",
        "phase16a_status": "ACCEPTED / FROZEN",
        "phase15_status": "COMPLETE / ACCEPTED / FROZEN",
        "phase14_status": "COMPLETE / ACCEPTED / FROZEN",
        "phase17_status": "NOT IMPLEMENTED",
        "qualitative_only": True,
        "no_scores_probabilities_or_forecasts": True,
        "no_new_phase16a_propagation_rules": True,
        "principal_test_count": 4,
        "reserve_test_count": 2,
        "active_holds_preserved": {
            "great_black_swamp": "C — HOLD / noncanonical",
            "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
        },
        "deferred_maintenance_preserved": [
            "Phase 6B manifest-status wording mismatch",
            "Phase 3A missing manifest status",
            "Phase 2A superseded legacy worktree",
        ],
        "counts": counts,
        "artifacts": entries,
        "release_created": False,
        "tag_created": False,
    }
    write_text(MANIFEST, json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> int:
    stressors, rules, responses, modifiers = source_rows()
    candidate_map = {row["candidate_id"]: row for row in read_csv(CANDIDATES)}
    if set(candidate_map) != set(IMPLEMENTED + RESERVE):
        raise AssertionError("Phase 16A candidate registry does not contain exactly the expected six candidates")
    definitions = build_definitions(candidate_map, stressors)
    stages, by_branch = build_stages(stressors, rules, responses)
    terminations = build_terminations(stressors, rules, by_branch)
    state_rows = build_system_states(stages)
    response_rows = build_response_states(stages, responses)
    regime_rows = build_regime_effects(stages, modifiers)
    uncertainty_rows = build_uncertainties(stages)
    comparison_rows = build_comparison(definitions, stages, terminations, state_rows, response_rows, regime_rows)
    hooks = build_hooks(definitions, stages)

    write_csv(DEFINITIONS, CSV_SCHEMAS["definitions"], definitions)
    write_csv(CHAIN_STAGES, CSV_SCHEMAS["stages"], stages)
    write_csv(TERMINATIONS, CSV_SCHEMAS["terminations"], terminations)
    write_csv(SYSTEM_STATE_ROWS, CSV_SCHEMAS["system_states"], state_rows)
    write_csv(RESPONSE_STATE_ROWS, CSV_SCHEMAS["responses"], response_rows)
    write_csv(REGIME_EFFECTS, CSV_SCHEMAS["regimes"], regime_rows)
    write_csv(UNCERTAINTIES, CSV_SCHEMAS["uncertainties"], uncertainty_rows)
    write_csv(COMPARISON, CSV_SCHEMAS["comparison"], comparison_rows)
    write_csv(NARRATIVE_HOOKS, CSV_SCHEMAS["hooks"], hooks)
    figure_geometry = build_figures(definitions, stages, terminations, regime_rows)
    build_reports(definitions, stages, terminations, state_rows, response_rows, regime_rows, uncertainty_rows, comparison_rows, hooks, figure_geometry)

    counts = {
        "principal_tests": len(IMPLEMENTED),
        "reserve_tests": len(RESERVE),
        "chain_stages": len(stages),
        "branches": len(terminations),
        "system_state_observations": len(state_rows),
        "response_adaptation_states": len(response_rows),
        "regime_effect_rows": len(regime_rows),
        "uncertainty_rows": len(uncertainty_rows),
        "comparison_rows": len(comparison_rows),
        "narrative_hooks": len(hooks),
        "scenario_conditioned_stages": sum(row["baseline_or_scenario"] == "scenario-conditioned" for row in stages),
        "terminated_branches": sum(row["termination_status"] == "TERMINATED — NO DEFENSIBLE CURRENT PATH" for row in terminations),
    }
    build_manifest(counts)
    print(json.dumps({"phase": "16B", "counts": counts, "manifest": "reports/phase16b_manifest.json"}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
