"""Build the bounded Phase 13A infectious-disease systems baseline.

This is a factual 2026 surveillance and systems-context package. It keeps
pathogen presence, exposure, infection, reported case, local transmission,
outbreak, and disease burden separate. It does not create a disease-risk
index, forecast, individual case map, or future scenario.
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

MAP_BASE = MAPS / "41_infectious_disease_system_baseline_2026"
MANIFEST = REPORTS / "infectious_disease_baseline_manifest.json"
LEDGER = REPORTS / "phase13a_citation_ledger.json"

CITATION_URLS = [
    "https://www.cdc.gov/nndss/about/index.html",
    "https://wonder.cdc.gov/nndss.html",
    "https://www.cdc.gov/west-nile-virus/data-maps",
    "https://www.cdc.gov/lyme/data-research/facts-stats/index.html",
    "https://www.cdc.gov/legionella/php/surveillance/index.html",
    "https://www.cdc.gov/legionella/about/index.html",
    "https://www.cdc.gov/healthy-water-data/about/index.html",
    "https://www.cdc.gov/nors/about/index.html",
    "https://www.cdc.gov/national-enteric-surveillance/about/index.html",
    "https://www.cdc.gov/foodnet/about/index.html",
    "https://www.cdc.gov/fluview/index.html",
    "https://www.cdc.gov/fluview/overview/index.html",
    "https://www.cdc.gov/wastewater/about-data/",
    "https://www.cdc.gov/rabies/about/index.html",
    "https://www.cdc.gov/nhsn/about-nhsn/index.html",
    "https://www.cdc.gov/antimicrobial-resistance/data-research/threats/index.html",
    "https://www.in.gov/health/idepd/communicable-disease-reporting",
    "https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update",
    "https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf",
    "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
    "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
    "reports/phase11a_population_settlement_freeze_manifest.json",
    "reports/phase12a_vector_ecology_freeze_manifest.json",
    "reports/phase4b_information_freeze_manifest.json",
    "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
    "https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county",
    "reports/vector_ecology_findings.md",
]

SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "publication_or_period",
    "retrieval_date", "geographic_scale", "method_or_product", "evidence_use",
    "use_limitations", "retrieval_url", "retrieval_provenance",
]
SOURCE_ROWS = [
    ["s13_nndss_about", "CDC National Notifiable Diseases Surveillance System", CITATION_URLS[0], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / state-local-territorial reporting", "case surveillance system overview", "NNDSS case-surveillance structure and public-health reporting interface", "Case surveillance is not a complete census of infection; disease-specific definitions and reporting completeness vary."],
    ["s13_nndss_wonder", "CDC WONDER NNDSS Data", CITATION_URLS[1], "federal_surveillance", "annual and weekly tables; page reviewed 2026-09-09", RETRIEVAL_DATE, "United States / jurisdiction and disease tables", "reported occurrence tables", "reported occurrence and state/territorial reporting basis", "Published occurrence is not exposure geography, infection incidence for all infections, or local transmission."],
    ["s13_cdc_wnv", "CDC West Nile Data and Maps", CITATION_URLS[2], "federal_surveillance", "current-year and historic data page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / state and territorial", "ArboNET and NNDSS context", "separate vector, animal, and human West Nile reporting streams", "The page does not make a positive vector record a human infection or transmission finding."],
    ["s13_cdc_lyme", "CDC Lyme Disease Surveillance and Data", CITATION_URLS[3], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / state and county of residence context", "NNDSS case-surveillance context", "Lyme case-surveillance geography and reporting limitations", "Reported case geography does not identify the place of exposure or local transmission."],
    ["s13_cdc_legionella_surv", "CDC Legionellosis Surveillance and Trends", CITATION_URLS[4], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / jurisdiction and national", "two national surveillance systems; NNDSS trend context", "Legionellosis surveillance structure, reported cases, provisional status, and exposure fields", "Reported cases are descriptive surveillance data; environmental source attribution requires investigation."],
    ["s13_cdc_legionella_about", "CDC About Legionnaires' Disease", CITATION_URLS[5], "federal_public_health", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / general transmission context", "clinical and transmission pathway reference", "Legionella aerosolized-water and healthcare/building-water interface", "General pathway biology is not a local building contamination or illness finding."],
    ["s13_cdc_water_surv", "CDC Waterborne Disease Surveillance", CITATION_URLS[6], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / outbreak investigation", "waterborne disease surveillance and outbreak definition", "waterborne surveillance, exposure-location linkage, and outbreak-definition boundary", "A water condition does not establish treatment failure, exposure, infection, or illness without a supported evidence chain."],
    ["s13_cdc_nors", "CDC National Outbreak Reporting System", CITATION_URLS[7], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / state-local-territorial outbreak reporting", "outbreak reports through SEDRIC/NORS", "waterborne, foodborne, animal-contact, and enteric outbreak reporting structure", "NORS is outbreak reporting, not a denominator for all infections or a continuous local incidence series."],
    ["s13_cdc_enteric", "CDC National Enteric Disease Surveillance", CITATION_URLS[8], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / state and territorial laboratories", "case-based and laboratory-based surveillance", "Campylobacter, Salmonella, Shigella, and STEC laboratory surveillance plus case-based systems", "Laboratory reporting captures identified infections and does not equal all community infections or exposure locations."],
    ["s13_cdc_foodnet", "CDC FoodNet", CITATION_URLS[9], "federal_surveillance", "current page; reporting changes after 2025-07-01", RETRIEVAL_DATE, "FoodNet surveillance area / ten state health departments", "active laboratory-based surveillance", "eight-pathogen surveillance scope, participating partners, coverage, and reporting changes", "FoodNet is not a Western Basin county surveillance system; its surveillance area and reporting rules differ from NNDSS/LEDS."],
    ["s13_cdc_fluview", "CDC FluView", CITATION_URLS[10], "federal_surveillance", "weekly 2026 surveillance interface; data preliminary", RETRIEVAL_DATE, "United States / HHS region / state / national", "weekly influenza surveillance report", "influenza surveillance reporting interface", "Weekly data are preliminary and are not a single community transmission rate."],
    ["s13_cdc_flu_methods", "CDC U.S. Influenza Surveillance Purpose and Methods", CITATION_URLS[11], "federal_surveillance", "current methods page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / laboratory, outpatient, hospital, mortality streams", "ICLS, NREVSS, ILINet and other surveillance components", "laboratory denominators, sentinel outpatient, hospitalization, and mortality stream distinctions", "Testing practices and stream denominators differ; hospitalizations and tests do not equal community incidence."],
    ["s13_cdc_wastewater", "CDC About Wastewater Data", CITATION_URLS[12], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "community / sewershed / state / regional / national", "wastewater viral monitoring", "community-level respiratory-virus surveillance and early-warning context", "Wastewater cannot currently determine the number of infections; sewershed coverage can over-represent connected populations."],
    ["s13_cdc_rabies", "CDC About Rabies", CITATION_URLS[13], "federal_public_health", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / animal-human interface", "animal reservoir, exposure, and post-exposure prophylaxis reference", "animal-contact pathway and response interface", "Animal cases, potential exposures, PEP, and human disease are separate records."],
    ["s13_cdc_nhsn", "CDC National Healthcare Safety Network", CITATION_URLS[14], "federal_surveillance", "current page; accessed 2026-09-09", RETRIEVAL_DATE, "healthcare facilities / state / regional / national", "facility reporting and HAI tracking system", "general HAI surveillance, facility participation, reporting, and benchmarking interface", "Facility participation and HAI measures do not describe community incidence or rank local facilities in this phase."],
    ["s13_cdc_ar", "CDC Antibiotic Resistance Threats Report", CITATION_URLS[15], "federal_surveillance", "2019 report page; accessed 2026-09-09", RETRIEVAL_DATE, "United States / national estimates and threat categories", "AR burden estimates and threat categories", "generalized antimicrobial-resistance surveillance/response context", "National estimates are not Western Basin observations and are not used as a regional burden estimate."],
    ["s13_ind_reportable", "Indiana Communicable Disease Reporting", CITATION_URLS[16], "state_surveillance", "current reportable-disease reporting page; accessed 2026-09-09", RETRIEVAL_DATE, "Indiana / healthcare-provider and hospital reporting", "reportable-condition list and NBS/forms", "state reporting pathway and reportable-condition interface", "Reporting requirements do not supply a comparable incidence denominator for every listed condition."],
    ["s13_ohio_vector", "Ohio Vector-borne Disease Surveillance Update", CITATION_URLS[17], "state_surveillance", "2025 annual summary used in accepted Phase 12 context", RETRIEVAL_DATE, "Ohio / agency and county", "pooled mosquito surveillance and human-case reporting", "Ohio WNV and other vector-surveillance observations", "Counts retain program denominators and are not comparable to human case counts or other states without harmonization."],
    ["s13_mi_vector", "Michigan EZID Annual Surveillance Summary", CITATION_URLS[18], "state_surveillance", "2023 annual summary", RETRIEVAL_DATE, "Michigan / participating local health departments", "mosquito pooling, identification, and laboratory testing", "Michigan WNV/arbovirus surveillance context", "Participating jurisdictions and methods vary; positive pools are not human cases or incidence."],
    ["phase7_exposure", "Accepted Phase 7A exposure/environmental-health layer", CITATION_URLS[19], "repository_accepted_layer", "accepted/frozen 2026 layer", RETRIEVAL_DATE, "Western Basin / pathway and monitoring context", "accepted exposure pathways and monitoring boundaries", "source-water, recreational-water, HAB, and exposure-evidence separation", "Reused context only; no infectious disease, dose, illness, or individual exposure is imported."],
    ["phase9_climate", "Accepted Phase 9 climate/natural-hazard layer", CITATION_URLS[20], "repository_accepted_layer", "accepted/frozen 2026 physical and scenario layer", RETRIEVAL_DATE, "Western Basin / station, county, watershed, shoreline", "accepted climate/hazard observations and interfaces", "temperature, precipitation, flooding, drought, lake/coastal, and seasonal context", "Reused context only; no disease suitability or incidence relationship is inferred."],
    ["phase11_population", "Accepted Phase 11 population/settlement layer", CITATION_URLS[21], "repository_accepted_layer", "accepted/frozen 2026 population/mobility layer", RETRIEVAL_DATE, "Western Basin / county, place, generalized employment", "accepted population and settlement tables", "population, settlement, workplace, and mobility context", "Population presence is not contact, exposure, infection, disease, or local risk."],
    ["phase12_vector", "Accepted Phase 12 vector-ecology layer", CITATION_URLS[22], "repository_accepted_layer", "accepted/frozen 2026 vector ecology/dependency/futures layers", RETRIEVAL_DATE, "Western Basin / county, habitat, program, and generalized ecology", "accepted vector surveillance and ecology artifacts", "vector presence, pathogen-in-vector, habitat, method, and surveillance boundaries", "Vector ecology is reused; vector detection is not human infection and county status is not local disease burden."],
    ["phase4_information", "Accepted Phase 4 observation/information layer", CITATION_URLS[23], "repository_accepted_layer", "accepted/frozen observation and information layers", RETRIEVAL_DATE, "Western Basin / station, program, agency, and information chain", "accepted public observation-to-decision artifacts", "observation, data, uncertainty, and decision-interface context", "Monitoring and information availability are not complete surveillance or control effectiveness."],
    ["phase10_governance", "Accepted Phase 10 governance/jurisdiction layer", CITATION_URLS[24], "repository_accepted_layer", "accepted/frozen 2026 institutional layer", RETRIEVAL_DATE, "Western Basin / institutional and program scales", "accepted actor, authority, and coordination artifacts", "institutional role, reporting, response, and governance distinctions", "Monitoring, funding, advice, ownership, and information are not automatically legal authority or operational control."],
    ["s13_ind_wnv_2026", "Indiana Department of Health — First 2026 WNV Case", CITATION_URLS[25], "state_surveillance", "2026-08-28 news release", RETRIEVAL_DATE, "Indiana / county and state summary", "mosquito testing and human-case surveillance", "Indiana 2026 positive-mosquito county summary and contextual Allen County human case", "The release does not provide comparable county sampling effort or species counts; human case geography is residence context."],
    ["phase12_vector_findings", "Accepted Phase 12A Vector Ecology Findings", CITATION_URLS[26], "repository_accepted_layer", "accepted/frozen Phase 12A findings", RETRIEVAL_DATE, "Ohio / agency and county summaries", "accepted/frozen findings report preserving dated 2025 Ohio values", "fixed reference for the exact 2025 Ohio vector-surveillance values reused here", "The report is a protected project artifact; it does not expand the 2025 values into a current 2026 estimate."],
]
# Keep the primary source identity separate from the retrieval path/provenance.
# External pages were verified during Phase 13A source acquisition; repository
# references are protected accepted/frozen context inputs.
SOURCE_ROWS = [
    row + [row[2], "web_extract/source-page verification on 2026-09-09" if row[2].startswith("http") else "repository accepted/frozen artifact reference; hash-checked by validator"]
    for row in SOURCE_ROWS
]

NODE_COLUMNS = [
    "node_id", "name", "node_class", "disease_group", "pathogen_or_agent",
    "transmission_pathway", "environment_or_host_interface", "geographic_scale",
    "latitude", "longitude", "source_id", "evidence_status", "confidence",
    "reality_status", "canon_status", "notes",
]
NODE_ROWS = [
    ["DID-001", "West Nile virus system", "disease_system", "vector-borne", "West Nile virus", "mosquito-mediated enzootic cycle with human infection as a distinct endpoint", "Culex/vector, bird-host, human, and seasonal environmental interfaces", "state/county/program; human case geography may be residence", "", "", "s13_cdc_wnv", "documented_system", "high", "real", "verified", "Included as a distinct vector-borne surveillance system; positive pools, human cases, infection, and local transmission remain separate; a vector record is not a human infection and is not local transmission."],
    ["DID-002", "Lyme disease system", "disease_system", "vector-borne", "Borrelia burgdorferi sensu lato; Ixodes scapularis interface", "tick-mediated transmission with human case surveillance as a separate stream", "Ixodes, forest/edge, vertebrate hosts, and human interface", "county/state; case surveillance commonly uses residence geography", "", "", "s13_cdc_lyme", "documented_system", "high", "real", "verified", "Uses accepted Phase 12 tick ecology context without reconstructing vector abundance or human exposure location."],
    ["DID-003", "Legionellosis system", "disease_system", "waterborne/environmental", "Legionella bacteria; Legionnaires' disease and Pontiac fever", "inhalation of aerosolized water or droplets; generally not person-to-person", "building water systems, cooling/aerosol interfaces, and healthcare settings", "jurisdiction/national; investigation-specific exposure setting", "", "", "s13_cdc_legionella_about", "documented_system", "high", "real", "verified", "A building-water pathway is not a contamination, treatment-failure, exposure, infection, or illness finding by itself."],
    ["DID-004", "Waterborne enteric disease system", "disease_system", "waterborne/environmental", "multiple enteric agents including norovirus, Giardia, Cryptosporidium, and bacteria", "ingestion, contact, or other water-associated pathways established through investigation", "drinking water, recreational water, and environmental water interfaces", "outbreak investigation / state-local-territorial reporting", "", "", "s13_cdc_water_surv", "documented_system", "high", "real", "verified", "Retained as a distinct multi-agent system; no nutrient, bloom, indicator, or infrastructure-age-to-illness inference is made."],
    ["DID-005", "Salmonella infection system", "disease_system", "foodborne/enteric", "Salmonella", "foodborne, environmental, animal-contact, and person-to-person pathways", "food, clinical laboratory, animal, and outbreak-investigation interfaces", "state/territorial/national; case and laboratory reporting", "", "", "s13_cdc_enteric", "documented_system", "high", "real", "verified", "Kept distinct from Campylobacter, STEC, and outbreak records; it is not a composite disease-risk score and no composite enteric burden is created."],
    ["DID-006", "Campylobacter infection system", "disease_system", "foodborne/enteric", "Campylobacter", "foodborne and other enteric pathways", "food, clinical laboratory, and state/territorial laboratory interfaces", "state/territorial/national; laboratory-based reporting", "", "", "s13_cdc_enteric", "documented_system", "high", "real", "verified", "FoodNet/LEDS/NNDSS system context is retained without treating surveillance coverage as all community infections."],
    ["DID-007", "Shiga toxin-producing E. coli system", "disease_system", "foodborne/enteric", "Shiga toxin-producing Escherichia coli (STEC)", "foodborne, water/environmental, animal-contact, and person-to-person pathways", "food, animal, water, clinical laboratory, and outbreak interfaces", "state/territorial/national; laboratory and case reporting", "", "", "s13_cdc_enteric", "documented_system", "high", "real", "verified", "STEC O157 and non-O157 distinctions remain source-dependent; no illness or exposure location is inferred."],
    ["DID-008", "Seasonal influenza system", "disease_system", "respiratory", "influenza A and B viruses", "respiratory transmission with laboratory, outpatient, hospital, and mortality observation streams", "community, healthcare, laboratory, and sentinel-provider interfaces", "national/HHS region/state; stream-specific", "", "", "s13_cdc_flu_methods", "documented_system", "high", "real", "verified", "Included as a surveillance-system example, not a single transmission-rate or pandemic reconstruction."],
    ["DID-009", "SARS-CoV-2 community surveillance system", "disease_system", "respiratory", "SARS-CoV-2", "respiratory transmission with wastewater and clinical surveillance interfaces", "community/sewershed, laboratory, healthcare, and public-health interfaces", "sewershed/community/state/regional/national", "", "", "s13_cdc_wastewater", "documented_system", "high", "real", "verified", "Wastewater is an observation stream; it does not supply an infection count, individual exposure estimate, or risk surface."],
    ["DID-010", "Rabies system", "disease_system", "zoonotic", "rabies virus", "animal bite/scratch or saliva exposure with human and animal endpoints distinct", "wildlife, domestic animal, animal-control, laboratory, and PEP interfaces", "animal/state/national; exposure investigation-specific", "", "", "s13_cdc_rabies", "documented_system", "high", "real", "verified", "Animal infection, potential exposure, PEP, human infection, and human disease remain separate records."],
    ["DID-011", "Healthcare-associated infection system", "disease_system", "healthcare/institutional", "multiple healthcare-associated pathogens", "healthcare-associated acquisition and facility surveillance pathways", "healthcare facilities, infection prevention, laboratory, and public reporting interfaces", "facility/state/regional/national", "", "", "s13_cdc_nhsn", "documented_system", "high", "real", "verified", "Generalized HAI system only; no facility ranking, performance score, patient data, or community-incidence inference."],
    ["DID-012", "Antimicrobial-resistance surveillance system", "disease_system", "healthcare/institutional", "multiple antimicrobial-resistant bacteria and fungi", "resistance detection and healthcare/community surveillance pathways", "clinical laboratory, healthcare, public-health laboratory, and response interfaces", "facility/state/regional/national", "", "", "s13_cdc_ar", "documented_system", "moderate", "real", "verified", "Generalized AR surveillance context only; national threat estimates are not Western Basin observations."],
    ["DID-013", "HAB toxic/noninfectious boundary", "boundary_interface", "noninfectious environmental health", "cyanobacterial toxins and other HAB-associated hazards", "toxic/environmental pathways kept separate from infection", "source water, recreational water, monitoring, and treatment interfaces", "lake/source-water/recreational-water program", "", "", "phase7_exposure", "documented_boundary", "high", "real", "verified", "HAB context is not placed in the infectious-disease pathogen set; contamination, toxin exposure, and illness remain separate; it is not a disease-risk index and is not a risk surface."],
    ["SUR-001", "NNDSS case-surveillance interface", "surveillance_system", "cross-cutting", "nationally notifiable conditions", "case reporting from state, local, tribal, and territorial health departments", "healthcare, laboratory, public-health, and jurisdictional reporting", "state/territorial/national", "", "", "s13_nndss_about", "documented_program", "high", "real", "verified", "NNDSS collects case-surveillance data; disease-specific definitions and completeness are not interchangeable."],
    ["SUR-002", "State and local reportable-disease systems", "surveillance_system", "cross-cutting", "reportable infectious conditions", "provider, laboratory, and public-health reporting", "state/local health departments, hospitals, laboratories, and reporting forms", "state/county/jurisdiction", "", "", "s13_ind_reportable", "documented_program", "high", "real", "verified", "Ohio, Michigan, and Indiana reporting systems are retained as jurisdictional interfaces; no uniform three-state denominator is assumed."],
    ["SUR-003", "ArboNET and mosquito surveillance interface", "surveillance_system", "vector-borne", "West Nile virus and other arbovirus vector/animal/human streams", "mosquito trapping, pooled testing, animal and human reporting", "agency/county/state", "", "", "s13_cdc_wnv", "documented_program", "high", "real", "verified", "Reuses Phase 12 vector context; vector detection, pathogen-positive pools, human infection, and cases remain separate."],
    ["SUR-004", "Legionellosis surveillance interface", "surveillance_system", "waterborne/environmental", "Legionellosis", "case reporting and supplemental exposure/source information", "jurisdiction/national; investigation-specific setting", "", "", "s13_cdc_legionella_surv", "documented_program", "high", "real", "verified", "CDC describes two national surveillance systems and reports provisional periods; this package does not reconstruct case counts."],
    ["SUR-005", "Waterborne and foodborne outbreak reporting", "surveillance_system", "waterborne/foodborne", "multiple agents and outbreak types", "epidemiologic investigation and outbreak reporting", "state/local/territorial outbreak and exposure setting", "", "", "s13_cdc_nors", "documented_program", "high", "real", "verified", "Outbreak reporting requires an investigation context; it is not a continuous incidence denominator."],
    ["SUR-006", "National enteric laboratory and case surveillance", "surveillance_system", "foodborne/enteric", "Campylobacter, Salmonella, Shigella, STEC and other enteric conditions", "clinical and public-health laboratory reporting plus case-based surveillance", "state/territorial public-health laboratory and NNDSS/SEDRIC", "", "", "s13_cdc_enteric", "documented_program", "high", "real", "verified", "Laboratory-identified infections and case records do not capture all infections or identify exposure location by default."],
    ["SUR-007", "FoodNet active surveillance interface", "surveillance_system", "foodborne/enteric", "eight foodborne pathogens", "active communication with clinical laboratories and detailed infection follow-up", "FoodNet surveillance area / ten state health departments", "", "", "s13_cdc_foodnet", "documented_program", "high", "real", "verified", "FoodNet coverage and post-2025 reporting changes make it complementary to, not interchangeable with, NNDSS/LEDS."],
    ["SUR-008", "FluView and influenza surveillance components", "surveillance_system", "respiratory", "influenza A/B", "laboratory, outpatient, hospitalization, mortality, and other reporting streams", "national/HHS region/state and sentinel stream", "", "", "s13_cdc_flu_methods", "documented_program", "high", "real", "verified", "Testing, sentinel outpatient, hospital, and mortality streams have distinct denominators and interpretations."],
    ["SUR-009", "CDC wastewater monitoring", "surveillance_system", "respiratory", "SARS-CoV-2 and other tracked respiratory viruses", "sewershed wastewater sampling and viral measurement", "sewershed/community/state/regional/national", "", "", "s13_cdc_wastewater", "documented_program", "high", "real", "verified", "Community-level observation and early warning are not an infection count, incidence rate, or individual risk measure."],
    ["SUR-010", "Animal rabies and human PEP interface", "surveillance_system", "zoonotic", "rabies virus", "animal testing, exposure assessment, and post-exposure prophylaxis", "animal-control/veterinary/public-health and exposure investigation", "", "", "s13_cdc_rabies", "documented_program", "high", "real", "verified", "Animal test results and PEP are response records; neither is substituted for human infection or disease burden."],
    ["SUR-011", "NHSN healthcare-associated infection surveillance", "surveillance_system", "healthcare/institutional", "HAIs and facility measures", "facility reporting and standardized HAI measures", "facility/state/regional/national", "", "", "s13_cdc_nhsn", "documented_program", "high", "real", "verified", "The system supports facility and public-health reporting; participation is not a community denominator."],
    ["SUR-012", "Antimicrobial-resistance observation/response interface", "surveillance_system", "healthcare/institutional", "antimicrobial-resistant bacteria and fungi", "clinical laboratory and public-health surveillance", "facility/state/regional/national", "", "", "s13_cdc_ar", "documented_program", "moderate", "real", "verified", "Retained at generalized system level; no local AR prevalence or facility ranking is generated."],
    ["ENV-001", "Drinking and recreational water interface", "environmental_interface", "waterborne/environmental", "water-associated pathogens and noninfectious agents", "ingestion/contact/aerosol pathways requiring evidence", "source water, finished water, recreational water, and investigation setting", "source/recreational-water/program", "", "", "phase7_exposure", "accepted_context", "high", "real", "verified", "Source-water condition, treatment, exposure, infection, and reported illness remain separate states."],
    ["ENV-002", "Building water and aerosol interface", "environmental_interface", "waterborne/environmental", "Legionella and building-water pathogens", "aerosol/droplet inhalation and healthcare/building-water interface", "building water systems, cooling/aerosol, healthcare", "building/healthcare/investigation", "", "", "s13_cdc_legionella_about", "documented_context", "high", "real", "verified", "No building-specific sampling, contamination, exposure, or illness claim is made."],
    ["ENV-003", "Food, animal, and environmental interface", "environmental_interface", "foodborne/zoonotic", "enteric pathogens and rabies virus as separate systems", "foodborne, animal-contact, environmental, and bite/scratch pathways", "food chain, wildlife/domestic animals, laboratories, and investigations", "regional/state/program", "", "", "s13_cdc_nors", "documented_context", "high", "real", "verified", "The shared interface does not merge unlike pathogens or assert a common burden."],
    ["ENV-004", "Respiratory community and wastewater interface", "environmental_interface", "respiratory", "influenza, SARS-CoV-2, and other tracked respiratory viruses", "respiratory transmission observed through clinical and wastewater systems", "community, sewershed, laboratory, outpatient, and hospital interfaces", "community/sewershed/state/regional", "", "", "s13_cdc_wastewater", "documented_context", "high", "real", "verified", "Wastewater, testing, hospitalization, and case reports are complementary streams, not one transmission rate."],
    ["HOST-001", "Population and settlement interface", "host_interface", "cross-cutting", "human host context", "human presence, activity, care-seeking, and reporting interface", "settlement, workplace, mobility, household, and healthcare context", "county/place/generalized employment", "", "", "phase11_population", "accepted_context", "high", "real", "verified", "Reuses Phase 11 at native scale; population presence does not establish contact, exposure, infection, or disease."],
    ["INST-001", "Public-health laboratory and reporting interface", "institutional_response_interface", "cross-cutting", "clinical, environmental, animal, and vector specimens", "testing, laboratory confirmation, electronic reporting, and case classification", "laboratory/state/local/territorial/national", "", "", "phase4_information", "accepted_context", "high", "real", "verified", "Laboratory and reporting systems observe selected events; testing intensity is not disease intensity."],
    ["INST-002", "Public-health response and decision interface", "institutional_response_interface", "cross-cutting", "surveillance-informed public-health actions", "investigation, communication, treatment/referral, control, and prevention", "agency/program/jurisdiction/healthcare", "", "", "phase10_governance", "accepted_context", "high", "real", "verified", "Monitoring, advice, funding, and information are kept distinct from operational control and legal authority."],
    ["REF-7A", "Accepted Phase 7A exposure context reference", "accepted_layer_reference", "cross-cutting", "environmental exposure pathways", "accepted environmental-health evidence ladder", "water, air, soil, food, recreation, and heat context", "Western Basin / pathway and monitoring scale", "", "", "phase7_exposure", "accepted_reference", "high", "real", "verified", "Reference only; Phase 7A artifacts are protected and not rebuilt or modified."],
    ["REF-9", "Accepted Phase 9 climate context reference", "accepted_layer_reference", "cross-cutting", "climate and natural-hazard observations", "accepted physical-environmental context", "station, county, watershed, shoreline, lake, and regional context", "Western Basin / native Phase 9 scales", "", "", "phase9_climate", "accepted_reference", "high", "real", "verified", "Reference only; no disease suitability, incidence, or causal attribution is derived."],
    ["REF-11", "Accepted Phase 11 population context reference", "accepted_layer_reference", "cross-cutting", "population, settlement, workplace, and mobility context", "accepted aggregate population context", "county, place, generalized employment, and mobility scales", "Western Basin / native Phase 11 scales", "", "", "phase11_population", "accepted_reference", "high", "real", "verified", "Reference only; no individual movement or local disease downscaling is created."],
    ["REF-12", "Accepted Phase 12 vector ecology context reference", "accepted_layer_reference", "vector-borne", "vector taxa, pathogen-in-vector, habitat, and surveillance context", "accepted vector ecology and surveillance relationships", "county, habitat, program, and generalized ecology scales", "Western Basin / native Phase 12 scales", "", "", "phase12_vector", "accepted_reference", "high", "real", "verified", "Reference only; vector detection != pathogen-positive vector != human infection."],
    ["REF-4", "Accepted Phase 4 observation context reference", "accepted_layer_reference", "cross-cutting", "public observations and information chains", "accepted observation-to-decision context", "station, program, agency, and information-chain scales", "Western Basin / native Phase 4 scales", "", "", "phase4_information", "accepted_reference", "high", "real", "verified", "Reference only; monitoring coverage is heterogeneous and is not complete surveillance."],
    ["REF-10", "Accepted Phase 10 governance context reference", "accepted_layer_reference", "cross-cutting", "actors, authorities, and coordination", "accepted institutional-role distinctions", "agency/program/jurisdictional scales", "Western Basin / native Phase 10 scales", "", "", "phase10_governance", "accepted_reference", "high", "real", "verified", "Reference only; governance roles are not collapsed into response performance or vulnerability."],
]

# Surveillance nodes retain their program scale explicitly; keep coordinates blank
# because these are generalized systems, not collection sites or case locations.
SURVEILLANCE_NODE_SCALES = {
    "SUR-003": "agency/county/state", "SUR-004": "jurisdiction/national",
    "SUR-005": "state/local/territorial", "SUR-006": "state/territorial/national",
    "SUR-007": "FoodNet surveillance area", "SUR-008": "national/HHS region/state",
    "SUR-009": "sewershed/community/state/regional", "SUR-010": "animal/state/exposure investigation",
    "SUR-011": "facility/state/regional/national", "SUR-012": "facility/state/regional/national",
    "INST-001": "laboratory/state/local/territorial/national", "INST-002": "agency/program/jurisdiction/healthcare",
}
for _row in NODE_ROWS:
    if _row[0] in SURVEILLANCE_NODE_SCALES and len(_row) == 15:
        _row.insert(7, SURVEILLANCE_NODE_SCALES[_row[0]])

REL_COLUMNS = [
    "relationship_id", "from_id", "to_id", "relationship_type", "relationship_basis",
    "geographic_scale", "evidence_status", "source_id", "confidence", "reality_status",
    "canon_status", "notes",
]
REL_ROWS = [
    ["IDR-001", "DID-001", "SUR-003", "observed_by", "documented_source", "agency/county/state", "documented_program", "s13_cdc_wnv", "high", "real", "verified", "West Nile vector surveillance includes mosquito and other separate reporting streams."],
    ["IDR-002", "DID-001", "SUR-001", "reported_through", "documented_source", "state/territorial/national", "documented_program", "s13_nndss_about", "high", "real", "verified", "West Nile disease is nationally notifiable; reported cases remain case-surveillance records."],
    ["IDR-003", "DID-001", "REF-12", "vector_ecology_context", "accepted_layer", "county/habitat/program", "accepted_reference", "phase12_vector", "high", "real", "verified", "Phase 12 vector ecology is reused without inferring human infection or disease burden."],
    ["IDR-004", "DID-001", "REF-9", "seasonal_environment_context", "accepted_layer", "station/county/regional", "accepted_reference", "phase9_climate", "limited", "real", "inferred", "Climate context can frame seasonality but does not establish vector abundance, infection, or incidence."],
    ["IDR-005", "DID-002", "REF-12", "vector_ecology_context", "accepted_layer", "county/habitat/program", "accepted_reference", "phase12_vector", "high", "real", "verified", "Accepted Ixodes records and habitat context are not human contact or Lyme case locations."],
    ["IDR-006", "DID-002", "SUR-001", "reported_through", "documented_source", "state/county of residence/national", "documented_program", "s13_cdc_lyme", "high", "real", "verified", "Case surveillance provides a reporting stream, not the exposure location or local transmission proof."],
    ["IDR-007", "DID-003", "ENV-002", "environmental_interface", "documented_source", "building/healthcare/investigation", "documented_relationship", "s13_cdc_legionella_about", "high", "real", "verified", "Legionella aerosolized-water context is retained without building-specific contamination or illness claims."],
    ["IDR-008", "DID-003", "SUR-004", "observed_by", "documented_source", "jurisdiction/national", "documented_program", "s13_cdc_legionella_surv", "high", "real", "verified", "CDC describes two national legionellosis surveillance systems and provisional reporting periods."],
    ["IDR-009", "DID-003", "SUR-001", "reported_through", "documented_source", "state/territorial/national", "documented_program", "s13_nndss_wonder", "high", "real", "verified", "NNDSS reported occurrence is not source attribution or place of exposure."],
    ["IDR-010", "DID-004", "ENV-001", "environmental_interface", "documented_source", "source/recreational-water/investigation", "documented_relationship", "s13_cdc_water_surv", "high", "real", "verified", "Waterborne illness linkage requires an evidence chain; contamination alone is insufficient."],
    ["IDR-011", "DID-004", "SUR-005", "outbreak_observed_by", "documented_source", "state/local/territorial outbreak", "documented_program", "s13_cdc_nors", "high", "real", "verified", "NORS records investigated outbreaks, not all water-associated infections."],
    ["IDR-012", "DID-004", "SUR-006", "laboratory_context", "documented_source", "state/territorial/national", "documented_program", "s13_cdc_enteric", "high", "real", "verified", "Enteric laboratory reporting can identify agents but does not establish a water exposure without investigation."],
    ["IDR-013", "DID-004", "REF-7A", "exposure_boundary_context", "accepted_layer", "pathway/monitoring", "accepted_reference", "phase7_exposure", "high", "real", "verified", "Accepted exposure ladder preserves contamination != exposure != infection != illness."],
    ["IDR-014", "DID-005", "SUR-006", "laboratory_surveillance", "documented_source", "state/territorial/national", "documented_program", "s13_cdc_enteric", "high", "real", "verified", "Salmonella is separately represented in national laboratory/case surveillance."],
    ["IDR-015", "DID-005", "SUR-007", "active_surveillance_context", "documented_source", "FoodNet surveillance area", "documented_program", "s13_cdc_foodnet", "high", "real", "verified", "FoodNet provides active surveillance context for Salmonella without Western Basin downscaling."],
    ["IDR-016", "DID-006", "SUR-006", "laboratory_surveillance", "documented_source", "state/territorial/national", "documented_program", "s13_cdc_enteric", "high", "real", "verified", "Campylobacter is separately represented in national laboratory-based surveillance."],
    ["IDR-017", "DID-006", "SUR-007", "active_surveillance_context", "documented_source", "FoodNet surveillance area", "documented_program", "s13_cdc_foodnet", "high", "real", "verified", "FoodNet coverage and optional-reporting changes are retained as program limits."],
    ["IDR-018", "DID-007", "SUR-006", "laboratory_surveillance", "documented_source", "state/territorial/national", "documented_program", "s13_cdc_enteric", "high", "real", "verified", "STEC surveillance distinguishes laboratory and case streams; no exposure source is assumed."],
    ["IDR-019", "DID-007", "SUR-007", "active_surveillance_context", "documented_source", "FoodNet surveillance area", "documented_program", "s13_cdc_foodnet", "high", "real", "verified", "FoodNet is retained as complementary surveillance, not a regional incidence denominator."],
    ["IDR-020", "DID-008", "SUR-008", "observed_by", "documented_source", "national/HHS region/state/stream", "documented_program", "s13_cdc_flu_methods", "high", "real", "verified", "FluView combines distinct laboratory, outpatient, hospital, mortality, and other streams."],
    ["IDR-021", "DID-008", "ENV-004", "community_interface", "documented_plus_inferred", "community/sewershed/healthcare", "documented_context", "s13_cdc_flu_methods", "moderate", "real", "inferred", "Respiratory observations meet community and healthcare interfaces, but case count is not a transmission rate."],
    ["IDR-022", "DID-009", "SUR-009", "observed_by", "documented_source", "sewershed/community/state/regional", "documented_program", "s13_cdc_wastewater", "high", "real", "verified", "Wastewater supplies community-level viral observation and early-warning context."],
    ["IDR-023", "DID-009", "ENV-004", "community_interface", "documented_source", "sewershed/community", "documented_context", "s13_cdc_wastewater", "high", "real", "verified", "CDC states wastewater cannot currently determine the number of infections."],
    ["IDR-024", "DID-010", "SUR-010", "animal_response_observed_by", "documented_source", "animal/state/exposure investigation", "documented_program", "s13_cdc_rabies", "high", "real", "verified", "Animal testing, exposure assessment, and PEP are distinct response and surveillance records."],
    ["IDR-025", "DID-010", "ENV-003", "animal_human_interface", "documented_source", "wildlife/domestic animal/public-health", "documented_relationship", "s13_cdc_rabies", "high", "real", "verified", "Animal contact is a pathway context; it does not establish human infection or disease."],
    ["IDR-026", "DID-011", "SUR-011", "observed_by", "documented_source", "facility/state/regional/national", "documented_program", "s13_cdc_nhsn", "high", "real", "verified", "NHSN tracks HAI measures through facility reporting and does not represent community incidence."],
    ["IDR-027", "DID-012", "SUR-012", "observed_by", "documented_source", "facility/state/regional/national", "documented_program", "s13_cdc_ar", "moderate", "real", "verified", "AMR remains a generalized surveillance/response interface; national estimates are not regional observations."],
    ["IDR-028", "DID-011", "DID-012", "institutional_context", "project_boundary", "healthcare/institutional", "boundary_rule", "s13_cdc_nhsn", "high", "real", "verified", "HAI and AMR systems intersect institutionally but are not combined into a burden score."],
    ["IDR-029", "SUR-001", "INST-001", "receives_reports", "documented_source", "state/territorial/national", "documented_program", "s13_nndss_about", "high", "real", "verified", "NNDSS depends on jurisdictional case surveillance and reporting pathways."],
    ["IDR-030", "SUR-006", "INST-001", "receives_laboratory_data", "documented_source", "state/territorial/national", "documented_program", "s13_cdc_enteric", "high", "real", "verified", "Public-health laboratories submit identified enteric infections and specimen information."],
    ["IDR-031", "SUR-008", "INST-001", "receives_surveillance_data", "documented_source", "national/stream", "documented_program", "s13_cdc_flu_methods", "high", "real", "verified", "FluView is a multi-partner observation system with stream-specific denominators."],
    ["IDR-032", "SUR-009", "INST-001", "receives_environmental_observations", "documented_source", "sewershed/community/state", "documented_program", "s13_cdc_wastewater", "high", "real", "verified", "Wastewater observations complement other surveillance and do not supply infection counts."],
    ["IDR-033", "INST-001", "INST-002", "informs_response", "documented_plus_inferred", "agency/program/jurisdiction", "project_inference", "phase10_governance", "moderate", "real", "inferred", "Observation can inform decisions, but monitoring is not control and response effectiveness is not estimated."],
    ["IDR-034", "SUR-003", "INST-002", "informs_response", "documented_plus_inferred", "agency/county/state", "project_inference", "phase10_governance", "moderate", "real", "inferred", "Vector detections can enter response interfaces; they do not establish human cases or local transmission."],
    ["IDR-035", "HOST-001", "REF-11", "population_context", "accepted_layer", "county/place/generalized employment", "accepted_reference", "phase11_population", "high", "real", "verified", "Population and settlement context is retained at native scale and not downscaled to disease risk."],
    ["IDR-036", "REF-9", "ENV-004", "environmental_context", "accepted_layer", "station/county/community", "accepted_reference", "phase9_climate", "limited", "real", "inferred", "Climate context can frame seasonal observation timing but does not establish incidence or suitability."],
    ["IDR-037", "REF-7A", "ENV-001", "exposure_context", "accepted_layer", "pathway/monitoring", "accepted_reference", "phase7_exposure", "high", "real", "verified", "Accepted exposure context keeps source-water condition, pathway, exposure, dose, and health outcome separate."],
    ["IDR-038", "REF-4", "INST-001", "observation_context", "accepted_layer", "station/program/agency", "accepted_reference", "phase4_information", "high", "real", "verified", "Accepted observation architecture is reused without claiming complete infectious-disease surveillance coverage."],
    ["IDR-039", "REF-10", "INST-002", "governance_context", "accepted_layer", "agency/program/jurisdiction", "accepted_reference", "phase10_governance", "high", "real", "verified", "Accepted governance roles remain distinct from operations, legal authority, and control effectiveness."],
    ["IDR-040", "DID-013", "REF-7A", "noninfectious_boundary", "project_boundary", "source/recreational-water", "boundary_rule", "phase7_exposure", "high", "real", "verified", "HAB toxic pathways remain separate from infectious disease and are not included in a pathogen-risk index."],
]

OBS_COLUMNS = [
    "observation_id", "system_node_id", "observation_type", "reporting_year_or_period",
    "geography", "geographic_scale", "observed_value", "units", "reporting_basis",
    "numerator", "denominator", "case_definition_or_surveillance_definition",
    "residence_or_exposure_basis", "observed_estimated_modeled", "source_id",
    "evidence_status", "confidence", "uncertainty_notes", "notes",
]
OBS_ROWS = [
    ["IDO-001", "DID-001", "vector_surveillance", "2025", "Ohio; 42 counties with positive pools", "state/county/agency", "42", "counties", "Ohio pooled mosquito surveillance", "counties with positive WNV pools", "11,980 pooled samples from 58 agencies in 49 counties", "pooled mosquito surveillance; human case definition not applicable", "not applicable; vector sampling geography", "observed", "phase12_vector_findings", "documented", "high", "Species composition and comparable county trap effort are not supplied.", "Positive mosquito pools are not human infection, human cases, or local transmission proof."],
    ["IDO-002", "DID-001", "surveillance_effort", "2025", "Ohio; statewide agency summary", "state/agency/county", "11,980", "pooled samples", "Ohio pooled mosquito surveillance", "pooled samples tested", "58 agencies in 49 counties", "pooled mosquito surveillance; no human case definition", "not applicable; vector sampling geography", "observed", "phase12_vector_findings", "documented", "high", "Pool counts are not individual mosquito abundance and cannot be compared directly with case counts.", "Sampling effort is retained as a denominator, not converted to incidence."],
    ["IDO-003", "DID-001", "human_case_context", "2025", "Ohio; county of residence", "county of residence", "45", "reported WNV cases", "Ohio human disease surveillance map", "reported cases", "not meaningful for this contextual count", "reported human WNV case; source map context", "county of residence; exposure location not supplied", "observed", "phase12_vector_findings", "documented", "high", "Residence is not exposure or infection location.", "Contextual case observation only; not a vector record, contact measure, or local-transmission finding."],
    ["IDO-004", "DID-001", "vector_surveillance", "2023", "Michigan participating jurisdictions", "state/participating counties", "124", "WNV-positive mosquito pools", "Michigan annual mosquito-pool surveillance", "positive pools", "6,351 mosquito pools tested", "pooled mosquito surveillance; human case definition not applicable", "not applicable; sampling geography", "observed", "s13_mi_vector", "documented", "high", "Participating jurisdictions and methods vary.", "Positive pools remain separate from human cases and community incidence."],
    ["IDO-005", "DID-001", "vector_surveillance", "2026 dated update", "Indiana; 33 counties", "state/county", "33", "counties with positive mosquito tests", "Indiana mosquito testing summary", "counties with positive mosquito tests", "not supplied in source release", "mosquito testing; human case definition not applicable", "not applicable; sampling geography", "observed", "s13_ind_wnv_2026", "documented", "moderate", "Comparable county-level effort and species counts are not supplied.", "Positive mosquitoes are not human cases or local transmission proof."],
    ["IDO-006", "DID-001", "human_case_context", "2026 dated update", "Allen County, Indiana; county of residence", "county of residence", "1", "reported human WNV case", "Indiana human surveillance", "reported case", "not meaningful for this contextual count", "reported human WNV case; source release context", "county of residence; exposure location not supplied", "observed", "s13_ind_wnv_2026", "documented", "high", "Source does not establish exposure location or local transmission.", "Case geography is residence-based context and is not a downscaled disease map."],
    ["IDO-007", "DID-002", "case_surveillance_context", "2023/current page context", "United States; state and county-of-residence reporting context", "state/county of residence", "reported Lyme cases; value not extracted in Phase 13A", "reported cases", "state health department case surveillance", "reported cases meeting surveillance definition", "not supplied for Western Basin frame", "CDC Lyme case-surveillance context", "case residence; exposure location not necessarily known", "observed", "s13_cdc_lyme", "documented", "high", "The source page gives surveillance context but this baseline does not extract a comparable regional numerator.", "No neighborhood distribution, exposure location, or transmission rate is inferred."],
    ["IDO-008", "DID-003", "case_surveillance_context", "2014–2025; 2024–2025 provisional", "United States and jurisdictions", "jurisdiction/national", "reported legionellosis cases and incidence tables; value not extracted", "reported cases/incidence context", "two CDC national surveillance systems", "reported cases in national surveillance", "jurisdiction/year denominators are source-specific", "legionellosis surveillance system and disease-specific case definition", "exposure setting requires investigation; not inferred from residence", "observed", "s13_cdc_legionella_surv", "documented", "high", "Provisional years and reporting system combination limit direct comparison.", "Descriptive surveillance context only; no Western Basin case count is fabricated."],
    ["IDO-009", "DID-004", "outbreak_definition", "current page", "United States; outbreak investigation", "outbreak/investigation", "two or more epidemiologically linked ill people", "definition", "waterborne outbreak investigation", "ill people linked by time, exposure location, and illness type", "not applicable; outbreak definition", "CDC waterborne outbreak definition requires epidemiologic linkage and water implicated as probable source", "exposure location is part of investigation evidence, not assumed from residence", "observed", "s13_cdc_water_surv", "documented", "high", "Individual infections outside an outbreak are difficult to link to water without investigation.", "This is a definition observation, not an outbreak assertion for the Western Basin."],
    ["IDO-010", "DID-004", "outbreak_reporting_scope", "current page", "United States; state/local/territorial partners", "state/local/territorial", "waterborne, foodborne, animal-contact, and enteric outbreak reports", "reported outbreaks", "CDC NORS/SEDRIC reporting", "outbreaks submitted by public-health partners", "not a denominator for all infections", "NORS outbreak-reporting categories", "investigation-specific exposure setting", "observed", "s13_cdc_nors", "documented", "high", "Reporting is investigation-dependent and cannot be read as absence when no report is present.", "NORS is a response and outbreak-observation system, not a continuous incidence surface."],
    ["IDO-011", "DID-005", "active_surveillance_scope", "current page; post-2025 reporting change", "FoodNet surveillance area", "surveillance area", "8", "pathogens tracked historically by FoodNet", "FoodNet collaboration", "pathogens with active surveillance history", "surveillance area includes 16% of U.S. population; ten state health departments", "laboratory-diagnosed infection surveillance", "surveillance-area population; not Western Basin population", "observed", "s13_cdc_foodnet", "documented", "high", "FoodNet coverage and reporting rules differ from NNDSS/LEDS.", "Program scope is not a Western Basin Salmonella incidence estimate."],
    ["IDO-012", "DID-006", "laboratory_surveillance_scope", "current page", "United States; state and territorial public-health laboratories", "state/territorial/laboratory", "laboratory-identified infections", "reported laboratory infections", "CDC national laboratory-based surveillance/LEDS", "identified Campylobacter infections", "not supplied in source page", "laboratory identification of ill-person specimens", "patient residence/risk-factor detail is limited and exposure is not assumed", "observed", "s13_cdc_enteric", "documented", "high", "Laboratory-confirmed surveillance does not capture all community infections.", "Kept distinct from FoodNet active surveillance and NORS outbreaks."],
    ["IDO-013", "DID-007", "laboratory_surveillance_scope", "current page", "United States; state and territorial public-health laboratories", "state/territorial/laboratory", "laboratory-identified STEC infections", "reported laboratory infections", "CDC national laboratory-based surveillance/LEDS", "identified STEC infections", "not supplied in source page", "laboratory identification; NNDSS does not differentiate O157/non-O157 in the same way as LEDS", "exposure source and location not assumed", "observed", "s13_cdc_enteric", "documented", "high", "Subtype and reporting distinctions vary by system.", "No composite enteric burden or local foodborne source is inferred."],
    ["IDO-014", "DID-008", "surveillance_component", "2026 weekly interface", "United States / HHS region / state", "national/HHS region/state/stream", "preliminary weekly influenza surveillance data", "laboratory specimens, positive tests, outpatient, hospital, and other stream observations", "CDC FluView and FluView Interactive", "stream-specific observations", "stream-specific; not one denominator", "component-specific surveillance methods", "case geography and exposure location are stream-specific and not assumed", "observed", "s13_cdc_flu_methods", "documented", "high", "Weekly data are preliminary; testing practices differ by laboratory type.", "Case count is not transmission rate and hospitalization is not community incidence."],
    ["IDO-015", "DID-009", "wastewater_surveillance", "2026 current program", "community/sewershed/state/regional/national", "sewershed/community", "community-level viral activity observation", "viral measurement/trend signal", "CDC wastewater monitoring", "wastewater viral measurements", "sewershed population coverage; not infection denominator", "wastewater viral monitoring", "sewershed geography; not individual residence or exposure", "observed", "s13_cdc_wastewater", "documented", "high", "CDC states the number of infections should not be determined from wastewater at this time; septic populations may be underrepresented.", "Wastewater is a complementary observation and early-warning interface, not a case count."],
    ["IDO-016", "DID-010", "animal_human_response_scope", "current page", "United States; wildlife and domestic-animal interface", "animal/state/exposure investigation", "animal rabies cases, potential exposures, and PEP context", "animal testing and exposure/PEP records", "CDC rabies public-health guidance", "records are event- and response-specific", "not a denominator for all animal contacts or human infections", "animal testing/exposure assessment; human clinical disease separate", "exposure investigation location, not assumed from residence", "observed", "s13_cdc_rabies", "documented", "high", "Animal cases, potential exposure, PEP, infection, and disease are separate states.", "No regional animal-case inventory or human PEP count is generated."],
    ["IDO-017", "DID-011", "facility_surveillance_scope", "current page", "healthcare facilities and public-health partners", "facility/state/regional/national", "approximately 25,000 participating medical facilities", "participating facilities tracking HAIs", "CDC NHSN", "facility participation and facility-reported measures", "participating-facility denominator; not community population", "NHSN facility reporting and standardized HAI measures", "facility reporting geography; not community exposure geography", "observed", "s13_cdc_nhsn", "documented", "high", "Participation and reporting vary by facility type; no local facility list or ranking is used.", "HAI surveillance is an institutional system example, not community incidence."],
    ["IDO-018", "DID-012", "national_context", "2019 report; current page", "United States", "national", "national AR threat estimates and categories", "national estimates; value not used as regional observation", "CDC AR Threats report", "national estimate context", "national population/healthcare denominator is report-specific", "AR threat-category and burden-estimate methodology", "not Western Basin residence or exposure geography", "estimated", "s13_cdc_ar", "documented", "moderate", "National estimates are not transferred to the Western Basin.", "Generalized system-level context only; no local prevalence or burden estimate."],
    ["IDO-019", "SUR-002", "reporting_pathway", "2026 current page", "Indiana", "state/provider/hospital", "reportable-condition list and NBS/forms reporting pathway", "reported conditions through provider/lab/hospital channels", "Indiana communicable disease reporting", "reports submitted under state reporting rules", "not a uniform incidence denominator", "state reportable-condition definitions and reporting instructions", "case geography and exposure geography are condition-specific", "observed", "s13_ind_reportable", "documented", "high", "Reporting pathway confirms observation infrastructure, not complete detection or absence.", "State reporting systems are retained as institutional interfaces."],
    ["IDO-020", "DID-013", "noninfectious_boundary", "accepted 2026 context", "Western Basin source/recreational water", "pathway/monitoring", "HAB toxic/environmental context is not an infectious-disease observation", "boundary classification", "accepted Phase 7A exposure layer", "not applicable", "not applicable", "accepted exposure evidence ladder", "no individual exposure or illness is asserted", "observed", "phase7_exposure", "documented_boundary", "high", "HAB and infectious pathways must not be conflated.", "Included solely to preserve the infectious/toxic boundary."],
    ["IDO-021", "REF-12", "accepted_reference", "accepted 2026 context", "Western Basin vector ecology and surveillance", "county/habitat/program", "Phase 12 vector presence, pathogen-in-vector, and surveillance context", "accepted reference layer", "accepted Phase 12A/B/C package", "not re-counted in Phase 13A", "Phase 12 denominators remain in Phase 12 artifacts", "accepted vector surveillance definitions", "vector sampling geography; not human exposure location", "observed", "phase12_vector", "accepted_reference", "high", "Phase 12 artifacts are frozen and remain unchanged.", "This observation explicitly documents reuse rather than rebuilding vector ecology."],
    ["IDO-022", "REF-9", "accepted_reference", "accepted 2026 context", "Western Basin climate and hazard interfaces", "station/county/watershed/shoreline", "temperature, precipitation, flooding, drought, and seasonal context", "accepted reference layer", "accepted Phase 9A/B/C package", "not re-counted in Phase 13A", "Phase 9 denominators remain in Phase 9 artifacts", "accepted climate observation definitions", "native Phase 9 geography; not disease exposure location", "observed", "phase9_climate", "accepted_reference", "high", "No climate-to-disease causation is assumed.", "Context only."],
    ["IDO-023", "REF-11", "accepted_reference", "accepted 2026 context", "Western Basin population and settlement interfaces", "county/place/generalized employment", "population, settlement, workplace, and mobility context", "accepted reference layer", "accepted Phase 11A/B/C package", "not re-counted in Phase 13A", "Phase 11 denominators remain in Phase 11 artifacts", "accepted aggregate population definitions", "county/place/generalized geography; not individual exposure or case location", "observed", "phase11_population", "accepted_reference", "high", "No neighborhood disease inference is made.", "Context only."],
    ["IDO-024", "REF-4", "accepted_reference", "accepted 2026 context", "Western Basin observation and information systems", "station/program/agency", "public observation, data, uncertainty, and decision interfaces", "accepted reference layer", "accepted Phase 4A/B package", "not re-counted in Phase 13A", "Phase 4 denominators remain in Phase 4 artifacts", "accepted observation-system definitions", "observation geography; not case or exposure geography", "observed", "phase4_information", "accepted_reference", "high", "Monitoring coverage remains heterogeneous.", "Context only."],
    ["IDO-025", "REF-10", "accepted_reference", "accepted 2026 context", "Western Basin governance and institutional roles", "agency/program/jurisdiction", "reporting, monitoring, response, and authority interfaces", "accepted reference layer", "accepted Phase 10A/B/C package", "not re-counted in Phase 13A", "Phase 10 denominators remain in Phase 10 artifacts", "accepted institutional-role definitions", "jurisdictional reporting basis; not a disease geography", "observed", "phase10_governance", "accepted_reference", "high", "Monitoring, advice, funding, ownership, and authority remain separate.", "Context only."],
]

SURV_COLUMNS = [
    "surveillance_id", "disease_or_pathogen", "reporting_period", "geography",
    "surveillance_system", "case_definition_or_surveillance_definition", "reporting_basis",
    "numerator", "denominator", "case_geography_basis", "exposure_geography_basis",
    "suppression_missingness", "source_id", "confidence", "uncertainty", "notes",
]
SURV_ROWS = [
    ["IDS-001", "West Nile virus", "2025", "Ohio; agency/county", "Ohio pooled mosquito surveillance", "pooled mosquito surveillance; positive-pool status", "agency and county mosquito-pool testing", "42 counties with positive pools", "11,980 pooled samples; 58 agencies; 49 counties", "not applicable; vector sampling geography", "not applicable; no human exposure geography", "species and county effort not supplied", "phase12_vector_findings", "high", "positive pool != human infection/case/local transmission", "Retains program effort and positive-pool results separately."],
    ["IDS-002", "West Nile virus", "2025", "Ohio; county of residence", "Ohio human disease surveillance", "reported human WNV case map", "reported cases to state public health", "45 reported cases", "not meaningful for case count context", "county of residence", "exposure location not supplied", "case map does not resolve exposure or infection location", "phase12_vector_findings", "high", "residence != exposure; case != local transmission", "Contextual human-case record only."],
    ["IDS-003", "West Nile virus", "2023", "Michigan participating jurisdictions", "Michigan MDHHS/local mosquito surveillance", "pooled mosquito surveillance; positive-pool status", "local health-department sampling and laboratory testing", "124 WNV-positive pools", "6,351 mosquito pools tested", "not applicable; sampling geography", "not applicable; no human exposure geography", "participating jurisdictions and methods vary", "s13_mi_vector", "high", "positive pool != human case/incidence", "Program denominator is not merged with Ohio or Indiana."],
    ["IDS-004", "West Nile virus", "2026 dated update", "Indiana; 33 counties", "Indiana mosquito testing", "mosquito testing positive status", "state/county mosquito testing summary", "33 counties with positive mosquito tests", "not supplied", "not applicable; sampling geography", "not applicable; no human exposure geography", "effort and species counts not supplied", "s13_ind_wnv_2026", "moderate", "positive mosquito != human infection/case", "State summary retained without a comparable denominator."],
    ["IDS-005", "West Nile virus", "2026 dated update", "Allen County, Indiana; residence", "Indiana human surveillance", "reported human WNV case", "state public-health case reporting", "one reported case", "not meaningful for this context", "county of residence", "exposure location not supplied", "source release provides no exposure location", "s13_ind_wnv_2026", "high", "residence != exposure; reported case != local transmission", "Context only."],
    ["IDS-006", "Lyme disease", "2023/current context", "United States; state/county residence context", "CDC/NNDSS Lyme surveillance", "CDC Lyme case-surveillance context", "state health department case reporting", "reported cases; regional value not extracted", "not supplied for this package", "state/county of residence context", "exposure location not necessarily identified", "case geography and underdiagnosis/reporting limitations remain", "s13_cdc_lyme", "high", "case != exposure location/transmission", "No Western Basin case count or local map is generated."],
    ["IDS-007", "Legionellosis", "2014–2025; 2024–2025 provisional", "United States and jurisdictions", "CDC legionellosis surveillance", "Legionellosis national surveillance systems and disease-specific case definition", "jurisdictional case reporting plus supplemental surveillance", "reported cases/incidence; regional value not extracted", "jurisdiction/year-specific", "jurisdiction/case reporting geography", "investigation-specific exposure setting; not inferred", "provisional years and system combination", "s13_cdc_legionella_surv", "high", "reported case != environmental source attribution", "Source page supports system structure and provisional status; no local count fabricated."],
    ["IDS-008", "Waterborne disease outbreaks", "current system", "United States; state/local/territorial investigations", "CDC waterborne surveillance/NORS", "two or more epidemiologically linked people plus water implicated as probable source for an outbreak definition", "epidemiologic outbreak investigation/reporting", "investigated outbreak reports", "not a denominator for all infections", "investigation-specific time/location/illness linkage", "exposure location is investigation evidence", "reporting depends on investigation and identification", "s13_cdc_water_surv", "high", "contamination != exposure/infection/illness", "Definition and reporting interface only; no Western Basin outbreak is asserted."],
    ["IDS-009", "Foodborne and enteric pathogens", "current system", "United States; state/local/territorial partners", "CDC NORS/SEDRIC", "outbreak reporting categories for foodborne, animal-contact, person-to-person, environmental, and other enteric outbreaks", "public-health outbreak reporting", "reported outbreaks", "not a denominator for all infections", "outbreak investigation geography", "exposure setting is outbreak-specific", "non-reporting is not absence", "s13_cdc_nors", "high", "outbreak report != incidence", "Retained as an outbreak-observation system distinct from case surveillance."],
    ["IDS-010", "Salmonella, Campylobacter, and STEC", "current system", "United States; state/territorial public-health laboratories", "CDC national enteric laboratory surveillance/LEDS plus NNDSS", "laboratory identification and case-based surveillance definitions", "laboratory and case reporting", "identified infections; package does not extract regional numerators", "not supplied in source page", "case reporting/residence fields vary", "exposure information is condition-specific and not assumed", "laboratory and case completeness vary", "s13_cdc_enteric", "high", "lab-confirmed/reporting != all community infection", "Three foodborne systems remain distinct within one surveillance interface."],
    ["IDS-011", "FoodNet pathogen set", "current page; reporting changes after 2025-07-01", "FoodNet surveillance area", "FoodNet active surveillance", "laboratory-diagnosed infection surveillance and active clinical-laboratory follow-up", "CDC/USDA/FDA/ten state health departments collaboration", "eight historically tracked pathogens", "surveillance area includes 16% of U.S. population", "surveillance-area reporting; not Western Basin residence", "exposure fields are infection-specific", "post-2025 reporting optional for most pathogens except Salmonella and STEC", "s13_cdc_foodnet", "high", "program coverage != Western Basin incidence", "Scope and denominator context only."],
    ["IDS-012", "Influenza A/B", "2026 weekly interface", "United States/HHS region/state and stream-specific systems", "CDC FluView/FluView Interactive", "component-specific laboratory, outpatient, hospitalization, mortality, and other surveillance definitions", "multi-partner weekly reporting", "stream-specific observations; no package numerator", "stream-specific laboratory/outpatient/hospital denominators", "stream-specific geography", "exposure location not part of most streams", "weekly data preliminary; testing practices differ", "s13_cdc_flu_methods", "high", "testing intensity != disease intensity; hospitalization != community incidence", "System example only; no large pandemic dataset reproduced."],
    ["IDS-013", "SARS-CoV-2 and tracked respiratory viruses", "2026 current program", "community/sewershed/state/regional/national", "CDC wastewater monitoring", "wastewater viral measurement and trend interpretation", "sewershed sample collection and laboratory measurement", "viral activity measurements/trend signals", "sewershed population coverage, not infection denominator", "sewershed/community geography", "not individual exposure or residence", "septic and disconnected populations may be underrepresented; infection count not determinable", "s13_cdc_wastewater", "high", "wastewater signal != infection count/incidence", "Complementary community-level observation."],
    ["IDS-014", "Rabies virus", "current system", "United States; animal and exposure investigations", "animal rabies testing and PEP interface", "animal testing, potential-exposure assessment, and PEP response records", "animal-control/veterinary/public-health reporting", "animal tests/exposure/PEP records; no regional numerator extracted", "not a denominator for all animal contact", "animal test or exposure-investigation geography", "exposure investigation location; residence not substituted", "event- and response-dependent", "s13_cdc_rabies", "high", "animal case/exposure/PEP != human infection/disease", "Zoonotic interface retained without an animal or human risk ranking."],
    ["IDS-015", "Healthcare-associated infections", "current system", "healthcare facilities/state/regional/national", "CDC NHSN", "standardized facility HAI surveillance definitions and measures", "facility reporting and public-health/CMS reporting interfaces", "facility-reported HAI measures; local value not extracted", "participating facilities and measure-specific denominators", "facility/state reporting geography", "facility acquisition context; not community exposure geography", "participation and measure coverage vary", "s13_cdc_nhsn", "high", "facility surveillance != community incidence", "Generalized institutional system only."],
    ["IDS-016", "Antimicrobial resistance", "2019 national report context", "United States; national", "CDC AR threat and surveillance context", "AR threat categories and report-specific estimation methods", "national laboratory/healthcare/public-health context", "national estimates; not used as regional numerator", "national/report-specific", "national estimate geography", "not Western Basin exposure geography", "national estimates and older report year", "s13_cdc_ar", "moderate", "national estimate != Western Basin burden", "No local prevalence, resistance map, or facility ranking."],
    ["IDS-017", "Reportable infectious conditions", "2026 current page", "Indiana provider/hospital reporting", "Indiana communicable disease reporting", "state reportable-condition list and NBS/forms instructions", "healthcare provider, hospital, laboratory, and public-health reporting", "reports submitted under state rules", "not a uniform condition-specific denominator", "condition-specific reporting geography", "condition-specific exposure fields", "reportability and completeness are condition-specific", "s13_ind_reportable", "high", "reporting pathway != incidence", "State infrastructure context."],
]

UNC_COLUMNS = ["uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"]
UNC_ROWS = [
    ["IDU-001", "DID-001", "vector_to_human", "Positive mosquito pools and vector detections do not establish human infection, clinical disease, or local transmission.", "qualified", "s13_cdc_wnv", "high", "Vector detection != pathogen-positive vector != human infection."],
    ["IDU-002", "DID-002", "case_geography", "Lyme case residence geography does not identify the place of exposure or local transmission.", "qualified", "s13_cdc_lyme", "high", "Reported case != place of exposure."],
    ["IDU-003", "DID-003", "environmental_chain", "Building-water or aerosol pathway context does not establish contamination, treatment failure, exposure, infection, or illness.", "qualified", "s13_cdc_legionella_about", "high", "Direct evidence chain required."],
    ["IDU-004", "DID-004", "water_chain", "Source-water contamination, microbial indicators, HABs, nutrient loading, or infrastructure age do not independently establish illness.", "qualified", "s13_cdc_water_surv", "high", "Contamination != exposure != infection != reported case."],
    ["IDU-005", "DID-004", "outbreak_reporting", "NORS and waterborne outbreak reports are investigation-dependent and non-reporting is not pathogen absence.", "open", "s13_cdc_nors", "high", "Outbreak surveillance is not a continuous incidence series."],
    ["IDU-006", "DID-005", "enteric_coverage", "Laboratory-based Salmonella, Campylobacter, and STEC reporting does not capture all community infections or all exposures.", "open", "s13_cdc_enteric", "high", "Detection depends on care-seeking, testing, laboratory methods, and reporting."],
    ["IDU-007", "DID-006", "foodnet_scale", "FoodNet coverage and participation do not support Western Basin county or neighborhood estimates.", "open", "s13_cdc_foodnet", "high", "FoodNet surveillance area != Western Basin."],
    ["IDU-008", "DID-008", "respiratory_denominators", "Influenza laboratory positivity, outpatient visits, hospitalizations, and mortality have different denominators and are not one transmission rate.", "qualified", "s13_cdc_flu_methods", "high", "Testing intensity != disease intensity; hospitalization != community incidence."],
    ["IDU-009", "DID-009", "wastewater_interpretation", "Wastewater data provide community-level signals but cannot currently determine the number of infections.", "qualified", "s13_cdc_wastewater", "high", "Sewershed coverage and shedding variation remain important limits."],
    ["IDU-010", "DID-010", "zoonotic_endpoints", "Animal rabies cases, potential exposures, PEP, human infection, and human disease are distinct records.", "qualified", "s13_cdc_rabies", "high", "Animal-human interface does not imply human disease."],
    ["IDU-011", "DID-011", "facility_scale", "NHSN facility participation and HAI measures do not represent community incidence or permit a facility ranking in this baseline.", "open", "s13_cdc_nhsn", "high", "Healthcare surveillance remains generalized."],
    ["IDU-012", "DID-012", "regional_transfer", "National antimicrobial-resistance estimates are not transferred to the Western Basin.", "qualified", "s13_cdc_ar", "moderate", "National estimate != regional observation."],
    ["IDU-013", "HOST-001", "population_interface", "Population, settlement, workplace, and mobility context identify system interfaces only; they do not establish contact, exposure, infection, or disease.", "qualified", "phase11_population", "high", "County/place scale is retained."],
    ["IDU-014", "INST-001", "surveillance_effort", "Surveillance intensity, testing availability, reporting infrastructure, and laboratory participation are not incidence.", "qualified", "phase4_information", "high", "Observation effort != disease intensity."],
    ["IDU-015", "DID-013", "toxic_infectious_boundary", "HAB toxic/environmental pathways are not folded into an infectious-disease system or composite score.", "qualified", "phase7_exposure", "high", "Toxicity and infection remain separate."],
    ["IDU-016", "REF-12", "frozen_reuse", "Phase 12A/B/C accepted artifacts are reused by reference and remain immutable during Phase 13A.", "qualified", "phase12_vector", "high", "No vector ecology rebuild or modification."],
    ["IDU-017", "REF-9", "climate_boundary", "Accepted climate observations provide environmental context but do not establish causal disease incidence or future behavior.", "qualified", "phase9_climate", "high", "Historical climate behavior != future disease baseline."],
    ["IDU-018", "REF-10", "governance_boundary", "Institutional monitoring, advice, funding, and information are not automatically operational control or legal authority.", "qualified", "phase10_governance", "high", "Governance roles remain distinct."],
]


def normalize_url(url: str) -> str:
    return url.rstrip("/") or url


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_rows(name: str, rows: list[list[str]], columns: list[str]) -> None:
    assert all(len(row) == len(columns) for row in rows), name


def write_csv(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    assert_rows(str(path), rows, columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, lineterminator="\n")


def ensure_ledger() -> None:
    if LEDGER.exists():
        return
    LEDGER.write_text(json.dumps({"version": 1, "sources": [{"id": i, "url": normalize_url(url), "title": "", "accessed": RETRIEVAL_DATE} for i, url in enumerate(CITATION_URLS, 1)]}, indent=2) + "\n", encoding="utf-8", newline="\n")


def citation_block() -> str:
    return "\n## Sources\n\n" + "\n".join(f"[{i}] {normalize_url(url)}" for i, url in enumerate(CITATION_URLS, 1)) + "\n"


def metadata(paths: list[Path]) -> dict[str, dict[str, object]]:
    return {str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in paths}


def load_layers():
    huc8 = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wetlands = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flowlines = gpd.read_file(GPKG, layer="hydrography_physical")
    flowlines["geometry"] = flowlines.geometry.simplify(0.002, preserve_topology=False)
    return huc8, lake, wetlands, flowlines


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"id=\"p[0-9a-f]+\"", 'id="p13vector"', text)
    text = re.sub(r"url\(#p[0-9a-f]+\)", "url(#p13vector)", text)
    generated_marker_ids = list(dict.fromkeys(re.findall(r"\bm[0-9a-f]{6,}\b", text)))
    for index, token in enumerate(generated_marker_ids, 1):
        text = text.replace(token, f"p13marker{index}")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def save_map(fig: plt.Figure) -> None:
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(MAP_BASE.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(MAP_BASE.with_suffix(".svg"))


def render_map() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc8, lake, wetlands, flowlines = load_layers()
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc8.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.42)
    flowlines.plot(ax=ax, color="#4a8798", linewidth=0.28, alpha=0.48)
    anchors = [
        ("vector surveillance", -83.56, 41.66, "#6b4b91", "o"),
        ("water / Legionella", -83.22, 41.69, "#2b7182", "s"),
        ("enteric / foodborne", -83.37, 41.50, "#b26d32", "D"),
        ("respiratory / wastewater", -83.92, 41.78, "#c8643f", "^"),
        ("animal-human", -84.10, 41.27, "#4c8a69", "P"),
        ("healthcare / HAI / AR", -83.54, 41.57, "#355f7d", "X"),
        ("public-health reporting", -83.72, 41.92, "#9a4f59", "h"),
    ]
    for label, x, y, color, marker in anchors:
        ax.scatter([x], [y], s=160, facecolors="#f1eadc", edgecolors=color, marker=marker, linewidth=1.8, zorder=7)
        ax.text(x, y - 0.035, label, fontsize=7.0, color=color, ha="center", va="top", zorder=8)
    for i, j in [(0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (0, 2), (1, 3)]:
        x1, y1 = anchors[i][1], anchors[i][2]
        x2, y2 = anchors[j][1], anchors[j][2]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, linewidth=0.9, color="#6e6a60", alpha=0.42, connectionstyle="arc3,rad=0.08", zorder=4))
    ax.text(-83.42, 41.77, "Western Lake Erie", fontsize=11, weight="bold", color="#235a68", ha="center")
    ax.text(-83.57, 41.42, "Maumee River / tributary context", fontsize=8.5, color="#285f71", rotation=18, ha="center")
    ax.set_xlim(-84.55, -82.55)
    ax.set_ylim(40.9, 42.15)
    ax.set_axis_off()

    side = fig.add_axes([0.67, 0.055, 0.30, 0.88])
    side.axis("off")
    side.text(0.03, 0.98, "MAP 41 — WESTERN BASIN\nINFECTIOUS DISEASE SYSTEM\nBASELINE, 2026", va="top", fontsize=13.3, weight="bold", color="#17384b", linespacing=1.16)
    side.text(0.03, 0.835, "Generalized surveillance geography and transmission-system interfaces over accepted water, climate, population, vector, observation, and governance context. Markers are not cases, facilities, exposure sites, or risk surfaces.", va="top", fontsize=8.1, color="#3f4645", linespacing=1.3)
    side.text(0.03, 0.69, "SYSTEM ARCHETYPES", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.655, "• Vector: West Nile virus; Lyme disease\n• Water/environment: Legionella; enteric waterborne systems\n• Foodborne: Salmonella; Campylobacter; STEC\n• Respiratory: influenza; SARS-CoV-2 wastewater\n• Zoonotic: rabies\n• Institutional: HAI and antimicrobial-resistance surveillance", va="top", fontsize=7.55, color="#3f4645", linespacing=1.32)
    side.text(0.03, 0.425, "OBSERVATION SYSTEMS", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.39, "NNDSS; Ohio/Michigan/Indiana reporting; ArboNET and vector programs; Legionellosis surveillance; NORS/SEDRIC; enteric laboratory surveillance; FoodNet; FluView; wastewater monitoring; rabies response; NHSN; AR systems.", va="top", fontsize=7.55, color="#3f4645", linespacing=1.32)
    side.text(0.03, 0.235, "BOUNDARY", fontsize=9.8, weight="bold", color="#17384b")
    side.text(0.05, 0.20, "Pathogen presence ≠ exposure ≠ infection ≠ reported case ≠ local transmission ≠ outbreak ≠ disease burden. Surveillance intensity ≠ incidence. Residence ≠ exposure location. County ≠ neighborhood. No individual cases, downscaling, composite disease score, outbreak forecast, or future scenario.", va="top", fontsize=7.45, color="#3f4645", linespacing=1.28)
    side.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1eadc", markeredgecolor="#6b4b91", markersize=7, label="vector surveillance interface"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#f1eadc", markeredgecolor="#2b7182", markersize=7, label="water/environment interface"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#f1eadc", markeredgecolor="#b26d32", markersize=7, label="enteric/foodborne interface"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#f1eadc", markeredgecolor="#c8643f", markersize=7, label="respiratory/wastewater interface"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="accepted water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="accepted wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.01), frameon=False, fontsize=7.0)
    save_map(fig)


def reports(nodes: pd.DataFrame, relationships: pd.DataFrame, observations: pd.DataFrame, surveillance: pd.DataFrame, uncertainties: pd.DataFrame) -> dict[str, str]:
    coverage = """\n## Source coverage\n\nNational case surveillance and reported occurrence are documented by [1][2][3].\n\nVector, Lyme, and Legionella system context is documented by [4][5][6].\n\nWaterborne, NORS, and enteric surveillance structure is documented by [7][8][9].\n\nFoodNet, FluView, and influenza methods are documented by [10][11][12].\n\nWastewater, rabies, and healthcare surveillance are documented by [13][14][15].\n\nAntimicrobial-resistance, Indiana reporting, and Ohio vector context are documented by [16][17][18].\n\nMichigan vector context and accepted Phase 7/9 layers are documented by [19][20][21].\n\nAccepted Phase 11/12/4 context is documented by [22][23][24].\n\nAccepted Phase 10 governance context is documented by [25].
Indiana WNV context is documented by [26].
The fixed Phase 12A findings reference is documented by [27].\n"""
    src = coverage + citation_block()
    source_report = """# Phase 13A Infectious Disease System Baseline Sources

The baseline uses CDC NNDSS and CDC WONDER for the national case-surveillance and reporting frame.[1][2]

West Nile and Lyme disease are represented as distinct vector-borne systems. West Nile reporting is linked to the accepted Phase 12 vector ecology context without rebuilding vector ecology.[3][4][23]

Legionellosis surveillance and Legionella transmission context are sourced separately so a building-water pathway is not confused with a reported case.[5][6]

Waterborne surveillance and NORS provide outbreak-investigation and reporting-system context.[7][8]

CDC national enteric surveillance and FoodNet support separate Salmonella, Campylobacter, and STEC system representations.[9][10]

Influenza surveillance uses FluView and its methods page to keep laboratory, outpatient, hospitalization, mortality, and other streams distinct.[11][12]

CDC wastewater material is used as a community-level observation interface, not an infection count.[13]

Rabies, NHSN, and antimicrobial-resistance material provide generalized zoonotic and healthcare/institutional surveillance contexts.[14][15][16]

Indiana reportable-disease material provides state reporting context.[17]
Accepted Ohio and Michigan vector summaries provide state surveillance context.[18][19]
The Indiana WNV release supplies the dated positive-mosquito and human-case context.[26]
The protected Phase 12A findings report preserves the exact dated Ohio values reused here.[27]

Accepted Phase 7, 9, and 11 layers are reused only as protected context references.[20][21][22]
Phase 12, Phase 4, and Phase 10 references are also protected.[23][24][25]

The source registry records reporting period, geographic scale, method, evidence use, use limitations, and retrieval provenance for each source.[1][2][20]
No external source is used to justify an unsupported local case surface, risk score, or outbreak forecast.[7][13][25]
""" + src
    assumptions = f"""# Phase 13A Infectious Disease System Baseline Assumptions

## Product boundary

This is a compact factual 2026 infectious-disease systems baseline with {len(nodes)} nodes, {len(relationships)} transmission/system relationships, {len(observations)} observations, and {len(surveillance)} surveillance records.[1][2]
It includes {len(uncertainties)} explicit uncertainties.[20]
It is not a disease-risk ranking, outbreak forecast, burden model, or individual health product.[7][13]

## Included systems

The package includes West Nile virus; Lyme disease; Legionellosis; a multi-agent waterborne enteric system; Salmonella; Campylobacter; STEC; influenza; SARS-CoV-2 wastewater surveillance; rabies; generalized HAI surveillance; and generalized antimicrobial-resistance surveillance.[3][4][5]
HAB is represented only as a noninfectious toxic/environmental boundary.[7][20]
The categories are not combined into a single index.[15]

## Evidence and reporting ladder

Pathogen presence, environmental interface, potential exposure, infection, reported case, local transmission, outbreak, and disease burden are separate statuses.[1][7][13]
Surveillance intensity is not incidence. Reported case geography is not exposure geography. Non-reporting is not pathogen absence. County records are not neighborhood records. Vector detection is not pathogen-positive vector, human infection, or clinical disease. Water contamination is not treatment failure, exposure, infection, or illness.[3][4][7]

Every surveillance row retains the system, reporting period, geography, surveillance system, case or surveillance definition, reporting basis, numerator, denominator where meaningful, case geography, exposure geography, suppression/missingness, source, and uncertainty.[1][2][9]
Values are left qualified or unextracted when a source does not support a comparable regional numerator.[10][12]

## Reused layers and scale

Phase 12 vector ecology, Phase 7 exposure/environmental health, Phase 9 climate, Phase 11 population/settlement, Phase 4 observation/information, and Phase 10 governance are linked by accepted reference nodes and source IDs.[20][21][22]
Their accepted/frozen artifacts are not copied into new disease tables or modified.[23][24][25]
Native scales remain county, state, program, station, watershed, sewershed, facility, and generalized regional context as supported.[4][13][15]

Map 41 is a hybrid geographic/schematic view.[13][24]
Its markers are generalized system interfaces, not individual cases, facilities, exposure locations, or continuous disease surfaces. No case is downscaled below its source geography.[4][22]

## Exclusions

No composite infectious-disease risk index, vulnerability score, county danger ranking, neighborhood ranking, individual infection probability, individual case map, personal health data, unsupported outbreak forecast, causal attribution from coincidence, disease-burden aggregation across unlike diseases, or Phase 13B/13C implementation is present.[7][13][15]
No future inference is included.[20][21]

Great Black Swamp remains C — HOLD / noncanonical.[21]
The Toledo intake-coordinate discrepancy remains UNRESOLVED.[20]
Phase 6B manifest wording mismatch and Phase 3A missing manifest status remain deferred and unchanged.[21]
""" + src
    findings = """# Phase 13A Infectious Disease System Baseline Findings, 2026

## Dominant transmission-system types

FACT: The baseline is organized into vector-borne, waterborne/environmental, and foodborne/enteric surveillance archetypes rather than one disease category.[3][5][7]

FACT: Respiratory, zoonotic, and healthcare/institutional systems are represented separately.[9][11][14]

INFERENCE: Western Basin infectious-disease structure is best understood as several observation and response systems that meet at environmental interfaces, hosts, healthcare, laboratories, and jurisdictions.[1][9][15]
This is a systems interpretation, not a comparative disease-burden ranking.[20]

FACT: West Nile and Lyme disease require distinct vector systems. Accepted Phase 12 records provide vector ecology and surveillance context, but this phase does not infer human infection or disease from vector ecology.[3][4][23]

FACT: Legionellosis is a nationally notifiable condition with two national surveillance systems, while CDC describes Legionella transmission through aerosolized water and generally not person-to-person spread.[5][6]

FACT: CDC waterborne surveillance defines a waterborne disease outbreak through epidemiologic linkage and evidence implicating water as the probable source. NORS collects outbreak reports from public-health partners across waterborne, foodborne, animal-contact, environmental, and enteric categories.[7][8]

FACT: CDC national enteric surveillance includes laboratory-based surveillance for Campylobacter, Salmonella, Shigella, and STEC. FoodNet provides a separate active-surveillance network covering eight pathogens in a surveillance area that includes 16% of the U.S. population and ten state health departments.[9][10]

FACT: FluView is a weekly, preliminary, multi-partner surveillance product. Its methods distinguish laboratory, outpatient, hospitalization, mortality, and other streams with different denominators and interpretations.[11][12]

FACT: CDC wastewater data provide a community-level observation and early-warning perspective, but CDC states that the number of infections should not currently be determined from wastewater.[13]

FACT: CDC describes rabies as an animal-human interface involving wildlife and domestic animals, potential exposure, and post-exposure prophylaxis. Animal surveillance, exposure assessment, human infection, and human disease are distinct endpoints.[14]

FACT: CDC NHSN is a facility reporting and HAI tracking system used by healthcare facilities and public-health partners. It is not a community-incidence system.[15]

## Surveillance strengths

INFERENCE: The strongest regional structure is the existence of state and local reportable-disease reporting, NNDSS, and vector and mosquito-pool surveillance.[1][2][3]

INFERENCE: Laboratory-based enteric surveillance, influenza multi-stream surveillance, wastewater monitoring, animal rabies response, NHSN, and generalized AR surveillance are additional established observation channels.[9][11][13]

INFERENCE: The healthcare and antimicrobial-resistance channels remain institutionally distinct from community case surveillance.[14][15][16]

FACT: Ohio's accepted vector-surveillance context reports 11,980 pooled mosquito samples from 58 agencies in 49 counties and WNV-positive pools in 42 counties in 2025. The same accepted context reports 45 Ohio WNV cases by county of residence. These are different surveillance products with different numerators and geographies.[27]

FACT: Michigan's accepted vector-surveillance context reports 6,351 mosquito pools tested and 124 WNV-positive pools in its 2023 annual summary.[19]
FACT: Indiana's cited 2026 summary reports positive mosquito tests in 33 counties and one human WNV case in an Allen County resident.[18][26]
These values are not merged into a cross-state incidence or abundance index.[3]

## Environmental, vector, population, and institutional interfaces

INFERENCE: Environmental interfaces are pathway contexts rather than disease outcomes.[5][6][7]
Drinking/recreational water, building water/aerosols, food/animal environments, respiratory sewersheds, and accepted climate/hydrology context connect to surveillance only through condition-specific evidence and investigation.[20][21]

INFERENCE: Population and settlement concentration, workplace context, and mobility can identify where observation and response systems meet human hosts at county/place/generalized scales. They do not establish contact, exposure, infection, or disease.[22]

INFERENCE: Vector ecology is a prerequisite context for understanding surveillance architecture, not a human disease burden surface. Phase 12 is linked by explicit reference nodes; it is not rebuilt or converted into an infectious-disease score.[23]

INFERENCE: Governance and observation systems determine how signals can be reported, interpreted, and acted on, but monitoring is not control and information availability is not complete surveillance or response effectiveness.[24][25]

## Principal surveillance limitations

UNCERTAINTY: Disease systems use incompatible case definitions, denominators, sampling frames, reporting periods, and ascertainment pathways.[1][2][9]
Therefore the package does not compare unlike diseases or rank counties.[10][11][12]

UNCERTAINTY: Vector sampling effort, pooled mosquito results, tick status, human case reporting, wastewater viral activity, laboratory confirmation, hospital reporting, and animal testing have different observation units.[3][4][23]
Positive vectors, environmental signals, or surveillance intensity cannot be read as infection, incidence, or burden.[13][14]

UNCERTAINTY: Reported residence, reporting jurisdiction, sewershed, facility, sampling site, and investigated exposure location are different geographies.[4][7][13]
No record is downscaled to a neighborhood, census tract, municipality, or individual facility.[22]

UNCERTAINTY: Missing, suppressed, provisional, optional, or non-comparable observations remain limitations.[5][8][10]
Absence of a reported case or a surveillance record is not interpreted as pathogen absence.[11][17]

## Health boundary

FACT/BOUNDARY: The baseline does not assert disease burden, individual risk, local transmission, outbreak occurrence, causal exposure, dose, or illness from environmental coincidence.[7][13][20]
Pathogen presence, exposure, infection, reported case, local transmission, outbreak, and disease burden remain separate states.[1][3][5]
""" + src
    qa = f"""# Phase 13A Infectious Disease System Baseline QA

The package contains {len(nodes)} nodes, {len(relationships)} relationships, {len(observations)} observations, {len(surveillance)} surveillance records, {len(SOURCE_ROWS)} source records, and {len(uncertainties)} uncertainty records.[1][2]
Map 41 PNG/SVG is included as the geographic/schematic product.[24]

The Phase 13A Python validator checks exact row schemas and widths, unique IDs, source references, relationship endpoints, system-category vocabulary, surveillance reporting-basis fields, numerator/denominator semantics, residence-versus-exposure fields, vector/water/respiratory/healthcare boundaries, scale limits, explicit uncertainty, active holds, no scoring fields, no individual cases, no future rows, Map 41 text/raster integrity, phase-local manifest hashes, and Phase 1–12 freeze integrity.[1][7][13]

The independent R validator re-reads the generated CSVs through an independent code path, checks the same counts and references, recomputes artifact hashes, checks Map 41 PNG/SVG presence and required text, verifies negative scope and active holds, and checks that Phase 13B/13C products are not implemented.[23][24]

Semantic checks explicitly reject: ecological suitability as disease burden; case counts as transmission rates; residence as exposure location; surveillance intensity as incidence; non-reporting as absence; environmental contamination as illness; positive vector/pathogen detection as human infection; incompatible diseases combined into a composite score; unsupported local downscaling; and unsupported future inference.[3][7][13]

Accepted/frozen Phase 1–12 artifacts are checked through their existing manifests and are not rewritten by this phase.[20][21][22]
Great Black Swamp remains C — HOLD / noncanonical, the Toledo intake-coordinate discrepancy remains UNRESOLVED, and deferred historical metadata maintenance remains unchanged.[21]

No vulnerability score, individual risk field, disease-risk index, outbreak forecast, Phase 13B/13C implementation, release, or tag is included.[13][15][25]
""" + src
    return {
        "reports/infectious_disease_sources.md": source_report,
        "reports/infectious_disease_assumptions.md": assumptions,
        "reports/infectious_disease_findings.md": findings,
        "reports/infectious_disease_qa.md": qa,
    }


def write_manifest(paths: list[Path], counts: dict[str, int]) -> None:
    manifest = {
        "phase": "13A",
        "baseline": "Infectious Disease System Baseline, 2026",
        "status": "implemented_validated_pending_sol_acceptance",
        "map_number": 41,
        "counts": counts,
        "artifacts": metadata(paths),
        "protected_inputs": [
            "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
            "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
            "reports/phase11a_population_settlement_freeze_manifest.json",
            "reports/phase12a_vector_ecology_freeze_manifest.json",
            "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
            "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
        ],
        "phase12abc_accepted_frozen": True,
        "phase1_12_immutable": True,
        "phase13b_implemented": False,
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


def main() -> None:
    for rows, cols, name in [
        (SOURCE_ROWS, SOURCE_COLUMNS, "sources"), (NODE_ROWS, NODE_COLUMNS, "nodes"),
        (REL_ROWS, REL_COLUMNS, "relationships"), (OBS_ROWS, OBS_COLUMNS, "observations"),
        (SURV_ROWS, SURV_COLUMNS, "surveillance"), (UNC_ROWS, UNC_COLUMNS, "uncertainties"),
    ]:
        assert_rows(name, rows, cols)
    NETWORKS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    MAPS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ensure_ledger()

    paths: list[Path] = []
    products = [
        (NETWORKS / "infectious_disease_nodes.csv", NODE_COLUMNS, NODE_ROWS),
        (NETWORKS / "infectious_disease_transmission_relationships.csv", REL_COLUMNS, REL_ROWS),
        (ANALYSIS / "infectious_disease_observations.csv", OBS_COLUMNS, OBS_ROWS),
        (ANALYSIS / "infectious_disease_surveillance.csv", SURV_COLUMNS, SURV_ROWS),
        (ANALYSIS / "infectious_disease_sources.csv", SOURCE_COLUMNS, SOURCE_ROWS),
        (ANALYSIS / "infectious_disease_uncertainties.csv", UNC_COLUMNS, UNC_ROWS),
    ]
    for path, columns, rows in products:
        write_csv(path, columns, rows)
        paths.append(path)
    render_map()
    paths += [MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    for rel, text in reports(pd.DataFrame(NODE_ROWS, columns=NODE_COLUMNS), pd.DataFrame(REL_ROWS, columns=REL_COLUMNS), pd.DataFrame(OBS_ROWS, columns=OBS_COLUMNS), pd.DataFrame(SURV_ROWS, columns=SURV_COLUMNS), pd.DataFrame(UNC_ROWS, columns=UNC_COLUMNS)).items():
        path = ROOT / rel
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)
    for rel in [
        "docs/phase_briefs/phase13a_infectious_disease_baseline.md",
        "docs/phase_briefs/phase13b_infectious_disease_dependencies.md",
        "docs/phase_briefs/phase13c_infectious_disease_futures.md",
    ]:
        paths.append(ROOT / rel)
    for rel in [
        "reports/infectious_disease_independent_review_initial.md",
        "reports/infectious_disease_independent_review.md",
    ]:
        review_path = ROOT / rel
        if review_path.exists():
            paths.append(review_path)
    paths.append(LEDGER)
    paths += [
        ROOT / "src/python/systems/build_infectious_disease_baseline.py",
        ROOT / "src/python/systems/validate_infectious_disease_baseline.py",
        ROOT / "src/R/systems/validate_infectious_disease_baseline.R",
    ]
    counts = {
        "nodes": len(NODE_ROWS), "relationships": len(REL_ROWS), "observations": len(OBS_ROWS),
        "surveillance_records": len(SURV_ROWS), "sources": len(SOURCE_ROWS), "uncertainties": len(UNC_ROWS),
    }
    write_manifest(paths, counts)
    print(json.dumps({"status": "built", "map_number": 41, **counts}, indent=2))


if __name__ == "__main__":
    main()
