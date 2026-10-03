# Project status

**Verified 3 October 2026 against the checkout, GitHub main, saved products and site source.**
This page describes current work. [Historical status records](reports/project_status_history_2026-10-03.md)
retain earlier decisions and checkpoints.

## Available now

| Area | Actual state | Start here |
| --- | --- | --- |
| Research foundation | Phase 1–16 scientific and system packages are preserved at their reviewed versions. They include sourced evidence, derived models and separately labeled qualitative scenarios. | [Research by subject](reports/README.md), [sources](metadata/sources.yml) |
| Public Atlas | Four 2075 futurescapes and four supporting studies have page entries, assets and publication records. The site also has Methods, Updates and Roadmap. | [Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/), [site source](src/atlas/main.ts) |
| Model Lab | v0.1A routing ledger and v0.1B traces/sensitivities are committed synthetic diagnostics. v0.2A is a checked local, read-only Shiny explorer of the three saved v0.1B cases. | [Run documentation](data/model_lab/README.md), [explorer](src/R/model_lab/explorer/README.md), [integration review](reports/model_lab_v02a_explorer_review.md) |
| Basin Reading Hall | HF-05 direction selected; production brief and qualitative spatial study prepared locally. Camera A and lighting are recommendations. Finished imagery and publication remain pending. | [Production brief](docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md), [spatial study](assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg) |
| Narrative and game | Role/story seeds and cast prototypes remain provisional. Vesper Station is a separate experimental browser game. | [Narrative seeds](reports/phase17c_role_and_story_seed_matrix.md), [game design](DESIGN.md) |

The four published futurescapes are **Glass City 2075**, **Maumee Bio-Ag Landscape 2075**,
**Industrial Metabolism 2075**, and **Lake Erie Energy & Security Coast 2075**. They
remain composite scenarios/design concepts, with no new factual deployment or performance
claim. Their imagery and production records were not changed by this cleanup.

## Current development

Phase 17D Atlas/futurescape development is active. Phase 17A's study-production work
and Phase 17B's initial future-world translation are complete; Phase 17C narrative
material is accepted for development, not established canon. HF-05 is the next
visual development priority. Older inset migration remains deferred work.

The [cleanup/status report](reports/repository_cleanup_2026-10-03.md) records the
repository review, conservative archival decisions, reader-facing changes,
validation and remaining debt. This cleanup advances current-state clarity and
Model Lab discoverability; it adds no model or futurescape development.

## Scientific and setting boundaries

- Frozen research products, source/provenance records, accepted outputs and Model Lab mathematics remain unchanged.
- Synthetic Model Lab pulses test accounting and routing assumptions; they are not measured loads, concentrations, travel times or ecological retention.
- Great Black Swamp candidate geometry remains held/noncanonical. The physical Toledo intake crib location is resolved at **41.699444, -83.259167**; monitoring-station coordinates remain separate. See the [coordinate record](reports/toledo_water_intake_crib_coordinate_resolution.md).
- HF-05 architecture and institutional arrangements remain S/K. The invention catalog retains GBI-01 through GBI-03; no new canon or invention number is established.
- The [canon register](docs/canon_status.md) preserves setting decisions; old phase-boundary wording there is historical, not a second current-work schedule.

## Repository and publication state

At the start of this pass, `main`, `origin/main` and GitHub `main` matched
`ededbb5eee7f9cad70517a6e1a1e3449a4eac928`. The worktree already contained HF-05
brief/spatial-study work and associated index/status updates; that work was preserved.
The cleanup and existing HF-05 brief/spatial study are integrated in source.
Pages publication remains pending; a local build is not a publication. Use `git status` and the
[current handoff](reports/current_phase_handoff.md) for the resumption state.
