"""Build Phase 10A: Governance & Jurisdiction Baseline, 2026.

The package is deliberately a role registry, not a legal-opinion engine. It
records documented institutional functions at the level needed to connect the
accepted Western Basin physical systems to decision-making institutions.
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

ACTORS = [
    ["GA-001", "U.S. Environmental Protection Agency", "federal_agency", "federal", "United States / Great Lakes", "Water;Environmental Health / Exposure;Biogeochemical / Nutrient Flux;Ecology / Biodiversity", "Federal environmental standards, program oversight, permitting/enforcement authorities in defined programs, monitoring, and funding/coordination roles.", "s01_epa_sdwa", "high", "real", "verified", "EPA authority is program-specific; it is not the operator of Toledo's municipal water plant or private utilities."],
    ["GA-002", "Ohio Environmental Protection Agency", "state_agency", "state", "Ohio", "Water;Environmental Health / Exposure;Biogeochemical / Nutrient Flux;Ecology / Biodiversity;Climate / Natural Hazards", "Ohio water, air, public-water, NPDES, and related environmental regulatory and monitoring programs.", "s02_ohio_pws", "high", "real", "verified", "State permitting and regulation do not equal physical operation of public utilities, farms, or wetlands."],
    ["GA-003", "City of Toledo", "municipal_government", "municipal", "City of Toledo", "Water;Freight / Industry;Climate / Natural Hazards;Environmental Health / Exposure", "Municipal owner/authority for city services, including the public water system through its utility division.", "s03_toledo_treatment", "high", "real", "verified", "Municipal ownership and operation are distinct from Ohio EPA regulation."],
    ["GA-004", "City of Toledo Public Utilities — Water Treatment Division", "public_utility", "public utility", "Toledo service area and surrounding customers", "Water;Environmental Health / Exposure", "Operates and maintains the municipal surface-water treatment and distribution system and performs water-quality monitoring/reporting.", "s03_toledo_treatment", "high", "real", "verified", "The utility's operational responsibility does not make it the drinking-water regulator or the source-water scientific authority."],
    ["GA-005", "U.S. Geological Survey", "research_monitoring_body", "federal", "United States / monitoring locations", "Water;Climate / Natural Hazards;Data / Sensors / Security", "Collects and publishes water observations and scientific information through monitoring locations and data services.", "s06_usgs_data", "high", "real", "verified", "USGS observation and data roles do not confer regulatory, permitting, or operational control."],
    ["GA-006", "National Oceanic and Atmospheric Administration / National Weather Service", "federal_agency", "federal", "United States / forecast and warning areas", "Climate / Natural Hazards;Water;Data / Sensors / Security;Ecology / Biodiversity", "Provides weather, water, and climate observations, forecasts, warnings, and decision-support information.", "s36_nws", "high", "real", "verified", "Warning and information roles do not equal local emergency command or utility operation."],
    ["GA-007", "NOAA Great Lakes Environmental Research Laboratory", "research_monitoring_body", "federal", "Great Lakes / western Lake Erie", "Water;Ecology / Biodiversity;Climate / Natural Hazards;Data / Sensors / Security", "Great Lakes observing, research, modeling, and information products that inform management decisions.", "s07_glerl", "high", "real", "verified", "Scientific information is kept separate from legal decision authority and physical operation."],
    ["GA-008", "U.S. Army Corps of Engineers", "federal_agency", "federal", "United States / waters and projects within federal programs", "Ecology / Biodiversity;Water;Freight / Industry;Environmental Health / Exposure", "Regulatory permitting and related compliance functions for covered aquatic and infrastructure activities; separate civil-works and remediation functions are not treated as universal control.", "s07_usace_regulatory", "high", "real", "verified", "A permit role is not physical operation of every permitted project."],
    ["GA-009", "U.S. Fish and Wildlife Service", "federal_agency", "federal", "United States / national wetland and wildlife programs", "Ecology / Biodiversity;Water", "Wetland and habitat mapping, monitoring, conservation, technical information, and restoration/program roles.", "s08_usfws_nwi", "high", "real", "verified", "Ecological interest and data production do not by themselves establish a permit or enforcement authority."],
    ["GA-010", "Federal Emergency Management Agency", "federal_agency", "federal", "United States / state, tribal, local partners", "Climate / Natural Hazards;Water", "Flood-hazard information, mitigation planning guidance, and conditional assistance/funding mechanisms.", "s34_fema_nfhl", "high", "real", "verified", "FEMA data and funding roles do not make FEMA the local floodplain administrator or owner of local assets."],
    ["GA-011", "USDA Natural Resources Conservation Service", "federal_agency", "federal", "United States / Ohio agricultural programs", "Biogeochemical / Nutrient Flux;Water;Ecology / Biodiversity;Climate / Natural Hazards", "Technical and financial assistance for voluntary conservation planning and practices.", "s11_nrcs_ohio", "high", "real", "verified", "EQIP/CSP assistance is not a general regulatory mandate or direct control over farm operations."],
    ["GA-012", "Ohio Department of Agriculture", "state_agency", "state", "Ohio / agricultural programs", "Biogeochemical / Nutrient Flux;Water;Ecology / Biodiversity", "State agriculture program, coordination, and agriculture-specific regulatory/assistance context.", "s44_ohio_oda", "moderate", "real", "verified", "This baseline does not infer a universal individual nutrient obligation from program participation or targets."],
    ["GA-013", "Lucas Soil and Water Conservation District", "special_district", "special district", "Lucas County / conservation service area", "Biogeochemical / Nutrient Flux;Water;Ecology / Biodiversity", "Local technical assistance, planning, coordination, and participation in voluntary conservation programs.", "s10_h2ohio", "moderate", "real", "verified", "District assistance is not the same as state or federal regulatory authority."],
    ["GA-014", "Ohio Department of Natural Resources", "state_agency", "state", "Ohio", "Geology / Strategic Materials;Ecology / Biodiversity;Water;Climate / Natural Hazards", "State natural-resource management, monitoring, planning, restoration, and selected permitting/regulatory functions.", "s45_odnr", "limited", "real", "inferred", "The package does not infer authority for a particular site or wetland without a specific legal/program source."],
    ["GA-015", "Michigan Department of Environment, Great Lakes, and Energy", "state_agency", "state", "Michigan / Great Lakes waters", "Water;Ecology / Biodiversity;Climate / Natural Hazards;Biogeochemical / Nutrient Flux", "Michigan water-quality standards, assessment, monitoring, permitting, compliance, shoreline, and related environmental programs.", "s37_michigan_egle", "high", "real", "verified", "Michigan authority is represented as a neighboring state interface, not a Western Basin-wide jurisdiction."],
    ["GA-016", "Indiana Department of Environmental Management", "state_agency", "state", "Indiana", "Water;Biogeochemical / Nutrient Flux;Ecology / Biodiversity", "Neighboring-state environmental regulatory and coordination interface where watershed or Great Lakes matters cross state boundaries.", "s46_indiana_idem", "limited", "real", "inferred", "Specific Western Basin permit or facility authority is not mapped without a source-specific determination."],
    ["GA-017", "Great Lakes Commission", "interstate_body", "interstate", "Eight Great Lakes states and Canadian observers", "Water;Ecology / Biodiversity;Biogeochemical / Nutrient Flux", "Compact-created regional policy, coordination, and advisory institution.", "s13_glc", "high", "real", "verified", "The Commission recommends policies and brings actors together; it is not treated as a general environmental regulator."],
    ["GA-018", "Great Lakes–St. Lawrence Governors & Premiers", "binational_body", "binational", "Eight Great Lakes states and two provinces", "Water;Ecology / Biodiversity;Freight / Industry", "Executive-level regional coordination and policy framework for water management and restoration.", "s14_gsgp", "high", "real", "verified", "The framework is not substituted for state permits, federal regulation, or local operations."],
    ["GA-019", "International Joint Commission", "binational_body", "binational", "United States–Canada boundary waters", "Water;Ecology / Biodiversity;Data / Sensors / Security", "Binational reference, advisory, investigative, and coordination functions under the Boundary Waters Treaty framework.", "s16_ijc", "limited", "real", "inferred", "The available page was not fully retrievable in this run; no direct domestic permit or enforcement power is asserted."],
    ["GA-020", "U.S.–Canada Great Lakes Water Quality Agreement parties", "binational_body", "binational", "Great Lakes basin", "Water;Ecology / Biodiversity;Biogeochemical / Nutrient Flux", "Agreement framework for binational objectives, annex coordination, reporting, and implementation by responsible governments.", "s15_glwqa", "moderate", "real", "verified", "The agreement framework is not treated as a stand-alone domestic regulator or individual permit."],
    ["GA-021", "Great Lakes Indian Fish & Wildlife Commission", "tribal_sovereign", "tribal", "Treaty-ceded territories served by member Ojibwe tribes", "Ecology / Biodiversity;Water;Data / Sensors / Security", "Intertribal natural-resource management, treaty-rights support, conservation enforcement support, legal/policy analysis, and public information.", "s17_glifwc", "high", "real", "verified", "GLIFWC is not a generic tribal actor and is not assigned current Western Basin jurisdiction without nation- and treaty-specific evidence."],
    ["GA-022", "Pokagon Band of Potawatomi Indians", "tribal_sovereign", "tribal", "Nation-specific government and citizens", "Water;Ecology / Biodiversity;Environmental Health / Exposure", "Federally recognized tribal government and potential consultation/resource-interest interface.", "s19_pokagon", "moderate", "real", "verified", "No current Western Basin territorial or permitting authority is inferred from sovereignty, history, or regional interest alone."],
    ["GA-023", "Little Traverse Bay Bands of Odawa Indians", "tribal_sovereign", "tribal", "Nation-specific government and Great Lakes treaty/resource context", "Water;Ecology / Biodiversity;Environmental Health / Exposure", "Nation-specific sovereign and treaty/resource-interest interface for consultation review.", "s20_ltbb", "limited", "real", "verified", "Current project-specific authority in the Western Basin remains unresolved and is not represented as a polygon."],
    ["GA-024", "Federal Energy Regulatory Commission", "federal_agency", "federal", "Interstate electricity and wholesale energy jurisdiction", "Energy / Grid / Compute", "Regulates interstate transmission and wholesale electricity, enforces requirements, oversees markets, and approves/oversees defined energy facilities.", "s21_ferc", "high", "real", "verified", "FERC is not local distribution operation, retail regulation, or utility ownership."],
    ["GA-025", "North American Electric Reliability Corporation", "interstate_body", "interstate", "North American bulk power system", "Energy / Grid / Compute", "Develops and administers reliability standards and compliance functions within the FERC-approved reliability framework.", "s23_nerc", "high", "real", "verified", "NERC standards are distinct from asset ownership and physical control of local facilities."],
    ["GA-026", "PJM Interconnection", "system_operator", "interstate", "PJM footprint including Ohio and Michigan interfaces", "Energy / Grid / Compute;Data / Sensors / Security", "Operates the wholesale electricity market, manages high-voltage grid operations, coordinates movement of wholesale electricity, and plans regionally.", "s24_pjm", "high", "real", "verified", "PJM is not a utility owner and is not the local distribution operator for every customer."],
    ["GA-027", "Public Utilities Commission of Ohio", "state_agency", "state", "Ohio utility and transportation services", "Energy / Grid / Compute;Water;Freight / Industry", "State economic and service regulation of specified utility and transportation providers.", "s25_puco", "high", "real", "verified", "PUCO regulation is distinct from physical generation, transmission, distribution, water-treatment, or freight operation."],
    ["GA-028", "U.S. Nuclear Regulatory Commission", "federal_agency", "federal", "United States civilian nuclear materials and facilities", "Energy / Grid / Compute;Environmental Health / Exposure", "Licensing, inspection, enforcement, and regulation of commercial nuclear power and other civilian nuclear materials.", "s26_nrc", "high", "real", "verified", "NRC nuclear regulation is distinct from grid-market operation and utility asset ownership."],
    ["GA-029", "U.S. Department of Energy", "federal_agency", "federal", "United States", "Energy / Grid / Compute;Data / Sensors / Security", "Federal research, coordination, technical assistance, and funding context for grid modernization.", "s27_doe", "moderate", "real", "verified", "DOE support and coordination do not equal local grid dispatch or ownership."],
    ["GA-030", "FirstEnergy / Toledo Edison", "private_operator", "private", "FirstEnergy Ohio electric service context", "Energy / Grid / Compute", "Investor-owned electric utility ownership and operation context for generation/transmission/distribution subsidiaries.", "s28_firstenergy", "high", "real", "verified", "The source does not establish a facility-specific Toledo service assignment; no exact local asset map is created."],
    ["GA-031", "Ohio Department of Transportation", "state_agency", "state", "Ohio public transportation system", "Freight / Industry;Climate / Natural Hazards", "State transportation planning, public-road ownership/operation context, and funding coordination.", "s39_odot", "moderate", "real", "verified", "Public highway responsibility is not operation of private rail, marine, or industrial networks."],
    ["GA-032", "Federal Highway Administration", "federal_agency", "federal", "United States / National Highway Freight Network", "Freight / Industry", "Federal freight planning, data, program guidance, and discretionary infrastructure funding.", "s29_fhwa", "high", "real", "verified", "FHWA funding/planning does not mean FHWA operates local roads or private freight carriers."],
    ["GA-033", "Federal Railroad Administration", "federal_agency", "federal", "United States rail network", "Freight / Industry;Climate / Natural Hazards", "Issues, implements, and enforces rail-safety regulations; selectively invests and conducts research/planning.", "s30_fra", "high", "real", "verified", "FRA regulation and funding are distinct from private railroad ownership and train operation."],
    ["GA-034", "Maritime Administration", "federal_agency", "federal", "United States maritime system", "Freight / Industry", "Federal maritime policy, assistance, and planning context for ports and marine transportation.", "s31_marad", "moderate", "real", "verified", "MARAD is not the operator of every port, terminal, vessel, or cargo movement."],
    ["GA-035", "Toledo-Lucas County Port Authority", "regional_authority", "regional authority", "Port-authority facilities and regional development programs", "Freight / Industry;Energy / Grid / Compute", "Public port-authority ownership, control, financing, development, and regional economic/transportation functions for authority facilities.", "s32_port", "high", "real", "verified", "Port-authority facilities and financing do not convert private rail, vessel, or industrial operations into public operation."],
    ["GA-036", "Norfolk Southern Railway", "private_operator", "private", "Private rail network / served facilities", "Freight / Industry", "Private railroad ownership and operation context.", "s41_norfolk_southern", "moderate", "real", "verified", "Public rail safety regulation and infrastructure funding do not establish public operation or ownership."],
    ["GA-037", "CSX Transportation", "private_operator", "private", "Private rail network / served facilities", "Freight / Industry", "Private railroad ownership and operation context.", "s42_csx", "moderate", "real", "verified", "Specific local route or facility authority is not inferred from the company identity."],
    ["GA-038", "Lucas County", "county_government", "county", "Lucas County", "Climate / Natural Hazards;Water;Environmental Health / Exposure;Freight / Industry", "County planning, coordination, public-service, and mitigation-partner context; precise delegated authority varies by program.", "s35_fema_mitigation", "moderate", "real", "inferred", "The package does not assume county ownership or control of all floodplains, utilities, roads, or private assets."],
    ["GA-039", "Toledo-Lucas County Health Department", "special_district", "special district", "Toledo and Lucas County health district", "Environmental Health / Exposure;Water;Climate / Natural Hazards", "Local public-health monitoring, advice, warning, and response interface.", "s40_lucas_health", "limited", "real", "verified", "Environmental monitoring or public-health advice is not automatically medical treatment authority over environmental systems or utility operation."],
    ["GA-040", "Ohio Department of Health", "state_agency", "state", "Ohio", "Environmental Health / Exposure;Water", "State public-health and private-water regulatory/monitoring context.", "s38_odh", "moderate", "real", "verified", "Medical/public-health authority is distinct from environmental permitting and municipal water operation."],
]

SOURCE_COLUMNS = ["source_id", "title", "url", "source_type", "evidence_role", "publication_or_update", "retrieval_date", "geographic_scope", "use_limitations", "retrieval_status"]
SOURCES = [
    ["s01_epa_sdwa", "National Primary Drinking Water Regulations", "https://www.epa.gov/ground-water-and-drinking-water/national-primary-drinking-water-regulations", "federal_regulation", "national drinking-water standards context", "current page", "2026-09-04", "United States", "Standards context; not a facility-specific operating record.", "retrieved"],
    ["s02_ohio_pws", "Understanding Public Water Systems", "https://epa.ohio.gov/divisions-and-offices/drinking-and-ground-waters/public-water-systems", "state_program", "Ohio public-water regulation and monitoring", "current page", "2026-09-04", "Ohio", "Program description does not assign a role to every local actor.", "retrieved"],
    ["s03_toledo_treatment", "City of Toledo Water Treatment", "https://toledo.oh.gov/departments/public-works/water/water-treatment", "municipal_primary_source", "municipal ownership and operation", "2020-06-19 page; current access", "2026-09-04", "Toledo service area", "Operator description; not an independent legal opinion.", "retrieved"],
    ["s04_toledo_quality", "City of Toledo Water Quality", "https://toledo.oh.gov/residents/water/quality", "municipal_primary_source", "water-quality monitoring and reporting", "updated 2026-06-01", "2026-09-04", "Toledo service area", "Public reporting and monitoring context; no undisclosed threshold is modeled.", "retrieved"],
    ["s05_ohio_npdes", "Ohio EPA DSW Permitting", "https://epa.ohio.gov/divisions-and-offices/surface-water/permitting", "state_regulatory_program", "NPDES, PTI, 401, and isolated-wetland permitting", "current page", "2026-09-04", "Ohio", "Program scope is not a facility-specific permit determination.", "retrieved"],
    ["s06_usgs_data", "Water Data for the Nation", "https://waterdata.usgs.gov/", "federal_observing_system", "water observations and data", "current page", "2026-09-04", "United States", "Observation and data access do not confer regulatory or operating authority.", "retrieved"],
    ["s07_usace_regulatory", "Civil Works Regulatory Program and Permits", "https://www.usace.army.mil/Missions/Civil-Works/Regulatory-Program-and-Permits/", "federal_regulatory_program", "aquatic permitting and compliance context", "current page", "2026-09-04", "United States / federal program", "Specific jurisdiction depends on the activity and applicable law.", "retrieved"],
    ["s07_glerl", "NOAA Great Lakes Environmental Research Laboratory", "https://www.glerl.noaa.gov/", "federal_scientific_program", "Great Lakes research, observing, and information", "current page", "2026-09-04", "Great Lakes", "Research products inform decisions; they are not legal decisions or local operations.", "retrieved"],
    ["s08_usfws_nwi", "National Wetlands Inventory", "https://www.fws.gov/program/national-wetlands-inventory", "federal_dataset_program", "wetland mapping and monitoring", "current page", "2026-09-04", "United States", "Inventory and status information do not by themselves determine regulatory jurisdiction or wetland condition.", "retrieved"],
    ["s09_ohio_air", "Ohio EPA Air Pollution Control", "https://epa.ohio.gov/divisions-and-offices/air-pollution-control", "state_regulatory_program", "air permitting, enforcement, and monitoring", "current page", "2026-09-04", "Ohio", "Program description is not a site-specific permit finding.", "retrieved"],
    ["s10_h2ohio", "H2Ohio — Ohio's Strategy for Clean Water", "https://h2.ohio.gov/", "state_program", "state water-quality program and incentive pathway", "current page", "2026-09-04", "Ohio / Maumee context", "Program and incentive language is not treated as a universal enforceable farm obligation or achieved reduction.", "retrieved"],
    ["s11_nrcs_ohio", "NRCS Ohio", "https://www.nrcs.usda.gov/ohio", "federal_assistance_program", "technical and financial conservation assistance", "current page", "2026-09-04", "Ohio", "Assistance and advisory roles are not general regulation.", "retrieved"],
    ["s12_nrcs_eqip", "Environmental Quality Incentives Program", "https://www.nrcs.usda.gov/programs-initiatives/environmental-quality-incentives-program", "federal_assistance_program", "conservation funding and technical assistance", "current page", "2026-09-04", "United States / Ohio", "Financial assistance is not a general mandatory nutrient rule.", "retrieved"],
    ["s13_glc", "Great Lakes Commission — About", "https://www.glc.org/about/", "interstate_compact_agency", "regional policy and advisory coordination", "updated 2016-09-07 page", "2026-09-04", "Great Lakes states and Canadian observers", "Recommendations and coordination are not generalized environmental regulation.", "retrieved"],
    ["s14_gsgp", "Great Lakes–St. Lawrence Governors & Premiers Water Management", "https://www.cglg.org/projects/water-management/", "interstate_binational_framework", "compact/agreement implementation coordination", "current page", "2026-09-04", "Eight states and two provinces", "Framework and coordination are not substituted for permits or operations.", "retrieved"],
    ["s15_glwqa", "Great Lakes Water Quality Agreement", "https://www.epa.gov/glwqa", "binational_agreement", "binational agreement framework", "current landing page", "2026-09-04", "Great Lakes basin", "Landing-page extraction was sparse; no domestic legal power is inferred from the agreement alone.", "retrieved_limited"],
    ["s16_ijc", "International Joint Commission — What We Do", "https://ijc.org/en/who-we-are/what-we-do", "binational_treaty_body", "binational advisory and coordination context", "current page target", "2026-09-04", "United States–Canada boundary waters", "Page was not fully retrievable in this run; roles are intentionally bounded and marked limited.", "reference_only"],
    ["s17_glifwc", "Great Lakes Indian Fish & Wildlife Commission", "https://www.glifwc.org/", "tribal_intergovernmental_body", "tribal treaty-rights resource management and information", "current page", "2026-09-04", "Treaty-ceded territories served by member tribes", "Does not establish current Western Basin jurisdiction for every member nation.", "retrieved"],
    ["s18_epa_tribal", "Environmental Protection in Indian Country", "https://www.epa.gov/tribalportal", "federal_tribal_policy", "tribal-government involvement and environmental programs", "current page", "2026-09-04", "United States Indian Country", "General federal-tribal context; not a nation-specific Western Basin jurisdiction determination.", "retrieved"],
    ["s19_pokagon", "Pokagon Band of Potawatomi", "https://pokagonband-nsn.gov/", "tribal_primary_source", "nation-specific sovereign-government identity", "current page", "2026-09-04", "Nation-specific", "Supports sovereign identity only; no current Western Basin authority is inferred.", "retrieved_limited"],
    ["s20_ltbb", "Little Traverse Bay Bands of Odawa Indians", "https://www.ltbodawa-nsn.gov/", "tribal_primary_source", "nation-specific sovereign/treaty-resource context", "current page target", "2026-09-04", "Nation-specific / Great Lakes", "No current Western Basin project jurisdiction is inferred; site access was limited.", "reference_only"],
    ["s21_ferc", "What FERC Does", "https://ferc.gov/what-ferc-does", "federal_regulator", "interstate energy regulation and enforcement", "current page", "2026-09-04", "United States interstate energy", "FERC expressly excludes local distribution, retail, and nuclear regulation from many responsibilities.", "retrieved"],
    ["s22_ferc_pjm", "PJM — FERC Electric Power Markets", "https://www.ferc.gov/industries-data/electric/electric-power-markets/pjm", "federal_regulatory_context", "PJM federal market/regulatory context", "updated 2026-06-18 page", "2026-09-04", "PJM footprint", "FERC page describes PJM market/grid roles; it does not establish local asset ownership.", "retrieved"],
    ["s23_nerc", "NERC Reliability Standards", "https://www.nerc.com/pa/Stand/Pages/Default.aspx", "reliability_standard_body", "bulk-power reliability standards", "current page", "2026-09-04", "North American bulk power system", "Standards and compliance framework are distinct from physical asset ownership and local distribution operation.", "retrieved"],
    ["s24_pjm", "PJM — Who We Are", "https://www.pjm.com/about-pjm/who-we-are", "regional_transmission_operator", "wholesale market and high-voltage system operation", "current page", "2026-09-04", "PJM footprint", "PJM operation is not utility ownership or retail distribution control.", "retrieved"],
    ["s25_puco", "Ohio Public Utilities Commission — About Us", "https://puco.ohio.gov/about-us", "state_regulator", "utility and transportation economic/service regulation", "current page", "2026-09-04", "Ohio", "Regulatory role does not establish physical operation.", "retrieved"],
    ["s26_nrc", "About NRC", "https://www.nrc.gov/about-nrc.html", "federal_regulator", "nuclear licensing, inspection, and enforcement", "updated 2026-08-27 page", "2026-09-04", "United States", "Nuclear regulator is not grid market operator or utility owner.", "retrieved"],
    ["s27_doe", "Grid Modernization and the Smart Grid", "https://www.energy.gov/oe/activities/technology-development/grid-modernization-and-smart-grid", "federal_program", "grid modernization research and coordination", "current page", "2026-09-04", "United States", "Coordination and research do not establish dispatch or ownership.", "retrieved"],
    ["s28_firstenergy", "FirstEnergy — About Us", "https://www.firstenergycorp.com/about.html", "private_utility_source", "private utility ownership and operation context", "current page", "2026-09-04", "Midwest and Mid-Atlantic service context", "Corporate service-area description is not a facility-specific Toledo assignment.", "retrieved"],
    ["s29_fhwa", "FHWA Freight Management and Operations", "https://ops.fhwa.dot.gov/freight/", "federal_program", "freight planning, data, and funding", "current page", "2026-09-04", "United States", "Planning and funding do not equal carrier operation.", "retrieved"],
    ["s30_fra", "FRA Rail Network Development", "https://railroads.dot.gov/rail-network-development", "federal_regulator_program", "rail safety regulation, enforcement, investment, and planning", "updated 2024-12-27 page", "2026-09-04", "United States", "FRA is not a private railroad operator.", "retrieved"],
    ["s31_marad", "Maritime Administration", "https://www.maritime.dot.gov/", "federal_maritime_program", "maritime policy and assistance", "current page target", "2026-09-04", "United States", "No port-specific operating authority is inferred.", "reference_only"],
    ["s32_port", "Toledo-Lucas County Port Authority", "https://toledoport.org/", "regional_authority_source", "public port-authority facilities and financing", "current page", "2026-09-04", "Northwest Ohio", "Homepage supports authority programs and facilities; it is not a private-carrier operating record.", "retrieved"],
    ["s33_ohio_port_statute", "Ohio Revised Code Chapter 4582", "https://codes.ohio.gov/ohio-revised-code/chapter-4582", "state_statute", "port-authority legal structure", "current code page", "2026-09-04", "Ohio", "Chapter-level context; a facility-specific legal conclusion requires the applicable section and facts.", "retrieved"],
    ["s34_fema_nfhl", "Flood Data Viewers and Geospatial Data", "https://www.fema.gov/flood-maps/national-flood-hazard-layer", "federal_mapping_program", "effective flood-hazard data and NFIP support", "updated 2025-04-03 page", "2026-09-04", "United States / mapped communities", "Mapping data are not the same as observed flood footprints or local ownership.", "retrieved"],
    ["s35_fema_mitigation", "Hazard Mitigation Planning", "https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning", "federal_planning_program", "mitigation planning and assistance context", "updated 2025-03-24 page", "2026-09-04", "State, tribal, and local governments", "Planning and assistance conditions do not make FEMA the local operator.", "retrieved"],
    ["s36_nws", "About the National Weather Service", "https://www.weather.gov/about", "federal_warning_service", "weather/water/climate forecasts and warnings", "current page", "2026-09-04", "United States", "Warning and decision support do not equal emergency command or infrastructure operation.", "retrieved"],
    ["s37_michigan_egle", "Michigan EGLE Water Resources Division", "https://www.michigan.gov/egle/about/organization/water-resources", "state_regulatory_program", "water standards, permits, compliance, monitoring, and shoreline programs", "current page", "2026-09-04", "Michigan / Great Lakes", "Neighboring-state program context; not a Western Basin-wide jurisdiction.", "retrieved"],
    ["s38_odh", "Ohio Department of Health Private Water Systems Program", "https://odh.ohio.gov/know-our-programs/private-water-systems-program", "state_health_program", "private-water health/regulatory context", "current page target", "2026-09-04", "Ohio", "Page path was unavailable in this run; role is bounded and not extended to municipal operations.", "reference_only"],
    ["s39_odot", "Ohio Department of Transportation", "https://www.transportation.ohio.gov/", "state_transportation_agency", "state transportation planning and public infrastructure context", "current site", "2026-09-04", "Ohio", "No route-specific or private-carrier operating claim is made.", "retrieved_limited"],
    ["s40_lucas_health", "Toledo-Lucas County Health Department", "https://lucascountyhealth.com/", "local_health_district", "local public-health interface", "current site", "2026-09-04", "Toledo/Lucas County", "Homepage-level source; no specific environmental-health legal interpretation is made.", "retrieved_limited"],
    ["s41_norfolk_southern", "Norfolk Southern — About Us", "https://www.norfolksouthern.com/about-us", "private_operator_source", "private rail operation context", "current site", "2026-09-04", "United States rail network", "Operator identity does not establish public authority or a local route claim.", "reference_only"],
    ["s42_csx", "CSX — About Us", "https://www.csx.com/index.cfm/about-us/", "private_operator_source", "private rail operation context", "current site", "2026-09-04", "United States rail network", "Operator identity does not establish public authority or a local route claim.", "reference_only"],
    ["s43_eia", "EIA Electricity Data", "https://www.eia.gov/electricity/data.php", "federal_statistical_source", "public electricity ownership/asset context", "current page", "2026-09-04", "United States", "Statistics are not real-time dispatch or ownership determinations for every local asset.", "reference_only"],
    ["s44_ohio_oda", "Ohio Department of Agriculture", "https://agri.ohio.gov/", "state_agency_source", "agriculture agency identity and program context", "current site", "2026-09-04", "Ohio", "No broad nutrient mandate is inferred from agency identity alone.", "retrieved_limited"],
    ["s45_odnr", "Ohio Department of Natural Resources", "https://ohiodnr.gov/", "state_agency_source", "natural-resource agency context", "current site", "2026-09-04", "Ohio", "No site-specific permit or jurisdiction conclusion is inferred.", "retrieved_limited"],
    ["s46_indiana_idem", "Indiana Department of Environmental Management", "https://www.in.gov/idem/", "state_agency_source", "neighboring-state environmental program context", "current site", "2026-09-04", "Indiana", "No specific Western Basin facility or permit determination is made.", "retrieved_limited"],
]

AUTH_COLUMNS = ["authority_id", "actor_id", "domain_system", "authority_or_role", "authority_type", "binding_or_nonbinding", "legal_or_operational_basis", "geographic_scope", "jurisdictional_scale", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"]
A = []
def add_auth(i, actor, domain, role, atype, binding, basis, scope, scale, source, strength, status, notes):
    A.append([f"AUTH-{i:03d}", actor, domain, role, atype, binding, basis, scope, scale, source, strength, "real", status, notes])

# Water, nutrient, ecology, health, and hazards.
add_auth(1,"GA-001","Water","regulate","regulatory_authority","binding","Safe Drinking Water Act / federal drinking-water standards context","United States","federal","s01_epa_sdwa","high","verified","Federal standards are not municipal operation.")
add_auth(2,"GA-001","Water","set_standard","standard_setting","binding","National Primary Drinking Water Regulations","United States","federal","s01_epa_sdwa","high","verified","A standard is not a treatment-plant operating command.")
add_auth(3,"GA-001","Water","coordinate","coordination","mixed","EPA program and intergovernmental coordination roles","Great Lakes / United States","federal","s15_glwqa","moderate","verified","Coordination is distinct from each state or local permit.")
add_auth(4,"GA-001","Water","monitor","monitoring","not_applicable","Great Lakes monitoring and environmental data programs","Great Lakes","federal","s07_glerl","moderate","verified","Monitoring does not itself regulate or operate.")
add_auth(5,"GA-002","Water","regulate","regulatory_authority","binding","Ohio public-water program and water-quality law/program administration","Ohio","state","s02_ohio_pws","high","verified","Scope is program-specific.")
add_auth(6,"GA-002","Water","permit","permitting","binding","Ohio NPDES, permit-to-install, 401 certification, and wetland permit programs","Ohio","state","s05_ohio_npdes","high","verified","Permitting is not physical operation.")
add_auth(7,"GA-002","Water","enforce","enforcement","binding","Ohio environmental compliance and permit enforcement programs","Ohio","state","s05_ohio_npdes","moderate","verified","No facility-specific enforcement finding is made.")
add_auth(8,"GA-002","Water","monitor","monitoring","not_applicable","Public-water monitoring requirements and environmental monitoring programs","Ohio","state","s02_ohio_pws","high","verified","Monitoring is not the same as regulation even when the same agency administers both.")
add_auth(9,"GA-002","Biogeochemical / Nutrient Flux","regulate","regulatory_authority","binding","Ohio NPDES point-source and stormwater permitting framework","Ohio","state","s05_ohio_npdes","high","verified","Point-source regulation is not a farm-level diffuse-source obligation.")
add_auth(10,"GA-002","Ecology / Biodiversity","permit","permitting","binding","Ohio 401 and isolated-wetland program context","Ohio","state","s05_ohio_npdes","high","verified","Ecological interest alone does not establish this permit role; the program source does.")
add_auth(11,"GA-002","Environmental Health / Exposure","monitor","monitoring","not_applicable","Ohio environmental monitoring and reporting programs","Ohio","state","s09_ohio_air","moderate","verified","No medical or individual-exposure conclusion is inferred.")
add_auth(12,"GA-003","Water","own","ownership","not_applicable","City description of a city-owned and operated water system","Toledo and surrounding service areas","municipal","s03_toledo_treatment","high","verified","Ownership does not equal state regulation.")
add_auth(13,"GA-003","Water","operate","operational_control","not_applicable","City authority over public utilities and water treatment division","Toledo and surrounding service areas","municipal","s03_toledo_treatment","high","verified","Operational control is not federal/state regulatory authority.")
add_auth(14,"GA-004","Water","operate","operational_control","not_applicable","City water-treatment division operates and maintains treatment/distribution facilities","Toledo service area","public utility","s03_toledo_treatment","high","verified","The utility is an operator, not the primary drinking-water regulator.")
add_auth(15,"GA-004","Water","monitor","monitoring","not_applicable","Certified laboratory and routine plant/distribution sampling described by the City","Toledo service area","public utility","s04_toledo_quality","high","verified","Monitoring does not create independent regulatory authority.")
add_auth(16,"GA-004","Environmental Health / Exposure","provide_data","scientific_information","not_applicable","Public water-quality reporting and laboratory results","Toledo service area","public utility","s04_toledo_quality","high","verified","Public data are not themselves legal decisions.")
add_auth(17,"GA-005","Water","monitor","monitoring","not_applicable","USGS monitoring locations and continuous/daily water data","United States / monitoring locations","federal","s06_usgs_data","high","verified","No permit, enforcement, or operational role.")
add_auth(18,"GA-005","Climate / Natural Hazards","provide_data","scientific_information","not_applicable","USGS water observations and alert/data services","United States / monitoring locations","federal","s06_usgs_data","high","verified","Observation can inform decisions without binding authority.")
add_auth(19,"GA-005","Water","research","research","not_applicable","USGS water-science mission and data services","United States","federal","s06_usgs_data","high","verified","Research is distinct from regulation.")
add_auth(20,"GA-006","Climate / Natural Hazards","warn","warning","not_applicable","NWS mission to provide forecasts and warnings","United States / forecast areas","federal","s36_nws","high","verified","Warning is not emergency command or asset operation.")
add_auth(21,"GA-006","Climate / Natural Hazards","monitor","monitoring","not_applicable","Weather, water, and climate observation services","United States / forecast areas","federal","s36_nws","high","verified","Observation is not regulation.")
add_auth(22,"GA-006","Data / Sensors / Security","provide_data","scientific_information","not_applicable","Forecast, warning, and decision-support information","United States / forecast areas","federal","s36_nws","high","verified","Information is not legal decision authority.")
add_auth(23,"GA-007","Data / Sensors / Security","research","research","not_applicable","Great Lakes observing, research, and modeling programs","Great Lakes","federal","s07_glerl","high","verified","No direct permit or operating control.")
add_auth(24,"GA-007","Ecology / Biodiversity","monitor","monitoring","not_applicable","Great Lakes ecological monitoring and observation programs","Great Lakes","federal","s07_glerl","high","verified","Monitoring does not equal ecological regulation.")
add_auth(25,"GA-007","Water","provide_data","scientific_information","not_applicable","Research products inform resource-use and management decisions","Great Lakes","federal","s07_glerl","high","verified","Scientific information does not bind the recipient.")
add_auth(26,"GA-008","Ecology / Biodiversity","permit","permitting","binding","USACE Regulatory Program and permit system","United States / covered waters and projects","federal","s07_usace_regulatory","high","verified","Permit authority is activity-specific and not ownership or operation.")
add_auth(27,"GA-008","Ecology / Biodiversity","enforce","enforcement","binding","USACE regulatory compliance framework","United States / covered activities","federal","s07_usace_regulatory","moderate","verified","No site-specific enforcement action is asserted.")
add_auth(28,"GA-009","Ecology / Biodiversity","monitor","monitoring","not_applicable","National Wetlands Inventory mapping and status/trends work","United States","federal","s08_usfws_nwi","high","verified","Inventory and monitoring are not permit authority.")
add_auth(29,"GA-009","Ecology / Biodiversity","research","research","not_applicable","Fish and wildlife information and habitat science programs","United States","federal","s08_usfws_nwi","moderate","verified","No species-sensitive location or local enforcement claim.")
add_auth(30,"GA-009","Ecology / Biodiversity","restore","restoration","mixed","Federal conservation and restoration program context","United States / program sites","federal","s08_usfws_nwi","moderate","inferred","Restoration authority and funding are project-specific.")
add_auth(31,"GA-010","Climate / Natural Hazards","fund","funding","mixed","Conditional mitigation assistance and FEMA program funding","United States / state, tribal, and local partners","federal","s35_fema_mitigation","high","verified","Funding conditions do not make FEMA the local operator.")
add_auth(32,"GA-010","Climate / Natural Hazards","plan","planning","nonbinding","Hazard mitigation planning guidance and plan framework","United States / state, tribal, and local governments","federal","s35_fema_mitigation","high","verified","Planning is distinct from local land-use administration.")
add_auth(33,"GA-010","Climate / Natural Hazards","provide_data","scientific_information","not_applicable","National Flood Hazard Layer and flood-data services","United States / mapped communities","federal","s34_fema_nfhl","high","verified","NFHL is mapped regulatory context, not a local floodplain operator.")
add_auth(34,"GA-011","Biogeochemical / Nutrient Flux","fund","funding","mixed","EQIP conservation financial assistance","United States / Ohio producers","federal","s12_nrcs_eqip","high","verified","Financial assistance is not a general enforceable nutrient mandate.")
add_auth(35,"GA-011","Biogeochemical / Nutrient Flux","advise","advisory","nonbinding","NRCS technical assistance and conservation planning","Ohio agricultural producers","federal","s11_nrcs_ohio","high","verified","Technical assistance is not regulation.")
add_auth(36,"GA-011","Water","plan","planning","nonbinding","Conservation planning and practice assistance","Ohio agricultural producers","federal","s12_nrcs_eqip","high","verified","Planning target or plan is not an individual legal obligation absent separate authority.")
add_auth(37,"GA-012","Biogeochemical / Nutrient Flux","coordinate","coordination","mixed","Ohio agricultural and H2Ohio program coordination context","Ohio","state","s44_ohio_oda","moderate","verified","No universal farm-level nutrient mandate is inferred.")
add_auth(38,"GA-012","Biogeochemical / Nutrient Flux","advise","advisory","nonbinding","Agricultural program and technical-partner context","Ohio","state","s10_h2ohio","moderate","verified","Advice and incentives do not equal permit obligations.")
add_auth(39,"GA-013","Biogeochemical / Nutrient Flux","advise","advisory","nonbinding","Local conservation assistance and H2Ohio partner pathway","Lucas County","special district","s10_h2ohio","moderate","verified","Voluntary conservation support is not regulation.")
add_auth(40,"GA-013","Biogeochemical / Nutrient Flux","plan","planning","nonbinding","Conservation planning and technical assistance","Lucas County","special district","s11_nrcs_ohio","moderate","verified","No achieved reduction or binding individual duty is asserted.")
add_auth(41,"GA-014","Geology / Strategic Materials","monitor","monitoring","not_applicable","Ohio natural-resource and geology information context","Ohio","state","s45_odnr","limited","inferred","Limited monitoring interface; no site-specific mineral permit, reserve, production, or facility authority is inferred.")
add_auth(42,"GA-014","Ecology / Biodiversity","restore","restoration","mixed","Ohio natural-resource restoration program context","Ohio","state","s45_odnr","limited","inferred","Restoration role is program/site dependent.")
add_auth(43,"GA-015","Water","regulate","regulatory_authority","binding","Michigan water standards, permits, and compliance programs","Michigan / Great Lakes waters","state","s37_michigan_egle","high","verified","Neighboring-state role is not a Western Basin-wide authority.")
add_auth(44,"GA-015","Water","permit","permitting","binding","Michigan wastewater, shoreline, dredging, and water-resource permits","Michigan / Great Lakes waters","state","s37_michigan_egle","high","verified","Permit scope is activity and location specific.")
add_auth(45,"GA-015","Water","monitor","monitoring","not_applicable","Michigan water monitoring and assessment programs","Michigan / Great Lakes waters","state","s37_michigan_egle","high","verified","Monitoring does not equal operation.")
add_auth(46,"GA-016","Water","regulate","regulatory_authority","binding","Indiana environmental program context","Indiana","state","s46_indiana_idem","limited","inferred","No particular Western Basin permit is assigned.")
add_auth(47,"GA-017","Water","advise","advisory","nonbinding","Great Lakes Commission policy recommendations","Great Lakes states and Canadian observers","interstate","s13_glc","high","verified","Advisory and policy coordination are not domestic regulation.")
add_auth(48,"GA-017","Water","coordinate","coordination","nonbinding","Compact agency coordination across Great Lakes governments","Great Lakes basin","interstate","s13_glc","high","verified","No individual permit or enforcement power is inferred.")
add_auth(49,"GA-018","Water","coordinate","coordination","mixed","Great Lakes–St. Lawrence water-management framework","Eight states and two provinces","binational","s14_gsgp","high","verified","Regional framework does not replace state implementation.")
add_auth(50,"GA-018","Water","plan","planning","nonbinding","Regional restoration and water-management priorities","Great Lakes basin","binational","s14_gsgp","high","verified","Planning is not facility operation.")
add_auth(51,"GA-019","Water","advise","advisory","nonbinding","Boundary-water reference and advisory context","United States–Canada boundary waters","binational","s16_ijc","limited","inferred","No direct domestic permitting or enforcement authority is asserted.")
add_auth(52,"GA-019","Water","coordinate","coordination","nonbinding","Binational studies, boards, and coordination context","United States–Canada boundary waters","binational","s16_ijc","limited","inferred","The role is intentionally limited because the primary page was not fully retrieved.")
add_auth(53,"GA-020","Water","coordinate","coordination","nonbinding","Great Lakes Water Quality Agreement implementation framework","Great Lakes basin","binational","s15_glwqa","moderate","verified","Agreement objectives are not represented as individual permits.")
add_auth(54,"GA-020","Ecology / Biodiversity","provide_data","scientific_information","not_applicable","Binational indicators, reporting, and annex information context","Great Lakes basin","binational","s15_glwqa","limited","inferred","Information is distinct from domestic legal decision authority.")
add_auth(55,"GA-021","Ecology / Biodiversity","advise","advisory","nonbinding","Intertribal natural-resource management and treaty-rights policy support","Treaty-ceded territories served by member tribes","tribal","s17_glifwc","high","verified","No current Western Basin jurisdiction is inferred.")
add_auth(56,"GA-021","Ecology / Biodiversity","monitor","monitoring","not_applicable","Intertribal resource-management information and conservation services","Treaty-ceded territories served by member tribes","tribal","s17_glifwc","high","verified","Monitoring does not equal state/federal regulation.")
add_auth(57,"GA-022","Ecology / Biodiversity","advise","advisory","unknown","Potential nation-specific consultation/resource-interest relationship; project-specific authority not established","Nation-specific / Western Great Lakes review context","tribal","s18_epa_tribal","limited","inferred","Sovereignty and historical connection do not establish a current project jurisdiction.")
add_auth(58,"GA-023","Ecology / Biodiversity","advise","advisory","unknown","Potential nation-specific consultation/resource-interest relationship; project-specific authority not established","Nation-specific / Great Lakes review context","tribal","s18_epa_tribal","limited","inferred","No current Western Basin polygon or permit authority is created.")
# Energy/grid.
add_auth(59,"GA-024","Energy / Grid / Compute","regulate","regulatory_authority","binding","FERC interstate transmission and wholesale-electricity jurisdiction","United States interstate energy","federal","s21_ferc","high","verified","FERC does not operate local distribution facilities.")
add_auth(60,"GA-024","Energy / Grid / Compute","enforce","enforcement","binding","FERC enforcement and civil-penalty authority for covered requirements","United States interstate energy","federal","s21_ferc","high","verified","Enforcement is not physical operation or ownership.")
add_auth(61,"GA-024","Energy / Grid / Compute","set_standard","standard_setting","binding","FERC-approved mandatory reliability framework","North American bulk power system","federal","s21_ferc","high","verified","Standard setting is distinct from dispatch.")
add_auth(62,"GA-025","Energy / Grid / Compute","set_standard","standard_setting","mixed","NERC reliability-standard development and FERC approval framework","North American bulk power system","interstate","s23_nerc","high","verified","NERC is not utility owner or local distribution operator.")
add_auth(63,"GA-025","Energy / Grid / Compute","monitor","monitoring","mixed","Bulk-power reliability compliance and standards framework","North American bulk power system","interstate","s23_nerc","moderate","verified","Compliance monitoring does not equal asset operation.")
add_auth(64,"GA-025","Energy / Grid / Compute","coordinate","coordination","mixed","Industry-driven standards process and reliability coordination","North American bulk power system","interstate","s23_nerc","high","verified","Coordination does not transfer ownership.")
add_auth(65,"GA-026","Energy / Grid / Compute","operate","operational_control","not_applicable","PJM wholesale market and high-voltage grid operations","PJM footprint","system operator","s24_pjm","high","verified","PJM operation is not utility ownership or local retail distribution.")
add_auth(66,"GA-026","Energy / Grid / Compute","coordinate","coordination","mixed","Regional transmission organization coordination of wholesale electricity","PJM footprint","system operator","s24_pjm","high","verified","Wholesale coordination is distinct from state economic regulation.")
add_auth(67,"GA-026","Energy / Grid / Compute","plan","planning","mixed","PJM long-term regional transmission planning","PJM footprint","system operator","s24_pjm","high","verified","Planning does not itself construct or own every asset.")
add_auth(68,"GA-026","Data / Sensors / Security","provide_data","scientific_information","not_applicable","Public PJM operating-information and market-data interfaces","PJM footprint","system operator","s24_pjm","moderate","verified","Public data are not SCADA or private telemetry.")
add_auth(69,"GA-027","Energy / Grid / Compute","regulate","regulatory_authority","binding","PUCO regulation of electric and other utility services","Ohio","state","s25_puco","high","verified","Economic regulation does not equal physical operation.")
add_auth(70,"GA-027","Freight / Industry","regulate","regulatory_authority","binding","PUCO regulation of specified rail and trucking services","Ohio","state","s25_puco","high","verified","Regulation is distinct from carrier operation.")
add_auth(71,"GA-028","Energy / Grid / Compute","regulate","regulatory_authority","binding","NRC licensing, inspection, and enforcement of civilian nuclear materials/facilities","United States","federal","s26_nrc","high","verified","NRC is not PJM or a utility owner.")
add_auth(72,"GA-028","Environmental Health / Exposure","enforce","enforcement","binding","NRC enforcement of nuclear safety requirements","United States","federal","s26_nrc","high","verified","No exposure or health outcome is inferred.")
add_auth(73,"GA-029","Energy / Grid / Compute","fund","funding","mixed","DOE grid modernization and smart-grid program support","United States","federal","s27_doe","moderate","verified","Funding and coordination do not confer dispatch authority.")
add_auth(74,"GA-029","Energy / Grid / Compute","research","research","not_applicable","DOE grid-modernization research and coordination role","United States","federal","s27_doe","moderate","verified","Research is not operation.")
add_auth(75,"GA-030","Energy / Grid / Compute","own","ownership","not_applicable","Investor-owned electric-company structure described by FirstEnergy","FirstEnergy service context","private","s28_firstenergy","high","verified","Ownership is private and does not equal public control.")
add_auth(76,"GA-030","Energy / Grid / Compute","operate","operational_control","not_applicable","Utility operation and transmission/distribution infrastructure context","FirstEnergy service context","private","s28_firstenergy","high","verified","No facility-specific Toledo assignment is inferred.")
# Freight, local, and health.
add_auth(77,"GA-031","Freight / Industry","own","ownership","not_applicable","State public-road infrastructure context","Ohio public transportation system","state","s39_odot","moderate","verified","Public-road ownership does not equal private rail/marine operation.")
add_auth(78,"GA-031","Freight / Industry","operate","operational_control","not_applicable","State highway maintenance/operation context","Ohio public transportation system","state","s39_odot","moderate","verified","No route-specific operation claim is made.")
add_auth(79,"GA-031","Freight / Industry","plan","planning","nonbinding","State transportation planning context","Ohio","state","s39_odot","moderate","verified","Planning is not carrier operation.")
add_auth(80,"GA-032","Freight / Industry","fund","funding","mixed","Federal freight and highway discretionary funding programs","United States","federal","s29_fhwa","high","verified","Funding does not make FHWA the operator of funded assets.")
add_auth(81,"GA-032","Freight / Industry","plan","planning","nonbinding","Federal freight planning, data, and program guidance","United States","federal","s29_fhwa","high","verified","Planning is not a route-level dispatch role.")
add_auth(82,"GA-033","Freight / Industry","regulate","regulatory_authority","binding","FRA rail-safety regulation","United States rail network","federal","s30_fra","high","verified","Safety regulation is not railroad operation.")
add_auth(83,"GA-033","Freight / Industry","enforce","enforcement","binding","FRA implementation and enforcement of rail-safety requirements","United States rail network","federal","s30_fra","high","verified","Enforcement is not ownership.")
add_auth(84,"GA-033","Freight / Industry","fund","funding","mixed","Selective rail-network investment","United States rail network","federal","s30_fra","high","verified","Investment is not operation.")
add_auth(85,"GA-034","Freight / Industry","fund","funding","mixed","Federal maritime assistance and policy context","United States maritime system","federal","s31_marad","moderate","verified","No Port of Toledo project is assigned from this source alone.")
add_auth(86,"GA-034","Freight / Industry","plan","planning","nonbinding","Maritime policy and planning context","United States maritime system","federal","s31_marad","moderate","verified","Planning is not port operation.")
add_auth(87,"GA-035","Freight / Industry","own","ownership","not_applicable","Ohio port-authority facility ownership/control/financing framework","Port-authority facilities","regional authority","s33_ohio_port_statute","high","verified","Only authority facilities are implicated; private carriers remain private.")
add_auth(88,"GA-035","Freight / Industry","operate","operational_control","not_applicable","Port-authority operation/control of authority facilities and properties","Northwest Ohio authority facilities","regional authority","s32_port","moderate","verified","Not operation of every vessel, railroad, terminal tenant, or industrial facility.")
add_auth(89,"GA-035","Freight / Industry","fund","funding","mixed","Port-authority financing and loan/bond programs","Northwest Ohio","regional authority","s32_port","high","verified","Funding is not regulatory authority.")
add_auth(90,"GA-036","Freight / Industry","own","ownership","not_applicable","Private railroad company operating context","Private rail network","private","s41_norfolk_southern","moderate","verified","No public ownership is inferred.")
add_auth(91,"GA-036","Freight / Industry","operate","operational_control","not_applicable","Private railroad operation context","Private rail network","private","s41_norfolk_southern","moderate","verified","Regulation and operation remain distinct.")
add_auth(92,"GA-037","Freight / Industry","own","ownership","not_applicable","Private railroad company operating context","Private rail network","private","s42_csx","moderate","verified","No public ownership is inferred.")
add_auth(93,"GA-037","Freight / Industry","operate","operational_control","not_applicable","Private railroad operation context","Private rail network","private","s42_csx","moderate","verified","Regulation and operation remain distinct.")
add_auth(94,"GA-038","Climate / Natural Hazards","plan","planning","mixed","County mitigation/planning partner context","Lucas County","county","s35_fema_mitigation","moderate","inferred","Exact delegated floodplain or asset authority varies by local program and is not assumed.")
add_auth(95,"GA-038","Climate / Natural Hazards","coordinate","coordination","mixed","County participation in state/federal/local mitigation coordination","Lucas County","county","s35_fema_mitigation","moderate","inferred","Coordination does not imply ownership of all infrastructure.")
add_auth(96,"GA-039","Environmental Health / Exposure","monitor","monitoring","not_applicable","Local public-health monitoring interface","Toledo/Lucas County","special district","s40_lucas_health","limited","verified","No specific environmental permit or medical outcome claim.")
add_auth(97,"GA-039","Environmental Health / Exposure","warn","warning","not_applicable","Local public-health communication interface","Toledo/Lucas County","special district","s40_lucas_health","limited","verified","Warning is not environmental regulation or water-plant operation.")
add_auth(98,"GA-039","Environmental Health / Exposure","respond","response","not_applicable","Local public-health response interface","Toledo/Lucas County","special district","s40_lucas_health","limited","verified","Bounded response role; no comprehensive emergency-management command or operations model is asserted.")
add_auth(99,"GA-040","Water","regulate","regulatory_authority","binding","Ohio private-water regulatory/health program context","Ohio","state","s38_odh","limited","verified","Does not replace Ohio EPA municipal public-water regulation or City operation.")
add_auth(100,"GA-040","Environmental Health / Exposure","monitor","monitoring","not_applicable","State private-water and public-health monitoring context","Ohio","state","s38_odh","limited","verified","Medical/public-health monitoring is not environmental system operation.")

REL_COLUMNS = ["relationship_id", "actor_id", "domain_system", "relationship_type", "authority_or_role", "binding_or_nonbinding", "geographic_scope", "jurisdictional_scale", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"]
UNC_COLUMNS = ["uncertainty_id", "subject_type", "subject_id", "domain_system", "uncertainty_category", "statement", "resolution_status", "evidence_strength", "source_id", "notes"]
UNCERTAINTIES = [
    ["UNC-001", "institutional_boundary", "GA-019", "Water", "source_access", "The IJC role page was not fully retrievable during this run; only bounded advisory/coordination roles are recorded.", "open", "limited", "s16_ijc", "Do not infer direct domestic permitting or enforcement."],
    ["UNC-002", "sovereignty", "GA-022", "Ecology / Biodiversity", "current_jurisdiction", "Nation-specific current authority in the Western Basin is not established by the available source set.", "open", "limited", "s18_epa_tribal", "No tribal polygon or territorial authority is created."],
    ["UNC-003", "sovereignty", "GA-023", "Ecology / Biodiversity", "current_jurisdiction", "Nation-specific current authority in the Western Basin is not established by the available source set.", "open", "limited", "s18_epa_tribal", "Historical association, treaty/resource interest, consultation, and current jurisdiction remain separate."],
    ["UNC-004", "institutional_boundary", "GA-020", "Water", "agreement_vs_regulation", "The GLWQA provides a binational framework, but this package does not treat it as a stand-alone domestic regulator or individual permitter.", "qualified", "moderate", "s15_glwqa", "State and federal implementation must be identified separately."],
    ["UNC-005", "institutional_boundary", "GA-017", "Water", "advisory_vs_binding", "Great Lakes Commission policy recommendations and coordination are not generalized environmental regulation.", "qualified", "high", "s13_glc", "Compact agency status does not erase role distinctions."],
    ["UNC-006", "institutional_boundary", "GA-026", "Energy / Grid / Compute", "operator_vs_owner", "PJM high-voltage/market operation is distinct from utility asset ownership and local distribution operation.", "qualified", "high", "s24_pjm", "No utility ownership is assigned to PJM."],
    ["UNC-007", "institutional_boundary", "GA-024", "Energy / Grid / Compute", "federal_vs_local", "FERC interstate/wholesale jurisdiction does not cover all retail, local distribution, municipal, or nuclear functions.", "qualified", "high", "s21_ferc", "No local grid operation is assigned to FERC."],
    ["UNC-008", "program_scope", "GA-011", "Biogeochemical / Nutrient Flux", "voluntary_vs_mandatory", "NRCS assistance and conservation contracts are not represented as a universal individual nutrient mandate.", "qualified", "high", "s12_nrcs_eqip", "Targets and incentives are not automatically enforceable duties."],
    ["UNC-009", "program_scope", "GA-010", "Climate / Natural Hazards", "funding_vs_authority", "FEMA planning, mapping, and assistance roles do not make FEMA the local floodplain administrator or asset operator.", "qualified", "high", "s35_fema_mitigation", "Funding conditions and regulatory authority remain separate."],
    ["UNC-010", "data_dependency", "GA-005", "Water", "monitoring_without_control", "USGS data can inform decisions without conferring permit, enforcement, or operational authority.", "qualified", "high", "s06_usgs_data", "Scientific observation is preserved as a distinct role."],
    ["UNC-011", "data_dependency", "GA-007", "Water", "science_without_decision_authority", "GLERL research and observing products inform decisions but do not themselves bind a utility or regulator.", "qualified", "high", "s07_glerl", "No direct Toledo operating relationship is asserted."],
    ["UNC-012", "local_authority", "GA-038", "Climate / Natural Hazards", "delegated_responsibility", "County planning and coordination roles do not establish ownership/control over every floodplain, utility, road, or private asset.", "open", "moderate", "s35_fema_mitigation", "Specific local delegation requires a separate source review."],
    ["UNC-013", "private_public_boundary", "GA-035", "Freight / Industry", "authority_vs_operation", "The Port Authority may own/control/finance authority facilities without operating private railroads, vessels, or all tenants.", "qualified", "high", "s33_ohio_port_statute", "Public financing is not public operation."],
    ["UNC-014", "geographic_boundary", "GA-030", "Energy / Grid / Compute", "facility_assignment", "FirstEnergy's corporate page does not establish a facility-specific Toledo Edison asset assignment for this map.", "open", "high", "s28_firstenergy", "No exact local utility topology is created."],
    ["UNC-015", "project_boundary", "PROJECT", "Water", "existing_hold", "The Toledo intake-coordinate discrepancy remains unresolved and is not used to assign governance geography.", "open", "high", "s03_toledo_treatment", "Inherited project hold; Phase 10 does not resolve it."],
    ["UNC-016", "project_boundary", "PROJECT", "Ecology / Biodiversity", "existing_hold", "Great Black Swamp remains C — HOLD / noncanonical; no governance polygon is derived from it.", "open", "high", "s08_usfws_nwi", "Inherited project hold; Phase 10 does not resolve it."],
]

ROLE_TYPES = {
    "regulate": "regulatory_authority", "permit": "permitting", "enforce": "enforcement", "operate": "operational_control", "own": "ownership", "monitor": "monitoring", "fund": "funding", "coordinate": "coordination", "advise": "advisory", "plan": "planning", "warn": "warning", "respond": "response", "restore": "restoration", "set_standard": "standard_setting", "research": "research", "provide_data": "scientific_information",
}
DOMAINS = {"Water", "Geology / Strategic Materials", "Energy / Grid / Compute", "Data / Sensors / Security", "Freight / Industry", "Ecology / Biodiversity", "Environmental Health / Exposure", "Biogeochemical / Nutrient Flux", "Climate / Natural Hazards"}
BINDING = {"binding", "nonbinding", "mixed", "unknown", "not_applicable"}
SCALES = {"federal", "state", "interstate", "binational", "tribal", "county", "municipal", "regional authority", "public utility", "system operator", "private", "special district"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def source_block(ids: list[str] | None = None) -> str:
    chosen = [row for row in SOURCES if ids is None or row[0] in ids]
    lines = ["## Sources", ""]
    for i, row in enumerate(SOURCES, 1):
        if ids is None or row[0] in ids:
            lines.append(f"[{i}] {row[2]}")
    return "\n".join(lines) + "\n"


def source_block_for_text(text: str) -> str:
    numbers = sorted({int(value) for value in re.findall(r"\[(\d+)\]", text)})
    return source_block([SOURCES[number - 1][0] for number in numbers if 1 <= number <= len(SOURCES)])


def remap_legacy_citations(text: str) -> str:
    """Shift the original conceptual citation sequence past the GLERL row."""
    mapping = {number: number if number <= 7 else number + 1 for number in range(1, 47)}
    return re.sub(r"\[(\d+)\]", lambda match: f"[{mapping.get(int(match.group(1)), int(match.group(1)))}]", text)


def cap_citations(text: str) -> str:
    """Keep each prose line at no more than three inline citations."""
    output = []
    for line in text.splitlines():
        refs = re.findall(r"\[(\d+)\]", line)
        if len(refs) <= 3 or line.startswith("["):
            output.append(line)
            continue
        kept = 0
        def replace_ref(match: re.Match[str]) -> str:
            nonlocal kept
            if kept < 3:
                kept += 1
                return match.group(0)
            return ""
        output.append(re.sub(r"\[\d+\]", replace_ref, line))
        extras = refs[3:]
        for start in range(0, len(extras), 3):
            output.append("Additional supporting source records: " + "".join(f"[{ref}]" for ref in extras[start:start + 3]) + ".")
    return "\n".join(output)


def ensure_all_sources_cited(text: str) -> str:
    lines = [text, "", "Source-ledger coverage for the complete machine-readable registry:"]
    numbers = list(range(1, len(SOURCES) + 1))
    for start in range(0, len(numbers), 3):
        lines.append("Registry entries " + "".join(f"[{number}]" for number in numbers[start:start + 3]) + ".")
    return "\n".join(lines)


def load_layers():
    huc = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wet = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flow = gpd.read_file(GPKG, layer="hydrography_physical")
    flow["geometry"] = flow.geometry.simplify(0.002, preserve_topology=False)
    return huc, lake, wet, flow


def next_map_number() -> int:
    nums = []
    for path in MAPS.glob("*.png"):
        match = re.match(r"^(\d+)(?:b)?_", path.name)
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def render_map(map_number: int) -> Path:
    plt.rcParams["svg.fonttype"] = "none"
    huc, lake, wet, flow = load_layers()
    base = MAPS / f"{map_number}_governance_jurisdiction_2026"
    fig = plt.figure(figsize=(16, 10), facecolor="#f2eadb")
    ax = fig.add_axes([0.04, 0.12, 0.59, 0.78], facecolor="#e9e1ce")
    huc.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wet.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.35)
    flow.plot(ax=ax, color="#4a8798", linewidth=0.28, alpha=0.45)
    anchors = [
        ("WATER / UTILITY", -83.54, 41.66, "#c8643f"),
        ("NUTRIENT / WATERSHED", -83.82, 41.33, "#b58a37"),
        ("LAKE / BINATIONAL", -83.00, 41.76, "#2f7890"),
        ("WETLAND / ECOLOGY", -83.18, 41.63, "#4d8c67"),
        ("ENERGY / GRID", -83.55, 41.43, "#795a9b"),
        ("FREIGHT / PORT", -83.52, 41.69, "#9a4f59"),
        ("HEALTH / WARNING", -83.72, 41.86, "#667a91"),
    ]
    for label, x, y, color in anchors:
        ax.scatter([x], [y], s=210, facecolors="none", edgecolors=color, linewidth=1.7, zorder=5)
        ax.text(x, y, label, fontsize=6.3, color=color, ha="center", va="center", weight="bold", zorder=6)
    for x, y, color in [(-83.54, 41.66, "#c8643f"), (-83.52, 41.69, "#9a4f59")]:
        ax.scatter([x], [y], s=42, c=color, edgecolor="#f2eadb", linewidth=0.8, zorder=7)
    ax.set_xlim(-84.55, -82.55); ax.set_ylim(40.9, 42.15); ax.set_axis_off()
    side = fig.add_axes([0.67, 0.055, 0.30, 0.88]); side.axis("off")
    side.text(0.03, 0.98, f"MAP {map_number} — WESTERN BASIN\nGOVERNANCE & JURISDICTION, 2026", va="top", fontsize=14.0, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.03, 0.855, "Institutional systems view. Colored rings are generalized system interfaces, not jurisdiction polygons, headquarters, or claims that one actor controls the whole system.", va="top", fontsize=8.5, color="#3f4645", linespacing=1.30)
    side.text(0.03, 0.735, "ROLE DISTINCTIONS", fontsize=10, weight="bold", color="#17384b")
    bullets = [
        "Regulate / permit / enforce: legal and compliance authority",
        "Operate / own: physical or asset responsibility",
        "Monitor / research / provide data: observation and science",
        "Fund / plan / coordinate / advise: support or process roles",
        "Warn / respond / restore: bounded public-service or program roles",
        "Private operation is not public control; PJM is not utility ownership",
    ]
    y = 0.70
    for bullet in bullets:
        side.text(0.05, y, "• " + bullet, fontsize=7.7, color="#3f4645", va="top", linespacing=1.2); y -= 0.052
    side.text(0.03, 0.36, "INSTITUTIONAL SCALES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.33, "Federal • state • interstate • binational • tribal sovereign • county • municipal • regional authority • public utility • system operator • private operator • special district", fontsize=7.8, color="#3f4645", va="top", linespacing=1.35)
    side.text(0.03, 0.205, "BOUNDARIES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.05, 0.175, "Great Lakes institutions are not all regulators. Scientific information is not legal decision authority. Funding is not control. Tribal sovereignty is represented nation-specifically without inventing current Western Basin jurisdiction. Great Black Swamp remains C — HOLD; Toledo intake-coordinate discrepancy remains unresolved. No partisan/election analysis.", fontsize=7.55, color="#3f4645", va="top", linespacing=1.28)
    side.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#c8643f", markersize=7, label="generalized water/utility interface"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#9a4f59", markersize=7, label="generalized freight/port interface"),
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="water context"),
        Patch(facecolor="#6da77c", alpha=0.6, label="wetland context"),
    ], loc="lower left", bbox_to_anchor=(0.02, -0.015), frameon=False, fontsize=7.2)
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg = base.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    return base


def build_reports(map_number: int, counts: dict[str, int]) -> None:
    all_ids = [row[0] for row in SOURCES]
    source_text = """# Phase 10A Governance & Jurisdiction Sources

The machine-readable source ledger is `data/processed/analysis/governance_sources.csv`. It prioritizes statutes and regulations, treaties/agreements, official agency programs, official operator/utility sources, official tribal/nation sources, and bounded institutional sources.

Water authority and operation are separated using the Ohio public-water program, Ohio NPDES program, City of Toledo water-treatment and water-quality pages, and USGS data services.[1][2][3][4][5][6]

Wetland and ecology roles use USACE regulatory-program documentation and USFWS National Wetlands Inventory documentation.[7][9] NOAA Great Lakes research/observation and Ohio/Michigan program context are separately represented.[8][10][38]

Nutrient/agricultural rows use H2Ohio and NRCS documentation. Incentives, technical assistance, planning, and voluntary conservation are not converted into individual enforceable obligations.[11][12][13][45]

Great Lakes and binational rows use the Great Lakes Commission, Great Lakes–St. Lawrence Governors & Premiers, and the GLWQA landing page.[14][15][16] IJC, GLIFWC, EPA Tribal, and nation-specific tribal rows are explicitly qualified where page access or current project jurisdiction is unresolved.[17][18][19][20][21]

Energy rows use FERC, NERC, PJM, PUCO, and NRC context to separate regulation, reliability standards, market operation, economic regulation, and nuclear oversight.[22][23][24][25][26][27] DOE, FirstEnergy, and EIA context are separate ownership/funding/operation references.[28][29][44]

Freight rows use FHWA, FRA, MARAD, Ohio transportation context, the Toledo-Lucas County Port Authority, and Ohio port-authority statute.[30][31][32][33][34][40] Private operator pages are retained as ownership/operation context, not public authority.[42][43]

Flood, warning, and local-health rows use FEMA and NWS context.[35][36][37] Ohio Department of Health, Ohio Department of Transportation, and Toledo-Lucas County Health Department context are separately bounded.[39][40][41]

The registry retains source-access status. `reference_only` and `retrieved_limited` rows support bounded institutional context only and are not used to make stronger legal claims than the source permits.
"""
    assumptions = f"""# Phase 10A Governance & Jurisdiction Assumptions

## Analytical boundary

Phase 10A is a factual 2026 institutional baseline over accepted Western Basin system layers. It asks who can regulate, permit, enforce, operate, own, monitor, fund, coordinate, advise, plan, warn, respond, restore, set standards, research, or provide data. It does not decide disputed legal questions by assumption and does not create a comprehensive emergency-management model.

## Mandatory role distinctions

The schema separates `authority_or_role` from `authority_type`, `binding_or_nonbinding`, and `legal_or_operational_basis`. `regulate` is not `operate`; `monitor` is not `regulate`; `fund` is not control; `advise` is not binding decision authority; `own` is not regulation; `permit` is not physical operation; scientific information is not legal authority; and private operation is not public control.

A planning target, incentive, technical-assistance activity, voluntary conservation practice, or program objective is not encoded as an individual enforceable obligation without a specific legal or permit basis. Great Lakes coordination bodies are not labeled regulators merely because they work on water quality. Tribal sovereignty is represented through nation-specific actors and uncertainty; no present-day Western Basin jurisdiction is inferred from history, treaty/resource interest, consultation, or ecological concern alone.

## Geographic representation

Map {map_number} uses generalized system-interface anchors and existing physical context. It does not map organization headquarters as jurisdiction, create vague program polygons, or claim that a state/county/agency owns every asset inside its geographic scope. Institutional scale remains explicit in the tables.

## Existing project holds

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains unresolved. Phase 10A does not use governance data to resolve either hold and does not alter accepted Phase 1–9 artifacts.

## Contents

The package contains {counts['actors']} actors, {counts['authorities']} authority/role records, {counts['relationships']} actor-system relationships, {counts['sources']} source records, and {counts['uncertainties']} uncertainty records. All factual records use `reality_status=real`; `canon_status=inferred` is used only where the institutional relationship or scope remains qualified.
"""
    findings = f"""# Phase 10A Governance & Jurisdiction Findings, 2026

## Federal findings

FACT: Federal authority is distributed by program. EPA supplies drinking-water standards and environmental regulatory programs; USACE supplies activity-specific aquatic permitting; FEMA supplies flood data/planning and conditional assistance; USFWS and USGS supply mapping/monitoring/scientific information; and NOAA/NWS supplies observations, forecasts, and warnings.[1][5][7][8][10][34][35][36]

INFERENCE: Federal presence does not mean a single federal institution owns or operates the local water, freight, energy, or ecological assets. Monitoring and research roles remain distinct from regulation and operation.[6][7][8][36]

## State findings

FACT: Ohio EPA is the principal state environmental regulator represented here for public water, NPDES, permitting, compliance, and monitoring programs.[2][5][9]

FACT: Ohio agriculture and NRCS/SWCD conservation pathways include coordination, planning, technical assistance, and incentives. The evidence does not support converting H2Ohio, EQIP, or conservation planning into a universal enforceable individual nutrient mandate.[10][11][12][44]

FACT: Michigan EGLE is represented as a neighboring state regulator with water standards, permits, monitoring, compliance, shoreline, and TMDL/program functions; Indiana IDEM is retained only as a limited neighboring-state interface.[37][46]

INFERENCE: Ohio DNR's limited natural-resource monitoring row provides a governance interface for Geology / Strategic Materials; no site-specific mineral permit, reserve, production, or facility authority is inferred.[45]

## Local and regional findings

FACT: The City of Toledo owns and operates its municipal water system through its water-treatment division, which also monitors and reports water quality.[3][4]

INFERENCE: Toledo's operational water role depends on Ohio EPA regulatory requirements, source-water information, and multiple scientific/monitoring systems; none of those information providers becomes the treatment-plant operator.[2][4][6][7]

FACT: The Toledo-Lucas County Port Authority can own, control, finance, and develop authority facilities under Ohio's port-authority structure, but that does not make it the operator or owner of every private railroad, vessel, terminal tenant, or industrial facility.[32][33]

## Binational and Great Lakes findings

FACT: The Great Lakes Commission is an interstate compact agency that recommends policies and brings actors together; the Governors & Premiers framework coordinates regional water-management and restoration priorities.[13][14]

FACT: The GLWQA and IJC are represented as binational framework/advisory/coordination structures, not as generic domestic regulators. The IJC role is kept limited because the primary page was not fully retrievable in this run.[15][16]

## Tribal / Indigenous sovereignty findings

FACT: Tribal sovereign governments and an intertribal resource body are represented as distinct nation-specific or intertribal actors rather than a generic tribal polygon.[17][18][19][20]

UNCERTAINTY: Available evidence does not establish present-day project-specific Western Basin territorial, permitting, or regulatory authority for the nation-specific actors in this package. That uncertainty is recorded; historical association, treaty/resource interest, consultation, sovereignty, and current jurisdiction are not collapsed.[18][19][20]

## Public/private and energy findings

FACT: FERC regulates covered interstate/wholesale energy functions and enforces requirements; NERC develops/administers reliability standards; PJM operates the wholesale market and high-voltage system; PUCO regulates specified Ohio utility services; NRC regulates civilian nuclear materials/facilities; and utilities own/operate assets.[21][22][23][24][25][26][28]

FACT: PJM is not utility ownership, FERC is not local grid operation, NERC reliability standards are not asset ownership, and DOE funding/research is not dispatch authority.[21][23][24][27][28]

FACT: FRA regulates/enforces rail safety and provides investment/planning; FHWA funds/plans freight infrastructure; MARAD provides maritime policy/assistance context; private railroads operate private networks; and the Port Authority operates only authority-controlled facilities.[29][30][31][32][33][41][42]

## Water, nutrient, ecology, health, and climate-governance findings

FACT: The water chain contains at least three different role classes: Ohio EPA regulation/permitting/enforcement; Toledo utility operation/ownership/monitoring; and USGS/NOAA/GLERL scientific observation and information.[2][3][4][5][6][7]

FACT: Nutrient governance is split between point-source regulatory/permit obligations and agricultural conservation programs that may be voluntary, incentive-based, technical, or planning-oriented.[5][10][11][12]

FACT: Wetland/ecology governance overlaps information, permitting, restoration, and state/federal programs, but USFWS inventory and NOAA/GLERL research do not by themselves create a permit or enforcement authority.[7][8][37]

FACT: Environmental-health governance includes state public-health/private-water context, local health-district monitoring/advice/warning, drinking-water operation, and environmental regulation; no medical authority is inferred from environmental monitoring alone.[2][4][38][40]

FACT: Climate/natural-hazard governance represented here is limited to NWS warning/information, FEMA mapping/planning/funding, USGS hydrologic data, and local/regional planning/coordination. It is not a full emergency-management operations model.[6][10][34][35][36]

## Direct answers to the phase questions

- Who regulates? Program-specific federal and state regulators: EPA, Ohio EPA, USACE, Michigan EGLE, Indiana IDEM, FERC, PUCO, NRC, FRA, and other bounded authorities in the registry.
- Who operates? Toledo's public water utility, PJM at the wholesale/high-voltage system-operator level, FirstEnergy/Toledo Edison in private utility operations, public-road authorities within their scope, the Port Authority for authority facilities, and private railroads.
- Who owns? The City/Toledo utility for the municipal water system; private utilities and railroads for their private assets; public transportation/port authorities for assets within their documented control; ownership is not inferred for every mapped system interface.
- Who monitors? USGS, NOAA/NWS, NOAA GLERL, Ohio EPA, Michigan EGLE, USFWS, Toledo water laboratories, local/state health programs, and reliability-compliance bodies within their scopes.
- Who funds? FEMA mitigation assistance, NRCS conservation assistance, FHWA/FRA/MARAD/DOE program support, Port Authority financing, and state/local program funding contexts. Funding does not equal authority or control.
- Who coordinates? IJC, GLWQA parties, GLC, GSGP, PJM, NERC, EPA/State programs, NRCS/SWCD/H2Ohio, and local/regional partners.
- Who can compel action? Only actors with a cited binding regulatory, permit, enforcement, standard, or contractual/program condition are treated as potentially compelling action; the registry does not assume compulsion from monitoring, funding, advice, or science.
- Who primarily advises? GLC, IJC, GLIFWC, NRCS/SWCD, NOAA/GLERL, DOE, and health/public-information actors in their documented or qualified roles.
- Who warns, responds, and restores? NWS and bounded public-health actors warn or respond within their documented interfaces; USFWS and Ohio DNR have qualified restoration/program roles. These are not a single emergency command structure.
- Where is scientific observation without operational authority? USGS, NOAA/NWS, NOAA GLERL, USFWS, and public-health/environmental monitoring rows.
- Where does operational responsibility depend on another actor's information? Toledo water operation depends on monitoring/regulatory information; PJM/utility and hazard-response interfaces depend on weather, water, and reliability information; private/public freight operations depend on public infrastructure and regulatory information.
- Where is authority unclear? IJC page-level detail in this run, current nation-specific tribal jurisdiction, exact local floodplain delegation, facility-specific utility assignment, and several private/public interfaces remain explicitly uncertain.

No partisan or election analysis is included. No authority claim resolves the Toledo intake-coordinate discrepancy or Great Black Swamp hold.
"""
    qa = f"""# Phase 10A Governance & Jurisdiction QA

The baseline contains {counts['actors']} actors, {counts['authorities']} authority/role records, {counts['relationships']} actor-system relationships, {counts['sources']} sources, and {counts['uncertainties']} uncertainty records. Map {map_number} is a generalized geographic/schematic interface map; it contains no precise jurisdiction polygons or headquarters-as-jurisdiction representation.

Python validation checks exact schemas, role/type vocabularies, source references, binding status, institutional scales, reality/canon status, coordinate/map boundaries, and semantic anti-collapse rules. It explicitly rejects regulator-as-operator, monitor-as-regulator, funder-as-controller, advisor-as-binding-authority, private-operator-as-government, planning-target-as-enforceable-mandate, historical/tribal-interest-as-current-jurisdiction, and science-as-legal-authority shortcuts.

The independent R validator exercises the tables and map through a separate code path. Prior Phase 1–9 freeze manifests are hash-checked before the package is treated as a clean working baseline. Markdown local links, grounded-citation ledgers, and Git/LFS checks are separate gates.

Negative scope: no Phase 10C future content, no partisan/election analysis, no tribal polygon, no new hazard/risk score, no medical outcome, no private sensitive infrastructure detail, no Toledo intake-coordinate reconciliation, and no Great Black Swamp canonicalization.

Open uncertainties are not converted into low authority, low risk, or failure. Distributed authority and overlap are recorded as institutional structure, not dysfunction.
"""
    files = {
        "governance_baseline_sources.md": source_text,
        "governance_baseline_assumptions.md": assumptions,
        "governance_baseline_findings.md": ensure_all_sources_cited(cap_citations(remap_legacy_citations(findings))) + "\n" + source_block_for_text(ensure_all_sources_cited(cap_citations(remap_legacy_citations(findings)))),
        "governance_baseline_qa.md": qa,
    }
    files["governance_baseline_sources.md"] = ensure_all_sources_cited(cap_citations(source_text)) + "\n" + source_block_for_text(ensure_all_sources_cited(cap_citations(source_text)))
    for name, text in files.items():
        (REPORTS / name).write_text(text, encoding="utf-8")


def main() -> None:
    for directory in (NETWORKS, ANALYSIS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    map_number = 32 if (MAPS / "32_governance_jurisdiction_2026.png").exists() else next_map_number()
    assert map_number == 32, map_number
    actor_frame = pd.DataFrame(ACTORS, columns=["actor_id", "name", "actor_type", "jurisdictional_scale", "geographic_scope", "systems", "operational_or_authority_summary", "source_id", "evidence_strength", "reality_status", "canon_status", "notes"])
    auth_frame = pd.DataFrame(A, columns=AUTH_COLUMNS)
    source_frame = pd.DataFrame(SOURCES, columns=SOURCE_COLUMNS)
    rel_rows = []
    for row in A:
        rel_rows.append([row[0].replace("AUTH", "REL"), row[1], row[2], "actor_system_role", row[3], row[5], row[7], row[8], row[9], row[10], row[11], row[12], row[13]])
    rel_frame = pd.DataFrame(rel_rows, columns=REL_COLUMNS)
    uncertainty_frame = pd.DataFrame(UNCERTAINTIES, columns=UNC_COLUMNS)
    paths = {
        "actors": ANALYSIS / "governance_actors.csv",
        "authorities": ANALYSIS / "governance_authorities.csv",
        "relationships": NETWORKS / "governance_relationships.csv",
        "sources": ANALYSIS / "governance_sources.csv",
        "uncertainties": ANALYSIS / "governance_uncertainty_register.csv",
    }
    write_csv(actor_frame, paths["actors"]); write_csv(auth_frame, paths["authorities"]); write_csv(rel_frame, paths["relationships"]); write_csv(source_frame, paths["sources"]); write_csv(uncertainty_frame, paths["uncertainties"])
    base = render_map(map_number)
    counts = {"actors": len(actor_frame), "authorities": len(auth_frame), "relationships": len(rel_frame), "sources": len(source_frame), "uncertainties": len(uncertainty_frame)}
    build_reports(map_number, counts)
    artifacts = [*paths.values(), base.with_suffix(".png"), base.with_suffix(".svg"), REPORTS / "governance_baseline_sources.md", REPORTS / "governance_baseline_assumptions.md", REPORTS / "governance_baseline_findings.md", REPORTS / "governance_baseline_qa.md"]
    manifest = {"phase": "10A", "map_number": map_number, "status": "implemented_validated_pending_sol_acceptance", "counts": counts, "artifacts": {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    (REPORTS / "governance_baseline_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "10A", "map_number": map_number, **counts}, indent=2))


if __name__ == "__main__":
    main()
