# Phase 5A Freight System QA

## Structural checks

- Freight nodes: 22 unique nodes.
- Freight edges: 26 unique relationships.
- All nodes and edges have source IDs, confidence, and notes.
- Existing materials IDs are reused rather than duplicated.
- Public corridor nodes and broad market nodes remain distinguishable from
  physical industrial/material nodes.

## Mode and corridor checks

- Marine: Port of Toledo and Ironville documented port interface.
- Rail: NS, CSX, and CN public Class I corridor context from USDOT/BTS NTAD;
  Wheeling & Lake Erie is retained as a listed port interface without invented
  line geometry.
- Highway: I-75, I-80/90, I-280, and US-23 from existing public TIGER primary
  road geometry and freight context.
- Fuel: generalized external petroleum/fuel interface only.
- No pipeline alignment, capacity, station, valve, pressure, dispatch, or
  hazardous-material route is represented.

## Flow-evidence checks

- Port → Great Lakes/St. Lawrence market is a documented port connection.
- Port → rail carriers and I-75/I-80/90 are interchange/corridor relationships,
  not shipment assignments.
- Port → Ironville and Ironville → generalized market by vessel/truck/rail are
  documented at the port-authority level, with destinations generalized.
- Woodville, Genoa, and Elmore relationships are generalized logistics functions
  unless the source explicitly documents the role.
- Luckey → external licensed disposal is a documented program-level remediation
  logistics relationship without route geometry.
- No edge contains shipment quantity, schedule, count, or facility-specific route.

## Materials Corridor test

**B — WEAKLY SUPPORTED.**

The documented port, rail, highway, Woodville, Genoa, Elmore, and Luckey roles
provide network-level geographic support for an industrial-material
interpretation. They do not establish a single named corridor, continuous
facility-to-facility shipment chain, polygon, jurisdiction, sixth macroregion,
or freight route.

## Artifact checks

`src/python/systems/validate_freight_system.py` validates schemas, endpoints,
source registry references, commodity/mode classes, route/quantity exclusions,
Map 17 and optional flow-figure integrity, and Phase 4A–4C freeze manifests.
`src/R/systems/validate_freight_system.R` provides an independent schema/count,
provenance, mode, endpoint, and artifact check.

The machine-readable result is `reports/freight_system_artifact_check.json`.
The build manifest is `reports/freight_system_manifest.json`.
