# Glasspunk: Blackout at Vesper Station

[Vesper Station](game/index.html) is a small CGA-style browser mystery: one
night shift, two repairs, five rooms. It takes place at a fictional district
service station on Toledo’s river/industrial edge in 2075. A first play is
intended to fit roughly 10–15 minutes; this is a design target, not a measured
audience result. The game remains experimental fiction and establishes no Atlas
canon.

## Scene card

- **Place:** a composite Maumee river edge, with glass roofs, gantries, a bridge,
  reeds and a heron. Interior routes stay fixed: Control Room ↔ Corridor ↔
  Furnace Gallery; Corridor ↔ Pump House ↔ River Terrace.
- **People:** Mara wants a reliable morning handoff and a hot coffee. Niko wants
  to get home without leaving the next shift a hidden problem.
- **Spatial invention:** a removable heat exchanger and protected circulation
  loop connect the process hall to district heat. Its return wheel is awkward;
  Niko’s existing glove finally earns its place in inventory.
- **Choice:** arrange the local dispatch queue. At the final handoff, send the
  dated maintenance observations to the Reading Hall first and defer a flexible
  roof render, or finish the render and queue the observations for morning.
  Cooling remains supplied in both branches. The queue order may change before
  filing; replay explicitly returns to that moment.
- **Image beats:** dead equipment and Mara’s mug; gloved work on a labeled loop;
  first light over the river and a completed handoff.
- **Returning hook:** Niko’s roof-as-jellyfish joke, the good mug, a record that
  can be questioned later. This shift resolves its two repairs.

## Player loop

1. Read the shift log in the control room; Mara gives the locker key.
2. Find the ceramic fuse and breaker note in the corridor. Explore the furnace
   tag/scorch mark and speak to Niko about an altered log entry.
3. Select the fuse and inspect the console. A wrong tool produces a recoverable
   response; there is no timer or resource attrition.
4. Follow the newly powered corridor door to the pump house. Read its loop
   card, select the glove from the furnace service tag, open RETURN, then start
   the pump. The interlock makes the order visible.
5. Explore the river terrace and basin route board. Read the dispatch slip and
   prepare either queue order.
6. Return to the control-room Case Review terminal. Choose an explanation and
   cite two supporting items, report it, withhold your explanation, or postpone
   to explore further. Reporting and withholding both complete the service
   handoff; the maintenance observations are separate from the cause claim.
7. Read the ending in Shift Notes. Replay the handoff with repairs/notes retained,
   or restart for a fresh shift.

The inherited case-review scores are hand-authored fictional puzzle rules, not
probabilities, causal inference or Model Lab output. Assessment covers the cited
items; readers are warned that uncited clues may disagree. Future improvements
should distinguish testimony and actions from cause evidence more carefully
before expanding the mystery.

## Grounding and limits

The [industrial futurescape](atlas/industrial-metabolism-2075/index.html)
supplies repairable process spaces and qualified heat exchange; the
[Reading Hall](atlas/basin-reading-hall/index.html) supplies dated records and
a distinction between observation and explanation. The
[maps](maps/index.html) supply regional character.

The thermal principle is simple: heat must move through a defined path, and
circulation needs a return. Flexible computing and essential service loads have
different scheduling needs. These are qualitative ideas enacted through a toy
puzzle. Station geometry, control sequences, institutions, failure cause and
characters are invented; this is neither a real plant control procedure nor an
engineering or energy-performance model. No factual baseline was changed.

## Presentation and controls

320×200 logical canvas, backed at 2× for legible type and scaled with pixelated
rendering. Black, cyan, magenta and white remain the palette. Region silhouettes,
chunky workers, a visible tag/glove and bright equipment states add context
without external art dependencies. Local pipe/floor seams replace the corridor’s
full-width horizontal stripes.

All essential actions have native buttons, including both conversations,
inventory, queue choices and case review. On the canvas: arrows/WASD select a
hotspot; Enter/Space inspects; I cycles inventory; H gives a current hint; Y/N
answer Niko; F requests Case Review; Escape clears selection; R restarts.
Tab retains native page navigation. Full dialogue and endings appear in Shift
Notes, with nearby feedback on narrow screens. The placeholder Mute button was
removed; this version has no audio.

SAVE/LOAD use the existing local storage key. Invalid identifiers are rejected
or filtered; denied storage fails safely. Earlier saves retain their notes and
acquire service defaults. An old review-screen save returns to the unfinished
handoff, with its case selections preserved. Old ending saves remain readable
and can replay the handoff.

## Implementation

- [Room/content definitions](src/game/data.ts).
- [Pure case and inventory rules](src/game/logic.ts).
- [State, progression and save migration](src/game/engine.ts).
- [Canvas scenes](src/game/renderer.ts) and [review hit targets](src/game/review.ts).
- [Pointer/keyboard/native controls](src/main.ts) and [layout](src/style.css).
- [State tests](src/game/engine.test.ts).
- [Development and publication record](reports/vesper_station_update_2026-10-04.md).

Run `npm test` and `npm run build`. A bounded browser playthrough checks
reachability, both dispatch consequences, input, persistence and legibility.
These checks are not evidence of human enjoyment; get a few first-time players’
responses before investing in a longer chapter.
