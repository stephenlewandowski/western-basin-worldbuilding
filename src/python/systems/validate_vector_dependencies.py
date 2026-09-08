"""Validate the qualitative Phase 12B vector/environment/human dependencies."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

SOURCES = ANALYSIS / "vector_ecology_sources.csv"
NODES = NETWORKS / "vector_ecology_nodes.csv"
A_MANIFEST = REPORTS / "vector_ecology_baseline_manifest.json"
B_MANIFEST = REPORTS / "vector_dependency_manifest.json"
A_CHECK = REPORTS / "vector_ecology_artifact_check.json"
MAP_PNG = MAPS / "39_vector_environment_human_dependencies_2026.png"
MAP_SVG = MAPS / "39_vector_environment_human_dependencies_2026.svg"
CHECK = REPORTS / "vector_dependency_artifact_check.json"

DEP = ANALYSIS / "vector_system_dependency_register.csv"
EDGES = NETWORKS / "vector_system_dependency_edges.csv"
MATRIX = ANALYSIS / "vector_system_dependency_matrix.csv"
EVIDENCE = ANALYSIS / "vector_dependency_evidence.csv"

SOURCE_COLUMNS = {
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
}

DEP_COLUMNS = {
    "dependency_id", "object_a", "object_b", "system_a", "system_b", "relationship_type",
    "documented_or_inferred", "relationship_basis", "spatial_scale", "evidence_strength",
    "source_id", "confidence", "reality_status", "canon_status", "notes",
}
MATRIX_COLUMNS = {
    "object_id", "object_type", "object_name", "temperature_relationship", "precipitation_hydrology",
    "wetland_standing_water", "urban_container", "forest_edge_host", "host_ecology",
    "population_contact_interface", "surveillance_detection", "governance_decision_interface",
    "spatial_scale_certainty", "temporal_certainty", "notes",
}
EVIDENCE_COLUMNS = {
    "evidence_id", "dependency_id", "claim_type", "claim_status", "source_id", "spatial_scale",
    "temporal_scope", "supported_statement", "not_supported_statement",
}
QUALITATIVE = {"strong", "moderate", "limited", "unknown", "not_applicable"}
DEPENDENCY_STATUSES = {"documented", "documented_plus_inferred", "inferred", "documented_boundary", "accepted_context_plus_inferred"}
RELATIONSHIPS = {"seasonal_development", "habitat_opportunity", "habitat_association", "habitat_interface", "container_habitat", "questing_habitat", "woodland_habitat", "host_association", "potential_interface", "detection_interface", "information_to_decision", "observation_interface", "environmental_driver", "spatial_scale", "health_boundary", "separation_rule", "effort_detection_boundary", "scale_boundary", "case_transmission_boundary", "monitoring_control_boundary", "hold_preservation"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def check_manifest(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    checked = []
    for rel, metadata in entries(payload).items():
        expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
        assert manifest_matches(ROOT, rel, str(expected)), rel
        checked.append(rel)
    return checked


def check_prior_freezes() -> tuple[int, int]:
    expected_hashes: dict[str, str] = {}
    unique: set[str] = set()
    total = 0
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for rel, metadata in entries(payload).items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if rel in expected_hashes:
                assert expected_hashes[rel] == expected, rel
            expected_hashes[rel] = expected
            assert manifest_matches(ROOT, rel, expected), rel
            unique.add(rel)
            total += 1
    return total, len(unique)


def check_phase11_and_holds() -> None:
    for name in (
        "phase11a_population_settlement_freeze_manifest.json",
        "phase11b_population_mobility_dependencies_freeze_manifest.json",
        "phase11c_population_settlement_futures_freeze_manifest.json",
    ):
        payload = json.loads((REPORTS / name).read_text(encoding="utf-8"))
        assert payload["status"] == "ACCEPTED / FROZEN", name
    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, rel
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, rel
    handoff = (REPORTS / "current_phase_handoff.md").read_text(encoding="utf-8").lower()
    assert "phase 12" in handoff and "phase12c" in handoff and "phase 13" in handoff


def check_no_later_implementation() -> None:
    roots = [ROOT / "data/processed", ROOT / "outputs/maps/systems", ROOT / "src/python/systems", ROOT / "src/R/systems"]
    bad = []
    for base in roots:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/").lower()
            name = path.name.lower()
            if "phase13" in rel or "phase13" in name:
                bad.append(rel)
            if ("vector" in name and "future" in name) or ("future" in name and "vector" in name):
                bad.append(rel)
            if name.startswith("40_") or name.startswith("40b_"):
                bad.append(rel)
    assert not bad, bad


def check_a_immutability() -> int:
    payload = json.loads(A_MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "12A" and payload["phase12c_implemented"] is False and payload["phase13_implemented"] is False
    checked = 0
    for rel, metadata in payload["artifacts"].items():
        expected = str(metadata["sha256"])
        assert manifest_matches(ROOT, rel, expected), rel
        checked += 1
    protected = json.loads(B_MANIFEST.read_text(encoding="utf-8"))["protected_12a_manifest"]
    assert manifest_matches(ROOT, str(protected["path"]), str(protected["sha256"]))
    canonical = A_MANIFEST.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = canonical.replace(b"\n", b"\r\n")
    assert int(protected["bytes"]) in {A_MANIFEST.stat().st_size, len(canonical), len(crlf)}
    return checked


def check_boundaries(dep: pd.DataFrame, matrix: pd.DataFrame, evidence: pd.DataFrame) -> None:
    frames = [dep, matrix, evidence]
    fields = set().union(*(set(frame.columns) for frame in frames))
    forbidden_fields = {"risk_score", "vulnerability_score", "ej_score", "infection_probability", "contact_probability", "disease_incidence", "hospitalization", "mortality", "dose", "exposure_score"}
    assert not fields.intersection(forbidden_fields)
    text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower().replace("_", " ")
    for required in ("documented", "inferred", "temperature", "standing water", "container", "forest", "host", "population", "surveillance", "detection", "not exposure", "not abundance", "local transmission", "not absence"):
        assert required in text, required
    assert not re.search(r"(?:risk score|vulnerability score|ej score|infection probability|disease incidence)\s*[,=:]\s*[0-9]", text)
    assert not re.search(r"\b(?:2050|2075)\b", text)
    assert not re.search(r"(?:contact|infection|disease|exposure|dose)\s*(?:probability|score|estimate)\s*[,=:]\s*[0-9]", text)


def check_map() -> list[int]:
    with Image.open(MAP_PNG) as image:
        image.verify()
        size = list(image.size)
    ET.parse(MAP_SVG)
    text = " ".join(ET.parse(MAP_SVG).getroot().itertext()).lower()
    for required in ("map 39", "vector", "environment", "human-system", "temperature", "standing water", "urban containers", "forest / edge", "surveillance", "not continuous", "not exposure"):
        assert required in text, required
    return size


def main() -> None:
    dep, edge, matrix, evidence, nodes, sources = (read(path) for path in (DEP, EDGES, MATRIX, EVIDENCE, NODES, SOURCES))
    assert set(dep.columns) == DEP_COLUMNS
    assert set(edge.columns) == DEP_COLUMNS
    assert set(matrix.columns) == MATRIX_COLUMNS
    assert set(evidence.columns) == EVIDENCE_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert len(dep) == 28 and dep.dependency_id.is_unique
    assert len(edge) == 28 and edge.dependency_id.is_unique
    assert len(matrix) == 8 and matrix.object_id.is_unique
    assert len(evidence) == 8 and evidence.evidence_id.is_unique
    assert len(nodes) == 20 and nodes.node_id.is_unique
    assert len(sources) == 27 and sources.source_id.is_unique
    ixodes = sources.loc[sources.source_id == "v12_cdc_ixodes"].iloc[0]
    assert ixodes.url == "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html"
    assert ixodes.retrieval_url == "https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx"
    assert "not CDC-hosted" in ixodes.retrieval_provenance
    assert "HTTP 403" in ixodes.retrieval_provenance
    source_ids = set(sources.source_id)
    assert dep.source_id.isin(source_ids).all() and edge.source_id.isin(source_ids).all() and evidence.source_id.isin(source_ids).all()
    assert dep.relationship_type.isin(RELATIONSHIPS).all()
    assert dep.documented_or_inferred.isin(DEPENDENCY_STATUSES).all()
    assert dep.evidence_strength.isin(QUALITATIVE).all() and dep.confidence.isin({"high", "moderate", "limited", "unknown"}).all()
    assert dep.reality_status.eq("real").all() and dep.canon_status.isin({"verified", "inferred"}).all()
    assert dep.notes.str.len().gt(0).all() and evidence.not_supported_statement.str.len().gt(0).all()
    assert matrix.iloc[:, 3:14].apply(lambda column: column.isin(QUALITATIVE)).all().all()
    assert matrix.notes.str.len().gt(0).all()
    assert "qualitative matrix" in " ".join(matrix.notes).lower()
    assert set(evidence.dependency_id) <= set(dep.dependency_id)
    assert set(edge.dependency_id) == set(dep.dependency_id)
    assert edge.equals(dep)
    required_relationships = {
        "seasonal_development", "habitat_opportunity", "container_habitat", "questing_habitat",
        "host_association", "potential_interface", "detection_interface", "information_to_decision",
        "health_boundary", "effort_detection_boundary", "case_transmission_boundary",
    }
    assert required_relationships <= set(dep.relationship_type)
    check_boundaries(dep, matrix, evidence)
    a_checked = check_a_immutability()
    check_phase11_and_holds()
    prior_entries, prior_unique = check_prior_freezes()
    check_no_later_implementation()
    map_size = check_map()
    manifest = json.loads(B_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "12B" and manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["map_number"] == 39
    assert manifest["counts"] == {"dependency_register": 28, "dependency_edges": 28, "matrix_rows": 8, "evidence_rows": 8, "sources_reused": 27}
    checked = check_manifest(B_MANIFEST)
    result = {
        "status": "passed", "phase": "12B", "map_number": 39,
        "dependency_register": len(dep), "dependency_edges": len(edge), "matrix_rows": len(matrix),
        "evidence_rows": len(evidence), "sources_reused": len(sources), "map39_valid": True,
        "image_size": map_size, "phase12a_artifacts_checked": a_checked,
        "phase12b_manifest_artifacts_checked": len(checked), "prior_freeze_manifest_entries_checked": prior_entries,
        "prior_unique_protected_artifacts_checked": prior_unique, "phase11a_b_c_accepted_frozen": True,
        "documented_vs_inferred_boundary": True, "presence_abundance_boundary": True,
        "vector_pathogen_human_case_boundary": True, "sampling_effort_boundary": True,
        "spatial_scale_boundary": True, "no_individual_risk": True, "no_vulnerability_scoring": True,
        "no_unsupported_disease_attribution": True, "no_unsupported_future_range": True,
        "phase12c_absent": True, "phase13_absent": True, "active_holds_preserved": True,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
