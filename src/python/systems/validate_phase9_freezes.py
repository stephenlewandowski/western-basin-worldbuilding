"""Independently validate the accepted Phase 9 freeze manifests and protected bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image
from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
EXPECTED_SOURCE_COMMIT = "b5680aa9de0e17544c92cdfabe7b2d9e039f7f07"
MANIFEST_SPECS = {
    "9A": {
        "path": ROOT / "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
        "baseline": "Climate & Natural Hazards Baseline, 2026",
        "counts": {"nodes": 28, "edges": 29, "observations": 28, "sources": 21},
        "artifacts": [
            "data/processed/networks/climate_hazard_nodes.csv",
            "data/processed/networks/climate_hazard_edges.csv",
            "data/processed/analysis/climate_hazard_observations.csv",
            "data/processed/analysis/climate_hazard_sources.csv",
            "reports/phase9a_acquisition_summary.json",
            "outputs/maps/systems/29_climate_natural_hazards_2026.png",
            "outputs/maps/systems/29_climate_natural_hazards_2026.svg",
            "reports/climate_hazard_sources.md",
            "reports/climate_hazard_assumptions.md",
            "reports/climate_hazard_findings.md",
            "reports/climate_hazard_qa.md",
            "reports/phase9a_artifact_check.json",
            "reports/phase9a_correction_qa.md",
        ],
        "maps": ["29_climate_natural_hazards_2026"],
    },
    "9B": {
        "path": ROOT / "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
        "baseline": "Climate/Hazard Dependencies, Compound Events & Resilience, 2026",
        "counts": {"dependency_edges": 24, "dependency_register": 24, "compound_events": 9, "controls": 12, "matrix_rows": 9},
        "artifacts": [
            "data/processed/networks/climate_hazard_dependency_edges.csv",
            "data/processed/analysis/climate_hazard_dependency_register.csv",
            "data/processed/analysis/climate_compound_event_register.csv",
            "data/processed/analysis/climate_resilience_control_register.csv",
            "data/processed/analysis/climate_hazard_dependency_matrix.csv",
            "data/processed/analysis/climate_dependency_sources.csv",
            "outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.png",
            "outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg",
            "reports/climate_dependency_sources.md",
            "reports/climate_dependency_assumptions.md",
            "reports/climate_dependency_findings.md",
            "reports/climate_dependency_qa.md",
            "reports/phase9b_artifact_check.json",
            "reports/phase9_correction_qa.md",
        ],
        "maps": ["30_climate_hazard_dependencies_resilience_2026"],
    },
    "9C": {
        "path": ROOT / "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
        "baseline": "Climate & Hazard Futures, 2050 / 2075",
        "counts": {"projection_records": 12, "assumptions": 36, "hazard_states": 36, "dependency_states": 48, "resilience_states": 48, "compound_event_states": 54, "comparison_rows": 6},
        "artifacts": [
            "data/processed/analysis/climate_projection_evidence.csv",
            "data/processed/scenarios/climate_scenario_assumptions.csv",
            "data/processed/scenarios/climate_scenario_hazard_states.csv",
            "data/processed/scenarios/climate_scenario_dependency_states.csv",
            "data/processed/scenarios/climate_scenario_resilience_states.csv",
            "data/processed/scenarios/climate_compound_event_scenario_states.csv",
            "outputs/figures/climate_scenario_comparison.csv",
            "data/processed/analysis/climate_scenario_sources.csv",
            "outputs/maps/systems/31_climate_hazard_futures_2050.png",
            "outputs/maps/systems/31_climate_hazard_futures_2050.svg",
            "outputs/maps/systems/31b_climate_hazard_futures_2075.png",
            "outputs/maps/systems/31b_climate_hazard_futures_2075.svg",
            "reports/climate_scenario_sources.md",
            "reports/climate_scenario_assumptions.md",
            "reports/climate_scenario_consistency.md",
            "reports/climate_scenario_findings.md",
            "reports/climate_scenario_worldbuilding.md",
            "reports/climate_scenario_qa.md",
            "reports/climate_scenario_manifest.json",
            "reports/phase9c_artifact_check.json",
            "reports/phase9_independent_review.md",
        ],
        "maps": ["31_climate_hazard_futures_2050", "31b_climate_hazard_futures_2075"],
    },
}
CURRENT_MANIFEST_NAMES = {spec["path"].name for spec in MANIFEST_SPECS.values()}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_maps(bases: list[str]) -> None:
    for base in bases:
        png = ROOT / f"outputs/maps/systems/{base}.png"
        svg = ROOT / f"outputs/maps/systems/{base}.svg"
        with Image.open(png) as image:
            image.verify()
        text = " ".join(ET.parse(svg).getroot().itertext())
        assert len(text) > 100, base


def verify_phase9() -> tuple[int, int]:
    seen: set[str] = set()
    protected = 0
    for phase, spec in MANIFEST_SPECS.items():
        manifest = json.loads(spec["path"].read_text(encoding="utf-8"))
        assert manifest["accepted_phase"] == phase
        assert manifest["baseline"] == spec["baseline"]
        assert manifest["status"] == "ACCEPTED / FROZEN"
        assert manifest["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
        assert manifest["source_commit"] == EXPECTED_SOURCE_COMMIT
        assert manifest["counts"] == spec["counts"]
        artifacts = manifest["artifacts"]
        assert set(artifacts) == set(spec["artifacts"]), phase
        assert not seen.intersection(artifacts), "Phase 9 artifact assigned twice"
        for rel, metadata in artifacts.items():
            path = ROOT / rel
            assert path.exists(), rel
            assert set(metadata) >= {"sha256", "bytes", "role"}, rel
            assert len(metadata["sha256"]) == 64, rel
            assert path.stat().st_size == metadata["bytes"], rel
            assert digest(path) == metadata["sha256"], rel
            seen.add(rel)
            protected += 1
        verify_maps(spec["maps"])
    return protected, len(seen)


def verify_prior_freezes() -> tuple[int, int]:
    prior_paths: set[str] = set()
    total = 0
    newline_only = 0
    for path in sorted((ROOT / "reports").glob("phase*_freeze_manifest.json")):
        if path.name in CURRENT_MANIFEST_NAMES:
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        artifacts = manifest.get("artifacts", manifest.get("files", {}))
        for rel, metadata in artifacts.items():
            artifact = ROOT / rel
            expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
            assert artifact.exists(), rel
            if isinstance(metadata, dict) and "bytes" in metadata:
                assert artifact.stat().st_size == metadata["bytes"], rel
            if digest(artifact) != expected:
                assert manifest_matches(ROOT, rel, expected), rel
                newline_only += 1
            assert rel not in prior_paths, f"prior artifact assigned twice: {rel}"
            assert rel not in {a for spec in MANIFEST_SPECS.values() for a in spec["artifacts"]}, rel
            prior_paths.add(rel)
            total += 1
    assert total == 148, total
    return total, newline_only


def main() -> None:
    protected, unique = verify_phase9()
    prior, newline_only = verify_prior_freezes()
    result = {
        "status": "passed",
        "phase9_freeze_manifests": len(MANIFEST_SPECS),
        "phase9_protected_artifacts": protected,
        "phase9_unique_artifacts": unique,
        "prior_phase1_8_protected_artifacts": prior,
        "prior_newline_only_matches": newline_only,
        "maps_valid": True,
        "manifest_artifact_hashes_valid": True,
        "source_commit": EXPECTED_SOURCE_COMMIT,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
