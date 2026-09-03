"""Validate Sol-accepted Phase 8A-8C freeze manifests and protected bytes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = [
    ROOT / "reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json",
    ROOT / "reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json",
    ROOT / "reports/phase8c_biogeochemical_futures_freeze_manifest.json",
]
EXPECTED = {
    "8A": {"nodes": 18, "flux_edges": 24, "quantitative_records": 10},
    "8B": {"dependency_edges": 22, "controls": 10, "matrix_rows": 8},
    "8C": {"assumptions": 36, "scenario_nodes": 48, "scenario_edges": 42, "scenario_controls": 48, "scenario_uncertainty": 48, "comparison_rows": 6},
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    seen = set()
    total = 0
    for manifest_path in MANIFESTS:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        phase = manifest["accepted_phase"]
        assert manifest["status"] == "ACCEPTED / FROZEN", phase
        assert manifest["source_commit"] == "21f8d6cc3ab6925a8001551f21ab771622ea9d41", phase
        assert manifest["counts"] == EXPECTED[phase], phase
        assert set(manifest["artifacts"]).isdisjoint(seen), "phase artifact assigned twice"
        for rel, meta in manifest["artifacts"].items():
            path = ROOT / rel
            assert path.exists(), rel
            assert path.stat().st_size == meta["bytes"], rel
            assert digest(path) == meta["sha256"], rel
            seen.add(rel)
            total += 1
    assert total == 30
    for base in (
        "26_biogeochemical_nutrient_flux_system_2026",
        "27_biogeochemical_dependencies_controls_2026",
        "28_biogeochemical_futures_2050",
        "28b_biogeochemical_futures_2075",
    ):
        with Image.open(ROOT / f"outputs/maps/systems/{base}.png") as image:
            image.verify()
        root = ET.parse(ROOT / f"outputs/maps/systems/{base}.svg").getroot()
        assert len(" ".join(root.itertext())) > 100, base
    print(json.dumps({"status": "passed", "phase8_manifests": len(MANIFESTS), "protected_artifacts": total, "maps_valid": True}, indent=2))


if __name__ == "__main__":
    main()
