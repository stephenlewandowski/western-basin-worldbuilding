"""Validate Phase 9B qualitative climate dependencies, compounds, and controls."""
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from PIL import Image
from freeze_hash import manifest_matches
ROOT=Path(__file__).resolve().parents[3]; N=ROOT/'data/processed/networks'; A=ROOT/'data/processed/analysis'; M=ROOT/'outputs/maps/systems'; R=ROOT/'reports'
QUAL={'strong','moderate','limited','unknown','not_applicable'}

def read(p): return pd.read_csv(p,dtype=str).fillna('')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check_9a():
 man=json.loads((R/'climate_hazard_baseline_manifest.json').read_text(encoding='utf-8'))
 for rel,meta in man['artifacts'].items(): assert manifest_matches(ROOT,rel,meta['sha256']),rel
 return len(man['artifacts'])
def main():
 dep=read(N/'climate_hazard_dependency_edges.csv'); reg=read(A/'climate_hazard_dependency_register.csv'); comp=read(A/'climate_compound_event_register.csv'); ctl=read(A/'climate_resilience_control_register.csv'); mat=read(A/'climate_hazard_dependency_matrix.csv'); src=read(A/'climate_dependency_sources.csv'); base=read(N/'climate_hazard_nodes.csv')
 assert len(dep)==24 and dep.dependency_id.is_unique; assert len(reg)==24 and reg.dependency_id.is_unique; assert len(comp)==9 and comp.compound_id.is_unique; assert len(ctl)==12 and ctl.control_id.is_unique; assert len(mat)==9; assert len(src)==11 and src.source_id.is_unique
 assert dep.hazard_node_id.isin(set(base.node_id)).all(); assert reg.hazard_node_id.isin(set(base.node_id)).all(); assert dep.source_id.isin(set(src.source_id)|set(read(A/'climate_hazard_sources.csv').source_id)).all(); assert reg.source_id.isin(set(src.source_id)|set(read(A/'climate_hazard_sources.csv').source_id)).all(); assert comp.source_id.isin(set(src.source_id)|set(read(A/'climate_hazard_sources.csv').source_id)).all(); assert ctl.source_id.isin(set(src.source_id)|set(read(A/'climate_hazard_sources.csv').source_id)).all()
 assert dep.dependency_strength.isin(QUAL).all(); assert dep.monitoring_strength.isin(QUAL).all(); assert dep.warning_capacity.isin(QUAL).all(); assert dep.spatial_certainty.isin(QUAL).all(); assert dep.temporal_certainty.isin(QUAL).all()
 assert reg.dependency_strength.isin(QUAL).all(); assert comp.observed_or_plausible.isin({'historically_documented','physically_plausible_pathway','documented_mechanism_plus_plausible_pathway'}).all(); assert comp.confidence.isin({'high','moderate','limited','unknown'}).all(); assert ctl.confidence.isin({'high','moderate','limited','unknown'}).all()
 assert mat.iloc[:,1:-1].stack().isin(QUAL).all()
 for frame in [dep,reg,comp,ctl,mat,src]:
  col='notes' if 'notes' in frame.columns else 'use_limitations' if 'use_limitations' in frame.columns else 'notes'
  assert frame[col].str.len().gt(0).all()
 text=' '.join(' '.join(map(str,row)) for frame in [dep,reg,comp,ctl,mat] for row in frame.to_numpy()).lower(); assert '2050' not in text and '2075' not in text
 assert not re.search(r'(^|,)(probability|risk_score|hazard_score|mortality|dose|social_vulnerability)(,|$)',text)
 assert 'joint probability' in text and 'no joint probability' in text
 assert 'emergency-management model' in text and 'no comprehensive emergency-management model' in text
 with Image.open(M/'30_climate_hazard_dependencies_resilience_2026.png') as im: im.verify(); size=list(im.size)
 svg=' '.join(ET.parse(M/'30_climate_hazard_dependencies_resilience_2026.svg').getroot().itertext()).lower()
 for term in ['map 30','compound pathways','heat + power','precipitation + nutrient','lake level','freeze-thaw','not routes','seiche','not ocean storm surge']: assert term in svg,term
 man=json.loads((R/'climate_dependency_manifest.json').read_text(encoding='utf-8')); assert man['counts']=={'dependency_edges':24,'dependency_register':24,'compound_events':9,'controls':12,'matrix_rows':9}
 for rel,meta in man['artifacts'].items(): assert (ROOT/rel).exists() and sha(ROOT/rel)==meta['sha256'],rel
 protected=check_9a(); result={'status':'passed','phase':'9B','dependency_edges':len(dep),'dependency_register':len(reg),'compound_events':len(comp),'controls':len(ctl),'matrix_rows':len(mat),'map30_valid':True,'phase9a_artifacts_checked':protected,'probabilities_absent':True,'composite_score_absent':True,'phase9a_immutable':True,'health_social_scope_absent':True}; (R/'phase9b_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
