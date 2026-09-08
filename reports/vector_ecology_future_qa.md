# Phase 12C Vector Ecology Futures QA

The package contains 36 scenario assumptions, 36 vector states, 48 habitat states, 30 surveillance states, 168 dependency states, 60 uncertainty states, six comparison rows, 28 scenario-source records, Maps 40/40b, a comparison figure, and deterministic Python/R validators.

The Phase 12C Python validator checks exact schemas and row counts, producer/reference integrity, scenario and horizon coverage, assumption references, fictional/scenario status, baseline separation, A/B/C distinction, 2050/2075 horizon distinction, qualitative-only fields, vector-specific Culex/Aedes/Ixodes logic, surveillance boundaries, habitat scale, negative scope, active holds, Maps 40/40b, Phase 12A/12B freeze hashes, and the Phase 1–11 protected artifact inventory.

The independent R validator re-reads the tables and manifests through a separate code path, recomputes structural counts, checks assumption and baseline references, checks qualitative and negative-scope boundaries, verifies the maps and citations, and independently recomputes protected-artifact hashes.

Prohibited constructs include a continuous disease-risk surface, precise synthetic future range polygons, future case maps, individual-risk or exposure maps, abundance inferred from surveillance effort, climate suitability presented as disease burden, human infection forecasts, vulnerability/EJ scoring, Phase 13 implementation, and frozen-artifact modification.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains UNRESOLVED. Deferred maintenance remains outside this phase: Phase 6B manifest status wording mismatch and Phase 3A missing manifest status.
