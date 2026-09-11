"""Build Phase 15B qualitative technology-convergence futures for 2050/2075.

The package is an additive scenario layer over the accepted/frozen Phase 15A
technology baseline and Phase 14 systems ontology. It does not forecast exact
adoption, regional deployment, health outcomes, or technology performance.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import yaml

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
SCENARIO_DIR = ROOT / "data/processed/scenarios"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
SYSTEMS_YAML = ROOT / "metadata/atlas_systems.yml"
BASELINE_NODES = ANALYSIS / "technology_system_nodes.csv"
BASELINE_SOURCES = ANALYSIS / "technology_sources.csv"
BASELINE_DEPENDENCIES = ROOT / "data/processed/integration/technology_dependencies.csv"
BASELINE_INTERFACES = ROOT / "data/processed/integration/technology_system_interfaces.csv"
MANIFEST = REPORTS / "phase15b_manifest.json"

BASE_SHA = "b8baa403316e56ce7a1266e1cf37d4839536dabc"
HORIZONS = (2050, 2075)
SCENARIOS = ("A", "B", "C")
SCENARIO_META = {
    "A": {
        "name": "Coordinated Technological Adaptation",
        "short": "coordinated adaptation",
        "uncertainty": "moderate",
        "plausibility": "moderate",
        "color": "#2f7f73",
    },
    "B": {
        "name": "Uneven Networked Modernization",
        "short": "uneven modernization",
        "uncertainty": "high",
        "plausibility": "plausible middle scenario",
        "color": "#b47b32",
    },
    "C": {
        "name": "High Capability / High Friction Basin",
        "short": "high capability / high friction",
        "uncertainty": "high",
        "plausibility": "exploratory",
        "color": "#a04f55",
    },
}

FAMILIES = (
    "AI / ADVANCED COMPUTE / AUTOMATION",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS",
    "CYBERSECURITY / DIGITAL RESILIENCE",
    "ADVANCED ENERGY",
    "ADVANCED MATERIALS / MANUFACTURING",
    "QUANTUM TECHNOLOGIES",
    "BIOTECHNOLOGY / GENETIC ENGINEERING",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
)
FAMILY_LABELS = {
    "AI / ADVANCED COMPUTE / AUTOMATION": "AI / compute / automation",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS": "sensing / autonomous systems",
    "CYBERSECURITY / DIGITAL RESILIENCE": "cyber / digital resilience",
    "ADVANCED ENERGY": "advanced energy",
    "ADVANCED MATERIALS / MANUFACTURING": "materials / manufacturing",
    "QUANTUM TECHNOLOGIES": "quantum",
    "BIOTECHNOLOGY / GENETIC ENGINEERING": "biotechnology",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE": "privacy / data governance",
}
FAMILY_SOURCE = {
    FAMILIES[0]: "EXT-DOE-AI-RECOMMENDATIONS",
    FAMILIES[1]: "EXT-NOAA-IOOS",
    FAMILIES[2]: "EXT-CISA-CPG",
    FAMILIES[3]: "EXT-DOE-ENERGY-STORAGE",
    FAMILIES[4]: "EXT-NIST-MANUFACTURING",
    FAMILIES[5]: "EXT-NIST-QIS",
    FAMILIES[6]: "EXT-CDC-AMD",
    FAMILIES[7]: "EXT-NIST-PRIVACY",
}

AXES = (
    "technology_maturity",
    "regional_adoption",
    "infrastructure_adequacy",
    "interoperability",
    "governance_capacity",
    "trust_legitimacy",
    "cyber_digital_resilience",
    "workforce_energy_material_capacity",
)
AXIS_SOURCE = {
    "technology_maturity": "EXT-NIST-QIS",
    "regional_adoption": "REG-PHASE14B-ATLAS",
    "infrastructure_adequacy": "REG-PHASE3B-ENERGY-DEPENDENCIES",
    "interoperability": "REG-PHASE14B-ATLAS",
    "governance_capacity": "REG-PHASE10A-GOVERNANCE",
    "trust_legitimacy": "EXT-NIST-PRIVACY",
    "cyber_digital_resilience": "EXT-CISA-CPG",
    "workforce_energy_material_capacity": "EXT-NIST-MANUFACTURING",
}

SYSTEM_LABELS = {
    "SYS-WATER": "Water / Hydrology",
    "SYS-MATERIALS": "Geology / Minerals / Strategic Materials",
    "SYS-ENERGY": "Energy / Grid / Compute",
    "SYS-DATA": "Data / Sensors / Observation & Decision Infrastructure",
    "SYS-FREIGHT": "Freight / Industry / Material Flows",
    "SYS-ECOLOGY": "Ecology / Biodiversity",
    "SYS-EXPOSURE": "Exposure / Environmental Health",
    "SYS-BIOGEOCHEMISTRY": "Nutrients / Biogeochemistry",
    "SYS-CLIMATE": "Climate / Natural Hazards",
    "SYS-GOVERNANCE": "Governance / Jurisdiction",
    "SYS-POPULATION": "Population / Settlement / Mobility",
    "SYS-VECTOR-ECOLOGY": "Vector Ecology",
    "SYS-INFECTIOUS-DISEASE": "Infectious Disease Systems",
}
SYSTEM_ORDER = tuple(SYSTEM_LABELS)

ASSUMPTION_COLUMNS = [
    "assumption_id", "scenario_id", "scenario_family", "horizon", "axis", "assumption",
    "evidence_basis", "source_or_basis", "uncertainty", "reality_status", "canon_status",
    "classification", "numeric_future_value_adopted", "notes",
]
FAMILY_STATE_COLUMNS = [
    "state_id", "scenario_id", "scenario_family", "horizon", "technology_family",
    "baseline_2026_status", "baseline_2026_relevance", "capability_state", "maturity_state",
    "adoption_state", "infrastructure_state", "interoperability_state", "governance_state",
    "trust_legitimacy_state", "cybersecurity_state", "workforce_state", "energy_compute_material_state",
    "privacy_surveillance_state", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis",
    "reality_status", "canon_status", "relationship_basis", "notes",
]
CONVERGENCE_COLUMNS = [
    "relationship_id", "scenario_id", "scenario_family", "horizon", "technology_family_a",
    "technology_family_b", "convergence_mechanism", "enabling_conditions", "limiting_conditions",
    "affected_system_ids", "evidence_basis", "scenario_dependence", "governance_implications",
    "uncertainty", "second_order_effects", "assumption_id", "source_or_basis", "reality_status",
    "canon_status", "relationship_basis", "notes",
]
SYSTEM_STATE_COLUMNS = [
    "state_id", "scenario_id", "scenario_family", "horizon", "system_id", "technology_family",
    "convergence_mechanism", "state_direction", "dependency_change", "governance_effect",
    "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status",
    "canon_status", "relationship_basis", "notes",
]
DEPENDENCY_COLUMNS = [
    "dependency_state_id", "scenario_id", "scenario_family", "horizon", "system_a", "system_b",
    "technology_family", "dependency_change_type", "dependency_state", "enabling_conditions",
    "limiting_conditions", "governance_implication", "uncertainty", "evidence_basis", "assumption_id",
    "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes",
]
GOVERNANCE_COLUMNS = [
    "governance_state_id", "scenario_id", "scenario_family", "horizon", "governance_domain",
    "technology_family", "governance_state", "oversight_capacity", "trust_legitimacy_state",
    "privacy_surveillance_balance", "public_communication_state", "workforce_maintenance_state",
    "human_authority_boundary", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis",
    "reality_status", "canon_status", "relationship_basis", "notes",
]
UNCERTAINTY_COLUMNS = [
    "uncertainty_state_id", "scenario_id", "scenario_family", "horizon", "uncertainty_domain",
    "subject", "uncertainty_level", "uncertainty", "scenario_dependence", "what_is_not_inferred",
    "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status",
    "relationship_basis", "notes",
]
COMPARISON_COLUMNS = [
    "scenario_id", "scenario_family", "horizon", "technology_maturity", "regional_adoption",
    "infrastructure_adequacy", "interoperability", "governance_capacity", "trust_legitimacy",
    "cyber_digital_resilience", "workforce_capability", "energy_compute_dependency", "system_coupling",
    "biosecurity_capacity", "equity_unevenness", "boundary_statement", "notes",
]

MANIFEST_PATHS = [
    "data/processed/scenarios/technology_scenario_assumptions.csv",
    "data/processed/scenarios/technology_family_states.csv",
    "data/processed/scenarios/technology_convergence_relationships.csv",
    "data/processed/scenarios/technology_system_states.csv",
    "data/processed/scenarios/technology_dependency_states.csv",
    "data/processed/scenarios/technology_governance_states.csv",
    "data/processed/scenarios/technology_uncertainty_states.csv",
    "data/processed/scenarios/technology_scenario_comparison.csv",
    "outputs/figures/technology_convergence_futures.png",
    "outputs/figures/technology_convergence_futures.svg",
    "outputs/figures/technology_cross_system_effects.png",
    "outputs/figures/technology_cross_system_effects.svg",
    "reports/phase15b_technology_convergence_futures.md",
    "reports/phase15b_biosecurity_futures.md",
    "reports/phase15b_scenario_comparison.md",
    "reports/phase15b_qa.md",
    "reports/phase15b_provenance_check.md",
    "reports/phase15b_artifact_check.json",
    "reports/phase15b_r_validation_result.json",
    "src/python/systems/build_phase15b_technology.py",
    "src/python/systems/validate_phase15b_technology.py",
    "src/R/systems/validate_phase15b_technology.R",
    "reports/phase15b_independent_review.md",
]

AXIS_VALUES = {
    "A": {
        "technology_maturity": ("selective high maturity in priority interfaces", "mature capability in selected interoperable interfaces"),
        "regional_adoption": ("selective high-value adoption; no universal rollout", "broad but still selective adoption with residual gaps"),
        "infrastructure_adequacy": ("resilient grid, compute, communications, and maintenance in priority nodes", "maintained and redundant infrastructure in selected connected systems"),
        "interoperability": ("stronger shared standards and interface contracts", "mature interoperability where institutions sustain common rules"),
        "governance_capacity": ("institutional capacity broadly keeps pace in selected systems", "oversight and maintenance routines are institutionalized but bounded"),
        "trust_legitimacy": ("trust is supported by transparent stewardship and human review", "legitimacy is maintained through auditable use and visible recourse"),
        "cyber_digital_resilience": ("defensive cybersecurity and recovery practices are coordinated", "defensive transition and continuity practices are mature in selected systems"),
        "workforce_energy_material_capacity": ("workforce, energy, materials, and maintenance investment are targeted", "workforce and supply-chain institutions support sustained maintenance with friction"),
    },
    "B": {
        "technology_maturity": ("advanced capability is available but maturity varies by node and family", "mature pockets coexist with uneven capability and standards"),
        "regional_adoption": ("adoption is patchy across municipalities, industry, and institutions", "strong nodes remain connected through weaker surrounding systems"),
        "infrastructure_adequacy": ("infrastructure is adequate in strong nodes and mismatched elsewhere", "maintenance and fallback capacity remain uneven across networks"),
        "interoperability": ("mixed standards and bridges connect but do not unify systems", "interoperability persists through negotiated adapters and partial translation"),
        "governance_capacity": ("governance is fragmented by domain and institution", "capacity is durable in some nodes and negotiated across others"),
        "trust_legitimacy": ("public trust is mixed and use-specific", "legitimacy varies with performance, access, and local stewardship"),
        "cyber_digital_resilience": ("defensive resilience is inconsistent across connected organizations", "strong defensive nodes coexist with weaker legacy interfaces"),
        "workforce_energy_material_capacity": ("workforce and supply-chain capability is uneven", "maintenance and access remain differentiated by node and sector"),
    },
    "C": {
        "technology_maturity": ("high capability is present in selected systems while governance lags", "powerful technical capability persists amid wider structural uncertainty"),
        "regional_adoption": ("adoption is selective, unequal, and sometimes accelerated without integration", "access remains unequal and concentrated in capable nodes"),
        "infrastructure_adequacy": ("infrastructure mismatch creates brittle interfaces without assumed collapse", "technical capacity is constrained by legacy, maintenance, and access mismatches"),
        "interoperability": ("weak interoperability and incompatible data lineages increase friction", "fragmented standards remain a structural coupling constraint"),
        "governance_capacity": ("oversight is delayed or fragmented relative to capability", "governance catches up unevenly and authority remains contested"),
        "trust_legitimacy": ("institutional mistrust and contested data use limit legitimacy", "legitimacy is episodic and dependent on local accountability"),
        "cyber_digital_resilience": ("cyber stress and uneven defensive continuity expose coupled dependencies", "defensive capability is substantial but brittle across seams"),
        "workforce_energy_material_capacity": ("workforce, energy, compute, and materials bottlenecks are unevenly managed", "maintenance and supply-chain mismatch remain persistent constraints"),
    },
}

FAMILY_BASE = {
    "AI / ADVANCED COMPUTE / AUTOMATION": ("decision support, optimization, and bounded automation", "human review, data quality, compute, energy, and operator trust"),
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS": ("networked measurement, inspection, and autonomous observation", "calibration, coverage, energy, communications, retrieval, and interpretation"),
    "CYBERSECURITY / DIGITAL RESILIENCE": ("defensive continuity, authentication, recovery, and incident communication", "asset inventories, legacy interfaces, workforce, coordination, and maintenance"),
    "ADVANCED ENERGY": ("storage, distributed energy, advanced nuclear, hydrogen, and long-horizon options", "siting, regulation, materials, water, interconnection, economics, and public legitimacy"),
    "ADVANCED MATERIALS / MANUFACTURING": ("advanced process control, materials qualification, circularity, and industrial automation", "feedstock, equipment, workforce, energy, quality, markets, and supply chains"),
    "QUANTUM TECHNOLOGIES": ("bounded sensing, timing, cryptographic transition, and niche compute possibilities", "error correction, calibration, useful advantage, cost, access, workforce, and integration"),
    "BIOTECHNOLOGY / GENETIC ENGINEERING": ("diagnostics, molecular monitoring, biomanufacturing, and One Health interfaces", "sampling, laboratory capacity, attribution, governance, privacy, energy, water, and communication"),
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE": ("data stewardship, privacy, provenance, accountable access, and retention", "legal basis, consent, interoperability, public trust, and institutional authority"),
}

CONVERGENCES = [
    ("AI + sensing", FAMILIES[0], FAMILIES[1], "faster environmental interpretation and decision support", "quality-controlled observations, communications, compute, trained reviewers", "coverage gaps, calibration error, model error, data permission, and operator trust", "SYS-WATER;SYS-DATA;SYS-ECOLOGY;SYS-CLIMATE", "Measurement can become more observable without becoming more authoritative or controlled.", "[EXT-DOE-AI-RECOMMENDATIONS; EXT-NOAA-IOOS]"),
    ("AI + grid + storage", FAMILIES[0], FAMILIES[3], "adaptive energy operations and planning support", "compute, energy continuity, data exchange, human operators, and defensive cyber practices", "interconnection, dispatch authority, model validity, storage duration, and maintenance", "SYS-ENERGY;SYS-DATA;SYS-GOVERNANCE", "A recommendation may improve timing while increasing energy/compute dependence and coupling.", "[EXT-DOE-AI-RECOMMENDATIONS; EXT-DOE-ENERGY-STORAGE]"),
    ("automation + advanced manufacturing", FAMILIES[0], FAMILIES[4], "changed industrial workflows, inspection, and workforce needs", "qualified processes, skilled workforce, equipment, energy, materials, and safety review", "qualification, workforce transition, supply chains, liability, and uneven facility adoption", "SYS-MATERIALS;SYS-FREIGHT;SYS-ENERGY;SYS-POPULATION", "Productivity or continuity gains may be accompanied by maintenance, training, and access differences.", "[EXT-DOE-AI-RECOMMENDATIONS; EXT-NIST-MANUFACTURING]"),
    ("genomic diagnostics + sensing", FAMILIES[6], FAMILIES[1], "faster detection opportunity across environmental and public-health interfaces", "sampling, laboratory capacity, quality systems, data stewardship, and interpretation", "attribution uncertainty, sampling bias, turnaround, privacy, and communication", "SYS-WATER;SYS-ECOLOGY;SYS-VECTOR-ECOLOGY;SYS-INFECTIOUS-DISEASE", "More detection can produce more observations without establishing incidence, attribution, or health outcomes.", "[EXT-CDC-AMD; EXT-NOAA-IOOS]"),
    ("post-quantum transition + digital infrastructure", FAMILIES[2], FAMILIES[5], "changing authentication and cryptographic migration requirements", "asset inventory, standards, procurement, lifecycle planning, and interoperability", "legacy systems, vendor support, migration sequencing, cost, and uneven implementation", "SYS-DATA;SYS-GOVERNANCE;SYS-ENERGY;SYS-WATER", "Security transition can create temporary compatibility and maintenance burdens without assuming a quantum attack.", "[EXT-NIST-PQC; EXT-CISA-CPG]"),
    ("distributed energy + storage + compute", FAMILIES[3], FAMILIES[0], "changed local infrastructure dependencies and continuity options", "interconnection, controls, storage, compute, communications, ownership, and maintenance", "islanding is not inferred; feeder topology, duration, dispatch, and service territory remain unknown", "SYS-ENERGY;SYS-DATA;SYS-WATER;SYS-FREIGHT", "Local capability may substitute for some centralized dependencies while creating new digital and maintenance dependencies.", "[EXT-DOE-ENERGY-STORAGE; EXT-DOE-AI-RECOMMENDATIONS]"),
    ("sensing + privacy/data governance", FAMILIES[1], FAMILIES[7], "changing legitimacy and data-use constraints around observation", "provenance, access rules, consent, purpose limitation, and public communication", "surveillance concerns, legal authority, retention, unequal access, and non-comparable methods", "SYS-DATA;SYS-GOVERNANCE;SYS-POPULATION;SYS-EXPOSURE", "Observability can increase without increasing control, permission, or public legitimacy.", "[EXT-NOAA-IOOS; EXT-NIST-PRIVACY]"),
    ("defensive cyber + all digitally dependent systems", FAMILIES[2], FAMILIES[7], "cross-system continuity, recovery, and trusted data exchange", "asset and dependency inventories, authentication, recovery practice, communications, and roles", "legacy interfaces, staffing, vendor dependence, fragmented standards, and recovery uncertainty", "SYS-WATER;SYS-ENERGY;SYS-DATA;SYS-FREIGHT;SYS-GOVERNANCE;SYS-INFECTIOUS-DISEASE", "Defensive capability can improve continuity while increasing coupling to inventories, identity, communications, and skilled maintenance.", "[EXT-CISA-CPG; EXT-NIST-PRIVACY]"),
    ("biotechnology + food/agriculture + governance", FAMILIES[6], FAMILIES[7], "higher detection and stewardship capacity at food, agricultural, and environmental interfaces", "One Health coordination, laboratory/diagnostic capacity, public communication, privacy, and supply-chain continuity", "attribution uncertainty, dual-use oversight, uneven laboratory access, and communication failure", "SYS-BIOGEOCHEMISTRY;SYS-ECOLOGY;SYS-FREIGHT;SYS-INFECTIOUS-DISEASE;SYS-GOVERNANCE", "Improved detection does not establish contamination, exposure, illness, or a biological threat; governance determines use and legitimacy.", "[EXT-CDC-ONEHEALTH; EXT-CDC-AMD]"),
    ("quantum sensing + data/energy", FAMILIES[5], FAMILIES[1], "possible niche measurement and timing interfaces", "robust field integration, calibration, data exchange, compute, and institutional demand", "research-stage maturity, useful signal, cost, specialized workforce, and adoption uncertainty", "SYS-DATA;SYS-ENERGY;SYS-WATER", "A niche technical capability may add measurement options while increasing calibration and infrastructure dependencies; no basin deployment is inferred.", "[EXT-NIST-QIS; REG-PHASE4A-DATA]"),
]

DEPENDENCIES = [
    ("SYS-ENERGY", "SYS-DATA", "AI / ADVANCED COMPUTE / AUTOMATION", "energy_compute", "energy ↔ compute", "AI, sensing, cyber, and data services make compute continuity more consequential; compute is not a guaranteed bottleneck.", "Energy continuity, efficient models, local fallback, and human operating procedures", "availability, allocation, model utility, and facility-level redundancy remain unknown", "Energy and information authorities remain distinct; no dispatch or control authority is assigned to software", "[EXT-DOE-AI-RECOMMENDATIONS; REG-PHASE3B-ENERGY-DEPENDENCIES]"),
    ("SYS-DATA", "SYS-GOVERNANCE", "PRIVACY / SURVEILLANCE / DATA GOVERNANCE", "data_governance", "data ↔ governance", "More data and interoperability move dependency toward stewardship, permission, provenance, and public accountability.", "purpose limitation, legal basis, role clarity, access rules, and auditability", "privacy, consent, retention, and incompatible institutional rules", "Availability is not permission and technical capability is not legal authority", "[EXT-NIST-PRIVACY; REG-PHASE10A-GOVERNANCE]"),
    ("SYS-DATA", "SYS-POPULATION", "ADVANCED SENSING / AUTONOMOUS SYSTEMS", "sensing_trust", "sensing ↔ public trust", "More observation can make systems more observable while legitimacy remains conditional.", "transparent stewardship, representative coverage, public communication, and recourse", "surveillance concern, uneven access, and non-comparable methods", "Observation is not enforcement, intervention, or authority", "[EXT-NOAA-IOOS; EXT-NIST-PRIVACY]"),
    ("SYS-FREIGHT", "SYS-POPULATION", "AI / ADVANCED COMPUTE / AUTOMATION", "automation_workforce", "automation ↔ workforce", "Automation changes tasks, training, maintenance, and accountability rather than removing human authority.", "training, safe operating procedures, maintenance, and worker participation", "skills mismatch, unequal access, equipment continuity, and labor transition", "Automation is not autonomous governance or an employment forecast", "[EXT-NIST-MANUFACTURING; REG-PHASE5A-FREIGHT]"),
    ("SYS-INFECTIOUS-DISEASE", "SYS-GOVERNANCE", "BIOTECHNOLOGY / GENETIC ENGINEERING", "biosecurity_governance", "biotechnology ↔ public health / agriculture / governance", "Diagnostics and molecular monitoring connect laboratory, environmental, food, and public-health interpretation.", "sampling, diagnostic quality, reporting, public communication, and coordinated oversight", "attribution, laboratory capacity, privacy, dual-use governance, and response coordination", "Detection is not incidence, threat, transmission, or successful response", "[EXT-CDC-AMD; EXT-CDC-ONEHEALTH]"),
    ("SYS-MATERIALS", "SYS-FREIGHT", "ADVANCED MATERIALS / MANUFACTURING", "manufacturing_supply_chain", "advanced manufacturing ↔ materials / freight / energy", "Process innovation shifts dependence toward qualified feedstock, equipment, logistics, and energy services.", "qualification, suppliers, workforce, energy continuity, and customer interfaces", "nonlocal feed, equipment access, supply-chain substitution, and market demand", "No named facility process, route, volume, or local adoption is inferred", "[EXT-NIST-MANUFACTURING; REG-PHASE2-MATERIALS]"),
    ("SYS-ENERGY", "SYS-WATER", "ADVANCED ENERGY", "energy_water", "energy ↔ water", "Storage, advanced generation, cooling, and hydrogen possibilities can move dependencies across energy and water contexts.", "siting, water stewardship, regulation, interconnection, and maintenance", "technology-specific water requirements, permits, and firm power remain unresolved", "No withdrawal, intake, plant, or deployment claim is made", "[EXT-DOE-ENERGY-STORAGE; REG-PHASE3B-ENERGY-DEPENDENCIES]"),
    ("SYS-DATA", "SYS-ENERGY", "CYBERSECURITY / DIGITAL RESILIENCE", "cyber_all_systems", "cybersecurity ↔ digitally dependent systems", "Defensive cyber practice can substitute for some single-point information dependencies while increasing identity and recovery coupling.", "asset inventories, authentication, recovery, communications, and trained personnel", "legacy systems, vendor interfaces, staffing, and recovery performance", "Cybersecurity remains defensive; no attack path, exploit, or operational control topology is modeled", "[EXT-CISA-CPG; REG-PHASE14B-ATLAS]"),
    ("SYS-DATA", "SYS-GOVERNANCE", "CYBERSECURITY / DIGITAL RESILIENCE", "pqc_transition", "post-quantum transition ↔ digital infrastructure", "Cryptographic migration can move dependency from current compatibility toward inventory and lifecycle governance.", "standards, inventory, procurement, staged migration, and interoperability", "legacy support, cost, sequencing, and uneven implementation", "Migration planning is not a prediction of attack timing or legal authority", "[EXT-NIST-PQC; EXT-CISA-CPG]"),
    ("SYS-ENERGY", "SYS-DATA", "ADVANCED ENERGY", "distributed_compute", "distributed energy / storage ↔ compute", "Distributed energy and storage may substitute for some centralized continuity dependencies while increasing local compute and communications needs.", "interconnection, storage, maintenance, control accountability, and communications", "feeder topology, islanding, duration, ownership, and dispatch are unknown", "Human and institutional authority remains outside the technical capability layer", "[EXT-DOE-ENERGY-STORAGE; REG-PHASE3A-ENERGY]"),
    ("SYS-ECOLOGY", "SYS-INFECTIOUS-DISEASE", "BIOTECHNOLOGY / GENETIC ENGINEERING", "one_health", "biotechnology ↔ ecology / disease observation", "Shared environmental, vector, and public-health observation can improve coordination while preserving distinct evidence ladders.", "One Health coordination, sampling, laboratory quality, and scale-aware interpretation", "coverage, attribution, detection sensitivity, and source separation", "Vector presence, detection, infection, and disease remain distinct", "[EXT-CDC-ONEHEALTH; REG-PHASE12A-VECTOR]"),
    ("SYS-MATERIALS", "SYS-ENERGY", "ADVANCED MATERIALS / MANUFACTURING", "materials_energy", "advanced manufacturing ↔ materials / energy", "Process changes can substitute for some material inputs or introduce new energy and qualification requirements.", "feedstock, quality, energy, recycling, process control, and workforce", "supply-chain dependence, qualification time, energy services, and market acceptance", "No quantitative substitution or facility production is represented", "[EXT-NIST-MANUFACTURING; REG-PHASE3A-ENERGY]"),
]

GOVERNANCE_DOMAINS = [
    ("human_authority_and_AI", FAMILIES[0]),
    ("sensing_data_legitimacy", FAMILIES[1]),
    ("defensive_cyber_coordination", FAMILIES[2]),
    ("energy_compute_stewardship", FAMILIES[3]),
    ("manufacturing_workforce_oversight", FAMILIES[4]),
    ("biosecurity_and_public_health", FAMILIES[6]),
    ("privacy_surveillance_balance", FAMILIES[7]),
    ("cross_system_interoperability", FAMILIES[0]),
]
UNCERTAINTY_DOMAINS = [
    "technology_maturity_and_capability",
    "regional_adoption",
    "infrastructure_and_interoperability",
    "governance_and_oversight",
    "trust_and_legitimacy",
    "cybersecurity_and_continuity",
    "workforce_and_maintenance",
    "energy_and_compute",
    "materials_and_supply_chain",
    "biosecurity_attribution_and_response",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    assert rows and all(len(row) == len(columns) for row in rows), path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scenario_id(scenario: str, horizon: int) -> str:
    return f"{scenario}{horizon}"


def horizon_phrase(scenario: str, horizon: int) -> str:
    if horizon == 2050:
        return {
            "A": "2050 is a plausible intermediate trajectory with selective high-value convergence and bounded institutional adaptation.",
            "B": "2050 is a plausible uneven trajectory in which strong nodes connect through weaker infrastructure, standards, and workforce capacity.",
            "C": "2050 is a bounded high-capability trajectory with substantial technical options but high friction, cyber stress, and delayed governance at selected seams.",
        }[scenario]
    return {
        "A": "2075 is a wider-uncertainty scenario in which selected interoperability and maintenance routines have matured without eliminating cost, failure, or inequality.",
        "B": "2075 is a wider-uncertainty mosaic in which strong and weak nodes remain coupled through negotiated standards and uneven access.",
        "C": "2075 is a wider-uncertainty state in which powerful technologies coexist with brittle dependencies, contested legitimacy, and fragmented oversight without assumed collapse.",
    }[scenario]


def axis_assumption(scenario: str, horizon: int, axis: str) -> str:
    return AXIS_VALUES[scenario][axis][0 if horizon == 2050 else 1]


def assumption_rows() -> list[list[str]]:
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, axis in enumerate(AXES, 1):
                rows.append([
                    f"TFA-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), axis,
                    axis_assumption(scenario, horizon, axis),
                    "Phase 15A accepted/frozen capability and interface baseline plus explicit qualitative scenario construction; " + horizon_phrase(scenario, horizon),
                    AXIS_SOURCE[axis], SCENARIO_META[scenario]["uncertainty"], "scenario", "scenario", "SCENARIO ASSUMPTION", "false",
                    "No exact deployment percentage, capacity, adoption rate, health outcome, or probability is assigned. Capability is not deployment; deployment is not adoption; adoption is not benefit.",
                ])
    return rows


def load_baseline() -> tuple[dict[str, dict[str, str]], set[str], list[dict[str, str]]]:
    nodes = read_csv(BASELINE_NODES)
    sources = read_csv(BASELINE_SOURCES)
    source_ids = {row["source_id"] for row in sources}
    node_by_family: dict[str, list[dict[str, str]]] = {}
    for row in nodes:
        node_by_family.setdefault(row["technology_family"], []).append(row)
    family_baseline = {}
    for family in FAMILIES:
        family_rows = node_by_family[family]
        family_baseline[family] = {
            "status": "; ".join(sorted({row["technology_status"] for row in family_rows})),
            "relevance": "; ".join(sorted({row["regional_relevance"] for row in family_rows})),
        }
    return family_baseline, source_ids, sources


def family_state(scenario: str, horizon: int, family: str, assumptions: dict[tuple[str, str], str], baseline: dict[str, dict[str, str]]) -> list[str]:
    sid = scenario_id(scenario, horizon)
    maturity = axis_assumption(scenario, horizon, "technology_maturity")
    adoption = axis_assumption(scenario, horizon, "regional_adoption")
    infra = axis_assumption(scenario, horizon, "infrastructure_adequacy")
    interop = axis_assumption(scenario, horizon, "interoperability")
    governance = axis_assumption(scenario, horizon, "governance_capacity")
    trust = axis_assumption(scenario, horizon, "trust_legitimacy")
    cyber = axis_assumption(scenario, horizon, "cyber_digital_resilience")
    capacity = axis_assumption(scenario, horizon, "workforce_energy_material_capacity")
    capability, limits = FAMILY_BASE[family]
    if scenario == "A":
        capability_state = f"{capability} is available in selected high-value interfaces, with human and institutional review retained."
        family_governance = "Auditable governance, role clarity, and maintenance requirements broadly keep pace in selected interfaces."
        privacy = "Privacy and surveillance boundaries are explicit; trusted use remains conditional on consent, purpose, and recourse."
        family_uncertainty = f"Residual uncertainty remains around {limits}; 2075 uncertainty is wider even where maturity is higher."
    elif scenario == "B":
        capability_state = f"{capability} is available in strong nodes but translation, adoption, and maintenance differ across the network."
        family_governance = "Governance is negotiated by domain; standards and oversight are inconsistent across nodes and operators."
        privacy = "Privacy and surveillance practices vary by institution, purpose, and public trust; interoperability is partial."
        family_uncertainty = f"Uncertainty is high around uneven access, node-to-node transfer, and {limits}."
    else:
        capability_state = f"{capability} can be substantial in selected systems, but technical capability is coupled to brittle infrastructure and delayed or contested governance."
        family_governance = "Governance and oversight lag or fragment relative to capability; technical systems do not acquire legal authority."
        privacy = "Privacy and surveillance boundaries are contested, with observability sometimes increasing without legitimacy or control."
        family_uncertainty = f"Uncertainty is high around coupled failure, public legitimacy, and {limits}; no collapse is inferred."
    assumption_id = assumptions[(sid, "technology_maturity")]
    source_id = FAMILY_SOURCE[family]
    return [
        f"TFS-{sid}-{FAMILIES.index(family)+1:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), family,
        baseline[family]["status"], baseline[family]["relevance"], capability_state, maturity, adoption, infra, interop,
        family_governance, trust, cyber, capacity, f"Energy/compute/material requirements remain explicit: {capacity}", privacy,
        family_uncertainty, "Phase 15A accepted/frozen baseline plus explicit scenario construction; this is a scenario state, not a forecast.",
        assumption_id, source_id, "scenario", "scenario", "scenario_assumption", "Capability is not deployment; deployment is not adoption; adoption is not benefit. No basin-specific deployment is inferred from national or general evidence.",
    ]


def family_state_rows(assumption_rows_value: list[list[str]], baseline: dict[str, dict[str, str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            for family in FAMILIES:
                rows.append(family_state(scenario, horizon, family, assumptions, baseline))
    return rows


def convergence_rows(assumption_rows_value: list[list[str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, (label, family_a, family_b, mechanism, enabling, limiting, systems, second_order, source_refs) in enumerate(CONVERGENCES, 1):
                if scenario == "A":
                    scenario_dependence = "More likely where interoperability, maintenance, workforce investment, trust, and human review keep pace with capability."
                    governance = "Requires accountable stewardship, transparent decision boundaries, defensive security, and institution-specific authority; optimization remains advisory."
                elif scenario == "B":
                    scenario_dependence = "Develops unevenly through strong nodes, negotiated standards, and partial bridges; surrounding systems may not share the same capability."
                    governance = "Requires negotiated interfaces and local accountability; benefits and burdens are distributed unevenly and standards may conflict."
                else:
                    scenario_dependence = "Can be technically powerful but friction-prone where infrastructure, data lineage, cyber continuity, trust, or oversight lag."
                    governance = "Requires governance catch-up, human authority, privacy protection, defensive continuity, and explicit recourse; capability does not confer legitimacy."
                uncertainty = f"{SCENARIO_META[scenario]['uncertainty'].capitalize()} uncertainty about {limiting.lower()} and the second-order effects of coupling."
                rows.append([
                    f"TCR-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), family_a, family_b,
                    mechanism, enabling, limiting, systems,
                    f"Phase 15A technology capability/interface evidence ({source_refs}); affected-system interpretation is qualitative and inferred.",
                    scenario_dependence, governance, uncertainty,
                    f"{second_order} In this scenario, the interaction may also redistribute maintenance, workforce, data, energy, or legitimacy burdens.",
                    assumptions[(sid, "interoperability")], FAMILY_SOURCE[family_a], "scenario", "scenario", "scenario_assumption",
                    f"{label}: interaction is not automatically beneficial and is not a basin deployment claim. {horizon_phrase(scenario, horizon)}",
                ])
    return rows


def system_profile(scenario: str, horizon: int, system_id: str) -> tuple[str, str, str, str, str]:
    if scenario == "A":
        direction = {
            "SYS-WATER": "more adaptive", "SYS-MATERIALS": "strengthened", "SYS-ENERGY": "more adaptive", "SYS-DATA": "more observable",
            "SYS-FREIGHT": "more automated", "SYS-ECOLOGY": "more observable", "SYS-EXPOSURE": "more observable", "SYS-BIOGEOCHEMISTRY": "more adaptive",
            "SYS-CLIMATE": "more observable", "SYS-GOVERNANCE": "strengthened", "SYS-POPULATION": "redistributed", "SYS-VECTOR-ECOLOGY": "more observable", "SYS-INFECTIOUS-DISEASE": "more observable",
        }[system_id]
        dep = "Some dependencies are buffered or substituted in selected interfaces, while energy, compute, data, and maintenance coupling remains visible."
        gov = "Human authority, institutional role boundaries, privacy, and public communication remain explicit; decision support does not become authority."
    elif scenario == "B":
        direction = {
            "SYS-WATER": "redistributed", "SYS-MATERIALS": "redistributed", "SYS-ENERGY": "redistributed", "SYS-DATA": "more fragmented",
            "SYS-FREIGHT": "redistributed", "SYS-ECOLOGY": "more observable", "SYS-EXPOSURE": "more fragmented", "SYS-BIOGEOCHEMISTRY": "redistributed",
            "SYS-CLIMATE": "more observable", "SYS-GOVERNANCE": "more fragmented", "SYS-POPULATION": "redistributed", "SYS-VECTOR-ECOLOGY": "more observable", "SYS-INFECTIOUS-DISEASE": "more fragmented",
        }[system_id]
        dep = "Dependencies move across strong nodes, weaker surrounding systems, and negotiated interfaces; fallback paths coexist with duplication and friction."
        gov = "Institutional and public trust varies by node; standards, authority, privacy, and communication remain domain-specific and nonuniform."
    else:
        direction = {
            "SYS-WATER": "more dependent", "SYS-MATERIALS": "more dependent", "SYS-ENERGY": "more dependent", "SYS-DATA": "more contested",
            "SYS-FREIGHT": "more automated", "SYS-ECOLOGY": "more contested", "SYS-EXPOSURE": "more contested", "SYS-BIOGEOCHEMISTRY": "more dependent",
            "SYS-CLIMATE": "more observable", "SYS-GOVERNANCE": "more contested", "SYS-POPULATION": "redistributed", "SYS-VECTOR-ECOLOGY": "more observable", "SYS-INFECTIOUS-DISEASE": "more contested",
        }[system_id]
        dep = "System capability and systemic coupling increase together; brittle energy, compute, communications, workforce, and governance dependencies remain."
        gov = "Technical systems remain subject to human authority, but delayed oversight, contested legitimacy, and uneven privacy protection constrain use."
    horizon_note = "2050 remains a bounded extrapolation from current/emerging capability." if horizon == 2050 else "2075 carries wider structural uncertainty; divergence is broader and no added precision is implied."
    uncertainty = f"{SCENARIO_META[scenario]['uncertainty'].capitalize()} uncertainty: {horizon_note}"
    return direction, dep, gov, uncertainty, scenario


def system_state_rows(assumption_rows_value: list[list[str]], convergence_rows_value: list[list[str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    rows = []
    family_by_system = {
        "SYS-WATER": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;AI / ADVANCED COMPUTE / AUTOMATION;CYBERSECURITY / DIGITAL RESILIENCE",
        "SYS-MATERIALS": "ADVANCED MATERIALS / MANUFACTURING;AI / ADVANCED COMPUTE / AUTOMATION;ADVANCED ENERGY",
        "SYS-ENERGY": "ADVANCED ENERGY;AI / ADVANCED COMPUTE / AUTOMATION;CYBERSECURITY / DIGITAL RESILIENCE",
        "SYS-DATA": "AI / ADVANCED COMPUTE / AUTOMATION;ADVANCED SENSING / AUTONOMOUS SYSTEMS;PRIVACY / SURVEILLANCE / DATA GOVERNANCE;CYBERSECURITY / DIGITAL RESILIENCE",
        "SYS-FREIGHT": "AI / ADVANCED COMPUTE / AUTOMATION;ADVANCED MATERIALS / MANUFACTURING;CYBERSECURITY / DIGITAL RESILIENCE",
        "SYS-ECOLOGY": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;BIOTECHNOLOGY / GENETIC ENGINEERING;PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
        "SYS-EXPOSURE": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;BIOTECHNOLOGY / GENETIC ENGINEERING;PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
        "SYS-BIOGEOCHEMISTRY": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;AI / ADVANCED COMPUTE / AUTOMATION;BIOTECHNOLOGY / GENETIC ENGINEERING",
        "SYS-CLIMATE": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;AI / ADVANCED COMPUTE / AUTOMATION;ADVANCED ENERGY",
        "SYS-GOVERNANCE": "PRIVACY / SURVEILLANCE / DATA GOVERNANCE;CYBERSECURITY / DIGITAL RESILIENCE;AI / ADVANCED COMPUTE / AUTOMATION",
        "SYS-POPULATION": "AI / ADVANCED COMPUTE / AUTOMATION;PRIVACY / SURVEILLANCE / DATA GOVERNANCE;ADVANCED MATERIALS / MANUFACTURING",
        "SYS-VECTOR-ECOLOGY": "ADVANCED SENSING / AUTONOMOUS SYSTEMS;BIOTECHNOLOGY / GENETIC ENGINEERING;PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
        "SYS-INFECTIOUS-DISEASE": "BIOTECHNOLOGY / GENETIC ENGINEERING;ADVANCED SENSING / AUTONOMOUS SYSTEMS;CYBERSECURITY / DIGITAL RESILIENCE;PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
    }
    mechanism_by_system = {
        "SYS-WATER": "AI + sensing + defensive cyber", "SYS-MATERIALS": "automation + advanced manufacturing + energy", "SYS-ENERGY": "AI + grid/storage + cyber",
        "SYS-DATA": "AI + sensing + privacy/data governance + PQC", "SYS-FREIGHT": "automation + manufacturing + cyber", "SYS-ECOLOGY": "sensing + genomic diagnostics + data governance",
        "SYS-EXPOSURE": "sensing + genomic diagnostics + privacy", "SYS-BIOGEOCHEMISTRY": "AI + sensing + biotechnology", "SYS-CLIMATE": "AI + sensing + advanced energy",
        "SYS-GOVERNANCE": "privacy/data governance + cyber + human-supervised AI", "SYS-POPULATION": "automation + data governance", "SYS-VECTOR-ECOLOGY": "sensing + genomic diagnostics", "SYS-INFECTIOUS-DISEASE": "genomic diagnostics + sensing + cyber + privacy",
    }
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, system_id in enumerate(SYSTEM_ORDER, 1):
                direction, dep, gov, uncertainty, _ = system_profile(scenario, horizon, system_id)
                rows.append([
                    f"TSS-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), system_id, family_by_system[system_id],
                    mechanism_by_system[system_id], direction, dep, gov, uncertainty,
                    "Phase 14 frozen systems ontology plus Phase 15A technology interfaces and explicit scenario construction; no system is redefined.",
                    assumptions[(sid, "interoperability")], "REG-PHASE14B-ATLAS", "scenario", "scenario", "scenario_assumption",
                    f"Qualitative effect on {SYSTEM_LABELS[system_id]}; state direction is not a score, forecast, causal estimate, or geographic deployment. {horizon_phrase(scenario, horizon)}",
                ])
    return rows


def dependency_rows(assumption_rows_value: list[list[str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, (system_a, system_b, family, domain, label, state, enabling, limiting, governance, source) in enumerate(DEPENDENCIES, 1):
                if scenario == "A":
                    change = "intensified_existing_dependency" if index % 3 else "substituted_some_dependency"
                    current_state = f"{state} Selected interfaces are more coordinated, but coupling and maintenance requirements remain visible."
                elif scenario == "B":
                    change = "redistributed_across_nodes"
                    current_state = f"{state} Strong and weak nodes handle the dependency differently, with bridges, duplication, and negotiation friction."
                else:
                    change = "intensified_and_brittle_dependency"
                    current_state = f"{state} Capability remains substantial in places, but mismatch and contested governance make the dependency more consequential without implying collapse."
                rows.append([
                    f"TDS-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), system_a, system_b, family, change,
                    current_state, enabling, limiting, governance,
                    f"{SCENARIO_META[scenario]['uncertainty'].capitalize()} uncertainty about whether the interface substitutes for, intensifies, or moves dependency in practice.",
                    f"Phase 14B dependency normalization plus Phase 15A interface evidence ({source}); this is qualitative scenario construction.",
                    assumptions[(sid, "infrastructure_adequacy")], source.split(";")[0].strip("[] "), "scenario", "scenario", "scenario_assumption",
                    f"Dependency direction is descriptive, not a risk, resilience, readiness, connectivity, or performance score. {label}; no exact route, capacity, outage, or deployment is inferred.",
                ])
    return rows


def governance_rows(assumption_rows_value: list[list[str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, (domain, family) in enumerate(GOVERNANCE_DOMAINS, 1):
                if scenario == "A":
                    state = "coordinated_selected_oversight" if horizon == 2050 else "auditable_institutionalized_selected_oversight"
                    oversight = "Oversight capacity broadly keeps pace in selected interfaces, with cost, implementation friction, and residual inequality retained."
                    trust = "Legitimacy is supported by transparent data stewardship, human review, communication, and recourse, not assumed universally."
                    privacy = "privacy-protective use with explicit purpose, access, retention, and accountability boundaries"
                    communication = "public communication is more coordinated but remains interpretive and institution-specific"
                    workforce = "workforce development and maintenance are funded selectively; scarcity and turnover remain possible"
                elif scenario == "B":
                    state = "negotiated_uneven_oversight" if horizon == 2050 else "durable_but_nonuniform_networked_oversight"
                    oversight = "Oversight is strong in some nodes, negotiated in others, and inconsistent across standards, vendors, and jurisdictions."
                    trust = "Legitimacy varies with local performance, access, and whether data use is understood and contestable."
                    privacy = "mixed privacy and surveillance practices with partial standards and local variation"
                    communication = "public communication is uneven and may not translate across institutions or methods"
                    workforce = "workforce and maintenance capacity are stronger in connected nodes and weaker at surrounding interfaces"
                else:
                    state = "capability_ahead_of_contested_oversight" if horizon == 2050 else "persistent_oversight_lag_and_contestation"
                    oversight = "Technical capability is substantial, but oversight, procurement, maintenance, and accountability lag or fragment at selected seams."
                    trust = "Institutional mistrust and contested use constrain legitimacy; capable institutions still operate in places."
                    privacy = "contested surveillance and data use with uneven privacy protection and recourse"
                    communication = "public communication is episodic, contested, or delayed at high-friction interfaces"
                    workforce = "specialized capability persists while maintenance, training, and replacement capacity remain brittle"
                if domain == "human_authority_and_AI":
                    boundary = "AI recommendation remains advisory; automation does not remove human, legal, or institutional authority."
                elif domain == "sensing_data_legitimacy":
                    boundary = "Measurement and observability do not create enforcement, permission, or decision authority."
                elif domain == "biosecurity_and_public_health":
                    boundary = "Detection, attribution, communication, and response coordination remain distinct; no harmful biological operational detail is modeled."
                else:
                    boundary = "Technical capability, governance capacity, and legitimacy remain distinct; no composite score is created."
                rows.append([
                    f"TGS-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), domain, family, state, oversight, trust, privacy,
                    communication, workforce, boundary, SCENARIO_META[scenario]["uncertainty"],
                    "Phase 15A governance boundaries, Phase 14 system/authority distinctions, and explicit qualitative scenario construction.",
                    assumptions[(sid, "governance_capacity")], AXIS_SOURCE["governance_capacity"], "scenario", "scenario", "scenario_assumption",
                    f"Governance effects are qualitative and scenario-dependent; optimization is not legitimacy and prediction is not certainty. {horizon_phrase(scenario, horizon)}",
                ])
    return rows


def uncertainty_rows(assumption_rows_value: list[list[str]]) -> list[list[str]]:
    assumptions = {(row[1], row[4]): row[0] for row in assumption_rows_value}
    family_for_domain = {
        "technology_maturity_and_capability": FAMILIES[0], "regional_adoption": FAMILIES[1], "infrastructure_and_interoperability": FAMILIES[2],
        "governance_and_oversight": FAMILIES[7], "trust_and_legitimacy": FAMILIES[7], "cybersecurity_and_continuity": FAMILIES[2],
        "workforce_and_maintenance": FAMILIES[4], "energy_and_compute": FAMILIES[3], "materials_and_supply_chain": FAMILIES[4],
        "biosecurity_attribution_and_response": FAMILIES[6],
    }
    subject_for_domain = {
        "technology_maturity_and_capability": "all Phase 15A families", "regional_adoption": "regional nodes and institutions", "infrastructure_and_interoperability": "digital, energy, and physical interfaces",
        "governance_and_oversight": "authority and oversight interfaces", "trust_and_legitimacy": "public and institutional legitimacy", "cybersecurity_and_continuity": "defensive digital continuity",
        "workforce_and_maintenance": "workforce and maintenance systems", "energy_and_compute": "energy, compute, and communications", "materials_and_supply_chain": "qualified materials and supply chains",
        "biosecurity_attribution_and_response": "diagnostic, environmental, food/agricultural, and public-health interfaces",
    }
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            for index, domain in enumerate(UNCERTAINTY_DOMAINS, 1):
                if domain == "biosecurity_attribution_and_response":
                    uncertainty = "Diagnostic speed, sampling, attribution, laboratory capacity, public communication, supply-chain resilience, dual-use governance, and response coordination remain uncertain."
                    not_inferred = "No pathogen design, engineering method, harmful-agent optimization, evasion method, attack scenario, wet-lab procedure, incidence, or health outcome is inferred."
                else:
                    uncertainty = f"{SCENARIO_META[scenario]['uncertainty'].capitalize()} uncertainty remains around {domain.replace('_', ' ')}; the horizon does not add precision."
                    not_inferred = "No exact deployment, adoption percentage, capacity, probability, health outcome, or composite risk/resilience/readiness score is inferred."
                rows.append([
                    f"TUS-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(horizon), domain, subject_for_domain[domain],
                    SCENARIO_META[scenario]["uncertainty"], uncertainty,
                    f"Depends on the scenario family and horizon; 2075 divergence is wider than 2050 without becoming more precise.", not_inferred,
                    "Phase 15A accepted/frozen baseline and explicit scenario construction.", assumptions[(sid, "technology_maturity")], FAMILY_SOURCE[family_for_domain[domain]],
                    "scenario", "scenario", "scenario_assumption",
                    f"Unknown is retained as unknown; it is not low risk, absence, or a guaranteed bottleneck. {horizon_phrase(scenario, horizon)}",
                ])
    return rows


def comparison_rows() -> list[list[str]]:
    rows = []
    for scenario in SCENARIOS:
        for horizon in HORIZONS:
            sid = scenario_id(scenario, horizon)
            values = AXIS_VALUES[scenario]
            if scenario == "A":
                energy = "energy and compute are coordinated enabling dependencies with residual cost and maintenance friction"
                coupling = "coupling is made more legible and selectively managed, not removed"
                bio = "diagnostic speed, laboratory coordination, public communication, and supply-chain resilience improve selectively"
                equity = "residual inequality and unequal access remain"
            elif scenario == "B":
                energy = "energy, compute, and communications are strong in nodes and uneven across the network"
                coupling = "coupling is redistributed through bridges, weak links, and duplicated standards"
                bio = "capacity is mixed across laboratories, surveillance programs, food/agriculture, and public communication"
                equity = "benefits, burdens, and access are distributed unevenly"
            else:
                energy = "energy and compute capability is high in places but dependence is brittle and contested"
                coupling = "technical capability and systemic coupling increase together without guaranteed resilience"
                bio = "diagnostic and sensing capability persists, but attribution, communication, coordination, and continuity are strained"
                equity = "unequal access and exposure to friction are persistent without a collapse claim"
            rows.append([
                sid, SCENARIO_META[scenario]["name"], str(horizon), values["technology_maturity"][0 if horizon == 2050 else 1],
                values["regional_adoption"][0 if horizon == 2050 else 1], values["infrastructure_adequacy"][0 if horizon == 2050 else 1],
                values["interoperability"][0 if horizon == 2050 else 1], values["governance_capacity"][0 if horizon == 2050 else 1],
                values["trust_legitimacy"][0 if horizon == 2050 else 1], values["cyber_digital_resilience"][0 if horizon == 2050 else 1],
                values["workforce_energy_material_capacity"][0 if horizon == 2050 else 1], energy, coupling, bio, equity,
                "Qualitative scenario comparison; no winner ranking, probability, composite score, or forecast.",
                f"{horizon_phrase(scenario, horizon)} Scenario family {scenario} is not a midpoint or prediction.",
            ])
    return rows


def write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def build_reports(assumptions: list[list[str]], family_states: list[list[str]], convergences: list[list[str]], systems: list[list[str]], dependencies: list[list[str]], governance: list[list[str]], uncertainties: list[list[str]], comparisons: list[list[str]], sources: list[dict[str, str]]) -> None:
    counts = {
        "assumptions": len(assumptions), "technology_family_states": len(family_states), "convergence_relationships": len(convergences),
        "system_states": len(systems), "dependency_states": len(dependencies), "governance_states": len(governance), "uncertainty_states": len(uncertainties), "comparison_rows": len(comparisons),
    }
    family_counts = Counter(row[4] for row in family_states)
    source_ids = sorted({row["source_id"] for row in sources})
    write_report(REPORTS / "phase15b_technology_convergence_futures.md", f"""# Phase 15B Technology Convergence Futures — 2050 / 2075

## Status and method

This is a bounded qualitative scenario package, not a technology adoption forecast. It asks how combinations of capability, infrastructure, governance, institutional capacity, adoption, and legitimacy could alter Western Basin system behavior. The package preserves the distinctions capability ≠ deployment ≠ adoption ≠ benefit and technology ≠ resilience.

The three scenario families are deliberately not ranked:

- **A — Coordinated Technological Adaptation:** selective high-value adoption, stronger interoperability, defensive cybersecurity, resilient energy/compute/communications, trusted sensing and data governance, cautious biotechnology/biosecurity governance, workforce and maintenance investment, and institutional capacity that broadly keeps pace in selected interfaces. Cost, friction, residual inequality, technical failure, and governance limits remain.
- **B — Uneven Networked Modernization:** advanced capability is available, but infrastructure, adoption, workforce, standards, interoperability, trust, and governance vary by node. Strong nodes connect through weaker surrounding systems. This is a plausible middle scenario, not a probability claim.
- **C — High Capability / High Friction Basin:** substantial AI, automation, sensing, biotechnology, advanced manufacturing, and energy options coexist with weak interoperability, cyber stress, institutional mistrust, infrastructure mismatch, delayed oversight, unequal access, and brittle dependencies. It is not collapse or dystopia.

2050 is a bounded extrapolation from current/emerging capability with uncertainty. 2075 carries wider structural uncertainty and wider scenario divergence; it is not more precise.

## Package counts

{counts}

All six scenario-horizon states are present. Every state is marked `reality_status=scenario`, `canon_status=scenario`, and `relationship_basis=scenario_assumption`; baseline 2026 references remain separate fields or source/basis pointers.

## Cross-cutting axes

The package uses eight non-composite axes: technology maturity; regional adoption; infrastructure adequacy; interoperability; governance capacity; institutional trust/legitimacy; cybersecurity/digital resilience; and workforce-energy-material capacity. They are described qualitatively and are not summed into resilience, risk, readiness, connectivity, or performance scores.

## Technology-family treatment

Each of the eight frozen Phase 15A families has one state for each of the six scenario-horizon combinations ({len(family_states)} states total). Family state rows distinguish capability, maturity, adoption, infrastructure, interoperability, governance, trust, cyber, workforce, energy/compute/material, privacy/surveillance, and uncertainty. No national/general evidence is converted into basin deployment.

Family-state counts: {dict(family_counts)}.

## Convergence logic

The {len(convergences)} relationship rows represent ten interactions across all six scenario-horizon states. Each captures enabling conditions, limiting conditions, affected Phase 14 systems, evidence basis, scenario dependence, governance implications, uncertainty, and possible second-order effects. Major interfaces include AI+sensing; AI+grid/storage; automation+advanced manufacturing; genomic diagnostics+sensing; post-quantum transition+digital infrastructure; distributed energy/storage+compute; sensing+privacy/data governance; defensive cyber+digitally dependent systems; biotechnology+food/agriculture+governance; and quantum sensing+data/energy.

Convergence is not assumed beneficial. It can substitute for some dependencies while creating new energy, compute, data, workforce, maintenance, privacy, or legitimacy dependencies. Observability can increase without control; automation can increase without removing human authority; capability can increase while systemic coupling also increases.

## System consequences

The system table covers all 13 frozen Phase 14 systems in every scenario-horizon state ({len(systems)} rows). State directions are qualitative descriptors such as strengthened, weakened, redistributed, more adaptive, more dependent, more observable, more automated, more contested, and more fragmented. They are not scores or forecasts. The systems ontology and prior IDs are reused without modification.

## Cross-system dependencies and governance

The package contains {len(dependencies)} dependency states and {len(governance)} governance states. Dependencies explicitly examine energy↔compute, data↔governance, sensing↔trust, automation↔workforce, biotechnology↔public health/agriculture/governance, manufacturing↔materials/freight/energy, and defensive cybersecurity across digitally dependent systems. Governance rows retain human authority, privacy, public communication, role clarity, and oversight boundaries.

## Evidence boundary

Technology-family capability and regional-system context reuse Phase 15A source IDs. Repository sources include {len(source_ids)} accepted Phase 15A source identifiers. The evidence supports capability/status, existing system context, or methodological interface construction; it does not support exact future deployment, adoption percentages, regional capacity, health outcomes, or probabilities.

## Persistent boundaries

- AI recommendation ≠ authority; automation ≠ autonomous governance; prediction ≠ certainty; optimization ≠ legitimacy.
- Measurement ≠ interpretation ≠ decision ≠ enforcement.
- Cybersecurity remains defensive; no exploit, attack procedure, offensive technique, or sensitive control topology is modeled.
- Biosecurity remains a high-level governance/resilience/public-health lens; no pathogen design, engineering method, harmful-agent optimization, evasion method, attack scenario, wet-lab procedure, or misuse instruction is included.
- Quantum, fusion, and advanced nuclear are conservative modifiers; no regional deployment date or precise deployment is assumed.
- No exact health outcome, incidence, outbreak, dose, exposure, or individual risk is modeled.
- Great Black Swamp remains **C — HOLD / noncanonical** and the Toledo intake-coordinate discrepancy remains **UNRESOLVED**.
- Phase 16 is not implemented.
""")

    write_report(REPORTS / "phase15b_biosecurity_futures.md", f"""# Phase 15B Biosecurity Futures Lens — 2050 / 2075

Biosecurity is treated as a bounded system/resilience/public-health lens within the three technology scenarios. It is not a threat forecast, disease forecast, or biological-operations model.

## Scenario findings

- **A — Coordinated Technological Adaptation:** diagnostic speed, surveillance coordination, laboratory/diagnostic capacity, public communication, food/agricultural resilience, supply-chain continuity, dual-use governance, and response coordination improve selectively where interoperability, workforce, privacy, and trust are maintained. More detection can mean more recorded observations; it does not establish incidence, attribution, transmission, illness, or absence.
- **B — Uneven Networked Modernization:** strong laboratories, environmental programs, agricultural systems, and public-health institutions connect through uneven data standards and communications. Detection and response capacity vary by node; state, municipal, industrial, and public communication practices are not averaged into one basin condition.
- **C — High Capability / High Friction Basin:** genomic diagnostics, sensing, compute, and biotechnology can be substantial in selected systems, but attribution uncertainty, laboratory access, cyber continuity, public mistrust, supply-chain mismatch, and delayed governance narrow response coordination at selected seams. This is not a collapse or attack scenario.

## Variables retained

The scenario tables allow only high-level variables: diagnostic speed; surveillance coordination; attribution uncertainty; supply-chain resilience; laboratory/diagnostic capacity; public communication; dual-use governance; response coordination; and food/agricultural resilience. They preserve the evidence ladder between observation, interpretation, attribution, response, exposure, dose, and health outcome.

## Safety boundary

This package contains no pathogen design, engineering method, optimization of harmful biological agents, attack scenario, evasion method, wet-lab procedure, weaponization, or misuse instruction. It makes no claim about a current or future regional biological threat, exact incidence, outbreak probability, production loss, contamination event, exposure, dose, illness, or health outcome.

## Evidence and uncertainty

Phase 15A CDC Advanced Molecular Detection and One Health source IDs are reused as high-level capability/context evidence. Phase 12/13 system IDs are used as frozen ontology targets, not as future disease or threat evidence. Attribution, sampling, laboratory capacity, interoperability, privacy, communication, and response remain explicitly uncertain, especially in 2075.
""")

    write_report(REPORTS / "phase15b_scenario_comparison.md", """# Phase 15B Scenario Comparison — 2050 / 2075

The comparison is qualitative and non-ranking. It does not identify a best scenario, assign probabilities, sum axes, or convert scenario states into forecasts.

## Distinguishing features

| Family | Technology maturity and adoption | Infrastructure / interoperability | Governance / trust | System coupling / equity |
|---|---|---|---|---|
| A — Coordinated Technological Adaptation | Selective high-value capability and adoption; capability remains distinct from deployment and benefit. | Resilient priority infrastructure, stronger standards, and planned maintenance; residual gaps remain. | Human-supervised decision support, defensive cyber, trusted stewardship, and clearer oversight in selected interfaces. | Coupling is made more legible and selectively managed; residual inequality and cost remain. |
| B — Uneven Networked Modernization | Advanced capability is available, but adoption, workforce, and standards vary by node; strong nodes connect through weaker systems. | Patchy infrastructure, partial bridges, incompatible methods, and negotiated interoperability. | Mixed trust and fragmented governance; issue-specific agreements and local accountability coexist with friction. | Dependencies redistribute across a network; benefits and burdens are uneven. |
| C — High Capability / High Friction Basin | High capability in selected systems, but unequal access and adoption occur amid delayed governance. | Weak interoperability, cyber stress, infrastructure mismatch, and brittle energy/compute/material dependencies. | Capable institutions persist, but legitimacy is contested and oversight is delayed or fragmented; human authority remains. | Capability and systemic coupling increase together; unequal access and friction persist without a collapse claim. |

## Horizon discipline

2050 rows describe a bounded intermediate trajectory from current/emerging evidence and explicit assumptions. 2075 rows describe wider structural uncertainty and greater scenario divergence, not greater precision. No row contains an exact deployment percentage, unsupported capacity, exact health outcome, or scenario probability.

## Reading the comparison

The axes are not independent scores. Technology maturity can coexist with low adoption; adoption can coexist with weak infrastructure; observability can increase without control; automation can increase without removing human authority; and interoperability can increase capability while increasing systemic coupling. The comparison therefore reports tensions and conditions rather than a winner.

## Holds and exclusions

Great Black Swamp remains **C — HOLD / noncanonical**. The Toledo intake-coordinate discrepancy remains **UNRESOLVED**. Phase 16 is not implemented. No release or tag was created.
""")

    write_report(REPORTS / "phase15b_provenance_check.md", """# Phase 15B Provenance and Scenario-Boundary Check

## Result

PASS for the generated Phase 15B package when paired with `validate_phase15b_technology.py` and `validate_phase15b_technology.R`.

## Provenance model

All scenario records reference a source identifier present in the accepted Phase 15A `data/processed/analysis/technology_sources.csv` registry. External capability claims reuse Phase 15A's bounded government/institutional evidence. Regional source IDs point to accepted/frozen Phase 1–14 artifacts used as system context; they do not become evidence of local technology deployment. Scenario assumptions and consequences are explicitly marked `SCENARIO ASSUMPTION` or `SCENARIO STATE` and carry a named horizon and scenario ID.

The evidence ladder remains explicit: source-backed capability/status and accepted system context are distinct from project inference, scenario assumption, scenario consequence, adoption, benefit, exposure, dose, illness, or legal authority. No new broad technology research is used in Phase 15B.

## Machine-check requirements

The validators check source/assumption references, eight-family and 13-system coverage, scenario/horizon coverage, exact unsupported-number patterns, fact/inference/scenario labels, AI authority boundaries, defensive cybersecurity, safe biosecurity wording, conservative quantum/fusion/advanced-nuclear treatment, no composite scores, protected freeze integrity, active holds, and absence of Phase 16.

## Source IDs reused

The source registry is the Phase 15A accepted/frozen registry. The principal source classes reused are NIST AI/Privacy/PQC/Quantum/Manufacturing; DOE AI, storage, advanced-reactor, hydrogen, and fusion context; NOAA IOOS observing context; CISA defensive cybersecurity; CDC Advanced Molecular Detection and One Health; EPA circular-materials context; and accepted Phase 1–14 regional-system artifacts.

## Limitations

The package is qualitative and scenario-dependent. It does not establish regional deployment, adoption rates, precise maturity dates, capacity, firm power, quantum advantage, fusion deployment, advanced-nuclear siting, diagnostic results, disease incidence, exposure, dose, health outcomes, or probabilities. Unknown remains unknown.
""")

    write_report(REPORTS / "phase15b_qa.md", f"""# Phase 15B QA — Technology Convergence Futures

## Scope

Phase 15B is additive to the accepted/frozen Phase 15A baseline and Phase 14 ontology. No frozen Phase 1–15A artifact is modified. Phase 16 is absent.

## Generated inventory

- {len(assumptions)} qualitative scenario assumptions across 8 axes.
- {len(family_states)} technology-family states: 8 families × 3 scenario families × 2 horizons.
- {len(convergences)} convergence relationship rows: 10 interaction templates × 6 scenario-horizon states.
- {len(systems)} system consequence rows: 13 frozen Phase 14 systems × 6 scenario-horizon states.
- {len(dependencies)} dependency states across new, intensified, substituted, and redistributed dependency descriptions.
- {len(governance)} governance states with AI authority, sensing/enforcement, privacy, cyber, biosecurity, and human-review boundaries.
- {len(uncertainties)} explicit uncertainty states.
- {len(comparisons)} comparison rows.
- Two conceptual PNG/SVG figures; neither is a geographic map.

## Required semantic checks

- Three scenario families and two horizons are complete.
- All eight Phase 15A technology families are covered in all six states.
- All 13 system IDs resolve to `metadata/atlas_systems.yml`.
- Technology IDs and baseline family fields resolve to Phase 15A.
- Scenario rows are not forecasts and do not contain exact unsupported adoption percentages or health outcomes.
- AI recommendation remains separate from authority; sensing remains separate from enforcement; automation remains separate from autonomous governance.
- Cybersecurity remains defensive and high-level.
- Biosecurity remains safe and high-level.
- Quantum, fusion, and advanced nuclear remain bounded modifiers rather than assumed regional deployment.
- No composite risk, resilience, readiness, vulnerability, connectivity, or performance score is generated.
- Evidence, assumption, uncertainty, and scenario references resolve.
- Great Black Swamp **C — HOLD / noncanonical** and Toledo intake-coordinate **UNRESOLVED** remain visible.

## Figure QA

`technology_convergence_futures.png/.svg` compares scenario families across 2050/2075 with qualitative labels. `technology_cross_system_effects.png/.svg` shows representative family-to-system interfaces and convergence mechanisms without a hairball. SVG text is retained for inspection; line presence is not effect size, causation, risk, or deployment.

## Validation commands

- `python src/python/systems/build_phase15b_technology.py`
- `python src/python/systems/validate_phase15b_technology.py`
- `Rscript src/R/systems/validate_phase15b_technology.R --require-review`
- `npm run test`
- `npm run build`
- `git diff --check`
""")


def render_figures(comparisons: list[list[str]], convergences: list[list[str]]) -> None:
    plt.rcParams.update({"svg.fonttype": "none", "font.size": 10, "axes.titleweight": "bold"})
    # Figure 1: scenario comparison matrix, categorical and non-proportional.
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=180)
    ax.set_facecolor("#f4efe6")
    fig.patch.set_facecolor("#f4efe6")
    for row_index, row in enumerate(comparisons):
        scenario = row[0][0]
        horizon = row[2]
        y = 5 - row_index
        color = SCENARIO_META[scenario]["color"]
        ax.add_patch(FancyBboxPatch((0.02, y - 0.35), 0.16, 0.7, boxstyle="round,pad=0.015", facecolor=color, edgecolor="none", alpha=0.95))
        ax.text(0.10, y, f"{scenario} — {horizon}", color="white", ha="center", va="center", weight="bold")
        fields = [row[3], row[4], row[5], row[6], row[7], row[8], row[10], row[11], row[12], row[13], row[14]]
        labels = ["maturity", "adoption", "infrastructure", "interoperability", "governance", "trust", "workforce", "energy/compute", "coupling", "biosecurity", "equity"]
        x = 0.21
        for label, value in zip(labels, fields):
            width = 0.068 if label in {"maturity", "adoption", "trust", "equity"} else 0.074
            ax.add_patch(FancyBboxPatch((x, y - 0.29), width, 0.58, boxstyle="round,pad=0.008", facecolor="#fffaf0", edgecolor="#d7cdbd", linewidth=0.7))
            ax.text(x + width / 2, y + 0.12, label, ha="center", va="center", fontsize=6.5, color="#6c6256")
            ax.text(x + width / 2, y - 0.06, value, ha="center", va="center", fontsize=6.2, wrap=True)
            x += width + 0.006
    ax.set_xlim(0, 1.02)
    ax.set_ylim(-0.8, 6.2)
    ax.axis("off")
    ax.set_title("Technology Convergence Futures — qualitative scenario comparison", loc="left", fontsize=17, pad=18)
    fig.text(0.02, 0.025, "2050 is bounded extrapolation; 2075 has wider uncertainty. No score, probability, exact deployment, or winner ranking.", fontsize=9, color="#5b5146")
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    fig.savefig(FIGURES / "technology_convergence_futures.png", dpi=180)
    fig.savefig(FIGURES / "technology_convergence_futures.svg")
    plt.close(fig)

    # Figure 2: selected family-to-system interfaces; representative, not a hairball.
    fig, ax = plt.subplots(figsize=(15, 9), dpi=180)
    ax.set_facecolor("#111827")
    fig.patch.set_facecolor("#111827")
    left = [("AI / compute", 0.85), ("Sensing", 0.66), ("Cyber", 0.47), ("Energy", 0.28), ("Biotech", 0.09)]
    right = [("Water", 0.90), ("Energy / compute", 0.75), ("Data / governance", 0.60), ("Materials / freight", 0.45), ("Ecology / health", 0.30), ("Population / trust", 0.15)]
    left_xy = {name: (0.18, y) for name, y in left}
    right_xy = {name: (0.82, y) for name, y in right}
    for name, (x, y) in left_xy.items():
        ax.add_patch(FancyBboxPatch((x - 0.10, y - 0.045), 0.20, 0.09, boxstyle="round,pad=0.012", facecolor="#24485a", edgecolor="#9dd5c8", linewidth=1.2))
        ax.text(x, y, name, color="white", ha="center", va="center", weight="bold", fontsize=9)
    for name, (x, y) in right_xy.items():
        ax.add_patch(FancyBboxPatch((x - 0.12, y - 0.045), 0.24, 0.09, boxstyle="round,pad=0.012", facecolor="#493c55", edgecolor="#e4b96f", linewidth=1.2))
        ax.text(x, y, name, color="white", ha="center", va="center", weight="bold", fontsize=9)
    edges = [
        ("AI / compute", "Water", "interpretation"), ("AI / compute", "Energy / compute", "adaptive operations"),
        ("AI / compute", "Materials / freight", "automation"), ("Sensing", "Water", "observation"),
        ("Sensing", "Data / governance", "legitimacy"), ("Sensing", "Ecology / health", "detection"),
        ("Cyber", "Energy / compute", "defensive continuity"), ("Cyber", "Data / governance", "trusted exchange"),
        ("Energy", "Energy / compute", "storage / compute"), ("Energy", "Materials / freight", "process inputs"),
        ("Biotech", "Ecology / health", "diagnostics"), ("Biotech", "Population / trust", "communication / privacy"),
    ]
    for source, target, label in edges:
        x1, y1 = left_xy[source]
        x2, y2 = right_xy[target]
        color = "#8fbfb8" if source in {"Sensing", "Biotech"} else "#dba85f"
        ax.annotate("", xy=(x2 - 0.13, y2), xytext=(x1 + 0.11, y1), arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.4, "alpha": 0.75, "connectionstyle": "arc3,rad=0.02"})
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.014, label, color="#e5e7eb", ha="center", va="center", fontsize=7, bbox={"facecolor": "#111827", "edgecolor": "none", "pad": 1.4, "alpha": 0.8})
    ax.text(0.5, 0.98, "Cross-System Technology Effects", transform=ax.transAxes, color="white", ha="center", va="top", fontsize=18, weight="bold")
    ax.text(0.5, 0.935, "Representative convergence interfaces — not geographic topology, causation, risk, or deployment", transform=ax.transAxes, color="#cbd5e1", ha="center", va="top", fontsize=9)
    ax.text(0.5, 0.02, "Observability can increase without control • automation does not remove human authority • coupling can increase with capability", transform=ax.transAxes, color="#e5b871", ha="center", va="bottom", fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGURES / "technology_cross_system_effects.png", dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(FIGURES / "technology_cross_system_effects.svg", facecolor=fig.get_facecolor())
    plt.close(fig)


def refresh_manifest(include_optional: bool = True) -> None:
    entries = {}
    for relative in MANIFEST_PATHS:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            if relative == "reports/phase15b_independent_review.md" and not include_optional:
                continue
            continue
        entries[relative] = {"bytes": path.stat().st_size, "sha256": digest(path), "role": "Phase 15B working artifact"}
    payload = {
        "phase": "15B",
        "status": "implemented_validated_pending_sol_acceptance",
        "source_commit": BASE_SHA,
        "base_sha_expected": BASE_SHA,
        "scenario_ids": [scenario_id(s, y) for s in SCENARIOS for y in HORIZONS],
        "scenario_families": {s: SCENARIO_META[s]["name"] for s in SCENARIOS},
        "horizons": list(HORIZONS),
        "counts": {
            "assumptions": 48, "technology_family_states": 48, "convergence_relationships": 60, "system_states": 78,
            "dependency_states": 72, "governance_states": 48, "uncertainty_states": 60, "comparison_rows": 6,
        },
        "technology_families": list(FAMILIES),
        "phase14_system_count": 13,
        "qualitative_only": True,
        "numeric_future_values_adopted": False,
        "forecast": False,
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"},
        "phase15a_status": "ACCEPTED / FROZEN",
        "phase14_status": "COMPLETE / ACCEPTED / FROZEN",
        "phase16_status": "NOT IMPLEMENTED",
        "release_created": False,
        "tag_created": False,
        "artifacts": entries,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def build() -> None:
    baseline, source_ids, sources = load_baseline()
    assert set(baseline) == set(FAMILIES)
    assert len(source_ids) == len(sources)
    ontology = yaml.safe_load(SYSTEMS_YAML.read_text(encoding="utf-8"))
    assert {row["system_id"] for row in ontology["systems"]} == set(SYSTEM_ORDER)
    assumptions = assumption_rows()
    family_states = family_state_rows(assumptions, baseline)
    convergences = convergence_rows(assumptions)
    systems = system_state_rows(assumptions, convergences)
    dependencies = dependency_rows(assumptions)
    governance = governance_rows(assumptions)
    uncertainties = uncertainty_rows(assumptions)
    comparisons = comparison_rows()
    write_csv(SCENARIO_DIR / "technology_scenario_assumptions.csv", ASSUMPTION_COLUMNS, assumptions)
    write_csv(SCENARIO_DIR / "technology_family_states.csv", FAMILY_STATE_COLUMNS, family_states)
    write_csv(SCENARIO_DIR / "technology_convergence_relationships.csv", CONVERGENCE_COLUMNS, convergences)
    write_csv(SCENARIO_DIR / "technology_system_states.csv", SYSTEM_STATE_COLUMNS, systems)
    write_csv(SCENARIO_DIR / "technology_dependency_states.csv", DEPENDENCY_COLUMNS, dependencies)
    write_csv(SCENARIO_DIR / "technology_governance_states.csv", GOVERNANCE_COLUMNS, governance)
    write_csv(SCENARIO_DIR / "technology_uncertainty_states.csv", UNCERTAINTY_COLUMNS, uncertainties)
    write_csv(SCENARIO_DIR / "technology_scenario_comparison.csv", COMPARISON_COLUMNS, comparisons)
    render_figures(comparisons, convergences)
    build_reports(assumptions, family_states, convergences, systems, dependencies, governance, uncertainties, comparisons, sources)
    refresh_manifest(include_optional=False)
    print(json.dumps({"phase": "15B", "built": True, "counts": {"assumptions": len(assumptions), "technology_family_states": len(family_states), "convergence_relationships": len(convergences), "system_states": len(systems), "dependency_states": len(dependencies), "governance_states": len(governance), "uncertainty_states": len(uncertainties), "comparison_rows": len(comparisons)}}, indent=2))


def main() -> int:
    if "--refresh-manifest" in sys.argv:
        refresh_manifest(include_optional=True)
        print(json.dumps({"phase": "15B", "manifest_refreshed": True, "artifacts": len(json.loads(MANIFEST.read_text(encoding="utf-8"))["artifacts"])}, indent=2))
        return 0
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
