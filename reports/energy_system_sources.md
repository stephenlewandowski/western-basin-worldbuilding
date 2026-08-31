# Phase 3A energy / grid / compute sources

Map 11 is a 2026 factual baseline built from public, authoritative sources. The machine-readable registry is `data/processed/networks/energy_system_sources.csv`.

The generation and storage inventory begins with EIA’s Power Plants in the United States service (EIA-860, EIA-860M, and EIA-923; service period 2025-02). NRC pages govern the operating-license status of Davis-Besse and Fermi 2. EPA permitting corroborates Oregon Clean Energy Center; AMP corroborates Fremont and Bowling Green solar/storage; DTE’s regulatory report qualifies Monroe as operating in the baseline with planned phased retirement.

The grid layer is the EIA/HIFLD public transmission service, clipped to the study extent and filtered to `IN SERVICE` and at least 230 kV. Its geometry is generalized public cartographic context. It is not a complete bus/branch model and supports no inference about direction, capacity, dispatch, congestion, contingency performance, or feeder assignment.

City of Toledo pages document Collins Park and Bay View as critical water-system facilities but publish no electricity-demand values. EPA and company evidence identify the Elmore and Woodville industrial processes, likewise without demand values. City of Bowling Green GIS plans document a 5 MW data-center project at 2501 Woodstream Drive; operation in 2026 is not confirmed, so the node remains qualified as permitted/planned.

## Scope limits

- Capacity fields retain their named source basis; gross, summer, installed, and total operating capacity are not silently conflated.
- Distributed generation below the selected regional-significance threshold is not an exhaustive inventory.
- Substations, feeders, transfer limits, real-time conditions, and power-flow outputs are intentionally absent.
- The baseline contains no fictional future infrastructure or scenario assumptions.
