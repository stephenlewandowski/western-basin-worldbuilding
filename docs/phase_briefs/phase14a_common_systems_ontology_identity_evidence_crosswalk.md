# Phase 14A — Common Systems Ontology, Identity & Evidence Crosswalk

Status: APPROVED EXECUTION SCOPE; additive integration layer only.

## Objectives

1. Inventory the systems actually represented across accepted Phases 1–13.
2. Assign stable Atlas system identifiers without modifying local phase IDs.
3. Crosswalk local entity identifiers to deterministic Atlas entity identities.
4. Audit Phase 13B `EXT-*` / `REF-*` conceptual endpoints without inventing nodes.
5. Normalize evidence/status vocabulary while preserving fact, inference, scenario, observation, and derived distinctions.
6. Inventory local relation/edge terminology without performing Phase 14B normalization.
7. Define namespace, alias, external-interface, unresolved-identity, provenance, and deterministic-generation rules.
8. Provide an Atlas-facing conceptual architecture figure, not a geographic evidence map.

## Required outputs

- `metadata/atlas_systems.yml`
- `metadata/atlas_evidence_vocabulary.yml`
- `data/processed/integration/system_identity_crosswalk.csv`
- `data/processed/integration/external_endpoint_crosswalk.csv`
- `data/processed/integration/relationship_taxonomy_inventory.csv`
- Phase 14A reports and artifact check
- `outputs/figures/western_basin_systems_architecture.svg`
- `outputs/figures/western_basin_systems_architecture.png`
- `src/python/systems/build_phase14a_integration.py`
- `src/python/systems/validate_phase14a_integration.py`
- `src/R/systems/validate_phase14a_integration.R`

## Interpretation rules

The ontology is an interoperability registry, not a universal table. System-level mappings are explicitly interpretive. Exact identity is reserved for a local record whose source artifact and identifier are directly present. `EXT-*` and `REF-*` identifiers remain visible in the endpoint crosswalk even when they are mapped to a system-level concept. Unresolved and intentionally distinct records are never silently promoted.

The relationship inventory is descriptive and provisional. It records local terms, likely synonyms, incompatible semantics, and ambiguities for later Phase 14B work; it does not rewrite local relation values.

## Validation gates

Python and R independently check registry schemas, stable ID uniqueness, source-artifact and local-ID resolution, endpoint totals, vocabulary coverage, fact/inference/scenario separation, retained holds, frozen-artifact integrity with text newline portability, absence of Phase 14B/15 products, and architecture figure integrity.
