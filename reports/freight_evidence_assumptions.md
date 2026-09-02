# Freight Evidence Validation Assumptions

Baseline: **2026**

Phase 5B is an evidence-strengthening layer over the frozen Phase 5A freight
network. It does not replace or edit `freight_system_nodes.csv` or
`freight_system_edges.csv`.

## Evidence classes

- `documented_facility_access` — a public source names access to a facility or
  port, without assigning every movement to it.
- `documented_shipment_relationship` — a public source names a movement or
  movement function, while quantities/routes may remain generalized.
- `documented_interchange` — a public source supports a modal or carrier
  interchange relationship.
- `documented_corridor` — public infrastructure or carrier corridor is
  documented; facility use is not implied.
- `generalized_logistics_dependency` — a sourced industrial/material role implies
  logistics in broad functional terms only.
- `proximity_only` — locations or corridor proximity exist, but access or use is
  not documented.
- `unresolved` — the relevant relationship remains open.

`upgrade_status` records whether Phase 5A evidence is confirmed, strengthened,
unchanged, downgraded, or unresolved. Evidence strengthening does not authorize
new geometry in the frozen Phase 5A network.

## Modal distinction

Physical co-location and documented interchange are separate fields. The Port of
Toledo's on-dock Class I rail and heavy-haul access are documented interfaces.
Ironville's vessel input and truck/rail outputs are documented movement
relationships, but the model does not claim a specific transfer design between
modes. W&LE's public listing is retained as relevant but not upgraded to a
specific interchange.

## Commodity distinction

The port source strengthens general cargo, bulk, liquid-bulk, industrial/metal,
and Ironville HBI-related functions. Broad agricultural/bulk context remains
from FAF; a Toledo-specific grain shipment or elevator relationship is not
created. No source-supported quantity is needed for this phase.

## Facility policy

Existing Woodville, Genoa, Elmore, and Luckey nodes are referenced by their
Phase 5A IDs. Facility existence, product role, or remediation status does not
become evidence of freight access without a source. The resulting corridor test
is therefore intentionally conservative.

## Materials Corridor decision

Phase 5B result: **B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT**.

The evidence is stronger for a network of industrial/material relationships and
modal interfaces than it was in Phase 5A, but it does not support a single
coherent geographic corridor. The term remains a loose network/worldbuilding
motif, not a polygon, route, jurisdiction, or sixth macroregion.

## Exclusions

No shipment-volume simulation, route optimization, hazardous-material route,
pipeline capacity, train/truck/vessel schedule, security-sensitive logistics
topology, or future freight content is introduced.
