"""Validate the factual Phase 9A climate and natural-hazards baseline."""
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
RAW = ROOT / "data/raw/climate_hazards"
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
NODES = NETWORKS / "climate_hazard_nodes.csv"
EDGES = NETWORKS / "climate_hazard_edges.csv"
OBS = ANALYSIS / "climate_hazard_observations.csv"
SOURCES = ANALYSIS / "climate_hazard_sources.csv"
MAP_PNG = MAPS / "29_climate_natural_hazards_2026.png"
MAP_SVG = MAPS / "29_climate_natural_hazards_2026.svg"
MANIFEST = REPORTS / "climate_hazard_baseline_manifest.json"
CHECK = REPORTS / "phase9a_artifact_check.json"

NODE_COLUMNS = {"node_id", "name", "hazard_family", "node_type", "reality_status", "canon_status", "scale", "latitude", "longitude", "spatial_role", "source_id", "confidence", "notes"}
EDGE_COLUMNS = {"edge_id", "from_id", "to_id", "relationship_type", "relationship_basis", "scale", "source_id", "confidence", "notes"}
OBS_COLUMNS = {"observation_id", "hazard_family", "metric", "value", "units", "period", "station_or_scope", "spatial_scale", "observed_or_modeled", "source_id", "confidence", "notes"}
SOURCE_COLUMNS = {"source_id", "title", "url", "product_or_endpoint", "source_type", "observation_or_model", "spatial_scope", "temporal_scope", "retrieval_date", "use_limitations"}
QUALITATIVE = {"high", "moderate", "limited", "unknown"}
SCALES = {"station", "county", "NWS point / service area", "HUC8 / HUC12 interface", "station / river reach", "river / floodplain interface", "modeled regulatory flood zone", "urban area / subwatershed", "station / shoreline", "western Lake Erie / shoreline", "shoreline / nearshore", "western Lake Erie / bay", "regional / county event context", "county / event record", "regional / forecast area", "forecast area / county", "station / river network", "station / county / regional", "station / Great Lakes network", "county / regional status", "site / regional frequency product", "Great Lakes / station network", "urban / regional function", "HUC8 / river / floodplain", "HUC8 / station", "HUC8 / station network", "county / station", "station / Great Lakes", "station / river", "lake / network", "county / regional", "regional / county", "regional / urban", "site / HUC8", "river / floodplain", "river / forecast area", "urban / river", "lake / station network", "HUC8 / floodplain", "county / urban", "station / urban"}
OBS_STATUSES = {"observed", "derived from observed", "observed_adjusted_series", "expert_assessed_status", "expert_assessed_index", "historical_event_record", "warning_threshold"}
RELATIONSHIPS = {"observed_by", "warning_for", "hydrologically_amplified_by", "affects", "forecast_by", "monitored_by", "coastal_interface_with", "historically_occurs_in"}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_prior_manifests() -> list[str]:
    protected = []
    for path in sorted(REPORTS.glob("phase*_freeze_manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for rel, metadata in manifest.get("artifacts", manifest.get("files", {})).items():
            artifact = ROOT / rel
            assert artifact.exists(), rel
            expected = metadata["sha256"] if isinstance(metadata, dict) else metadata
            assert manifest_matches(ROOT, rel, expected), rel
            protected.append(rel)
    return protected


def check_usgs_raw_extreme() -> tuple[str, str]:
    payload = json.loads((RAW / "usgs_maumee_waterville_daily_flow_2025_2026.json").read_text(encoding="utf-8"))
    values = {}
    for block in payload["value"]["timeSeries"][0]["values"]:
        for value in block["value"]:
            values[value["dateTime"][:10]] = value.get("value")
    assert values.get("2026-07-29") == "313", values.get("2026-07-29")
    assert values.get("2026-09-02") == "476", values.get("2026-09-02")
    return "2026-07-29", "313"


def row(frame: pd.DataFrame, key: str, value: str) -> pd.Series:
    match = frame.loc[frame[key] == value]
    assert len(match) == 1, (key, value, len(match))
    return match.iloc[0]


def check_explicit_provenance(nodes: pd.DataFrame, edges: pd.DataFrame, obs: pd.DataFrame) -> None:
    n004 = row(nodes, "node_id", "HZ-004")
    assert n004.source_id == "b9_usgs_dv" and n004.canon_status == "inferred" and n004.confidence == "limited"
    assert "project-inferred" in n004.notes.lower() and "does not establish watershed-wide runoff" in n004.notes.lower()
    n008 = row(nodes, "node_id", "HZ-008")
    assert n008.source_id == "b9_noaa_atlas14" and n008.canon_status == "inferred"
    assert "project-inferred" in n008.notes.lower() and "supports site/grid precipitation-frequency context only" in n008.notes.lower()
    n016 = row(nodes, "node_id", "HZ-016")
    assert n016.source_id == "b9_storm_events_2025" and "dated 2025 details snapshot" in n016.notes.lower()
    n021 = row(nodes, "node_id", "HZ-021")
    assert n021.source_id == "b9_coops_daily" and n021.scale == "station / shoreline"
    n026 = row(nodes, "node_id", "HZ-026")
    assert "project-inferred" in n026.notes.lower() and "nws point metadata" in n026.notes.lower()
    assert row(nodes, "node_id", "HZ-024").source_id == "b9_ncei_cag" and row(nodes, "node_id", "HZ-024").scale == "county"
    assert row(nodes, "node_id", "HZ-027").source_id == "b9_acis" and row(nodes, "node_id", "HZ-027").scale == "station"
    assert row(nodes, "node_id", "HZ-028").source_id == "b9_storm_events_2025" and row(nodes, "node_id", "HZ-028").scale == "county / event record"

    expected_edges = {
        "HZE-004": ("b9_usgs_dv", "project inference", "limited"),
        "HZE-007": ("b9_noaa_atlas14", "project inference", "limited"),
        "HZE-018": ("b9_storm_events_2025", "historical event-record aggregation", "high"),
        "HZE-021": ("b9_nws_winter", "project inference", "limited"),
        "HZE-022": ("b9_nws_thunderstorm", "project inference", "limited"),
        "HZE-029": ("b9_usdm_area", "project inference", "limited"),
        "HZE-030": ("b9_acis", "project inference", "limited"),
    }
    for edge_id, (source_id, basis, confidence) in expected_edges.items():
        e = row(edges, "edge_id", edge_id)
        assert e.source_id == source_id and basis in e.relationship_basis.lower() and e.confidence == confidence
        assert "inference" in e.notes.lower() or "aggregation" in e.notes.lower() or "project-inferred" in e.notes.lower() or "snapshot" in e.notes.lower()
    hze004 = row(edges, "edge_id", "HZE-004")
    assert hze004.from_id == "HZ-006" and hze004.to_id == "HZ-004"
    assert "HZE-023" not in set(edges.edge_id)

    event_rows = obs[obs.observation_id.isin([f"HZO-{i:03d}" for i in range(21, 27)])]
    assert len(event_rows) == 6
    assert event_rows.source_id.eq("b9_storm_events_2025").all()
    assert event_rows.units.eq("county event records").all()
    assert event_rows.spatial_scale.eq("county / event record").all()
    assert event_rows.notes.str.contains("not a rate", case=False).any()


def check_semantic_boundaries(nodes: pd.DataFrame, edges: pd.DataFrame, obs: pd.DataFrame) -> None:
    flood = row(nodes, "node_id", "HZ-007")
    assert flood.scale == "modeled regulatory flood zone" and flood.node_type == "floodplain_context"
    assert "distinct from observed" in flood.notes.lower()
    e006 = row(edges, "edge_id", "HZE-006")
    e028 = row(edges, "edge_id", "HZE-028")
    assert e006.source_id == "b9_fema_nfhl" and "not an observed flood footprint" in e006.notes.lower()
    assert e028.source_id == "b9_fema_nfhl" and "remain distinct categories" in e028.notes.lower()

    event_rows = obs[obs.observation_id.isin([f"HZO-{i:03d}" for i in range(21, 27)])]
    assert event_rows.metric.str.contains("event records", case=False).all()
    assert not event_rows.metric.str.contains("rate|probability", case=False).any()
    note_requirements = {"HZO-021": "not a rate", "HZO-022": "deterministic", "HZO-023": "probability", "HZO-024": "distinct from", "HZO-025": "not a regional", "HZO-026": "qualitative"}
    for observation_id, required in note_requirements.items():
        assert required in row(obs, "observation_id", observation_id).notes.lower()

    for item_id, text in {
        "HZ-009": row(nodes, "node_id", "HZ-009").notes,
        "HZ-022": row(nodes, "node_id", "HZ-022").notes,
        "HZO-013": row(obs, "observation_id", "HZO-013").notes,
        "HZO-020": row(obs, "observation_id", "HZO-020").notes,
    }.items():
        assert "groundwater" in text.lower() and re.search(r"\bno\b|\bnot\b", text.lower())
    assert not re.search(r"groundwater\s+(?:depletion|level|impact)\s*(?:is|=|:)?\s*(?:observed|estimated|high|low|[0-9])", " ".join(obs.notes).lower())

    assert set(nodes.scale).issuperset({"station", "county", "HUC8 / HUC12 interface", "modeled regulatory flood zone", "station / shoreline"})
    assert set(obs.spatial_scale).issuperset({"station", "county", "county / event record"})
    assert row(obs, "observation_id", "HZO-027").observed_or_modeled == "warning_threshold"
    assert row(obs, "observation_id", "HZO-027").units.startswith("feet;")


def main() -> None:
    nodes, edges, obs, sources = (read(path) for path in (NODES, EDGES, OBS, SOURCES))
    assert set(nodes.columns) == NODE_COLUMNS
    assert set(edges.columns) == EDGE_COLUMNS
    assert set(obs.columns) == OBS_COLUMNS
    assert set(sources.columns) == SOURCE_COLUMNS
    assert len(nodes) == 28 and nodes.node_id.is_unique
    assert len(edges) == 29 and edges.edge_id.is_unique
    assert len(obs) == 28 and obs.observation_id.is_unique
    assert len(sources) == 21 and sources.source_id.is_unique and sources.url.is_unique
    source_ids = set(sources.source_id)
    node_ids = set(nodes.node_id)
    assert nodes.source_id.isin(source_ids).all()
    assert edges.source_id.isin(source_ids).all()
    assert obs.source_id.isin(source_ids).all()
    assert edges.from_id.isin(node_ids).all() and edges.to_id.isin(node_ids).all()
    assert nodes.reality_status.eq("real").all()
    assert nodes.canon_status.isin({"verified", "inferred"}).all()
    assert nodes.confidence.isin(QUALITATIVE).all() and edges.confidence.isin(QUALITATIVE).all() and obs.confidence.isin(QUALITATIVE).all()
    assert nodes.scale.isin(SCALES).all() and edges.scale.isin(SCALES | {"station / forecast area", "regional / river / floodplain", "station / event record"}).all()
    assert edges.relationship_type.isin(RELATIONSHIPS).all()
    assert obs.spatial_scale.isin(SCALES | {"regional / county event context", "county / event record"}).all()
    assert obs.observed_or_modeled.isin(OBS_STATUSES).all()
    assert obs.value.map(lambda value: bool(re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", value))).all()
    for frame in (nodes, edges, obs):
        assert frame.notes.str.len().gt(0).all()
    assert sources.use_limitations.str.len().gt(0).all()
    for _, item in nodes.iterrows():
        for col in ("latitude", "longitude"):
            if item[col] != "":
                value = float(item[col])
                assert -90 <= value <= 90 if col == "latitude" else -180 <= value <= 180
        assert not (item.latitude == "" and item.longitude != "")
        assert not (item.latitude != "" and item.longitude == "")
    assert nodes.loc[nodes.node_id == "HZ-001", "latitude"].iloc[0] == "41.56327"
    assert nodes.loc[nodes.node_id == "HZ-011", "longitude"].iloc[0] == "-83.4723"
    min_date, min_value = check_usgs_raw_extreme()
    hzo015 = row(obs, "observation_id", "HZO-015")
    assert hzo015.value == "313.0" and hzo015.period == min_date
    assert row(obs, "observation_id", "HZO-014").value == "68200.0"
    assert row(obs, "observation_id", "HZO-021").value == "58.0"
    assert row(obs, "observation_id", "HZO-018").value == "100.0"
    check_explicit_provenance(nodes, edges, obs)
    check_semantic_boundaries(nodes, edges, obs)

    field_names = set(nodes.columns) | set(edges.columns) | set(obs.columns) | set(sources.columns)
    assert not field_names & {"hazard_score", "risk_score", "probability", "mortality", "exposure_estimate", "dose", "social_vulnerability"}
    data_text = " ".join(" ".join(map(str, row_values)) for frame in (nodes, edges, obs, sources) for row_values in frame.to_numpy()).lower()
    assert not re.search(r"(?:hazard|event|outage)[ _-]probability\s*[,=:]\s*[0-9]", data_text)
    assert not re.search(r"(?:mortality|hospitalization|disease incidence|dose)\s*[,=:]\s*[0-9]", data_text)
    assert "future" not in " ".join(obs.period.str.lower())
    assert "2050" not in data_text and "2075" not in data_text
    assert "ocean storm surge" in data_text
    for match in re.finditer(r"ocean storm surge", data_text):
        assert "not" in data_text[max(0, match.start() - 30):match.start()]
    with Image.open(MAP_PNG) as image:
        image.verify()
        image_size = list(image.size)
    root = ET.parse(MAP_SVG).getroot()
    svg_text = " ".join(root.itertext())
    for required in ["MAP 29", "EXTREME HEAT", "PRECIP / FLOOD", "DROUGHT / LOW WATER", "LAKE / COASTAL", "CONVECTIVE", "WINTER", "not hazard zones", "seiche"]:
        assert required.lower() in svg_text.lower(), required
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phase"] == "9A" and manifest["status"] == "implemented_validated_pending_sol_acceptance"
    assert manifest["counts"] == {"nodes": 28, "edges": 29, "observations": 28, "sources": 21}
    for rel, metadata in manifest["artifacts"].items():
        path = ROOT / rel
        assert path.exists() and digest(path) == metadata["sha256"] and path.stat().st_size == metadata["bytes"], rel
    protected = check_prior_manifests()
    changed = subprocess.run(["git", "diff", "--name-only", "main"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    assert not any(path.startswith("outputs/maps/systems/2[0-8]") for path in changed)
    assert not any(path.startswith("data/processed/networks/biogeochemical_") for path in changed)
    result = {"status": "passed", "phase": "9A", "nodes": len(nodes), "edges": len(edges), "observations": len(obs), "sources": len(sources), "map29_valid": True, "image_size": image_size, "phase8_and_prior_frozen_artifacts_checked": len(protected), "usgs_2026_minimum_checked": {"date": min_date, "value_cfs": int(min_value)}, "explicit_provenance_assertions": True, "semantic_boundary_assertions": True, "future_rows_absent": True, "unsupported_probabilities_absent": True, "health_and_social_scoring_absent": True, "scale_distinctions_checked": True, "regulatory_observed_forecast_distinctions_checked": True}
    CHECK.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
