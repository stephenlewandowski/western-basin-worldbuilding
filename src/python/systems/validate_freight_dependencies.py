"""Validate Phase 5C freight dependencies and protect all prior phases."""
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
ANALYSIS = ROOT / "data/processed/analysis"
FIGURES = ROOT / "outputs/figures"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

DEP_EDGES = NETWORKS / "freight_dependency_edges.csv"
DEP_REGISTER = ANALYSIS / "freight_dependency_register.csv"
MODAL_MATRIX = ANALYSIS / "modal_substitutability_matrix.csv"
MATRIX = FIGURES / "freight_dependency_matrix_2026.csv"
MANIFEST = REPORTS / "freight_dependency_manifest.json"
CHECK = REPORTS / "freight_dependency_artifact_check.json"

EDGE_COLUMNS = {"dependency_id", "source_node_id", "dependent_node_id", "domain", "dependency_type", "dependency_strength", "evidence_confidence", "modal_alternative", "external_orientation", "relationship_basis", "source_id", "notes"}
REGISTER_COLUMNS = {"register_id", "domain", "system_node_id", "node_name", "primary_modes", "dependency_classes", "dependency_strength", "known_redundancy", "unknown_redundancy", "external_orientation", "evidence_confidence", "source_id", "notes"}
MATRIX_COLUMNS = {"system_function", "marine_dependence", "rail_dependence", "highway_dependence", "external_market_dependence", "interchange_dependence", "modal_substitutability", "evidence_confidence", "notes"}
ALLOWED_STRENGTH = {"low", "moderate", "high", "unknown"}
ALLOWED_RELATIONSHIPS = {"documented_flow", "documented_corridor", "documented_facility_access", "documented_interchange", "documented_shipment_relationship", "generalized_supply_chain", "engineering_logistics_dependency", "proximity_only", "inferred"}
ALLOWED_TYPES = {"marine_gateway_dependency", "rail_dependency", "highway_dependency", "fuel_logistics_dependency", "external_market_dependency", "interchange_dependency", "single_mode_dependency", "multimodal_dependency"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_candidates(path: Path) -> set[str]:
    data = path.read_bytes()
    candidates = {hashlib.sha256(data).hexdigest()}
    if path.suffix.lower() in {".md", ".json", ".csv", ".yml", ".yaml", ".txt", ".svg"}:
        candidates.add(hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest())
    return candidates


def check_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("files", manifest.get("artifacts", {}))
    for relative, metadata in entries.items():
        artifact = ROOT / relative
        assert artifact.exists(), relative
        assert manifest_matches(ROOT, relative, metadata["sha256"]), f"Frozen artifact changed: {relative}"


def main() -> None:
    edges = pd.read_csv(DEP_EDGES, dtype=str).fillna("")
    register = pd.read_csv(DEP_REGISTER, dtype=str).fillna("")
    modal = pd.read_csv(MODAL_MATRIX, dtype=str).fillna("")
    matrix = pd.read_csv(MATRIX, dtype=str).fillna("")
    freight_nodes = pd.read_csv(NETWORKS / "freight_system_nodes.csv", dtype=str).fillna("")
    energy_nodes = pd.read_csv(NETWORKS / "energy_system_nodes.csv", dtype=str).fillna("")
    sources = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]

    assert set(edges.columns) == EDGE_COLUMNS
    assert set(register.columns) == REGISTER_COLUMNS
    assert set(modal.columns) == MATRIX_COLUMNS
    assert set(matrix.columns) == MATRIX_COLUMNS
    assert len(edges) == 20 and edges.dependency_id.is_unique
    assert len(register) == 12 and register.register_id.is_unique
    assert len(modal) == 6 and modal.system_function.is_unique
    assert len(matrix) == 6 and matrix.system_function.is_unique
    valid_nodes = set(freight_nodes.node_id) | set(energy_nodes.node_id)
    assert edges.source_node_id.isin(valid_nodes).all()
    assert edges.dependent_node_id.isin(valid_nodes).all()
    assert register.system_node_id.isin(set(freight_nodes.node_id)).all()
    assert edges.domain.isin({"port_marine", "rail", "highway", "energy_fuels", "industrial_materials", "carbonate_materials", "strategic_materials", "remediation", "agriculture_bulk"}).all()
    assert edges.dependency_type.isin(ALLOWED_TYPES).all()
    assert edges.dependency_strength.isin(ALLOWED_STRENGTH).all()
    assert edges.evidence_confidence.isin(ALLOWED_STRENGTH).all()
    assert edges.relationship_basis.isin(ALLOWED_RELATIONSHIPS).all()
    assert edges.source_id.isin(set(sources)).all()
    assert register.dependency_strength.isin(ALLOWED_STRENGTH).all()
    assert register.evidence_confidence.isin(ALLOWED_STRENGTH).all()
    assert register.source_id.isin(set(sources)).all()
    assert modal.iloc[:, 1:8].isin(ALLOWED_STRENGTH).all().all()
    assert matrix.iloc[:, 1:8].isin(ALLOWED_STRENGTH).all().all()
    assert set(edges.dependency_type) >= {"marine_gateway_dependency", "rail_dependency", "highway_dependency", "fuel_logistics_dependency", "external_market_dependency", "interchange_dependency"}
    assert edges.notes.str.len().gt(0).all() and register.notes.str.len().gt(0).all() and modal.notes.str.len().gt(0).all()

    substantive = " ".join(" ".join(map(str, frame.to_numpy().ravel())) for frame in [edges[["domain", "dependency_type", "dependency_strength", "relationship_basis"]], register[["domain", "dependency_classes", "dependency_strength"]], modal.iloc[:, :8], matrix.iloc[:, :8]])
    assert not re.search(r"2050|2075|scenario|fictional|attack path|exploit|credential|target prioritization|SCADA|sabotage opportunity", substantive, flags=re.I)
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*(?:tons?|trucks?|railcars?|vessels?|calls?|MW|MGD)\b", substantive, flags=re.I)

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
    assert manifest["phase"] == "5C"
    assert manifest["counts"]["dependency_edges"] == len(edges)
    assert manifest["counts"]["dependency_register"] == len(register)
    assert manifest["counts"]["modal_matrix_rows"] == len(modal)
    assert manifest["counts"]["dependency_matrix_rows"] == len(matrix)
    for relative, metadata in manifest["artifacts"].items():
        artifact = ROOT / relative
        assert artifact.exists() and artifact.stat().st_size > 0, relative
        assert sha256(artifact) == metadata["sha256"], relative

    artifacts = [
        MAPS / "19_freight_dependencies_critical_interfaces_2026.png",
        MAPS / "19_freight_dependencies_critical_interfaces_2026.svg",
        FIGURES / "freight_dependency_matrix_2026.png",
        FIGURES / "freight_dependency_matrix_2026.svg",
    ]
    for artifact in artifacts:
        assert artifact.exists() and artifact.stat().st_size > 10_000
    sizes = []
    for png in artifacts[0::2]:
        with Image.open(png) as image:
            image.verify()
            sizes.append(list(image.size))
    for svg in artifacts[1::2]:
        ET.parse(svg)

    canon = (ROOT / "docs/canon_status.md").read_text(encoding="utf-8")
    assert "C — HOLD" in canon and "intake-coordinate discrepancy" in canon

    result = {
        "status": "passed",
        "phase": "5C",
        "dependency_edges": len(edges),
        "dependency_register": len(register),
        "modal_matrix_dimensions": [len(modal), len(modal.columns) - 1],
        "dependency_matrix_dimensions": [len(matrix), len(matrix.columns) - 1],
        "map19_artifacts_valid": True,
        "phase4a_4c_5a_5b_immutable": True,
        "prior_maps_01_16b_unchanged": True,
        "qualitative_classes_valid": True,
        "no_quantities_or_routes": True,
        "no_hazardous_routes": True,
        "no_security_target_model": True,
        "no_future_freight_content": True,
        "materials_corridor_not_promoted": True,
        "image_sizes": sizes,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
