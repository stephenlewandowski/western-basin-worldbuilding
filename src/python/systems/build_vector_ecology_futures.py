"""Build qualitative Phase 12C vector-ecology futures for 2050 and 2075.

This is a scenario layer over the accepted/frozen Phase 12A baseline and Phase
12B dependency layer. It does not forecast disease, human infection, abundance,
or precise future vector distribution.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

BASELINE_NODES = NETWORKS / "vector_ecology_nodes.csv"
BASELINE_HABITAT = ANALYSIS / "vector_habitat_associations.csv"
BASELINE_DEPS = ANALYSIS / "vector_system_dependency_register.csv"
BASELINE_UNCERTAINTY = ANALYSIS / "vector_ecology_uncertainty.csv"

ASSUMPTIONS = SCENARIOS / "vector_ecology_scenario_assumptions.csv"
VECTOR_STATES = SCENARIOS / "vector_ecology_vector_states_scenario.csv"
HABITAT_STATES = SCENARIOS / "vector_ecology_habitat_states_scenario.csv"
SURVEILLANCE_STATES = SCENARIOS / "vector_ecology_surveillance_states_scenario.csv"
DEPENDENCY_STATES = SCENARIOS / "vector_ecology_dependency_states_scenario.csv"
UNCERTAINTY_STATES = SCENARIOS / "vector_ecology_uncertainty_states_scenario.csv"
SOURCES = ANALYSIS / "vector_ecology_future_sources.csv"
COMPARISON = FIGURES / "vector_ecology_future_comparison.csv"
COMPARISON_PNG = FIGURES / "vector_ecology_future_comparison.png"
COMPARISON_SVG = FIGURES / "vector_ecology_future_comparison.svg"
MAP2050 = MAPS / "40_vector_ecology_futures_2050"
MAP2075 = MAPS / "40b_vector_ecology_futures_2075"
MANIFEST = REPORTS / "vector_ecology_future_manifest.json"
LEDGER = REPORTS / "phase12c_citation_ledger.json"
CITATION_SCRIPT = Path.home() / "AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py"
PY_VALIDATOR = ROOT / "src/python/systems/validate_vector_ecology_futures.py"
R_VALIDATOR = ROOT / "src/R/systems/validate_vector_ecology_futures.R"
REVIEW = REPORTS / "vector_ecology_future_independent_review.md"
INITIAL_REVIEW = REPORTS / "vector_ecology_future_independent_review_initial.md"

HORIZONS = (2050, 2075)
SCENARIO_IDS = tuple(f"{scenario}{year}" for scenario in "ABC" for year in HORIZONS)
SCENARIO_META = {
    "A": {
        "name": "Managed Ecological Adaptation",
        "plausibility": "moderate",
        "uncertainty": "moderate",
    },
    "B": {
        "name": "Heterogeneous Adaptive Basin",
        "plausibility": "high",
        "uncertainty": "high",
    },
    "C": {
        "name": "Warmer / More Variable Vector Landscape",
        "plausibility": "exploratory",
        "uncertainty": "high",
    },
}

SOURCE_URLS = [
    "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/animals/mosquitoes-in-ohio",
    "https://ohioline.osu.edu/factsheet/ent-89",
    "https://www.mdpi.com/2075-4450/14/1/56",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4106292",
    "https://www.in.gov/health/idepd/zoonotic-and-vectorborne-epidemiology-entomology/vector-borne-diseases/mosquito-borne-diseases/aedes-albopictus",
    "https://www.cdc.gov/mosquitoes/about",
    "https://www.cdc.gov/mosquitoes/php/toolkit/mosquito-surveillance-traps.html",
    "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html",
    "https://www.cdc.gov/ticks/data-research/facts-stats/american-dog-tick-surveillance.html",
    "https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf",
    "https://glisa.umich.edu/wp-content/uploads/2025/06/GLISA-Climate-Trends-2-Pager.pdf",
    "https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023/",
    "https://doi.org/10.7930/NCA5.2023.CH24",
    "https://www.cdc.gov/west-nile-virus/about",
    "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update",
    "https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html",
    "https://www.cdc.gov/west-nile-virus/data-maps",
    "https://www.cdc.gov/lyme/data-research/facts-stats/index.html",
    "https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf",
    "https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county",
    "https://www.cdc.gov/ticks/data-research/facts-stats",
    "https://ohid.ohio.gov/wps/wcm/connect/gov/ohio+content+english/odh/know-our-programs/zoonotic-disease-program/media/west-nile-virus-map",
]

SOURCE_ROWS = [
    ["VFS-001", "Ohio Department of Health — Mosquitoes in Ohio", SOURCE_URLS[0], "state_public_health", "species, habitat, and seasonal context", "Ohio species and seasonal context", "2026-09-08", "retrieved_from_accepted_12A_registry", "Supports established species/habitat context; not a future abundance or local distribution model."],
    ["VFS-002", "Ohio State University Ohioline — Northern House Mosquito", SOURCE_URLS[1], "university_extension", "Culex habitat, host, temperature, and overwintering context", "Ohio species ecology", "2026-09-08", "retrieved_from_accepted_12A_registry", "Supports qualitative biology only; no fitted phenology or abundance response is adopted."],
    ["VFS-003", "Insects — Invasive Aedes japonicus Mosquitoes in Wooster, Ohio", SOURCE_URLS[2], "peer_reviewed", "study-area Aedes japonicus detection and trap composition", "Wooster, Ohio study", "2026-09-08", "retrieved_from_accepted_12A_registry", "Study-specific evidence is not generalized to a Western Basin range or abundance claim."],
    ["VFS-004", "Establishment of Aedes japonicus in Michigan", SOURCE_URLS[3], "peer_reviewed", "Michigan container-habitat and surveillance context", "Saginaw County study context", "2026-09-08", "retrieved_from_accepted_12A_registry", "Study-area evidence informs plausible habitat relationships, not a current or future basin boundary."],
    ["VFS-005", "Indiana Department of Health — Aedes albopictus", SOURCE_URLS[4], "state_public_health", "Aedes container habitat and temperature-linked lifecycle context", "Indiana regional context", "2026-09-08", "retrieved_from_accepted_12A_registry", "Distribution-map and lifecycle context do not support a continuous future range or abundance surface."],
    ["VFS-006", "CDC — About Mosquitoes", SOURCE_URLS[5], "federal_public_health", "mosquito ecology and vector/pathogen distinction", "United States general biology", "2026-09-08", "retrieved_from_accepted_12A_registry", "General biology is not a Western Basin future distribution or disease forecast."],
    ["VFS-007", "CDC — Mosquito Surveillance Traps", SOURCE_URLS[6], "federal_surveillance_guidance", "trap selectivity, life-stage coverage, and effort limits", "United States surveillance methods", "2026-09-08", "retrieved_from_accepted_12A_registry", "Surveillance intensity and detection timing are not abundance."],
    ["VFS-008", "CDC — Blacklegged Tick Surveillance", SOURCE_URLS[7], "federal_surveillance", "Ixodes status definitions, seasonality, and broad habitat context", "United States county/regional context", "2026-09-08", "retrieved_from_accepted_12A_registry", "County status is not precise local distribution, abundance, or future establishment."],
    ["VFS-009", "CDC — American Dog Tick Surveillance", SOURCE_URLS[8], "federal_surveillance", "Dermacentor broad regional context", "Eastern United States", "2026-09-08", "retrieved_from_accepted_12A_registry", "Retained as context only; no new D. variabilis future range is modeled."],
    ["VFS-010", "GLISA — Summary of Climate Change in the Great Lakes Region", SOURCE_URLS[9], "regional_climate_synthesis", "mid- and late-century temperature and precipitation envelopes", "Great Lakes region", "2026-09-08", "retrieved_from_accepted_9C_registry", "Projection evidence is regional scenario context, not an observed vector distribution or local forecast."],
    ["VFS-011", "GLISA — Climate Trends", SOURCE_URLS[10], "regional_climate_synthesis", "directional warming and hot-day context", "Great Lakes region", "2026-09-08", "retrieved_from_accepted_9C_registry", "Directional climate evidence does not establish vector abundance, pathogen prevalence, or disease burden."],
    ["VFS-012", "LOCA Version 2 for North America", SOURCE_URLS[11], "downscaled_climate_method", "CMIP6 daily temperature and precipitation method context", "North America / 6 km method context", "2026-09-08", "retrieved_from_accepted_9C_registry", "Method metadata informs scenario framing; no synthetic future range or exact local value is generated."],
    ["VFS-013", "Fifth National Climate Assessment — Midwest", SOURCE_URLS[12], "federal_climate_assessment", "Midwest climate-system and adaptation context", "Midwest United States", "2026-09-08", "retrieved_from_accepted_9C_registry", "Assessment context supports scenario construction, not a vector or disease forecast."],
    ["VFS-020", "CDC — About West Nile", SOURCE_URLS[13], "federal_public_health", "bird–mosquito lifecycle and vector/pathogen context", "United States general ecology", "2026-09-08", "retrieved_from_accepted_12A_registry", "Used as ecological context only; no human infection, prevalence, or disease forecast is created."],
    ["VFS-021", "Ohio Vector-borne Disease Surveillance Update", SOURCE_URLS[14], "state_surveillance", "Ohio pooled-mosquito surveillance context", "Ohio agency/county summaries", "2026-09-08", "retrieved_from_accepted_12A_registry", "Program summaries are not comparable abundance measures or local transmission evidence."],
    ["VFS-022", "CDC — Tick Surveillance Data Sets", SOURCE_URLS[15], "federal_surveillance", "tick status definitions and no-record caveat", "United States county surveillance", "2026-09-08", "retrieved_from_accepted_12A_registry", "Status categories and no-records are not abundance, absence, or precise distribution."],
    ["VFS-023", "CDC — Data and Maps for West Nile", SOURCE_URLS[16], "federal_surveillance", "separate vector, animal, and human surveillance streams", "United States state/county reporting", "2026-09-08", "retrieved_from_accepted_12A_registry", "Positive vector pools are not human cases or local transmission proof."],
    ["VFS-024", "CDC — Lyme Disease Surveillance and Data", SOURCE_URLS[17], "federal_surveillance", "case-geography and surveillance limitation context", "United States county-of-residence context", "2026-09-08", "retrieved_from_accepted_12A_registry", "Human case geography is not a vector record, exposure location, or local transmission proof."],
    ["VFS-025", "Michigan EZID Annual Surveillance Summary", SOURCE_URLS[18], "state_surveillance", "Michigan participating-jurisdiction mosquito surveillance context", "Michigan participating jurisdictions", "2026-09-08", "retrieved_from_accepted_12A_registry", "Program totals and positive pools are not a comparable abundance index."],
    ["VFS-026", "Indiana Department of Health — First 2026 WNV Case", SOURCE_URLS[19], "state_surveillance", "Indiana mosquito and contextual human-case reporting", "Indiana state/county summary", "2026-09-08", "retrieved_from_accepted_12A_registry", "The release does not establish local transmission, abundance, or human-vector contact."],
    ["VFS-027", "CDC — Tick Data", SOURCE_URLS[20], "federal_surveillance", "tick surveillance product catalog context", "United States county dashboards", "2026-09-08", "retrieved_from_accepted_12A_registry", "Product availability does not imply uniform sampling or comparable effort."],
    ["VFS-028", "Ohio West Nile Virus Disease in Ohio Map", SOURCE_URLS[21], "state_surveillance", "human case county-of-residence context", "Ohio county of residence", "2026-09-08", "retrieved_from_accepted_12A_registry", "Case geography is not exposure location, vector abundance, or local transmission proof."],
    ["VFS-014", "Accepted Phase 1 hydrology and wetlands context", "reports/water_system_manifest.json", "repository_accepted_layer", "standing-water, drainage, wetland, and floodplain interfaces", "Western Basin watershed/wetland context", "2026-09-08", "verified_in_repository", "Reused context only; no future water footprint or vector abundance is created."],
    ["VFS-015", "Accepted Phase 6 ecology and biodiversity context", "reports/phase6a_ecology_freeze_manifest.json", "repository_accepted_layer", "wetland, riparian, terrestrial, and host-ecology context", "Western Basin ecological systems", "2026-09-08", "verified_in_repository", "Reused generalized context; Great Black Swamp remains held and noncanonical."],
    ["VFS-016", "Accepted Phase 10 governance futures context", "reports/phase10c_governance_futures_freeze_manifest.json", "repository_accepted_layer", "monitoring, coordination, and management-interface context", "Western Basin institutional interfaces", "2026-09-08", "verified_in_repository", "Scenario governance interfaces do not prove control effectiveness or complete surveillance."],
    ["VFS-017", "Accepted Phase 11 population and settlement futures context", "reports/phase11c_population_settlement_futures_freeze_manifest.json", "repository_accepted_layer", "settlement form and population-concentration interface", "Western Basin generalized county/place context", "2026-09-08", "verified_in_repository", "Population and settlement context is not human-vector contact, exposure, infection, or disease risk."],
    ["VFS-018", "Accepted Phase 7 environmental-health context", "reports/phase7a_exposure_environmental_health_freeze_manifest.json", "repository_accepted_layer", "potential pathway and monitoring boundary", "Western Basin pathway context", "2026-09-08", "verified_in_repository", "No exposure, dose, illness, or disease outcome is represented."],
    ["VFS-019", "Accepted Phase 4 observation/data context", "reports/observation_system_manifest.json", "repository_accepted_layer", "observation, uncertainty, and decision-interface context", "Western Basin information chains", "2026-09-08", "verified_in_repository", "Observation coverage is heterogeneous and is not treated as complete surveillance."],
]

ASSUMPTION_COLUMNS = [
    "assumption_id", "scenario_id", "scenario", "horizon", "domain", "assumption",
    "evidence_basis", "source_id", "uncertainty", "reality_status", "canon_status",
    "classification", "numeric_future_value_adopted", "notes",
]
VECTOR_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_node_id", "baseline_name",
    "taxon_or_system", "vector_group", "baseline_presence_context", "seasonal_suitability_state",
    "habitat_opportunity_state", "overwintering_or_activity_context", "future_range_state",
    "establishment_state", "abundance_state", "pathogen_state", "human_interface_state",
    "current_fact", "scenario_assumption", "scenario_consequence", "assumption_id",
    "source_or_basis", "plausibility", "uncertainty", "reality_status", "canon_status",
    "relationship_basis", "notes",
]
HABITAT_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_object_id", "baseline_association_id", "habitat_relationship",
    "vector_group", "current_fact", "future_suitability_state", "habitat_opportunity_state",
    "spatial_pattern", "change_type", "assumption_id", "source_or_basis", "plausibility",
    "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
SURVEILLANCE_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_object_id", "surveillance_dimension",
    "current_fact", "surveillance_capacity_state", "detection_timing_state", "method_and_effort_state",
    "management_response_interface", "abundance_inference_boundary", "assumption_id", "source_or_basis",
    "plausibility", "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
DEPENDENCY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_dependency_id", "object_a", "object_b",
    "system_a", "system_b", "relationship_type", "spatial_scale", "current_fact", "scenario_assumption",
    "scenario_consequence", "dependency_state", "assumption_id", "source_or_basis", "plausibility",
    "uncertainty", "reality_status", "canon_status", "relationship_basis", "notes",
]
UNCERTAINTY_COLUMNS = [
    "state_id", "scenario_id", "scenario", "horizon", "baseline_uncertainty_id", "category", "subject_id",
    "current_fact", "scenario_assumption", "uncertainty_state", "assumption_id", "source_or_basis",
    "reality_status", "canon_status", "relationship_basis", "notes",
]
COMPARISON_COLUMNS = [
    "scenario_id", "scenario", "horizon", "seasonal_suitability", "urban_container_opportunity",
    "standing_water_opportunity", "forest_edge_humidity", "host_ecology_interface", "surveillance_capacity",
    "detection_timing", "management_response", "spatial_heterogeneity", "range_statement",
    "abundance_statement", "pathogen_statement", "human_interface_statement", "scenario_distinctiveness",
    "uncertainty_profile", "notes",
]

VECTOR_SOURCE = {
    "VEC-001": "VFS-002", "VEC-002": "VFS-002", "VEC-003": "VFS-001", "VEC-004": "VFS-003",
    "VEC-005": "VFS-001", "VEC-006": "VFS-008",
}
HABITAT_ROWS = [
    ("HABSTATE-001", "VEC-009", "HAB-003", "urban_container_habitat", "mosquito", "VFS-005"),
    ("HABSTATE-002", "VEC-001", "HAB-001", "catch_basin_stagnant_water", "mosquito", "VFS-002"),
    ("HABSTATE-003", "VEC-008", "HAB-011", "wetland_standing_water", "mosquito/tick interface", "VFS-014"),
    ("HABSTATE-004", "VEC-011", "HAB-011", "ditch_floodplain_water", "mosquito", "VFS-014"),
    ("HABSTATE-005", "VEC-010", "HAB-007", "forest_edge_humidity", "tick/mosquito", "VFS-008"),
    ("HABSTATE-006", "VEC-012", "HAB-012", "host_ecology", "mosquito/tick", "VFS-008"),
    ("HABSTATE-007", "VEC-013", "HAB-015", "temperature_seasonality", "mosquito/tick", "VFS-002"),
    ("HABSTATE-008", "VEC-014", "HAB-011", "precipitation_hydrology", "mosquito", "VFS-014"),
]
SURVEILLANCE_ROWS = [
    ("SURVSTATE-001", "VEC-015", "mosquito surveillance program"),
    ("SURVSTATE-002", "VEC-016", "regional/state participating programs"),
    ("SURVSTATE-003", "VEC-017", "state and local mosquito activity reporting"),
    ("SURVSTATE-004", "VEC-018", "federal vector and tick surveillance interface"),
    ("SURVSTATE-005", "VDE-017", "detection-to-decision interface"),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    assert all(len(row) == len(columns) for row in rows), path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_ledger() -> None:
    if not CITATION_SCRIPT.exists():
        raise FileNotFoundError(CITATION_SCRIPT)
    subprocess.run([sys.executable, str(CITATION_SCRIPT), "--ledger", str(LEDGER), "reset"], check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(CITATION_SCRIPT), "--ledger", str(LEDGER), "add", *SOURCE_URLS], check=True, capture_output=True, text=True)


def horizon_phrase(year: int, scenario: str) -> str:
    if year == 2050:
        modifier = {
            "A": "priority maintenance and coordinated review are emerging and remain selective",
            "B": "local habitat and program differences are emerging and remain structurally uneven",
            "C": "climate variability begins to expose selected habitat and monitoring seams",
        }[scenario]
        return f"This is the {scenario} scenario's intermediate 2050 ecological trajectory: {modifier}; it is not an observed distribution or forecast."
    modifier = {
        "A": "selected maintenance and recurring review routines are institutionalized while residual habitat remains",
        "B": "local habitat and program differences are durable across overlapping adaptive networks",
        "C": "warmth, variability, and selected response lags are entrenched without universal failure",
    }[scenario]
    return f"By 2075, this is the {scenario} scenario's matured or diverged ecological state: {modifier}; it is not an observed distribution or forecast."


def assumption_text(scenario: str, year: int, domain: str) -> tuple[str, str, str]:
    texts = {
        "A": {
            "climate_hydrology": "Temperature and precipitation variability remain physical drivers, while adaptive water and habitat management reduces some persistent standing-water opportunities without eliminating seasonal or episodic habitat.",
            "urban_containers": "Coordinated container, catch-basin, and developed-edge maintenance reduces some unmanaged Aedes and Culex habitat opportunities in selected urban and suburban settings.",
            "forest_edge_host": "Forest-edge stewardship and ecological monitoring improve attention to humidity, host, and edge conditions without controlling tick or mosquito presence.",
            "surveillance": "Vector surveillance, method documentation, and cross-program reporting become more coordinated, supporting earlier detection in selected settings without making surveillance complete or quantitative abundance.",
            "settlement_interface": "Settlement and infrastructure planning uses generalized vector-habitat interfaces to target maintenance and monitoring without assigning residents to contact, exposure, or infection.",
            "governance_response": "Public-health, ecological, and local infrastructure actors use more connected monitoring-to-management routines while retaining distinct authority, program limits, and uncertainty.",
        },
        "B": {
            "climate_hydrology": "Climate and hydrologic conditions become more permissive for some vectors in some settings, but urban, wetland, agricultural, forest-edge, and suburban responses remain different and are not averaged.",
            "urban_containers": "Container opportunities vary with settlement form, maintenance, shade, precipitation, and local practices; some developed areas constrain opportunities while others remain permissive.",
            "forest_edge_host": "Forest and edge conditions form a patchwork of moisture, vegetation, host, and access contexts, so tick and woodland-mosquito opportunities diverge locally.",
            "surveillance": "Surveillance remains functional but uneven across programs, habitats, methods, and jurisdictions; detections can expand in some places without establishing a comparable abundance measure.",
            "settlement_interface": "Population concentration, workplace form, and land-cover interfaces differ across the basin; these differences guide potential monitoring interfaces rather than human-contact estimates.",
            "governance_response": "Management and surveillance operate through overlapping local and regional arrangements, producing functional adaptation in some places and persistent negotiation or coverage gaps in others.",
        },
        "C": {
            "climate_hydrology": "Warmer conditions and stronger drought/heavy-rain contrasts create episodic habitat opportunities and interruptions; selected seasonal windows may lengthen while local water availability remains variable.",
            "urban_containers": "Developed edges, containers, gutters, and stagnant infrastructure provide more opportunities in selected locations where maintenance struggles to keep pace, without implying uniform habitat or abundance.",
            "forest_edge_host": "Warmth, humidity variability, vegetation change, and host relationships alter forest-edge conditions in uncertain and location-specific ways; suitable microhabitat remains possible but unmeasured.",
            "surveillance": "Selected locations experience surveillance or management lag relative to ecological change, while capable programs continue elsewhere; detection timing and effort therefore remain uneven.",
            "settlement_interface": "Settlement concentration and infrastructure conditions create selected vector-environment interfaces, but no person-level contact, exposure, infection, or disease inference is made.",
            "governance_response": "Monitoring and management coordination struggles to keep pace at selected seams, increasing uncertainty about detection and response without assuming institutional collapse or disease outcomes.",
        },
    }
    return texts[scenario][domain], f"accepted vector, climate, hydrology, population, and governance context plus explicit scenario construction; {horizon_phrase(year, scenario)}", {
        "climate_hydrology": "VFS-010", "urban_containers": "VFS-005", "forest_edge_host": "VFS-008", "surveillance": "VFS-007", "settlement_interface": "VFS-017", "governance_response": "VFS-016",
    }[domain]


def build_assumptions() -> list[list[str]]:
    rows: list[list[str]] = []
    domains = ["climate_hydrology", "urban_containers", "forest_edge_host", "surveillance", "settlement_interface", "governance_response"]
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for index, domain in enumerate(domains, 1):
                text, basis, source_id = assumption_text(scenario, year, domain)
                rows.append([
                    f"VEFA-{sid}-{index:02d}", sid, SCENARIO_META[scenario]["name"], str(year), domain, f"{text} {horizon_phrase(year, scenario)}",
                    basis, source_id, SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario",
                    "SCENARIO ASSUMPTION", "false", "Qualitative assumption only; no vector count, abundance, prevalence, contact, infection, disease, probability, or exact range is assigned.",
                ])
    return rows


def vector_future(scenario: str, year: int, node_id: str) -> tuple[str, str, str, str, str]:
    if node_id in {"VEC-001", "VEC-002"}:
        if scenario == "A":
            if year == 2050:
                return ("seasonal development opportunity is moderated in managed priority settings", "persistent stagnant-water opportunities are reduced in selected catch-basin, ditch, and container interfaces", "warm-season activity and overwintering remain possible; episodic water conditions are retained", "future suitability/opportunity only; no future Culex range is observed or mapped")
            return ("mature adaptive maintenance limits persistent stagnant-water opportunity in selected systems", "routine maintenance and drainage adaptation constrain some opportunities while episodic heavy-rain retention remains possible", "seasonal activity and diapause context remain possible under a warmer, managed setting", "future suitability/opportunity only; no future Culex range is observed or mapped")
        if scenario == "B":
            if year == 2050:
                return ("seasonal opportunity varies among urban, ditch, floodplain, and rural interfaces", "a mosaic of constrained, permissive, and episodic standing-water settings emerges", "activity and overwintering context differ by local temperature and water conditions", "future suitability/opportunity varies locally; no basin-wide Culex range is observed or mapped")
            return ("a persistent habitat mosaic remains the defining state, with locally divergent seasonal windows", "some interfaces remain constrained while others retain recurrent or episodic standing-water opportunity", "local activity and overwintering conditions remain heterogeneous and uncertain", "future suitability/opportunity varies locally; no basin-wide Culex range is observed or mapped")
        if year == 2050:
            return ("warmer conditions may lengthen seasonal opportunity in selected settings, while drought interrupts habitat elsewhere", "episodic heavy rain, stagnant infrastructure, and dry intervals create patchy water opportunity", "seasonality becomes more variable; no universal extension is assumed", "future suitability/opportunity may be more permissive in selected settings; no future Culex range is observed or mapped")
        return ("a longer and less predictable warm-season opportunity is plausible in selected settings amid strong dry/wet pulses", "stagnant infrastructure and episodic retention coexist with drought-limited habitat", "seasonality and overwintering remain location-specific and uncertain", "future suitability/opportunity may be more permissive in selected settings; no future Culex range is observed or mapped")
    if node_id in {"VEC-003", "VEC-004", "VEC-005"}:
        if scenario == "A":
            if year == 2050:
                return ("warm-season container suitability is moderated where container and gutter management is maintained", "selected urban, suburban, woodland, and artificial-container opportunities are reduced but not eliminated", "winter constraints and local shade/moisture remain relevant; no overwintering transition is assumed", "future suitability/opportunity only; no future Aedes range is observed or mapped")
            return ("managed container networks constrain persistent opportunities in selected developed and woodland-edge settings", "routine container, tire, gutter, and treehole attention reduces some habitat opportunities while residual habitat remains", "winter constraints remain a local uncertainty even as warm-season conditions persist", "future suitability/opportunity only; no future Aedes range is observed or mapped")
        if scenario == "B":
            if year == 2050:
                return ("container suitability differs sharply among urban, suburban, woodland, and maintained settings", "some settlement interfaces remain permissive while others constrain containers through local maintenance", "temperature, shade, and overwintering constraints vary by micro-setting", "future suitability/opportunity varies locally; no future Aedes range is observed or mapped")
            return ("a durable mosaic of container-constrained and container-permissive settings remains", "local settlement form, maintenance, shade, and precipitation continue to separate habitat opportunity", "overwintering constraints remain heterogeneous and unresolved rather than disappearing basin-wide", "future suitability/opportunity varies locally; no future Aedes range is observed or mapped")
        if year == 2050:
            return ("warmer seasonal conditions may increase opportunity in selected container settings", "urban and suburban containers, gutters, tires, and woodland-edge receptacles create episodic opportunities where maintenance lags", "winter constraints may ease in some warm urban settings but remain uncertain and local", "future suitability/opportunity may be more permissive in selected settings; no future Aedes range is observed or mapped")
        return ("longer seasonal opportunity is plausible in selected developed and woodland-edge settings, with strong year-to-year variability", "container habitat opportunities become more consequential in selected locations under variable precipitation and maintenance lag", "overwintering constraints remain uncertain; suitability does not guarantee establishment", "future suitability/opportunity may be more permissive in selected settings; no future Aedes range is observed or mapped")
    if scenario == "A":
        if year == 2050:
            return ("forest-edge seasonal activity is monitored and managed in selected ecological interfaces", "targeted edge stewardship and host-habitat attention reduce some unmanaged opportunity without eliminating tick habitat", "temperature, humidity, host ecology, and above-freezing activity remain possible", "future suitability/opportunity only; no future Ixodes range is observed or mapped")
        return ("mature edge stewardship preserves selected forest and humid refugia interfaces while leaving ecological uncertainty", "maintenance and habitat connectivity choices constrain some unmanaged edge conditions", "seasonal activity remains possible under warmer conditions; host relationships are not projected", "future suitability/opportunity only; no future Ixodes range is observed or mapped")
    if scenario == "B":
        if year == 2050:
            return ("forest-edge suitability is strongly differentiated by moisture, vegetation, host, and access context", "some forest and edge patches retain opportunity while others are constrained or dry", "questing conditions vary by local humidity, temperature, and host ecology", "future suitability/opportunity varies locally; no future Ixodes range is observed or mapped")
        return ("a persistent patchwork of humid, dry, connected, and fragmented edge settings remains", "local forest/edge differences, not a basin average, organize potential opportunity", "seasonal activity and host relationships remain spatially heterogeneous and uncertain", "future suitability/opportunity varies locally; no future Ixodes range is observed or mapped")
    if year == 2050:
        return ("warmer seasonal conditions may lengthen activity opportunity in selected forest/edge settings", "some humid edge and host interfaces remain permissive while drought reduces other microhabitats", "temperature, humidity, and host ecology may shift in different directions", "future suitability/opportunity may be more permissive in selected settings; no future Ixodes range is observed or mapped")
    return ("longer or less predictable seasonal activity is plausible in selected forest/edge settings", "drought and heavy-rain contrasts create shifting humid refugia and fragmented opportunities", "host ecology and humidity remain major unresolved controls", "future suitability/opportunity may be more permissive in selected settings; no future Ixodes range is observed or mapped")


def build_vector_states(assumption_rows: list[list[str]], nodes: list[dict[str, str]]) -> list[list[str]]:
    assumption_lookup = {(r[1], r[4]): r for r in assumption_rows}
    focal = [node for node in nodes if node["node_id"] in VECTOR_SOURCE]
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for node in focal:
                profile = "climate_hydrology" if node["node_id"] in {"VEC-001", "VEC-002"} else "urban_containers" if node["node_id"] in {"VEC-003", "VEC-004", "VEC-005"} else "forest_edge_host"
                aid = assumption_lookup[(sid, profile)][0]
                suitability, habitat, activity, range_state = vector_future(scenario, year, node["node_id"])
                source_id = VECTOR_SOURCE[node["node_id"]]
                rows.append([
                    f"VECSTATE-{sid}-{node['node_id']}", sid, SCENARIO_META[scenario]["name"], str(year), node["node_id"], node["name"],
                    node["taxon_or_system"], node["vector_group"], node["notes"], suitability, habitat, activity, range_state,
                    "not projected; future suitability is not guaranteed establishment",
                    "not estimated; surveillance effort, suitability, and habitat opportunity do not provide abundance",
                    "not projected; pathogen-in-vector detection and prevalence remain outside this scenario layer",
                    "not modeled; habitat, settlement, and host interfaces do not establish human-vector contact",
                    f"CURRENT FACT (2026 baseline): {node['notes']}",
                    f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, profile)][5]}",
                    f"SCENARIO CONSEQUENCE: {horizon_phrase(year, scenario)} Ecological opportunity may change qualitatively for this vector context, but presence, abundance, establishment, pathogen prevalence, contact, infection, and clinical disease remain separate and unprojected.",
                    aid, source_id, SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Vector ecology future state; not an observed future record, continuous range, abundance estimate, pathogen forecast, human-risk estimate, or disease forecast.",
                ])
    return rows


def habitat_future(scenario: str, year: int, relationship: str) -> tuple[str, str, str, str]:
    if scenario == "A":
        if relationship in {"urban_container_habitat", "catch_basin_stagnant_water", "ditch_floodplain_water"}:
            if year == 2050:
                return ("potential opportunity is reduced in selected maintained interfaces", "management constrains persistent opportunity while episodic habitat remains possible", "selected targeted maintenance and monitoring", "managed_opportunity_reduced")
            return ("potential opportunity is constrained by routine maintenance in selected priority interfaces", "recurring drainage and container maintenance limits persistent opportunity while episodic habitat remains possible", "routine selected maintenance and adaptive review", "managed_opportunity_routinized")
        if relationship == "forest_edge_humidity":
            if year == 2050:
                return ("potential humid-edge opportunity is managed selectively", "stewardship changes local edge conditions without eliminating habitat", "selected managed forest/edge interfaces", "edge_stewardship_increased")
            return ("selected humid-edge opportunity is incorporated into routine stewardship", "mature edge review constrains some unmanaged conditions while ecological uncertainty remains", "routine forest/edge stewardship interfaces", "edge_stewardship_routinized")
        if year == 2050:
            return ("environmental opportunity is tracked through emerging adaptive monitoring", "conditions remain variable and are not converted to a habitat surface", "coordinated but generalized basin interfaces", "adaptive_monitoring_strengthened")
        return ("environmental opportunity is tracked through recurring adaptive review", "longer-term monitoring routines document variability without creating a habitat surface", "institutionalized but generalized basin interfaces", "adaptive_review_routinized")
    if scenario == "B":
        if year == 2050:
            return ("potential opportunity is habitat-specific and locally divergent", "constrained, permissive, and episodic settings coexist", "urban, wetland, agricultural, forest-edge, and suburban mosaic", "local_mosaic_divergence")
        return ("potential opportunity remains a durable local mosaic", "land-cover, maintenance, moisture, and settlement differences persist by setting", "persistent heterogeneous basin mosaic", "heterogeneity_entrenched")
    if year == 2050:
        return ("potential opportunity may increase episodically in selected settings while other settings dry or remain constrained", "drought/heavy-rain contrasts and infrastructure create patchy conditions", "selected stressed interfaces with capable refugia elsewhere", "episodic_opportunity_and_interruptions")
    return ("potential opportunity is longer or more variable in selected settings but remains unmeasured", "warm-season, dry/wet, and infrastructure conditions diverge strongly", "patchy selected opportunities and interruptions", "warmer_variable_patchiness")


def build_habitat_states(assumption_rows: list[list[str]], habitat: list[dict[str, str]]) -> list[list[str]]:
    assumption_lookup = {(r[1], r[4]): r for r in assumption_rows}
    habitat_lookup = {row["association_id"]: row for row in habitat}
    rows: list[list[str]] = []
    domains = {"urban_container_habitat": "urban_containers", "catch_basin_stagnant_water": "climate_hydrology", "wetland_standing_water": "climate_hydrology", "ditch_floodplain_water": "climate_hydrology", "forest_edge_humidity": "forest_edge_host", "host_ecology": "forest_edge_host", "temperature_seasonality": "climate_hydrology", "precipitation_hydrology": "climate_hydrology"}
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for index, (prefix, baseline_id, association_id, relationship, vector_group, source_id) in enumerate(HABITAT_ROWS, 1):
                aid = assumption_lookup[(sid, domains[relationship])][0]
                future, opportunity, spatial, change = habitat_future(scenario, year, relationship)
                base = habitat_lookup[association_id]
                current = base.get("relationship_description", f"Accepted Phase 12A generalized {relationship} context")
                rows.append([
                    f"{prefix}-{sid}", sid, SCENARIO_META[scenario]["name"], str(year), baseline_id, association_id, relationship, vector_group,
                    f"CURRENT FACT (2026 baseline): {current}",
                    f"SCENARIO SUITABILITY: {future}; this is potential opportunity, not observed future suitability.", opportunity, spatial, change,
                    aid, source_id, SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Habitat relationship is generalized; no precise polygon, vector count, abundance estimate, establishment claim, or human-risk inference is made.",
                ])
    return rows


def surveillance_profile(scenario: str, year: int, dimension: str) -> tuple[str, str, str, str]:
    if scenario == "A":
        if year == 2050:
            return ("selected programs coordinate methods, effort documentation, and reporting", "earlier detection is plausible in priority interfaces", "method and effort remain separate across programs", "detection can feed targeted management without proving control")
        return ("routine cross-program protocols support sustained detection and management in selected interfaces", "earlier detection and recurring review are treated as mature scenario states", "methods, denominators, and coverage remain explicitly non-comparable", "management response is more connected but does not eliminate vectors or uncertainty")
    if scenario == "B":
        if year == 2050:
            return ("functional but uneven participation and capacity by jurisdiction and habitat", "detection timing varies by program, method, and local coverage", "heterogeneous methods and effort remain structural", "local detection can inform local response; monitoring is not control")
        return ("durable but nonuniform surveillance networks operate through habitat-specific arrangements", "some locations detect earlier while others retain reporting and coverage gaps", "multiple methods and denominators remain non-comparable", "response is distributed and functional in places, not basin-wide or complete")
    if year == 2050:
        return ("selected programs struggle to keep pace with ecological change while others remain capable", "detection may lag in selected locations and seasons", "effort and method gaps become more consequential but remain unknown", "management response is delayed or uneven in selected settings")
    return ("surveillance and management capacity remain patchy relative to a warmer, more variable landscape", "detection lag persists in selected locations despite capable programs elsewhere", "coverage, method, and effort remain heterogeneous and cannot infer abundance", "selected response interfaces struggle to keep pace; no collapse or disease outcome is assumed")


def build_surveillance_states(assumption_rows: list[list[str]], nodes: list[dict[str, str]], dependencies: list[dict[str, str]]) -> list[list[str]]:
    assumption_lookup = {(r[1], r[4]): r for r in assumption_rows}
    node_lookup = {row["node_id"]: row for row in nodes}
    dep_lookup = {row["dependency_id"]: row for row in dependencies}
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for prefix, baseline_id, dimension in SURVEILLANCE_ROWS:
                base = node_lookup.get(baseline_id, dep_lookup.get(baseline_id, {}))
                domain = "surveillance"
                aid = assumption_lookup[(sid, domain)][0]
                capacity, timing, methods, response = surveillance_profile(scenario, year, dimension)
                current = base.get("notes", "Accepted Phase 12B detection-to-decision interface")
                source_id = "VFS-016" if dimension == "detection-to-decision interface" else "VFS-007"
                rows.append([
                    f"{prefix}-{sid}", sid, SCENARIO_META[scenario]["name"], str(year), baseline_id, dimension,
                    f"CURRENT FACT (2026 baseline): {current}", capacity, timing, methods, response,
                    "Surveillance intensity, effort, coverage, and detection timing are not abundance and do not establish presence, establishment, or pathogen prevalence.",
                    aid, source_id, SCENARIO_META[scenario]["plausibility"], SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Surveillance future state is a qualitative detection/decision scenario, not an abundance index, control-effectiveness claim, human-risk model, or disease forecast.",
                ])
    return rows


def dependency_state(scenario: str, year: int, relationship_type: str) -> tuple[str, str]:
    if scenario == "A":
        state = "selected_interface_strengthened" if year == 2050 else "selected_interface_routinized"
        consequence = "monitoring, habitat management, and decision handoffs are more connected in selected systems; the underlying evidence limits remain"
    elif scenario == "B":
        state = "habitat_specific_networked" if year == 2050 else "durable_local_networks_with_friction"
        consequence = "the dependency is handled differently by habitat and institution, preserving local adaptation alongside uneven coverage and negotiation friction"
    else:
        state = "selected_interface_strained" if year == 2050 else "patchy_interface_strain_entrenched"
        consequence = "the dependency becomes harder to coordinate at selected seams while capable local programs or habitats can persist"
    return state, f"SCENARIO CONSEQUENCE: {horizon_phrase(year, scenario)} {consequence}; no abundance, contact, infection, disease, or probability is inferred."


def source_map(source_id: str) -> str:
    mapping = {
        "v12_ohio_mosquitoes": "VFS-001", "v12_osu_culex": "VFS-002", "v12_ohio_ae_japonicus": "VFS-003", "v12_mi_ae_japonicus": "VFS-004",
        "v12_in_ae_albopictus": "VFS-005", "v12_cdc_mosquito_biology": "VFS-006", "v12_cdc_mosquito_traps": "VFS-007", "v12_cdc_ticks_live": "VFS-008",
        "v12_cdc_ixodes": "VFS-008", "v12_cdc_dvariabilis": "VFS-009", "phase9_climate_context": "VFS-010", "phase1_hydrology_context": "VFS-014",
        "phase6_ecology_context": "VFS-015", "phase7_health_context": "VFS-018", "phase10_governance_context": "VFS-016", "phase11_population_context": "VFS-017",
        "phase4_data_context": "VFS-019", "v12_cdc_wnv_about": "VFS-020", "v12_ohio_vector_update": "VFS-021",
        "v12_cdc_tick_sets": "VFS-022", "v12_cdc_wnv_data": "VFS-023", "v12_cdc_lyme": "VFS-024", "v12_mi_annual_2023": "VFS-025",
        "v12_in_wnv_2026": "VFS-026", "v12_cdc_tick_data": "VFS-027", "v12_ohio_wnv_map": "VFS-028",
    }
    if source_id not in mapping:
        raise KeyError(f"No Phase 12C source mapping for accepted source ID {source_id}")
    return mapping[source_id]


def build_dependency_states(assumption_rows: list[list[str]], dependencies: list[dict[str, str]]) -> list[list[str]]:
    assumption_lookup = {(r[1], r[4]): r for r in assumption_rows}
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for index, dep in enumerate(dependencies, 1):
                domain = "governance_response" if dep["system_a"] in {"surveillance", "governance", "information"} or dep["system_b"] in {"surveillance", "governance", "information"} else "climate_hydrology" if dep["system_a"] in {"climate", "hydrology"} or dep["system_b"] in {"climate", "hydrology"} else "settlement_interface" if dep["system_a"] in {"population_settlement", "population_mobility", "settlement"} or dep["system_b"] in {"population_settlement", "population_mobility", "settlement"} else "forest_edge_host"
                aid = assumption_lookup[(sid, domain)][0]
                state, consequence = dependency_state(scenario, year, dep["relationship_type"])
                source_id = source_map(dep["source_id"])
                current = f"CURRENT FACT (2026 baseline): {dep['object_a']} to {dep['object_b']} is recorded as a {dep['relationship_type']} interface at {dep['spatial_scale']}; evidence class is {dep['documented_or_inferred']}."
                rows.append([
                    f"VECDEPSTATE-{sid}-{index:03d}", sid, SCENARIO_META[scenario]["name"], str(year), dep["dependency_id"], dep["object_a"], dep["object_b"],
                    dep["system_a"], dep["system_b"], dep["relationship_type"], dep["spatial_scale"], current,
                    f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, domain)][5]}", consequence, state, aid, source_id,
                    SCENARIO_META[scenario]["plausibility"], "high" if dep["documented_or_inferred"] == "inferred" else SCENARIO_META[scenario]["uncertainty"], "fictional", "scenario", "scenario_assumption",
                    "Dependency future state preserves documented-versus-inferred and scale limits; no dependency becomes a risk score, control proof, contact estimate, or disease forecast.",
                ])
    return rows


def build_uncertainty_states(assumption_rows: list[list[str]], uncertainties: list[dict[str, str]]) -> list[list[str]]:
    assumption_lookup = {(r[1], r[4]): r for r in assumption_rows}
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            for index, item in enumerate(uncertainties, 1):
                domain = "forest_edge_host" if item["category"] in {"study_generalization", "county_scale", "held_geometry"} else "surveillance" if "effort" in item["category"] or "coverage" in item["category"] or "state" in item["category"] else "climate_hydrology"
                aid = assumption_lookup[(sid, domain)][0]
                if item["uncertainty_id"] == "VUNC-010":
                    future = "Great Black Swamp remains C — HOLD / noncanonical; no future vector habitat polygon is derived from the held geometry."
                elif scenario == "A":
                    future = "uncertainty remains explicit and becomes a candidate for coordinated monitoring or review; it is not resolved by scenario construction"
                elif scenario == "B":
                    future = "uncertainty remains spatially and programmatically heterogeneous; local differences are preserved rather than averaged"
                else:
                    future = "uncertainty may become more consequential under variability and uneven monitoring, but unknown is not converted into absence, risk, or failure"
                horizon_detail = {
                    "A": "selected review priorities are emerging" if year == 2050 else "recurring review routines are mature",
                    "B": "local differences are emerging" if year == 2050 else "local differences are durable",
                    "C": "variability is beginning to expose selected seams" if year == 2050 else "variability and selected response lag are entrenched",
                }[scenario]
                future = f"{horizon_detail}; {future}"
                rows.append([
                    f"VECUNCSTATE-{sid}-{index:03d}", sid, SCENARIO_META[scenario]["name"], str(year), item["uncertainty_id"], item["category"], item["subject_id"],
                    f"CURRENT FACT (2026 baseline): {item['statement']}", f"SCENARIO ASSUMPTION: {assumption_lookup[(sid, domain)][5]}",
                    f"{horizon_phrase(year, scenario)} {future}", aid, source_map(item["source_id"]), "fictional", "scenario", "scenario_assumption",
                    "Uncertainty state preserves source, scale, method, and hold limitations; no probability, abundance, disease, human-risk, or future range claim is created.",
                ])
    return rows


def comparison_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for scenario in "ABC":
        for year in HORIZONS:
            sid = f"{scenario}{year}"
            if scenario == "A":
                values = [
                    "managed seasonal opportunity", "reduced in selected maintained settings", "reduced persistent opportunity with episodic residuals", "selected stewardship of humid edges", "host context monitored, not projected", "coordinated selected programs", "earlier detection in priority interfaces", "more connected monitoring-to-management", "heterogeneity remains but is managed selectively", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "management-first adaptation without eliminating vectors", "moderate and explicit",
                ] if year == 2050 else [
                    "mature managed seasonal opportunity", "routine maintenance constrains selected settings", "persistent opportunity constrained in selected systems", "mature selected edge stewardship", "host context remains an uncertainty", "routine selected cross-program protocols", "earlier detection and recurring review in selected interfaces", "management and monitoring handoffs are more connected", "heterogeneity remains and is selectively managed", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "mature adaptive management without vector elimination", "moderate, with residual ecological uncertainty",
                ]
            elif scenario == "B":
                values = [
                    "habitat-specific permissiveness", "varies by settlement and maintenance", "constrained, permissive, and episodic mosaic", "moisture and edge differences dominate", "host context differs locally", "functional but uneven programs", "timing varies by program and habitat", "local response through overlapping arrangements", "heterogeneity is the organizing mechanism", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "heterogeneous mosaic with networked local adaptation, not a midpoint", "high and spatially explicit",
                ] if year == 2050 else [
                    "persistent local divergence", "durable local differences", "durable heterogeneous mosaic", "persistent humid/dry edge patchwork", "host context remains locally unresolved", "durable but nonuniform networks", "some early and some delayed detection", "distributed response with negotiation friction", "heterogeneity remains structurally durable", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "mature heterogeneous adaptation, not a midpoint", "high, with persistent local unknowns",
                ]
            else:
                values = [
                    "selected longer windows amid variability", "selected container opportunity where maintenance lags", "episodic opportunity and interruption", "variable humidity and edge conditions", "host relationships change uncertainly", "selected surveillance lag", "delayed in selected locations", "uneven response at selected seams", "patchy stressed interfaces with capable refugia elsewhere", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "warmth/variability and management lag, not epidemic disease", "high and exploratory",
                ] if year == 2050 else [
                    "longer or less predictable selected windows", "more consequential selected container opportunity", "strong dry/wet and infrastructure patchiness", "shifting humid refugia and fragmented edges", "host and humidity controls remain unresolved", "patchy capacity relative to change", "persistent selected detection lag", "management struggles at selected seams", "warmer-variable patchiness is entrenched without universal failure", "no observed or mapped future range; suitability/opportunity only", "not estimated; surveillance is not abundance", "not projected; ecology is not pathogen prevalence", "not modeled; potential interface is not contact/exposure/infection", "warmer variability and response lag without disease forecast", "high, exploratory, and unresolved",
                ]
            rows.append([sid, SCENARIO_META[scenario]["name"], str(year), *values, "Qualitative comparison only; dimensions are not aggregated, ranked, scored, or converted into disease or human-risk estimates."])
    return rows


def render_map(year: int, path: Path) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "phase12c-vector-ecology-futures"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    left = fig.add_axes([0.04, 0.16, 0.38, 0.72], facecolor="#e9e1ce")
    left.set_xlim(0, 1); left.set_ylim(0, 1); left.axis("off")
    left.text(0.03, 0.96, "GENERALIZED ECOLOGICAL INTERFACES", fontsize=11, weight="bold", color="#17384b", va="top")
    left.text(0.03, 0.91, "Schematic system context; no future range polygon or collection location is shown.", fontsize=7.2, color="#3f4645", va="top")
    boxes = [
        (0.08, 0.70, 0.36, 0.12, "urban / suburban containers", "Aedes + Culex\ncontainers, gutters, catch basins"),
        (0.56, 0.70, 0.36, 0.12, "wetland / ditch / floodplain", "standing water\nepisodic and seasonal opportunity"),
        (0.08, 0.43, 0.36, 0.12, "forest / edge / humidity", "Ixodes + woodland Aedes\nhost and edge context"),
        (0.56, 0.43, 0.36, 0.12, "temperature / precipitation", "seasonality\ndrought and heavy-rain contrasts"),
        (0.29, 0.16, 0.42, 0.12, "surveillance / management interface", "detection, effort, method, response\nnot abundance or control proof"),
    ]
    for x, y, w, h, title, text in boxes:
        left.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012", facecolor="#f8f4e9", edgecolor="#5a7e82", linewidth=1.2, transform=left.transAxes))
        left.text(x + 0.02, y + h - 0.025, title, transform=left.transAxes, fontsize=8, weight="bold", color="#17384b", va="top")
        left.text(x + 0.02, y + h - 0.060, text, transform=left.transAxes, fontsize=6.7, color="#3f4645", va="top", linespacing=1.35)
    for start, end in [((0.44, 0.76), (0.56, 0.76)), ((0.26, 0.70), (0.26, 0.55)), ((0.74, 0.70), (0.74, 0.55)), ((0.44, 0.49), (0.56, 0.49)), ((0.50, 0.43), (0.50, 0.28))]:
        left.add_patch(FancyArrowPatch(start, end, transform=left.transAxes, arrowstyle="-|>", mutation_scale=10, color="#8a6f4b", linewidth=1.0, alpha=0.75))
    left.text(0.03, 0.05, "Presence ≠ abundance ≠ pathogen prevalence ≠ contact ≠ infection ≠ disease", fontsize=7.1, color="#7a423e", weight="bold")

    right = fig.add_axes([0.46, 0.11, 0.50, 0.78])
    right.axis("off")
    map_id = "40" if year == 2050 else "40b"
    right.text(0.0, 1.02, f"MAP {map_id} — VECTOR ECOLOGY FUTURES, {year}", fontsize=13.5, weight="bold", color="#17384b", va="top")
    right.text(0.0, 0.965, "Three qualitative alternatives over the accepted 2026 vector ecology baseline and 2026 dependency layer. Suitability is not observed distribution or guaranteed establishment.", fontsize=7.1, color="#3f4645", va="top", linespacing=1.3)
    colors = {"A": "#4f927b", "B": "#c08a42", "C": "#a8524d"}
    names = {s: SCENARIO_META[s]["name"] for s in "ABC"}
    bullets = {
        "A": ["Culex: managed standing-water opportunity emerging", "Aedes: selected container maintenance", "Ixodes: targeted forest/edge stewardship", "Earlier detection supports priority response"],
        "B": ["Culex: emerging urban/wetland/ditch mosaic", "Aedes: settlement and maintenance differences", "Ixodes: early moisture/edge divergence", "Functional but uneven surveillance"],
        "C": ["Culex: episodic water + selected longer windows", "Aedes: selected container opportunities", "Ixodes: variable humid-edge activity context", "Management/surveillance lags in selected locations"],
    } if year == 2050 else {
        "A": ["Culex: routine management constrains persistent water", "Aedes: mature container maintenance", "Ixodes: routine forest/edge stewardship", "Recurring review supports selected response"],
        "B": ["Culex: durable urban/wetland/ditch mosaic", "Aedes: persistent settlement differences", "Ixodes: durable humid/dry edge patchwork", "Durable but nonuniform surveillance"],
        "C": ["Culex: dry/wet pulses + less predictable windows", "Aedes: consequential selected containers", "Ixodes: shifting humid refugia", "Response lag entrenched at selected seams"],
    }
    y_positions = [0.68, 0.41, 0.14]
    for scenario, y in zip("ABC", y_positions):
        color = colors[scenario]
        right.add_patch(Rectangle((0.0, y), 0.98, 0.22, facecolor=color, alpha=0.13, edgecolor=color, linewidth=1.4, transform=right.transAxes))
        right.text(0.025, y + 0.185, f"{scenario} — {names[scenario]}", transform=right.transAxes, fontsize=9.4, weight="bold", color=color, va="top")
        right.text(0.95, y + 0.185, "2050 intermediate" if year == 2050 else "2075 matured / diverged", transform=right.transAxes, fontsize=6.4, color="#3f4645", ha="right", va="top")
        right.text(0.04, y + 0.135, "\n".join("• " + item for item in bullets[scenario]), transform=right.transAxes, fontsize=7.1, color="#3f4645", va="top", linespacing=1.45)
    right.text(0.0, 0.035, "BOUNDARIES  No exact future range, range polygon, abundance value, pathogen prevalence, disease-incidence forecast, human-risk surface, exposure/dose model, or individual contact model. Surveillance intensity ≠ abundance; climate suitability ≠ disease burden. Great Black Swamp: C — HOLD / noncanonical. Toledo intake-coordinate discrepancy: UNRESOLVED.", transform=right.transAxes, fontsize=6.6, color="#3f4645", va="bottom", linespacing=1.35)
    fig.savefig(path.with_suffix(".png"), dpi=180, facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix(".svg"), facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg = path.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def render_comparison(rows: list[list[str]]) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["svg.hashsalt"] = "phase12c-vector-ecology-futures"
    fig, ax = plt.subplots(figsize=(18, 11), facecolor="#f1eadc")
    ax.axis("off")
    headers = ["state", "seasonality", "container / water", "forest / host", "surveillance", "heterogeneity", "boundary"]
    table_rows = []
    for row in rows:
        table_rows.append([row[0], row[3], f"{row[4]}; {row[5]}", f"{row[6]}; {row[7]}", f"{row[8]}; {row[9]}", row[10], "suitability ≠ range; surveillance ≠ abundance"])
    table = ax.table(cellText=table_rows, colLabels=headers, loc="center", cellLoc="left", colLoc="left", colWidths=[0.08, 0.17, 0.22, 0.18, 0.18, 0.16, 0.18])
    table.auto_set_font_size(False); table.set_fontsize(6.6); table.scale(1, 2.15)
    colors = {"A": "#dbece4", "B": "#f0e3cb", "C": "#efd9d5"}
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#c6bda8")
        if r == 0:
            cell.set_facecolor("#17384b"); cell.get_text().set_color("white"); cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(colors.get(table_rows[r - 1][0][0], "#f8f4e9"))
            cell.get_text().set_color("#3f4645")
    ax.set_title("Phase 12C — Qualitative Vector Ecology Futures Comparison", loc="left", fontsize=15, weight="bold", color="#17384b", pad=18)
    ax.text(0.0, 0.965, "2050 is an intermediate trajectory; 2075 is a matured or diverged ecological state. Rows are not scores, rankings, forecasts, or disease-risk estimates.", transform=ax.transAxes, fontsize=7.4, color="#3f4645", va="top")
    fig.savefig(COMPARISON_PNG, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(COMPARISON_SVG, facecolor=fig.get_facecolor(), metadata={"Date": None}, bbox_inches="tight")
    plt.close(fig)
    COMPARISON_SVG.write_text("\n".join(line.rstrip() for line in COMPARISON_SVG.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def report_texts() -> dict[str, str]:
    return {
        "vector_ecology_future_sources.md": """# Phase 12C Vector Ecology Futures Sources

This scenario package reuses the accepted Phase 12A vector/ecology source registry and the accepted Phase 9 climate-futures context.

Ohio and university sources support Culex habitat, temperature, seasonality, hosts, and overwintering context.[1][2]

Ohio, Indiana, and Midwest study sources support container-associated Aedes context without establishing a Western Basin-wide future range or abundance surface.[3][4][5]

CDC mosquito guidance distinguishes vector ecology from pathogen and human records and describes trap-specific target taxa and life stages; those limits are carried into the scenario layer.[6][7]

CDC Ixodes material supplies broad regional, seasonal, and surveillance context, not a precise future distribution or abundance claim.[8]

The American dog tick reference is retained as broad regional context only.[9]

The CDC West Nile, Ohio surveillance-update, and CDC tick-data pages anchor separate surveillance streams, program limits, and county-status definitions.[14][15][16]

The CDC West Nile data and Lyme surveillance pages preserve vector-versus-human-case and case-geography boundaries.[17][18]

Michigan, Indiana, and CDC tick-catalog sources provide additional program, effort, and status limitations.[19][20][21]

The Ohio case map is retained only as county-of-residence context.[22]

Accepted Phase 9 climate futures provide regional warming, hot-day, and precipitation context.[10][11]

LOCA2 supplies downscaling-method context.[12]

The Fifth National Climate Assessment supplies broader Midwest adaptation context.[13]

These are projection or scenario evidence, not observed future vector distribution, establishment, abundance, pathogen prevalence, human contact, infection, or disease burden.

Accepted Phase 1, 6, 7, 10, 11, and 12 layers supply generalized hydrology, habitat, governance, population, exposure-boundary, and surveillance interfaces. They remain protected inputs and are not rewritten by this phase.

The source package does not support exact 2050 or 2075 vector counts, abundance estimates, species boundaries, infection prevalence, case totals, or individual risk. Future suitability is retained as a qualitative scenario condition only.
""",
        "vector_ecology_future_assumptions.md": """# Phase 12C Vector Ecology Futures Assumption Ledger

The ledger contains six scenario-horizon states: A2050, A2075, B2050, B2075, C2050, and C2075. Each assumption is explicitly classified as SCENARIO ASSUMPTION, has `reality_status=fictional`, `canon_status=scenario`, and adopts no numeric future value.

A — Managed Ecological Adaptation assumes stronger habitat management, standing-water and container maintenance, ecological/public-health coordination, and earlier detection in selected settings.[1][2][6]

Culex opportunities are reduced in selected managed water interfaces; Aedes opportunities are reduced in selected container settings; Ixodes and forest-edge conditions receive targeted stewardship.[7][10][12]

B — Heterogeneous Adaptive Basin is structurally distinct from A and C.

Its organizing mechanism is spatial and institutional heterogeneity: urban, wetland, agricultural, forest-edge, suburban, and local surveillance settings diverge.[1][3][4]

Some vectors may have locally permissive suitability while others remain constrained; functional management remains uneven and no basin average is asserted.[5][8][10]

C — Warmer / More Variable Vector Landscape assumes longer or less predictable seasonal opportunities for selected vectors, stronger drought/heavy-rain contrasts, episodic standing-water and container opportunities, altered forest-edge humidity/host contexts, and surveillance or management lag in selected locations.[2][5][6]

The selected tick context remains bounded by broad CDC ecology rather than an added range claim.[8][9]

These are qualitative stress-test assumptions and do not imply epidemic disease, human infection, or universal establishment.[10][11][12]

The Fifth National Climate Assessment supplies broader Midwest context for this scenario framing.[13]

The direct surveillance and case-geography sources are retained as boundary evidence rather than as future disease inputs.[14][15][16]

Separate vector, animal, and human records remain separate in the future layer.[17][18]

Michigan, Indiana, and CDC tick-catalog sources remain program-context evidence rather than abundance inputs.[19][20][21]

The Ohio case map remains county-of-residence context rather than a vector or transmission record.[22]

2050 is an intermediate ecological trajectory. 2075 is a matured or diverged ecological state, not a simple intensity copy. All assumptions preserve the distinction that vector presence, abundance, pathogen prevalence, contact, infection, and clinical disease are separate states.
""",
        "vector_ecology_future_findings.md": """# Phase 12C Vector Ecology Futures Findings

## A2050 — Managed Ecological Adaptation

SCENARIO: Coordinated container, catch-basin, ditch, wetland, and selected forest-edge management reduces some unmanaged habitat opportunities while seasonal and episodic conditions remain.[1][2][5]

Surveillance and management interfaces support earlier detection in priority settings, but effort and coverage are not treated as abundance.[6][7][10]

Culex retains warm-season, stagnant-water, bird-host, and overwintering context. Aedes retains container and temperature context with local winter constraints. Ixodes retains forest/edge, humidity, host, and seasonal activity context. None is assigned a future range, abundance value, establishment result, pathogen prevalence, human contact, infection, or disease outcome.[2][5][8]

## A2075 — Managed Ecological Adaptation

SCENARIO: Selected adaptive maintenance and monitoring routines are mature enough to constrain persistent opportunities in priority interfaces, while residual habitat, episodic rainfall, seasonal warmth, and ecological uncertainty remain.[1][2][6]

Selected monitoring and management routines remain bounded by method, coverage, and regional climate context.[7][10][12]

This is a matured management state rather than vector elimination. The package does not convert stronger surveillance into abundance or stronger management into guaranteed absence.

## B2050 — Heterogeneous Adaptive Basin

SCENARIO: Vector-ecology conditions diverge among urban/container, wetland/ditch/floodplain, agricultural, forest-edge, and suburban settings.[1][3][4]

Local maintenance, moisture, temperature, host ecology, settlement form, and program coverage produce a mosaic of constrained, permissive, and episodic opportunities.[5][8][10]

B is not a midpoint. Heterogeneity itself is the future mechanism: some vectors may expand locally in suitability while others remain constrained, and functional surveillance does not create a comparable abundance index.[6][7]

## B2075 — Heterogeneous Adaptive Basin

SCENARIO: Local ecological and institutional differences become durable. A persistent mosaic of humid/dry, connected/fragmented, managed/unmanaged, and early/late detection settings remains, with overlapping management arrangements and negotiation friction.[8][10][12]

No basin-wide vector boundary is inferred. The scenario preserves unresolved local establishment, effort, host ecology, and microhabitat conditions.

The direct surveillance and case-geography sources remain boundary evidence only.[14][15][16]

Michigan, Indiana, and CDC tick-catalog sources remain program-context evidence only.[19][20][21]

The Ohio case map remains county-of-residence context only.[22]

## C2050 — Warmer / More Variable Vector Landscape

SCENARIO: Warmer conditions may lengthen selected seasonal windows, while drought and heavy-rain contrasts interrupt habitat elsewhere.[2][5][10]

Containers, stagnant infrastructure, and episodic retention create opportunities in selected locations where management lags.[11][12]

Forest-edge temperature, humidity, vegetation, and host conditions may shift in different directions. Surveillance and management lag is represented as a detection/response condition, not as abundance, disease risk, or institutional collapse.[6][7][8]

## C2075 — Warmer / More Variable Vector Landscape

SCENARIO: A warmer and more variable landscape contains selected longer or less predictable seasonal opportunities, shifting humid refugia, dry/wet pulses, and persistent infrastructure or container interfaces.[10][11][12]

Capability remains uneven, and selected monitoring-to-management seams struggle to keep pace.[13]

Broad tick context remains bounded by the CDC regional reference.[9]

Separate vector and human surveillance streams remain explicit.[17][18]

This is not an epidemic forecast. No future case total, pathogen prevalence, local transmission, human infection, clinical disease, individual exposure, or individual risk is modeled.

## Cross-system interpretation

Settlement form can shape container and developed-edge opportunity; land-cover and edge conditions can shape generalized habitat context; climate and hydrology can alter seasonal or episodic opportunity; and governance/surveillance can alter detection and response interfaces. These are qualitative dependencies, not human-contact or disease models.

Presence ≠ abundance ≠ pathogen prevalence ≠ human contact ≠ human infection ≠ clinical disease. Future suitability ≠ guaranteed establishment; range-expansion potential ≠ observed future range; climate suitability ≠ disease burden; surveillance intensity ≠ abundance.
""",
        "vector_ecology_future_consistency.md": """# Phase 12C Vector Ecology Futures Consistency

The future tables are separate from the accepted Phase 12A vector ecology and Phase 12B dependency tables. Every future row carries a scenario identifier, horizon, baseline reference, scenario assumption ID, provenance basis, qualitative plausibility/uncertainty, fictional/scenario status, and a scenario relationship basis.

Vector states carry current-fact, scenario-assumption, and scenario-consequence fields. Suitability and habitat opportunity are explicitly potential scenario conditions. Establishment, abundance, pathogen prevalence, human contact, infection, and clinical disease are not projected.

Habitat states retain generalized urban/container, standing-water, wetland/floodplain, forest/edge, host, temperature, and precipitation relationships. Each habitat state carries an explicit Phase 12A habitat-association reference and matched current-fact crosswalk. They do not create precise future polygons or collection locations. Surveillance states retain program, method, effort, coverage, and detection limits; surveillance intensity is not abundance.

Dependency states reuse the 28 accepted Phase 12B dependency identifiers as baseline references without appending future rows to the factual dependency table. Documented and inferred relationships, spatial scale, monitoring/control boundaries, and health boundaries remain distinct.

Uncertainty states carry forward the accepted Phase 12A limitations with source mappings matched to the accepted source IDs. Each 2050/2075 state table contains a substantive horizon distinction rather than only a relabeled year. Great Black Swamp remains C — HOLD / noncanonical, and the Toledo intake-coordinate discrepancy remains UNRESOLVED. No future vector habitat polygon is derived from the held geometry.
""",
        "vector_ecology_future_qa.md": """# Phase 12C Vector Ecology Futures QA

The package contains 36 scenario assumptions, 36 vector states, 48 habitat states, 30 surveillance states, 168 dependency states, 60 uncertainty states, six comparison rows, 28 scenario-source records, Maps 40/40b, a comparison figure, and deterministic Python/R validators.

The Phase 12C Python validator checks exact schemas and row counts, producer/reference integrity, scenario and horizon coverage, assumption references, fictional/scenario status, baseline separation, A/B/C distinction, 2050/2075 horizon distinction, qualitative-only fields, vector-specific Culex/Aedes/Ixodes logic, surveillance boundaries, habitat scale, negative scope, active holds, Maps 40/40b, Phase 12A/12B freeze hashes, and the Phase 1–11 protected artifact inventory.

The independent R validator re-reads the tables and manifests through a separate code path, recomputes structural counts, checks assumption and baseline references, checks qualitative and negative-scope boundaries, verifies the maps and citations, and independently recomputes protected-artifact hashes.

Prohibited constructs include a continuous disease-risk surface, precise synthetic future range polygons, future case maps, individual-risk or exposure maps, abundance inferred from surveillance effort, climate suitability presented as disease burden, human infection forecasts, vulnerability/EJ scoring, Phase 13 implementation, and frozen-artifact modification.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. Deferred maintenance remains outside this phase: Phase 6B manifest status wording mismatch and Phase 3A missing manifest status.
""",
        "vector_ecology_future_worldbuilding.md": """# Phase 12C Vector Ecology Futures — Speculative Worldbuilding

Everything in this section is SPECULATIVE WORLDBUILDING, not an observed scientific fact, a disease forecast, or accepted canon.

- A basin maintenance compact can turn catch basins, containers, wetland edges, and forest-edge monitoring into recurring civic work without eliminating ecological variability.
- B's political and ecological texture comes from local divergence: the same warm season can mean container pressure, dry drainage, wetland retention, or forest-edge refuge in different places.
- C makes seasonality feel unreliable rather than simply longer: drought can erase one habitat opportunity while heavy rain or stagnant infrastructure creates another.
- Surveillance becomes a contested language of attention: what is detected early, what is method-limited, and what remains unknown can shape institutions without becoming abundance or disease truth.
- The held Great Black Swamp geometry remains an absence of canonical cartography, not a future vector refuge polygon.
""",
    }


def append_citation_blocks() -> None:
    for name in ("vector_ecology_future_sources.md", "vector_ecology_future_assumptions.md", "vector_ecology_future_findings.md"):
        path = REPORTS / name
        result = subprocess.run([sys.executable, str(CITATION_SCRIPT), "--ledger", str(LEDGER), "render", "--style", "markdown", "--cited-in", str(path)], check=True, capture_output=True, text=True)
        path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n\n" + result.stdout.strip() + "\n", encoding="utf-8")


def main() -> None:
    for directory in (ANALYSIS, SCENARIOS, MAPS, FIGURES, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    ensure_ledger()
    nodes = read_rows(BASELINE_NODES)
    habitat = read_rows(BASELINE_HABITAT)
    dependencies = read_rows(BASELINE_DEPS)
    uncertainties = read_rows(BASELINE_UNCERTAINTY)
    assumptions = build_assumptions()
    vector_states = build_vector_states(assumptions, nodes)
    habitat_states = build_habitat_states(assumptions, habitat)
    surveillance_states = build_surveillance_states(assumptions, nodes, dependencies)
    dependency_states = build_dependency_states(assumptions, dependencies)
    uncertainty_states = build_uncertainty_states(assumptions, uncertainties)
    comparisons = comparison_rows()
    write_rows(ASSUMPTIONS, ASSUMPTION_COLUMNS, assumptions)
    write_rows(VECTOR_STATES, VECTOR_COLUMNS, vector_states)
    write_rows(HABITAT_STATES, HABITAT_COLUMNS, habitat_states)
    write_rows(SURVEILLANCE_STATES, SURVEILLANCE_COLUMNS, surveillance_states)
    write_rows(DEPENDENCY_STATES, DEPENDENCY_COLUMNS, dependency_states)
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
        ASSUMPTIONS, VECTOR_STATES, HABITAT_STATES, SURVEILLANCE_STATES, DEPENDENCY_STATES, UNCERTAINTY_STATES,
        SOURCES, COMPARISON, COMPARISON_PNG, COMPARISON_SVG, MAP2050.with_suffix(".png"), MAP2050.with_suffix(".svg"),
        MAP2075.with_suffix(".png"), MAP2075.with_suffix(".svg"), LEDGER,
        *(REPORTS / name for name in report_texts()),
        PY_VALIDATOR, R_VALIDATOR,
    ]
    if REVIEW.exists():
        artifacts.append(REVIEW)
    if INITIAL_REVIEW.exists():
        artifacts.append(INITIAL_REVIEW)
    manifest = {
        "phase": "12C",
        "status": "implemented_validated_pending_sol_acceptance",
        "scope": "qualitative vector ecology futures, 2050 / 2075",
        "scenario_ids": list(SCENARIO_IDS),
        "map_numbers": [40, "40b"],
        "counts": {
            "scenario_assumptions": len(assumptions), "vector_states": len(vector_states), "habitat_states": len(habitat_states),
            "surveillance_states": len(surveillance_states), "dependency_states": len(dependency_states), "uncertainty_states": len(uncertainty_states),
            "scenario_sources": len(SOURCE_ROWS), "comparison_rows": len(comparisons),
        },
        "numeric_future_values_adopted": False,
        "future_range_polygons": False,
        "disease_incidence_forecast": False,
        "human_risk_model": False,
        "protected_inputs": [
            "reports/phase12a_vector_ecology_freeze_manifest.json",
            "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
        ],
        "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": digest(path)} for path in artifacts},
        "phase12a_12b_immutable": True,
        "phase1_11_immutable": True,
        "phase13_implemented": False,
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
