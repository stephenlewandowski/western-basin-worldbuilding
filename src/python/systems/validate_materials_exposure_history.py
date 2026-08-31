"""Validate Phase 2C materials, exposure, and remediation-history artifacts."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
from PIL import Image
import pyogrio


ROOT = Path(__file__).resolve().parents[3]
HISTORY = ROOT / "data" / "processed" / "history"
NETWORKS = ROOT / "data" / "processed" / "networks"
MAP_STEM = ROOT / "outputs" / "maps" / "systems" / "09_luckey_elmore_materials_exposure_history"
REPORT = ROOT / "reports" / "materials_exposure_history_artifact_check.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def date_floor(value: str) -> date:
    parts = [int(part) for part in value.split("-")]
    if len(parts) == 1:
        return date(parts[0], 1, 1)
    if len(parts) == 2:
        return date(parts[0], parts[1], 1)
    return date(*parts)


def date_ceiling(value: str) -> date:
    parts = [int(part) for part in value.split("-")]
    if len(parts) == 1:
        return date(parts[0], 12, 31)
    if len(parts) == 2:
        month = parts[1]
        next_month = date(parts[0] + (month == 12), month % 12 + 1, 1)
        return date.fromordinal(next_month.toordinal() - 1)
    return date(*parts)


def main() -> None:
    events = pd.read_csv(HISTORY / "materials_exposure_events.csv", keep_default_na=False)
    substances = pd.read_csv(HISTORY / "materials_exposure_substances.csv", keep_default_na=False)
    pathways = pd.read_csv(HISTORY / "materials_exposure_pathways.csv", keep_default_na=False)
    exposure_sources = pd.read_csv(HISTORY / "materials_exposure_sources.csv", keep_default_na=False)
    nodes = pd.read_csv(NETWORKS / "materials_system_nodes.csv", keep_default_na=False)
    edges = pd.read_csv(NETWORKS / "materials_system_edges.csv", keep_default_na=False)
    material_sources = pd.read_csv(NETWORKS / "materials_system_sources.csv", keep_default_na=False)

    event_schema = ["event_id", "site_id", "site_name", "start_date", "end_date", "date_precision", "event_type", "material", "activity", "role", "agency", "operator", "source_id", "confidence", "notes", "reality_status", "canon_status"]
    substance_schema = ["substance_id", "site_id", "material", "historical_role", "date_range", "source_id", "contamination_status", "medium", "confidence", "notes"]
    pathway_schema = ["pathway_id", "site_id", "period", "pathway", "evidence_class", "documented_human_exposure", "environmental_medium", "source_id", "confidence", "notes"]
    source_schema = ["source_id", "title", "agency_or_publisher", "publication_date", "URL_or_identifier", "retrieval_date", "source_type", "historical_period", "spatial_scale_if_applicable", "terms", "confidence", "notes"]
    require(list(events.columns) == event_schema, "event schema differs from contract")
    require(list(substances.columns) == substance_schema, "substance schema differs from contract")
    require(list(pathways.columns) == pathway_schema, "pathway schema differs from contract")
    require(list(exposure_sources.columns) == source_schema, "source schema differs from contract")
    require((len(events), len(substances), len(pathways), len(exposure_sources)) == (30, 9, 7, 13), "unexpected Phase 2C record count")
    for frame, key in [(events, "event_id"), (substances, "substance_id"), (pathways, "pathway_id"), (exposure_sources, "source_id")]:
        require(frame[key].is_unique, f"duplicate {key}")

    require(set(events.site_id) <= {"LUCKEY", "ELMORE", "PROGRAM"}, "unknown event site")
    require(set(events.date_precision) <= {"exact_date", "month", "year", "range", "approximate"}, "unknown date precision")
    for event in events.itertuples(index=False):
        require(date_floor(event.start_date) <= date_ceiling(event.end_date), f"reversed event date: {event.event_id}")
        if event.date_precision == "exact_date":
            require(len(event.start_date) == 10 and len(event.end_date) == 10, f"false exact-date precision: {event.event_id}")
        if event.date_precision == "month":
            require(len(event.start_date) == 7 and len(event.end_date) == 7, f"false month precision: {event.event_id}")
        if event.date_precision == "year":
            require(len(event.start_date) == 4 and len(event.end_date) == 4, f"false year precision: {event.event_id}")

    known_sources = set(exposure_sources.source_id) | set(material_sources.source_id)
    for frame in (events, substances, pathways, nodes, edges):
        require(set(frame.source_id) <= known_sources, "orphan source reference")
    required_events = {
        ("1942", "historical_production"), ("1949", "historical_production"),
        ("1957", "historical_production"), ("1992", "federal_designation"),
        ("2006", "regulatory_decision"), ("2008", "regulatory_decision"),
        ("2018-04-16", "excavation"), ("2025-09-15", "groundwater_monitoring"),
    }
    actual_events = set(zip(events.start_date, events.event_type))
    require(required_events <= actual_events, "required Luckey chronology event missing")
    require(events.loc[events.start_date == "2006", "activity"].str.contains("soil", case=False).any(), "2006 soil ROD missing")
    require(events.loc[events.start_date == "2008", "activity"].str.contains("groundwater", case=False).any(), "2008 groundwater ROD missing")
    planned = events[events.event_type == "planned_milestone"]
    planned_text = planned.activity + " " + planned.notes
    require(len(planned) == 2 and planned_text.str.contains("plan|planned", case=False).all(), "future cleanup milestones not clearly qualified")

    require(set(substances.site_id) <= {"LUCKEY", "ELMORE"}, "unknown substance site")
    require(not substances.material.str.contains("solvent", case=False).any(), "unsupported solvent claim")
    require(not substances.notes.str.contains("cancer|diagnos|illness caused", case=False, regex=True).any(), "unsupported health outcome")
    allowed_pathway_classes = {"potential_exposure_pathway", "documented_environmental_contamination", "documented_waste_logistics", "controlled_potential_pathway", "generalized_regulated_pathway"}
    require(set(pathways.evidence_class) <= allowed_pathway_classes, "unknown pathway evidence class")
    human = pathways.documented_human_exposure.astype(str).str.lower()
    require((human == "false").all(), "documented individual exposure claim entered")
    require(pathways.notes.str.len().gt(20).all(), "pathway qualification missing")

    require((len(nodes), len(edges), len(material_sources)) == (30, 31, 27), "extended graph count mismatch")
    new_node_ids = {"EXP-PATH-HIST-OCC", "EXP-LEG-ENV-CONTAM", "EXP-REM-FUSRAP", "EXP-IF-WASTE-LOGISTICS", "EXP-CTRL-MODERN"}
    new_edge_ids = {"EXP-E01", "EXP-E02", "EXP-E03", "EXP-E04", "EXP-E05"}
    require(new_node_ids <= set(nodes.node_id) and new_edge_ids <= set(edges.edge_id), "Phase 2C graph extension missing")
    require(not ((edges.from_id == "BER-LEG-LUCKEY") & (edges.to_id == "BER-PROC-ELMORE")).any(), "direct Luckey-to-Elmore flow prohibited")
    luckey = nodes[nodes.node_id == "BER-LEG-LUCKEY"].iloc[0]
    elmore = nodes[nodes.node_id == "BER-PROC-ELMORE"].iloc[0]
    require(luckey.supply_chain_role == "legacy_cleanup", "Luckey misclassified as current production")
    require(elmore.supply_chain_role == "advanced_processing" and str(elmore.local_resource).lower() == "false", "Elmore misclassified as extraction")

    map_checks = {}
    png = MAP_STEM.with_suffix(".png")
    svg = MAP_STEM.with_suffix(".svg")
    require(png.exists() and svg.exists(), "Map 09 PNG/SVG pair missing")
    with Image.open(png) as image:
        require(image.width >= 2800 and image.height >= 1700, "Map 09 raster too small")
        map_checks["png_pixels"] = [image.width, image.height]
    ET.parse(svg)
    map_checks["svg_parseable"] = True

    layers = set(pyogrio.list_layers(ROOT / "data" / "processed" / "glasspunk_base.gpkg")[:, 0])
    require(len(layers) == 16, "Phase 2C unexpectedly changed GeoPackage layer inventory")
    prohibited_names = [p.as_posix() for p in ROOT.rglob("*") if p.is_file() and ("exposure_radius" in p.name.lower() or "groundwater_plume" in p.name.lower() or ("materials_corridor" in p.name.lower() and p.suffix.lower() in {".gpkg", ".geojson", ".shp"}))]
    require(not prohibited_names, f"prohibited Phase 2C artifact found: {prohibited_names}")

    result = {
        "status": "pass",
        "phase": "Phase 2C - strategic materials, exposure and remediation history",
        "counts": {"events": len(events), "substances": len(substances), "pathways": len(pathways), "exposure_sources": len(exposure_sources), "nodes": len(nodes), "edges": len(edges), "material_sources": len(material_sources), "gpkg_layers": len(layers)},
        "exposure_findings": {"documented_individual_exposure_count": int((human == "true").sum()), "qualified_pathway_count": len(pathways)},
        "map_09": map_checks,
        "constraints": {"luckey_legacy_only": True, "elmore_nonextractive": True, "no_direct_luckey_elmore_flow": True, "no_plume_or_radius": True, "future_scenarios_separate": True, "no_corridor_geometry": True},
    }
    REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
