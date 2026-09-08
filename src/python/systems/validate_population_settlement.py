"""Independent Python validator for Phase 11A population/settlement baseline."""
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
A = ROOT / "data/processed/analysis"
N = ROOT / "data/processed/networks"
M = ROOT / "outputs/maps/systems"
R = ROOT / "reports"
NODE_PATH = A / "population_settlement_nodes.csv"
OBS_PATH = A / "population_settlement_observations.csv"
REL_PATH = N / "population_settlement_relationships.csv"
SOURCE_PATH = A / "population_settlement_sources.csv"
UNC_PATH = A / "population_settlement_uncertainty.csv"
MANIFEST = R / "population_settlement_baseline_manifest.json"

NODE_COLUMNS = {"node_id", "node_type", "name", "state", "geoid", "geographic_unit", "geographic_scale", "latitude", "longitude", "settlement_class", "study_frame", "source_id", "confidence", "reality_status", "canon_status", "notes"}
OBS_COLUMNS = {"record_id", "metric", "value", "units", "reference_year", "release_year", "estimate_period", "geographic_unit", "geographic_scale", "node_id", "source_product", "observed_estimated_modeled", "source_id", "confidence", "reality_status", "canon_status", "notes"}
REL_COLUMNS = {"relationship_id", "module", "source_node_id", "target_node_id", "relationship_type", "value", "units", "reference_year", "release_year", "estimate_period", "origin_geography", "destination_geography", "geographic_scale", "source_product", "observed_estimated_modeled", "source_id", "evidence_strength", "relationship_basis", "confidence", "reality_status", "canon_status", "notes"}
SOURCE_COLUMNS = {"source_id", "title", "url", "source_type", "source_product", "reference_year", "release_year", "estimate_period", "geographic_scale", "observed_estimated_modeled", "retrieval_date", "use_limitations"}
UNC_COLUMNS = {"uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"}
ALLOWED_STATUS = {"observed", "estimated", "modeled"}
ALLOWED_SCALES = {"county", "place", "county/place"}
ALLOWED_NODES = {"population_zone", "municipality", "employment_center"}
ALLOWED_METRICS = {"population_count", "housing_unit_count", "household_count", "occupied_housing_units", "vacant_housing_units", "vacancy_rate", "population_density", "population_estimate", "population_change", "population_change_percent", "median_age", "age_under_18_share", "age_65_plus_share", "average_household_size", "median_year_structure_built", "job_count", "drive_alone_share", "carpool_share", "public_transit_share", "walk_share", "work_from_home_share", "commute_45_plus_share"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def check_prior_freezes() -> tuple[int, int, int]:
    final = [
        "phase10a_governance_jurisdiction_freeze_manifest.json",
        "phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "phase10c_governance_futures_freeze_manifest.json",
    ]
    phase10_entries = 0
    phase10_unique: set[str] = set()
    for name in final:
        manifest = json.loads((R / name).read_text(encoding="utf-8"))
        assert manifest["status"] == "ACCEPTED / FROZEN"
        for rel, meta in manifest["artifacts"].items():
            assert (ROOT / rel).exists(), rel
            assert manifest_matches(ROOT, rel, str(meta["sha256"])), rel
            phase10_entries += 1
            phase10_unique.add(rel)
    prior_total = 0
    prior_unique: set[str] = set()
    for path in sorted(R.glob("phase*_freeze_manifest.json")):
        if path.name in final:
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        artifacts = manifest.get("artifacts", manifest.get("files", {}))
        for rel, meta in artifacts.items():
            expected = str(meta["sha256"] if isinstance(meta, dict) else meta)
            assert (ROOT / rel).exists(), rel
            assert manifest_matches(ROOT, rel, expected), rel
            assert rel not in prior_unique, rel
            assert rel not in phase10_unique, rel
            prior_unique.add(rel)
            prior_total += 1
    assert prior_total == 196, prior_total
    return phase10_entries, len(phase10_unique), prior_total


def check_manifest() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert payload["phase"] == "11A"
    assert payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["map_number"] == 35
    assert payload["phase11c_implemented"] is False
    checked = 0
    for rel, meta in payload["artifacts"].items():
        path = ROOT / rel
        assert path.exists() and path.stat().st_size > 0, rel
        assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"], rel
        assert path.stat().st_size == meta["bytes"], rel
        checked += 1
    return checked


def main() -> None:
    nodes, obs, rel, sources, unc = (read(path) for path in [NODE_PATH, OBS_PATH, REL_PATH, SOURCE_PATH, UNC_PATH])
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(obs.columns) == OBS_COLUMNS
    assert set(rel.columns) == REL_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert set(unc.columns) == UNC_COLUMNS
    assert len(nodes) == 62 and nodes.node_id.is_unique
    assert len(obs) == 918 and obs.record_id.is_unique
    assert len(rel) == 44 and rel.relationship_id.is_unique
    assert len(sources) == 34 and sources.source_id.is_unique
    assert len(unc) == 9 and unc.uncertainty_id.is_unique
    assert nodes.node_type.isin(ALLOWED_NODES).all()
    assert nodes.geographic_scale.isin({"county", "place"}).all()
    assert nodes.confidence.isin({"high", "moderate", "limited", "unknown"}).all()
    assert nodes.reality_status.eq("real").all() and nodes.canon_status.isin({"verified", "inferred"}).all()
    assert nodes.source_id.isin(set(sources.source_id)).all()
    assert obs.metric.isin(ALLOWED_METRICS).all()
    assert obs.observed_estimated_modeled.isin(ALLOWED_STATUS).all()
    assert obs.geographic_scale.isin(ALLOWED_SCALES).all()
    assert obs.source_id.isin(set(sources.source_id)).all()
    assert obs.node_id.isin(set(nodes.node_id)).all()
    assert obs.reference_year.astype(str).str.len().gt(0).all()
    assert obs.release_year.astype(str).str.len().gt(0).all()
    assert obs.estimate_period.astype(str).str.len().gt(0).all()
    assert rel.module.eq("11A").all()
    assert rel.relationship_type.isin({"contains_settlement", "employment_concentration"}).all()
    assert rel.source_node_id.isin(set(nodes.node_id)).all()
    assert rel.target_node_id.isin(set(nodes.node_id)).all()
    assert rel.source_id.isin(set(sources.source_id)).all()
    assert set(obs.loc[obs.metric == "population_count", "units"]) == {"persons"}
    assert set(obs.loc[obs.metric == "household_count", "units"]) == {"households"}
    assert set(obs.loc[obs.metric == "housing_unit_count", "units"]) == {"housing_units"}
    assert set(obs.loc[obs.metric == "population_density", "units"]) == {"persons_per_square_mile"}
    assert obs.loc[obs.metric == "population_density", "observed_estimated_modeled"].isin({"observed", "estimated"}).all()
    assert obs.loc[obs.metric == "job_count", "units"].eq("jobs").all()
    assert obs.loc[obs.metric == "job_count", "observed_estimated_modeled"].eq("modeled").all()
    assert not set(nodes.columns) & {"risk_score", "vulnerability_score", "ej_score", "protected_class_rank"}
    assert not set(obs.columns) & {"dose", "illness", "mortality", "exposure_score", "vulnerability_score"}
    all_data = " ".join(" ".join(map(str, row)) for frame in [nodes, obs, rel] for row in frame.to_numpy()).lower()
    assert "individual profile" not in all_data
    assert not re.search(r"\b(?:2050|2075)\b", all_data)
    assert "great black swamp" in " ".join(unc.statement).lower() and "noncanonical" in " ".join(unc.statement).lower()
    assert "intake-coordinate discrepancy" in " ".join(unc.statement).lower() and "unresolved" in " ".join(unc.statement).lower()
    with Image.open(M / "35_population_settlement_2026.png") as image:
        image.verify(); image_size = list(image.size)
    svg_text = " ".join(ET.parse(M / "35_population_settlement_2026.svg").getroot().itertext()).lower()
    for term in ["map 35", "population & settlement", "2020 census", "person ≠ household", "great black swamp"]:
        assert term in svg_text, term
    manifest_artifacts = check_manifest()
    phase10_entries, phase10_unique, prior = check_prior_freezes()
    result = {"status": "passed", "phase": "11A", "map_number": 35, "settlement_nodes": len(nodes), "population_observations": len(obs), "relationships": len(rel), "sources": len(sources), "uncertainties": len(unc), "map35_valid": True, "image_size": image_size, "manifest_artifacts_checked": manifest_artifacts, "phase10_manifest_entries": phase10_entries, "phase10_unique_artifacts": phase10_unique, "prior_phase1_9_protected_artifacts": prior, "vintage_scale_quantity_checks": True, "negative_scope_checks": True, "holds_preserved": True, "phase11c_absent": True}
    (R / "population_settlement_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
