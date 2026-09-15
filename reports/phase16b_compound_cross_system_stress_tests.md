# Phase 16B — Compound Cross-System Stress Tests

## Status

Phase 16B is **IMPLEMENTED / DETERMINISTICALLY VALIDATED / AWAITING INDEPENDENT REVIEW** in the additive working package; it is not integrated and has not been accepted. Phase 16A remains **ACCEPTED / FROZEN** and is the only propagation-rule framework used here. Phase 17 remains **NOT IMPLEMENTED**.

FACT: Four principal tests are implemented as qualitative applications of selected frozen Phase 16A rules. Two additional Phase 16A candidates remain reserve / unimplemented.

INFERENCE: A compound test places bounded stressors in one analytical context. It does not create a new cross-stressor edge, a probability, or a guaranteed joint event.

SCENARIO: A/B/C regime rows reuse frozen Phase 15B state references as optional technology-regime modifiers. They are not rankings, forecasts, deployments, or new propagation paths.

## Package counts

- Principal tests: **4**
- Reserve tests: **2**
- Propagation stage rows: **13**
- Branches / termination rows: **14**
- System-state observations: **26** (two positions per propagation stage)
- Response/adaptation states: **13**
- A/B/C × horizon regime-effect rows: **24**
- Uncertainty rows: **4**
- Cross-test comparison rows: **4**
- Noncanonical Atlas hooks: **4**

Counts are structural inventory counts, not scores or measures of severity, risk, resilience, vulnerability, probability, or outcome.

## Principal and reserve tests

| Test | Class | Status | Stressors | Phase 16A rule inputs |
|---|---|---|---|---|
| `P16B-CAND-001` | PRINCIPAL | IMPLEMENTED / QUALITATIVE | EXTREME HEAT + LOW FLOW + GRID STRESS | `RULE-16A-001;RULE-16A-005;RULE-16A-006;RULE-16A-016` |
| `P16B-CAND-002` | PRINCIPAL | IMPLEMENTED / QUALITATIVE | HARMFUL ALGAL BLOOM / WATER-QUALITY PRESSURE + WATER-TREATMENT DISRUPTION | `RULE-16A-012;RULE-16A-014;RULE-16A-015` |
| `P16B-CAND-003` | PRINCIPAL | IMPLEMENTED / QUALITATIVE | FREIGHT / MATERIAL DISRUPTION + INDUSTRIAL ENERGY CONSTRAINT | `RULE-16A-019;RULE-16A-020` |
| `P16B-CAND-004` | PRINCIPAL | IMPLEMENTED / QUALITATIVE | INFECTIOUS-DISEASE PRESSURE + SURVEILLANCE / DATA-GOVERNANCE FRICTION | `RULE-16A-022;RULE-16A-023;RULE-16A-026;RULE-16A-033` |
| `P16B-CAND-005` | RESERVE | RESERVE / UNIMPLEMENTED | HEAVY PRECIPITATION / FLOODING + INFRASTRUCTURE / LOGISTICS DISRUPTION | `RULE-16A-009;RULE-16A-010;RULE-16A-036;RULE-16A-037` |
| `P16B-CAND-006` | RESERVE | RESERVE / UNIMPLEMENTED | CYBER / DIGITAL-RESILIENCE STRESS + SENSOR / DECISION-SUPPORT DEGRADATION | `RULE-16A-017;RULE-16A-018;RULE-16A-027;RULE-16A-028;RULE-16A-029` |

The reserve rows remain in `phase16b_stress_test_definitions.csv` only as reserve / unimplemented inventory. No stage or regime result is generated for them.

## Propagation chains and fan-out

Every stage row carries its exact Phase 16A stressor, rule, relationship, evidence class, response, source lineage, and optional technology modifier IDs. Stage 1 rows are parallel initial branches. Later stages require the exact preceding target and same-stressor parent relationship. The only selected stage-2 continuation is the low-flow branch in principal test 001.

| Test | Stage rows | Branches | Scenario-conditioned stages | Termination result |
|---|---:|---:|---:|---|
| `P16B-CAND-001` | 4 | 3 | 1 | 3 × TERMINATED — NO DEFENSIBLE CURRENT PATH |
| `P16B-CAND-002` | 3 | 3 | 0 | 3 × TERMINATED — NO DEFENSIBLE CURRENT PATH |
| `P16B-CAND-003` | 2 | 4 | 0 | 4 × TERMINATED — NO DEFENSIBLE CURRENT PATH |
| `P16B-CAND-004` | 4 | 4 | 1 | 4 × TERMINATED — NO DEFENSIBLE CURRENT PATH |

Fan-out is not sequential propagation. Compound stressors are retained as co-occurring test inputs; no unsupported rule is invented to join branches. `TERMINATED — NO DEFENSIBLE CURRENT PATH` is a valid result when the frozen Phase 16A vocabulary does not support a continuation.

## System states and responses

System-state rows copy the source and target descriptors from each selected Phase 16A rule. Response/adaptation rows copy the referenced Phase 16A response mechanism, enabling condition, limiting condition, evidence class, and capacity boundary. An option is not a successful response.

## Technology-regime comparison

The A/B/C regime effects are qualitative and non-ranked:

- **A — Coordinated Technological Adaptation:** selected interfaces may gain observability and coordination or selected buffering/substitution options, while energy, compute, data, maintenance, and human-authority dependencies remain visible.
- **B — Uneven Networked Modernization:** observability, substitution, duplication, and workforce requirements may be redistributed across strong and weak interfaces; coupling and negotiation friction remain uneven.
- **C — High Capability / High Friction Basin:** capability and observability may increase at selected nodes while coupling, governance/trust friction, cyber/digital exposure, and brittle maintenance dependencies remain visible without implying collapse.

No regime creates a propagation pathway unsupported by Phase 16A. The regime table retains the exact Phase 16A technology modifier IDs and frozen Phase 15B state references.

## Uncertainty and scientific boundaries

The package does not create risk, resilience, vulnerability, severity, or connectivity scores; probabilities; economic-loss forecasts; health-outcome forecasts; or epidemiological predictions. Boundary shorthand: propagation ≠ probability; dependency ≠ guaranteed failure; response option ≠ successful response; AI recommendation ≠ authority. Co-location is not causation. Contamination, exposure, dose, and illness remain distinct. Surveillance signal is not incidence.

Biosecurity remains high-level only: governance, surveillance, diagnostics, data stewardship, public-health coordination, workforce continuity, and resilience interfaces. No pathogen engineering; no operational attack; no transmission optimization; no evasion; no laboratory procedure; and no harmful-biology detail is represented.

## Noncanonical / future Atlas bridge

Each principal test has one explicitly labeled `NONCANONICAL / FUTURE ATLAS HOOK` row. These rows provide a generalized system/place setting, operational decision point, human/institutional role, observable sign of strain, response moment, and scientific lineage only. They create no characters, fiction, future story canon, geography, or baseline fact.

## Protected project state

Phase 16A is **ACCEPTED / FROZEN**. Phase 15 is **COMPLETE / ACCEPTED / FROZEN**. Phase 14 is **COMPLETE / ACCEPTED / FROZEN**. Great Black Swamp remains **C — HOLD / noncanonical**. The Toledo intake-coordinate discrepancy remains **UNRESOLVED**. Deferred Phase 6B manifest-status wording, Phase 3A missing manifest status, and Phase 2A superseded legacy-worktree maintenance remain deferred.

No release or tag was created.
