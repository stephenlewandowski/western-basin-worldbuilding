# Phase 16B Provenance and Lineage

## Result model

Every propagation stage is a derived application of an accepted Phase 16A rule. The package does not introduce a new propagation relationship or mechanism. The source rule supplies the stressor, relationship, endpoints, mechanism, application evidence, lineage evidence, scenario condition, response, uncertainty, and optional Phase 15 technology modifier.

## Frozen lineage layers

- Phase 16A stressor, relationship, rule, response, and technology-modifier catalogs are read-only inputs.
- Phase 14 relationship direction and evidence lineage remain inherited through the Phase 16A relationship and rule records.
- Phase 15A/15B technology lineage is inherited through the Phase 16A technology-modifier catalog and the Phase 15B state anchors in the regime table.
- Scenario-conditioned Phase 16A rules retain their `SCENARIO_STATE` evidence and Phase 15B state IDs; they do not become baseline direct paths.
- Response rows retain the Phase 16A response catalog source lineage and capacity boundary; response option does not imply successful response.

## Evidence classification

`OBSERVED_DOCUMENTED`, `INFERRED`, and `SCENARIO_STATE` remain distinct in the stage table. A derived stage cannot be stronger than the selected Phase 16A rule or its underlying relationship. Current-path absence is represented by an explicit termination row, not by a fabricated inferred edge.

## A/B/C regime layer

Regime rows cite `TM-16A-009`, `TM-16A-010`, or `TM-16A-011`, then resolve the modifier's Phase 15B lineage and representative 2050/2075 state anchors. The table is an optional scenario modifier layer; it does not change chain topology. The three regimes are compared without ranking.

## Uncertainty and negative scope

The package leaves event coincidence, duration, local operating conditions, access, capacity, governance, diagnostic timeliness, exposure, dose, illness, incidence, transmission, and economic consequences unresolved where Phase 16A does not support them. No numeric risk, resilience, vulnerability, severity, probability, forecast, economic-loss, or health-outcome field is created.

Biosecurity is high-level only: surveillance, diagnostics, data stewardship, public-health governance, communication, workforce continuity, and resilience. No pathogen engineering; no operational attack; no transmission optimization; no evasion; and no laboratory procedure is modeled.

## Holds

Great Black Swamp remains `C — HOLD / noncanonical`; the Toledo intake-coordinate discrepancy remains `UNRESOLVED`; deferred Phase 6B/3A/2A maintenance is unchanged.

## Branch termination audit

The builder checked every Phase 16B branch against the complete frozen Phase 16A rule catalog. For staged branches, the check required no unused sequential rule with the same stressor, the final selected rule as parent, the final target as source, and the next stage number. For stressors with no selected stage, the check required no Phase 16A rule for that stressor. Rule, relationship, endpoint, and response lookups were resolved before this termination disposition; every staged final row has a response/adaptation state. No termination is caused by lookup failure, endpoint reversal, unresolved rule lineage, or suppressed parallel fan-out.

| Branch | Final selected stage | Final target | Valid unused continuation | Final response state | Audit |
|---|---|---|---|---|---|
| `P16B-001-HEAT` | stage 1 / RULE-16A-001 | `SYS-ENERGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-001-LOW-FLOW` | stage 2 / RULE-16A-006 | `SYS-ENERGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-001-GRID` | stage 1 / RULE-16A-016 | `SYS-DATA` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-002-HAB` | stage 1 / RULE-16A-012 | `SYS-ECOLOGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-002-TREATMENT-ENERGY` | stage 1 / RULE-16A-014 | `SYS-ENERGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-002-TREATMENT-DISEASE` | stage 1 / RULE-16A-015 | `SYS-INFECTIOUS-DISEASE` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-003-TRANSPORT` | stage 1 / RULE-16A-019 | `SYS-ENERGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-003-CRITICAL-MATERIAL` | no selected stage | `—` | NONE — no Phase 16A rule exists for the stressor | NOT APPLICABLE | PASS |
| `P16B-003-FUEL` | stage 1 / RULE-16A-020 | `SYS-ENERGY` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-003-FEEDSTOCK` | no selected stage | `—` | NONE — no Phase 16A rule exists for the stressor | NOT APPLICABLE | PASS |
| `P16B-004-INFECTIOUS-DATA` | stage 1 / RULE-16A-022 | `SYS-DATA` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-004-INFECTIOUS-GOVERNANCE` | stage 1 / RULE-16A-023 | `SYS-GOVERNANCE` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-004-SURVEILLANCE` | stage 1 / RULE-16A-026 | `SYS-GOVERNANCE` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
| `P16B-004-PRIVACY` | stage 1 / RULE-16A-033 | `SYS-GOVERNANCE` | NONE — no valid same-stressor sequential Phase 16A rule begins at the final target | PRESENT | PASS |
