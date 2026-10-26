"""Tests for water-source cache retrieval evidence without GIS dependencies."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python" / "systems"))
import water_source_provenance as provenance


class WaterSourceProvenanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name) / "query.geojson"
        self.cache.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
        self.url = "https://example.test/arcgis/0/query"
        self.query = {"where": "1=1", "out_fields": "id", "geometry": None,
                      "page_size": 1000, "max_allowable_offset": None}

    def test_reused_download_keeps_recorded_retrieval_date(self) -> None:
        provenance.record_retrieval(self.cache, self.url, self.query, "2020-01-02")
        with mock.patch.object(provenance, "date") as clock:
            clock.today.return_value = date(2030, 5, 6)
            clock.fromisoformat.side_effect = date.fromisoformat
            first = provenance.read_cache_provenance(self.cache, self.url, self.query)
            second = provenance.read_cache_provenance(self.cache, self.url, self.query)
        self.assertEqual("2020-01-02", first["retrieved_date"])
        self.assertEqual("recorded_retrieval", first["status"])
        self.assertEqual(first, second)
        clock.today.assert_not_called()

    def test_reused_sidecar_must_match_source_query_and_content(self) -> None:
        provenance.record_retrieval(self.cache, self.url, self.query, "2020-01-02")
        with self.assertRaisesRegex(ValueError, "source URL or query differs"):
            provenance.read_cache_provenance(self.cache, self.url + "-different", self.query)
        with self.assertRaisesRegex(ValueError, "source URL or query differs"):
            provenance.read_cache_provenance(self.cache, self.url, {**self.query, "where": "id=1"})
        self.cache.write_text('{"type":"FeatureCollection","features":[1]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "cache hash differs"):
            provenance.read_cache_provenance(self.cache, self.url, self.query)

    def test_missing_sidecar_is_explicitly_unknown_and_invalid_dates_fail(self) -> None:
        result = provenance.read_cache_provenance(self.cache, self.url, self.query)
        self.assertIsNone(result["retrieved_date"])
        self.assertEqual("unknown", result["status"])
        provenance.record_retrieval(self.cache, self.url, self.query, "2020-01-02")
        sidecar = provenance.sidecar_path(self.cache)
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        metadata["retrieved_date"] = "not-a-date"
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid cache provenance"):
            provenance.read_cache_provenance(self.cache, self.url, self.query)

    def test_original_tracked_cache_has_documented_date_and_query(self) -> None:
        cache = ROOT / "data/raw/usgs/wbd_huc12_maumee_basin.geojson"
        url = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/6/query"
        hucs = [f"0410000{i}" for i in range(3, 10)]
        query = {"where": " OR ".join(f"huc12 LIKE '{h}%'" for h in hucs),
                 "out_fields": "huc12,name,areasqkm,states,tohuc,hutype,humod",
                 "geometry": None, "page_size": 1000, "max_allowable_offset": None}
        result = provenance.read_cache_provenance(cache, url, query)
        self.assertEqual("2026-08-29", result["retrieved_date"])
        self.assertEqual("documented_phase1_snapshot", result["status"])
        with self.assertRaisesRegex(ValueError, "does not match"):
            provenance.read_cache_provenance(cache, url, {**query, "where": "1=1"})


if __name__ == "__main__":
    unittest.main()
