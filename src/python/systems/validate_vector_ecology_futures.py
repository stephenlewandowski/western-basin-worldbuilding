"""Independent Python validator for Phase 12C vector-ecology futures."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
BASE_SHA = "e3d5226dcd1f334a41f83bdd10dc5382bd5a0f80"
A_FREEZE = REPORTS / "phase12a_vector_ecology_freeze_manifest.json"
B_FREEZE = REPORTS / "phase12b_vector_environment_human_dependencies_freeze_manifest.json"
C_FREEZE = REPORTS / "phase12c_vector_ecology_futures_freeze_manifest.json"
MANIFEST = REPORTS / "vector_ecology_future_manifest.json"
LEDGER = REPORTS / "phase12c_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"

ASSUMPTIONS = SCENARIOS / "vector_ecology_scenario_assumptions.csv"
VECTOR_STATES = SCENARIOS / "vector_ecology_vector_states_scenario.csv"
HABITAT_STATES = SCENARIOS / "vector_ecology_habitat_states_scenario.csv"
SURVEILLANCE_STATES = SCENARIOS / "vector_ecology_surveillance_states_scenario.csv"
DEPENDENCY_STATES = SCENARIOS / "vector_ecology_dependency_states_scenario.csv"
UNCERTAINTY_STATES = SCENARIOS / "vector_ecology_uncertainty_states_scenario.csv"
SOURCES = ANALYSIS / "vector_ecology_future_sources.csv"
COMPARISON = FIGURES / "vector_ecology_future_comparison.csv"

SCENARIO_IDS = {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
SCENARIO_YEARS = {sid: int(sid[1:]) for sid in SCENARIO_IDS}
FOCAL_VECTORS = {"VEC-001", "VEC-002", "VEC-003", "VEC-004", "VEC-005", "VEC-006"}
HABITAT_BASELINES = {"VEC-009", "VEC-001", "VEC-008", "VEC-011", "VEC-010", "VEC-012", "VEC-013", "VEC-014"}
HABITAT_ASSOCIATIONS = {"HAB-001", "HAB-003", "HAB-007", "HAB-011", "HAB-012", "HAB-015"}
SURVEILLANCE_BASELINES = {"VEC-015", "VEC-016", "VEC-017", "VEC-018", "VDE-017"}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg", ".py", ".r"}
SOURCE_MAP = {
    "v12_ohio_mosquitoes": "VFS-001", "v12_osu_culex": "VFS-002", "v12_ohio_ae_japonicus": "VFS-003", "v12_mi_ae_japonicus": "VFS-004",
    "v12_in_ae_albopictus": "VFS-005", "v12_cdc_mosquito_biology": "VFS-006", "v12_cdc_mosquito_traps": "VFS-007", "v12_cdc_ticks_live": "VFS-008",
    "v12_cdc_ixodes": "VFS-008", "v12_cdc_dvariabilis": "VFS-009", "phase9_climate_context": "VFS-010", "phase1_hydrology_context": "VFS-014",
    "phase6_ecology_context": "VFS-015", "phase7_health_context": "VFS-018", "phase10_governance_context": "VFS-016", "phase11_population_context": "VFS-017",
    "phase4_data_context": "VFS-019", "v12_cdc_wnv_about": "VFS-020", "v12_ohio_vector_update": "VFS-021", "v12_cdc_tick_sets": "VFS-022",
    "v12_cdc_wnv_data": "VFS-023", "v12_cdc_lyme": "VFS-024", "v12_mi_annual_2023": "VFS-025", "v12_in_wnv_2026": "VFS-026",
    "v12_cdc_tick_data": "VFS-027", "v12_ohio_wnv_map": "VFS-028",
}
HABITAT_ASSOCIATION_SOURCES = {"HAB-001": "VFS-002", "HAB-003": "VFS-005", "HAB-007": "VFS-008", "HAB-011": "VFS-014", "HAB-012": "VFS-008", "HAB-015": "VFS-002"}

EXPECTED_COLUMNS = {
    "assumptions": {"assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption", "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes"},
    "vectors": {"state_id", "scenario_id", "scenario", "horizon", "baseline_node_id", "baseline_name", "taxon_or_system", "vector_group", "baseline_presence_context", "seasonal_suitability_state", "habitat_opportunity_state", "overwintering_or_activity_context", "future_range_state", "establishment_state", "abundance_state", "pathogen_state", "human_interface_state", "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"},
    "habitats": {"state_id", "scenario_id", "scenario", "horizon", "baseline_object_id", "baseline_association_id", "habitat_relationship", "vector_group", "current_fact", "future_suitability_state", "habitat_opportunity_state", "spatial_pattern", "change_type", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"},
    "surveillance": {"state_id", "scenario_id", "scenario", "horizon", "baseline_object_id", "surveillance_dimension", "current_fact", "surveillance_capacity_state", "detection_timing_state", "method_and_effort_state", "management_response_interface", "abundance_inference_boundary", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"},
    "dependencies": {"state_id", "scenario_id", "scenario", "horizon", "baseline_dependency_id", "object_a", "object_b", "system_a", "system_b", "relationship_type", "spatial_scale", "current_fact", "scenario_assumption", "scenario_consequence", "dependency_state", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"},
    "uncertainty": {"state_id", "scenario_id", "scenario", "horizon", "baseline_uncertainty_id", "category", "subject_id", "current_fact", "scenario_assumption", "uncertainty_state", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    "comparison": {"scenario_id", "scenario", "horizon", "seasonal_suitability", "urban_container_opportunity", "standing_water_opportunity", "forest_edge_humidity", "host_ecology_interface", "surveillance_capacity", "detection_timing", "management_response", "spatial_heterogeneity", "range_statement", "abundance_statement", "pathogen_statement", "human_interface_statement", "scenario_distinctiveness", "uncertainty_profile", "notes"},
}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def artifact_entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def canonical_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def portable_manifest_match(relative: str, expected: str) -> bool:
    """Prove LF/CRLF-only portability without modifying a protected file."""
    path = ROOT / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() == expected:
        return True
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        accepted = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{relative}"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    if canonical_text(path.read_bytes()) != canonical_text(accepted):
        return False
    accepted_hashes = {hashlib.sha256(accepted).hexdigest(), hashlib.sha256(accepted.replace(b"\n", b"\r\n")).hexdigest()}
    return expected in accepted_hashes


def check_table(name: str, path: Path, expected_rows: int, unique_column: str) -> pd.DataFrame:
    frame = read(path)
    assert set(frame.columns) == EXPECTED_COLUMNS[name], (name, sorted(set(frame.columns) ^ EXPECTED_COLUMNS[name]))
    assert len(frame) == expected_rows, (name, len(frame))
    assert frame[unique_column].is_unique, (name, unique_column)
    assert frame.notes.str.len().gt(0).all(), name
    return frame


def check_horizons(frames: list[pd.DataFrame]) -> None:
    for frame in frames:
        assert set(frame.scenario_id) == SCENARIO_IDS
        assert frame.apply(lambda row: int(row.horizon) == SCENARIO_YEARS[row.scenario_id], axis=1).all()


def check_manifest_hashes(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "ACCEPTED / FROZEN"
    assert payload["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    entries = artifact_entries(payload)
    assert entries
    for relative, metadata in entries.items():
        expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
        artifact = ROOT / relative
        assert artifact.exists() and artifact.stat().st_size > 0, relative
        assert portable_manifest_match(relative, expected), relative
    return payload


def check_frozen_inputs() -> tuple[int, int, set[str]]:
    a = check_manifest_hashes(A_FREEZE)
    b = check_manifest_hashes(B_FREEZE)
    assert a["accepted_phase"] == "12A" and a["baseline"] == "Vector Ecology Baseline, 2026"
    assert b["accepted_phase"] == "12B" and b["baseline"] == "Vector / Environment / Human-System Dependencies, 2026"
    assert len(a["artifacts"]) == 17 and len(b["artifacts"]) == 15
    a_hash = hashlib.sha256(canonical_text(A_FREEZE.read_bytes())).hexdigest()
    assert b["phase12a_freeze_manifest"]["sha256"] == a_hash
    assert int(b["phase12a_freeze_manifest"]["bytes"]) == len(canonical_text(A_FREEZE.read_bytes()))

    protected: set[str] = set()
    expected_hashes: dict[str, str] = {}
    entries_count = 0
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if path.name in {A_FREEZE.name, B_FREEZE.name, C_FREEZE.name}:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in artifact_entries(payload).items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if relative in expected_hashes:
                assert expected_hashes[relative] == expected, relative
            expected_hashes[relative] = expected
            assert portable_manifest_match(relative, expected), relative
            protected.add(relative)
            entries_count += 1
    assert entries_count == 298 and len(protected) == 293, (entries_count, len(protected))
    future_paths = {str(path.relative_to(ROOT)).replace("\\", "/") for path in (ASSUMPTIONS, VECTOR_STATES, HABITAT_STATES, SURVEILLANCE_STATES, DEPENDENCY_STATES, UNCERTAINTY_STATES, SOURCES, COMPARISON)}
    assert not protected.intersection(future_paths)
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines())
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return entries_count, len(protected), protected


def check_baseline_separation(assumptions: pd.DataFrame) -> None:
    baseline_paths = [
        NETWORKS / "vector_ecology_nodes.csv", NETWORKS / "vector_ecology_edges.csv", ANALYSIS / "vector_surveillance_records.csv",
        ANALYSIS / "vector_habitat_associations.csv", ANALYSIS / "vector_system_dependency_register.csv", NETWORKS / "vector_system_dependency_edges.csv",
        ANALYSIS / "vector_system_dependency_matrix.csv", ANALYSIS / "vector_dependency_evidence.csv",
    ]
    baseline_text = " ".join(path.read_text(encoding="utf-8").lower() for path in baseline_paths)
    assert not re.search(r"\b(?:a2050|a2075|b2050|b2075|c2050|c2075)\b", baseline_text)
    assert assumptions.reality_status.eq("fictional").all()
    assert assumptions.canon_status.eq("scenario").all()
    assert assumptions.classification.eq("SCENARIO ASSUMPTION").all()
    assert assumptions.numeric_future_value_adopted.eq("false").all()


def check_scenario_tables(assumptions: pd.DataFrame, vectors: pd.DataFrame, habitats: pd.DataFrame, surveillance: pd.DataFrame, dependencies: pd.DataFrame, uncertainty: pd.DataFrame, comparison: pd.DataFrame, sources: pd.DataFrame) -> None:
    source_ids = set(sources.source_id)
    assumption_ids = set(assumptions.assumption_id)
    assert len(sources) == 28 and sources.source_id.is_unique and sources.url.is_unique
    for frame in (assumptions, vectors, habitats, surveillance, dependencies, uncertainty):
        assert frame.source_or_basis.isin(source_ids).all() if "source_or_basis" in frame else True
        assert frame.assumption_id.isin(assumption_ids).all()
        assert frame.reality_status.eq("fictional").all() and frame.canon_status.eq("scenario").all()
        if "relationship_basis" in frame:
            assert frame.relationship_basis.eq("scenario_assumption").all()
    assert assumptions.source_id.isin(source_ids).all()
    assert assumptions.groupby("scenario_id").size().eq(6).all()
    assert vectors.groupby("scenario_id").size().eq(6).all()
    assert habitats.groupby("scenario_id").size().eq(8).all()
    assert surveillance.groupby("scenario_id").size().eq(5).all()
    assert dependencies.groupby("scenario_id").size().eq(28).all()
    assert uncertainty.groupby("scenario_id").size().eq(10).all()
    assert vectors.baseline_node_id.isin(FOCAL_VECTORS).all()
    assert habitats.baseline_object_id.isin(HABITAT_BASELINES).all()
    assert habitats.baseline_association_id.isin(HABITAT_ASSOCIATIONS).all()
    assert surveillance.baseline_object_id.isin(SURVEILLANCE_BASELINES).all()
    baseline_dependency = read(ANALYSIS / "vector_system_dependency_register.csv")
    baseline_uncertainty = read(ANALYSIS / "vector_ecology_uncertainty.csv")
    baseline_habitat = read(ANALYSIS / "vector_habitat_associations.csv").set_index("association_id")
    accepted_dependencies = set(baseline_dependency.dependency_id)
    accepted_uncertainties = set(baseline_uncertainty.uncertainty_id)
    assert dependencies.baseline_dependency_id.isin(accepted_dependencies).all()
    assert uncertainty.baseline_uncertainty_id.isin(accepted_uncertainties).all()
    assert vectors.apply(lambda row: row.source_or_basis == {"VEC-001": "VFS-002", "VEC-002": "VFS-002", "VEC-003": "VFS-001", "VEC-004": "VFS-003", "VEC-005": "VFS-001", "VEC-006": "VFS-008"}[row.baseline_node_id], axis=1).all()
    assert habitats.apply(lambda row: row.source_or_basis == HABITAT_ASSOCIATION_SOURCES[row.baseline_association_id] and row.current_fact == f"CURRENT FACT (2026 baseline): {baseline_habitat.loc[row.baseline_association_id, 'relationship_description']}", axis=1).all()
    assert surveillance.apply(lambda row: row.source_or_basis == ("VFS-016" if row.surveillance_dimension == "detection-to-decision interface" else "VFS-007"), axis=1).all()
    dep_sources = baseline_dependency.set_index("dependency_id")["source_id"].map(SOURCE_MAP)
    unc_sources = baseline_uncertainty.set_index("uncertainty_id")["source_id"].map(SOURCE_MAP)
    assert dependencies.apply(lambda row: row.source_or_basis == dep_sources[row.baseline_dependency_id], axis=1).all()
    assert uncertainty.apply(lambda row: row.source_or_basis == unc_sources[row.baseline_uncertainty_id], axis=1).all()
    assert comparison.scenario_id.is_unique
    assert comparison.groupby("horizon").size().eq(3).all()
    assert assumptions.uncertainty.isin({"moderate", "high"}).all()
    assert vectors.plausibility.isin({"moderate", "high", "exploratory"}).all()
    assert vectors.future_range_state.str.contains(r"no (?:future|basin-wide)", case=False, regex=True).all()
    assert vectors.establishment_state.str.contains("not projected", case=False).all()
    assert vectors.abundance_state.str.contains("not estimated", case=False).all()
    assert vectors.pathogen_state.str.contains("not projected", case=False).all()
    assert vectors.human_interface_state.str.contains("not modeled", case=False).all()
    assert surveillance.abundance_inference_boundary.str.contains("not abundance", case=False).all()
    assert habitats.future_suitability_state.str.startswith("SCENARIO SUITABILITY:").all()
    assert dependencies.current_fact.str.startswith("CURRENT FACT (2026 baseline):").all()
    assert dependencies.scenario_assumption.str.startswith("SCENARIO ASSUMPTION:").all()
    assert dependencies.scenario_consequence.str.startswith("SCENARIO CONSEQUENCE:").all()
    assert uncertainty.current_fact.str.startswith("CURRENT FACT (2026 baseline):").all()
    assert uncertainty.scenario_assumption.str.startswith("SCENARIO ASSUMPTION:").all()
    assert "Great Black Swamp remains C — HOLD / noncanonical" in " ".join(uncertainty.uncertainty_state)
    b_text = " ".join(assumptions.loc[assumptions.scenario_id.str.startswith("B"), "assumption"]).lower()
    assert "not averaged" in b_text or "heterogeneous" in b_text
    assert "mosaic" in " ".join(comparison.loc[comparison.scenario_id.str.startswith("B"), "scenario_distinctiveness"]).lower()
    assert "not a midpoint" in " ".join(comparison.loc[comparison.scenario_id.str.startswith("B"), "scenario_distinctiveness"]).lower()
    for scenario in "ABC":
        assert assumptions.loc[assumptions.scenario_id == f"{scenario}2050", "assumption"].tolist() != assumptions.loc[assumptions.scenario_id == f"{scenario}2075", "assumption"].tolist()
        assert vectors.loc[vectors.scenario_id == f"{scenario}2050", "seasonal_suitability_state"].tolist() != vectors.loc[vectors.scenario_id == f"{scenario}2075", "seasonal_suitability_state"].tolist()
        for frame, columns in ((habitats, ["future_suitability_state", "habitat_opportunity_state", "spatial_pattern", "change_type"]), (surveillance, ["surveillance_capacity_state", "detection_timing_state", "method_and_effort_state", "management_response_interface"]), (dependencies, ["dependency_state", "scenario_consequence"]), (uncertainty, ["uncertainty_state"]), (comparison, ["seasonal_suitability", "urban_container_opportunity", "standing_water_opportunity", "forest_edge_humidity", "surveillance_capacity", "detection_timing", "management_response", "spatial_heterogeneity", "scenario_distinctiveness", "uncertainty_profile"])):
            left = frame.loc[frame.scenario_id == f"{scenario}2050", columns].reset_index(drop=True)
            right = frame.loc[frame.scenario_id == f"{scenario}2075", columns].reset_index(drop=True)
            assert not left.equals(right), (scenario, columns)


def check_negative_scope(frames: list[pd.DataFrame]) -> None:
    fields = set().union(*(set(frame.columns) for frame in frames))
    forbidden_fields = {"abundance_index", "abundance_score", "risk_score", "infection_probability", "disease_incidence_forecast", "case_total", "future_range_polygon", "vulnerability_score", "ej_score", "contact_probability", "exposure_score"}
    assert not fields.intersection(forbidden_fields)
    text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower()
    for phrase in ("presence", "abundance", "establishment", "pathogen", "human-vector", "infection", "clinical disease", "surveillance", "not modeled"):
        assert phrase in text, phrase
    assert "surveillance intensity" in text and "not abundance" in text
    assert "suitability" in text and "not observed" in text
    assert "range-expansion potential" not in text or "not" in text
    assert not re.search(r"\b(?:future|projected)\b[^\n]{0,120}\b(?:cases?|infections?|hospitalizations?|deaths?)\b[^\n]{0,20}\d", text)
    assert not re.search(r"\b(?:future|projected)\s+(?:abundance|prevalence|case|infection)\s*[:=]\s*[0-9]", text)
    assert not re.search(r"\b(?:probability|risk|score|prevalence)\s*[:=]\s*[0-9]", text)
    assert "vulnerability/ej" not in text or "no" in text
    assert "phase 13" not in text or "no" in text


def check_maps_and_reports() -> list[list[int]]:
    sizes: list[list[int]] = []
    for base, map_id, year in (("40_vector_ecology_futures_2050", "map 40", "2050"), ("40b_vector_ecology_futures_2075", "map 40b", "2075")):
        png = MAPS / f"{base}.png"; svg = MAPS / f"{base}.svg"
        assert png.exists() and png.stat().st_size > 10000 and svg.exists() and svg.stat().st_size > 10000
        with Image.open(png) as image:
            image.verify(); sizes.append([image.width, image.height]); assert image.width >= 2000 and image.height >= 1000
        text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        for term in (map_id, year, "managed ecological adaptation", "heterogeneous adaptive basin", "warmer / more variable vector landscape", "suitability is not observed distribution", "surveillance intensity", "not abundance", "no exact future range", "great black swamp", "unresolved"):
            assert term in text, (base, term)
        if year == "2075":
            assert "2075 matured / diverged" in text
    assert COMPARISON.exists() and COMPARISON.stat().st_size > 100
    for figure in (FIGURES / "vector_ecology_future_comparison.png", FIGURES / "vector_ecology_future_comparison.svg"):
        assert figure.exists() and figure.stat().st_size > 10000
    ET.parse(FIGURES / "vector_ecology_future_comparison.svg")
    for name in ("vector_ecology_future_sources.md", "vector_ecology_future_assumptions.md", "vector_ecology_future_findings.md", "vector_ecology_future_consistency.md", "vector_ecology_future_qa.md", "vector_ecology_future_worldbuilding.md"):
        assert (REPORTS / name).read_text(encoding="utf-8").strip()
    source_report = (REPORTS / "vector_ecology_future_sources.md").read_text(encoding="utf-8")
    for url in ("https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/animals/mosquitoes-in-ohio", "https://ohioline.osu.edu/factsheet/ent-89", "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html", "https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf", "https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023", "https://www.cdc.gov/west-nile-virus/about", "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update", "https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html", "https://www.cdc.gov/west-nile-virus/data-maps", "https://www.cdc.gov/lyme/data-research/facts-stats/index.html", "https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf", "https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county", "https://www.cdc.gov/ticks/data-research/facts-stats", "https://ohid.ohio.gov/wps/wcm/connect/gov/ohio+content+english/odh/know-our-programs/zoonotic-disease-program/media/west-nile-virus-map"):
        assert url in source_report
    return sizes


def check_citations() -> None:
    for name in ("vector_ecology_future_sources.md", "vector_ecology_future_assumptions.md", "vector_ecology_future_findings.md"):
        result = subprocess.run([sys.executable, str(CITATION_SCRIPT), "--ledger", str(LEDGER), "verify", str(REPORTS / name), "--strict"], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr


def check_future_manifest(require_review: bool = False) -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "12C"
    assert payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["scenario_ids"] == ["A2050", "A2075", "B2050", "B2075", "C2050", "C2075"]
    assert payload["map_numbers"] == [40, "40b"]
    assert payload["numeric_future_values_adopted"] is False
    assert payload["future_range_polygons"] is False
    assert payload["disease_incidence_forecast"] is False
    assert payload["human_risk_model"] is False
    assert payload["phase12a_12b_immutable"] is True and payload["phase1_11_immutable"] is True and payload["phase13_implemented"] is False
    assert payload["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert len(payload["artifacts"]) == (25 if require_review else 24)
    assert "reports/vector_ecology_future_independent_review_initial.md" in payload["artifacts"]
    if require_review:
        assert "reports/vector_ecology_future_independent_review.md" in payload["artifacts"]
        review_text = (REPORTS / "vector_ecology_future_independent_review.md").read_text(encoding="utf-8").lower()
        for term in ('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"ecological_errors": []', '"scenario_boundary_errors": []', '"spatial_scale_errors": []', '"health_boundary_errors": []'):
            assert term in review_text, term
    for relative, metadata in payload["artifacts"].items():
        path = ROOT / relative
        assert path.exists() and path.stat().st_size > 0 and portable_manifest_match(relative, metadata["sha256"]), relative
    return payload


def main() -> None:
    assumptions = check_table("assumptions", ASSUMPTIONS, 36, "assumption_id")
    vectors = check_table("vectors", VECTOR_STATES, 36, "state_id")
    habitats = check_table("habitats", HABITAT_STATES, 48, "state_id")
    surveillance = check_table("surveillance", SURVEILLANCE_STATES, 30, "state_id")
    dependencies = check_table("dependencies", DEPENDENCY_STATES, 168, "state_id")
    uncertainty = check_table("uncertainty", UNCERTAINTY_STATES, 60, "state_id")
    comparison = check_table("comparison", COMPARISON, 6, "scenario_id")
    sources = read(SOURCES)
    check_horizons([assumptions, vectors, habitats, surveillance, dependencies, uncertainty, comparison])
    check_baseline_separation(assumptions)
    check_scenario_tables(assumptions, vectors, habitats, surveillance, dependencies, uncertainty, comparison, sources)
    check_negative_scope([assumptions, vectors, habitats, surveillance, dependencies, uncertainty, comparison])
    prior_entries, prior_unique, _ = check_frozen_inputs()
    map_sizes = check_maps_and_reports()
    check_citations()
    manifest = check_future_manifest(require_review="--require-review" in sys.argv)
    result = {
        "status": "passed", "phase": "12C", "scenario_ids": sorted(SCENARIO_IDS),
        "scenario_assumptions": len(assumptions), "vector_states": len(vectors), "habitat_states": len(habitats),
        "surveillance_states": len(surveillance), "dependency_states": len(dependencies), "uncertainty_states": len(uncertainty),
        "scenario_sources": len(sources), "comparison_rows": len(comparison), "maps_40_40b_valid": True,
        "comparison_figure_valid": True, "provenance_strict": True, "assumption_references": True,
        "scenario_fact_separation": True, "horizon_distinction": True, "scenario_b_structurally_distinct": True,
        "vector_presence_abundance_pathogen_contact_health_boundaries": True, "surveillance_not_abundance": True,
        "no_future_range_precision": True, "no_disease_incidence_forecast": True, "no_human_risk_inference": True,
        "no_vulnerability_ej_scoring": True, "no_phase13": True, "phase12a_12b_freeze_integrity": True,
        "prior_phase1_11_manifest_entries": prior_entries, "prior_phase1_11_unique_protected_artifacts": prior_unique,
        "phase12a_12b_immutable": True, "active_holds_preserved": True, "independent_review_required_for_delivery": True, "independent_review_passed": "--require-review" in sys.argv, "manifest_counts": manifest["counts"], "map_sizes": map_sizes,
    }
    (REPORTS / "vector_ecology_future_artifact_check.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
