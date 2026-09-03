"""Build Phase 9B qualitative climate/hazard dependencies and resilience."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
NETWORKS=ROOT/"data/processed/networks"; ANALYSIS=ROOT/"data/processed/analysis"; MAPS=ROOT/"outputs/maps/systems"; REPORTS=ROOT/"reports"; GPKG=ROOT/"data/processed/glasspunk_base.gpkg"
DEP=NETWORKS/"climate_hazard_dependency_edges.csv"; REG=ANALYSIS/"climate_hazard_dependency_register.csv"; CMP=ANALYSIS/"climate_compound_event_register.csv"; CTRL_PATH=ANALYSIS/"climate_resilience_control_register.csv"; MAT=ANALYSIS/"climate_hazard_dependency_matrix.csv"; MAP=MAPS/"30_climate_hazard_dependencies_resilience_2026"; MAN=REPORTS/"climate_dependency_manifest.json"

SOURCE_COLUMNS=["source_id","title","url","product_or_endpoint","source_type","evidence_role","spatial_scope","temporal_scope","use_limitations"]
SOURCE_ROWS=[
 ["d9_nca_midwest","Fifth National Climate Assessment Midwest chapter","https://doi.org/10.7930/NCA5.2023.CH24","Regional climate hazards, infrastructure, agriculture, and ecological context","federal_assessment","dependency and future context","Midwest / Great Lakes","historical and projected","Regional assessment; not a local damage, outage, or health model."],
 ["d9_nca_energy","Fifth National Climate Assessment energy chapter","https://doi.org/10.7930/NCA5.2023.CH5","Heat, cooling demand, and energy-system context","federal_assessment","thermal and energy dependency","United States / Midwest","historical and projected","Supports direction and mechanism; no local outage probability."],
 ["d9_epa_great_lakes","EPA Great Lakes climate indicators","https://www.epa.gov/climate-indicators/great-lakes","Observed lake levels/temperature and variability context","federal_indicators","lake-level and freight context","Great Lakes","1860-present observations","Observed indicators and synthesis; not a shoreline or damage model."],
 ["d9_noaa_seiche","NOAA seiche explanation","https://oceanservice.noaa.gov/facts/seiche.html","Seiche and wind-driven standing-wave mechanism","federal_science","coastal compound mechanism","Great Lakes and enclosed waters","process context","Mechanism source; no local recurrence estimate."],
 ["d9_glerl_ice","NOAA GLERL Great Lakes ice cover","https://www.glerl.noaa.gov/data/ice","Ice-cover observations and archive context","federal_dataset","winter/coastal context","Great Lakes","1973-present","Lake-wide ice cover does not establish local shoreline ice shove or harbor conditions."],
 ["d9_noaa_llv","NOAA Office for Coastal Management Lake Level Viewer","https://coast.noaa.gov/llv","Screening-level lake-level inundation context","federal_tool","coastal control/context","Great Lakes shoreline","historical and scenario viewer","Calm-day mapped extent excludes wind-driven waves and seiche; not a local damage model."],
 ["d9_noaa_inundation","NOAA CO-OPS inundation database","https://tidesandcurrents.noaa.gov/inundationdb/inundation.html?id=9063085","Station-specific coastal-inundation context","federal_tool","registry-only coastal context","Toledo station / shoreline","station product","Registry-only context; not adopted as a new inundation footprint or claim-row source in this qualitative layer."],
 ["d9_nws_gl_obs","NWS Great Lakes observations","https://www.weather.gov/greatlakes/globs","Lake wind, wave, and observation service context","federal_service","monitoring dependency","Great Lakes / station network","current and archived observations","Observation access does not imply complete shoreline coverage."],
 ["d9_nws_cle_winter","NWS Cleveland winter forecasts","https://www.weather.gov/cle/winter","Snow, ice, and winter forecast products","federal_service","warning and seasonal dependency","NWS forecast area","current operational products","Forecast products are not historical climatology or infrastructure-loss estimates."],
 ["d9_pnas_hab","Western Lake Erie agricultural and meteorological HAB study","https://www.pnas.org/doi/10.1073/pnas.1216006110","Documented nutrient/meteorological/ecological compound mechanism","peer_reviewed","precipitation-nutrient compound mechanism","Western Lake Erie","2011 event and future-consistency analysis","Mechanism evidence; no future bloom magnitude or health outcome."],
 ["d9_fema_nfhl","FEMA National Flood Hazard Layer","https://www.fema.gov/flood-maps/national-flood-hazard-layer","Regulatory flood-hazard mapping context","federal_web","registry-only flood-planning context","floodplain / mapped community","current product context","Registry-only parallel source; Phase 9A b9_fema_nfhl is the claim-row source. Regulatory zones remain distinct from observed flood footprints."],
 ["bge_ohio_epa_npdes","Ohio EPA NPDES program","https://epa.ohio.gov/divisions-and-offices/surface-water/permitting","Permitted discharge and treatment regulatory context","state_regulatory","stormwater and treatment planning context","Ohio / permitted discharges","current program context","Permits are not actual loads or evidence of local control performance."],
 ["bge_usfws_nwi","USFWS National Wetlands Inventory","https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer","Wetland inventory and broad retention/transformation interface","federal_dataset","wetland and floodplain context","Western Basin / wetland inventory","current inventory context","Inventory presence does not establish condition or a uniform removal rate."],
 ["bge_ohio_h2ohio","Ohio H2Ohio program","https://h2.ohio.gov/","Nutrient-management, wetlands, and water-quality intervention context","state_program","management pathway context","Ohio / Maumee context","current program context","Program context does not establish farm-level adoption or achieved reduction."],
]

DEP_BASE_COLUMNS=["dependency_id","hazard_node_id","affected_system","system_interface","dependency_type","dependency_strength","mechanism","monitoring_strength","warning_capacity","spatial_certainty","temporal_certainty","source_id","confidence","notes"]
DEP_COLUMNS=["dependency_id","hazard_node_id","affected_system","system_interface","dependency_type","dependency_strength","mechanism","relationship_basis","monitoring_strength","warning_capacity","spatial_certainty","temporal_certainty","source_id","confidence","notes"]
D=[]
def add(i,h,system,interface,typ,strength,mechanism,monitor,warning,spatial,temp,source,conf,note): D.append([f"HZD-{i:03d}",h,system,interface,typ,strength,mechanism,monitor,warning,spatial,temp,source,conf,note])
add(1,"HZ-001","energy","heat → cooling demand","thermal_dependency","strong","Hot conditions can increase cooling demand and thermal stress on infrastructure.","moderate","strong","limited","moderate","d9_nca_energy","moderate","No local demand or outage probability.")
add(2,"HZ-001","information_sensors","heat → forecast/warning","monitoring_dependency","moderate","Temperature observations and forecasts support warning decisions.","moderate","strong","moderate","moderate","b9_nws_points","moderate","Warning capacity is not hazard absence.")
add(3,"HZ-001","exposure_context","heat → receptor context","thermal_dependency","moderate","Developed-system and receptor interfaces coincide with heat conditions.","limited","moderate","limited","moderate","d9_nca_midwest","limited","No individual exposure or health outcome.")
add(4,"HZ-004","water","heavy precipitation → runoff","hydrologic_dependency","strong","Precipitation can enter drainage and tributary pathways.","moderate","strong","moderate","strong","b9_usgs_dv","moderate","USGS supports one river observation; the precipitation-to-runoff relationship is not quantified basin-wide.")
add(5,"HZ-004","biogeochemical","runoff → nutrient mobilization","water_quality_dependency","strong","Runoff and event connectivity can mobilize nutrients and sediment.","moderate","moderate","moderate","strong","d9_pnas_hab","moderate","No future load or bloom magnitude.")
add(6,"HZ-008","water","stormwater → receiving system","infrastructure_dependency","moderate","Urban drainage burden can connect intense rain to receiving waters.","limited","moderate","limited","moderate","d9_nca_midwest","limited","No outfall inventory or overflow count.")
add(7,"HZ-006","freight","flood → access","transport_dependency","moderate","Flooded crossings, roads, and interfaces can disrupt access.","limited","moderate","limited","moderate","d9_nca_midwest","limited","No route-level disruption probability.")
add(8,"HZ-006","water","high-flow observation → generalized source-water/treatment context","hydrologic_dependency","unknown","No direct treatment or intake operating relationship is established by the gauge record.","moderate","moderate","limited","unknown","b9_usgs_dv","unknown","USGS daily flow supports one gauge observation only; no treatment or intake operating evidence is included.")
add(9,"HZ-009","agriculture","drought → soil/crop water context","agricultural_dependency","moderate","Drought assessment and soil-water stress can affect agricultural operations.","moderate","limited","moderate","strong","b9_usdm_area","moderate","No yield or farm-level stress estimate.")
add(10,"HZ-009","ecology","drought → ecological water context","ecological_dependency","moderate","Low-water conditions can alter aquatic, wetland, and riparian context.","limited","limited","limited","moderate","d9_nca_midwest","limited","No population, abundance, or biodiversity score.")
add(11,"HZ-010","water","low flow → receiving system","hydrologic_dependency","moderate","One-gauge low-flow observation provides generalized receiving-water context; basin-wide dilution or transport effects are not established.","strong","limited","moderate","strong","b9_usgs_dv","moderate","One gauge does not describe the entire watershed.")
add(12,"HZ-012","freight","lake level → navigation/access","transport_dependency","moderate","Lake-level variability can affect draft, dock access, and navigation context as a system inference.","moderate","moderate","moderate","moderate","d9_epa_great_lakes","limited","EPA supports observed lake-level variability, not navigation operations; no cargo-loss or route probability.")
add(13,"HZ-013","coastal","lake-level screening → generalized shoreline context","coastal_dependency","moderate","NOAA Lake Level Viewer supplies calm-day lake-level screening context for generalized shoreline planning; wind-driven waves and seiche are excluded.","limited","moderate","limited","moderate","d9_noaa_llv","moderate","Not direct evidence of port burden, wind/wave effects, local inundation, or damage.")
add(14,"HZ-014","freight","wind setup/seiche → shoreline","coastal_dependency","moderate","Wind-driven lake-level displacement can interact with high background levels as a physical inference.","moderate","moderate","limited","moderate","d9_noaa_seiche","limited","NOAA supports the seiche mechanism; no local shoreline effect, joint probability, or amplitude recurrence is established.")
add(15,"HZ-015","ecology","lake-wide ice-cover monitoring → local coastal ecology context","seasonal_dependency","unknown","No local coastal ecological effect is established by lake-wide ice observations.","limited","limited","limited","unknown","d9_glerl_ice","unknown","Lake-wide ice cover is regional seasonal context; local shoreline ice, wave, and ecological effects remain unknown.")
add(16,"HZ-016","energy","severe storm → power interface","energy_dependency","moderate","Convective wind and lightning can coincide with power-system disruption.","moderate","strong","limited","moderate","d9_nca_energy","moderate","No outage probability or restoration estimate.")
add(17,"HZ-016","information_sensors","severe storm → communications","monitoring_dependency","moderate","Storm conditions can burden warning, sensor, and communication continuity.","limited","strong","limited","moderate","d9_nca_midwest","limited","No cyber or communications-failure model.")
add(18,"HZ-018","freight","winter forecast → transport planning/maintenance input","seasonal_dependency","moderate","Winter forecasts can inform transport planning and maintenance as a physical inference.","moderate","strong","moderate","strong","d9_nws_cle_winter","limited","NWS products support winter hazard and forecast context, not road closures, freight delays, or their probabilities.")
add(19,"HZ-018","water","winter forecast → generalized seasonal infrastructure planning","infrastructure_dependency","limited","Winter forecasts can inform generalized seasonal infrastructure planning as a physical inference.","limited","moderate","limited","moderate","d9_nws_cle_winter","limited","NWS products support winter hazard context, not water-infrastructure failure or operating effects; no failure rate.")
add(20,"HZ-023","information_sensors","frequency products → planning","monitoring_dependency","moderate","Frequency products provide design/planning context distinct from observations.","moderate","limited","moderate","moderate","b9_noaa_atlas14","moderate","No numeric weighting or risk score.")
add(21,"HZ-002","biogeochemical","climate variability → nutrient timing","seasonal_dependency","moderate","Temperature and precipitation timing can alter seasonal material transport context.","limited","limited","moderate","limited","d9_pnas_hab","limited","No future load or bloom model.")
add(22,"HZ-011","water_quality","lake-level observation → generalized intake/source-water context","water_quality_dependency","unknown","No direct lake-level effect on Toledo treatment or intake operations is established in this package.","moderate","moderate","limited","unknown","d9_epa_great_lakes","unknown","EPA supports observed Great Lakes lake-level variability only; treatment/intake operating effects are unsupported here and the Toledo intake-coordinate discrepancy remains unresolved.")
add(23,"HZ-019","information_sensors","warning → decision-information interface","warning_capacity","moderate","Warnings provide a public decision-information interface; response effectiveness is not established.","moderate","strong","moderate","moderate","b9_nws_points","moderate","No emergency-management system or response outcome is modeled.")
add(24,"HZ-022","information_sensors","drought assessment → situational-awareness/management input","monitoring_dependency","moderate","Drought assessment supports situational awareness and can inform management input; management outcomes are not established.","strong","limited","moderate","strong","b9_drought_gov","moderate","Unknown local condition is not treated as low and no management outcome is inferred.")

DEP_BASIS=[
    "supported_system_dependency", "documented_observation_interface", "physically_plausible_system_pathway", "physically_plausible_system_pathway",
    "documented_mechanism_plus_plausible_pathway", "physically_plausible_system_pathway", "physically_plausible_system_pathway", "unsupported_unknown_interface",
    "physically_plausible_system_pathway", "physically_plausible_system_pathway", "supported_system_dependency", "physically_plausible_system_pathway",
    "documented_product_interface", "physically_plausible_system_pathway", "unsupported_unknown_interface", "supported_system_dependency",
    "physically_plausible_system_pathway", "physically_plausible_system_pathway", "physically_plausible_system_pathway", "documented_product_interface",
    "documented_mechanism_plus_plausible_pathway", "unsupported_unknown_interface", "documented_control_interface", "documented_control_interface",
]

REG_COLUMNS=["dependency_id","hazard_node_id","affected_system","system_interface","dependency_type","dependency_strength","affected_function","evidence_basis","source_id","confidence","quantity_status","notes"]
R=[d[:6]+[d[6],basis,d[11],d[12],"not_quantified",d[13]] for d,basis in zip(D,DEP_BASIS)]
CMP_COLUMNS=["compound_id","hazard_a","hazard_b","affected_system","mechanism","evidence_basis","observed_or_plausible","spatial_scope","temporal_relationship","confidence","source_id","notes"]
C=[
 ["CPL-001","extreme heat","power demand / thermal-load context","energy","Heat can increase cooling demand and thermal load as a physically plausible pathway.","NCA energy chapter supports heat/cooling-demand direction; no local outage series","physically_plausible_pathway","urban / regional","same event or seasonal overlap","moderate","d9_nca_energy","No outage probability, restoration time, equipment-failure, or health outcome claim."],
 ["CPL-002","extreme heat","drought / low water","water;agriculture;ecology","Heat increases evaporative demand while drought reduces water availability.","Regional assessment mechanism","physically_plausible_pathway","county / watershed / lake","seasonal or multi-week","moderate","d9_nca_midwest","No soil-moisture, groundwater, yield, or ecological-population estimate."],
 ["CPL-003","extreme precipitation","nutrient mobilization","biogeochemical;ecology","Event runoff can mobilize landscape nutrients and sediment toward receiving waters.","Western Lake Erie study and accepted nutrient system","documented_mechanism_plus_plausible_pathway","Maumee watershed / western Lake Erie","event-to-seasonal","high","d9_pnas_hab","No future load or bloom magnitude."],
 ["CPL-004","extreme precipitation","wastewater / stormwater burden","water;infrastructure","Intense rain can burden urban drainage and wastewater interfaces as a physical inference.","NCA provides regional precipitation/infrastructure context; no local overflow or treatment evidence","physically_plausible_pathway","urban / watershed","event-scale","limited","d9_nca_midwest","No overflow probability or treatment failure claim; source does not establish local control performance."],
 ["CPL-005","high lake level","wind setup / seiche","coastal;freight","Wind-driven displacement can interact with a generally elevated background lake-level context as a physically plausible compound.","NOAA seiche mechanism; background lake-level context is separate","physically_plausible_pathway","western Lake Erie / shoreline","same event","moderate","d9_noaa_seiche","The source supports the seiche mechanism, not a local combined level; no joint probability, additive level, or inundation footprint."],
 ["CPL-006","flooding","freight / access disruption","freight;infrastructure","Flooded access interfaces can interrupt generalized transportation function.","Assessment and accepted freight system context","physically_plausible_pathway","watershed / regional access","event-scale","moderate","d9_nca_midwest","No route-specific disruption estimate."],
 ["CPL-007","freeze-thaw","infrastructure stress","infrastructure;freight","Alternating freezing and thawing can impose seasonal physical stress as a physical inference.","NWS winter hazard context; no local freeze-thaw or infrastructure evidence","physically_plausible_pathway","regional / infrastructure interface","seasonal","limited","d9_nws_cle_winter","No cycle count or failure rate."],
 ["CPL-008","severe storm","power / communication continuity burden","energy;information_sensors","Wind, lightning, and storm conditions can burden public energy and information continuity as a physical inference.","NCA energy context; communications effect is not directly documented locally","physically_plausible_pathway","regional / urban","same event","limited","d9_nca_energy","No outage, cyber, restoration, or communications-failure model."],
 ["CPL-009","drought","agricultural / ecological stress","agriculture;ecology","Low-water and soil-water conditions can overlap with agricultural and ecological management burden as a physical inference.","Drought Monitor methodology; no local agricultural/ecological effect series","physically_plausible_pathway","county / watershed","seasonal or multi-week","limited","b9_drought_gov","No yield, abundance, or ecological-risk score."],
]
CTRL_BASE_COLUMNS=["control_id","control_type","control_name","targets","documented_mechanism","effectiveness_status","source_id","confidence","notes"]
CTRL_COLUMNS=["control_id","control_type","control_name","targets","documented_mechanism","support_status","effectiveness_status","source_id","confidence","notes"]
CTRL=[
 ["HZC-001","warning","NWS forecasts and hazard warnings","heat;convective;winter;flood","Public forecast and warning interface exists.","documented_control","effectiveness not quantified","b9_nws_points","moderate","Not a guarantee of receipt, compliance, or hazard reduction."],
 ["HZC-002","heat_warning","NWS heat warning / forecast interface","extreme heat","NWS forecast and warning products can support public heat decisions.","documented_control","effectiveness not quantified","b9_nws_points","moderate","No cooling-center inventory, receipt/compliance evidence, or health analysis."],
 ["HZC-003","hydrologic_monitoring","USGS stream gauges","flood;low flow","Daily streamflow observation supports flood and low-flow awareness.","documented_control","coverage partial","b9_usgs_dv","high","One representative gauge does not cover all tributaries."],
 ["HZC-004","lake_monitoring","NOAA CO-OPS Toledo water-level observations","lake level;coastal","CO-OPS station 9063085 measures and archives local daily-mean water levels.","documented_control","coverage partial; effectiveness not applicable","b9_coops_daily","high","One station is not a complete Great Lakes network or shoreline risk score."],
 ["HZC-005","drought_monitoring","U.S. Drought Monitor","drought;low water","Weekly multi-indicator drought assessment supports regional awareness.","documented_control","local specificity limited","b9_drought_gov","high","Assessment is not groundwater measurement."],
 ["HZC-006","floodplain_management","FEMA regulatory flood-hazard mapping and management","flood","Regulatory flood mapping provides planning context.","documented_planning_context","effectiveness not inferred","b9_fema_nfhl","moderate","Regulatory zones are not observed event footprints."],
 ["HZC-007","stormwater_context","Ohio EPA NPDES permitted-discharge and treatment context","precipitation;stormwater","Ohio EPA NPDES provides permitted-discharge and treatment regulatory context; no local municipal stormwater control inventory is established here.","documented_planning_context","effectiveness unknown","bge_ohio_epa_npdes","moderate","Permits are not actual loads or evidence of local outfall, overflow, or treatment performance."],
 ["HZC-008","ecological_buffer","USFWS NWI wetlands and floodplain storage context","flood;nutrient;ecology","USFWS NWI provides wetland inventory and a potential retention/buffering interface as physical system logic.","potential_buffer_inference","effectiveness site-specific","bge_usfws_nwi","moderate","Inventory presence does not establish condition, storage, or nutrient-removal rate."],
 ["HZC-009","agricultural_conservation","H2Ohio conservation and nutrient-management pathway","drought;precipitation;nutrient","H2Ohio provides a nutrient-management and water-quality intervention pathway, not a verified local control inventory.","documented_management_pathway","regional outcome heterogeneous","bge_ohio_h2ohio","moderate","Program context does not establish farm-level adoption or achieved reduction."],
 ["HZC-010","coastal_management","lake-level viewer and shoreline planning tools","lake level;coastal","Screening tools expose lake-level context for planning.","documented_tool","not effectiveness","d9_noaa_llv","moderate","Calm-day viewer excludes wind/seiche and erosion."],
 ["HZC-011","winterization","seasonal winter maintenance context","winter;freeze-thaw","Winter forecasts can support seasonal preparation; asset maintenance is not inventoried here.","plausible_control","effectiveness not quantified","d9_nws_cle_winter","limited","No asset-level winterization inventory."],
 ["HZC-012","information_integration","NWS Great Lakes observation interface","lake;coastal;winter","NWS Great Lakes observations provide a public lake-condition information interface; cross-network coordination is not established here.","documented_interfaces_only","integration effectiveness unknown","d9_nws_gl_obs","moderate","No comprehensive emergency-management model."],
]
CTRL_SUPPORT_STATUS=["documented_control","documented_control","documented_control","documented_control","documented_control","documented_planning_context","unknown_unverified_local_control","potential_buffer_inference","documented_management_pathway","documented_tool","plausible_control","documented_interfaces_only"]
MATRIX_COLUMNS=["pathway","hazard_exposure_context","system_dependency","monitoring_strength","warning_capacity","physical_redundancy","ecological_buffering","infrastructure_control","seasonality","compound_event_potential","spatial_certainty","temporal_certainty","notes"]
MATRIX=[
 ["heat → energy / developed systems","strong","strong","moderate","strong","unknown","limited","moderate","strong","strong","limited","moderate","No demand, outage, or health score."],
 ["precipitation → water / floodplain","strong","strong","moderate","strong","unknown","moderate","moderate","strong","strong","moderate","moderate","Observed and regulatory flood categories remain separate."],
 ["precipitation → nutrient / water quality","strong","strong","moderate","moderate","limited","moderate","moderate","strong","strong","moderate","limited","No future load or bloom probability."],
 ["drought → water / agriculture / ecology","moderate","strong","moderate","limited","unknown","limited","limited","strong","strong","moderate","limited","Drought status, flow, soil, and ecology are not interchangeable."],
 ["lake level + wind setup/seiche","strong","moderate","moderate","moderate","unknown","limited","limited","strong","strong","limited","moderate","No joint probability or shoreline footprint."],
 ["flood → freight / access","moderate","moderate","limited","moderate","unknown","limited","moderate","moderate","strong","limited","moderate","No route-specific disruption probability."],
 ["severe storm → energy / information","moderate","moderate","moderate","strong","unknown","limited","moderate","strong","strong","limited","moderate","No outage or communications-failure model."],
 ["freeze-thaw → infrastructure","moderate","moderate","limited","moderate","unknown","limited","limited","strong","moderate","limited","moderate","No cycle count or failure rate."],
 ["drought / precipitation → ag/ecology","moderate","moderate","limited","limited","limited","moderate","limited","strong","moderate","limited","limited","No social-vulnerability or ecological score."],
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(df,p): p.parent.mkdir(parents=True,exist_ok=True); df.to_csv(p,index=False)
def load_layers():
 h=gpd.read_file(GPKG,layer="water_watersheds_huc8"); l=gpd.read_file(GPKG,layer="water_lake_erie"); w=gpd.read_file(GPKG,layer="water_current_wetlands_25ac"); f=gpd.read_file(GPKG,layer="hydrography_physical"); f["geometry"]=f.geometry.simplify(0.002,preserve_topology=False); return h,l,w,f
def render():
 plt.rcParams["svg.fonttype"]="none"; h,l,w,f=load_layers(); fig=plt.figure(figsize=(16,10),facecolor="#f1eadc"); ax=fig.add_axes([.04,.12,.59,.78],facecolor="#e9e1ce"); h.boundary.plot(ax=ax,color="#9f967f",linewidth=.45,alpha=.65); l.plot(ax=ax,color="#a9d7df",edgecolor="#478c9a",linewidth=.8,alpha=.9); w.plot(ax=ax,color="#6da77c",edgecolor="none",alpha=.4); f.plot(ax=ax,color="#4a8798",linewidth=.3,alpha=.5)
 pts={"heat":(-83.7,41.72),"precip/flood":(-83.85,41.35),"drought":(-83.55,41.12),"lake/coast":(-83.05,41.7),"storm":(-83.35,41.95),"winter":(-84.15,41.55),"systems":(-83.48,41.5)}; colors={"heat":"#c8643f","precip/flood":"#4a8798","drought":"#b58a37","lake/coast":"#2f7890","storm":"#9a4f59","winter":"#667a91","systems":"#6b5c91"}
 for name,(x,y) in pts.items(): ax.scatter([x],[y],s=180,facecolors="none",edgecolors=colors[name],linewidth=1.5,zorder=5); ax.text(x,y,name.upper(),fontsize=6.5,color=colors[name],ha="center",va="center",weight="bold",zorder=6)
 for a,b in [("heat","systems"),("precip/flood","systems"),("drought","systems"),("lake/coast","systems"),("storm","systems"),("winter","systems")]: ax.add_patch(FancyArrowPatch(pts[a],pts[b],arrowstyle="-|>",mutation_scale=10,color="#806b64",linewidth=1,alpha=.65,zorder=4))
 ax.set_xlim(-84.55,-82.55); ax.set_ylim(40.9,42.15); ax.set_axis_off(); side=fig.add_axes([.67,.055,.3,.88]); side.axis("off"); side.text(.03,.98,"MAP 30 — CLIMATE / HAZARD\nDEPENDENCIES & RESILIENCE, 2026",va="top",fontsize=14,weight="bold",color="#17384b",linespacing=1.2); side.text(.03,.855,"Qualitative cross-system interfaces over the factual Phase 9A hazard baseline. Arrows are schematic dependency pathways, not routes, flowlines, or risk surfaces.",va="top",fontsize=8.4,color="#3f4645",linespacing=1.3); side.text(.03,.735,"COMPOUND PATHWAYS",fontsize=10,weight="bold",color="#17384b"); bullets=["Heat + power demand / thermal-load interface","Heat + drought water and seasonal stress","Extreme precipitation + nutrient mobilization","Extreme precipitation + wastewater / stormwater burden","High lake level + wind setup / seiche","Flooding + freight / access disruption","Freeze-thaw + infrastructure stress","Severe storm + power / communication interface","Drought + agricultural / ecological stress"]; y=.70
 for b in bullets: side.text(.05,y,"• "+b,fontsize=7.7,color="#3f4645",va="top"); y-=.048
 side.text(.03,.255,"CONTROLS / BOUNDARIES",fontsize=10,weight="bold",color="#17384b"); side.text(.05,.225,"Warnings, gauges, drought assessments, flood mapping, wetlands, stormwater context, conservation pathways, coastal tools, and seasonal maintenance are documented interfaces, planning contexts, potential buffers, or plausible controls; effectiveness is not quantified. Unknown/unverified interfaces are not low. No probability, composite score, health/EJ ranking, or comprehensive emergency-management model. Great Lakes seiche/wind setup is not ocean storm surge.",fontsize=7.5,color="#3f4645",va="top",linespacing=1.3); side.legend(handles=[Line2D([0],[0],marker="o",color="w",markerfacecolor="#c8643f",markersize=7,label="schematic hazard family"),Line2D([0],[0],color="#806b64",lw=1.2,label="qualitative dependency"),Patch(facecolor="#a9d7df",edgecolor="#478c9a",label="water context"),Patch(facecolor="#6da77c",alpha=.6,label="wetland context")],loc="lower left",bbox_to_anchor=(.02,-.015),frameon=False,fontsize=7.3)
 fig.savefig(MAP.with_suffix(".png"),dpi=220,bbox_inches="tight",facecolor=fig.get_facecolor()); fig.savefig(MAP.with_suffix(".svg"),bbox_inches="tight",facecolor=fig.get_facecolor(),metadata={"Date":None}); plt.close(fig); MAP.with_suffix(".svg").write_text("\n".join(x.rstrip() for x in MAP.with_suffix(".svg").read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
def main():
 for p in (NETWORKS,ANALYSIS,MAPS,REPORTS): p.mkdir(parents=True,exist_ok=True)
 dep_frame=pd.DataFrame(D,columns=DEP_BASE_COLUMNS); dep_frame.insert(7,"relationship_basis",DEP_BASIS)
 ctrl_frame=pd.DataFrame(CTRL,columns=CTRL_COLUMNS)
 write(pd.DataFrame(SOURCE_ROWS,columns=SOURCE_COLUMNS),ANALYSIS/"climate_dependency_sources.csv"); write(dep_frame,DEP); write(pd.DataFrame(R,columns=REG_COLUMNS),REG); write(pd.DataFrame(C,columns=CMP_COLUMNS),CMP); write(ctrl_frame,CTRL_PATH); write(pd.DataFrame(MATRIX,columns=MATRIX_COLUMNS),MAT); render()
 report={"climate_dependency_sources.md":"""# Phase 9B Climate/Hazard Dependency Sources

The Phase 9B source registry is `data/processed/analysis/climate_dependency_sources.csv`.

The Fifth National Climate Assessment supplies Midwest climate/infrastructure context, but does not directly document local asset effects.[1]

Its energy chapter supplies heat, cooling-demand, and energy-dependency context.[2]

EPA supplies observed Great Lakes lake-level variability context; it is not direct evidence of navigation or treatment/intake operations.[3]

NOAA supplies seiche and wind-driven standing-wave mechanism context.[4]

NOAA GLERL supplies Great Lakes ice-cover context; lake-wide ice does not establish local shoreline or ecological effects.[5]

NOAA coastal tools supply screening-level lake-level and inundation context.[6][7]

NWS Great Lakes and winter products supply monitoring and warning interfaces, not direct evidence of freight, infrastructure, or communications consequences.[8][9]

The Western Lake Erie study supplies a documented nutrient/meteorological/ecological compound mechanism.[10]

FEMA regulatory mapping is retained as a distinct flood-planning context.[11]. The parallel `d9_fema_nfhl` and `d9_noaa_inundation` registry rows are retained for audit context only and are not used as claim-row sources; their limitations state this explicitly.

The machine-readable rows distinguish supported system dependencies, documented observation/product interfaces, physically plausible pathways, documented mechanisms plus plausible pathways, documented controls/tools, potential-buffer inference, and unsupported/unknown interfaces. Phase 9B uses these sources to qualify relationships and controls, not to create outage, damage, illness, exposure, social-vulnerability, or joint-probability estimates.
""",
 "climate_dependency_assumptions.md":"""# Phase 9B Climate/Hazard Dependency Assumptions

Phase 9B is a qualitative analytical layer over Phase 9A and does not rebuild accepted Water, Materials, Energy, Information/Sensors, Freight, Ecology, Exposure/Environmental Health, or Biogeochemical systems. A dependency records a mechanism and strength, not a vulnerability score or failure prediction.

Dependency and compound records distinguish supported system dependency, documented mechanism plus plausible pathway, physically plausible pathway, documented control/product interface, and unsupported/unknown interface. No joint probability is assigned. Heat plus power, heat plus drought, precipitation plus nutrient mobilization, precipitation plus stormwater/wastewater, high lake level plus wind setup/seiche, flooding plus freight access, freeze-thaw plus infrastructure stress, severe storm plus power/communication, and drought plus agricultural/ecological stress are retained only as documented mechanisms or explicitly qualified physical/system pathways.

Controls include documented monitoring, warning, planning, public-tool, and management interfaces plus potential buffers. The `support_status` field identifies documented controls, planning contexts, potential-buffer inference, or unknown/unverified local controls. Effectiveness is not inferred from presence. Unknown remains unknown. Great Lakes seiche/wind setup is not ocean storm surge. No health, EJ, demographic, personal-exposure, dose, or emergency-management model is included.
""",
 "climate_dependency_findings.md":"""# Phase 9B Climate/Hazard Dependencies, Compound Events & Resilience Findings

## Dependency structure

INFERENCE: The register labels heat-to-energy demand, precipitation-to-runoff and floodplain connectivity, drought-to-water/agriculture/ecology, lake level-to-coastal/freight access, and severe storm-to-energy/information as prominent qualitative interfaces. The source records support different parts of these relationships and do not establish uniform local effects.[1][2][3]

INFERENCE: Monitoring and warning capacity is strongest where public operational networks are explicit, but network presence does not demonstrate complete coverage or effective outcomes.[8][9]

The matrix preserves qualitative labels only. It contains no numeric weighting, cumulative vulnerability, or hazard score.

## Compound-event register

The register contains nine bounded pathways.

The precipitation-plus-nutrient pathway is the only compound row classified as a documented mechanism plus plausible pathway, based on the Western Lake Erie study linking agricultural phosphorus, spring meteorology, circulation, warm conditions, and residence time.[10]

Heat-plus-power is a physically plausible energy pathway because hot conditions can increase cooling demand; no local outage relationship is documented.[2]

Heat-plus-drought is a plausible seasonal water/agriculture/ecology pathway.[1]

Extreme precipitation plus stormwater/wastewater burden is retained only as a physically plausible urban-hydrologic pathway; NCA context does not document local overflows or treatment performance.[1]

High lake level plus wind setup/seiche is a physically plausible coastal compound because seiche is a wind/pressure-driven standing-wave process in enclosed or semi-enclosed water; no local combined level or shoreline effect is established.[4]

Flood plus freight/access and freeze-thaw plus infrastructure are retained as physically plausible system pathways, not documented local disruptions or route-level predictions.[1][9]

Severe storm plus power/communication and drought plus agricultural/ecological stress remain physically plausible qualitative pathways because no local consequence or joint-probability dataset was found.[1][2]

## Resilience and controls

Documented interfaces include public warnings, USGS stream gauges, the Toledo CO-OPS station, and U.S. Drought Monitor assessment.[3][8][9]

FEMA mapping, urban drainage context, wetland/floodplain potential buffering, conservation pathways, the Lake Level Viewer, and winter forecasts are represented with their support status and limitations.[6][7][9]

Great Lakes ice-cover resources remain contextual monitoring rather than local shoreline, harbor, or ecological-effect evidence.[5]

FEMA regulatory mapping remains a separate planning context.[11]

The controls register does not claim uniform effectiveness; HZC-007 is explicitly an unknown/unverified local-control context and HZC-008 is potential-buffer inference.

NOAA's Lake Level Viewer is a screening tool for calm-day lake-level context and excludes wind-driven waves and seiche; it is not direct evidence of port burden or a local inundation or erosion forecast.[6]

## Boundary and uncertainty

The major uncertainty is the difference between a physically credible pathway and an observed co-occurring event series.

Future climate forcing, local topography, asset condition, operational redundancy, and temporal alignment are not collapsed into a single vulnerability result.
""",
 "climate_dependency_qa.md":"""# Phase 9B Climate/Hazard Dependency QA

The package contains 24 qualitative dependency edges, 24 dependency-register rows, nine compound-event records, 12 controls, a nine-row qualitative matrix, and Map 30 PNG/SVG.

Python and R validators check schemas, source references, explicit relationship-basis and support-status vocabularies, flagged-row source assignments, compound-event classification, absence of probabilities and scores, independently recomputed Phase 9A hash immutability, map integrity, and negative health/social scope.

Compound records do not use probability fields. The unaccepted Phase 9A working baseline is read and hash-checked but is not regenerated by Phase 9B. Existing system tables are reused by named domain/interface strings rather than rebuilt. Unknown/unsupported interfaces remain explicitly marked rather than being converted to low strength.

Map 30 uses generalized schematic interfaces and arrows. It does not display hazard polygons, exact routes, facility topology, social-vulnerability rankings, or emergency-management operations. Great Black Swamp remains C — HOLD / noncanonical and Toledo intake-coordinate reconciliation remains unresolved.
"""}
 for name,text in report.items(): (REPORTS/name).write_text(text,encoding="utf-8")
 src_block="\n## Sources\n\n"+"\n".join(f"[{i}] {row[2]}" for i,row in enumerate(SOURCE_ROWS,1))+"\n"
 (REPORTS/"climate_dependency_sources.md").write_text((REPORTS/"climate_dependency_sources.md").read_text(encoding="utf-8")+src_block,encoding="utf-8")
 (REPORTS/"climate_dependency_findings.md").write_text((REPORTS/"climate_dependency_findings.md").read_text(encoding="utf-8")+src_block,encoding="utf-8")
 artifacts=[DEP,REG,CMP,CTRL_PATH,MAT,ANALYSIS/"climate_dependency_sources.csv",MAP.with_suffix(".png"),MAP.with_suffix(".svg"),REPORTS/"climate_dependency_sources.md",REPORTS/"climate_dependency_assumptions.md",REPORTS/"climate_dependency_findings.md",REPORTS/"climate_dependency_qa.md"]
 out={"phase":"9B","status":"implemented_validated_pending_sol_acceptance","counts":{"dependency_edges":len(D),"dependency_register":len(R),"compound_events":len(C),"controls":len(CTRL),"matrix_rows":len(MATRIX)},"artifacts":{str(p.relative_to(ROOT)).replace("\\","/"): {"bytes":p.stat().st_size,"sha256":sha(p)} for p in artifacts}}
 MAN.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8"); print(json.dumps(out["counts"],indent=2))
if __name__=="__main__": main()
