"""Policy-aware topology trace checks for Model Lab v0.1B."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parents[1] / "src" / "python" / "model_lab"
sys.path.insert(0, str(MODEL_DIR))

from trace_huc_paths import TRACE_FIELDS, trace_rows, write_traces  # noqa: E402


A = "000000000001"
B = "000000000002"
C = "000000000003"
D = "000000000004"
ROUTES = {
    A: (B, "REPLACED_PHYSICAL"),
    B: (D, "UNRESOLVED"),
    C: (D, "REPLACED_AUTHORITATIVE_CONNECTOR"),
    D: ("", "BOUNDARY_EXPORT"),
}


def _find(rows: list[dict[str, str]], focus: str, traced: str) -> dict[str, str]:
    matches = [row for row in rows if row["focus_huc12"] == focus and row["traced_huc12"] == traced]
    if len(matches) != 1:
        raise AssertionError(f"Expected one trace row for {focus}/{traced}, found {len(matches)}")
    return matches[0]


class ModelLabV01BTraceTest(unittest.TestCase):
    def test_strict_paths_remain_visible_after_unresolved_cut(self) -> None:
        downstream, upstream = trace_rows("toy", "diagnostic", "strict", ROUTES)
        self.assertEqual(8, len(downstream))
        self.assertEqual(8, len(upstream))
        self.assertEqual("True", _find(downstream, A, A)["policy_reachable"])
        self.assertEqual("True", _find(downstream, A, B)["policy_reachable"])
        self.assertEqual("", _find(downstream, B, B)["first_unresolved_link_from_huc12"])
        blocked = _find(downstream, A, D)
        self.assertEqual("2", blocked["hops"])
        self.assertEqual("False", blocked["policy_reachable"])
        self.assertEqual(B, blocked["first_unresolved_link_from_huc12"])
        self.assertEqual("False", _find(upstream, D, A)["policy_reachable"])
        self.assertEqual(B, _find(upstream, D, B)["first_unresolved_link_from_huc12"])
        self.assertEqual("True", _find(upstream, D, C)["policy_reachable"])

    def test_wbd_sensitivity_keeps_cut_provenance(self) -> None:
        downstream, upstream = trace_rows("toy", "diagnostic", "assume_wbd", ROUTES)
        self.assertTrue(all(row["policy_reachable"] == "True" for row in downstream + upstream))
        self.assertEqual(B, _find(downstream, A, D)["first_unresolved_link_from_huc12"])
        self.assertEqual(B, _find(upstream, D, A)["first_unresolved_link_from_huc12"])

    def test_first_unresolved_link_is_nearest_to_origin(self) -> None:
        routes = {
            A: (B, "UNRESOLVED"),
            B: (D, "UNRESOLVED"),
            D: ("", "BOUNDARY_EXPORT"),
        }
        downstream, upstream = trace_rows("toy", "diagnostic", "strict", routes)
        self.assertEqual(A, _find(downstream, A, D)["first_unresolved_link_from_huc12"])
        self.assertEqual(B, _find(downstream, B, D)["first_unresolved_link_from_huc12"])
        self.assertEqual(A, _find(upstream, D, A)["first_unresolved_link_from_huc12"])
        self.assertEqual("True", _find(downstream, A, A)["policy_reachable"])

    def test_cycle_and_unknown_policy_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "policy"):
            trace_rows("toy", "diagnostic", "unknown", ROUTES)
        with self.assertRaisesRegex(ValueError, "Cycle"):
            trace_rows("toy", "diagnostic", "strict", {A: (B, "REPLACED_PHYSICAL"), B: (A, "UNRESOLVED")})

    def test_written_schema_and_constituent_consistency(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            (run_dir / "run_manifest.json").write_text(
                json.dumps({"run_id": "toy", "period": "diagnostic", "unresolved_policy": "strict"}),
                encoding="utf-8",
            )
            ledger_path = run_dir / "huc_balance.csv"
            fields = (
                "run_id", "period", "huc12", "constituent", "route_to_huc12",
                "routing_basis", "qa_status",
            )
            with ledger_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for huc, (target, qa_status) in ROUTES.items():
                    for constituent in ("water", "TN", "TP"):
                        writer.writerow({
                            "run_id": "toy", "period": "diagnostic", "huc12": huc,
                            "constituent": constituent, "route_to_huc12": target,
                            "routing_basis": "test", "qa_status": qa_status,
                        })
            self.assertEqual({"downstream_trace.csv": 8, "upstream_trace.csv": 8}, write_traces(run_dir))
            for name in ("downstream_trace.csv", "upstream_trace.csv"):
                with (run_dir / name).open(newline="", encoding="utf-8") as stream:
                    reader = csv.DictReader(stream)
                    self.assertEqual(list(TRACE_FIELDS), reader.fieldnames)
                    self.assertEqual(8, len(list(reader)))
            with (run_dir / "upstream_trace.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual("False", _find(rows, D, A)["policy_reachable"])

            # The writer refuses to infer one topology if constituents disagree.
            text = ledger_path.read_text(encoding="utf-8")
            ledger_path.write_text(text.replace(f"{A},TN,{B}", f"{A},TN,{D}"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differ by constituent"):
                write_traces(run_dir)


if __name__ == "__main__":
    unittest.main()
