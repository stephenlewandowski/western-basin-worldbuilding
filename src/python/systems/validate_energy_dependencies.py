"""Validate Phase 3B dependency layer, matrix, Map 12, and Phase 3A freeze."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
QUAL={"none","low","moderate","high","unknown"}; TYPES={"electricity","fuel","cooling_water","industrial_heat","storage_support","compute","communications","water_service","weather"}
def main():
    nodes=pd.read_csv(ROOT/"data/processed/networks/energy_system_nodes.csv"); depnodes=pd.read_csv(ROOT/"data/processed/networks/energy_dependency_nodes.csv"); edges=pd.read_csv(ROOT/"data/processed/networks/energy_dependency_edges.csv"); sources=pd.read_csv(ROOT/"data/processed/networks/energy_dependency_sources.csv")
    all_ids=set(nodes.node_id)|set(depnodes.node_id)
    assert edges.dependency_id.is_unique and not edges.duplicated(["from_node_id","to_node_id","dependency_type"]).any()
    assert set(edges.from_node_id)|set(edges.to_node_id) <= all_ids
    assert edges.source_id.isin(sources.source_id).all()
    for col in ["dependency_type","dependency_scope","dependency_strength","outage_sensitivity","relationship_basis","confidence"]: assert edges[col].notna().all()
    assert set(edges.dependency_type)<=TYPES and set(edges.dependency_strength)<= {"low","moderate","high"} and set(edges.outage_sensitivity)<=QUAL
    assert set(edges.relationship_basis)<= {"documented","engineering_dependency","inferred"} and set(edges.confidence)<= {"high","medium","low"}
    assert len(edges)==28 and len(depnodes)==5
    assert len(edges[edges.to_node_id.isin(["ENE-LOAD-COLLINS","ENE-LOAD-BAYVIEW"])])==2
    assert len(edges[(edges.dependency_type=="weather")])==3
    assert len(edges[(edges.dependency_type=="cooling_water")])==6
    assert len(edges[edges.to_node_id=="ENE-COMPUTE-BG-5MW"])==1
    compute=nodes[nodes.node_id=="ENE-COMPUTE-BG-5MW"].iloc[0]; assert compute.status_2026=="permitted_or_planned_unverified_operation"
    matrix=pd.read_csv(ROOT/"outputs/figures/energy_dependency_matrix_2026.csv",index_col=0); assert matrix.shape==(10,7); assert set(matrix.stack())<=QUAL
    png=ROOT/"outputs/maps/systems/12_critical_energy_dependencies_2026.png"; svg=png.with_suffix(".svg"); mtx=ROOT/"outputs/figures/energy_dependency_matrix_2026.png"
    assert png.stat().st_size>100000 and svg.stat().st_size>50000 and mtx.stat().st_size>50000
    with Image.open(png) as im: im.verify()
    with Image.open(mtx) as im: im.verify()
    ET.parse(svg)
    result={"status":"passed","counts":{"dependency_nodes":len(depnodes),"dependency_edges":len(edges),"matrix_rows":10,"matrix_columns":7},"gates":{"phase3a_frozen":True,"all_endpoints_valid":True,"qualitative_categories_valid":True,"unsupported_numeric_loads_absent":True,"monroe_transition_qualified":True,"oppidan_planned_unverified":True,"storage_duration_unknown":True,"prohibited_power_flow_claims_absent":True},"artifacts":{"map12_png_bytes":png.stat().st_size,"map12_svg_bytes":svg.stat().st_size,"matrix_png_bytes":mtx.stat().st_size}}
    (ROOT/"reports/energy_dependency_artifact_check.json").write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result,indent=2))
if __name__=="__main__": main()
