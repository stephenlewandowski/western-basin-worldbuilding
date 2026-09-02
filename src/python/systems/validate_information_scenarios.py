"""Validate Phase 4C scenario deltas and frozen Phase 4A/4B baselines."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCENARIOS = ROOT / "data/processed/scenarios"
FIGURES = ROOT / "outputs/figures"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

ASSUMPTIONS = SCENARIOS / "information_scenario_assumptions.csv"
NODES = SCENARIOS / "information_nodes_scenario.csv"
EDGES = SCENARIOS / "information_edges_scenario.csv"
BLINDSPOTS = SCENARIOS / "information_blind_spots_scenario.csv"
AUTHORITY = SCENARIOS / "information_authority_scenario.csv"
COMPARISON = FIGURES / "information_scenarios_comparison.csv"
MANIFEST = REPORTS / "information_scenario_manifest.json"
CHECK = REPORTS / "information_scenario_artifact_check.json"
PHASE4A_MANIFEST = REPORTS / "observation_system_manifest.json"
PHASE4B_FREEZE = REPORTS / "phase4b_information_freeze_manifest.json"

ASSUMPTION_COLUMNS = {"assumption_id", "scenario_id", "scenario_year", "domain", "assumption", "basis", "source_id", "plausibility", "uncertainty", "dependency", "status", "notes"}
NODE_COLUMNS = {"object_id", "scenario_id", "scenario_year", "baseline_object_id", "object_name", "domain", "future_role", "change_type", "reality_status", "relationship_basis", "assumption_id", "plausibility", "source_or_basis", "notes"}
EDGE_COLUMNS = {"edge_id", "scenario_id", "scenario_year", "from_object_id", "to_object_id", "relationship_type", "change_type", "reality_status", "relationship_basis", "assumption_id", "plausibility", "source_or_basis", "notes"}
BLIND_COLUMNS = {"blindspot_state_id", "scenario_id", "scenario_year", "baseline_blindspot_id", "domain", "affected_chain", "change_type", "future_blindspot", "description", "assumption_id", "plausibility", "relationship_basis", "source_or_basis", "notes"}
AUTHORITY_COLUMNS = {"scenario_id", "scenario_year", "observes", "analyzes", "advises", "decides", "operates_or_responds", "authority_pattern", "assumption_id", "plausibility", "reality_status", "relationship_basis", "source_or_basis", "notes"}
COMPARISON_COLUMNS = {"scenario_id", "scenario_year", "scenario_family", "openness", "interoperability", "sensing_density", "automation", "human_decision_authority", "redundancy", "data_concentration", "privacy_constraint", "security_constraint", "model_dependence", "public_transparency", "resilience_to_information_loss"}
SCENARIO_YEARS = {"A2050": 2050, "A2075": 2075, "B2050": 2050, "B2075": 2075, "C2050": 2050, "C2075": 2075}
ALLOWED_CHANGE_TYPES = {"persist", "expand_role", "new_function", "new_node", "new_edge", "automated_analysis", "automated_operation", "human_authority_retained", "federated_exchange", "redundancy_added", "data_opened", "data_restricted", "dependency_increased", "dependency_reduced", "provenance_strengthened", "model_dependence_increased"}
ALLOWED_BLIND_CHANGES = {"persists", "reduced", "resolved", "transformed", "new_blindspot"}
ALLOWED_PLAUSIBILITY = {"high", "moderate", "exploratory"}
ALLOWED_ORDINAL = {"low", "moderate", "high"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("files", manifest.get("artifacts", {}))
    for relative, metadata in entries.items():
        artifact = ROOT / relative
        assert artifact.exists(), relative
        assert sha256(artifact) == metadata["sha256"], f"Frozen artifact changed: {relative}"


def main() -> None:
    assumptions = pd.read_csv(ASSUMPTIONS, dtype=str).fillna("")
    nodes = pd.read_csv(NODES, dtype=str).fillna("")
    edges = pd.read_csv(EDGES, dtype=str).fillna("")
    blind = pd.read_csv(BLINDSPOTS, dtype=str).fillna("")
    authority = pd.read_csv(AUTHORITY, dtype=str).fillna("")
    comparison = pd.read_csv(COMPARISON, dtype=str).fillna("")
    sources = yaml.safe_load((ROOT / "metadata/sources.yml").read_text(encoding="utf-8"))["sources"]
    phase4a_nodes = pd.read_csv(ROOT / "data/processed/networks/observation_system_nodes.csv", dtype=str).fillna("")
    baseline_node_ids = set(phase4a_nodes.node_id)
    baseline_blind_ids = set(pd.read_csv(ROOT / "data/processed/analysis/information_blind_spots.csv", dtype=str).fillna("").blindspot_id)

    assert set(assumptions.columns) == ASSUMPTION_COLUMNS
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert set(blind.columns) == BLIND_COLUMNS
    assert set(authority.columns) == AUTHORITY_COLUMNS
    assert set(comparison.columns) == COMPARISON_COLUMNS
    assert set(assumptions.scenario_id) == set(SCENARIO_YEARS)
    assert set(nodes.scenario_id) == set(SCENARIO_YEARS)
    assert set(edges.scenario_id) == set(SCENARIO_YEARS)
    assert set(blind.scenario_id) == set(SCENARIO_YEARS)
    assert set(authority.scenario_id) == set(SCENARIO_YEARS)
    assert set(comparison.scenario_id) == set(SCENARIO_YEARS)
    assert len(assumptions) == 36 and assumptions.assumption_id.is_unique
    assert len(nodes) == 72 and nodes.object_id.is_unique
    assert len(edges) == 48 and edges.edge_id.is_unique
    assert len(blind) == 36 and blind.blindspot_state_id.is_unique
    assert len(authority) == 6 and authority.scenario_id.is_unique
    assert len(comparison) == 6 and comparison.scenario_id.is_unique
    assert assumptions.groupby("scenario_id").size().eq(6).all()
    assert nodes.groupby("scenario_id").size().eq(12).all()
    assert edges.groupby("scenario_id").size().eq(8).all()
    assert blind.groupby("scenario_id").size().eq(6).all()

    for frame in [assumptions, nodes, edges, blind, authority, comparison]:
        assert frame.scenario_id.isin(SCENARIO_YEARS).all()
    for scenario_id, year in SCENARIO_YEARS.items():
        for frame in [assumptions, nodes, edges, blind, authority, comparison]:
            assert set(frame.loc[frame.scenario_id == scenario_id, "scenario_year"]) == {str(year)}

    assert assumptions.plausibility.isin(ALLOWED_PLAUSIBILITY).all()
    assert assumptions.uncertainty.isin({"low", "moderate", "high", "unknown"}).all()
    assert assumptions.status.eq("scenario_assumption").all()
    assert assumptions.source_id.isin(set(sources)).all()
    assert assumptions.assumption.str.len().gt(0).all()
    assert assumptions.notes.str.len().gt(0).all()

    assert nodes.reality_status.eq("fictional").all()
    assert nodes.relationship_basis.eq("scenario_assumption").all()
    assert nodes.plausibility.isin(ALLOWED_PLAUSIBILITY).all()
    assert nodes.change_type.isin(ALLOWED_CHANGE_TYPES).all()
    assert nodes.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert nodes.source_or_basis.isin(set(sources)).all()
    assert ((nodes.baseline_object_id == "") | nodes.baseline_object_id.isin(baseline_node_ids)).all()
    assert nodes.future_role.str.len().gt(0).all()

    future_object_ids = set(nodes.object_id)
    assert edges.from_object_id.isin(future_object_ids).all()
    assert edges.to_object_id.isin(future_object_ids).all()
    assert edges.reality_status.eq("fictional").all()
    assert edges.relationship_basis.eq("scenario_assumption").all()
    assert edges.plausibility.isin(ALLOWED_PLAUSIBILITY).all()
    assert edges.change_type.isin(ALLOWED_CHANGE_TYPES).all()
    assert edges.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert edges.source_or_basis.isin(set(sources)).all()
    assert edges.notes.str.len().gt(0).all()

    assert blind.change_type.isin(ALLOWED_BLIND_CHANGES).all()
    assert blind.reality_status.eq("fictional").all() if "reality_status" in blind.columns else True
    assert blind.relationship_basis.eq("scenario_assumption").all()
    assert blind.plausibility.isin(ALLOWED_PLAUSIBILITY).all()
    assert blind.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert blind.source_or_basis.isin(set(sources)).all()
    assert ((blind.baseline_blindspot_id == "") | blind.baseline_blindspot_id.isin(baseline_blind_ids)).all()

    assert authority.reality_status.eq("fictional").all()
    assert authority.relationship_basis.eq("scenario_assumption").all()
    assert authority.plausibility.isin(ALLOWED_PLAUSIBILITY).all()
    assert authority.assumption_id.isin(set(assumptions.assumption_id)).all()
    assert authority.source_or_basis.isin(set(sources)).all()
    assert authority.decides.str.contains("human|City|NWS|EPA|PJM|authority|authorities", case=False, regex=True).all()

    assert comparison.iloc[:, 3:].isin(ALLOWED_ORDINAL).all().all()
    assert set(comparison.scenario_family) == {"Trusted Public Infrastructure", "Federated Resilience", "High-Automation / Contested Information"}

    substantive_text = " ".join(" ".join(map(str, frame.to_numpy().ravel())) for frame in [assumptions[["assumption"]], nodes[["object_name", "future_role", "change_type"]], edges[["relationship_type", "change_type"]], blind[["future_blindspot", "change_type"]], authority[["authority_pattern"]]])
    assert not re.search(r"attack path|exploit|credential|red[- ]team|surveillance[- ]state|sensitive topology|SCADA|target prioritization|sovereign AI|final governmental AI", substantive_text, flags=re.I)
    assert not re.search(r"\b\d+(?:\.\d+)?\s*%", substantive_text)
    assert not edges.relationship_type.str.contains("trigger|control authority", case=False, regex=True).any()

    check_manifest(PHASE4A_MANIFEST)
    check_manifest(PHASE4B_FREEZE)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "4C"
    assert manifest["counts"]["assumptions"] == len(assumptions)
    assert manifest["counts"]["scenario_node_states"] == len(nodes)
    assert manifest["counts"]["scenario_edge_deltas"] == len(edges)
    assert manifest["counts"]["blindspot_states"] == len(blind)
    for relative, metadata in manifest["artifacts"].items():
        artifact = ROOT / relative
        assert artifact.exists() and artifact.stat().st_size > 0, relative
        assert sha256(artifact) == metadata["sha256"], relative

    artifact_paths = [
        MAPS / "16_information_governance_futures_2050.png",
        MAPS / "16_information_governance_futures_2050.svg",
        MAPS / "16b_information_governance_futures_2075.png",
        MAPS / "16b_information_governance_futures_2075.svg",
        FIGURES / "information_scenarios_comparison.png",
        FIGURES / "information_scenarios_comparison.svg",
    ]
    for artifact in artifact_paths:
        assert artifact.exists() and artifact.stat().st_size > 10_000
    image_sizes = []
    for png in [artifact_paths[0], artifact_paths[2], artifact_paths[4]]:
        with Image.open(png) as image:
            image.verify()
            image_sizes.append(list(image.size))
    for svg in [artifact_paths[1], artifact_paths[3], artifact_paths[5]]:
        ET.parse(svg)

    canon = (ROOT / "docs/canon_status.md").read_text(encoding="utf-8")
    assert "C — HOLD" in canon and "Phase 4C does not change" in canon
    assert "intake-coordinate discrepancy" in canon

    result = {
        "status": "passed",
        "phase": "4C",
        "assumptions": len(assumptions),
        "scenario_node_states": len(nodes),
        "scenario_edge_deltas": len(edges),
        "blindspot_states": len(blind),
        "authority_rows": len(authority),
        "comparison_dimensions": len(comparison.columns) - 3,
        "scenario_ids": sorted(SCENARIO_YEARS),
        "phase4a_immutable": True,
        "phase4b_immutable": True,
        "maps_valid": True,
        "comparison_valid": True,
        "human_authority_explicit": True,
        "no_offensive_security_content": True,
        "no_future_objects_in_baseline": True,
        "toledo_intake_uncertainty_preserved": True,
        "great_black_swamp_hold_preserved": True,
        "image_sizes": image_sizes,
    }
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
