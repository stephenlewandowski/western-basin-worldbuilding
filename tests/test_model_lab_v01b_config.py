"""Explicit v0.1B sensitivity and output-contract checks on toy arithmetic.

Toy HUCs and pulses are synthetic diagnostics, not basin observations.
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/python/model_lab"))

from route_water_nutrients import (  # noqa: E402
    load_network, load_sensitivity_config, run_model, run_sensitivity_config, write_run,
)
from validate_run import SCHEMA_V01B, validate_run  # noqa: E402

H1, H2, H3, OUTSIDE = (f"{number:012d}" for number in range(1, 5))
UNITS = {"water": "m3/period", "TN": "kg/period", "TP": "kg/period"}


def _csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class ModelLabV01BConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wbd = self.root / "hucs.geojson"
        self.routing = self.root / "routing.csv"
        self.inputs = self.root / "inputs.csv"
        self.assumptions = self.root / "assumptions.csv"
        self.config_path = self.root / "sensitivity.json"
        features = [
            {
                "type": "Feature", "properties": {"huc12": huc, "tohuc": target},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [index, 0], [index + 1, 0], [index + 1, 1], [index, 1], [index, 0],
                ]]},
            }
            for index, (huc, target) in enumerate(((H1, H3), (H2, H3), (H3, OUTSIDE)))
        ]
        self.wbd.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
        _csv(self.routing, (
            "from_huc12", "to_huc12", "qa_status", "routing_basis", "physical_geometry",
        ), [
            {"from_huc12": H1, "to_huc12": H3, "qa_status": "REPLACED_PHYSICAL",
             "routing_basis": "physical_3dhp", "physical_geometry": "True"},
            {"from_huc12": H2, "to_huc12": H3, "qa_status": "UNRESOLVED",
             "routing_basis": "project_inference", "physical_geometry": "False"},
        ])
        self.config = {
            "config_version": "0.1B", "period": "toy_no_time",
            "inputs": str(self.inputs), "wbd": str(self.wbd), "routing": str(self.routing),
            "runs": [
                {"run_id": "toy_strict", "label": "Strict", "description": "Synthetic strict case",
                 "unresolved_policy": "strict", "assumptions": None, "out_dir": str(self.root / "strict")},
                {"run_id": "toy_wbd", "label": "WBD successor", "description": "Synthetic routing sensitivity",
                 "unresolved_policy": "assume_wbd", "assumptions": None, "out_dir": str(self.root / "wbd")},
                {"run_id": "toy_half", "label": "TN half pass", "description": "Synthetic TN pass-through sensitivity",
                 "unresolved_policy": "strict", "assumptions": str(self.assumptions),
                 "out_dir": str(self.root / "half")},
            ],
        }
        rows = []
        for case in self.config["runs"]:
            for huc in (H1, H2):
                for constituent, unit in UNITS.items():
                    rows.append({
                        "run_id": case["run_id"], "period": "toy_no_time", "huc12": huc,
                        "constituent": constituent, "local_input": "1", "unit": unit,
                        "input_status": "synthetic_diagnostic", "source_id": "toy_test",
                        "method": "unit pulse", "uncertainty_note": "No empirical interpretation",
                    })
        _csv(self.inputs, (
            "run_id", "period", "huc12", "constituent", "local_input", "unit",
            "input_status", "source_id", "method", "uncertainty_note",
        ), rows)
        _csv(self.assumptions, (
            "huc12", "constituent", "pass_through", "assumption_status", "source_id", "notes",
        ), [{
            "huc12": H1, "constituent": "TN", "pass_through": "0.5",
            "assumption_status": "synthetic_diagnostic", "source_id": "toy_test",
            "notes": "Hypothetical arithmetic only",
        }])
        self._write_config()

    def _write_config(self) -> None:
        self.config_path.write_text(json.dumps(self.config, indent=2) + "\n", encoding="utf-8")

    def _build(self) -> list[tuple[Path, object]]:
        return run_sensitivity_config(self.config_path)

    def test_three_cases_write_versioned_schema_and_preserve_arithmetic(self) -> None:
        completed = self._build()
        self.assertEqual(3, len(completed))
        expected = {
            "toy_strict": (Decimal(0), Decimal(1), Decimal(1)),
            "toy_wbd": (Decimal(0), Decimal(0), Decimal(2)),
            "toy_half": (Decimal("0.5"), Decimal(1), Decimal("0.5")),
        }
        for out_dir, result in completed:
            with self.subTest(run=out_dir.name):
                self.assertEqual([], validate_run(out_dir))
                manifest = result.manifest
                self.assertEqual("0.1B", manifest["model_version"])
                self.assertEqual("0.1B", manifest["schema_version"])
                self.assertEqual({name: list(fields) for name, fields in SCHEMA_V01B.items()}, manifest["output_schema"])
                self.assertEqual(set(SCHEMA_V01B), {path.name for path in out_dir.glob("*.csv")})
                self.assertIsNotNone(manifest["source_files"]["trace_generator_sha256"])
                summary = next(row for row in result.summary if row["constituent"] == "TN")
                actual = tuple(Decimal(summary[field]) for field in (
                    "total_not_forwarded_assumed", "total_unrouted_at_unresolved", "boundary_export",
                ))
                self.assertEqual(expected[manifest["run_id"]], actual)

    def test_config_rejects_duplicate_run_ids_and_output_paths(self) -> None:
        self.config["runs"][1]["run_id"] = "toy_strict"
        self._write_config()
        with self.assertRaisesRegex(ValueError, "distinct run IDs"):
            load_sensitivity_config(self.config_path)
        self.config["runs"][1]["run_id"] = "toy_wbd"
        self.config["runs"][1]["out_dir"] = self.config["runs"][0]["out_dir"]
        self._write_config()
        with self.assertRaisesRegex(ValueError, "distinct run IDs"):
            load_sensitivity_config(self.config_path)

    def test_config_rejects_unknown_policy_and_implicit_assumptions(self) -> None:
        self.config["runs"][0]["unresolved_policy"] = "unqualified_route"
        self._write_config()
        with self.assertRaisesRegex(ValueError, "unknown unresolved policy"):
            load_sensitivity_config(self.config_path)
        self.config["runs"][0]["unresolved_policy"] = "strict"
        del self.config["runs"][0]["assumptions"]
        self._write_config()
        with self.assertRaisesRegex(ValueError, "must have exactly"):
            load_sensitivity_config(self.config_path)

    def test_config_cannot_replace_historical_or_unmanifested_run(self) -> None:
        self.config["runs"][0]["run_id"] = "v01a_unit_pulse_strict"
        self.config["runs"][0]["out_dir"] = str(ROOT / "outputs/model_lab/v01a_unit_pulse_strict")
        self._write_config()
        with self.assertRaisesRegex(ValueError, "different or historical run"):
            load_sensitivity_config(self.config_path)
        self.config["runs"][0]["run_id"] = "toy_strict"
        unmanifested = self.root / "occupied"
        unmanifested.mkdir()
        (unmanifested / "other.txt").write_text("unrelated", encoding="utf-8")
        self.config["runs"][0]["out_dir"] = str(unmanifested)
        self._write_config()
        with self.assertRaisesRegex(ValueError, "nonempty output directory"):
            load_sensitivity_config(self.config_path)

    def test_validator_detects_changed_config_and_output_header(self) -> None:
        self._build()
        out_dir = self.root / "strict"
        self.config["runs"][0]["description"] = "Altered after production"
        self._write_config()
        self.assertTrue(any("Source hash mismatch for sensitivity_config" in problem
                            for problem in validate_run(out_dir)))
        self.config["runs"][0]["description"] = "Synthetic strict case"
        self._write_config()
        path = out_dir / "huc_balance.csv"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("not_forwarded_assumed", "old_field", 1), encoding="utf-8")
        self.assertTrue(any("header differs" in problem for problem in validate_run(out_dir)))

    def test_validator_detects_corrupt_trace(self) -> None:
        self._build()
        out_dir = self.root / "strict"
        path = out_dir / "downstream_trace.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = tuple(reader.fieldnames or ()), list(reader)
        nonself = next(row for row in rows if row["hops"] != "0")
        nonself["policy_reachable"] = "False" if nonself["policy_reachable"] == "True" else "True"
        _csv(path, fields, rows)
        self.assertTrue(any("policy reachability differs" in problem for problem in validate_run(out_dir)))

    def test_unconfigured_single_run_keeps_a_valid_v01b_manifest(self) -> None:
        out_dir = self.root / "single"
        result = run_model("toy_strict", "toy_no_time", self.inputs, load_network(self.wbd, self.routing))
        write_run(result, out_dir)
        self.assertIsNone(result.manifest["sensitivity_case"])
        self.assertIsNone(result.manifest["source_files"]["sensitivity_config"])
        self.assertEqual([], validate_run(out_dir))

    def test_accepted_v01a_outputs_remain_valid(self) -> None:
        for name in ("v01a_unit_pulse_strict", "v01a_unit_pulse_assume_wbd"):
            with self.subTest(name=name):
                self.assertEqual([], validate_run(ROOT / "outputs/model_lab" / name))


if __name__ == "__main__":
    unittest.main()
