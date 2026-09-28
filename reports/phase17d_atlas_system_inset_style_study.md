# Phase 17D Atlas system-inset style study v1.0

**HF-02 pilot · three graphic treatments for one unchanged conceptual coast section.** The accepted HF-02 lead and working-detail images are unchanged. Temporary A/B/C study outputs live under `temp/phase17d-hf02-inset-style/` and are not part of the Git deliverable. Human review accepted Option C for HF-02 production as the **Atlas system-inset style v1.0 candidate**, limited to HF-02; the production SVG is the accepted Option-C rendering. No older inset is migrated here. The [public visual house guide](../docs/phase_briefs/phase17d_public_visual_style_guide.md), [three-hero retrospective](phase17d_three_hero_visual_retrospective.md), [HF-02 composition study](phase17d_hf02_composition_studies.md), and [HF-02 production notes](phase17d_hf02_final_production_notes.md) bound the visual and claim decisions.

## Diagnosis and shared design rules

The current HF-02 inset preserves the correct land → protected service → dry recovery → quay → lake relationship, but **seven top label clusters, three footer cards, near-equal room outlines and stick workers** compete with its section. The internal “HF-02 / supporting system explanation” heading gives production language more prominence than the public question. Fouling, screen wear and isolation are mainly explained in words. The HF-01/03/04 insets show the same family tendency: useful information, too many near-equal graphic elements.

All three alternatives reuse **one coast drawing** and the same six information groups: (1) outside supply and staffed threshold, (2) opaque utility service with an isolatable bay, (3) sacrificial screen and human instrument comparison, (4) grounded civilian survey craft in a dry cradle, (5) weathered/fouled working quay, and (6) open Lake Erie. A long roof and a stepped retained quay form the primary silhouette. Human silhouettes, a panel at service height, sensor case and bench, dry rollers, protected cyan zone, exposed water, hatch for unavailable equipment, and restrained wet-edge fouling carry detail without more prose. The drawing asserts no surveyed geometry or working procedure.

- **Typography:** Georgia editorial title, 44 px at the 1440 px plate; Arial 18 px subtitle, 19 px callout label, 16 px short note, 15 px claim footer. Public title: **“How the lake-edge service terrace works.”** The eyebrow says “Western Basin Atlas / System inset”; internal phase/HF codes stay in filenames and metadata.
- **Line weights:** 6 px for the continuous ground/section datum; 3 px for architecture and equipment; 1.5 px for leaders and secondary details. Major boundaries are darker than texture. Boxes appear only where an actual room, door or case has physical enclosure.
- **Color:** warm paper `#f3f1e9`, neutral concrete `#d4d1c6`, structural blue-gray `#3e5357`, muted lake teal `#8baeb9`, pale protected-screen cyan `#d8e9e6`. Ochre `#a78c56` marks an outside utility/access connection and isolation hatch only. Color does not encode capacity, outcome or certainty.
- **Callouts and people:** six keyed groups at most; A/B use hairline leaders, C uses a narrow key. Workers are small filled coat-and-leg silhouettes doing service tasks, not cartoon stick figures or authority badges. Texture is limited to concrete age, translucent screen, service hold hatch, weather marks, wave lines and lower-quay fouling.
- **Claim boundary:** one quiet two-part footer: “Scenario / design concept · qualitative relationships only · no measured dimensions or performance” and “Composite coast; not a real facility or crib retrofit.” The accessible SVG description states the fuller nonclaims. E/S/K should remain in surrounding page copy, not become the plate headline.

## A / B / C comparison

| Review test | A — editorial section + callouts | B — section + margins | C — section + key strip |
| --- | --- | --- | --- |
| Section dominates; reads before labels | Yes; full-width continuous cut. Top callouts draw a second glance. | Partly; margin width shrinks the cut. | Strongest; full-width cut has very few competing marks. |
| Scientific/editorial Atlas feel | Closest to a conventional annotated architectural plate. | Field-guide-like, but long leaders cross the drawing. | Cleanest compact plate; key reads as a legend, not UI cards. |
| Human scale, functional transparency, exposed/protected split | Same restrained silhouettes, screen hatch, opaque utility bay and open water in all three. | Same shared scene. | Same shared scene. |
| Fouling and interrupted service | Lower wet-edge marks and hatched utility bay; named in callouts. | Same marks; smaller at equal display width. | Same marks; “quay + fouling” and “utility / isolation” key entries. |
| 390 px relationship and numbers | Coast sequence and numbers survive; perimeter copy is tiny. | Weakest: margins compress the scene and leaders become thin. | Best: coast sequence and in-scene numbers survive; key text needs enlargement. |
| Claim footer and migration potential | Compact footer; good for complex HF-01/HF-04 sections. | Compact footer; likely needs more width than mobile provides. | Compact footer; reusable default for the other three if their content is edited down. |

**Accepted for HF-02: C — section + small key strip, as the Atlas system-inset style v1.0 candidate.** It gives the coast section first reading, preserves six keyed relationships and has the most coherent 390 px silhouette. A is a useful alternate when the editorial page has enough width and a leader must point to a precise joint. B is not the selected HF-02 treatment: its whitespace is attractive at full size, but the drawing loses too much width and leaders cross the section. This decision does not authorize or claim migration of HF-01, HF-03, or HF-04 insets.

At 1440 and 900 px, all three labels and the compact claim footer are readable without collision. At 560 and 390 px, the physical sequence and keyed numbers survive, but **small label/key/footer type is not independently readable**. The HF-02 page therefore provides six corresponding semantic HTML callouts after the SVG; at narrow widths they form a single text column so readers do not need the small SVG key to understand the system. The SVG remains an openable standalone graphic. The apparent open sky/negative space is intentional, with no clipped text or empty canvas artifact. None of the SVGs contains a Windows path.

## HF-02 invention observations

- **Lake instrument recovery cradle:** The U-shaped dry interruption is spatially recognizable and has a grounded civilian craft, rollers and nearby person. It changes the coast edge, but the exact handoff and weather protection remain underspecified. At small size it may still read as a generic service berth. **Provisional K; no GBI number.**
- **Weather-screened inspection gallery:** The protected cyan depth, sacrificial screen, worker, bench and isolated neighbor show why the gallery has section thickness and needs upkeep. The screen can still look like an ordinary window unless a future detail plate explains its replaceable interface. **Provisional K; no GBI number.**

## Migration plan for older system insets — no asset edits here

| Inset | Carries over cleanly | Redesign / density / possible second plate |
| --- | --- | --- |
| **HF-01 canopy / old wall** | Wall-to-canopy relationship, replaceable leaf and open berth, walkable rib, visible break to an unconnected neighbor. | Replace oversized type and stick worker; simplify competing structural/data/power linework. Density is high. A second small interface plate could hold power/data, public access and property-agreement boundaries while the main plate keeps roof and old wall. |
| **HF-03 field / seam / drainage** | Open field → selective bay → opaque work → old gate/ditch → separate wetland reads well. | Remove top-row label crowding and three UI-like bottom cards; soften soil texture and worker icon. Density is high. A later second plate could separate qualification/hold/outward paths from the landscape/drainage section. |
| **HF-04 old hall / cell frontage** | Retained hall and crane, vertical frontage, open berth, protected checking and outside freight are strong. | Thin heavy borders, replace stick riggers, reduce internal labels and four colored material cards. Density is high. A later material-disposition plate could cover incoming/hold/qualified/residual and utility routes, leaving the hall/cell section dominant. |

## Production and QA

`src/python/phase17d/build_atlas_system_inset_style_study.py` regenerates the three same-information SVGs and, with `--render` and CairoSVG, their 1440 × 900 PNG previews. SVGs are XML-parsed by the builder. All six temporary study outputs were inspected at native 1440 px and at 900, 560 and 390 px scaled review widths. The earlier HF-01/HF-03/HF-04 insets were visually inspected for the migration plan only; none is migrated by this transaction. The production builder writes the accepted HF-02 Option-C SVG. This study does not change the scientific baseline or assign an invention ID.
