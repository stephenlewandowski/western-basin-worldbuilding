"""Build qualitative Phase 6C ecological futures for 2050 and 2075."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[3]; SCEN=ROOT/'data/processed/scenarios'; MAPS=ROOT/'outputs/maps/systems'; FIG=ROOT/'outputs/figures'; REP=ROOT/'reports'
ASS=SCEN/'ecology_scenario_assumptions.csv'; NODES=SCEN/'ecology_nodes_scenario.csv'; EDGES=SCEN/'ecology_edges_scenario.csv'; DIST=SCEN/'ecological_disturbance_scenario.csv'; RES=SCEN/'ecological_resilience_scenario.csv'; COMP=FIG/'ecological_scenarios_comparison.csv'; MAP2050=MAPS/'22_ecological_futures_2050'; MAP2075=MAPS/'22b_ecological_futures_2075'; MAN=REP/'ecology_scenario_manifest.json'

components=['western_lake_erie_aquatic','maumee_tributary_floodplain','coastal_wetlands_marshes','black_swamp_legacy_agriculture','terrestrial_habitat_fragmentation','migratory_mobile_species']
scenarios={'A':'Restored Connectivity','B':'Managed Working Basin','C':'High-Pressure Fragmented Basin'}
plaus={'A':'moderate','B':'high','C':'moderate'}
source_by={'western_lake_erie_aquatic':'noaa_hab','maumee_tributary_floodplain':'usgs_3dhp_all','coastal_wetlands_marshes':'usfws_nwi','black_swamp_legacy_agriculture':'h2ohio_great_black_swamp_history','terrestrial_habitat_fragmentation':'phase6a_mrlc_land_cover','migratory_mobile_species':'phase6a_usfws_ottawa_nwr'}

def assumptions():
 rows=[]
 themes={'A':['Wetland and riparian restoration expands through coordinated adaptive management.','Ecological monitoring and nutrient management support stronger connectivity.','Land availability and maintenance constrain restoration reach.'], 'B':['Working agriculture, cities, industry, and ecological functions continue together.','Targeted buffers, drainage adaptation, and selective restoration persist.','Fragmentation remains but strategic links are maintained.'], 'C':['Compound disturbance pressure outpaces broad restoration capacity.','Aquatic and wetland management becomes more intensive and uncertain.','Ecological refugia and managed support become more important.']}
 for s in scenarios:
  for y in [2050,2075]:
   for i,t in enumerate(themes[s],1): rows.append([f'ECSA-{s}{y}-{i}',f'{s}{y}',y,'cross_system',t,'landscape_and_ecological_drivers','qualitative_scenario_basis',source_by['coastal_wetlands_marshes'],plaus[s],'unknown' if i==3 else 'moderate','connectivity_and_disturbance','scenario_assumption','No probability or forecast is assigned.'])
 return pd.DataFrame(rows,columns=['assumption_id','scenario_id','scenario_year','ecological_component','assumption','driver','basis','source_id','plausibility','uncertainty','dependency','status','notes'])

def future_state(s,comp,y):
 if s=='A': return {'western_lake_erie_aquatic':('persist','resilience_increased'),'maumee_tributary_floodplain':('reconnect','resilience_increased'),'coastal_wetlands_marshes':('expand','restore'),'black_swamp_legacy_agriculture':('restore','disturbance_reduced'),'terrestrial_habitat_fragmentation':('reconnect','resilience_increased'),'migratory_mobile_species':('expand','monitoring_expanded')}[comp]
 if s=='B': return {'western_lake_erie_aquatic':('persist','management_intensified'),'maumee_tributary_floodplain':('persist','dependency_increased'),'coastal_wetlands_marshes':('persist','restore'),'black_swamp_legacy_agriculture':('persist','management_intensified'),'terrestrial_habitat_fragmentation':('persist','dependency_increased'),'migratory_mobile_species':('persist','monitoring_expanded')}[comp]
 return {'western_lake_erie_aquatic':('fragment','disturbance_increased'),'maumee_tributary_floodplain':('contract','disturbance_increased'),'coastal_wetlands_marshes':('contract','resilience_reduced'),'black_swamp_legacy_agriculture':('fragment','disturbance_increased'),'terrestrial_habitat_fragmentation':('fragment','disturbance_increased'),'migratory_mobile_species':('contract','resilience_reduced')}[comp]

def build_tables():
 a=assumptions(); rows=[]; erows=[]; drows=[]; rrows=[]
 for s in scenarios:
  for y in [2050,2075]:
   sid=f'{s}{y}'
   for j,c in enumerate(components,1):
    state,change=future_state(s,c,y); aid=f'ECSA-{s}{y}-{((j-1)%3)+1}'; oid=f'SCN-{sid}-{j:02d}'
    rows.append([sid,y,oid,f'ECO-{j:03d}',c,change,state,'fictional','scenario_assumption',aid,source_by[c],plaus[s],'Qualitative future function; no precise habitat boundary or species location.'])
   for j in range(1,6): erows.append([sid,y,f'SE-{sid}-{j:02d}',f'SCN-{sid}-{j:02d}',f'SCN-{sid}-{j+1:02d}','qualitative_interface','fictional','scenario_assumption',f'ECSA-{s}{y}-{((j-1)%3)+1}',source_by[components[j-1]],plaus[s],'Scenario relationship is not an exact movement route.'])
   for j,c in enumerate(components,1):
    st,ch=future_state(s,c,y); dstate='reduced' if s=='A' else 'persists' if s=='B' else 'intensified'; rstate='strengthened' if s=='A' else 'persists' if s=='B' else 'weakened'
    drows.append([sid,y,f'ECDIS-{j:03d}',c,dstate,'qualitative_scenario','scenario_assumption',source_by[c],plaus[s],'No quantitative consequence or species-specific impact.'])
    rrows.append([sid,y,c,rstate,'qualitative_scenario','scenario_assumption',source_by[c],plaus[s],'Descriptive future support state, not a risk score.'])
 dims=['wetland_function','aquatic_connectivity','riparian_connectivity','terrestrial_connectivity','habitat_redundancy','restoration_intensity','disturbance_pressure','agricultural_compatibility','management_intensity','monitoring_capacity','ecological_uncertainty','mobility_or_recolonization_support']
 levels={'A':['high','high','high','high','high','high','low','moderate','high','high','moderate','high'],'B':['moderate','moderate','moderate','moderate','moderate','moderate','moderate','high','moderate','moderate','moderate','moderate'],'C':['low','low','low','low','low','low','high','moderate','high','low','high','low']}
 crows=[]
 for s in scenarios:
  for y in [2050,2075]:
   for d,l in zip(dims,levels[s]): crows.append([f'{s}{y}',y,d,l,'Qualitative scenario comparison; no probability or quantitative risk.'])
 return a,pd.DataFrame(rows,columns=['scenario_id','scenario_year','object_id','baseline_object_id','ecological_component','change_type','future_state','reality_status','relationship_basis','assumption_id','source_id','plausibility','notes']),pd.DataFrame(erows,columns=['scenario_id','scenario_year','edge_id','from_object_id','to_object_id','relationship_type','reality_status','relationship_basis','assumption_id','source_id','plausibility','notes']),pd.DataFrame(drows,columns=['scenario_id','scenario_year','disturbance_id','ecological_component','future_state','relationship_basis','assumption_id','source_id','plausibility','notes']),pd.DataFrame(rrows,columns=['scenario_id','scenario_year','ecological_component','future_state','change_type','relationship_basis','source_id','plausibility','notes']),pd.DataFrame(crows,columns=['scenario_id','scenario_year','dimension','level','notes'])

def render(year,path):
 plt.rcParams['svg.fonttype']='none'
 colors={'A':'#4f927b','B':'#c08a42','C':'#a8524d'}; fig,ax=plt.subplots(figsize=(16,9),facecolor='#f1eadc'); ax.set_facecolor('#e9e1ce'); ax.axis('off'); ax.text(.03,.95,f'MAP {"22" if year==2050 else "22b"} — ECOLOGICAL FUTURES, {year}',transform=ax.transAxes,fontsize=18,weight='bold',color='#17384b',va='top'); ax.text(.03,.90,'Three qualitative alternatives diverge from the factual 2026 ecological baseline. Scenario panels are not forecasts.',transform=ax.transAxes,fontsize=9,color='#3f4645')
 for i,(s,name) in enumerate(scenarios.items()):
  x=.03+i*.325; ax.add_patch(Rectangle((x,.18),.29,.62,facecolor=colors[s],alpha=.16,edgecolor=colors[s],linewidth=2,transform=ax.transAxes)); ax.text(x+.02,.75,f'{s} — {name}',transform=ax.transAxes,fontsize=12,weight='bold',color=colors[s]); texts={'A':'Wetland and riparian reconnection\nProtected and restored support expands\nMonitoring and adaptive management grow\nTension: ambition vs land and maintenance','B':'Working landscape persists\nTargeted buffers and selective restoration\nFragmentation remains managed\nTension: productivity vs connectivity','C':'Compound pressures intensify\nHabitat isolation and managed refugia\nUncertainty and management burden grow\nTension: adaptation vs disturbance'}; ax.text(x+.02,.68,texts[s],transform=ax.transAxes,fontsize=9,color='#3f4645',va='top',linespacing=1.5); y=.48
  for c in components: st,_=future_state(s,c,year); ax.text(x+.025,y,f'{c.replace("_"," ")}: {st}',transform=ax.transAxes,fontsize=7.6,color='#3f4645'); y-=.042
 ax.text(.03,.10,'BOUNDARIES  No future population values, extinction events, exact range/migration/spawning locations, disease/vector ecology, historical Great Black Swamp restoration boundary, or probability is modeled. Great Black Swamp remains C — HOLD / noncanonical.',transform=ax.transAxes,fontsize=8,color='#3f4645',wrap=True)
 fig.savefig(path.with_suffix('.png'),dpi=180,bbox_inches='tight',facecolor=fig.get_facecolor()); svg=path.with_suffix('.svg'); fig.savefig(svg,bbox_inches='tight',facecolor=fig.get_facecolor(),metadata={'Date':None}); plt.close(fig); svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')

def main():
 SCEN.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True); MAPS.mkdir(parents=True,exist_ok=True); a,n,e,d,r,c=build_tables(); a.to_csv(ASS,index=False); n.to_csv(NODES,index=False); e.to_csv(EDGES,index=False); d.to_csv(DIST,index=False); r.to_csv(RES,index=False); c.to_csv(COMP,index=False); render(2050,MAP2050); render(2075,MAP2075)
 artifacts=[ASS,NODES,EDGES,DIST,RES,COMP,MAP2050.with_suffix('.png'),MAP2050.with_suffix('.svg'),MAP2075.with_suffix('.png'),MAP2075.with_suffix('.svg')]; out={'phase':'6C','generated':'2026-09-02','status':'ecological_scenarios','counts':{'assumptions':len(a),'scenario_nodes':len(n),'scenario_edges':len(e),'disturbance_states':len(d),'resilience_states':len(r),'comparison_rows':len(c)},'artifacts':{str(p.relative_to(ROOT)).replace('\\','/'): {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}}; MAN.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out['counts'],indent=2))
if __name__=='__main__': main()
