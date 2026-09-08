"""Validate the final Sol acceptance/freeze boundary for Phase 11A and 11B."""
from __future__ import annotations

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
MAPS = ROOT / "outputs/maps/systems"
SOURCE_COMMIT = "f2abcb45f39f7222b3d1585c3c322937e540bb95"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}
PHASE10_NAMES = {
    "phase10a_governance_jurisdiction_freeze_manifest.json",
    "phase10b_governance_dependencies_coordination_freeze_manifest.json",
    "phase10c_governance_futures_freeze_manifest.json",
}
PHASE11_NAMES = {
    "phase11a_population_settlement_freeze_manifest.json",
    "phase11b_population_mobility_dependencies_freeze_manifest.json",
    "phase11c_population_settlement_futures_freeze_manifest.json",
}
MATRIX_DIMENSIONS = [
    "settlement_concentration",
    "mobility_dependency",
    "employment_access",
    "housing_constraint",
    "water_dependency",
    "wastewater_dependency",
    "energy_dependency",
    "transport_dependency",
    "climate_hazard_interface",
    "environmental_health_interface",
    "governance_dependency",
    "service_access",
    "data_certainty",
]
QUALITATIVE = {"strong", "moderate", "limited", "unknown", "not_applicable"}

PHASE11A = REPORTS / "phase11a_population_settlement_freeze_manifest.json"
PHASE11B = REPORTS / "phase11b_population_mobility_dependencies_freeze_manifest.json"

EXPECTED_A = {
    "data/processed/analysis/population_settlement_nodes.csv",
    "data/processed/analysis/population_settlement_observations.csv",
    "data/processed/networks/population_settlement_relationships.csv",
    "data/processed/analysis/population_settlement_sources.csv",
    "data/processed/analysis/population_settlement_uncertainty.csv",
    "outputs/maps/systems/35_population_settlement_2026.png",
    "outputs/maps/systems/35_population_settlement_2026.svg",
    "reports/population_settlement_sources.md",
    "reports/population_settlement_assumptions.md",
    "reports/population_settlement_findings.md",
    "reports/population_settlement_qa.md",
    "reports/population_settlement_baseline_manifest.json",
    "reports/population_settlement_artifact_check.json",
    "reports/population_settlement_independent_review.md",
}
EXPECTED_B = {
    "data/processed/analysis/population_mobility_observations.csv",
    "data/processed/networks/population_mobility_relationships.csv",
    "data/processed/analysis/population_system_dependency_register.csv",
    "data/processed/analysis/population_system_dependency_matrix.csv",
    "outputs/maps/systems/36_population_mobility_dependencies_2026.png",
    "outputs/maps/systems/36_population_mobility_dependencies_2026.svg",
    "reports/population_mobility_sources.md",
    "reports/population_mobility_assumptions.md",
    "reports/population_mobility_findings.md",
    "reports/population_mobility_qa.md",
    "reports/phase11_working_manifest.json",
    "reports/population_mobility_artifact_check.json",
    "reports/population_settlement_independent_review.md",
}
EXPECTED_C = {
    "data/processed/scenarios/population_settlement_scenario_assumptions.csv",
    "data/processed/scenarios/population_settlement_projection_evidence.csv",
    "data/processed/scenarios/population_settlement_future_states.csv",
    "data/processed/networks/population_settlement_future_relationships.csv",
    "data/processed/scenarios/population_settlement_future_uncertainty.csv",
    "data/processed/analysis/population_settlement_future_sources.csv",
    "outputs/figures/population_settlement_future_comparison.csv",
    "outputs/figures/population_settlement_future_comparison.png",
    "outputs/figures/population_settlement_future_comparison.svg",
    "outputs/maps/systems/37_population_settlement_futures_2050.png",
    "outputs/maps/systems/37_population_settlement_futures_2050.svg",
    "outputs/maps/systems/37b_population_settlement_futures_2075.png",
    "outputs/maps/systems/37b_population_settlement_futures_2075.svg",
    "reports/population_settlement_future_sources.md",
    "reports/population_settlement_future_assumptions.md",
    "reports/population_settlement_future_findings.md",
    "reports/population_settlement_future_qa.md",
    "reports/population_settlement_future_independent_review.md",
    "reports/population_settlement_future_manifest.json",
    "reports/population_settlement_future_artifact_check.json",
    "src/python/systems/validate_phase11_freezes.py",
    "src/R/systems/validate_phase11_freezes.R",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def allowed_sizes(path: Path) -> set[int]:
    raw = path.read_bytes()
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return {len(raw)}
    canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return {len(raw), len(canonical), len(canonical.replace(b"\n", b"\r\n"))}


def verify_artifact(rel: str, metadata: dict[str, object]) -> None:
    path = ROOT / rel
    assert path.exists() and path.stat().st_size > 0, rel
    assert set(metadata) == {"sha256", "bytes", "role"}, rel
    assert manifest_matches(ROOT, rel, str(metadata["sha256"])), rel
    assert int(metadata["bytes"]) in allowed_sizes(path), rel
    assert str(metadata["role"]), rel


def verify_final_manifest(path: Path, phase: str, baseline: str, counts: dict[str, int], expected: set[str]) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["accepted_phase"] == phase
    assert payload["baseline"] == baseline
    assert payload["status"] == "ACCEPTED / FROZEN"
    assert payload["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert payload["accepted_date"] == "2026-09-08"
    assert payload["source_commit"] == SOURCE_COMMIT
    assert payload["counts"] == counts
    assert payload["phase11c_implemented"] is False
    artifacts = payload["artifacts"]
    assert set(artifacts) == expected
    for rel, metadata in artifacts.items():
        verify_artifact(rel, metadata)
    return payload


def verify_phase11c_final() -> dict[str, object]:
    path = REPORTS / "phase11c_population_settlement_futures_freeze_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["accepted_phase"] == "11C"
    assert payload["baseline"] == "Population & Settlement Futures, 2050 / 2075"
    assert payload["status"] == "ACCEPTED / FROZEN"
    assert payload["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert payload["accepted_date"] == "2026-09-08"
    assert payload["source_commit"] == "00c582c0f6204eb7f7a3952d90c2768a30f4bf68"
    assert payload["counts"] == {
        "scenario_assumptions": 36,
        "projection_evidence": 6,
        "future_states": 108,
        "future_relationships": 108,
        "uncertainty_states": 36,
        "scenario_sources": 11,
        "comparison_rows": 6,
    }
    assert payload["protected_inputs"] == [
        "reports/phase11a_population_settlement_freeze_manifest.json",
        "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
        "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "reports/phase10c_governance_futures_freeze_manifest.json",
    ]
    assert payload["phase11a_11b_immutable"] is True
    assert payload["phase1_10_immutable"] is True
    assert payload["numeric_future_values_adopted"] is False
    assert payload["climate_migration_as_growth_assumption"] is False
    assert payload["phase12_implemented"] is False
    assert payload["active_holds_preserved"] == {
        "great_black_swamp": "C — HOLD / noncanonical",
        "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
    }
    artifacts = payload["artifacts"]
    assert set(artifacts) == EXPECTED_C
    for rel, metadata in artifacts.items():
        verify_artifact(rel, metadata)
    review = (REPORTS / "population_settlement_future_independent_review.md").read_text(encoding="utf-8").lower()
    for term in (
        '"passed": true',
        '"security_concerns": []',
        '"logic_errors": []',
        '"provenance_errors": []',
        '"statistical_errors": []',
        '"scenario_boundary_errors": []',
        '"spatial_scale_errors": []',
        '"demographic_boundary_errors": []',
    ):
        assert term in review, term
    working = json.loads((REPORTS / "population_settlement_future_manifest.json").read_text(encoding="utf-8"))
    assert working["phase"] == "11C"
    assert working["status"] == "implemented_validated_pending_sol_acceptance"
    assert working["numeric_future_values_adopted"] is False
    assert working["phase12_implemented"] is False
    return payload


def verify_phase10_freeze_integrity() -> tuple[int, int, set[str]]:
    expected_counts = {
        "phase10a_governance_jurisdiction_freeze_manifest.json": {"actors": 40, "authorities": 100, "relationships": 100, "sources": 48, "uncertainties": 16},
        "phase10b_governance_dependencies_coordination_freeze_manifest.json": {"dependency_register": 25, "dependency_edges": 25, "coordination_mechanisms": 14, "matrix_rows": 10, "sources_reused": 48},
        "phase10c_governance_futures_freeze_manifest.json": {"scenario_assumptions": 48, "actor_states": 120, "authority_states": 90, "dependency_states": 150, "coordination_states": 84, "uncertainty_states": 96, "scenario_sources": 19, "comparison_rows": 6},
    }
    seen: set[str] = set()
    entries = 0
    for name in sorted(PHASE10_NAMES):
        payload = json.loads((REPORTS / name).read_text(encoding="utf-8"))
        assert payload["status"] == "ACCEPTED / FROZEN"
        assert payload["counts"] == expected_counts[name]
        for rel, metadata in payload["artifacts"].items():
            verify_artifact(rel, metadata)
            seen.add(rel)
            entries += 1
    assert entries == 53
    assert len(seen) == 49
    b = json.loads((REPORTS / "phase10b_governance_dependencies_coordination_freeze_manifest.json").read_text(encoding="utf-8"))
    a_path = ROOT / b["phase10a_freeze_manifest"]["path"]
    assert b["phase10a_freeze_manifest"]["sha256"] == digest(a_path)
    assert b["phase10a_freeze_manifest"]["bytes"] == a_path.stat().st_size
    return entries, len(seen), seen


def verify_phase1_9_immutability(excluded: set[str]) -> tuple[int, int]:
    protected: set[str] = set()
    total = 0
    newline_only = 0
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if path.name in PHASE10_NAMES or path.name in PHASE11_NAMES:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifacts = payload.get("artifacts", payload.get("files", {}))
        assert artifacts
        for rel, metadata in artifacts.items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            verify_artifact(rel, {"sha256": expected, "bytes": (metadata.get("bytes", 0) if isinstance(metadata, dict) else 0), "role": "prior protected artifact"}) if isinstance(metadata, dict) and "bytes" in metadata else assert_manifest_match(rel, expected)
            if isinstance(metadata, dict) and "bytes" in metadata:
                pass
            if digest(ROOT / rel) != expected:
                newline_only += 1
            assert rel not in protected, f"prior artifact assigned twice: {rel}"
            assert rel not in excluded, f"prior artifact overlaps current protected scope: {rel}"
            protected.add(rel)
            total += 1
    assert total == 196
    changed = set(subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines())
    assert not changed.intersection(protected)
    return total, newline_only


def assert_manifest_match(rel: str, expected: str) -> None:
    path = ROOT / rel
    assert path.exists() and manifest_matches(ROOT, rel, expected), rel


def verify_package() -> dict[str, int]:
    nodes = read(ANALYSIS / "population_settlement_nodes.csv")
    observations = read(ANALYSIS / "population_settlement_observations.csv")
    settlement_rel = read(NETWORKS / "population_settlement_relationships.csv")
    sources = read(ANALYSIS / "population_settlement_sources.csv")
    uncertainty = read(ANALYSIS / "population_settlement_uncertainty.csv")
    mobility = read(ANALYSIS / "population_mobility_observations.csv")
    mobility_rel = read(NETWORKS / "population_mobility_relationships.csv")
    dependencies = read(ANALYSIS / "population_system_dependency_register.csv")
    matrix = read(ANALYSIS / "population_system_dependency_matrix.csv")

    assert len(nodes) == 62 and nodes.node_id.is_unique
    assert len(observations) == 918 and observations.record_id.is_unique
    assert len(settlement_rel) == 44 and settlement_rel.relationship_id.is_unique
    assert len(sources) == 34 and sources.source_id.is_unique
    assert len(uncertainty) == 9 and uncertainty.uncertainty_id.is_unique
    assert len(mobility) == 302 and mobility.record_id.is_unique
    assert len(mobility_rel) == 142 and mobility_rel.relationship_id.is_unique
    assert len(dependencies) == 520 and dependencies.dependency_id.is_unique
    assert len(matrix) == 52 and matrix.object_id.is_unique

    source_meta = sources.set_index("source_id").to_dict("index")
    expected_vintages = {
        "s11b_lodes_oh_wac": ("LODES 8.4 WAC 2023", "2023", "2023"),
        "s11b_lodes_oh_rac": ("LODES 8.4 RAC 2023", "2023", "2023"),
        "s11b_lodes_oh_od": ("LODES 8.4 OD 2023", "2023", "2023"),
        "s11b_lodes_in_wac": ("LODES 8.4 WAC 2023", "2023", "2023"),
        "s11b_lodes_in_rac": ("LODES 8.4 RAC 2023", "2023", "2023"),
        "s11b_lodes_in_od": ("LODES 8.4 OD 2023", "2023", "2023"),
        "s11b_lodes_mi_wac": ("LODES 8.4 WAC 2021", "2021", "2021"),
        "s11b_lodes_mi_rac": ("LODES 8.4 RAC 2023", "2023", "2023"),
        "s11b_lodes_mi_od": ("LODES 8.4 OD 2021", "2021", "2021"),
    }
    for source_id, (product, reference, estimate) in expected_vintages.items():
        assert source_id in source_meta
        meta = source_meta[source_id]
        assert (meta["source_product"], str(meta["reference_year"]), str(meta["estimate_period"])) == (product, reference, estimate)

    differences = mobility[mobility.metric == "workplace_residence_difference"]
    assert len(differences) == 16
    assert not differences.source_id.str.contains("mi_wac_rac", regex=False).any()
    for row in differences.itertuples():
        meta = source_meta[row.source_id]
        assert row.source_product == meta["source_product"]
        assert str(row.reference_year) == str(meta["reference_year"])
        assert str(row.estimate_period) == str(meta["estimate_period"])

    node_state = nodes.set_index("node_id")["state"].to_dict()
    for row in dependencies.itertuples():
        state = str(node_state[row.population_or_settlement_object])
        if row.system == "transport":
            assert row.source_id == f"s11b_lodes_{state.lower()}_od"
            assert row.documented_or_inferred == "inferred"
        if row.system == "water":
            expected = "phase10_s03_toledo_treatment" if row.population_or_settlement_object in {"POP-ZONE-39095", "MUNI-3977000"} else "phase10_governance_context"
            assert row.source_id == expected
        if row.system == "wastewater":
            expected = "phase10_s05_ohio_npdes" if state == "OH" else "phase10_governance_context"
            assert row.source_id == expected
    assert set(matrix.columns) == {"object_id", "object_type", "object_name", *MATRIX_DIMENSIONS, "notes"}
    assert matrix[MATRIX_DIMENSIONS].apply(lambda col: col.isin(QUALITATIVE)).all().all()
    assert matrix.notes.str.contains("derived from the dependency register", case=False).all()

    for frame in [nodes, observations, settlement_rel, mobility, mobility_rel, dependencies, matrix]:
        columns = set(frame.columns)
        assert not columns.intersection({"risk_score", "vulnerability_score", "ej_score", "protected_class_rank", "dose", "illness", "mortality"})
        text = " ".join(" ".join(map(str, row)) for row in frame.to_numpy()).lower()
        assert not any(token in text for token in ("individual profile", "individual movement inference", "unsupported demographic forecast"))
        assert not any(value in text.split() for value in ("2050", "2075"))

    return {
        "nodes": len(nodes),
        "population_observations": len(observations),
        "settlement_relationships": len(settlement_rel),
        "sources": len(sources),
        "uncertainties": len(uncertainty),
        "mobility_observations": len(mobility),
        "mobility_relationships": len(mobility_rel),
        "dependencies": len(dependencies),
        "matrix_rows": len(matrix),
    }


def verify_maps_and_review() -> None:
    for base in ("35_population_settlement_2026", "36_population_mobility_dependencies_2026"):
        png = MAPS / f"{base}.png"
        svg = MAPS / f"{base}.svg"
        with Image.open(png) as image:
            image.verify()
        text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        required = ("map 35", "population", "settlement") if base.startswith("35") else ("map 36", "mobility", "commuting", "employment", "migration", "vulnerability")
        for term in required:
            assert term in text, (base, term)

    review = (REPORTS / "population_settlement_independent_review.md").read_text(encoding="utf-8").lower()
    for term in ("passed: true", "security_concerns: []", "logic_errors: []", "provenance_errors: []", "statistical_errors: []", "spatial_scale_errors: []", "demographic_boundary_errors: []"):
        assert term in review, term
    assert "non-blocking suggestions" in review


def verify_status_records() -> None:
    required = (
        "PROJECT_STATUS.md",
        "docs/canon_status.md",
        "docs/phase_briefs/phase11a_population_settlement_baseline.md",
        "docs/phase_briefs/phase11b_population_mobility_dependencies.md",
        "docs/phase_briefs/phase11c_population_settlement_futures.md",
        "reports/current_phase_handoff.md",
        "README.md",
        "CHANGELOG.md",
        "reports/README.md",
    )
    for rel in required:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "phase 11a" in text and "phase 11b" in text and "accepted / frozen" in text, rel
        assert "phase 11c" in text, rel
    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "active phase" in text and "none" in text, rel
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, rel
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, rel
    assert "phase 12" in (REPORTS / "current_phase_handoff.md").read_text(encoding="utf-8").lower()


def main() -> None:
    a = verify_final_manifest(PHASE11A, "11A", "Population & Settlement Baseline, 2026", {"nodes": 62, "population_observations": 918, "relationships": 44, "sources": 34, "uncertainties": 9}, EXPECTED_A)
    b = verify_final_manifest(PHASE11B, "11B", "Population, Mobility & System Dependencies, 2026", {"mobility_observations": 302, "mobility_relationships": 142, "dependency_register": 520, "matrix_rows": 52, "sources_reused": 34}, EXPECTED_B)
    c = verify_phase11c_final()
    assert b["phase11a_freeze_manifest"]["path"] == "reports/phase11a_population_settlement_freeze_manifest.json"
    assert manifest_matches(ROOT, "reports/phase11a_population_settlement_freeze_manifest.json", str(b["phase11a_freeze_manifest"]["sha256"]))
    assert int(b["phase11a_freeze_manifest"]["bytes"]) in allowed_sizes(PHASE11A)
    phase10_entries, phase10_unique, phase10_paths = verify_phase10_freeze_integrity()
    prior, newline_only = verify_phase1_9_immutability(set(a["artifacts"]) | set(b["artifacts"]) | set(c["artifacts"]) | phase10_paths)
    package_counts = verify_package()
    verify_maps_and_review()
    verify_status_records()
    result = {
        "status": "passed",
        "phase11a_freeze_manifest": "reports/phase11a_population_settlement_freeze_manifest.json",
        "phase11b_freeze_manifest": "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "phase11a_protected_artifacts": len(a["artifacts"]),
        "phase11b_protected_artifacts": len(b["artifacts"]),
        "phase11c_freeze_manifest": "reports/phase11c_population_settlement_futures_freeze_manifest.json",
        "phase11c_protected_artifacts": len(c["artifacts"]),
        "unique_phase11_protected_artifacts": len(set(a["artifacts"]) | set(b["artifacts"]) | set(c["artifacts"])),
        "phase10_manifest_entries": phase10_entries,
        "phase10_unique_artifacts": phase10_unique,
        "prior_phase1_9_protected_artifacts": prior,
        "prior_newline_only_matches": newline_only,
        "package_counts": package_counts,
        "independent_review_passed_and_preserved": True,
        "maps_35_36_valid": True,
        "status_manifest_consistency_valid": True,
        "active_holds_preserved": True,
        "phase11c_implemented": True,
        "phase12_implemented": False,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
