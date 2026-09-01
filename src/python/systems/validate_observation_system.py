"""Validate the Phase 4A observation-to-decision baseline and Map 14."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
REPORTS = ROOT / "reports"
MAPS = ROOT / "outputs/maps/systems"
NODES_PATH = NETWORKS / "observation_system_nodes.csv"
EDGES_PATH = NETWORKS / "observation_system_edges.csv"
MANIFEST_PATH = REPORTS / "observation_system_manifest.json"
CHECK_PATH = REPORTS / "observation_system_artifact_check.json"

NODE_COLUMNS = {
    "node_id", "name", "domain", "node_type", "status", "organization",
    "latitude", "longitude", "spatial_role", "source_id", "confidence", "notes",
}
EDGE_COLUMNS = {
    "edge_id", "from_id", "to_id", "relationship_type", "relationship_basis",
    "source_id", "confidence", "notes",
}
ALLOWED_NODE_TYPES = {
    "physical_system", "sensor_or_station", "observation_network", "data_product",
    "model_or_forecast", "decision_organization", "operational_response",
}
ALLOWED_DOMAINS = {"lake_erie_hab", "maumee_hydrology", "environmental_regulatory", "energy_information"}
ALLOWED_BASIS = {"observed", "documented", "qualified_documented", "inferred", "engineering_dependency"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}

# These hashes were captured from main before Phase 4A work began. They protect
# every existing Map 01-13b PNG/SVG pair from accidental regeneration.
PRIOR_MAP_HASHES = {
    "outputs/maps/systems/01_water_baseline_2026.png": "13041db7f9756c4030335cc67334551f1cdf007a7fbce75474da9022f1b5fbd5",
    "outputs/maps/systems/01_water_baseline_2026.svg": "b6faf587c12a1596ddc6914426cce78eb507360493a0329bc9ed6365601c3544",
    "outputs/maps/systems/02_maumee_nutrient_network.png": "0a851645fbb660e9ab532b92b7cc8a6312c047757d600e6cfd645cb4fa047996",
    "outputs/maps/systems/02_maumee_nutrient_network.svg": "4ef4c695ee64c3085035a6e13450ae7ef0806f395ae49fb2d4a872c22a36d101",
    "outputs/maps/systems/03_black_swamp_drainage_system.png": "54d70695fb27d155d4f68820074b633d3c5e161f09d78e510949dbc58155de2d",
    "outputs/maps/systems/03_black_swamp_drainage_system.svg": "f4e50f2a44579977b9c53afbf1c9c4cf0d641bd32251538c1a8ae83d2def3ee0",
    "outputs/maps/systems/04_lake_erie_hab_intake_dependency.png": "6f575b233c97adb60b9f6cbfb5ea22fe5d3f43365691b25e90bb871ba15fa81e",
    "outputs/maps/systems/04_lake_erie_hab_intake_dependency.svg": "5101556319f6c31402063a910b648c7fd4ff2569283274eba56027d43864ead9",
    "outputs/maps/systems/05_water_system_2050_scenario.png": "b20274f2a53ead80050c0d5d01e7b6e4742a28bc347b4f12cb683946b062522c",
    "outputs/maps/systems/05_water_system_2050_scenario.svg": "841fc58498fff151fd46a5d03f5eae0abbc8bbe917fc14fd822fd8d280e6a905",
    "outputs/maps/systems/06_geology_resources_2026.png": "a768668df8bd6a9860c6693677c668e623de6f878e47e146662763137ddfebd6",
    "outputs/maps/systems/06_geology_resources_2026.svg": "c5d48333553b7a0417c65d13de013cbabed1d6b6feb6375de02ef983ad0715d1",
    "outputs/maps/systems/07_carbonate_materials_system.png": "d20ce609e0ce416d7d65a071ed4032b92da3c4374cd8f1dd994c4b2d5b6a98e4",
    "outputs/maps/systems/07_carbonate_materials_system.svg": "29ada4ffee0ac370ecf814a3c897b5987c6adb67fe30227baad79c592163bc41",
    "outputs/maps/systems/08_beryllium_strategic_supply_chain.png": "ce1af11848b5e3a247ec5d60ad9b50747c4942fdc282105e7ef917a9ebf0edcc",
    "outputs/maps/systems/08_beryllium_strategic_supply_chain.svg": "3da298fe97aa0a0d8ae4a9db257d54acc9f5e52a2ca20ca74e6341f69a75302c",
    "outputs/maps/systems/09_luckey_elmore_materials_exposure_history.png": "23afcbfb0fe4625ee321bcf851d633a888bef4981b3d5b866b21a5ddc944662c",
    "outputs/maps/systems/09_luckey_elmore_materials_exposure_history.svg": "0ff46a750c5607e91378644490b5ab01505d283eef012d3d90d910a4f7e29d4c",
    "outputs/maps/systems/10_materials_system_2050.png": "06268dac1f05b4a2ea6ee832a2e9eb93ee933305610bfd19ff0ca4554c319ebf",
    "outputs/maps/systems/10_materials_system_2050.svg": "d7f322d333729bdbedcbf0f149dc0e5ff2c34b109c26c4b1609c491d2187c330",
    "outputs/maps/systems/10b_materials_system_2075.png": "2a9707e8845051776445687adb361cb002e4c2eb40a643b6f6e84a8c0f4d934c",
    "outputs/maps/systems/10b_materials_system_2075.svg": "2cf6088c3cb6c662bc15f19995841918748a76f11693bb3f7cc6527d363b8c2e",
    "outputs/maps/systems/11_energy_grid_compute_baseline_2026.png": "069a50ce2d469de1cc3370bbbbcc11ca1c4ea0315fea451222594ecb872173ef",
    "outputs/maps/systems/11_energy_grid_compute_baseline_2026.svg": "246028770058ac071796f10aee327e3bef7b4d7f1d9088494d8aa13a3b6a6481",
    "outputs/maps/systems/12_critical_energy_dependencies_2026.png": "df8959b1c6d81dc1be22bfaa5d7a6a1fac749325ee227f3e81244513629c58f1",
    "outputs/maps/systems/12_critical_energy_dependencies_2026.svg": "ddd1f71de08dd29531e021b5a39118c408d2b7ee669248bba7c5d99e1a26c684",
    "outputs/maps/systems/13_energy_grid_compute_futures_2050.png": "968b37dfb28aa81124cd0c98fa2d7bbcce598405c37dc77087b21c40351564bd",
    "outputs/maps/systems/13_energy_grid_compute_futures_2050.svg": "aad3028b16e6c21634e3571f945eec90ce98a154979251e721d78aec23d8048d",
    "outputs/maps/systems/13b_energy_grid_compute_futures_2075.png": "96b4d754160482d51198cc19d991b8f9a485383ea1d614ebb8701a292be3edc9",
    "outputs/maps/systems/13b_energy_grid_compute_futures_2075.svg": "7c7ee09de55f8c114cad95cb3b859b9c2fee6f9482d1448b4d0a48483e11a386",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    nodes = pd.read_csv(NODES_PATH, dtype=str).fillna("")
    edges = pd.read_csv(EDGES_PATH, dtype=str).fillna("")
    sources = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]
    source_ids = set(sources)

    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert len(nodes) == 25
    assert len(edges) == 21
    assert nodes.node_id.is_unique and edges.edge_id.is_unique
    assert set(nodes.node_type) <= ALLOWED_NODE_TYPES
    assert set(nodes.domain) == ALLOWED_DOMAINS
    assert set(nodes.confidence) <= ALLOWED_CONFIDENCE
    assert set(edges.relationship_basis) <= ALLOWED_BASIS
    assert set(edges.confidence) <= ALLOWED_CONFIDENCE
    assert nodes.source_id.str.len().gt(0).all()
    assert edges.source_id.str.len().gt(0).all()
    assert set(nodes.source_id) <= source_ids
    assert set(edges.source_id) <= source_ids
    assert set(edges.from_id) <= set(nodes.node_id)
    assert set(edges.to_id) <= set(nodes.node_id)
    assert nodes.status.str.contains(r"2050|2075|scenario|fictional", case=False, regex=True).sum() == 0
    assert nodes.name.str.contains(r"cyber|SCADA|AGI|surveillance", case=False, regex=True).sum() == 0
    assert edges.relationship_type.str.lower().str.contains("trigger|automated|control").sum() == 0

    coordinate_rows = nodes[(nodes.latitude != "") | (nodes.longitude != "")]
    assert len(coordinate_rows) == 2
    assert set(coordinate_rows.node_type) == {"sensor_or_station"}
    for _, row in coordinate_rows.iterrows():
        latitude = float(row.latitude)
        longitude = float(row.longitude)
        assert -90 <= latitude <= 90 and -180 <= longitude <= 180
    glos = nodes.loc[nodes.node_id == "OBS-SNS-GLOS-TOLEDO-CRIB"].iloc[0]
    assert glos.latitude == "41.67496" and glos.longitude == "-83.3079"
    assert "not" in glos.notes.lower() and "intake" in glos.notes.lower()
    usgs = nodes.loc[nodes.node_id == "OBS-SNS-USGS-04193500"].iloc[0]
    assert usgs.latitude == "41.5000526" and usgs.longitude == "-83.7127145"

    required_nodes = {
        "OBS-PHY-LAKE-ERIE-WESTERN", "OBS-MOD-NOAA-HAB-FORECAST", "OBS-ORG-CITY-TOLEDO-WATER",
        "OBS-PHY-MAUMEE-LOWER", "OBS-MOD-NOAA-NWPS", "OBS-ORG-NWS",
        "OBS-PHY-REGULATED-FACILITY", "OBS-DAT-EPA-ECHO", "OBS-ORG-NPDES-PROGRAM",
        "OBS-PHY-REGIONAL-GRID", "OBS-DAT-PJM-DATAMINER", "OBS-ORG-PJM",
    }
    assert required_nodes <= set(nodes.node_id)
    assert set(edges.relationship_type) >= {"observes", "publishes", "feeds", "supports_decision", "used_by", "operates", "reports_to"}

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["phase"] == "4A"
    assert manifest["counts"]["nodes"] == len(nodes)
    assert manifest["counts"]["edges"] == len(edges)
    for relative, expected in manifest["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and path.stat().st_size > 0, relative
        assert sha256(path) == expected["sha256"], relative

    map_png = MAPS / "14_observation_decision_system_2026.png"
    map_svg = MAPS / "14_observation_decision_system_2026.svg"
    with Image.open(map_png) as image:
        image.verify()
        map_size = image.size
    ET.parse(map_svg)

    for relative, expected in PRIOR_MAP_HASHES.items():
        path = ROOT / relative
        assert path.exists(), relative
        assert sha256(path) == expected, f"Prior map changed: {relative}"

    result = {
        "status": "passed",
        "phase": "4A",
        "nodes": len(nodes),
        "edges": len(edges),
        "domains": sorted(nodes.domain.unique().tolist()),
        "geolocated_observation_nodes": len(coordinate_rows),
        "map14_png_dimensions": list(map_size),
        "map14_artifacts_valid": True,
        "prior_maps_01_13b_unchanged": True,
        "provenance_complete": True,
        "automated_control_asserted": False,
        "future_scenario_content": False,
        "checked_prior_map_files": len(PRIOR_MAP_HASHES),
    }
    CHECK_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
