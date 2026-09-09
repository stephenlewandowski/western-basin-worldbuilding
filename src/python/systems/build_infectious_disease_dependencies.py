"""Build Phase 13B qualitative infectious-disease dependency products and Map 42.

This layer reuses the accepted Phase 13A disease/system baseline and accepted
cross-system context. It describes interfaces and dependencies, not incidence,
risk, outbreaks, disease burden, or deterministic causation.
"""
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

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"
RETRIEVAL_DATE = "2026-09-09"

BASELINE_SOURCES = ANALYSIS / "infectious_disease_sources.csv"
PHASE13A_FREEZE = REPORTS / "phase13a_infectious_disease_freeze_manifest.json"
MANIFEST = REPORTS / "infectious_disease_dependency_manifest.json"
LEDGER = REPORTS / "phase13b_citation_ledger.json"
MAP_BASE = MAPS / "42_infectious_disease_transmission_dependencies_2026"

BASE_SOURCE_IDS = [
    "s13_nndss_about", "s13_nndss_wonder", "s13_cdc_wnv", "s13_cdc_lyme",
    "s13_cdc_legionella_surv", "s13_cdc_legionella_about", "s13_cdc_water_surv",
    "s13_cdc_nors", "s13_cdc_enteric", "s13_cdc_foodnet", "s13_cdc_fluview",
    "s13_cdc_flu_methods", "s13_cdc_wastewater", "s13_cdc_rabies",
    "s13_cdc_nhsn", "s13_cdc_ar", "s13_ind_reportable", "s13_ohio_vector",
    "s13_mi_vector", "phase7_exposure", "phase9_climate", "phase11_population",
    "phase12_vector", "phase4_information", "phase10_governance",
]
EXTRA_SOURCES = [
    {
        "source_id": "phase1_water_context",
        "title": "Validated Phase 1 water-system and hydrography context",
        "url": "reports/water_system_manifest.json",
        "source_type": "repository_validated_layer",
        "publication_or_period": "validated current-development baseline",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "Western Basin / watershed, wetland, hydrography",
        "method_or_product": "validated water-system manifest and accepted context",
        "evidence_use": "hydrology, standing-water, wetland, source-water, and water-infrastructure interface context",
        "use_limitations": "Context is not a disease observation, exposure measurement, contamination result, or illness finding.",
        "retrieval_url": "reports/water_system_manifest.json",
        "retrieval_provenance": "repository manifest reference; validated in the Phase 13B package; not rebuilt or modified",
    },
    {
        "source_id": "phase3_energy_context",
        "title": "Accepted Phase 3B energy dependency and reliability context",
        "url": "reports/phase3b_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "regional grid, generalized energy dependencies",
        "method_or_product": "accepted energy dependency and reliability artifacts",
        "evidence_use": "generalized infrastructure continuity interface for healthcare and surveillance systems",
        "use_limitations": "No facility outage, service territory, or disease outcome is inferred.",
        "retrieval_url": "reports/phase3b_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase5_freight_context",
        "title": "Accepted Phase 5C freight dependency and critical-interface context",
        "url": "reports/phase5c_freight_dependency_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "regional freight, gateway, interchange, and generalized market interfaces",
        "method_or_product": "accepted freight dependency register and interface layer",
        "evidence_use": "food/freight connectivity and distribution-interface context",
        "use_limitations": "No commodity volume, shipment route, carrier operation, outbreak, or facility-specific food claim is inferred.",
        "retrieval_url": "reports/phase5c_freight_dependency_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase6_ecology_context",
        "title": "Accepted Phase 6A ecology and biodiversity context",
        "url": "reports/phase6a_ecology_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "Western Basin / wetland, riparian, terrestrial, host-ecology context",
        "method_or_product": "accepted ecological system skeleton",
        "evidence_use": "generalized host, habitat, wetland, and landscape interfaces",
        "use_limitations": "No sensitive species location, abundance, contact rate, infection, or disease burden is inferred.",
        "retrieval_url": "reports/phase6a_ecology_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase9_hazard_dependency_context",
        "title": "Accepted Phase 9B climate/hazard dependency context",
        "url": "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 qualitative dependency layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "station, county, watershed, shoreline, and regional context",
        "method_or_product": "accepted climate/hazard dependencies and resilience interfaces",
        "evidence_use": "flooding, precipitation, seasonality, and infrastructure-interface context",
        "use_limitations": "No disease incidence, exposure probability, hazard probability, or deterministic climate-to-disease claim is inferred.",
        "retrieval_url": "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase11_mobility_context",
        "title": "Accepted Phase 11B population, mobility, and system-dependency context",
        "url": "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "county, place, generalized employment, and aggregate mobility interfaces",
        "method_or_product": "accepted mobility observations and qualitative dependencies",
        "evidence_use": "population/contact structure and generalized mobility-connectivity context",
        "use_limitations": "Commuting is not transmission; no individual trajectory, contact network, or local disease inference is created.",
        "retrieval_url": "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase12_vector_dependency_context",
        "title": "Accepted Phase 12B vector/environment/human dependency context",
        "url": "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 qualitative dependency layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "county, habitat, program, watershed, and generalized regional context",
        "method_or_product": "accepted vector/environment/human dependency register and map",
        "evidence_use": "vector ecology, habitat, surveillance, and potential-interface context",
        "use_limitations": "Vector ecology and potential contact are not human exposure, infection, disease, or incidence.",
        "retrieval_url": "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
    {
        "source_id": "phase10_coordination_context",
        "title": "Accepted Phase 10B governance dependency and coordination context",
        "url": "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "source_type": "repository_accepted_layer",
        "publication_or_period": "accepted/frozen 2026 qualitative governance layer",
        "retrieval_date": RETRIEVAL_DATE,
        "geographic_scale": "agency, program, jurisdictional, interstate, binational, and public/private interfaces",
        "method_or_product": "accepted authority, dependency, and coordination artifacts",
        "evidence_use": "monitoring, reporting, decision-support, intervention, and coordination interfaces",
        "use_limitations": "Monitoring is not control; coordination capacity is not proof of response effectiveness or disease burden.",
        "retrieval_url": "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
        "retrieval_provenance": "accepted/frozen repository artifact reference; hash-checked by Phase 13B validator",
    },
]
EXTRA_SOURCE_IDS = [row["source_id"] for row in EXTRA_SOURCES]
SOURCE_ORDER = BASE_SOURCE_IDS + EXTRA_SOURCE_IDS

SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
]

DEPENDENCY_COLUMNS = [
    "dependency_id", "from_id", "to_id", "relationship_type", "dependency_type",
    "archetype", "documented_or_inferred", "relationship_basis", "direction",
    "spatial_scale", "temporal_scope", "evidence_strength", "source_id",
    "uncertainty_id", "uncertainty", "confidence", "reality_status", "canon_status",
    "relevant_disease_systems", "notes",
]

MATRIX_COLUMNS = [
    "matrix_id", "archetype", "climate_sensitivity", "hydrologic_sensitivity",
    "vector_dependence", "food_freight_dependence", "population_contact_dependence",
    "mobility_dependence", "healthcare_dependence", "surveillance_dependence",
    "governance_dependence", "spatial_scale", "temporal_scope",
    "source_ids", "notes",
]

CROSSWALK_COLUMNS = [
    "evidence_id", "dependency_id", "claim_type", "claim_status", "source_id",
    "evidence_basis", "spatial_scale", "temporal_scope", "supported_statement",
    "not_supported_statement",
]

UNCERTAINTY_COLUMNS = [
    "uncertainty_id", "subject", "category", "statement", "resolution_status",
    "source_id", "confidence", "notes",
]

UNCERTAINTIES = [
    ["IDBU-001", "IDB-001", "climate_vector", "Climate observations can frame seasonal context, but this package does not estimate vector suitability, abundance, or disease incidence.", "open", "phase9_hazard_dependency_context", "high", "Driver is not deterministic cause."],
    ["IDBU-002", "IDB-002", "hydrology_vector", "Standing-water and wetland context can identify a habitat interface, but vector response is not quantified.", "open", "phase1_water_context", "high", "Hydrology is not a vector count or disease surface."],
    ["IDBU-003", "IDB-004", "vector_human", "Vector ecology and pathogen-in-vector context do not establish human contact, exposure, infection, or clinical disease.", "qualified", "phase12_vector_dependency_context", "high", "Vector ecology != human disease."],
    ["IDBU-004", "IDB-010", "water_chain", "Water-system condition or flooding identifies an exposure opportunity only; contamination, exposure, infection, illness, and outbreak require separate evidence.", "qualified", "s13_cdc_water_surv", "high", "Contamination != illness."],
    ["IDBU-005", "IDB-009", "infrastructure_condition", "Water and energy infrastructure are generalized dependencies; facility condition and treatment performance are not modeled.", "open", "phase1_water_context", "high", "No facility-specific burden or service assignment."],
    ["IDBU-006", "IDB-013", "food_freight", "Food/freight connectivity is an interface for distribution and investigation, not evidence of shipment, contamination, or outbreak.", "open", "phase5_freight_context", "high", "No commodity route or outbreak claim."],
    ["IDBU-007", "IDB-019", "population_contact", "Population concentration identifies a possible contact structure, not contact events, exposure, infection, or incidence.", "qualified", "phase11_population", "high", "Aggregate settlement scale only."],
    ["IDBU-008", "IDB-020", "mobility", "Aggregate mobility can indicate possible connectivity, but commuting and movement are not transmission observations.", "qualified", "phase11_mobility_context", "high", "Mobility != transmission."],
    ["IDBU-009", "IDB-021", "respiratory_setting", "Indoor/community setting is a qualitative interface for respiratory systems; no density-to-incidence relationship is estimated.", "open", "s13_cdc_flu_methods", "high", "Population concentration != incidence."],
    ["IDBU-010", "IDB-026", "zoonotic_host", "Wildlife, domestic-animal, and occupational interfaces are pathway contexts; animal contact does not establish human infection or disease.", "qualified", "s13_cdc_rabies", "high", "Animal endpoint and human endpoint remain separate."],
    ["IDBU-011", "IDB-031", "surveillance_ascertainment", "Surveillance intensity, testing, reporting, and laboratory participation change detection opportunity and do not equal incidence or burden.", "qualified", "s13_nndss_about", "high", "Surveillance != incidence."],
    ["IDBU-012", "IDB-034", "healthcare_scale", "Healthcare facility presence creates a care and detection interface; it does not establish facility-level disease burden.", "qualified", "s13_cdc_nhsn", "high", "Healthcare presence != prevalence."],
    ["IDBU-013", "IDB-033", "infrastructure_continuity", "Energy and communications dependencies may affect continuity of healthcare or surveillance functions, but no outage probability or health outcome is modeled.", "open", "phase3_energy_context", "high", "Infrastructure dependency is not disease burden."],
    ["IDBU-014", "IDB-036", "spatial_scale", "County, sewershed, facility, watershed, program, and generalized regional scales remain distinct and are not downscaled to neighborhoods or individuals.", "qualified", "phase11_population", "high", "Native source scale is retained."],
]


def normalize_url(url: str) -> str:
    value = str(url).strip()
    stripped = value.rstrip("/")
    return stripped or value


def make_source_rows() -> list[dict[str, str]]:
    baseline = pd.read_csv(BASELINE_SOURCES, dtype=str).fillna("")
    by_id = {row["source_id"]: row.to_dict() for _, row in baseline.iterrows()}
    by_id.update({row["source_id"]: row for row in EXTRA_SOURCES})
    assert set(SOURCE_ORDER) <= set(by_id)
    rows = [{column: str(by_id[source_id][column]) for column in SOURCE_COLUMNS} for source_id in SOURCE_ORDER]
    for row in rows:
        row["url"] = normalize_url(row["url"])
    assert len(rows) == len(SOURCE_ORDER) and len({row["source_id"] for row in rows}) == len(rows)
    return rows


def dependency_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(dep_id: str, from_id: str, to_id: str, relationship_type: str, dependency_type: str,
            archetype: str, status: str, basis: str, direction: str, scale: str, temporal: str,
            strength: str, source_id: str, uncertainty_id: str, confidence: str,
            systems: str, notes: str) -> None:
        uncertainty = next(row[3] for row in UNCERTAINTIES if row[0] == uncertainty_id)
        rows.append({
            "dependency_id": dep_id, "from_id": from_id, "to_id": to_id,
            "relationship_type": relationship_type, "dependency_type": dependency_type,
            "archetype": archetype, "documented_or_inferred": status,
            "relationship_basis": basis, "direction": direction, "spatial_scale": scale,
            "temporal_scope": temporal, "evidence_strength": strength, "source_id": source_id,
            "uncertainty_id": uncertainty_id, "uncertainty": uncertainty,
            "confidence": confidence, "reality_status": "real", "canon_status": "inferred" if status == "inferred" else "verified",
            "relevant_disease_systems": systems, "notes": notes,
        })

    # Vector-borne: drivers and ecology frame opportunity; they do not become disease outcomes.
    add("IDB-001", "EXT-CLIMATE", "EXT-VECTOR-ECOLOGY", "frames_seasonality", "environmental driver", "vector-borne", "inferred", "accepted_layer_plus_project_inference", "climate context -> seasonal vector ecology potential", "station/county/regional", "2026 context; seasonal", "moderate", "phase9_hazard_dependency_context", "IDBU-001", "limited", "DID-001;DID-002", "Accepted climate/hazard context can frame seasonality; it is not a thermal suitability model or disease forecast.")
    add("IDB-002", "EXT-HYDROLOGY", "EXT-VECTOR-ECOLOGY", "creates_habitat_opportunity", "ecological mediator", "vector-borne", "inferred", "accepted_layer_plus_project_inference", "hydrology context -> standing-water/vector habitat opportunity", "watershed/wetland/ditch generalized", "2026 context; event/season dependent", "moderate", "phase1_water_context", "IDBU-002", "limited", "DID-001", "Hydrology and wetland context can identify a habitat interface, but no vector count, abundance response, or human disease result is inferred.")
    add("IDB-003", "EXT-ECOLOGY", "EXT-VECTOR-ECOLOGY", "mediates_host_habitat", "ecological mediator", "vector-borne", "inferred", "accepted_layer_plus_project_inference", "ecology/host context -> vector lifecycle interface", "regional ecology/forest/wetland", "2026 context", "moderate", "phase6_ecology_context", "IDBU-003", "limited", "DID-001;DID-002", "Accepted ecology and vector layers meet at generalized habitat and host interfaces; no abundance or contact rate is produced.")
    add("IDB-004", "EXT-VECTOR-ECOLOGY", "DID-001", "frames_transmission_opportunity", "ecological mediator", "vector-borne", "inferred", "accepted_layer_plus_project_inference", "vector ecology context -> vector-borne transmission opportunity", "county/habitat/program", "2026 context", "moderate", "phase12_vector_dependency_context", "IDBU-003", "limited", "DID-001", "Vector ecology is a dependency context for the West Nile system; it is not human infection, disease, incidence, or local transmission.")
    add("IDB-005", "HOST-001", "DID-002", "frames_contact_opportunity", "population/contact interface", "vector-borne", "inferred", "project_inference", "aggregate settlement context -> possible human-vector contact interface", "county/place/generalized employment", "2026 context", "limited", "phase11_population", "IDBU-007", "limited", "DID-002", "Population and settlement context identifies a possible interface only; no individual contact, exposure, infection, or disease is assigned.")
    add("IDB-006", "SUR-003", "REF-4", "feeds_observation", "surveillance dependency", "vector-borne", "inferred", "accepted_layer_plus_project_inference", "vector surveillance -> observation/data interface", "agency/county/state/program", "2026 program context", "moderate", "phase4_information", "IDBU-011", "moderate", "DID-001;SUR-003", "Vector detections can enter an observation chain; this is not a disease observation or a risk estimate; detection intensity is not incidence, abundance, or response effectiveness.")

    # Waterborne/environmental: condition and infrastructure create opportunity, not illness.
    add("IDB-007", "EXT-HYDROLOGY", "ENV-001", "conditions_exposure_opportunity", "environmental driver", "waterborne/environmental", "inferred", "accepted_layer_plus_project_inference", "hydrology/flooding context -> water exposure opportunity", "watershed/source/recreational water", "2026 context; event dependent", "moderate", "phase1_water_context", "IDBU-004", "limited", "DID-003;DID-004", "Water-system and hydrologic context support pathway analysis only; no contamination or exposure event is asserted.")
    add("IDB-008", "EXT-FLOODING", "ENV-001", "disrupts_or_connects_pathway", "environmental driver", "waterborne/environmental", "inferred", "accepted_layer_plus_project_inference", "flooding/runoff context -> water-system exposure opportunity", "watershed/floodplain/source/recreational water", "2026 context; event dependent", "moderate", "phase9_hazard_dependency_context", "IDBU-004", "limited", "DID-004", "Flooding and runoff are qualitative pathway interfaces; the record does not establish contamination, infection, illness, or outbreak.")
    add("IDB-009", "EXT-WATER-INFRASTRUCTURE", "ENV-001", "depends_on_system_condition", "infrastructure dependency", "waterborne/environmental", "inferred", "accepted_layer_plus_project_inference", "water infrastructure condition -> treatment/source-water pathway context", "water system/source/utility generalized", "2026 context", "moderate", "phase1_water_context", "IDBU-005", "limited", "DID-003;DID-004", "Infrastructure condition is generalized; no treatment failure, facility condition, receptor exposure, or disease burden is inferred.")
    add("IDB-010", "ENV-001", "DID-004", "frames_exposure_opportunity", "population/contact interface", "waterborne/environmental", "documented", "documented_source", "water interface -> waterborne exposure opportunity", "source/recreational-water/investigation", "current surveillance/pathway context", "strong", "s13_cdc_water_surv", "IDBU-004", "high", "DID-004", "CDC waterborne surveillance supports an exposure/pathway interface; contamination is not infection or illness.")
    add("IDB-011", "SUR-004", "INST-001", "supplies_case_observation", "surveillance dependency", "waterborne/environmental", "documented", "documented_source", "legionellosis surveillance -> laboratory/reporting interface", "jurisdiction/national/investigation", "current program context", "strong", "s13_cdc_legionella_surv", "IDBU-011", "high", "DID-003;SUR-004", "Legionellosis reporting and exposure-setting information are surveillance interfaces; source attribution requires investigation.")
    add("IDB-012", "REF-4", "REF-10", "supports_response_coordination", "institutional response dependency", "waterborne/environmental", "inferred", "accepted_layer_plus_project_inference", "observation/data -> governance/coordination decision interface", "program/agency/jurisdiction", "2026 context", "moderate", "phase10_coordination_context", "IDBU-011", "moderate", "DID-004;SUR-005", "Observation may inform coordination; this is not a risk model; monitoring is not control and no response effectiveness is estimated.")

    # Foodborne/enteric: production, processing, and freight remain generalized interfaces.
    add("IDB-013", "EXT-FOOD-PRODUCTION", "EXT-FOOD-PROCESSING", "connects_food_system", "food/freight interface", "foodborne/enteric", "inferred", "accepted_layer_plus_project_inference", "food production context -> processing/distribution interface", "regional/agricultural/bulk generalized", "2026 context", "limited", "phase5_freight_context", "IDBU-006", "limited", "DID-005;DID-006;DID-007", "Accepted freight/material context supports a generalized food-system interface; no facility, commodity, shipment, or contamination claim is made.")
    add("IDB-014", "EXT-FOOD-PROCESSING", "EXT-FREIGHT", "connects_distribution", "food/freight interface", "foodborne/enteric", "inferred", "accepted_layer_plus_project_inference", "food processing context -> generalized freight/distribution connectivity", "regional freight/gateway/interchange", "2026 context", "limited", "phase5_freight_context", "IDBU-006", "limited", "DID-005;DID-006;DID-007", "Freight connectivity is an interface for propagation opportunity and investigation, not evidence of a shipment or outbreak.")
    add("IDB-015", "EXT-FREIGHT", "DID-005", "creates_propagation_opportunity", "food/freight interface", "foodborne/enteric", "inferred", "accepted_layer_plus_project_inference", "distribution connectivity -> possible foodborne propagation opportunity", "regional freight/gateway/interchange", "2026 context", "limited", "phase5_freight_context", "IDBU-006", "limited", "DID-005", "Food/freight connectivity is an interface, not a shipment, contaminated product, exposure, infection, incidence, or outbreak finding.")
    add("IDB-016", "DID-005", "SUR-006", "is_observed_by", "surveillance dependency", "foodborne/enteric", "documented", "documented_source", "enteric disease system -> laboratory/case surveillance", "state/territorial/national laboratory", "current program context", "strong", "s13_cdc_enteric", "IDBU-011", "high", "DID-005;DID-006;DID-007;SUR-006", "Laboratory and case surveillance identifies reported records; it does not capture all community infections or exposure locations.")
    add("IDB-017", "SUR-006", "SUR-007", "complements_detection", "surveillance dependency", "foodborne/enteric", "documented", "documented_source", "laboratory/case surveillance -> active surveillance interface", "state/territorial/FoodNet surveillance area", "current program context", "strong", "s13_cdc_foodnet", "IDBU-011", "high", "DID-005;DID-006;DID-007", "FoodNet is complementary surveillance with its own coverage and denominator; it is not a Western Basin incidence estimate.")
    add("IDB-018", "SUR-005", "REF-10", "supports_investigation_response", "institutional response dependency", "foodborne/enteric", "inferred", "accepted_layer_plus_project_inference", "outbreak reporting/investigation -> governance response interface", "state/local/territorial investigation", "current program context", "moderate", "s13_cdc_nors", "IDBU-006", "moderate", "DID-005;DID-006;DID-007;SUR-005", "Outbreak reporting can support investigation and coordination; this is not outbreak evidence and connectivity is not an outbreak assertion.")

    # Respiratory: contact structure and mobility are opportunity interfaces, not incidence.
    add("IDB-019", "EXT-SETTLEMENT", "EXT-CONTACT-STRUCTURE", "structures_contact_opportunity", "population/contact interface", "respiratory", "inferred", "accepted_layer_plus_project_inference", "settlement context -> possible contact structure", "county/place/generalized settlement", "2026 context", "moderate", "phase11_population", "IDBU-007", "limited", "DID-008;DID-009", "Population concentration is an interface for contact structure only; no density-to-incidence relationship is estimated.")
    add("IDB-020", "EXT-MOBILITY", "EXT-CONTACT-STRUCTURE", "connects_contact_opportunity", "mobility interface", "respiratory", "inferred", "accepted_layer_plus_project_inference", "aggregate mobility -> possible connectivity among settings", "county/place/generalized mobility", "2026 context", "limited", "phase11_mobility_context", "IDBU-008", "limited", "DID-008;DID-009", "Aggregate mobility and commuting do not identify transmission, contacts, infections, or local incidence.")
    add("IDB-021", "EXT-CONTACT-STRUCTURE", "DID-008", "frames_transmission_opportunity", "population/contact interface", "respiratory", "inferred", "project_inference", "contact structure -> respiratory transmission opportunity", "community/setting/generalized", "2026 context", "limited", "s13_cdc_flu_methods", "IDBU-009", "limited", "DID-008", "Respiratory contact opportunity is a systems interface, not a population-density incidence model.")
    add("IDB-022", "DID-009", "SUR-009", "is_observed_by", "surveillance dependency", "respiratory", "documented", "documented_source", "SARS-CoV-2 community system -> wastewater observation", "sewershed/community/state/regional", "current program context", "strong", "s13_cdc_wastewater", "IDBU-011", "high", "DID-009;SUR-009", "Wastewater supplies a community-level signal; it does not determine the number of infections or individual exposure.")
    add("IDB-023", "SUR-008", "INST-001", "supplies_surveillance_data", "surveillance dependency", "respiratory", "documented", "documented_source", "influenza surveillance streams -> laboratory/reporting interface", "national/HHS region/state/stream", "2026 weekly program context", "strong", "s13_cdc_flu_methods", "IDBU-011", "high", "DID-008;SUR-008", "Influenza laboratory, outpatient, hospital, and mortality streams have distinct denominators and are not one transmission rate.")
    add("IDB-024", "REF-4", "REF-10", "supports_response_coordination", "institutional response dependency", "respiratory", "inferred", "accepted_layer_plus_project_inference", "observation/data -> governance/coordination decision interface", "program/agency/jurisdiction", "2026 context", "moderate", "phase10_coordination_context", "IDBU-011", "moderate", "DID-008;DID-009;SUR-008;SUR-009", "Detection can inform response interfaces; surveillance intensity is not disease intensity and response effectiveness is not estimated.")

    # Zoonotic: animal and human endpoints remain separate.
    add("IDB-025", "EXT-ECOLOGY", "EXT-ANIMAL-HOSTS", "mediates_host_interface", "ecological mediator", "zoonotic", "inferred", "accepted_layer_plus_project_inference", "ecology context -> wildlife/domestic host interface", "regional ecology/wildlife/domestic animal", "2026 context", "limited", "phase6_ecology_context", "IDBU-010", "limited", "DID-010", "Generalized host ecology is retained without an animal abundance, contact, or infection estimate.")
    add("IDB-026", "EXT-ANIMAL-HOSTS", "DID-010", "frames_animal_human_opportunity", "population/contact interface", "zoonotic", "documented", "documented_source", "animal host/contact interface -> possible rabies exposure opportunity", "wildlife/domestic animal/exposure investigation", "current public-health context", "strong", "s13_cdc_rabies", "IDBU-010", "high", "DID-010", "Rabies animal contact and potential-exposure pathways are documented; human infection or disease is not inferred.")
    add("IDB-027", "EXT-OCCUPATIONAL-CONTACT", "DID-010", "frames_contact_opportunity", "population/contact interface", "zoonotic", "inferred", "documented_source_plus_project_inference", "occupational/environmental contact -> possible animal-human interface", "occupational/exposure investigation", "current public-health context", "limited", "s13_cdc_rabies", "IDBU-010", "limited", "DID-010", "Potential contact is not documented exposure, infection, clinical disease, or disease burden.")
    add("IDB-028", "DID-010", "SUR-010", "is_observed_by", "surveillance dependency", "zoonotic", "documented", "documented_source", "rabies system -> animal testing/exposure/PEP surveillance", "animal-control/veterinary/public-health", "current program context", "strong", "s13_cdc_rabies", "IDBU-011", "high", "DID-010;SUR-010", "Animal testing, exposure assessment, and post-exposure prophylaxis are separate response records.")
    add("IDB-029", "SUR-010", "REF-10", "supports_response_coordination", "institutional response dependency", "zoonotic", "inferred", "accepted_layer_plus_project_inference", "animal/public-health surveillance -> coordination interface", "animal/state/exposure investigation", "current program context", "moderate", "phase10_coordination_context", "IDBU-011", "moderate", "DID-010;SUR-010", "Surveillance can inform coordination; a response interface is not proof of complete detection or outcome.")
    add("IDB-030", "SUR-010", "INST-001", "supplies_animal_observations", "surveillance dependency", "zoonotic", "documented", "documented_source", "animal testing/exposure records -> reporting/laboratory interface", "animal-control/veterinary/public-health", "current program context", "moderate", "s13_cdc_rabies", "IDBU-011", "high", "DID-010;SUR-010", "Animal surveillance and human case surveillance remain distinct streams.")

    # Healthcare/AMR: care, detection, and infrastructure interfaces are not prevalence measures.
    add("IDB-031", "EXT-HEALTHCARE", "DID-011", "frames_care_detection_interface", "healthcare interface", "healthcare/AMR", "documented", "documented_source", "healthcare setting -> HAI care/detection interface", "facility/state/regional/national", "current program context", "strong", "s13_cdc_nhsn", "IDBU-012", "high", "DID-011", "Healthcare presence != facility-level disease burden; healthcare-associated infection surveillance is a facility reporting interface.")
    add("IDB-032", "EXT-HEALTHCARE", "DID-012", "frames_resistance_detection_interface", "healthcare interface", "healthcare/AMR", "documented", "documented_source", "healthcare/laboratory setting -> antimicrobial-resistance detection interface", "facility/state/regional/national", "current program context", "moderate", "s13_cdc_ar", "IDBU-012", "moderate", "DID-012", "Generalized AR surveillance is retained without transferring national estimates to the Western Basin or ranking facilities.")
    add("IDB-033", "EXT-INFRASTRUCTURE", "EXT-HEALTHCARE", "supports_service_continuity", "infrastructure dependency", "healthcare/AMR", "inferred", "accepted_layer_plus_project_inference", "energy/infrastructure continuity -> healthcare and laboratory service interface", "regional/generalized infrastructure", "2026 context", "limited", "phase3_energy_context", "IDBU-013", "limited", "DID-011;DID-012", "Energy dependency is a continuity interface only; no outage probability, facility performance, disease burden, or health outcome is modeled.")
    add("IDB-034", "DID-011", "SUR-011", "is_observed_by", "surveillance dependency", "healthcare/AMR", "documented", "documented_source", "HAI system -> NHSN surveillance interface", "facility/state/regional/national", "current program context", "strong", "s13_cdc_nhsn", "IDBU-011", "high", "DID-011;SUR-011", "NHSN provides standardized facility reporting context; it is not a community-incidence denominator.")
    add("IDB-035", "DID-012", "SUR-012", "is_observed_by", "surveillance dependency", "healthcare/AMR", "documented", "documented_source", "AMR system -> laboratory/public-health surveillance interface", "facility/state/regional/national", "current program context", "moderate", "s13_cdc_ar", "IDBU-011", "moderate", "DID-012;SUR-012", "AMR observations are a generalized detection/response interface; national estimates are not regional observations.")
    add("IDB-036", "SUR-011", "REF-10", "supports_infection_control_coordination", "institutional response dependency", "healthcare/AMR", "inferred", "accepted_layer_plus_project_inference", "healthcare surveillance -> governance/coordination interface", "facility/state/regional/program", "current program context", "moderate", "phase10_coordination_context", "IDBU-014", "moderate", "DID-011;SUR-011", "Surveillance can support coordination and infection-control interfaces; it does not establish facility-level prevalence or response effectiveness."),
    assert len(rows) == 36 and len({row["dependency_id"] for row in rows}) == 36
    return rows


def matrix_rows() -> list[dict[str, str]]:
    rows = [
        ["IDBM-001", "vector-borne", "moderate", "moderate", "strong", "not_applicable", "limited", "limited", "limited", "strong", "moderate", "county/habitat/program", "seasonal/current program", "phase9_hazard_dependency_context;phase1_water_context;phase12_vector_dependency_context;phase4_information", "Qualitative dependency structure only; climate/vector context does not become incidence or risk."],
        ["IDBM-002", "waterborne/environmental", "limited", "strong", "not_applicable", "limited", "limited", "limited", "moderate", "strong", "strong", "watershed/source/recreational/utility", "event/current program", "phase1_water_context;phase9_hazard_dependency_context;s13_cdc_water_surv;phase10_coordination_context", "Water condition, infrastructure, pathway, surveillance, and response interfaces remain separate from illness."],
        ["IDBM-003", "foodborne/enteric", "limited", "limited", "not_applicable", "strong", "limited", "moderate", "moderate", "strong", "moderate", "regional food/freight/program", "current program", "phase5_freight_context;s13_cdc_enteric;s13_cdc_foodnet;s13_cdc_nors", "Food/freight dependence is a propagation/investigation interface, not an outbreak or burden measure."],
        ["IDBM-004", "respiratory", "moderate", "not_applicable", "not_applicable", "not_applicable", "strong", "moderate", "moderate", "strong", "moderate", "community/sewershed/stream", "seasonal/current program", "phase11_population;phase11_mobility_context;s13_cdc_flu_methods;s13_cdc_wastewater;phase10_coordination_context", "Contact structure, mobility connectivity, healthcare, and surveillance are qualitative interfaces, not incidence predictors."],
        ["IDBM-005", "zoonotic", "limited", "limited", "not_applicable", "not_applicable", "moderate", "limited", "moderate", "strong", "moderate", "animal/state/exposure investigation", "current program", "phase6_ecology_context;s13_cdc_rabies;phase10_coordination_context", "Animal, potential-exposure, PEP, human infection, and disease endpoints remain distinct."],
        ["IDBM-006", "healthcare/AMR", "not_applicable", "not_applicable", "not_applicable", "not_applicable", "limited", "limited", "strong", "strong", "strong", "facility/state/regional/national", "current program", "phase3_energy_context;s13_cdc_nhsn;s13_cdc_ar;phase10_coordination_context", "Healthcare and infrastructure dependencies describe care/detection interfaces, not facility prevalence or community burden."],
    ]
    assert all(len(row) == len(MATRIX_COLUMNS) for row in rows)
    return [dict(zip(MATRIX_COLUMNS, row)) for row in rows]


def uncertainty_rows() -> list[dict[str, str]]:
    return [dict(zip(UNCERTAINTY_COLUMNS, row)) for row in UNCERTAINTIES]


def crosswalk_rows(dependencies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for index, dep in enumerate(dependencies, 1):
        not_supported = "The relationship does not establish pathogen presence, exposure, infection, reported case, local transmission, outbreak, disease burden, individual risk, or a quantitative risk score."
        if dep["archetype"] == "vector-borne":
            not_supported = "It does not establish vector abundance, human contact, infection, disease, incidence, or local transmission."
        elif dep["archetype"] == "waterborne/environmental":
            not_supported = "It does not establish contamination, treatment failure, exposure, infection, illness, or outbreak."
        elif dep["archetype"] == "foodborne/enteric":
            not_supported = "It does not establish a shipment, contaminated product, exposure, infection, outbreak, or incidence."
        elif dep["archetype"] == "respiratory":
            not_supported = "It does not establish contact events, infection, incidence, or transmission from density or mobility."
        elif dep["archetype"] == "zoonotic":
            not_supported = "It does not establish animal-to-human exposure, infection, clinical disease, or local transmission."
        elif dep["archetype"] == "healthcare/AMR":
            not_supported = "It does not establish facility-level prevalence, community incidence, resistance burden, or outcome."
        rows.append({
            "evidence_id": f"IDB-E-{index:03d}",
            "dependency_id": dep["dependency_id"],
            "claim_type": dep["dependency_type"],
            "claim_status": dep["documented_or_inferred"],
            "source_id": dep["source_id"],
            "evidence_basis": dep["relationship_basis"],
            "spatial_scale": dep["spatial_scale"],
            "temporal_scope": dep["temporal_scope"],
            "supported_statement": dep["notes"],
            "not_supported_statement": not_supported,
        })
    return rows


def assert_rows(name: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    assert rows and all(set(row) == set(columns) for row in rows), name
    assert all(all(str(row[column]).strip() for column in columns) for row in rows), name


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    assert_rows(str(path), rows, columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, lineterminator="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_block() -> str:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    return "\n## Sources\n\n" + "\n".join(f"[{row['id']}] {row['url']}" for row in ledger["sources"]) + "\n"


def citation_lines() -> str:
    groups = []
    for start in range(1, len(SOURCE_ORDER) + 1, 3):
        ids = list(range(start, min(start + 3, len(SOURCE_ORDER) + 1)))
        groups.append("Source-registry entries " + "".join(f"[{i}]" for i in ids) + " are retained with their source identity, scale, method, and limitations.")
    return "\n".join(groups)


def write_ledger(source_rows: list[dict[str, str]]) -> None:
    payload = {
        "version": 1,
        "sources": [
            {"id": index, "url": row["url"], "title": row["title"], "accessed": RETRIEVAL_DATE}
            for index, row in enumerate(source_rows, 1)
        ],
    }
    LEDGER.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_reports(dependencies: list[dict[str, str]], matrix: list[dict[str, str]], crosswalk: list[dict[str, str]], sources: list[dict[str, str]], uncertainties: list[dict[str, str]]) -> list[Path]:
    common_sources = citation_lines()
    source_report = f"""# Phase 13B Infectious Disease Transmission Dependencies Sources

Phase 13B reuses the accepted Phase 13A disease/system baseline rather than creating a new disease catalog. The Phase 13A CDC, state, laboratory, healthcare, and reporting references are retained at claim level in the dependency source registry. {common_sources}

Accepted repository context is used for climate and hazard dependencies, water/hydrology, ecology, vector/environment interfaces, population and mobility, data/observation systems, governance/coordination, freight, and generalized infrastructure. These references are contextual inputs; their protected artifacts are not copied into or modified by Phase 13B. {common_sources}

The dependency source registry contains {len(sources)} rows. External sources retain primary source identity and retrieval provenance from Phase 13A. Accepted-layer references identify the repository manifest used for context and are not evidence of disease outcomes. {common_sources}

Every dependency row has a source ID, evidence basis, spatial scale, temporal scope, uncertainty, confidence, and documented-versus-inferred status. {common_sources}
""" + source_block()
    assumptions = f"""# Phase 13B Infectious Disease Transmission Dependencies Assumptions

## Scope

Phase 13B is a qualitative dependency/interface layer over the accepted Phase 13A factual 2026 infectious-disease baseline. It contains {len(dependencies)} dependency-register rows and edges, {len(matrix)} archetype matrix rows, {len(crosswalk)} evidence crosswalk rows, {len(uncertainties)} explicit uncertainties, and Map 42.

The layer does not create a new disease catalog. The six archetypes are vector-borne, waterborne/environmental, foodborne/enteric, respiratory, zoonotic, and healthcare/AMR. Not every disease is forced into every dependency category. Phase 13A disease and surveillance node IDs are reused where a disease-system or observation endpoint is represented. {common_sources}

## Relationship discipline

Each edge is explicitly documented or inferred and carries a relationship class, evidence basis, direction, native spatial scale, temporal scope, source ID, uncertainty, confidence, and relevant disease-system IDs. An inferred systems dependency is not presented as a documented epidemiological relationship. {common_sources}

The matrix uses strong, moderate, limited, unknown, and not_applicable as bounded qualitative labels. It is not summed, ranked, or interpreted as a disease-risk, vulnerability, service-access, or burden index. Unknown is retained as unknown. {common_sources}

## Scientific boundaries

Pathogen presence ≠ exposure ≠ infection ≠ reported case ≠ local transmission ≠ outbreak ≠ disease burden. Driver ≠ deterministic cause. Association ≠ attribution. Surveillance ≠ incidence. Mobility ≠ transmission. Contamination ≠ illness. Vector ecology ≠ human disease. Healthcare presence ≠ facility-level disease burden. Food/freight connectivity ≠ outbreak. {common_sources}

No individual cases, individual risk, neighborhood downscaling, disease-incidence forecast, outbreak probability, composite risk score, disease burden aggregation, or Phase 13C content is included. {common_sources}

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. Phase 6B manifest status wording mismatch and Phase 3A missing manifest status remain deferred and unchanged. {common_sources}
""" + source_block()
    findings = f"""# Phase 13B Infectious Disease Transmission Dependencies Findings, 2026

## Principal cross-system findings

FACT: The accepted Phase 13A baseline already provides distinct vector-borne, waterborne/environmental, foodborne/enteric, respiratory, zoonotic, and healthcare/AMR system and surveillance nodes. Phase 13B adds interfaces among those nodes and accepted contextual layers without adding diseases. [1][3][5]

INFERENCE: Climate and hydrology can frame seasonal and habitat opportunity for vector-borne systems, but the dependency is qualitative and does not establish vector abundance, human contact, infection, disease, or incidence. [21][26][27]

INFERENCE: Water-system condition, flooding/runoff, and generalized treatment/infrastructure context meet waterborne pathways at an exposure-opportunity interface. The chain stops before contamination-to-exposure, exposure-to-infection, and infection-to-illness claims unless separate evidence is present. [7][20][26][30]

INFERENCE: Food production, processing, and freight/gateway connectivity create a generalized distribution and investigation interface for enteric systems. The package does not infer a shipment, contaminated product, propagation event, or outbreak. [9][10][28]

INFERENCE: Settlement concentration and aggregate mobility can identify possible contact structure and connectivity for respiratory systems. They do not establish contacts, transmission, infection, incidence, or density-based disease risk. [12][22][29]

FACT: Rabies remains an animal-human response interface in which animal testing, potential exposure, post-exposure prophylaxis, human infection, and disease are separate endpoints. [14][25]

FACT: NHSN and antimicrobial-resistance references provide healthcare and laboratory detection interfaces. Healthcare presence, reporting participation, or generalized energy continuity does not establish facility prevalence, community incidence, resistance burden, or health outcome. [15][16][26]

## Surveillance and governance

INFERENCE: Observation and reporting systems are dependencies for detection and decision support, not direct measurements of incidence. More testing, reporting, or laboratory participation can change what is detected without proving more disease. [1][9][11]

INFERENCE: Governance and coordination are interfaces through which signals may be interpreted and acted upon. Monitoring is not control, coordination is not effectiveness, and a response interface is not proof of complete detection or successful intervention. [24][25][30]

UNCERTAINTY: Source systems use different case definitions, denominators, reporting periods, surveillance methods, spatial scales, and ascertainment pathways. The matrix therefore remains qualitative and does not compare unlike diseases or rank places. [1][2][9]

## Evidence boundaries

BOUNDARY: The dependency register is not a transmission network, incidence model, outbreak model, disease-risk ranking, vulnerability index, or disease-burden estimate. Every claim crosswalk records what the source or accepted layer supports and what it does not support. [7][13][15]

BOUNDARY: County, sewershed, facility, program, watershed, and generalized regional scales remain distinct. No case, exposure, transmission, or burden is downscaled to a neighborhood, census tract, municipality, facility, or individual. [4][13][22]

Active holds and deferred maintenance remain unchanged. [26][30]
""" + citation_lines() + source_block()
    qa = f"""# Phase 13B Infectious Disease Transmission Dependencies QA

The generated package contains {len(dependencies)} dependency-register rows, {len(dependencies)} dependency edges, {len(matrix)} matrix rows, {len(crosswalk)} evidence-crosswalk rows, {len(sources)} source rows, {len(uncertainties)} uncertainty rows, and Map 42 PNG/SVG. {citation_lines()}

The Phase 13B Python validator checks exact schemas, producer row widths, unique IDs, Phase 13A node references, source and uncertainty references, documented-versus-inferred vocabulary, relationship classes, spatial scale, temporal scope, matrix labels, claim-level evidence crosswalks, map raster/SVG integrity, phase13A freeze integrity, Phase 1–12 immutability, active holds, and prohibited content. {citation_lines()}

The independent R validator re-reads the Phase 13B tables through a separate base-R path, checks the same counts and semantic boundaries, independently recomputes hashes for Phase 13A and prior protected manifests, and validates Map 42 PNG/SVG. {citation_lines()}

Negative-scope checks explicitly reject driver-as-deterministic-cause, ecological suitability-as-incidence, mobility-as-transmission, surveillance-as-incidence, contamination-as-illness, food/freight-connectivity-as-outbreak, healthcare-presence-as-prevalence, unlike-disease scoring, individual risk, unsupported local downscaling, Phase 13A modification, and Phase 13C implementation. Caveat language is retained as boundary evidence rather than treated as a positive claim. {citation_lines()}

Great Black Swamp remains C — HOLD / noncanonical; the Toledo intake-coordinate discrepancy remains UNRESOLVED. Phase 6B manifest status wording mismatch and Phase 3A missing manifest status remain deferred. No release or tag is created. {citation_lines()}
""" + source_block()
    paths = []
    for name, text in (
        ("infectious_disease_dependency_sources.md", source_report),
        ("infectious_disease_dependency_assumptions.md", assumptions),
        ("infectious_disease_dependency_findings.md", findings),
        ("infectious_disease_dependency_qa.md", qa),
    ):
        path = REPORTS / name
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def load_layers():
    huc8 = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wetlands = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flowlines = gpd.read_file(GPKG, layer="hydrography_physical")
    flowlines["geometry"] = flowlines.geometry.simplify(0.002, preserve_topology=False)
    return huc8, lake, wetlands, flowlines


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'id="p[0-9a-f]+"', 'id="p13bvector"', text)
    text = re.sub(r'url\(#p[0-9a-f]+\)', "url(#p13bvector)", text)
    text = re.sub(r'\bm[0-9a-f]{6,}\b', "p13bmarker", text)
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def render_map() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc8, lake, wetlands, flowlines = load_layers()
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc8.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.38)
    flowlines.plot(ax=ax, color="#4a8798", linewidth=0.28, alpha=0.46)
    anchors = {
        "ENVIRONMENT": (-84.12, 41.98, "#667a91"),
        "VECTORS": (-83.92, 41.29, "#6b4b91"),
        "WATER": (-83.40, 41.78, "#2b7182"),
        "FOOD / FREIGHT": (-83.45, 41.48, "#b26d32"),
        "POPULATION / MOBILITY": (-83.55, 41.63, "#9a4f59"),
        "HEALTHCARE": (-83.53, 41.53, "#355f7d"),
        "SURVEILLANCE": (-83.72, 41.91, "#c8643f"),
        "GOVERNANCE": (-83.13, 42.00, "#4c8a69"),
    }
    for label, (x, y, color) in anchors.items():
        ax.scatter([x], [y], s=240, facecolors="#f1eadc", edgecolors=color, linewidth=1.8, zorder=7)
        ax.text(x, y, label, fontsize=6.2, color=color, ha="center", va="center", weight="bold", zorder=8)
    connections = [
        ("ENVIRONMENT", "VECTORS"), ("ENVIRONMENT", "WATER"), ("WATER", "SURVEILLANCE"),
        ("FOOD / FREIGHT", "SURVEILLANCE"), ("POPULATION / MOBILITY", "SURVEILLANCE"),
        ("HEALTHCARE", "SURVEILLANCE"), ("SURVEILLANCE", "GOVERNANCE"),
        ("VECTORS", "SURVEILLANCE"), ("WATER", "GOVERNANCE"),
    ]
    for source, target in connections:
        x1, y1, _ = anchors[source]
        x2, y2, _ = anchors[target]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, linewidth=1.05, color="#6e6a60", alpha=0.58, connectionstyle="arc3,rad=0.08", zorder=4))
    ax.text(-83.42, 41.77, "Western Lake Erie", fontsize=11, weight="bold", color="#235a68", ha="center")
    ax.text(-83.56, 41.42, "Maumee River / tributary context", fontsize=8.5, color="#285f71", rotation=18, ha="center")
    ax.set_xlim(-84.55, -82.55)
    ax.set_ylim(40.9, 42.15)
    ax.set_axis_off()

    side = fig.add_axes([0.67, 0.045, 0.30, 0.90])
    side.axis("off")
    side.text(0.03, 0.98, "MAP 42 — INFECTIOUS DISEASE\nTRANSMISSION DEPENDENCIES, 2026", va="top", fontsize=13.5, weight="bold", color="#17384b", linespacing=1.16)
    side.text(0.03, 0.855, "Generalized qualitative interfaces among environment, vectors, water, food/freight, population/mobility, healthcare, surveillance, and governance. Arrows are dependency interfaces, not transmission routes or disease surfaces.", va="top", fontsize=8.15, color="#3f4645", linespacing=1.28)
    side.text(0.03, 0.705, "TRANSMISSION ARCHETYPES", fontsize=9.7, weight="bold", color="#17384b")
    side.text(0.05, 0.67, "• Vector-borne: climate, hydrology, ecology, contact, surveillance\n• Waterborne/environmental: water, flooding, infrastructure, monitoring\n• Foodborne/enteric: production, processing, freight, laboratories\n• Respiratory: settlement, mobility, settings, wastewater, reporting\n• Zoonotic: animal hosts, contact, veterinary/public health\n• Healthcare/AMR: care, infrastructure, laboratory, coordination", va="top", fontsize=7.45, color="#3f4645", linespacing=1.30)
    side.text(0.03, 0.405, "EVIDENCE STATUS", fontsize=9.7, weight="bold", color="#17384b")
    side.text(0.05, 0.37, "Documented relationships are source-backed. Inferred relationships are bounded systems interpretations with source/evidence basis, scale, direction, and uncertainty retained.", va="top", fontsize=7.6, color="#3f4645", linespacing=1.30)
    side.text(0.03, 0.245, "BOUNDARIES", fontsize=9.7, weight="bold", color="#17384b")
    side.text(0.05, 0.21, "Driver ≠ deterministic cause. Vector ecology ≠ human disease. Contamination ≠ illness. Mobility ≠ transmission. Surveillance ≠ incidence. Healthcare presence ≠ disease burden. Food/freight connectivity ≠ outbreak. No cases, local downscaling, composite risk score, incidence forecast, or Phase 13C.", va="top", fontsize=7.35, color="#3f4645", linespacing=1.27)
    side.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1eadc", markeredgecolor="#667a91", markersize=7, label="environment / climate"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1eadc", markeredgecolor="#6b4b91", markersize=7, label="vector ecology"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1eadc", markeredgecolor="#2b7182", markersize=7, label="water systems"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1eadc", markeredgecolor="#b26d32", markersize=7, label="food / freight"),
        Line2D([0], [0], color="#6e6a60", lw=1.2, label="qualitative dependency"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="accepted water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="accepted wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.01), frameon=False, fontsize=6.9)
    MAPS.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(MAP_BASE.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(MAP_BASE.with_suffix(".svg"))


def metadata(paths: list[Path]) -> dict[str, dict[str, object]]:
    return {str(path.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(path), "bytes": path.stat().st_size} for path in paths}


def main() -> None:
    for directory in (NETWORKS, ANALYSIS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    source_rows = make_source_rows()
    write_ledger(source_rows)
    dependencies = dependency_rows()
    matrix = matrix_rows()
    uncertainties = uncertainty_rows()
    crosswalk = crosswalk_rows(dependencies)

    dep_path = ANALYSIS / "infectious_disease_dependency_register.csv"
    edge_path = NETWORKS / "infectious_disease_dependency_edges.csv"
    matrix_path = ANALYSIS / "infectious_disease_dependency_matrix.csv"
    crosswalk_path = ANALYSIS / "infectious_disease_evidence_crosswalk.csv"
    sources_path = ANALYSIS / "infectious_disease_dependency_sources.csv"
    uncertainty_path = ANALYSIS / "infectious_disease_dependency_uncertainties.csv"
    write_csv(dep_path, dependencies, DEPENDENCY_COLUMNS)
    edges = [{"edge_id": f"IDBE-{index:03d}", **row} for index, row in enumerate(dependencies, 1)]
    write_csv(edge_path, edges, ["edge_id"] + DEPENDENCY_COLUMNS)
    write_csv(matrix_path, matrix, MATRIX_COLUMNS)
    write_csv(crosswalk_path, crosswalk, CROSSWALK_COLUMNS)
    write_csv(sources_path, source_rows, SOURCE_COLUMNS)
    write_csv(uncertainty_path, uncertainties, UNCERTAINTY_COLUMNS)
    render_map()
    report_paths = write_reports(dependencies, matrix, crosswalk, source_rows, uncertainties)

    artifacts = [
        dep_path, edge_path, matrix_path, crosswalk_path, sources_path, uncertainty_path,
        MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg"), *report_paths, LEDGER,
        ROOT / "src/python/systems/build_infectious_disease_dependencies.py",
        ROOT / "src/python/systems/validate_infectious_disease_dependencies.py",
        ROOT / "src/R/systems/validate_infectious_disease_dependencies.R",
    ]
    assert all(path.exists() and path.stat().st_size > 0 for path in artifacts)
    phase13a_bytes = PHASE13A_FREEZE.read_bytes()
    manifest = {
        "phase": "13B",
        "baseline": "Infectious Disease Transmission Dependencies, 2026",
        "map_number": 42,
        "status": "implemented_validated_pending_sol_acceptance",
        "counts": {
            "dependency_register": len(dependencies), "dependency_edges": len(edges),
            "matrix_rows": len(matrix), "evidence_crosswalk": len(crosswalk),
            "sources": len(source_rows), "uncertainties": len(uncertainties),
        },
        "phase13a_freeze_manifest": {
            "path": "reports/phase13a_infectious_disease_freeze_manifest.json",
            "sha256": hashlib.sha256(phase13a_bytes).hexdigest(), "bytes": len(phase13a_bytes),
        },
        "protected_inputs": [
            "reports/phase13a_infectious_disease_freeze_manifest.json",
            "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
            "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
            "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
            "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
            "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
            "reports/phase11a_population_settlement_freeze_manifest.json",
            "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
            "reports/phase12a_vector_ecology_freeze_manifest.json",
            "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
            "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
            "reports/phase5a_freight_freeze_manifest.json",
            "reports/phase5b_freight_evidence_freeze_manifest.json",
            "reports/phase5c_freight_dependency_freeze_manifest.json",
            "reports/phase3a_freeze_manifest.json",
            "reports/phase3b_freeze_manifest.json",
        ],
        "artifacts": metadata(artifacts),
        "phase13a_accepted_frozen": True,
        "phase1_12_immutable": True,
        "phase13c_implemented": False,
        "composite_disease_risk_index": False,
        "individual_case_or_risk_map": False,
        "active_holds_preserved": {
            "great_black_swamp": "C — HOLD / noncanonical",
            "toledo_intake_coordinate_discrepancy": "UNRESOLVED",
        },
        "deferred_maintenance_preserved": [
            "Phase 6B manifest status wording mismatch",
            "Phase 3A missing manifest status",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"phase": "13B", "map_number": 42, **manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()
