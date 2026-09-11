"""Independent Python validator for Phase 15B technology-convergence futures."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCENARIO_DIR = ROOT / "data/processed/scenarios"
ANALYSIS = ROOT / "data/processed/analysis"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "outputs/figures"
SYSTEMS_YAML = ROOT / "metadata/atlas_systems.yml"
BASELINE_NODES = ANALYSIS / "technology_system_nodes.csv"
BASELINE_SOURCES = ANALYSIS / "technology_sources.csv"
MANIFEST = REPORTS / "phase15b_manifest.json"
CHECK = REPORTS / "phase15b_artifact_check.json"
PHASE15A_FREEZE = REPORTS / "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
PHASE14A_FREEZE = REPORTS / "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
PHASE14B_FREEZE = REPORTS / "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
BASE_SHA = "b8baa403316e56ce7a1266e1cf37d4839536dabc"

SCENARIO_IDS = {f"{scenario}{year}" for scenario in "ABC" for year in (2050, 2075)}
SCENARIOS = {"A", "B", "C"}
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
FAMILY_BY_LABEL = {value: value for value in FAMILIES}
FAMILY_STATE = SCENARIO_DIR / "technology_family_states.csv"
ASSUMPTIONS = SCENARIO_DIR / "technology_scenario_assumptions.csv"
CONVERGENCES = SCENARIO_DIR / "technology_convergence_relationships.csv"
SYSTEM_STATES = SCENARIO_DIR / "technology_system_states.csv"
DEPENDENCIES = SCENARIO_DIR / "technology_dependency_states.csv"
GOVERNANCE = SCENARIO_DIR / "technology_governance_states.csv"
UNCERTAINTIES = SCENARIO_DIR / "technology_uncertainty_states.csv"
COMPARISON = SCENARIO_DIR / "technology_scenario_comparison.csv"
REVIEW = REPORTS / "phase15b_independent_review.md"

EXPECTED_COLUMNS = {
    ASSUMPTIONS.name: {"assumption_id", "scenario_id", "scenario_family", "horizon", "axis", "assumption", "evidence_basis", "source_or_basis", "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes"},
    FAMILY_STATE.name: {"state_id", "scenario_id", "scenario_family", "horizon", "technology_family", "baseline_2026_status", "baseline_2026_relevance", "capability_state", "maturity_state", "adoption_state", "infrastructure_state", "interoperability_state", "governance_state", "trust_legitimacy_state", "cybersecurity_state", "workforce_state", "energy_compute_material_state", "privacy_surveillance_state", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    CONVERGENCES.name: {"relationship_id", "scenario_id", "scenario_family", "horizon", "technology_family_a", "technology_family_b", "convergence_mechanism", "enabling_conditions", "limiting_conditions", "affected_system_ids", "evidence_basis", "scenario_dependence", "governance_implications", "uncertainty", "second_order_effects", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    SYSTEM_STATES.name: {"state_id", "scenario_id", "scenario_family", "horizon", "system_id", "technology_family", "convergence_mechanism", "state_direction", "dependency_change", "governance_effect", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    DEPENDENCIES.name: {"dependency_state_id", "scenario_id", "scenario_family", "horizon", "system_a", "system_b", "technology_family", "dependency_change_type", "dependency_state", "enabling_conditions", "limiting_conditions", "governance_implication", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    GOVERNANCE.name: {"governance_state_id", "scenario_id", "scenario_family", "horizon", "governance_domain", "technology_family", "governance_state", "oversight_capacity", "trust_legitimacy_state", "privacy_surveillance_balance", "public_communication_state", "workforce_maintenance_state", "human_authority_boundary", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    UNCERTAINTIES.name: {"uncertainty_state_id", "scenario_id", "scenario_family", "horizon", "uncertainty_domain", "subject", "uncertainty_level", "uncertainty", "scenario_dependence", "what_is_not_inferred", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"},
    COMPARISON.name: {"scenario_id", "scenario_family", "horizon", "technology_maturity", "regional_adoption", "infrastructure_adequacy", "interoperability", "governance_capacity", "trust_legitimacy", "cyber_digital_resilience", "workforce_capability", "energy_compute_dependency", "system_coupling", "biosecurity_capacity", "equity_unevenness", "boundary_statement", "notes"},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    assert path.is_file() and path.stat().st_size > 0, path
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def hash_matches(path: Path, expected: str) -> bool:
    raw = path.read_bytes()
    return digest(raw) == expected or digest(normalized(raw)) == expected


def entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    assert isinstance(value, dict)
    return value


def verify_manifest(path: Path, expected_phase: str, expected_status: str | None = None, expected_count: int | None = None) -> tuple[dict[str, Any], set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload.get("accepted_phase") == expected_phase, path
    if expected_status is not None:
        assert payload.get("status") == expected_status, path
    artifact_entries = entries(payload)
    if expected_count is not None:
        assert len(artifact_entries) == expected_count, (path, len(artifact_entries))
    protected = set()
    for relative, metadata in artifact_entries.items():
        expected = metadata if isinstance(metadata, str) else str(metadata.get("sha256", ""))
        target = ROOT / relative
        assert target.is_file() and target.stat().st_size > 0, relative
        assert hash_matches(target, expected), relative
        protected.add(relative.replace("\\", "/"))
    return payload, protected


def prior_integrity() -> tuple[int, set[str]]:
    total = 0
    protected: set[str] = set()
    for path in sorted(REPORTS.glob("*freeze_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in entries(payload).items():
            expected = metadata if isinstance(metadata, str) else str(metadata.get("sha256", ""))
            target = ROOT / relative
            assert target.is_file() and hash_matches(target, expected), (path.name, relative)
            total += 1
            protected.add(relative.replace("\\", "/"))
    return total, protected


def scenario_check(frame: list[dict[str, str]], unique_key: str, expected_count: int, assumption_ids: set[str], source_ids: set[str], system_ids: set[str] | None = None) -> None:
    assert frame and len(frame) == expected_count
    assert len({row[unique_key] for row in frame}) == len(frame)
    assert {row["scenario_id"] for row in frame} == SCENARIO_IDS
    assert all(int(row["horizon"]) == int(row["scenario_id"][1:]) for row in frame)
    assert all(row["assumption_id"] in assumption_ids for row in frame)
    assert all(row["source_or_basis"] in source_ids for row in frame)
    assert all(row["reality_status"] == "scenario" and row["canon_status"] == "scenario" and row["relationship_basis"] == "scenario_assumption" for row in frame)
    assert all(row["notes"] and row["uncertainty"] for row in frame)
    if system_ids is not None:
        assert all(row["system_id"] in system_ids for row in frame)


def split_ids(value: str) -> set[str]:
    return {item for item in value.split(";") if item}


def main() -> int:
    require_review = "--require-review" in sys.argv
    checks: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: Any) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    phase15a, phase15a_paths = verify_manifest(PHASE15A_FREEZE, "15A", "ACCEPTED / FROZEN", 30)
    phase14a, phase14a_paths = verify_manifest(PHASE14A_FREEZE, "14A", "ACCEPTED / FROZEN", 24)
    phase14b, phase14b_paths = verify_manifest(PHASE14B_FREEZE, "14B", "ACCEPTED / FROZEN", 23)
    prior_total, prior_paths = prior_integrity()
    changed = {line.replace("\\", "/") for line in subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines()}
    protected = prior_paths | phase15a_paths | phase14a_paths | phase14b_paths
    check("phase15a_accepted_frozen", phase15a.get("status") == "ACCEPTED / FROZEN", phase15a.get("status"))
    check("phase15a_protected_artifact_count", len(phase15a_paths) == 30, len(phase15a_paths))
    check("phase14_complete_accepted_frozen", phase14b.get("phase14_overall_status") == "COMPLETE / ACCEPTED / FROZEN", phase14b.get("phase14_overall_status"))
    check("phase14a_and_14b_accepted_frozen", phase14a.get("status") == "ACCEPTED / FROZEN" and phase14b.get("status") == "ACCEPTED / FROZEN", (phase14a.get("status"), phase14b.get("status")))
    check("prior_freeze_integrity", prior_total == 565 and len(prior_paths) == 556, {"entries": prior_total, "unique_paths": len(prior_paths)})
    check("no_frozen_artifact_modified", not changed.intersection(protected), sorted(changed.intersection(protected)))
    check("expected_starting_sha", subprocess.check_output(["git", "-C", str(ROOT), "merge-base", "HEAD", BASE_SHA], text=True).strip() == BASE_SHA, BASE_SHA)
    check("phase16_absent", not any("phase16" in path.lower() for path in changed if path.startswith(("data/", "outputs/", "src/"))), sorted(path for path in changed if "phase16" in path.lower()))
    check("no_release_or_tag", not any(path.startswith(".github/") and "release" in path.lower() for path in changed), "release/tag artifacts are out of scope")

    ontology = yaml.safe_load(SYSTEMS_YAML.read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology["systems"]}
    source_rows = read_csv(BASELINE_SOURCES)
    source_ids = {row["source_id"] for row in source_rows}
    baseline_nodes = read_csv(BASELINE_NODES)
    technology_ids = {row["technology_id"] for row in baseline_nodes}
    baseline_families = {row["technology_family"] for row in baseline_nodes}
    check("phase14_ontology_has_13_systems", len(system_ids) == 13, len(system_ids))
    check("eight_phase15a_families", baseline_families == FAMILIES, sorted(baseline_families))
    check("phase15a_source_registry_unique", len(source_ids) == len(source_rows), len(source_rows))

    frames = {path.name: read_csv(path) for path in (ASSUMPTIONS, FAMILY_STATE, CONVERGENCES, SYSTEM_STATES, DEPENDENCIES, GOVERNANCE, UNCERTAINTIES, COMPARISON)}
    for name, frame in frames.items():
        check(f"schema_{name}", set(frame[0]) == EXPECTED_COLUMNS[name], sorted(set(frame[0]) ^ EXPECTED_COLUMNS[name]))

    assumptions = frames[ASSUMPTIONS.name]
    assumption_ids = {row["assumption_id"] for row in assumptions}
    check("assumption_count_and_ids", len(assumptions) == 48 and len(assumption_ids) == 48, len(assumptions))
    check("assumption_scenario_horizon", {row["scenario_id"] for row in assumptions} == SCENARIO_IDS and all(int(row["horizon"]) == int(row["scenario_id"][1:]) for row in assumptions), "scenario/horizon")
    check("assumption_axes", len({row["axis"] for row in assumptions}) == 8 and all(row["classification"] == "SCENARIO ASSUMPTION" for row in assumptions), sorted({row["axis"] for row in assumptions}))
    check("assumption_status", all(row["reality_status"] == "scenario" and row["canon_status"] == "scenario" and row["numeric_future_value_adopted"] == "false" for row in assumptions), "scenario status")
    check("assumption_sources", all(row["source_or_basis"] in source_ids for row in assumptions), "source reference")

    family_states = frames[FAMILY_STATE.name]
    scenario_check(family_states, "state_id", 48, assumption_ids, source_ids)
    check("family_state_coverage", {row["technology_family"] for row in family_states} == FAMILIES and all(Counter(row["scenario_id"] for row in family_states if row["technology_family"] == family) == Counter({sid: 1 for sid in SCENARIO_IDS}) for family in FAMILIES), "family/horizon coverage")
    check("family_state_baseline_resolution", all(set(row["baseline_2026_status"].split("; ")) and set(row["baseline_2026_relevance"].split("; ")) for row in family_states), "baseline family references")

    convergence = frames[CONVERGENCES.name]
    scenario_check(convergence, "relationship_id", 60, assumption_ids, source_ids)
    check("convergence_family_resolution", all(row["technology_family_a"] in FAMILIES and row["technology_family_b"] in FAMILIES for row in convergence), "convergence family")
    check("convergence_system_resolution", all(split_ids(row["affected_system_ids"]) <= system_ids and split_ids(row["affected_system_ids"]) for row in convergence), "convergence systems")
    check("convergence_required_fields", all(row["enabling_conditions"] and row["limiting_conditions"] and row["governance_implications"] and row["second_order_effects"] for row in convergence), "relationship fields")

    system_states = frames[SYSTEM_STATES.name]
    scenario_check(system_states, "state_id", 78, assumption_ids, source_ids)
    check("all_13_systems_covered", {row["system_id"] for row in system_states} == system_ids and all(Counter(row["scenario_id"] for row in system_states if row["system_id"] == system_id) == Counter({sid: 1 for sid in SCENARIO_IDS}) for system_id in system_ids), "system coverage")
    check("system_family_resolution", all(split_ids(row["technology_family"]) <= FAMILIES and split_ids(row["technology_family"]) for row in system_states), "system family")
    allowed_directions = {"strengthened", "weakened", "redistributed", "more adaptive", "more dependent", "more observable", "more automated", "more contested", "more fragmented", "unchanged / indeterminate"}
    check("qualitative_system_directions", {row["state_direction"] for row in system_states} <= allowed_directions, sorted({row["state_direction"] for row in system_states} - allowed_directions))

    dependency = frames[DEPENDENCIES.name]
    scenario_check(dependency, "dependency_state_id", 72, assumption_ids, source_ids)
    check("dependency_system_resolution", all(row["system_a"] in system_ids and row["system_b"] in system_ids for row in dependency), "dependency systems")
    check("dependency_family_resolution", all(row["technology_family"] in FAMILIES for row in dependency), "dependency family")
    check("dependency_change_types", {row["dependency_change_type"] for row in dependency} <= {"intensified_existing_dependency", "substituted_some_dependency", "redistributed_across_nodes", "intensified_and_brittle_dependency"}, sorted({row["dependency_change_type"] for row in dependency}))
    check("dependency_boundaries", all("not a risk" in row["notes"].lower() and row["governance_implication"] for row in dependency), "dependency boundary")

    governance = frames[GOVERNANCE.name]
    scenario_check(governance, "governance_state_id", 48, assumption_ids, source_ids)
    check("governance_family_resolution", all(row["technology_family"] in FAMILIES for row in governance), "governance family")
    governance_text = " ".join(" ".join(row.values()) for row in governance).lower()
    check("ai_authority_boundary", "ai recommendation remains advisory" in governance_text and "automation does not remove human" in governance_text, "AI authority boundary")
    check("sensing_authority_boundary", "measurement and observability do not create enforcement" in governance_text, "sensing/enforcement boundary")

    uncertainty = frames[UNCERTAINTIES.name]
    scenario_check(uncertainty, "uncertainty_state_id", 60, assumption_ids, source_ids)
    check("uncertainty_domains", len({row["uncertainty_domain"] for row in uncertainty}) == 10, sorted({row["uncertainty_domain"] for row in uncertainty}))
    check("uncertainty_explicit", all(row["uncertainty"] and row["what_is_not_inferred"] and "unknown" in row["notes"].lower() for row in uncertainty), "uncertainty language")

    comparison = frames[COMPARISON.name]
    check("comparison_count_and_ids", len(comparison) == 6 and {row["scenario_id"] for row in comparison} == SCENARIO_IDS, len(comparison))
    check("comparison_no_score", not any("score" in field.lower() or "probability" in field.lower() for field in comparison[0]), "comparison fields")
    check("comparison_boundaries", all("no winner" in row["boundary_statement"].lower() or "no winner" in row["notes"].lower() or "winner" in row["boundary_statement"].lower() for row in comparison), "comparison ranking boundary")

    all_model_text = " ".join(" ".join(str(value) for value in row.values()) for frame in frames.values() for row in frame).lower()
    check("scenario_status_not_fact", all(row.get("reality_status") == "scenario" for frame in frames.values() if frame and "reality_status" in frame[0] for row in frame), "scenario status")
    check("no_exact_percentages", not re.search(r"\b\d+(?:\.\d+)?\s*%", all_model_text), "unsupported percentage")
    check("no_exact_health_outcomes", not re.search(r"\b(?:cases?|incidence|deaths?|hospitalizations?|illness)\s*[:=]\s*\d", all_model_text), "unsupported health outcome")
    forbidden_fields = {"risk_score", "resilience_score", "readiness_score", "vulnerability_score", "connectivity_score", "performance_score", "deployment_percentage", "adoption_percentage", "future_capacity_mw", "incidence_rate", "outbreak_probability"}
    check("no_composite_score_fields", not forbidden_fields.intersection(set().union(*(set(frame[0]) for frame in frames.values()))), sorted(forbidden_fields.intersection(set().union(*(set(frame[0]) for frame in frames.values())))))
    check("scenario_not_forecast", all(term in all_model_text for term in ("scenario", "not a forecast", "not a score", "not a basin deployment")), "scenario boundary language")
    cyber_positive_text = " ".join(
        " ".join(row[field] for field in ("capability_state", "governance_state", "cybersecurity_state"))
        for row in family_states if row["technology_family"] == "CYBERSECURITY / DIGITAL RESILIENCE"
    ).lower()
    check("cyber_defensive", "defensive" in cyber_positive_text and not re.search(r"\b(?:exploit|malware|payload|attack procedure|offensive technique)\b", cyber_positive_text), "cyber scope")
    check("biosecurity_safe", all(term in all_model_text for term in ("diagnostic", "attribution", "public communication", "no pathogen design")) and not any("wet-lab procedure" in " ".join(row.values()).lower() and "no " not in " ".join(row.values()).lower() for row in uncertainty), "biosecurity scope")
    quantum = [row for row in family_states if row["technology_family"] == "QUANTUM TECHNOLOGIES"]
    check("quantum_bounded", all("research-stage" in row["baseline_2026_status"] and "deployment" in row["notes"].lower() for row in quantum), "quantum boundary")
    advanced_energy = [row for row in family_states if row["technology_family"] == "ADVANCED ENERGY"]
    check("advanced_energy_bounded", all("deployment" in row["notes"].lower() for row in advanced_energy), "advanced energy boundary")

    for name, required in {
        "technology_convergence_futures.svg": ("Technology Convergence Futures", "2050", "2075", "No score"),
        "technology_cross_system_effects.svg": ("Cross-System Technology Effects", "observability", "human authority", "coupling"),
    }.items():
        path = FIGURES / name
        try:
            ET.parse(path)
            figure_text = path.read_text(encoding="utf-8").lower()
            check(f"figure_svg_{name}", all(term.lower() in figure_text for term in required), {"bytes": path.stat().st_size, "required": required})
        except Exception as exc:
            check(f"figure_svg_{name}", False, str(exc))
    for name in ("technology_convergence_futures.png", "technology_cross_system_effects.png"):
        path = FIGURES / name
        try:
            with Image.open(path) as image:
                image.verify()
                dimensions = (image.width, image.height)
            check(f"figure_png_{name}", dimensions[0] >= 1200 and dimensions[1] >= 600 and path.stat().st_size > 10000, {"bytes": path.stat().st_size, "dimensions": dimensions})
        except Exception as exc:
            check(f"figure_png_{name}", False, str(exc))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("working_manifest_identity", manifest.get("phase") == "15B" and manifest.get("status") == "implemented_validated_pending_sol_acceptance" and manifest.get("source_commit") == BASE_SHA, {key: manifest.get(key) for key in ("phase", "status", "source_commit")})
    manifest_errors = []
    for relative, metadata in entries(manifest).items():
        path = ROOT / relative
        expected = metadata if isinstance(metadata, str) else str(metadata.get("sha256", ""))
        if not path.is_file() or not expected or not hash_matches(path, expected):
            manifest_errors.append(relative)
    check("working_manifest_artifacts", not manifest_errors, manifest_errors[:10])
    status_text = "\n".join((ROOT / relative).read_text(encoding="utf-8") for relative in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"))
    check("status_surfaces", all(term in status_text for term in ("Phase 15B", "ACCEPTED / FROZEN", "C — HOLD / noncanonical", "UNRESOLVED", "Phase 16")), "status/canon/handoff")

    if REVIEW.exists():
        review_text = REVIEW.read_text(encoding="utf-8").lower()
        review_ok = all(term in review_text for term in ('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"scenario_boundary_errors": []', '"technology_maturity_errors": []', '"regional_relevance_errors": []', '"governance_boundary_errors": []', '"biosecurity_boundary_errors": []', '"system_integration_errors": []', '"canon_boundary_errors": []'))
        check("independent_review_passed", review_ok, "review record")
    else:
        check("independent_review_passed", not require_review, "review record absent")

    result = {
        "phase": "15B",
        "passed": not errors,
        "checks": checks,
        "counts": {
            "assumptions": len(assumptions), "technology_family_states": len(family_states), "convergence_relationships": len(convergence), "system_states": len(system_states),
            "dependency_states": len(dependency), "governance_states": len(governance), "uncertainty_states": len(uncertainty), "comparison_rows": len(comparison),
            "technology_families": len(FAMILIES), "phase14_systems": len(system_ids), "phase15a_protected_artifacts": len(phase15a_paths), "phase14a_protected_artifacts": len(phase14a_paths), "phase14b_protected_artifacts": len(phase14b_paths), "prior_freeze_entries": prior_total, "prior_freeze_unique_paths": len(prior_paths),
        },
        "errors": errors,
    }
    CHECK.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "15B", "passed": result["passed"], "counts": result["counts"], "errors": errors}, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
