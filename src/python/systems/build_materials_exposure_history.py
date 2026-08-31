"""Build the Phase 2C Luckey-Elmore history tables, graph interfaces, and Map 09."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import pandas as pd
from shapely.geometry import Point

from build_material_flows import MAP_CRS, add_north_scale, load_context


ROOT = Path(__file__).resolve().parents[3]
HISTORY = ROOT / "data" / "processed" / "history"
NETWORKS = ROOT / "data" / "processed" / "networks"
MAPS = ROOT / "outputs" / "maps" / "systems"
REPORTS = ROOT / "reports"
EVENTS_CSV = HISTORY / "materials_exposure_events.csv"
SUBSTANCES_CSV = HISTORY / "materials_exposure_substances.csv"
PATHWAYS_CSV = HISTORY / "materials_exposure_pathways.csv"
SOURCES_CSV = HISTORY / "materials_exposure_sources.csv"
NODES_CSV = NETWORKS / "materials_system_nodes.csv"
EDGES_CSV = NETWORKS / "materials_system_edges.csv"
MATERIAL_SOURCES_CSV = NETWORKS / "materials_system_sources.csv"
MAP09 = MAPS / "09_luckey_elmore_materials_exposure_history"
MANIFEST = REPORTS / "materials_exposure_history_manifest.json"
RETRIEVED = "2026-08-31"


def source(source_id, title, publisher, publication_date, url, source_type, historical_period,
           spatial_scale="non-spatial document", confidence="high", notes=""):
    return {
        "source_id": source_id,
        "title": title,
        "agency_or_publisher": publisher,
        "publication_date": publication_date,
        "URL_or_identifier": url,
        "retrieval_date": RETRIEVED,
        "source_type": source_type,
        "historical_period": historical_period,
        "spatial_scale_if_applicable": spatial_scale,
        "terms": "Public official web page or publication; retain agency attribution.",
        "confidence": confidence,
        "notes": notes,
    }


SOURCES = [
    source("PH2C-USACE-LUCKEY-2026", "Luckey Site", "U.S. Army Corps of Engineers, Buffalo District", "2026-07-16", "https://www.lrd.usace.army.mil/Missions/Projects/Article/3613204/luckey-site/", "government_summary", "1942-2030", "approximately 40-acre site; address point used on map", notes="Primary Phase 2C chronology, contaminant, remedy, and 2026 status source."),
    source("PH2C-USACE-GW-2026", "Groundwater Monitoring Data Release: Fall 2025 Sampling Event", "U.S. Army Corps of Engineers, Buffalo District", "2026-01", "https://d34w7g4gy10iej.cloudfront.net/pubs/pdf_76367.pdf", "regulatory_record", "2002-2025 monitoring series", "site monitoring-well network", notes="Three onsite, non-water-supply wells exceeded the beryllium MCL in September 2025; sampled residential well did not exceed listed COC standards."),
    source("PH2C-USACE-FUSRAP", "Formerly Utilized Sites Remedial Action Program", "U.S. Army Corps of Engineers", "current", "https://www.usace.army.mil/Missions/Environmental/FUSRAP.aspx", "government_summary", "1974-present", notes="Program began in 1974; execution transferred from DOE to USACE in October 1997."),
    source("PH2C-USACE-MILESTONE-2021", "Luckey FUSRAP Site Hits Milestone Trifecta", "U.S. Army Corps of Engineers, Buffalo District", "2021-03-23", "https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3637812/luckey-fusrap-site-hits-milestone-trifecta/", "government_summary", "2018-2021", "site/remediation project", notes="Documents excavation, production-building deconstruction, controlled dust practices, and licensed off-site disposal."),
    source("PH2C-USACE-MILESTONE-2022", "10,000 Truckloads Safely Moved from the Luckey FUSRAP Site", "U.S. Army Corps of Engineers, Buffalo District", "2022-07-21", "https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3636698/10000-truckloads-safely-moved-from-the-luckey-fusrap-site/", "government_summary", "2018-2022", "site-to-licensed-disposal logistics; route not modeled", notes="Documents remediation waste logistics and progress, not historical production transport."),
    source("PH2C-USACE-FY2023", "Progress on Buffalo District FUSRAP Projects Highlighted in Annual Report", "U.S. Army Corps of Engineers, Buffalo District", "2024-02-08", "https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3669657/progress-on-buffalo-district-fusrap-projects-highlighted-in-annual-report/", "government_summary", "2023", "project summary", notes="Documents FY2023 soil disposal and water treatment; values are not used as current totals."),
    source("PH2C-USACE-FIVEYEAR-2021", "Five-Year Review of Selected Remedies: Luckey FUSRAP Site", "U.S. Army Corps of Engineers, Buffalo District", "2021-12-06", "https://www.lrd.usace.army.mil/News/News-Releases/Display/Article/3637910/five-year-review-of-selected-remedies-luckey-formerly-utilized-sites-remedial-a/", "regulatory_record", "2006-2021", "soil and groundwater operable units", notes="Documents CERCLA review, soil excavation remedy, groundwater monitored natural attenuation, and future stewardship."),
    source("PH2C-NIOSH-LUCKEY-2011", "Residual Beryllium Evaluations: Brush Luckey Plant", "NIOSH", "2011-03-09", "https://www.cdc.gov/niosh/ocas/pdfs/tbd/rescon/appx-b2-030911.pdf", "government_summary", "1949-present", "facility-level historical evaluation", notes="Corroborates AEC-contracted beryllium work and remediation period; does not establish individual exposure or illness."),
    source("PH2C-DOE-WORKER-SCREEN", "Brush Luckey Plant Former Construction Worker Screening Projects", "U.S. Department of Energy", "current", "https://www.energy.gov/ehss/brush-luckey-plant-former-construction-worker-screening-projects", "government_summary", "former-worker program", notes="Documents an eligible screening program and exposure concerns, not a finding that a named worker was exposed or ill."),
    source("PH2C-NIOSH-BE-2011", "Preventing Beryllium Sensitization and Chronic Beryllium Disease", "NIOSH", "2011-02", "https://www.cdc.gov/niosh/docs/2011-107/default.html", "government_summary", "modern health context", notes="General occupational-health mechanism and prevention context; not a Luckey or Elmore disease finding."),
    source("PH2C-OSHA-BE-2018", "Occupational Exposure to Beryllium: Final Rule", "Occupational Safety and Health Administration", "2018-03-07", "https://www.osha.gov/laws-regs/federalregister/2018-03-07", "regulatory_record", "modern regulation", notes="Documents current PEL/STEL and exposure assessment, controls, PPE, housekeeping, surveillance, communication, and recordkeeping requirements."),
    source("PH2C-ATSDR-BE-2022", "Toxicological Profile for Beryllium", "Agency for Toxic Substances and Disease Registry", "2022-09", "https://www.atsdr.cdc.gov/toxprofiles/tp4.pdf", "government_summary", "modern toxicological context", notes="General inhalation/dermal health context; no site-specific disease inference."),
    source("PH2C-ATSDR-ELMORE-2006", "Brush Wellman Elmore Plant Health Consultation", "Agency for Toxic Substances and Disease Registry", "2006-12-01", "https://www.atsdr.cdc.gov/HAC/PHA/brush_wellman/BrushWellmanHCRevised120106.pdf", "regulatory_record", "historical Elmore review through 2006", "facility/community review", notes="Historical public-health consultation; not evidence of 2026 conditions or a Luckey-to-Elmore production link."),
]


def event(event_id, site_id, site_name, start_date, end_date, date_precision, event_type, material,
          activity, role, agency, operator, source_id, confidence="high", notes="", reality_status="historical", canon_status="verified"):
    return locals()


EVENTS = [
    event("MEH-E001", "LUCKEY", "Luckey Site", "1942", "1945", "range", "historical_production", "magnesium", "Federal magnesium processing facility operated during World War II", "production", "U.S. government", "National Lead", "PH2C-USACE-LUCKEY-2026"),
    event("MEH-E002", "LUCKEY", "Luckey Site", "1949", "1958", "range", "historical_production", "beryllium", "AEC beryllium production", "production", "Atomic Energy Commission", "Brush Beryllium Company", "PH2C-USACE-LUCKEY-2026", notes="Produced beryllium oxide, hydroxide, and pebbles."),
    event("MEH-E003", "LUCKEY", "Luckey Site", "1951", "1952", "approximate", "material_storage", "radioactively contaminated scrap metal", "Approximately 1,000 tons sent for proposed magnesium processing but not used", "storage", "Atomic Energy Commission", "Brush Beryllium Company", "PH2C-USACE-LUCKEY-2026", notes="USACE states site investigations determined this scrap did not cause the site's radioactive contamination."),
    event("MEH-E004", "LUCKEY", "Luckey Site", "1957", "1960", "range", "historical_production", "beryllium", "Sintering and powder blending", "production", "Atomic Energy Commission", "Brush Beryllium Company", "PH2C-USACE-LUCKEY-2026"),
    event("MEH-E005", "LUCKEY", "Luckey Site", "1958", "1958", "year", "production_cessation", "beryllium", "Beryllium production ceased", "closure", "Atomic Energy Commission", "Brush Beryllium Company", "PH2C-USACE-LUCKEY-2026"),
    event("MEH-E006", "LUCKEY", "Luckey Site", "1959", "1959", "year", "closure", "process sludge", "AEC closure contract and two-acre diked landfill construction", "waste management", "Atomic Energy Commission", "Brush Beryllium Company", "PH2C-USACE-LUCKEY-2026", notes="Sludge from three lagoons was reportedly moved to the landfill, capped, graded, and seeded."),
    event("MEH-E007", "LUCKEY", "Luckey Site", "1961", "1961", "year", "ownership_transition", "not applicable", "Federal sale of facility", "ownership", "General Services Administration", "various subsequent owners", "PH2C-USACE-LUCKEY-2026"),
    event("MEH-E008", "PROGRAM", "FUSRAP", "1974", "1974", "year", "federal_program", "radiological legacy", "FUSRAP initiated", "institutional response", "U.S. Department of Energy predecessor program", "not applicable", "PH2C-USACE-FUSRAP", reality_status="real"),
    event("MEH-E009", "LUCKEY", "Luckey Site", "1992", "1992", "year", "federal_designation", "beryllium", "Luckey designated a FUSRAP site due to extensive surface contamination", "designation", "U.S. Department of Energy", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E010", "PROGRAM", "FUSRAP", "1997-10", "1997-10", "month", "agency_transition", "radiological legacy", "Congress transferred FUSRAP execution from DOE to USACE", "institutional response", "U.S. Congress / USACE / DOE", "not applicable", "PH2C-USACE-FUSRAP", reality_status="real"),
    event("MEH-E011", "LUCKEY", "Luckey Site", "2000", "2000", "year", "site_characterization", "multiple contaminants", "Remedial investigation report released", "characterization", "USACE", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E012", "LUCKEY", "Luckey Site", "2003", "2003", "year", "remedial_investigation", "multiple contaminants", "Feasibility study and proposed plan released", "remedy development", "USACE", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E013", "LUCKEY", "Luckey Site", "2006", "2006", "year", "regulatory_decision", "beryllium; lead; radium-226; thorium-230; uranium-234; uranium-238", "Soils Record of Decision selected excavation and off-site disposal", "soil remedy", "USACE under CERCLA", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E014", "ELMORE", "Materion Elmore", "2006-12-01", "2006-12-01", "exact_date", "public_health_review", "beryllium", "ATSDR health consultation published", "historical regulatory review", "ATSDR", "Brush Wellman", "PH2C-ATSDR-ELMORE-2006", reality_status="real", notes="Historical consultation; not a statement of current 2026 conditions."),
    event("MEH-E015", "LUCKEY", "Luckey Site", "2008", "2008", "year", "regulatory_decision", "beryllium; lead; uranium", "Groundwater Record of Decision selected monitored natural attenuation and land-use controls", "groundwater remedy", "USACE under CERCLA", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E016", "LUCKEY", "Luckey Site", "2010-03", "2010-03", "month", "site_characterization", "soil and radiological conditions", "Additional sampling and radiological, geophysical, and topographic surveys", "characterization", "USACE", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E017", "LUCKEY", "Luckey Site", "2015", "2015", "year", "cleanup_design", "FUSRAP-contaminated soil", "Soil-cleanup contract awarded", "remedy implementation", "USACE", "remediation contractor", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E018", "LUCKEY", "Luckey Site", "2016-09", "2016-09", "month", "remediation", "FUSRAP-contaminated soil", "Mobilization plus background soil and air sampling", "remedy implementation and controls", "USACE", "remediation contractor", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E019", "LUCKEY", "Luckey Site", "2017-03", "2017-03", "month", "regulatory_decision", "FUSRAP-contaminated soil", "Explanation of Significant Differences revised cost, volume, and building-removal scope", "remedy revision", "USACE", "not applicable", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E020", "LUCKEY", "Luckey Site", "2018-04-16", "2018-04-16", "exact_date", "excavation", "FUSRAP-contaminated soil", "Soil remediation began at former lagoons", "excavation and off-site disposal", "USACE", "remediation contractor", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E021", "LUCKEY", "Luckey Site", "2021-02", "2021-09-08", "range", "building_removal", "building debris and underlying soil", "Production and six other buildings deconstructed for subsurface access", "remediation", "USACE", "remediation contractor", "PH2C-USACE-LUCKEY-2026", reality_status="real"),
    event("MEH-E022", "LUCKEY", "Luckey Site", "2021-12-06", "2021-12-06", "exact_date", "five_year_review", "soil and groundwater remedies", "CERCLA five-year review announced", "regulatory review", "USACE", "not applicable", "PH2C-USACE-FIVEYEAR-2021", reality_status="real"),
    event("MEH-E023", "ELMORE", "Materion Elmore", "2022-07-27", "2022-07-27", "exact_date", "documented_supply_relationship", "beryllium fluoride / FLiBe", "Materion-Kairos collaboration documented", "current strategic processing", "not applicable", "Materion", "SRC-MATERION-KAIROS-2022", reality_status="real", notes="2026 operating status not independently reverified."),
    event("MEH-E024", "LUCKEY", "Luckey Site", "2022-07-20", "2022-07-20", "exact_date", "waste_shipment", "remediation waste", "10,000th remediation truckload milestone", "licensed off-site disposal", "USACE", "remediation contractor", "PH2C-USACE-MILESTONE-2022", reality_status="real", notes="Waste-logistics milestone; no production-supply route is modeled."),
    event("MEH-E025", "LUCKEY", "Luckey Site", "2023", "2023", "year", "cleanup_milestone", "contaminated soil and collected site water", "Continued excavation, off-site disposal, and water treatment", "remediation", "USACE", "remediation contractor", "PH2C-USACE-FY2023", reality_status="real"),
    event("MEH-E026", "ELMORE", "Materion Elmore", "2025-10-31", "2025-10-31", "exact_date", "documented_supply_relationship", "beryllium fluoride / FLiBe", "Materion-CFS supply agreement announced", "current strategic processing", "not applicable", "Materion", "SRC-MATERION-CFS-2025", reality_status="real"),
    event("MEH-E027", "LUCKEY", "Luckey Site", "2025-09-15", "2025-09-17", "range", "groundwater_monitoring", "beryllium; lead; total uranium", "Fall groundwater sampling event", "monitoring", "USACE", "not applicable", "PH2C-USACE-GW-2026", reality_status="real", notes="Three onsite non-water-supply wells exceeded the beryllium MCL; sampled residential well did not exceed listed COC standards."),
    event("MEH-E028", "LUCKEY", "Luckey Site", "2025", "2027", "range", "remediation", "soil; building slabs; utilities", "Ongoing final soil-remediation phases", "remediation", "USACE", "remediation contractor", "PH2C-USACE-LUCKEY-2026", reality_status="real", notes="Official schedule anticipates all cleanup fieldwork by 2027; completion has not yet occurred."),
    event("MEH-E029", "LUCKEY", "Luckey Site", "2027", "2028", "range", "planned_milestone", "not applicable", "Planned project closeout", "scheduled institutional transition", "USACE", "not applicable", "PH2C-USACE-LUCKEY-2026", confidence="medium_high", reality_status="real", notes="Documented schedule, not a completed event."),
    event("MEH-E030", "LUCKEY", "Luckey Site", "2030", "2030", "approximate", "planned_milestone", "groundwater stewardship", "Planned transfer of long-term management to DOE Legacy Management", "scheduled institutional transition", "USACE / DOE", "not applicable", "PH2C-USACE-LUCKEY-2026", confidence="medium_high", reality_status="real", notes="USACE says transfer by 2030; date is a plan, not completion."),
]


SUBSTANCES = [
    {"substance_id":"MES-S01","site_id":"LUCKEY","material":"magnesium","historical_role":"wartime processing product/process","date_range":"1942-1945","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"historical process documented; not listed by USACE as a current contaminant of concern","medium":"facility/process","confidence":"high","notes":"Do not convert historical handling into a contamination claim."},
    {"substance_id":"MES-S02","site_id":"LUCKEY","material":"beryl ore / beryllium-bearing feed","historical_role":"feed for beryllium extraction","date_range":"1949-1958","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"process generated beryllium-bearing and radionuclide-bearing waste","medium":"process feed and wastes","confidence":"high","notes":"Exact feed origin and transport route are not modeled."},
    {"substance_id":"MES-S03","site_id":"LUCKEY","material":"beryllium oxide; beryllium hydroxide; beryllium pebbles","historical_role":"documented products","date_range":"1949-1958","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"beryllium is a soil and groundwater contaminant of concern","medium":"soil; groundwater; former buildings/waste areas","confidence":"high","notes":"Production history does not establish individual exposure."},
    {"substance_id":"MES-S04","site_id":"LUCKEY","material":"radioactively contaminated scrap metal","historical_role":"stored for proposed magnesium production; not used","date_range":"late 1951-early 1952 onward","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"USACE determined the scrap did not cause site radioactive contamination","medium":"stored material","confidence":"high","notes":"Preserve this negative causation finding."},
    {"substance_id":"MES-S05","site_id":"LUCKEY","material":"lead","historical_role":"not specified as a product","date_range":"legacy/remediation era","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"soil and groundwater contaminant of concern","medium":"soil; groundwater","confidence":"high","notes":"No unsupported production role assigned."},
    {"substance_id":"MES-S06","site_id":"LUCKEY","material":"radium-226","historical_role":"naturally associated element concentrated in process wastes","date_range":"beryllium-production legacy","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"soil contaminant addressed by the 2006 remedy","medium":"soil/process waste","confidence":"high","notes":"Not presented as an intended product."},
    {"substance_id":"MES-S07","site_id":"LUCKEY","material":"thorium-230","historical_role":"naturally associated element concentrated in process wastes","date_range":"beryllium-production legacy","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"soil contaminant addressed by the 2006 remedy","medium":"soil/process waste","confidence":"high","notes":"Not presented as an intended product."},
    {"substance_id":"MES-S08","site_id":"LUCKEY","material":"uranium-234 and uranium-238 / total uranium","historical_role":"naturally associated elements concentrated in process wastes","date_range":"beryllium-production legacy through current monitoring","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"soil and groundwater contaminant of concern","medium":"soil; groundwater; process waste","confidence":"high","notes":"Current monitoring reports total uranium; no plume geometry modeled."},
    {"substance_id":"MES-S09","site_id":"LUCKEY","material":"lagoon sludge / process waste solutions","historical_role":"waste from beryllium processing","date_range":"1949-1959","source_id":"PH2C-USACE-LUCKEY-2026","contamination_status":"reportedly moved to onsite landfill during closure; former lagoon areas entered excavation remedy","medium":"lagoons; landfill; soil","confidence":"high","notes":"Reported movement is preserved as reported, not upgraded to surveyed geometry."},
]


PATHWAYS = [
    {"pathway_id":"MEP-P01","site_id":"LUCKEY","period":"1949-1960","pathway":"occupational inhalation of process dust/fume","evidence_class":"potential_exposure_pathway","documented_human_exposure":"false","environmental_medium":"workplace air","source_id":"PH2C-NIOSH-BE-2011","confidence":"medium","notes":"Process and general beryllium mechanism are documented; no individual Luckey exposure or illness is asserted."},
    {"pathway_id":"MEP-P02","site_id":"LUCKEY","period":"1949-1960","pathway":"occupational skin contact with beryllium-bearing material","evidence_class":"potential_exposure_pathway","documented_human_exposure":"false","environmental_medium":"workplace surfaces/material","source_id":"PH2C-ATSDR-BE-2022","confidence":"medium","notes":"General mechanism only; no individual outcome asserted."},
    {"pathway_id":"MEP-P03","site_id":"LUCKEY","period":"legacy","pathway":"process waste to soil","evidence_class":"documented_environmental_contamination","documented_human_exposure":"false","environmental_medium":"soil","source_id":"PH2C-USACE-LUCKEY-2026","confidence":"high","notes":"Soil contamination and excavation remedy are documented; this is not proof of human exposure."},
    {"pathway_id":"MEP-P04","site_id":"LUCKEY","period":"legacy/current monitoring","pathway":"contaminants in groundwater below the site","evidence_class":"documented_environmental_contamination","documented_human_exposure":"false","environmental_medium":"groundwater","source_id":"PH2C-USACE-GW-2026","confidence":"high","notes":"September 2025 beryllium exceedances were in three onsite wells not used for water supply; sampled residential well did not exceed listed standards."},
    {"pathway_id":"MEP-P05","site_id":"LUCKEY","period":"remediation","pathway":"excavation/deconstruction dust potential","evidence_class":"controlled_potential_pathway","documented_human_exposure":"false","environmental_medium":"worksite air","source_id":"PH2C-USACE-MILESTONE-2021","confidence":"high","notes":"USACE documents background/operational air monitoring, water-spray dust control, and methodical deconstruction."},
    {"pathway_id":"MEP-P06","site_id":"LUCKEY","period":"2018-present","pathway":"remediation waste handling and off-site disposal","evidence_class":"documented_waste_logistics","documented_human_exposure":"false","environmental_medium":"containerized soil/debris","source_id":"PH2C-USACE-MILESTONE-2022","confidence":"high","notes":"No transport route is drawn; destination detail is retained only in the source report."},
    {"pathway_id":"MEP-P07","site_id":"ELMORE","period":"modern","pathway":"occupational inhalation or skin contact potential in beryllium processing","evidence_class":"generalized_regulated_pathway","documented_human_exposure":"false","environmental_medium":"workplace air/surfaces","source_id":"PH2C-OSHA-BE-2018","confidence":"medium_high","notes":"General regulatory context, not a Materion compliance finding or evidence of current worker exposure."},
]


GRAPH_SOURCES = {
    s["source_id"]: {
        "source_id": s["source_id"], "title": s["title"], "agency_or_publisher": s["agency_or_publisher"],
        "url_or_identifier": s["URL_or_identifier"], "retrieved_date": s["retrieval_date"],
        "publication_or_dataset_date": s["publication_date"], "spatial_resolution_or_scale": s["spatial_scale_if_applicable"],
        "license_or_terms": s["terms"], "confidence": s["confidence"], "source_type": s["source_type"], "notes": s["notes"],
    } for s in SOURCES
}


GRAPH_NODES = [
    {"node_id":"EXP-PATH-HIST-OCC","name":"Historical occupational exposure potential","material_system":"exposure","node_type":"exposure_pathway","supply_chain_role":"exposure_pathway","reality_status":"historical","canon_status":"inferred","local_resource":"not_applicable","scenario_year":"historical","region":"Exposure / Environmental Health interface","latitude":"","longitude":"","source_id":"PH2C-NIOSH-BE-2011","confidence":"medium","notes":"Potential inhalation/skin-contact pathway; no individual Luckey exposure or disease is asserted."},
    {"node_id":"EXP-LEG-ENV-CONTAM","name":"Luckey environmental contamination legacy","material_system":"exposure","node_type":"environmental_legacy","supply_chain_role":"legacy_contamination","reality_status":"historical","canon_status":"verified","local_resource":"not_applicable","scenario_year":"historical","region":"Black Swamp Country","latitude":"","longitude":"","source_id":"PH2C-USACE-LUCKEY-2026","confidence":"high","notes":"Documented soil and groundwater contamination; no plume or exposure radius geometry."},
    {"node_id":"EXP-REM-FUSRAP","name":"Luckey FUSRAP remediation system","material_system":"exposure","node_type":"regulatory_program","supply_chain_role":"remediation","reality_status":"real","canon_status":"verified","local_resource":"not_applicable","scenario_year":"2026","region":"Black Swamp Country","latitude":"","longitude":"","source_id":"PH2C-USACE-LUCKEY-2026","confidence":"high","notes":"Current cleanup/monitoring institution; not current production."},
    {"node_id":"EXP-IF-WASTE-LOGISTICS","name":"Licensed remediation waste logistics","material_system":"exposure","node_type":"system_interface","supply_chain_role":"logistics_interface","reality_status":"real","canon_status":"verified","local_resource":"not_applicable","scenario_year":"2026","region":"External remediation interface","latitude":"","longitude":"","source_id":"PH2C-USACE-MILESTONE-2022","confidence":"high","notes":"Off-site licensed disposal is documented; no route geometry is modeled."},
    {"node_id":"EXP-CTRL-MODERN","name":"Modern beryllium industrial-hygiene controls","material_system":"exposure","node_type":"control_system","supply_chain_role":"exposure_control","reality_status":"real","canon_status":"verified","local_resource":"not_applicable","scenario_year":"2026","region":"Exposure / Environmental Health interface","latitude":"","longitude":"","source_id":"PH2C-OSHA-BE-2018","confidence":"high","notes":"General current regulatory requirements; not a facility-specific compliance conclusion."},
]


GRAPH_EDGES = [
    {"edge_id":"EXP-E01","from_id":"BER-LEG-LUCKEY","to_id":"EXP-PATH-HIST-OCC","material":"beryllium-bearing dust/contact","flow_type":"potential_exposure_pathway","relationship_basis":"scientific_inference","reality_status":"historical","canon_status":"inferred","confidence":"medium","source_id":"PH2C-NIOSH-BE-2011","relationship_date":"1949-1960","current_status":"historical_potential; no individual exposure finding","notes":"Production plus general hazard mechanism support a potential pathway, not documented individual exposure or disease."},
    {"edge_id":"EXP-E02","from_id":"BER-LEG-LUCKEY","to_id":"EXP-LEG-ENV-CONTAM","material":"beryllium; lead; radionuclides","flow_type":"historical_legacy","relationship_basis":"historical_documentation","reality_status":"historical","canon_status":"verified","confidence":"high","source_id":"PH2C-USACE-LUCKEY-2026","relationship_date":"1949-present legacy","current_status":"documented_environmental_legacy","notes":"Documented process wastes and contamination; no direct Luckey-to-Elmore continuity inferred."},
    {"edge_id":"EXP-E03","from_id":"EXP-LEG-ENV-CONTAM","to_id":"EXP-REM-FUSRAP","material":"contaminated soil and groundwater","flow_type":"legacy_to_remediation","relationship_basis":"observed","reality_status":"real","canon_status":"verified","confidence":"high","source_id":"PH2C-USACE-LUCKEY-2026","relationship_date":"1992-present","current_status":"active_cleanup_and_monitoring","notes":"FUSRAP designation, remedies, excavation, and monitoring are documented."},
    {"edge_id":"EXP-E04","from_id":"EXP-REM-FUSRAP","to_id":"EXP-IF-WASTE-LOGISTICS","material":"excavated soil and building debris","flow_type":"remediation_to_waste_logistics","relationship_basis":"observed","reality_status":"real","canon_status":"verified","confidence":"high","source_id":"PH2C-USACE-MILESTONE-2022","relationship_date":"2018-present","current_status":"documented_licensed_offsite_disposal","notes":"No route, schedule, or future quantity is modeled."},
    {"edge_id":"EXP-E05","from_id":"BER-PROC-ELMORE","to_id":"EXP-CTRL-MODERN","material":"beryllium processing controls","flow_type":"processing_to_controls","relationship_basis":"regulatory_requirement","reality_status":"real","canon_status":"inferred","confidence":"medium_high","source_id":"PH2C-OSHA-BE-2018","relationship_date":"2017-present","current_status":"general_regulatory_context","notes":"OSHA requirements provide a modern control interface; this is not a facility-specific compliance audit or safety conclusion."},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def append_unique(path: Path, rows: list[dict], key: str) -> pd.DataFrame:
    current = pd.read_csv(path, keep_default_na=False)
    additions = pd.DataFrame(rows)
    additions = additions[current.columns]
    merged = pd.concat([current[~current[key].isin(additions[key])], additions], ignore_index=True)
    merged.to_csv(path, index=False)
    return merged


def box(ax, xy, text, fc, ec="#334e68", width=0.25, height=0.12, size=8.2):
    x, y = xy
    patch = FancyBboxPatch((x-width/2, y-height/2), width, height, boxstyle="round,pad=0.012", fc=fc, ec=ec, lw=1.25, transform=ax.transAxes)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", transform=ax.transAxes, fontsize=size, color="#17324d")


def arrow(ax, start, end, color="#526d82", dashed=False):
    ax.annotate("", xy=end, xytext=start, xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, linestyle="--" if dashed else "-", mutation_scale=11))


def render_map(events: pd.DataFrame) -> None:
    _, hydro, lake, roads, places = load_context()
    fig = plt.figure(figsize=(17, 10.5), facecolor="#f7f4ec")
    grid = fig.add_gridspec(2, 2, width_ratios=[0.84, 1.36], height_ratios=[0.68, 0.32], wspace=0.055, hspace=0.12)
    ax = fig.add_subplot(grid[:, 0]); timeline = fig.add_subplot(grid[0, 1]); pathways = fig.add_subplot(grid[1, 1])
    ax.set_facecolor("#eef3f5")
    lake.plot(ax=ax, color="#d7edf5", edgecolor="#6d9fb5", linewidth=0.7)
    hydro.plot(ax=ax, color="#4b91aa", linewidth=0.45, alpha=0.58)
    roads.plot(ax=ax, color="#8b98a5", linewidth=0.55, alpha=0.48)
    focus = (-83.78, 41.30, -82.97, 41.70)
    bounds = gpd.GeoSeries([Point(focus[0], focus[1]), Point(focus[2], focus[3])], crs=4326).to_crs(MAP_CRS)
    minx, miny = bounds.iloc[0].x, bounds.iloc[0].y; maxx, maxy = bounds.iloc[1].x, bounds.iloc[1].y
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy); ax.set_xticks([]); ax.set_yticks([])
    points = gpd.GeoDataFrame(
        [{"name":"Luckey FUSRAP","kind":"legacy","geometry":Point(-83.490434663133,41.458801748910)},
         {"name":"Materion Elmore","kind":"current","geometry":Point(-83.215860027455,41.491149985926)}], crs=4326).to_crs(MAP_CRS)
    luckey = points[points.kind == "legacy"]; elmore = points[points.kind == "current"]
    luckey.plot(ax=ax, marker="X", color="#a33d2e", edgecolor="#5f2118", markersize=170, zorder=8)
    elmore.plot(ax=ax, marker="*", color="#167d8d", edgecolor="white", linewidth=1.2, markersize=280, zorder=8)
    lr = next(luckey.itertuples()); er = next(elmore.itertuples())
    ax.annotate("LUCKEY\nHISTORICAL PRODUCTION\nCURRENT REMEDIATION", (lr.geometry.x, lr.geometry.y), xytext=(12, -46), textcoords="offset points", ha="left", fontsize=8.2, weight="bold", color="#7f1d1d", bbox=dict(boxstyle="round,pad=0.3", fc="#fee2e2", ec="#b4534b"))
    ax.annotate("ELMORE\nCURRENT ADVANCED PROCESSING\nLOCAL EXTRACTION = FALSE", (er.geometry.x, er.geometry.y), xytext=(-12, 13), textcoords="offset points", ha="right", fontsize=8.2, weight="bold", color="#0f5f6b", bbox=dict(boxstyle="round,pad=0.3", fc="#dff7f7", ec="#167d8d"))
    place_points = places.copy(); place_points["geometry"] = place_points.geometry.representative_point()
    for row in place_points[place_points.BASENAME.isin({"Toledo","Luckey","Elmore","Woodville","Genoa","Oak Harbor","Fremont"})].itertuples():
        ax.plot(row.geometry.x, row.geometry.y, "o", ms=2.4, color="#52606d")
        ax.annotate(row.BASENAME, (row.geometry.x, row.geometry.y), xytext=(3,-6), textcoords="offset points", fontsize=7.3, color="#52606d")
    ax.set_title("REGIONAL ANCHOR", loc="left", fontsize=14, color="#17324d", weight="bold")
    ax.text(0.02, 0.025, "Authoritative facility points; physical waterways for context only.\nNo contamination plume, exposure radius, groundwater arrow,\nor Luckey→Elmore production-flow link is mapped.", transform=ax.transAxes, fontsize=7.8, color="#486581", bbox=dict(boxstyle="round,pad=0.3", fc="#fff", ec="#bcccdc", alpha=0.94))
    add_north_scale(ax, minx+5000, miny+5500, 25_000)

    timeline.set_facecolor("#faf8f2"); timeline.set_xlim(1938, 2032); timeline.set_ylim(-0.3, 4.5)
    timeline.set_yticks([0.4,1.4,2.4,3.4], ["CURRENT / PLANNED", "REMEDIATION", "LEGACY / OVERSIGHT", "HISTORICAL PRODUCTION"])
    timeline.set_xticks([1940,1950,1960,1970,1980,1990,2000,2010,2020,2030]); timeline.grid(axis="x", color="#d9e2ec", lw=0.7)
    timeline.tick_params(axis="y", labelsize=8.3); timeline.tick_params(axis="x", labelsize=8)
    for spine in ["top","right","left"]: timeline.spines[spine].set_visible(False)
    milestones = [
        (1942,3.4,"1942–45\nMg / National Lead","#b76e2b",0,0.34), (1949,3.4,"1949–58\nBe production","#b76e2b",0,-0.34),
        (1960,3.4,"1960\nsintering ends","#b76e2b",0,0.34), (1992,2.4,"1992\nFUSRAP","#8f4752",0,-0.34),
        (1997,2.4,"1997\nUSACE lead","#8f4752",0,0.34), (2006,2.4,"2006\nsoil ROD","#8f4752",0,-0.34),
        (2008,2.4,"2008\nGW ROD","#8f4752",0,0.34), (2018.3,1.4,"2018\nexcavation","#2f855a",0,-0.34),
        (2021.7,1.4,"2021\nbuildings removed","#2f855a",-0.2,0.36), (2022.57,0.4,"2022\nKairos","#167d8d",-1.4,-0.34),
        (2025.83,0.4,"2025\nCFS","#167d8d",-0.6,0.38), (2026.3,1.4,"2026\ncleanup + monitoring","#2f855a",1.1,-0.34),
        (2027.2,0.4,"by 2027\nfieldwork plan","#6b7280",1.1,0.16), (2030,0.4,"by 2030\nLM transfer plan","#6b7280",0,-0.34),
    ]
    for x,y,label,color,dx,dy in milestones:
        timeline.scatter([x],[y],s=65,color=color,edgecolor="white",linewidth=0.8,zorder=4)
        timeline.annotate(label,(x,y),xytext=(x+dx,y+dy),textcoords="data",ha="center",va="center",fontsize=7.1,color="#243b53",arrowprops=dict(arrowstyle="-",color=color,lw=0.8))
    timeline.set_title("MAP 09 — LUCKEY–ELMORE MATERIALS / EXPOSURE HISTORY\nSource-grounded chronology · plans remain plans", loc="left", fontsize=15, color="#17324d", weight="bold", pad=13)
    timeline.text(0.99,0.02,"Luckey production ≠ Luckey remediation ≠ Elmore current processing",transform=timeline.transAxes,ha="right",fontsize=8.5,color="#7f1d1d",weight="bold")

    pathways.set_axis_off(); pathways.set_xlim(0,1); pathways.set_ylim(0,1)
    pathways.text(0.0,0.96,"QUALIFIED EXPOSURE / CONTROL INTERFACES",transform=pathways.transAxes,fontsize=11.5,weight="bold",color="#17324d")
    box(pathways,(0.12,0.68),"LUCKEY\nhistorical process",fc="#fde7c2",ec="#b76e2b",width=0.20)
    box(pathways,(0.40,0.68),"POTENTIAL WORKPLACE\ndust / inhalation / contact\nNO individual exposure finding",fc="#fff1d6",ec="#d3993f",width=0.30,height=0.16,size=7.6)
    box(pathways,(0.69,0.68),"DOCUMENTED LEGACY\nsoil + groundwater",fc="#fee2e2",ec="#a33d2e",width=0.22)
    box(pathways,(0.90,0.68),"FUSRAP\nexcavate · dispose\nmonitor",fc="#dcfce7",ec="#2f855a",width=0.16,height=0.16,size=7.4)
    arrow(pathways,(0.22,0.68),(0.25,0.68),color="#b76e2b",dashed=True)
    arrow(pathways,(0.55,0.68),(0.58,0.68),color="#a33d2e",dashed=True)
    arrow(pathways,(0.80,0.68),(0.82,0.68),color="#2f855a")
    box(pathways,(0.18,0.27),"ELMORE\ncurrent advanced processing\nNOT extraction",fc="#dff7f7",ec="#167d8d",width=0.25,height=0.17,size=7.5)
    box(pathways,(0.52,0.27),"MODERN CONTROL CONTEXT\nexposure assessment · engineering controls\nPPE · housekeeping · medical surveillance",fc="#e0f2fe",ec="#287aa1",width=0.32,height=0.18,size=7.1)
    arrow(pathways,(0.305,0.27),(0.36,0.27),color="#167d8d")
    pathways.text(0.84,0.27,"General OSHA context —\nnot a facility compliance finding\nand not a claim that modern\noperations are risk-free.",transform=pathways.transAxes,ha="center",va="center",fontsize=7.2,color="#486581")
    pathways.text(0.5,0.025,"Health context: beryllium sensitization/CBD are established occupational hazards. Map 09 attributes no illness to a Luckey or Elmore individual.",transform=pathways.transAxes,ha="center",fontsize=7.5,color="#486581")

    for suffix in ["png","svg"]:
        fig.savefig(MAP09.with_suffix(f".{suffix}"), dpi=220 if suffix == "png" else None, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    HISTORY.mkdir(parents=True, exist_ok=True); MAPS.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    events = pd.DataFrame(EVENTS); substances = pd.DataFrame(SUBSTANCES); pathways = pd.DataFrame(PATHWAYS); sources = pd.DataFrame(SOURCES)
    events.to_csv(EVENTS_CSV,index=False); substances.to_csv(SUBSTANCES_CSV,index=False); pathways.to_csv(PATHWAYS_CSV,index=False); sources.to_csv(SOURCES_CSV,index=False)
    nodes = append_unique(NODES_CSV, GRAPH_NODES, "node_id")
    edges = append_unique(EDGES_CSV, GRAPH_EDGES, "edge_id")
    graph_sources = append_unique(MATERIAL_SOURCES_CSV, list(GRAPH_SOURCES.values()), "source_id")
    render_map(events)
    artifacts = [EVENTS_CSV,SUBSTANCES_CSV,PATHWAYS_CSV,SOURCES_CSV,NODES_CSV,EDGES_CSV,MATERIAL_SOURCES_CSV,MAP09.with_suffix(".png"),MAP09.with_suffix(".svg")]
    manifest = {
        "phase":"Phase 2C - strategic materials, exposure and remediation history",
        "counts":{"events":len(events),"substances":len(substances),"pathways":len(pathways),"sources":len(sources),"materials_nodes_total":len(nodes),"materials_edges_total":len(edges),"materials_sources_total":len(graph_sources),"new_graph_nodes":len(GRAPH_NODES),"new_graph_edges":len(GRAPH_EDGES)},
        "exposure_findings":{"documented_individual_exposure_count":0,"potential_or_environmental_pathway_count":len(pathways)},
        "scientific_constraints":{"luckey_current_production":False,"elmore_local_extraction":False,"direct_luckey_to_elmore_flow":False,"contamination_polygon_created":False,"groundwater_plume_created":False,"exposure_radius_created":False,"map_10_created":False},
        "files":{str(p.relative_to(ROOT)).replace("\\","/"):sha256(p) for p in artifacts},
    }
    MANIFEST.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
