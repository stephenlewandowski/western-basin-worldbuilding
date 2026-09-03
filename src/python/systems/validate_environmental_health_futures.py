"""Validate Phase 7C qualitative scenario separation and artifacts."""
from pathlib import Path
import pandas as pd,json,hashlib
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
def main():
 s=ROOT/'data/processed/scenarios'; f=ROOT/'outputs/figures';m=ROOT/'outputs/maps/systems';r=ROOT/'reports'
 a=pd.read_csv(s/'environmental_health_scenario_assumptions.csv',dtype=str).fillna(''); n=pd.read_csv(s/'exposure_nodes_scenario.csv',dtype=str).fillna('');e=pd.read_csv(s/'exposure_edges_scenario.csv',dtype=str).fillna('');c=pd.read_csv(s/'exposure_controls_scenario.csv',dtype=str).fillna('');u=pd.read_csv(s/'exposure_uncertainty_scenario.csv',dtype=str).fillna('');x=pd.read_csv(f/'environmental_health_scenarios_comparison.csv',dtype=str).fillna('')
 assert (len(a),len(n),len(e),len(c),len(u),len(x))==(36,30,30,30,30,6)
 assert set(a.scenario_id)=={'A','B','C'} and set(a.scenario_year)=={'2050','2075'}
 assert n.scenario_id.notna().all() and n.scenario_year.notna().all() and n.reality_status.eq('fictional').all()
 text=' '.join(' '.join(map(str,row)) for df in [a,n,e,c,u,x] for row in df.to_numpy()).lower()
 for bad in ['exposure score','dose score','mortality','hospitalization','cancer','epidemiology','mosquito','west nile']: assert bad not in text,bad
 for q in ['25_environmental_health_futures_2050','25b_environmental_health_futures_2075']:
  Image.open(m/(q+'.png')).verify(); root=ET.parse(m/(q+'.svg')).getroot(); assert 'ENVIRONMENTAL HEALTH FUTURES' in ' '.join(root.itertext())
 fm=json.loads((r/'environmental_health_scenario_manifest.json').read_text());assert fm['counts']['assumptions']==36
 for rel,h in fm['artifacts'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
 out={'status':'passed','phase':'7C','assumptions':len(a),'scenario_nodes':len(n),'scenario_edges':len(e),'control_states':len(c),'uncertainty_states':len(u),'comparison_rows':len(x),'maps_25_25b_valid':True,'qualitative_only':True,'baseline_separation':True};(r/'environmental_health_scenario_artifact_check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
