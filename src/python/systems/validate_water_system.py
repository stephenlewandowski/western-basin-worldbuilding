"""Post-build artifact validation for Water System v0.1."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image
import pyogrio


ROOT = Path(__file__).resolve().parents[3]
MAP_DIR = ROOT / "outputs" / "maps" / "systems"
REPORT = ROOT / "reports" / "water_system_artifact_check.json"


def main() -> None:
    stems = [
        "01_water_baseline_2026",
        "02_maumee_nutrient_network",
        "03_black_swamp_drainage_system",
        "04_lake_erie_hab_intake_dependency",
        "05_water_system_2050_scenario",
    ]
    checked: list[str] = []
    for stem in stems:
        png = MAP_DIR / f"{stem}.png"
        svg = MAP_DIR / f"{stem}.svg"
        assert png.stat().st_size > 10_000 and svg.stat().st_size > 10_000
        with Image.open(png) as image:
            image.verify()
        ET.parse(svg)
        checked.extend([str(png.relative_to(ROOT)), str(svg.relative_to(ROOT))])

    gpkg = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
    layers = set(pyogrio.list_layers(gpkg)[:, 0])
    required_layers = {
        "water_watersheds_huc8", "water_subwatersheds_huc12", "water_flowlines_order3",
        "water_huc12_routing_inferred", "water_lake_erie", "water_current_wetlands_25ac",
        "water_verified_facilities",
    }
    assert required_layers.issubset(layers)

    nodes = pd.read_csv(ROOT / "data" / "processed" / "networks" / "water_system_nodes.csv")
    edges = pd.read_csv(ROOT / "data" / "processed" / "networks" / "water_system_edges.csv")
    assert set(edges.from_id).issubset(set(nodes.feature_id))
    assert set(edges.to_id).issubset(set(nodes.feature_id))
    scenario = nodes[nodes.reality_status == "fictional"]
    assert scenario.longitude.isna().all() and scenario.latitude.isna().all()

    for path in [
        ROOT / "outputs" / "figures" / "water_system_network.png",
        ROOT / "outputs" / "figures" / "water_system_network.svg",
        ROOT / "outputs" / "figures" / "water_system_R_validation.png",
        ROOT / "reports" / "water_system_sources.md",
        ROOT / "reports" / "water_system_assumptions.md",
        ROOT / "reports" / "water_system_qa.md",
        ROOT / "reports" / "water_system_phase1_handoff.md",
    ]:
        assert path.exists() and path.stat().st_size > 0
        checked.append(str(path.relative_to(ROOT)))

    result = {
        "status": "passed",
        "map_pairs": len(stems),
        "gpkg_layers": sorted(layers),
        "nodes": len(nodes),
        "edges": len(edges),
        "checked_files": checked,
    }
    REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
