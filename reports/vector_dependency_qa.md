# Phase 12B Vector / Environment / Human-System Dependency QA

The package contains 28 dependency records, 8 qualitative matrix rows, 8 claim-level evidence rows, and Map 39 PNG/SVG. Phase 12A contains 20 nodes and 36 surveillance/context records and is checked as an immutable working baseline.

The Python validator checks exact schemas, referential/controlled vocabularies, documented-versus-inferred fields, matrix labels, source references, the required relationship families, presence/abundance and pathogen/case boundaries, sampling-effort and spatial-scale caveats, no individual risk or vulnerability score, no unsupported future range, Map 39 integrity/text, Phase 12A artifact hashes, all Phase 1–11 freeze manifests, active holds, and absence of Phase 12C/Phase 13 content.

The independent R validator performs the same checks through a separate code path and independently verifies Phase 12A hashes, the Phase 12B manifest, source references, matrix values, map text, negative scope, and inherited holds.
