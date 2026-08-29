"""Build the Phase 2A geology and strategic-materials 2026 baseline.

This builder adds Phase 2A layers to the shared GeoPackage without deleting or
rewriting any validated Phase 1 water layer. It renders only Map 06. Facility
coordinates are reproducible address-geocoder results from official addresses;
they are never estimated by the model.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import pyogrio
import requests
from shapely.geometry import Point, box


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MAPS = ROOT / "outputs" / "maps" / "systems"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "reports"
GPKG = PROCESSED / "glasspunk_base.gpkg"
RETRIEVED = date.today().isoformat()

ODNR_BEDROCK = "https://gis2.ohiodnr.gov/arcgis/rest/services/DNR_Services/SUBSURFACE/MapServer/5"
CENSUS_TRANSPORT = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer"
CENSUS_PLACES = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer"
ARCGIS_GEOCODER = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"
FOCUS = (-83.95, 41.12, -82.72, 41.82)
MAP_CRS = "EPSG:5070"

ODNR_SOURCE = "Ohio Department of Natural Resources, Bedrock Type"
ODNR_SOURCE_URL = "https://gis2.ohiodnr.gov/arcgis/rest/services/DNR_Services/SUBSURFACE/MapServer/5"
GEOCODER_NOTE = "Coordinate from ArcGIS World Geocoder using the cited official facility address; not AI-generated."

COMMON_FIELDS = [
    "resource_class",
    "supply_chain_role",
    "local_resource",
    "reality_status",
    "canon_status",
    "source_name",
    "source_url_or_identifier",
    "retrieved_date",
    "confidence",
    "notes",
]

FACILITIES = [
    {
        "feature_id": "MAT-IND-WOODVILLE-MM",
        "feature_name": "Martin Marietta Woodville Lime Facility",
        "operator": "Martin Marietta",
        "address": "755 Lime Rd, Woodville, OH 43469",
        "longitude": -83.366181833374,
        "latitude": 41.465048865166,
        "geocode_score": 100.0,
        "geocode_type": "PointAddress",
        "layer": "industrial_mineral_sites",
        "resource_class": "lime",
        "supply_chain_role": "primary_processing",
        "local_resource": True,
        "source_name": "Martin Marietta Woodville Lime Facility",
        "source_url_or_identifier": "https://www.martinmarietta.com/locations/specialty-products/lime/lime",
        "dataset_date": "2026 current page; facility operations corroborated by 2024 sustainability report",
        "spatial_resolution": "point-address geocode",
        "terms": "public company webpage",
        "confidence": "high",
        "notes": "Woodville carbonate processing; company documentation describes dolomitic limestone feed and lime kilns. Co-located quarry/extraction context is supported by ODNR's 2021 mineral-industries map. " + GEOCODER_NOTE,
    },
    {
        "feature_id": "MAT-IND-WOODVILLE-AREA",
        "feature_name": "Area Aggregates Woodville Plant",
        "operator": "Area Aggregates / The Olen Corporation",
        "address": "659 N Anderson Rd, Woodville, OH 43469",
        "longitude": -83.357258672099,
        "latitude": 41.440421365979,
        "geocode_score": 99.55,
        "geocode_type": "StreetAddress",
        "layer": "industrial_mineral_sites",
        "resource_class": "limestone",
        "supply_chain_role": "extraction",
        "local_resource": True,
        "source_name": "Ohio EPA NPDES permit 2IJ00028 and Kokosing/Olen specialty aggregate page",
        "source_url_or_identifier": "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf",
        "dataset_date": "permit effective 2022-01-01 through 2026-12-31",
        "spatial_resolution": "street-address geocode",
        "terms": "public agency permit and public company webpage",
        "confidence": "medium",
        "notes": "Active 2026 permit at the official address; current company materials describe Woodville agricultural lime and filter sand. Street-address, rather than parcel/entrance, resolution. " + GEOCODER_NOTE,
    },
    {
        "feature_id": "MAT-IND-GENOA-GRAYMONT",
        "feature_name": "Graymont Genoa Plant",
        "operator": "Graymont",
        "address": "21880 W State Route 163, Genoa, OH 43430",
        "longitude": -83.355189973188,
        "latitude": 41.515270001961,
        "geocode_score": 100.0,
        "geocode_type": "PointAddress",
        "layer": "industrial_mineral_sites",
        "resource_class": "lime",
        "supply_chain_role": "primary_processing",
        "local_resource": True,
        "source_name": "Graymont Genoa facility and solutions pages",
        "source_url_or_identifier": "https://www.graymont.com/contact-us/",
        "dataset_date": "2026 current pages",
        "spatial_resolution": "point-address geocode",
        "terms": "public company webpage",
        "confidence": "high",
        "notes": "Genoa lime manufacture from high-purity dolomitic limestone. The facility is part of the local carbonate system, but this phase does not establish a verified site-specific feed route or source quarry. " + GEOCODER_NOTE,
    },
    {
        "feature_id": "MAT-STR-ELMORE-MATERION",
        "feature_name": "Materion Elmore Advanced Materials Facility",
        "operator": "Materion",
        "address": "14710 W Portage River South Rd, Elmore, OH 43416",
        "longitude": -83.215860027455,
        "latitude": 41.491149985926,
        "geocode_score": 100.0,
        "geocode_type": "PointAddress",
        "layer": "strategic_material_sites",
        "resource_class": "beryllium",
        "supply_chain_role": "advanced_processing",
        "local_resource": False,
        "source_name": "Materion Elmore facility documentation and USGS Mineral Commodity Summaries 2026",
        "source_url_or_identifier": "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-beryllium.pdf",
        "dataset_date": "2026",
        "spatial_resolution": "point-address geocode",
        "terms": "public-domain USGS report; public company and EPA documentation",
        "confidence": "high",
        "notes": "Advanced beryllium materials processing, not a beryllium mine. USGS documents Utah extraction/imported beryl followed by shipment of intermediate material to Ohio; local_resource is therefore false. " + GEOCODER_NOTE,
    },
    {
        "feature_id": "MAT-LEG-LUCKEY-FUSRAP",
        "feature_name": "Luckey FUSRAP Site",
        "operator": "U.S. Army Corps of Engineers",
        "address": "21200 Luckey Rd, Luckey, OH 43443",
        "longitude": -83.490434663133,
        "latitude": 41.458801748910,
        "geocode_score": 100.0,
        "geocode_type": "PointAddress",
        "layer": "legacy_remediation_sites",
        "resource_class": "remediation",
        "supply_chain_role": "legacy_cleanup",
        "local_resource": False,
        "source_name": "U.S. Army Corps of Engineers Luckey Site",
        "source_url_or_identifier": "https://www.lrd.usace.army.mil/Missions/Projects/Article/3613204/luckey-site/",
        "dataset_date": "page updated 2026-07-16",
        "spatial_resolution": "point-address geocode",
        "terms": "public federal webpage",
        "confidence": "high",
        "notes": "Active FUSRAP remediation of historical magnesium/beryllium-era contamination; not active strategic-material production. " + GEOCODER_NOTE,
    },
]


def ensure_dirs() -> None:
    for path in [RAW / "ohiodnr", RAW / "census", RAW / "facilities", PROCESSED, MAPS, FIGURES, TABLES, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def arcgis_geojson(
    url: str,
    *,
    where: str,
    out_fields: str,
    cache: Path,
    geometry: str | None = None,
    page_size: int = 1000,
) -> gpd.GeoDataFrame:
    """Download a bounded ArcGIS layer as cached GeoJSON."""
    if cache.exists():
        return gpd.read_file(cache)
    features: list[dict[str, Any]] = []
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
            params.update({
                "geometry": geometry,
                "geometryType": "esriGeometryEnvelope",
                "inSR": 4326,
                "spatialRel": "esriSpatialRelIntersects",
            })
        response = requests.get(f"{url}/query", params=params, timeout=180)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(f"ArcGIS query failed for {url}: {payload['error']}")
        batch = payload.get("features", [])
        features.extend(batch)
        if len(batch) < page_size:
            break
        offset += len(batch)
        if offset > 50_000:
            raise RuntimeError("ArcGIS pagination exceeded safety limit")
    cache.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    if not features:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    return gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")


def normalize(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    frame = frame.copy()
    frame.columns = [str(column).split(".")[-1].lower() for column in frame.columns]
    return frame


def add_geology_fields(frame: gpd.GeoDataFrame, resource_class: pd.Series | str) -> gpd.GeoDataFrame:
    frame = frame.copy()
    frame["feature_id"] = "MAT-GEO-" + frame["objectid"].astype(str)
    frame["feature_name"] = frame.get("unit_name", pd.Series("Bedrock unit", index=frame.index)).fillna("Bedrock unit")
    frame["system_id"] = "SYS-MATERIALS"
    frame["resource_class"] = resource_class
    frame["supply_chain_role"] = "geologic_occurrence"
    frame["local_resource"] = True
    frame["reality_status"] = "real"
    frame["canon_status"] = "verified"
    frame["source_name"] = ODNR_SOURCE
    frame["source_url_or_identifier"] = ODNR_SOURCE_URL
    frame["retrieved_date"] = RETRIEVED
    frame["dataset_date"] = "2006 compilation; source quadrangles largely 1989-1998"
    frame["spatial_resolution"] = "1:500,000 statewide compilation"
    frame["terms"] = "public Ohio DNR service; source credit retained"
    frame["confidence"] = "high"
    frame["notes"] = "Regional bedrock occurrence, not a reserve or production estimate."
    return frame


def acquire_geology() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    bedrock = normalize(arcgis_geojson(
        ODNR_BEDROCK,
        where="1=1",
        out_fields="OBJECTID,UNIT_CODE,AAPG_CD,CSDCODE,UNIT_NAME,UNIT_AGE,UNIT_LITH,UNIT_DESCRIPTION,GlobalID",
        geometry=",".join(map(str, FOCUS)),
        cache=RAW / "ohiodnr" / "bedrock_type_western_basin.geojson",
    ))
    bedrock = gpd.clip(bedrock, box(*FOCUS))
    bedrock = bedrock[~bedrock.geometry.is_empty & bedrock.geometry.notna()].copy()
    combined = (
        bedrock.get("unit_name", "").fillna("").astype(str) + " "
        + bedrock.get("unit_lith", "").fillna("").astype(str) + " "
        + bedrock.get("unit_description", "").fillna("").astype(str)
    ).str.lower()
    full_class = pd.Series(np.where(combined.str.contains("dolomit"), "dolomite", np.where(combined.str.contains("limestone|carbonate"), "limestone", "other_bedrock")), index=bedrock.index)
    bedrock = add_geology_fields(bedrock, full_class)
    carbonate = bedrock[combined.str.contains("limestone|dolomit|carbonate")].copy()
    carbonate["feature_id"] = carbonate["feature_id"].str.replace("MAT-GEO-", "MAT-CARB-", regex=False)
    return bedrock, carbonate


def acquire_orientation() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    envelope = ",".join(map(str, FOCUS))
    primary = normalize(arcgis_geojson(
        f"{CENSUS_TRANSPORT}/2",
        where="1=1",
        out_fields="*",
        geometry=envelope,
        cache=RAW / "census" / "tigerweb_primary_roads.geojson",
    ))
    secondary = normalize(arcgis_geojson(
        f"{CENSUS_TRANSPORT}/6",
        where="1=1",
        out_fields="*",
        geometry=envelope,
        cache=RAW / "census" / "tigerweb_secondary_roads.geojson",
    ))
    places = normalize(arcgis_geojson(
        f"{CENSUS_PLACES}/4",
        where="STATE='39'",
        out_fields="*",
        geometry=envelope,
        cache=RAW / "census" / "tigerweb_incorporated_places.geojson",
    ))
    return primary, secondary, places


def facility_layers() -> dict[str, gpd.GeoDataFrame]:
    table = pd.DataFrame(FACILITIES)
    table["system_id"] = "SYS-MATERIALS"
    table["reality_status"] = "real"
    table["canon_status"] = "verified"
    table["retrieved_date"] = RETRIEVED
    table["location_source_name"] = "ArcGIS World Geocoder"
    table["location_source_url"] = ARCGIS_GEOCODER
    table.to_csv(RAW / "facilities" / "facility_geocodes_2026.csv", index=False)
    geodata = gpd.GeoDataFrame(
        table,
        geometry=gpd.points_from_xy(table.longitude, table.latitude),
        crs="EPSG:4326",
    )
    return {name: geodata[geodata.layer == name].drop(columns=["layer"]).copy() for name in table.layer.unique()}


def write_layers(layers: dict[str, gpd.GeoDataFrame]) -> None:
    before = set(pyogrio.list_layers(GPKG)[:, 0])
    water_layers = {name for name in before if name.startswith("water_")}
    for name, frame in layers.items():
        pyogrio.write_dataframe(frame, GPKG, layer=name, driver="GPKG", append=False)
    after = set(pyogrio.list_layers(GPKG)[:, 0])
    if not water_layers.issubset(after):
        raise RuntimeError("Phase 1 layer preservation check failed")


def export_render_tables(carbonate: gpd.GeoDataFrame, facilities: dict[str, gpd.GeoDataFrame]) -> None:
    all_sites = pd.concat([frame.drop(columns="geometry") for frame in facilities.values()], ignore_index=True)
    all_sites.to_csv(TABLES / "materials_sites_render_data.csv", index=False)
    rows: list[dict[str, Any]] = []
    for _, feature in carbonate.to_crs(4326).iterrows():
        geometry = feature.geometry
        polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
        for part_number, polygon in enumerate(polygons):
            for vertex_number, (lon, lat) in enumerate(polygon.exterior.coords):
                rows.append({
                    "feature_id": feature.feature_id,
                    "part": part_number,
                    "seq": vertex_number,
                    "longitude": lon,
                    "latitude": lat,
                    "resource_class": feature.resource_class,
                })
    pd.DataFrame(rows).to_csv(TABLES / "materials_carbonate_render_data.csv", index=False)


def _bedrock_color(text: str) -> str:
    value = str(text).lower()
    if "shale" in value:
        return "#b5a7a0"
    if "sandstone" in value:
        return "#d9c99d"
    if "dolomit" in value:
        return "#c9b677"
    if "limestone" in value:
        return "#d8c993"
    return "#d8d4c7"


def render_map(
    bedrock: gpd.GeoDataFrame,
    carbonate: gpd.GeoDataFrame,
    facilities: dict[str, gpd.GeoDataFrame],
    roads_primary: gpd.GeoDataFrame,
    roads_secondary: gpd.GeoDataFrame,
    places: gpd.GeoDataFrame,
) -> None:
    layers = set(pyogrio.list_layers(GPKG)[:, 0])
    flow = pyogrio.read_dataframe(GPKG, layer="water_flowlines_order3") if "water_flowlines_order3" in layers else gpd.GeoDataFrame(geometry=[], crs=4326)
    lake = pyogrio.read_dataframe(GPKG, layer="water_lake_erie") if "water_lake_erie" in layers else gpd.GeoDataFrame(geometry=[], crs=4326)

    bedrock_p = bedrock.to_crs(MAP_CRS)
    carbonate_p = carbonate.to_crs(MAP_CRS)
    primary_p = roads_primary.to_crs(MAP_CRS)
    secondary_p = roads_secondary.to_crs(MAP_CRS)
    places_p = places.to_crs(MAP_CRS)
    flow_p = flow.to_crs(MAP_CRS) if not flow.empty else flow
    lake_p = lake.to_crs(MAP_CRS) if not lake.empty else lake
    facility_p = {name: frame.to_crs(MAP_CRS) for name, frame in facilities.items()}
    focus_p = gpd.GeoSeries([box(*FOCUS)], crs=4326).to_crs(MAP_CRS).iloc[0]

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    fig = plt.figure(figsize=(16, 10), facecolor="#f3efe5")
    ax = fig.add_axes([0.035, 0.08, 0.74, 0.84], facecolor="#eee9dc")
    panel = fig.add_axes([0.79, 0.08, 0.185, 0.84], facecolor="#e7e0d2")
    panel.set_xticks([])
    panel.set_yticks([])
    for spine in panel.spines.values():
        spine.set_color("#8b7f6b")

    bedrock_p.plot(ax=ax, color=[_bedrock_color(value) for value in bedrock_p.get("unit_lith", "")], edgecolor="#a39a89", linewidth=0.25, alpha=0.72, zorder=1)
    carbonate_p.plot(ax=ax, color="#d4bc69", edgecolor="#8c6f2e", linewidth=0.65, alpha=0.45, zorder=2)
    if not lake_p.empty:
        lake_p.plot(ax=ax, color="#a8cee1", edgecolor="#5d97b2", linewidth=0.7, zorder=3)
    secondary_p.plot(ax=ax, color="#9b968b", linewidth=0.28, alpha=0.45, zorder=4)
    primary_p.plot(ax=ax, color="#6f6b63", linewidth=0.7, alpha=0.65, zorder=5)
    if not flow_p.empty:
        flow_p.plot(ax=ax, color="#4f96b4", linewidth=0.45, alpha=0.8, zorder=6)

    styles = {
        "industrial_mineral_sites": dict(marker="s", color="#c18d22", edgecolor="#fff7dd", label="Industrial mineral site"),
        "strategic_material_sites": dict(marker="*", color="#8f4f77", edgecolor="white", label="Strategic processing"),
        "legacy_remediation_sites": dict(marker="D", color="#b95142", edgecolor="white", label="Legacy remediation"),
    }
    for name, frame in facility_p.items():
        style = styles[name]
        ax.scatter(frame.geometry.x, frame.geometry.y, s=120 if name != "strategic_material_sites" else 190, marker=style["marker"], c=style["color"], edgecolors=style["edgecolor"], linewidths=1.2, zorder=10)
        for _, row in frame.iterrows():
            label = row.feature_name.replace(" Facility", "").replace(" Site", "")
            ax.annotate(label, (row.geometry.x, row.geometry.y), xytext=(7, 7), textcoords="offset points", fontsize=7.7, color="#18333f", weight="bold", bbox=dict(boxstyle="round,pad=0.18", fc="#f7f2e7", ec="none", alpha=0.82), zorder=11)

    label_names = {"Toledo", "Oregon", "Northwood", "Rossford", "Perrysburg", "Maumee", "Bowling Green", "Woodville", "Elmore", "Luckey", "Genoa", "Oak Harbor", "Port Clinton", "Pemberville", "Walbridge"}
    name_col = next((column for column in ["basename", "name"] if column in places_p.columns), None)
    if name_col:
        for _, row in places_p[places_p[name_col].isin(label_names)].iterrows():
            point = row.geometry.representative_point()
            ax.plot(point.x, point.y, "o", ms=2.4, color="#243b42", zorder=8)
            ax.text(point.x + 1300, point.y - 900, row[name_col], fontsize=6.8, color="#243b42", zorder=8)

    context_labels = [
        ("GLASS CITY CORE", -83.63, 41.64),
        ("MAUMEE RIVER COMMONS", -83.72, 41.39),
        ("LAKE ERIE ENERGY & SECURITY COAST", -83.02, 41.70),
        ("BLACK SWAMP COUNTRY", -83.18, 41.29),
        ("GREAT LAKES INDUSTRIAL BELT", -83.39, 41.59),
    ]
    for label, lon, lat in context_labels:
        point = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(MAP_CRS).iloc[0]
        ax.text(point.x, point.y, label, fontsize=7.2, color="#53656a", alpha=0.42, ha="center", weight="bold", zorder=7)

    ax.set_xlim(focus_p.bounds[0], focus_p.bounds[2])
    ax.set_ylim(focus_p.bounds[1], focus_p.bounds[3])
    ax.set_axis_off()
    ax.set_title("06  GEOLOGY + STRATEGIC MATERIALS — 2026 BASELINE", loc="left", fontsize=19, color="#18333f", pad=13)
    ax.text(0.0, 1.008, "What physical resources and strategic-processing capabilities exist in the Western Basin region in 2026?", transform=ax.transAxes, fontsize=9.5, color="#45565b")

    legend = [
        Patch(facecolor="#d4bc69", edgecolor="#8c6f2e", alpha=0.55, label="Carbonate-bearing bedrock unit"),
        Line2D([0], [0], color="#6f6b63", lw=1.0, label="Census road context"),
        Line2D([0], [0], color="#4f96b4", lw=1.0, label="USGS hydrology context"),
    ]
    legend.extend(Line2D([0], [0], marker=s["marker"], color="none", markerfacecolor=s["color"], markeredgecolor=s["edgecolor"], markersize=8, label=s["label"]) for s in styles.values())
    ax.legend(handles=legend, loc="lower left", frameon=True, facecolor="#f5f0e5", edgecolor="#8b7f6b", fontsize=7.4, ncol=2)

    panel.text(0.08, 0.95, "MATERIAL REALITY CHECK", fontsize=12.5, weight="bold", color="#18333f", va="top")
    panel.text(0.08, 0.895, "LOCAL CARBONATE", fontsize=9.5, weight="bold", color="#8c6f2e")
    panel.text(0.08, 0.855, "Bedrock occurrence supports\nverified extraction and lime\nprocessing near Woodville/Genoa.", fontsize=8.2, color="#33464c", va="top", linespacing=1.35)
    panel.text(0.08, 0.70, "EXTERNAL BERYLLIUM FEED", fontsize=9.5, weight="bold", color="#8f4f77")
    panel.text(0.08, 0.66, "Elmore is an advanced materials\nprocessing site — not a mine.\nRaw beryllium supply is nonlocal.", fontsize=8.2, color="#33464c", va="top", linespacing=1.35)
    panel.text(0.08, 0.50, "LEGACY, NOT PRODUCTION", fontsize=9.5, weight="bold", color="#b95142")
    panel.text(0.08, 0.46, "Luckey is shown for active federal\ncleanup of a historical facility,\nnot current strategic production.", fontsize=8.2, color="#33464c", va="top", linespacing=1.35)
    panel.text(0.08, 0.29, "MAP LIMITS", fontsize=9.5, weight="bold", color="#18333f")
    panel.text(0.08, 0.25, "No reserve or output quantities.\nNo groundwater-flow direction.\nNo speculative corridor polygon.\nNo future scenario. Five-region\nlabels are context only.", fontsize=8.0, color="#33464c", va="top", linespacing=1.32)
    panel.text(0.08, 0.055, "EPSG:5070 • Baseline year 2026", fontsize=7.4, color="#53656a")

    fig.text(0.04, 0.025, "Sources: Ohio DNR Bedrock Type (1:500,000); U.S. Census TIGERweb roads/places; USGS Phase 1 hydrology; official facility, USGS and USACE records. Facility coordinates: address geocoder; precision recorded per feature.", fontsize=7.2, color="#53656a")
    png = MAPS / "06_geology_resources_2026.png"
    svg = MAPS / "06_geology_resources_2026.svg"
    fig.savefig(png, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    bedrock, carbonate = acquire_geology()
    roads_primary, roads_secondary, places = acquire_orientation()
    facilities = facility_layers()
    layers = {
        "geology_bedrock_units": bedrock,
        "geology_carbonate_units": carbonate,
        **facilities,
    }
    write_layers(layers)
    export_render_tables(carbonate, facilities)
    render_map(bedrock, carbonate, facilities, roads_primary, roads_secondary, places)
    summary = {
        "bedrock_units": len(bedrock),
        "carbonate_units": len(carbonate),
        "industrial_mineral_sites": len(facilities["industrial_mineral_sites"]),
        "strategic_material_sites": len(facilities["strategic_material_sites"]),
        "legacy_remediation_sites": len(facilities["legacy_remediation_sites"]),
        "map": str((MAPS / "06_geology_resources_2026.png").relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
