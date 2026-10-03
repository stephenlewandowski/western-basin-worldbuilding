# Maps, regional character and quantitative evidence

**3 October 2026.** Starting source checkpoint: `5852857882f7ae13fb4b502ca7f555ef938d971c`,
clean `main` matching `origin/main`. This work advances the user's request to give
earlier maps, regional characteristics and landmarks a larger role in the Atlas,
while connecting exploration to real observations and scientific principles.

## Result

Maps are now a primary entry from the homepage and main navigation. The public
map uses retained geography, eleven sourced landmarks and five overlapping
regional readings, with direct links into existing futures, studies and Reading
Hall encounters. Futures receive no exact site pins. Source geography stays
separate from the fictional identities.

The approach follows the [original regional Atlas intent](../docs/worldbuilding/Glasspunk_Regional_and_Systems_Atlas_v0.1.md):
real geography first, regional character second, systems and dependencies third.
The five readings are Glass City Core, Maumee River Commons, Black Swamp Country,
Energy & Security Coast and Great Lakes Industrial Belt. They change highlighted
anchors and interpretation, without inventing territorial polygons.

Four earlier research plates have a visible public collection: watershed
pathways, geology/materials, energy/grid/compute and freight/industry. Original
plate labels, notes, files and dated source records remain unchanged. The newer
geographic entry excludes nonphysical connectors; the older pathway plate keeps
its distinct analytical connections and explains them in its accompanying copy.

## Geographic choices and preserved boundaries

The [new derivative](../assets/atlas/region/README.md) reads the retained GeoPackage's
seven HUC8 watersheds, Lake Erie and physical waterways. A standard-library
[builder](../src/python/atlas/build_region_explorer.py) decodes 2D GeoPackage WKB,
projects a local equirectangular drawing and generalizes render copies only.
The public subset has 4,270 physical features with stream order ≥5. No stream
width represents discharge, nutrient load or travel time. Smaller channels and
much tile drainage are absent; no complete drainage claim is made.

Municipal landmarks use Census representative points. Materials and energy
landmarks retain source-specific address/asset precision. This avoids two older
anchor traps: the legacy intake monitoring point is not the physical crib;
the older pathway builder's treatment-plant coordinate is not civic Toledo.
The new Toledo representative is 41.664071, −83.5818608. The crib uses its
resolved physical position, 41.699444, −83.259167. Waterville's real USGS
observation point is 41.5000526, −83.7127145.

Accepted older plates and builders are preserved, rather than silently corrected.
The Great Black Swamp candidate remains held/noncanonical, without a public
boundary. Archived generated concept maps and unlicensed reference photographs
are excluded. No frozen science, accepted model result, Model Lab mathematics,
Reading Hall composition, source/provenance record or worktree draft is changed.
The comic remains withdrawn after failed human-author continuity review; its
route and promotional assets are not restored.

## A bounded scientific connection

The Waterville explorer copies all 365 original daily means and their flags from
the complete retained 2025 CSV. Date, slider, previous/next and example-day controls
keep the chart cursor and readout synchronized. Approval and estimated flags
describe the September 2026 snapshot, rather than present USGS approval.
Estimated and approved can overlap. Original ft³/s values are retained; m³/s is
a dimensional conversion rounded for display.

Highest and lowest refer to this year's daily means: 68,200 ft³/s on 4 April
and 65 ft³/s on 25 October. They are not all-time or instantaneous extremes.
The first provisional day is 19 November; an estimated/approved day is 1 January.
No interpolation, gap filling, gauge-to-HUC allocation or new routed case is added.

The scientific principle is kept close to the interaction: discharge describes
water passing a point, while transported nutrient mass requires concentration
and discharge over time. The displayed relation is `mass = ∫ C(t) Q(t) dt`.
Compatible nutrient measurements remain a separate next step, with no invented
observed concentration or load. [USGS nutrient-flux methods](https://pubs.usgs.gov/of/2007/1080/of-2007-1080/methods.html)
and [streamgaging basics](https://www.usgs.gov/mission-areas/water-resources/science/streamgaging-basics)
ground the explanation. This record cannot answer the Reading Hall character's
question about a specific picnic channel, flood extent or safety.

Model Lab remains a parallel synthetic accounting track. The website offers
observation and scientific context; it does not host Shiny or duplicate its model.

## Interface and reproducibility

- Map and regional entry from the homepage/header/footer, plus context links back
  from futures and studies; Methods, Updates and Roadmap explain the addition.
- Whole-basin and coast views, pointer/keyboard landmark controls and equivalent
  native place buttons. Selecting an upstream point restores a view that contains it.
- Date controls preserve bounds; beginning/end buttons disable appropriately.
- Earlier maps are selected individually and can be opened full size. Original
  images are imported directly, avoiding duplicate raster assets.
- Map code/data load separately on the map route; existing pages do not load the
  interactive geographic dataset. The homepage gets a small SVG preview.
- A source manifest records all derivative inputs, hashes, settings and credits.

## Assessment and next investment

This remains worthwhile as a regional exploratory setting. The material already
supports a coherent route from a recognisable river basin to distinctive work,
devices and consequential human choices. The new map gives that collection a
spatial spine; the measured day offers a concrete scientific action that does
not require reading a technical report first.

This is an assessment of the available products, not evidence of successful
human audience response. Maps and the two playable encounters now provide useful
ways to test what an unfamiliar reader follows next. No new agent impressions
are presented as a human audience result.

Recommended next priorities:

1. Watch a few human visitors navigate map → region → place/encounter and gauge
   → day. Refine labels and pace from their actual choices.
2. Develop one compact upstream or industrial encounter using an existing person
   or device, after human-author response to The Return Visit.
3. Mature measured nutrient inputs with compatible units, dates, flags and
   geographic crosswalk. Do not turn a regulatory target into an observed load.
4. If visitors want more quantitative interaction, expose a compact conservation
   comparison from the existing saved Model Lab ledgers, without changing its math.

Remaining debt: original dense plates require full-size reading; some historical
plates use legacy anchor labels; this generalized map omits roads, many waterways
and detailed settlement polygons. Current energy/facility status is not refreshed
by publishing a dated baseline. Further map layers should answer an actual reader
question rather than expand a dashboard indefinitely.

## Validation and publication

Local tests: 26 web tests pass; TypeScript and the 15-route production build pass.
All 485 repository-relative Markdown links pass. Derivative input/output hashes match; rebuilding reproduces the exact
map/data/preview bytes. Git LFS fsck passes. Preservation checks find no drift in
654 frozen paths, 665 historical hash references after expected checkout newline
normalization, original Reading Hall work or accepted Model Lab/futurescape assets.
Comic archive content is unchanged and its former route is absent from the build.

Browser checks pass across 15 routes at 1440 and 390 pixels: 30 layout observations,
36 decoded image targets and 32 repository source targets; local links/assets
return HTTP 200, internal anchors resolve, and there are no page errors, failed
local requests or horizontal overflow. Region/landmark selection, coast/upstream
view changes, all four research plates, keyboard/date/slider controls, extreme
and quality-flag examples and direct map anchors pass. Both Reading Hall
encounters retain their checked ending/restart behavior. A focused read-only
review found no scientific/continuity blocker and suggested the implemented
mobile link to the regional reading.

Derivative input hashes canonicalize text to LF and preserve exact GeoPackage
bytes, avoiding false hash drift across Windows checkout conventions. Original
scientific manifests and products remain unchanged. Model Lab/R regressions
were not rerun: this changes presentation only, and their code/results are
verified unchanged.

Feature commit `349051face5470d211f1862e4395beb2c3bf927e` is pushed normally to
`main`. [Pages run 37123839201](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37123839201)
completed successfully, including Linux CI tests/build and deployment.

Live [Maps](https://stephenlewandowski.github.io/western-basin-worldbuilding/maps/),
homepage, Methods, Updates, Roadmap and Reading Hall all return HTTP 200.
Public map controls, Waterville low/provisional examples and the geology plate
work; the original and sequel encounter anchors remain present. Browser checks
report no page errors. The former comic route still returns HTTP 404. The
publication-checkpoint commit changes documentation only, without another web
build or deployment. Final normal push leaves clean `main` matching origin.

## Exact changed paths

No files were removed or relocated. All source additions are below; ignored local
QA screenshots/scripts and `dist/` are not published repository scaffolding.

- `PROJECT_STATUS.md`
- `README.md`
- `assets/atlas/region/README.md`
- `assets/atlas/region/basin_preview.svg`
- `assets/atlas/region/region_explorer.json`
- `assets/atlas/region/source_manifest.json`
- `docs/README.md`
- `maps/index.html`
- `reports/README.md`
- `reports/atlas_maps_and_evidence_2026-10-03.md`
- `reports/current_phase_handoff.md`
- `src/atlas/landmarks.json`
- `src/atlas/main.ts`
- `src/atlas/observed-flow.test.ts`
- `src/atlas/observed-flow.ts`
- `src/atlas/region-explorer.ts`
- `src/atlas/style.css`
- `src/python/atlas/build_region_explorer.py`
- `tsconfig.json`
- `vite.config.ts`
