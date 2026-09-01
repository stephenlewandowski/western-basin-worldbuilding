"""Validate the accepted/frozen Phase 3B dependency baseline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "reports/phase3b_freeze_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ACCEPTED / FROZEN"
    assert manifest["dependency_nodes"] == 5
    assert manifest["dependency_edges"] == 28
    for rel, meta in manifest["files"].items():
        path = ROOT / rel
        assert path.exists(), rel
        assert path.stat().st_size == meta["bytes"], rel
        assert digest(path) == meta["sha256"], rel
    png = ROOT / "outputs/maps/systems/12_critical_energy_dependencies_2026.png"
    svg = ROOT / "outputs/maps/systems/12_critical_energy_dependencies_2026.svg"
    with Image.open(png) as image:
        image.verify()
    ET.parse(svg)
    print("Phase 3B freeze validation passed: Map 12, 5 dependency nodes, 28 edges, and matrix/reports unchanged")


if __name__ == "__main__":
    main()
