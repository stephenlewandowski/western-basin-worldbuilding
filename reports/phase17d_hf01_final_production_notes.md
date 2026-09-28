# Phase 17D HF-01 — final production notes

**Status (2026-09-28):** Accepted HF-01 production set and Phase 17D style calibration in the Vite Atlas build. The follow-on HF-04 instruction establishes this acceptance; no further visual changes were requested. The accepted direction is **C — Glasspunk Promotional Hero**, with treatment #3 as the art-direction reference. This set remains S/K development material and creates no canon. GitHub Pages publication still depends on the site's manual deployment workflow.

## Delivery and provenance

| Final asset | Display pixels | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `assets/phase17d/hf01/hf01_glass_city_2075_hero_wide.webp` | 2400 × 1350 | 691,950 | `88baa48bd8fb2385708300618507b9fcb8129c2cacbd45df79c1508c46503df9` |
| `assets/phase17d/hf01/hf01_glass_city_2075_maintenance.webp` | 1600 × 1200 | 503,536 | `0facdeed739eb15217cb3f711d3af5d8191c24ce92e7e9a358e0c9183314d2f2` |
| `assets/phase17d/hf01/hf01_canopy_old_wall_section.svg` | 1440 × 900 viewBox | 7,832 | `e7c4f08a9ec4dda3c1ec2aa2833ac2d97790bd60cd96c9fa2df2ef080b77e99d` |

The user-supplied approved reference image, `ChatGPT Image Sep 27, 2026, 08_49_59 PM.png` (1448 × 1086), has SHA-256 `de3e9e54e3c9a358b340ff8bc88f98bd3d43da76bd1d165025b21687bab58fa9`. It governed the old-brick/canopy/repair material language; it is not a final site file. The wide and maintenance views were produced as **separate image-generation compositions** using the built-in image generator. Their retained source PNGs are `exec-a4796e26-2f8b-4a8b-ab49-0b48ec325a87.png` (1672 × 941; SHA-256 `e221fb86615ece7ec909a47369765492077aea440396ea9abad6a8082b99e9d0`) and `exec-51fceded-84a4-4806-98d9-4ec90f75de6c.png` (1448 × 1086; SHA-256 `6b5e066a62fc4088dddecb4f1a953df3925dd8ea0bd1852010d4403b40593c3d`). The PNGs remain in the production host's Codex generated-images store; they are not extra repository deliveries.

The generation brief for the wide called for a low, pedestrian-adjacent 16:9 view of the **same Toledo-derived composite street and optical-canopy invention**: a strong branching leaf silhouette above aged brick, human-guided suspended cassette, visible legacy rail and service ribs, bounded freight, public passage, property edge, river/port depth, and storm-break light on wet surfaces. Keep generic infrastructure and no baked text, neon, seamless dome, autonomous repair, mapped parcel, or performance implication. The maintenance brief used the approved reference and wide candidate to make a **distinct 4:3 repair-height view**, with workers, hoist, thick cassette edge and attachment berth, old/new joints, wear, service access, and the same public/freight/river context. The five accepted canopy refinements govern both: directional leaf families, thick cassette edges, repeatable attachment shoes, walkable service ribs tied to legacy rail, and visibly different panel generations. Generation is not pixel-deterministic from prose; the SHA-identified source PNGs are required to reproduce the exact final pixels.

`src/python/phase17d/build_hf01_glass_city_hero.py` and `build_hf01_glass_city_maintenance.py` reproducibly crop/resize those separate source images, convert to RGB, and encode WebP at quality 88 and 86 respectively. Run each with `--source <source-png>`; optional focal and quality flags are documented in `--help`. `build_hf01_canopy_section.py` regenerates the qualitative SVG. No physical dimensions are inferred from image pixel sizes.

## Visual and claim decisions

The wide pairs the replacement action and aged brick on the left with a repeated translucent arcade, wet street, freight edge, and generic waterfront depth. It keeps open sky on the right for responsive display. The maintenance view moves onto the service rib so worker-guided handling and cassette interface lead, while the street remains visible below. The inset gives the older wall, replaceable glazing, attachment, service rib, separate electrical/data routes, public route, and unconnected neighbor an explanatory reading order. It is a relationship diagram, not an engineered section.

**Required public caption:** “Composite Toledo-derived 2075 scenario / K architectural form.” The inherited Toledo/Western Basin industrial and systems context is E; possible adaptation relationships are S; this canopy, street arrangement, repair sequence, and ordinary activities are K. The scene is not a built project or surveyed view. Structural capacity, optical or cooling performance, bird safety, property agreements, affordability, and adoption remain unresolved. The depicted lift is not an engineered work instruction.

## Site and review gate

The local build adds `/atlas/glass-city-2075/`, features HF-01 on the home page, and records the milestone at `/updates/`. Methods, roadmap, the Toledo Crib study, and Phase 17D source reports remain cross-linked. At this HF-01 checkpoint, HF-04 has no image or route. The selected images were inspected at full size and at 900, 560, and 390 pixel wide 16:9 presentations; the canopy, worker, and cassette remain legible at card scale. The accepted set is the visual and production calibration for HF-04.

Validation and protected-artifact audit results are recorded in the current phase handoff after the final checks. The Vite site uses manual GitHub Pages publication; a local build or later push alone does not prove live deployment.
