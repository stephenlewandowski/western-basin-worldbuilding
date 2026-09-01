"""Build Phase 3C qualitative energy/grid/compute future scenarios.

The 2026 Phase 3A and Phase 3B tables are read-only inputs.  This builder
creates separate assumption, node-state, edge-delta, comparison, map, and
manifest artifacts for six non-probabilistic scenario states.
"""
from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SCENARIO_DIR = ROOT / "data/processed/scenarios"
MAP_DIR = ROOT / "outputs/maps/systems"
FIG_DIR = ROOT / "outputs/figures"
REPORT_DIR = ROOT / "reports"

BASELINE = ROOT / "data/processed/networks/energy_system_nodes.csv"

SOURCE_ROWS = [
    {
        "source_id": "SRC-EIA-AEO2026",
        "title": "Annual Energy Outlook 2026",
        "agency_or_publisher": "U.S. Energy Information Administration",
        "url_or_identifier": "https://www.eia.gov/outlooks/aeo/",
        "publication_or_dataset_date": "2026-04-08",
        "notes": "Alternative cases document uncertainty in electricity demand, fuels, nuclear, and renewable trajectories; not a Western Basin forecast.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-EIA-DATACENTER-2026",
        "title": "Data center server energy use grows across the commercial building stock",
        "agency_or_publisher": "U.S. Energy Information Administration",
        "url_or_identifier": "https://www.eia.gov/todayinenergy/detail.php?id=67704",
        "publication_or_dataset_date": "2026-05-19",
        "notes": "Supports compute-growth as a broad driver; national projection is not allocated to Toledo or a named future facility.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-PJM-LOAD-2026",
        "title": "2026 Long-Term Load Forecast",
        "agency_or_publisher": "PJM Interconnection",
        "url_or_identifier": "https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2026-load-report.pdf",
        "publication_or_dataset_date": "2026-01-14",
        "notes": "Planning forecast includes large-load adjustments, data centers, electrification, storage, and uncertainty treatment; not a local feeder model.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-DOE-TRANSMISSION-2026",
        "title": "National Transmission Needs Study (draft)",
        "agency_or_publisher": "U.S. Department of Energy",
        "url_or_identifier": "https://www.energy.gov/oe/national-transmission-needs-study",
        "publication_or_dataset_date": "2026-07-09",
        "notes": "Broad driver for modernization, load growth, new generation integration, and severe-weather resilience; no corridor is assigned.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-DOE-GRID-DEPLOYMENT-2025",
        "title": "Pathways to Commercial Liftoff: Innovative Grid Deployment",
        "agency_or_publisher": "U.S. Department of Energy",
        "url_or_identifier": "https://www.energy.gov/sites/default/files/2025-07/LIFTOFF_DOE_Innovative-Grid-Deployment.pdf",
        "publication_or_dataset_date": "2025-07",
        "notes": "Supports grid-enhancing technologies, digitization, topology optimization, and storage as qualitative modernization options.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-NREL-STORAGE-2021",
        "title": "Storage Futures Study",
        "agency_or_publisher": "National Renewable Energy Laboratory",
        "url_or_identifier": "https://www.nrel.gov/docs/fy22osti/81956.pdf",
        "publication_or_dataset_date": "2022-06",
        "notes": "Supports multiple storage deployment pathways through 2050; does not supply project-specific duration or siting.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-NRC-LICENSE-RENEWAL-2026",
        "title": "Reactor License Renewal Overview",
        "agency_or_publisher": "U.S. Nuclear Regulatory Commission",
        "url_or_identifier": "https://www.nrc.gov/reactors/operating/licensing/renewal/overview",
        "publication_or_dataset_date": "2026-08-27",
        "notes": "Confirms renewal is voluntary and case-specific; supports scenario uncertainty for Davis-Besse and Fermi 2 without assuming extensions.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-DOE-INDUSTRIAL-2050",
        "title": "Industrial Technology Joint Strategy / Industrial Decarbonization Roadmap",
        "agency_or_publisher": "U.S. Department of Energy",
        "url_or_identifier": "https://www.energy.gov/industrial-technologies/industrial-technology-joint-strategy-factsheet",
        "publication_or_dataset_date": "2022-09",
        "notes": "Supports efficiency, electrification, low-carbon fuels, and process innovation as alternative industrial pathways to 2050.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
    {
        "source_id": "SRC-DOE-LDES-2023",
        "title": "Pathways to Commercial Liftoff: Long Duration Energy Storage Opportunities",
        "agency_or_publisher": "U.S. Department of Energy",
        "url_or_identifier": "https://www.energy.gov/sites/default/files/2023-09/Pathways%20to%20Commercial%20Liftoff%20Long%20Duration%20Energy%20Storage%20Opportunities_508.pdf",
        "publication_or_dataset_date": "2023-09",
        "notes": "Supports differentiated short- and long-duration storage roles; no scenario duration is treated as a guarantee.",
        "retrieved_date": "2026-09-01",
        "confidence": "high",
    },
]

ASSET_ORDER = [
    "ENE-EIA-6149", "ENE-EIA-1729", "ENE-EIA-1733", "ENE-EIA-59764",
    "ENE-EIA-55348", "ENE-EIA-55701", "ENE-EIA-60622", "ENE-EIA-63322",
    "ENE-EIA-56226", "ENE-EIA-67758", "ENE-EIA-65951", "ENE-LOAD-COLLINS",
    "ENE-LOAD-BAYVIEW", "ENE-LOAD-ELMORE", "ENE-LOAD-WOODVILLE",
    "ENE-COMPUTE-BG-5MW",
]

ROLE_TO_CHANGE = {
    "PERSISTS": "persist",
    "EXPANDS ROLE": "expand_role",
    "CHANGES FUNCTION": "new_function",
    "DECLINES": "decline_role",
    "RETIRES": "retire",
    "UNKNOWN": "uncertain_future",
}

DOMAIN_FOR_TYPE = {
    "generation": "GEN",
    "storage": "STORAGE",
    "major_load": "LOAD",
    "compute": "COMPUTE",
}

SCENARIOS = {
    "A2050": {
        "year": 2050, "family": "A", "name": "Managed Transition",
        "premise": "Evolutionary transition absorbs Monroe's retirement through a changing regional mix.",
        "plausibility": "moderate",
        "roles": {
            "ENE-EIA-6149": "PERSISTS", "ENE-EIA-1729": "PERSISTS", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "DECLINES", "ENE-EIA-55348": "DECLINES", "ENE-EIA-55701": "DECLINES",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "CHANGES FUNCTION", "ENE-LOAD-BAYVIEW": "CHANGES FUNCTION",
            "ENE-LOAD-ELMORE": "EXPANDS ROLE", "ENE-LOAD-WOODVILLE": "CHANGES FUNCTION",
            "ENE-COMPUTE-BG-5MW": "EXPANDS ROLE",
        },
        "gas_change": "dependency_reduced", "nuclear_change": "dependency_increased",
        "water_change": "dependency_reduced", "compute_change": "dependency_increased",
        "dependency_note": "Incremental modernization and efficiency reduce selected critical-load exposure while preserving regional coordination.",
    },
    "A2075": {
        "year": 2075, "family": "A", "name": "Managed Transition",
        "premise": "A mature, lower-fuel mix emerges, but nuclear license outcomes and compute scale remain uncertain.",
        "plausibility": "moderate",
        "roles": {
            "ENE-EIA-6149": "UNKNOWN", "ENE-EIA-1729": "UNKNOWN", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "DECLINES", "ENE-EIA-55348": "DECLINES", "ENE-EIA-55701": "DECLINES",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "CHANGES FUNCTION", "ENE-LOAD-BAYVIEW": "CHANGES FUNCTION",
            "ENE-LOAD-ELMORE": "EXPANDS ROLE", "ENE-LOAD-WOODVILLE": "CHANGES FUNCTION",
            "ENE-COMPUTE-BG-5MW": "EXPANDS ROLE",
        },
        "gas_change": "dependency_reduced", "nuclear_change": "uncertain_future",
        "water_change": "dependency_reduced", "compute_change": "dependency_increased",
        "dependency_note": "Mature efficiency and flexibility lower direct fuel dependence, but no technology replacement is assumed.",
    },
    "B2050": {
        "year": 2050, "family": "B", "name": "Distributed Resilience",
        "premise": "Reliability is increasingly delivered by distributed support, flexible demand, and critical-load resilience.",
        "plausibility": "moderate",
        "roles": {
            "ENE-EIA-6149": "PERSISTS", "ENE-EIA-1729": "PERSISTS", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "DECLINES", "ENE-EIA-55348": "DECLINES", "ENE-EIA-55701": "DECLINES",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "CHANGES FUNCTION", "ENE-LOAD-BAYVIEW": "CHANGES FUNCTION",
            "ENE-LOAD-ELMORE": "CHANGES FUNCTION", "ENE-LOAD-WOODVILLE": "CHANGES FUNCTION",
            "ENE-COMPUTE-BG-5MW": "CHANGES FUNCTION",
        },
        "gas_change": "dependency_reduced", "nuclear_change": "dependency_reduced",
        "water_change": "dependency_reduced", "compute_change": "dependency_reduced",
        "dependency_note": "Distributed support reduces selected single-interface dependence; storage is still finite and conditional.",
    },
    "B2075": {
        "year": 2075, "family": "B", "name": "Distributed Resilience",
        "premise": "A mature mesh of distributed support and demand flexibility carries more critical functions locally.",
        "plausibility": "moderate",
        "roles": {
            "ENE-EIA-6149": "PERSISTS", "ENE-EIA-1729": "UNKNOWN", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "DECLINES", "ENE-EIA-55348": "DECLINES", "ENE-EIA-55701": "DECLINES",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "CHANGES FUNCTION", "ENE-LOAD-BAYVIEW": "CHANGES FUNCTION",
            "ENE-LOAD-ELMORE": "CHANGES FUNCTION", "ENE-LOAD-WOODVILLE": "CHANGES FUNCTION",
            "ENE-COMPUTE-BG-5MW": "EXPANDS ROLE",
        },
        "gas_change": "dependency_reduced", "nuclear_change": "uncertain_future",
        "water_change": "dependency_reduced", "compute_change": "dependency_reduced",
        "dependency_note": "Local flexibility and water-system resilience are stronger, but no indefinite islanding or guaranteed autonomy is modeled.",
    },
    "C2050": {
        "year": 2050, "family": "C", "name": "High-Load Convergence",
        "premise": "Advanced materials, electrification, compute, and strategic manufacturing increase the value of firm power.",
        "plausibility": "exploratory",
        "roles": {
            "ENE-EIA-6149": "EXPANDS ROLE", "ENE-EIA-1729": "EXPANDS ROLE", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "PERSISTS", "ENE-EIA-55348": "PERSISTS", "ENE-EIA-55701": "PERSISTS",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "EXPANDS ROLE", "ENE-LOAD-BAYVIEW": "EXPANDS ROLE",
            "ENE-LOAD-ELMORE": "EXPANDS ROLE", "ENE-LOAD-WOODVILLE": "EXPANDS ROLE",
            "ENE-COMPUTE-BG-5MW": "EXPANDS ROLE",
        },
        "gas_change": "dependency_increased", "nuclear_change": "dependency_increased",
        "water_change": "dependency_increased", "compute_change": "dependency_increased",
        "dependency_note": "Concentrated high-value loads increase coupling among grid, cooling, materials, and compute systems.",
    },
    "C2075": {
        "year": 2075, "family": "C", "name": "High-Load Convergence",
        "premise": "A speculative mature convergence keeps strategic industry and compute power-intensive, with uncertain firm-generation choices.",
        "plausibility": "exploratory",
        "roles": {
            "ENE-EIA-6149": "UNKNOWN", "ENE-EIA-1729": "UNKNOWN", "ENE-EIA-1733": "RETIRES",
            "ENE-EIA-59764": "PERSISTS", "ENE-EIA-55348": "PERSISTS", "ENE-EIA-55701": "PERSISTS",
            "ENE-EIA-60622": "EXPANDS ROLE", "ENE-EIA-63322": "EXPANDS ROLE", "ENE-EIA-56226": "EXPANDS ROLE",
            "ENE-EIA-67758": "EXPANDS ROLE", "ENE-EIA-65951": "EXPANDS ROLE",
            "ENE-LOAD-COLLINS": "EXPANDS ROLE", "ENE-LOAD-BAYVIEW": "EXPANDS ROLE",
            "ENE-LOAD-ELMORE": "EXPANDS ROLE", "ENE-LOAD-WOODVILLE": "EXPANDS ROLE",
            "ENE-COMPUTE-BG-5MW": "EXPANDS ROLE",
        },
        "gas_change": "dependency_increased", "nuclear_change": "uncertain_future",
        "water_change": "dependency_increased", "compute_change": "dependency_increased",
        "dependency_note": "High-load convergence strengthens strategic value but leaves fuel, cooling, and firm-generation choices unresolved.",
    },
}

ASSUMPTION_TEMPLATES = {
    "GEN": ("generation", "SRC-EIA-AEO2026", "The regional generation mix changes through retirement, persistence, or expansion roles without assigning future shares or replacement MW."),
    "GRID": ("grid", "SRC-DOE-GRID-DEPLOYMENT-2025", "Grid modernization, coordination, and weather resilience are treated as generalized functions rather than routes, substations, or power-flow claims."),
    "STORAGE": ("storage", "SRC-NREL-STORAGE-2021", "Storage roles expand according to the scenario, but duration, state of charge, and indefinite-backup capability remain unknown."),
    "LOAD": ("critical_loads", "SRC-PJM-LOAD-2026", "Water and industrial critical loads gain efficiency, flexibility, or resilience functions without invented demand values."),
    "COMPUTE": ("compute", "SRC-EIA-DATACENTER-2026", "Compute grows only as a generalized regional or existing-site future role; no hyperscale site, customer, or MW load is assigned."),
    "MATERIALS": ("materials", "SRC-DOE-INDUSTRIAL-2050", "Industrial electrification and circular-material interfaces change process roles without a corridor polygon, freight route, or quantity."),
}

COMPARISON = {
    "A2050": {"centralized_generation_dependence":"moderate","distributed_resilience":"moderate","storage_reliance":"moderate","external_fuel_dependence":"moderate","critical_load_resilience":"moderate","industrial_electrification":"moderate","compute_intensity":"moderate","water_energy_coupling":"moderate"},
    "A2075": {"centralized_generation_dependence":"low","distributed_resilience":"moderate","storage_reliance":"moderate","external_fuel_dependence":"low","critical_load_resilience":"moderate","industrial_electrification":"high","compute_intensity":"moderate","water_energy_coupling":"low"},
    "B2050": {"centralized_generation_dependence":"low","distributed_resilience":"high","storage_reliance":"high","external_fuel_dependence":"low","critical_load_resilience":"high","industrial_electrification":"moderate","compute_intensity":"moderate","water_energy_coupling":"low"},
    "B2075": {"centralized_generation_dependence":"low","distributed_resilience":"high","storage_reliance":"high","external_fuel_dependence":"low","critical_load_resilience":"high","industrial_electrification":"high","compute_intensity":"moderate","water_energy_coupling":"low"},
    "C2050": {"centralized_generation_dependence":"high","distributed_resilience":"moderate","storage_reliance":"high","external_fuel_dependence":"high","critical_load_resilience":"moderate","industrial_electrification":"high","compute_intensity":"high","water_energy_coupling":"high"},
    "C2075": {"centralized_generation_dependence":"high","distributed_resilience":"moderate","storage_reliance":"high","external_fuel_dependence":"high","critical_load_resilience":"moderate","industrial_electrification":"high","compute_intensity":"high","water_energy_coupling":"high"},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_assumptions() -> pd.DataFrame:
    rows = []
    for sid, cfg in SCENARIOS.items():
        for code, (domain, source_id, basis) in ASSUMPTION_TEMPLATES.items():
            text = {
                "GEN": f"{cfg['name']} treats Monroe's planned retirement and the nuclear/gas/renewable mix as {cfg['roles']['ENE-EIA-1733'].lower()} / scenario-dependent; no single replacement is selected.",
                "GRID": cfg["dependency_note"],
                "STORAGE": "Storage expands as a balancing or resilience resource, but it is finite and not indefinite backup.",
                "LOAD": "Collins Park and Bay View receive a qualitative resilience/efficiency treatment; Elmore and Woodville remain energy-relevant without demand values.",
                "COMPUTE": "Oppidan remains planned/unverified in 2026; future compute is generalized or an existing-site role, never an invented hyperscale campus.",
                "MATERIALS": "Industrial electrification and circular-material coupling are explored as functions; no Materials Corridor polygon or freight route is created.",
            }[code]
            uncertainty = "moderate" if cfg["plausibility"] != "exploratory" else "high"
            if code == "GEN" and sid in {"A2075", "B2075", "C2075"}:
                uncertainty = "high"
            rows.append({
                "assumption_id": f"{sid}-{code}", "scenario_id": sid, "scenario_year": cfg["year"],
                "domain": domain, "assumption": text, "basis": basis, "source_id": source_id,
                "plausibility": cfg["plausibility"], "uncertainty": uncertainty,
                "dependency": "qualitative_system_delta", "status": "scenario_assumption",
                "notes": "No numeric probability, future MW value, precise route, or facility coordinate is assigned.",
            })
    return pd.DataFrame(rows)


def build_nodes(baseline: pd.DataFrame, assumptions: pd.DataFrame) -> pd.DataFrame:
    records = []
    by_id = baseline.set_index("node_id")
    for sid, cfg in SCENARIOS.items():
        for node_id in ASSET_ORDER:
            row = by_id.loc[node_id]
            role = cfg["roles"][node_id]
            code = DOMAIN_FOR_TYPE[row["node_type"]]
            records.append({
                "scenario_id": sid, "scenario_year": cfg["year"], "baseline_object_id": node_id,
                "object_id": f"{sid}-{node_id}", "object_name": row["name"], "object_class": row["node_type"],
                "change_type": ROLE_TO_CHANGE[role], "future_role": role, "reality_status": "fictional",
                "relationship_basis": "scenario_assumption", "assumption_id": f"{sid}-{code}",
                "plausibility": cfg["plausibility"], "source_or_basis": f"{sid}-{code}",
                "notes": "Scenario state only; 2026 factual row remains unchanged. " + cfg["dependency_note"],
            })
        new_nodes = [
            (f"SCN-{sid}-GRID", "Regional grid modernization function", "grid_function", "new_node", "GRID", "Generalized sensors, coordination, and grid-enhancing function; no route or substation."),
            (f"SCN-{sid}-RESILIENCE", "Critical-load resilience function", "resilience_function", "new_node", "LOAD", "Generalized water/industrial resilience support; no microgrid site or backup duration."),
            (f"SCN-{sid}-INDUSTRIAL-COMPUTE", "Industrial / compute convergence function", "industrial_compute_function", "new_node", "COMPUTE", "Generalized existing-site or regional function; no hyperscale customer or future MW."),
        ]
        for object_id, name, cls, change_type, code, note in new_nodes:
            records.append({
                "scenario_id": sid, "scenario_year": cfg["year"], "baseline_object_id": "",
                "object_id": object_id, "object_name": name, "object_class": cls,
                "change_type": change_type, "future_role": "NEW FUNCTION", "reality_status": "fictional",
                "relationship_basis": "scenario_assumption", "assumption_id": f"{sid}-{code}",
                "plausibility": cfg["plausibility"], "source_or_basis": f"{sid}-{code}", "notes": note,
            })
    return pd.DataFrame(records)


def build_edges() -> pd.DataFrame:
    rows = []
    gas_assets = ["ENE-EIA-59764", "ENE-EIA-55348", "ENE-EIA-55701"]
    nuclear_assets = ["ENE-EIA-6149", "ENE-EIA-1729"]
    renewables = ["ENE-EIA-60622", "ENE-EIA-63322", "ENE-EIA-56226"]

    def add(sid, from_id, to_id, change, aid, note):
        cfg = SCENARIOS[sid]
        rows.append({
            "scenario_id": sid, "scenario_year": cfg["year"], "from_object_id": from_id,
            "to_object_id": to_id, "change_type": change, "reality_status": "fictional",
            "relationship_basis": "scenario_assumption", "assumption_id": aid,
            "plausibility": cfg["plausibility"], "source_or_basis": aid,
            "notes": note + " Not a power-flow route or quantitative reliability claim.",
        })

    for sid, cfg in SCENARIOS.items():
        # New generalized functions connect to existing regional interfaces and loads.
        add(sid, f"SCN-{sid}-GRID", "ENE-GRID-ATSI", "new_edge", f"{sid}-GRID", "Scenario grid-modernization function supports the ATSI interface.")
        add(sid, f"SCN-{sid}-GRID", "ENE-GRID-DTE", "new_edge", f"{sid}-GRID", "Scenario grid-modernization function supports the DTE interface.")
        add(sid, f"SCN-{sid}-RESILIENCE", "ENE-LOAD-COLLINS", "resilience_upgrade", f"{sid}-LOAD", "Qualitative critical-water resilience function.")
        add(sid, f"SCN-{sid}-RESILIENCE", "ENE-LOAD-BAYVIEW", "distributed_support", f"{sid}-LOAD", "Qualitative wastewater resilience function.")
        add(sid, f"SCN-{sid}-INDUSTRIAL-COMPUTE", "ENE-LOAD-ELMORE", "dependency_increased" if sid.startswith("C") else "new_function", f"{sid}-MATERIALS", "Industrial-processing role changes without facility demand values.")
        add(sid, f"SCN-{sid}-INDUSTRIAL-COMPUTE", "ENE-LOAD-WOODVILLE", "dependency_increased" if sid.startswith("C") else "new_function", f"{sid}-MATERIALS", "Industrial-efficiency/electrification role changes without route or quantity.")
        add(sid, f"SCN-{sid}-INDUSTRIAL-COMPUTE", "ENE-COMPUTE-BG-5MW", "compute_growth" if sid != "B2050" else "dependency_reduced", f"{sid}-COMPUTE", "Generalized compute-service role; Oppidan's 2026 status remains planned/unverified.")
        add(sid, "ENE-EIA-65951", "ENE-GRID-ATSI", "storage_expansion", f"{sid}-STORAGE", "Bowling Green storage becomes a scenario support interface.")
        add(sid, "ENE-EIA-67758", "ENE-GRID-DTE", "storage_expansion", f"{sid}-STORAGE", "Slocum storage becomes a scenario support interface.")
        for asset in gas_assets:
            add(sid, "DEP-NATURAL-GAS-SUPPLY", asset, cfg["gas_change"], f"{sid}-GEN", "External natural-gas dependence changes qualitatively.")
        add(sid, "DEP-FUEL-LOGISTICS", "ENE-EIA-1733", "dependency_reduced" if cfg["roles"]["ENE-EIA-1733"] == "RETIRES" else "dependency_increased", f"{sid}-GEN", "Monroe fuel/logistics relationship follows the scenario transition context.")
        for asset in nuclear_assets:
            add(sid, "DEP-COOLING-WATER", asset, cfg["nuclear_change"], f"{sid}-GEN", "Nuclear cooling/water relationship remains qualitative and license-dependent.")
        for asset in renewables:
            add(sid, "DEP-WEATHER-RESOURCE", asset, "dependency_increased" if cfg["roles"][asset] == "EXPANDS ROLE" else "uncertain_future", f"{sid}-GEN", "Weather/resource dependence changes with renewable role.")
        add(sid, "DEP-COMMUNICATIONS-NETWORK", f"SCN-{sid}-GRID", "new_edge", f"{sid}-GRID", "Operational communications remain a generalized coordination dependency.")
    return pd.DataFrame(rows)


def build_comparison() -> pd.DataFrame:
    rows = []
    for sid, values in COMPARISON.items():
        for dimension, level in values.items():
            rows.append({"scenario_id": sid, "scenario_year": SCENARIOS[sid]["year"], "scenario_family": SCENARIOS[sid]["family"], "dimension": dimension, "level": level, "basis": "qualitative scenario comparison; not probability or quantitative risk"})
    return pd.DataFrame(rows)


ROLE_COLORS = {
    "PERSISTS": "#2f5d8a", "EXPANDS ROLE": "#2e8b57", "CHANGES FUNCTION": "#7a55a3",
    "DECLINES": "#d08b24", "RETIRES": "#333333", "UNKNOWN": "#f3efe5",
}
# A square is used for UNKNOWN so the legend remains renderable across
# Matplotlib versions; the label itself carries the uncertainty meaning.
ROLE_MARKERS = {"PERSISTS":"o", "EXPANDS ROLE":"*", "CHANGES FUNCTION":"D", "DECLINES":"v", "RETIRES":"x", "UNKNOWN":"s"}


def draw_panel(ax, sid: str, baseline: pd.DataFrame, nodes: pd.DataFrame, edges: pd.DataFrame, horizon: int):
    cfg = SCENARIOS[sid]
    ax.set_xlim(-83.92, -83.00)
    ax.set_ylim(41.22, 42.24)
    ax.set_facecolor("#f4efdf")
    ax.grid(color="#c8c0ac", alpha=.35, linewidth=.6)
    # Lake Erie and a schematic regional shoreline, deliberately non-authoritative.
    lake = Polygon([(-83.92,42.06),(-83.72,42.16),(-83.38,42.19),(-83.00,42.16),(-83.00,42.24),(-83.92,42.24)], facecolor="#b7d7e4", edgecolor="#6c9db1", linewidth=1.0, alpha=.9)
    ax.add_patch(lake)
    ax.text(-83.25, 42.18, "LAKE ERIE", color="#326b86", fontsize=9, weight="bold", ha="center")
    # Faint county/grid context.
    for x in np.linspace(-83.85, -83.1, 6):
        ax.plot([x,x], [41.26,42.14], color="#b8af9d", lw=.55, alpha=.55)
    for y in np.linspace(41.38, 42.02, 5):
        ax.plot([-83.9,-83.02], [y,y], color="#b8af9d", lw=.55, alpha=.55)

    b = baseline.set_index("node_id")
    s = nodes[(nodes.scenario_id == sid) & (nodes.baseline_object_id != "")].set_index("baseline_object_id")
    for node_id, row in b.iterrows():
        if pd.isna(row.get("latitude")) or pd.isna(row.get("longitude")):
            continue
        x, y = float(row["longitude"]), float(row["latitude"])
        ax.scatter([x],[y],s=20,c="#777777",alpha=.45,zorder=3)
    # Future role markers and labels.
    for node_id, row in s.iterrows():
        x, y = float(b.loc[node_id,"longitude"]), float(b.loc[node_id,"latitude"])
        role = row.future_role
        face = ROLE_COLORS[role]
        edge = "#222222" if role == "UNKNOWN" else face
        ax.scatter([x],[y],s=90 if role != "EXPANDS ROLE" else 125, marker=ROLE_MARKERS[role], facecolors=face if role != "UNKNOWN" else "#ffffff", edgecolors=edge, linewidths=1.2, zorder=5)
        short = str(b.loc[node_id,"name"]).replace("Bowling Green Energy Storage Project","BG storage").replace("DG AMP Solar Bowling Green","BG solar").replace("Bowling Green Wind","BG wind").replace("Temperance Solar, LLC","Temperance solar").replace("Oppidan Bowling Green data-center project","Oppidan compute")
        if len(short) > 19: short = short[:18] + "…"
        ax.text(x+0.012, y+0.008, short, fontsize=5.8, color="#263b4d", zorder=6)
    # A few qualitative scenario relationships, curved and explicitly non-geographic.
    def xy(node_id):
        if node_id.startswith("SCN-"):
            if node_id.endswith("GRID"): return (-83.52, 41.58)
            if node_id.endswith("RESILIENCE"): return (-83.58, 41.42)
            return (-83.35, 41.38)
        if node_id in b.index: return (float(b.loc[node_id,"longitude"]), float(b.loc[node_id,"latitude"]))
        if node_id == "ENE-GRID-ATSI": return (-83.55,41.64)
        if node_id == "ENE-GRID-DTE": return (-83.27,41.84)
        return (-83.45,41.65)
    plotted = 0
    for _, edge in edges[edges.scenario_id == sid].iterrows():
        if plotted >= 11: break
        from_id, to_id = edge.from_object_id, edge.to_object_id
        if from_id.startswith("DEP-") or to_id.startswith("DEP-"): continue
        x1,y1=xy(from_id); x2,y2=xy(to_id)
        color = "#b45d3f" if edge.change_type in {"dependency_increased","compute_growth"} else "#4b7f78"
        rad = 0.12 if plotted % 2 else -0.10
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),connectionstyle=f"arc3,rad={rad}",arrowstyle="-|>",mutation_scale=7,lw=1.0,linestyle="--",color=color,alpha=.65,zorder=2))
        plotted += 1
    ax.set_title(f"{cfg['family']} — {cfg['name']}\n{sid} · {horizon}", fontsize=11, weight="bold", color="#17324d", pad=7)
    ax.text(0.02, 0.98, textwrap.fill(cfg["premise"], 43), transform=ax.transAxes, va="top", fontsize=7.4, color="#3e4d58", bbox=dict(boxstyle="round,pad=.35", facecolor="#f8f3e6", edgecolor="#a88f6c", alpha=.95))
    ax.text(0.02, 0.02, "colored markers = scenario roles\nlines = qualitative relationships, not power flows", transform=ax.transAxes, va="bottom", fontsize=6.3, color="#4f4b43")


def render_map(path_png: Path, path_svg: Path, horizon: int, baseline: pd.DataFrame, nodes: pd.DataFrame, edges: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(18, 8.8), dpi=220, constrained_layout=False)
    fig.patch.set_facecolor("#eee6d3")
    fig.suptitle(f"MAP {13 if horizon == 2050 else '13b'} — ENERGY / GRID / COMPUTE FUTURES, {horizon}", fontsize=19, weight="bold", color="#17324d", y=.985)
    fig.text(.5, .948, "2026 factual anchors are retained; colored future roles are scenario deltas, not forecasts or power-flow routes.", ha="center", fontsize=10.0, color="#4d5961")
    for ax, sid in zip(axes, [f"A{horizon}", f"B{horizon}", f"C{horizon}"]):
        draw_panel(ax, sid, baseline, nodes, edges, horizon)
    handles = [Line2D([0],[0],marker=ROLE_MARKERS[r],color="none",markerfacecolor=ROLE_COLORS[r] if r != "UNKNOWN" else "#ffffff",markeredgecolor="#333333",markersize=9,label=r) for r in ROLE_COLORS]
    fig.legend(handles=handles, loc="lower center", ncol=6, bbox_to_anchor=(.5,.028), frameon=False, fontsize=9)
    fig.text(.5, .002, "SCENARIO ASSUMPTIONS · NO PRECISE FUTURE MW, SUBSTATIONS, TRANSMISSION ROUTES, OUTAGE PROBABILITIES, OR RESTORATION TIMES", ha="center", fontsize=8, color="#6b5d4a")
    fig.subplots_adjust(left=.025,right=.975,top=.84,bottom=.11,wspace=.055)
    fig.savefig(path_png, facecolor=fig.get_facecolor())
    fig.savefig(path_svg, format="svg", facecolor=fig.get_facecolor())
    plt.close(fig)


def render_comparison(path: Path, comparison: pd.DataFrame):
    dimensions = list(COMPARISON["A2050"].keys())
    scenarios = list(SCENARIOS)
    level_map = {"low":0,"moderate":1,"high":2}
    data = np.array([[level_map[COMPARISON[s][d]] for d in dimensions] for s in scenarios])
    fig, ax = plt.subplots(figsize=(15, 6.5), dpi=220)
    fig.patch.set_facecolor("#eee6d3")
    ax.set_facecolor("#f8f3e6")
    cmap = plt.matplotlib.colors.ListedColormap(["#b8d4cf", "#e3b96e", "#c45a47"])
    ax.imshow(data, cmap=cmap, vmin=-.5, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(dimensions)), [d.replace("_", "\n") for d in dimensions], rotation=0, fontsize=9)
    ax.set_yticks(range(len(scenarios)), [f"{s} — {SCENARIOS[s]['name']}" for s in scenarios], fontsize=9)
    for i, sid in enumerate(scenarios):
        for j, d in enumerate(dimensions):
            ax.text(j,i,COMPARISON[sid][d],ha="center",va="center",fontsize=8,color="#22313b")
    ax.set_title("QUALITATIVE ENERGY FUTURES COMPARISON — WESTERN BASIN", fontsize=17, weight="bold", color="#17324d", pad=28)
    ax.text(.5,1.02,"2050 / 2075 scenario deltas · low / moderate / high are qualitative intensity descriptors, not probability", transform=ax.transAxes, ha="center", fontsize=10, color="#4d5961")
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_xticks(np.arange(-.5,len(dimensions),1), minor=True); ax.set_yticks(np.arange(-.5,len(scenarios),1), minor=True)
    ax.grid(which="minor", color="#f8f3e6", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.tight_layout(rect=(.01,.04,.99,.94))
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    for directory in (SCENARIO_DIR, MAP_DIR, FIG_DIR, REPORT_DIR): directory.mkdir(parents=True, exist_ok=True)
    baseline = pd.read_csv(BASELINE)
    assumptions = build_assumptions()
    nodes = build_nodes(baseline, assumptions)
    edges = build_edges()
    comparison = build_comparison()
    sources = pd.DataFrame(SOURCE_ROWS)

    assumptions.to_csv(SCENARIO_DIR / "energy_scenario_assumptions.csv", index=False)
    nodes.to_csv(SCENARIO_DIR / "energy_nodes_scenario.csv", index=False)
    edges.to_csv(SCENARIO_DIR / "energy_edges_scenario.csv", index=False)
    comparison.to_csv(FIG_DIR / "energy_scenarios_comparison.csv", index=False)
    sources.to_csv(SCENARIO_DIR / "energy_scenario_sources.csv", index=False)

    render_map(MAP_DIR / "13_energy_grid_compute_futures_2050.png", MAP_DIR / "13_energy_grid_compute_futures_2050.svg", 2050, baseline, nodes, edges)
    render_map(MAP_DIR / "13b_energy_grid_compute_futures_2075.png", MAP_DIR / "13b_energy_grid_compute_futures_2075.svg", 2075, baseline, nodes, edges)
    render_comparison(FIG_DIR / "energy_scenarios_comparison.png", comparison)

    artifacts = [
        SCENARIO_DIR / "energy_scenario_assumptions.csv", SCENARIO_DIR / "energy_nodes_scenario.csv",
        SCENARIO_DIR / "energy_edges_scenario.csv", SCENARIO_DIR / "energy_scenario_sources.csv",
        FIG_DIR / "energy_scenarios_comparison.csv", FIG_DIR / "energy_scenarios_comparison.png",
        MAP_DIR / "13_energy_grid_compute_futures_2050.png", MAP_DIR / "13_energy_grid_compute_futures_2050.svg",
        MAP_DIR / "13b_energy_grid_compute_futures_2075.png", MAP_DIR / "13b_energy_grid_compute_futures_2075.svg",
    ]
    manifest = {
        "phase": "3C", "generated": "2026-09-01", "scenario_ids": list(SCENARIOS),
        "counts": {"assumptions": len(assumptions), "scenario_node_states": len(nodes), "scenario_edge_deltas": len(edges), "comparison_rows": len(comparison), "sources": len(sources)},
        "artifacts": {str(p.relative_to(ROOT)): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in artifacts},
    }
    (REPORT_DIR / "energy_scenario_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
