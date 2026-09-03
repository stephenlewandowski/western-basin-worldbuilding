"""Validate Phase 9C projection-led qualitative climate futures."""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image
from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "data/processed/analysis"
S = ROOT / "data/processed/scenarios"
M = ROOT / "outputs/maps/systems"
F = ROOT / "outputs/figures"
R = ROOT / "reports"
QUAL = {"high", "moderate", "limited", "unknown"}
HAZARD_BASELINES = {"extreme_heat": "HZ-001", "heavy_precipitation_flooding": "HZ-004", "drought_low_water": "HZ-009", "lake_coastal": "HZ-012", "severe_convective": "HZ-016", "winter": "HZ-018"}
PATH_BASELINES = {"heat_to_energy": "HZD-001", "precip_to_nutrient": "HZD-005", "precip_to_stormwater": "HZD-006", "flood_to_freight": "HZD-007", "lake_to_coastal": "HZD-013", "storm_to_power_information": "HZD-016;HZD-017", "drought_to_ag_ecology": "HZD-009;HZD-010", "winter_to_infrastructure": "HZD-018;HZD-019"}
CONTROL_BASELINES = {"warning_systems": "HZC-001", "heat_adaptation": "HZC-002", "floodplain_stormwater": "HZC-006", "wetland_floodplain_buffer": "HZC-008", "water_treatment": "HZD-008;HZD-022", "lake_monitoring": "HZC-004", "agricultural_conservation": "HZC-009", "grid_information_redundancy": "HZC-012"}
PATH_SOURCES = {"heat_to_energy": "c9_nca_energy", "precip_to_nutrient": "c9_pnas_hab", "precip_to_stormwater": "c9_nca_midwest", "flood_to_freight": "c9_nca_midwest", "lake_to_coastal": "c9_epa_great_lakes", "storm_to_power_information": "c9_nca_energy", "drought_to_ag_ecology": "c9_nca_midwest", "winter_to_infrastructure": "c9_nca_midwest"}
COMPOUND_SOURCES = {"heat_plus_power": "c9_nca_energy", "heat_plus_drought": "c9_nca_midwest", "precip_plus_nutrient": "c9_pnas_hab", "precip_plus_stormwater_wastewater": "c9_nca_midwest", "high_lake_plus_seiche": "c9_epa_great_lakes", "flood_plus_freight": "c9_nca_midwest", "freeze_thaw_plus_infrastructure": "c9_nca_midwest", "storm_plus_power_communications": "c9_nca_energy", "drought_plus_ag_ecology": "c9_nca_midwest"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(frame: pd.DataFrame, key: str, value: str) -> pd.Series:
    match = frame.loc[frame[key] == value]
    assert len(match) == 1, (key, value, len(match))
    return match.iloc[0]


def check_manifest(path: Path) -> int:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for rel, metadata in manifest["artifacts"].items():
        assert manifest_matches(ROOT, rel, metadata["sha256"]), rel
    return len(manifest["artifacts"])


def check_baseline_references(haz: pd.DataFrame, dep: pd.DataFrame, res: pd.DataFrame) -> None:
    base_nodes = read(ROOT / "data/processed/networks/climate_hazard_nodes.csv")
    base_dep = read(ROOT / "data/processed/analysis/climate_hazard_dependency_register.csv")
    base_ctl = read(ROOT / "data/processed/analysis/climate_resilience_control_register.csv")
    assert set(haz.baseline_object_id).issubset(set(base_nodes.node_id))
    assert set(dep.baseline_interface.str.split(";").explode()).issubset(set(base_dep.dependency_id))
    assert set(res.baseline_control.str.split(";").explode()).issubset(set(base_ctl.control_id) | set(base_dep.dependency_id))
    for family, baseline in HAZARD_BASELINES.items():
        assert set(haz.loc[haz.hazard_family == family, "baseline_object_id"]) == {baseline}
    for interface, baseline in PATH_BASELINES.items():
        assert set(dep.loc[dep.baseline_interface == baseline, "baseline_interface"]) == {baseline}
    for domain, baseline in CONTROL_BASELINES.items():
        assert set(res.loc[res.control_domain == domain, "baseline_control"]) == {baseline}


def check_sources(haz: pd.DataFrame, dep: pd.DataFrame, cp: pd.DataFrame) -> None:
    expected_hazard_sources = {"extreme_heat": "c9_glisa_summary", "heavy_precipitation_flooding": "c9_glisa_summary", "drought_low_water": "c9_nca_midwest", "lake_coastal": "c9_notaro_levels", "severe_convective": "c9_nca_midwest", "winter": "c9_notaro_snow"}
    for family, source in expected_hazard_sources.items():
        assert set(haz.loc[haz.hazard_family == family, "source_id"]) == {source}
    for interface, source in PATH_SOURCES.items():
        assert set(dep.loc[dep.baseline_interface == PATH_BASELINES[interface], "source_id"]) == {source}
    for compound, source in COMPOUND_SOURCES.items():
        assert set(cp.loc[cp.compound_id == compound, "source_id"]) == {source}


def main() -> None:
    proj = read(A / "climate_projection_evidence.csv")
    src = read(A / "climate_scenario_sources.csv")
    ass = read(S / "climate_scenario_assumptions.csv")
    haz = read(S / "climate_scenario_hazard_states.csv")
    dep = read(S / "climate_scenario_dependency_states.csv")
    res = read(S / "climate_scenario_resilience_states.csv")
    cp = read(S / "climate_compound_event_scenario_states.csv")
    comp = read(F / "climate_scenario_comparison.csv")
    assert len(proj) == 12 and proj.projection_id.is_unique
    assert len(src) == 13 and src.source_id.is_unique
    assert len(ass) == 36 and ass.assumption_id.is_unique
    assert len(haz) == 36 and haz.state_id.is_unique
    assert len(dep) == 48 and dep.state_id.is_unique
    assert len(res) == 48 and res.state_id.is_unique
    assert len(cp) == 54 and cp.state_id.is_unique
    assert len(comp) == 6 and comp.scenario_id.is_unique
    allowed_scen = {"A", "B", "C"}
    allowed_horiz = {2050, 2075}
    ids = {f"{s}{y}" for s in allowed_scen for y in allowed_horiz}
    assert set(ass.scenario_id) == allowed_scen and set(ass.scenario_year.astype(int)) == allowed_horiz
    assert set(haz.scenario_id) <= ids and set(dep.scenario_id) <= ids and set(res.scenario_id) <= ids and set(cp.scenario_id) <= ids
    source_ids = set(src.source_id)
    assert ass.source_id.isin(source_ids).all() and proj.source_id.isin(source_ids).all() and haz.source_id.isin(source_ids).all() and dep.source_id.isin(source_ids).all() and res.source_id.isin(source_ids).all() and cp.source_id.isin(source_ids).all()
    assert ass.reality_status.eq("fictional").all() and haz.reality_status.eq("fictional").all() and dep.reality_status.eq("fictional").all() and res.reality_status.eq("fictional").all() and cp.reality_status.eq("fictional").all()
    assert ass.plausibility.isin(QUAL).all() and ass.uncertainty.isin(QUAL).all() and haz.plausibility.isin(QUAL).all() and dep.plausibility.isin(QUAL).all() and res.plausibility.isin(QUAL).all() and cp.plausibility.isin(QUAL).all()
    assert proj.observed_or_modeled.isin({"modeled_projection", "model_metadata"}).all() and proj.confidence.isin(QUAL).all() and proj.value.str.len().gt(0).all()
    assert (~proj.projection_period.str.fullmatch("2075")).all()
    for frame in (ass, haz, dep, res, cp, comp, proj, src):
        for column in ("notes", "limitations"):
            if column in frame:
                assert frame[column].str.len().gt(0).all()
    check_baseline_references(haz, dep, res)
    check_sources(haz, dep, cp)
    base_obs = read(A / "climate_hazard_observations.csv")
    assert row(base_obs, "observation_id", "HZO-015").value == "313.0" and row(base_obs, "observation_id", "HZO-015").period == "2026-07-29"

    fields = set(proj.columns) | set(ass.columns) | set(haz.columns) | set(dep.columns) | set(res.columns) | set(cp.columns) | set(comp.columns)
    assert not fields & {"probability", "risk_score", "hazard_score", "mortality", "disease_incidence", "dose", "social_vulnerability", "shoreline_position", "outage_probability"}
    text = " ".join(" ".join(map(str, values)) for frame in (proj, ass, haz, dep, res, cp, comp) for values in frame.to_numpy()).lower()
    assert "no probability" in text and "not a 2075 point estimate" in text
    assert not re.search(r"(?:future|scenario)[ _-](?:tornado|hail|outage|damage|shoreline)[ _-]?(?:count|probability|position)\s*[,=:]\s*[0-9]", text)
    assert not re.search(r"(?:mortality|disease|social[-_ ]vulnerability)\s*(?:probability|score|estimate)\s*[,=:]\s*[0-9]", text)
    for base in ["31_climate_hazard_futures_2050", "31b_climate_hazard_futures_2075"]:
        with Image.open(M / (base + ".png")) as image:
            image.verify()
        svg = " ".join(ET.parse(M / (base + ".svg")).getroot().itertext()).lower()
        for term in ["map " + ("31" if "31_" in base else "31b"), "adaptive / buffered basin", "managed variable basin", "compound hazard basin", "not hazard zones", "seiche"]:
            assert term in svg, term
        if "31b_" in base:
            assert "not a 2075 point estimate" in svg
    man = json.loads((R / "climate_scenario_manifest.json").read_text(encoding="utf-8"))
    assert man["counts"] == {"projection_records": 12, "assumptions": 36, "hazard_states": 36, "dependency_states": 48, "resilience_states": 48, "compound_event_states": 54, "comparison_rows": 6}
    for rel, metadata in man["artifacts"].items():
        assert (ROOT / rel).exists() and sha(ROOT / rel) == metadata["sha256"], rel
    prior = check_manifest(R / "climate_hazard_baseline_manifest.json") + check_manifest(R / "climate_dependency_manifest.json")
    assert prior == 23
    result = {"status": "passed", "phase": "9C", "projection_records": len(proj), "assumptions": len(ass), "hazard_states": len(haz), "dependency_states": len(dep), "resilience_states": len(res), "compound_event_states": len(cp), "comparison_rows": len(comp), "map31_valid": True, "map31b_valid": True, "phase9a_9b_artifacts_checked": prior, "baseline_references_checked": True, "baseline_immutability": True, "future_probabilities_absent": True, "no_health_social_scoring": True, "late_century_not_relabelled_2075": True}
    (R / "phase9c_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
