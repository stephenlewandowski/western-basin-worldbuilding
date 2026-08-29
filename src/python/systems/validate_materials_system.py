"""Validate Phase 2A materials layers, Map 06, and Phase 1 preservation."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image
import pyogrio


ROOT = Path(__file__).resolve().parents[3]
GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
REPORT = ROOT / "reports" / "materials_system_artifact_check.json"

REQUIRED_MATERIALS_LAYERS = {
    "geology_carbonate_units",
    "industrial_mineral_sites",
    "strategic_material_sites",
    "legacy_remediation_sites",
}
REQUIRED_WATER_LAYERS = {
    "water_watersheds_huc8": 7,
    "water_subwatersheds_huc12": 252,
    "water_flowlines_order3": 864,
    "water_huc12_routing_inferred": 251,
    "water_lake_erie": 10,
    "water_current_wetlands_25ac": 608,
    "water_verified_facilities": 2,
}
COMMON_FIELDS = {
    "resource_class",
    "supply_chain_role",
    "local_resource",
    "reality_status",
    "canon_status",
    "source_name",
    "source_url_or_identifier",
    "retrieved_date",
    "confidence",
    "notes",
}
ALLOWED_ROLES = {
    "geologic_occurrence",
    "extraction",
    "primary_processing",
    "advanced_processing",
    "fabrication",
    "logistics",
    "end_use",
    "legacy_cleanup",
}


def assert_frame(name: str):
    frame = pyogrio.read_dataframe(GPKG, layer=name)
    assert not frame.empty, f"{name} is empty"
    assert COMMON_FIELDS.issubset(frame.columns), f"{name} missing common fields"
    assert frame.crs is not None and frame.crs.to_epsg() == 4326, f"{name} CRS is not EPSG:4326"
    assert frame.geometry.notna().all() and (~frame.geometry.is_empty).all(), f"{name} has empty geometry"
    assert frame.geometry.is_valid.all(), f"{name} has invalid geometry"
    assert frame[list(COMMON_FIELDS)].notna().all().all(), f"{name} has null required values"
    assert set(frame.supply_chain_role).issubset(ALLOWED_ROLES)
    assert set(frame.reality_status) == {"real"}
    assert set(frame.canon_status) == {"verified"}
    return frame


def main() -> None:
    available = set(pyogrio.list_layers(GPKG)[:, 0])
    assert REQUIRED_MATERIALS_LAYERS.issubset(available)
    assert set(REQUIRED_WATER_LAYERS).issubset(available)

    phase1_counts = {}
    for name, expected in REQUIRED_WATER_LAYERS.items():
        count = len(pyogrio.read_dataframe(GPKG, layer=name, read_geometry=False))
        assert count == expected, f"Phase 1 regression in {name}: {count} != {expected}"
        phase1_counts[name] = count

    carbonate = assert_frame("geology_carbonate_units")
    industrial = assert_frame("industrial_mineral_sites")
    strategic = assert_frame("strategic_material_sites")
    legacy = assert_frame("legacy_remediation_sites")

    assert set(carbonate.supply_chain_role) == {"geologic_occurrence"}
    assert carbonate.local_resource.astype(bool).all()
    assert len(industrial) >= 2
    assert industrial.local_resource.astype(bool).all()
    assert {"Woodville", "Genoa"}.issubset(set(" ".join(industrial.feature_name).split()))

    elmore = strategic[strategic.feature_name.str.contains("Elmore", case=False)]
    assert len(elmore) == 1
    assert elmore.iloc[0].supply_chain_role == "advanced_processing"
    assert not bool(elmore.iloc[0].local_resource)
    assert "not a beryllium mine" in elmore.iloc[0].notes.lower()

    luckey = legacy[legacy.feature_name.str.contains("Luckey", case=False)]
    assert len(luckey) == 1
    assert luckey.iloc[0].supply_chain_role == "legacy_cleanup"
    assert "not active strategic-material production" in luckey.iloc[0].notes.lower()

    all_sites = pd.concat([industrial, strategic, legacy], ignore_index=True)
    assert all_sites.geometry.x.between(-83.95, -82.72).all()
    assert all_sites.geometry.y.between(41.12, 41.82).all()
    forbidden_columns = {"capacity", "capacity_units", "groundwater_flow_direction", "reserve_quantity", "production_quantity"}
    assert forbidden_columns.isdisjoint(all_sites.columns)

    png = ROOT / "outputs" / "maps" / "systems" / "06_geology_resources_2026.png"
    svg = ROOT / "outputs" / "maps" / "systems" / "06_geology_resources_2026.svg"
    assert png.stat().st_size > 50_000 and svg.stat().st_size > 50_000
    with Image.open(png) as image:
        image.verify()
    ET.parse(svg)

    site_csv = ROOT / "outputs" / "tables" / "materials_sites_render_data.csv"
    polygon_csv = ROOT / "outputs" / "tables" / "materials_carbonate_render_data.csv"
    assert len(pd.read_csv(site_csv)) == len(all_sites)
    assert len(pd.read_csv(polygon_csv)) > 100
    for path in [
        ROOT / "reports" / "materials_system_sources.md",
        ROOT / "reports" / "materials_system_qa.md",
        ROOT / "outputs" / "figures" / "materials_system_R_validation.png",
    ]:
        assert path.exists() and path.stat().st_size > 0, f"Missing {path}"

    result = {
        "status": "passed",
        "phase1_layer_counts_preserved": phase1_counts,
        "materials_layer_counts": {
            "geology_carbonate_units": len(carbonate),
            "industrial_mineral_sites": len(industrial),
            "strategic_material_sites": len(strategic),
            "legacy_remediation_sites": len(legacy),
        },
        "classification_gates": {
            "woodville_and_genoa_local_carbonate": "passed",
            "elmore_advanced_processing_not_mine": "passed",
            "luckey_legacy_cleanup_not_production": "passed",
            "unsupported_quantities_absent": "passed",
            "groundwater_flow_claim_absent": "passed",
        },
        "map_pair": [str(png.relative_to(ROOT)), str(svg.relative_to(ROOT))],
    }
    REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
