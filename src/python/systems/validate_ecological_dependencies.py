"""Validate Phase 6B ecological dependencies, disturbances, and resilience."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from PIL import Image
from freeze_hash import manifest_matches

ROOT=Path(__file__).resolve().parents[3]; NETWORKS=ROOT/'data/processed/networks'; ANALYSIS=ROOT/'data/processed/analysis'; MAPS=ROOT/'outputs/maps/systems'; REPORTS=ROOT/'reports'
DEP=NETWORKS/'ecology_dependency_edges.csv'; DIST=ANALYSIS/'ecological_disturbance_register.csv'; RES=ANALYSIS/'ecological_resilience_matrix.csv'; MAPPNG=MAPS/'21_ecological_dependencies_disturbances_2026.png'; MAPSVG=MAPS/'21_ecological_dependencies_disturbances_2026.svg'; MAN=REPORTS/'ecological_dependency_manifest.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check_manifest(path):
 m=json.loads(path.read_text());
 for rel,meta in m.get('artifacts',m.get('files',{})).items(): assert manifest_matches(ROOT,rel,meta['sha256']),rel

def main():
 d=pd.read_csv(DEP,dtype=str).fillna(''); x=pd.read_csv(DIST,dtype=str).fillna(''); r=pd.read_csv(RES,dtype=str).fillna(''); n=pd.read_csv(NETWORKS/'ecology_system_nodes.csv',dtype=str).fillna(''); import yaml; sources=set(yaml.safe_load((ROOT/'metadata/sources.yml').read_text())['sources'])
 assert len(d)==18 and d.dependency_id.is_unique; assert len(x)==10 and x.disturbance_id.is_unique; assert len(r)==6 and r.ecological_system.is_unique
 assert d.source_node_id.isin(set(n.node_id)).all() and d.dependent_node_id.isin(set(n.node_id)).all()
 assert d.source_id.isin(sources).all() and x.source_id.isin(sources).all(); assert d.confidence.isin({'low','moderate','high','unknown'}).all(); assert r.iloc[:,1:10].isin({'low','moderate','high','unknown'}).all().all()
 assert d.notes.str.len().gt(0).all() and x.notes.str.len().gt(0).all() and r.notes.str.len().gt(0).all()
 assert x.ecological_component.nunique()==6; assert set(d.ecological_component)=={'western_lake_erie_aquatic','maumee_tributary_floodplain','coastal_wetlands_marshes','black_swamp_legacy_agriculture','terrestrial_habitat_fragmentation','migratory_mobile_species'}
 text=' '.join(' '.join(map(str,row)) for f in [d,x,r] for row in f.to_numpy())
 assert not re.search(r'2050|2075|scenario|\bpopulation\b|\bextinction\b|\babundance\b|species richness|exact (?:animal|migration|flight) route|vulnerability score|risk score|\bnest\b|\broost\b|\bden\b|\bdisease\b|malaria|arbovirus',text,re.I)
 assert 'Great Black Swamp' not in text or 'polygon' in text
 check_manifest(ROOT/'reports/phase3a_freeze_manifest.json'); check_manifest(ROOT/'reports/phase3b_freeze_manifest.json'); check_manifest(ROOT/'reports/phase4b_information_freeze_manifest.json'); check_manifest(ROOT/'reports/phase4c_information_freeze_manifest.json'); check_manifest(ROOT/'reports/phase5a_freight_freeze_manifest.json'); check_manifest(ROOT/'reports/phase5b_freight_evidence_freeze_manifest.json'); check_manifest(ROOT/'reports/phase5c_freight_dependency_freeze_manifest.json'); check_manifest(ROOT/'reports/phase6a_ecology_freeze_manifest.json')
 prior=json.loads((ROOT/'reports/phase5a_prior_map_hashes.json').read_text())['files']; assert len(prior)==38
 for rel,val in prior.items(): assert manifest_matches(ROOT,rel,val)
 m=json.loads(MAN.read_text()); assert m['counts']=={'dependency_edges':18,'disturbances':10,'resilience_rows':6}
 for rel,meta in m['artifacts'].items(): p=ROOT/rel; assert p.exists() and p.stat().st_size>100 and sha(p)==meta['sha256']
 with Image.open(MAPPNG) as im: im.verify(); size=list(im.size)
 ET.parse(MAPSVG); svg=' '.join(''.join(e.itertext()) for e in ET.parse(MAPSVG).getroot().iter() if e.tag.endswith('text'))
 for q in ['MAP 21','DEPENDENCIES','DISTURBANCES','Great Black Swamp','No ecological-risk score']: assert q.lower() in svg.lower(),q
 result={'status':'passed','phase':'6B','dependency_edges':len(d),'disturbances':len(x),'resilience_dimensions':[len(r),len(r.columns)-1],'map21_valid':True,'phase6a_frozen':True,'prior_maps_01_20_unchanged':True,'no_quantitative_risk':True,'no_sensitive_locations':True,'no_future_scenarios':True,'no_exact_routes':True,'image_size':size}; print(json.dumps(result,indent=2)); (REPORTS/'ecological_dependency_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__': main()
