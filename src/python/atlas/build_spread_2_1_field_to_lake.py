"""Build Phase 17A Prototype 2.1 'From Field to Lake' static figures.

Additive Phase-17 Atlas builder. Reads accepted/frozen Phase 1-16 inputs only
and never writes to them. Produces four qualitative static figures (2.1A-D), a
source/provenance manifest, a constituent-process matrix, an R-export, and
grayscale / 50%-size proofs.

Epistemic status: all figures are E (Evidence / Model) with representation
descriptors MAP, SCHEMATIC, or FIGURE. No animation is produced.

Scientific contract: water connects the agricultural landscape of the Maumee
watershed to western Lake Erie, but water, sediment, phosphorus, nitrogen, and
carbon may be mobilized, transported, retained, transformed, or diverted
differently before reaching receiving waters. Delivery to western Lake Erie is
not equivalent to bloom formation.

Qualitative-only: biogeochemical_flux_edges.csv records quantity_status =
"unknown quantity" for all edges; no figure encodes magnitude via line width,
particle count, intensity, brightness, or speed.
"""

from __future__ import annotations

import json
from datetime import date, timezone
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
import pandas as pd

from atlas_ph2_1_common import (  # script runs from src/python/atlas
    ANALYSIS,
    APPROVED_PROCESSES,
    CONSTITUENT_TRACKS,
    CONSTITUENT_MATRIX,
    DATA,
    FOCUS_WINDOW,
    GPKG,
    LAYER_HUC12,
    LAYER_HUC8,
    LAYER_HYDRO_CONNECTORS,
    LAYER_HYDRO_PHYSICAL,
    LAYER_LAKE,
    LAYER_ROUTING_UNRESOLVED,
    MANIFEST,
    MAP_CRS,
    NETWORKS,
    OPTIONAL_INPUTS,
    OUT_DIR,
    RELATIONSHIP_TO_PROCESS,
    RENDER_MIN_STREAMORDER,
    RENDER_SIMPLIFY_TOL,
    REPORTS,
    REQUIRED_INPUTS,
    ROOT,
    WATER_CRS,
)

RETRIEVED = date.today().isoformat()

# Qualitative visual grammar (Phase 17A v0.3; not a frozen final style).
INK = "#1F2428"
WATER = "#3C6E8F"
WATER_LIGHT = "#B9DDEB"
LAND = "#EFEAE0"
AG = "#CBD1A8"
CONNECTOR = "#8A8A86"  # analytical connector (non-physical), dashed
CONTEXT = "#667078"
HAB = "#9E7BB5"  # receiving-water response/context (distinct from transport)
HUC12_LINE = "#C6C6BB"  # faint HUC-12 subwatershed boundary (background context)
ANNOT_LEADER = "#A3A7A9"  # thin neutral annotation pointer (distinct from system lines)


# ---------------------------------------------------------------------------
# Input / source helpers
# ---------------------------------------------------------------------------
def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def check_inputs() -> dict[str, str]:
    missing = [str(p) for p in REQUIRED_INPUTS if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required inputs: {missing}")
    manifest = {"required": [str(p) for p in REQUIRED_INPUTS]}
    manifest["optional"] = {
        str(p): {"exists": bool(p.exists()), "present_in_repo": bool(p.exists())}
        for p in OPTIONAL_INPUTS
    }
    return manifest


def read_flux() -> pd.DataFrame:
    return pd.read_csv(NETWORKS / "biogeochemical_flux_edges.csv")


def load_layers() -> dict[str, gpd.GeoDataFrame]:
    layers = {
        "hydro_physical": gpd.read_file(GPKG, layer=LAYER_HYDRO_PHYSICAL),
        "hydro_connectors": gpd.read_file(GPKG, layer=LAYER_HYDRO_CONNECTORS),
        "routing_unresolved": gpd.read_file(GPKG, layer=LAYER_ROUTING_UNRESOLVED),
        "huc8": gpd.read_file(GPKG, layer=LAYER_HUC8),
        "huc12": gpd.read_file(GPKG, layer=LAYER_HUC12),
        "lake": gpd.read_file(GPKG, layer=LAYER_LAKE),
    }
    return layers


def render_copy(frame: gpd.GeoDataFrame, tolerance: float = RENDER_SIMPLIFY_TOL) -> gpd.GeoDataFrame:
    """Return a generalized render copy projected to MAP_CRS; source is untouched."""
    f = frame.to_crs(MAP_CRS).copy()
    if tolerance and not f.empty:
        f.geometry = f.geometry.simplify(tolerance * 111_000, preserve_topology=True)
    return f


def _focus_limits(frames: list[gpd.GeoDataFrame], window_bounds, pad_frac: float = 0.04):
    """Focal map limits: union of rendered data clipped to the focus window, with
    a small outward pad. Use this (not the raw window) so the geography fills the
    canvas. Data and selection logic are unchanged."""
    x0, y0, x1, y1 = window_bounds
    xs, ys = [], []
    for g in frames:
        if g is None or g.empty:
            continue
        b = g.total_bounds
        ix0, ix1 = max(b[0], x0), min(b[2], x1)
        iy0, iy1 = max(b[1], y0), min(b[3], y1)
        if ix1 > ix0 and iy1 > iy0:
            xs += [ix0, ix1]
            ys += [iy0, iy1]
    cx0, cx1 = min(xs), max(xs)
    cy0, cy1 = min(ys), max(ys)
    w, h = (cx1 - cx0), (cy1 - cy0)
    return (cx0 - pad_frac * w, cx1 + pad_frac * w,
            cy0 - pad_frac * h, cy1 + pad_frac * h)


# ---------------------------------------------------------------------------
# 2.1A Geographic Pathway Map  E . MAP
# ---------------------------------------------------------------------------
def build_2_1a(layers: dict[str, gpd.GeoDataFrame]) -> None:
    huc8 = render_copy(layers["huc8"])
    huc12 = render_copy(layers["huc12"], tolerance=0.001)
    lake = render_copy(layers["lake"], tolerance=0.003)

    # Physical waterways: only streamorder >= threshold from hydrography_physical.
    hydro = layers["hydro_physical"]
    hydro = hydro[hydro["streamorder"].astype(float) >= RENDER_MIN_STREAMORDER].copy()
    hydro = hydro.to_crs(MAP_CRS)
    hydro.geometry = hydro.geometry.simplify(RENDER_SIMPLIFY_TOL * 111_000, preserve_topology=True)

    # Maumee main stem = lower-Maumee HUC-8 (04100009) high-order physical channel.
    maumee_main = hydro[hydro["huc12"].astype(str).str.startswith("04100009")]

    # Analytical connectors: represented distinctly (dashed, gray), never as a
    # physical stream. Display subset matches the physical display threshold.
    conn_full = layers["hydro_connectors"].copy()
    if "streamorder" in conn_full.columns:
        conn_full = conn_full[conn_full["streamorder"].astype(float) >= RENDER_MIN_STREAMORDER]
    conn = render_copy(conn_full, tolerance=0.0006)

    fig, ax = plt.subplots(figsize=(13.5, 9.5), dpi=120, facecolor="#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Western Lake Erie / receiving water (filled from accepted lake geometry).
    lake.plot(ax=ax, color=WATER_LIGHT, edgecolor=WATER, linewidth=0.8, zorder=1)

    # HUC-8 watershed context.
    huc8.plot(ax=ax, color=LAND, edgecolor=INK, linewidth=1.1, zorder=2, alpha=0.75)
    huc12.boundary.plot(ax=ax, color=HUC12_LINE, linewidth=0.16, alpha=0.6, zorder=3)

    # Physical waterways: uniform qualitative width (no magnitude encoding).
    hydro.plot(ax=ax, color=WATER, linewidth=0.65, alpha=0.75, zorder=4)
    # Maumee main stem emphasized as *category*, not magnitude.
    maumee_main.plot(ax=ax, color=INK, linewidth=1.15, alpha=0.95, zorder=5)
    # Analytical connectors remain visibly non-physical (dashed).
    conn.plot(ax=ax, color=CONNECTOR, linewidth=0.55, linestyle=(0, (4, 3)), alpha=0.55, zorder=3.5)

    # Map extent: zoom to the rendered focal content (clipped to the focus
    # window) so the geography fills the canvas more effectively. Geographic
    # data and selection logic are unchanged.
    from shapely.geometry import box as _box
    fwin = gpd.GeoSeries([_box(*tuple(FOCUS_WINDOW))], crs=WATER_CRS).to_crs(MAP_CRS).total_bounds
    fx0, fx1, fy0, fy1 = _focus_limits([lake, huc8, hydro, conn], fwin, pad_frac=0.04)
    ax.set_xlim(fx0, fx1)
    ax.set_ylim(fy0, fy1)
    ax.set_aspect("equal")

    # Labels (Maumee Bay = labeled nearshore interface within lake geometry).
    # Anchor points converted from degrees to projected coordinates.
    pts = gpd.GeoSeries([_box(bay_pt[0], bay_pt[1], bay_pt[0], bay_pt[1]) for bay_pt in [
        (-83.30, 41.80), (-82.95, 42.02), (-83.42, 41.95),
    ]], crs=WATER_CRS).to_crs(MAP_CRS)
    pt_bay, pt_wle, pt_bay2 = [g.centroid for g in pts.geometry]
    ax.annotate(
        "MAUMEE BAY / NEARSHORE\n(RECEIVING-WATER INTERFACE)",
        xy=(pt_bay.x, pt_bay.y), xycoords="data", ha="center", fontsize=9.5,
        fontweight="bold", color=INK, linespacing=1.15,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor=WATER, alpha=0.85),
    )
    ax.text(pt_wle.x, pt_wle.y, "WESTERN LAKE ERIE\n(receiving water)", fontsize=9.5, fontweight="bold",
            color=INK, ha="center", va="top", bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF",
             edgecolor=WATER, alpha=0.85))
    along = maumee_main.total_bounds
    mid_x, mid_y = (along[0] + along[2]) / 2, (along[1] + along[3]) / 2
    ax.annotate("MAUMEE RIVER", xy=(mid_x, mid_y), xytext=(mid_x + 14_000, mid_y + 9_000),
                fontsize=10, fontweight="bold", color=INK,
                arrowprops=dict(arrowstyle="->", color=ANNOT_LEADER, lw=0.8,
                                shrinkA=2, shrinkB=3))

    # Toledo civic / geographic anchor (label only; not physical intake geometry).
    tol = gpd.GeoSeries([_box(-83.47596, 41.663405, -83.47596, 41.663405)], crs=WATER_CRS).to_crs(MAP_CRS).iloc[0].centroid
    ax.plot(tol.x, tol.y, marker="o", markersize=6, color=INK, zorder=6,
            markeredgecolor="#FFFFFF", markeredgewidth=1.0)
    ax.text(tol.x + 8_000, tol.y + 8_000, "Toledo\n(civic anchor)", fontsize=8,
            color=INK, ha="left", va="bottom")

    ax.set_axis_off()
    ax.set_title("2.1A  FROM FIELD TO LAKE — GEOGRAPHIC PATHWAY MAP", loc="left",
                 fontsize=15, fontweight="bold", color=INK, pad=14)
    ax.text(0, 1.012, "E · MAP  —  Where does the connected watershed-to-lake pathway occur?",
            transform=ax.transAxes, fontsize=9.5, color=CONTEXT, va="bottom")

    legend = [
        Patch(facecolor=LAND, edgecolor=INK, label="Maumee HUC-8 watersheds (accepted)"),
        Line2D([0], [0], color=WATER, lw=2.4, label="Physical waterways (accepted geometry)"),
        Line2D([0], [0], color=INK, lw=2.4, label="Maumee River main stem (physical)"),
        Line2D([0], [0], color=CONNECTOR, lw=1.6, ls=(0, (4, 3)), label="Analytical connector (not a physical stream)"),
        Patch(facecolor=WATER_LIGHT, edgecolor=WATER, label="Accepted Lake Erie / receiving water"),
    ]
    ax.legend(handles=legend, loc="lower left", fontsize=7.6, frameon=True, title="E · MAP")
    fig.text(0.008, 0.012,
             "Sources: data/processed/glasspunk_base.gpkg — hydrography_physical, water_watersheds_huc8, "
             "water_subwatersheds_huc12, water_lake_erie. Physical waterways only; network connectors are shown "
             "as dashed analytical context and are never rendered as physical streams. Qualitative-only: no "
             "nutrient magnitude is encoded by width, intensity, or density.",
             fontsize=6.8, color=CONTEXT)
    save_figure(fig, "2_1a_geographic_flow_map")
    plt.close(fig)


def build_2_1b() -> None:
    stages = [
        "LANDSCAPE / FIELD",
        "DRAINAGE / SMALL CHANNEL",
        "TRIBUTARY",
        "MAUMEE RIVER",
        "MAUMEE BAY / NEARSHORE INTERFACE",
        "WESTERN LAKE ERIE",
    ]
    # Approved normalized process categories (qualitative). Chain arrows are
    # unlabeled conveyance; the positioned annotations below communicate WHERE
    # along the chain each generic process can be expected to act. Discharge is
    # a separate regulated point-source pathway and is shown as a note, not as
    # a physical discharge arrow on this chain (no discharge pipe is invented).

    n = len(stages)
    xs = 2.6  # chain x-center
    y0, y1, gap = 1.2, 8.8, (8.8 - 1.2) / (n - 1)
    centers = [y0 + i * gap for i in range(n)]

    fig, ax = plt.subplots(figsize=(12, 10), dpi=120, facecolor="#FFFFFF")
    ax.set_xlim(-1.4, 12.0)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    # -- Draw the vertical process chain (left column) --
    for label, y in zip(stages, centers):
        box = FancyBboxPatch((xs - 1.6, y - 0.42), 3.2, 0.84,
                             boxstyle="round,pad=0.04", linewidth=1.4,
                             edgecolor=INK, facecolor="#F4F4F4")
        ax.add_patch(box)
        ax.text(xs, y, label, ha="center", va="center", fontsize=8.6,
                fontweight="bold", color=INK, linespacing=1.1)

    # -- Unlabeled conveyance arrows between consecutive stages --
    for i in range(n - 1):
        ax.add_patch(FancyArrowPatch((xs, centers[i] + 0.42), (xs, centers[i + 1] - 0.42),
                                     arrowstyle="-|>", mutation_scale=14,
                                     linewidth=1.1, color=WATER, zorder=3))

    # -- Positioned process annotations (single transition; thin neutral leader) --
    def plabel(text, i, j):
        ym = (centers[i] + centers[j]) / 2
        ax.text(0.9, ym, text, ha="right", va="center", fontsize=7.3, color=INK, style="italic")
        ax.plot([1.2, xs - 0.02], [ym, ym], color=ANNOT_LEADER, lw=0.8, zorder=1)

    # mobilization near the source transition (LANDSCAPE/FIELD -> DRAINAGE)
    plabel("mobilization", 0, 1)
    # delivery entering the receiving-water interface (MAUMEE RIVER -> BAY)
    plabel("delivery", 3, 4)
    # receiving-water response/context at the lake side (BAY -> ERIE)
    plabel("receiving-water\nresponse/context", 4, 5)

    # transport spans the conveyance stages (DRAINAGE .. MAUMEE RIVER): a side
    # bracket rather than a single arrow, so it reads as a conveyance property.
    t_x = 0.55
    t_yA, t_yB = centers[1] + 0.42, centers[3] - 0.42
    t_mid = (t_yA + t_yB) / 2
    ax.plot([t_x, t_x], [t_yA, t_yB], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.plot([t_x, t_x + 0.18], [t_yA, t_yA], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.plot([t_x, t_x + 0.18], [t_yB, t_yB], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.text(t_x - 0.2, t_mid, "transport\n(conveyance)", ha="right", va="center",
            fontsize=7.3, color=INK, style="italic")

    # -- Retention / transformation: spanning side annotation (multiple stages) --
    r_x = 4.95
    r_yA, r_yB = centers[1] + 0.42, centers[4] - 0.42  # DRAINAGE .. MAUMEE BAY
    rm = (r_yA + r_yB) / 2
    ax.plot([r_x, r_x], [r_yA, r_yB], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.plot([r_x, r_x + 0.6], [r_yA, r_yA], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.plot([r_x, r_x + 0.6], [r_yB, r_yB], color=ANNOT_LEADER, lw=0.8, zorder=1)
    ax.text(r_x + 0.72, rm, "retention /\ntransformation\nmay occur at\nmultiple stages",
            ha="left", va="center", fontsize=7.0, color=CONTEXT, style="italic", linespacing=1.05)

    # -- Right column: relationship legend (approved process vocabulary) --
    lx = 7.6
    ax.text(lx, 8.9, "APPROVED PROCESS VOCABULARY", fontsize=9.2, fontweight="bold", color=INK)
    proc_defs = {
        "mobilization": "landscape/field source enters connected pathway",
        "transport": "conveyance through drainage, tributary, or river",
        "retention / transformation": "may be stopped, stored, or changed along the way",
        "delivery": "reaches Maumee Bay / nearshore receiving-water interface",
        "discharge": "regulated or documented release to a receiving water",
        "receiving-water response/context": "lake conditions interact with local delivery",
    }
    y = 8.15
    for proc in APPROVED_PROCESSES:
        ax.text(lx, y, f"• {proc}", fontsize=7.8, fontweight="bold", color=INK)
        ax.text(lx + 0.35, y - 0.20, proc_defs[proc], fontsize=6.6, color=CONTEXT)
        y -= 0.72

    # -- Discharge: explicit non-chain point-source note --
    d = FancyBboxPatch((6.0, 0.9), 5.3, 1.15, boxstyle="round,pad=0.12",
                       linewidth=1.0, edgecolor=CONTEXT, facecolor="#F6F6F2")
    ax.add_patch(d)
    ax.text(6.25, 1.78, "DISCHARGE", fontsize=7.4, fontweight="bold", color=INK)
    ax.text(6.25, 1.30,
            "separate regulated point-source pathway;\nnot shown in this generalized chain (no "
            "physical discharge pipe drawn)",
            fontsize=6.7, color=CONTEXT, va="top", linespacing=1.15)

    ax.text(6.0, 0.35,
            "Generalized explanatory abstraction — not one mapped farm or one measured event.",
            fontsize=6.6, color=CONTEXT, style="italic")

    ax.set_title("2.1B  FROM FIELD TO LAKE — PROCESS SCHEMATIC", loc="left",
                 fontsize=15, fontweight="bold", color=INK, pad=14)
    fig.text(0.012, 0.012,
             "E · SCHEMATIC — What kinds of processes occur between field and receiving water?\n"
             "Qualitative sequence normalized from accepted relationship vocabulary; arrow styles denote "
             "process semantics, not quantity. No nutrient magnitude implied; retention is not stage-specific.",
             fontsize=6.8, color=CONTEXT, va="bottom", linespacing=1.4)
    save_figure(fig, "2_1b_process_schematic")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2.1C Constituent Pathway Comparison  E . FIGURE
# ---------------------------------------------------------------------------
def build_2_1c(flux: pd.DataFrame) -> pd.DataFrame:
    # For each constituent track, which approved process categories occur in the
    # accepted flux edges. This is data-driven: tracks differ when their
    # relationship types differ.
    rows = []
    for track_name, tokens in CONSTITUENT_TRACKS:
        token_set = set(tokens)
        involved = flux[flux["material"].apply(lambda m: bool(token_set & set(str(m).split(";"))))]
        procs = sorted({
            p for p in involved["relationship_type"].map(RELATIONSHIP_TO_PROCESS).dropna().unique()
        }, key=APPROVED_PROCESSES.index)
        rows.append({"constituent_track": track_name, "supported_processes": ";".join(procs)})
    mtx = pd.DataFrame(rows)
    mtx.to_csv(CONSTITUENT_MATRIX, index=False)

    fig, ax = plt.subplots(figsize=(14.5, 8), dpi=120, facecolor="#FFFFFF")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ncells = len(APPROVED_PROCESSES)
    # Water is carrier/context and is kept OUT of the constituent matrix.
    present = [t for t in mtx["constituent_track"].tolist() if not t.startswith("water")]
    nrows = len(present)
    # layout in axes-fraction space (matrix enlarged toward the canvas)
    left, right = 0.32, 0.99
    top, bottom = 0.74, 0.40
    col_x = {p: left + (right - left) * i / max(ncells - 1, 1) for i, p in enumerate(APPROVED_PROCESSES)}
    row_y = {name: bottom + (top - bottom) * (nrows - 1 - k) / max(nrows - 1, 1)
             for k, name in enumerate(present)}
    header_y = 0.84

    # Water as carrier/context (outside the matrix).
    ax.text(left, 0.96,
            "Water provides the transport context; the rows below show constituent-specific\nsupported relationships.",
            ha="left", va="center", fontsize=8.0, color=CONTEXT, style="italic", linespacing=1.2)

    # Column headers (rotated so long process names do not collide).
    headers = {
        "mobilization": "mobilization",
        "transport": "transport",
        "retention / transformation": "retention /\ntransformation",
        "delivery": "delivery",
        "discharge": "discharge",
        "receiving-water response/context": "receiving-water\nresponse/context",
    }
    for p in APPROVED_PROCESSES:
        ax.text(col_x[p], header_y, headers[p], fontsize=7.2, fontweight="bold", color=INK,
                va="bottom", ha="right", rotation=22, linespacing=1.05)
    for p in APPROVED_PROCESSES:
        ax.plot([col_x[p], col_x[p]], [bottom, header_y - 0.02], color="#D8D8D2", lw=0.6, zorder=1)

    # Data rows (constituent tracks only). A single fixed-size presence square for
    # every supported relationship; glyph size, darkness, and intensity are never
    # used to encode strength, magnitude, frequency, or confidence.
    for name in present:
        row = mtx[mtx["constituent_track"] == name].iloc[0]
        supported = set(row["supported_processes"].split(";")) if row["supported_processes"] else set()
        ax.text(left - 0.02, row_y[name], name, fontsize=7.4, fontweight="bold", color=INK,
                va="center", ha="right")
        for p in APPROVED_PROCESSES:
            xc = col_x[p]
            if p in supported:
                ax.plot(xc, row_y[name], marker="s", markersize=8, color=INK,
                        markeredgecolor=INK, zorder=3)
            else:
                # clearly non-quantitative absent-state convention
                ax.text(xc, row_y[name], "·", fontsize=11, color="#B9B9B0",
                        va="center", ha="center", zorder=3)

    ax.set_title("2.1C  CONSTITUENT PATHWAY COMPARISON", loc="left",
                 fontsize=15, fontweight="bold", color=INK, pad=10)

    ax.text(left, bottom - 0.05,
            "Rows: constituent tracks (phosphorus, nitrogen, carbon/organic matter, sediment). "
            "Columns: approved process categories.\n"
            "Shared process categories do not imply identical form, rate, transport, or fate.\n"
            "Each square marks that the accepted source supports that process for that constituent\n"
            "(presence only). No cell encodes quantity, load, ranking, or confidence. Tracks are not\n"
            "interchangeable. HAB_context is a context/modifier token, never a constituent track;\n"
            "carbon tracks are organic-matter context, not a greenhouse-gas inventory.",
            fontsize=6.8, color=CONTEXT, va="top", linespacing=1.35)
    ax.text(right, 0.96, "E · FIGURE", ha="right", va="center", fontsize=9.5,
            color=CONTEXT, fontweight="bold")
    fig.text(0.012, 0.012,
             "Source: data/processed/networks/biogeochemical_flux_edges.csv (qualitative; quantity_status = "
             "'unknown quantity' for all edges).\n"
             "Cell presence = the accepted relationship type supports that process for that constituent "
             "— presence, never magnitude or ranking.",
             fontsize=6.6, color=CONTEXT, va="bottom", linespacing=1.4)
    save_figure(fig, "2_1c_constituent_pathways")
    plt.close(fig)
    return mtx


def wrap(s: str, n: int = 9) -> str:
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) <= n:
            cur += " " + w
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2.1D Receiving-Water Boundary Inset  E . SCHEMATIC
# ---------------------------------------------------------------------------
def build_2_1d() -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.8), dpi=120, facecolor="#FFFFFF")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    def box(x, y, w, h, label, face, edge):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                     linewidth=1.5, edgecolor=edge, facecolor=face))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=8, fontweight="bold", color=INK, linespacing=1.15)

    box(0.8, 4.6, 3.2, 1.5, "WATERSHED\nDELIVERY", "#EFF3F5", WATER)
    box(6.0, 4.6, 3.2, 1.5, "RECEIVING-WATER\nCONDITIONS", "#F1EFF4", HAB)
    box(3.3, 0.7, 3.4, 1.3, "POSSIBLE BLOOM-\nFAVORABLE CONDITIONS", "#FBF7EA", "#C98F2E")

    # Shared interaction/junction: the two inputs converge here, then a single
    # outgoing arrow leads to possible bloom-favorable conditions. No direct
    # nutrient -> HAB edge is drawn, and no additive "+" symbol is implied.
    jx, jy = 5.0, 3.2
    ax.add_patch(plt.Circle((jx, jy), 0.24, facecolor="#F6F6F2",
                             edgecolor=CONTEXT, linewidth=1.4, zorder=4))
    ax.add_patch(FancyArrowPatch((2.4, 4.6), (jx - 0.30, jy + 0.18), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.2, color=WATER, zorder=3))
    ax.add_patch(FancyArrowPatch((7.6, 4.6), (jx + 0.30, jy + 0.18), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.2, color=HAB, zorder=3))
    ax.add_patch(FancyArrowPatch((jx, jy - 0.26), (5.0, 2.0), arrowstyle="-|>",
                                 mutation_scale=15, linewidth=1.3, color=CONTEXT, zorder=3))

    ax.text(5.12, 2.35, "can contribute to\nbloom-favorable conditions\n(not inevitable bloom formation)",
            ha="left", va="center", fontsize=7.0, color=CONTEXT, style="italic", linespacing=1.2)

    ax.text(5.0, 0.38,
            "Receiving-water physical / chemical / biological conditions are a distinct process domain.\n"
            "This inset deliberately does NOT draw a direct nutrient → HAB causal edge.",
            fontsize=6.8, color=CONTEXT, ha="center", va="center", style="italic")

    ax.set_title("2.1D  RECEIVING-WATER BOUNDARY", loc="left",
                 fontsize=15, fontweight="bold", color=INK, pad=12)
    ax.text(0.01, 1.18, "E · SCHEMATIC  —  delivery and lake conditions converge; "
                        "no nutrient → HAB causal edge", transform=ax.transAxes,
            fontsize=8.0, color=CONTEXT, va="bottom")
    save_figure(fig, "2_1d_receiving_water_boundary")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save SVG + PNG, then grayscale-proof and 50%-size-proof PNG copies.

    Matplotlib SVG output places a trailing space before each newline inside
    long path attributes; strip trailing whitespace so the committed SVG is
    clean under `git diff --check` while remaining a well-formed SVG.
    """
    fig.savefig(OUT_DIR / f"{stem}.png", bbox_inches="tight", facecolor="#FFFFFF")
    svg = OUT_DIR / f"{stem}.svg"
    fig.savefig(svg, bbox_inches="tight", facecolor="#FFFFFF")
    svg.write_text("\n".join(ln.rstrip() for ln in svg.read_text(encoding="utf-8").split("\n")),
                   encoding="utf-8")
    _proof_from_png(OUT_DIR / f"{stem}.png", OUT_DIR / f"{stem}_grayscale.png", grayscale=True, scale=1.0)
    _proof_from_png(OUT_DIR / f"{stem}.png", OUT_DIR / f"{stem}_50pct.png", grayscale=False, scale=0.5)
    _proof_from_png(OUT_DIR / f"{stem}.png", OUT_DIR / f"{stem}_grayscale_50pct.png", grayscale=True, scale=0.5)


def _proof_from_png(src: Path, dst: Path, *, grayscale: bool, scale: float) -> None:
    from PIL import Image
    img = Image.open(src).convert("RGB")
    if grayscale:
        img = img.convert("L")
    if scale != 1.0:
        w, h = img.size
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(dst)


# ---------------------------------------------------------------------------
# Source / provenance manifest
# ---------------------------------------------------------------------------
def write_manifest(input_chk: dict[str, str], flux: pd.DataFrame,
                   layers: dict[str, gpd.GeoDataFrame]) -> None:
    hyd_phys = layers["hydro_physical"]
    hyd_phys_render = hyd_phys[hyd_phys["streamorder"].astype(float) >= RENDER_MIN_STREAMORDER]
    manifest = {
        "prototype": "2.1",
        "title": "From Field to Lake",
        "phase": "17A",
        "status": "static analytical prototype (qualitative)",
        "epistemic_status": "E",
        "representation_designators": {"2.1A": "MAP", "2.1B": "SCHEMATIC", "2.1C": "FIGURE", "2.1D": "SCHEMATIC"},
        "built": RETRIEVED,
        "quantitative": False,
        "quantity_status_source": "biogeochemical_flux_edges.csv quantity_status = unknown quantity (all edges)",
        "inputs": {
            "required": input_chk["required"],
            "optional": {k: v["exists"] for k, v in input_chk["optional"].items()},
        },
        "geography": {
            "gpkg": str(GPKG.relative_to(ROOT)),
            "physical_waterways_layer": LAYER_HYDRO_PHYSICAL,
            "physical_waterway_count": int(len(hyd_phys)),
            "physical_waterway_render_count": int(len(hyd_phys_render)),
            "render_min_streamorder": RENDER_MIN_STREAMORDER,
            "network_connectors_layer": LAYER_HYDRO_CONNECTORS,
            "routing_unresolved_layer": LAYER_ROUTING_UNRESOLVED,
            "watershed_huc8_layer": LAYER_HUC8,
            "watershed_huc12_layer": LAYER_HUC12,
            "lake_layer": LAYER_LAKE,
            "maumee_bay_representation": "labeled nearshore / receiving-water interface within accepted Lake Erie geometry; no standalone polygon",
            "toledo_intake_geometry_used": False,
            "toledo_role": "civic / geographic anchor only",
            "glos_crib_used_as_geometry": False,
            "great_black_swamp_geometry_used": False,
        },
        "constituent_tracks": [t[0] for t in CONSTITUENT_TRACKS],
        "hab_context_constituent": False,
        "approved_processes": APPROVED_PROCESSES,
        "release_process_introduced": False,
        "deterministic_nutrient_to_hab_edge": False,
        "flow_styling": "uniform qualitative widths; no magnitude encoding",
        "outputs": sorted(str(p.relative_to(ROOT)) for p in OUT_DIR.iterdir() if p.is_file()),
    }
    (OUT_DIR / "2_1_source_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    pd.DataFrame([{"field": k, "value": v if not isinstance(v, (list, dict)) else json.dumps(v, default=str)}
                  for k, v in manifest.items()]).to_csv(
        OUT_DIR / "2_1_source_manifest.csv", index=False)


# ---------------------------------------------------------------------------
# R-export: independent validation consumption
# ---------------------------------------------------------------------------
def export_r() -> None:
    flux = read_flux()
    flux.drop(columns=[c for c in ["notes", "relationship_basis", "scale"] if c in flux.columns])\
        .assign(material=str)  # placeholder to keep schema stable
    # write a compact, R-friendly classification of every rendered relationship
    rows = []
    for _, r in flux.iterrows():
        proc = RELATIONSHIP_TO_PROCESS.get(r["relationship_type"]) or ""
        rows.append({
            "edge_id": r["edge_id"],
            "material": r["material"],
            "relationship_type": r["relationship_type"],
            "atlas_process": proc,
            "quantity_status": r["quantity_status"],
        })
    pd.DataFrame(rows).to_csv(OUT_DIR / "2_1_r_edge_classification.csv", index=False)


# ---------------------------------------------------------------------------
def main() -> None:
    ensure_dirs()
    input_chk = check_inputs()
    flux = read_flux()
    layers = load_layers()
    build_2_1a(layers)
    build_2_1b()
    build_2_1c(flux)
    build_2_1d()
    export_r()
    write_manifest(input_chk, flux, layers)
    print("Built Phase 17A Prototype 2.1 static figures ->", OUT_DIR)


if __name__ == "__main__":
    main()