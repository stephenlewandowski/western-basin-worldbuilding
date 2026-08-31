"""Validate Phase 2B materials-flow data, maps, and GeoPackage integration."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image
import pyogrio


ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data" / "processed" / "networks"
GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
REPORT = ROOT / "reports" / "materials_phase2b_artifact_check.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    nodes = pd.read_csv(NETWORKS / "materials_system_nodes.csv", keep_default_na=False)
    edges = pd.read_csv(NETWORKS / "materials_system_edges.csv", keep_default_na=False)
    sources = pd.read_csv(NETWORKS / "materials_system_sources.csv", keep_default_na=False)

    required_nodes = {"node_id", "name", "material_system", "node_type", "supply_chain_role", "reality_status", "canon_status", "local_resource", "scenario_year", "source_id", "confidence", "notes"}
    required_edges = {"edge_id", "from_id", "to_id", "material", "flow_type", "relationship_basis", "reality_status", "canon_status", "confidence", "source_id", "relationship_date", "current_status", "notes"}
    required_sources = {"source_id", "title", "agency_or_publisher", "url_or_identifier", "retrieved_date", "publication_or_dataset_date", "spatial_resolution_or_scale", "license_or_terms", "confidence", "source_type", "notes"}
    require(required_nodes <= set(nodes), "node schema incomplete")
    require(required_edges <= set(edges), "edge schema incomplete")
    require(required_sources <= set(sources), "source schema incomplete")
    require(nodes.node_id.is_unique and edges.edge_id.is_unique and sources.source_id.is_unique, "IDs must be unique")
    require(set(edges.from_id) <= set(nodes.node_id) and set(edges.to_id) <= set(nodes.node_id), "orphan edge endpoint")
    require(set(nodes.source_id) <= set(sources.source_id) and set(edges.source_id) <= set(sources.source_id), "orphan source reference")
    require(not edges.duplicated(["from_id", "to_id", "material", "flow_type"]).any(), "unintended duplicate relationship")
    for field in ["relationship_basis", "reality_status", "canon_status", "confidence", "source_id"]:
        require(edges[field].astype(str).str.strip().ne("").all(), f"blank edge {field}")
    core_nodes = nodes[~nodes.node_id.str.startswith("EXP-")]
    core_edges = edges[~edges.edge_id.str.startswith("EXP-")]
    require(set(core_nodes.material_system) == {"carbonate", "beryllium", "shared"}, "Phase 2B material-system core changed")
    require(set(nodes.material_system) <= {"carbonate", "beryllium", "shared", "exposure"}, "unexpected material system")
    allowed_basis = {"observed", "documented_supply_relationship", "engineering_dependency", "scientific_inference", "supply_chain_inference", "historical_documentation", "regulatory_requirement"}
    require(set(edges.relationship_basis) <= allowed_basis, "unqualified relationship basis")
    require(set(core_nodes.reality_status) == {"real"} and set(core_edges.reality_status) == {"real"}, "Phase 2B core contains non-real records")
    require(set(nodes.reality_status) <= {"real", "historical"} and set(edges.reality_status) <= {"real", "historical"}, "unsupported reality status")
    require(set(nodes.canon_status) <= {"verified", "inferred"} and set(edges.canon_status) <= {"verified", "inferred"}, "scenario/experimental canon status entered baseline")
    require(set(core_nodes.scenario_year.astype(str)) == {"2026"}, "future scenario entered Phase 2B core")
    require(set(nodes.scenario_year.astype(str)) <= {"2026", "historical"}, "future scenario entered current materials graph")
    require(not any(c.lower() in {"quantity", "tonnage", "volume", "capacity"} for c in edges.columns), "shipment quantity field prohibited")

    elmore = nodes[nodes.node_id == "BER-PROC-ELMORE"].iloc[0]
    require(elmore.supply_chain_role == "advanced_processing", "Elmore must be advanced processing")
    require(str(elmore.local_resource).lower() == "false", "Elmore local extraction must be false")
    require("not a" in elmore.notes.lower() and "mine" in elmore.notes.lower(), "Elmore not-a-mine qualification absent")
    luckey = nodes[nodes.node_id == "BER-LEG-LUCKEY"].iloc[0]
    require(luckey.supply_chain_role == "legacy_cleanup", "Luckey must remain legacy cleanup")
    cfs = edges[edges.edge_id == "BER-E08"].iloc[0]
    require(cfs.relationship_basis == "documented_supply_relationship", "CFS relationship qualification wrong")
    require(cfs.relationship_date == "2025-10-31" and "beryllium fluoride" in cfs.material.lower(), "CFS date/material missing")
    kairos = edges[edges.edge_id == "BER-E09"].iloc[0]
    require("unresolved" in kairos.current_status.lower(), "Kairos current-status caveat missing")
    route_fields = {"route", "route_geometry", "transport_mode", "shipment_schedule", "origin_terminal", "destination_terminal"}
    require(not (route_fields & set(edges.columns)), "transport-route fields are prohibited")
    require(not edges.flow_type.str.contains("route|shipment", case=False, regex=True).any(), "flow type asserts a transport route")

    map_results = {}
    for number, stem in [(7, "07_carbonate_materials_system"), (8, "08_beryllium_strategic_supply_chain")]:
        png = ROOT / "outputs" / "maps" / "systems" / f"{stem}.png"
        svg = png.with_suffix(".svg")
        require(png.exists() and svg.exists(), f"Map {number:02d} formats missing")
        with Image.open(png) as image:
            require(image.width >= 2400 and image.height >= 1500, f"Map {number:02d} raster too small")
            map_results[f"map_{number:02d}"] = {"png_pixels": [image.width, image.height], "svg_parseable": True}
        ET.parse(svg)

    layers = set(pyogrio.list_layers(GPKG)[:, 0])
    required_layers = {"hydrography_physical", "geology_bedrock_units", "geology_carbonate_units", "industrial_mineral_sites", "strategic_material_sites", "legacy_remediation_sites", "materials_flow_nodes"}
    require(required_layers <= layers, f"GeoPackage missing layers: {sorted(required_layers - layers)}")
    spatial = pyogrio.read_dataframe(GPKG, layer="materials_flow_nodes")
    expected_spatial = nodes[(nodes.latitude != "") & (nodes.longitude != "")]
    require(len(spatial) == len(expected_spatial), "materials_flow_nodes count mismatch")
    require(set(spatial.node_id) == set(expected_spatial.node_id), "materials_flow_nodes IDs mismatch")
    prohibited = [p for p in ROOT.rglob("*") if p.is_file() and "materials_corridor" in p.name.lower() and p.suffix.lower() in {".gpkg", ".geojson", ".shp"}]
    require(not prohibited, f"prohibited corridor geometry found: {prohibited}")

    result = {
        "status": "pass",
        "phase": "Phase 2B - 2026 materials-flow baseline",
        "counts": {"nodes": len(nodes), "edges": len(edges), "sources": len(sources), "spatial_nodes": len(spatial)},
        "relationship_basis_counts": edges.relationship_basis.value_counts().sort_index().to_dict(),
        "map_checks": map_results,
        "gpkg_required_layers": sorted(required_layers),
        "constraints": {
            "elmore_not_local_extraction": True,
            "luckey_legacy_cleanup": True,
            "no_transport_routes": True,
            "no_shipment_quantities": True,
            "no_future_scenarios": True,
            "phase_2b_core_preserved_after_phase_2c_extension": True,
            "future_scenarios_separate_from_phase_2b_core": True,
            "no_materials_corridor_geometry": True,
        },
    }
    REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
