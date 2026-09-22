# Phase 17A Prototype Findings and Production Pattern

## 1. Purpose

Phase 17A tested the bridge from the accepted Phase 1–16 systems foundation to an illustrated Atlas and, eventually, a lived future-world layer. The prototype suite tested Atlas visual architecture; visible separation of evidence, scenario, canon, and sketch; reproducible analytical figures; real-asset reconstruction; future-system concept visualization; circular/open-system representation; and motion as an optional medium.

This is a synthesis of the committed prototype outputs, contact sheets, manifests, validation reports, and current status records. It closes the prototype-and-production-pattern phase; it does not freeze final Atlas styling, change scientific data, redesign a prototype, or begin Phase 17B content. The evidence base is the committed material for [2.1](../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_validation_report.md), [2.3](../outputs/atlas/prototypes/2_3_toledo_crib/2_3_validation_report.md), [4.3](../outputs/atlas/prototypes/4_3_farm_2075/4_3_validation_report.md), and [5.3](../outputs/atlas/prototypes/5_3_industrial_exchange/5_3_validation_report.md), together with their source manifests and contact sheets. In this report, prototype status and validation statements are FACTS from those records; cross-prototype lessons are INFERENCES; and future arrangements remain SCENARIO/SKETCH material rather than canon.

## 2. Prototype findings

| Prototype | Question tested | Primary medium | What worked | What did not add value / needed correction | Durable lesson |
|---|---|---|---|---|---|
| **2.1 From Field to Lake** | Can a complex watershed-to-lake process become intuitive without implying unsupported magnitude or causality? | Accepted static MAP / SCHEMATIC / FIGURE set; animation test | The four static analytical products separate physical waterways from analytical connectors, keep constituent tracks distinct, preserve the receiving-water boundary, and maintain qualitative-only encoding. The static set is **ACCEPTED**. | The animation was technically validated but classified **DROP / CHANGE MEDIUM**. Human review found that the 32-second sequence behaved mainly as a slideshow and did not materially improve understanding beyond the accepted static figures. The MP4 is not retained as an accepted Atlas product. | Static explanation is the default product. Motion must communicate a process or state change that the static representation cannot communicate as effectively. |
| **2.3 Toledo Crib** | Can a real utility landmark evolve toward a future state without losing location, physical identity, or epistemic clarity? | PHOTO/MAP evidence → simple 3D reference reconstruction → 3D/CONCEPT retrofit → persistence FIGURE | The committed package distinguishes the verified physical crib from the legacy GLOS coordinate, keeps the current and future base geometry recognizable, and makes future additions explicit: sensing, communications, maintenance/access, inspection, service, and limited resilience interfaces. The persistence panel makes **PERSISTS / MODIFIED / ADDED** legible. | No measured dimensions were used; the reconstruction is approximate, inferred, and non-engineering. No animation was needed. The model must not be presented as a surveyed or engineered reconstruction. | Build the future on a recognizable real base. Preserve location and evidence status, then use additive overlays and persistence language rather than clean-sheet replacement. |
| **4.3 Farm 2075** | Can a regenerative future farm emerge from Western Basin constraints and functions rather than decorative solarpunk imagery? | Static MAP/CONCEPT, SCHEMATIC/FIGURE, and low-fi 3D/blockout | The synthetic farm remains a scenario/sketch, not a real parcel or forecast. Agriculture stays the primary land use while water/nutrient management, maintenance, service access, external inputs, downstream export, and open-system boundaries remain visible. Builder checks passed 16/16; visual/text-collision QA and human visual QA passed. | One surgical correction wrapped the existing final BOUNDARY bullet in 4.3C so its rendered text fit the sidebar. The correction changed no geometry or semantics. The committed scope remained static-only; no animation comparison was performed, and no yield, load, capacity, or profitability claim was added. | A simple blockout can test spatial fit, while static schematics can carry operating logic. Human visual QA remains necessary for clipping and readability even when structural checks pass. |
| **5.3 Industrial Exchange** | Can multiple systems and organizations form a plausible future network without becoming an idealized closed-loop diagram? | Static MAP/3D/CONCEPT plus SCHEMATIC/FIGURE | The synthetic district keeps selected exchange relationships qualitative and constant-width, makes external inputs and outputs visible, separates residual from recoverable resource and qualified input, and gives contracts, standards, monitoring, QA, regulation, data sharing, maintenance, and replacement a visible place. Builder checks passed 18/18; the package is accepted. | The committed scope remained static-only; no animation comparison was performed. The network is intentionally selected rather than exhaustive, and every thermal, material, and coordination interface remains scenario/sketch work rather than proof of throughput, viability, compatibility, or continuous operation. | Circularity must be drawn as gated, maintained exchange inside an open system. Show qualification and governance, not an automatic “waste becomes resource” transformation. |

Across the suite, an INFERENCE from the strongest results is that medium should match the question. Static analytical figures carried geography, process boundaries, and comparison. Simple 3D/blockout carried form, persistence, and spatial organization. Future-system panels worked when they preserved external dependencies, maintenance, and uncertainty instead of implying autonomous or self-sufficient systems.

The 4.3 and 5.3 source manifests remain producer inventories with pre-visual-QA/PENDING status fields. Their validation reports and current status surfaces record final acceptance. This is a production-hygiene distinction: a source manifest can document the build inventory without silently replacing the later acceptance decision.

## 3. Production pattern v1

The practical workflow that emerged is:

```text
SOURCE GATE
    → COMPACT PRODUCTION BRIEF
    → DIRECT BUILD
    → HUMAN VISUAL QA
    → MAXIMUM ONE SURGICAL CORRECTION PASS
    → PROPORTIONAL VALIDATION
    → COMMIT / PUSH
```

SOURCE GATE means identifying the exact accepted tables, spatial layers, assets, manifests, and status vocabulary before drawing. The gate also records the intended epistemic status, representation descriptor, relationship semantics, and explicit non-implications. It confirms that held or noncanonical geometry is excluded and that no Phase 1–16 artifact will be rewritten.

The COMPACT PRODUCTION BRIEF states one reader question, the chosen medium, the output set, the source and provenance boundary, the E/S/C/K treatment, the negative claims the image must not imply, and the acceptance checks. It is shorter than a new phase architecture document and specific enough to prevent the builder from making semantic decisions by accident.

DIRECT BUILD means using Python as the default reproducible production environment. The prototype builders show that a small source-backed script can assemble static maps, schematics, figures, contact sheets, manifests, and semantic checks without requiring a separate cinematic pipeline. Build the static explanation first. Use simple 3D or blockout geometry when form or spatial fit carries information. Blender is optional, not required by default; it becomes useful when a reusable or richer 3D asset clearly adds understanding.

HUMAN VISUAL QA is a distinct gate. Structural validation can confirm file existence, schemas, allowed vocabularies, status fields, and geometry rules, but it cannot by itself prove that a rendered label is legible, a caveat is visible, a contact-sheet thumbnail is readable, or a boundary note is not clipped. Review full-size outputs and contact sheets, including grayscale or reduced-size proofs when they are part of the package.

The correction policy is a maximum of one surgical pass after visual review. The 4.3C text-wrap correction is the model: repair the demonstrated presentation defect, preserve wording and semantics, confirm protected output hashes, and rerun the affected checks. Do not use visual QA as an invitation to redesign the prototype.

VALIDATION should be proportional to semantic risk. A multi-layer analytical figure with strict geography and constituent boundaries may need an independent second path, as in the 2.1 Python/R checks. A bounded static concept package may use builder-level checks plus explicit manifest and visual QA, as in 4.3 and 5.3. Every package still needs artifact existence, provenance/status, epistemic separation, negative-scope, and protected-artifact checks. A passing validator is not a substitute for rendered visual review.

COMMIT / PUSH follows a complete diff review. Stage only the report and intended mutable status surfaces, run Markdown and whitespace checks, verify the union of protected Phase 1–16 paths is untouched, confirm no prototype graphics or animation were regenerated, then commit and push the requested ref. The workflow closes with a fresh local/remote readback and a clean tree.

Animation is exceptional rather than default. A static figure must not be animated merely to reveal its panels sequentially. A motion pass is justified only after the static representation is understood and a specific process, state, or reconfiguration has been identified.

## 4. Medium-selection rules

Use MAP / FIGURE / SCHEMATIC when geography, relationships, comparison, or causal boundaries are the main information. These media should carry the explanation directly and should not rely on motion or 3D atmosphere to make a static idea appear more important.

Use PHOTO + 3D / CONCEPT when a real physical asset, spatial persistence, retrofit, or accumulated future needs to be understood. Keep the real reference, inferred reconstruction, and future design visibly separate.

Use 3D / CONCEPT when spatial organization itself carries meaning: whether components fit together, how an old structure persists under additions, or how a future district assembles around interfaces.

Use animation only when motion communicates something materially unavailable in the static representation, such as:

- state change;
- accumulation;
- branching;
- feedback;
- seasonal cycling;
- network switching; or
- spatial reconfiguration.

Do not animate merely to reveal static panels sequentially. The 2.1 result is the explicit production rule: technically valid motion can still be the wrong medium.

## 5. Visual Grammar findings

The following conventions proved durable within this prototype suite:

- **E / S / C / K epistemic status** remains the compact answer to what kind of claim is being shown.
- A **representation descriptor remains separate from epistemic status**. `E` or `S/K` does not by itself say whether the object is a map, figure, schematic, photograph, model, artifact, or concept.
- **Map and schematic remain visibly distinct.** Real geography should not be mistaken for explanatory abstraction.
- **Qualitative encoding discipline** remains mandatory when the sources do not support quantity. Line width, particle count, brightness, color intensity, spacing, and duration must not silently become load, severity, probability, velocity, capacity, or performance.
- **Accumulated-future / persistence logic** works: show what survived, what was modified, and what was added.
- **Maintenance visibility** is part of the representation. People, access, service, repair, replacement, inspection, and monitoring should not disappear behind the future technology.
- **Circular systems remain open systems.** Internal loops can be shown, but external inputs, outputs, residuals, discharge, markets, watershed connections, governance, labor, and replacement dependencies remain visible.
- **Scenario relationship semantics remain separate from visual intensity.** A stronger-looking line or brighter node must not promote a scenario interface into evidence or imply quantitative strength.
- Technology follows **need → function → interface → device / structure → form**. The interface and its work come before a gadget aesthetic.

Still unfrozen, and intentionally not settled by Phase 17A, are exact fonts; exact colors; the final Atlas page grid; badge placement; exact stroke weights; final book typography; final 3D rendering style; and animation conventions. These remain production choices to test later, not final Atlas style rules.

## 6. Phase 17B handoff

Phase 17A established a viable production workflow and visual grammar. Phase 17B should now translate accepted systems/scenarios into lived 2050/2075 future conditions without collapsing scenario into canon.

The Phase 17B translation grammar is:

```text
REAL PLACE
    → SYSTEM
    → FUTURE CONDITION
    → HUMAN EXPERIENCE
    → ARTIFACT
    → UNCERTAINTY
```

Retain the governing boundary:

```text
EVIDENCE constrains SCENARIO
SCENARIO informs CANON
CANON never becomes EVIDENCE
```

Phase 17B content is not begun in this transaction. The accepted Phase 17A prototypes remain prototype components rather than final Atlas page composition; final presentation details remain unfrozen; Phase 1–16 scientific baselines remain protected; and no release or tag is created.
