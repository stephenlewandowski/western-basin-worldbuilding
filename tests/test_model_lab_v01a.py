"""Synthetic, independently checkable unit pulses for Model Lab v0.1A.

These toy HUC IDs and one-unit quantities are arithmetic diagnostics, not
western basin observations or calibrated parameters.
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[1] / "src" / "python" / "model_lab"
sys.path.insert(0, str(MODEL_DIR))

from route_water_nutrients import load_network, run_model, write_run  # noqa: E402
from validate_run import validate_run  # noqa: E402

H1 = "000000000001"
H2 = "000000000002"
H3 = "000000000003"
OUTSIDE = "000000000004"
CONSTITUENTS = ("water", "TN", "TP")
UNITS = {"water": "m3/period", "TN": "kg/period", "TP": "kg/period"}
INPUT_FIELDS = (
    "run_id", "period", "huc12", "constituent", "local_input", "unit",
    "input_status", "source_id", "method", "uncertainty_note",
)
ROUTING_FIELDS = (
    "from_huc12", "to_huc12", "qa_status", "routing_basis", "physical_geometry",
)
ASSUMPTION_FIELDS = (
    "huc12", "constituent", "pass_through", "assumption_status", "source_id", "notes",
)


def _csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _amount(result: object, huc: str, constituent: str, field: str) -> Decimal:
    rows = [row for row in result.balances if row["huc12"] == huc and row["constituent"] == constituent]
    if len(rows) != 1:
        raise AssertionError(f"Expected one balance row for {huc}/{constituent}, got {len(rows)}")
    return Decimal(str(rows[0][field]))


class ModelLabV01ATest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wbd = self.root / "toy_hucs.geojson"
        self.routing = self.root / "toy_routing.csv"
        self.inputs = self.root / "toy_inputs.csv"
        self.assumptions = self.root / "toy_assumptions.csv"
        self.out = self.root / "run"
        self._write_network()

    def _write_network(self, *, route_1: str = H3, route_2: str = H3) -> None:
        features = []
        for index, (huc, tohuc) in enumerate(((H1, route_1), (H2, route_2), (H3, OUTSIDE))):
            x = float(index)
            features.append({
                "type": "Feature",
                "properties": {"huc12": huc, "tohuc": tohuc},
                "geometry": {"type": "Polygon", "coordinates": [[
                    [x, 0], [x + 1, 0], [x + 1, 1], [x, 1], [x, 0],
                ]]},
            })
        self.wbd.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
        _csv(self.routing, ROUTING_FIELDS, [
            {
                "from_huc12": H1, "to_huc12": route_1,
                "qa_status": "REPLACED_PHYSICAL", "routing_basis": "physical_3dhp",
                "physical_geometry": "True",
            },
            {
                "from_huc12": H2, "to_huc12": route_2,
                "qa_status": "UNRESOLVED", "routing_basis": "project_inference",
                "physical_geometry": "False",
            },
        ])

    def _rows(self, huc: str = H1, amount: str = "1") -> list[dict[str, str]]:
        return [{
            "run_id": "toy_pulse", "period": "diagnostic", "huc12": huc,
            "constituent": constituent, "local_input": amount,
            "unit": UNITS[constituent], "input_status": "synthetic_diagnostic",
            "source_id": "toy_test", "method": "one-unit arithmetic pulse",
            "uncertainty_note": "Synthetic topology check; no empirical inference",
        } for constituent in CONSTITUENTS]

    def _run(self, rows: list[dict[str, str]], *, policy: str = "strict", assumptions: bool = False):
        _csv(self.inputs, INPUT_FIELDS, rows)
        network = load_network(self.wbd, self.routing)
        result = run_model(
            "toy_pulse", "diagnostic", self.inputs, network, policy=policy,
            assumptions_path=self.assumptions if assumptions else None,
        )
        write_run(result, self.out)
        self.assertEqual([], validate_run(self.out))
        return result

    def test_network_topology_is_three_hucs_two_links_one_terminal(self) -> None:
        network = load_network(self.wbd, self.routing)
        self.assertEqual({H1, H2, H3}, set(network.hucs))
        self.assertEqual(H3, network.terminal)
        self.assertEqual(3, len(network.order))
        self.assertLess(network.order.index(H1), network.order.index(H3))
        self.assertLess(network.order.index(H2), network.order.index(H3))

    def test_each_constituent_unit_pulse_reaches_boundary_on_qualified_link(self) -> None:
        result = self._run(self._rows(H1))
        for constituent in CONSTITUENTS:
            with self.subTest(constituent=constituent):
                self.assertEqual(Decimal(1), _amount(result, H1, constituent, "downstream_out"))
                self.assertEqual(Decimal(1), _amount(result, H3, constituent, "upstream_in"))
                self.assertEqual(Decimal(1), _amount(result, H3, constituent, "boundary_export"))
                self.assertEqual(Decimal(0), _amount(result, H3, constituent, "residual"))

    def test_strict_policy_leaves_pulse_unrouted_at_unresolved_link(self) -> None:
        result = self._run(self._rows(H2))
        for constituent in CONSTITUENTS:
            with self.subTest(constituent=constituent):
                self.assertEqual(Decimal(1), _amount(result, H2, constituent, "unrouted_at_unresolved"))
                self.assertEqual(Decimal(0), _amount(result, H2, constituent, "downstream_out"))
                self.assertEqual(Decimal(0), _amount(result, H3, constituent, "boundary_export"))

    def test_assume_wbd_policy_routes_pulse_across_unresolved_link(self) -> None:
        result = self._run(self._rows(H2), policy="assume_wbd")
        for constituent in CONSTITUENTS:
            with self.subTest(constituent=constituent):
                self.assertEqual(Decimal(0), _amount(result, H2, constituent, "unrouted_at_unresolved"))
                self.assertEqual(Decimal(1), _amount(result, H2, constituent, "downstream_out"))
                self.assertEqual(Decimal(1), _amount(result, H3, constituent, "boundary_export"))

    def test_upstream_pulse_stops_at_downstream_unresolved_cut(self) -> None:
        self._write_network(route_1=H2)
        result = self._run(self._rows(H1))
        for constituent in CONSTITUENTS:
            with self.subTest(constituent=constituent):
                self.assertEqual(Decimal(1), _amount(result, H2, constituent, "upstream_in"))
                self.assertEqual(Decimal(1), _amount(result, H2, constituent, "unrouted_at_unresolved"))
                self.assertEqual(Decimal(0), _amount(result, H3, constituent, "boundary_export"))

    def test_terminal_local_pulse_is_boundary_export(self) -> None:
        result = self._run(self._rows(H3))
        for constituent in CONSTITUENTS:
            self.assertEqual(Decimal(1), _amount(result, H3, constituent, "boundary_export"))
            self.assertEqual(Decimal(0), _amount(result, H3, constituent, "downstream_out"))

    def test_zero_inputs_close_without_export_or_unrouted_quantity(self) -> None:
        result = self._run([])
        for row in result.balances:
            self.assertEqual(Decimal(0), Decimal(str(row["available"])))
            self.assertEqual(Decimal(0), Decimal(str(row["residual"])))
        self.assertEqual([], result.input_rows)

    def test_explicit_fractional_pass_through_accounts_for_not_forwarded_quantity(self) -> None:
        _csv(self.assumptions, ASSUMPTION_FIELDS, [{
            "huc12": H1, "constituent": "TN", "pass_through": "0.5",
            "assumption_status": "synthetic_diagnostic", "source_id": "toy_test",
            "notes": "Hypothetical arithmetic sensitivity; no measured retention",
        }])
        result = self._run(self._rows(H1), assumptions=True)
        self.assertEqual(Decimal("0.5"), _amount(result, H1, "TN", "not_forwarded_assumed"))
        self.assertEqual(Decimal("0.5"), _amount(result, H3, "TN", "boundary_export"))
        self.assertEqual(Decimal(1), _amount(result, H3, "water", "boundary_export"))
        self.assertEqual(Decimal(1), _amount(result, H3, "TP", "boundary_export"))

    def test_written_schema_uses_bookkeeping_dispositions(self) -> None:
        result = self._run(self._rows(H2))
        self.assertEqual("default_unit_pass_through_reference", result.manifest["assumption_status"])
        for filename, expected in (
            ("huc_balance.csv", {"not_forwarded_assumed", "unrouted_at_unresolved"}),
            ("boundary_summary.csv", {"total_not_forwarded_assumed", "total_unrouted_at_unresolved"}),
        ):
            with self.subTest(filename=filename), (self.out / filename).open(newline="", encoding="utf-8") as stream:
                fields = set(csv.DictReader(stream).fieldnames or ())
                self.assertTrue(expected.issubset(fields))
                self.assertFalse(fields.intersection({
                    "held_assumed", "held_unresolved", "total_held_assumed", "total_held_unresolved",
                }))

    def test_rejects_unknown_huc(self) -> None:
        rows = self._rows()
        rows[0]["huc12"] = "999999999999"
        _csv(self.inputs, INPUT_FIELDS, rows)
        with self.assertRaises(ValueError):
            run_model("toy_pulse", "diagnostic", self.inputs, load_network(self.wbd, self.routing))

    def test_rejects_duplicate_huc_constituent_input(self) -> None:
        rows = self._rows()
        _csv(self.inputs, INPUT_FIELDS, rows + [rows[0].copy()])
        with self.assertRaises(ValueError):
            run_model("toy_pulse", "diagnostic", self.inputs, load_network(self.wbd, self.routing))

    def test_rejects_negative_input(self) -> None:
        rows = self._rows(amount="-1")
        _csv(self.inputs, INPUT_FIELDS, rows)
        with self.assertRaises(ValueError):
            run_model("toy_pulse", "diagnostic", self.inputs, load_network(self.wbd, self.routing))

    def test_rejects_wrong_unit(self) -> None:
        rows = self._rows()
        rows[0]["unit"] = "kg/period"
        _csv(self.inputs, INPUT_FIELDS, rows)
        with self.assertRaises(ValueError):
            run_model("toy_pulse", "diagnostic", self.inputs, load_network(self.wbd, self.routing))

    def test_rejects_cycle(self) -> None:
        self._write_network(route_1=H2, route_2=H1)
        with self.assertRaises(ValueError):
            load_network(self.wbd, self.routing)

    def test_validator_detects_corrupt_written_edge(self) -> None:
        self._run(self._rows(H1))
        path = self.out / "edge_flux.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields = tuple(reader.fieldnames or ())
            rows = list(reader)
        self.assertTrue(rows)
        rows[0]["amount"] = "0.75"
        _csv(path, fields, rows)
        self.assertTrue(any("edge out" in problem or "edge in" in problem for problem in validate_run(self.out)))

    def test_validator_detects_corrupt_written_summary(self) -> None:
        self._run(self._rows(H1))
        path = self.out / "boundary_summary.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields = tuple(reader.fieldnames or ())
            rows = list(reader)
        rows[0]["boundary_export"] = "0.75"
        _csv(path, fields, rows)
        self.assertTrue(any("boundary_export" in problem for problem in validate_run(self.out)))

    def test_validator_detects_changed_source_and_recorded_engine_hash(self) -> None:
        self._run(self._rows(H1))
        original = self.inputs.read_bytes()
        self.inputs.write_bytes(original + b"# source changed after run\n")
        self.assertTrue(any("Source hash mismatch for input" in problem for problem in validate_run(self.out)))
        self.inputs.write_bytes(original)
        manifest_path = self.out / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["source_files"]["engine_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("Engine source hash mismatch" in problem for problem in validate_run(self.out)))


if __name__ == "__main__":
    unittest.main()
