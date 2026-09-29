"""Render diagnostic SVGs from a Model Lab water/TN/TP ledger run.

These graphics inspect routing provenance and arithmetic. They do not portray
measured basin loads, physical stream traces, or calibrated model performance.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from xml.sax.saxutils import escape


CONSTITUENTS = ("water", "TN", "TP")
BALANCE_FIELDS = (
    "run_id", "period", "huc12", "constituent", "unit", "residual",
    "routing_basis", "qa_status", "physical_geometry", "input_status",
)
SUMMARY_FIELDS = (
    "run_id", "period", "constituent", "unit", "total_local_input",
    "total_not_forwarded_assumed", "total_unrouted_at_unresolved", "boundary_export",
    "residual", "unresolved_policy",
)
CLASS_INFO = {
    "physical_3dhp": ("3DHP physical crossing", "#36799b"),
    "official_3dhp_connector": ("Official 3DHP connector", "#a6c5c8"),
    "physical_nhdplus_hr_existing": ("Existing physical representation", "#597e64"),
    "project_inference": ("Unresolved project inference", "#d48b54"),
    "terminal": ("Terminal HUC", "#4c527f"),
    "other": ("Other declared routing basis", "#b8b8b8"),
}
INK = "#203342"
MUTED = "#536674"
RULE = "#ced8dc"


def xml(value: object) -> str:
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def read_csv(path: Path, required: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(required) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def number(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"nonfinite {key} in {row.get('constituent')} / {row.get('huc12')}")
    return value


def fmt(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.6g}"


def svg_open(title: str, description: str, width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-labelledby="title desc">',
        f"<title id=\"title\">{xml(title)}</title>",
        f"<desc id=\"desc\">{xml(description)}</desc>",
        '<rect width="100%" height="100%" fill="#fcfdfb"/>',
        '<g font-family="system-ui, Segoe UI, sans-serif" fill="#203342">',
    ]


def svg_close(parts: list[str], path: Path) -> None:
    parts.extend(("</g>", "</svg>"))
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def text(parts: list[str], x: float, y: float, value: object, *, size: int = 16,
         weight: int = 400, color: str = INK, anchor: str = "start") -> None:
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}" text-anchor="{anchor}">{xml(value)}</text>'
    )


def rect(parts: list[str], x: float, y: float, width: float, height: float,
         fill: str, *, stroke: str | None = None, rx: int = 0) -> None:
    attrs = f' stroke="{stroke}"' if stroke else ""
    parts.append(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(0, width):.2f}" '
        f'height="{max(0, height):.2f}" rx="{rx}" fill="{fill}"{attrs}/>'
    )


def line(parts: list[str], x1: float, y1: float, x2: float, y2: float,
         color: str = RULE) -> None:
    parts.append(
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" '
        f'y2="{y2:.2f}" stroke="{color}"/>'
    )


def declared_status(rows: list[dict[str, str]], manifest: dict) -> str:
    statuses = sorted({r["input_status"] for r in rows})
    manifest_status = manifest.get("input_status")
    if manifest_status == "synthetic_diagnostic":
        return "Synthetic diagnostic inputs"
    if manifest_status:
        return f"Declared input status: {manifest_status}"
    if set(statuses) <= {"synthetic_diagnostic", "omitted_zero_diagnostic"}:
        return "Synthetic diagnostic inputs"
    return "Declared input status: " + ", ".join(statuses)


def route_class(row: dict[str, str]) -> str:
    basis = row["routing_basis"].strip()
    if not row["route_to_huc12"].strip():
        return "terminal"
    if row["qa_status"].strip().upper() == "UNRESOLVED":
        return "project_inference"
    return basis if basis in CLASS_INFO else "other"


def rings(geometry: dict) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return geometry["coordinates"]
    if geometry["type"] == "MultiPolygon":
        return [ring for polygon in geometry["coordinates"] for ring in polygon]
    raise ValueError(f"unsupported WBD geometry: {geometry['type']}")


def point_distance_sq(point: tuple[float, float], left: tuple[float, float],
                      right: tuple[float, float]) -> float:
    dx, dy = right[0] - left[0], right[1] - left[1]
    if dx == dy == 0:
        return (point[0] - left[0]) ** 2 + (point[1] - left[1]) ** 2
    t = max(0.0, min(1.0, ((point[0] - left[0]) * dx +
                            (point[1] - left[1]) * dy) / (dx * dx + dy * dy)))
    return (point[0] - left[0] - t * dx) ** 2 + (point[1] - left[1] - t * dy) ** 2


def simplify(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Douglas-Peucker on a ring's open point sequence, retaining closure later."""
    if len(points) < 4:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    tol2 = tolerance * tolerance
    while stack:
        first, last = stack.pop()
        farthest = -1
        largest = tol2
        for index in range(first + 1, last):
            d2 = point_distance_sq(points[index], points[first], points[last])
            if d2 > largest:
                farthest, largest = index, d2
        if farthest >= 0:
            keep.add(farthest)
            stack.extend(((first, farthest), (farthest, last)))
    selected = [points[index] for index in sorted(keep)]
    return selected if len(selected) >= 3 else points


def render_map(run_dir: Path, wbd_path: Path, rows: list[dict[str, str]],
               run_id: str, period: str, input_label: str) -> None:
    first_constituent = {r["huc12"]: r for r in rows if r["constituent"] == "water"}
    if not first_constituent:
        raise ValueError("huc_balance.csv has no water rows for routing map")
    with wbd_path.open(encoding="utf-8") as handle:
        features = json.load(handle)["features"]
    polygons = {}
    for feature in features:
        huc = str(feature["properties"]["huc12"])
        if huc in polygons:
            raise ValueError(f"duplicate WBD HUC-12 {huc}")
        polygons[huc] = rings(feature["geometry"])
    absent = set(first_constituent) - set(polygons)
    if absent:
        raise ValueError(f"ledger HUC-12s absent from WBD: {sorted(absent)[:5]}")

    # A local equirectangular display projection is sufficient for a QA inset.
    all_coords = [p for poly in polygons.values() for ring in poly for p in ring]
    center_lat = (min(p[1] for p in all_coords) + max(p[1] for p in all_coords)) / 2
    cosine = math.cos(math.radians(center_lat))
    xs = [p[0] * cosine for p in all_coords]
    ys = [p[1] for p in all_coords]
    west, east, south, north = min(xs), max(xs), min(ys), max(ys)
    map_x, map_y, map_w, map_h = 58, 134, 870, 600
    scale = min(map_w / (east - west), map_h / (north - south))
    actual_w, actual_h = (east - west) * scale, (north - south) * scale
    offset_x = map_x + (map_w - actual_w) / 2
    offset_y = map_y + (map_h - actual_h) / 2

    def project(point: list[float]) -> tuple[float, float]:
        return (offset_x + (point[0] * cosine - west) * scale,
                offset_y + (north - point[1]) * scale)

    counts = Counter(route_class(r) for r in first_constituent.values())
    parts = svg_open(
        "HUC-12 routing evidence map",
        "Source WBD HUC-12 polygons colored by outgoing routing evidence in the "
        "derived accounting network. Polygon boundaries are not stream routes. "
        f"Run {run_id}, period {period}; {input_label}.", 1280, 830,
    )
    text(parts, 56, 55, "Routing evidence by HUC-12", size=29, weight=700)
    text(parts, 56, 86, f"{run_id} · {period} · {input_label}", size=16, color=MUTED)
    text(parts, 56, 112, "WBD polygon geography; fill classifies each HUC's outgoing accounting link.", size=15, color=MUTED)
    for huc, polygon in polygons.items():
        if huc not in first_constituent:
            fill = "#edf0f0"
        else:
            fill = CLASS_INFO[route_class(first_constituent[huc])][1]
        segments = []
        for ring in polygon:
            raw = [project(point) for point in ring]
            if raw and raw[0] == raw[-1]:
                raw.pop()
            if len(raw) < 3:
                continue
            sampled = simplify(raw, 0.55)
            segments.append("M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in sampled) + " Z")
        if segments:
            parts.append(
                f'<path d="{" ".join(segments)}" fill="{fill}" fill-rule="evenodd" '
                f'stroke="#f8faf8" stroke-width="0.7"><title>HUC-12 {xml(huc)}: '
                f'{xml(CLASS_INFO[route_class(first_constituent[huc])][0] if huc in first_constituent else "outside run")}'
                "</title></path>"
            )
    line(parts, 955, 139, 955, 729)
    text(parts, 982, 164, "Outgoing link basis", size=19, weight=700)
    y = 204
    for key in ("physical_3dhp", "physical_nhdplus_hr_existing",
                "official_3dhp_connector", "project_inference", "terminal", "other"):
        count = counts[key]
        if not count:
            continue
        label, color = CLASS_INFO[key]
        rect(parts, 984, y - 14, 18, 18, color)
        text(parts, 1014, y, label, size=14)
        text(parts, 1014, y + 20, f"{count} HUC-12" + ("s" if count != 1 else ""),
             size=13, color=MUTED)
        y += 62 if len(label) < 33 else 70
    text(parts, 982, min(y + 30, 647), f"{len(first_constituent)} ledger HUC-12s", size=15, weight=600)
    text(parts, 56, 776, "Unresolved links are project inferences; official connectors are not physical channels.", size=14, color=MUTED)
    text(parts, 56, 802, "This map reports routing provenance, not measured transport or channel geometry.", size=14, color=MUTED)
    svg_close(parts, run_dir / "routing_qa.svg")


def render_mass_balance(run_dir: Path, summaries: dict[str, dict[str, str]],
                        run_id: str, period: str, input_label: str) -> None:
    parts = svg_open(
        "Water, total nitrogen, and total phosphorus accounting dispositions",
        "Three separate constituent panels compare supplied local input with "
        "amounts not forwarded under an explicit assumption, amounts unrouted "
        "at unresolved links, and boundary export. Each panel has its own scale "
        "and unit. These are accounting dispositions, not measured storage, "
        f"treatment, retention, or removal. Run {run_id}; {input_label}.", 1280, 900,
    )
    text(parts, 50, 51, "Accounting dispositions", size=29, weight=700)
    text(parts, 50, 83, f"{run_id} · {period} · {input_label}", size=16, color=MUTED)
    text(parts, 50, 109, "Each constituent has its own scale. Bars compare local inputs with recorded dispositions.", size=15, color=MUTED)
    components = (
        ("total_not_forwarded_assumed", "Not forwarded (assumed)", "#9d759d"),
        ("total_unrouted_at_unresolved", "Unrouted at unresolved link", "#d48b54"),
        ("boundary_export", "Boundary export", "#36799b"),
    )
    for index, constituent in enumerate(CONSTITUENTS):
        row = summaries[constituent]
        y = 146 + index * 226
        unit = row["unit"].replace("m3", "m³")
        title = {"water": "Water", "TN": "Total nitrogen (TN)", "TP": "Total phosphorus (TP)"}[constituent]
        rect(parts, 48, y, 1184, 203, "#f2f6f5", rx=8)
        text(parts, 70, y + 34, f"{title} · {unit}", size=21, weight=700)
        supplied = number(row, "total_local_input")
        amounts = [(label, number(row, field), color) for field, label, color in components]
        if supplied < 0 or any(amount < 0 for _, amount, _ in amounts):
            raise ValueError(f"negative balance amount in {constituent}")
        disposition = sum(amount for _, amount, _ in amounts)
        maximum = max(supplied, disposition)
        bar_x, bar_w = 248, 680
        text(parts, 70, y + 82, "Local input", size=15)
        text(parts, 70, y + 130, "Disposition", size=15)
        rect(parts, bar_x, y + 59, bar_w, 25, "#e3e9e8", rx=3)
        rect(parts, bar_x, y + 107, bar_w, 25, "#e3e9e8", rx=3)
        if maximum:
            rect(parts, bar_x, y + 59, bar_w * supplied / maximum, 25, INK, rx=3)
            current_x = bar_x
            for _, amount, color in amounts:
                width = bar_w * amount / maximum
                if width:
                    rect(parts, current_x, y + 107, width, 25, color)
                current_x += width
        text(parts, 947, y + 79, fmt(supplied), size=16, weight=600)
        text(parts, 947, y + 127, fmt(disposition), size=16, weight=600)
        legend_x = 72
        for label, amount, color in amounts:
            rect(parts, legend_x, y + 162, 14, 14, color)
            text(parts, legend_x + 20, y + 175, f"{label}: {fmt(amount)}", size=13)
            legend_x += 335 if label == "Unrouted at unresolved link" else 287
        text(parts, 947, y + 175, f"Residual: {fmt(number(row, 'residual'))}", size=13, color=MUTED)
    text(parts, 51, 843, "Unrouted or not forwarded means a bookkeeping disposition, not storage, treatment, retention, or removal.", size=14, color=MUTED)
    text(parts, 51, 868, "An arithmetic balance does not establish an observed basin water or nutrient budget.", size=14, color=MUTED)
    svg_close(parts, run_dir / "mass_balance.svg")


def render_residuals(run_dir: Path, rows: list[dict[str, str]],
                     summaries: dict[str, dict[str, str]], run_id: str,
                     period: str, input_label: str) -> None:
    parts = svg_open(
        "HUC-12 node balance residual diagnostic",
        "Per-constituent counts of absolute arithmetic node residuals in four "
        "display bins, with largest absolute node residual and aggregate "
        f"residual. These bins are not scientific uncertainty thresholds. Run {run_id}.",
        1280, 750,
    )
    text(parts, 50, 52, "Node closure diagnostic", size=29, weight=700)
    text(parts, 50, 83, f"{run_id} · {period} · {input_label}", size=16, color=MUTED)
    text(parts, 50, 112, "Absolute ledger residual at each HUC-12; bins are display guides, not model acceptance thresholds.", size=15, color=MUTED)
    colors = ("#6e9e83", "#b9c8a2", "#dfbf7b", "#c97863")
    labels = ("exact zero", "0 to 1e-12", "1e-12 to 1e-9", "above 1e-9")
    for index, constituent in enumerate(CONSTITUENTS):
        group = [r for r in rows if r["constituent"] == constituent]
        y = 149 + index * 169
        rect(parts, 48, y, 1184, 148, "#f2f6f5", rx=8)
        unit = summaries[constituent]["unit"].replace("m3", "m³")
        title = {"water": "Water", "TN": "Total nitrogen", "TP": "Total phosphorus"}[constituent]
        text(parts, 69, y + 34, f"{title} · {unit}", size=20, weight=700)
        values = [abs(number(r, "residual")) for r in group]
        bins = [0, 0, 0, 0]
        for value in values:
            bins[0 if value == 0 else 1 if value <= 1e-12 else 2 if value <= 1e-9 else 3] += 1
        bar_x, bar_y, bar_w = 72, y + 60, 774
        rect(parts, bar_x, bar_y, bar_w, 29, "#e3e9e8", rx=3)
        cursor = bar_x
        for count, color in zip(bins, colors):
            width = bar_w * count / len(group) if group else 0
            if width:
                rect(parts, cursor, bar_y, width, 29, color)
            cursor += width
        text(parts, 867, y + 74, f"{len(group)} HUC-12 nodes", size=15, weight=600)
        text(parts, 867, y + 100, f"Max |residual|: {fmt(max(values, default=0))}", size=14)
        text(parts, 867, y + 123,
             f"Aggregate residual: {fmt(number(summaries[constituent], 'residual'))}",
             size=14, color=MUTED)
        legend_x = 74
        for label, count, color in zip(labels, bins, colors):
            rect(parts, legend_x, y + 111, 12, 12, color)
            text(parts, legend_x + 18, y + 122, f"{label}: {count}", size=12)
            legend_x += 183 if label != "above 1e-9" else 160
    text(parts, 53, 696, "Zero or small residuals verify arithmetic only; they do not validate input data or routing physics.", size=14, color=MUTED)
    text(parts, 53, 720, "Check the machine-readable ledger and validator for the actual pass/fail decision.", size=14, color=MUTED)
    svg_close(parts, run_dir / "residuals.svg")


def render(run_dir: Path, wbd_path: Path) -> None:
    balances = read_csv(run_dir / "huc_balance.csv", BALANCE_FIELDS + ("route_to_huc12",))
    summary_rows = read_csv(run_dir / "boundary_summary.csv", SUMMARY_FIELDS)
    with (run_dir / "run_manifest.json").open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    run_ids = {row["run_id"] for row in balances + summary_rows}
    periods = {row["period"] for row in balances + summary_rows}
    if len(run_ids) != 1 or len(periods) != 1:
        raise ValueError("figures require one run_id and one period")
    if len({(r["huc12"], r["constituent"]) for r in balances}) != len(balances):
        raise ValueError("duplicate HUC-12 × constituent balance rows")
    if len({r["constituent"] for r in summary_rows}) != len(summary_rows):
        raise ValueError("duplicate constituent boundary summaries")
    summaries = {r["constituent"]: r for r in summary_rows}
    if set(summaries) != set(CONSTITUENTS):
        raise ValueError(f"expected summaries for {CONSTITUENTS}, got {tuple(summaries)}")
    hucs_by_constituent = {
        constituent: {r["huc12"] for r in balances if r["constituent"] == constituent}
        for constituent in CONSTITUENTS
    }
    if len(set(map(frozenset, hucs_by_constituent.values()))) != 1:
        raise ValueError("constituent HUC-12 coverage differs")
    run_id, period = next(iter(run_ids)), next(iter(periods))
    input_label = declared_status(balances, manifest)
    render_map(run_dir, wbd_path, balances, run_id, period, input_label)
    render_mass_balance(run_dir, summaries, run_id, period, input_label)
    render_residuals(run_dir, balances, summaries, run_id, period, input_label)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--wbd", required=True, type=Path,
                        help="source WBD HUC-12 GeoJSON; used only for polygon display")
    args = parser.parse_args()
    render(args.run_dir, args.wbd)


if __name__ == "__main__":
    main()
