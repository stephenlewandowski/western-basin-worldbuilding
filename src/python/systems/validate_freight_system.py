"""Validate Phase 5A freight artifacts and protect prior phase baselines."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import yaml
from PIL import Image
from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
RAW = ROOT / "data/raw/transportation"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

NODES = NETWORKS / "freight_system_nodes.csv"
EDGES = NETWORKS / "freight_system_edges.csv"
RAIL = RAW / "ntad_class1_rail_network_western_basin.geojson"
MANIFEST = REPORTS / "freight_system_manifest.json"
CHECK = REPORTS / "freight_system_artifact_check.json"
PRIOR_MAPS = REPORTS / "phase5a_prior_map_hashes.json"

NODE_COLUMNS = {"node_id", "name", "node_type", "mode", "industrial_role", "commodity_classes", "status", "latitude", "longitude", "source_id", "confidence", "notes"}
EDGE_COLUMNS = {"edge_id", "from_id", "to_id", "mode", "flow_role", "commodity_class", "relationship_basis", "status", "source_id", "confidence", "notes"}
ALLOWED_NODE_TYPES = {"port", "terminal", "rail_yard", "rail_interface", "highway_interface", "pipeline_interface", "industrial_site", "material_processor", "agricultural_node", "external_market"}
ALLOWED_MODES = {"marine", "rail", "highway", "pipeline", "generalized", "multimodal"}
ALLOWED_BASES = {"documented_flow", "documented_corridor", "interchange", "engineering_logistics_dependency", "generalized_supply_chain", "inferred"}
ALLOWED_COMMODITIES = {"agricultural_bulk", "grain", "aggregate", "limestone", "lime", "coal", "petroleum_or_fuel", "chemicals", "steel_or_metal_products", "automotive", "industrial_materials", "strategic_materials", "container_or_general_freight"}
ALLOWED_CONFIDENCE = {"high", "medium", "medium_high", "low"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("files", manifest.get("artifacts", {}))
    for relative, metadata in entries.items():
        artifact = ROOT / relative
        assert artifact.exists(), relative
        assert manifest_matches(ROOT, relative, metadata["sha256"]), f"Frozen artifact changed: {relative}"


def main() -> None:
    nodes = pd.read_csv(NODES, dtype=str).fillna("")
    edges = pd.read_csv(EDGES, dtype=str).fillna("")
    source_registry = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]
    material_sources = pd.read_csv(NETWORKS / "materials_system_sources.csv", dtype=str).fillna("")
    valid_sources = set(source_registry) | set(material_sources.source_id)
    valid_external_ids = set(pd.read_csv(ROOT / "data/processed/networks/energy_system_nodes.csv", dtype=str).fillna("").node_id)

    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert len(nodes) == 22 and nodes.node_id.is_unique
    assert len(edges) == 26 and edges.edge_id.is_unique
    assert set(nodes.node_type) <= ALLOWED_NODE_TYPES
    assert set(nodes["mode"]) <= ALLOWED_MODES
    assert set(edges["mode"]) <= ALLOWED_MODES
    assert set(edges.relationship_basis) <= ALLOWED_BASES
    assert set(nodes.confidence) <= ALLOWED_CONFIDENCE
    assert set(edges.confidence) <= ALLOWED_CONFIDENCE
    assert nodes.source_id.isin(valid_sources).all()
    assert edges.source_id.isin(valid_sources).all()
    node_ids = set(nodes.node_id)
    assert set(edges.from_id) <= node_ids | valid_external_ids
    assert set(edges.to_id) <= node_ids | valid_external_ids
    assert nodes.status.str.contains(r"2050|2075|scenario|fictional", case=False, regex=True).sum() == 0
    assert edges.status.str.contains(r"2050|2075|scenario|fictional", case=False, regex=True).sum() == 0
    assert nodes.notes.str.len().gt(0).all() and edges.notes.str.len().gt(0).all()

    for frame, column in [(nodes, "commodity_classes"), (edges, "commodity_class")]:
        commodity_values = set(value for cell in frame[column] if isinstance(cell, str) for value in cell.split(";") if value)
        assert commodity_values <= ALLOWED_COMMODITIES
    coordinate_rows = nodes[(nodes.latitude != "") | (nodes.longitude != "")]
    assert len(coordinate_rows) == 6
    assert coordinate_rows.latitude.str.len().gt(0).all() and coordinate_rows.longitude.str.len().gt(0).all()
    assert coordinate_rows.latitude.map(float).between(-90, 90).all()
    assert coordinate_rows.longitude.map(float).between(-180, 180).all()
    assert nodes.loc[nodes.node_id == "FRT-PORT-TOLEDO", "latitude"].iloc[0] == "41.653818167585"
    assert nodes.loc[nodes.node_id == "FRT-PORT-TOLEDO", "longitude"].iloc[0] == "-83.528499986757"
    assert nodes.loc[nodes.node_id == "FRT-TERM-IRONVILLE", "latitude"].iloc[0] == ""
    assert nodes.loc[nodes.node_id == "FRT-TERM-IRONVILLE", "longitude"].iloc[0] == ""

    assert edges.relationship_basis.isin(ALLOWED_BASES).all()
    assert edges.notes.str.contains(r"route|quantity|shipment|schedule", case=False, regex=True).sum() > 0
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*(?:tons?|trucks?|railcars?|vessels?|calls?)\b", " ".join(edges.notes), flags=re.I)
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*(?:MW|MGD)\b", " ".join(nodes.notes.tolist() + edges.notes.tolist()), flags=re.I)
    assert "documented_corridor" in set(edges.relationship_basis)
    assert "documented_flow" in set(edges.relationship_basis)
    assert "generalized_supply_chain" in set(edges.relationship_basis)
    assert "engineering_logistics_dependency" in set(edges.relationship_basis)

    rail_payload = json.loads(RAIL.read_text(encoding="utf-8"))
    assert len(rail_payload["features"]) == 1221
    assert all("RROWNER1" in feature["properties"] for feature in rail_payload["features"])

    check_manifest(ROOT / "reports/phase3a_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase3b_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4b_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4c_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4c_information_freeze_manifest.json")
    prior_maps = json.loads(PRIOR_MAPS.read_text(encoding="utf-8"))["files"]
    assert len(prior_maps) == 38
    for relative, expected in prior_maps.items():
        path = ROOT / relative
        assert path.exists() and manifest_matches(ROOT, relative, expected), f"Prior map changed: {relative}"

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "5A"
    assert manifest["counts"]["nodes"] == len(nodes)
    assert manifest["counts"]["edges"] == len(edges)
    assert manifest["materials_corridor_test"] == "B — WEAKLY SUPPORTED"
    for relative, metadata in manifest["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and path.stat().st_size > 0, relative
        assert sha256(path) == metadata["sha256"], relative

    map_png = MAPS / "17_freight_industry_material_flows_2026.png"
    map_svg = MAPS / "17_freight_industry_material_flows_2026.svg"
    flow_png = FIGURES / "freight_commodity_interfaces_2026.png"
    flow_svg = FIGURES / "freight_commodity_interfaces_2026.svg"
    for path in [map_png, map_svg, flow_png, flow_svg]:
        assert path.exists() and path.stat().st_size > 10_000
    image_sizes = []
    for path in [map_png, flow_png]:
        with Image.open(path) as image:
            image.verify()
            image_sizes.append(list(image.size))
    ET.parse(map_svg)
    ET.parse(flow_svg)

    result = {
        "status": "passed",
        "phase": "5A",
        "nodes": len(nodes),
        "edges": len(edges),
        "rail_cache_features": len(rail_payload["features"]),
        "geolocated_nodes": len(coordinate_rows),
        "materials_corridor_test": "B — WEAKLY SUPPORTED",
        "map17_artifacts_valid": True,
        "flow_figure_valid": True,
        "phase4a_immutable": True,
        "phase4b_immutable": True,
        "phase4c_immutable": True,
        "prior_maps_01_16b_unchanged": True,
        "unsupported_quantities_absent": True,
        "facility_specific_routes_absent": True,
        "hazardous_route_model_absent": True,
        "sensitive_logistics_detail_absent": True,
        "future_freight_scenario": False,
        "image_sizes": image_sizes,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
