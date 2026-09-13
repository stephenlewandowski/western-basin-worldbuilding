# Phase 16A — Propagation Framework

## Rule semantics

Each rule names the source system, source state/effect, retained Phase 14 relationship class, target system, propagation mechanism, application evidence class, underlying lineage evidence class, enabling and limiting conditions, temporal/spatial character, reversibility, optional Phase 15 technology modifier, governance boundary, response option, second-order effect, uncertainty, and source lineage. `application_fit` records whether the cited relationship is an exact application, a qualified inference, or a scenario-state application.

Rules use explicit stage numbers and parent references. Stage 1 source systems equal the stressor initial system and use `parallel_initial_branch`; later stages require a preceding rule for the same stressor whose target is the later source and use `sequential`. The package does not calculate transitive closure; cycles are not treated as runaway feedback.

## Relationship classes retained

The framework keeps `physical flow`, `material flow`, `operational dependency`, `information / observation`, `governance / authority`, `ecological relationship`, `exposure pathway`, `surveillance / detection`, `population / mobility interface`, `scenario influence`, `high-level association`, and `unresolved / unclassified` distinct. It does not use generic causation as a replacement class.

## Evidence and lineage

Propagation relationships retain Phase 14 Atlas dependency-crosswalk IDs or an explicitly labeled Phase 14 system-level conceptual architecture pointer. Scenario-conditioned technology interactions retain Phase 15B state IDs and are never represented as baseline facts. A rule application cannot be stronger than its sole relationship lineage; direct/documented and inferred edges remain machine-readable and visually distinct.

## Reusable chain template

`chain_id, stage, stressor_id, chain_parent_rule_id, initial_system, initial_effect, relationship_id, target_system, propagation_mechanism, evidence_class, lineage_evidence_class, application_fit, technology_modifier, governance_modifier, response_option, second_order_effect, uncertainty, source_lineage`

Multiple stages are allowed. A repeated system is not a feedback loop unless the feedback inventory independently supports that interpretation.

## Qualitative system-state vocabulary

Nominal, stressed, constrained, degraded, redistributed, more dependent, less observable, more observable, more coupled, less interoperable, delayed, fragmented, adaptive, recovering, and indeterminate are descriptors only. They are not ordinal scores and “stressed” does not mean imminent failure.

## Matrix interpretation

The 312-cell system × stressor matrix answers only whether a defensible pathway is selected: {'DIRECT': 47, 'INDIRECT': 4, 'NO CURRENT DEFENSIBLE PATH': 253, 'NOT ASSESSED': 3, 'SCENARIO-CONDITIONED': 5}. Scenario-conditioned stressor/pathway status is evaluated before initial-system matching, so scenario-only initial systems are not baseline DIRECT cells. It is not a severity, risk, resilience, vulnerability, or ranking matrix. Rows and columns must not be summed.
