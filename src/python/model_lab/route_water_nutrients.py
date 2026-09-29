"""Model Lab v0.1A: conditional HUC-12 water/TN/TP accounting.

This deliberately has no empirical load estimator, hydrologic calibration,
travel times, or ecological effects. Inputs and unresolved-route policy govern
the result; node and run ledgers expose every disposition.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WBD = ROOT / "data/raw/usgs/wbd_huc12_maumee_basin.geojson"
DEFAULT_ROUTING = ROOT / "data/processed/networks/huc12_routing_current.csv"
CONSTITUENTS = ("water", "TN", "TP")
UNITS = {"water": "m3/period", "TN": "kg/period", "TP": "kg/period"}
ZERO = Decimal(0)
ONE = Decimal(1)
getcontext().prec = 50
STATUS_BASIS = {
    "REPLACED_PHYSICAL": "physical_3dhp",
    "REPLACED_AUTHORITATIVE_CONNECTOR": "official_3dhp_connector",
    "ALREADY_REDUNDANT": "physical_nhdplus_hr_existing",
    "UNRESOLVED": "project_inference",
}
BALANCE_FIELDS = (
    "run_id", "period", "huc12", "constituent", "unit", "local_input",
    "upstream_in", "available", "pass_through", "not_forwarded_assumed",
    "unrouted_at_unresolved", "downstream_out", "boundary_export", "residual",
    "route_to_huc12", "routing_basis", "qa_status", "physical_geometry",
    "input_status",
)
EDGE_FIELDS = (
    "run_id", "period", "from_huc12", "to_huc12", "constituent",
    "unit", "amount", "routing_basis", "qa_status", "assumed_unresolved",
)
SUMMARY_FIELDS = (
    "run_id", "period", "constituent", "unit", "total_local_input",
    "total_not_forwarded_assumed", "total_unrouted_at_unresolved", "boundary_export",
    "residual", "unresolved_policy",
)
INPUT_FIELDS = (
    "run_id", "period", "huc12", "constituent", "local_input", "unit",
    "input_status", "source_id", "method", "uncertainty_note",
)
ASSUMPTION_FIELDS = (
    "huc12", "constituent", "pass_through", "assumption_status",
    "source_id", "notes",
)


@dataclass(frozen=True)
class Network:
    hucs: frozenset[str]
    routing: dict[str, dict[str, str]]
    order: tuple[str, ...]
    terminal: str
    external_boundary: str
    accepted_baseline: bool
    wbd_path: Path
    routing_path: Path


@dataclass(frozen=True)
class RunResult:
    balances: list[dict[str, str]]
    edges: list[dict[str, str]]
    summary: list[dict[str, str]]
    manifest: dict
    input_rows: list[dict[str, str]]


def _read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not set(fields).issubset(reader.fieldnames):
            raise ValueError(f"{path} is missing required columns: {sorted(set(fields) - set(reader.fieldnames or []))}")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError(f"{path} has malformed CSV rows")
    return rows


def _number(raw: str, label: str) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, TypeError):
        raise ValueError(f"{label} must be a finite number: {raw!r}") from None
    if not value.is_finite() or value < ZERO:
        raise ValueError(f"{label} must be finite and nonnegative: {raw!r}")
    return value


def _fmt(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    return format(value.normalize(), "f")


def _near_zero(value: Decimal, scale: Decimal) -> bool:
    return abs(value) <= max(Decimal("0.000000001"), abs(scale) * Decimal("0.000000000001"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_path(path: Path) -> str:
    """Keep repository inputs portable; retain an absolute path for external fixtures."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def load_network(wbd_path: Path, routing_path: Path) -> Network:
    """Validate the qualified one-successor accounting graph, not stream geometry."""
    wbd_path, routing_path = Path(wbd_path), Path(routing_path)
    features = json.loads(wbd_path.read_text(encoding="utf-8"))["features"]
    properties: dict[str, dict] = {}
    for feature in features:
        prop = feature["properties"]
        huc = str(prop.get("huc12", ""))
        if not huc.isdigit() or len(huc) != 12 or huc in properties:
            raise ValueError(f"Invalid or duplicate WBD HUC-12: {huc!r}")
        properties[huc] = prop
    if not properties:
        raise ValueError("WBD contains no HUC-12 units")

    routing: dict[str, dict[str, str]] = {}
    for row in _read_csv(routing_path, ("from_huc12", "to_huc12", "qa_status", "routing_basis", "physical_geometry")):
        source, target = row["from_huc12"], row["to_huc12"]
        status = row["qa_status"]
        if source in routing or source not in properties or target not in properties or source == target:
            raise ValueError(f"Invalid, duplicate, or out-of-network route: {source} -> {target}")
        if status not in STATUS_BASIS or row["routing_basis"] != STATUS_BASIS[status]:
            raise ValueError(f"Unrecognized route status/basis at {source}")
        if row["physical_geometry"] not in ("True", "False"):
            raise ValueError(f"Invalid physical_geometry at {source}")
        if (row["physical_geometry"] == "True") != (status in ("REPLACED_PHYSICAL", "ALREADY_REDUNDANT")):
            raise ValueError(f"Physical-geometry status conflict at {source}")
        if str(properties[source].get("tohuc", "")) != target:
            raise ValueError(f"Route differs from WBD successor at {source}")
        routing[source] = row

    terminals = set(properties) - set(routing)
    if len(terminals) != 1:
        raise ValueError(f"Expected one terminal HUC, found {len(terminals)}")
    terminal = next(iter(terminals))
    external_boundary = str(properties[terminal].get("tohuc", ""))
    if not external_boundary or external_boundary in properties:
        raise ValueError("Terminal must point to a named out-of-extract WBD HUC")

    indegree = {huc: 0 for huc in properties}
    for row in routing.values():
        indegree[row["to_huc12"]] += 1
    ready = [huc for huc, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        huc = heapq.heappop(ready)
        order.append(huc)
        if huc in routing:
            target = routing[huc]["to_huc12"]
            indegree[target] -= 1
            if indegree[target] == 0:
                heapq.heappush(ready, target)
    if len(order) != len(properties):
        raise ValueError("HUC routing contains a cycle")

    accepted = (
        wbd_path.resolve() == DEFAULT_WBD.resolve()
        and routing_path.resolve() == DEFAULT_ROUTING.resolve()
    )
    if accepted and (
        len(properties) != 252 or len(routing) != 251
        or sum(row["qa_status"] == "UNRESOLVED" for row in routing.values()) != 12
        or terminal != "041000090904"
    ):
        raise ValueError("Accepted current-development routing counts or boundary changed")
    return Network(
        frozenset(properties), routing, tuple(order), terminal,
        external_boundary, accepted, wbd_path, routing_path,
    )


def _load_inputs(
    inputs_path: Path, run_id: str, period: str, network: Network,
) -> tuple[dict[tuple[str, str], Decimal], dict[tuple[str, str], str], list[dict[str, str]], str]:
    rows = _read_csv(Path(inputs_path), INPUT_FIELDS)
    selected = [row for row in rows if row["run_id"] == run_id and row["period"] == period]
    if rows and not selected:
        raise ValueError(f"No inputs for run_id={run_id!r}, period={period!r}")
    amounts: dict[tuple[str, str], Decimal] = {}
    statuses: dict[tuple[str, str], str] = {}
    run_statuses: set[str] = set()
    for row in selected:
        huc, constituent = row["huc12"], row["constituent"]
        key = (huc, constituent)
        if huc not in network.hucs or constituent not in CONSTITUENTS or key in amounts:
            raise ValueError(f"Unknown HUC/constituent or duplicate input: {key}")
        if row["unit"] != UNITS[constituent]:
            raise ValueError(f"Wrong unit for {constituent} at {huc}")
        status = row["input_status"]
        if status not in ("synthetic_diagnostic", "parameterized", "observed_derived"):
            raise ValueError(f"Unknown input status: {status}")
        if not row["source_id"] or not row["method"]:
            raise ValueError(f"Input provenance missing at {huc}")
        amounts[key] = _number(row["local_input"], f"local input {key}")
        statuses[key] = status
        run_statuses.add(status)
    if len(run_statuses) > 1:
        raise ValueError("Do not mix input-status classes within one v0.1A run")
    run_status = next(iter(run_statuses), "synthetic_diagnostic")
    if run_status != "synthetic_diagnostic" and len(amounts) != len(network.hucs) * len(CONSTITUENTS):
        raise ValueError("Non-diagnostic runs require explicit HUC/constituent coverage")
    return amounts, statuses, selected, run_status


def _load_assumptions(path: Path | None, network: Network) -> tuple[dict[tuple[str, str], Decimal], str]:
    if path is None:
        return {}, "default_unit_pass_through_reference"
    values: dict[tuple[str, str], Decimal] = {}
    statuses: set[str] = set()
    for row in _read_csv(Path(path), ASSUMPTION_FIELDS):
        key = (row["huc12"], row["constituent"])
        if key[0] not in network.hucs or key[1] not in CONSTITUENTS or key in values:
            raise ValueError(f"Unknown or duplicate pass-through assumption: {key}")
        fraction = _number(row["pass_through"], f"pass-through {key}")
        if fraction > ONE:
            raise ValueError(f"Pass-through exceeds one: {key}")
        status = row["assumption_status"]
        if status not in ("parameterized", "synthetic_diagnostic") or not row["source_id"]:
            raise ValueError(f"Explicit pass-through needs parameter status and provenance: {key}")
        statuses.add(status)
        values[key] = fraction
    if len(statuses) > 1:
        raise ValueError("Do not mix assumption-status classes within one v0.1A run")
    return values, next(iter(statuses), "default_unit_pass_through_reference")


def run_model(
    run_id: str, period: str, inputs_path: Path, network: Network,
    policy: str = "strict", assumptions_path: Path | None = None,
) -> RunResult:
    if not run_id or not period or policy not in ("strict", "assume_wbd"):
        raise ValueError("Supply run_id, period, and strict or assume_wbd policy")
    inputs_path = Path(inputs_path)
    assumptions_path = Path(assumptions_path) if assumptions_path is not None else None
    local, statuses, selected, run_status = _load_inputs(inputs_path, run_id, period, network)
    fractions, assumption_status = _load_assumptions(assumptions_path, network)
    upstream = {(h, c): ZERO for h in network.hucs for c in CONSTITUENTS}
    balances: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    totals = {c: {name: ZERO for name in ("input", "not_forwarded_assumed", "unrouted_at_unresolved", "boundary")} for c in CONSTITUENTS}

    for huc in network.order:
        route = network.routing.get(huc)
        for constituent in CONSTITUENTS:
            key = (huc, constituent)
            own, received = local.get(key, ZERO), upstream[key]
            available = own + received
            fraction = fractions.get(key, ONE)
            not_forwarded_assumed = available * (ONE - fraction)
            remainder = available - not_forwarded_assumed
            blocked = route is not None and route["qa_status"] == "UNRESOLVED" and policy == "strict"
            unrouted_at_unresolved = remainder if blocked else ZERO
            downstream = remainder if route is not None and not blocked else ZERO
            boundary = remainder if route is None else ZERO
            residual = own + received - not_forwarded_assumed - unrouted_at_unresolved - downstream - boundary
            if not _near_zero(residual, available):
                raise AssertionError(f"Internal ledger failed at {huc} {constituent}")
            if downstream:
                target = route["to_huc12"]
                upstream[(target, constituent)] += downstream
                edges.append({
                    "run_id": run_id, "period": period, "from_huc12": huc,
                    "to_huc12": target, "constituent": constituent,
                    "unit": UNITS[constituent], "amount": _fmt(downstream),
                    "routing_basis": route["routing_basis"], "qa_status": route["qa_status"],
                    "assumed_unresolved": str(route["qa_status"] == "UNRESOLVED"),
                })
            totals[constituent]["input"] += own
            totals[constituent]["not_forwarded_assumed"] += not_forwarded_assumed
            totals[constituent]["unrouted_at_unresolved"] += unrouted_at_unresolved
            totals[constituent]["boundary"] += boundary
            balances.append({
                "run_id": run_id, "period": period, "huc12": huc,
                "constituent": constituent, "unit": UNITS[constituent],
                "local_input": _fmt(own), "upstream_in": _fmt(received),
                "available": _fmt(available), "pass_through": _fmt(fraction),
                "not_forwarded_assumed": _fmt(not_forwarded_assumed),
                "unrouted_at_unresolved": _fmt(unrouted_at_unresolved),
                "downstream_out": _fmt(downstream), "boundary_export": _fmt(boundary),
                "residual": _fmt(residual),
                "route_to_huc12": route["to_huc12"] if route else "",
                "routing_basis": route["routing_basis"] if route else "wbd_out_of_extract_boundary",
                "qa_status": route["qa_status"] if route else "BOUNDARY_EXPORT",
                "physical_geometry": route["physical_geometry"] if route else "False",
                "input_status": statuses.get(key, "omitted_zero_diagnostic" if run_status == "synthetic_diagnostic" else run_status),
            })

    summary: list[dict[str, str]] = []
    for constituent in CONSTITUENTS:
        t = totals[constituent]
        residual = t["input"] - t["not_forwarded_assumed"] - t["unrouted_at_unresolved"] - t["boundary"]
        if not _near_zero(residual, t["input"]):
            raise AssertionError(f"Global ledger failed for {constituent}: {residual}")
        summary.append({
            "run_id": run_id, "period": period, "constituent": constituent,
            "unit": UNITS[constituent], "total_local_input": _fmt(t["input"]),
            "total_not_forwarded_assumed": _fmt(t["not_forwarded_assumed"]),
            "total_unrouted_at_unresolved": _fmt(t["unrouted_at_unresolved"]),
            "boundary_export": _fmt(t["boundary"]), "residual": _fmt(residual),
            "unresolved_policy": policy,
        })

    counts = Counter(row["qa_status"] for row in network.routing.values())
    manifest = {
        "model": "Western Basin Model Lab HUC-12 accounting",
        "model_version": "0.1A",
        "purpose": "conditional mass accounting / synthetic diagnostic, not observed loading",
        "run_id": run_id, "period": period, "input_status": run_status,
        "assumption_status": assumption_status,
        "unresolved_policy": policy,
        "topology": {
            "huc_count": len(network.hucs), "link_count": len(network.routing),
            "unresolved_link_count": counts["UNRESOLVED"],
            "terminal_huc12": network.terminal,
            "external_wbd_target": network.external_boundary,
            "accepted_baseline": network.accepted_baseline,
            "routing_qa_counts": dict(sorted(counts.items())),
        },
        "units": UNITS,
        "source_files": {
            "wbd_huc12": {"path": _source_path(network.wbd_path), "sha256": _sha256(network.wbd_path)},
            "qualified_routing": {"path": _source_path(network.routing_path), "sha256": _sha256(network.routing_path)},
            "input": {"path": _source_path(inputs_path), "sha256": _sha256(inputs_path)},
            "assumptions": {"path": _source_path(assumptions_path), "sha256": _sha256(assumptions_path)} if assumptions_path else None,
            "engine_sha256": _sha256(Path(__file__)),
        },
        "interpretation": [
            "HUC-12 is an accounting unit, not a homogeneous catchment or mapped stream.",
            "Default pass-through is one; quantities not forwarded under explicit assumptions are hypothetical accounting dispositions, not observed retention.",
            "Strict unresolved routes leave quantities unrouted in this ledger, not physically stored, treated, or ecologically retained.",
            "Within-period transfer has no travel time or storage dynamics.",
            "Boundary export is a model edge, not a measured Maumee or Lake Erie load.",
            "Unresolved-route pass-through is an explicit WBD sensitivity assumption.",
        ],
    }
    return RunResult(balances, edges, summary, manifest, selected)


def write_run(result: RunResult, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in (
        ("huc_balance.csv", BALANCE_FIELDS, result.balances),
        ("edge_flux.csv", EDGE_FIELDS, result.edges),
        ("boundary_summary.csv", SUMMARY_FIELDS, result.summary),
        ("input_snapshot.csv", INPUT_FIELDS, result.input_rows),
    ):
        with (out_dir / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    (out_dir / "run_manifest.json").write_text(
        json.dumps(result.manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--policy", choices=("strict", "assume_wbd"), default="strict")
    parser.add_argument("--assumptions", type=Path)
    parser.add_argument("--wbd", type=Path, default=DEFAULT_WBD)
    parser.add_argument("--routing", type=Path, default=DEFAULT_ROUTING)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    network = load_network(args.wbd, args.routing)
    result = run_model(args.run_id, args.period, args.inputs, network, args.policy, args.assumptions)
    write_run(result, args.out_dir)
    print(f"Wrote {len(result.balances)} HUC balances and {len(result.edges)} transfers to {args.out_dir}")
    for row in result.summary:
        print(f"{row['constituent']}: input={row['total_local_input']}, unrouted_at_unresolved={row['total_unrouted_at_unresolved']}, boundary={row['boundary_export']} {row['unit']}")


if __name__ == "__main__":
    main()
