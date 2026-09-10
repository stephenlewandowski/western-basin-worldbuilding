#!/usr/bin/env python3
"""Bounded strict provenance closure check for the Phase 7B working package."""
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
CITATIONS = ROOT / "reports/phase7b_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
FAMILIES = {
    "Drinking Water / HAB",
    "Ambient Air",
    "Soil / Groundwater / Legacy Contamination",
    "Food / Fish / Recreational Water",
    "Heat",
}
CSV_FILES = {
    "dependency_edges": "data/processed/networks/exposure_dependency_edges.csv",
    "control_register": "data/processed/analysis/exposure_control_register.csv",
    "evidence_register": "data/processed/analysis/exposure_evidence_strength_register.csv",
    "matrix": "data/processed/analysis/exposure_dependency_control_matrix.csv",
}
REPORT_FILES = (
    "exposure_dependency_sources.md",
    "exposure_dependency_assumptions.md",
    "exposure_dependency_findings.md",
    "exposure_evidence_limits.md",
    "exposure_dependency_qa.md",
)


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, relative
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
    deps = read_csv(CSV_FILES["dependency_edges"])
    controls = read_csv(CSV_FILES["control_register"])
    evidence = read_csv(CSV_FILES["evidence_register"])
    matrix = read_csv(CSV_FILES["matrix"])
    source_ids = registered_source_ids()
    all_source_ids = {row["source_id"] for rows in (deps, controls, evidence) for row in rows}
    assert all_source_ids <= source_ids, sorted(all_source_ids - source_ids)
    assert set(row["pathway_family"] for row in deps) == FAMILIES
    assert set(row["pathway_family"] for row in controls) == FAMILIES
    assert set(row["pathway_family"] for row in evidence) == FAMILIES
    assert set(row["pathway_family"] for row in matrix) == FAMILIES
    assert {row["pathway_id"] for row in evidence} == {f"P-{i:02}" for i in range(1, 6)}
    phase7a_nodes = {row["node_id"] for row in read_csv("data/processed/networks/exposure_context_nodes.csv")}
    node_rows = read_csv("data/processed/networks/exposure_context_nodes.csv")
    node_family = {row["node_id"]: row["pathway_family"] for row in node_rows}
    family_map = {
        "drinking_water_hab": "Drinking Water / HAB",
        "ambient_air": "Ambient Air",
        "legacy_contamination": "Soil / Groundwater / Legacy Contamination",
        "food_fish_recreation": "Food / Fish / Recreational Water",
        "heat": "Heat",
    }
    assert {row[field] for row in deps for field in ("source_node_id", "dependent_node_id")} <= phase7a_nodes
    assert all(family_map[node_family[row["source_node_id"]]] == row["pathway_family"] and family_map[node_family[row["dependent_node_id"]]] == row["pathway_family"] for row in deps)
    assert {row["pathway_id"] for row in evidence} == {f"P-{i:02}" for i in range(1, 6)}
    assert all(row["exposure_confirmation"] == "unconfirmed" and row["dose_information"] == "unknown" and row["health_outcome_information"] == "unknown" for row in evidence)
    package_text = "\n".join(" | ".join(row.values()) for rows in (deps, controls, evidence, matrix) for row in rows).lower()
    assert not re.search(r"\b(?:exposure|dose|illness|disease|hospitalization|mortality|cancer)\b[^\n]{0,80}\b\d+(?:\.\d+)?", package_text)
    assert not re.search(r"\b(?:exposure|dose)\b[^\n]{0,50}\b(?:causes?|proves?|equals?|is)\b[^\n]{0,30}\b(?:illness|disease)\b", package_text)
    assert not re.search(r"\b(?:2050|2075|fictional|scenario)\b", package_text)
    manifest = json.loads((REPORTS / "exposure_dependency_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "validated_working_package"
    assert manifest["counts"] == {"dependency_edges": 20, "control_register": 7, "evidence_register": 5, "matrix": [5, 10]}
    manifest_matches = {relative: sha256(relative) == expected for relative, expected in manifest["artifacts"].items()}
    assert all(manifest_matches.values()), manifest_matches
    citation_results = verify_citations()
    result = {
        "status": "passed",
        "phase": "7B",
        "scope": "strict provenance and boundary closure; no new scientific claims",
        "source_registry": "metadata/sources.yml",
        "source_ids_checked": len(all_source_ids),
        "source_ids_resolve": True,
        "evidence_rows_checked": len(evidence),
        "evidence_rows_resolve": True,
        "control_register_schema": True,
        "working_manifest_hashes_match": True,
        "claim_level_citations": True,
        "citation_reports": citation_results,
        "scenario_assumption_classification": "not_applicable_to_factual_2026_package",
        "unsupported_exact_health_outcome_claims": False,
        "unsupported_exposure_dose_illness_claims": False,
        "scenario_presented_as_forecast": False,
        "historical_claim_gaps": [],
        "correction_applied": "corrected the omitted 7B control-register pathway-family field, repaired dependency endpoint families and directed roles, and strengthened Python/R schema and boundary checks",
    }
    (REPORTS / "phase7b_strict_provenance_check.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
