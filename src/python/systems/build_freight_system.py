"""Build Phase 5A factual freight/industry/material-flow baseline and Map 17.

The model represents public corridors and documented/generalized commodity
functions. It deliberately excludes shipment volumes, schedules, facility-
specific routes, hazardous-material routing, and sensitive logistics topology.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
RAW_TRANSPORT = ROOT / "data/raw/transportation"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

NODES_PATH = NETWORKS / "freight_system_nodes.csv"
EDGES_PATH = NETWORKS / "freight_system_edges.csv"
RAIL_CACHE = RAW_TRANSPORT / "ntad_class1_rail_network_western_basin.geojson"
MAP_BASE = MAPS / "17_freight_industry_material_flows_2026"
FLOW_FIGURE = FIGURES / "freight_commodity_interfaces_2026"
MANIFEST = REPORTS / "freight_system_manifest.json"
RETRIEVED_DATE = "2026-09-02"
RAIL_QUERY = "https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines_Class_I_Railroads/FeatureServer/0/query"

NODE_COLUMNS = ["node_id", "name", "node_type", "mode", "industrial_role", "commodity_classes", "status", "latitude", "longitude", "source_id", "confidence", "notes"]
EDGE_COLUMNS = ["edge_id", "from_id", "to_id", "mode", "flow_role", "commodity_class", "relationship_basis", "status", "source_id", "confidence", "notes"]


def n(node_id, name, node_type, mode, role, commodities, status, source, confidence, notes, latitude="", longitude=""):
    return {"node_id": node_id, "name": name, "node_type": node_type, "mode": mode, "industrial_role": role, "commodity_classes": commodities, "status": status, "latitude": latitude, "longitude": longitude, "source_id": source, "confidence": confidence, "notes": notes}


NODES = [
    n("FRT-PORT-TOLEDO", "Port of Toledo", "port", "marine", "Great Lakes port gateway", "container_or_general_freight;aggregate;steel_or_metal_products;industrial_materials", "operating public port", "phase5a_port_geocode", "high", "Address-level port anchor at 1 Maritime Plaza; terminals and docks are generalized, not individually mapped.", "41.653818167585", "-83.528499986757"),
    n("FRT-TERM-IRONVILLE", "Ironville Terminal / Cleveland-Cliffs HBI interface", "terminal", "marine", "direct-reduced iron / HBI bulk-material interface", "steel_or_metal_products;industrial_materials", "documented terminal role; point not separately geocoded", "phase5a_toledo_port", "high", "Port authority documents vessel delivery of product to the Ironville direct-reduction plant and finished product leaving by truck and rail; destination routes are not specified."),
    n("FRT-RAIL-NS", "Norfolk Southern Class I freight corridor context", "rail_interface", "rail", "Class I freight rail corridor", "steel_or_metal_products;aggregate;industrial_materials;container_or_general_freight", "public corridor", "phase5a_ntad_rail", "high", "NTAD Class I corridor geometry; corridor presence does not prove facility use or a shipment."),
    n("FRT-RAIL-CSXT", "CSX Class I freight corridor context", "rail_interface", "rail", "Class I freight rail corridor", "steel_or_metal_products;aggregate;industrial_materials;container_or_general_freight", "public corridor", "phase5a_ntad_rail", "high", "NTAD Class I corridor geometry; corridor presence does not prove facility use or a shipment."),
    n("FRT-RAIL-CN", "Canadian National Class I freight corridor context", "rail_interface", "rail", "Class I freight rail corridor", "steel_or_metal_products;aggregate;industrial_materials;container_or_general_freight", "public corridor", "phase5a_ntad_rail", "high", "NTAD Class I corridor geometry; carrier presence is represented at corridor level only."),
    n("FRT-RAIL-WLE", "Wheeling & Lake Erie Railway public port interface", "rail_interface", "rail", "regional freight-rail interface", "aggregate;lime;industrial_materials;steel_or_metal_products", "publicly listed regional interface; geometry not modeled", "phase5a_toledo_port", "medium", "Port authority lists the carrier as a rail contact; no line, yard, customer, or shipment route is inferred."),
    n("FRT-HWY-I75", "I-75 freight corridor", "highway_interface", "highway", "north-south regional freight corridor", "container_or_general_freight;automotive;steel_or_metal_products;industrial_materials", "public primary-road corridor", "census_tigerweb_context", "high", "Existing TIGER primary-road geometry; no plant-specific truck route or truck count."),
    n("FRT-HWY-I80-90", "I-80 / I-90 Ohio Turnpike freight corridor", "highway_interface", "highway", "east-west regional freight corridor", "container_or_general_freight;agricultural_bulk;aggregate;industrial_materials", "public primary-road corridor", "census_tigerweb_context", "high", "Existing TIGER primary-road geometry and Port of Toledo crossroads context; no facility-specific route or truck count."),
    n("FRT-HWY-I280", "I-280 freight connector context", "highway_interface", "highway", "Toledo harbor and regional connector", "container_or_general_freight;steel_or_metal_products;industrial_materials", "public primary-road corridor", "census_tigerweb_context", "medium", "Existing TIGER primary-road geometry; no port-terminal route or truck movement is inferred."),
    n("FRT-HWY-US23", "US-23 freight corridor", "highway_interface", "highway", "north-south regional freight connector", "container_or_general_freight;agricultural_bulk;automotive;industrial_materials", "public primary-road corridor", "census_tigerweb_context", "high", "Existing TIGER primary-road geometry; no facility-specific route or truck count."),
    n("FRT-FUEL-EXTERNAL", "External fuel and petroleum logistics interface", "pipeline_interface", "generalized", "high-level external fuel supply context", "petroleum_or_fuel;chemicals", "generalized external interface", "phase5a_eia_petroleum", "medium", "Generalized regional fuel interface only; no pipeline alignment, station, valve, pressure, capacity, or contract route is modeled."),
    n("FRT-MKT-GREAT-LAKES", "Great Lakes / St. Lawrence external markets", "external_market", "marine", "marine-connected external market interface", "container_or_general_freight;aggregate;steel_or_metal_products;industrial_materials", "generalized market interface", "phase5a_great_lakes_seaway", "high", "External connection through the Great Lakes/St. Lawrence Seaway System; no vessel schedule or named customer is modeled."),
    n("FRT-MKT-MIDWEST-INDUSTRIAL", "Midwest industrial markets", "external_market", "multimodal", "generalized regional industrial market interface", "steel_or_metal_products;aggregate;lime;industrial_materials;automotive", "generalized market interface", "phase5a_fhwa_faf", "medium", "Generalized market endpoint for documented or broad functional flows; no destination facility or volume is assigned."),
    n("FRT-MKT-MICHIGAN-CANADA", "Michigan / Canada freight interface", "external_market", "multimodal", "cross-border and heavy-haul market interface", "container_or_general_freight;steel_or_metal_products;industrial_materials;automotive", "generalized market interface", "phase5a_toledo_port", "medium", "Port authority documents designated heavy-haul connections; no exact route, permit, schedule, or customer is modeled."),
    n("FRT-MKT-LICENSED-DISPOSAL", "External licensed remediation-disposal destination", "external_market", "generalized", "remediation logistics destination", "industrial_materials;chemicals", "documented program-level destination", "phase5a_luckey_logistics", "high", "Represents off-site licensed disposal as a destination class; no hazardous-material route, facility, schedule, or quantity is modeled."),
    n("FRT-AG-MIDWEST-BULK", "Midwest agricultural bulk market context", "agricultural_node", "multimodal", "broad agricultural bulk origin/market context", "agricultural_bulk;grain", "generalized external context", "phase5a_fhwa_faf", "medium", "Freight Analysis Framework context only; no Toledo-specific grain shipment, elevator, volume, or route is asserted."),
    n("FRT-IND-IRONVILLE", "Cleveland-Cliffs Ironville direct-reduction plant", "industrial_site", "multimodal", "HBI production and bulk industrial processing", "steel_or_metal_products;industrial_materials", "documented industrial role; exact terminal point generalized", "phase5a_toledo_port", "high", "Port authority documents vessel input and truck/rail output; this node is not separately geocoded to avoid inventing terminal geometry."),
    n("CARB-EXT-AREA-WOODVILLE", "Area Aggregates Woodville extraction", "industrial_site", "generalized", "carbonate aggregate extraction", "aggregate;limestone;agricultural_bulk", "operating 2026 permit context", "phase5a_area_woodville", "high", "Existing materials-system node reused; freight mode, customer, route, and quantity are not established.", "41.440421365979", "-83.357258672099"),
    n("CARB-PROC-MM-WOODVILLE", "Martin Marietta Woodville lime processing", "material_processor", "generalized", "lime and dolomitic-material processing", "lime;limestone;industrial_materials;agricultural_bulk", "operating 2026 facility context", "phase5a_mm_woodville", "high", "Existing materials-system node reused; distribution relationship is generalized and no route or quantity is asserted.", "41.465048865166", "-83.366181833374"),
    n("CARB-PROC-GRAYMONT-GENOA", "Graymont Genoa lime processing", "material_processor", "generalized", "dolomitic lime processing", "lime;limestone;industrial_materials", "operating 2026 facility context", "phase5a_graymont_genoa", "high", "Existing materials-system node reused; specific quarry/feed and freight route remain unresolved.", "41.515270001961", "-83.355189973188"),
    n("BER-PROC-ELMORE", "Materion Elmore advanced processing", "material_processor", "generalized", "advanced strategic-material processing", "strategic_materials;industrial_materials", "operating 2026 facility context", "phase5a_materion_elmore", "high", "Existing materials-system node reused; nonlocal feed is documented, but transport mode, route, schedule, and quantity are not.", "41.491149985926", "-83.215860027455"),
    n("BER-LEG-LUCKEY", "Luckey FUSRAP remediation site", "industrial_site", "generalized", "legacy remediation and licensed waste logistics", "industrial_materials;chemicals", "active remediation 2026", "phase5a_luckey_usace", "high", "Existing materials-system node reused; this is legacy/remediation context, not current production or a freight corridor.", "41.45880174891", "-83.490434663133"),
]


def e(edge_id, from_id, to_id, mode, role, commodity, basis, status, source, confidence, notes):
    return {"edge_id": edge_id, "from_id": from_id, "to_id": to_id, "mode": mode, "flow_role": role, "commodity_class": commodity, "relationship_basis": basis, "status": status, "source_id": source, "confidence": confidence, "notes": notes}


EDGES = [
    e("FRT-E-001", "FRT-PORT-TOLEDO", "FRT-MKT-GREAT-LAKES", "marine", "documented_port_connection", "container_or_general_freight;aggregate;steel_or_metal_products;industrial_materials", "documented_corridor", "current_2026", "phase5a_toledo_port", "high", "Port is linked to global markets through the Great Lakes/St. Lawrence Seaway System; no named shipment is asserted."),
    e("FRT-E-002", "FRT-PORT-TOLEDO", "FRT-MKT-MICHIGAN-CANADA", "highway", "documented_heavy_haul_interface", "container_or_general_freight;steel_or_metal_products;industrial_materials", "documented_corridor", "current_2026", "phase5a_toledo_port", "medium", "Designated Michigan/Canada heavy-haul context; exact routes and permits are not modeled."),
    e("FRT-E-003", "FRT-PORT-TOLEDO", "FRT-RAIL-NS", "rail", "documented_on_dock_class_i_access", "container_or_general_freight;steel_or_metal_products;industrial_materials", "interchange", "current_2026", "phase5a_toledo_port", "high", "Port page documents on-dock Class I rail access; the corridor is not a claim that every terminal uses NS."),
    e("FRT-E-004", "FRT-PORT-TOLEDO", "FRT-RAIL-CSXT", "rail", "documented_carrier_interface", "container_or_general_freight;steel_or_metal_products;industrial_materials", "interchange", "current_2026", "phase5a_toledo_port", "medium", "Port public transportation page lists CSX; no customer-specific route is inferred."),
    e("FRT-E-005", "FRT-PORT-TOLEDO", "FRT-RAIL-CN", "rail", "documented_carrier_interface", "container_or_general_freight;steel_or_metal_products;industrial_materials", "interchange", "current_2026", "phase5a_toledo_port", "medium", "Port public transportation page lists CN; no customer-specific route is inferred."),
    e("FRT-E-006", "FRT-PORT-TOLEDO", "FRT-RAIL-WLE", "rail", "documented_regional_rail_interface", "aggregate;lime;industrial_materials;steel_or_metal_products", "interchange", "current_2026", "phase5a_toledo_port", "medium", "Port public transportation page lists Wheeling & Lake Erie; no line or shipment route is inferred."),
    e("FRT-E-007", "FRT-PORT-TOLEDO", "FRT-HWY-I75", "highway", "documented_port_access", "container_or_general_freight;automotive;industrial_materials", "documented_corridor", "current_2026", "phase5a_toledo_port", "high", "Port identifies I-75 as a crossroads; no plant-specific truck route is inferred."),
    e("FRT-E-008", "FRT-PORT-TOLEDO", "FRT-HWY-I80-90", "highway", "documented_port_access", "container_or_general_freight;agricultural_bulk;aggregate;industrial_materials", "documented_corridor", "current_2026", "phase5a_toledo_port", "high", "Port identifies I-80/90 as a crossroads; no plant-specific truck route is inferred."),
    e("FRT-E-009", "FRT-PORT-TOLEDO", "FRT-TERM-IRONVILLE", "marine", "documented_vessel_delivery_to_terminal", "steel_or_metal_products;industrial_materials", "documented_flow", "current_2026", "phase5a_toledo_port", "high", "Port authority documents product delivered by vessel to the Ironville direct-reduction plant; quantity is intentionally not used."),
    e("FRT-E-010", "FRT-TERM-IRONVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "documented_finished_product_exit", "steel_or_metal_products", "documented_flow", "current_2026", "phase5a_toledo_port", "high", "Port authority states that finished HBI product leaves via rail; destination remains generalized."),
    e("FRT-E-011", "FRT-TERM-IRONVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "documented_finished_product_exit", "steel_or_metal_products", "documented_flow", "current_2026", "phase5a_toledo_port", "high", "Port authority states that finished HBI product leaves via truck; destination and route remain generalized."),
    e("FRT-E-012", "FRT-RAIL-NS", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "regional_corridor_to_market", "steel_or_metal_products;aggregate;industrial_materials", "documented_corridor", "current_2026", "phase5a_ntad_rail", "medium", "Class I corridor geometry supports regional connectivity, not a facility-to-market shipment claim."),
    e("FRT-E-013", "FRT-RAIL-CSXT", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "regional_corridor_to_market", "steel_or_metal_products;aggregate;industrial_materials", "documented_corridor", "current_2026", "phase5a_ntad_rail", "medium", "Class I corridor geometry supports regional connectivity, not a facility-to-market shipment claim."),
    e("FRT-E-014", "FRT-RAIL-CN", "FRT-MKT-GREAT-LAKES", "rail", "regional_corridor_to_market", "container_or_general_freight;industrial_materials", "documented_corridor", "current_2026", "phase5a_ntad_rail", "medium", "Class I corridor geometry supports regional connectivity, not a facility-to-market shipment claim."),
    e("FRT-E-015", "FRT-HWY-I75", "FRT-MKT-MICHIGAN-CANADA", "highway", "regional_freight_connectivity", "container_or_general_freight;automotive;industrial_materials", "documented_corridor", "current_2026", "phase5a_fhwa_faf", "medium", "Freight-relevant public corridor; no facility-specific truck route is inferred."),
    e("FRT-E-016", "FRT-HWY-I80-90", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "regional_freight_connectivity", "container_or_general_freight;agricultural_bulk;aggregate;industrial_materials", "documented_corridor", "current_2026", "phase5a_fhwa_faf", "medium", "Freight-relevant public corridor; no facility-specific truck route is inferred."),
    e("FRT-E-017", "FRT-HWY-I280", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "regional_freight_connectivity", "container_or_general_freight;industrial_materials", "documented_corridor", "current_2026", "phase5a_fhwa_faf", "low", "Primary-road corridor is mapped as context only; no port-terminal or plant-specific movement is inferred."),
    e("FRT-E-018", "FRT-HWY-US23", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "regional_freight_connectivity", "agricultural_bulk;automotive;industrial_materials", "documented_corridor", "current_2026", "phase5a_fhwa_faf", "medium", "Freight-relevant public corridor; no facility-specific truck route is inferred."),
    e("FRT-E-019", "FRT-AG-MIDWEST-BULK", "FRT-MKT-GREAT-LAKES", "multimodal", "broad_agricultural_market_interface", "agricultural_bulk;grain", "generalized_supply_chain", "current_2026", "phase5a_fhwa_faf", "low", "Broad FAF commodity context only; no Toledo-specific elevator, shipment, route, or volume is asserted."),
    e("FRT-E-020", "FRT-FUEL-EXTERNAL", "ENE-EIA-59764", "generalized", "external_fuel_interface", "petroleum_or_fuel", "engineering_logistics_dependency", "current_2026", "phase5a_eia_petroleum", "low", "General fuel-interface relationship only; no pipeline, contract, capacity, or facility route is modeled."),
    e("FRT-E-021", "FRT-FUEL-EXTERNAL", "FRT-MKT-MIDWEST-INDUSTRIAL", "generalized", "external_fuel_supply_context", "petroleum_or_fuel;chemicals", "generalized_supply_chain", "current_2026", "phase5a_eia_petroleum", "low", "External fuel context only; no regional pipeline alignment or quantity is asserted."),
    e("FRT-E-022", "CARB-EXT-AREA-WOODVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "generalized", "aggregate_product_distribution", "aggregate;limestone;agricultural_bulk", "generalized_supply_chain", "current_2026", "phase5a_area_woodville", "medium", "Existing facility/product evidence supports a generalized distribution function, not a route or customer."),
    e("FRT-E-023", "CARB-PROC-MM-WOODVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "generalized", "lime_product_distribution", "lime;industrial_materials;agricultural_bulk", "generalized_supply_chain", "current_2026", "phase5a_mm_woodville", "medium", "Existing processing evidence supports a generalized logistics dependency, not a mode, route, schedule, or quantity."),
    e("FRT-E-024", "CARB-PROC-GRAYMONT-GENOA", "FRT-MKT-MIDWEST-INDUSTRIAL", "generalized", "lime_product_distribution", "lime;industrial_materials", "generalized_supply_chain", "current_2026", "phase5a_graymont_genoa", "medium", "Genoa product role is documented; quarry/feed and freight route remain unresolved."),
    e("FRT-E-025", "BER-PROC-ELMORE", "FRT-MKT-GREAT-LAKES", "generalized", "strategic_material_logistics_dependency", "strategic_materials;industrial_materials", "generalized_supply_chain", "current_2026", "phase5a_materion_elmore", "medium", "Existing nonlocal-feed and broad end-use evidence supports logistics dependency, not a local route or customer."),
    e("FRT-E-026", "BER-LEG-LUCKEY", "FRT-MKT-LICENSED-DISPOSAL", "generalized", "remediation_waste_logistics", "industrial_materials;chemicals", "documented_flow", "current_2026", "phase5a_luckey_logistics", "high", "USACE documents licensed off-site disposal; no hazardous-material route, schedule, or quantity is modeled."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_box(ax, x, y, width, height, label, color, fontsize=8.0):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.3))
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#29343a", wrap=True)


def load_rail() -> gpd.GeoDataFrame:
    if not RAIL_CACHE.exists():
        params = {"where": "1=1", "geometry": "-85.5,40.9,-82.5,42.2", "geometryType": "esriGeometryEnvelope", "inSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID,FRAARCID,STATEAB,RROWNER1,RROWNER2,DIVISION,SUBDIV,BRANCH,YARDNAME,PASSNGR,STRACNET,MILES,KM", "returnGeometry": "true", "outSR": 4326, "f": "geojson"}
        response = requests.get(RAIL_QUERY, params=params, timeout=180)
        response.raise_for_status()
        RAIL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        RAIL_CACHE.write_text(json.dumps(response.json()), encoding="utf-8")
    return gpd.read_file(RAIL_CACHE)


def render_map(nodes: pd.DataFrame) -> None:
    plt.rcParams["svg.hashsalt"] = "western-basin-phase5a-freight"
    plt.rcParams["svg.fonttype"] = "none"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.045, 0.18, 0.58, 0.75], facecolor="#e9e1ce")
    flow = fig.add_axes([0.045, 0.045, 0.58, 0.095], facecolor="#eee5d3")
    side = fig.add_axes([0.66, 0.045, 0.30, 0.885], facecolor="#eee5d3")
    flow.axis("off")
    side.axis("off")
    lake = gpd.read_file(GPKG, layer="water_lake_erie").cx[-85.5:-82.5, 40.9:42.2]
    watersheds = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    water_flow = gpd.read_file(GPKG, layer="water_flowlines_order3")
    roads = gpd.read_file(ROOT / "data/raw/census/tigerweb_primary_roads.geojson")
    roads = roads[roads.NAME.isin(["I- 75", "I- 80", "I- 90", "I- 280", "US Hwy 23"])]
    rail = load_rail()
    owners = rail.RROWNER1.fillna("")
    rail = rail[owners.isin(["NS", "CSXT", "CN"])].copy()
    rail = rail[~rail.SUBDIV.fillna("").str.contains("SPUR|LEAD|TERMINAL|YARD", case=False, regex=True)]
    watersheds.plot(ax=ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.55, zorder=1)
    lake.plot(ax=ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    water_flow.plot(ax=ax, color="#6d9aab", linewidth=0.45, alpha=0.35, zorder=2)
    road_colors = {"I- 75": "#c87938", "I- 80": "#c87938", "I- 90": "#c87938", "I- 280": "#d49b50", "US Hwy 23": "#d49b50"}
    for name, frame in roads.groupby("NAME"):
        frame.plot(ax=ax, color=road_colors.get(name, "#d49b50"), linewidth=1.25, alpha=0.74, zorder=3)
    rail_colors = {"NS": "#3d454d", "CSXT": "#7b5268", "CN": "#496f68"}
    for owner, frame in rail.groupby(owners.loc[frame.index] if False else "RROWNER1"):
        frame.plot(ax=ax, color=rail_colors.get(owner, "#4b5257"), linewidth=0.72, alpha=0.70, zorder=4)
    points = nodes[nodes.latitude != ""].copy()
    point_styles = {"port": ("#1c5b78", "*", 190), "industrial_site": ("#b65d45", "o", 70), "material_processor": ("#7a4f92", "s", 78)}
    for node_type, frame in points.groupby("node_type"):
        color, marker, size = point_styles[node_type]
        ax.scatter(frame.longitude.astype(float), frame.latitude.astype(float), color=color, marker=marker, s=size, edgecolor="#fff9ed", linewidth=1.0, zorder=7)
    labels = {
        "FRT-PORT-TOLEDO": ("Port of Toledo\n(address-level anchor)", (7, 8)),
        "CARB-EXT-AREA-WOODVILLE": ("Area Aggregates\nWoodville", (6, -24)),
        "CARB-PROC-MM-WOODVILLE": ("Martin Marietta\nWoodville", (6, 7)),
        "CARB-PROC-GRAYMONT-GENOA": ("Graymont Genoa", (6, -22)),
        "BER-PROC-ELMORE": ("Materion Elmore", (6, 7)),
        "BER-LEG-LUCKEY": ("Luckey remediation", (6, -22)),
    }
    for _, row in points.iterrows():
        if row.node_id in labels:
            text, offset = labels[row.node_id]
            ax.annotate(text, (float(row.longitude), float(row.latitude)), xytext=offset, textcoords="offset points", fontsize=7.2, color="#293238", bbox=dict(boxstyle="round,pad=.2", facecolor="#f8f2e5", edgecolor="#b18a72", alpha=0.92), zorder=8)
    ax.set_xlim(-85.25, -82.72)
    ax.set_ylim(41.08, 42.10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("MAP 17 — WESTERN BASIN FREIGHT & INDUSTRIAL FLOW SYSTEM, 2026", loc="left", fontsize=16.2, weight="bold", color="#17384b", pad=15)
    ax.text(0.01, 0.965, "Selected public freight corridors and sourced industrial/material nodes", transform=ax.transAxes, fontsize=9.5, color="#4d5b5c", va="top")
    ax.text(0.01, 0.025, "Corridor presence ≠ documented shipment. Facility routes and quantities are intentionally absent.", transform=ax.transAxes, fontsize=7.6, color="#4f514b")
    ax.legend(handles=[Line2D([0], [0], marker="*", color="none", markerfacecolor="#1c5b78", markeredgecolor="white", markersize=11, label="Port"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#b65d45", markeredgecolor="white", markersize=8, label="Industrial / bulk site"), Line2D([0], [0], marker="s", color="none", markerfacecolor="#7a4f92", markeredgecolor="white", markersize=8, label="Material processor"), Line2D([0], [0], color="#3d454d", linewidth=2, label="Class I rail corridor"), Line2D([0], [0], color="#c87938", linewidth=2, label="Major highway corridor")], loc="upper left", bbox_to_anchor=(0.01, 0.90), frameon=True, facecolor="#f8f2e5", edgecolor="#a69876", fontsize=7.5)
    flow.text(0.005, 0.82, "COMMODITY / MODE INTERFACES", fontsize=9.1, weight="bold", color="#17384b")
    boxes = [(0.01, "AGRICULTURE\n/ BULK", "#b38a3f"), (0.20, "AGGREGATE\n/ LIME", "#7a4f92"), (0.39, "PORT / RAIL\n/ HIGHWAY", "#1c5b78"), (0.58, "INDUSTRY /\nSTRATEGIC", "#b65d45"), (0.79, "EXTERNAL\nMARKETS", "#527e8b")]
    for x, label, color in boxes:
        draw_box(flow, x, 0.16, 0.14, 0.50, label, color, 6.8)
    for x in [0.15, 0.34, 0.53, 0.72]:
        flow.add_patch(FancyArrowPatch((x, 0.41), (x + 0.04, 0.41), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0, linestyle="--"))
    flow.text(0.01, 0.03, "Dashed arrows = generalized functional flow; solid map lines = public corridor context.", fontsize=7.3, color="#4f514b")
    side.text(0.04, 0.975, "FREIGHT STRUCTURE", fontsize=13.2, weight="bold", color="#17384b", va="top")
    side.text(0.04, 0.94, "A bounded 2026 baseline of corridors, nodes, and broad commodity functions.", fontsize=8.5, color="#4d5b5c", va="top", wrap=True)
    sections = [("MARINE", "Port of Toledo: 13 terminals, Seaway connection, bulk/general cargo, on-dock Class I rail, and documented Ironville vessel/truck/rail functions.", "#1c5b78"), ("RAIL", "NTAD Class I corridor geometry for NS, CSX, and CN. W&LE is retained as a listed regional interface without invented geometry.", "#3d454d"), ("HIGHWAY", "I-75, I-80/I-90, I-280, and US-23 primary-road corridors. No plant-specific truck routes or counts.", "#c87938"), ("FUEL", "Generalized external petroleum/fuel interface only. No pipeline alignment, capacity, station, valve, or contract route.", "#9a6647"), ("MATERIALS", "Woodville, Genoa, Elmore, and Luckey reuse existing sourced nodes. Freight relationships remain generalized unless the source documents a function.", "#7a4f92"), ("CORRIDOR TEST", "Materials Corridor finding: B — WEAKLY SUPPORTED. Network relationships exist, but the evidence does not justify a polygon, named route, sixth macroregion, or single corridor claim.", "#b65d45")]
    y = 0.875
    for title, body, color in sections:
        side.add_patch(FancyBboxPatch((0.03, y - 0.115), 0.94, 0.105, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.15))
        side.text(0.06, y - 0.035, title, fontsize=8.2, weight="bold", color=color, va="top")
        side.text(0.06, y - 0.062, body, fontsize=7.0, color="#343b3d", va="top", wrap=True, linespacing=1.12)
        y -= 0.13
    side.text(0.04, 0.115, "BOUNDARIES", fontsize=10.0, weight="bold", color="#17384b")
    side.text(0.04, 0.09, "No shipment simulation, route optimization, exact facility-to-facility route, hazardous-material route, schedule, train/truck/vessel count, pipeline capacity, or sensitive logistics topology.\n\nPort proximity, corridor presence, and material function are not treated as proof of a commercial shipment.", fontsize=7.6, color="#3f4645", va="top", linespacing=1.28)
    fig.savefig(output_png := MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def render_flow_figure() -> None:
    fig, ax = plt.subplots(figsize=(13, 5.5), facecolor="#f1eadc")
    ax.set_facecolor("#eee5d3")
    ax.axis("off")
    boxes = [(0.05, 0.52, "AGRICULTURE\n/ BULK", "#b38a3f"), (0.05, 0.16, "AGGREGATES\n/ LIME", "#7a4f92"), (0.31, 0.34, "PORT / RAIL /\nHIGHWAY INTERFACES", "#1c5b78"), (0.59, 0.52, "INDUSTRIAL /\nSTRATEGIC MATERIALS", "#b65d45"), (0.59, 0.16, "EXTERNAL FUEL\nINTERFACE", "#9a6647"), (0.85, 0.34, "EXTERNAL\nMARKETS / DISPOSAL", "#527e8b")]
    for x, y, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 0.12, 0.22, boxstyle="round,pad=.02", facecolor="#f8f2e5", edgecolor=color, linewidth=1.5, transform=ax.transAxes))
        ax.text(x + 0.06, y + 0.11, label, ha="center", va="center", fontsize=9, color="#29343a", transform=ax.transAxes)
    for start, end in [((0.17, 0.63), (0.31, 0.45)), ((0.17, 0.27), (0.31, 0.43)), ((0.43, 0.45), (0.59, 0.63)), ((0.43, 0.43), (0.85, 0.45)), ((0.71, 0.63), (0.85, 0.45)), ((0.17, 0.27), (0.59, 0.27))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, linewidth=1.4, linestyle="--", color="#626969", transform=ax.transAxes))
    ax.text(0.05, 0.90, "FREIGHT COMMODITY INTERFACES — WESTERN BASIN, 2026", fontsize=15, weight="bold", color="#17384b", transform=ax.transAxes)
    ax.text(0.05, 0.82, "Broad documented and generalized functions; not a shipment-volume or route model.", fontsize=9.5, color="#4d595a", transform=ax.transAxes)
    ax.text(0.05, 0.04, "Dashed connectors = generalized functional relationships. Exact customers, routes, schedules, and quantities are intentionally absent.", fontsize=8, color="#4f514b", transform=ax.transAxes)
    fig.savefig(FLOW_FIGURE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = FLOW_FIGURE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    NETWORKS.mkdir(parents=True, exist_ok=True)
    MAPS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    nodes = pd.DataFrame(NODES, columns=NODE_COLUMNS)
    edges = pd.DataFrame(EDGES, columns=EDGE_COLUMNS)
    nodes.to_csv(NODES_PATH, index=False)
    edges.to_csv(EDGES_PATH, index=False)
    render_map(nodes)
    render_flow_figure()
    artifacts = [NODES_PATH, EDGES_PATH, RAIL_CACHE, MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg"), FLOW_FIGURE.with_suffix(".png"), FLOW_FIGURE.with_suffix(".svg")]
    manifest = {"phase": "5A", "generated": RETRIEVED_DATE, "status": "baseline", "counts": {"nodes": len(nodes), "edges": len(edges), "marine_nodes": int((nodes["mode"] == "marine").sum()), "rail_nodes": int((nodes["mode"] == "rail").sum()), "highway_nodes": int((nodes["mode"] == "highway").sum()), "industrial_material_nodes": int(nodes["node_type"].isin(["industrial_site", "material_processor"]).sum())}, "materials_corridor_test": "B — WEAKLY SUPPORTED", "artifacts": {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
