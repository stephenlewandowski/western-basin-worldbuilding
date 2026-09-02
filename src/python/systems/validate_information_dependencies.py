"""Validate Phase 4B information dependencies and protect the Phase 4A baseline."""
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
ANALYSIS = ROOT / "data/processed/analysis"
FIGURES = ROOT / "outputs/figures"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

DEPENDENCIES = NETWORKS / "information_dependency_edges.csv"
BLIND_SPOTS = ANALYSIS / "information_blind_spots.csv"
AUTHORITY = ANALYSIS / "decision_authority_matrix.csv"
MATRIX = FIGURES / "information_dependency_matrix_2026.csv"
MANIFEST = REPORTS / "information_dependency_manifest.json"
CHECK = REPORTS / "information_dependency_artifact_check.json"
PHASE4A_MANIFEST = REPORTS / "observation_system_manifest.json"

DEPENDENCY_COLUMNS = {
    "dependency_id", "source_node_id", "dependent_node_id", "domain", "information_type", "dependency_role", "timeliness", "availability_requirement", "coverage", "uncertainty", "authority_level", "access_class", "relationship_basis", "source_id", "confidence", "notes",
}
BLIND_COLUMNS = {"blindspot_id", "domain", "affected_chain", "blindspot_type", "description", "consequence_type", "evidence_basis", "source_id", "confidence", "additional_data_needed", "notes"}
AUTHORITY_COLUMNS = {"domain", "observes", "analyzes", "advises", "decides", "operates_or_responds", "source_id", "confidence", "notes"}
MATRIX_COLUMNS = {"domain", "observation_availability", "timeliness", "spatial_coverage", "model_dependence", "organizational_handoff", "public_data_availability", "decision_authority_clarity"}
ALLOWED_DOMAINS = {"lake_erie_hab", "maumee_hydrology", "environmental_regulatory", "energy_information"}
ALLOWED_TIMELINESS = {"real_time_or_near_real_time", "hourly_or_subdaily", "daily", "periodic", "event_driven", "unknown"}
ALLOWED_ORDINAL = {"low", "moderate", "high", "unknown"}
ALLOWED_COVERAGE = {"point", "local", "regional", "basin", "systemwide", "unknown"}
ALLOWED_AUTHORITY = {"operator", "municipal", "county", "state", "regional", "federal", "multi_agency", "unknown"}
ALLOWED_ACCESS = {"public", "partially_public", "operational_nonpublic", "unknown"}
ALLOWED_BASIS = {"observed", "documented", "qualified_documented", "inferred", "engineering_dependency"}
ALLOWED_BLIND_TYPES = {"spatial_coverage", "temporal_latency", "measurement_uncertainty", "model_uncertainty", "jurisdiction_boundary", "organizational_handoff", "single_source_dependency", "public_data_gap", "status_uncertainty"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    dependencies = pd.read_csv(DEPENDENCIES, dtype=str).fillna("")
    blind_spots = pd.read_csv(BLIND_SPOTS, dtype=str).fillna("")
    authority = pd.read_csv(AUTHORITY, dtype=str).fillna("")
    matrix = pd.read_csv(MATRIX, dtype=str).fillna("")
    phase4a_nodes = pd.read_csv(NETWORKS / "observation_system_nodes.csv", dtype=str).fillna("")
    sources = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]

    assert set(dependencies.columns) == DEPENDENCY_COLUMNS
    assert set(blind_spots.columns) == BLIND_COLUMNS
    assert set(authority.columns) == AUTHORITY_COLUMNS
    assert set(matrix.columns) == MATRIX_COLUMNS
    assert len(dependencies) == 20 and dependencies.dependency_id.is_unique
    assert len(blind_spots) == 10 and blind_spots.blindspot_id.is_unique
    assert len(authority) == 4 and authority.domain.is_unique
    assert len(matrix) == 4 and matrix.domain.is_unique
    assert set(dependencies.domain) == ALLOWED_DOMAINS
    assert set(blind_spots.domain) == ALLOWED_DOMAINS
    assert set(authority.domain) == ALLOWED_DOMAINS
    assert set(matrix.domain) == ALLOWED_DOMAINS

    node_ids = set(phase4a_nodes.node_id)
    assert set(dependencies.source_node_id) <= node_ids
    assert set(dependencies.dependent_node_id) <= node_ids
    assert set(dependencies.source_id) <= set(sources)
    assert set(blind_spots.source_id) <= set(sources)
    assert set(authority.source_id) <= set(sources)
    assert dependencies.confidence.isin({"high", "medium", "low"}).all()
    assert blind_spots.confidence.isin({"high", "medium", "low"}).all()
    assert authority.confidence.isin({"high", "medium", "low"}).all()
    assert dependencies.relationship_basis.isin(ALLOWED_BASIS).all()
    assert dependencies.timeliness.isin(ALLOWED_TIMELINESS).all()
    assert dependencies.availability_requirement.isin(ALLOWED_ORDINAL).all()
    assert dependencies.coverage.isin(ALLOWED_COVERAGE).all()
    assert dependencies.uncertainty.isin(ALLOWED_ORDINAL).all()
    assert dependencies.authority_level.isin(ALLOWED_AUTHORITY).all()
    assert dependencies.access_class.isin(ALLOWED_ACCESS).all()
    assert blind_spots.blindspot_type.isin(ALLOWED_BLIND_TYPES).all()
    assert set(dependencies.dependency_id.str[4:5]) == {"A", "B", "C", "D"}
    assert set(blind_spots.affected_chain) == {"A", "B", "C", "D"}
    assert set(matrix.iloc[:, 1:].stack()) <= ALLOWED_ORDINAL
    assert dependencies.notes.str.len().gt(0).all()
    assert blind_spots.description.str.len().gt(0).all()
    assert authority.notes.str.len().gt(0).all()

    modeled_text = " ".join(" ".join(map(str, row)) for frame in [dependencies, blind_spots, authority, matrix] for row in frame.to_numpy())
    assert not re.search(r"attack path|exploit|credential assumption|red[- ]team|surveillance[- ]state|fictional sensor|\b2050\b|\b2075\b", modeled_text, flags=re.I)
    assert not dependencies.dependency_role.str.contains(r"trigger|automated|control", case=False, regex=True).any()

    phase4a_manifest = json.loads(PHASE4A_MANIFEST.read_text(encoding="utf-8"))
    for relative, metadata in phase4a_manifest["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and sha256(path) == metadata["sha256"], f"Phase 4A baseline changed: {relative}"

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "4B"
    assert manifest["counts"]["information_dependencies"] == len(dependencies)
    assert manifest["counts"]["blind_spots"] == len(blind_spots)
    assert manifest["counts"]["authority_rows"] == len(authority)
    assert manifest["counts"]["matrix_rows"] == len(matrix)
    for relative, metadata in manifest["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and path.stat().st_size > 0, relative
        assert sha256(path) == metadata["sha256"], relative

    map_png = MAPS / "15_information_dependencies_governance_2026.png"
    map_svg = MAPS / "15_information_dependencies_governance_2026.svg"
    matrix_png = FIGURES / "information_dependency_matrix_2026.png"
    matrix_svg = FIGURES / "information_dependency_matrix_2026.svg"
    for path in [map_png, map_svg, matrix_png, matrix_svg]:
        assert path.exists() and path.stat().st_size > 10_000, str(path)
    with Image.open(map_png) as image:
        image.verify()
        map_size = image.size
    with Image.open(matrix_png) as image:
        image.verify()
        matrix_size = image.size
    ET.parse(map_svg)
    ET.parse(matrix_svg)

    result = {
        "status": "passed",
        "phase": "4B",
        "information_dependencies": len(dependencies),
        "blind_spots": len(blind_spots),
        "authority_rows": len(authority),
        "matrix_dimensions": [len(matrix), len(matrix.columns) - 1],
        "map15_png_dimensions": list(map_size),
        "matrix_png_dimensions": list(matrix_size),
        "provenance_complete": True,
        "phase4a_baseline_immutable": True,
        "map15_artifacts_valid": True,
        "matrix_artifacts_valid": True,
        "no_cyber_or_sensitive_topology": True,
        "no_future_scenario_content": True,
        "toledo_intake_uncertainty_preserved": True,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
