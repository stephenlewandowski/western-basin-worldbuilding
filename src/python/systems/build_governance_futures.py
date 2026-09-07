"""Build Phase 10C: qualitative governance futures for 2050 and 2075.

The package is a separate scenario layer over the accepted/frozen Phase 10A and
10B 2026 institutional baselines. It does not amend baseline tables, assign
future legal authority, create jurisdiction polygons, or rank governance.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from textwrap import shorten

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch
try:
    import geopandas as gpd
except Exception:  # pragma: no cover - map context is optional at build time
    gpd = None

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

ASSUMPTIONS = SCENARIOS / "governance_scenario_assumptions.csv"
ACTOR_STATES = SCENARIOS / "governance_actor_states_scenario.csv"
AUTHORITY_STATES = SCENARIOS / "governance_authority_states_scenario.csv"
DEPENDENCY_STATES = SCENARIOS / "governance_dependency_states_scenario.csv"
COORDINATION_STATES = SCENARIOS / "governance_coordination_states_scenario.csv"
UNCERTAINTY_STATES = SCENARIOS / "governance_uncertainty_states_scenario.csv"
SOURCES = ANALYSIS / "governance_scenario_sources.csv"
COMPARISON = FIGURES / "governance_scenario_comparison.csv"
COMPARISON_PNG = FIGURES / "governance_scenario_comparison.png"
COMPARISON_SVG = FIGURES / "governance_scenario_comparison.svg"
MAP2050 = MAPS / "34_governance_futures_2050"
MAP2075 = MAPS / "34b_governance_futures_2075"
MANIFEST = REPORTS / "governance_scenario_manifest.json"

SCENARIOS_META = {
    "A": {
        "name": "Integrated Basin Governance",
        "short": "integrated",
        "plausibility": "moderate",
        "source": "GFS-001",
        "basis": "Great Lakes coordination precedent, adaptive-governance literature, and explicit scenario construction",
    },
    "B": {
        "name": "Federated / Networked Governance",
        "short": "federated",
        "plausibility": "moderate",
        "source": "GFS-010",
        "basis": "polycentric governance literature, Great Lakes coordination precedent, and explicit scenario construction",
    },
    "C": {
        "name": "Fragmented / Contested Governance",
        "short": "fragmented",
        "plausibility": "exploratory",
        "source": "GFS-009",
        "basis": "institutional-stress logic, adaptive-capacity literature, and explicit scenario construction",
    },
}
HORIZONS = (2050, 2075)
SCENARIO_IDS = tuple(f"{s}{y}" for s in SCENARIOS_META for y in HORIZONS)

SOURCE_ROWS = [
    ["GFS-001", "Great Lakes Commission — About", "https://www.glc.org/about", "interstate_institutional_source", "Great Lakes Commission structure and coordination role", "Great Lakes states and Canadian provinces", "2026-09-07", "retrieved", "Supports institutional precedent and coordination context; it is not a future legal forecast."],
    ["GFS-002", "Great Lakes–St. Lawrence Governors & Premiers — Water Management", "https://www.cglg.org/projects/water-management", "binational_institutional_source", "regional water-management framework and implementation coordination", "eight states and two provinces", "2026-09-07", "retrieved", "Supports coordination precedent; it does not establish a future Western Basin government."],
    ["GFS-003", "Great Lakes Indian Fish & Wildlife Commission", "https://www.glifwc.org", "tribal_primary_source", "intertribal natural-resource, treaty-rights, and information functions", "member tribes and treaty-ceded territories", "2026-09-07", "retrieved", "Supports GLIFWC as an intertribal body; it does not support assigning new Western Basin jurisdiction."],
    ["GFS-004", "NIST AI Risk Management Framework", "https://www.nist.gov/itl/ai-risk-management-framework", "federal_governance_guidance", "voluntary trustworthy-AI risk-management and public/private collaboration context", "United States / general", "2026-09-07", "retrieved", "Supports bounded decision-support governance; no future AI deployment or legal authority is forecast."],
    ["GFS-005", "NIST Privacy Framework", "https://www.nist.gov/privacy-framework", "federal_governance_guidance", "privacy-aware data stewardship and risk management", "United States / general", "2026-09-07", "retrieved", "Supports privacy-aware federation; no personal dataset or privacy score is modeled."],
    ["GFS-006", "NOAA Integrated Ocean Observing System", "https://ioos.noaa.gov", "federal_observing_system_source", "integrated observing network, predictive tools, and public-safety information", "coasts and Great Lakes", "2026-09-07", "retrieved", "Supports an observing-system precedent; it does not imply complete future coverage or authority."],
    ["GFS-007", "DOE Grid Modernization and the Smart Grid", "https://www.energy.gov/oe/grid-modernization-and-smart-grid", "federal_infrastructure_guidance", "public/private grid modernization and interoperable technology context", "United States / general", "2026-09-07", "retrieved", "Supports public/private coordination context; no local asset topology, dispatch, or control claim is made."],
    ["GFS-008", "FEMA Hazard Mitigation Planning", "https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning", "federal_planning_guidance", "hazard-mitigation planning exchange and planning support", "United States / state, tribal, and local partners", "2026-09-07", "retrieved", "Supports planning and finance context; it does not make FEMA the local operator or regulator."],
    ["GFS-009", "USGS Climate Adaptation Science Centers", "https://www.usgs.gov/programs/climate-adaptation-science-centers", "federal_science_network", "adaptation science partnerships and actionable data/tools", "United States / regional centers", "2026-09-07", "retrieved", "Supports adaptation-learning context; it does not quantify future governance performance."],
    ["GFS-010", "Ostrom — A General Framework for Analyzing Sustainability of Social-Ecological Systems", "https://www.science.org/doi/10.1126/science.1172133", "peer_reviewed_governance_literature", "multi-level social-ecological systems and institutional diversity", "general / social-ecological systems", "2026-09-07", "retrieved", "Supports polycentric and multi-level analysis; it is not a Western Basin forecast or governance ranking."],
    ["GFS-011", "Canada — Great Lakes Water Quality Agreement", "https://www.canada.ca/en/environment-climate-change/corporate/international-affairs/partnerships-countries-regions/north-america/great-lakes-water-quality-agreement.html", "binational_treaty_source", "GLWQA agreement status, objectives, annexes, implementation, and reporting context", "Canada–United States Great Lakes", "2026-09-07", "delegated_research_retrieved", "Current agreement context only; no future treaty amendment or domestic authority is inferred."],
    ["GFS-012", "Canada Water Agency — Great Lakes Protection", "https://www.canada.ca/en/canada-water-agency/freshwater-ecosystem-initiatives/great-lakes/great-lakes-protection/canada-united-states-water-quality-agreement.html", "binational_program_source", "GLWQA implementation, consultation, participation, and adaptive-management context", "Canada–United States Great Lakes", "2026-09-07", "delegated_research_retrieved", "Supports current participation context; future participation changes remain scenario assumptions."],
    ["GFS-013", "International Joint Commission — Role", "https://ijc.org/en/who/role", "binational_treaty_body_source", "IJC case-by-case boundary-water approval, investigation, recommendation, and order context", "United States–Canada boundary waters", "2026-09-07", "delegated_research_retrieved", "Current role context only; recommendations and project approvals are not generalized into a basin regulator."],
    ["GFS-014", "International Joint Commission — Boards", "https://ijc.org/en/who/boards", "binational_adaptive_management_source", "Great Lakes–St. Lawrence adaptive-management and assessment precedent", "Great Lakes–St. Lawrence", "2026-09-07", "delegated_research_retrieved", "Supports adaptive-assessment precedent; no future board authority is predicted."],
    ["GFS-015", "Great Lakes St. Lawrence Governors & Premiers — Agreement and Compact", "https://www.gsgp.org/projects/water-management/great-lakes-agreement-and-compact", "binational_state_provincial_source", "state/provincial water-management framework and implementation context", "eight states and two provinces", "2026-09-07", "delegated_research_retrieved", "Supports current framework precedent; no future legal change is inferred."],
    ["GFS-016", "Folke et al. — Adaptive Governance of Social-Ecological Systems", "https://doi.org/10.1146/annurev.energy.30.050504.144511", "peer_reviewed_governance_literature", "multi-level networks, learning, bridging organizations, and adaptive co-management", "general / social-ecological systems", "2026-09-07", "delegated_research_retrieved", "Literature basis for scenario construction, not a Western Basin forecast."],
    ["GFS-017", "Chaffin, Gosnell & Cosens — Adaptive Governance in the Anthropocene", "https://www.ecologyandsociety.org/vol19/iss3/art56/", "peer_reviewed_governance_literature", "adaptive governance under complexity and uncertainty", "general / social-ecological systems", "2026-09-07", "delegated_research_retrieved", "Literature basis; institutionalization remains an uncertainty, not a predicted outcome."],
    ["GFS-018", "Carlisle & Gruby — Polycentric Systems of Governance", "https://doi.org/10.1111/psj.12212", "peer_reviewed_governance_literature", "polycentricity, semiautonomous centers, redundancy, and conflict resolution", "general governance systems", "2026-09-07", "delegated_research_retrieved", "Supports Scenario B design; multiplicity does not guarantee resilience or effectiveness."],
    ["GFS-019", "Weber & Khademian — Wicked Problems, Knowledge Challenges", "https://doi.org/10.1111/j.1540-6210.2007.00866.x", "peer_reviewed_governance_literature", "network knowledge transfer, integration, and collaborative capacity", "general public administration", "2026-09-07", "delegated_research_retrieved", "Supports network friction and knowledge-integration assumptions; not a local forecast."],
]

ASSUMPTION_COLUMNS = [
    "assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption",
    "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status", "classification", "notes",
]
ACTOR_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "actor_id", "actor_name", "actor_type",
    "current_fact", "scenario_assumption", "scenario_consequence", "future_role", "change_type",
    "authority_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes",
]
AUTHORITY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "authority_id", "actor_id", "domain_system",
    "authority_or_role", "current_fact", "scenario_assumption", "scenario_consequence", "future_authority_pattern",
    "legal_status", "human_decision_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes",
]
DEPENDENCY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "dependency_id", "system_a", "system_b", "dependency_type",
    "current_fact", "scenario_assumption", "scenario_consequence", "dependency_state", "coordination_implication",
    "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes",
]
COORDINATION_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "mechanism_id", "mechanism_type", "mechanism_name",
    "current_fact", "scenario_assumption", "scenario_consequence", "future_mechanism", "mechanism_character",
    "authority_boundary", "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes",
]
UNCERTAINTY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "uncertainty_id", "subject_type", "subject_id", "domain_system",
    "uncertainty_category", "current_fact", "scenario_assumption", "scenario_consequence", "uncertainty_state",
    "assumption_id", "current_fact_source_id", "source_id", "reality_status", "canon_status", "notes",
]
COMPARISON_COLUMNS = [
    "scenario_id", "scenario", "horizon", "scenario_family", "authority_clarity", "cross_jurisdiction_coordination",
    "data_interoperability", "monitoring_to_decision_linkage", "public_private_coordination", "binational_coordination",
    "tribal_consultation_and_participation", "funding_alignment", "adaptive_management", "decision_latency",
    "institutional_redundancy", "enforcement_alignment", "voluntary_program_coordination", "emergency_coordination",
    "ecological_infrastructure_governance", "technology_governance", "notes",
]

# These are deliberate scenario assumptions, not predictions of law or institutional behavior.
ASSUMPTION_TOPICS = {
    "A": [
        ("data_and_sensors", "Interoperable public environmental and infrastructure data standards expand across selected basin products.", "GFS-006"),
        ("coordination", "Federal, state, local, tribal, and binational actors use clearer cross-system review protocols while retaining distinct authority.", "GFS-011"),
        ("adaptive_management", "Nutrient, water, ecology, and climate programs use recurring evidence review and adjustment cycles across selected interfaces.", "GFS-014"),
        ("binational_and_tribal", "Great Lakes and treaty-related coordination becomes more legible in planning and monitoring without merging sovereign nations or creating a single basin government.", "GFS-012"),
        ("funding", "Selected resilience-finance programs align water, ecological-infrastructure, and infrastructure-maintenance priorities more consistently.", "GFS-008"),
        ("public_private", "Public agencies and private operators use stronger reporting and continuity agreements while regulation, ownership, and operation remain distinct.", "GFS-007"),
        ("ecological_infrastructure", "Wetlands, riparian systems, and other ecological infrastructure are treated as maintained cross-system assets in selected planning processes.", "GFS-009"),
        ("technology_and_learning", "Environmental analytics, bounded AI recommendations, digital model exchange, and institutional after-action learning improve selected decision handoffs without transferring legal authority to software.", "GFS-004"),
    ],
    "B": [
        ("standards_and_agreements", "Issue-specific agreements, common standards, and shared-data practices expand without a single regional data owner or government.", "GFS-018"),
        ("distributed_stewardship", "Observation, reporting, and analysis remain distributed among agencies, municipalities, tribes, and operators, with uneven interoperability.", "GFS-005"),
        ("domain_networks", "Water, nutrients, ecology, energy, freight, health, and hazards coordinate through overlapping networks whose coverage differs by domain.", "GFS-017"),
        ("binational_and_tribal", "Selective cross-border and nation-specific participation expands through agreements and consultation, while sovereign authority remains distinct.", "GFS-015"),
        ("mixed_mechanisms", "Voluntary programs, mandatory requirements, market structures, and operator practices coexist with domain-specific handoffs.", "GFS-007"),
        ("operator_continuity", "Public and private operators improve continuity information and fallback arrangements without collapsing regulation, operation, or ownership.", "GFS-007"),
        ("redundancy_and_friction", "Institutional redundancy provides alternative paths but also creates duplication, negotiation costs, structural friction, and incompatible interpretations.", "GFS-018"),
        ("adaptive_review", "Adaptive review is durable in some domains and episodic in others because capacity, funding, and local priorities remain uneven.", "GFS-009"),
    ],
    "C": [
        ("seams", "Environmental, infrastructure, and climate pressures make jurisdictional seams more consequential while governments and capable institutions continue to operate.", "GFS-017"),
        ("data_divergence", "Data standards, access rules, and model lineages diverge across selected jurisdictions and operators.", "GFS-005"),
        ("funding", "Funding and maintenance for cross-system adaptation become uneven, with durable projects in some places and deferred interfaces in others.", "GFS-008"),
        ("public_private", "Public/private coordination becomes harder where reporting, liability, continuity, or maintenance expectations do not align.", "GFS-007"),
        ("binational_and_tribal", "Cross-border decisions and some consultation pathways slow or become selective; no treaty amendment, sovereignty change, or new jurisdiction is assumed.", "GFS-013"),
        ("monitoring_to_action", "Monitoring remains strong in selected institutions but is less consistently connected to shared decisions, funding, or enforcement.", "GFS-006"),
        ("compound_stress", "Compound environmental and infrastructure stresses increase decision latency and responsibility misalignment at institutional seams.", "GFS-009"),
        ("institutional_continuity", "Highly capable individual institutions and local programs persist even as basin-wide coordination becomes less coherent; collapse is not assumed.", "GFS-010"),
    ],
}

ACTOR_IDS = [
    "GA-001", "GA-002", "GA-003", "GA-004", "GA-005", "GA-006", "GA-007", "GA-012", "GA-017", "GA-018",
    "GA-019", "GA-020", "GA-021", "GA-022", "GA-023", "GA-024", "GA-026", "GA-030", "GA-035", "GA-038",
]
AUTHORITY_IDS = [
    "AUTH-001", "AUTH-005", "AUTH-008", "AUTH-014", "AUTH-017", "AUTH-020", "AUTH-022", "AUTH-031",
    "AUTH-037", "AUTH-049", "AUTH-053", "AUTH-055", "AUTH-064", "AUTH-076", "AUTH-095",
]

COMPARISON_LEVELS = {
    "A": {
        "authority_clarity": ("clearer_interfaces", "clear distributed interfaces"),
        "cross_jurisdiction_coordination": ("stronger_protocols", "institutionalized_review"),
        "data_interoperability": ("expanding_shared_standards", "mature_selected_standards"),
        "monitoring_to_decision_linkage": ("stronger_selected_links", "routine_review_links"),
        "public_private_coordination": ("stronger_compacts", "mature_interface_rules"),
        "binational_coordination": ("stronger_implementation_links", "durable_implementation_network"),
        "tribal_consultation_and_participation": ("expanded_consultation_and_data_roles", "institutionalized_participation_without_sovereignty_merge"),
        "funding_alignment": ("more_aligned_priority_funding", "multi-year_alignment_routines"),
        "adaptive_management": ("recurring_review_cycles", "institutionalized_learning_cycles"),
        "decision_latency": ("reduced_in_priority_chains", "shorter_selected_handoffs"),
        "institutional_redundancy": ("planned_alternatives", "layered_redundancy"),
        "enforcement_alignment": ("clearer_referral_and_compliance_links", "more_consistent_referral_protocols"),
        "voluntary_program_coordination": ("better_linked_incentives_and_requirements", "coordinated_but_distinct_mechanisms"),
        "emergency_coordination": ("integrated_situational_awareness", "institutional_memory_and_joint_protocols"),
        "ecological_infrastructure_governance": ("selected_assets_in_planning", "maintained_governed_asset_class"),
        "technology_governance": ("bounded_explainable_decision_support", "auditable_human_supervision"),
    },
    "B": {
        "authority_clarity": ("domain_specific_clarity", "plural_negotiated_clarity"),
        "cross_jurisdiction_coordination": ("issue_specific_networks", "durable_overlapping_networks"),
        "data_interoperability": ("uneven_federated_exchange", "multiple_standards_with_bridges"),
        "monitoring_to_decision_linkage": ("negotiated_by_domain", "multiple_local_and_regional_paths"),
        "public_private_coordination": ("operator_agreements", "networked_operator_compacts"),
        "binational_coordination": ("selective_agreements", "durable_selective_links"),
        "tribal_consultation_and_participation": ("nation_specific_consultation", "expanded_but_nonuniform_participation"),
        "funding_alignment": ("program_specific_alignment", "multiple_funding_channels"),
        "adaptive_management": ("uneven_domain_review", "mature_but_variable_review"),
        "decision_latency": ("variable_by_domain", "negotiation_cost_persists"),
        "institutional_redundancy": ("fallback_paths_with_friction", "redundancy_and_duplication"),
        "enforcement_alignment": ("selective_referral_links", "jurisdiction_specific_enforcement"),
        "voluntary_program_coordination": ("mixed_mechanisms", "coexisting_mechanisms"),
        "emergency_coordination": ("networked_warning_and_fallback", "multiple_response_networks"),
        "ecological_infrastructure_governance": ("project_specific_stewardship", "distributed_maintenance"),
        "technology_governance": ("federated_model_and_data_rules", "plural_audit_and_access_rules"),
    },
    "C": {
        "authority_clarity": ("seams_more_consequential", "misaligned_responsibility"),
        "cross_jurisdiction_coordination": ("slower_cross_system_handoffs", "patchy_basin_coherence"),
        "data_interoperability": ("diverging_standards", "persistent_incompatible_lineages"),
        "monitoring_to_decision_linkage": ("strong_in_places_weakly_connected", "uneven_action_connection"),
        "public_private_coordination": ("harder_reporting_and_continuity", "persistent_interface_conflict"),
        "binational_coordination": ("slower_selective_links", "patchy_cross_border_coordination"),
        "tribal_consultation_and_participation": ("uneven_opportunities", "selective_participation_paths"),
        "funding_alignment": ("uneven_and_deferred", "patchwork_maintenance"),
        "adaptive_management": ("episodic_and_capacity_bound", "inconsistent_learning"),
        "decision_latency": ("longer_at_seams", "persistent_latency"),
        "institutional_redundancy": ("uneven_local_redundancy", "patchy_redundancy"),
        "enforcement_alignment": ("referral_gaps_at_seams", "uneven_compliance_alignment"),
        "voluntary_program_coordination": ("less_coherent_program_mix", "fragmented_program_mix"),
        "emergency_coordination": ("slower_compound_event_coordination", "uneven_response_networks"),
        "ecological_infrastructure_governance": ("uneven_project_stewardship", "selective_maintained_assets"),
        "technology_governance": ("contested_models_and_access", "divergent_model_governance"),
    },
}
COMPARISON_DIMENSIONS = list(COMPARISON_LEVELS["A"])


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def status_prefix(kind: str, text: str) -> str:
    return f"{kind}: {text}"


def trajectory(scenario: str, horizon: int) -> str:
    if scenario == "A" and horizon == 2050:
        return "By 2050, transition toward integrated basin protocols is underway: selected data, finance, warning, and review interfaces are stronger while legal sovereignty remains distributed."
    if scenario == "A":
        return "By 2075, selected basin protocols and learning routines are mature enough to connect many systems, but institutional diversity, private operation, and tribal sovereignty remain explicit."
    if scenario == "B" and horizon == 2050:
        return "By 2050, issue-specific agreements and standards improve selected handoffs; authority remains distributed and coordination varies by domain."
    if scenario == "B":
        return "By 2075, a durable federation of overlapping networks provides fallback and cross-checking, while negotiated standards, duplication, and friction remain structural."
    if horizon == 2050:
        return "By 2050, coordination gaps widen at selected seams under compound pressures, but capable agencies, utilities, operators, and local programs continue to function."
    return "By 2075, divergence is entrenched across selected data, funding, and coordination interfaces; institutions remain capable in places without basin-wide coherence or assumed collapse."


def scenario_consequence(scenario: str, horizon: int, domain: str, subject: str = "") -> str:
    phase = "intermediate institutional trajectory" if horizon == 2050 else "matured or diverged institutional state"
    if scenario == "A":
        return status_prefix("SCENARIO CONSEQUENCE", f"{phase}: {domain} gains a more legible cross-system handoff, shared review, or finance interface; the underlying actor's legal or ownership boundary is retained.")
    if scenario == "B":
        return status_prefix("SCENARIO CONSEQUENCE", f"{phase}: {domain} is handled through domain-specific networks, agreements, standards, or operator structures; redundancy and local autonomy coexist with negotiation friction.")
    return status_prefix("SCENARIO CONSEQUENCE", f"{phase}: {domain} experiences slower or less aligned handoffs at selected seams while strong individual institutions can continue operating; the scenario does not imply universal failure.")


def source_for_domain(domain: str, scenario: str) -> str:
    d = domain.lower()
    if "tribal" in d or "ecology" in d:
        return "GFS-003" if "tribal" in d else "GFS-009"
    if "binational" in d or "water" in d:
        return "GFS-002"
    if "data" in d or "sensor" in d or "technology" in d:
        return "GFS-004" if scenario == "A" else "GFS-005"
    if "public" in d or "private" in d or "energy" in d:
        return "GFS-007"
    if "fund" in d or "emergency" in d or "climate" in d:
        return "GFS-008"
    if "adaptive" in d or "monitor" in d:
        return "GFS-009"
    return SCENARIOS_META[scenario]["source"]


def build_tables() -> tuple[list[list[str]], list[list[str]], list[list[str]], list[list[str]], list[list[str]], list[list[str]], list[list[str]]]:
    actors = {r["actor_id"]: r for r in read_rows(ANALYSIS / "governance_actors.csv")}
    authorities = {r["authority_id"]: r for r in read_rows(ANALYSIS / "governance_authorities.csv")}
    deps = {r["dependency_id"]: r for r in read_rows(ANALYSIS / "governance_dependency_register.csv")}
    mechanisms = {r["mechanism_id"]: r for r in read_rows(ANALYSIS / "governance_coordination_mechanisms.csv")}
    uncertainties = {r["uncertainty_id"]: r for r in read_rows(ANALYSIS / "governance_uncertainty_register.csv")}
    assumptions: list[list[str]] = []
    assumption_lookup: dict[str, dict[str, str]] = {}
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            for i, (domain, text, source_id) in enumerate(ASSUMPTION_TOPICS[scenario], 1):
                if horizon == 2050:
                    wording = f"{text} This is the {scenario} scenario's intermediate 2050 trajectory, not a legal forecast."
                else:
                    wording = f"{text} By 2075, this condition is treated as a {('mature' if scenario != 'C' else 'entrenched')} scenario state, not a legal forecast."
                aid = f"GSA-{sid}-{i:02d}"
                row = [aid, sid, meta["name"], horizon, domain, wording, meta["basis"], source_id, "high" if scenario == "C" and i in (1, 2, 6, 7) else "moderate", "fictional", "scenario", "SCENARIO ASSUMPTION", "Qualitative assumption; no probability, composite governance score, or deterministic institutional response is assigned."]
                assumptions.append(row)
                assumption_lookup[aid] = {"text": wording, "source": source_id}

    actor_states: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            aids = [f"GSA-{sid}-{i:02d}" for i in range(1, 9)]
            for i, actor_id in enumerate(ACTOR_IDS, 1):
                actor = actors[actor_id]
                aid = aids[(i - 1) % 8]
                name = actor["name"]
                if actor_id == "GA-021":
                    role = "GLIFWC remains an intertribal participant; stronger or weaker consultation and data visibility are explored without assigning it sovereign status or new Western Basin jurisdiction."
                elif actor_id in {"GA-022", "GA-023"}:
                    role = "The nation remains a distinct sovereign actor; consultation, participation, or data partnership may vary by scenario without inventing territory, permit authority, or enforcement authority."
                elif actor["actor_type"] in {"private_operator", "public_utility"}:
                    role = "The actor retains its current ownership/operation boundary while its reporting, continuity, and coordination interface changes under the scenario."
                elif scenario == "A":
                    role = "The actor retains its current role and participates in stronger cross-system protocols and evidence review where relevant."
                elif scenario == "B":
                    role = "The actor retains its current role and joins issue-specific networks or agreements where relevant; participation is not universal."
                else:
                    role = "The actor retains its current role, but cross-system handoffs and coordination opportunities are uneven under pressure."
                change = "coordination_interface_strengthened" if scenario == "A" else "domain_networked" if scenario == "B" else "coordination_interface_contested"
                if horizon == 2075:
                    change += "_matured" if scenario in {"A", "B"} else "_entrenched"
                current = status_prefix("CURRENT FACT (2026 baseline)", actor["operational_or_authority_summary"])
                assumption = status_prefix("SCENARIO ASSUMPTION", assumption_lookup[aid]["text"])
                consequence = scenario_consequence(scenario, horizon, f"the {name} institutional interface")
                boundary = "Current legal, sovereign, ownership, and operational boundaries remain distinct; coordination is not itself binding authority. AI or automated analysis, if present, can advise or prioritize but cannot replace legal or human decision authority; automated monitoring is not automatic enforcement. AI recommendation ≠ legal authority; automated monitoring ≠ automatic enforcement; algorithmic prioritization ≠ final public decision; sensor coverage ≠ institutional capacity."
                actor_states.append([f"GAS-{sid}-{i:03d}", sid, meta["name"], horizon, actor_id, name, actor["actor_type"], current, assumption, consequence, role, change, boundary, aid, actor["source_id"], assumption_lookup[aid]["source"], "fictional", "scenario", "Future actor state is a scenario delta over the accepted 2026 actor registry; it is not a new legal classification."])

    authority_states: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            aids = [f"GSA-{sid}-{i:02d}" for i in range(1, 9)]
            for i, authority_id in enumerate(AUTHORITY_IDS, 1):
                auth = authorities[authority_id]
                aid = aids[(i - 1) % 8]
                current = status_prefix("CURRENT FACT (2026 baseline)", f"{auth['actor_id']} has the recorded {auth['authority_or_role']} role in {auth['domain_system']}; binding status is {auth['binding_or_nonbinding']}.")
                assumption = status_prefix("SCENARIO ASSUMPTION", assumption_lookup[aid]["text"])
                pattern = "stronger protocol around distributed authority" if scenario == "A" else "agreement-mediated and domain-specific coordination around distributed authority" if scenario == "B" else "distributed authority with slower or less aligned handoffs"
                consequence = scenario_consequence(scenario, horizon, f"{auth['authority_or_role']} in {auth['domain_system']}")
                human = "Any model, sensor, AI recommendation, automated screening, or algorithmic prioritization remains advisory or administrative support; the named legal/public/operational actor retains final human decision authority."
                authority_states.append([f"GAU-{sid}-{i:03d}", sid, meta["name"], horizon, authority_id, auth["actor_id"], auth["domain_system"], auth["authority_or_role"], current, assumption, consequence, pattern, "CURRENT AUTHORITY RETAINED; SCENARIO COORDINATION CHANGE", human, aid, auth["source_id"], assumption_lookup[aid]["source"], "fictional", "scenario", "Scenario coordination does not amend statute, treaty, compact, permit, sovereignty, ownership, or operating authority."])

    dependency_states: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            aids = [f"GSA-{sid}-{i:02d}" for i in range(1, 9)]
            for i, dep_id in enumerate(deps, 1):
                dep = deps[dep_id]
                aid = aids[(i - 1) % 8]
                current = status_prefix("CURRENT FACT (2026 baseline)", f"{dep['system_a']} ↔ {dep['system_b']} is recorded as {dep['dependency_type']} through {dep['coordination_mechanism']}; this is a {dep['documented_or_inferred']} relationship.")
                assumption = status_prefix("SCENARIO ASSUMPTION", assumption_lookup[aid]["text"])
                state = "shared_review_and_protocol_strengthened" if scenario == "A" else "issue_specific_exchange_and_fallback" if scenario == "B" else "handoff_slower_or_less_aligned"
                consequence = scenario_consequence(scenario, horizon, f"{dep['system_a']} to {dep['system_b']} dependency")
                implication = "Dependency is not converted into a governance score, failure probability, or universal control claim."
                if dep["dependency_type"] == "binational_dependency":
                    implication = "Cross-border coordination remains an interface among existing institutions; no treaty amendment or new binational legal authority is assumed."
                elif dep["dependency_type"] == "public_private_dependency":
                    implication = "Regulation, public finance, private operation, and asset ownership remain separate roles."
                elif dep["dependency_type"] == "monitoring-without-control":
                    implication = "Monitoring can inform decisions without becoming regulation, enforcement, or operation."
                dependency_states.append([f"GAD-{sid}-{i:03d}", sid, meta["name"], horizon, dep_id, dep["system_a"], dep["system_b"], dep["dependency_type"], current, assumption, consequence, state, implication, aid, dep["source_id"], assumption_lookup[aid]["source"], "fictional", "scenario", "Future dependency state preserves the accepted Phase 10B interface and adds only a qualitative scenario consequence."])

    coordination_states: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            aids = [f"GSA-{sid}-{i:02d}" for i in range(1, 9)]
            for i, mechanism_id in enumerate(mechanisms, 1):
                mech = mechanisms[mechanism_id]
                aid = aids[(i - 1) % 8]
                current = status_prefix("CURRENT FACT (2026 baseline)", f"{mech['mechanism_name']} is recorded as a {mech['mechanism_type']} with {mech['mandatory_or_voluntary']} character.")
                assumption = status_prefix("SCENARIO ASSUMPTION", assumption_lookup[aid]["text"])
                future = "interoperable_iterative_mechanism" if scenario == "A" else "agreement_mediated_domain_mechanism" if scenario == "B" else "available_but_uneven_mechanism"
                consequence = scenario_consequence(scenario, horizon, f"{mech['mechanism_name']} coordination")
                character = "stronger shared protocol, iterative review, and explicit human handoff" if scenario == "A" else "overlapping agreements, standards, and fallback paths with negotiation friction" if scenario == "B" else "uneven access, slower handoff, and less coherent voluntary coordination"
                boundary = "The mechanism cannot by itself create a single basin government, new sovereign territory, permit jurisdiction, enforcement power, or automatic legal decision."
                coordination_states.append([f"GAC-{sid}-{i:03d}", sid, meta["name"], horizon, mechanism_id, mech["mechanism_type"], mech["mechanism_name"], current, assumption, consequence, future, character, boundary, aid, mech["source_id"], assumption_lookup[aid]["source"], "fictional", "scenario", "Mandatory, mixed, and voluntary mechanisms remain distinguishable in the future layer."])

    uncertainty_states: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            aids = [f"GSA-{sid}-{i:02d}" for i in range(1, 9)]
            for i, uncertainty_id in enumerate(uncertainties, 1):
                item = uncertainties[uncertainty_id]
                aid = aids[(i - 1) % 8]
                current = status_prefix("CURRENT FACT (2026 baseline)", item["statement"])
                assumption = status_prefix("SCENARIO ASSUMPTION", assumption_lookup[aid]["text"])
                if uncertainty_id == "UNC-015":
                    consequence = status_prefix("SCENARIO CONSEQUENCE", "The Toledo intake-coordinate discrepancy remains UNRESOLVED and is not used to assign future governance geography.")
                elif uncertainty_id == "UNC-016":
                    consequence = status_prefix("SCENARIO CONSEQUENCE", "Great Black Swamp remains C — HOLD / noncanonical; no future governance polygon is derived from it.")
                elif scenario == "A":
                    consequence = scenario_consequence(scenario, horizon, "the inherited uncertainty")
                elif scenario == "B":
                    consequence = scenario_consequence(scenario, horizon, "the inherited uncertainty")
                else:
                    consequence = scenario_consequence(scenario, horizon, "the inherited uncertainty")
                state = "made_explicit_in_adaptive_review" if scenario == "A" else "distributed_and_compared_across_networks" if scenario == "B" else "compounded_at_seams_without_equating_unknown_with_failure"
                uncertainty_states.append([f"GAUQ-{sid}-{i:03d}", sid, meta["name"], horizon, uncertainty_id, item["subject_type"], item["subject_id"], item["domain_system"], item["uncertainty_category"], current, assumption, consequence, state, aid, item["source_id"], assumption_lookup[aid]["source"], "fictional", "scenario", "Uncertainty state carries the accepted 2026 limitation forward; it does not convert a gap into risk, failure, or absence."])

    comparisons: list[list[str]] = []
    for scenario, meta in SCENARIOS_META.items():
        for horizon in HORIZONS:
            sid = f"{scenario}{horizon}"
            values = [COMPARISON_LEVELS[scenario][d][0 if horizon == 2050 else 1] for d in COMPARISON_DIMENSIONS]
            comparisons.append([sid, meta["name"], horizon, meta["name"], *values, "Qualitative comparison only; dimensions are not aggregated, ranked, or converted into a governance score."])
    return assumptions, actor_states, authority_states, dependency_states, coordination_states, uncertainty_states, comparisons


def load_context():
    if gpd is None or not GPKG.exists():
        return None
    try:
        layers = {}
        for layer in ("water_watersheds_huc8", "water_lake_erie", "water_current_wetlands_25ac"):
            layers[layer] = gpd.read_file(GPKG, layer=layer)
        return layers
    except Exception:
        return None


def draw_network_panel(ax, scenario: str, horizon: int, y0: float) -> None:
    colors = {"A": "#4f927b", "B": "#c08a42", "C": "#a8524d"}
    names = {"A": "Integrated Basin", "B": "Federated / Networked", "C": "Fragmented / Contested"}
    color = colors[scenario]
    ax.add_patch(FancyBboxPatch((0.0, y0), 1.0, 0.275, boxstyle="round,pad=0.008", facecolor=color, alpha=0.10, edgecolor=color, linewidth=1.2, transform=ax.transAxes))
    ax.text(0.035, y0 + 0.245, f"{scenario} — {names[scenario]}", transform=ax.transAxes, fontsize=9.0, weight="bold", color=color, va="top")
    ax.text(0.97, y0 + 0.245, "2050 transition" if horizon == 2050 else "2075 mature/diverged", transform=ax.transAxes, fontsize=6.5, color="#3f4645", ha="right", va="top")
    xs = [0.12, 0.34, 0.56, 0.78]
    labels = ["science / data", "public authority", "tribal / nation", "operator / finance"]
    linestyle = "-" if scenario == "A" else ("--" if scenario == "B" else ":")
    alpha = 0.92 if scenario == "A" else (0.72 if scenario == "B" else 0.55)
    for x1, x2 in zip(xs[:-1], xs[1:]):
        ax.plot([x1, x2], [y0 + 0.135, y0 + 0.135], transform=ax.transAxes, color=color, linewidth=1.6, linestyle=linestyle, alpha=alpha)
    for x, label in zip(xs, labels):
        ax.scatter([x], [y0 + 0.135], transform=ax.transAxes, s=55, color=color, edgecolor="#f1eadc", linewidth=0.8, zorder=4)
        ax.text(x, y0 + 0.055, label, transform=ax.transAxes, fontsize=5.4, color="#3f4645", ha="center", va="top")


def render_map(year: int, path: Path) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "phase10c-governance-futures"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.53, 0.78], facecolor="#e9e1ce")
    context = load_context()
    if context:
        context["water_watersheds_huc8"].boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
        context["water_lake_erie"].plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
        context["water_current_wetlands_25ac"].plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.35)
        ax.set_xlim(-84.55, -82.55)
        ax.set_ylim(40.90, 42.15)
        ax.text(-84.48, 42.08, "Western Basin regional context", fontsize=10, color="#17384b", weight="bold")
        ax.text(-84.48, 41.99, "Physical layers are context only; governance networks at right are schematic.", fontsize=6.8, color="#3f4645")
    else:
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.5, 0.55, "Western Basin\nregional context", ha="center", va="center", fontsize=18, color="#17384b", weight="bold")
    ax.set_axis_off()
    right = fig.add_axes([0.61, 0.06, 0.36, 0.88])
    right.set_axis_off()
    map_id = "34" if year == 2050 else "34b"
    right.text(0.02, 0.985, f"MAP {map_id} — GOVERNANCE FUTURES, {year}", va="top", fontsize=13.2, weight="bold", color="#17384b")
    right.text(0.02, 0.925, "Three qualitative alternatives for authority interfaces, information relationships, cross-system dependencies, and coordination. Markers and links are schematic; they are not jurisdiction boundaries, headquarters, ownership maps, or legal forecasts.", va="top", fontsize=7.4, color="#3f4645", linespacing=1.27)
    for scenario, y0 in zip(("A", "B", "C"), (0.63, 0.335, 0.04)):
        draw_network_panel(right, scenario, year, y0)
    right.text(0.02, 0.005, "BOUNDARIES  Current 2026 authority remains separate from scenario deltas. Regulation ≠ operation; public finance ≠ public ownership; market operation ≠ asset ownership. GLIFWC remains an intertribal body and distinct nations remain distinct actors. AI recommendation ≠ legal authority; automated monitoring ≠ automatic enforcement. Great Black Swamp: C — HOLD / noncanonical. Toledo intake-coordinate discrepancy: UNRESOLVED.", va="bottom", fontsize=6.5, color="#3f4645", linespacing=1.25)
    fig.savefig(path.with_suffix(".png"), dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix(".svg"), facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg = path.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def render_comparison(rows: list[list[str]]) -> None:
    plt.rcParams["svg.hashsalt"] = "phase10c-governance-futures"
    values = [r[4:-1] for r in rows]
    labels = [f"{r[0]} — {r[1]}" for r in rows]
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#f1eadc")
    ax.set_facecolor("#f1eadc")
    ax.imshow([[{"low": 0, "moderate": 1, "high": 2}.get(v, 1) for v in row] for row in values], cmap="YlGnBu", vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(COMPARISON_DIMENSIONS)), [d.replace("_", "\n") for d in COMPARISON_DIMENSIONS], rotation=55, ha="right", fontsize=6.5)
    ax.set_yticks(range(len(labels)), labels, fontsize=7)
    # Overlay text because values are qualitative states, not numeric scores.
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            ax.text(j, i, value.replace("_", " "), ha="center", va="center", fontsize=5.6, color="#17384b")
    ax.set_title("Phase 10C — Qualitative Governance Futures Comparison", loc="left", fontsize=14, weight="bold", color="#17384b")
    ax.text(0, 1.03, "Dimensions are shown side by side and are not aggregated, ranked, or converted into a composite governance score.", transform=ax.transAxes, fontsize=7.5, color="#3f4645")
    ax.tick_params(length=0)
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.savefig(COMPARISON_PNG, dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(COMPARISON_SVG, facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    COMPARISON_SVG.write_text("\n".join(line.rstrip() for line in COMPARISON_SVG.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def report_texts() -> dict[str, str]:
    source_report = """# Phase 10C Governance Futures Sources

This scenario layer reuses the accepted Phase 10A/10B current institutional records and adds bounded external context for scenario construction. The Great Lakes Commission describes an interstate compact agency that brings actors together around issues no single community, state, province, or nation can tackle alone.[1] The Governors & Premiers water-management page describes a legal and policy framework for eight states and two provinces; this is treated as precedent for coordination, not as a forecast of a new Western Basin government.[2]

GLIFWC's own description supports its status as an intertribal body serving member Ojibwe tribes and providing natural-resource management, conservation enforcement, legal/policy analysis, and public information; the future layer does not convert that role into a single sovereign actor or new Western Basin jurisdiction.[3]

Canada's official Great Lakes Water Quality Agreement materials provide direct current context for the Agreement's objectives, annexes, implementation, reporting, consultation, public engagement, and adaptive-management language.[11][12] The IJC materials provide direct current context for case-by-case boundary-water responsibilities, nonbinding recommendations, project approvals, and Great Lakes adaptive-assessment boards.[13][14] The Governors & Premiers Agreement and Compact page provides additional state/provincial implementation precedent.[15]

NIST's AI Risk Management Framework is voluntary and developed with public and private sectors; it is used here only to bound future decision-support, provenance, explanation, and human-governance assumptions.[4] NIST's Privacy Framework is a voluntary privacy-risk management tool and supports the possibility of privacy-aware federated exchange without a personal-data model.[5]

NOAA IOOS provides a precedent for integrated observing data and predictive tools across coasts and Great Lakes; the scenario layer does not infer complete coverage, automatic enforcement, or legal authority from sensing.[6] DOE describes grid modernization as an ecosystem of asset owners, service providers, and public officials and explicitly discusses public/private coordination; the future layer preserves operation, regulation, ownership, and finance as separate roles.[7]

FEMA hazard-mitigation planning and USGS Climate Adaptation Science Centers provide planning, partnership, data, and adaptation-learning context.[8][9] Ostrom's social-ecological-systems framework supports analyzing multiple interacting governance levels without assuming that one universal institutional arrangement is always superior.[10]

Adaptive-governance literature grounds the scenario distinction between bridging, learning, and institutionalization as analytical possibilities rather than predictions.[16][17] Polycentricity literature supports Scenario B's semiautonomous centers, redundancy, conflict resolution, and institutional fit without treating multiplicity as guaranteed success.[18][19]

These sources ground mechanisms and analytical precedent only. They do not establish exact 2050/2075 law, institutional behavior, funding totals, sensor counts, response times, probabilities, or governance rankings.
"""
    assumptions_report = """# Phase 10C Governance Futures Assumption Ledger

The ledger contains six scenario-horizon states: A2050, A2075, B2050, B2075, C2050, and C2075. Each row is explicitly classified as SCENARIO ASSUMPTION, has `reality_status=fictional` and `canon_status=scenario`, and points to a scenario source. The accepted 2026 institutional baseline is not appended to these rows.

A — Integrated Basin Governance strengthens interoperability, review, resilience finance, ecological-infrastructure governance, and institutional learning while retaining federal, state, local, tribal, private, and binational distinctions.[1][2][3] This is integration without a single Western Basin government; interoperable observing and public/private technology precedent informs the scenario.[6][7] Resilience finance, adaptation partnerships, and bounded decision support inform the scenario without making it a forecast.[4][8][9]

B — Federated / Networked Governance is a distinct future, not a midpoint. Its organizing logic is overlapping issue-specific agreements, standards, local stewardship, fallback paths, and operator networks.[1][2][5] It expects both resilience from redundancy and friction from duplication, negotiated access, and multiple interpretations.[7][10]

C — Fragmented / Contested Governance is a bounded stress-test. Seams, divergent data standards, uneven funding, slower cross-border decisions, and weaker monitoring-to-action links become more consequential, while highly capable institutions can persist.[3][8][9] It does not assume collapse, corruption, authoritarianism, partisan causation, or universal failure.[10]

2050 is modeled as an intermediate trajectory: protocols are emerging, institutional choices are still path-dependent, and implementation is selective. 2075 is modeled as a matured or diverged state: A has institutionalized selected basin routines, B has durable overlapping networks with structural friction, and C has entrenched patchwork coordination. The two horizons are therefore not a simple intensity scale.[1][9][10]

The direct GLWQA and IJC materials anchor current agreement, participation, decision, and adaptive-assessment boundaries.[11][12][13] The IJC boards and Governors & Premiers implementation materials add current adaptive and state/provincial precedent.[14][15][16] The adaptive-governance, polycentricity, and network-capacity literature grounds the alternative mechanisms without predicting their realization.[17][18][19]

No assumption predicts treaty amendment, election outcome, party control, precise future jurisdiction, tribal land transfer, permit jurisdiction, enforcement authority, public ownership, private ownership, or exact institutional performance. Future legal authority remains an explicit boundary condition rather than a forecast.
"""
    consistency_report = """# Phase 10C Governance Futures Consistency

The future tables are separate from the accepted 2026 Phase 10A/10B tables. Every actor, authority, dependency, coordination, and uncertainty state carries a baseline reference, a CURRENT FACT (2026 baseline) field, a SCENARIO ASSUMPTION field, a SCENARIO CONSEQUENCE field, a valid assumption ID, a current-fact source ID, and a scenario-source ID.

The actor-state layer uses valid Phase 10A actor IDs. The authority-state layer uses valid Phase 10A authority IDs and keeps legal status as CURRENT AUTHORITY RETAINED; SCENARIO COORDINATION CHANGE. The dependency-state layer uses valid Phase 10B dependency IDs, and the coordination-state layer uses valid Phase 10B mechanism IDs.

GLIFWC remains an intertribal body. Distinct sovereign nations remain distinct actors. No future state creates sovereign territory, a treaty settlement, permit jurisdiction, enforcement authority, land transfer, or historical-association-to-current-authority inference. Binational coordination is represented as implementation, information, consultation, and agreement interfaces; no treaty amendment is asserted.

Public/private distinctions remain explicit: regulation is not operation, public finance is not public ownership, market operation is not asset ownership, and private operation does not eliminate public regulation. Technology is bounded: AI recommendation is not legal authority, automated monitoring is not automatic enforcement, algorithmic prioritization is not final public decision, and sensor coverage is not institutional capacity.

The inherited holds remain active in every relevant scenario: Great Black Swamp is C — HOLD / noncanonical, and the Toledo intake-coordinate discrepancy is UNRESOLVED.
"""
    findings_report = """# Phase 10C Governance Futures Findings

## A2050 — Integrated Basin Governance

SCENARIO: This is an intermediate institutional trajectory in which interoperable data, cross-system review, resilience finance, warning protocols, ecological-infrastructure planning, and public/private continuity interfaces strengthen selectively.[1][2][6] Existing legal sovereignty and actor diversity remain intact; resilience finance and adaptation partnerships inform the scenario.[7][8][9]

The principal consequence is a shorter and more legible handoff from monitoring and analysis to human institutional decisions in priority chains. It is not automatic enforcement, centralized ownership, or a single basin government.[4][6]

## A2075 — Integrated Basin Governance

SCENARIO: Selected interoperability, adaptive review, basin coordination, and institutional memory have matured into durable routines while federal, state, municipal, tribal, private, and binational institutions remain distinct.[1][2][3] This scenario uses adaptation-learning and multi-level governance precedent without treating the result as a forecast.[9][10]

The principal consequence is integrated ecological-infrastructure and infrastructure-finance governance in selected systems, with auditable decision-support and explicit human/legal authority. Diversity remains a design feature and a source of continuing negotiation.[4][7][10]

## B2050 — Federated / Networked Governance

SCENARIO: Issue-specific agreements, standards, data exchanges, and operator continuity networks improve selected handoffs without a central owner.[1][2][5] Local autonomy and multiple institutional paths are central to the scenario; the pattern follows networked public/private precedent.[7][10]

The principal consequence is graceful fallback in some domains alongside variable data lineage, duplication, and negotiation costs. B is not a midpoint between A and C; its distinctive mechanism is networked pluralism.[5][10]

## B2075 — Federated / Networked Governance

SCENARIO: Overlapping water, nutrient, ecology, energy, freight, health, hazard, and binational networks have become durable.[1][2][5] Multiple standards and local stewardship remain, producing both redundancy and friction; polycentric governance literature informs the interpretation.[7][10]

The principal consequence is a mature federation whose resilience depends on cross-checking and fallback rather than central command. Participation, access, and review remain domain-specific and nonuniform.[3][5]

## C2050 — Fragmented / Contested Governance

SCENARIO: Coordination fails to keep pace in selected interfaces as climate, infrastructure, and environmental pressures rise. Data standards diverge, funding is uneven, and monitoring is not consistently linked to shared action.[5][8][9]

The principal consequence is greater decision latency and responsibility misalignment at seams. Strong individual institutions, utilities, operators, and local programs remain possible; universal institutional failure is not assumed.[7][9][10]

## C2075 — Fragmented / Contested Governance

SCENARIO: Divergence is entrenched across selected data, finance, maintenance, consultation, and cross-border interfaces. Some institutions are highly capable, but basin-wide coherence is patchy and contested.[2][3][5] Adaptation planning and multi-level governance literature inform this stress-test without making a collapse claim.[8][9][10]

The principal consequence is a patchwork of durable local or domain capacity with slower compound-event coordination and contested definitions of environmental reality. This is a stress-test alternative, not a prediction of collapse or partisan causation.[9][10]

## Cross-system synthesis

Water and nutrient governance depend on links among monitoring, agricultural programs, regulation, treatment, ecological infrastructure, and finance. Energy, freight, and compute add public/private operator interfaces and technology-dependence boundaries.[1][6][7] Ecology, exposure, and climate systems add adaptive-learning and emergency-coordination requirements. These are qualitative interfaces, not a composite score or universal ranking.[8][9]

The tribal future remains bounded: stronger consultation, participation, monitoring partnerships, and resource-governance visibility may be explored, but GLIFWC remains intertribal and distinct sovereign nations remain distinct. The binational future may strengthen GLWQA implementation, IJC/GLC/Governors & Premiers coordination, shared data, nutrient/water-quality work, ecology, and climate adaptation without predicting treaty amendments or new legal authority.[1][2][3]

The direct GLWQA materials anchor current agreement objectives, participation, implementation, reporting, and adaptive-management boundaries.[11][12] IJC role and board materials anchor current project-approval, recommendation, and adaptive-assessment distinctions.[13][14] The Governors & Premiers implementation page adds state/provincial precedent.[15]

The technology future remains bounded: sensor networks and AI-assisted analysis may change information timing and accountability, but AI recommendation is not legal authority, automated monitoring is not automatic enforcement, algorithmic prioritization is not the final public decision, and sensor coverage is not institutional capacity.[4][5][6]

Adaptive-governance literature supports learning, bridging, and institutionalization as analytical possibilities rather than predictions.[16][17] Polycentricity and network-capacity literature support Scenario B's semiautonomous centers, redundancy, conflict resolution, and knowledge-integration tests.[18][19]
"""
    worldbuilding_report = """# Phase 10C Governance Futures — Speculative Worldbuilding

Everything in this section is SPECULATIVE WORLDBUILDING, not a scientific fact, legal forecast, or accepted canon.

- Data becomes regional power: the institution that controls timing, provenance, translation, and public explanation can shape what counts as an actionable basin condition.
- Environmental sensors reshape responsibility by making missing observations, delayed feeds, and incompatible standards visible political objects without turning coverage into capacity.
- Jurisdiction is encoded into technical standards: an API, reporting schema, model lineage rule, or access credential can become a quiet map of sovereignty and responsibility.
- Nutrient credits and water-quality markets create new public/private interfaces in which price, compliance, ecological function, and local legitimacy can diverge.
- Ecological infrastructure becomes governed capital: wetlands, riparian systems, and floodplain storage acquire maintenance budgets, performance narratives, and competing claims.
- Digital basin twins become institutional memory, but conflict follows over whose model defines environmental reality and whose uncertainty is visible.
- Automated regulatory screening accelerates triage while human veto authority becomes a constitutional feature of machine-mediated governance.
- Public/private infrastructure compacts blur the boundary between service continuity and ownership without erasing regulation.
- Institutional memory after climate disasters becomes a resource that can be shared, withheld, or encoded into procurement and planning rules.
- Basin identity competes with state, municipal, tribal, national, and operator identities; regional trust becomes infrastructure in its own right.
- Bureaucratic latency becomes a recurring antagonist to technological acceleration, especially where authority is distributed and responsibility is contested.
"""
    qa_report = """# Phase 10C Governance Futures QA

The package is qualitative scenario content for six states: A2050, A2075, B2050, B2075, C2050, and C2075. It contains 48 assumptions, 120 actor states, 90 authority states, 150 dependency states, 84 coordination states, 96 uncertainty states, six comparison rows, Maps 34/34b, and a side-by-side comparison figure.

The Python and independent R validators check schema, scenario/horizon coverage, valid Phase 10A/10B references, source references, explicit current-fact/assumption/consequence separation, fictional/scenario status, horizon divergence, Scenario B distinctness, tribal/binational boundaries, public/private role separation, technology boundaries, political negative scope, qualitative-only comparison values, map integrity, and prior freeze integrity.

The validators reject positive unsupported future sovereign territory, treaty settlement, land transfer, permit jurisdiction, enforcement authority, single-basin government, composite governance score, partisan/election content, quantitative governance claims, AI legal authority, automatic enforcement, and future rows inserted into factual tables. Boundary language explaining what is not modeled is retained.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. No Phase 11 work is included.
"""
    return {
        "governance_scenario_sources.md": source_report,
        "governance_scenario_assumptions.md": assumptions_report,
        "governance_scenario_consistency.md": consistency_report,
        "governance_scenario_findings.md": findings_report,
        "governance_scenario_worldbuilding.md": worldbuilding_report,
        "governance_scenario_qa.md": qa_report,
    }


def append_citation_blocks() -> None:
    script = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
    if not script.exists():
        return
    for name in ("governance_scenario_sources.md", "governance_scenario_assumptions.md", "governance_scenario_findings.md"):
        path = REPORTS / name
        result = subprocess.run(["python", str(script), "render", "--style", "markdown", "--cited-in", str(path)], capture_output=True, text=True, check=True)
        base = re.sub(r"(\])\s+(?=[A-Z])", r"\1\n", path.read_text(encoding="utf-8"))
        path.write_text(base.rstrip() + "\n\n" + result.stdout.strip() + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for path in (ANALYSIS, NETWORKS, SCENARIOS, MAPS, FIGURES, REPORTS):
        path.mkdir(parents=True, exist_ok=True)
    assumptions, actor_states, authority_states, dependency_states, coordination_states, uncertainty_states, comparisons = build_tables()
    write_rows(ASSUMPTIONS, ASSUMPTION_COLUMNS, assumptions)
    write_rows(ACTOR_STATES, ACTOR_COLUMNS, actor_states)
    write_rows(AUTHORITY_STATES, AUTHORITY_COLUMNS, authority_states)
    write_rows(DEPENDENCY_STATES, DEPENDENCY_COLUMNS, dependency_states)
    write_rows(COORDINATION_STATES, COORDINATION_COLUMNS, coordination_states)
    write_rows(UNCERTAINTY_STATES, UNCERTAINTY_COLUMNS, uncertainty_states)
    write_rows(SOURCES, ["source_id", "title", "url", "source_type", "evidence_role", "source_scope", "retrieval_date", "retrieval_status", "use_limitations"], SOURCE_ROWS)
    write_rows(COMPARISON, COMPARISON_COLUMNS, comparisons)
    render_map(2050, MAP2050)
    render_map(2075, MAP2075)
    render_comparison(comparisons)
    for name, text in report_texts().items():
        (REPORTS / name).write_text(text, encoding="utf-8")
    append_citation_blocks()
    artifacts = [
        ASSUMPTIONS, ACTOR_STATES, AUTHORITY_STATES, DEPENDENCY_STATES, COORDINATION_STATES, UNCERTAINTY_STATES,
        SOURCES, COMPARISON, COMPARISON_PNG, COMPARISON_SVG,
        MAP2050.with_suffix(".png"), MAP2050.with_suffix(".svg"), MAP2075.with_suffix(".png"), MAP2075.with_suffix(".svg"),
        *(REPORTS / name for name in report_texts()),
    ]
    review_artifact = REPORTS / "governance_scenario_independent_review.md"
    if review_artifact.exists():
        artifacts.append(review_artifact)
    manifest = {
        "phase": "10C",
        "status": "implemented_validated_pending_sol_acceptance",
        "scope": "qualitative governance futures, 2050 / 2075",
        "scenario_ids": list(SCENARIO_IDS),
        "counts": {
            "scenario_assumptions": len(assumptions), "actor_states": len(actor_states), "authority_states": len(authority_states),
            "dependency_states": len(dependency_states), "coordination_states": len(coordination_states), "uncertainty_states": len(uncertainty_states),
            "comparison_rows": len(comparisons),
        },
        "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": digest(path)} for path in artifacts},
        "protected_inputs": [
            "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
            "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
            "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
            "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
            "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
