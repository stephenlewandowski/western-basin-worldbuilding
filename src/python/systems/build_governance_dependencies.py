"""Build Phase 10B: cross-system governance dependencies and coordination, 2026."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch
import pandas as pd

from build_governance_baseline import SOURCES, source_block_for_text, cap_citations, ensure_all_sources_cited, remap_legacy_citations, load_layers, next_map_number

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
A_MANIFEST = REPORTS / "governance_baseline_manifest.json"

DEP_COLUMNS = ["dependency_id", "system_a", "system_b", "actor_a", "actor_b", "role_a", "role_b", "dependency_type", "coordination_mechanism", "mandatory_or_voluntary", "documented_or_inferred", "jurisdictional_scale", "evidence_strength", "source_id", "notes"]
DEPS = [
    ["GDEP-001", "Biogeochemical / Nutrient Flux", "Water", "GA-012", "GA-002", "coordinate", "regulate", "split_responsibility", "planning process", "voluntary", "inferred", "state / state", "moderate", "s10_h2ohio", "Agricultural program coordination and point-source water regulation are separate institutional tracks; no individual nutrient duty is inferred."],
    ["GDEP-002", "Water", "Water", "GA-002", "GA-004", "regulate", "operate", "mandatory_coordination", "statute/regulation", "mandatory", "documented", "state / public utility", "high", "s02_ohio_pws", "Ohio EPA public-water requirements constrain the operator; no facility-specific permit is claimed by this general program source."],
    ["GDEP-003", "Water", "Water", "GA-005", "GA-002", "monitor", "regulate", "information_dependency", "scientific/data-sharing network", "unknown", "documented", "federal / state", "high", "s06_usgs_data", "USGS water observations may inform regulation, but observation does not transfer regulatory authority."],
    ["GDEP-004", "Water", "Water", "GA-004", "GA-002", "monitor", "regulate", "mandatory_coordination", "statute/regulation", "mandatory", "documented", "public utility / state", "high", "s04_toledo_quality", "Toledo water monitoring/reporting supports Ohio EPA compliance; the utility remains the operator and Ohio EPA remains the regulator."],
    ["GDEP-005", "Water", "Water", "GA-007", "GA-004", "research", "operate", "monitoring-without-control", "scientific/data-sharing network", "unknown", "inferred", "federal / public utility", "moderate", "s07_glerl", "Great Lakes research can inform management decisions without controlling the treatment plant."],
    ["GDEP-006", "Climate / Natural Hazards", "Energy / Grid / Compute", "GA-006", "GA-030", "warn", "operate", "information_dependency", "emergency protocol", "unknown", "inferred", "federal / private", "moderate", "s36_nws", "Weather warnings may inform utility operations; no formal utility protocol or outcome is asserted."],
    ["GDEP-007", "Energy / Grid / Compute", "Energy / Grid / Compute", "GA-026", "GA-030", "operate", "operate", "public_private_dependency", "market/operator rule", "mandatory", "documented", "system operator / private", "high", "s24_pjm", "PJM wholesale/high-voltage operation and utility asset operation are linked but not identical; PJM is not utility ownership."],
    ["GDEP-008", "Energy / Grid / Compute", "Energy / Grid / Compute", "GA-024", "GA-026", "regulate", "operate", "sequential_authority", "market/operator rule", "mandatory", "documented", "federal / system operator", "high", "s21_ferc", "FERC regulatory oversight and PJM operation occupy different institutional roles."],
    ["GDEP-009", "Energy / Grid / Compute", "Energy / Grid / Compute", "GA-025", "GA-030", "set_standard", "operate", "control-without-direct-observation", "market/operator rule", "mandatory", "documented", "interstate / private", "high", "s23_nerc", "Reliability standards create requirements without making NERC the owner or physical operator of utility assets."],
    ["GDEP-010", "Energy / Grid / Compute", "Energy / Grid / Compute", "GA-027", "GA-030", "regulate", "operate", "sequential_authority", "statute/regulation", "mandatory", "documented", "state / private", "high", "s25_puco", "PUCO economic/service regulation is distinct from utility operation."],
    ["GDEP-011", "Climate / Natural Hazards", "Climate / Natural Hazards", "GA-006", "GA-038", "warn", "plan", "emergency_coordination", "emergency protocol", "unknown", "inferred", "federal / county", "moderate", "s36_nws", "NWS warning provision is documented; the specific warning-to-county planning protocol is inferred and no command structure is modeled."],
    ["GDEP-012", "Climate / Natural Hazards", "Climate / Natural Hazards", "GA-010", "GA-038", "fund", "plan", "funding_dependency", "funding program", "mixed", "documented", "federal / county", "high", "s35_fema_mitigation", "FEMA assistance and planning conditions can support local mitigation without making FEMA the local planner/operator."],
    ["GDEP-013", "Climate / Natural Hazards", "Climate / Natural Hazards", "GA-010", "GA-038", "provide_data", "plan", "information_dependency", "planning process", "mixed", "documented", "federal / county", "high", "s34_fema_nfhl", "NFHL data inform local planning; mapped data are not local ownership or observed-event control."],
    ["GDEP-014", "Ecology / Biodiversity", "Ecology / Biodiversity", "GA-008", "GA-002", "permit", "permit", "overlapping_authority", "permit", "mandatory", "inferred", "federal / state", "moderate", "s05_ohio_npdes", "Ohio EPA source documents state permitting; the overlap with USACE is a qualified project inference, not a blanket legal conclusion."],
    ["GDEP-015", "Ecology / Biodiversity", "Ecology / Biodiversity", "GA-009", "GA-008", "monitor", "permit", "monitoring-without-control", "scientific/data-sharing network", "unknown", "inferred", "federal / federal", "moderate", "s08_usfws_nwi", "USFWS inventory/monitoring may inform decisions without itself being the permitter."],
    ["GDEP-016", "Water", "Water", "GA-002", "GA-015", "regulate", "regulate", "interstate_dependency", "compact", "mixed", "documented", "state / state", "moderate", "s14_gsgp", "Ohio and Michigan state programs are separate authorities connected through regional Great Lakes coordination; no shared regulator is created."],
    ["GDEP-017", "Water", "Water", "GA-020", "GA-019", "coordinate", "coordinate", "binational_dependency", "treaty/agreement", "mixed", "inferred", "binational / binational", "limited", "s15_glwqa", "GLWQA implementation and IJC reference/coordination roles are binational interfaces, not domestic permits."],
    ["GDEP-018", "Ecology / Biodiversity", "Water", "GA-021", "GA-018", "advise", "coordinate", "advisory_relationship", "consultation relationship", "voluntary", "inferred", "tribal / binational", "moderate", "s17_glifwc", "Intertribal treaty-rights/resource expertise may inform regional coordination; no Western Basin jurisdiction is inferred."],
    ["GDEP-019", "Ecology / Biodiversity", "Water", "GA-022", "GA-001", "advise", "coordinate", "advisory_relationship", "consultation relationship", "voluntary", "documented", "tribal / federal", "limited", "s18_epa_tribal", "EPA describes Tribal-government involvement; this does not establish a specific nation-specific project jurisdiction."],
    ["GDEP-020", "Biogeochemical / Nutrient Flux", "Water", "GA-011", "GA-013", "advise", "advise", "voluntary_coordination", "funding program", "voluntary", "documented", "federal / special district", "moderate", "s11_nrcs_ohio", "NRCS technical/financial assistance and local conservation support are voluntary/program-based rather than general regulation."],
    ["GDEP-021", "Freight / Industry", "Freight / Industry", "GA-032", "GA-031", "fund", "own", "funding_dependency", "funding program", "mixed", "documented", "federal / state", "high", "s29_fhwa", "Federal freight funding and state public-road ownership/operation are sequential support roles."],
    ["GDEP-022", "Freight / Industry", "Freight / Industry", "GA-033", "GA-036", "regulate", "operate", "public_private_dependency", "statute/regulation", "mandatory", "documented", "federal / private", "high", "s30_fra", "FRA safety regulation/enforcement and Norfolk Southern private operation are distinct."],
    ["GDEP-023", "Freight / Industry", "Freight / Industry", "GA-035", "GA-037", "own", "operate", "public_private_dependency", "memorandum/agreement", "mixed", "inferred", "regional authority / private", "moderate", "s32_port", "Port-authority facilities and private railroad operation can interface without public operation of the railroad."],
    ["GDEP-024", "Freight / Industry", "Freight / Industry", "GA-034", "GA-035", "plan", "own", "funding_dependency", "funding program", "mixed", "inferred", "federal / regional authority", "limited", "s31_marad", "Federal maritime assistance may interface with port-authority facilities; no project-specific award or control is asserted."],
    ["GDEP-025", "Environmental Health / Exposure", "Water", "GA-039", "GA-004", "monitor", "operate", "monitoring-without-control", "scientific/data-sharing network", "unknown", "inferred", "special district / public utility", "limited", "s40_lucas_health", "Local health information can inform utility/public-health decisions without controlling treatment operations."],
]

MECH_COLUMNS = ["mechanism_id", "mechanism_type", "mechanism_name", "actors", "systems", "mandatory_or_voluntary", "documented_or_inferred", "binding_character", "source_id", "evidence_strength", "notes"]
MECHANISMS = [
    ["GCM-001", "statute/regulation", "Ohio public-water and NPDES requirements", "GA-002;GA-004", "Water;Biogeochemical / Nutrient Flux", "mandatory", "documented", "binding where applicable", "s02_ohio_pws", "high", "Regulatory requirements and utility operation remain separate roles."],
    ["GCM-002", "permit", "Ohio EPA and USACE aquatic permitting", "GA-002;GA-008", "Water;Ecology / Biodiversity", "mandatory", "documented", "binding permit conditions", "s05_ohio_npdes", "high", "Exact jurisdiction depends on activity, resource, and applicable law."],
    ["GCM-003", "compact", "Great Lakes Basin Compact / regional water framework", "GA-017;GA-018", "Water;Ecology / Biodiversity", "mixed", "documented", "framework-specific", "s13_glc", "high", "Regional coordination is not a general state/federal permit."],
    ["GCM-004", "treaty/agreement", "Great Lakes Water Quality Agreement and binational implementation", "GA-019;GA-020", "Water;Ecology / Biodiversity", "mixed", "inferred", "agreement framework", "s15_glwqa", "limited", "The agreement is not encoded as a stand-alone domestic regulator."],
    ["GCM-005", "funding program", "NRCS EQIP and conservation assistance", "GA-011;GA-013", "Biogeochemical / Nutrient Flux;Water", "voluntary", "documented", "program/contract conditions", "s12_nrcs_eqip", "high", "Financial assistance and technical plans are not universal individual mandates."],
    ["GCM-006", "funding program", "FEMA hazard-mitigation assistance", "GA-010;GA-038", "Climate / Natural Hazards", "mixed", "documented", "conditional assistance", "s35_fema_mitigation", "high", "Funding conditions do not transfer local operational control."],
    ["GCM-007", "funding program", "Federal freight and rail investment", "GA-032;GA-033;GA-031", "Freight / Industry", "mixed", "documented", "program conditions", "s29_fhwa", "high", "Funding supports infrastructure/program objectives but does not operate private carriers."],
    ["GCM-008", "market/operator rule", "FERC/NERC/PJM reliability and market framework", "GA-024;GA-025;GA-026;GA-030", "Energy / Grid / Compute", "mandatory", "documented", "FERC-approved/market rules", "s23_nerc", "high", "Standards, market operation, regulation, and utility ownership are distinct."],
    ["GCM-009", "planning process", "H2Ohio and conservation planning", "GA-012;GA-013;GA-011", "Biogeochemical / Nutrient Flux;Water", "voluntary", "documented", "program/planning", "s10_h2ohio", "moderate", "Planning targets and incentive pathways are not assumed to be enforceable farm obligations."],
    ["GCM-010", "emergency protocol", "Weather/water warnings to local and utility decision-makers", "GA-006;GA-030;GA-038;GA-039", "Climate / Natural Hazards;Energy / Grid / Compute;Water", "unknown", "inferred", "protocol not established here", "s36_nws", "moderate", "Warning exists; a specific local command or utility protocol is not modeled."],
    ["GCM-011", "scientific/data-sharing network", "USGS, NOAA, GLERL, EPA, and public-utility data interfaces", "GA-005;GA-006;GA-007;GA-001;GA-004", "Water;Data / Sensors / Security;Climate / Natural Hazards", "mixed", "inferred", "information interface", "s06_usgs_data", "moderate", "Data dependency does not make scientific agencies the legal decision-maker."],
    ["GCM-012", "memorandum/agreement", "Port-authority / private-carrier interface", "GA-035;GA-036;GA-037", "Freight / Industry", "mixed", "inferred", "contractual/project-specific", "s32_port", "limited", "No specific contract is asserted; the mechanism is a bounded coordination category."],
    ["GCM-013", "consultation relationship", "EPA / Tribal government involvement", "GA-001;GA-022;GA-023", "Ecology / Biodiversity;Water", "voluntary", "documented", "consultation/involvement", "s18_epa_tribal", "limited", "Consultation and resource interest are not current territorial jurisdiction."],
    ["GCM-014", "planning process", "FEMA flood data and local mitigation planning", "GA-010;GA-038", "Climate / Natural Hazards;Water", "mixed", "documented", "planning/assistance", "s34_fema_nfhl", "high", "NFHL data support planning; local authority remains separate."],
]

MATRIX_COLUMNS = ["pathway", "authority_clarity", "jurisdiction_overlap", "coordination_requirement", "monitoring_alignment", "enforcement_basis", "funding_dependency", "public_private_dependency", "cross_border_dependency", "data_dependency", "decision_sequence", "uncertainty", "notes"]
MATRIX = [
    ["agricultural source → watershed transport → water-quality regulation", "moderate", "moderate", "strong", "moderate", "moderate", "strong", "not_applicable", "limited", "strong", "strong", "moderate", "Point-source permits are clearer than diffuse agricultural program obligations; no farm-level mandate inferred."],
    ["water-quality permit → municipal treatment operation", "strong", "limited", "strong", "strong", "strong", "limited", "not_applicable", "not_applicable", "strong", "strong", "limited", "Regulator and operator are distinct but linked by permit/compliance information."],
    ["scientific water observation → regulatory or operational decision", "moderate", "limited", "moderate", "moderate", "limited", "not_applicable", "not_applicable", "not_applicable", "strong", "moderate", "moderate", "Observation can inform decisions without legal or operational authority."],
    ["wetland function → federal/state permitting → restoration", "moderate", "strong", "strong", "moderate", "strong", "moderate", "not_applicable", "limited", "moderate", "strong", "moderate", "Overlapping programs are not automatically dysfunction; exact jurisdiction is activity-specific."],
    ["weather warning → utility/grid and local planning", "moderate", "limited", "moderate", "moderate", "limited", "limited", "moderate", "not_applicable", "strong", "moderate", "moderate", "Warning and response links are partly inferred; no command protocol or outage estimate."],
    ["FERC/NERC/PJM/utility electricity chain", "strong", "moderate", "strong", "moderate", "strong", "moderate", "strong", "limited", "strong", "strong", "limited", "Federal regulation, reliability standards, market operation, and private ownership are distributed."],
    ["public freight infrastructure → private rail/marine operation", "moderate", "limited", "strong", "limited", "strong", "strong", "strong", "limited", "moderate", "strong", "moderate", "Public funding/roads/port facilities interface with private carriers without public operation."],
    ["Great Lakes state programs → binational coordination", "moderate", "moderate", "strong", "moderate", "limited", "moderate", "not_applicable", "strong", "strong", "moderate", "moderate", "Compact, agreement, and treaty bodies are not collapsed into one regulator."],
    ["tribal sovereign/resource interest → consultation/coordination", "limited", "unknown", "moderate", "limited", "unknown", "limited", "not_applicable", "moderate", "moderate", "limited", "strong", "Nation-specific current Western Basin authority is unresolved; no polygon is created."],
    ["environmental-health monitoring → water-system operation", "moderate", "limited", "moderate", "moderate", "limited", "limited", "not_applicable", "not_applicable", "strong", "moderate", "moderate", "Health/environmental observation may inform operations without medical or regulatory control."],
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def render_map(map_number: int) -> Path:
    plt.rcParams["svg.fonttype"] = "none"
    huc, lake, wet, flow = load_layers()
    base = MAPS / f"{map_number}_cross_system_governance_dependencies_2026"
    fig = plt.figure(figsize=(16, 10), facecolor="#f2eadb")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wet.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.35)
    flow.plot(ax=ax, color="#4a8798", linewidth=0.28, alpha=0.45)
    pts = {"NUTRIENT": (-83.82, 41.33), "WATER": (-83.54, 41.66), "WEATHER": (-83.72, 41.86), "ENERGY": (-83.55, 41.43), "FREIGHT": (-83.52, 41.69), "WETLAND": (-83.18, 41.63), "BINATIONAL": (-83.00, 41.76)}
    colors = {"NUTRIENT": "#b58a37", "WATER": "#c8643f", "WEATHER": "#667a91", "ENERGY": "#795a9b", "FREIGHT": "#9a4f59", "WETLAND": "#4d8c67", "BINATIONAL": "#2f7890"}
    for label, (x, y) in pts.items():
        ax.scatter([x], [y], s=210, facecolors="none", edgecolors=colors[label], linewidth=1.7, zorder=5)
        ax.text(x, y, label, fontsize=6.6, color=colors[label], ha="center", va="center", weight="bold", zorder=6)
    arrows = [("NUTRIENT", "WATER"), ("WEATHER", "ENERGY"), ("WEATHER", "WATER"), ("WETLAND", "WATER"), ("FREIGHT", "ENERGY"), ("BINATIONAL", "WATER")]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(pts[start], pts[end], arrowstyle="-|>", mutation_scale=10, color="#806b64", linewidth=1.1, alpha=0.72, zorder=4))
    ax.set_xlim(-84.55, -82.55); ax.set_ylim(40.9, 42.15); ax.set_axis_off()
    side = fig.add_axes([0.67, 0.055, 0.30, 0.88]); side.axis("off")
    side.text(0.03, 0.98, f"MAP {map_number} — CROSS-SYSTEM\nGOVERNANCE DEPENDENCIES, 2026", va="top", fontsize=14.0, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.03, 0.855, "Qualitative institutional interfaces over accepted physical systems. Arrows are generalized decision/dependency chains, not routes, flowlines, jurisdiction boundaries, or risk scores.", va="top", fontsize=8.4, color="#3f4645", linespacing=1.30)
    side.text(0.03, 0.735, "CROSS-SYSTEM SEAMS", fontsize=10, weight="bold", color="#17384b")
    bullets = [
        "Agricultural programs ↔ watershed/water-quality regulation",
        "Weather and water observation ↔ utility/local decisions",
        "Wetland function ↔ federal/state permits ↔ restoration",
        "FERC/NERC/PJM ↔ private utility ownership/operation",
        "Public roads/ports ↔ private rail and marine operations",
        "Great Lakes state programs ↔ binational frameworks",
    ]
    y = 0.70
    for bullet in bullets:
        side.text(0.05, y, "• " + bullet, fontsize=7.65, color="#3f4645", va="top", linespacing=1.2); y -= 0.052
    side.text(0.03, 0.35, "MECHANISM TYPES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.32, "Statute/regulation • permit • compact • treaty/agreement • funding program • market/operator rule • planning process • emergency protocol • scientific/data-sharing network • memorandum/agreement • consultation • voluntary program", fontsize=7.6, color="#3f4645", va="top", linespacing=1.32)
    side.text(0.03, 0.19, "BOUNDARIES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.16, "UNKNOWN ≠ FAILURE. OVERLAP ≠ DYSFUNCTION. Distributed authority ≠ absence of authority. “Gap” is reserved for documented absence, not lack of project evidence or coordination burden. No composite governance score, jurisdiction polygons from vague descriptions, partisan/election analysis, or Phase 10C futures.", fontsize=7.5, color="#3f4645", va="top", linespacing=1.25)
    side.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#b58a37", markersize=7, label="system interface"),
        Line2D([0], [0], color="#806b64", lw=1.2, label="qualitative dependency"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.015), frameon=False, fontsize=7.2)
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg = base.with_suffix(".svg")
    svg_text = svg.read_text(encoding="utf-8")
    svg_text = re.sub(r'id="p[0-9a-f]+"', 'id="p0d5d59bb27"', svg_text)
    svg_text = re.sub(r'url\(#p[0-9a-f]+\)', 'url(#p0d5d59bb27)', svg_text)
    with svg.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n")
    return base


def main() -> None:
    for directory in (NETWORKS, ANALYSIS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    map_number = 33 if (MAPS / "33_cross_system_governance_dependencies_2026.png").exists() else next_map_number()
    assert map_number == 33, map_number
    dep = pd.DataFrame(DEPS, columns=DEP_COLUMNS)
    mech = pd.DataFrame(MECHANISMS, columns=MECH_COLUMNS)
    matrix = pd.DataFrame(MATRIX, columns=MATRIX_COLUMNS)
    dep_path = ANALYSIS / "governance_dependency_register.csv"
    mech_path = ANALYSIS / "governance_coordination_mechanisms.csv"
    matrix_path = ANALYSIS / "governance_dependency_matrix.csv"
    edge_path = NETWORKS / "governance_dependency_edges.csv"
    write_csv(dep, dep_path); write_csv(mech, mech_path); write_csv(matrix, matrix_path)
    edges = dep[["dependency_id", "system_a", "system_b", "actor_a", "actor_b", "role_a", "role_b", "dependency_type", "coordination_mechanism", "source_id", "evidence_strength", "notes"]].copy()
    edges.insert(0, "edge_id", edges.pop("dependency_id").str.replace("GDEP", "GEDGE", regex=False))
    write_csv(edges, edge_path)
    base = render_map(map_number)
    source_text = """# Phase 10B Cross-System Governance Dependency Sources

The Phase 10B dependency and coordination registers reuse the Phase 10A source ledger at `data/processed/analysis/governance_sources.csv` and preserve row-level `source_id` provenance.

Water-quality, municipal-operation, USGS-observation, and Great Lakes research interfaces use Ohio EPA, City of Toledo, USGS, and NOAA GLERL sources.[2][3][4][5][6][7]

The nutrient/agricultural chain distinguishes H2Ohio and NRCS assistance from regulatory permit obligations.[10][11][12]

Federal/state wetland, flood, and environmental interfaces use USACE, USFWS, FEMA, Ohio EPA, and Michigan EGLE program sources.[5][7][8][34][35][37]

The binational and tribal coordination rows use the Great Lakes Commission, Governors & Premiers, GLWQA, IJC, GLIFWC, EPA Tribal, and nation-specific sources. The registry keeps advisory, treaty/agreement, consultation, and current-jurisdiction uncertainty separate.[13][14][15][16][17][18][19][20]

Energy dependencies use FERC, NERC, PJM, PUCO, FirstEnergy, DOE, and NRC context. Freight dependencies use FHWA, FRA, MARAD, the Port Authority, Ohio port law, ODOT, and private operator context.[21][23][24][25][26][27][28][29][30][31][32][33][39][41][42]

Public-health and warning dependencies use NWS, FEMA, Ohio Department of Health, and local-health context.[35][36][38][40]

Coordination mechanisms are not presumed legally binding. `mandatory_or_voluntary`, `documented_or_inferred`, `binding_character`, and `evidence_strength` are separate fields.
"""
    assumptions = f"""# Phase 10B Cross-System Governance Dependency Assumptions

Phase 10B is a qualitative dependency layer over the Phase 10A working baseline and accepted Phase 1–9 systems. It records where a role, information stream, permit, funding pathway, public/private seam, or coordination mechanism crosses institutional boundaries. It does not rank governance quality and contains no composite score.

Dependency types distinguish overlapping authority, sequential authority, split responsibility, information dependency, funding dependency, permit dependency, public/private dependency, interstate dependency, binational dependency, monitoring-without-control, control-without-direct-observation, voluntary coordination, mandatory coordination, emergency coordination, and advisory relationship.

Coordination mechanism types distinguish statute/regulation, permit, compact, treaty/agreement, memorandum/agreement, funding program, market/operator rule, planning process, emergency protocol, scientific/data-sharing network, and consultation relationship. Binding character is recorded separately from whether a relationship is documented or inferred. An inferred physical/institutional pathway is not a legal conclusion.

The qualitative matrix uses strong, moderate, limited, unknown, and not_applicable only. UNKNOWN is not failure. OVERLAP is not dysfunction. Distributed authority is not absence of authority. The term “gap” is reserved for a documented absence of authority; lack of project evidence, unclear responsibility, coordination burden, monitoring limitation, and voluntary rather than mandatory authority remain separate categories.

Map {map_number} spatializes only generalized system interfaces over existing physical context. It does not map headquarters as jurisdiction or derive precise jurisdiction polygons from program descriptions. Great Black Swamp remains C — HOLD / noncanonical and the Toledo intake-coordinate discrepancy remains unresolved.

The package contains {len(dep)} dependency-register rows, {len(edges)} dependency edges, {len(mech)} coordination-mechanism rows, and {len(matrix)} matrix rows. Phase 10C is not implemented.
"""
    findings = """# Phase 10B Cross-System Governance Dependencies & Coordination Findings, 2026

## Authority seams

INFERENCE: The Western Basin governance structure is distributed rather than institutionally singular. Water regulation, public-utility operation, scientific observation, and public-health information meet in the same physical system but remain different roles.[2][3][4][5][6][7]

INFERENCE: Wetland and aquatic projects can encounter overlapping federal/state permitting and ecological-information roles. Overlap is recorded as a coordination requirement, not as evidence of dysfunction.[5][7][8][37]

INFERENCE: Energy authority is sequential and split: FERC regulates covered interstate/wholesale functions, NERC supplies the reliability-standard framework, PJM operates the wholesale/high-voltage system, PUCO regulates specified Ohio utility services, and private utilities own/operate assets.[21][23][24][25][28]

## Sequential authority and dependencies

FACT: Ohio public-water regulation and municipal treatment operation form a regulator/operator seam: Ohio EPA's public-water program and the City of Toledo's water-treatment division have different responsibilities.[2][3][4]

INFERENCE: Agricultural conservation programs and water-quality regulation form a sequence with a qualification: incentive/technical/planning pathways may support nutrient management, while regulatory permit obligations apply to covered point sources. H2Ohio/EQIP/NRCS program participation is not converted into a universal individual nutrient mandate.[5][10][11][12]

FACT: FRA's rail-safety regulation and investment role is distinct from private railroad operation; FHWA freight funding/planning is distinct from operation of public roads or private carriers.[29][30][41][42]

## Monitoring without control and control without direct observation

FACT: USGS, NOAA/NWS, NOAA GLERL, USFWS, FEMA flood data, and local/state monitoring rows provide observations, maps, forecasts, or scientific information without becoming the treatment-plant operator, private utility, private railroad, or local regulator.[6][7][8][34][36][40]

INFERENCE: NERC reliability standards, permits, and public funding can constrain or condition action without the standard setter/funder/permitter physically operating the asset. The register calls this control-without-direct-observation, permit dependency, or funding dependency rather than ownership.[5][12][23][30][35]

## Public/private seams

FACT: PJM's regional transmission-organization operation is not utility ownership; the Port Authority's authority-facility role is not private railroad, vessel, terminal-tenant, or industrial operation; FRA regulation is not railroad ownership.[24][28][30][32][33]

INFERENCE: Public infrastructure and funding can be prerequisites for private freight activity while leaving private operational control with the carrier. The package does not infer a specific contract, facility assignment, route, or service interruption.[29][31][32][41][42]

## Federal/state/local seams

FACT: Federal and state environmental roles are layered: EPA/USACE/FEMA/USFWS/NOAA/USGS provide federal standards, permits, data, funding, and science; Ohio EPA, Ohio DNR, Michigan EGLE, Indiana IDEM, ODH, ODOT, and local actors perform state/local or bounded program roles.[1][5][6][7][8][9][34][35][37][38][39][45][46]

INFERENCE: Local planning and operation often depend on information, permits, funding, or standards generated elsewhere, but the dependency does not transfer the underlying authority. Exact county floodplain delegation and facility-specific utility boundaries remain unresolved in this project.[28][34][35]

## Interstate and binational seams

FACT: Great Lakes regional institutions coordinate policy, water-management, agreement implementation, science, and treaty/resource contexts across states, provinces, nations, and tribal governments.[13][14][15][16][17][18][19][20]

INFERENCE: These relationships should be represented as compact, treaty/agreement, advisory, consultation, scientific, or coordination mechanisms—not collapsed into a single Great Lakes regulator.[13][14][15][16]

UNCERTAINTY: Current nation-specific Western Basin jurisdiction is not established by the available sources. Tribal sovereignty and treaty/resource interests are retained as real legal/institutional categories, but no unsupported territory, permit, or enforcement claim is created.[17][18][19][20]

## Voluntary, mandatory, and “gap” discipline

FACT: NPDES/public-water/rail-safety/reliability/permit relationships are represented as binding or mandatory where the source supports that characterization; NRCS/EQIP, H2Ohio, SWCD, consultation, and several planning/assistance relationships are voluntary, mixed, or nonbinding.[2][5][10][11][12][23][30]

The matrix does not call distributed authority a failure. It distinguishes documented absence of authority, distributed authority, unclear responsibility, coordination burden, lack of project evidence, monitoring limitation, and voluntary rather than mandatory authority. No documented absence is promoted to a generalized governance gap by this package.

## Direct dependency questions

- Where do physical/environmental dependencies cross boundaries? At nutrient-to-water-quality, warning-to-utility/local planning, wetland-to-permit/restoration, energy regulation/standards/market/utility, public-infrastructure/private-freight, and binational/tribal coordination seams.
- Which are overlapping? Federal/state aquatic permitting and Great Lakes coordination interfaces.
- Which are sequential? Permit-to-operation, regulation-to-market operation, standards-to-utility operation, funding-to-public infrastructure, and regulation-to-private rail operation.
- Where is monitoring without control? USGS, NOAA/NWS, GLERL, USFWS, FEMA data, health monitoring, and utility monitoring rows.
- Where is control without direct observation? Reliability standards, permits, funding conditions, and planning/assistance pathways where the controlling institution is not the physical operator.
- Where are public/private seams? PJM/utility, Port Authority/private rail, FHWA/ODOT/private carriers, FRA/private rail, and federal maritime/port interfaces.
- Where are federal/state/local seams? Ohio EPA/Toledo water, FEMA/Lucas County planning, USACE/Ohio EPA permits, FHWA/ODOT roads, and state/local health/water programs.
- Where are interstate/binational seams? Ohio/Michigan/Indiana environmental interfaces, GLC/GSGP/GLWQA/IJC, and tribal/resource coordination.
- Which relationships are mandatory or voluntary? The register records both explicitly; no program target or funding pathway is silently treated as a universal mandate.
- Are governance gaps demonstrated? No generalized gap is claimed. Several rows document uncertainty, coordination burden, limited monitoring alignment, or unclear responsibility; these are not equivalent to documented absence of authority.

No Phase 10C futures, partisan/election analysis, emergency-management operations model, or unsupported legal interpretation is included.
"""
    qa = f"""# Phase 10B Cross-System Governance Dependency QA

The package contains {len(dep)} dependency-register rows, {len(edges)} dependency edges, {len(mech)} coordination-mechanism rows, {len(matrix)} matrix rows, and Map {map_number} PNG/SVG. The Phase 10A working baseline is protected by `reports/governance_baseline_manifest.json` and is hash-checked before this layer is accepted as clean.

Python validation checks exact schemas, actor/role references, dependency and mechanism vocabularies, documented/inferred separation, mandatory/voluntary distinctions, matrix labels, source references, negative scope, and Map 33 integrity/readability. It checks that no relationship converts monitoring into regulation, funding into control, advisory status into binding authority, private operation into government, or a program target into an individual mandate.

The independent R validator exercises the dependency, mechanism, matrix, Phase 10A manifest, and map through a separate code path. Prior Phase 1–9 freeze manifests remain protected and are rechecked by both the 10A gate and the 10B gate.

“Gap” is not used as a synonym for distributed authority, unclear responsibility, coordination burden, lack of project evidence, monitoring limitation, or voluntary authority. UNKNOWN is preserved as unknown. OVERLAP is not labeled dysfunction.

Negative scope: no Phase 10C implementation, no future scenario rows, no composite governance score, no precise jurisdiction polygons, no partisan/election analysis, no sensitive infrastructure topology, no Phase 11, and no changes to accepted/frozen Phase 1–9 artifacts.
"""
    source_text = ensure_all_sources_cited(cap_citations(remap_legacy_citations(source_text))) + "\n" + source_block_for_text(ensure_all_sources_cited(cap_citations(remap_legacy_citations(source_text))))
    finding_text = ensure_all_sources_cited(cap_citations(remap_legacy_citations(findings))) + "\n" + source_block_for_text(ensure_all_sources_cited(cap_citations(remap_legacy_citations(findings))))
    (REPORTS / "governance_dependency_sources.md").write_text(source_text, encoding="utf-8")
    (REPORTS / "governance_dependency_assumptions.md").write_text(assumptions, encoding="utf-8")
    (REPORTS / "governance_dependency_findings.md").write_text(finding_text, encoding="utf-8")
    (REPORTS / "governance_dependency_qa.md").write_text(qa, encoding="utf-8")
    artifacts = [dep_path, mech_path, matrix_path, edge_path, ANALYSIS / "governance_sources.csv", base.with_suffix(".png"), base.with_suffix(".svg"), REPORTS / "governance_dependency_sources.md", REPORTS / "governance_dependency_assumptions.md", REPORTS / "governance_dependency_findings.md", REPORTS / "governance_dependency_qa.md"]
    manifest = {"phase": "10B", "map_number": map_number, "status": "implemented_validated_pending_sol_acceptance", "counts": {"dependency_register": len(dep), "dependency_edges": len(edges), "coordination_mechanisms": len(mech), "matrix_rows": len(matrix), "sources_reused": len(SOURCES)}, "phase10a_manifest": "reports/governance_baseline_manifest.json", "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    (REPORTS / "governance_dependency_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "10B", "map_number": map_number, **manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()
