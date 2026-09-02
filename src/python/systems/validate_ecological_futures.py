"""Validate qualitative Phase 6C ecological futures and baseline separation."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from PIL import Image
from freeze_hash import manifest_matches
ROOT=Path(__file__).resolve().parents[3]; S=ROOT/'data/processed/scenarios'; F=ROOT/'outputs/figures'; M=ROOT/'outputs/maps/systems'; R=ROOT/'reports'
A=S/'ecology_scenario_assumptions.csv'; N=S/'ecology_nodes_scenario.csv'; E=S/'ecology_edges_scenario.csv'; D=S/'ecological_disturbance_scenario.csv'; Q=S/'ecological_resilience_scenario.csv'; C=F/'ecological_scenarios_comparison.csv'

def check_manifest(p):
 m=json.loads(p.read_text());
 for rel,meta in m.get('artifacts',m.get('files',{})).items(): assert manifest_matches(ROOT,rel,meta['sha256']),rel

def main():
 a=pd.read_csv(A,dtype=str).fillna(''); n=pd.read_csv(N,dtype=str).fillna(''); e=pd.read_csv(E,dtype=str).fillna(''); d=pd.read_csv(D,dtype=str).fillna(''); q=pd.read_csv(Q,dtype=str).fillna(''); c=pd.read_csv(C,dtype=str).fillna('')
 states={'A2050','A2075','B2050','B2075','C2050','C2075'}; comps={'western_lake_erie_aquatic','maumee_tributary_floodplain','coastal_wetlands_marshes','black_swamp_legacy_agriculture','terrestrial_habitat_fragmentation','migratory_mobile_species'}
 assert len(a)==18 and len(n)==36 and len(e)==30 and len(d)==36 and len(q)==36 and len(c)==72
 assert set(a.scenario_id)==states and set(n.scenario_id)==states and set(c.scenario_id)==states
 assert a.groupby('scenario_id').size().eq(3).all() and n.groupby('scenario_id').size().eq(6).all() and e.groupby('scenario_id').size().eq(5).all() and d.groupby('scenario_id').size().eq(6).all() and q.groupby('scenario_id').size().eq(6).all() and c.groupby('scenario_id').size().eq(12).all()
 assert set(n.ecological_component)==comps and set(d.ecological_component)==comps and set(q.ecological_component)==comps
 assert n.reality_status.eq('fictional').all() and n.relationship_basis.eq('scenario_assumption').all() and e.reality_status.eq('fictional').all()
 assert n.baseline_object_id.str.startswith('ECO-').all() and n.source_id.str.len().gt(0).all(); assert e.from_object_id.isin(set(n.object_id)).all() and e.to_object_id.isin(set(n.object_id)).all()
 assert a.plausibility.isin({'high','moderate','exploratory'}).all() and n.plausibility.isin({'high','moderate','exploratory'}).all()
 assert c.level.isin({'low','moderate','high'}).all()
 text=' '.join(' '.join(map(str,row)) for x in [a,n,e,d,q,c] for row in x.to_numpy())
 assert not re.search(r'\b(?:[0-9][0-9,]*(?:\.\d+)?\s*(?:MW|MGD|tons?|trucks?|railcars?|vessels?|percent|%))\b|\b(?:extinction|malaria|arbovirus|mosquito transmission|exact (?:migration|animal|flight|spawning) route)\b|precise (?:nest|roost|den|spawning) location',text,re.I)
 assert not re.search(r'Great Black Swamp.{0,100}(?:polygon|boundary)',text,re.I)
 check_manifest(R/'phase3a_freeze_manifest.json'); check_manifest(R/'phase3b_freeze_manifest.json'); check_manifest(R/'phase4b_information_freeze_manifest.json'); check_manifest(R/'phase4c_information_freeze_manifest.json'); check_manifest(R/'phase5a_freight_freeze_manifest.json'); check_manifest(R/'phase5b_freight_evidence_freeze_manifest.json'); check_manifest(R/'phase5c_freight_dependency_freeze_manifest.json'); check_manifest(R/'phase6a_ecology_freeze_manifest.json'); check_manifest(R/'phase6b_ecological_dependency_freeze_manifest.json')
 prior=json.loads((R/'phase5a_prior_map_hashes.json').read_text())['files']; assert len(prior)==38
 for rel,val in prior.items(): assert manifest_matches(ROOT,rel,val)
 m=json.loads((R/'ecology_scenario_manifest.json').read_text()); assert m['counts']=={'assumptions':18,'scenario_nodes':36,'scenario_edges':30,'disturbance_states':36,'resilience_states':36,'comparison_rows':72}
 for rel,meta in m['artifacts'].items(): p=ROOT/rel; assert p.exists() and p.stat().st_size>100 and hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256']
 sizes=[]
 for p in [M/'22_ecological_futures_2050.png',M/'22b_ecological_futures_2075.png']:
  with Image.open(p) as im: im.verify(); sizes.append(list(im.size))
 texts=[]
 for p in [M/'22_ecological_futures_2050.svg',M/'22b_ecological_futures_2075.svg']:
  root=ET.parse(p).getroot(); texts.append(' '.join(''.join(x.itertext()) for x in root.iter() if x.tag.endswith('text')))
 for t,year in zip(texts,[2050,2075]):
  assert f'{year}' in t and 'Restored Connectivity' in t and 'Managed Working Basin' in t and 'High-Pressure Fragmented Basin' in t
 result={'status':'passed','phase':'6C','assumptions':len(a),'scenario_nodes':len(n),'scenario_edges':len(e),'disturbance_states':len(d),'resilience_states':len(q),'comparison_rows':len(c),'phase6a_immutable':True,'phase6b_immutable':True,'prior_maps_01_21_unchanged':True,'all_scenarios_explicit':True,'no_future_population_values':True,'no_extinction_or_disease':True,'no_sensitive_locations':True,'great_black_swamp_hold_preserved':True,'image_sizes':sizes}; (R/'ecology_scenario_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
