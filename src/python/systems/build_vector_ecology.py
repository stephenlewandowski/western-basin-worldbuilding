"""Build the bounded Phase 12A/12B vector ecology package.

The package separates vector ecology, surveillance observations, and qualitative
cross-system dependencies. It does not estimate abundance, contact, infection,
disease risk, or future range.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/vector_ecology"
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"
RETRIEVAL_DATE = "2026-09-08"
TICK_XLSX = RAW / "Public_Use_Ixodes_County_Table_2024_summary.xlsx"
CITATION_LEDGER = REPORTS / "phase12_citation_ledger.json"

MAP38_BASE = MAPS / "38_vector_ecology_baseline_2026"
MAP39_BASE = MAPS / "39_vector_environment_human_dependencies_2026"
A_MANIFEST = REPORTS / "vector_ecology_baseline_manifest.json"
B_MANIFEST = REPORTS / "vector_dependency_manifest.json"
WORKING_MANIFEST = REPORTS / "phase12_working_manifest.json"
A_CHECK = REPORTS / "vector_ecology_artifact_check.json"
B_CHECK = REPORTS / "vector_dependency_artifact_check.json"

CITATION_URLS = [
    "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/animals/mosquitoes-in-ohio",
    "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update",
    "https://ohid.ohio.gov/wps/wcm/connect/gov/ohio+content+english/odh/know-our-programs/zoonotic-disease-program/media/west-nile-virus-map",
    "https://ohioline.osu.edu/factsheet/ent-89",
    "https://www.mdpi.com/2075-4450/14/1/56",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4106292",
    "https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf",
    "https://www.michigan.gov/emergingdiseases/home/west-nile",
    "https://www.in.gov/health/idepd/zoonotic-and-vectorborne-epidemiology-entomology/vector-borne-diseases/mosquito-borne-diseases/aedes-albopictus",
    "https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county",
    "https://www.cdc.gov/mosquitoes/about",
    "https://www.cdc.gov/mosquitoes/php/toolkit/mosquito-surveillance-traps.html",
    "https://www.cdc.gov/west-nile-virus/data-maps",
    "https://www.cdc.gov/west-nile-virus/about",
    "https://www.cdc.gov/ticks/about/where-ticks-live.html",
    "https://www.cdc.gov/ticks/data-research/facts-stats",
    "https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html",
    "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html",
    "https://www.cdc.gov/ticks/data-research/facts-stats/american-dog-tick-surveillance.html",
    "https://www.cdc.gov/lyme/data-research/facts-stats/index.html",
]

CORE_COUNTIES = {
    "39039": ("OH", "Defiance"), "39051": ("OH", "Fulton"),
    "39063": ("OH", "Hancock"), "39069": ("OH", "Henry"),
    "39095": ("OH", "Lucas"), "39123": ("OH", "Ottawa"),
    "39125": ("OH", "Paulding"), "39137": ("OH", "Putnam"),
    "39143": ("OH", "Sandusky"), "39147": ("OH", "Seneca"),
    "39161": ("OH", "Van Wert"), "39171": ("OH", "Williams"),
    "39173": ("OH", "Wood"), "26091": ("MI", "Lenawee"),
    "26115": ("MI", "Monroe"), "18003": ("IN", "Allen"),
    "18033": ("IN", "DeKalb"), "18151": ("IN", "Steuben"),
}

SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
]
SOURCE_BASE_COLUMNS = SOURCE_COLUMNS[:10]
SOURCE_ROWS = [
    ["v12_ohio_mosquitoes", "Ohio Department of Health — Mosquitoes in Ohio", CITATION_URLS[0], "state_public_health", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "Ohio / species and seasonal context", "state species and habitat page", "Ohio species presence, habitats, host context, and May–October activity statement", "Page-level distribution is not an abundance survey; lack of a record is not absence."],
    ["v12_ohio_vector_update", "Ohio Vector-borne Disease Surveillance Update", CITATION_URLS[1], "state_surveillance", "2025 year-end update dated 2025-12-11", RETRIEVAL_DATE, "Ohio / agency and county summaries", "trapping, pooled mosquito samples, laboratory surveillance", "2025 Ohio mosquito-pool and human/vector surveillance summaries", "Species-specific pool counts, trap effort by county, and local transmission are not established by the summary."],
    ["v12_ohio_wnv_map", "Ohio West Nile Virus Disease in Ohio Map", CITATION_URLS[2], "state_surveillance", "2025 data as of 2025-11-19", RETRIEVAL_DATE, "Ohio / county of residence", "reported human-case map", "Contextual human-case observation only", "County of residence is not county of infection or local transmission; human cases are not vector abundance."],
    ["v12_osu_culex", "Ohio State University Ohioline — Northern House Mosquito", CITATION_URLS[3], "university_extension", "current fact sheet; accessed 2026-09-08", RETRIEVAL_DATE, "Ohio / urban-suburban-rural and habitat context", "species fact sheet and cited literature", "Culex pipiens habitat, host, seasonality, life-cycle and surveillance context", "Fact-sheet claims are not a Western Basin abundance estimate; clinical material is not used as a disease model."],
    ["v12_ohio_ae_japonicus", "Invasive Aedes japonicus Mosquitoes in Wooster, Ohio", CITATION_URLS[4], "peer_reviewed", "2023 article; 2021 field collections", RETRIEVAL_DATE, "Wooster, northeastern Ohio", "CDC light, BG-Sentinel, and gravid traps; morphology and molecular confirmation", "Regional evidence of Ae. japonicus establishment and trap-specific composition", "Wooster trap composition cannot be generalized to the Western Basin or treated as regional abundance."],
    ["v12_mi_ae_japonicus", "Establishment of Aedes japonicus in Michigan", CITATION_URLS[5], "peer_reviewed", "2014 article; Michigan field surveillance", RETRIEVAL_DATE, "Michigan / Saginaw County study", "CDC gravid and New Jersey light traps", "Midwest container-habitat and surveillance-method context", "Study-area findings do not establish current Western Basin distribution or abundance."],
    ["v12_mi_annual_2023", "Michigan EZID Annual Surveillance Summary", CITATION_URLS[6], "state_surveillance", "2023 annual summary", RETRIEVAL_DATE, "Michigan / participating local health departments", "local health department mosquito sampling, identification, and laboratory testing", "2023 mosquito-pool totals, arbovirus detections, and invasive Aedes response context", "Participating jurisdictions and methods vary; mosquito-pool positives are not human cases or local transmission."],
    ["v12_mi_wnv", "Michigan Emerging Disease Issues — West Nile virus", CITATION_URLS[7], "state_public_health", "current program page; accessed 2026-09-08", RETRIEVAL_DATE, "Michigan / state and county program", "public surveillance and reporting program", "Michigan surveillance-program context", "Program page is not a species abundance or local vector-density dataset."],
    ["v12_in_ae_albopictus", "Indiana Department of Health — Aedes albopictus", CITATION_URLS[8], "state_public_health", "page updated 2025-05; distribution map updated 2023-02", RETRIEVAL_DATE, "Indiana / county distribution context", "distribution map and species life-cycle page", "Indiana Ae. albopictus presence, container habitat, and temperature-linked development context", "Known distribution map is not a continuous range or abundance surface; effort is not reported on the page."],
    ["v12_in_wnv_2026", "Indiana Department of Health — First 2026 WNV Case", CITATION_URLS[9], "state_surveillance", "2026-08-28 news release", RETRIEVAL_DATE, "Indiana / county and state summary", "mosquito testing and human-case surveillance", "33 counties with positive mosquitoes and one contextual human case", "The release does not provide comparable county sampling effort or species counts; human case is county of residence context."],
    ["v12_cdc_mosquito_biology", "CDC — About Mosquitoes", CITATION_URLS[10], "federal_public_health", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / general biology", "public-health biology reference", "Vector-versus-pathogen distinction and environmental determinants of mosquito life span", "General biology is not a Western Basin occurrence or abundance record."],
    ["v12_cdc_mosquito_traps", "CDC — Mosquito Surveillance Traps", CITATION_URLS[11], "federal_surveillance_guidance", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / surveillance methods", "trap-method guidance", "Trap selectivity, life-stage coverage, and effort limitations", "Different traps sample different species and life stages; trap counts are not interchangeable abundance measures."],
    ["v12_cdc_wnv_data", "CDC — Data and Maps for West Nile", CITATION_URLS[12], "federal_surveillance", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / state and territorial reporting", "ArboNET and NNDSS context", "Separate mosquito, animal, and human surveillance streams", "Reported case data and vector data are distinct surveillance products."],
    ["v12_cdc_wnv_about", "CDC — About West Nile", CITATION_URLS[13], "federal_public_health", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / general ecology", "vector-pathogen lifecycle reference", "Bird–mosquito ecological context and seasonal activity framing", "Used only as ecological context; no infection probability or clinical model is created."],
    ["v12_cdc_ticks_live", "CDC — Where Ticks Live", CITATION_URLS[14], "federal_public_health", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "Contiguous United States / broad distribution", "species distribution and host-seeking context", "Ixodes scapularis and Dermacentor variabilis regional relevance, habitat/season context", "Approximate distributions are not precise local maps or abundance estimates."],
    ["v12_cdc_tick_data", "CDC — Tick Data", CITATION_URLS[15], "federal_surveillance", "current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / county dashboards", "surveillance dashboard catalog", "Availability and scope of tick surveillance products", "Dashboard availability does not imply uniform sampling or comparable effort."],
    ["v12_cdc_tick_sets", "CDC — Tick Surveillance Data Sets", CITATION_URLS[16], "federal_surveillance", "2023/2025 data definitions; accessed 2026-09-08", RETRIEVAL_DATE, "United States / county", "ArboNET tick-module status definitions", "Established/reported/no-record status definitions and non-absence caveat", "County status is cumulative and sampling/reporting is heterogeneous; no-records is not absence."],
    ["v12_cdc_ixodes", "CDC — Blacklegged Tick Surveillance", CITATION_URLS[17], "federal_surveillance", "2025 map and current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / county and modeled suitability context", "ArboNET county status and map", "Ixodes scapularis established-status definition and seasonality", "Six-or-more threshold is a status rule, not an abundance index; current workbook used here is the 2023 summary."],
    ["v12_cdc_dvariabilis", "CDC — American Dog Tick Surveillance", CITATION_URLS[18], "federal_surveillance", "2025 map and current page; accessed 2026-09-08", RETRIEVAL_DATE, "United States / county and broad distribution", "ArboNET/locality-record map", "Dermacentor variabilis broad regional relevance and surveillance caveat", "No current core-county D. variabilis workbook was ingested; no local abundance claim is made."],
    ["v12_cdc_lyme", "CDC — Lyme Disease Surveillance and Data", CITATION_URLS[19], "federal_surveillance", "2023 case-surveillance context; accessed 2026-09-08", RETRIEVAL_DATE, "United States / county of residence", "NNDSS surveillance guidance", "Context for the distinction between human case records and exposure/transmission location", "Human cases are not vector records, local transmission proof, or exposure locations."],

    ["phase1_hydrology_context", "Accepted Phase 1 hydrology and wetlands context", "reports/water_system_manifest.json", "repository_accepted_layer", "accepted current-development layer", RETRIEVAL_DATE, "Western Basin / watershed and wetland", "accepted water-system and hydrography artifacts", "Generalized standing-water, wetland, tributary, and floodplain interface", "Reused context only; does not create vector detections or a hydrologic risk surface."],
    ["phase6_ecology_context", "Accepted Phase 6 ecology and biodiversity context", "reports/phase6a_ecology_freeze_manifest.json", "repository_accepted_layer", "accepted/frozen ecological layer", RETRIEVAL_DATE, "Western Basin / ecological systems", "accepted ecology nodes and relationships", "Generalized wetland, riparian, terrestrial, and host-ecology interface", "Reused context only; Great Black Swamp remains held and noncanonical."],
    ["phase7_health_context", "Accepted Phase 7 environmental-health context", "reports/phase7a_exposure_environmental_health_freeze_manifest.json", "repository_accepted_layer", "accepted/frozen exposure-context layer", RETRIEVAL_DATE, "Western Basin / pathway context", "accepted exposure pathway and monitoring artifacts", "Potential vector-related environmental-health interface without exposure or dose", "No individual exposure, dose, illness, or disease attribution is added."],
    ["phase9_climate_context", "Accepted Phase 9 climate and natural-hazard context", "reports/phase9a_climate_natural_hazards_freeze_manifest.json", "repository_accepted_layer", "accepted/frozen climate layer", RETRIEVAL_DATE, "Western Basin / station, county, watershed, shoreline", "accepted climate observations and qualitative dependencies", "Temperature, precipitation, drought, and flooding context", "Reused context only; no future range or hazard surface is generated."],
    ["phase10_governance_context", "Accepted Phase 10 governance/surveillance context", "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", "repository_accepted_layer", "accepted/frozen governance layer", RETRIEVAL_DATE, "Western Basin / institutional and program scales", "accepted governance actors, roles, and coordination artifacts", "Surveillance, monitoring, warning, data, and decision interfaces", "Monitoring is not control and program participation is not proof of complete coverage."],
    ["phase11_population_context", "Accepted Phase 11 population/settlement context", "reports/phase11b_population_mobility_dependencies_freeze_manifest.json", "repository_accepted_layer", "accepted/frozen population/mobility layer", RETRIEVAL_DATE, "Western Basin / county, place, generalized employment", "accepted population and mobility artifacts", "Population concentration and settlement/workplace interface", "Population presence is not contact, exposure, infection, or disease risk."],
    ["phase4_data_context", "Accepted Phase 4 observation/data context", "reports/observation_system_manifest.json", "repository_accepted_layer", "accepted/frozen observation layer", RETRIEVAL_DATE, "Western Basin / station and information chain", "accepted observation-to-decision artifacts", "Detection, data availability, uncertainty, and decision-interface context", "Observation coverage is heterogeneous and is not treated as complete surveillance."],
]

NODE_COLUMNS = [
    "node_id", "name", "node_type", "vector_group", "taxon_or_system", "habitat_context",
    "seasonality", "geographic_scale", "latitude", "longitude", "source_id",
    "evidence_status", "confidence", "reality_status", "canon_status", "notes",
]
NODE_ROWS = [
    ["VEC-001", "Northern house mosquito", "vector_taxon", "mosquito", "Culex pipiens", "urban/suburban/rural; stagnant water, catch basins, ditches, containers", "twilight activity; Ohio warm-season activity; overwintering/diapause context", "Ohio / regional species context", "", "", "v12_ohio_mosquitoes", "documented_presence", "high", "real", "verified", "Ohio source describes widespread occurrence; this is presence and ecology context, not abundance."],
    ["VEC-002", "Culex pipiens/restuans complex context", "vector_taxon", "mosquito", "Culex pipiens plus close relative Culex restuans", "temperate urban, suburban, rural, and wet/ditch interfaces", "seasonal mosquito activity; taxon-level surveillance may differ by program", "Ohio / Midwest taxonomic context", "", "", "v12_osu_culex", "documented_taxonomic_context", "moderate", "real", "verified", "The project retains the complex as a surveillance/ecology context and does not combine species into a pseudo-abundance measure."],
    ["VEC-003", "Asian tiger mosquito", "vector_taxon", "mosquito", "Aedes albopictus", "vegetated urban edges; artificial and natural containers; tires and gutters", "day activity, especially shade; warm-season container lifecycle", "Ohio/Indiana/Michigan regional context", "", "", "v12_ohio_mosquitoes", "documented_presence", "high", "real", "verified", "Ohio and Indiana sources document regional presence/context; county records are not a precise Western Basin distribution."],
    ["VEC-004", "Asian bush mosquito", "vector_taxon", "mosquito", "Aedes japonicus", "natural and artificial container habitats; forest/stream settings in study sources", "field-study seasonality; trap-specific detection", "Ohio/Michigan study context", "", "", "v12_ohio_ae_japonicus", "documented_regional_study", "moderate", "real", "verified", "Wooster Ohio and Michigan study evidence is retained as regional context, not a local Western Basin range claim."],
    ["VEC-005", "Eastern treehole mosquito", "vector_taxon", "mosquito", "Aedes triseriatus", "wooded areas, treeholes, parks, and artificial containers", "day activity in shady wooded settings", "Ohio / species context", "", "", "v12_ohio_mosquitoes", "documented_presence", "high", "real", "verified", "Ohio source describes distribution and habitat; no abundance or disease-incidence inference is made."],
    ["VEC-006", "Blacklegged tick", "vector_taxon", "tick", "Ixodes scapularis", "grass/shrub questing and host-associated forest/edge interface", "spring, summer, fall; adults may quest above freezing in winter", "selected Ohio/Michigan/Indiana counties", "", "", "v12_cdc_ixodes", "surveillance_status", "high", "real", "verified", "County status rows below use the CDC 2023 summary; established status is a threshold-based surveillance classification, not abundance."],
    ["VEC-007", "American dog tick", "vector_taxon", "tick", "Dermacentor variabilis", "grass/shrub and terrestrial edge context", "highest biting context in spring and summer", "eastern United States / regional context", "", "", "v12_cdc_dvariabilis", "documented_broad_distribution", "moderate", "real", "verified", "CDC documents broad eastern distribution; no core-county D. variabilis status table is asserted here."],
    ["VEC-008", "Western Basin wetland and standing-water interface", "habitat_context", "mosquito/tick interface", "wetland and standing-water systems", "wetlands, ponds, ditches, temporary and permanent water", "seasonal water availability; hydrologic variability", "wetland / watershed / generalized regional", "41.690", "-83.220", "phase1_hydrology_context", "accepted_context", "high", "real", "verified", "Generalized accepted wetland context anchor; it is not a vector collection location or detection."],
    ["VEC-009", "Urban and container habitat interface", "habitat_context", "mosquito", "artificial containers and developed edges", "artificial containers, catch basins, gutters, tires, household and developed edges", "warm-season container availability", "urban/suburban generalized interface", "", "", "v12_ohio_mosquitoes", "documented_habitat_context", "high", "real", "inferred", "Habitat class is generalized; no parcel, block, container inventory, or local abundance is modeled."],
    ["VEC-010", "Forest and edge host interface", "habitat_context", "tick/mosquito", "woodland edge, grasses, shrubs, treeholes, and hosts", "woodland edge, grass, shrubs, treeholes, small-mammal and deer host interface", "spring through fall tick context; shaded mosquito context", "forest/edge generalized interface", "", "", "v12_cdc_ticks_live", "documented_habitat_context", "moderate", "real", "inferred", "Broad host-seeking and habitat interface; no exact movement route or sensitive host location."],
    ["VEC-011", "Agricultural, ditch, and floodplain water interface", "habitat_context", "mosquito", "ditches, temporary water, floodplain, and drainage-altered landscape", "ditches, temporary water, floodplain and drainage-altered landscape", "event and season dependent", "watershed / floodplain generalized interface", "", "", "phase1_hydrology_context", "project_interface", "limited", "real", "inferred", "A generalized hydrology-to-habitat interface; no flood footprint or mosquito abundance is assigned."],
    ["VEC-012", "Vertebrate host ecology context", "host_ecology", "mosquito/tick", "birds, small mammals, deer, domestic animals, and humans", "birds, small mammals, deer, domestic animals, and humans as distinct host contexts", "life-stage and season dependent", "regional ecological context", "", "", "v12_cdc_wnv_about", "documented_ecological_context", "moderate", "real", "verified", "Host ecology supports lifecycle context; host presence is not contact, infection, or disease."],
    ["VEC-013", "Temperature and seasonal development interface", "environmental_driver", "mosquito/tick", "temperature, humidity, photoperiod, and freeze/thaw", "temperature, humidity, photoperiod, freeze/thaw", "seasonal development and activity", "station/regional climate context", "", "", "phase9_climate_context", "accepted_context_plus_documented_biology", "moderate", "real", "inferred", "Temperature relationship is a qualitative interface; no thermal suitability or future range model is created."],
    ["VEC-014", "Precipitation and hydrology interface", "environmental_driver", "mosquito", "rainfall, standing water, flow, wetlands, and drainage", "rainfall, standing water, flow, wetland and drainage conditions", "event and season dependent", "station/watershed/wetland context", "", "", "phase1_hydrology_context", "accepted_context_plus_documented_habitat", "moderate", "real", "inferred", "Hydrology is linked qualitatively to habitat opportunity; no continuous habitat surface or causal count is estimated."],
    ["VEC-015", "Ohio vector surveillance program", "surveillance_program", "mosquito/tick", "Ohio Department of Health, laboratory, local public-health, and sanitary-district partners", "Ohio Department of Health, laboratory, local public-health and sanitary-district partners", "summer/fall reporting program", "state/agency/county", "", "", "v12_ohio_vector_update", "documented_program", "high", "real", "verified", "Program and pooled results are retained as surveillance records with effort and scale limits."],
    ["VEC-016", "Michigan arbovirus surveillance program", "surveillance_program", "mosquito/tick", "MDHHS, local health departments, laboratories, and partners", "MDHHS, local health departments, laboratories and partners", "seasonal arbovirus surveillance", "state/participating-local-health-department", "", "", "v12_mi_annual_2023", "documented_program", "high", "real", "verified", "Participating jurisdictions and methods vary; counts are not a statewide abundance index."],
    ["VEC-017", "Indiana mosquito-borne activity surveillance", "surveillance_program", "mosquito", "Indiana Department of Health and local surveillance", "Indiana Department of Health and local surveillance", "warm-season activity through hard freeze context", "state/county", "", "", "v12_in_wnv_2026", "documented_program", "high", "real", "verified", "State/county surveillance context; species, effort, and human cases remain separate."],
    ["VEC-018", "CDC ArboNET and tick surveillance interface", "surveillance_program", "mosquito/tick", "ArboNET, NNDSS, county tick-status, and pathogen-surveillance products", "ArboNET, NNDSS, county tick-status and pathogen-surveillance products", "annual and seasonal reporting products", "national/state/county", "", "", "v12_cdc_tick_sets", "documented_program", "high", "real", "verified", "CDC programs maintain separate vector, pathogen, animal, and human records; no combined index is created."],
    ["VEC-019", "West Nile virus pathogen-in-vector context", "pathogen_context", "mosquito", "West Nile virus in mosquito-pool and other surveillance streams", "West Nile virus in mosquito-pool and other surveillance streams", "summer/fall seasonal context", "state/county surveillance scale", "", "", "v12_cdc_wnv_data", "context_only", "high", "real", "verified", "A positive vector pool is not a human case, contact, infection, clinical disease, or proof of local transmission."],
    ["VEC-020", "Tickborne pathogen surveillance context", "pathogen_context", "tick", "selected pathogens in host-seeking Ixodes ticks", "selected pathogens in host-seeking Ixodes ticks", "surveillance-period dependent", "county surveillance scale", "", "", "v12_cdc_tick_sets", "context_only", "high", "real", "verified", "Pathogen-in-tick status is distinct from tick presence, human contact, infection, disease, and county-of-residence cases."],
]

EDGE_COLUMNS = [
    "edge_id", "from_id", "to_id", "relationship_type", "relationship_basis", "geographic_scale",
    "source_id", "evidence_status", "confidence", "reality_status", "canon_status", "notes",
]
EDGE_ROWS = [
    ["VEE-001", "VEC-001", "VEC-009", "uses_habitat", "documented_source", "urban/suburban generalized", "v12_ohio_mosquitoes", "documented_relationship", "high", "real", "verified", "Culex pipiens habitat includes stagnant water, catch basins, ditches, and water-holding containers."],
    ["VEE-002", "VEC-001", "VEC-011", "uses_habitat", "documented_source", "ditch/floodplain generalized", "v12_ohio_mosquitoes", "documented_relationship", "moderate", "real", "verified", "The source describes ditches and stagnant water; the floodplain interface is generalized and not a local density estimate."],
    ["VEE-003", "VEC-001", "VEC-012", "host_association", "documented_source", "regional ecology", "v12_ohio_mosquitoes", "documented_relationship", "high", "real", "verified", "Ohio source describes bird preference; host association is not human contact or infection."],
    ["VEE-004", "VEC-001", "VEC-019", "pathogen_context", "documented_source", "state/county surveillance", "v12_ohio_mosquitoes", "documented_context", "moderate", "real", "verified", "Culex and WNV are retained as ecological context; no disease attribution is made."],
    ["VEE-005", "VEC-003", "VEC-009", "uses_habitat", "documented_source", "urban/container generalized", "v12_ohio_mosquitoes", "documented_relationship", "high", "real", "verified", "Aedes albopictus uses artificial and natural containers, tires, treeholes, and gutters."],
    ["VEE-006", "VEC-003", "VEC-013", "seasonal_activity", "documented_source", "regional seasonality", "v12_ohio_mosquitoes", "documented_relationship", "moderate", "real", "verified", "Day activity and warm-season container development are retained without a suitability curve."],
    ["VEE-007", "VEC-004", "VEC-009", "uses_habitat", "documented_source", "study-area container habitat", "v12_ohio_ae_japonicus", "documented_relationship", "moderate", "real", "verified", "Wooster and Michigan studies support container-habitat context; findings are not generalized abundance."],
    ["VEE-008", "VEC-005", "VEC-010", "uses_habitat", "documented_source", "woodland/park generalized", "v12_ohio_mosquitoes", "documented_relationship", "high", "real", "verified", "Aedes triseriatus is associated with wooded areas, parks, treeholes, and some artificial containers."],
    ["VEE-009", "VEC-006", "VEC-010", "host_seeking_interface", "documented_source", "forest/edge generalized", "v12_cdc_ticks_live", "documented_relationship", "moderate", "real", "verified", "CDC describes tick questing on grasses/shrubs and host-associated habitat; no exact route is mapped."],
    ["VEE-010", "VEC-006", "VEC-012", "host_association", "documented_source", "regional ecology", "v12_cdc_ticks_live", "documented_relationship", "moderate", "real", "verified", "Host-seeking behavior is ecological context, not human-vector contact or infection."],
    ["VEE-011", "VEC-007", "VEC-010", "uses_habitat", "documented_source", "eastern U.S. terrestrial context", "v12_cdc_dvariabilis", "documented_relationship", "limited", "real", "verified", "Broad D. variabilis distribution and spring/summer biting context are not local abundance evidence."],
    ["VEE-012", "VEC-008", "VEC-014", "hydrologic_context", "accepted_layer", "wetland/watershed", "phase1_hydrology_context", "accepted_context", "high", "real", "verified", "Accepted wetland/hydrology context is reused without adding vector detections."],
    ["VEE-013", "VEC-014", "VEC-011", "habitat_opportunity", "documented_plus_inferred", "watershed/floodplain", "phase1_hydrology_context", "project_inference", "limited", "real", "inferred", "Precipitation and standing-water opportunity are physically plausible; no measured abundance response is asserted."],
    ["VEE-014", "VEC-013", "VEC-001", "seasonal_development", "documented_source", "Ohio/regional", "v12_osu_culex", "documented_relationship", "moderate", "real", "verified", "OSU describes temperature-linked larval duration and seasonal diapause/emergence context."],
    ["VEE-015", "VEC-013", "VEC-003", "seasonal_development", "documented_source", "Indiana/regional", "v12_in_ae_albopictus", "documented_relationship", "moderate", "real", "verified", "Indiana source states that high temperatures can shorten the stated Aedes life-cycle duration."],
    ["VEE-016", "VEC-013", "VEC-006", "seasonal_activity", "documented_source", "county/regional", "v12_cdc_ixodes", "documented_relationship", "moderate", "real", "verified", "CDC identifies spring/summer/fall activity and above-freezing winter adult questing context."],
    ["VEE-017", "VEC-012", "VEC-019", "lifecycle_context", "documented_source", "state/county surveillance", "v12_cdc_wnv_about", "documented_context", "moderate", "real", "verified", "Bird–mosquito pathogen-cycle context is retained without moving to human infection or disease."],
    ["VEE-018", "VEC-015", "VEC-019", "tests_vector_pools", "documented_source", "Ohio agency/county", "v12_ohio_vector_update", "documented_surveillance", "high", "real", "verified", "Ohio summary reports pooled mosquito testing and positive WNV pools with agency/county scope."],
    ["VEE-019", "VEC-016", "VEC-019", "tests_vector_pools", "documented_source", "Michigan participating counties", "v12_mi_annual_2023", "documented_surveillance", "high", "real", "verified", "Michigan annual summary reports local mosquito sampling, identification, and laboratory testing."],
    ["VEE-020", "VEC-017", "VEC-019", "tests_vector_pools", "documented_source", "Indiana counties", "v12_in_wnv_2026", "documented_surveillance", "moderate", "real", "verified", "Indiana release reports positive mosquito tests in 33 counties; comparable effort is not reported."],
    ["VEE-021", "VEC-018", "VEC-006", "classifies_county_status", "documented_source", "county", "v12_cdc_tick_sets", "documented_surveillance", "high", "real", "verified", "CDC county tick statuses retain established/reported/no-record classes and explicit non-absence caveats."],
    ["VEE-022", "VEC-018", "VEC-020", "tests_pathogens_in_ticks", "documented_source", "county", "v12_cdc_tick_sets", "documented_surveillance", "high", "real", "verified", "CDC pathogen-in-tick status uses molecular detection in host-seeking Ixodes; it is not a human case record."],
    ["VEE-023", "VEC-019", "VEC-020", "keeps_pathogen_streams_separate", "project_boundary", "state/county program", "v12_cdc_wnv_data", "boundary_rule", "high", "real", "verified", "Mosquito-pool and tick-pathogen programs remain separate surveillance streams; no combined pathogen index is created."],
    ["VEE-024", "VEC-006", "VEC-008", "generalized_habitat_interface", "accepted_ecology_context", "wetland/forest edge", "phase6_ecology_context", "accepted_context", "limited", "real", "inferred", "Phase 6 wetland and terrestrial context is reused as a generalized interface, not a local tick or mosquito occurrence claim."],
    ["VEE-025", "VEC-009", "VEC-015", "surveillance_target_context", "project_inference", "urban/agency", "v12_cdc_mosquito_traps", "project_inference", "limited", "real", "inferred", "Container habitat can guide surveillance targeting conceptually; no program performance or local detection is inferred."],
    ["VEE-026", "VEC-013", "VEC-015", "seasonal_program_timing", "documented_program", "state/agency", "v12_ohio_vector_update", "documented_program", "moderate", "real", "verified", "Ohio reports summer/fall surveillance timing; this is not a complete seasonal effort series."],
]

SURV_COLUMNS = [
    "record_id", "year", "vector_group", "species_or_vector", "pathogen", "surveillance_program",
    "surveillance_method", "geographic_area", "geographic_scale", "sampling_effort",
    "detection_status", "observed_value", "units", "source_id", "evidence_status",
    "confidence", "uncertainty_notes", "notes",
]

HAB_COLUMNS = [
    "association_id", "vector_or_group", "association_type", "environment_or_host",
    "relationship_description", "season_or_period", "geographic_scale", "evidence_status",
    "source_id", "confidence", "notes",
]
HAB_ROWS = [
    ["HAB-001", "Culex pipiens", "presence_and_habitat", "stagnant water, catch basins, ditches, containers with organic matter", "Ohio source documents widespread presence and these breeding contexts.", "warm season; twilight adult activity", "Ohio / species page", "documented", "v12_ohio_mosquitoes", "high", "Sampling effort and abundance are not supplied."],
    ["HAB-002", "Culex pipiens", "host_ecology", "birds; humans and dogs as accepted hosts", "Bird preference and broader host context are documented; this is not contact or infection evidence.", "spring/early summer bird context; seasonal shift discussed by OSU", "Ohio / species ecology", "documented", "v12_osu_culex", "moderate", "No host-contact rate is estimated."],
    ["HAB-003", "Aedes albopictus", "container_habitat", "tires, plastic containers, treeholes, clogged gutters", "Ohio and Indiana sources identify artificial/natural container habitats.", "warm season; day activity in shade", "Ohio/Indiana regional", "documented", "v12_ohio_mosquitoes", "high", "Container presence is not a local abundance or contact estimate."],
    ["HAB-004", "Aedes albopictus", "development_temperature", "water-holding container lifecycle", "Indiana states that the 7–10 day lifecycle can take less time during high temperatures.", "warm-season development", "Indiana species page", "documented", "v12_in_ae_albopictus", "moderate", "No thermal threshold or suitability surface is modeled."],
    ["HAB-005", "Aedes japonicus", "container_and_forest_edge", "natural/artificial containers, forest/stream study sites", "Ohio and Michigan studies document container-associated field surveillance.", "study-period dependent", "Ohio/Michigan study areas", "documented", "v12_ohio_ae_japonicus", "moderate", "Trap composition is not regional abundance."],
    ["HAB-006", "Aedes triseriatus", "woodland_treehole", "treeholes, wooded areas, parks, artificial containers", "Ohio source documents distribution and habitat association.", "day activity in shady conditions", "Ohio / species page", "documented", "v12_ohio_mosquitoes", "high", "No exact wooded occurrence points are mapped."],
    ["HAB-007", "Ixodes scapularis", "questing_habitat", "grasses, shrubs, forest/edge paths and host interface", "CDC describes questing and broad eastern distribution.", "spring/summer/fall; above-freezing winter adult context", "contiguous U.S. / regional", "documented", "v12_cdc_ticks_live", "moderate", "Broad habitat context is not a local range or abundance estimate."],
    ["HAB-008", "Dermacentor variabilis", "terrestrial_edge", "grass and shrub terrestrial habitats", "CDC documents broad eastern distribution and spring/summer biting context.", "spring/summer", "eastern U.S. / regional", "documented", "v12_cdc_dvariabilis", "moderate", "No core-county status table is ingested."],
    ["HAB-009", "mosquitoes", "seasonality", "warm-season air and water conditions", "Ohio describes mosquito activity usually May through October; CDC WNV page describes summer through fall activity.", "May–October / summer–fall", "Ohio/United States", "documented", "v12_ohio_mosquitoes", "high", "Seasonality is not a daily abundance curve."],
    ["HAB-010", "ticks", "seasonality", "temperature and host-seeking conditions", "CDC identifies spring, summer, and fall activity with above-freezing winter adult context for Ixodes.", "spring–fall; winter exception", "contiguous U.S. / regional", "documented", "v12_cdc_ixodes", "high", "No activity probability is estimated."],
    ["HAB-011", "mosquitoes", "precipitation_hydrology", "temporary standing water, wetlands, ditches, floodplain and drainage context", "Source-supported habitat logic is cross-linked to accepted hydrology; spatial vector response remains an inference.", "event and season dependent", "wetland/watershed generalized", "documented_plus_inferred", "phase1_hydrology_context", "moderate", "No continuous habitat or abundance surface is generated."],
    ["HAB-012", "ticks", "host_ecology", "deer, small mammals, birds, and other vertebrate hosts", "Host-seeking and life-stage context are retained from CDC tick ecology sources.", "life-stage and season dependent", "regional ecology", "documented_context", "v12_cdc_ticks_live", "moderate", "Host presence is not human-vector contact."],
    ["HAB-013", "mosquitoes", "surveillance_methods", "CDC light, gravid, BG-Sentinel, ovicup, and resting traps", "CDC describes different target taxa/life stages and trap uses.", "method-dependent", "surveillance-method context", "documented", "v12_cdc_mosquito_traps", "high", "Trap counts are not comparable without effort and design harmonization."],
    ["HAB-014", "Aedes japonicus", "study_composition", "gravid-trap and other trap collections in Wooster", "Ae. japonicus dominated the cited Wooster gravid-trap collection; the observation is study- and trap-specific.", "2021 field study", "Wooster, northeastern Ohio", "documented_study", "v12_ohio_ae_japonicus", "high", "The record explicitly does not become a regional abundance index."],
    ["HAB-015", "Culex pipiens", "temperature_and_overwintering", "seasonal emergence, diapause, and larval development", "OSU describes temperature-linked larval duration and overwintering/emergence context.", "spring emergence; late-summer/autumn diapause context", "Ohio / species ecology", "documented", "v12_osu_culex", "moderate", "No phenology model is fitted."],
]

UNC_COLUMNS = ["uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"]
UNC_ROWS = [
    ["VUNC-001", "VEC-001", "presence_vs_abundance", "Ohio presence and habitat documentation do not quantify local abundance.", "open", "v12_ohio_mosquitoes", "high", "Presence != abundance."],
    ["VUNC-002", "VEC-004", "study_generalization", "Wooster and Michigan study findings are not a Western Basin-wide range or abundance estimate.", "open", "v12_ohio_ae_japonicus", "high", "Study detection and trap composition retain local scope."],
    ["VUNC-003", "VEC-006", "tick_no_records", "CDC no-record county status is not evidence of tick absence.", "qualified", "v12_cdc_tick_sets", "high", "Detection != establishment; no records != absence."],
    ["VUNC-004", "VEC-006", "county_scale", "CDC county status does not resolve precise local distribution within a county.", "open", "v12_cdc_tick_sets", "high", "County record != precise local distribution."],
    ["VUNC-005", "VEC-015", "mosquito_effort", "Ohio pooled counts do not provide comparable county-level trap effort or species composition.", "open", "v12_ohio_vector_update", "high", "Sampling effort != abundance."],
    ["VUNC-006", "VEC-016", "program_coverage", "Michigan surveillance totals reflect participating jurisdictions and program methods, not uniform statewide coverage.", "open", "v12_mi_annual_2023", "high", "Coverage and methods vary."],
    ["VUNC-007", "VEC-017", "state_effort", "Indiana 2026 positive-county summary does not report comparable sampling effort or species-level counts.", "open", "v12_in_wnv_2026", "high", "Detection status cannot be converted to abundance."],
    ["VUNC-008", "VEC-019", "pathogen_health_boundary", "A positive mosquito pool or tick pathogen record is not a human case, infection, clinical disease, or local transmission proof.", "qualified", "v12_cdc_wnv_data", "high", "Health boundary is explicit."],
    ["VUNC-009", "VEC-020", "case_geography", "Human case county-of-residence data are not necessarily exposure or infection location.", "qualified", "v12_cdc_lyme", "high", "Reported human case != local transmission."],
    ["VUNC-010", "VEC-008", "held_geometry", "Great Black Swamp remains C — HOLD / noncanonical and is not used as a vector habitat polygon.", "open", "phase6_ecology_context", "high", "Toledo intake-coordinate discrepancy remains unresolved."],
]

DEPENDENCY_COLUMNS = [
    "dependency_id", "object_a", "object_b", "system_a", "system_b", "relationship_type",
    "documented_or_inferred", "relationship_basis", "spatial_scale", "evidence_strength",
    "source_id", "confidence", "reality_status", "canon_status", "notes",
]
DEPENDENCY_ROWS = [
    ["VDE-001", "temperature", "mosquito_seasonal_development", "climate", "vector_ecology", "seasonal_development", "documented", "documented_relationship", "station/regional", "moderate", "v12_osu_culex", "moderate", "real", "verified", "Temperature affects development timing in cited species ecology; no regional thermal model."],
    ["VDE-002", "temperature", "Aedes_lifecycle", "climate", "vector_ecology", "seasonal_development", "documented", "documented_relationship", "regional", "moderate", "v12_in_ae_albopictus", "moderate", "real", "verified", "Indiana reports a shorter lifecycle during high temperatures; no threshold surface."],
    ["VDE-003", "temperature", "Ixodes_activity", "climate", "vector_ecology", "seasonal_development", "documented", "documented_relationship", "regional", "moderate", "v12_cdc_ixodes", "moderate", "real", "verified", "Above-freezing winter adult questing context is not an activity probability."],
    ["VDE-004", "precipitation", "temporary_standing_water", "climate", "hydrology", "habitat_opportunity", "documented_plus_inferred", "physical_plausibility_plus_source_habitat", "station/wetland/watershed", "moderate", "phase1_hydrology_context", "limited", "real", "inferred", "Precipitation can create or replenish water-holding habitat; project relationship is qualitative."],
    ["VDE-005", "standing_water", "mosquito_habitat", "hydrology", "vector_ecology", "habitat_association", "documented", "documented_relationship", "wetland/ditch/container", "strong", "v12_ohio_mosquitoes", "high", "real", "verified", "Standing-water habitat association is distinct from abundance."],
    ["VDE-006", "wetlands", "mosquito_habitat", "ecology", "vector_ecology", "habitat_interface", "documented_plus_inferred", "accepted_context_plus_source_habitat", "wetland/watershed", "moderate", "phase6_ecology_context", "moderate", "real", "inferred", "Accepted wetland context is generalized and does not mark vector detections."],
    ["VDE-007", "urban_containers", "Aedes_albopictus", "settlement", "vector_ecology", "container_habitat", "documented", "documented_relationship", "urban/suburban", "strong", "v12_ohio_mosquitoes", "high", "real", "verified", "Containers support habitat association; no parcel inventory or local abundance."],
    ["VDE-008", "urban_containers", "Aedes_japonicus", "settlement", "vector_ecology", "container_habitat", "documented", "documented_relationship", "study-area/generalized", "moderate", "v12_ohio_ae_japonicus", "moderate", "real", "verified", "Study-area container records are not a Western Basin distribution surface."],
    ["VDE-009", "forest_edge", "Ixodes_host_interface", "ecology", "vector_ecology", "questing_habitat", "documented", "documented_relationship", "forest/edge", "moderate", "v12_cdc_ticks_live", "moderate", "real", "verified", "Forest/edge habitat is a generalized host-seeking interface, not an exact route."],
    ["VDE-010", "forest_edge", "Aedes_triseriatus", "ecology", "vector_ecology", "woodland_habitat", "documented", "documented_relationship", "woodland/park", "moderate", "v12_ohio_mosquitoes", "moderate", "real", "verified", "Wooded habitat context is distinct from human contact."],
    ["VDE-011", "host_ecology", "mosquito_lifecycle", "ecology", "vector_ecology", "host_association", "documented", "documented_relationship", "regional ecology", "moderate", "v12_cdc_wnv_about", "moderate", "real", "verified", "Bird–mosquito context is retained without human infection or disease modeling."],
    ["VDE-012", "host_ecology", "tick_lifecycle", "ecology", "vector_ecology", "host_association", "documented", "documented_relationship", "regional ecology", "moderate", "v12_cdc_ticks_live", "moderate", "real", "verified", "Host ecology supports lifecycle context; host presence is not contact."],
    ["VDE-013", "population_concentration", "potential_contact_interface", "population_settlement", "vector_ecology", "potential_interface", "inferred", "project_system_inference", "county/place/generalized", "limited", "phase11_population_context", "limited", "real", "inferred", "Population concentration can identify a potential interface for planning; it does not establish contact or exposure."],
    ["VDE-014", "workplace_settlement", "potential_contact_interface", "population_mobility", "vector_ecology", "potential_interface", "inferred", "project_system_inference", "county/place/generalized", "limited", "phase11_population_context", "limited", "real", "inferred", "Workplace/residence context is not passenger surveillance, contact, or infection."],
    ["VDE-015", "mosquito_surveillance", "vector_detection", "surveillance", "vector_ecology", "detection_interface", "documented", "documented_program", "state/county/agency", "strong", "v12_ohio_vector_update", "high", "real", "verified", "Surveillance programs produce detection records with method and effort limitations."],
    ["VDE-016", "tick_surveillance", "Ixodes_county_status", "surveillance", "vector_ecology", "detection_interface", "documented", "documented_program", "county", "strong", "v12_cdc_tick_sets", "high", "real", "verified", "CDC status definitions retain established/reported/no-record and non-absence rules."],
    ["VDE-017", "vector_detection", "decision_interface", "surveillance", "governance", "information_to_decision", "inferred", "project_system_inference", "agency/county/state", "moderate", "phase10_governance_context", "limited", "real", "inferred", "Detection can inform decisions; monitoring is not control and does not guarantee complete detection."],
    ["VDE-018", "data_sensors", "surveillance_detection", "information", "surveillance", "observation_interface", "documented_plus_inferred", "accepted_context_plus_program_records", "station/program/county", "moderate", "phase4_data_context", "moderate", "real", "inferred", "Observation methods and coverage shape detection; no completeness claim."],
    ["VDE-019", "climate_hazards", "seasonal_habitat_context", "climate", "vector_ecology", "environmental_driver", "documented_plus_inferred", "accepted_context_plus_source_habitat", "station/county/wetland", "moderate", "phase9_climate_context", "limited", "real", "inferred", "Accepted climate observations are cross-linked without future range or hazard-surface modeling."],
    ["VDE-020", "hydrography_wetlands", "standing_water_context", "hydrology", "vector_ecology", "environmental_driver", "accepted_context_plus_inferred", "accepted_layer_plus_physical_plausibility", "watershed/wetland", "moderate", "phase1_hydrology_context", "limited", "real", "inferred", "Hydrography is not a mosquito occurrence layer."],
    ["VDE-021", "ecology_landscape", "host_habitat_context", "ecology", "vector_ecology", "habitat_interface", "accepted_context_plus_inferred", "accepted_layer_plus_ecological_reasoning", "regional/forest/wetland", "moderate", "phase6_ecology_context", "limited", "real", "inferred", "Ecology context is not a host-density or vector-abundance model."],
    ["VDE-022", "environmental_health_pathway", "potential_contact_interface", "environmental_health", "vector_ecology", "health_boundary", "inferred", "boundary_crosswalk", "regional/pathway", "limited", "phase7_health_context", "high", "real", "verified", "Potential vector contact interface is not exposure, dose, infection, illness, or disease."],
    ["VDE-023", "positive_vector_pool", "human_case_context", "vector_surveillance", "environmental_health", "separation_rule", "documented_boundary", "surveillance_boundary", "county/program", "strong", "v12_cdc_wnv_data", "high", "real", "verified", "Positive vector pool and reported human case remain separate observations."],
    ["VDE-024", "sampling_effort", "detection_status", "surveillance", "data_quality", "effort_detection_boundary", "documented_boundary", "surveillance_methodology", "program/county", "strong", "v12_cdc_mosquito_traps", "high", "real", "verified", "Sampling effort is not abundance and non-detection is not absence."],
    ["VDE-025", "county_record", "local_distribution", "surveillance", "spatial_scale", "scale_boundary", "documented_boundary", "CDC county caveat", "county/local", "strong", "v12_cdc_tick_sets", "high", "real", "verified", "County record is not precise local distribution."],
    ["VDE-026", "reported_human_case", "local_transmission", "environmental_health", "public_health", "case_transmission_boundary", "documented_boundary", "CDC case-geography caveat", "county of residence", "strong", "v12_cdc_lyme", "high", "real", "verified", "Reported case is not local transmission without supporting evidence."],
    ["VDE-027", "surveillance_program", "control_or_response", "governance", "vector_management", "monitoring_control_boundary", "documented_boundary", "accepted governance distinction", "agency/program", "strong", "phase10_governance_context", "high", "real", "verified", "Surveillance and monitoring do not by themselves establish control effectiveness."],
    ["VDE-028", "Great_Black_Swamp", "vector_habitat_polygon", "canon", "spatial_boundary", "hold_preservation", "documented_boundary", "accepted canon status", "historical/noncanonical", "strong", "phase6_ecology_context", "high", "real", "verified", "Held geometry is not used as a vector habitat polygon."],
]

MATRIX_COLUMNS = [
    "object_id", "object_type", "object_name", "temperature_relationship", "precipitation_hydrology",
    "wetland_standing_water", "urban_container", "forest_edge_host", "host_ecology",
    "population_contact_interface", "surveillance_detection", "governance_decision_interface",
    "spatial_scale_certainty", "temporal_certainty", "notes",
]
MATRIX_ROWS = [
    ["DOBJ-001", "ecological_interface", "Mosquito seasonal development", "moderate", "moderate", "moderate", "limited", "limited", "moderate", "not_applicable", "limited", "unknown", "moderate", "limited", "Qualitative matrix derived from documented biology and accepted environmental context; no abundance or probability score."],
    ["DOBJ-002", "ecological_interface", "Mosquito standing-water habitat", "limited", "strong", "strong", "moderate", "limited", "limited", "not_applicable", "limited", "unknown", "limited", "limited", "Habitat opportunity is not vector presence or abundance."],
    ["DOBJ-003", "ecological_interface", "Aedes container interface", "moderate", "moderate", "moderate", "strong", "limited", "limited", "limited", "limited", "unknown", "moderate", "limited", "Container habitat is documented; potential population interface is inferred and not contact."],
    ["DOBJ-004", "ecological_interface", "Ixodes forest/edge host interface", "moderate", "limited", "limited", "not_applicable", "strong", "moderate", "limited", "limited", "unknown", "moderate", "limited", "Broad tick habitat/host context; county status does not resolve local distribution."],
    ["DOBJ-005", "ecological_interface", "Host ecology and lifecycle", "limited", "limited", "limited", "limited", "moderate", "strong", "not_applicable", "limited", "unknown", "limited", "limited", "Host association is not human-vector contact, infection, or disease."],
    ["DOBJ-006", "human_interface", "Population concentration and potential contact interface", "limited", "limited", "limited", "limited", "limited", "limited", "moderate", "unknown", "limited", "limited", "limited", "Potential interface is an inference; no individual risk or contact model."],
    ["DOBJ-007", "surveillance_interface", "Vector surveillance detection", "limited", "limited", "limited", "limited", "limited", "limited", "not_applicable", "strong", "moderate", "limited", "moderate", "Detection depends on program, method, effort, and reporting; detection is not abundance or establishment."],
    ["DOBJ-008", "health_boundary", "Pathogen/vector/human-case separation", "not_applicable", "not_applicable", "not_applicable", "not_applicable", "not_applicable", "not_applicable", "limited", "moderate", "moderate", "moderate", "strong", "Positive vector pool, human case, contact, infection, and clinical disease remain separate states."],
]

DEPENDENCY_EVIDENCE_COLUMNS = ["evidence_id", "dependency_id", "claim_type", "claim_status", "source_id", "spatial_scale", "temporal_scope", "supported_statement", "not_supported_statement"]
DEPENDENCY_EVIDENCE_ROWS = [
    ["VEV-001", "VDE-001", "temperature_to_development", "documented", "v12_osu_culex", "species/Ohio", "current biology", "Temperature is described as affecting larval duration and seasonal emergence context.", "No regional development-rate model or abundance response."],
    ["VEV-002", "VDE-004", "precipitation_to_water", "documented_plus_inferred", "phase1_hydrology_context", "watershed/wetland", "current accepted context", "Water availability and drainage are accepted environmental context for standing-water interfaces.", "No vector count, habitat polygon, or causal precipitation response."],
    ["VEV-003", "VDE-007", "containers_to_Aedes", "documented", "v12_ohio_mosquitoes", "Ohio/Indiana regional", "current species context", "Artificial containers are documented Aedes habitat.", "No parcel-level container inventory or local abundance."],
    ["VEV-004", "VDE-009", "forest_edge_to_ticks", "documented", "v12_cdc_ticks_live", "broad regional", "current CDC ecology", "Questing on grasses/shrubs and host-associated edge context are documented.", "No exact movement route or neighborhood distribution."],
    ["VEV-005", "VDE-013", "population_to_contact_interface", "project_inference", "phase11_population_context", "county/place/generalized", "2026 accepted population context", "Population concentration is a potential interface for planning.", "No human-vector contact, exposure, infection, or disease score."],
    ["VEV-006", "VDE-015", "surveillance_to_detection", "documented", "v12_ohio_vector_update", "state/agency/county", "2025 surveillance summary", "Programs report trapping, pooling, and testing detections.", "No complete surveillance coverage or comparable abundance index."],
    ["VEV-007", "VDE-017", "detection_to_decision", "project_inference", "phase10_governance_context", "agency/county/state", "accepted governance context", "Information can enter a decision interface.", "Monitoring is not control or proof of response effectiveness."],
    ["VEV-008", "VDE-023", "pool_to_case_separation", "documented_boundary", "v12_cdc_wnv_data", "state/county program", "current surveillance framing", "CDC separates vector, animal, and human surveillance streams.", "A positive vector pool is not a human case or transmission proof."],
]

SURVEILLANCE_BASE_ROWS = [
    ["VS-001", "2025", "mosquito", "species not specified in source", "West Nile virus", "Ohio Department of Health and local partners", "traps; pooled mosquito samples; laboratory testing", "Ohio; 42 counties with positive pools", "state/county", "11,980 pooled samples from 58 agencies in 49 counties", "positive mosquito pools detected in 42 counties", "42", "counties", "v12_ohio_vector_update", "documented_surveillance", "high", "Species composition and comparable county trap effort are not reported in the page summary.", "Positive pool counties are a detection record, not abundance, human contact, human infection, or local transmission proof."],
    ["VS-002", "2025", "mosquito", "species not specified in source", "not specified", "Ohio Department of Health and local partners", "traps and pooled mosquito testing", "Ohio statewide summary", "state/agency/county", "11,980 pooled samples; 58 agencies; 49 counties", "samples tested", "11980", "pooled samples", "v12_ohio_vector_update", "documented_surveillance", "high", "Pooled sample count is not a count of individual mosquitoes or abundance.", "Sampling effort is retained as reported and is not merged with other programs."],
    ["VS-003", "2025", "mosquito", "species not specified in source", "La Crosse virus", "Ohio Department of Health and local partners", "traps; pooled mosquito samples; laboratory testing", "Ohio; 4 counties with positive pools", "state/county", "1,297 pooled samples from 53 agencies in 44 counties", "positive mosquito pools detected in 4 counties", "4", "counties", "v12_ohio_vector_update", "documented_surveillance", "high", "Species composition and county-level effort are not reported in the summary.", "This is a separate pathogen stream from WNV and is not combined into an index."],
    ["VS-004", "2025", "human-case-context", "not applicable", "West Nile virus", "Ohio human surveillance", "reported human disease surveillance", "Ohio; county of residence", "county of residence", "Case reporting; sampling effort not applicable", "reported human cases in 23 counties; 45 total in cited map", "45", "reported cases", "v12_ohio_wnv_map", "contextual_human_observation", "high", "County of residence is not county of exposure or infection; page data are not a vector record.", "Context only; not a human-vector contact record or local transmission finding."],
    ["VS-005", "2023", "mosquito", "species not specified in source", "West Nile virus", "Michigan MDHHS and local health departments", "local health-department mosquito sampling, identification, and laboratory testing", "Michigan; Kent and Ottawa among positive-pool counties", "state/participating counties", "6,351 mosquito pools tested", "124 WNV-positive pools", "124", "pools", "v12_mi_annual_2023", "documented_surveillance", "high", "Participating jurisdictions and species/effort details vary.", "Positive pools are not human cases, contact, infection, or disease incidence."],
    ["VS-006", "2023", "mosquito", "species not specified in source", "Eastern equine encephalitis virus", "Michigan MDHHS and local health departments", "local health-department mosquito sampling and laboratory testing", "Michigan participating jurisdictions", "state/participating counties", "6,351 mosquito pools tested in annual arbovirus summary", "4 EEE-positive pools", "4", "pools", "v12_mi_annual_2023", "documented_surveillance", "moderate", "The summary is not a uniform statewide abundance survey.", "Separate pathogen stream; no human-case or transmission inference."],
    ["VS-007", "2023", "mosquito", "species not specified in source", "Jamestown Canyon virus", "Michigan MDHHS and local health departments", "local health-department mosquito sampling and laboratory testing", "Michigan participating jurisdictions", "state/participating counties", "6,351 mosquito pools tested in annual arbovirus summary", "6 JCV-positive pools", "6", "pools", "v12_mi_annual_2023", "documented_surveillance", "moderate", "Species-level pool composition and effort distribution are not supplied.", "Separate pathogen stream; no human-case or transmission inference."],
    ["VS-008", "2023", "mosquito", "species not specified in source", "arbovirus group", "Michigan MDHHS and local health departments", "local health-department mosquito sampling and laboratory testing", "Michigan participating jurisdictions", "state/participating counties", "6,351 mosquito pools tested", "total mosquito pools tested", "6351", "pools", "v12_mi_annual_2023", "documented_surveillance", "high", "Annual total is a program denominator, not comparable abundance across programs.", "Retained as effort/context only."],
    ["VS-009", "2026", "mosquito", "species not specified in source", "West Nile virus", "Michigan MDHHS 2026 weekly arbovirus summary", "mosquito-pool testing", "Michigan; Kent (2) and Ottawa (1) positive pools", "state/county", "536 pools and 7,383 mosquitoes tested as of 2026-06-12", "3 WNV-positive pools", "3", "pools", "v12_mi_wnv", "documented_surveillance", "high", "Weekly summary is date-bounded and not a full-season total.", "Positive pool record only; no human-case or transmission inference."],
    ["VS-010", "2026", "mosquito", "species not specified in source", "Jamestown Canyon virus", "Michigan MDHHS 2026 weekly arbovirus summary", "mosquito-pool testing", "Michigan; Kent positive pool", "state/county", "536 pools and 7,383 mosquitoes tested as of 2026-06-12", "1 JCV-positive pool", "1", "pool", "v12_mi_wnv", "documented_surveillance", "moderate", "Weekly summary is date-bounded and species-level effort is not reported.", "Separate pathogen stream; no human-case or transmission inference."],
    ["VS-011", "2023", "mosquito", "Aedes albopictus and Aedes aegypti", "not specified", "Michigan MDHHS, Kent County Health Department and partners", "property detection; enhanced trapping; control response", "Kent County property", "county/property", "Enhanced trapping reported; trap count not reported", "detected at a local property in Aug–Sep 2023; retained as program context", "", "detection record", "v12_mi_annual_2023", "documented_detection", "high", "The source describes first Kent County detection and enhanced trapping, not a county-wide range.", "Detection is not establishment, abundance, or a continuous distribution."],
    ["VS-012", "2026", "mosquito", "species not specified in release", "West Nile virus", "Indiana Department of Health", "mosquito testing", "Indiana; 33 counties", "state/county", "Sampling effort not specified in release", "mosquitoes tested positive in 33 counties", "33", "counties", "v12_in_wnv_2026", "documented_surveillance", "moderate", "No comparable county effort or species breakdown is supplied.", "Positive mosquitoes are not human cases or local transmission proof."],
    ["VS-013", "2026", "human-case-context", "not applicable", "West Nile virus", "Indiana human surveillance", "reported human disease surveillance", "Allen County, Indiana; county of residence", "county of residence", "Case reporting; sampling effort not applicable", "first reported 2026 human case in Indiana", "1", "reported case", "v12_in_wnv_2026", "contextual_human_observation", "high", "Patient details are withheld and case geography is residence-based.", "Context only; not vector abundance, contact, infection probability, or local transmission proof."],
    ["VS-014", "2023", "mosquito", "Aedes albopictus", "not specified", "Indiana Department of Health", "distribution-map record; method/effort not reported", "Indiana; map includes northern and southern counties", "state/county", "Sampling effort not reported on page", "known distribution map record", "", "distribution record", "v12_in_ae_albopictus", "documented_distribution_context", "moderate", "Map was updated February 2023 and does not provide a continuous range or abundance.", "Presence/detection context is not establishment, abundance, or contact."],
    ["VS-015", "2023", "tick", "Ixodes scapularis", "not assessed in this record", "CDC ArboNET Tick Module", "county status table; underlying passive jurisdictional surveillance", "selected Western Basin core counties", "county", "County-specific collection effort not reported; status threshold is six or more ticks of one life stage or more than one life stage within 12 months", "see county status rows VS-016 onward", "", "county status", "v12_cdc_tick_sets", "documented_surveillance", "high", "The table explicitly says no records are not absence and status is cumulative.", "Program-level method record; county rows retain their own status and scale."],
    ["VS-016", "2023", "tick", "Ixodes scapularis", "not assessed in this record", "CDC ArboNET Tick Module", "county status table", "Allen County, IN", "county", "County effort not reported; threshold-based status", "established", "", "county status", "v12_cdc_ixodes", "documented_surveillance", "high", "Established means CDC status threshold was met; not an abundance estimate.", "County record is not precise local distribution."],
    ["VS-017", "2023", "tick", "Ixodes scapularis", "not assessed in this record", "CDC ArboNET Tick Module", "county status table", "DeKalb County, IN", "county", "County effort not reported; threshold-based status", "established", "", "county status", "v12_cdc_ixodes", "documented_surveillance", "high", "Established means CDC status threshold was met; not an abundance estimate.", "County record is not precise local distribution."],
    ["VS-018", "2023", "tick", "Ixodes scapularis", "not assessed in this record", "CDC ArboNET Tick Module", "county status table", "Steuben County, IN", "county", "County effort not reported; threshold-based status", "established", "", "county status", "v12_cdc_ixodes", "documented_surveillance", "high", "Established means CDC status threshold was met; not an abundance estimate.", "County record is not precise local distribution."],
]


def citation_block() -> str:
    return "\n## Sources\n\n" + "\n".join(f"[{i}] {url}" for i, url in enumerate(CITATION_URLS, 1)) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(paths: list[Path]) -> dict[str, dict[str, object]]:
    return {str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in paths}


def assert_rows(name: str, rows: list[list[str]], columns: list[str]) -> None:
    assert all(len(row) == len(columns) for row in rows), name


def xlsx_sheet_rows(path: Path, sheet_name: str) -> list[dict[str, str]]:
    """Read the small public XLSX without adding an optional parser dependency."""
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["main"])) for si in root.findall("main:si", ns)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        target = None
        for sheet in workbook.findall("main:sheets/main:sheet", ns):
            if sheet.attrib.get("name") == sheet_name:
                target = rel_map[sheet.attrib[f"{{{ns['rel']}}}id"]]
                break
        assert target, sheet_name
        sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
        root = ET.fromstring(archive.read(sheet_path))
        rows: list[dict[str, str]] = []
        for row in root.findall(".//main:row", ns):
            values: dict[str, str] = {}
            for cell in row.findall("main:c", ns):
                value = cell.find("main:v", ns)
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared[int(text)]
                ref = cell.attrib.get("r", "")
                column = re.match(r"[A-Z]+", ref)
                if column:
                    values[column.group(0)] = text.strip()
            rows.append(values)
        return rows


def tick_status_rows() -> list[list[str]]:
    rows = xlsx_sheet_rows(TICK_XLSX, "Ixodes records 2023")
    header = next(i for i, row in enumerate(rows) if row.get("A") == "FIPSCode")
    selected: list[list[str]] = []
    for row in rows[header + 1:]:
        fips = row.get("A", "")
        if fips not in CORE_COUNTIES:
            continue
        state, county = CORE_COUNTIES[fips]
        status = row.get("D", "")
        selected.append([
            f"VS-TICK-{fips}", "2023", "tick", "Ixodes scapularis", "not assessed in this record",
            "CDC ArboNET Tick Module", "county status table", f"{county} County, {state}", "county",
            "County-specific collection effort not reported; established threshold is six or more ticks of one life stage or more than one life stage within 12 months",
            status.lower() if status.lower() != "no records" else "no records (not absence)", "", "county status", "v12_cdc_ixodes", "documented_surveillance", "high",
            "The CDC table states that no records should not be interpreted as absence and that county status is cumulative.",
            "Established/reported/no-record status is a surveillance classification, not abundance or precise local distribution.",
        ])
    assert len(selected) == len(CORE_COUNTIES)
    return selected


def load_layers():
    huc8 = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wetlands = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flowlines = gpd.read_file(GPKG, layer="hydrography_physical")
    flowlines["geometry"] = flowlines.geometry.simplify(0.002, preserve_topology=False)
    return huc8, lake, wetlands, flowlines


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"id=\"p[0-9a-f]+\"", 'id="p12vector"', text)
    text = re.sub(r"url\(#p[0-9a-f]+\)", "url(#p12vector)", text)
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def save_map(fig: plt.Figure, base: Path) -> None:
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(base.with_suffix(".svg"))


def render_map38() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc8, lake, wetlands, flowlines = load_layers()
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.60, 0.78], facecolor="#e9e1ce")
    huc8.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.45)
    flowlines.plot(ax=ax, color="#4a8798", linewidth=0.30, alpha=0.55)
    anchors = [
        ("Ottawa NWR / wetland context", -83.14, 41.63, "#6b4b91", "^"),
        ("Maumee Bay wetland context", -83.22, 41.69, "#6b4b91", "^"),
        ("Lower Maumee hydrology context", -83.7127145, 41.5000526, "#2b7182", "s"),
    ]
    for label, x, y, color, marker in anchors:
        ax.scatter([x], [y], s=72, c=color, marker=marker, edgecolor="#f1eadc", linewidth=0.9, zorder=6)
        ax.text(x, y - 0.035, label, fontsize=7.0, color=color, ha="center", va="top", zorder=7)
    ax.text(-83.42, 41.77, "Western Lake Erie", fontsize=11, weight="bold", color="#235a68", ha="center")
    ax.text(-83.56, 41.43, "Maumee River / tributary structure", fontsize=8.5, color="#285f71", rotation=18, ha="center")
    ax.set_xlim(-84.55, -82.55)
    ax.set_ylim(40.9, 42.15)
    ax.set_axis_off()
    side = fig.add_axes([0.68, 0.06, 0.29, 0.86]); side.axis("off")
    side.text(0.03, 0.98, "MAP 38 — WESTERN BASIN\nVECTOR ECOLOGY BASELINE, 2026", va="top", fontsize=14.2, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.03, 0.855, "Generalized ecology and surveillance context over accepted water, wetland, hydrography, and regional system layers. Markers are context anchors, not vector collection locations or detections.", va="top", fontsize=8.4, color="#3f4645", linespacing=1.3)
    side.text(0.03, 0.72, "VECTOR GROUPS", fontsize=10, weight="bold", color="#17384b")
    bullets = [
        "Culex pipiens / restuans complex context",
        "Aedes albopictus and Aedes triseriatus",
        "Aedes japonicus — Ohio/Michigan study context",
        "Ixodes scapularis — CDC county-status context",
        "Dermacentor variabilis — broad eastern distribution context",
        "Wetland, standing-water, container, forest/edge, host, and seasonal interfaces",
    ]
    y = 0.685
    for bullet in bullets:
        side.text(0.05, y, "• " + bullet, fontsize=7.8, color="#3f4645", va="top", linespacing=1.2); y -= 0.047
    side.text(0.03, 0.39, "SURVEILLANCE BOUNDARY", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.36, "Ohio, Michigan, Indiana, CDC ArboNET/NNDSS, and CDC tick-status programs are retained with program, method, scale, effort, and uncertainty fields. Incompatible streams are not merged into abundance.", fontsize=7.7, color="#3f4645", va="top", linespacing=1.3)
    side.text(0.03, 0.19, "HEALTH BOUNDARY", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.16, "Presence ≠ abundance ≠ pathogen detection ≠ contact ≠ infection ≠ clinical disease. Positive vector pool ≠ human case. County record ≠ precise local distribution. No individual risk, disease forecast, or unsupported future range.", fontsize=7.6, color="#3f4645", va="top", linespacing=1.28)
    side.legend(handles=[
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#6b4b91", markersize=7, label="accepted wetland/ecology context"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#2b7182", markersize=7, label="accepted hydrology context"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="Lake / water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.01), frameon=False, fontsize=7.2)
    save_map(fig, MAP38_BASE)


def render_map39() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc8, lake, wetlands, flowlines = load_layers()
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc8.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.40)
    flowlines.plot(ax=ax, color="#4a8798", linewidth=0.30, alpha=0.50)
    # These are generalized conceptual interface anchors, not sample sites or routes.
    nodes = [
        ("temperature", -84.14, 41.94, "#c8643f"),
        ("standing water", -83.98, 41.25, "#2f7890"),
        ("wetlands", -83.17, 41.77, "#4c8a69"),
        ("urban containers", -83.54, 41.65, "#9a4f59"),
        ("forest / edge", -82.85, 41.27, "#6b4b91"),
        ("population interface", -83.35, 41.52, "#b26d32"),
        ("surveillance / decision", -83.72, 41.91, "#355f7d"),
    ]
    for label, x, y, color in nodes:
        ax.scatter([x], [y], s=250, facecolors="none", edgecolors=color, linewidth=1.7, zorder=6)
        ax.text(x, y, label.upper(), fontsize=6.5, color=color, ha="center", va="center", weight="bold", zorder=7)
    for (a, b) in [(0, 1), (1, 2), (2, 4), (3, 5), (4, 5), (5, 6), (0, 6)]:
        x1, y1 = nodes[a][1], nodes[a][2]; x2, y2 = nodes[b][1], nodes[b][2]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, linewidth=1.0, color="#6e6a60", alpha=0.45, connectionstyle="arc3,rad=0.08", zorder=4))
    ax.set_xlim(-84.55, -82.55); ax.set_ylim(40.9, 42.15); ax.set_axis_off()
    side = fig.add_axes([0.67, 0.055, 0.30, 0.88]); side.axis("off")
    side.text(0.03, 0.98, "MAP 39 — VECTOR / ENVIRONMENT /\nHUMAN-SYSTEM DEPENDENCIES, 2026", va="top", fontsize=13.2, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.03, 0.845, "Generalized qualitative interfaces. Rings and arrows are schematic relationships over regional context, not continuous vector abundance, contact, infection, transmission, or hazard surfaces.", va="top", fontsize=8.3, color="#3f4645", linespacing=1.3)
    side.text(0.03, 0.72, "DOCUMENTED RELATIONSHIPS", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.685, "• temperature → seasonal development\n• precipitation / standing water → habitat opportunity\n• containers → Aedes habitat\n• forest / edge → tick-host interface\n• host ecology → vector lifecycle\n• surveillance → detection interface", va="top", fontsize=7.7, color="#3f4645", linespacing=1.35)
    side.text(0.03, 0.43, "PROJECT INFERENCES", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.395, "• population concentration → potential interface\n• detection → decision/information interface\n• accepted climate, hydrology, ecology, health, governance, and data layers cross-linked at their native scales", va="top", fontsize=7.7, color="#3f4645", linespacing=1.35)
    side.text(0.03, 0.205, "NEGATIVE SCOPE", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.17, "No individual infection probability, disease incidence, hospitalization, mortality, personal exposure/dose, neighborhood disease-risk score, vulnerability/EJ score, unsupported future range, or Phase 13. Potential contact interface is not exposure, dose, infection, or disease; monitoring ≠ control; detection ≠ establishment; case ≠ local transmission.", va="top", fontsize=7.6, color="#3f4645", linespacing=1.28)
    save_map(fig, MAP39_BASE)


def report_texts(nodes: pd.DataFrame, edges: pd.DataFrame, surveillance: pd.DataFrame, habitat: pd.DataFrame, uncertainty: pd.DataFrame, dependencies: pd.DataFrame, matrix: pd.DataFrame, evidence: pd.DataFrame) -> dict[str, str]:
    tick = surveillance[surveillance.record_id.str.startswith("VS-TICK-")]
    established = int(tick.detection_status.eq("established").sum())
    reported = int(tick.detection_status.eq("reported").sum())
    no_records = int(tick.detection_status.str.startswith("no records").sum())
    ohio_tick = tick[tick.geographic_area.str.endswith(", OH")]
    mi_tick = tick[tick.geographic_area.str.endswith(", MI")]
    in_tick = tick[tick.geographic_area.str.endswith(", IN")]
    sources = citation_block()
    a_sources = """# Phase 12A Vector Ecology Baseline Sources

The baseline uses Ohio Department of Health species and surveillance pages.[1][2][3]

It also uses Ohio State University extension ecology.[4]

It uses Michigan MDHHS surveillance summaries.[7][8]

It also uses the Indiana Department of Health Aedes and WNV pages.[9][10]

It uses CDC mosquito surveillance-method guidance.[11][12]

It also uses CDC ArboNET/NNDSS context.[13][14]

It uses CDC tick distribution/status definitions.[15][16][17]

The CDC tick surveillance pages add species-specific status context.[18][19]

The CDC Lyme surveillance limitation page supplies case-geography context.[20]

Ohio records include state species/habitat context and a dated 2025 pooled-surveillance summary.[1][2] The Ohio human-case map is retained only as county-of-residence context.[3]

The cited Ohio Aedes japonicus study and Michigan establishment study are study-area evidence with trap and method limitations; their results are not generalized into a Western Basin abundance or continuous-range surface.[5][6]

Michigan 2023 and 2026 summaries retain program denominators, positive-pool counts, participating jurisdictions, and date limits.[7][8]

Indiana records retain the published county summary and Aedes distribution-map limitations.[9][10]

CDC mosquito-trap guidance is used to preserve trap/life-stage selectivity and sampling-effort limitations.[11][12]

CDC ArboNET and NNDSS pages establish separate vector, pathogen, animal, and human surveillance streams.[13][14]

CDC tick pages and the cached public 2023 Ixodes county workbook provide county status records for the selected core-county frame.[15][16][17]

The CDC blacklegged and American dog tick pages provide species-specific context.[18][19]

The original CDC data-set and blacklegged-tick pages are retained in the source registry. The actual workbook bytes were retrieved from https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx, a mirror that is not CDC-hosted, after the direct CDC binary URL returned HTTP 403 in this environment. No D. variabilis core-county workbook was ingested.

The accepted Phase 1 and Phase 6 layers provide generalized hydrology, wetland, hydrography, ecological, and landscape context without adding vector detections. Great Black Swamp remains C — HOLD / noncanonical.
""" + sources
    a_assumptions = f"""# Phase 12A Vector Ecology Baseline Assumptions

## Product boundary

This is a compact factual 2026 vector ecology and surveillance baseline, not an infectious-disease module. It contains {len(nodes)} nodes, {len(edges)} ecology relationships, {len(surveillance)} surveillance/context records, {len(habitat)} habitat/seasonality/host associations, and {len(uncertainty)} uncertainty records. The source registry contains {len(SOURCE_ROWS)} records.

## Evidence ladder

The package keeps vector presence, vector abundance, pathogen detection in vector, human-vector contact, human infection, and clinical disease separate. It also keeps sampling effort separate from abundance; detection separate from establishment; county record separate from precise local distribution; positive vector pool separate from human case; and reported human case separate from local transmission unless supported.

Mosquito program totals are retained with their program, method, geographic scale, denominator, and missing effort fields. Ohio, Michigan, Indiana, and CDC tick products are not combined into a pseudo-abundance index. Tick no-records are retained as no-records-not-absence. CDC established status is retained as a threshold-based classification and not as a count or density.

## Spatial representation

Map 38 uses accepted generalized water/wetland/hydrography context anchors. It does not plot vector collection locations, sensitive host locations, exact tick movement, or continuous vector distributions. County status rows are tabular county-scale surveillance records and do not resolve local placement.

## Time and source limitations

The baseline label is 2026, but each record retains its source year or surveillance period. Included observations span 2023–2026 because the most recent public program/source releases differ by product. A recent source is not relabeled as a 2026 observation. The cached CDC Ixodes workbook covers records through 2023.

## Exclusions

No individual infection probability, disease-incidence forecast, hospitalization, mortality, personal exposure/dose, neighborhood disease-risk score, vulnerability/EJ score, unsupported disease attribution, unsupported future range, full infectious-disease dynamics, biosecurity, Phase 12C, Phase 13, or accepted/frozen prior-artifact modification is included. Human-case rows are contextual observations only.
"""
    a_findings = f"""# Phase 12A Vector Ecology Baseline Findings, 2026

## Documented vector ecology

FACT: Ohio's public-health species page describes 59 mosquito species in Ohio and identifies only a subset as disease vectors; it documents widespread Ohio context for Culex pipiens, Ohio presence/habitat context for Aedes albopictus and Aedes triseriatus, and usual Ohio mosquito activity from May through October.[1]

FACT: Ohio's Northern house mosquito fact sheet describes Culex pipiens across urban, suburban, and rural habitats, with calm/stagnant water, catch basins, ditches, containers, bird host preference, temperature-linked larval duration, and overwintering/diapause context.[4]

FACT: Indiana's Aedes albopictus page identifies a distribution map with records in southern and northern Indiana counties, container habitat, daytime/shade activity, and a lifecycle that can be shorter during high temperatures.[9]

FACT: The Wooster study reported Aedes japonicus as the dominant species in its 2021 gravid-trap collections and used multiple trap types plus morphological/molecular identification.[5] This is a study-specific trap-composition observation, not a Western Basin abundance estimate. Michigan research separately documents establishment and container-habitat colonization in a study setting.[6]

FACT: CDC describes Ixodes scapularis as broadly distributed across the eastern United States, with spring/summer/fall activity and above-freezing winter adult questing context.[15][18]

FACT: CDC describes Dermacentor variabilis as broadly distributed east of the Rocky Mountains with highest biting context in spring and summer.[19]

## Surveillance records

FACT: Ohio's 2025 update reports 11,980 pooled mosquito samples from 58 agencies in 49 counties and WNV-positive mosquito pools from 42 counties.[2] It separately reports 1,297 pooled samples from 53 agencies in 44 counties for a La Crosse virus summary, with positive pools in four counties.[2]

FACT: The Ohio 2025 human-case map reports 45 WNV cases and identifies county of residence as the geographic basis.[3] This row is contextual only: a human case is not a vector record, a positive pool, or proof of local transmission.

FACT: Michigan's 2023 annual summary reports 6,351 mosquito pools tested, including 124 WNV-positive, four EEE-positive, and six JCV-positive pools.[7] The 2026 weekly summary context reports 536 pools and 7,383 mosquitoes tested, three WNV-positive pools, and one JCV-positive pool as of its dated update.[8]

FACT: Indiana's 2026 release reports positive mosquito tests in 33 counties and one first reported human WNV case in an Allen County resident.[10] The release does not provide comparable county-level sampling effort or species counts.

FACT: CDC trap guidance identifies different target taxa and life stages for different traps, so trap collections are not interchangeable abundance samples.[11]

FACT: CDC's tick-data catalog identifies separate surveillance dashboards and data sets; catalog availability does not establish uniform county sampling.[16]

FACT: The CDC Ixodes workbook records {established} established, {reported} reported, and {no_records} no-records-not-absence statuses across the {len(tick)} selected core counties through 2023.[17][18]

FACT: Within the frame, Ohio has {int(ohio_tick.detection_status.eq('established').sum())} established, {int(ohio_tick.detection_status.eq('reported').sum())} reported, and {int(ohio_tick.detection_status.str.startswith('no records').sum())} no-records-not-absence statuses; Michigan has {int(mi_tick.detection_status.eq('established').sum())} established and {int(mi_tick.detection_status.str.startswith('no records').sum())} no-records-not-absence; Indiana has {int(in_tick.detection_status.eq('established').sum())} established statuses.[17][18]

## Principal interpretation

INFERENCE: The regionally supported ecology is heterogeneous: Culex and container-associated Aedes connect urban/developed water-holding habitats with seasonal mosquito activity; wetland, ditch, floodplain, and standing-water context creates a separate habitat interface; forest/edge and host ecology matter for ticks and woodland mosquitoes; and temperature is a seasonal-development driver. These are documented relationships plus clearly labeled project interfaces, not a basin-wide abundance result.

INFERENCE: Surveillance is strongest as a detection and decision interface, not as a comparable abundance measure. Program denominators, trap types, participating jurisdictions, county status rules, and reporting periods differ. Non-detection and CDC no-records remain uncertainty, not absence.

## Health boundary and limitations

UNCERTAINTY: The package does not estimate human-vector contact, infection, clinical disease, disease incidence, or local transmission.

CDC distinguishes vector, pathogen, animal, and human surveillance streams.[12][13][14]

Human case geography may be county of residence rather than exposure location.[20]

UNCERTAINTY: Species-specific mosquito counts, comparable trap effort, larval habitat inventories, tick collection effort by county, local establishment timing, pathogen prevalence, host density, and fine-scale spatial distribution remain incomplete or out of scope. The data do not support a continuous risk surface.
""" + sources
    a_qa = f"""# Phase 12A Vector Ecology Baseline QA

The package contains {len(nodes)} nodes, {len(edges)} edges, {len(surveillance)} surveillance/context rows, {len(habitat)} habitat associations, {len(uncertainty)} uncertainty rows, {len(SOURCE_ROWS)} source records, and Map 38 PNG/SVG.

The Python validator checks exact schemas, IDs, source references, year/method/scale/effort/detection fields, tick status definitions, presence-versus-abundance notes, vector/pathogen/human-case separation, detection-versus-establishment notes, no-records non-absence, county-scale limits, negative scope, map text/readability, the Phase 12A manifest, the cached raw workbook, all Phase 1–11 freeze manifests, active holds, and absence of Phase 12C/Phase 13 artifacts.

The independent R validator re-reads the generated tables, recomputes counts, checks source IDs and controlled vocabularies, checks the raw workbook and manifest hashes through a separate code path, verifies Map 38, and asserts the health boundary and no unsupported future range.

No individual infection probability, disease forecast, hospitalization, mortality, dose, neighborhood risk score, vulnerability/EJ score, unsupported human transmission claim, or continuous abundance/risk surface is included.
"""
    b_sources = """# Phase 12B Vector / Environment / Human-System Dependency Sources

Phase 12B reuses the Phase 12A source registry for vector ecology, habitat, seasonality, and surveillance methods. It cross-links those records to accepted Phase 1 hydrology/wetlands, Phase 4 data/sensors, Phase 6 ecology, Phase 7 environmental-health, Phase 9 climate/hazards, Phase 10 governance, and Phase 11 population/settlement layers.

The documented relationship families use Ohio species and ecology sources.[1][4][5]

State surveillance updates and contextual human-case records are retained separately.[2][3][10]

They also use Michigan surveillance and Indiana species sources.[7][8][9]

The Michigan establishment study is retained as study-specific evidence.[6]

CDC mosquito and vector-pathogen sources provide method and lifecycle context.[11][12][14]

The CDC ArboNET page provides separate surveillance-stream context.[13]

CDC tick distribution and status sources provide tick-scale and surveillance definitions.[15][16][17]

CDC tick surveillance and case-geography sources provide additional boundary context.[18][19][20]

Population concentration, detection-to-decision, and cross-system information relationships are explicitly project inferences rather than source-reported contact, infection, control, or disease relationships.
""" + sources
    b_assumptions = f"""# Phase 12B Vector / Environment / Human-System Dependency Assumptions

The dependency layer contains {len(dependencies)} qualitative dependency rows, {len(matrix)} matrix rows, and {len(evidence)} claim-level evidence crosswalk rows. It does not modify the Phase 12A factual working baseline or any accepted/frozen Phase 1–11 artifact.

Documented relationships are separated from project inference. The matrix uses qualitative labels only: strong, moderate, limited, unknown, and not_applicable. UNKNOWN is not LOW; dependence is not vulnerability; potential contact interface is not exposure, dose, infection, or disease.

The model cross-links temperature, precipitation/standing water, wetlands, urban containers, forest/edge habitat, host ecology, population/settlement concentration, surveillance detection, governance/decision interface, and accepted data/sensor context at generalized native scales. It does not assign residents to vector contact or exposure, map exact vector routes, or infer control effectiveness from monitoring.

## Exclusions

No individual infection probability, disease-incidence forecast, hospitalization, mortality, personal exposure/dose, neighborhood disease-risk score, vulnerability/EJ score, unsupported pathogen attribution, unsupported future range, full infectious-disease dynamics, biosecurity, Phase 12C, Phase 13, or continuous risk surface is created. Human cases remain contextual only.
"""
    b_findings = f"""# Phase 12B Vector / Environment / Human-System Dependency Findings, 2026

## Documented relationships

FACT: The source-grounded relationship set supports temperature-to-seasonal-development context for Culex and Aedes, and seasonal activity context for Ixodes.[4][9][18]

FACT: It supports precipitation/standing-water-to-habitat opportunity and container-to-Aedes habitat.[1][4][5]

FACT: It supports forest/edge-to-tick questing context and the broader tick distribution/status distinction.[15][17][19]

FACT: It supports host ecology-to-vector lifecycle context through mosquito and tick biology references.[11][14]

FACT: It supports surveillance-program-to-detection interfaces in Ohio and Michigan.[2][7]

FACT: Indiana and CDC surveillance sources document additional program and method context.[10][12][16]

FACT: The accepted hydrology/wetland, ecology, climate, and data layers provide generalized environmental and observation context at watershed, wetland, station, regional, and program scales. They do not create vector detections or a continuous vector surface.

FACT: Ohio and Michigan study sources remain study- or program-specific and are not generalized into a Western Basin abundance surface.[5][6][7]

FACT: The CDC mosquito page distinguishes vectors from nuisance mosquitoes, while CDC tick and Lyme pages distinguish vector ecology from human case geography.[11][20]

FACT: Michigan's current public program page is retained as surveillance context rather than a species-abundance dataset.[8]

## Project inferences

INFERENCE: Population and settlement concentration can identify a potential human-system interface for surveillance planning, but population presence does not establish human-vector contact, exposure, infection, or disease. The Phase 11 county/place/employment scales remain distinct from vector sampling scales.

INFERENCE: Surveillance detections can feed a governance/data decision interface, but detection depends on method, effort, program coverage, reporting, and geographic scale. Monitoring is not control, and a detection is not establishment or abundance.

INFERENCE: Climate, hydrology, ecology, environmental-health, governance, and data/sensor layers form a dependency network in which a missing observation is uncertainty rather than evidence of absence. These interfaces are qualitative and not a composite score.

## Health and surveillance boundary

FACT/BOUNDARY: Positive vector pools, tick pathogen records, and reported human cases remain separate surveillance products. A positive vector pool is not a human case.[3][10][13]

FACT/BOUNDARY: A reported case is not local transmission without supporting evidence, and a potential contact interface is not exposure, dose, infection, or clinical disease.[19][20]

UNCERTAINTY: The package cannot resolve fine-scale vector distribution, comparable abundance, sampling completeness, host density, contact rates, infection probability, clinical incidence, or local transmission. It therefore does not produce a neighborhood disease-risk surface.
""" + sources
    b_qa = f"""# Phase 12B Vector / Environment / Human-System Dependency QA

The package contains {len(dependencies)} dependency records, {len(matrix)} qualitative matrix rows, {len(evidence)} claim-level evidence rows, and Map 39 PNG/SVG. Phase 12A contains {len(nodes)} nodes and {len(surveillance)} surveillance/context records and is checked as an immutable working baseline.

The Python validator checks exact schemas, referential/controlled vocabularies, documented-versus-inferred fields, matrix labels, source references, the required relationship families, presence/abundance and pathogen/case boundaries, sampling-effort and spatial-scale caveats, no individual risk or vulnerability score, no unsupported future range, Map 39 integrity/text, Phase 12A artifact hashes, all Phase 1–11 freeze manifests, active holds, and absence of Phase 12C/Phase 13 content.

The independent R validator performs the same checks through a separate code path and independently verifies Phase 12A hashes, the Phase 12B manifest, source references, matrix values, map text, negative scope, and inherited holds.
"""
    return {
        "vector_ecology_sources.md": a_sources,
        "vector_ecology_assumptions.md": a_assumptions,
        "vector_ecology_findings.md": a_findings,
        "vector_ecology_qa.md": a_qa,
        "vector_dependency_sources.md": b_sources,
        "vector_dependency_assumptions.md": b_assumptions,
        "vector_dependency_findings.md": b_findings,
        "vector_dependency_qa.md": b_qa,
    }


def build_phase12a() -> dict[str, object]:
    assert TICK_XLSX.exists() and TICK_XLSX.stat().st_size > 1000
    for directory in (RAW, NETWORKS, ANALYSIS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    nodes = pd.DataFrame(NODE_ROWS, columns=NODE_COLUMNS)
    edges = pd.DataFrame(EDGE_ROWS, columns=EDGE_COLUMNS)
    surveillance = pd.DataFrame(SURVEILLANCE_BASE_ROWS + tick_status_rows(), columns=SURV_COLUMNS)
    habitat = pd.DataFrame(HAB_ROWS, columns=HAB_COLUMNS)
    uncertainty = pd.DataFrame(UNC_ROWS, columns=UNC_COLUMNS)
    for name, rows, columns in (
        ("nodes", NODE_ROWS, NODE_COLUMNS), ("edges", EDGE_ROWS, EDGE_COLUMNS),
        ("surveillance", SURVEILLANCE_BASE_ROWS, SURV_COLUMNS), ("habitat", HAB_ROWS, HAB_COLUMNS),
        ("uncertainty", UNC_ROWS, UNC_COLUMNS), ("sources", SOURCE_ROWS, SOURCE_BASE_COLUMNS),
        ("dependencies", DEPENDENCY_ROWS, DEPENDENCY_COLUMNS), ("matrix", MATRIX_ROWS, MATRIX_COLUMNS),
        ("evidence", DEPENDENCY_EVIDENCE_ROWS, DEPENDENCY_EVIDENCE_COLUMNS),
    ):
        assert_rows(name, rows, columns)
    sources = pd.DataFrame(SOURCE_ROWS, columns=SOURCE_BASE_COLUMNS)
    sources["retrieval_url"] = ""
    sources["retrieval_provenance"] = ""
    ixodes = sources["source_id"].eq("v12_cdc_ixodes")
    sources.loc[ixodes, "retrieval_url"] = "https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx"
    sources.loc[ixodes, "retrieval_provenance"] = "Actual workbook bytes retrieved from restoredcdc.org mirror; mirror is not CDC-hosted; direct CDC binary URL returned HTTP 403."
    nodes.to_csv(NETWORKS / "vector_ecology_nodes.csv", index=False)
    edges.to_csv(NETWORKS / "vector_ecology_edges.csv", index=False)
    surveillance.to_csv(ANALYSIS / "vector_surveillance_records.csv", index=False)
    habitat.to_csv(ANALYSIS / "vector_habitat_associations.csv", index=False)
    uncertainty.to_csv(ANALYSIS / "vector_ecology_uncertainty.csv", index=False)
    sources.to_csv(ANALYSIS / "vector_ecology_sources.csv", index=False)
    render_map38()
    texts = report_texts(nodes, edges, surveillance, habitat, uncertainty, pd.DataFrame(columns=DEPENDENCY_COLUMNS), pd.DataFrame(columns=MATRIX_COLUMNS), pd.DataFrame(columns=DEPENDENCY_EVIDENCE_COLUMNS))
    report_paths = []
    for name, text in texts.items():
        if name.startswith("vector_ecology_"):
            path = REPORTS / name
            path.write_text(text, encoding="utf-8", newline="\n")
            report_paths.append(path)
    artifacts = [
        NETWORKS / "vector_ecology_nodes.csv", NETWORKS / "vector_ecology_edges.csv",
        ANALYSIS / "vector_surveillance_records.csv", ANALYSIS / "vector_habitat_associations.csv",
        ANALYSIS / "vector_ecology_sources.csv", ANALYSIS / "vector_ecology_uncertainty.csv",
        MAP38_BASE.with_suffix(".png"), MAP38_BASE.with_suffix(".svg"), *report_paths,
        TICK_XLSX, CITATION_LEDGER,
    ]
    counts = {"nodes": len(nodes), "edges": len(edges), "surveillance_records": len(surveillance), "habitat_associations": len(habitat), "sources": len(sources), "uncertainties": len(uncertainty)}
    manifest = {"phase": "12A", "status": "implemented_validated_pending_sol_acceptance", "map_number": 38, "counts": counts, "artifacts": metadata(artifacts), "raw_inputs": {str(TICK_XLSX.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(TICK_XLSX), "bytes": TICK_XLSX.stat().st_size, "retrieval_note": "Original CDC data-set page: https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html; direct CDC binary URL returned HTTP 403; actual bytes retrieved from https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx, a mirror that is not CDC-hosted."}}, "phase12c_implemented": False, "phase13_implemented": False, "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}}
    A_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"nodes": nodes, "edges": edges, "surveillance": surveillance, "habitat": habitat, "uncertainty": uncertainty, "sources": sources, "manifest": manifest}


def build_phase12b(package: dict[str, object]) -> dict[str, object]:
    nodes = package["nodes"]; edges = package["edges"]; surveillance = package["surveillance"]; habitat = package["habitat"]; uncertainty = package["uncertainty"]; sources = package["sources"]
    a_manifest = json.loads(A_MANIFEST.read_text(encoding="utf-8"))
    for rel, meta in a_manifest["artifacts"].items():
        assert sha256(ROOT / rel) == meta["sha256"], rel
    dependencies = pd.DataFrame(DEPENDENCY_ROWS, columns=DEPENDENCY_COLUMNS)
    matrix = pd.DataFrame(MATRIX_ROWS, columns=MATRIX_COLUMNS)
    evidence = pd.DataFrame(DEPENDENCY_EVIDENCE_ROWS, columns=DEPENDENCY_EVIDENCE_COLUMNS)
    dependencies.to_csv(ANALYSIS / "vector_system_dependency_register.csv", index=False)
    dependencies.to_csv(NETWORKS / "vector_system_dependency_edges.csv", index=False)
    matrix.to_csv(ANALYSIS / "vector_system_dependency_matrix.csv", index=False)
    evidence.to_csv(ANALYSIS / "vector_dependency_evidence.csv", index=False)
    render_map39()
    texts = report_texts(nodes, edges, surveillance, habitat, uncertainty, dependencies, matrix, evidence)
    report_paths = []
    for name, text in texts.items():
        if name.startswith("vector_dependency_"):
            path = REPORTS / name
            path.write_text(text, encoding="utf-8", newline="\n")
            report_paths.append(path)
    artifacts = [
        ANALYSIS / "vector_system_dependency_register.csv", NETWORKS / "vector_system_dependency_edges.csv",
        ANALYSIS / "vector_system_dependency_matrix.csv", ANALYSIS / "vector_dependency_evidence.csv",
        MAP39_BASE.with_suffix(".png"), MAP39_BASE.with_suffix(".svg"), *report_paths,
    ]
    counts = {"dependency_register": len(dependencies), "dependency_edges": len(dependencies), "matrix_rows": len(matrix), "evidence_rows": len(evidence), "sources_reused": len(sources)}
    manifest = {"phase": "12B", "status": "implemented_validated_pending_sol_acceptance", "map_number": 39, "counts": counts, "artifacts": metadata(artifacts), "protected_12a_manifest": {"path": "reports/vector_ecology_baseline_manifest.json", "sha256": sha256(A_MANIFEST), "bytes": A_MANIFEST.stat().st_size}, "phase12c_implemented": False, "phase13_implemented": False, "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"}}
    B_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    working = {"phase": "12A/12B", "status": "implemented_validated_pending_sol_acceptance", "maps": [38, 39], "counts": {"12A": package["manifest"]["counts"], "12B": counts}, "phase12a_manifest": "reports/vector_ecology_baseline_manifest.json", "phase12b_manifest": "reports/vector_dependency_manifest.json", "phase12c_implemented": False, "phase13_implemented": False, "active_holds_preserved": True}
    WORKING_MANIFEST.write_text(json.dumps(working, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"dependencies": dependencies, "matrix": matrix, "evidence": evidence, "manifest": manifest}


def main() -> None:
    package = build_phase12a()
    result = build_phase12b(package)
    print(json.dumps({"phase": "12A/12B", "12A": package["manifest"]["counts"], "12B": result["manifest"]["counts"], "maps": [38, 39]}, indent=2))


if __name__ == "__main__":
    main()
