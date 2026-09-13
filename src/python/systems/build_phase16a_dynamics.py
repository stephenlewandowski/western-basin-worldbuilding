"""Build the Phase 16A qualitative integrated-basin dynamics package.

This builder consumes the frozen Phase 14 crosswalks and Phase 15 technology
products without modifying them. It creates only an additive vocabulary,
qualitative propagation rules, a pathway matrix, candidate Phase 16B tests,
reports, and a conceptual Atlas figure. No stress test is executed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import yaml

ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = ROOT / "data/processed/integration"
SCENARIOS = ROOT / "data/processed/scenarios"
ANALYSIS = ROOT / "data/processed/analysis"
METADATA = ROOT / "metadata"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "outputs/figures"
BRIEFS = ROOT / "docs/phase_briefs"
VOCABULARY = METADATA / "basin_dynamics_vocabulary.yml"
SYSTEMS = METADATA / "atlas_systems.yml"
PHASE14_RELATIONSHIPS = INTEGRATION / "atlas_dependency_crosswalk.csv"
PHASE15A_INTERFACES = INTEGRATION / "technology_system_interfaces.csv"
PHASE15A_DEPENDENCIES = INTEGRATION / "technology_dependencies.csv"
PHASE15A_NODES = ANALYSIS / "technology_system_nodes.csv"
PHASE15B_STATES = SCENARIOS / "technology_system_states.csv"
PHASE15B_DEPENDENCIES = SCENARIOS / "technology_dependency_states.csv"
PHASE15B_GOVERNANCE = SCENARIOS / "technology_governance_states.csv"
BASE_SHA = "038669819731b2206f74a078f6b652ebafacb007"
ARCHITECTURE_LINEAGE_PREFIX = "metadata/atlas_systems.yml#architecture.interfaces:"

STRESSORS = [
    ("STRESS-HEAT-EXTREME", "CLIMATE_ENVIRONMENTAL", "Extreme heat", "SYS-CLIMATE", "Climate/hazard state may become stressed or constrained; no heat-health outcome is forecast.", "OBSERVED_DOCUMENTED", "data/processed/analysis/climate_hazard_dependency_register.csv; Phase 9B accepted context"),
    ("STRESS-LOW-FLOW-DROUGHT", "CLIMATE_ENVIRONMENTAL", "Low flow / drought-like hydrologic stress", "SYS-CLIMATE", "Hydrologic observations and water-system conditions may become constrained at their native scale.", "OBSERVED_DOCUMENTED", "data/processed/analysis/climate_hazard_dependency_register.csv; Phase 9B accepted context"),
    ("STRESS-HEAVY-PRECIP-FLOOD", "CLIMATE_ENVIRONMENTAL", "Heavy precipitation / flooding", "SYS-CLIMATE", "Flood and runoff context may constrain water, freight, and selected pathway interfaces.", "OBSERVED_DOCUMENTED", "data/processed/analysis/climate_hazard_dependency_register.csv; Phase 9B accepted context"),
    ("STRESS-HAB-WATER-QUALITY", "CLIMATE_ENVIRONMENTAL", "Harmful algal bloom / nutrient-water-quality pressure", "SYS-BIOGEOCHEMISTRY", "Nutrient-water-quality context may become constrained or less observable; no bloom magnitude or health outcome is forecast.", "OBSERVED_DOCUMENTED", "data/processed/analysis/biogeochemical_quantitative_fluxes.csv; Phase 8 accepted context"),
    ("STRESS-SEVERE-STORM", "CLIMATE_ENVIRONMENTAL", "Severe storm / wind / ice", "SYS-CLIMATE", "Hazard and continuity context may be stressed; no event probability or damage estimate is asserted.", "OBSERVED_DOCUMENTED", "data/processed/analysis/climate_hazard_dependency_register.csv; Phase 9B accepted context"),
    ("STRESS-ECOLOGICAL-DISTURBANCE", "CLIMATE_ENVIRONMENTAL", "Ecological disturbance", "SYS-ECOLOGY", "Ecological function or habitat context may become constrained or redistributed.", "OBSERVED_DOCUMENTED", "data/processed/analysis/ecological_disturbance_register.csv; Phase 6B accepted context"),
    ("STRESS-ELECTRIC-GRID", "INFRASTRUCTURE", "Electric-grid stress", "SYS-ENERGY", "Energy service may become constrained or delayed; no outage probability or failure is inferred.", "INFERRED", "data/processed/integration/technology_dependencies.csv; Phase 3B/15A dependency context"),
    ("STRESS-COMMS-COMPUTE", "INFRASTRUCTURE", "Communications / compute disruption", "SYS-DATA", "Observation and decision-support continuity may become degraded or delayed.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 3B/4B dependency context"),
    ("STRESS-WATER-TREATMENT", "INFRASTRUCTURE", "Water-treatment or conveyance disruption", "SYS-WATER", "Water operations may become constrained or delayed; treatment failure and exposure are not inferred.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 3B/13B dependency context"),
    ("STRESS-TRANSPORT-FREIGHT", "INFRASTRUCTURE", "Transportation / freight disruption", "SYS-FREIGHT", "Freight and logistics interfaces may become constrained or rerouted; no route or quantity is estimated.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 5C/11B dependency context"),
    ("STRESS-INDUSTRIAL-FACILITY", "INFRASTRUCTURE", "Industrial facility disruption", "SYS-FREIGHT", "Industrial and gateway functions may become constrained; no facility failure is asserted.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 5C dependency context"),
    ("STRESS-FUEL-CONSTRAINT", "MATERIAL_SUPPLY", "Fuel constraint", "SYS-FREIGHT", "Generalized fuel-input interfaces may become constrained; no pipeline, contract, or shipment path is modeled.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 5C material-input context"),
    ("STRESS-CRITICAL-MATERIAL", "MATERIAL_SUPPLY", "Critical material constraint", "SYS-MATERIALS", "Materials processing or feedstock interfaces may become constrained; no production forecast is asserted.", "INFERRED", "data/processed/integration/technology_dependencies.csv; Phase 15A materials context"),
    ("STRESS-INDUSTRIAL-FEEDSTOCK", "MATERIAL_SUPPLY", "Industrial feedstock disruption", "SYS-MATERIALS", "Qualified feedstock and processing dependencies may become constrained; local extraction and nonlocal processing remain distinct.", "INFERRED", "data/processed/integration/technology_dependencies.csv; Phase 15A materials context"),
    ("STRESS-LOGISTICS-INTERRUPTION", "MATERIAL_SUPPLY", "Logistics interruption", "SYS-FREIGHT", "Material and freight interfaces may be delayed or redistributed; no exact route or cargo quantity is modeled.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 5A/5C context"),
    ("STRESS-INFECTIOUS-PRESSURE", "PUBLIC_HEALTH_BIOLOGICAL", "Infectious-disease pressure", "SYS-INFECTIOUS-DISEASE", "Surveillance, diagnostic, workforce, and coordination interfaces may become constrained; no incidence or outbreak forecast is made.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 13A/13B accepted context"),
    ("STRESS-VECTOR-PRESSURE", "PUBLIC_HEALTH_BIOLOGICAL", "Vector-pressure increase", "SYS-VECTOR-ECOLOGY", "Vector observation or ecological context may become more variable; no abundance, infection, or disease forecast is made.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 12A/12B accepted context"),
    ("STRESS-WORKFORCE-ABSENTEEISM", "PUBLIC_HEALTH_BIOLOGICAL", "Workforce illness / absenteeism", "SYS-POPULATION", "Aggregate workforce and mobility interfaces may become constrained or redistributed; no individual data or illness estimate is used.", "INFERRED", "data/processed/integration/technology_dependencies.csv; Phase 11/15A context"),
    ("STRESS-SURVEILLANCE-STRAIN", "PUBLIC_HEALTH_BIOLOGICAL", "Surveillance / diagnostic strain", "SYS-DATA", "Observation, detection, and reporting may become delayed or less observable; surveillance is not incidence.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 4B/13B context"),
    ("STRESS-SENSOR-DATA-DEGRADATION", "INSTITUTIONAL_INFORMATION", "Sensor-data degradation", "SYS-DATA", "Observation coverage, timeliness, or interpretability may become degraded; a gap is not proof of absence.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 4B accepted context"),
    ("STRESS-CYBER-DIGITAL", "INSTITUTIONAL_INFORMATION", "Cyber / digital-resilience stress", "SYS-DATA", "Digital continuity and observability may become degraded or less interoperable; no attack path or offensive detail is modeled.", "INFERRED", "data/processed/integration/technology_system_interfaces.csv; Phase 15A defensive context"),
    ("STRESS-GOV-COORDINATION", "INSTITUTIONAL_INFORMATION", "Governance coordination friction", "SYS-GOVERNANCE", "Coordination or authority interfaces may become delayed, fragmented, or less interoperable; no governance score is assigned.", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv; Phase 10B accepted context"),
    ("STRESS-TRUST-LEGITIMACY", "INSTITUTIONAL_INFORMATION", "Public-trust / legitimacy stress", "SYS-GOVERNANCE", "Coordination, communication, and legitimacy interfaces may become constrained; no political or ideological score is assigned.", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_governance_states.csv; Phase 15B optional modifier"),
    ("STRESS-DATA-PRIVACY", "INSTITUTIONAL_INFORMATION", "Data-access / privacy constraint", "SYS-DATA", "Data access and interoperability may become constrained or redistributed; privacy is not treated as a technical failure.", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_dependency_states.csv; Phase 15B optional modifier"),
]

# Each direct lineage is a frozen Phase 14 dependency-crosswalk row. The two
# conceptual/scenario entries are kept explicit rather than masquerading as
# local documented edges.
RELATION_SPECS = [
    ("REL-16A-001", "SYS-CLIMATE", "SYS-ENERGY", "operational dependency", "energy dependency", "AR-9B-HZD-001-13a6b9b4", "baseline"),
    ("REL-16A-002", "SYS-CLIMATE", "SYS-WATER", "physical flow", "physical flow propagation", "AR-9B-HZD-004-7a781c1a", "baseline"),
    ("REL-16A-003", "SYS-CLIMATE", "SYS-FREIGHT", "material flow", "material-flow propagation", "AR-9B-HZD-007-41e5b974", "baseline"),
    ("REL-16A-004", "SYS-CLIMATE", "SYS-INFECTIOUS-DISEASE", "exposure pathway", "exposure pathway", "AR-13B-IDB-008-d35015f6", "baseline"),
    ("REL-16A-005", "SYS-CLIMATE", "SYS-ECOLOGY", "ecological relationship", "ecological pathway", "AR-9B-HZD-010-5424717c", "baseline"),
    ("REL-16A-006", "SYS-CLIMATE", "SYS-BIOGEOCHEMISTRY", "operational dependency", "ecological pathway", "AR-9B-HZD-005-ddd4be3d", "baseline"),
    ("REL-16A-007", "SYS-CLIMATE", "SYS-WATER", "operational dependency", "physical flow propagation", "AR-9B-HZD-006-361fc1dc", "baseline"),
    ("REL-16A-008", "SYS-WATER", "SYS-ENERGY", "operational dependency", "operational dependency", "AR-3B-DEP-016-95a609bc", "baseline"),
    ("REL-16A-009", "SYS-WATER", "SYS-INFECTIOUS-DISEASE", "exposure pathway", "exposure pathway", "AR-13B-IDB-007-c8da7d06", "baseline"),
    ("REL-16A-010", "SYS-WATER", "SYS-INFECTIOUS-DISEASE", "ecological relationship", "ecological pathway", "AR-13B-IDB-009-0b36d503", "baseline"),
    ("REL-16A-011", "SYS-WATER", "SYS-VECTOR-ECOLOGY", "ecological relationship", "ecological pathway", "AR-13B-IDB-002-eb173fa7", "baseline"),
    ("REL-16A-012", "SYS-DATA", "SYS-ENERGY", "information / observation", "information / observation degradation", "AR-3B-DEP-027-60a602d4", "baseline"),
    ("REL-16A-013", "SYS-DATA", "SYS-GOVERNANCE", "governance / authority", "governance / authority constraint", "AR-13B-IDB-012-50ef95ce", "baseline"),
    ("REL-16A-014", "SYS-FREIGHT", "SYS-ENERGY", "material flow", "supply-chain propagation", "AR-5C-FDE-013-a496499f", "baseline"),
    ("REL-16A-015", "SYS-FREIGHT", "SYS-INFECTIOUS-DISEASE", "high-level association", "supply-chain propagation", "AR-13B-IDB-015-291c716f", "baseline"),
    ("REL-16A-016", "SYS-GOVERNANCE", "SYS-WATER", "governance / authority", "governance / authority constraint", "AR-10B-GDEP-001-f50f412f", "baseline"),
    ("REL-16A-017", "SYS-INFECTIOUS-DISEASE", "SYS-DATA", "information / observation", "surveillance / detection pathway", "AR-13B-IDB-006-1b416a5c", "baseline"),
    ("REL-16A-018", "SYS-INFECTIOUS-DISEASE", "SYS-GOVERNANCE", "governance / authority", "governance / authority constraint", "AR-13B-IDB-029-40f322e0", "baseline"),
    ("REL-16A-019", "SYS-INFECTIOUS-DISEASE", "SYS-GOVERNANCE", "operational dependency", "operational dependency", "AR-13B-IDB-018-80d58860", "baseline"),
    ("REL-16A-020", "SYS-POPULATION", "SYS-ENERGY", "operational dependency", "workforce / mobility effect", "AR-11B-DEP-0001-ENERGY-b93f58d9", "baseline"),
    ("REL-16A-021", "SYS-POPULATION", "SYS-FREIGHT", "operational dependency", "workforce / mobility effect", "AR-11B-DEP-0001-TRANSPORT-07641b2d", "baseline"),
    ("REL-16A-022", "SYS-POPULATION", "SYS-INFECTIOUS-DISEASE", "high-level association", "workforce / mobility effect", "AR-13B-IDB-021-9eedbe4c", "baseline"),
    ("REL-16A-023", "SYS-POPULATION", "SYS-BIOGEOCHEMISTRY", "material flow", "material-flow propagation", "AR-11B-DEP-0001-BIOGEOCHEMICAL-81787412", "baseline"),
    ("REL-16A-024", "SYS-POPULATION", "SYS-WATER", "operational dependency", "operational dependency", "AR-11B-DEP-0001-WATER-1f586075", "baseline"),
    ("REL-16A-025", "SYS-VECTOR-ECOLOGY", "SYS-INFECTIOUS-DISEASE", "high-level association", "ecological pathway", "AR-13B-IDB-004-567747f1", "baseline"),
    ("REL-16A-026", "SYS-ECOLOGY", "SYS-INFECTIOUS-DISEASE", "high-level association", "ecological pathway", "AR-13B-IDB-026-6a5151fc", "baseline"),
    ("REL-16A-027", "SYS-EXPOSURE", "SYS-VECTOR-ECOLOGY", "exposure pathway", "exposure pathway", "AR-12B-VDE-022-e55d7c20", "baseline"),
    ("REL-16A-028", "SYS-CLIMATE", "SYS-VECTOR-ECOLOGY", "ecological relationship", "ecological pathway", "AR-12B-VDE-001-feb95688", "baseline"),
    ("REL-16A-029", "SYS-ENERGY", "SYS-DATA", "operational dependency", "technology / compute dependency", "TDS-A2050-01", "scenario-conditioned"),
    ("REL-16A-030", "SYS-DATA", "SYS-GOVERNANCE", "governance / authority", "scenario-conditioned interaction", "TDS-A2050-02", "scenario-conditioned"),
    ("REL-16A-031", "SYS-FREIGHT", "SYS-POPULATION", "operational dependency", "workforce / mobility effect", "TDS-A2050-04", "scenario-conditioned"),
    ("REL-16A-032", "SYS-INFECTIOUS-DISEASE", "SYS-GOVERNANCE", "operational dependency", "technology / compute dependency", "TDS-A2050-05", "scenario-conditioned"),
    ("REL-16A-033", "SYS-BIOGEOCHEMISTRY", "SYS-ECOLOGY", "ecological relationship", "ecological pathway", "metadata/atlas_systems.yml#architecture.interfaces:SYS-BIOGEOCHEMISTRY>SYS-ECOLOGY", "conceptual"),
    ("REL-16A-034", "SYS-CLIMATE", "SYS-WATER", "physical flow", "low-flow propagation", "AR-9B-HZD-011-6487677d", "baseline"),
    ("REL-16A-035", "SYS-CLIMATE", "SYS-ENERGY", "operational dependency", "severe-storm power-interface propagation", "AR-9B-HZD-016-938027aa", "baseline"),
    ("REL-16A-036", "SYS-CLIMATE", "SYS-FREIGHT", "operational dependency", "wind/seiche freight-interface propagation", "AR-9B-HZD-014-08221b51", "baseline"),
]

TECHNOLOGY_MODIFIERS = [
    ("TM-16A-001", "AI / ADVANCED COMPUTE / AUTOMATION", "TECH-AI-COMPUTE", "may increase observability or delay interpretation while increasing compute, data, communications, and operator coupling", "Phase 15A interface TSI-001; Phase 15B TSS-A2050-04", "INFERRED", "A/B/C optional; capability is not deployment or authority", "reduce propagation; delay propagation; increase observability; increase coupling"),
    ("TM-16A-002", "ADVANCED SENSING / AUTONOMOUS SYSTEMS", "TECH-SENS-ENVIRONMENTAL", "may increase observation and detection opportunity while remaining dependent on power, communications, maintenance, calibration, and stewardship", "Phase 15A interface TSI-008; Phase 15B TSS-A2050-04", "INFERRED", "A/B/C optional; observation is not control", "delay propagation; increase observability; create new dependencies"),
    ("TM-16A-003", "CYBERSECURITY / DIGITAL RESILIENCE", "TECH-CYBER-RESILIENCE", "may reduce or delay digital propagation but may also create maintenance, interoperability, and trust friction", "Phase 15A interface TSI-014; Phase 15B TDS-C2050-08", "INFERRED", "A/B/C optional; defensive only", "reduce propagation; delay propagation; increase coupling; create governance / trust friction"),
    ("TM-16A-004", "ADVANCED ENERGY", "TECH-ENERGY-DISTRIBUTED", "may create substitution or distributed-operation options while retaining material, maintenance, siting, and governance dependencies", "Phase 15A technology node TECH-ENERGY-DISTRIBUTED; Phase 15B TDS-A2050-10 (ADVANCED ENERGY family-level mapping)", "INFERRED", "A/B/C optional; no capacity or deployment claim", "create substitution options; reduce propagation; create new dependencies"),
    ("TM-16A-005", "ADVANCED ENERGY", "TECH-ENERGY-LDES", "may support load shifting or continuity options in a scenario, without establishing firm capacity or outage protection", "Phase 15A interface TSI-021; Phase 15B TDS-A2050-10 (ADVANCED ENERGY family-level mapping)", "INFERRED", "A/B/C optional; no dispatch or capacity model", "delay propagation; create substitution options; increase coupling"),
    ("TM-16A-006", "ADVANCED MATERIALS / MANUFACTURING", "TECH-MATERIALS-CIRCULAR", "may support supply substitution or alternate processing pathways while shifting dependence toward qualified feedstock and logistics", "Phase 15A technology node TECH-MATERIALS-CIRCULAR; Phase 15B TDS-A2050-06", "INFERRED", "A/B/C optional; not a production forecast", "create substitution options; supply substitution; shift workforce requirements"),
    ("TM-16A-007", "BIOTECHNOLOGY / GENETIC ENGINEERING", "TECH-BIO-DIAGNOSTICS", "may increase detection and diagnostic observability while leaving attribution, interpretation, communication, and authority distinct", "Phase 15A technology node TECH-BIO-DIAGNOSTICS; Phase 15B TDS-A2050-05", "INFERRED", "A/B/C optional; high-level public-health lens only", "increase observability; delay propagation; create governance / trust friction"),
    ("TM-16A-008", "PRIVACY / SURVEILLANCE / DATA GOVERNANCE", "TECH-DATA-GOVERNANCE", "may enable stewardship and privacy-preserving access or constrain interoperability and timeliness", "Phase 15A technology node TECH-DATA-GOVERNANCE; Phase 15B TDS-A2050-02", "INFERRED", "A/B/C optional; access is not control", "increase observability; create substitution options; create governance / trust friction"),
    ("TM-16A-009", "REGIME-A", "REGIME-A", "Coordinated Technological Adaptation may buffer selected pathways while leaving compute, energy, data, maintenance, and human-authority dependencies visible", "Phase 15B TSS-A2050-01; TDS-A2050-01", "SCENARIO_STATE", "optional regime modifier only", "reduce propagation; improve coordination; increase observability"),
    ("TM-16A-010", "REGIME-B", "REGIME-B", "Uneven Networked Modernization may create uneven substitution and observability with uneven interoperability and workforce requirements", "Phase 15B TSS-B2050-01; TDS-B2050-01", "SCENARIO_STATE", "optional regime modifier only", "create substitution options; increase coupling; shift workforce requirements"),
    ("TM-16A-011", "REGIME-C", "REGIME-C", "High Capability / High Friction Basin may increase capability and observability while increasing governance, trust, cyber, and maintenance friction", "Phase 15B TSS-C2050-01; TDS-C2050-01", "SCENARIO_STATE", "optional regime modifier only", "increase observability; increase coupling; create governance / trust friction; create cyber / digital exposure"),
]

# rule_id, stressor, relationship, stage, source_state, initial_effect,
# enabling, limiting, temporal, spatial, reversibility, technology_modifier,
# governance_modifier, response, second_order, uncertainty, status.
RULE_SPECS = [
    ("RULE-16A-001", "STRESS-HEAT-EXTREME", "REL-16A-001", 1, "climate stressed", "heat-related continuity pressure may constrain energy operations", "accepted hazard/dependency interface is applicable", "no demand, outage, or failure probability is inferred", "episodic / seasonal", "native regional hazard to system interface", "potentially reversible; duration unknown", "TM-16A-004;TM-16A-005", "human/operator and institutional authority remain required", "load shifting", "energy service may be delayed or redistributed", "native-scale hazard and operating conditions are unresolved", "baseline"),
    ("RULE-16A-002", "STRESS-HEAT-EXTREME", "REL-16A-005", 1, "climate stressed", "ecological condition may become constrained", "the documented climate/ecology relationship supports only a qualified qualitative inference for this heat application", "the cited relationship is drought/low-water-specific; a heat-specific ecological response is inferred; no abundance, range, or population effect is inferred", "episodic / seasonal", "regional climate to ecological context", "potentially reversible; recovery unknown", "TM-16A-002", "monitoring does not create ecological control", "increased monitoring", "ecological observations may become less comparable across time", "scale and response are uncertain", "baseline"),


    ("RULE-16A-005", "STRESS-LOW-FLOW-DROUGHT", "REL-16A-034", 1, "hydrologic context constrained", "physical-flow context may be constrained", "accepted low-flow/receiving-system relationship supports qualitative propagation", "one gauge or local record is not a basin-wide forecast", "seasonal / potentially persistent", "native gauge and water-system scales", "potentially reversible; recovery unknown", "NONE", "no operational control is inferred", "conservation", "water-system observability may become less complete", "spatial coverage and duration are unresolved", "baseline"),
    ("RULE-16A-006", "STRESS-LOW-FLOW-DROUGHT", "REL-16A-008", 2, "water constrained after low-flow context", "water-dependent energy operations may become constrained", "stage 1 water pathway and accepted dependency support the chain", "no cooling load, outage, or capacity estimate", "seasonal / potentially persistent", "water-system to energy interface", "potentially reversible; duration unknown", "TM-16A-005", "operator review and authority remain required", "load shifting", "water-energy coordination may be delayed", "local operating evidence is not present", "baseline"),
    ("RULE-16A-007", "STRESS-LOW-FLOW-DROUGHT", "REL-16A-009", 2, "water constrained after low-flow context", "potential exposure pathway context may be delayed or less observable", "accepted water/pathway relationship supports only qualitative review", "contamination, exposure, infection, illness, and outbreak remain separate", "seasonal / duration unknown", "native water and surveillance scales", "potentially reversible; recovery unknown", "TM-16A-007", "diagnostics are not disease authority", "increased monitoring", "detection or communication timing may change", "health boundary is intentionally non-predictive", "baseline"),
    ("RULE-16A-008", "STRESS-LOW-FLOW-DROUGHT", "REL-16A-011", 2, "water constrained after low-flow context", "vector-ecology context may be redistributed or less observable", "accepted water/vector ecological relationship supports pathway review", "no abundance, establishment, contact, infection, or disease inference", "seasonal / duration unknown", "native water and vector scales", "potentially reversible; recovery unknown", "TM-16A-002", "surveillance is not control", "increased monitoring", "vector observation effort may need redistribution", "sampling effort and detection remain distinct", "baseline"),
    ("RULE-16A-009", "STRESS-HEAVY-PRECIP-FLOOD", "REL-16A-002", 1, "flooding context stressed", "physical-flow and water-system context may be delayed or constrained", "accepted physical-flow relationship supports qualitative pathway review", "no flood extent, discharge, treatment failure, or exposure is inferred", "episodic", "event-scale to native water-system scale", "potentially reversible; recovery unknown", "TM-16A-002", "monitoring does not create control", "alternate routing", "water and freight interfaces may be temporally misaligned", "event footprint is unresolved", "baseline"),
    ("RULE-16A-010", "STRESS-HEAVY-PRECIP-FLOOD", "REL-16A-003", 1, "flooding context stressed", "freight/material interfaces may be delayed or redistributed", "accepted climate/freight relationship supports qualitative chain", "no route, volume, cargo, or probability is inferred", "episodic", "corridor/interface scale; not an exact route", "potentially reversible; recovery unknown", "TM-16A-006", "automation does not select a route or authorize movement", "alternate routing", "industrial and energy interfaces may be delayed", "freight disruption remains qualitative", "baseline"),
    ("RULE-16A-011", "STRESS-HEAVY-PRECIP-FLOOD", "REL-16A-004", 1, "flooding context stressed", "potential exposure pathway context may become less observable", "accepted climate/disease pathway supports only high-level review", "no contamination, exposure, infection, illness, or outbreak is inferred", "episodic / lagged", "event-scale to native health-surveillance scale", "potentially reversible; recovery unknown", "TM-16A-007", "surveillance and communication are not incidence or authority", "increased monitoring", "diagnostic or communication timing may be altered", "health-outcome forecasting is excluded", "baseline"),
    ("RULE-16A-012", "STRESS-HAB-WATER-QUALITY", "REL-16A-033", 1, "nutrient-water-quality context constrained", "ecological condition may become constrained or less observable", "accepted Phase 14 conceptual interface is explicitly system-level", "no bloom magnitude, ecology score, exposure, dose, or illness is inferred", "seasonal / event-linked", "system-level water-quality to ecological interface", "recovery unknown", "TM-16A-002;TM-16A-008", "monitoring and stewardship are not control", "increased monitoring", "ecological observation and governance coordination may be delayed", "conceptual interface is inferred, not exact local identity", "baseline"),

    ("RULE-16A-014", "STRESS-WATER-TREATMENT", "REL-16A-008", 1, "water operations constrained", "water-dependent energy operations may be constrained or delayed", "accepted water-energy dependency supports only functional pathway", "treatment disruption is not water contamination or illness", "episodic / duration unknown", "water facility/system interface; no exact site claim", "potentially reversible; recovery unknown", "TM-16A-005", "operator authority and treatment decisions are not modeled", "manual fallback", "coordination and service timing may be delayed", "facility-specific operating details are absent", "baseline"),
    ("RULE-16A-015", "STRESS-WATER-TREATMENT", "REL-16A-009", 1, "water operations constrained", "potential exposure-pathway context may become delayed or less observable", "accepted water/disease pathway supports qualitative review", "contamination, exposure, dose, illness, and outbreak remain unasserted", "episodic / duration unknown", "water-system to surveillance interface", "potentially reversible; recovery unknown", "TM-16A-007", "diagnostic support is not health authority", "increased monitoring", "detection and communication timing may change", "no individual exposure or outcome is modeled", "baseline"),
    ("RULE-16A-016", "STRESS-ELECTRIC-GRID", "REL-16A-029", 1, "energy stressed", "technology/compute-dependent data services may become more coupled or delayed", "only the named Phase 15B scenario state enables this edge", "not a baseline energy-to-data guarantee or outage model", "scenario-conditioned / horizon-specific", "system-level energy-to-data interface", "scenario recovery is indeterminate", "TM-16A-009;TM-16A-010;TM-16A-011", "AI remains advisory; human authority remains explicit", "distributed operation", "observability may improve in one regime and fragment in another", "scenario family, adoption, and continuity are unresolved", "scenario-conditioned"),
    ("RULE-16A-017", "STRESS-COMMS-COMPUTE", "REL-16A-012", 1, "data/communications degraded", "energy operations may become less observable or delayed", "accepted information/energy dependency supports qualitative pathway", "no communications topology, outage probability, or control authority", "episodic / duration unknown", "system-level data-to-energy interface", "potentially reversible; recovery unknown", "TM-16A-001;TM-16A-003", "information is not control or authority", "manual fallback", "coordination timing may increase", "generalized dependency only", "baseline"),
    ("RULE-16A-018", "STRESS-COMMS-COMPUTE", "REL-16A-013", 1, "data/communications degraded", "governance coordination may be delayed or fragmented", "accepted data/governance relationship supports a parallel initial branch", "data degradation is not governance failure", "episodic / duration unknown", "system-level information-to-governance interface", "potentially reversible; recovery unknown", "TM-16A-008", "data access does not create or remove authority", "manual fallback", "response coordination may be less timely", "institutional response is not forecast", "baseline"),
    ("RULE-16A-019", "STRESS-TRANSPORT-FREIGHT", "REL-16A-014", 1, "freight constrained", "generalized fuel/material input interface may be constrained", "accepted freight-energy material-flow relationship", "no shipment, route, contract, or capacity inference", "episodic / duration unknown", "corridor/interface scale", "potentially reversible; recovery unknown", "TM-16A-006", "no operator or market authority is inferred", "alternate routing", "industrial operations may be delayed", "route-level evidence is absent", "baseline"),
    ("RULE-16A-020", "STRESS-FUEL-CONSTRAINT", "REL-16A-014", 1, "fuel/material input constrained", "energy-related freight interface may be constrained", "accepted generalized fuel interface", "fuel is a material input, not an electricity flow or pipeline model", "episodic / duration unknown", "regional interface; no exact route", "potentially reversible; recovery unknown", "TM-16A-004;TM-16A-006", "coordination is not procurement control", "supply substitution", "industrial and freight timing may be redistributed", "no quantities or probabilities", "baseline"),
    ("RULE-16A-021", "STRESS-LOGISTICS-INTERRUPTION", "REL-16A-015", 1, "freight/logistics delayed", "food/freight interface with disease systems may become less timely", "accepted high-level association only", "connectivity is not shipment, contamination, exposure, infection, or outbreak", "episodic / duration unknown", "generalized logistics interface", "potentially reversible; recovery unknown", "TM-16A-006", "investigation and communication are not incidence authority", "alternate routing", "surveillance and distribution coordination may be delayed", "biosecurity boundary remains high-level", "baseline"),
    ("RULE-16A-022", "STRESS-INFECTIOUS-PRESSURE", "REL-16A-017", 1, "disease surveillance pressure", "surveillance and reporting may become degraded or delayed", "accepted disease/data observation relationship", "surveillance is not incidence, burden, or response effectiveness", "episodic / duration unknown", "surveillance-program/system scale", "potentially reversible; recovery unknown", "TM-16A-007;TM-16A-008", "diagnostics and analytics are not authority", "mutual aid", "detection timing and reported observations may change", "no cases, incidence, or outbreak probability", "baseline"),
    ("RULE-16A-023", "STRESS-INFECTIOUS-PRESSURE", "REL-16A-018", 1, "disease surveillance pressure", "governance/coordination interface may become constrained", "accepted disease/governance relationship", "response capacity is not absence of disease or legal authority", "episodic / duration unknown", "institutional and program scale", "potentially reversible; recovery unknown", "TM-16A-007", "communication and coordination remain distinct from authority", "institutional coordination", "response timing may be delayed", "no health-outcome forecast", "baseline"),
    ("RULE-16A-024", "STRESS-WORKFORCE-ABSENTEEISM", "REL-16A-020", 1, "aggregate workforce constrained", "population/energy interface may become delayed or redistributed", "accepted aggregate population dependency", "no individual workforce, illness, or utility-territory inference", "episodic / duration unknown", "aggregate population/system interface", "potentially reversible; recovery unknown", "TM-16A-004", "workforce substitution is not guaranteed capacity", "workforce substitution", "service timing and maintenance burden may change", "aggregate data remain descriptive", "baseline"),
    ("RULE-16A-025", "STRESS-WORKFORCE-ABSENTEEISM", "REL-16A-021", 1, "aggregate workforce constrained", "freight/transport interface may become delayed or redistributed", "accepted aggregate mobility/freight dependency", "commuting is not migration; no individual flow is modeled", "episodic / duration unknown", "aggregate population/freight interface", "potentially reversible; recovery unknown", "TM-16A-006", "automation does not remove human authority or labor requirements", "workforce substitution", "logistics continuity may be delayed", "workforce evidence is generalized", "baseline"),
    ("RULE-16A-026", "STRESS-SURVEILLANCE-STRAIN", "REL-16A-013", 1, "observation/detection degraded", "governance coordination may become less observable or delayed", "accepted data/governance relationship", "observation is not authority, enforcement, or control", "episodic / duration unknown", "information-to-governance interface", "potentially reversible; recovery unknown", "TM-16A-008", "privacy and stewardship constraints remain explicit", "manual fallback", "coordination and accountability may be delayed", "unknown is not low or absent", "baseline"),
    ("RULE-16A-027", "STRESS-SENSOR-DATA-DEGRADATION", "REL-16A-012", 1, "data less observable", "energy operations may become less observable or delayed", "accepted information/energy relationship", "no control, topology, or outage claim", "episodic / duration unknown", "system-level information-to-energy interface", "potentially reversible; recovery unknown", "TM-16A-002;TM-16A-003", "observation does not create control", "manual fallback", "decision timing may be delayed", "coverage and representativeness are unresolved", "baseline"),
    ("RULE-16A-028", "STRESS-CYBER-DIGITAL", "REL-16A-012", 1, "digital continuity degraded", "energy-related information interface may become less interoperable", "accepted generalized communications dependency", "no attack detail, topology, or failure probability", "episodic / duration unknown", "system-level information-to-energy interface", "potentially reversible; recovery unknown", "TM-16A-003;TM-16A-011", "defensive capability is not authority or immunity", "manual fallback", "coordination burden may increase", "digital exposure is high-level only", "baseline"),
    ("RULE-16A-029", "STRESS-CYBER-DIGITAL", "REL-16A-030", 1, "data less interoperable", "governance/data stewardship interface may become constrained", "only Phase 15B scenario state supports this parallel initial branch", "scenario-conditioned governance friction is not baseline failure", "scenario-conditioned / horizon-specific", "system-level data-to-governance interface", "scenario recovery is indeterminate", "TM-16A-008;TM-16A-011", "privacy, trust, and authority remain distinct", "institutional coordination", "data access and legitimacy may be redistributed", "no operational cyber detail", "scenario-conditioned"),
    ("RULE-16A-030", "STRESS-GOV-COORDINATION", "REL-16A-016", 1, "governance coordination delayed", "water-system coordination interface may be delayed or fragmented", "accepted governance/water relationship", "governance role is not operational control or treatment outcome", "episodic / duration unknown", "institutional-to-water interface", "potentially reversible; recovery unknown", "TM-16A-008", "authority, ownership, monitoring, and operation remain distinct", "institutional coordination", "water response timing may be delayed", "specific authority path remains qualified", "baseline"),
    ("RULE-16A-031", "STRESS-GOV-COORDINATION", "REL-16A-009", 2, "water coordination delayed", "potential exposure-pathway observation may become delayed", "stage 1 governance/water relationship plus accepted water/pathway relationship", "no exposure or health outcome is asserted", "episodic / duration unknown", "institutional-to-water-to-surveillance interface", "potentially reversible; recovery unknown", "TM-16A-007", "monitoring is not control", "mutual aid", "communication timing may change", "health boundary remains explicit", "baseline"),

    ("RULE-16A-033", "STRESS-DATA-PRIVACY", "REL-16A-030", 1, "data access constrained", "governance/data interface may become constrained or redistributed", "only Phase 15B data-governance state supports the interaction", "privacy constraint is not a data failure or loss of legitimacy", "scenario-conditioned / horizon-specific", "system-level data-to-governance interface", "scenario recovery is indeterminate", "TM-16A-008", "access and authority remain distinct", "institutional coordination", "timeliness and interoperability may change", "scenario assumption, not current fact", "scenario-conditioned"),
    ("RULE-16A-034", "STRESS-VECTOR-PRESSURE", "REL-16A-025", 1, "vector ecology context variable", "disease-system interface may become more observable or less certain", "accepted vector/disease relationship supports high-level review", "vector presence is not exposure, infection, or disease burden", "seasonal / duration unknown", "vector and disease surveillance scales", "recovery unknown", "TM-16A-007", "surveillance is not incidence or control", "increased monitoring", "reported observations may change with effort", "no disease forecast", "baseline"),

    ("RULE-16A-036", "STRESS-SEVERE-STORM", "REL-16A-035", 1, "storm/ice context stressed", "energy continuity interface may become constrained or delayed", "accepted severe-storm/power-interface relationship", "no outage probability, damage, or failure is inferred", "episodic", "event-scale to energy-system interface", "potentially reversible; recovery unknown", "TM-16A-004;TM-16A-005", "technology does not guarantee continuity", "distributed operation", "freight/data timing may be affected in a later test", "no compound test is executed here", "baseline"),
    ("RULE-16A-037", "STRESS-SEVERE-STORM", "REL-16A-036", 1, "storm/ice context stressed", "freight interface may be delayed or redistributed", "the cited relationship supports only the wind/seiche component of this broader stressor", "the broader severe-storm application is inferred; no route, volume, damage estimate, or general severe-storm effect is inferred", "episodic", "event-scale to generalized corridor context", "potentially reversible; recovery unknown", "TM-16A-006", "alternate routing is an option, not a guarantee", "alternate routing", "industrial timing may be redistributed", "public abstraction only; ice and non-wind storm effects remain unassessed", "baseline"),
]

REMOVED_RULE_IDS = {
    "RULE-16A-003", "RULE-16A-004", "RULE-16A-013", "RULE-16A-032",
    "RULE-16A-035", "RULE-16A-038",
}

# A relationship can be documented while a stressor-specific application is
# only an explicitly qualified inference. The rule evidence class describes
# that application, not the stronger class of the underlying relationship.
RULE_APPLICATION_EVIDENCE = {
    "RULE-16A-002": "INFERRED",
    "RULE-16A-037": "INFERRED",
}

RULE_APPLICATION_FIT = {
    "RULE-16A-002": "QUALIFIED_INFERENCE_FROM_DIFFERENT_CLIMATE_STRESSOR",
    "RULE-16A-037": "QUALIFIED_INFERENCE_FROM_WIND_SEICHE_COMPONENT",
}

RESPONSE_ROWS = [
    ("RESP-16A-001", "redundancy", "energy;data;water", "more than one accepted or scenario-supported service path is explicitly identified", "redundancy is not immunity and no facility-level redundancy is asserted", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_dependency_states.csv#TDS-A2050-01", "capacity or option exists; successful adaptation remains indeterminate"),
    ("RESP-16A-002", "substitution", "energy;materials;freight", "an accepted scenario or generalized dependency names an alternate input or interface", "substitution may require qualification, energy, logistics, workforce, or authority", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_dependency_states.csv#TDS-A2050-06", "option to substitute is not proof of continuity"),
    ("RESP-16A-003", "load shifting", "energy;water", "timing or demand can be considered qualitatively without capacity arithmetic", "no dispatch, demand, or capacity is estimated", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv#AR-3B-DEP-016-95a609bc", "an option is not a measured result"),
    ("RESP-16A-004", "conservation", "water;energy;materials", "accepted phase products identify stewardship, control, or resource-use interfaces", "conservation action and effect are not measured in Phase 16A", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv#AR-10B-GDEP-001-f50f412f", "capacity or intent is not successful conservation"),
    ("RESP-16A-005", "distributed operation", "energy;data", "Phase 15 optional technology regimes identify distributed or alternative interfaces", "no deployment, capacity, or local adoption is asserted", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_system_states.csv#TSS-A2050-03", "scenario option only"),
    ("RESP-16A-006", "alternate routing", "freight;materials", "accepted freight evidence distinguishes corridors, interchange, and modal alternatives", "no exact route or shipment quantity is modeled", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv#AR-9B-HZD-007-41e5b974", "an alternate interface is not guaranteed access"),
    ("RESP-16A-007", "increased monitoring", "data;water;ecology;infectious disease", "accepted observation, surveillance, or detection relationships support a qualitative monitoring response", "monitoring is not control, incidence, exposure, or enforcement", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv#AR-13B-IDB-006-1b416a5c", "monitoring capacity does not ensure detection or response"),
    ("RESP-16A-008", "manual fallback", "data;energy;governance", "Phase 15 governance boundaries preserve human/operator review", "fallback availability is not established for every interface", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_governance_states.csv#TGS-A2050-01", "human authority does not imply successful fallback"),
    ("RESP-16A-009", "institutional coordination", "governance;water;public health", "accepted governance roles and coordination interfaces are present", "coordination is not unified authority or operational control", "INFERRED", "data/processed/integration/atlas_dependency_crosswalk.csv#AR-10B-GDEP-001-f50f412f", "coordination capacity is not coordination success"),
    ("RESP-16A-010", "mutual aid", "public health;energy;water", "Phase 15/Phase 13 scenario contexts allow high-level coordination options", "no agreement, resource volume, or activation is asserted", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_governance_states.csv#TGS-A2050-06", "option is not deployment or outcome"),
    ("RESP-16A-011", "workforce substitution", "population;freight;industry", "technology states identify changed tasks, training, and maintenance requirements", "automation does not remove workforce, accountability, or skill requirements", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_dependency_states.csv#TDS-A2050-04", "capacity is not successful substitution"),
    ("RESP-16A-012", "supply substitution", "materials;freight;energy", "Phase 15 materials and energy scenarios identify alternate input options", "qualified feedstock, logistics, energy, and market dependencies remain", "SCENARIO_ASSUMPTION", "data/processed/scenarios/technology_dependency_states.csv#TDS-A2050-06", "substitution option is not immunity"),
    ("RESP-16A-013", "technology-assisted decision support", "all represented systems", "Phase 15A interfaces explicitly support qualitative analytics or observation", "AI recommendation is not autonomous authority; sensing is not control", "INFERRED", "data/processed/integration/technology_system_interfaces.csv#TSI-001", "decision support may improve observability without guaranteeing action"),
]

FEEDBACK_ROWS = [
    ("FC-16A-001", "energy ↔ compute/data", "scenario-conditioned", "Phase 15B energy/data dependency states", "energy continuity can condition compute/data observability and compute can increase energy coupling", "no documented two-way operational loop in the frozen baseline; no gain or stability claim"),
    ("FC-16A-002", "water ↔ energy", "inferred", "Phase 14 AR-3B-DEP-016-95a609bc", "water-dependent energy operation is documented as a dependency; reverse influence is not separately established", "inventory is one-way-supported plus plausible context, not a closed dynamic loop"),
    ("FC-16A-003", "industry ↔ freight/materials", "scenario-conditioned", "Phase 14 Atlas architecture and Phase 15 TDS-A2050-06", "industrial processing, feedstock, and logistics can condition one another in a scenario", "no shipment quantity, capacity, or production loop is modeled"),
    ("FC-16A-004", "population ↔ workforce", "inferred", "Phase 11B aggregate population/mobility context and Phase 15 workforce states", "population/workplace context and workforce requirements are connected at aggregate scale", "commuting is not migration; no individual or labor-market forecast"),
    ("FC-16A-005", "sensing ↔ governance", "inferred", "Phase 14 AR-13B-IDB-012-50ef95ce", "observation and stewardship can condition coordination while coordination conditions access and interpretation", "observation is not authority, enforcement, or control"),
    ("FC-16A-006", "public health ↔ workforce", "inferred", "Phase 13B disease/governance and Phase 11B population context", "surveillance/response strain and aggregate workforce continuity can interact", "no cases, absenteeism rate, incidence, or health-outcome forecast"),
    ("FC-16A-007", "ecology ↔ water quality", "inferred", "Phase 14 conceptual BGC/ecology interface plus Phase 8 accepted context", "water-quality/nutrient conditions and ecological observations can condition one another", "no bloom model, ecological score, abundance, or causal gain"),
    ("FC-16A-008", "surveillance ↔ response coordination", "inferred", "Phase 13B AR-13B-IDB-006-1b416a5c and AR-13B-IDB-029-40f322e0", "detection timing can condition coordination while coordination can condition reporting", "surveillance is not incidence and response capacity is not absence of disease"),
    ("FC-16A-009", "technology ↔ governance/trust", "scenario-conditioned", "Phase 15B governance states TGS-A2050-01 through TGS-C2050-06", "technology can improve observability or coordination while increasing privacy, trust, or authority friction", "not a governance performance or legitimacy score"),
    ("FC-16A-010", "unresolved or unsupported loops", "not currently supported", "Phase 14 joinability and evidence rules", "no defensible current closed loop is selected for exact co-location, generic proximity, or unreferenced causation", "do not interpret absence of a selected loop as absence of interaction"),
]

CANDIDATES = [
    ("P16B-CAND-001", "EXTREME HEAT + LOW FLOW + GRID STRESS", "STRESS-HEAT-EXTREME;STRESS-LOW-FLOW-DROUGHT;STRESS-ELECTRIC-GRID", "SYS-CLIMATE;SYS-WATER;SYS-ENERGY;SYS-DATA;SYS-POPULATION;SYS-EXPOSURE;SYS-ECOLOGY", "Tests a climate-to-water-to-energy chain with optional observation and technology modifiers.", "RULE-16A-001;RULE-16A-005;RULE-16A-006;RULE-16A-016", "APPROVED SCOPE / NOT IMPLEMENTED", "No health outcome, outage probability, or compound severity is modeled."),
    ("P16B-CAND-002", "HARMFUL ALGAL BLOOM / WATER-QUALITY PRESSURE + WATER-TREATMENT DISRUPTION", "STRESS-HAB-WATER-QUALITY;STRESS-WATER-TREATMENT", "SYS-BIOGEOCHEMISTRY;SYS-WATER;SYS-ECOLOGY;SYS-EXPOSURE;SYS-GOVERNANCE;SYS-POPULATION;SYS-DATA", "Tests the bounded nutrient-water-quality, water-operations, observation, ecology, and governance interfaces.", "RULE-16A-012;RULE-16A-014;RULE-16A-015", "APPROVED SCOPE / NOT IMPLEMENTED", "No bloom magnitude, treatment failure, exposure, dose, illness, or risk score is modeled."),
    ("P16B-CAND-003", "FREIGHT / MATERIAL DISRUPTION + INDUSTRIAL ENERGY CONSTRAINT", "STRESS-TRANSPORT-FREIGHT;STRESS-CRITICAL-MATERIAL;STRESS-FUEL-CONSTRAINT;STRESS-INDUSTRIAL-FEEDSTOCK", "SYS-FREIGHT;SYS-MATERIALS;SYS-ENERGY;SYS-POPULATION;SYS-GOVERNANCE", "Tests generalized logistics, material input, energy, workforce, and coordination interfaces.", "RULE-16A-019;RULE-16A-020", "APPROVED SCOPE / NOT IMPLEMENTED", "No exact route, quantity, contract, production, or market forecast is modeled."),
    ("P16B-CAND-004", "INFECTIOUS-DISEASE PRESSURE + SURVEILLANCE / DATA-GOVERNANCE FRICTION", "STRESS-INFECTIOUS-PRESSURE;STRESS-SURVEILLANCE-STRAIN;STRESS-DATA-PRIVACY", "SYS-INFECTIOUS-DISEASE;SYS-DATA;SYS-GOVERNANCE;SYS-POPULATION", "Tests surveillance, diagnostics, workforce, communication, stewardship, and coordination without epidemiological forecasting.", "RULE-16A-022;RULE-16A-023;RULE-16A-026;RULE-16A-033", "APPROVED SCOPE / NOT IMPLEMENTED", "High-level only: no pathogen engineering, transmission optimization, evasion, lab procedure, incidence, or outbreak probability."),
    ("P16B-CAND-005", "HEAVY PRECIPITATION / FLOODING + INFRASTRUCTURE / LOGISTICS DISRUPTION", "STRESS-HEAVY-PRECIP-FLOOD;STRESS-TRANSPORT-FREIGHT;STRESS-ELECTRIC-GRID", "SYS-CLIMATE;SYS-WATER;SYS-FREIGHT;SYS-ENERGY;SYS-POPULATION", "Tests event-scale water, freight, energy, and aggregate population interfaces.", "RULE-16A-009;RULE-16A-010;RULE-16A-036;RULE-16A-037", "APPROVED SCOPE / NOT IMPLEMENTED", "No flood extent, route loss, damage, outage probability, or population harm is modeled."),
    ("P16B-CAND-006", "CYBER / DIGITAL-RESILIENCE STRESS + SENSOR / DECISION-SUPPORT DEGRADATION", "STRESS-CYBER-DIGITAL;STRESS-COMMS-COMPUTE;STRESS-SENSOR-DATA-DEGRADATION", "SYS-DATA;SYS-ENERGY;SYS-WATER;SYS-GOVERNANCE;SYS-INFECTIOUS-DISEASE", "Tests observation, communications, defensive cyber, technology coupling, and manual fallback boundaries.", "RULE-16A-017;RULE-16A-018;RULE-16A-027;RULE-16A-028;RULE-16A-029", "APPROVED SCOPE / NOT IMPLEMENTED", "No operational attack details, exploit path, sensitive topology, or automatic control claim is modeled."),
]

SYSTEM_FAMILIES = {
    "natural_environment": "Natural environment",
    "infrastructure_technology": "Infrastructure / technology",
    "production_resources": "Production / resources",
    "production_logistics": "Production / logistics",
    "health_environment": "Health / environment",
    "institutional_human": "Institutional / human",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_relationship_rows() -> dict[str, dict[str, str]]:
    return {row["atlas_relationship_id"]: row for row in read_csv(PHASE14_RELATIONSHIPS)}


def endpoint_pair_matches(
    actual_source: str,
    actual_target: str,
    expected_source: str,
    expected_target: str,
    *,
    explicitly_undirected: bool = False,
) -> bool:
    ordered = (actual_source, actual_target) == (expected_source, expected_target)
    reversed_allowed = explicitly_undirected and (actual_source, actual_target) == (expected_target, expected_source)
    return ordered or reversed_allowed


def assert_lineage_endpoint_compatibility(
    relationship_id: str,
    actual_source: str,
    actual_target: str,
    expected_source: str,
    expected_target: str,
    *,
    lineage_kind: str,
    source_endpoint_field: str,
    target_endpoint_field: str,
    explicitly_undirected: bool = False,
) -> None:
    if endpoint_pair_matches(
        actual_source,
        actual_target,
        expected_source,
        expected_target,
        explicitly_undirected=explicitly_undirected,
    ):
        return
    allowance = "; reversed orientation is allowed only by an explicit undirected source declaration" if not explicitly_undirected else "; the explicit undirected declaration did not match either orientation"
    raise AssertionError(
        f"{relationship_id}: {lineage_kind} endpoint mismatch: "
        f"Phase 16A source_system_id={actual_source!r}, target_system_id={actual_target!r}; "
        f"frozen {source_endpoint_field}={expected_source!r}, {target_endpoint_field}={expected_target!r}{allowance}"
    )


def load_architecture_interfaces() -> dict[str, dict[str, object]]:
    payload = yaml.safe_load(SYSTEMS.read_text(encoding="utf-8"))
    interfaces = payload.get("architecture", {}).get("interfaces", [])
    assert isinstance(interfaces, list) and interfaces, "Phase 14 architecture interfaces"
    lookup: dict[str, dict[str, object]] = {}
    for interface in interfaces:
        assert isinstance(interface, list) and len(interface) == 4, ("Phase 14 architecture interface schema", interface)
        source, target, interface_type, status = (str(value) for value in interface)
        lineage = f"{ARCHITECTURE_LINEAGE_PREFIX}{source}>{target}"
        assert lineage not in lookup, ("duplicate Phase 14 architecture lineage", lineage)
        lookup[lineage] = {
            "source_system_id": source,
            "target_system_id": target,
            "interface_type": interface_type,
            "status": status,
            "explicitly_undirected": any(str(value).strip().lower() in {"undirected", "bidirectional"} for value in (interface_type, status)),
        }
    return lookup


def load_technology_lineage() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for path, key in ((PHASE15B_DEPENDENCIES, "dependency_state_id"), (PHASE15B_STATES, "state_id"), (PHASE15B_GOVERNANCE, "governance_state_id")):
        lookup.update({row[key]: row for row in read_csv(path)})
    return lookup


def build_relationships(system_ids: set[str]) -> list[dict[str, object]]:
    direct = load_relationship_rows()
    technology = load_technology_lineage()
    architecture = load_architecture_interfaces()
    rows: list[dict[str, object]] = []
    for rid, source, target, relation_class, mechanism, lineage, status in RELATION_SPECS:
        assert source in system_ids and target in system_ids, (rid, source, target)
        if lineage.startswith("AR-"):
            assert lineage in direct, lineage
            base = direct[lineage]
            assert base["source_system_id"] == source, (rid, "source endpoint", base["source_system_id"], source)
            assert base["target_system_id"] == target, (rid, "target endpoint", base["target_system_id"], target)
            assert base["normalized_relationship_class"] == relation_class, (rid, "relationship class", base["normalized_relationship_class"], relation_class)
            evidence_class = base["evidence_class"]
            source_artifact = base["source_artifact"]
            source_id = base["source_id"]
            source_local = base["local_relationship_id"]
            caveat = base["caveat"]
            direct_status = "direct" if evidence_class == "OBSERVED_DOCUMENTED" else "inferred"
            relationship_basis = "frozen_phase14_dependency_crosswalk"
        elif lineage.startswith("TDS-"):
            assert lineage in technology, (rid, "missing Phase 15B TDS lineage", lineage)
            base = technology[lineage]
            assert "system_a" in base and "system_b" in base, (rid, "Phase 15B TDS endpoint schema", lineage, base)
            assert_lineage_endpoint_compatibility(
                rid,
                source,
                target,
                base["system_a"],
                base["system_b"],
                lineage_kind="Phase 15B scenario dependency",
                source_endpoint_field="system_a",
                target_endpoint_field="system_b",
                explicitly_undirected=str(base.get("directionality", "")).strip().lower() in {"undirected", "bidirectional"},
            )
            evidence_class = "SCENARIO_STATE"
            source_artifact = "data/processed/scenarios/technology_dependency_states.csv"
            source_id = base.get("source_or_basis", "")
            source_local = lineage
            caveat = "Phase 15B scenario state is an optional modifier; it is not a 2026 baseline relationship."
            direct_status = "scenario-conditioned"
            relationship_basis = "phase15b_scenario_state"
        else:
            assert lineage.startswith(ARCHITECTURE_LINEAGE_PREFIX), (rid, "unsupported lineage kind", lineage)
            base = architecture.get(lineage)
            assert base is not None, (rid, "missing Phase 14 architecture lineage", lineage, source, target)
            assert_lineage_endpoint_compatibility(
                rid,
                source,
                target,
                str(base["source_system_id"]),
                str(base["target_system_id"]),
                lineage_kind="Phase 14 conceptual architecture",
                source_endpoint_field="interfaces[0]",
                target_endpoint_field="interfaces[1]",
                explicitly_undirected=bool(base["explicitly_undirected"]),
            )
            evidence_class = "INFERRED"
            source_artifact = "metadata/atlas_systems.yml"
            source_id = ""
            source_local = lineage.split(":", 1)[1]
            caveat = "System-level conceptual interface; not an exact entity join or documented local dependency."
            direct_status = "inferred"
            relationship_basis = "phase14_system_level_conceptual_architecture"
        rows.append({
            "relationship_id": rid,
            "source_system_id": source,
            "target_system_id": target,
            "relationship_class": relation_class,
            "propagation_mechanism": mechanism,
            "evidence_class": evidence_class,
            "direct_or_inferred": direct_status,
            "baseline_or_scenario": status,
            "relationship_basis": relationship_basis,
            "source_artifact": source_artifact,
            "source_relationship_id": source_local,
            "source_id": source_id,
            "source_lineage": f"{source_artifact}#{lineage}" if lineage.startswith(("AR-", "TDS-")) else lineage,
            "limitation": caveat,
            "spatial_character": "native source scale; no common geographic scale is inferred",
            "temporal_character": "source temporal basis retained; no event duration inferred",
            "reversibility": "context-dependent / not quantified",
            "uncertainty": "local uncertainty, native scale, and endpoint caveats remain in source artifact",
            "suitable_for_stress_test_propagation": "QUALITATIVE_ONLY",
            "notes": "Dependency or interface is not risk, failure probability, guaranteed effect, or causation. Co-location alone is not used.",
        })
    return rows


def build_rules(relationships: list[dict[str, object]], stressor_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_id = {row["relationship_id"]: row for row in relationships}
    initial_system = {str(row["stressor_id"]): str(row["initial_system_id"]) for row in stressor_rows}
    rows: list[dict[str, object]] = []
    for spec in RULE_SPECS:
        (rule_id, stressor, relation_id, stage, state, effect, enabling, limiting,
         temporal, spatial, reversible, technology_modifier, governance_modifier,
         response, second_order, uncertainty, status) = spec
        assert rule_id not in REMOVED_RULE_IDS, rule_id
        relationship = by_id[relation_id]
        assert stressor in initial_system, stressor
        source_system = str(relationship["source_system_id"])
        target_system = str(relationship["target_system_id"])
        if stage == 1:
            assert source_system == initial_system[stressor], (rule_id, "stage-1 source", source_system, initial_system[stressor])
            parent_rule_id = ""
            chain_relation_type = "parallel_initial_branch"
        else:
            parent = next(
                (
                    row for row in reversed(rows)
                    if row["stressor_id"] == stressor
                    and int(row["stage"]) == stage - 1
                    and row["target_system_id"] == source_system
                ),
                None,
            )
            assert parent is not None, (rule_id, "missing preceding parent", source_system)
            parent_rule_id = str(parent["rule_id"])
            chain_relation_type = "sequential"
        lineage_evidence_class = str(relationship["evidence_class"])
        application_evidence_class = RULE_APPLICATION_EVIDENCE.get(rule_id, lineage_evidence_class)
        if status == "scenario-conditioned":
            assert lineage_evidence_class == "SCENARIO_STATE"
            assert application_evidence_class in {"SCENARIO_STATE", "SCENARIO_ASSUMPTION"}
            direct_or_inferred = "scenario-conditioned"
            application_fit = "SCENARIO_STATE_APPLICATION"
        elif lineage_evidence_class == "SCENARIO_STATE":
            raise AssertionError((rule_id, "scenario source on baseline rule"))
        elif application_evidence_class == "OBSERVED_DOCUMENTED":
            assert lineage_evidence_class == "OBSERVED_DOCUMENTED", (rule_id, "observed rule from weaker lineage", lineage_evidence_class)
            direct_or_inferred = "direct"
            application_fit = "EXACT_SOURCE_APPLICATION"
        else:
            direct_or_inferred = "inferred"
            application_fit = RULE_APPLICATION_FIT.get(rule_id, "INFERRED_SOURCE_APPLICATION")
        assert response in {r[1] for r in RESPONSE_ROWS}
        rows.append({
            "rule_id": rule_id,
            "stage": stage,
            "stressor_id": stressor,
            "chain_parent_rule_id": parent_rule_id,
            "chain_relation_type": chain_relation_type,
            "source_system_id": source_system,
            "source_state_or_effect": state,
            "initial_or_prior_effect": effect,
            "relationship_id": relation_id,
            "relationship_class": relationship["relationship_class"],
            "target_system_id": target_system,
            "propagation_mechanism": relationship["propagation_mechanism"],
            "evidence_class": application_evidence_class,
            "lineage_evidence_class": lineage_evidence_class,
            "application_fit": application_fit,
            "direct_or_inferred": direct_or_inferred,
            "baseline_or_scenario": status,
            "enabling_condition": enabling,
            "limiting_condition": limiting,
            "temporal_character": temporal,
            "spatial_character": spatial,
            "reversibility": reversible,
            "technology_modifier": technology_modifier,
            "governance_modifier": governance_modifier,
            "response_option": next(r[0] for r in RESPONSE_ROWS if r[1] == response),
            "second_order_effect": second_order,
            "uncertainty": uncertainty,
            "source_lineage": relationship["source_lineage"],
            "notes": "Stage is an explicit qualitative chain position; parallel initial branches are not sequential propagation; repeated systems do not imply runaway feedback.",
        })
    return rows


def build_matrix(stressor_rows: list[dict[str, object]], rules: list[dict[str, object]], system_ids: list[str]) -> list[dict[str, object]]:
    initial = {row["stressor_id"]: row["initial_system_id"] for row in stressor_rows}
    stressor_status = {row["stressor_id"]: row["baseline_or_scenario"] for row in stressor_rows}
    direct: dict[str, set[str]] = {
        sid: {initial[sid]} if stressor_status[sid] == "BASELINE" else set()
        for sid in initial
    }
    indirect: dict[str, set[str]] = {sid: set() for sid in initial}
    scenario: dict[str, set[str]] = {sid: set() for sid in initial}
    for sid, system_id in initial.items():
        if stressor_status[sid] != "BASELINE":
            scenario[sid].add(str(system_id))
    for row in rules:
        stressor = str(row["stressor_id"])
        if row["baseline_or_scenario"] == "scenario-conditioned":
            scenario[stressor].add(str(row["target_system_id"]))
        elif int(row["stage"]) == 1:
            direct[stressor].add(str(row["target_system_id"]))
        else:
            indirect[stressor].add(str(row["target_system_id"]))
    not_assessed = {
        ("STRESS-INFECTIOUS-PRESSURE", "SYS-ECOLOGY"),
        ("STRESS-CYBER-DIGITAL", "SYS-ECOLOGY"),
        ("STRESS-DATA-PRIVACY", "SYS-ECOLOGY"),
    }
    rows: list[dict[str, object]] = []
    for stressor in sorted(initial):
        for system_id in system_ids:
            if (stressor, system_id) in not_assessed:
                cell = "NOT ASSESSED"
                basis = "Phase 16A bounded package does not assess this pairing."
            elif system_id in scenario[stressor]:
                cell = "SCENARIO-CONDITIONED"
                basis = "Scenario-conditioned stressor/pathway status takes precedence over initial-system matching."
            elif system_id in direct[stressor]:
                cell = "DIRECT"
                basis = "Immediate baseline source-system effect or explicit baseline stage-1 pathway."
            elif system_id in indirect[stressor]:
                cell = "INDIRECT"
                basis = "Explicit stage-2 qualitative chain from an accepted relationship; no transitive closure beyond listed stages."
            else:
                cell = "NO CURRENT DEFENSIBLE PATH"
                basis = "No Phase 14 relationship or explicit Phase 15 scenario interaction selected in Phase 16A."
            rows.append({
                "stressor_id": stressor,
                "system_id": system_id,
                "pathway_cell": cell,
                "basis": basis,
                "is_severity_measure": "false",
                "is_risk_or_vulnerability_score": "false",
                "notes": "Compatibility/pathway finding only; do not rank, sum, or interpret as severity, risk, or vulnerability.",
            })
    return rows


def build_figure(system_rows: list[dict[str, object]], relationship_rows: list[dict[str, object]]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "western-basin-phase16a"
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=180)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    colors = ["#38bdf8", "#a78bfa", "#fbbf24", "#34d399", "#fb7185", "#94a3b8"]
    labels = [
        ("STRESSOR", "climate • infrastructure • material • public health • information", 1.0, colors[0]),
        ("SYSTEM EFFECT", "nominal → stressed → constrained / degraded", 3.4, colors[1]),
        ("DEPENDENCY / INTERFACE", "Phase 14 relationship class retained", 5.8, colors[2]),
        ("PROPAGATION", "direct / inferred / scenario-conditioned", 8.2, colors[3]),
        ("RESPONSE / ADAPTATION", "option ≠ capacity ≠ success", 10.7, colors[4]),
        ("SECOND-ORDER EFFECT", "residual • delayed • redistributed • indeterminate", 13.0, colors[5]),
    ]
    for title, subtitle, x, color in labels:
        box = FancyBboxPatch((x - 0.75, 3.1), 1.55, 1.9, boxstyle="round,pad=0.04,rounding_size=0.08", facecolor="#172554", edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, 4.25, title, ha="center", va="center", color="white", fontsize=9, fontweight="bold", wrap=True)
        ax.text(x, 3.55, subtitle, ha="center", va="center", color="#cbd5e1", fontsize=6.8, wrap=True)
    for x in [2.0, 4.4, 6.8, 9.2, 11.95]:
        ax.annotate("", xy=(x + 0.55, 4.05), xytext=(x - 0.15, 4.05), arrowprops={"arrowstyle": "-|>", "color": "#e2e8f0", "linewidth": 1.8})
    ax.text(7.5, 7.25, "Western Basin Stress Propagation Architecture", ha="center", color="white", fontsize=18, fontweight="bold")
    ax.text(7.5, 6.72, "Atlas-facing conceptual figure • system-family aggregation • non-geographic • non-proportional", ha="center", color="#cbd5e1", fontsize=10)
    ax.text(7.5, 2.05, "System families represented: natural environment • infrastructure / technology • production / logistics • health / environment • institutional / human", ha="center", color="#cbd5e1", fontsize=8.5)
    legend = [("direct / documented", "#38bdf8", "solid"), ("inferred", "#a78bfa", "dotted"), ("scenario-conditioned", "#fbbf24", "dashdot"), ("response / adaptation", "#34d399", "solid")]
    x0 = 1.2
    for i, (text, color, style) in enumerate(legend):
        x = x0 + i * 3.25
        ax.plot([x, x + 0.45], [1.15, 1.15], color=color, linestyle=style, linewidth=2.6)
        ax.text(x + 0.55, 1.15, text, va="center", color="#e2e8f0", fontsize=8)
    ax.text(7.5, 0.38, "Line presence does not imply causation, proportional effect, failure, probability, risk, or vulnerability. Cycles require explicit support; technology is an optional modifier, not automatic protection.", ha="center", color="#fbbf24", fontsize=8)
    for ext in ("png", "svg"):
        fig.savefig(FIGURES / f"western_basin_stress_propagation_architecture.{ext}", bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)


def validate_technology_lineage(
    family: str,
    technology_id: str,
    lineage: str,
    phase15a_nodes: dict[str, dict[str, str]],
    phase15a_interfaces: dict[str, dict[str, str]],
    phase15a_dependencies: dict[str, dict[str, str]],
    phase15b_states: dict[str, dict[str, str]],
    phase15b_dependencies: dict[str, dict[str, str]],
    phase15b_governance: dict[str, dict[str, str]],
) -> None:
    if technology_id.startswith("REGIME-"):
        assert family == technology_id
        scenario_prefix = technology_id[-1]
        assert any(f"-{scenario_prefix}2050-" in ref or f"-{scenario_prefix}2075-" in ref for ref in re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage))
        return
    node = phase15a_nodes.get(technology_id)
    assert node is not None, technology_id
    assert family == node["technology_family"], (technology_id, family, node["technology_family"])
    refs = re.findall(r"(?:TSI|TDEP|TECH)-[A-Z0-9-]+", lineage)
    phase15a_matches = []
    for ref in refs:
        if ref.startswith("TSI-"):
            row = phase15a_interfaces.get(ref)
            assert row is not None, ref
            assert row["technology_id"] == technology_id, (ref, row["technology_id"], technology_id)
            phase15a_matches.append(ref)
        elif ref.startswith("TDEP-"):
            row = phase15a_dependencies.get(ref)
            assert row is not None, ref
            assert row["technology_id"] == technology_id, (ref, row["technology_id"], technology_id)
            phase15a_matches.append(ref)
        elif ref.startswith("TECH-"):
            assert ref == technology_id, (ref, technology_id)
            phase15a_matches.append(ref)
    assert phase15a_matches, (technology_id, lineage)
    phase15b_maps = {**phase15b_states, **phase15b_dependencies, **phase15b_governance}
    phase15b_refs = re.findall(r"(?:TSS|TDS|TGS)-[A-Z0-9-]+", lineage)
    assert phase15b_refs, (technology_id, lineage)
    for ref in phase15b_refs:
        row = phase15b_maps.get(ref)
        assert row is not None, ref
        referenced_families = set(row.get("technology_family", "").split(";"))
        assert family in referenced_families, (ref, family, referenced_families)


def build_reports(counts: dict[str, int], relationship_rows: list[dict[str, object]], rules: list[dict[str, object]], matrix: list[dict[str, object]]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["pathway_cell"] for row in matrix)
    evidence_counts = Counter(row["evidence_class"] for row in relationship_rows)
    (REPORTS / "phase16a_integrated_basin_dynamics.md").write_text(f"""# Phase 16A — Integrated Basin Dynamics Framework & Propagation Rules

Status: IMPLEMENTED / VALIDATED / UNDER CORRECTION / AWAITING FRESH INDEPENDENT REVIEW (working package).

## Purpose

Phase 16A defines a bounded qualitative chain:

`STRESSOR → INITIAL SYSTEM EFFECT → DEPENDENCY / INTERFACE → CROSS-SYSTEM PROPAGATION → RESPONSE / ADAPTATION → RESIDUAL OR SECOND-ORDER EFFECT`

It consumes the accepted/frozen Phase 14 interoperability architecture and uses Phase 15 technology interfaces and convergence regimes only as optional modifiers. It does not run Phase 16B stress tests.

## Package counts

- Stressors: {counts['stressors']}
- Propagation relationships: {counts['relationships']}
- Propagation rules: {counts['rules']}
- Adaptation/response mechanisms: {counts['responses']}
- Technology modifiers: {counts['technology_modifiers']}
- Feedback/coupling inventory rows: {counts['feedback']}
- System × stressor matrix cells: {counts['matrix']}
- Candidate Phase 16B stress tests: {counts['candidates']} (identified only)

Evidence classes in the propagation relationship table: {dict(sorted(evidence_counts.items()))}.

## Boundaries

This is not a quantitative risk model, calibrated forecast, probability model, resilience index, vulnerability score, Monte Carlo model, or system-dynamics simulator. It contains no ordinal numeric scores, probabilities, health-outcome forecasts, or causal claims from co-location. A dependency is not guaranteed failure; adaptation capacity is not successful adaptation; redundancy is not immunity; monitoring is not control; and decision support is not authority.

Infectious-disease and biosecurity content remains high-level: surveillance, diagnostics, workforce, supply-chain, communication, governance, and response coordination only. No pathogen engineering, transmission optimization, evasion, laboratory procedure, or operational attack detail is represented.

## Status

Phase 14: COMPLETE / ACCEPTED / FROZEN. Phase 15: COMPLETE / ACCEPTED / FROZEN. Phase 16A is the only implemented Phase 16 subphase. Phase 16B is APPROVED SCOPE / NOT IMPLEMENTED. Phase 17 is NOT IMPLEMENTED.

Active holds remain: Great Black Swamp C — HOLD / noncanonical; Toledo intake-coordinate discrepancy UNRESOLVED. Deferred maintenance remains unchanged.
""", encoding="utf-8", newline="\n")
    (REPORTS / "phase16a_propagation_framework.md").write_text(f"""# Phase 16A — Propagation Framework

## Rule semantics

Each rule names the source system, source state/effect, retained Phase 14 relationship class, target system, propagation mechanism, application evidence class, underlying lineage evidence class, enabling and limiting conditions, temporal/spatial character, reversibility, optional Phase 15 technology modifier, governance boundary, response option, second-order effect, uncertainty, and source lineage. `application_fit` records whether the cited relationship is an exact application, a qualified inference, or a scenario-state application.

Rules use explicit stage numbers and parent references. Stage 1 source systems equal the stressor initial system and use `parallel_initial_branch`; later stages require a preceding rule for the same stressor whose target is the later source and use `sequential`. The package does not calculate transitive closure; cycles are not treated as runaway feedback.

## Relationship classes retained

The framework keeps `physical flow`, `material flow`, `operational dependency`, `information / observation`, `governance / authority`, `ecological relationship`, `exposure pathway`, `surveillance / detection`, `population / mobility interface`, `scenario influence`, `high-level association`, and `unresolved / unclassified` distinct. It does not use generic causation as a replacement class.

## Evidence and lineage

Propagation relationships retain Phase 14 Atlas dependency-crosswalk IDs or an explicitly labeled Phase 14 system-level conceptual architecture pointer. Scenario-conditioned technology interactions retain Phase 15B state IDs and are never represented as baseline facts. A rule application cannot be stronger than its sole relationship lineage; direct/documented and inferred edges remain machine-readable and visually distinct.

## Reusable chain template

`chain_id, stage, stressor_id, chain_parent_rule_id, initial_system, initial_effect, relationship_id, target_system, propagation_mechanism, evidence_class, lineage_evidence_class, application_fit, technology_modifier, governance_modifier, response_option, second_order_effect, uncertainty, source_lineage`

Multiple stages are allowed. A repeated system is not a feedback loop unless the feedback inventory independently supports that interpretation.

## Qualitative system-state vocabulary

Nominal, stressed, constrained, degraded, redistributed, more dependent, less observable, more observable, more coupled, less interoperable, delayed, fragmented, adaptive, recovering, and indeterminate are descriptors only. They are not ordinal scores and “stressed” does not mean imminent failure.

## Matrix interpretation

The {len(matrix)}-cell system × stressor matrix answers only whether a defensible pathway is selected: {dict(sorted(status_counts.items()))}. Scenario-conditioned stressor/pathway status is evaluated before initial-system matching, so scenario-only initial systems are not baseline DIRECT cells. It is not a severity, risk, resilience, vulnerability, or ranking matrix. Rows and columns must not be summed.
""", encoding="utf-8", newline="\n")
    (REPORTS / "phase16a_candidate_stress_tests.md").write_text("""# Phase 16A — Candidate Phase 16B Stress Tests

The following six compound stress tests are identified for later review. None is executed in Phase 16A. Their status is `APPROVED SCOPE / NOT IMPLEMENTED`.

| Candidate | Compound stressors | Status |
|---|---|---|
| P16B-CAND-001 | Extreme heat + low flow + grid stress | APPROVED SCOPE / NOT IMPLEMENTED |
| P16B-CAND-002 | HAB / water-quality pressure + water-treatment disruption | APPROVED SCOPE / NOT IMPLEMENTED |
| P16B-CAND-003 | Freight / material disruption + industrial energy constraint | APPROVED SCOPE / NOT IMPLEMENTED |
| P16B-CAND-004 | Infectious-disease pressure + surveillance / data-governance friction | APPROVED SCOPE / NOT IMPLEMENTED |
| P16B-CAND-005 | Heavy precipitation / flooding + infrastructure / logistics disruption | APPROVED SCOPE / NOT IMPLEMENTED |
| P16B-CAND-006 | Cyber / digital-resilience stress + sensor / decision-support degradation | APPROVED SCOPE / NOT IMPLEMENTED |

Candidate descriptions remain qualitative and public-abstraction only. The infectious-disease candidate excludes incidence, outbreak probability, pathogen engineering, transmission optimization, evasion, and laboratory procedures. The cyber candidate excludes attack paths, exploits, sensitive topology, and operational attack detail.
""", encoding="utf-8", newline="\n")
    (REPORTS / "phase16a_qa.md").write_text(f"""# Phase 16A — QA and Scope Boundaries

Working-package QA is recorded for deterministic Python/R validation and the independent review gate.

## Required checks

- Phase 14 and Phase 15 status confirmed from repository authority surfaces.
- Frozen Phase 1–15 artifacts remain outside the write scope.
- Stressor, system-state, propagation, response, feedback, technology-modifier, matrix, and candidate schemas are deterministic.
- System IDs resolve to the frozen Phase 14 ontology.
- Relationship classes resolve to the frozen Phase 14 vocabulary.
- Evidence classes and direct/inferred/scenario-conditioned status remain distinct; derived evidence cannot be stronger than its sole source lineage.
- Stage-1 initial-system consistency, later-stage parent continuity, source/target orientation, stressor/mechanism fit, and technology-family lineage are enforced by builder and validators.
- Every relationship and rule retains source lineage.
- No relationship is created from co-location alone.
- No numeric risk/resilience/vulnerability scoring, probability, health forecast, unsupported causal claim, or harmful biosecurity detail is present.
- Active holds and deferred maintenance are preserved.
- Phase 16B candidate tests are identified only; Phase 16B and Phase 17 are not implemented.
- The conceptual figure is non-geographic, aggregated by system family, and non-proportional.

## Matrix result

The system × stressor matrix contains {counts['matrix']} pathway cells. It is a compatibility/pathway matrix only; it does not rank systems or sum rows/columns.

## Figure QA intent

`outputs/figures/western_basin_stress_propagation_architecture.png/.svg` must contain the six-stage stress-propagation chain, direct/documented, inferred, scenario-conditioned, and response/adaptation legend semantics, system-family aggregation, and non-proportional caveats.

## Active boundaries

Great Black Swamp: C — HOLD / noncanonical. Toledo intake-coordinate discrepancy: UNRESOLVED. Phase 6B manifest-status wording, Phase 3A missing historical manifest status, and Phase 2A superseded legacy worktree remain deferred.
""", encoding="utf-8", newline="\n")


def main() -> None:
    metadata = yaml.safe_load(VOCABULARY.read_text(encoding="utf-8"))
    ontology = yaml.safe_load(SYSTEMS.read_text(encoding="utf-8"))
    system_rows = ontology["systems"]
    system_ids = [row["system_id"] for row in system_rows]
    assert len(system_ids) == len(set(system_ids)) == 13
    stressor_rows = [
        {"stressor_id": sid, "stressor_class": cls, "label": label, "initial_system_id": system, "initial_effect": effect, "evidence_class": evidence, "source_lineage": lineage, "baseline_or_scenario": "BASELINE" if evidence not in {"SCENARIO_ASSUMPTION"} else "SCENARIO-CONDITIONED", "notes": "Bounded stressor class; not a probability, forecast, risk, or severity value."}
        for sid, cls, label, system, effect, evidence, lineage in STRESSORS
    ]
    relationships = build_relationships(set(system_ids))
    rules = build_rules(relationships, stressor_rows)
    matrix = build_matrix(stressor_rows, rules, system_ids)
    technology_rows = []
    phase15a_node_rows = read_csv(PHASE15A_NODES)
    phase15a_nodes = {row["technology_id"]: row for row in phase15a_node_rows}
    phase15a_interfaces = {row["interface_id"]: row for row in read_csv(PHASE15A_INTERFACES)}
    phase15a_dependencies = {row["dependency_id"]: row for row in read_csv(PHASE15A_DEPENDENCIES)}
    phase15b_states = {row["state_id"]: row for row in read_csv(PHASE15B_STATES)}
    phase15b_dependencies = {row["dependency_state_id"]: row for row in read_csv(PHASE15B_DEPENDENCIES)}
    phase15b_governance = {row["governance_state_id"]: row for row in read_csv(PHASE15B_GOVERNANCE)}
    for modifier_id, family, technology_id, effect, lineage, evidence, condition, effects in TECHNOLOGY_MODIFIERS:
        validate_technology_lineage(family, technology_id, lineage, phase15a_nodes, phase15a_interfaces, phase15a_dependencies, phase15b_states, phase15b_dependencies, phase15b_governance)
        technology_rows.append({
            "technology_modifier_id": modifier_id,
            "technology_family_or_regime": family,
            "phase15_technology_or_regime_id": technology_id,
            "modifier_effect": effect,
            "evidence_class": evidence,
            "optional_condition": condition,
            "effects_allowed": effects,
            "source_lineage": lineage,
            "notes": "Technology may reduce, delay, expose, couple, substitute, coordinate, or friction-shift a pathway; it is not automatically protective.",
        })
    response_rows = [{
        "response_id": rid, "response_mechanism": mechanism, "applies_to": systems,
        "enabling_condition": enabling, "limiting_condition": limiting,
        "evidence_class": evidence, "source_lineage": lineage,
        "adaptation_capacity_boundary": boundary,
        "notes": "Response option is not a guaranteed action, capacity, benefit, or outcome.",
    } for rid, mechanism, systems, enabling, limiting, evidence, lineage, boundary in RESPONSE_ROWS]
    feedback_rows = [{"feedback_id": fid, "coupling_pair": pair, "feedback_class": cls, "evidence_basis": basis, "plausible_interaction": interaction, "boundary": boundary, "numeric_gain_or_stability_claim": "false", "notes": "Inventory only; no dynamic simulation or runaway interpretation."} for fid, pair, cls, basis, interaction, boundary in FEEDBACK_ROWS]
    candidate_rows = [{"candidate_id": cid, "label": label, "stressor_ids": stressors, "system_ids": systems, "selection_basis": basis, "phase16a_rule_inputs": inputs, "status": status, "boundary": boundary, "executed": "false"} for cid, label, stressors, systems, basis, inputs, status, boundary in CANDIDATES]

    write_csv(INTEGRATION / "stressor_catalog.csv", list(stressor_rows[0]), stressor_rows)
    write_csv(INTEGRATION / "propagation_relationships.csv", list(relationships[0]), relationships)
    write_csv(INTEGRATION / "propagation_rules.csv", list(rules[0]), rules)
    write_csv(INTEGRATION / "adaptation_response_catalog.csv", list(response_rows[0]), response_rows)
    write_csv(INTEGRATION / "technology_modifier_catalog.csv", list(technology_rows[0]), technology_rows)
    write_csv(INTEGRATION / "feedback_coupling_inventory.csv", list(feedback_rows[0]), feedback_rows)
    write_csv(INTEGRATION / "system_stressor_matrix.csv", list(matrix[0]), matrix)
    write_csv(INTEGRATION / "phase16b_candidate_stress_tests.csv", list(candidate_rows[0]), candidate_rows)
    build_figure(system_rows, relationships)
    counts = {"stressors": len(stressor_rows), "relationships": len(relationships), "rules": len(rules), "responses": len(response_rows), "technology_modifiers": len(technology_rows), "feedback": len(feedback_rows), "matrix": len(matrix), "candidates": len(candidate_rows)}
    build_reports(counts, relationships, rules, matrix)

    artifacts = [
        "metadata/basin_dynamics_vocabulary.yml",
        "docs/phase_briefs/phase16_integrated_basin_dynamics.md",
        "docs/phase_briefs/phase16a_integrated_basin_dynamics_framework_propagation_rules.md",
        "docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md",
        "data/processed/integration/stressor_catalog.csv",
        "data/processed/integration/propagation_relationships.csv",
        "data/processed/integration/propagation_rules.csv",
        "data/processed/integration/adaptation_response_catalog.csv",
        "data/processed/integration/technology_modifier_catalog.csv",
        "data/processed/integration/feedback_coupling_inventory.csv",
        "data/processed/integration/system_stressor_matrix.csv",
        "data/processed/integration/phase16b_candidate_stress_tests.csv",
        "outputs/figures/western_basin_stress_propagation_architecture.png",
        "outputs/figures/western_basin_stress_propagation_architecture.svg",
        "reports/phase16a_integrated_basin_dynamics.md",
        "reports/phase16a_propagation_framework.md",
        "reports/phase16a_candidate_stress_tests.md",
        "reports/phase16a_qa.md",
        "reports/phase16a_independent_review_initial.md",
        "reports/phase16a_independent_review_second_failed.md",
        "src/python/systems/build_phase16a_dynamics.py",
        "src/python/systems/validate_phase16a_dynamics.py",
        "src/R/systems/validate_phase16a_dynamics.R",
    ]
    manifest = {
        "phase": "16A",
        "accepted_phase": "16A",
        "status": "implemented_validated_pending_sol_acceptance",
        "source_commit": BASE_SHA,
        "scope": "Integrated Basin Dynamics Framework & Propagation Rules",
        "phase16b_status": "APPROVED SCOPE / NOT IMPLEMENTED",
        "phase17_status": "NOT IMPLEMENTED",
        "qualitative_only": True,
        "no_numeric_scores_or_probabilities": True,
        "no_phase16b_execution": True,
        "counts": counts,
        "evidence_classes": metadata["evidence_classes"],
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate": "UNRESOLVED"},
        "deferred_maintenance_preserved": ["Phase 6B historical manifest-status wording mismatch", "Phase 3A missing historical manifest status", "Phase 2A superseded legacy worktree"],
        "artifacts": {path: {"sha256": sha256(ROOT / path), "bytes": (ROOT / path).stat().st_size} for path in artifacts},
    }
    (REPORTS / "phase16a_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "16A", "counts": counts, "manifest": "reports/phase16a_manifest.json"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
