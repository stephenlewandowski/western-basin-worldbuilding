# Technical reader guide

The [Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/)
is the public publication. This repository keeps its research, models, source
records and development history. Start with [current project status](../PROJECT_STATUS.md)
and [research by subject](../reports/README.md), rather than reconstructing the
project from old phase milestones.

## Where to look

| Need | Location |
| --- | --- |
| Findings and scientific limits | [Subject index](../reports/README.md); each package retains findings, assumptions, sources, QA and manifests |
| Sources and rights | [Source registry](../metadata/sources.yml), [licensing notes](references/DATA_AND_ASSET_LICENSING.md) |
| Quantitative diagnostic examples | [Model Lab run/data guide](../data/model_lab/README.md), [local explorer guide](../src/R/model_lab/explorer/README.md) |
| Current visual development | [Reading Hall continuity lock and plan](phase_briefs/hf05_reading_hall_continuity_lock.md), [original brief](phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md), [house style](phase_briefs/phase17d_public_visual_style_guide.md) |
| Stories, comics and game scenes | [Story workshop](../stories/README.md), [small scene template](templates/scene_card.md), [comic and reader simulation](../reports/reading_hall_comic_reader_simulation_2026-10-03.md) |
| Preserved worktree drafts | [Archive guide](archive/README.md), [inventory](../reports/worktree_draft_inventory_2026-10-03.md) |
| Setting choices and holds | [Canon register](canon_status.md); provisional design material is not canon |
| How to resume work | [Current handoff](../reports/current_phase_handoff.md), [workflow](agent_workflow.md) |
| Earlier decisions | [Status history](../reports/project_status_history_2026-10-03.md), [handoff history](../reports/handoff_history_2026-10-03.md), [changelog](../CHANGELOG.md) |
| Companion game | [Design](../DESIGN.md), `src/game/`; separate from Atlas science and canon |

## Directory roles

```text
assets/                 futurescape illustrations, system insets, visual source studies
atlas/                  study and futurescape HTML entries
data/raw/               retained source material / reproducible acquisition inputs
data/processed/         reviewed scientific, network, scenario and integration products
data/model_lab/         synthetic input cases, assumptions and configuration
metadata/               source registries and evidence/system/scenario vocabularies
outputs/maps/systems/   analytical map pairs
outputs/figures/        system diagrams and matrices
outputs/atlas/          study outputs, manifests and review lineage
outputs/model_lab/      saved synthetic runs; observations/ is a separate source-record display
outputs/qa/             source/geography review artifacts
reports/                findings, sources, checks, freezes and decision history
docs/                   briefs, reference material, editorial and workflow guidance
src/python/, src/R/     acquisition, builders, rendering and independent validation
src/atlas/              public content, rendering and styles
src/game/               companion game data, logic and rendering
stories/                provisional fiction workshop and adaptation cards
tests/                  Model Lab regression tests; web tests also live under src/
```

Historical filenames and phase IDs are stable provenance, not public navigation
labels. Avoid bulk renaming. Native SVGs, package CSVs, manifests and alternate
review figures can be necessary even when a final PNG or WebP exists. Freeze
manifests and source references take precedence over a simple “unused file” scan.

`dist/`, `node_modules/`, caches and transient work under `temp/` are ignored.
Some `temp/` directories are registered Git worktrees; some contain the only
local approved image reference or useful review proof. Inspect Git worktree state
and provenance before removing them. Do not delete the directory wholesale.

For local site commands, use the [root README](../README.md#local-checks).
Scientific runtime requirements vary by package; see `requirements-systems.txt`
at the repository root and each package's reproduction notes. Model Lab has its
own Python/base-R checks and optional Shiny dependencies.

## Research architecture and development context

The following context was relocated from the root README. Internal phase names
belong here and in technical records; [current status](../PROJECT_STATUS.md)
governs the active work schedule.


For current state, use [Project Status](../PROJECT_STATUS.md), the [canon register](../docs/canon_status.md) and the [current handoff](../reports/current_phase_handoff.md). Public language follows the [working editorial guide](../docs/public_atlas_language_guide.md). Historical filenames, identifiers and phase records remain stable.

### Research architecture and limits

The research spans water and hydrology; geology and strategic materials; energy and grids; compute, communications and sensing; cybersecurity and privacy; freight and industry; ecology and biodiversity; environmental health; nutrient cycling; climate and hazards; governance; population; vector ecology; infectious disease; emerging technology; and cross-system dynamics.

Phases 1–13 establish the underlying system studies. Phase 14 organizes them into 13 integrated system families with common evidence and dependency vocabularies. Phase 15 explores eight technology families and three qualitative futures at 2050 and 2075: coordinated technological adaptation, uneven networked modernization, and high capability/high friction. These are alternative scenario structures, not probabilities or forecasts. Technology capability does not establish deployment, adoption, benefit, authority or resilience.

Phase 16 examines bounded compound stresses: heat/low flow/grid stress; water-quality pressure/water-treatment disruption; freight/material disruption/industrial-energy constraint; and infectious-disease pressure/surveillance/data-governance friction. These qualitative pathways assign no event probabilities, risk or resilience scores, economic losses or predicted health outcomes. Propagation stops when no defensible next step is available.

Reviewed scientific packages are preserved using versioned freeze manifests. “Frozen” means the recorded research is protected from silent changes during subsequent worldbuilding, not that knowledge of the basin is complete. The report index retains the full validation and review history.

### Place and interpretation

Five overlapping interpretive identities organize the setting: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country and Great Lakes Industrial Belt. They are not jurisdictions or mutually exclusive GIS polygons. Physical, administrative, historical and fictional geographies remain distinct.

The current physical Toledo intake crib location is resolved at **41.699444, -83.259167**, using the U.S. Coast Guard Light List with NOAA/NDBC and aerial corroboration. Monitoring-station coordinates remain separate records; approximate or future architectural drawings do not inherit surveyed geometry. See the [coordinate-resolution report](../reports/toledo_water_intake_crib_coordinate_resolution.md). Great Black Swamp candidate geometry remains held and noncanonical.

### Atlas and narrative development

Phase 17 connects research with illustrated explanation and possible lived worlds: the earlier study-production pattern, scenario packets, developing roles and stories, and current futurescapes. The [study synthesis](../reports/phase17a_prototype_findings_and_production_pattern.md), [lived-world packets](../reports/phase17b_lived_world_condition_packets.md) and [role/story seeds](../reports/phase17c_role_and_story_seed_matrix.md) preserve that lineage. Developing narrative hooks remain provisional unless explicitly established in the canon register.

Glasspunk remains working visual/setting terminology; the separate Glass Basin naming question remains open. Western Basin Atlas identifies the publication, while Western Basin Worldbuilding identifies the project and repository.
