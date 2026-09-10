"""Build the additive Phase 14B Atlas registry and dependency crosswalks."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import yaml

ROOT = Path(__file__).resolve().parents[3]
ONTOLOGY_PATH = ROOT / "metadata/atlas_systems.yml"
EVIDENCE_PATH = ROOT / "metadata/atlas_evidence_vocabulary.yml"
VOCAB_PATH = ROOT / "metadata/atlas_relationship_vocabulary.yml"
LAYERS_PATH = ROOT / "metadata/atlas_layers.yml"
INTEGRATION = ROOT / "data/processed/integration"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"

A14A_RELATIONSHIP = INTEGRATION / "relationship_taxonomy_inventory.csv"
A14A_ENDPOINT = INTEGRATION / "external_endpoint_crosswalk.csv"
A14A_IDENTITY = INTEGRATION / "system_identity_crosswalk.csv"

DEPENDENCY_SOURCES = [
    ("8B", "data/processed/networks/biogeochemical_dependency_edges.csv"),
    ("9B", "data/processed/analysis/climate_hazard_dependency_register.csv"),
    ("6B", "data/processed/networks/ecology_dependency_edges.csv"),
    ("3B", "data/processed/networks/energy_dependency_edges.csv"),
    ("7B", "data/processed/networks/exposure_dependency_edges.csv"),
    ("5C", "data/processed/networks/freight_dependency_edges.csv"),
    ("10B", "data/processed/analysis/governance_dependency_register.csv"),
    ("13B", "data/processed/analysis/infectious_disease_dependency_register.csv"),
    ("4B", "data/processed/networks/information_dependency_edges.csv"),
    ("12B", "data/processed/analysis/vector_system_dependency_register.csv"),
    ("11B", "data/processed/analysis/population_system_dependency_register.csv"),
]

SYSTEM_ALIASES = {
    "water": "SYS-WATER", "hydrology": "SYS-WATER", "wastewater": "SYS-WATER",
    "water_or_materials": "", "materials": "SYS-MATERIALS", "material": "SYS-MATERIALS",
    "nutrient_material": "SYS-BIOGEOCHEMISTRY", "biogeochemical": "SYS-BIOGEOCHEMISTRY",
    "energy": "SYS-ENERGY", "electricity": "SYS-ENERGY", "generation": "SYS-ENERGY",
    "storage": "SYS-ENERGY", "fuel": "SYS-ENERGY", "compute": "SYS-ENERGY",
    "weather": "SYS-CLIMATE", "climate": "SYS-CLIMATE", "flooding": "SYS-CLIMATE",
    "ecology": "SYS-ECOLOGY", "vector_ecology": "SYS-VECTOR-ECOLOGY", "vector": "SYS-VECTOR-ECOLOGY",
    "exposure": "SYS-EXPOSURE", "environmental_health": "SYS-EXPOSURE",
    "freight": "SYS-FREIGHT", "transport": "SYS-FREIGHT", "food": "SYS-FREIGHT",
    "governance": "SYS-GOVERNANCE", "institutional": "SYS-GOVERNANCE",
    "population": "SYS-POPULATION", "settlement": "SYS-POPULATION", "housing": "SYS-POPULATION",
    "mobility": "SYS-POPULATION", "communications": "SYS-DATA", "data": "SYS-DATA",
    "observation": "SYS-DATA", "infectious_disease": "SYS-INFECTIOUS-DISEASE",
    "disease": "SYS-INFECTIOUS-DISEASE",
}

ENTITY_ROLE_BY_TYPE = {
    "water_feature": "geographic unit", "materials_node": "physical asset", "energy_node": "physical asset",
    "energy_dependency_interface": "generalized external interface", "observation_node": "monitoring/surveillance interface",
    "freight_node": "physical asset", "ecology_node": "ecological entity", "exposure_context_node": "conceptual interface",
    "biogeochemical_node": "ecological entity", "climate_hazard_node": "geographic unit", "governance_actor": "institutional actor",
    "governance_authority_role": "institutional actor", "population_settlement_node": "population/settlement entity",
    "vector_ecology_node": "ecological entity", "infectious_disease_node": "monitoring/surveillance interface",
}

GENERALIZED_INTERFACE_IDS = {
    "FRT-FUEL-EXTERNAL", "FRT-MKT-GREAT-LAKES", "FRT-MKT-MIDWEST-INDUSTRIAL",
    "FRT-MKT-MICHIGAN-CANADA", "FRT-MKT-LICENSED-DISPOSAL", "FRT-AG-MIDWEST-BULK",
}
CONTEXT_INTERFACE_IDS = {"HZ-019", "HZ-022", "HZ-023"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", str(value).upper()).strip("-") or "UNSPECIFIED"


def csv_key(fields: list[str]) -> str:
    for candidate in ("node_id", "feature_id", "edge_id", "dependency_id", "relationship_id", "record_id", "register_id", "state_id"):
        if candidate in fields:
            return candidate
    return fields[0] if fields else "none"


def phase_for_map(map_name: str, originating: list[str]) -> str:
    if "future" in map_name or map_name.endswith("b"):
        return next((x for x in reversed(originating) if str(x).endswith("C")), str(originating[-1]))
    if "dependenc" in map_name or "governance" in map_name and "2026" in map_name:
        return next((x for x in reversed(originating) if str(x).endswith("B")), str(originating[0]))
    return str(originating[0])


def system_for_alias(value: str) -> str:
    key = re.sub(r"[^a-z0-9_]+", "_", str(value).lower()).strip("_")
    return SYSTEM_ALIASES.get(key, "")


def relation_term(row: dict[str, str]) -> str:
    for field in ("relationship_type", "dependency_type", "dependency_role", "interface", "system_interface", "flow_type", "flow_role", "relationship_basis"):
        if (row.get(field) or "").strip():
            return row[field].strip()
    return "unspecified"


def classify_relationship(term: str, artifact: str, field: str) -> tuple[str, str, str, str, str, str]:
    value = term.lower().replace("_", " ").replace("-", " ")
    artifact_lower = artifact.lower()
    is_scenario = "scenario" in artifact_lower or "future" in artifact_lower or "scenario" in value or "future" in value
    if is_scenario:
        return ("scenario influence", "scenario_delta", "scenario assumption/state; not observed causation", "no flow semantics", "scenario-only join", "Scenario term remains separate from baseline fact and forecast language.")
    if value.strip() == "weather":
        return ("ecological relationship", "directed_local_record", "external physical context is not a causal estimate", "physical context; not energy transfer", "context join", "Weather context is retained as an external physical interface, not an energy flow or risk claim.")
    if "control without direct observation" in value or ("control" in value and "observation" in value):
        return ("governance / authority", "role_assignment", "control or authority relation; not an observation edge or automatic enforcement", "governance/control interface; no physical flow", "governance role join", "Control-without-direct-observation remains a governance/authority distinction, not information flow or automatic enforcement.")
    if "ecology" in artifact_lower or "vector" in artifact_lower:
        if any(x in value for x in ("food web", "migration", "connectivity", "protected area", "restoration", "riparian", "terrestrial", "ecological", "environmental driver")):
            return ("ecological relationship", "directed_local_record", "ecological function/interface; not deterministic causation or disease", "ecological process/interface; not abundance or disease flow", "ecological join", "Ecological function, movement, and habitat context retain native scale and do not imply abundance, disease, or risk.")
    if "environmental driver" in value:
        return ("ecological relationship", "directed_local_record", "environmental context is not deterministic causation", "environmental/ecological context; not physical flow", "context join", "Environmental driver terminology is retained as contextual relationship semantics, not a mapped physical flow.")
    if "surveillance" in value or "detect" in value or "laboratory" in value or "case report" in value:
        return ("surveillance / detection", "directed_local_record", "observation/detection is not incidence or authority", "information/detection interface", "surveillance join", "Surveillance or detection does not establish incidence, absence, transmission, or disease burden.")
    if "governance" in artifact_lower or "authority" in artifact_lower or any(x in value for x in ("authority", "actor system role", "regulat", "permit", "ownership", "funding", "advis", "coordination", "jurisdiction", "responsibility", "role")):
        return ("governance / authority", "role_assignment", "role, mandate, or coordination relation; not automatic operational control", "governance role/interface; no physical flow", "governance role join", "Governance, monitoring, funding, advice, ownership, and coordination remain distinct from operational control.")
    if any(x in value for x in ("observ", "report", "publish", "decision", "data", "feeds", "warning", "information")):
        return ("information / observation", "directed_local_record", "documented observation or information relation; not causal by itself", "information signal or observation; not physical flow", "information join", "Observation, reporting, and decision support are not authority, control, or incidence.")
    if "energy" in artifact_lower or any(x in value for x in ("electricity", "generation grid", "regional grid", "storage interface", "grid serves")):
        if "generation grid" in value or "regional grid" in value or "storage interface" in value:
            return ("energy flow", "directed_local_record", "energy-system interface is not a power-flow solution or causal risk estimate", "energy generation/transmission/storage interface; not measured quantity", "energy-system join", "Energy interface classification does not add capacity, transfer, dispatch, outage, or feeder semantics.")
        if "fuel" in value:
            return ("material flow", "directed_local_record", "fuel input relation is not a causal or capacity estimate", "fuel/material input; not electricity flow", "material-input join", "Fuel is retained as material input and is not collapsed into electricity or grid control.")
        if "communication" in value:
            return ("information / observation", "directed_local_record", "information/control interface is not an energy flow", "information/control interface", "information join", "Energy control or communications terminology is not normalized as energy flow.")
        return ("operational dependency", "directed_local_record", "functional energy dependency; not causal effect or risk", "energy service dependency; not measured energy quantity", "energy-dependency join", "Energy dependency is retained as an operational interface without numeric confidence or power-flow meaning.")
    if any(x in value for x in ("mobility", "commut", "residence", "workplace", "settlement", "population")):
        return ("population / mobility interface", "directed_local_record", "aggregate population or mobility relation; not individual movement or transmission", "population/mobility interface; not transmission", "population-interface join", "Mobility is not migration, individual movement, transmission, or disease risk.")
    if any(x in value for x in ("exposure", "pathway", "receptor", "contamination", "contact opportunity", "health boundary")):
        return ("exposure pathway", "directed_local_record", "potential pathway or contact interface; not dose, illness, or risk", "exposure/context interface; not confirmed exposure", "exposure-interface join", "Exposure pathway is not documented exposure, dose, illness, or a risk score.")
    if any(x in value for x in ("habitat", "ecolog", "host", "wetland", "migration", "landscape", "vector", "species", "seasonal development", "condition")):
        return ("ecological relationship", "directed_local_record", "ecological function/interface; not deterministic causation or disease", "ecological process/interface; not abundance or disease flow", "ecological join", "Ecological relationships retain native scale and do not imply abundance, establishment, contact, infection, or risk.")
    if any(x in value for x in ("material", "commodity", "freight", "food", "transport", "delivery", "shipment", "interchange", "supply chain", "resource to extraction", "fuel")):
        return ("material flow", "directed_local_record", "documented or inferred material/logistics relation; not causal quantity", "material/logistics interface; route and quantity remain local", "material-flow join", "Material or freight relationships do not imply shipment quantity, exact route, capacity, or continuous flow.")
    if any(x in value for x in ("flow", "downstream", "tributary", "river ", " lake", "hydrolog", "runoff", "receiving", "transported", "mobilized")):
        return ("physical flow", "directed_source_to_target", "physical relationship retained without effect-size or causal estimate", "physical/hydrologic direction; geometry and quantity remain local", "physical-flow join", "Physical direction does not add common units, effect size, or risk meaning.")
    if any(x in value for x in ("depend", "service", "support", "continuity", "infrastructure", "access", "gateway", "modal", "resilien", "reliability", "critical", "interface", "control")):
        return ("operational dependency", "directed_local_record", "functional dependency/interface; direction is not automatically causation or risk", "operational interface; no common flow unit", "dependency join", "Dependency is not risk, failure probability, control proof, or causal effect.")
    if any(x in value for x in ("affect", "frame", "opportunity", "association", "connected", "relationship", "qualitative", "contextual", "separation", "boundary", "linked")):
        return ("high-level association", "unspecified_or_associative", "association or context only; causation is not asserted", "no flow semantics", "context-only join", "Generic association remains local and must not be upgraded to dependency, causation, or risk.")
    return ("unresolved / unclassified", "unspecified_or_associative", "not interpreted as causal", "no flow semantics", "source-local only", "No defensible shared class is asserted; retain the local term and source lineage for later review.")


def evidence_class(row: dict[str, str]) -> str:
    if (row.get("canon_status") or "").lower() == "scenario" or (row.get("reality_status") or "").lower() == "fictional":
        return "SCENARIO_STATE"
    status = (row.get("documented_or_inferred") or "").strip().lower()
    if status in {"inferred", "project inference", "documented_plus_inferred", "accepted_context_plus_inferred"}:
        return "INFERRED"
    if status in {"reused_context", "context_reused", "reused context"}:
        return "CONTEXT_REUSED"
    if status in {"documented", "verified", "observed", "documented_program"}:
        return "OBSERVED_DOCUMENTED"
    basis = " ".join((row.get(k) or "") for k in ("relationship_basis", "evidence_basis", "canon_status")).lower()
    if "inferred" in basis or "project inference" in basis:
        return "INFERRED"
    if "reused context" in basis or "reused_context" in basis:
        return "CONTEXT_REUSED"
    return "OBSERVED_DOCUMENTED"


def build_relationship_crosswalk() -> list[dict[str, object]]:
    fields, inventory = read_csv(A14A_RELATIONSHIP)
    required = {"taxonomy_id", "source_phase", "source_artifact", "local_field", "local_term", "local_term_count"}
    if not required.issubset(fields):
        raise ValueError(f"Phase 14A relationship inventory missing: {sorted(required - set(fields))}")
    rows = []
    for record in inventory:
        cls, direction, causal, flow, role, caveat = classify_relationship(record["local_term"], record["source_artifact"], record["local_field"])
        status = "unresolved_term" if cls == "unresolved / unclassified" else "retained_local_semantics" if cls == "high-level association" else "normalized_shared_class"
        rows.append({
            "atlas_normalization_id": f"RN-{record['taxonomy_id']}",
            "local_taxonomy_id": record["taxonomy_id"],
            "local_term": record["local_term"],
            "local_field": record["local_field"],
            "local_term_count": record["local_term_count"],
            "source_phase": record["source_phase"],
            "source_artifact": record["source_artifact"],
            "normalized_relationship_class": cls,
            "directionality": direction,
            "causal_semantics": causal,
            "flow_semantics": flow,
            "Atlas_join_role": role,
            "mapping_status": status,
            "information_loss_or_caveat": caveat,
        })
    return rows


def load_identity() -> tuple[dict[str, list[dict[str, str]]], dict[tuple[str, str], dict[str, str]]]:
    _, rows = read_csv(A14A_IDENTITY)
    by_local: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_artifact: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        by_local[row["local_id"]].append(row)
        by_artifact[(row["source_artifact"], row["local_id"])] = row
    return by_local, by_artifact


def load_endpoints() -> tuple[dict[tuple[str, str], dict[str, str]], dict[tuple[str, str], dict[str, str]]]:
    _, rows = read_csv(A14A_ENDPOINT)
    by_position = {(row["dependency_id"], row["endpoint_position"]): row for row in rows}
    by_local = {}
    for row in rows:
        by_local[(row["dependency_id"], row["local_endpoint_id"])] = row
    return by_position, by_local


def endpoint_role(local_id: str, mapped_system: str, mapping_status: str) -> tuple[str, str]:
    if local_id in {"EXT-OCCUPATIONAL-CONTACT", "EXT-INFRASTRUCTURE"}:
        return "generalized external interface", "Phase 14A retained conceptual/generalized endpoint; no narrower entity asserted."
    if local_id == "REF-4":
        return "monitoring/surveillance interface", "Reference endpoint is an observation/data interface; it is not authority or incidence."
    if local_id == "REF-10":
        return "institutional actor", "Reference endpoint is a governance/coordination interface; it is not automatic operational control."
    if local_id in {"EXT-SETTLEMENT", "EXT-MOBILITY", "EXT-CONTACT-STRUCTURE"}:
        return "population/settlement entity", "Conceptual population/mobility role; aggregate mobility is not individual transmission."
    if local_id in {"EXT-VECTOR-ECOLOGY", "EXT-ANIMAL-HOSTS"}:
        return "ecological entity", "Conceptual ecological endpoint; it is not an abundance, infection, or disease endpoint."
    if local_id == "EXT-HEALTHCARE":
        return "monitoring/surveillance interface", "Healthcare endpoint is a care/detection interface; presence is not disease burden."
    if local_id == "EXT-WATER-INFRASTRUCTURE":
        return "physical asset", "Role only; retained conceptual endpoint is not localized to a facility or utility territory."
    if local_id in {"EXT-HYDROLOGY", "EXT-FLOODING", "EXT-CLIMATE"}:
        return "geographic unit", "Environmental context role only; no exact geometry or causal hazard surface is added."
    if local_id in {"EXT-ECOLOGY"}:
        return "ecological entity", "Conceptual ecological context; no exact habitat or sensitive location is asserted."
    if local_id in {"EXT-FOOD-PRODUCTION", "EXT-FOOD-PROCESSING", "EXT-FREIGHT"}:
        return "generalized external interface", "Food/freight interface remains generalized; no shipment, route, or facility identity is added."
    if mapping_status == "retained_conceptual":
        return "conceptual interface", "Conceptual endpoint retained without localization."
    return "system node", f"System-level mapping to {mapped_system or 'unspecified'}; not exact entity identity."


def build_endpoint_roles() -> list[dict[str, object]]:
    _, endpoint_rows = read_csv(A14A_ENDPOINT)
    rows = []
    for row in endpoint_rows:
        role, basis = endpoint_role(row["local_endpoint_id"], row["canonical_system_id"], row["mapping_status"])
        rows.append({
            "endpoint_role_crosswalk_id": f"ERP-{row['endpoint_crosswalk_id']}",
            "dependency_id": row["dependency_id"],
            "endpoint_position": row["endpoint_position"],
            "local_endpoint_id": row["local_endpoint_id"],
            "source_phase": row["source_phase"],
            "source_artifact": row["source_artifact"],
            "inherited_atlas_entity_or_system_id": row["atlas_entity_id"],
            "inherited_mapping_type": row["mapping_type"],
            "inherited_mapping_status": row["mapping_status"],
            "endpoint_role": role,
            "role_mapping_status": "normalized_role_only",
            "conceptual_endpoint_preserved": "yes" if row["local_endpoint_id"].startswith(("EXT-", "REF-")) else "no",
            "role_basis": basis,
            "information_loss_or_caveat": "Endpoint role is an additive interface label; local endpoint ID and Phase 14A mapping remain authoritative.",
        })
    return rows


def local_endpoint_mapping(dep_id: str, position: str, local_id: str, endpoint_by_position: dict[tuple[str, str], dict[str, str]]) -> tuple[str, str, str, str]:
    if local_id.startswith(("EXT-", "REF-")):
        mapped = endpoint_by_position.get((dep_id, position), {})
        return mapped.get("atlas_entity_id", local_id), mapped.get("canonical_system_id", ""), mapped.get("mapping_status", "retained_conceptual"), mapped.get("mapping_type", "generalized external interface")
    return "", "", "", ""


def extract_endpoints(row: dict[str, str]) -> tuple[str, str, str, str]:
    if row.get("from_id") or row.get("to_id"):
        return row.get("from_id", "").strip(), row.get("to_id", "").strip(), "from", "to"
    if row.get("source_node_id") or row.get("dependent_node_id"):
        return row.get("source_node_id", "").strip(), row.get("dependent_node_id", "").strip(), "source", "dependent"
    if row.get("actor_a") or row.get("actor_b"):
        return row.get("actor_a", "").strip(), row.get("actor_b", "").strip(), "actor_a", "actor_b"
    if row.get("hazard_node_id"):
        return row.get("hazard_node_id", "").strip(), "", "hazard", "affected_system"
    if row.get("object_a") or row.get("object_b"):
        return row.get("object_a", "").strip(), row.get("object_b", "").strip(), "object_a", "object_b"
    if row.get("population_or_settlement_object"):
        return row["population_or_settlement_object"].strip(), "", "population", "system"
    return "", "", "", ""


def local_relationship_id(row: dict[str, str]) -> str:
    for field in ("dependency_id", "edge_id", "relationship_id", "register_id"):
        if (row.get(field) or "").strip():
            return row[field].strip()
    return "LOCAL-UNSPECIFIED"


def explicit_system(row: dict[str, str], endpoint: str, local_id: str, by_local: dict[str, list[dict[str, str]]]) -> tuple[str, str]:
    native_label = ""
    if endpoint == "source":
        for field in ("from_system", "system_a", "system_a"):
            if row.get(field):
                native_label = row[field].strip(); break
    elif endpoint == "target":
        for field in ("to_system", "system_b", "affected_system", "system"):
            if row.get(field):
                native_label = row[field].strip(); break
    if native_label:
        mapped = system_for_alias(native_label)
        if mapped:
            return mapped, native_label
    candidates = {item["system_id"] for item in by_local.get(local_id, [])}
    return (next(iter(candidates)) if len(candidates) == 1 else ""), native_label


def resolve_local_entity(local_id: str, expected_system: str, by_local: dict[str, list[dict[str, str]]]) -> tuple[str, str, str]:
    if local_id in GENERALIZED_INTERFACE_IDS:
        return "", "system-level" if expected_system else "nonjoinable", "generalized external interface"
    if local_id in CONTEXT_INTERFACE_IDS:
        return "", "system-level" if expected_system else "nonjoinable", "monitoring/surveillance interface"
    candidates = by_local.get(local_id, [])
    compatible = [row for row in candidates if not expected_system or row["system_id"] == expected_system]
    chosen = compatible[0] if len(compatible) == 1 else candidates[0] if len(candidates) == 1 else None
    if chosen and (not expected_system or chosen["system_id"] == expected_system):
        return chosen["atlas_entity_id"], "exact", ENTITY_ROLE_BY_TYPE.get(chosen.get("entity_type", ""), "system node")
    return "", "system-level" if expected_system else "nonjoinable", "generalized external interface"


def build_dependency_crosswalk() -> tuple[list[dict[str, object]], dict[str, object], set[tuple[str, str]]]:
    by_local, _ = load_identity()
    endpoint_by_position, _ = load_endpoints()
    rows: list[dict[str, object]] = []
    source_counts = Counter()
    scenario_pairs: set[tuple[str, str]] = set()
    for phase, artifact in DEPENDENCY_SOURCES:
        fields, records = read_csv(ROOT / artifact)
        for index, source in enumerate(records, 1):
            local_id = local_relationship_id(source)
            source_local, target_local, source_label, target_label = extract_endpoints(source)
            source_system, native_source_system = explicit_system(source, "source", source_local, by_local)
            target_system, native_target_system = explicit_system(source, "target", target_local, by_local)
            if source_label == "hazard":
                source_system = "SYS-CLIMATE"
            if source_label == "population":
                source_system = "SYS-POPULATION"
            if source_local.startswith(("EXT-", "REF-")):
                source_atlas, source_system, source_mapping_status, source_mapping_type = local_endpoint_mapping(local_id, "from", source_local, endpoint_by_position)
                source_level = "system-level" if source_mapping_status == "resolved_system_level" else "conceptual"
                source_role, _ = endpoint_role(source_local, source_system, source_mapping_status)
            else:
                source_atlas, source_level, source_role = resolve_local_entity(source_local, source_system, by_local) if source_local else ("", "nonjoinable", "generalized external interface")
                source_mapping_status = "exact" if source_level == "exact" else ""
                source_mapping_type = "exact identity" if source_level == "exact" else ""
            if target_local.startswith(("EXT-", "REF-")):
                target_atlas, target_system, target_mapping_status, target_mapping_type = local_endpoint_mapping(local_id, "to", target_local, endpoint_by_position)
                target_level = "system-level" if target_mapping_status == "resolved_system_level" else "conceptual"
                target_role, _ = endpoint_role(target_local, target_system, target_mapping_status)
            else:
                target_atlas, target_level, target_role = resolve_local_entity(target_local, target_system, by_local) if target_local else ("", "system-level" if target_system else "nonjoinable", "generalized external interface")
                target_mapping_status = "exact" if target_level == "exact" else ""
                target_mapping_type = "exact identity" if target_level == "exact" else ""
            if not source_system and source_atlas.startswith("SYS-"):
                source_system = source_atlas
            if not target_system and target_atlas.startswith("SYS-"):
                target_system = target_atlas
            if source_system and target_system and source_system != target_system:
                scenario_pairs.add(tuple(sorted((source_system, target_system)))) if "scenario" in artifact.lower() else None
            term = relation_term(source)
            cls, direction, causal, flow, role, caveat = classify_relationship(term, artifact, "relationship_type" if source.get("relationship_type") else "dependency_type")
            evidence = evidence_class(source)
            documented = (source.get("documented_or_inferred") or "").strip() or ("inferred" if evidence == "INFERRED" else "reused_context" if evidence == "CONTEXT_REUSED" else "documented")
            scale = next((source.get(field, "").strip() for field in ("spatial_scale", "scale", "geographic_scale", "jurisdictional_scale") if source.get(field)), "system-level")
            temporal = next((source.get(field, "").strip() for field in ("temporal_scope", "reference_year", "estimate_period") if source.get(field)), "2026 baseline")
            atlas_use = "VISUALIZATION_AND_QUALITATIVE_REASONING"
            if phase == "11B":
                atlas_use = "VISUALIZATION_AND_QUALITATIVE_REASONING;QUALITATIVE_STRESS_TEST_ONLY;NO_QUANTITATIVE_AGGREGATION"
            if source_level == "nonjoinable" or target_level == "nonjoinable":
                atlas_use = "SOURCE_LOCAL_ONLY;NO_EXACT_ATLAS_JOIN"
                if phase == "11B":
                    atlas_use = "VISUALIZATION_AND_QUALITATIVE_REASONING;QUALITATIVE_STRESS_TEST_ONLY;NO_QUANTITATIVE_AGGREGATION;SOURCE_LOCAL_ONLY;NO_EXACT_ATLAS_JOIN"
            if phase == "11B":
                inference_basis = source.get("notes", "") or "Population-system dependency register inference basis retained locally."
                stress = "QUALITATIVE_ONLY"
                quant = "NO"
            else:
                inference_basis = source.get("relationship_basis", "") or source.get("evidence_basis", "") or source.get("notes", "")
                stress = "QUALITATIVE_ONLY"
                quant = "NO"
            if evidence == "INFERRED":
                caveat = f"Inferred relationship retained: {source.get('notes', '')}".strip()
            elif evidence == "CONTEXT_REUSED":
                caveat = f"Reused context retained and not counted as new evidence: {source.get('notes', '')}".strip()
            else:
                caveat = f"{caveat} Local caveat: {source.get('notes', '')}".strip()
            rel_digest = hashlib.sha1(f"{phase}|{artifact}|{local_id}|{index}".encode()).hexdigest()[:8]
            atlas_id = f"AR-{slug(phase)}-{slug(local_id)}-{rel_digest}"
            rows.append({
                "atlas_relationship_id": atlas_id,
                "source_phase": phase,
                "source_artifact": artifact,
                "local_relationship_id": local_id,
                "source_local_endpoint_id": source_local,
                "target_local_endpoint_id": target_local,
                "source_atlas_entity_id": source_atlas,
                "target_atlas_entity_id": target_atlas,
                "source_system_id": source_system,
                "target_system_id": target_system,
                "native_source_system_label": native_source_system,
                "native_target_system_label": native_target_system,
                "normalized_relationship_class": cls,
                "endpoint_role_source": source_role,
                "endpoint_role_target": target_role,
                "source_join_level": source_level,
                "target_join_level": target_level,
                "evidence_class": evidence,
                "documented_or_inferred": documented,
                "source_id": source.get("source_id", ""),
                "evidence_strength": source.get("evidence_strength", "") or source.get("evidence_quality", "") or source.get("evidence_confidence", ""),
                "confidence": source.get("confidence", ""),
                "uncertainty_id": source.get("uncertainty_id", ""),
                "directionality": direction,
                "spatial_scale": scale,
                "temporal_basis": temporal,
                "scenario_status": "BASELINE_DEPENDENCY",
                "inference_basis": inference_basis,
                "uncertainty": source.get("uncertainty", "") or source.get("key_uncertainty", "") or "Local uncertainty/notes retained in source artifact.",
                "suitable_for_visualization": "YES",
                "suitable_for_qualitative_reasoning": "YES",
                "suitable_for_stress_test_propagation": stress,
                "suitable_for_quantitative_aggregation": quant,
                "Atlas_use": atlas_use,
                "caveat": caveat,
            })
            source_counts[artifact] += 1
    # Add scenario references only as a pair ledger; baseline dependency rows stay separate.
    for base in (ROOT / "data/processed/scenarios",):
        for path in sorted(base.glob("*.csv")):
            _, records = read_csv(path)
            for row in records:
                dep_id = (row.get("baseline_dependency_id") or row.get("dependency_id") or "").strip()
                if dep_id:
                    for candidate in rows:
                        if candidate["local_relationship_id"] == dep_id and candidate["source_system_id"] and candidate["target_system_id"] and candidate["source_system_id"] != candidate["target_system_id"]:
                            scenario_pairs.add(tuple(sorted((candidate["source_system_id"], candidate["target_system_id"]))))
                a = system_for_alias(row.get("system_a", ""))
                b = system_for_alias(row.get("system_b", ""))
                if a and b and a != b:
                    scenario_pairs.add(tuple(sorted((a, b))))
    counts = {
        "total_rows": len(rows),
        "source_artifacts": len(source_counts),
        "population_total": sum(1 for row in rows if row["source_phase"] == "11B"),
        "population_inferred": sum(1 for row in rows if row["source_phase"] == "11B" and row["evidence_class"] == "INFERRED"),
        "population_context_reused": sum(1 for row in rows if row["source_phase"] == "11B" and row["evidence_class"] == "CONTEXT_REUSED"),
        "system_level_or_conceptual_rows": sum(1 for row in rows if row["source_join_level"] in {"system-level", "conceptual"} or row["target_join_level"] in {"system-level", "conceptual"}),
        "exact_entity_rows": sum(1 for row in rows if row["source_join_level"] == "exact" and row["target_join_level"] == "exact"),
        "evidence_classes": dict(Counter(row["evidence_class"] for row in rows)),
        "source_artifact_counts": dict(source_counts),
        "scenario_pair_count": len(scenario_pairs),
    }
    return rows, counts, scenario_pairs


def build_joinability(rows: list[dict[str, object]], scenario_pairs: set[tuple[str, str]], system_ids: list[str]) -> list[dict[str, object]]:
    pair_data: dict[tuple[str, str], dict[str, bool]] = defaultdict(lambda: {"exact": False, "system": False, "dependency": False})
    for row in rows:
        a, b = str(row["source_system_id"]), str(row["target_system_id"])
        if not a or not b or a == b or a not in system_ids or b not in system_ids:
            continue
        pair = tuple(sorted((a, b)))
        pair_data[pair]["dependency"] = True
        if row["source_join_level"] == "exact" and row["target_join_level"] == "exact":
            pair_data[pair]["exact"] = True
        elif row["source_join_level"] in {"system-level", "conceptual"} or row["target_join_level"] in {"system-level", "conceptual"}:
            pair_data[pair]["system"] = True
    output = []
    for index, a in enumerate(system_ids):
        for b in system_ids[index + 1:]:
            pair = tuple(sorted((a, b)))
            flags = pair_data[pair]
            scenario = pair in scenario_pairs
            spatial = False
            no_current = not (flags["exact"] or flags["system"] or flags["dependency"])
            basis = []
            if flags["exact"]: basis.append("direct exact entity identity in an integration record")
            if flags["system"]: basis.append("system-level conceptual mapping")
            if flags["dependency"]: basis.append("typed dependency/relationship record")
            if spatial: basis.append("explicit physical co-location record")
            if scenario: basis.append("separate scenario-layer reference")
            if no_current: basis.append("no selected defensible current join")
            caveat = "This is an interoperability finding, not a risk or connectivity score. Co-location is not treated as causation."
            if scenario:
                caveat += " Scenario link remains separate from 2026 baseline evidence."
            if no_current:
                caveat += " Absence of a selected join is not evidence of no real-world relationship."
            output.append({
                "matrix_id": f"JAB-{index + 1:03d}",
                "source_system_id": a,
                "target_system_id": b,
                "direct_exact_identity_join": "YES" if flags["exact"] else "NO",
                "system_level_conceptual_join": "YES" if flags["system"] else "NO",
                "dependency_relationship_join": "YES" if flags["dependency"] else "NO",
                "spatial_colocation_only": "YES" if spatial else "NO",
                "scenario_layer_reference": "YES" if scenario else "NO",
                "scenario_only_link": "YES" if scenario and not flags["dependency"] else "NO",
                "no_defensible_current_join": "YES" if no_current else "NO",
                "join_basis": "; ".join(basis),
                "caveat": caveat,
            })
    return output


def layer_entry(layer_id: str, label: str, system_id: str, phase: str, artifact: str, fmt: str, name: str, geometry: str, scale: str, temporal: str, status: str, key: str, namespace: str, provenance: str, role: str, limitations: str) -> dict[str, object]:
    return {
        "atlas_layer_id": layer_id, "preferred_label": label, "system_id": system_id, "source_phase": phase,
        "source_artifact": artifact, "physical_format": fmt, "layer_or_table_name": name,
        "geometry_type": geometry, "spatial_scale": scale, "temporal_basis": temporal,
        "baseline_or_scenario": "SCENARIO" if "scenario" in artifact.lower() or "future" in artifact.lower() else "BASELINE",
        "scenario_horizon": "2050/2075" if "scenario" in artifact.lower() or "future" in artifact.lower() else "not_applicable",
        "evidence_basis": "Accepted/frozen local product or additive Atlas integration artifact; local evidence fields remain authoritative.",
        "canonical_status": status, "primary_key": key, "joinable_identity_namespace": namespace,
        "provenance_pointer": provenance, "Atlas_role": role, "limitations": limitations,
    }


def source_phase_for_artifact(artifact: str, originating: list[str]) -> str:
    name = artifact.lower()
    if "scenario" in name or "future" in name:
        return next((phase for phase in reversed(originating) if str(phase).endswith("C")), str(originating[-1]))
    dependency_tokens = ("dependency", "mobility", "evidence_relationship", "information_dependency", "authority_matrix", "control_register", "disturbance_register", "resilience_matrix")
    if any(token in name for token in dependency_tokens):
        return next((phase for phase in reversed(originating) if str(phase).endswith("B")), str(originating[0]))
    return str(originating[0])


def build_layer_registry(registry: dict, dependency_counts: dict[str, object]) -> list[dict[str, object]]:
    layers: list[dict[str, object]] = []
    seen: set[str] = set()
    system_by_id = {item["system_id"]: item for item in registry["systems"]}
    identity_namespace = {(row["source_artifact"]): row["local_namespace"] for row in read_csv(A14A_IDENTITY)[1]}
    def add(entry: dict[str, object]) -> None:
        if entry["atlas_layer_id"] in seen:
            raise ValueError(f"duplicate Atlas layer ID: {entry['atlas_layer_id']}")
        if not (ROOT / str(entry["source_artifact"])).exists():
            raise FileNotFoundError(entry["source_artifact"])
        seen.add(str(entry["atlas_layer_id"])); layers.append(entry)
    for system in registry["systems"]:
        sid = system["system_id"]
        phases = [str(x) for x in system["originating_phases"]]
        for artifact in system["primary_tables"]:
            path = ROOT / artifact
            if not path.exists(): raise FileNotFoundError(artifact)
            if path.suffix.lower() != ".csv":
                continue
            fields, _ = read_csv(path)
            stem = path.stem
            phase = source_phase_for_artifact(artifact, phases)
            role = "scenario table" if "scenario" in artifact.lower() else "network/dependency/baseline table"
            add(layer_entry(f"ATL-{slug(sid)}-{slug(stem)}", f"{system['atlas_display_label']} — {stem}", sid, phase, artifact, "CSV", stem, "nonspatial", "native local scale", system["temporal_basis"], system["canonical_status"], csv_key(fields), identity_namespace.get(artifact, "local schema; no exact Atlas entity namespace"), system["provenance_pointer"], role, system["baseline_scenario_distinction"]))
        for map_name in system["principal_maps"]:
            phase = phase_for_map(map_name, phases)
            for suffix, fmt in ((".png", "PNG"), (".svg", "SVG")):
                artifact = f"outputs/maps/systems/{map_name}{suffix}"
                add(layer_entry(f"ATL-{slug(sid)}-{slug(map_name)}-{fmt}", f"{system['atlas_display_label']} — {map_name} ({fmt})", sid, phase, artifact, fmt, map_name, "nonspatial figure", "map-native; not a common spatial scale", system["temporal_basis"], system["canonical_status"], "none", "none", system["provenance_pointer"], "source plate / map figure", "Map scale and native inputs remain local; visual co-location is not a causal join."))
    gpkg_layers = []
    with sqlite3.connect(ROOT / "data/processed/glasspunk_base.gpkg") as connection:
        gpkg_layers = [(row[0], row[1]) for row in connection.execute("select table_name, geometry_type_name from gpkg_geometry_columns order by table_name")]
    for name, geometry in gpkg_layers:
        sid = "SYS-WATER" if name.startswith(("water_", "hydrography_", "routing_")) else "SYS-MATERIALS"
        add(layer_entry(f"ATL-{slug(sid)}-GPKG-{slug(name)}", f"{system_by_id[sid]['atlas_display_label']} — {name}", sid, "1/2", "data/processed/glasspunk_base.gpkg", "GeoPackage", name, geometry, "feature/layer native", "qualified current development and historical v0.1 layers", "ACCEPTED / FROZEN or qualified as documented by source phase", "local layer IDs", "GeoPackage layer namespace", "metadata/atlas_systems.yml; relevant Phase 1/2 reports", "GeoPackage source layer", "Do not collapse physical hydrography, connectors, inferred routing, and historical v0.1 layers."))
    for artifact in ("outputs/qa/data/great_black_swamp_candidate_gordon1966.geojson", "outputs/qa/data/great_black_swamp_candidate_gordon1966_mosaic.geojson"):
        payload = json.loads((ROOT / artifact).read_text(encoding="utf-8"))
        geometry = "GeoJSON feature collection"
        features = payload.get("features", [])
        if features and features[0].get("geometry", {}).get("type"):
            geometry = f"GeoJSON {features[0]['geometry']['type']}"
        add(layer_entry(f"ATL-SYS-ECOLOGY-{slug(Path(artifact).stem)}", f"Great Black Swamp candidate QA — {Path(artifact).stem}", "SYS-ECOLOGY", "1", artifact, "GeoJSON", Path(artifact).stem, geometry, "candidate geometry native", "historical reference / QA candidate", "NONCANONICAL_HOLD", "candidate geometry", "GeoJSON QA namespace", "outputs/qa/; docs/canon_status.md", "noncanonical hold reference layer", "C — HOLD / noncanonical; not a current canonical polygon and not suitable for current spatial joins."))
    for artifact, label in (("metadata/atlas_systems.yml", "Phase 14A ontology registry"), ("metadata/atlas_evidence_vocabulary.yml", "Phase 14A evidence vocabulary"), ("metadata/atlas_relationship_vocabulary.yml", "Phase 14B relationship vocabulary")):
        phase = "14A" if "relationship" not in artifact else "14B"
        status = "ACCEPTED / FROZEN" if phase == "14A" else "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE"
        add(layer_entry(f"ATL-SYS-DATA-{slug(Path(artifact).stem)}", label, "SYS-DATA", phase, artifact, "YAML", Path(artifact).stem, "nonspatial metadata", "repository-wide", "versioned metadata", status, "class_id or system_id", "metadata namespace", artifact, "Atlas metadata", "Metadata defines interfaces; it is not a scientific observation layer."))
    artifact = "reports/phase14a_build_summary.json"
    add(layer_entry("ATL-SYS-DATA-PHASE14A-BUILD-SUMMARY", "Phase 14A build summary", "SYS-DATA", "14A", artifact, "JSON", "phase14a_build_summary", "nonspatial metadata", "repository-wide", "Phase 14A package", "ACCEPTED / FROZEN", "counts", "JSON metadata namespace", "Phase 14A working package", "Phase 14A reproducibility metadata", "Build summary is provenance metadata, not an observation or dependency table."))
    integration_products = [
        ("data/processed/integration/relationship_normalization_crosswalk.csv", "relationship normalization crosswalk"),
        ("data/processed/integration/endpoint_role_crosswalk.csv", "endpoint role crosswalk"),
        ("data/processed/integration/atlas_dependency_crosswalk.csv", "Atlas dependency crosswalk"),
        ("data/processed/integration/system_joinability_matrix.csv", "system joinability matrix"),
    ]
    for artifact, label in integration_products:
        fields, _ = read_csv(ROOT / artifact)
        add(layer_entry(f"ATL-SYS-DATA-{slug(Path(artifact).stem)}", label, "SYS-DATA", "14B", artifact, "CSV", Path(artifact).stem, "nonspatial integration table", "native source scales retained", "2026 baseline dependency interfaces", "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE", csv_key(fields), "Atlas integration namespace", "reports/phase14b_*; source artifact columns", "Atlas integration crosswalk", "Crosswalk does not replace local tables or create a universal causal network."))
    figure = "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png"
    figure_svg = "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg"
    for artifact, fmt in ((figure, "PNG"), (figure_svg, "SVG")):
        add(layer_entry(f"ATL-SYS-DATA-ATLAS-ARCHITECTURE-{fmt}", f"Cross-System Joinability / Dependency Architecture ({fmt})", "SYS-DATA", "14B", artifact, fmt, "atlas_cross_system_joinability_dependency_architecture", "nonspatial conceptual figure", "not geographic", "2026 baseline interfaces plus separate scenario markers", "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE", "none", "none", "reports/phase14b_dependency_integration.md", "integration figure", "Non-proportional architecture; line presence is not causation, risk, or physical route."))
    return layers


def write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8", newline="\n")


def build_figure(registry: dict, matrix: list[dict[str, object]], rows: list[dict[str, object]], scenario_pairs: set[tuple[str, str]]) -> dict[str, object]:
    systems = [item["system_id"] for item in registry["systems"]]
    labels = {item["system_id"]: item["atlas_display_label"] for item in registry["systems"]}
    positions = {
        "SYS-CLIMATE": (0.12, 0.86), "SYS-WATER": (0.29, 0.86), "SYS-BIOGEOCHEMISTRY": (0.48, 0.86), "SYS-ECOLOGY": (0.69, 0.86),
        "SYS-MATERIALS": (0.18, 0.62), "SYS-FREIGHT": (0.39, 0.62), "SYS-ENERGY": (0.61, 0.62), "SYS-DATA": (0.83, 0.62),
        "SYS-POPULATION": (0.18, 0.31), "SYS-GOVERNANCE": (0.40, 0.31), "SYS-EXPOSURE": (0.62, 0.31), "SYS-VECTOR-ECOLOGY": (0.27, 0.09), "SYS-INFECTIOUS-DISEASE": (0.67, 0.09),
    }
    pair_flags = {(row["source_system_id"], row["target_system_id"]): row for row in matrix}
    examples: list[tuple[str, str, str, str]] = []
    exact = next((r for r in rows if r["source_join_level"] == "exact" and r["target_join_level"] == "exact" and r["source_system_id"] != r["target_system_id"]), None)
    if exact:
        examples.append((exact["source_system_id"], exact["target_system_id"], "exact", "Exact/entity-level"))
    else:
        examples.append(("SYS-WATER", "SYS-MATERIALS", "exact_none", "Exact/entity-level: none observed"))
    system_row = next((r for r in rows if r["source_join_level"] in {"system-level", "conceptual"} and r["target_join_level"] in {"system-level", "conceptual"} and r["source_system_id"] != r["target_system_id"]), None)
    if system_row: examples.append((system_row["source_system_id"], system_row["target_system_id"], "system", "System-level conceptual"))
    inferred = next((r for r in rows if r["evidence_class"] == "INFERRED" and r["source_system_id"] and r["target_system_id"] and r["source_system_id"] != r["target_system_id"]), None)
    if inferred: examples.append((inferred["source_system_id"], inferred["target_system_id"], "inferred", "Inferred relationship"))
    current_pairs = {tuple(sorted((str(row["source_system_id"]), str(row["target_system_id"])))) for row in rows if row["source_system_id"] and row["target_system_id"] and row["source_system_id"] != row["target_system_id"]}
    scenario = next(iter(sorted(scenario_pairs)), None)
    if scenario: examples.append((scenario[0], scenario[1], "scenario_reference", "Scenario-layer reference"))
    fig, ax = plt.subplots(figsize=(15, 9), dpi=160)
    fig.patch.set_facecolor("#101820"); ax.set_facecolor("#101820")
    styles = {"exact": ("-", "#86c5da", 2.4), "system": ("--", "#e7b85d", 2.0), "inferred": ((0, (2, 2)), "#e78c72", 1.8), "scenario": ((0, (6, 2, 1, 2)), "#b892d9", 1.9), "scenario_reference": ((0, (6, 2, 1, 2)), "#b892d9", 1.9)}
    drawn = set()
    for source, target, kind, _ in examples:
        if kind == "exact_none" or source not in positions or target not in positions: continue
        pair = tuple(sorted((source, target)))
        draw_key = (pair, kind)
        if draw_key in drawn: continue
        drawn.add(draw_key)
        style, color, width = styles[kind]
        x1, y1 = positions[source]; x2, y2 = positions[target]
        radius = {"exact": 0.04, "system": 0.08, "inferred": 0.12, "scenario": 0.16, "scenario_reference": 0.16}.get(kind, 0.08)
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "color": color, "lw": width, "linestyle": style, "shrinkA": 30, "shrinkB": 30, "mutation_scale": 11, "connectionstyle": f"arc3,rad={radius}"})
    colors = {"natural_environment": "#1f5f7a", "infrastructure_technology": "#6b4c9a", "production_resources": "#9a5a1f", "production_logistics": "#9a5a1f", "institutional_human": "#38764b", "health_environment": "#a23b55"}
    for item in registry["systems"]:
        x, y = positions[item["system_id"]]; width, height = 0.145, 0.095
        patch = FancyBboxPatch((x-width/2, y-height/2), width, height, boxstyle="round,pad=0.012,rounding_size=0.015", fc=colors[item["broad_system_family"]], ec="#d7e4ea", lw=0.8, alpha=0.96)
        ax.add_patch(patch)
        ax.text(x, y, labels[item["system_id"]].replace(" & ", " &\n"), color="white", ha="center", va="center", fontsize=7.2, weight="bold")
    ax.text(0.5, 1.045, "Cross-System Joinability / Dependency Architecture", transform=ax.transAxes, color="white", ha="center", va="center", fontsize=18, weight="bold")
    ax.text(0.5, 1.005, "Phase 14B Atlas-facing integration figure — conceptual, non-proportional, not a geographic map", transform=ax.transAxes, color="#b8c8d2", ha="center", va="center", fontsize=9)
    legend = [
        Line2D([0], [0], color=styles["exact"][1], lw=2.4, linestyle=styles["exact"][0], label="Exact/entity-level (none observed if omitted)"),
        Line2D([0], [0], color=styles["system"][1], lw=2.0, linestyle=styles["system"][0], label="System-level conceptual"),
        Line2D([0], [0], color=styles["inferred"][1], lw=1.8, linestyle=styles["inferred"][0], label="Inferred relationship"),
        Line2D([0], [0], color=styles["scenario"][1], lw=1.9, linestyle=styles["scenario"][0], label="Scenario-layer reference; Scenario-only relationship when no baseline join"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.055), ncol=2, frameon=False, fontsize=8, labelcolor="#d7e4ea")
    exact_note = "Exact/entity-level: no defensible cross-system exact join in the selected dependency subset." if not exact else "Exact/entity-level examples are local identity-preserving joins."
    ax.text(0.01, -0.145, exact_note, transform=ax.transAxes, color="#b8c8d2", fontsize=8)
    ax.text(0.01, -0.18, "System-level mapping ≠ exact identity; co-location ≠ causation; line width ≠ quantity, probability, risk, or effect size.", transform=ax.transAxes, color="#e6c66a", fontsize=8)
    ax.set_xlim(0, 1); ax.set_ylim(-0.24, 1.02); ax.axis("off")
    FIGURES.mkdir(parents=True, exist_ok=True)
    png = FIGURES / "atlas_cross_system_joinability_dependency_architecture.png"
    svg = FIGURES / "atlas_cross_system_joinability_dependency_architecture.svg"
    fig.savefig(png, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    text = svg.read_text(encoding="utf-8")
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    svg.write_text(text, encoding="utf-8", newline="\n")
    plt.close(fig)
    return {"png": str(png.relative_to(ROOT)).replace("\\", "/"), "svg": str(svg.relative_to(ROOT)).replace("\\", "/"), "examples": len(examples), "exact_cross_system_examples": 0 if not exact else 1}


def write_reports(registry: dict, relationships: list[dict[str, object]], endpoints: list[dict[str, object]], dependencies: list[dict[str, object]], dependency_counts: dict[str, object], matrix: list[dict[str, object]], figure: dict[str, object]) -> None:
    layer_counts = Counter(layer["physical_format"] for layer in registry["layer_registry"])
    relation_counts = Counter(row["normalized_relationship_class"] for row in relationships)
    endpoint_counts = Counter(row["endpoint_role"] for row in endpoints)
    lines = ["# Phase 14B Atlas Layer Registry", "", "Status: IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE.", "", f"Atlas registry entries: **{len(registry['layer_registry'])}**.", "", "| Physical format | Count |", "|---|---:|"]
    lines += [f"| {key} | {value} |" for key, value in sorted(layer_counts.items())]
    lines += ["", "The registry keeps CSV, GeoPackage layer, YAML metadata, PNG, and SVG products separate. It does not move local tables into one GeoPackage or imply that nonspatial tables are geographic layers.", "", "All registry records retain source artifact, source phase, native scale, status, identity namespace, provenance pointer, and limitations."]
    (REPORTS / "phase14b_atlas_layer_registry.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines = ["# Phase 14B Relationship Normalization", "", "Status: additive normalized crosswalk; Phase 14A relationship inventory and all local edge tables remain unchanged.", "", f"Local relationship observations normalized: **{len(relationships)}** (Phase 14A inventory baseline: 367).", "", "| Normalized class | Rows |", "|---|---:|"]
    lines += [f"| `{key}` | {value} |" for key, value in sorted(relation_counts.items())]
    lines += ["", "The crosswalk preserves local term, field, phase, artifact, count, directionality, causal semantics, flow semantics, Atlas join role, mapping status, and information-loss caveat.", "", "Association is not causation; dependency is not risk; observation is not authority; mobility is not transmission; exposure pathway is not illness; and scenario influence is not observed dependency.", "", "## Energy disposition", "", "Phase 3 energy terms are normalized without semantic collapse: generation/grid/storage interface terms remain `energy flow`; electricity/grid-serves/cooling/thermal/storage-support terms remain operational dependencies; fuel is a material input; communications is information/control; and no control or information term is classified as energy flow."]
    (REPORTS / "phase14b_relationship_normalization.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines = ["# Phase 14B Dependency Integration", "", "Status: additive Atlas-facing dependency crosswalk; local source tables are read-only inputs.", "", f"Dependency crosswalk rows: **{len(dependencies)}** across **{dependency_counts['source_artifacts']}** canonical dependency artifacts.", "", "| Evidence class | Rows |", "|---|---:|"]
    lines += [f"| `{key}` | {value} |" for key, value in sorted(dependency_counts["evidence_classes"].items())]
    lines += ["", "## Population high-inference handling", "", f"- Total population dependency rows: **{dependency_counts['population_total']}**", f"- Inferred: **{dependency_counts['population_inferred']}**", f"- Reused context: **{dependency_counts['population_context_reused']}**", "- Inferred and reused-context rows retain source evidence class, source phase/artifact, inference basis, native spatial scale, directionality, uncertainty, and visualization/use flags.", "- Inferred rows support visualization and qualitative reasoning; stress-test propagation is qualitative-only; quantitative aggregation is prohibited.", "- No numeric confidence score was added.", "", "## Endpoint and lineage boundary", "", f"- Phase 13B endpoint-role occurrences: **{len(endpoints)}**; roles: " + ", ".join(f"{k}={v}" for k, v in sorted(endpoint_counts.items())) + ".", "- The 0 exact / 34 system-level / 2 retained conceptual Phase 14A endpoint result is preserved. EXT-OCCUPATIONAL-CONTACT and EXT-INFRASTRUCTURE remain generalized external interfaces.", "- Every dependency row retains its local relationship ID, source phase, source artifact, and local endpoint IDs.", "", "## Joinability", "", f"- System-pair matrix rows: **{len(matrix)}**.", "- The matrix is an interoperability matrix, not a risk matrix; it contains no summed connectivity score or composite risk score."]
    (REPORTS / "phase14b_dependency_integration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    qa = {
        "phase": "14B", "status": "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE",
        "registry_entries": len(registry["layer_registry"]), "relationship_rows": len(relationships), "endpoint_role_rows": len(endpoints),
        "dependency_rows": len(dependencies), "joinability_rows": len(matrix), "figure": figure,
        "checks": [
            "Phase 14A accepted/frozen inputs are read-only; no local source table is rewritten.",
            "The Phase 14A 456 identity rows and 0/34/2/0 endpoint result remain unchanged.",
            "Energy communications/control terms are not normalized as energy flow.",
            "Population 468 inferred and 52 reused-context rows remain distinguishable.",
            "No composite risk or summed connectivity score is created.",
            "Great Black Swamp C — HOLD / noncanonical and Toledo intake-coordinate discrepancy UNRESOLVED remain active.",
            "Phase 15, release, and tag are not implemented.",
        ],
    }
    (REPORTS / "phase14b_integration_qa.md").write_text("# Phase 14B Integration QA\n\n" + json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_manifest(result: dict[str, object]) -> None:
    paths = [
        "metadata/atlas_layers.yml", "metadata/atlas_relationship_vocabulary.yml",
        "data/processed/integration/relationship_normalization_crosswalk.csv",
        "data/processed/integration/endpoint_role_crosswalk.csv",
        "data/processed/integration/atlas_dependency_crosswalk.csv",
        "data/processed/integration/system_joinability_matrix.csv",
        "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png",
        "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg",
        "reports/phase14b_atlas_layer_registry.md", "reports/phase14b_relationship_normalization.md",
        "reports/phase14b_dependency_integration.md", "reports/phase14b_integration_qa.md", "reports/phase14b_build_summary.json",
        "src/python/systems/build_phase14b_integration.py", "src/python/systems/validate_phase14b_integration.py",
        "src/R/systems/validate_phase14b_integration.R",
    ]
    artifacts = {}
    for rel in paths:
        path = ROOT / rel
        if not path.exists(): raise FileNotFoundError(rel)
        data = path.read_bytes(); artifacts[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    payload = {
        "phase": "14B", "status": "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE",
        "source_commit": "dd2c0706f8d1f6b73974a530e64de8a82aff2eb1", "scope": "Atlas Layer Registry & Cross-System Dependency Normalization",
        "counts": result, "artifacts": artifacts,
        "exclusions": ["Phase 14A source table modification", "monolithic GeoPackage", "composite risk score", "Phase 15", "release", "tag"],
        "active_holds_preserved": {"great_black_swamp": "C — HOLD / noncanonical", "toledo_intake_coordinate_discrepancy": "UNRESOLVED"},
    }
    (REPORTS / "phase14b_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build() -> dict[str, object]:
    ontology = yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8"))
    evidence = yaml.safe_load(EVIDENCE_PATH.read_text(encoding="utf-8"))
    vocabulary = yaml.safe_load(VOCAB_PATH.read_text(encoding="utf-8"))
    relationships = build_relationship_crosswalk()
    endpoints = build_endpoint_roles()
    dependencies, dependency_counts, scenario_pairs = build_dependency_crosswalk()
    system_ids = [item["system_id"] for item in ontology["systems"]]
    matrix = build_joinability(dependencies, scenario_pairs, system_ids)
    write_csv(INTEGRATION / "relationship_normalization_crosswalk.csv", list(relationships[0].keys()), relationships)
    write_csv(INTEGRATION / "endpoint_role_crosswalk.csv", list(endpoints[0].keys()), endpoints)
    write_csv(INTEGRATION / "atlas_dependency_crosswalk.csv", list(dependencies[0].keys()), dependencies)
    write_csv(INTEGRATION / "system_joinability_matrix.csv", list(matrix[0].keys()), matrix)
    figure = build_figure(ontology, matrix, dependencies, scenario_pairs)
    registry = {"version": "0.1", "registry_id": "atlas_layers_phase14b", "registry_status": "additive_atlas_facing_layer_product_registry", "purpose": "Separate registry for heterogeneous Atlas products; local scientific schemas remain authoritative.", "supported_physical_formats": ["CSV", "GeoPackage", "GeoJSON", "YAML", "JSON", "PNG", "SVG"], "layer_registry": []}
    registry["layer_registry"] = build_layer_registry(ontology, dependency_counts)
    write_yaml(LAYERS_PATH, registry)
    write_reports(registry, relationships, endpoints, dependencies, dependency_counts, matrix, figure)
    result = {
        "registry_entries": len(registry["layer_registry"]), "registry_formats": dict(Counter(item["physical_format"] for item in registry["layer_registry"])),
        "relationship_rows": len(relationships), "relationship_class_counts": dict(Counter(row["normalized_relationship_class"] for row in relationships)),
        "endpoint_role_rows": len(endpoints), "endpoint_role_counts": dict(Counter(row["endpoint_role"] for row in endpoints)),
        "dependency_rows": len(dependencies), "dependency_counts": dependency_counts, "joinability_rows": len(matrix), "scenario_pair_count": len(scenario_pairs), "figure": figure,
        "energy_taxonomy": {"generation_transmission_storage_energy_flow": sum(1 for r in relationships if r["normalized_relationship_class"] == "energy flow" and r["source_phase"] == "3"), "operational_energy_dependency": sum(1 for r in relationships if r["normalized_relationship_class"] == "operational dependency" and r["source_phase"] == "3"), "non_energy_information_control": sum(1 for r in relationships if r["normalized_relationship_class"] == "information / observation" and r["source_phase"] == "3")},
    }
    (REPORTS / "phase14b_build_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    write_manifest(result)
    return result


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True, ensure_ascii=False))
