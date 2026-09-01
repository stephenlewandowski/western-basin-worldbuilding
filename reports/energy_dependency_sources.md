# Phase 3B dependency sources

Phase 3B reuses the Phase 3A source registry and adds only sources needed to justify qualitative dependency relationships. The complete machine-readable registry is `data/processed/networks/energy_dependency_sources.csv`.

- NRC’s generic license-renewal environmental statement documents condenser cooling as the predominant nuclear-plant water use. It supports a coarse cooling/water dependency, not plant-specific withdrawal volumes.
- EIA documents that natural-gas power-plant fuel purchases have both supply and pipeline-delivery components, with firm and interruptible arrangements. No Western Basin contract or pipeline is assigned here.
- DOE/NREL and DOE solar-integration material document wind/solar variability and weather/daylight uncertainty. No local forecast, capacity factor, or production estimate is modeled.
- PJM planning material is used only for regional planning/coordination context. No contingency, stability, congestion, reserve, or transfer conclusion is drawn.
- Phase 3A municipal, facility, NRC, EPA, AMP, DTE, and EIA sources continue to govern the named asset identities and statuses.

## Source-use limits

All dependency edges are qualitative and carry an explicit relationship basis, scope, strength, outage sensitivity, confidence, and note. General engineering dependencies are not claims about local operating practice. Unknown duration, demand, topology, and outage effects remain unknown.
