"""Build Phase 11C: qualitative population and settlement futures, 2050/2075.

This is a separate scenario layer over the accepted Phase 11A/11B 2026
population, settlement, mobility, and dependency baselines. It models spatial
redistribution and settlement form with explicit qualitative states. It does
not write to factual baseline tables, create future population totals, or turn
commuting into migration.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
COUNTY_GEOMETRY = ROOT / "data/raw/census/tigerweb_counties_oh_in_mi.geojson"

NODES = ANALYSIS / "population_settlement_nodes.csv"
BASELINE_MANIFEST = REPORTS / "phase11a_population_settlement_freeze_manifest.json"
MOBILITY_MANIFEST = REPORTS / "phase11b_population_mobility_dependencies_freeze_manifest.json"
ASSUMPTIONS = SCENARIOS / "population_settlement_scenario_assumptions.csv"
PROJECTION_EVIDENCE = SCENARIOS / "population_settlement_projection_evidence.csv"
STATES = SCENARIOS / "population_settlement_future_states.csv"
RELATIONSHIPS = NETWORKS / "population_settlement_future_relationships.csv"
UNCERTAINTY = SCENARIOS / "population_settlement_future_uncertainty.csv"
SOURCES = ANALYSIS / "population_settlement_future_sources.csv"
COMPARISON = FIGURES / "population_settlement_future_comparison.csv"
COMPARISON_PNG = FIGURES / "population_settlement_future_comparison.png"
COMPARISON_SVG = FIGURES / "population_settlement_future_comparison.svg"
MAP2050 = MAPS / "37_population_settlement_futures_2050"
MAP2075 = MAPS / "37b_population_settlement_futures_2075"
MANIFEST = REPORTS / "population_settlement_future_manifest.json"

HORIZONS = (2050, 2075)
SCENARIO_IDS = tuple(f"{scenario}{year}" for scenario in "ABC" for year in HORIZONS)

SCENARIOS_META = {
    "A": {
        "name": "Connected Reconcentration",
        "plausibility": "moderate",
        "basis": "accepted 2026 settlement and employment anchors plus explicit connected-reconcentration scenario construction",
        "source_id": "S11C-POP-PROJ",
    },
    "B": {
        "name": "Polycentric Adaptive Basin",
        "plausibility": "moderate",
        "basis": "accepted 2026 settlement and employment network plus explicit polycentric adaptive scenario construction",
        "source_id": "S11C-NETWORK",
    },
    "C": {
        "name": "Uneven Change / Infrastructure Strain",
        "plausibility": "exploratory",
        "basis": "accepted 2026 spatial and service interfaces plus explicit uneven-change stress-test construction",
        "source_id": "S11C-CLIMATE",
    },
}

SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "evidence_role", "source_scope",
    "retrieval_date", "retrieval_status", "use_limitations",
]
SOURCE_ROWS = [
    [
        "S11C-BASELINE-11A",
        "Accepted Phase 11A population and settlement freeze manifest",
        "reports/phase11a_population_settlement_freeze_manifest.json",
        "repository_accepted_layer",
        "current factual baseline",
        "selected OH/MI/IN county and place settlement frame",
        "2026-09-08",
        "verified in repository",
        "Baseline reference only; no future values are copied into factual tables.",
    ],
    [
        "S11C-BASELINE-11B",
        "Accepted Phase 11B population mobility and dependency freeze manifest",
        "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "repository_accepted_layer",
        "current mobility and dependency context",
        "generalized residence/workplace and system interfaces",
        "2026-09-08",
        "verified in repository",
        "Commuting, workplace, residence, and dependencies remain distinct from migration and future totals.",
    ],
    [
        "S11C-POP-PROJ",
        "U.S. Census Bureau Population Projections",
        "https://www.census.gov/programs-surveys/popproj.html",
        "federal_projection_program",
        "official projection method and horizon context",
        "United States; national projection program",
        "2026-09-08",
        "retrieved",
        "Supports projection context only; it does not allocate a future total to this selected county frame.",
    ],
    [
        "S11C-POP-PROJ-TABLES",
        "2023 National Population Projections Tables: Main Series",
        "https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html",
        "federal_projection_tables",
        "official 2023–2100 national projection series and alternative-scenario boundary",
        "United States; national tables",
        "2026-09-08",
        "retrieved",
        "2050 is available at national scale, not as an adopted selected-county forecast; the package uses no numeric projection values.",
    ],
    [
        "S11C-PEP",
        "Census Bureau Population and Housing Unit Estimates",
        "https://www.census.gov/programs-surveys/popest.html",
        "federal_estimate_program",
        "distinction between current estimates and projections",
        "states, counties, metropolitan areas, cities, and towns",
        "2026-09-08",
        "retrieved",
        "PEP provides estimates, not a 2050/2075 local projection for this package.",
    ],
    [
        "S11C-NOAA",
        "NOAA Climate Change Impacts",
        "https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts",
        "federal_science_education_source",
        "climate impacts on water, energy, transportation, infrastructure, ecosystems, and human systems",
        "United States; national climate context",
        "2026-09-08",
        "retrieved",
        "Used for broad climate-system context only; climate migration remains an explicit high-uncertainty scenario mechanism with no migration count or causal local forecast.",
    ],
    [
        "S11C-OHIO",
        "Ohio Department of Development — Population Projections Overview: 2020 to 2050",
        "https://development.ohio.gov/about-us/research/population/population-projections/pop-projection-overview-2020-2050",
        "state_government_context",
        "official Ohio 2020–2050 county projection overview",
        "Ohio; statewide projection with county comparison and map",
        "2026-09-08",
        "retrieved",
        "Supports 2050 county directional reference; exact values are not copied into scenario-state rows, which remain qualitative.",
    ],
    [
        "S11C-MICHIGAN",
        "Michigan Center for Data and Analytics — County Population Projections through 2050",
        "https://www.michigan.gov/mcda/insights/2025/03/06/mich-county-popproj-2050",
        "state_government_context",
        "official Michigan 2025–2050 all-county projection overview",
        "Michigan; all 83 counties",
        "2026-09-08",
        "retrieved",
        "Supports 2050 county directional reference for Lenawee and Monroe; exact values are not copied into qualitative scenario-state rows.",
    ],
    [
        "S11C-INDIANA",
        "STATS Indiana — Population Projections Help Page",
        "https://www.stats.indiana.edu/pop_proj/default.html",
        "state_university_context",
        "official Indiana 2025–2050 substate projection tool",
        "Indiana; counties, regions, and custom county groupings",
        "2026-09-08",
        "retrieved",
        "Supports 2050 county directional reference for Allen, DeKalb, and Steuben; exact values are not copied into qualitative scenario-state rows.",
    ],
    [
        "S11C-NETWORK",
        "Phase 11B generalized mobility and system-dependency interfaces",
        "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "repository_accepted_layer",
        "spatial and functional relationship context",
        "county interfaces; generalized employment and service relationships",
        "2026-09-08",
        "verified in repository",
        "Provides relationship context, not a future commuting or migration simulator.",
    ],
    [
        "S11C-CLIMATE",
        "Accepted Phase 9 climate and natural-hazards context",
        "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
        "repository_accepted_layer",
        "inherited climate-hazard scenario context",
        "Western Basin; qualitative 2050/2075 hazard layer",
        "2026-09-08",
        "verified in repository",
        "Climate interface is not a population projection, exposure finding, or migration count.",
    ],
]

ASSUMPTION_COLUMNS = [
    "assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption",
    "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status",
    "classification", "numeric_future_value_adopted", "notes",
]
PROJECTION_COLUMNS = [
    "evidence_id", "jurisdiction", "geographic_scale", "projection_horizon", "source_id",
    "projection_status", "availability_at_scale", "adopted_use", "numeric_value_adopted",
    "uncertainty", "notes",
]
STATE_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_node_id", "baseline_name",
    "baseline_geographic_scale", "baseline_settlement_class", "current_fact",
    "population_distribution_state", "settlement_form_state", "housing_form_state",
    "employment_geography_state", "mobility_interface_state", "service_dependency_state",
    "projection_relation", "climate_migration_role", "assumption_id", "source_or_basis",
    "plausibility", "reality_status", "canon_status", "relationship_basis",
    "numeric_future_value_adopted", "notes",
]
RELATIONSHIP_COLUMNS = [
    "relationship_id", "scenario_id", "scenario", "horizon", "source_node_id", "target_node_id",
    "relationship_type", "spatial_scale", "current_fact", "scenario_assumption",
    "scenario_consequence", "commuting_migration_boundary", "source_or_basis", "assumption_id",
    "evidence_strength", "reality_status", "canon_status", "relationship_basis",
    "numeric_future_value_adopted", "notes",
]
UNCERTAINTY_COLUMNS = [
    "uncertainty_id", "scenario_id", "scenario", "horizon", "category", "subject",
    "current_fact", "scenario_assumption", "uncertainty_state", "source_or_basis",
    "assumption_id", "reality_status", "canon_status", "notes",
]
COMPARISON_COLUMNS = [
    "scenario_id", "scenario", "horizon", "population_distribution", "settlement_concentration",
    "settlement_form", "housing_form", "employment_geography", "mobility_interface",
    "climate_migration_role", "service_dependence", "projection_use", "uncertainty_profile",
    "notes",
]

DOMAINS = (
    "population_distribution", "settlement_form", "housing_form", "employment_geography",
    "mobility_and_migration_boundary", "infrastructure_service_dependence",
)
UNCERTAINTY_CATEGORIES = (
    "projection_coverage", "subcounty_distribution", "climate_migration", "household_housing_conversion",
    "employment_worker_job_relationship", "service_territory_and_capacity",
)

# Representative county links used only as qualitative scenario interfaces. They
# are not routes, flows, or predictions of residential movement.
EDGE_PAIRS = (
    ("POP-ZONE-39095", "POP-ZONE-39173"),
    ("POP-ZONE-39095", "POP-ZONE-39063"),
    ("POP-ZONE-39095", "POP-ZONE-26115"),
    ("POP-ZONE-39095", "POP-ZONE-18003"),
    ("POP-ZONE-39095", "POP-ZONE-39069"),
    ("POP-ZONE-39095", "POP-ZONE-39123"),
    ("POP-ZONE-39173", "POP-ZONE-39143"),
    ("POP-ZONE-39173", "POP-ZONE-39063"),
    ("POP-ZONE-39063", "POP-ZONE-39147"),
    ("POP-ZONE-39063", "POP-ZONE-39137"),
    ("POP-ZONE-26115", "POP-ZONE-26091"),
    ("POP-ZONE-18003", "POP-ZONE-18033"),
    ("POP-ZONE-18003", "POP-ZONE-18151"),
    ("POP-ZONE-39051", "POP-ZONE-39039"),
    ("POP-ZONE-39051", "POP-ZONE-39095"),
    ("POP-ZONE-39143", "POP-ZONE-39123"),
    ("POP-ZONE-39161", "POP-ZONE-39173"),
    ("POP-ZONE-39171", "POP-ZONE-39039"),
)


def write_rows(path: Path, columns: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def read_rows(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def state_key(scenario: str, horizon: int) -> str:
    return f"{scenario}{horizon}"


def assumption_id(scenario: str, horizon: int, domain_index: int) -> str:
    return f"S11C-{state_key(scenario, horizon)}-{domain_index:02d}"


def zone_role(node: pd.Series) -> str:
    # The employment-center IDs were created and frozen in Phase 11A. This
    # role is a qualitative cartographic grouping, not a rank.
    if node["geoid"] in {"39095", "39173", "39063", "26115", "18003"}:
        return "regional_anchor_context"
    if node["geographic_scale"] == "county":
        return "secondary_or_distributed_county_context"
    return "place_context"


def scenario_values(scenario: str, horizon: int, role: str) -> dict[str, str]:
    mature = horizon == 2075
    anchor = role == "regional_anchor_context"
    if scenario == "A":
        return {
            "population_distribution_state": "relative reconcentration toward existing anchors and connected secondary centers" if not mature else "mature connected reconcentration with selected infill and secondary-center continuity",
            "settlement_form_state": "hub-and-secondary-center pattern with stronger connected urban and town interfaces" if not mature else "connected hub network with durable infill, reuse, and linked smaller centers",
            "housing_form_state": "infill, reuse, and mixed housing forms receive stronger planning attention near anchors" if not mature else "infill and reuse are established alongside selected new housing at connected secondary centers",
            "employment_geography_state": "employment remains concentrated at existing nodes while selected secondary centers gain linked functions" if not mature else "employment anchors and linked secondary centers form a connected, nonuniform geography",
            "mobility_interface_state": "commuting interfaces become more anchor-connected; commuting is not migration and no individual path is modeled" if not mature else "commuting and service interfaces are mature across connected centers; commuting remains distinct from migration",
            "service_dependency_state": "water, wastewater, energy, transport, housing, and hazard planning follows connected service interfaces without exact territory assignment" if not mature else "selected service investments follow the connected network while operator and territory boundaries remain unknown",
        }
    if scenario == "B":
        return {
            "population_distribution_state": "relative rebalancing among several centers and adaptive town/county nodes" if not mature else "polycentric distribution persists across multiple centers rather than a single dominant concentration",
            "settlement_form_state": "polycentric centers, town networks, and adaptive corridors develop unevenly" if not mature else "durable polycentric basin with multiple center types and local adaptation",
            "housing_form_state": "mixed infill, incremental reuse, and locally varied housing forms" if not mature else "locally adapted housing forms persist with mixed infill and reuse across the network",
            "employment_geography_state": "employment functions are distributed across several anchors and specialized local nodes" if not mature else "multiple employment centers and specialized local nodes remain connected but nonuniform",
            "mobility_interface_state": "commuting interfaces remain cross-county and networked; commuting is not migration and no individual path is modeled" if not mature else "networked commuting and service interfaces persist with local variation; migration is not inferred",
            "service_dependency_state": "service adaptation is polycentric and negotiated across operators and jurisdictions without exact territory assignment" if not mature else "multiple service arrangements provide adaptive alternatives, with redundancy and coordination friction",
        }
    return {
        "population_distribution_state": "uneven change leaves some anchors stable while other counties and centers face settlement pressure" if not mature else "uneven settlement retention and contraction persist alongside durable local anchors",
        "settlement_form_state": "patchwork settlement form with selective retention, infill, and infrastructure-strained interfaces" if not mature else "diverged settlement forms persist: durable anchors, retained towns, and strained low-density interfaces",
        "housing_form_state": "housing reinvestment, reuse, and availability diverge by place; no household or unit total is forecast" if not mature else "housing form remains uneven, with durable reinvestment in some places and deferred reuse in others",
        "employment_geography_state": "employment anchors persist but access and supporting settlement functions diverge by place" if not mature else "employment remains concentrated in capable nodes while weaker links and local functions diverge",
        "mobility_interface_state": "commuting interfaces remain distinct from migration while infrastructure strain creates uneven access to centers" if not mature else "commuting and service interfaces remain uneven; no individual movement or migration count is modeled",
        "service_dependency_state": "water, wastewater, energy, transport, housing, and hazard dependencies expose maintenance seams without a vulnerability score or territory assignment" if not mature else "infrastructure-service strain is entrenched in selected interfaces while capable local systems persist",
    }


def scenario_projection_relation(horizon: int) -> str:
    if horizon == 2050:
        return "OFFICIAL PROJECTION CONTEXT AVAILABLE AT NATIONAL SCALE; no selected-county numeric projection adopted"
    return "EXPLICIT SCENARIO HORIZON; no official local 2075 projection and no mechanical extrapolation"


def climate_migration_role(horizon: int) -> str:
    if horizon == 2050:
        return "high-uncertainty scenario mechanism that may alter housing and settlement demand; not a population-growth assumption"
    return "higher-uncertainty long-horizon scenario mechanism; not a migration count, causal claim, or population-growth assumption"


def assumption_text(scenario: str, horizon: int, domain: str) -> str:
    name = SCENARIOS_META[scenario]["name"]
    horizon_text = "intermediate trajectory" if horizon == 2050 else "matured or diverged scenario state"
    domain_text = {
        "population_distribution": "relative population distribution changes among existing county and settlement anchors without a future total",
        "settlement_form": "settlement form changes through concentration, deconcentration, infill, reuse, and secondary-center relationships",
        "housing_form": "housing form and reuse diverge qualitatively without converting persons into households or housing units",
        "employment_geography": "employment geography changes as a relationship among jobs, workers, and settlement locations without forecasting job totals",
        "mobility_and_migration_boundary": "commuting and migration remain separate; no individual movement or residential-relocation path is modeled",
        "infrastructure_service_dependence": "service dependence and maintenance interfaces change without assigning residents to exact utility territories or calculating vulnerability",
    }[domain]
    return f"{name} treats {domain_text}. This is an explicit {horizon_text} scenario assumption, not an official local forecast."


def build_assumptions() -> tuple[list[list[object]], dict[str, list[str]]]:
    rows: list[list[object]] = []
    lookup: dict[str, list[str]] = {}
    for scenario in "ABC":
        for horizon in HORIZONS:
            sid = state_key(scenario, horizon)
            ids: list[str] = []
            for i, domain in enumerate(DOMAINS, 1):
                aid = assumption_id(scenario, horizon, i)
                ids.append(aid)
                uncertainty = "high" if domain in {"population_distribution", "mobility_and_migration_boundary"} and horizon == 2075 else ("moderate" if scenario != "C" else "high")
                source = SCENARIOS_META[scenario]["source_id"]
                rows.append([
                    aid, sid, SCENARIOS_META[scenario]["name"], horizon, domain,
                    assumption_text(scenario, horizon, domain),
                    SCENARIOS_META[scenario]["basis"], source, uncertainty,
                    "fictional", "scenario", "SCENARIO ASSUMPTION", "false",
                    "Qualitative future state only; no unsupported exact population, household, housing-unit, worker, job, commuter, or migration value is created.",
                ])
            lookup[sid] = ids
    return rows, lookup


def build_projection_evidence() -> list[list[object]]:
    return [
        ["PE-001", "United States", "national", "2023-2100", "S11C-POP-PROJ-TABLES", "official national projection series", "available", "method and horizon context only", "false", "moderate", "The source includes 2050 at national scale; it is not allocated to the selected county frame."],
        ["PE-002", "Ohio", "state / county", "2020-2050", "S11C-OHIO", "official county projection available", "available", "2050 directional reference; no deterministic scenario total", "false", "moderate", "Ohio's official overview reports statewide decline with county variation and a projected-2050 county comparison/map; exact values are not copied into qualitative scenario-state rows."],
        ["PE-003", "Michigan", "state / county", "2025-2050", "S11C-MICHIGAN", "official all-county projection available", "available", "2050 directional reference; no deterministic scenario total", "false", "moderate", "Michigan MCDA reports all 83 counties through 2050 and a majority-decline pattern with county variation; exact values are not copied into qualitative scenario-state rows."],
        ["PE-004", "Indiana", "state / county", "2025-2050", "S11C-INDIANA", "official county projection tool available", "available", "2050 directional reference; no deterministic scenario total", "false", "moderate", "STATS Indiana provides county projections through 2050 for the selected Indiana counties; exact values are not copied into qualitative scenario-state rows."],
        ["PE-005", "Selected Western Basin counties", "county", "2050", "S11C-BASELINE-11A", "no common numeric projection adopted", "not adopted", "current baseline anchor only", "false", "high", "PEP/ACS/Census observations are not relabeled as official 2050 projections."],
        ["PE-006", "Selected Western Basin counties", "county / place / network", "2075", "S11C-CLIMATE", "explicit scenario horizon only", "not applicable", "scenario mechanism context only", "false", "high", "2075 is not mechanically extrapolated and contains no exact future total."],
    ]


def build_states(nodes: pd.DataFrame, lookup: dict[str, list[str]]) -> list[list[object]]:
    county_nodes = nodes[nodes.node_type == "population_zone"].copy()
    rows: list[list[object]] = []
    for scenario in "ABC":
        for horizon in HORIZONS:
            sid = state_key(scenario, horizon)
            values_for_domain = lookup[sid]
            for _, node in county_nodes.iterrows():
                role = zone_role(node)
                vals = scenario_values(scenario, horizon, role)
                current = f"CURRENT FACT (2026 baseline): {node['name']} is represented as a Census county-scale population-zone node with a generalized settlement context; no future value is implied."
                notes = (
                    "County geography is a statistical/cartographic frame, not a jurisdiction or utility service territory. "
                    "Population ≠ household ≠ housing unit ≠ worker ≠ job ≠ commuter; this row carries no numeric future value. "
                    "No vulnerability/EJ score or protected-class ranking is represented."
                )
                rows.append([
                    f"PFS-{sid}-{node['geoid']}", sid, SCENARIOS_META[scenario]["name"], horizon,
                    node["node_id"], node["name"], node["geographic_scale"], node["settlement_class"], current,
                    vals["population_distribution_state"], vals["settlement_form_state"], vals["housing_form_state"],
                    vals["employment_geography_state"], vals["mobility_interface_state"], vals["service_dependency_state"],
                    scenario_projection_relation(horizon), climate_migration_role(horizon), values_for_domain[0],
                    "S11C-BASELINE-11A;S11C-POP-PROJ-TABLES;S11C-CLIMATE", SCENARIOS_META[scenario]["plausibility"],
                    "fictional", "scenario", "qualitative scenario delta over accepted 2026 baseline", "false", notes,
                ])
    return rows


def build_relationships(lookup: dict[str, list[str]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for scenario in "ABC":
        for horizon in HORIZONS:
            sid = state_key(scenario, horizon)
            for index, (source, target) in enumerate(EDGE_PAIRS, 1):
                if scenario == "A":
                    rel_type = "connected_reconcentration_interface"
                    consequence = "SCENARIO CONSEQUENCE: selected anchor and secondary-center interfaces become more connected without a predicted route, volume, or residential relocation flow."
                elif scenario == "B":
                    rel_type = "polycentric_adaptive_interface"
                    consequence = "SCENARIO CONSEQUENCE: multiple centers exchange functions through adaptive, nonuniform interfaces; redundancy and local variation remain."
                else:
                    rel_type = "uneven_change_infrastructure_strain_interface"
                    consequence = "SCENARIO CONSEQUENCE: selected interfaces experience uneven settlement and service continuity while capable local nodes can persist."
                transition = "2050 intermediate trajectory" if horizon == 2050 else "2075 matured or diverged state"
                rows.append([
                    f"PFR-{sid}-{index:02d}", sid, SCENARIOS_META[scenario]["name"], horizon, source, target,
                    rel_type, "county_pair", "CURRENT FACT (2026 baseline): Phase 11B provides generalized county-scale residence/workplace and dependency context; it does not establish a future flow.",
                    f"SCENARIO ASSUMPTION: {transition} relationship among existing settlement and employment interfaces; no exact movement or service-territory assignment.",
                    consequence,
                    "Commuting is not migration; this relationship is not an individual movement path, migration count, or freight route.",
                    "S11C-BASELINE-11B;S11C-NETWORK", lookup[sid][0], "limited", "fictional", "scenario",
                    "explicit qualitative scenario interface; not a documented future route or flow", "false",
                    "Spatial scale is a generalized county pair. No population total, household total, housing-unit total, worker count, job count, commuter count, probability, or vulnerability score is assigned.",
                ])
    return rows


def build_uncertainty(lookup: dict[str, list[str]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for scenario in "ABC":
        for horizon in HORIZONS:
            sid = state_key(scenario, horizon)
            for index, category in enumerate(UNCERTAINTY_CATEGORIES, 1):
                if category == "projection_coverage":
                    state = "official projection context exists at national scale; comparable selected-county 2050 adoption remains unresolved"
                elif category == "subcounty_distribution":
                    state = "future block, tract, neighborhood, and parcel redistribution is unknown"
                elif category == "climate_migration":
                    state = "high-uncertainty scenario mechanism; not a population-growth assumption, count, or causal claim"
                elif category == "household_housing_conversion":
                    state = "future household size, vacancy, tenure, and housing-unit conversion are unknown"
                elif category == "employment_worker_job_relationship":
                    state = "future jobs, workers, workplaces, and commuter interfaces are not forecast or converted into population"
                else:
                    state = "exact utility service territories, capacity, and population served are unknown"
                rows.append([
                    f"PFU-{sid}-{index:02d}", sid, SCENARIOS_META[scenario]["name"], horizon, category,
                    "selected Western Basin county/place settlement frame",
                    "CURRENT FACT (2026 baseline): accepted Phase 11A/11B records preserve their native scales and vintages.",
                    f"SCENARIO ASSUMPTION: {SCENARIOS_META[scenario]['name']} explores this uncertainty at the {horizon} horizon without promoting it to fact.",
                    state, "S11C-BASELINE-11A;S11C-BASELINE-11B;S11C-POP-PROJ", lookup[sid][min(index - 1, 5)],
                    "fictional", "scenario", "Unknown is retained as unknown; it is not treated as low, absent, or a vulnerability score.",
                ])
    return rows


def build_comparison() -> list[list[object]]:
    values = {
        "A": ("relative_reconcentration", "connected_anchor_network", "infill_and_reuse", "anchored_but_connected", "anchor_to_secondary_center", "high_uncertainty_mechanism_only", "connected_service_interfaces", "national_context_only", "moderate; local distribution unknown"),
        "B": ("polycentric_rebalancing", "multiple_adaptive_centers", "locally_varied_mixed_form", "distributed_nonuniform_nodes", "networked_cross_county_interfaces", "high_uncertainty_mechanism_only", "polycentric_and_negotiated", "national_context_only", "moderate; local distribution unknown"),
        "C": ("uneven_change", "patchwork_retention_and_strain", "divergent_reuse_and_investment", "durable_anchors_and_strained_interfaces", "uneven_center_access", "high_uncertainty_mechanism_only", "maintenance_seams_and_unknown_territories", "national_context_only", "high; local distribution and mechanisms unknown"),
    }
    rows: list[list[object]] = []
    for scenario in "ABC":
        for horizon in HORIZONS:
            sid = state_key(scenario, horizon)
            base = values[scenario]
            if horizon == 2050:
                projection = "official 2050 county projection evidence available as reference; no deterministic scenario total"
                note = "2050 is an intermediate scenario horizon; values are qualitative and not a forecast total."
            else:
                projection = "explicit scenario only; no mechanical extrapolation"
                note = "2075 is a matured or diverged scenario horizon; no official local point estimate is adopted."
            rows.append([
                sid, SCENARIOS_META[scenario]["name"], horizon, *base[:8], projection, base[8], note + " Dimensions are not aggregated or ranked.",
            ])
    return rows


def load_county_geometry() -> gpd.GeoDataFrame | None:
    if not COUNTY_GEOMETRY.exists():
        return None
    try:
        geometry = gpd.read_file(COUNTY_GEOMETRY)
        geometry["GEOID"] = geometry["GEOID"].astype(str)
        return geometry
    except Exception:
        return None


def map_pattern(scenario: str, node: pd.Series) -> str:
    role = zone_role(node)
    if scenario == "A":
        return "anchor network" if role == "regional_anchor_context" else "connected secondary"
    if scenario == "B":
        return "polycentric center" if role == "regional_anchor_context" else "adaptive node"
    return "durable local anchor" if role == "regional_anchor_context" else "uneven / strain interface"


def render_map(horizon: int, states: pd.DataFrame, nodes: pd.DataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "phase11c-population-settlement-futures"
    geometry = load_county_geometry()
    fig, axes = plt.subplots(1, 3, figsize=(17, 8.8), facecolor="#f1eadc")
    colors = {
        "A": {"anchor network": "#317c78", "connected secondary": "#80b9a7"},
        "B": {"polycentric center": "#b17d2f", "adaptive node": "#d5b071"},
        "C": {"durable local anchor": "#9b4f4b", "uneven / strain interface": "#d69a83"},
    }
    for ax, scenario in zip(axes, "ABC"):
        ax.set_facecolor("#e9e1ce")
        subset = nodes[nodes.node_type == "population_zone"].copy()
        subset["pattern"] = subset.apply(lambda row: map_pattern(scenario, row), axis=1)
        if geometry is not None:
            plot = geometry[geometry.GEOID.isin(set(subset.geoid))].copy()
            plot["pattern"] = plot.GEOID.map(dict(zip(subset.geoid, subset.pattern)))
            for pattern, color in colors[scenario].items():
                part = plot[plot.pattern == pattern]
                if len(part):
                    part.plot(ax=ax, color=color, edgecolor="#f1eadc", linewidth=0.7)
            centroids = subset[["geoid", "name", "latitude", "longitude", "pattern"]].copy()
        else:
            centroids = subset[["geoid", "name", "latitude", "longitude", "pattern"]].copy()
        for _, row in centroids.iterrows():
            ax.scatter(float(row.longitude), float(row.latitude), s=20, color="#17384b", edgecolor="#f1eadc", linewidth=0.5, zorder=4)
            if row.geoid in {"39095", "39173", "18003"}:
                ax.text(float(row.longitude) + 0.015, float(row.latitude) + 0.012, row["name"].replace(" County, ", " "), fontsize=5.4, color="#17384b")
        ax.set_xlim(-85.0, -81.9)
        ax.set_ylim(40.75, 42.25)
        ax.set_axis_off()
        ax.set_title(f"{scenario} — {SCENARIOS_META[scenario]['name']}", loc="left", fontsize=10.2, weight="bold", color="#17384b")
        ax.text(0.01, 0.965, "qualitative spatial redistribution / settlement form", transform=ax.transAxes, va="top", fontsize=6.8, color="#3f4645")
        ax.legend(handles=[Patch(facecolor=color, edgecolor="none", label=pattern) for pattern, color in colors[scenario].items()], loc="lower left", fontsize=6.2, frameon=False, labelcolor="#3f4645")
    map_id = "37" if horizon == 2050 else "37b"
    fig.suptitle(f"MAP {map_id} — POPULATION & SETTLEMENT FUTURES, {horizon}", x=0.04, y=0.975, ha="left", fontsize=15, weight="bold", color="#17384b")
    fig.text(0.04, 0.925, "Three alternative spatial futures for settlement distribution, form, housing, employment geography, and service interfaces. Colors are qualitative scenario states, not population totals, official projections, probabilities, or rankings.", fontsize=7.4, color="#3f4645")
    fig.text(0.04, 0.045, "BOUNDARIES  County polygons are current statistical/cartographic context. Population ≠ household ≠ housing unit ≠ worker ≠ job ≠ commuter. Commuting ≠ migration; climate migration is a high-uncertainty scenario mechanism, not a population-growth assumption. No individual movement, utility-territory assignment, vulnerability/EJ score, or protected-class ranking. Great Black Swamp: C — HOLD / noncanonical. Toledo intake-coordinate discrepancy: UNRESOLVED.", fontsize=6.4, color="#3f4645", wrap=True)
    fig.subplots_adjust(left=0.035, right=0.985, top=0.87, bottom=0.11, wspace=0.04)
    path = MAP2050 if horizon == 2050 else MAP2075
    fig.savefig(path.with_suffix(".png"), dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix(".svg"), facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg = path.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def render_comparison(rows: list[list[object]]) -> None:
    values = [row[3:12] for row in rows]
    labels = [f"{row[0]} — {row[1]}" for row in rows]
    categories = sorted({value for row in values for value in row})
    lookup = {value: index for index, value in enumerate(categories)}
    fig, ax = plt.subplots(figsize=(17, 8.5), facecolor="#f1eadc")
    ax.set_facecolor("#f1eadc")
    ax.imshow([[lookup[value] for value in row] for row in values], cmap="PuBuGn", aspect="auto")
    ax.set_xticks(range(9), [column.replace("_", "\n") for column in COMPARISON_COLUMNS[3:12]], rotation=55, ha="right", fontsize=6.4)
    ax.set_yticks(range(len(labels)), labels, fontsize=7)
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            ax.text(j, i, value.replace("_", " "), ha="center", va="center", fontsize=5.1, color="#17384b", wrap=True)
    ax.set_title("Phase 11C — Qualitative Population & Settlement Futures Comparison", loc="left", fontsize=14, weight="bold", color="#17384b")
    ax.text(0, 1.03, "Rows and dimensions are qualitative scenario descriptors; they are not aggregated, ranked, or converted into a population or vulnerability score.", transform=ax.transAxes, fontsize=7.5, color="#3f4645")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.savefig(COMPARISON_PNG, dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(COMPARISON_SVG, facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    COMPARISON_SVG.write_text("\n".join(line.rstrip() for line in COMPARISON_SVG.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def report_texts(counts: dict[str, int]) -> dict[str, str]:
    source_report = """# Phase 11C Population & Settlement Futures Sources

This package is a separate scenario layer over the accepted Phase 11A and Phase 11B 2026 baselines.[1][2] Those accepted layers retain actual Census, ACS, PEP, LODES, place, county, workplace, residence, and dependency vintages; this phase does not rewrite them.

The U.S. Census Bureau's 2023 National Population Projections provide an official projection series from 2023 through 2100 and use a cohort-component method at national scale.[3][4] That source makes a 2050 projection horizon available for national context, but it does not supply an adopted exact future total for this selected Western Basin county frame. Census PEP produces estimates for counties, cities, towns, and other geographies, which remain estimates rather than a 2050 or 2075 local projection.[5]

Authoritative county-projection products are available for the three state portions of the frame: Ohio's Department of Development publishes a 2020–2050 county projection overview, Michigan's Center for Data and Analytics publishes all-county projections through 2050, and STATS Indiana provides county/substate projections through 2050.[6][7][8] The projection-evidence table records those products as 2050 reference evidence. Exact projection values are intentionally not copied into the qualitative scenario-state rows, because this phase models spatial redistribution and settlement form rather than issuing a deterministic future total; that is a scope boundary, not a claim that projection data are unavailable.

NOAA's climate-impact resource describes effects across water, energy, transportation, infrastructure, ecosystems, and human systems.[9] It informs broad climate-system context, while climate migration remains an explicit high-uncertainty scenario mechanism. No migration count, causal migration explanation, health outcome, vulnerability score, or population-growth assumption is derived from it.

Sources are used to distinguish current observations, official projection context, and explicit scenario assumptions. No source supports the exact 2050/2075 future totals, household totals, housing-unit totals, worker totals, job totals, commuter totals, or individual movements absent from this package.

## Sources

[1] reports/phase11a_population_settlement_freeze_manifest.json
[2] reports/phase11b_population_mobility_dependencies_freeze_manifest.json
[3] https://www.census.gov/programs-surveys/popproj.html
[4] https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html
[5] https://www.census.gov/programs-surveys/popest.html
[6] https://development.ohio.gov/about-us/research/population/population-projections/pop-projection-overview-2020-2050
[7] https://www.michigan.gov/mcda/insights/2025/03/06/mich-county-popproj-2050
[8] https://www.stats.indiana.edu/pop_proj/default.html
[9] https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts
"""
    assumptions_report = """# Phase 11C Population & Settlement Futures Assumption Ledger

The scenario IDs are A2050, A2075, B2050, B2075, C2050, and C2075. Every future row is explicitly classified as `SCENARIO ASSUMPTION` or `SCENARIO CONSEQUENCE`, with `reality_status=fictional` and `canon_status=scenario`, over the accepted Phase 11A/11B baselines.[1][2]

A — Connected Reconcentration explores relative reconcentration around existing settlement and employment anchors, stronger links to secondary centers, and infill/reuse. It does not forecast a basin-wide population increase or assign every resident to an anchor.

B — Polycentric Adaptive Basin explores rebalancing among multiple centers, adaptive town/county nodes, locally varied housing form, and networked employment/service interfaces. B is not a midpoint between A and C; polycentricity is the organizing mechanism.

C — Uneven Change / Infrastructure Strain is an exploratory stress-test. It represents uneven settlement retention, diverging housing reinvestment, persistent employment anchors, and maintenance seams without universal decline, collapse, vulnerability scoring, or a protected-class ranking.

2050 is an intermediate horizon. Official Ohio, Michigan, and Indiana county projection products are used as reference evidence.[6][7][8]
The national Census projection series supplies additional method and horizon context.[3][4]
This package does not copy projection values into the qualitative scenario states or treat them as deterministic scenario totals. 2075 is a matured or diverged scenario horizon, not a mechanical extrapolation and not an official local point estimate.

Climate migration is treated as a high-uncertainty scenario mechanism that may affect housing and settlement demand. It is not a population-growth assumption, migration count, causal claim, or individual movement model.[9]

Population, households, housing units, workers, jobs, and commuters remain separate concepts. The scenario layer changes qualitative relationships among them; it does not convert one unit into another. Current PEP/ACS/LODES products remain baseline estimates or tabulations rather than future observations.[5] Commuting remains distinct from migration, and population presence does not assign utility service territory.

## Sources

[1] reports/phase11a_population_settlement_freeze_manifest.json
[2] reports/phase11b_population_mobility_dependencies_freeze_manifest.json
[3] https://www.census.gov/programs-surveys/popproj.html
[4] https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html
[5] https://www.census.gov/programs-surveys/popest.html
[6] https://development.ohio.gov/about-us/research/population/population-projections/pop-projection-overview-2020-2050
[7] https://www.michigan.gov/mcda/insights/2025/03/06/mich-county-popproj-2050
[8] https://www.stats.indiana.edu/pop_proj/default.html
[9] https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts
"""
    findings_report = f"""# Phase 11C Population & Settlement Futures Findings

## Package scale

The deterministic package contains {counts['assumptions']} scenario assumptions, {counts['projection_evidence']} projection-evidence records, {counts['states']} county-scale future settlement states, {counts['relationships']} qualitative spatial relationships, {counts['uncertainty']} uncertainty states, six comparison rows, and Maps 37/37b. It is a scenario layer over the accepted Phase 11A/11B baselines.[1][2]

## 2050 — intermediate horizon

SCENARIO: 2050 represents a path-dependent intermediate trajectory rather than a future Census observation. A concentrates relative attention around connected anchors and secondary centers; B distributes adaptation among multiple centers; C produces uneven retention and infrastructure-service strain at selected interfaces.

INFERENCE: The meaningful 2050 difference is spatial form: whether settlement demand and reinvestment are organized around connected anchors, distributed among multiple adaptive nodes, or split between durable anchors and strained interfaces. No scenario supplies an exact county total, household total, housing-unit total, worker total, job total, or commuter total.

Official Ohio, Michigan, and Indiana products provide 2050 county projection reference evidence for the selected state portions.[6][7][8]
The package uses those products to establish that an official 2050 reference horizon is available, but does not mechanically combine their different methods or vintages, copy values into scenario states, or treat the current PEP/ACS baseline as a 2050 observation. The national Census projection series remains method and horizon context rather than a local allocation.[3][4]

## 2075 — matured or diverged horizon

SCENARIO: 2075 is intentionally different from 2050. A is a mature connected hub network with established infill and reuse; B is a durable but nonuniform polycentric basin with redundancy and local variation; C is an entrenched patchwork of durable local capacity, retained towns, and strained interfaces.

UNCERTAINTY: 2075 is primarily scenario-based. The package does not extend an official series mechanically, create a point estimate, calculate a compound annual growth rate, or present fake future Census precision.

## Spatial and unit boundaries

The map and state tables preserve county-scale geography as current statistical/cartographic context. They model qualitative spatial redistribution and settlement form, not a population surface. County, place, and employment-center scales remain distinct. Population ≠ household ≠ housing unit ≠ worker ≠ job ≠ commuter. PEP, ACS, and LODES baseline estimates and tabulations remain distinct from future scenario states.[5]

Commuting is not migration. The relationship table contains no individual movement paths, migration counts, freight routes, or household relocation records. Climate migration is a high-uncertainty scenario mechanism, not a population-growth assumption.[9]

Water, wastewater, energy, transport, climate, housing, ecology, environmental-health, nutrient/material, and governance interfaces remain generalized dependencies. Population presence does not assign exact utility service territories, and no vulnerability/EJ score or protected-class ranking is created.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED.

## Sources

[1] reports/phase11a_population_settlement_freeze_manifest.json
[2] reports/phase11b_population_mobility_dependencies_freeze_manifest.json
[3] https://www.census.gov/programs-surveys/popproj.html
[4] https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html
[5] https://www.census.gov/programs-surveys/popest.html
[6] https://development.ohio.gov/about-us/research/population/population-projections/pop-projection-overview-2020-2050
[7] https://www.michigan.gov/mcda/insights/2025/03/06/mich-county-popproj-2050
[8] https://www.stats.indiana.edu/pop_proj/default.html
[9] https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts
"""
    qa_report = f"""# Phase 11C Population & Settlement Futures QA

The package covers six scenario-horizon states: A2050, A2075, B2050, B2075, C2050, and C2075. It contains {counts['assumptions']} assumptions, {counts['projection_evidence']} projection-evidence rows, {counts['states']} county future states, {counts['relationships']} qualitative future relationships, {counts['uncertainty']} uncertainty states, six comparison rows, comparison PNG/SVG, and Maps 37/37b PNG/SVG.

Python and independent R validators check schemas, exact counts, scenario/horizon coverage, baseline-node references, explicit CURRENT FACT / SCENARIO ASSUMPTION / SCENARIO CONSEQUENCE separation, source references, fictional/scenario status, 2050/2075 horizon differentiation, projection boundaries, climate-migration uncertainty, spatial-scale boundaries, person/household/housing-unit/worker/job/commuter distinctions, commuting/migration separation, no numeric future totals, no individual movement, no vulnerability/EJ or protected-class ranking, map integrity, and Phase 11A/11B plus Phase 1–10 immutability.

The maps are qualitative pattern maps over current county geography. They do not use a future population choropleth, exact future label, probability, official local projection, utility territory, vulnerability score, or protected-class ranking. SVG text is retained for inspection, and PNGs are verified as readable image files.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. No Phase 12 content, release, or tag is included.
"""
    return {
        "population_settlement_future_sources.md": source_report,
        "population_settlement_future_assumptions.md": assumptions_report,
        "population_settlement_future_findings.md": findings_report,
        "population_settlement_future_qa.md": qa_report,
    }


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    # The builder is intentionally rooted at its repository checkout. --root is
    # retained for discoverability but does not change ROOT-relative imports.
    del args
    for path in (ANALYSIS, NETWORKS, SCENARIOS, MAPS, FIGURES, REPORTS):
        path.mkdir(parents=True, exist_ok=True)

    nodes = read_rows(NODES)
    assumptions, lookup = build_assumptions()
    projection_evidence = build_projection_evidence()
    states = build_states(nodes, lookup)
    relationships = build_relationships(lookup)
    uncertainty = build_uncertainty(lookup)
    comparison = build_comparison()
    write_rows(ASSUMPTIONS, ASSUMPTION_COLUMNS, assumptions)
    write_rows(PROJECTION_EVIDENCE, PROJECTION_COLUMNS, projection_evidence)
    write_rows(STATES, STATE_COLUMNS, states)
    write_rows(RELATIONSHIPS, RELATIONSHIP_COLUMNS, relationships)
    write_rows(UNCERTAINTY, UNCERTAINTY_COLUMNS, uncertainty)
    write_rows(SOURCES, SOURCE_COLUMNS, SOURCE_ROWS)
    write_rows(COMPARISON, COMPARISON_COLUMNS, comparison)
    state_frame = pd.DataFrame(states, columns=STATE_COLUMNS)
    render_map(2050, state_frame[state_frame.horizon == 2050], nodes)
    render_map(2075, state_frame[state_frame.horizon == 2075], nodes)
    render_comparison(comparison)
    counts = {
        "scenario_assumptions": len(assumptions),
        "projection_evidence": len(projection_evidence),
        "future_states": len(states),
        "future_relationships": len(relationships),
        "uncertainty_states": len(uncertainty),
        "comparison_rows": len(comparison),
        "scenario_sources": len(SOURCE_ROWS),
    }
    texts = report_texts({
        "assumptions": len(assumptions), "projection_evidence": len(projection_evidence),
        "states": len(states), "relationships": len(relationships), "uncertainty": len(uncertainty),
    })
    for name, text in texts.items():
        (REPORTS / name).write_text(text, encoding="utf-8")
    artifacts = [
        ASSUMPTIONS, PROJECTION_EVIDENCE, STATES, RELATIONSHIPS, UNCERTAINTY, SOURCES, COMPARISON,
        COMPARISON_PNG, COMPARISON_SVG, MAP2050.with_suffix(".png"), MAP2050.with_suffix(".svg"),
        MAP2075.with_suffix(".png"), MAP2075.with_suffix(".svg"), *(REPORTS / name for name in texts),
    ]
    review = REPORTS / "population_settlement_future_independent_review.md"
    if review.exists():
        artifacts.append(review)
    manifest = {
        "phase": "11C",
        "status": "implemented_validated_pending_sol_acceptance",
        "scope": "qualitative population and settlement futures, 2050 / 2075",
        "scenario_ids": list(SCENARIO_IDS),
        "counts": counts,
        "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": digest(path)} for path in artifacts},
        "protected_inputs": [
            "reports/phase11a_population_settlement_freeze_manifest.json",
            "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
            "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
            "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
            "reports/phase10c_governance_futures_freeze_manifest.json",
        ],
        "phase11a_11b_immutable": True,
        "phase1_10_immutable": True,
        "numeric_future_values_adopted": False,
        "climate_migration_as_growth_assumption": False,
        "active_holds_preserved": {
            "great_black_swamp": "C — HOLD / noncanonical",
            "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
        },
        "phase12_implemented": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
