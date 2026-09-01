"""Regression guard for the accepted Phase 3A Map 11 and factual tables."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]

def sha(path: Path) -> str:
    h = hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main() -> None:
    manifest = json.loads((ROOT / "reports/phase3a_freeze_manifest.json").read_text(encoding="utf-8"))
    for rel, meta in manifest["files"].items():
        path = ROOT / rel
        assert path.exists(), f"Missing frozen artifact: {rel}"
        assert sha(path) == meta["sha256"], f"Phase 3A freeze changed: {rel}"
    nodes = pd.read_csv(ROOT / "data/processed/networks/energy_system_nodes.csv")
    edges = pd.read_csv(ROOT / "data/processed/networks/energy_system_edges.csv")
    assert len(nodes) == manifest["nodes"] == 18
    assert len(edges) == manifest["edges"] == 17
    print("Phase 3A freeze validation passed: Map 11 and 18-node/17-edge tables unchanged")

if __name__ == "__main__": main()
