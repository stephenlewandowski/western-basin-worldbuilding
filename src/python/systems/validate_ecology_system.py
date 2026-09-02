"""Validate the bounded factual Phase 6A ecology baseline."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
NODES = NETWORKS / "ecology_system_nodes.csv"
EDGES = NETWORKS / "ecology_system_edges.csv"
INDICATORS = ANALYSIS / "ecological_indicators_2026.csv"
MAP_PNG = MAPS / "20_ecological_system_2026.png"
MAP_SVG = MAPS / "20_ecological_system_2026.svg"
MANIFEST = REPORTS / "ecology_system_manifest.json"
CHECK = REPORTS / "ecology_system_artifact_check.json"

NODE_COLUMNS = {"node_id", "name", "ecological_component", "node_type", "habitat_class", "taxonomic_relevance", "status", "latitude", "longitude", "spatial_role", "source_id", "confidence", "notes"}
EDGE_COLUMNS = {"edge_id", "from_id", "to_id", "relationship_type", "ecological_function", "relationship_basis", "source_id", "confidence", "notes"}
INDICATOR_COLUMNS = {"indicator_id", "ecological_system", "taxonomic_group", "indicator_type", "metric", "value", "units", "year_or_period", "spatial_scope", "source_id", "confidence", "notes"}
QUALITATIVE = {"high", "moderate", "low", "unknown"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for relative, metadata in manifest.get("artifacts", manifest.get("files", {})).items():
        artifact = ROOT / relative
        assert artifact.exists(), relative
        assert manifest_matches(ROOT, relative, metadata["sha256"]), relative


def main() -> None:
    nodes = pd.read_csv(NODES, dtype=str).fillna("")
    edges = pd.read_csv(EDGES, dtype=str).fillna("")
    indicators = pd.read_csv(INDICATORS, dtype=str).fillna("")
    import yaml
    source_registry = set(yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"])
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert set(indicators.columns) == INDICATOR_COLUMNS
    assert len(nodes) == 16 and nodes.node_id.is_unique
    assert len(edges) == 20 and edges.edge_id.is_unique
    assert len(indicators) == 3 and indicators.indicator_id.is_unique
    assert nodes.source_id.isin(source_registry).all()
    assert edges.source_id.isin(source_registry).all()
    assert indicators.source_id.isin(source_registry).all()
    assert nodes.status.eq("real_2026").all()
    assert set(nodes.ecological_component) == {"western_lake_erie_aquatic", "maumee_tributary_floodplain", "coastal_wetlands_marshes", "black_swamp_legacy_agriculture", "terrestrial_habitat_fragmentation", "migratory_mobile_species"}
    assert set(edges.from_id) <= set(nodes.node_id) and set(edges.to_id) <= set(nodes.node_id)
    assert nodes.confidence.isin(QUALITATIVE).all() and edges.confidence.isin(QUALITATIVE).all() and indicators.confidence.isin(QUALITATIVE).all()
    assert indicators.value.str.len().gt(0).all() and indicators.notes.str.len().gt(0).all()
    assert indicators.loc[indicators.indicator_id == "ECOI-001", "value"].iloc[0] == "608"
    assert indicators.loc[indicators.indicator_id == "ECOI-002", "value"].iloc[0] == "864"
    assert indicators.loc[indicators.indicator_id == "ECOI-003", "value"].iloc[0] == "7"
    assert "ECO-009" in set(nodes.node_id)
    swamp = nodes.loc[nodes.node_id == "ECO-009"].iloc[0]
    assert "noncanonical" in swamp.notes.lower() and swamp.latitude == "" and swamp.longitude == ""
    assert not set(nodes.latitude[nodes.latitude != ""]) & {""}
    forbidden = " ".join(" ".join(map(str, row)) for frame in [nodes, edges, indicators] for row in frame.to_numpy())
    assert not re.search(r"exact (?:flight|migration|animal) route|nest|roost|den|abundance estimate|species richness estimate|vulnerability score|risk score|population dynamics|2050|2075|scenario", forbidden, re.I)
    assert not re.search(r"(?:endangered|threatened).*(?:latitude|longitude|coordinate)|latitude.*(?:endangered|threatened)", forbidden, re.I)
    assert not any(nodes.node_id.str.startswith("GREAT-BLACK-SWAMP"))
    check_manifest(ROOT / "reports/phase3a_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase3b_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4b_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4c_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase5a_freight_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase5b_freight_evidence_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase5c_freight_dependency_freeze_manifest.json")
    prior_maps = json.loads((ROOT / "reports/phase5a_prior_map_hashes.json").read_text(encoding="utf-8"))["files"]
    assert len(prior_maps) == 38
    for relative, expected in prior_maps.items():
        assert manifest_matches(ROOT, relative, expected), relative
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "6A"
    assert manifest["counts"] == {"nodes": 16, "edges": 20, "indicators": 3}
    for relative, metadata in manifest["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and path.stat().st_size > 100, relative
        assert sha256(path) == metadata["sha256"], relative
    with Image.open(MAP_PNG) as image:
        image.verify()
        image_size = list(image.size)
    ET.parse(MAP_SVG)
    svg_text = " ".join("".join(element.itertext()) for element in ET.parse(MAP_SVG).getroot().iter() if element.tag.endswith("text"))
    for required in ["MAP 20", "Western Lake Erie", "Maumee River", "Ottawa NWR", "Great Black Swamp", "No sensitive species"]:
        assert required.lower() in svg_text.lower(), required
    result = {"status": "passed", "phase": "6A", "nodes": len(nodes), "edges": len(edges), "indicators": len(indicators), "map20_valid": True, "phase5c_frozen": True, "prior_maps_01_19_unchanged": True, "great_black_swamp_hold_preserved": True, "sensitive_locations_absent": True, "invented_biodiversity_values_absent": True, "exact_migration_routes_absent": True, "ecological_risk_scoring_absent": True, "future_ecology_absent": True, "image_size": image_size}
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
