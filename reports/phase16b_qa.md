# Phase 16B QA — Compound Cross-System Stress Tests

## Required deterministic checks

- Exactly four principal tests are implemented; candidates 005 and 006 remain `RESERVE / UNIMPLEMENTED` with no generated stages or regime results.
- Each stressor resolves to the frozen Phase 16A stressor catalog and has a valid initial system.
- The builder loads the authoritative Atlas system vocabulary from `metadata/atlas_systems.yml`; duplicate, empty, unavailable, or noncanonical system IDs fail with record and field context.
- Each stage resolves to an existing Phase 16A rule, relationship, response, and optional technology modifier; no Phase 16B rule is created.
- Stage-1 initial systems match the stressor initial system and use parallel fan-out. Later stages match the exact preceding target and same-stressor Phase 16A parent.
- Relationship source/target direction, relationship class, mechanism, lineage, application evidence, and scenario status are copied without reversal or strengthening.
- Scenario-conditioned stages retain their Phase 15B state references and are never represented as baseline direct paths.
- Every branch terminates explicitly. A missing continuation is recorded as `TERMINATED — NO DEFENSIBLE CURRENT PATH` rather than being forced.
- System-state descriptors and response/adaptation states resolve to their selected Phase 16A stage/rule/response source.
- Regime rows resolve to Phase 16A technology modifiers and frozen Phase 15B scenario state records; regime effects cannot create a new propagation pathway.
- Evidence inheritance, source lineage, uncertainty, response capacity boundaries, and active scenario conditions remain machine-readable.
- No score, probability, forecast, economic-loss forecast, health-outcome forecast, dose, illness, or unsupported causal field is present.
- Infectious-disease and biosecurity content remains high-level only; no pathogen engineering; no operational attack detail; no transmission optimization; no evasion method; and no laboratory procedure is represented.
- Narrative hooks are explicitly `NONCANONICAL / FUTURE ATLAS HOOK` and contain no characters or story canon.
- Phase 16A, Phase 15A/15B, Phase 14A/14B, and all prior freeze-manifest artifacts remain unchanged.

## Figure QA intent

- `phase16b_compound_stress_propagation.png/.svg` is qualitative, non-geographic, non-proportional, and shows the four tests, fan-out, selected stage links, response/adaptation, and defensible branch termination.
- `phase16b_technology_regime_effects.png/.svg` shows A/B/C qualitative modifier effects without ranking, scoring, or new propagation edges.
- SVG text remains inspectable; PNG dimensions and signatures are machine-checked.

## Deterministic technology-regime geometry QA

- Header row: top=2.55, height=1.15, bottom=3.70; first data row top=4.20; minimum gap=0.40; `data_top > header_bottom + minimum_gap` is asserted.
- Grid: dedicated column 0 plus A/B/C columns; row height=2.75; row gap=0.45; all 0 card-rectangle overlaps detected.
- Containment: 32 wrapped card text blocks passed rendered bounding-box checks; all four stress-test labels remain inside column 0; B text enters C=False; C text outside its figure/card=False.

## Validation commands

- `python src/python/systems/build_phase16b_stress_tests.py`
- `python src/python/systems/validate_phase16b_stress_tests.py`
- `Rscript src/R/systems/validate_phase16b_stress_tests.R`
- Independent review is not part of this checkpoint; use `--require-review` only after a valid final passed review record exists at `reports/phase16b_independent_review.md`.
- `npm run test`
- `npm run build`
- `git diff --check`
