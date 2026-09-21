# Prototype 2.1 — From Field to Lake — Animation Validation Report

- Prototype: 2.1 (Phase 17A), animation
- Date: 2026-09-21
- Result: **PASS**
- Checks passed: 35 / 35

## Canonical video

- 1920 x 1080, 30 fps, 32.0 s, 960 frames, H.264 (libx264 expectation), no audio.
- Transition behavior: linear fade, linear crossfade, static hold only.
- No particles, travel pulses, camera movement, zoom, motion blur, or
  quantitative animation.

## Checks

- [x] 21 A0-A5 keyframes exist
- [x] 6 all keyframes are 1920x1080 — {'A0': (1920, 1080), 'A1': (1920, 1080), 'A2': (1920, 1080), 'A3': (1920, 1080), 'A4': (1920, 1080), 'A5': (1920, 1080)}
- [x] 1 exact states A0-A5 present in order — ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
- [x] 2 timeline begins at 0.0 — 0.0
- [x] 3 timeline ends at 32.0 — 32.0
- [x] 4 no state gaps/overlaps (contiguous boundaries)
- [x] 5 end_seconds strictly greater than start_seconds per state
- [x] 7 30 fps declared in source manifest
- [x] 8 960 frames expected (32.0 s * 30 fps)
- [x] 9 canvas 1920x1080 declared
- [x] 10 epistemic status E throughout
- [x] 11 quantitative_encoding=false throughout
- [x] 12 randomization=false
- [x] 13 source manifest declares no_new_science=true
- [x] 14 no Great Black Swamp geometry
- [x] 15 no Toledo physical intake geometry
- [x] 16 HAB_context not a constituent
- [x] 17 no unsupported release process
- [x] 18 no deterministic nutrient->HAB edge
- [x] 19 equal-size constituent presence glyph semantics preserved
- [x] 20 A4 uses one shared convergence junction
- [x] 21 one outgoing relationship from junction
- [x] 22 persistent explanatory footer declared
- [x] 20 reduced-motion endpoint exists
- [x] 22 MP4 exists
- [x] 23 MP4 duration approximately 32.0 s — 32.0000s
- [x] 24 MP4 frame count = 960 — nb_frames=960
- [x] 25 MP4 resolution = 1920x1080 — 1920x1080
- [x] 26 MP4 has no audio stream — 0 audio stream(s)
- [x] MP4 video codec is H.264 (libx264 expectation) — h264
- [x] 27 state/source figure mapping consistent
- [x] 28 source & state manifests present
- [x] accepted static source manifest present (unchanged reference)
- [x] 29 no Phase 1-16 protected frozen artifact modified — 0 protected path(s): []
- [x] accepted static Python validator still passes — === RESULT: PASS (29/29 passed) ===

## Qualitative-only scope

- All animation states are E (Evidence / Model), qualitative-only.
- No quantity, velocity, travel time, probability, or severity is encoded.
- No deterministic nutrient → HAB edge; receiving-water conditions remain
  a distinct process domain.

## Frozen-artifact boundary

- No Phase 1-16 protected/frozen artifact was modified.
- Accepted static Prototype 2.1 figures are unchanged; they are the
  immutable visual sources for the animation.