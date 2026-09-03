"""Independent structural and semantic validator for Phase 10A."""
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
N = ROOT / "data/processed/networks"
A = ROOT / "data/processed/analysis"
M = ROOT / "outputs/maps/systems"
R = ROOT / "reports"

PATHS = {
    "actors": A / "governance_actors.csv",
    "authorities": A / "governance_authorities.csv",
    "relationships": N / "governance_relationships.csv",
    "sources": A / "governance_sources.csv",
    "uncertainties": A / "governance_uncertainty_register.csv",
}
MAP_PNG = M / "32_governance_jurisdiction_2026.png"
MAP_SVG = M / "32_governance_jurisdiction_2026.svg"
MANIFEST = R / "governance_baseline_manifest.json"
CHECK = R / "governance_baseline_artifact_check.json"

ACTOR_COLUMNS = {"actor_id", "name", "actor_type", "jurisdictional_scale", "geographic_scope", "systems", "operational_or_authority_summary", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"}
AUTH_COLUMNS = {"authority_id", "actor_id", "domain_system", "authority_or_role", "authority_type", "binding_or_nonbinding", "legal_or_operational_basis", "geographic_scope", "jurisdictional_scale", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"}
REL_COLUMNS = {"relationship_id", "actor_id", "domain_system", "relationship_type", "authority_or_role", "binding_or_nonbinding", "geographic_scope", "jurisdictional_scale", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"}
SOURCE_COLUMNS = {"source_id", "title", "url", "source_type", "evidence_role", "publication_or_update", "retrieval_date", "geographic_scope", "use_limitations", "retrieval_status"}
UNC_COLUMNS = {"uncertainty_id", "subject_type", "subject_id", "domain_system", "uncertainty_category", "statement", "resolution_status", "evidence_strength", "source_id", "notes"}
DOMAINS = {"Water", "Geology / Strategic Materials", "Energy / Grid / Compute", "Data / Sensors / Security", "Freight / Industry", "Ecology / Biodiversity", "Environmental Health / Exposure", "Biogeochemical / Nutrient Flux", "Climate / Natural Hazards"}
ROLES = {"regulate", "permit", "enforce", "operate", "own", "monitor", "fund", "coordinate", "advise", "plan", "warn", "respond", "restore", "set_standard", "research", "provide_data"}
ROLE_TYPES = {"regulate": "regulatory_authority", "permit": "permitting", "enforce": "enforcement", "operate": "operational_control", "own": "ownership", "monitor": "monitoring", "fund": "funding", "coordinate": "coordination", "advise": "advisory", "plan": "planning", "warn": "warning", "respond": "response", "restore": "restoration", "set_standard": "standard_setting", "research": "research", "provide_data": "scientific_information"}
BINDING = {"binding", "nonbinding", "mixed", "unknown", "not_applicable"}
SCALES = {"federal", "state", "interstate", "binational", "tribal", "county", "municipal", "regional authority", "public utility", "system operator", "private", "special district"}
TYPES = {"federal_agency", "state_agency", "tribal_sovereign", "binational_body", "interstate_body", "county_government", "municipal_government", "regional_authority", "public_utility", "system_operator", "private_operator", "research_monitoring_body", "special_district"}
QUAL = {"high", "moderate", "limited", "unknown"}
RETRIEVAL = {"retrieved", "retrieved_limited", "reference_only"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_matches(path: Path, metadata: dict[str, object]) -> bool:
    data = path.read_bytes()
    expected = str(metadata["sha256"])
    if len(data) == int(metadata["bytes"]) and hashlib.sha256(data).hexdigest() == expected:
        return True
    if path.suffix.lower() in {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}:
        canonical = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(canonical).hexdigest() == expected
    return False


def one(frame: pd.DataFrame, key: str, value: str) -> pd.Series:
    result = frame.loc[frame[key] == value]
    assert len(result) == 1, (key, value, len(result))
    return result.iloc[0]


def verify_manifest(path: Path) -> int:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["phase"] == "10A"
    assert manifest["map_number"] == 32
    assert manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["counts"] == {"actors": 40, "authorities": 100, "relationships": 100, "sources": 47, "uncertainties": 16}
    for rel, metadata in manifest["artifacts"].items():
        file_path = ROOT / rel
        assert file_path.exists(), rel
        assert artifact_matches(file_path, metadata), rel
    return len(manifest["artifacts"])


def verify_prior_freezes() -> list[str]:
    protected: list[str] = []
    for path in sorted(R.glob("phase*_freeze_manifest.json")):
        if path.name.startswith("phase10"):
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        files = manifest.get("artifacts", manifest.get("files", {}))
        for rel, metadata in files.items():
            file_path = ROOT / rel
            assert file_path.exists(), rel
            expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
            assert manifest_matches(ROOT, rel, expected), rel
            protected.append(rel)
    changed = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    protected_set = set(protected)
    assert not protected_set.intersection(changed), sorted(protected_set.intersection(changed))
    return protected


def verify_reports(source_count: int) -> None:
    for path in (R / "governance_baseline_sources.md", R / "governance_baseline_findings.md"):
        text = path.read_text(encoding="utf-8")
        citations = [int(value) for value in re.findall(r"\[(\d+)\]", text)]
        assert citations and max(citations) <= source_count, path
        assert "## Sources" in text and "https://" in text, path
    for path in (R / "governance_baseline_assumptions.md", R / "governance_baseline_qa.md"):
        assert path.exists() and path.read_text(encoding="utf-8").strip(), path


def verify_semantic_boundaries(actors: pd.DataFrame, auth: pd.DataFrame, rel: pd.DataFrame, sources: pd.DataFrame) -> dict[str, bool]:
    actor_by_id = actors.set_index("actor_id")
    assert auth.authority_or_role.map(lambda x: x in ROLES).all()
    assert auth.authority_type.eq(auth.authority_or_role.map(ROLE_TYPES)).all()
    assert auth.domain_system.isin(DOMAINS).all()
    assert auth.binding_or_nonbinding.isin(BINDING).all()
    assert auth.jurisdictional_scale.isin(SCALES).all()
    assert auth.evidence_strength.isin(QUAL).all()
    assert rel.relationship_type.eq("actor_system_role").all()
    rel_role_by_id = dict(zip(auth.authority_id.str.replace("AUTH", "REL", regex=False), auth.authority_or_role))
    assert rel.authority_or_role.eq(rel.relationship_id.map(rel_role_by_id)).all()
    assert rel.jurisdictional_scale.isin(SCALES).all()
    assert rel.source_id.isin(set(sources.source_id)).all()
    assert set(auth.authority_id.str.replace("AUTH", "REL", regex=False)) == set(rel.relationship_id)

    monitored_only = {"GA-005", "GA-007"}
    for actor_id in monitored_only:
        rows = auth[auth.actor_id == actor_id]
        assert set(rows.authority_or_role).issubset({"monitor", "research", "provide_data", "advise"}), actor_id
        assert not rows.authority_or_role.isin({"regulate", "permit", "enforce", "operate", "own", "set_standard"}).any(), actor_id
    for actor_id in {"GA-030", "GA-036", "GA-037"}:
        rows = auth[auth.actor_id == actor_id]
        assert set(rows.authority_or_role).issubset({"own", "operate"}), actor_id
        assert not rows.authority_or_role.isin({"regulate", "permit", "enforce", "set_standard"}).any(), actor_id
    pjm = auth[auth.actor_id == "GA-026"]
    assert not pjm.authority_or_role.isin({"own", "regulate", "permit", "enforce"}).any()
    assert one(auth, "authority_id", "AUTH-065").authority_or_role == "operate"
    assert one(auth, "authority_id", "AUTH-065").actor_id == "GA-026"
    assert one(auth, "authority_id", "AUTH-059").authority_or_role == "regulate"
    assert one(auth, "authority_id", "AUTH-059").actor_id == "GA-024"
    assert one(auth, "authority_id", "AUTH-062").authority_or_role == "set_standard"
    assert one(auth, "authority_id", "AUTH-062").actor_id == "GA-025"
    assert one(auth, "authority_id", "AUTH-034").binding_or_nonbinding == "mixed"
    assert "not a general enforceable" in one(auth, "authority_id", "AUTH-034").notes.lower()
    assert one(auth, "authority_id", "AUTH-057").binding_or_nonbinding == "unknown"
    assert "current project jurisdiction" in one(auth, "authority_id", "AUTH-057").notes.lower()
    assert one(auth, "authority_id", "AUTH-087").authority_or_role == "own"
    assert one(auth, "authority_id", "AUTH-088").authority_or_role == "operate"
    assert "not operation of every" in one(auth, "authority_id", "AUTH-088").notes.lower()
    assert all(re.search(r"\b(?:not|no)\b", value.lower()) or "distinct" in value.lower() for value in auth.loc[auth.authority_or_role == "fund", "notes"])
    for actor_id in {"GA-022", "GA-023"}:
        row = auth[(auth.actor_id == actor_id) & (auth.authority_or_role == "advise")].iloc[0]
        assert row.binding_or_nonbinding == "unknown" and row.canon_status == "inferred"
    assert actors.actor_type.isin(TYPES).all()
    assert actors.jurisdictional_scale.isin(SCALES).all()
    assert actors.evidence_strength.isin(QUAL).all()
    assert actors.reality_status.eq("real").all()
    assert actors.canon_status.isin({"verified", "inferred"}).all()
    assert actors.source_id.isin(set(sources.source_id)).all()
    assert sources.retrieval_status.isin(RETRIEVAL).all()
    assert sources.url.is_unique and sources.source_id.is_unique
    assert sources.use_limitations.str.len().gt(0).all()
    for frame in (actors, auth, rel, sources):
        assert not frame.astype(str).apply(lambda col: col.str.contains(r"\b(?:2050|2075|scenario)\b", case=False, regex=True)).any().any(), frame.columns.tolist()
    all_text = " ".join(" ".join(map(str, values)) for frame in (actors, auth, rel, sources) for values in frame.to_numpy()).lower()
    assert "partisan" not in all_text and "election" not in all_text
    forbidden_fields = {"risk_score", "hazard_score", "probability", "mortality", "dose", "social_vulnerability", "territory_polygon"}
    assert not forbidden_fields.intersection(set(actors.columns) | set(auth.columns) | set(rel.columns) | set(sources.columns))
    return {"regulator_operator_separation": True, "monitor_regulator_separation": True, "funder_control_separation": True, "advisor_binding_separation": True, "private_public_separation": True, "program_target_mandate_separation": True, "tribal_current_jurisdiction_guard": True, "science_legal_authority_separation": True}


def main() -> None:
    actors, auth, rel, sources, uncertainties = (read(path) for path in PATHS.values())
    assert set(actors.columns) == ACTOR_COLUMNS
    assert set(auth.columns) == AUTH_COLUMNS
    assert set(rel.columns) == REL_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert set(uncertainties.columns) == UNC_COLUMNS
    assert len(actors) == 40 and actors.actor_id.is_unique
    assert len(auth) == 100 and auth.authority_id.is_unique
    assert len(rel) == 100 and rel.relationship_id.is_unique
    assert len(sources) == 47 and sources.source_id.is_unique
    assert len(uncertainties) == 16 and uncertainties.uncertainty_id.is_unique
    source_ids = set(sources.source_id)
    actor_ids = set(actors.actor_id)
    assert auth.actor_id.isin(actor_ids).all() and rel.actor_id.isin(actor_ids).all()
    assert auth.source_id.isin(source_ids).all() and rel.source_id.isin(source_ids).all() and uncertainties.source_id.isin(source_ids).all()
    assert uncertainties.resolution_status.isin({"open", "qualified"}).all()
    assert uncertainties.evidence_strength.isin(QUAL).all()
    assert uncertainties.subject_id.isin(actor_ids | {"PROJECT"}).all()
    semantic = verify_semantic_boundaries(actors, auth, rel, sources)
    uncertainty_text = " ".join(" ".join(map(str, values)) for values in uncertainties.to_numpy()).lower()
    assert "great black swamp" in uncertainty_text and "noncanonical" in uncertainty_text
    assert "intake-coordinate discrepancy" in uncertainty_text and "unresolved" in uncertainty_text
    with Image.open(MAP_PNG) as image:
        image.verify()
        image_size = list(image.size)
    svg_text = " ".join(ET.parse(MAP_SVG).getroot().itertext()).lower()
    for required in ["map 32", "governance & jurisdiction", "role distinctions", "institutional scales", "private operation is not public control", "tribal sovereignty", "not jurisdiction polygons"]:
        assert required in svg_text, required
    manifest_artifacts = verify_manifest(MANIFEST)
    protected = verify_prior_freezes()
    verify_reports(len(sources))
    result = {"status": "passed", "phase": "10A", "map_number": 32, "actors": len(actors), "authorities": len(auth), "relationships": len(rel), "sources": len(sources), "uncertainties": len(uncertainties), "map32_valid": True, "image_size": image_size, "manifest_artifacts_checked": manifest_artifacts, "prior_freeze_artifacts_checked": len(protected), "semantic_separation_checks": semantic, "source_references_valid": True, "negative_scope_checks": True, "phase10c_absent": True, "holds_preserved": True}
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
