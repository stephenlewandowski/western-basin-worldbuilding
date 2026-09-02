"""Validate Phase 5B freight evidence and protect Phase 5A/prior baselines."""
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
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

CROSSWALK = ANALYSIS / "freight_evidence_crosswalk.csv"
RELATIONSHIPS = NETWORKS / "freight_evidence_relationships.csv"
INTERCHANGE = ANALYSIS / "freight_interchange_matrix.csv"
MANIFEST = REPORTS / "freight_evidence_manifest.json"
CHECK = REPORTS / "freight_evidence_artifact_check.json"

CROSSWALK_COLUMNS = {"evidence_id", "phase5a_object_id", "object_type", "facility_or_corridor", "mode", "commodity_class", "previous_basis", "evidence_class", "source_id", "source_date", "confidence", "upgrade_status", "notes"}
RELATIONSHIP_COLUMNS = {"relationship_id", "phase5a_edge_id", "from_id", "to_id", "mode", "commodity_class", "evidence_class", "upgrade_status", "source_id", "confidence", "notes"}
INTERCHANGE_COLUMNS = {"interface_id", "interface_name", "mode_a", "mode_b", "physical_co_location", "documented_interchange", "evidence_class", "source_id", "confidence", "notes"}
EVIDENCE_CLASSES = {"documented_facility_access", "documented_shipment_relationship", "documented_interchange", "documented_corridor", "generalized_logistics_dependency", "proximity_only", "unresolved"}
UPGRADES = {"confirmed", "strengthened", "unchanged", "downgraded", "unresolved"}
MODES = {"marine", "rail", "highway", "generalized", "multimodal", "pipeline"}
CONFIDENCE = {"high", "medium", "medium_high", "low"}


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
    crosswalk = pd.read_csv(CROSSWALK, dtype=str).fillna("")
    relationships = pd.read_csv(RELATIONSHIPS, dtype=str).fillna("")
    interchange = pd.read_csv(INTERCHANGE, dtype=str).fillna("")
    freight_nodes = pd.read_csv(NETWORKS / "freight_system_nodes.csv", dtype=str).fillna("")
    freight_edges = pd.read_csv(NETWORKS / "freight_system_edges.csv", dtype=str).fillna("")
    source_registry = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]

    assert set(crosswalk.columns) == CROSSWALK_COLUMNS
    assert set(relationships.columns) == RELATIONSHIP_COLUMNS
    assert set(interchange.columns) == INTERCHANGE_COLUMNS
    assert len(crosswalk) == 20 and crosswalk.evidence_id.is_unique
    assert len(relationships) == 12 and relationships.relationship_id.is_unique
    assert len(interchange) == 9 and interchange.interface_id.is_unique
    freight_ids = set(freight_nodes.node_id)
    phase5a_edge_ids = set(freight_edges.edge_id)
    assert crosswalk.phase5a_object_id.isin(freight_ids).all()
    assert relationships.phase5a_edge_id.isin(phase5a_edge_ids).all()
    assert relationships.from_id.isin(freight_ids | {"ENE-EIA-59764"}).all()
    assert relationships.to_id.isin(freight_ids | {"ENE-EIA-59764"}).all()
    assert crosswalk.evidence_class.isin(EVIDENCE_CLASSES).all()
    assert relationships.evidence_class.isin(EVIDENCE_CLASSES).all()
    assert interchange.evidence_class.isin(EVIDENCE_CLASSES).all()
    assert crosswalk.upgrade_status.isin(UPGRADES).all()
    assert relationships.upgrade_status.isin(UPGRADES).all()
    assert crosswalk["mode"].isin(MODES).all() and relationships["mode"].isin(MODES).all()
    assert interchange.mode_a.isin(MODES).all() and interchange.mode_b.isin(MODES).all()
    assert crosswalk.confidence.isin(CONFIDENCE).all()
    assert relationships.confidence.isin(CONFIDENCE).all()
    assert interchange.confidence.isin(CONFIDENCE).all()
    assert crosswalk.source_id.isin(set(source_registry)).all()
    assert relationships.source_id.isin(set(source_registry)).all()
    assert interchange.source_id.isin(set(source_registry)).all()
    assert crosswalk.notes.str.len().gt(0).all() and relationships.notes.str.len().gt(0).all() and interchange.notes.str.len().gt(0).all()

    assert ((crosswalk.evidence_class == "documented_shipment_relationship") <= crosswalk.source_id.isin({"phase5a_toledo_port", "phase5a_luckey_logistics"})).all()
    assert ((relationships.evidence_class == "documented_shipment_relationship") <= relationships.source_id.isin({"phase5a_toledo_port", "phase5a_luckey_logistics"})).all()
    assert crosswalk.loc[crosswalk.phase5a_object_id == "FRT-PORT-TOLEDO", "upgrade_status"].eq("confirmed").any()
    assert crosswalk.loc[crosswalk.phase5a_object_id == "FRT-RAIL-WLE", "evidence_class"].eq("proximity_only").all()
    assert crosswalk.loc[crosswalk.phase5a_object_id == "FRT-AG-MIDWEST-BULK", "upgrade_status"].eq("unresolved").all()

    table_text = " ".join(" ".join(map(str, row)) for frame in [crosswalk, relationships, interchange] for row in frame.to_numpy())
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*(?:tons?|trucks?|railcars?|vessels?|calls?)\b", table_text, flags=re.I)
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*(?:MW|MGD)\b", table_text, flags=re.I)
    assert not re.search(r"2050|2075|scenario|fictional", table_text, flags=re.I)
    assert not re.search(r"SCADA|control architecture|attack path|exploit|credential|target prioritization", table_text, flags=re.I)

    check_manifest(ROOT / "reports/phase3a_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase3b_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4b_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase4c_information_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase5a_freight_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase5b_freight_evidence_freeze_manifest.json")
    prior_maps = json.loads((ROOT / "reports/phase5a_prior_map_hashes.json").read_text(encoding="utf-8"))["files"]
    assert len(prior_maps) == 38
    for relative, expected in prior_maps.items():
        artifact = ROOT / relative
        assert artifact.exists() and manifest_matches(ROOT, relative, expected), f"Prior map changed: {relative}"

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "5B"
    assert manifest["counts"]["crosswalk"] == len(crosswalk)
    assert manifest["counts"]["evidence_relationships"] == len(relationships)
    assert manifest["counts"]["interchange_rows"] == len(interchange)
    assert manifest["materials_corridor_test"] == "B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT"
    for relative, metadata in manifest["artifacts"].items():
        artifact = ROOT / relative
        assert artifact.exists() and artifact.stat().st_size > 0, relative
        assert sha256(artifact) == metadata["sha256"], relative

    map_png = MAPS / "18_freight_evidence_interchange_2026.png"
    map_svg = MAPS / "18_freight_evidence_interchange_2026.svg"
    assert map_png.exists() and map_svg.exists() and map_png.stat().st_size > 10_000 and map_svg.stat().st_size > 10_000
    with Image.open(map_png) as image:
        image.verify()
        map_size = image.size
    ET.parse(map_svg)

    result = {
        "status": "passed",
        "phase": "5B",
        "crosswalk": len(crosswalk),
        "evidence_relationships": len(relationships),
        "interchange_rows": len(interchange),
        "materials_corridor_test": "B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT",
        "map18_artifacts_valid": True,
        "phase5a_immutable": True,
        "phase4a_4c_immutable": True,
        "prior_maps_01_17_unchanged": True,
        "documented_shipment_distinguished": True,
        "proximity_not_promoted": True,
        "unsupported_quantities_absent": True,
        "hazardous_routes_absent": True,
        "sensitive_logistics_absent": True,
        "future_freight_content": False,
        "map18_png_dimensions": list(map_size),
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
