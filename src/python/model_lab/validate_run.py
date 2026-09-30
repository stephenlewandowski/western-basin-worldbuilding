"""Independently check a Model Lab v0.1A or v0.1B routing ledger on disk.

This checks arithmetic and structural consistency, not empirical validity. A
closed synthetic ledger is not evidence of observed water or nutrient loads.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

CONSTITUENT_UNITS = {"water": "m3/period", "TN": "kg/period", "TP": "kg/period"}
OUTPUT_FILES = {
    "balances": "huc_balance.csv",
    "edges": "edge_flux.csv",
    "summary": "boundary_summary.csv",
    "inputs": "input_snapshot.csv",
}
BALANCE_FIELDS = (
    "run_id", "period", "huc12", "constituent", "unit", "local_input",
    "upstream_in", "available", "pass_through", "not_forwarded_assumed",
    "unrouted_at_unresolved", "downstream_out", "boundary_export", "residual",
    "route_to_huc12", "routing_basis", "qa_status", "physical_geometry",
    "input_status",
)
EDGE_FIELDS = (
    "run_id", "period", "from_huc12", "to_huc12", "constituent", "unit",
    "amount", "routing_basis", "qa_status", "assumed_unresolved",
)
SUMMARY_FIELDS = (
    "run_id", "period", "constituent", "unit", "total_local_input",
    "total_not_forwarded_assumed", "total_unrouted_at_unresolved",
    "boundary_export", "residual", "unresolved_policy",
)
INPUT_FIELDS = (
    "run_id", "period", "huc12", "constituent", "local_input", "unit",
    "input_status", "source_id", "method", "uncertainty_note",
)
TRACE_FIELDS = (
    "run_id", "period", "unresolved_policy", "focus_huc12", "traced_huc12",
    "hops", "policy_reachable", "first_unresolved_link_from_huc12",
)
SCHEMA_V01B = {
    "huc_balance.csv": BALANCE_FIELDS,
    "edge_flux.csv": EDGE_FIELDS,
    "boundary_summary.csv": SUMMARY_FIELDS,
    "input_snapshot.csv": INPUT_FIELDS,
    "downstream_trace.csv": TRACE_FIELDS,
    "upstream_trace.csv": TRACE_FIELDS,
}
V01A_ENGINE_SHA256 = "0bc7e92dd43278c9b0a8e570fbe4dfe16b94feeea2c4ccfc58bfa8ccfcc62893"
BALANCE_AMOUNTS = (
    "local_input", "upstream_in", "available", "not_forwarded_assumed",
    "unrouted_at_unresolved", "downstream_out", "boundary_export",
)
SUMMARY_AMOUNTS = (
    "total_local_input", "total_not_forwarded_assumed", "total_unrouted_at_unresolved",
    "boundary_export",
)
ROUTING_CLASSES = {
    ("REPLACED_PHYSICAL", "physical_3dhp"),
    ("REPLACED_AUTHORITATIVE_CONNECTOR", "official_3dhp_connector"),
    ("ALREADY_REDUNDANT", "physical_nhdplus_hr_existing"),
    ("UNRESOLVED", "project_inference"),
}
INPUT_STATUSES = {"synthetic_diagnostic", "parameterized", "observed_derived"}
REPO_ROOT = Path(__file__).resolve().parents[3]


def _near(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= max(Decimal("0.000000001"), max(abs(a), abs(b)) * Decimal("0.000000000001"))


def _read_csv(path: Path, errors: list[str], expected_fields: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    if not path.is_file():
        errors.append(f"Missing output file: {path.name}")
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                errors.append(f"CSV has no header: {path.name}")
                return []
            if expected_fields is not None and tuple(reader.fieldnames) != expected_fields:
                errors.append(f"{path.name}: header differs from v0.1B schema")
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"Cannot read {path.name}: {exc}")
        return []


def _decimal(row: dict[str, str], field: str, where: str, errors: list[str], *, nonnegative: bool = True) -> Decimal:
    raw = row.get(field)
    if raw is None or raw.strip() == "":
        errors.append(f"{where}: missing {field}")
        return Decimal(0)
    try:
        value = Decimal(raw)
    except InvalidOperation:
        errors.append(f"{where}: invalid {field}={raw!r}")
        return Decimal(0)
    if not value.is_finite():
        errors.append(f"{where}: nonfinite {field}={raw!r}")
        return Decimal(0)
    if nonnegative and value < 0:
        errors.append(f"{where}: negative {field}={raw!r}")
    return value


def _equal(actual: Decimal, expected: Decimal, where: str, errors: list[str]) -> None:
    if not _near(actual, expected):
        errors.append(f"{where}: got {actual}, expected {expected}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_sources(manifest: dict, errors: list[str]) -> None:
    sources = manifest.get("source_files")
    if not isinstance(sources, dict):
        errors.append("Manifest source_files must be an object")
        return
    version = manifest.get("model_version")
    for name in ("wbd_huc12", "qualified_routing", "input", "assumptions", "sensitivity_config"):
        entry = sources.get(name)
        if name in ("assumptions", "sensitivity_config") and entry is None and name in sources:
            continue
        if name == "sensitivity_config" and version == "0.1A":
            continue
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            errors.append(f"Manifest source_files.{name} needs path and sha256")
            continue
        source_path = Path(entry["path"])
        if not source_path.is_absolute():
            source_path = REPO_ROOT / source_path
        try:
            actual = _sha256(source_path)
        except OSError as exc:
            errors.append(f"Cannot read source_files.{name} at {source_path}: {exc}")
            continue
        if actual != entry["sha256"].lower():
            errors.append(f"Source hash mismatch for {name}: {source_path}")
    recorded_engine = sources.get("engine_sha256")
    if not isinstance(recorded_engine, str):
        errors.append("Manifest source_files.engine_sha256 is missing")
    elif version == "0.1A":
        if recorded_engine.lower() != V01A_ENGINE_SHA256:
            errors.append("Historical v0.1A engine source hash mismatch")
    else:
        engine_path = Path(__file__).with_name("route_water_nutrients.py")
        try:
            if _sha256(engine_path) != recorded_engine.lower():
                errors.append(f"Engine source hash mismatch: {engine_path}")
        except OSError as exc:
            errors.append(f"Cannot read engine source at {engine_path}: {exc}")
    if version == "0.1B":
        recorded_trace = sources.get("trace_generator_sha256")
        if not isinstance(recorded_trace, str):
            errors.append("Manifest source_files.trace_generator_sha256 is missing")
        else:
            trace_path = Path(__file__).with_name("trace_huc_paths.py")
            try:
                if _sha256(trace_path) != recorded_trace.lower():
                    errors.append(f"Trace generator source hash mismatch: {trace_path}")
            except OSError as exc:
                errors.append(f"Cannot read trace generator source at {trace_path}: {exc}")


def _validate_v01b_schema(manifest: dict, errors: list[str]) -> None:
    if manifest.get("schema_version") != "0.1B":
        errors.append("v0.1B manifest needs schema_version 0.1B")
    declared = manifest.get("output_schema")
    expected = {name: list(fields) for name, fields in SCHEMA_V01B.items()}
    if declared != expected:
        errors.append("v0.1B output_schema does not match the stable ordered CSV contract")


def _resolve_source_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else REPO_ROOT / path


def _validate_sensitivity_config(manifest: dict, run_dir: Path, errors: list[str]) -> None:
    sources = manifest.get("source_files", {})
    config_source = sources.get("sensitivity_config") if isinstance(sources, dict) else None
    metadata = manifest.get("sensitivity_case")
    if config_source is None:
        if metadata is not None:
            errors.append("sensitivity_case metadata requires a sensitivity config source")
        return
    if not isinstance(config_source, dict) or not isinstance(config_source.get("path"), str):
        errors.append("Invalid sensitivity config provenance")
        return
    if not isinstance(metadata, dict) or set(metadata) != {"label", "description"} or any(
        not isinstance(metadata[field], str) or not metadata[field].strip()
        for field in ("label", "description")
    ):
        errors.append("Configured run needs nonempty sensitivity_case label and description")
        return
    path = _resolve_source_path(config_source["path"])
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read sensitivity config: {exc}")
        return
    if not isinstance(config, dict) or config.get("config_version") != "0.1B":
        errors.append("Sensitivity config must declare config_version 0.1B")
        return
    cases = config.get("runs")
    if not isinstance(cases, list):
        errors.append("Sensitivity config runs must be a list")
        return
    matches = [case for case in cases if isinstance(case, dict) and case.get("run_id") == manifest.get("run_id")]
    if len(matches) != 1:
        errors.append("Manifest run_id must identify exactly one sensitivity case")
        return
    case = matches[0]
    if config.get("period") != manifest.get("period"):
        errors.append("Sensitivity config period differs from manifest")
    if case.get("unresolved_policy") != manifest.get("unresolved_policy"):
        errors.append("Sensitivity config unresolved policy differs from manifest")
    if {"label": case.get("label"), "description": case.get("description")} != metadata:
        errors.append("Sensitivity config case metadata differs from manifest")
    if not isinstance(case.get("out_dir"), str) or _resolve_source_path(case["out_dir"]).resolve() != run_dir.resolve():
        errors.append("Sensitivity config output directory differs from run directory")
    for config_key, source_key in (
        ("inputs", "input"), ("wbd", "wbd_huc12"), ("routing", "qualified_routing"),
    ):
        entry = sources.get(source_key)
        value = config.get(config_key)
        if not isinstance(value, str) or not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or (
            _resolve_source_path(value).resolve() != _resolve_source_path(entry["path"]).resolve()
        ):
            errors.append(f"Sensitivity config {config_key} path differs from manifest source")
    assumption = case.get("assumptions")
    entry = sources.get("assumptions")
    if assumption is None:
        if entry is not None:
            errors.append("Sensitivity config declares no assumptions but manifest has a source")
    elif not isinstance(assumption, str) or not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or (
        _resolve_source_path(assumption).resolve() != _resolve_source_path(entry["path"]).resolve()
    ):
        errors.append("Sensitivity config assumptions path differs from manifest source")


def _validate_traces(
    tables: dict[str, list[dict[str, str]]],
    balances: dict[str, dict[str, dict[str, str]]],
    run_id: str, period: str, policy: str,
    errors: list[str],
) -> None:
    """Reconstruct every path from ledger successors, independent of writer."""
    routes = {
        huc: (row.get("route_to_huc12", ""), row.get("qa_status", ""))
        for huc, row in balances.get("water", {}).items()
    }
    if not routes or any(target and target not in routes for target, _ in routes.values()):
        errors.append("Trace validation needs a complete internal HUC successor graph")
        return
    expected: dict[str, dict[tuple[str, str], tuple[str, str, str]]] = {
        "downstream_trace.csv": {}, "upstream_trace.csv": {},
    }
    for origin in routes:
        current, hops, first_cut = origin, 0, ""
        seen: set[str] = set()
        while current:
            if current in seen:
                errors.append(f"Trace source topology has a cycle at {current}")
                return
            seen.add(current)
            value = (str(hops), str(policy == "assume_wbd" or not first_cut), first_cut)
            expected["downstream_trace.csv"][(origin, current)] = value
            expected["upstream_trace.csv"][(current, origin)] = value
            target, qa = routes[current]
            if qa == "UNRESOLVED" and not first_cut:
                first_cut = current
            current, hops = target, hops + 1
    for filename, expected_rows in expected.items():
        seen_keys: set[tuple[str, str]] = set()
        for index, row in enumerate(tables[filename], 2):
            where = f"{filename}:{index}"
            key = (row.get("focus_huc12", ""), row.get("traced_huc12", ""))
            if row.get("run_id") != run_id or row.get("period") != period or row.get("unresolved_policy") != policy:
                errors.append(f"{where}: run identity or policy differs from manifest")
            if key in seen_keys:
                errors.append(f"{where}: duplicate trace pair")
            seen_keys.add(key)
            actual = (row.get("hops"), row.get("policy_reachable"), row.get("first_unresolved_link_from_huc12"))
            if expected_rows.get(key) != actual:
                errors.append(f"{where}: path, hop count, unresolved cut, or policy reachability differs from topology")
        if seen_keys != set(expected_rows):
            errors.append(f"{filename}: trace pair coverage differs from complete topology paths")


def validate_run(run_dir: Path) -> list[str]:
    """Return problems found in one written run; an empty list means consistent.

    The validator reads output files afresh and recomputes local, edge, and
    global identities. It never trusts a stored residual as proof of closure.
    """
    errors: list[str] = []
    manifest_path = run_dir / "run_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be an object")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"Cannot read run_manifest.json: {exc}"]
    version = manifest.get("model_version")
    if version not in ("0.1A", "0.1B"):
        errors.append(f"Unknown Model Lab model_version: {version!r}")
        return errors
    _validate_sources(manifest, errors)
    if version == "0.1B":
        _validate_v01b_schema(manifest, errors)
        _validate_sensitivity_config(manifest, run_dir, errors)
    tables = {
        name: _read_csv(
            run_dir / filename, errors,
            SCHEMA_V01B[filename] if version == "0.1B" else None,
        )
        for name, filename in OUTPUT_FILES.items()
    }
    if version == "0.1B":
        for filename in ("downstream_trace.csv", "upstream_trace.csv"):
            tables[filename] = _read_csv(run_dir / filename, errors, SCHEMA_V01B[filename])
    if errors:
        return errors

    run_id = manifest.get("run_id")
    period = manifest.get("period")
    policy = manifest.get("unresolved_policy")
    topology = manifest.get("topology")
    if not isinstance(run_id, str) or not run_id or not isinstance(period, str) or not period:
        errors.append("Manifest must declare a nonempty run_id and period")
    if policy not in {"strict", "assume_wbd"}:
        errors.append(f"Unknown unresolved_policy: {policy!r}")
    if not isinstance(topology, dict):
        errors.append("Manifest must declare topology counts and terminal HUC")
        topology = {}
    terminal = topology.get("terminal_huc12")

    balances = tables["balances"]
    edges = tables["edges"]
    summaries = tables["summary"]
    inputs = tables["inputs"]
    if not balances:
        errors.append("huc_balance.csv has no rows")
        return errors

    by_constituent: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    balance_amount: dict[tuple[str, str], dict[str, Decimal]] = {}
    hucs: set[str] = set()
    for index, row in enumerate(balances, 2):
        where = f"huc_balance.csv:{index}"
        constituent = row.get("constituent", "")
        huc = row.get("huc12", "")
        if constituent not in CONSTITUENT_UNITS or not huc:
            errors.append(f"{where}: unknown constituent or empty HUC")
            continue
        if row.get("run_id") != run_id or row.get("period") != period:
            errors.append(f"{where}: run_id/period differs from manifest")
        if row.get("unit") != CONSTITUENT_UNITS[constituent]:
            errors.append(f"{where}: wrong unit for {constituent}")
        if huc in by_constituent[constituent]:
            errors.append(f"{where}: duplicate HUC/constituent row")
            continue
        by_constituent[constituent][huc] = row
        hucs.add(huc)
        amounts = {name: _decimal(row, name, where, errors) for name in BALANCE_AMOUNTS}
        residual = _decimal(row, "residual", where, errors, nonnegative=False)
        fraction = _decimal(row, "pass_through", where, errors)
        if fraction > 1:
            errors.append(f"{where}: pass_through exceeds one")
        balance_amount[(constituent, huc)] = amounts
        _equal(amounts["available"], amounts["local_input"] + amounts["upstream_in"], f"{where} available", errors)
        _equal(amounts["not_forwarded_assumed"], amounts["available"] * (1 - fraction),
               f"{where} quantity not forwarded under assumption", errors)
        calculated = (amounts["local_input"] + amounts["upstream_in"]
                      - amounts["not_forwarded_assumed"] - amounts["unrouted_at_unresolved"]
                      - amounts["downstream_out"] - amounts["boundary_export"])
        _equal(calculated, Decimal(0), f"{where} node balance", errors)
        _equal(residual, calculated, f"{where} stored residual", errors)

        route_to = row.get("route_to_huc12", "")
        qa = row.get("qa_status", "")
        basis = row.get("routing_basis", "")
        if huc != terminal:
            if route_to == "":
                errors.append(f"{where}: nonterminal HUC has no successor")
            if (qa, basis) not in ROUTING_CLASSES:
                errors.append(f"{where}: unrecognized routing class {qa}/{basis}")
            expected_geometry = "True" if qa in {"REPLACED_PHYSICAL", "ALREADY_REDUNDANT"} else "False"
            if row.get("physical_geometry") != expected_geometry:
                errors.append(f"{where}: physical geometry contradicts routing class")
        elif route_to or qa != "BOUNDARY_EXPORT":
            errors.append(f"{where}: terminal must be boundary export without an internal successor")
        if route_to and qa == "UNRESOLVED" and policy == "strict":
            _equal(amounts["downstream_out"], Decimal(0), f"{where} strict unresolved transfer", errors)
            _equal(amounts["unrouted_at_unresolved"], amounts["available"] - amounts["not_forwarded_assumed"],
                   f"{where} strict unrouted quantity", errors)
        if route_to and qa == "UNRESOLVED" and policy == "assume_wbd":
            _equal(amounts["unrouted_at_unresolved"], Decimal(0),
                   f"{where} assumed WBD successor unrouted quantity", errors)
            _equal(amounts["downstream_out"], amounts["available"] - amounts["not_forwarded_assumed"],
                   f"{where} assumed WBD successor transfer", errors)
        if qa != "UNRESOLVED" and amounts["unrouted_at_unresolved"] != 0:
            errors.append(f"{where}: unrouted quantity at a non-unresolved HUC")

    for constituent in CONSTITUENT_UNITS:
        if set(by_constituent[constituent]) != hucs:
            errors.append(f"{constituent}: balance rows do not cover every HUC")
    if terminal not in hucs:
        errors.append(f"Terminal HUC absent from balances: {terminal!r}")
    if len({huc for huc in hucs if by_constituent.get("water", {}).get(huc, {}).get("route_to_huc12") == ""}) != 1:
        errors.append("Network must have exactly one terminal HUC")
    for huc in hucs:
        routes = {
            (row.get("route_to_huc12"), row.get("routing_basis"), row.get("qa_status"), row.get("physical_geometry"))
            for by_huc in by_constituent.values() if (row := by_huc.get(huc)) is not None
        }
        if len(routes) > 1:
            errors.append(f"{huc}: route metadata differ across constituents")
    for constituent, by_huc in by_constituent.items():
        for huc, row in by_huc.items():
            boundary = balance_amount[(constituent, huc)]["boundary_export"]
            if huc != terminal and boundary != 0:
                errors.append(f"{constituent}/{huc}: boundary export outside terminal HUC")
            if huc == terminal and balance_amount[(constituent, huc)]["downstream_out"] != 0:
                errors.append(f"{constituent}/{huc}: terminal has downstream transfer")

    # Edge entries are the independent source of actual HUC-to-HUC transfers.
    outgoing: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    incoming: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    edge_keys: set[tuple[str, str, str]] = set()
    for index, row in enumerate(edges, 2):
        where = f"edge_flux.csv:{index}"
        constituent = row.get("constituent", "")
        source = row.get("from_huc12", "")
        target = row.get("to_huc12", "")
        if constituent not in CONSTITUENT_UNITS or source not in hucs or target not in hucs:
            errors.append(f"{where}: invalid constituent or edge HUC")
            continue
        if row.get("run_id") != run_id or row.get("period") != period:
            errors.append(f"{where}: run_id/period differs from manifest")
        if row.get("unit") != CONSTITUENT_UNITS[constituent]:
            errors.append(f"{where}: wrong unit for {constituent}")
        key = (constituent, source, target)
        if key in edge_keys:
            errors.append(f"{where}: duplicate edge/constituent")
        edge_keys.add(key)
        source_row = by_constituent[constituent].get(source, {})
        if source_row.get("route_to_huc12") != target:
            errors.append(f"{where}: edge contradicts qualified route")
        if policy == "strict" and source_row.get("qa_status") == "UNRESOLVED":
            errors.append(f"{where}: strict policy routed across unresolved edge")
        amount = _decimal(row, "amount", where, errors)
        outgoing[(constituent, source)] += amount
        incoming[(constituent, target)] += amount
    for key, amounts in balance_amount.items():
        _equal(amounts["downstream_out"], outgoing[key], f"{key} edge out", errors)
        _equal(amounts["upstream_in"], incoming[key], f"{key} edge in", errors)

    # Snapshot must explain every local input; absent synthetic rows are zero.
    snapshot: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    input_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(inputs, 2):
        where = f"input_snapshot.csv:{index}"
        constituent, huc = row.get("constituent", ""), row.get("huc12", "")
        if constituent not in CONSTITUENT_UNITS or huc not in hucs:
            errors.append(f"{where}: invalid constituent or HUC")
            continue
        if row.get("run_id") != run_id or row.get("period") != period:
            errors.append(f"{where}: run_id/period differs from manifest")
        if row.get("unit") != CONSTITUENT_UNITS[constituent]:
            errors.append(f"{where}: wrong unit for {constituent}")
        if row.get("input_status") not in INPUT_STATUSES:
            errors.append(f"{where}: unrecognized input status")
        if not row.get("source_id") or not row.get("method"):
            errors.append(f"{where}: missing input provenance")
        key = (constituent, huc)
        if key in input_keys:
            errors.append(f"{where}: duplicate HUC/constituent input")
        input_keys.add(key)
        snapshot[key] += _decimal(row, "local_input", where, errors)
    for key, amounts in balance_amount.items():
        _equal(amounts["local_input"], snapshot[key], f"{key} input snapshot", errors)

    summary_by_constituent: dict[str, dict[str, str]] = {}
    for index, row in enumerate(summaries, 2):
        where = f"boundary_summary.csv:{index}"
        constituent = row.get("constituent", "")
        if constituent not in CONSTITUENT_UNITS:
            errors.append(f"{where}: unknown constituent")
            continue
        if constituent in summary_by_constituent:
            errors.append(f"{where}: duplicate constituent summary")
        summary_by_constituent[constituent] = row
        if row.get("run_id") != run_id or row.get("period") != period:
            errors.append(f"{where}: run_id/period differs from manifest")
        if row.get("unit") != CONSTITUENT_UNITS[constituent]:
            errors.append(f"{where}: wrong unit for {constituent}")
        if row.get("unresolved_policy") != policy:
            errors.append(f"{where}: unresolved policy differs from manifest")
        totals = {name: _decimal(row, name, where, errors) for name in SUMMARY_AMOUNTS}
        totals["residual"] = _decimal(row, "residual", where, errors, nonnegative=False)
        matching = [balance_amount[(constituent, huc)] for huc in by_constituent[constituent]]
        for summary_name, balance_name in (
            ("total_local_input", "local_input"),
            ("total_not_forwarded_assumed", "not_forwarded_assumed"),
            ("total_unrouted_at_unresolved", "unrouted_at_unresolved"),
            ("boundary_export", "boundary_export"),
        ):
            _equal(totals[summary_name], sum((part[balance_name] for part in matching), Decimal(0)),
                   f"{where} {summary_name}", errors)
        calculated = (totals["total_local_input"] - totals["total_not_forwarded_assumed"]
                      - totals["total_unrouted_at_unresolved"] - totals["boundary_export"])
        _equal(calculated, Decimal(0), f"{where} global balance", errors)
        _equal(totals["residual"], calculated, f"{where} stored residual", errors)
    if set(summary_by_constituent) != set(CONSTITUENT_UNITS):
        errors.append("Summary must contain exactly water, TN, and TP")

    # The accepted source topology has 252 HUCs, 251 internal links and 12
    # unresolved project inferences. These are structural checks, not loads.
    linked = {huc for huc in hucs if any(
        by_constituent[c].get(huc, {}).get("route_to_huc12") in hucs
        for c in CONSTITUENT_UNITS
    )}
    unresolved = {huc for huc in hucs if any(
        by_constituent[c].get(huc, {}).get("qa_status") == "UNRESOLVED"
        for c in CONSTITUENT_UNITS
    )}
    for field, count in (("huc_count", len(hucs)), ("link_count", len(linked)),
                         ("unresolved_link_count", len(unresolved))):
        declared = topology.get(field)
        if declared != count:
            errors.append(f"Topology {field}: manifest {declared!r}, balance rows {count}")
    if topology.get("accepted_baseline") is True:
        if (len(hucs), len(linked), len(unresolved), terminal) != (252, 251, 12, "041000090904"):
            errors.append("Accepted baseline topology differs from 252 HUCs / 251 links / 12 unresolved / terminal 041000090904")
    if version == "0.1B":
        _validate_traces(tables, by_constituent, run_id, period, policy, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="Directory containing one written Model Lab run")
    args = parser.parse_args(argv)
    errors = validate_run(args.run_dir)
    if errors:
        for problem in errors:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"PASS: Model Lab ledger and topology consistency: {args.run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
