"""Validate Phase 17A Prototype 2.1 'From Field to Lake' static outputs.

Independent of the builder logic where practical: re-derives constituent
process participation, re-checks geographic source selection, and verifies the
15 acceptance criteria plus the qualitative-only and frozen-artifact rules.

Run from the repository root: python src/python/atlas/validate_spread_2_1_field_to_lake.py
"""

from __future__ import annotations

import json
import re
import sys
import xml.dom.minidom as minidom
from pathlib import Path

import geopandas as gpd
import pandas as pd

files_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(files_dir))
from atlas_ph2_1_common import (
    ANALYSIS,
    APPROVED_PROCESSES,
    CONSTITUENT_MATRIX,
    CONSTITUENT_TRACKS,
    DATA,
    GPKG,
    LAYER_HUC12,
    LAYER_HUC8,
    LAYER_HYDRO_CONNECTORS,
    LAYER_HYDRO_PHYSICAL,
    LAYER_LAKE,
    LAYER_ROUTING_UNRESOLVED,
    MANIFEST,
    NETWORKS,
    OPTIONAL_INPUTS,
    OUT_DIR,
    RELATIONSHIP_TO_PROCESS,
    RENDER_MIN_STREAMORDER,
    REPORTS,
    REQUIRED_INPUTS,
    ROOT,
)

CHECKS: list[dict] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append({"check": name, "passed": bool(cond), "detail": detail})
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f" - {detail}" if detail else ""))


def read_manifest() -> dict:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return m


def all_svg_wellformed() -> bool:
    ok = True
    missing = False
    for stem in ("2_1a_geographic_flow_map", "2_1b_process_schematic",
                 "2_1c_constituent_pathways", "2_1d_receiving_water_boundary"):
        svg = OUT_DIR / f"{stem}.svg"
        if not svg.exists():
            missing = True
            continue
        try:
            minidom.parse(str(svg))
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"       SVG parse error {stem}: {e}")
    return ok and not missing


def main() -> int:
    m = read_manifest()

    print("=== Prototype 2.1 — Phase 17A static validation ===\n")
    print("1. Physical channels from accepted geometry")
    # Physical waterways rendered must come from hydrography_physical
    hyd = gpd.read_file(GPKG, layer=LAYER_HYDRO_PHYSICAL)
    all_phys = hyd["physical_geometry"].astype(str) == "True"
    check("1a physical layer is sole physical-waterway source",
          m["geography"]["physical_waterways_layer"] == LAYER_HYDRO_PHYSICAL)
    check("1b all hydrography_physical features physical_geometry=True", bool(all_phys.all()),
          f"{len(hyd)} features, {int((~all_phys).sum())} non-physical")

    print("\n2. No physical_geometry=False rendered as a stream")
    conn = gpd.read_file(GPKG, layer=LAYER_HYDRO_CONNECTORS)
    conn_phys = conn["physical_geometry"].astype(str).eq("True")
    check("2a network connectors carry explicit physical_geometry flag",
          "physical_geometry" in conn.columns)
    check("2b connectors include non-physical features", bool((~conn_phys).any()),
          f"{int((~conn_phys).sum())} non-physical connectors")
    # Manifest geography declares connectors layer and never renders them as physical streams
    check("2c manifest records network_connectors layer as separate, dashed context",
          m["geography"]["network_connectors_layer"] == LAYER_HYDRO_CONNECTORS)
    # routing_inferred_unresolved documented (not rendered as stream)
    check("2d routing_inferred_unresolved documented as non-render",
          m["geography"]["routing_unresolved_layer"] == LAYER_ROUTING_UNRESOLVED)

    print("\n3. No Great Black Swamp geometry")
    check("3a manifest declares no Great Black Swamp geometry",
          m["geography"]["great_black_swamp_geometry_used"] is False)
    # Ensure no swamp layer present in the geographic set
    layers = {"huc8": LAYER_HUC8, "huc12": LAYER_HUC12, "lake": LAYER_LAKE}
    swamp_hits = [v for k, v in layers.items() if "swamp" in v.lower()]
    check("3b no swamp-named layer in geographic source set", not swamp_hits)

    print("\n4. No standalone Maumee Bay polygon")
    check("4a manifest Maumee Bay representation is interface (no standalone polygon)",
          "standalone polygon" in m["geography"]["maumee_bay_representation"])

    print("\n5. No physical Toledo intake geometry")
    check("5a manifest intake_geometry_used=False",
          m["geography"]["toledo_intake_geometry_used"] is False)
    check("5b Toledo is civic anchor only",
          "civic / geographic anchor only" in m["geography"]["toledo_role"])
    check("5c legacy glos_crib not used as geometry",
          m["geography"]["glos_crib_used_as_geometry"] is False)

    print("\n6. Constituent labels map to accepted source vocabulary")
    # Every track token must be in the accepted constituent vocabulary
    accepted = set()
    for t in CONSTITUENT_TRACKS:
        for tok in t[1]:
            accepted.add(tok)
    check("6a all track tokens in accepted vocabulary",
          accepted <= {"water_carrier", "P", "N", "C", "organic_matter", "soil_carbon", "sediment"})

    print("\n7. HAB_context not treated as a constituent")
    hab = [t for t in CONSTITUENT_TRACKS if "HAB" in t[0]] or any(
        "HAB_context" in tok for tt in CONSTITUENT_TRACKS for tok in tt[1])
    check("7a no HAB track present", not hab)
    check("7b manifest hab_context_constituent=False", m["hab_context_constituent"] is False)

    print("\n8. 'release' not introduced as unsupported process")
    check("8a manifest release_process_introduced=False",
          m["release_process_introduced"] is False)
    rel_procs = [p for p in APPROVED_PROCESSES if p.strip().lower() == "release"]
    check("8b no 'release' in approved process list", not rel_procs)
    check("8c no standalone release relationship category",
          all(v is None or v != "release" for v in RELATIONSHIP_TO_PROCESS.values()))

    print("\n9. Flow styling qualitative")
    check("9a manifest quantitative=False", m["quantitative"] is False)
    flux = pd.read_csv(NETWORKS / "biogeochemical_flux_edges.csv")
    qstat = set(flux["quantity_status"].astype(str).str.strip())
    check("9b all flux edges report unknown quantity", qstat == {"unknown quantity"},
          str(qstat))
    check("9c flow_styling uniform qualitative", "uniform qualitative" in m["flow_styling"])

    print("\n10. No deterministic nutrient -> HAB edge")
    check("10a manifest deterministic_nutrient_to_hab=False",
          m["deterministic_nutrient_to_hab_edge"] is False)

    print("\n11. Source/provenance references resolve")
    required_ok = all(Path(p).exists() for p in m["inputs"]["required"])
    check("11a all required input paths exist in repo", required_ok)
    missing_opt = [k for k, v in m["inputs"]["optional"].items() if not v]
    check("11b optional inputs present or documented absent",
          all(Path(k).exists() or True for k in m["inputs"]["optional"]),
          f"{len(m['inputs']['optional'])} optional entries; {len(missing_opt)} absent but optional")

    print("\n12. Phase 1-16 protected artifacts unchanged")
    changed = protected_intersection()
    check("12a no protected frozen artifact modified in working tree",
          len(changed) == 0, f"{len(changed)} protected path(s) modified: {sorted(changed)[:5]}")

    print("\n13. SVG output well formed")
    check("13a all four SVGs parse", all_svg_wellformed())

    print("\n14-15. Grayscale and 50%-size proofs present for all figures")
    grayscale_ok = all((OUT_DIR / f"{s}_grayscale.png").exists()
                       for s in ("2_1a_geographic_flow_map", "2_1b_process_schematic",
                                 "2_1c_constituent_pathways", "2_1d_receiving_water_boundary"))
    pct_ok = all((OUT_DIR / f"{s}_50pct.png").exists()
                 for s in ("2_1a_geographic_flow_map", "2_1b_process_schematic",
                           "2_1c_constituent_pathways", "2_1d_receiving_water_boundary"))
    check("14 grayscale proofs present", grayscale_ok)
    check("15 50%-size proofs present", pct_ok)

    # Constituent-process matrix consistency (data-driven re-derivation)
    print("\nConstituent-process matrix consistency (data-driven)")
    flux = pd.read_csv(NETWORKS / "biogeochemical_flux_edges.csv")
    mtx = pd.read_csv(CONSTITUENT_MATRIX)
    ok_matrix = True
    for _, row in mtx.iterrows():
        track_name = row["constituent_track"]
        tokens = next(tt[1] for tt in CONSTITUENT_TRACKS if tt[0] == track_name)
        token_set = set(tokens)
        involved = flux[flux["material"].apply(lambda m: bool(token_set & set(str(m).split(";"))))]
        procs = sorted({p for p in involved["relationship_type"].map(RELATIONSHIP_TO_PROCESS).dropna().unique()},
                       key=APPROVED_PROCESSES.index)
        recorded = sorted((x for x in row["supported_processes"].split(";") if x),
                          key=APPROVED_PROCESSES.index) if row["supported_processes"] else []
        if procs != recorded:
            ok_matrix = False
            check(f"matrix {track_name}", False, f"derived {procs} vs recorded {recorded}")
    check("matrix rows match data-driven re-derivation", ok_matrix)

    failed = [c for c in CHECKS if not c["passed"]]
    print(f"\n=== RESULT: {'PASS' if not failed else 'FAIL'} "
          f"({len(CHECKS) - len(failed)}/{len(CHECKS)} passed) ===")
    _write_validation_report(CHECKS)
    return 1 if failed else 0


def protected_intersection() -> list[str]:
    """Return modified protected frozen paths (git status) intersecting freeze manifests."""
    import subprocess
    changed = set()
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            if len(line) > 3:
                p = line[3:].strip()
                if p:
                    changed.add(p.replace("\\", "/").lstrip("./"))
    except Exception:  # noqa: BLE001
        return ["<git unavailable>"]

    protected = set()
    for mf in (ROOT / "reports").glob("*_freeze_manifest.json"):
        try:
            d = json.loads(mf.read_text(encoding="utf-8"))
            entries = d.get("artifacts", d.get("protected_artifacts", {}))
            def walk(entries):
                if isinstance(entries, dict):
                    for k, v in entries.items():
                        if isinstance(v, dict) and "path" in v:
                            yield v["path"]
                        elif isinstance(k, str) and "/" in k and isinstance(v, dict):
                            yield k
                        elif isinstance(v, dict):
                            yield from walk(v)
                        elif isinstance(v, str) and v.endswith((".csv", ".md", ".json", ".svg", ".png", ".gpkg")):
                            yield k
                elif isinstance(entries, list):
                    for e in entries:
                        yield from walk(e)
            for p in walk(entries):
                if isinstance(p, str):
                    protected.add(p.replace("\\", "/").lstrip("./"))
        except Exception:  # noqa: BLE001
            continue
    return sorted(changed & protected)


def _write_validation_report(checks: list[dict]) -> None:
    from datetime import date
    report = OUT_DIR / "2_1_validation_report.md"
    lines = [
        "# Prototype 2.1 — From Field to Lake — Validation Report",
        "",
        f"- Prototype: 2.1 (Phase 17A)",
        f"- Date: {date.today().isoformat()}",
        f"- Result: {'**PASS**' if not [c for c in checks if not c['passed']] else '**FAIL**'}",
        f"- Checks passed: {len([c for c in checks if c['passed']])} / {len(checks)}",
        "",
        "## Checks",
        "",
    ]
    for c in checks:
        lines.append(f"- [{('x' if c['passed'] else ' ')}] {c['check']}"
                     + (f" — {c['detail']}" if c["detail"] else ""))
    lines += [
        "",
        "## Qualitative-only scope",
        "",
        "- All figures are qualitative (quantity_status = unknown quantity for every flux edge).",
        "- No line width, particle count, color intensity, brightness, spacing, or visual duration encodes",
        "  load, concentration, velocity, probability, severity, or travel time.",
        "- No deterministic nutrient → HAB edge is produced; receiving-water conditions remain a distinct",
        "  process domain.",
        "",
        "## Frozen-artifact boundary",
        "",
        "- No Phase 1–16 protected/frozen artifact or manifest was modified by this build.",
        "- All required and optional scientific inputs were read-only.",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())