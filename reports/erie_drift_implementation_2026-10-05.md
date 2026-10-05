# Erie Drift implementation

**5 October 2026 · browser prototype**

The user requested a lightweight walleye/perch fishing game on Lake Erie, with
Godot available if appropriate. Starting main was clean at
`9057b074e7af38829b5792c520e8538f569af2f6`, matching origin/main.
The initial build and user-requested expansion
add a complete small outing using the existing browser stack. The user authorized
commit, push and GitHub Pages publication on 5 October 2026. The game establishes
no new fictional canon.

## Delivered

- New `/erie-drift/` route, with native controls and Canvas map/fishing scenes.
- Six named grounds: Maumee Bay, Toledo Intake, Niagara Reef, South Bass,
  Kelleys Island and East Harbor; a newly drawn schematic map and two starting
  marinas. Local angler reports supply historical lore, not current catch advice.
- Battery budget, protected return charge, seasonal/cloud-dependent solar top-up.
  Travel has a cost; menus, pauses and held bite prompts cannot farm energy.
- Four tackle choices and three compatible bait types change mixed-catch weights.
  Perch, walleye, smallmouth, bluegill, sheepshead, white perch and round goby have
  separate journal entries and drawings. Optional snakehead is explicitly
  speculative 2075 fiction, off by default. Invasive catches are logged for a
  fictional dock team rather than given a keep/release choice.
- Best-catch-per-species scoring uses type and length. Keeping/releasing/logging
  earns equal points. Three starting seasons and three sky/wind presets.
  Standard and relaxed timing, tension/landing feedback, pause, hidden-tab
  pause, reduced motion and optional locally synthesized sound.
- Keep/release choices, bounded household basket, catch journal, eight used drifts,
  early return, three supper outcomes and complete restart.
- New painted lake asset; original map/boat/fish/rod/instrument drawings; source
  PNG archive, full prompt and hashes. Existing art remains intact.
- Discovery from the homepage, coast page and Updates. Root documentation and
  current handoff link to the browser prototype and its source record.

[Design, scene card and rules](../docs/erie_drift_design.md),
[place/species sources and boundaries](../docs/erie_drift_sources.md),
[artwork lineage](../assets/erie-drift/README.md).

## Validation

All **64 tests across nine files** pass, including 13 game-rule tests. Coverage
includes every rig on every ground, depth/lane effects, standard/relaxed handling,
pause/time jumps, basket limits, duplicate prevention, eight-drift closure,
return reserve across repeated travel, marina-dependent range, solar caps and
idle exploits, bait compatibility, mixed catches, score fairness and the explicit
snakehead gate. TypeScript and production build pass with 17 HTML routes.

Production-preview playthroughs pass at 1440, 390 and 320 px: starting marina, season/sky,
map click and ground buttons, native keyboard controls, tackle/bait, depth,
pause, bite focus, reeling/easing, catch disposition, score, eight-drift closure,
home and full reset. Desktop uses standard timing; phones use relaxed timing.
No horizontal page overflow or game runtime errors were found. Visual review
corrected fish-title overlap and made phase transitions redraw immediately,
including restart. The painted view and action controls stay adjacent on phones.

All 17 public route paths return 200 locally. Repository-relative Markdown links
pass (663), `git diff --check` passes and `git lfs fsck` passes. The new PNG master
and WebP match manifest hashes. 636 protected files / 645 freeze references match
the starting commit. Science, Model Lab, empirical records, Vesper, Hall continuity
and accepted artwork are untouched. The game JS is approximately 43.4 KB
(17.5 KB gzip), plus the existing new-game 290 KB WebP; no new runtime dependency.

Local development preview:
`http://127.0.0.1:4175/western-basin-worldbuilding/erie-drift/`.
Production preview uses the same route on port 4176.
This addition contains the 20 paths below. GitHub Pages publication uses the
repository's manually dispatched `deploy-pages.yml` workflow after pushing main.
The user responded positively to the first build and requested this expansion;
that is not a substitute for an uncoached playtest of the expanded controls.

## Changed paths

Added:

```text
erie-drift/index.html
src/erie-drift/logic.ts
src/erie-drift/content.ts
src/erie-drift/logic.test.ts
src/erie-drift/render.ts
src/erie-drift/main.ts
src/erie-drift/style.css
assets/erie-drift/lake-morning.webp
assets/erie-drift/source_png.zip
assets/erie-drift/manifest.json
assets/erie-drift/README.md
docs/erie_drift_design.md
docs/erie_drift_sources.md
reports/erie_drift_implementation_2026-10-05.md
```

Modified:

```text
vite.config.ts
src/atlas/main.ts
README.md
PROJECT_STATUS.md
reports/README.md
reports/current_phase_handoff.md
```

No removals. Browser proofs and packaging helpers are ignored under
`temp/erie-drift/`. No frozen, empirical, Model Lab, Vesper Station, Hall continuity
or accepted artwork path is modified.

## Remaining limits

One painted panorama supplies all six fishing views with subtle season/cloud
tints. It is shared scenic artwork, not six site-specific illustrations. The map
is intentionally schematic; positioning is by lane, not free steering. Sonar
provides unusually legible game hints, not species identification. Boat costs,
solar factors, fish lengths, catch weights and score factors are authored values,
not Model Lab outputs, observed conditions or a 2075 stock forecast.

The next useful test is whether players understand the reserved charge, find
switching tackle rewarding and enjoy mixed catches without the menus slowing
the day. Tune those choices before adding a shop, economy or campaign. More
distinctive ground-specific horizon art could follow observed player interest.
