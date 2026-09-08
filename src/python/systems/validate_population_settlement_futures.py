"""Independent Python validator for Phase 11C population/settlement futures."""
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

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIO_DIR = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
MANIFEST = REPORTS / "population_settlement_future_manifest.json"
A_MANIFEST = REPORTS / "phase11a_population_settlement_freeze_manifest.json"
B_MANIFEST = REPORTS / "phase11b_population_mobility_dependencies_freeze_manifest.json"

SCENARIO_IDS = {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
SCENARIO_YEARS = {sid: int(sid[1:]) for sid in SCENARIO_IDS}

ASSUMPTIONS = SCENARIO_DIR / "population_settlement_scenario_assumptions.csv"
PROJECTION = SCENARIO_DIR / "population_settlement_projection_evidence.csv"
STATES = SCENARIO_DIR / "population_settlement_future_states.csv"
RELATIONSHIPS = NETWORKS / "population_settlement_future_relationships.csv"
UNCERTAINTY = SCENARIO_DIR / "population_settlement_future_uncertainty.csv"
SOURCES = ANALYSIS / "population_settlement_future_sources.csv"
COMPARISON = FIGURES / "population_settlement_future_comparison.csv"

EXPECTED_COLUMNS = {
    "assumptions": {"assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption", "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes"},
    "projection": {"evidence_id", "jurisdiction", "geographic_scale", "projection_horizon", "source_id", "projection_status", "availability_at_scale", "adopted_use", "numeric_value_adopted", "uncertainty", "notes"},
    "states": {"state_id", "scenario_id", "scenario", "horizon", "baseline_node_id", "baseline_name", "baseline_geographic_scale", "baseline_settlement_class", "current_fact", "population_distribution_state", "settlement_form_state", "housing_form_state", "employment_geography_state", "mobility_interface_state", "service_dependency_state", "projection_relation", "climate_migration_role", "assumption_id", "source_or_basis", "plausibility", "reality_status", "canon_status", "relationship_basis", "numeric_future_value_adopted", "notes"},
    "relationships": {"relationship_id", "scenario_id", "scenario", "horizon", "source_node_id", "target_node_id", "relationship_type", "spatial_scale", "current_fact", "scenario_assumption", "scenario_consequence", "commuting_migration_boundary", "source_or_basis", "assumption_id", "evidence_strength", "reality_status", "canon_status", "relationship_basis", "numeric_future_value_adopted", "notes"},
    "uncertainty": {"uncertainty_id", "scenario_id", "scenario", "horizon", "category", "subject", "current_fact", "scenario_assumption", "uncertainty_state", "source_or_basis", "assumption_id", "reality_status", "canon_status", "notes"},
    "comparison": {"scenario_id", "scenario", "horizon", "population_distribution", "settlement_concentration", "settlement_form", "housing_form", "employment_geography", "mobility_interface", "climate_migration_role", "service_dependence", "projection_use", "uncertainty_profile", "notes"},
}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_table(name: str, path: Path, expected_rows: int, unique_column: str) -> pd.DataFrame:
    frame = read(path)
    assert set(frame.columns) == EXPECTED_COLUMNS[name], (name, sorted(set(frame.columns) ^ EXPECTED_COLUMNS[name]))
    assert len(frame) == expected_rows, (name, len(frame))
    assert frame[unique_column].is_unique, unique_column
    assert frame.notes.str.len().gt(0).all(), name
    return frame


def check_scenario_horizons(frame: pd.DataFrame) -> None:
    assert set(frame.scenario_id) == SCENARIO_IDS
    assert frame.apply(lambda row: int(row.horizon) == SCENARIO_YEARS[row.scenario_id], axis=1).all()


def check_protected_manifests() -> dict[str, int]:
    counts = {}
    for path in (A_MANIFEST, B_MANIFEST):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["status"] == "ACCEPTED / FROZEN"
        assert payload["phase11c_implemented"] is False
        for rel, meta in payload["artifacts"].items():
            assert (ROOT / rel).exists() and manifest_matches(ROOT, rel, str(meta["sha256"])), rel
        counts[path.name] = len(payload["artifacts"])
    b = json.loads(B_MANIFEST.read_text(encoding="utf-8"))
    raw = A_MANIFEST.read_bytes()
    canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    portable_sizes = {len(raw), len(canonical), len(canonical.replace(b"\n", b"\r\n"))}
    assert manifest_matches(ROOT, "reports/phase11a_population_settlement_freeze_manifest.json", str(b["phase11a_freeze_manifest"]["sha256"]))
    assert int(b["phase11a_freeze_manifest"]["bytes"]) in portable_sizes
    return counts


def run_prior_freeze_validator() -> None:
    result = subprocess.run([sys.executable, "src/python/systems/validate_phase11_freezes.py"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "passed"' in result.stdout
    assert '"prior_phase1_9_protected_artifacts": 196' in result.stdout


def check_baseline_separation(assumptions: pd.DataFrame, sources: pd.DataFrame) -> None:
    baseline_text = " ".join(
        path.read_text(encoding="utf-8").lower()
        for path in (
            ANALYSIS / "population_settlement_nodes.csv",
            ANALYSIS / "population_settlement_observations.csv",
            NETWORKS / "population_settlement_relationships.csv",
            ANALYSIS / "population_mobility_observations.csv",
            NETWORKS / "population_mobility_relationships.csv",
            ANALYSIS / "population_system_dependency_register.csv",
            ANALYSIS / "population_system_dependency_matrix.csv",
        )
    )
    assert not re.search(r"\b(?:a2050|a2075|b2050|b2075|c2050|c2075)\b", baseline_text)
    assert set(assumptions.source_id).issubset(set(sources.source_id))
    assert assumptions.reality_status.eq("fictional").all()
    assert assumptions.canon_status.eq("scenario").all()
    assert assumptions.classification.eq("SCENARIO ASSUMPTION").all()
    assert assumptions.numeric_future_value_adopted.eq("false").all()


def check_boundaries(assumptions: pd.DataFrame, states: pd.DataFrame, relationships: pd.DataFrame, uncertainty: pd.DataFrame, comparison: pd.DataFrame) -> None:
    frames = [assumptions, states, relationships, uncertainty, comparison]
    all_text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower()
    forbidden_columns = {"population_2050", "population_2075", "households_2050", "housing_units_2050", "worker_2050", "job_2050", "commuter_2050", "migration_2050", "vulnerability_score", "ej_score", "protected_class_rank", "risk_score", "dose", "illness", "mortality"}
    assert not forbidden_columns.intersection(set().union(*(set(frame.columns) for frame in frames)))
    assert not re.search(r"\b(?:partisan|election|candidate|voter|party control|ideological)\b", all_text)
    assert "commuting is not migration" in all_text
    assert "population" in all_text and "household" in all_text and "housing unit" in all_text and "worker" in all_text and "job" in all_text and "commuter" in all_text
    assert "high-uncertainty scenario mechanism" in all_text
    assert "not a population-growth assumption" in all_text
    assert "no individual" in all_text
    assert "utility service territories" in all_text or "utility territory" in all_text
    assert "vulnerability" in all_text and "protected-class" in all_text
    assert "not aggregated" in all_text or "not a" in all_text
    assert states.numeric_future_value_adopted.eq("false").all()
    assert relationships.numeric_future_value_adopted.eq("false").all()
    assert states.reality_status.eq("fictional").all() and states.canon_status.eq("scenario").all()
    assert relationships.reality_status.eq("fictional").all() and relationships.canon_status.eq("scenario").all()
    assert uncertainty.reality_status.eq("fictional").all() and uncertainty.canon_status.eq("scenario").all()


def check_horizon_distinction(assumptions: pd.DataFrame, states: pd.DataFrame, comparison: pd.DataFrame) -> None:
    for scenario in "ABC":
        a2050 = assumptions[assumptions.scenario_id == f"{scenario}2050"].assumption.tolist()
        a2075 = assumptions[assumptions.scenario_id == f"{scenario}2075"].assumption.tolist()
        s2050 = states[states.scenario_id == f"{scenario}2050"].population_distribution_state.tolist()
        s2075 = states[states.scenario_id == f"{scenario}2075"].population_distribution_state.tolist()
        assert a2050 != a2075
        assert s2050 != s2075
    assert comparison.scenario_id.is_unique
    assert set(comparison.scenario) == {"Connected Reconcentration", "Polycentric Adaptive Basin", "Uneven Change / Infrastructure Strain"}
    assert comparison[comparison.horizon == "2050"].projection_use.str.contains("official 2050 county projection evidence available").all()
    assert comparison[comparison.horizon == "2075"].projection_use.str.contains("explicit scenario only").all()
    assert assumptions[assumptions.scenario_id.str.startswith("B")].assumption.str.contains("Polycentric Adaptive Basin").all()


def check_maps_and_reports() -> None:
    for base, map_id, horizon in (("37_population_settlement_futures_2050", "map 37", "2050"), ("37b_population_settlement_futures_2075", "map 37b", "2075")):
        png = MAPS / f"{base}.png"
        svg = MAPS / f"{base}.svg"
        assert png.exists() and png.stat().st_size > 10000
        assert svg.exists() and svg.stat().st_size > 10000
        with Image.open(png) as image:
            image.verify()
            assert image.width >= 2000 and image.height >= 1000
        text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        for term in (map_id, horizon, "population", "settlement", "connected reconcentration", "polycentric adaptive basin", "uneven change / infrastructure strain", "not population totals", "climate migration", "commuting ≠ migration", "great black swamp", "unresolved"):
            assert term in text, (base, term)
    assert COMPARISON.exists() and COMPARISON.stat().st_size > 100
    for path in (FIGURES / "population_settlement_future_comparison.png", FIGURES / "population_settlement_future_comparison.svg"):
        assert path.exists() and path.stat().st_size > 10000
    ET.parse(FIGURES / "population_settlement_future_comparison.svg")
    for name in ("population_settlement_future_sources.md", "population_settlement_future_assumptions.md", "population_settlement_future_findings.md", "population_settlement_future_qa.md"):
        text = (REPORTS / name).read_text(encoding="utf-8").lower()
        assert text.strip() and "phase 11c" in text
    source_report = (REPORTS / "population_settlement_future_sources.md").read_text(encoding="utf-8")
    for url in ("https://www.census.gov/programs-surveys/popproj.html", "https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html", "https://www.census.gov/programs-surveys/popest.html", "https://development.ohio.gov/about-us/research/population/population-projections/pop-projection-overview-2020-2050", "https://www.michigan.gov/mcda/insights/2025/03/06/mich-county-popproj-2050", "https://www.stats.indiana.edu/pop_proj/default.html", "https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts"):
        assert url in source_report


def check_manifest() -> dict[str, object]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "11C"
    assert payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["scenario_ids"] == ["A2050", "A2075", "B2050", "B2075", "C2050", "C2075"]
    assert payload["numeric_future_values_adopted"] is False
    assert payload["climate_migration_as_growth_assumption"] is False
    assert payload["phase12_implemented"] is False
    assert payload["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    for rel, meta in payload["artifacts"].items():
        path = ROOT / rel
        assert path.exists() and path.stat().st_size > 0 and digest(path) == meta["sha256"]
    return payload["counts"]


def main() -> None:
    assumptions = check_table("assumptions", ASSUMPTIONS, 36, "assumption_id")
    projection = check_table("projection", PROJECTION, 6, "evidence_id")
    states = check_table("states", STATES, 108, "state_id")
    relationships = check_table("relationships", RELATIONSHIPS, 108, "relationship_id")
    uncertainty = check_table("uncertainty", UNCERTAINTY, 36, "uncertainty_id")
    comparison = check_table("comparison", COMPARISON, 6, "scenario_id")
    sources = read(SOURCES)
    nodes = read(ANALYSIS / "population_settlement_nodes.csv")
    assert len(sources) == 11 and sources.source_id.is_unique
    assert len(nodes[nodes.node_type == "population_zone"]) == 18
    check_scenario_horizons(assumptions)
    check_scenario_horizons(states)
    check_scenario_horizons(relationships)
    check_scenario_horizons(uncertainty)
    check_scenario_horizons(comparison)
    assert projection.numeric_value_adopted.eq("false").all()
    assert projection.source_id.isin(set(sources.source_id)).all()
    assert states.baseline_node_id.isin(set(nodes.node_id)).all()
    assert states.baseline_geographic_scale.eq("county").all()
    assert states.groupby("scenario_id").size().eq(18).all()
    assert relationships.source_node_id.isin(set(nodes.node_id)).all() and relationships.target_node_id.isin(set(nodes.node_id)).all()
    assert relationships.source_node_id.ne(relationships.target_node_id).all()
    assert relationships.groupby("scenario_id").size().eq(18).all()
    assert relationships.spatial_scale.eq("county_pair").all()
    assert uncertainty.groupby("scenario_id").size().eq(6).all()
    assert set(assumptions.domain) == {"population_distribution", "settlement_form", "housing_form", "employment_geography", "mobility_and_migration_boundary", "infrastructure_service_dependence"}
    check_baseline_separation(assumptions, sources)
    check_boundaries(assumptions, states, relationships, uncertainty, comparison)
    check_horizon_distinction(assumptions, states, comparison)
    check_maps_and_reports()
    frozen = check_protected_manifests()
    run_prior_freeze_validator()
    manifest_counts = check_manifest()
    result = {
        "status": "passed",
        "phase": "11C",
        "scenario_ids": sorted(SCENARIO_IDS),
        "scenario_assumptions": len(assumptions),
        "projection_evidence": len(projection),
        "future_states": len(states),
        "future_relationships": len(relationships),
        "uncertainty_states": len(uncertainty),
        "comparison_rows": len(comparison),
        "scenario_sources": len(sources),
        "maps_37_37b_valid": True,
        "comparison_figure_valid": True,
        "scenario_separation": True,
        "horizon_distinction": True,
        "official_2050_county_reference_without_scenario_total": True,
        "2075_explicit_scenario_only": True,
        "climate_migration_high_uncertainty": True,
        "population_unit_boundaries": True,
        "commuting_migration_boundary": True,
        "spatial_scale_boundary": True,
        "negative_scope_checks": True,
        "phase11a_11b_protected_entries": frozen,
        "phase1_10_immutability": True,
        "phase1_9_protected_artifacts": 196,
        "manifest_counts": manifest_counts,
        "active_holds_preserved": True,
        "phase12_implemented": False,
    }
    (REPORTS / "population_settlement_future_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
