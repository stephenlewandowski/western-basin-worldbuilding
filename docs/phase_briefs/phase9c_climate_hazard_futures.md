# Phase 9C — Climate & Hazard Futures, 2050 / 2075

Status: ACCEPTED / FROZEN; the corrected Phase 9C package is protected by `reports/phase9c_climate_hazard_futures_freeze_manifest.json`.

Primary products: Map 31 — Climate & Hazard Futures, 2050; Map 31b — Climate & Hazard Futures, 2075.

## Purpose

Create three non-probabilistic scenario families that diverge from immutable Phase 9A/9B working baselines while preserving physical uncertainty and adaptation differences:

- A — Adaptive / Buffered Basin: hazards intensify or shift, while adaptation, ecological buffers, infrastructure, monitoring, and governance substantially improve resilience. Hazards do not disappear.
- B — Managed Variable Basin: variability increases and adaptation is uneven, with targeted investment and persistent management burden. This is a distinct working-system future, not a midpoint.
- C — Compound Hazard Basin: physical hazards interact more severely with existing hydrologic, ecological, infrastructure, energy, freight, and nutrient systems while adaptation lags. Do not assert inevitable catastrophe or collapse.

## Scenario data products

Keep all future objects separate from factual 2026 tables and include explicit provenance:

- scenario assumption ledger
- scenario hazard states
- scenario dependency states
- scenario resilience/control states
- compound-event scenario states
- qualitative scenario comparison matrix
- projection/source report
- assumptions, consistency, QA, and worldbuilding-implications reports
- Map 31 and Map 31b PNG/SVG

Future objects should carry scenario_id, scenario_year, baseline_object_id where applicable, change_type, reality_status, relationship_basis, assumption_id, plausibility, source_or_basis, and notes.

## Projection evidence

Prefer National Climate Assessment, NOAA/NCEI, USGS, EPA, GLISA/regional climate resources, peer-reviewed Great Lakes work, and transparent CMIP6/downscaled products. Record model/ensemble, emissions or scenario framing, baseline/reference period, horizon, spatial resolution, method, and uncertainty. The repository CMIP7 reference is methodological context only; do not force CMIP7 into a regional claim if a mature product is not available.

Use supported ranges or directional findings for temperature, extreme heat, precipitation/heavy precipitation, and seasonal shifts. Keep tornado counts, exact future flood damage, exact Lake Erie shoreline position, outage probability, mortality, disease burden, and economic loss out of scope unless directly supported by an appropriate source; normally these remain qualitative.

## Required validation

- Independent Python and R scenario validators.
- Explicit separation and hash protection of Phase 9A/9B and prior accepted artifacts.
- Projection-record provenance and scenario-ledger consistency checks.
- Map 31/31b PNG/SVG and text/readability checks.
- Prior-system regressions, Markdown validation, application tests/build, Git/LFS checks, security scan, complete diff review, and independent scientific/code review.

Scientific findings must remain distinct from speculative worldbuilding implications. No health outcomes, social-vulnerability/EJ ranking, emergency-management expansion, unsupported probabilities, or unrelated hazard module is permitted.

## Completion gate

After clean validation, independent review, commit, push, fast-forward integration, synchronization readback, and Sol acceptance, record Phase 9A, 9B, and 9C as **ACCEPTED / FROZEN**; set Active phase to **NONE** and Next analytical phase to **NOT APPROVED**. Do not start another major scientific module.
