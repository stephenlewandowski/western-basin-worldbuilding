"""Validate the bounded factual Phase 12A vector ecology baseline."""
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
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

NODES = NETWORKS / "vector_ecology_nodes.csv"
EDGES = NETWORKS / "vector_ecology_edges.csv"
SURVEILLANCE = ANALYSIS / "vector_surveillance_records.csv"
HABITAT = ANALYSIS / "vector_habitat_associations.csv"
SOURCES = ANALYSIS / "vector_ecology_sources.csv"
UNCERTAINTY = ANALYSIS / "vector_ecology_uncertainty.csv"
MAP_PNG = MAPS / "38_vector_ecology_baseline_2026.png"
MAP_SVG = MAPS / "38_vector_ecology_baseline_2026.svg"
MANIFEST = REPORTS / "vector_ecology_baseline_manifest.json"
CHECK = REPORTS / "vector_ecology_artifact_check.json"
RAW_TICK = ROOT / "data/raw/vector_ecology/Public_Use_Ixodes_County_Table_2024_summary.xlsx"

NODE_COLUMNS = {
    "node_id", "name", "node_type", "vector_group", "taxon_or_system", "habitat_context",
    "seasonality", "geographic_scale", "latitude", "longitude", "source_id",
    "evidence_status", "confidence", "reality_status", "canon_status", "notes",
}
EDGE_COLUMNS = {
    "edge_id", "from_id", "to_id", "relationship_type", "relationship_basis",
    "geographic_scale", "source_id", "evidence_status", "confidence", "reality_status",
    "canon_status", "notes",
}
SURV_COLUMNS = {
    "record_id", "year", "vector_group", "species_or_vector", "pathogen", "surveillance_program",
    "surveillance_method", "geographic_area", "geographic_scale", "sampling_effort",
    "detection_status", "observed_value", "units", "source_id", "evidence_status",
    "confidence", "uncertainty_notes", "notes",
}
HAB_COLUMNS = {
    "association_id", "vector_or_group", "association_type", "environment_or_host",
    "relationship_description", "season_or_period", "geographic_scale", "evidence_status",
    "source_id", "confidence", "notes",
}
UNC_COLUMNS = {"uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"}
SOURCE_COLUMNS = {
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
}
QUALITATIVE = {"high", "moderate", "limited", "unknown"}
NODE_TYPES = {"vector_taxon", "habitat_context", "host_ecology", "environmental_driver", "surveillance_program", "pathogen_context"}
EDGE_BASIS = {"documented_source", "documented_plus_inferred", "accepted_layer", "project_boundary", "project_inference", "documented_program", "accepted_ecology_context"}
SURV_EVIDENCE = {"documented_surveillance", "contextual_human_observation", "documented_detection", "documented_distribution_context"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def check_manifest(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    checked: list[str] = []
    for rel, metadata in artifact_entries(payload).items():
        expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
        artifact = ROOT / rel
        assert artifact.exists() and artifact.stat().st_size > 0, rel
        assert manifest_matches(ROOT, rel, str(expected)), rel
        checked.append(rel)
    return checked


def check_prior_freezes() -> tuple[int, int, dict[str, str]]:
    protected: set[str] = set()
    expected_hashes: dict[str, str] = {}
    statuses: dict[str, str] = {}
    total = 0
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        statuses[path.name] = str(payload.get("status", ""))
        for rel, metadata in artifact_entries(payload).items():
            expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
            if rel in expected_hashes:
                assert expected_hashes[rel] == str(expected), rel
            expected_hashes[rel] = str(expected)
            assert manifest_matches(ROOT, rel, str(expected)), rel
            protected.add(rel)
            total += 1
    return total, len(protected), statuses


def check_phase11_frozen() -> None:
    expected = {
        "phase11a_population_settlement_freeze_manifest.json",
        "phase11b_population_mobility_dependencies_freeze_manifest.json",
        "phase11c_population_settlement_futures_freeze_manifest.json",
    }
    for name in expected:
        payload = json.loads((REPORTS / name).read_text(encoding="utf-8"))
        assert payload["status"] == "ACCEPTED / FROZEN", name
        assert payload["accepted_phase"].startswith("11"), name


def check_required_status_surfaces() -> None:
    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "phase 11a" in text and "phase 11b" in text and "phase 11c" in text, rel
        assert "accepted / frozen" in text, rel
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, rel
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, rel
    handoff = (REPORTS / "current_phase_handoff.md").read_text(encoding="utf-8").lower()
    assert "phase 12" in handoff and "phase12c" in handoff and "phase 13" in handoff


def check_no_later_implementation() -> None:
    roots = [ROOT / "data/processed", ROOT / "outputs/maps/systems", ROOT / "src/python/systems", ROOT / "src/R/systems"]
    paths = [p for base in roots for p in base.rglob("*") if p.is_file()]
    bad = []
    for path in paths:
        rel = str(path.relative_to(ROOT)).replace("\\", "/").lower()
        name = path.name.lower()
        if "phase13" in rel or "phase13" in name:
            bad.append(rel)
        if ("vector" in name and "future" in name) or ("future" in name and "vector" in name):
            bad.append(rel)
        if name.startswith("40_") or name.startswith("40b_"):
            bad.append(rel)
    assert not bad, bad
    assert not (MAPS / "40_vector_ecology_futures_2050.png").exists()
    assert not (MAPS / "40b_vector_ecology_futures_2075.png").exists()


def check_coordinates(nodes: pd.DataFrame) -> None:
    for row in nodes.itertuples():
        assert (row.latitude == "") == (row.longitude == ""), row.node_id
        if row.latitude:
            assert -90 <= float(row.latitude) <= 90
            assert -180 <= float(row.longitude) <= 180
    anchor = nodes.loc[nodes.node_id == "VEC-008"].iloc[0]
    assert anchor.latitude == "41.690" and anchor.longitude == "-83.220"


def check_surveillance(surv: pd.DataFrame, source_ids: set[str]) -> dict[str, int]:
    assert len(surv) == 36 and surv.record_id.is_unique
    assert surv.source_id.isin(source_ids).all()
    for column in ("year", "surveillance_method", "geographic_scale", "sampling_effort", "detection_status", "source_id", "uncertainty_notes", "notes"):
        assert surv[column].str.len().gt(0).all(), column
    assert surv.evidence_status.isin(SURV_EVIDENCE).all()
    assert surv.confidence.isin(QUALITATIVE).all()
    assert set(surv.year).issubset({"2023", "2025", "2026"})
    assert not surv.vector_group.eq("human-case-context").any() or surv.loc[surv.vector_group == "human-case-context", "surveillance_method"].str.contains("case|disease", case=False).all()
    human = surv[surv.vector_group == "human-case-context"]
    assert len(human) == 2 and human.notes.str.contains("context only", case=False).all()
    assert human.detection_status.str.contains("reported", case=False).all()
    assert not human.surveillance_method.str.contains("trap|pool", case=False).any()
    county_ticks = surv[surv.record_id.str.startswith("VS-TICK-")]
    assert len(county_ticks) == 18
    assert set(county_ticks.detection_status).issubset({"established", "reported", "no records (not absence)"})
    assert county_ticks.uncertainty_notes.str.contains("no records", case=False).all()
    assert county_ticks.sampling_effort.str.contains("not reported", case=False).all()
    assert county_ticks.notes.str.contains("not abundance", case=False).all()
    exact_values = {
        "VS-001": "42", "VS-002": "11980", "VS-003": "4", "VS-004": "45",
        "VS-005": "124", "VS-006": "4", "VS-007": "6", "VS-008": "6351",
        "VS-009": "3", "VS-010": "1", "VS-012": "33", "VS-013": "1",
    }
    for record_id, value in exact_values.items():
        row = surv.loc[surv.record_id == record_id].iloc[0]
        assert row.observed_value == value, record_id
    assert surv.loc[surv.record_id == "VS-011", "year"].iloc[0] == "2023"
    return {"total": len(surv), "county_tick_statuses": len(county_ticks), "human_context_rows": len(human)}


def check_boundary_text(frames: list[pd.DataFrame]) -> None:
    text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower()
    fields = set().union(*(set(frame.columns) for frame in frames))
    forbidden_fields = {"abundance_index", "abundance_score", "risk_score", "infection_probability", "disease_incidence_forecast", "hospitalization", "mortality", "dose", "vulnerability_score", "ej_score", "contact_probability"}
    assert not fields.intersection(forbidden_fields)
    assert "presence != abundance" in text or "presence is not abundance" in text
    assert "sampling effort" in text and "not abundance" in text
    assert "detection" in text and "establishment" in text
    assert "no records" in text and "not absence" in text
    assert "positive vector pool" in text and "human case" in text
    assert "local transmission" in text
    assert not re.search(r"(?:infection probability|disease incidence|risk score|vulnerability score|ej score)\s*[,=:]\s*[0-9]", text)
    assert not re.search(r"\b(?:2050|2075)\b", text)
    assert not re.search(r"(?:established|abundance|prevalence)\s*[,=:]\s*[0-9]", text)


def check_map() -> list[int]:
    with Image.open(MAP_PNG) as image:
        image.verify()
        size = list(image.size)
    root = ET.parse(MAP_SVG).getroot()
    text = " ".join(root.itertext()).lower()
    for required in ("map 38", "vector ecology", "culex", "aedes", "ixodes", "surveillance boundary", "presence", "abundance", "positive vector pool", "not vector collection"):
        assert required in text, required
    return size


def main() -> None:
    nodes, edges, surv, habitat, sources, uncertainty = (read(path) for path in (NODES, EDGES, SURVEILLANCE, HABITAT, SOURCES, UNCERTAINTY))
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert set(surv.columns) == SURV_COLUMNS
    assert set(habitat.columns) == HAB_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert set(uncertainty.columns) == UNC_COLUMNS
    assert len(nodes) == 20 and nodes.node_id.is_unique
    assert len(edges) == 26 and edges.edge_id.is_unique
    assert len(habitat) == 15 and habitat.association_id.is_unique
    assert len(sources) == 27 and sources.source_id.is_unique and sources.url.is_unique
    assert len(uncertainty) == 10 and uncertainty.uncertainty_id.is_unique
    source_ids = set(sources.source_id)
    assert nodes.source_id.isin(source_ids).all() and edges.source_id.isin(source_ids).all()
    assert habitat.source_id.isin(source_ids).all() and uncertainty.source_id.isin(source_ids).all()
    assert nodes.node_type.isin(NODE_TYPES).all()
    assert nodes.confidence.isin(QUALITATIVE).all() and edges.confidence.isin(QUALITATIVE).all()
    assert edges.relationship_basis.isin(EDGE_BASIS).all()
    assert edges.from_id.isin(set(nodes.node_id)).all() and edges.to_id.isin(set(nodes.node_id)).all()
    assert edges.reality_status.eq("real").all() and edges.canon_status.isin({"verified", "inferred"}).all()
    assert habitat.confidence.isin(QUALITATIVE).all() and uncertainty.confidence.isin(QUALITATIVE).all()
    assert sources.use_limitations.str.len().gt(0).all()
    ixodes = sources.loc[sources.source_id == "v12_cdc_ixodes"].iloc[0]
    assert ixodes.url == "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html"
    assert ixodes.retrieval_url == "https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx"
    assert "not CDC-hosted" in ixodes.retrieval_provenance
    assert "HTTP 403" in ixodes.retrieval_provenance
    check_coordinates(nodes)
    surveillance_counts = check_surveillance(surv, source_ids)
    check_boundary_text([nodes, edges, surv, habitat, uncertainty])
    assert RAW_TICK.exists() and RAW_TICK.stat().st_size > 1000
    retrieval_note = json.loads(MANIFEST.read_text(encoding="utf-8"))["raw_inputs"][str(RAW_TICK.relative_to(ROOT)).replace("\\", "/")]["retrieval_note"]
    assert "HTTP 403" in retrieval_note
    assert "https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html" in retrieval_note
    assert "https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx" in retrieval_note
    assert "not CDC-hosted" in retrieval_note
    check_phase11_frozen()
    prior_entries, prior_unique, prior_statuses = check_prior_freezes()
    check_required_status_surfaces()
    check_no_later_implementation()
    map_size = check_map()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "12A" and manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["map_number"] == 38
    assert manifest["counts"] == {"nodes": 20, "edges": 26, "surveillance_records": 36, "habitat_associations": 15, "sources": 27, "uncertainties": 10}
    checked = check_manifest(MANIFEST)
    result = {
        "status": "passed", "phase": "12A", "map_number": 38,
        "nodes": len(nodes), "edges": len(edges), "surveillance_records": len(surv),
        "habitat_associations": len(habitat), "sources": len(sources), "uncertainties": len(uncertainty),
        "map38_valid": True, "image_size": map_size,
        "manifest_artifacts_checked": len(checked), "prior_freeze_manifest_entries_checked": prior_entries,
        "prior_unique_protected_artifacts_checked": prior_unique, "prior_manifest_statuses": prior_statuses,
        "phase11a_b_c_accepted_frozen": True, "presence_abundance_boundary": True,
        "vector_pathogen_human_case_boundary": True, "detection_establishment_boundary": True,
        "sampling_effort_boundary": True, "spatial_scale_boundary": True,
        "no_individual_risk": True, "no_vulnerability_scoring": True,
        "no_unsupported_disease_attribution": True, "no_unsupported_future_range": True,
        "phase12c_absent": True, "phase13_absent": True, "active_holds_preserved": True,
        "surveillance_summary": surveillance_counts,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
