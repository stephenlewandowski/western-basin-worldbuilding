# Erie Drift

**5 October 2026 · playable browser prototype · provisional 2075 fiction**

A relaxed Lake Erie fishing adventure: find a productive drift, feel for a bite,
land a fish, then decide whether to stay or move. One borrowed boat, seven regular species,
six familiar grounds and a shared supper at the landing give the outing a beginning and
an end. [Play the browser prototype](https://stephenlewandowski.github.io/western-basin-worldbuilding/erie-drift/).
The user authorized GitHub Pages publication on 5 October 2026.

Run `npm run dev` and open `/western-basin-worldbuilding/erie-drift/` on the printed
server. The current local preview uses port 4175. Production builds include the
same route alongside the existing Atlas and Vesper Station.

## Scene card

- **Place/season:** schematic western Lake Erie, late spring, summer or early
  autumn 2075. Real place names anchor invented depths and compressed travel.
  Maumee Bay Marina and East Harbor State Park Marina offer western/eastern
  departures. The latter sits on West Harbor. No map point is a navigation aid.
- **People/want:** the player has borrowed *Little Else*, a patched-up electric
  fishing boat, and promised fish for supper. Companion Jo has sandwiches and
  backup beans. This provisional Jo establishes no identity with other Atlas
  characters of the same name.
- **Spatial choice:** choose the inner, middle or outer starting lane. Wind
  carries the boat across the displayed school. Lane alignment and fishing
  depth affect bite timing. Boat positioning is a simple three-lane choice;
  this first version does not implement free steering.
- **Encounter:** catch or miss a fish, keep or release it, try another ground or
  go home. Eight used drifts bound the outing; the basket holds three fish.
  These are household/game limits, not current or predicted fishing regulations.
- **Image beats:** a chart and little boat; a rod over painted summer water;
  a distinctive fish in the net, followed by supper.
- **Return hook:** Jo makes ordinary trouble out of the lemon and invites the
  neighboring boat. The supper happens even with an empty basket.

## Playing

Choose a marina, season and sky: clear, broken cloud or overcast. Wind changes
drift speed; cloud and season affect the solar top-up. These are authored presets,
not actual daily weather. One scenic panorama is shared across grounds, with
subtle sky/season tinting; it does not depict the selected ground literally.

1. Push off; choose Maumee Bay, Toledo Intake, Niagara Reef, South Bass,
   Kelleys Island or East Harbor. The chart and buttons show accessibility.
2. Fit a bottom spreader, drift jig, spinner harness or light float. Pick
   compatible minnows, nightcrawlers or soft plastic. Read the sounder, adjust
   depth and choose a starting lane. A rig suggests a useful initial depth.
3. Drift through the echoes and strike at the bite. Habitat, bait and tackle
   affect the catch mix: perch, walleye, smallmouth, bluegill, freshwater drum
   (sheepshead), white perch and round goby. The sounder does not identify species.
4. Reel while the fish rests; ease when it pulls. Larger fighting types pull
   harder. Relaxed timing forgives handling mistakes; standard mode can lose fish.
5. Keep or release native catches; log invasive encounters for the fictional
   dock team. Try another drift, change grounds or head back for supper.

### Charge and range

The battery starts at 100. Travel costs are rounded schematic distance × 0.085;
these are game-budget points, not kilometres, fuel volumes or kilowatt-hours.
The game reserves enough charge to return to the departure marina and disables
trips that would spend it. Returning spends that reserve once. Starting marina
therefore matters, and repeated ground changes have a cost.

Solar adds at most four charge points per drift, accruing only during active
drifting at 0.1 points/second × season × sky factors. Summer/late spring/early
autumn factors are 1/0.72/0.48; clear/broken/overcast are 1/0.55/0.15. No charge
accrues in menus, paused play, held bite prompts or fights. No waiting/refill
exploit or real boat range claim is intended.

### Catch journal and score

Only the best fish of each species contributes: 50 points + length in cm ×
species factor (perch/white perch 5; walleye/drum/snakehead 3; smallmouth 4;
bluegill 6; goby 8). Smaller species remain worth finding. Kept, released and
logged fish score equally. Eight drifts and three supper places still bound the
outing; scoring does not change its human ending or require filling the basket.

An optional, off-by-default **speculative 2075 snakehead introduction** adds a
bay encounter. The source record does not establish a current Lake Erie
population. Catch text repeats that distinction. A new outing disables it again.

Relaxed timing is on by default: the bite waits for a response, and tight/slack
line is forgiven. Standard mode has a five-second bite window and recoverable
losses from sustained tight or slack line. Empty drifts give depth feedback.
No account, persistent save, live data service or remote audio/font dependencies.

All essential controls are native buttons, radios, checkbox settings and a depth
slider. On the focusable lake canvas: Space casts/strikes/toggles reel/ease; P
pauses; left/right choose a starting lane before casting. Map clicks duplicate
the nearby ground buttons. Pause is available beside the view and current action.
Hidden tabs pause automatically. Reduced motion is respected and can be selected
manually; optional sounds duplicate text/visual feedback. A fresh outing clears
the basket, score, charge, journal, visited grounds and used drifts while retaining the player's
accessibility preferences.

## Real principles and authored rules

The expanded [place, forum-lore and species source record](erie_drift_sources.md)
separates present-day anchors, angler anecdotes and future inventions.

Ohio DNR describes mobile walleye at varying depths, often favoring lower light,
and yellow perch commonly near the bottom with subtle bites. We use those broad
differences, not a calibrated ecology or angling-success model.

- [Ohio DNR, Lake Erie fishing guide, Tips and Techniques, p. 5](https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/wildlife/fishing/Pub5276_LakeErieFishingGuide_Web.pdf):
  consulted 5 October 2026 for behavioral/technique context only. Historical
  regulatory text in that guide is not used as current law or future law.
- [Working coast](../atlas/lake-erie-energy-security-coast-2075/index.html),
  [climate study](../atlas/climate-thermal-regime/index.html) and
  [coast evidence record](../reports/lake_erie_coast_context_2026-10-04.md) supply
  the broader regional setting.

Sonar echoes expose the game’s fish layer; they do not identify the species.
The simplified depth/lane hints are more certain than a real instrument.
Fish length varies with a seeded generator for replay. Catch timing,
species availability, depths, lanes, fighting cycles, basket and outing length
are game rules. They neither use nor modify Model Lab, Waterville or climate
projection outputs. No forecast of 2075 stocks, conditions, catch safety or
future jurisdiction is established. Existing scientific products and canon remain
unchanged.

## Implementation and art

The bounded game uses the existing TypeScript/Vite/Canvas stack. That keeps the
new route small, shares the project's build/test setup and retains native browser
controls. No Godot runtime/export or engine installation is needed for this
version. The simulation is isolated in [logic.ts](../src/erie-drift/logic.ts),
and the [place/species/tackle catalog](../src/erie-drift/content.ts),
with [rendering](../src/erie-drift/render.ts), [interaction](../src/erie-drift/main.ts)
and [styles](../src/erie-drift/style.css) kept separate.

One new [lake backdrop](../assets/erie-drift/README.md) uses the built-in imagegen
tool; its full prompt and master/derivative hashes are retained. Canvas draws the
map, little boat, fish, rod and instruments. No accepted illustration is replaced.
Short optional sounds are synthesized locally with Web Audio.

## First play questions

Can a new player tell where to set up a drift? Is waiting for a bite pleasurable?
Does switching between reeling and easing feel clear? Do bait, place and charge
create enjoyable choices without slowing the outing? Do players want another
outing or a different part of the lake?
Observed player interest, rather than agent impressions, should guide additional
grounds, boat customization or a longer campaign.

[Implementation and verification](../reports/erie_drift_implementation_2026-10-05.md).
