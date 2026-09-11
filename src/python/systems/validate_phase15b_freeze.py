#!/usr/bin/env python3
"""Independent freeze-boundary validation for accepted Phase 15B."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

FINAL_MANIFEST = "reports/phase15b_technology_convergence_futures_freeze_manifest.json"
WORKING_MANIFEST = "reports/phase15b_manifest.json"
ARTIFACT_CHECK = "reports/phase15b_artifact_check.json"
R_RESULT = "reports/phase15b_r_validation_result.json"
REVIEW = "reports/phase15b_independent_review.md"
INITIAL_REVIEW = "reports/phase15b_independent_review_initial.md"
SECOND_REVIEW = "reports/phase15b_independent_review_second_failed.md"
PHASE15A_FINAL = "reports/phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
PHASE14A_FINAL = "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
PHASE14B_FINAL = "reports/phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
SOURCE_COMMIT = "9b842db483d9ae3f58189607ef17c97d94790102"
EXPECTED_PRIOR_ENTRIES = 565
EXPECTED_PRIOR_UNIQUE = 556
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".txt", ".yml", ".yaml", ".svg", ".toml"}

WORKING_ARTIFACTS = [
    "data/processed/scenarios/technology_convergence_relationships.csv",
    "data/processed/scenarios/technology_dependency_states.csv",
    "data/processed/scenarios/technology_family_states.csv",
    "data/processed/scenarios/technology_governance_states.csv",
    "data/processed/scenarios/technology_scenario_assumptions.csv",
    "data/processed/scenarios/technology_scenario_comparison.csv",
    "data/processed/scenarios/technology_system_states.csv",
    "data/processed/scenarios/technology_uncertainty_states.csv",
    "outputs/figures/technology_convergence_futures.png",
    "outputs/figures/technology_convergence_futures.svg",
    "outputs/figures/technology_cross_system_effects.png",
    "outputs/figures/technology_cross_system_effects.svg",
    ARTIFACT_CHECK,
    "reports/phase15b_biosecurity_futures.md",
    "reports/phase15b_provenance_check.md",
    "reports/phase15b_qa.md",
    R_RESULT,
    "reports/phase15b_scenario_comparison.md",
    "reports/phase15b_technology_convergence_futures.md",
    "src/R/systems/validate_phase15b_technology.R",
    "src/python/systems/build_phase15b_technology.py",
    "src/python/systems/validate_phase15b_technology.py",
]
FREEZE_VALIDATORS = [
    "src/python/systems/validate_phase15b_freeze.py",
    "src/R/systems/validate_phase15b_freeze.R",
]
FINAL_ARTIFACTS = sorted(
    WORKING_ARTIFACTS
    + [
        WORKING_MANIFEST,
        REVIEW,
        INITIAL_REVIEW,
        SECOND_REVIEW,
        *FREEZE_VALIDATORS,
    ]
)

SCENARIO_IDS = {f"{scenario}{year}" for scenario in "ABC" for year in (2050, 2075)}
SCENARIO_FAMILIES = {
    "A": "Coordinated Technological Adaptation",
    "B": "Uneven Networked Modernization",
    "C": "High Capability / High Friction Basin",
}
HORIZONS = {2050, 2075}
FAMILIES = {
    "AI / ADVANCED COMPUTE / AUTOMATION",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS",
    "CYBERSECURITY / DIGITAL RESILIENCE",
    "ADVANCED ENERGY",
    "ADVANCED MATERIALS / MANUFACTURING",
    "QUANTUM TECHNOLOGIES",
    "BIOTECHNOLOGY / GENETIC ENGINEERING",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
}
SCENARIO_TABLES = {
    "technology_scenario_assumptions.csv": (48, "assumption_id"),
    "technology_family_states.csv": (48, "state_id"),
    "technology_convergence_relationships.csv": (60, "relationship_id"),
    "technology_system_states.csv": (78, "state_id"),
    "technology_dependency_states.csv": (72, "dependency_state_id"),
    "technology_governance_states.csv": (48, "governance_state_id"),
    "technology_uncertainty_states.csv": (60, "uncertainty_state_id"),
}
REQUIRED_REVIEW_ARRAYS = (
    "security_concerns",
    "logic_errors",
    "provenance_errors",
    "scenario_boundary_errors",
    "technology_maturity_errors",
    "regional_relevance_errors",
    "governance_boundary_errors",
    "biosecurity_boundary_errors",
    "system_integration_errors",
    "canon_boundary_errors",
)
STATUS_SURFACES = (
    "PROJECT_STATUS.md",
    "docs/canon_status.md",
    "reports/current_phase_handoff.md",
    "README.md",
    "reports/README.md",
    "docs/agent_workflow.md",
    "CHANGELOG.md",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_candidates(path: Path) -> list[tuple[str, int]]:
    raw = path.read_bytes()
    candidates = [(digest(raw), len(raw))]
    if path.suffix in TEXT_SUFFIXES:
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        crlf = normalized.replace(b"\n", b"\r\n")
        candidates.extend(((digest(normalized), len(normalized)), (digest(crlf), len(crlf))))
    return candidates


def artifact_entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(value, dict), "manifest artifact collection is not an object"
    return value


def verify_hash(root: Path, relative: str, metadata: dict[str, Any] | str) -> None:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0, f"missing protected artifact: {relative}"
    expected = metadata if isinstance(metadata, str) else str(metadata["sha256"])
    expected_bytes = None if isinstance(metadata, str) else metadata.get("bytes")
    for actual_hash, actual_bytes in portable_candidates(path):
        if actual_hash == expected and (expected_bytes is None or int(expected_bytes) == actual_bytes):
            return
    raise AssertionError(f"hash/byte mismatch: {relative}")


def load_json(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_manifest(root: Path, relative: str, expected_count: int, expected_inventory: list[str] | None = None) -> dict[str, int]:
    payload = load_json(root, relative)
    entries = artifact_entries(payload)
    assert len(entries) == expected_count, f"{relative}: artifact count {len(entries)}"
    if expected_inventory is not None:
        assert list(entries) == expected_inventory, f"{relative}: artifact inventory differs"
    exact = 0
    normalized = 0
    for path, metadata in entries.items():
        verify_hash(root, path, metadata)
        if isinstance(metadata, str) or digest((root / path).read_bytes()) == metadata.get("sha256"):
            exact += 1
        else:
            normalized += 1
    return {"entries": len(entries), "exact": exact, "newline_normalized": normalized}


def review_verdict(root: Path, relative: str) -> dict[str, Any]:
    text = (root / relative).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert match, f"review JSON block missing: {relative}"
    return json.loads(match.group(1))


def verify_review_lineage(root: Path) -> dict[str, Any]:
    final = review_verdict(root, REVIEW)
    assert "deleg_53b320bb" in (root / REVIEW).read_text(encoding="utf-8")
    assert final.get("passed") is True
    for key in REQUIRED_REVIEW_ARRAYS:
        assert final.get(key) == [], f"{REVIEW}: {key}"
    expected = {
        INITIAL_REVIEW: ("deleg_e21c8764", False),
        SECOND_REVIEW: ("deleg_78928bd2", False),
    }
    preserved = {}
    for relative, (review_id, passed) in expected.items():
        text = (root / relative).read_text(encoding="utf-8")
        assert review_id in text, f"review lineage ID missing: {review_id}"
        verdict = review_verdict(root, relative)
        assert verdict.get("passed") is passed, f"review lineage verdict: {relative}"
        preserved[relative] = {"review_id": review_id, "passed": passed}
    return {"final_review_id": "deleg_53b320bb", "final_passed": True, "preserved": preserved}


def prior_freeze_integrity(root: Path) -> dict[str, Any]:
    entries = 0
    protected: set[str] = set()
    manifests = []
    final_name = Path(FINAL_MANIFEST).name
    for path in sorted((root / "reports").glob("*freeze_manifest.json")):
        if path.name == final_name:
            continue
        manifests.append(path.name)
        payload = load_json(root, f"reports/{path.name}")
        for relative, metadata in artifact_entries(payload).items():
            entries += 1
            normalized = relative.replace("\\", "/")
            protected.add(normalized)
            verify_hash(root, normalized, metadata)
    assert entries == EXPECTED_PRIOR_ENTRIES, entries
    assert len(protected) == EXPECTED_PRIOR_UNIQUE, len(protected)
    return {"manifest_count": len(manifests), "entries": entries, "unique_paths": len(protected), "protected_paths": sorted(protected)}


def changed_paths(root: Path) -> set[str]:
    tracked = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", SOURCE_COMMIT], text=True)
    untracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"], text=True)
    return {line.replace("\\", "/") for line in (tracked + untracked).splitlines() if line}


def check_scenario_table(root: Path, path: Path, expected_count: int, key: str, assumptions: set[str], sources: set[str], system_ids: set[str] | None = None) -> tuple[list[str], list[dict[str, str]]]:
    fields, rows = read_csv(path)
    assert len(rows) == expected_count, (path.name, len(rows))
    assert len({row[key] for row in rows}) == expected_count, path.name
    assert {row["scenario_id"] for row in rows} == SCENARIO_IDS, path.name
    assert all(int(row["horizon"]) in HORIZONS and int(row["horizon"]) == int(row["scenario_id"][1:]) for row in rows), path.name
    assert all(row["assumption_id"] in assumptions and row["source_or_basis"] in sources for row in rows), path.name
    assert all(row["reality_status"] == "scenario" and row["canon_status"] == "scenario" and row["relationship_basis"] == "scenario_assumption" for row in rows), path.name
    assert all(row["uncertainty"] and row["notes"] for row in rows), path.name
    if system_ids is not None:
        assert all(row["system_id"] in system_ids for row in rows), path.name
    return fields, rows


def png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", path
    return int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")


def verify_package(root: Path) -> dict[str, Any]:
    ontology = yaml.safe_load((root / "metadata/atlas_systems.yml").read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology["systems"]}
    assert len(system_ids) == 13
    sources = {row["source_id"] for row in read_csv(root / "data/processed/analysis/technology_sources.csv")[1]}
    assert sources
    scenario_dir = root / "data/processed/scenarios"
    assumptions_fields, assumptions = read_csv(scenario_dir / "technology_scenario_assumptions.csv")
    assert len(assumptions) == 48 and len({row["assumption_id"] for row in assumptions}) == 48
    assert len({row["axis"] for row in assumptions}) == 8
    assert all(row["classification"] == "SCENARIO ASSUMPTION" and row["numeric_future_value_adopted"] == "false" for row in assumptions)
    assumption_ids = {row["assumption_id"] for row in assumptions}

    frames: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    for filename, (expected_count, key) in SCENARIO_TABLES.items():
        path = scenario_dir / filename
        if filename == "technology_scenario_assumptions.csv":
            frames[filename] = (assumptions_fields, assumptions)
        elif filename == "technology_family_states.csv":
            frames[filename] = check_scenario_table(root, path, expected_count, key, assumption_ids, sources)
        elif filename == "technology_system_states.csv":
            frames[filename] = check_scenario_table(root, path, expected_count, key, assumption_ids, sources, system_ids)
        else:
            frames[filename] = check_scenario_table(root, path, expected_count, key, assumption_ids, sources)

    family_rows = frames["technology_family_states.csv"][1]
    assert {row["technology_family"] for row in family_rows} == FAMILIES
    assert all(Counter(row["scenario_id"] for row in family_rows if row["technology_family"] == family) == Counter(SCENARIO_IDS) for family in FAMILIES)

    convergence_rows = frames["technology_convergence_relationships.csv"][1]
    assert all(row["technology_family_a"] in FAMILIES and row["technology_family_b"] in FAMILIES for row in convergence_rows)
    assert all(set(row["affected_system_ids"].split(";")) <= system_ids and row["affected_system_ids"] for row in convergence_rows)

    system_rows = frames["technology_system_states.csv"][1]
    assert {row["system_id"] for row in system_rows} == system_ids
    assert all(Counter(row["scenario_id"] for row in system_rows if row["system_id"] == system_id) == Counter(SCENARIO_IDS) for system_id in system_ids)

    dependency_rows = frames["technology_dependency_states.csv"][1]
    assert all(row["system_a"] in system_ids and row["system_b"] in system_ids and row["technology_family"] in FAMILIES for row in dependency_rows)
    assert {row["dependency_change_type"] for row in dependency_rows} <= {"intensified_existing_dependency", "substituted_some_dependency", "redistributed_across_nodes", "intensified_and_brittle_dependency"}
    assert all("not a risk" in row["notes"].lower() and row["governance_implication"] for row in dependency_rows)

    governance_rows = frames["technology_governance_states.csv"][1]
    assert all(row["technology_family"] in FAMILIES for row in governance_rows)
    governance_text = " ".join(" ".join(row.values()) for row in governance_rows).lower()
    assert "ai recommendation remains advisory" in governance_text
    assert "measurement and observability do not create enforcement" in governance_text

    uncertainty_rows = frames["technology_uncertainty_states.csv"][1]
    assert len({row["uncertainty_domain"] for row in uncertainty_rows}) == 10
    assert all(row["what_is_not_inferred"] and "unknown" in row["notes"].lower() for row in uncertainty_rows)

    comparison_fields, comparison_rows = read_csv(scenario_dir / "technology_scenario_comparison.csv")
    assert len(comparison_rows) == 6 and {row["scenario_id"] for row in comparison_rows} == SCENARIO_IDS
    assert not any("score" in field.lower() or "probability" in field.lower() for field in comparison_fields)
    assert all("winner" in row["boundary_statement"].lower() or "winner" in row["notes"].lower() for row in comparison_rows)

    model_text = " ".join(" ".join(str(value) for value in row.values()) for fields, rows in [*frames.values(), (comparison_fields, comparison_rows)] for row in rows).lower()
    assert not re.search(r"\b\d+(?:\.\d+)?\s*%", model_text)
    forbidden_fields = {"risk_score", "resilience_score", "readiness_score", "connectivity_score", "performance_score", "scenario_probability", "deployment_percentage", "adoption_percentage"}
    all_fields = set().union(*(set(fields) for fields, _ in [*frames.values(), (comparison_fields, comparison_rows)]))
    assert not forbidden_fields.intersection(all_fields)
    assert all(term in model_text for term in ("scenario", "not a forecast", "not a score", "not a basin deployment"))

    biosecurity = (root / "reports/phase15b_biosecurity_futures.md").read_text(encoding="utf-8").lower()
    for term in ("diagnostic speed", "attribution uncertainty", "laboratory/diagnostic capacity", "supply-chain resilience", "public communication", "dual-use governance", "no pathogen design", "wet-lab procedure"):
        assert term in biosecurity, term

    for name, dimensions in {
        "technology_convergence_futures.png": (2700, 1530),
        "technology_cross_system_effects.png": (2700, 1620),
    }.items():
        path = root / "outputs/figures" / name
        assert png_dimensions(path) == dimensions, (name, png_dimensions(path))
    for name, required in {
        "technology_convergence_futures.svg": ("Technology Convergence Futures", "2050", "2075", "No score"),
        "technology_cross_system_effects.svg": ("Cross-System Technology Effects", "observability", "human authority", "coupling"),
    }.items():
        path = root / "outputs/figures" / name
        ET.parse(path)
        text = path.read_text(encoding="utf-8").lower()
        assert all(term.lower() in text for term in required), name

    r_source = (root / "src/R/systems/validate_phase15b_technology.R").read_text(encoding="utf-8")
    assert "unsupported_percentage <- grepl" in r_source
    assert "if (unsupported_percentage) stop(" in r_source
    return {
        "scenario_horizon_states": 6,
        "assumptions": len(assumptions),
        "technology_family_states": len(family_rows),
        "convergence_relationships": len(convergence_rows),
        "system_states": len(system_rows),
        "dependency_states": len(dependency_rows),
        "governance_states": len(governance_rows),
        "uncertainty_states": len(uncertainty_rows),
        "comparison_rows": len(comparison_rows),
        "technology_families": len(FAMILIES),
        "phase14_systems": len(system_ids),
        "figure_dimensions": {"technology_convergence_futures": [2700, 1530], "technology_cross_system_effects": [2700, 1620]},
    }


def verify_status(root: Path) -> None:
    required = (
        "phase 15b",
        "accepted / frozen",
        Path(FINAL_MANIFEST).name,
        "phase 16",
        "not implemented",
        "great black swamp",
        "hold",
        "toledo intake-coordinate discrepancy",
        "unresolved",
        "no release or tag",
    )
    for relative in STATUS_SURFACES:
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in required:
            assert term in text, f"{relative}: missing {term}"
    for relative in STATUS_SURFACES[:-1]:
        text = (root / relative).read_text(encoding="utf-8").lower()
        assert "phase 14" in text and "complete" in text, f"{relative}: Phase 14 completion missing"
    for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        for term in ("phase 6b manifest status wording mismatch", "phase 3a missing manifest status", "phase 2a superseded legacy worktree"):
            assert term in text, f"{relative}: missing {term}"
    assert all("phase 15b is **accepted / frozen**" in (root / relative).read_text(encoding="utf-8").lower() for relative in STATUS_SURFACES if relative != "CHANGELOG.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]

    final = load_json(root, FINAL_MANIFEST)
    assert final["accepted_phase"] == "15B"
    assert final["baseline"] == "Technology Convergence Futures, 2050 / 2075"
    assert final["status"] == "ACCEPTED / FROZEN"
    assert final["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert final["accepted_date"] == "2026-09-11"
    assert final["source_commit"] == SOURCE_COMMIT
    assert final["counts"] == {
        "scenario_horizon_states": 6,
        "assumptions": 48,
        "technology_family_states": 48,
        "convergence_relationships": 60,
        "system_states": 78,
        "dependency_states": 72,
        "governance_states": 48,
        "uncertainty_states": 60,
        "comparison_rows": 6,
        "technology_families": 8,
        "phase14_systems": 13,
    }
    assert final["scenario_families"] == SCENARIO_FAMILIES
    assert final["horizons"] == [2050, 2075]
    assert final["qualitative_only"] is True and final["forecast"] is False and final["numeric_future_values_adopted"] is False
    assert final["phase15a_status"] == "ACCEPTED / FROZEN"
    assert final["phase14_status"] == "COMPLETE / ACCEPTED / FROZEN"
    assert final["phase16_status"] == "NOT IMPLEMENTED"
    assert final["active_holds_preserved"] == {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}
    assert final["deferred_maintenance_preserved"] == ["Phase 6B manifest status wording mismatch", "Phase 3A missing manifest status", "Phase 2A superseded legacy worktree"]
    assert final["release_created"] is False and final["tag_created"] is False
    assert final["final_manifest_path"] == FINAL_MANIFEST
    assert FINAL_MANIFEST not in artifact_entries(final)
    final_result = verify_manifest(root, FINAL_MANIFEST, len(FINAL_ARTIFACTS), FINAL_ARTIFACTS)

    working = load_json(root, WORKING_MANIFEST)
    assert working["phase"] == "15B" and working["status"] == "implemented_validated_pending_sol_acceptance" and working["source_commit"] == "b8baa403316e56ce7a1266e1cf37d4839536dabc"
    working_result = verify_manifest(root, WORKING_MANIFEST, len(WORKING_ARTIFACTS), sorted(WORKING_ARTIFACTS))
    artifact_check = load_json(root, ARTIFACT_CHECK)
    assert artifact_check["phase"] == "15B" and artifact_check["passed"] is True and artifact_check["errors"] == []
    assert artifact_check["counts"]["prior_freeze_entries"] == EXPECTED_PRIOR_ENTRIES and artifact_check["counts"]["prior_freeze_unique_paths"] == EXPECTED_PRIOR_UNIQUE
    r_result = load_json(root, R_RESULT)
    assert r_result["phase"] == "15B" and r_result["passed"] is True

    phase15a = load_json(root, PHASE15A_FINAL)
    phase14a = load_json(root, PHASE14A_FINAL)
    phase14b = load_json(root, PHASE14B_FINAL)
    assert phase15a["accepted_phase"] == "15A" and phase15a["status"] == "ACCEPTED / FROZEN"
    assert phase14a["accepted_phase"] == "14A" and phase14a["status"] == "ACCEPTED / FROZEN"
    assert phase14b["accepted_phase"] == "14B" and phase14b["status"] == "ACCEPTED / FROZEN" and phase14b["phase14_overall_status"] == "COMPLETE / ACCEPTED / FROZEN"
    phase15a_result = verify_manifest(root, PHASE15A_FINAL, 30)
    phase14a_result = verify_manifest(root, PHASE14A_FINAL, 24)
    phase14b_result = verify_manifest(root, PHASE14B_FINAL, 23)

    package = verify_package(root)
    prior = prior_freeze_integrity(root)
    prior_paths = set(prior["protected_paths"])
    changed = changed_paths(root)
    assert not (changed & prior_paths), sorted(changed & prior_paths)
    assert not (changed & set(WORKING_ARTIFACTS + [REVIEW, INITIAL_REVIEW, SECOND_REVIEW])), sorted(changed & set(WORKING_ARTIFACTS + [REVIEW, INITIAL_REVIEW, SECOND_REVIEW]))
    allowed = set(list(STATUS_SURFACES) + [FINAL_MANIFEST] + FREEZE_VALIDATORS)
    assert changed <= allowed, sorted(changed - allowed)
    assert not any("phase16" in path.lower() for path in changed if not path.startswith("docs/phase_briefs/"))

    review = verify_review_lineage(root)
    verify_status(root)
    print(json.dumps({
        "status": "passed",
        "phase": "15B",
        "final_manifest": {"path": FINAL_MANIFEST, **final_result},
        "working_manifest": {"path": WORKING_MANIFEST, **working_result},
        "package": package,
        "phase15a_integrity": phase15a_result,
        "phase14_integrity": {"phase14a": phase14a_result, "phase14b": phase14b_result},
        "prior_freeze_integrity": {key: value for key, value in prior.items() if key != "protected_paths"},
        "review_lineage": review,
        "changed_paths_from_source_commit": len(changed),
        "release_created": False,
        "tag_created": False,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
