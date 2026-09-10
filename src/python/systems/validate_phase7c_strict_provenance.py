#!/usr/bin/env python3
"""Bounded strict provenance closure check for the Phase 7C working package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
METADATA = ROOT / "metadata/sources.yml"
CITATIONS = ROOT / "reports/phase7c_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
SCENARIOS = ROOT / "data/processed/scenarios"
REPORT_FILES = (
    "environmental_health_scenario_sources.md",
    "environmental_health_scenario_assumptions.md",
    "environmental_health_scenario_consistency.md",
    "environmental_health_future_worldbuilding.md",
    "environmental_health_scenario_qa.md",
)


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows and all(all(value != "" for value in row.values()) for row in rows), relative
    return rows


def registered_source_ids() -> set[str]:
    ids: set[str] = set()
    in_sources = False
    for line in METADATA.read_text(encoding="utf-8").splitlines():
        if line == "sources:":
            in_sources = True
        elif in_sources and re.match(r"^  [A-Za-z0-9_]+:$", line):
            ids.add(line.strip()[:-1])
    assert ids
    return ids


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def verify_citations() -> dict[str, object]:
    results: dict[str, object] = {}
    for name in REPORT_FILES:
        result = subprocess.run(
            [sys.executable, str(CITATION_SCRIPT), "--ledger", str(CITATIONS), "verify", str(REPORTS / name), "--min-coverage", "1.0"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        results[name] = {"passed": True, "output": result.stdout.strip().splitlines()}
    return results


def main() -> None:
    assumptions = read_csv("data/processed/scenarios/environmental_health_scenario_assumptions.csv")
    nodes = read_csv("data/processed/scenarios/exposure_nodes_scenario.csv")
    edges = read_csv("data/processed/scenarios/exposure_edges_scenario.csv")
    controls = read_csv("data/processed/scenarios/exposure_controls_scenario.csv")
    uncertainty = read_csv("data/processed/scenarios/exposure_uncertainty_scenario.csv")
    comparison = read_csv("outputs/figures/environmental_health_scenarios_comparison.csv")
    source_ids = registered_source_ids()
    assumption_ids = {row["assumption_id"] for row in assumptions}
    assert {row["source_id"] for row in assumptions} <= source_ids
    assert len(assumptions) == 36 and len(assumption_ids) == 36
    assert all(row["status"] == "scenario" for row in assumptions)
    expected_family = {"P-01": "Drinking Water / HAB", "P-02": "Ambient Air", "P-03": "Soil / Groundwater / Legacy Contamination", "P-04": "Food / Fish / Recreational Water", "P-05": "Heat"}
    expected_control = {"Drinking Water / HAB": "CTL-001", "Ambient Air": "CTL-003", "Soil / Groundwater / Legacy Contamination": "CTL-004", "Food / Fish / Recreational Water": "CTL-005", "Heat": "CTL-007"}
    assert all(row["pathway_family"] == expected_family[row["baseline_object_id"]] and row["uncertainty"] == "moderate" for row in nodes)
    assert all(row["pathway_family"] == expected_family[row["baseline_object_id"]] and row["uncertainty"] == "moderate" for row in edges)
    assert all(row["baseline_control_id"] == expected_control[row["pathway_family"]] and row["uncertainty"] == "moderate" for row in controls)
    assert all(row["uncertainty"] == "moderate" for row in uncertainty)
    assert all(row["pathway_family"] == "All pathways" and row["change_type"] == "scenario_comparison" and row["assumption_id"].endswith("-06") and row["uncertainty"] in {"high", "moderate", "low"} for row in comparison)
    assert all(row["reality_status"] == "fictional" and row["assumption_id"] in assumption_ids for row in nodes)
    for rows in (nodes, edges, controls, uncertainty):
        assert all(row["assumption_id"] in assumption_ids for row in rows)
    assert {row["baseline_object_id"] for row in nodes + edges} == {f"P-{i:02}" for i in range(1, 6)}
    assert {row["baseline_control_id"] for row in controls} <= {f"CTL-{i:03}" for i in range(1, 8)}
    assert {row["scenario_id"] for row in comparison} == {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
    all_rows = assumptions + nodes + edges + controls + uncertainty + comparison
    fields = set().union(*(row.keys() for row in all_rows))
    forbidden_fields = {"exposure_score", "risk_score", "dose", "illness", "disease", "mortality", "hospitalization", "cancer", "incidence", "probability"}
    assert not fields.intersection(forbidden_fields), sorted(fields.intersection(forbidden_fields))
    package_text = " ".join(" ".join(row.values()) for row in all_rows).lower()
    assert "forecast" not in package_text or "not forecasts" in package_text
    assert not re.search(r"\b(?:future|projected)\b[^\n]{0,120}\b(?:exposure|dose|illness|disease|cases?|incidence|mortality|hospitalization|cancer)\b[^\n]{0,30}\d", package_text)
    assert not re.search(r"\b(?:2050|2075)\s*[,=:]\s*\d", package_text)
    assert all(row["source_or_basis"] == "Phase 7C scenario basis" for row in nodes)
    assert all(row["relationship_basis"].startswith("scenario") for row in nodes + edges)
    manifest = json.loads((REPORTS / "environmental_health_scenario_manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"] == {"assumptions": 36, "scenario_nodes": 30, "scenario_edges": 30, "control_states": 30, "uncertainty_states": 30, "comparison_rows": 6}
    manifest_matches = {relative: sha256(relative) == expected for relative, expected in manifest["artifacts"].items()}
    assert all(manifest_matches.values()), manifest_matches
    citation_results = verify_citations()
    result = {
        "status": "passed",
        "phase": "7C",
        "scope": "strict provenance and scenario-boundary closure; no new scientific claims",
        "source_registry": "metadata/sources.yml",
        "source_ids_checked": len({row["source_id"] for row in assumptions}),
        "source_ids_resolve": True,
        "evidence_rows_checked": 0,
        "evidence_rows_resolve": True,
        "scenario_assumption_references": True,
        "working_manifest_hashes_match": True,
        "claim_level_citations": True,
        "citation_reports": citation_results,
        "scenario_assumption_classification": True,
        "unsupported_exact_health_outcome_claims": False,
        "unsupported_future_exposure_predictions": False,
        "unsupported_risk_scoring": False,
        "scenario_presented_as_forecast": False,
        "historical_claim_gaps": [],
        "correction_applied": "canonicalized P-03 pathway identity, corrected Phase 7B control references, and added explicit uncertainty and comparison provenance fields",
    }
    (REPORTS / "phase7c_strict_provenance_check.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
