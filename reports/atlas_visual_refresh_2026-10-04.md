# Atlas visual and interface refresh

4 October 2026. Author-directed revision from starting main
`e14bb6cec9f14f3092f3ca368ed782b4737ed7d4`.

## Result

The approved real-place explorer now sits beside **The Glass Basin**, an
ink-and-wash fantasy map of five imagined regional identities. Illustrated regions
lead the Maps page and homepage teaser; real places and records remain one click
away. Both modes share regional readings and links to futurescapes and encounters.
An explicit URL mode persists on reload; direct observation links open real mode.

Four equipment SVG displays are replaced by architectural ink concept sketches.
The crib study gains a paired approximate present/future sketch. No stick figures
appear in these new equipment sheets. Six numbered equipment relationships stay
in adjacent readable text, separate from inferred perspective and machinery.

Fifteen original study plates are de-emphasized rather than deleted. The retained
watershed map stays visible; crib, farm and industrial study leads use the new
paired drawing or clearly captioned related futurescape art. Linked headings,
ordered steps, comparison columns and tables explain processes and dependencies.
Original plates and validation records remain linked in the source boxes.

The Methods page uses compact observation counts and links to the interactive
daily record. On Maps, the quantitative yearly curve remains available in a
native expandable panel. Exact values, units, conversions, date controls and
approval/estimation flags are unchanged. Diagram styling is not a reason to remove
a useful quantitative plot or the approved physical geography.

## Sources and preservation

[Artwork lineage](../assets/atlas/visual-refresh/README.md) and
[full manifest](../assets/atlas/visual-refresh/manifest.json) retain prompts,
reference hashes, packaging settings and original generated PNGs in a ZIP.
Public WebPs total about 3.9 MB; the preserved master/reference archive is about
23.5 MB and is not imported into the site build. No external crib photo was used.

References are the existing generated futurescape illustrations, approximate
crib source plate, retained geographic derivative and earlier project sketchbook
style. Earlier sketchbook geography and superseded region terminology were not
adopted. The map provides stylized geography, no territorial or historical swamp
boundary, no exact future-site pins and no new fictional canon. Sketches provide
no measured engineering, performance or technology validation.

Frozen scientific products, original figures/builders, accepted Model Lab cases,
Waterville observations, source/provenance records and active Reading Hall work
are preserved. The comic **failed human-author continuity review** and stays
withdrawn; the two interactive encounters remain available. This revision is a
presentation improvement, not a successful audience test.

## Changed paths

- `src/atlas/content.ts`, `main.ts`, `region-explorer.ts`, `observed-flow.ts`,
  `inset-callouts.ts`, `style.css`, new `study-reading.ts`.
- New `assets/atlas/visual-refresh/`: `README.md`, `manifest.json`,
  `source_pngs.zip`, `illustrated_regions_2075.webp`, `canopy_blueprint.webp`,
  `industry_blueprint.webp`, `farm_blueprint.webp`, `coast_blueprint.webp`,
  `crib_blueprint.webp`.
- `README.md`, `PROJECT_STATUS.md`, `docs/templates/scene_card.md`,
  `reports/README.md`, `reports/current_phase_handoff.md`, this report.

No tracked files removed. Ignored preparation/screenshot files remain local in
`temp/atlas-visual-refresh/`.

## Assessment and next investment

The two maps serve different kinds of curiosity: imagined regional character
invites exploration, while sourced locations and a real record answer questions.
Architectural sketches fit the existing illustrated places better than vector
people and crowded arrows; prose preserves distinctions without requiring readers
to decode a diagram. Human response remains the useful next check.

Next: test a short map-to-place-to-encounter journey with human readers; refine one
regional encounter with a returning person or device; mature compatible measured
nutrient data on the parallel scientific track. Avoid adding more decorative
diagrams or fake precision. Source plots and maps can remain technical where useful.

## Validation and publication

- TypeScript check and production build pass; 26 web tests pass.
- Repository-relative Markdown links pass (497 links); `git diff --check` passes.
- Browser checks cover 15 routes at 1440 and 390 pixels: no overflow, image decode
  or console failures; local links/assets return HTTP 200; 34 file sources exist.
- Both map modes, all five regional selections, real landmarks, four research
  plates, study section anchors, date bounds/flags/conversion, expandable curve
  and both encounters work. Explicit illustrated mode survives an observation
  hash and reload. Equipment sheets and desktop/mobile layouts inspected visually.
- Git LFS integrity passes. All 654 protected paths are unchanged; 665 historical
  hash references match after documented LF normalization (190 pre-existing
  newline-only differences). Original futurescape assets, Model Lab and active
  Reading Hall work are unchanged. Seven existing worktrees are untouched.
- Manifest verifies public artwork, original PNG entries, geography reference and
  source hashes. The PNG ZIP is absent from `dist`; original equipment SVGs and
  dense flowchart images are absent from the public build.

Source commit `82fce91e255557d8eba7904f8fc81d5c58238b07` is pushed to main.
[Pages run 37167030241](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37167030241)
succeeded for that exact commit. Live checks confirm all 15 public routes return
HTTP 200, illustrated/real modes work, all four equipment images decode, the four
study interfaces are present, the measured flow controls/curve work and both
encounters remain. No page errors occurred; the withdrawn comic route returns
HTTP 404. A following documentation-only checkpoint records this result without
changing the deployed build.
