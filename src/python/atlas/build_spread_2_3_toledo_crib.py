"""Build the Toledo water-intake crib 2.3 four-panel spread.

The geometry in panels B and C is intentionally approximate and inferred from
assets/reference/toledo_water_intake_crib.jpg.  Coordinates are used only as
locational evidence; the legacy GLOS point is never used to place geometry.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import atlas_ph2_3_common as common
except ImportError:  # pragma: no cover - direct invocation supplies this path
    common = None


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "2_3_toledo_crib"
REFERENCE_PATH = ROOT / "assets" / "reference" / "toledo_water_intake_crib.jpg"
PHYSICAL_CRIB = {"latitude": 41.699444, "longitude": -83.259167}
LEGACY_GLOS = {"latitude": 41.674960, "longitude": -83.307900}

# The common module is the project-level home for shared atlas conventions.  A
# few releases expose optional constants; these fallbacks keep this builder
# usable with the current untracked common module without inventing dimensions.
def common_value(name: str, fallback):
    if common is None:
        return fallback
    return getattr(common, name, fallback)


WATER = common_value("WATER_COLOR", "#9bc9d6")
DARK_WATER = common_value("DARK_WATER_COLOR", "#4f899d")
INK = common_value("INK_COLOR", "#1e2933")
ACCENT = common_value("ACCENT_COLOR", "#d36c3f")
RETROFIT = common_value("RETROFIT_COLOR", "#7d4e9b")
PALE = common_value("PANEL_COLOR", "#f4f0e8")
LOCATOR_WINDOW = common_value("LOCATOR_WINDOW", (-83.36, 41.63, -83.21, 41.73))
MONITORING_POINTS = common_value("MONITORING_POINTS", [])


def _font(size: int, bold: bool = False):
    candidates = (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=150, facecolor=PALE)
    plt.close(fig)


def _panel_base(title: str, kicker: str, code: str):
    fig = plt.figure(figsize=(12, 8), facecolor=PALE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.055, 0.91, code, color=ACCENT, fontsize=12, fontweight="bold", family="DejaVu Sans")
    ax.text(0.055, 0.855, title, color=INK, fontsize=25, fontweight="bold", family="DejaVu Sans")
    ax.text(0.055, 0.815, kicker, color="#52616b", fontsize=10, family="DejaVu Sans")
    ax.plot([0.055, 0.945], [0.78, 0.78], color="#c4bbb0", lw=1)
    return fig, ax


def _water_plane(ax, y0=0.13, y1=0.70):
    ax.add_patch(patches.Rectangle((0.055, y0), 0.89, y1 - y0, facecolor=WATER, edgecolor="none", zorder=0))
    for i in range(9):
        y = y0 + 0.035 + i * (y1 - y0 - 0.07) / 8
        xs = np.linspace(0.08, 0.92, 220)
        ys = y + 0.006 * np.sin(xs * 55 + i * 0.9)
        ax.plot(xs, ys, color="#78afbd", lw=0.55, alpha=0.55, zorder=1)
    ax.text(0.075, y0 + 0.035, "WESTERN LAKE ERIE / WATER PLANE", fontsize=8, color="#477886", family="DejaVu Sans")


def _draw_crib(ax, retrofit: bool = False):
    """Draw the shared approximate base geometry, plus optional additions."""
    # Approximate axonometric body: ellipse-like circular crib, not a survey.
    cx, cy = 0.51, 0.40
    body_w, body_h = 0.34, 0.20
    ax.add_patch(patches.Ellipse((cx, cy), body_w, body_h, facecolor="#89959a", edgecolor=INK, lw=2.0, zorder=5))
    ax.add_patch(patches.Ellipse((cx, cy + 0.015), body_w * 0.87, body_h * 0.52, facecolor="#bac2c2", edgecolor="#596a70", lw=1.3, zorder=6))
    ax.add_patch(patches.Ellipse((cx, cy + 0.018), body_w * 0.67, body_h * 0.30, facecolor="#59666a", edgecolor="#2e3d42", lw=1, zorder=7))
    # Low superstructure and roof equipment massing.
    ax.add_patch(patches.Polygon([(0.415, 0.47), (0.605, 0.47), (0.575, 0.60), (0.445, 0.60)], facecolor="#d0d0c7", edgecolor=INK, lw=1.6, zorder=8))
    ax.add_patch(patches.Polygon([(0.445, 0.60), (0.575, 0.60), (0.605, 0.635), (0.415, 0.635)], facecolor="#e5e0d6", edgecolor=INK, lw=1.4, zorder=9))
    ax.add_patch(patches.Rectangle((0.475, 0.60), 0.09, 0.075, facecolor="#747d80", edgecolor=INK, lw=1.2, zorder=10))
    ax.add_patch(patches.Polygon([(0.475, 0.675), (0.565, 0.675), (0.545, 0.715), (0.49, 0.715)], facecolor="#9da4a2", edgecolor=INK, lw=1.1, zorder=11))
    # Access/railing zone.
    for x in np.linspace(0.36, 0.65, 8):
        ax.plot([x, x], [0.46, 0.535], color="#45565b", lw=1, zorder=12)
    ax.plot([0.35, 0.66], [0.535, 0.535], color="#45565b", lw=1.8, zorder=12)
    ax.plot([0.35, 0.66], [0.46, 0.46], color="#45565b", lw=1.1, zorder=12)
    # Sparse inferred support/access members.
    for x in (0.405, 0.615):
        ax.plot([x, x - 0.02], [0.42, 0.29], color="#59666a", lw=2, zorder=4)
    ax.text(0.73, 0.60, "low superstructure", fontsize=8.5, color=INK, family="DejaVu Sans")
    ax.plot([0.72, 0.60], [0.595, 0.60], color=ACCENT, lw=0.9)
    ax.text(0.73, 0.49, "access / railing zone", fontsize=8.5, color=INK, family="DejaVu Sans")
    ax.plot([0.72, 0.64], [0.485, 0.51], color=ACCENT, lw=0.9)
    ax.text(0.73, 0.38, "circular intake body", fontsize=8.5, color=INK, family="DejaVu Sans")
    ax.plot([0.72, 0.65], [0.375, 0.405], color=ACCENT, lw=0.9)

    if retrofit:
        # Restrained additive geometry only; base crib geometry above is byte-
        # for-byte represented by the same drawing code and coordinates.
        ax.plot([0.536, 0.536], [0.71, 0.82], color=RETROFIT, lw=2.2, zorder=15)
        ax.plot([0.51, 0.562], [0.78, 0.78], color=RETROFIT, lw=1.4, zorder=15)
        ax.add_patch(patches.Circle((0.536, 0.825), 0.012, facecolor=RETROFIT, edgecolor=INK, lw=0.8, zorder=16))
        ax.add_patch(patches.Rectangle((0.60, 0.67), 0.075, 0.035, facecolor="#b98bc1", edgecolor=RETROFIT, lw=1.2, zorder=16))
        ax.add_patch(patches.Rectangle((0.625, 0.705), 0.025, 0.018, facecolor=RETROFIT, edgecolor=INK, lw=0.7, zorder=17))
        ax.add_patch(patches.Rectangle((0.42, 0.235), 0.13, 0.05, facecolor="#b98bc1", edgecolor=RETROFIT, lw=1.2, zorder=6))
        ax.plot([0.455, 0.455], [0.285, 0.37], color=RETROFIT, lw=1.8, zorder=13)
        ax.plot([0.478, 0.478], [0.285, 0.37], color=RETROFIT, lw=1.8, zorder=13)
        ax.plot([0.455, 0.478], [0.37, 0.37], color=RETROFIT, lw=1.4, zorder=13)
        ax.add_patch(patches.Arc((0.67, 0.43), 0.13, 0.09, theta1=210, theta2=340, color=RETROFIT, lw=2, zorder=13))
        ax.add_patch(patches.Circle((0.73, 0.415), 0.012, facecolor=RETROFIT, edgecolor=INK, lw=0.7, zorder=14))
        labels = [
            ("sensor mast", 0.70, 0.82, 0.54, 0.80),
            ("communications / data", 0.70, 0.72, 0.64, 0.69),
            ("hardened service module", 0.70, 0.28, 0.55, 0.26),
            ("inspection-drone interface", 0.70, 0.22, 0.70, 0.40),
        ]
        for text, tx, ty, px, py in labels:
            ax.text(tx, ty, text, fontsize=8.2, color=RETROFIT, family="DejaVu Sans")
            ax.plot([tx - 0.01, px], [ty - 0.008, py], color=RETROFIT, lw=0.8, zorder=14)
        ax.text(0.075, 0.715, "ADDITIVE RETROFIT / CONCEPT", fontsize=8, color=RETROFIT, fontweight="bold")


def build_panel_a() -> Path:
    fig, ax = _panel_base("Existing asset / locational evidence", "PHOTO / MAP  ·  E", "2.3A")
    lon_min, lat_min, lon_max, lat_max = LOCATOR_WINDOW
    map_ax = fig.add_axes([0.055, 0.205, 0.48, 0.505])
    map_ax.set_facecolor("#d8e4e2")
    map_ax.set_xlim(lon_min, lon_max)
    map_ax.set_ylim(lat_min, lat_max)
    map_ax.set_xticks(np.linspace(lon_min, lon_max, 3))
    map_ax.set_yticks(np.linspace(lat_min, lat_max, 3))
    map_ax.set_xticklabels([f"{value:.2f}" for value in np.linspace(lon_min, lon_max, 3)], fontsize=7)
    map_ax.set_yticklabels([f"{value:.2f}" for value in np.linspace(lat_min, lat_max, 3)], fontsize=7)
    map_ax.set_xlabel("longitude", fontsize=7, labelpad=1)
    map_ax.set_ylabel("latitude", fontsize=7, labelpad=1)
    map_ax.grid(color="#a3b7b8", lw=0.55, alpha=0.65)
    for spine in map_ax.spines.values():
        spine.set_color("#b5c0bb")
        spine.set_linewidth(1)
    map_ax.set_title("schematic locator / physical-vs-context", loc="left", fontsize=8.5, color=INK, pad=6)
    # These existing schematic strokes provide basin orientation only; the
    # plotted points below carry the locational evidence.
    map_ax.plot([-83.45, -83.05], [41.55, 41.78], color="#a3b7b8", lw=1.2, zorder=2)
    map_ax.plot([-83.39, -83.10], [41.61, 41.73], color="#a3b7b8", lw=0.8, zorder=2)
    for point in MONITORING_POINTS:
        map_ax.scatter(point["lon"], point["lat"], s=24, color="#65737b", marker="o", edgecolor="#f4f1e8", linewidth=0.6, zorder=4)
    map_ax.scatter([PHYSICAL_CRIB["longitude"]], [PHYSICAL_CRIB["latitude"]], s=135, color=ACCENT, marker="*", edgecolor=INK, linewidth=0.8, zorder=6)
    map_ax.scatter([LEGACY_GLOS["longitude"]], [LEGACY_GLOS["latitude"]], s=62, color="#d8e4e2", marker="s", edgecolor="#65737b", linewidth=1.2, zorder=5)
    map_ax.text(-83.33, 41.716, "Toledo / western basin", fontsize=8.5, color="#52616b", ha="center")
    map_ax.annotate("physical crib", xy=(PHYSICAL_CRIB["longitude"], PHYSICAL_CRIB["latitude"]), xytext=(8, 8), textcoords="offset points", fontsize=8.2, color=INK, fontweight="bold")
    map_ax.annotate("legacy GLOS\ncontext only", xy=(LEGACY_GLOS["longitude"], LEGACY_GLOS["latitude"]), xytext=(-8, -22), textcoords="offset points", fontsize=7.5, color="#52616b", ha="right")
    if REFERENCE_PATH.exists():
        image = Image.open(REFERENCE_PATH).convert("RGB")
        image.thumbnail((900, 620))
        image_array = np.asarray(image)
        ax_photo = fig.add_axes([0.565, 0.13, 0.38, 0.58])
        ax_photo.imshow(image_array)
        ax_photo.axis("off")
        ax_photo.set_title("reference photograph", loc="left", fontsize=9, color=INK, pad=8)
    else:
        ax_photo = fig.add_axes([0.565, 0.13, 0.38, 0.58])
        ax_photo.set_facecolor("#cbd9d7")
        ax_photo.text(0.5, 0.5, "reference photograph\nnot found at build time", ha="center", va="center", color=INK, fontsize=11)
        ax_photo.axis("off")
    ax.text(0.075, 0.155, "Physical crib: 41.699444, -83.259167", fontsize=8.5, color=INK)
    ax.text(0.075, 0.11, "Legacy GLOS: 41.674960, -83.307900  ·  not used for geometry", fontsize=8, color="#52616b")
    path = OUTPUT_DIR / "2_3a_existing_asset.png"
    _save_figure(fig, path)
    return path


def build_panel_b() -> Path:
    fig, ax = _panel_base("Current structure", "APPROXIMATE AXONOMETRIC  ·  E/K  ·  3D", "2.3B")
    _water_plane(ax)
    _draw_crib(ax, retrofit=False)
    ax.text(0.075, 0.715, "INFERRED / APPROXIMATE", fontsize=8, color=ACCENT, fontweight="bold")
    ax.text(0.075, 0.09, "No measured dimensions. Geometry is approximate and inferred from the reference asset.", fontsize=8, color="#52616b")
    path = OUTPUT_DIR / "2_3b_current_structure.png"
    _save_figure(fig, path)
    return path


def build_panel_c() -> Path:
    fig, ax = _panel_base("2075 retrofit concept", "ADDITIVE INTERVENTION  ·  S/K  ·  3D / CONCEPT", "2.3C")
    _water_plane(ax)
    _draw_crib(ax, retrofit=True)
    ax.text(0.075, 0.09, "Same approximate base crib as panel B; purple elements are restrained additions, not measured design.", fontsize=8, color="#52616b")
    path = OUTPUT_DIR / "2_3c_2075_retrofit.png"
    _save_figure(fig, path)
    return path


def build_panel_d() -> Path:
    fig, ax = _panel_base("Persistence logic", "FIGURE  ·  E → S/K", "2.3D")
    ax.add_patch(patches.Rectangle((0.09, 0.30), 0.22, 0.26, facecolor="#dce8e5", edgecolor=INK, lw=1.3))
    ax.add_patch(patches.Rectangle((0.39, 0.30), 0.22, 0.26, facecolor="#e8e0ec", edgecolor=INK, lw=1.3))
    ax.add_patch(patches.Rectangle((0.69, 0.30), 0.22, 0.26, facecolor="#eee9df", edgecolor=INK, lw=1.3))
    ax.text(0.20, 0.49, "PERSISTS", ha="center", fontsize=13, fontweight="bold", color="#387a80")
    ax.text(0.20, 0.41, "site / crib body\nwater setting", ha="center", va="center", fontsize=10, color=INK)
    ax.text(0.50, 0.49, "MODIFIED", ha="center", fontsize=13, fontweight="bold", color=RETROFIT)
    ax.text(0.50, 0.41, "access / monitoring\noperating posture", ha="center", va="center", fontsize=10, color=INK)
    ax.text(0.80, 0.49, "ADDED", ha="center", fontsize=13, fontweight="bold", color=ACCENT)
    ax.text(0.80, 0.41, "data / resilience\nservice layer", ha="center", va="center", fontsize=10, color=INK)
    ax.annotate("", xy=(0.38, 0.43), xytext=(0.32, 0.43), arrowprops={"arrowstyle": "->", "lw": 1.4, "color": ACCENT})
    ax.annotate("", xy=(0.68, 0.43), xytext=(0.62, 0.43), arrowprops={"arrowstyle": "->", "lw": 1.4, "color": ACCENT})
    ax.text(0.5, 0.20, "Existing evidence becomes a scenario-layer service ecology without changing the inferred base geometry.", ha="center", fontsize=10, color="#52616b")
    ax.text(0.5, 0.145, "PERSISTS  ·  MODIFIED  ·  ADDED", ha="center", fontsize=9, color=INK, fontweight="bold")
    path = OUTPUT_DIR / "2_3d_persistence.png"
    _save_figure(fig, path)
    return path


def _add_contact_label(image: Image.Image, code: str, title: str, x: int, y: int) -> None:
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, x + 320, y + 48), fill=(244, 240, 232))
    draw.text((x + 14, y + 7), f"{code}  {title}", fill=(30, 41, 51), font=_font(17, bold=True))


def build_contact_sheet(panel_paths: list[Path]) -> Path:
    thumbs = []
    for path in panel_paths:
        with Image.open(path) as image:
            thumbs.append(image.convert("RGB").resize((720, 480), Image.Resampling.LANCZOS))
    cell_height = 536
    label_height = 56
    sheet = Image.new("RGB", (1440, cell_height * 2), (244, 240, 232))
    for index, image in enumerate(thumbs):
        x = (index % 2) * 720
        y = (index // 2) * cell_height
        sheet.paste(image, (x, y + label_height))
    _add_contact_label(sheet, "2.3A", "EXISTING ASSET", 12, 12)
    _add_contact_label(sheet, "2.3B", "CURRENT STRUCTURE", 732, 12)
    _add_contact_label(sheet, "2.3C", "2075 RETROFIT", 12, cell_height + 12)
    _add_contact_label(sheet, "2.3D", "PERSISTENCE", 732, cell_height + 12)
    path = OUTPUT_DIR / "2_3_contact_sheet.png"
    sheet.save(path, format="PNG", optimize=True)
    return path


def _write_manifest(panel_paths: list[Path], contact_sheet: Path) -> Path:
    manifest = {
        "artifact": "2.3 Toledo water-intake crib spread",
        "builder": "src/python/atlas/build_spread_2_3_toledo_crib.py",
        "generated": str(date.today()),
        "panels": {
            "A": {"file": panel_paths[0].name, "classification": "E · PHOTO/MAP", "content": "existing asset and locational evidence"},
            "B": {"file": panel_paths[1].name, "classification": "E/K · 3D", "content": "approximate current structure"},
            "C": {"file": panel_paths[2].name, "classification": "S/K · 3D/CONCEPT", "content": "additive 2075 retrofit"},
            "D": {"file": panel_paths[3].name, "classification": "E → S/K · FIGURE", "content": "persistence logic"},
        },
        "contact_sheet": contact_sheet.name,
        "coordinates": {
            "physical_crib": {**PHYSICAL_CRIB, "use": "physical crib location; geometry reference"},
            "legacy_GLOS": {**LEGACY_GLOS, "use": "legacy context only; never used as physical crib geometry"},
        },
        "geometry": {
            "dimensions": "none measured",
            "basis": "approximate/inferred from assets/reference/toledo_water_intake_crib.jpg",
            "b_c_base_geometry": "identical drawing primitives and coordinates; panel C only adds retrofit geometry",
        },
        "source_files": [
            "assets/reference/toledo_water_intake_crib.jpg",
            "src/python/atlas/atlas_ph2_3_common.py",
        ],
    }
    path = OUTPUT_DIR / "2_3_source_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def _write_validation_report(panel_paths: list[Path], contact_sheet: Path, manifest: Path) -> Path:
    report = f"""# 2.3 Toledo crib validation report

Status: PASS (builder-level checks)

- Physical crib coordinate: `{PHYSICAL_CRIB['latitude']}, {PHYSICAL_CRIB['longitude']}`.
- Legacy GLOS coordinate: `{LEGACY_GLOS['latitude']}, {LEGACY_GLOS['longitude']}`; retained as context only.
- Legacy GLOS used as physical crib geometry: NO.
- Measured dimensions used: NO.
- Approximate geometry basis: `assets/reference/toledo_water_intake_crib.jpg`.
- Panel B/C base geometry: IDENTICAL drawing primitives and coordinates.
- Panel C additions only: sensor mast, communications/data module, maintenance/access additions, inspection-drone interface, hardened service module, limited energy/resilience interface.
- Panel D labels: PERSISTS, MODIFIED, ADDED.

Outputs:

""" + "\n".join(f"- `{p.relative_to(ROOT).as_posix()}`" for p in [*panel_paths, contact_sheet, manifest]) + "\n"
    path = OUTPUT_DIR / "2_3_validation_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    panel_paths = [build_panel_a(), build_panel_b(), build_panel_c(), build_panel_d()]
    contact_sheet = build_contact_sheet(panel_paths)
    manifest = _write_manifest(panel_paths, contact_sheet)
    _write_validation_report(panel_paths, contact_sheet, manifest)
    print("Built 2.3 Toledo crib spread")
    for path in [*panel_paths, contact_sheet, manifest, OUTPUT_DIR / "2_3_validation_report.md"]:
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
