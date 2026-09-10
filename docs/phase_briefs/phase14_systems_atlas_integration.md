# Phase 14 — Systems Atlas Integration, Ontology, and Evidence Crosswalk

Status: MODIFIED PHASE APPROVED FOR EXECUTION; Phase 14A only in this work package.

## Purpose

Create the additive interoperability layer needed to treat the accepted Phases 1–13 as one Western Basin systems model without homogenizing unlike scientific datasets or rewriting accepted/frozen outputs.

## Scope

Phase 14A creates:

- a common Atlas-facing systems ontology;
- stable Atlas namespace rules;
- additive local-identifier and conceptual-endpoint crosswalks;
- a normalized evidence/status vocabulary with explicit information-loss notes;
- an inventory and provisional high-level taxonomy of local relationships;
- one system-level architecture figure;
- deterministic Python and independent R validation;
- a durable QA report and review record.

Phase 14A references CSV, GeoPackage, GeoJSON, YAML/JSON metadata, scenario tables, and network tables without consolidating them into a monolithic GeoPackage.

## Exclusions

- Do not modify accepted/frozen Phase 1–13 artifacts.
- Do not modify `metadata/systems.yml`; it remains the historically scoped original water/materials registry.
- Do not normalize all relationship edges; detailed cross-system dependency normalization is Phase 14B.
- Do not implement a new environmental or health domain.
- Do not implement Phase 14B or Phase 15.
- Do not create a composite score, quantitative coupled model, risk model, or forecast.
- Do not create a release or tag.

## Protected boundaries

Fact, observation, derived value, inference, scenario assumption, scenario state, context, unresolved status, and noncanonical hold remain distinct. Dependency is not risk; association is not causation; contamination is not exposure; exposure is not dose; dose is not illness; and surveillance is not incidence.

Great Black Swamp remains `C — HOLD / noncanonical`. The Toledo intake-coordinate discrepancy remains `UNRESOLVED`. Phase 6B manifest wording, Phase 3A manifest-status maintenance, and the Phase 2A legacy worktree remain deferred.

## Products

The Phase 14A brief, the Phase 14B approved-scope brief, additive metadata registries, integration crosswalk CSVs, reports, architecture figure, reproducible builder, Python validator, independent R validator, artifact check, and independent review record.

## Delivery status target

Phase 14A: IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE.

Phase 14B: APPROVED SCOPE / NOT IMPLEMENTED.

Phase 15: NOT IMPLEMENTED.
