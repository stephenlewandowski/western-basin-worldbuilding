"""Independently validate the final Sol-accepted Phase 10 freeze manifests."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from freeze_hash import manifest_matches

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
SOURCE_COMMIT = "e1f233cc89e3694d2f08dfd81fde6f9194f57a65"
FINAL = {
    "10A": {
        "path": REPORTS / "phase10a_governance_jurisdiction_freeze_manifest.json",
        "baseline": "Governance & Jurisdiction Baseline, 2026",
        "counts": {"actors": 40, "authorities": 100, "relationships": 100, "sources": 48, "uncertainties": 16},
        "artifacts": {
            "data/processed/analysis/governance_actors.csv",
            "data/processed/analysis/governance_authorities.csv",
            "data/processed/networks/governance_relationships.csv",
            "data/processed/analysis/governance_sources.csv",
            "data/processed/analysis/governance_uncertainty_register.csv",
            "outputs/maps/systems/32_governance_jurisdiction_2026.png",
            "outputs/maps/systems/32_governance_jurisdiction_2026.svg",
            "reports/governance_baseline_sources.md",
            "reports/governance_baseline_assumptions.md",
            "reports/governance_baseline_findings.md",
            "reports/governance_baseline_qa.md",
            "reports/governance_baseline_artifact_check.json",
            "reports/governance_independent_review.md",
            "reports/governance_post_correction_independent_review.md",
            "reports/governance_additional_post_correction_independent_review.md",
        },
    },
    "10B": {
        "path": REPORTS / "phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "baseline": "Cross-System Authority, Dependencies & Coordination, 2026",
        "counts": {"dependency_register": 25, "dependency_edges": 25, "coordination_mechanisms": 14, "matrix_rows": 10, "sources_reused": 48},
        "artifacts": {
            "data/processed/analysis/governance_dependency_register.csv",
            "data/processed/analysis/governance_coordination_mechanisms.csv",
            "data/processed/analysis/governance_dependency_matrix.csv",
            "data/processed/networks/governance_dependency_edges.csv",
            "data/processed/analysis/governance_sources.csv",
            "outputs/maps/systems/33_cross_system_governance_dependencies_2026.png",
            "outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg",
            "reports/governance_dependency_sources.md",
            "reports/governance_dependency_assumptions.md",
            "reports/governance_dependency_findings.md",
            "reports/governance_dependency_qa.md",
            "reports/governance_dependency_artifact_check.json",
            "reports/governance_independent_review.md",
            "reports/governance_post_correction_independent_review.md",
            "reports/governance_additional_post_correction_independent_review.md",
        },
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_matches(path: Path, metadata: dict[str, object]) -> bool:
    data = path.read_bytes()
    expected = str(metadata["sha256"])
    if path.suffix.lower() not in {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}:
        return len(data) == int(metadata["bytes"]) and hashlib.sha256(data).hexdigest() == expected
    canonical = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = canonical.replace(b"\n", b"\r\n")
    candidates = {hashlib.sha256(data).hexdigest(), hashlib.sha256(canonical).hexdigest(), hashlib.sha256(crlf).hexdigest()}
    return expected in candidates and int(metadata["bytes"]) in {len(data), len(canonical), len(crlf)}


def verify_final_manifests() -> tuple[int, int, set[str]]:
    seen: set[str] = set()
    entries = 0
    for phase, spec in FINAL.items():
        manifest = json.loads(spec["path"].read_text(encoding="utf-8"))
        assert manifest["accepted_phase"] == phase
        assert manifest["baseline"] == spec["baseline"]
        assert manifest["status"] == "ACCEPTED / FROZEN"
        assert manifest["accepted_by"] == "Sol explicit acceptance decision supplied for this run"
        assert manifest["accepted_date"] == "2026-09-04"
        assert manifest["source_commit"] == SOURCE_COMMIT
        assert manifest["counts"] == spec["counts"]
        artifacts = manifest["artifacts"]
        assert set(artifacts) == spec["artifacts"], phase
        for rel, metadata in artifacts.items():
            path = ROOT / rel
            assert path.exists(), rel
            assert set(metadata) == {"sha256", "bytes", "role"}, rel
            assert artifact_matches(path, metadata), rel
            seen.add(rel)
            entries += 1
    b = json.loads(FINAL["10B"]["path"].read_text(encoding="utf-8"))
    a_path = ROOT / b["phase10a_freeze_manifest"]["path"]
    assert b["phase10a_freeze_manifest"]["sha256"] == digest(a_path)
    assert b["phase10a_freeze_manifest"]["bytes"] == a_path.stat().st_size
    return entries, len(seen), seen


def verify_prior_freezes(final_artifacts: set[str]) -> tuple[int, int]:
    prior_paths: set[str] = set()
    total = 0
    newline_only = 0
    final_names = {spec["path"].name for spec in FINAL.values()}
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        if path.name in final_names:
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
            assert rel not in final_artifacts, f"Phase 1-9 artifact overlaps Phase 10: {rel}"
            prior_paths.add(rel)
            total += 1
    assert total == 196, total
    changed = subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines()
    assert not set(changed).intersection(prior_paths)
    return total, newline_only


def verify_records_and_status() -> None:
    post = (REPORTS / "governance_post_correction_independent_review.md").read_text(encoding="utf-8")
    additional = (REPORTS / "governance_additional_post_correction_independent_review.md").read_text(encoding="utf-8")
    assert "deleg_2e8d515e" in post and '"passed": true' in post
    assert "deleg_eedc4116" in additional and '"passed": true' in additional
    for rel in (
        "PROJECT_STATUS.md",
        "docs/canon_status.md",
        "docs/phase_briefs/phase10a_governance_jurisdiction_baseline.md",
        "docs/phase_briefs/phase10b_governance_dependencies_coordination.md",
        "reports/current_phase_handoff.md",
        "README.md",
        "CHANGELOG.md",
        "reports/README.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "accepted / frozen" in text, rel
        assert "phase 10c" in text and "not implemented" in text, rel
    canon = (ROOT / "docs/canon_status.md").read_text(encoding="utf-8")
    handoff = (ROOT / "reports/current_phase_handoff.md").read_text(encoding="utf-8")
    for text in (canon, handoff):
        lower = text.lower()
        assert "great black swamp" in lower and "hold" in lower and "noncanonical" in lower
        assert "intake-coordinate discrepancy" in lower and "unresolved" in lower
    changed = subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", SOURCE_COMMIT], text=True).splitlines()
    assert all("phase10c" not in rel.lower() or rel.lower() == "docs/phase_briefs/phase10c_governance_futures.md" for rel in changed)


def main() -> None:
    entries, unique, final_artifacts = verify_final_manifests()
    prior, newline_only = verify_prior_freezes(final_artifacts)
    verify_records_and_status()
    result = {
        "status": "passed",
        "phase10_manifests": 2,
        "phase10_manifest_entries": entries,
        "phase10_unique_artifacts": unique,
        "prior_phase1_9_protected_artifacts": prior,
        "prior_newline_only_matches": newline_only,
        "manifest_hashes_valid": True,
        "status_consistency_valid": True,
        "review_records_preserved": ["deleg_2e8d515e", "deleg_eedc4116"],
        "phase10c_unimplemented": True,
        "holds_preserved": True,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
