# The Orange Band — implementation and publication

4 October 2026. Starting main clean at
`1f24ad335a7e148ad674032a31150f03b6432a30`.
The user requested the replacement and explicitly said to stop for human
narrative review: **do not commit, push or deploy**. That 4 October checkpoint
was local and is preserved below. On 5 October the user explicitly authorized
**commit / push / publish**, with clearer reader-facing Hall descriptions.
The newer instruction supersedes the earlier stop; it does not establish
audience success or new canon.

## Implementation

The working Reading Hall page now presents one standalone encounter at `#story`:
The Orange Band. The existing artwork and orientation remain. Three optional
conversations and three mutually exclusive endings focus on Renata’s daughter
waiting beside the water. The Hall can clarify the card’s basis and a place;
it cannot produce the missing water answer or decide for her.

A permanent blue/orange/gray legend precedes the controls. The native dialog
contains a fictional Water Conditions Card for Willow Steps, 12–14 July 2075,
edition 4: a small patterned schematic map, labeled field-visit points, model
band and no-coverage side channel. The diagram says SCHEMATIC / NOT TO SCALE.
The place ring is not another observation or real address. The card explicitly
states that it determines neither safe/unsafe nor clean/contaminated water, and
is not real monitoring, GIS or current Model Lab output.

Keyboard/native controls preserve card dismissal/focus return, revisit-able
questions, one locked ending and restart. The story introduces no score,
countdown, saved state or interaction network requests. Home/maps/Roadmap,
Updates, metadata and current guides promote only the replacement in the
working site. Previous published deployments remain historical and unchanged.

Exact old scene source bytes are retained in
[the archive](../stories/archive/reading_hall_2026-10-04/README.md). The first
module was replaced in place; the sequel module moved outside the build.
Earlier narrative documents are marked superseded and link to those snapshots;
older dated assessments remain history. The comic stays withdrawn; only its
archive README’s obsolete active-story link is corrected, with art/source
unchanged.

## Narrative refinements for review

- “This card doesn’t cover our channel” avoids claiming the channel was never
  visited in any other period.
- Blue dots remain visited points, without an invented observed-area boundary.
- If the optional exact-location comparison happened, the second ending uses
  the same point; its choice becomes “Ask her to wait for you.”
- The third ending introduces its wording-review request before referring to it
  later. No accepted revision or new observation appears.
- The third ending stops at the daughter’s interpretation, without a lesson
  summary or sensational harm.
- Renata remains public-side. Staff take the closed case at the left-rear hatch;
  Hannah brings a dry route copy to a public table only after custody handoff.

These are continuity/editorial checks, not a claim of successful human narrative
review. All endings use the same unresolved record and promise no future visit,
measurement, jurisdiction or universal capability.

## Local preview and validation

Preview while Vite is running:
`http://127.0.0.1:4175/western-basin-worldbuilding/atlas/basin-reading-hall/#story`.
Validation completed on both the development server and production build:

| Check | Result |
| --- | --- |
| Existing web tests plus encounter tests | 42 tests in 6 files passed. |
| Production build | TypeScript and Vite passed; 15 public routes built. |
| Browser playthroughs | Chromium at 1440, 390 and 320 px: all three endings, conversation revisits, checked/unchecked location choice, locked ending and full restart passed. |
| Card and keyboard | Enter, Tab, Shift+Tab, Escape and Close passed; focus returns to the card opener. Opening/dismissing the card preserves progress before and after an ending. |
| Mobile layout | Touch controls, dialog scrolling and page/dialog widths checked at 390 and 320 px; no horizontal overflow. Desktop/mobile screenshots visually reviewed. |
| Interaction isolation | Zero story-triggered network requests or storage writes; no browser runtime errors in the playthroughs. |
| Route integration | 15 routes return 200 on the production preview; no retired story promotions, stale sequel anchors, duplicate IDs or missing local fragment targets. The withdrawn comic route is absent from the build. |
| Repository links | 551 repository-relative Markdown links passed. |
| Whitespace and LFS | `git diff --check` and `git lfs fsck` passed. Git reports routine LF/CRLF checkout warnings only. |
| Preservation | 636 unique protected paths, including freeze-manifest products, canon register and Hall continuity lock, match the starting checkpoint. No scientific/model/output/art path overlaps. |
| Superseded source | Both archived modules match the original committed text after Git line-ending normalization; archive hash tests passed. |

Temporary scripts, screenshots and machine-readable browser results remain in
ignored `temp/orange-band/`. These checks do not substitute for human narrative
review, screen-reader evaluation or testing on every browser. The local preview
server's fallback for unknown URLs is not evidence of a deployed 404.

Frozen science, Model Lab mathematics/outputs, Waterville observations, Hall
continuity lock and canon register must remain unchanged. Only the observed-flow
interface’s story-reference copy changes; its calculations and record do not.

## Exact changed paths

Modified:

```text
PROJECT_STATUS.md
README.md
assets/phase17d/hf05/comic/README.md
atlas/basin-reading-hall/index.html
docs/templates/scene_card.md
reports/README.md
reports/current_phase_handoff.md
src/atlas/main.ts
src/atlas/observed-flow.ts
src/atlas/reading-hall.ts
src/atlas/region-explorer.ts
src/atlas/style.css
stories/README.md
stories/before_the_last_bus.md
stories/the_return_visit.md
```

Added, currently untracked:

```text
reports/orange_band_implementation_2026-10-04.md
src/atlas/reading-hall.test.ts
stories/archive/reading_hall_2026-10-04/README.md
stories/archive/reading_hall_2026-10-04/reading-hall.ts.txt
stories/archive/reading_hall_2026-10-04/return-visit.ts.txt
stories/the_orange_band.md
```

Removed from its active location, preserved above:

```text
src/atlas/return-visit.ts
```

## Historical stop state · 4 October

At that checkpoint, changes were uncommitted on `main`; HEAD and upstream stayed at the starting
checkpoint. No push or deployment had been performed. The public site still
served the earlier storyline pending review and subsequent authorization.
Working tree at that point: 15 modified paths, 6 untracked additions and 1 source
move shown as a deletion. Nothing was staged. No new canon or science was established.

## Publication · 5 October

The user authorized publishing the encounter and requested removal of internal
production language from the Hall page. “Inside the Reading Hall” replaces the
unclear composition heading. The view captions describe field returns and
instrument rooms; the device section describes ordinary work, and the grounding
paragraph distinguishes fictional people/card from real project research.
Composition A and the continuity lock remain unchanged.

Pre-publication checks on 5 October passed: all 42 tests, TypeScript/Vite build,
554 repository-relative Markdown links, whitespace, LFS and preservation of
636 protected files. Production-preview playthroughs pass at 1440/390/320 px,
including all endings, keyboard dialog/focus, restart and 15 public routes.
The revised Hall copy is visually checked at those widths without overflow.

Source `6e3a1178c04a32927fad2972072c3937389f73a1` is committed and pushed to main.
[Pages run 37252340501](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37252340501)
completed successfully and deployed that exact source.

Live Chromium checks at 1440/390/320 px pass all three endings, optional
conversation revisits, checked/unchecked location wording, card inspection and
keyboard/focus return, exclusive ending guard and complete restart. The card
record remains unchanged across choices. Story interactions make no network
requests or storage writes; no runtime errors or horizontal overflow were found.
All 15 public routes return 200 and contain no retired story promotions or sequel
anchors. The revised “Inside the Reading Hall” heading and reader copy appear in
the served bundle. The withdrawn comic route returns HTTP 404.

[Play The Orange Band](https://stephenlewandowski.github.io/western-basin-worldbuilding/atlas/basin-reading-hall/#story).
Ignored `temp/orange-band/live-browser-results.json` and screenshots retain
the local live-browser proofs. These are interaction/integration checks, not a
claim of audience success. A documentation-only checkpoint follows without
changing the deployed build; final Markdown links and whitespace checks pass.
