"""Build Phase 3B qualitative cross-system dependencies, matrix, and Map 12.

This layer models functional dependencies, not electrons. It deliberately does
not estimate loads, outage probabilities, transfer limits, or power flows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
REPORTS = ROOT / "reports"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
TABLES = ROOT / "outputs/tables"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"
EIA_LINES = ROOT / "data/raw/eia/transmission_lines_western_basin_230kv.geojson"
NODES = NETWORKS / "energy_system_nodes.csv"
EDGES = NETWORKS / "energy_dependency_edges.csv"
DEP_NODES = NETWORKS / "energy_dependency_nodes.csv"
SOURCES = NETWORKS / "energy_dependency_sources.csv"
MAP12 = MAPS / "12_critical_energy_dependencies_2026"
MATRIX = FIGURES / "energy_dependency_matrix_2026"
MANIFEST = REPORTS / "energy_dependency_manifest.json"

DEPENDENCY_SOURCES = [
    ("SRC-NRC-COOLING-GENERIC-2026", "Generic Environmental Impact Statement for License Renewal of Nuclear Plants — Cooling and Auxiliary Water Systems", "U.S. Nuclear Regulatory Commission", "https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1437/v1/part02", "Updated 2026", "Documents condenser cooling as the predominant nuclear-plant water use; supports qualitative cooling-water dependency, not facility-specific withdrawals."),
    ("SRC-EIA-NG-CONTRACTS-2018", "Natural gas power plants purchase fuel using different types of contracts", "U.S. Energy Information Administration", "https://www.eia.gov/todayinenergy/detail.php?id=35112", "2018-02-27", "Documents supply and pipeline-delivery components and firm/interruptible contract distinctions; no Western Basin contract inferred."),
    ("SRC-DOE-VRE-2026", "Wind and solar variability and bulk-system reliability review", "U.S. Department of Energy / National Renewable Energy Laboratory", "https://www.energy.gov/documents/craig-order-202-26-31-pios-exhibits-2-171-2-189-july-24-2026", "2026", "Documents wind/solar variability and uncertainty; no local forecast or reliability claim made."),
    ("SRC-DOE-SOLAR-GRID-2021", "Solar Grid Planning and Operation Basics", "U.S. Department of Energy", "https://www.energy.gov/cmei/systems/solar-grid-planning-and-operation-basics", "2021", "Documents weather and daylight variability plus the role of storage and controls; no local performance forecast."),
    ("SRC-PJM-PLANNING-2026", "PJM Transmission Planning Criteria", "PJM Interconnection", "https://www.pjm.com/planning/planning-criteria/to-planning-criteria.aspx", "Current 2026 page", "Planning context only; no contingency, stability, congestion, or reserve conclusion is drawn."),
]

QUALITATIVE = {"none", "low", "moderate", "high", "unknown"}
ALLOWED_TYPES = {"electricity", "fuel", "cooling_water", "industrial_heat", "storage_support", "compute", "communications", "water_service", "weather"}
ALLOWED_SCOPES = {"local", "regional", "external"}
ALLOWED_STRENGTH = {"low", "moderate", "high"}
ALLOWED_BASIS = {"documented", "engineering_dependency", "inferred"}
ALLOWED_SENSITIVITY = {"low", "moderate", "high", "unknown"}


def dep(from_system, from_id, to_system, to_id, typ, scope, strength, sensitivity, basis, source, confidence, notes):
    return {"dependency_id": f"DEP-{len(DEPENDENCIES)+1:03d}", "from_system": from_system, "from_node_id": from_id,
            "to_system": to_system, "to_node_id": to_id, "dependency_type": typ, "dependency_scope": scope,
            "dependency_strength": strength, "outage_sensitivity": sensitivity, "relationship_basis": basis,
            "source_id": source, "confidence": confidence, "notes": notes}


DEPENDENCIES = []
def add(*args): DEPENDENCIES.append(dep(*args))

# Critical loads rely on regional electricity; feeder and MW demand remain unknown.
for target, strength in [("ENE-LOAD-COLLINS", "high"), ("ENE-LOAD-BAYVIEW", "high"),
                         ("ENE-LOAD-ELMORE", "high"), ("ENE-LOAD-WOODVILLE", "moderate")]:
    add("energy", "ENE-GRID-ATSI", "water_or_materials", target, "electricity", "local", strength, "high", "engineering_dependency", "SRC-TOLEDO-COLLINS-2026" if "COLLINS" in target else ("SRC-TOLEDO-BAYVIEW-2026" if "BAYVIEW" in target else ("SRC-EPA-MATERION-ELMORE" if "ELMORE" in target else "SRC-MM-WOODVILLE-2025")), "high", "Functional electricity dependence; no feeder, demand, or outage duration modeled.")
add("energy", "ENE-GRID-ATSI", "compute", "ENE-COMPUTE-BG-5MW", "electricity", "local", "high", "unknown", "documented", "SRC-BG-DATACENTER-2025", "medium", "Planned project only; operation and interconnection remain unverified.")

# Grid connection is a functional dependency for generation and storage assets.
for source_id, target, grid in [("SRC-NRC-FERMI-2026", "ENE-EIA-1729", "ENE-GRID-DTE"), ("SRC-NRC-DAVIS-2026", "ENE-EIA-6149", "ENE-GRID-ATSI"),
    ("SRC-DTE-MONROE-2024", "ENE-EIA-1733", "ENE-GRID-DTE"), ("SRC-EPA-OCEC-2025", "ENE-EIA-59764", "ENE-GRID-ATSI"),
    ("SRC-EIA-PLANTS-2025", "ENE-EIA-55348", "ENE-GRID-ATSI"), ("SRC-AMP-FREMONT-2026", "ENE-EIA-55701", "ENE-GRID-ATSI")]:
    add("energy", grid, "generation", target, "electricity", "regional", "moderate", "high", "engineering_dependency", source_id, "high", "Grid interconnection/auxiliary dependence; no bus topology or flow inferred.")

# Thermal generation depends on fuel and cooling; no pipeline or intake geometry is modeled.
for target, source in [("ENE-EIA-59764", "SRC-EIA-NG-CONTRACTS-2018"), ("ENE-EIA-55348", "SRC-EIA-NG-CONTRACTS-2018"), ("ENE-EIA-55701", "SRC-EIA-NG-CONTRACTS-2018")]:
    add("fuel", "DEP-NATURAL-GAS-SUPPLY", "generation", target, "fuel", "external", "high", "moderate", "engineering_dependency", source, "high", "Generalized gas supply and delivery dependence; no pipeline or contract assigned.")
add("fuel", "DEP-FUEL-LOGISTICS", "generation", "ENE-EIA-1733", "fuel", "external", "high", "moderate", "inferred", "SRC-DTE-MONROE-2024", "medium", "Coal/petcoke feed and logistics are required in general; source, route, and inventory are unresolved.")

for target, source, strength in [("ENE-EIA-1729", "SRC-NRC-COOLING-GENERIC-2026", "high"), ("ENE-EIA-6149", "SRC-NRC-COOLING-GENERIC-2026", "high"),
    ("ENE-EIA-1733", "SRC-EIA-PLANTS-2025", "moderate"), ("ENE-EIA-59764", "SRC-EIA-PLANTS-2025", "moderate"),
    ("ENE-EIA-55348", "SRC-EIA-PLANTS-2025", "moderate"), ("ENE-EIA-55701", "SRC-EIA-PLANTS-2025", "moderate")]:
    add("water", "DEP-COOLING-WATER", "generation", target, "cooling_water", "regional", strength, "high", "engineering_dependency", source, "high" if "NRC" in source else "medium", "General thermal/cooling dependence; plant-specific intake, withdrawal, and permit conditions are not modeled.")

for target in ["ENE-EIA-60622", "ENE-EIA-63322", "ENE-EIA-56226"]:
    add("weather", "DEP-WEATHER-RESOURCE", "generation", target, "weather", "external", "moderate", "moderate", "engineering_dependency", "SRC-DOE-VRE-2026", "high", "Weather-dependent availability is qualitative; no production forecast or capacity factor inferred.")

for source_id, target, grid in [("SRC-AMP-BG-2024", "ENE-EIA-65951", "ENE-GRID-ATSI"), ("SRC-EIA-PLANTS-2025", "ENE-EIA-67758", "ENE-GRID-DTE")]:
    add("storage", target, "energy", grid, "storage_support", "regional", "moderate", "unknown", "engineering_dependency", source_id, "medium", "Storage can provide short-duration support; duration, dispatch, and sustained-loss replacement are unknown.")
add("communications", "DEP-COMMUNICATIONS-NETWORK", "energy", "ENE-GRID-ATSI", "communications", "regional", "moderate", "unknown", "inferred", "SRC-PJM-PLANNING-2026", "low", "Operational communications are a generalized dependency; no communications topology or failure probability modeled.")
add("communications", "DEP-COMMUNICATIONS-NETWORK", "energy", "ENE-GRID-DTE", "communications", "regional", "moderate", "unknown", "inferred", "SRC-PJM-PLANNING-2026", "low", "Operational communications are a generalized dependency; no communications topology or failure probability modeled.")

DEP_NODE_ROWS = [
    ("DEP-NATURAL-GAS-SUPPLY", "Regional/external natural-gas supply", "fuel", "external", "SRC-EIA-NG-CONTRACTS-2018", "high", "Generalized supply-and-delivery dependency; no pipeline geometry."),
    ("DEP-FUEL-LOGISTICS", "External coal/petcoke fuel logistics", "fuel", "external", "SRC-DTE-MONROE-2024", "medium", "Monroe feed dependency only; route and inventory unresolved."),
    ("DEP-COOLING-WATER", "Cooling and auxiliary water", "water", "regional", "SRC-NRC-COOLING-GENERIC-2026", "high", "Generalized thermal cooling requirement; no intake or withdrawal quantity."),
    ("DEP-WEATHER-RESOURCE", "Weather-dependent renewable resource", "weather", "external", "SRC-DOE-VRE-2026", "high", "Wind/solar availability varies with weather; no forecast."),
    ("DEP-COMMUNICATIONS-NETWORK", "Operational communications network", "communications", "regional", "SRC-PJM-PLANNING-2026", "low", "Generalized coordination dependency; no topology or outage model."),
]

MATRIX_ROWS = ["drinking water", "wastewater", "strategic materials", "carbonate processing", "compute", "nuclear generation", "gas generation", "coal generation", "renewables", "storage"]
MATRIX_COLS = ["electricity", "fuel", "cooling/water", "logistics", "weather", "grid", "communications"]
MATRIX_VALUES = [
    ["high", "none", "low", "moderate", "moderate", "high", "moderate"],
    ["high", "none", "low", "moderate", "moderate", "high", "moderate"],
    ["high", "moderate", "unknown", "moderate", "low", "high", "moderate"],
    ["high", "moderate", "unknown", "moderate", "low", "high", "moderate"],
    ["high", "none", "unknown", "low", "low", "high", "high"],
    ["low", "moderate", "high", "moderate", "low", "moderate", "moderate"],
    ["low", "high", "moderate", "low", "low", "moderate", "moderate"],
    ["low", "high", "high", "high", "low", "moderate", "moderate"],
    ["low", "none", "low", "low", "high", "moderate", "moderate"],
    ["low", "none", "none", "moderate", "low", "high", "moderate"],
]

def sha(path: Path) -> str:
    h = hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def render_matrix() -> None:
    m = pd.DataFrame(MATRIX_VALUES, index=MATRIX_ROWS, columns=MATRIX_COLS)
    m.to_csv(FIGURES / "energy_dependency_matrix_2026.csv", index_label="system")
    order = ["none", "low", "moderate", "high", "unknown"]
    codes = m.apply(lambda col: col.map(order.index)).to_numpy()
    fig, ax = plt.subplots(figsize=(13, 7.8), facecolor="#f2ead8")
    ax.set_facecolor("#f2ead8")
    cmap = matplotlib.colors.ListedColormap(["#e8e0cc", "#b8cfcc", "#e1b66f", "#c45b48", "#a69bbd"])
    ax.imshow(codes, cmap=cmap, vmin=-.5, vmax=4.5, aspect="auto")
    ax.set_xticks(range(len(MATRIX_COLS)), MATRIX_COLS, rotation=25, ha="right", fontsize=10)
    ax.set_yticks(range(len(MATRIX_ROWS)), MATRIX_ROWS, fontsize=10)
    for i in range(len(MATRIX_ROWS)):
        for j in range(len(MATRIX_COLS)):
            ax.text(j, i, m.iloc[i, j], ha="center", va="center", fontsize=8.5, color="#1f2527")
    ax.set_title("QUALITATIVE DEPENDENCY MATRIX — WESTERN BASIN, 2026", loc="left", fontsize=16, weight="bold", color="#17334d", pad=16)
    fig.text(.5, .935, "Ordinal evidence map, not quantitative risk analysis. Categories describe modeled dependence, not outage probability.", ha="center", fontsize=9, color="#4b5353")
    handles = [plt.Rectangle((0,0),1,1,fc=cmap(i), ec="none") for i in range(5)]
    ax.legend(handles, order, ncol=5, loc="upper center", bbox_to_anchor=(.5, -.13), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(MATRIX.with_suffix(".png"), dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)

def draw_box(ax, xy, wh, text, color, fs=8.5):
    x,y=xy; w,h=wh
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.012",fc="#f7f1e3",ec=color,lw=1.25))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color="#2d3335",wrap=True)

def plot_map(nodes: pd.DataFrame, lines: gpd.GeoDataFrame) -> None:
    fig = plt.figure(figsize=(16, 10), facecolor="#f2ead8")
    ax = fig.add_axes([.04,.37,.63,.55], facecolor="#e9e2cf")
    flow = fig.add_axes([.04,.06,.63,.24], facecolor="#efe7d4"); flow.axis("off")
    panel = fig.add_axes([.70,.05,.27,.87], facecolor="#efe7d4"); panel.axis("off")
    lake = gpd.read_file(GPKG, layer="water_lake_erie").to_crs(4326); lake.plot(ax=ax,color="#b7d4df",edgecolor="#6f929f",linewidth=.6,zorder=0)
    counties = gpd.read_file(ROOT/"data/raw/census/tigerweb_counties_oh_in_mi.geojson"); counties.boundary.plot(ax=ax,color="#a79d87",linewidth=.5,zorder=1)
    lines.plot(ax=ax,color="#6e7792",linewidth=.8,alpha=.5,zorder=2)
    palette={"generation":"#c2543d","storage":"#78549a","major_load":"#2b7a78","compute":"#d28b23"}; markers={"generation":"o","storage":"s","major_load":"^","compute":"D"}
    spatial=nodes[nodes.longitude.notna() & nodes.latitude.notna()]
    for kind in ["generation","storage","major_load","compute"]:
        d=spatial[spatial.node_type==kind]; ax.scatter(d.longitude,d.latitude,s=70 if kind!="generation" else 82,marker=markers[kind],color=palette[kind],edgecolor="#f8f2e4",linewidth=.8,zorder=5)
    anchors={"ENE-GRID-ATSI":(-83.42,41.68),"ENE-GRID-DTE":(-83.34,41.98)}
    for nid,(x,y) in anchors.items():
        ax.scatter([x],[y],s=170,marker="*",color="#273d66",edgecolor="#fff7e8",linewidth=1,zorder=7)
        ax.annotate("ATSI / Toledo Edison\nschematic interface" if nid.endswith("ATSI") else "DTE regional\nschematic interface",(x,y),xytext=(7,7),textcoords="offset points",fontsize=7,color="#273d66",bbox=dict(boxstyle="round,pad=.18",fc="#f7f1e3",ec="none",alpha=.9),zorder=8)
    # Functional grid-to-load arrows only; they are intentionally not drawn as electrical routes.
    for _,r in spatial[spatial.node_type.isin(["major_load","compute"])].iterrows():
        anchor=anchors["ENE-GRID-ATSI"]
        ax.annotate("",xy=(r.longitude,r.latitude),xytext=anchor,arrowprops=dict(arrowstyle="-|>",color="#2b7a78",lw=1,alpha=.55,linestyle="--"),zorder=3)
    labels={"ENE-EIA-1733":"Monroe","ENE-EIA-1729":"Fermi 2","ENE-EIA-6149":"Davis-Besse","ENE-EIA-59764":"Oregon CEC","ENE-EIA-55348":"Troy","ENE-EIA-55701":"Fremont","ENE-EIA-60622":"BG solar","ENE-EIA-63322":"Temperance solar","ENE-EIA-56226":"BG wind","ENE-EIA-67758":"Slocum","ENE-EIA-65951":"BG storage","ENE-COMPUTE-BG-5MW":"BG compute (planned)"}
    for _,r in spatial.iterrows():
        if r.node_id in labels: ax.annotate(labels[r.node_id],(r.longitude,r.latitude),xytext=(5,5),textcoords="offset points",fontsize=7,bbox=dict(boxstyle="round,pad=.14",fc="#f7f1e3",ec="none",alpha=.78),zorder=8)
    ax.set(xlim=(-84.02,-82.58),ylim=(41.05,42.16)); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("MAP 12 — CRITICAL ENERGY DEPENDENCIES & RELIABILITY, 2026",loc="left",fontsize=17,color="#17334d",pad=14)
    ax.text(-84.0,42.115,"Geographic anchors above • functional dependencies and external inputs below",fontsize=9,color="#4b5860")
    ax.text(.99,.015,"Dashed arrows = functional dependency, not a feeder or power-flow route",transform=ax.transAxes,ha="right",fontsize=7.2,color="#4f4b43")
    ax.legend(handles=[plt.Line2D([0],[0],marker=markers[k],color="none",markerfacecolor=palette[k],markeredgecolor="white",markersize=8,label=k.replace("_"," ").title()) for k in palette],loc="lower left",ncol=2,frameon=True,facecolor="#f7f1e3",edgecolor="#8b806c",fontsize=8)
    flow.text(.01,.90,"QUALITATIVE DEPENDENCY PATHWAYS",fontsize=10,weight="bold",color="#17334d")
    boxes=[((.01,.54),(.15,.24),"GAS\nSUPPLY","#b86b45"),((.19,.54),(.15,.24),"FUEL /\nLOGISTICS","#b86b45"),((.37,.54),(.15,.24),"COOLING /\nWATER","#2b7a78"),((.55,.54),(.15,.24),"WEATHER\nRESOURCE","#6b9b75"),((.76,.54),(.18,.24),"GENERATION\n(nuclear • gas • coal • VRE)","#c2543d")]
    for xy,wh,t,c in boxes: draw_box(flow,xy,wh,t,c)
    for x, rad in [(.16,.28),(.34,.16),(.52,.04),(.70,-.10)]:
        flow.add_patch(FancyArrowPatch((x,.66),(.76,.66),connectionstyle=f"arc3,rad={rad}",arrowstyle="-|>",mutation_scale=11,color="#596064",lw=1.15))
    draw_box(flow,(.29,.13),(.18,.23),"REGIONAL\nGRID", "#273d66")
    draw_box(flow,(.52,.13),(.17,.23),"STORAGE\n(short-duration support)","#78549a",7.8)
    draw_box(flow,(.76,.13),(.19,.23),"CRITICAL LOADS\nwater • materials • compute","#2b7a78",7.8)
    flow.add_patch(FancyArrowPatch((.85,.54),(.38,.36),connectionstyle="arc3,rad=-.16",arrowstyle="-|>",mutation_scale=11,color="#596064",lw=1.2))
    flow.add_patch(FancyArrowPatch((.47,.245),(.52,.245),arrowstyle="-|>",mutation_scale=11,color="#596064",lw=1.2))
    flow.add_patch(FancyArrowPatch((.69,.245),(.76,.245),arrowstyle="-|>",mutation_scale=11,color="#596064",lw=1.2))
    flow.text(.01,.18,"COMMUNICATIONS → GRID COORDINATION (generalized)",fontsize=7.5,color="#5b5b55")
    panel.text(.04,.97,"RELIABILITY LENS",fontsize=14,weight="bold",color="#17334d",va="top")
    panel.text(.04,.925,"Dependency concentration is visible; outage probability is not modeled.",fontsize=9,color="#31363a",wrap=True)
    y=.875
    for title,body,color in [("WATER", "Grid electricity is a high-sensitivity dependency for Collins Park and Bay View; demand and outage duration are unresolved.","#2b7a78"),("MATERIALS", "Elmore and Woodville are energy-relevant process loads; no facility demand or process-heat split is asserted.","#2b7a78"),("THERMAL", "Gas generation depends on external supply; Monroe retains operating status plus a planned-retirement transition.","#c2543d"),("NUCLEAR", "Davis-Besse and Fermi 2 carry qualitative cooling-water and grid dependencies; fuel logistics stay generalized.","#c2543d"),("RENEWABLES / STORAGE", "Weather shapes wind/solar availability. Storage is present but duration and sustained-loss coverage are unknown.","#78549a"),("COMPUTE", "The Bowling Green 5 MW project remains planned/unverified and therefore is not treated as an operating load.","#d28b23")]:
        panel.add_patch(FancyBboxPatch((.03,y-.082),.94,.082,boxstyle="round,pad=.012",fc="#f7f1e3",ec=color,lw=1.1)); panel.text(.06,y-.018,title,fontsize=8.5,weight="bold",color=color); panel.text(.06,y-.044,textwrap.fill(body,width=66),fontsize=7.25,va="top",color="#383834",linespacing=1.18); y-=.097
    panel.text(.04,.205,"POTENTIAL DEPENDENCY CONCENTRATIONS",fontsize=9.2,weight="bold",color="#17334d")
    panel.text(.04,.178,"• critical-load dependence on grid electricity\n• thermal fuel + cooling concentration\n• 3,066 MW Monroe transition context\n• unknown battery duration\n• continuous-power need for compute\n• generalized communications dependence",fontsize=7.55,va="top",linespacing=1.28,color="#3c3a35")
    panel.text(.04,.035,"No N-1, reserve-margin, congestion, stability, outage-probability, restoration-time, or blackout-footprint claim.",fontsize=6.8,color="#5b5149",wrap=True)
    fig.savefig(MAP12.with_suffix(".png"),dpi=220,bbox_inches="tight",facecolor=fig.get_facecolor()); fig.savefig(MAP12.with_suffix(".svg"),bbox_inches="tight",facecolor=fig.get_facecolor()); plt.close(fig)

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--no-map",action="store_true"); args=parser.parse_args()
    for d in [NETWORKS,REPORTS,MAPS,FIGURES,TABLES]: d.mkdir(parents=True,exist_ok=True)
    base=pd.read_csv(NODES)
    base_ids=set(base.node_id)
    dep_nodes=pd.DataFrame(DEP_NODE_ROWS,columns=["node_id","name","node_system","reality_status","source_id","confidence","notes"])
    dep_nodes["canon_status"]="qualified"; dep_nodes.to_csv(DEP_NODES,index=False)
    src=pd.read_csv(NETWORKS/"energy_system_sources.csv")
    extra=pd.DataFrame(DEPENDENCY_SOURCES,columns=["source_id","title","agency_or_publisher","url_or_identifier","publication_or_dataset_date","notes"])
    extra["retrieved_date"]="2026-09-01"; extra["confidence"]="high"
    src=pd.concat([src,extra],ignore_index=True).drop_duplicates("source_id"); src.to_csv(SOURCES,index=False)
    edges=pd.DataFrame(DEPENDENCIES)
    assert set(edges.from_node_id)|set(edges.to_node_id) <= base_ids|set(dep_nodes.node_id)
    edges.to_csv(EDGES,index=False)
    render_matrix()
    if not args.no_map:
        lines=gpd.read_file(EIA_LINES); plot_map(base,lines)
    artifacts=[DEP_NODES,EDGES,SOURCES,FIGURES/"energy_dependency_matrix_2026.csv",MATRIX.with_suffix(".png")]
    if not args.no_map: artifacts += [MAP12.with_suffix(".png"),MAP12.with_suffix(".svg")]
    manifest={"phase":"3B","generated":"2026-09-01","counts":{"dependency_nodes":len(dep_nodes),"dependency_edges":len(edges),"matrix_rows":len(MATRIX_ROWS),"matrix_columns":len(MATRIX_COLS)},"artifacts":{str(p.relative_to(ROOT)): {"bytes":p.stat().st_size,"sha256":sha(p)} for p in artifacts}}
    MANIFEST.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest["counts"],indent=2))

if __name__=="__main__": main()
