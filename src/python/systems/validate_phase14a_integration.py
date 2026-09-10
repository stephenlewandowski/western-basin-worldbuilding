"""Independent deterministic validator for the Phase 14A integration package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
ONTOLOGY_PATH = ROOT / "metadata/atlas_systems.yml"
EVIDENCE_PATH = ROOT / "metadata/atlas_evidence_vocabulary.yml"
IDENTITY_PATH = ROOT / "data/processed/integration/system_identity_crosswalk.csv"
ENDPOINT_PATH = ROOT / "data/processed/integration/external_endpoint_crosswalk.csv"
RELATIONSHIP_PATH = ROOT / "data/processed/integration/relationship_taxonomy_inventory.csv"
MANIFEST_PATH = ROOT / "reports/phase14a_manifest.json"
CHECK_PATH = ROOT / "reports/phase14a_artifact_check.json"
TEXT_EXTENSIONS = {".csv", ".md", ".json", ".yml", ".yaml", ".svg", ".txt", ".py", ".r"}
ALLOWED_MAPPING_TYPES = {"exact identity", "system-level concept", "generalized external interface", "unresolved"}
ALLOWED_MAPPING_STATUS = {"resolved", "resolved_system_level", "retained_conceptual", "unresolved"}
ALLOWED_REL_CLASSES = {
    "physical flow", "material flow", "energy flow", "information / observation",
    "governance / authority", "operational dependency", "ecological relationship",
    "exposure pathway", "population / mobility interface", "surveillance / detection",
    "scenario influence", "high-level interface / association", "unclassified candidate",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def normalize_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_matches(path: Path, expected: str) -> tuple[bool, str]:
    raw = path.read_bytes()
    if sha256(raw) == expected:
        return True, "raw"
    if path.suffix.lower() in TEXT_EXTENSIONS and sha256(normalize_text(raw)) == expected:
        return True, "lf_crlf_portable"
    return False, "mismatch"


def manifest_entries(data: dict) -> dict[str, dict]:
    entries = data.get("artifacts", data.get("files", {}))
    return entries if isinstance(entries, dict) else {}


def git_changed_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=True)
    paths = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        value = line[3:] if len(line) >= 3 else line
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        paths.append(value.replace("\\", "/"))
    return paths


def main() -> int:
    checks: dict[str, dict[str, object]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    ontology = yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8"))
    evidence = yaml.safe_load(EVIDENCE_PATH.read_text(encoding="utf-8"))
    systems = ontology.get("systems", [])
    system_ids = [item.get("system_id", "") for item in systems]
    check("ontology_system_count", len(systems) == 13, len(systems))
    check("ontology_system_ids_unique", len(system_ids) == len(set(system_ids)) and all(x.startswith("SYS-") for x in system_ids), system_ids)
    required_system_fields = {"system_id", "preferred_label", "aliases", "broad_system_family", "originating_phases", "canonical_status", "primary_tables", "principal_maps", "temporal_basis", "baseline_scenario_distinction", "provenance_pointer", "atlas_display_label"}
    check("ontology_required_fields", all(required_system_fields.issubset(item) for item in systems), sorted(required_system_fields))
    missing_tables = []
    missing_maps = []
    for item in systems:
        missing_tables.extend([path for path in item["primary_tables"] if not (ROOT / path).exists()])
        for map_name in item["principal_maps"]:
            for suffix in (".png", ".svg"):
                if not (ROOT / "outputs/maps/systems" / f"{map_name}{suffix}").exists():
                    missing_maps.append(f"{map_name}{suffix}")
    check("ontology_primary_tables_exist", not missing_tables, missing_tables[:20])
    check("ontology_principal_maps_exist", not missing_maps, missing_maps[:20])
    check("existing_systems_registry_untouched", not any(p == "metadata/systems.yml" for p in git_changed_paths()), git_changed_paths())

    identity_fields, identity = read_csv(IDENTITY_PATH)
    endpoint_fields, endpoints = read_csv(ENDPOINT_PATH)
    relationship_fields, relationships = read_csv(RELATIONSHIP_PATH)
    check("identity_required_fields", {"atlas_entity_id", "local_id", "source_artifact", "system_id", "mapping_type", "mapping_status", "evidence_basis"}.issubset(identity_fields), identity_fields)
    check("identity_atlas_ids_unique", len({row["atlas_entity_id"] for row in identity}) == len(identity), len(identity))
    check("identity_local_namespace_pairs_unique", len({(row["source_artifact"], row["local_id"]) for row in identity}) == len(identity), len(identity))
    check("identity_mapping_types_valid", all(row["mapping_type"] == "exact identity" for row in identity), sorted({row["mapping_type"] for row in identity}))
    check("identity_mapping_status_valid", all(row["mapping_status"] == "resolved" for row in identity), sorted({row["mapping_status"] for row in identity}))
    check("identity_system_ids_known", all(row["system_id"] in system_ids for row in identity), sorted({row["system_id"] for row in identity if row["system_id"] not in system_ids}))

    source_ids: dict[str, set[str]] = {}
    source_headers: dict[str, list[str]] = {}
    for source in ontology["identity_sources"]:
        fields, records = read_csv(ROOT / source["source_artifact"])
        source_headers[source["source_artifact"]] = fields
        source_ids[source["source_artifact"]] = {record[source["id_field"]].strip() for record in records}
    unresolved_identity = []
    scenario_identity_errors = []
    for row in identity:
        if row["source_artifact"] not in source_ids or row["local_id"] not in source_ids[row["source_artifact"]]:
            unresolved_identity.append(f"{row['source_artifact']}:{row['local_id']}")
        is_scenario = row.get("canon_status", "").lower() == "scenario" or row.get("reality_status", "").lower() == "fictional"
        if is_scenario and not (row.get("canon_status", "").lower() == "scenario" and row.get("reality_status", "").lower() == "fictional"):
            scenario_identity_errors.append(row["atlas_entity_id"])
    check("all_local_ids_resolve_to_source_artifacts", not unresolved_identity, unresolved_identity[:20])
    check("identity_scenario_labels_retained", not scenario_identity_errors, scenario_identity_errors)
    check("identity_provenance_complete", all(row["source_phase"] and row["source_artifact"] and row["local_id"] and row["evidence_basis"] for row in identity), "blank provenance field")
    exact_conflicts = defaultdict(set)
    for row in identity:
        exact_conflicts[(row["source_artifact"], row["local_id"])].add(row["atlas_entity_id"])
    check("no_conflicting_exact_identity_mappings", all(len(values) == 1 for values in exact_conflicts.values()), "conflicting exact identity rows")

    check("endpoint_required_fields", {"dependency_id", "endpoint_position", "local_endpoint_id", "source_artifact", "atlas_entity_id", "mapping_type", "mapping_status", "evidence_basis"}.issubset(endpoint_fields), endpoint_fields)
    register_path = ROOT / "data/processed/analysis/infectious_disease_dependency_register.csv"
    register_fields, register = read_csv(register_path)
    register_by_id = {row["dependency_id"]: row for row in register}
    conceptual_rows = {row["dependency_id"] for row in endpoints}
    expected_conceptual_rows = {row["dependency_id"] for row in register if row["from_id"].startswith(("EXT-", "REF-")) or row["to_id"].startswith(("EXT-", "REF-"))}
    check("endpoint_register_source_exists", register_path.exists(), str(register_path))
    check("endpoint_dependency_ids_resolve", all(row["dependency_id"] in register_by_id for row in endpoints), sorted({row["dependency_id"] for row in endpoints if row["dependency_id"] not in register_by_id}))
    endpoint_mismatch = []
    for row in endpoints:
        source = register_by_id.get(row["dependency_id"], {})
        expected = source.get(f"{row['endpoint_position']}_id")
        if expected != row["local_endpoint_id"]:
            endpoint_mismatch.append(f"{row['endpoint_crosswalk_id']} expected {expected} got {row['local_endpoint_id']}")
    check("endpoint_local_ids_match_source_rows", not endpoint_mismatch, endpoint_mismatch[:20])
    check("endpoint_conceptual_dependency_rows_reconcile", conceptual_rows == expected_conceptual_rows and len(conceptual_rows) == 25, {"actual": len(conceptual_rows), "expected": len(expected_conceptual_rows)})
    endpoint_counts = Counter(row["mapping_status"] for row in endpoints)
    check("endpoint_mapping_status_valid", set(endpoint_counts).issubset({"resolved_system_level", "retained_conceptual", "unresolved"}), dict(endpoint_counts))
    check("endpoint_resolution_totals_reconcile", endpoint_counts == Counter({"resolved_system_level": 34, "retained_conceptual": 2}), dict(endpoint_counts))
    check("endpoint_exact_identity_not_invented", not any(row["mapping_type"] == "exact identity" for row in endpoints), "conceptual endpoint marked exact")
    check("endpoint_unresolved_explicit", all((row["mapping_status"] != "unresolved") or (not row["atlas_entity_id"] and row["mapping_type"] == "unresolved") for row in endpoints), "unresolved endpoint not explicit")
    check("endpoint_system_mappings_known", all((not row["canonical_system_id"]) or row["canonical_system_id"] in system_ids for row in endpoints), sorted({row["canonical_system_id"] for row in endpoints if row["canonical_system_id"] and row["canonical_system_id"] not in system_ids}))
    check("endpoint_provenance_complete", all(row["source_phase"] == "13B" and row["source_artifact"] == "data/processed/analysis/infectious_disease_dependency_register.csv" and row["evidence_basis"] for row in endpoints), "endpoint lineage incomplete")

    normalized_classes = {item["class_id"] for item in evidence.get("normalized_classes", [])}
    required_classes = {"OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD"}
    check("evidence_vocabulary_complete", normalized_classes == required_classes, sorted(normalized_classes))
    check("evidence_mappings_reference_known_classes", all(item.get("normalized_class") in normalized_classes for item in evidence.get("mappings", [])), sorted({item.get("normalized_class") for item in evidence.get("mappings", []) if item.get("normalized_class") not in normalized_classes}))
    check("evidence_mappings_have_loss_notes", all(item.get("information_lost_or_caveat") for item in evidence.get("mappings", [])), "mapping without information-loss caveat")
    non_eq = {tuple(item) for item in evidence.get("explicit_non_equivalences", [])}
    required_non_eq = {("fact", "inference"), ("fact", "scenario_assumption"), ("fact", "scenario_state"), ("observation", "derived_value"), ("dependency", "risk"), ("association", "causation")}
    check("evidence_non_equivalences_retained", required_non_eq.issubset(non_eq), sorted(required_non_eq - non_eq))
    crosswalk_terms = {(item["local_field"], item["local_term"]) for item in evidence.get("mappings", [])}
    check("evidence_local_terms_are_explicit", all(field and term for field, term in crosswalk_terms), len(crosswalk_terms))

    check("relationship_required_fields", {"taxonomy_id", "source_phase", "source_artifact", "local_field", "local_term", "proposed_high_level_class", "normalization_status", "semantic_compatibility", "information_lost_or_caveat"}.issubset(relationship_fields), relationship_fields)
    check("relationship_taxonomy_ids_unique", len({row["taxonomy_id"] for row in relationships}) == len(relationships), len(relationships))
    relationship_errors = []
    relation_counts = Counter()
    for row in relationships:
        path = ROOT / row["source_artifact"]
        if not path.exists():
            relationship_errors.append(f"missing:{row['source_artifact']}")
            continue
        fields, records = read_csv(path)
        if row["local_field"] not in fields:
            relationship_errors.append(f"field:{row['source_artifact']}:{row['local_field']}")
            continue
        actual_count = sum(1 for record in records if (record.get(row["local_field"]) or "").strip() == row["local_term"])
        if actual_count != int(row["local_term_count"]):
            relationship_errors.append(f"count:{row['taxonomy_id']} expected {actual_count} got {row['local_term_count']}")
        relation_counts[row["proposed_high_level_class"]] += 1
    check("relationship_rows_resolve_and_counts_match", not relationship_errors, relationship_errors[:20])
    check("relationship_classes_allowed", set(relation_counts).issubset(ALLOWED_REL_CLASSES), sorted(set(relation_counts) - ALLOWED_REL_CLASSES))
    check("relationship_inventory_not_claimed_as_14B_normalization", all(row["normalization_status"] == "inventory_only_14A" for row in relationships), sorted({row["normalization_status"] for row in relationships}))
    check("relationship_caveats_present", all(row["information_lost_or_caveat"] for row in relationships), "missing relationship caveat")

    required_reports = [
        "reports/phase14a_systems_ontology.md", "reports/phase14a_identity_crosswalk.md",
        "reports/phase14a_evidence_crosswalk.md", "reports/phase14a_relationship_taxonomy.md",
        "reports/phase14a_integration_qa.md", "reports/phase14a_build_summary.json",
    ]
    check("phase14a_reports_present", all((ROOT / path).exists() and (ROOT / path).stat().st_size > 0 for path in required_reports), required_reports)
    svg = ROOT / "outputs/figures/western_basin_systems_architecture.svg"
    png = ROOT / "outputs/figures/western_basin_systems_architecture.png"
    svg_ok = False
    try:
        ET.parse(svg)
        svg_text = svg.read_text(encoding="utf-8")
        svg_ok = "Western Basin Systems Architecture" in svg_text and "not a geographic map" in svg_text
    except Exception as exc:
        svg_text = str(exc)
    check("architecture_svg_qa", svg_ok, svg_text[:200])
    png_bytes = png.read_bytes() if png.exists() else b""
    png_dims = None
    if len(png_bytes) >= 24 and png_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        png_dims = [int.from_bytes(png_bytes[16:20], "big"), int.from_bytes(png_bytes[20:24], "big")]
    check("architecture_png_qa", bool(png_dims and png_dims[0] >= 1000 and png_dims[1] >= 500), png_dims)

    # Protect all prior freeze-manifest artifacts. Text newline representation is the only tolerated difference.
    freeze_entries = 0
    freeze_unique = set()
    freeze_errors = []
    for manifest_path in sorted((ROOT / "reports").glob("*freeze_manifest.json")):
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rel, meta in manifest_entries(data).items():
            freeze_entries += 1
            freeze_unique.add(rel)
            artifact = ROOT / rel
            expected = meta.get("sha256") if isinstance(meta, dict) else meta
            if not artifact.exists():
                freeze_errors.append(f"missing:{manifest_path.name}:{rel}")
            elif expected:
                ok, mode = hash_matches(artifact, expected)
                if not ok:
                    freeze_errors.append(f"hash:{manifest_path.name}:{rel}")
    check("prior_freeze_integrity", not freeze_errors, {"entries": freeze_entries, "unique_paths": len(freeze_unique), "errors": freeze_errors[:10]})

    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    working_errors = []
    for rel, meta in manifest_entries(manifest_data).items():
        artifact = ROOT / rel
        expected = meta.get("sha256") if isinstance(meta, dict) else meta
        if not artifact.exists():
            working_errors.append(f"missing:{rel}")
        elif expected and not hash_matches(artifact, expected)[0]:
            working_errors.append(f"hash:{rel}")
    check("phase14a_manifest_integrity", not working_errors, {"artifacts": len(manifest_entries(manifest_data)), "errors": working_errors[:10]})

    changed = git_changed_paths()
    forbidden_changes = [path for path in changed if path == "metadata/systems.yml" or path == "data/processed/glasspunk_base.gpkg" or path.startswith("reports/phase") and path.endswith("freeze_manifest.json")]
    check("no_frozen_or_historical_artifact_modification", not forbidden_changes, forbidden_changes)
    check("active_holds_retained", "C — HOLD" in (ROOT / "docs/canon_status.md").read_text(encoding="utf-8") and "UNRESOLVED" in (ROOT / "docs/canon_status.md").read_text(encoding="utf-8"), "active hold text missing")
    forbidden_new = [path for path in changed if path.startswith("data/processed/integration/atlas_layer") or "phase14b" in path.lower() and path not in {"docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md"} or "phase15" in path.lower()]
    check("phase14b_and_phase15_not_implemented", not forbidden_new, forbidden_new)
    check("no_monolithic_geopackage_added", not any(path.endswith(".gpkg") for path in changed), [path for path in changed if path.endswith(".gpkg")])

    counts = {
        "systems": len(systems), "identity_rows": len(identity), "endpoint_rows": len(endpoints),
        "conceptual_dependency_rows": len(conceptual_rows), "total_dependencies": len(register),
        "exact_resolved": 0, "system_level_resolved": endpoint_counts.get("resolved_system_level", 0),
        "retained_conceptual": endpoint_counts.get("retained_conceptual", 0), "unresolved": endpoint_counts.get("unresolved", 0),
        "relationship_rows": len(relationships), "evidence_classes": len(normalized_classes),
        "freeze_manifest_entries": freeze_entries, "freeze_unique_paths": len(freeze_unique),
    }
    result = {"passed": not errors, "checks": checks, "counts": counts, "errors": errors}
    CHECK_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "counts": counts, "errors": errors}, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
