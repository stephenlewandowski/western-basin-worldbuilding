# Public Atlas Language & IA Audit

**29 September 2026 · Proposal for human review; no implementation.** Audited clean `main` and local `origin/main` at `876601e7f7b78988bfd72210464681da2cc67e78`, the supplied deployed baseline. Deployment identity was supplied by the project; this audit did not independently verify the remote deployment.

## Executive findings

1. **The public entry points disagree about what exists.** README describes a future Atlas and a four-essay preview, while the site now presents four futurescapes as well as four studies. Put the live Atlas and current work before the phase history.
2. **HF-02 supplies a useful vocabulary, but it is not applied consistently.** Glass City, Maumee and Industrial Metabolism still expose HF IDs, phase/order badges and “K architectural form.” Methods still says “HERO FUTURESCAPE.” Publication order is taking the place of a useful content category.
3. **Studies need their own visible navigation and accurate scope.** The collection includes evidence/model material, an evidence-to-concept study, and two scenario studies. Calling the whole collection scientific support can make its speculative parts appear evidential.
4. **Transparency is strong but badly distributed.** Long status paragraphs, production links and repeated canon disclaimers interrupt the pictures. Retain scene-specific limits next to the work; organize code definitions, provenance and release history in Methods and repository records.
5. **The proposed cleanup can preserve all stable identifiers.** Change visible labels and reading order; retain routes, source targets, phase records, asset filenames, HF/GBI IDs and historical reports.

### Audit basis and scope

Reviewed [README](../README.md), [status context](../PROJECT_STATUS.md), the complete [page renderer](../src/atlas/main.ts), [study content](../src/atlas/content.ts), [site styles](../src/atlas/style.css), home and all eight Atlas HTML entry points, Methods/Updates/Roadmap entries, and [game entry](../game/index.html). Also inspected the public source-link labels and their roles, the [licensing note](../docs/references/DATA_AND_ASSET_LICENSING.md), current HF-02 standard and all four production SVGs. Temporary raster previews were used to inspect the SVGs; production files were not regenerated.

This is a source and content audit with visual inspection of the insets, not a new full-site browser accessibility or responsive certification. The GitHub About description is not represented by a dedicated setting in the inspected repository files; its live text was not fetched. Suggested About copy below is a proposal, not a report of current GitHub settings. No broad audit of internal research Markdown was performed.

## Public vs internal vocabulary

Use place names, human activity and the kind of material a reader is seeing. Internal identifiers remain valuable in research records and reproducibility instructions. A public label may differ from a filename without weakening provenance.

**Classification:** A = keep publicly; B = translate; C = move to Methods/technical context; D = remove from that public surface; E = keep internal only. D never means delete the underlying historical record. A term can receive different decisions in different contexts: a drainage **gate** and staffed material **acceptance** describe the world; a publication **gate** and **accepted image** describe production.

## Terminology translation table

| Internal wording / role | Preferred public treatment | Class and reason |
| --- | --- | --- |
| Hero, hero image | **Lead image** when naming the picture | B; avoid production jargon |
| Hero futurescape | **Futurescape** for the whole illustrated place | B; distinct from an individual image |
| Hero set | Omit the package label; name the futurescape and its images/inset when needed | B; “futurescape set” adds little |
| HF-01 / HF-02 / HF-03 / HF-04 | Glass City 2075 / Lake Erie Energy & Security Coast 2075 / Maumee Bio-Ag Landscape 2075 / Industrial Metabolism 2075 | B publicly; E in identifiers |
| Phase 17D | **2075 Futurescapes** for the collection; **Futurescapes** in navigation | B; phase history belongs in technical records |
| Phase 17A / prototype collection | **Studies**, with each study's evidence/concept distinction | B; do not imply all four are evidence |
| Maintenance view/detail | **Working detail** as the recurring section label | B; maintenance remains a precise activity in prose |
| Explanatory section/inset | **How it works** as the page heading; **system inset** as the graphic type | B; heading and artifact have different jobs |
| K architectural form / S–K concept | **Scenario and design concept** in future-scene captions | B; retain composite place and year |
| E / S / K boundary | **What is grounded / What is speculative** | B inline; A for defined codes in Methods |
| E / S / C / K definitions | Evidence/model; scenario; fictional canon; provisional sketch | A in Methods; “design concept” describes visual K, not every K record |
| GBI number / established invention entry | Named **design concept**, only if useful to understanding the scene | B name; C catalog link; E registration/status detail |
| Published | Keep in dated announcements and bibliographic context | A; D as repeated card/page status decoration |
| Accepted / production gate / human review | Omit from the public content hierarchy | E workflow; C revision provenance if consequential |
| Candidate / provisional | Say **proposed** or **design concept** when it qualifies an actual idea | B; E when it only means an unpublished asset |
| Frozen baseline | **Versioned research baseline**, with preservation/reproduction explained | B/C; technical freeze terminology remains in repository records |
| Scenario-development material | **Scenario** or **design concept**, as appropriate | B; do not upgrade epistemic status |
| Prototype / sketch | Keep if describing a medium or experimental narrative work; use **study** for this Atlas collection | A/B by context |
| Review / gate / acceptance in human work | Keep scientific review, drainage gates and human material decisions | A; never use blanket string replacement |

## Occurrence register

Locations below refer to the audited commit. Repeated terms on the same source line are grouped by visible field; each group has a disposition. `main` means `src/atlas/main.ts`; `content` means `src/atlas/content.ts`. Imported paths, CSS classes such as `.hero`, variable names and source URL strings are **E** throughout, and must remain stable.

### Home, shared UI and metadata

| Location / visible occurrence | Disposition |
| --- | --- |
| main:30,39–41,58 — Worldbuilding brand, Atlas Preview/v0.1, publication-count footer | B: use Western Basin Atlas as the publication label, with Worldbuilding as the project/repository identity. D: version/count/status footer clutter; A: place description and guiding principle. Naming is an editorial proposal, not a repository rename. |
| main:63 — HF-01 art label; K architectural form caption | B: place title and “Composite Toledo-derived 2075 scenario and design concept.” |
| main:65,67 — four published; first/second/third/fourth; HF IDs; S–K concept | B: collection heading “2075 Futurescapes,” place titles and scenario/design labels. D: ordinal/publication badges on cards. HF-02 title already follows the place-name rule. |
| main:66,74 — lead image/working detail; accepted Phase 17A scientific/support studies | A: new image vocabulary. B: “Studies of the basin and its possible futures”; C: phase lineage. |
| main:77 — accepted/frozen Phase 16, Phase 17A, published quartet, GBI-03 established, provisional module, Phase 17C tests | C: research preservation; E: phase and invention dispositions. D: this delivery-status paragraph; replace with a short topic-based development link. |
| main:78 — E/S/C/K and “no new canon” home key | C: full code definitions in Methods. B: short home explanation of evidence and imagined futures. |
| main:52,85–91 — study status pills, “visual essay,” interpretive boundary, source labels | A: useful per-study claim distinction and source access. B: standardize collection/back-link language to “Studies.” C: development-only boundary content identified below. |
| main:92 — Industrial Metabolism “hero”; Phase/S–K development lineage | B: futurescape; C: detailed lineage. A: distinct architectural interpretation rather than district reconstruction. |
| index.html — “illustrated preview,” Atlas Preview title | B: public Atlas identity after editorial approval; do not change URL. |
| atlas/glass-city-2075/index.html and atlas/industrial-metabolism-2075/index.html — Phase 17D scenario/architectural sketch descriptions | B: composite scenario and design concept; D: phase identifier in search descriptions. |
| atlas/maumee-bio-ag-2075/index.html — Published Phase 17D, S/K architectural form | B: scene and concept description; D: production status and codes. |
| atlas/lake-erie-energy-security-coast-2075/index.html — scenario/design concept, no performance claim | A: established direction; retain useful place/scene detail. |
| updates/index.html — Phase 17D visual development description | B: dated additions and changes to the Atlas. |
| methods/index.html; roadmap/index.html; four study entry descriptions | A: accurate subject and uncertainty descriptions; roadmap wording should follow topic-based plan below. |

### Futurescape pages

| Location / visible occurrence | Disposition |
| --- | --- |
| main:99–100 — HF-01 caption, K form, Phase 17D/first | B: public caption and place title; D: ordinal/phase eyebrow. |
| main:101–102 — maintenance view; explanatory/supporting section; schematic K | B: Working detail / How it works / qualitative design concept. A: lifting, geometry and performance limits. |
| main:103 — E/S/K, no new canon; Phase synthesis, HF concept, production notes and HF update links | B: grounded/speculative explanation. C: codes and provenance links under technical details. E: canon-promotion status. A: specific unresolved constraints. |
| main:104 — HF-04-related copy and support-study references | B: place-based links; A: retained distinct source relationships. |
| main:110–111 — HF-04 caption, K form, Phase 17D/second | B: caption and title; D: phase/order badge. |
| main:112–113 — maintenance view, explanatory section, schematic K; qualification/acceptance/rejection | B: section labels. A: qualification, rejection and human decisions describe the work. |
| main:114 — E/S/K; FT-03; no new canon; HF-04, phase, production and provenance source labels | B: prose boundary; C: coded scenario/provenance detail. A: held/rejected/outward material and nonclaims. |
| main:115 — Phase 17A, S/K, first/second hero and public visual calibration | B: earlier system study and separate design concept; E: calibration and production-order history. |
| main:121–122 — HF-03 caption, K form, Phase 17D/third published | B: place caption and concept language; D: badge. |
| main:122–124 — drainage gate, maintenance view, explanatory section, schematic K | A: actual gate/work; B: recurring labels and K shorthand. |
| main:125 — E/S/K; candidate swamp geometry; GBI-03, S/K entry, provisional module; phase/HF/composition/production links | B: scene-specific grounded/speculative text; C: invention/visual provenance. E: register dispositions and unused candidate-geometry workflow. A: no real farm, organism release, water-treatment or yield claims. |
| main:126 — “Three different working futurescapes” | B: “Other working landscapes”; D: count tied to release history. |
| main:132–135 — Lead image, Working detail, How it works, scenario/design concept, six callouts | A: preferred vocabulary and accessible explanation. D: “fourth published” eyebrow at 133. B: shorten the explanatory text about HTML mechanics; preserve the key and its limits. |
| main:136 — scenario/design boundary, no new canon, candidate catalog and visual-record links | B: grounded/speculative heading. E: canon-promotion sentence. C: visual-production links and catalog; A: scene's specific limits and Methods access. |
| main:137 — named futurescape and crib links | A: keep; the explicit separation from the real crib prevents a false location inference. |

### Methods, Updates, Roadmap and studies

| Location / visible occurrence | Disposition |
| --- | --- |
| main:142–143 — preview, E/S/C/K definitions, canon | A: definitions here; B: publication description; E: repeated release-level “no new canon.” |
| main:144 — HERO FUTURESCAPE, scenario/sketch, Phase 17A/frozen baseline, accepted inset/migration, GBI-03 established and provisional module | B: Futurescape and design-concept language; A: basic reading order. C: research versioning. E: migration/acceptance/registration status. D: duplicated six-HTML-callout explanation. |
| main:145–146 — accepted science, source gates, Phase 14/16/17A, prototype, freeze/validation records | A: methods, qualitative limits, sources and rights. C: phase crosswalk/builders/manifests in technical subsection. B: studies in editorial prose. E: review outcomes that do not affect the reader's interpretation. |
| main:151–159 — reviewed date, frozen/accepted/active timeline, phase headings, development packets/counts, HF-05, S/K/no C, detailed-status link | A: reviewed date and detailed-record access. B: topic headings and developed/developing/exploring descriptions. E: packet counts, phase states and release gates. C: uncertainty-register details. |
| main:160 — “accepted visual studies” CTA | B: “Explore the studies.” |
| main:164 — project updates/futurescape development, produced, evidence/canon | B: “New in the Atlas,” additions and revisions; A: dates and interpretation-changing corrections. |
| main:166 — fourth published, accepted lead, six matching HTML callouts, civilian interpretation, no new canon | A: publication event and scene subject. D: ordinal/accepted wording and implementation trivia. E: canon transaction statement; retain relevant limits concisely. |
| main:167 — HF-03 accepted/published/third hero, Phase 17D, human review, C/C-L1, authorization, S/K, GBI and production links | A: publication date and visible farm work; B: futurescape names and concept label; E: review decisions/authorization. C: catalog and production record. |
| main:168 — two-hero retrospective, HF selection/order, production not begun, no new C | E: internal delivery-log entry; preserve original retrospective, omit from curated public updates or link from a technical archive. |
| main:169 — HF-04 hero set/build/second Phase 17D, S/K | B: Industrial Metabolism addition and visible human work; C: production record. A: qualification, external exchange and limits. |
| main:170 — HF-01 hero set/build/first, S/K, HF-04 not produced yet | B: Glass City addition; E: comparative build status; C: production record. |
| main:171 — Phase 17D direction, hero-led, S/K/no C, Phase 17A | B: illustrated places now lead the Atlas; C: design-method explanation; E: phase transaction status. |
| main:172 — HF-01 procedural study not selected as hero; HF-04 second | E: asset-selection history; retain in reports, not the public milestone feed. |
| content:48,50,55 — evidence/model; accepted geography/model | A: evidence category; B: sourced geography/model, avoiding acceptance as evidence of truth. |
| content:63,65–66 — prototype accepted, rejected animation; prototype brief/validation | E: animation decision; B: boundary should explain analytical limits already present in reading text; C: brief/validation behind clear technical-source labels. |
| content:72,86,89 — evidence→sketch; verified coordinate, sketch material, prototype validation | B: “Existing structure and future concept”; A: verified location vs approximate drawing and unconfirmed image rights; C: validation record. |
| content:95,112–113 — scenario/sketch, prototype validation, Phase 17B packets | B: scenario and design concept; C: validation/scenario-source links. |
| content:119,124,129,134,136–137 — scenario/sketch; spatial sketch; prototype validation; Phase 17A synthesis | B: recurring status label; A: ordinary “spatial sketch” as a medium and conditional exchange explanation; C: production/phase-source links. |
| Older production SVG headers/footers — HF IDs, K/S/C, supporting explanation, qualification gate | B: public titles and concept footer in later migrations. A: material qualification gate; E: identifiers remain in paths/builders. See migration plan. |

### README and exposed repository records

| Location / occurrence | Disposition |
| --- | --- |
| README:11,35–56,73–75 — developing toward Atlas; phase summary; complete/accepted/frozen, prototypes, role packets | B: current Atlas introduction; C: concise technical history near the bottom; E: acceptance/packet machinery in status records. |
| README:60–79 — resolved crib, held swamp, next Phase 17, status/canon links | C: research notes / development details. A: links remain available; remove their prominence before the Atlas link. |
| README:83–98 — Atlas Preview v0.1, four essays, accepted Phase 17A prototypes, deployment commands | B: accurate four-futurescape/four-study overview; C: local build/deployment instructions and licensing. A: live site link. |
| README:134–150 — evidence, scenario, canon, sketch | A: brief principle; C: full definitions through Methods. |
| README:158–192 — Phase 15/16, regimes, terminated propagation | A: findings and model limits; C: long technical detail and phase IDs. |
| README:197–224 — future-tense Atlas, Phase 16B noncanonical hooks | B: current publication plus future work; E: hook disposition. A: field sketches as an ordinary medium. |
| README:230–246 — accepted packages, independent review, freeze manifests, frozen science | A/C: concise reproducibility section; technical terms are appropriate here with explanation. |
| README:250–272 — four page entries, Atlas Preview, src/game prototype, reports/reviews | B: accurate repository guide; E: directory names retained. `game/index.html` actually loads `src/main.ts`; verify directory descriptions before rewriting. |
| PROJECT_STATUS, canon status, phase briefs, composition/production reports reached through source links | E: retain their internal vocabulary and historical record. C: label links “Technical records” and route discovery through Methods; their accessibility does not make them editorial homepage copy. |
| Licensing note and source/validation indexes | A: ownership, rights and source limitations; C: detailed manifest/phase vocabulary. No evidence for renaming these records. |

## Homepage

Recommended order: **Western Basin Atlas introduction → 2075 Futurescapes → Studies → How the Atlas is built → Updates / what is being developed**. Keep the existing strong place-based headline or test a shorter subtitle; no new visual redesign is needed.

Use four place-name cards without ordinal badges or HF IDs. Keep the four study cards as a distinct collection. Replace the long status band with two short links to Updates and Roadmap. Reduce the full E/S/C/K home key to a short explanation: the Atlas pairs sourced studies of the basin with clearly marked imagined futures. Link to Methods for definitions.

Label Studies accurately: From Field to Lake is an evidence/model study; Toledo Intake Crib combines a real asset with an approximate drawing and a future concept; Farm 2075 and Industrial Exchange are scenario/design studies. Do not imply that the latter validate the futurescapes' technologies.

## Navigation

| Public label | Existing destination | Treatment |
| --- | --- | --- |
| Brand / home | `/` | Western Basin Atlas publication identity; project name remains in About/footer |
| Futurescapes | `/#futurescapes` | Replace ambiguous “Atlas” link |
| Studies | `/#essays` | Make existing collection directly discoverable; retain anchor |
| Methods | `/methods/` | Credits remain within page |
| Updates | `/updates/` | Public additions and revisions |
| Game | `/game/` | Secondary utility/footer link, named “Vesper Station game” where space permits |
| Roadmap | `/roadmap/` | Footer and Updates link; remains a stable public page |

Prefer four primary content links to five equally weighted tabs. Game is an experimental narrative companion, not a fifth evidence collection. Add a simple “Back to Atlas” link to the game shell in a later navigation-only change: the current `game/index.html` has controls but no Atlas return link. Do not revise game content or imply that its fiction is new Atlas canon. Review wrapping and focus order at mobile sizes when implementing.

## Futurescape pages

Use this common structure for the four published pages and any later fifth page, without initiating that fifth page now:

1. **Place title and one-sentence premise** before the lead image, so readers know what they are entering. Keep this header compact; move longer introductory prose below the image or reduce it.
2. **Lead image**, preserving the accepted image and useful crop. Caption: “Composite [place]-derived 2075 scenario and design concept.” Preserve Maumee-derived for Maumee and Lake Erie / Toledo-derived for the coast.
3. **Working detail**, with an action-specific heading and one short account of human work. Preserve precise limits such as a depicted exchange not being an engineered lifting procedure.
4. **How it works**, dominant system inset plus an ordered HTML key. Say what interfaces and dependencies the drawing explains; do not promise an operating mechanism or measured result.
5. **What is grounded / What is speculative**, two short, scene-specific paragraphs and the most consequential unresolved claims. Keep the distinction on the page rather than hiding all uncertainty in Methods.
6. **Related studies and Methods**, followed by a small technical-provenance link. Prefer topical relationships over production chronology.

Useful transitions: Maumee → Farm 2075 and From Field to Lake; Industrial Metabolism → Industrial Exchange; Lake Erie → Toledo Intake Crib with explicit no-co-location distinction. Glass City can link to Methods and the broader systems collection rather than implying the water studies verify its canopy. Do not require the template to repeat its place title inside every caption.

## Methods and public technical-transparency boundary

| Layer | Keep there |
| --- | --- |
| Caption / image alt | Composite place and year; scenario/design label where needed; visible subject and action. Avoid an entire limitations inventory in alt text. |
| Futurescape prose / small callout | Actual evidence inheritance, conditional scenario dependencies, invented arrangement, specific unknowns and physical separations. |
| Methods, plain-language opening | Evidence/model vs scenario vs fictional canon vs provisional sketch; why appearance is not proof; qualitative geometry; source/rights and image-making disclosure. |
| Methods, technical subsection | E/S/C/K crosswalk, reproducibility, phase-to-subject index, model constraints, versioned research baselines and links to builders/manifests. Explain “frozen” as preservation of reviewed research. |
| Repository reports/status/catalog | Exact review decisions, production gates, HF/GBI registration, commit lineage, hashes, freeze manifests and detailed scenario packets. |

Do not relabel all K as established design: K also covers provisional narrative material. Do not equate scientific grounding with validation of the depicted future machinery. Add concise image provenance in Methods: the raster futurescapes are generated concept illustrations, while system insets are authored qualitative diagrams; neither supplies measurements. Link exact production records for readers who need source hashes and generation history. Retain third-party image exclusions and licensing limits.

## Updates

Keep true publication dates and reader-visible additions. Prefer a title such as “Explore a working Lake Erie coast in 2075,” followed by what the reader can see and why it adds something: weather-screen work, returned survey equipment and dependence on human service. “Published” is useful event language; “accepted” is not a content type.

Condense each public entry to an addition, an interpretive point and a link. Remove composition codes, publication authorization, build status and comparisons with not-yet-produced assets from the feed. Preserve the original records in the repository. The two retrospective/selection-only entries are delivery history, not necessary public milestones. Keep corrections that materially change interpretation visible and dated; do not rewrite history to suggest an asset existed earlier.

## Roadmap

Replace phase-first rows with **Research foundation**, **Studies**, **2075 Futurescapes**, and **People and stories**. State what readers can explore and what is still being developed. Keep unresolved geographic/interpretive issues in a brief topic-based note; exact canon dispositions stay one link away. Avoid promising a schedule or treating “complete scientific foundation” as complete knowledge of the basin. Retain the date reviewed and a technical status link.

## GitHub README

The opening clearly establishes Toledo, the Maumee and western Lake Erie and a sound geography-first principle. It does not quickly connect a new reader to the current Atlas. The first site link is around line 94, after detailed phase and crib-coordinate history; none of the four futurescapes is introduced. The “next major stage” and “will transform” wording is stale relative to the published work.

Recommended hierarchy:

1. One-paragraph project definition: an illustrated, scientifically grounded futures atlas rooted in Toledo, the Maumee watershed and western Lake Erie.
2. **Explore the Atlas**: live link and a sentence distinguishing publication from research repository.
3. **2075 Futurescapes**: four named links and a common scenario/design-concept qualifier.
4. **Studies**: four named links with their actual evidence/scenario character.
5. **Methods and reproducibility**: distinction between claims, Methods link, then local build commands and source/validation indexes.
6. **Game / experimental narrative**: Vesper Station, clearly a companion work.
7. **Repository guide**: accurate directories, keeping current names.
8. **Development details**: concise date/status link and technical history.

Suggested GitHub About text, if later authorized: “An illustrated futures atlas grounded in the geography and systems of Toledo, the Maumee watershed and western Lake Erie.” Set the existing Atlas URL as the website field only in a separate authorized implementation. Do not settle the open Glass Basin naming question through this copy edit.

## High / medium / low cleanup priorities

| Priority | Reader problem | Later action |
| --- | --- | --- |
| HIGH | README fails to introduce the current publication | Lead with live Atlas and four named futurescapes; repair stale hierarchy/counts |
| HIGH | First three futurescapes and their metadata use internal labels | Apply the HF-02 vocabulary, preserving scene-specific uncertainty |
| HIGH | Studies are hard to find and can be mistaken for uniform evidence | Add Studies navigation and accurate per-study labels |
| HIGH | Updates/Roadmap require development history knowledge | Curate public milestones and topic-based development areas |
| MEDIUM | Long intros/status sections repeat Methods and release machinery | Use compact title/premise; consolidate transparency into the layers above |
| MEDIUM | HF-02 callout solution is absent from older insets | Follow the separate migration plan one futurescape at a time |
| MEDIUM | Related work follows chronology more than subject | Add specific study connections and explain limits of support |
| MEDIUM | Game has no evident Atlas return path | Add a small shell link; keep narrative contents intact |
| LOW | Preview/version/count labels and inconsistent “essay/study” wording | Standardize labels and footer after higher-priority copy work |
| LOW | Repeated diagram/HTML implementation explanations | Replace with simple reader guidance; keep accessibility behavior |

Eight cards across two real collections are not inherently excessive. Remove repetitive status decoration before changing the card system. No evidence from this audit warrants a navigation redesign or replacing accepted lead images.

## Recommended implementation sequence

1. Human approval of public vocabulary, navigation and the title/premise-first template.
2. A bounded public-copy/IA change, including metadata, README and navigation-only game return link. Preserve all URLs/IDs and technical records. Review public rendering and claims before publication.
3. Migrate HF-01's inset plus HTML key; human visual and meaning review.
4. Migrate HF-03; review open-field dominance, containment/drainage separation and mobile key.
5. Migrate HF-04; review material distinctions and external dependence. A second plate remains separately scoped work.
6. Final consistency/accessibility/link review across both collections, Methods, README and public updates; approve any publication separately.
7. Consider HF-05 only in a later authorized transaction.

See the [system-inset migration plan](phase17d_system_inset_migration_plan.md) and [proposed compact language guide](../docs/public_atlas_language_guide.md). This transaction creates documents only; approval of this audit does not itself authorize deployment.

## Transaction validation

`git diff --check` passed. The repository Markdown-link validator passed with **185 links**. The tracked diff against the audited baseline is empty; status lists only this report, the migration plan and the compact language guide as new untracked files. No public-site file, production asset or protected Phase 1–16 file changed. No internal filename or route was renamed. No commit, push or deployment was performed. Full-site runtime QA belongs to the later implementation transaction.

## Implementation authorization — 29 September 2026

Approved for bounded implementation on 29 September 2026. The local candidate adopts the public vocabulary and information architecture; publication remains subject to human review. The original audit and its transaction validation above describe the earlier audit-only state. System-inset migration remains future work.

## Human review and publication authorization — 29 September 2026

The public-language and information-architecture candidate passed human review. Publication is authorized. This approval does not expand the accepted cleanup: system-inset migration and HF-05 remain outside this transaction, and no new canon is created.
