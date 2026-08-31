# Phase 2B Materials-System Assumptions

Baseline: **2026**

Status vocabulary: **verified** or **inferred**; no scenario records are present.

## Modeling boundary

The shared node/edge model represents material relationships, not freight itineraries or commercial volume. A spatial point establishes a sourced facility location. It does not establish a supplier contract, transport mode, route, schedule, throughput, reserve, quarry boundary, or customer.

`relationship_basis` controls interpretation:

- `observed` — sourced facility, process, product, or system interface.
- `documented_supply_relationship` — a named public relationship supported by an official party statement.
- `engineering_dependency` — a defensible generalized material-to-function dependency, not a local purchase claim.
- `scientific_inference` — an interpretation supported by regional scientific evidence but not site-specific geometry.
- `supply_chain_inference` — a broad upstream/downstream connection without a named customer or route.

## Carbonate assumptions

- ODNR 1:500,000 carbonate-bearing units are regional occurrence context, not reserves or parcel-scale resource geometry.
- Woodville extraction and Woodville/Genoa processing roles are sourced independently. Proximity does not create an undocumented plant-to-plant edge.
- Lime/carbonate use in water and wastewater treatment is an `engineering_dependency`. The model does **not** say a named local facility supplies Toledo.
- Agriculture, construction, metallurgy, and environmental treatment are broad supported functions, not a claim that every plotted plant serves every sector.
- The accepted `hydrography_physical` layer is map context only. No groundwater flow, quarry capture zone, dewatering impact, wetland drawdown, or aquifer connection is inferred.

## Beryllium assumptions

- USGS evidence places the broad upstream system in Utah-derived material and imported beryl, with intermediate material moving to Ohio. Exact origins, mode, route, schedule, and tonnage are deliberately absent.
- Materion Elmore is `advanced_processing`, with `local_resource=false`; it is not a mine.
- Aerospace/defense, electronics/telecommunications, and precision optics are broad sourced sectors. They are not named Elmore customers.
- The 31 October 2025 Materion–Commonwealth Fusion Systems announcement is a `documented_supply_relationship` for Elmore beryllium fluoride used in FLiBe for ARC. It is not evidence of a Northwest Ohio fusion reactor.
- The 27 July 2022 Materion–Kairos Power collaboration is documented, but its 2026 operating status was not independently reverified.
- Luckey remains legacy/remediation context and is not current production.

## Deferred questions

Current parcel/quarry boundaries, a comprehensive 2026 active-facility census, customer-specific carbonate contracts, named intermediate beryllium origins, transport modes, shipment quantities, and current Kairos operating status remain unresolved. These gaps are represented through inference classes and notes rather than fabricated precision.
