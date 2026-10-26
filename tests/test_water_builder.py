"""Regression checks for safe, provenance-aware water-builder reruns.

Set WATER_BUILDER_TEST_GPKG to a current, hydrated project GeoPackage to run
the larger preservation check. Every test writes only to a temporary directory.
"""

from __future__ import annotations

import hashlib
from contextlib import closing
from datetime import date
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python" / "systems"))

try:
    import geopandas as gpd
    import pyogrio
    from shapely.geometry import Point
    import build_water_system as builder
    import water_source_provenance as provenance
except ImportError as exc:
    GIS_IMPORT_ERROR = str(exc)
else:
    GIS_IMPORT_ERROR = None


WATER_LAYERS = {
    "water_watersheds_huc8", "water_subwatersheds_huc12", "water_flowlines_order3",
    "water_huc12_routing_inferred", "water_lake_erie", "water_current_wetlands_25ac",
    "water_verified_facilities",
}


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _table_fingerprints(path: Path, names: set[str]) -> dict[str, str]:
    """Compare every value, including geometry blobs, in the preserved layers."""
    result = {}
    with closing(sqlite3.connect(path)) as db:
        for name in sorted(names):
            quoted = '"' + name.replace('"', '""') + '"'
            digest = hashlib.sha256()
            for row in db.execute(f"SELECT * FROM {quoted} ORDER BY rowid"):
                for value in row:
                    data = value if isinstance(value, bytes) else repr(value).encode("utf-8")
                    digest.update(len(data).to_bytes(8, "big"))
                    digest.update(data)
            result[name] = digest.hexdigest()
    return result


@unittest.skipIf(GIS_IMPORT_ERROR is not None, f"water builder GIS dependencies unavailable: {GIS_IMPORT_ERROR}")
class WaterBuilderGeoPackageTest(unittest.TestCase):
    def setUp(self) -> None:
        scratch_parent = ROOT / "temp"
        scratch_parent.mkdir(exist_ok=True)
        self.scratch = tempfile.TemporaryDirectory(prefix="water-builder-test-", dir=scratch_parent)
        self.root = Path(self.scratch.name)
        self.addCleanup(self.scratch.cleanup)
        self.frame = gpd.GeoDataFrame({"name": ["new water"]}, geometry=[Point(-83.4, 41.6)], crs="EPSG:4326")
        self.layers = {name: self.frame.copy() for name in ("huc8", "huc12", "flow", "connectors", "lake", "wetlands")}

    def make_source(self) -> Path:
        source = self.root / "source.gpkg"
        original = gpd.GeoDataFrame({"name": ["preserve"]}, geometry=[Point(-84, 41)], crs="EPSG:4326")
        original.to_file(source, layer="unrelated_hydrography", driver="GPKG", index=False)
        original.to_file(source, layer="water_flowlines_order3", driver="GPKG", index=False)
        return source

    def test_preserves_unrelated_layer_and_replaces_water_layers(self) -> None:
        source = self.make_source()
        before_source = _digest(source)
        before = _table_fingerprints(source, {"unrelated_hydrography"})
        output = self.root / "rebuilt.gpkg"
        builder.write_gpkg(self.layers, self.frame, source_gpkg=source, output_gpkg=output)
        self.assertEqual(before_source, _digest(source))
        self.assertEqual(before, _table_fingerprints(output, {"unrelated_hydrography"}))
        self.assertEqual(WATER_LAYERS | {"unrelated_hydrography"}, set(pyogrio.list_layers(output)[:, 0]))
        self.assertEqual(["new water"], pyogrio.read_dataframe(output, layer="water_flowlines_order3")["name"].tolist())

    def test_failure_does_not_partially_replace_existing_output(self) -> None:
        source = self.make_source()
        output = self.root / "rebuilt.gpkg"
        shutil.copy2(source, output)
        before = _digest(output)
        calls = 0
        write_file = gpd.GeoDataFrame.to_file

        def fail_on_second_layer(frame, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("injected write failure")
            return write_file(frame, *args, **kwargs)

        with patch.object(gpd.GeoDataFrame, "to_file", new=fail_on_second_layer):
            with self.assertRaisesRegex(RuntimeError, "injected write failure"):
                builder.write_gpkg(self.layers, self.frame, source_gpkg=source, output_gpkg=output)
        self.assertEqual(2, calls)
        self.assertEqual(before, _digest(output))
        self.assertFalse(list(self.root.glob(".water-build-*.gpkg")))

    def test_refuses_to_replace_the_source_geopackage(self) -> None:
        source = self.make_source()
        before = _digest(source)
        with self.assertRaises(ValueError):
            builder.write_gpkg(self.layers, self.frame, source_gpkg=source, output_gpkg=source)
        self.assertEqual(before, _digest(source))

    def test_output_root_rejects_protected_and_nonempty_directories(self) -> None:
        occupied = self.root / "occupied"
        occupied.mkdir()
        marker = occupied / "keep.txt"
        marker.write_text("existing work", encoding="utf-8")
        for destination in (ROOT, ROOT / "data", occupied):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                builder.configure_output_root(destination)
        self.assertEqual("existing work", marker.read_text(encoding="utf-8"))

    def test_download_then_cached_rebuild_preserves_retrieval_date(self) -> None:
        raw = self.root / "source-raw"
        output = self.root / "output-raw"
        cache = raw / "usgs" / "test.geojson"
        url = "https://example.invalid/flowlines/query"
        kwargs = {"where": "1=1", "out_fields": "name", "cache": cache}
        response = Mock()
        response.json.return_value = {"features": self.frame.__geo_interface__["features"]}
        fake_date = Mock(wraps=date)
        fake_date.today.return_value = date(2020, 5, 17)
        with patch.object(builder, "RAW", raw), patch.object(builder, "OUTPUT_RAW", output), \
             patch.object(builder, "SOURCE_PROVENANCE", {}), patch.object(builder, "BUILD_DATE", "2035-01-02"), \
             patch.object(provenance, "date", fake_date), patch.object(builder.requests, "get", return_value=response) as get:
            first = builder.arcgis_geojson(url, **kwargs)
            self.assertEqual(1, get.call_count)
            entry = builder.SOURCE_PROVENANCE[url]
            self.assertEqual("2020-05-17", entry["retrieved_date"])
            self.assertEqual("recorded_retrieval", entry["status"])
            saved = output / "usgs" / "test.geojson"
            self.assertEqual(_digest(saved), entry["sha256"])
            first_hash = _digest(saved)
            fake_date.today.return_value = date(2035, 1, 2)
            second = builder.arcgis_geojson(url, **kwargs)
            self.assertEqual(1, get.call_count)
            self.assertEqual(first_hash, _digest(saved))
            self.assertEqual("2020-05-17", builder.SOURCE_PROVENANCE[url]["retrieved_date"])
            tagged = builder.add_common(second, prefix="TEST-", name_col="name", feature_type="test",
                                        source_name="test", source_url=url,
                                        retrieved_date=builder.SOURCE_PROVENANCE[url]["retrieved_date"])
            self.assertEqual(["2020-05-17"], tagged["retrieved_date"].tolist())
            self.assertEqual(first["name"].tolist(), second["name"].tolist())

    def test_undated_custom_cache_remains_unknown_without_fetch(self) -> None:
        raw = self.root / "source-raw"
        cache = raw / "usgs" / "custom.geojson"
        cache.parent.mkdir(parents=True)
        self.frame.to_file(cache, driver="GeoJSON", index=False)
        before = _digest(cache)
        with patch.object(builder, "RAW", raw), patch.object(builder, "OUTPUT_RAW", self.root / "output-raw"), \
             patch.object(builder, "SOURCE_PROVENANCE", {}), patch.object(builder.requests, "get") as get:
            builder.arcgis_geojson("https://example.invalid/custom", where="1=1", out_fields="*", cache=cache)
            entry = builder.SOURCE_PROVENANCE["https://example.invalid/custom"]
            self.assertIsNone(entry["retrieved_date"])
            self.assertEqual("unknown", entry["status"])
            get.assert_not_called()
            self.assertEqual(before, _digest(cache))

    def test_source_report_distinguishes_rebuild_and_cache_retrieval_dates(self) -> None:
        reports = self.root / "reports"
        reports.mkdir()
        known_url = "https://example.invalid/known/query"
        unknown_url = "https://example.invalid/unknown/query"
        sources = {
            known_url: {"retrieved_date": "2020-05-17", "status": "recorded_retrieval", "sha256": "a" * 64},
            unknown_url: {"retrieved_date": None, "status": "unknown", "sha256": "b" * 64},
        }
        with patch.object(builder, "REPORTS", reports), patch.object(builder, "BUILD_DATE", "2035-01-02"), \
             patch.object(builder, "SOURCE_PROVENANCE", sources):
            builder.write_reports(self.layers, [], [])
        source_report = (reports / "water_system_sources.md").read_text(encoding="utf-8")
        self.assertIn("Historical-template rebuild, not a current review or release", source_report)
        self.assertIn("Rebuilt: 2035-01-02", source_report)
        self.assertIn("those references are not fetched by this rebuild", source_report)
        self.assertIn(f"| {known_url} | 2020-05-17 | recorded_retrieval | `{'a' * 64}` |", source_report)
        self.assertIn(f"| {unknown_url} | unknown | unknown | `{'b' * 64}` |", source_report)
        self.assertNotIn("| 2035-01-02 |", source_report)
        for name in ("water_system_assumptions.md", "water_system_qa.md", "water_system_phase1_handoff.md"):
            self.assertIn("Historical-template rebuild, not a current review or release",
                          (reports / name).read_text(encoding="utf-8"))

    def test_preserves_layers_in_existing_output_not_in_source(self) -> None:
        source = self.make_source()
        output = self.root / "rebuilt.gpkg"
        shutil.copy2(source, output)
        self.frame.to_file(output, layer="extra_output_layer", driver="GPKG", index=False)
        before = _table_fingerprints(output, {"extra_output_layer"})
        builder.write_gpkg(self.layers, self.frame, source_gpkg=source, output_gpkg=output)
        self.assertEqual(before, _table_fingerprints(output, {"extra_output_layer"}))

    @unittest.skipUnless(os.environ.get("WATER_BUILDER_TEST_GPKG"), "set WATER_BUILDER_TEST_GPKG to the hydrated current project GeoPackage")
    def test_preserves_current_project_nonwater_layers_in_temporary_copy(self) -> None:
        current = Path(os.environ["WATER_BUILDER_TEST_GPKG"])
        source = self.root / "current-copy.gpkg"
        shutil.copy2(current, source)
        source_digest = _digest(source)
        existing = set(pyogrio.list_layers(source)[:, 0])
        untouched = existing - WATER_LAYERS
        self.assertTrue({"hydrography_physical", "hydrography_network_connectors", "routing_inferred_unresolved"} <= untouched)
        before = _table_fingerprints(source, untouched)
        output = self.root / "rebuilt.gpkg"
        builder.write_gpkg(self.layers, self.frame, source_gpkg=source, output_gpkg=output)
        self.assertEqual(source_digest, _digest(source))
        self.assertEqual(existing | WATER_LAYERS, set(pyogrio.list_layers(output)[:, 0]))
        self.assertEqual(before, _table_fingerprints(output, untouched))


if __name__ == "__main__":
    unittest.main()
