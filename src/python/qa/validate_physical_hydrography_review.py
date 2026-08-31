"""Validate the Phase 1 physical-hydrography QA package without canonical writes."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "usgs" / "3dhp_flowlines_maumee_buffer500m.geojson.gz"
MANIFEST = ROOT / "reports" / "physical_hydrography_source_manifest.json"
SUMMARY = ROOT / "reports" / "physical_hydrography_qa.json"
RECONCILIATION = ROOT / "reports" / "wbd_connector_reconciliation.csv"
TRANSITIONS = ROOT / "outputs" / "qa" / "data" / "3dhp_huc12_transitions.csv"
ROUTING = ROOT / "outputs" / "qa" / "data" / "huc12_authoritative_routing.csv"
UNRESOLVED = ROOT / "reports" / "unresolved_routing_summary.csv"
GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
TRANSITION_MANIFEST = ROOT / "reports" / "development_gpkg_transition_manifest.json"
EXPECTED_GPKG_SHA256 = "555D23D076638E69942C9BB5D6B1043D00A152A945788BDB7C988EE72C576882"
ALLOWED_STATUS = {
    "REPLACED_PHYSICAL",
    "REPLACED_AUTHORITATIVE_CONNECTOR",
    "ALREADY_REDUNDANT",
    "UNRESOLVED",
    "INVALID_BASELINE_INFERENCE",
}
ALLOWED_TYPES = {
    "Channel Line",
    "Canal",
    "Drainageway",
    "Surface Connector",
    "Waterbody Connector",
    "Elevation Breaching Connector",
    "Hydro Unenforced Connector",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    required = [
        RAW,
        MANIFEST,
        SUMMARY,
        RECONCILIATION,
        TRANSITIONS,
        ROUTING,
        UNRESOLVED,
        ROOT / "reports" / "water_hydrography_source_review.md",
        ROOT / "reports" / "physical_hydrography_reconciliation.md",
        ROOT / "reports" / "physical_hydrography_baseline_comparison.csv",
        ROOT / "outputs" / "qa" / "hydrography_baseline_vs_authoritative.png",
        ROOT / "outputs" / "qa" / "hydrography_baseline_vs_authoritative.svg",
        ROOT / "outputs" / "qa" / "huc12_routing_reconciliation.png",
        ROOT / "outputs" / "qa" / "huc12_routing_reconciliation.svg",
    ]
    require(all(path.exists() and path.stat().st_size > 0 for path in required), "Missing QA artifact")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if TRANSITION_MANIFEST.exists():
        integration = json.loads(TRANSITION_MANIFEST.read_text(encoding="utf-8"))
        require(integration["historical_v0_1_gpkg_sha256"] == EXPECTED_GPKG_SHA256, "Historical v0.1 hash record changed")
        # The transition hash is an immutable receipt for the hydrography-only
        # integration, not a permanent whole-file lock. Later phases may add
        # layers to the current-development GeoPackage; hydro layer semantics
        # and counts are validated independently below.
        require(integration["current_development_gpkg_sha256"] == manifest["current_development_gpkg_sha256"], "Hydrography transition hash record changed")
        require(manifest["historical_v0_1_gpkg_sha256"] == EXPECTED_GPKG_SHA256, "Source manifest historical hash mismatch")
    else:
        require(sha256(GPKG) == EXPECTED_GPKG_SHA256, "Pre-integration GeoPackage changed")
        require(manifest["canonical_gpkg_sha256"] == EXPECTED_GPKG_SHA256, "Manifest canonical hash mismatch")
    require(sha256(RAW) == manifest["raw_snapshot_sha256"], "Raw snapshot hash mismatch")
    require(summary["human_decision"] == "B — ACCEPT WITH QUALIFICATION", "Human decision mismatch")
    require(summary["review_status"] == "accepted_with_qualification", "Review acceptance status mismatch")
    require(summary["canonical_status"] in {"current_development_integration_pending", "accepted_current_development"}, "Unexpected development integration status")

    with gzip.open(RAW, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    flowlines = gpd.GeoDataFrame.from_features(payload["features"], crs="EPSG:4326")
    flowlines.columns = [str(column).lower() for column in flowlines.columns]
    require(str(flowlines.crs) == "EPSG:4326", "Raw snapshot CRS mismatch")
    require(len(flowlines) == manifest["feature_count"] == summary["feature_count"], "Feature count mismatch")
    require(flowlines["objectid"].is_unique, "Duplicate OBJECTID")
    require(flowlines["id3dhp"].is_unique, "Duplicate id3dhp")
    require(not flowlines.geometry.isna().any(), "Null geometry")
    require(not flowlines.geometry.is_empty.any(), "Empty geometry")
    require(flowlines.geometry.is_valid.all(), "Invalid geometry")
    require(set(flowlines["featuretypelabel"].dropna()) <= ALLOWED_TYPES, "Unknown feature type")
    require(flowlines["workunitid"].astype(str).eq("NHD").sum() == 102525, "Migrated NHD provenance count mismatch")
    require(flowlines["workunitid"].astype(str).eq("300290").sum() == 232, "EDH work-unit provenance count mismatch")
    require(flowlines.total_bounds[0] > -90 and flowlines.total_bounds[2] < -75, "Extreme longitude")
    require(flowlines.total_bounds[1] > 35 and flowlines.total_bounds[3] < 50, "Extreme latitude")
    network = flowlines.loc[flowlines["hydrosequence"].notna()].copy()
    require(network["hydrosequence"].is_unique, "Duplicate hydrosequence")
    require(not network["hydrosequence"].eq(network["dnhydrosequence"]).any(), "Native topology self-loop")

    reconciliation = pd.read_csv(RECONCILIATION, dtype={"from_huc12": str, "to_huc12": str})
    baseline = gpd.read_file(GPKG, layer="water_huc12_routing_inferred")
    require(len(reconciliation) == len(baseline) == 251, "Connector reconciliation is not one-to-one")
    require(reconciliation["old_connector_id"].is_unique, "Duplicate connector QA row")
    require(set(reconciliation["old_connector_id"]) == set(baseline["feature_id"]), "Connector IDs differ from v0.1")
    require(set(reconciliation["qa_status"]) <= ALLOWED_STATUS, "Unknown reconciliation status")
    require(not reconciliation["from_huc12"].eq(reconciliation["to_huc12"]).any(), "Connector self-loop")
    require(reconciliation["qa_status"].notna().all(), "Unclassified connector")
    unresolved = reconciliation.loc[reconciliation["qa_status"].eq("UNRESOLVED")]
    require(unresolved["source_method"].eq("project_inference").all(), "Unresolved source method must remain project inference")
    require(unresolved["physical_geometry"].astype(str).str.lower().eq("false").all(), "Unresolved edges must not claim physical geometry")
    require(unresolved["unresolved_category"].notna().all(), "Unresolved category missing")
    require(unresolved["explanation"].str.len().gt(40).all(), "Unresolved explanation missing")

    transitions = pd.read_csv(TRANSITIONS, dtype={"from_huc12": str, "to_huc12": str})
    require(transitions["transition_id"].is_unique, "Duplicate transition ID")
    require(not transitions["from_huc12"].eq(transitions["to_huc12"]).any(), "Cross-HUC table contains same-HUC edge")
    require(set(transitions["transition_class"]) == {"physical_hydrography", "authoritative_network_connector"}, "Transition classes incomplete")
    require(transitions["up_hydrosequence"].notna().all(), "Missing upstream topology ID")
    require(transitions["down_hydrosequence"].notna().all(), "Missing downstream topology ID")

    routing = pd.read_csv(ROUTING, dtype={"huc12": str, "downstream_huc12": str})
    huc12 = gpd.read_file(GPKG, layer="water_subwatersheds_huc12")
    require(len(routing) == len(huc12) == 252, "HUC routing table must cover all HUC-12s")
    require(routing["huc12"].is_unique, "Duplicate HUC routing row")
    require(set(routing["huc12"]) == set(huc12["huc12"]), "HUC routing IDs mismatch")

    if TRANSITION_MANIFEST.exists():
        physical = gpd.read_file(GPKG, layer="hydrography_physical")
        official = gpd.read_file(GPKG, layer="hydrography_network_connectors")
        inferred = gpd.read_file(GPKG, layer="routing_inferred_unresolved")
        require(len(physical) == 86410, "Integrated physical layer count mismatch")
        require(len(official) == 16347, "Integrated official connector count mismatch")
        require(len(inferred) == len(unresolved), "Integrated unresolved layer count mismatch")
        require(physical["physical_geometry"].astype(bool).all(), "Physical layer semantic flag failed")
        require(not official["physical_geometry"].astype(bool).any(), "Official connectors claim physical geometry")
        require(not inferred["physical_geometry"].astype(bool).any(), "Inferred routing claims physical geometry")
        require(set(official["physicality"]) == {"authoritative_network_connector"}, "Official connector physicality mismatch")
        require(inferred["source_method"].eq("project_inference").all(), "Integrated inferred source method mismatch")

    checks = summary["checks"]
    require(checks["storage_crs"] == "EPSG:4326", "Storage CRS validation failed")
    require(checks["analysis_crs"] == "EPSG:26917", "Analysis CRS validation failed")
    require(checks["invalid_geometry_count"] == 0, "Geometry validation failed")
    require(checks["self_loop_count"] == 0, "Topology self-loop validation failed")
    require(checks["maumee_to_terminal_continuity_pass"] is True, "Maumee terminal continuity failed")
    require(checks["linked_geometry_gap_over_1m_count"] == 0, "Native linked geometry gap exceeds 1 m")
    require(checks["pathlength_downstream_reversal_count"] == 0, "Downstream pathlength reversal")
    require(checks["maumee_terminal_intersects_lake_erie"] is True, "Maumee terminal does not intersect Lake Erie")
    require(all(value["pass"] for value in checks["major_tributary_terminal_traces"].values()), "Major tributary terminal trace failed")
    require(sum(summary["reconciliation_status_counts"].values()) == 251, "Status count total mismatch")

    unresolved_table = pd.read_csv(UNRESOLVED, dtype={"from_huc12": str, "to_huc12": str})
    require(len(unresolved_table) == len(unresolved), "Unresolved detail table count mismatch")
    require(set(unresolved_table["old_connector_id"]) == set(unresolved["old_connector_id"]), "Unresolved detail IDs mismatch")
    for svg_name in ["hydrography_baseline_vs_authoritative.svg", "huc12_routing_reconciliation.svg"]:
        svg_text = (ROOT / "outputs" / "qa" / svg_name).read_text(encoding="utf-8")
        require("not mapped waterway" in svg_text, f"Required analytical-edge label missing from {svg_name}")

    print("PASS: physical hydrography review package is internally consistent")
    print(f"PASS: historical v0.1 GeoPackage SHA-256 {EXPECTED_GPKG_SHA256} preserved in the release record")
    print(f"PASS: {len(flowlines):,} unique valid 3DHP flowlines in EPSG:4326")
    print(f"PASS: {len(reconciliation)} released connectors each have one QA outcome; {len(unresolved)} remain explicit abstract edges")
    print(f"PASS: {len(transitions):,} native cross-HUC transitions; no self-loops")
    print("PASS: Maumee named-flowline traces reach native terminals")


if __name__ == "__main__":
    main()
