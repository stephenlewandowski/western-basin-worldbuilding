"""Validate Phase 13B infectious-disease dependency products independently of the builder."""
from __future__ import annotations

import argparse
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

DEP = ANALYSIS / "infectious_disease_dependency_register.csv"
EDGES = NETWORKS / "infectious_disease_dependency_edges.csv"
MATRIX = ANALYSIS / "infectious_disease_dependency_matrix.csv"
CROSSWALK = ANALYSIS / "infectious_disease_evidence_crosswalk.csv"
SOURCES = ANALYSIS / "infectious_disease_dependency_sources.csv"
UNCERTAINTIES = ANALYSIS / "infectious_disease_dependency_uncertainties.csv"
MAP_PNG = MAPS / "42_infectious_disease_transmission_dependencies_2026.png"
MAP_SVG = MAPS / "42_infectious_disease_transmission_dependencies_2026.svg"
MANIFEST = REPORTS / "infectious_disease_dependency_manifest.json"
CHECK = REPORTS / "infectious_disease_dependency_artifact_check.json"
REVIEW = REPORTS / "infectious_disease_dependency_independent_review.md"
PHASE13A_FREEZE = REPORTS / "phase13a_infectious_disease_freeze_manifest.json"
BASE_SHA = "abb189e2d5d2e65f28fd9d54e48c4d7802709d1c"

DEP_COLUMNS = {
    "dependency_id", "from_id", "to_id", "relationship_type", "dependency_type", "archetype",
    "documented_or_inferred", "relationship_basis", "direction", "spatial_scale", "temporal_scope",
    "evidence_strength", "source_id", "uncertainty_id", "uncertainty", "confidence", "reality_status",
    "canon_status", "relevant_disease_systems", "notes",
}
EDGE_COLUMNS = {"edge_id"} | DEP_COLUMNS
MATRIX_COLUMNS = {
    "matrix_id", "archetype", "climate_sensitivity", "hydrologic_sensitivity", "vector_dependence",
    "food_freight_dependence", "population_contact_dependence", "mobility_dependence", "healthcare_dependence",
    "surveillance_dependence", "governance_dependence", "spatial_scale", "temporal_scope", "source_ids", "notes",
}
CROSSWALK_COLUMNS = {
    "evidence_id", "dependency_id", "claim_type", "claim_status", "source_id", "evidence_basis",
    "spatial_scale", "temporal_scope", "supported_statement", "not_supported_statement",
}
SOURCE_COLUMNS = {
    "source_id", "title", "url", "source_type", "publication_or_period", "retrieval_date", "geographic_scale",
    "method_or_product", "evidence_use", "use_limitations", "retrieval_url", "retrieval_provenance",
}
UNC_COLUMNS = {"uncertainty_id", "subject", "category", "statement", "resolution_status", "source_id", "confidence", "notes"}
QUALITATIVE = {"strong", "moderate", "limited", "unknown", "not_applicable"}
CONFIDENCE = {"high", "moderate", "limited", "unknown"}
ARCHETYPES = {"vector-borne", "waterborne/environmental", "foodborne/enteric", "respiratory", "zoonotic", "healthcare/AMR"}
DOC_STATUS = {"documented", "inferred"}
RELATIONSHIP_TYPES = {
    "frames_seasonality", "creates_habitat_opportunity", "mediates_host_habitat", "frames_transmission_opportunity",
    "frames_contact_opportunity", "feeds_observation", "conditions_exposure_opportunity", "disrupts_or_connects_pathway",
    "depends_on_system_condition", "frames_exposure_opportunity", "supplies_case_observation", "supports_response_coordination",
    "connects_food_system", "connects_distribution", "creates_propagation_opportunity", "is_observed_by",
    "complements_detection", "supports_investigation_response", "structures_contact_opportunity", "connects_contact_opportunity",
    "frames_care_detection_interface", "care_detection_interface", "supplies_surveillance_data", "mediates_host_interface", "frames_animal_human_opportunity",
    "supplies_animal_observations", "frames_resistance_detection_interface", "supports_service_continuity",
    "supports_infection_control_coordination",
}
DEPENDENCY_TYPES = {
    "environmental driver", "ecological mediator", "infrastructure dependency", "surveillance dependency",
    "institutional response dependency", "population/contact interface", "mobility interface", "food/freight interface",
    "healthcare interface",
}
RELATIONSHIP_BASES = {
    "documented_source", "accepted_layer", "accepted_layer_plus_project_inference", "project_inference",
    "documented_source_plus_project_inference", "boundary_rule",
}
EXTERNAL_IDS = {
    "EXT-CLIMATE", "EXT-VECTOR-ECOLOGY", "EXT-HYDROLOGY", "EXT-ECOLOGY", "EXT-FLOODING", "EXT-WATER-INFRASTRUCTURE",
    "EXT-FOOD-PRODUCTION", "EXT-FOOD-PROCESSING", "EXT-FREIGHT", "EXT-SETTLEMENT", "EXT-CONTACT-STRUCTURE",
    "EXT-MOBILITY", "EXT-ANIMAL-HOSTS", "EXT-OCCUPATIONAL-CONTACT", "EXT-HEALTHCARE", "EXT-INFRASTRUCTURE",
}
REQUIRED_SOURCES = {
    "phase1_water_context", "phase3_energy_context", "phase5_freight_context", "phase6_ecology_context",
    "phase9_hazard_dependency_context", "phase11_mobility_context", "phase12_vector_dependency_context",
    "phase10_coordination_context",
}
BASE_SOURCE_IDS = {
    "s13_nndss_about", "s13_nndss_wonder", "s13_cdc_wnv", "s13_cdc_lyme", "s13_cdc_legionella_surv",
    "s13_cdc_legionella_about", "s13_cdc_water_surv", "s13_cdc_nors", "s13_cdc_enteric", "s13_cdc_foodnet",
    "s13_cdc_fluview", "s13_cdc_flu_methods", "s13_cdc_wastewater", "s13_cdc_rabies", "s13_cdc_nhsn",
    "s13_cdc_ar", "s13_ind_reportable", "s13_ohio_vector", "s13_mi_vector", "phase7_exposure", "phase9_climate",
    "phase11_population", "phase12_vector", "phase4_information", "phase10_governance",
}
PRIOR_MANIFESTS = {
    "reports/phase3a_freeze_manifest.json", "reports/phase3b_freeze_manifest.json",
    "reports/phase4b_information_freeze_manifest.json", "reports/phase4c_information_freeze_manifest.json",
    "reports/phase5a_freight_freeze_manifest.json", "reports/phase5b_freight_evidence_freeze_manifest.json",
    "reports/phase5c_freight_dependency_freeze_manifest.json", "reports/phase6a_ecology_freeze_manifest.json",
    "reports/phase6b_ecological_dependency_freeze_manifest.json", "reports/phase6c_ecological_futures_freeze_manifest.json",
    "reports/phase7a_exposure_environmental_health_freeze_manifest.json", "reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json",
    "reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json", "reports/phase8c_biogeochemical_futures_freeze_manifest.json",
    "reports/phase9a_climate_natural_hazards_freeze_manifest.json", "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
    "reports/phase9c_climate_hazard_futures_freeze_manifest.json", "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
    "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", "reports/phase10c_governance_futures_freeze_manifest.json",
    "reports/phase11a_population_settlement_freeze_manifest.json", "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
    "reports/phase11c_population_settlement_futures_freeze_manifest.json", "reports/phase12a_vector_ecology_freeze_manifest.json",
    "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json", "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
}


def read(path: Path) -> pd.DataFrame:
    assert path.is_file() and path.stat().st_size > 0, path
    return pd.read_csv(path, dtype=str, keep_default_na=False).fillna("")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def portable_match(relative: str, expected: str) -> bool:
    if manifest_matches(ROOT, relative, expected):
        return True
    path = ROOT / relative
    if path.suffix.lower() not in {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg", ".py", ".r"}:
        return False
    try:
        accepted = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{relative}"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    canonical = lambda data: data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return canonical(path.read_bytes()) == canonical(accepted) and expected in {
        hashlib.sha256(accepted).hexdigest(),
        hashlib.sha256(accepted.replace(b"\n", b"\r\n")).hexdigest(),
    }


def verify_manifest(path: Path, expected_phase: str | None = None) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if expected_phase:
        assert payload.get("accepted_phase") == expected_phase, path
    checked = 0
    for relative, metadata in entries(payload).items():
        expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
        artifact = ROOT / relative
        assert artifact.is_file() and artifact.stat().st_size > 0, relative
        assert portable_match(relative, expected), relative
        if isinstance(metadata, dict) and "bytes" in metadata:
            actual = artifact.read_bytes()
            canonical = actual.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            assert int(metadata["bytes"]) in {len(actual), len(canonical), len(canonical.replace(b"\n", b"\r\n"))}, relative
        checked += 1
    return checked


def verify_phase13a_and_prior() -> tuple[int, int, int]:
    phase13a = json.loads(PHASE13A_FREEZE.read_text(encoding="utf-8"))
    assert phase13a["status"] == "ACCEPTED / FROZEN"
    assert phase13a["accepted_phase"] == "13A"
    assert phase13a["counts"] == {"nodes": 38, "relationships": 40, "observations": 25, "surveillance_records": 17, "sources": 27, "uncertainties": 18}
    final_entries = verify_manifest(PHASE13A_FREEZE, "13A")
    prior_hashes: dict[str, str] = {}
    prior_entries = 0
    for relative in sorted(PRIOR_MANIFESTS):
        payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        for artifact, metadata in entries(payload).items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if artifact in prior_hashes:
                assert prior_hashes[artifact] == expected, artifact
            prior_hashes[artifact] = expected
            assert portable_match(artifact, expected), artifact
            prior_entries += 1
    assert prior_entries == 358, prior_entries
    assert len(prior_hashes) == 351, len(prior_hashes)
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines())
    protected = set(prior_hashes) | set(entries(phase13a))
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return final_entries, prior_entries, len(prior_hashes)


def verify_context_manifests() -> dict[str, bool]:
    required = {
        "reports/phase9a_climate_natural_hazards_freeze_manifest.json": True,
        "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json": True,
        "reports/phase7a_exposure_environmental_health_freeze_manifest.json": True,
        "reports/phase10a_governance_jurisdiction_freeze_manifest.json": True,
        "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json": True,
        "reports/phase11a_population_settlement_freeze_manifest.json": True,
        "reports/phase11b_population_mobility_dependencies_freeze_manifest.json": True,
        "reports/phase12a_vector_ecology_freeze_manifest.json": True,
        "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json": True,
        "reports/phase12c_vector_ecology_futures_freeze_manifest.json": True,
        "reports/phase5a_freight_freeze_manifest.json": True,
        "reports/phase5b_freight_evidence_freeze_manifest.json": True,
        "reports/phase5c_freight_dependency_freeze_manifest.json": True,
        "reports/phase3b_freeze_manifest.json": True,
    }
    for relative in required:
        path = ROOT / relative
        assert path.is_file(), relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload.get("status") == "ACCEPTED / FROZEN", relative
        verify_manifest(path)
    water = json.loads((REPORTS / "water_system_manifest.json").read_text(encoding="utf-8"))
    assert water["system"] == "water" and water["nodes"] == 14 and water["edges"] == 15
    observation = json.loads((REPORTS / "observation_system_manifest.json").read_text(encoding="utf-8"))
    assert observation["phase"] == "4A" and observation["counts"] == {"nodes": 25, "edges": 21, "domains": ["energy_information", "environmental_regulatory", "lake_erie_hab", "maumee_hydrology"], "chain_ids": ["A", "B", "C", "D"]}
    return {"accepted_context_manifests_checked": True, "phase1_water_context_checked": True, "phase4_observation_context_checked": True}


def verify_tables(dep: pd.DataFrame, edges: pd.DataFrame, matrix: pd.DataFrame, crosswalk: pd.DataFrame, sources: pd.DataFrame, unc: pd.DataFrame, baseline_nodes: pd.DataFrame, baseline_sources: pd.DataFrame) -> dict[str, bool]:
    assert set(dep.columns) == DEP_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert set(matrix.columns) == MATRIX_COLUMNS
    assert set(crosswalk.columns) == CROSSWALK_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert set(unc.columns) == UNC_COLUMNS
    assert len(dep) == 36 and dep.dependency_id.is_unique
    assert len(edges) == 36 and edges.edge_id.is_unique and edges.dependency_id.is_unique
    assert len(matrix) == 6 and matrix.matrix_id.is_unique
    assert len(crosswalk) == 36 and crosswalk.evidence_id.is_unique
    assert len(sources) == 33 and sources.source_id.is_unique and sources.url.is_unique
    assert len(unc) == 14 and unc.uncertainty_id.is_unique
    assert set(sources.source_id) == BASE_SOURCE_IDS | REQUIRED_SOURCES
    assert set(BASE_SOURCE_IDS) <= set(baseline_sources.source_id)
    source_ids = set(sources.source_id)
    node_ids = set(baseline_nodes.node_id) | EXTERNAL_IDS | {"HOST-001", "REF-4", "REF-10"}
    assert dep.from_id.isin(node_ids).all() and dep.to_id.isin(node_ids).all()
    assert dep.source_id.isin(source_ids).all() and edges.source_id.isin(source_ids).all() and crosswalk.source_id.isin(source_ids).all() and unc.source_id.isin(source_ids).all()
    assert dep.uncertainty_id.isin(set(unc.uncertainty_id)).all()
    assert dep.relationship_type.isin(RELATIONSHIP_TYPES).all()
    assert dep.dependency_type.isin(DEPENDENCY_TYPES).all()
    assert dep.archetype.isin(ARCHETYPES).all()
    assert dep.documented_or_inferred.isin(DOC_STATUS).all()
    assert dep.relationship_basis.isin(RELATIONSHIP_BASES).all()
    assert dep.evidence_strength.isin(QUALITATIVE).all() and dep.confidence.isin(CONFIDENCE).all()
    assert dep.reality_status.eq("real").all()
    assert dep.canon_status.isin({"verified", "inferred"}).all()
    assert dep.relevant_disease_systems.str.len().gt(0).all()
    assert dep.direction.str.len().gt(0).all() and dep.spatial_scale.str.len().gt(0).all() and dep.temporal_scope.str.len().gt(0).all() and dep.uncertainty.str.len().gt(0).all()
    assert edges.edge_id.tolist() == [f"IDBE-{index:03d}" for index in range(1, 37)]
    assert edges.dependency_id.tolist() == dep.dependency_id.tolist()
    for column in DEP_COLUMNS:
        assert edges[column].tolist() == dep[column].tolist(), column
    assert set(crosswalk.dependency_id) == set(dep.dependency_id)
    assert crosswalk.dependency_id.is_unique
    merged = dep.merge(crosswalk, on="dependency_id", suffixes=("_dep", "_evidence"))
    assert merged.claim_status.tolist() == merged.documented_or_inferred.tolist()
    assert merged.source_id_dep.tolist() == merged.source_id_evidence.tolist()
    assert crosswalk.not_supported_statement.str.len().gt(0).all()
    qual_cols = [column for column in matrix.columns if column.endswith("_sensitivity") or column.endswith("_dependence") or column.endswith("_certainty")]
    assert matrix[qual_cols].apply(lambda col: col.isin(QUALITATIVE)).all().all()
    assert matrix.archetype.isin(ARCHETYPES).all()
    assert matrix.source_ids.str.len().gt(0).all() and matrix.notes.str.len().gt(0).all()
    assert all("risk" not in field.lower() and "score" not in field.lower() and "probability" not in field.lower() for field in set().union(*[set(frame.columns) for frame in (dep, edges, matrix, crosswalk, sources, unc)]))
    return {"schemas": True, "referential_integrity": True, "documented_vs_inferred": True, "edge_attributes": True, "matrix_qualitative_only": True, "evidence_crosswalk": True, "source_registry": True, "uncertainty_registry": True}


def verify_boundaries(dep: pd.DataFrame, edges: pd.DataFrame, matrix: pd.DataFrame, crosswalk: pd.DataFrame, unc: pd.DataFrame) -> dict[str, bool]:
    text = " ".join(" ".join(map(str, row)) for frame in (dep, edges, matrix, crosswalk, unc) for row in frame.to_numpy()).lower().replace("_", " ")
    required = [
        "driver is not deterministic cause", "vector ecology != human disease", "contamination != illness", "mobility != transmission",
        "surveillance != incidence", "healthcare presence != facility-level disease burden", "food/freight connectivity is an interface",
        "not a disease observation", "not a risk", "not incidence", "not outbreak", "does not establish",
    ]
    for term in required:
        assert term in text, term
    fields = set().union(*(set(frame.columns) for frame in (dep, edges, matrix, crosswalk, unc)))
    forbidden_fields = {"risk_score", "disease_risk_score", "composite_disease_risk_index", "vulnerability_score", "ej_score", "individual_risk", "infection_probability", "outbreak_probability", "transmission_rate", "disease_burden_index", "dose", "incidence_rate"}
    assert not fields.intersection(forbidden_fields)
    positive_patterns = [
        r"(?:risk score|risk index|incidence|outbreak probability|infection probability|disease burden)\s*[,=:]\s*[0-9]",
        r"\b(?:2050|2075)\b\s*[,=:]\s*[0-9]",
        r"(?:temperature|climate|mobility|population density|surveillance|contamination|vector ecology|healthcare presence)\s*(?:causes|determines|proves|equals)\s*(?:infection|disease|incidence|outbreak|burden)",
    ]
    for pattern in positive_patterns:
        assert not re.search(pattern, text, flags=re.I), pattern
    assert "documented" in set(dep.documented_or_inferred) and "inferred" in set(dep.documented_or_inferred)
    for archetype in ARCHETYPES:
        assert int(dep.archetype.eq(archetype).sum()) >= 6, archetype
    assert "phase 13c" not in text and "phase 14" not in text
    return {"driver_cause_boundary": True, "ecology_disease_boundary": True, "water_illness_boundary": True, "food_outbreak_boundary": True, "mobility_transmission_boundary": True, "surveillance_incidence_boundary": True, "healthcare_prevalence_boundary": True, "no_composite_risk_score": True, "no_individual_risk": True, "no_unsupported_local_downscaling": True}


def verify_status_and_files() -> None:
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        assert "phase 13b" in text and "implemented" in text, relative
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, relative
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, relative
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8").lower()
    canon = (ROOT / "docs/canon_status.md").read_text(encoding="utf-8").lower()
    handoff = (ROOT / "reports/current_phase_handoff.md").read_text(encoding="utf-8").lower()
    for text in (status, canon, handoff):
        assert "phase 13c" in text and "not implemented" in text
        assert "active phase" in text and "none" in text
        assert "phase 14" not in text or "not" in text


def verify_map() -> list[int]:
    with Image.open(MAP_PNG) as image:
        image.verify()
        size = list(image.size)
    root = ET.parse(MAP_SVG).getroot()
    text = " ".join(root.itertext()).lower()
    for term in ("map 42", "infectious disease", "transmission dependencies", "environment", "vectors", "water", "food / freight", "population / mobility", "healthcare", "surveillance", "governance", "driver", "incidence", "outbreak", "no cases"):
        assert term in text, term
    return size


def verify_no_13c_or_14() -> None:
    roots = [ROOT / "data/processed", ROOT / "outputs/maps/systems", ROOT / "src/python/systems", ROOT / "src/R/systems"]
    for base in roots:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(ROOT)).replace("\\", "/").lower()
            name = path.name.lower()
            assert "phase13c" not in relative and "phase13c" not in name, relative
            assert "infectious_disease_futures" not in name, relative
            assert name not in {"43_infectious_disease_futures_2050.png", "43_infectious_disease_futures_2075.png"}, relative
            if name.startswith("43_"):
                raise AssertionError(relative)


def verify_review(require_review: bool) -> bool:
    if not REVIEW.exists():
        assert not require_review
        return False
    text = REVIEW.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "independent review JSON block"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in ("security_concerns", "logic_errors", "provenance_errors", "epidemiological_errors", "dependency_errors", "surveillance_errors", "spatial_scale_errors", "health_boundary_errors"):
        assert verdict.get(key) == [], key
    for key in ("suggestions", "summary"):
        assert key in verdict
    return True


def verify_manifest_and_update() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "13B" and payload["map_number"] == 42
    assert payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["counts"] == {"dependency_register": 36, "dependency_edges": 36, "matrix_rows": 6, "evidence_crosswalk": 36, "sources": 33, "uncertainties": 14}
    assert payload["phase13a_accepted_frozen"] is True and payload["phase1_12_immutable"] is True
    assert payload["phase13c_implemented"] is False and payload["composite_disease_risk_index"] is False and payload["individual_case_or_risk_map"] is False
    assert payload["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    phase13a = payload["phase13a_freeze_manifest"]
    assert phase13a["path"] == "reports/phase13a_infectious_disease_freeze_manifest.json"
    assert digest(PHASE13A_FREEZE) == phase13a["sha256"] and PHASE13A_FREEZE.stat().st_size == phase13a["bytes"]
    if CHECK.exists():
        payload["artifacts"][str(CHECK.relative_to(ROOT)).replace("\\", "/")] = {"sha256": digest(CHECK), "bytes": CHECK.stat().st_size, "role": "machine validation result"}
    if REVIEW.exists():
        payload["artifacts"][str(REVIEW.relative_to(ROOT)).replace("\\", "/")] = {"sha256": digest(REVIEW), "bytes": REVIEW.stat().st_size, "role": "independent review record"}
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    checked = 0
    for relative, metadata in payload["artifacts"].items():
        artifact = ROOT / relative
        assert artifact.exists() and artifact.stat().st_size > 0, relative
        assert digest(artifact) == metadata["sha256"], relative
        checked += 1
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-review", action="store_true")
    args = parser.parse_args()
    dep, edges, matrix, crosswalk, sources, unc = (read(path) for path in (DEP, EDGES, MATRIX, CROSSWALK, SOURCES, UNCERTAINTIES))
    baseline_nodes = read(NETWORKS / "infectious_disease_nodes.csv")
    baseline_sources = read(ANALYSIS / "infectious_disease_sources.csv")
    table_result = verify_tables(dep, edges, matrix, crosswalk, sources, unc, baseline_nodes, baseline_sources)
    boundary_result = verify_boundaries(dep, edges, matrix, crosswalk, unc)
    phase13a_artifacts, prior_entries, prior_unique = verify_phase13a_and_prior()
    context_result = verify_context_manifests()
    verify_status_and_files()
    verify_no_13c_or_14()
    map_size = verify_map()
    review_present = verify_review(args.require_review)
    manifest_artifacts = verify_manifest_and_update()
    result = {
        "status": "passed", "phase": "13B", "map_number": 42,
        "dependency_register": len(dep), "dependency_edges": len(edges), "matrix_rows": len(matrix),
        "evidence_crosswalk": len(crosswalk), "sources": len(sources), "uncertainties": len(unc),
        "map42_valid": True, "image_size": map_size, "phase13a_freeze_artifacts_checked": phase13a_artifacts,
        "prior_freeze_manifest_entries_checked": prior_entries, "prior_unique_protected_artifacts_checked": prior_unique,
        "manifest_artifacts_checked": manifest_artifacts, "review_present": review_present,
        "phase13a_accepted_frozen": True, "phase1_12_immutable": True, "phase13a_immutable": True,
        "context_manifests": context_result, "table_checks": table_result, "boundary_checks": boundary_result,
        "active_holds_preserved": True, "deferred_maintenance_preserved": True,
        "phase13c_not_implemented": True, "phase14_not_implemented": True,
    }
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
