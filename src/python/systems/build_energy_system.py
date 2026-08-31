"""Build the Phase 3A factual energy/grid/compute baseline and Map 11.

Transmission geometry is cartographic context, not a solved power-flow network.
Edges encode only coarse documented or explicitly qualified functional interfaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import requests
from shapely.geometry import Point, box


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "eia"
NETWORKS = ROOT / "data" / "processed" / "networks"
MAPS = ROOT / "outputs" / "maps" / "systems"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
PLANTS_CACHE = RAW / "power_plants_western_basin.geojson"
LINES_CACHE = RAW / "transmission_lines_western_basin_230kv.geojson"
NODES_CSV = NETWORKS / "energy_system_nodes.csv"
EDGES_CSV = NETWORKS / "energy_system_edges.csv"
SOURCES_CSV = NETWORKS / "energy_system_sources.csv"
MAP11 = MAPS / "11_energy_grid_compute_baseline_2026"
MANIFEST = REPORTS / "energy_system_manifest.json"
RETRIEVED = "2026-08-31"
FOCUS = (-84.02, 41.05, -82.58, 42.16)

PLANT_SERVICE = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Power_Plants_in_the_US/FeatureServer/0/query"
LINE_SERVICE = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0/query"
SELECTED_PLANTS = {
    1733: ("generation", "fossil", "operating_planned_retirement"),
    1729: ("generation", "nuclear", "operating"),
    6149: ("generation", "nuclear", "operating"),
    59764: ("generation", "fossil", "operating"),
    55348: ("generation", "fossil", "operating"),
    55701: ("generation", "fossil", "operating"),
    63322: ("generation", "renewable", "operating"),
    60622: ("generation", "renewable", "operating"),
    56226: ("generation", "renewable", "operating"),
    67758: ("storage", "battery", "operating"),
    65951: ("storage", "battery", "operating"),
}

SOURCES = [
    ("SRC-EIA-PLANTS-2025", "EIA Power Plants in the United States", "U.S. Energy Information Administration", "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Power_Plants_in_the_US/FeatureServer", "EIA-860/860M/923; service period 2025-02", "Facility locations, technology, and nameplate/net-capacity fields; current status cross-checked where material."),
    ("SRC-EIA-TRANSMISSION-2025", "U.S. Electric Power Transmission Lines", "U.S. Energy Information Administration / HIFLD", "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0", "Service metadata updated 2025", "In-service lines >=230 kV clipped to study extent; cartographic context only."),
    ("SRC-NRC-DAVIS-2026", "Davis-Besse reactor information", "U.S. Nuclear Regulatory Commission", "https://www.nrc.gov/info-finder/reactors/davi", "Updated 2026-08-27", "Operating-license and reactor-status authority."),
    ("SRC-NRC-FERMI-2026", "Fermi Unit 2 reactor information", "U.S. Nuclear Regulatory Commission", "https://www.nrc.gov/info-finder/reactors/ferm2", "Updated 2026-08-27", "Operating-license and reactor-status authority."),
    ("SRC-EPA-OCEC-2025", "Oregon Clean Energy Center permitting information", "U.S. Environmental Protection Agency", "https://www.epa.gov/nsr/oregon-clean-energy-center-permitting-information-0", "Updated 2025-10-22", "Confirms facility, address, combined-cycle technology, and 844 MW gross permitting basis."),
    ("SRC-AMP-FREMONT-2026", "AMP Fremont Energy Center", "American Municipal Power", "https://www.amppartners.org/investors/bond-programs/amp-fremont-energy-center-revenue-bonds/", "Current 2026 page", "Confirms 675 MW summer duct-fired / 512 MW unfired ratings and operation."),
    ("SRC-DTE-MONROE-2024", "Monroe Power Plant cessation-of-coal annual report", "DTE Electric Company", "https://www.dteenergy.com/content/dam/dteenergy/deg/website/common/dte-impact-and-news/environment/elg-rule-compliance/MONPP_Cessation_of_Coal_Annual_Report_2024.pdf", "2024 report", "Confirms 3,280 MW gross rating and phased retirement commitment; EIA capacity retained in table."),
    ("SRC-AMP-BG-2024", "Bowling Green system achievements", "American Municipal Power", "https://www.amppartners.org/news/newsroom/bowling-green-receives-national-recognition-for-system-achievements/", "2024", "Confirms 20 MW solar, municipal wind participation, 12 MW storage, and Bellard interconnection."),
    ("SRC-TOLEDO-COLLINS-2026", "Collins Park Treatment Plant improvements", "City of Toledo", "https://toledo.oh.gov/residents/water/water-system-improvements/collins-park-treatment-plant-improvements", "Current 2026 page", "Confirms 140 MGD treatment capacity and electrical/instrumentation modernization; electricity demand not published."),
    ("SRC-TOLEDO-BAYVIEW-2026", "Bay View Water Reclamation Plant improvements", "City of Toledo", "https://toledo.oh.gov/residents/water/water-system-improvements/bay-view-wastewater-treatment-plant-improvements", "Current 2026 page", "Confirms 65 MGD dry-weather and up to 400 MGD wet-weather treatment; electricity demand not published."),
    ("SRC-EPA-MATERION-ELMORE", "Materion Elmore permit documentation", "U.S. Environmental Protection Agency", "https://semspub.epa.gov/work/05/967810.pdf", "Public permit record", "Confirms advanced-processing facility; electricity demand not published."),
    ("SRC-MM-WOODVILLE-2025", "Woodville lime facility", "Martin Marietta", "https://mcdn.martinmarietta.com/assets/sustainability/2025sustainabilityreport.pdf", "2025", "Confirms lime-kiln processing; electricity demand not published."),
    ("SRC-BG-DATACENTER-2025", "Construction plans for Bowling Green 5 MW data center", "City of Bowling Green GIS", "https://gis.bgohio.org/tiff/tiffimages_view.php?editid1=%7B45BED83D-52DE-4115-83A7-0CCBDD3BFCC8%7D", "Plans dated 2025-03-21", "Documents a 5 MW Oppidan data-center plan at 2501 Woodstream Drive; operational status not confirmed."),
    ("SRC-PJM-ATSI-2026", "PJM operating regions and Toledo Edison planning criteria", "PJM Interconnection", "https://emergencyprocedures.pjm.com/ep/pages/regions.jsf", "Current 2026 page", "Confirms Toledo Edison within the ATSI/PJM operating region; no topology or flow modeled."),
]


def fetch_geojson(url: str, params: dict, path: Path, refresh: bool) -> gpd.GeoDataFrame:
    if refresh or not path.exists():
        response = requests.get(url, params={**params, "f": "geojson"}, timeout=120)
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
    return gpd.read_file(path)


def retrieve(refresh: bool) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    geom = ",".join(map(str, FOCUS))
    common = {"geometry": geom, "geometryType": "esriGeometryEnvelope", "inSR": 4326,
              "spatialRel": "esriSpatialRelIntersects", "outSR": 4326, "returnGeometry": "true"}
    plants = fetch_geojson(PLANT_SERVICE, {**common, "where": "1=1", "outFields": "*"}, PLANTS_CACHE, refresh)
    lines = fetch_geojson(LINE_SERVICE, {**common, "where": "STATUS='IN SERVICE' AND VOLTAGE>=230",
        "outFields": "ID,STATUS,OWNER,VOLTAGE,VOLT_CLASS,INFERRED,SUB_1,SUB_2"}, LINES_CACHE, refresh)
    return plants, lines


def build_nodes(plants: gpd.GeoDataFrame) -> pd.DataFrame:
    rows = []
    for code, (node_type, asset_class, status) in SELECTED_PLANTS.items():
        hit = plants[plants.Plant_Code.astype(int) == code]
        if len(hit) != 1:
            raise AssertionError(f"Expected one EIA plant {code}, found {len(hit)}")
        r = hit.iloc[0]
        corroborating = {6149:"SRC-NRC-DAVIS-2026", 1729:"SRC-NRC-FERMI-2026",
            1733:"SRC-DTE-MONROE-2024", 59764:"SRC-EPA-OCEC-2025", 55701:"SRC-AMP-FREMONT-2026",
            60622:"SRC-AMP-BG-2024", 56226:"SRC-AMP-BG-2024", 65951:"SRC-AMP-BG-2024"}.get(code, "")
        if node_type == "storage":
            capacity, basis = float(r.Bat_MW), "EIA battery operating capacity (2025-02 service snapshot)"
        elif asset_class == "nuclear":
            capacity, basis = float(r.Nuclear_MW), "EIA nuclear operating capacity (2025-02 service snapshot)"
        elif asset_class == "fossil":
            field = "Coal_MW" if str(r.PrimSource).lower() == "coal" else "NG_MW"
            capacity, basis = float(r[field]), f"EIA {field} operating capacity (2025-02 service snapshot)"
        else:
            field = "Solar_MW" if str(r.PrimSource).lower() == "solar" else "Wind_MW"
            capacity, basis = float(r[field]), f"EIA {field} operating capacity (2025-02 service snapshot)"
        rows.append({"node_id": f"ENE-EIA-{code}", "name": r.Plant_Name, "node_type": node_type,
            "asset_class": asset_class, "fuel_or_technology": r.PrimSource, "status_2026": status,
            "capacity_mw": capacity, "capacity_basis": basis,
            "operator_or_owner": r.Utility_Na, "latitude": float(r.Latitude), "longitude": float(r.Longitude),
            "source_id": "SRC-EIA-PLANTS-2025", "corroborating_source_id": corroborating,
            "confidence": "high", "reality_status": "real", "canon_status": "verified",
            "notes": "Selected regional baseline asset; no dispatch, flow, or utilization inferred."})
    static = [
        ("ENE-GRID-ATSI", "PJM / ATSI–Toledo Edison regional interface", "grid", "regional_interface", "transmission", "operating", None, "not quantified", "PJM / ATSI / Toledo Edison", None, None, "SRC-PJM-ATSI-2026", "high", "Nonspatial control-area/interface node; not a substation or bus model."),
        ("ENE-GRID-DTE", "DTE Southeast Michigan regional interface", "grid", "regional_interface", "transmission", "operating", None, "not quantified", "DTE Electric", None, None, "SRC-EIA-TRANSMISSION-2025", "medium_high", "Nonspatial regional interface; no transfer capability inferred."),
        ("ENE-LOAD-COLLINS", "Collins Park Water Treatment Plant", "major_load", "water", "treatment", "operating", None, "electric demand not published", "City of Toledo", 41.663405, -83.47596, "SRC-TOLEDO-COLLINS-2026", "high", "Critical 140 MGD water-treatment load; no MW demand estimate."),
        ("ENE-LOAD-BAYVIEW", "Bay View Water Reclamation Plant", "major_load", "water", "wastewater treatment", "operating", None, "electric demand not published", "City of Toledo", 41.7064, -83.4584, "SRC-TOLEDO-BAYVIEW-2026", "medium_high", "Critical 65/400 MGD dry/wet-weather facility; point is approximate facility centroid."),
        ("ENE-LOAD-ELMORE", "Materion Elmore advanced processing", "major_load", "industrial", "advanced materials processing", "operating", None, "electric demand not published", "Materion", 41.491149985926, -83.215860027455, "SRC-EPA-MATERION-ELMORE", "high", "Energy-relevant industrial process; no MW demand estimate."),
        ("ENE-LOAD-WOODVILLE", "Martin Marietta Woodville lime processing", "major_load", "industrial", "lime kilns", "operating", None, "electric demand not published", "Martin Marietta", 41.465048865166, -83.366181833374, "SRC-MM-WOODVILLE-2025", "high", "Energy-relevant process load; no electricity or fuel split inferred."),
        ("ENE-COMPUTE-BG-5MW", "Oppidan Bowling Green data-center project", "compute", "data_center", "data center", "permitted_or_planned_unverified_operation", 5.0, "City construction-plan title", "Oppidan project", 41.3587, -83.6019, "SRC-BG-DATACENTER-2025", "medium", "Address-level approximate point; 2026 operational status not confirmed."),
    ]
    for x in static:
        rows.append(dict(zip(["node_id","name","node_type","asset_class","fuel_or_technology","status_2026","capacity_mw","capacity_basis","operator_or_owner","latitude","longitude","source_id","confidence","notes"], x)) | {"corroborating_source_id":"", "reality_status":"real","canon_status":"verified" if x[5] == "operating" else "qualified"})
    return pd.DataFrame(rows)


def build_edges(nodes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for node_id in nodes.loc[nodes.node_type == "generation", "node_id"]:
        target = "ENE-GRID-DTE" if node_id in {"ENE-EIA-1729", "ENE-EIA-1733", "ENE-EIA-63322"} else "ENE-GRID-ATSI"
        rows.append((f"EDGE-{node_id}", node_id, target, "generation_grid_interface", "coarse regional interconnection", "SRC-EIA-TRANSMISSION-2025", "medium"))
    for node_id in nodes.loc[nodes.node_type == "storage", "node_id"]:
        target = "ENE-GRID-DTE" if node_id == "ENE-EIA-67758" else "ENE-GRID-ATSI"
        rows.append((f"EDGE-{node_id}", node_id, target, "bidirectional_storage_interface", "coarse regional interconnection", "SRC-EIA-TRANSMISSION-2025", "medium"))
    for node_id in nodes.loc[nodes.node_type == "major_load", "node_id"]:
        rows.append((f"EDGE-{node_id}", "ENE-GRID-ATSI", node_id, "grid_serves_load", "functional dependency; feeder unknown", "SRC-PJM-ATSI-2026", "medium"))
    rows.append(("EDGE-COMPUTE-BG", "ENE-GRID-ATSI", "ENE-COMPUTE-BG-5MW", "grid_serves_planned_compute", "project design capacity; feeder unknown", "SRC-BG-DATACENTER-2025", "medium"))
    rows.append(("EDGE-REGIONAL-INTERFACE", "ENE-GRID-ATSI", "ENE-GRID-DTE", "regional_grid_interface", "high-level interconnected grid context", "SRC-EIA-TRANSMISSION-2025", "low"))
    cols = ["edge_id","from_node_id","to_node_id","relationship_type","relationship_basis","source_id","confidence"]
    out = pd.DataFrame(rows, columns=cols)
    out["reality_status"] = "real"
    out["canon_status"] = "qualified"
    out["notes"] = "Not a feeder, dispatch, transfer-capability, or power-flow claim."
    return out


def plot_map(nodes: pd.DataFrame, lines: gpd.GeoDataFrame) -> None:
    fig = plt.figure(figsize=(16, 10), facecolor="#f2ead8")
    ax = fig.add_axes([0.04, 0.07, 0.68, 0.84], facecolor="#e9e2cf")
    panel = fig.add_axes([0.745, 0.07, 0.225, 0.84], facecolor="#efe7d4")
    panel.axis("off")
    lake = gpd.read_file(GPKG, layer="water_lake_erie").to_crs(4326)
    lake.plot(ax=ax, color="#b7d4df", edgecolor="#6f929f", linewidth=0.6, zorder=0)
    counties = gpd.read_file(ROOT / "data/raw/census/tigerweb_counties_oh_in_mi.geojson").to_crs(4326)
    counties.boundary.plot(ax=ax, color="#a79d87", linewidth=0.55, zorder=1)
    roads = gpd.read_file(ROOT / "data/raw/census/tigerweb_primary_roads.geojson").to_crs(4326)
    roads.plot(ax=ax, color="#c4b69d", linewidth=0.7, zorder=1)
    lines.plot(ax=ax, color="#273d66", linewidth=lines.VOLTAGE.astype(float).map(lambda v: 1.0 if v < 300 else 1.8), alpha=0.72, zorder=2)
    palette = {"generation":"#c2543d", "storage":"#78549a", "major_load":"#2b7a78", "compute":"#d28b23"}
    markers = {"generation":"o", "storage":"s", "major_load":"^", "compute":"D"}
    spatial = nodes[nodes.longitude.notna() & nodes.latitude.notna()]
    for kind in ["generation", "storage", "major_load", "compute"]:
        d = spatial[spatial.node_type == kind]
        ax.scatter(d.longitude, d.latitude, s=76 if kind != "generation" else 92, marker=markers[kind],
                   color=palette[kind], edgecolor="#f8f2e4", linewidth=0.9, zorder=5, label=kind.replace("_", " ").title())
    labels = {
        "ENE-EIA-1733":"Monroe coal", "ENE-EIA-1729":"Fermi 2", "ENE-EIA-6149":"Davis-Besse",
        "ENE-EIA-59764":"Oregon CEC", "ENE-EIA-55348":"Troy Energy", "ENE-EIA-55701":"AMP Fremont",
        "ENE-EIA-60622":"BG solar", "ENE-EIA-56226":"BG wind", "ENE-EIA-63322":"Temperance solar",
        "ENE-EIA-67758":"Slocum storage", "ENE-EIA-65951":"BG storage", "ENE-COMPUTE-BG-5MW":"BG data center (planned)",
        "ENE-LOAD-COLLINS":"Collins Park water", "ENE-LOAD-BAYVIEW":"Bay View wastewater",
        "ENE-LOAD-ELMORE":"Materion Elmore", "ENE-LOAD-WOODVILLE":"Woodville lime",
    }
    offsets = {
        "ENE-LOAD-BAYVIEW": (7, 9), "ENE-LOAD-COLLINS": (7, -10), "ENE-EIA-59764": (7, 7),
        "ENE-LOAD-ELMORE": (7, 7), "ENE-LOAD-WOODVILLE": (7, -10), "ENE-EIA-60622": (12, 11),
        "ENE-EIA-65951": (7, 6), "ENE-COMPUTE-BG-5MW": (7, -10),
    }
    for _, r in spatial.iterrows():
        if r.node_id in labels:
            ax.annotate(labels[r.node_id], (r.longitude, r.latitude), xytext=offsets.get(r.node_id, (5, 5)), textcoords="offset points",
                        fontsize=7.3, color="#262a2c", bbox=dict(boxstyle="round,pad=.16", fc="#f5efdf", ec="none", alpha=.78), zorder=6)
    ax.set(xlim=(FOCUS[0], FOCUS[2]), ylim=(FOCUS[1], FOCUS[3]))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("MAP 11 — WESTERN BASIN ENERGY / GRID / COMPUTE BASELINE, 2026", loc="left", fontsize=18, color="#17334d", pad=15)
    ax.text(FOCUS[0]+.02, FOCUS[3]-.045, "Factual asset inventory + high-voltage cartographic context", fontsize=10, color="#4b5860")
    ax.legend(loc="lower left", frameon=True, facecolor="#f5efdf", edgecolor="#8b806c", fontsize=9, ncol=2)
    ax.text(0.99, 0.012, "EIA/HIFLD in-service transmission ≥230 kV • no power-flow, congestion, or feeder inference",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#4f4b43")

    counts = nodes.node_type.value_counts()
    panel.text(0.04, .965, "SYSTEM BASELINE", fontsize=14, weight="bold", color="#17334d", va="top")
    panel.text(0.04, .91, f"{len(nodes)} nodes  •  17 coarse edges", fontsize=10.5, color="#31363a")
    y = .855
    for title, body, color in [
        ("GENERATION", "9 assets\n2 nuclear • 4 fossil • 3 renewable", palette["generation"]),
        ("GRID", f"2 regional interface nodes\n{len(lines)} mapped ≥230 kV line features", "#273d66"),
        ("STORAGE", "2 battery assets\nBowling Green 12 MW • Slocum 14 MW", palette["storage"]),
        ("MAJOR LOADS", "4 critical/industrial facilities\nDemand intentionally unquantified", palette["major_load"]),
        ("COMPUTE", "1 documented 5 MW project\nPermitted/planned; operation unverified", palette["compute"]),
    ]:
        panel.add_patch(FancyBboxPatch((.03, y-.105), .94, .105, boxstyle="round,pad=.012", fc="#f7f1e3", ec=color, lw=1.2))
        panel.text(.06, y-.025, title, fontsize=9.6, weight="bold", color=color)
        panel.text(.06, y-.055, body, fontsize=8.5, color="#353535", va="top", linespacing=1.35)
        y -= .137
    panel.text(.04, .155, "READING RULES", fontsize=10, weight="bold", color="#17334d")
    panel.text(.04, .125, "• capacities are source-specific bases\n• lines are public generalized geometry\n• grid nodes are nonspatial interfaces\n• planned compute is not an operating claim\n• no future scenario is shown", fontsize=8.2, va="top", linespacing=1.45, color="#3c3a35")
    fig.savefig(MAP11.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(MAP11.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def sha256(path: Path) -> str:
    h = hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    for d in [RAW, NETWORKS, MAPS, TABLES, REPORTS]: d.mkdir(parents=True, exist_ok=True)
    plants, lines = retrieve(args.refresh)
    nodes = build_nodes(plants)
    edges = build_edges(nodes)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)
    pd.DataFrame(SOURCES, columns=["source_id","title","agency_or_publisher","url_or_identifier","publication_or_dataset_date","notes"]).assign(retrieved_date=RETRIEVED, confidence="high").to_csv(SOURCES_CSV, index=False)
    nodes[nodes.longitude.notna()].to_csv(TABLES / "energy_nodes_render_data.csv", index=False)
    lines.drop(columns="geometry").to_csv(TABLES / "energy_transmission_render_data.csv", index=False)
    plot_map(nodes, lines)
    outputs = [NODES_CSV, EDGES_CSV, SOURCES_CSV, MAP11.with_suffix(".png"), MAP11.with_suffix(".svg"), PLANTS_CACHE, LINES_CACHE]
    manifest = {"phase":"3A", "scenario_year":2026, "generated":RETRIEVED,
        "counts":{"generation":int((nodes.node_type=="generation").sum()),"grid":int((nodes.node_type=="grid").sum()),
                  "storage":int((nodes.node_type=="storage").sum()),"major_load":int((nodes.node_type=="major_load").sum()),
                  "compute":int((nodes.node_type=="compute").sum()),"nodes":len(nodes),"edges":len(edges),"transmission_features":len(lines)},
        "artifacts":{str(p.relative_to(ROOT)): {"bytes":p.stat().st_size,"sha256":sha256(p)} for p in outputs}}
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__": main()
