"""Build the additive Phase 15A technology baseline and system interfaces."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
INTEGRATION = ROOT / "data/processed/integration"
METADATA = ROOT / "metadata"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
BRIEFS = ROOT / "docs/phase_briefs"

STATUS_VALUES = {
    "established",
    "commercially emerging",
    "demonstration / pilot",
    "research-stage",
    "speculative / long-horizon",
}
CURRENT_VALUES = {"current", "emerging", "speculative"}
FAMILIES = [
    "AI / ADVANCED COMPUTE / AUTOMATION",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS",
    "CYBERSECURITY / DIGITAL RESILIENCE",
    "ADVANCED ENERGY",
    "ADVANCED MATERIALS / MANUFACTURING",
    "QUANTUM TECHNOLOGIES",
    "BIOTECHNOLOGY / GENETIC ENGINEERING",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
]
SYSTEM_IDS = [
    "SYS-WATER", "SYS-MATERIALS", "SYS-ENERGY", "SYS-DATA", "SYS-FREIGHT",
    "SYS-ECOLOGY", "SYS-EXPOSURE", "SYS-BIOGEOCHEMISTRY", "SYS-CLIMATE",
    "SYS-GOVERNANCE", "SYS-POPULATION", "SYS-VECTOR-ECOLOGY", "SYS-INFECTIOUS-DISEASE",
]

NODE_FIELDS = [
    "technology_id", "technology_family", "technology_label", "technology_status",
    "capability_scope", "current_or_emerging", "regional_relevance", "source_id",
    "regional_evidence_source_id", "evidence_class", "governance_interface",
    "adoption_boundary", "uncertainty", "notes",
]
OBS_FIELDS = [
    "observation_id", "technology_id", "technology_family", "observation_type",
    "observation_label", "observation_status", "evidence_class", "claim_scope",
    "geographic_scope", "temporal_basis", "regional_relevance", "source_id",
    "regional_evidence_source_id", "uncertainty", "notes",
]
SOURCE_FIELDS = [
    "source_id", "title", "url", "source_type", "source_scope", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "regional_deployment_supported", "use_limitations", "retrieval_url", "retrieval_provenance",
]
INTERFACE_FIELDS = [
    "interface_id", "technology_id", "technology_family", "technology_label", "technology_status",
    "source_system_id", "target_system_id", "interface_type", "normalized_relationship_class",
    "evidence_class", "current_or_emerging", "regional_relevance", "dependency_basis",
    "governance_interface", "uncertainty", "source_id", "notes",
]
DEPENDENCY_FIELDS = [
    "dependency_id", "technology_id", "technology_family", "dependency_class", "dependency_role",
    "dependency_label", "affected_system_id", "technology_status", "evidence_class",
    "regional_relevance", "dependency_basis", "limitation", "governance_interface", "uncertainty",
    "source_id", "notes",
]
UNCERTAINTY_FIELDS = [
    "uncertainty_id", "technology_id", "technology_family", "affected_system_id", "uncertainty_type",
    "uncertainty_status", "uncertainty", "evidence_class", "source_id", "regional_evidence_source_id",
    "notes",
]

TECHNOLOGIES = [
    {
        "technology_id": "TECH-AI-COMPUTE",
        "technology_family": FAMILIES[0],
        "technology_label": "AI / advanced compute decision support",
        "technology_status": "commercially emerging",
        "capability_scope": "Models, optimization, forecasting, and decision-support tools for human-supervised use.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-DOE-AI-RECOMMENDATIONS", "regional_evidence_source_id": "REG-PHASE14B-ATLAS",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Decision support only; no autonomous legal, operational, or enforcement authority.",
        "adoption_boundary": "AI capability and compute capacity do not establish reliable deployment or useful intelligence.",
        "uncertainty": "Model validity, data quality, compute access, operator trust, and deployment continuity are unresolved.",
        "notes": "Regional interface is inferred from existing energy, data, water, freight, health, and governance systems; local AI deployment is not claimed.",
    },
    {
        "technology_id": "TECH-AI-INDUSTRIAL-AUTOMATION",
        "technology_family": FAMILIES[0],
        "technology_label": "Industrial automation and machine-assisted operations",
        "technology_status": "commercially emerging",
        "capability_scope": "Machine-assisted inspection, scheduling, process optimization, and bounded automation.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-NIST-MANUFACTURING", "regional_evidence_source_id": "REG-PHASE5A-FREIGHT",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Human/operator accountability remains separate from automated recommendation or actuation; automation is not autonomous authority.",
        "adoption_boundary": "A manufacturing capability is not evidence of adoption at a named Western Basin facility.",
        "uncertainty": "Workforce, integration, safety validation, and continuity requirements are unresolved.",
        "notes": "Phase 5 industrial and freight nodes provide the regional interface, not proof of advanced automation.",
    },
    {
        "technology_id": "TECH-SENS-ENVIRONMENTAL",
        "technology_family": FAMILIES[1],
        "technology_label": "Advanced environmental sensing and observing",
        "technology_status": "established",
        "capability_scope": "In-situ, remote, networked, and quality-controlled measurement of environmental conditions.",
        "current_or_emerging": "current", "regional_relevance": "current",
        "source_id": "EXT-NOAA-IOOS", "regional_evidence_source_id": "REG-PHASE4A-DATA",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Measurement supports interpretation and decisions; observation is not enforcement or authority.",
        "adoption_boundary": "A sensing platform measures; interpretation, decision, and enforcement remain separate steps.",
        "uncertainty": "Coverage, calibration, timeliness, representativeness, and data stewardship vary.",
        "notes": "Existing Phase 4A public observation chains establish a current regional interface; no exhaustive advanced-sensor inventory is added.",
    },
    {
        "technology_id": "TECH-SENS-AUTONOMOUS",
        "technology_family": FAMILIES[1],
        "technology_label": "Autonomous and mobile environmental observing",
        "technology_status": "established",
        "capability_scope": "Autonomous or mobile platforms that collect environmental measurements or support bounded inspection.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-NOAA-IOOS-GLIDERS", "regional_evidence_source_id": "REG-PHASE3B-ENERGY-DEPENDENCIES",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Autonomous collection does not create decision authority, consent, or enforcement power.",
        "adoption_boundary": "Platform capability does not establish routine regional operation or reliable interpretation.",
        "uncertainty": "Communications, battery/energy, weather, retrieval, safety, and data-quality dependencies are unresolved.",
        "notes": "Potential interface to water, energy, freight, exposure, and infectious-disease observation systems remains qualitative.",
    },
    {
        "technology_id": "TECH-CYBER-RESILIENCE",
        "technology_family": FAMILIES[2],
        "technology_label": "Defensive cybersecurity and digital resilience",
        "technology_status": "established",
        "capability_scope": "Asset identification, authentication, secure configuration, monitoring, continuity, recovery, and incident communication.",
        "current_or_emerging": "current", "regional_relevance": "current",
        "source_id": "EXT-CISA-CPG", "regional_evidence_source_id": "REG-PHASE14B-ATLAS",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Defensive risk management, accountability, continuity, and recovery; no offensive technique or attack procedure.",
        "adoption_boundary": "A framework or goal does not demonstrate implementation, maturity, or uninterrupted service.",
        "uncertainty": "Asset inventories, redundancy, authentication coverage, recovery time, and cross-organization coordination are unresolved.",
        "notes": "Interfaces are intentionally kept at defensive/system-resilience level for water, grid, industry, freight, health, and municipal services.",
    },
    {
        "technology_id": "TECH-CYBER-PQC",
        "technology_family": FAMILIES[2],
        "technology_label": "Post-quantum cryptographic transition",
        "technology_status": "commercially emerging",
        "capability_scope": "Migration planning and deployment of quantum-resistant cryptographic standards and inventory practices.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-NIST-PQC", "regional_evidence_source_id": "REG-PHASE4B-INFO-GOV",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Trust, authentication, procurement, standards, and lifecycle governance; not a prediction of quantum attack timing.",
        "adoption_boundary": "Published standards and migration guidance do not prove local migration completion.",
        "uncertainty": "Legacy inventories, vendor support, interoperability, cost, and migration sequencing are unresolved.",
        "notes": "This is a defensive transition context connected to data and municipal systems, not an offensive cyber model.",
    },
    {
        "technology_id": "TECH-ENERGY-ADVANCED-NUCLEAR",
        "technology_family": FAMILIES[3],
        "technology_label": "Advanced nuclear reactors",
        "technology_status": "demonstration / pilot",
        "capability_scope": "Reactor concepts and demonstration programs intended to mature advanced nuclear generation.",
        "current_or_emerging": "emerging", "regional_relevance": "speculative",
        "source_id": "EXT-DOE-ARDP", "regional_evidence_source_id": "REG-PHASE3A-ENERGY",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Regulatory, siting, ownership, operation, fuel, and emergency-planning roles remain separate.",
        "adoption_boundary": "Demonstration support is not commercial availability, dependable regional generation, or local deployment.",
        "uncertainty": "Licensing, cost, fuel supply, cooling, workforce, interconnection, and public legitimacy are unresolved.",
        "notes": "The regional interface is a strategic possibility over the frozen energy baseline; no new reactor is added to the basin inventory.",
    },
    {
        "technology_id": "TECH-ENERGY-LDES",
        "technology_family": FAMILIES[3],
        "technology_label": "Long-duration and grid-scale energy storage",
        "technology_status": "demonstration / pilot",
        "capability_scope": "Storage systems intended to shift energy across longer durations or support grid services.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-DOE-ENERGY-STORAGE", "regional_evidence_source_id": "REG-PHASE3B-ENERGY-DEPENDENCIES",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Storage service, dispatch, ownership, and grid authority remain distinct; no dispatch schedule is modeled.",
        "adoption_boundary": "A storage pathway does not establish duration, capacity, dispatch, or regional adoption.",
        "uncertainty": "Duration, degradation, materials, interconnection, market rules, and replacement supply are unresolved.",
        "notes": "Phase 3 storage assets are reused context; this record does not alter their frozen capacity or status.",
    },
    {
        "technology_id": "TECH-ENERGY-DISTRIBUTED",
        "technology_family": FAMILIES[3],
        "technology_label": "Distributed energy and microgrid coordination",
        "technology_status": "commercially emerging",
        "capability_scope": "Distributed generation, storage, controls, and continuity arrangements at generalized system level; this record uses accepted regional energy context rather than a national deployment claim.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "REG-PHASE3A-ENERGY", "regional_evidence_source_id": "REG-PHASE3A-ENERGY",
        "evidence_class": "CONTEXT_REUSED",
        "governance_interface": "Coordination and continuity support do not imply feeder topology, automatic control, or service-territory assignment.",
        "adoption_boundary": "Capability does not establish a microgrid, islanding behavior, or dependable resilience benefit.",
        "uncertainty": "Interconnection, control trust, maintenance, fuel, storage duration, and ownership are unresolved.",
        "notes": "The existing energy/grid/compute package is reused without rebuilding the energy system.",
    },
    {
        "technology_id": "TECH-ENERGY-HYDROGEN",
        "technology_family": FAMILIES[3],
        "technology_label": "Hydrogen production, storage, and use",
        "technology_status": "demonstration / pilot",
        "capability_scope": "Hydrogen as an energy carrier for selected industrial, storage, and heavy-transport interfaces.",
        "current_or_emerging": "emerging", "regional_relevance": "speculative",
        "source_id": "EXT-DOE-H2HUBS", "regional_evidence_source_id": "REG-PHASE5A-FREIGHT",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Production, delivery, end-use, safety, environmental permitting, and market coordination remain separate.",
        "adoption_boundary": "A national hub program is not evidence of a Western Basin hydrogen project or supply chain.",
        "uncertainty": "Feedstock, water, electricity, storage, delivery, demand, and regional permitting are unresolved.",
        "notes": "Hydrogen is retained as an emerging strategic interface, not a current regional deployment claim.",
    },
    {
        "technology_id": "TECH-ENERGY-FUSION",
        "technology_family": FAMILIES[3],
        "technology_label": "Fusion energy research",
        "technology_status": "research-stage",
        "capability_scope": "Research and development toward a future fusion energy source and supporting materials/diagnostics.",
        "current_or_emerging": "speculative", "regional_relevance": "speculative",
        "source_id": "EXT-DOE-FUSION", "regional_evidence_source_id": "REG-PHASE3A-ENERGY",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Research, regulation, commercialization, and operation remain distinct.",
        "adoption_boundary": "Research trajectory is not commercial availability, firm power, or current regional generation.",
        "uncertainty": "Foundational science, materials, fuel cycle, cost, licensing, and deployment pathway are unresolved.",
        "notes": "Fusion is a bounded strategic watch item only; no current Western Basin fusion facility is represented.",
    },
    {
        "technology_id": "TECH-MATERIALS-ADVANCED",
        "technology_family": FAMILIES[4],
        "technology_label": "Advanced materials and smart manufacturing",
        "technology_status": "commercially emerging",
        "capability_scope": "Measurement, process control, advanced materials, and manufacturing methods that may affect industrial products.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-NIST-MANUFACTURING", "regional_evidence_source_id": "REG-PHASE2-MATERIALS",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Standards, quality, safety, procurement, and ownership remain separate from production authority.",
        "adoption_boundary": "National manufacturing capability does not establish a named regional facility's process or product adoption.",
        "uncertainty": "Feedstock, qualification, workforce, equipment, recycling, and market demand are unresolved.",
        "notes": "Phase 2 materials and Phase 5 industry are reused as regional interface context; no capability is invented for Elmore, Woodville, Genoa, or Luckey.",
    },
    {
        "technology_id": "TECH-MATERIALS-CIRCULAR",
        "technology_family": FAMILIES[4],
        "technology_label": "Sustainable circular materials management",
        "technology_status": "established",
        "capability_scope": "Life-cycle material reuse, recovery, and recycling interfaces.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-EPA-SMM", "regional_evidence_source_id": "REG-PHASE5A-FREIGHT",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Material certification, waste/recovery regulation, and production decisions remain role-bounded.",
        "adoption_boundary": "A plausible materials interface is not a documented local recycling or additive-manufacturing operation.",
        "uncertainty": "Material recovery rates, quality, energy, water, waste classification, and customer demand are unresolved.",
        "notes": "The interface remains system-level and non-quantitative.",
    },
    {
        "technology_id": "TECH-QUANTUM-SENSING",
        "technology_family": FAMILIES[5],
        "technology_label": "Quantum sensing and timing",
        "technology_status": "research-stage",
        "capability_scope": "Quantum-enabled measurement and timing concepts for high-precision sensing or synchronization.",
        "current_or_emerging": "speculative", "regional_relevance": "speculative",
        "source_id": "EXT-NIST-QIS", "regional_evidence_source_id": "REG-PHASE4A-DATA",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Measurement standards, calibration, procurement, and interpretation remain separate.",
        "adoption_boundary": "Laboratory capability is not operational deployment in basin water, grid, or ecological monitoring.",
        "uncertainty": "Robustness, cost, calibration, field integration, and useful regional signal are unresolved.",
        "notes": "Retained as a low-priority watch item with a defensible data/sensing interface.",
    },
    {
        "technology_id": "TECH-QUANTUM-COMPUTING",
        "technology_family": FAMILIES[5],
        "technology_label": "Quantum computing and optimization",
        "technology_status": "research-stage",
        "capability_scope": "Quantum-computing research and possible future optimization, simulation, or chemistry applications.",
        "current_or_emerging": "speculative", "regional_relevance": "speculative",
        "source_id": "EXT-NIST-QIS", "regional_evidence_source_id": "REG-PHASE3A-ENERGY",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Research, access, standards, and procurement remain distinct from operational decision authority.",
        "adoption_boundary": "Quantum research is not economically transformative application, useful intelligence, or local deployment.",
        "uncertainty": "Error correction, algorithms, access, cost, workforce, and comparative advantage are unresolved.",
        "notes": "The regional interface is limited to compute, optimization, materials, and cryptographic transition context.",
    },
    {
        "technology_id": "TECH-BIO-DIAGNOSTICS",
        "technology_family": FAMILIES[6],
        "technology_label": "Genomic diagnostics and environmental molecular monitoring",
        "technology_status": "commercially emerging",
        "capability_scope": "Sequencing, molecular detection, diagnostics, and bioinformatics for public-health or environmental interpretation.",
        "current_or_emerging": "emerging", "regional_relevance": "emerging",
        "source_id": "EXT-CDC-AMD", "regional_evidence_source_id": "REG-PHASE13A-DISEASE",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Laboratory quality, privacy, reporting, public communication, and response roles remain distinct.",
        "adoption_boundary": "National or state capacity does not establish a local laboratory result, disease incidence, or transmission finding.",
        "uncertainty": "Sampling, laboratory capacity, attribution, turnaround, data sharing, and interpretation are unresolved.",
        "notes": "The record is high-level and does not include pathogen engineering, wet-lab protocols, or operational misuse detail.",
    },
    {
        "technology_id": "TECH-BIO-BIOMANUFACTURING",
        "technology_family": FAMILIES[6],
        "technology_label": "Biomanufacturing and industrial biotechnology",
        "technology_status": "commercially emerging",
        "capability_scope": "Biological production pathways for materials, products, agriculture, or industrial processes.",
        "current_or_emerging": "emerging", "regional_relevance": "speculative",
        "source_id": "EXT-NIST-MANUFACTURING", "regional_evidence_source_id": "REG-PHASE2-MATERIALS",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Biosafety, quality, environmental review, intellectual property, and supply-chain oversight remain separate.",
        "adoption_boundary": "General biomanufacturing capability does not demonstrate a Western Basin plant, product, or economic effect.",
        "uncertainty": "Feedstocks, water, energy, containment, qualification, workforce, and markets are unresolved.",
        "notes": "High-level industrial interface only; no biological production protocol is modeled.",
    },
    {
        "technology_id": "TECH-DATA-GOVERNANCE",
        "technology_family": FAMILIES[7],
        "technology_label": "Privacy, surveillance, and data governance",
        "technology_status": "established",
        "capability_scope": "Data stewardship, privacy risk management, access control, provenance, retention, and accountable use of observations.",
        "current_or_emerging": "current", "regional_relevance": "current",
        "source_id": "EXT-NIST-PRIVACY", "regional_evidence_source_id": "REG-PHASE4B-INFO-GOV",
        "evidence_class": "OBSERVED_DOCUMENTED",
        "governance_interface": "Observation is not authority; data availability is not permission; technical capability is not legal authority.",
        "adoption_boundary": "A framework or sensor network does not establish justified intervention, consent, or lawful use.",
        "uncertainty": "Data quality, legal basis, consent, access, interoperability, public trust, and retention are unresolved.",
        "notes": "Phase 4 and Phase 10 are reused without creating a privacy-impact assessment or surveillance-state scenario.",
    },
]

# Each tuple is technology_id, target system, interface type, normalized class, basis, governance, uncertainty, source.
INTERFACE_SPECS = [
    ("TECH-AI-COMPUTE", "SYS-ENERGY", "grid and load decision support", "operational dependency", "Compute, data, communications, and operator review are required; no dispatch or control is inferred.", "Decision support is not autonomous authority or grid control.", "Model validity and continuity are unresolved.", "REG-PHASE3A-ENERGY"),
    ("TECH-AI-COMPUTE", "SYS-WATER", "water-system decision support", "information / observation", "Existing water observations can be inputs to analysis; sensor coverage and treatment operations remain local.", "Recommendation is not treatment authority, intake control, or legal mandate.", "Toledo intake coordinate discrepancy and operating details remain unresolved.", "REG-PHASE4A-DATA"),
    ("TECH-AI-COMPUTE", "SYS-DATA", "environmental modeling and analytics", "information / observation", "Phase 4 observation-to-decision chains provide a current data interface.", "Analysis is not an institutional decision or enforcement action.", "Data quality, representativeness, and model error are unresolved.", "REG-PHASE4B-INFO-GOV"),
    ("TECH-AI-COMPUTE", "SYS-CLIMATE", "climate and hazard modeling", "information / observation", "Phase 9 hazard observations provide a regional context for model-assisted interpretation.", "Model output is not a hazard forecast, probability, or emergency authority.", "Resolution, model error, and event attribution are unresolved.", "REG-PHASE9A-CLIMATE"),
    ("TECH-AI-INDUSTRIAL-AUTOMATION", "SYS-FREIGHT", "industrial optimization and logistics", "operational dependency", "Freight and industrial nodes provide a documented system context; facility automation is not claimed.", "Automation does not establish operator authority, route selection, or shipment volume.", "Facility integration, workforce, and continuity are unresolved.", "REG-PHASE5A-FREIGHT"),
    ("TECH-AI-INDUSTRIAL-AUTOMATION", "SYS-MATERIALS", "process and materials optimization", "operational dependency", "Phase 2 materials processing and Phase 5 industry provide regional context.", "A recommendation is not a production decision or capability claim.", "Nonlocal feed, equipment, and qualification remain unresolved.", "REG-PHASE2-MATERIALS"),
    ("TECH-AI-COMPUTE", "SYS-INFECTIOUS-DISEASE", "public-health surveillance analytics", "surveillance / detection", "Phase 13 surveillance and reporting interfaces support a high-level analytics connection.", "Analytics is not diagnosis, incidence, outbreak declaration, or response authority.", "Sampling, reporting, and interpretation remain uncertain.", "REG-PHASE13A-DISEASE"),
    ("TECH-SENS-ENVIRONMENTAL", "SYS-WATER", "water-quality observation", "surveillance / detection", "Phase 4A and Phase 8/13 water-observation context supports a current regional interface.", "Measurement is not treatment failure, exposure, or enforcement.", "Coverage, calibration, timing, and representativeness vary.", "REG-PHASE4A-DATA"),
    ("TECH-SENS-ENVIRONMENTAL", "SYS-ECOLOGY", "ecosystem observation", "surveillance / detection", "Phase 6 ecological and Phase 12 vector observation contexts support measurement interfaces.", "Observation is not habitat enforcement, abundance, or disease incidence.", "Detection is not establishment; ecological interpretation remains separate.", "REG-PHASE6A-ECOLOGY"),
    ("TECH-SENS-ENVIRONMENTAL", "SYS-BIOGEOCHEMISTRY", "nutrient and runoff observation", "surveillance / detection", "Phase 8 nutrient and water-carrier records provide a regional observation context.", "Measurement is not a load estimate, bloom forecast, or control result.", "Seasonal coverage, source apportionment, and retention are unresolved.", "REG-PHASE8A-BGC"),
    ("TECH-SENS-AUTONOMOUS", "SYS-ENERGY", "infrastructure inspection", "operational dependency", "Phase 3 energy assets provide generalized inspection context, not an autonomous inspection deployment.", "Inspection does not create operational control or access authority.", "Weather, energy, communications, and retrieval are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
    ("TECH-SENS-AUTONOMOUS", "SYS-FREIGHT", "corridor and asset inspection", "operational dependency", "Phase 5 corridors provide a bounded freight interface; no exact route or sensor fleet is added.", "Inspection is not carrier control, enforcement, or shipment attribution.", "Coverage, safety, and data custody are unresolved.", "REG-PHASE5A-FREIGHT"),
    ("TECH-SENS-AUTONOMOUS", "SYS-EXPOSURE", "environmental-health observation", "surveillance / detection", "Phase 7 monitoring pathways provide a context for potential measurement.", "Measurement is not personal exposure, dose, illness, or intervention authority.", "Receptor contact and dose remain unknown.", "REG-PHASE7A-EXPOSURE"),
    ("TECH-CYBER-RESILIENCE", "SYS-WATER", "defensive continuity", "operational dependency", "Phase 4 and Phase 14 identify water/data interfaces without reconstructing control topology.", "Resilience planning is not an attack path or operational command.", "Redundancy, recovery, and authentication coverage are unresolved.", "REG-PHASE14B-ATLAS"),
    ("TECH-CYBER-RESILIENCE", "SYS-ENERGY", "defensive grid resilience", "operational dependency", "Phase 3B records generalized communications and energy dependencies.", "Defensive security does not imply offensive capability or control authority.", "Continuity and restoration performance are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
    ("TECH-CYBER-RESILIENCE", "SYS-FREIGHT", "defensive logistics continuity", "operational dependency", "Phase 5C identifies freight and gateway dependencies at public abstraction.", "No exploit, target, route, or sensitive logistics detail is modeled.", "Vendor, carrier, and recovery dependencies are unresolved.", "REG-PHASE5C-FREIGHT"),
    ("TECH-CYBER-RESILIENCE", "SYS-INFECTIOUS-DISEASE", "public-health digital continuity", "operational dependency", "Phase 13 surveillance and response interfaces depend on information continuity.", "Continuity planning is not disease incidence or an attack procedure.", "Laboratory, reporting, and recovery dependencies are unresolved.", "REG-PHASE13A-DISEASE"),
    ("TECH-CYBER-PQC", "SYS-DATA", "cryptographic trust transition", "information / observation", "Phase 4 information systems provide a regional data-governance context.", "Authentication and trust are not permission or authority.", "Inventory and migration sequencing are unresolved.", "REG-PHASE4B-INFO-GOV"),
    ("TECH-ENERGY-ADVANCED-NUCLEAR", "SYS-ENERGY", "advanced generation possibility", "energy flow", "Phase 3 energy baseline is the affected system; DOE evidence is a national demonstration context.", "Licensing and operation are not inferred from research or demonstration support.", "Commercial availability, firm power, and siting are unresolved.", "REG-PHASE3A-ENERGY"),
    ("TECH-ENERGY-LDES", "SYS-ENERGY", "long-duration storage interface", "energy flow", "Phase 3 storage context supports a qualitative storage interface only.", "Storage capability is not dispatch authority or dependable capacity.", "Duration, degradation, and replacement are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
    ("TECH-ENERGY-LDES", "SYS-WATER", "storage and cooling dependency", "operational dependency", "Water is an enabling dependency for selected energy technologies; plant-specific conditions are not modeled.", "A cooling dependency is not a water withdrawal or permit claim.", "Technology-specific water requirements are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
    ("TECH-ENERGY-DISTRIBUTED", "SYS-ENERGY", "distributed generation/storage interface", "energy flow", "Phase 3 generation and storage assets provide system context without feeder modeling.", "Distributed capability is not service-territory or islanding authority.", "Interconnection, ownership, and continuity are unresolved.", "REG-PHASE3A-ENERGY"),
    ("TECH-ENERGY-HYDROGEN", "SYS-MATERIALS", "hydrogen material-input interface", "material flow", "Phase 2 materials and DOE hub evidence support a strategic interface, not local supply.", "Fuel/material input is not electricity flow or local production.", "Feedstock, water, and delivery are unresolved.", "REG-PHASE2-MATERIALS"),
    ("TECH-ENERGY-HYDROGEN", "SYS-FREIGHT", "heavy-industry and freight energy carrier", "material flow", "Phase 5 freight/industry context supports a possible carrier interface.", "A national hub program is not a regional route, shipment, or facility claim.", "Demand, storage, delivery, and safety are unresolved.", "REG-PHASE5A-FREIGHT"),
    ("TECH-ENERGY-FUSION", "SYS-ENERGY", "fusion generation research interface", "energy flow", "DOE research evidence supports a long-horizon strategic interface only.", "Research is not generation, interconnection, or local deployment.", "Foundational science, materials, and commercialization are unresolved.", "REG-PHASE3A-ENERGY"),
    ("TECH-MATERIALS-ADVANCED", "SYS-MATERIALS", "advanced material process interface", "material flow", "Phase 2 processing and NIST manufacturing evidence support a qualitative capability interface.", "Manufacturing methods do not identify a local adopted process.", "Feedstock, qualification, and workforce are unresolved.", "REG-PHASE2-MATERIALS"),
    ("TECH-MATERIALS-ADVANCED", "SYS-FREIGHT", "manufacturing supply-chain interface", "operational dependency", "Phase 5 freight nodes provide logistics context without a facility route or volume.", "Supply-chain relevance is not shipment evidence.", "Mode, customer, and substitution are unresolved.", "REG-PHASE5A-FREIGHT"),
    ("TECH-MATERIALS-CIRCULAR", "SYS-MATERIALS", "recovery and circular-material interface", "material flow", "Existing materials records support a bounded recycling/circular interface.", "A circular relationship is not a documented recovery facility or rate.", "Recovery quality and markets are unresolved.", "REG-PHASE2-MATERIALS"),
    ("TECH-MATERIALS-CIRCULAR", "SYS-ENERGY", "material-process energy dependency", "operational dependency", "Materials processing is connected qualitatively to the frozen energy system.", "Energy dependence is not a capacity or outage claim.", "Process energy and substitution are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
    ("TECH-QUANTUM-SENSING", "SYS-DATA", "quantum measurement interface", "surveillance / detection", "NIST describes quantum sensing as a research/industry measurement direction; Phase 4 provides data context.", "Measurement is not interpretation, authority, or enforcement.", "Field readiness and useful signal are unresolved.", "REG-PHASE4A-DATA"),
    ("TECH-QUANTUM-SENSING", "SYS-WATER", "high-precision water observation watch item", "high-level association", "Water observations are a defensible possible application context, not local deployment.", "Possible measurement does not establish intake monitoring or decision authority.", "Technology utility and local integration are unresolved.", "REG-PHASE4A-DATA"),
    ("TECH-QUANTUM-COMPUTING", "SYS-ENERGY", "optimization research interface", "operational dependency", "Energy planning is an existing system context; no quantum advantage or local use is claimed.", "Optimization output is not dispatch or grid authority.", "Algorithmic advantage, access, and cost are unresolved.", "REG-PHASE3A-ENERGY"),
    ("TECH-QUANTUM-COMPUTING", "SYS-FREIGHT", "logistics optimization watch item", "operational dependency", "Freight planning is a plausible system interface without shipment or route modeling.", "Optimization is not carrier authority or route evidence.", "Useful performance and data access are unresolved.", "REG-PHASE5A-FREIGHT"),
    ("TECH-BIO-DIAGNOSTICS", "SYS-INFECTIOUS-DISEASE", "genomic detection and diagnosis", "surveillance / detection", "CDC AMD evidence and Phase 13 surveillance provide a high-level detection interface.", "Detection is not incidence, attribution certainty, outbreak declaration, or treatment authority.", "Sampling, laboratory capacity, and interpretation are unresolved.", "REG-PHASE13A-DISEASE"),
    ("TECH-BIO-DIAGNOSTICS", "SYS-WATER", "environmental molecular monitoring", "surveillance / detection", "Water and wastewater are existing Phase 1/4/13 contexts; no new local result is asserted.", "A molecular signal is not contamination, exposure, dose, or illness.", "Sampling and source attribution are unresolved.", "REG-PHASE13A-DISEASE"),
    ("TECH-BIO-BIOMANUFACTURING", "SYS-MATERIALS", "biomanufacturing materials interface", "material flow", "Materials and manufacturing provide a regional interface for possible bio-based production.", "General capability is not a local plant, product, or process.", "Feedstock, water, energy, containment, and qualification are unresolved.", "REG-PHASE2-MATERIALS"),
    ("TECH-BIO-DIAGNOSTICS", "SYS-ECOLOGY", "One Health biological monitoring", "ecological relationship", "CDC One Health and Phase 6/12 ecology provide a shared human-animal-environment context.", "Shared context is not a disease, abundance, or causation claim.", "Attribution, monitoring coverage, and coordination are unresolved.", "REG-PHASE12A-VECTOR"),
    ("TECH-BIO-DIAGNOSTICS", "SYS-VECTOR-ECOLOGY", "vector and host surveillance", "surveillance / detection", "Phase 12 vector surveillance provides a regional biological-observation context.", "Detection is not establishment, human infection, transmission, or disease burden.", "Sampling effort, detection sensitivity, and local distribution are unresolved.", "REG-PHASE12A-VECTOR"),
    ("TECH-BIO-DIAGNOSTICS", "SYS-GOVERNANCE", "biosecurity governance lens", "governance / authority", "Phase 10 governance and Phase 13 response interfaces support a bounded oversight lens.", "Oversight and coordination are not proof of a threat or operational control.", "Roles, communication, and response capacity are unresolved.", "REG-PHASE10A-GOVERNANCE"),
    ("TECH-DATA-GOVERNANCE", "SYS-DATA", "sensor and data stewardship", "governance / authority", "Phase 4 observation and Phase 14 registry records provide direct regional system context.", "Data availability is not permission; observation is not authority.", "Access, provenance, and retention are unresolved.", "REG-PHASE4B-INFO-GOV"),
    ("TECH-DATA-GOVERNANCE", "SYS-GOVERNANCE", "privacy and accountability interface", "governance / authority", "Phase 10 actor/authority distinctions provide the institutional context.", "Technical capability is not legal authority or justified intervention.", "Legal basis, consent, and public legitimacy are unresolved.", "REG-PHASE10A-GOVERNANCE"),
    ("TECH-DATA-GOVERNANCE", "SYS-POPULATION", "mobility and utility data governance", "population / mobility interface", "Phase 11 aggregate mobility and settlement data provide context without individual profiling.", "Aggregate data is not individual movement, identity, or permission.", "Scale, privacy, and representativeness are unresolved.", "REG-PHASE11A-POPULATION"),
    ("TECH-DATA-GOVERNANCE", "SYS-INFECTIOUS-DISEASE", "public-health data stewardship", "surveillance / detection", "Phase 13 surveillance records provide a regional public-health data interface.", "Reporting and surveillance are not incidence, diagnosis, or enforcement.", "Completeness, timeliness, and privacy are unresolved.", "REG-PHASE13A-DISEASE"),
    ("TECH-DATA-GOVERNANCE", "SYS-ENERGY", "operating-information continuity", "operational dependency", "Phase 3B identifies generalized communications dependencies for energy operations.", "Information continuity is not energy flow or control authority.", "Redundancy and recovery are unresolved.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
]

DEPENDENCY_SPECS = {
    "TECH-AI-COMPUTE": [
        ("compute", "enabling", "compute capacity", "SYS-ENERGY", "Compute capacity is an enabling dependency, not a guaranteed bottleneck.", "Availability, allocation, and useful model performance are unresolved.", "REG-PHASE3A-ENERGY"),
        ("data", "enabling", "quality and provenance data", "SYS-DATA", "Useful intelligence requires data, provenance, and validation.", "Data availability does not ensure permission or representativeness.", "REG-PHASE4B-INFO-GOV"),
        ("communications", "limiting", "communications continuity", "SYS-DATA", "Decision support depends on communications and data exchange.", "No topology or failure probability is modeled.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
        ("skilled workforce", "limiting", "model stewardship and operator skill", "SYS-GOVERNANCE", "Human review, maintenance, and accountability are required.", "Workforce capacity is not measured.", "REG-PHASE10A-GOVERNANCE"),
    ],
    "TECH-SENS-ENVIRONMENTAL": [
        ("electricity", "enabling", "sensor power", "SYS-ENERGY", "Measurement platforms require energy and maintenance.", "No device-level load or redundancy is inferred.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
        ("communications", "enabling", "data transmission", "SYS-DATA", "Networked observation requires communications and data stewardship.", "No network topology is modeled.", "REG-PHASE4A-DATA"),
        ("data", "limiting", "calibration and interpretation data", "SYS-DATA", "Measurement is distinct from interpretation and decision.", "Coverage and quality are variable.", "REG-PHASE4B-INFO-GOV"),
        ("physical infrastructure", "limiting", "platform access and maintenance", "SYS-WATER", "Field observation depends on access and maintained assets.", "Facility-level condition is not represented.", "REG-PHASE4A-DATA"),
    ],
    "TECH-CYBER-RESILIENCE": [
        ("communications", "enabling", "trusted communications", "SYS-DATA", "Defensive resilience requires trusted communications and authentication.", "No offensive or exploit detail is modeled.", "REG-PHASE4B-INFO-GOV"),
        ("skilled workforce", "limiting", "security and recovery workforce", "SYS-GOVERNANCE", "Continuity and recovery depend on people and roles.", "Staffing and performance are unresolved.", "REG-PHASE10A-GOVERNANCE"),
        ("data", "enabling", "asset and dependency inventory", "SYS-DATA", "Defensive improvement needs accurate asset and dependency records.", "Inventory completeness is unknown.", "REG-PHASE14B-ATLAS"),
        ("public trust / legitimacy", "limiting", "trust in continuity and reporting", "SYS-POPULATION", "Incident communication and service continuity interact with public trust.", "No trust score or behavior model is created.", "REG-PHASE11A-POPULATION"),
    ],
    "TECH-ENERGY-ADVANCED-NUCLEAR": [
        ("materials", "enabling", "qualified reactor materials", "SYS-MATERIALS", "Advanced generation depends on qualified materials and supply chains.", "No regional material capability is invented.", "REG-PHASE2-MATERIALS"),
        ("water", "limiting", "cooling and water context", "SYS-WATER", "Water can be an engineering dependency; plant-specific conditions are not modeled.", "No withdrawal, permit, or intake claim is made.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
        ("regulatory authority", "limiting", "licensing and oversight", "SYS-GOVERNANCE", "Licensing and oversight are prerequisites for any deployment.", "Research or demonstration is not a license or approval.", "REG-PHASE10A-GOVERNANCE"),
        ("physical infrastructure", "limiting", "interconnection and site infrastructure", "SYS-ENERGY", "Generation would require site and grid interfaces.", "No facility, feeder, or interconnection is added.", "REG-PHASE3A-ENERGY"),
    ],
    "TECH-MATERIALS-ADVANCED": [
        ("materials", "enabling", "feedstock and qualified inputs", "SYS-MATERIALS", "Material innovation requires feedstock, qualification, and process control.", "Elmore feed remains nonlocal in the frozen baseline.", "REG-PHASE2-MATERIALS"),
        ("electricity", "limiting", "process energy", "SYS-ENERGY", "Industrial processes depend on energy services.", "No process load or outage claim is inferred.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
        ("skilled workforce", "limiting", "process and quality workforce", "SYS-FREIGHT", "Qualification and production require skilled work.", "No local workforce capability is quantified.", "REG-PHASE5A-FREIGHT"),
        ("supply chain", "limiting", "equipment and customer network", "SYS-FREIGHT", "Adoption depends on equipment, suppliers, and customers.", "No exact routes, volumes, or customers are inferred.", "REG-PHASE5C-FREIGHT"),
    ],
    "TECH-QUANTUM-SENSING": [
        ("compute", "enabling", "quantum control and analysis", "SYS-DATA", "Quantum sensing requires control, calibration, and analysis infrastructure.", "No field deployment is claimed.", "REG-PHASE4A-DATA"),
        ("materials", "limiting", "specialized components", "SYS-MATERIALS", "Specialized materials and fabrication enable devices.", "Regional manufacturing capability is unknown.", "REG-PHASE2-MATERIALS"),
        ("communications", "limiting", "timing and data transfer", "SYS-DATA", "Networked timing and data exchange are required.", "No communications architecture is modeled.", "REG-PHASE4B-INFO-GOV"),
        ("skilled workforce", "limiting", "measurement-science workforce", "SYS-GOVERNANCE", "Specialized operation and calibration require expertise.", "Workforce and institutional capacity are unresolved.", "REG-PHASE10A-GOVERNANCE"),
    ],
    "TECH-BIO-DIAGNOSTICS": [
        ("water", "enabling", "environmental sampling context", "SYS-WATER", "Environmental molecular monitoring can use water or wastewater context.", "A signal is not contamination, exposure, dose, or illness.", "REG-PHASE13A-DISEASE"),
        ("skilled workforce", "limiting", "laboratory and bioinformatics capacity", "SYS-INFECTIOUS-DISEASE", "Diagnostic interpretation requires laboratory and epidemiology capability.", "Capacity and turnaround are unresolved.", "REG-PHASE13A-DISEASE"),
        ("data", "enabling", "laboratory and surveillance data", "SYS-DATA", "Genomic results require provenance, privacy, and reporting systems.", "Data access is not permission or authority.", "REG-PHASE4B-INFO-GOV"),
        ("regulatory authority", "limiting", "quality and oversight", "SYS-GOVERNANCE", "Diagnostics and environmental monitoring require role-bounded oversight.", "Oversight is not proof of a threat or response success.", "REG-PHASE10A-GOVERNANCE"),
    ],
    "TECH-DATA-GOVERNANCE": [
        ("electricity", "enabling", "service continuity", "SYS-ENERGY", "Digital stewardship depends on maintained energy services.", "No load, outage, or feeder claim is inferred.", "REG-PHASE3B-ENERGY-DEPENDENCIES"),
        ("communications", "enabling", "trusted data exchange", "SYS-DATA", "Data governance requires authenticated exchange and continuity.", "No network topology is modeled.", "REG-PHASE4B-INFO-GOV"),
        ("data", "enabling", "provenance and stewardship records", "SYS-DATA", "Governance depends on metadata, provenance, and access records.", "Availability does not equal permission.", "REG-PHASE14B-ATLAS"),
        ("public trust / legitimacy", "limiting", "legitimacy of observation and use", "SYS-POPULATION", "Surveillance and data use interact with public trust.", "No privacy impact or trust score is created.", "REG-PHASE11A-POPULATION"),
    ],
}


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_sources() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    def external(source_id: str, title: str, url: str, scale: str, product: str, use: str, limitation: str) -> None:
        rows.append({
            "source_id": source_id, "title": title, "url": url, "source_type": "authoritative_government_or_institutional",
            "source_scope": "general_technology_capability", "publication_or_period": "current page accessed 2026-09-11",
            "retrieval_date": "2026-09-11", "geographic_scale": scale, "method_or_product": product,
            "evidence_use": use, "regional_deployment_supported": "no", "use_limitations": limitation,
            "retrieval_url": url, "retrieval_provenance": "URL verified by bounded web extraction or direct public retrieval; general capability/status only.",
        })

    external("EXT-NIST-AI-RMF", "AI Risk Management Framework | NIST", "https://www.nist.gov/itl/ai-risk-management-framework", "United States / general", "NIST AI RMF 1.0 and critical-infrastructure profile context", "AI trustworthiness, risk management, and human-governance boundary", "Voluntary framework; not evidence of local AI deployment, reliability, or authority.")
    external("EXT-DOE-AI-RECOMMENDATIONS", "Recommendations on Artificial Intelligence for the U.S. Department of Energy", "https://www.energy.gov/sites/default/files/2024-08/Artificial%20Intelligence%20at%20the%20U.S.%20Department%20of%20Energy%20Recommendations%20July%202024.pdf", "United States / DOE energy and research context", "July 2024 DOE advisory memorandum on AI, compute, data, storage, energy infrastructure, and guardrails", "AI/compute capability and energy-system decision-support interface", "National DOE strategy does not prove Western Basin AI deployment or adoption.")
    external("EXT-NIST-MANUFACTURING", "Manufacturing | NIST", "https://www.nist.gov/manufacturing", "United States / general", "NIST manufacturing, smart manufacturing, materials, additive, and resilience context", "Advanced materials, manufacturing innovation, biomanufacturing, and process-monitoring capability", "General national capability; no named Western Basin process or facility adoption.")
    external("EXT-NOAA-IOOS", "U.S. Integrated Ocean Observing System | NOAA", "https://ioos.noaa.gov", "United States / coasts / Great Lakes", "Integrated observing, data, and predictive-tool system context", "Environmental sensing and observation interfaces", "Great Lakes scope supports a technology class/interface, not exhaustive Toledo deployment.")
    external("EXT-NOAA-IOOS-GLIDERS", "Underwater Gliders | NOAA IOOS", "https://ioos.noaa.gov/project/underwater-gliders", "United States / coastal and Great Lakes observing context", "IOOS underwater-glider observing platforms, data assembly, and applications", "Autonomous/mobile environmental observing status and capability", "The page supports observing platforms, not a Western Basin glider deployment or infrastructure-inspection program.")
    external("EXT-CISA-CPG", "Cross-Sector Cybersecurity Performance Goals | CISA", "https://www.cisa.gov/cross-sector-cybersecurity-performance-goals", "United States / critical infrastructure", "Cross-sector defensive cybersecurity practices", "Defensive cybersecurity, continuity, authentication, and recovery boundary", "Voluntary goals do not prove implementation or service continuity.")
    external("EXT-NIST-PQC", "Post-Quantum Cryptography | NIST", "https://www.nist.gov/pqcrypto", "United States / global standards", "PQC standards and migration context", "Cryptographic transition and digital trust dependency", "Future quantum threat timing and local migration status are not inferred.")
    external("EXT-DOE-ARDP", "Advanced Reactor Demonstration Program | DOE", "https://www.energy.gov/ne/advanced-reactor-demonstration-program", "United States / demonstration program", "Advanced reactor demonstration and risk-reduction pathways", "Advanced nuclear maturity/status", "Demonstration support is not commercial availability or regional adoption.")
    external("EXT-DOE-ENERGY-STORAGE", "Energy Storage | DOE", "https://www.energy.gov/oe/energy-storage", "United States / grid-scale energy storage", "Energy Storage Division research, deployment, reliability, and long-duration storage context", "Long-duration and grid-scale storage maturity/status", "DOE storage programs do not establish a specific Western Basin project, duration, or adoption.")
    external("EXT-DOE-H2HUBS", "Regional Clean Hydrogen Hubs | DOE", "https://www.energy.gov/oced/regional-clean-hydrogen-hubs", "United States / regional program", "Hydrogen producers, consumers, and connective infrastructure program context", "Hydrogen energy-carrier status and system interfaces", "National program is not evidence of a Western Basin project, route, or facility.")
    external("EXT-DOE-FUSION", "Fusion Energy Sciences | DOE", "https://www.energy.gov/science/fes/fusion-energy-sciences", "United States / research program", "Fusion research and technology foundation context", "Fusion research-stage status", "Research trajectory is not current generation, firm power, or local deployment.")
    external("EXT-NIST-QIS", "Quantum information science | NIST", "https://www.nist.gov/quantum-information-science", "United States / research and standards", "Quantum computing, sensing, networks, and measurement context", "Quantum category/status and possible sensing/timing interfaces", "Laboratory capability is not operational deployment or economic transformation.")
    external("EXT-NIST-PRIVACY", "Privacy Framework | NIST", "https://www.nist.gov/privacy-framework", "United States / general organizations", "Voluntary privacy risk-management tool", "Privacy governance and responsible data-use boundary", "Framework is not legal advice, consent evidence, or a local surveillance inventory.")
    external("EXT-EPA-SMM", "Sustainable Materials Management Basics | EPA", "https://www.epa.gov/smm/sustainable-materials-management-basics", "United States / general materials lifecycle", "EPA sustainable materials management and life-cycle reuse context", "Circular/reuse materials-management capability and governance interface", "EPA approach does not prove a named Western Basin recycling facility, process, or rate.")
    external("EXT-NIST-CSF", "Cybersecurity Framework | NIST", "https://www.nist.gov/cyberframework", "United States / organizations", "NIST CSF 2.0", "Defensive cybersecurity governance context", "Framework does not demonstrate local implementation or operational maturity.")
    external("EXT-CDC-ONEHEALTH", "About One Health | CDC", "https://www.cdc.gov/one-health/about", "Local to global / human-animal-environment", "One Health collaboration and monitoring context", "High-level biosecurity, coordination, and shared-environment lens", "Conceptual health-system approach; not evidence of local transmission or threat.")
    external("EXT-CDC-AMD", "About CDC Advanced Molecular Detection | CDC", "https://www.cdc.gov/advanced-molecular-detection/php/about/index.html", "United States / state and local public health interfaces", "Genomic sequencing, high-performance computing, epidemiology, and diagnostics context", "Biological detection and diagnostic capability", "General public-health capacity; no local result, incidence, or harmful-biology procedure.")

    regional = [
        ("REG-PHASE2-MATERIALS", "Accepted Phase 2 materials baseline", "data/processed/networks/materials_system_nodes.csv", "Phase 2A–2C", "Regional materials and processing context", "Elmore remains processing with nonlocal feed; no capability is invented."),
        ("REG-PHASE3A-ENERGY", "Accepted Phase 3A energy/grid/compute baseline", "data/processed/networks/energy_system_nodes.csv", "Phase 3A", "Energy, grid, storage, loads, and planned/unverified compute context", "The planned compute project is not proof of AI deployment or operation."),
        ("REG-PHASE3B-ENERGY-DEPENDENCIES", "Accepted Phase 3B energy dependencies", "data/processed/networks/energy_dependency_edges.csv", "Phase 3B", "Cooling, communications, fuel, storage, and generalized energy dependencies", "No power-flow, outage, feeder, or facility-control model."),
        ("REG-PHASE4A-DATA", "Accepted Phase 4A observation baseline", "data/processed/networks/observation_system_nodes.csv", "Phase 4A", "Public observation-to-decision chains and sensor context", "Representative public information chains; not an exhaustive advanced-sensor inventory."),
        ("REG-PHASE4B-INFO-GOV", "Accepted Phase 4B information governance baseline", "data/processed/networks/information_dependency_edges.csv", "Phase 4B", "Information dependencies, blind spots, and authority distinctions", "Observation is not authority; no cyber topology or privacy-impact model."),
        ("REG-PHASE5A-FREIGHT", "Accepted Phase 5A freight/industry baseline", "data/processed/networks/freight_system_nodes.csv", "Phase 5A", "Industrial, freight, gateway, and generalized market interfaces", "No exact route, quantity, facility adoption, or hazardous-material detail."),
        ("REG-PHASE5C-FREIGHT", "Accepted Phase 5C freight dependencies", "data/processed/networks/freight_dependency_edges.csv", "Phase 5C", "Freight continuity and gateway dependency context", "Qualitative dependency only; no route-level disruption probability."),
        ("REG-PHASE6A-ECOLOGY", "Accepted Phase 6A ecology baseline", "data/processed/networks/ecology_system_nodes.csv", "Phase 6A", "Ecological components and habitat-function context", "No sensitive locations, abundance, or future ecology is added."),
        ("REG-PHASE7A-EXPOSURE", "Accepted Phase 7A exposure baseline", "data/processed/networks/exposure_context_nodes.csv", "Phase 7A", "Environmental-health pathways and monitoring context", "No documented individual exposure, dose, illness, or risk score."),
        ("REG-PHASE8A-BGC", "Accepted Phase 8A biogeochemical baseline", "data/processed/networks/biogeochemical_system_nodes.csv", "Phase 8A", "Nutrient, runoff, wastewater, wetland, and monitoring context", "No load forecast, bloom magnitude, or control-effect estimate."),
        ("REG-PHASE9A-CLIMATE", "Accepted Phase 9A climate and hazards baseline", "data/processed/networks/climate_hazard_nodes.csv", "Phase 9A", "Climate and natural-hazard observations/context", "No deterministic hazard surface, probability, or impact forecast."),
        ("REG-PHASE10A-GOVERNANCE", "Accepted Phase 10A governance baseline", "data/processed/analysis/governance_actors.csv", "Phase 10A", "Actors, roles, authority, ownership, regulation, and coordination", "Role distinctions are preserved; no performance or authority collapse."),
        ("REG-PHASE11A-POPULATION", "Accepted Phase 11A population baseline", "data/processed/analysis/population_settlement_nodes.csv", "Phase 11A", "Aggregate population, settlement, housing, and employment context", "No individual profile, vulnerability ranking, or utility territory."),
        ("REG-PHASE12A-VECTOR", "Accepted Phase 12A vector ecology baseline", "data/processed/networks/vector_ecology_nodes.csv", "Phase 12A", "Vector ecology and surveillance context", "Detection is not establishment, infection, or disease burden."),
        ("REG-PHASE13A-DISEASE", "Accepted Phase 13A infectious-disease baseline", "data/processed/networks/infectious_disease_nodes.csv", "Phase 13A", "Disease-system surveillance, diagnosis, and response context", "No incidence forecast, outbreak model, individual case map, or local transmission claim."),
        ("REG-PHASE14B-ATLAS", "Accepted Phase 14B Atlas integration", "metadata/atlas_layers.yml", "Phase 14B", "Frozen ontology, relationship, dependency, identity, and joinability contract", "Additive Atlas interface; does not rewrite Phase 1–14 artifacts."),
    ]
    for source_id, title, artifact, period, use, limitation in regional:
        rows.append({
            "source_id": source_id, "title": title, "url": f"repo://{artifact}", "source_type": "accepted_phase_artifact",
            "source_scope": "regional_system_context", "publication_or_period": period, "retrieval_date": "2026-09-11",
            "geographic_scale": "Western Basin system scale", "method_or_product": artifact, "evidence_use": use,
            "regional_deployment_supported": "no", "use_limitations": limitation, "retrieval_url": f"repo://{artifact}",
            "retrieval_provenance": "Protected repository artifact at the synchronized Phase 15A base; reused as regional system context, not technology-deployment evidence.",
        })
    return rows


def render_figure(interfaces: list[dict[str, object]]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    short_systems = {
        "SYS-WATER": "Water", "SYS-MATERIALS": "Materials", "SYS-ENERGY": "Energy", "SYS-DATA": "Data",
        "SYS-FREIGHT": "Freight", "SYS-ECOLOGY": "Ecology", "SYS-EXPOSURE": "Exposure", "SYS-BIOGEOCHEMISTRY": "Nutrients",
        "SYS-CLIMATE": "Climate", "SYS-GOVERNANCE": "Governance", "SYS-POPULATION": "Population", "SYS-VECTOR-ECOLOGY": "Vector",
        "SYS-INFECTIOUS-DISEASE": "Disease",
    }
    family_short = ["AI / compute / automation", "Sensing / autonomous", "Cyber / digital resilience", "Advanced energy", "Materials / manufacturing", "Quantum", "Biotech / genetic", "Privacy / surveillance / data"]
    family_index = {family: i for i, family in enumerate(FAMILIES)}
    target_index = {system: i for i, system in enumerate(SYSTEM_IDS)}
    cell: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in interfaces:
        cell[(family_index[row["technology_family"]], target_index[row["target_system_id"]])].append(row)

    fig, ax = plt.subplots(figsize=(18, 9.4), facecolor="#f6f3eb")
    ax.set_facecolor("#f6f3eb")
    colors = {"current": "#247a5b", "emerging": "#d58a24", "speculative": "#7956a8"}
    for (r, c), rows in cell.items():
        relevance = rows[0]["regional_relevance"]
        x, y = c, len(FAMILIES) - 1 - r
        ax.add_patch(FancyBboxPatch((x - .44, y - .32), .88, .64, boxstyle="round,pad=.025,rounding_size=.05", facecolor=colors[relevance], edgecolor="#20323c", linewidth=.8, alpha=.95))
        marker = "G" if any(row["target_system_id"] in {"SYS-DATA", "SYS-GOVERNANCE"} or row["normalized_relationship_class"] == "governance / authority" for row in rows) else "●"
        ax.text(x, y + .02, marker, ha="center", va="center", color="white", fontsize=12, weight="bold")
        if len(rows) > 1:
            ax.text(x, y - .20, str(len(rows)), ha="center", va="center", color="white", fontsize=7)
    for x in range(len(SYSTEM_IDS)):
        ax.axvline(x - .5, color="#d5d0c5", linewidth=.55, zorder=0)
    for y in range(len(FAMILIES)):
        ax.axhline(y - .5, color="#d5d0c5", linewidth=.55, zorder=0)
    ax.set_xlim(-.5, len(SYSTEM_IDS) - .5)
    ax.set_ylim(-1.7, len(FAMILIES) - .05)
    ax.set_xticks(range(len(SYSTEM_IDS)))
    ax.set_xticklabels([short_systems[x] for x in SYSTEM_IDS], rotation=38, ha="right", fontsize=9, color="#20323c")
    ax.set_yticks(range(len(FAMILIES)))
    ax.set_yticklabels(list(reversed(family_short)), fontsize=10, color="#20323c")
    ax.tick_params(length=0)
    ax.set_title("Technology–System Convergence Architecture, 2026", loc="left", fontsize=18, weight="bold", color="#17384b", pad=20)
    ax.text(-.48, 7.72, "Conceptual matrix/network hybrid: technology families → existing Western Basin systems", fontsize=10.5, color="#3f4645", va="bottom")
    ax.text(-.48, -1.21, "Cell color shows current / emerging / speculative regional interface relevance. G marks governance/data dependency.\nConceptual system-level figure; not a geographic map. Cell presence is not deployment, causation, risk, quantity, or authority.", fontsize=9.5, color="#3f4645", va="top", linespacing=1.25)
    legend = [
        Rectangle((0, 0), 1, 1, facecolor=colors["current"], label="Established/current interface"),
        Rectangle((0, 0), 1, 1, facecolor=colors["emerging"], label="Emerging interface"),
        Rectangle((0, 0), 1, 1, facecolor=colors["speculative"], label="Speculative/long-horizon interface"),
        Rectangle((0, 0), 1, 1, facecolor="#ffffff", edgecolor="#20323c", label="G = governance/data dependency"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0, -0.26), ncol=4, frameon=False, fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=.20, right=.98, top=.87, bottom=.25)
    png = FIGURES / "technology_system_convergence_architecture_2026.png"
    svg = FIGURES / "technology_system_convergence_architecture_2026.svg"
    fig.savefig(png, dpi=220, facecolor=fig.get_facecolor())
    fig.savefig(svg, facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def write_reports(nodes: list[dict[str, object]], observations: list[dict[str, object]], interfaces: list[dict[str, object]], dependencies: list[dict[str, object]], uncertainties: list[dict[str, object]]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    BRIEFS.mkdir(parents=True, exist_ok=True)
    counts = Counter(row["current_or_emerging"] for row in nodes)
    status = Counter(row["technology_status"] for row in nodes)
    iface = Counter(row["regional_relevance"] for row in interfaces)
    family_lines = []
    for family in FAMILIES:
        fam = [row for row in nodes if row["technology_family"] == family]
        family_lines.append(f"| {family} | {len(fam)} | " + ", ".join(f"{row['technology_label']} — {row['technology_status']} / {row['regional_relevance']}" for row in fam) + " |")

    (BRIEFS / "phase15_technology_strategic_systems_convergence.md").write_text("""# Phase 15 — Technology and Strategic-Systems Convergence

Status: APPROVED SCOPE; Phase 15A is the only implemented work package.

Phase 15 treats technology as a capability layer over the accepted/frozen Western Basin systems. It asks what a technology could interface with, what dependencies it introduces, and what capability change is plausible without assuming adoption, success, societal benefit, or resilience.

## Subphases

- Phase 15A — Technology & Strategic-Systems Baseline and Interfaces, 2026: IMPLEMENTED in this work package.
- Phase 15B — Technology Convergence Futures, 2050 / 2075: APPROVED SCOPE / NOT IMPLEMENTED.

The package is additive. It does not modify Phase 14 registries, local IDs, or accepted/frozen Phase 1–14 artifacts. Technology capability is not deployment; deployment is not adoption; adoption is not benefit; and technology is not resilience.

Phase 15B remains a future qualitative scenario package. No Phase 15B scenario records, maps, forecasts, or future technology states are created here. Phase 16 is not implemented.
""", encoding="utf-8")
    (BRIEFS / "phase15a_technology_strategic_systems_baseline_2026.md").write_text("""# Phase 15A — Technology & Strategic-Systems Baseline and Interfaces, 2026

Status: IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE.

## Purpose

Create a bounded, source-backed technology capability layer that interfaces with the frozen Phase 14 ontology and the accepted/frozen Western Basin systems. The package records technology family, maturity/status, current/emerging/speculative relevance, enabling and limiting dependencies, governance boundaries, provenance, and uncertainty.

## Included families

AI / advanced compute / automation; advanced sensing / autonomous systems; cybersecurity / digital resilience; advanced energy; advanced materials / manufacturing; quantum technologies; biotechnology / genetic engineering; and privacy / surveillance / data governance.

## Exclusions

No Phase 15B future layer; no Phase 16 stress test; no technology-specific adoption forecast; no regional deployment inferred from national capability; no offensive cyber material; no harmful-biology operational detail; no AI authority; no sensing-as-enforcement; no quantum/fusion hype; no composite score; no new system registry; and no modification of frozen Phase 1–14 artifacts.

## Required distinctions

Decision support is not autonomous authority. Measurement is not interpretation, decision, or enforcement. Research trajectory is not commercial availability. Demonstration is not regional adoption. Generation capacity is not firm dependable power. Observation is not permission or legal authority. Biosecurity is a bounded system lens covering detection, attribution uncertainty, laboratory/diagnostic capacity, monitoring, supply-chain and agricultural resilience, dual-use governance, coordination, communication, and response capacity.
""", encoding="utf-8")
    (BRIEFS / "phase15b_technology_convergence_futures.md").write_text("""# Phase 15B — Technology Convergence Futures, 2050 / 2075

Status: APPROVED SCOPE / NOT IMPLEMENTED.

The approved future package may later crosswalk technology capabilities against 2050 and 2075 system conditions using separate qualitative scenario records. It must preserve technology status, dependency, adoption uncertainty, governance, privacy, biosecurity, and existing-system boundaries. It must not relabel national trajectories as local deployment, convert scenarios into forecasts, or modify the Phase 15A baseline.

No Phase 15B tables, figures, scenario states, assumptions, future dependencies, or forecasts are implemented by Phase 15A. Phase 16 is not implemented.
""", encoding="utf-8")

    (REPORTS / "phase15a_technology_systems_baseline.md").write_text(f"""# Phase 15A Technology Systems Baseline — 2026

## Status and scope

This is a factual/current technology capability and interface baseline, not a technology adoption forecast. NIST describes AI RMF as a voluntary framework for incorporating trustworthiness into AI design and use; it does not establish reliable deployment or authority.[1] DOE's 2024 AI recommendations describe data, storage, compute, energy infrastructure, and guardrails as part of an AI capability context.[15] NIST's manufacturing program connects measurement, smart manufacturing, additive manufacturing, biomanufacturing, and supply-chain resilience at national scale, but that capability is not local facility evidence.[12]

The repository contributes the regional system context. Phase 3 supplies energy/grid/compute interfaces; Phase 4 supplies observation and information governance; Phase 5 supplies freight/industry; Phase 6–8 supply ecology, exposure, and nutrients; Phase 10–13 supply governance, population, vectors, and infectious disease; and Phase 14 supplies the additive ontology and dependency contract. These are existing-system inputs, not evidence that every listed technology is deployed locally.

## Counts

- Technology families: {len(FAMILIES)}.
- Technology records: {len(nodes)}.
- Technology status: {dict(status)}.
- Technology records by current_or_emerging: current {counts['current']}, emerging {counts['emerging']}, speculative {counts['speculative']}.
- Technology-node regional relevance: current {sum(row['regional_relevance'] == 'current' for row in nodes)}, emerging {sum(row['regional_relevance'] == 'emerging' for row in nodes)}, speculative {sum(row['regional_relevance'] == 'speculative' for row in nodes)}.
- Observations: {len(observations)}; system interfaces: {len(interfaces)}; dependencies: {len(dependencies)}; uncertainties: {len(uncertainties)}.

## Technology families

| Family | Records | Representative status and relevance |
|---|---:|---|
""" + "\n".join(family_lines) + """

## Regional relevance findings

The strongest current interfaces are established environmental observation, defensive digital resilience, and privacy/data governance over existing public-information, energy, water, ecological, population, and institutional systems. NOAA's IOOS describes integrated observation and predictive tools for the Great Lakes, which supports an observation interface but not an exhaustive Toledo technology inventory.[9] Its underwater-glider page documents robotic/mobile observing platforms and applications, but not a Western Basin glider deployment.[16] CISA's cross-sector goals support a defensive continuity lens across critical infrastructure, not proof of local implementation.[2]

Emerging interfaces include AI/compute decision support, autonomous inspection, storage, distributed energy, advanced manufacturing, post-quantum migration, and genomic diagnostics. The frozen Phase 3A baseline contains one documented 5 MW compute project with operating status unverified; this is regional compute context, not evidence of AI deployment. Phase 2 and Phase 5 provide materials and industry context without inventing regional advanced manufacturing capability.

DOE describes advanced reactors through demonstration pathways, while its fusion program is a research program addressing foundational science and technology gaps.[3][4] DOE's hydrogen-hub page describes a national program connecting producers, consumers, and infrastructure; it does not establish a basin project.[13] NIST describes quantum sensing, networks, and computing as research and measurement directions; no operational regional deployment is asserted.[5]

DOE's Energy Storage Division describes research and efforts to deploy grid-scale and long-duration storage, but this does not establish a Western Basin project, duration, or adoption.[14]

EPA describes sustainable materials management as using and reusing materials across their life cycles; this supports a circular-materials interface, not a local facility or recovery rate.[17]

## Boundaries

Technology capability ≠ reliable deployment ≠ adoption ≠ benefit. A dependency is not a guaranteed bottleneck. The package contains no capacity, probability, risk, performance, or resilience score. It does not alter accepted/frozen Phase 1–14 artifacts.
""", encoding="utf-8")

    (REPORTS / "phase15a_technology_interfaces.md").write_text(f"""# Phase 15A Technology–System Interfaces — 2026

## Interface contract

Each interface identifies a technology record and an existing Phase 14 system target. `source_system_id` is intentionally blank: technology is an additive capability layer, not a new Phase 14 ontology member. Every nonblank `target_system_id` resolves to a frozen Phase 14 Atlas system. Interface classes reuse the Phase 14 relationship vocabulary: physical/material/energy flow, information/observation, governance/authority, operational dependency, ecological relationship, exposure pathway, surveillance/detection, population/mobility, high-level association, and scenario influence. Phase 15A contains no scenario influence rows.

The package contains {len(interfaces)} additive interfaces. Their regional relevance counts are current {iface['current']}, emerging {iface['emerging']}, and speculative {iface['speculative']}. Regional relevance is a defensible interface to an existing system, not a claim of local technology deployment.

## Capability-to-interface rules

- AI recommendation and optimization remain decision support. They do not become autonomous legal authority, operational control, or enforcement.[1][15]
- Sensing rows stop at measurement/detection. NOAA's glider materials support autonomous/mobile observing platforms, not interpretation, decision, enforcement, exposure, dose, incidence, or disease.[16]
- Cybersecurity rows are defensive: authentication, trust, continuity, data integrity, communications, and recovery. CISA's goals are a voluntary baseline for critical-infrastructure protection, not an offensive technique catalogue.[2]
- Energy rows preserve the Phase 3 distinction between energy flow, operational dependency, material/fuel input, and information/control. Advanced nuclear, hydrogen, storage, and fusion are not treated as dependable regional generation.[3][4][13]
- DOE's energy-storage program provides general status context for long-duration storage; it does not prove regional deployment or firm dependable power.[14]
- Quantum rows are research-stage or speculative. NIST identifies quantum sensors, networks, and computers as areas of development; laboratory capability is not operational deployment.[5]
- Biotechnology rows remain high-level and safe. CDC's AMD program connects genomic sequencing, high-performance computing, and epidemiology to public-health response; this supports a detection/diagnostic interface, not a local incidence or threat claim.[11]
- Privacy/data rows preserve observation ≠ authority, data availability ≠ permission, and technical capability ≠ legal authority. NIST's Privacy Framework is voluntary and intended for privacy-risk management, not a local legal finding.[6]
- Circular-materials rows use EPA's life-cycle reuse framework as general capability context; no local recovery facility or process is asserted.[17]

## Existing systems affected

The matrix connects technology families to Water, Materials, Energy, Data, Freight, Ecology, Exposure, Nutrients, Climate, Governance, Population, Vector Ecology, and Infectious Disease only where the repository has a defensible contextual interface. The figure is conceptual and non-geographic. Cell presence does not represent deployment in Toledo/NW Ohio, measured flow, causation, risk, or benefit.
""", encoding="utf-8")

    (REPORTS / "phase15a_biosecurity_lens.md").write_text("""# Phase 15A Bounded Biosecurity Lens — 2026

## Scope

Biosecurity is a bounded system lens within biotechnology, public health, agriculture, sensing, and governance interfaces. It is not a standalone domain phase, threat assessment, or operational security package. CDC's One Health framing connects people, animals, plants, and shared environments and emphasizes multisector coordination.[10] CDC's Advanced Molecular Detection program describes genomic sequencing, high-performance computing, and epidemiology as public-health capabilities; this supports a high-level detection and response interface.[11]

## Findings

1. Detection: molecular diagnostics, environmental monitoring, vector surveillance, wastewater context, and reporting can improve the opportunity to detect a condition. Detection is not incidence, attribution, transmission, or disease burden.
2. Attribution uncertainty: a signal may require sampling, laboratory confirmation, source attribution, and interpretation. A signal is not by itself a cause, threat, outbreak, or local transmission finding.
3. Laboratory/diagnostic capacity: workforce, quality systems, turnaround, interoperability, and data stewardship enable interpretation. National or state capability does not establish a local result.
4. Biological monitoring: ecology, water, exposure, vector, and infectious-disease systems provide existing context. Monitoring is not absence, control, enforcement, or proof of safety.
5. Supply-chain resilience: food, freight, materials, energy, water, and laboratory inputs can affect continuity. Connectivity is not an outbreak claim or a facility-specific vulnerability.
6. Food/agricultural resilience: existing nutrient, ecology, freight, population, and disease interfaces support a high-level One Health connection. No production loss, contamination event, disease burden, or agricultural-risk score is modeled.
7. Dual-use governance: oversight, privacy, quality, reporting, communication, and role clarity are governance interfaces. A dual-use concern is not evidence of an actual threat.
8. Coordination and public communication: detection value depends on bounded roles, data interpretation, public explanation, and response capacity. Coordination is not automatic authority or successful intervention.

## Safety boundary

This lens includes no pathogen engineering methods, harmful-agent enhancement, weaponization, evasion, attack design, wet-lab protocol, or operational misuse procedure. It makes no claim about a current regional biological threat.
""", encoding="utf-8")

    (REPORTS / "phase15a_technology_qa.md").write_text(f"""# Phase 15A Technology QA

## Package checks

The reproducible builder writes {len(nodes)} technology records across {len(FAMILIES)} families, {len(observations)} observations, {len(interfaces)} technology-system interfaces, {len(dependencies)} dependency records, {len(uncertainties)} uncertainty records, {len(make_sources())} source records, and one conceptual PNG/SVG figure. The machine result is `reports/phase15a_artifact_check.json`; Python and independent base-R validators are required before acceptance.

## Required semantic checks

- technology IDs, families, maturity values, current/emerging/speculative labels, source IDs, and system IDs resolve;
- target systems resolve to the frozen Phase 14 ontology without adding a technology system to `metadata/atlas_systems.yml`;
- relationship and evidence classes reuse the Phase 14 vocabularies;
- regional deployment claims are absent unless directly supported; general capability is not relabeled local;
- AI rows preserve decision support ≠ autonomous authority;
- sensing rows preserve observation ≠ interpretation ≠ decision ≠ enforcement;
- cybersecurity remains defensive and resilience-oriented;
- quantum remains research-stage/speculative and fusion remains non-current;
- biotechnology remains high-level and the biosecurity lens contains no operational harmful-biology detail;
- prior freeze manifests and active holds remain intact;
- Phase 15B/16 data, scenario, and map artifacts are absent.

## Figure QA

`outputs/figures/technology_system_convergence_architecture_2026.png` and `.svg` are a conceptual matrix/network hybrid, not a geographic map. The SVG retains text labels for established/current, emerging, speculative/long-horizon, governance/data dependency, and the non-deployment caveat. Matrix cell color is categorical interface relevance, not probability, risk, quantity, or effect size.

## Provenance

External capability claims use the grounded-citation ledger and numbered citations in the reports. Repository source IDs point to accepted/frozen system artifacts used as regional context. The Phase 15A interface is generally an explicit project inference over those inputs; it does not promote the input artifacts into technology-deployment evidence.
""", encoding="utf-8")

    (REPORTS / "phase15a_provenance_check.md").write_text("""# Phase 15A Grounded Provenance Check

This short ledger-facing report records the external capability/status claims used by Phase 15A. It does not support local deployment claims.

- NIST describes the AI Risk Management Framework as a voluntary tool for trustworthiness in AI design, development, use, and evaluation.[1]
- CISA describes Cross-Sector Cybersecurity Performance Goals as a common protective baseline for critical infrastructure.[2]
- DOE describes advanced reactors through demonstration and risk-reduction pathways, not as an adopted regional generation asset.[3]
- DOE describes fusion through a research program addressing the scientific and technological foundation for a future energy source.[4]
- NIST identifies quantum computing, quantum sensors, and quantum networks as developing quantum-information areas.[5]
- NIST describes the Privacy Framework as a voluntary tool for managing privacy risk while protecting individuals.[6]
- NIST presents CSF 2.0 as a framework for organizations to reduce cybersecurity risks.[7]
- NIST's PQC project describes quantum-resistant cryptographic standards and migration in response to a future quantum-computing threat.[8]
- NOAA IOOS describes integrated observing data and predictive tools for oceans, coasts, and the Great Lakes.[9]
- CDC's One Health approach recognizes connections among people, animals, plants, and shared environments and requires multisector collaboration.[10]
- CDC's Advanced Molecular Detection program connects genomic sequencing, high-performance computing, and epidemiology to public-health response.[11]
- NIST describes manufacturing measurement, smart manufacturing, additive manufacturing, biomanufacturing, and production resilience at national scale.[12]
- DOE describes Regional Clean Hydrogen Hubs as a national network of producers, consumers, and connective infrastructure.[13]
- DOE describes energy-storage research and deployment efforts for grid-scale and long-duration storage.[14]
- DOE's 2024 AI memorandum describes AI capability in relation to data, storage, compute, energy infrastructure, and guardrails.[15]
- NOAA IOOS describes underwater gliders as robotic observing platforms for subsurface missions.[16]
- EPA describes sustainable materials management as using and reusing materials across material life cycles.[17]

Each statement is used only for general technology capability/status. Regional interface claims are separately based on accepted/frozen repository artifacts and are labeled as inference or reused context; no external source is treated as proof of Western Basin deployment.
""", encoding="utf-8")

    # Render the ledger-owned Sources blocks after all cited reports exist.
    citation_script = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
    for report in (REPORTS / "phase15a_technology_systems_baseline.md", REPORTS / "phase15a_technology_interfaces.md", REPORTS / "phase15a_biosecurity_lens.md", REPORTS / "phase15a_technology_qa.md", REPORTS / "phase15a_provenance_check.md"):
        if citation_script.exists():
            subprocess.run([sys.executable, str(citation_script), "render", "--replace-in", str(report)], check=False, capture_output=True, text=True)


def main() -> int:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    INTEGRATION.mkdir(parents=True, exist_ok=True)
    METADATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    sources = make_sources()
    source_ids = {row["source_id"] for row in sources}
    write_csv(ANALYSIS / "technology_sources.csv", SOURCE_FIELDS, sources)
    write_csv(ANALYSIS / "technology_system_nodes.csv", NODE_FIELDS, TECHNOLOGIES)

    observations: list[dict[str, object]] = []
    for index, node in enumerate(TECHNOLOGIES, start=1):
        observations.append({
            "observation_id": f"TOB-{index:03d}", "technology_id": node["technology_id"], "technology_family": node["technology_family"],
            "observation_type": "technology_status", "observation_label": node["technology_label"], "observation_status": node["technology_status"],
            "evidence_class": node["evidence_class"], "claim_scope": "general_capability", "geographic_scope": "national_or_general",
            "temporal_basis": "2026 current status context", "regional_relevance": node["regional_relevance"], "source_id": node["source_id"],
            "regional_evidence_source_id": node["regional_evidence_source_id"], "uncertainty": node["uncertainty"],
            "notes": "General capability/status record; it is not evidence of regional deployment or adoption.",
        })
    observations.extend([
        {"observation_id": "TOB-REG-001", "technology_id": "TECH-AI-COMPUTE", "technology_family": FAMILIES[0], "observation_type": "regional_system_context", "observation_label": "Phase 3A documented 5 MW compute project", "observation_status": "planned / operating status unverified", "evidence_class": "OBSERVED_DOCUMENTED", "claim_scope": "regional_system_context", "geographic_scope": "Western Basin / Phase 3A project context", "temporal_basis": "2026 baseline", "regional_relevance": "emerging", "source_id": "REG-PHASE3A-ENERGY", "regional_evidence_source_id": "REG-PHASE3A-ENERGY", "uncertainty": "Operating status and AI use are unverified.", "notes": "Regional compute context only; does not establish AI deployment, useful intelligence, or local adoption."},
        {"observation_id": "TOB-REG-002", "technology_id": "TECH-SENS-ENVIRONMENTAL", "technology_family": FAMILIES[1], "observation_type": "regional_system_context", "observation_label": "Representative Phase 4A observation-to-decision chains", "observation_status": "accepted/frozen context", "evidence_class": "CONTEXT_REUSED", "claim_scope": "regional_system_context", "geographic_scope": "Western Basin public-information interfaces", "temporal_basis": "2026 baseline", "regional_relevance": "current", "source_id": "REG-PHASE4A-DATA", "regional_evidence_source_id": "REG-PHASE4A-DATA", "uncertainty": "Coverage, timing, and interpretation vary.", "notes": "Existing observation context supports a sensing interface; it is not a deployment claim, exhaustive advanced-sensor inventory, or enforcement system."},
        {"observation_id": "TOB-REG-003", "technology_id": "TECH-MATERIALS-ADVANCED", "technology_family": FAMILIES[4], "observation_type": "regional_system_context", "observation_label": "Phase 2 materials and Phase 5 industry/freight context", "observation_status": "accepted/frozen context", "evidence_class": "CONTEXT_REUSED", "claim_scope": "regional_system_context", "geographic_scope": "Western Basin materials and freight interfaces", "temporal_basis": "2026 baseline", "regional_relevance": "emerging", "source_id": "REG-PHASE2-MATERIALS", "regional_evidence_source_id": "REG-PHASE5A-FREIGHT", "uncertainty": "Advanced process adoption, equipment, and customer links are unresolved.", "notes": "Existing material/industry systems support an interface only; it is not a local capability or deployment claim."},
    ])
    write_csv(ANALYSIS / "technology_system_observations.csv", OBS_FIELDS, observations)

    node_by_id = {node["technology_id"]: node for node in TECHNOLOGIES}
    interfaces: list[dict[str, object]] = []
    for index, (technology_id, target, interface_type, relationship, basis, governance, uncertainty, source_id) in enumerate(INTERFACE_SPECS, start=1):
        node = node_by_id[technology_id]
        interfaces.append({
            "interface_id": f"TSI-{index:03d}", "technology_id": technology_id, "technology_family": node["technology_family"],
            "technology_label": node["technology_label"], "technology_status": node["technology_status"], "source_system_id": "",
            "target_system_id": target, "interface_type": interface_type, "normalized_relationship_class": relationship,
            "evidence_class": "INFERRED", "current_or_emerging": node["current_or_emerging"], "regional_relevance": node["regional_relevance"],
            "dependency_basis": basis, "governance_interface": governance, "uncertainty": uncertainty, "source_id": source_id,
            "notes": "Additive project inference over accepted/frozen regional system context; not a deployment, causal, risk, or quantity claim.",
        })
    write_csv(INTEGRATION / "technology_system_interfaces.csv", INTERFACE_FIELDS, interfaces)

    dependencies: list[dict[str, object]] = []
    dep_index = 1
    for technology_id, specs in DEPENDENCY_SPECS.items():
        node = node_by_id[technology_id]
        for dep_class, role, label, affected, basis, limitation, source_id in specs:
            dependencies.append({
                "dependency_id": f"TDEP-{dep_index:03d}", "technology_id": technology_id, "technology_family": node["technology_family"],
                "dependency_class": dep_class, "dependency_role": role, "dependency_label": label, "affected_system_id": affected,
                "technology_status": node["technology_status"], "evidence_class": "INFERRED", "regional_relevance": node["regional_relevance"],
                "dependency_basis": basis, "limitation": limitation, "governance_interface": node["governance_interface"],
                "uncertainty": node["uncertainty"], "source_id": source_id,
                "notes": "Dependency is not a guaranteed bottleneck, failure probability, risk, or benefit; capability and adoption remain separate.",
            })
            dep_index += 1
    write_csv(INTEGRATION / "technology_dependencies.csv", DEPENDENCY_FIELDS, dependencies)

    uncertainties: list[dict[str, object]] = []
    uncertainty_specs = [
        ("TECH-AI-COMPUTE", "SYS-DATA", "deployment_reliability", "Model performance, data quality, monitoring, and operator review may not transfer from demonstration to reliable regional use.", "REG-PHASE14B-ATLAS"),
        ("TECH-SENS-AUTONOMOUS", "SYS-WATER", "coverage_interpretation", "Measurement, interpretation, decision, and enforcement remain separate; field coverage and retrieval are unknown.", "REG-PHASE4A-DATA"),
        ("TECH-CYBER-RESILIENCE", "SYS-DATA", "continuity_recovery", "Authentication, redundancy, recovery, and cross-organization continuity are not measured here.", "REG-PHASE4B-INFO-GOV"),
        ("TECH-ENERGY-ADVANCED-NUCLEAR", "SYS-ENERGY", "commercial_availability", "Demonstration and research status do not establish commercial availability, firm power, or local siting.", "REG-PHASE3A-ENERGY"),
        ("TECH-MATERIALS-ADVANCED", "SYS-MATERIALS", "regional_capability", "Existing materials and industrial nodes do not document advanced-process adoption or regional feedstock substitution.", "REG-PHASE2-MATERIALS"),
        ("TECH-QUANTUM-COMPUTING", "SYS-ENERGY", "useful_advantage", "Research-stage quantum computing does not establish useful regional optimization or economic transformation.", "REG-PHASE3A-ENERGY"),
        ("TECH-BIO-DIAGNOSTICS", "SYS-INFECTIOUS-DISEASE", "attribution_capacity", "Detection requires sampling, laboratory capacity, attribution, interpretation, communication, and response; a signal is not a threat or outbreak.", "REG-PHASE13A-DISEASE"),
        ("TECH-DATA-GOVERNANCE", "SYS-GOVERNANCE", "legal_authority_trust", "Data availability and technical surveillance capability do not establish legal authority, permission, justified intervention, or legitimacy.", "REG-PHASE10A-GOVERNANCE"),
    ]
    for index, (technology_id, affected, kind, text, regional_source) in enumerate(uncertainty_specs, start=1):
        node = node_by_id[technology_id]
        uncertainties.append({
            "uncertainty_id": f"TUNC-{index:03d}", "technology_id": technology_id, "technology_family": node["technology_family"],
            "affected_system_id": affected, "uncertainty_type": kind, "uncertainty_status": "open", "uncertainty": text,
            "evidence_class": "INFERRED", "source_id": node["source_id"], "regional_evidence_source_id": regional_source,
            "notes": "Unknown is retained as unknown; no low-risk, absence, bottleneck, or forecast conclusion is drawn.",
        })
    write_csv(ANALYSIS / "technology_uncertainties.csv", UNCERTAINTY_FIELDS, uncertainties)

    METADATA.joinpath("technology_vocabulary.yml").write_text("""version: '0.1'
registry_id: phase15a_technology_vocabulary
status: additive_phase15a_baseline
purpose: >-
  Bound technology families, maturity, interfaces, dependencies, evidence, and
  governance without modifying the frozen Phase 14 ontology or Phase 1-14 artifacts.
technology_families:
  - AI / ADVANCED COMPUTE / AUTOMATION
  - ADVANCED SENSING / AUTONOMOUS SYSTEMS
  - CYBERSECURITY / DIGITAL RESILIENCE
  - ADVANCED ENERGY
  - ADVANCED MATERIALS / MANUFACTURING
  - QUANTUM TECHNOLOGIES
  - BIOTECHNOLOGY / GENETIC ENGINEERING
  - PRIVACY / SURVEILLANCE / DATA GOVERNANCE
technology_status:
  - established
  - commercially emerging
  - demonstration / pilot
  - research-stage
  - speculative / long-horizon
regional_relevance:
  - current
  - emerging
  - speculative
relationship_classes_reused_from_phase14:
  - physical flow
  - material flow
  - energy flow
  - information / observation
  - governance / authority
  - operational dependency
  - ecological relationship
  - exposure pathway
  - population / mobility interface
  - surveillance / detection
  - high-level association
  - unresolved / unclassified
phase15a_evidence_classes:
  - OBSERVED_DOCUMENTED
  - DERIVED_CALCULATED
  - INFERRED
  - CONTEXT_REUSED
  - UNRESOLVED
  - NONCANONICAL_HOLD
phase15a_exclusions:
  - Phase 15B futures, forecasts, and scenario states
  - Phase 16 integrated stress tests
  - offensive cyber techniques, exploitation, attack procedures, or sensitive control topology
  - pathogen engineering, harmful-agent enhancement, evasion, weaponization, or wet-lab protocols
  - composite risk, resilience, vulnerability, connectivity, or performance scores
  - local deployment inferred from national capability or research trajectory
boundary_rules:
  - decision support is not autonomous authority
  - capability is not reliable deployment
  - compute capacity is not useful intelligence
  - measurement is not interpretation, decision, or enforcement
  - research trajectory is not commercial availability
  - demonstration is not regional adoption
  - generation capacity is not firm dependable power
  - observation is not permission or legal authority
  - dependency is not a guaranteed bottleneck
  - technology is not resilience
  - biosecurity is a bounded high-level system lens, not a standalone threat or operations model
interface_contract:
  technology_source: technology_id
  phase14_target: target_system_id
  source_system_id: blank_by_design_technology_is_not_phase14_system
  target_system_ids: frozen_phase14_atlas_system_ids_only
  scenario_status: BASELINE_2026_ONLY
""", encoding="utf-8")

    render_figure(interfaces)
    write_reports(TECHNOLOGIES, observations, interfaces, dependencies, uncertainties)

    primary = [
        "data/processed/analysis/technology_system_nodes.csv",
        "data/processed/analysis/technology_system_observations.csv",
        "data/processed/analysis/technology_sources.csv",
        "data/processed/analysis/technology_uncertainties.csv",
        "data/processed/integration/technology_system_interfaces.csv",
        "data/processed/integration/technology_dependencies.csv",
        "metadata/technology_vocabulary.yml",
        "outputs/figures/technology_system_convergence_architecture_2026.png",
        "outputs/figures/technology_system_convergence_architecture_2026.svg",
        "reports/phase15a_technology_systems_baseline.md",
        "reports/phase15a_technology_interfaces.md",
        "reports/phase15a_biosecurity_lens.md",
        "reports/phase15a_technology_qa.md",
        "reports/phase15a_provenance_check.md",
        "reports/phase15a_independent_review_initial.md",
        "reports/phase15a_independent_review_second_failed.md",
        "reports/phase15a_independent_review_third_failed.md",
        "docs/phase_briefs/phase15_technology_strategic_systems_convergence.md",
        "docs/phase_briefs/phase15a_technology_strategic_systems_baseline_2026.md",
        "docs/phase_briefs/phase15b_technology_convergence_futures.md",
        "src/python/systems/build_phase15a_technology.py",
    ]
    manifest = {
        "phase": "15A", "baseline": "Technology & Strategic-Systems Baseline and Interfaces, 2026",
        "status": "generated_working_package", "source_commit": "d8247cf3419be6e0caf0b345f63644f2795c2ac6",
        "counts": {"technology_families": len(FAMILIES), "technology_nodes": len(TECHNOLOGIES), "observations": len(observations), "interfaces": len(interfaces), "dependencies": len(dependencies), "uncertainties": len(uncertainties), "sources": len(sources), "current": sum(row["current_or_emerging"] == "current" for row in TECHNOLOGIES), "emerging": sum(row["current_or_emerging"] == "emerging" for row in TECHNOLOGIES), "speculative": sum(row["current_or_emerging"] == "speculative" for row in TECHNOLOGIES)},
        "artifacts": {rel: {"sha256": sha(ROOT / rel), "bytes": (ROOT / rel).stat().st_size, "role": "Phase 15A generated package artifact"} for rel in primary if (ROOT / rel).exists() and rel != "src/python/systems/build_phase15a_technology.py"},
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"},
        "phase15b_status": "APPROVED SCOPE / NOT IMPLEMENTED", "phase16_status": "NOT IMPLEMENTED", "release_created": False, "tag_created": False,
    }
    manifest["artifacts"]["src/python/systems/build_phase15a_technology.py"] = {"sha256": sha(ROOT / "src/python/systems/build_phase15a_technology.py"), "bytes": (ROOT / "src/python/systems/build_phase15a_technology.py").stat().st_size, "role": "reproducible Phase 15A builder"}
    (REPORTS / "phase15a_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "15A", "counts": manifest["counts"], "manifest": "reports/phase15a_manifest.json"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
