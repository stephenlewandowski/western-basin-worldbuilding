"""Shared constants for Phase 17A Prototype 2.1 \"From Field to Lake\".

Additive Phase-17 Atlas support; reads frozen Phase 1-16 inputs only and never
writes to them. This module is shared by the Python builder and validator so the
approved process/constituent vocabulary and source maps live in one place.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# ---- Project paths ---------------------------------------------------------
DATA = ROOT / "data" / "processed"
NETWORKS = DATA / "networks"
ANALYSIS = DATA / "analysis"
REPORTS = ROOT / "reports"
GPKG = DATA / "glasspunk_base.gpkg"
OUT_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "2_1_from_field_to_lake"

MANIFEST = OUT_DIR / "2_1_source_manifest.json"
CONSTITUENT_MATRIX = OUT_DIR / "2_1_constituent_process_matrix.csv"
VALIDATION_REPORT = OUT_DIR / "2_1_validation_report.md"

# Required implementation inputs (accepted/frozen).
REQUIRED_INPUTS = [
    NETWORKS / "biogeochemical_flux_edges.csv",
    NETWORKS / "biogeochemical_system_nodes.csv",
    NETWORKS / "biogeochemical_dependency_edges.csv",
    NETWORKS / "huc12_routing_current.csv",
    NETWORKS / "water_system_nodes.csv",
    NETWORKS / "water_system_edges.csv",
    GPKG,
    REPORTS / "physical_hydrography_source_manifest.json",
    REPORTS / "physical_hydrography_reconciliation.md",
    ROOT / "docs" / "canon_status.md",
    REPORTS / "toledo_water_intake_crib_coordinate_resolution.md",
]

# Optional scientific/editorial context.
OPTIONAL_INPUTS = [
    REPORTS / "water_system_phase1_handoff.md",
    REPORTS / "water_system_sources.md",
    ROOT / "docs" / "phase_briefs" / "phase8a_biogeochemical_nutrient_flux_baseline.md",
    ROOT / "docs" / "phase_briefs" / "phase8b_biogeochemical_dependencies_controls.md",
    ROOT / "metadata" / "atlas_layers.yml",
    ROOT / "metadata" / "atlas_systems.yml",
    ROOT / "metadata" / "atlas_evidence_vocabulary.yml",
    ROOT / "metadata" / "atlas_relationship_vocabulary.yml",
    ANALYSIS / "biogeochemical_quantitative_fluxes.csv",
]

# Accepted geographic layer names in the canonical GeoPackage.
LAYER_HYDRO_PHYSICAL = "hydrography_physical"
LAYER_HYDRO_CONNECTORS = "hydrography_network_connectors"
LAYER_ROUTING_UNRESOLVED = "routing_inferred_unresolved"
LAYER_HUC8 = "water_watersheds_huc8"
LAYER_HUC12 = "water_subwatersheds_huc12"
LAYER_LAKE = "water_lake_erie"

# CRS used for map rendering (consistent with existing system maps).
MAP_CRS = "EPSG:5070"
WATER_CRS = "EPSG:4326"

# Western / study-area focus window for the geographic map (lon_min, lat_min,
# lon_max, lat_max). Covers the Maumee HUC-8 basin plus adjacent western Lake
# Erie receiving-water edge. Bounds derive from the accepted huc8 layer.
FOCUS_WINDOW = (-85.45, 40.30, -82.60, 42.10)

# Physical waterway display subset: stream order threshold and simplification
# tolerance (degrees, EPSG:4326) applied only to render copies, not source.
RENDER_MIN_STREAMORDER = 4
RENDER_SIMPLIFY_TOL = 0.0006

# Accepted constituent vocabulary (source tokens that may be shown as tracks).
# water_carrier is the carrier/context track; HAB_context is excluded.
ACCEPTED_CONSTITUENTS = {
    "water_carrier",  # water as carrier / context
    "P",
    "N",
    "C",
    "organic_matter",
    "soil_carbon",
    "sediment",
}

# Constituent tracks used for the comparison figure. Each maps to accepted
# source tokens; water/context is a carrier track, not a nutrient load.
CONSTITUENT_TRACKS = [
    ("water / carrier", ("water_carrier",)),
    ("phosphorus (P)", ("P",)),
    ("nitrogen (N)", ("N",)),
    ("carbon / organic matter (C)", ("C", "organic_matter", "soil_carbon")),
    ("sediment", ("sediment",)),
]

# Atlas-facing process categories approved for Prototype 2.1, mapping from
# biogeochemical flux relationship types (verbatim source vocabulary). No
# standalone "release" category is introduced.
RELATIONSHIP_TO_PROCESS = {
    "mobilized_from": "mobilization",
    "mobilized_by": "mobilization",
    "transported_by": "transport",
    "retained_or_transformed_by": "retention / transformation",
    "transformed_by": "retention / transformation",
    "delivered_to": "delivery",
    "discharged_to": "discharge",
    "ecological_interface": "receiving-water response/context",
    "managed_by": None,  # program context; not a transport or process category
    "monitored_by": None,  # monitoring context; not a transport or process category
}

APPROVED_PROCESSES = [
    "mobilization",
    "transport",
    "retention / transformation",
    "delivery",
    "discharge",
    "receiving-water response/context",
]

# Verbatim source relationship types that signal a deterministic nutrient->HAB
# edge if they ever appear as a direct single-constituent-to-HAB arrow. In the
# accepted source tables no such deterministic pipe exists.
HAB_DIRECT_EDGE_RELATIONSHIP_TYPES = frozenset()