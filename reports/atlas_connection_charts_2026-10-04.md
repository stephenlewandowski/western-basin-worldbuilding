# Readable web connection charts

4 October 2026. Starting main: `dd7b340`.

The author approved the illustrated maps and architectural sketches, then clarified
that networks and flowcharts should remain diagrams. Tables and lists alone had
removed a useful way to understand connections. This revision restores that view
as web components, with readable HTML cards and a dynamically rendered connector
layer. Original SVG/PNG source files are preserved; no new static diagram image
or graph-library dependency is required.

## Reader interface

Nine charts across four studies:

- Field to Lake: generalized water route, constituent/process membership,
  receiving-water interaction.
- Farm: water/reuse/decisions, operating lanes and cross-lane dependencies.
- Industrial Exchange: selected exchanges, thermal/material qualification,
  open-system coordination and outward interfaces.
- Intake Crib: persistence, modification and imagined additions.

The related farm and crane-hall futurescapes also expose their study charts,
without presenting a synthetic district as the literal pictured building.
Tables, prose, research maps, architectural sketches and earlier source links stay
available as complementary readings.

Charts retain natural-size card labels inside a bounded scroll area. Readers can
swipe, use native scrolling/keyboard navigation, drag empty space with a mouse,
zoom between 75–150%, reset the view and find a card by name. Selecting a card
highlights adjacent connections; selecting a line or its equivalent native menu
shows the endpoints, connection kind and explanation. Endpoint buttons navigate
to either part. Connection-kind controls highlight a layer without deleting the
remaining network. Native menus provide keyboard alternatives to pointer lines.
Simple diagrams use a shorter viewport; large networks scroll in both directions.

## Source fidelity and limits

Definitions live in [connection-data.ts](../src/atlas/connection-data.ts), sourced
from the retained study builders, industrial semantic manifest and constituent
CSV. Every chart includes its source link and limit. Layout coordinates are
editorial; constant line width provides no quantity. Information, dependencies,
physical movement, possible exchanges, context, reading sequence and membership
are distinct meanings. Highlighting communicates selection, not flow magnitude.

The field chart supplies no invented discharge pipe, mandatory retention node or
direct nutrient-to-bloom edge. Constituent connections exactly match the retained
matrix; missing membership means not represented in the source. The farm's
record/decision/maintenance layer is separate from water movement. Its assembly
plate is a spatial blockout, so no invented directed assembly network is supplied.

Both industrial reuse routes pass through qualification. Outside handling remains
possible at every stage. Older drawing geometry has two ambiguities: its final
maintenance arrow conflicts with the semantic registry, and its simplified open
district arrow bypasses qualification. This derivative follows the registry's
maintenance-to-collective-core meaning and the gated qualification narrative;
it does not invent per-facility maintenance links or repeat unlabeled shortcuts.
Accepted source products remain unchanged. The crib arrows are an interpretation
sequence, never water/material flow.

No mathematical Model Lab changes, empirical loads, calibrated predictions or
new fictional canon are introduced. Frozen products, original figures, artwork
masters, Reading Hall work and observations are preserved. The comic remains
withdrawn after failed human-author continuity review; both encounters remain.

## Changed paths

- New `src/atlas/connection-data.ts`, `connection-data.test.ts`,
  `connection-charts.ts`; modified `src/atlas/main.ts`, `style.css`.
- `README.md`, `PROJECT_STATUS.md`, `docs/templates/scene_card.md`,
  `reports/README.md`, `reports/current_phase_handoff.md`,
  `reports/atlas_visual_refresh_2026-10-04.md`, this report.

No tracked files removed. Preparation and browser records stay in ignored
`temp/connection-charts/`.

## Validation and publication

- TypeScript and production build pass; 30 web tests pass, including exact
  constituent/process membership, valid graph endpoints, receiving-water
  interaction and qualification that cannot be bypassed.
- Browser checks cover all nine charts on six routes at 1440 and 390 pixels
  (28 chart observations). No page overflow, clipped cards or script errors.
  Card/edge menus, endpoint navigation, type highlighting, zoom bounds/reset,
  keyboard scrolling and mouse dragging pass. Desktop/mobile layouts inspected.
- Markdown links pass (502 links); `git diff --check` and LFS integrity pass.
- All 654 protected paths and active Reading Hall originals match their baseline;
  665 historical references match after documented LF normalization. No changed
  paths overlap `outputs`, `data`, scientific Python/R, original assets or stories.
  Existing worktrees remain untouched. Model Lab tests need no rerun because
  its code, mathematics, inputs and outputs are unchanged.

Verified live publication will be recorded after deployment.
