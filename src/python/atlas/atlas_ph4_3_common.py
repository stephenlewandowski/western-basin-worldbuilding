"""Shared paths, palette, and semantic contract for Prototype 4.3.

Prototype 4.3 is an additive Phase 17A presentation layer. It reads accepted
source tables but does not modify them. The farm geometry is synthetic and
illustrative: no parcel, dimensions, crop yield, nutrient load, energy capacity,
or performance result is asserted.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "processed"
NETWORKS = DATA / "networks"
ANALYSIS = DATA / "analysis"
INTEGRATION = DATA / "integration"
OUT_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "4_3_farm_2075"

INPUTS = {
    "agriculture_hydrology_context": NETWORKS / "water_system_nodes.csv",
    "hydrology_relationships": NETWORKS / "water_system_edges.csv",
    "nutrient_flux_relationships": NETWORKS / "biogeochemical_flux_edges.csv",
    "nutrient_management_controls": ANALYSIS / "biogeochemical_control_register.csv",
    "ecology_components": NETWORKS / "ecology_system_nodes.csv",
    "ecology_relationships": NETWORKS / "ecology_system_edges.csv",
    "ecology_indicators": ANALYSIS / "ecological_indicators_2026.csv",
    "energy_assets": NETWORKS / "energy_system_nodes.csv",
    "energy_relationships": NETWORKS / "energy_system_edges.csv",
    "technology_capabilities": ANALYSIS / "technology_system_nodes.csv",
    "technology_interfaces": INTEGRATION / "technology_system_interfaces.csv",
    "technology_dependencies": INTEGRATION / "technology_dependencies.csv",
}

REQUIRED_COLUMNS = {
    "agriculture_hydrology_context": {"feature_id", "feature_name", "commodity_or_flow", "canon_status"},
    "hydrology_relationships": {"feature_id", "from_id", "to_id", "flow_type", "relationship_basis"},
    "nutrient_flux_relationships": {"edge_id", "material", "relationship_type", "quantity_status"},
    "nutrient_management_controls": {"control_id", "control_type", "control_name", "uncertainty"},
    "ecology_components": {"node_id", "name", "node_type", "habitat_class"},
    "ecology_relationships": {"edge_id", "from_id", "to_id", "ecological_function"},
    "ecology_indicators": {"indicator_id", "indicator_type", "metric", "notes"},
    "energy_assets": {"node_id", "name", "node_type", "fuel_or_technology", "capacity_basis"},
    "energy_relationships": {"edge_id", "from_node_id", "to_node_id", "relationship_type"},
    "technology_capabilities": {"technology_id", "technology_family", "technology_label", "adoption_boundary"},
    "technology_interfaces": {"interface_id", "technology_id", "target_system_id", "interface_type", "governance_interface"},
    "technology_dependencies": {"dependency_id", "technology_id", "dependency_class", "dependency_label", "limitation"},
}

# Visual Grammar v0.3 working palette. Exact colors are intentionally not frozen.
PAPER = "#F3EFE4"
PANEL = "#FBFAF5"
INK = "#263238"
MUTED = "#66727A"
RULE = "#B7B0A5"
E = "#355F7A"          # Evidence / Model
S = "#A87536"          # Scenario
K = "#776486"          # Sketch
C = "#4E756A"          # World Canon
WATER = "#3C6E8F"      # physical/material water flow
WATER_LIGHT = "#B9DDEB"
NUTRIENT = "#B36B3C"   # material / nutrient context
FIELD = "#D9C27A"
FIELD_ALT = "#C5B77C"
FIELD_EDGE = "#8A7A45"
PERENNIAL = "#718B61"
WETLAND = "#5B8C83"
WETLAND_LIGHT = "#B8D7CA"
ENERGY = "#D18E35"
SOLAR = "#D5A642"
MAINTENANCE = "#A94F3E"
DATA = "#806B8E"
HABITAT = "#466B50"
ROAD = "#B3A28C"

PANEL_STEMS = [
    "4_3a_farm_unit_2075",
    "4_3b_water_nutrient_management",
    "4_3c_farm_system_assembly",
    "4_3d_operating_logic",
]
CONTACT_SHEET = OUT_DIR / "4_3_contact_sheet.png"
MANIFEST = OUT_DIR / "4_3_source_manifest.json"
VALIDATION_REPORT = OUT_DIR / "4_3_validation_report.md"

ASSUMPTIONS = [
    {
        "id": "S-K-FARM-UNIT",
        "choice": "A synthetic farm unit at the Maumee River Commons / Black Swamp Country interface",
        "status": "S/K",
        "boundary": "Not a real parcel, site plan, or geographic claim",
    },
    {
        "id": "S-K-PRODUCTIVE-MOSAIC",
        "choice": "Annual fields remain the largest and visually dominant land-use blocks; perennial strips, habitat, and wetland cells are interleaved",
        "status": "S/K",
        "boundary": "Area is illustrative; no acreage, yield, or adoption rate is encoded",
    },
    {
        "id": "S-K-WATER-INTERFACES",
        "choice": "Controlled drainage, ditches, retention/wetland cells, storage, and supplemental reuse are connected as operating interfaces",
        "status": "S/K",
        "boundary": "Drainage and retention do not eliminate nutrient loss or downstream export",
    },
    {
        "id": "S-K-ENERGY-STACK",
        "choice": "Solar generation and storage supplement grid/fuel service for pumps, greenhouse, sensing, and repair work",
        "status": "S/K",
        "boundary": "Renewable generation is not energy independence",
    },
    {
        "id": "S-K-MAINTENANCE",
        "choice": "Repair building, staging yard, access lanes, pumps, gates, cabinets, and replaceable modules remain visible",
        "status": "S/K",
        "boundary": "Automation does not remove human work or service inputs",
    },
    {
        "id": "S-K-CONTROL",
        "choice": "Sensors feed records and human-supervised decisions; gates and pumps are interfaces, not autonomous authority",
        "status": "S/K",
        "boundary": "Monitoring is not control; sensing is not a successful response",
    },
]
