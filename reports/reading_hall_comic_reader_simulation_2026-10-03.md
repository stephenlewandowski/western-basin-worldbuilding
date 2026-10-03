# Reading Hall comic and reader simulation

**3 October 2026 · creative checkpoint.** Starting main: `26224cb`.

The useful invitation is a person with somewhere to go, an unfinished question,
and a future place whose upkeep is visible. Keep developing this: the existing
science now supports a compact scene without being delivered as a lecture.
This is encouraging prototype feedback, not evidence of an established audience.

## Products and continuity

- [Six-panel comic](https://stephenlewandowski.github.io/western-basin-worldbuilding/stories/before-the-last-bus/),
  [full page](../assets/phase17d/hf05/comic/before_the_last_bus.webp),
  [script/grounding](../stories/before_the_last_bus.md) and playable companion.
- User-selected Composition A is the canonical visual orientation. The
  [continuity lock](../docs/phase_briefs/hf05_reading_hall_continuity_lock.md) and
  [editable plan](../assets/phase17d/hf05/hf05_orientation_a_continuity.svg) fix the
  counter front-left, public floor middle, ascending spine right, field return and
  custody left-rear, rear service gallery and separate tall-end compute/preservation.
  The single ground berth moves from the earlier low/middle sketch to the tall end
  to match A. Original brief, spatial study and A/B/C images remain intact.
- Six consistent comic panels show a picnic question, partial coverage, field
  return, a repair, a private address handoff and a bus ride. No invented number
  supplies an instant answer. Lettering is short enough for a compact reading;
  no human reading duration has been measured.
- Built-in image generation produced the artwork; Sharp only encoded WebP and
  extracted panels for desktop pairs/mobile single-column reading. Exact original
  and edit prompts, source/output hashes and crop rectangles are in the
  [prompt](../assets/phase17d/hf05/comic/before_the_last_bus_prompt.json) and
  [manifest](../assets/phase17d/hf05/comic/before_the_last_bus_manifest.json).
  A text transcript and descriptive alt text carry the same dialogue.

## Small reader simulation

Three fresh agents received no project conversation or internal documents. Each
saw the same baseline comic, homepage, one futurescape and the playable encounter;
entry order varied. They answered the six requested questions before sharing any
responses. Agent identities: `reader_comic_first`, `reader_atlas_first`,
`reader_play_first`. Responses below are faithful condensations, with exact quotes
marked as quotations.

**Limits:** these are agent impressions, not human readers. They use the same model
family, and three responses cannot establish demand or format preference. All
visually inspected the comic bitmap; Atlas/story exposure used rendered DOM text,
image descriptions and button clicks, not the Atlas artwork. The comparison therefore
underrepresents the Atlas's visual appeal. All chose the private ending after all
three conversations, so this does not test the full range of player behavior.

| Entry order | Place inferred first | Most curiosity | Wanted next |
| --- | --- | --- | --- |
| Comic → Atlas → playable | River-information hall, part library/municipal water desk | Comic | Follow Renata's request; Industrial Metabolism |
| Atlas → comic → playable | Maintained Toledo/Lake Erie working region | Comic | Industrial Metabolism; Renata receiving an answer |
| Playable → comic → Atlas | Public library/information counter for neighborhood questions | Playable | Renata's return visit; Maumee Bio-Ag Landscape |

### Comic-first response

1. **Place:** a public river-information hall in Toledo, 2075; which Toledo was
   initially unclear until the Atlas anchored the Maumee/western Lake Erie region.
2. **Distinctive:** paper maps, an advanced instrument on an old trolley, and the
   daughter's paper sun. These made the future feel occupied by people with errands.
3. **Confusing:** what the visits measured, what the picnic question required,
   why the location was private, and the instrument repair's relation to that question.
4. **Human problem:** broad coverage does not answer a particular place's question;
   transport and another visit make clarification cost time.
5. **Another scene:** yes, follow the request and whether the picnic happens.
   Wanted **“Follow this request”** after the private ending; restart was available.
6. **Format:** comic. Deadline, paper sun and unfinished question supplied immediate
   stakes. Play added shirts/the green bowl, but endings felt like ways to leave
   with paperwork. Atlas language felt like an exhibition catalogue.

### Atlas-first response

1. **Place:** a future Toledo/Lake Erie working region shaped by inherited buildings,
   water, industry and public life; maintained rather than radically transformed.
2. **Distinctive:** repairs, freight, pedestrian passage and a property boundary share
   Glass City's roof/street. Mundane limits make the architecture feel inhabited.
3. **Confusing:** what makes the canopy optical, what it does beyond shade, why 2075
   changes daily life, and exactly which finding Renata read. Qualifications left
   the central attraction abstract.
4. **Human problem:** apply a broad finding to a daughter's picnic spot under a bus
   deadline, with limited geographic coverage and time for follow-up.
5. **Another scene:** yes, Industrial Metabolism's inherited crane hall and repair/
   material negotiations; also the answer Renata receives and tells her daughter.
6. **Format:** comic. The paper sun, cheap wheel and bus made the world tangible.
   Play gave character texture but choices mainly revealed passages.

### Playable-first response

1. **Place:** a future public library/counter where environmental findings meet
   neighborhood questions. Expected an ordinary civic encounter.
2. **Distinctive:** knowledge has physical upkeep. Folders, hatch, cabinets and wheel
   matter; shirts and the paper sun give Renata a life beyond the central question.
3. **Confusing:** privacy, what choices cost when every conversation is available,
   coverage less definite than the comic, and the optical canopy's benefit.
4. **Human problem:** a family decision needs clarification that competes with
   transport, work and parenting. A request number is no answer tonight.
5. **Another scene:** yes, the office's answer, whether Renata can get back, and what
   she tells her daughter. Wanted the upstream working landscape next.
6. **Format:** playable. Asking a question created curiosity about what Renata could
   accomplish. Comic made the room/sun immediate but its smile softened the cost;
   Atlas felt farther from individual stakes.

Bounded follow-up from this same reader: stay for a records check and miss the bus,
or leave with a scheduled next step. A missed errand should make the cost visible.
Payoff must settle coverage or supply a named person and definite action:
**“another ‘pending’ slip alone would feel like repetition.”** This is not a fourth reader.

## Changes driven by the responses

All three questioned privacy. The selected comic revision names the water report
and has Renata say **“Yes. Keep our address off the public copy.”** Play now explains
that same choice and states the sheet's missing coverage. The
[baseline shown to readers](../assets/phase17d/hf05/comic/before_the_last_bus_reader_baseline.webp)
is preserved with its hash; reported reactions belong to that baseline, not an
untested claim that the revision solved everything.

The homepage, Stories navigation, Reading Hall and Updates lead directly to the
comic, with play and nearby Atlas places as continuations. The comic introduces
Toledo/western Lake Erie plainly. Original futurescape copy/assets remain intact;
the optical-canopy confusion is an unresolved presentation task, not permission
to invent a technology benefit.

The [scene template](../docs/templates/scene_card.md) now calls for an immediate
want, visible continuity, a consequential playable action and one resolved question.
No timer, score, new framework or fictional performance metric was added.

## Next investment and worth

**Make [The Return Visit](../stories/the_return_visit.md)** as one small encounter
with a comic adaptation. Staying for Hannah competes with a bus and shirt handoff;
leaving preserves the errand. A revised scope card resolves coverage, while water
condition remains unknown. Give each path an observable consequence and a person/
action to follow. Avoid another chapter that ends only with administrative waiting.

The strongest recurring elements are the paper sun and ordinary livelihoods,
visible care of sophisticated equipment, versioned records one can handle, and
partial knowledge with a real cost. The comparison dock could later make method
differences playable, but it did not independently attract these readers yet.
Place still matters: readers wanted the crane hall and upstream farm landscape.
Use the Atlas as geography and spatial depth around people, rather than expanding
the catalogue ahead of encounters. A future-specific device should change what
someone can do; an ordinary municipal queue alone will not sustain this setting.

**Continue, at this scale.** It is productive when research becomes scenes and
reusable places; the finished comic is a concrete result. The next investment
should be one consequential sequel and a few actual human readers/players, not a
large game or more production scaffolding. If they cannot name a person, situation
or place they want back, fix the opening/payoff before expanding content.

The parallel scientific track remains Waterville observations and synthetic Model
Lab diagnostics, explicitly separate. The retained flow record already demonstrates
that distinction. Nutrient measurements, geographic crosswalks and empirical loads
can mature separately; future dashboard/story links must retain dates, units,
quality flags and observation/model boundaries. No acquisition or model change
was needed for this creative checkpoint.

## Validation and publication

- TypeScript check and production build pass (15 page entries); web tests pass **22/22**.
- **15 routes × 1440/390 widths**: 30 browser observations, no horizontal overflow,
  page errors or failed local requests; all internal URLs/assets return HTTP 200.
  37 distinct images decode with alt text; 26 repository source targets exist.
  Comic has six ordered panels, readable mobile lettering and a working transcript.
  All three conversations/endings, restart and keyboard activation pass.
- Final scoped layout/prose adjustment checked again on homepage/Hall at both widths.
- Relative Markdown links pass **461/461**, Markdown anchors **5/5**; whitespace
  checks pass and built files contain no local host/filesystem path leaks.
- Nine tracked comic/reference hashes plus two retained PNG-source hashes pass;
  continuity SVG parses. Dialogue/captions total 85 words including transcript
  speaker labels, before the short title/location line; no human timing claim.
- LFS integrity passes. **654 protected paths / 665 historical hash references** have
  no content drift or protected-path overlap. The 190 existing CRLF/LF reference
  differences normalize correctly. Original HF-05 brief/study/A/B/C, accepted model
  outputs/code/tests, observed Waterville products, older futurescape assets and
  historical archives remain unchanged. Existing worktrees remain untouched.

No files were removed. The old proposed comic beats were consolidated into the
published script card; the reader baseline is retained rather than silently replaced.
Ignored build, source PNGs and browser proofs remain local.

Remaining work: human response, genuinely consequential play, stronger explanation
of future devices through action, final architectural detail and empirical nutrient
input maturity. These are development priorities, not reasons to withhold this comic.

Publication: source commit `6bd1de12516cf5713b4f462971f89cef7d3fc159` is pushed to
main. [Pages run 37116017148](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37116017148)
completed successfully for that exact commit. Live homepage, comic, Hall and Methods
return HTTP 200; images decode at mobile width without overflow or page errors.
The published full comic matches the local WebP SHA-256. Transcript, privacy
conversation/private ending/restart and the retained Waterville display pass.
The following documentation-only commit records publication without changing the
deployed build. Git status is clean after that checkpoint is committed and pushed.


### Exact changed paths

```text
PROJECT_STATUS.md
README.md
assets/phase17d/hf05/comic/before_the_last_bus.webp
assets/phase17d/hf05/comic/before_the_last_bus_manifest.json
assets/phase17d/hf05/comic/before_the_last_bus_prompt.json
assets/phase17d/hf05/comic/before_the_last_bus_reader_baseline.webp
assets/phase17d/hf05/comic/panel_1.webp
assets/phase17d/hf05/comic/panel_2.webp
assets/phase17d/hf05/comic/panel_3.webp
assets/phase17d/hf05/comic/panel_4.webp
assets/phase17d/hf05/comic/panel_5.webp
assets/phase17d/hf05/comic/panel_6.webp
assets/phase17d/hf05/hf05_orientation_a_continuity.svg
docs/README.md
docs/canon_status.md
docs/phase_briefs/hf05_reading_hall_continuity_lock.md
docs/templates/scene_card.md
reports/README.md
reports/current_phase_handoff.md
reports/reading_hall_comic_reader_simulation_2026-10-03.md
src/atlas/comic.ts
src/atlas/main.ts
src/atlas/reading-hall.ts
src/atlas/style.css
stories/README.md
stories/before-the-last-bus/index.html
stories/before_the_last_bus.md
stories/the_return_visit.md
vite.config.ts
```
