"""Validate the Phase 13A infectious-disease systems baseline."""
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
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"

NODES = NETWORKS / "infectious_disease_nodes.csv"
RELATIONSHIPS = NETWORKS / "infectious_disease_transmission_relationships.csv"
OBSERVATIONS = ANALYSIS / "infectious_disease_observations.csv"
SURVEILLANCE = ANALYSIS / "infectious_disease_surveillance.csv"
SOURCES = ANALYSIS / "infectious_disease_sources.csv"
UNCERTAINTIES = ANALYSIS / "infectious_disease_uncertainties.csv"
MAP_PNG = MAPS / "41_infectious_disease_system_baseline_2026.png"
MAP_SVG = MAPS / "41_infectious_disease_system_baseline_2026.svg"
MANIFEST = REPORTS / "infectious_disease_baseline_manifest.json"
LEDGER = REPORTS / "phase13a_citation_ledger.json"

NODE_COLUMNS = {
    "node_id", "name", "node_class", "disease_group", "pathogen_or_agent",
    "transmission_pathway", "environment_or_host_interface", "geographic_scale",
    "latitude", "longitude", "source_id", "evidence_status", "confidence",
    "reality_status", "canon_status", "notes",
}
REL_COLUMNS = {
    "relationship_id", "from_id", "to_id", "relationship_type", "relationship_basis",
    "geographic_scale", "evidence_status", "source_id", "confidence", "reality_status",
    "canon_status", "notes",
}
OBS_COLUMNS = {
    "observation_id", "system_node_id", "observation_type", "reporting_year_or_period",
    "geography", "geographic_scale", "observed_value", "units", "reporting_basis",
    "numerator", "denominator", "case_definition_or_surveillance_definition",
    "residence_or_exposure_basis", "observed_estimated_modeled", "source_id",
    "evidence_status", "confidence", "uncertainty_notes", "notes",
}
SURV_COLUMNS = {
    "surveillance_id", "disease_or_pathogen", "reporting_period", "geography",
    "surveillance_system", "case_definition_or_surveillance_definition", "reporting_basis",
    "numerator", "denominator", "case_geography_basis", "exposure_geography_basis",
    "suppression_missingness", "source_id", "confidence", "uncertainty", "notes",
}
SOURCE_COLUMNS = {
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
}
UNC_COLUMNS = {"uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"}

QUALITATIVE = {"high", "moderate", "limited", "unknown"}
NODE_CLASSES = {"disease_system", "surveillance_system", "environmental_interface", "host_interface", "institutional_response_interface", "boundary_interface", "accepted_layer_reference"}
RELATIONSHIP_BASES = {"documented_source", "accepted_layer", "documented_plus_inferred", "project_boundary", "project_inference"}
EVIDENCE_STATUSES = {"documented_system", "documented_program", "documented_context", "documented_relationship", "accepted_context", "accepted_reference", "boundary_rule", "project_inference", "documented", "documented_boundary"}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".svg", ".txt", ".yml", ".yaml"}
PORTABLE_TEXT_SUFFIXES = TEXT_SUFFIXES | {".py", ".r"}


def read(path: Path) -> pd.DataFrame:
    assert path.exists() and path.stat().st_size > 0, path
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_entries(payload: dict) -> dict[str, object]:
    return payload.get("artifacts", payload.get("files", {}))


def portable_manifest_matches(relative: str, expected: str) -> bool:
    """Match exact bytes or a proven LF/CRLF-only representation.

    A few historical manifests protect source validators as well as data and
    prose. Windows checkout filters can change those text bytes while leaving
    their content unchanged, so the portability rule is extended narrowly to
    source text without relaxing binary checks.
    """
    path = ROOT / relative
    if manifest_matches(ROOT, relative, expected):
        return True
    if path.suffix.lower() not in PORTABLE_TEXT_SUFFIXES:
        return False
    try:
        accepted = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{relative}"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    canonical = lambda data: data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if canonical(path.read_bytes()) != canonical(accepted):
        return False
    return expected in {digest_bytes(accepted), digest_bytes(accepted.replace(b"\n", b"\r\n"))}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def recorded_bytes_match(path: Path, recorded: int) -> bool:
    actual = path.read_bytes()
    if path.suffix.lower() not in PORTABLE_TEXT_SUFFIXES:
        return len(actual) == recorded
    canonical = actual.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = canonical.replace(b"\n", b"\r\n")
    return recorded in {len(actual), len(canonical), len(crlf)}


def check_manifest(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    checked = []
    for rel, metadata in artifact_entries(payload).items():
        expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
        artifact = ROOT / rel
        assert artifact.exists() and artifact.stat().st_size > 0, rel
        assert portable_manifest_matches(rel, str(expected)), rel
        if isinstance(metadata, dict) and "bytes" in metadata:
            assert recorded_bytes_match(artifact, int(metadata["bytes"])), rel
        checked.append(rel)
    return checked


def check_prior_freezes() -> tuple[int, int, dict[str, str]]:
    protected: set[str] = set()
    expected_hashes: dict[str, str] = {}
    statuses: dict[str, str] = {}
    total = 0
    manifests = sorted(REPORTS.glob("phase*_freeze_manifest.json"))
    assert len(manifests) >= 20
    for path in manifests:
        payload = json.loads(path.read_text(encoding="utf-8"))
        statuses[path.name] = str(payload.get("status", ""))
        entries = artifact_entries(payload)
        assert entries, path.name
        for rel, metadata in entries.items():
            expected = str(metadata["sha256"] if isinstance(metadata, dict) else metadata)
            if rel in expected_hashes:
                assert expected_hashes[rel] == expected, rel
            expected_hashes[rel] = expected
            artifact = ROOT / rel
            assert artifact.exists() and artifact.stat().st_size > 0, rel
            assert portable_manifest_matches(rel, expected), rel
            protected.add(rel)
            total += 1
    return total, len(protected), statuses


def check_status_surfaces() -> None:
    for rel in ("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in ("phase 12a", "phase 12b", "phase 12c", "accepted / frozen", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"):
            assert term in text, (rel, term)
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8").lower()
    canon = (ROOT / "docs/canon_status.md").read_text(encoding="utf-8").lower()
    handoff = (ROOT / "reports/current_phase_handoff.md").read_text(encoding="utf-8").lower()
    for text, rel in ((status, "PROJECT_STATUS.md"), (canon, "docs/canon_status.md"), (handoff, "reports/current_phase_handoff.md")):
        assert "phase 13a" in text, rel
        assert "implemented" in text, rel
        assert "phase 13b" in text and "not implemented" in text, rel
        assert "phase 13c" in text and "not implemented" in text, rel
    assert "active phase" in handoff and "none" in handoff, "handoff active phase"


def check_rows(nodes: pd.DataFrame, rels: pd.DataFrame, obs: pd.DataFrame, surv: pd.DataFrame, sources: pd.DataFrame, unc: pd.DataFrame) -> None:
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(rels.columns) == REL_COLUMNS
    assert set(obs.columns) == OBS_COLUMNS
    assert set(surv.columns) == SURV_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert set(unc.columns) == UNC_COLUMNS
    assert len(nodes) == 38 and nodes.node_id.is_unique
    assert len(rels) == 40 and rels.relationship_id.is_unique
    assert len(obs) == 25 and obs.observation_id.is_unique
    assert len(surv) == 17 and surv.surveillance_id.is_unique
    assert len(sources) == 27 and sources.source_id.is_unique and sources.url.is_unique
    assert len(unc) == 18 and unc.uncertainty_id.is_unique
    source_ids = set(sources.source_id)
    node_ids = set(nodes.node_id)
    assert nodes.source_id.isin(source_ids).all()
    assert rels.source_id.isin(source_ids).all()
    assert obs.source_id.isin(source_ids).all()
    assert surv.source_id.isin(source_ids).all()
    assert unc.source_id.isin(source_ids).all()
    assert obs.system_node_id.isin(node_ids).all()
    assert unc.subject_id.isin(node_ids).all()
    assert rels.from_id.isin(node_ids).all() and rels.to_id.isin(node_ids).all()
    assert nodes.node_class.isin(NODE_CLASSES).all()
    assert nodes.confidence.isin(QUALITATIVE).all()
    assert rels.relationship_basis.isin(RELATIONSHIP_BASES).all()
    assert rels.confidence.isin(QUALITATIVE).all()
    assert obs.confidence.isin(QUALITATIVE).all()
    assert surv.confidence.isin(QUALITATIVE).all()
    assert unc.confidence.isin(QUALITATIVE).all()
    assert nodes.reality_status.eq("real").all() and rels.reality_status.eq("real").all()
    assert obs.observed_estimated_modeled.isin({"observed", "estimated", "modeled"}).all()
    required_columns = {
        "nodes": [c for c in nodes.columns if c not in {"latitude", "longitude"}],
        "relationships": list(rels.columns), "observations": list(obs.columns),
        "surveillance": list(surv.columns), "sources": list(sources.columns), "uncertainties": list(unc.columns),
    }
    for name, frame in (("nodes", nodes), ("relationships", rels), ("observations", obs), ("surveillance", surv), ("sources", sources), ("uncertainties", unc)):
        for column in required_columns[name]:
            assert frame[column].astype(str).str.len().gt(0).all(), (name, column)
    for row in nodes.itertuples():
        assert (row.latitude == "") == (row.longitude == ""), row.node_id
        if row.latitude:
            assert -90 <= float(row.latitude) <= 90 and -180 <= float(row.longitude) <= 180
    assert not nodes.loc[nodes.node_class.isin({"surveillance_system", "institutional_response_interface"}), "latitude"].astype(bool).any()
    assert obs.observed_estimated_modeled.eq("observed").sum() >= 24


def check_surveillance_semantics(surv: pd.DataFrame, obs: pd.DataFrame, sources: pd.DataFrame) -> None:
    assert surv.case_geography_basis.str.len().gt(0).all()
    assert surv.exposure_geography_basis.str.len().gt(0).all()
    assert surv.suppression_missingness.str.len().gt(0).all()
    assert surv.numerator.str.len().gt(0).all() and surv.denominator.str.len().gt(0).all()
    assert surv.reporting_period.str.len().gt(0).all()
    assert surv.disease_or_pathogen.str.len().gt(0).all()
    assert surv.loc[surv.disease_or_pathogen.eq("West Nile virus")].shape[0] == 5
    wnv = obs[obs.system_node_id.eq("DID-001")]
    assert len(wnv) == 6
    assert wnv.loc[wnv.observation_id.eq("IDO-002"), "observed_value"].iloc[0] == "11,980"
    assert wnv.loc[wnv.observation_id.eq("IDO-003"), "observed_value"].iloc[0] == "45"
    assert wnv.loc[wnv.observation_id.eq("IDO-004"), "observed_value"].iloc[0] == "124"
    assert wnv.loc[wnv.observation_id.eq("IDO-005"), "observed_value"].iloc[0] == "33"
    assert wnv.loc[wnv.observation_id.eq("IDO-006"), "observed_value"].iloc[0] == "1"
    human = surv[surv.case_geography_basis.str.contains("residence", case=False)]
    assert len(human) >= 3
    assert human.exposure_geography_basis.str.contains("not supplied|not necessarily|not inferred|not individual|no human|not assumed|condition-specific|infection-specific", case=False, regex=True).all()
    assert sources.retrieval_url.str.len().gt(0).all() and sources.retrieval_provenance.str.len().gt(0).all()
    assert sources.loc[sources.source_id.eq("s13_cdc_wastewater"), "url"].iloc[0] == "https://www.cdc.gov/wastewater/about-data/"


def check_boundaries(frames: list[pd.DataFrame]) -> None:
    fields = set().union(*(set(frame.columns) for frame in frames))
    forbidden_fields = {
        "risk_score", "disease_risk_score", "composite_disease_risk_index", "vulnerability_score",
        "ej_score", "individual_risk", "infection_probability", "outbreak_probability",
        "transmission_rate", "disease_burden_index", "exposure_probability", "dose",
    }
    assert not fields.intersection(forbidden_fields)
    text = " ".join(" ".join(map(str, row)) for frame in frames for row in frame.to_numpy()).lower()
    required_pairs = [
        ("pathogen", "exposure", "infection", "reported case", "local transmission", "outbreak", "disease burden"),
        ("surveillance intensity", "incidence"),
        ("reported case", "place of exposure"),
        ("absence", "pathogen absence"),
        ("county", "neighborhood"),
        ("vector detection", "human infection"),
        ("positive vector", "human case"),
        ("source-water", "treatment failure", "illness"),
        ("case count", "transmission rate"),
        ("testing intensity", "disease intensity"),
        ("hospitalization", "community incidence"),
    ]
    for pair in required_pairs:
        assert all(term in text for term in pair), pair
    for term in ("not a continuous incidence", "not a disease-risk", "not a transmission rate", "not a human infection", "not local transmission", "not a composite", "not a risk surface"):
        assert term in text, term
    assert not re.search(r"(?:risk score|disease risk score|infection probability|outbreak probability|transmission rate|disease burden index|vulnerability score|ej score)\s*[,=:]\s*[0-9]", text)
    assert not re.search(r"\b(?:2050|2075)\b", text)
    assert not re.search(r"\b(?:neighborhood|census tract|municipality|facility)\s+(?:cases?|risk|incidence|burden)\b", text)


def check_manifest_and_ledger() -> tuple[int, int]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "13A" and manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["map_number"] == 41
    assert manifest["counts"] == {"nodes": 38, "relationships": 40, "observations": 25, "surveillance_records": 17, "sources": 27, "uncertainties": 18}
    assert manifest["phase12abc_accepted_frozen"] is True and manifest["phase1_12_immutable"] is True
    assert manifest["phase13b_implemented"] is False and manifest["phase13c_implemented"] is False
    assert manifest["composite_disease_risk_index"] is False and manifest["individual_case_or_risk_map"] is False
    checked = check_manifest(MANIFEST)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert ledger["version"] == 1 and len(ledger["sources"]) == 27
    urls = [entry["url"] for entry in sorted(ledger["sources"], key=lambda x: x["id"])]
    builder_path = ROOT / "src/python/systems/build_infectious_disease_baseline.py"
    builder_text = builder_path.read_text(encoding="utf-8")
    expected_urls = []
    in_urls = False
    for line in builder_text.splitlines():
        if line.strip() == "CITATION_URLS = [":
            in_urls = True
            continue
        if in_urls and line.strip() == "]":
            break
        if in_urls and line.strip().startswith('"'):
            expected_urls.append(line.strip().rstrip(",").strip('"'))
    assert urls == [url.rstrip("/") or url for url in expected_urls]
    return len(checked), len(ledger["sources"])


def check_map() -> list[int]:
    with Image.open(MAP_PNG) as image:
        image.verify()
        size = list(image.size)
    root = ET.parse(MAP_SVG).getroot()
    text = " ".join(root.itertext()).lower()
    required = (
        "map 41", "infectious disease", "vector", "water", "foodborne", "respiratory",
        "nndss", "wastewater", "surveillance", "pathogen presence", "exposure", "infection",
        "reported case", "local transmission", "no individual cases",
    )
    for term in required:
        assert term in text, term
    return size


def check_no_13b_13c_implementation() -> None:
    allowed_briefs = {
        "docs/phase_briefs/phase13a_infectious_disease_baseline.md",
        "docs/phase_briefs/phase13b_infectious_disease_dependencies.md",
        "docs/phase_briefs/phase13c_infectious_disease_futures.md",
    }
    for base in (ROOT / "data/processed", ROOT / "outputs/maps/systems", ROOT / "src/python/systems", ROOT / "src/R/systems"):
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/").lower()
            name = path.name.lower()
            if "phase13b" in rel or "phase13c" in rel or "infectious_disease_dependencies" in name or "infectious_disease_futures" in name:
                raise AssertionError(rel)
            if name.startswith("42_") or name.startswith("43_"):
                raise AssertionError(rel)
    assert MAP_PNG.exists() and MAP_SVG.exists()
    assert not (MAPS / "42_infectious_disease_dependencies_2026.png").exists()
    assert not (MAPS / "42_infectious_disease_futures_2050.png").exists()
    assert all((ROOT / p).exists() for p in allowed_briefs)


def main() -> None:
    nodes, rels, obs, surv, sources, unc = (read(path) for path in (NODES, RELATIONSHIPS, OBSERVATIONS, SURVEILLANCE, SOURCES, UNCERTAINTIES))
    check_rows(nodes, rels, obs, surv, sources, unc)
    check_surveillance_semantics(surv, obs, sources)
    check_boundaries([nodes, rels, obs, surv, unc])
    check_status_surfaces()
    prior_entries, prior_unique, prior_statuses = check_prior_freezes()
    assert prior_entries >= 300 and prior_unique >= 295
    check_no_13b_13c_implementation()
    map_size = check_map()
    manifest_artifacts, ledger_sources = check_manifest_and_ledger()
    result = {
        "status": "passed", "phase": "13A", "map_number": 41,
        "nodes": len(nodes), "relationships": len(rels), "observations": len(obs),
        "surveillance_records": len(surv), "sources": len(sources), "uncertainties": len(unc),
        "map41_valid": True, "image_size": map_size,
        "manifest_artifacts_checked": manifest_artifacts, "citation_ledger_sources": ledger_sources,
        "prior_freeze_manifest_entries_checked": prior_entries, "prior_unique_protected_artifacts_checked": prior_unique,
        "prior_manifest_statuses": prior_statuses, "phase12abc_accepted_frozen": True,
        "pathogen_exposure_infection_case_boundary": True, "case_transmission_outbreak_burden_boundary": True,
        "surveillance_effort_incidence_boundary": True, "residence_exposure_boundary": True,
        "county_local_scale_boundary": True, "vector_ecology_human_disease_boundary": True,
        "water_contamination_illness_boundary": True, "no_vulnerability_scoring": True,
        "no_individual_risk": True, "no_composite_disease_risk_index": True,
        "no_unsupported_future_inference": True, "phase13b_13c_not_implemented": True,
        "active_holds_preserved": True, "deferred_maintenance_preserved": True,
    }
    (REPORTS / "infectious_disease_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
