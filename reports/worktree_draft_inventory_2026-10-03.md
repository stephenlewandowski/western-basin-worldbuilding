# Worktree draft inventory — 3 October 2026

Seven registered worktrees were inspected, including untracked drafts and ignored
creative sources. No branch, checkout, source file or ignored reference was removed.

| Worktree | Finding | Disposition |
| --- | --- | --- |
| Main | Active cleanup and Reading Hall sources | Cleanup integrated as `6c6ed91`; continue current development |
| `phase17c-ordinary-day-tests` | Six ordinary-day stories and review; 39,819 bytes | Preserve; use as provisional fiction workshop sources |
| `phase17d-hf01-art-direction` | Two art-direction/handoff records; 29,897 bytes | Preserve as history; superseded task restrictions are historical |
| `phase17d-hf01-glass-city` | Hero, section, two builders and notes; 228,745 bytes | Preserve together as a superseded procedural blockout |
| `phase17d-futurist-synthesis` | Clean; no unique commits | Keep until worktree retirement is separately requested |
| `phase17d-hf02-final-production` | Clean tracked tree; six ignored inset alternatives/previews, 337,156 bytes | Preserve visual alternatives; public style C already has a published descendant |
| External `western-basin-phase2a` | Clean; unique historical commit `b034160` | Preserve commit/branch; do not restore its stale scientific package |

The five creative branches contain no commits absent from main. Their unique
extra work is untracked or ignored. The external Phase 2A commit was selectively
integrated, as [materials QA](materials_system_qa.md) records. All seventeen
introduced scientific paths survive in main; later builder/source/QA differences
are useful progress, not a reason to cherry-pick the old commit or GeoPackage.

## Durable preservation

The [archive](../docs/archive/worktree_drafts_2026-10-03.zip) contains **twenty files**:
fourteen untracked drafts plus six ignored inset studies, **635,617 original bytes**.
The [manifest](../docs/archive/worktree_drafts_2026-10-03_manifest.json) supplies every
file path, size, exact-byte SHA-256 and archive entry. Every extracted payload was
checked against its source hash. Worktree originals remain in place.

The fourteen draft paths, relative to their source worktrees:

```text
phase17c-ordinary-day-tests:
  drafts/phase17c/ordinary_day_tests/01_nadine.md
  drafts/phase17c/ordinary_day_tests/02_dale.md
  drafts/phase17c/ordinary_day_tests/03_adam.md
  drafts/phase17c/ordinary_day_tests/04_renata.md
  drafts/phase17c/ordinary_day_tests/05_hannah.md
  drafts/phase17c/ordinary_day_tests/06_wendell.md
  drafts/phase17c/ordinary_day_tests/REVIEW.md
phase17d-hf01-art-direction:
  reports/phase17d_hf01_art_direction_studies.md
  reports/phase17d_hf01_image_generation_handoff.md
phase17d-hf01-glass-city:
  assets/phase17d/hf01/hf01_canopy_section.svg
  assets/phase17d/hf01/hf01_glass_city_2075.webp
  reports/phase17d_hf01_prototype_notes.md
  src/python/phase17d/build_hf01_canopy_section.py
  src/python/phase17d/build_hf01_glass_city.py
```

The six additional HF-02 files are under
`temp/phase17d-hf02-inset-style/` in its worktree. A and B are useful alternate
visual approaches; C differs from the published SVG only in its title. They
remain historical options, not extra public insets.

## Valuable ignored material left in place

| Material | Repository-relative path | Bytes / SHA-256 |
| --- | --- | --- |
| Approved coast reference | `temp/phase17d-hf02-reference/hf02_b-l1_approved_reference.png` | 3,443,564 / `a63d05cc83d1a094b87b42098c7c27f845170f13db753187efb85919f8a56dd7` |
| Approved farm reference | `temp/phase17d-hf03-reference/hf03_c-l1_approved_reference.png` | 3,036,570 / `4b0d76b91781bf73834a2ba93d18657b1796dc75e828bcc3c3cc4d8ca789a952` |
| Accepted field-to-lake animation | `outputs/atlas/prototypes/2_1_from_field_to_lake/animation/2_1_from_field_to_lake_animation.mp4` | 1,889,394 / `2d4844ffc7f96b4000d88e21554eb100b470fc5f1358f94006449065ce77843a` |

These already have committed provenance or delivery records. They are not junk
and are not added to ordinary Git by this pass. Current Reading Hall PNG sources,
Model Lab screenshots and cleanup proofs also remain local. Other inspected
ignored worktree files were caches, with no additional unique prose/science drafts.

## Creative use

Renata and Hannah provide the strongest bridge into the Reading Hall. Their
ordinary-day scenes supply the transit card, resale shirts, paper sun, field
handoff and disputed green bowl used in [Before the Last Bus](../stories/before_the_last_bus.md).
The new encounter remains fiction. Hannah’s original opening repeats a sentence;
keep the archived original and correct it only in a reading adaptation.
