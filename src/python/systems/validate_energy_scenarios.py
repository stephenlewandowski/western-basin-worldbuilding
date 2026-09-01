"""Validate Phase 3C scenario separation, schemas, and rendered artifacts."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCENARIOS = {"A2050": 2050, "A2075": 2075, "B2050": 2050, "B2075": 2075, "C2050": 2050, "C2075": 2075}
ALLOWED_ROLES = {"PERSISTS", "EXPANDS ROLE", "CHANGES FUNCTION", "DECLINES", "RETIRES", "UNKNOWN", "NEW FUNCTION"}
ALLOWED_CHANGES = {"persist", "expand_role", "new_function", "decline_role", "retire", "uncertain_future", "new_node", "resilience_upgrade", "distributed_support", "storage_expansion", "compute_growth", "dependency_reduced", "dependency_increased", "new_edge"}
ALLOWED_LEVELS = {"low", "moderate", "high"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for rel, meta in manifest["files"].items():
        file_path = ROOT / rel
        assert file_path.exists(), rel
        assert digest(file_path) == meta["sha256"], rel


def main() -> None:
    scenario_dir = ROOT / "data/processed/scenarios"
    assumptions = pd.read_csv(scenario_dir / "energy_scenario_assumptions.csv", dtype=str).fillna("")
    nodes = pd.read_csv(scenario_dir / "energy_nodes_scenario.csv", dtype=str).fillna("")
    edges = pd.read_csv(scenario_dir / "energy_edges_scenario.csv", dtype=str).fillna("")
    comparison = pd.read_csv(ROOT / "outputs/figures/energy_scenarios_comparison.csv", dtype=str).fillna("")
    baseline = pd.read_csv(ROOT / "data/processed/networks/energy_system_nodes.csv", dtype=str).fillna("")
    baseline_edges = pd.read_csv(ROOT / "data/processed/networks/energy_system_edges.csv", dtype=str).fillna("")
    dep_nodes = pd.read_csv(ROOT / "data/processed/networks/energy_dependency_nodes.csv", dtype=str).fillna("")

    assert set(assumptions.scenario_id) == set(SCENARIOS) and len(assumptions) == 36
    assert assumptions.assumption_id.is_unique
    assert assumptions.groupby("scenario_id").size().eq(6).all()
    assert assumptions.plausibility.isin({"high", "moderate", "exploratory"}).all()
    assert assumptions.status.eq("scenario_assumption").all()
    assert assumptions.source_id.str.len().gt(0).all()

    assert len(nodes) == 114 and nodes.object_id.is_unique
    assert set(nodes.scenario_id) == set(SCENARIOS)
    assert nodes.groupby("scenario_id").size().eq(19).all()
    assert nodes.future_role.isin(ALLOWED_ROLES).all()
    assert nodes.change_type.isin(ALLOWED_CHANGES).all()
    assert nodes.reality_status.eq("fictional").all()
    assert nodes.relationship_basis.eq("scenario_assumption").all()
    assert nodes.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert nodes.groupby("scenario_id").baseline_object_id.apply(lambda s: (s != "").sum()).eq(16).all()
    selected_baseline_ids = set(baseline[baseline.node_type.isin(["generation", "storage", "major_load", "compute"])].node_id)
    assert set(nodes[nodes.baseline_object_id != ""].baseline_object_id) == selected_baseline_ids

    valid_endpoints = set(baseline.node_id) | set(dep_nodes.node_id) | set(nodes.object_id)
    assert len(edges) == 114 and edges.groupby("scenario_id").size().eq(19).all()
    assert edges.from_object_id.isin(valid_endpoints).all() and edges.to_object_id.isin(valid_endpoints).all()
    assert edges.scenario_id.isin(SCENARIOS).all()
    assert edges.relationship_basis.eq("scenario_assumption").all()
    assert edges.reality_status.eq("fictional").all()
    assert edges.change_type.isin(ALLOWED_CHANGES).all()
    assert edges.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert edges.notes.str.contains("Not a power-flow route").all()

    assert len(comparison) == 48 and comparison.groupby("scenario_id").size().eq(8).all()
    assert set(comparison.scenario_id) == set(SCENARIOS)
    assert comparison.level.isin(ALLOWED_LEVELS).all()
    assert comparison.dimension.nunique() == 8

    for sid, year in SCENARIOS.items():
        assert set(nodes.loc[nodes.scenario_id == sid, "scenario_year"]) == {str(year)}
        assert set(edges.loc[edges.scenario_id == sid, "scenario_year"]) == {str(year)}
        assert set(assumptions.loc[assumptions.scenario_id == sid, "scenario_year"]) == {str(year)}

    # Future records contain no invented quantitative capacity, probability, or route claims.
    future_text = " ".join(
        " ".join(map(str, row))
        for frame, columns in (
            (assumptions, ["assumption", "basis", "notes"]),
            (nodes, ["object_name", "future_role", "notes"]),
            (edges, ["notes"]),
        )
        for row in frame[columns].values
    )
    assert not re.search(r"\b\d[\d,]*(?:\.\d+)?\s*MW\b", future_text, flags=re.I)
    assert not re.search(r"\b\d+(?:\.\d+)?\s*%\b", future_text)
    assert not re.search(r"\b(?:N-1|reserve margin|outage probability|restoration time|blackout footprint)\b", future_text, flags=re.I)
    assert baseline.loc[baseline.node_id == "ENE-EIA-1733", "status_2026"].iloc[0] == "operating_planned_retirement"
    assert baseline.loc[baseline.node_id == "ENE-COMPUTE-BG-5MW", "status_2026"].iloc[0] == "permitted_or_planned_unverified_operation"
    assert len(baseline) == 18 and len(baseline_edges) == 17 and len(dep_nodes) == 5

    check_manifest(ROOT / "reports/phase3a_freeze_manifest.json")
    check_manifest(ROOT / "reports/phase3b_freeze_manifest.json")
    artifacts = {
        "map13_png": ROOT / "outputs/maps/systems/13_energy_grid_compute_futures_2050.png",
        "map13_svg": ROOT / "outputs/maps/systems/13_energy_grid_compute_futures_2050.svg",
        "map13b_png": ROOT / "outputs/maps/systems/13b_energy_grid_compute_futures_2075.png",
        "map13b_svg": ROOT / "outputs/maps/systems/13b_energy_grid_compute_futures_2075.svg",
        "comparison_png": ROOT / "outputs/figures/energy_scenarios_comparison.png",
    }
    for name, path in artifacts.items():
        assert path.exists() and path.stat().st_size > 10000, name
        if path.suffix == ".svg": ET.parse(path)
        else:
            with Image.open(path) as image: image.verify()
    report = {
        "status": "passed",
        "counts": {"assumptions": len(assumptions), "scenario_node_states": len(nodes), "scenario_edge_deltas": len(edges), "comparison_rows": len(comparison)},
        "scenario_ids": list(SCENARIOS),
        "gates": {"phase3a_18_17": True, "phase3b_5_28": True, "phase3a_freeze": True, "phase3b_freeze": True, "future_separated": True, "no_future_mw": True, "no_prohibited_claims": True, "monroe_qualified": True, "oppidan_unverified": True, "maps_valid": True, "comparison_valid": True},
        "artifacts": {name: {"bytes": path.stat().st_size, "sha256": digest(path)} for name, path in artifacts.items()},
    }
    (ROOT / "reports/energy_scenario_artifact_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
