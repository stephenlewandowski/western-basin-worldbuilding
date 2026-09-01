# Phase 3B QA — critical energy dependencies and reliability

## Result

The completed analytical layer contains **28 dependency edges** and **5 generalized dependency nodes**. It preserves the accepted Phase 3A baseline at 18 nodes and 17 coarse relationships.

## Scientific and classification gates

- Energy → Water: Collins Park and Bay View are high-sensitivity electricity dependencies; no demand, outage duration, or untreated-flow consequence is estimated.
- Energy → Materials: Elmore and Woodville are high/moderate process-load dependencies; no facility MW or process-heat split is invented.
- Energy → Compute: the 5 MW Oppidan project remains planned/unverified and is not treated as an operating load.
- Nuclear: Davis-Besse and Fermi 2 receive qualitative cooling-water and grid dependencies; fuel remains generalized.
- Gas: Oregon, Troy, and Fremont receive generalized natural-gas supply dependencies; no pipeline network or capacity is modeled.
- Coal: Monroe receives external fuel/logistics and cooling dependencies while retaining operating plus planned-retirement status.
- Renewables: weather/resource dependencies are qualitative only.
- Storage: both assets are represented as short-duration-support interfaces with duration and sustained-loss contribution unknown.

## Prohibited-claim review

No power-flow, congestion, transfer-limit, reserve-margin, N-1, outage-probability, restoration-time, blackout-footprint, or future-generation claim appears in the dependency layer or Map 12.

## Artifact and regression review

Map 12 and the 10 × 7 dependency matrix were inspected at full resolution. The Phase 3A freeze validator confirms Map 11 and both Phase 3A tables are unchanged by hash. Existing Phase 1, Phase 2, hydrography, Great Black Swamp, and Markdown-link checks remain separate regression gates.
