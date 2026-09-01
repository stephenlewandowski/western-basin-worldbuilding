# Phase 3B dependency assumptions

## Category definitions

- **dependency_strength:** low = useful but nonessential or indirect; moderate = important functional input with plausible alternatives or unknown substitution; high = core input whose loss would directly impair the named function.
- **outage_sensitivity:** low/moderate/high describe qualitative sensitivity of the named function to an interruption; unknown is used when duration, backup, or operating conditions are not documented.
- **scope:** local = facility or immediate service area; regional = Western Basin/PJM or shared regional system; external = generalized supply/resource outside the modeled asset graph.
- **relationship_basis:** documented = source names the relationship; engineering_dependency = general physical/operational requirement; inferred = cautious system interpretation from documented assets and context.

These are ordinal descriptors, not scores, probabilities, or rankings.

## Modeling boundaries

The separate `energy_dependency_edges.csv` layer reuses Phase 3A node IDs and adds five generalized dependency nodes: natural-gas supply, external fuel logistics, cooling/water, weather resource, and operational communications. It does not modify `energy_system_nodes.csv` or `energy_system_edges.csv`.

The model does not estimate demand, outage duration, storage duration, state of charge, dispatch, fuel inventory, pipeline capacity, feeder topology, transfer limits, congestion, reserve margin, N-1 performance, or power flow.

Monroe’s operating status and planned retirement are retained as a transition dependency. The Oppidan Bowling Green data-center project remains permitted/planned with operation unverified.
