"""Validate Phase 2D scenario separation, artifacts, and baseline immutability."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from PIL import Image
import pyogrio

ROOT=Path(__file__).resolve().parents[3]; SCEN=ROOT/"data"/"processed"/"scenarios"; REPORT=ROOT/"reports"/"materials_scenarios_artifact_check.json"
EXPECTED_NODE_SHA="931E94AB4F73011BC4E3FFD37B08A41FFE8634E271EF543B3972C12BDA765E9A"; EXPECTED_EDGE_SHA="10D3875078F33CC255754FDA1FD9BC8D28770E7DC998D6A1713FA9F611EFC3C8"
def req(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def main():
    a=pd.read_csv(SCEN/"materials_scenario_assumptions.csv",keep_default_na=False); n=pd.read_csv(SCEN/"materials_nodes_scenario.csv",keep_default_na=False); e=pd.read_csv(SCEN/"materials_edges_scenario.csv",keep_default_na=False); c=pd.read_csv(SCEN/"materials_corridor_evaluation.csv",keep_default_na=False); s=pd.read_csv(SCEN/"materials_scenario_sources.csv",keep_default_na=False)
    bn=ROOT/"data/processed/networks/materials_system_nodes.csv"; be=ROOT/"data/processed/networks/materials_system_edges.csv"
    req(len(pd.read_csv(bn))==30 and len(pd.read_csv(be))==31,"baseline counts changed"); req(sha(bn)==EXPECTED_NODE_SHA and sha(be)==EXPECTED_EDGE_SHA,"baseline hashes changed")
    req((len(a),len(n),len(e),len(c),len(s))==(30,48,36,6,8),"scenario counts wrong")
    groups={(x,y) for x in ["continuity_resilience","circular_basin","high_convergence"] for y in [2050,2075]}
    for f in (a,n,e,c): req(set(zip(f.scenario_id,f.scenario_year))==groups,"six scenario states incomplete")
    for f,k in [(a,"assumption_id"),(n,"scenario_object_id"),(e,"scenario_object_id")]: req(f[k].is_unique,f"duplicate {k}")
    req(set(n.assumption_id)<=set(a.assumption_id) and set(e.assumption_id)<=set(a.assumption_id),"orphan assumption")
    req(set(e.from_scenario_id)<=set(n.scenario_object_id) and set(e.to_scenario_id)<=set(n.scenario_object_id),"orphan scenario edge")
    for f in (n,e):
        req(set(f.reality_status)=={"fictional"},"future object not fictional"); req(set(f.relationship_basis)=={"scenario_assumption"},"future relationship not assumption"); req(f.plausibility.isin(["high","moderate","exploratory"]).all(),"bad plausibility")
    req(n.latitude.astype(str).eq("").all() and n.longitude.astype(str).eq("").all(),"precise future coordinate entered")
    req(not any(x in e.columns for x in ["quantity","capacity","route_geometry","transport_mode"]),"prohibited quantitative/route field")
    req(not n.object_name.str.contains("beryllium mine|local beryllium extraction",case=False,regex=True).any(),"local beryllium extraction scenario")
    req((c.direct_interfacility_route_edges==0).all() and (~c.hard_corridor_geometry).all(),"corridor overclaimed")
    maps={}
    for stem in ["10_materials_system_2050","10b_materials_system_2075"]:
        png=ROOT/"outputs/maps/systems"/(stem+".png"); svg=png.with_suffix(".svg"); req(png.exists() and svg.exists(),stem+" missing");
        with Image.open(png) as im: req(im.width>=3000 and im.height>=1700,"map raster too small"); maps[stem]=[im.width,im.height]
        ET.parse(svg)
    for ext in ["png","svg"]:
        p=ROOT/"outputs/figures"/f"materials_scenarios_comparison.{ext}"; req(p.exists(),"comparison missing");
        if ext=="svg": ET.parse(p)
    req(len(pyogrio.list_layers(ROOT/"data/processed/glasspunk_base.gpkg"))==16,"GeoPackage changed")
    result={"status":"pass","counts":{"assumptions":len(a),"scenario_nodes":len(n),"scenario_edges":len(e),"scenario_states":6},"baseline":{"nodes":30,"edges":31,"node_sha256":sha(bn),"edge_sha256":sha(be),"immutable":True},"corridor_result":"B — CORRIDOR EMERGES WEAKLY","maps":maps,"constraints":{"no_future_coordinates":True,"no_future_quantities":True,"no_corridor_polygon":True,"no_local_beryllium_extraction":True}}
    REPORT.write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result,indent=2))
if __name__=="__main__": main()
