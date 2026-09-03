"""Build Phase 9C qualitative climate and natural-hazard futures."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
A=ROOT/"data/processed/analysis"; S=ROOT/"data/processed/scenarios"; M=ROOT/"outputs/maps/systems"; F=ROOT/"outputs/figures"; R=ROOT/"reports"; GPKG=ROOT/"data/processed/glasspunk_base.gpkg"
PROJ=A/"climate_projection_evidence.csv"; ASS=S/"climate_scenario_assumptions.csv"; HAZ=S/"climate_scenario_hazard_states.csv"; DEP=S/"climate_scenario_dependency_states.csv"; RES=S/"climate_scenario_resilience_states.csv"; CMPD=S/"climate_compound_event_scenario_states.csv"; COMP=F/"climate_scenario_comparison.csv"; SRC=A/"climate_scenario_sources.csv"; MAP2050=M/"31_climate_hazard_futures_2050"; MAP2075=M/"31b_climate_hazard_futures_2075"; MAN=R/"climate_scenario_manifest.json"

SOURCE_COLUMNS=["source_id","title","url","product_or_endpoint","source_type","projection_or_context","spatial_scope","temporal_scope","use_limitations"]
SOURCE_ROWS=[
 ["c9_nca_midwest","Fifth National Climate Assessment Midwest chapter","https://doi.org/10.7930/NCA5.2023.CH24","Midwest climate, infrastructure, agriculture, and ecological context","federal_assessment","projection context","Midwest / Great Lakes","historical and projected","State and regional synthesis; not local damage, outage, or health projections."],
 ["c9_nca_energy","Fifth National Climate Assessment energy chapter","https://doi.org/10.7930/NCA5.2023.CH5","Heat, cooling demand, and energy-system context","federal_assessment","projection context","United States / Midwest","historical and projected","Supports mechanisms and direction; no local outage probability."],
 ["c9_glisa_summary","GLISA Summary of Climate Change in the Great Lakes Region","https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf","Regional warming, hot days, precipitation, drought, and seasonality ranges","regional_assessment","projection synthesis","U.S. and Canadian Great Lakes","2040-2059 and 2080-2099 relative to 1980-1999","Ranges are regional synthesis envelopes and are not a single model/scenario mapping."],
 ["c9_glisa_trends","GLISA Climate Trends in the Great Lakes Region","https://glisa.umich.edu/wp-content/uploads/2025/06/GLISA-Climate-Trends-2-Pager.pdf","Regional climate trend and projection factsheet","regional_assessment","projection synthesis","Great Lakes region","mid- and late-century","Use rounded ranges with source period; do not relabel late-century as a 2075 point estimate."],
 ["c9_loca2","LOCA version 2 for North America","https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023/","Daily 6 km Tmin/Tmax/precipitation CMIP6 downscaled product","downscaled_climate_product","model_metadata","North America / Great Lakes grid","1950-2100; SSP245/370/585","Product metadata supports explicit 2050/2075 windows; it is not a Lake Erie hydrodynamic or impact model."],
 ["c9_nex_gddp","NASA NEX-GDDP-CMIP6","https://nccs.nasa.gov/data-collections/nex-gddp-cmip6/","Bias-corrected daily global downscaled CMIP6 context","downscaled_climate_product","model_metadata","global / Great Lakes scale","historical and future","Secondary screening context; archive/model availability must be checked before numeric use."],
 ["c9_ohio_summary","NOAA Ohio State Climate Summary","https://statesummaries.ncics.org/chapter/oh/","State-level warming, precipitation, flooding, and drought direction","state_assessment","projection context","Ohio","2006-2100 projections","State direction is not a western-basin local quantitative projection."],
 ["c9_michigan_summary","NOAA Michigan State Climate Summary","https://statesummaries.ncics.org/chapter/mi/","State-level warming, precipitation, Great Lakes, and drought direction","state_assessment","projection context","Michigan / Great Lakes","2006-2100 projections","State direction is not a western-basin shoreline quantitative projection."],
 ["c9_epa_great_lakes","EPA Great Lakes climate indicators","https://www.epa.gov/climate-indicators/great-lakes","Observed Great Lakes levels/temperature and future variability context","federal_indicators","observed_and_synthesis","Great Lakes","1860-present observations; future synthesis","Models disagree on overall level sign; do not impose a single trend."],
 ["c9_notaro_levels","Dynamical Downscaling-Based Projections of Great Lakes Water Levels","https://journals.ametsoc.org/view/journals/clim/28/24/jcli-d-14-00847.1.xml","Opposing MIROC5/CNRM lake-level branches under RCP8.5","peer_reviewed","model_projection","Great Lakes / cross-lake","2040-2059 and 2080-2099","Cross-lake ranges are not western Lake Erie shoreline positions or probabilities."],
 ["c9_notaro_snow","Dynamically Downscaled Projections of Lake-Effect Snow","https://journals.ametsoc.org/view/journals/clim/28/4/jcli-d-14-00467.1.xml","Lake-effect snow, ice, rain/snow transition, and seasonality","peer_reviewed","model_projection","Great Lakes / Lake Erie context","2040-2059 and 2080-2099","Older RCP8.5 model study; no exact future snowstorm or freeze-thaw count."],
 ["c9_basile_precip","Projected precipitation changes within the Great Lakes and Western Lake Erie Basin","https://doi.org/10.1002/joc.5128","Western Lake Erie precipitation ensemble context","peer_reviewed","model_projection","Great Lakes and Western Lake Erie Basin","1980-1999 and 2041-2060","Mixed CMIP5/CMIP3/RCM ensembles; no direct 2075 result or probability."],
 ["c9_pnas_hab","Western Lake Erie agricultural and meteorological HAB study","https://www.pnas.org/doi/10.1073/pnas.1216006110","Observed nutrient/meteorological/ecological compound mechanism","peer_reviewed","historical_mechanism","Western Lake Erie","2011 event and future-consistency discussion","Supports mechanism, not future bloom magnitude, toxin, illness, or treatment burden."],
]

PROJ_COLUMNS=["projection_id","hazard_family","metric","value","units","baseline_period","projection_period","scenario_or_model","model_ensemble_or_method","spatial_scope","observed_or_modeled","source_id","confidence","limitations"]
PROJ_ROWS=[
 ["PRJ-001","extreme_heat","average air temperature change","3.0 to 5.8","deg F","1980-1999","2040-2059","regional synthesis","GLISA synthesis; source does not map range to one scenario","U.S. and Canadian Great Lakes","modeled_projection","c9_glisa_summary","moderate","Regional range; not a western Lake Erie shoreline or municipal value."],
 ["PRJ-002","extreme_heat","average air temperature change","6.3 to 11.4","deg F","1980-1999","2080-2099","regional synthesis","GLISA synthesis","U.S. and Canadian Great Lakes","modeled_projection","c9_glisa_summary","moderate","Late-century bounding range; not a 2075 point estimate."],
 ["PRJ-003","extreme_heat","annual days above 90 F change","9 to 37","days per year","1980-1999","2040-2059","regional synthesis","GLISA synthesis","Great Lakes region","modeled_projection","c9_glisa_trends","moderate","Regional range; no local heat-index or mortality inference."],
 ["PRJ-004","extreme_heat","annual days above 90 F change","27 to 66","days per year","1980-1999","2080-2099","regional synthesis","GLISA synthesis","Great Lakes region","modeled_projection","c9_glisa_trends","moderate","Late-century bounding range; not a 2075 point estimate."],
 ["PRJ-005","heavy_precipitation_flooding","annual precipitation change envelope","-0.3 to +4.2","inches","1980-1999","mid/late-century synthesis","regional synthesis","GLISA summary envelope","Great Lakes region","modeled_projection","c9_glisa_summary","limited","Metric and model aggregation are broad; no flood damage or inundation value."],
 ["PRJ-006","all","downscaled daily grid resolution","6","kilometers","1950-2014 historical training/reference","1950-2100","SSP245; SSP370; SSP585","LOCA version 2; up to 27 CMIP6 models and up to 10 members where available","North America / Great Lakes","model_metadata","c9_loca2","high","Method metadata; numeric regional climate slices require explicit extraction and windowing."],
 ["PRJ-007","lake_coastal","lake-level change branch","-24 to -132","millimeters","1980-1999","2040-2059","MIROC5 / RCP8.5","25 km RegCM4 plus 1-D lake model and GLERL channel model","Great Lakes cross-lake","modeled_projection","c9_notaro_levels","limited","Opposing-sign branch range; not western Lake Erie shoreline or inundation."],
 ["PRJ-008","lake_coastal","lake-level change branch","+75 to +180","millimeters","1980-1999","2040-2059","CNRM / RCP8.5","25 km RegCM4 plus 1-D lake model and GLERL channel model","Great Lakes cross-lake","modeled_projection","c9_notaro_levels","limited","Opposing-sign branch range; not western Lake Erie shoreline or inundation."],
 ["PRJ-009","lake_coastal","lake-level change branch","-97 to -296","millimeters","1980-1999","2080-2099","MIROC5 / RCP8.5","25 km RegCM4 plus 1-D lake model and GLERL channel model","Great Lakes cross-lake","modeled_projection","c9_notaro_levels","limited","Late-century bound; not a 2075 point estimate."],
 ["PRJ-010","lake_coastal","lake-level change branch","+134 to +420","millimeters","1980-1999","2080-2099","CNRM / RCP8.5","25 km RegCM4 plus 1-D lake model and GLERL channel model","Great Lakes cross-lake","modeled_projection","c9_notaro_levels","limited","Late-century bound; not a 2075 point estimate."],
 ["PRJ-011","winter","heavy lake-effect snow day change","-35 to -46","percent","1980-1999","2080-2099","MIROC5/CNRM / RCP8.5","25 km RegCM4 with 1-D lake model","Great Lakes / Lake Erie context","modeled_projection","c9_notaro_snow","limited","Older model study; heavy events remain possible and no exact storm count is inferred."],
 ["PRJ-012","heavy_precipitation_flooding","precipitation change envelope","10 to 20","percent","1980-1999","2041-2060","multi-ensemble / mixed pathways","CMIP5, NARCCAP, and RCM4 comparisons","Great Lakes and Western Lake Erie Basin","modeled_projection","c9_basile_precip","limited","Seasonal/model-dependent range; no direct 2075 support."],
]

scenarios={"A":"Adaptive / Buffered Basin","B":"Managed Variable Basin","C":"Compound Hazard Basin"}
families=["extreme_heat","heavy_precipitation_flooding","drought_low_water","lake_coastal","severe_convective","winter"]
paths=["heat_to_energy","precip_to_nutrient","precip_to_stormwater","flood_to_freight","lake_to_coastal","storm_to_power_information","drought_to_ag_ecology","winter_to_infrastructure"]
controls=["warning_systems","heat_adaptation","floodplain_stormwater","wetland_floodplain_buffer","water_treatment","lake_monitoring","agricultural_conservation","grid_information_redundancy"]
compounds=["heat_plus_power","heat_plus_drought","precip_plus_nutrient","precip_plus_stormwater_wastewater","high_lake_plus_seiche","flood_plus_freight","freeze_thaw_plus_infrastructure","storm_plus_power_communications","drought_plus_ag_ecology"]
hazard_baselines={"extreme_heat":"HZ-001","heavy_precipitation_flooding":"HZ-004","drought_low_water":"HZ-009","lake_coastal":"HZ-012","severe_convective":"HZ-016","winter":"HZ-018"}
path_baselines={"heat_to_energy":"HZD-001","precip_to_nutrient":"HZD-005","precip_to_stormwater":"HZD-006","flood_to_freight":"HZD-007","lake_to_coastal":"HZD-013","storm_to_power_information":"HZD-016;HZD-017","drought_to_ag_ecology":"HZD-009;HZD-010","winter_to_infrastructure":"HZD-018;HZD-019"}
control_baselines={"warning_systems":"HZC-001","heat_adaptation":"HZC-002","floodplain_stormwater":"HZC-006","wetland_floodplain_buffer":"HZC-008","water_treatment":"HZD-008;HZD-022","lake_monitoring":"HZC-004","agricultural_conservation":"HZC-009","grid_information_redundancy":"HZC-012"}
path_sources={"heat_to_energy":"c9_nca_energy","precip_to_nutrient":"c9_pnas_hab","precip_to_stormwater":"c9_nca_midwest","flood_to_freight":"c9_nca_midwest","lake_to_coastal":"c9_epa_great_lakes","storm_to_power_information":"c9_nca_energy","drought_to_ag_ecology":"c9_nca_midwest","winter_to_infrastructure":"c9_nca_midwest"}
compound_sources={"heat_plus_power":"c9_nca_energy","heat_plus_drought":"c9_nca_midwest","precip_plus_nutrient":"c9_pnas_hab","precip_plus_stormwater_wastewater":"c9_nca_midwest","high_lake_plus_seiche":"c9_epa_great_lakes","flood_plus_freight":"c9_nca_midwest","freeze_thaw_plus_infrastructure":"c9_nca_midwest","storm_plus_power_communications":"c9_nca_energy","drought_plus_ag_ecology":"c9_nca_midwest"}

ASS_COLUMNS=["assumption_id","scenario_id","scenario_year","scope","assumption","basis","value_type","source_id","plausibility","uncertainty","reality_status","notes"]
HAZ_COLUMNS=["scenario_id","scenario_year","state_id","baseline_object_id","hazard_family","change_type","future_state","reality_status","relationship_basis","assumption_id","source_id","plausibility","notes"]
DEP_COLUMNS=["scenario_id","scenario_year","state_id","baseline_interface","affected_system","future_state","change_type","reality_status","relationship_basis","assumption_id","source_id","plausibility","notes"]
RES_COLUMNS=["scenario_id","scenario_year","state_id","control_domain","baseline_control","future_state","change_type","reality_status","relationship_basis","assumption_id","source_id","plausibility","notes"]
CMPD_COLUMNS=["scenario_id","scenario_year","state_id","compound_id","hazard_a","hazard_b","affected_system","future_state","change_type","reality_status","relationship_basis","assumption_id","source_id","plausibility","notes"]
COMP_COLUMNS=["scenario_id","scenario_year","hazard_driver","heat","precipitation_flood","drought_low_water","lake_coastal","convective_winter","compound_burden","monitoring","resilience_control","uncertainty","worldbuilding_read"]

def assumption_rows():
 rows=[]
 themes={"A":["Shared climate projection envelopes remain possible while adaptation and ecological buffers substantially improve.","Extreme heat and hot-day exposure are addressed through cooling, warning, and urban adaptation.","Precipitation variability and flood pathways are buffered through floodplain, wetland, and stormwater investment.","Drought and low-water variability are managed through water monitoring, conservation, and agricultural adaptation.","Lake-level sign uncertainty remains, while coastal planning targets exposure to high water, waves, and seiche.","Monitoring, governance, and infrastructure redundancy improve without eliminating physical hazards."],"B":["Regional warming and precipitation variability increase while adaptation proceeds unevenly.","Heat burden persists and cooling adaptation is selective across urban and infrastructure systems.","Flood and stormwater management improves in targeted places while management burden persists.","Drought and low-water conditions remain variable with uneven agricultural and ecological adaptation.","Lake-level sign remains uncertain and coastal management is selective rather than comprehensive.","Monitoring and infrastructure controls improve incrementally but redundancy is uneven."],"C":["The upper or more disruptive part of the regional climate envelope interacts with lagging adaptation.","Heat, cooling demand, and seasonal stress intensify the compound management burden.","Heavy precipitation and runoff create more frequent or severe nutrient/stormwater management episodes as a scenario premise.","Drought variability and water stress interact with agriculture and ecological systems while adaptation lags.","High background lake levels, wind setup/seiche, waves, and access burdens interact episodically.","Warning, monitoring, grid, freight, and infrastructure controls face greater compound-event load and uncertainty."]}
 src=["c9_glisa_summary","c9_glisa_trends","c9_basile_precip","c9_epa_great_lakes","c9_notaro_levels","c9_nca_midwest"]
 for s in scenarios:
  for y in (2050,2075):
   for i,text in enumerate(themes[s],1): rows.append([f"CSA-{s}{y}-{i:02d}",s,y,"climate_hazard_system",text,"projection envelope plus scenario adaptation premise","qualitative",src[i-1],"moderate" if s=="B" else "limited","high" if (s=="C" and i in (1,3,4,5)) else "moderate","fictional","No probability or deterministic future hazard value is assigned."])
 return rows

def hazard_state(s,f):
 base={"extreme_heat":"warming_and_hot_days_continue","heavy_precipitation_flooding":"precipitation_variability_persists","drought_low_water":"drought_low_water_variability_persists","lake_coastal":"lake_level_sign_uncertain","severe_convective":"convective_change_uncertain","winter":"warmer_winter_with_snow_ice_transition"}[f]
 return {"A":base+"_buffered","B":base+"_managed_unevenly","C":base+"_compound_burden"}[s]
def dep_state(s,p): return {"A":"dependency_persists_buffered","B":"dependency_persists_selective","C":"dependency_intensifies_episodically"}[s]
def res_state(s,c): return {"A":"control_strengthened_and_integrated","B":"control_targeted_or_uneven","C":"control_burdened_and_lagging"}[s]
def comp_state(s,c): return {"A":"pathway_remains_possible_but_buffered","B":"pathway_persists_with_local_management","C":"pathway_more_disruptive_and_uncertain"}[s]

def tables():
 ass=assumption_rows(); h=[]; d=[]; r=[]; cp=[]
 for s in scenarios:
  for y in (2050,2075):
   sid=f"{s}{y}"
   for i,f in enumerate(families,1): h.append([sid,y,f"CSH-{sid}-{i:02d}",hazard_baselines[f],f,"qualitative_driver",hazard_state(s,f),"fictional","scenario_assumption",f"CSA-{s}{y}-{((i-1)%6)+1:02d}","c9_glisa_summary" if f in ("extreme_heat","heavy_precipitation_flooding") else "c9_notaro_levels" if f=="lake_coastal" else "c9_notaro_snow" if f=="winter" else "c9_nca_midwest","moderate" if s=="B" else "limited","Qualitative scenario state; no local future hazard surface or probability."])
   for i,p in enumerate(paths,1): d.append([sid,y,f"CSD-{sid}-{i:02d}",path_baselines[p],"cross_system",dep_state(s,p),"qualitative_change","fictional","scenario_assumption",f"CSA-{s}{y}-{((i+1)%6)+1:02d}",path_sources[p],"moderate" if s=="B" else "limited","Qualitative scenario state references a Phase 9B interface; no numeric dependency strength or outage probability."])
   for i,c in enumerate(controls,1): r.append([sid,y,f"CSR-{sid}-{i:02d}",c,control_baselines[c],res_state(s,c),"qualitative_change","fictional","scenario_assumption",f"CSA-{s}{y}-{((i+2)%6)+1:02d}","c9_nca_energy" if c=="heat_adaptation" else "c9_epa_great_lakes" if c=="lake_monitoring" else "c9_nca_midwest","moderate" if s=="B" else "limited","Control state is qualitative; effectiveness is not quantified."])
   for i,c in enumerate(compounds,1):
    a,b=(c.split("_plus_",1)+["system"])[:2] if "_plus_" in c else (c,"system")
    cp.append([sid,y,f"CSC-{sid}-{i:02d}",c,a,b,"cross_system",comp_state(s,c),"qualitative_change","fictional","scenario_assumption",f"CSA-{s}{y}-{((i+3)%6)+1:02d}",compound_sources[c],"moderate" if s=="B" else "limited","Scenario interaction, not a probability or guaranteed co-occurrence."])
 return ass,h,d,r,cp

COMP_ROWS=[]
for s in scenarios:
 for y in (2050,2075):
  COMP_ROWS.append([f"{s}{y}",y,"regional_projection_envelope_shared","persistent_with_adaptation" if s=="A" else "persistent_uneven" if s=="B" else "upper_or_disruptive_envelope","buffered" if s=="A" else "managed_unevenly" if s=="B" else "compound_burden","managed" if s=="A" else "variable" if s=="B" else "episodically_intensified","sign_uncertain_managed" if s=="A" else "sign_uncertain_selective" if s=="B" else "high_background_and_seiche_burden","uncertain_seasonal" if s=="A" else "persistent_variable" if s=="B" else "compound_burden","possible_buffered" if s=="A" else "managed_uneven" if s=="B" else "more_disruptive_uncertain","expanded" if s=="A" else "incremental" if s=="B" else "burdened","strengthened_integrated" if s=="A" else "selective" if s=="B" else "lagging_burdened","moderate" if s=="A" else "moderate_high" if s=="B" else "high","Climate-conditioned infrastructure, governance, and seasonal work become worldbuilding levers; not a forecast."])

def load_layers():
 h=gpd.read_file(GPKG,layer="water_watersheds_huc8"); l=gpd.read_file(GPKG,layer="water_lake_erie"); w=gpd.read_file(GPKG,layer="water_current_wetlands_25ac"); f=gpd.read_file(GPKG,layer="hydrography_physical"); f["geometry"]=f.geometry.simplify(0.002,preserve_topology=False); return h,l,w,f
def render(year,path):
 plt.rcParams["svg.fonttype"]="none"; h,l,w,f=load_layers(); fig=plt.figure(figsize=(16,10),facecolor="#f1eadc"); ax=fig.add_axes([.04,.12,.59,.78],facecolor="#e9e1ce"); h.boundary.plot(ax=ax,color="#9f967f",linewidth=.45,alpha=.65); l.plot(ax=ax,color="#a9d7df",edgecolor="#478c9a",linewidth=.8,alpha=.9); w.plot(ax=ax,color="#6da77c",edgecolor="none",alpha=.4); f.plot(ax=ax,color="#4a8798",linewidth=.3,alpha=.5)
 pts={"A":(-84.0,41.75),"B":(-83.45,41.75),"C":(-82.9,41.75)}; cols={"A":"#4f927b","B":"#c08a42","C":"#a8524d"};
 for s,(x,y) in pts.items(): ax.scatter([x],[y],s=260,c=cols[s],edgecolor="#f1eadc",linewidth=1.1,zorder=6); ax.text(x,y,s,color="white",weight="bold",ha="center",va="center",zorder=7); ax.text(x,y-.065,scenarios[s].split(" / ")[0],fontsize=7.2,color=cols[s],ha="center",va="top",zorder=7)
 ax.set_xlim(-84.55,-82.55); ax.set_ylim(40.9,42.15); ax.set_axis_off(); side=fig.add_axes([.67,.045,.30,.90]); side.axis("off"); side.text(.03,.98,f"MAP {'31' if year==2050 else '31b'} — CLIMATE & HAZARD FUTURES, {year}",va="top",fontsize=13.5,weight="bold",color="#17384b",linespacing=1.15); side.text(.03,.865,"Three qualitative alternatives diverge in resilience, management, and compound-event burden. Scenario markers are schematic; they are not hazard zones, forecasts, or probabilities.",va="top",fontsize=8.3,color="#3f4645",linespacing=1.3); side.text(.03,.75,"SCENARIO FAMILIES",fontsize=10,weight="bold",color="#17384b")
 texts={"A":"Adaptive / Buffered Basin\nHazards persist or shift\nBuffers, monitoring, cooling, and redundancy strengthen","B":"Managed Variable Basin\nVariability increases\nAdaptation is targeted and uneven","C":"Compound Hazard Basin\nInteractions become more burdensome\nAdaptation lags without inevitable collapse"}; y=.715
 for s in scenarios: side.text(.05,y,f"{s} — {texts[s]}",fontsize=7.7,color=cols[s],va="top",linespacing=1.25); y-=.105
 side.text(.03,.365,"PROJECTION ANCHORS",fontsize=10,weight="bold",color="#17384b"); side.text(.05,.335,"GLISA mid-century uses 2040–2059; late-century uses 2080–2099 and is not a 2075 point estimate. LOCA2 supports explicit centered windows for 2050 and 2075. Great Lakes water-level studies retain opposing signs. RCP/SSP/model provenance remains explicit.",fontsize=7.7,color="#3f4645",va="top",linespacing=1.3); side.text(.03,.205,"BOUNDARIES",fontsize=10,weight="bold",color="#17384b"); side.text(.05,.175,"No single deterministic forecast, probability, future flood damage, tornado count, shoreline position, outage probability, mortality, disease, or social-vulnerability score. No hazard surface or comprehensive emergency-management model. Great Lakes seiche/wind setup is not ocean storm surge.",fontsize=7.5,color="#3f4645",va="top",linespacing=1.25); side.legend(handles=[Line2D([0],[0],marker="o",color="w",markerfacecolor=cols["A"],markersize=7,label="A adaptive / buffered"),Line2D([0],[0],marker="o",color="w",markerfacecolor=cols["B"],markersize=7,label="B managed variable"),Line2D([0],[0],marker="o",color="w",markerfacecolor=cols["C"],markersize=7,label="C compound hazard"),Patch(facecolor="#a9d7df",edgecolor="#478c9a",label="water context"),Patch(facecolor="#6da77c",alpha=.6,label="wetland context")],loc="lower left",bbox_to_anchor=(.02,-.015),frameon=False,fontsize=7.2)
 fig.savefig(path.with_suffix(".png"),dpi=220,bbox_inches="tight",facecolor=fig.get_facecolor()); fig.savefig(path.with_suffix(".svg"),bbox_inches="tight",facecolor=fig.get_facecolor(),metadata={"Date":None}); plt.close(fig); path.with_suffix(".svg").write_text("\n".join(x.rstrip() for x in path.with_suffix(".svg").read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for p in (A,S,M,F,R): p.mkdir(parents=True,exist_ok=True)
 ass,h,d,r,cp=tables(); pd.DataFrame(PROJ_ROWS,columns=PROJ_COLUMNS).to_csv(PROJ,index=False); pd.DataFrame(ass,columns=ASS_COLUMNS).to_csv(ASS,index=False); pd.DataFrame(h,columns=HAZ_COLUMNS).to_csv(HAZ,index=False); pd.DataFrame(d,columns=DEP_COLUMNS).to_csv(DEP,index=False); pd.DataFrame(r,columns=RES_COLUMNS).to_csv(RES,index=False); pd.DataFrame(cp,columns=CMPD_COLUMNS).to_csv(CMPD,index=False); pd.DataFrame(COMP_ROWS,columns=COMP_COLUMNS).to_csv(COMP,index=False); pd.DataFrame(SOURCE_ROWS,columns=SOURCE_COLUMNS).to_csv(SRC,index=False); render(2050,MAP2050); render(2075,MAP2075)
 reports={"climate_scenario_sources.md":"""# Phase 9C Climate & Hazard Futures Sources

The Phase 9C source registry is `data/processed/analysis/climate_scenario_sources.csv`.

The Fifth National Climate Assessment provides Midwest climate and energy context.[1][2]

GLISA provides Great Lakes regional projection envelopes for warming, hot days, precipitation, and seasonality.[3][4]

LOCA version 2 provides a transparent CMIP6 downscaling method for explicit daily windows centered on 2050 and 2075.[5]

NASA NEX-GDDP-CMIP6 and NOAA state summaries are retained as secondary or state-scale context, not silently substituted for local slices.[6][7][8]

EPA and peer-reviewed Great Lakes studies preserve observed variability and opposing future lake-level signs.[9][10]

The same evidence preserves lake-effect snow transition and Western Lake Erie precipitation limits.[11][12]

The Western Lake Erie nutrient/meteorological study supports a compound mechanism, not a future bloom magnitude.[13]

The future package uses ranges and qualitative states without probabilities. Late-century 2080–2099 ranges are not relabeled as 2075 point estimates, and RCP/SSP/model provenance is preserved.
""",
 "climate_scenario_assumptions.md":"""# Phase 9C Climate & Hazard Futures Assumptions

The three scenario families share the same external climate evidence envelope and diverge primarily through adaptation, management, monitoring, ecological buffering, infrastructure redundancy, and compound-event burden.[1][3][5]

A — Adaptive / Buffered Basin does not remove hazards. It strengthens cooling, floodplain/wetland, stormwater, water, warning, monitoring, coastal, agricultural, grid, and infrastructure controls.[1][2][3]

B — Managed Variable Basin is not a midpoint. It represents uneven, targeted, incremental adaptation under persistent variability.[3][7][9]

C — Compound Hazard Basin is a stress-test alternative in which interactions burden systems more severely while adaptation lags. It does not assert inevitable catastrophe or collapse.[1][2][13]

Projection values are used only where the source directly supports a range or method. No exact 2075 local slice, future flood damage, shoreline position, tornado count, outage probability, health outcome, or joint compound-event probability is fabricated.[5][9][10]
""",
 "climate_scenario_consistency.md":"""# Phase 9C Climate & Hazard Scenario Consistency

All six scenario-horizon states reference explicit Phase 9A hazard-node IDs and Phase 9B dependency/control IDs from the corrected working baselines without modifying those baselines.

The scenario layer separates projection evidence, scenario assumptions, hazard states, dependency states, resilience states, compound-event states, and speculative worldbuilding implications. Baseline IDs are checked against the Phase 9A/9B tables rather than inferred from row order.[3][5][9]

The climate evidence is not converted into probabilities. Lake-level sign uncertainty is retained, and late-century source periods are not relabeled as 2075 point estimates.[9][10]

No scenario state asserts a deterministic flood footprint, shoreline position, outage probability, tornado count, disease burden, mortality, or social-vulnerability ranking.
""",
 "climate_scenario_findings.md":"""# Phase 9C Climate & Hazard Futures Findings

## Projection evidence actually used

FACT: The GLISA regional synthesis gives a mid-century average-temperature increase envelope of 3.0–5.8 deg F for 2040–2059 relative to 1980–1999.[3]

FACT: Its late-century envelope is 6.3–11.4 deg F for 2080–2099 relative to 1980–1999.[3]

FACT: GLISA reports an increase of roughly 9–37 annual days above 90 deg F by mid-century and 27–66 by late century.[4]

FACT: The regional synthesis contains a broad annual-precipitation envelope of approximately -0.3 to +4.2 inches.[3]

FACT: LOCA2 provides 6 km daily Tmin, Tmax, and precipitation data across 1950–2100 for SSP245, SSP370, and SSP585 with model/member availability recorded in the product metadata.[5]

FACT: A Great Lakes lake-level study preserves opposing MIROC5 and CNRM branches rather than a single sign.[10]

FACT: The same study reports cross-lake mid-century branches of approximately -24 to -132 mm and +75 to +180 mm, and late-century branches of approximately -97 to -296 mm and +134 to +420 mm.[10]

FACT: A lake-effect-snow study projects a late-century reduction of roughly 35–46 percent in heavy lake-effect snow days under its RCP8.5 model configurations.[11]

FACT: A Western Lake Erie precipitation study reports model-dependent mid-century changes generally around 10–20 percent depending on season and ensemble.[12]

FACT: NASA NEX-GDDP-CMIP6 is retained as secondary downscaled climate-data context, not as a lake-level or impact model.[6]

FACT: NOAA state summaries provide state-scale directional context for Ohio and Michigan, not western-basin local values.[7][8]

These projection records are ranges, model metadata, or directional evidence. They are not probabilities, confidence intervals, local shoreline positions, or exact 2050/2075 values.

## A — Adaptive / Buffered Basin

SCENARIO: A retains physical heat, precipitation, drought, lake-level, storm, and winter hazards while strengthening cooling, floodplain/wetland, stormwater, water-treatment, monitoring, coastal, agricultural, grid, and access controls.[1][2][3]

A2050 is a buffered mid-century adaptation state using the 2040–2059 projection envelope as context, not as a single local forecast.[3][5]

A2075 uses an explicit centered-window principle and late-century ranges only as bounds; hazards remain possible while control capacity is stronger.[4][5][9]

## B — Managed Variable Basin

SCENARIO: B represents a working basin with persistent climate variability and selective adaptation across cities, farms, infrastructure, ecology, freight, and monitoring.[1][3][7]

B2050 emphasizes persistent heat, variable precipitation, drought/low-water management, uncertain lake levels, and locally uneven resilience.[3][9][12]

B2075 extends that uneven management burden without treating the late-century envelope as a point prediction.[4][5][10]

## C — Compound Hazard Basin

SCENARIO: C represents a physically plausible stress-test in which heat, precipitation, drought, lake processes, severe weather, winter transitions, nutrient mobilization, stormwater, power, communications, freight, and ecological systems interact under lagging adaptation.[1][2][13]

C2050 emphasizes compound-event load around the mid-century envelope and does not assert collapse.[3][10][12]

C2075 emphasizes higher uncertainty and management burden using late-century bounds.[4][5]

It preserves explicit model disagreement in lake-level and winter outcomes.[10][11]

## Hazard-family futures

Heat futures are the most directly quantified regional signal through temperature and hot-day ranges.[3][4]

Precipitation and flood futures are more uncertain because annual totals, seasonal timing, extreme intensity, watershed response, floodplain geometry, and urban drainage are distinct.[3][5][12]

Drought futures are represented as higher evaporative and soil-water stress possibilities, not exact frequency or groundwater forecasts.[1][7][9]

Coastal futures preserve opposing lake-level signs and treat wind setup/seiche, waves, ice, and shoreline effects as qualitative compound states.[9][10][11]

Severe convective and winter futures remain directional or qualitative; no future tornado count, hail count, freeze-thaw count, or local snow probability is assigned.[1][7][11]

## Compound-event futures

The scenario register carries nine compound pathways from Phase 9B into A/B/C states. The precipitation-plus-nutrient pathway retains the documented Western Lake Erie mechanism while excluding future loads, bloom magnitude, toxin, and illness claims.[13]

Heat-plus-power, heat-plus-drought, flood-plus-freight, and freeze-thaw-plus-infrastructure remain qualitative interaction states.[1][2]

Severe-storm-plus-power/communications, high-lake-plus-seiche, and drought-plus-agriculture/ecology also remain qualitative interaction states.[9][10]

No future joint probability is assigned to any compound event.

## Resilience and adaptation futures

A strengthens and integrates controls but does not eliminate hazards.[1][2][3]

B expands selected controls unevenly and preserves local differences in redundancy and monitoring.[3][7][9]

C increases management burden and uncertainty while retaining non-catastrophic alternatives and possible targeted buffers.[1][2][13]
""",
 "climate_scenario_worldbuilding.md":"""# Phase 9C Climate & Hazard Futures — Worldbuilding Implications

These are explicitly speculative implications, not scientific baseline or projection claims:

- Wetlands and floodplains become climate infrastructure whose storage, maintenance, and land claims are negotiated.
- Cooling networks become civic infrastructure rather than private household equipment alone.
- Freight, agriculture, and seasonal labor reorganize around heat, wet access, low water, ice, and warning windows.
- Water-treatment resilience becomes a public trust institution during compound runoff and lake-condition episodes.
- Coastal retreat, selective hardening, and movable access infrastructure compete as lake-level sign uncertainty persists.
- Distributed grid and communications redundancy become visible regional design choices rather than invisible engineering.
- Warning fatigue becomes a governance problem when alerts are frequent but unevenly consequential.
- Climate sensor networks become civic power: control over data timing, interpretation, and public release shapes accountability.
- Stormwater landscapes and heat-adapted urban design turn roads, parks, roofs, and drainage into seasonal climate interfaces.
- Institutions design for compound events rather than one hazard at a time.
""",
 "climate_scenario_qa.md":"""# Phase 9C Climate & Hazard Futures QA

The package contains 12 projection evidence records, 36 scenario assumptions, 36 hazard-state records, 48 dependency-state records, 48 resilience-state records, 54 compound-event scenario states, six comparison rows, and Maps 31/31b.

Python and R validators check scenario separation, source references, projection-period provenance, baseline object/interface IDs, qualitative vocabularies, absence of probabilities and unsupported impact values, recomputed Phase 9A/9B immutability hashes, map integrity, and health/social negative scope.

The validators reject future tornado counts, future flood damages, shoreline positions, outage probabilities, mortality, disease, social-vulnerability scoring, composite hazard scores, and deterministic hazard surfaces. They require explicit scenario year, model/scenario framing, baseline references, relationship basis, assumption reference, source reference, and uncertainty.

Map 31 and Map 31b use generalized scenario markers and projection caveats. They do not display hazard zones, exact routes, inundation footprints, shoreline predictions, or infrastructure-failure probabilities. Late-century 2080–2099 evidence is not relabeled as a 2075 point estimate.
""",
 }
 for name,text in reports.items(): (R/name).write_text(text,encoding="utf-8")
 block="\n## Sources\n\n"+"\n".join(f"[{i}] {row[2]}" for i,row in enumerate(SOURCE_ROWS,1))+"\n"
 for name in ("climate_scenario_sources.md","climate_scenario_findings.md"): (R/name).write_text((R/name).read_text(encoding="utf-8")+block,encoding="utf-8")
 arts=[PROJ,ASS,HAZ,DEP,RES,CMPD,COMP,SRC,MAP2050.with_suffix('.png'),MAP2050.with_suffix('.svg'),MAP2075.with_suffix('.png'),MAP2075.with_suffix('.svg'),R/"climate_scenario_sources.md",R/"climate_scenario_assumptions.md",R/"climate_scenario_consistency.md",R/"climate_scenario_findings.md",R/"climate_scenario_worldbuilding.md",R/"climate_scenario_qa.md"]
 out={"phase":"9C","status":"implemented_validated_pending_sol_acceptance","counts":{"projection_records":len(PROJ_ROWS),"assumptions":len(ass),"hazard_states":len(h),"dependency_states":len(d),"resilience_states":len(r),"compound_event_states":len(cp),"comparison_rows":len(COMP_ROWS)},"artifacts":{str(p.relative_to(ROOT)).replace('\\','/'): {"bytes":p.stat().st_size,"sha256":sha(p)} for p in arts}}
 MAN.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out['counts'],indent=2))
if __name__=='__main__': main()
