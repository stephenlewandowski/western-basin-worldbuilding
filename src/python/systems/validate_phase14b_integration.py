"""Deterministic Phase 14B validator with Phase 14A freeze readback."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
BASE_SHA = "dd2c0706f8d1f6b73974a530e64de8a82aff2eb1"
ONTOLOGY = ROOT / "metadata/atlas_systems.yml"
EVIDENCE = ROOT / "metadata/atlas_evidence_vocabulary.yml"
LAYERS = ROOT / "metadata/atlas_layers.yml"
VOCAB = ROOT / "metadata/atlas_relationship_vocabulary.yml"
RELATIONSHIPS = ROOT / "data/processed/integration/relationship_normalization_crosswalk.csv"
ENDPOINT_ROLES = ROOT / "data/processed/integration/endpoint_role_crosswalk.csv"
DEPENDENCIES = ROOT / "data/processed/integration/atlas_dependency_crosswalk.csv"
MATRIX = ROOT / "data/processed/integration/system_joinability_matrix.csv"
A14A_FINAL = ROOT / "reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
A14A_WORKING = ROOT / "reports/phase14a_manifest.json"
MANIFEST = ROOT / "reports/phase14b_manifest.json"
CHECK = ROOT / "reports/phase14b_artifact_check.json"
R_RESULT = ROOT / "reports/phase14b_r_validation_result.json"
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".r", ".R", ".yml", ".yaml", ".svg", ".txt"}
VALID_PHASES = {"1", "2A", "2B", "2C", "2D", "3A", "3B", "3C", "4A", "4B", "4C", "5A", "5B", "5C", "6A", "6B", "6C", "7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B", "9C", "10A", "10B", "10C", "11A", "11B", "11C", "12A", "12B", "12C", "13A", "13B", "13C", "14A", "14B", "1/2"}
VALID_RELATIONSHIP_CLASSES = {"physical flow", "material flow", "energy flow", "information / observation", "governance / authority", "operational dependency", "ecological relationship", "exposure pathway", "population / mobility interface", "surveillance / detection", "scenario influence", "high-level association", "unresolved / unclassified"}
VALID_ENDPOINT_ROLES = {"physical asset", "geographic unit", "system node", "institutional actor", "ecological entity", "population/settlement entity", "monitoring/surveillance interface", "generalized external interface", "conceptual interface", "scenario-only entity"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def normalize_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hash(path: Path, expected: Any) -> bool:
    expected_hash = expected if isinstance(expected, str) else str(expected.get("sha256", ""))
    raw = path.read_bytes()
    if digest(raw) == expected_hash:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES and digest(normalize_text(raw)) == expected_hash


def entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    return value if isinstance(value, dict) else {}


def source_rows(root: Path, rel: str) -> list[dict[str, str]]:
    return read_csv(root / rel)[1]


def main() -> int:
    checks: dict[str, dict[str, object]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    ontology = yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8"))
    evidence = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
    vocabulary = yaml.safe_load(VOCAB.read_text(encoding="utf-8"))
    system_ids = {item["system_id"] for item in ontology["systems"]}
    evidence_classes = {item["class_id"] for item in evidence["normalized_classes"]}
    changed = [line.replace("\\", "/") for line in subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines()]
    check("ontology_system_count", len(system_ids) == 13, len(system_ids))
    check("valid_changed_scope", not any("phase15" in path.lower() or path.endswith(".gpkg") and path != "data/processed/glasspunk_base.gpkg" for path in changed), [p for p in changed if "phase15" in p.lower()])
    check("original_system_registry_untouched", "metadata/systems.yml" not in changed, changed)
    check("no_phase1_13_freeze_manifest_modified", not any(path.endswith("freeze_manifest.json") and "phase14b" not in path.lower() for path in changed), [p for p in changed if p.endswith("freeze_manifest.json")])

    layer_payload = yaml.safe_load(LAYERS.read_text(encoding="utf-8"))
    layer_rows = layer_payload.get("layer_registry", [])
    layer_ids = [row.get("atlas_layer_id", "") for row in layer_rows]
    layer_missing = [row.get("source_artifact", "") for row in layer_rows if not (ROOT / row.get("source_artifact", "")).exists()]
    layer_bad_systems = sorted({row.get("system_id", "") for row in layer_rows if row.get("system_id") not in system_ids})
    layer_bad_phases = sorted({row.get("source_phase", "") for row in layer_rows if row.get("source_phase") not in VALID_PHASES})
    check("layer_registry_nonempty", len(layer_rows) > 0, len(layer_rows))
    check("layer_ids_unique", len(layer_ids) == len(set(layer_ids)) and all(layer_ids), len(layer_ids))
    check("registered_artifacts_exist", not layer_missing, layer_missing[:10])
    check("registered_system_ids_resolve", not layer_bad_systems, layer_bad_systems)
    check("registered_source_phases_valid", not layer_bad_phases, layer_bad_phases)
    check("registry_multiple_formats", len({row.get("physical_format") for row in layer_rows}) >= 4, sorted({row.get("physical_format") for row in layer_rows}))
    check("registry_geometry_semantics", all(row.get("geometry_type") for row in layer_rows), "blank geometry/nonspatial field")
    check("registry_provenance_and_limits", all(row.get("provenance_pointer") and row.get("limitations") for row in layer_rows), "blank provenance or limitation")

    rel_fields, rel_rows = read_csv(RELATIONSHIPS)
    rel_inventory_fields, rel_inventory = read_csv(ROOT / "data/processed/integration/relationship_taxonomy_inventory.csv")
    inventory_keys = {(row["taxonomy_id"], row["source_artifact"], row["local_field"], row["local_term"]) for row in rel_inventory}
    rel_keys = {(row["local_taxonomy_id"], row["source_artifact"], row["local_field"], row["local_term"]) for row in rel_rows}
    check("relationship_rows_retain_14A_inventory", len(rel_rows) == 367 and rel_keys == inventory_keys, {"normalized": len(rel_rows), "inventory": len(rel_inventory)})
    check("relationship_normalization_ids_unique", len({row["atlas_normalization_id"] for row in rel_rows}) == len(rel_rows), len(rel_rows))
    check("relationship_classes_valid", set(row["normalized_relationship_class"] for row in rel_rows).issubset(VALID_RELATIONSHIP_CLASSES), sorted(set(row["normalized_relationship_class"] for row in rel_rows) - VALID_RELATIONSHIP_CLASSES))
    check("relationship_caveats_present", all(row["information_loss_or_caveat"] for row in rel_rows), "blank caveat")
    check("relationship_lineage_present", all(row["source_phase"] in {r["source_phase"] for r in rel_inventory} and row["source_artifact"] and row["local_term"] for row in rel_rows), "missing source lineage")
    check("relationship_semantic_fields_present", all(row["directionality"] and row["causal_semantics"] and row["flow_semantics"] and row["Atlas_join_role"] and row["mapping_status"] for row in rel_rows), "missing normalized semantic field")

    energy = [row for row in rel_rows if row["source_phase"] == "3"]
    energy_by_term = {row["local_term"].lower(): row["normalized_relationship_class"] for row in energy}
    check("energy_generation_interfaces_preserved", all(energy_by_term.get(term) == "energy flow" for term in ("generation_grid_interface", "regional_grid_interface", "bidirectional_storage_interface") if term in energy_by_term), energy_by_term)
    check("energy_fuel_is_material_input", energy_by_term.get("fuel") in {"material flow", None}, energy_by_term.get("fuel"))
    check("energy_control_information_not_energy_flow", energy_by_term.get("communications") != "energy flow", energy_by_term.get("communications"))
    check("energy_operational_dependencies_preserved", all(energy_by_term.get(term) in {"operational dependency", None} for term in ("electricity", "grid_serves_load", "grid_serves_planned_compute", "cooling_water", "thermal_dependency", "storage_support")), energy_by_term)

    endpoint_fields, endpoint_rows = read_csv(ENDPOINT_ROLES)
    check("endpoint_role_rows_and_ids", len(endpoint_rows) == 36 and len({row["endpoint_role_crosswalk_id"] for row in endpoint_rows}) == 36, len(endpoint_rows))
    check("endpoint_roles_valid", set(row["endpoint_role"] for row in endpoint_rows).issubset(VALID_ENDPOINT_ROLES), sorted(set(row["endpoint_role"] for row in endpoint_rows) - VALID_ENDPOINT_ROLES))
    check("conceptual_endpoints_preserved", all(row["conceptual_endpoint_preserved"] == "yes" and row["role_mapping_status"] == "normalized_role_only" for row in endpoint_rows), "conceptual endpoint role changed to identity")
    check("endpoint_result_preserved", Counter(row["inherited_mapping_status"] for row in endpoint_rows) == Counter({"resolved_system_level": 34, "retained_conceptual": 2}), dict(Counter(row["inherited_mapping_status"] for row in endpoint_rows)))
    check("generalized_endpoints_not_localized", all(row["inherited_mapping_status"] != "retained_conceptual" or row["endpoint_role"] == "generalized external interface" for row in endpoint_rows), "retained endpoint localized")

    dep_fields, dep_rows = read_csv(DEPENDENCIES)
    required_dep = {"atlas_relationship_id", "source_phase", "source_artifact", "local_relationship_id", "source_atlas_entity_id", "target_atlas_entity_id", "source_system_id", "target_system_id", "normalized_relationship_class", "endpoint_role_source", "endpoint_role_target", "evidence_class", "documented_or_inferred", "source_id", "evidence_strength", "confidence", "uncertainty_id", "directionality", "spatial_scale", "temporal_basis", "scenario_status", "Atlas_use", "caveat"}
    check("dependency_required_fields", required_dep.issubset(dep_fields), sorted(required_dep - set(dep_fields)))
    check("dependency_ids_unique", len({row["atlas_relationship_id"] for row in dep_rows}) == len(dep_rows), len(dep_rows))
    dep_artifacts = sorted({row["source_artifact"] for row in dep_rows})
    source_cache: dict[str, list[dict[str, str]]] = {}
    local_index: dict[tuple[str, str], dict[str, str]] = {}
    source_errors = []
    for artifact in dep_artifacts:
        path = ROOT / artifact
        if not path.exists(): source_errors.append(f"missing:{artifact}"); continue
        source_cache[artifact] = source_rows(ROOT, artifact)
        for source in source_cache[artifact]:
            local = next((source.get(field, "").strip() for field in ("dependency_id", "edge_id", "relationship_id", "register_id") if source.get(field)), "")
            if local: local_index[(artifact, local)] = source
    unresolved_local = [f"{row['source_artifact']}:{row['local_relationship_id']}" for row in dep_rows if (row["source_artifact"], row["local_relationship_id"]) not in local_index]
    check("dependency_source_artifacts_exist", not source_errors, source_errors)
    check("dependency_local_relationship_ids_resolve", not unresolved_local, unresolved_local[:10])
    check("dependency_system_ids_resolve", all(row["source_system_id"] in system_ids and row["target_system_id"] in system_ids for row in dep_rows if row["source_system_id"] and row["target_system_id"]), sorted({x for row in dep_rows for x in (row["source_system_id"], row["target_system_id"]) if x and x not in system_ids}))
    check("dependency_evidence_classes_resolve", set(row["evidence_class"] for row in dep_rows).issubset(evidence_classes), sorted(set(row["evidence_class"] for row in dep_rows) - evidence_classes))
    check("documented_inferred_distinction_retained", all(row["documented_or_inferred"] for row in dep_rows) and all(row["evidence_class"] in evidence_classes for row in dep_rows), sorted({row["documented_or_inferred"] for row in dep_rows}))
    check("dependency_scenario_baseline_retained", set(row["scenario_status"] for row in dep_rows) == {"BASELINE_DEPENDENCY"}, sorted({row["scenario_status"] for row in dep_rows}))
    check("dependency_roles_valid", set(row["endpoint_role_source"] for row in dep_rows).issubset(VALID_ENDPOINT_ROLES) and set(row["endpoint_role_target"] for row in dep_rows).issubset(VALID_ENDPOINT_ROLES), "invalid dependency endpoint role")
    entity_errors = []
    for row in dep_rows:
        for side in ("source", "target"):
            level, value = row[f"{side}_join_level"], row[f"{side}_atlas_entity_id"]
            if level == "exact" and not value.startswith("ENT-"): entity_errors.append(f"{row['atlas_relationship_id']}:{side}:exact:{value}")
            if level == "system-level" and value and not value.startswith("SYS-"): entity_errors.append(f"{row['atlas_relationship_id']}:{side}:system:{value}")
            if level == "conceptual" and not value.startswith(("EXT-", "REF-", "SYS-")): entity_errors.append(f"{row['atlas_relationship_id']}:{side}:conceptual:{value}")
    check("atlas_entity_and_system_join_keys_are_typed", not entity_errors, entity_errors[:10])
    check("exact_and_system_level_joins_distinct", not any(row["source_join_level"] == "exact" and row["source_atlas_entity_id"].startswith("SYS-") or row["target_join_level"] == "exact" and row["target_atlas_entity_id"].startswith("SYS-") for row in dep_rows), "system ID used as exact entity")
    pop = [row for row in dep_rows if row["source_phase"] == "11B"]
    check("population_high_inference_counts", len(pop) == 520 and sum(row["evidence_class"] == "INFERRED" for row in pop) == 468 and sum(row["evidence_class"] == "CONTEXT_REUSED" for row in pop) == 52, {"total": len(pop), "inferred": sum(row["evidence_class"] == "INFERRED" for row in pop), "context": sum(row["evidence_class"] == "CONTEXT_REUSED" for row in pop)})
    check("population_use_rules", all("QUALITATIVE_STRESS_TEST_ONLY" in row["Atlas_use"] and "NO_QUANTITATIVE_AGGREGATION" in row["Atlas_use"] for row in pop), "population use rule missing")
    check("no_numeric_confidence_added", not any("numeric confidence" in row["caveat"].lower() for row in pop), "numeric confidence claim")
    check("dependency_lineage_complete", all(row["source_phase"] and row["source_artifact"] and row["local_relationship_id"] and row["caveat"] for row in dep_rows), "dependency lineage/caveat incomplete")
    check("dependency_source_ids_retained", all(row["source_id"] for row in dep_rows), "blank source_id")
    check("generalized_and_context_roles_not_exact", not any(row["source_local_endpoint_id"] in {"FRT-FUEL-EXTERNAL", "FRT-MKT-GREAT-LAKES", "FRT-MKT-MIDWEST-INDUSTRIAL", "FRT-MKT-MICHIGAN-CANADA", "FRT-MKT-LICENSED-DISPOSAL", "FRT-AG-MIDWEST-BULK", "HZ-019", "HZ-022", "HZ-023"} and row["source_join_level"] == "exact" for row in dep_rows) and not any(row["target_local_endpoint_id"] in {"FRT-FUEL-EXTERNAL", "FRT-MKT-GREAT-LAKES", "FRT-MKT-MIDWEST-INDUSTRIAL", "FRT-MKT-MICHIGAN-CANADA", "FRT-MKT-LICENSED-DISPOSAL", "FRT-AG-MIDWEST-BULK", "HZ-019", "HZ-022", "HZ-023"} and row["target_join_level"] == "exact" for row in dep_rows), "generalized/context endpoint marked exact")

    matrix_fields, matrix_rows = read_csv(MATRIX)
    check("joinability_pair_count", len(matrix_rows) == 78, len(matrix_rows))
    check("joinability_has_no_score", not any(field.lower() in {"score", "connectivity_score", "risk_score"} for field in matrix_fields), matrix_fields)
    check("joinability_no_colocation_causation", all(row["spatial_colocation_only"] == "NO" and "co-location is not treated as causation" in row["caveat"].lower() for row in matrix_rows), "co-location rule missing")
    check("joinability_findings_are_boolean", all(row[field] in {"YES", "NO"} for row in matrix_rows for field in ("direct_exact_identity_join", "system_level_conceptual_join", "dependency_relationship_join", "spatial_colocation_only", "scenario_layer_reference", "scenario_only_link", "no_defensible_current_join")), "non-boolean matrix status")
    check("scenario_reference_and_exclusive_flags_distinct", all(row["scenario_only_link"] == "NO" or row["dependency_relationship_join"] == "NO" for row in matrix_rows), "scenario-only flag overlaps baseline dependency")
    check("matrix_not_risk_matrix", not any(field.lower() in {"score", "connectivity_score", "risk_score", "composite_risk_score"} for field in matrix_fields), matrix_fields)

    figure_svg = ROOT / "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg"
    figure_png = ROOT / "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png"
    svg_ok = False
    try:
        ET.parse(figure_svg)
        text = figure_svg.read_text(encoding="utf-8")
        required = ("Cross-System Joinability / Dependency Architecture", "Exact/entity-level", "System-level conceptual", "Inferred relationship", "Scenario-only relationship", "not a geographic map", "co-location")
        svg_ok = all(term in text for term in required)
    except Exception as exc:
        text = str(exc)
    png = figure_png.read_bytes() if figure_png.exists() else b""
    dims = [int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")] if len(png) >= 24 and png[:8] == b"\x89PNG\r\n\x1a\n" else []
    check("integration_figure_svg_qa", svg_ok, text[:300])
    check("integration_figure_png_qa", bool(dims and dims[0] >= 1000 and dims[1] >= 500), dims)

    # Phase 14A and all prior frozen manifests are checked by their recorded hashes.
    freeze_errors = []
    freeze_entries = 0
    freeze_unique = set()
    for manifest_path in sorted((ROOT / "reports").glob("*freeze_manifest.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rel, meta in entries(payload).items():
            freeze_entries += 1; freeze_unique.add(rel)
            path = ROOT / rel
            if not path.exists() or not verify_hash(path, meta): freeze_errors.append(f"{manifest_path.name}:{rel}")
    check("phase14a_and_prior_freeze_integrity", not freeze_errors, {"entries": freeze_entries, "unique_paths": len(freeze_unique), "errors": freeze_errors[:10]})
    a14a_final = json.loads(A14A_FINAL.read_text(encoding="utf-8"))
    check("phase14a_status_and_counts_preserved", a14a_final.get("accepted_phase") == "14A" and a14a_final.get("status") == "ACCEPTED / FROZEN" and a14a_final.get("counts", {}).get("identity_rows") == 456 and a14a_final.get("counts", {}).get("relationship_rows") == 367, a14a_final.get("counts"))
    a14a_errors = [rel for rel, meta in entries(a14a_final).items() if not (ROOT / rel).exists() or not verify_hash(ROOT / rel, meta)]
    check("phase14a_final_manifest_readback", not a14a_errors, a14a_errors[:10])

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    working_errors = [rel for rel, meta in entries(manifest).items() if not (ROOT / rel).exists() or not verify_hash(ROOT / rel, meta)]
    check("phase14b_working_manifest_integrity", not working_errors and manifest.get("phase") == "14B", working_errors[:10])
    r_result = json.loads(R_RESULT.read_text(encoding="utf-8")) if R_RESULT.exists() else {}
    check("independent_r_result_persisted", R_RESULT.exists() and r_result.get("phase") == "14B" and r_result.get("passed") is True, r_result)
    status_text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in ("PROJECT_STATUS.md", "docs/canon_status.md", "docs/agent_workflow.md", "reports/current_phase_handoff.md"))
    check("active_holds_retained", "C — HOLD / noncanonical" in status_text and "UNRESOLVED" in status_text, "active hold missing")
    check("phase15_release_tag_boundary", "Phase 15" in status_text and "NOT IMPLEMENTED" in status_text and "No release or tag" in status_text, "boundary text missing")
    check("no_composite_risk_artifact", not any("risk_score" in path.lower() or "connectivity_score" in path.lower() for path in changed), [p for p in changed if "score" in p.lower()])

    counts = {
        "registry_entries": len(layer_rows), "registry_formats": dict(Counter(row.get("physical_format") for row in layer_rows)),
        "relationship_rows": len(rel_rows), "endpoint_role_rows": len(endpoint_rows), "dependency_rows": len(dep_rows), "joinability_rows": len(matrix_rows),
        "population_total": len(pop), "population_inferred": sum(row["evidence_class"] == "INFERRED" for row in pop), "population_context_reused": sum(row["evidence_class"] == "CONTEXT_REUSED" for row in pop),
        "phase14a_freeze_entries": freeze_entries, "phase14a_freeze_unique_paths": len(freeze_unique), "phase14a_identity_rows": 456, "phase14a_endpoint_occurrences": 36,
    }
    result = {"passed": not errors, "checks": checks, "counts": counts, "errors": errors}
    CHECK.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "counts": counts, "errors": errors}, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
