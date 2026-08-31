# Phase 3A assumptions and relationship semantics

## Inclusion rule

Generation includes the region’s major nuclear, coal, and gas anchors plus the most legible municipal/regional renewable assets. Storage includes the two public EIA facilities found in the study extent. Loads are selected because they are critical water infrastructure or documented energy-relevant industrial processes; they are not ranked by unreported MW demand.

## Edges

`generation_grid_interface` and `bidirectional_storage_interface` mean that an asset participates in the named regional grid context. `grid_serves_load` means only functional electricity dependence. `regional_grid_interface` records broad interconnection context. Every edge is qualified and explicitly disclaims feeder, dispatch, transfer-capability, and power-flow meaning.

## Geographic precision

EIA plant coordinates are used for generation and storage. Existing verified project coordinates are reused for Collins Park, Elmore, and Woodville. Bay View and the planned Bowling Green data center are address/facility-centroid approximations and are labeled accordingly.

## Deferred questions

- Current substation topology and feeder assignment.
- Facility-specific peak/annual demand for water and industrial loads.
- Storage duration, operating strategy, and state of charge.
- Whether the Bowling Green data-center project entered service after its 2025 plan set.
- Transmission ratings, constraints, contingencies, and power flows.

These are candidates for Phase 3B only after source acquisition and a separate method review.
