# Western Basin Worldbuilding / Western Basin Atlas

An illustrated, scientifically grounded futures atlas rooted in Toledo, the Maumee watershed, western Lake Erie and the region's connected systems. Real geography and systems constrain the work, which includes sourced studies and clearly marked imagined futures. This repository preserves the sources, models, scripts, provenance and development records behind the Atlas.

**Real geography first; fictional interpretation second.**

## Explore the Atlas

**[Open the Western Basin Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/).** The Atlas is the public publication; this GitHub repository is its research and development record.

Begin with an illustrated place, follow a system through a study, or read [Methods and credits](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/) to understand the evidence and uncertainty. [Updates](https://stephenlewandowski.github.io/western-basin-worldbuilding/updates/) record additions; the [Roadmap](https://stephenlewandowski.github.io/western-basin-worldbuilding/roadmap/) describes areas of ongoing work.

## 2075 Futurescapes

These composite places are **scenarios and design concepts**, not forecasts, measured sites or validated technologies. Each combines a lead image, working detail and qualitative system inset.

- [Glass City 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/glass-city-2075/) — an optical canopy, cassette replacement and public passage through an inherited Toledo-derived street.
- [Maumee Bio-Ag Landscape 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/maumee-bio-ag-2075/) — open fields, selective cultivation, machine service and maintained drainage beside a distinct wetland edge.
- [Industrial Metabolism 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/industrial-metabolism-2075/) — removable process cells, human qualification and external exchange inside an older crane hall.
- [Lake Erie Energy & Security Coast 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/lake-erie-energy-security-coast-2075/) — weather-screen work, civilian survey recovery, utility spaces and an exposed working quay.

## Studies

The collection includes different kinds of explanation. Scenario studies offer context without proving the performance of a futurescape's proposed technology.

| Study | What it presents |
| --- | --- |
| [From Field to Lake](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/field-to-lake/) | Evidence/model-oriented watershed geography and qualitative process explanation, with explicit limits at the receiving lake |
| [The Toledo Intake Crib](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/toledo-crib/) | A real structure and verified location, an approximate representation, and a separately identified future retrofit concept |
| [Farm 2075](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/farm-2075/) | A synthetic agricultural scenario/design study, with drainage, labor and outside dependencies |
| [Industrial Exchange](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/industrial-exchange/) | A scenario/design study of conditional material exchange, qualification and an open district boundary |

## Methods and reproducibility

The Atlas distinguishes **evidence/model** (sourced or reproducibly derived current-system information), **scenario** (conditional future exploration), **fictional canon** (deliberate choices for the imagined setting), and **provisional sketch** (proposed design or narrative material). Technical records use E, S, C and K respectively. A polished picture does not change those statuses.

Source registries, Python builders and validators, independent R checks, figure manifests and review records preserve the chain from inputs to interpretation. Geometry may be qualitative or approximate where measurements are unavailable. Generated futurescape illustrations and authored system insets do not supply measurements or performance evidence. Full definitions, image provenance and rights are explained in [Methods](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/).

- [Source registry](metadata/sources.yml)
- [Research, validation and report index](reports/README.md)
- [Data and asset licensing](docs/references/DATA_AND_ASSET_LICENSING.md)

### Local development

```sh
npm ci
npm run dev
npm test
npm run build
```

Open the URL printed by Vite. The static build is written to `dist/` and uses the GitHub Pages project path `/western-basin-worldbuilding/`. Publication uses the manual [Pages workflow](.github/workflows/deploy-pages.yml); a local build does not publish the site.

The repository's MIT license covers original code and documentation; third-party data and imagery retain their own terms. The public site excludes the third-party crib reference photograph with unconfirmed reuse rights and the held Great Black Swamp reference imagery.

## Game / experimental narrative

[Vesper Station](https://stephenlewandowski.github.io/western-basin-worldbuilding/game/) is a companion experimental browser game. Its narrative does not establish Atlas canon. The game remains separate from the research and study collections.

## Repository guide

```text
assets/                 concept illustrations and system insets
atlas/                  study and futurescape page entries
data/raw/               cached public-source material and reproducible inputs
data/processed/         scientific, network, scenario and integration products
docs/                   research, references, phase briefs and editorial guidance
metadata/               source registries and system/evidence/scenario vocabularies
outputs/maps/systems/   analytical map pairs
outputs/figures/        system diagrams, matrices and conceptual figures
outputs/atlas/          supporting study figures and validation records
outputs/qa/             review graphics
reports/                findings, assumptions, validation, manifests and handoffs
src/python/             acquisition, construction, rendering and validation
src/R/                  independent validation and rendering
src/atlas/              public Atlas content, rendering and styles
src/main.ts             game entry and interaction wiring
src/game/               game data, logic and rendering
game/                   browser-game page entry
methods/, roadmap/,
updates/                public explanatory and project-history pages
```

## Development details

For current state, use [Project Status](PROJECT_STATUS.md), the [canon register](docs/canon_status.md) and the [current handoff](reports/current_phase_handoff.md). Public language follows the [working editorial guide](docs/public_atlas_language_guide.md). Historical filenames, identifiers and phase records remain stable.

### Research architecture and limits

The research spans water and hydrology; geology and strategic materials; energy and grids; compute, communications and sensing; cybersecurity and privacy; freight and industry; ecology and biodiversity; environmental health; nutrient cycling; climate and hazards; governance; population; vector ecology; infectious disease; emerging technology; and cross-system dynamics.

Phases 1–13 establish the underlying system studies. Phase 14 organizes them into 13 integrated system families with common evidence and dependency vocabularies. Phase 15 explores eight technology families and three qualitative futures at 2050 and 2075: coordinated technological adaptation, uneven networked modernization, and high capability/high friction. These are alternative scenario structures, not probabilities or forecasts. Technology capability does not establish deployment, adoption, benefit, authority or resilience.

Phase 16 examines bounded compound stresses: heat/low flow/grid stress; water-quality pressure/water-treatment disruption; freight/material disruption/industrial-energy constraint; and infectious-disease pressure/surveillance/data-governance friction. These qualitative pathways assign no event probabilities, risk or resilience scores, economic losses or predicted health outcomes. Propagation stops when no defensible next step is available.

Reviewed scientific packages are preserved using versioned freeze manifests. “Frozen” means the recorded research is protected from silent changes during subsequent worldbuilding, not that knowledge of the basin is complete. The report index retains the full validation and review history.

### Place and interpretation

Five overlapping interpretive identities organize the setting: Glass City Core, Maumee River Commons, Lake Erie Energy & Security Coast, Black Swamp Country and Great Lakes Industrial Belt. They are not jurisdictions or mutually exclusive GIS polygons. Physical, administrative, historical and fictional geographies remain distinct.

The current physical Toledo intake crib location is resolved at **41.699444, -83.259167**, using the U.S. Coast Guard Light List with NOAA/NDBC and aerial corroboration. Monitoring-station coordinates remain separate records; approximate or future architectural drawings do not inherit surveyed geometry. See the [coordinate-resolution report](reports/toledo_water_intake_crib_coordinate_resolution.md). Great Black Swamp candidate geometry remains held and noncanonical.

### Atlas and narrative development

Phase 17 connects research with illustrated explanation and possible lived worlds: the earlier study-production pattern, scenario packets, developing roles and stories, and current futurescapes. The [study synthesis](reports/phase17a_prototype_findings_and_production_pattern.md), [lived-world packets](reports/phase17b_lived_world_condition_packets.md) and [role/story seeds](reports/phase17c_role_and_story_seed_matrix.md) preserve that lineage. Developing narrative hooks remain provisional unless explicitly established in the canon register.

Glasspunk remains working visual/setting terminology; the separate Glass Basin naming question remains open. Western Basin Atlas identifies the publication, while Western Basin Worldbuilding identifies the project and repository.
