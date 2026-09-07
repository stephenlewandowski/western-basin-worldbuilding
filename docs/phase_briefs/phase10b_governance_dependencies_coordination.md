# Phase 10B — Cross-System Authority, Dependencies & Coordination, 2026

Status: ACCEPTED / FROZEN by Sol explicit acceptance decision on 2026-09-04.

Primary product: Map 33 — Cross-System Governance Dependencies & Coordination, 2026 (or the next sequential map number confirmed from repository state).

## Purpose

Show where physical and environmental system dependencies cross institutional boundaries. Build over the Phase 10A working baseline and reuse accepted physical, ecological, infrastructure, health, nutrient, and hazard systems. The layer is qualitative; it does not rank institutions or calculate a composite governance score.

## Transition and immutability

Begin only after Phase 10A has passed its targeted Python/R/provenance/schema/map checks. Protect or hash the 10A working baseline before adding 10B. Do not alter accepted/frozen Phase 1–9 artifacts. Formal Sol acceptance of 10A is not assumed by implementation status.

## Products

- `data/processed/analysis/governance_dependency_register.csv`
- `data/processed/analysis/governance_coordination_mechanisms.csv`
- `data/processed/analysis/governance_dependency_matrix.csv`
- `data/processed/networks/governance_dependency_edges.csv`
- Map 33 PNG/SVG, using the actual next sequential map number confirmed by the builder
- `reports/governance_dependency_sources.md`
- `reports/governance_dependency_assumptions.md`
- `reports/governance_dependency_findings.md`
- `reports/governance_dependency_qa.md`
- machine-readable artifact check, manifest, reproducible builder, Python validator, and independent R validator

## Dependency register

Use fields including dependency_id, system_a, system_b, actor_a, actor_b, role_a, role_b, dependency_type, coordination_mechanism, mandatory_or_voluntary, documented_or_inferred, jurisdictional_scale, evidence_strength, source_id, and notes. Supported dependency types include overlapping authority, sequential authority, split responsibility, information dependency, funding dependency, permit dependency, public/private dependency, interstate dependency, binational dependency, monitoring-without-control, control-without-direct-observation, voluntary coordination, mandatory coordination, emergency coordination, and advisory relationship.

## Coordination mechanisms

Where supported, distinguish statute/regulation, permit, compact, treaty/agreement, memorandum/agreement, funding program, market/operator rule, planning process, emergency protocol, scientific/data-sharing network, and voluntary program. Do not imply that every coordination relationship is legally binding.

## Qualitative matrix

Use separate dimensions: authority_clarity, jurisdiction_overlap, coordination_requirement, monitoring_alignment, enforcement_basis, funding_dependency, public_private_dependency, cross_border_dependency, data_dependency, decision_sequence, and uncertainty. Allowed values are strong, moderate, limited, unknown, and not_applicable. Do not calculate a composite score or rank governance quality. UNKNOWN is not failure; overlap is not dysfunction; distributed authority is not absence of authority.

## Gap discipline and evidence status

Use distinct labels for documented absence of authority, distributed authority, unclear responsibility, coordination burden, lack of project evidence, monitoring limitation, and voluntary rather than mandatory authority. Use “gap” only when evidence supports a documented absence of authority. Distinguish FACT, INFERENCE, and SCENARIO and preserve row-level provenance.

## Boundary examples to test, not assume

Evaluate evidence-supported chains such as agricultural nutrient source to watershed transport to water-quality regulation to municipal treatment to ecological consequence; severe weather warning to utility/grid response to municipal service and water/wastewater consequence; wetland function to permitting to restoration funding to local land-use interaction; and port/freight private operation to public infrastructure to federal/state regulation and environmental permitting. Each chain must be supported or labeled inferred, and no example is factual merely because it is plausible.

## Map rules

Map only defensible geographic meaning: authoritative jurisdictional areas where supported, generalized institutional nodes, system interfaces, jurisdictional connectors, and cross-system decision chains. Do not map organization headquarters as jurisdiction and do not create precise polygons from vague program descriptions.

## Validation and transition gate

Validate 10A working-baseline hashes, schemas, controlled vocabularies, source references, documented/inferred separation, mandatory/voluntary distinctions, gap discipline, matrix labels, negative scope, map artifact/readability, Python/R independence, prior Phase 1–9 freeze manifests, Markdown links, Git/LFS, and complete diff review. Do not begin Phase 10C, Phase 11, population, infectious disease, vector ecology, biosecurity, emergency-management operations, or AI/AGI convergence in this session. Phase 10B is accepted/frozen and protected by its final freeze manifest.

## Acceptance / freeze record

Sol formally accepted and froze Phase 10B on 2026-09-04. Final freeze manifest: `reports/phase10b_governance_dependencies_coordination_freeze_manifest.json`; it references the frozen Phase 10A manifest. The accepted distinctions remain unchanged: overlap ≠ dysfunction, unknown ≠ failure, and distributed authority is not absence of authority. GLIFWC remains an `intertribal_body`; distinct sovereign nations remain distinct actors; no present-day Western Basin tribal territory or permit/enforcement jurisdiction is inferred. Great Black Swamp remains C — HOLD / noncanonical and the Toledo intake-coordinate discrepancy remains UNRESOLVED. Phase 10C is accepted / frozen as a separate qualitative scenario layer under `reports/phase10c_governance_futures_freeze_manifest.json`.
