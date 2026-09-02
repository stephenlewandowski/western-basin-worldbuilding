"""Build Phase 6B qualitative ecological dependencies, disturbances, and resilience."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[3]
NETWORKS=ROOT/'data/processed/networks'; ANALYSIS=ROOT/'data/processed/analysis'; MAPS=ROOT/'outputs/maps/systems'; REPORTS=ROOT/'reports'; GPKG=ROOT/'data/processed/glasspunk_base.gpkg'
DEP=NETWORKS/'ecology_dependency_edges.csv'; DIST=ANALYSIS/'ecological_disturbance_register.csv'; RES=ANALYSIS/'ecological_resilience_matrix.csv'; MAP=MAPS/'21_ecological_dependencies_disturbances_2026'; MAN=REPORTS/'ecological_dependency_manifest.json'

DEP_COLS=['dependency_id','source_node_id','dependent_node_id','ecological_component','dependency_type','ecological_function','relationship_basis','dependency_strength','evidence_quality','source_id','confidence','notes']
DIST_COLS=['disturbance_id','ecological_component','affected_function','disturbance_type','description','relationship_basis','evidence_status','spatial_scope','source_id','confidence','notes']
RES_COLS=['ecological_system','habitat_redundancy','hydrologic_connectivity','spatial_connectivity','restoration_capacity','protected_area_support','mobility_or_recolonization','monitoring_information','disturbance_exposure','evidence_confidence','notes']

DEPS=[
['ECD-001','ECO-001','ECO-016','western_lake_erie_aquatic','hydrologic_dependency','aquatic condition depends on lake and tributary water exchange','documented_hydrography','high','high','usgs_nhdplus_hr','high','Broad water-system dependency; no effect size or scoring.'],
['ECD-002','ECO-016','ECO-002','western_lake_erie_aquatic','nutrient_condition_dependency','HAB condition interface depends on nutrient and water-quality context','documented_water_quality_context','moderate','moderate','epa_lake_erie','moderate','Condition relationship is not quantified causation.'],
['ECD-003','ECO-002','ECO-005','coastal_wetlands_marshes','wetland_dependency','nearshore function depends on coastal wetland interfaces','habitat_dependency','moderate','moderate','usfws_nwi','moderate','Generalized wetland interface; no habitat-quality score.'],
['ECD-004','ECO-005','ECO-008','coastal_wetlands_marshes','habitat_dependency','wetland function depends on contemporary wetland network','documented_wetland_inventory','high','high','usfws_nwi','high','Inventory presence is not equivalent to condition or redundancy.'],
['ECD-005','ECO-006','ECO-013','migratory_mobile_species','protected_area_dependency','migratory stopover function depends partly on protected coastal habitat','documented_protected_area','moderate','moderate','phase6a_usfws_ottawa_nwr','moderate','Generalized refuge function; no sensitive occurrences.'],
['ECD-006','ECO-003','ECO-004','maumee_tributary_floodplain','connectivity_dependency','tributary and floodplain function depends on river connectivity','documented_hydrography','high','high','usgs_3dhp_all','high','Physical network structure, not animal movement route.'],
['ECD-007','ECO-011','ECO-003','maumee_tributary_floodplain','riparian_dependency','riparian function depends on river/floodplain interface','habitat_dependency','moderate','moderate','usgs_3dhp_all','moderate','Generalized riparian relationship.'],
['ECD-008','ECO-014','ECO-003','migratory_mobile_species','migration_dependency','fish movement function depends on lake-to-tributary connectivity','documented_fishery_context','moderate','moderate','phase6a_glfc_lake_erie_committee','moderate','No passage model, stock size, or precise spawning location.'],
['ECD-009','ECO-009','ECO-008','black_swamp_legacy_agriculture','landscape_dependency','modern agricultural matrix function depends on wetland remnants and drainage context','historical_context_plus_inventory','moderate','moderate','h2ohio_great_black_swamp_history','moderate','Historical legacy is not a modern habitat boundary.'],
['ECD-010','ECO-010','ECO-011','terrestrial_habitat_fragmentation','habitat_dependency','terrestrial mosaic depends on riparian and habitat-edge continuity','generalized_land_cover','moderate','low','phase6a_mrlc_land_cover','low','Broad class relationship; no habitat-quality metric.'],
['ECD-011','ECO-013','ECO-010','migratory_mobile_species','migration_dependency','migratory-bird function depends on connected coastal and terrestrial habitat','documented_ecological_function','moderate','moderate','phase6a_usfws_ottawa_nwr','moderate','Functional network, not flight path.'],
['ECD-012','ECO-015','ECO-010','migratory_mobile_species','habitat_dependency','pollinator function depends on habitat mosaic and flowering edges','generalized_land_cover','low','low','phase6a_mrlc_land_cover','low','No insect inventory or movement route.'],
['ECD-013','ECO-004','ECO-003','maumee_tributary_floodplain','hydrologic_dependency','floodplain ecological function depends on hydrologic connectivity','documented_hydrography','high','high','usgs_3dhp_all','high','Tributary and river structure are linked at a generalized ecological level.'],
['ECD-014','ECO-012','ECO-010','terrestrial_habitat_fragmentation','landscape_dependency','urban edge constrains terrestrial habitat continuity','generalized_land_cover','moderate','moderate','phase6a_mrlc_land_cover','moderate','Broad fragmentation interface; no causal harm claim.'],
['ECD-015','ECO-007','ECO-005','coastal_wetlands_marshes','restoration_dependency','coastal wetland function may be supported by restoration context','documented_wetland_inventory','low','low','usfws_nwi','low','No project boundary or restoration performance is asserted.'],
['ECD-016','ECO-008','ECO-013','migratory_mobile_species','connectivity_dependency','wetland network supports broad migratory stopover function','documented_ecological_function','moderate','moderate','phase6a_usfws_ottawa_nwr','moderate','No exact route is asserted.'],
['ECD-017','ECO-016','ECO-001','western_lake_erie_aquatic','food_web_dependency','aquatic productivity interfaces support fish and plankton functions','documented_monitoring_science','low','low','noaa_hab','low','Conceptual food-web interface; no numerical fish or productivity measure.'],
['ECD-018','ECO-010','ECO-015','migratory_mobile_species','landscape_dependency','pollinator function depends on terrestrial habitat continuity','generalized_land_cover','low','low','phase6a_mrlc_land_cover','low','Generalized habitat function only.'],
]
DISTS=[
['ECDIS-001','western_lake_erie_aquatic','aquatic condition','nutrient_enrichment','Nutrient enrichment is a documented basin-scale pressure context for western Lake Erie.','documented_water_quality_context','documented_context','western Lake Erie / Maumee watershed','epa_lake_erie','high','Presence of pressure does not quantify ecological consequence.'],
['ECDIS-002','western_lake_erie_aquatic','HAB and aquatic productivity','HAB_or_hypoxia_condition','HAB conditions are a recurring ecological-condition interface in the lake system.','documented_monitoring_science','documented_context','western Lake Erie','noaa_hab','high','No current footprint, probability, or effect size is modeled.'],
['ECDIS-003','maumee_tributary_floodplain','river/floodplain function','hydrologic_alteration','Drainage and altered hydrology constrain wetland, floodplain, and tributary interfaces.','historical_context_plus_hydrography','qualified_context','Maumee basin','h2ohio_great_black_swamp_history','moderate','No parcel or ditch-level causal claim.'],
['ECDIS-004','coastal_wetlands_marshes','wetland function','wetland_loss_or_alteration','Wetland loss and alteration are represented as broad contemporary landscape pressures.','documented_wetland_inventory','qualified_context','Western Basin focus window','usfws_nwi','moderate','Inventory does not measure loss rate or condition.'],
['ECDIS-005','terrestrial_habitat_fragmentation','habitat continuity','habitat_fragmentation','Developed and transportation edges constrain broad terrestrial continuity.','generalized_land_cover','qualified_context','Western Basin landscape','phase6a_mrlc_land_cover','moderate','No conservation-priority ranking or damage attribution.'],
['ECDIS-006','black_swamp_legacy_agriculture','wetland/agricultural interface','agricultural_landscape_change','Modern agriculture and drainage represent the legacy working-landscape context.','historical_context_plus_inventory','qualified_context','Former swamp landscape context','h2ohio_great_black_swamp_history','moderate','Does not use the held polygon as a boundary.'],
['ECDIS-007','coastal_wetlands_marshes','shoreline habitat','shoreline_modification','Coastal development and shoreline modification are broad interface pressures.','generalized_land_cover','qualified_context','Lake Erie coastal edge','phase6a_mrlc_land_cover','low','No site-specific impact is inferred.'],

['ECDIS-008','migratory_mobile_species','migratory stopover function','habitat_fragmentation','Fragmentation of coastal habitat can constrain broad stopover function.','documented_protected_area','qualified_context','Western Lake Erie coastal edge','phase6a_usfws_ottawa_nwr','low','Generalized function only; no occurrence or route is asserted.'],

['ECDIS-009','western_lake_erie_aquatic','aquatic condition','climate_sensitive_condition','Aquatic ecological conditions may be climate-sensitive, but Phase 6B does not model future change.','documented_monitoring_science','qualified_context','Western Lake Erie','noaa_hab','low','Current analytical layer only; no climate projection.'],
['ECDIS-010','terrestrial_habitat_fragmentation','habitat mosaic','urban_development','Urban/developed expansion is represented as a broad landscape interface.','generalized_land_cover','qualified_context','Western Basin landscape','phase6a_mrlc_land_cover','moderate','No future projection or quantitative conversion estimate.'],
]
RES_ROWS=[
['western_lake_erie_aquatic','moderate','moderate','moderate','low','low','moderate','moderate','moderate','moderate','Lake/tributary structure and monitoring support remain visible; redundancy and condition are not quantified.'],
['maumee_tributary_floodplain','moderate','high','moderate','moderate','low','moderate','moderate','moderate','moderate','Physical hydrologic structure is strong; ecological continuity and disturbance exposure remain qualified.'],
['coastal_wetlands_marshes','moderate','moderate','moderate','moderate','high','high','moderate','moderate','moderate','NWI and protected refuge context support function; condition and redundancy remain uncertain.'],
['black_swamp_legacy_agriculture','unknown','moderate','low','low','low','moderate','low','high','moderate','Modern matrix is broad and altered; the historical swamp polygon is not used.'],
['terrestrial_habitat_fragmentation','unknown','moderate','low','low','low','moderate','low','moderate','low','Generalized land-cover classes provide context, not habitat-quality measurement.'],
['migratory_mobile_species','moderate','moderate','moderate','moderate','moderate','high','moderate','moderate','moderate','Mobility supports broad functional redundancy, but exact routes and numerical series are absent.'],
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def render_map():
    plt.rcParams['svg.fonttype']='none'
    huc=gpd.read_file(GPKG,layer='water_watersheds_huc8'); lake=gpd.read_file(GPKG,layer='water_lake_erie'); wet=gpd.read_file(GPKG,layer='water_current_wetlands_25ac'); flow=gpd.read_file(GPKG,layer='hydrography_physical'); flow['geometry']=flow.geometry.simplify(0.002,preserve_topology=False)
    fig=plt.figure(figsize=(16,10),facecolor='#f1eadc'); ax=fig.add_axes([.045,.16,.58,.76],facecolor='#e9e1ce')
    huc.boundary.plot(ax=ax,color='#9f967f',linewidth=.45,alpha=.65); lake.plot(ax=ax,color='#a9d7df',edgecolor='#478c9a',linewidth=.8,alpha=.9); wet.plot(ax=ax,color='#6da77c',edgecolor='none',alpha=.42); flow.plot(ax=ax,color='#4a8798',linewidth=.3,alpha=.55)
    ax.scatter([-83.14,-83.22], [41.63,41.69], s=55,c='#7b4f92',marker='^',edgecolor='#f1eadc',linewidth=.8,zorder=5); ax.text(-83.14,41.615,'Ottawa NWR',fontsize=8,color='#4d2e60',ha='center'); ax.text(-83.22,41.72,'Maumee Bay coastal wetland',fontsize=8,color='#4d2e60',ha='center'); ax.text(-83.42,41.72,'Western Lake Erie',fontsize=11,weight='bold',color='#235a68',ha='center'); ax.text(-83.56,41.47,'Maumee River / tributary structure',fontsize=9,color='#285f71',rotation=18,ha='center'); ax.set_xlim(-84.55,-82.55); ax.set_ylim(40.9,42.15); ax.set_axis_off()
    side=fig.add_axes([.665,.07,.30,.85]); side.axis('off'); side.text(.04,.98,'MAP 21 — ECOLOGICAL\nDEPENDENCIES & DISTURBANCES, 2026',va='top',fontsize=14,weight='bold',color='#17384b'); side.text(.04,.86,'Qualitative dependencies and broad disturbance interfaces over the accepted 2026 ecological skeleton. Lines are analytical relationships, not animal routes.',va='top',fontsize=8.5,color='#3f4645',linespacing=1.3)
    side.text(.04,.75,'DEPENDENCY LENS',fontsize=10,weight='bold',color='#17384b'); bullets=['Aquatic condition depends on lake, bay, tributary, and nutrient interfaces','Wetland and migratory functions depend on habitat continuity and protected support','River, riparian, and floodplain functions depend on hydrologic connection','Agricultural and terrestrial matrices remain fragmented and disturbance-exposed','Redundancy and restoration capacity are qualitative and evidence-qualified']
    y=.715
    for b in bullets: side.text(.06,y,'• '+b,fontsize=8.1,color='#3f4645',va='top'); y-=.052
    side.text(.04,.39,'INTERFACES',fontsize=10,weight='bold',color='#17384b'); legend=[Patch(facecolor='#a9d7df',edgecolor='#478c9a',label='Ecological system'),Line2D([0],[0],color='#4a8798',lw=2,label='Hydrologic dependency'),Patch(facecolor='#6da77c',alpha=.6,label='Wetland habitat'),Line2D([0],[0],marker='^',color='w',markerfacecolor='#7b4f92',markersize=8,label='Protected support'),Patch(facecolor='#c56e55',alpha=.75,label='Disturbance interface')]; side.legend(handles=legend,loc='upper left',bbox_to_anchor=(.04,.36),frameon=False,fontsize=8)
    side.text(.04,.20,'BOUNDARIES',fontsize=10,weight='bold',color='#17384b'); side.text(.04,.17,'Concentration is not vulnerability. No ecological-risk score, population model, exact migration route, sensitive species location, unsupported causal claim, or future scenario is modeled. Great Black Swamp remains C — HOLD / noncanonical.',fontsize=7.5,color='#3f4645',va='top',linespacing=1.3)
    fig.savefig(MAP.with_suffix('.png'),dpi=220,bbox_inches='tight',facecolor=fig.get_facecolor()); svg=MAP.with_suffix('.svg'); fig.savefig(svg,bbox_inches='tight',facecolor=fig.get_facecolor(),metadata={'Date':None}); plt.close(fig); svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')

def main():
    DEP.parent.mkdir(parents=True,exist_ok=True); ANALYSIS.mkdir(parents=True,exist_ok=True); MAPS.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(DEPS,columns=DEP_COLS).to_csv(DEP,index=False); pd.DataFrame(DISTS,columns=DIST_COLS).to_csv(DIST,index=False); pd.DataFrame(RES_ROWS,columns=RES_COLS).to_csv(RES,index=False); render_map()
    artifacts=[DEP,DIST,RES,MAP.with_suffix('.png'),MAP.with_suffix('.svg')]
    out={'phase':'6B','generated':'2026-09-02','status':'ecological_dependency_baseline','counts':{'dependency_edges':len(DEPS),'disturbances':len(DISTS),'resilience_rows':len(RES_ROWS)},'artifacts':{str(p.relative_to(ROOT)).replace('\\','/'): {'bytes':p.stat().st_size,'sha256':sha(p)} for p in artifacts}}
    MAN.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out['counts'],indent=2))
if __name__=='__main__': main()
