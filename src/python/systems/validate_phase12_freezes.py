"""Validate the final Sol acceptance/freeze boundary for Phase 12A and 12B."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd
from PIL import Image

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
MAPS = ROOT / "outputs/maps/systems"
SOURCE_COMMIT = "e158740aa35f31d2155a9906a3bc2c5529fb5147"
FINAL_A = REPORTS / "phase12a_vector_ecology_freeze_manifest.json"
FINAL_B = REPORTS / "phase12b_vector_environment_human_dependencies_freeze_manifest.json"
FINAL_NAMES = {FINAL_A.name, FINAL_B.name}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}

EXPECTED_A = {
    "data/processed/networks/vector_ecology_nodes.csv",
    "data/processed/networks/vector_ecology_edges.csv",
    "data/processed/analysis/vector_surveillance_records.csv",
    "data/processed/analysis/vector_habitat_associations.csv",
    "data/processed/analysis/vector_ecology_sources.csv",
    "data/processed/analysis/vector_ecology_uncertainty.csv",
    "outputs/maps/systems/38_vector_ecology_baseline_2026.png",
    "outputs/maps/systems/38_vector_ecology_baseline_2026.svg",
    "reports/vector_ecology_sources.md",
    "reports/vector_ecology_assumptions.md",
    "reports/vector_ecology_findings.md",
    "reports/vector_ecology_qa.md",
    "data/raw/vector_ecology/Public_Use_Ixodes_County_Table_2024_summary.xlsx",
    "reports/phase12_citation_ledger.json",
    "reports/phase12_working_manifest.json",
    "reports/vector_ecology_artifact_check.json",
    "reports/phase12_independent_review.md",
}
EXPECTED_B = {
    "data/processed/analysis/vector_system_dependency_register.csv",
    "data/processed/networks/vector_system_dependency_edges.csv",
    "data/processed/analysis/vector_system_dependency_matrix.csv",
    "data/processed/analysis/vector_dependency_evidence.csv",
    "outputs/maps/systems/39_vector_environment_human_dependencies_2026.png",
    "outputs/maps/systems/39_vector_environment_human_dependencies_2026.svg",
    "reports/vector_dependency_sources.md",
    "reports/vector_dependency_assumptions.md",
    "reports/vector_dependency_findings.md",
    "reports/vector_dependency_qa.md",
    "reports/vector_dependency_artifact_check.json",
    "reports/phase12_working_manifest.json",
    "reports/phase12_independent_review.md",
    "src/python/systems/validate_phase12_freezes.py",
    "src/R/systems/validate_phase12_freezes.R",
}


def canonical_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(path: Path, canonical: bool = False) -> str:
    data = path.read_bytes()
    return hashlib.sha256(canonical_text(data) if canonical else data).hexdigest()


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def artifact_entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def final_artifact_match(relative: str, metadata: dict[str, object]) -> None:
    path = ROOT / relative
    assert path.exists() and path.stat().st_size > 0, relative
    expected = str(metadata["sha256"])
    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = canonical_text(raw)
        assert digest(path, canonical=True) == expected, relative
        assert int(metadata["bytes"]) == len(data), relative
    else:
        assert digest(path) == expected and int(metadata["bytes"]) == len(raw), relative
    assert str(metadata["role"]), relative


def verify_final_manifest(path: Path, phase: str, baseline: str, counts: dict[str, int], expected: set[str]) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["accepted_phase"] == phase
    assert payload["baseline"] == baseline
    assert payload["status"] == "ACCEPTED / FROZEN"
    assert payload["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
    assert payload["accepted_date"] == "2026-09-08"
    assert payload["source_commit"] == SOURCE_COMMIT
    assert payload["counts"] == counts
    artifacts = payload["artifacts"]
    assert set(artifacts) == expected
    for relative, metadata in artifacts.items():
        final_artifact_match(relative, metadata)
    return payload


def verify_working_manifest(relative: str, phase: str, count: int) -> int:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert payload["phase"] == phase
    assert payload["status"] == "implemented_validated_pending_sol_acceptance"
    assert payload["phase12c_implemented"] is False
    assert payload["phase13_implemented"] is False
    artifacts = artifact_entries(payload)
    assert len(artifacts) == count
    for rel, metadata in artifacts.items():
        expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
        assert manifest_matches(ROOT, rel, expected), rel
    return len(artifacts)


def verify_prior_immutability(excluded: set[str]) -> tuple[int, int]:
    expected_hashes: dict[str, str] = {}
    protected: set[str] = set()
    entries = 0
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if path.name in FINAL_NAMES:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for relative, metadata in artifact_entries(payload).items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if relative in expected_hashes:
                assert expected_hashes[relative] == expected, relative
            expected_hashes[relative] = expected
            assert manifest_matches(ROOT, relative, expected), relative
            protected.add(relative)
            entries += 1
    assert entries == 298 and len(protected) == 293
    assert not protected.intersection(excluded)
    changed = set(
        subprocess.check_output(
            ["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True
        ).splitlines()
    )
    assert not changed.intersection(protected)
    return entries, len(protected)


def verify_package() -> dict[str, int]:
    nodes = read(NETWORKS / "vector_ecology_nodes.csv")
    edges = read(NETWORKS / "vector_ecology_edges.csv")
    surveillance = read(ANALYSIS / "vector_surveillance_records.csv")
    habitat = read(ANALYSIS / "vector_habitat_associations.csv")
    sources = read(ANALYSIS / "vector_ecology_sources.csv")
    uncertainty = read(ANALYSIS / "vector_ecology_uncertainty.csv")
    dependency = read(ANALYSIS / "vector_system_dependency_register.csv")
    dependency_edges = read(NETWORKS / "vector_system_dependency_edges.csv")
    matrix = read(ANALYSIS / "vector_system_dependency_matrix.csv")
    evidence = read(ANALYSIS / "vector_dependency_evidence.csv")

    assert len(nodes) == 20 and nodes.node_id.is_unique
    assert len(edges) == 26 and edges.edge_id.is_unique
    assert len(surveillance) == 36 and surveillance.record_id.is_unique
    assert len(habitat) == 15 and habitat.association_id.is_unique
    assert len(sources) == 27 and sources.source_id.is_unique
    assert len(uncertainty) == 10 and uncertainty.uncertainty_id.is_unique
    assert len(dependency) == 28 and dependency.dependency_id.is_unique
    assert len(dependency_edges) == 28 and dependency_edges.dependency_id.is_unique
    assert len(matrix) == 8 and matrix.object_id.is_unique
    assert len(evidence) == 8 and evidence.evidence_id.is_unique
    assert dependency_edges.equals(dependency)

    source_ids = set(sources.source_id)
    assert nodes.source_id.isin(source_ids).all()
    assert edges.source_id.isin(source_ids).all()
    assert surveillance.source_id.isin(source_ids).all()
    assert habitat.source_id.isin(source_ids).all()
    assert uncertainty.source_id.isin(source_ids).all()
    assert dependency.source_id.isin(source_ids).all()
    assert evidence.source_id.isin(source_ids).all()

    ixodes = sources.loc[sources.source_id == "v12_cdc_ixodes"].iloc[0]
    assert ixodes.url == "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html"
    assert ixodes.retrieval_url == "https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx"
    assert "not CDC-hosted" in ixodes.retrieval_provenance and "HTTP 403" in ixodes.retrieval_provenance

    fields = set().union(*(set(frame.columns) for frame in (nodes, edges, surveillance, habitat, uncertainty, dependency, matrix, evidence)))
    forbidden = {"infection_probability", "disease_risk_score", "risk_score", "vulnerability_score", "ej_score", "dose", "contact_probability", "abundance_surface"}
    assert not fields.intersection(forbidden)
    text = " ".join(" ".join(map(str, row)) for frame in (nodes, edges, surveillance, habitat, uncertainty, dependency, matrix, evidence) for row in frame.to_numpy()).lower()
    for phrase in ("presence != abundance", "sampling effort", "not abundance", "detection", "establishment", "not absence", "positive vector pool", "human case", "local transmission", "not exposure"):
        assert phrase in text, phrase
    assert not any(token in text for token in ("infection probability: 0", "disease risk score: 0", "vulnerability/ej score: 0"))
    assert "vde-003" in text and "canon_status" in " ".join(dependency.columns)
    assert not any(term in text for term in ("2050", "2075"))

    for base, terms in (
        ("38_vector_ecology_baseline_2026", ("map 38", "vector ecology", "surveillance boundary", "presence", "abundance", "positive vector pool")),
        ("39_vector_environment_human_dependencies_2026", ("map 39", "vector", "environment", "human-system", "surveillance", "not continuous", "not exposure")),
    ):
        with Image.open(MAPS / f"{base}.png") as image:
            image.verify()
        svg_text = " ".join(__import__("xml.etree.ElementTree", fromlist=["ElementTree"]).parse(MAPS / f"{base}.svg").getroot().itertext()).lower()
        for term in terms:
            assert term in svg_text, (base, term)

    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "phase 12a" in text and "accepted / frozen" in text, rel
        assert "phase 12b" in text and "accepted / frozen" in text, rel
        assert "phase 12c" in text and "approved scope" in text and "not implemented" in text, rel
        assert "active phase" in text and "none" in text, rel
        assert "great black swamp" in text and "hold" in text and "noncanonical" in text, rel
        assert "intake-coordinate discrepancy" in text and "unresolved" in text, rel

    review = (REPORTS / "phase12_independent_review.md").read_text(encoding="utf-8").lower()
    for term in (
        '"passed": true',
        '"security_concerns": []',
        '"logic_errors": []',
        '"provenance_errors": []',
        '"ecological_errors": []',
        '"surveillance_errors": []',
        '"spatial_scale_errors": []',
        '"health_boundary_errors": []',
    ):
        assert term in review, term

    bad = []
    for root in (ROOT / "data/processed", ROOT / "outputs/maps/systems"):
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            lower = str(path.relative_to(ROOT)).replace("\\", "/").lower()
            if "phase13" in lower or ("vector" in path.name.lower() and "future" in path.name.lower()) or path.name.lower().startswith(("40_", "40b_")):
                bad.append(lower)
    assert not bad, bad

    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "surveillance_records": len(surveillance),
        "habitat_associations": len(habitat),
        "sources": len(sources),
        "uncertainties": len(uncertainty),
        "dependency_register": len(dependency),
        "dependency_edges": len(dependency_edges),
        "matrix_rows": len(matrix),
        "evidence_rows": len(evidence),
    }


def main() -> None:
    a = verify_final_manifest(FINAL_A, "12A", "Vector Ecology Baseline, 2026", {"nodes": 20, "edges": 26, "surveillance_records": 36, "habitat_associations": 15, "sources": 27, "uncertainties": 10}, EXPECTED_A)
    b = verify_final_manifest(FINAL_B, "12B", "Vector / Environment / Human-System Dependencies, 2026", {"dependency_register": 28, "dependency_edges": 28, "matrix_rows": 8, "evidence_rows": 8, "sources_reused": 27}, EXPECTED_B)
    protected_a = digest(FINAL_A, canonical=True)
    a_bytes = len(canonical_text(FINAL_A.read_bytes()))
    assert b["phase12a_freeze_manifest"]["path"] == "reports/phase12a_vector_ecology_freeze_manifest.json"
    assert b["phase12a_freeze_manifest"]["sha256"] == protected_a
    assert int(b["phase12a_freeze_manifest"]["bytes"]) == a_bytes
    working_a = verify_working_manifest("reports/vector_ecology_baseline_manifest.json", "12A", 14)
    working_b = verify_working_manifest("reports/vector_dependency_manifest.json", "12B", 10)
    prior_entries, prior_unique = verify_prior_immutability(set(a["artifacts"]) | set(b["artifacts"]) | {str(FINAL_A.relative_to(ROOT)).replace("\\", "/")})
    package = verify_package()
    result = {
        "status": "passed",
        "phase12a_freeze_manifest": FINAL_A.relative_to(ROOT).as_posix(),
        "phase12b_freeze_manifest": FINAL_B.relative_to(ROOT).as_posix(),
        "phase12a_protected_artifacts": len(a["artifacts"]),
        "phase12b_protected_artifacts": len(b["artifacts"]),
        "phase12a_working_manifest_artifacts": working_a,
        "phase12b_working_manifest_artifacts": working_b,
        "prior_phase1_11_manifest_entries": prior_entries,
        "prior_phase1_11_unique_protected_artifacts": prior_unique,
        "package_counts": package,
        "independent_review_passed_and_preserved": True,
        "phase12a_immutable": True,
        "phase1_11_immutable": True,
        "python_r_freeze_boundary": True,
        "phase12c_implemented": False,
        "phase13_implemented": False,
        "active_holds_preserved": True,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
