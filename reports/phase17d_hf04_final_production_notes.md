# Phase 17D HF-04 — final production notes

**Status (2026-09-28):** Local HF-04 Industrial Metabolism 2075 public hero set and Atlas integration, prepared against the accepted HF-01 Glass City visual/production calibration. The scene remains a composite S/K proposition, not a real facility, certified process, or new canon. GitHub Pages deployment is a separate manual workflow.

## Final set and provenance

| Final asset | Display pixels | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `assets/phase17d/hf04/hf04_industrial_metabolism_2075_hero_wide.webp` | 2400 × 1350 | 592,934 | `507880ef971ddc75c1953478952d64ed4dd4f617d9feb972ddbd662b26f4f317` |
| `assets/phase17d/hf04/hf04_industrial_metabolism_2075_maintenance.webp` | 1600 × 1200 | 367,148 | `efeaf343fbb8465186ddc063475a8728547c9841ec33cdc41ea13029f0590422` |
| `assets/phase17d/hf04/hf04_qualification_cell_section.svg` | 1440 × 900 viewBox | 8,596 | `4ff46aa486c58208c5a817c32b2c9f99bf62383355a57bde770beb0b553fdfc8` |

Both raster views were produced with the built-in image generator as **separate compositions**. The accepted HF-01 hero was the wide view's style reference for material, light, human scale, and editorial restraint; its optical canopy and street layout were excluded. The selected wide source is `exec-05199719-5c9f-4ccd-b53e-9fd20e0cc30a.png` (1672 × 941, SHA-256 `8266bb06d36b4b158f79139c7bc7f61a2c88859895dc16a10dea3306eac0dbda`). The selected maintenance source is `exec-5390f23e-6242-40ab-95a6-e751ac1ded15.png` (1448 × 1086, SHA-256 `d5822a417fc587c30578c6e57a13445f39dc3ca3ea7cf9a1ec0388833a74ab51`). Source PNGs remain in the production host's Codex generated-images store, outside the repository; their hashes identify the exact inputs. A less focused maintenance candidate was not selected or delivered.

The wide generation direction specified a low worker-height view through an **old soot-dark brick crane hall** toward a cooler freight yard. An old crane lifts one opaque replaceable cell beside a tall multi-level exchange frontage. Protected optical qualification, accessible heat/water valves, segregated material stores, human-guided rigging, a staffed acceptance point, and bounded robotic handoff occupy separate spaces. Dusty shafts of daylight, scarred steel, patched wet concrete, rail cars, and conventional freight establish age and outside dependencies. No named plant, readable text, exact process, mystery glow, seamless automation, or automatic material conversion was requested. The maintenance direction moved much closer to a worn coupling and empty berth; the cell edge, two riggers, a checking technician, and a quality worker with a red hold tag remain in the same hall. The image-generation prompts document revision intent; generation itself is not pixel-deterministic. Reproducing these exact WebPs requires the SHA-identified source PNGs.

`src/python/phase17d/build_hf04_industrial_metabolism_hero.py` and `build_hf04_industrial_metabolism_maintenance.py` use the shared Phase 17D WebP packager for deterministic crop, RGB conversion, 2400 × 1350 / 1600 × 1200 sizing, quality 88 / 86, and decode verification. Each accepts `--source <source-png>` and optional focal/quality flags. `build_hf04_qualification_cell_section.py` reproduces the qualitative SVG from text source. Pixel/viewBox coordinates are display layout, not physical measurements.

## Visual, system, and claim boundary

The wide hero's main silhouette is vertical cell frontage inside retained masonry, deliberately distinct from HF-01's broad optical arcade. Its suspended cell and riggers lead; the gallery, quality bench, separately colored stores, stopped carrier, and freight beyond establish the secondary reading. The close view makes an isolated empty berth, scuffed connection, dusty protected window, and human hold decision inspectable. The inset names incoming feedstock, hold/reject, qualified input, and outgoing residual as **separate dispositions**. It shows accessible utility valves and external freight without quantities or guaranteed exchange.

**Required public caption:** “Composite Toledo-derived 2075 scenario / K architectural form.” E is inherited industrial/freight/material context; S is FT-03's conditional qualification, exchange, outside dependency, and institutional responsibility; K is this hall arrangement, cell family, optical gallery, specific actions, and future material layout. The Phase 17A Industrial Exchange study is S/K lineage, not E evidence. No real plant, survey, structural capacity, compatible stream, throughput, recovery fraction, continuous operation, or environmental benefit is claimed. A residual can remain held, be rejected, or leave the depicted process. The lifting and isolation imagery is not a work instruction.

## Atlas use and QA

The local Vite build adds `/atlas/industrial-metabolism-2075/`, a second home futurescape card, an `/updates/` milestone, and links among HF-01, the Industrial Exchange study, methods, roadmap, Phase 17D records, and the FT-03 S packet. The wide was inspected at full size and 900, 560, and 390 pixel 16:9 display widths; the maintenance view was inspected at full and 900 pixel widths. The section was parsed and raster-rendered for visual QA. All three final files remain below their target budgets. Final mechanical, route, and protected-artifact results are recorded in the current phase handoff.
