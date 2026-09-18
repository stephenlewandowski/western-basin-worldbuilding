# Prototype 2.1 — From Field to Lake Production Plan

Extracted from `Phase17_Atlas_Plans_and_Prototypes_v0_2.md`.

## Production Plan

### 24.1 Prototype objective

**Prototype:** 2.1 — *From Field to Lake*  
**Chapter:** 2 — Water Makes the Basin  
**Primary production class:** new analytical figure + redraw/synthesize  
**Digital extension:** animation  
**Primary epistemic state:** E — Evidence / Model, with editorial synthesis that remains explicitly non-predictive  
**Primary design question:** Can the Atlas explain geographic and biogeochemical transport clearly without implying unsupported quantity, travel time, causality, or inevitability?

Scientific contract:

> Water connects the agricultural landscape of the Maumee watershed to western Lake Erie, but water, sediment, phosphorus, nitrogen, and carbon may be mobilized, transported, retained, transformed, or diverted differently before reaching receiving waters.

Boundary:

> Delivery to western Lake Erie is not equivalent to bloom formation.

### 24.2 Known exact repository inputs

The following exact paths have already been identified in the Phase 17 matrix and should be treated as the initial required source set:

```text
outputs/maps/systems/02_maumee_nutrient_network.png
outputs/maps/systems/26_biogeochemical_nutrient_flux_system_2026.png

data/processed/networks/biogeochemical_flux_edges.csv
data/processed/networks/huc12_routing_current.csv
data/processed/networks/water_system_nodes.csv
data/processed/networks/water_system_edges.csv
data/processed/networks/biogeochemical_system_nodes.csv

reports/water_system_phase1_handoff.md
docs/phase_briefs/phase8a_biogeochemical_nutrient_flux_baseline.md
docs/phase_briefs/phase8b_biogeochemical_dependencies_controls.md
```

Supporting accepted context likely needed during implementation:

```text
outputs/maps/systems/01_water_baseline_2026.png
outputs/maps/systems/04_lake_erie_hab_intake_dependency.png
outputs/maps/systems/27_biogeochemical_dependencies_controls_2026.png
```

The three existing PNG products are **visual/scientific references**, not preferred analytical inputs when equivalent processed tables or spatial layers are available.

### 24.3 Required pre-Codex inventory transaction

Before implementation, Hermes should deterministically inspect the canonical repository and return:

1. current HEAD and clean-worktree state;
2. exact schemas / column names for:
   - `biogeochemical_flux_edges.csv`;
   - `huc12_routing_current.csv`;
   - `water_system_nodes.csv`;
   - `water_system_edges.csv`;
   - `biogeochemical_system_nodes.csv`;
3. exact processed spatial/geographic file(s) used by the accepted Phase 1 water maps for:
   - Western Basin / study-area geometry;
   - HUC / watershed geometry;
   - physical river / flowline geometry;
   - Maumee Bay / western Lake Erie receiving-water context;
4. exact field(s) distinguishing physical waterways from analytical connectors / routing relationships;
5. exact evidence/provenance/status fields already present on the biogeochemical and water-system tables;
6. exact constituent vocabulary used for phosphorus, nitrogen, carbon, water, sediment if sediment is supported;
7. whether any existing source table already encodes retention / transformation / release semantics;
8. exact frozen-artifact boundaries relevant to these inputs;
9. confirmation that no Great Black Swamp held geometry is required for Prototype 2.1;
10. no file changes.

If an exact processed geographic source cannot be identified, stop and report the gap rather than inventing a path or deriving geometry from a rendered PNG.

### 24.4 Proposed additive implementation paths

These are provisional until repository conventions are inspected:

```text
src/python/atlas/build_spread_2_1_field_to_lake.py
src/python/atlas/validate_spread_2_1_field_to_lake.py
src/R/atlas/validate_spread_2_1_field_to_lake.R

outputs/atlas/prototypes/2_1_from_field_to_lake/
```

Likely output products:

```text
2_1a_geographic_flow_map.svg
2_1a_geographic_flow_map.png

2_1b_process_schematic.svg
2_1b_process_schematic.png

2_1c_constituent_pathways.svg
2_1c_constituent_pathways.png

2_1_animation_state_manifest.csv
2_1_animation_preview.mp4 or .gif
2_1_source_manifest.csv
2_1_validation_report.md
```

Actual paths and media format should follow existing repository conventions once inspected.

### 24.5 Target static figures

#### Figure 2.1A — Geographic pathway map

**Purpose:** answer **Where does the connected watershed-to-lake pathway occur?**

Required visual content:

- Western Basin / Great Lakes locator as needed;
- Maumee watershed context;
- physical waterways / tributary structure at suitable simplification;
- Maumee River;
- Maumee Bay;
- western Lake Erie receiving-water context;
- Toledo as a geographic anchor where appropriate;
- physical geographic flow visually distinct from analytical connectors.

Status:

> **E · MAP**

The figure must not encode nutrient quantity through line width unless a validated quantitative source explicitly supports it.

#### Figure 2.1B — Landscape-to-lake process schematic

**Purpose:** answer **What kinds of processes can occur between field and receiving water?**

General sequence:

```text
LANDSCAPE / FIELD
        ↓
DRAINAGE / SMALL CHANNEL
        ↓
TRIBUTARY
        ↓
MAUMEE RIVER
        ↓
MAUMEE BAY
        ↓
WESTERN LAKE ERIE
```

Process vocabulary may include, only where supported:

- mobilization;
- transport;
- retention;
- transformation;
- release;
- receiving water.

Status:

> **E · SCHEMATIC**

This is a generalized explanatory abstraction, not one mapped farm or one measured event.

#### Figure 2.1C — Constituent-pathway comparison

**Purpose:** prevent water, phosphorus, nitrogen, carbon, and any supported sediment pathway from being visually collapsed into one generic flow.

Each constituent track should inherit source terminology and should show only relationships supported in the accepted tables.

Status:

> **E · FIGURE**

No implied ranking, load magnitude, residence time, or universal efficiency.

#### Figure 2.1D — Receiving-water boundary inset

**Purpose:** make the HAB causal boundary explicit.

Concept:

```text
watershed delivery
        +
receiving-water physical / chemical / biological conditions
        ↓
possible bloom-favorable conditions
```

Not:

```text
nutrient → HAB
```

Status:

> **E · SCHEMATIC**

This can remain an inset rather than a standalone figure if the four-page composition becomes crowded.

### 24.6 Four-page composition target

**Pages 1–2: From Field to Lake**

- Figure 2.1A as the primary visual;
- Western Basin locator;
- concise explanation of watershed connection;
- minimal representation key.

**Pages 3–4: What Happens Along the Way?**

- Figure 2.1B as primary explanatory schematic;
- Figure 2.1C constituent comparison;
- Figure 2.1D receiving-water boundary inset;
- concise uncertainty / non-implication note.

The static spread must fully communicate the central idea without animation.

### 24.7 Animation state table

The animation is a **process animation**, not a quantitative simulation.

| State | Working label | Visible change | Semantic meaning | Must not imply |
|---|---|---|---|---|
| A0 | Basin at rest | Base watershed, river, bay, lake | Geographic context | hydrologic inactivity or zero nutrient movement |
| A1 | Precipitation cue | Localized precipitation appears over selected landscape areas | A mobilizing condition can occur | basin-wide uniform rainfall; measured event intensity |
| A2 | Landscape pathways activate | Selected surface / drainage pathways become visible | Water/material can enter connected pathways | every field contributes; exact runoff coefficient |
| A3 | Tributary transport | Selected pathways connect into tributaries | Downstream transport sequence | measured travel time or flux |
| A4 | Maumee conveyance | Active pathways join Maumee River | Basin-scale connectivity | all material remains unchanged |
| A5 | Bay / lake delivery | Some pathways reach Maumee Bay / western Lake Erie | Receiving-water delivery can occur | all mobilized material arrives; quantitative load |
| A6 | Constituent divergence | P / N / C / supported constituent tracks behave differently; some stop, transform, or continue | Constituents are not interchangeable | known universal retention or transformation rates |
| A7 | Receiving-water conditions | Separate lake-condition panel appears | Delivery interacts with additional lake conditions | nutrient delivery automatically creates HAB |
| A8 | Static end state | Animation resolves into the full explanatory figure | Summary / reduced-motion endpoint | forecast, probability, velocity, severity |

Animation timing should be editorial and explicitly nonquantitative unless later validated otherwise.

### 24.8 Motion grammar for Prototype 2.1

Allowed motion semantics:

- movement along a path = sequence / connectivity;
- pulse = activation / interaction;
- fade or stop = retention, interruption, or termination when supported;
- shape/state change = transformation;
- separate receiving-water panel = new process domain.

Prohibited default interpretations:

- speed ≠ velocity;
- particle count ≠ mass;
- line width ≠ load;
- brightness ≠ concentration or severity;
- animation duration ≠ real travel time;
- frequency ≠ probability.

### 24.9 Validation rules

#### Source and lineage

- every plotted node / edge must trace to an accepted input or an explicitly declared explanatory abstraction;
- every Atlas relationship must have an epistemic status;
- every Atlas relationship must have a relationship semantic;
- all E items must inherit provenance from frozen/accepted source material;
- no frozen source artifact is modified.

#### Geography

- use accepted processed geography, not traced rendered PNGs;
- physical waterways and analytical connectors must remain visually and semantically distinct;
- no Great Black Swamp held polygon may enter the figure;
- no invented field or farm is mapped as a real parcel;
- generalized schematic geometry must not be presented as mapped geography.

#### Biogeochemical semantics

- phosphorus, nitrogen, carbon, water, and any supported sediment representation must remain distinct;
- retention / transformation / release appear only where source semantics support them;
- no universal wetland or buffer removal efficiency may be inferred;
- no source-to-lake pathway should imply complete delivery;
- delivery ≠ exposure ≠ bloom ≠ health outcome.

#### Quantitative encoding

Unless supported by an explicit source field:

- line width is nonquantitative;
- particle count is nonquantitative;
- animation speed is nonquantitative;
- color intensity is nonquantitative;
- path brightness is nonquantitative.

Any quantitative encoding must declare:

- source field;
- unit;
- aggregation method;
- temporal basis;
- uncertainty / limitation.

#### HAB boundary

The output must not depict:

```text
nutrient → HAB
```

as a deterministic direct edge.

Receiving-water conditions must remain a distinct process domain.

#### Accessibility / visual grammar

- E/S/C/K remains legible in grayscale;
- relationship semantics remain distinguishable without color;
- output passes 50% size proof;
- static figure communicates core message before animation;
- reduced-motion endpoint is available;
- connector arrowheads do not cover node labels;
- representation type is explicit where map/schematic ambiguity could arise.

#### Circularity / open-system relevance

Prototype 2.1 is not primarily a circularity figure, but where retention, transformation, reuse, or return pathways are shown:

- loops must not imply closed mass balance;
- external inputs and downstream outputs remain visible;
- transformation is not automatically represented as recovery;
- no circularity score is created.

### 24.10 Independent R validation role

The R review should not recreate the Python rendering line for line.

It should independently verify:

- source row counts used by the prototype;
- node / edge inclusion criteria;
- constituent vocabulary;
- physical-vs-analytical relationship classification;
- provenance/status inheritance;
- absence of unsupported quantitative visual encodings;
- path/cycle logic where used;
- absence of held Great Black Swamp geometry;
- static output manifest consistency.

If a quantitative panel is later introduced, R should independently recompute the summarized values from the frozen source table.

### 24.11 Chat → Hermes → Codex handoff boundary

#### Chat owns

- scientific/editorial contract;
- spread composition;
- E/S/C/K semantics;
- visual grammar;
- relationship meanings;
- animation-state semantics;
- what the figure must not imply;
- acceptance criteria;
- final scientific and creative review.

Chat may refine the visual design but should not silently change the frozen source model.

#### Hermes owns the pre-implementation repository inventory

Hermes should:

- inspect exact source paths and schemas;
- identify the canonical processed geographic inputs;
- confirm frozen boundaries;
- confirm intended additive output paths;
- return a deterministic inventory;
- make **no scientific or creative decisions**.

Initial inventory should be read-only.

#### Codex owns implementation

Codex may:

- create additive Phase 17 prototype scripts;
- load accepted/frozen data;
- construct the static figures;
- construct animation state data;
- render static and motion outputs;
- add automated validation;
- add independent-R hooks/tests;
- generate source/provenance manifests.

Codex must not:

- modify Phase 1–16 frozen inputs;
- invent missing geographic sources;
- infer unsupported quantitative weights;
- decide which uncertain relationship should become Scenario or Canon;
- convert a Sketch into Canon;
- replace the accepted E/S/C/K grammar;
- map Great Black Swamp held geometry as accepted;
- introduce a direct deterministic nutrient → HAB causal edge.

If implementation reveals a scientific or design ambiguity, stop and return the ambiguity to Chat rather than resolving it creatively in code.

### 24.12 Proposed implementation acceptance gate

Prototype 2.1 can advance from implementation to reader testing only if:

1. deterministic Python build passes;
2. independent R validation passes;
3. source/provenance manifest is complete;
4. `git diff --check` and project-specific checks pass;
5. no frozen artifact changed;
6. static full-size figure passes scientific review;
7. grayscale and 50% proofs pass;
8. animation state semantics pass scientific review;
9. static-before-motion test passes;
10. a nontechnical reader can state the core message without collapsing the process into “farm nutrients flow directly to the lake and cause HABs.”

---

## 25. Immediate Handoff Sequence for Prototype 2.1

**Current state:** production plan drafted in Chat; implementation not yet authorized.

Recommended sequence:

```text
CHAT
accept 2.1 production specification
        ↓
HERMES
read-only exact source/schema/geography inventory
        ↓
CHAT
resolve any source or semantic gaps
        ↓
CODEX
implement static prototype + validators
        ↓
CHAT
scientific / visual review
        ↓
CODEX
implement animation from accepted state table
        ↓
CHAT
prototype acceptance + reader-test preparation
```

This sequence keeps higher reasoning focused on scientific meaning and visual communication while using deterministic agents for inventory and implementation.

---

# Inventory Resolution Addendum — Prototype 2.1

**Status:** Source gate passed; implementation remains unauthorized until the durable Phase 17A brief is added to the repository and explicitly approved.

## Inventory decision

The Hermes read-only inventory identifies all critical scientific and geographic inputs and reports no source gap. The repository remained clean at commit `13ce67e099ef0e0f5af2acf6c2994473141deaf1`.

## Locked source decisions

### Canonical geography

Use `data/processed/glasspunk_base.gpkg`.

Use `hydrography_physical` for rendered physical waterways. Use `water_watersheds_huc8` and `water_subwatersheds_huc12` for watershed context, and `water_lake_erie` for western Lake Erie receiving-water context.

`hydrography_network_connectors`, `routing_inferred_unresolved`, and nonphysical HUC routing edges may inform topology but must not be rendered as literal channels.

### Routing discriminator

`huc12_routing_current.csv` provides `physical_geometry`.

- `physical_geometry=True` may correspond to physical-channel relationships.
- `physical_geometry=False` must never be styled as a physical stream.

### Maumee Bay

No dedicated accepted Maumee Bay polygon exists. Prototype 2.1 will represent Maumee Bay as a **labeled receiving-water / nearshore interface within accepted Lake Erie geometry**, not as invented standalone geometry.

### Toledo intake

Prototype 2.1 does **not** require the physical Toledo intake as a mapped endpoint. The intake is reserved for Prototype 2.3.

If Toledo is shown on 2.1, it functions only as a geographic/civic anchor.

Do not use the legacy GLOS `glos_crib` coordinate as physical crib geometry.

### Constituent tracks

Water is the carrier/context.

Separate analytical tracks may be shown for:

- phosphorus (`P`);
- nitrogen (`N`);
- carbon / organic matter (`C`, `soil_carbon`, `organic_matter`);
- sediment (`sediment`).

`HAB_context` is a modifier/context token, not a constituent.

Carbon presentation must not imply a greenhouse-gas inventory.

### Process vocabulary

Phase 17 may normalize existing source strings into the following Atlas-facing categories without altering Phase 1–16 source tables:

| Atlas category | Source relationship terms |
| --- | --- |
| Mobilization | `mobilized_from`, `mobilized_by`, `source-to-mobilization`, `landscape_mobilization` |
| Transport | `transported_by`, `hydrologic_transport`, `river_delivery` |
| Retention / transformation | `retained_or_transformed_by`, `wetland_retention`, `transformed_by`, `riparian_transformation`, `soil_carbon_partitioning` |
| Delivery | `delivered_to`, `receiving_delivery`, `particulate_delivery` |
| Discharge | `discharged_to` |
| Receiving-water response/context | `ecological_interface`, `ecological_response_interface`, accepted inferred HAB-response relationship |

Do **not** introduce a separate `release` category unless a source or later approved derivation supports it.

### Quantitative encoding

`biogeochemical_flux_edges.csv` records `quantity_status = unknown quantity` for all 24 rows. Therefore Prototype 2.1 v1 is **qualitative**.

Line width, particle count, animation speed, path brightness, and color intensity must not encode load, concentration, velocity, probability, severity, or travel time.

### HAB boundary

No accepted source contains a deterministic `nutrient → HAB` pipe.

Show nutrient delivery and receiving-water physical/chemical/biological conditions as separate stages. The output may state that these conditions can contribute to bloom-favorable conditions, but must not imply inevitable bloom formation.

### Great Black Swamp

No held Great Black Swamp geometry is required or permitted in Prototype 2.1.

## Required implementation inputs

```text
data/processed/networks/biogeochemical_flux_edges.csv
data/processed/networks/biogeochemical_system_nodes.csv
data/processed/networks/biogeochemical_dependency_edges.csv
data/processed/networks/huc12_routing_current.csv
data/processed/networks/water_system_nodes.csv
data/processed/networks/water_system_edges.csv
data/processed/glasspunk_base.gpkg

reports/physical_hydrography_source_manifest.json
reports/physical_hydrography_reconciliation.md
docs/canon_status.md
reports/toledo_water_intake_crib_coordinate_resolution.md
```

Optional scientific/editorial context:

```text
reports/water_system_phase1_handoff.md
reports/water_system_sources.md
docs/phase_briefs/phase8a_biogeochemical_nutrient_flux_baseline.md
docs/phase_briefs/phase8b_biogeochemical_dependencies_controls.md
metadata/atlas_layers.yml
metadata/atlas_systems.yml
metadata/atlas_evidence_vocabulary.yml
metadata/atlas_relationship_vocabulary.yml
data/processed/analysis/biogeochemical_quantitative_fluxes.csv
```

Existing maps 01/02/04/26/27 are **visual references only** and must not be traced for geometry.

## Static-production gate

Codex implementation should begin with static outputs only:

1. **2.1A Geographic Pathway Map — `E · MAP`**
   - watershed context;
   - physical waterways from accepted geometry;
   - Maumee River;
   - labeled Maumee Bay / nearshore interface;
   - western Lake Erie;
   - optional Toledo geographic anchor;
   - no quantitative line-width encoding.

2. **2.1B Landscape-to-Lake Process Schematic — `E · SCHEMATIC`**
   - field/landscape → drainage/channel → tributary → Maumee River → bay/nearshore interface → western Lake Erie;
   - process labels only from the approved normalized mapping.

3. **2.1C Constituent Pathway Comparison — `E · FIGURE`**
   - water context plus separate P, N, carbon/organic-matter, and sediment pathways;
   - no common pathway should imply identical behavior.

4. **2.1D Receiving-Water Boundary Inset — `E · SCHEMATIC`**
   - watershed delivery + receiving-water conditions → possible bloom-favorable conditions;
   - no direct deterministic nutrient → HAB edge.

5. **Source manifest and validation report**
   - source paths;
   - source fields;
   - relationship semantics;
   - epistemic status;
   - any derived Atlas-facing process category;
   - confirmation of nonquantitative styling.

**Animation remains gated until Chat accepts the static figures.**

## Validation refinements after inventory

The validator must explicitly test:

- all rendered physical channels originate from `hydrography_physical` or another accepted physical-geometry source;
- no `physical_geometry=False` routing relationship is rendered as a stream;
- no Great Black Swamp geometry enters the build;
- no standalone Maumee Bay polygon is invented;
- no physical intake geometry is added to 2.1;
- all constituent labels map to accepted source tokens;
- `HAB_context` is never treated as a constituent;
- no `release` process appears unless separately justified;
- all 2.1 flow styling is qualitative unless an explicit approved quantitative field is introduced later;
- no deterministic nutrient → HAB edge exists in output data or figure metadata;
- source files remain byte-for-byte unchanged.

## Handoff decision

**Source gate: GO.**  
**Implementation gate: HOLD pending durable Phase 17A brief + explicit authorization.**

Recommended next repository transaction:

1. Add the accepted Phase 17A planning brief and Visual Grammar v0.3 assets as new additive files.
2. Add a durable Prototype 2.1 execution brief containing the decisions above.
3. Validate links/status.
4. Commit/push that planning transaction only.
5. Then authorize Codex to implement the static Prototype 2.1 pipeline.
