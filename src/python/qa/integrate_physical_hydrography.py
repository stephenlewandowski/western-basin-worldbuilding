"""Integrate the accepted 3DHP architecture into current development data.

This post-v0.1 integration preserves all legacy layers and the release tag. It
adds three semantically separate layers and a precedence-aware HUC routing
table after the B — ACCEPT WITH QUALIFICATION human decision.
"""

from __future__ import annotations

import gzip
import json
import shutil
import sqlite3
import subprocess
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import force_2d

from build_physical_hydrography_review import (
    CANONICAL_GPKG,
    MAP_CRS,
    RAW_FLOWLINES,
    ROOT,
    SUMMARY_JSON,
    assign_huc12,
    prepare_flowlines,
    sha256,
)


HISTORICAL_SHA256 = "555D23D076638E69942C9BB5D6B1043D00A152A945788BDB7C988EE72C576882"
RECONCILIATION = ROOT / "reports" / "wbd_connector_reconciliation.csv"
ROUTING_TABLE = ROOT / "data" / "processed" / "networks" / "huc12_routing_current.csv"
TRANSITION_MANIFEST = ROOT / "reports" / "development_gpkg_transition_manifest.json"
SOURCE_MANIFEST = ROOT / "reports" / "physical_hydrography_source_manifest.json"
TMP = ROOT / "tmp" / "physical_hydrography_integration"


def load_raw() -> gpd.GeoDataFrame:
    with gzip.open(RAW_FLOWLINES, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    frame = gpd.GeoDataFrame.from_features(payload["features"], crs="EPSG:4326")
    frame.attrs["retrieved_date"] = payload.get("retrieved_date")
    return prepare_flowlines(frame)


def accepted_layers(
    frame: gpd.GeoDataFrame, huc12: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    frame = frame.copy()
    frame["huc12"], _ = assign_huc12(frame, huc12)
    frame["source_authority"] = "USGS 3D Hydrography Program"
    common = [
        "objectid",
        "id3dhp",
        "featuredate",
        "mainstemid",
        "gnisidlabel",
        "featuretype",
        "featuretypelabel",
        "lengthkm",
        "flowdirection",
        "onsurface",
        "catchmentid3dhp",
        "flowpathid3dhp",
        "streamorder",
        "hydrosequence",
        "dnhydrosequence",
        "uphydrosequence",
        "divergence",
        "workunitid",
        "physicality",
        "source_generation",
        "huc12",
        "source_authority",
        "geometry",
    ]
    physical = frame.loc[
        frame["physicality"].isin(["physical_channel", "canal", "drainageway"]),
        common,
    ].copy()
    physical["routing_basis"] = "physical_3dhp"
    physical["physical_geometry"] = True
    physical.geometry = physical.geometry.map(force_2d)
    connectors = frame.loc[
        frame["physicality"].eq("authoritative_network_connector"), common
    ].copy()
    connectors["routing_basis"] = "official_3dhp_connector"
    connectors["physical_geometry"] = False
    connectors.geometry = connectors.geometry.map(force_2d)
    return physical, connectors


def unresolved_layer(
    legacy: gpd.GeoDataFrame, reconciliation: pd.DataFrame
) -> gpd.GeoDataFrame:
    unresolved = reconciliation.loc[reconciliation["qa_status"].eq("UNRESOLVED")].copy()
    layer = legacy.merge(
        unresolved,
        left_on="feature_id",
        right_on="old_connector_id",
        how="inner",
        suffixes=("", "_qa"),
    )
    layer["routing_basis"] = "project_inference"
    layer["physical_geometry"] = False
    layer["source_authority"] = "project / USGS WBD tohuc"
    layer["source_generation"] = "project_derived"
    layer["confidence"] = "low"
    layer["qa_status"] = "UNRESOLVED"
    layer["source_method"] = "project_inference"
    keep = [
        "feature_id",
        "from_huc12",
        "to_huc12",
        "feature_name",
        "routing_basis",
        "physical_geometry",
        "source_authority",
        "source_generation",
        "confidence",
        "qa_status",
        "source_method",
        "unresolved_category",
        "observed_3dhp_downstream_huc12",
        "explanation",
        "geometry",
    ]
    return layer[keep].copy()


def write_routing_table(reconciliation: pd.DataFrame) -> None:
    routing = reconciliation[
        [
            "old_connector_id",
            "from_huc12",
            "to_huc12",
            "routing_basis",
            "physical_geometry",
            "source_authority",
            "source_generation",
            "confidence",
            "qa_status",
            "replacement_ids",
            "replacement_feature_types",
            "unresolved_category",
            "observed_3dhp_downstream_huc12",
            "explanation",
        ]
    ].copy()
    routing = routing.rename(columns={"old_connector_id": "routing_id"})
    routing.insert(3, "routing_precedence", routing["routing_basis"].map({
        "physical_3dhp": 1,
        "physical_nhdplus_hr_existing": 1,
        "official_3dhp_connector": 2,
        "project_inference": 3,
    }))
    routing.to_csv(ROUTING_TABLE, index=False)


def main() -> None:
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    if summary.get("recommendation") != "B — ACCEPT WITH QUALIFICATION":
        raise AssertionError("QA package does not support qualified acceptance")
    before_hash = sha256(CANONICAL_GPKG)
    if before_hash != HISTORICAL_SHA256:
        raise AssertionError(
            "Current development GeoPackage is not the verified historical starting artifact"
        )

    reconciliation = pd.read_csv(
        RECONCILIATION, dtype={"from_huc12": str, "to_huc12": str}
    )
    if len(reconciliation) != 251:
        raise AssertionError("Connector reconciliation must contain 251 rows")
    huc12 = gpd.read_file(CANONICAL_GPKG, layer="water_subwatersheds_huc12")
    legacy = gpd.read_file(CANONICAL_GPKG, layer="water_huc12_routing_inferred")
    physical, official_connectors = accepted_layers(load_raw(), huc12)
    unresolved = unresolved_layer(legacy, reconciliation)
    if len(physical) != 86410 or len(official_connectors) != 16347 or len(unresolved) != 12:
        raise AssertionError("Accepted layer count differs from verified QA result")

    TMP.mkdir(parents=True, exist_ok=True)
    candidate = TMP / "glasspunk_base.integrating.gpkg"
    if candidate.exists():
        candidate.unlink()
    shutil.copy2(CANONICAL_GPKG, candidate)
    physical.to_file(candidate, layer="hydrography_physical", driver="GPKG", mode="a")
    official_connectors.to_file(
        candidate, layer="hydrography_network_connectors", driver="GPKG", mode="a"
    )
    unresolved.to_file(
        candidate, layer="routing_inferred_unresolved", driver="GPKG", mode="a"
    )
    with sqlite3.connect(candidate) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise AssertionError(f"Integrated GeoPackage integrity failed: {integrity}")
    shutil.copy2(candidate, CANONICAL_GPKG)
    after_hash = sha256(CANONICAL_GPKG)
    write_routing_table(reconciliation)

    try:
        release_commit = subprocess.check_output(
            ["git", "rev-list", "-n", "1", "v0.1-water-system"],
            cwd=ROOT,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        release_commit = "unavailable"
    manifest = {
        "integration_date": date.today().isoformat(),
        "human_decision": "B — ACCEPT WITH QUALIFICATION",
        "historical_release_tag": "v0.1-water-system",
        "historical_release_commit": release_commit,
        "historical_v0_1_gpkg_sha256": before_hash,
        "current_development_gpkg_sha256": after_hash,
        "legacy_layers_preserved": True,
        "accepted_layers": {
            "hydrography_physical": len(physical),
            "hydrography_network_connectors": len(official_connectors),
            "routing_inferred_unresolved": len(unresolved),
        },
        "current_routing_table": str(ROUTING_TABLE.relative_to(ROOT)).replace("\\", "/"),
        "released_maps_modified": False,
        "development_geometry_dimensions": "2D",
        "raw_snapshot_z_preserved": True,
        "integrity_check": integrity,
    }
    TRANSITION_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary.update(
        {
            "review_status": "accepted_with_qualification",
            "canonical_status": "accepted_current_development",
            "human_decision": "B — ACCEPT WITH QUALIFICATION",
            "historical_v0_1_gpkg_sha256": before_hash,
            "current_development_gpkg_sha256": after_hash,
            "canonical_gpkg_sha256": after_hash,
            "canonical_modified": True,
            "historical_release_modified": False,
            "integrated_layers": manifest["accepted_layers"],
        }
    )
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    source_manifest["historical_v0_1_gpkg_sha256"] = source_manifest.pop(
        "canonical_gpkg_sha256",
        source_manifest.get("historical_v0_1_gpkg_sha256", before_hash),
    )
    source_manifest["current_development_gpkg_sha256"] = after_hash
    source_manifest["human_decision"] = "B — ACCEPT WITH QUALIFICATION"
    SOURCE_MANIFEST.write_text(json.dumps(source_manifest, indent=2), encoding="utf-8")
    print(f"Integrated {len(physical):,} physical 3DHP features")
    print(f"Integrated {len(official_connectors):,} official connector features")
    print(f"Retained {len(unresolved)} project-inferred abstract routing edges")
    print(f"Historical v0.1 GeoPackage SHA-256: {before_hash}")
    print(f"Current development GeoPackage SHA-256: {after_hash}")


if __name__ == "__main__":
    main()
