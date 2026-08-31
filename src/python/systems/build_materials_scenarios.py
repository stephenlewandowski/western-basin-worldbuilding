"""Build Phase 2D alternative materials futures without changing the 2026 baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SCEN = ROOT / "data" / "processed" / "scenarios"
MAPS = ROOT / "outputs" / "maps" / "systems"
FIGS = ROOT / "outputs" / "figures"
REPORTS = ROOT / "reports"
BASE_NODES = ROOT / "data" / "processed" / "networks" / "materials_system_nodes.csv"
BASE_EDGES = ROOT / "data" / "processed" / "networks" / "materials_system_edges.csv"
RETRIEVED = "2026-08-31"

SCENARIOS = {
    "A": ("continuity_resilience", "CONTINUITY / STRATEGIC RESILIENCE", "#355c7d"),
    "B": ("circular_basin", "CIRCULAR INDUSTRIAL BASIN", "#2a9d8f"),
    "C": ("high_convergence", "HIGH-CONVERGENCE GLASS BASIN", "#9c4f73"),
}

SOURCES = [
    ("PH2D-DOE-IND-2022", "Industrial Decarbonization Roadmap", "U.S. Department of Energy", "2022-09", "https://www.energy.gov/sites/default/files/2022-09/Industrial%20Decarbonization%20Roadmap.pdf", "government_roadmap", "Efficiency, electrification, low-carbon fuels, circularity, and CCUS; national trajectories, not local commitments."),
    ("PH2D-USGS-MCS-2026", "Mineral Commodity Summaries 2026", "U.S. Geological Survey", "2026-02-06", "https://pubs.usgs.gov/publication/mcs2026", "government_statistics", "Current beryllium supply, uses, and recycling; no future quantity transferred."),
    ("PH2D-DOE-FUSION-2024", "DOE Fusion Energy Strategy 2024", "U.S. Department of Energy", "2024-06-06", "https://www.energy.gov/fusion/doe-fusion-energy-strategy-2024-executive-summary", "government_strategy", "Commercialization pathway and unresolved S&T/deployment risks; no Northwest Ohio reactor assumed."),
    ("PH2D-NIST-AI-2026", "2026 Roadmap on AI and Machine Learning for Smart Manufacturing", "National Institute of Standards and Technology", "2026-07-03", "https://www.nist.gov/publications/2026-roadmap-artificial-intelligence-and-machine-learning-smart-manufacturing", "government_technical_roadmap", "AI, sensing, robotics, digital twins, and reliability barriers."),
    ("PH2D-DOE-WATER-2026", "Industrial Water Reuse Technologies", "U.S. Department of Energy / NAWI", "2026-07-27", "https://www.energy.gov/cmei/ito/articles/national-alliance-water-innovation-seeks-proposals-industrial-water-reuse", "government_rd_d", "Onsite reuse and cross-process water upgrading; no local quantity or project assumed."),
    ("PH2D-DOT-EFFICIENT-2024", "Efficient Transportation Action Plan", "U.S. Department of Transportation", "2024-12", "https://www.transportation.gov/sites/dot.gov/files/2024-12/Efficient%20Transportation.pdf", "government_strategy", "Freight efficiency, rail/maritime options, and data-driven operations; no route modeled."),
    ("PH2D-DOE-GLASS-2024", "Glass Consortium: Advanced Electric Melting", "U.S. Department of Energy", "2024-06-26", "https://www.energy.gov/nepa/articles/cx-031186-glass-consortium-advanced-electric-melting-decarbonize-commercial-glass", "government_project_record", "Toledo-based R&D context; does not establish a future production facility."),
    ("PH2D-EPA-CMORE-2024", "Construction Material Opportunities to Reduce Emissions", "U.S. Environmental Protection Agency", "2024-12-19", "https://www.epa.gov/chemicals-under-tsca/epa-welcomes-input-technical-documents-cleaner-construction-materials-and", "government_program", "Low-embodied-carbon markets and environmental product information."),
]

ASSUMPTION_THEMES = {
    "A": [
        ("efficiency", "Existing carbonate and strategic-processing roles persist with efficiency improvements", "PH2D-DOE-IND-2022", "high", "Facility continuity to the horizon is uncertain"),
        ("resilience", "Domestic strategic-material resilience strengthens without local beryllium extraction", "PH2D-USGS-MCS-2026", "moderate", "Policy and demand may change"),
        ("recycling", "Beryllium and industrial-material recycling expands incrementally", "PH2D-USGS-MCS-2026", "moderate", "Recovery economics and scrap availability"),
        ("controls", "Industrial controls, traceability, and process assurance improve", "PH2D-NIST-AI-2026", "moderate", "Adoption and interoperability"),
        ("interfaces", "Energy, water, and freight interfaces modernize without a new detailed network", "PH2D-DOT-EFFICIENT-2024", "moderate", "Infrastructure investment and governance"),
    ],
    "B": [
        ("circularity", "Secondary feedstocks and waste-to-feedstock relationships become central", "PH2D-USGS-MCS-2026", "moderate", "Sorting, contamination, and economics"),
        ("low_carbon_lime", "Lime processing adopts combinations of efficiency, electrification, capture, and lower-carbon heat", "PH2D-DOE-IND-2022", "moderate", "Technology readiness and energy cost"),
        ("water_reuse", "Industrial water is treated and reused across processes", "PH2D-DOE-WATER-2026", "moderate", "Water quality, energy, and coordination"),
        ("reverse_logistics", "Reverse logistics supports regional recovery without a mapped route", "PH2D-DOT-EFFICIENT-2024", "moderate", "Collection density and mode availability"),
        ("legacy_knowledge", "Luckey becomes a monitored remediation-knowledge and environmental-observation node", "PH2C-USACE-LUCKEY-2026", "exploratory", "Stewardship and reuse decisions"),
    ],
    "C": [
        ("fusion", "Commercial fusion progress increases demand for FLiBe-related and high-temperature materials", "PH2D-DOE-FUSION-2024", "exploratory", "Commercial fusion timing and material choices"),
        ("glass", "Existing Toledo glass expertise supports higher-value electric-melting and technical-glass capability", "PH2D-DOE-GLASS-2024", "moderate", "R&D translation and markets"),
        ("ai", "AI, robotics, sensing, and validated digital twins deepen advanced manufacturing", "PH2D-NIST-AI-2026", "moderate", "Trust, security, standards, and workforce"),
        ("strategic_processing", "Elmore expands strategic-material functions while remaining non-extractive", "SRC-MATERION-CFS-2025", "exploratory", "Customer demand and process choices"),
        ("resource_load", "Convergence raises electricity, industrial-heat, water, compute, and security dependencies", "PH2D-DOE-IND-2022", "moderate", "Grid, water, and permitting constraints"),
    ],
}

NODE_TEMPLATES = {
    "A": [
        ("WOODVILLE_LIME", "CARB-PROC-MM-WOODVILLE", "Woodville carbonate processing", "expand_role", "EXPANDS"),
        ("GENOA_LIME", "CARB-PROC-GRAYMONT-GENOA", "Genoa lime processing", "persist", "PERSISTS"),
        ("ELMORE", "BER-PROC-ELMORE", "Elmore strategic processing", "expand_role", "EXPANDS"),
        ("LUCKEY", "BER-LEG-LUCKEY", "Luckey stewardship", "legacy_transition", "LEGACY ONLY"),
        ("WATER", "CARB-END-WATER", "Water-treatment materials interface", "persist", "PERSISTS"),
        ("RECOVERY", "", "Strategic-material recovery function", "new_function", "NEW FUNCTION"),
        ("TRACE", "", "Materials traceability and process assurance", "new_function", "NEW FUNCTION"),
        ("LOGISTICS", "SYS-IF-FREIGHT", "Modernized freight interface", "expand_role", "EXPANDS"),
    ],
    "B": [
        ("WOODVILLE_LIME", "CARB-PROC-MM-WOODVILLE", "Low-carbon Woodville lime function", "expand_role", "CHANGES FUNCTION"),
        ("GENOA_LIME", "CARB-PROC-GRAYMONT-GENOA", "Low-carbon Genoa lime function", "expand_role", "CHANGES FUNCTION"),
        ("ELMORE", "BER-PROC-ELMORE", "Elmore recovery-oriented processing", "expand_role", "CHANGES FUNCTION"),
        ("LUCKEY", "BER-LEG-LUCKEY", "Luckey remediation-knowledge node", "legacy_transition", "CHANGES FUNCTION"),
        ("RECOVERY", "", "Regional materials recovery exchange", "new_node", "NEW FUNCTION"),
        ("WATER_LOOP", "", "Industrial water-reuse interface", "closed_loop", "NEW FUNCTION"),
        ("REVERSE_LOG", "SYS-IF-FREIGHT", "Reverse-logistics interface", "new_function", "CHANGES FUNCTION"),
        ("CARBON", "", "Carbon accounting / mineralization interface", "new_function", "NEW FUNCTION"),
    ],
    "C": [
        ("WOODVILLE_LIME", "CARB-PROC-MM-WOODVILLE", "High-performance carbonate inputs", "expand_role", "EXPANDS"),
        ("ELMORE", "BER-PROC-ELMORE", "Elmore high-convergence strategic processing", "expand_role", "EXPANDS"),
        ("LUCKEY", "BER-LEG-LUCKEY", "Luckey environmental observatory", "legacy_transition", "LEGACY ONLY"),
        ("GLASS", "", "Technical glass / photonics capability", "new_function", "NEW FUNCTION"),
        ("FUSION", "BER-END-CFS", "Fusion-material demand interface", "expand_role", "EXPANDS"),
        ("DIGITAL", "", "AI / robotics / digital-twin manufacturing", "new_function", "NEW FUNCTION"),
        ("ENERGY", "SYS-IF-ENERGY", "High-reliability energy and heat interface", "expand_role", "EXPANDS"),
        ("RECOVERY", "", "High-value strategic-material recovery", "new_function", "NEW FUNCTION"),
    ],
}

EDGE_TEMPLATES = {
    "A": [("WOODVILLE_LIME","WATER","lime functions"),("ELMORE","RECOVERY","strategic-material recovery"),("TRACE","ELMORE","process assurance"),("LOGISTICS","ELMORE","resilient logistics"),("LUCKEY","TRACE","stewardship knowledge"),("RECOVERY","LOGISTICS","reverse material movement")],
    "B": [("WOODVILLE_LIME","RECOVERY","carbonate byproduct recovery"),("GENOA_LIME","CARBON","low-carbon processing"),("ELMORE","RECOVERY","strategic recovery"),("RECOVERY","REVERSE_LOG","secondary feedstocks"),("WATER_LOOP","WOODVILLE_LIME","closed-loop water"),("LUCKEY","RECOVERY","remediation knowledge")],
    "C": [("WOODVILLE_LIME","GLASS","high-performance inputs"),("ELMORE","FUSION","strategic fusion materials"),("DIGITAL","ELMORE","AI-assisted manufacturing"),("ENERGY","GLASS","electric process heat"),("RECOVERY","ELMORE","strategic recovery"),("LUCKEY","DIGITAL","environmental monitoring knowledge")],
}


def build_assumptions() -> pd.DataFrame:
    rows = []
    for code, (sid, _, _) in SCENARIOS.items():
        for year in (2050, 2075):
            for i, (domain, text, source, plaus, uncertainty) in enumerate(ASSUMPTION_THEMES[code], 1):
                suffix = "By the mature horizon, " + text[0].lower() + text[1:] if year == 2075 else text
                rows.append({"assumption_id": f"MAT_{code}_{year}_{i:03d}", "scenario_id": sid, "scenario_year": year, "domain": domain, "assumption": suffix, "basis": "authoritative current trajectory plus explicit scenario extrapolation", "source_id": source, "plausibility": plaus if year == 2050 else ("exploratory" if plaus != "high" else "moderate"), "uncertainty": uncertainty, "dependency": "scenario-specific policy, investment, technology adoption, and governance", "status": "scenario_assumption", "reality_status": "fictional", "notes": "Exploratory future; not a probability, forecast, announced project, or facility commitment."})
    return pd.DataFrame(rows)


def build_nodes_edges(assumptions: pd.DataFrame):
    nodes, edges = [], []
    for code, (sid, _, _) in SCENARIOS.items():
        for year in (2050, 2075):
            aids = assumptions[(assumptions.scenario_id == sid) & (assumptions.scenario_year == year)].assumption_id.tolist()
            idmap = {}
            for i, (key, baseline, name, change, persistence) in enumerate(NODE_TEMPLATES[code], 1):
                oid = f"MAT-{code}{year}-N{i:02d}"
                idmap[key] = oid
                nodes.append({"scenario_object_id": oid, "baseline_object_id": baseline, "scenario_id": sid, "scenario_year": year, "object_name": name, "object_type": "existing_site_future_role" if baseline else "generalized_regional_function", "change_type": change, "persistence_class": persistence, "status": "scenario", "reality_status": "fictional", "relationship_basis": "scenario_assumption", "assumption_id": aids[(i-1) % len(aids)], "source_id": assumptions.loc[assumptions.assumption_id == aids[(i-1) % len(aids)], "source_id"].iloc[0], "plausibility": assumptions.loc[assumptions.assumption_id == aids[(i-1) % len(aids)], "plausibility"].iloc[0], "source_or_basis": "baseline reference plus assumption ledger", "latitude": "", "longitude": "", "notes": "No new precise facility coordinate or footprint; baseline ID anchors existing-site roles."})
            for i, (a, b, material) in enumerate(EDGE_TEMPLATES[code], 1):
                plaus = "exploratory" if code == "C" or year == 2075 else "moderate"
                edges.append({"scenario_object_id": f"MAT-{code}{year}-E{i:02d}", "baseline_object_id": "", "from_scenario_id": idmap[a], "to_scenario_id": idmap[b], "scenario_id": sid, "scenario_year": year, "material_or_dependency": material, "change_type": "new_edge" if year == 2050 else "edge_strengthened", "status": "scenario", "reality_status": "fictional", "relationship_basis": "scenario_assumption", "assumption_id": aids[(i-1) % len(aids)], "source_id": assumptions.loc[assumptions.assumption_id == aids[(i-1) % len(aids)], "source_id"].iloc[0], "plausibility": plaus, "source_or_basis": "assumption ledger; schematic system interface", "notes": "No route, quantity, capacity, customer, or precise future geometry is asserted."})
    return pd.DataFrame(nodes), pd.DataFrame(edges)


def corridor_metrics(nodes, edges):
    rows = []
    for code, (sid, _, _) in SCENARIOS.items():
        for year in (2050, 2075):
            n = nodes[(nodes.scenario_id == sid) & (nodes.scenario_year == year)]
            e = edges[(edges.scenario_id == sid) & (edges.scenario_year == year)]
            graph = nx.Graph()
            graph.add_nodes_from(n.scenario_object_id)
            graph.add_edges_from(zip(e.from_scenario_id, e.to_scenario_id))
            components = nx.number_connected_components(graph)
            geographic = n.baseline_object_id.isin(["CARB-PROC-MM-WOODVILLE","CARB-PROC-GRAYMONT-GENOA","BER-PROC-ELMORE","BER-LEG-LUCKEY"]).sum()
            rows.append({"scenario_id": sid, "scenario_year": year, "scenario_nodes": len(n), "scenario_edges": len(e), "network_components": components, "named_anchor_roles": int(geographic), "direct_interfacility_route_edges": 0, "hard_corridor_geometry": False, "corridor_finding": "B — CORRIDOR EMERGES WEAKLY" if code in {"B","C"} else "C — NETWORK EXISTS BUT CORRIDOR IS MISLEADING", "method": "Weak requires repeated multi-anchor, cross-system connectivity; no transport route or polygon is implied."})
    return pd.DataFrame(rows)


def draw_scenario_map(nodes, edges, year, path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 10), facecolor="#f7f4ec")
    fig.suptitle(f"MAP 10{'B' if year == 2075 else ''} — MATERIALS SYSTEM {year}\nTHREE EXPLORATORY FUTURES · DELTAS OVER FIXED 2026 BASELINE", fontsize=21, fontweight="bold", color="#17324d", y=.97)
    for ax, (code, (sid, title, color)) in zip(axes, SCENARIOS.items()):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.set_title(f"SCENARIO {code}\n{title}", fontsize=14, fontweight="bold", color=color, pad=14)
        n = nodes[(nodes.scenario_id == sid) & (nodes.scenario_year == year)].reset_index(drop=True)
        e = edges[(edges.scenario_id == sid) & (edges.scenario_year == year)]
        positions = {}
        for i, row in n.iterrows():
            x = .27 if i % 2 == 0 else .73; y = .86 - (i // 2) * .19
            positions[row.scenario_object_id] = (x, y)
            real_anchor = bool(row.baseline_object_id)
            fc = "#eef4f7" if real_anchor else "#fff2cc"
            patch = FancyBboxPatch((x-.205, y-.062), .41, .124, boxstyle="round,pad=0.012", fc=fc, ec=color, lw=2 if real_anchor else 1.5, linestyle="-" if real_anchor else "--")
            ax.add_patch(patch)
            ax.text(x, y+.014, textwrap.fill(row.object_name, 27), ha="center", va="center", fontsize=7.3, fontweight="bold", linespacing=1.08)
            ax.text(x, y-.043, row.persistence_class, ha="center", va="center", fontsize=6.7, color=color)
        for row in e.itertuples(index=False):
            x1,y1=positions[row.from_scenario_id]; x2,y2=positions[row.to_scenario_id]
            ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="->", lw=1.5, color=color, linestyle="--" if row.plausibility != "exploratory" else ":", alpha=.75, shrinkA=30, shrinkB=30))
        ax.text(.5,.05,"Solid boxes = existing 2026 sites/functions\nDashed boxes/edges = fictional scenario additions\nNo quantities, routes, footprints, or probabilities",ha="center",va="center",fontsize=8,color="#486581",bbox=dict(boxstyle="round",fc="white",ec="#bcccdc"))
    fig.text(.5,.012,"2026 BASELINE UNCHANGED: 30 nodes · 31 relationships | Luckey = legacy/stewardship | Elmore = processing, NOT extraction",ha="center",fontsize=10,fontweight="bold",color="#8b2635")
    fig.tight_layout(rect=(0.02,.04,.98,.91))
    fig.savefig(path.with_suffix(".png"), dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix(".svg"), facecolor=fig.get_facecolor())
    plt.close(fig)


def draw_comparison():
    labels = ["Extraction\ndependence","Circularity","Strategic\nintensity","Energy\ndemand","Recycling","Advanced\nmanufacturing","Water\nintegration","Freight\nchange"]
    levels = {"low":0,"moderate":1,"high":2}
    rows, row_labels = [], []
    values = {
        "A2050":["moderate","low","moderate","moderate","moderate","moderate","moderate","moderate"],
        "A2075":["moderate","moderate","moderate","moderate","moderate","moderate","moderate","moderate"],
        "B2050":["moderate","high","moderate","moderate","high","moderate","high","high"],
        "B2075":["low","high","moderate","high","high","moderate","high","high"],
        "C2050":["moderate","moderate","high","high","moderate","high","moderate","moderate"],
        "C2075":["moderate","high","high","high","high","high","high","high"],
    }
    for k,v in values.items(): row_labels.append(k); rows.append([levels[x] for x in v])
    fig,ax=plt.subplots(figsize=(15,7),facecolor="#f7f4ec")
    im=ax.imshow(rows,cmap=matplotlib.colors.ListedColormap(["#e8eef2","#8ec3b0","#355c7d"]),vmin=0,vmax=2,aspect="auto")
    ax.set_xticks(range(len(labels)),labels); ax.set_yticks(range(len(row_labels)),row_labels)
    for i,v in enumerate(values.values()):
        for j,x in enumerate(v): ax.text(j,i,x.upper(),ha="center",va="center",fontsize=8,color="white" if x=="high" else "#17324d",fontweight="bold")
    ax.set_title("MATERIALS FUTURES — QUALITATIVE COMPARISON\nOrdinal descriptors are scenario assumptions, not measurements or probabilities",fontsize=17,fontweight="bold",color="#17324d",pad=18)
    fig.tight_layout(); fig.savefig(FIGS/"materials_scenarios_comparison.png",dpi=180,facecolor=fig.get_facecolor()); fig.savefig(FIGS/"materials_scenarios_comparison.svg",facecolor=fig.get_facecolor()); plt.close(fig)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    SCEN.mkdir(parents=True,exist_ok=True); MAPS.mkdir(parents=True,exist_ok=True); FIGS.mkdir(parents=True,exist_ok=True)
    assumptions=build_assumptions(); nodes,edges=build_nodes_edges(assumptions); metrics=corridor_metrics(nodes,edges)
    source_df=pd.DataFrame(SOURCES,columns=["source_id","title","agency_or_publisher","publication_date","url_or_identifier","source_type","notes"])
    source_df.insert(4,"retrieval_date",RETRIEVED)
    outputs={SCEN/"materials_scenario_assumptions.csv":assumptions,SCEN/"materials_nodes_scenario.csv":nodes,SCEN/"materials_edges_scenario.csv":edges,SCEN/"materials_corridor_evaluation.csv":metrics,SCEN/"materials_scenario_sources.csv":source_df}
    for path,frame in outputs.items(): frame.to_csv(path,index=False)
    draw_scenario_map(nodes,edges,2050,MAPS/"10_materials_system_2050")
    draw_scenario_map(nodes,edges,2075,MAPS/"10b_materials_system_2075")
    draw_comparison()
    manifest={"phase":"Phase 2D — alternative materials futures","counts":{"assumptions":len(assumptions),"scenario_nodes":len(nodes),"scenario_edges":len(edges),"scenario_states":6,"sources":len(source_df)},"baseline":{"node_count":len(pd.read_csv(BASE_NODES)),"edge_count":len(pd.read_csv(BASE_EDGES)),"node_sha256":sha(BASE_NODES),"edge_sha256":sha(BASE_EDGES)},"constraints":{"factual_baseline_modified":False,"future_precise_coordinates":False,"future_quantities":False,"corridor_polygon":False,"local_beryllium_extraction":False,"new_release":False},"artifacts":{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in list(outputs)+[MAPS/"10_materials_system_2050.png",MAPS/"10_materials_system_2050.svg",MAPS/"10b_materials_system_2075.png",MAPS/"10b_materials_system_2075.svg",FIGS/"materials_scenarios_comparison.png",FIGS/"materials_scenarios_comparison.svg"]}}
    (REPORTS/"materials_scenarios_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__": main()
