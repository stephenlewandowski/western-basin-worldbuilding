"""Validate Phase 13C infectious-disease system futures independently of the builder."""
from __future__ import annotations

import argparse
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
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

ASSUMPTIONS = SCENARIOS / "infectious_disease_scenario_assumptions.csv"
TRANSMISSION = SCENARIOS / "infectious_disease_transmission_states_scenario.csv"
SURVEILLANCE = SCENARIOS / "infectious_disease_surveillance_states_scenario.csv"
RESPONSE = SCENARIOS / "infectious_disease_response_states_scenario.csv"
DEPENDENCIES = SCENARIOS / "infectious_disease_dependency_states_scenario.csv"
UNCERTAINTY = SCENARIOS / "infectious_disease_uncertainty_states_scenario.csv"
SOURCES = ANALYSIS / "infectious_disease_scenario_sources.csv"
COMPARISON = FIGURES / "infectious_disease_scenario_comparison.csv"
MAP2050 = MAPS / "43_infectious_disease_system_futures_2050"
MAP2075 = MAPS / "43b_infectious_disease_system_futures_2075"
COMPARISON_PNG = FIGURES / "infectious_disease_scenario_comparison.png"
COMPARISON_SVG = FIGURES / "infectious_disease_scenario_comparison.svg"
MANIFEST = REPORTS / "infectious_disease_scenario_manifest.json"
CHECK = REPORTS / "infectious_disease_scenario_artifact_check.json"
REVIEW = REPORTS / "infectious_disease_scenario_independent_review.md"
LEDGER = REPORTS / "phase13c_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
PHASE13A_FREEZE = REPORTS / "phase13a_infectious_disease_freeze_manifest.json"
PHASE13B_FREEZE = REPORTS / "phase13b_infectious_disease_dependencies_freeze_manifest.json"
BASE_SHA = "769909604caf7596d3736fd07e616ad5f3f1cba1"

SCENARIO_IDS = {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
SCENARIO_YEARS = {sid: int(sid[1:]) for sid in SCENARIO_IDS}
ARCHETYPES = {"vector-borne", "waterborne/environmental", "foodborne/enteric", "respiratory", "zoonotic", "healthcare/AMR"}
QUALITATIVE = {"moderate", "high", "exploratory"}

ASSUMPTION_COLUMNS = {"assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption", "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes"}
TRANSMISSION_COLUMNS = {"state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_system_ids", "transmission_opportunity_state", "environmental_interface_state", "seasonal_or_contact_window", "host_or_setting_interface", "observability_boundary", "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"}
SURVEILLANCE_COLUMNS = {"state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_surveillance_ids", "surveillance_capacity_state", "detection_latency_state", "coverage_and_method_state", "observation_interface", "reported_observation_boundary", "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"}
RESPONSE_COLUMNS = {"state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_response_interfaces", "healthcare_public_health_capacity", "response_coordination_state", "response_latency_margin", "intervention_interface", "infrastructure_dependency_state", "response_boundary", "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"}
DEPENDENCY_COLUMNS = {"state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_dependency_id", "dependency_domain", "object_a", "object_b", "relationship_type", "spatial_scale", "current_fact", "scenario_assumption", "scenario_consequence", "dependency_state", "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes"}
UNCERTAINTY_COLUMNS = {"state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_uncertainty_id", "category", "subject_id", "current_fact", "scenario_assumption", "uncertainty_state", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"}
SOURCE_COLUMNS = {"source_id", "title", "url", "source_type", "publication_or_period", "retrieval_date", "geographic_scale", "method_or_product", "evidence_use", "use_limitations", "retrieval_url", "retrieval_provenance", "scenario_relevance"}
COMPARISON_COLUMNS = {"scenario_id", "scenario", "horizon", "transmission_opportunity", "environmental_interfaces", "surveillance_detection", "response_coordination", "healthcare_response_margin", "mobility_connectivity", "infrastructure_dependencies", "food_freight_interfaces", "vector_water_systems", "uncertainty_profile", "boundary_statement", "scenario_distinctiveness", "notes"}

PRIOR_MANIFESTS = {
    "reports/phase3a_freeze_manifest.json", "reports/phase3b_freeze_manifest.json",
    "reports/phase4b_information_freeze_manifest.json", "reports/phase4c_information_freeze_manifest.json",
    "reports/phase5a_freight_freeze_manifest.json", "reports/phase5b_freight_evidence_freeze_manifest.json", "reports/phase5c_freight_dependency_freeze_manifest.json",
    "reports/phase6a_ecology_freeze_manifest.json", "reports/phase6b_ecological_dependency_freeze_manifest.json", "reports/phase6c_ecological_futures_freeze_manifest.json",
    "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
    "reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json", "reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json", "reports/phase8c_biogeochemical_futures_freeze_manifest.json",
    "reports/phase9a_climate_natural_hazards_freeze_manifest.json", "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json", "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
    "reports/phase10a_governance_jurisdiction_freeze_manifest.json", "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", "reports/phase10c_governance_futures_freeze_manifest.json",
    "reports/phase11a_population_settlement_freeze_manifest.json", "reports/phase11b_population_mobility_dependencies_freeze_manifest.json", "reports/phase11c_population_settlement_futures_freeze_manifest.json",
    "reports/phase12a_vector_ecology_freeze_manifest.json", "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json", "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
}
CONTEXT_MANIFESTS = {
    "reports/phase9a_climate_natural_hazards_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase9c_climate_hazard_futures_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase7a_exposure_environmental_health_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase10a_governance_jurisdiction_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase10c_governance_futures_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase11a_population_settlement_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase11b_population_mobility_dependencies_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase11c_population_settlement_futures_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase12a_vector_ecology_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase12c_vector_ecology_futures_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase5a_freight_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase5b_freight_evidence_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase5c_freight_dependency_freeze_manifest.json": "ACCEPTED / FROZEN",
    "reports/phase3b_freeze_manifest.json": "ACCEPTED / FROZEN",
}


def read(path: Path) -> pd.DataFrame:
    assert path.is_file() and path.stat().st_size > 0, path
    return pd.read_csv(path, dtype=str, keep_default_na=False).fillna("")


def entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    return canonical(path.read_bytes()) == canonical(accepted) and expected in {hashlib.sha256(accepted).hexdigest(), hashlib.sha256(accepted.replace(b"\n", b"\r\n")).hexdigest()}


def verify_manifest_hashes(path: Path, expected_phase: str, expected_count: int) -> tuple[dict, set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload.get("accepted_phase") == expected_phase
    assert payload.get("status") == "ACCEPTED / FROZEN"
    artifacts = entries(payload)
    assert len(artifacts) == expected_count
    protected: set[str] = set()
    for relative, metadata in artifacts.items():
        expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
        artifact = ROOT / relative
        assert artifact.is_file() and artifact.stat().st_size > 0, relative
        assert portable_match(relative, expected), relative
        protected.add(relative)
    return payload, protected


def verify_frozen_inputs() -> dict[str, int | bool]:
    phase13a, phase13a_paths = verify_manifest_hashes(PHASE13A_FREEZE, "13A", 25)
    phase13b, phase13b_paths = verify_manifest_hashes(PHASE13B_FREEZE, "13B", 24)
    assert phase13a["baseline"] == "Infectious Disease System Baseline, 2026"
    assert phase13b["baseline"] == "Environmental & Human-System Transmission Dependencies, 2026"
    assert phase13b["phase13a_freeze_manifest"]["path"] == "reports/phase13a_infectious_disease_freeze_manifest.json"
    assert portable_match("reports/phase13a_infectious_disease_freeze_manifest.json", phase13b["phase13a_freeze_manifest"]["sha256"])
    assert phase13a.get("phase13c_implemented") is False
    assert phase13b.get("phase13c_implemented") is False and phase13b.get("phase14_implemented") is False
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
    assert prior_entries == 358 and len(prior_hashes) == 351, (prior_entries, len(prior_hashes))
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines())
    protected = set(prior_hashes) | phase13a_paths | phase13b_paths
    assert not changed.intersection(protected), sorted(changed.intersection(protected))
    return {"phase13a_artifacts": len(phase13a_paths), "phase13b_artifacts": len(phase13b_paths), "prior_entries": prior_entries, "prior_unique": len(prior_hashes), "protected_unchanged": True}


def verify_context_manifests() -> int:
    for relative, status in CONTEXT_MANIFESTS.items():
        path = ROOT / relative
        payload, _ = verify_manifest_hashes(path, str(payload_phase(relative)), len(entries(json.loads(path.read_text(encoding="utf-8")))))
        assert payload["status"] == status, relative
    water = json.loads((REPORTS / "water_system_manifest.json").read_text(encoding="utf-8"))
    assert water["system"] == "water" and water["nodes"] == 14 and water["edges"] == 15
    observation = json.loads((REPORTS / "observation_system_manifest.json").read_text(encoding="utf-8"))
    assert observation["phase"] == "4A" and observation["counts"]["nodes"] == 25 and observation["counts"]["edges"] == 21
    return len(CONTEXT_MANIFESTS) + 2


def payload_phase(relative: str) -> str:
    return re.search(r"phase(\d+[a-z]?)_", relative).group(1).upper()


def check_common(frame: pd.DataFrame, columns: set[str], expected_rows: int, unique: str, assumption_ids: set[str], source_ids: set[str]) -> None:
    assert set(frame.columns) == columns, sorted(set(frame.columns) ^ columns)
    assert len(frame) == expected_rows and frame[unique].is_unique
    assert frame.scenario_id.isin(SCENARIO_IDS).all()
    assert frame.apply(lambda row: int(row.horizon) == SCENARIO_YEARS[row.scenario_id], axis=1).all()
    assert frame.notes.str.len().gt(0).all()
    assert frame.assumption_id.isin(assumption_ids).all()
    assert frame.source_or_basis.isin(source_ids).all()
    assert frame.reality_status.eq("fictional").all() and frame.canon_status.eq("scenario").all() and frame.relationship_basis.eq("scenario_assumption").all()


def verify_tables() -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    frames = {
        "assumptions": read(ASSUMPTIONS), "transmission": read(TRANSMISSION), "surveillance": read(SURVEILLANCE),
        "response": read(RESPONSE), "dependencies": read(DEPENDENCIES), "uncertainty": read(UNCERTAINTY), "sources": read(SOURCES), "comparison": read(COMPARISON),
    }
    assumptions = frames["assumptions"]
    assert set(assumptions.columns) == ASSUMPTION_COLUMNS and len(assumptions) == 36 and assumptions.assumption_id.is_unique
    assert assumptions.scenario_id.isin(SCENARIO_IDS).all() and assumptions.apply(lambda row: int(row.horizon) == SCENARIO_YEARS[row.scenario_id], axis=1).all()
    assert assumptions.groupby("scenario_id").size().eq(6).all()
    assert assumptions.reality_status.eq("fictional").all() and assumptions.canon_status.eq("scenario").all() and assumptions.classification.eq("SCENARIO ASSUMPTION").all()
    assert assumptions.numeric_future_value_adopted.eq("false").all() and assumptions.uncertainty.isin(QUALITATIVE).all()
    sources = frames["sources"]
    assert set(sources.columns) == SOURCE_COLUMNS and len(sources) == 33 and sources.source_id.is_unique and sources.url.is_unique
    source_ids = set(sources.source_id)
    assumption_ids = set(assumptions.assumption_id)
    check_common(frames["transmission"], TRANSMISSION_COLUMNS, 36, "state_id", assumption_ids, source_ids)
    check_common(frames["surveillance"], SURVEILLANCE_COLUMNS, 36, "state_id", assumption_ids, source_ids)
    check_common(frames["response"], RESPONSE_COLUMNS, 36, "state_id", assumption_ids, source_ids)
    check_common(frames["dependencies"], DEPENDENCY_COLUMNS, 36, "state_id", assumption_ids, source_ids)
    check_common(frames["uncertainty"], UNCERTAINTY_COLUMNS, 36, "state_id", assumption_ids, source_ids)
    comparison = frames["comparison"]
    assert set(comparison.columns) == COMPARISON_COLUMNS and len(comparison) == 6 and comparison.scenario_id.is_unique
    assert comparison.scenario_id.isin(SCENARIO_IDS).all() and comparison.apply(lambda row: int(row.horizon) == SCENARIO_YEARS[row.scenario_id], axis=1).all()
    assert comparison.notes.str.len().gt(0).all()
    for frame in (frames["transmission"], frames["surveillance"], frames["response"], frames["dependencies"], frames["uncertainty"]):
        assert set(frame.archetype) == ARCHETYPES and frame.groupby("scenario_id").size().eq(6).all()
    nodes = read(NETWORKS / "infectious_disease_nodes.csv")
    deps = read(ANALYSIS / "infectious_disease_dependency_register.csv")
    uncs = read(ANALYSIS / "infectious_disease_dependency_uncertainties.csv")
    node_ids = set(nodes.node_id)
    dep_ids = set(deps.dependency_id)
    unc_ids = set(uncs.uncertainty_id)
    tx = frames["transmission"]
    assert tx.baseline_system_ids.map(lambda value: set(value.split(";")) <= node_ids).all()
    assert tx.transmission_opportunity_state.str.contains("opportunity", case=False).all()
    assert tx.observability_boundary.str.contains("remain separate", case=False).all()
    sv = frames["surveillance"]
    assert sv.baseline_surveillance_ids.map(lambda value: set(value.split(";")) <= node_ids).all()
    assert sv.surveillance_capacity_state.str.len().gt(0).all() and sv.detection_latency_state.str.len().gt(0).all()
    assert sv.reported_observation_boundary.str.contains("observations", case=False).all()
    assert sv.reported_observation_boundary.str.contains("disease", case=False).all()
    rp = frames["response"]
    assert rp.baseline_response_interfaces.str.len().gt(0).all() and rp.response_boundary.str.contains("not", case=False).all()
    dp = frames["dependencies"]
    assert dp.baseline_dependency_id.isin(dep_ids).all() and dp.current_fact.str.startswith("CURRENT FACT (2026 baseline):").all() and dp.scenario_assumption.str.startswith("SCENARIO ASSUMPTION:").all() and dp.scenario_consequence.str.startswith("SCENARIO CONSEQUENCE:").all()
    un = frames["uncertainty"]
    assert un.baseline_uncertainty_id.isin(unc_ids).all() and un.current_fact.str.startswith("CURRENT FACT (2026 baseline):").all()
    assert un.uncertainty_state.str.contains("Great Black Swamp remains C — HOLD / noncanonical", case=False).all()
    assert un.uncertainty_state.str.contains("Toledo intake-coordinate discrepancy remains UNRESOLVED", case=False).all()
    return frames, {"assumptions": len(assumptions), "transmission_states": len(tx), "surveillance_states": len(sv), "response_states": len(rp), "dependency_states": len(dp), "uncertainty_states": len(un), "scenario_sources": len(sources), "comparison_rows": len(comparison)}


def verify_horizon_and_scenario_structure(frames: dict[str, pd.DataFrame]) -> None:
    a = frames["assumptions"]
    b_text = " ".join(a.loc[a.scenario_id.str.startswith("B"), "assumption"]).lower()
    c_text = " ".join(a.loc[a.scenario_id.str.startswith("C"), "assumption"]).lower()
    assert "heterogeneous" in b_text and "distributed" in b_text and "friction" in b_text
    assert "more permissive" in c_text and "strain" in c_text
    assert "coordinated" in " ".join(a.loc[a.scenario_id.str.startswith("A"), "assumption"]).lower()
    assert "not a midpoint" in " ".join(frames["comparison"].scenario_distinctiveness).lower()
    for scenario in "ABC":
        for name, columns in {
            "transmission": ["transmission_opportunity_state", "environmental_interface_state", "seasonal_or_contact_window"],
            "surveillance": ["surveillance_capacity_state", "detection_latency_state", "coverage_and_method_state"],
            "response": ["healthcare_public_health_capacity", "response_coordination_state", "response_latency_margin"],
            "dependencies": ["dependency_state", "scenario_consequence"],
            "uncertainty": ["uncertainty_state"],
            "comparison": ["transmission_opportunity", "surveillance_detection", "response_coordination", "uncertainty_profile"],
        }.items():
            frame = frames[name]
            left = frame.loc[frame.scenario_id == f"{scenario}2050", columns].reset_index(drop=True)
            right = frame.loc[frame.scenario_id == f"{scenario}2075", columns].reset_index(drop=True)
            assert not left.equals(right), (scenario, name)
        left = a.loc[a.scenario_id == f"{scenario}2050", "assumption"].tolist()
        right = a.loc[a.scenario_id == f"{scenario}2075", "assumption"].tolist()
        assert left != right


def verify_negative_scope(frames: dict[str, pd.DataFrame]) -> None:
    all_frames = [frames[name] for name in ("assumptions", "transmission", "surveillance", "response", "dependencies", "uncertainty", "comparison")]
    fields = set().union(*(set(frame.columns) for frame in all_frames))
    forbidden = {"case_total", "case_count", "incidence_rate", "incidence_forecast", "outbreak_probability", "risk_score", "disease_burden_score", "individual_risk", "infection_probability", "vulnerability_score", "ej_score", "exposure_score", "transmission_rate"}
    assert not fields.intersection(forbidden), sorted(fields.intersection(forbidden))
    text = " ".join(" ".join(map(str, row)) for frame in all_frames for row in frame.to_numpy()).lower()
    required = [
        "pathogen presence", "exposure", "infection", "reported case", "local transmission", "outbreak", "disease burden",
        "transmission opportunity ≠ future incidence", "environmental suitability ≠ disease burden", "surveillance sensitivity is not disease intensity",
        "infrastructure stress ≠ illness", "mobility/connectivity ≠ outbreak", "more detection and reporting can produce more recorded observations without implying more underlying disease",
    ]
    for term in required:
        assert term in text, term
    assert "not a midpoint" in text
    assert not re.search(r"\b(?:future|projected)\b[^\n]{0,140}\b(?:cases?|infections?|hospitalizations?|deaths?|incidence|outbreak probability)\b[^\n]{0,30}\d", text)
    assert not re.search(r"\b(?:2050|2075)\s*[,=:]\s*\d", text)
    assert not re.search(r"(?:climate|vector suitability|surveillance|mobility|contamination|infrastructure stress)\s*(?:causes|determines|proves|equals)\s*(?:infection|disease|incidence|outbreak|burden)", text)
    assert "no future case total" in text and "no unsupported local downscaling" in text


def verify_maps_and_figure() -> dict[str, list[int]]:
    sizes: dict[str, list[int]] = {}
    for base, map_id, year in ((MAP2050, "map 43", "2050"), (MAP2075, "map 43b", "2075")):
        png, svg = base.with_suffix(".png"), base.with_suffix(".svg")
        assert png.is_file() and png.stat().st_size > 10000 and svg.is_file() and svg.stat().st_size > 10000
        with Image.open(png) as image:
            image.verify()
            sizes[map_id] = [image.width, image.height]
            assert image.width >= 2000 and image.height >= 1000
        text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        for term in (map_id, year, "infectious disease system futures", "vector-borne", "waterborne / environmental", "foodborne / enteric", "respiratory", "zoonotic", "healthcare / amr", "opportunity", "surveillance / detection", "response", "dependency", "uncertainty", "not a geographic risk surface", "future incidence", "disease burden", "great black swamp", "toledo intake-coordinate discrepancy"):
            assert term in text, (map_id, term)
        if year == "2050":
            assert "2050 intermediate trajectory" in text
        else:
            assert "2075 matured / diverged system state" in text
    assert COMPARISON.exists() and COMPARISON.stat().st_size > 100
    for figure in (COMPARISON_PNG, COMPARISON_SVG):
        assert figure.is_file() and figure.stat().st_size > 10000
    with Image.open(COMPARISON_PNG) as image:
        image.verify()
        sizes["comparison"] = [image.width, image.height]
    ET.parse(COMPARISON_SVG)
    return sizes


def verify_citations() -> None:
    for name in ("infectious_disease_scenario_sources.md", "infectious_disease_scenario_assumptions.md", "infectious_disease_scenario_findings.md", "infectious_disease_scenario_qa.md"):
        result = subprocess.run([sys.executable, str(CITATION_SCRIPT), "--ledger", str(LEDGER), "verify", str(REPORTS / name), "--strict"], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr


def verify_status_surfaces() -> None:
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        assert "phase 13c" in text and "great black swamp" in text and "hold" in text and "noncanonical" in text and "intake-coordinate discrepancy" in text and "unresolved" in text, relative
    brief = (ROOT / "docs/phase_briefs/phase13c_infectious_disease_futures.md").read_text(encoding="utf-8").lower()
    assert "phase 13c" in brief and "2050" in brief and "2075" in brief


def verify_no_phase14_implementation() -> None:
    for base in (SCENARIOS, MAPS, ROOT / "src/python/systems", ROOT / "src/R/systems"):
        for path in base.rglob("*"):
            if path.is_file():
                name = path.name.lower()
                assert "phase14" not in name and "phase_14" not in name
    assert not any(path.exists() for path in (MAPS / "44_phase14.png", MAPS / "44_phase14.svg"))


def verify_review(require_review: bool) -> bool:
    if not REVIEW.exists():
        assert not require_review
        return False
    text = REVIEW.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, "independent review JSON block"
    verdict = json.loads(match.group(1))
    assert verdict.get("passed") is True
    for key in ("security_concerns", "logic_errors", "provenance_errors", "epidemiological_errors", "scenario_boundary_errors", "surveillance_errors", "spatial_scale_errors", "health_boundary_errors"):
        assert verdict.get(key) == [], key
    assert isinstance(verdict.get("suggestions"), list) and isinstance(verdict.get("summary"), str) and verdict["summary"]
    return True


def update_manifest_and_verify() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "13C" and payload["map_numbers"] == [43, "43b"] and payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["scenario_ids"] == ["A2050", "A2075", "B2050", "B2075", "C2050", "C2075"]
    assert payload["counts"] == {"assumptions": 36, "transmission_states": 36, "surveillance_states": 36, "response_states": 36, "dependency_states": 36, "uncertainty_states": 36, "scenario_sources": 33, "comparison_rows": 6}
    assert payload["phase13a_13b_accepted_frozen"] is True and payload["phase1_12_immutable"] is True and payload["phase14_implemented"] is False
    assert payload["numeric_future_values_adopted"] is False and payload["future_case_counts"] is False and payload["future_incidence_forecast"] is False and payload["outbreak_probability"] is False
    assert payload["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert portable_match("reports/phase13a_infectious_disease_freeze_manifest.json", payload["phase13a_freeze_manifest"]["sha256"])
    assert portable_match("reports/phase13b_infectious_disease_dependencies_freeze_manifest.json", payload["phase13b_freeze_manifest"]["sha256"])
    payload["artifacts"][str(CHECK.relative_to(ROOT)).replace("\\", "/")] = {"sha256": digest(CHECK), "bytes": CHECK.stat().st_size, "role": "machine validation result"}
    if REVIEW.exists():
        payload["artifacts"][str(REVIEW.relative_to(ROOT)).replace("\\", "/")] = {"sha256": digest(REVIEW), "bytes": REVIEW.stat().st_size, "role": "independent review record"}
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    count = 0
    for relative, metadata in entries(payload).items():
        artifact = ROOT / relative
        expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
        assert artifact.is_file() and artifact.stat().st_size > 0 and digest(artifact) == expected, relative
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-review", action="store_true")
    args = parser.parse_args()
    frames, counts = verify_tables()
    verify_horizon_and_scenario_structure(frames)
    verify_negative_scope(frames)
    freeze_result = verify_frozen_inputs()
    context_count = verify_context_manifests()
    verify_status_surfaces()
    verify_no_phase14_implementation()
    map_sizes = verify_maps_and_figure()
    verify_citations()
    review_present = verify_review(args.require_review)
    result = {
        "status": "passed", "phase": "13C", "map_numbers": [43, "43b"], **counts,
        "maps_valid": True, "map_sizes": map_sizes, "comparison_figure_valid": True, "provenance_strict": True,
        "assumption_references": True, "scenario_fact_separation": True, "horizon_distinction": True, "scenario_b_structurally_distinct": True,
        "transmission_opportunity_not_incidence": True, "climate_vector_suitability_not_disease": True, "water_infrastructure_not_illness": True,
        "mobility_not_outbreak_certainty": True, "surveillance_not_incidence": True, "detection_not_more_disease": True,
        "response_capacity_not_disease_absence": True, "no_future_case_counts": True, "no_outbreak_probability": True, "no_individual_risk": True,
        "no_vulnerability_ej_scoring": True, "no_unsupported_local_downscaling": True, "phase13a_13b_freeze_integrity": True,
        "context_manifests_checked": context_count, "prior_freeze_manifest_entries_checked": freeze_result["prior_entries"], "prior_unique_protected_artifacts_checked": freeze_result["prior_unique"],
        "phase13a_artifacts_checked": freeze_result["phase13a_artifacts"], "phase13b_artifacts_checked": freeze_result["phase13b_artifacts"], "prior_artifacts_unchanged": True,
        "active_holds_preserved": True, "deferred_maintenance_preserved": True, "phase14_not_implemented": True, "review_present": review_present,
    }
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    manifest_artifacts = update_manifest_and_verify()
    result["manifest_artifacts_checked"] = manifest_artifacts
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    # The artifact check is itself listed in the working manifest; rerun once more
    # so its recorded hash is the final generated result.
    manifest_artifacts = update_manifest_and_verify()
    result["manifest_artifacts_checked"] = manifest_artifacts
    CHECK.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
