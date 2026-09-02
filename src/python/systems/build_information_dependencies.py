"""Build Phase 4B information dependencies, blind spots, authority matrix, and Map 15.

This is a modest factual 2026 analytical layer over the accepted Phase 4A
observation baseline. It describes information dependencies and governance
boundaries, not cyber threats, technical control architecture, or future
scenarios.
"""
from __future__ import annotations

import hashlib
import json
import textwrap
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

PHASE4A_NODES = NETWORKS / "observation_system_nodes.csv"
DEPENDENCIES = NETWORKS / "information_dependency_edges.csv"
BLIND_SPOTS = ANALYSIS / "information_blind_spots.csv"
AUTHORITY = ANALYSIS / "decision_authority_matrix.csv"
MATRIX_CSV = FIGURES / "information_dependency_matrix_2026.csv"
MAP_BASE = MAPS / "15_information_dependencies_governance_2026"
MATRIX_BASE = FIGURES / "information_dependency_matrix_2026"
MANIFEST = REPORTS / "information_dependency_manifest.json"
RETRIEVED_DATE = "2026-09-02"

DEPENDENCY_COLUMNS = [
    "dependency_id", "source_node_id", "dependent_node_id", "domain",
    "information_type", "dependency_role", "timeliness", "availability_requirement",
    "coverage", "uncertainty", "authority_level", "access_class", "relationship_basis",
    "source_id", "confidence", "notes",
]
BLIND_COLUMNS = [
    "blindspot_id", "domain", "affected_chain", "blindspot_type", "description",
    "consequence_type", "evidence_basis", "source_id", "confidence", "additional_data_needed", "notes",
]
AUTHORITY_COLUMNS = [
    "domain", "observes", "analyzes", "advises", "decides", "operates_or_responds",
    "source_id", "confidence", "notes",
]
MATRIX_COLUMNS = [
    "domain", "observation_availability", "timeliness", "spatial_coverage",
    "model_dependence", "organizational_handoff", "public_data_availability",
    "decision_authority_clarity",
]

DEPENDENCY_ROWS = [
    ("IDE-A-001", "OBS-SNS-GLOS-TOLEDO-CRIB", "OBS-DAT-GLOS-ERDDAP-CRIB", "lake_erie_hab", "Lake-water-quality observations", "public_observation_to_data", "unknown", "high", "point", "unknown", "regional", "public", "documented", "phase4a_glos_crib", "high", "Public station observations are exposed through the public ERDDAP product; measurement cadence and current station operation are not inferred."),
    ("IDE-A-002", "OBS-NET-NOAA-GLERL-HAB", "OBS-MOD-NOAA-HAB-FORECAST", "lake_erie_hab", "Integrated HAB observations", "forecast_input", "unknown", "high", "regional", "moderate", "federal", "public", "documented", "phase4a_glerl_hab", "high", "GLERL states that collected monitoring data inform forecast models; internal ingestion and update timing are not reconstructed."),
    ("IDE-A-003", "OBS-DAT-GLOS-ERDDAP-CRIB", "OBS-ORG-CITY-TOLEDO-WATER", "lake_erie_hab", "Toledo-crib water-quality data", "decision_support", "unknown", "moderate", "point", "unknown", "municipal", "public", "qualified_documented", "phase4a_glos_crib", "medium", "Public availability makes the product an available input; a Toledo-specific operational use path is not established."),
    ("IDE-A-004", "OBS-MOD-NOAA-HAB-FORECAST", "OBS-ORG-CITY-TOLEDO-WATER", "lake_erie_hab", "Lake Erie HAB forecast", "decision_support", "unknown", "high", "regional", "moderate", "municipal", "public", "qualified_documented", "phase4a_nccos_hab_forecast", "medium", "Forecast products identify drinking-water managers as stakeholders; no local threshold or direct machine feed is asserted."),
    ("IDE-A-005", "OBS-ORG-CITY-TOLEDO-WATER", "OBS-RSP-TOLEDO-WATER-OPERATIONS", "lake_erie_hab", "Water-quality operational status", "authority_interface", "event_driven", "high", "local", "unknown", "municipal", "public", "documented", "phase4a_toledo_water_quality", "high", "The City documents continuous monitoring and treatment operations; this is not an automated trigger or setpoint."),
    ("IDE-B-001", "OBS-SNS-USGS-04193500", "OBS-DAT-USGS-NWIS-RT", "maumee_hydrology", "River stage and discharge observation", "public_observation_to_data", "real_time_or_near_real_time", "high", "point", "unknown", "federal", "public", "documented", "phase4a_usgs_waterville", "high", "Representative real-time streamgage product; one station does not cover the full Maumee basin."),
    ("IDE-B-002", "OBS-DAT-USGS-NWIS-RT", "OBS-MOD-NOAA-NWPS", "maumee_hydrology", "River observation data", "forecast_input", "real_time_or_near_real_time", "high", "point", "unknown", "federal", "public", "qualified_documented", "phase4a_noaa_nwps", "medium", "The public chain is represented at product level; station-specific forecast ingestion is not documented here."),
    ("IDE-B-003", "OBS-MOD-NOAA-NWPS", "OBS-ORG-NWS", "maumee_hydrology", "Water prediction and flood information", "warning_support", "event_driven", "high", "regional", "moderate", "federal", "public", "documented", "phase4a_noaa_nwps", "high", "NWPS is represented as a public NOAA water-prediction interface associated with NWS warning work."),
    ("IDE-B-004", "OBS-MOD-NOAA-NWPS", "OBS-RSP-FLOOD-WARNING-RESPONSE", "maumee_hydrology", "Flood forecast information", "public_response_support", "event_driven", "high", "regional", "moderate", "multi_agency", "public", "documented", "phase4a_nws_flood", "high", "Public flood information supports response awareness; local protocols and action timing are not modeled."),
    ("IDE-B-005", "OBS-ORG-NWS", "OBS-RSP-FLOOD-WARNING-RESPONSE", "maumee_hydrology", "Flood warning and safety information", "warning_support", "event_driven", "moderate", "regional", "unknown", "multi_agency", "public", "documented", "phase4a_nws_flood", "high", "NWS warnings inform public-safety response; no county-specific decision is assigned."),
    ("IDE-C-001", "OBS-NET-NPDES-MONITORING", "OBS-DAT-EPA-ECHO", "environmental_regulatory", "Regulated monitoring and discharge reports", "reporting_to_public_data", "periodic", "moderate", "local", "unknown", "multi_agency", "partially_public", "documented", "phase4a_epa_echo", "medium", "ECHO exposes public facility and compliance information; raw measurement pathways are not reconstructed."),
    ("IDE-C-002", "OBS-DAT-EPA-ECHO", "OBS-ORG-NPDES-PROGRAM", "environmental_regulatory", "Facility compliance and environmental information", "regulatory_oversight", "periodic", "moderate", "systemwide", "unknown", "federal", "public", "documented", "phase4a_epa_npdes", "high", "Public data support program oversight; no named-facility finding or enforcement outcome is inferred."),
    ("IDE-C-003", "OBS-NET-NPDES-MONITORING", "OBS-ORG-NPDES-PROGRAM", "environmental_regulatory", "NPDES monitoring/reporting record", "regulatory_oversight", "periodic", "moderate", "local", "unknown", "multi_agency", "partially_public", "documented", "phase4a_epa_npdes", "medium", "The NPDES framework is represented at program level, including state authorization boundaries."),
    ("IDE-C-004", "OBS-ORG-NPDES-PROGRAM", "OBS-RSP-NPDES-COMPLIANCE", "environmental_regulatory", "Regulatory program determination", "authority_interface", "event_driven", "moderate", "local", "unknown", "state", "partially_public", "documented", "phase4a_epa_npdes", "medium", "Represents a possible compliance, permitting, or reporting response without assigning a case."),
    ("IDE-D-001", "OBS-NET-EIA-ELECTRICITY", "OBS-DAT-EIA-ELECTRICITY", "energy_information", "Generation and electricity statistics", "public_observation_to_data", "periodic", "moderate", "systemwide", "unknown", "federal", "public", "documented", "phase4a_eia_electricity", "high", "EIA statistical products provide system context and are not operational telemetry."),
    ("IDE-D-002", "OBS-DAT-EIA-ELECTRICITY", "OBS-RSP-GRID-OPERATIONS", "energy_information", "Public generation/capacity context", "public_context", "unknown", "moderate", "regional", "unknown", "regional", "public", "documented", "phase4a_eia_electricity", "medium", "EIA data support public understanding and planning context; no direct operator use is asserted."),
    ("IDE-D-003", "OBS-NET-PJM-OPERATING-DATA", "OBS-DAT-PJM-DATAMINER", "energy_information", "PJM public operating information", "public_observation_to_data", "unknown", "high", "regional", "unknown", "regional", "public", "documented", "phase4a_pjm_dataminer", "high", "PJM Data Miner is represented as a public data interface, not a control network."),
    ("IDE-D-004", "OBS-DAT-PJM-DATAMINER", "OBS-ORG-PJM", "energy_information", "PJM operator data", "operator_information", "unknown", "high", "regional", "unknown", "operator", "public", "documented", "phase4a_pjm_operations", "medium", "Public operator data support a high-level information interface; internal workflows remain unavailable."),
    ("IDE-D-005", "OBS-DAT-PJM-DATAMINER", "OBS-RSP-GRID-OPERATIONS", "energy_information", "Public operating-information product", "decision_support", "unknown", "high", "regional", "unknown", "operator", "public", "documented", "phase4a_pjm_dataminer", "medium", "The operational endpoint is generalized and does not imply a dispatch instruction or specific response."),
    ("IDE-D-006", "OBS-ORG-PJM", "OBS-RSP-GRID-OPERATIONS", "energy_information", "Operator authority and coordination", "authority_interface", "event_driven", "high", "regional", "unknown", "operator", "partially_public", "documented", "phase4a_pjm_operations", "medium", "PJM's public operational role is represented without sensitive topology or internal decision detail."),
]

BLIND_ROWS = [
    ("IBS-A-001", "lake_erie_hab", "A", "spatial_coverage", "The single public GLOS crib coordinate is a point observation context, not coverage of all Western Lake Erie conditions or a resolved physical intake location.", "decision_context_may_not_represent_full_lake", "GLOS publishes one named station dataset; the repository retains a separate intake-coordinate discrepancy.", "phase4a_glos_crib", "high", "Independent intake-coordinate reconciliation and additional public observation coverage metadata", "Do not treat the station coordinate as the sole intake geometry."),
    ("IBS-A-002", "lake_erie_hab", "A", "status_uncertainty", "The public dataset establishes a station and time series, but this baseline does not establish current operating status or update cadence.", "currentness_of_observation_is_uncertain", "ERDDAP dataset metadata and public station record", "phase4a_glos_crib", "medium", "Current station status and documented update/cadence metadata", "No station retirement or failure is inferred."),
    ("IBS-A-003", "lake_erie_hab", "A", "model_uncertainty", "NOAA's forecast combines satellite imagery, models, and field samples; this baseline does not assign local forecast error or an action threshold.", "forecast_interpretation_remains_qualified", "NOAA NCCOS forecast description", "phase4a_nccos_hab_forecast", "high", "Documented forecast uncertainty and locally adopted decision thresholds", "This is uncertainty, not a finding that the forecast is unreliable."),
    ("IBS-A-004", "lake_erie_hab", "A", "organizational_handoff", "Public sources support general drinking-water-manager use of HAB forecasts but do not establish a direct NOAA-to-Toledo operational data handoff.", "external_forecast_use_by_toledo_is_not_established", "GLERL stakeholder statement plus City monitoring description", "phase4a_glerl_hab", "medium", "Publicly documented Toledo use pathway or local decision record", "The Phase 4A edge remains qualified rather than treated as an automated feed."),
    ("IBS-B-001", "maumee_hydrology", "B", "spatial_coverage", "USGS 04193500 is one representative Lower Maumee gauge and cannot stand for rainfall, tributary, or basin-wide conditions.", "basin_understanding_is_point_limited", "USGS station record and representative-chain scope", "phase4a_usgs_waterville", "high", "Additional gauge/rainfall coverage and documented basin aggregation methods", "No complete hydrology inventory is attempted."),
    ("IBS-B-002", "maumee_hydrology", "B", "organizational_handoff", "The public chain does not document station-specific ingestion from NWIS into a particular NWPS forecast run.", "forecast_provenance_is_product_level", "NWIS and NWPS public service descriptions", "phase4a_noaa_nwps", "medium", "Public station-to-forecast provenance or method documentation", "Do not infer a missing feed or operational failure."),
    ("IBS-B-003", "maumee_hydrology", "B", "temporal_latency", "The baseline does not assign a common observation-to-warning update interval across gauge data, forecast products, and NWS warnings.", "warning_timeliness_is_not_quantified", "NWPS and NWS public forecast/warning interfaces", "phase4a_nws_flood", "medium", "Documented update schedules and event-specific warning timelines", "No response delay or probability is calculated."),
    ("IBS-C-001", "environmental_regulatory", "C", "public_data_gap", "ECHO exposes public facility/compliance information but is not modeled as a raw continuous sensor feed.", "public_view_is_not_full_measurement_record", "EPA ECHO data-download description", "phase4a_epa_echo", "high", "Underlying monitoring records and reporting cadence for a defined facility", "Periodic or self-reported data are not treated as evidence of regulatory failure."),
    ("IBS-C-002", "environmental_regulatory", "C", "jurisdiction_boundary", "EPA and state-authorized NPDES roles are distinct; this baseline does not assign a specific local regulatory decision.", "authority_path_is_program_level", "EPA NPDES program description", "phase4a_epa_npdes", "high", "Named permit, state program, facility, and decision record", "The boundary is organizational, not a claim of conflict or failure."),
    ("IBS-D-001", "energy_information", "D", "public_data_gap", "PJM public operating information and EIA statistics do not expose the private telemetry or internal decision detail needed to reconstruct operations.", "public_information_is_high_level", "PJM Data Miner, PJM Markets and Operations, and EIA public data pages", "phase4a_pjm_dataminer", "high", "Publicly releasable operator-method documentation at the required level", "No SCADA, control architecture, or cyber detail is sought."),
]

AUTHORITY_ROWS = [
    ("lake_erie_hab", "GLOS/IOOS; NOAA GLERL; City of Toledo monitoring", "NOAA NCCOS HAB forecast; City certified water-quality staff", "NOAA HAB forecast products; City water-quality information", "City of Toledo Water Treatment", "City of Toledo drinking-water monitoring and treatment operations", "phase4a_toledo_water_quality", "medium", "Public sources support the roles and boundaries; the direct external forecast handoff remains qualified."),
    ("maumee_hydrology", "U.S. Geological Survey streamgage/NWIS", "NOAA National Water Prediction Service / National Weather Service", "National Weather Service public flood information and warnings", "Local public-safety authorities are not specified in this baseline", "Public warning and safety response by NWS and affected public-safety partners", "phase4a_nws_flood", "medium", "NWS warning authority is documented; local responder decision authority is intentionally not assigned."),
    ("environmental_regulatory", "NPDES-regulated entities and program monitoring/reporting", "EPA ECHO and EPA/state-authorized NPDES program authorities", "EPA/state-authorized NPDES program oversight", "U.S. EPA and state-authorized NPDES authorities", "Program-level compliance, permitting, or reporting response", "phase4a_epa_npdes", "medium", "No facility-specific permit, measurement, or enforcement case is modeled."),
    ("energy_information", "EIA public statistical system; PJM public operating-information interface", "PJM public markets/operations information; EIA statistical products for context", "PJM public operator information and planning/operations context", "PJM Interconnection", "High-level regional operations/planning coordination", "phase4a_pjm_operations", "medium", "Public high-level roles only; utilities, SCADA, private telemetry, and internal workflows are not reconstructed."),
]

MATRIX_ROWS = [
    ("lake_erie_hab", "high", "unknown", "moderate", "moderate", "moderate", "high", "moderate"),
    ("maumee_hydrology", "high", "high", "moderate", "moderate", "moderate", "high", "moderate"),
    ("environmental_regulatory", "moderate", "unknown", "moderate", "low", "moderate", "moderate", "moderate"),
    ("energy_information", "moderate", "unknown", "moderate", "low", "moderate", "high", "moderate"),
]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dependency_frame = pd.DataFrame(DEPENDENCY_ROWS, columns=DEPENDENCY_COLUMNS)
    blind_frame = pd.DataFrame(BLIND_ROWS, columns=BLIND_COLUMNS)
    authority_frame = pd.DataFrame(AUTHORITY_ROWS, columns=AUTHORITY_COLUMNS)
    matrix_frame = pd.DataFrame(MATRIX_ROWS, columns=MATRIX_COLUMNS)
    assert dependency_frame.dependency_id.is_unique
    assert blind_frame.blindspot_id.is_unique
    assert authority_frame.domain.is_unique
    DEPENDENCIES.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    MAPS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    dependency_frame.to_csv(DEPENDENCIES, index=False)
    blind_frame.to_csv(BLIND_SPOTS, index=False)
    authority_frame.to_csv(AUTHORITY, index=False)
    matrix_frame.to_csv(MATRIX_CSV, index=False)
    return dependency_frame, blind_frame, authority_frame, matrix_frame

def draw_box(ax, x: float, y: float, width: float, height: float, label: str, color: str, fontsize: float = 8.0) -> None:
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.3))
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#29343a", wrap=True)

def render_matrix(matrix: pd.DataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    order = ["low", "moderate", "high", "unknown"]
    colors = {"low": "#c7ddd4", "moderate": "#e4c77f", "high": "#c56e55", "unknown": "#a9a4ba"}
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="#f1eadc")
    ax.set_facecolor("#e9e1ce")
    values = matrix.iloc[:, 1:].to_numpy()
    codes = [[order.index(value) for value in row] for row in values]
    from matplotlib.colors import ListedColormap
    ax.imshow(codes, cmap=ListedColormap([colors[key] for key in order]), vmin=-0.5, vmax=len(order) - 0.5, aspect="auto")
    ax.set_xticks(range(len(MATRIX_COLUMNS) - 1), [c.replace("_", " ") for c in MATRIX_COLUMNS[1:]], rotation=25, ha="right", fontsize=9)
    ax.set_yticks(range(len(matrix)), [d.replace("_", " / ") for d in matrix.domain], fontsize=10)
    for row_index, row in enumerate(values):
        for col_index, value in enumerate(row):
            ax.text(col_index, row_index, value, ha="center", va="center", fontsize=8.3, color="#29343a")
    ax.set_title("INFORMATION DEPENDENCY MATRIX — WESTERN BASIN, 2026", loc="left", fontsize=16, weight="bold", color="#17384b", pad=16)
    fig.text(0.5, 0.93, "Ordinal descriptors of information dependence; not quantitative risk scoring or failure probability.", ha="center", fontsize=9, color="#4d595a")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=colors[key], edgecolor="none") for key in order]
    ax.legend(handles, order, ncol=len(order), loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(MATRIX_BASE.with_suffix(".png"), dpi=220, facecolor=fig.get_facecolor())
    svg_path = MATRIX_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")

def render_map(nodes: pd.DataFrame) -> None:
    plt.rcParams["svg.hashsalt"] = "western-basin-phase4b-information-dependencies"
    plt.rcParams["svg.fonttype"] = "none"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    map_ax = fig.add_axes([0.045, 0.18, 0.58, 0.75], facecolor="#e9e1ce")
    matrix_ax = fig.add_axes([0.045, 0.045, 0.58, 0.095], facecolor="#eee5d3")
    side_ax = fig.add_axes([0.66, 0.045, 0.30, 0.885], facecolor="#eee5d3")
    matrix_ax.axis("off")
    side_ax.axis("off")
    lake = gpd.read_file(GPKG, layer="water_lake_erie").cx[-85.5:-82.5, 40.9:42.2]
    watersheds = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    flowlines = gpd.read_file(GPKG, layer="water_flowlines_order3")
    watersheds.plot(ax=map_ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.62, zorder=1)
    lake.plot(ax=map_ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    flowlines.plot(ax=map_ax, color="#5f91a6", linewidth=0.62, alpha=0.58, zorder=2)
    stations = nodes[(nodes.node_type == "sensor_or_station") & (nodes.latitude != "") & (nodes.longitude != "")]
    station_colors = {"lake_erie_hab": "#a8a92e", "maumee_hydrology": "#2d7fa6"}
    for _, row in stations.iterrows():
        color = station_colors[row.domain]
        x, y = float(row.longitude), float(row.latitude)
        map_ax.scatter(x, y, s=115, marker="o", color=color, edgecolor="#fff9ed", linewidth=1.4, zorder=6)
        if row.node_id.endswith("GLOS-TOLEDO-CRIB"):
            label, offset = "GLOS Toledo crib\n(public station coordinate)", (7, 8)
        else:
            label, offset = "USGS 04193500\nMaumee at Waterville", (7, -28)
        map_ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", fontsize=7.6, color="#263238", bbox=dict(boxstyle="round,pad=.22", facecolor="#f8f2e5", edgecolor=color, alpha=0.94), zorder=7)
    map_ax.set_xlim(-85.25, -82.72)
    map_ax.set_ylim(41.08, 42.10)
    map_ax.set_xticks([])
    map_ax.set_yticks([])
    map_ax.set_title("MAP 15 — INFORMATION DEPENDENCIES & GOVERNANCE, 2026", loc="left", fontsize=17, weight="bold", color="#17384b", pad=15)
    map_ax.text(0.01, 0.965, "Selected geographic observation anchors; dependency and authority layers remain schematic", transform=map_ax.transAxes, fontsize=9.5, color="#4d5b5c", va="top")
    map_ax.text(0.01, 0.025, "Abstract information flows are not physical communication routes.", transform=map_ax.transAxes, fontsize=7.8, color="#4f514b")
    map_ax.text(0.99, 0.025, "Toledo intake-coordinate discrepancy remains unresolved.", transform=map_ax.transAxes, ha="right", fontsize=7.8, color="#9a5543")
    map_ax.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor="#a8a92e", markeredgecolor="white", markersize=9, label="Lake / HAB observation"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#2d7fa6", markeredgecolor="white", markersize=9, label="Maumee hydrology observation"), Line2D([0], [0], color="#5f91a6", linewidth=2, label="Existing analytical water context")], loc="upper left", bbox_to_anchor=(0.01, 0.90), frameon=True, facecolor="#f8f2e5", edgecolor="#a69876", fontsize=7.8)
    matrix_ax.text(0.005, 0.82, "DEPENDENCY LENS", fontsize=9.2, weight="bold", color="#17384b")
    lens_boxes = [(0.01, "OBSERVATION", "#a8a92e"), (0.18, "DATA / MODEL", "#2d7fa6"), (0.35, "AUTHORITY", "#c37d32"), (0.52, "BLIND SPOT", "#a9a4ba"), (0.69, "DECISION", "#b65c48"), (0.86, "RESPONSE", "#527e8b")]
    for x, label, color in lens_boxes:
        draw_box(matrix_ax, x, 0.17, 0.12, 0.49, label, color, 7.0)
    for x in [0.135, 0.305, 0.475, 0.645, 0.815]:
        matrix_ax.add_patch(FancyArrowPatch((x, 0.415), (x + 0.04, 0.415), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0))
    side_ax.text(0.04, 0.975, "WHERE DEPENDENCIES COLLECT", fontsize=13.2, weight="bold", color="#17384b", va="top")
    side_ax.text(0.04, 0.94, "Information can be public without being complete, timely, or authoritative.", fontsize=8.5, color="#4d5b5c", va="top", wrap=True)
    chains = [
        ("A  HAB / WATER", "GLOS and GLERL observations → public data / HAB forecast → City of Toledo water authority → monitoring and treatment", "#a8a92e"),
        ("B  HYDROLOGY / FLOOD", "USGS point observation → NWIS → NWPS / NWS forecast and warning → public-safety response", "#2d7fa6"),
        ("C  ENVIRONMENT / REGULATION", "Program monitoring/reporting → EPA ECHO → EPA/state authority → compliance or permitting response", "#4f8a72"),
        ("D  ENERGY INFORMATION", "EIA statistics and PJM public data → high-level operator information → planning/operations coordination", "#c37d32"),
    ]
    y = 0.875
    for title, body, color in chains:
        side_ax.add_patch(FancyBboxPatch((0.03, y - 0.15), 0.94, 0.14, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.25))
        side_ax.text(0.06, y - 0.04, title, fontsize=8.7, weight="bold", color=color, va="top")
        side_ax.text(0.06, y - 0.075, textwrap.fill(body, width=48), fontsize=7.35, color="#343b3d", va="top", linespacing=1.18)
        y -= 0.18
    side_ax.text(0.04, 0.145, "GOVERNANCE BOUNDARIES", fontsize=10.2, weight="bold", color="#17384b")
    boundary = ("Authority is not the same as observation ownership.\n"
                "Public data are not assumed to expose operational detail.\n"
                "Coverage, timeliness, handoffs, model uncertainty, and jurisdiction\n"
                "are recorded as blind spots only where the sources support the gap.\n\n"
                "No attack path, sensitive topology, cyber architecture, AI authority,\n"
                "privacy-impact assessment, or future scenario is modeled.")
    side_ax.text(0.04, 0.12, boundary, fontsize=7.7, color="#3f4645", va="top", linespacing=1.30)
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")

def write_manifest(dependency_frame: pd.DataFrame, blind_frame: pd.DataFrame, authority_frame: pd.DataFrame, matrix: pd.DataFrame) -> dict[str, object]:
    artifacts = [DEPENDENCIES, BLIND_SPOTS, AUTHORITY, MATRIX_CSV, MATRIX_BASE.with_suffix(".png"), MATRIX_BASE.with_suffix(".svg"), MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    manifest = {"phase": "4B", "generated": RETRIEVED_DATE, "status": "baseline", "counts": {"information_dependencies": len(dependency_frame), "blind_spots": len(blind_frame), "authority_rows": len(authority_frame), "matrix_rows": len(matrix), "matrix_columns": len(matrix.columns) - 1}, "artifacts": {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

def main() -> None:
    dependency_frame, blind_frame, authority_frame, matrix = write_tables()
    phase4a_nodes = pd.read_csv(PHASE4A_NODES, dtype=str).fillna("")
    render_matrix(matrix)
    render_map(phase4a_nodes)
    manifest = write_manifest(dependency_frame, blind_frame, authority_frame, matrix)
    print(json.dumps(manifest["counts"], indent=2))

if __name__ == "__main__":
    main()
