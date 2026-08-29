"""Build the Phase 1 Great Black Swamp geometry review package.

This script intentionally does not write to data/processed/glasspunk_base.gpkg.
It creates a human-review candidate from the official ODNR digitization of
Robert B. Gordon's 1966 vegetation map without tracing, buffering, smoothing,
or manually editing source boundaries.
"""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd
import requests
from shapely import make_valid
from shapely.geometry import mapping
from shapely.ops import unary_union

matplotlib.rcParams["svg.hashsalt"] = "western-basin-phase1-gbs-qa"


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
QA = ROOT / "outputs" / "qa"
QA_DATA = QA / "data"
TMP = ROOT / "tmp" / "great_black_swamp_review"
RETRIEVED = date.today().isoformat()

ODNR_ZIP = RAW / "ohiodnr" / "original_vegetation_ohio" / "OriginalVegetationOhio.zip"
ODNR_URL = "https://gis.ohiodnr.gov/geodata/Statewide/OriginalVegetationOhio.zip"
ODNR_SCALE = 500_000
ODNR_CRS = "EPSG:3734"
MAP_CRS = "EPSG:5070"
OUTPUT_CRS = "EPSG:4326"

WBD_URL = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/4/query"
CENSUS_COUNTY_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"
)
CENSUS_PLACE_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/"
    "TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/4/query"
)

# Hydrologically named selection frame, not a digitized swamp outline. These
# are the seven Maumee HUC8s already used by Phase 1 plus Cedar-Portage, which
# covers the western Lake Erie drainage east of Toledo.
TARGET_HUC8S = tuple(f"0410000{i}" for i in range(3, 10)) + ("04100010",)

VEGETATION_CLASSES = {
    1: ("Beech", "exclude", "upland forest; not swamp evidence"),
    2: ("Mixed Oak", "exclude", "upland forest; not swamp evidence"),
    3: ("Oak-Sugar Maple", "exclude", "upland forest; not swamp evidence"),
    4: (
        "Elm-Ash Swamp Forests",
        "candidate basis",
        "closest source class to presettlement swamp forest; broader than the named Great Black Swamp",
    ),
    5: ("Mixed Mesophytic", "exclude", "upland/mesic forest; not swamp evidence"),
    6: ("Prairie Grasslands", "context only", "may include wet prairie but source class is not swamp-specific"),
    7: ("Oak Savannas", "context only", "important Oak Openings context; not swamp evidence"),
    8: (
        "Freshwater Marshes and Fens",
        "context only",
        "coastal/inland marsh context; excluded to avoid conflating marsh with swamp forest",
    ),
    9: ("Sphagnum Peat Bogs", "exclude", "distinct wetland type"),
    10: (
        "Bottomland Hardwood",
        "context only",
        "floodplain forest context; excluded to avoid conflating river bottoms with the named swamp",
    ),
    11: ("Mixed Mesophytic (special)", "exclude", "special source-map class; not swamp evidence"),
    12: ("White Pine-Red Maple Swamp", "exclude", "single northeastern Ohio class; outside candidate basis"),
    13: ("Beach", "exclude", "shoreline land cover; not swamp evidence"),
}


def ensure_dirs() -> None:
    for path in (REPORTS, QA, QA_DATA, TMP, RAW / "usgs", RAW / "census"):
        path.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def cached_arcgis(url: str, params: dict[str, Any], cache: Path) -> gpd.GeoDataFrame:
    """Read an authoritative ArcGIS query from cache, or save its raw GeoJSON."""
    if cache.exists():
        return gpd.read_file(cache)
    response = requests.get(url, params={**params, "f": "geojson"}, timeout=180)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"ArcGIS query failed: {payload['error']}")
    cache.write_text(json.dumps(payload), encoding="utf-8")
    return gpd.GeoDataFrame.from_features(payload.get("features", []), crs=OUTPUT_CRS)


def load_context() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    huc_where = "huc8 IN (" + ",".join(f"'{h}'" for h in TARGET_HUC8S) + ")"
    hucs = cached_arcgis(
        WBD_URL,
        {
            "where": huc_where,
            "outFields": "huc8,name,areasqkm,states",
            "returnGeometry": "true",
            "outSR": 4326,
        },
        RAW / "usgs" / "wbd_huc8_great_black_swamp_review.geojson",
    )
    counties = cached_arcgis(
        CENSUS_COUNTY_URL,
        {
            "where": "STATE IN ('18','26','39')",
            "outFields": "GEOID,NAME,STATE,BASENAME",
            "returnGeometry": "true",
            "outSR": 4326,
        },
        RAW / "census" / "tigerweb_counties_oh_in_mi.geojson",
    )
    places = cached_arcgis(
        CENSUS_PLACE_URL,
        {
            "where": "STATE IN ('18','26','39')",
            "outFields": "GEOID,NAME,STATE,BASENAME",
            "returnGeometry": "true",
            "outSR": 4326,
            "geometry": "-84.95,40.65,-82.65,42.05",
            "geometryType": "esriGeometryEnvelope",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
        },
        RAW / "census" / "tigerweb_places_great_black_swamp_review.geojson",
    )
    for frame in (hucs, counties, places):
        frame.columns = [str(c).lower() for c in frame.columns]
    return hucs, counties, places


def load_odnr() -> gpd.GeoDataFrame:
    if not ODNR_ZIP.exists():
        raise FileNotFoundError(f"Missing official ODNR archive: {ODNR_ZIP}")
    extract = TMP / "odnr_original_vegetation"
    extract.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ODNR_ZIP) as archive:
        archive.extractall(extract)
    frame = gpd.read_file(extract / "or_veg_spn83.shp")
    if frame.crs is None or frame.crs.to_epsg() != 3734:
        raise AssertionError(f"Expected EPSG:3734, got {frame.crs}")
    frame.columns = [str(c).lower() for c in frame.columns]
    frame["source_feature_id"] = frame["or_veg_s_1"].astype(int)
    return frame


def class_review(source: gpd.GeoDataFrame, hucs: gpd.GeoDataFrame) -> pd.DataFrame:
    projected = source.to_crs(MAP_CRS)
    project_union = hucs.to_crs(MAP_CRS).geometry.union_all()
    source_selection_union = hucs.to_crs(source.crs).geometry.union_all()
    rows: list[dict[str, Any]] = []
    for code, (name, decision, rationale) in VEGETATION_CLASSES.items():
        subset = projected[projected["veg_cde"] == code]
        source_subset = source[source["veg_cde"] == code]
        intersecting = subset[subset.geometry.intersects(project_union)]
        area_in_extent = sum(
            float(geom.intersection(project_union).area) for geom in intersecting.geometry
        ) / 1_000_000
        selected_complete = source_subset[
            source_subset.geometry.representative_point().within(source_selection_union)
        ].to_crs(MAP_CRS)
        rows.append(
            {
                "vegetation_code": code,
                "vegetation_class": name,
                "source_feature_count_statewide": len(subset),
                "feature_count_intersecting_project_extent": len(intersecting),
                "area_in_project_extent_km2": round(area_in_extent, 2),
                "area_of_selected_complete_polygons_km2": (
                    round(float(selected_complete.geometry.area.sum() / 1_000_000), 2)
                    if code == 4
                    else ""
                ),
                "candidate_gbs_component": "yes" if code == 4 else "no",
                "reason": rationale,
                "historical_support": (
                    "Gordon 1966 vegetation association interpreted at time of earliest land surveys"
                ),
                "uncertainty": (
                    "Class is generalized at 1:500,000 and is not itself a named Great Black Swamp boundary"
                ),
                "include_recommendation": decision,
                "source": "ODNR Original Natural Vegetation of Ohio (Gordon 1966 digitization)",
                "source_scale": "1:500,000",
            }
        )
    return pd.DataFrame(rows)


def build_candidate(
    source: gpd.GeoDataFrame, hucs: gpd.GeoDataFrame
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    source_huc = hucs.to_crs(source.crs).geometry.union_all()
    swamp = source[source["veg_cde"] == 4].copy()
    # Representative-point selection prevents tiny boundary slivers from
    # pulling in unrelated statewide polygons. It does not change geometry.
    selected = swamp[swamp.geometry.representative_point().within(source_huc)].copy()
    if selected.empty:
        raise AssertionError("No class-4 source polygons selected")
    selected["selection_rule"] = (
        "VEG_CDE=4 and source-polygon representative point within WBD HUC8 "
        + ",".join(TARGET_HUC8S)
    )
    selected["source_class"] = "Elm-Ash Swamp Forests"
    selected["source_scale"] = "1:500,000"

    source_invalid = int((~selected.geometry.is_valid).sum())
    geometries = [make_valid(geom) if not geom.is_valid else geom for geom in selected.geometry]
    dissolved = unary_union(geometries)
    if not dissolved.is_valid:
        dissolved = make_valid(dissolved)

    candidate = gpd.GeoDataFrame(
        [
            {
                "geometry_id": "great_black_swamp_candidate_gordon1966",
                "geometry_name": "Great Black Swamp review candidate — Gordon 1966 / ODNR class 4",
                "source_dataset": "Ohio DNR Original Natural Vegetation of Ohio; Robert B. Gordon (1966)",
                "source_url": ODNR_URL,
                "historical_period": "time of earliest land surveys; source published 1966",
                "source_scale": "1:500,000",
                "derivation_method": (
                    "Dissolve complete ODNR VEG_CDE=4 polygons whose representative points fall within "
                    "Maumee HUC8s 04100003-04100009 or Cedar-Portage HUC8 04100010; no clipping, "
                    "buffering, smoothing, tracing, or hand editing"
                ),
                "source_authority": "official state digitization of a published historical vegetation interpretation",
                "confidence": "medium for regional swamp-forest footprint; low for a named Great Black Swamp boundary",
                "boundary_uncertainty": "high; vegetation boundaries at 1:500,000 are not a named-swamp survey",
                "class_uncertainty": "medium; Elm-Ash class omits marsh, wet prairie, and bottomland types",
                "interstate_compatibility": "not merged; Indiana and Michigan require class/scale/terms crosswalk",
                "method_status": "resolved",
                "geometry_status": "candidate",
                "canonical_status": "hold",
                "source_gap": "direct official Great Black Swamp geometry or documented derivation remains unresolved",
                "human_review_status": "C — HOLD (recorded 2026-08-29)",
                "notes": "Regional historical reference only; not for parcel, restoration-targeting, or fine-scale hydrology",
                "selection_huc8s": ",".join(TARGET_HUC8S),
                "source_feature_count": len(selected),
                "source_invalid_repaired": source_invalid,
                "retrieved_date": RETRIEVED,
                "geometry": dissolved,
            }
        ],
        geometry="geometry",
        crs=source.crs,
    )
    return selected, candidate


def write_geojson(frame: gpd.GeoDataFrame, path: Path) -> None:
    output = frame.to_crs(OUTPUT_CRS)
    path.write_text(output.to_json(drop_id=True), encoding="utf-8")


def intersection_table(
    candidate: gpd.GeoDataFrame,
    context: gpd.GeoDataFrame,
    id_col: str,
    name_col: str,
) -> pd.DataFrame:
    cand = candidate.to_crs(MAP_CRS).geometry.iloc[0]
    ctx = context.to_crs(MAP_CRS).copy()
    rows = []
    for row in ctx.itertuples():
        overlap = cand.intersection(row.geometry)
        area = overlap.area / 1_000_000
        if area > 0.01:
            rows.append(
                {
                    id_col: getattr(row, id_col),
                    name_col: getattr(row, name_col),
                    "candidate_intersection_km2": round(area, 2),
                }
            )
    return pd.DataFrame(rows).sort_values("candidate_intersection_km2", ascending=False)


def render_map(
    source: gpd.GeoDataFrame,
    selected: gpd.GeoDataFrame,
    candidate: gpd.GeoDataFrame,
    hucs: gpd.GeoDataFrame,
    counties: gpd.GeoDataFrame,
    places: gpd.GeoDataFrame,
) -> None:
    focus = counties.to_crs(MAP_CRS)
    cand = candidate.to_crs(MAP_CRS)
    selected_map = selected.to_crs(MAP_CRS)
    hucs_map = hucs.to_crs(MAP_CRS)
    all_class4 = source[source["veg_cde"] == 4].to_crs(MAP_CRS)
    places_map = places.to_crs(MAP_CRS)
    river_path = RAW / "usgs" / "nhdplus_maumee_order3.geojson"
    lake_path = RAW / "usgs" / "nhd_lake_erie.geojson"
    wetlands_path = RAW / "usfws" / "nwi_nw_ohio_25ac_generalized.geojson"
    river = gpd.read_file(river_path).to_crs(MAP_CRS) if river_path.exists() else None
    lake = gpd.read_file(lake_path).to_crs(MAP_CRS) if lake_path.exists() else None
    wetlands = gpd.read_file(wetlands_path).to_crs(MAP_CRS) if wetlands_path.exists() else None

    minx, miny, maxx, maxy = cand.total_bounds
    pad_x, pad_y = 75_000, 65_000
    extent = (minx - pad_x, maxx + pad_x, miny - pad_y, maxy + pad_y)
    focus = focus.cx[extent[0] : extent[1], extent[2] : extent[3]]
    places_map = places_map.cx[extent[0] : extent[1], extent[2] : extent[3]]

    fig = plt.figure(figsize=(13.5, 9.0), facecolor="#f5f1e6")
    grid = fig.add_gridspec(1, 2, width_ratios=(3.2, 1.25), wspace=0.035)
    ax = fig.add_subplot(grid[0, 0])
    notes = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#e9e5d8")
    focus.plot(ax=ax, color="#f2eee3", edgecolor="#c2b9a5", linewidth=0.55, rasterized=True)
    if lake is not None:
        lake.plot(ax=ax, color="#b9dbe8", edgecolor="#6b9eb2", linewidth=0.7, zorder=1, rasterized=True)
    hucs_map.boundary.plot(ax=ax, color="#6b8fa6", linewidth=1.0, linestyle="--", zorder=2, rasterized=True)
    if wetlands is not None:
        wetlands.plot(ax=ax, color="#78a98c", edgecolor="none", alpha=0.20, zorder=2, rasterized=True)
    all_class4.plot(ax=ax, color="#b9b9ad", edgecolor="#85857e", linewidth=0.25, alpha=0.45, zorder=3, rasterized=True)
    selected_map.plot(ax=ax, color="#6f9773", edgecolor="#355c45", linewidth=0.75, alpha=0.80, zorder=4, rasterized=True)
    cand.boundary.plot(ax=ax, color="#173f2c", linewidth=1.8, zorder=5, rasterized=True)
    if river is not None:
        river.plot(ax=ax, color="#287da2", linewidth=1.0, alpha=0.85, zorder=6, rasterized=True)

    major_places = {
        "Toledo",
        "Bowling Green",
        "Defiance",
        "Findlay",
        "Fremont",
        "Port Clinton",
        "Perrysburg",
        "Maumee",
    }
    label_places = places_map[
        places_map["basename"].isin(major_places) & (places_map["state"].astype(str) == "39")
    ].copy()
    for row in label_places.itertuples():
        point = row.geometry.representative_point()
        ax.plot(point.x, point.y, "o", ms=3.2, color="#24333b", zorder=7)
        ax.annotate(row.basename, (point.x, point.y), xytext=(4, 3), textcoords="offset points", fontsize=8)

    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "Great Black Swamp historical geometry — QA review candidate",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color="#173443",
        pad=14,
    )
    ax.text(
        0,
        1.006,
        "Gordon (1966) / Ohio DNR class 4; source polygons preserved, then dissolved for review",
        transform=ax.transAxes,
        fontsize=9.5,
        color="#4a5a60",
    )
    ax.legend(
        handles=[
            Patch(facecolor="#6f9773", edgecolor="#173f2c", label="Selected Elm–Ash swamp-forest polygons"),
            Patch(facecolor="#b9b9ad", edgecolor="#85857e", alpha=0.45, label="Other statewide class-4 polygons"),
            Line2D([0], [0], color="#6b8fa6", linestyle="--", label="WBD HUC8 selection frame"),
            Line2D([0], [0], color="#287da2", label="Maumee river network"),
            Line2D([0], [0], color="#c2b9a5", label="Census county boundaries"),
        ],
        loc="lower left",
        frameon=True,
        framealpha=0.94,
        fontsize=8.5,
    )
    ax.annotate(
        "N",
        xy=(0.955, 0.91),
        xytext=(0.955, 0.80),
        xycoords="axes fraction",
        arrowprops=dict(facecolor="#173443", width=2.8, headwidth=9),
        ha="center",
        fontsize=10,
        fontweight="bold",
    )

    notes.set_facecolor("#fbf8ef")
    notes.axis("off")
    area = cand.geometry.area.iloc[0] / 1_000_000
    geom = cand.geometry.iloc[0]
    fragments = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1
    note_text = (
        "DECISION STATUS\n"
        "HOLD — not canonical\n\n"
        "WHY THIS CANDIDATE\n"
        "• Official Ohio DNR digitization\n"
        "• Published historical interpretation\n"
        "• Reproducible class + basin rule\n"
        "• No traced image geometry\n\n"
        "IMPORTANT LIMITS\n"
        "• Class 4 is swamp forest, not a named\n  Great Black Swamp boundary\n"
        "• Original scale 1:500,000\n"
        "• Ohio only\n"
        "• Basin selection is analytical\n"
        "• Marsh/prairie/bottomland omitted\n\n"
        f"QA SNAPSHOT\n• Area: {area:,.0f} km²\n"
        f"• Selected source polygons: {len(selected):,}\n"
        f"• Dissolved components: {fragments:,}\n"
        f"• Geometry valid: {'yes' if geom.is_valid else 'NO'}\n"
        f"• Source CRS: {ODNR_CRS}\n"
        f"• Review output: {OUTPUT_CRS}\n\n"
        "HUMAN REVIEW OPTIONS\n"
        "A — accept as canonical\n"
        "B — accept with qualification\n"
        "C — keep HOLD / request agency data\n"
        "D — reject candidate"
    )
    notes.text(0.06, 0.96, note_text, va="top", fontsize=9.3, linespacing=1.35, color="#26383f")
    notes.text(
        0.06,
        0.025,
        "Review artifact only • generated reproducibly • issue remains open",
        fontsize=8,
        color="#7b4b3d",
    )

    fig.savefig(QA / "great_black_swamp_geometry_review.png", dpi=220, bbox_inches="tight")
    svg_path = QA / "great_black_swamp_geometry_review.svg"
    fig.savefig(svg_path, bbox_inches="tight", metadata={"Date": None})
    # Matplotlib writes insignificant line-end spaces in path data. Normalize
    # them so repository whitespace validation remains clean and deterministic.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def write_qa(
    source: gpd.GeoDataFrame,
    selected: gpd.GeoDataFrame,
    candidate: gpd.GeoDataFrame,
    counties: gpd.GeoDataFrame,
    hucs: gpd.GeoDataFrame,
) -> None:
    cand_map = candidate.to_crs(MAP_CRS)
    geom = cand_map.geometry.iloc[0]
    components = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    county_table = intersection_table(candidate, counties, "geoid", "name")
    huc_table = intersection_table(candidate, hucs, "huc8", "name")
    county_table.to_csv(REPORTS / "great_black_swamp_candidate_county_intersections.csv", index=False)
    huc_table.to_csv(REPORTS / "great_black_swamp_candidate_watershed_intersections.csv", index=False)
    qa = {
        "geometry_id": "great_black_swamp_candidate_gordon1966",
        "status": "method_resolved_geometry_candidate_canonical_hold",
        "source_archive": str(ODNR_ZIP.relative_to(ROOT)).replace("\\", "/"),
        "source_archive_sha256": sha256(ODNR_ZIP),
        "source_crs": str(source.crs),
        "source_scale": "1:500,000",
        "output_crs": OUTPUT_CRS,
        "source_feature_count_total": len(source),
        "source_invalid_feature_count_total": int((~source.geometry.is_valid).sum()),
        "selected_source_feature_count": len(selected),
        "selected_invalid_feature_count_before_repair": int((~selected.geometry.is_valid).sum()),
        "candidate_valid": bool(candidate.geometry.is_valid.all()),
        "candidate_empty": bool(candidate.geometry.is_empty.any()),
        "candidate_geometry_type": candidate.geometry.iloc[0].geom_type,
        "candidate_component_count": len(components),
        "candidate_disconnected_fragment_count": max(0, len(components) - 1),
        "candidate_area_km2": round(float(geom.area / 1_000_000), 2),
        "largest_component_km2": round(max(float(g.area) for g in components) / 1_000_000, 2),
        "counties_intersected": len(county_table),
        "watersheds_intersected": len(huc_table),
        "selection_huc8s": list(TARGET_HUC8S),
        "selection_rule": "VEG_CDE=4 and representative point within named target HUC8 union",
        "geometry_operations": ["make_valid only where required", "unary union / dissolve"],
        "prohibited_operations_confirmed_absent": ["image tracing", "georeferencing", "buffer", "smoothing", "hand edit"],
        "retrieved_date": RETRIEVED,
    }
    (REPORTS / "great_black_swamp_geometry_qa.json").write_text(
        json.dumps(qa, indent=2), encoding="utf-8"
    )


def write_manifest() -> None:
    entries = [
        {
            "source": "Ohio DNR Original Natural Vegetation of Ohio",
            "url": ODNR_URL,
            "local_path": str(ODNR_ZIP.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(ODNR_ZIP),
            "retrieved_date": RETRIEVED,
        },
        {
            "source": "H2Ohio History of the Great Black Swamp educational PDF",
            "url": "https://dam.assets.ohio.gov/image/upload/h2.ohio.gov/STA/History_of_the_Great_Black_Swamp.pdf",
            "local_path": "data/raw/h2ohio/History_of_the_Great_Black_Swamp.pdf",
            "sha256": sha256(RAW / "h2ohio" / "History_of_the_Great_Black_Swamp.pdf"),
            "retrieved_date": RETRIEVED,
        },
    ]
    (REPORTS / "great_black_swamp_source_manifest.json").write_text(
        json.dumps(entries, indent=2), encoding="utf-8"
    )


def main() -> None:
    ensure_dirs()
    source = load_odnr()
    hucs, counties, places = load_context()
    review = class_review(source, hucs)
    review.to_csv(REPORTS / "great_black_swamp_class_review.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    selected, candidate = build_candidate(source, hucs)
    write_geojson(selected, QA_DATA / "great_black_swamp_candidate_gordon1966_mosaic.geojson")
    write_geojson(candidate, QA_DATA / "great_black_swamp_candidate_gordon1966.geojson")
    write_qa(source, selected, candidate, counties, hucs)
    render_map(source, selected, candidate, hucs, counties, places)
    write_manifest()
    print("Built Great Black Swamp review package; canonical Phase 1 GeoPackage was not modified.")


if __name__ == "__main__":
    main()
