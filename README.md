# Western Basin Worldbuilding

An illustrated futures atlas informed by research into Toledo, the Maumee watershed,
western Lake Erie and their connected systems. The project combines sourced studies,
explicit models and imagined places in 2075. This repository preserves the work behind
the **Western Basin Atlas**.

**[Explore the Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/).**

## What you can explore now

| Area | What it offers | Start here |
| --- | --- | --- |
| Futurescapes | Four imagined 2075 places, each with a lead image, working detail and system inset | [Atlas futurescapes](https://stephenlewandowski.github.io/western-basin-worldbuilding/#futurescapes) |
| Studies | Watershed pathways, the Toledo intake crib, a possible farm and industrial exchange | [Studies](https://stephenlewandowski.github.io/western-basin-worldbuilding/#essays) |
| Model Lab | Synthetic water/nutrient routing diagnostics and a local explorer of saved cases | [Run/data guide](data/model_lab/README.md), [local explorer](src/R/model_lab/explorer/README.md) |
| Methods | Evidence, uncertainty, image provenance, sources and rights | [Methods](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/), [research by subject](reports/README.md) |
| Companion game | Vesper Station, an experimental browser mystery | [Play](https://stephenlewandowski.github.io/western-basin-worldbuilding/game/), [game design](DESIGN.md) |

The four futurescapes are [Glass City 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/glass-city-2075/),
[Maumee Bio-Ag Landscape 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/maumee-bio-ag-2075/),
[Industrial Metabolism 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/industrial-metabolism-2075/),
and [Lake Erie Energy & Security Coast 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/lake-erie-energy-security-coast-2075/).
They are composite **scenarios and design concepts**, without forecasts, surveyed
sites or demonstrated technology performance.

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

## In development

**The Basin Reading Hall** is the selected information-ecology futurescape direction:
a civic place to inspect published findings and request clarification. Its
[production brief](docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md)
and [spatial study](assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg) are
development material; finished imagery remains pending. Narrative roles and stories
also remain provisional. Great Black Swamp candidate geometry remains held/noncanonical.

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
