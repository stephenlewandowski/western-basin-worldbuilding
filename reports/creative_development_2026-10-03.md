# Creative development checkpoint — 3 October 2026

**Intent:** turn the research-backed Western Basin into places and encounters that
can support stories, graphic novels and games. This pass follows the user's request
for creative progress with minimal review, while retaining the scientific foundation.

## What can be entered now

- [Basin Reading Hall workshop](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/basin-reading-hall/): three composition studies, a short interactive scene and reusable devices.
- [Before the Last Bus](../stories/before_the_last_bus.md): Renata chooses what to ask, then what to carry home. Three conversations and three endings explore time, public wording and private location detail.
- [Observed river record](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/#observed-flow): the retained complete 2025 Waterville series, with quality flags, separate from synthetic routing.
- Older public insets have six numbered groups and responsive explanations. Their original geometry, assets and builders remain preserved.

The site source adds a fourteenth page entry. Four finished futurescapes and four
studies remain; the Reading Hall is a developing workshop, not a fifth finished
futurescape or a settled fictional institution. Current publication is recorded
at the end of this report.

## Composition judgment and provenance

| Study | Result | Judgment |
| --- | --- | --- |
| [A — Public counter](../assets/phase17d/hf05/hf05_composition_a.webp) | Hands, two folders and consultation dominate; the stepped spine recedes behind ordinary readers. | Strongest lead. It gives the place a human purpose before explaining devices. |
| [B — Field return](../assets/phase17d/hf05/hf05_composition_b.webp) | Closed cooler, dry recorder bench and separate openings frame the hall. | Best supporting threshold view; useful comic establishing panel. |
| [C — Inhabited spine](../assets/phase17d/hf05/hf05_composition_c.webp) | Staff stairs, fixed tiers, access rail and a compact floor-supported service event read together. | Best architectural reference; counter encounter still anchors scale. |

All are **1672 × 941** generated composition studies. Built-in `image_gen` made
three independent new images using the shared brief and distinct camera prompts.
[Exact prompts](../assets/phase17d/hf05/hf05_composition_prompts.json) and the
[image manifest](../assets/phase17d/hf05/hf05_composition_manifest.json) record
tool, date, original PNG hashes and published WebP hashes/dimensions. WebP encoding
uses quality 88, without cropping or repainting. Raw generated PNGs remain local
under `temp/hf05_compositions/` and in the generator's original folder; the tracked
WebPs are the durable project illustrations. No third-party image was used as a
generation reference.

The original [production brief](../docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md)
and [spatial SVG](../assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg)
remain byte-identical. The studies retain the broad counter/spine/threshold concept,
but independently generated perspectives do not lock exact room continuity. The
final blockout should clarify the method dock, capped ground connectors, opaque
compute/plant end and separate dry preservation compartment. Staff/public boundaries
must stay readable. Incidental marks in pictured paper records are illustration,
not quoted findings. Depicted figures are not final portraits of Renata or Hannah.

## Inset migration

The three `_public.svg` derivatives of the Glass City, farm-seam and industrial-hall
insets retain every original shape attribute in order. Only baked-in text,
accessibility metadata and viewing frames change; six markers are added. The
[builder](../src/python/phase17d/build_public_inset_derivatives.py) checks retained
geometry before adding markers. The [lineage manifest](../assets/phase17d/public_inset_derivatives.json)
records original raw/LF hashes, derivative hashes and shape counts.

An independent read-only review checked the six-group semantics against original
assets/builders and the existing coast-inset pattern. Parent visual review checks
desktop/mobile appearance and marker order. No original diagram, accepted image,
builder or scientific result is rewritten. The older farm production-note hash
differs from today's retained source; its historical note remains intact and the
new manifest uses the actual source bytes. No flow arrows or performance claims
were introduced.

## Drafts and lighter production

[Worktree inventory](worktree_draft_inventory_2026-10-03.md) found fourteen untracked
draft files and six valuable ignored inset studies. All twenty are preserved in
one hash-verified archive. Existing approved reference PNGs, animation, Git branches
and scientific history stay in place. No worktree was deleted.

The new [scene card](../docs/templates/scene_card.md) and house-style addition favor
place, person, immediate want, spatial invention, choice and image beats. The
workflow now explicitly permits a small creative prototype with one bounded review.
Public pages lead with an experience; source and limits sit behind Methods and
workshop links. Home, Updates and Roadmap connect the hall, story and observed record.

Three recurring-device candidates are useful immediately: the **edition cabinet**,
**comparison dock**, and **instrument service berth**. They connect to existing
civic interpretation/cassette concepts. Test reuse in another scene before assigning
catalog numbers. This pass makes no new canon or GBI number.

## Is this still worthwhile?

**Yes, as a creative setting; its next value comes from scenes and small games.**
The region gives this project more specificity than a generic future city: a watershed,
working coast, manufacturing inheritance, farm drainage and people with obligations
beyond their jobs. The existing research now supplies enough constraints to make
interesting choices. The Reading Hall demonstrates that record quality and repair
can become visual and human material without a lecture.

The cost is an unusually large technical archive and a tendency to spend more time
explaining review boundaries than making experiences. More frameworks alone would
produce diminishing returns. This pass is productive because it delivers images,
a playable encounter and one real observation display, then reuses older work.

Audience appeal is still untested. The current scene is deliberately small and
low-stakes; it demonstrates tone and interaction, not a finished game or a market
for the setting. Test the next piece with a few readers/players before expanding
the cast, inventing a new engine or commissioning a large graphic novel.

## Next priorities

1. Make a six-panel comic or a second short scene: the return visit, with an answer
   that creates a new practical choice. Establish consistent character portraits.
2. Lock a single Reading Hall blockout using A's camera, then produce a distinct
   working detail and final qualitative inset rather than another concept report.
3. Reuse one hall invention outside the hall—at a neighborhood stop or field edge—to
   see whether it generates a different action and a stronger regional identity.
4. Get a small reader/player response to pace, clarity and enjoyment. Expand only
   the elements people remember or want to return to.
5. Pursue one measured nutrient record only if a concrete comparison needs it;
   preserve synthetic routing until the empirical input/crosswalk conditions are met.

## Validation and publication

Bounded checks completed:

- 22 existing web tests; TypeScript and Vite build with fourteen page entries.
- Fourteen routes at 1440 and 390 px: 28 layout observations, 31 decoded images,
  24 existing source-link targets, local asset/route URLs and internal anchors.
  No horizontal overflow, unnamed links, missing alt text, failed local requests
  or JavaScript exceptions. Three conversations, three endings, restart and
  keyboard activation pass at both sizes.
- Independent story continuity and inset semantic/visual review. A small final
  margin correction improves all four insets on phones; affected routes rechecked.
- 425 repository Markdown links, including the new stories directory; Git whitespace check.
- 30 Python Model Lab regressions and R/Shiny checks of three runs/252 HUCs pass.
  R emits the existing locale startup warnings, with no check failure.
- Git LFS integrity passes. 665 freeze hash references / 654 protected paths have
  zero byte drift and zero changed-path overlap. Original HF-05 brief/spatial SVG,
  accepted model code/cases, original published art and insets remain unchanged.
- Twenty archived payload hashes match originals. The observation builder checks
  complete dates, source identity, units and snapshot qualifier classes.

Source integration and Pages publication follow these checks. See Git history and
workflow outcome for their actual disposition. The cleanup was already integrated as
`6c6ed91` (`docs: integrate repository cleanup and Reading Hall brief`).

**Published:** creative source commit
`351f391e7b93f6ac5d3684cea76d98914ff72b91` was pushed normally to `main`.
The [Pages workflow](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37110062438)
completed successfully, including CI tests/build/deployment. A live mobile browser
check confirms homepage, Reading Hall and Methods HTTP 200, decoded images, no
overflow or JavaScript exceptions, and working story choice/restart. The live
[Reading Hall](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/basin-reading-hall/)
and [observed record](https://stephenlewandowski.github.io/western-basin-worldbuilding/methods/#observed-flow)
are available. A documentation-only follow-up records this outcome; it does not
change the deployed site. Working-tree status is clean after integration.

## Exact source paths in this cleanup/development integration

49 paths relative to the repository root, against starting `ededbb5`.

```text
.github/workflows/deploy-pages.yml
DESIGN.md
PROJECT_STATUS.md
README.md
assets/phase17d/hf01/hf01_canopy_old_wall_section_public.svg
assets/phase17d/hf03/hf03_field_seam_drainage_section_public.svg
assets/phase17d/hf04/hf04_qualification_cell_section_public.svg
assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg
assets/phase17d/hf05/hf05_composition_a.webp
assets/phase17d/hf05/hf05_composition_b.webp
assets/phase17d/hf05/hf05_composition_c.webp
assets/phase17d/hf05/hf05_composition_manifest.json
assets/phase17d/hf05/hf05_composition_prompts.json
assets/phase17d/public_inset_derivatives.json
atlas/basin-reading-hall/index.html
docs/README.md
docs/agent_workflow.md
docs/archive/README.md
docs/archive/worktree_drafts_2026-10-03.zip
docs/archive/worktree_drafts_2026-10-03_manifest.json
docs/canon_status.md
docs/phase_briefs/phase17d_hf01_hf04_production_plan.md
docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md
docs/phase_briefs/phase17d_public_site_update_plan.md
docs/phase_briefs/phase17d_public_visual_style_guide.md
docs/templates/scene_card.md
outputs/model_lab/observations/waterville_daily_flow_2025.csv
outputs/model_lab/observations/waterville_daily_flow_2025.svg
outputs/model_lab/observations/waterville_observation_manifest.json
reports/README.md
reports/creative_development_2026-10-03.md
reports/current_phase_handoff.md
reports/handoff_history_2026-10-03.md
reports/model_lab_empirical_inputs_2026-10-03.md
reports/project_status_history_2026-10-03.md
reports/repository_cleanup_2026-10-03.md
reports/worktree_draft_inventory_2026-10-03.md
src/R/model_lab/build_observed_flow_card.R
src/atlas/content.ts
src/atlas/inset-callouts.ts
src/atlas/main.ts
src/atlas/reading-hall.ts
src/atlas/style.css
src/python/model_lab/build_observed_flow_record.py
src/python/phase17d/build_public_inset_derivatives.py
src/python/qa/validate_markdown_links.py
stories/README.md
stories/before_the_last_bus.md
vite.config.ts
```

No tracked file was deleted. The cleanup record lists the four removed ignored scratch
scripts; active work, provenance and useful ignored sources were preserved.
