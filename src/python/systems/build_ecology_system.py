"""Build the bounded factual Phase 6A ecology and biodiversity baseline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"
NODES = NETWORKS / "ecology_system_nodes.csv"
EDGES = NETWORKS / "ecology_system_edges.csv"
INDICATORS = ANALYSIS / "ecological_indicators_2026.csv"
MAP_BASE = MAPS / "20_ecological_system_2026"
MANIFEST = REPORTS / "ecology_system_manifest.json"

NODE_COLUMNS = ["node_id", "name", "ecological_component", "node_type", "habitat_class", "taxonomic_relevance", "status", "latitude", "longitude", "spatial_role", "source_id", "confidence", "notes"]
EDGE_COLUMNS = ["edge_id", "from_id", "to_id", "relationship_type", "ecological_function", "relationship_basis", "source_id", "confidence", "notes"]
INDICATOR_COLUMNS = ["indicator_id", "ecological_system", "taxonomic_group", "indicator_type", "metric", "value", "units", "year_or_period", "spatial_scope", "source_id", "confidence", "notes"]

NODE_ROWS = [
    ["ECO-001", "Western Lake Erie aquatic system", "western_lake_erie_aquatic", "aquatic_system", "open water / nearshore", "fish; plankton; benthos", "real_2026", "", "", "regional system", "usgs_nhdplus_hr", "high", "Broad aquatic system; not a fisheries stock-assessment unit."],
    ["ECO-002", "Maumee Bay receiving-water interface", "western_lake_erie_aquatic", "aquatic_system", "bay / nearshore", "fish; waterbirds; plankton", "real_2026", "", "", "regional interface", "usgs_nhdplus_hr", "high", "Lake-to-river receiving-water interface; no current bloom footprint asserted."],
    ["ECO-003", "Maumee River corridor", "maumee_tributary_floodplain", "river_system", "river / riparian", "fish; riparian vegetation; waterbirds", "real_2026", "", "", "regional corridor", "usgs_3dhp_all", "high", "Physical hydrography structure reused from the accepted current-development layer."],
    ["ECO-004", "Maumee tributary and floodplain network", "maumee_tributary_floodplain", "river_system", "tributary / floodplain", "fish; amphibians; riparian vegetation", "real_2026", "", "", "regional network", "usgs_3dhp_all", "high", "Generalized tributary/floodplain interface; no straight-line animal route is implied."],
    ["ECO-005", "Western Lake Erie coastal wetland complex", "coastal_wetlands_marshes", "wetland_complex", "freshwater emergent / shrub / forested wetland", "waterfowl; shorebirds; wetland vegetation", "real_2026", "", "", "regional complex", "usfws_nwi", "high", "Generalized complex based on contemporary NWI features; inventory is not a jurisdictional determination."],
    ["ECO-006", "Ottawa National Wildlife Refuge", "coastal_wetlands_marshes", "protected_area", "coastal marsh / wetland", "migratory birds; wetland fauna", "real_2026", "41.63", "-83.14", "generalized public anchor", "phase6a_usfws_ottawa_nwr", "high", "Generalized public anchor only; sensitive species occurrence locations are not published."],
    ["ECO-007", "Maumee Bay State Park and coastal restoration context", "coastal_wetlands_marshes", "restoration_area", "coastal wetland / shoreline", "waterbirds; fish nursery function", "real_2026", "41.69", "-83.22", "generalized public anchor", "phase6a_usfws_ottawa_nwr", "low", "Broad coastal-restoration context; exact project boundaries are not modeled in this skeleton."],
    ["ECO-008", "Contemporary NWI wetland network", "coastal_wetlands_marshes", "wetland_complex", "freshwater wetland", "wetland vegetation; amphibians; birds", "real_2026", "", "", "inventory network", "usfws_nwi", "high", "Uses existing generalized NWI features at the established 25-acre focus threshold."],
    ["ECO-009", "Black Swamp legacy agricultural matrix", "black_swamp_legacy_agriculture", "agricultural_matrix", "agriculture / drainage-altered landscape", "soil biota; farmland birds; pollinators", "real_2026", "", "", "landscape context", "h2ohio_great_black_swamp_history", "moderate", "Historical ecological legacy and modern matrix context; Great Black Swamp geometry remains noncanonical and no polygon is used."],
    ["ECO-010", "Contemporary terrestrial habitat mosaic", "terrestrial_habitat_fragmentation", "terrestrial_habitat", "forest / grassland / agriculture / developed", "terrestrial wildlife; vegetation; pollinators", "real_2026", "", "", "regional class context", "phase6a_mrlc_land_cover", "moderate", "Generalized contemporary land-cover classes; no large raster is committed."],
    ["ECO-011", "Riparian and floodplain habitat interface", "terrestrial_habitat_fragmentation", "terrestrial_habitat", "riparian / floodplain", "riparian vegetation; fish; amphibians", "real_2026", "", "", "ecological interface", "usgs_3dhp_all", "moderate", "Riparian function is represented conceptually along mapped water structure."],
    ["ECO-012", "Urban / industrial ecological interface", "terrestrial_habitat_fragmentation", "urban_interface", "urban / industrial edge", "general terrestrial and aquatic interface", "real_2026", "", "", "regional interface", "census_tigerweb_context", "moderate", "Broad interface only; proximity is not treated as proof of ecological harm."],
    ["ECO-013", "Western Lake Erie migratory-bird stopover function", "migratory_mobile_species", "migration_interface", "coastal wetland / shoreline mosaic", "waterfowl; shorebirds; migratory songbirds", "real_2026", "", "", "functional network", "phase6a_usfws_ottawa_nwr", "moderate", "Generalized migratory function across wetland and shoreline systems; no exact flight path."],
    ["ECO-014", "Lake Erie–tributary fish movement function", "migratory_mobile_species", "migration_interface", "aquatic / river connection", "walleye; yellow perch; fish assemblages", "real_2026", "", "", "functional network", "phase6a_glfc_lake_erie_committee", "moderate", "Broad lake-to-tributary movement function; no stock-size or passage model."],
    ["ECO-015", "Terrestrial pollinator habitat function", "migratory_mobile_species", "migration_interface", "grassland / wetland edge / riparian", "pollinators; flowering plants", "real_2026", "", "", "functional network", "phase6a_mrlc_land_cover", "low", "Broad habitat function only; no species inventory or insect movement route."],
    ["ECO-016", "Nutrient and HAB ecological condition", "western_lake_erie_aquatic", "aquatic_system", "water-quality condition", "cyanobacteria; fish; plankton", "real_2026", "", "", "condition interface", "noaa_hab", "high", "Ecological condition context; no causal attribution or vulnerability calculation."],
]

EDGE_ROWS = [
    ["ECE-001", "ECO-003", "ECO-002", "hydrologically_connected", "river-to-bay exchange", "documented_hydrography", "usgs_nhdplus_hr", "high", "Mapped water structure; ecological exchange is generalized."],
    ["ECE-002", "ECO-002", "ECO-001", "hydrologically_connected", "bay-to-lake connection", "documented_hydrography", "usgs_nhdplus_hr", "high", "Receiving-water connection, not an animal travel route."],
    ["ECE-003", "ECO-004", "ECO-003", "habitat_connected", "tributary-river habitat structure", "documented_hydrography", "usgs_3dhp_all", "moderate", "Physical network supports a broad ecological interface."],
    ["ECE-004", "ECO-003", "ECO-011", "riparian_connection", "river-riparian edge function", "scientific_inference", "usgs_3dhp_all", "moderate", "Generalized riparian relationship; no parcel habitat claim."],
    ["ECE-005", "ECO-004", "ECO-008", "wetland_interface", "tributary-wetland hydrologic interface", "scientific_inference", "usfws_nwi", "moderate", "NWI and hydrography overlap supports an interface, not performance."],
    ["ECE-006", "ECO-005", "ECO-006", "habitat_connected", "coastal wetland complex", "documented_protected_area", "phase6a_usfws_ottawa_nwr", "moderate", "Generalized refuge-to-coastal-wetland relationship."],
    ["ECE-007", "ECO-005", "ECO-007", "restoration_link", "coastal wetland restoration context", "documented_public_context", "phase6a_usfws_ottawa_nwr", "low", "Restoration context is broad and not a project-boundary assertion."],
    ["ECE-008", "ECO-009", "ECO-008", "wetland_interface", "drainage-altered agricultural matrix and wetland remnants", "historical_context_plus_inventory", "h2ohio_great_black_swamp_history", "moderate", "Modern legacy context; no historical boundary is mapped."],
    ["ECE-009", "ECO-009", "ECO-010", "terrestrial_interface", "agricultural-terrestrial habitat mosaic", "generalized_land_cover", "phase6a_mrlc_land_cover", "moderate", "Broad land-cover relationship; no habitat-quality score."],
    ["ECE-010", "ECO-010", "ECO-011", "habitat_connected", "terrestrial-riparian interface", "scientific_inference", "usgs_3dhp_all", "moderate", "Generalized interface without inferred movement path."],
    ["ECE-011", "ECO-012", "ECO-010", "fragmented_by", "developed-edge fragmentation context", "generalized_land_cover", "phase6a_mrlc_land_cover", "low", "Broad pressure context only; no causal or vulnerability claim."],
    ["ECE-012", "ECO-013", "ECO-005", "migration_link", "coastal stopover function", "documented_ecological_function", "phase6a_usfws_ottawa_nwr", "moderate", "Functional link, not an exact route or occurrence map."],
    ["ECE-013", "ECO-013", "ECO-006", "migration_link", "protected coastal stopover context", "documented_protected_area", "phase6a_usfws_ottawa_nwr", "moderate", "Generalized public refuge function."],
    ["ECE-014", "ECO-014", "ECO-001", "migration_link", "fish lake habitat function", "documented_fishery_context", "phase6a_glfc_lake_erie_committee", "moderate", "No stock size, route, or passage probability."],
    ["ECE-015", "ECO-014", "ECO-003", "spawning_connection", "fish lake-tributary connection", "documented_fishery_context", "phase6a_glfc_lake_erie_committee", "low", "Broad ecological function; species-specific spawning sites are not exposed."],
    ["ECE-016", "ECO-015", "ECO-010", "habitat_connected", "pollinator habitat mosaic", "generalized_land_cover", "phase6a_mrlc_land_cover", "low", "No insect inventory or movement corridor is asserted."],
    ["ECE-017", "ECO-016", "ECO-002", "ecological_condition_interface", "HAB condition at bay interface", "documented_monitoring_science", "noaa_hab", "high", "Condition relationship only; no impact or vulnerability calculation."],
    ["ECE-018", "ECO-016", "ECO-001", "ecological_condition_interface", "HAB condition in western lake", "documented_monitoring_science", "noaa_hab", "high", "No current bloom footprint or numerical stock measure."],
    ["ECE-019", "ECO-003", "ECO-016", "nutrient_condition_interface", "tributary nutrient-to-lake ecological condition context", "documented_water_quality_context", "epa_lake_erie", "moderate", "No unsupported causal load or effect size."],
    ["ECE-020", "ECO-008", "ECO-013", "migration_link", "wetland network and migratory function", "documented_ecological_function", "phase6a_usfws_ottawa_nwr", "moderate", "Generalized habitat function; no sensitive locations."],
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_map() -> None:
    plt.rcParams["svg.fonttype"] = "none"
    huc8 = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    lake = gpd.read_file(GPKG, layer="water_lake_erie")
    wetlands = gpd.read_file(GPKG, layer="water_current_wetlands_25ac")
    flowlines = gpd.read_file(GPKG, layer="hydrography_physical")
    flowlines["geometry"] = flowlines.geometry.simplify(0.002, preserve_topology=False)
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    ax = fig.add_axes([0.045, 0.16, 0.58, 0.76], facecolor="#e9e1ce")
    huc8.boundary.plot(ax=ax, color="#9f967f", linewidth=0.45, alpha=0.65)
    lake.plot(ax=ax, color="#a9d7df", edgecolor="#478c9a", linewidth=0.8, alpha=0.9)
    wetlands.plot(ax=ax, color="#6da77c", edgecolor="none", alpha=0.45)
    flowlines.plot(ax=ax, color="#4a8798", linewidth=0.3, alpha=0.55)
    anchors = pd.DataFrame({"name": ["Ottawa NWR", "Maumee Bay State Park"], "longitude": [-83.14, -83.22], "latitude": [41.63, 41.69]})
    ax.scatter(anchors.longitude, anchors.latitude, s=55, c="#7b4f92", marker="^", edgecolor="#f1eadc", linewidth=0.8, zorder=5)
    ax.text(-83.14, 41.615, "Ottawa NWR", fontsize=8, color="#4d2e60", ha="center")
    ax.text(-83.22, 41.72, "Maumee Bay State Park", fontsize=8, color="#4d2e60", ha="center")
    ax.text(-83.42, 41.72, "Western Lake Erie", fontsize=11, weight="bold", color="#235a68", ha="center")
    ax.text(-83.56, 41.47, "Maumee River / tributary structure", fontsize=9, color="#285f71", rotation=18, ha="center")
    ax.set_xlim(-84.55, -82.55)
    ax.set_ylim(40.9, 42.15)
    ax.set_axis_off()
    side = fig.add_axes([0.665, 0.08, 0.30, 0.84]); side.axis("off")
    side.text(0.04, 0.98, "MAP 20 — WESTERN BASIN\nECOLOGICAL SYSTEM, 2026", va="top", fontsize=15, weight="bold", color="#17384b")
    side.text(0.04, 0.875, "Factual ecological-system skeleton over accepted water and hydrography baselines. Broad functions are not exact animal travel routes.", va="top", fontsize=8.5, color="#3f4645", linespacing=1.3)
    side.text(0.04, 0.76, "ECOLOGICAL STRUCTURE", fontsize=10, weight="bold", color="#17384b")
    bullets = [
        "Western Lake Erie aquatic and HAB-condition interfaces",
        "Maumee River, tributary, riparian, and floodplain structure",
        "Coastal wetlands, Ottawa refuge, and restoration context",
        "Modern drainage-altered agricultural matrix; historic Black Swamp remains noncanonical",
        "Terrestrial habitat mosaic and broad fragmentation context",
        "Migratory-bird, fish-movement, and pollinator functions",
    ]
    y = 0.725
    for b in bullets:
        side.text(0.06, y, "• " + b, fontsize=8.1, color="#3f4645", va="top", wrap=True); y -= 0.047
    side.text(0.04, 0.40, "MAP LEGEND", fontsize=10, weight="bold", color="#17384b")
    legend = [
        Patch(facecolor="#a9d7df", edgecolor="#478c9a", label="Aquatic system"),
        Line2D([0], [0], color="#4a8798", lw=2, label="River / hydrography structure"),
        Patch(facecolor="#6da77c", alpha=0.6, label="Coastal / contemporary wetland"),
        Patch(facecolor="#d6b37b", label="Agricultural matrix context"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#7b4f92", markersize=8, label="Protected / restoration anchor"),
    ]
    side.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.04, 0.38), frameon=False, fontsize=8)
    side.text(0.04, 0.22, "BOUNDARIES", fontsize=10, weight="bold", color="#17384b")
    side.text(0.04, 0.19, "No sensitive species locations, abundance estimates, richness estimates, exact migration routes, ecological-risk score, causation claim, or future ecological scenario is modeled. The Great Black Swamp candidate remains C — HOLD / noncanonical.", fontsize=7.5, color="#3f4645", va="top", linespacing=1.3)
    fig.savefig(MAP_BASE.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg = MAP_BASE.with_suffix(".svg")
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    NETWORKS.mkdir(parents=True, exist_ok=True); ANALYSIS.mkdir(parents=True, exist_ok=True); MAPS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(NODE_ROWS, columns=NODE_COLUMNS).to_csv(NODES, index=False)
    pd.DataFrame(EDGE_ROWS, columns=EDGE_COLUMNS).to_csv(EDGES, index=False)
    indicators = [
        ["ECOI-001", "coastal_wetlands_marshes", "wetland_inventory", "inventory_feature_count", "NWI generalized wetland features", 608, "features", "2026 inventory", "established Western Basin focus window", "usfws_nwi", "high", "Inventory count, not total wetland area or habitat quality."],
        ["ECOI-002", "maumee_tributary_floodplain", "aquatic_hydrography", "inventory_feature_count", "physical Lower Maumee flowlines", 864, "features", "2026 baseline", "Lower Maumee stream-order focus", "usgs_nhdplus_hr", "high", "Existing Phase 1 count; not a fish-passage or movement count."],
        ["ECOI-003", "western_basin_watershed", "all", "inventory_unit_count", "contributing HUC-8 watersheds", 7, "watersheds", "2026 baseline", "Maumee basin", "usgs_wbd", "high", "Hydrologic units provide context, not biodiversity richness."],
    ]
    pd.DataFrame(indicators, columns=INDICATOR_COLUMNS).to_csv(INDICATORS, index=False)
    render_map()
    artifacts = [NODES, EDGES, INDICATORS, MAP_BASE.with_suffix(".png"), MAP_BASE.with_suffix(".svg")]
    manifest = {"phase": "6A", "generated": "2026-09-02", "status": "ecology_baseline", "counts": {"nodes": len(NODE_ROWS), "edges": len(EDGE_ROWS), "indicators": len(indicators)}, "artifacts": {str(p.relative_to(ROOT)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
