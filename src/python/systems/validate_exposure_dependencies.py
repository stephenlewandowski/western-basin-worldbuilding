"""Independent validation for Phase 7B dependency/control products."""
from pathlib import Path
import hashlib,json,re
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
FAMILIES={'Drinking Water / HAB','Ambient Air','Soil / Groundwater / Legacy Contamination','Food / Fish / Recreational Water','Heat'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 n=ROOT/'data/processed/networks'; a=ROOT/'data/processed/analysis'; m=ROOT/'outputs/maps/systems'; r=ROOT/'reports'
 nodes=pd.read_csv(n/'exposure_context_nodes.csv',dtype=str).fillna('')
 d=pd.read_csv(n/'exposure_dependency_edges.csv',dtype=str).fillna(''); c=pd.read_csv(a/'exposure_control_register.csv',dtype=str).fillna(''); e=pd.read_csv(a/'exposure_evidence_strength_register.csv',dtype=str).fillna(''); x=pd.read_csv(a/'exposure_dependency_control_matrix.csv',dtype=str).fillna('')
 assert len(d)==20 and len(c)==7 and len(e)==5 and x.shape==(5,11)
 assert set(c.pathway_family)==set(FAMILIES) and c.control_type.ne('').all() and c.source_id.ne('').all()
 assert d.dependency_id.is_unique and c.control_id.is_unique and e.pathway_id.is_unique
 assert set(d.pathway_family)==set(e.pathway_family)==set(x.pathway_family)=={'Drinking Water / HAB','Ambient Air','Soil / Groundwater / Legacy Contamination','Food / Fish / Recreational Water','Heat'}
 node_family=dict(zip(nodes.node_id,nodes.pathway_family))
 family_map={'drinking_water_hab':'Drinking Water / HAB','ambient_air':'Ambient Air','legacy_contamination':'Soil / Groundwater / Legacy Contamination','food_fish_recreation':'Food / Fish / Recreational Water','heat':'Heat'}
 assert all(family_map[node_family[row.source_node_id]]==row.pathway_family and family_map[node_family[row.dependent_node_id]]==row.pathway_family for _,row in d.iterrows())
 allowed={'strong','moderate','limited','unknown','not_applicable'}
 assert d.evidence_strength.isin(allowed).all(); assert x.iloc[:,1:].isin(allowed).all().all()
 assert e.exposure_confirmation.eq('unconfirmed').all() and e.dose_information.eq('unknown').all() and e.health_outcome_information.eq('unknown').all()
 assert d.source_id.astype(bool).all() and c.source_id.astype(bool).all() and e.source_id.astype(bool).all()
 text=' '.join(' '.join(map(str,row)) for df in [d,c,e,x] for row in df.to_numpy()).lower()
 for forbidden in ['exposure score','dose score','disease model','epidemiology','mosquito','vector','infectious','disease','probability']: assert forbidden not in text, forbidden
 fm=json.loads((r/'phase7a_exposure_environmental_health_freeze_manifest.json').read_text()); assert fm['status']=='ACCEPTED / FROZEN'
 for rel,h in fm['artifacts'].items(): assert sha(ROOT/rel)==h,(rel,'freeze mismatch')
 mm=m/'24_exposure_dependencies_controls_2026.png'; sv=m/'24_exposure_dependencies_controls_2026.svg'; Image.open(mm).verify(); root=ET.parse(sv).getroot(); svg=' '.join(root.itertext()); assert all(q in svg for q in ['MAP 24','Environmental condition','Evidence gap'])
 out={'status':'passed','phase':'7B','dependency_edges':len(d),'control_register':len(c),'evidence_register':len(e),'matrix_dimensions':list(x.shape),'map24_valid':True,'phase7a_immutable':True,'no_exposure_score':True,'no_dose_or_health_model':True}; (r/'exposure_dependency_artifact_check.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
