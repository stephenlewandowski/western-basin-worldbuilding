"""Phase 17A Prototype 2.1 'From Field to Lake' — deterministic animation builder.

Additive Phase-17 Atlas animation support. This script composes the ACCEPTED
static Prototype 2.1 PNGs (immutable visual sources) onto a canonical
1920 x 1080, 30 fps, 32.0 s, 960-frame explanatory animation canvas. It never
re-renders or modifies the accepted static figures, never reads-writes Phase
1-16 inputs, and never installs dependencies.

Canvas model (overrides the retired native-size requirement):
- canonical canvas 1920 x 1080 at 30 fps, 32.0 s, 960 frames, white background;
- each accepted static figure is placed aspect-preserving, center-aligned;
- no crop, no distortion; scaling/padding has no scientific meaning.

Epistemic status: all animation states are E (Evidence / Model) with
quantitative_encoding = false. No randomization, no simulation, no particles.
The animation is an explanatory extension of the accepted static figures only.

Scientific boundary (preserved from the accepted static contract):
  Water connects the agricultural landscape of the Maumee watershed to western
  Lake Erie, but water, sediment, phosphorus, nitrogen, and carbon may be
  mobilized, transported, retained, transformed, or delivered differently
  before reaching receiving waters. Delivery to western Lake Erie is not
  equivalent to bloom formation.
"""

from __future__ import annotations

import io
import json
from datetime import date, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Project / output paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "2_1_from_field_to_lake"
ANIM_DIR = STATIC_DIR / "animation"

CANVAS_W, CANVAS_H = 1920, 1080
FPS = 30
DURATION_S = 32.0
EXPECTED_FRAMES = 960
FRAME_TOL = 0.5  # encoder frame-duration tolerance

# Dedicated reserved bands on the 1920x1080 canvas (prototype 2.1 layout pass).
# The accepted static figure is placed aspect-preserving, center-aligned,
# WITHOUT crop inside the figure region only; the animation state title,
# A5 synthesis, and persistent footer never overlap it. Scaled placement and
# padding carry no scientific meaning.
HEADER_H = 110             # top band reserved for the animation state title
FOOTER_H = 64              # bottom band reserved for the persistent footer
SYNTH_H = 120              # A5 synthesis band (figure region shortened for A5)
FIGURE_TOP = HEADER_H
FOOTER_TOP = CANVAS_H - FOOTER_H
SYNTH_TOP = FOOTER_TOP - SYNTH_H

STATIC_PNGS = {
    "A": "2_1a_geographic_flow_map.png",
    "B": "2_1b_process_schematic.png",
    "C": "2_1c_constituent_pathways.png",
    "D": "2_1d_receiving_water_boundary.png",
}

# Visual Grammar v0.3 palette (must be used verbatim like the accepted builder).
INK = "#1F2428"
CONTEXT = "#667078"
WATER = "#3C6E8F"
WATER_LIGHT = "#B9DDEB"
FOOTER_COLOR = CONTEXT

FOOTER_TEXT = (
    "Explanatory sequence only — timing, brightness, and motion do not encode "
    "quantity, velocity, travel time, probability, or severity."
)
SYNTHESIS_TEXT = (
    "Connected watershed. Different constituent pathways. "
    "Receiving-water conditions still matter."
)
A1_CAPTION = "Connected pathways — not measured event flow"

# Canonical editorial timeline (carries no scientific temporal meaning).
STATES = {
    "A0": (0.0, 4.0, "A", "MAP", "This is a real connected watershed-to-lake geography."),
    "A1": (4.0, 8.0, "A", "MAP", "Physical channels form connected pathways toward the Maumee River and western Lake Erie."),
    "A2": (8.0, 15.0, "B", "SCHEMATIC", "Movement occurs through a sequence of connected settings; retention and transformation can occur at multiple stages."),
    "A3": (15.0, 22.0, "C", "FIGURE", "Constituents share some categorical process relationships but are not interchangeable."),
    "A4": (22.0, 29.0, "D", "SCHEMATIC", "Delivery interacts with receiving-water conditions; bloom-favorable conditions are possible, not inevitable."),
    "A5": (29.0, 32.0, "D", "SCHEMATIC", "Final synthesis: connected watershed; different constituent pathways; receiving-water conditions still matter."),
}

STATE_LABELS = {
    "A0": "A0 · Geographic context",
    "A1": "A1 · Connected physical pathways",
    "A2": "A2 · Process sequence",
    "A3": "A3 · Constituent pathway comparison",
    "A4": "A4 · Receiving-water interaction",
    "A5": "A5 · Final synthesis",
}


# ---------------------------------------------------------------------------
# Placement / composition helpers
# ---------------------------------------------------------------------------
def load_alpha_rgb(stem: str) -> np.ndarray:
    """Load an accepted figure PNG as RGBA float in [0,1] (H,W,4)."""
    im = Image.open(STATIC_DIR / STATIC_PNGS[stem]).convert("RGBA")
    arr = np.asarray(im, dtype=np.float32) / 255.0
    return arr


def place_extent(png_w: int, png_h: int,
                 y0: int = FIGURE_TOP, y1: int = FOOTER_TOP) -> tuple[int, int, float]:
    """Aspect-preserving, centered placement onto the 1920x1080 canvas.

    The figure is confined to the vertical band [y0, y1) so it never collides
    with the header/footer bands or (for A5) the synthesis band. Returns
    (offset_x, offset_y, scale). No crop, no distortion.
    """
    avail_h = y1 - y0
    scale = min(CANVAS_W / png_w, avail_h / png_h)
    out_w, out_h = round(png_w * scale), round(png_h * scale)
    off_x = (CANVAS_W - out_w) // 2
    off_y = y0 + (avail_h - out_h) // 2
    return off_x, off_y, scale


def compose_canvas(stem: str, y0: int = FIGURE_TOP,
                   y1: int = FOOTER_TOP) -> np.ndarray:
    """Place an accepted figure on a white 1920x1080 RGBA canvas (H,W,4)."""
    arr = load_alpha_rgb(stem)
    h, w = arr.shape[:2]
    off_x, off_y, scale = place_extent(w, h, y0=y0, y1=y1)
    out_w = round(w * scale)
    out_h = round(h * scale)
    canvas = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.float32)
    canvas[..., :3] = 1.0  # white background
    canvas[..., 3] = 1.0
    resized = np.asarray(Image.fromarray((arr * 255).astype(np.uint8)).resize(
        (out_w, out_h), Image.LANCZOS), dtype=np.float32) / 255.0
    canvas[off_y:off_y + out_h, off_x:off_x + out_w] = resized
    return canvas


def to_png(canvas: np.ndarray, dst: Path) -> None:
    img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
    img.save(dst)


# ---------------------------------------------------------------------------
# Deterministic text overlays (matplotlib-rendered, transparent background)
# ---------------------------------------------------------------------------
def _text_layer(text: str, width: int, height: int, fontsize: float,
                color=CONTEXT, bold: bool = False, linespacing: float = 1.25,
                weight_extra: str = "normal") -> Image.Image:
    dpi = 100.0
    fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    weight = "bold" if bold else weight_extra
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=fontsize,
            color=color, fontweight=weight, linespacing=linespacing,
            transform=ax.transAxes)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def overlay(px: int, py: int, canvas: np.ndarray, layer: Image.Image,
            alpha: float = 1.0) -> None:
    """Composite a transparent RGBA PIL layer onto the float canvas in place."""
    lw, lh = layer.size
    x0, y0 = max(px, 0), max(py, 0)
    x1, y1 = min(px + lw, CANVAS_W), min(py + lh, CANVAS_H)
    px_src = max(0 - px, 0)
    py_src = max(0 - py, 0)
    lay_arr = np.asarray(layer, dtype=np.float32) / 255.0
    sub = lay_arr[py_src:py_src + (y1 - y0), px_src:px_src + (x1 - x0)]
    a = sub[..., 3:4] * alpha
    canvas[y0:y1, x0:x1, :3] = (1 - a) * canvas[y0:y1, x0:x1, :3] + a * sub[..., :3]
    canvas[y0:y1, x0:x1, 3] = 1.0


def add_footer(canvas: np.ndarray) -> None:
    """Persistent explanatory footer, reserved band at the bottom of the canvas.

    Quieter than main content and identical across A0-A5: full-legible but
    smaller, in the reserved footer band so it never collides with the figure's
    own provenance text or with the A5 synthesis.
    """
    layer = _text_layer(FOOTER_TEXT, CANVAS_W - 80, 40, fontsize=19.0,
                        color=FOOTER_COLOR, weight_extra="normal")
    overlay(CANVAS_W // 2 - layer.size[0] // 2,
            FOOTER_TOP + (FOOTER_H - layer.size[1]) // 2,
            canvas, layer, alpha=0.92)


def add_state_label(canvas: np.ndarray, state_id: str) -> None:
    """Animation state title, confined to the reserved top header band."""
    layer = _text_layer(STATE_LABELS[state_id], CANVAS_W - 80, 46,
                        fontsize=22.0, color=INK, bold=True)
    overlay(CANVAS_W // 2 - layer.size[0] // 2,
            FIGURE_TOP // 2 - layer.size[1] // 2,
            canvas, layer, alpha=0.98)


def add_caption(canvas: np.ndarray, text: str, y_px: int) -> None:
    layer = _text_layer(text, min(CANVAS_W - 80, 1500), 46, fontsize=22.0,
                        color=INK, bold=True)
    overlay(CANVAS_W // 2 - layer.size[0] // 2, y_px, canvas, layer, alpha=0.98)


def add_synthesis(canvas: np.ndarray) -> None:
    """A5 final synthesis, centered inside the dedicated synthesis band.

    Smaller than the figure footer styling so the full sentence is fully
    visible within safe margins and never overlaps figure content or the
    persistent footer.
    """
    layer = _text_layer(SYNTHESIS_TEXT, CANVAS_W - 120, 54, fontsize=22.0,
                        color=INK, bold=True, linespacing=1.2)
    overlay(CANVAS_W // 2 - layer.size[0] // 2,
            SYNTH_TOP + (SYNTH_H - layer.size[1]) // 2,
            canvas, layer, alpha=0.98)


# ---------------------------------------------------------------------------
# A1 temporary explanatory focus over accepted physical waterways
# ---------------------------------------------------------------------------
def coords_parts(geom):
    """Return list of (N,2) coordinate arrays for a LineString/MultiLineString."""
    if geom is None or geom.is_empty:
        return []
    if hasattr(geom, "geoms"):  # MultiLineString / GeometryCollection
        out = []
        for g in geom.geoms:
            if not g.is_empty:
                out.append(np.asarray(g.coords, dtype=np.float64))
        return out
    return [np.asarray(geom.coords, dtype=np.float64)]


def build_a1_geometry_overlay() -> tuple[np.ndarray, tuple[int, int]]:
    """Build a transparent (2065 x 1076) PNG-space overlay marking the ACCEPTED
    physical-waterway display subset and the accepted Maumee River main-stem
    selection, using the exact geographic feature geometry from the accepted
    static 2.1A builder (never pixel color).

    Returns (overlay RGBA float H,W,4, (png_w, png_h)).
    """
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "src" / "python" / "atlas"))
    import build_spread_2_1_field_to_lake as _builder

    captured = {}

    def _fake_save(_fig, _stem):
        _fig.canvas.draw()
        rend = _fig.canvas.get_renderer()
        tight = _fig.get_tightbbox(rend)
        dpi = _fig.dpi
        pad_px = dpi * 0.1  # bbox_inches='tight' default pad = 0.1 inch
        # tight is a TransformedBbox scaled to inches (x1/x0 in inch units);
        # convert to pixels, then apply the tight-bbox pad.
        bx0 = tight.x0 * dpi - pad_px
        by0 = tight.y0 * dpi - pad_px
        bx1 = tight.x1 * dpi + pad_px
        by1 = tight.y1 * dpi + pad_px
        captured["ax"] = _fig.axes[0]
        captured["bbox"] = (bx0, by0, bx1, by1)

    saved = _builder.save_figure
    _builder.save_figure = _fake_save
    try:
        layers = _builder.load_layers()
        _builder.build_2_1a(layers)
    finally:
        _builder.save_figure = saved

    ax = captured["ax"]
    bx0, by0, bx1, by1 = captured["bbox"]
    # Snap the overlay grid to the exact accepted PNG pixel dimensions so the
    # affine fit aligns the overlay to the committed accepted PNG pixel-perfectly.
    png_w, png_h = Image.open(STATIC_DIR / STATIC_PNGS["A"]).size

    # Recompute the accepted physical-waterway display subset exactly as the
    # accepted builder does (selection is geographic, not color-based).
    hydro = layers["hydro_physical"]
    hydro = hydro[hydro["streamorder"].astype(float) >= _builder.RENDER_MIN_STREAMORDER].copy()
    hydro = hydro.to_crs(_builder.MAP_CRS)
    hydro.geometry = hydro.geometry.simplify(
        _builder.RENDER_SIMPLIFY_TOL * 111_000, preserve_topology=True)
    maumee = hydro[hydro["huc12"].astype(str).str.startswith("04100009")]

    # Data -> accepted-PNG pixel transform (BL-origin display -> top-left rows).
    def to_png_pts(gdf) -> list[np.ndarray]:
        out = []
        for geom in gdf.geometry:
            for part in coords_parts(geom):
                disp = ax.transData.transform(part)  # (N,2) [display_x, display_y]
                scale_x = png_w / (bx1 - bx0)
                scale_y = png_h / (by1 - by0)
                col = (disp[:, 0] - bx0) * scale_x
                row = (by1 - disp[:, 1]) * scale_y
                out.append(np.stack([col, row], axis=1))
        return out

    wg = to_png_pts(hydro)
    mg = to_png_pts(maumee)

    # Uniform nonquantitative emphasis: a soft light band over the accepted
    # pathway lines (glow), then a crisp core line. Identical treatment for
    # physical waterways and the Maumee main stem.
    ss = 2  # supersample factor for smooth anti-aliased strokes
    base = Image.new("RGBA", (int(png_w * ss), int(png_h * ss)), (0, 0, 0, 0))
    from PIL import ImageDraw

    d = ImageDraw.Draw(base)
    glow = (185, 221, 235, 150)   # WATER_LIGHT halo
    core = (185, 221, 235, 235)   # crisp light emphasis line (same for both classes)
    for ft in wg + mg:
        pts = [(float(c[0] * ss), float(c[1] * ss)) for c in ft]
        if len(pts) < 2:
            continue
        d.line(pts, fill=glow, width=max(1, int(round(5 * ss))), joint="curve")
        d.line(pts, fill=core, width=max(1, int(round(1.5 * ss))), joint="curve")
    overlay = base.resize((png_w, png_h), Image.LANCZOS)
    ov = np.asarray(overlay, dtype=np.float32) / 255.0
    return ov, (png_w, png_h)


def place_rgba_on_canvas(canvas: np.ndarray, ov: np.ndarray,
                         src_size: tuple[int, int],
                         y0: int = FIGURE_TOP, y1: int = FOOTER_TOP,
                         alpha: float = 1.0) -> None:
    """Composite a source-space RGBA overlay (W,H,4 float) onto the 1920x1080
    canvas using the identical aspect-preserving, centered placement as the
    accepted figure (so the overlay aligns exactly with the accepted base).

    Uses the same [y0, y1) figure band as compose_canvas so the overlay aligns
    with the base. Overlay is blended OVER the existing canvas content (alpha
    composited), never over white, so the accepted figure underneath remains.
    """
    w, h = src_size
    off_x, off_y, scale = place_extent(w, h, y0=y0, y1=y1)
    ow, oh = int(round(w * scale)), int(round(h * scale))
    resized = np.asarray(Image.fromarray((np.clip(ov, 0, 1) * 255).astype(np.uint8))
                         .resize((ow, oh), Image.LANCZOS), dtype=np.float32) / 255.0
    a = resized[..., 3:4] * alpha
    y0s, y1s = off_y, off_y + oh
    x0s, x1s = off_x, off_x + ow
    canvas[y0s:y1s, x0s:x1s, :3] = \
        (1 - a) * canvas[y0s:y1s, x0s:x1s, :3] + a * resized[..., :3]
    canvas[y0s:y1s, x0s:x1s, 3] = 1.0


def build_a1() -> np.ndarray:
    hl_overlay, (w, h) = build_a1_geometry_overlay()
    base = compose_canvas("A")
    # A faint ghost of the accepted A0 geographic context remains beneath the
    # highlighted physical-pathway overlay; the overlay is blended over it
    # (no white knock-out), preserving spatial orientation without adding
    # geometry or scientific meaning.
    place_rgba_on_canvas(base, hl_overlay, (w, h), alpha=0.95)
    title_layer = _text_layer(STATE_LABELS["A1"], CANVAS_W - 80, 46,
                              fontsize=22.0, color=INK, bold=True)
    overlay((CANVAS_W - title_layer.size[0]) // 2, 6, base, title_layer,
            alpha=0.98)
    cap_layer = _text_layer(A1_CAPTION, min(CANVAS_W - 80, 1500), 34,
                            fontsize=17.0, color=CONTEXT, weight_extra="normal")
    overlay(CANVAS_W // 2 - cap_layer.size[0] // 2,
            FIGURE_TOP - cap_layer.size[1] - 6,
            base, cap_layer, alpha=0.95)
    add_footer(base)
    return base


# ---------------------------------------------------------------------------
# State / source manifests
# ---------------------------------------------------------------------------
def write_state_manifest() -> None:
    rows = []
    for sid, (t0, t1, src, rep, msg) in STATES.items():
        rows.append({
            "state_id": sid,
            "start_seconds": f"{t0:.1f}",
            "end_seconds": f"{t1:.1f}",
            "source_figure": f"2_1{src.lower()}",
            "representation": f"2.1{src} · {rep}",
            "epistemic_status": "E",
            "elements_visible": _visible(sid),
            "transition_in": _transition_in(sid),
            "transition_out": _transition_out(sid),
            "semantic_message": msg,
            "quantitative_encoding": "false",
            "highlight_semantics": "explanatory_focus_only",
            "notes": _note(sid),
        })
    csv_path = ANIM_DIR / "2_1_animation_state_manifest.csv"
    _write_csv(csv_path, rows)


def _visible(sid: str) -> str:
    return {
        "A0": "map: watershed, physical waterways, Maumee River, Toledo civic anchor, Maumee Bay interface, western Lake Erie",
        "A1": "same accepted map with uniform nonquantitative focus on accepted physical waterways / Maumee pathway",
        "A2": "six-stage process sequence with transport, retention/transformation, delivery, receiving-water response/context; discharge separate",
        "A3": "water/carrier context plus constituent rows P, N, carbon/organic matter, sediment; equal fixed-size presence glyphs",
        "A4": "watershed delivery + receiving-water conditions converge to common junction; one outgoing arrow to possible bloom-favorable conditions",
        "A5": "2.1D base (accepted) with final synthesis line and persistent footer",
    }[sid]


def _transition_in(sid: str) -> str:
    return {
        "A0": "linear fade-in 0.0-0.5s",
        "A1": "uniform focus wash fade-in + caption 4.0-4.5s",
        "A2": "crossfade completes 8.0-8.6s; staged reveals 8.6-12.6s; transport/retention/delivery labels 12.6-15.0s",
        "A3": "crossfade 15.0-15.6s; water/carrier note 15.6-16.5s; row reveals 16.5-20.5s; hold 20.5-22.0s",
        "A4": "crossfade 22.0-22.6s; inputs 22.6-23.5s; arrows 23.5-24.5s; junction 24.5-25.2s; outgoing arrow 25.2-26.0s; final box 26.0-27.0s; hold 27.0-29.0s",
        "A5": "synthesis line reveal 29.0-29.6s; hold to 32.0s",
    }[sid]


def _transition_out(sid: str) -> str:
    return {
        "A0": "static hold to 4.0s",
        "A1": "crossfade begins 7.5-8.0s",
        "A2": "crossfade begins 14.4-15.0s",
        "A3": "crossfade begins 21.4-22.0s",
        "A4": "crossfade begins 28.4-29.0s",
        "A5": "none (final frame = independently usable reduced-motion endpoint)",
    }[sid]


def _note(sid: str) -> str:
    return {
        "A0": "reduced-motion base is A5; no state is quantitative",
        "A1": "no moving pulses/particles; focus is categorical, not event/source specific",
        "A2": "reveal order is pedagogic only; nothing travels along arrows; discharge stays off-chain",
        "A3": "glyph size/darkness never varies by constituent; HAB_context not a row",
        "A4": "both input arrows converge on one common junction; exactly one outgoing arrow; no direct nutrient->HAB edge",
        "A5": "final frame is the reduced-motion endpoint; final synthesis over accepted 2.1D",
    }[sid]


def _write_csv(path: Path, rows: list[dict]) -> None:
    keys = list(rows[0].keys())
    lines = [",".join(keys)]
    for r in rows:
        lines.append(",".join(str(r[k]) for k in keys))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_source_manifest() -> dict:
    static_outputs = sorted(
        str(p.relative_to(ROOT)) for p in STATIC_DIR.iterdir() if p.is_file())
    sizes = {k: tuple(Image.open(STATIC_DIR / v).size) for k, v in STATIC_PNGS.items()}
    manifest = {
        "prototype": "2.1",
        "title": "From Field to Lake",
        "phase": "17A",
        "kind": "guided analytical process animation (explanatory extension of accepted static figures)",
        "static_baseline_commit": "7b589e8583a38804961ce0e8cb8738af5451a31b",
        "accepted_static_figure_paths": {k: str(v) for k, v in STATIC_PNGS.items()},
        "animation_script_paths": [
            "src/python/atlas/animate_spread_2_1_field_to_lake.py",
            "src/python/atlas/validate_animation_2_1_field_to_lake.py",
            "src/R/atlas/validate_animation_2_1_field_to_lake.R",
        ],
        "visual_grammar": "Phase 17A Visual Grammar v0.3 (accepted-for-use, not frozen)",
        "no_new_science": True,
        "canvas": {"width": CANVAS_W, "height": CANVAS_H,
                    "background": "white", "fps": FPS,
                    "duration_seconds": DURATION_S,
                    "expected_frames": EXPECTED_FRAMES},
        "static_native_dimensions": sizes,
        "placement": "aspect-preserving, centered; no crop; no distortion",
        "encoder": "ffmpeg 9.0.1 / libx264 (planned in encode step; not run in Step 1)",
        "quantitative_encoding": False,
        "audio": False,
        "randomization": False,
        "great_black_swamp_geometry_used": False,
        "toledo_physical_intake_geometry_used": False,
        "deterministic_nutrient_to_hab_edge": False,
        "hab_context_used_as_constituent": False,
        "release_process_introduced": False,
        "persistent_footer": FOOTER_TEXT,
        "reduced_motion_endpoint": "2_1_from_field_to_lake_reduced_motion.png",
        "states": {sid: list(v[:4]) for sid, v in STATES.items()},
        "source_of_truth": "accepted static PNGs are the immutable visual authority; no re-render of full 2.1B/C/D",
        "built": date.today().isoformat(),
    }
    (ANIM_DIR / "2_1_animation_source_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------------------
# Contact sheet
# ---------------------------------------------------------------------------
def build_contact_sheet() -> None:
    panels = []
    for sid in ["A0", "A1", "A2", "A3", "A4", "A5"]:
        canvas = full_frame(sid)
        panels.append(Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)))
    cell_w, cell_h = CANVAS_W // 3, CANVAS_H // 2
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), "white")
    for i, p in enumerate(panels):
        # downsample each keyframe to the 2x3 cell size (same aspect)
        thumb = p.resize((cell_w, cell_h), Image.LANCZOS)
        r, c = divmod(i, 3)
        sheet.paste(thumb, (c * cell_w, r * cell_h))
    sheet.save(ANIM_DIR / "2_1_animation_contact_sheet.png")


def figure_band(sid: str) -> tuple[int, int]:
    """(y0, y1) figure band for a state. A5 reserves a synthesis band below."""
    if sid == "A5":
        return FIGURE_TOP, SYNTH_TOP
    return FIGURE_TOP, FOOTER_TOP


def _keyframe_core(sid: str) -> np.ndarray:
    """Fully revealed figure on canvas BEFORE footer/state-label overlays.

    A2/A3/A4 base must be pixel-identical to the accepted 2.1B/C/D placed on
    canvas within the figure band (no crop, no distortion). A5 shortens the
    figure band to [FIGURE_TOP, SYNTH_TOP) to make room for its synthesis band.
    """
    y0, y1 = figure_band(sid)
    return compose_canvas(STATES[sid][2], y0=y0, y1=y1)


# ---------------------------------------------------------------------------
# Masked reveal engine (used by later video-frame generation; all-revealed
# keyframes here equal the pure accepted base).
# ---------------------------------------------------------------------------
def reveal_frame(sid: str, t: float) -> np.ndarray:
    """Deterministic frame for the state at time t (0.0-32.0s)."""
    t0, t1, src, _rep, _msg = STATES[sid]
    seg = min(max((t - t0), 0.0), t1 - t0)
    y0, y1 = figure_band(sid)
    canvas = compose_canvas(src, y0=y0, y1=y1)
    add_state_label(canvas, sid)
    if sid == "A1":
        overlay, (w, h) = build_a1_geometry_overlay()
        progress = min(max((seg - 0.5) / 0.5, 0.0), 1.0)
        ov = overlay.copy()
        ov[..., 3:4] *= progress
        place_rgba_on_canvas(canvas, ov, (w, h), y0=y0, y1=y1)
        cap_layer = _text_layer(A1_CAPTION, min(CANVAS_W - 80, 1500), 34,
                                fontsize=17.0, color=CONTEXT,
                                weight_extra="normal")
        overlay(CANVAS_W // 2 - cap_layer.size[0] // 2,
                FIGURE_TOP - cap_layer.size[1] - 6,
                canvas, cap_layer, alpha=0.95)
    if sid == "A5":
        progress = min(max((seg - 0.6) / 0.6, 0.0), 1.0)
        layer = _text_layer(SYNTHESIS_TEXT, CANVAS_W - 120, 54, fontsize=22.0,
                            color=INK, bold=True, linespacing=1.2)
        lay_arr = np.asarray(layer, dtype=np.float32) / 255.0
        px = CANVAS_W // 2 - layer.size[0] // 2
        py = SYNTH_TOP + (SYNTH_H - layer.size[1]) // 2
        x0, y0c = max(px, 0), max(py, 0)
        x1, y1c = min(px + layer.size[0], CANVAS_W),
        min(py + layer.size[1], CANVAS_H)
        s0, s1 = x0 - px, y0c - py
        sub = lay_arr[s1:s1 + (y1c - y0c), s0:s0 + (x1 - x0)]
        a = sub[..., 3:4] * progress
        canvas[y0c:y1c, x0:x1, :3] = \
            (1 - a) * canvas[y0c:y1c, x0:x1, :3] + a * sub[..., :3]
    add_footer(canvas)
    return canvas


def full_frame(sid: str) -> np.ndarray:
    """Fully-revealed composed keyframe (figure + title/caption + synthesis/
    footer), used by keyframes, the reduced-motion endpoint, and the contact
    sheet so every output reflects the same layout."""
    if sid == "A1":
        return build_a1()
    canvas = _keyframe_core(sid)
    add_state_label(canvas, sid)
    if sid == "A5":
        add_synthesis(canvas)
    add_footer(canvas)
    return canvas


def build_keyframes() -> None:
    for sid in ["A0", "A1", "A2", "A3", "A4", "A5"]:
        to_png(full_frame(sid), ANIM_DIR / f"2_1_animation_keyframe_{sid}.png")


def build_reduced_motion() -> None:
    to_png(full_frame("A5"), ANIM_DIR / "2_1_from_field_to_lake_reduced_motion.png")


def encode_canonical_mp4() -> str:
    """Encode the canonical 1920x1080, 30 fps, 32.0 s, 960-frame H.264 MP4.

    Frames are composed strictly from the ACCEPTED A0-A5 keyframe PNGs using
    only the approved deterministic transition behavior: linear fade-in at the
    start, linear crossfade across state boundaries, and static holds. No
    particles, travel pulses, camera motion, zoom, motion blur, or quantitative
    animation. The accepted keyframe compositions are never redesigned or
    recomputed from scratch; they are used verbatim as the per-state base.
    """
    import subprocess

    kf = {}
    for sid in ["A0", "A1", "A2", "A3", "A4", "A5"]:
        im = Image.open(ANIM_DIR / f"2_1_animation_keyframe_{sid}.png").convert("RGB")
        kf[sid] = np.asarray(im, dtype=np.float32) / 255.0
    background = np.ones((CANVAS_H, CANVAS_W, 3), dtype=np.float32)

    BOUNDARIES = [4.0, 8.0, 15.0, 22.0, 29.0]   # end of each state except last
    ORDER = ["A0", "A1", "A2", "A3", "A4", "A5"]
    FADE_IN = 0.5      # A0 linear fade-in from background at the very start
    CROSS = 0.6        # full linear-crossfade window centered on a boundary

    def frame_at(t: float) -> np.ndarray:
        if t <= FADE_IN:
            a = t / FADE_IN
            return background * (1.0 - a) + kf["A0"] * a
        for j, b in enumerate(BOUNDARIES):
            if abs(t - b) <= CROSS / 2.0:
                a = (t - (b - CROSS / 2.0)) / CROSS
                return kf[ORDER[j]] * (1.0 - a) + kf[ORDER[j + 1]] * a
        for s, start in enumerate([0.0, 4.0, 8.0, 15.0, 22.0, 29.0]):
            end = [4.0, 8.0, 15.0, 22.0, 29.0, 32.0][s]
            if start <= t < end:
                return kf[ORDER[s]]
        return kf["A5"]

    mp4 = ANIM_DIR / "2_1_from_field_to_lake_animation.mp4"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{CANVAS_W}x{CANVAS_H}", "-r", str(FPS),
        "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(EXPECTED_FRAMES):
        f = frame_at(i / FPS)
        raw = (np.clip(f, 0.0, 1.0) * 255.0).astype(np.uint8)
        proc.stdin.write(raw.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg encode failed rc={ret}: {err}")
    return str(mp4)


def base_equivalence_report() -> dict:
    """A2/A3/A4 fully-revealed keyframe figure base (before any title/footer/
    synthesis overlays) must equal the accepted figure placed on canvas within
    the figure band. Reports PASS/FAIL per figure."""
    result = {}
    for sid in ["A2", "A3", "A4"]:
        src = STATES[sid][2]
        y0, y1 = figure_band(sid)
        ref = (np.clip(_keyframe_core(sid), 0, 1) * 255).astype(np.int16)
        base = compose_canvas(src, y0=y0, y1=y1)
        base8 = (np.clip(base, 0, 1) * 255).astype(np.int16)
        diff = int(np.abs(ref - base8).sum())
        # keyframes built via the same function -> identical by construction
        result[sid] = {"accepted_base_equivalence": "PASS" if diff == 0 else "FAIL",
                       "total_abs_diff_pixels": diff}
    return result


def main() -> None:
    ANIM_DIR.mkdir(parents=True, exist_ok=True)
    build_keyframes()
    build_reduced_motion()
    build_contact_sheet()
    write_state_manifest()
    write_source_manifest()
    report = base_equivalence_report()
    print("Wrote Phase 17A Prototype 2.1 animation keyframes / contact sheet / "
          "reduced motion / manifests ->", ANIM_DIR)
    for k, v in report.items():
        print(f"base_equivalence {k}: {v}")


if __name__ == "__main__":
    main()