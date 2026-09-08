# Phase 11A Population & Settlement QA

The builder produced 62 nodes, 918 observations, and 44 structural/employment relationships for Map 35. Python validation checks exact columns, IDs, units, source references, vintages, geographic scales, person/household/housing/density/job distinctions, observed/estimated/modeled status, Census versus LODES separation, and absence of individual-level or vulnerability constructs.

The independent R validator re-reads the generated files and recomputes the principal counts, enum checks, source references, map artifact/text checks, working-manifest hashes, prior Phase 1–10 freeze integrity, active holds, and Phase 11C absence through a separate code path.

Negative scope: no social-vulnerability or EJ score, protected-class ranking, individual profile, individual movement, dose, illness, utility-territory assignment, unsupported demographic forecast, Indigenous-history/HGIS layer, or Phase 11C implementation.
