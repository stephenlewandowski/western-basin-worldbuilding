"""Build small public render derivatives, reading retained inputs without modifying them.

Python standard library only. GeoPackage WKB decoding supports the 2D geometries
used here. A local equirectangular drawing preserves orientation, not survey scale.
Run from anywhere: python src/python/atlas/build_region_explorer.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "assets/atlas/region"
BOUNDS = (-85.45, 40.30, -82.60, 42.10)
WIDTH, HEIGHT = 1000, 840
SCALE = 420
COS_LAT = math.cos(math.radians(41.2))


def project(lon: float, lat: float) -> tuple[float, float]:
    return ((lon - BOUNDS[0]) * COS_LAT * SCALE + 45,
            (BOUNDS[3] - lat) * SCALE + 40)


def geometry(blob: bytes) -> list[tuple[str, list[tuple[float, float]]]]:
    """Decode polygon rings and lines; fail rather than guess other dimensions."""
    assert blob[:2] == b"GP", "Expected GeoPackage geometry"
    envelope = (blob[3] >> 1) & 7
    pos = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[envelope]

    def read() -> list[tuple[str, list[tuple[float, float]]]]:
        nonlocal pos
        endian = "<" if blob[pos] == 1 else ">"
        pos += 1

        def uint() -> int:
            nonlocal pos
            value = struct.unpack_from(endian + "I", blob, pos)[0]
            pos += 4
            return value

        def points() -> list[tuple[float, float]]:
            nonlocal pos
            count = uint()
            result = [struct.unpack_from(endian + "dd", blob, pos + i * 16) for i in range(count)]
            pos += count * 16
            return result

        kind = uint()
        if kind == 2:
            return [("line", points())]
        if kind == 3:
            return [("ring", points()) for _ in range(uint())]
        if kind in (5, 6):
            result = []
            for _ in range(uint()):
                result.extend(read())
            return result
        raise ValueError(f"Unsupported WKB geometry type {kind}")

    return read()


def simplify(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Iterative Douglas–Peucker, in drawing units, retaining endpoints."""
    if len(points) < 3:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        ax, ay = points[first]
        bx, by = points[last]
        dx, dy = bx - ax, by - ay
        denom = dx * dx + dy * dy
        best, index = 0.0, first
        for i in range(first + 1, last):
            x, y = points[i]
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / denom)) if denom else 0.0
            distance = math.hypot(x - ax - t * dx, y - ay - t * dy)
            if distance > best:
                best, index = distance, i
        if best > tolerance:
            keep.add(index)
            stack.extend([(first, index), (index, last)])
    return [points[i] for i in sorted(keep)]


def path(blob: bytes, tolerance: float) -> str:
    commands = []
    for kind, coords in geometry(blob):
        points = [project(*point) for point in coords]
        if (max(x for x, _ in points) < 0 or min(x for x, _ in points) > WIDTH
                or max(y for _, y in points) < 0 or min(y for _, y in points) > HEIGHT):
            continue
        simplified = simplify(points, tolerance)
        if kind == "ring" and len(simplified) < 4:
            # Omit tiny render rings; never write the source geometry.
            continue
        commands.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in simplified) + ("Z" if kind == "ring" else ""))
    return "".join(commands)


def rows(file: str) -> list[dict[str, str]]:
    with (ROOT / file).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha(file: str, normalize_text: bool = False) -> str:
    content = (ROOT / file).read_bytes()
    if normalize_text:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gpkg = "data/processed/glasspunk_base.gpkg"
    connection = sqlite3.connect((ROOT / gpkg).as_uri() + "?mode=ro", uri=True)
    for layer in ("water_watersheds_huc8", "water_lake_erie", "hydrography_physical"):
        assert connection.execute("select srs_id from gpkg_geometry_columns where table_name=?", (layer,)).fetchone()[0] == 4326
    basins = [{"id": huc, "name": name, "path": path(blob, .65)} for huc, name, blob in
              connection.execute("select huc8,name,geom from water_watersheds_huc8 order by huc8")]
    lake = "".join(path(blob, .5) for (blob,) in connection.execute("select geom from water_lake_erie"))
    rivers = "".join(path(blob, .45) for (blob,) in connection.execute(
        "select geom from hydrography_physical where streamorder>=5 order by fid"))
    river_count = connection.execute("select count(*) from hydrography_physical where streamorder>=5").fetchone()[0]
    connection.close()

    settlements = rows("data/processed/analysis/population_settlement_nodes.csv")
    materials = rows("data/processed/networks/materials_system_nodes.csv")
    energy = rows("data/processed/networks/energy_system_nodes.csv")
    config = json.loads((ROOT / "src/atlas/landmarks.json").read_text(encoding="utf-8"))
    raw_flow = json.loads((ROOT / "data/raw/climate_hazards/usgs_maumee_waterville_daily_flow_2025_2026.json").read_text())
    gauge = raw_flow["value"]["timeSeries"][0]["sourceInfo"]["geoLocation"]["geogLocation"]
    landmarks = []
    for item in config:
        if item["kind"] == "municipality":
            record = next(row for row in settlements if row["node_id"] == item["source_id"])
        elif item["kind"] == "material":
            record = next(row for row in materials if row["node_id"] == item["source_id"])
        elif item["kind"] == "energy":
            record = next(row for row in energy if row["node_id"] == item["source_id"])
        elif item["kind"] == "gauge":
            record = gauge
        else:
            assert item["id"] == "crib"
            # Resolved physical structure, not the legacy GLOS monitoring point.
            record = {"longitude": -83.259167, "latitude": 41.699444}
            assert "41.699444" in (ROOT / item["source_id"]).read_text(encoding="utf-8")
        longitude, latitude = float(record["longitude"]), float(record["latitude"])
        x, y = project(longitude, latitude)
        landmarks.append({**item, "longitude": longitude, "latitude": latitude, "x": round(x, 2), "y": round(y, 2)})

    flow = [{"date": row["date"], "flow": float(row["daily_mean_discharge_ft3_s"]),
             "approval": row["approval_in_snapshot"], "estimated": row["estimated"] == "true",
             "qualifiers": row["source_qualifiers"]}
            for row in rows("outputs/model_lab/observations/waterville_daily_flow_2025.csv")]
    assert len(flow) == 365 and len({row["date"] for row in flow}) == 365
    assert all(math.isfinite(row["flow"]) and row["flow"] >= 0 for row in flow)
    dataset = {"width": WIDTH, "height": HEIGHT, "basins": basins, "lake": lake,
               "rivers": rivers, "landmarks": landmarks, "flow": flow}
    (OUT / "region_explorer.json").write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # Lightweight homepage preview reuses the same drawing geometry.
    preview = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title">'
               '<title id="title">Maumee watershed, physical waterways and western Lake Erie</title>'
               '<rect width="1000" height="840" fill="#e9e2cf"/>'
               + ''.join(f'<path d="{b["path"]}" fill="#d5d7b8" stroke="#a7b198" stroke-width="1.2"/>' for b in basins)
               + f'<path d="{lake}" fill="#a9cdd1" fill-rule="evenodd"/><path d="{rivers}" fill="none" stroke="#417f8c" stroke-width="1.3"/>'
               + ''.join(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="7" fill="#a24730"/><text x="{p["x"] + 13}" y="{p["y"] - 12}" font-family="sans-serif" font-size="24" fill="#203b40">{p["title"]}</text>' for p in landmarks if p["id"] in ("toledo", "defiance", "fort-wayne"))
               + '<text x="760" y="165" font-family="sans-serif" font-size="28" fill="#254e58">Lake Erie</text></svg>\n')
    (OUT / "basin_preview.svg").write_text(preview, encoding="utf-8", newline="\n")
    inputs = [gpkg, "src/atlas/landmarks.json", "data/processed/analysis/population_settlement_nodes.csv",
              "data/processed/networks/materials_system_nodes.csv", "data/processed/networks/energy_system_nodes.csv",
              "reports/toledo_water_intake_crib_coordinate_resolution.md",
              "data/raw/climate_hazards/usgs_maumee_waterville_daily_flow_2025_2026.json",
              "outputs/model_lab/observations/waterville_daily_flow_2025.csv",
              "outputs/model_lab/observations/waterville_observation_manifest.json",
              "src/python/atlas/build_region_explorer.py"]
    manifest = {"product": "Public geographic and observed-flow render derivative", "built_date": "2026-10-03",
                "source_crs": "EPSG:4326", "drawing_projection": "Local equirectangular; reference latitude 41.2 degrees; qualitative display",
                "bounds_lon_lat": BOUNDS, "simplification": "Douglas–Peucker render copies: basins .65, lake .5, rivers .45 drawing units; tiny rings omitted",
                "counts": {"huc8": len(basins), "physical_river_features_streamorder_at_least_5": river_count, "landmarks": len(landmarks), "daily_observations": len(flow)},
                "input_hash_basis": "GeoPackage exact bytes; text inputs canonicalized to LF for Git checkout portability",
                "inputs_sha256": {file: sha(file, normalize_text=not file.endswith('.gpkg')) for file in inputs},
                "outputs_sha256": {str(file.relative_to(ROOT)).replace('\\', '/'): sha(str(file.relative_to(ROOT))) for file in (OUT / "region_explorer.json", OUT / "basin_preview.svg")},
                "credits": ["USGS hydrography, WBD and daily discharge", "US Census representative municipality points", "Retained energy/materials source registries", "US Coast Guard physical crib position, corroborated by NOAA/NDBC"],
                "limits": ["No analytical connectors, unresolved routing lines, complete tile drainage or held swamp boundary", "Regional cards overlap conceptually; no region polygons or exact future-site pins", "Facility points retain source address/asset precision; no operational boundary", "One gauge, retained 2025 daily means and snapshot flags; no nutrient loads, safety, flood extent or future forecast", "All accepted inputs and older maps remain unchanged"]}
    (OUT / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest["counts"]))


if __name__ == "__main__":
    main()
