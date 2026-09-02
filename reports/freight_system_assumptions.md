# Phase 5A Freight System Assumptions

Baseline: **2026**

Phase 5A answers how major physical goods, fuels, agricultural/bulk products,
raw materials, industrial products, and strategic materials may move through the
Western Basin using a modest factual network of public corridors and sourced
node functions.

## Modeling boundary

The model represents:

`major node → public corridor or generalized interface → broad market/material function`

It does not represent every road, rail line, dock, terminal, carrier, ship,
train, truck, pipeline, facility, customer, or shipment.

The following are intentionally absent:

- shipment volumes;
- shipment schedules;
- train, truck, railcar, or vessel counts;
- exact facility-to-facility routes;
- hazardous-material routing;
- pipeline alignment, pressure, capacity, valve, or station detail;
- customer contracts; and
- route optimization or freight forecasting.

## Node policy

Existing materials-system IDs are reused for Area Aggregates Woodville, Martin
Marietta Woodville, Graymont Genoa, Materion Elmore, and Luckey. Freight-only
nodes represent the Port of Toledo, Ironville interface, public carrier/corridor
context, major highways, generalized fuel, and broad external markets.

Coordinates are included only when supported by a public station/facility or
address-level geocoder. The Port of Toledo point is an address-level anchor,
not a terminal or berth. Ironville is deliberately not separately geocoded.

## Corridor versus shipment

A public rail or highway corridor establishes transportation context. It does
not prove that a nearby plant uses that corridor. Similarly:

- Port cargo capability does not identify every customer or commodity movement.
- On-dock Class I rail access does not assign every terminal to every carrier.
- I-75, I-80/90, I-280, and US-23 are freight-relevant corridors, not plant
  routes.
- A material processor's existence does not establish its quarry, customer,
  transport mode, or shipment schedule.

The distinction is recorded in `relationship_basis`, with `documented_flow`,
`documented_corridor`, and `interchange` kept separate from
`generalized_supply_chain` and `engineering_logistics_dependency`.

## Commodity policy

Commodity classes are broad functional labels:

- `agricultural_bulk`
- `grain`
- `aggregate`
- `limestone`
- `lime`
- `petroleum_or_fuel`
- `chemicals`
- `steel_or_metal_products`
- `automotive`
- `industrial_materials`
- `strategic_materials`
- `container_or_general_freight`

A class indicates a documented or generalized commodity function, not a
quantity, customer, origin, destination, or contract.

## Mode policy

Marine, rail, and highway lines are public corridor context. `generalized` and
`multimodal` relationships are used where the public evidence supports a
logistics function but not a specific mode or route. The external fuel node is
an interface, not a pipeline map.

## Cross-system policy

The model includes only two cautious cross-system interfaces:

- generalized fuel logistics → an existing gas-generation node; and
- existing materials/remediation nodes → broad freight or disposal interfaces.

It does not build new Water, Materials, Energy, Freight, or information-control
systems beyond the Phase 5A tables and map.

## Materials Corridor test

Phase 5A finding: **B — WEAKLY SUPPORTED**.

Woodville, Genoa, Elmore, and Luckey have documented or source-supported
industrial/material roles and can be interpreted within a broader Toledo-area
freight network. However, the evidence does not establish one named corridor,
continuous facility-to-facility flow, common operator, route, polygon, sixth
macroregion, or commercial shipment chain. The Materials Corridor remains an
interpretive network concept only.

## Status and provenance

Every node and edge has a `source_id`, confidence, and notes. Existing materials
nodes retain their source-backed status and are not promoted to freight claims
beyond the documented/generalized relationships in the new edge table.
