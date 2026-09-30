"""Write policy-aware HUC topology traces for a completed Model Lab run.

These are paths through the qualified one-successor HUC graph. A reachable
path is only permitted by the run's unresolved-link policy; it is not evidence
of actual water or nutrient movement, source attribution, or physical stream
geometry. In particular, a zero local input or a zero pass-through fraction
can mean no quantity moves on an otherwise policy-reachable path.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TRACE_FIELDS = (
    "run_id", "period", "unresolved_policy", "focus_huc12", "traced_huc12",
    "hops", "policy_reachable", "first_unresolved_link_from_huc12",
)
TRACE_FILES = ("downstream_trace.csv", "upstream_trace.csv")
CONSTITUENTS = ("water", "TN", "TP")
ROUTE_STATUSES = (
    "REPLACED_PHYSICAL", "REPLACED_AUTHORITATIVE_CONNECTOR",
    "ALREADY_REDUNDANT", "UNRESOLVED",
)
BALANCE_REQUIRED = (
    "run_id", "period", "huc12", "constituent", "route_to_huc12",
    "routing_basis", "qa_status",
)


def _read_routes(run_dir: Path, run_id: str, period: str) -> dict[str, tuple[str, str]]:
    """Read topology from the run ledger and check constituent agreement."""
    with (run_dir / "huc_balance.csv").open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = set(BALANCE_REQUIRED) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"huc_balance.csv is missing trace fields: {sorted(missing)}")
        rows = list(reader)
    by_huc: dict[str, dict[str, tuple[str, str, str]]] = {}
    for row in rows:
        if row["run_id"] != run_id or row["period"] != period:
            raise ValueError("huc_balance.csv run_id/period disagrees with manifest")
        huc, constituent = row["huc12"], row["constituent"]
        if not huc or constituent not in CONSTITUENTS:
            raise ValueError(f"Invalid trace HUC or constituent: {huc!r}/{constituent!r}")
        per_constituent = by_huc.setdefault(huc, {})
        if constituent in per_constituent:
            raise ValueError(f"Duplicate trace HUC/constituent: {huc}/{constituent}")
        per_constituent[constituent] = (
            row["route_to_huc12"], row["qa_status"], row["routing_basis"]
        )
    if not by_huc:
        raise ValueError("huc_balance.csv has no HUC rows")
    routes: dict[str, tuple[str, str]] = {}
    for huc, per_constituent in by_huc.items():
        if set(per_constituent) != set(CONSTITUENTS):
            raise ValueError(f"Incomplete constituent coverage for trace HUC {huc}")
        if len(set(per_constituent.values())) != 1:
            raise ValueError(f"Route metadata differ by constituent at {huc}")
        target, qa_status, _ = per_constituent["water"]
        routes[huc] = (target, qa_status)
    terminals = [huc for huc, (target, _) in routes.items() if not target]
    if len(terminals) != 1:
        raise ValueError(f"Expected one trace terminal, found {len(terminals)}")
    for huc, (target, qa_status) in routes.items():
        if target and target not in routes:
            raise ValueError(f"Trace route leaves the HUC extract: {huc} -> {target}")
        if target == huc:
            raise ValueError(f"Trace self-loop at {huc}")
        if target and qa_status not in ROUTE_STATUSES:
            raise ValueError(f"Trace route has unknown QA status: {huc}/{qa_status}")
        if not target and qa_status != "BOUNDARY_EXPORT":
            raise ValueError(f"Trace terminal has unexpected QA status: {huc}/{qa_status}")
    return routes


def trace_rows(
    run_id: str, period: str, policy: str,
    routes: dict[str, tuple[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return downstream paths and their upstream index, including self rows.

    `first_unresolved_link_from_huc12` is the source of the first unresolved link
    encountered while walking from the upstream origin toward the downstream
    target. It remains visible in the assume_wbd sensitivity even though that
    policy allows the path.
    """
    if policy not in ("strict", "assume_wbd"):
        raise ValueError(f"Unknown unresolved-link policy: {policy!r}")
    downstream: list[dict[str, str]] = []
    for origin in sorted(routes):
        current, hops, first_unresolved = origin, 0, ""
        seen: set[str] = set()
        while True:
            if current in seen:
                raise ValueError(f"Cycle in trace route from {origin} at {current}")
            seen.add(current)
            downstream.append({
                "run_id": run_id,
                "period": period,
                "unresolved_policy": policy,
                "focus_huc12": origin,
                "traced_huc12": current,
                "hops": str(hops),
                "policy_reachable": str(policy == "assume_wbd" or not first_unresolved),
                "first_unresolved_link_from_huc12": first_unresolved,
            })
            target, qa_status = routes[current]
            if not target:
                break
            if target not in routes:
                raise ValueError(f"Trace route leaves the HUC extract: {current} -> {target}")
            if qa_status == "UNRESOLVED" and not first_unresolved:
                first_unresolved = current
            current, hops = target, hops + 1
    upstream = [
        {**row, "focus_huc12": row["traced_huc12"], "traced_huc12": row["focus_huc12"]}
        for row in downstream
    ]
    upstream.sort(key=lambda row: (row["focus_huc12"], int(row["hops"]), row["traced_huc12"]))
    return downstream, upstream


def write_traces(run_dir: Path) -> dict[str, int]:
    """Write both trace CSVs beside a completed ledger; return row counts."""
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    run_id, period, policy = (
        manifest.get("run_id"), manifest.get("period"), manifest.get("unresolved_policy")
    )
    if not isinstance(run_id, str) or not run_id or not isinstance(period, str) or not period:
        raise ValueError("Manifest needs nonempty run_id and period for traces")
    routes = _read_routes(run_dir, run_id, period)
    downstream, upstream = trace_rows(run_id, period, policy, routes)
    result: dict[str, int] = {}
    for name, rows in zip(TRACE_FILES, (downstream, upstream)):
        with (run_dir / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=TRACE_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        result[name] = len(rows)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    for filename, count in write_traces(args.run_dir).items():
        print(f"Wrote {count} {filename} rows to {args.run_dir}")


if __name__ == "__main__":
    main()
