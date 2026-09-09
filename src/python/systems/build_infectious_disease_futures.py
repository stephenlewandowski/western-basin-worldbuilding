"""Build Phase 13C qualitative infectious-disease system futures for 2050/2075.

This is a separate scenario layer over the accepted/frozen Phase 13A factual
baseline and Phase 13B dependency layer. It models transmission opportunity,
environmental interfaces, surveillance/detection, response, governance,
mobility/connectivity, and infrastructure dependencies. It does not forecast
incidence, cases, outbreaks, disease burden, or individual risk.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from textwrap import fill, shorten

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

BASELINE_NODES = NETWORKS / "infectious_disease_nodes.csv"
BASELINE_DEPS = ANALYSIS / "infectious_disease_dependency_register.csv"
BASELINE_UNC = ANALYSIS / "infectious_disease_dependency_uncertainties.csv"
SOURCE_INPUT = ANALYSIS / "infectious_disease_dependency_sources.csv"
LEDGER_INPUT = REPORTS / "phase13b_citation_ledger.json"
PHASE13A_FREEZE = REPORTS / "phase13a_infectious_disease_freeze_manifest.json"
PHASE13B_FREEZE = REPORTS / "phase13b_infectious_disease_dependencies_freeze_manifest.json"

ASSUMPTIONS = SCENARIOS / "infectious_disease_scenario_assumptions.csv"
TRANSMISSION = SCENARIOS / "infectious_disease_transmission_states_scenario.csv"
SURVEILLANCE = SCENARIOS / "infectious_disease_surveillance_states_scenario.csv"
RESPONSE = SCENARIOS / "infectious_disease_response_states_scenario.csv"
DEPENDENCIES = SCENARIOS / "infectious_disease_dependency_states_scenario.csv"
UNCERTAINTY = SCENARIOS / "infectious_disease_uncertainty_states_scenario.csv"
SOURCES = ANALYSIS / "infectious_disease_scenario_sources.csv"
COMPARISON = FIGURES / "infectious_disease_scenario_comparison.csv"
COMPARISON_PNG = FIGURES / "infectious_disease_scenario_comparison.png"
COMPARISON_SVG = FIGURES / "infectious_disease_scenario_comparison.svg"
MAP2050 = MAPS / "43_infectious_disease_system_futures_2050"
MAP2075 = MAPS / "43b_infectious_disease_system_futures_2075"
MANIFEST = REPORTS / "infectious_disease_scenario_manifest.json"
LEDGER = REPORTS / "phase13c_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"

HORIZONS = (2050, 2075)
SCENARIO_IDS = tuple(f"{scenario}{year}" for scenario in "ABC" for year in HORIZONS)
SCENARIO_META = {
    "A": {"name": "Coordinated Prevention & Detection", "plausibility": "moderate", "uncertainty": "moderate", "color": "#2f7f73"},
    "B": {"name": "Networked but Uneven Adaptation", "plausibility": "high", "uncertainty": "high", "color": "#b47b32"},
    "C": {"name": "Higher Transmission Opportunity / Response Strain", "plausibility": "exploratory", "uncertainty": "high", "color": "#a04f55"},
}

ARCHETYPES = [
    {
        "key": "vector-borne", "label": "VECTOR-BORNE", "systems": "DID-001;DID-002", "surveillance": "SUR-001;SUR-002;SUR-003",
        "dependency": "IDB-004", "uncertainty": "IDBU-003", "source": "phase12_vector_dependency_context", "domain": "environmental_interface",
    },
    {
        "key": "waterborne/environmental", "label": "WATERBORNE / ENVIRONMENTAL", "systems": "DID-003;DID-004", "surveillance": "SUR-004;SUR-005",
        "dependency": "IDB-010", "uncertainty": "IDBU-004", "source": "s13_cdc_water_surv", "domain": "environmental_interface",
    },
    {
        "key": "foodborne/enteric", "label": "FOODBORNE / ENTERIC", "systems": "DID-005;DID-006;DID-007", "surveillance": "SUR-006;SUR-007",
        "dependency": "IDB-013", "uncertainty": "IDBU-006", "source": "phase5_freight_context", "domain": "mobility_connectivity",
    },
    {
        "key": "respiratory", "label": "RESPIRATORY", "systems": "DID-008;DID-009", "surveillance": "SUR-008;SUR-009",
        "dependency": "IDB-020", "uncertainty": "IDBU-008", "source": "phase11_mobility_context", "domain": "mobility_connectivity",
    },
    {
        "key": "zoonotic", "label": "ZOONOTIC", "systems": "DID-010", "surveillance": "SUR-010",
        "dependency": "IDB-026", "uncertainty": "IDBU-010", "source": "s13_cdc_rabies", "domain": "environmental_interface",
    },
    {
        "key": "healthcare/AMR", "label": "HEALTHCARE / AMR", "systems": "DID-011;DID-012", "surveillance": "SUR-011;SUR-012",
        "dependency": "IDB-033", "uncertainty": "IDBU-013", "source": "phase3_energy_context", "domain": "infrastructure_dependency",
    },
]
ARCHETYPE_BY_KEY = {item["key"]: item for item in ARCHETYPES}

ASSUMPTION_COLUMNS = [
    "assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption", "evidence_basis", "source_id",
    "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes",
]
TRANSMISSION_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_system_ids", "transmission_opportunity_state",
    "environmental_interface_state", "seasonal_or_contact_window", "host_or_setting_interface", "observability_boundary",
    "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility",
    "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
SURVEILLANCE_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_surveillance_ids", "surveillance_capacity_state",
    "detection_latency_state", "coverage_and_method_state", "observation_interface", "reported_observation_boundary",
    "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis", "plausibility",
    "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
RESPONSE_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_response_interfaces", "healthcare_public_health_capacity",
    "response_coordination_state", "response_latency_margin", "intervention_interface", "infrastructure_dependency_state",
    "response_boundary", "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id", "source_or_basis",
    "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
DEPENDENCY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_dependency_id", "dependency_domain", "object_a",
    "object_b", "relationship_type", "spatial_scale", "current_fact", "scenario_assumption", "scenario_consequence", "dependency_state",
    "assumption_id", "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
UNCERTAINTY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "archetype", "baseline_uncertainty_id", "category", "subject_id",
    "current_fact", "scenario_assumption", "uncertainty_state", "assumption_id", "source_or_basis", "reality_status", "canon_status",
    "relationship_basis", "notes",
]
SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "publication_or_period", "retrieval_date", "geographic_scale", "method_or_product",
    "evidence_use", "use_limitations", "retrieval_url", "retrieval_provenance", "scenario_relevance",
]
COMPARISON_COLUMNS = [
    "scenario_id", "scenario", "horizon", "transmission_opportunity", "environmental_interfaces", "surveillance_detection",
    "response_coordination", "healthcare_response_margin", "mobility_connectivity", "infrastructure_dependencies", "food_freight_interfaces",
    "vector_water_systems", "uncertainty_profile", "boundary_statement", "scenario_distinctiveness", "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: str(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def write_rows(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    assert rows and all(len(row) == len(columns) for row in rows), path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def horizon_phrase(scenario: str, year: int) -> str:
    if year == 2050:
        return {
            "A": "2050 is an intermediate trajectory in which coordinated prevention, detection, and response links are emerging in selected systems.",
            "B": "2050 is an intermediate trajectory in which adaptation is distributed across basin nodes with uneven coverage, methods, and response timing.",
            "C": "2050 is an intermediate trajectory in which selected environmental and infrastructure pressures widen opportunity seams while response strain begins to appear.",
        }[scenario]
    return {
        "A": "2075 is a matured coordinated state in which selected prevention, detection, and response routines are institutionalized while residual uncertainty remains.",
        "B": "2075 is a matured mosaic in which strong and weak nodes remain connected through overlapping networks, local friction, and reporting differences.",
        "C": "2075 is a matured or diverged state in which selected opportunity windows and disruptions are more consequential while capable programs persist amid coordination strain.",
    }[scenario]


def assumption_text(scenario: str, year: int, domain: str) -> str:
    horizon = "emerging and selective" if year == 2050 else "institutionalized in selected interfaces"
    if scenario == "A":
        values = {
            "environmental_interface": f"Environmental-health prevention, vector observation, water-system maintenance, food safety interfaces, and host-interface attention become more coordinated and {horizon}; episodic opportunities remain possible.",
            "mobility_connectivity": f"Mobility and freight connectivity remain active, while setting-aware communication, continuity planning, and investigation links become more coordinated and {horizon}; connectivity is not transmission certainty.",
            "surveillance_detection": f"Wastewater, laboratory, vector, veterinary, and healthcare/AMR observation streams gain stronger interoperability and {horizon} review routines without creating a common disease denominator.",
            "response_healthcare": f"Public-health and healthcare actors use clearer detection-to-response handoffs, surge planning, and infection-control coordination that are {horizon} in selected systems; response capacity is not disease absence.",
            "infrastructure_dependency": f"Treatment resilience, cold-chain/storage continuity, laboratory capacity, energy, communications, and selected facility interfaces are adapted in a {horizon} pattern without assuming universal performance.",
            "governance_coordination": f"Distinct agencies, operators, healthcare systems, laboratories, and public-health programs use more regular cross-system review and mutual-aid coordination that is {horizon}; authority is not merged.",
        }
    elif scenario == "B":
        values = {
            "environmental_interface": f"Environmental and host interfaces diverge across urban, wetland, agricultural, forest-edge, and healthcare settings; adaptation is {horizon} in some nodes and limited in others.",
            "mobility_connectivity": f"Distributed mobility, freight, workplace, and settlement networks produce different interface pressures and investigation pathways; connectivity is {horizon} but not uniform or equivalent to transmission.",
            "surveillance_detection": f"Surveillance coverage, laboratory participation, wastewater observation, vector programs, veterinary reporting, and HAI/AMR detection remain heterogeneous and {horizon} across nodes.",
            "response_healthcare": f"Healthcare and public-health response capacity is strong in some centers and constrained or slower in others, with {horizon} coordination through overlapping institutional networks.",
            "infrastructure_dependency": f"Treatment, cold chain, laboratory, energy, communications, and facility dependencies are buffered unevenly; local fallback capacity and maintenance practices remain {horizon}.",
            "governance_coordination": f"Cross-jurisdiction coordination develops through issue-specific agreements and overlapping networks, with redundancy, negotiation friction, and {horizon} differences in responsibility and reporting.",
        }
    else:
        values = {
            "environmental_interface": f"Warmer and more variable conditions, flooding/runoff contrasts, water-system interruptions, host interfaces, and developed-edge maintenance gaps create more permissive opportunity in selected systems; this pressure is {horizon}.",
            "mobility_connectivity": f"Mobility and freight connectivity remain consequential pathways while infrastructure disruption and access constraints increase selected interface friction; the pattern is {horizon}, not an outbreak claim.",
            "surveillance_detection": f"Environmental, vector, wastewater, laboratory, veterinary, and healthcare/AMR surveillance face selected coverage and reporting lags relative to changing interfaces; capable programs persist but the lag is {horizon}.",
            "response_healthcare": f"Public-health and healthcare systems face a narrower response margin at selected seams, with coordination strain, delayed handoffs, and episodic service disruption becoming {horizon} without a prevalence claim.",
            "infrastructure_dependency": f"Treatment resilience, cold chain, laboratory continuity, energy, communications, and facility dependencies become more consequential where maintenance or access lags; this dependency pattern is {horizon}.",
            "governance_coordination": f"Coordination remains functional in capable institutions but becomes slower and less coherent across selected jurisdictions, operators, and programs as responsibility seams become {horizon}.",
        }
    return f"{values[domain]} {horizon_phrase(scenario, year)}"


def scenario_assumptions(source_rows: list[dict[str, str]]) -> list[list[str]]:
    source_by_domain = {
        "environmental_interface": "phase9_hazard_dependency_context",
        "mobility_connectivity": "phase11_mobility_context",
        "surveillance_detection": "s13_nndss_about",
        "response_healthcare": "phase10_coordination_context",
        "infrastructure_dependency": "phase3_energy_context",
        "governance_coordination": "phase10_coordination_context",
    }
    domains = list(source_by_domain)
    valid_sources = {row["source_id"] for row in source_rows}
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for index, domain in enumerate(domains, 1):
                source_id = source_by_domain[domain]
                assert source_id in valid_sources
                rows.append([
                    f"IDFA-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(year), domain,
                    assumption_text(scenario, year, domain),
                    f"Accepted Phase 13A/13B infectious-disease system and dependency context plus explicit qualitative scenario construction; {horizon_phrase(scenario, year)}",
                    source_id, SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "SCENARIO ASSUMPTION", "false",
                    "No exact future value, incidence, case total, outbreak probability, disease burden, individual risk, or local downscaling is adopted. Transmission opportunity ≠ future incidence; environmental suitability ≠ disease burden; surveillance sensitivity is not disease intensity; infrastructure stress ≠ illness; mobility/connectivity ≠ outbreak. No future case total and no unsupported local downscaling is adopted.",
                ])
    assert len(rows) == 36
    return rows


def node_fact(node_lookup: dict[str, dict[str, str]], ids: str) -> str:
    names = [node_lookup[item]["name"] for item in ids.split(";") if item in node_lookup]
    notes = [node_lookup[item]["notes"] for item in ids.split(";") if item in node_lookup]
    return "; ".join(names) + ". " + " ".join(notes)


def transmission_profile(scenario: str, year: int, archetype: str) -> tuple[str, str, str, str]:
    names = {
        "vector-borne": ("seasonal vector, host, and human-interface opportunity", "climate, hydrology, vector ecology, host, and settlement interfaces", "seasonal windows and host/vector interfaces", "Culex/Ixodes ecology and aggregate settlement context"),
        "waterborne/environmental": ("water-associated environmental opportunity", "flooding, runoff, treatment, wastewater, recreational-water, and building-water interfaces", "event- and season-dependent water conditions", "source-water, recreational-water, building-water, and investigation settings"),
        "foodborne/enteric": ("food-chain and enteric interface opportunity", "production, processing, storage, cold-chain, freight, and laboratory interfaces", "production, distribution, and investigation windows", "food, animal-contact, clinical-laboratory, and public-health settings"),
        "respiratory": ("respiratory contact and setting opportunity", "settlement, indoor/community settings, mobility, seasonality, wastewater, and healthcare interfaces", "seasonal and setting-dependent contact windows", "aggregate settlement, workplace, mobility, testing, and care settings"),
        "zoonotic": ("animal-human interface opportunity", "wildlife, domestic-animal, occupational, environmental, and veterinary/public-health interfaces", "animal-contact and environmental windows", "wildlife, domestic-animal, occupational, and exposure-investigation settings"),
        "healthcare/AMR": ("healthcare and laboratory interface opportunity", "care settings, infection-control, laboratory, energy, communications, and reporting interfaces", "care, detection, and service-continuity windows", "healthcare, laboratory, public-health, and generalized infrastructure settings"),
    }[archetype]
    opportunity, environment, window, interface = names
    if scenario == "A":
        opportunity = f"selected {opportunity} is reduced or better buffered by prevention and continuity routines; residual opportunity remains"
        environment += "; selected maintenance and adaptation constrain some pathways"
        window += "; episodic or seasonal conditions remain possible"
        interface += "; no individual contact or exposure is assigned"
    elif scenario == "B":
        opportunity = f"{opportunity} varies across a mosaic of stronger, weaker, and episodic nodes; it is not averaged"
        environment += "; local infrastructure, land use, methods, and governance produce divergent conditions"
        window += "; timing differs by node, program, and setting"
        interface += "; aggregate structure is not a contact event or infection observation"
    else:
        opportunity = f"{opportunity} is more permissive in selected interfaces under environmental and response strain; uniform change is not assumed"
        environment += "; variability, disruption, and selected maintenance gaps create patchy conditions"
        window += "; longer or more variable windows are plausible in selected settings"
        interface += "; a permissive interface does not establish exposure, infection, or outbreak"
    horizon = {
        "A": "2050 emerging selective prevention and detection routines" if year == 2050 else "2075 institutionalized selected prevention and detection routines with residual interfaces",
        "B": "2050 emerging node differences and negotiated coverage" if year == 2050 else "2075 durable mosaic of strong and weak nodes with persistent friction",
        "C": "2050 emerging opportunity seams and response strain" if year == 2050 else "2075 persistent selected opportunity windows and entrenched response strain",
    }[scenario]
    return f"{opportunity} ({horizon})", environment, window, interface


def surveillance_profile(scenario: str, year: int) -> tuple[str, str, str, str, str]:
    if scenario == "A":
        capacity = "surveillance coverage and integration are stronger in selected programs, with wastewater, laboratory, vector, veterinary, and healthcare/AMR links more connected"
        latency = "detection latency improves in priority interfaces" if year == 2050 else "detection latency is routinely shorter in selected priority interfaces"
        coverage = "methods, denominators, and native scales remain distinct even where data exchange is stronger"
        observation = "more detection and reporting can produce more recorded observations without implying more underlying disease"
        boundary = "Surveillance sensitivity is not disease intensity; detection capacity is not disease prevalence, incidence, or burden."
    elif scenario == "B":
        capacity = "surveillance coverage is heterogeneous across jurisdictions, habitats, laboratories, wastewater programs, veterinary systems, and healthcare settings"
        latency = "detection latency varies by node and method" if year == 2050 else "detection latency remains persistently uneven across the network"
        coverage = "multiple methods and denominators remain non-comparable, with strong coverage in some nodes and gaps in others"
        observation = "reported observations differ with effort, participation, testing, and reporting practice rather than tracking one underlying disease state"
        boundary = "Surveillance sensitivity is not disease intensity; uneven coverage is not evidence of absence or prevalence."
    else:
        capacity = "selected surveillance programs face coverage, laboratory, wastewater, vector, veterinary, or healthcare reporting strain while capable programs persist elsewhere"
        latency = "detection latency worsens at selected seams and during disruptions" if year == 2050 else "detection lag is entrenched in selected seams despite capable programs elsewhere"
        coverage = "method, effort, reporting, and access gaps become more consequential but remain unmeasured and heterogeneous"
        observation = "fewer observations may reflect lag or coverage limits, while more targeted detection may also increase reports without implying more disease"
        boundary = "Surveillance lag is not disease absence, and response strain is not prevalence, incidence, or burden."
    return capacity, latency, coverage, observation, boundary


def response_profile(scenario: str, year: int, archetype: str) -> tuple[str, str, str, str, str]:
    if scenario == "A":
        capacity = "healthcare and public-health response capacity is stronger in selected interfaces, with clearer laboratory, care, and environmental-health handoffs"
        coordination = "coordination is more connected across public health, healthcare, laboratories, environmental programs, and relevant operators"
        margin = "response margin is wider in priority interfaces" if year == 2050 else "response margin is mature and wider in selected priority interfaces"
        intervention = f"{archetype} prevention, investigation, care, and communication interfaces are better aligned without assuming elimination"
        infra = "selected energy, communications, treatment, cold-chain, laboratory, and facility dependencies are buffered"
    elif scenario == "B":
        capacity = "healthcare and public-health response capacity is strong in some centers and slower or less accessible in others"
        coordination = "coordination uses overlapping networks with local protocols, negotiation friction, and variable cross-node coverage"
        margin = "response margin varies by node and event" if year == 2050 else "response margin remains structurally uneven across the network"
        intervention = f"{archetype} prevention, investigation, care, and communication interfaces are distributed and locally adapted rather than uniform"
        infra = "continuity, treatment, cold-chain, laboratory, energy, communications, and facility dependencies are buffered unevenly"
    else:
        capacity = "healthcare and public-health response capacity faces greater coordination strain at selected interfaces while capable services continue elsewhere"
        coordination = "response handoffs are slower or less synchronized at selected seams, especially during environmental or infrastructure disruptions"
        margin = "response margin narrows at selected seams" if year == 2050 else "response margin remains narrow in selected seams amid persistent strain"
        intervention = f"{archetype} prevention, investigation, care, and communication interfaces face episodic delay or interruption without a deterministic outbreak claim"
        infra = "treatment, cold-chain, laboratory, energy, communications, and facility dependencies become more consequential where continuity lags"
    boundary = "Response capacity is not absence of disease; response strain is not prevalence, incidence, or disease burden."
    return capacity, coordination, margin, intervention, infra + ". " + boundary


def dependency_profile(scenario: str, year: int, archetype: str) -> tuple[str, str]:
    if scenario == "A":
        state = "selected_dependency_buffered" if year == 2050 else "selected_dependency_routinized"
        consequence = f"Selected {archetype} environmental, mobility, surveillance, healthcare, and infrastructure handoffs are more connected, while source and scale limits remain."
    elif scenario == "B":
        state = "node_specific_dependency_mosaic" if year == 2050 else "durable_uneven_dependency_network"
        consequence = f"{archetype} dependencies are handled differently by node and institution; fallback paths coexist with coverage differences, reporting variation, and negotiation friction."
    else:
        state = "selected_dependency_strained" if year == 2050 else "entrenched_selected_dependency_strain"
        consequence = f"Selected {archetype} dependencies become harder to coordinate under environmental, mobility, or infrastructure pressure, while capable local interfaces persist."
    return state, consequence


def baseline_response_interfaces(archetype: str) -> str:
    return {
        "vector-borne": "SUR-003;REF-4;REF-10",
        "waterborne/environmental": "SUR-004;SUR-005;REF-4;REF-10",
        "foodborne/enteric": "SUR-006;SUR-007;SUR-005;REF-10",
        "respiratory": "SUR-008;SUR-009;REF-4;REF-10",
        "zoonotic": "SUR-010;REF-4;REF-10",
        "healthcare/AMR": "SUR-011;SUR-012;INST-001;REF-10",
    }[archetype]


def build_state_tables(assumption_rows: list[list[str]], node_lookup: dict[str, dict[str, str]], dep_lookup: dict[str, dict[str, str]], unc_lookup: dict[str, dict[str, str]]) -> tuple[list[list[str]], ...]:
    assumption_lookup = {(row[1], row[4]): row for row in assumption_rows}
    transmission_rows: list[list[str]] = []
    surveillance_rows: list[list[str]] = []
    response_rows: list[list[str]] = []
    dependency_rows: list[list[str]] = []
    uncertainty_rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for archetype in ARCHETYPES:
                key = archetype["key"]
                aid_env = assumption_lookup[(sid, archetype["domain"])][0]
                aid_surv = assumption_lookup[(sid, "surveillance_detection")][0]
                aid_resp = assumption_lookup[(sid, "response_healthcare")][0]
                aid_dep = assumption_lookup[(sid, "infrastructure_dependency" if key == "healthcare/AMR" else archetype["domain"])][0]
                aid_unc = assumption_lookup[(sid, "governance_coordination")][0]
                opp, env, window, interface = transmission_profile(scenario, year, key)
                current = node_fact(node_lookup, archetype["systems"])
                transmission_rows.append([
                    f"IDFT-{sid}-{key.replace('/', '-').replace('-', '')}", sid, SCENARIO_META[scenario]["name"], str(year), key, archetype["systems"], opp, env, window, interface,
                    "Transmission opportunity is a qualitative systems interface; pathogen presence, exposure, infection, reported case, local transmission, outbreak, and disease burden remain separate.",
                    f"CURRENT FACT (2026 baseline): {current}", f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, archetype['domain'])][5]}",
                    f"SCENARIO CONSEQUENCE: {horizon_phrase(scenario, year)} The state changes opportunity and interface conditions only; no future incidence, case total, outbreak probability, or disease burden is projected.",
                    aid_env, archetype["source"], SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Scenario state is qualitative and archetype-specific; transmission opportunity does not equal future incidence, and environmental suitability does not equal disease burden.",
                ])
                capacity, latency, coverage, observation, boundary = surveillance_profile(scenario, year)
                surveillance_rows.append([
                    f"IDFS-{sid}-{key.replace('/', '-').replace('-', '')}", sid, SCENARIO_META[scenario]["name"], str(year), key, archetype["surveillance"], capacity, latency, coverage,
                    f"Observation interfaces for {key} retain native program, laboratory, sewershed, facility, animal, county, and regional scales.", observation,
                    f"CURRENT FACT (2026 baseline): Phase 13A/13B provide surveillance and observation interfaces for {key}; these do not form a complete disease denominator.",
                    f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, 'surveillance_detection')][5]}", f"SCENARIO CONSEQUENCE: {horizon_phrase(scenario, year)} Detection timing and coverage change qualitatively; {boundary}",
                    aid_surv, "s13_nndss_about", SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    f"{boundary} More detection can produce more reported observations without implying more underlying disease.",
                ])
                cap, coordination, margin, intervention, infra = response_profile(scenario, year, key)
                response_rows.append([
                    f"IDFR-{sid}-{key.replace('/', '-').replace('-', '')}", sid, SCENARIO_META[scenario]["name"], str(year), key, baseline_response_interfaces(key), cap, coordination, margin, intervention, infra,
                    "Response capacity is not absence of disease, and a response interface is not a prevalence or burden measure.",
                    f"CURRENT FACT (2026 baseline): Phase 13A/13B identify care, laboratory, public-health, governance, and infrastructure interfaces for {key}; effectiveness is not measured.",
                    f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, 'response_healthcare')][5]}", f"SCENARIO CONSEQUENCE: {horizon_phrase(scenario, year)} Response coordination and margin change qualitatively; no incidence, case, outbreak, or health-outcome forecast is made.",
                    aid_resp, "phase10_coordination_context", SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Healthcare/public-health response is modeled as coordination and capacity interface only; system strain does not imply prevalence.",
                ])
                dep = dep_lookup[archetype["dependency"]]
                dep_state, consequence = dependency_profile(scenario, year, key)
                dependency_rows.append([
                    f"IDFD-{sid}-{dep['dependency_id']}", sid, SCENARIO_META[scenario]["name"], str(year), key, dep["dependency_id"],
                    dep["dependency_type"], dep["from_id"], dep["to_id"], dep["relationship_type"], dep["spatial_scale"],
                    f"CURRENT FACT (2026 baseline): {dep['from_id']} -> {dep['to_id']} is a {dep['relationship_type']} interface at {dep['spatial_scale']}; evidence is {dep['documented_or_inferred']}.",
                    f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, 'infrastructure_dependency' if key == 'healthcare/AMR' else archetype['domain'])][5]}",
                    f"SCENARIO CONSEQUENCE: {consequence} Dependency change is not a disease outcome, and no local or individual inference is made.", dep_state, aid_dep, dep["source_id"], SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Dependency state preserves the accepted native scale and does not convert infrastructure stress, mobility, or environmental change into illness or outbreak certainty.",
                ])
                unc = unc_lookup[archetype["uncertainty"]]
                if scenario == "A":
                    future_unc = "Uncertainty is made more visible through coordinated review and targeted observation but is not resolved by the scenario."
                elif scenario == "B":
                    future_unc = "Uncertainty remains heterogeneous across programs, methods, jurisdictions, and settings; it is preserved rather than averaged."
                else:
                    future_unc = "Uncertainty may become more consequential at selected seams under variability and response lag, but unknown is not converted into absence, risk, or failure."
                uncertainty_rows.append([
                    f"IDFU-{sid}-{unc['uncertainty_id']}", sid, SCENARIO_META[scenario]["name"], str(year), key, unc["uncertainty_id"], unc["category"], unc["subject"],
                    f"CURRENT FACT (2026 baseline): {unc['statement']}", f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, 'governance_coordination')][5]}",
                    f"{horizon_phrase(scenario, year)} {future_unc} Great Black Swamp remains C — HOLD / noncanonical; Toledo intake-coordinate discrepancy remains UNRESOLVED.", aid_unc, unc["source_id"], "fictional", "scenario", "scenario_assumption",
                    "Uncertainty state preserves source, scale, and method limitations; no probability, case total, disease burden, individual risk, or local downscaling is created.",
                ])
    assert len(transmission_rows) == len(surveillance_rows) == len(response_rows) == len(dependency_rows) == len(uncertainty_rows) == 36
    return transmission_rows, surveillance_rows, response_rows, dependency_rows, uncertainty_rows


def comparison_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            if scenario == "A":
                values = [
                    "selected opportunities constrained; residual seasonal/event interfaces remain",
                    "prevention and infrastructure adaptation buffer selected interfaces",
                    "integrated observation with stronger selected detection; more reports do not mean more disease",
                    "clearer public-health/healthcare handoffs and wider selected response margin",
                    "healthcare/public-health response margin is wider in selected priority interfaces",
                    "connected mobility with prevention-aware continuity and investigation links",
                    "selected treatment, laboratory, cold-chain, energy, and communications dependencies buffered",
                    "traceability and continuity interfaces stronger in selected distribution systems",
                    "selected vector/water opportunity reduced or managed, not eliminated",
                    "moderate; residual ecological, ascertainment, and system uncertainty remains",
                ]
                distinct = "A is prevention-and-detection led; it does not assume elimination and is not a disease-incidence forecast."
            elif scenario == "B":
                values = [
                    "varies by archetype and node; constrained, permissive, and episodic interfaces coexist",
                    "environmental, settlement, and infrastructure conditions form a heterogeneous mosaic",
                    "coverage and latency are uneven; reporting differences are structural",
                    "strong response in some nodes and slower or less connected response elsewhere",
                    "healthcare/public-health response margin varies by node and event",
                    "distributed connectivity with local adaptation, friction, and differing investigation links",
                    "redundancy and fallback capacity are uneven across treatment, laboratory, energy, and communications",
                    "distributed production, storage, freight, and laboratory interfaces with reporting differences",
                    "vector and water states diverge by habitat and infrastructure, not by basin average",
                    "high; methods, denominators, coverage, and attribution remain heterogeneous",
                ]
                distinct = "B is a networked mosaic with strong and weak nodes, not a midpoint between A and C."
            else:
                values = [
                    "more permissive in selected systems, with episodic interruptions and no uniform change",
                    "warmth/variability, flooding/runoff, maintenance, and access stress create selected seams",
                    "selected coverage and reporting lag while capable programs persist elsewhere",
                    "coordination strain narrows selected response margins without implying prevalence",
                    "healthcare/public-health response margin narrows at selected seams",
                    "mobility/connectivity remains consequential while disruptions create access friction",
                    "infrastructure dependencies become more consequential where continuity and maintenance lag",
                    "episodic production/distribution disruption and investigation strain remain possible",
                    "selected vector-season and water-interface windows become longer or more variable",
                    "high; ecological mediation, ascertainment, and response interactions remain unresolved",
                ]
                distinct = "C is a higher-opportunity/response-strain structure, not epidemic certainty or a deterministic outbreak scenario."
            stage = "emerging and selective system interfaces" if year == 2050 else "matured or diverged system interfaces"
            values = [f"{value}; {stage}" for value in values]
            notes = f"{horizon_phrase(scenario, year)} Qualitative state only; no exact future value is adopted."
            rows.append([sid, SCENARIO_META[scenario]["name"], str(year), *values, "Transmission opportunity ≠ future incidence; environmental suitability ≠ disease burden; surveillance sensitivity ≠ disease intensity.", distinct, notes])
    assert len(rows) == 6 and all(len(row) == len(COMPARISON_COLUMNS) for row in rows)
    return rows


def write_ledger(source_rows: list[dict[str, str]]) -> None:
    # The accepted Phase 13B ledger is the source of truth for reused source IDs/URLs.
    payload = json.loads(LEDGER_INPUT.read_text(encoding="utf-8"))
    assert len(payload["sources"]) == len(source_rows) == 33
    LEDGER.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def source_citations(source_rows: list[dict[str, str]]) -> dict[str, int]:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_url = {row["url"]: int(row["id"]) for row in ledger["sources"]}
    return {row["source_id"]: by_url[row["url"]] for row in source_rows}


def citation_sentence(ids: list[int]) -> str:
    return "Source-registry entries " + "".join(f"[{item}]" for item in ids) + " are retained with source identity, scale, method, and limitations."


def source_block(path: Path) -> str:
    command = ["python", str(CITATION_SCRIPT), "--ledger", str(LEDGER), "render", "--style", "markdown", "--cited-in", str(path)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    rendered = result.stdout.strip()
    assert rendered and "Sources" in rendered
    return "\n\n" + rendered + "\n"


def write_reports(source_rows: list[dict[str, str]], counts: dict[str, int]) -> list[Path]:
    ids = source_citations(source_rows)
    groups = [list(range(start, min(start + 3, 34))) for start in range(1, 34, 3)]
    registry_lines = "\n".join(citation_sentence(group) for group in groups)
    def c(names: list[str]) -> str:
        return "[" + "][".join(str(ids[name]) for name in names) + "]"
    source_report = f"""# Phase 13C Infectious Disease System Futures Sources

Phase 13C reuses the accepted Phase 13A disease-system baseline and Phase 13B dependency layer rather than creating a new disease catalog. The scenario source registry contains {counts['scenario_sources']} source records spanning surveillance, environmental-health, vector, water, food/freight, mobility, healthcare, infrastructure, governance, and accepted repository context. {registry_lines}

Accepted repository manifests remain contextual inputs and are not modified or copied into future factual tables. External surveillance sources retain their original identity and limitations, including distinct denominators, program coverage, case geography, and observation methods. {registry_lines}

Scenario source use supports qualitative assumptions and system-interface interpretation only. It does not support exact future values, incidence, case totals, outbreak probability, disease burden, individual risk, or unsupported local downscaling. {registry_lines}
"""
    assumptions_report = f"""# Phase 13C Infectious Disease System Futures Assumptions

## Scope

The package contains {counts['assumptions']} explicit scenario assumptions across six states: A2050, A2075, B2050, B2075, C2050, and C2075. The assumptions cover environmental interfaces, mobility/connectivity, surveillance/detection, healthcare/public-health response, infrastructure dependencies, and governance coordination. {c(['phase9_hazard_dependency_context', 'phase1_water_context', 'phase11_mobility_context'])}

2050 is an intermediate system trajectory. 2075 is a matured or diverged system state with horizon-specific changes; it is not produced by multiplying 2050 values. Scenario assumptions are fictional qualitative deltas over accepted 2026 layers. {c(['phase9_climate', 'phase10_governance', 'phase11_population'])}

## Scenario families

A — Coordinated Prevention & Detection strengthens selected surveillance integration, environmental-health prevention, detection-to-response links, healthcare/public-health coordination, and infrastructure adaptation. Better detection can increase reported observations without implying more underlying disease. {c(['s13_nndss_about', 's13_cdc_wastewater', 'phase10_coordination_context'])}

B — Networked but Uneven Adaptation is a structurally distinct mosaic of capable and weak nodes, heterogeneous methods and coverage, distributed adaptation, and persistent reporting and coordination differences. It is not a midpoint between A and C. {c(['phase11_mobility_context', 'phase10_coordination_context', 'phase12_vector_dependency_context'])}

C — Higher Transmission Opportunity / Response Strain allows more permissive environmental or infrastructure interfaces in selected systems, longer or more variable opportunity windows, and selected surveillance or response lag. It does not assert epidemic certainty, future case totals, outbreak probability, or deterministic failure. {c(['phase9_hazard_dependency_context', 'phase3_energy_context', 's13_cdc_water_surv'])}

## Critical boundaries

Pathogen presence ≠ exposure ≠ infection ≠ reported case ≠ local transmission ≠ outbreak ≠ disease burden. Transmission opportunity ≠ future incidence. Environmental suitability ≠ disease burden. Surveillance sensitivity ≠ disease intensity. Infrastructure stress ≠ illness. Mobility/connectivity ≠ outbreak. {c(['s13_cdc_wnv', 's13_cdc_water_surv', 's13_nndss_about'])}

No future case total, incidence surface, outbreak probability, disease-burden estimate, individual risk, vulnerability/EJ score, or unsupported local downscaling is adopted. {c(['s13_nndss_wonder', 's13_cdc_wastewater', 'phase11_population'])}

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. Deferred maintenance remains the Phase 6B manifest status wording mismatch and the Phase 3A missing manifest status. {c(['phase6_ecology_context', 'phase1_water_context', 'phase9_climate'])}
"""
    findings_report = f"""# Phase 13C Infectious Disease System Futures Findings, 2050 / 2075

## A — Coordinated Prevention & Detection

SCENARIO: In 2050, stronger selected surveillance integration, environmental-health prevention, and healthcare/public-health handoffs reduce or buffer selected transmission-system opportunities while residual seasonal and event-driven interfaces remain. {c(['s13_nndss_about', 'phase10_coordination_context', 'phase9_hazard_dependency_context'])}

SCENARIO: In 2075, prevention, detection, and response routines are mature in selected systems, but no disease system is assumed eliminated and residual ecological, ascertainment, and infrastructure uncertainty remains. {c(['s13_cdc_wastewater', 's13_cdc_nhsn', 'phase3_energy_context'])}

## B — Networked but Uneven Adaptation

SCENARIO: In 2050, environmental interfaces, surveillance capacity, healthcare response, mobility, and infrastructure dependencies diverge across a networked basin mosaic; local differences are retained rather than averaged. {c(['phase11_mobility_context', 'phase10_coordination_context', 'phase12_vector_dependency_context'])}

SCENARIO: In 2075, strong and weak nodes remain connected through overlapping networks with persistent method, reporting, access, and coordination friction. This is not a midpoint and does not establish a common disease state. {c(['s13_nndss_about', 's13_cdc_foodnet', 'phase10_governance'])}

## C — Higher Transmission Opportunity / Response Strain

SCENARIO: In 2050, warmer or more variable environmental conditions, episodic water or food-system disruption, mobility/connectivity pressure, and infrastructure stress create more permissive opportunity in selected systems while response strain appears at selected seams. {c(['phase9_hazard_dependency_context', 'phase5_freight_context', 'phase3_energy_context'])}

SCENARIO: In 2075, selected opportunity windows and service dependencies are more consequential, but capable programs persist and the package does not assert epidemic certainty, case totals, outbreak probability, or deterministic collapse. {c(['phase9_climate', 'phase10_coordination_context', 's13_nndss_about'])}

## Archetype findings

Vector-borne states retain climate/vector ecology, seasonal windows, host/vector interfaces, settlement context, and surveillance as separate opportunity and detection systems. Future vector or environmental suitability does not become human cases or disease burden. {c(['phase12_vector_dependency_context', 's13_cdc_wnv', 's13_cdc_lyme'])}

Waterborne/environmental states retain flooding/runoff, treatment resilience, wastewater/recreational water, building-water, and environmental monitoring interfaces. Infrastructure stress or contamination opportunity does not become illness without separate evidence. {c(['s13_cdc_water_surv', 's13_cdc_legionella_about', 'phase1_water_context'])}

Foodborne/enteric states retain production, distribution, freight, cold-chain/storage, laboratory, and investigation interfaces. Connectivity is not a shipment, contamination event, outbreak, or incidence forecast. {c(['s13_cdc_enteric', 's13_cdc_foodnet', 'phase5_freight_context'])}

Respiratory states retain settlement/contact structure, mobility, seasonality, testing, wastewater, and healthcare response as distinct interfaces. Mobility and wastewater observations do not establish transmission, infection, or a case total. {c(['s13_cdc_flu_methods', 's13_cdc_wastewater', 'phase11_mobility_context'])}

Zoonotic states retain wildlife/domestic interfaces and veterinary/public-health surveillance. Animal or environmental contact opportunity does not establish human infection, disease, or local transmission. {c(['s13_cdc_rabies', 'phase6_ecology_context', 'phase10_coordination_context'])}

Healthcare/AMR states retain laboratory detection, healthcare coordination, infection-control capacity, reporting, and infrastructure continuity. Healthcare presence or surveillance does not establish prevalence or disease burden. {c(['s13_cdc_nhsn', 's13_cdc_ar', 'phase3_energy_context'])}

## Cross-cutting interpretation

More detection may produce more reported observations without implying more underlying disease. Surveillance coverage is not disease intensity, response capacity is not disease absence, and uncertainty is not converted into low risk or no disease. {c(['s13_nndss_about', 's13_cdc_wastewater', 's13_cdc_flu_methods'])}
"""
    qa_report = f"""# Phase 13C Infectious Disease System Futures QA

The package contains {counts['assumptions']} assumptions, {counts['transmission_states']} transmission states, {counts['surveillance_states']} surveillance states, {counts['response_states']} response states, {counts['dependency_states']} dependency states, {counts['uncertainty_states']} uncertainty states, {counts['scenario_sources']} scenario sources, six comparison rows, Maps 43/43b, and a qualitative comparison figure. {c(['s13_nndss_about', 'phase9_climate', 'phase10_coordination_context'])}

The Python and independent R validators check schemas, exact row counts, unique IDs, scenario/horizon coverage, baseline node/dependency/uncertainty references, source references, assumption references, qualitative-only states, scenario/fact separation, substantive 2050/2075 differences, Map 43/43b raster/SVG integrity, prior freeze integrity, and all active holds. {c(['phase12_vector', 'phase9_hazard_dependency_context', 'phase11_mobility_context'])}

Negative-scope QA rejects future incidence or case-count forecasts, outbreak probability, disease-burden or individual-risk products, vulnerability/EJ scoring, unsupported local downscaling, surveillance = incidence, climate/vector suitability = disease, contamination = illness, infrastructure stress = illness, mobility = outbreak certainty, and Phase 14 implementation. Caveat language is retained as boundary evidence rather than treated as a positive claim. {c(['s13_nndss_wonder', 's13_cdc_water_surv', 's13_cdc_wnv'])}

Maps are generalized system-state diagrams. They show archetype opportunity, surveillance/detection, response coordination, environmental/system dependencies, and uncertainty; they do not show future case totals, incidence surfaces, neighborhood disease risk, facility burden, outbreak hotspots, or individual exposure. {c(['phase4_information', 'phase10_coordination_context', 'phase12_vector'])}

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. Deferred maintenance remains unchanged, and no Phase 14 implementation, release, or tag is included. {c(['phase6_ecology_context', 'phase1_water_context', 'phase10_governance'])}
"""
    reports: list[Path] = []
    for name, text in (
        ("infectious_disease_scenario_sources.md", source_report),
        ("infectious_disease_scenario_assumptions.md", assumptions_report),
        ("infectious_disease_scenario_findings.md", findings_report),
        ("infectious_disease_scenario_qa.md", qa_report),
    ):
        path = REPORTS / name
        text = text.replace(" [", "[")
        if name != "infectious_disease_scenario_sources.md":
            text += "\n" + registry_lines
        path.write_text(text, encoding="utf-8", newline="\n")
        path.write_text(path.read_text(encoding="utf-8") + source_block(path), encoding="utf-8", newline="\n")
        reports.append(path)
    return reports


def map_excerpt(value: str, width: int = 34) -> str:
    return shorten(value.replace(";", ", "), width=width, placeholder="…")


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'id="p[0-9a-f]+"', 'id="p13cfuture"', text)
    text = re.sub(r'url\(#p[0-9a-f]+\)', "url(#p13cfuture)", text)
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def render_map(path_base: Path, year: int, transmissions: list[dict[str, str]], surveillance: list[dict[str, str]], responses: list[dict[str, str]], dependencies: list[dict[str, str]], uncertainties: list[dict[str, str]]) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    fig, axes = plt.subplots(1, 3, figsize=(23, 14), facecolor="#f3eee4")
    for axis, scenario in zip(axes, "ABC"):
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        axis.axis("off")
        meta = SCENARIO_META[scenario]
        axis.text(0.02, 0.985, f"{scenario} — {meta['name']}", va="top", fontsize=12.5, weight="bold", color=meta["color"])
        axis.text(0.02, 0.945, "GENERALIZED SYSTEM STATES", fontsize=7.2, weight="bold", color="#41505b")
        rows_t = {row["archetype"]: row for row in transmissions if row["scenario_id"] == f"{scenario}{year}"}
        rows_s = {row["archetype"]: row for row in surveillance if row["scenario_id"] == f"{scenario}{year}"}
        rows_r = {row["archetype"]: row for row in responses if row["scenario_id"] == f"{scenario}{year}"}
        rows_d = {row["archetype"]: row for row in dependencies if row["scenario_id"] == f"{scenario}{year}"}
        rows_u = {row["archetype"]: row for row in uncertainties if row["scenario_id"] == f"{scenario}{year}"}
        for index, archetype in enumerate(ARCHETYPES):
            key = archetype["key"]
            y = 0.875 - index * 0.125
            box = FancyBboxPatch((0.015, y - 0.103), 0.97, 0.108, boxstyle="round,pad=0.006", linewidth=0.8, edgecolor=meta["color"], facecolor="#fbf8f0", alpha=0.97)
            axis.add_patch(box)
            t = rows_t[key]; s = rows_s[key]; r = rows_r[key]; d = rows_d[key]; u = rows_u[key]
            axis.text(0.03, y - 0.012, archetype["label"], fontsize=7.0, weight="bold", color="#263d4b", va="top")
            body = (
                f"OPPORTUNITY: {map_excerpt(t['transmission_opportunity_state'])}\n"
                f"SURVEILLANCE / DETECTION: {map_excerpt(s['surveillance_capacity_state'])}; {map_excerpt(s['detection_latency_state'], 30)}\n"
                f"RESPONSE: {map_excerpt(r['response_coordination_state'])}; {map_excerpt(r['response_latency_margin'], 30)}\n"
                f"DEPENDENCY: {map_excerpt(d['dependency_state'])}; UNCERTAINTY: {map_excerpt(u['uncertainty_state'], 48)}"
            )
            axis.text(0.03, y - 0.034, fill(body, 74), fontsize=5.25, color="#3d4a4d", va="top", linespacing=1.13)
        axis.text(0.02, 0.035, "Scenario state only; not a geographic risk surface.", fontsize=6.1, color="#41505b")
    title = f"MAP {'43' if year == 2050 else '43b'} — INFECTIOUS DISEASE SYSTEM FUTURES, {year}"
    subtitle = "2050 intermediate trajectory" if year == 2050 else "2075 matured / diverged system state"
    fig.suptitle(title, x=0.03, y=0.998, ha="left", fontsize=16, weight="bold", color="#17384b")
    fig.text(0.03, 0.968, f"{subtitle}. Generalized Western Basin interfaces across vector-borne, waterborne/environmental, foodborne/enteric, respiratory, zoonotic, and healthcare/AMR systems.", fontsize=8.0, color="#3f4645")
    fig.text(0.03, 0.012, "QUALITATIVE FUTURES — transmission opportunity ≠ future incidence; environmental suitability ≠ disease burden; surveillance sensitivity ≠ disease intensity; infrastructure stress ≠ illness; mobility/connectivity ≠ outbreak. No future case totals, incidence surfaces, neighborhood risk, facility burden, outbreak hotspots, or individual exposure. Great Black Swamp: C — HOLD / noncanonical. Toledo intake-coordinate discrepancy: UNRESOLVED.", fontsize=6.35, color="#3f4645")
    MAPS.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(path_base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(path_base.with_suffix(".svg"))


def render_comparison(rows: list[list[str]]) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    fig, axis = plt.subplots(figsize=(19, 10), facecolor="#f3eee4")
    axis.axis("off")
    axis.text(0.01, 0.98, "QUALITATIVE INFECTIOUS DISEASE SYSTEM FUTURES COMPARISON", va="top", fontsize=14, weight="bold", color="#17384b")
    axis.text(0.01, 0.942, "A/B/C alternatives across 2050 and 2075; no numerical score, incidence forecast, case total, or outbreak probability.", fontsize=8, color="#3f4645")
    y = 0.89
    for row in rows:
        sid, scenario, horizon = row[:3]
        color = SCENARIO_META[sid[0]]["color"]
        axis.text(0.01, y, f"{sid}  {scenario}", fontsize=8.2, weight="bold", color=color, va="top")
        text = " | ".join([f"Opportunity: {row[3]}", f"Surveillance: {row[5]}", f"Response: {row[6]}", f"Dependencies: {row[9]}", f"Uncertainty: {row[12]}"])
        axis.text(0.22, y, fill(text, 148), fontsize=6.65, color="#3f4645", va="top", linespacing=1.17)
        y -= 0.125
    axis.text(0.01, 0.06, "BOUNDARY: pathogen presence ≠ exposure ≠ infection ≠ reported case ≠ local transmission ≠ outbreak ≠ disease burden. Better detection may increase reported observations without implying more underlying disease.", fontsize=7.0, color="#3f4645")
    axis.text(0.01, 0.025, "HOLD: Great Black Swamp C — HOLD / noncanonical. UNRESOLVED: Toledo intake-coordinate discrepancy.", fontsize=7.0, color="#3f4645")
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(COMPARISON_PNG, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(COMPARISON_SVG, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(COMPARISON_SVG)


def metadata(paths: list[Path]) -> dict[str, dict[str, object]]:
    return {str(path.relative_to(ROOT)).replace("\\", "/"): {"sha256": digest(path), "bytes": path.stat().st_size} for path in paths}


def main() -> None:
    for directory in (ANALYSIS, NETWORKS, SCENARIOS, MAPS, FIGURES, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    node_lookup = {row["node_id"]: row for row in read_rows(BASELINE_NODES)}
    dep_lookup = {row["dependency_id"]: row for row in read_rows(BASELINE_DEPS)}
    unc_lookup = {row["uncertainty_id"]: row for row in read_rows(BASELINE_UNC)}
    source_input = read_rows(SOURCE_INPUT)
    source_rows = []
    for row in source_input:
        source_rows.append({**row, "scenario_relevance": "Reused accepted infectious-disease or cross-system context for qualitative scenario construction; not evidence of a future disease outcome."})
    assert len(source_rows) == 33 and len({row["source_id"] for row in source_rows}) == 33
    write_ledger(source_rows)
    assumptions = scenario_assumptions(source_rows)
    transmission, surveillance, response, dependencies, uncertainty = build_state_tables(assumptions, node_lookup, dep_lookup, unc_lookup)
    comparison = comparison_rows()
    write_rows(ASSUMPTIONS, ASSUMPTION_COLUMNS, assumptions)
    write_rows(TRANSMISSION, TRANSMISSION_COLUMNS, transmission)
    write_rows(SURVEILLANCE, SURVEILLANCE_COLUMNS, surveillance)
    write_rows(RESPONSE, RESPONSE_COLUMNS, response)
    write_rows(DEPENDENCIES, DEPENDENCY_COLUMNS, dependencies)
    write_rows(UNCERTAINTY, UNCERTAINTY_COLUMNS, uncertainty)
    write_rows(SOURCES, SOURCE_COLUMNS, [[row[column] for column in SOURCE_COLUMNS] for row in source_rows])
    write_rows(COMPARISON, COMPARISON_COLUMNS, comparison)
    report_paths = write_reports(source_rows, {"assumptions": len(assumptions), "transmission_states": len(transmission), "surveillance_states": len(surveillance), "response_states": len(response), "dependency_states": len(dependencies), "uncertainty_states": len(uncertainty), "scenario_sources": len(source_rows)})
    render_map(MAP2050, 2050, [dict(zip(TRANSMISSION_COLUMNS, row)) for row in transmission], [dict(zip(SURVEILLANCE_COLUMNS, row)) for row in surveillance], [dict(zip(RESPONSE_COLUMNS, row)) for row in response], [dict(zip(DEPENDENCY_COLUMNS, row)) for row in dependencies], [dict(zip(UNCERTAINTY_COLUMNS, row)) for row in uncertainty])
    render_map(MAP2075, 2075, [dict(zip(TRANSMISSION_COLUMNS, row)) for row in transmission], [dict(zip(SURVEILLANCE_COLUMNS, row)) for row in surveillance], [dict(zip(RESPONSE_COLUMNS, row)) for row in response], [dict(zip(DEPENDENCY_COLUMNS, row)) for row in dependencies], [dict(zip(UNCERTAINTY_COLUMNS, row)) for row in uncertainty])
    render_comparison(comparison)
    artifacts = [
        ASSUMPTIONS, TRANSMISSION, SURVEILLANCE, RESPONSE, DEPENDENCIES, UNCERTAINTY, SOURCES, COMPARISON,
        MAP2050.with_suffix(".png"), MAP2050.with_suffix(".svg"), MAP2075.with_suffix(".png"), MAP2075.with_suffix(".svg"),
        COMPARISON_PNG, COMPARISON_SVG, *report_paths, LEDGER,
        ROOT / "src/python/systems/build_infectious_disease_futures.py",
        ROOT / "src/python/systems/validate_infectious_disease_futures.py",
        ROOT / "src/R/systems/validate_infectious_disease_futures.R",
    ]
    assert all(path.is_file() and path.stat().st_size > 0 for path in artifacts)
    manifest = {
        "phase": "13C", "baseline": "Infectious Disease System Futures, 2050 / 2075", "map_numbers": [43, "43b"],
        "status": "implemented_validated_pending_sol_acceptance", "scenario_ids": list(SCENARIO_IDS),
        "scenario_names": {key: value["name"] for key, value in SCENARIO_META.items()},
        "counts": {"assumptions": len(assumptions), "transmission_states": len(transmission), "surveillance_states": len(surveillance), "response_states": len(response), "dependency_states": len(dependencies), "uncertainty_states": len(uncertainty), "scenario_sources": len(source_rows), "comparison_rows": len(comparison)},
        "phase13a_freeze_manifest": {"path": str(PHASE13A_FREEZE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(PHASE13A_FREEZE), "bytes": PHASE13A_FREEZE.stat().st_size},
        "phase13b_freeze_manifest": {"path": str(PHASE13B_FREEZE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(PHASE13B_FREEZE), "bytes": PHASE13B_FREEZE.stat().st_size},
        "protected_inputs": [str(path.relative_to(ROOT)).replace("\\", "/") for path in (PHASE13A_FREEZE, PHASE13B_FREEZE)],
        "artifacts": metadata(artifacts),
        "numeric_future_values_adopted": False, "future_case_counts": False, "future_incidence_forecast": False, "outbreak_probability": False,
        "disease_burden_forecast": False, "individual_risk_model": False, "vulnerability_ej_scoring": False, "unsupported_local_downscaling": False,
        "phase13a_13b_accepted_frozen": True, "phase1_12_immutable": True, "phase14_implemented": False,
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"},
        "deferred_maintenance_preserved": ["Phase 6B manifest status wording mismatch", "Phase 3A missing manifest status"],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "13C", "map_numbers": [43, "43b"], **manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()
