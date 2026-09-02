# Phase 4C Information Scenario QA

## Scope and separation

- Six states exist: A2050, A2075, B2050, B2075, C2050, and C2075.
- All scenario records are separate from factual Phase 4A/4B records.
- Future records use `reality_status=fictional` and
  `relationship_basis=scenario_assumption`.
- No numeric probabilities or precise future sensor coordinates are used.

## Structural checks

- Assumption ledger: 36 records, six states, six assumptions per state.
- Scenario node states: 72 records, 12 per state.
- Scenario edge deltas: 48 records, eight per state.
- Blind-spot evolution: 36 records, six per state.
- Governance evolution: six authority rows, one per state.
- Scenario comparison: six rows and 12 qualitative dimensions.
- Every future node and edge has an assumption ID and source/basis.

## Governance and AI checks

- Observation, analysis, recommendation, automated operation, and final decision
  authority remain distinct in the scenario descriptions.
- AI is limited to explicitly fictional assisted analysis, recommendation,
  anomaly detection, and bounded operations.
- Human authority is retained in every scenario family.
- Security remains high-level: provenance, authentication, availability,
  continuity, access, redundancy, trust, and concentration.
- No attack path, exploit, credential, SCADA, sensitive topology, target list,
  offensive scenario, or vulnerability scan is present.
- No future object is added to the factual baseline.

## Baseline immutability

The scenario validator checks the Phase 4A manifest and the Phase 4B acceptance
freeze manifest. It verifies Map 14, Map 15, the Phase 4A/4B tables, the
Phase 4B matrix, and principal frozen reports before accepting the scenario
package.

## Known limitations

The scenario package does not resolve the Toledo intake-coordinate discrepancy,
Great Black Swamp geometry hold, current station cadence, organizational
handoff evidence, or public operational-data gaps. Those remain baseline
uncertainties carried into future interpretations.

## Artifact validation

`src/python/systems/validate_information_scenarios.py` validates assumptions,
scenario node/edge separation, blind-spot and authority evolution, comparison
values, Map 16/16b, and frozen Phase 4A/4B hashes.
`src/R/systems/validate_information_scenarios.R` independently checks schemas,
state counts, provenance presence, baseline IDs, matrix values, and image/SVG
artifacts.
