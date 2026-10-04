# Vesper Station: one night, two repairs

4 October 2026. Requested controlled enhancement of the linked CGA game.
Starting main: `6367c32be501cdac198a7bbc42837a8bff5b5600`, clean.

## Result

The separate experimental game now has five fixed locations and two acts:
restore the lights, then restore a district heat-return loop. The previously
unused glove opens the pump-house return wheel. A river terrace connects glass
roofs, industry, river life and the Reading Hall through scenery, a basin route
board and a local queue choice. The final handoff executes either record-first
or render-first; both protect essential circulation and give Mara/Niko a small
human payoff. A short [scene card and route](../DESIGN.md) replace the stale
slice-design description. The intended 10–15-minute scale has not been measured
with unfamiliar human players.

The corridor’s horizontal lines came from a full-width repeated scenery loop.
Localized overhead pipes and floor seams now replace it. CGA palette and logical
resolution remain; regional silhouettes, workers and equipment-state indicators
make progress visible without an art/style replacement.

Native scene/item/conversation/dispatch/review buttons provide touch and keyboard
parity. Tab retains ordinary focus navigation. Long text has a readable Shift
Notes area and nearby mobile feedback; canvas excerpts stay inside their panels.
Hints orient without granting clues/items. Wrong-tool attempts are recoverable.
The nonfunctional Mute control is removed. Save/load retains its original key,
filters unknown identifiers, catches storage denial and migrates older review
saves to the unfinished service handoff without discarding case selections.
Completed endings retain their text through save/load; replay explicitly returns
to before filing, rather than undoing an already sent record within the story.

## Boundaries and remaining questions

Vesper is a composite fictional Toledo river-edge service station, not a regional
control center or a real installation. Heat circulation, a defined return path
and flexible work scheduling are qualitative principles, enacted through toy
controls. No new measured data, engineering performance or Model Lab coupling is
claimed. Frozen science, accepted model outputs, empirical observations, Atlas
art and Reading Hall continuity remain unchanged.

The inherited cause-review scores remain hand-authored game rules. Public copy
states that the assessment covers cited items and other clues may disagree.
Before expanding the mystery, improve the separation between testimony, player
disclosure actions and causal evidence. This limited update adds no extra cause
evidence beyond the existing canvas capacity.

The chapter is a useful playable bridge from regional systems to ordinary people.
It is ready for human play, not validated as fun by automated checks. Next effort
should go into first-time player observations—can they find the pump door,
understand the queue tradeoff, and remember Mara/Niko? Refine this chapter before
adding locations, combat, resource systems or another case. Audio remains absent.

## Validation and publication

- `npm test`: 38 tests in five files pass, including full service branches,
  progression gates, recoverable tools, hints, new/old saves and storage denial.
- `npm run build`: TypeScript and all 15 Vite routes build successfully.
- Browser: complete five-room route at 1440px and 390px, both queue orders,
  report/withhold, saved service progress, ending save/load and handoff replay
  pass. Native Enter/Tab work; mobile essential actions use touch taps. No page
  errors or horizontal document overflow. Scene/text screenshots inspected.
- Home, Updates, maps, industrial futurescape and Reading Hall return links
  resolve during both browser runs; Updates promotes the new game chapter.
- `git diff --check`: pass. Repository-relative Markdown links: 527 pass.
- `git lfs fsck`: pass. Largest existing tracked blobs inspected; this change
  adds no binary assets or generated output.
- 634 unique protected paths / 645 freeze-manifest references match starting
  `6367c32` bytes, allowing only Git checkout CRLF/LF conversion for text.
  Changed paths do not overlap scientific/model/output/art paths.

Integrated and pushed by normal fast-forward:
`b5e66cb10ea1e1d349ab2bc5ece115a1a4c9975d`.
[Pages run 37185856049](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37185856049)
succeeded for that exact source. The
[live game](https://stephenlewandowski.github.io/western-basin-worldbuilding/game/)
passed complete desktop/mobile playthroughs, both dispatch orders, report and
withhold outcomes, save/load, ending preservation, replay and native Tab/Enter.
Related Atlas routes resolve, with no page errors or document overflow. Live
scene screenshots were retained alongside local proofs. A documentation-only
checkpoint records this verified publication; no further game source changed.
Temporary browser scripts, screenshots and hash results remain in ignored
`temp/vesper-update/`; no generated build or new binary asset is tracked.

## Changed paths

- `game/index.html`
- `src/main.ts`
- `src/style.css`
- `src/game/data.ts`
- `src/game/engine.ts`
- `src/game/renderer.ts`
- `src/game/engine.test.ts`
- `src/atlas/main.ts` (Updates entry)
- `DESIGN.md`
- `README.md`
- `PROJECT_STATUS.md`
- `reports/README.md`
- `reports/current_phase_handoff.md`
- `reports/vesper_station_update_2026-10-04.md`

No files were deleted or archived. The separate local `Glasspunk_Vesper` source
copy was inspected but not edited; the Atlas-hosted repository is the target.
