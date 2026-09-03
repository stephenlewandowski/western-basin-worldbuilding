"""Validate Phase 8A-8C biogeochemical products and qualitative boundaries."""
from __future__ import annotations
import hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
N=ROOT/'data/processed/networks'; A=ROOT/'data/processed/analysis'; S=ROOT/'data/processed/scenarios'; M=ROOT/'outputs/maps/systems'; F=ROOT/'outputs/figures'; R=ROOT/'reports'

def read(p): return pd.read_csv(p,dtype=str).fillna('')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 nodes=read(N/'biogeochemical_system_nodes.csv'); edges=read(N/'biogeochemical_flux_edges.csv'); q=read(A/'biogeochemical_quantitative_fluxes.csv'); src=read(N/'biogeochemical_system_sources.csv'); deps=read(N/'biogeochemical_dependency_edges.csv'); controls=read(A/'biogeochemical_control_register.csv'); matrix=read(A/'biogeochemical_dependency_matrix.csv'); ass=read(S/'biogeochemical_scenario_assumptions.csv'); sn=read(S/'biogeochemical_nodes_scenario.csv'); se=read(S/'biogeochemical_edges_scenario.csv'); sc=read(S/'biogeochemical_controls_scenario.csv'); su=read(S/'biogeochemical_uncertainty_scenario.csv'); comp=read(F/'biogeochemical_scenarios_comparison.csv')
 assert len(nodes)==18 and nodes.node_id.is_unique and {'reality_status','canon_status'}.issubset(nodes.columns)
 assert len(edges)==24 and edges.edge_id.is_unique and edges.from_id.isin(set(nodes.node_id)).all() and edges.to_id.isin(set(nodes.node_id)).all() and {'reality_status','canon_status'}.issubset(edges.columns)
 assert len(q)==10 and q.flux_id.is_unique and q.source_id.isin(set(src.source_id)).all()
 assert len(deps)==22 and deps.dependency_id.is_unique and deps.source_node_id.isin(set(nodes.node_id)).all() and deps.dependent_node_id.isin(set(nodes.node_id)).all()
 assert len(controls)==10 and controls.control_id.is_unique and len(matrix)==8
 assert len(ass)==36 and len(sn)==48 and len(se)==42 and len(sc)==48 and len(su)==48 and len(comp)==6
 assert set(ass.scenario_id)=={'A','B','C'} and set(ass.scenario_year)=={'2050','2075'}
 assert sn.reality_status.eq('fictional').all() and se.reality_status.eq('fictional').all() and sc.reality_status.eq('fictional').all()
 assert set(matrix.iloc[:,1:-1].stack()) <= {'strong','moderate','limited','unknown','not_applicable'}
 text=' '.join(' '.join(map(str,row)) for df in [nodes,edges,q,deps,controls,matrix,ass,sn,se,sc,su,comp] for row in df.to_numpy()).lower()
 for bad in ['future concentration','future hab magnitude','crop yield','removal percentage','greenhouse-gas inventory','predictive hab model','private landowner','composite score','worst area']:
  assert bad not in text,bad
 for base in ['26_biogeochemical_nutrient_flux_system_2026','27_biogeochemical_dependencies_controls_2026','28_biogeochemical_futures_2050','28b_biogeochemical_futures_2075']:
  png=M/(base+'.png'); svg=M/(base+'.svg'); Image.open(png).verify(); root=ET.parse(svg).getroot(); svgtext=' '.join(root.itertext()); assert len(svgtext)>100,base
 manifest=json.loads((R/'biogeochemical_module_manifest.json').read_text()); assert manifest['counts']['baseline_nodes']==18 and manifest['counts']['quantitative_records']==10 and manifest['counts']['dependencies']==22
 for rel,h in manifest['artifacts'].items(): assert sha(ROOT/rel)==h,rel
 prior=subprocess.run(['git','diff','--name-only','main'],cwd=ROOT,capture_output=True,text=True,check=False).stdout.splitlines()
 assert not any('data/processed/networks/exposure_' in p or 'outputs/maps/systems/25_' in p or 'outputs/maps/systems/25b_' in p for p in prior)
 result={'status':'passed','phase':'8A-8C','baseline_nodes':len(nodes),'baseline_edges':len(edges),'quantitative_records':len(q),'dependencies':len(deps),'controls':len(controls),'matrix_rows':len(matrix),'scenario_assumptions':len(ass),'scenario_nodes':len(sn),'scenario_edges':len(se),'scenario_controls':len(sc),'scenario_uncertainty':len(su),'comparison_rows':len(comp),'maps_26_27_28_28b_valid':True,'qualitative_future_only':True,'phase7_immutability_check':True,'no_unsupported_future_quantities':True,'no_predictive_hab_model':True}
 (R/'biogeochemical_artifact_check.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
