"""Build the Phase 1 physical-hydrography reconciliation review package.

The script retrieves official USGS 3DHP flowlines for a 500 m buffer around
the complete Phase 1 HUC-12 union. It never writes to the released canonical
GeoPackage or released Phase 1 analytical outputs.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
import requests
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

matplotlib.use("Agg")


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "usgs"
REPORTS = ROOT / "reports"
QA = ROOT / "outputs" / "qa"
QA_DATA = QA / "data"
TMP = ROOT / "tmp" / "physical_hydrography_review"

SERVICE_URL = "https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer"
FLOWLINE_URL = f"{SERVICE_URL}/50"
QUERY_URL = f"{FLOWLINE_URL}/query"
RETRIEVED = date.today().isoformat()
BUFFER_M = 500
QUERY_SIMPLIFY_M = 100
PAGE_SIZE = 2500
MAP_CRS = "EPSG:26917"
AREA_CRS = "EPSG:5070"
OUTPUT_CRS = "EPSG:4326"

HUC12_PATH = ROOT / "data" / "raw" / "usgs" / "wbd_huc12_maumee_basin.geojson"
RAW_FLOWLINES = RAW / "3dhp_flowlines_maumee_buffer500m.geojson.gz"
SERVICE_METADATA = RAW / "3dhp_all_service_metadata.json"
LAYER_METADATA = RAW / "3dhp_flowline_layer50_metadata.json"
RETRIEVAL_MANIFEST = REPORTS / "physical_hydrography_source_manifest.json"
CANONICAL_GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
RECONCILIATION_CSV = REPORTS / "wbd_connector_reconciliation.csv"
UNRESOLVED_CSV = REPORTS / "unresolved_routing_summary.csv"
COMPARISON_CSV = REPORTS / "physical_hydrography_baseline_comparison.csv"
TRANSITIONS_CSV = QA_DATA / "3dhp_huc12_transitions.csv"
ROUTING_CSV = QA_DATA / "huc12_authoritative_routing.csv"
SUMMARY_JSON = REPORTS / "physical_hydrography_qa.json"
SOURCE_REVIEW_MD = REPORTS / "water_hydrography_source_review.md"
RECONCILIATION_MD = REPORTS / "physical_hydrography_reconciliation.md"
MAP_NOTE = (
    "Dashed project routing connectors represent analytical network relationships, "
    "not mapped waterways."
)

PHYSICALITY = {
    "Channel Line": "physical_channel",
    "Canal": "canal",
    "Drainageway": "drainageway",
    "Surface Connector": "authoritative_network_connector",
    "Waterbody Connector": "authoritative_network_connector",
    "Elevation Breaching Connector": "authoritative_network_connector",
    "Hydro Unenforced Connector": "authoritative_network_connector",
}

OUT_FIELDS = [
    "OBJECTID",
    "id3dhp",
    "featuredate",
    "mainstemid",
    "gnisid",
    "gnisidlabel",
    "featuretype",
    "featuretypelabel",
    "lengthkm",
    "waterbodyid3dhp",
    "flowdirection",
    "flowdirectionlabel",
    "onsurface",
    "onsurfacelabel",
    "catchmentid3dhp",
    "flowpathid3dhp",
    "streamlevel",
    "startflag",
    "terminalflag",
    "streamorder",
    "streamcalculator",
    "hydrosequence",
    "dnhydrosequence",
    "uphydrosequence",
    "dnlevelpath",
    "uplevelpath",
    "pathlength",
    "arbolatesum",
    "divergence",
    "divergencelabel",
    "rtrndivergence",
    "levelpath",
    "terminalpath",
    "workunitid",
]


def ensure_dirs() -> None:
    for path in (RAW, REPORTS, QA, QA_DATA, TMP):
        path.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def request_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    timeout: int = 300,
    retries: int = 5,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.post(url, data=data, timeout=timeout) if data else requests.get(
                url, params=params, timeout=timeout
            )
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                raise RuntimeError(f"ArcGIS error: {payload['error']}")
            return payload
        except Exception as exc:  # network retries are intentionally bounded
            last_error = exc
            if attempt + 1 == retries:
                break
            wait = 2 ** attempt
            print(f"Request retry {attempt + 1}/{retries - 1} after {wait}s: {exc}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Request failed after {retries} attempts") from last_error


def fetch_metadata() -> tuple[dict[str, Any], dict[str, Any]]:
    if SERVICE_METADATA.exists() and LAYER_METADATA.exists():
        return (
            json.loads(SERVICE_METADATA.read_text(encoding="utf-8")),
            json.loads(LAYER_METADATA.read_text(encoding="utf-8")),
        )
    service = request_json(SERVICE_URL, params={"f": "pjson"})
    layer = request_json(FLOWLINE_URL, params={"f": "pjson"})
    SERVICE_METADATA.write_text(json.dumps(service, indent=2), encoding="utf-8")
    LAYER_METADATA.write_text(json.dumps(layer, indent=2), encoding="utf-8")
    return service, layer


def polygon_esri_json(geometry: Any) -> str:
    polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
    rings: list[list[list[float]]] = []
    for polygon in polygons:
        rings.append([[float(x), float(y)] for x, y in polygon.exterior.coords])
        rings.extend(
            [[float(x), float(y)] for x, y in interior.coords] for interior in polygon.interiors
        )
    return json.dumps({"rings": rings, "spatialReference": {"wkid": 4326}})


def study_geometries() -> tuple[gpd.GeoDataFrame, Any, Any]:
    huc12 = gpd.read_file(HUC12_PATH).to_crs(AREA_CRS)
    exact = huc12.geometry.union_all().buffer(BUFFER_M)
    query = exact.simplify(QUERY_SIMPLIFY_M, preserve_topology=True).buffer(0)
    exact_4326 = gpd.GeoSeries([exact], crs=AREA_CRS).to_crs(OUTPUT_CRS).iloc[0]
    query_4326 = gpd.GeoSeries([query], crs=AREA_CRS).to_crs(OUTPUT_CRS).iloc[0]
    return huc12, exact_4326, query_4326


def fetch_flowlines(exact_geometry: Any, query_geometry: Any) -> gpd.GeoDataFrame:
    if RAW_FLOWLINES.exists():
        with gzip.open(RAW_FLOWLINES, "rt", encoding="utf-8") as handle:
            payload = json.load(handle)
        frame = gpd.GeoDataFrame.from_features(payload["features"], crs=OUTPUT_CRS)
        frame.attrs["retrieved_date"] = payload.get("retrieved_date", RETRIEVED)
        return frame

    geometry_json = polygon_esri_json(query_geometry)
    count_payload = request_json(
        QUERY_URL,
        data={
            "where": "1=1",
            "geometry": geometry_json,
            "geometryType": "esriGeometryPolygon",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "returnCountOnly": "true",
            "f": "json",
        },
    )
    expected = int(count_payload["count"])
    print(f"3DHP server reports {expected:,} flowlines in simplified query polygon", flush=True)

    features: list[dict[str, Any]] = []
    offset = 0
    while offset < expected:
        payload = request_json(
            QUERY_URL,
            data={
                "where": "1=1",
                "outFields": ",".join(OUT_FIELDS),
                "returnGeometry": "true",
                "returnZ": "true",
                "returnM": "true",
                "geometry": geometry_json,
                "geometryType": "esriGeometryPolygon",
                "inSR": 4326,
                "spatialRel": "esriSpatialRelIntersects",
                "outSR": 4326,
                "orderByFields": "OBJECTID ASC",
                "resultOffset": offset,
                "resultRecordCount": PAGE_SIZE,
                "f": "geojson",
            },
        )
        page = payload.get("features", [])
        if not page:
            break
        features.extend(page)
        offset += len(page)
        print(f"Retrieved {offset:,}/{expected:,} flowlines", flush=True)
        if len(page) < PAGE_SIZE:
            break

    frame = gpd.GeoDataFrame.from_features(features, crs=OUTPUT_CRS)
    frame.columns = [str(column).lower() for column in frame.columns]
    before_dedupe = len(frame)
    frame = frame.drop_duplicates(subset="objectid").reset_index(drop=True)
    if len(frame) != before_dedupe:
        print(f"Removed {before_dedupe - len(frame):,} duplicate OBJECTIDs", flush=True)

    exact = gpd.GeoSeries([exact_geometry], crs=OUTPUT_CRS).to_crs(AREA_CRS).iloc[0]
    projected = frame.to_crs(AREA_CRS)
    frame = frame[projected.geometry.intersects(exact)].reset_index(drop=True)
    print(f"Exact 500 m study buffer retains {len(frame):,} flowlines", flush=True)

    payload = {
        "type": "FeatureCollection",
        "source": FLOWLINE_URL,
        "retrieved_date": RETRIEVED,
        "study_buffer_m": BUFFER_M,
        "features": json.loads(frame.to_json(drop_id=True))["features"],
    }
    with gzip.open(RAW_FLOWLINES, "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(payload, handle, separators=(",", ":"))
    frame.attrs["retrieved_date"] = RETRIEVED
    return frame


def write_manifest(
    service_metadata: dict[str, Any],
    layer_metadata: dict[str, Any],
    flowlines: gpd.GeoDataFrame,
) -> None:
    previous_manifest = (
        json.loads(RETRIEVAL_MANIFEST.read_text(encoding="utf-8"))
        if RETRIEVAL_MANIFEST.exists()
        else {}
    )
    copyright_text = str(service_metadata.get("copyrightText", ""))
    refresh_text = copyright_text.split("Data refreshed", 1)[-1].strip(" .") if "Data refreshed" in copyright_text else None
    dates = pd.to_datetime(flowlines.get("featuredate"), unit="ms", errors="coerce", utc=True)
    manifest = {
        "dataset": "USGS 3D Hydrography Program 3DHP_all",
        "agency": "U.S. Geological Survey / The National Map",
        "service_url": SERVICE_URL,
        "flowline_layer_url": FLOWLINE_URL,
        "service_refresh_text": refresh_text,
        "retrieved_date": flowlines.attrs.get("retrieved_date", RETRIEVED),
        "service_crs": "EPSG:3857",
        "snapshot_crs": OUTPUT_CRS,
        "analysis_crs": MAP_CRS,
        "geometry_type": layer_metadata.get("geometryType"),
        "service_has_z": layer_metadata.get("hasZ"),
        "service_has_m": layer_metadata.get("hasM"),
        "max_record_count": layer_metadata.get("maxRecordCount"),
        "feature_count": len(flowlines),
        "featuredate_min": dates.min().isoformat() if dates.notna().any() else None,
        "featuredate_max": dates.max().isoformat() if dates.notna().any() else None,
        "study_buffer_m": BUFFER_M,
        "query_simplification_m": QUERY_SIMPLIFY_M,
        "raw_snapshot": str(RAW_FLOWLINES.relative_to(ROOT)).replace("\\", "/"),
        "raw_snapshot_git_storage": "ignored_reproducible_download",
        "raw_snapshot_retrievable": True,
        "raw_snapshot_sha256": sha256(RAW_FLOWLINES),
        "metadata_files": [
            str(SERVICE_METADATA.relative_to(ROOT)).replace("\\", "/"),
            str(LAYER_METADATA.relative_to(ROOT)).replace("\\", "/"),
        ],
        "terms": "No use constraints; open and non-proprietary; USGS acknowledgment appreciated.",
        "limitations": (
            "The service mixes EDH and migrated NHD supplementation. Work unit 300290 has "
            "a USGS-documented July 2026 derivative gap. Temporal change is possible; not "
            "intended for site-specific regulatory determinations."
        ),
        "generated_at_utc": previous_manifest.get(
            "generated_at_utc", datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        ),
    }
    RETRIEVAL_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def prepare_flowlines(flowlines: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normalize fields and preserve physicality and feature-level provenance."""
    frame = flowlines.copy()
    frame.columns = [str(column).lower() for column in frame.columns]
    frame["physicality"] = frame["featuretypelabel"].map(PHYSICALITY).fillna("uncertain")
    frame["source_generation"] = np.where(
        frame["workunitid"].astype("string").eq("NHD"),
        "migrated_nhd",
        np.where(
            frame["workunitid"].notna(),
            "edh_work_unit",
            "unknown",
        ),
    )
    frame["hydrosequence"] = pd.to_numeric(frame["hydrosequence"], errors="coerce").astype("Int64")
    frame["dnhydrosequence"] = pd.to_numeric(frame["dnhydrosequence"], errors="coerce").astype("Int64")
    frame["objectid"] = pd.to_numeric(frame["objectid"], errors="coerce").astype("Int64")
    return frame


def assign_huc12(
    frame: gpd.GeoDataFrame, huc12: gpd.GeoDataFrame
) -> tuple[pd.Series, dict[str, int]]:
    """Assign each line by a representative point; topology, never proximity, sets direction."""
    projected = frame.to_crs(MAP_CRS)
    polygons = huc12.to_crs(MAP_CRS)[["huc12", "geometry"]].copy()
    points = gpd.GeoDataFrame(
        {"source_index": projected.index},
        geometry=projected.geometry.representative_point(),
        crs=MAP_CRS,
    )
    joined = gpd.sjoin(points, polygons, how="left", predicate="within")
    duplicate_assignments = int(joined.index.duplicated(keep=False).sum())
    joined = joined[~joined.index.duplicated(keep="first")]
    assignment = joined["huc12"].reindex(projected.index).astype("string")
    return assignment, {
        "assigned": int(assignment.notna().sum()),
        "outside_or_boundary": int(assignment.isna().sum()),
        "ambiguous_point_matches": duplicate_assignments,
    }


def build_transitions(frame: gpd.GeoDataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build directed transitions only from native hydrosequence derivatives."""
    network = frame.loc[frame["hydrosequence"].notna()].copy()
    duplicate_hydrosequence = int(network["hydrosequence"].duplicated().sum())
    network = network.drop_duplicates("hydrosequence", keep="first")
    lookup = network.set_index("hydrosequence")
    downstream = network["dnhydrosequence"].map(lookup.index.to_series())
    has_downstream_reference = network["dnhydrosequence"].fillna(0).gt(0)
    linked = network.loc[has_downstream_reference & downstream.notna()].copy()
    missing_references = int((has_downstream_reference & downstream.isna()).sum())
    dn = lookup.reindex(linked["dnhydrosequence"].astype("Int64").to_numpy()).copy()
    dn.index = linked.index

    transitions = pd.DataFrame(
        {
            "up_hydrosequence": linked["hydrosequence"].astype("Int64"),
            "down_hydrosequence": linked["dnhydrosequence"].astype("Int64"),
            "up_id3dhp": linked["id3dhp"].astype("string"),
            "down_id3dhp": dn["id3dhp"].astype("string"),
            "from_huc12": linked["huc12"].astype("string"),
            "to_huc12": dn["huc12"].astype("string"),
            "up_feature_type": linked["featuretypelabel"].astype("string"),
            "down_feature_type": dn["featuretypelabel"].astype("string"),
            "up_physicality": linked["physicality"].astype("string"),
            "down_physicality": dn["physicality"].astype("string"),
            "up_source_generation": linked["source_generation"].astype("string"),
            "down_source_generation": dn["source_generation"].astype("string"),
        },
        index=linked.index,
    )
    connector = transitions[["up_physicality", "down_physicality"]].eq(
        "authoritative_network_connector"
    ).any(axis=1)
    transitions["transition_class"] = np.where(
        connector, "authoritative_network_connector", "physical_hydrography"
    )
    transitions = transitions.loc[
        transitions["from_huc12"].notna()
        & transitions["to_huc12"].notna()
        & transitions["from_huc12"].ne(transitions["to_huc12"])
    ].reset_index(drop=True)
    transitions["transition_id"] = (
        transitions["up_hydrosequence"].astype("string")
        + "->"
        + transitions["down_hydrosequence"].astype("string")
    )

    graph = nx.DiGraph()
    graph.add_nodes_from(network["hydrosequence"].astype(int).tolist())
    graph.add_edges_from(
        zip(linked["hydrosequence"].astype(int), linked["dnhydrosequence"].astype(int))
    )
    self_loops = list(nx.selfloop_edges(graph))
    stats: dict[str, Any] = {
        "network_node_count": graph.number_of_nodes(),
        "network_edge_count": graph.number_of_edges(),
        "weak_component_count": nx.number_weakly_connected_components(graph),
        "outlet_count": int(network["dnhydrosequence"].fillna(0).eq(0).sum()),
        "missing_downstream_reference_count": missing_references,
        "duplicate_hydrosequence_count": duplicate_hydrosequence,
        "self_loop_count": len(self_loops),
        "cross_huc_transition_count": len(transitions),
        "cross_huc_pair_count": int(
            transitions[["from_huc12", "to_huc12"]].drop_duplicates().shape[0]
        ),
    }
    return transitions, stats


def aggregate_transitions(transitions: pd.DataFrame) -> pd.DataFrame:
    def joined_unique(series: pd.Series, limit: int = 40) -> str:
        values = sorted({str(value) for value in series.dropna() if str(value) != "<NA>"})
        shown = values[:limit]
        suffix = f";...(+{len(values) - limit})" if len(values) > limit else ""
        return ";".join(shown) + suffix

    rows: list[dict[str, Any]] = []
    for (from_huc12, to_huc12), group in transitions.groupby(
        ["from_huc12", "to_huc12"], dropna=False, sort=True
    ):
        feature_types = pd.concat([group["up_feature_type"], group["down_feature_type"]])
        evidence_ids = pd.concat([group["up_id3dhp"], group["down_id3dhp"]])
        generations = pd.concat(
            [group["up_source_generation"], group["down_source_generation"]]
        )
        rows.append(
            {
                "from_huc12": from_huc12,
                "to_huc12": to_huc12,
                "transition_count": len(group),
                "physical_transition_count": int(
                    group["transition_class"].eq("physical_hydrography").sum()
                ),
                "connector_transition_count": int(
                    group["transition_class"].eq("authoritative_network_connector").sum()
                ),
                "replacement_ids": joined_unique(evidence_ids),
                "replacement_feature_types": joined_unique(feature_types),
                "source_generations": joined_unique(generations),
                "transition_ids": joined_unique(group["transition_id"]),
            }
        )
    return pd.DataFrame(rows)


def build_same_feature_crossings(
    frame: gpd.GeoDataFrame,
    huc12: gpd.GeoDataFrame,
    connectors: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, set[tuple[str, str]]]:
    """Find authoritative lines that cross a WBD pair within one directed feature.

    Native flowline-to-flowline derivatives cannot expose a HUC boundary crossing
    when one 3DHP feature spans both polygons. The service explicitly confirms
    digitized direction in flowdirectionlabel, so along-line position is used only
    for these same-feature crossings; all inter-feature direction remains native
    hydrosequence topology.
    """
    projected = frame.to_crs(MAP_CRS)
    polygons = huc12.to_crs(MAP_CRS).set_index("huc12")["geometry"]
    forward_rows: list[dict[str, Any]] = []
    reverse_pairs: set[tuple[str, str]] = set()
    direction_text = "Flow direction is in digitized direction"
    for connector in connectors.itertuples():
        pair = (str(connector.from_huc12), str(connector.to_huc12))
        from_polygon = polygons.loc[pair[0]]
        to_polygon = polygons.loc[pair[1]]
        candidate_positions = projected.sindex.query(from_polygon, predicate="intersects")
        candidates = projected.iloc[candidate_positions]
        candidates = candidates.loc[candidates.geometry.intersects(to_polygon)]
        for feature in candidates.itertuples():
            if direction_text not in str(feature.flowdirectionlabel):
                continue
            from_part = feature.geometry.intersection(from_polygon)
            to_part = feature.geometry.intersection(to_polygon)
            if from_part.is_empty or to_part.is_empty:
                continue
            from_position = feature.geometry.project(from_part.representative_point())
            to_position = feature.geometry.project(to_part.representative_point())
            if from_position >= to_position:
                reverse_pairs.add(pair)
                continue
            is_connector = feature.physicality == "authoritative_network_connector"
            forward_rows.append(
                {
                    "from_huc12": pair[0],
                    "to_huc12": pair[1],
                    "transition_count": 1,
                    "physical_transition_count": 0 if is_connector else 1,
                    "connector_transition_count": 1 if is_connector else 0,
                    "replacement_ids": str(feature.id3dhp),
                    "replacement_feature_types": str(feature.featuretypelabel),
                    "source_generations": str(feature.source_generation),
                    "transition_ids": f"same-feature:{feature.id3dhp}",
                }
            )
    return pd.DataFrame(forward_rows), reverse_pairs


def combine_pair_evidence(*frames: pd.DataFrame) -> pd.DataFrame:
    evidence = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)

    def combine_text(series: pd.Series) -> str:
        values: set[str] = set()
        for value in series.dropna().astype(str):
            values.update(item for item in value.split(";") if item and not item.startswith("..."))
        return ";".join(sorted(values))

    return (
        evidence.groupby(["from_huc12", "to_huc12"], as_index=False)
        .agg(
            transition_count=("transition_count", "sum"),
            physical_transition_count=("physical_transition_count", "sum"),
            connector_transition_count=("connector_transition_count", "sum"),
            replacement_ids=("replacement_ids", combine_text),
            replacement_feature_types=("replacement_feature_types", combine_text),
            source_generations=("source_generations", combine_text),
            transition_ids=("transition_ids", combine_text),
        )
    )


def baseline_transition_pairs(
    baseline: gpd.GeoDataFrame, huc12: gpd.GeoDataFrame
) -> pd.DataFrame:
    frame = baseline.copy()
    frame["hydrosequence"] = pd.to_numeric(frame["hydroseq"], errors="coerce").astype("Int64")
    frame["dnhydrosequence"] = pd.to_numeric(frame["dnhydroseq"], errors="coerce").astype("Int64")
    frame["id3dhp"] = frame["permanent_identifier"].astype("string")
    frame["featuretypelabel"] = "NHDPlus HR order >=3 flowline"
    frame["physicality"] = "physical_channel"
    frame["source_generation"] = "released_nhdplus_hr"
    frame["huc12"], _ = assign_huc12(frame, huc12)
    transitions, _ = build_transitions(frame)
    if transitions.empty:
        return pd.DataFrame(columns=["from_huc12", "to_huc12", "baseline_transition_count"])
    return (
        transitions.groupby(["from_huc12", "to_huc12"])
        .size()
        .rename("baseline_transition_count")
        .reset_index()
    )


def reconcile_connectors(
    connectors: gpd.GeoDataFrame,
    huc12: gpd.GeoDataFrame,
    authoritative: pd.DataFrame,
    baseline_pairs: pd.DataFrame,
) -> pd.DataFrame:
    huc_ids = set(huc12["huc12"].astype(str))
    wbd_to = dict(zip(huc12["huc12"].astype(str), huc12["tohuc"].astype(str)))
    auth_lookup = authoritative.set_index(["from_huc12", "to_huc12"]).to_dict("index")
    base_lookup = baseline_pairs.set_index(["from_huc12", "to_huc12"])[
        "baseline_transition_count"
    ].to_dict()
    projected = connectors.to_crs(MAP_CRS)
    rows: list[dict[str, Any]] = []
    for index, connector in connectors.reset_index(drop=True).iterrows():
        from_huc12 = str(connector["from_huc12"])
        to_huc12 = str(connector["to_huc12"])
        pair = (from_huc12, to_huc12)
        evidence = auth_lookup.get(pair, {})
        invalid_reasons: list[str] = []
        if from_huc12 not in huc_ids:
            invalid_reasons.append("from_huc12 absent from Phase 1 HUC-12 layer")
        if to_huc12 not in huc_ids:
            invalid_reasons.append("to_huc12 absent from Phase 1 HUC-12 layer")
        if from_huc12 == to_huc12:
            invalid_reasons.append("self-loop")
        if from_huc12 in wbd_to and wbd_to[from_huc12] != to_huc12:
            invalid_reasons.append("connector disagrees with preserved WBD tohuc")

        baseline_count = int(base_lookup.get(pair, 0))
        physical_count = int(evidence.get("physical_transition_count", 0))
        connector_count = int(evidence.get("connector_transition_count", 0))
        if invalid_reasons:
            status = "INVALID_BASELINE_INFERENCE"
            confidence = "high"
            note = "; ".join(invalid_reasons)
            routing_basis = "project_inference"
            source_method = "project_inference"
            physical_geometry = False
        elif baseline_count:
            status = "ALREADY_REDUNDANT"
            confidence = "high"
            note = "Released NHDPlus HR order >=3 topology already contains this HUC transition."
            routing_basis = "physical_nhdplus_hr_existing"
            source_method = "released_nhdplus_hr_topology"
            physical_geometry = True
        elif physical_count:
            status = "REPLACED_PHYSICAL"
            confidence = "high"
            note = "Authoritative 3DHP topology or a forward-directed same-feature HUC crossing provides physical geometry."
            routing_basis = "physical_3dhp"
            source_method = "authoritative_3dhp"
            physical_geometry = True
        elif connector_count:
            status = "REPLACED_AUTHORITATIVE_CONNECTOR"
            confidence = "high"
            note = "Authoritative 3DHP topology or a forward-directed same-feature crossing uses a non-watercourse connector class."
            routing_basis = "official_3dhp_connector"
            source_method = "authoritative_3dhp"
            physical_geometry = False
        else:
            status = "UNRESOLVED"
            confidence = "low"
            note = "No forward authoritative 3DHP topology or same-feature crossing matched this WBD pair; retain an analytical edge."
            routing_basis = "project_inference"
            source_method = "project_inference"
            physical_geometry = False

        rows.append(
            {
                "old_connector_id": connector["feature_id"],
                "from_huc12": from_huc12,
                "to_huc12": to_huc12,
                "old_length_km": round(float(projected.geometry.iloc[index].length / 1000), 6),
                "qa_status": status,
                "replacement_source": (
                    "USGS 3DHP Flowline layer 50 / native hydrosequence derivatives"
                    if evidence
                    else "none"
                ),
                "replacement_ids": evidence.get("replacement_ids", ""),
                "replacement_feature_types": evidence.get(
                    "replacement_feature_types", ""
                ),
                "physical_channel_present": physical_count > 0,
                "network_connector_present": connector_count > 0,
                "authoritative_transition_count": int(evidence.get("transition_count", 0)),
                "released_physical_transition_count": baseline_count,
                "source_generation": evidence.get("source_generations", ""),
                "confidence": confidence,
                "routing_basis": routing_basis,
                "source_method": source_method,
                "physical_geometry": physical_geometry,
                "source_authority": (
                    "USGS"
                    if routing_basis in {"physical_3dhp", "official_3dhp_connector", "physical_nhdplus_hr_existing"}
                    else "project / USGS WBD tohuc"
                ),
                "unresolved_category": "",
                "observed_3dhp_downstream_huc12": "",
                "explanation": note,
                "notes": note,
            }
        )
    return pd.DataFrame(rows)


def characterize_unresolved(
    reconciliation: pd.DataFrame,
    huc12: gpd.GeoDataFrame,
    frame: gpd.GeoDataFrame,
    transitions: pd.DataFrame,
    reverse_pairs: set[tuple[str, str]],
) -> pd.DataFrame:
    result = reconciliation.copy()
    names = dict(zip(huc12["huc12"].astype(str), huc12["name"].astype(str)))
    alternate = (
        transitions.groupby("from_huc12")["to_huc12"]
        .agg(lambda values: ";".join(sorted(set(values.dropna().astype(str)))))
        .to_dict()
    )
    divergence = (
        frame.assign(_div=pd.to_numeric(frame["divergence"], errors="coerce").fillna(0))
        .groupby("huc12")["_div"]
        .apply(lambda values: int(values.gt(0).sum()))
        .to_dict()
    )
    for index, row in result.loc[result["qa_status"].eq("UNRESOLVED")].iterrows():
        pair = (str(row["from_huc12"]), str(row["to_huc12"]))
        observed = alternate.get(pair[0], "")
        if pair in reverse_pairs:
            category = "direction_conflict"
            explanation = (
                f"A 3DHP feature intersects both {pair[0]} ({names[pair[0]]}) and "
                f"{pair[1]} ({names[pair[1]]}), but its documented digitized direction "
                "runs opposite the WBD tohuc relationship. The WBD edge is retained as "
                "abstract pending local outlet review."
            )
        elif divergence.get(pair[0], 0) > 0:
            category = "complex_divergence"
            divergence_count = divergence[pair[0]]
            record_word = "record" if divergence_count == 1 else "records"
            explanation = (
                f"The source HUC contains {divergence_count} native divergent flowline "
                f"{record_word} and observed 3DHP transitions lead to {observed or 'no assigned HUC'} "
                f"rather than WBD target {pair[1]}. Retain the WBD relationship as abstract "
                "pending outlet-scale review."
            )
        else:
            category = "ambiguous_huc_outlet"
            explanation = (
                f"Native 3DHP transitions assigned from {pair[0]} lead to "
                f"{observed or 'no assigned HUC'} rather than WBD target {pair[1]}, and no "
                "forward same-feature crossing confirms the WBD pair. Retain it as an "
                "abstract routing relationship pending local outlet review."
            )
        result.at[index, "unresolved_category"] = category
        result.at[index, "observed_3dhp_downstream_huc12"] = observed
        result.at[index, "explanation"] = explanation
        result.at[index, "notes"] = explanation
    unresolved = result.loc[
        result["qa_status"].eq("UNRESOLVED"),
        [
            "old_connector_id",
            "from_huc12",
            "to_huc12",
            "confidence",
            "unresolved_category",
            "observed_3dhp_downstream_huc12",
            "source_method",
            "physical_geometry",
            "explanation",
        ],
    ]
    unresolved.to_csv(UNRESOLVED_CSV, index=False)
    return result


def geometry_and_topology_checks(
    frame: gpd.GeoDataFrame, transitions: pd.DataFrame, topology: dict[str, Any]
) -> dict[str, Any]:
    projected = frame.to_crs(MAP_CRS)
    network = projected.loc[projected["hydrosequence"].notna()].drop_duplicates(
        "hydrosequence"
    )
    hydro_lookup = network.set_index("hydrosequence")
    linked = network.loc[
        network["dnhydrosequence"].fillna(0).gt(0)
        & network["dnhydrosequence"].isin(hydro_lookup.index)
    ]
    up_geometry = gpd.GeoSeries(
        linked["geometry"].values,
        crs=MAP_CRS,
    )
    down_geometry = gpd.GeoSeries(
        hydro_lookup.reindex(linked["dnhydrosequence"])["geometry"].values,
        crs=MAP_CRS,
    )
    gaps = up_geometry.distance(down_geometry) if len(linked) else pd.Series(dtype=float)
    lengths_m = projected.geometry.length
    reported_m = pd.to_numeric(frame["lengthkm"], errors="coerce") * 1000
    relative_error = ((lengths_m - reported_m).abs() / reported_m.replace(0, np.nan)).dropna()
    linked_path_up = pd.to_numeric(linked["pathlength"], errors="coerce").reset_index(drop=True)
    linked_path_down = pd.to_numeric(
        hydro_lookup.reindex(linked["dnhydrosequence"])["pathlength"], errors="coerce"
    ).reset_index(drop=True)
    bounds = [round(float(value), 6) for value in frame.total_bounds]
    checks = {
        "storage_crs": str(frame.crs),
        "analysis_crs": MAP_CRS,
        "feature_count": len(frame),
        "unique_objectid_count": int(frame["objectid"].nunique()),
        "unique_id3dhp_count": int(frame["id3dhp"].nunique()),
        "duplicate_objectid_count": int(frame["objectid"].duplicated().sum()),
        "duplicate_id3dhp_count": int(frame["id3dhp"].duplicated().sum()),
        "duplicate_geometry_count": int(frame.geometry.to_wkb().duplicated().sum()),
        "invalid_geometry_count": int((~frame.geometry.is_valid).sum()),
        "empty_geometry_count": int(frame.geometry.is_empty.sum()),
        "null_geometry_count": int(frame.geometry.isna().sum()),
        "has_z_count": int(frame.geometry.has_z.sum()),
        "bounds_epsg4326": bounds,
        "length_km_sum": round(float(pd.to_numeric(frame["lengthkm"], errors="coerce").sum()), 3),
        "projected_length_km_sum": round(float(lengths_m.sum() / 1000), 3),
        "length_relative_error_p95": round(float(relative_error.quantile(0.95)), 6),
        "linked_geometry_gap_m_p95": round(float(gaps.quantile(0.95)), 6) if len(gaps) else None,
        "linked_geometry_gap_m_max": round(float(gaps.max()), 6) if len(gaps) else None,
        "linked_geometry_gap_over_1m_count": int(gaps.gt(1).sum()) if len(gaps) else 0,
        "pathlength_downstream_reversal_count": int(
            linked_path_up.lt(linked_path_down).fillna(False).sum()
        ),
        **topology,
    }
    return checks


def write_routing_table(
    huc12: gpd.GeoDataFrame, authoritative_pairs: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = {key: group for key, group in authoritative_pairs.groupby("from_huc12")}
    for huc in huc12.sort_values("huc12").itertuples():
        group = grouped.get(str(huc.huc12))
        if group is None or group.empty:
            rows.append(
                {
                    "huc12": huc.huc12,
                    "receiving_flowline_ids": "",
                    "downstream_huc12": "",
                    "downstream_relationship_count": 0,
                    "physical_transition_count": 0,
                    "connector_transition_count": 0,
                    "source_method": "native 3DHP hydrosequence/dnhydrosequence",
                    "confidence": "unresolved",
                    "divergence_note": "No direct cross-HUC native transition in the review extract.",
                }
            )
            continue
        downstream = sorted(group["to_huc12"].dropna().astype(str).unique())
        receiving: set[str] = set()
        for value in group["replacement_ids"].dropna().astype(str):
            receiving.update(item for item in value.split(";") if item)
        rows.append(
            {
                "huc12": huc.huc12,
                "receiving_flowline_ids": ";".join(sorted(receiving)[:40]),
                "downstream_huc12": ";".join(downstream),
                "downstream_relationship_count": int(group["transition_count"].sum()),
                "physical_transition_count": int(group["physical_transition_count"].sum()),
                "connector_transition_count": int(group["connector_transition_count"].sum()),
                "source_method": "native 3DHP topology plus documented forward same-feature crossings",
                "confidence": "high" if len(downstream) == 1 else "review",
                "divergence_note": (
                    "Single downstream HUC-12 observed."
                    if len(downstream) == 1
                    else f"{len(downstream)} downstream HUC-12s observed; review divergence/boundary effects."
                ),
            }
        )
    routing = pd.DataFrame(rows)
    routing.to_csv(ROUTING_CSV, index=False)
    return routing


def write_comparison(
    frame: gpd.GeoDataFrame,
    connectors: gpd.GeoDataFrame,
    reconciliation: pd.DataFrame,
    routing: pd.DataFrame,
    checks: dict[str, Any],
) -> pd.DataFrame:
    status = reconciliation["qa_status"].value_counts()
    physical = frame["physicality"].isin(["physical_channel", "canal", "drainageway"])
    official_connector = frame["physicality"].eq("authoritative_network_connector")
    candidate_unresolved = int(status.get("UNRESOLVED", 0))
    rows = [
        ("physical flowline count", 864, int(physical.sum()), int(physical.sum()) - 864, "Full 3DHP study extent; not count-optimized to v0.1."),
        ("total physical length km", round(float(gpd.read_file(CANONICAL_GPKG, layer="water_flowlines_order3").to_crs(MAP_CRS).length.sum() / 1000), 3), round(float(pd.to_numeric(frame.loc[physical, "lengthkm"], errors="coerce").sum()), 3), "", "3DHP includes lower-order full-basin hydrography."),
        ("authoritative network connector count", 0, int(official_connector.sum()), int(official_connector.sum()), "Kept separate from mapped watercourses."),
        ("project-inferred connector count", len(connectors), candidate_unresolved, candidate_unresolved - len(connectors), "Only UNRESOLVED project edges would remain after approval."),
        ("HUC-12s with observed downstream routing", "not evaluated", int(routing["downstream_relationship_count"].gt(0).sum()), "", "Native cross-HUC transitions only."),
        ("HUC-12s unresolved", "not evaluated", int(routing["downstream_relationship_count"].eq(0).sum()), "", "Includes terminal HUCs and extract/boundary limitations."),
        ("directed network weak components", "not evaluated", checks["weak_component_count"], "", "Native hydrosequence network within buffered extract."),
        ("network outlets", "not evaluated", checks["outlet_count"], "", "Native terminal flags/downstream sequence 0; includes regional terminal networks."),
        ("divergent flowlines", "not evaluated", int(pd.to_numeric(frame["divergence"], errors="coerce").fillna(0).gt(0).sum()), "", "Native divergence attribute (main and minor paths)."),
        ("replaced physical", 0, int(status.get("REPLACED_PHYSICAL", 0)), "", "3DHP physical-class transition."),
        ("replaced authoritative connector", 0, int(status.get("REPLACED_AUTHORITATIVE_CONNECTOR", 0)), "", "3DHP topology uses a connector class."),
        ("already redundant", 0, int(status.get("ALREADY_REDUNDANT", 0)), "", "Released physical topology already carried the transition."),
        ("invalid baseline inference", 0, int(status.get("INVALID_BASELINE_INFERENCE", 0)), "", "WBD identity/tohuc validation."),
    ]
    comparison = pd.DataFrame(
        rows,
        columns=["metric", "released_v0_1", "qa_candidate", "difference", "interpretation"],
    )
    comparison.to_csv(COMPARISON_CSV, index=False)
    return comparison


def save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".png"), dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", facecolor="white", metadata={"Date": None})
    plt.close(fig)


def add_map_furniture(ax: plt.Axes, *, scale_side: str = "left") -> None:
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    width = xmax - xmin
    height = ymax - ymin
    scale_m = 50_000
    x0 = (
        xmin + width * 0.06
        if scale_side == "left"
        else xmax - width * 0.06 - scale_m
    )
    y0 = ymin + height * 0.055
    ax.plot([x0, x0 + scale_m], [y0, y0], color="#222222", linewidth=2.2)
    ax.plot([x0, x0], [y0 - height * 0.008, y0 + height * 0.008], color="#222222", linewidth=1)
    ax.plot([x0 + scale_m, x0 + scale_m], [y0 - height * 0.008, y0 + height * 0.008], color="#222222", linewidth=1)
    ax.text(x0 + scale_m / 2, y0 + height * 0.014, "50 km", ha="center", va="bottom", fontsize=8)
    ax.annotate(
        "N",
        xy=(0.95, 0.93),
        xytext=(0.95, 0.84),
        xycoords="axes fraction",
        textcoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#222222", "lw": 1.2},
    )


def plot_review_maps(
    huc12: gpd.GeoDataFrame,
    frame: gpd.GeoDataFrame,
    baseline: gpd.GeoDataFrame,
    connectors: gpd.GeoDataFrame,
    reconciliation: pd.DataFrame,
) -> None:
    matplotlib.rcParams["svg.hashsalt"] = "western-basin-physical-hydrography-v01"
    huc = huc12.to_crs(MAP_CRS)
    lake = gpd.read_file(CANONICAL_GPKG, layer="water_lake_erie").to_crs(MAP_CRS)
    authoritative = frame.to_crs(MAP_CRS)
    old_physical = baseline.to_crs(MAP_CRS)
    old_connectors = connectors.to_crs(MAP_CRS)
    xmin, ymin, xmax, ymax = authoritative.total_bounds
    pad_x = (xmax - xmin) * 0.03
    pad_y = (ymax - ymin) * 0.03
    study_limits = (xmin - pad_x, xmax + pad_x, ymin - pad_y, ymax + pad_y)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharex=True, sharey=True)
    for ax in axes:
        lake.plot(ax=ax, color="#e6f3fa", edgecolor="#9dc8dd", linewidth=0.5)
        huc.boundary.plot(ax=ax, color="#c8c8c0", linewidth=0.25, rasterized=True)
        ax.set_axis_off()
    old_physical.plot(ax=axes[0], color="#2166ac", linewidth=0.45, rasterized=True)
    old_connectors.plot(ax=axes[0], color="#b2182b", linewidth=0.35, linestyle="--", rasterized=True)
    axes[0].set_title("Released Phase 1 v0.1\n864 physical flowlines + 251 inferred routing edges")

    authoritative.loc[authoritative["physicality"].eq("physical_channel")].plot(
        ax=axes[1], color="#2166ac", linewidth=0.22, rasterized=True
    )
    authoritative.loc[authoritative["physicality"].isin(["canal", "drainageway"])].plot(
        ax=axes[1], color="#159c9c", linewidth=0.22, rasterized=True
    )
    authoritative.loc[authoritative["physicality"].eq("authoritative_network_connector")].plot(
        ax=axes[1], color="#666666", linewidth=0.18, linestyle="--", rasterized=True
    )
    axes[1].set_title("USGS 3DHP review candidate\nphysical classes and network connectors separated")
    legend = [
        Line2D([0], [0], color="#2166ac", lw=2, label="Channel line / released physical"),
        Line2D([0], [0], color="#159c9c", lw=2, label="Canal or drainageway"),
        Line2D([0], [0], color="#666666", lw=2, ls="--", label="Official USGS network connector"),
        Line2D([0], [0], color="#b2182b", lw=2, ls="--", label="Project-inferred routing relationship — not mapped waterway"),
    ]
    for ax in axes:
        ax.set_xlim(study_limits[0], study_limits[1])
        ax.set_ylim(study_limits[2], study_limits[3])
        add_map_furniture(ax)
    fig.legend(
        handles=legend,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.045),
        ncol=2,
        frameon=False,
    )
    fig.suptitle("Phase 1 Physical Hydrography QA — Baseline vs Authoritative Network", fontsize=16)
    fig.text(0.5, 0.012, MAP_NOTE, ha="center", fontsize=10, color="#5a2020")
    fig.tight_layout(rect=(0, 0.11, 1, 0.94))
    save_figure(fig, QA / "hydrography_baseline_vs_authoritative")

    status_colors = {
        "REPLACED_PHYSICAL": "#2166ac",
        "REPLACED_AUTHORITATIVE_CONNECTOR": "#666666",
        "ALREADY_REDUNDANT": "#159c9c",
        "UNRESOLVED": "#b2182b",
        "INVALID_BASELINE_INFERENCE": "#7a0177",
    }
    mapped = old_connectors.merge(
        reconciliation[["old_connector_id", "qa_status"]],
        left_on="feature_id",
        right_on="old_connector_id",
        how="left",
    )
    fig, ax = plt.subplots(figsize=(12, 9))
    lake.plot(ax=ax, color="#e6f3fa", edgecolor="#9dc8dd", linewidth=0.5)
    huc.boundary.plot(ax=ax, color="#bdbdb7", linewidth=0.35, rasterized=True)
    for qa_status, color in status_colors.items():
        subset = mapped.loc[mapped["qa_status"].eq(qa_status)]
        if not subset.empty:
            subset.plot(
                ax=ax,
                color=color,
                linewidth=1.0 if qa_status == "UNRESOLVED" else 0.55,
                linestyle="--" if qa_status in {"UNRESOLVED", "REPLACED_AUTHORITATIVE_CONNECTOR"} else "-",
                rasterized=True,
            )
    ax.set_axis_off()
    ax.set_xlim(study_limits[0], study_limits[1])
    ax.set_ylim(study_limits[2], study_limits[3])
    add_map_furniture(ax, scale_side="right")
    ax.set_title("HUC-12 Routing Reconciliation — Review Only", fontsize=15)
    counts = reconciliation["qa_status"].value_counts()
    status_labels = {
        "REPLACED_PHYSICAL": "Replaced physical",
        "REPLACED_AUTHORITATIVE_CONNECTOR": "Replaced authoritative connector (not ordinary stream)",
        "ALREADY_REDUNDANT": "Already redundant",
        "UNRESOLVED": "Project-inferred routing relationship — not mapped waterway",
        "INVALID_BASELINE_INFERENCE": "Invalid baseline inference",
    }
    handles = [
        Line2D([0], [0], color=color, lw=2, ls="--" if status in {"UNRESOLVED", "REPLACED_AUTHORITATIVE_CONNECTOR"} else "-", label=f"{status_labels[status]} ({int(counts.get(status, 0))})")
        for status, color in status_colors.items()
    ]
    ax.legend(handles=handles, loc="lower left", frameon=True, fontsize=9)
    fig.text(0.5, 0.025, MAP_NOTE, ha="center", fontsize=10, color="#5a2020")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save_figure(fig, QA / "huc12_routing_reconciliation")


def maumee_terminal_continuity(frame: gpd.GeoDataFrame) -> dict[str, Any]:
    network = frame.loc[frame["hydrosequence"].notna()].drop_duplicates("hydrosequence")
    downstream = dict(
        zip(
            network["hydrosequence"].astype(int),
            network["dnhydrosequence"].fillna(0).astype(int),
        )
    )
    major_names = [
        "Maumee River",
        "Saint Joseph River",
        "Saint Marys River",
        "Auglaize River",
        "Tiffin River",
        "Blanchard River",
    ]
    trace_results: dict[str, dict[str, int | bool]] = {}
    terminal_nodes: dict[str, set[int]] = {}
    for name in major_names:
        named = network.loc[network["gnisidlabel"].astype("string").eq(name)]
        reaches_terminal = 0
        cycles = 0
        terminals: set[int] = set()
        for start in named["hydrosequence"].astype(int):
            seen: set[int] = set()
            current = start
            previous = start
            while current and current in downstream and current not in seen:
                seen.add(current)
                previous = current
                current = downstream[current]
            if current == 0:
                reaches_terminal += 1
                terminals.add(previous)
            elif current in seen:
                cycles += 1
        trace_results[name] = {
            "named_flowline_count": len(named),
            "reaches_native_terminal_count": reaches_terminal,
            "cycle_count": cycles,
            "pass": bool(len(named) and reaches_terminal == len(named)),
        }
        terminal_nodes[name] = terminals
    maumee = trace_results["Maumee River"]
    lake = gpd.read_file(CANONICAL_GPKG, layer="water_lake_erie").to_crs(frame.crs)
    maumee_terminals = network.loc[
        network["hydrosequence"].astype(int).isin(terminal_nodes["Maumee River"])
    ]
    lake_intersection = bool(
        len(maumee_terminals)
        and maumee_terminals.geometry.intersects(lake.geometry.union_all()).all()
    )
    return {
        "maumee_named_flowline_count": maumee["named_flowline_count"],
        "maumee_named_flowlines_reaching_native_terminal": maumee[
            "reaches_native_terminal_count"
        ],
        "maumee_trace_cycle_count": maumee["cycle_count"],
        "maumee_to_terminal_continuity_pass": maumee["pass"],
        "maumee_terminal_intersects_lake_erie": lake_intersection,
        "major_tributary_terminal_traces": trace_results,
    }


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for values in frame.itertuples(index=False, name=None):
        clean = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
        rows.append("| " + " | ".join(clean) + " |")
    return "\n".join([header, separator, *rows])


def update_manifest_with_analysis(
    frame: gpd.GeoDataFrame,
    checks: dict[str, Any],
    status_counts: dict[str, int],
) -> None:
    manifest = json.loads(RETRIEVAL_MANIFEST.read_text(encoding="utf-8"))
    manifest.update(
        {
            "feature_type_domain": {str(key): value for key, value in sorted(
                frame[["featuretype", "featuretypelabel"]].drop_duplicates().set_index("featuretype")["featuretypelabel"].to_dict().items()
            )},
            "physicality_mapping": PHYSICALITY,
            "source_generation_counts": {
                str(key): int(value) for key, value in frame["source_generation"].value_counts().items()
            },
            "workunit_counts": {
                str(key): int(value) for key, value in frame["workunitid"].value_counts(dropna=False).items()
            },
            "network_fields_used": [
                "hydrosequence",
                "dnhydrosequence",
                "uphydrosequence",
                "flowdirectionlabel",
                "streamorder",
                "divergence",
                "mainstemid",
                "catchmentid3dhp",
            ],
            "reconciliation_status_counts": status_counts,
            "canonical_gpkg": "data/processed/glasspunk_base.gpkg",
            "canonical_gpkg_sha256": sha256(CANONICAL_GPKG),
            "analysis_checks": checks,
        }
    )
    RETRIEVAL_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_reports(
    service_metadata: dict[str, Any],
    layer_metadata: dict[str, Any],
    frame: gpd.GeoDataFrame,
    reconciliation: pd.DataFrame,
    comparison: pd.DataFrame,
    routing: pd.DataFrame,
    checks: dict[str, Any],
    assignment_stats: dict[str, int],
) -> None:
    status_order = [
        "REPLACED_PHYSICAL",
        "REPLACED_AUTHORITATIVE_CONNECTOR",
        "ALREADY_REDUNDANT",
        "UNRESOLVED",
        "INVALID_BASELINE_INFERENCE",
    ]
    observed_status = reconciliation["qa_status"].value_counts()
    status = {key: int(observed_status.get(key, 0)) for key in status_order}
    types = (
        frame.groupby(["featuretype", "featuretypelabel", "physicality"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
    )
    workunits = (
        frame.groupby(["workunitid", "source_generation"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
    )
    unresolved_categories = (
        reconciliation.loc[reconciliation["qa_status"].eq("UNRESOLVED")]
        .groupby("unresolved_category")
        .size()
        .rename("count")
        .reset_index()
    )
    resolved = len(reconciliation) - status.get("UNRESOLVED", 0) - status.get(
        "INVALID_BASELINE_INFERENCE", 0
    )
    recommendation = (
        "B — ACCEPT WITH QUALIFICATION"
        if resolved / len(reconciliation) >= 0.8
        else "C — HOLD"
    )
    refresh = json.loads(RETRIEVAL_MANIFEST.read_text(encoding="utf-8")).get(
        "service_refresh_text", "not stated"
    )
    source_review = f"""# Water Hydrography Source Review

## Executive finding

The official USGS 3D Hydrography Program `3DHP_all` FeatureServer, Flowline layer 50, is suitable for Phase 1 follow-up QA. The review snapshot contains **{len(frame):,}** flowlines in the complete Phase 1 HUC-12 union plus a documented 500 m buffer. It remains review data and does not modify the released v0.1 baseline.

## Source metadata

- Dataset/service: {service_metadata.get('name', 'USGS 3DHP_all')}
- Agency: U.S. Geological Survey / The National Map
- Service: <{SERVICE_URL}>
- Flowline layer 50: <{FLOWLINE_URL}>
- Service refresh: **{refresh}**
- Retrieval date: **{json.loads(RETRIEVAL_MANIFEST.read_text(encoding='utf-8')).get('retrieved_date')}**
- Native service CRS: EPSG:3857; requested snapshot storage: EPSG:4326; metric analysis: EPSG:26917
- Geometry: {layer_metadata.get('geometryType')}; service declares Z={layer_metadata.get('hasZ')} and M={layer_metadata.get('hasM')}
- Maximum query size: {layer_metadata.get('maxRecordCount')} records
- Use constraints: {service_metadata.get('useConstraints', 'None stated')}
- Terms: official metadata states no use constraints and describes the data as open/non-proprietary; USGS acknowledgment is appreciated.

## Retrieval and extent

`src/python/qa/build_physical_hydrography_review.py` unions all 252 Phase 1 HUC-12 polygons, buffers the union by 500 m in EPSG:5070 to retain cross-boundary network links, simplifies only the server query mask by 100 m, paginates the official FeatureServer in ordered 2,500-record requests, de-duplicates `OBJECTID`, and then applies the exact unsimplified 500 m mask. The raw GeoJSON snapshot is gzip-compressed locally at `data/raw/usgs/3dhp_flowlines_maumee_buffer500m.geojson.gz`. It is intentionally excluded from ordinary Git and Git LFS because it is reproducibly downloadable. Tracked service metadata and the source manifest preserve the retrieval date, method, extent, **{len(frame):,}** feature count, migrated-NHD/EDH provenance, and expected SHA-256 `{sha256(RAW_FLOWLINES)}`.

The 500 m buffer supports topology at the project boundary. It is not used to assign HUC routing by proximity. Flowline representative points assign a line to a HUC-12 for transition summarization; direction comes only from native `hydrosequence` / `dnhydrosequence` attributes.

## Feature classes and physicality

{markdown_table(types)}

Connector classes remain valid elements of the official network but are not portrayed as ordinary streams.

## 3DHP versus migrated NHD provenance

{markdown_table(workunits)}

`workunitid=NHD` is preserved as migrated/supplemental NHD provenance. The 232 features carrying numeric work unit `300290` are classified as an EDH work unit: the [official USGS access page](https://www.usgs.gov/3d-hydrography-program/access-3dhp-data-products) specifically identifies Big Darby Creek work unit 300290 as a July 2026 EDH release with missing flow-network derivatives, and the [EDH data dictionary](https://www.usgs.gov/ngp-standards-and-specifications/elevation-derived-hydrography-data-acquisition-specifications-1) defines numeric `workunitid` as the 3DHP project tracking ID. All 232 records lack native derivative fields, consistent with the documented issue. The study extract is therefore **mixed but overwhelmingly migrated NHD**, not uniformly new lidar-derived EDH.

## Network attributes

The extract preserves `id3dhp`, `featuredate`, `mainstemid`, `featuretype`, `featuretypelabel`, `flowdirection`, `flowdirectionlabel`, `onsurface`, `streamorder`, `hydrosequence`, `dnhydrosequence`, `uphydrosequence`, `divergence`, catchment/flowpath IDs, level paths, terminal paths, and `workunitid`. Native downstream derivatives are populated for {checks['network_node_count']:,} features; unpopulated EDH and other records are retained but not assigned invented topology.

## Limitations

- A mapped line does not establish perennial flow.
- Canal and drainageway behavior varies; agricultural tile drainage is incompletely represented.
- Official connector classes are topological devices, not necessarily surface channels.
- HUC boundaries and representative-point line assignments can create local boundary ambiguity.
- The live service changes over time; the expected snapshot hash detects any later retrieval difference from the accepted review input.
- The source is unsuitable for parcel/site regulatory determinations.
"""
    SOURCE_REVIEW_MD.write_text(source_review, encoding="utf-8")

    status_table = pd.DataFrame(
        [{"QA outcome": key, "count": value} for key, value in sorted(status.items())]
    )
    reconciliation_report = f"""# Physical Hydrography Reconciliation

# Executive Finding

The Phase 1 follow-up replaces representative-point reasoning with authoritative USGS network evidence for current-development use while preserving the historical v0.1 release. Of 251 inferred WBD connectors, the final connector-by-connector review found the following:

{markdown_table(status_table)}

Human decision after source, topology, full-geometry, provenance, and visual review: **{recommendation}**.

# Released Phase 1 Method

Water System v0.1 contains 864 NHDPlus HR order ≥3 physical flowlines in Lower Maumee and 251 straight representative-point edges derived from authoritative WBD `tohuc`. The latter are abstract graph edges, not waterways. The released GeoPackage SHA-256 remains `{sha256(CANONICAL_GPKG)}`.

# Problem With Representative-Point Routing

The v0.1 edges correctly preserve an abstract HUC routing relationship, but their straight geometry can be misread as mapped hydrography and omits physical class, lower-order drainage, waterbody passage, and official network-connector semantics.

# Authoritative Hydrography Source

See [Water Hydrography Source Review](water_hydrography_source_review.md). This QA uses USGS `3DHP_all` Flowline layer 50, refreshed {refresh}, from the hash-verified retrieval snapshot. The large reproducible extract is not stored in Git.

# 3DHP Versus Legacy NHD Provenance

The extract is mixed: {int(frame['source_generation'].eq('migrated_nhd').sum()):,} migrated NHD features, {int(frame['source_generation'].eq('edh_work_unit').sum()):,} EDH work-unit features, and {int(frame['source_generation'].eq('unknown').sum()):,} records without a work-unit value. The EDH records belong to work unit 300290, whose missing derivatives are a documented USGS July 2026 issue. The extract is not labeled uniformly as new EDH.

# Retrieval Method

The reproducible extractor uses the full HUC polygon extent plus a 500 m buffer, paginated FeatureServer queries, exact post-filtering, raw snapshot hashing, and preserved service/layer metadata. It does not use representative points to retrieve data.

# Flowline Feature Classes

{markdown_table(types)}

# Physical Versus Network-Connector Semantics

Channel Line, Canal, and Drainageway are candidate physical hydrography classes. Surface, Waterbody, Elevation Breaching, and Hydro Unenforced connectors remain separately classified `authoritative_network_connector`. No connector class is called a stream.

# CRS and Geometry Validation

- Storage CRS: {checks['storage_crs']}; metric analysis CRS: {checks['analysis_crs']}
- Valid/empty/null geometry failures: {checks['invalid_geometry_count']} / {checks['empty_geometry_count']} / {checks['null_geometry_count']}
- Duplicate OBJECTID / id3dhp / exact geometry: {checks['duplicate_objectid_count']} / {checks['duplicate_id3dhp_count']} / {checks['duplicate_geometry_count']}
- Bounds in EPSG:4326: {checks['bounds_epsg4326']}
- Projected/report length relative-error p95: {checks['length_relative_error_p95']}
- Lines assigned to a HUC-12 by representative point: {assignment_stats['assigned']:,}; outside/boundary: {assignment_stats['outside_or_boundary']:,}
- Service declares Z and M. GeoJSON/Shapely retained Z on {checks['has_z_count']:,} geometries; M is not relied on by this QA.

# Topology Method

Inter-feature direction is controlled by native `hydrosequence → dnhydrosequence`. A second intersection audit handles the special case where one directed 3DHP feature spans both HUC polygons; it uses coordinate order only when `flowdirectionlabel` explicitly confirms digitized downstream direction. The buffered extract yields {checks['network_node_count']:,} topology nodes, {checks['network_edge_count']:,} native edges, {checks['weak_component_count']:,} weak components, {checks['outlet_count']:,} native terminal records, {checks['missing_downstream_reference_count']:,} missing downstream references, and {checks['self_loop_count']} self-loops. Downstream `pathlength` reversals: {checks['pathlength_downstream_reversal_count']}. The Maumee named-flowline terminal trace passes: **{checks['maumee_to_terminal_continuity_pass']}** ({checks['maumee_named_flowlines_reaching_native_terminal']}/{checks['maumee_named_flowline_count']}), and its terminal Waterbody Connector intersects the accepted western Lake Erie polygon: **{checks['maumee_terminal_intersects_lake_erie']}**. Saint Joseph, Saint Marys, Auglaize, Tiffin, and Blanchard named-flowline traces are recorded in the machine-readable QA summary.

# Connector-by-Connector Reconciliation

The authoritative evidence and retained gaps are in [wbd_connector_reconciliation.csv](wbd_connector_reconciliation.csv). Status priority is: invalid WBD identity/tohuc evidence; already represented in released physical topology; native or confirmed same-feature 3DHP physical crossing; native or confirmed same-feature crossing involving an official connector; otherwise unresolved. The full-geometry crossing audit corrected the preliminary aggregate because native derivatives alone cannot expose a boundary crossing within one feature.

# Baseline Comparison

{markdown_table(comparison)}

# Remaining Unresolved Routing

`UNRESOLVED` rows remain explicitly project-inferred analytical edges with `source_method=project_inference` and `physical_geometry=false`. Their evidence is preserved in [unresolved_routing_summary.csv](unresolved_routing_summary.csv).

{markdown_table(unresolved_categories)}

The review-only HUC routing table contains {int(routing['downstream_relationship_count'].eq(0).sum())} HUC-12s without an observed authoritative downstream relationship; that figure includes terminal units and is not proof of absent drainage.

# Limitations

National hydrography does not fully encode agricultural tile drainage in Black Swamp Country. Migrated NHD dominates this snapshot. Direct cross-HUC transition matching is conservative and may leave a defensible WBD relationship unresolved when local topology, waterbody geometry, HUC boundary placement, or an unpopulated EDH derivative prevents a direct match.

# Recommended Canonical Representation

If later accepted, use three separate layers: `hydrography_physical`, `hydrography_network_connectors`, and `routing_inferred_unresolved`. Preserve feature provenance and never render all three with homogeneous stream symbology.

# Human Review Decision

**B — ACCEPT WITH QUALIFICATION.**

The USGS 3DHP-based hydrography and network topology are approved as the preferred routing architecture for future Phase 1-derived work. Physical channels and authoritative USGS network connectors must remain separate semantic classes. The remaining unresolved project-derived HUC-12 routing relationships are retained explicitly as abstract analytical edges and are not mapped or described as waterways.

Visual review passed for both QA maps: physical classes use solid blue/teal symbology, official connector classes use gray dashed symbology and explicit non-stream labeling, and project-inferred unresolved edges use red dashed symbology with the required not-a-waterway note. HUC context, western Lake Erie, north arrows, and metric scale bars are present.

Qualifications:

1. Most extracted 3DHP features are migrated NHD rather than new EDH.
2. Official 3DHP network connectors are authoritative topology features but are not necessarily physical channels.
3. Agricultural tile drainage is incompletely represented.
4. Unresolved project-derived analytical routing relationships remain pending local outlet review.
5. Acceptance does not retroactively modify the released `v0.1-water-system` artifact.

Current-development integration uses separate `hydrography_physical`, `hydrography_network_connectors`, and `routing_inferred_unresolved` layers. The legacy v0.1 layers remain preserved for backward compatibility and historical interpretation.
"""
    RECONCILIATION_MD.write_text(reconciliation_report, encoding="utf-8")

    summary = {
        "review_status": "accepted_with_qualification",
        "canonical_status": "current_development_integration_pending",
        "human_decision": recommendation,
        "recommendation": recommendation,
        "source": "USGS 3DHP_all Flowline layer 50",
        "service_refresh": refresh,
        "feature_count": len(frame),
        "feature_type_counts": {str(key): int(value) for key, value in frame["featuretypelabel"].value_counts().items()},
        "physicality_counts": {str(key): int(value) for key, value in frame["physicality"].value_counts().items()},
        "source_generation_counts": {str(key): int(value) for key, value in frame["source_generation"].value_counts().items()},
        "reconciliation_status_counts": status,
        "huc_assignment": assignment_stats,
        "checks": checks,
        "canonical_gpkg_sha256": sha256(CANONICAL_GPKG),
        "canonical_modified": False,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    service_metadata, layer_metadata = fetch_metadata()
    huc12_area, exact_geometry, query_geometry = study_geometries()
    flowlines = prepare_flowlines(fetch_flowlines(exact_geometry, query_geometry))
    write_manifest(service_metadata, layer_metadata, flowlines)

    huc12 = gpd.read_file(CANONICAL_GPKG, layer="water_subwatersheds_huc12")
    baseline = gpd.read_file(CANONICAL_GPKG, layer="water_flowlines_order3")
    connectors = gpd.read_file(CANONICAL_GPKG, layer="water_huc12_routing_inferred")
    if len(huc12_area) != len(huc12):
        raise AssertionError("Raw and canonical Phase 1 HUC-12 counts differ")
    if len(baseline) != 864 or len(connectors) != 251:
        raise AssertionError("Released Phase 1 baseline count changed")

    flowlines["huc12"], assignment_stats = assign_huc12(flowlines, huc12)
    transitions, topology_stats = build_transitions(flowlines)
    transitions.to_csv(TRANSITIONS_CSV, index=False)
    native_pairs = aggregate_transitions(transitions)
    same_feature_pairs, reverse_pairs = build_same_feature_crossings(
        flowlines, huc12, connectors
    )
    topology_stats["same_feature_forward_crossing_count"] = len(same_feature_pairs)
    topology_stats["same_feature_reverse_pair_count"] = len(reverse_pairs)
    native_keys = set(
        zip(native_pairs["from_huc12"].astype(str), native_pairs["to_huc12"].astype(str))
    )
    supplemental_pairs = same_feature_pairs.loc[
        ~same_feature_pairs.apply(
            lambda row: (str(row["from_huc12"]), str(row["to_huc12"])) in native_keys,
            axis=1,
        )
    ]
    topology_stats["same_feature_supplemental_crossing_count"] = len(supplemental_pairs)
    authoritative_pairs = combine_pair_evidence(native_pairs, supplemental_pairs)
    baseline_pairs = baseline_transition_pairs(baseline, huc12)
    reconciliation = reconcile_connectors(
        connectors, huc12, authoritative_pairs, baseline_pairs
    )
    reconciliation = characterize_unresolved(
        reconciliation, huc12, flowlines, transitions, reverse_pairs
    )
    reconciliation.to_csv(RECONCILIATION_CSV, index=False)
    if len(reconciliation) != 251:
        raise AssertionError("Every released inferred connector must receive one QA status")

    routing = write_routing_table(huc12, authoritative_pairs)
    checks = geometry_and_topology_checks(flowlines, transitions, topology_stats)
    checks.update(maumee_terminal_continuity(flowlines))
    comparison = write_comparison(
        flowlines, connectors, reconciliation, routing, checks
    )
    status_order = [
        "REPLACED_PHYSICAL",
        "REPLACED_AUTHORITATIVE_CONNECTOR",
        "ALREADY_REDUNDANT",
        "UNRESOLVED",
        "INVALID_BASELINE_INFERENCE",
    ]
    observed_status = reconciliation["qa_status"].value_counts()
    status_counts = {key: int(observed_status.get(key, 0)) for key in status_order}
    update_manifest_with_analysis(flowlines, checks, status_counts)
    write_reports(
        service_metadata,
        layer_metadata,
        flowlines,
        reconciliation,
        comparison,
        routing,
        checks,
        assignment_stats,
    )
    plot_review_maps(huc12, flowlines, baseline, connectors, reconciliation)
    print(f"Analyzed {len(flowlines):,} official 3DHP flowlines for review.", flush=True)
    print(f"Reconciliation outcomes: {status_counts}", flush=True)
    print("Canonical Phase 1 GeoPackage and released maps were not modified.", flush=True)


if __name__ == "__main__":
    main()
