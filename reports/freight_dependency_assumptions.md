# Freight Dependency Assumptions

Baseline: **2026**

Phase 5C is a qualitative dependency layer over accepted/frozen Phase 5A and
Phase 5B freight evidence. It does not modify either baseline.

## Dependency semantics

- `marine_gateway_dependency` — broad dependence on the Port of Toledo or Great
  Lakes marine gateway.
- `rail_dependency` — qualitative reliance on a rail corridor or rail interface.
- `highway_dependency` — qualitative reliance on a major highway corridor.
- `fuel_logistics_dependency` — broad external-fuel interface.
- `external_market_dependency` — orientation toward external markets or disposal.
- `interchange_dependency` — reliance on a documented or qualified modal/carrier
  interface.
- `single_mode_dependency` — a broad function has limited plausible modal
  alternatives; this is not an operational proof.
- `multimodal_dependency` — multiple modes are visible, but substitution is not
  assumed feasible.

## Qualitative classes

`high`, `moderate`, `low`, and `unknown` are ordinal descriptors. They are not
probabilities, outage estimates, vulnerability scores, or optimization results.

`known_redundancy` records only named or visible alternative interfaces. A blank
or qualified alternative is recorded under `unknown_redundancy`; no redundancy
is inferred from geographic proximity.

## Modal substitutability

Modal substitutability asks whether another mode could plausibly serve the same
broad function. It does not claim that a substitute is operationally available,
permitted, economical, or equivalent in capacity. Bulk marine, strategic-material,
and external-fuel functions receive conservative `low` or `unknown` values where
no source establishes substitution.

## Node and interface policy

Existing Phase 5A node IDs are reused. Generalized markets, the Port, major
corridors, and the external fuel interface remain broad analytical interfaces.
No new facility route, hazardous-material route, pipeline detail, or security
target is created.

## Cross-system policy

The dependency layer may connect freight to the existing energy node
`ENE-EIA-59764` as a generalized fuel-interface relationship. It does not create
new Water, Materials, Energy, Information, or Freight infrastructure models.

## Boundary

Dependency concentration is not vulnerability. The model does not identify
exploitable chokepoints, sabotage opportunities, sensitive facility access,
security weaknesses, hazardous routes, shipment volumes, or future freight
scenarios.
