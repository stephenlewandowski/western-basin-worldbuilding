"""Validate the review-only Great Black Swamp QA package."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import geopandas as gpd
import yaml


ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports"
QA = ROOT / "outputs" / "qa"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    candidate_path = QA / "data" / "great_black_swamp_candidate_gordon1966.geojson"
    mosaic_path = QA / "data" / "great_black_swamp_candidate_gordon1966_mosaic.geojson"
    candidate = gpd.read_file(candidate_path)
    mosaic = gpd.read_file(mosaic_path)
    qa = json.loads((REPORTS / "great_black_swamp_geometry_qa.json").read_text(encoding="utf-8"))
    sources = yaml.safe_load((ROOT / "metadata" / "sources.yml").read_text(encoding="utf-8"))

    require(len(candidate) == 1, "candidate must contain exactly one review feature")
    require(len(mosaic) == 117, "source mosaic feature count changed")
    require(candidate.geometry.is_valid.all(), "candidate geometry is invalid")
    require(not candidate.geometry.is_empty.any(), "candidate geometry is empty")
    require(candidate.crs is not None and candidate.crs.to_epsg() == 4326, "candidate CRS must be EPSG:4326")
    require(
        candidate.iloc[0]["geometry_id"] == "great_black_swamp_candidate_gordon1966",
        "candidate identifier is incorrect",
    )
    require(
        candidate.iloc[0]["canonical_status"] == "review_only_not_canonical",
        "candidate must remain non-canonical",
    )
    require(str(candidate.iloc[0]["human_review_status"]).startswith("HOLD"), "human stop gate missing")
    require(4_600 < float(qa["candidate_area_km2"]) < 4_800, "candidate area outside recorded QA band")
    require(qa["candidate_component_count"] == 116, "component count changed")
    require(qa["candidate_valid"] is True, "QA record does not confirm validity")
    require(
        qa["prohibited_operations_confirmed_absent"]
        == ["image tracing", "georeferencing", "buffer", "smoothing", "hand edit"],
        "prohibited-operation audit changed",
    )
    require((QA / "great_black_swamp_geometry_review.png").stat().st_size > 100_000, "PNG missing/too small")
    require((QA / "great_black_swamp_geometry_review.svg").stat().st_size > 100_000, "SVG missing/too small")
    require(
        "odnr_original_natural_vegetation_3135" in sources["sources"],
        "ODNR source register entry missing",
    )
    require(
        not (ROOT / "data" / "processed" / "great_black_swamp_candidate_gordon1966.geojson").exists(),
        "candidate must not be promoted to processed canonical data",
    )

    class_rows = list(
        csv.DictReader((REPORTS / "great_black_swamp_class_review.csv").open(encoding="utf-8"))
    )
    require(len(class_rows) == 13, "class review must include all 13 vegetation codes")
    included = [row for row in class_rows if row["candidate_gbs_component"] == "yes"]
    require(
        len(included) == 1 and included[0]["vegetation_code"] == "4",
        "only vegetation class 4 may be included",
    )

    required_report_headings = [
        "## Executive Finding",
        "## Candidate Sources",
        "## Preferred Source",
        "## Source Authority",
        "## Historical Reference Period",
        "## Original Scale",
        "## Digital Provenance",
        "## Vegetation-Class Selection",
        "## Derivation Method",
        "## Comparison With Official Great Black Swamp Maps",
        "## Interstate Compatibility",
        "## Area / Geometry QA",
        "## Uncertainty",
        "## Permitted Uses",
        "## Uses Not Supported",
        "## Terms / Licensing / Disclaimer",
        "## Recommendation",
        "## Human Review Decision",
    ]
    report = (REPORTS / "great_black_swamp_geometry_source_review.md").read_text(encoding="utf-8")
    for heading in required_report_headings:
        require(heading in report, f"missing report heading: {heading}")

    print("Great Black Swamp review validation: PASS")
    print("Canonical Phase 1 GeoPackage is not written or promoted by this QA package.")


if __name__ == "__main__":
    main()
