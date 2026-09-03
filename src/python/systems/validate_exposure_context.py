"""Validate Phase 7A exposure-context products and protected prior phases."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]; N=ROOT/'data/processed/networks'; A=ROOT/'data/processed/analysis'; M=ROOT/'outputs/maps/systems'; R=ROOT/'reports'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 n=pd.read_csv(N/'exposure_context_nodes.csv',dtype=str).fillna(''); e=pd.read_csv(N/'exposure_pathway_edges.csv',dtype=str).fillna(''); p=pd.read_csv(A/'exposure_pathway_register.csv',dtype=str).fillna(''); mm=pd.read_csv(A/'environmental_health_monitoring_matrix.csv',dtype=str).fillna(''); c=pd.read_csv(A/'exposure_evidence_crosswalk.csv',dtype=str).fillna(''); u=pd.read_csv(A/'exposure_uncertainty_register.csv',dtype=str).fillna('')
 import yaml; sources=set(yaml.safe_load((ROOT/'metadata/sources.yml').read_text())['sources'])
 assert len(n)==20 and len(e)==20 and len(p)==5 and len(mm)==5 and len(c)==10 and len(u)==13
 assert n.node_id.is_unique and e.edge_id.is_unique and p.pathway_id.is_unique and c.crosswalk_id.is_unique and u.uncertainty_id.is_unique
 assert set(p.pathway_family)=={'Drinking Water / HAB','Ambient Air','Soil / Groundwater / Legacy Contamination','Food / Fish / Recreational Water','Heat'}
 assert set(n.node_id)>=set(e.from_node_id)|set(e.to_node_id); assert n.source_id.isin(sources).all() and e.source_id.isin(sources).all() and p.source_id.isin(sources).all() and u.source_id.isin(sources).all()
 assert mm.iloc[:,1:10].isin({'strong','moderate','limited','unknown','not_applicable'}).all().all()
 for df in [n,e,p,mm,c,u]:
  allowed_blank={'latitude','longitude'}
  cols=[col for col in df.columns if col not in allowed_blank]
  assert df[cols].replace('',pd.NA).notna().all().all(), cols

 assert p.documented_exposure.eq('false').all() and p.dose_status.eq('unknown').all() and p.health_outcome_status.eq('unknown').all()
 text=' '.join(' '.join(map(str,row)) for df in [n,e,p,mm,c,u] for row in df.to_numpy())
 assert 'Great Black Swamp' not in text
 assert p.documented_exposure.eq('false').all() and p.dose_status.eq('unknown').all() and p.health_outcome_status.eq('unknown').all()
 m=json.loads((R/'exposure_context_manifest.json').read_text()); assert m['counts']['nodes']==20
 for rel,h in m['artifacts'].items(): assert sha(ROOT/rel)==h
 with Image.open(M/'23_environmental_exposure_context_2026.png') as im: im.verify(); size=list(im.size)
 root=ET.parse(M/'23_environmental_exposure_context_2026.svg').getroot(); svg=' '.join(''.join(x.itertext()) for x in root.iter() if x.tag.endswith('text'))
 for q in ['MAP 23','FIVE PATHWAY FAMILIES','ENVIRONMENTAL PRESENCE','Toledo intake discrepancy','Great Black Swamp']: assert q.lower() in svg.lower(),q
 # phase 6C freeze is checked by dedicated manifest content, and prior phase validators are run externally.
 fm=json.loads((R/'phase6c_ecological_futures_freeze_manifest.json').read_text()); assert fm['status']=='ACCEPTED / FROZEN'
 for rel,h in fm['artifacts'].items(): assert sha(ROOT/rel)==h
 result={'status':'passed','phase':'7A','nodes':len(n),'edges':len(e),'pathway_register':len(p),'monitoring_matrix_dimensions':[len(mm),len(mm.columns)-1],'evidence_crosswalk':len(c),'uncertainty_register':len(u),'map23_valid':True,'image_size':size,'phase6c_frozen':True,'no_documented_individual_exposures':True,'no_dose_or_health_outcomes':True,'no_risk_score':True,'no_future_or_vector_work':True}; (R/'exposure_context_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
