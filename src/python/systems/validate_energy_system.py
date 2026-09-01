"""Validate Phase 3A artifacts and regression guards."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]

def digest(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    nodes=pd.read_csv(ROOT/"data/processed/networks/energy_system_nodes.csv")
    edges=pd.read_csv(ROOT/"data/processed/networks/energy_system_edges.csv")
    sources=pd.read_csv(ROOT/"data/processed/networks/energy_system_sources.csv")
    assert nodes.node_id.is_unique and edges.edge_id.is_unique
    assert set(edges.from_node_id)|set(edges.to_node_id) <= set(nodes.node_id)
    assert nodes.source_id.isin(sources.source_id).all() and edges.source_id.isin(sources.source_id).all()
    corroborating=nodes.corroborating_source_id.dropna()
    assert corroborating.isin(sources.source_id).all()
    expected={"generation":9,"grid":2,"storage":2,"major_load":4,"compute":1}
    assert nodes.node_type.value_counts().to_dict()==expected
    assert len(nodes)==18 and len(edges)==17
    assert len(nodes[(nodes.node_type=="generation")&(nodes.asset_class=="nuclear")])==2
    assert len(nodes[(nodes.node_type=="generation")&(nodes.asset_class=="fossil")])==4
    assert len(nodes[(nodes.node_type=="generation")&(nodes.asset_class=="renewable")])==3
    assert nodes.loc[nodes.node_id=="ENE-EIA-1729","capacity_mw"].iloc[0]==1141
    assert nodes.loc[nodes.node_type=="major_load","capacity_mw"].isna().all()
    compute=nodes[nodes.node_type=="compute"].iloc[0]
    assert compute.status_2026=="permitted_or_planned_unverified_operation" and compute.capacity_mw==5
    assert edges.notes.str.contains("Not a feeder").all()
    png=ROOT/"outputs/maps/systems/11_energy_grid_compute_baseline_2026.png"
    svg=png.with_suffix(".svg")
    assert png.stat().st_size>100_000 and svg.stat().st_size>50_000
    with Image.open(png) as im: im.verify()
    ET.parse(svg)
    # Keep the Phase 3A regression set limited to Maps 01–10b; Phase 3B's
    # newly added Map 12 is validated by validate_energy_dependencies.py.
    map_hashes={p.name:digest(p) for p in sorted((ROOT/"outputs/maps/systems").glob("*.png")) if not p.name.startswith(("11_","12_"))}
    baseline=json.loads((ROOT/"reports/phase3a_preflight_map_hashes.json").read_text(encoding="utf-8"))
    assert map_hashes==baseline, "Maps 01-10b changed"
    report={"status":"passed","counts":expected|{"nodes":len(nodes),"edges":len(edges)},
            "classification_gates":{"compute_status_qualified":"passed","major_load_demand_not_invented":"passed","power_flow_claim_absent":"passed"},
            "maps_01_10b_unchanged":True,"map11":{"png_bytes":png.stat().st_size,"svg_bytes":svg.stat().st_size}}
    (ROOT/"reports/energy_system_artifact_check.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
