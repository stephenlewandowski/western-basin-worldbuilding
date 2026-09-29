# Atlas System-Inset Migration Plan

**29 September 2026 · Proposed v1.0 rules and migration briefs; human review pending.** Baseline: `876601e7f7b78988bfd72210464681da2cc67e78`. No production inset, page or asset is changed by this plan. HF-02 is the accepted reference; extending its treatment to other futurescapes remains a separate implementation decision.

## HF-02 reference standard

Reviewed the current [Lake Erie service-terrace inset](../assets/phase17d/hf02/hf02_service_terrace_recovery_section.svg), its [builder](../src/python/phase17d/build_hf02_service_terrace_recovery_section.py), the [shared study drawing](../src/python/phase17d/build_atlas_system_inset_style_study.py), [HTML renderer](../src/atlas/main.ts) and [CSS](../src/atlas/style.css). All four production SVGs were rasterized to temporary files for visual inspection; originals were read only.

Option C succeeds because one physical section carries the explanation: staffed landward access, opaque services, screened comparison work, a dry recovery cradle, exposed quay and open lake. Six markers stay inside the scene; a small strip names them without surrounding the drawing with paragraphs. The HTML key supplies the complete explanation and its limits. This is the reference relationship between drawing and text, not a mandate to reproduce the coast's building shape.

Useful existing conventions: 1440 × 900 viewBox; cream background; dark structural linework; secondary service lines; restrained condition patterns; human silhouettes doing work; serif title; compact qualitative-claim footer. The current page uses two HTML columns, switching to one below 650 px. The SVG key is not independently readable at phone scale. Full-size access and adjacent HTML are essential parts of the design, not optional extras.

One implementation consideration: the HF-02 production builder currently imports the Option C drawing from the style-study builder. A later small shared helper for typography, markers and footer may reduce duplication, but it must not couple all section geometries or regenerate accepted HF-02 incidentally.

## Shared v1.0 rules

These are minimum proposed rules, subject to the first migration review.

| Element | Rule |
| --- | --- |
| Canvas | Keep the demonstrated 1440 × 900 viewBox for these migrations; display coordinates only. Fit the complete plate responsively without a fixed-height crop. |
| Title | Top-left “WESTERN BASIN ATLAS / SYSTEM INSET” kicker and one place/system-specific title. Use the established serif title with sans-serif explanations. No HF or phase badge in visible artwork. |
| Subtitle | One sentence identifying what relationship the section explains and its qualitative/composite character. Avoid review status and exhaustive nonclaims. |
| Drawing area | Give the physical section the broad middle of the plate; approximately three fifths of canvas height is available between heading and strip. Preserve useful negative space. Do not enforce equal zone widths or enlarge soil/water merely to fill the canvas. |
| Line hierarchy | Primary section/structure heavier than equipment; equipment heavier than patterns/leaders. HF-02's 6 / 3 / 1.5 display-unit strokes are a useful starting reference, not physical sizes or a rule for every path. |
| Callouts | Use 4–6 numbered groups; these briefs propose six each. Numbers identify places/interfaces, not steps in an automatic process. |
| Marker | Filled dark circle and high-contrast light number, matching HF-02's treatment; keep off critical joints and work gestures. Use short leaders only where needed. |
| Key strip | One compact row in the same reading order as markers and HTML. Short noun phrases, not paragraphs or six boxed mini-diagrams. If it cannot fit clearly, shorten/group labels before shrinking type. |
| Palette | Cream ground, dark gray/teal structure, restrained scene accents. Color alone must not encode service type, state or material disposition. |
| People | Small filled silhouettes with legible posture, tool or contact point. Show a specific maintenance/inspection action, avoiding decorative figures or misleading procedural precision. |
| Patterns | Sparse material/condition marks: patched panel, clouded screen, clay, wear or wetting where relevant. They distinguish condition without inventing calibrated intensity or abundance. |
| Footer | One compact concept/qualitative statement plus the most relevant local limit. Example: “Scenario and design concept · qualitative relationships; no measured dimensions or performance.” Keep the fuller limits in HTML/Methods. |
| Accessibility | SVG title/description, meaningful page alt, semantic ordered HTML list, logical heading order, keyboard-accessible full-size link. SVG text embedded through an image is not a substitute for HTML. |
| HTML relationship | One-to-one number and concept match. Expand each phrase into a short explanation including necessary conditionality. Keep full descriptions outside hover, tooltip or click-only interactions. |
| Responsive behavior | Preserve all zones. Two text columns where comfortable, one on mobile. Reserve image aspect ratio and use available content width; inspect default figure margins rather than inheriting unnecessary inset space. |

The current SVG's 15–18-unit small text is a desktop annotation, not a phone text size. Do not claim mobile accessibility merely because the picture shrinks without overflow. Use ordinary readable HTML text, and verify contrast and zoom behavior during implementation.

## What remains futurescape-specific

Keep the section geometry, orientation, number/size of zones, accent colors, materials, weather/environment cues, maintenance action and dominant medium specific to the place. Lake, soil, public street and industrial interior must remain visually distinct. Interpretive order can be horizontal, vertical or branched if the scene requires it. Do not impose the coast's flat roof, equal compartments, wind marks or water strip on another plate. A repeated visual style must not suggest a common technology, measured scale or operating result.

## HF-01 migration brief — first

Source: [canopy / old-wall section](../assets/phase17d/hf01/hf01_canopy_old_wall_section.svg).

**Keep:** retained masonry and lintel; branching/sloping canopy support; replaceable cassette and open position; walkable service rib; reachable attachment/interface; maintenance clearance and public route; separate data/optical and electrical/service paths; an actual break before the unconnected neighbor.

The old/new section and the missing cassette are already the strongest relationships. A compact label strip can free the drawing from the current large leaders and explanatory blocks. Replace the stick figure with a working silhouette and soften the heavy structural bars without erasing their hierarchy. Shade/daylight remains a qualitative cue, not a quantified optical diagram.

**Dominant section:** inherited wall → serviceable canopy and open cassette position → inhabited route beneath → unconnected neighbor. Preserve the neighbor even if it receives less area. The proposed title is “How the canopy meets the old street.”

| Key | HTML explanation to preserve |
| --- | --- |
| 01 Existing wall | Older masonry remains distinct from proposed attachments; suitability is unresolved. |
| 02 Replaceable canopy | A cassette can be removed and a position left open; the drawing assigns no verified optical or cooling performance. |
| 03 Service rib + joints | Walkable access and reachable connections shape the roof; this is not a lifting or safety procedure. |
| 04 Separate services | Distinguish optical/data from electrical/service paths by line pattern and short labels as well as color. |
| 05 Work + public passage | Maintenance clearance and the public route share the section; staffing and access agreements remain necessary. |
| 06 Unconnected neighbor | A visible interface/property break prevents the roof from implying automatic streetwide continuity. |

**Labels to relocate:** long public-route sentence, clearance explanation, repeated K/S footer and redundant “supporting system explanation” header. Keep service-type distinctions as a small line key within group 04 or HTML plus visible differentiated lines; do not silently collapse them into “utilities.”

**Second plate:** not needed for first migration. A later joint/service interface plate could explain attachment, power/data and access agreements if detail becomes too dense. It must not introduce verified joint design or electrical specifications.

**Meaning risk:** optical paths must not become measured rays; property break must not become a connected span; schematic attachment must not appear certified. Successful migration changes presentation only, with no scientific or canon change.

**Why first:** this is the homepage entry scene and its existing section has a strong, comparatively simple spatial hierarchy. It can establish reusable title/key/HTML treatment before the denser agricultural and industrial cases.

## HF-03 migration brief

Source: [field / seam / drainage section](../assets/phase17d/hf03/hf03_field_seam_drainage_section.svg).

**Current issue:** the open field occupies a narrow left portion while a large, heavily textured soil block and several building-like modules dominate. Seven top labels and three bottom boxes compete for attention. A mobile reduction risks reading as greenhouse plus ditch rather than productive landscape with a working seam.

**Dominant section:** substantial open field → selective cultivation envelope → interrupted service/contained-work seam → maintained drainage → distinct wetland edge. Widen the field's visual presence and reduce empty soil depth/pattern weight. Keep cultivation selective; no roof over the farm. A proposed title is “How the working seam meets field and water.”

| Key | HTML explanation to preserve |
| --- | --- |
| 01 Open productive field | Unroofed cultivation remains the main landscape use, with external inputs and no yield claim. |
| 02 Selective cultivation | Translucent propagation surfaces cover selected work; the envelope is a design concept, not a generic whole-farm greenhouse. |
| 03 Service + outside supply | A stopped wheeled machine, human repair, conventional delivery access and an empty/isolated seam position show interruption and dependence. |
| 04 Contained work + outward route | Opaque processing/qualification remains separate from field and water. Hold/reject storage and outward handling remain possible, without a release path into the ditch. |
| 05 Old gate + ditch | A worker clears/inspects sedimented drainage infrastructure; water and wear show a maintenance task, not treatment success. |
| 06 Wetland edge | Reeds and wetland space remain distinct from drainage hardware and contained work; no ecological outcome is shown. |

**Keep contained work on the main plate.** Its physical separation is central to understanding the future landscape. Compress its qualification logic into key 04 and a distinct hold/outward cue. Move the current bottom-box prose to HTML; put outside supply and the empty segment into the section itself.

A separate later routing plate may explain qualification, hold/reject and external dispositions. Treat downstream drainage as a separate relationship, never an implied processing outflow or treatment chain. No color change across the gate, purification symbol or closed-loop arrows.

**Mobile review:** field, folded/segmented envelope, ditch/wetland break and one human action must survive the complete 390 px presentation. Keep six concepts readable in HTML; do not squeeze seven labels into the picture. If simplification still looks like a conventional greenhouse complex, return for focused visual review before producing more plates.

## HF-04 migration brief

Source: [qualification-cell / old-hall section](../assets/phase17d/hf04/hf04_qualification_cell_section.svg).

**Current issue:** the hall/crane/cell relationship is strong, but internal room labels, heavy frames, utility lines and four large material cards ask the reader to follow both architecture and disposition logic at once. The four bays are important distinctions, not decorative colors.

**Dominant section:** retained hall/crane enclosing a removable opaque cell, empty berth, protected staffed gallery and accessible services. A proposed title is “How a process cell meets the working hall.” Preserve human inspection and rigging without making the drawing an operating procedure.

| Key | HTML explanation to preserve |
| --- | --- |
| 01 Retained hall + crane | Existing brick, floor and crane structure remain distinct from proposed equipment; no capacity claim. |
| 02 Replaceable cell | Opaque removable equipment requires human handling, access and repair; no selected process or throughput. |
| 03 Empty berth + services | A vacant/isolated position and reachable heat/water interfaces make interruption and outside utility dependence visible. |
| 04 Staffed qualification | People inspect and decide in a protected gallery; classification/acceptance does not guarantee compatibility or use. |
| 05 Separate material states | Incoming, held/rejected, conditionally qualified and outgoing residual material remain physically distinguishable. |
| 06 Outside exchange | External supplies, freight and outward residual handling remain visible; the hall is an open system. |

Replace long room labels with markers. Convert the four bottom UI-like cards into small separated bays within the physical section and preserve their distinctions in key 05. Do not merge hold/reject with qualified storage or turn every outgoing residual into a usable input. Keep heat and water differentiated by more than color.

**Recommend a second later plate if readers need the decision logic.** The main plate should explain where work happens. A later qualification/disposition plate could explain inspection, hold, rejection, conditional use and external handling. It would not be a mandatory fourth asset for this migration, and none is created now. Until separately approved, the main plate and HTML must remain complete enough to show all four dispositions and outside dependence.

## Responsive / HTML-callout strategy

Retain a whole-section image and adjacent ordered text rather than making a phone crop that removes a boundary. Number and label concepts in the same order in SVG, alt/description and HTML. Keep a short informative alt that points to the text key; the SVG's own title/description supports standalone use. Preserve keyboard focus, full-size opening and text at 200% zoom. Avoid duplicate spoken numbering if visual numbers are separately styled.

During implementation inspect native 1440 × 900 rendering and page widths 1440, 900, 560 and 390 px. Check image decoding, overflow, heading order, all callouts, contrast, full-size link and natural reading order. At phone width the physical relationship and numbered points must survive; small strip/footer lettering may defer to equivalent HTML. This audit visually inspected full-size rasterizations only; these checks are future acceptance work, not claimed completed migration QA.

Keep the SVGs vector-only and free of embedded raster textures. Current HF-02 is roughly 10 KB, a useful scale reference rather than an arbitrary byte ceiling. Keep temporary previews out of versioned production assets. Record final source/hash/size in the existing production notes when a migration is later approved.

## Migration sequence and human-review gates

1. Approve [public vocabulary and IA](public_atlas_language_ia_audit.md), then implement that bounded cleanup first. Keep existing routes and internal identifiers.
2. Produce one HF-01 migration with its matching HTML key. Review native/mobile appearance, all six relationships and claim equivalence before extending shared helpers.
3. Produce HF-03; review field dominance and absence of implied treatment/release. Accept it before starting the next migration.
4. Produce HF-04; review material separation, human qualification and external exchange. Decide separately whether a later logic plate is useful.
5. Review family consistency across all four, stable links, accessible text and Methods/provenance boundaries. Only a separate publication authorization permits deployment.
6. HF-05 remains outside this plan's implementation scope and requires a later task.

For every future migration retain a before/after concept checklist: nothing measured, nothing newly connected, no performance promoted, no governing distinction removed. Public words may change while internal E/S/K and GBI dispositions remain exactly as recorded. Do not rename `hf01_*`, `hf02_*`, `hf03_*`, `hf04_*`, phase documents, routes, branches or historical reports.
