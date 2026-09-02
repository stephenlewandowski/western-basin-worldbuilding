"""Build Phase 5C qualitative freight dependencies and critical interfaces."""
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
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"
RAIL = ROOT / "data/raw/transportation/ntad_class1_rail_network_western_basin.geojson"

DEP_EDGES = NETWORKS / "freight_dependency_edges.csv"
DEP_REGISTER = ANALYSIS / "freight_dependency_register.csv"
MODAL_MATRIX = ANALYSIS / "modal_substitutability_matrix.csv"
MATRIX = FIGURES / "freight_dependency_matrix_2026.csv"
MAP_BASE = MAPS / "19_freight_dependencies_critical_interfaces_2026"
MATRIX_BASE = FIGURES / "freight_dependency_matrix_2026"
MANIFEST = REPORTS / "freight_dependency_manifest.json"
RETRIEVED_DATE = "2026-09-02"

EDGE_COLUMNS = ["dependency_id", "source_node_id", "dependent_node_id", "domain", "dependency_type", "dependency_strength", "evidence_confidence", "modal_alternative", "external_orientation", "relationship_basis", "source_id", "notes"]
REGISTER_COLUMNS = ["register_id", "domain", "system_node_id", "node_name", "primary_modes", "dependency_classes", "dependency_strength", "known_redundancy", "unknown_redundancy", "external_orientation", "evidence_confidence", "source_id", "notes"]
MODAL_COLUMNS = ["system_function", "marine_dependence", "rail_dependence", "highway_dependence", "external_market_dependence", "interchange_dependence", "modal_substitutability", "evidence_confidence", "notes"]
MATRIX_COLUMNS = MODAL_COLUMNS

EDGE_ROWS = [
    ("FDE-001", "FRT-PORT-TOLEDO", "FRT-MKT-GREAT-LAKES", "port_marine", "marine_gateway_dependency", "high", "high", "low", "high", "documented_corridor", "phase5a_toledo_port", "Port of Toledo is a marine gateway to Great Lakes/St. Lawrence markets; no volume or vessel schedule."),
    ("FDE-002", "FRT-PORT-TOLEDO", "FRT-RAIL-NS", "port_marine", "interchange_dependency", "high", "moderate", "moderate", "high", "documented_interchange", "phase5a_toledo_port", "On-dock Class I access and public NS interface are documented; carrier substitution is not evaluated."),
    ("FDE-003", "FRT-PORT-TOLEDO", "FRT-RAIL-CSXT", "port_marine", "interchange_dependency", "moderate", "moderate", "moderate", "high", "documented_interchange", "phase5a_toledo_port", "Public port carrier listing supports relevance; terminal assignment is not established."),
    ("FDE-004", "FRT-PORT-TOLEDO", "FRT-RAIL-CN", "port_marine", "interchange_dependency", "moderate", "moderate", "moderate", "high", "documented_interchange", "phase5a_toledo_port", "Public port carrier listing supports relevance; terminal assignment is not established."),
    ("FDE-005", "FRT-PORT-TOLEDO", "FRT-HWY-I75", "port_marine", "highway_dependency", "high", "high", "high", "high", "documented_facility_access", "phase5a_toledo_port", "Port access to I-75 is documented; no plant-specific truck route is modeled."),
    ("FDE-006", "FRT-PORT-TOLEDO", "FRT-HWY-I80-90", "port_marine", "highway_dependency", "high", "high", "moderate", "high", "documented_facility_access", "phase5a_toledo_port", "Port access to I-80/90 is documented; no plant-specific truck route is modeled."),
    ("FDE-007", "FRT-TERM-IRONVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "industrial_materials", "external_market_dependency", "high", "high", "moderate", "high", "documented_shipment_relationship", "phase5a_toledo_port", "Ironville finished product exits by truck and rail to generalized markets; no destination facility is named."),
    ("FDE-008", "FRT-RAIL-NS", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "rail_dependency", "moderate", "moderate", "moderate", "high", "documented_corridor", "phase5a_ntad_rail", "Public corridor supports regional connectivity; facility-specific dependence is unknown."),
    ("FDE-009", "FRT-RAIL-CSXT", "FRT-MKT-MIDWEST-INDUSTRIAL", "rail", "rail_dependency", "moderate", "moderate", "moderate", "high", "documented_corridor", "phase5a_ntad_rail", "Public corridor supports regional connectivity; facility-specific dependence is unknown."),
    ("FDE-010", "FRT-RAIL-CN", "FRT-MKT-GREAT-LAKES", "rail", "rail_dependency", "moderate", "moderate", "moderate", "high", "documented_corridor", "phase5a_ntad_rail", "Public corridor supports regional connectivity; facility-specific dependence is unknown."),
    ("FDE-011", "FRT-HWY-I75", "FRT-MKT-MICHIGAN-CANADA", "highway", "external_market_dependency", "moderate", "moderate", "moderate", "high", "documented_corridor", "phase5a_fhwa_faf", "Freight-relevant corridor supports broad regional connectivity, not a specific shipper."),
    ("FDE-012", "FRT-HWY-I80-90", "FRT-MKT-MIDWEST-INDUSTRIAL", "highway", "external_market_dependency", "high", "moderate", "moderate", "high", "documented_corridor", "phase5a_fhwa_faf", "Freight-relevant corridor supports broad regional connectivity, not a specific shipper."),
    ("FDE-013", "FRT-FUEL-EXTERNAL", "ENE-EIA-59764", "energy_fuels", "fuel_logistics_dependency", "high", "low", "low", "high", "engineering_logistics_dependency", "phase5a_eia_petroleum", "Generalized fuel interface only; no pipeline or contract route is represented."),
    ("FDE-014", "CARB-EXT-AREA-WOODVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "carbonate_materials", "external_market_dependency", "moderate", "moderate", "moderate", "moderate", "generalized_supply_chain", "phase5a_area_woodville", "Aggregate product function implies logistics, but mode and customer are unknown."),
    ("FDE-015", "CARB-PROC-MM-WOODVILLE", "FRT-MKT-MIDWEST-INDUSTRIAL", "carbonate_materials", "highway_dependency", "moderate", "moderate", "moderate", "moderate", "generalized_supply_chain", "phase5a_mm_woodville", "Lime distribution is generalized; no road or rail assignment is made."),
    ("FDE-016", "CARB-PROC-GRAYMONT-GENOA", "FRT-MKT-MIDWEST-INDUSTRIAL", "carbonate_materials", "external_market_dependency", "moderate", "moderate", "unknown", "moderate", "generalized_supply_chain", "phase5a_graymont_genoa", "Genoa product role is documented; source quarry and freight mode remain unresolved."),
    ("FDE-017", "BER-PROC-ELMORE", "FRT-MKT-GREAT-LAKES", "strategic_materials", "external_market_dependency", "high", "moderate", "unknown", "high", "generalized_supply_chain", "phase5a_materion_elmore", "Nonlocal feed and broad strategic end-use context imply external orientation; route and mode absent."),
    ("FDE-018", "BER-LEG-LUCKEY", "FRT-MKT-LICENSED-DISPOSAL", "remediation", "external_market_dependency", "moderate", "high", "low", "moderate", "documented_flow", "phase5a_luckey_logistics", "Licensed off-site disposal is documented; destination and route remain generalized."),
    ("FDE-019", "FRT-AG-MIDWEST-BULK", "FRT-MKT-GREAT-LAKES", "agriculture_bulk", "external_market_dependency", "moderate", "low", "unknown", "high", "generalized_supply_chain", "phase5a_fhwa_faf", "Broad agricultural/bulk context only; Toledo-specific flow remains unresolved."),
    ("FDE-020", "FRT-PORT-TOLEDO", "FRT-MKT-MIDWEST-INDUSTRIAL", "port_marine", "interchange_dependency", "moderate", "high", "moderate", "high", "documented_facility_access", "phase5b_toledo_annual_report", "General-cargo warehouse and liquid-bulk transloading strengthen interchange context; no product route or quantity."),
]

REGISTER_ROWS = [
    ("FDR-001", "port_marine", "FRT-PORT-TOLEDO", "Port of Toledo", "marine;rail;highway", "marine_gateway_dependency;interchange_dependency;external_market_dependency", "high", "multiple named modes and 13-terminal context", "terminal-specific use and carrier substitution", "high", "high", "phase5a_toledo_port", "Gateway concentration is visible; no vulnerability claim."),
    ("FDR-002", "rail", "FRT-RAIL-NS", "Norfolk Southern Class I corridor context", "rail", "rail_dependency;interchange_dependency", "moderate", "other listed Class I interfaces", "facility-specific use and substitution", "high", "moderate", "phase5a_ntad_rail", "Corridor evidence is stronger than facility-use evidence."),
    ("FDR-003", "rail", "FRT-RAIL-CSXT", "CSX Class I corridor context", "rail", "rail_dependency;interchange_dependency", "moderate", "other listed Class I interfaces", "facility-specific use and substitution", "high", "moderate", "phase5a_ntad_rail", "Corridor evidence is stronger than facility-use evidence."),
    ("FDR-004", "rail", "FRT-RAIL-CN", "Canadian National Class I corridor context", "rail", "rail_dependency;external_market_dependency", "moderate", "other listed Class I interfaces", "facility-specific use and substitution", "high", "moderate", "phase5a_ntad_rail", "Corridor evidence is stronger than facility-use evidence."),
    ("FDR-005", "highway", "FRT-HWY-I75", "I-75 corridor", "highway", "highway_dependency;external_market_dependency", "high", "parallel regional highways", "plant-specific movement", "high", "high", "phase5a_fhwa_faf", "Regional connectivity is documented; local assignments are not."),
    ("FDR-006", "highway", "FRT-HWY-I80-90", "I-80/I-90 corridor", "highway", "highway_dependency;external_market_dependency", "high", "parallel regional highways", "plant-specific movement", "high", "high", "phase5a_fhwa_faf", "Regional connectivity is documented; local assignments are not."),
    ("FDR-007", "fuel", "FRT-FUEL-EXTERNAL", "External fuel interface", "generalized", "fuel_logistics_dependency;external_market_dependency", "high", "unknown", "pipeline and contract substitution unknown", "high", "low", "phase5a_eia_petroleum", "Generalized external interface, not a pipeline map."),
    ("FDR-008", "carbonate_materials", "CARB-EXT-AREA-WOODVILLE", "Area Aggregates Woodville", "generalized", "external_market_dependency;highway_dependency", "moderate", "unknown", "mode and customer unknown", "moderate", "moderate", "phase5a_area_woodville", "Existing facility node; freight access remains unresolved."),
    ("FDR-009", "carbonate_materials", "CARB-PROC-MM-WOODVILLE", "Martin Marietta Woodville", "generalized", "external_market_dependency;highway_dependency", "moderate", "unknown", "mode and customer unknown", "moderate", "moderate", "phase5a_mm_woodville", "Existing facility node; freight access remains unresolved."),
    ("FDR-010", "carbonate_materials", "CARB-PROC-GRAYMONT-GENOA", "Graymont Genoa", "generalized", "external_market_dependency", "moderate", "unknown", "quarry/feed and mode unknown", "moderate", "moderate", "phase5a_graymont_genoa", "Existing facility node; specific freight access remains unresolved."),
    ("FDR-011", "strategic_materials", "BER-PROC-ELMORE", "Materion Elmore", "generalized", "external_market_dependency;interchange_dependency", "high", "unknown", "nonlocal feed route and mode unknown", "high", "moderate", "phase5a_materion_elmore", "External orientation is supported; precise logistics are not."),
    ("FDR-012", "agriculture_bulk", "FRT-AG-MIDWEST-BULK", "Midwest agricultural bulk context", "multimodal", "external_market_dependency", "moderate", "unknown", "Toledo-specific route unknown", "high", "low", "phase5a_fhwa_faf", "Broad commodity context only."),
]

MATRIX_ROWS = [
    ("agriculture/bulk", "moderate", "moderate", "moderate", "high", "moderate", "unknown", "low", "Broad FAF context; Toledo-specific grain/port flow unresolved."),
    ("carbonate materials", "low", "unknown", "moderate", "moderate", "low", "moderate", "moderate", "Material roles documented; facility access and mode remain qualified."),
    ("strategic materials", "moderate", "unknown", "unknown", "high", "moderate", "low", "moderate", "Elmore external orientation documented; route/mode not documented."),
    ("general industry", "moderate", "moderate", "high", "high", "moderate", "moderate", "moderate", "Multiple broad modes and markets are visible; facility assignments remain limited."),
    ("energy/fuels", "unknown", "unknown", "unknown", "high", "low", "low", "low", "Generalized fuel interface only; no pipeline or contract evidence."),
    ("port commerce", "high", "high", "high", "high", "high", "low", "high", "Port gateway and modal access are strongest; substitutability is not operationally established."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_box(ax, x, y, width, height, label, color, fontsize=8.0):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.3))
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#29343a", wrap=True)


def render_matrix(matrix: pd.DataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    order = ["low", "moderate", "high", "unknown"]
    colors = {"low": "#c7ddd4", "moderate": "#e4c77f", "high": "#c56e55", "unknown": "#a9a4ba"}
    fig, ax = plt.subplots(figsize=(15, 8.5), facecolor="#f1eadc")
    values = matrix.iloc[:, 1:8].to_numpy()
    codes = [[order.index(value) for value in row] for row in values]
    from matplotlib.colors import ListedColormap
    ax.imshow(codes, cmap=ListedColormap([colors[key] for key in order]), vmin=-0.5, vmax=3.5, aspect="auto")
    ax.set_xticks(range(7), [c.replace("_", " ") for c in MATRIX_COLUMNS[1:8]], rotation=25, ha="right", fontsize=8.7)
    ax.set_yticks(range(len(matrix)), matrix.system_function, fontsize=9.5)
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            ax.text(j, i, value, ha="center", va="center", fontsize=8.0, color="#29343a")
    ax.set_title("FREIGHT DEPENDENCY MATRIX — WESTERN BASIN, 2026", loc="left", fontsize=16, weight="bold", color="#17384b", pad=16)
    fig.text(0.5, 0.93, "Qualitative dependency and substitutability descriptors; not probabilities, vulnerabilities, or optimization results.", ha="center", fontsize=9, color="#4d595a")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=colors[key], edgecolor="none") for key in order]
    ax.legend(handles, order, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(MATRIX_BASE.with_suffix(".png"), dpi=220, facecolor=fig.get_facecolor())
    svg_path = MATRIX_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def render_map() -> None:
    plt.rcParams["svg.hashsalt"] = "western-basin-phase5c-dependencies"
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
    rail = gpd.read_file(RAIL)
    rail = rail[rail.RROWNER1.fillna("").isin(["NS", "CSXT", "CN"])].copy()
    rail = rail[~rail.SUBDIV.fillna("").str.contains("SPUR|LEAD|TERMINAL|YARD", case=False, regex=True)]
    watersheds.plot(ax=ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.46, zorder=1)
    lake.plot(ax=ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    water_flow.plot(ax=ax, color="#6d9aab", linewidth=0.4, alpha=0.22, zorder=2)
    roads.plot(ax=ax, color="#d1a05b", linewidth=0.75, alpha=0.35, zorder=3)
    rail.plot(ax=ax, color="#4e565c", linewidth=0.5, alpha=0.28, zorder=4)
    nodes = pd.read_csv(NETWORKS / "freight_system_nodes.csv", dtype=str).fillna("")
    points = nodes[(nodes.latitude != "") & (nodes.longitude != "")]
    for node_type, frame in points.groupby("node_type"):
        marker = "*" if node_type == "port" else ("s" if node_type == "material_processor" else "o")
        color = "#1c6f83" if node_type == "port" else ("#7a4f92" if node_type == "material_processor" else "#b65d45")
        ax.scatter(frame.longitude.astype(float), frame.latitude.astype(float), marker=marker, s=190 if node_type == "port" else 72, color=color, edgecolor="#fff9ed", linewidth=1.0, zorder=7)
    labels = {"FRT-PORT-TOLEDO": ("Port of Toledo\ngateway concentration", (7, 8)), "CARB-EXT-AREA-WOODVILLE": ("Area Aggregates\naccess unknown", (6, -23)), "CARB-PROC-MM-WOODVILLE": ("Martin Marietta\nmode unknown", (6, 7)), "CARB-PROC-GRAYMONT-GENOA": ("Graymont Genoa\nfeed/mode unknown", (6, -23)), "BER-PROC-ELMORE": ("Materion Elmore\nexternal orientation", (6, 7)), "BER-LEG-LUCKEY": ("Luckey remediation\ndisposal interface", (6, -23))}
    for _, row in points.iterrows():
        if row.node_id in labels:
            label, offset = labels[row.node_id]
            ax.annotate(label, (float(row.longitude), float(row.latitude)), xytext=offset, textcoords="offset points", fontsize=7.0, color="#293238", bbox=dict(boxstyle="round,pad=.2", facecolor="#f8f2e5", edgecolor="#a28a78", alpha=0.93), zorder=8)
    ax.set_xlim(-85.25, -82.72)
    ax.set_ylim(41.08, 42.10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("MAP 19 — FREIGHT DEPENDENCIES & CRITICAL INTERFACES, 2026", loc="left", fontsize=16.0, weight="bold", color="#17384b", pad=15)
    ax.text(0.01, 0.965, "Qualitative mode/gateway dependencies over the accepted 2026 freight evidence baseline", transform=ax.transAxes, fontsize=9.2, color="#4d5b5c", va="top")
    ax.text(0.01, 0.025, "Dependency concentration is shown; no exploitable chokepoint or security target is identified.", transform=ax.transAxes, fontsize=7.5, color="#4f514b")
    ax.legend(handles=[Line2D([0], [0], marker="*", color="none", markerfacecolor="#1c6f83", markeredgecolor="white", markersize=11, label="Port/gateway"), Line2D([0], [0], marker="s", color="none", markerfacecolor="#7a4f92", markeredgecolor="white", markersize=8, label="Material processor"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#b65d45", markeredgecolor="white", markersize=8, label="Industrial/bulk site"), Line2D([0], [0], color="#4e565c", linewidth=2, label="Rail corridor context"), Line2D([0], [0], color="#d1a05b", linewidth=2, label="Highway corridor context")], loc="upper left", bbox_to_anchor=(0.01, 0.90), frameon=True, facecolor="#f8f2e5", edgecolor="#a69876", fontsize=7.2)
    flow.text(0.005, 0.82, "DEPENDENCY LENS", fontsize=9.1, weight="bold", color="#17384b")
    for x, label, color in [(0.01, "MARINE\nGATEWAY", "#1c6f83"), (0.20, "RAIL", "#4e565c"), (0.39, "HIGHWAY", "#c87938"), (0.58, "FUEL /\nEXTERNAL", "#9a6647"), (0.79, "MATERIAL /\nMARKET", "#7a4f92")]:
        draw_box(flow, x, 0.16, 0.14, 0.50, label, color, 6.7)
    for x in [0.15, 0.34, 0.53, 0.72]:
        flow.add_patch(FancyArrowPatch((x, 0.41), (x + 0.04, 0.41), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0, linestyle="--"))
    flow.text(0.01, 0.03, "Qualitative dependency only; modal alternatives and redundancy are not operationally proven.", fontsize=7.2, color="#4f514b")
    side.text(0.04, 0.975, "DEPENDENCY CONCENTRATIONS", fontsize=12.8, weight="bold", color="#17384b", va="top")
    side.text(0.04, 0.94, "Map 19 asks where broad freight functions depend on modes, gateways, interfaces, and external markets.", fontsize=8.3, color="#4d5b5c", va="top", wrap=True)
    sections = [("PORT / MARINE", "Port of Toledo has the strongest gateway and modal-interface concentration: marine, rail, highway, and external-market relationships.", "#1c6f83"), ("RAIL", "NS, CSX, and CN provide public Class I corridor context. Facility-specific rail dependence and W&LE substitution remain unknown.", "#4e565c"), ("HIGHWAY", "I-75 and I-80/90 have documented port access; I-280 and US-23 remain regional context. Plant-specific routes are absent.", "#c87938"), ("MATERIALS", "Elmore is externally oriented; Woodville/Genoa access remains generalized or unresolved; Luckey disposal is documented without route.", "#7a4f92"), ("AGRICULTURE / BULK", "Broad agricultural/bulk external orientation is supported by FAF context, but Toledo-specific grain and modal dependence remain unknown.", "#b38a3f"), ("SUBSTITUTABILITY", "General goods have more plausible broad alternatives than bulk marine or strategic-material functions, but no substitution is operationally proven.", "#527e8b")]
    y = 0.875
    for title, body, color in sections:
        side.add_patch(FancyBboxPatch((0.03, y - 0.115), 0.94, 0.105, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.15))
        side.text(0.06, y - 0.035, title, fontsize=8.1, weight="bold", color=color, va="top")
        side.text(0.06, y - 0.062, body, fontsize=6.95, color="#343b3d", va="top", wrap=True, linespacing=1.12)
        y -= 0.13
    side.text(0.04, 0.115, "BOUNDARIES", fontsize=10.0, weight="bold", color="#17384b")
    side.text(0.04, 0.09, "Dependency concentration is not vulnerability. No exploitable chokepoint, sabotage opportunity, hazardous route, security target, shipment volume, or future freight scenario is modeled.", fontsize=7.5, color="#3f4645", va="top", linespacing=1.25)
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    for directory in [NETWORKS, ANALYSIS, MAPS, FIGURES, REPORTS]:
        directory.mkdir(parents=True, exist_ok=True)
    edges = pd.DataFrame(EDGE_ROWS, columns=EDGE_COLUMNS)
    register = pd.DataFrame(REGISTER_ROWS, columns=REGISTER_COLUMNS)
    modal = pd.DataFrame(MATRIX_ROWS, columns=MODAL_COLUMNS)
    matrix = modal.copy()
    edges.to_csv(DEP_EDGES, index=False)
    register.to_csv(DEP_REGISTER, index=False)
    modal.to_csv(MODAL_MATRIX, index=False)
    matrix.to_csv(MATRIX, index=False)
    render_matrix(matrix)
    render_map()
    artifacts = [DEP_EDGES, DEP_REGISTER, MODAL_MATRIX, MATRIX, MATRIX_BASE.with_suffix(".png"), MATRIX_BASE.with_suffix(".svg"), MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    manifest = {"phase": "5C", "generated": RETRIEVED_DATE, "status": "dependency_baseline", "counts": {"dependency_edges": len(edges), "dependency_register": len(register), "modal_matrix_rows": len(modal), "modal_matrix_columns": len(modal.columns) - 1, "dependency_matrix_rows": len(matrix), "dependency_matrix_columns": len(matrix.columns) - 1}, "artifacts": {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
