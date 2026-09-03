"""Validate Phase 9B qualitative climate dependencies, compounds, and controls."""
from __future__ import annotations

import hashlib
import json
import re
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
QUAL = {"strong", "moderate", "limited", "unknown", "not_applicable"}
BASIS = {"supported_system_dependency", "documented_observation_interface", "physically_plausible_system_pathway", "documented_mechanism_plus_plausible_pathway", "unsupported_unknown_interface", "documented_product_interface", "documented_control_interface"}
SUPPORT = {"documented_control", "documented_planning_context", "unknown_unverified_local_control", "potential_buffer_inference", "documented_management_pathway", "documented_tool", "plausible_control", "documented_interfaces_only"}
DEP_COLUMNS = {"dependency_id", "hazard_node_id", "affected_system", "system_interface", "dependency_type", "dependency_strength", "mechanism", "relationship_basis", "monitoring_strength", "warning_capacity", "spatial_certainty", "temporal_certainty", "source_id", "confidence", "notes"}
REG_COLUMNS = {"dependency_id", "hazard_node_id", "affected_system", "system_interface", "dependency_type", "dependency_strength", "affected_function", "evidence_basis", "source_id", "confidence", "quantity_status", "notes"}
COMP_COLUMNS = {"compound_id", "hazard_a", "hazard_b", "affected_system", "mechanism", "evidence_basis", "observed_or_plausible", "spatial_scope", "temporal_relationship", "confidence", "source_id", "notes"}
CTRL_COLUMNS = {"control_id", "control_type", "control_name", "targets", "documented_mechanism", "support_status", "effectiveness_status", "source_id", "confidence", "notes"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(frame: pd.DataFrame, key: str, value: str) -> pd.Series:
    match = frame.loc[frame[key] == value]
    assert len(match) == 1, (key, value, len(match))
    return match.iloc[0]


def check_9a() -> int:
    manifest = json.loads((R / "climate_hazard_baseline_manifest.json").read_text(encoding="utf-8"))
    for rel, metadata in manifest["artifacts"].items():
        assert manifest_matches(ROOT, rel, metadata["sha256"]), rel
    return len(manifest["artifacts"])


def check_provenance(dep: pd.DataFrame, reg: pd.DataFrame, comp: pd.DataFrame, ctl: pd.DataFrame) -> None:
    expected = {
        "HZD-001": ("supported_system_dependency", "d9_nca_energy", "strong"),
        "HZD-004": ("physically_plausible_system_pathway", "b9_usgs_dv", "strong"),
        "HZD-005": ("documented_mechanism_plus_plausible_pathway", "d9_pnas_hab", "strong"),
        "HZD-008": ("unsupported_unknown_interface", "b9_usgs_dv", "unknown"),
        "HZD-012": ("physically_plausible_system_pathway", "d9_epa_great_lakes", "moderate"),
        "HZD-013": ("documented_product_interface", "d9_noaa_llv", "moderate"),
        "HZD-014": ("physically_plausible_system_pathway", "d9_noaa_seiche", "moderate"),
        "HZD-015": ("unsupported_unknown_interface", "d9_glerl_ice", "unknown"),
        "HZD-018": ("physically_plausible_system_pathway", "d9_nws_cle_winter", "moderate"),
        "HZD-019": ("physically_plausible_system_pathway", "d9_nws_cle_winter", "limited"),
        "HZD-022": ("unsupported_unknown_interface", "d9_epa_great_lakes", "unknown"),
        "HZD-023": ("documented_control_interface", "b9_nws_points", "moderate"),
        "HZD-024": ("documented_control_interface", "b9_drought_gov", "moderate"),
    }
    for dep_id, (basis, source, strength) in expected.items():
        d = row(dep, "dependency_id", dep_id)
        r = row(reg, "dependency_id", dep_id)
        assert d.relationship_basis == basis and d.source_id == source and d.dependency_strength == strength
        assert r.evidence_basis == basis and r.source_id == source and r.dependency_strength == strength
    assert "not direct evidence of port" in row(dep, "dependency_id", "HZD-013").notes.lower()
    assert "treatment or intake" in row(dep, "dependency_id", "HZD-008").mechanism.lower()
    assert "remain unknown" in row(dep, "dependency_id", "HZD-015").notes.lower()
    assert "unsupported here" in row(dep, "dependency_id", "HZD-022").notes.lower()

    for _, c in comp.iterrows():
        if c.compound_id == "CPL-003":
            assert c.observed_or_plausible == "documented_mechanism_plus_plausible_pathway" and c.source_id == "d9_pnas_hab" and c.confidence == "high"
        else:
            assert c.observed_or_plausible == "physically_plausible_pathway"
    assert row(comp, "compound_id", "CPL-004").confidence == "limited"
    assert row(comp, "compound_id", "CPL-005").source_id == "d9_noaa_seiche"
    assert row(comp, "compound_id", "CPL-007").source_id == "d9_nws_cle_winter"
    assert row(comp, "compound_id", "CPL-009").source_id == "b9_drought_gov"

    expected_controls = {
        "HZC-001": ("documented_control", "b9_nws_points"),
        "HZC-002": ("documented_control", "b9_nws_points"),
        "HZC-004": ("documented_control", "b9_coops_daily"),
        "HZC-007": ("documented_planning_context", "bge_ohio_epa_npdes"),
        "HZC-008": ("potential_buffer_inference", "bge_usfws_nwi"),
        "HZC-009": ("documented_management_pathway", "bge_ohio_h2ohio"),
        "HZC-010": ("documented_tool", "d9_noaa_llv"),
        "HZC-011": ("plausible_control", "d9_nws_cle_winter"),
        "HZC-012": ("documented_interfaces_only", "d9_nws_gl_obs"),
    }
    for control_id, (status, source) in expected_controls.items():
        c = row(ctl, "control_id", control_id)
        assert c.support_status == status and c.source_id == source
    assert "no local" in row(ctl, "control_id", "HZC-007").documented_mechanism.lower()
    assert "calm-day" in row(ctl, "control_id", "HZC-010").notes.lower()
    assert not ctl.effectiveness_status.str.contains(r"effective(?!ness)|guarantee|eliminat", case=False, regex=True).any()


def main() -> None:
    dep = read(N / "climate_hazard_dependency_edges.csv")
    reg = read(A / "climate_hazard_dependency_register.csv")
    comp = read(A / "climate_compound_event_register.csv")
    ctl = read(A / "climate_resilience_control_register.csv")
    mat = read(A / "climate_hazard_dependency_matrix.csv")
    src = read(A / "climate_dependency_sources.csv")
    base = read(N / "climate_hazard_nodes.csv")
    assert set(dep.columns) == DEP_COLUMNS
    assert set(reg.columns) == REG_COLUMNS
    assert set(comp.columns) == COMP_COLUMNS
    assert set(ctl.columns) == CTRL_COLUMNS
    assert len(dep) == 24 and dep.dependency_id.is_unique
    assert len(reg) == 24 and reg.dependency_id.is_unique
    assert len(comp) == 9 and comp.compound_id.is_unique
    assert len(ctl) == 12 and ctl.control_id.is_unique
    assert len(mat) == 9
    assert len(src) == 14 and src.source_id.is_unique
    source_ids = set(src.source_id) | set(read(A / "climate_hazard_sources.csv").source_id)
    assert dep.hazard_node_id.isin(set(base.node_id)).all() and reg.hazard_node_id.isin(set(base.node_id)).all()
    assert dep.source_id.isin(source_ids).all() and reg.source_id.isin(source_ids).all() and comp.source_id.isin(source_ids).all() and ctl.source_id.isin(source_ids).all()
    for registry_only in ("d9_fema_nfhl", "d9_noaa_inundation"):
        source_row = row(src, "source_id", registry_only)
        assert "registry-only" in source_row.use_limitations.lower()
        assert not any(registry_only in frame.source_id.to_list() for frame in (dep, reg, comp, ctl))
    assert dep.relationship_basis.isin(BASIS).all() and reg.evidence_basis.isin(BASIS).all() and ctl.support_status.isin(SUPPORT).all()
    assert dep.dependency_strength.isin(QUAL).all() and dep.monitoring_strength.isin(QUAL).all() and dep.warning_capacity.isin(QUAL).all() and dep.spatial_certainty.isin(QUAL).all() and dep.temporal_certainty.isin(QUAL).all()
    assert reg.dependency_strength.isin(QUAL).all()
    assert comp.observed_or_plausible.isin({"historically_documented", "physically_plausible_pathway", "documented_mechanism_plus_plausible_pathway"}).all()
    assert comp.confidence.isin({"high", "moderate", "limited", "unknown"}).all() and ctl.confidence.isin({"high", "moderate", "limited", "unknown"}).all()
    assert mat.iloc[:, 1:-1].stack().isin(QUAL).all()
    for frame in (dep, reg, comp, ctl, mat, src):
        column = "notes" if "notes" in frame.columns else "use_limitations"
        assert frame[column].str.len().gt(0).all()
    check_provenance(dep, reg, comp, ctl)

    text = " ".join(" ".join(map(str, values)) for frame in (dep, reg, comp, ctl, mat) for values in frame.to_numpy()).lower()
    assert "2050" not in text and "2075" not in text
    assert not re.search(r"(^|,)(probability|risk_score|hazard_score|mortality|dose|social_vulnerability)(,|$)", text)
    assert "joint probability" in text and "no joint probability" in text
    assert "emergency-management model" in text and "no comprehensive emergency-management model" in text
    assert "unknown" in dep.loc[dep.relationship_basis == "unsupported_unknown_interface", "dependency_strength"].tolist()
    assert not re.search(r"(?:outage|damage|mortality|disease|social[-_ ]vulnerability)\s*(?:probability|score|estimate)\s*[,=:]\s*[0-9]", text)

    with Image.open(M / "30_climate_hazard_dependencies_resilience_2026.png") as image:
        image.verify()
        image_size = list(image.size)
    svg_text = " ".join(ET.parse(M / "30_climate_hazard_dependencies_resilience_2026.svg").getroot().itertext()).lower()
    for term in ["map 30", "compound pathways", "heat + power", "precipitation + nutrient", "lake level", "freeze-thaw", "not routes", "seiche", "not ocean storm surge"]:
        assert term in svg_text, term
    manifest = json.loads((R / "climate_dependency_manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"] == {"dependency_edges": 24, "dependency_register": 24, "compound_events": 9, "controls": 12, "matrix_rows": 9}
    for rel, metadata in manifest["artifacts"].items():
        assert (ROOT / rel).exists() and sha(ROOT / rel) == metadata["sha256"], rel
    protected = check_9a()
    result = {"status": "passed", "phase": "9B", "dependency_edges": len(dep), "dependency_register": len(reg), "compound_events": len(comp), "controls": len(ctl), "matrix_rows": len(mat), "map30_valid": True, "phase9a_artifacts_checked": protected, "explicit_relationship_basis_checked": True, "explicit_control_support_checked": True, "probabilities_absent": True, "composite_score_absent": True, "phase9a_immutable": True, "health_social_scope_absent": True}
    (R / "phase9b_artifact_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
