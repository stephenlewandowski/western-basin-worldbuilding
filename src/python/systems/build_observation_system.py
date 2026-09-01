"""Build Phase 4A observation-to-decision baseline and Map 14.

This is a modest factual 2026 baseline. It records representative public
observation, data, forecast, decision, and response interfaces without claiming
an exhaustive sensor inventory or automated control architecture.
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
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

NODES_PATH = NETWORKS / "observation_system_nodes.csv"
EDGES_PATH = NETWORKS / "observation_system_edges.csv"
MAP_BASE = MAPS / "14_observation_decision_system_2026"
MANIFEST_PATH = REPORTS / "observation_system_manifest.json"

RETRIEVED_DATE = "2026-09-01"

NODE_COLUMNS = [
    "node_id",
    "name",
    "domain",
    "node_type",
    "status",
    "organization",
    "latitude",
    "longitude",
    "spatial_role",
    "source_id",
    "confidence",
    "notes",
]
EDGE_COLUMNS = [
    "edge_id",
    "from_id",
    "to_id",
    "relationship_type",
    "relationship_basis",
    "source_id",
    "confidence",
    "notes",
]


def node(
    node_id: str,
    name: str,
    domain: str,
    node_type: str,
    status: str,
    organization: str,
    source_id: str,
    confidence: str,
    notes: str,
    latitude: str = "",
    longitude: str = "",
    spatial_role: str = "schematic only",
) -> dict[str, str]:
    return {
        "node_id": node_id,
        "name": name,
        "domain": domain,
        "node_type": node_type,
        "status": status,
        "organization": organization,
        "latitude": latitude,
        "longitude": longitude,
        "spatial_role": spatial_role,
        "source_id": source_id,
        "confidence": confidence,
        "notes": notes,
    }


NODES = [
    node(
        "OBS-PHY-LAKE-ERIE-WESTERN",
        "Western Lake Erie / Toledo water source",
        "lake_erie_hab",
        "physical_system",
        "factual_2026",
        "Western Lake Erie system",
        "phase4a_glerl_hab",
        "high",
        "Physical context for HAB and drinking-water observation; no bloom footprint or intake geometry asserted.",
    ),
    node(
        "OBS-SNS-GLOS-TOLEDO-CRIB",
        "GLOS / IOOS City of Toledo Water Intake Crib station",
        "lake_erie_hab",
        "sensor_or_station",
        "public station; operating status not assessed",
        "Great Lakes Observing System / NOAA ERDDAP",
        "phase4a_glos_crib",
        "medium",
        "Public station coordinate only. It is not selected as the sole physical Toledo intake coordinate; the project intake-coordinate discrepancy remains unresolved.",
        "41.67496",
        "-83.3079",
        "public observation station coordinate; not canonical intake geometry",
    ),
    node(
        "OBS-NET-NOAA-GLERL-HAB",
        "NOAA GLERL Great Lakes HABs and Hypoxia observation program",
        "lake_erie_hab",
        "observation_network",
        "public research and monitoring program",
        "NOAA Great Lakes Environmental Research Laboratory",
        "phase4a_glerl_hab",
        "high",
        "Program-level observation network using satellite imagery, remote sensing, buoys, and monitoring; no exhaustive sensor inventory modeled.",
    ),
    node(
        "OBS-DAT-GLOS-ERDDAP-CRIB",
        "GLOS ERDDAP Toledo crib time-series data",
        "lake_erie_hab",
        "data_product",
        "public data product",
        "Great Lakes Observing System / NOAA ERDDAP",
        "phase4a_glos_crib",
        "high",
        "Public time-series product includes location and water-quality variables such as blue-green algae, chlorophyll, conductivity, and temperature.",
    ),
    node(
        "OBS-MOD-NOAA-HAB-FORECAST",
        "NOAA Lake Erie HAB Forecast",
        "lake_erie_hab",
        "model_or_forecast",
        "public seasonal forecast service",
        "NOAA National Centers for Coastal Ocean Science",
        "phase4a_nccos_hab_forecast",
        "high",
        "Uses satellite imagery, forecasting/mixing models, and field samples; forecast position and toxicity are not converted into a local threshold here.",
    ),
    node(
        "OBS-ORG-CITY-TOLEDO-WATER",
        "City of Toledo drinking-water decision organization",
        "lake_erie_hab",
        "decision_organization",
        "public organizational role",
        "City of Toledo Water Treatment",
        "phase4a_toledo_water_quality",
        "high",
        "City describes continuous water-quality monitoring, certified testing, and treatment protection from harmful algal blooms; direct use of one external forecast is not claimed.",
    ),
    node(
        "OBS-RSP-TOLEDO-WATER-OPERATIONS",
        "Toledo drinking-water monitoring and treatment operations",
        "lake_erie_hab",
        "operational_response",
        "documented operational role; local thresholds not modeled",
        "City of Toledo Water Treatment",
        "phase4a_toledo_water_quality",
        "high",
        "Operational endpoint for the public chain. No automatic trigger, control logic, treatment setpoint, or undisclosed facility telemetry is modeled.",
    ),
    node(
        "OBS-PHY-MAUMEE-LOWER",
        "Lower Maumee River hydrologic system",
        "maumee_hydrology",
        "physical_system",
        "factual_2026",
        "Lower Maumee watershed",
        "phase4a_usgs_nwis",
        "high",
        "Physical context for representative streamgage observation and flood information; no complete hydrometeorological network inventory modeled.",
    ),
    node(
        "OBS-SNS-USGS-04193500",
        "USGS 04193500 Maumee River at Waterville, OH",
        "maumee_hydrology",
        "sensor_or_station",
        "public streamgage; status represented from NWIS station record",
        "U.S. Geological Survey",
        "phase4a_usgs_waterville",
        "high",
        "NWIS station coordinate: 41.5000526, -83.7127145. One representative gauge only; it does not stand for every basin or flood sensor.",
        "41.5000526",
        "-83.7127145",
        "USGS station coordinate",
    ),
    node(
        "OBS-DAT-USGS-NWIS-RT",
        "USGS National Water Information System real-time data",
        "maumee_hydrology",
        "data_product",
        "public real-time data product",
        "U.S. Geological Survey",
        "phase4a_usgs_nwis",
        "high",
        "Public station observations and metadata; this baseline does not calculate flood thresholds or basin-wide derived statistics.",
    ),
    node(
        "OBS-MOD-NOAA-NWPS",
        "NOAA National Water Prediction Service",
        "maumee_hydrology",
        "model_or_forecast",
        "public forecast and warning service",
        "NOAA / National Weather Service",
        "phase4a_noaa_nwps",
        "high",
        "Public water-prediction and flood-information service; station-specific ingestion and internal model architecture are not asserted.",
    ),
    node(
        "OBS-ORG-NWS",
        "National Weather Service public warning organization",
        "maumee_hydrology",
        "decision_organization",
        "public organizational role",
        "NOAA / National Weather Service",
        "phase4a_nws_flood",
        "high",
        "Issues public flood information and warnings; county-specific emergency-management decisions are not modeled.",
    ),
    node(
        "OBS-RSP-FLOOD-WARNING-RESPONSE",
        "Flood warning and public-safety response",
        "maumee_hydrology",
        "operational_response",
        "documented public-response interface; local action not modeled",
        "Public safety partners and affected communities",
        "phase4a_nws_flood",
        "medium",
        "Public-facing response endpoint supported by NWS warning/safety information. No specific county protocol, evacuation decision, or emergency-operations telemetry is inferred.",
    ),
    node(
        "OBS-PHY-REGULATED-FACILITY",
        "Regulated wastewater / industrial facility context",
        "environmental_regulatory",
        "physical_system",
        "factual 2026 program context",
        "NPDES-regulated facilities",
        "phase4a_epa_npdes",
        "high",
        "General facility-monitoring context only; no facility-specific sampling location, discharge, permit limit, or compliance finding is added.",
    ),
    node(
        "OBS-NET-NPDES-MONITORING",
        "NPDES monitoring and discharge-reporting network",
        "environmental_regulatory",
        "observation_network",
        "public regulatory reporting framework",
        "U.S. EPA and state-authorized NPDES authorities",
        "phase4a_epa_npdes",
        "high",
        "Represents regulated-entity monitoring and reporting at program level; facility-specific measurement pathways remain outside this phase.",
    ),
    node(
        "OBS-DAT-EPA-ECHO",
        "EPA ECHO facility compliance and environmental data",
        "environmental_regulatory",
        "data_product",
        "public data product",
        "U.S. Environmental Protection Agency",
        "phase4a_epa_echo",
        "high",
        "Public search/download interface for facility, compliance, enforcement, and NPDES-related information; it is not treated as a raw sensor feed.",
    ),
    node(
        "OBS-ORG-NPDES-PROGRAM",
        "US EPA / state-authorized NPDES program authorities",
        "environmental_regulatory",
        "decision_organization",
        "public regulatory role",
        "U.S. EPA and state-authorized NPDES authorities",
        "phase4a_epa_npdes",
        "high",
        "Program-level regulatory decision interface; no local permit action or facility-specific enforcement decision is inferred.",
    ),
    node(
        "OBS-RSP-NPDES-COMPLIANCE",
        "NPDES compliance, permitting, or reporting response",
        "environmental_regulatory",
        "operational_response",
        "documented program response; case not modeled",
        "U.S. EPA and state-authorized NPDES authorities",
        "phase4a_epa_npdes",
        "medium",
        "Represents possible regulatory or operational response at program level, not a finding about a named facility.",
    ),
    node(
        "OBS-PHY-REGIONAL-GRID",
        "Western Basin regional electric system",
        "energy_information",
        "physical_system",
        "factual 2026 system context",
        "Regional grid operators and utilities",
        "phase4a_pjm_operations",
        "high",
        "Public high-level grid-information context; no SCADA, control-center detail, cyber architecture, feeder, or power-flow model.",
    ),
    node(
        "OBS-NET-EIA-ELECTRICITY",
        "EIA public electricity statistics network",
        "energy_information",
        "observation_network",
        "public statistical information network",
        "U.S. Energy Information Administration",
        "phase4a_eia_electricity",
        "high",
        "Public generation, capacity, transmission, and electricity statistics; not an operational telemetry network.",
    ),
    node(
        "OBS-DAT-EIA-ELECTRICITY",
        "EIA electricity data products",
        "energy_information",
        "data_product",
        "public data product",
        "U.S. Energy Information Administration",
        "phase4a_eia_electricity",
        "high",
        "Public statistical products provide factual context for generation and grid information; no real-time dispatch or local operating decision is inferred.",
    ),
    node(
        "OBS-NET-PJM-OPERATING-DATA",
        "PJM public operating-information network",
        "energy_information",
        "observation_network",
        "public operating-information interface",
        "PJM Interconnection",
        "phase4a_pjm_dataminer",
        "high",
        "High-level public market and operations information only; no SCADA, private telemetry, control-center detail, or cyber architecture modeled.",
    ),
    node(
        "OBS-DAT-PJM-DATAMINER",
        "PJM Data Miner 2 public data products",
        "energy_information",
        "data_product",
        "public data product",
        "PJM Interconnection",
        "phase4a_pjm_dataminer",
        "high",
        "Public operator data interface; product contents and use are represented at a high level rather than as a reconstructed control system.",
    ),
    node(
        "OBS-ORG-PJM",
        "PJM Interconnection operational organization",
        "energy_information",
        "decision_organization",
        "public organizational role",
        "PJM Interconnection",
        "phase4a_pjm_operations",
        "high",
        "Public regional transmission-organization role; exact internal decision workflow and sensitive infrastructure information are excluded.",
    ),
    node(
        "OBS-RSP-GRID-OPERATIONS",
        "High-level grid operations and planning coordination",
        "energy_information",
        "operational_response",
        "documented public interface; internal action not modeled",
        "PJM Interconnection and regional operators",
        "phase4a_pjm_operations",
        "medium",
        "Operational endpoint for public information flow. No dispatch instruction, outage response, congestion result, or automated control is claimed.",
    ),
]


def edge(
    edge_id: str,
    from_id: str,
    to_id: str,
    relationship_type: str,
    relationship_basis: str,
    source_id: str,
    confidence: str,
    notes: str,
) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "from_id": from_id,
        "to_id": to_id,
        "relationship_type": relationship_type,
        "relationship_basis": relationship_basis,
        "source_id": source_id,
        "confidence": confidence,
        "notes": notes,
    }


EDGES = [
    edge("OBS-A-001", "OBS-PHY-LAKE-ERIE-WESTERN", "OBS-SNS-GLOS-TOLEDO-CRIB", "observes", "observed", "phase4a_glos_crib", "medium", "Public observation-station coordinate; not a canonical intake coordinate."),
    edge("OBS-A-002", "OBS-PHY-LAKE-ERIE-WESTERN", "OBS-NET-NOAA-GLERL-HAB", "observes", "documented", "phase4a_glerl_hab", "high", "Program uses satellite, remote sensing, buoy, and monitoring inputs; no exhaustive station inventory modeled."),
    edge("OBS-A-003", "OBS-NET-NOAA-GLERL-HAB", "OBS-MOD-NOAA-HAB-FORECAST", "feeds", "documented", "phase4a_glerl_hab", "high", "GLERL states that collected data inform forecast models; exact internal data path is not reconstructed."),
    edge("OBS-A-004", "OBS-SNS-GLOS-TOLEDO-CRIB", "OBS-DAT-GLOS-ERDDAP-CRIB", "publishes", "documented", "phase4a_glos_crib", "high", "ERDDAP exposes the public station time series and quality-controlled variables."),
    edge("OBS-A-005", "OBS-MOD-NOAA-HAB-FORECAST", "OBS-ORG-CITY-TOLEDO-WATER", "supports_decision", "qualified_documented", "phase4a_nccos_hab_forecast", "medium", "Public sources identify drinking-water managers as forecast stakeholders; a Toledo-specific automated or direct feed is not established."),
    edge("OBS-A-006", "OBS-ORG-CITY-TOLEDO-WATER", "OBS-RSP-TOLEDO-WATER-OPERATIONS", "operates", "documented", "phase4a_toledo_water_quality", "high", "City documents continuous monitoring, certified testing, and treatment operations; thresholds and control logic are not modeled."),
    edge("OBS-B-001", "OBS-PHY-MAUMEE-LOWER", "OBS-SNS-USGS-04193500", "observes", "observed", "phase4a_usgs_waterville", "high", "Representative USGS streamgage only; not an exhaustive basin observation inventory."),
    edge("OBS-B-002", "OBS-SNS-USGS-04193500", "OBS-DAT-USGS-NWIS-RT", "publishes", "documented", "phase4a_usgs_nwis", "high", "NWIS publishes station observations and metadata."),
    edge("OBS-B-003", "OBS-DAT-USGS-NWIS-RT", "OBS-MOD-NOAA-NWPS", "feeds", "qualified_documented", "phase4a_noaa_nwps", "medium", "The public-service chain is represented at product level; station-specific ingestion into a forecast run is not asserted."),
    edge("OBS-B-004", "OBS-MOD-NOAA-NWPS", "OBS-ORG-NWS", "used_by", "documented", "phase4a_noaa_nwps", "high", "NWPS is a NOAA public water-prediction service associated with NWS forecast and warning operations."),
    edge("OBS-B-005", "OBS-ORG-NWS", "OBS-RSP-FLOOD-WARNING-RESPONSE", "supports_decision", "documented", "phase4a_nws_flood", "high", "NWS public flood information and warnings inform public-safety response; local protocols are not modeled."),
    edge("OBS-C-001", "OBS-PHY-REGULATED-FACILITY", "OBS-NET-NPDES-MONITORING", "observes", "documented", "phase4a_epa_npdes", "high", "NPDES regulates point-source discharges and requires program-level monitoring/reporting; no facility-specific observation is added."),
    edge("OBS-C-002", "OBS-NET-NPDES-MONITORING", "OBS-DAT-EPA-ECHO", "reports_to", "documented", "phase4a_epa_echo", "medium", "ECHO provides public facility and compliance data; the table does not reconstruct each reporting pathway."),
    edge("OBS-C-003", "OBS-DAT-EPA-ECHO", "OBS-ORG-NPDES-PROGRAM", "used_by", "documented", "phase4a_epa_npdes", "high", "Public regulatory data support program oversight; no named-facility decision is inferred."),
    edge("OBS-C-004", "OBS-ORG-NPDES-PROGRAM", "OBS-RSP-NPDES-COMPLIANCE", "supports_decision", "documented", "phase4a_epa_npdes", "medium", "Represents program-level compliance, permitting, or reporting response only."),
    edge("OBS-D-001", "OBS-PHY-REGIONAL-GRID", "OBS-NET-EIA-ELECTRICITY", "observes", "documented", "phase4a_eia_electricity", "high", "EIA provides public statistical information, not operational telemetry."),
    edge("OBS-D-002", "OBS-NET-EIA-ELECTRICITY", "OBS-DAT-EIA-ELECTRICITY", "publishes", "documented", "phase4a_eia_electricity", "high", "Public electricity statistics are published as data products."),
    edge("OBS-D-003", "OBS-PHY-REGIONAL-GRID", "OBS-NET-PJM-OPERATING-DATA", "observes", "documented", "phase4a_pjm_dataminer", "medium", "PJM public operating information is represented as a high-level interface, not a SCADA network."),
    edge("OBS-D-004", "OBS-NET-PJM-OPERATING-DATA", "OBS-DAT-PJM-DATAMINER", "publishes", "documented", "phase4a_pjm_dataminer", "high", "PJM Data Miner is the public data interface."),
    edge("OBS-D-005", "OBS-DAT-PJM-DATAMINER", "OBS-ORG-PJM", "used_by", "documented", "phase4a_pjm_operations", "medium", "Public operator data support a high-level operational-information interface; internal workflows are not modeled."),
    edge("OBS-D-006", "OBS-ORG-PJM", "OBS-RSP-GRID-OPERATIONS", "supports_decision", "documented", "phase4a_pjm_operations", "medium", "Operational endpoint is generalized; no dispatch, outage, congestion, or automated-control claim is made."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = pd.DataFrame(NODES, columns=NODE_COLUMNS)
    edges = pd.DataFrame(EDGES, columns=EDGE_COLUMNS)
    assert nodes.node_id.is_unique
    assert edges.edge_id.is_unique
    assert set(edges.from_id) | set(edges.to_id) <= set(nodes.node_id)
    nodes.to_csv(NODES_PATH, index=False)
    edges.to_csv(EDGES_PATH, index=False)
    return nodes, edges


def draw_box(ax, x: float, y: float, width: float, height: float, label: str, color: str, fontsize: float = 8.0) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=.012",
            facecolor="#f8f2e5",
            edgecolor=color,
            linewidth=1.4,
        )
    )
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#273238", wrap=True)


def render_map(nodes: pd.DataFrame) -> None:
    plt.rcParams["svg.hashsalt"] = "western-basin-phase4a-observation-decision"
    plt.rcParams["svg.fonttype"] = "none"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    map_ax = fig.add_axes([0.045, 0.18, 0.58, 0.75], facecolor="#e9e1ce")
    flow_ax = fig.add_axes([0.045, 0.045, 0.58, 0.095], facecolor="#eee5d3")
    side_ax = fig.add_axes([0.66, 0.045, 0.30, 0.885], facecolor="#eee5d3")
    flow_ax.axis("off")
    side_ax.axis("off")

    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    lake = lake.cx[-85.5:-82.5, 40.9:42.2]
    watersheds = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    flowlines = gpd.read_file(GPKG, layer="water_flowlines_order3")
    watersheds.plot(ax=map_ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.62, zorder=1)
    lake.plot(ax=map_ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    flowlines.plot(ax=map_ax, color="#5f91a6", linewidth=0.62, alpha=0.58, zorder=2)

    station_colors = {"lake_erie_hab": "#a8a92e", "maumee_hydrology": "#2d7fa6"}
    stations = nodes[(nodes.node_type == "sensor_or_station") & (nodes.latitude != "") & (nodes.longitude != "")]
    for _, row in stations.iterrows():
        color = station_colors[row.domain]
        map_ax.scatter(float(row.longitude), float(row.latitude), s=115, marker="o", color=color, edgecolor="#fff9ed", linewidth=1.4, zorder=6)
        label = "GLOS Toledo crib\n(public station coordinate)" if row.node_id.endswith("GLOS-TOLEDO-CRIB") else "USGS 04193500\nMaumee at Waterville"
        offset = (7, 8) if row.node_id.endswith("GLOS-TOLEDO-CRIB") else (7, -28)
        map_ax.annotate(label, (float(row.longitude), float(row.latitude)), xytext=offset, textcoords="offset points", fontsize=7.6, color="#263238", bbox=dict(boxstyle="round,pad=.22", facecolor="#f8f2e5", edgecolor=color, alpha=0.94), zorder=7)

    map_ax.set_xlim(-85.25, -82.72)
    map_ax.set_ylim(41.08, 42.10)
    map_ax.set_xticks([])
    map_ax.set_yticks([])
    map_ax.set_title("MAP 14 — WESTERN BASIN OBSERVATION & DECISION SYSTEM, 2026", loc="left", fontsize=17, weight="bold", color="#17384b", pad=15)
    map_ax.text(0.01, 0.965, "Selected public observation locations and geographic context", transform=map_ax.transAxes, fontsize=9.5, color="#4d5b5c", va="top")
    map_ax.text(0.01, 0.025, "Only two public station coordinates are plotted. Abstract networks, data products, organizations, and responses remain schematic.", transform=map_ax.transAxes, fontsize=7.7, color="#4f514b")
    map_ax.text(0.99, 0.025, "Toledo intake-coordinate discrepancy remains unresolved.", transform=map_ax.transAxes, ha="right", fontsize=7.7, color="#9a5543")
    map_ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#a8a92e", markeredgecolor="white", markersize=9, label="Lake / HAB observation"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#2d7fa6", markeredgecolor="white", markersize=9, label="Maumee hydrology observation"),
            Line2D([0], [0], color="#5f91a6", linewidth=2, label="Existing analytical water network context"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.01, 0.90),
        frameon=True,
        facecolor="#f8f2e5",
        edgecolor="#a69876",
        fontsize=7.8,
    )

    flow_ax.text(0.005, 0.82, "INFORMATION CHAIN", fontsize=9.2, weight="bold", color="#17384b")
    boxes = [
        (0.01, "ENVIRONMENT", "#527e8b"),
        (0.18, "SENSOR /\nSTATION", "#a8a92e"),
        (0.35, "DATA\nPRODUCT", "#2d7fa6"),
        (0.52, "ANALYSIS /\nFORECAST", "#8b65a5"),
        (0.69, "DECISION\nORGANIZATION", "#c37d32"),
        (0.86, "OPERATION /\nRESPONSE", "#b65c48"),
    ]
    for x, label, color in boxes:
        draw_box(flow_ax, x, 0.17, 0.12, 0.49, label, color, 7.0)
    for x in [0.135, 0.305, 0.475, 0.645, 0.815]:
        flow_ax.add_patch(FancyArrowPatch((x, 0.415), (x + 0.04, 0.415), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0))

    side_ax.text(0.04, 0.975, "REPRESENTATIVE CHAINS", fontsize=13.5, weight="bold", color="#17384b", va="top")
    side_ax.text(0.04, 0.94, "Factual 2026 public-information interfaces", fontsize=8.7, color="#4d5b5c", va="top")
    chain_text = [
        ("A  HAB / DRINKING WATER", "Western Lake Erie → GLOS / NOAA GLERL → public data and HAB forecast → City of Toledo water decision → monitoring / treatment operations", "#a8a92e"),
        ("B  HYDROLOGY / FLOOD", "Lower Maumee → USGS streamgage / NWIS → NOAA NWPS → NWS warning → public-safety response", "#2d7fa6"),
        ("C  ENVIRONMENT / REGULATION", "Regulated facility context → NPDES monitoring / reporting → EPA ECHO → NPDES authorities → compliance or permit response", "#4f8a72"),
        ("D  ENERGY INFORMATION", "Regional grid context → PJM public operating information → PJM → high-level operations / planning coordination; EIA statistics are parallel context", "#c37d32"),
    ]
    y = 0.875
    for title, body, color in chain_text:
        side_ax.add_patch(FancyBboxPatch((0.03, y - 0.15), 0.94, 0.14, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.25))
        side_ax.text(0.06, y - 0.04, title, fontsize=8.7, weight="bold", color=color, va="top")
        side_ax.text(0.06, y - 0.075, textwrap.fill(body, width=48), fontsize=7.35, color="#343b3d", va="top", linespacing=1.18)
        y -= 0.18

    side_ax.text(0.04, 0.145, "BOUNDARIES", fontsize=10.3, weight="bold", color="#17384b")
    boundary = (
        "No exhaustive sensor inventory. No invented station locations.\n"
        "No automated-control relationship is asserted.\n"
        "No SCADA, cyber architecture, sensitive telemetry, military monitoring,\n"
        "AI decision authority, privacy analysis, or future 2050/2075 layer.\n\n"
        "GLOS station coordinate ≠ resolved physical Toledo intake coordinate.\n"
        "All non-geolocated nodes are intentionally schematic."
    )
    side_ax.text(0.04, 0.12, boundary, fontsize=7.8, color="#3f4645", va="top", linespacing=1.32)

    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def write_manifest(nodes: pd.DataFrame, edges: pd.DataFrame) -> dict[str, object]:
    artifacts = [NODES_PATH, EDGES_PATH, MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    manifest = {
        "phase": "4A",
        "generated": RETRIEVED_DATE,
        "status": "baseline",
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "domains": sorted(nodes.domain.unique().tolist()),
            "chain_ids": ["A", "B", "C", "D"],
        },
        "artifacts": {
            path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    for directory in [NETWORKS, MAPS, REPORTS]:
        directory.mkdir(parents=True, exist_ok=True)
    nodes, edges = write_tables()
    render_map(nodes)
    manifest = write_manifest(nodes, edges)
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
