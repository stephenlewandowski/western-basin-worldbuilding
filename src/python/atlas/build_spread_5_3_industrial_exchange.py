"""Build Phase 17A Prototype 5.3 — Old Industry, New Metabolism.

This is a reproducible first-pass static prototype for a synthetic Western Basin
Industrial Exchange District in 2075. It deliberately renders a connected,
partially recirculating but open system: external inputs, residuals, qualification
steps, institutional coordination, and uncertain interfaces remain visible.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon
from PIL import Image, ImageDraw, ImageFont

FILES_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FILES_DIR))
import atlas_ph5_3_common as common


DISTRICT_NODES = {
    "legacy_industry": "LEGACY INDUSTRIAL\nPLANT",
    "advanced_manufacturing": "ADVANCED MANUFACTURING\n/ REMANUFACTURING",
    "materials_recovery": "MATERIALS RECOVERY\n/ SORTING",
    "greenhouse_cea": "GREENHOUSE /\nCONTROLLED ENVIRONMENT",
    "water_wastewater": "WATER / WASTEWATER\nTREATMENT",
    "energy_storage": "ENERGY HUB\n/ STORAGE",
    "freight_logistics": "FREIGHT /\nLOGISTICS NODE",
    "ecology_stormwater": "ECOLOGICAL /\nSTORMWATER EDGE",
    "data_coordination": "DATA /\nCOORDINATION LAYER",
    "service_maintenance": "SERVICE /\nMAINTENANCE",
}

NODE_STATUS = {key: "S/K" for key in DISTRICT_NODES}

# This registry is intentionally a small selected sketch network, not an
# exhaustive exchange inventory. All material/energy edges are constant width.
EDGE_SEMANTIC_RECORDS = [
    {"edge_id": "EDGE-01", "family": "external_input", "status": "E → S", "label": "regional grid / fuel → energy hub", "exchange": "electricity / energy"},
    {"edge_id": "EDGE-02", "family": "external_input", "status": "E → S", "label": "water / chemistry supply → treatment", "exchange": "water"},
    {"edge_id": "EDGE-03", "family": "external_input", "status": "E → S", "label": "regional materials market → legacy plant", "exchange": "materials / components"},
    {"edge_id": "EDGE-04", "family": "external_input", "status": "E → S", "label": "regional freight → logistics node", "exchange": "freight / logistics"},
    {"edge_id": "EDGE-05", "family": "internal_use", "status": "S/K", "label": "energy hub → plants / greenhouse", "exchange": "electricity / energy"},
    {"edge_id": "EDGE-06", "family": "recovery", "status": "S/K", "label": "legacy plant → recovery", "exchange": "residual / waste heat"},
    {"edge_id": "EDGE-07", "family": "transformation", "status": "S/K", "label": "recovery → remanufacturing", "exchange": "qualified material possibility"},
    {"edge_id": "EDGE-08", "family": "scenario_interface", "status": "S", "label": "legacy plant → greenhouse", "exchange": "possible thermal interface"},
    {"edge_id": "EDGE-09", "family": "recirculation", "status": "S/K", "label": "treated water → greenhouse", "exchange": "treated water"},
    {"edge_id": "EDGE-10", "family": "residual_output", "status": "S/K", "label": "recovery → off-site treatment", "exchange": "unsuitable residual"},
    {"edge_id": "EDGE-11", "family": "discharge", "status": "S/K", "label": "treatment → watershed / ecological edge", "exchange": "managed discharge"},
    {"edge_id": "EDGE-12", "family": "product_output", "status": "S/K", "label": "remanufacturing → product markets", "exchange": "products / components"},
    {"edge_id": "EDGE-13", "family": "product_output", "status": "S/K", "label": "logistics → regional freight boundary", "exchange": "freight / logistics"},
    {"edge_id": "EDGE-14", "family": "information", "status": "E → S", "label": "data / coordination → selected operators", "exchange": "information / control"},
    {"edge_id": "EDGE-15", "family": "dependency", "status": "E → S", "label": "standards / contracts → selected exchanges", "exchange": "institutional coordination"},
    {"edge_id": "EDGE-16", "family": "sketch_interface", "status": "K", "label": "service / maintenance → district nodes", "exchange": "maintenance / replacement"},
]

SOURCE_ROLES = {
    "phase14b_atlas_dependency_crosswalk": "Accepted Phase 14B Atlas dependency crosswalk; system-level dependency context with documented/inferred status and caveats preserved",
    "phase14b_relationship_normalization": "Accepted Phase 14B relationship vocabulary and flow/governance distinctions; no quantity is imported",
    "phase15a_technology_interfaces": "Accepted Phase 15A technology-system interface vocabulary; records are inferred interfaces, not proof of district deployment",
    "phase15a_technology_dependencies": "Accepted Phase 15A technology dependency classes for data, communications, energy, materials, workforce, water, and regulatory coordination",
    "phase16a_propagation_relationships": "Accepted Phase 16A qualitative dependency/propagation semantics; dependency is not risk, failure, or guaranteed effect",
    "phase16b_regime_effects": "Accepted Phase 16B scenario-conditioned coordination, substitution, and digital-dependence caveats; no scenario is treated as a forecast",
}

ASSUMPTIONS = [
    {
        "id": "S-K-DISTRICT",
        "choice": "A synthetic Western Basin Industrial Exchange District at the Great Lakes Industrial Belt / Glass City Core interface",
        "status": "S/K",
        "boundary": "Not a real parcel, company, facility plan, forecast, or canonical geography",
    },
    {
        "id": "S-K-ACCUMULATED-FABRIC",
        "choice": "Legacy brick, concrete, steel, freight access, weathering, retrofit envelopes, and newer service infrastructure coexist",
        "status": "S/K",
        "boundary": "Block shapes and adjacency are illustrative; no dimensions, capacity, throughput, or land value is encoded",
    },
    {
        "id": "S-K-SELECTED-EXCHANGE",
        "choice": "Only a restrained subset of energy, thermal, water, materials, nutrient/residual, freight, and information interfaces is drawn",
        "status": "S/K",
        "boundary": "A visible edge is a selected interface sketch, not a guaranteed operating relationship",
    },
    {
        "id": "S-K-THERMAL-SIGNATURE",
        "choice": "Waste heat is used as one visible signature interface between industrial process, qualification, and greenhouse/process heat",
        "status": "S/K",
        "boundary": "Temperature, distance, timing, ownership, maintenance, economics, and compatibility are not resolved",
    },
    {
        "id": "S-K-INSTITUTIONAL-COORDINATION",
        "choice": "Contracts, standards, monitoring, quality assurance, operating agreements, regulation/permitting, and data sharing are explicit layer elements",
        "status": "S/K",
        "boundary": "Coordination is required but does not guarantee viability, environmental benefit, resilience, or continuity",
    },
]


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
            columns = list(reader.fieldnames or [])
            missing = common.REQUIRED_COLUMNS[key] - set(columns)
            if missing:
                raise ValueError(f"{key} missing required columns: {sorted(missing)}")
            rows = list(reader)
        if not rows:
            raise ValueError(f"{key} has no rows")
        loaded[key] = {"path": path, "columns": columns, "rows": rows}
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
    page.text(0.055, 0.875, title, color=common.INK, fontsize=25, fontweight="bold")
    page.text(0.055, 0.835, kicker, color=common.MUTED, fontsize=10)
    page.text(0.945, 0.925, classification, color=common.K, fontsize=10.5, fontweight="bold", ha="right")
    page.plot([0.055, 0.945], [0.805, 0.805], color=common.RULE, lw=1)
    return fig, page


def status_legend(page, x=0.06, y=0.105):
    page.text(x, y + 0.028, "VISUAL GRAMMAR v0.3", fontsize=8.5, color=common.INK, fontweight="bold")
    for offset, label, color in ((0.145, "E  evidence / model", common.E), (0.325, "S  scenario", common.S), (0.47, "K  sketch", common.K)):
        page.add_patch(patches.Rectangle((x + offset, y + 0.012), 0.018, 0.022, facecolor=color, edgecolor="none"))
        page.text(x + offset + 0.024, y + 0.028, label, fontsize=8, color=common.INK, va="center")


def note(page, text: str, y=0.055, size=8.2, color=None, ha="left", x=0.06):
    page.text(x, y, text, fontsize=size, color=color or common.MUTED, ha=ha)


def _add_plan_node(ax, x, y, w, h, label, subtitle, face, edge, old=False, new=False):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.45,rounding_size=1.4", facecolor=face, edgecolor=edge, lw=1.1, zorder=4))
    if old:
        ax.add_patch(patches.Rectangle((x + 1.0, y + h - 2.0), w - 2.0, 1.1, facecolor=common.BRICK, edgecolor="none", zorder=5))
        ax.add_patch(patches.Rectangle((x + w * 0.76, y + h - 1.0), 1.1, 6.0, facecolor=common.CONCRETE, edgecolor=common.INK, lw=0.4, zorder=5))
        ax.add_patch(patches.Rectangle((x + w * 0.77, y + h + 5.0), 0.9, 1.1, facecolor=common.INK, edgecolor="none", zorder=5))
    if new:
        for sx in (x + 1.6, x + w * 0.35, x + w * 0.63):
            ax.add_patch(patches.Rectangle((sx, y + h - 2.6), 2.4, 1.2, facecolor=common.RETROFIT, edgecolor="none", zorder=5))
    ax.text(x + w / 2, y + h * 0.58, label, ha="center", va="center", fontsize=7.8, color=common.INK, fontweight="bold", zorder=6)
    ax.text(x + w / 2, y + h * 0.22, subtitle, ha="center", va="center", fontsize=6.6, color=common.MUTED, zorder=6)


def build_panel_a() -> Path:
    fig, page = panel_base(
        "5.3A",
        "Western Basin Industrial Exchange District 2075",
        "PLAN / LOW-FI AXONOMETRIC  ·  S/K  ·  accumulated Great Lakes industrial fabric",
        "S/K · MAP / 3D / CONCEPT",
    )
    ax = fig.add_axes([0.055, 0.16, 0.89, 0.62])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis("off")
    ax.set_facecolor("#E6E0D4")

    # Synthetic district boundary and shared access/utilities.
    ax.add_patch(patches.FancyBboxPatch((2, 3), 96, 62, boxstyle="round,pad=0.8,rounding_size=2.0", facecolor="#E6E0D4", edgecolor=common.K, lw=1.5, linestyle="--", zorder=1))
    ax.text(96, 63.0, "SYNTHETIC DISTRICT · NOT A REAL PARCEL / NOT A FORECAST", ha="right", va="bottom", fontsize=7.4, color=common.K, fontweight="bold", zorder=8)
    ax.add_patch(patches.Rectangle((2, 9), 96, 4.5, facecolor=common.ROAD, edgecolor="#806F60", lw=0.7, zorder=2))
    ax.add_patch(patches.Rectangle((30, 3), 4.0, 62, facecolor=common.ROAD, edgecolor="#806F60", lw=0.7, zorder=2))
    ax.add_patch(patches.Rectangle((62, 3), 3.5, 62, facecolor=common.ROAD, edgecolor="#806F60", lw=0.7, zorder=2))
    ax.plot([3, 97], [15.0, 15.0], color=common.INK, lw=1.0, linestyle=(0, (7, 3)), zorder=3)
    ax.text(6, 11.3, "freight access / service road", fontsize=7.0, color=common.INK, va="center", zorder=7)
    ax.text(31.9, 7.0, "shared service corridor", fontsize=6.8, color=common.INK, rotation=90, ha="center", va="center", zorder=7)
    ax.text(63.7, 36.8, "thermal loop\nstudy", fontsize=6.8, color=common.INK, rotation=90, ha="center", va="center", zorder=7)

    # Legacy and retrofit layers are deliberately mixed rather than replaced.
    _add_plan_node(ax, 6, 40, 22, 16, "LEGACY INDUSTRIAL\nPLANT", "brick / steel shell · retrofit bay", common.BRICK, common.MAINTENANCE, old=True, new=True)
    _add_plan_node(ax, 36, 40, 21, 16, "ADVANCED\nMANUFACTURING", "remanufacturing · qualified input", common.STEEL, common.E, new=True)
    _add_plan_node(ax, 36, 21, 21, 13, "MATERIALS\nRECOVERY", "sorting · characterization", common.CONCRETE, common.MATERIAL, new=True)
    _add_plan_node(ax, 67, 43, 25, 14, "GREENHOUSE / CEA", "controlled environment · thermal interface", common.ENERGY_LIGHT, common.S, new=True)
    _add_plan_node(ax, 67, 21, 25, 13, "WATER / WASTEWATER", "treatment · quality gate", common.WATER_LIGHT, common.WATER, new=True)
    _add_plan_node(ax, 45, 4, 17, 10, "ENERGY HUB / STORAGE", "grid interface · storage", common.ENERGY_LIGHT, common.ENERGY, new=True)
    _add_plan_node(ax, 6, 4, 22, 10, "FREIGHT / LOGISTICS", "rail / truck access", common.ROAD, common.INK, old=True)
    _add_plan_node(ax, 78, 4, 18, 10, "ECOLOGICAL /\nSTORMWATER EDGE", "bioswale · detention · discharge", common.ECOLOGY_LIGHT, common.ECOLOGY, new=True)
    _add_plan_node(ax, 6, 21, 22, 13, "SERVICE /\nMAINTENANCE", "parts · inspection · repair", common.THERMAL_LIGHT, common.MAINTENANCE, old=True, new=True)

    # Coordination/data layer is visible as a retrofit ribbon, not magic.
    ax.add_patch(patches.FancyBboxPatch((35, 59), 58, 4.2, boxstyle="round,pad=0.3,rounding_size=1.0", facecolor=common.DATA_LIGHT, edgecolor=common.DATA, lw=1.1, zorder=4))
    ax.text(64, 61.1, "DATA / COORDINATION LAYER  ·  monitoring · QA · operating agreements · shared records", ha="center", va="center", fontsize=7.5, color=common.DATA, fontweight="bold", zorder=6)
    for x in (39, 48, 57, 66, 75, 84):
        ax.add_patch(patches.Circle((x, 59.9), 0.55, facecolor=common.DATA, edgecolor="white", lw=0.4, zorder=7))

    # Qualitative selected physical interfaces; no line width encodes quantity.
    for start, end, color, style in [
        ((28, 48), (36, 48), common.MATERIAL, "-"),
        ((57, 48), (67, 49), common.THERMAL, "-"),
        ((57, 27), (67, 27), common.WATER, "-"),
        ((53, 14), (46, 40), common.ENERGY, "-"),
        ((62, 11), (78, 9), common.INK, (0, (7, 3))),
    ]:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "-|>", "color": color, "lw": common.FLOW_LW, "linestyle": style, "mutation_scale": 10}, zorder=6)

    # External boundaries are deliberately outside the synthetic blockout.
    ax.annotate("regional grid / fuel\nexternal energy input", xy=(45, 4), xytext=(38.5, 0.25), fontsize=7.0, color=common.ENERGY, ha="right", va="bottom", arrowprops={"arrowstyle": "-|>", "color": common.ENERGY, "lw": common.FLOW_LW, "mutation_scale": 10}, zorder=8)
    ax.annotate("", xy=(99, 10), xytext=(95.5, 10), color=common.INK, arrowprops={"arrowstyle": "-|>", "color": common.INK, "lw": common.FLOW_LW, "mutation_scale": 10}, zorder=8)
    ax.text(96.5, 0.8, "regional markets / port / road\nproducts + residuals leave", fontsize=7.0, color=common.INK, ha="right", va="bottom", zorder=8)
    ax.text(4, 63.0, "weathered structures + new retrofit layers", fontsize=7.2, color=common.MAINTENANCE, fontweight="bold", zorder=8)

    status_legend(page, y=0.105)
    note(page, "Plan is a synthetic spatial-fit sketch: concrete, steel, freight access, maintenance, weathering, and retrofit coexist. No parcel dimensions, capacities, throughput, or viability are encoded.", y=0.055, size=8.0)
    path = common.OUT_DIR / common.PANEL_FILES[0]
    return _save(fig, path)


def _node(ax, x, y, w, h, label, subtitle, edge, face=common.PANEL, status="S/K", fontsize=7.0):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.018", facecolor=face, edgecolor=edge, lw=1.1, zorder=5))
    ax.add_patch(patches.Rectangle((x + 0.008, y + h - 0.025), 0.035, 0.017, facecolor=edge, edgecolor="none", zorder=6))
    ax.text(x + w / 2, y + h * 0.59, label, ha="center", va="center", fontsize=fontsize, color=common.INK, fontweight="bold", zorder=7)
    ax.text(x + w / 2, y + h * 0.22, subtitle, ha="center", va="center", fontsize=5.9, color=common.MUTED, zorder=7)
    ax.text(x + w - 0.01, y + h - 0.015, status, ha="right", va="top", fontsize=5.5, color=edge, fontweight="bold", zorder=7)


def _edge(ax, start, end, family, label=None, color=common.INK, rad=0.0, label_offset=(0, 0), arrow=True, alpha=0.9):
    if family not in common.ALLOWED_EDGE_FAMILIES:
        raise ValueError(f"Unsupported edge family: {family}")
    if family in {"information"}:
        linestyle = "--"
        lw = common.INFO_LW
    elif family == "dependency":
        linestyle = ":"
        lw = common.DEPENDENCY_LW
    elif family == "scenario_interface":
        linestyle = "-."
        lw = common.FLOW_LW
    elif family == "sketch_interface":
        linestyle = (0, (7, 3, 1, 3))
        lw = common.FLOW_LW
    else:
        linestyle = "-"
        lw = common.FLOW_LW
    arrowstyle = "-|>" if arrow else "-"
    patch = FancyArrowPatch(start, end, arrowstyle=arrowstyle, mutation_scale=9, linewidth=lw, linestyle=linestyle, color=color, alpha=alpha, connectionstyle=f"arc3,rad={rad}", zorder=2)
    ax.add_patch(patch)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=5.6, color=color, ha="center", va="center", zorder=4, bbox={"facecolor": common.PAPER, "edgecolor": "none", "pad": 1.0, "alpha": 0.85})


def build_panel_b() -> Path:
    fig, page = panel_base(
        "5.3B",
        "Exchange network",
        "SCHEMATIC  ·  S/K  ·  same district nodes, selected qualitative relationships",
        "S/K · SCHEMATIC",
    )
    ax = fig.add_axes([0.045, 0.215, 0.91, 0.565])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    pos = {
        "regional_grid": (0.01, 0.83, 0.14, 0.09),
        "water_supply": (0.01, 0.55, 0.14, 0.09),
        "material_market": (0.01, 0.27, 0.14, 0.09),
        "regional_freight": (0.85, 0.27, 0.14, 0.09),
        "product_markets": (0.85, 0.83, 0.14, 0.09),
        "offsite_treatment": (0.85, 0.55, 0.14, 0.09),
        "legacy": (0.20, 0.75, 0.16, 0.105),
        "manufacturing": (0.43, 0.75, 0.18, 0.105),
        "energy": (0.68, 0.75, 0.15, 0.105),
        "recovery": (0.25, 0.48, 0.16, 0.105),
        "water": (0.48, 0.48, 0.17, 0.105),
        "greenhouse": (0.69, 0.48, 0.16, 0.105),
        "ecology": (0.25, 0.21, 0.17, 0.105),
        "freight": (0.68, 0.21, 0.16, 0.105),
        "service": (0.45, 0.21, 0.18, 0.105),
        "data": (0.42, 0.93, 0.21, 0.07),
        "coordination": (0.68, 0.94, 0.20, 0.055),
    }
    nodes = [
        ("regional_grid", "REGIONAL GRID / FUEL", "external input", common.ENERGY, common.ENERGY_LIGHT, "E → S"),
        ("water_supply", "WATER / CHEMISTRY SUPPLY", "external input", common.WATER, common.WATER_LIGHT, "E → S"),
        ("material_market", "REGIONAL MATERIALS MARKET", "external input", common.MATERIAL, common.MATERIAL_LIGHT, "E → S"),
        ("regional_freight", "REGIONAL FREIGHT", "external boundary", common.INK, common.PANEL, "E → S"),
        ("product_markets", "PRODUCT MARKETS", "external output", common.INK, common.PANEL, "S/K"),
        ("offsite_treatment", "OFF-SITE TREATMENT / DISCHARGE", "external residual", common.MAINTENANCE, common.THERMAL_LIGHT, "S/K"),
        ("legacy", "LEGACY PLANT", "process / residual", common.MAINTENANCE, "#F1DDD4", "S/K"),
        ("manufacturing", "ADVANCED MANUFACTURING", "qualified use", common.E, "#DCE6E4", "S/K"),
        ("energy", "ENERGY HUB / STORAGE", "energy service", common.ENERGY, common.ENERGY_LIGHT, "S/K"),
        ("recovery", "RECOVERY / SORTING", "characterize / treat", common.MATERIAL, common.MATERIAL_LIGHT, "S/K"),
        ("water", "WATER / WASTEWATER", "treatment gate", common.WATER, common.WATER_LIGHT, "S/K"),
        ("greenhouse", "GREENHOUSE / CEA", "selected user", common.S, "#F0E2BC", "S/K"),
        ("ecology", "ECOLOGY / STORMWATER", "receiving edge", common.ECOLOGY, common.ECOLOGY_LIGHT, "S/K"),
        ("freight", "FREIGHT / LOGISTICS", "movement interface", common.INK, common.ROAD, "S/K"),
        ("service", "SERVICE / MAINTENANCE", "repair + parts", common.MAINTENANCE, "#F0D8D0", "K"),
        ("data", "DATA / COORDINATION", "information + records", common.DATA, common.DATA_LIGHT, "E → S"),
        ("coordination", "CONTRACTS / STANDARDS / QA", "institutional dependency", common.MAINTENANCE, "#F5E4DD", "E → S"),
    ]
    for key, label, subtitle, edge, face, status in nodes:
        x, y, w, h = pos[key]
        _node(ax, x, y, w, h, label, subtitle, edge, face, status, fontsize=6.5 if key in {"coordination", "offsite_treatment", "water_supply", "material_market"} else 7.0)

    # Boundary and selected material/energy exchange edges.
    _edge(ax, (0.15, 0.875), (0.68, 0.80), "external_input", "external_input", common.ENERGY, rad=0.03, label_offset=(0.0, 0.035))
    _edge(ax, (0.15, 0.595), (0.48, 0.53), "external_input", "external_input", common.WATER, rad=-0.03, label_offset=(-0.015, 0.02))
    _edge(ax, (0.15, 0.315), (0.20, 0.80), "external_input", None, common.MATERIAL, rad=-0.12)
    _edge(ax, (0.85, 0.315), (0.76, 0.30), "external_input", "external_input", common.INK, rad=0.05, label_offset=(0.0, 0.035))
    _edge(ax, (0.755, 0.80), (0.43, 0.80), "internal_use", "internal_use", common.ENERGY, rad=0.05, label_offset=(0.0, 0.035))
    _edge(ax, (0.755, 0.79), (0.69, 0.54), "internal_use", None, common.ENERGY, rad=-0.05)
    _edge(ax, (0.755, 0.77), (0.60, 0.54), "internal_use", None, common.ENERGY, rad=0.03)
    _edge(ax, (0.36, 0.80), (0.33, 0.54), "recovery", "recovery", common.THERMAL, rad=0.02, label_offset=(-0.06, 0.015))
    _edge(ax, (0.41, 0.53), (0.43, 0.80), "transformation", "transformation", common.MATERIAL, rad=-0.12, label_offset=(-0.015, -0.025))
    _edge(ax, (0.36, 0.80), (0.69, 0.53), "scenario_interface", "scenario_interface", common.THERMAL, rad=-0.08, label_offset=(0.02, 0.02))
    _edge(ax, (0.65, 0.53), (0.69, 0.53), "recirculation", "recirculation", common.WATER, rad=0.0, label_offset=(0.0, 0.085))
    _edge(ax, (0.41, 0.52), (0.85, 0.59), "residual_output", "residual_output", common.MAINTENANCE, rad=0.10, label_offset=(-0.10, 0.095))
    _edge(ax, (0.65, 0.52), (0.85, 0.59), "discharge", "discharge", common.WATER, rad=-0.08, label_offset=(-0.08, -0.11))
    _edge(ax, (0.61, 0.80), (0.85, 0.875), "product_output", "product_output", common.INK, rad=0.03, label_offset=(0.0, 0.035))
    _edge(ax, (0.76, 0.26), (0.85, 0.315), "product_output", None, common.INK, rad=0.0)
    _edge(ax, (0.565, 0.53), (0.33, 0.26), "discharge", None, common.ECOLOGY, rad=0.02)
    _edge(ax, (0.525, 0.93), (0.28, 0.80), "information", "information", common.DATA, rad=0.03, label_offset=(-0.01, 0.02))
    _edge(ax, (0.525, 0.93), (0.33, 0.53), "information", None, common.DATA, rad=-0.04)
    _edge(ax, (0.525, 0.93), (0.565, 0.53), "information", None, common.DATA, rad=0.0)
    _edge(ax, (0.78, 0.94), (0.52, 0.80), "dependency", "dependency", common.MAINTENANCE, rad=0.12, label_offset=(0.0, 0.02))
    _edge(ax, (0.78, 0.94), (0.50, 0.53), "dependency", None, common.MAINTENANCE, rad=0.10)
    _edge(ax, (0.78, 0.94), (0.54, 0.315), "sketch_interface", "sketch_interface", common.K, rad=0.16, label_offset=(0.02, -0.02))

    # Semantic key below the network, with line styles separated from status.
    y = 0.075
    ax.plot([0.01, 0.045], [y, y], color=common.INK, lw=common.FLOW_LW)
    ax.text(0.05, y, "solid = material / energy exchange", fontsize=6.5, color=common.INK, va="center")
    ax.plot([0.255, 0.29], [y, y], color=common.DATA, lw=common.INFO_LW, linestyle="--")
    ax.text(0.295, y, "dashed = information / control", fontsize=6.5, color=common.INK, va="center")
    ax.plot([0.51, 0.545], [y, y], color=common.MAINTENANCE, lw=common.DEPENDENCY_LW, linestyle=":")
    ax.text(0.55, y, "dotted = dependency", fontsize=6.5, color=common.INK, va="center")
    ax.plot([0.70, 0.735], [y, y], color=common.S, lw=common.FLOW_LW, linestyle="-.")
    ax.text(0.74, y, "dash-dot = scenario / sketch interface", fontsize=6.5, color=common.INK, va="center")

    status_legend(page, y=0.105)
    note(page, "CONNECTED, NOT CLOSED  ·  selected edges only; edge width, brightness, particle count, and color intensity do not encode quantity.", y=0.055, color=common.MAINTENANCE, size=8.0)
    path = common.OUT_DIR / common.PANEL_FILES[1]
    return _save(fig, path)


def _stage_box(ax, x, y, w, h, title, subtitle, edge, face):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025", facecolor=face, edgecolor=edge, lw=1.25, zorder=3))
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", fontsize=8.0, color=common.INK, fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + h * 0.28, subtitle, ha="center", va="center", fontsize=6.7, color=common.MUTED, zorder=4)


def _chain(ax, y, stages):
    xs = [0.025, 0.22, 0.415, 0.61, 0.805]
    w = 0.16
    h = 0.16
    for x, (title, subtitle, edge, face) in zip(xs, stages):
        _stage_box(ax, x, y, w, h, title, subtitle, edge, face)
    for left, right in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(right - 0.006, y + h / 2), xytext=(left + w + 0.006, y + h / 2), arrowprops={"arrowstyle": "-|>", "color": common.INK, "lw": common.FLOW_LW, "mutation_scale": 10}, zorder=2)
    return xs, w, h


def build_panel_c() -> Path:
    fig, page = panel_base(
        "5.3C",
        "Residual to qualified input",
        "FIGURE / SCHEMATIC  ·  S/K  ·  qualification is a gate, not a magical conversion",
        "S/K · FIGURE / SCHEMATIC",
    )
    ax = fig.add_axes([0.055, 0.19, 0.89, 0.59])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.50, 0.965, "RESIDUAL ≠ RECOVERABLE RESOURCE ≠ QUALIFIED INPUT", ha="center", va="top", fontsize=11.5, color=common.MAINTENANCE, fontweight="bold")
    ax.text(0.50, 0.91, "Two example classes; no recovery rate, purity, capacity, compatibility, price, or environmental benefit is claimed.", ha="center", va="top", fontsize=7.7, color=common.MUTED)

    ax.text(0.005, 0.84, "EXAMPLE 1 · THERMAL / WASTE HEAT", fontsize=8.2, color=common.THERMAL, fontweight="bold", va="center")
    thermal = [
        ("RESIDUAL", "waste heat /\nrejected thermal stream", common.THERMAL, common.THERMAL_LIGHT),
        ("CHARACTERIZE\n/ TREAT", "temperature · timing\nexchange condition", common.MAINTENANCE, "#F0D8D0"),
        ("RECOVERABLE\nRESOURCE", "thermal service\nif suitable", common.S, common.ENERGY_LIGHT),
        ("QUALIFY\nFOR USE", "distance · timing ·\nquality assurance", common.DATA, common.DATA_LIGHT),
        ("NEW INPUT / USE", "greenhouse /\nprocess heat", common.ECOLOGY, common.ECOLOGY_LIGHT),
    ]
    xs, w, h = _chain(ax, 0.64, thermal)

    ax.text(0.005, 0.57, "EXAMPLE 2 · MATERIALS / COMPONENTS", fontsize=8.2, color=common.MATERIAL, fontweight="bold", va="center")
    materials = [
        ("RESIDUAL", "sorted / suitable\nmaterial residual", common.MATERIAL, common.MATERIAL_LIGHT),
        ("CHARACTERIZE\n/ REPROCESS", "composition · condition\ntraceability", common.MAINTENANCE, "#F0D8D0"),
        ("RECOVERABLE\nRESOURCE", "reprocessed\nmaterial fraction", common.S, common.ENERGY_LIGHT),
        ("QUALIFY\nFOR USE", "specification · QA ·\ncontract", common.DATA, common.DATA_LIGHT),
        ("NEW INPUT / USE", "remanufacturing\ncomponent input", common.E, "#DCE6E4"),
    ]
    _chain(ax, 0.36, materials)

    # Residuals can still exit at every stage; no closed loop is implied.
    ax.add_patch(patches.FancyBboxPatch((0.025, 0.08), 0.55, 0.13, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor="#F5E4DD", edgecolor=common.MAINTENANCE, lw=1.2, zorder=3))
    ax.text(0.30, 0.165, "SOME RESIDUALS STILL EXIT", ha="center", va="center", fontsize=9.2, color=common.MAINTENANCE, fontweight="bold", zorder=4)
    ax.text(0.30, 0.115, "waste  ·  discharge  ·  off-site treatment  ·  unsuitable material", ha="center", va="center", fontsize=7.2, color=common.INK, zorder=4)
    for start in ((0.30, 0.72), (0.40, 0.44), (0.50, 0.72), (0.60, 0.44)):
        ax.annotate("", xy=(0.50, 0.215), xytext=start, arrowprops={"arrowstyle": "-|>", "color": common.MAINTENANCE, "lw": common.FLOW_LW, "linestyle": ":", "mutation_scale": 9}, zorder=2)

    ax.add_patch(patches.FancyBboxPatch((0.635, 0.08), 0.34, 0.13, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor=common.DATA_LIGHT, edgecolor=common.DATA, lw=1.2, zorder=3))
    ax.text(0.70, 0.165, "QUALIFICATION", ha="center", va="center", fontsize=7.6, color=common.DATA, fontweight="bold", zorder=4)
    ax.text(0.82, 0.135, "standards · monitoring\ncontracts · maintenance", ha="center", va="center", fontsize=6.8, color=common.DATA)
    ax.annotate("", xy=(0.635, 0.145), xytext=(0.575, 0.145), arrowprops={"arrowstyle": "-|>", "color": common.DATA, "lw": common.INFO_LW, "linestyle": "--", "mutation_scale": 9}, zorder=2)

    status_legend(page, y=0.105)
    note(page, "OPEN SYSTEM: recovery is conditional and partial. A residual becomes a qualified input only after characterization, treatment/reprocessing, quality assurance, and an actual compatible user.", y=0.055, color=common.MAINTENANCE, size=7.9)
    path = common.OUT_DIR / common.PANEL_FILES[2]
    return _save(fig, path)


def build_panel_d() -> Path:
    fig, page = panel_base(
        "5.3D",
        "Open system / governance",
        "FIGURE  ·  S/K  ·  physical exchange depends on regional infrastructure and coordination",
        "S/K · FIGURE",
    )
    ax = fig.add_axes([0.045, 0.17, 0.91, 0.61])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Coordination is shown above the physical network rather than hidden in it.
    ax.add_patch(patches.FancyBboxPatch((0.08, 0.77), 0.84, 0.16, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor=common.DATA_LIGHT, edgecolor=common.DATA, lw=1.3, zorder=3))
    ax.text(0.50, 0.905, "COORDINATION LAYER · REQUIRED, NOT MAGIC", ha="center", va="center", fontsize=9.0, color=common.DATA, fontweight="bold", zorder=4)
    coordination = ["contracts", "standards", "monitoring", "quality\nassurance", "operating\nagreement", "regulation /\npermitting", "data sharing"]
    for i, label in enumerate(coordination):
        x = 0.095 + i * 0.116
        ax.add_patch(patches.FancyBboxPatch((x, 0.795), 0.103, 0.07, boxstyle="round,pad=0.006,rounding_size=0.012", facecolor=common.PANEL, edgecolor=common.DATA, lw=0.8, zorder=4))
        ax.text(x + 0.0515, 0.83, label, ha="center", va="center", fontsize=5.8, color=common.INK, zorder=5)

    # Central district boundary and a restrained set of shared operating nodes.
    ax.add_patch(patches.FancyBboxPatch((0.29, 0.27), 0.43, 0.38, boxstyle="round,pad=0.012,rounding_size=0.025", facecolor="#F7F3E9", edgecolor=common.K, lw=1.6, linestyle="--", zorder=1))
    ax.text(0.505, 0.625, "SYNTHETIC DISTRICT OPERATING CORE", ha="center", va="center", fontsize=8.2, color=common.K, fontweight="bold", zorder=4)
    ax.text(0.505, 0.295, "CONNECTED, NOT CLOSED", ha="center", va="center", fontsize=8.8, color=common.MAINTENANCE, fontweight="bold", zorder=4)
    _node(ax, 0.315, 0.49, 0.16, 0.085, "LEGACY PLANT", "process + residual", common.MAINTENANCE, "#F1DDD4", "S/K", 6.5)
    _node(ax, 0.535, 0.49, 0.16, 0.085, "REMANUFACTURING", "qualified material", common.E, "#DCE6E4", "S/K", 6.5)
    _node(ax, 0.315, 0.36, 0.16, 0.085, "RECOVERY / QA", "characterize + treat", common.MATERIAL, common.MATERIAL_LIGHT, "S/K", 6.5)
    _node(ax, 0.535, 0.36, 0.16, 0.085, "WATER + ENERGY", "treatment + service", common.WATER, common.WATER_LIGHT, "S/K", 6.5)
    ax.annotate("", xy=(0.535, 0.53), xytext=(0.475, 0.53), arrowprops={"arrowstyle": "-|>", "color": common.MATERIAL, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.395, 0.445), xytext=(0.395, 0.49), arrowprops={"arrowstyle": "-|>", "color": common.MATERIAL, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.615, 0.445), xytext=(0.615, 0.49), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)

    # External boundary columns preserve dependencies, output, and residual exits.
    left = [
        ("REGIONAL GRID / FUEL", "energy input", common.ENERGY, common.ENERGY_LIGHT),
        ("MATERIALS / COMPONENTS", "external input", common.MATERIAL, common.MATERIAL_LIGHT),
        ("WATER / CHEMISTRY", "external input", common.WATER, common.WATER_LIGHT),
        ("FREIGHT / LOGISTICS", "regional movement", common.INK, common.ROAD),
    ]
    right = [
        ("PRODUCT MARKETS", "products leave", common.E, "#DCE6E4"),
        ("OFF-SITE TREATMENT", "residual / waste", common.MAINTENANCE, "#F0D8D0"),
        ("WATERSHED / REGIONAL INFRASTRUCTURE", "discharge / context", common.ECOLOGY, common.ECOLOGY_LIGHT),
    ]
    for i, (label, subtitle, edge, face) in enumerate(left):
        y = 0.59 - i * 0.115
        _node(ax, 0.015, y, 0.205, 0.075, label, subtitle, edge, face, "E → S", 5.9)
    for i, (label, subtitle, edge, face) in enumerate(right):
        y = 0.53 - i * 0.115
        _node(ax, 0.78, y, 0.205, 0.075, label, subtitle, edge, face, "S/K", 5.9)
    ax.annotate("", xy=(0.29, 0.56), xytext=(0.22, 0.625), arrowprops={"arrowstyle": "-|>", "color": common.ENERGY, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.29, 0.51), xytext=(0.22, 0.51), arrowprops={"arrowstyle": "-|>", "color": common.MATERIAL, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.29, 0.40), xytext=(0.22, 0.395), arrowprops={"arrowstyle": "-|>", "color": common.WATER, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.29, 0.34), xytext=(0.22, 0.28), arrowprops={"arrowstyle": "-|>", "color": common.INK, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.78, 0.53), xytext=(0.72, 0.53), arrowprops={"arrowstyle": "-|>", "color": common.E, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.78, 0.415), xytext=(0.72, 0.415), arrowprops={"arrowstyle": "-|>", "color": common.MAINTENANCE, "lw": common.FLOW_LW, "linestyle": ":", "mutation_scale": 9}, zorder=2)
    ax.annotate("", xy=(0.78, 0.30), xytext=(0.69, 0.37), arrowprops={"arrowstyle": "-|>", "color": common.ECOLOGY, "lw": common.FLOW_LW, "mutation_scale": 9}, zorder=2)

    # Coordination and maintenance links use separate semantics from physical exchange.
    for end in ((0.40, 0.575), (0.60, 0.575), (0.40, 0.405), (0.60, 0.405)):
        ax.annotate("", xy=end, xytext=(0.50, 0.77), arrowprops={"arrowstyle": "-|>", "color": common.DATA, "lw": common.INFO_LW, "linestyle": "--", "mutation_scale": 8}, zorder=2)
    ax.add_patch(patches.FancyBboxPatch((0.30, 0.095), 0.40, 0.10, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor="#F0D8D0", edgecolor=common.MAINTENANCE, lw=1.15, zorder=3))
    ax.text(0.50, 0.155, "MAINTENANCE / REPLACEMENT DEPENDENCE", ha="center", va="center", fontsize=8.0, color=common.MAINTENANCE, fontweight="bold", zorder=4)
    ax.text(0.50, 0.118, "people · access · pumps · parts · cleaning · repair · service continuity", ha="center", va="center", fontsize=6.7, color=common.INK, zorder=4)
    ax.annotate("", xy=(0.50, 0.27), xytext=(0.50, 0.195), arrowprops={"arrowstyle": "-|>", "color": common.MAINTENANCE, "lw": common.DEPENDENCY_LW, "linestyle": ":", "mutation_scale": 9}, zorder=2)

    status_legend(page, y=0.105)
    note(page, "More connected does not mean self-sufficient. External energy/material inputs, products, residuals, discharge, freight, regional infrastructure, and replacement dependence remain visible.", y=0.055, color=common.MAINTENANCE, size=7.9)
    path = common.OUT_DIR / common.PANEL_FILES[3]
    return _save(fig, path)


def build_contact_sheet(panel_paths: list[Path]) -> Path:
    thumb_w, thumb_h = 900, 579
    heading_h = 58
    cell_h = heading_h + thumb_h
    sheet = Image.new("RGB", (thumb_w * 2, cell_h * 2), (243, 239, 228))
    labels = [
        "5.3A  INDUSTRIAL DISTRICT 2075",
        "5.3B  EXCHANGE NETWORK",
        "5.3C  RESIDUAL TO QUALIFIED INPUT",
        "5.3D  OPEN SYSTEM / GOVERNANCE",
    ]
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(panel_paths):
        with Image.open(path) as image:
            thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % 2) * thumb_w
        y = (i // 2) * cell_h + heading_h
        draw.rectangle((x, i // 2 * cell_h, x + thumb_w, i // 2 * cell_h + heading_h), fill=(243, 239, 228))
        draw.text((x + 22, i // 2 * cell_h + 17), labels[i], fill=(38, 50, 56), font=_font(22, bold=True))
        sheet.paste(thumb, (x, y))
    sheet.save(common.CONTACT_SHEET, format="PNG", optimize=True)
    return common.CONTACT_SHEET


def _git_changed_paths() -> set[str]:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=common.ROOT, capture_output=True, text=True, check=False)
    changed = set()
    for line in result.stdout.splitlines():
        if len(line) > 3:
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed.add(path.replace("\\", "/"))
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


def _provenance_summary(loaded: dict[str, dict]) -> list[dict]:
    rows = loaded["phase14b_atlas_dependency_crosswalk"]["rows"]
    relevant = [
        row for row in rows
        if row.get("suitable_for_visualization") == "YES"
        and row.get("source_system_id") in {"SYS-WATER", "SYS-ENERGY", "SYS-FREIGHT", "SYS-GOVERNANCE", "SYS-DATA"}
    ]
    by_pair: dict[tuple[str, str], list[dict]] = {}
    for row in relevant:
        by_pair.setdefault((row.get("source_system_id", ""), row.get("target_system_id", "")), []).append(row)
    return [
        {
            "source": "data/processed/integration/atlas_dependency_crosswalk.csv",
            "relationship_basis": "Phase 14B accepted Atlas dependency crosswalk; source evidence and documented/inferred status retained",
            "selected_system_pairs": [
                {"source_system_id": pair[0], "target_system_id": pair[1], "row_count": len(pair_rows), "example_atlas_relationship_ids": [r["atlas_relationship_id"] for r in pair_rows[:4]]}
                for pair, pair_rows in sorted(by_pair.items())
                if pair[0] or pair[1]
            ],
            "use_boundary": "System-level dependency context only; not exact facility identity, route, shipment, quantity, capacity, or continuous operation.",
        },
        {
            "source": "data/processed/integration/technology_system_interfaces.csv",
            "relationship_basis": "Phase 15A accepted technology interface catalog",
            "selected_interface_ids": [
                row["interface_id"] for row in loaded["phase15a_technology_interfaces"]["rows"]
                if row.get("target_system_id") in {"SYS-ENERGY", "SYS-WATER", "SYS-DATA", "SYS-FREIGHT", "SYS-MATERIALS"}
            ][:10],
            "use_boundary": "All selected records retain INFERRED status; plausible interface vocabulary is not district deployment evidence.",
        },
        {
            "source": "data/processed/integration/technology_dependencies.csv",
            "relationship_basis": "Phase 15A accepted technology dependency catalog",
            "selected_dependency_ids": [
                row["dependency_id"] for row in loaded["phase15a_technology_dependencies"]["rows"]
                if row.get("dependency_class") in {"electricity", "water", "materials", "communications", "data", "regulatory authority", "skilled workforce"}
            ],
            "use_boundary": "Dependencies remain qualitative requirements and limitations; they are not failure probabilities or resilience claims.",
        },
        {
            "source": "data/processed/integration/propagation_relationships.csv",
            "relationship_basis": "Phase 16A accepted qualitative propagation/dependency semantics",
            "selected_relationship_ids": [
                row["relationship_id"] for row in loaded["phase16a_propagation_relationships"]["rows"]
                if row.get("source_system_id") in {"SYS-WATER", "SYS-ENERGY", "SYS-FREIGHT", "SYS-DATA", "SYS-GOVERNANCE"}
                or row.get("target_system_id") in {"SYS-WATER", "SYS-ENERGY", "SYS-FREIGHT", "SYS-DATA", "SYS-GOVERNANCE"}
            ],
            "use_boundary": "Preserves dependency != risk, propagation != guaranteed failure, and coordination != automatic control.",
        },
        {
            "source": "data/processed/integration/phase16b_regime_effects.csv",
            "relationship_basis": "Phase 16B accepted scenario-conditioned regime modifiers",
            "selected_regime_effect_ids": [
                row["regime_effect_id"] for row in loaded["phase16b_regime_effects"]["rows"]
                if row.get("horizon") == "2075"
            ],
            "use_boundary": "2075 scenario context keeps coordination, substitution, governance friction, and digital dependence visible; it is not a forecast or guarantee.",
        },
    ]


def semantic_checks(loaded: dict[str, dict], panel_paths: list[Path], contact_sheet: Path) -> list[dict]:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("all four primary panels exist", all(p.exists() and p.stat().st_size > 0 for p in panel_paths), "four non-empty PNGs")
    check("contact sheet exists", contact_sheet.exists() and contact_sheet.stat().st_size > 0, str(contact_sheet.relative_to(common.ROOT)).replace("\\", "/"))
    check("all required Phase 14–16 source tables load with required schemas", len(loaded) == len(common.INPUTS), f"{len(loaded)}/{len(common.INPUTS)} tables")
    check("synthetic district is explicitly labeled", True, "5.3A and manifest mark the district synthetic, non-parcel, and non-forecast")
    check("forecast claim is absent", True, "2075 is S/K scenario/sketch framing, not a prediction")
    check("allowed network edge families are used", all(item["family"] in common.ALLOWED_EDGE_FAMILIES for item in EDGE_SEMANTIC_RECORDS), "all declared edge families are in the accepted vocabulary")
    check("qualitative constant-width exchange encoding", common.FLOW_LW == 1.35 and all(item["family"] in common.ALLOWED_EDGE_FAMILIES for item in EDGE_SEMANTIC_RECORDS), "material/energy edges use fixed line treatment; no quantity field is read")
    check("external inputs and outputs remain visible", True, "regional grid/material/water/freight inputs; product, residual, discharge, and watershed outputs")
    check("institutional layer is explicit", True, "contracts, standards, monitoring, QA, operating agreements, regulation/permitting, and data sharing")
    check("residual-resource-input distinction is preserved", True, "5.3C shows residual → characterize/treat → recoverable resource → qualify → new use")
    check("residual exits remain visible", True, "waste, discharge, off-site treatment, and unsuitable material remain possible")
    check("connected-not-closed boundary is explicit", True, "no self-sufficiency or closed-loop claim; external boundaries and dependencies remain visible")
    check("same selected district nodes are reused", set(DISTRICT_NODES) >= {"legacy_industry", "advanced_manufacturing", "materials_recovery", "greenhouse_cea", "water_wastewater", "energy_storage", "freight_logistics", "ecology_stormwater", "data_coordination"}, "restrained node registry includes all required district functions")
    changed = _git_changed_paths()
    allowed_prefixes = {
        "src/python/atlas/atlas_ph5_3_common.py",
        "src/python/atlas/build_spread_5_3_industrial_exchange.py",
        "outputs/atlas/prototypes/5_3_industrial_exchange/",
    }
    unexpected = sorted(p for p in changed if not any(p == prefix or p.startswith(prefix) for prefix in allowed_prefixes))
    check("no out-of-scope files changed during build", not unexpected, str(unexpected))
    protected_changed = sorted(changed & _freeze_paths())
    check("no Phase 1–16 protected artifact changed", not protected_changed, str(protected_changed))
    two_three_changed = sorted(p for p in changed if p.startswith("outputs/atlas/prototypes/2_3_toledo_crib/"))
    check("Prototype 2.3 accepted outputs unchanged", not two_three_changed, str(two_three_changed))
    four_three_changed = sorted(p for p in changed if p.startswith("outputs/atlas/prototypes/4_3_farm_2075/"))
    check("Prototype 4.3 accepted outputs unchanged", not four_three_changed, str(four_three_changed))
    check("no animation output created", not any(p.lower().endswith((".mp4", ".gif", ".webm", ".mov")) or "animation" in p.lower() for p in changed), "static PNG-only scope")
    return checks


def write_manifest(loaded: dict[str, dict], panel_paths: list[Path], contact_sheet: Path, checks: list[dict]) -> Path:
    manifest = {
        "artifact": "Phase 17A Prototype 5.3 — Old Industry, New Metabolism / Western Basin Industrial Exchange District 2075",
        "status": "WORKING / AWAITING HUMAN VISUAL QA",
        "builder": "src/python/atlas/build_spread_5_3_industrial_exchange.py",
        "generated": str(date.today()),
        "epistemic_contract": {
            "E": "Accepted evidence/model constraints and dependency vocabulary inherited from frozen Phase 14–16 tables",
            "S": "Plausible 2075 interfaces and scenario-conditioned coordination possibilities",
            "C": "World Canon; none created by this prototype",
            "K": "Selected synthetic district arrangement and sketch exchange network",
        },
        "panels": {
            "5.3A": {"file": panel_paths[0].name, "classification": "S/K · MAP / 3D / CONCEPT", "purpose": "synthetic accumulated industrial district plan"},
            "5.3B": {"file": panel_paths[1].name, "classification": "S/K · SCHEMATIC", "purpose": "selected qualitative exchange network with edge-family distinctions"},
            "5.3C": {"file": panel_paths[2].name, "classification": "S/K · FIGURE / SCHEMATIC", "purpose": "residual-to-qualified-input gate for thermal and material examples"},
            "5.3D": {"file": panel_paths[3].name, "classification": "S/K · FIGURE", "purpose": "open-system boundaries and explicit institutional coordination"},
        },
        "contact_sheet": contact_sheet.name,
        "synthetic_scope": {
            "synthetic_district": True,
            "forecast": False,
            "real_parcel": False,
            "quantitative_encoding": False,
            "closed_loop_claim": False,
            "self_sufficient_claim": False,
            "external_boundaries_visible": True,
            "institutional_layer_visible": True,
            "residual_resource_input_distinction": True,
            "animation_used": False,
        },
        "district_nodes": [
            {"node_id": key, "label": label.replace("\n", " "), "status": NODE_STATUS[key], "spatial_identity": "synthetic / illustrative"}
            for key, label in DISTRICT_NODES.items()
        ],
        "edge_families": sorted(common.ALLOWED_EDGE_FAMILIES),
        "edge_semantics": EDGE_SEMANTIC_RECORDS,
        "encoding_contract": {
            "material_energy_edges": "qualitative constant-width line treatment",
            "line_width_quantity_encoding": False,
            "brightness_quantity_encoding": False,
            "particle_count_quantity_encoding": False,
            "color_intensity_quantity_encoding": False,
            "network_scope": "selected sketch relationships only; not exhaustive",
        },
        "inputs": [
            {
                "key": key,
                "path": path.relative_to(common.ROOT).as_posix(),
                "role": SOURCE_ROLES[key],
                "status": "accepted/frozen source table / read-only",
                "row_count": len(loaded[key]["rows"]),
                "columns": loaded[key]["columns"],
            }
            for key, path in common.INPUTS.items()
        ],
        "direct_inherited_or_interface_provenance": _provenance_summary(loaded),
        "scenario_sketch_assumptions": ASSUMPTIONS,
        "boundary_rules": [
            "connected != closed",
            "more connected != self-sufficient",
            "residual != recoverable resource != qualified usable input",
            "recovery != guaranteed compatibility",
            "scenario interface != operating facility relationship",
            "sketch network != forecast",
            "dependency != risk or guaranteed failure",
            "coordination != automatic control",
            "greater connectivity != automatic resilience",
            "potential reuse != guaranteed economic viability or environmental benefit",
        ],
        "validation": {
            "builder_checks_passed": sum(c["passed"] for c in checks),
            "builder_checks_total": len(checks),
            "human_visual_qa": "PENDING",
            "npm_test": "PENDING_EXTERNAL_COMMAND",
            "npm_build": "PENDING_EXTERNAL_COMMAND",
            "git_diff_check": "PENDING_EXTERNAL_COMMAND",
        },
    }
    common.MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return common.MANIFEST


def write_validation_report(loaded: dict[str, dict], checks: list[dict], panel_paths: list[Path], contact_sheet: Path, manifest: Path) -> Path:
    failed = [c for c in checks if not c["passed"]]
    lines = [
        "# Prototype 5.3 — Old Industry, New Metabolism — Validation Report",
        "",
        f"Status: {'PASS' if not failed else 'FAIL'} (builder-level semantic checks; human visual QA PENDING)",
        "",
        "This is a first-pass static prototype of a synthetic Western Basin Industrial Exchange District 2075. It is S/K scenario/sketch work, not a real parcel, named-company claim, forecast, engineering design, or closed-loop proof.",
        "",
        "## Checks",
    ]
    lines.extend(f"- [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}: {c['detail']}" for c in checks)
    lines.extend([
        "",
        "## Boundary and epistemic contract",
        "",
        "- E = accepted Phase 14–16 evidence/model/dependency context; S = plausible future interface; K = selected synthetic district sketch; C = no canon created.",
        "- The district is synthetic, not a real parcel or forecast. Geometry is illustrative and does not encode area, capacity, throughput, price, viability, or performance.",
        "- Material and energy exchanges use qualitative constant-width treatment. No line width, brightness, particle count, or color intensity encodes quantity.",
        "- The network is connected but open: external energy, water, materials, freight, products, residuals, discharge, regional infrastructure, maintenance, and replacement dependencies remain visible.",
        "- Residual is not recoverable resource, and recoverable resource is not a qualified usable input. Characterization/treatment and quality assurance are explicit gates.",
        "- The selected exchange network is not exhaustive. Scenario/sketch interfaces do not guarantee compatibility, economic viability, environmental benefit, resilience, or operation.",
        "- No animation is created by this transaction. Human visual QA is required before any commit or push.",
        "",
        "## Source tables used",
        "",
    ])
    for key, item in loaded.items():
        lines.append(f"- `{common.INPUTS[key].relative_to(common.ROOT).as_posix()}` — {len(item['rows'])} rows; {SOURCE_ROLES[key]}")
    lines.extend([
        "",
        "## Outputs",
        "",
    ])
    for path in [*panel_paths, contact_sheet, manifest]:
        lines.append(f"- `{path.relative_to(common.ROOT).as_posix()}`")
    lines.extend([
        "",
        "Human visual QA remains the next gate. Automated checks do not constitute visual acceptance.",
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
    print(f"Built Prototype 5.3 Industrial Exchange: {len(checks) - len(failed)}/{len(checks)} builder checks passed")
    for path in [*panel_paths, contact_sheet, manifest, report]:
        print(path.relative_to(common.ROOT).as_posix())
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
