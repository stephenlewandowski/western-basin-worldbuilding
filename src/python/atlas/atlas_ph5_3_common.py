"""Shared paths, palette, and source contract for Phase 17A Prototype 5.3."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = ROOT / "data" / "processed" / "integration"
OUT_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "5_3_industrial_exchange"

INPUTS = {
    "phase14b_atlas_dependency_crosswalk": INTEGRATION / "atlas_dependency_crosswalk.csv",
    "phase14b_relationship_normalization": INTEGRATION / "relationship_normalization_crosswalk.csv",
    "phase15a_technology_interfaces": INTEGRATION / "technology_system_interfaces.csv",
    "phase15a_technology_dependencies": INTEGRATION / "technology_dependencies.csv",
    "phase16a_propagation_relationships": INTEGRATION / "propagation_relationships.csv",
    "phase16b_regime_effects": INTEGRATION / "phase16b_regime_effects.csv",
}

REQUIRED_COLUMNS = {
    "phase14b_atlas_dependency_crosswalk": {
        "atlas_relationship_id",
        "source_system_id",
        "target_system_id",
        "normalized_relationship_class",
        "evidence_class",
        "documented_or_inferred",
        "suitable_for_visualization",
        "suitable_for_qualitative_reasoning",
        "suitable_for_quantitative_aggregation",
        "caveat",
    },
    "phase14b_relationship_normalization": {
        "atlas_normalization_id",
        "local_term",
        "normalized_relationship_class",
        "directionality",
        "flow_semantics",
        "Atlas_join_role",
        "mapping_status",
        "information_loss_or_caveat",
    },
    "phase15a_technology_interfaces": {
        "interface_id",
        "technology_id",
        "technology_family",
        "technology_label",
        "technology_status",
        "source_system_id",
        "target_system_id",
        "interface_type",
        "normalized_relationship_class",
        "evidence_class",
        "dependency_basis",
        "governance_interface",
        "uncertainty",
        "source_id",
    },
    "phase15a_technology_dependencies": {
        "dependency_id",
        "technology_id",
        "technology_family",
        "dependency_class",
        "dependency_role",
        "dependency_label",
        "affected_system_id",
        "technology_status",
        "evidence_class",
        "dependency_basis",
        "limitation",
        "governance_interface",
        "uncertainty",
        "source_id",
    },
    "phase16a_propagation_relationships": {
        "relationship_id",
        "source_system_id",
        "target_system_id",
        "relationship_class",
        "propagation_mechanism",
        "evidence_class",
        "direct_or_inferred",
        "baseline_or_scenario",
        "relationship_basis",
        "limitation",
        "uncertainty",
        "notes",
    },
    "phase16b_regime_effects": {
        "regime_effect_id",
        "scenario_id",
        "horizon",
        "scenario_family",
        "coordination_effect",
        "substitution_effect",
        "digital_dependence_effect",
        "relationship_status",
        "uncertainty",
        "notes",
    },
}

# Visual Grammar v0.3 working palette. Exact colors remain unfrozen.
PAPER = "#F3EFE4"
PANEL = "#FBFAF5"
INK = "#263238"
MUTED = "#66727A"
RULE = "#B7B0A5"
E = "#355F7A"
S = "#A87536"
K = "#776486"
C = "#4E756A"
WATER = "#3C6E8F"
WATER_LIGHT = "#B9DDEB"
MATERIAL = "#B36B3C"
MATERIAL_LIGHT = "#E7C7B3"
THERMAL = "#C76D3E"
THERMAL_LIGHT = "#F0D8C8"
ENERGY = "#D18E35"
ENERGY_LIGHT = "#F1DCA9"
DATA = "#806B8E"
DATA_LIGHT = "#E6DDEB"
MAINTENANCE = "#A94F3E"
ECOLOGY = "#466B50"
ECOLOGY_LIGHT = "#D7E2C7"
ROAD = "#B3A28C"
STEEL = "#9CA9AA"
CONCRETE = "#C9C8C0"
BRICK = "#A95A45"
RETROFIT = "#7E9D9A"

FLOW_LW = 1.35
INFO_LW = 1.25
DEPENDENCY_LW = 1.25

ALLOWED_EDGE_FAMILIES = {
    "external_input",
    "internal_use",
    "recovery",
    "transformation",
    "recirculation",
    "product_output",
    "residual_output",
    "discharge",
    "information",
    "dependency",
    "scenario_interface",
    "sketch_interface",
}

PANEL_FILES = [
    "5_3a_industrial_district.png",
    "5_3b_exchange_network.png",
    "5_3c_residual_to_input.png",
    "5_3d_open_system_governance.png",
]
CONTACT_SHEET = OUT_DIR / "5_3_contact_sheet.png"
MANIFEST = OUT_DIR / "5_3_source_manifest.json"
VALIDATION_REPORT = OUT_DIR / "5_3_validation_report.md"
