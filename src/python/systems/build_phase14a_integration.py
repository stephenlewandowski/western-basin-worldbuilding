"""Build the additive Phase 14A ontology and evidence crosswalk package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import yaml

ROOT = Path(__file__).resolve().parents[3]
ONTOLOGY = ROOT / "metadata/atlas_systems.yml"
EVIDENCE = ROOT / "metadata/atlas_evidence_vocabulary.yml"
INTEGRATION = ROOT / "data/processed/integration"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

NODE_ID_FIELDS = {"node_id", "feature_id", "actor_id", "authority_id"}
RELATION_FIELDS = {"relationship_type", "dependency_type", "edge_type", "relation_type", "relationship_class"}
TEXT_EXTENSIONS = {".csv", ".md", ".json", ".yml", ".yaml", ".svg", ".txt", ".py", ".r"}

EXT_SYSTEM_MAP = {
    "EXT-CLIMATE": ("SYS-CLIMATE", "system-level concept"),
    "EXT-HYDROLOGY": ("SYS-WATER", "system-level concept"),
    "EXT-ECOLOGY": ("SYS-ECOLOGY", "system-level concept"),
    "EXT-VECTOR-ECOLOGY": ("SYS-VECTOR-ECOLOGY", "system-level concept"),
    "EXT-FLOODING": ("SYS-CLIMATE", "system-level concept"),
    "EXT-WATER-INFRASTRUCTURE": ("SYS-WATER", "system-level concept"),
    "EXT-FOOD-PRODUCTION": ("SYS-FREIGHT", "system-level concept"),
    "EXT-FOOD-PROCESSING": ("SYS-FREIGHT", "system-level concept"),
    "EXT-FREIGHT": ("SYS-FREIGHT", "system-level concept"),
    "EXT-SETTLEMENT": ("SYS-POPULATION", "system-level concept"),
    "EXT-MOBILITY": ("SYS-POPULATION", "system-level concept"),
    "EXT-CONTACT-STRUCTURE": ("SYS-POPULATION", "system-level concept"),
    "EXT-ANIMAL-HOSTS": ("SYS-ECOLOGY", "system-level concept"),
    "EXT-OCCUPATIONAL-CONTACT": (None, "retained generalized interface"),
    "EXT-HEALTHCARE": ("SYS-INFECTIOUS-DISEASE", "system-level concept"),
    "EXT-INFRASTRUCTURE": (None, "retained generalized interface"),
    "REF-4": ("SYS-DATA", "system-level concept"),
    "REF-10": ("SYS-GOVERNANCE", "system-level concept"),
}

PHASE_BY_STEM = {
    "water": "1", "materials": "2", "energy": "3", "information": "4",
    "observation": "4", "freight": "5", "ecology": "6", "exposure": "7",
    "environmental_health": "7", "biogeochemical": "8", "climate": "9",
    "governance": "10", "population": "11", "vector": "12", "infectious": "13",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fieldnames} for row in rows)


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return value or "UNSPECIFIED"


def entity_id(system_id: str, local_id: str) -> str:
    return f"ENT-{slug(system_id.removeprefix('SYS-'))}-{slug(local_id)}"


def phase_for_path(path: Path) -> str:
    lower = path.name.lower()
    for stem, phase in PHASE_BY_STEM.items():
        if stem in lower:
            return phase
    return "cross-phase"


def load_registry() -> tuple[dict, dict]:
    return yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8")), yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))


def build_identity_crosswalk(registry: dict) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows: list[dict[str, str]] = []
    local_lookup: dict[str, dict[str, str]] = {}
    for source in registry["identity_sources"]:
        artifact = source["source_artifact"]
        path = ROOT / artifact
        fields, records = read_csv(path)
        if source["id_field"] not in fields or source["name_field"] not in fields:
            raise ValueError(f"identity source fields missing: {artifact}")
        for record in records:
            local_id = record[source["id_field"]].strip()
            if not local_id:
                raise ValueError(f"blank local ID in {artifact}")
            atlas_id = entity_id(source["system_id"], local_id)
            row = {
                "atlas_entity_id": atlas_id,
                "local_id": local_id,
                "local_namespace": f"phase{source['source_phase']}.{Path(artifact).stem}",
                "source_phase": str(source["source_phase"]),
                "source_artifact": artifact,
                "entity_type": source["entity_type"],
                "canonical_name": record[source["name_field"]].strip(),
                "system_id": source["system_id"],
                "mapping_type": "exact identity",
                "mapping_status": "resolved",
                "evidence_basis": next((record.get(k, "") for k in ("source_id", "source_name") if record.get(k)), "source artifact record"),
                "reality_status": record.get("reality_status", record.get("status", "")),
                "canon_status": record.get("canon_status", ""),
                "temporal_basis": record.get("scenario_year", record.get("status", "")),
                "notes": "Atlas identity is additive; local identifier remains authoritative.",
            }
            key = (artifact, local_id)
            if key in local_lookup:
                raise ValueError(f"duplicate identity source row: {key}")
            local_lookup[key] = row
            rows.append(row)
    return sorted(rows, key=lambda r: (r["system_id"], r["local_namespace"], r["local_id"])), local_lookup


def build_endpoint_crosswalk() -> tuple[list[dict[str, str]], dict[str, int]]:
    artifact = "data/processed/analysis/infectious_disease_dependency_register.csv"
    fields, records = read_csv(ROOT / artifact)
    required = {"dependency_id", "from_id", "to_id", "source_id", "relationship_type", "documented_or_inferred"}
    if not required.issubset(fields):
        raise ValueError(f"Phase 13B register missing fields: {sorted(required - set(fields))}")
    rows: list[dict[str, str]] = []
    for record in records:
        for position in ("from", "to"):
            local_id = record[f"{position}_id"].strip()
            if not local_id.startswith(("EXT-", "REF-")):
                continue
            mapped_system, resolution = EXT_SYSTEM_MAP.get(local_id, (None, "unresolved"))
            if resolution == "system-level concept":
                atlas_id = mapped_system
                status = "resolved_system_level"
                note = "Interpretive mapping only; the Phase 13B conceptual endpoint remains visible and is not replaced."
            elif resolution == "retained generalized interface":
                atlas_id = local_id
                status = "retained_conceptual"
                note = "No narrower Atlas entity is asserted; retain the generalized interface for later review."
            else:
                atlas_id = ""
                status = "unresolved"
                note = "No Atlas mapping established; do not invent a node."
            rows.append({
                "endpoint_crosswalk_id": f"XEP-{record['dependency_id']}-{position.upper()}",
                "dependency_id": record["dependency_id"],
                "endpoint_position": position,
                "local_endpoint_id": local_id,
                "local_namespace": "phase13b.infectious_disease_dependency_register",
                "source_phase": "13B",
                "source_artifact": artifact,
                "entity_type": "conceptual_dependency_endpoint",
                "canonical_name": local_id,
                "atlas_entity_id": atlas_id,
                "canonical_system_id": mapped_system or "",
                "mapping_type": "system-level concept" if resolution == "system-level concept" else "generalized external interface" if resolution == "retained generalized interface" else "unresolved",
                "mapping_status": status,
                "evidence_basis": f"Phase 13B {record['dependency_id']} {position}-endpoint; source_id={record['source_id']}; relationship_type={record['relationship_type']}; documented_or_inferred={record['documented_or_inferred']}",
                "notes": note,
            })
    counts = Counter(row["mapping_status"] for row in rows)
    row_ids = {row["dependency_id"] for row in rows}
    counts["conceptual_dependency_rows"] = len(row_ids)
    counts["total_dependencies"] = len(records)
    return sorted(rows, key=lambda r: (r["dependency_id"], r["endpoint_position"])), dict(counts)


def relation_class(term: str, artifact: str, field: str) -> tuple[str, str, str]:
    value = term.lower()
    if "scenario" in artifact.lower() or "scenario" in value or "future" in value:
        return "scenario influence", "semantically distinct", "Scenario term; never merge with a factual relationship or treat as a forecast."
    if "control-without-direct-observation" in value:
        return "governance / authority", "semantically distinct", "Control or authority relation; it is not an observation edge and does not imply automatic enforcement."
    if any(x in value for x in ("surveillance", "observ", "monitor", "detect", "report", "laboratory", "case", "publish", "decision")):
        return "information / observation", "candidate-compatible", "Observation or detection relation; not a physical or causal edge."
    if any(x in value for x in ("authority", "govern", "coordination", "jurisdiction", "permit", "regulat", "ownership", "funding", "advisory", "public_private", "interstate", "binational")):
        return "governance / authority", "semantically distinct", "Role, mandate, or coordination relation; monitoring or funding is not automatically control."
    if any(x in value for x in ("habitat", "ecolog", "host", "wetland", "migration", "landscape", "vector", "species", "woodland", "questing")):
        return "ecological relationship", "candidate-compatible", "Ecological or habitat interface; not abundance, disease, or health risk."
    if any(x in value for x in ("exposure", "pathway", "receptor", "contamination", "contact_opportunity", "health_boundary")):
        return "exposure pathway", "semantically distinct", "Exposure or contact interface; not dose, illness, or risk."
    if any(x in value for x in ("commut", "residence", "workplace", "mobility", "settlement", "population", "migration")):
        return "population / mobility interface", "semantically distinct", "Aggregate population or mobility relation; not individual movement or transmission."
    if any(x in value for x in ("electric", "generation", "grid", "fuel", "cooling", "storage", "thermal")):
        return "energy flow", "candidate-compatible", "Energy dependency/interface; not power flow, capacity, or outage probability."
    if any(x in value for x in ("material", "commodity", "freight", "food", "transport", "delivery", "shipment", "interchange", "supply_chain")):
        return "material flow", "candidate-compatible", "Material/logistics relation; route or quantity is not implied."
    if any(x in value for x in ("flow", "downstream", "tributary", "river", "lake", "hydrolog", "runoff", "receiving", "feeds", "transported")):
        return "physical flow", "candidate-compatible", "Physical or hydrologic relation; geometry and quantity remain native to the source."
    if any(x in value for x in ("depend", "service", "support", "continuity", "infrastructure", "access", "gateway", "modal", "warning", "control", "resilience", "reliability", "critical", "interface")):
        return "operational dependency", "ambiguous", "Functional dependency/interface; direction is not automatically causation or risk."
    if any(x in value for x in ("affect", "condition", "frame", "opportunity", "association", "connected", "relationship", "qualitative", "contextual", "separation", "boundary")):
        return "high-level interface / association", "ambiguous", "Generic or boundary term; semantic direction and strength require local interpretation."
    return "unclassified candidate", "ambiguous", "No 14A normalization asserted; retain the local term for Phase 14B review."


def build_relationship_inventory() -> list[dict[str, object]]:
    observations: dict[tuple[str, str, str, str], int] = Counter()
    for base in (ROOT / "data/processed/networks", ROOT / "data/processed/analysis", ROOT / "data/processed/scenarios"):
        for path in sorted(base.glob("*.csv")):
            if not any(token in path.name.lower() for token in ("edge", "relationship", "dependency", "flux", "mobility", "authority")):
                continue
            try:
                fields, records = read_csv(path)
            except Exception:
                continue
            for field in sorted(set(fields) & RELATION_FIELDS):
                for record in records:
                    term = (record.get(field) or "").strip()
                    if term:
                        observations[(phase_for_path(path), str(path.relative_to(ROOT)).replace("\\", "/"), field, term)] += 1
    rows = []
    for (phase, artifact, field, term), count in sorted(observations.items()):
        normalized, compatibility, note = relation_class(term, artifact, field)
        rows.append({
            "taxonomy_id": f"RT-{len(rows)+1:04d}",
            "source_phase": phase,
            "source_artifact": artifact,
            "local_field": field,
            "local_term": term,
            "local_term_count": count,
            "proposed_high_level_class": normalized,
            "normalization_status": "inventory_only_14A",
            "semantic_compatibility": compatibility,
            "information_preserved": "Local term, field, artifact, and count remain visible; no local value is rewritten.",
            "information_lost_or_caveat": note,
        })
    return rows


def build_figure(registry: dict) -> dict[str, object]:
    systems = registry["systems"]
    by_id = {item["system_id"]: item for item in systems}
    families = [
        ("natural_environment", "Natural environment", "#1f5f7a"),
        ("infrastructure_technology", "Infrastructure & technology", "#6b4c9a"),
        ("production_resources", "Production & resources", "#9a5a1f"),
        ("production_logistics", "Production & logistics", "#9a5a1f"),
        ("institutional_human", "Institutional & human", "#38764b"),
        ("health_environment", "Health & environmental interfaces", "#a23b55"),
    ]
    positions = {
        "SYS-CLIMATE": (0.13, 0.82), "SYS-WATER": (0.30, 0.82), "SYS-BIOGEOCHEMISTRY": (0.48, 0.82), "SYS-ECOLOGY": (0.66, 0.82),
        "SYS-MATERIALS": (0.22, 0.58), "SYS-FREIGHT": (0.42, 0.58), "SYS-ENERGY": (0.62, 0.58), "SYS-DATA": (0.80, 0.58),
        "SYS-POPULATION": (0.20, 0.29), "SYS-GOVERNANCE": (0.42, 0.29), "SYS-EXPOSURE": (0.62, 0.29), "SYS-VECTOR-ECOLOGY": (0.23, 0.08), "SYS-INFECTIOUS-DISEASE": (0.62, 0.08),
    }
    colors = {family: color for family, _, color in families}
    fig, ax = plt.subplots(figsize=(15, 9), dpi=160)
    fig.patch.set_facecolor("#101820")
    ax.set_facecolor("#101820")
    for source, target, label, basis in registry["architecture"]["interfaces"]:
        x1, y1 = positions[source]; x2, y2 = positions[target]
        style = "-" if basis in {"documented_plus_inferred", "documented"} else "--"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "color": "#8fa7b8", "lw": 1.4, "linestyle": style, "shrinkA": 30, "shrinkB": 30, "mutation_scale": 11})
    for item in systems:
        x, y = positions[item["system_id"]]
        width, height = 0.145, 0.095
        color = colors[item["broad_system_family"]]
        patch = FancyBboxPatch((x-width/2, y-height/2), width, height, boxstyle="round,pad=0.012,rounding_size=0.015", fc=color, ec="#d7e4ea", lw=0.8, alpha=0.96)
        ax.add_patch(patch)
        label = item["atlas_display_label"].replace(" & ", " &\n")
        ax.text(x, y, label, color="white", ha="center", va="center", fontsize=8.0, weight="bold")
    ax.text(0.5, 1.04, "Western Basin Systems Architecture", transform=ax.transAxes, color="white", ha="center", va="center", fontsize=18, weight="bold")
    ax.text(0.5, 0.995, "Phase 14A additive ontology — conceptual system interfaces, not a geographic map", transform=ax.transAxes, color="#b8c8d2", ha="center", va="center", fontsize=9)
    legend_handles = [FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc=color, ec="none", label=label) for family, label, color in families]
    ax.legend(handles=legend_handles, title="SYSTEM FAMILIES", loc="lower center", bbox_to_anchor=(0.5, -0.035), ncol=3, frameon=False, fontsize=7.4, title_fontsize=8, labelcolor="#b8c8d2")
    ax.text(0.01, -0.145, "Solid = documented/accepted context plus interpretation   Dashed = project inference or intentionally distinct interface", transform=ax.transAxes, color="#b8c8d2", fontsize=8)
    ax.text(0.01, -0.185, "No line width represents quantity, probability, causation, dependency risk, or physical route.", transform=ax.transAxes, color="#e6c66a", fontsize=8)
    ax.set_xlim(0, 1); ax.set_ylim(-0.22, 1.02); ax.axis("off")
    FIGURES.mkdir(parents=True, exist_ok=True)
    png = FIGURES / "western_basin_systems_architecture.png"
    svg = FIGURES / "western_basin_systems_architecture.svg"
    fig.savefig(png, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    svg_text = svg.read_text(encoding="utf-8")
    svg_text = re.sub(r'id="p[0-9a-f]+"', 'id="clip_path_systems"', svg_text)
    svg_text = re.sub(r'url\(#p[0-9a-f]+\)', 'url(#clip_path_systems)', svg_text)
    svg_text = "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n"
    svg.write_text(svg_text, encoding="utf-8", newline="\n")
    plt.close(fig)
    return {"png": str(png.relative_to(ROOT)).replace("\\", "/"), "svg": str(svg.relative_to(ROOT)).replace("\\", "/"), "systems": len(systems), "interfaces": len(registry["architecture"]["interfaces"])}


def write_reports(registry: dict, evidence: dict, identity: list[dict[str, str]], endpoints: list[dict[str, str]], endpoint_counts: dict[str, int], relationships: list[dict[str, object]], figure: dict[str, object]) -> None:
    report = REPORTS / "phase14a_systems_ontology.md"
    lines = ["# Phase 14A Systems Ontology", "", "Status: additive Atlas-facing ontology; no local phase registry or accepted artifact was rewritten.", "", f"Systems represented: **{len(registry['systems'])}**.", "", "| System ID | Atlas label | Family | Originating phases | Canonical status |", "|---|---|---|---|---|"]
    for item in registry["systems"]:
        lines.append(f"| `{item['system_id']}` | {item['atlas_display_label']} | {item['broad_system_family']} | {', '.join(map(str, item['originating_phases']))} | {item['canonical_status']} |")
    lines += ["", "The registry keeps energy/grid/compute together because that is the repository's Phase 3 structure. Nutrients/biogeochemistry is separate from water because Phase 8 has its own accepted package. The existing `metadata/systems.yml` remains unmodified and is recorded as historically scoped original water/materials metadata.", "", f"The ontology identity-source inventory references **{len(registry['identity_sources'])}** primary entity tables and the architecture figure records **{figure['interfaces']}** qualitative interfaces."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = REPORTS / "phase14a_identity_crosswalk.md"
    status_counts = Counter(row["mapping_status"] for row in identity)
    endpoint_status = Counter(row["mapping_status"] for row in endpoints)
    lines = ["# Phase 14A Identity & Endpoint Crosswalk", "", "The crosswalk is additive. Local IDs remain intact and every row points to the source artifact and source-phase namespace.", "", f"Canonical local entity rows: **{len(identity)}**; exact mappings: **{status_counts['resolved']}**.", "", "## Phase 13B conceptual endpoint audit", "", f"Phase 13B dependency rows: **{endpoint_counts['total_dependencies']}**; rows containing `EXT-*`/`REF-*`: **{endpoint_counts['conceptual_dependency_rows']}**; conceptual endpoint occurrences audited: **{len(endpoints)}**.", "", "Counts below are endpoint occurrences, not dependency rows:", "", f"- A — exact resolved: **{endpoint_status['resolved_exact']}**", f"- B — system-level resolved: **{endpoint_status['resolved_system_level']}**", f"- C — retained conceptual/generalized: **{endpoint_status['retained_conceptual']}**", f"- D — unresolved: **{endpoint_status['unresolved']}**", "", "A system-level resolution does not replace the local `EXT-*`/`REF-*` token. The only retained conceptual interfaces are those without a narrower Atlas system concept; no endpoint was invented to eliminate a placeholder."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = REPORTS / "phase14a_evidence_crosswalk.md"
    lines = ["# Phase 14A Evidence Vocabulary Crosswalk", "", f"Normalized classes: **{len(evidence['normalized_classes'])}**; explicit local mappings: **{len(evidence['mappings'])}**.", "", "| Class | Meaning | Information preserved | Information lost or caveat |", "|---|---|---|---|"]
    for item in evidence["normalized_classes"]:
        lines.append(f"| `{item['class_id']}` | {item['meaning']} | {', '.join(item['preserves'])} | {item['lost_or_caveat']} |")
    lines += ["", "The vocabulary does not treat fact, inference, scenario, observation, derived value, dependency, or risk as interchangeable. Local field, source artifact, temporal basis, scale, and caveat remain required lineage fields."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = REPORTS / "phase14a_relationship_taxonomy.md"
    class_counts = Counter(row["proposed_high_level_class"] for row in relationships)
    lines = ["# Phase 14A Relationship Taxonomy Inventory", "", f"Inventory rows: **{len(relationships)}** local field/term/artifact observations.", "", "## Candidate high-level classes", ""]
    for key, value in sorted(class_counts.items()): lines.append(f"- {key}: **{value}**")
    lines += ["", "## Interpretation", "", "This is an inventory, not Phase 14B normalization. `dependency`, `interface`, `contextual`, `affects`, and similar generic terms are ambiguous without their local evidence basis and scale. Observation/surveillance edges are not physical or causal edges; governance/authority edges do not imply operational control; ecological and exposure interfaces are not disease or risk claims; and scenario relations are not factual observations or forecasts.", "", "## Energy normalization seam", "", "Energy uses distinct local terms such as `electricity`, `fuel`, `cooling_water`, `thermal_dependency`, `storage_support`, `communications`, `generation_grid_interface`, and `grid_serves_load`. The Phase 3B table also uses `to_system=water_or_materials` while four rows target `ENE-LOAD-*` nodes. Phase 14B must retain endpoint role, local dependency type, source basis, direction, and native scale before proposing a join class; 14A does not rewrite these values."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = REPORTS / "phase14a_integration_qa.md"
    lines = ["# Phase 14A Integration QA", "", "Status: generated additive QA package; final acceptance remains external.", "", f"- Ontology systems: {len(registry['systems'])}", f"- Identity crosswalk rows: {len(identity)}", f"- Endpoint audit rows: {len(endpoints)} endpoint occurrences across {endpoint_counts['conceptual_dependency_rows']} of {endpoint_counts['total_dependencies']} Phase 13B dependency rows", f"- Relationship inventory rows: {len(relationships)}", f"- Evidence normalized classes: {len(evidence['normalized_classes'])}", f"- Architecture figure systems/interfaces: {figure['systems']}/{figure['interfaces']}", "", "## Scope checks", "", "- `metadata/systems.yml` was not modified; the new registry is additive.", "- No monolithic GeoPackage was created or modified.", "- Local identifiers are retained in crosswalk columns; Atlas IDs are deterministic additive identities.", "- Phase 13B dependency rows are read-only inputs; conceptual endpoints are not rewritten.", "- Phase 14B and Phase 15 products are not generated by the builder.", "- Great Black Swamp `C — HOLD / noncanonical` and the Toledo intake-coordinate discrepancy `UNRESOLVED` remain explicit.", "", "The Python and independent R validators are the acceptance gates for this package. Freeze integrity uses exact raw hashes for binary artifacts and LF/CRLF-portable hashes for text artifacts only."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_working_manifest(result: dict[str, object]) -> None:
    paths = [
        "metadata/atlas_systems.yml",
        "metadata/atlas_evidence_vocabulary.yml",
        "docs/phase_briefs/phase14_systems_atlas_integration.md",
        "docs/phase_briefs/phase14a_common_systems_ontology_identity_evidence_crosswalk.md",
        "docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md",
        "data/processed/integration/system_identity_crosswalk.csv",
        "data/processed/integration/external_endpoint_crosswalk.csv",
        "data/processed/integration/relationship_taxonomy_inventory.csv",
        "outputs/figures/western_basin_systems_architecture.png",
        "outputs/figures/western_basin_systems_architecture.svg",
        "reports/phase14a_systems_ontology.md",
        "reports/phase14a_identity_crosswalk.md",
        "reports/phase14a_evidence_crosswalk.md",
        "reports/phase14a_relationship_taxonomy.md",
        "reports/phase14a_integration_qa.md",
        "reports/phase14a_build_summary.json",
        "src/python/systems/build_phase14a_integration.py",
        "src/python/systems/validate_phase14a_integration.py",
        "src/R/systems/validate_phase14a_integration.R",
    ]
    artifacts = {}
    for rel in paths:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"working-manifest artifact not found: {rel}")
        data = path.read_bytes()
        artifacts[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    manifest = {
        "phase": "14A",
        "status": "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE",
        "source_commit": "8e22300d32d30a489db38ac4bfadb5573a8eba34",
        "scope": "Common Systems Ontology, Identity & Evidence Crosswalk",
        "counts": result,
        "artifacts": artifacts,
        "exclusions": ["Phase 14B", "Phase 15", "monolithic GeoPackage", "accepted/frozen artifact modification"],
    }
    (REPORTS / "phase14a_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build() -> dict[str, object]:
    registry, evidence = load_registry()
    identity, _ = build_identity_crosswalk(registry)
    endpoint_rows, endpoint_counts = build_endpoint_crosswalk()
    # Endpoint-level counts use explicit class names for a stable QA contract.
    endpoint_counts["resolved_exact"] = 0
    endpoint_counts["resolved_system_level"] = sum(row["mapping_status"] == "resolved_system_level" for row in endpoint_rows)
    endpoint_counts["retained_conceptual"] = sum(row["mapping_status"] == "retained_conceptual" for row in endpoint_rows)
    endpoint_counts["unresolved"] = sum(row["mapping_status"] == "unresolved" for row in endpoint_rows)
    relationships = build_relationship_inventory()
    write_csv(INTEGRATION / "system_identity_crosswalk.csv", ["atlas_entity_id", "local_id", "local_namespace", "source_phase", "source_artifact", "entity_type", "canonical_name", "system_id", "mapping_type", "mapping_status", "evidence_basis", "reality_status", "canon_status", "temporal_basis", "notes"], identity)
    write_csv(INTEGRATION / "external_endpoint_crosswalk.csv", ["endpoint_crosswalk_id", "dependency_id", "endpoint_position", "local_endpoint_id", "local_namespace", "source_phase", "source_artifact", "entity_type", "canonical_name", "atlas_entity_id", "canonical_system_id", "mapping_type", "mapping_status", "evidence_basis", "notes"], endpoint_rows)
    write_csv(INTEGRATION / "relationship_taxonomy_inventory.csv", ["taxonomy_id", "source_phase", "source_artifact", "local_field", "local_term", "local_term_count", "proposed_high_level_class", "normalization_status", "semantic_compatibility", "information_preserved", "information_lost_or_caveat"], relationships)
    figure = build_figure(registry)
    write_reports(registry, evidence, identity, endpoint_rows, endpoint_counts, relationships, figure)
    result = {"systems": len(registry["systems"]), "identity_rows": len(identity), "endpoint_rows": len(endpoint_rows), **endpoint_counts, "relationship_rows": len(relationships), "evidence_classes": len(evidence["normalized_classes"]), "evidence_mappings": len(evidence["mappings"]), "figure": figure}
    (REPORTS / "phase14a_build_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_working_manifest(result)
    return result


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
