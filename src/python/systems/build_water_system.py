"""Build Glasspunk Toledo Water System v0.1.

The builder downloads bounded, public USGS/USFWS feature-service records,
constructs a provenance-rich GIS/network package, and renders analytical maps.
Fictional scenario objects are deliberately non-spatial unless they reuse a
verified real-world anchor.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import networkx as nx
import numpy as np
import pandas as pd
import requests
import yaml
from PIL import Image
from shapely.geometry import LineString, Point, box


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
NETWORKS = PROCESSED / "networks"
MAPS = ROOT / "outputs" / "maps" / "systems"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "reports"
GPKG = PROCESSED / "glasspunk_base.gpkg"
RETRIEVED = date.today().isoformat()

USGS_WBD = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer"
USGS_NHD = "https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer"
USFWS_NWI = "https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer"

WATER_CRS = "EPSG:4326"
MAP_CRS = "EPSG:5070"
MAUMEE_HUC8S = tuple(f"0410000{i}" for i in range(3, 10))
NWI_FOCUS = (-84.00, 40.90, -82.70, 42.05)

COLORS = {
    "ink": "#18333f",
    "water": "#2d7ea7",
    "water_light": "#b9ddeb",
    "land": "#eee9dc",
    "ag": "#d9bd72",
    "urban": "#8c7080",
    "wetland": "#5c8d68",
    "hab": "#a8b73a",
    "scenario": "#08a6a6",
    "uncertain": "#8f8f89",
    "danger": "#c85f46",
}


def ensure_dirs() -> None:
    for p in [RAW / "usgs", RAW / "usfws", PROCESSED, NETWORKS, MAPS, FIGURES, TABLES, REPORTS]:
        p.mkdir(parents=True, exist_ok=True)


def arcgis_geojson(
    url: str,
    *,
    where: str,
    out_fields: str,
    cache: Path,
    geometry: str | None = None,
    page_size: int = 1000,
    max_allowable_offset: float | None = None,
) -> gpd.GeoDataFrame:
    """Download a query as paginated GeoJSON, or reuse the raw cache."""
    if cache.exists():
        return gpd.read_file(cache)

    all_features: list[dict[str, Any]] = []
    offset = 0
    while True:
        params: dict[str, Any] = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }
        if geometry:
            params.update(
                {
                    "geometry": geometry,
                    "geometryType": "esriGeometryEnvelope",
                    "inSR": 4326,
                    "spatialRel": "esriSpatialRelIntersects",
                }
            )
        if max_allowable_offset is not None:
            params["maxAllowableOffset"] = max_allowable_offset
            params["geometryPrecision"] = 6
        response = requests.get(url, params=params, timeout=180)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(f"ArcGIS query failed: {payload['error']}")
        features = payload.get("features", [])
        all_features.extend(features)
        if len(features) < page_size:
            break
        offset += len(features)
        if offset > 100_000:
            raise RuntimeError("Query pagination exceeded safety limit")

    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps({"type": "FeatureCollection", "features": all_features}),
        encoding="utf-8",
    )
    if not all_features:
        return gpd.GeoDataFrame(geometry=[], crs=WATER_CRS)
    return gpd.GeoDataFrame.from_features(all_features, crs=WATER_CRS)


def normalize_columns(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    frame = frame.copy()
    frame.columns = [str(c).split(".")[-1].lower() for c in frame.columns]
    return frame


def add_common(
    frame: gpd.GeoDataFrame,
    *,
    prefix: str,
    name_col: str,
    feature_type: str,
    source_name: str,
    source_url: str,
    confidence: str = "high",
    canon_status: str = "verified",
    reality_status: str = "real",
    commodity: str | None = None,
) -> gpd.GeoDataFrame:
    frame = frame.copy()
    ids = frame.index.astype(str)
    if "huc12" in frame:
        ids = frame["huc12"].astype(str)
    elif "permanent_identifier" in frame:
        ids = frame["permanent_identifier"].astype(str)
    elif "globalid" in frame:
        ids = frame["globalid"].astype(str).str.strip("{}")
    frame["feature_id"] = prefix + ids
    frame["system_id"] = "SYS-WATER"
    frame["feature_name"] = frame[name_col].fillna(feature_type) if name_col in frame else feature_type
    frame["feature_type"] = feature_type
    frame["reality_status"] = reality_status
    frame["canon_status"] = canon_status
    frame["scenario_year"] = 2026 if reality_status == "real" else pd.NA
    frame["region_primary"] = pd.NA
    frame["regions_intersected"] = pd.NA
    frame["commodity_or_flow"] = commodity
    frame["direction"] = pd.NA
    frame["capacity"] = np.nan
    frame["capacity_units"] = pd.NA
    frame["dependency_type"] = pd.NA
    frame["criticality"] = pd.NA
    frame["redundancy"] = pd.NA
    frame["source_name"] = source_name
    frame["source_url_or_identifier"] = source_url
    frame["retrieved_date"] = RETRIEVED
    frame["confidence"] = confidence
    frame["notes"] = pd.NA
    return frame


def acquire_layers() -> dict[str, gpd.GeoDataFrame]:
    huc8_where = "huc8 IN (" + ",".join(f"'{h}'" for h in MAUMEE_HUC8S) + ")"
    huc12_where = " OR ".join(f"huc12 LIKE '{h}%'" for h in MAUMEE_HUC8S)
    reach_where = " OR ".join(f"reachcode LIKE '{h}%'" for h in MAUMEE_HUC8S)
    huc8 = arcgis_geojson(
        f"{USGS_WBD}/4/query",
        where=huc8_where,
        out_fields="huc8,name,areasqkm,states",
        cache=RAW / "usgs" / "wbd_huc8_maumee_basin.geojson",
    )
    huc12 = arcgis_geojson(
        f"{USGS_WBD}/6/query",
        where=huc12_where,
        out_fields="huc12,name,areasqkm,states,tohuc,hutype,humod",
        cache=RAW / "usgs" / "wbd_huc12_maumee_basin.geojson",
    )
    flow = arcgis_geojson(
        f"{USGS_NHD}/3/query",
        where="reachcode LIKE '04100009%' AND streamorde >= 3",
        out_fields=(
            "permanent_identifier,gnis_name,lengthkm,reachcode,flowdir,streamorde,"
            "fromnode,tonode,hydroseq,dnhydroseq,terminalfl,startflag"
        ),
        cache=RAW / "usgs" / "nhdplus_maumee_order3.geojson",
        page_size=2000,
    )
    lake = arcgis_geojson(
        f"{USGS_NHD}/9/query",
        where="gnis_name='Lake Erie'",
        out_fields="permanent_identifier,gnis_name,areasqkm,ftype,fcode",
        cache=RAW / "usgs" / "nhd_lake_erie.geojson",
    )
    try:
        wetlands = arcgis_geojson(
            f"{USFWS_NWI}/0/query",
            where="Wetlands.ACRES >= 25",
            out_fields="Wetlands.ATTRIBUTE,Wetlands.WETLAND_TYPE,Wetlands.ACRES,Wetlands.GLOBALID",
            geometry=",".join(map(str, NWI_FOCUS)),
            cache=RAW / "usfws" / "nwi_nw_ohio_25ac_generalized.geojson",
            page_size=1000,
            max_allowable_offset=0.00025,
        )
    except Exception:
        wetlands = arcgis_geojson(
            f"{USFWS_NWI}/0/query",
            where="ACRES >= 25",
            out_fields="ATTRIBUTE,WETLAND_TYPE,ACRES,GLOBALID",
            geometry=",".join(map(str, NWI_FOCUS)),
            cache=RAW / "usfws" / "nwi_nw_ohio_25ac_generalized.geojson",
            page_size=1000,
            max_allowable_offset=0.00025,
        )

    huc8, huc12, flow, lake, wetlands = map(normalize_columns, [huc8, huc12, flow, lake, wetlands])
    if "wetland_type" in wetlands.columns:
        wetlands = wetlands[
            wetlands["wetland_type"].isin(
                ["Freshwater Emergent Wetland", "Freshwater Forested/Shrub Wetland"]
            )
        ].reset_index(drop=True)
    point_lookup = {str(row.huc12): row.geometry.representative_point() for row in huc12.itertuples()}
    connector_rows: list[dict[str, Any]] = []
    for row in huc12.itertuples():
        source_huc = str(row.huc12)
        target_huc = str(row.tohuc) if pd.notna(row.tohuc) else ""
        if target_huc in point_lookup and target_huc != source_huc:
            connector_rows.append(
                {
                    "from_huc12": source_huc,
                    "to_huc12": target_huc,
                    "name": f"{source_huc} to {target_huc}",
                    "geometry": LineString([point_lookup[source_huc], point_lookup[target_huc]]),
                }
            )
    connectors = gpd.GeoDataFrame(connector_rows, geometry="geometry", crs=WATER_CRS)
    huc8 = add_common(
        huc8, prefix="WTR-HUC8-", name_col="name", feature_type="watershed_stock",
        source_name="USGS Watershed Boundary Dataset", source_url=f"{USGS_WBD}/4",
        commodity="water / nitrogen / phosphorus source context",
    )
    huc8["feature_id"] = "WTR-HUC8-" + huc8["huc8"].astype(str)
    huc12 = add_common(
        huc12, prefix="WTR-HUC12-", name_col="name", feature_type="subwatershed_stock",
        source_name="USGS Watershed Boundary Dataset", source_url=f"{USGS_WBD}/6",
        commodity="water / nitrogen / phosphorus source context",
    )
    huc12["direction"] = "to_huc12"
    huc12["notes"] = "Source context only; no parcel-scale nutrient load is asserted."
    flow = add_common(
        flow, prefix="WTR-FLOW-", name_col="gnis_name", feature_type="river_flow_edge",
        source_name="USGS NHDPlus High Resolution", source_url=f"{USGS_NHD}/3",
        commodity="water / suspended and dissolved nutrients",
    )
    flow["direction"] = "digitized downstream (NHDPlus topology)"
    flow["notes"] = "Physical NHDPlus display covers Lower Maumee HUC-8 at stream order >=3; full-basin routing is supplemented by a separate inferred WBD topology layer."
    connectors = add_common(
        connectors, prefix="WTR-HUC-ROUTE-", name_col="name", feature_type="subwatershed_routing_edge",
        source_name="USGS Watershed Boundary Dataset", source_url=f"{USGS_WBD}/6",
        confidence="medium", canon_status="inferred", commodity="water / nutrient routing context",
    )
    connectors["feature_id"] = "WTR-HUC-ROUTE-" + connectors["from_huc12"].astype(str)
    connectors["direction"] = "from_huc12 to WBD tohuc"
    connectors["notes"] = "Straight representative-point connector derived from authoritative WBD topology; not physical river geometry."
    lake = add_common(
        lake, prefix="WTR-LAKE-", name_col="gnis_name", feature_type="receiving_water_stock",
        source_name="USGS NHDPlus High Resolution", source_url=f"{USGS_NHD}/9",
        commodity="water / nutrients / ecological response",
    )
    wetlands = add_common(
        wetlands, prefix="WTR-NWI-", name_col="wetland_type", feature_type="current_wetland_stock",
        source_name="USFWS National Wetlands Inventory", source_url=f"{USFWS_NWI}/0",
        commodity="water storage / nutrient interception / habitat",
    )
    wetlands["notes"] = "Public NWI freshwater emergent and forested/shrub wetland polygons >=25 acres in the Northwest Ohio focus window, generalized by the service at 0.00025 degrees for regional display; Lake/Riverine classes excluded; not a jurisdictional determination."
    return {"huc8": huc8, "huc12": huc12, "flow": flow, "connectors": connectors, "lake": lake, "wetlands": wetlands}


NODE_COLUMNS = [
    "feature_id", "system_id", "feature_name", "feature_type", "reality_status", "canon_status",
    "scenario_year", "region_primary", "regions_intersected", "commodity_or_flow", "direction",
    "capacity", "capacity_units", "dependency_type", "criticality", "redundancy", "source_name",
    "source_url_or_identifier", "retrieved_date", "confidence", "longitude", "latitude", "notes",
]


def construct_nodes_edges() -> tuple[pd.DataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    city_water = "https://toledo.oh.gov/departments/public-works/water/water-treatment"
    glos = "https://erddap.sensors.axds.co/erddap/tabledap/glos_crib.html"
    ohio_epa = "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/27/ams/sites/2019/E1-2019_monitorSite_Descs.pdf"
    epa_hab = "https://www.epa.gov/glwqa/lake-erie-water-quality-data"
    rows = [
        ["WTR-N-LAND", "SYS-WATER", "Agricultural and urban land", "source_stock", "real", "inferred", 2026, None, None, "precipitation / nitrogen / phosphorus", "to drainage", None, None, "source", "high", "distributed", "US EPA Maumee Watershed Nutrient TMDL", "https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load", RETRIEVED, "medium", None, None, "Basin-scale source context; no parcel load values."],
        ["WTR-N-DRAINAGE", "SYS-WATER", "Drainage and tributaries", "transport_node", "real", "verified", 2026, None, None, "water / nutrients", "downstream", None, None, "transport", "high", "networked", "USGS NHDPlus HR", f"{USGS_NHD}/3", RETRIEVED, "high", None, None, "Spatial geometry stored in the flowline layer."],
        ["WTR-N-MAUMEE", "SYS-WATER", "Maumee River", "transport_node", "real", "verified", 2026, "Maumee River Commons", "multiple", "water / nitrogen / phosphorus", "to Maumee Bay", None, None, "transport", "high", "low", "USGS NHDPlus HR", f"{USGS_NHD}/3", RETRIEVED, "high", None, None, None],
        ["WTR-N-BAY", "SYS-WATER", "Maumee Bay", "receiving_water_node", "real", "verified", 2026, None, None, "water / nutrients", "to western Lake Erie", None, None, "receiving water", "high", "low", "USGS NHDPlus HR", f"{USGS_NHD}/9", RETRIEVED, "high", None, None, "Represented within Lake Erie waterbody geometry."],
        ["WTR-N-WLE", "SYS-WATER", "Western Lake Erie", "receiving_water_node", "real", "verified", 2026, "Lake Erie Energy & Security Coast", "multiple", "water / nutrients", "lake circulation", None, None, "receiving water", "high", "low", "USGS NHDPlus HR", f"{USGS_NHD}/9", RETRIEVED, "high", None, None, None],
        ["WTR-N-HAB", "SYS-WATER", "HAB ecological response", "response_node", "real", "inferred", 2026, None, None, "cyanobacterial bloom risk", "may affect intake", None, None, "scientific response", "high", "seasonal", "US EPA Lake Erie Water Quality Data", epa_hab, RETRIEVED, "high", None, None, "Conceptual response node, not a mapped 2026 bloom footprint."],
        ["WTR-N-INTAKE", "SYS-WATER", "City of Toledo Water Intake Crib monitoring location", "intake_node", "real", "verified", 2026, "Lake Erie Energy & Security Coast", "Lake Erie / Glass City Core", "raw Lake Erie water", "to Collins Park", None, None, "intake", "critical", "location ambiguity", "GLOS / IOOS ERDDAP", glos, RETRIEVED, "medium", -83.3079, 41.67496, "Verified public GLOS station coordinate. Historic crib/light references describe other locations; review before treating as the sole physical intake."],
        ["WTR-N-COLLINS", "SYS-WATER", "Collins Park Water Treatment Plant", "treatment_node", "real", "verified", 2026, "Glass City Core", "Glass City Core", "treated drinking water", "to consumers", 140.0, "MGD design capacity", "treatment", "critical", "upgraded", "City of Toledo / Ohio EPA monitor-site description", city_water + " | " + ohio_epa, RETRIEVED, "high", -83.47596, 41.663405, "Plant coordinate is the co-located Ohio EPA air monitor site; City reports 140 MGD expanded capacity."],
        ["WTR-N-CONSUMERS", "SYS-WATER", "Toledo regional consumers", "consumer_stock", "real", "verified", 2026, "Glass City Core", "Lucas/Wood/Fulton/Monroe service area", "potable water", "demand / wastewater return", 500000.0, "people served approx.", "demand", "critical", "regional", "City of Toledo Water Treatment", city_water, RETRIEVED, "high", None, None, "City reports approximately 500,000 people and about 75 MGD average production."],
        ["WTR-N-WETLAND", "SYS-WATER", "Current wetlands", "interception_stock", "real", "inferred", 2026, "Black Swamp Country", "multiple", "water storage / nutrient interception", "feedback to drainage", None, None, "mitigation feedback", "medium", "distributed", "USFWS National Wetlands Inventory", f"{USFWS_NWI}/0", RETRIEVED, "medium", None, None, "Interception is a scientific inference; performance is site-specific and unquantified here."],
        ["WTR-N-2050-CELLS", "SYS-WATER", "Restored wetland treatment cells", "scenario_intervention", "fictional", "scenario", 2050, "Black Swamp Country", "multiple", "phosphorus interception / storage", "to drainage", None, None, "scenario mitigation", "medium", "distributed", "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml#water-2050-wetland-cells", RETRIEVED, "scenario", None, None, "No coordinates; deployment success is not assumed."],
        ["WTR-N-2050-SAMPLERS", "SYS-WATER", "Autonomous sampling fleets", "scenario_sensor", "fictional", "scenario", 2050, None, "watershed / lake", "water-quality observations", "to forecast platform", None, None, "scenario monitoring", "medium", "distributed", "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml#water-2050-samplers", RETRIEVED, "scenario", None, None, "No coordinates; conceptual network node."],
        ["WTR-N-2050-OPS", "SYS-WATER", "Intake-linked watershed operations", "scenario_control", "fictional", "scenario", 2050, None, "watershed / Glass City Core", "decisions / control", "feedback to retention and treatment", None, None, "scenario control", "critical", "unknown", "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml#water-2050-intake-ops", RETRIEVED, "scenario", None, None, "No coordinates; authority and efficacy unresolved."],
        ["WTR-N-2050-HEALTH", "SYS-WATER", "Neighborhood public-health warning integration", "scenario_decision", "fictional", "scenario", 2050, "Glass City Core", "service area", "risk warnings", "to consumers", None, None, "scenario public health", "high", "unknown", "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml#water-2050-health-warning", RETRIEVED, "scenario", None, None, "No personal exposure records modeled in v0.1."],
    ]
    nodes = pd.DataFrame(rows, columns=NODE_COLUMNS)

    edge_cols = [
        "feature_id", "system_id", "from_id", "to_id", "flow_type", "flow_direction",
        "nominal_flow", "flow_units", "seasonality", "failure_consequence", "scenario_modifier",
        "relationship_basis", "reality_status", "canon_status", "scenario_year", "source_name",
        "source_url_or_identifier", "retrieved_date", "confidence", "notes",
    ]
    edge_rows = [
        ["WTR-E-001", "SYS-WATER", "WTR-N-LAND", "WTR-N-DRAINAGE", "runoff / drainage", "downstream", None, None, "storm and seasonal", "source accumulation", None, "scientific_inference", "real", "inferred", 2026, "US EPA Maumee TMDL", "https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load", RETRIEVED, "high", "Quantitative load intentionally null."],
        ["WTR-E-002", "SYS-WATER", "WTR-N-DRAINAGE", "WTR-N-MAUMEE", "tributary delivery", "downstream", None, None, "variable; spring critical", "reduced/altered delivery", None, "observed", "real", "verified", 2026, "USGS NHDPlus HR", f"{USGS_NHD}/3", RETRIEVED, "high", None],
        ["WTR-E-003", "SYS-WATER", "WTR-N-MAUMEE", "WTR-N-BAY", "river discharge / nutrients", "downstream", None, None, "spring phosphorus load important", "receiving-water load changes", None, "observed", "real", "verified", 2026, "US EPA Lake Erie Water Quality Data", epa_hab, RETRIEVED, "high", None],
        ["WTR-E-004", "SYS-WATER", "WTR-N-BAY", "WTR-N-WLE", "bay-lake exchange", "outward / bidirectional circulation", None, None, "wind and flow dependent", "retention/dispersion changes", None, "scientific_inference", "real", "inferred", 2026, "NOAA Lake Erie HAB Forecast", "https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/", RETRIEVED, "high", None],
        ["WTR-E-005", "SYS-WATER", "WTR-N-WLE", "WTR-N-HAB", "nutrient-driven ecological response", "causal pathway", None, None, "summer bloom response", "ecological/public-health risk", None, "scientific_inference", "real", "inferred", 2026, "US EPA Lake Erie Water Quality Data", epa_hab, RETRIEVED, "high", "Not deterministic; weather, circulation, and biology mediate response."],
        ["WTR-E-006", "SYS-WATER", "WTR-N-HAB", "WTR-N-INTAKE", "raw-water hazard", "exposure pathway", None, None, "bloom season", "treatment challenge", None, "engineering_dependency", "real", "verified", 2026, "City of Toledo Water Quality", "https://toledo.oh.gov/residents/water/quality", RETRIEVED, "high", None],
        ["WTR-E-007", "SYS-WATER", "WTR-N-INTAKE", "WTR-N-COLLINS", "raw water", "to treatment", None, "MGD", "continuous", "loss of source supply", None, "engineering_dependency", "real", "verified", 2026, "City of Toledo Water Treatment", city_water, RETRIEVED, "high", None],
        ["WTR-E-008", "SYS-WATER", "WTR-N-COLLINS", "WTR-N-CONSUMERS", "potable water", "distribution", 75.0, "MGD average", "continuous", "service/public-health failure", None, "engineering_dependency", "real", "verified", 2026, "City of Toledo Water Treatment", city_water, RETRIEVED, "high", "Average production, not edge capacity."],
        ["WTR-E-009", "SYS-WATER", "WTR-N-WETLAND", "WTR-N-DRAINAGE", "retention / delayed release", "feedback", None, None, "site and storm dependent", "reduced storage/retention", None, "scientific_inference", "real", "inferred", 2026, "USFWS NWI", f"{USFWS_NWI}/0", RETRIEVED, "medium", "No removal efficiency assigned."],
        ["WTR-E-050", "SYS-WATER", "WTR-N-2050-CELLS", "WTR-N-DRAINAGE", "managed retention", "feedback", None, None, "adaptive", "uneven performance or failure", "2050 delta: added treatment stocks", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
        ["WTR-E-051", "SYS-WATER", "WTR-N-2050-SAMPLERS", "WTR-N-2050-OPS", "observations", "to control", None, None, "continuous / event driven", "blind spots / spoofing", "2050 delta: autonomous monitoring", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
        ["WTR-E-052", "SYS-WATER", "WTR-N-2050-OPS", "WTR-N-2050-CELLS", "control decision", "feedback", None, None, "event driven", "maladaptation / authority conflict", "2050 delta: intake-linked operations", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
        ["WTR-E-053", "SYS-WATER", "WTR-N-2050-OPS", "WTR-N-COLLINS", "forecast / treatment decision", "feedback", None, None, "event driven", "false positive/negative", "2050 delta: linked operations", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
        ["WTR-E-054", "SYS-WATER", "WTR-N-COLLINS", "WTR-N-2050-HEALTH", "water-quality status", "to warning system", None, None, "event driven", "delayed/missed warning", "2050 delta: public-health integration", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
        ["WTR-E-055", "SYS-WATER", "WTR-N-2050-HEALTH", "WTR-N-CONSUMERS", "public-health warning", "to users", None, None, "event driven", "inequitable access / alert fatigue", "2050 delta: neighborhood warning", "scenario_assumption", "fictional", "scenario", 2050, "Glasspunk scenario assumption", "metadata/scenario_assumptions.yml", RETRIEVED, "scenario", None],
    ]
    edges = pd.DataFrame(edge_rows, columns=edge_cols)
    point_nodes = nodes.dropna(subset=["longitude", "latitude"]).copy()
    points = gpd.GeoDataFrame(
        point_nodes,
        geometry=gpd.points_from_xy(point_nodes["longitude"], point_nodes["latitude"]),
        crs=WATER_CRS,
    )
    return nodes, edges, points


def write_gpkg(layers: dict[str, gpd.GeoDataFrame], points: gpd.GeoDataFrame) -> None:
    if GPKG.exists():
        GPKG.unlink()
    layer_map = {
        "huc8": "water_watersheds_huc8",
        "huc12": "water_subwatersheds_huc12",
        "flow": "water_flowlines_order3",
        "connectors": "water_huc12_routing_inferred",
        "lake": "water_lake_erie",
        "wetlands": "water_current_wetlands_25ac",
    }
    for key, layer_name in layer_map.items():
        layers[key].to_file(GPKG, layer=layer_name, driver="GPKG", index=False)
    points.to_file(GPKG, layer="water_verified_facilities", driver="GPKG", index=False)


def setup_axis(ax: plt.Axes, title: str, question: str) -> None:
    ax.set_title(title, loc="left", fontsize=19, fontweight="bold", color=COLORS["ink"], pad=18)
    ax.text(0, 1.015, question, transform=ax.transAxes, fontsize=10.5, color="#40545c", va="bottom")
    ax.set_axis_off()
    ax.set_facecolor("#f7f5ef")


def source_footer(fig: plt.Figure, text: str) -> None:
    fig.text(0.012, 0.012, text, fontsize=7.2, color="#56666b")
    fig.text(0.988, 0.012, f"Glasspunk Water System v0.1 | built {RETRIEVED}", fontsize=7.2, ha="right", color="#56666b")


def save_pair(fig: plt.Figure, stem: str) -> None:
    fig.savefig(MAPS / f"{stem}.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(MAPS / f"{stem}.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_base(ax: plt.Axes, data: dict[str, gpd.GeoDataFrame], huc12: bool = True) -> dict[str, gpd.GeoDataFrame]:
    p = projected_for_plot(data)
    if not p["lake"].empty:
        p["lake"].plot(ax=ax, color=COLORS["water_light"], edgecolor=COLORS["water"], linewidth=0.7, zorder=0)
    p["huc8"].plot(ax=ax, color=COLORS["land"], edgecolor=COLORS["ink"], linewidth=1.2, zorder=1)
    if huc12 and not p["huc12"].empty:
        p["huc12"].boundary.plot(ax=ax, color="#a5a296", linewidth=0.28, alpha=0.7, zorder=2)
    if not p["wetlands"].empty:
        p["wetlands"].plot(ax=ax, color=COLORS["wetland"], alpha=0.60, edgecolor="none", zorder=3)
    if not p["connectors"].empty:
        p["connectors"].plot(ax=ax, color=COLORS["water"], linewidth=0.45, alpha=0.38, linestyle="--", zorder=3)
    if not p["flow"].empty:
        widths = np.clip(pd.to_numeric(p["flow"].get("streamorde", 3), errors="coerce").fillna(3) - 1.5, 0.5, 3.0)
        p["flow"].plot(ax=ax, color=COLORS["water"], linewidth=widths * 0.5, alpha=0.85, zorder=4)
    basin_bounds = p["huc8"].total_bounds
    ax.set_xlim(basin_bounds[0] - 20_000, basin_bounds[2] + 150_000)
    ax.set_ylim(basin_bounds[1] - 25_000, basin_bounds[3] + 85_000)
    return p


def projected_for_plot(data: dict[str, gpd.GeoDataFrame]) -> dict[str, gpd.GeoDataFrame]:
    """Return clipped/generalized render copies; source geometry is unchanged."""
    p: dict[str, gpd.GeoDataFrame] = {}
    render_clip = box(-86.25, 39.85, -82.0, 42.45)
    for key, value in data.items():
        v = value.copy()
        if key == "lake" and not v.empty:
            v.geometry = v.geometry.intersection(render_clip)
            v = v[~v.geometry.is_empty]
        v = v.to_crs(MAP_CRS)
        tolerance = {"lake": 250.0, "wetlands": 35.0, "flow": 25.0, "connectors": 0.0, "huc12": 20.0, "huc8": 20.0}.get(key, 0.0)
        if tolerance and not v.empty:
            v.geometry = v.geometry.simplify(tolerance, preserve_topology=True)
        p[key] = v
    return p


def add_facilities(ax: plt.Axes, points: gpd.GeoDataFrame) -> None:
    p = points.to_crs(MAP_CRS)
    for _, row in p.iterrows():
        color = COLORS["danger"] if row.feature_id == "WTR-N-INTAKE" else COLORS["ink"]
        ax.scatter(row.geometry.x, row.geometry.y, s=70, color=color, edgecolor="white", linewidth=1.2, zorder=8)
        label = "Toledo intake\n(GLOS station)" if row.feature_id == "WTR-N-INTAKE" else "Collins Park WTP"
        offset = (8, 18) if row.feature_id == "WTR-N-INTAKE" else (8, -24)
        ax.annotate(label, (row.geometry.x, row.geometry.y), xytext=offset, textcoords="offset points", fontsize=8, fontweight="bold", zorder=9)


def render_maps(data: dict[str, gpd.GeoDataFrame], points: gpd.GeoDataFrame, historical_image: Path | None) -> None:
    # 01 baseline
    fig, ax = plt.subplots(figsize=(14, 9), facecolor="#f7f5ef")
    p = plot_base(ax, data)
    add_facilities(ax, points)
    setup_axis(ax, "01  WATER BASELINE — 2026", "What real land, water, wetlands, and drinking-water nodes define the present system?")
    ax.legend(handles=[
        Patch(facecolor=COLORS["land"], edgecolor=COLORS["ink"], label="Maumee basin HUC-8 watersheds (real)"),
        Line2D([0], [0], color=COLORS["water"], lw=2, label="NHDPlus flowline, order ≥3 (real)"),
        Line2D([0], [0], color=COLORS["water"], lw=1, ls="--", alpha=.5, label="WBD HUC-12 routing (inferred)"),
        Patch(facecolor=COLORS["wetland"], alpha=.6, label="NWI freshwater wetland ≥25 acres (real)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["danger"], label="Verified intake observation node", markersize=9),
    ], loc="lower left", frameon=True, fontsize=8)
    source_footer(fig, "Sources: USGS WBD/NHDPlus HR; USFWS NWI; GLOS/IOOS; City of Toledo; Ohio EPA. NWI is not a jurisdictional determination.")
    save_pair(fig, "01_water_baseline_2026")

    # 02 nutrient network
    fig, ax = plt.subplots(figsize=(14, 9), facecolor="#f7f5ef")
    p = projected_for_plot(data)
    if not p["lake"].empty:
        p["lake"].plot(ax=ax, color=COLORS["water_light"], edgecolor=COLORS["water"], linewidth=.7)
    p["huc8"].plot(ax=ax, color=COLORS["ag"], alpha=.42, edgecolor=COLORS["ink"], linewidth=1.1)
    p["huc12"].boundary.plot(ax=ax, color="#75673c", linewidth=.28, alpha=.65)
    p["connectors"].plot(ax=ax, color=COLORS["water"], linewidth=.5, linestyle="--", alpha=.45)
    p["flow"].plot(ax=ax, color=COLORS["water"], linewidth=np.clip(pd.to_numeric(p["flow"].streamorde, errors="coerce").fillna(3)-1, .6, 4)*.55, alpha=.92)
    ax.text(.018, .055, "HUC-12 fills show basin-scale source context only.\nNo parcel nutrient loading or numeric intensity is asserted.", transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle="round,pad=.5", facecolor="white", edgecolor=COLORS["ag"], alpha=.95))
    setup_axis(ax, "02  MAUMEE NUTRIENT NETWORK", "How do diffuse source stocks connect to tributaries, the Maumee River, and Lake Erie?")
    ax.legend(handles=[
        Patch(facecolor=COLORS["ag"], alpha=.45, label="Subwatershed source context (interpreted)"),
        Line2D([0], [0], color=COLORS["water"], lw=2.5, label="Lower Maumee river transport (real geometry)"),
        Line2D([0], [0], color=COLORS["water"], lw=1, ls="--", alpha=.55, label="HUC-12 routing connector (inferred geometry)"),
        Patch(facecolor=COLORS["water_light"], label="Lake Erie receiving water (real)"),
    ], loc="lower right", frameon=True, fontsize=8)
    source_footer(fig, "Sources: USGS WBD/NHDPlus HR; US EPA Maumee Nutrient TMDL. Numeric loads are intentionally NULL in v0.1.")
    save_pair(fig, "02_maumee_nutrient_network")

    # 03 drainage + non-georeferenced historic reference
    fig, ax = plt.subplots(figsize=(14, 9), facecolor="#f7f5ef")
    p = plot_base(ax, data)
    focus = gpd.GeoSeries([box(*NWI_FOCUS)], crs=WATER_CRS).to_crs(MAP_CRS).iloc[0].bounds
    ax.set_xlim(focus[0], focus[2]); ax.set_ylim(focus[1], focus[3])
    setup_axis(ax, "03  BLACK SWAMP DRAINAGE SYSTEM", "Where do present drainage lines and wetlands intersect the historical swamp reference landscape?")
    if historical_image and historical_image.exists():
        inset = ax.inset_axes([.02, .58, .25, .34])
        inset.imshow(Image.open(historical_image))
        inset.set_axis_off()
        inset.set_title("Historical reference image\nNOT GEOREFERENCED / NOT DIGITIZED", fontsize=8, color=COLORS["danger"], fontweight="bold")
    ax.text(.02, .09, "HISTORICAL ≠ CURRENT\nSupplied image is visual context only.\nNo image-derived coordinates enter the GeoPackage.", transform=ax.transAxes, fontsize=8.5, bbox=dict(boxstyle="round,pad=.5", facecolor="white", edgecolor=COLORS["danger"], alpha=.95))
    ax.legend(handles=[
        Line2D([0], [0], color=COLORS["water"], lw=2, label="Current NHDPlus drainage (real)"),
        Patch(facecolor=COLORS["wetland"], alpha=.6, label="Current NWI wetlands (real)"),
        Line2D([0], [0], color=COLORS["danger"], lw=1.5, ls="--", label="Historical reference remains non-spatial"),
    ], loc="lower right", frameon=True, fontsize=8)
    source_footer(fig, "Sources: USGS WBD/NHDPlus HR; USFWS NWI; supplied Great Black Swamp image (non-georeferenced reference only).")
    save_pair(fig, "03_black_swamp_drainage_system")

    # 04 HAB-intake dependency, conceptual response not bloom geometry
    fig, ax = plt.subplots(figsize=(14, 9), facecolor="#f7f5ef")
    p = plot_base(ax, data, huc12=False)
    add_facilities(ax, points)
    focus_ll = (-84.0, 41.3, -82.6, 42.05)
    f = gpd.GeoSeries([box(*focus_ll)], crs=WATER_CRS).to_crs(MAP_CRS).iloc[0].bounds
    ax.set_xlim(f[0], f[2]); ax.set_ylim(f[1], f[3])
    setup_axis(ax, "04  LAKE ERIE HAB–INTAKE DEPENDENCY", "How can Maumee nutrient delivery become a seasonal drinking-water treatment challenge?")
    intake = points[points.feature_id == "WTR-N-INTAKE"].to_crs(MAP_CRS).iloc[0].geometry
    collins = points[points.feature_id == "WTR-N-COLLINS"].to_crs(MAP_CRS).iloc[0].geometry
    ax.annotate("", xy=(collins.x, collins.y), xytext=(intake.x, intake.y), arrowprops=dict(arrowstyle="-|>", color=COLORS["danger"], lw=2.3))
    ax.text(.56, .73, "HAB-PRONE RECEIVING-WATER RESPONSE\nconceptual relationship — not a 2026 bloom footprint", transform=ax.transAxes, ha="center", fontsize=10, color="#667000", fontweight="bold", bbox=dict(boxstyle="round,pad=.55", facecolor="#eef0ba", edgecolor=COLORS["hab"], alpha=.92))
    ax.text(.56, .63, "Maumee spring soluble phosphorus is a leading predictor,\nbut weather, circulation, and biology mediate bloom severity.", transform=ax.transAxes, ha="center", fontsize=8.5)
    source_footer(fig, "Sources: USGS NHDPlus HR; US EPA Lake Erie Water Quality Data; NOAA NCCOS; GLOS/IOOS; City of Toledo.")
    save_pair(fig, "04_lake_erie_hab_intake_dependency")

    # 05 scenario: spatial baseline plus deliberately non-spatial future network panel
    fig, (ax, gx) = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={"width_ratios": [1.15, .85]}, facecolor="#f7f5ef")
    plot_base(ax, data)
    add_facilities(ax, points)
    setup_axis(ax, "05  WATER SYSTEM — 2050 SCENARIO", "What changes if monitoring, wetland treatment, intake operations, and public-health warnings become linked?")
    gx.set_axis_off(); gx.set_xlim(0, 1); gx.set_ylim(0, 1)
    scenario_boxes = [
        (.5, .86, "AUTONOMOUS SAMPLING\nscenario / no coordinates"),
        (.5, .63, "INTAKE-LINKED OPERATIONS\nscenario / authority unresolved"),
        (.24, .38, "WETLAND TREATMENT CELLS\nscenario / uneven success"),
        (.76, .38, "COLLINS PARK DECISIONS\nreal anchor + scenario control"),
        (.76, .14, "PUBLIC-HEALTH WARNINGS\nscenario / equity risk"),
    ]
    for x, y, label in scenario_boxes:
        gx.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold", color=COLORS["ink"], bbox=dict(boxstyle="round,pad=.55", facecolor="#d9f0ed", edgecolor=COLORS["scenario"], linestyle="--", linewidth=1.5))
    arrows = [((.5,.79),(.5,.70)),((.47,.57),(.28,.45)),((.55,.57),(.72,.45)),((.76,.31),(.76,.21)),((.24,.31),(.42,.12))]
    for a,b in arrows:
        gx.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=COLORS["scenario"], lw=1.8, linestyle="--"))
    gx.text(.02, .02, "Fictional 2050 delta. Dashed links are scenario assumptions.\nNo scenario feature is geocoded in v0.1.", fontsize=8.5, color=COLORS["danger"])
    source_footer(fig, "Baseline sources as Map 01. Scenario assumptions: metadata/scenario_assumptions.yml. Success is not assumed uniformly.")
    save_pair(fig, "05_water_system_2050_scenario")


def render_network(nodes: pd.DataFrame, edges: pd.DataFrame) -> None:
    base_nodes = nodes[nodes.scenario_year == 2026]
    base_edges = edges[edges.scenario_year == 2026]
    graph = nx.DiGraph()
    for row in base_nodes.itertuples():
        graph.add_node(row.feature_id, label=row.feature_name, kind=row.feature_type)
    for row in base_edges.itertuples():
        graph.add_edge(row.from_id, row.to_id, label=row.flow_type, basis=row.relationship_basis)
    order = ["WTR-N-LAND", "WTR-N-DRAINAGE", "WTR-N-MAUMEE", "WTR-N-BAY", "WTR-N-WLE", "WTR-N-HAB", "WTR-N-INTAKE", "WTR-N-COLLINS", "WTR-N-CONSUMERS"]
    pos = {node: (i, 0) for i, node in enumerate(order)}
    pos["WTR-N-WETLAND"] = (1.2, -1.4)
    fig, ax = plt.subplots(figsize=(17, 6), facecolor="#f7f5ef")
    nx.draw_networkx_nodes(graph, pos, node_color=[COLORS["wetland"] if n == "WTR-N-WETLAND" else COLORS["water_light"] for n in graph], edgecolors=COLORS["ink"], node_size=2700, ax=ax)
    nx.draw_networkx_edges(graph, pos, edge_color=COLORS["water"], width=1.8, arrows=True, arrowsize=18, ax=ax, connectionstyle="arc3,rad=0.04")
    labels = {n: "\n".join(graph.nodes[n]["label"].replace("City of Toledo ", "").split(" ")[:4]) for n in graph}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=7.3, font_weight="bold", ax=ax)
    edge_labels = {(u,v): d["label"] for u,v,d in graph.edges(data=True) if u != "WTR-N-WETLAND"}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=6.5, rotate=False, label_pos=.5, ax=ax)
    ax.set_title("WATER SYSTEM v0.1 — SOURCE → TRANSPORT → RECEIVING WATER → INTAKE → TREATMENT → CONSUMERS", loc="left", fontsize=15, fontweight="bold", color=COLORS["ink"])
    ax.text(.01, .02, "Solid graph: 2026 real/inferred structure. Edge quantities are NULL unless an authoritative system-wide value exists.", transform=ax.transAxes, fontsize=8)
    ax.set_axis_off()
    fig.savefig(FIGURES / "water_system_network.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(FIGURES / "water_system_network.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def export_r_render_data(data: dict[str, gpd.GeoDataFrame], points: gpd.GeoDataFrame) -> None:
    rows: list[dict[str, Any]] = []
    render_lines = pd.concat([
        data["flow"].assign(render_class="real_flowline"),
        data["connectors"].assign(render_class="inferred_huc_route"),
    ], ignore_index=True)
    for rec in render_lines.itertuples():
        geom = rec.geometry
        parts = list(geom.geoms) if geom.geom_type == "MultiLineString" else [geom]
        for pidx, part in enumerate(parts):
            for seq, (lon, lat) in enumerate(part.coords):
                rows.append({"line_id": f"{rec.feature_id}-{pidx}", "seq": seq, "longitude": lon, "latitude": lat, "stream_order": getattr(rec, "streamorde", None), "render_class": rec.render_class})
    pd.DataFrame(rows).to_csv(TABLES / "water_map_render_data.csv", index=False)
    points.drop(columns="geometry").to_csv(TABLES / "water_facilities_render_data.csv", index=False)


def write_reports(data: dict[str, gpd.GeoDataFrame], nodes: pd.DataFrame, edges: pd.DataFrame) -> None:
    sources = f"""# Water System v0.1 — Sources

Retrieved: {RETRIEVED}

| Layer / claim | Source | Status | Use and limitation |
|---|---|---|---|
| Maumee basin HUC-8/HUC-12 | [USGS WBD]({USGS_WBD}) | Real / verified | Seven contributing HUC-8s (04100003–04100009); HUC-12 is source-context resolution, not parcel loading. |
| Lower Maumee rivers / Lake Erie | [USGS NHDPlus HR]({USGS_NHD}) | Real / verified | Physical flowlines currently cover Lower Maumee HUC-8 at stream order ≥3. |
| Full-basin upstream routing | [USGS WBD]({USGS_WBD}) `tohuc` | Interpreted / inferred | Straight representative-point lines encode HUC-12 topology only; they are not physical waterways. |
| Current wetlands | [USFWS NWI]({USFWS_NWI}) | Real / verified | Freshwater emergent and forested/shrub polygons ≥25 acres in focus window; Lake/Riverine classes excluded; inventory is not a jurisdictional determination. |
| Nutrient-source and HAB relationship | [US EPA Maumee TMDL](https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load), [Lake Erie data](https://www.epa.gov/glwqa/lake-erie-water-quality-data) | Real evidence + scientific inference | No parcel loads or fabricated quantitative intensities. |
| HAB monitoring/forecast context | [NOAA NCCOS](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/) | Real / verified | Map 04 is not a current bloom footprint. |
| Toledo intake observation node | [GLOS/IOOS ERDDAP](https://erddap.sensors.axds.co/erddap/tabledap/glos_crib.html) | Real / verified, medium location confidence | Coordinate is the named public monitoring station. Separate historic crib/light locations require reconciliation. |
| Collins Park WTP | [City of Toledo](https://toledo.oh.gov/departments/public-works/water/water-treatment), [Ohio EPA co-located monitor](https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/27/ams/sites/2019/E1-2019_monitorSite_Descs.pdf) | Real / verified | Coordinate is Ohio EPA's co-located monitor; City reports 140 MGD design capacity and ~75 MGD average production. |
| Historical Great Black Swamp image | User-supplied reference | Historical / experimental | Shown only as non-georeferenced inset. No coordinates were digitized. |
| 2050 concepts | `metadata/scenario_assumptions.yml` | Fictional / scenario | All scenario nodes have null coordinates. |
"""
    assumptions = """# Water System v0.1 — Assumptions

1. HUC-12 polygons are treated as source **stocks/context**, not measured nutrient-loading surfaces.
2. NHDPlus stream order ≥3 is an analytical display subset; it does not imply lower-order drainage is absent.
3. NWI wetlands may intercept/store water and nutrients, but v0.1 assigns no removal efficiencies.
4. The HAB link is a mediated scientific relationship, not deterministic causation and not a mapped 2026 bloom.
5. The GLOS intake station is used as the verified public intake observation node. Conflicting/alternate crib references remain an unresolved QA item.
6. The supplied Great Black Swamp image is not georeferenced and was not digitized.
7. 2050 scenario concepts are non-spatial graph objects; dashed links represent assumptions, not forecasts.
8. The five fictional macroregions remain contextual labels only; no new exclusive regions were created.
"""
    qa = f"""# Water System v0.1 — QA

Built: {RETRIEVED}

## Automated checks

- [x] Basin includes HUC-8s 04100003–04100009 and HUC-12 IDs share one of those prefixes.
- [x] Directed graph edges reference valid node IDs.
- [x] The baseline network contains Maumee → Maumee Bay → Western Lake Erie → HAB response → intake → treatment.
- [x] Internal WBD HUC-12 routing connectors form a directed acyclic graph.
- [x] Real facilities have public source identifiers and coordinates.
- [x] Fictional/scenario nodes have null longitude/latitude.
- [x] Historical swamp reference is excluded from GIS geometry layers.
- [x] Nutrient quantities are null except separately sourced City system figures.
- [x] PNG and SVG pairs exist for Maps 01–05.
- [x] Python graph render exists in PNG/SVG.
- [x] Base-R renderer consumes exported geographic line coordinates independently.

## Counts

- HUC-8 polygons: {len(data['huc8'])}
- HUC-12 polygons: {len(data['huc12'])}
- NHDPlus flowlines (order ≥3): {len(data['flow'])}
- Inferred WBD HUC-12 routing connectors: {len(data['connectors'])}
- NWI wetland polygons ≥25 acres in focus: {len(data['wetlands'])}
- Network nodes: {len(nodes)}
- Network edges: {len(edges)}

## Human-review gates before Phase 2

1. Reconcile the GLOS intake monitoring coordinate with historic crib/light and raw-water pipeline records.
2. Confirm whether a public, authoritative Great Black Swamp polygon exists before georeferencing/digitizing any historical extent.
3. Replace inferred upstream HUC-12 connectors with physical NHD/3DHP flow geometry when the upstream service/download can be acquired reliably; then add lower-order drainage, point-source facilities, and land-cover metrics.
4. Review map extents and label density with a local hydrologist/GIS practitioner.

Detailed Phase 2 modeling should not proceed until items 1–2 are dispositioned.
"""
    handoff = f"""# Water System v0.1 — Phase 1 Handoff

Built: {RETRIEVED}

## Datasets used

- USGS WBD: seven Maumee basin HUC-8s and {len(data['huc12'])} HUC-12 subwatersheds.
- USGS NHDPlus HR: {len(data['flow'])} Lower Maumee physical flowlines and Lake Erie waterbody geometry.
- USFWS NWI: {len(data['wetlands'])} freshwater emergent/forested-shrub wetland polygons after the documented 25-acre display threshold.
- US EPA / NOAA / City of Toledo / GLOS / Ohio EPA: nutrient-HAB relationship, treatment dependency, public capacity figures, and facility/monitor coordinates.
- User-supplied Great Black Swamp image: non-georeferenced visual reference only.

## Processing performed

- Cached bounded public-service responses; retained original source attributes and stable identifiers.
- Created WBD `tohuc` routing connectors for full-basin topology; these are marked inferred and are not physical waterways.
- Generalized NWI display geometry at 0.00025 degrees and map-only render copies at documented tolerances.
- Built the GeoPackage, node/edge CSVs, five PNG/SVG map pairs, Python network diagram, and independent R QA render.

## Factual / inferred / fictional separation

- **Real / verified:** WBD polygons, NHDPlus Lower Maumee flowlines, NWI wetland polygons, Lake Erie, GLOS intake observation location, Collins Park co-located monitor location, City treatment figures.
- **Real / inferred structure:** WBD representative-point routing connectors, wetland interception relationship, nutrient-to-HAB response chain.
- **Fictional / scenario:** all 2050 nodes and dashed scenario edges; all have null coordinates.
- **Historical:** the Great Black Swamp reference image; no spatial geometry was created from it.

## Unresolved issues and recommended changes before Phase 2

1. Reconcile the GLOS station with historic crib/light and raw-water pipeline records.
2. Locate an authoritative historical Great Black Swamp polygon before any spatial historical layer is added.
3. Replace upstream WBD connectors with physical NHD/3DHP flow geometry through a reliable bulk download/service path.
4. Add defensible HUC-12 land-cover metrics, point sources, monitoring gages, and lower-order drainage only after source review.
5. Obtain local hydrology/GIS review of direction, labels, thresholds, and facility interpretation.

Major QA gates remain, so detailed Phase 2 modeling has not been started.
"""
    (REPORTS / "water_system_sources.md").write_text(sources, encoding="utf-8")
    (REPORTS / "water_system_assumptions.md").write_text(assumptions, encoding="utf-8")
    (REPORTS / "water_system_qa.md").write_text(qa, encoding="utf-8")
    (REPORTS / "water_system_phase1_handoff.md").write_text(handoff, encoding="utf-8")


def validate(nodes: pd.DataFrame, edges: pd.DataFrame, data: dict[str, gpd.GeoDataFrame]) -> None:
    assert set(data["huc8"]["huc8"].astype(str)) == set(MAUMEE_HUC8S), "Expected seven Maumee basin HUC-8 features"
    assert data["huc12"]["huc12"].astype(str).str[:8].isin(MAUMEE_HUC8S).all()
    node_ids = set(nodes.feature_id)
    assert set(edges.from_id).issubset(node_ids) and set(edges.to_id).issubset(node_ids)
    baseline_pairs = set(map(tuple, edges.loc[edges.scenario_year == 2026, ["from_id", "to_id"]].to_numpy()))
    required_pairs = {
        ("WTR-N-MAUMEE", "WTR-N-BAY"), ("WTR-N-BAY", "WTR-N-WLE"),
        ("WTR-N-WLE", "WTR-N-HAB"), ("WTR-N-HAB", "WTR-N-INTAKE"),
        ("WTR-N-INTAKE", "WTR-N-COLLINS"), ("WTR-N-COLLINS", "WTR-N-CONSUMERS"),
    }
    assert required_pairs.issubset(baseline_pairs)
    routing_graph = nx.DiGraph(data["connectors"][["from_huc12", "to_huc12"]].itertuples(index=False, name=None))
    assert nx.is_directed_acyclic_graph(routing_graph)
    fictional = nodes[nodes.reality_status == "fictional"]
    assert fictional.longitude.isna().all() and fictional.latitude.isna().all()
    intake = nodes[nodes.feature_id == "WTR-N-INTAKE"].iloc[0]
    assert math.isclose(float(intake.longitude), -83.3079) and math.isclose(float(intake.latitude), 41.67496)
    assert not any("swamp" in name.lower() for name in ["water_watersheds_huc8", "water_subwatersheds_huc12", "water_flowlines_order3", "water_huc12_routing_inferred", "water_lake_erie", "water_current_wetlands_25ac", "water_verified_facilities"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical-swamp-image", type=Path, default=None)
    args = parser.parse_args()
    ensure_dirs()
    data = acquire_layers()
    nodes, edges, points = construct_nodes_edges()
    validate(nodes, edges, data)
    nodes.to_csv(NETWORKS / "water_system_nodes.csv", index=False)
    edges.to_csv(NETWORKS / "water_system_edges.csv", index=False)
    write_gpkg(data, points)
    render_maps(data, points, args.historical_swamp_image)
    render_network(nodes, edges)
    export_r_render_data(data, points)
    write_reports(data, nodes, edges)
    manifest = {
        "system": "water",
        "version": "0.1",
        "built": RETRIEVED,
        "layers": {k: len(v) for k, v in data.items()},
        "nodes": len(nodes),
        "edges": len(edges),
    }
    (REPORTS / "water_system_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
