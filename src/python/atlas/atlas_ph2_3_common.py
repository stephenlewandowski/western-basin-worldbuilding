"""Shared constants for Phase 17A Prototype 2.3 "Toledo Water Intake Crib".

Additive Phase-17 Atlas support. This module reads accepted/frozen reference
and documentation inputs only and never writes to them. It is shared by the
Python builder and validator so the accepted coordinate table, epistemic-status
vocabulary, and cultural-color mapping live in one place.

Scientific contract (from the Phase 17A brief, section 14.2):
    The Toledo Water Works Intake Crib is a real offshore utility landmark
    embedded in a larger drinking-water and monitoring system. Future adaptation
    may be explored, but present infrastructure, nearby monitoring assets,
    system interpretation, and 2075 design remain visibly distinct.

Photograph-derived geometry is treated as approximate / inferred only. No
measured dimension is invented. The 2075 retrofit is an accumulated-future
sketch (S/K) layered onto the recognizable existing structure; it is never
presented as evidence or as a replacement.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# ---- Project paths ---------------------------------------------------------
REPORTS = ROOT / "reports"
ASSETS_REF = ROOT / "assets" / "reference"
OUT_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "2_3_toledo_crib"

REFERENCE_IMAGE = ASSETS_REF / "toledo_water_intake_crib.jpg"
REFERENCE_MD = ASSETS_REF / "toledo_water_intake_crib.md"
COORD_REPORT = REPORTS / "toledo_water_intake_crib_coordinate_resolution.md"
CANON_STATUS = ROOT / "docs" / "canon_status.md"
PHASE_BRIEF = ROOT / "docs" / "phase_briefs" / "phase17a_atlas_architecture.md"

MANIFEST = OUT_DIR / "2_3_source_manifest.json"
VALIDATION_REPORT = OUT_DIR / "2_3_validation_report.md"

# ---- Accepted physical-asset coordinate ------------------------------------
# Primary authority: U.S. Coast Guard Light List No. 6025 (verified / resolved).
PHYSICAL_CRIB = (41.699444, -83.259167)  # (lat, lon) — canonical physical asset
PHYSICAL_CRIB_DMS = "41°41′58.000″ N, 83°15′33.000″ W"

# Legacy dataset coordinate (GLOS/ERDDAP `glos_crib`). Separate entity; MUST NOT
# be used as physical crib geometry. Kept here so builder + validator share it.
LEGACY_GLOS_CRIB = (41.674960, -83.307900)  # (lat, lon)

# Nearby monitoring / observation coordinates (separate from the physical crib).
# From reports/toledo_water_intake_crib_coordinate_resolution.md table.
MONITORING_POINTS = [
    {"id": "TWCO1", "name": "NOAA/NDBC TWCO1", "lat": 41.699444, "lon": -83.258611, "dist_m": 46},
    {"id": "6025.5", "name": "Limno Toledo / USCG 6025.5", "lat": 41.701278, "lon": -83.256139, "dist_m": 324},
    {"id": "GLOS45165", "name": "GLOS 45165 (buoy)", "lat": 41.702033, "lon": -83.261450, "dist_m": 345},
    {"id": "6025.1", "name": "Limno Tech buoy A / USCG 6025.1", "lat": 41.703642, "lon": -83.264008, "dist_m": 616},
]

# ----

# ---- Epistemic / representation vocabulary (Visual Grammar v0.3) -----------
# Status vocab: E Evidence/Model, S Scenario, C World Canon, K Sketch.
# Representation descriptors: PHOTO / MAP / FIGURE / SCHEMATIC / 3D / CONCEPT.
# Status is separate from relationship semantics. Status is separate from the
# accumulated-future persistence treatment (PERSISTS / MODIFIED / ADDED).

# ---- Visual-grammar palette (Phase 17A v0.3; not frozen final style) -------
PAPER = "#F4F1E8"        # sheet background
PANEL = "#FBFAF6"        # panel card fill
BORDER = "#A7A39A"       # panel / neutral border
INK = "#1F2428"          # primary dark ink
MUTED = "#667078"        # context / secondary text
LEADER = "#A3A7A9"       # neutral annotation pointer

# Epistemic-status badge colors (status vocabulary).
E = "#355F7A"            # Evidence / Model
S = "#A87536"            # Scenario
K = "#776486"            # Sketch
C = "#4E756A"            # World Canon

# Relationship semantics.
WATER = "#3C6E8F"        # physical / material flow
WATER_LIGHT = "#B9DDEB"  # water fill
INFO = "#806B8E"         # information / signal flow (dashed)
DEPEND = INK             # dependency / requirement
TEMPORAL = "#B07A37"     # temporal sequence

# Existing-asset material colors (recognizable crib character).
CONCRETE_BASE = "#B9B4A9"   # weathered concrete body / crib
CONCRETE_UPPER = "#C9C3B6"  # lighter upper service structure
CONCRETE_DARK = "#8E8A80"   # shadowed / darker massing
STEEL = "#66707A"           # structural steel
RED_METAL = "#A8473C"       # red railing / metalwork character
EQUIP = "#3A3F45"           # roof nav/monitoring equipment massing

# Accumulated-future persistence treatment (Visual Grammar v0.3 section 4).
PERSISTS = INK             # original existing structure (retained)
MODIFIED = "#A87536"       # existing element changed / upgraded (S/K, scenario tone)
ADDED = "#607A5A"          # new element added by 2075 (S/K, sketch/scenario tone)
ADDED_FILL = "#8FB5A9"


# ---- Technology grammar (system need -> function -> interface -> device) ---
# 2075 retrofit families, each tied to a system need and a function. Used for
# the 2.3C callout legend and naming; devices stay intentionally simple and are
# explicitly S/K. Function comes first; gadget last.
RETROFIT_FAMILIES = [
    {
        "key": "sensing",
        "label": "Environmental sensing",
        "need": "know basin & intake conditions",
        "function": "measure water / weather / HAB-risk indicators",
        "devices": ["sensor mast", "instrument cluster"],
    },
    {
        "key": "comms",
        "label": "Communications / data",
        "need": "return data & commands reliably",
        "function": "relay telemetry to shore operations",
        "devices": ["antenna", "radome", "data cabinet"],
    },
    {
        "key": "access",
        "label": "Modular maintenance access",
        "need": "safe, repeatable service visits",
        "function": "get crew and tools on/off the crib",
        "devices": ["service platform ring", "davit / hoist", "shore-mooring landing"],
    },
    {
        "key": "hardened",
        "label": "Replaceable / hardened exterior",
        "need": "survive storms, ice, weathering",
        "function": "shield critical skin & recover failed panels",
        "devices": ["armor cladding band", "replaceable railing segment"],
    },
    {
        "key": "wq",
        "label": "Water-quality / treatment-support",
        "need": "protect intake & inform treatment",
        "function": "sample and trend source water at the intake",
        "devices": ["sample riser / port"],
    },
    {
        "key": "inspection",
        "label": "Autonomous inspection support",
        "need": "inspect hard-to-reach structure",
        "function": "augment crewed inspection, not replace it",
        "devices": ["inspection drone dock", "crawler ring"],
    },
    {
        "key": "energy",
        "label": "Energy / resilience interfaces",
        "need": "secure localized power & resilience",
        "function": "supply low-power monitoring and backup loads",
        "devices": ["PV canopy / array", "battery cabinet"],
    },
]

RETROFIT_KEYS = [f["key"] for f in RETROFIT_FAMILIES]


# ---- Geographic locator window (2.3A) --------------------------------------
# A tight western-basin window covering the physical crib (lon -83.259), nearby
# monitoring points (~46-616 m), and the legacy GLOS point (~4.88 km away) so the
# physical-vs-legacy separation is visually explicit.
LOCATOR_WINDOW = (-83.36, 41.63, -83.21, 41.73)  # (lon_min, lat_min, lon_max, lat_max)
LAKE_LAYER = "water_lake_erie"


# ---- Output stems ----------------------------------------------------------
PANEL_STEMS = [
    "2_3a_existing_asset",
    "2_3b_current_structure",
    "2_3c_2075_retrofit",
    "2_3d_persistence",
]
CONTACT_SHEET = OUT_DIR / "2_3_contact_sheet.png"
