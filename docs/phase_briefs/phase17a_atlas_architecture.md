# Phase 17 Atlas Plans and Prototype Design

**Project:** Western Basin Worldbuilding  
**Working public/creative identity:** *The Glass Basin*  
**Phase:** 17A — Atlas Architecture  
**Status:** Planning and prototype design; Phase 17A Visual Grammar v0.3 accepted-for-use; repository implementation has not yet begun  
**Primary principle:** **REAL GEOGRAPHY FIRST; FICTIONAL INTERPRETATION SECOND.**  
**Compiled:** 2026-09-17

---

## 1. Phase 17 Purpose

Phase 17 translates the accepted/frozen Phase 1–16 scientific and systems foundation into a work that can be:

- **read** as an illustrated regional and systems atlas;
- **explored** as a web atlas and interactive model;
- **inhabited** as a coherent future world;
- **extended** through artifacts, animation, concept art, and selective 3D modeling.

The scientific repository remains authoritative for real-world evidence, model structure, provenance, and validated scenario layers. Phase 17 adds editorial synthesis and creative interpretation without rewriting the frozen scientific baseline.

The governing editorial sequence is:

> **REAL PLACE → SYSTEM → FUTURE CONDITION → HUMAN EXPERIENCE → ARTIFACT → UNCERTAINTY**

---

## 2. Product Architecture

### 2.1 Primary product — illustrated Atlas/book

**Working title:** *The Glass Basin: A Regional & Systems Atlas*

The illustrated Atlas is the design driver. It establishes:

- editorial sequence;
- visual identity;
- chapter rhythm;
- selected maps and systems diagrams;
- future-world interpretation;
- recurring places and eventually characters;
- artifacts and short narrative material;
- explicit but unobtrusive uncertainty/provenance.

The book should be readable from beginning to end as a coherent work rather than only consulted as a reference.

### 2.2 Companion product — web Atlas

The web Atlas should be designed after book prototypes reveal what benefits from interaction.

Likely functions:

- zoomable geography;
- 2026 / 2050 / 2075 switching;
- Evidence / Scenario / Canon / Sketch visibility controls;
- system-layer selection;
- deeper scientific notes and provenance;
- interactive network relationships;
- process animations;
- time sliders;
- selected 3D models;
- alternate scenario states.

The web Atlas should extend the book rather than become a generic GIS viewer.

### 2.3 Internal product — world bible

The world bible will be the authority for fictional continuity.

Initial conceptual structure:

```text
world/
├── timeline
├── places
├── institutions
├── technologies
├── characters
└── canon_register
```

This structure is conceptual only until Phase 17 is formally implemented.

### 2.4 Public GitHub website

The existing GitHub website should serve as a curated project window rather than mirror the repository.

Potential incremental public outputs:

- project overview;
- selected Atlas maps and diagrams;
- prototype spreads;
- concept art;
- milestone updates;
- animations;
- Blender renders;
- later links into the interactive web Atlas.

### 2.5 Cross-cutting visual-production tracks

These support the Atlas, web companion, and website:

- reproducible maps;
- analytical diagrams;
- concept art;
- artifacts;
- animation;
- 3D / Blender models.

---

## 3. Audience

The primary reader is a scientifically curious general audience that does not need prior familiarity with the repository.

Secondary audiences include readers interested in:

- Great Lakes and Midwestern geography;
- Toledo and Northwest Ohio;
- environmental science;
- infrastructure;
- climate adaptation;
- industrial history;
- systems thinking;
- speculative futures;
- maps and illustrated atlases;
- science fiction grounded in recognizable places.

The Atlas should support three depths of engagement:

1. **Immediate visual reading** — map, diagram, photograph, artifact, or scene.
2. **Narrative/system reading** — understandable explanation of how the place works and why it matters.
3. **Deep technical reading** — provenance, methodology, scientific assumptions, uncertainty, web companion, and repository references.

---

## 4. Temporal Architecture

### 2026 — evidence baseline

The principal factual reference state.

**Question:** *What is the basin?*

### 2050 — transition horizon

A bridge between present evidence and the lived future.

**Question:** *How did the basin begin to change?*

Useful for:

- infrastructure transitions;
- adaptation decisions;
- ecological change;
- industrial transformation;
- technology adoption;
- institutional evolution;
- incomplete projects;
- roots of later conflicts and dependencies.

### 2075 — primary inhabited world

The principal future viewpoint.

**Question:** *What did this place become, and what is it like to live there?*

The 2075 world should not simply select one Phase 15 scenario regime. Different systems and places may show different mixtures of:

- coordinated technological adaptation;
- uneven networked modernization;
- high capability / high friction.

---

## 5. Narrative Voice

### Atlas voice

A contemporary analytical/editorial voice explains:

- geography;
- science;
- history;
- system relationships;
- scenarios;
- assumptions;
- uncertainty.

### In-world voice

2075 appears through:

- public notices;
- work orders;
- sensor interfaces;
- dashboards;
- advertisements;
- correspondence;
- field notebooks;
- news excerpts;
- oral histories;
- maintenance records;
- permits;
- maps;
- personal observations.

The book should not masquerade entirely as an in-world 2075 document. Scientific provenance remains visible.

---

## 6. Epistemic Framework

The core status vocabulary is intentionally simple:

### E — Evidence / Model

Observed, documented, sourced, or reproducibly derived information about the real basin.

### S — Scenario

A plausible, evidence-constrained future state or transition.

Scenario is exploratory, not predictive.

### C — World Canon

A deliberate fictional choice established as true within *The Glass Basin*.

### K — Sketch

A provisional creative idea that may later become canon, be revised, or be discarded.

Governing direction:

> **Evidence constrains Scenario → Scenario informs Canon → Sketch explores alternatives.**

Canon never retroactively becomes scientific evidence.

### Optional representation descriptor

Epistemic status may be paired with a small representation descriptor:

- **PHOTO**
- **MAP**
- **FIGURE**
- **SCHEMATIC**
- **MODEL**
- **ARTIFACT**
- **CONCEPT**

Examples:

- `E · MAP`
- `E · SCHEMATIC`
- `S · FIGURE`
- `K · CONCEPT`
- `C · ARTIFACT`

Avoid adding separate mini-ontologies such as `K · NETWORK`, `S · SYSTEM`, or `E · BASIS` unless a later prototype demonstrates that they are necessary.

---

## 7. Phase 17 Visual Grammar v0.1

### 7.1 Epistemic status and relationship semantics are separate

E/S/C/K answers:

> **What kind of claim is this?**

Connector styles answer:

> **What kind of relationship is this?**

Do not use one graphic variable to encode both dimensions.

Relationship families likely include:

- physical/material movement;
- information/signal flow;
- dependency/requirement;
- temporal sequence;
- possible future interface.

Exact stroke and arrow styles remain to be tested.

### 7.2 Real geography vs explanatory abstraction

Real geography and system schematics should remain visibly distinct.

Recurring pattern:

```text
REAL PLACE / MAP
        ↓
SYSTEM / SCHEMATIC
```

Examples:

- Maumee watershed map → field-to-lake process schematic;
- crib location map → intake-system schematic;
- future farm plan → water/energy/nutrient schematic;
- industrial district concept → metabolism network.

### 7.3 Accumulated future / persistence silhouette

The Glass Basin should usually show:

> **what survived + what was modified + what was added**

rather than clean-sheet replacement.

Conceptual visual device:

```text
2026  ███████████
2050  ███████████ + ▒▒▒
2075  ███████████ + ▒▒▒ + ░░░
```

Potential applications:

- intake crib;
- industrial buildings;
- port infrastructure;
- farms;
- drainage systems;
- power facilities;
- neighborhoods;
- wetland-control structures.

### 7.4 Circularity and Circular Systems

Circularity should become an explicit visual-grammar concept.

The key rule is:

> **Show internal loops, but keep system boundaries and external dependencies visible.**

Circular systems should not automatically be presented as closed systems.

A circularity diagram should distinguish:

- external inputs;
- internal use;
- recovery;
- partial recirculation;
- transformation;
- outputs/products;
- residuals;
- discharge;
- external markets;
- watershed/environmental connections;
- labor, regulation, capital, replacement parts, and other institutional dependencies when relevant.

Conceptual grammar:

```text
              OUTSIDE SYSTEM
 inputs ↓                       ↑ products
          ┌─────────────────┐
          │                 │
 water ──►│   local loops   │──► residuals
 grid ───►│     ↻ ↻ ↻       │──► exports
          │                 │
          └─────────────────┘
                  │
                  ▼
              watershed
```

**Circularity is partial internal recirculation within an open system unless actual evidence demonstrates closure.**

Avoid a generic “circularity score” unless a future quantitative methodology and data justify one.

### 7.5 Residual ≠ recoverable resource ≠ usable input

For future industrial and agricultural metabolism graphics:

```text
RESIDUAL STREAM
      │
      ▼
CHARACTERIZATION / TREATMENT
      │
      ▼
RECOVERABLE RESOURCE
      │
      ▼
QUALIFIED INPUT
      │
      ▼
NEW USE
```

This prevents visually magical circular economies.

### 7.6 Maintenance remains visible

Future infrastructure should visibly require:

- people;
- access;
- pumps;
- cabinets;
- inspection;
- replacement parts;
- roads/tracks;
- pipes;
- cables;
- repair;
- cleaning;
- monitoring.

Maintenance should be part of the Glass Basin aesthetic rather than hidden.

### 7.7 Technology appears as interfaces before gadgets

Preferred design sequence:

```text
SYSTEM NEED
    ↓
FUNCTION
    ↓
INTERFACE
    ↓
DEVICE / STRUCTURE
    ↓
VISUAL DESIGN
```

### 7.8 Regenerative / solarpunk design has a function

Major ecological or regenerative features should perform identifiable work.

Potential elements:

- wetlands;
- agroforestry;
- windbreaks;
- perennial crops;
- habitat corridors;
- rainwater capture;
- greenhouse / controlled-environment systems;
- water reuse;
- distributed energy;
- bioswales;
- productive landscapes.

The setting should not become “cyberpunk + plants” or “generic solarpunk + Toledo.”

### 7.9 Western Basin visual identity

Recurring qualities include:

- Great Lakes weather, winter light, fog, storms, heat, and ice;
- working waterfronts;
- glass and reflective materials;
- concrete, steel, timber, and weathered composites;
- agricultural geometry;
- drainage infrastructure;
- wetlands and reeds;
- industrial reuse;
- visible repair;
- layered old/new systems;
- sensing and monitoring equipment;
- practical automation;
- productive ecology.

The future should often look accumulated rather than replaced.

---

## 8. Motion / Animation Grammar

Animation answers:

> **What changes, moves, propagates, cycles, or operates through time?**

The four prototype animation archetypes are:

1. **Directional movement** — *From Field to Lake*
2. **Temporal layering / transformation** — *Toledo Crib*
3. **Seasonal cycle / operating states** — *Farm 2075*
4. **Network orchestration / changing dependencies** — *Old Industry, New Metabolism*

Unless supported by quantitative data:

- speed ≠ velocity;
- particle count ≠ mass;
- brightness ≠ severity;
- pulse frequency ≠ probability;
- line width ≠ flow magnitude;
- animation duration ≠ real-world duration.

Animation should communicate sequence and state before quantity.

---

## 9. 3D / Blender Grammar

3D is justified where it improves understanding.

Three primary roles:

### 9.1 Reference reconstruction

Example: **Toledo Water Works Intake Crib**

Purpose: understand real physical form.

### 9.2 Spatial feasibility / blockout

Example: **Farm 2075**

Purpose: test whether landscape components physically fit together.

### 9.3 Modular future-system assembly

Example: **Old Industry, New Metabolism**

Purpose: build reusable infrastructure components and test spatial relationships.

Later cinematic/atmospheric rendering is optional and should follow explanatory use.

Preferred workflow:

> **REAL REFERENCE → ANALYTICAL UNDERSTANDING → FUTURE DESIGN → 3D MODEL → RENDER / ANIMATION / WEB OBJECT**

---

## 10. Book / Web / World Bible Relationship

```text
              SCIENTIFIC REPOSITORY
          evidence / models / provenance
                       │
                       ▼
                 SCENARIO LAYER
                       │
                       ▼
                  WORLD BIBLE
            canon / continuity / state
                       │
                ┌──────┴──────┐
                ▼             ▼
         ILLUSTRATED       WEB ATLAS
             ATLAS          COMPANION
        curated journey    exploration
                │             │
                └──────┬──────┘
                       ▼
                PUBLIC WEBSITE
             selected strong outputs

Cross-cutting production:
maps • diagrams • concept art • artifacts • animation • 3D
```

Authority:

- scientific repository → science/model authority;
- world bible → fictional canon authority;
- illustrated Atlas → curated narrative synthesis;
- web Atlas → exploratory interface;
- website → public presentation.

---

## 11. Chapter Architecture

### Part I — The Basin

**0. How to Read the Basin**  
Epistemic framework, time horizons, visual language, uncertainty.

**1. The Western Basin**  
Physical geography, geology, lake, river, settlement, historical landscape, macroregions.

**2. Water Makes the Basin**  
Hydrology, drainage, nutrients, HABs, wetlands, water supply, intake infrastructure.

### Part II — The Working Basin

**3. Glass City Core**  
Urban Toledo as civic, industrial, infrastructural, and cultural nexus.

**4. Maumee River Commons**  
Agriculture, river communities, nutrients, ecology, logistics, flooding.

**5. Great Lakes Industrial Belt**  
Glass, automotive, refining, materials, freight, industrial ecology.

**6. Lake Erie Energy & Security Coast**  
Energy, ports, shorelines, islands, lake infrastructure, navigation, fisheries.

**7. Black Swamp Country**  
Drainage, agriculture, wetlands, biodiversity, settlement, ecological memory.

### Part III — The Invisible Basin

**8. Networks That Watch and Decide**  
Sensors, weather, buoys, compute, communications, AI, cyber, privacy, surveillance.

**9. Governing the Basin**  
Utilities, local government, state/federal roles, industry, coordination, authority.

**10. The Living Basin**  
Population, health, environmental exposure, biodiversity, vectors, infectious disease.

### Part IV — The Glass Basin

**11. Three Futures**  
Phase 15 technology/scenario regimes.

**12. When Systems Collide**  
Phase 16 compound-stress cases.

**13. 2075: The Glass Basin**  
The synthesized future state.

**14. Lives in the Basin**  
Characters, occupations, routines, relationships, documents, perspectives.

**15. What We Do Not Know**  
Uncertainty, alternate futures, holds, unresolved questions, model boundaries.

---

## 12. Chapters 1–7 Candidate Spread Matrix

### Chapter 1 — The Western Basin

- **1.1 Why Here?** — regional synthesis of water, geology, settlement, climate.
- **1.2 Five Basins Within the Basin** — five interpretive macroregions.
- **1.3 A Landscape Re-engineered** — wetlands, drainage, agriculture, cities.

### Chapter 2 — Water Makes the Basin

- **2.1 From Field to Lake**
- **2.2 The Basin Metabolism**
- **2.3 The Toledo Crib**
- **2.4 A Bloom Is Not a Single Cause**

### Chapter 3 — Glass City Core

- **3.1 Toledo as an Urban Organism**
- **3.2 A Day of Invisible Infrastructure**
- **3.3 Old Glass / New Glass**
- **3.4 The Accumulated City**

### Chapter 4 — Maumee River Commons

- **4.1 A Working Watershed**
- **4.2 Wetland as Infrastructure**
- **4.3 Farm 2075**
- **4.4 The River Changes With the Season**

### Chapter 5 — Great Lakes Industrial Belt

- **5.1 What Toledo Makes**
- **5.2 Materials Do Not Move Themselves**
- **5.3 Old Industry, New Metabolism**
- **5.4 Luckey–Elmore: Memory in the Landscape**

### Chapter 6 — Lake Erie Energy & Security Coast

- **6.1 Power at the Water’s Edge**
- **6.2 Port, Plant, Lake**
- **6.3 Winter Lake / Summer Lake**
- **6.4 Coast 2075**

### Chapter 7 — Black Swamp Country

- **7.1 The Swamp That Is and Isn’t There**
- **7.2 The Drainage Machine**
- **7.3 Productive Wetlands**
- **7.4 Insect Country**

---

## 13. Production-Class Summary

Primary production classes:

- `reuse existing`
- `redraw/synthesize`
- `new analytical figure`
- `concept art`
- `animation`
- `3D`

General finding:

- direct reuse of frozen scientific artifacts should be relatively rare;
- most Atlas products should redraw/synthesize accepted source material;
- reproducible analytical graphics should remain data-driven;
- concept art begins where the project translates scenarios and constraints into lived future form;
- animation is strongest when process or state change matters;
- 3D is strongest when form, spatial feasibility, or modular infrastructure matters.

---

## 14. Four-Prototype Suite

The prototype suite tests the Phase 17 visual toolkit before broader production.

### 14.1 Prototype 2.1 — From Field to Lake

**Pipeline:** analytical figure → editorial synthesis → animation  
**Epistemic range:** E → K  
**Primary question:** Can a complex scientific process become intuitive without implying unsupported magnitude or causality?

Core scientific contract:

> Water connects the agricultural landscape of the Maumee watershed to western Lake Erie, but water, sediment, phosphorus, nitrogen, and carbon may be mobilized, transported, retained, transformed, or diverted differently before reaching receiving waters.

Second boundary:

> Delivery to western Lake Erie is not equivalent to bloom formation.

#### Proposed four-page structure

Pages 1–2:

- Western Basin locator;
- Maumee basin main flow map;
- field → drainage → tributary → river → bay → lake;
- geographic-flow grammar.

Pages 3–4:

- generalized landscape-process section;
- distinct constituent pathways;
- mobilization;
- transport;
- retention;
- transformation;
- release;
- receiving water;
- concise uncertainty boundary.

#### Animation

Directional-flow animation:

- watershed appears;
- selected runoff/drainage pathways activate;
- constituents move differently;
- some movement stops or transforms;
- receiving-water conditions are shown as separate from transport.

#### Key prohibitions

Do not imply:

- every rainfall event produces runoff;
- every nutrient source reaches the lake;
- all constituents behave identically;
- wetlands have a fixed universal efficiency;
- routing edges are always literal channels;
- animation speed represents real velocity;
- particle count represents mass;
- nutrient delivery automatically produces HABs.

---

### 14.2 Prototype 2.3 — Toledo Crib

**Pipeline:** evidence/reference → system diagram → 3D reference model → future design  
**Epistemic range:** E → S/K  
**Primary question:** Can a real landmark evolve into the future without losing epistemic clarity or regional identity?

Core contract:

> The Toledo Water Works Intake Crib is a real offshore utility landmark embedded in a larger drinking-water and monitoring system. Future adaptation may be explored, but present infrastructure, nearby monitoring assets, system interpretation, and 2075 design remain visibly distinct.

#### Evidence anchor

Physical crib:

- verified current position: **41.699444, -83.259167**;
- USCG Light List No. 6025;
- archived reference image retained for visual development.

Nearby monitoring assets are separate entities and should not be conflated with the crib.

#### Proposed spread

Pages 1–2:

- current photograph;
- verified location;
- lake-context map;
- current structure silhouette;
- nearby monitoring points.

Pages 3–4:

- high-level intake sequence;
- separate information/monitoring sequence;
- future functional overlay;
- current structure remains visibly persistent under speculative additions.

#### 3D strategy

**Model A:** current simplified reference massing.  
**Model B:** explanatory cutaway.  
**Model C:** 2075 design study layered onto Model A.

#### Design rule

> **2075 is layered onto 2026.**

Future functional families may include:

- environmental sensing;
- communications;
- maintenance;
- autonomous inspection interfaces;
- energy resilience;
- environmental protection;
- human operations;
- retained navigation identity.

Do not prematurely specify exact gadgets.

---

### 14.3 Prototype 4.3 — Farm 2075

**Pipeline:** scientific constraints → concept design → system illustration → 3D environment  
**Epistemic range:** S → K  
**Primary question:** Can regenerative/solarpunk elements emerge plausibly from Western Basin systems rather than being decorative?

Core contract:

> Farm 2075 is a synthetic future working landscape assembled from documented Western Basin hydrology, nutrient dynamics, ecology, climate pressures, energy dependencies, agricultural functions, and plausible technological adaptations. It is not a forecast.

#### Synthetic setting

**Western Basin Farm Unit 2075**  
Maumee River Commons / Black Swamp Country interface.

Not an actual parcel.

#### Potential components

- conventional productive field blocks;
- perennial/agroforestry strips;
- controlled drainage;
- restored/constructed wetland cell;
- ditch/riparian vegetation;
- greenhouse / controlled-environment cluster;
- solar canopy / distributed energy;
- operations and repair yard;
- water storage/reuse;
- sensing and communications;
- habitat/pollinator corridors;
- road/logistics access.

#### Design rules

- farming remains the primary land use;
- ecological systems do work;
- greenhouses complement rather than automatically replace field agriculture;
- distributed energy does not imply grid independence;
- automation does not eliminate human work;
- maintenance remains visible;
- internal loops remain connected to external systems.

#### 3D blockout

Model only broad spatial components initially:

- flat terrain;
- fields;
- ditch;
- wetland;
- windbreaks;
- road;
- operations building;
- greenhouse volumes;
- solar canopy;
- water tank;
- control structures.

Primary question:

> **Does the system physically fit together?**

#### Animation

Seasonal operational cycle:

- spring runoff;
- early summer production;
- late-summer heat/water demand;
- autumn harvest/logistics;
- winter greenhouse/energy operation.

---

### 14.4 Prototype 5.3 — Old Industry, New Metabolism

**Pipeline:** cross-system analytical synthesis → scenario diagram → future industrial concept  
**Epistemic range:** E + S → K  
**Primary question:** Can multiple systems and organizations form a plausible future network without becoming an idealized circular-economy diagram?

Core contract:

> Old Industry, New Metabolism explores how existing industrial, energy, water, freight, material, food-production, and environmental systems might develop new interfaces by 2075. The network remains open and dependent on external systems.

#### Synthetic setting

**Western Basin Industrial Exchange District, 2075**

Great Lakes Industrial Belt / Glass City Core interface.

Not a fictional claim about any specific present company.

#### Functional nodes

- industrial plant A;
- manufacturing plant B;
- materials-recovery facility;
- greenhouse/CEA cluster;
- water/wastewater interface;
- energy hub;
- freight interchange;
- ecological/stormwater edge;
- operations/data coordination layer.

#### Exchange families

- energy;
- thermal;
- water;
- materials;
- nutrients/biological resources;
- logistics;
- information/control.

#### Interface hierarchy

The graphic should distinguish:

1. documented present dependency;
2. technically plausible future interface;
3. specific Phase 17 design choice.

#### Signature exchange

Waste/rejected heat may be explored as:

```text
INDUSTRIAL PROCESS
        │
        ▼
 rejected heat
        │
        ▼
 HEAT RECOVERY
        │
        ▼
 DISTRICT THERMAL LOOP
        │
        ├──► greenhouse
        ├──► buildings
        └──► thermal storage
```

But viability depends on temperature, distance, timing, infrastructure, ownership, and maintenance.

#### Circularity rule

Do not show:

> waste → resource

as an automatic transformation.

Instead:

> residual → characterization/treatment → recoverable resource → qualified input → new use.

#### Institutional layer

Each exchange may require:

- contracts;
- pricing;
- service standards;
- maintenance responsibility;
- emergency procedures;
- data sharing;
- quality standards;
- regulation;
- liability.

Physical flow and institutional authority should remain distinct.

#### Animation

Network orchestration:

1. separate entities;
2. documented baseline dependencies;
3. candidate scenario interfaces;
4. selected sketch network;
5. one interface becomes unavailable;
6. operating state changes rather than automatic collapse;
7. zoom outward to show regional external dependencies.

End concept:

> **Connected, not closed.**

---

## 15. Prototype Testing Framework

All four prototypes should pass five gates.

### Gate 1 — Scientific fidelity

For each substantive element:

- What is the source?
- Is it E/S/C/K?
- Does the graphic imply more than the source supports?
- What does each arrow mean?
- Does size, speed, brightness, density, or line width accidentally imply magnitude or probability?

### Gate 2 — Reader comprehension

Give the prototype to readers unfamiliar with the repository.

Ask:

> What is this showing?

Then ask a few spread-specific questions.

Repeated misunderstanding matters more than numerical scoring.

### Gate 3 — Visual hierarchy

Test:

- **5 seconds** — what catches the eye?
- **30 seconds** — what is the major idea?
- **2 minutes** — can the mechanism be understood?
- **5 minutes** — are provenance and epistemic distinctions visible?

### Gate 4 — Added-medium value

A/B test:

- static;
- static + animation or 3D.

Animation should clarify process/change.

3D should clarify form/spatial relationship/mechanism.

Concept art should clarify experience and visual character.

### Gate 5 — Production viability

Ask:

- Can analytical components regenerate from data?
- Can styles propagate?
- Can assets be reused?
- Can the method scale?
- How much manual work is required?
- Can book and web share assets?

Use `PASS`, `REVISE`, or `DROP / CHANGE MEDIUM` rather than a composite numeric score.

---

## 16. Pre-production Tests for the Common Visual Grammar

Before production implementation:

1. **Monochrome test** — E/S/C/K and relationship types remain understandable in grayscale.
2. **Small-size test** — spread hierarchy and labels survive tablet/laptop scale.
3. **Five-second hierarchy test** — central idea is immediately apparent.
4. **Epistemic test** — readers can distinguish real/model/scenario/sketch.
5. **Arrow test** — movement, dependency, information, and time are not confused.
6. **No-color test** — semantics do not depend on hue alone.
7. **Static-before-motion test** — static spread stands on its own.
8. **Reduced-motion test** — animations retain an understandable static alternative.
9. **Generic-future test** — future environments remain recognizably Western Basin.
10. **Production-cost test** — effort and reusable asset value are recorded.

Do not yet freeze:

- exact colors;
- fonts;
- page size;
- grid dimensions;
- map projection conventions;
- line styles;
- arrowhead designs;
- icon set;
- exact 2050/2075 overlay styles;
- animation timing;
- final 3D render style.

---

## 17. Python and R Integration with Phase 17

The existing systems repository already uses a strong pattern:

- **Python** for acquisition, construction, rendering, and validation;
- **independent R** for validation and selected independent renders.

Phase 17 should extend that model additively rather than bypass it.

### 17.1 Principle: Atlas graphics consume frozen science

Phase 17 analytical products should generally read from:

- accepted/frozen processed tables;
- Atlas system ontology and layer registry;
- normalized relationship crosswalks;
- accepted scenario tables;
- Phase 16 propagation structures;
- validated geographic layers.

They should not rewrite the frozen scientific inputs.

The Atlas layer becomes a **presentation/synthesis pipeline** over the frozen model.

### 17.2 Python's likely Phase 17 role

Python is a strong default for:

- combining several frozen system tables into one spread-specific view;
- spatial filtering and joins;
- network/graph construction;
- relationship typing;
- Atlas metadata assembly;
- reproducible map and diagram generation;
- SVG generation;
- animation-frame generation;
- lightweight interactive-data exports;
- production manifests;
- visual-semantic validation.

Potential future conceptual structure:

```text
src/python/atlas/
    build_spread_2_1_field_to_lake.py
    build_spread_2_3_toledo_crib.py
    build_spread_4_3_farm_2075.py
    build_spread_5_3_industrial_metabolism.py
    validate_atlas_visual_semantics.py
```

This is a proposed structure only and should not be created until Phase 17 implementation is approved.

### 17.3 R's likely Phase 17 role

R should continue to provide independent checks rather than duplicate Python line for line.

Potential uses:

- independent validation of input counts and joins;
- statistical summaries where applicable;
- independent verification of scenario/evidence separation;
- graph/path/cycle sanity checks;
- reproducibility checks for quantitative panels;
- independent alternate renders for selected scientific figures;
- verification that no unsupported quantitative encoding has entered a figure.

Conceptual future structure:

```text
src/R/atlas/
    validate_spread_2_1_field_to_lake.R
    validate_spread_2_3_toledo_crib.R
    validate_spread_4_3_farm_2075.R
    validate_spread_5_3_industrial_metabolism.R
    validate_atlas_visual_semantics.R
```

Again: proposed only.

### 17.4 Circularity as graph structure, not a score

Python/R can make the circular-systems grammar analytically rigorous.

For each circularity/metabolism figure, a machine-readable table could classify every edge as:

- `external_input`
- `internal_use`
- `recovery`
- `transformation`
- `recirculation`
- `product_output`
- `residual_output`
- `discharge`
- `information`
- `dependency`
- `scenario_interface`
- `sketch_interface`

The code can then verify:

- internal loops are actually cycles in the graph;
- external inputs remain visible;
- residual outputs/discharges are not silently removed;
- scenario/sketch edges are not mislabeled as evidence;
- no connection becomes quantitative without a quantitative source;
- an open system is not rendered as a closed system;
- all Atlas edges inherit source/evidence metadata.

Useful descriptive outputs may include:

- cycle membership;
- path tracing;
- external-input inventory;
- external-output inventory;
- edge-status counts;
- unresolved-interface list.

Avoid a composite **circularity score** unless later evidence supports a meaningful quantitative definition.

### 17.5 Animation tie-in

Python can create deterministic animation states from the same edge/node tables used for static figures.

Examples:

**2.1 From Field to Lake**
- ordered pathway states;
- constituent-specific path visibility;
- retention/transformation states.

**2.3 Toledo Crib**
- present structure → system context → future overlay states.

**4.3 Farm 2075**
- seasonal operating-state table.

**5.3 Old Industry, New Metabolism**
- baseline dependencies;
- possible interfaces;
- chosen sketch network;
- degraded/alternate operating state.

This allows static and animated versions to share one source model.

### 17.6 3D / Blender tie-in

The scientific code should not automatically invent 3D geometry.

Instead Python can export **scene manifests** describing:

- object IDs;
- spatial anchors;
- epistemic status;
- functional role;
- source references;
- dimensions only where known;
- inferred/provisional flags;
- relationships to other objects.

Blender can consume those manifests while allowing creative geometry to remain explicitly sketch/scenario/canon.

Example conceptual manifest:

```json
{
  "object_id": "toledo_crib_2026",
  "status": "E",
  "representation": "MODEL",
  "coordinate_status": "verified",
  "geometry_fidelity": "simplified_reference_reconstruction",
  "future_overlay_allowed": true
}
```

For invented future farms or industrial districts, the manifest should make clear that spatial arrangement is `K`, even when component functions derive from `E` or `S`.

### 17.7 Visual-semantic validators

A Phase 17 validation layer could check rules such as:

- every plotted relationship has a relationship type;
- every future relationship has E/S/C/K status;
- E and K items are not silently merged;
- line width is not data-driven unless an explicit quantity field exists;
- animation speed is not labeled as quantitative unless supported;
- geographic coordinates are null for invented locations unless explicitly canonicalized;
- open-loop diagrams retain documented external inputs/outputs;
- held/noncanonical geography cannot appear as accepted geometry;
- present-day assets cannot inherit future attributes by accident.

This is a high-value use of code: **validate the grammar rather than merely draw it.**

---

## 18. Division of Labor

### Chat / higher reasoning

Best for:

- Atlas architecture;
- chapter logic;
- visual grammar;
- scenario → world translation;
- spread concepts;
- scientific interpretation before visualization;
- world bible design;
- characters/institutions;
- concept-art direction;
- prototype test design;
- final acceptance reviews.

### Hermes

Best for:

- exact repository inventories;
- deterministic file crosswalks;
- creating approved Markdown/CSV planning artifacts;
- path validation;
- Git transactions;
- LFS checks;
- applying accepted text;
- routine repo housekeeping.

### Codex

Best for:

- reproducible Python/R Atlas figure builders;
- animation code;
- SVG/JS interactive components;
- web-Atlas implementation;
- Atlas build/export tooling;
- Blender Python/procedural helpers;
- tests and refactoring.

### Higher reasoning priority

Use limited higher reasoning for:

1. initial design of each prototype;
2. scenario-to-2075 translation;
3. scientific QA of near-final analytical visuals;
4. Chapter 13 / 2075 world synthesis;
5. final visual-grammar freeze.

Do not spend premium reasoning on routine Git/file work, straightforward refactors, repetitive style application, or deterministic validation.

---

## 19. Phase 17A Visual Grammar v0.3 — Accepted-for-Use

**Decision:** Phase 17A Visual Grammar v0.3 is accepted as the **viable visual-language prototype** for continued Atlas development.

This is an **accepted working reference**, not a frozen final style specification.

The following concepts are accepted for use in prototype production:

- E / S / C / K as the core epistemic-status vocabulary;
- optional representation descriptors: PHOTO / MAP / FIGURE / SCHEMATIC / 3D / ARTIFACT / CONCEPT;
- strict separation of epistemic status from relationship semantics;
- explicit distinction between real geography and explanatory schematics;
- accumulated-future / persistence-silhouette treatment;
- Circularity / Circular Systems represented as partial internal recirculation within open systems;
- visible external inputs, products, residuals, discharges, watershed/environmental connections, and institutional dependencies;
- residual ≠ recoverable resource ≠ qualified usable input;
- visible maintenance, repair, access, labor, and service infrastructure;
- function → interface → device / structure → visual design;
- regenerative / solarpunk elements as functional infrastructure rather than decoration;
- animation used primarily for sequence, state, transformation, and orchestration unless quantitative evidence supports stronger encoding;
- 3D used for reference reconstruction, spatial feasibility, or modular system assembly before cinematic rendering;
- static Atlas spread remains primary; animation, 3D, and web interaction extend rather than repair the static explanation.

The v0.3 test sheet passed concept-level review for:

- 5-second hierarchy;
- E/S/C/K clarity;
- grayscale survivability;
- map-vs-schematic distinction;
- relationship-semantic separation;
- persistence treatment;
- open-system circularity;
- visible maintenance;
- four-prototype coherence.

The following remain intentionally unfrozen:

- final color palette;
- fonts;
- page size;
- page/grid system;
- exact line weights;
- exact arrowhead design;
- icon set;
- final map projection conventions;
- final 2050/2075 overlay styling;
- animation timing;
- final 3D rendering style.

Accepted reference assets from the Chat prototype process:

```text
phase17A_visual_style_test_sheet_v0_3.svg
phase17A_visual_style_test_sheet_v0_3.png
phase17A_visual_style_test_sheet_v0_3_grayscale.png
phase17A_visual_style_test_sheet_v0_3_50pct.png
phase17A_visual_style_test_sheet_v0_3_grayscale_50pct.png
```

These files are not yet repository artifacts until explicitly added in a bounded repository transaction.

---

## 20. Phase 17A Completion Criteria

17A should eventually produce:

1. accepted Atlas design brief;
2. chapter matrix;
3. visual-language specification;
4. epistemic-label specification;
5. minimal world-bible schema;
6. prototype-spread shortlist;
7. Phase 1–16 → Atlas content crosswalk;
8. animation/3D candidate shortlist;
9. prototype test results;
10. Phase 17B handoff.

---

## 21. Current Prototype Acceptance Goal

The prototype suite succeeds if the same visual system can:

- explain a watershed process;
- document and evolve a real utility landmark;
- invent a plausible regenerative farm;
- describe a future industrial exchange network;

while readers can always distinguish:

- what is real;
- what is modeled;
- what is scenario;
- what is provisional design;
- and eventually what becomes world canon.

---

## 22. Next Recommended Steps

The single-page visual-style test sheet has been completed and **v0.3 is accepted-for-use**.

The next active design/production-planning priority is:

> **Prototype 2.1 — From Field to Lake**

Production planning should establish:

- exact source inputs and remaining inventory questions;
- target static figures;
- animation state model;
- visual-semantic validation rules;
- independent R review points;
- output naming and additive repository boundaries;
- handoff boundary between Chat design and Codex implementation.

Hermes should be used only for the bounded deterministic repository inventory / archival transaction once the production plan is accepted.

Codex should not begin implementation until the exact Phase 2.1 source inventory and output contract have been verified.

---

## 23. Current Boundaries and Holds

- Phase 1–16 scientific baseline remains accepted/frozen.
- Phase 17 is planning/prototyping only until formally implemented.
- Great Black Swamp geometry remains **C — HOLD / noncanonical**.
- The current physical Toledo Water Works Intake Crib coordinate is resolved/verified at **41.699444, -83.259167**; nearby monitoring and legacy dataset coordinates remain separate entities.
- No release/tag should be created merely for Phase 17 planning.
- No scientific baseline should be altered to make an Atlas graphic easier to produce.

---

## 24. Prototype 2.1 Production Plan — From Field to Lake

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
