"""Build Phase 5B freight evidence and interchange validation artifacts."""
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

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
RAW = ROOT / "data/raw/transportation"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

CROSSWALK = ANALYSIS / "freight_evidence_crosswalk.csv"
RELATIONSHIPS = NETWORKS / "freight_evidence_relationships.csv"
INTERCHANGE = ANALYSIS / "freight_interchange_matrix.csv"
MAP_BASE = MAPS / "18_freight_evidence_interchange_2026"
MANIFEST = REPORTS / "freight_evidence_manifest.json"
RAIL_CACHE = RAW / "ntad_class1_rail_network_western_basin.geojson"
RETRIEVED_DATE = "2026-09-02"

CROSSWALK_COLUMNS = ["evidence_id", "phase5a_object_id", "object_type", "facility_or_corridor", "mode", "commodity_class", "previous_basis", "evidence_class", "source_id", "source_date", "confidence", "upgrade_status", "notes"]
RELATIONSHIP_COLUMNS = ["relationship_id", "phase5a_edge_id", "from_id", "to_id", "mode", "commodity_class", "evidence_class", "upgrade_status", "source_id", "confidence", "notes"]
INTERCHANGE_COLUMNS = ["interface_id", "interface_name", "mode_a", "mode_b", "physical_co_location", "documented_interchange", "evidence_class", "source_id", "confidence", "notes"]

CROSSWALK_ROWS = [
    ("EVID-001", "FRT-PORT-TOLEDO", "port", "Port of Toledo / 13-terminal gateway", "marine", "container_or_general_freight;aggregate;steel_or_metal_products;industrial_materials", "generalized_supply_chain", "documented_facility_access", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port authority documents 13 terminals, storage, cargo equipment, and seaway/global-market connection."),
    ("EVID-002", "FRT-PORT-TOLEDO", "port", "Facility #1 general cargo dock / warehouse", "marine", "container_or_general_freight;industrial_materials", "generalized_supply_chain", "documented_facility_access", "phase5b_toledo_annual_report", "2025 annual report", "high", "strengthened", "Port annual-report material documents the Facility #1 general-cargo warehouse and terminal modernization; no customer or shipment assigned."),
    ("EVID-003", "FRT-PORT-TOLEDO", "port", "Adjacent liquid-bulk transloading operation", "marine", "petroleum_or_fuel;chemicals", "generalized_supply_chain", "documented_facility_access", "phase5b_toledo_annual_report", "2025 annual report", "high", "strengthened", "Port annual-report material documents an adjacent liquid-bulk transloading operation; no product, customer, quantity, or route assigned."),
    ("EVID-004", "FRT-PORT-TOLEDO", "port", "Port on-dock Class I rail access", "rail", "container_or_general_freight;industrial_materials", "interchange", "documented_interchange", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "On-dock Class I rail access is documented; a specific terminal/carrier assignment is not universalized."),
    ("EVID-005", "FRT-RAIL-NS", "rail_interface", "Norfolk Southern port/corridor interface", "rail", "container_or_general_freight;industrial_materials", "documented_corridor", "documented_interchange", "phase5a_toledo_port", "current 2026 page", "medium", "strengthened", "Port public transportation material lists NS and documents Class I rail access; exact facility use remains unassigned."),
    ("EVID-006", "FRT-RAIL-CSXT", "rail_interface", "CSX port/corridor interface", "rail", "container_or_general_freight;industrial_materials", "documented_corridor", "documented_interchange", "phase5a_toledo_port", "current 2026 page", "medium", "strengthened", "Port public transportation material lists CSX; exact facility use remains unassigned."),
    ("EVID-007", "FRT-RAIL-CN", "rail_interface", "Canadian National port/corridor interface", "rail", "container_or_general_freight;industrial_materials", "documented_corridor", "documented_interchange", "phase5a_toledo_port", "current 2026 page", "medium", "strengthened", "Port public transportation material lists CN; exact facility use remains unassigned."),
    ("EVID-008", "FRT-RAIL-WLE", "rail_interface", "Wheeling & Lake Erie listed port interface", "rail", "aggregate;lime;industrial_materials", "interchange", "proximity_only", "phase5a_toledo_port", "current 2026 page", "medium", "unchanged", "Public carrier listing supports relevance but does not document a specific Port of Toledo interchange or line use."),
    ("EVID-009", "FRT-HWY-I75", "highway_interface", "I-75 Port of Toledo access", "highway", "container_or_general_freight;automotive;industrial_materials", "documented_corridor", "documented_facility_access", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port identifies I-75 as a crossroads; no plant-specific truck route is established."),
    ("EVID-010", "FRT-HWY-I80-90", "highway_interface", "I-80/I-90 Port of Toledo access", "highway", "container_or_general_freight;aggregate;industrial_materials", "documented_corridor", "documented_facility_access", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port identifies I-80/90 as a crossroads; no plant-specific truck route is established."),
    ("EVID-011", "FRT-MKT-MICHIGAN-CANADA", "external_market", "Michigan/Canada heavy-haul interface", "highway", "container_or_general_freight;industrial_materials;automotive", "generalized_supply_chain", "documented_corridor", "phase5a_toledo_port", "current 2026 page", "medium", "strengthened", "Port documents designated heavy-haul routes; exact permits and route paths are not modeled."),
    ("EVID-012", "FRT-TERM-IRONVILLE", "terminal", "Ironville vessel input", "marine", "steel_or_metal_products;industrial_materials", "documented_flow", "documented_shipment_relationship", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port authority documents vessel-delivered product for the Ironville direct-reduction plant; no quantity is used."),
    ("EVID-013", "FRT-TERM-IRONVILLE", "terminal", "Ironville finished-product rail output", "rail", "steel_or_metal_products", "documented_flow", "documented_shipment_relationship", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port authority documents finished product leaving by rail; destination remains generalized."),
    ("EVID-014", "FRT-TERM-IRONVILLE", "terminal", "Ironville finished-product truck output", "highway", "steel_or_metal_products", "documented_flow", "documented_shipment_relationship", "phase5a_toledo_port", "current 2026 page", "high", "confirmed", "Port authority documents finished product leaving by truck; destination and route remain generalized."),
    ("EVID-015", "CARB-EXT-AREA-WOODVILLE", "industrial_site", "Area Aggregates Woodville", "generalized", "aggregate;limestone;agricultural_bulk", "generalized_supply_chain", "proximity_only", "phase5a_area_woodville", "2026 permit context", "medium", "unchanged", "Facility and product evidence exists, but no specific freight access, customer, mode, route, or quantity is documented."),
    ("EVID-016", "CARB-PROC-MM-WOODVILLE", "material_processor", "Martin Marietta Woodville", "generalized", "lime;limestone;industrial_materials", "generalized_supply_chain", "proximity_only", "phase5a_mm_woodville", "2026 facility page", "medium", "unchanged", "Processing is documented, but no specific freight access, customer, mode, route, or quantity is documented."),
    ("EVID-017", "CARB-PROC-GRAYMONT-GENOA", "material_processor", "Graymont Genoa", "generalized", "lime;limestone;industrial_materials", "generalized_supply_chain", "unresolved", "phase5a_graymont_genoa", "2026 facility material", "medium", "unresolved", "Genoa product role is documented; quarry/feed and freight access remain unresolved."),
    ("EVID-018", "BER-PROC-ELMORE", "material_processor", "Materion Elmore", "generalized", "strategic_materials;industrial_materials", "generalized_supply_chain", "generalized_logistics_dependency", "phase5a_materion_elmore", "2026 facility record", "medium", "unchanged", "Nonlocal feed and advanced processing are documented; mode, route, schedule, and quantity are not."),
    ("EVID-019", "BER-LEG-LUCKEY", "industrial_site", "Luckey FUSRAP remediation", "generalized", "industrial_materials;chemicals", "documented_flow", "documented_shipment_relationship", "phase5a_luckey_logistics", "2026 remediation source", "high", "confirmed", "Licensed off-site disposal logistics are documented at program level; no hazardous-material route is modeled."),
    ("EVID-020", "FRT-AG-MIDWEST-BULK", "agricultural_node", "Midwest agricultural bulk context", "multimodal", "agricultural_bulk;grain", "generalized_supply_chain", "unresolved", "phase5a_fhwa_faf", "2026 FAF context", "low", "unresolved", "Broad commodity context does not document a Toledo-specific elevator, port shipment, route, or volume."),
]

RELATIONSHIP_ROWS = [
    ("EREL-001", "FRT-E-002", "FRT-PORT-TOLEDO", "FRT-MKT-MICHIGAN-CANADA", "highway", "container_or_general_freight;industrial_materials", "documented_corridor", "strengthened", "phase5a_toledo_port", "medium", "Port page provides designated Michigan/Canada heavy-haul evidence; exact route and permit remain outside scope."),
    ("EREL-002", "FRT-E-003", "FRT-PORT-TOLEDO", "FRT-RAIL-NS", "rail", "container_or_general_freight;industrial_materials", "documented_interchange", "strengthened", "phase5a_toledo_port", "medium", "On-dock Class I access plus public NS listing strengthens the interface; terminal-specific use is not claimed."),
    ("EREL-003", "FRT-E-004", "FRT-PORT-TOLEDO", "FRT-RAIL-CSXT", "rail", "container_or_general_freight;industrial_materials", "documented_interchange", "strengthened", "phase5a_toledo_port", "medium", "Public port carrier listing supports relevance; no terminal-specific use is claimed."),
    ("EREL-004", "FRT-E-005", "FRT-PORT-TOLEDO", "FRT-RAIL-CN", "rail", "container_or_general_freight;industrial_materials", "documented_interchange", "strengthened", "phase5a_toledo_port", "medium", "Public port carrier listing supports relevance; no terminal-specific use is claimed."),
    ("EREL-005", "FRT-E-006", "FRT-PORT-TOLEDO", "FRT-RAIL-WLE", "rail", "aggregate;lime;industrial_materials", "proximity_only", "unchanged", "phase5a_toledo_port", "medium", "W&LE is publicly listed but a specific interchange remains unverified."),
    ("EREL-006", "FRT-E-007", "FRT-PORT-TOLEDO", "FRT-HWY-I75", "highway", "container_or_general_freight;industrial_materials", "documented_facility_access", "confirmed", "phase5a_toledo_port", "high", "Port identifies I-75 access; no plant-specific truck assignment is made."),
    ("EREL-007", "FRT-E-008", "FRT-PORT-TOLEDO", "FRT-HWY-I80-90", "highway", "container_or_general_freight;aggregate;industrial_materials", "documented_facility_access", "confirmed", "phase5a_toledo_port", "high", "Port identifies I-80/90 access; no plant-specific truck assignment is made."),
    ("EREL-008", "FRT-E-009", "FRT-PORT-TOLEDO", "FRT-TERM-IRONVILLE", "marine", "steel_or_metal_products;industrial_materials", "documented_shipment_relationship", "confirmed", "phase5a_toledo_port", "high", "Vessel-delivered input to Ironville is documented; quantity and route remain absent."),
    ("EREL-009", "FRT-E-010", "FRT-TERM-IRONVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "steel_or_metal_products", "documented_shipment_relationship", "confirmed", "phase5a_toledo_port", "high", "Finished product leaves Ironville by rail; destination is generalized."),
    ("EREL-010", "FRT-E-011", "FRT-TERM-IRONVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "steel_or_metal_products", "documented_shipment_relationship", "confirmed", "phase5a_toledo_port", "high", "Finished product leaves Ironville by truck; destination and route are generalized."),
    ("EREL-011", "FRT-E-025", "BER-PROC-ELMORE", "FRT-MKT-GREAT-LAKES", "generalized", "strategic_materials;industrial_materials", "generalized_logistics_dependency", "unchanged", "phase5a_materion_elmore", "medium", "Elmore logistics dependency remains generalized; no specific freight mode or route is documented."),
    ("EREL-012", "FRT-E-026", "BER-LEG-LUCKEY", "FRT-MKT-LICENSED-DISPOSAL", "generalized", "industrial_materials;chemicals", "documented_shipment_relationship", "confirmed", "phase5a_luckey_logistics", "high", "Licensed off-site remediation disposal is documented without a route or quantity."),
]

INTERCHANGE_ROWS = [
    ("INT-001", "Port on-dock Class I rail", "marine", "rail", "Port facility/on-dock access documented", "documented", "documented_interchange", "phase5a_toledo_port", "high", "Physical access and port rail interface are documented; carrier/terminal assignment is not universal."),
    ("INT-002", "Port marine to highway heavy-haul", "marine", "highway", "Port access and designated heavy-haul context", "documented", "documented_facility_access", "phase5a_toledo_port", "medium", "Access is documented; no exact terminal-to-road movement is modeled."),
    ("INT-003", "Facility #1 general cargo to liquid bulk context", "marine", "generalized", "Adjacent port facilities documented", "documented", "documented_facility_access", "phase5b_toledo_annual_report", "high", "Annual-report material documents general-cargo warehouse and adjacent liquid-bulk operation; no transfer route or product assignment."),
    ("INT-004", "Ironville marine input to rail output", "marine", "rail", "Ironville terminal role documented", "not established", "documented_shipment_relationship", "phase5a_toledo_port", "high", "Vessel input and rail output are documented, but a physical transfer design is not modeled."),
    ("INT-005", "Ironville marine input to truck output", "marine", "highway", "Ironville terminal role documented", "not established", "documented_shipment_relationship", "phase5a_toledo_port", "high", "Vessel input and truck output are documented, but a physical transfer design is not modeled."),
    ("INT-006", "Ironville rail and highway outputs", "rail", "highway", "Same generalized Ironville industrial role", "not established", "documented_shipment_relationship", "phase5a_toledo_port", "high", "Both outputs are documented; rail-highway transfer or shared route is not asserted."),
    ("INT-007", "Port NS/CSX/CN carrier interfaces", "marine", "rail", "Port carrier listings and Class I access", "documented", "documented_interchange", "phase5a_toledo_port", "medium", "Carrier relevance is documented at port level; specific interchange operations remain unverified."),
    ("INT-008", "W&LE port interface", "marine", "rail", "Public carrier listing only", "not established", "proximity_only", "phase5a_toledo_port", "medium", "Listing does not establish a specific interchange or freight path."),
    ("INT-009", "Woodville/Genoa/Elmore material sites to corridors", "generalized", "rail", "Facility/corridor geography only", "not established", "proximity_only", "phase5a_mm_woodville", "low", "No site-specific access or modal relationship is established by proximity."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_box(ax, x, y, width, height, label, color, fontsize=8.0):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.3))
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#29343a", wrap=True)


def render_map() -> None:
    plt.rcParams["svg.hashsalt"] = "western-basin-phase5b-evidence-interchange"
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
    rail = gpd.read_file(RAIL_CACHE)
    rail = rail[rail.RROWNER1.fillna("").isin(["NS", "CSXT", "CN"])].copy()
    rail = rail[~rail.SUBDIV.fillna("").str.contains("SPUR|LEAD|TERMINAL|YARD", case=False, regex=True)]
    watersheds.plot(ax=ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.48, zorder=1)
    lake.plot(ax=ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    water_flow.plot(ax=ax, color="#6d9aab", linewidth=0.4, alpha=0.24, zorder=2)
    for _, frame in roads.groupby("NAME"):
        frame.plot(ax=ax, color="#d1a05b", linewidth=1.0, alpha=0.45, zorder=3)
    rail_colors = {"NS": "#3d454d", "CSXT": "#7b5268", "CN": "#496f68"}
    for owner, frame in rail.groupby("RROWNER1"):
        frame.plot(ax=ax, color=rail_colors.get(owner, "#4b5257"), linewidth=0.6, alpha=0.35, zorder=4)
    evidence = pd.DataFrame(CROSSWALK_ROWS, columns=CROSSWALK_COLUMNS)
    freight_nodes = pd.read_csv(NETWORKS / "freight_system_nodes.csv", dtype=str).fillna("")
    rank = {"confirmed": 4, "strengthened": 3, "unchanged": 2, "downgraded": 1, "unresolved": 0}
    evidence["rank"] = evidence.upgrade_status.map(rank)
    evidence_status = evidence.sort_values(["phase5a_object_id", "rank"], ascending=[True, False]).drop_duplicates("phase5a_object_id")[["phase5a_object_id", "upgrade_status"]]
    nodes = freight_nodes.merge(evidence_status, left_on="node_id", right_on="phase5a_object_id", how="left")
    nodes["upgrade_status"] = nodes.upgrade_status.fillna("unchanged")
    points = nodes[(nodes.latitude != "") & (nodes.longitude != "")].copy()
    colors = {"confirmed": "#4f8a72", "strengthened": "#1c6f83", "unchanged": "#8c8b7d", "unresolved": "#b65d45"}
    markers = {"port": "*", "industrial_site": "o", "material_processor": "s"}
    for _, row in points.iterrows():
        marker = markers.get(row.node_type, "o")
        color = colors.get(row.upgrade_status, "#8c8b7d")
        ax.scatter([float(row.longitude)], [float(row.latitude)], marker=marker, s=190 if row.node_type == "port" else 76, color=color, edgecolor="#fff9ed", linewidth=1.0, zorder=7)
    labels = {"FRT-PORT-TOLEDO": ("Port of Toledo\nconfirmed address anchor", (7, 8)), "CARB-EXT-AREA-WOODVILLE": ("Area Aggregates\naccess unresolved", (6, -23)), "CARB-PROC-MM-WOODVILLE": ("Martin Marietta\naccess unresolved", (6, 7)), "CARB-PROC-GRAYMONT-GENOA": ("Graymont Genoa\nfeed/access unresolved", (6, -23)), "BER-PROC-ELMORE": ("Materion Elmore\ngeneralized logistics", (6, 7)), "BER-LEG-LUCKEY": ("Luckey remediation\nlicensed disposal", (6, -23))}
    for _, row in points.iterrows():
        if row.phase5a_object_id in labels:
            label, offset = labels[row.phase5a_object_id]
            ax.annotate(label, (float(row.longitude), float(row.latitude)), xytext=offset, textcoords="offset points", fontsize=7.1, color="#293238", bbox=dict(boxstyle="round,pad=.2", facecolor="#f8f2e5", edgecolor=colors.get(row.upgrade_status, "#8c8b7d"), alpha=0.93), zorder=8)
    ax.set_xlim(-85.25, -82.72)
    ax.set_ylim(41.08, 42.10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("MAP 18 — FREIGHT EVIDENCE & INTERCHANGE VALIDATION, 2026", loc="left", fontsize=16.2, weight="bold", color="#17384b", pad=15)
    ax.text(0.01, 0.965, "Evidence-strengthening view over Map 17 corridors and existing sourced material nodes", transform=ax.transAxes, fontsize=9.3, color="#4d5b5c", va="top")
    ax.text(0.01, 0.025, "Confirmed access/interchange ≠ complete shipment route. Unresolved evidence remains explicit.", transform=ax.transAxes, fontsize=7.6, color="#4f514b")
    ax.legend(handles=[Line2D([0], [0], marker="*", color="none", markerfacecolor="#1c6f83", markeredgecolor="white", markersize=11, label="Port / strengthened"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#4f8a72", markeredgecolor="white", markersize=8, label="Confirmed facility flow"), Line2D([0], [0], marker="s", color="none", markerfacecolor="#8c8b7d", markeredgecolor="white", markersize=8, label="Unchanged/generalized"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#b65d45", markeredgecolor="white", markersize=8, label="Unresolved"), Line2D([0], [0], color="#3d454d", linewidth=2, label="Class I corridor"), Line2D([0], [0], color="#d1a05b", linewidth=2, label="Highway context")], loc="upper left", bbox_to_anchor=(0.01, 0.90), frameon=True, facecolor="#f8f2e5", edgecolor="#a69876", fontsize=7.2)
    flow.text(0.005, 0.82, "EVIDENCE CLASSES", fontsize=9.1, weight="bold", color="#17384b")
    for x, label, color in [(0.01, "DOCUMENTED\nACCESS", "#1c6f83"), (0.20, "DOCUMENTED\nINTERCHANGE", "#4f8a72"), (0.39, "DOCUMENTED\nFLOW", "#5a7d5e"), (0.58, "CORRIDOR\nONLY", "#8c8b7d"), (0.79, "UNRESOLVED\n/ PROXIMITY", "#b65d45")]:
        draw_box(flow, x, 0.16, 0.14, 0.50, label, color, 6.6)
    for x in [0.15, 0.34, 0.53, 0.72]:
        flow.add_patch(FancyArrowPatch((x, 0.41), (x + 0.04, 0.41), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0, linestyle="--"))
    flow.text(0.01, 0.03, "Map lines are public corridor context; evidence classes describe relationship support, not route geometry.", fontsize=7.2, color="#4f514b")
    side.text(0.04, 0.975, "EVIDENCE STRENGTH", fontsize=13.1, weight="bold", color="#17384b", va="top")
    side.text(0.04, 0.94, "Map 18 asks where the evidence supports actual access or interchange—not merely geographic proximity.", fontsize=8.4, color="#4d5b5c", va="top", wrap=True)
    sections = [("PORT", "Strongest evidence: on-dock Class I access, I-75/I-80/90 access, general-cargo warehouse, liquid-bulk transloading, and Ironville vessel/truck/rail roles.", "#1c6f83"), ("RAIL", "NS, CSX, and CN are strengthened to public port/corridor interfaces. W&LE remains listed but specific interchange is unresolved.", "#3d454d"), ("MODAL", "Marine↔rail and marine↔highway access are documented at port level. Ironville truck/rail outputs are documented, but transfer design is not.", "#4f8a72"), ("FACILITIES", "Woodville and Genoa freight access remain proximity-only or unresolved; Elmore remains generalized; Luckey licensed disposal is documented.", "#7a4f92"), ("COMMODITIES", "Iron/HBI and general industrial/bulk roles are strongest. Port-specific grain activity remains unresolved; no quantities are added.", "#b38a3f"), ("CORRIDOR TEST", "B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT. Industrial relationships exist, but “Materials Corridor” remains a loose network motif, not a geographic corridor.", "#b65d45")]
    y = 0.875
    for title, body, color in sections:
        side.add_patch(FancyBboxPatch((0.03, y - 0.115), 0.94, 0.105, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.15))
        side.text(0.06, y - 0.035, title, fontsize=8.1, weight="bold", color=color, va="top")
        side.text(0.06, y - 0.062, body, fontsize=6.95, color="#343b3d", va="top", wrap=True, linespacing=1.12)
        y -= 0.13
    side.text(0.04, 0.115, "BOUNDARIES", fontsize=10.0, weight="bold", color="#17384b")
    side.text(0.04, 0.09, "No shipment simulation, exact facility route, hazardous-material route, pipeline detail, quantity, schedule, train/truck/vessel count, or sensitive logistics topology.", fontsize=7.5, color="#3f4645", va="top", linespacing=1.25)
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    for directory in [NETWORKS, ANALYSIS, MAPS, FIGURES, REPORTS]:
        directory.mkdir(parents=True, exist_ok=True)
    crosswalk = pd.DataFrame(CROSSWALK_ROWS, columns=CROSSWALK_COLUMNS)
    relationships = pd.DataFrame(RELATIONSHIP_ROWS, columns=RELATIONSHIP_COLUMNS)
    interchange = pd.DataFrame(INTERCHANGE_ROWS, columns=INTERCHANGE_COLUMNS)
    crosswalk.to_csv(CROSSWALK, index=False)
    relationships.to_csv(RELATIONSHIPS, index=False)
    interchange.to_csv(INTERCHANGE, index=False)
    render_map()
    artifacts = [CROSSWALK, RELATIONSHIPS, INTERCHANGE, MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    manifest = {"phase": "5B", "generated": RETRIEVED_DATE, "status": "evidence_validation", "counts": {"crosswalk": len(crosswalk), "evidence_relationships": len(relationships), "interchange_rows": len(interchange)}, "materials_corridor_test": "B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT", "artifacts": {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
