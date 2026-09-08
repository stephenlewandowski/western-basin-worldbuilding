# Phase 12A Vector Ecology Baseline QA

The package contains 20 nodes, 26 edges, 36 surveillance/context rows, 15 habitat associations, 10 uncertainty rows, 27 source records, and Map 38 PNG/SVG.

The Python validator checks exact schemas, IDs, source references, year/method/scale/effort/detection fields, tick status definitions, presence-versus-abundance notes, vector/pathogen/human-case separation, detection-versus-establishment notes, no-records non-absence, county-scale limits, negative scope, map text/readability, the Phase 12A manifest, the cached raw workbook, all Phase 1–11 freeze manifests, active holds, and absence of Phase 12C/Phase 13 artifacts.

The independent R validator re-reads the generated tables, recomputes counts, checks source IDs and controlled vocabularies, checks the raw workbook and manifest hashes through a separate code path, verifies Map 38, and asserts the health boundary and no unsupported future range.

No individual infection probability, disease forecast, hospitalization, mortality, dose, neighborhood risk score, vulnerability/EJ score, unsupported human transmission claim, or continuous abundance/risk surface is included.
