"""Deterministic Phase 15A technology baseline validator."""
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
BASE_SHA = "d8247cf3419be6e0caf0b345f63644f2795c2ac6"
SYSTEMS = ROOT / "metadata/atlas_systems.yml"
VOCABULARY = ROOT / "metadata/technology_vocabulary.yml"
NODES = ROOT / "data/processed/analysis/technology_system_nodes.csv"
OBSERVATIONS = ROOT / "data/processed/analysis/technology_system_observations.csv"
SOURCES = ROOT / "data/processed/analysis/technology_sources.csv"
UNCERTAINTIES = ROOT / "data/processed/analysis/technology_uncertainties.csv"
INTERFACES = ROOT / "data/processed/integration/technology_system_interfaces.csv"
DEPENDENCIES = ROOT / "data/processed/integration/technology_dependencies.csv"
MANIFEST = ROOT / "reports/phase15a_manifest.json"
FINAL_FREEZE_MANIFEST = ROOT / "reports/phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
CHECK = ROOT / "reports/phase15a_artifact_check.json"
FIGURE_SVG = ROOT / "outputs/figures/technology_system_convergence_architecture_2026.svg"
FIGURE_PNG = ROOT / "outputs/figures/technology_system_convergence_architecture_2026.png"
BIOSECURITY_REPORT = ROOT / "reports/phase15a_biosecurity_lens.md"
PROVENANCE_REPORT = ROOT / "reports/phase15a_provenance_check.md"

FAMILIES = {
    "AI / ADVANCED COMPUTE / AUTOMATION",
    "ADVANCED SENSING / AUTONOMOUS SYSTEMS",
    "CYBERSECURITY / DIGITAL RESILIENCE",
    "ADVANCED ENERGY",
    "ADVANCED MATERIALS / MANUFACTURING",
    "QUANTUM TECHNOLOGIES",
    "BIOTECHNOLOGY / GENETIC ENGINEERING",
    "PRIVACY / SURVEILLANCE / DATA GOVERNANCE",
}
STATUSES = {"established", "commercially emerging", "demonstration / pilot", "research-stage", "speculative / long-horizon"}
RELEVANCE = {"current", "emerging", "speculative"}
EVIDENCE = {"OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "UNRESOLVED", "NONCANONICAL_HOLD"}
RELATIONSHIPS = {"physical flow", "material flow", "energy flow", "information / observation", "governance / authority", "operational dependency", "ecological relationship", "exposure pathway", "population / mobility interface", "surveillance / detection", "high-level association", "unresolved / unclassified"}
DEPENDENCY_CLASSES = {"electricity", "compute", "communications", "skilled workforce", "water", "materials", "supply chain", "data", "regulatory authority", "public trust / legitimacy", "physical infrastructure"}
INTERFACE_TYPES = {
    "grid and load decision support", "water-system decision support", "environmental modeling and analytics", "climate and hazard modeling", "industrial optimization and logistics", "process and materials optimization", "public-health surveillance analytics",
    "water-quality observation", "ecosystem observation", "nutrient and runoff observation", "infrastructure inspection", "corridor and asset inspection", "environmental-health observation",
    "defensive continuity", "defensive grid resilience", "defensive logistics continuity", "public-health digital continuity", "cryptographic trust transition",
    "advanced generation possibility", "long-duration storage interface", "storage and cooling dependency", "distributed generation/storage interface", "hydrogen material-input interface", "heavy-industry and freight energy carrier", "fusion generation research interface",
    "advanced material process interface", "manufacturing supply-chain interface", "recovery and circular-material interface", "material-process energy dependency",
    "quantum measurement interface", "high-precision water observation watch item", "optimization research interface", "logistics optimization watch item",
    "genomic detection and diagnosis", "environmental molecular monitoring", "biomanufacturing materials interface", "One Health biological monitoring", "vector and host surveillance", "biosecurity governance lens",
    "sensor and data stewardship", "privacy and accountability interface", "mobility and utility data governance", "public-health data stewardship", "operating-information continuity",
}
TEXT_EXTENSIONS = {".csv", ".json", ".md", ".py", ".r", ".R", ".yml", ".yaml", ".svg", ".txt"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def normalized(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_matches(path: Path, expected: str) -> bool:
    raw = path.read_bytes()
    return digest(raw) == expected or (path.suffix in TEXT_EXTENSIONS and digest(normalized(raw)) == expected)


def manifest_entries(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("artifacts", payload.get("files", {}))
    return value if isinstance(value, dict) else {}


def prior_freeze_paths() -> tuple[int, set[str], list[str]]:
    total = 0
    paths: set[str] = set()
    errors: list[str] = []
    for manifest_path in sorted((ROOT / "reports").glob("*freeze_manifest.json")):
        if manifest_path.name == FINAL_FREEZE_MANIFEST.name:
            continue
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rel, value in manifest_entries(payload).items():
            total += 1
            paths.add(rel.replace("\\", "/"))
            expected = value if isinstance(value, str) else str(value.get("sha256", ""))
            target = ROOT / rel
            if not target.exists() or not expected or not hash_matches(target, expected):
                errors.append(f"{manifest_path.name}:{rel}")
    return total, paths, errors


def main() -> int:
    checks: dict[str, dict[str, object]] = {}
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks[name] = {"passed": bool(condition), "detail": detail}
        if not condition:
            errors.append(f"{name}: {detail}")

    vocabulary = yaml.safe_load(VOCABULARY.read_text(encoding="utf-8"))
    ontology = yaml.safe_load(SYSTEMS.read_text(encoding="utf-8"))
    system_ids = {row["system_id"] for row in ontology.get("systems", [])}
    check("phase14_ontology_count", len(system_ids) == 13, len(system_ids))
    check("technology_vocabulary_families", set(vocabulary.get("technology_families", [])) == FAMILIES, vocabulary.get("technology_families"))
    check("technology_vocabulary_status", set(vocabulary.get("technology_status", [])) == STATUSES, vocabulary.get("technology_status"))
    check("technology_vocabulary_relevance", set(vocabulary.get("regional_relevance", [])) == RELEVANCE, vocabulary.get("regional_relevance"))

    changed = [line.replace("\\", "/") for line in subprocess.check_output(["git", "-C", str(ROOT), "diff", "--name-only", BASE_SHA], text=True).splitlines()]
    prior_total, protected, freeze_errors = prior_freeze_paths()
    changed_protected = sorted(set(changed) & protected)
    check("prior_freeze_hash_integrity", not freeze_errors, {"entries": prior_total, "unique_paths": len(protected), "errors": freeze_errors[:10]})
    check("no_prior_frozen_artifact_modified", not changed_protected, changed_protected)
    check("original_phase14_registries_untouched", "metadata/atlas_systems.yml" not in changed and "metadata/atlas_layers.yml" not in changed, changed)
    check("no_phase16_implementation", not any(("phase16" in path.lower()) and not path.startswith("docs/phase_briefs/") for path in changed), [p for p in changed if "phase16" in p.lower()])
    check("phase15b_brief_only", not any(("phase15b" in path.lower()) and not path.startswith("docs/phase_briefs/") for path in changed), [p for p in changed if "phase15b" in p.lower()])
    check("no_future_data_or_maps", not any("scenario" in path.lower() or "future" in path.lower() for path in changed if path.startswith(("data/", "outputs/"))), [p for p in changed if "scenario" in p.lower() or "future" in p.lower()])

    source_fields, source_rows = read_csv(SOURCES)
    source_ids = {row["source_id"] for row in source_rows}
    regional_source_ids = {row["source_id"] for row in source_rows if row["source_scope"] == "regional_system_context"}
    check("source_ids_unique", len(source_ids) == len(source_rows) and all(source_ids), len(source_rows))
    check("source_urls_present", all(row["url"] and row["retrieval_url"] and row["retrieval_date"] for row in source_rows), "blank URL or retrieval metadata")
    check("source_scope_values", set(row["source_scope"] for row in source_rows) <= {"general_technology_capability", "regional_system_context"}, sorted(set(row["source_scope"] for row in source_rows)))
    check("regional_deployment_not_claimed", all(row["regional_deployment_supported"].lower() == "no" for row in source_rows), [row["source_id"] for row in source_rows if row["regional_deployment_supported"].lower() != "no"])
    check("external_urls_are_https", all((row["source_type"] != "authoritative_government_or_institutional") or row["url"].startswith("https://") for row in source_rows), "non-HTTPS external source")

    node_fields, nodes = read_csv(NODES)
    node_ids = {row["technology_id"] for row in nodes}
    node_by_id = {row["technology_id"]: row for row in nodes}
    check("technology_ids_unique", len(node_ids) == len(nodes) and all(node_ids), len(nodes))
    check("technology_families_valid", set(row["technology_family"] for row in nodes) <= FAMILIES, sorted(set(row["technology_family"] for row in nodes) - FAMILIES))
    check("all_families_represented", set(row["technology_family"] for row in nodes) == FAMILIES, sorted(FAMILIES - set(row["technology_family"] for row in nodes)))
    check("technology_status_valid", set(row["technology_status"] for row in nodes) <= STATUSES, sorted(set(row["technology_status"] for row in nodes) - STATUSES))
    check("technology_relevance_valid", set(row["regional_relevance"] for row in nodes) <= RELEVANCE, sorted(set(row["regional_relevance"] for row in nodes) - RELEVANCE))
    check("current_emerging_speculative_preserved", set(row["current_or_emerging"] for row in nodes) == RELEVANCE, sorted(set(row["current_or_emerging"] for row in nodes)))
    check("node_sources_resolve", all(row["source_id"] in source_ids and row["regional_evidence_source_id"] in source_ids for row in nodes), "unresolved node source")
    check("node_regional_basis_is_regional_context", all(row["regional_evidence_source_id"] in regional_source_ids for row in nodes), "nonregional technology basis")
    check("node_governance_and_uncertainty", all(row["governance_interface"] and row["uncertainty"] and row["adoption_boundary"] for row in nodes), "blank governance/boundary/uncertainty")

    observation_fields, observations = read_csv(OBSERVATIONS)
    observation_ids = {row["observation_id"] for row in observations}
    check("observation_ids_unique", len(observation_ids) == len(observations), len(observations))
    check("observation_technology_ids_resolve", all(row["technology_id"] in node_ids for row in observations), "unresolved observation technology")
    check("observation_sources_resolve", all(row["source_id"] in source_ids and row["regional_evidence_source_id"] in source_ids for row in observations), "unresolved observation source")
    general = [row for row in observations if row["claim_scope"] == "general_capability"]
    check("general_capability_not_localized", all("Western Basin" not in row["geographic_scope"] and "Toledo" not in row["geographic_scope"] for row in general), "general claim labeled local")
    regional = [row for row in observations if row["claim_scope"] == "regional_system_context"]
    check("regional_context_is_not_deployment", all("not" in row["notes"].lower() and ("deployment" in row["notes"].lower() or "inventory" in row["notes"].lower()) for row in regional), "regional observation lacks non-deployment caveat")
    check("observation_evidence_valid", set(row["evidence_class"] for row in observations) <= EVIDENCE, sorted(set(row["evidence_class"] for row in observations) - EVIDENCE))

    interface_fields, interfaces = read_csv(INTERFACES)
    interface_ids = {row["interface_id"] for row in interfaces}
    check("interface_ids_unique", len(interface_ids) == len(interfaces), len(interfaces))
    check("interface_technology_ids_resolve", all(row["technology_id"] in node_ids for row in interfaces), "unresolved interface technology")
    check("interface_target_systems_resolve", all(row["target_system_id"] in system_ids for row in interfaces), sorted({row["target_system_id"] for row in interfaces if row["target_system_id"] not in system_ids}))
    check("interface_source_system_blank_by_design", all(not row["source_system_id"] for row in interfaces), "technology promoted into source system registry")
    check("interface_types_valid", set(row["interface_type"] for row in interfaces) <= INTERFACE_TYPES, sorted(set(row["interface_type"] for row in interfaces) - INTERFACE_TYPES))
    check("interface_relationships_valid", set(row["normalized_relationship_class"] for row in interfaces) <= RELATIONSHIPS, sorted(set(row["normalized_relationship_class"] for row in interfaces) - RELATIONSHIPS))
    check("interface_evidence_valid", set(row["evidence_class"] for row in interfaces) <= EVIDENCE, sorted(set(row["evidence_class"] for row in interfaces) - EVIDENCE))
    check("interface_sources_resolve", all(row["source_id"] in source_ids for row in interfaces), "unresolved interface source")
    check("interface_current_value_matches_node", all(row["current_or_emerging"] == node_by_id[row["technology_id"]]["current_or_emerging"] and row["regional_relevance"] == node_by_id[row["technology_id"]]["regional_relevance"] for row in interfaces), "relevance/status drift")
    check("interface_governance_uncertainty_present", all(row["governance_interface"] and row["uncertainty"] and row["dependency_basis"] for row in interfaces), "blank interface field")
    check("interface_is_inferred", all(row["evidence_class"] == "INFERRED" for row in interfaces), sorted(set(row["evidence_class"] for row in interfaces)))

    dependency_fields, dependencies = read_csv(DEPENDENCIES)
    dependency_ids = {row["dependency_id"] for row in dependencies}
    check("dependency_ids_unique", len(dependency_ids) == len(dependencies), len(dependencies))
    check("dependency_technology_ids_resolve", all(row["technology_id"] in node_ids for row in dependencies), "unresolved dependency technology")
    check("dependency_classes_valid", set(row["dependency_class"] for row in dependencies) <= DEPENDENCY_CLASSES, sorted(set(row["dependency_class"] for row in dependencies) - DEPENDENCY_CLASSES))
    check("dependency_roles_valid", set(row["dependency_role"] for row in dependencies) <= {"enabling", "limiting"}, sorted(set(row["dependency_role"] for row in dependencies)))
    check("dependency_systems_resolve", all(row["affected_system_id"] in system_ids for row in dependencies), "unresolved dependency system")
    check("dependency_evidence_sources_resolve", all(row["evidence_class"] in EVIDENCE and row["source_id"] in source_ids for row in dependencies), "unresolved dependency evidence/source")
    check("dependency_status_reused", all(row["technology_status"] == node_by_id[row["technology_id"]]["technology_status"] for row in dependencies), "technology status drift")
    check("dependency_boundary_fields", all(row["limitation"] and row["governance_interface"] and "not" in row["notes"].lower() for row in dependencies), "dependency limitation/boundary missing")

    uncertainty_fields, uncertainties = read_csv(UNCERTAINTIES)
    uncertainty_ids = {row["uncertainty_id"] for row in uncertainties}
    check("uncertainty_ids_unique", len(uncertainty_ids) == len(uncertainties), len(uncertainties))
    check("uncertainty_references_resolve", all(row["technology_id"] in node_ids and row["affected_system_id"] in system_ids and row["source_id"] in source_ids and row["regional_evidence_source_id"] in source_ids for row in uncertainties), "unresolved uncertainty reference")
    check("uncertainty_is_open", all(row["uncertainty_status"] == "open" for row in uncertainties), sorted(set(row["uncertainty_status"] for row in uncertainties)))
    check("uncertainty_is_not_risk_score", not any("score" in field.lower() or "probability" in field.lower() for field in uncertainty_fields), uncertainty_fields)

    ai_nodes = [row for row in nodes if row["technology_family"] == "AI / ADVANCED COMPUTE / AUTOMATION"]
    check("ai_decision_support_not_authority", all("decision support" in row["governance_interface"].lower() or "recommendation" in row["governance_interface"].lower() for row in ai_nodes) and all("autonomous" in row["governance_interface"].lower() or "production decision" in row["governance_interface"].lower() for row in ai_nodes), "AI authority boundary missing")
    sensing = [row for row in interfaces if row["technology_family"] == "ADVANCED SENSING / AUTONOMOUS SYSTEMS"]
    check("sensing_not_enforcement", not any("enforcement" in row["interface_type"].lower() for row in sensing) and all(any(term in (row["governance_interface"] + row["interface_type"]).lower() for term in ("measurement", "observation", "inspection")) for row in sensing), "sensing/enforcement collapse")
    cyber_positive = " ".join(" ".join(row.get(field, "") for field in ("technology_label", "capability_scope", "interface_type", "dependency_label")) for row in nodes + interfaces + dependencies)
    check("cyber_defensive_scope", all(term in cyber_positive.lower() for term in ("defensive", "resilience")) and not re.search(r"\b(offensive|exploit|malware|payload|attack procedure)\b", cyber_positive.lower()), "cyber positive content is not bounded")
    quantum = [row for row in nodes if row["technology_family"] == "QUANTUM TECHNOLOGIES"]
    check("quantum_conservative_status", all(row["technology_status"] == "research-stage" and row["current_or_emerging"] == "speculative" and row["regional_relevance"] == "speculative" for row in quantum), [(row["technology_id"], row["technology_status"], row["regional_relevance"]) for row in quantum])
    fusion = node_by_id["TECH-ENERGY-FUSION"]
    check("fusion_not_current_deployment", fusion["technology_status"] == "research-stage" and fusion["current_or_emerging"] == "speculative" and fusion["regional_relevance"] == "speculative" and "no current" in fusion["notes"].lower(), fusion)
    biotech_positive = " ".join(" ".join(row.get(field, "") for field in ("technology_label", "capability_scope", "interface_type", "dependency_label")) for row in nodes + interfaces + dependencies)
    check("biotech_positive_scope_safe", not re.search(r"\b(weaponization|pathogen optimization|harmful-agent enhancement|evasion tactic|wet-lab protocol)\b", biotech_positive.lower()), "unsafe positive biotechnology detail")
    check("biosecurity_lens_bounded", all(term in BIOSECURITY_REPORT.read_text(encoding="utf-8") for term in ("Detection", "Attribution uncertainty", "Laboratory/diagnostic capacity", "Biological monitoring", "Supply-chain resilience", "Dual-use governance", "public communication", "no pathogen engineering")), "biosecurity lens topic/boundary")
    provenance_text = PROVENANCE_REPORT.read_text(encoding="utf-8")
    check("grounded_provenance_report", all(f"[{index}]" in provenance_text for index in range(1, 18)) and "## Sources" in provenance_text, "ledger citations/source block")

    figure_svg_ok = False
    figure_detail = ""
    try:
        ET.parse(FIGURE_SVG)
        figure_text = FIGURE_SVG.read_text(encoding="utf-8")
        required = ("Technology", "Established/current interface", "Emerging interface", "Speculative/long-horizon interface", "G = governance/data dependency", "not deployment", "not a geographic map")
        figure_svg_ok = all(term in figure_text for term in required)
        figure_detail = {"required": required, "bytes": FIGURE_SVG.stat().st_size}
    except Exception as exc:
        figure_detail = str(exc)
    check("convergence_figure_svg_qa", figure_svg_ok, figure_detail)
    png = FIGURE_PNG.read_bytes() if FIGURE_PNG.exists() else b""
    dimensions = [int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")] if len(png) >= 24 and png[:8] == b"\x89PNG\r\n\x1a\n" else []
    check("convergence_figure_png_qa", bool(dimensions and dimensions[0] >= 1200 and dimensions[1] >= 500), dimensions)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_counts = {"technology_families": 8, "technology_nodes": len(nodes), "observations": len(observations), "interfaces": len(interfaces), "dependencies": len(dependencies), "uncertainties": len(uncertainties), "sources": len(source_rows)}
    check("working_manifest_identity", manifest.get("phase") == "15A" and manifest.get("source_commit") == BASE_SHA and manifest.get("status") == "generated_working_package", {key: manifest.get(key) for key in ("phase", "source_commit", "status")})
    check("working_manifest_counts", all(manifest.get("counts", {}).get(key) == value for key, value in expected_counts.items()), manifest.get("counts"))
    manifest_errors = []
    for rel, meta in manifest_entries(manifest).items():
        target = ROOT / rel
        expected = meta if isinstance(meta, str) else str(meta.get("sha256", ""))
        if not target.exists() or not expected or not hash_matches(target, expected):
            manifest_errors.append(rel)
    check("working_manifest_artifacts", not manifest_errors, manifest_errors[:10])

    status_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in ("PROJECT_STATUS.md", "docs/canon_status.md", "docs/agent_workflow.md", "reports/current_phase_handoff.md"))
    check("active_holds_retained", "C — HOLD / noncanonical" in status_text and "UNRESOLVED" in status_text, "active hold missing")
    check("phase14_complete_accepted_frozen", "Phase 14 is **COMPLETE / ACCEPTED / FROZEN**" in status_text or "Phase 14: **COMPLETE / ACCEPTED / FROZEN**" in status_text, "Phase 14 status missing")
    check("phase15b_and_phase16_boundary", "APPROVED SCOPE / NOT IMPLEMENTED" in (ROOT / "docs/phase_briefs/phase15b_technology_convergence_futures.md").read_text(encoding="utf-8") and "Phase 16" in status_text or "Phase 16" in (ROOT / "docs/phase_briefs/phase15_technology_strategic_systems_convergence.md").read_text(encoding="utf-8"), "future boundary missing")
    check("no_release_or_tag", not manifest.get("release_created") and not manifest.get("tag_created") and "No release or tag" in status_text, "release/tag boundary missing")

    counts = {
        "technology_families": len(FAMILIES), "technology_nodes": len(nodes), "observations": len(observations), "interfaces": len(interfaces), "dependencies": len(dependencies), "uncertainties": len(uncertainties), "sources": len(source_rows),
        "status_counts": dict(Counter(row["technology_status"] for row in nodes)), "current_emerging_speculative_counts": dict(Counter(row["current_or_emerging"] for row in nodes)),
        "interface_relevance_counts": dict(Counter(row["regional_relevance"] for row in interfaces)), "prior_freeze_entries": prior_total, "prior_freeze_unique_paths": len(protected),
    }
    result = {"phase": "15A", "passed": not errors, "checks": checks, "counts": counts, "errors": errors}
    CHECK.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "15A", "passed": result["passed"], "counts": counts, "errors": errors}, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
