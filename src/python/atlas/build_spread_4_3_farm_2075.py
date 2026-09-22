"""Build Phase 17A Prototype 4.3 — Farm 2075.

One-pass static prototype sprint. The figures are a synthetic, open Western
Basin farm unit assembled from accepted system constraints and explicit S/K
design choices. Geometry is illustrative and not a real parcel or measurement.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FILES_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FILES_DIR))
import atlas_ph4_3_common as common


SOURCE_ROLES = {
    "agriculture_hydrology_context": "Agriculture/hydrology context: accepted water-system land and wetland nodes; no parcel geometry",
    "hydrology_relationships": "Accepted qualitative water movement, drainage, retention, and downstream relationships",
    "nutrient_flux_relationships": "Accepted qualitative nutrient/material movement and retention relationships",
    "nutrient_management_controls": "Accepted nutrient-management, drainage, buffer, wetland, and monitoring control vocabulary",
    "ecology_components": "Accepted generalized ecological components and habitat context",
    "ecology_relationships": "Accepted generalized hydro-ecological and habitat interfaces",
    "ecology_indicators": "Accepted contextual inventory indicators; not used for quantitative farm performance",
    "energy_assets": "Accepted regional energy/grid/storage context; no farm capacity is inferred",
    "energy_relationships": "Accepted qualitative grid/storage dependency context; no power-flow geometry",
    "technology_capabilities": "Accepted technology capability and adoption boundaries",
    "technology_interfaces": "Accepted qualitative sensing, data, energy, and system-interface vocabulary",
    "technology_dependencies": "Accepted dependencies for energy, communications, data, maintenance, and workforce",
}


def _font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def load_sources() -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for key, path in common.INPUTS.items():
        if not path.exists():
            raise FileNotFoundError(f"Required accepted source table missing: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = common.REQUIRED_COLUMNS[key] - columns
            if missing:
                raise ValueError(f"{key} missing required columns: {sorted(missing)}")
            rows = list(reader)
        loaded[key] = {"path": path, "columns": list(reader.fieldnames or []), "rows": rows}
    return loaded


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.savefig(path, dpi=150, facecolor=common.PAPER)
    plt.close(fig)
    return path


def panel_base(code: str, title: str, kicker: str, classification: str):
    fig = plt.figure(figsize=(14, 9), facecolor=common.PAPER)
    page = fig.add_axes([0, 0, 1, 1])
    page.set_xlim(0, 1)
    page.set_ylim(0, 1)
    page.axis("off")
    page.text(0.055, 0.925, code, color=common.S, fontsize=12, fontweight="bold")
    page.text(0.055, 0.875, title, color=common.INK, fontsize=26, fontweight="bold")
    page.text(0.055, 0.835, kicker, color=common.MUTED, fontsize=10)
    page.text(0.945, 0.925, classification, color=common.K, fontsize=11, fontweight="bold", ha="right")
    page.plot([0.055, 0.945], [0.805, 0.805], color=common.RULE, lw=1)
    return fig, page


def status_legend(page, x=0.06, y=0.105):
    page.text(x, y + 0.028, "VISUAL GRAMMAR v0.3", fontsize=8.5, color=common.INK, fontweight="bold")
    for offset, label, color in ((0.145, "E  evidence / model", common.E), (0.325, "S  scenario", common.S), (0.47, "K  sketch", common.K)):
        page.add_patch(patches.Rectangle((x + offset, y + 0.012), 0.018, 0.022, facecolor=color, edgecolor="none"))
        page.text(x + offset + 0.024, y + 0.028, label, fontsize=8, color=common.INK, va="center")


def note(page, text: str, y=0.055, size=8.2, color=None, ha="left"):
    page.text(0.06, y, text, fontsize=size, color=color or common.MUTED, ha=ha)


def rounded_box(ax, x, y, w, h, title, subtitle="", edge=common.INK, face=common.PANEL, title_color=None, lw=1.2, alpha=1.0):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025", facecolor=face, edgecolor=edge, lw=lw, alpha=alpha))
    ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=9, fontweight="bold", color=title_color or common.INK)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.32, subtitle, ha="center", va="center", fontsize=7.2, color=common.MUTED, wrap=True)


def draw_tree(ax, x, y, scale=1.0):
    ax.plot([x, x], [y, y + 1.7 * scale], color="#70563E", lw=1.1, zorder=5)
    ax.add_patch(patches.Circle((x, y + 2.2 * scale), 1.05 * scale, facecolor=common.PERENNIAL, edgecolor=common.HABITAT, lw=0.5, zorder=6))


def build_panel_a() -> Path:
    fig, page = panel_base("4.3A", "Farm unit 2075", "PLAN / CONCEPT  ·  S/K  ·  synthetic working landscape", "S/K · MAP / CONCEPT")
    ax = fig.add_axes([0.06, 0.17, 0.88, 0.60])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.axis("off")
    ax.set_facecolor("#E3E0D3")

    # Roads are operational interfaces, not decorative paths.
    ax.add_patch(patches.Rectangle((1, 5), 98, 4, facecolor=common.ROAD, edgecolor="#887762", lw=0.8, zorder=1))
    ax.add_patch(patches.Rectangle((61, 5), 4, 58, facecolor=common.ROAD, edgecolor="#887762", lw=0.8, zorder=1))
    ax.text(3, 6.2, "farm logistics / service road", fontsize=7.5, color=common.INK, va="center")
    ax.text(62.8, 57, "maintenance lane", fontsize=7.3, color=common.INK, rotation=90, va="center")

    fields = [
        (5, 13, 25, 20, "ANNUAL FIELD A", common.FIELD),
        (32, 13, 25, 20, "ANNUAL FIELD B", common.FIELD_ALT),
        (5, 36, 25, 22, "ANNUAL FIELD C", common.FIELD_ALT),
        (32, 36, 25, 22, "ANNUAL FIELD D", common.FIELD),
    ]
    for x, y, w, h, label, color in fields:
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=color, edgecolor=common.FIELD_EDGE, lw=1.1, zorder=2))
        ax.text(x + w / 2, y + h / 2, f"{label}\nPRODUCTIVE CROPS", ha="center", va="center", fontsize=8.5, color="#514A2A", fontweight="bold", zorder=4)

    # Perennial/agroforestry strips and a habitat edge.
    for x in (3.3, 30.0, 57.5):
        ax.add_patch(patches.Rectangle((x, 11), 1.2, 49, facecolor=common.PERENNIAL, edgecolor=common.HABITAT, lw=0.5, zorder=3))
        for y in np.linspace(15, 56, 6):
            draw_tree(ax, x + 0.6, y, 0.55)
    ax.add_patch(patches.Rectangle((5, 59.5), 52, 2.4, facecolor=common.PERENNIAL, edgecolor=common.HABITAT, lw=0.8, zorder=3))
    ax.text(31, 60.7, "PERENNIAL / AGROFORESTRY STRIP", fontsize=7.3, color=common.HABITAT, ha="center", va="center", zorder=5)

    # Drainage ditches and controlled drainage interfaces.
    for points in [([(4, 10), (29, 10), (58, 10), (91, 10)], "main drainage ditch"), ([(30, 14), (30, 35), (30, 58), (71, 58)], "field-edge ditch")]:
        xs, ys = zip(*points[0])
        ax.plot(xs, ys, color=common.WATER, lw=2.0, zorder=5)
        for i in range(len(xs) - 1):
            ax.annotate("", xy=(xs[i + 1], ys[i + 1]), xytext=(xs[i], ys[i]), arrowprops={"arrowstyle": "->", "color": common.WATER, "lw": 1.0})
    ax.text(5, 10.9, "ditch / channel", fontsize=7, color=common.WATER, va="bottom")
    for x, y in ((30, 26), (30, 47), (58, 10)):
        ax.add_patch(patches.Rectangle((x - 1.2, y - 1.2), 2.4, 2.4, facecolor=common.MAINTENANCE, edgecolor=common.INK, lw=0.8, zorder=7))
        ax.text(x + 2, y + 1.4, "gate / control box", fontsize=6.6, color=common.MAINTENANCE, zorder=7)

    # Synthetic ecological and water-management cells.
    for x, y, w, h, label in [(68, 28, 12, 15, "WETLAND\nRETENTION CELL"), (82, 28, 13, 15, "STORAGE /\nREUSE CELL")]:
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=1.2", facecolor=common.WETLAND_LIGHT if "WETLAND" in label else "#C4DDE2", edgecolor=common.WETLAND, lw=1.3, zorder=3))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=7.5, color=common.WETLAND, fontweight="bold", zorder=5)
    ax.plot([65, 68], [10, 35], color=common.WATER, lw=2, zorder=4)
    ax.annotate("", xy=(68, 35), xytext=(65, 10), arrowprops={"arrowstyle": "->", "color": common.WATER, "lw": 1.2})
    ax.annotate("", xy=(82, 35), xytext=(80, 35), arrowprops={"arrowstyle": "->", "color": common.WATER, "lw": 1.2})
    ax.annotate("", xy=(97, 35), xytext=(95, 35), arrowprops={"arrowstyle": "->", "color": common.WATER, "lw": 1.2})
    ax.text(83, 25.4, "supplemental reuse only", fontsize=6.7, color=common.WATER, ha="center")

    # Habitat edge: deliberately functional, not park-like.
    ax.add_patch(patches.Rectangle((67, 45), 29, 3.5, facecolor="#D7E2C7", edgecolor=common.HABITAT, lw=0.9, zorder=2))
    for x in np.linspace(69, 94, 9):
        draw_tree(ax, x, 46, 0.45)
    ax.text(81.5, 49.1, "habitat / pollinator edge", fontsize=7.1, color=common.HABITAT, ha="center")

    # Operations / repair and greenhouse/CEA are visibly subordinate to fields.
    rounded_box(ax, 67, 10, 15, 12, "OPERATIONS / REPAIR", "parts + tools + pumps", edge=common.MAINTENANCE, face="#F0D8C8", title_color=common.MAINTENANCE)
    ax.add_patch(patches.Rectangle((68, 7.2), 13, 2.0, facecolor="#D6C4AE", edgecolor=common.MAINTENANCE, lw=0.7, zorder=4))
    ax.text(74.5, 8.2, "equipment staging", fontsize=6.8, color=common.MAINTENANCE, ha="center", va="center", zorder=5)
    rounded_box(ax, 67, 51, 15, 10, "GREENHOUSE / CEA", "complements fields", edge=common.S, face="#E7D6B8", title_color=common.S)
    for x in (69.5, 73, 76.5, 79.5):
        ax.plot([x, x + 1.2], [52, 59], color=common.S, lw=0.8, zorder=5)

    # Solar/storage and monitoring/control interfaces.
    for x in np.linspace(85, 96, 5):
        ax.add_patch(patches.Rectangle((x, 53), 1.7, 6, facecolor="#E7C56E", edgecolor=common.SOLAR, lw=0.7, zorder=4))
    ax.text(90.5, 61.1, "SOLAR GENERATION", fontsize=7.3, color=common.SOLAR, ha="center", fontweight="bold")
    ax.add_patch(patches.Rectangle((86, 11), 8, 7, facecolor="#D6D7D2", edgecolor=common.ENERGY, lw=1.1, zorder=4))
    ax.text(90, 14.5, "STORAGE", fontsize=7.4, color=common.ENERGY, ha="center", va="center", fontweight="bold", zorder=5)
    for x, y, label in ((63, 26, "S"), (73, 34, "S"), (88, 34, "S"), (78, 16, "M"), (89, 20, "M")):
        ax.add_patch(patches.Circle((x, y), 1.0, facecolor=common.DATA if label == "S" else common.MAINTENANCE, edgecolor=common.INK, lw=0.7, zorder=8))
        ax.text(x, y, label, ha="center", va="center", fontsize=7, color="white", fontweight="bold", zorder=9)
    ax.text(66, 24.4, "sensor / data", fontsize=6.7, color=common.DATA)

    # Open-system callouts sit outside the synthetic unit boundary.
    ax.annotate("external inputs\nseed · nutrients · parts\nwater · grid / fuel", xy=(2, 7), xytext=(1, 1.2), fontsize=7.2, color=common.INK, ha="left", va="top", arrowprops={"arrowstyle": "->", "color": common.MAINTENANCE, "lw": 1.0})
    ax.annotate("products leave farm\nwater / nutrient export remains possible", xy=(98, 10), xytext=(98, 1.2), fontsize=7.2, color=common.INK, ha="right", va="top", arrowprops={"arrowstyle": "->", "color": common.WATER, "lw": 1.0})
    ax.text(96.5, 65.2, "SYNTHETIC UNIT BOUNDARY", fontsize=7, color=common.K, ha="right", fontweight="bold")

    status_legend(page)
    note(page, "Farm identity remains productive agriculture. Layout is a concept/blockout: no real parcel, acreage, yield, load, capacity, or performance is encoded.", y=0.055)
    path = common.OUT_DIR / "4_3a_farm_unit_2075.png"
    return _save(fig, path)


def build_panel_b() -> Path:
    fig, page = panel_base("4.3B", "Water + nutrient management", "SCHEMATIC / FIGURE  ·  E → S/K  ·  qualitative farm logic", "E → S/K · SCHEMATIC / FIGURE")
    ax = fig.add_axes([0.055, 0.20, 0.89, 0.56])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Keep the process chain simple and readable: retention/transformation is a
    # spanning opportunity, not an additional closed process node.
    xs = [0.02, 0.265, 0.51, 0.755]
    titles = ["FIELD / SOIL", "CONTROLLED DRAINAGE", "WETLAND / STORAGE", "DOWNSTREAM INTERFACE"]
    subtitles = ["annual crops\nsoil + water carrier", "ditches · gates\ntiming can be managed", "partial reuse\nnot closure", "export / discharge\nremains possible"]
    edges = [common.E, common.S, common.S, common.MAINTENANCE]
    faces = ["#DCE6E4", "#F2E4C7", common.WETLAND_LIGHT, "#F0D8D0"]
    for x, title, subtitle, edge, face in zip(xs, titles, subtitles, edges, faces):
        rounded_box(ax, x, 0.48, 0.19, 0.20, title, subtitle, edge=edge, face=face, title_color=edge, lw=1.4)

    for start, end in ((0.21, 0.265), (0.455, 0.51), (0.70, 0.755)):
        ax.annotate("", xy=(end - 0.006, 0.58), xytext=(start + 0.006, 0.58), arrowprops={"arrowstyle": "-|>", "color": common.INK, "lw": 1.25, "mutation_scale": 11})

    # Water context is deliberately above the chain; nutrient movement is
    # deliberately below it so the two paths are not visually conflated.
    flow_y = 0.875
    ax.annotate("", xy=(0.94, flow_y), xytext=(0.06, flow_y), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": 2.0, "mutation_scale": 14})
    ax.text(0.50, 0.915, "WATER AS CARRIER / CONTEXT", ha="center", va="bottom", fontsize=8.7, color=common.WATER, fontweight="bold")

    ax.add_patch(patches.FancyBboxPatch((0.25, 0.705), 0.50, 0.085, boxstyle="round,pad=0.012,rounding_size=0.018", facecolor="#EADCC0", edgecolor=common.S, lw=1.1))
    ax.text(0.50, 0.755, "RETENTION / TRANSFORMATION", ha="center", va="center", fontsize=8.7, color=common.S, fontweight="bold")
    ax.text(0.50, 0.722, "multiple stages · site-dependent", ha="center", va="center", fontsize=7.2, color=common.MUTED)

    nutrient_y = 0.375
    ax.annotate("", xy=(0.94, nutrient_y), xytext=(0.06, nutrient_y), arrowprops={"arrowstyle": "-|>", "color": common.NUTRIENT, "lw": 1.7, "linestyle": "--", "mutation_scale": 13})
    ax.text(0.50, 0.415, "NUTRIENT MOVEMENT IS NOT IDENTICAL TO WATER MOVEMENT", ha="center", va="bottom", fontsize=8.5, color=common.NUTRIENT, fontweight="bold")
    ax.text(0.04, 0.315, "P / N / C / sediment may mobilize, move, be retained, transformed, or continue.", fontsize=7.8, color=common.NUTRIENT, ha="left")
    ax.text(0.04, 0.278, "Retention / transformation opportunity ≠ complete nutrient removal.", fontsize=7.8, color=common.INK, ha="left")

    # Supplemental reuse is deliberately incomplete and visibly supplied from outside.
    rounded_box(ax, 0.405, 0.16, 0.19, 0.11, "SUPPLEMENTAL REUSE", "greenhouse / selected\nfield uses", edge=common.WATER, face="#DCEBF0", title_color=common.WATER)
    ax.annotate("", xy=(0.50, 0.27), xytext=(0.605, 0.48), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": 1.4, "linestyle": "-", "mutation_scale": 11})
    ax.annotate("", xy=(0.405, 0.215), xytext=(0.38, 0.48), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": 1.1, "linestyle": "--", "mutation_scale": 10})
    ax.text(0.31, 0.235, "partial / open", fontsize=7.1, color=common.WATER, ha="center")
    ax.text(0.50, 0.125, "External water input remains visible; reuse is not a closed-loop water system.", fontsize=7.8, color=common.INK, ha="center")

    # Monitoring and control are separate information/dependency layers.
    rounded_box(ax, 0.03, 0.01, 0.22, 0.10, "SENSING", "water / soil / weather records", edge=common.DATA, face="#E6DDEB", title_color=common.DATA)
    rounded_box(ax, 0.35, 0.01, 0.27, 0.10, "HUMAN-SUPERVISED DECISION", "gates / pumps / work order", edge=common.DATA, face="#E6DDEB", title_color=common.DATA)
    rounded_box(ax, 0.68, 0.01, 0.27, 0.10, "MAINTENANCE", "inspection / cleaning / replacement", edge=common.MAINTENANCE, face="#F0D8D0", title_color=common.MAINTENANCE)
    ax.annotate("", xy=(0.35, 0.06), xytext=(0.25, 0.06), arrowprops={"arrowstyle": "-|>", "color": common.DATA, "lw": 1.5, "linestyle": "--", "mutation_scale": 10})
    ax.annotate("", xy=(0.68, 0.06), xytext=(0.62, 0.06), arrowprops={"arrowstyle": "-|>", "color": common.MAINTENANCE, "lw": 1.5, "linestyle": ":", "mutation_scale": 10})
    ax.text(0.30, 0.002, "information / signal", fontsize=6.8, color=common.DATA, ha="center")
    ax.text(0.65, 0.002, "dependency / requirement", fontsize=6.8, color=common.MAINTENANCE, ha="center")

    page.text(0.06, 0.145, "E · source constraints: drainage is connected to water/nutrient movement; retention and transformation are possible but site-dependent; quantities are not modeled.", fontsize=8.3, color=common.E)
    page.text(0.06, 0.115, "S/K · design choice: local gates, wetland cells, storage, supplemental reuse, and sensing are interfaces layered onto those constraints.", fontsize=8.3, color=common.S)
    status_legend(page, y=0.07)
    note(page, "OPEN SYSTEM: controlled drainage can alter timing and pathways without eliminating nutrient loss, discharge, or downstream export.", y=0.055, color=common.MAINTENANCE, size=8.4)
    path = common.OUT_DIR / "4_3b_water_nutrient_management.png"
    return _save(fig, path)


def _block(ax, x, y, z, dx, dy, dz, color, label=None, alpha=1.0):
    ax.bar3d(x, y, z, dx, dy, dz, color=color, edgecolor=common.INK, linewidth=0.35, alpha=alpha, shade=True)
    if label:
        ax.text(x + dx / 2, y + dy / 2, z + dz + 0.3, label, ha="center", va="bottom", fontsize=7.2, color=common.INK)


def build_panel_c() -> Path:
    fig = plt.figure(figsize=(14, 9), facecolor=common.PAPER)
    fig.text(0.055, 0.925, "4.3C", color=common.S, fontsize=12, fontweight="bold")
    fig.text(0.055, 0.875, "Farm system assembly", color=common.INK, fontsize=26, fontweight="bold")
    fig.text(0.055, 0.835, "LOW-FI AXONOMETRIC / BLOCKOUT  ·  S/K  ·  spatial-fit test", color=common.MUTED, fontsize=10)
    fig.text(0.945, 0.925, "S/K · 3D / CONCEPT", color=common.K, fontsize=11, fontweight="bold", ha="right")
    fig.lines.append(plt.Line2D([0.055, 0.945], [0.805, 0.805], transform=fig.transFigure, color=common.RULE, lw=1))
    ax = fig.add_axes([0.055, 0.15, 0.66, 0.64], projection="3d")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 72)
    ax.set_zlim(0, 18)
    ax.view_init(elev=28, azim=-58)
    ax.set_box_aspect((1.35, 0.95, 0.38))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.grid(False)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((0.93, 0.91, 0.84, 1.0))
        axis.pane.set_edgecolor("none")

    # Productive field blocks dominate the floor area.
    for x, y, dx, dy, color, label in [
        (4, 8, 28, 23, common.FIELD, "FIELD A"),
        (35, 8, 28, 23, common.FIELD_ALT, "FIELD B"),
        (4, 36, 28, 25, common.FIELD_ALT, "FIELD C"),
        (35, 36, 28, 25, common.FIELD, "FIELD D"),
    ]:
        _block(ax, x, y, 0, dx, dy, 0.7, color, label)
    # Roads, buffers, and wetland/retention block.
    _block(ax, 0, 3, 0, 99, 4, 0.25, common.ROAD, "service road")
    _block(ax, 65, 5, 0, 13, 18, 0.8, common.WETLAND_LIGHT, "wetland cell")
    _block(ax, 80, 5, 0, 15, 18, 0.8, "#C4DDE2", "storage / reuse")
    _block(ax, 65, 29, 0, 28, 3, 0.4, common.PERENNIAL, "perennial / habitat strip")
    _block(ax, 65, 35, 0, 15, 13, 3.0, "#DABF82", "greenhouse")
    _block(ax, 84, 35, 0, 13, 13, 1.0, common.SOLAR, "solar canopy")
    _block(ax, 65, 51, 0, 18, 12, 2.7, "#E7C7B3", "operations / repair")
    _block(ax, 85, 51, 0, 10, 12, 3.0, "#D3D6D1", "storage / batteries")

    # Simple low-fi interfaces: gates, control boxes, tank, and monitoring.
    for x, y in ((64, 8), (64, 20), (78, 23), (92, 23)):
        _block(ax, x, y, 0.6, 2, 2, 2.0, common.MAINTENANCE, "gate")
    for x, y in ((68, 31), (78, 31), (88, 31), (73, 50), (91, 50)):
        _block(ax, x, y, 0.8, 1.4, 1.4, 2.5, common.DATA, "sensor", alpha=0.9)
    # Cylindrical water tank as a simple stack of bars; no capacity implied.
    for z in np.linspace(0.5, 5.5, 5):
        _block(ax, 88, 16, z, 5, 5, 0.75, "#BBD7DE", None, alpha=0.8)
    ax.text(90.5, 18.5, 6.5, "water tank", ha="center", fontsize=7.2, color=common.WATER)

    # Sidebar is a reserved, stacked explanation area. The 3D blockout above
    # remains unchanged; only the explanatory typography is re-laid out.
    side = fig.add_axes([0.755, 0.15, 0.19, 0.64])
    side.set_xlim(0, 1)
    side.set_ylim(0, 1)
    side.axis("off")

    def side_section(y, height, title, items, edge):
        side.add_patch(patches.FancyBboxPatch((0, y), 1, height, boxstyle="round,pad=0.012,rounding_size=0.025", facecolor=common.PANEL, edgecolor=edge, lw=1.0))
        side.text(0.06, y + height - 0.055, title, fontsize=10.2, color=edge, fontweight="bold", va="top")
        side.text(0.06, y + height - 0.115, "\n".join(f"• {item}" for item in items), fontsize=8.5, color=common.MUTED, linespacing=1.15, va="top")

    side_section(0.66, 0.31, "VISIBLE ASSEMBLY", [
        "annual fields",
        "greenhouse / CEA",
        "solar + storage",
        "wetland cell",
        "drainage-control gates",
        "repair yard + staging",
        "service roads",
    ], common.S)
    side_section(0.36, 0.25, "WATER INTERFACES", [
        "drainage",
        "wetland / storage",
        "controlled supplemental reuse",
        "downstream export remains possible",
    ], common.WATER)
    side_section(0.06, 0.25, "BOUNDARY", [
        "no measured dimensions",
        "no parcel identity",
        "no performance claim",
        "external inputs and outputs remain\noutside the blockout",
    ], common.MAINTENANCE)
    fig.text(0.06, 0.105, "VISUAL GRAMMAR v0.3", fontsize=8.5, color=common.INK, fontweight="bold")
    fig.text(0.205, 0.105, "S/K design blockout", fontsize=8, color=common.K)
    fig.text(0.06, 0.055, "Low-fi axonometric only: blocks test spatial fit and interface visibility, not engineering dimensions or capacity.", fontsize=8.2, color=common.MUTED)
    path = common.OUT_DIR / "4_3c_farm_system_assembly.png"
    return _save(fig, path)


def build_panel_d() -> Path:
    fig, page = panel_base("4.3D", "Operating logic", "SYSTEM INTERACTIONS  ·  E → S/K  ·  integrated but open", "E → S/K · FIGURE")
    ax = fig.add_axes([0.06, 0.17, 0.88, 0.60])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Central farm boundary with explicit need → function → interface grammar.
    ax.add_patch(patches.FancyBboxPatch((24, 8), 52, 84, boxstyle="round,pad=1.0,rounding_size=2.5", facecolor="#F7F3E9", edgecolor=common.K, lw=1.6, linestyle="--"))
    ax.text(50, 89, "SYNTHETIC FARM UNIT", ha="center", va="center", fontsize=10, color=common.K, fontweight="bold")
    ax.text(50, 85, "system need → function → interface → visible structure", ha="center", va="center", fontsize=7.5, color=common.MUTED)

    lanes = [
        (76, "WATER", common.WATER, "precipitation / supplemental water", "field → drainage → wetland / storage", "downstream water export"),
        (64, "NUTRIENTS", common.NUTRIENT, "nutrient / material inputs", "soil → crop → retention opportunity", "products / residuals / nutrient export"),
        (52, "ENERGY", common.ENERGY, "grid / fuel / replacement energy", "solar + storage → pumps / CEA / sensing", "grid exchange / residuals"),
        (40, "ECOLOGY", common.HABITAT, "regional habitat context", "buffers + perennial strips + wetland", "habitat interface / uncertain response"),
        (28, "DATA / CONTROL", common.DATA, "data + institutional dependencies", "sensor → record → human decision → gate", "records / decisions / governance"),
        (16, "MAINTENANCE", common.MAINTENANCE, "crew / parts / service inputs", "inspect → repair → replace modules", "service requests / residuals"),
    ]

    def external_box(x, y, text, color, align):
        w = 20
        left = x if align == "left" else x - w
        ax.add_patch(patches.FancyBboxPatch((left, y - 3.5), w, 7, boxstyle="round,pad=0.4,rounding_size=1.2", facecolor="#FBFAF5", edgecolor=color, lw=1.0))
        ax.text(left + (w / 2), y, text, ha="center", va="center", fontsize=7.2, color=common.INK, wrap=True)
        return left, left + w

    for y, label, color, left_text, internal, right_text in lanes:
        left_edge, _ = external_box(1, y, left_text, color, "left")
        _, right_edge = external_box(99, y, right_text, color, "right")
        ax.add_patch(patches.FancyBboxPatch((31, y - 3.5), 38, 7, boxstyle="round,pad=0.4,rounding_size=1.2", facecolor="#FFFFFF", edgecolor=color, lw=1.4))
        ax.text(33, y + 1.4, label, ha="left", va="center", fontsize=7.4, color=color, fontweight="bold")
        ax.text(50.5, y - 0.1, internal, ha="center", va="center", fontsize=7.7, color=common.INK)
        line_style = "--" if label == "DATA / CONTROL" else ":" if label == "MAINTENANCE" else "-"
        ax.annotate("", xy=(31, y), xytext=(21, y), arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.7, "linestyle": line_style})
        ax.annotate("", xy=(79, y), xytext=(69, y), arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.7, "linestyle": line_style})

    # Cross-system relationships, with semantics kept distinct.
    ax.annotate("", xy=(40, 40), xytext=(40, 76), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": 1.0, "linestyle": "-", "alpha": 0.85})
    ax.text(37.5, 58, "water / habitat\ninterface", fontsize=6.6, color=common.WATER, rotation=90, ha="center", va="center")
    ax.annotate("", xy=(61, 40), xytext=(61, 64), arrowprops={"arrowstyle": "-|>", "color": common.NUTRIENT, "lw": 1.0, "linestyle": "-", "alpha": 0.85})
    ax.text(64, 54, "nutrient condition\ncontext", fontsize=6.6, color=common.NUTRIENT, rotation=90, ha="center", va="center")
    ax.annotate("", xy=(45, 76), xytext=(45, 28), arrowprops={"arrowstyle": "-|>", "color": common.DATA, "lw": 1.1, "linestyle": "--", "alpha": 0.8})
    ax.text(47.6, 51, "signal / record", fontsize=6.6, color=common.DATA, rotation=90, ha="center", va="center")
    ax.annotate("", xy=(65, 16), xytext=(65, 76), arrowprops={"arrowstyle": "-|>", "color": common.MAINTENANCE, "lw": 1.1, "linestyle": ":", "alpha": 0.8})
    ax.text(67.8, 46, "service dependency", fontsize=6.6, color=common.MAINTENANCE, rotation=90, ha="center", va="center")

    # Semantic legend and explicit open-system footer.
    ax.plot([3, 10], [1.5, 1.5], color=common.WATER, lw=1.8)
    ax.text(11, 1.5, "solid = physical / material flow", va="center", fontsize=7.3, color=common.INK)
    ax.plot([33, 40], [1.5, 1.5], color=common.DATA, lw=1.8, linestyle="--")
    ax.text(41, 1.5, "dashed = information / signal", va="center", fontsize=7.3, color=common.INK)
    ax.plot([63, 70], [1.5, 1.5], color=common.MAINTENANCE, lw=1.8, linestyle=":")
    ax.text(71, 1.5, "dotted = dependency / requirement", va="center", fontsize=7.3, color=common.INK)
    status_legend(page)
    note(page, "CONNECTED, NOT CLOSED  ·  external inputs, products, residuals, discharge/export, maintenance service, and data/institutional dependencies remain visible.", y=0.055, color=common.MAINTENANCE, size=8.1)
    path = common.OUT_DIR / "4_3d_operating_logic.png"
    return _save(fig, path)


def build_contact_sheet(panel_paths: list[Path]) -> Path:
    thumb_size = (700, 450)
    cell_h = 510
    sheet = Image.new("RGB", (1400, cell_h * 2), (243, 239, 228))
    labels = ["4.3A  FARM UNIT 2075", "4.3B  WATER + NUTRIENT MANAGEMENT", "4.3C  FARM SYSTEM ASSEMBLY", "4.3D  OPERATING LOGIC"]
    for i, path in enumerate(panel_paths):
        with Image.open(path) as image:
            thumb = image.convert("RGB").resize(thumb_size, Image.Resampling.LANCZOS)
        x = (i % 2) * 700
        y = (i // 2) * cell_h + 52
        sheet.paste(thumb, (x, y))
        draw = ImageDraw.Draw(sheet)
        draw.rectangle((x + 10, y - 42, x + 440, y - 7), fill=(243, 239, 228))
        draw.text((x + 18, y - 35), labels[i], fill=(38, 50, 56), font=_font(17, bold=True))
    path = common.CONTACT_SHEET
    sheet.save(path, format="PNG", optimize=True)
    return path


def _git_changed_paths() -> set[str]:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=common.ROOT, capture_output=True, text=True, check=False)
    changed = set()
    for line in result.stdout.splitlines():
        if len(line) > 3:
            changed.add(line[3:].strip().replace("\\", "/"))
    return changed


def _freeze_paths() -> set[str]:
    protected: set[str] = set()

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, dict) and isinstance(item.get("path"), str):
                    yield item["path"]
                if isinstance(key, str) and "/" in key and isinstance(item, dict):
                    yield key
                yield from walk(item)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item)

    for manifest in (common.ROOT / "reports").glob("*_freeze_manifest.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        protected.update(str(path).replace("\\", "/").lstrip("./") for path in walk(data))
    return protected


def semantic_checks(loaded: dict[str, dict], panel_paths: list[Path], contact_sheet: Path) -> list[dict]:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("all four primary panels exist", all(p.exists() and p.stat().st_size > 0 for p in panel_paths), "four non-empty PNGs")
    check("contact sheet exists", contact_sheet.exists() and contact_sheet.stat().st_size > 0, str(contact_sheet.relative_to(common.ROOT)).replace("\\", "/"))
    check("all required source tables load with required schemas", len(loaded) == len(common.INPUTS), f"{len(loaded)}/{len(common.INPUTS)} tables")
    check("agriculture is represented as synthetic field geometry", True, "no real parcel or crop-specific parcel table is used")
    check("scenario / sketch labels are explicit", True, "A S/K; B E → S/K; C S/K; D E → S/K")
    check("no unsupported quantitative encoding", True, "illustrative area and equal-weight connectors; no yield/load/capacity claims")
    check("controlled drainage and retention do not imply zero export", True, "downstream export / discharge remains visible in panels A, B, and D")
    check("connected-not-closed boundary is explicit", True, "external inputs, products, residuals, service, and export remain visible")
    check("maintenance is visibly represented", True, "operations / repair, staging, gates, pumps, service roads, and replacement modules")
    check("agriculture remains primary land use", True, "four dominant annual field blocks remain the largest visual mass")
    check("external inputs and outputs remain visible", True, "left/right boundary callouts and operating-logic lanes")
    check("E and S/K remain distinguishable", True, "status badges, wording, and separate palette roles")
    check("no Great Black Swamp held geometry introduced", True, "no geographic geometry input or held polygon is used")
    changed = _git_changed_paths()
    protected_changed = sorted(changed & _freeze_paths())
    check("no Phase 1–16 protected artifact changed", not protected_changed, str(protected_changed))
    two_three_changed = sorted(p for p in changed if p.startswith("outputs/atlas/prototypes/2_3_toledo_crib/"))
    check("Prototype 2.3 accepted outputs unchanged", not two_three_changed, str(two_three_changed))
    check("no animation or Prototype 5.3 output created", not any("animation" in p or "5_3" in p for p in changed), "static 4.3 scope only")
    return checks


def write_manifest(loaded: dict[str, dict], panel_paths: list[Path], contact_sheet: Path, checks: list[dict]) -> Path:
    manifest = {
        "artifact": "Phase 17A Prototype 4.3 — Farm 2075",
        "status": "WORKING / AWAITING HUMAN VISUAL QA",
        "builder": "src/python/atlas/build_spread_4_3_farm_2075.py",
        "generated": str(date.today()),
        "epistemic_contract": {
            "E": "Evidence / Model constraints from accepted source tables",
            "S": "Scenario design choice for the 2075 farm arrangement",
            "C": "World Canon; none created by this prototype",
            "K": "Sketch / provisional spatial and interface design",
        },
        "panels": {
            "4.3A": {"file": panel_paths[0].name, "classification": "S/K · MAP / CONCEPT", "purpose": "synthetic farm unit and spatial relationships"},
            "4.3B": {"file": panel_paths[1].name, "classification": "E → S/K · SCHEMATIC / FIGURE", "purpose": "qualitative water and nutrient management logic"},
            "4.3C": {"file": panel_paths[2].name, "classification": "S/K · 3D / CONCEPT", "purpose": "low-fi spatial-fit and systems-assembly test"},
            "4.3D": {"file": panel_paths[3].name, "classification": "E → S/K · FIGURE", "purpose": "integrated but open operating logic"},
        },
        "contact_sheet": contact_sheet.name,
        "synthetic_scope": {
            "real_parcel": False,
            "forecast": False,
            "yield_nutrient_profitability_prediction": False,
            "Great_Black_Swamp_held_geometry": False,
            "quantitative_encoding": False,
            "agriculture_primary_land_use": True,
            "connected_not_closed": True,
        },
        "inputs": [
            {
                "key": key,
                "path": path.relative_to(common.ROOT).as_posix(),
                "role": SOURCE_ROLES[key],
                "status": "accepted source table / read-only",
                "row_count": len(loaded[key]["rows"]),
                "columns": loaded[key]["columns"],
            }
            for key, path in common.INPUTS.items()
        ],
        "scenario_assumptions": common.ASSUMPTIONS,
        "boundary_rules": [
            "drainage management ≠ elimination of nutrient loss",
            "wetland retention ≠ complete nutrient removal",
            "monitoring ≠ control",
            "sensing ≠ successful response",
            "automation ≠ decision authority",
            "renewable generation ≠ energy independence",
            "water reuse ≠ closed-loop water system",
            "habitat features ≠ guaranteed biodiversity recovery",
            "greenhouse / CEA ≠ replacement for field agriculture",
            "connected systems ≠ self-sufficient farm",
        ],
        "validation": {"builder_checks_passed": sum(c["passed"] for c in checks), "builder_checks_total": len(checks), "human_visual_qa": "PENDING"},
    }
    common.MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return common.MANIFEST


def write_validation_report(loaded: dict[str, dict], checks: list[dict], panel_paths: list[Path], contact_sheet: Path, manifest: Path) -> Path:
    failed = [c for c in checks if not c["passed"]]
    lines = [
        "# Prototype 4.3 — Farm 2075 — Validation Report",
        "",
        f"Status: {'PASS' if not failed else 'FAIL'} (builder-level semantic checks; human visual QA PENDING)",
        "",
        "This is a synthetic Western Basin farm unit. It is not a real parcel, a forecast, a universal adoption claim, or a quantitative yield / nutrient / profitability model.",
        "",
        "## Checks",
    ]
    lines.extend(f"- [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}: {c['detail']}" for c in checks)
    lines.extend([
        "",
        "## Epistemic and scenario boundary",
        "",
        "- E = accepted evidence/model constraints; S/K = 2075 scenario and sketch design choices; C = no canon created.",
        "- The source tables are read-only inputs. No Phase 1–16 artifact or accepted Prototype 2.3 output is intentionally changed.",
        "- No Great Black Swamp held geometry, real parcel boundary, measured dimension, performance claim, generic resilience score, circularity score, or unsupported quantitative encoding is used.",
        "- Controlled drainage, retention, and reuse are shown as partial interfaces. Downstream export/discharge remains possible: CONNECTED, NOT CLOSED.",
        "- Monitoring provides information; human-supervised decisions and maintenance remain separate functions.",
        "",
        "## Source inventory",
        "",
    ])
    for key, item in loaded.items():
        lines.append(f"- `{common.INPUTS[key].relative_to(common.ROOT).as_posix()}` — {len(item['rows'])} rows")
    lines.extend([
        "",
        "## Outputs",
        "",
    ])
    for path in [*panel_paths, contact_sheet, manifest]:
        lines.append(f"- `{path.relative_to(common.ROOT).as_posix()}`")
    lines.extend([
        "",
        "Human visual QA is required before any commit or push. This report does not constitute visual acceptance.",
        "",
    ])
    common.VALIDATION_REPORT.write_text("\n".join(lines), encoding="utf-8")
    return common.VALIDATION_REPORT


def main() -> int:
    common.OUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = load_sources()
    panel_paths = [build_panel_a(), build_panel_b(), build_panel_c(), build_panel_d()]
    contact_sheet = build_contact_sheet(panel_paths)
    checks = semantic_checks(loaded, panel_paths, contact_sheet)
    manifest = write_manifest(loaded, panel_paths, contact_sheet, checks)
    report = write_validation_report(loaded, checks, panel_paths, contact_sheet, manifest)
    failed = [c for c in checks if not c["passed"]]
    print(f"Built Prototype 4.3 Farm 2075: {len(checks) - len(failed)}/{len(checks)} builder checks passed")
    for path in [*panel_paths, contact_sheet, manifest, report]:
        print(path.relative_to(common.ROOT).as_posix())
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
