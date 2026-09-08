"""Independent Python validator for Phase 11B mobility/dependency package."""
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
BASELINE = R / "population_settlement_baseline_manifest.json"
WORKING = R / "phase11_working_manifest.json"
MOB = A / "population_mobility_observations.csv"
MOB_REL = N / "population_mobility_relationships.csv"
DEP = A / "population_system_dependency_register.csv"
MATRIX = A / "population_system_dependency_matrix.csv"
NODE = A / "population_settlement_nodes.csv"
SETTLE_REL = N / "population_settlement_relationships.csv"
SOURCES = A / "population_settlement_sources.csv"

MOB_COLUMNS = {"record_id", "metric", "value", "units", "reference_year", "release_year", "estimate_period", "geographic_unit", "geographic_scale", "origin_node_id", "destination_node_id", "source_product", "observed_estimated_modeled", "source_id", "confidence", "reality_status", "canon_status", "notes"}
REL_COLUMNS = {"relationship_id", "module", "source_node_id", "target_node_id", "relationship_type", "value", "units", "reference_year", "release_year", "estimate_period", "origin_geography", "destination_geography", "geographic_scale", "source_product", "observed_estimated_modeled", "source_id", "evidence_strength", "relationship_basis", "confidence", "reality_status", "canon_status", "notes"}
DEP_COLUMNS = {"dependency_id", "population_or_settlement_object", "system", "interface", "relationship_type", "documented_or_inferred", "spatial_scale", "evidence_strength", "source_id", "confidence", "reality_status", "canon_status", "notes"}
MATRIX_DIMENSIONS = ["settlement_concentration", "mobility_dependency", "employment_access", "housing_constraint", "water_dependency", "wastewater_dependency", "energy_dependency", "transport_dependency", "climate_hazard_interface", "environmental_health_interface", "governance_dependency", "service_access", "data_certainty"]
ALLOWED = {"strong", "moderate", "limited", "unknown", "not_applicable"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def check_protected_artifacts() -> tuple[int, int, int]:
    final = ["phase10a_governance_jurisdiction_freeze_manifest.json", "phase10b_governance_dependencies_coordination_freeze_manifest.json", "phase10c_governance_futures_freeze_manifest.json"]
    phase10_entries = 0
    phase10_unique: set[str] = set()
    for name in final:
        payload = json.loads((R / name).read_text(encoding="utf-8"))
        assert payload["status"] == "ACCEPTED / FROZEN"
        for rel, meta in payload["artifacts"].items():
            assert (ROOT / rel).exists() and manifest_matches(ROOT, rel, str(meta["sha256"])), rel
            phase10_entries += 1; phase10_unique.add(rel)
    prior = 0; prior_paths: set[str] = set()
    for path in sorted(R.glob("phase*_freeze_manifest.json")):
        if path.name in final: continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for rel, meta in payload.get("artifacts", payload.get("files", {})).items():
            expected = str(meta["sha256"] if isinstance(meta, dict) else meta)
            assert (ROOT / rel).exists() and manifest_matches(ROOT, rel, expected), rel
            assert rel not in prior_paths and rel not in phase10_unique, rel
            prior_paths.add(rel); prior += 1
    assert prior == 196
    return phase10_entries, len(phase10_unique), prior


def check_baseline() -> int:
    payload = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert payload["phase"] == "11A" and payload["phase11c_implemented"] is False
    checked = 0
    for rel, meta in payload["artifacts"].items():
        path = ROOT / rel
        assert path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"] and path.stat().st_size == meta["bytes"], rel
        checked += 1
    return checked


def main() -> None:
    mob, rel, dep, matrix, nodes, settle_rel, sources = (read(p) for p in [MOB, MOB_REL, DEP, MATRIX, NODE, SETTLE_REL, SOURCES])
    assert set(mob.columns) == MOB_COLUMNS and set(rel.columns) == REL_COLUMNS and set(dep.columns) == DEP_COLUMNS
    assert len(mob) == 302 and mob.record_id.is_unique
    assert len(rel) == 142 and rel.relationship_id.is_unique
    assert len(dep) == 520 and dep.dependency_id.is_unique
    assert len(matrix) == 52 and matrix.object_id.is_unique
    assert len(nodes) >= 40 and nodes.node_id.is_unique
    assert set(mob.source_id).issubset(set(sources.source_id))
    assert set(rel.source_id).issubset(set(sources.source_id))
    assert set(dep.source_id).issubset(set(sources.source_id))
    source_meta = sources.set_index("source_id").to_dict("index")
    node_state = nodes.set_index("node_id")["state"].to_dict()
    allowed_metrics = {"job_count", "worker_count", "workplace_residence_difference", "drive_alone_share", "carpool_share", "public_transit_share", "walk_share", "work_from_home_share", "commute_45_plus_share", "commuter_flow"}
    assert mob.metric.isin(allowed_metrics).all()
    assert mob.observed_estimated_modeled.isin({"estimated", "modeled"}).all()
    assert mob.geographic_scale.isin({"county", "county_pair"}).all()
    assert mob.reference_year.astype(str).str.len().gt(0).all() and mob.release_year.astype(str).str.len().gt(0).all()
    differences = mob[mob.metric == "workplace_residence_difference"]
    assert len(differences) == 16
    for row in differences.itertuples():
        meta = source_meta[row.source_id]
        assert row.source_product == meta["source_product"], row.record_id
        assert str(row.reference_year) == str(meta["reference_year"]), row.record_id
        assert str(row.estimate_period) == str(meta["estimate_period"]), row.record_id
        assert not row.source_id.endswith("mi_wac_rac"), row.record_id
    assert rel.module.eq("11B").all() and rel.relationship_type.eq("commuting_interface_with").all()
    assert rel.geographic_scale.eq("county_pair").all() and rel.units.eq("jobs").all()
    assert rel.source_node_id.isin(set(nodes.node_id)).all() and rel.target_node_id.isin(set(nodes.node_id)).all()
    assert (rel.source_node_id != rel.target_node_id).all()
    assert rel.observed_estimated_modeled.eq("modeled").all()
    assert dep.system.isin({"water", "wastewater", "energy", "transport", "climate_hazard", "environmental_health", "ecology_land", "biogeochemical", "housing_infrastructure", "governance"}).all()
    assert dep.documented_or_inferred.isin({"documented", "inferred", "documented_and_inferred", "reused_context"}).all()
    assert dep.evidence_strength.isin(ALLOWED).all() and dep.confidence.isin({"high", "moderate", "limited", "unknown"}).all()
    assert dep.population_or_settlement_object.isin(set(nodes.node_id)).all()
    for row in dep.itertuples():
        state = str(node_state[row.population_or_settlement_object])
        if row.system == "transport":
            assert row.source_id == f"s11b_lodes_{state.lower()}_od", row.dependency_id
            assert row.documented_or_inferred == "inferred", row.dependency_id
        if row.system == "water":
            expected = "phase10_s03_toledo_treatment" if row.population_or_settlement_object in {"POP-ZONE-39095", "MUNI-3977000"} else "phase10_governance_context"
            assert row.source_id == expected, row.dependency_id
        if row.system == "wastewater":
            expected = "phase10_s05_ohio_npdes" if state == "OH" else "phase10_governance_context"
            assert row.source_id == expected, row.dependency_id
    assert set(matrix.columns) == {"object_id", "object_type", "object_name", *MATRIX_DIMENSIONS, "notes"}
    assert matrix[MATRIX_DIMENSIONS].apply(lambda c: c.isin(ALLOWED)).all().all()
    assert matrix.object_id.isin(set(nodes.node_id)).all()
    assert matrix.notes.str.contains("derived from the dependency register", case=False).all()
    for frame in [mob, rel, dep, matrix]:
        text = " ".join(" ".join(map(str, row)) for row in frame.to_numpy()).lower()
        assert "individual travel path" not in text or "no individual travel path" in text
        if "vulnerability score" in text:
            assert "not a" in text or "not vulnerability" in text
    assert not {"vulnerability_score", "ej_score", "risk_score", "protected_class_rank", "dose", "illness", "mortality"}.intersection(set(mob.columns) | set(rel.columns) | set(dep.columns) | set(matrix.columns))
    for frame in [mob, rel, dep, matrix]:
        assert not frame.astype(str).apply(lambda col: col.str.fullmatch("2050|2075", na=False)).any().any()
    with Image.open(M / "35_population_settlement_2026.png") as image: image.verify()
    with Image.open(M / "36_population_mobility_dependencies_2026.png") as image: map36_size = list(image.size); image.verify()
    svg35 = " ".join(ET.parse(M / "35_population_settlement_2026.svg").getroot().itertext()).lower()
    svg36 = " ".join(ET.parse(M / "36_population_mobility_dependencies_2026.svg").getroot().itertext()).lower()
    for term in ["map 35", "population", "settlement"]: assert term in svg35
    for term in ["map 36", "mobility", "commuting", "employment", "migration", "vulnerability"]: assert term in svg36
    baseline_artifacts = check_baseline()
    phase10_entries, phase10_unique, prior = check_protected_artifacts()
    working = json.loads(WORKING.read_text(encoding="utf-8"))
    assert working["phase"] == "11A/11B" and working["phase11c_implemented"] is False and working["active_holds_preserved"] is True
    checked = 0
    for relpath, meta in working["artifacts"].items():
        path = ROOT / relpath
        assert path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"] and path.stat().st_size == meta["bytes"], relpath
        checked += 1
    result = {"status": "passed", "phase": "11B", "map_numbers": [35, 36], "mobility_observations": len(mob), "mobility_relationships": len(rel), "dependencies": len(dep), "matrix_rows": len(matrix), "baseline_artifacts_checked": baseline_artifacts, "working_artifacts_checked": checked, "phase10_manifest_entries": phase10_entries, "phase10_unique_artifacts": phase10_unique, "prior_phase1_9_protected_artifacts": prior, "residence_workplace_checks": True, "commuting_migration_checks": True, "utility_assignment_boundary": True, "negative_scope_checks": True, "maps_valid": True, "phase11c_absent": True, "holds_preserved": True}
    (R / "population_mobility_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
