# Biogeochemical Module QA

## Structural

- Phase 8A: 18 nodes, 24 directed flux edges, ten quantitative/context records, and 15-source registry.
- Phase 8B: 22 dependency edges, 10 controls, and eight matrix rows.
- Phase 8C: 36 assumptions, 48 scenario nodes, 42 scenario edges, 48 control states, 48 uncertainty states, and six comparison rows.
- Maps 26, 27, 28, and 28b include PNG and SVG artifacts.

## Scientific boundaries

The validators check node/edge references, unique identifiers, scenario separation, qualitative dependency vocabulary, manifest hashes, map readability/artifact integrity, and absence of unsupported future concentration/load/HAB-magnitude claims. The package does not create a predictive HAB model, basin-wide station extrapolation, farm-level attribution, uniform wetland removal efficiency, carbon budget, exposure/dose model, or future probability.

## Immutability

The Phase 8 feature diff adds new biogeochemical artifacts and does not modify Phase 7 exposure tables or Maps 25/25b. Accepted historical baselines remain outside the module's write scope.

## Remaining gaps

Regional station coverage, compatible seasonal load series, diffuse-source apportionment, tile-drainage representation, wetland condition/performance, sediment budgets, and wastewater actual-load records remain incomplete or heterogeneous. These gaps are preserved rather than filled by synthetic estimates.

## Target-definition caution

Public Lake Erie nutrient materials use different target presentations and source vintages for some spring phosphorus reductions. The module therefore records the 6,000 metric-ton annual target as target framing only and does not reconcile percentage targets by arithmetic or treat any target as an observed reduction. A future acceptance review should preserve source dates and definitions if target tables are expanded.
