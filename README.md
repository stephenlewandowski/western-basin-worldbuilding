# Western Basin Worldbuilding

An illustrated futures atlas informed by research into Toledo, the Maumee watershed,
western Lake Erie and their connected systems. The project combines sourced studies,
explicit models and imagined places in 2075. This repository preserves the work behind
the **Western Basin Atlas**.

The aim is a regional future setting people can enjoy exploring and use for stories,
graphic novels and games. Research gives the places their constraints; ordinary
people, surprising devices and consequential choices make them worth entering.

**[Explore the Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/).**

## What you can explore now

| Area | What it offers | Start here |
| --- | --- | --- |
| Maps & regions | An illustrated fantasy map beside real geography, eleven landmarks, five regional readings and four research plates | [Explore the basin](https://stephenlewandowski.github.io/western-basin-worldbuilding/maps/) |
| Original sketchbook | Nine curated drawings of buildings, work machines and people, with three preserved early sheets | [Sketchbook](https://stephenlewandowski.github.io/western-basin-worldbuilding/sketchbook/), [source lineage](assets/atlas/sketchbook/README.md) |
| Futurescapes | Four imagined 2075 places, each with a lead image, working detail and architectural ink sketch | [Atlas futurescapes](https://stephenlewandowski.github.io/western-basin-worldbuilding/#futurescapes) |
| Studies | Interactive connection charts and linked readings: watershed pathways, intake crib, farm, industrial exchange and climate | [Studies](https://stephenlewandowski.github.io/western-basin-worldbuilding/#essays) |
| Model Lab | Synthetic water/nutrient routing diagnostics and a local explorer of saved cases | [Run/data guide](data/model_lab/README.md), [local explorer](src/R/model_lab/explorer/README.md) |
| Methods | Evidence, uncertainty, image provenance, sources and rights | [Methods](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/), [research by subject](reports/README.md) |
| Stories | The Orange Band: a standalone Reading Hall encounter, with earlier sources and ordinary-day drafts preserved | [Play The Orange Band](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/basin-reading-hall/#story), [encounter record](stories/the_orange_band.md), [story workshop](stories/README.md) |
| Companion game | Vesper Station: a CGA night shift with five rooms, two repairs and a Reading Hall dispatch choice | [Play](https://stephenlewandowski.github.io/western-basin-worldbuilding/game/), [game design](DESIGN.md) |

**[Play Erie Drift](https://stephenlewandowski.github.io/western-basin-worldbuilding/erie-drift/).** Take a small fishing boat onto a
fictional Lake Erie in 2075. Choose between two marinas and six familiar grounds,
budget a solar-electric boat’s charge, select bait/tackle and meet a mixed catch,
then return to supper at the landing. [Design and controls](docs/erie_drift_design.md),
[implementation and checks](reports/erie_drift_implementation_2026-10-05.md).
For local development, run `npm run dev` and open
`/western-basin-worldbuilding/erie-drift/` on the printed server.

The four futurescapes are [Glass City 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/glass-city-2075/),
[Maumee Bio-Ag Landscape 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/maumee-bio-ag-2075/),
[Industrial Metabolism 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/industrial-metabolism-2075/),
and [Lake Erie Energy & Security Coast 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/lake-erie-energy-security-coast-2075/).
They are composite **scenarios and design concepts**, without forecasts, surveyed
sites or demonstrated technology performance.

The [Lake Erie coast](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/lake-erie-energy-security-coast-2075/#coast-field-guide)
now explores Davis-Besse and nuclear/compute relationships, alternative fission
and fusion futures, waste stewardship, working security, fish and migratory birds,
and possible Cedar Point rides. A web chart follows electricity, heat, cooling and
custody separately. [Dated grounding and boundaries](reports/lake_erie_coast_context_2026-10-04.md).

## Evidence, models and imagined futures

Sourced observations and reproducibly derived models have stated limits. Scenarios
explore conditional futures; proposed architecture and stories remain design/sketch
material unless deliberately established as fictional canon. Technical records use
E, S, K and C for those distinctions. An illustration supplies no measurement or
performance evidence, and the game does not establish Atlas canon.

Model Lab adds quantitative **accounting tests**, not calibrated watershed prediction.
Its committed cases use synthetic unit pulses to compare qualified routing and
explicit assumptions. They do not estimate measured loads, concentrations, travel
time or nutrient removal. The local read-only Shiny explorer displays those saved
cases; GitHub Pages does not host the R app. Setup, schemas, validators and limitations
are in the guides linked above.

Source registries, Python builders, independent R checks, manifests and review records
preserve reproducibility. [Research records](reports/README.md) and the
[technical reader guide](docs/README.md) provide subject-based routes into that material.
Original code/documentation use the repository's MIT license; third-party data and
imagery retain their own terms. See [licensing notes](docs/references/DATA_AND_ASSET_LICENSING.md).

Maps are a primary way into the world: illustrated regional character beside real
geography, then connected systems and possible lives. Switch between the two
readings on the same page. Composite futures receive
no exact site pins. [Geographic sources](assets/atlas/region/README.md), [concept-art lineage](assets/atlas/visual-refresh/README.md).

## Climate and the working world

The [Climate & Thermal Regime study](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/climate-thermal-regime/)
starts with real Toledo airport, Lake Erie surface-temperature and ice histories,
then follows heat through shade, electricity peaks, air quality and lake mixing.
[Five small indicator families](data/climate/README.md) retain units, source hashes
and coverage. A first Lucas County comparison uses three published climate-model series;
full ensemble/member extraction and lake projections remain further work. [Readiness and evidence](reports/climate_integration_2026-10-05.md),
[place/system matrix](reports/climate_futurescape_matrix_2026-10-05.md) and
[future art direction](docs/climate_art_direction.md). Existing accepted imagery
remains unchanged. The public study remains a prototype with explicit data boundaries.

A Glass City summer afternoon is now playable in **[The Usual Table](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/glass-city-2075/#summer-scene)**:
peaches, dominoes and a missing patch of shade change where two friends spend
their afternoon. [Scene and new illustration](stories/the_usual_table.md),
[separate local climate calculation](reports/glass_city_summer_and_local_climate_2026-10-05.md).
The story's weather is fictional; it is not a model prediction for that day.

## In development

**The Basin Reading Hall** is the selected information-ecology futurescape direction:
a civic place to inspect published findings and request clarification. Its
[production brief](docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md)
and [spatial study](assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg) now
have [three composition studies](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/basin-reading-hall/)
and the published standalone encounter, *The Orange Band*.
The earlier bus/shirt storyline is superseded;
its [exact sources](stories/archive/reading_hall_2026-10-04/README.md) and narrative
records remain preserved. [Implementation and publication record](reports/orange_band_implementation_2026-10-04.md).
Composition A fixes the hall's visual orientation;
[a small continuity plan](docs/phase_briefs/hf05_reading_hall_continuity_lock.md)
keeps subsequent scenes in the same building. Architectural detail and cast remain
provisional. The six-panel strip failed human-author continuity review and is
withdrawn; its assets and sources remain in the repository. Ordinary people in
distinctive working places remain promising, with interactive encounters currently
communicating that idea better. Agent impressions are not a successful audience test.
[Assessment](reports/reading_hall_comic_reader_simulation_2026-10-03.md) and
[scene template](docs/templates/scene_card.md). Great Black Swamp candidate geometry remains held/noncanonical.

A separate [observed river explorer](https://stephenlewandowski.github.io/western-basin-worldbuilding/maps/#river-record)
lets readers select a day in the retained 2025 USGS flow record, convert units and
inspect its quality flags. A short scientific connection explains why discharge
alone cannot establish nutrient load or the condition of a side channel. It does not turn the synthetic
Model Lab into an empirical watershed predictor. [Input assessment](reports/model_lab_empirical_inputs_2026-10-03.md).

[Current project status](PROJECT_STATUS.md) distinguishes available work from active
development. [Updates](https://stephenlewandowski.github.io/western-basin-worldbuilding/updates/)
record public additions; [Roadmap](https://stephenlewandowski.github.io/western-basin-worldbuilding/roadmap/)
describes ongoing questions. Historical decisions remain in the report index and changelog.

## Local checks

```sh
npm ci
npm run dev
npm test
npm run build
python src/python/qa/validate_markdown_links.py
```

Use the Vite URL printed by the development server. The static build goes to ignored
`dist/` under `/western-basin-worldbuilding/`; the manual [Pages workflow](.github/workflows/deploy-pages.yml)
publishes it. A local build does not publish. Model Lab launch/check commands are in
its separate guides, including R/Shiny setup.

For contribution and recovery, read the [technical guide](docs/README.md),
[workflow](docs/agent_workflow.md) and [current handoff](reports/current_phase_handoff.md).
Preserve frozen research, source records and active work before changing structure.
