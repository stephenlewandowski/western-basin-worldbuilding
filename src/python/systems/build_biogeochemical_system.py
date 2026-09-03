"""Build Phase 8A-8C biogeochemical and nutrient-flux products."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
SCEN_DIR = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

SRC = [
    ["bge_usgs_wbd", "USGS Watershed Boundary Dataset", "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer", "Watershed and HUC scale context; not a loading surface.", "federal_dataset"],
    ["bge_usgs_3dhp", "USGS 3D Hydrography Program", "https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer", "Mapped physical water-carrier context; not a complete nutrient-flow model.", "federal_dataset"],
    ["bge_epa_lake_erie", "US EPA Lake Erie Water Quality Data", "https://www.epa.gov/glwqa/lake-erie-water-quality-data", "Annual phosphorus loads, western-basin HAB context, and target/status framing.", "federal_web"],
    ["bge_epa_mwn_tmdl", "US EPA Maumee Watershed Nutrient TMDL approval", "https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load", "Approved TP TMDL planning and point/nonpoint allocation context.", "federal_web"],
    ["bge_epa_mwn_tmdl_faqs", "US EPA Maumee Watershed Nutrient TMDL FAQs", "https://www.epa.gov/system/files/documents/2023-09/maumee-watershed-nutrient-tmdl-faqs.pdf", "Spring TP loading-capacity and Waterville target framing; planning values, not observed loads.", "federal_document"],
    ["bge_epa_mwn_tmdl_tables", "US EPA/Ohio EPA Maumee Watershed Nutrient TMDL Tables", "https://www.epa.gov/system/files/documents/2023-09/2023.9.18_att_1_mwn-tmdl-tables.pdf", "Spring TP point/nonpoint allocation table; planning allocations, not measured source contributions.", "federal_document"],
    ["bge_noaa_hab", "NOAA NCCOS Lake Erie HAB Forecast", "https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/", "HAB monitoring/forecast interface; no new predictive model.", "federal_science"],
    ["bge_ncwqr", "Heidelberg University NCWQR monitoring program", "https://ncwqr.org/", "Public Great Lakes surface-water monitoring and data-portal context.", "institutional_program"],
    ["bge_nass", "USDA NASS Cropland Data Layer", "https://www.nass.usda.gov/Research_and_Science/Cropland/Release/", "Agricultural landscape context; not farm-level management or export attribution.", "federal_dataset"],
    ["bge_nrscs", "USDA NRCS Conservation Practice Standards", "https://www.nrcs.usda.gov/conservation-basics/conservation-by-state/ohio", "Conservation and soil-management control context; effectiveness is site-dependent.", "federal_program"],
    ["bge_ohio_h2ohio", "Ohio H2Ohio program", "https://h2.ohio.gov/", "Documented nutrient-management, wetlands, and water-quality intervention context.", "state_program"],
    ["bge_ohio_epa_npdes", "Ohio EPA NPDES program", "https://epa.ohio.gov/divisions-and-offices/surface-water/permitting", "Permitted discharge and treatment regulatory context; permits are not actual loads.", "state_regulatory"],
    ["bge_usfws_nwi", "USFWS National Wetlands Inventory", "https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer", "Wetland inventory and broad retention/transformation interface; no uniform removal rate.", "federal_dataset"],
    ["bge_glri_annex4", "Great Lakes Water Quality Agreement Annex 4", "https://binational.net/annexes/a4/", "Binational nutrient-reduction target and adaptive-management context.", "binational_program"],
    ["bge_noaa_climate", "NOAA climate data and projections", "https://www.ncei.noaa.gov/", "External qualitative scenario driver for precipitation, temperature, and hydrologic variability.", "federal_science"],
]

NODE_COLS = ["node_id","name","domain","node_type","status","scale","latitude","longitude","spatial_role","source_id","confidence","notes"]
EDGE_COLS = ["edge_id","from_id","to_id","material","relationship_type","flux_status","relationship_basis","scale","source_id","confidence","quantity_status","notes"]
Q_COLS = ["flux_id","material","chemical_form","source_or_station","destination_or_scope","metric","value","units","period","year","method","source_id","confidence","notes"]

NODES = [
 ["BGC-001","Agricultural soil and crop landscape","agriculture","agricultural_landscape","factual_2026","regional / HUC8","","","landscape context","bge_nass","moderate","Cropland context; no individual farm, parcel behavior, or soil-stock quantity asserted."],
 ["BGC-002","Fertilizer and manure nutrient inputs","agriculture","source_stock","factual_2026","regional / watershed","","","schematic source stock","bge_ohio_h2ohio","moderate","Input source context; no basin total or farm-level attribution."],
 ["BGC-003","Soil organic matter and nutrient stocks","agriculture","soil_system","factual_2026","field / subwatershed","","","schematic system","bge_nrscs","limited","Soil stocks are represented conceptually; no sampled regional inventory is substituted."],
 ["BGC-004","Runoff and tile-drainage mobilization","water_agriculture","mobilization_interface","factual_2026","field / HUC12","","","schematic interface","bge_usgs_wbd","moderate","Runoff and drainage are transport mechanisms; no tile network or export rate is mapped."],
 ["BGC-005","Tributary network","water","tributary","factual_2026","HUC8 / river","","","regional network","bge_usgs_3dhp","high","Physical water-carrier context reused from accepted hydrology."],
 ["BGC-006","Maumee River at representative monitoring reach","water_monitoring","river_system","factual_2026","monitoring station / river","41.5000526","-83.7127145","representative station context","bge_ncwqr","moderate","Representative monitoring context; station observations are not basin-wide conditions."],
 ["BGC-007","Lower Maumee River to bay","water","river_system","factual_2026","river / receiving-water interface","","","regional interface","bge_usgs_3dhp","high","Directional river-to-bay carrier relationship; quantity is not inferred."],
 ["BGC-008","Western Lake Erie receiving system","water_ecology","receiving_water","factual_2026","western Lake Erie","","","regional receiving system","bge_epa_lake_erie","high","Receiving-water condition context; no new bloom model or footprint."],
 ["BGC-009","Maumee Bay and nearshore interface","water_ecology","receiving_water","factual_2026","nearshore / bay","","","regional interface","bge_epa_lake_erie","high","Nearshore receiving interface; nutrient delivery does not imply a specific local bloom."],
 ["BGC-010","Coastal and floodplain wetlands","ecology","wetland","factual_2026","wetland complex / HUC12","41.69","-83.22","generalized public anchor","bge_usfws_nwi","moderate","Inventory-supported wetland context; condition and uniform performance are unknown."],
 ["BGC-011","Riparian buffer and floodplain interface","ecology","riparian_system","factual_2026","reach / floodplain","","","schematic interface","bge_usgs_3dhp","moderate","Broad retention/transformation interface; no project boundary or removal rate."],
 ["BGC-012","Urban stormwater landscape","urban","urban_system","factual_2026","municipal / subwatershed","","","schematic landscape","bge_ohio_epa_npdes","moderate","Urban runoff source context; no parcel or outfall load assignment."],
 ["BGC-013","Wastewater treatment and permitted discharge","wastewater","wastewater_system","factual_2026","facility / receiving water","","","public regulatory context","bge_ohio_epa_npdes","high","Permitted discharge and treatment context; permit limit is not actual discharge."],
 ["BGC-014","Nutrient and water-quality monitoring network","monitoring","monitoring_system","factual_2026","station / basin network","","","public monitoring context","bge_ncwqr","moderate","Representative public monitoring context; not an exhaustive network inventory."],
 ["BGC-015","Sediment and particulate organic matter","material_transport","material_pool","factual_2026","river / nearshore","","","schematic material pool","bge_epa_lake_erie","limited","Sediment-associated transport is included where relevant; no sediment budget is estimated."],
 ["BGC-016","HAB and aquatic ecological interface","ecology","ecological_interface","factual_2026","western Lake Erie","","","regional condition interface","bge_noaa_hab","high","Nutrient/HAB relationship is a documented ecological context, not a new forecast."],
 ["BGC-017","Nutrient-management and restoration programs","management","management_control","factual_2026","regional / watershed","","","program interface","bge_ohio_h2ohio","moderate","Documented controls and targets; effectiveness is not assumed."],
 ["BGC-018","Phosphorus recovery / circular nutrient interface","management","management_control","factual_2026","facility / regional","","","future-facing management interface","bge_ohio_epa_npdes","limited","Potential management interface only; no operating regional recovery system asserted."],
]

EDGES = [
 ["BGE-001","BGC-002","BGC-001","P","mobilized_from","documented directional relationship","agricultural input enters soil/crop system","field / watershed","bge_ohio_h2ohio","moderate","unknown quantity","No input total or farm allocation."],
 ["BGE-002","BGC-001","BGC-004","P;N;C;organic_matter","mobilized_by","inferred system relationship","runoff and drainage can mobilize landscape materials","field / HUC12","bge_usgs_wbd","moderate","unknown quantity","Mechanism does not establish delivery in every event."],
 ["BGE-003","BGC-003","BGC-004","P;N;C","mobilized_by","inferred system relationship","soil stock interacts with water movement","field / HUC12","bge_nrscs","limited","unknown quantity","No soil-stock measurement is asserted."],
 ["BGE-004","BGC-004","BGC-005","P;N;C;sediment","transported_by","documented directional relationship","runoff/drainage enters tributary network","HUC12 / HUC8","bge_usgs_3dhp","moderate","unknown quantity","Physical water connection is reused; flux magnitude unknown."],
 ["BGE-005","BGC-005","BGC-006","P;N;sediment","monitored_by","documented monitoring relationship","tributary material is observed at representative reaches","station / river","bge_ncwqr","moderate","unknown quantity","Station data are not basin-wide."],
 ["BGE-006","BGC-005","BGC-007","P;N;sediment","transported_by","documented directional relationship","tributaries join Lower Maumee carrier","HUC8 / river","bge_usgs_3dhp","high","unknown quantity","Network relationship, not a measured load."],
 ["BGE-007","BGC-007","BGC-009","P;N;sediment;organic_matter","delivered_to","documented directional relationship","Lower Maumee discharges toward bay receiving interface","river / bay","bge_epa_lake_erie","high","unknown quantity","Delivery relationship does not imply retention-free transfer."],
 ["BGE-008","BGC-009","BGC-008","P;N;organic_matter","delivered_to","documented directional relationship","bay connects to western Lake Erie receiving system","bay / lake","bge_epa_lake_erie","high","unknown quantity","No exact plume or bloom footprint."],
 ["BGE-009","BGC-010","BGC-007","P;N;sediment","retained_or_transformed_by","inferred system relationship","wetland/floodplain can retain or transform materials before downstream delivery","wetland / river","bge_usfws_nwi","moderate","unknown quantity","Performance varies; no removal efficiency."],
 ["BGE-010","BGC-011","BGC-007","P;N;sediment","retained_or_transformed_by","inferred system relationship","riparian/floodplain interface can modify material movement","reach / river","bge_nrscs","moderate","unknown quantity","No buffer performance estimate."],
 ["BGE-011","BGC-012","BGC-005","P;N;organic_matter","transported_by","inferred system relationship","urban runoff can enter mapped tributaries","municipal / HUC8","bge_ohio_epa_npdes","moderate","unknown quantity","No outfall-specific load."],
 ["BGE-012","BGC-013","BGC-009","P;N;organic_matter","discharged_to","documented regulatory relationship","permitted wastewater systems discharge to receiving waters","facility / bay or river","bge_ohio_epa_npdes","high","unknown quantity","Permit status is not measured load."],
 ["BGE-013","BGC-014","BGC-005","P;N","monitored_by","documented monitoring relationship","monitoring network samples tributary conditions","station / HUC8","bge_ncwqr","moderate","unknown quantity","Coverage and timing vary."],
 ["BGE-014","BGC-014","BGC-008","P;N;HAB_context","monitored_by","documented monitoring relationship","lake monitoring and HAB programs observe receiving conditions","station/network / lake","bge_noaa_hab","high","unknown quantity","Observation is not causal attribution."],
 ["BGE-015","BGC-007","BGC-015","sediment;organic_matter","transported_by","inferred system relationship","river carrier transports particulate material","river / nearshore","bge_epa_lake_erie","limited","unknown quantity","No sediment budget."],
 ["BGE-016","BGC-015","BGC-009","P;N;organic_matter","delivered_to","inferred system relationship","particulate material can reach receiving interface","river / bay","bge_epa_lake_erie","limited","unknown quantity","Partitioning and settling are not quantified."],
 ["BGE-017","BGC-008","BGC-016","P;HAB_context","ecological_interface","documented condition relationship","western Lake Erie eutrophication/HAB condition relates to phosphorus context","lake","bge_epa_lake_erie","high","unknown quantity","No new bloom prediction."],
 ["BGE-018","BGC-017","BGC-001","P;N;soil_carbon","managed_by","documented program relationship","programs act on agricultural nutrient management and soil function","regional / watershed","bge_ohio_h2ohio","moderate","unknown quantity","Effectiveness remains evidence-qualified."],
 ["BGE-019","BGC-017","BGC-010","P;N;sediment","managed_by","documented program relationship","restoration programs can act on wetland/riparian retention","regional / wetland","bge_ohio_h2ohio","moderate","unknown quantity","No project performance claim."],
 ["BGE-020","BGC-017","BGC-013","P;N","managed_by","documented program relationship","regulatory/treatment programs act on point-source controls","facility / receiving water","bge_ohio_epa_npdes","moderate","unknown quantity","No compliance or outcome inference."],
 ["BGE-021","BGC-018","BGC-013","P;N","transformed_by","scenario-ready management interface","recovery could transform wastewater nutrient management","facility / regional","bge_ohio_epa_npdes","limited","unknown quantity","Not asserted as an operating 2026 system."],
 ["BGE-022","BGC-006","BGC-007","water_carrier","transported_by","documented directional relationship","representative river reach is part of downstream Maumee carrier","station / river","bge_usgs_3dhp","moderate","unknown quantity","Station location is not a basin boundary."],
 ["BGE-023","BGC-005","BGC-014","water_carrier","monitored_by","documented monitoring relationship","tributary network is sampled by public programs","HUC8 / station","bge_ncwqr","moderate","unknown quantity","Not exhaustive."],
 ["BGE-024","BGC-008","BGC-016","N;C;organic_matter","ecological_interface","inferred system relationship","receiving-water materials interact with aquatic ecological condition","lake","bge_noaa_hab","moderate","unknown quantity","No disease, exposure, toxicity, or bloom magnitude claim."],
]

QUANTS = [
 ["BGCQ-001","P","total phosphorus","Lake Erie target","western basin","annual load target","6000","metric tons per year","target framing","2026","EPA/ECCC target context","bge_epa_lake_erie","high","Target, not an observed 2026 load or achieved outcome."],
 ["BGCQ-002","P","total phosphorus","Maumee River watershed","western basin","drainage area","6568","square miles","EPA summary","2026","EPA watershed context","bge_epa_lake_erie","high","Watershed area, not a nutrient load."],
 ["BGCQ-003","P","total phosphorus","Maumee River watershed","western basin","cropland context","over 4 million","acres","EPA summary","2026","EPA watershed context","bge_epa_lake_erie","high","Cropland context across OH/MI/IN, not farm-level attribution."],
 ["BGCQ-004","HAB_context","cyanobacteria biomass","western Lake Erie","western basin","desired biomass threshold","9600","metric tons","EPA/NOAA target framing","2026","Severity-target context","bge_epa_lake_erie","high","Ecological target context, not a nutrient flux or future forecast."],
 ["BGCQ-005","HAB_context","Lake Erie Severity Index","western Lake Erie","western basin","2024 severity index","3.9","index units","NOAA/EPA reported series","2024","Remote sensing validated by field samples","bge_epa_lake_erie","high","Bloom indicator context, not a causal nutrient estimate."],
 ["BGCQ-006","P","total phosphorus","Maumee River watershed","Maumee watershed","trend statement","stable","qualitative","EPA assessment","as of 2021","Annual monitoring/model assessment","bge_epa_lake_erie","high","Qualitative trend; no missing years filled."],
 ["BGCQ-007","P","total phosphorus","Maumee River at Waterville","Maumee Bay mouth","spring loading capacity","914.4","metric tons per spring season","EPA TMDL FAQ","March 1–July 31","TMDL loading-capacity framing","bge_epa_mwn_tmdl_faqs","high","Planning/loading-capacity value, not an observed annual load or bloom guarantee."],
 ["BGCQ-008","P","total phosphorus","Maumee River at Waterville","Waterville reference point","spring target","860","metric tons per spring season","EPA TMDL FAQ","March 1–July 31","Target based on 2008 reference load","bge_epa_mwn_tmdl_faqs","high","Target, not observed load or achieved reduction."],
 ["BGCQ-009","P","total phosphorus","Maumee watershed TMDL boundary","western basin","spring wasteload allocation","107.8","metric tons per spring season","EPA/Ohio EPA TMDL tables","March 1–July 31","Regulatory planning allocation","bge_epa_mwn_tmdl_tables","high","Point-source planning allocation, not measured facility discharge."],
 ["BGCQ-010","P","total phosphorus","Maumee watershed TMDL boundary","western basin","spring nonpoint landscape allocation","547.0","metric tons per spring season","EPA/Ohio EPA TMDL tables","March 1–July 31","Regulatory planning allocation","bge_epa_mwn_tmdl_tables","high","Nonpoint allocation, not proof that all material is agricultural or an observed source load."],
]

DEP_COLS=["dependency_id","source_node_id","dependent_node_id","material_or_process","dependency_type","dependency_strength","evidence_quality","scale","source_id","confidence","quantity_status","notes"]
DEPENDENCIES=[]
for i,(a,b,mat,typ,strength,evid,scale,src,conf,note) in enumerate([
 ("BGC-002","BGC-004","P;N","source-to-mobilization","strong","moderate","field/HUC12","bge_ohio_h2ohio","moderate","Input presence does not quantify export."),
 ("BGC-004","BGC-005","P;N;sediment","hydrologic_transport","strong","moderate","HUC12/HUC8","bge_usgs_3dhp","moderate","Connectivity is physical context; event transport varies."),
 ("BGC-005","BGC-007","P;N","river_delivery","strong","high","river/bay","bge_usgs_3dhp","high","Directional connection, no load magnitude."),
 ("BGC-007","BGC-009","P;N","receiving_delivery","strong","high","river/bay","bge_epa_lake_erie","high","Delivery can be modified by settling and mixing."),
 ("BGC-009","BGC-008","P;N","lake_exchange","moderate","high","bay/lake","bge_epa_lake_erie","high","No plume or bloom footprint."),
 ("BGC-001","BGC-004","P;N;C","landscape_mobilization","strong","moderate","field/HUC12","bge_nass","moderate","Landscape context not management behavior."),
 ("BGC-010","BGC-007","P;N;sediment","wetland_retention","moderate","moderate","wetland/river","bge_usfws_nwi","moderate","Function varies; removal unknown."),
 ("BGC-011","BGC-007","P;N;sediment","riparian_transformation","moderate","moderate","reach/floodplain","bge_nrscs","moderate","No efficiency estimate."),
 ("BGC-012","BGC-005","P;N","urban_runoff","moderate","limited","municipal/HUC8","bge_ohio_epa_npdes","limited","No outfall load."),
 ("BGC-013","BGC-009","P;N","point_source_control","moderate","high","facility/receiving water","bge_ohio_epa_npdes","high","Permit is not actual discharge."),
 ("BGC-014","BGC-005","P;N","monitoring_coverage","moderate","moderate","station/HUC8","bge_ncwqr","moderate","Temporal/spatial coverage varies."),
 ("BGC-014","BGC-008","P;N;HAB","monitoring_coverage","moderate","high","station/lake","bge_noaa_hab","high","Monitoring does not create basin-wide estimate."),
 ("BGC-017","BGC-001","P;N","agricultural_control","moderate","moderate","regional/watershed","bge_ohio_h2ohio","moderate","Documented intervention, outcome not assumed."),
 ("BGC-017","BGC-010","P;N;sediment","restoration_control","limited","limited","wetland/watershed","bge_ohio_h2ohio","limited","Site-specific performance unknown."),
 ("BGC-017","BGC-013","P;N","wastewater_control","moderate","moderate","facility/receiving water","bge_ohio_epa_npdes","moderate","Treatment capacity and actual load distinct."),
 ("BGC-006","BGC-005","P;N","station_representativeness","limited","moderate","station/river","bge_ncwqr","moderate","One station is not the basin."),
 ("BGC-004","BGC-007","P;N;sediment","seasonal_event_transport","strong","moderate","HUC12/river","bge_epa_lake_erie","moderate","Spring/event dependence is important; no seasonal load fabricated."),
 ("BGC-003","BGC-015","C;organic_matter","soil_carbon_partitioning","limited","limited","field/river","bge_nrscs","limited","Bounded carbon context only."),
 ("BGC-015","BGC-009","sediment;organic_matter","particulate_delivery","moderate","limited","river/bay","bge_epa_lake_erie","limited","No sediment budget."),
 ("BGC-018","BGC-013","P;N","recovery_interface","limited","limited","facility/regional","bge_ohio_epa_npdes","limited","Potential control only."),
 ("BGC-008","BGC-016","P;HAB","ecological_response_interface","strong","high","lake","bge_epa_lake_erie","high","No bloom magnitude or toxicity forecast."),
 ("BGC-005","BGC-010","water","wetland_connectivity","moderate","high","river/wetland","bge_usgs_3dhp","moderate","Physical connection does not ensure retention."),
],1): DEPENDENCIES.append([f"BGD-{i:03d}",a,b,mat,typ,strength,evid,scale,src,conf,"unknown",note])

CONTROLS = [
 ["BGC-CTL-001","nutrient_management","Agricultural nutrient-management planning and practice programs","BGC-001;BGC-002","Documented state/federal program context; practice adoption and outcome vary","bge_ohio_h2ohio","moderate","No farm-level behavior or achieved load reduction asserted."],
 ["BGC-CTL-002","fertilizer_management","Timing, rate, placement, and source management","BGC-002;BGC-004","Practice framework supports mobilization control; regional performance is not uniform","bge_nrscs","moderate","No export coefficient assigned."],
 ["BGC-CTL-003","wetland_restoration","Wetland restoration and water-storage interfaces","BGC-010;BGC-007","Can provide retention/transformation context where connected","bge_ohio_h2ohio","moderate","No universal removal efficiency."],
 ["BGC-CTL-004","riparian_buffer","Riparian and edge-of-field conservation interfaces","BGC-011;BGC-004","Can intercept or transform materials under appropriate conditions","bge_nrscs","moderate","Site conditions and maintenance matter."],
 ["BGC-CTL-005","wastewater_treatment","Permitted wastewater treatment and discharge controls","BGC-013;BGC-009","Regulatory control applies to point-source context","bge_ohio_epa_npdes","high","Permit limit is not measured discharge."],
 ["BGC-CTL-006","stormwater_control","Urban stormwater management","BGC-012;BGC-005","Public control interface for runoff pathways","bge_ohio_epa_npdes","moderate","No outfall inventory or load."],
 ["BGC-CTL-007","drainage_management","Drainage and water-retention management","BGC-004;BGC-005","Hydrologic timing and connectivity can be managed in some settings","bge_ohio_h2ohio","limited","No tile-network geometry or effectiveness claim."],
 ["BGC-CTL-008","monitoring","Tributary, lake, and HAB monitoring","BGC-014;BGC-006","Supports observation and adaptive management","bge_ncwqr","moderate","Coverage and timeliness remain uneven."],
 ["BGC-CTL-009","regulatory_target","Lake Erie nutrient-reduction targets and Maumee TMDL","BGC-008;BGC-017","Official targets and planning allocations establish management direction","bge_epa_mwn_tmdl","high","Targets are not observed reductions."],
 ["BGC-CTL-010","nutrient_recovery","Potential phosphorus recovery/circular nutrient interface","BGC-018;BGC-013","Conceptual management interface for future scenario layer","bge_ohio_epa_npdes","limited","Not asserted as a regional 2026 operating system."],
]
CONTROL_COLS=["control_id","control_type","control_name","acts_on","evidence_support","source_id","confidence","uncertainty"]
MATRIX_COLS=["system_interface","source_strength","transport_connectivity","hydrologic_dependence","seasonality","retention_capacity","management_control","monitoring_strength","spatial_certainty","temporal_certainty","flux_quantification","notes"]
MATRIX=[
 ["agricultural landscape → tributary","strong","strong","strong","strong","limited","moderate","moderate","moderate","moderate","limited","Landscape and event pathways are important; quantities remain incomplete."],
 ["tributary → Lower Maumee","moderate","strong","strong","strong","limited","limited","moderate","strong","moderate","limited","Physical carrier is clear; flux partitioning is not."],
 ["Lower Maumee → western Lake Erie","moderate","strong","strong","strong","limited","moderate","moderate","strong","moderate","moderate","Receiving delivery is documented; annual variability is large."],
 ["wetland/floodplain retention","limited","moderate","strong","moderate","unknown","moderate","limited","limited","limited","unknown","Function is supported but performance is site-specific."],
 ["wastewater → receiving water","moderate","moderate","moderate","limited","limited","strong","moderate","moderate","moderate","limited","Permit and treatment controls exist; actual loads require data."],
 ["urban stormwater → tributary","moderate","moderate","strong","strong","limited","moderate","limited","limited","limited","unknown","No exhaustive outfall/load model."],
 ["monitoring → decision","moderate","moderate","strong","strong","not_applicable","moderate","moderate","moderate","moderate","limited","Observation supports control but does not fill all gaps."],
 ["sediment/organic matter transport","limited","moderate","strong","strong","unknown","limited","limited","limited","limited","unknown","Bounded interface; no regional sediment budget."],
]

SCENARIO_ASSUMPTIONS=[]
SCENARIOS={"A":"Regenerative / Retentive Basin","B":"Productive Managed Basin","C":"High-Flux / Compound-Stress Basin"}
for s,name in SCENARIOS.items():
 for y in (2050,2075):
  for i,(theme,basis,unc) in enumerate([
   ("Landscape retention and soil-function investment changes material mobilization.","qualitative scenario driver","moderate"),
   ("Hydrologic variability changes the timing and connectivity of transport.","external climate/landscape driver","high"),
   ("Wetland, riparian, and drainage controls change retention and transformation interfaces.","management trajectory","moderate"),
   ("Wastewater and urban controls change point-source and stormwater interfaces.","infrastructure trajectory","moderate"),
   ("Monitoring and adaptive governance change the ability to observe and manage fluxes.","governance trajectory","moderate"),
   ("Ecological consequences remain condition interfaces, not deterministic HAB outcomes.","scientific boundary","high"),
  ],1):
   SCENARIO_ASSUMPTIONS.append([f"BGSA-{s}{y}-{i:02d}",s,y,"cross_system",theme,basis,"qualitative", "bge_noaa_climate" if i==2 else "bge_epa_lake_erie", "moderate" if s=="B" else "limited",unc,"scenario","No probability or exact future flux is assigned."])
SCN_ASS_COLS=["assumption_id","scenario_id","scenario_year","scope","assumption","basis","value_type","source_id","plausibility","uncertainty","status","notes"]
BASE_COMPS=["BGC-001","BGC-004","BGC-005","BGC-007","BGC-008","BGC-010","BGC-013","BGC-014"]
SCN_NODES=[]; SCN_EDGES=[]; SCN_CONTROLS=[]; SCN_UNC=[]
state_map={"A": ["retention_strengthened","mobilization_reduced","transport_managed","delivery_reduced_or_buffered","condition_improved_but_variable","wetland_function_strengthened","treatment_upgraded","monitoring_expanded"],"B":["production_persists","mobilization_managed","transport_persists","delivery_persists_managed","condition_persists_variable","targeted_retention","selective_treatment_upgrade","monitoring_expanded"],"C":["mobilization_increased_episodically","transport_more_variable","transport_intensified","delivery_persists_highly_variable","condition_stress_increased","retention_weakened_in_some_systems","control_burden_increased","monitoring_burden_increased"]}
for s in SCENARIOS:
 for y in (2050,2075):
  sid=f"{s}{y}"
  for j,base in enumerate(BASE_COMPS,1):
   SCN_NODES.append([sid,y,f"SCN-{sid}-{j:02d}",base,"biogeochemical_component",state_map[s][j-1],"fictional","scenario_assumption",f"BGSA-{s}{y}-{((j-1)%6)+1:02d}","bge_epa_lake_erie","moderate" if s=="B" else "limited","Qualitative future state; no numeric load, concentration, or HAB magnitude."])
  for j in range(1,8):
   SCN_EDGES.append([sid,y,f"BGS-E-{sid}-{j:02d}",f"SCN-{sid}-{j:02d}",f"SCN-{sid}-{j+1:02d}","material_or_control_interface","qualitative_change", "fictional","scenario_assumption",f"BGSA-{s}{y}-{((j-1)%6)+1:02d}","bge_epa_lake_erie","No exact future transport or effect size."])
  for j,base in enumerate(BASE_COMPS,1):
   SCN_CONTROLS.append([sid,y,f"BGS-C-{sid}-{j:02d}",base,"control_or_retention_state",("strengthened" if s=="A" else "selective" if s=="B" else "burden_increased"),"fictional",f"BGSA-{s}{y}-{((j-1)%6)+1:02d}","bge_ohio_h2ohio","Qualitative control state; effectiveness not quantified."])
   SCN_UNC.append([sid,y,f"BGS-U-{sid}-{j:02d}",base,"uncertainty_state",("moderate" if s=="A" else "moderate" if s=="B" else "high"),"scenario","bge_noaa_climate","Uncertainty is not low risk or absence."])
SCN_NODE_COLS=["scenario_id","scenario_year","object_id","baseline_object_id","component","future_state","reality_status","relationship_basis","assumption_id","source_id","plausibility","notes"]
SCN_EDGE_COLS=["scenario_id","scenario_year","edge_id","from_object_id","to_object_id","interface_type","change_type","reality_status","relationship_basis","assumption_id","source_id","notes"]
SCN_CTRL_COLS=["scenario_id","scenario_year","control_state_id","baseline_object_id","control_domain","future_state","reality_status","assumption_id","source_id","notes"]
SCN_UNC_COLS=["scenario_id","scenario_year","uncertainty_id","baseline_object_id","uncertainty_domain","level","status","source_id","notes"]
COMP_COLS=["scenario_id","scenario_year","retention","mobilization","transport_variability","delivery","management","monitoring","ecological_interface","worldbuilding_read"]
COMP=[]
for s in SCENARIOS:
 for y in (2050,2075):
  COMP.append([f"{s}{y}",y,"strengthened" if s=="A" else "targeted" if s=="B" else "weakened_in_some_systems","reduced" if s=="A" else "managed" if s=="B" else "increased_episodically","managed" if s=="A" else "persistent" if s=="B" else "more_variable","reduced_or_buffered" if s=="A" else "persists_managed" if s=="B" else "persists_highly_variable","adaptive_and_integrated" if s=="A" else "selective_and_technical" if s=="B" else "burdened_and_constrained","expanded" if s in ("A","B") else "burden_increased","improved_but_not_eliminated" if s=="A" else "persistent_managed" if s=="B" else "stress_increased_uncertain","Nutrients become visible regional infrastructure; no future bloom forecast."])

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(df,path): path.parent.mkdir(parents=True,exist_ok=True); df.to_csv(path,index=False)
def load_layers():
 huc=gpd.read_file(GPKG,layer="water_watersheds_huc8"); lake=gpd.read_file(GPKG,layer="water_lake_erie"); wet=gpd.read_file(GPKG,layer="water_current_wetlands_25ac"); flow=gpd.read_file(GPKG,layer="hydrography_physical"); flow["geometry"]=flow.geometry.simplify(0.002,preserve_topology=False); return huc,lake,wet,flow
def render_map(number,title,subtitle,path,scenario=False):
 huc,lake,wet,flow=load_layers(); fig=plt.figure(figsize=(16,10),facecolor="#f1eadc"); ax=fig.add_axes([.04,.12,.59,.78],facecolor="#e9e1ce"); huc.boundary.plot(ax=ax,color="#9f967f",linewidth=.45,alpha=.65); lake.plot(ax=ax,color="#a9d7df",edgecolor="#478c9a",linewidth=.8,alpha=.9); wet.plot(ax=ax,color="#6da77c",edgecolor="none",alpha=.42); flow.plot(ax=ax,color="#4a8798",linewidth=.3,alpha=.55)
 if scenario:
  cols={"A":"#4f927b","B":"#c08a42","C":"#a8524d"}; xs=[-83.95,-83.35,-82.95]
  for s,x in zip(("A","B","C"),xs): ax.scatter([x],[41.35],s=260,c=cols[s],marker="o",alpha=.8,edgecolor="#f1eadc",linewidth=1.2,zorder=5); ax.text(x,41.35, s,ha="center",va="center",color="white",weight="bold",zorder=6)
  ax.text(-83.45,41.62,"A / B / C qualitative pathways",ha="center",fontsize=10,color="#17384b")
 else:
  pts=[(-84.0,41.55),(-83.65,41.48),(-83.25,41.62),(-83.05,41.55),(-83.35,41.85)]; labels=["Agriculture / soils","Tributaries","Maumee carrier","Western Lake Erie","Wetland / riparian"]
  for (x,y),lab in zip(pts,labels): ax.scatter([x],[y],s=75,c="#a95d3a",marker="o",edgecolor="#f1eadc",linewidth=1,zorder=5); ax.text(x,y+.035,lab,fontsize=7.5,ha="center",color="#713c2d")
  for (x1,y1),(x2,y2) in zip(pts[:4],pts[1:4]): ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=12,color="#9b573c",linewidth=1.4,alpha=.8))
  ax.add_patch(FancyArrowPatch(pts[4],pts[2],arrowstyle="-|>",mutation_scale=12,color="#4f927b",linewidth=1.4,alpha=.8))
 ax.set_xlim(-84.55,-82.55); ax.set_ylim(40.9,42.15); ax.set_axis_off(); side=fig.add_axes([.67,.06,.3,.86]); side.axis("off"); side.text(.03,.97,f"MAP {number} — {title}",va="top",fontsize=14,weight="bold",color="#17384b"); side.text(.03,.86,subtitle,va="top",fontsize=8.6,color="#3f4645",linespacing=1.35)
 side.text(.03,.71,"SYSTEM LENS",fontsize=10,weight="bold",color="#17384b"); bullets=( ["Agricultural sources and soil stocks mobilize through runoff and drainage","Tributaries and the Maumee act as water carriers","Wetlands and riparian systems may retain or transform materials","Wastewater and urban systems are distinct point/runoff interfaces","Monitoring observes selected stations and receiving conditions","Quantities are separated from directional relationships"] if not scenario else ["A — retention, soil function, restoration, and adaptive monitoring strengthen","B — productive working landscape with targeted management and persistent export","C — episodic mobilization and uncertainty increase management burden","All futures remain qualitative scenario deltas, not forecasts","No future load, concentration, crop yield, removal rate, or HAB magnitude"] )
 y=.675
 for b in bullets: side.text(.05,y,"• "+b,fontsize=8.1,color="#3f4645",va="top"); y-=.052
 side.text(.03,.23,"BOUNDARIES",fontsize=10,weight="bold",color="#17384b"); side.text(.03,.20,"Nutrient loading is not bloom magnitude, exposure, or toxicity. No farm-level attribution, exact route, uniform wetland efficiency, predictive HAB model, future probability, or deterministic ecosystem collapse is represented. Great Black Swamp remains C — HOLD / noncanonical.",fontsize=7.5,color="#3f4645",va="top",linespacing=1.3)
 fig.savefig(path.with_suffix(".png"),dpi=220,bbox_inches="tight",facecolor=fig.get_facecolor()); svg=path.with_suffix(".svg"); fig.savefig(svg,bbox_inches="tight",facecolor=fig.get_facecolor(),metadata={"Date":None}); plt.close(fig); svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
def report(name,text): (REPORTS/name).write_text(text.replace("\\n","\n"),encoding="utf-8")
def main():
 NETWORKS.mkdir(parents=True,exist_ok=True); ANALYSIS.mkdir(parents=True,exist_ok=True); SCEN_DIR.mkdir(parents=True,exist_ok=True); MAPS.mkdir(parents=True,exist_ok=True); FIGURES.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
 paths=[]
 source_path=NETWORKS/"biogeochemical_system_sources.csv"; write(pd.DataFrame(SRC,columns=["source_id","title","url","use","source_type"]),source_path); paths.append(source_path)
 node_path=NETWORKS/"biogeochemical_system_nodes.csv"; edge_path=NETWORKS/"biogeochemical_flux_edges.csv"; q_path=ANALYSIS/"biogeochemical_quantitative_fluxes.csv"; map26=MAPS/"26_biogeochemical_nutrient_flux_system_2026"; node_df=pd.DataFrame(NODES,columns=NODE_COLS); node_df["reality_status"]="real"; node_df["canon_status"]="verified"; edge_df=pd.DataFrame(EDGES,columns=EDGE_COLS); edge_df["reality_status"]="real"; edge_df["canon_status"]=edge_df["relationship_basis"].map(lambda x: "verified" if "documented" in x else "inferred"); write(node_df,node_path); write(edge_df,edge_path); write(pd.DataFrame(QUANTS,columns=Q_COLS),q_path); render_map("26","BIOGEOCHEMICAL & NUTRIENT FLUX SYSTEM, 2026","A bounded factual network of source stocks, mobilization, transport, retention, delivery, ecological interfaces, and controls. Quantitative records are not combined into a single load estimate.",map26); paths += [node_path,edge_path,q_path,map26.with_suffix('.png'),map26.with_suffix('.svg')]
 dep_path=NETWORKS/"biogeochemical_dependency_edges.csv"; ctrl_path=ANALYSIS/"biogeochemical_control_register.csv"; mat_path=ANALYSIS/"biogeochemical_dependency_matrix.csv"; map27=MAPS/"27_biogeochemical_dependencies_controls_2026"; write(pd.DataFrame(DEPENDENCIES,columns=DEP_COLS),dep_path); write(pd.DataFrame(CONTROLS,columns=CONTROL_COLS),ctrl_path); write(pd.DataFrame(MATRIX,columns=MATRIX_COLS),mat_path); render_map("27","BIOGEOCHEMICAL DEPENDENCIES & CONTROLS, 2026","Qualitative dependencies, controls, bottlenecks, and monitoring interfaces over the Phase 8A working baseline. Strong does not mean quantified; unknown does not mean low.",map27); paths += [dep_path,ctrl_path,mat_path,map27.with_suffix('.png'),map27.with_suffix('.svg')]
 ass_path=SCEN_DIR/"biogeochemical_scenario_assumptions.csv"; sn_path=SCEN_DIR/"biogeochemical_nodes_scenario.csv"; se_path=SCEN_DIR/"biogeochemical_edges_scenario.csv"; sc_path=SCEN_DIR/"biogeochemical_controls_scenario.csv"; su_path=SCEN_DIR/"biogeochemical_uncertainty_scenario.csv"; comp_path=FIGURES/"biogeochemical_scenarios_comparison.csv"; map28=MAPS/"28_biogeochemical_futures_2050"; map28b=MAPS/"28b_biogeochemical_futures_2075"; write(pd.DataFrame(SCENARIO_ASSUMPTIONS,columns=SCN_ASS_COLS),ass_path); write(pd.DataFrame(SCN_NODES,columns=SCN_NODE_COLS),sn_path); write(pd.DataFrame(SCN_EDGES,columns=SCN_EDGE_COLS),se_path); write(pd.DataFrame(SCN_CONTROLS,columns=SCN_CTRL_COLS),sc_path); write(pd.DataFrame(SCN_UNC,columns=SCN_UNC_COLS),su_path); write(pd.DataFrame(COMP,columns=COMP_COLS),comp_path); render_map("28","BIOGEOCHEMICAL FUTURES, 2050","Three qualitative alternatives diverge from the factual 2026 nutrient-flux baseline.",map28,True); render_map("28b","BIOGEOCHEMICAL FUTURES, 2075","Three qualitative alternatives diverge from the factual 2026 nutrient-flux baseline.",map28b,True); paths += [ass_path,sn_path,se_path,sc_path,su_path,comp_path,map28.with_suffix('.png'),map28.with_suffix('.svg'),map28b.with_suffix('.png'),map28b.with_suffix('.svg')]
 manifest={"phase":"8A-8C","status":"implemented_validated_pending_sol_acceptance","counts":{"baseline_nodes":len(NODES),"baseline_edges":len(EDGES),"quantitative_records":len(QUANTS),"dependencies":len(DEPENDENCIES),"controls":len(CONTROLS),"matrix_rows":len(MATRIX),"scenario_assumptions":len(SCENARIO_ASSUMPTIONS),"scenario_nodes":len(SCN_NODES),"scenario_edges":len(SCN_EDGES),"scenario_controls":len(SCN_CONTROLS),"scenario_uncertainty":len(SCN_UNC),"comparison_rows":len(COMP)},"artifacts":{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}}
 (REPORTS/"biogeochemical_module_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 report("biogeochemical_sources.md","""# Biogeochemical & Nutrient Flux Sources\n\nThe Phase 8 module uses the machine-readable registry at `data/processed/networks/biogeochemical_system_sources.csv`. US EPA Lake Erie data document annual phosphorus-load tracking, western-basin eutrophic context, Maumee importance, and target/status distinctions. EPA's Maumee Watershed Nutrient TMDL approval documents a planning framework allocating western-basin phosphorus between point and nonpoint sources. USGS hydrography/WBD, NWI, NCWQR, USDA, Ohio EPA, H2Ohio, GLRI Annex 4, and NOAA provide bounded system and management context.\n\nNo source is used to infer farm-level behavior, a continuous nutrient route, a basin-wide station measurement, a uniform wetland removal rate, or a future nutrient load.\n\n## Key URLs\n\n- https://www.epa.gov/glwqa/lake-erie-water-quality-data\n- https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load\n- https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/\n- https://ncwqr.org/\n- https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer\n- https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/FeatureServer\n- https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer\n""")
 report("biogeochemical_assumptions.md","""# Biogeochemical Module Assumptions\n\nThe baseline models a compact network rather than an exhaustive geochemical inventory. Water is a carrier reused from accepted hydrology. Agriculture is represented as landscape and source-stock context; private farms and management behavior are not identified. Wetlands and riparian systems are represented as possible retention/transformation interfaces without universal performance values. Wastewater is represented through public regulatory and treatment context; permitted discharge is not actual discharge. Carbon is bounded to soil organic matter, aquatic organic matter, and sediment-associated material; this is not a greenhouse-gas inventory.\n\nQuantitative records retain incompatible metrics separately and include targets/indicators only where the source directly supports them.\n""")
 report("biogeochemical_findings.md","""# Biogeochemical & Nutrient Flux Findings\n\n## Baseline\n\nThe strongest documented structure is agricultural landscape → runoff/drainage → tributary network → Lower Maumee → Maumee Bay/western Lake Erie. This is a directional system relationship, not a claim that every source reaches the lake. Phosphorus is the clearest load/HAB interface in current public reporting. Nitrogen is included as a co-transported nutrient whose magnitude and pathways vary by source, season, and hydrologic connection. Carbon and organic matter remain bounded, primarily as soil, aquatic, wetland, and sediment-associated context rather than a regional carbon budget.\n\nWetlands and riparian/floodplain areas are plausible retention/transformation interfaces, but inventory presence does not establish condition or removal performance. Wastewater treatment and NPDES permitting are distinct point-source control interfaces; permit limits are not actual loads. Monitoring is spatially and temporally incomplete, so station measurements are not basin-wide conditions.\n\n## Scientific boundary\n\nEPA/NOAA nutrient and HAB materials support a nutrient-to-ecological-condition relationship, but this module creates no predictive HAB model. Nutrient loading is not bloom magnitude, exposure, toxicity, or health outcome.\n""")
 report("biogeochemical_dependency_findings.md","""# Biogeochemical Dependencies, Controls & Bottlenecks\n\nThe principal dependencies are hydrologic connectivity, event/seasonal transport, source mobilization, receiving-water delivery, and observation coverage. Retention and transformation by wetlands, riparian areas, floodplains, and sediment processes are important but poorly quantified at the project scale. Point-source controls are more institutionally explicit than diffuse agricultural and stormwater controls, but actual outcomes still require measured loads and appropriate temporal coverage.\n\nOfficial phosphorus-reduction targets are represented as targets, not observed reductions or forecasts. The dependency matrix uses qualitative labels only; unknown is preserved as unknown.\n""")
 report("biogeochemical_future_worldbuilding.md","""# Biogeochemical Futures — Worldbuilding Implications\n\nThese are speculative interpretations, separate from scientific claims:\n\n- Nutrients become infrastructure: drainage, treatment, wetlands, soils, and sensors are managed as a basin metabolism.\n- Phosphorus recovery and circular fertilizer systems create new strategic material and governance interfaces.\n- Wetlands become treatment landscapes whose public value is negotiated season by season.\n- Agricultural drainage becomes visible regional infrastructure rather than background property detail.\n- Sensor-driven watershed management ties public trust to seasonal water conditions and the legibility of responsibility.\n- Conflicts emerge over who bears responsibility for a material that moves across farms, jurisdictions, tributaries, and the lake.\n\nA/B/C states are qualitative alternatives, not predictions.\n""")
 print(json.dumps(manifest["counts"],indent=2))
if __name__ == "__main__": main()
