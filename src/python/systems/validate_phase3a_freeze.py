"""Regression guard for the accepted Phase 3A Map 11 and factual tables."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from freeze_hash import assert_portability_self_check, manifest_matches

ROOT = Path(__file__).resolve().parents[3]

def main() -> None:
    manifest = json.loads((ROOT / "reports/phase3a_freeze_manifest.json").read_text(encoding="utf-8"))
    target = "data/processed/networks/energy_system_nodes.csv"
    assert_portability_self_check(ROOT, target, manifest["files"][target]["sha256"])
    for rel, meta in manifest["files"].items():
        path = ROOT / rel
        assert path.exists(), f"Missing frozen artifact: {rel}"
        assert manifest_matches(ROOT, rel, meta["sha256"]), f"Phase 3A freeze changed: {rel}"
    nodes = pd.read_csv(ROOT / "data/processed/networks/energy_system_nodes.csv")
    edges = pd.read_csv(ROOT / "data/processed/networks/energy_system_edges.csv")
    assert len(nodes) == manifest["nodes"] == 18
    assert len(edges) == manifest["edges"] == 17
    print("Phase 3A freeze validation passed: Map 11 and 18-node/17-edge tables unchanged")

if __name__ == "__main__": main()
