"""Validate Phase 9C projection-led qualitative climate futures."""
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from PIL import Image
from freeze_hash import manifest_matches
ROOT=Path(__file__).resolve().parents[3]; A=ROOT/'data/processed/analysis'; S=ROOT/'data/processed/scenarios'; M=ROOT/'outputs/maps/systems'; F=ROOT/'outputs/figures'; R=ROOT/'reports'
QUAL={'high','moderate','limited','unknown'}
def read(p): return pd.read_csv(p,dtype=str).fillna('')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check_manifest(path):
 m=json.loads(path.read_text(encoding='utf-8'))
 for rel,meta in m['artifacts'].items(): assert manifest_matches(ROOT,rel,meta['sha256']),rel
 return len(m['artifacts'])
def main():
 proj=read(A/'climate_projection_evidence.csv'); src=read(A/'climate_scenario_sources.csv'); ass=read(S/'climate_scenario_assumptions.csv'); haz=read(S/'climate_scenario_hazard_states.csv'); dep=read(S/'climate_scenario_dependency_states.csv'); res=read(S/'climate_scenario_resilience_states.csv'); cp=read(S/'climate_compound_event_scenario_states.csv'); comp=read(F/'climate_scenario_comparison.csv')
 assert len(proj)==12 and proj.projection_id.is_unique; assert len(src)==13 and src.source_id.is_unique; assert len(ass)==36 and ass.assumption_id.is_unique; assert len(haz)==36 and haz.state_id.is_unique; assert len(dep)==48 and dep.state_id.is_unique; assert len(res)==48 and res.state_id.is_unique; assert len(cp)==54 and cp.state_id.is_unique; assert len(comp)==6 and comp.scenario_id.is_unique
 allowed_scen={'A','B','C'}; allowed_horiz={2050,2075}; ids={f'{s}{y}' for s in allowed_scen for y in allowed_horiz}; source_ids=set(src.source_id); assert set(ass.scenario_id)==allowed_scen and set(ass.scenario_year.astype(int))==allowed_horiz; assert set(haz.scenario_id+'') <= ids and set(dep.scenario_id+'') <= ids and set(res.scenario_id+'') <= ids and set(cp.scenario_id+'') <= ids
 assert ass.source_id.isin(source_ids).all() and proj.source_id.isin(source_ids).all(); assert haz.source_id.isin(source_ids).all() and dep.source_id.isin(source_ids).all() and res.source_id.isin(source_ids).all() and cp.source_id.isin(source_ids).all()
 assert ass.reality_status.eq('fictional').all() and haz.reality_status.eq('fictional').all() and dep.reality_status.eq('fictional').all() and res.reality_status.eq('fictional').all() and cp.reality_status.eq('fictional').all()
 assert ass.plausibility.isin(QUAL).all() and ass.uncertainty.isin(QUAL).all(); assert haz.plausibility.isin(QUAL).all() and dep.plausibility.isin(QUAL).all() and res.plausibility.isin(QUAL).all() and cp.plausibility.isin(QUAL).all()
 assert set(proj.observed_or_modeled) <= {'modeled_projection','model_metadata'} and proj.confidence.isin(QUAL).all(); assert proj.value.str.len().gt(0).all(); assert (~proj.projection_period.str.fullmatch('2075')).all()
 for frame in (ass,haz,dep,res,cp,comp,proj,src):
  for column in ('notes','limitations'):
   if column in frame: assert frame[column].str.len().gt(0).all()
 text=' '.join(' '.join(map(str,row)) for frame in (proj,ass,haz,dep,res,cp,comp) for row in frame.to_numpy()).lower(); fields=set(proj.columns)|set(ass.columns)|set(haz.columns)|set(dep.columns)|set(res.columns)|set(cp.columns)|set(comp.columns)
 assert not fields & {'probability','risk_score','hazard_score','mortality','disease_incidence','dose','social_vulnerability','shoreline_position','outage_probability'}
 assert 'no probability' in text and 'not a 2075 point estimate' in text
 assert not re.search(r'(?:future|scenario)[ _-](?:tornado|hail|outage|damage|shoreline)[ _-]?(?:count|probability|position)\s*[,=:]\s*[0-9]',text)
 for base in ['31_climate_hazard_futures_2050','31b_climate_hazard_futures_2075']:
  with Image.open(M/(base+'.png')) as im: im.verify(); size=list(im.size)
  svg=' '.join(ET.parse(M/(base+'.svg')).getroot().itertext()).lower()
  for term in ['map '+('31' if '31_' in base else '31b'),'adaptive / buffered basin','managed variable basin','compound hazard basin','not hazard zones','seiche']: assert term in svg,term
  if '31b_' in base: assert 'not a 2075 point estimate' in svg
 man=json.loads((R/'climate_scenario_manifest.json').read_text(encoding='utf-8')); assert man['counts']=={'projection_records':12,'assumptions':36,'hazard_states':36,'dependency_states':48,'resilience_states':48,'compound_event_states':54,'comparison_rows':6}
 for rel,meta in man['artifacts'].items(): assert (ROOT/rel).exists() and sha(ROOT/rel)==meta['sha256'],rel
 prior=check_manifest(R/'climate_hazard_baseline_manifest.json')+check_manifest(R/'climate_dependency_manifest.json'); assert prior==23
 result={'status':'passed','phase':'9C','projection_records':len(proj),'assumptions':len(ass),'hazard_states':len(haz),'dependency_states':len(dep),'resilience_states':len(res),'compound_event_states':len(cp),'comparison_rows':len(comp),'map31_valid':True,'map31b_valid':True,'phase9a_9b_artifacts_checked':prior,'future_probabilities_absent':True,'baseline_immutability':True,'no_health_social_scoring':True,'late_century_not_relabelled_2075':True}; (R/'phase9c_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
