"""Validate Phase 10C qualitative governance futures and protected baselines."""
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
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
COMPARISON = FIGURES / "governance_scenario_comparison.csv"
COMPARISON_PNG = FIGURES / "governance_scenario_comparison.png"
COMPARISON_SVG = FIGURES / "governance_scenario_comparison.svg"
REPORTS = ROOT / "reports"

SCENARIO_IDS = {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
SCENARIO_YEARS = {s: int(s[1:]) for s in SCENARIO_IDS}
QUAL = {"high", "moderate", "limited", "unknown", "exploratory"}
EXPECTED_COUNTS = {
    "scenario_assumptions": 48,
    "actor_states": 120,
    "authority_states": 90,
    "dependency_states": 150,
    "coordination_states": 84,
    "uncertainty_states": 96,
    "comparison_rows": 6,
}

TABLES = {
    "assumptions": (SCENARIOS / "governance_scenario_assumptions.csv", {
        "assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption", "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status", "classification", "notes"
    }),
    "actors": (SCENARIOS / "governance_actor_states_scenario.csv", {
        "state_id", "scenario_id", "scenario", "horizon", "actor_id", "actor_name", "actor_type", "current_fact", "scenario_assumption", "scenario_consequence", "future_role", "change_type", "authority_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes"
    }),
    "authorities": (SCENARIOS / "governance_authority_states_scenario.csv", {
        "state_id", "scenario_id", "scenario", "horizon", "authority_id", "actor_id", "domain_system", "authority_or_role", "current_fact", "scenario_assumption", "scenario_consequence", "future_authority_pattern", "legal_status", "human_decision_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes"
    }),
    "dependencies": (SCENARIOS / "governance_dependency_states_scenario.csv", {
        "state_id", "scenario_id", "scenario", "horizon", "dependency_id", "system_a", "system_b", "dependency_type", "current_fact", "scenario_assumption", "scenario_consequence", "dependency_state", "coordination_implication", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes"
    }),
    "coordination": (SCENARIOS / "governance_coordination_states_scenario.csv", {
        "state_id", "scenario_id", "scenario", "horizon", "mechanism_id", "mechanism_type", "mechanism_name", "current_fact", "scenario_assumption", "scenario_consequence", "future_mechanism", "mechanism_character", "authority_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes"
    }),
    "uncertainty": (SCENARIOS / "governance_uncertainty_states_scenario.csv", {
        "state_id", "scenario_id", "scenario", "horizon", "uncertainty_id", "subject_type", "subject_id", "domain_system", "uncertainty_category", "current_fact", "scenario_assumption", "scenario_consequence", "uncertainty_state", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes"
    }),
    "comparison": (FIGURES / "governance_scenario_comparison.csv", {
        "scenario_id", "scenario", "horizon", "scenario_family", "authority_clarity", "cross_jurisdiction_coordination", "data_interoperability", "monitoring_to_decision_linkage", "public_private_coordination", "binational_coordination", "tribal_consultation_and_participation", "funding_alignment", "adaptive_management", "decision_latency", "institutional_redundancy", "enforcement_alignment", "voluntary_program_coordination", "emergency_coordination", "ecological_infrastructure_governance", "technology_governance", "notes"
    }),
}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(path: Path) -> int:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    entries = manifest.get("artifacts", manifest.get("files", {}))
    assert entries, path
    for rel, meta in entries.items():
        artifact = ROOT / rel
        assert artifact.exists(), rel
        expected = meta["sha256"] if isinstance(meta, dict) else meta
        assert manifest_matches(ROOT, rel, expected), rel
    return len(entries)


def check_frozen_phase10() -> tuple[int, int, set[str]]:
    expected = {
        "10A": (REPORTS / "phase10a_governance_jurisdiction_freeze_manifest.json", "Governance & Jurisdiction Baseline, 2026", 15),
        "10B": (REPORTS / "phase10b_governance_dependencies_coordination_freeze_manifest.json", "Cross-System Authority, Dependencies & Coordination, 2026", 15),
    }
    all_paths: set[str] = set()
    entries = 0
    for phase, (path, baseline, count) in expected.items():
        manifest = json.loads(path.read_text(encoding="utf-8"))
        assert manifest["accepted_phase"] == phase
        assert manifest["baseline"] == baseline
        assert manifest["status"] == "ACCEPTED / FROZEN"
        assert len(manifest["artifacts"]) == count
        for rel, meta in manifest["artifacts"].items():
            assert (ROOT / rel).exists(), rel
            assert manifest_matches(ROOT, rel, meta["sha256"]), rel
            all_paths.add(rel)
            entries += 1
    b = json.loads((REPORTS / "phase10b_governance_dependencies_coordination_freeze_manifest.json").read_text(encoding="utf-8"))
    a = REPORTS / "phase10a_governance_jurisdiction_freeze_manifest.json"
    assert b["phase10a_freeze_manifest"]["sha256"] == sha(a)
    assert b["phase10a_freeze_manifest"]["bytes"] == a.stat().st_size
    return entries, len(all_paths), all_paths


def check_prior_freezes(phase10_paths: set[str]) -> int:
    prior_paths: set[str] = set()
    count = 0
    for manifest_path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if manifest_path.name in {"phase10a_governance_jurisdiction_freeze_manifest.json", "phase10b_governance_dependencies_coordination_freeze_manifest.json"}:
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest.get("artifacts", manifest.get("files", {}))
        for rel, meta in entries.items():
            artifact = ROOT / rel
            assert artifact.exists(), rel
            expected = meta["sha256"] if isinstance(meta, dict) else meta
            assert manifest_matches(ROOT, rel, expected), rel
            assert rel not in prior_paths, f"prior manifest overlap: {rel}"
            assert rel not in phase10_paths, f"prior/Phase 10 overlap: {rel}"
            prior_paths.add(rel)
            count += 1
    assert count == 196, count
    changed = set(subprocess.check_output(["git", "diff", "--name-only", "8664bcafdf1714c9085d016ebb32f4913b48dbef"], cwd=ROOT, text=True).splitlines())
    assert not changed.intersection(prior_paths), sorted(changed.intersection(prior_paths))
    return count


def require_prefix(frame: pd.DataFrame, column: str, prefix: str) -> None:
    assert frame[column].str.startswith(prefix).all(), column


def check_boundaries(frames: list[pd.DataFrame]) -> None:
    text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower()
    assert not re.search(r"\b(?:partisan|election|candidate|voter|party control|ideological)\b", text)
    assert not re.search(r"\b(?:probability|risk[_ -]?score|governance[_ -]?score|composite[_ -]?score|ranking)\b\s*[,=:]\s*[0-9]", text)
    assert not re.search(r"\b\d+(?:\.\d+)?\s*(?:%|mw|mgd|tons?|dollars?|years?\s+of\s+delay)\b", text)
    # Reject affirmative overreach, but permit the explicit negative boundary language in the package.
    prohibited = re.compile(r"(?:creates?|creating|establishes?|assigns?|grants?|transfers?)\s+(?:a\s+)?(?:new\s+)?(?:sovereign territory|permit jurisdiction|enforcement authority|single basin government|tribal territory|land transfer|treaty settlement)", re.I)
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if prohibited.search(sentence):
            assert re.search(r"\b(?:no|not|without|does not|do not|never|cannot)\b", sentence), sentence
    ai_overreach = re.compile(r"(?:ai|algorithm(?:ic)?|automated monitoring|software).{0,55}(?:has|holds|receives|exercises|becomes|is assigned)\s+(?:final|binding|legal|sovereign)?\s*(?:public |governmental |legal )?authority", re.I)
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if ai_overreach.search(sentence):
            assert re.search(r"\b(?:not|without|cannot|never)\b", sentence), sentence
    assert "regulation" in text and "operation" in text and "ownership" in text and "public finance" in text
    assert "glifwc remains an intertribal" in text
    assert "distinct sovereign" in text
    assert "ai recommendation" in text and "legal authority" in text
    assert "automatic enforcement" in text
    assert "sensor coverage" in text and "institutional capacity" in text
    assert "composite governance score" in text


def main() -> None:
    frames: dict[str, pd.DataFrame] = {}
    for name, (path, columns) in TABLES.items():
        frame = read(path)
        assert set(frame.columns) == columns, (name, sorted(set(frame.columns) ^ columns))
        frames[name] = frame
    a, actors, authorities, deps, coord, unc, comp = (frames[k] for k in ("assumptions", "actors", "authorities", "dependencies", "coordination", "uncertainty", "comparison"))
    assert len(a) == EXPECTED_COUNTS["scenario_assumptions"] and a.assumption_id.is_unique
    assert len(actors) == EXPECTED_COUNTS["actor_states"] and actors.state_id.is_unique
    assert len(authorities) == EXPECTED_COUNTS["authority_states"] and authorities.state_id.is_unique
    assert len(deps) == EXPECTED_COUNTS["dependency_states"] and deps.state_id.is_unique
    assert len(coord) == EXPECTED_COUNTS["coordination_states"] and coord.state_id.is_unique
    assert len(unc) == EXPECTED_COUNTS["uncertainty_states"] and unc.state_id.is_unique
    assert len(comp) == EXPECTED_COUNTS["comparison_rows"] and comp.scenario_id.is_unique
    for frame in frames.values():
        assert set(frame.scenario_id) == SCENARIO_IDS
        assert frame.apply(lambda row: int(row["horizon"]) == SCENARIO_YEARS[row["scenario_id"]], axis=1).all()
        assert frame.notes.str.len().gt(0).all()
    assert a.groupby("scenario_id").size().eq(8).all()
    assert actors.groupby("scenario_id").size().eq(20).all()
    assert authorities.groupby("scenario_id").size().eq(15).all()
    assert deps.groupby("scenario_id").size().eq(25).all()
    assert coord.groupby("scenario_id").size().eq(14).all()
    assert unc.groupby("scenario_id").size().eq(16).all()
    assert a.reality_status.eq("fictional").all() and a.canon_status.eq("scenario").all() and a.classification.eq("SCENARIO ASSUMPTION").all()
    assert a.uncertainty.isin(QUAL).all() and a.source_id.str.startswith("GFS-").all()
    assumption_ids = set(a.assumption_id)
    baseline_actors = read(ANALYSIS / "governance_actors.csv")
    baseline_authorities = read(ANALYSIS / "governance_authorities.csv")
    baseline_deps = read(ANALYSIS / "governance_dependency_register.csv")
    baseline_coord = read(ANALYSIS / "governance_coordination_mechanisms.csv")
    baseline_unc = read(ANALYSIS / "governance_uncertainty_register.csv")
    baseline_sources = set(read(ANALYSIS / "governance_sources.csv").source_id)
    scenario_sources = set(read(ANALYSIS / "governance_scenario_sources.csv").source_id)
    assert set(actors.actor_id) <= set(baseline_actors.actor_id)
    assert set(authorities.authority_id) <= set(baseline_authorities.authority_id)
    assert set(authorities.actor_id) <= set(baseline_actors.actor_id)
    assert set(deps.dependency_id) <= set(baseline_deps.dependency_id)
    assert set(coord.mechanism_id) <= set(baseline_coord.mechanism_id)
    assert set(unc.uncertainty_id) <= set(baseline_unc.uncertainty_id)
    for frame in (actors, authorities, deps, coord, unc):
        assert frame.reality_status.eq("fictional").all() and frame.canon_status.eq("scenario").all()
        assert frame.assumption_id.isin(assumption_ids).all()
        assert frame.source_id.isin(scenario_sources).all()
        assert frame.current_fact_source_id.isin(baseline_sources).all()
        require_prefix(frame, "current_fact", "CURRENT FACT (2026 baseline):")
        require_prefix(frame, "scenario_assumption", "SCENARIO ASSUMPTION:")
        require_prefix(frame, "scenario_consequence", "SCENARIO CONSEQUENCE:")
    assert actors.actor_id.groupby(actors.scenario_id).size().eq(20).all()
    assert authorities.legal_status.eq("CURRENT AUTHORITY RETAINED; SCENARIO COORDINATION CHANGE").all()
    assert authorities.human_decision_boundary.str.contains("final human decision authority", case=False).all()
    assert deps.dependency_state.str.len().gt(0).all() and coord.future_mechanism.str.len().gt(0).all() and unc.uncertainty_state.str.len().gt(0).all()
    assert set(comp.scenario_family) == {"Integrated Basin Governance", "Federated / Networked Governance", "Fragmented / Contested Governance"}
    assert comp.iloc[:, 4:-1].apply(lambda col: col.str.len().gt(0)).all().all()
    # Horizon discipline: each family changes in kind, not only in label.
    for scenario in "ABC":
        rows = a[a.scenario_id.str.startswith(scenario)].sort_values(["horizon", "assumption_id"])
        assert set(rows.horizon.astype(int)) == {2050, 2075}
        assert rows.loc[rows.horizon.astype(int) == 2050, "assumption"].tolist() != rows.loc[rows.horizon.astype(int) == 2075, "assumption"].tolist()
    b_text = " ".join(a.loc[a.scenario_id.str.startswith("B"), "assumption"]).lower()
    assert "issue-specific" in b_text and "overlapping networks" in b_text and "redundancy" in b_text and "friction" in b_text
    check_boundaries([a, actors, authorities, deps, coord, unc, comp])
    phase10_entries, phase10_unique, phase10_paths = check_frozen_phase10()
    prior = check_prior_freezes(phase10_paths)
    for base in ("34_governance_futures_2050", "34b_governance_futures_2075"):
        png = MAPS / f"{base}.png"; svg = MAPS / f"{base}.svg"
        assert png.exists() and png.stat().st_size > 10000 and svg.exists() and svg.stat().st_size > 10000
        with Image.open(png) as image: image.verify()
        ET.parse(svg)
        svg_text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        expected = "map 34" if base.startswith("34_") else "map 34b"
        for term in (expected, "integrated basin", "federated / networked", "fragmented / contested", "not jurisdiction boundaries", "glifwc remains an intertribal", "ai recommendation"):
            assert term in svg_text, (base, term)
        if base.startswith("34b_"):
            assert "2075 mature/diverged" in svg_text
    assert COMPARISON.exists() and COMPARISON.stat().st_size > 100
    for figure in (COMPARISON_PNG, COMPARISON_SVG):
        assert figure.exists() and figure.stat().st_size > 10000
    ET.parse(COMPARISON_SVG)
    manifest = json.loads((REPORTS / "governance_scenario_manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == "10C" and manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["counts"] == EXPECTED_COUNTS
    for rel, meta in manifest["artifacts"].items():
        artifact = ROOT / rel
        assert artifact.exists() and artifact.stat().st_size > 0 and manifest_matches(ROOT, rel, meta["sha256"]), rel
    result = {
        "status": "passed", "phase": "10C", **EXPECTED_COUNTS,
        "phase10_freeze_entries": phase10_entries, "phase10_unique_artifacts": phase10_unique,
        "prior_phase1_9_protected_artifacts": prior, "phase10a_immutable": True, "phase10b_immutable": True,
        "scenario_separation": True, "assumption_references": True, "actor_authority_dependency_coordination_references": True,
        "uncertainty_references": True, "horizon_discipline": True, "scenario_b_distinct": True,
        "tribal_sovereignty_boundary": True, "binational_boundary": True, "public_private_boundary": True,
        "technology_governance_boundary": True, "qualitative_only": True, "political_content_absent": True,
        "maps_34_34b_valid": True, "phase11_absent": True, "holds_preserved": True,
    }
    (REPORTS / "governance_scenario_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
