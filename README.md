# Western Basin Worldbuilding

**A scientifically grounded regional-systems model and speculative worldbuilding project for Toledo, Northwest Ohio, the Maumee watershed, and western Lake Erie.**

Western Basin Worldbuilding begins with the real landscape: water, geology, ecology, infrastructure, industry, population, public health, governance, data, energy, and technology.

It then asks a worldbuilding question:

> **What kinds of places, institutions, technologies, conflicts, adaptations, and lives could plausibly emerge from this basin?**

The project is developing toward a **Regional & Systems Atlas** that combines reproducible scientific analysis with future scenarios, maps, diagrams, visual worldbuilding, fictional artifacts, characters, and narrative.

**Core principle: real geography first; fictional interpretation second.**

---

## The Project

The western Lake Erie basin is an unusually rich setting for systems-oriented worldbuilding.

Toledo sits where the Maumee River, Lake Erie, industrial manufacturing, agriculture, freight networks, energy infrastructure, drinking-water systems, wetlands, public institutions, and Great Lakes ecology intersect.

Rather than inventing a future setting first and adding scientific detail afterward, this project works in the opposite direction:

**real basin → scientific systems → cross-system dependencies → plausible futures → inhabited world**

The repository is deliberately named **Western Basin Worldbuilding** so the project is not locked to a single fictional title or aesthetic.

**Glasspunk** remains useful working terminology for the setting and visual language.

**The Glass Basin** is emerging as a possible public-facing identity for the future Atlas and fictional world, but final naming remains open.

---

## Current Status

The scientific and analytical foundation is complete through **Phase 16**.

Phases 1–13 establish the major environmental, infrastructural, demographic, health, governance, and technological systems of the basin.

**Phase 14** integrates those systems into a common Atlas ontology, layer registry, evidence vocabulary, and dependency architecture.

**Phase 15** examines emerging technologies and three qualitative technological futures for 2050 and 2075.

**Phase 16** establishes cross-system propagation rules and applies them to bounded compound-stress tests.

Phase 16 is **COMPLETE / ACCEPTED / FROZEN**.

Active phase: **NONE**. Phase 17 is **NOT IMPLEMENTED**.

### Toledo Water Works Intake Crib

The current physical crib location is **RESOLVED / VERIFIED** at
**41.699444, -83.259167** using U.S. Coast Guard Light List No. 6025,
corroborated by NOAA/NDBC and aerial imagery.

Nearby monitoring-buoy and legacy dataset coordinates remain separate
observation records and are not physical-crib geometry.

See the [Toledo intake crib coordinate-resolution report](reports/toledo_water_intake_crib_coordinate_resolution.md).

The Great Black Swamp geometry remains **C — HOLD / noncanonical**.

The next major stage is:

> **Phase 17 — Atlas Synthesis / Model-to-World Bridge**

Phase 17 shifts the project from building additional scientific machinery toward curating, visualizing, interpreting, and inhabiting the world already described by the model.

For detailed project state, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

For authoritative canon status, see [docs/canon_status.md](docs/canon_status.md).

---

## The Western Basin

The current working model uses five overlapping interpretive regions:

- **Glass City Core** — Toledo's urban, civic, industrial, water, and cultural center.
- **Maumee River Commons** — the river and watershed linking agriculture, communities, ecosystems, transportation, and Lake Erie.
- **Lake Erie Energy & Security Coast** — shoreline, islands, major water and energy infrastructure, ports, fisheries, and strategic systems.
- **Black Swamp Country** — the transformed landscape of the former Great Black Swamp, including agriculture, wetlands, drainage, biodiversity, and settlement.
- **Great Lakes Industrial Belt** — glass, automotive manufacturing, refining, materials processing, rail, freight, and industrial infrastructure.

These are **interpretive regional identities**, not jurisdictions or mutually exclusive GIS polygons.

Physical geography, infrastructure, governance, historical geography, and fictional geography remain distinct layers.

---

## What the Model Contains

The project includes interconnected work on:

water and hydrology; geology and strategic materials; energy and grid systems; compute and communications; sensors and data; cybersecurity and privacy; freight and industry; ecology and biodiversity; environmental health; nutrient and biogeochemical cycling; climate and natural hazards; governance and jurisdiction; population and settlement; vector ecology; infectious disease; emerging technology; and cross-system dynamics.

The emphasis is increasingly on **relationships between systems**, rather than treating each subject as an independent map layer.

Phase 14 defines a common Atlas architecture of **13 integrated system families** while preserving the more detailed identities and evidence structures of the underlying scientific packages.

---

## Evidence, Scenario, and World

A central design principle is keeping different kinds of knowledge visibly separate.

### Evidence / Model

Sourced, observed, or reproducibly derived information about the real western basin.

### Scenario / Plausible Future

Defensible extrapolation used to explore possible future conditions.

Scenario is **not prediction**.

### World Canon

Deliberate fictional choices belonging to the future setting.

### Sketch

Provisional creative material that has not yet entered canon.

This separation allows the scientific model and fictional world to inform one another without presenting fiction as evidence or scenario assumptions as forecasts.

---

## Technology Futures

Phase 15 examines eight broad technology families and their interactions with the basin's environmental, infrastructural, social, and governance systems.

Three qualitative future regimes are explored at 2050 and 2075:

**A — Coordinated Technological Adaptation**

**B — Uneven Networked Modernization**

**C — High Capability / High Friction Basin**

These are alternative scenario structures, not probabilities or forecasts.

Technology capability does not imply deployment, adoption, benefit, authority, or resilience.

---

## Integrated Basin Dynamics

Phase 16 moves beyond individual systems and asks how stresses can propagate across the basin.

Four principal compound cases are implemented:

- **Extreme heat + low flow + grid stress**
- **Harmful-algal-bloom / water-quality pressure + water-treatment disruption**
- **Freight / material disruption + industrial-energy constraint**
- **Infectious-disease pressure + surveillance / data-governance friction**

The stress tests trace defensible qualitative propagation pathways, system states, response options, technological modifiers, uncertainties, and explicit termination points.

They do **not** assign event probabilities, risk scores, vulnerability scores, resilience scores, economic-loss estimates, or predicted health outcomes.

Where the model cannot support another causal step, propagation terminates explicitly:

**TERMINATED — NO DEFENSIBLE CURRENT PATH**

That boundary is treated as a scientific result rather than a gap to be filled speculatively.

---

## Toward the Atlas

Phase 17 will transform the accumulated model into a reader-facing Atlas and speculative world.

The Atlas is expected to combine:

- scientific maps and regional geography
- system and infrastructure diagrams
- material and energy flows
- future maps
- dashboards and interfaces
- field sketches and notebooks
- public notices
- work orders
- advertisements
- technical documents
- institutional artifacts
- character viewpoints
- oral histories
- short narrative material

The aim is not simply to describe a future Toledo.

It is to make the western basin feel like a place whose future grew out of its **landscape, history, infrastructure, ecology, institutions, and constraints**.

The four Phase 16B narrative hooks are currently marked:

**NONCANONICAL / FUTURE ATLAS HOOK**

They are intended as controlled bridges between the scientific model and future creative work.

---

## Reproducibility and Validation

The scientific foundation is designed to remain inspectable and reproducible.

Accepted phases use combinations of:

- Python builders and validators
- independent R validation
- source and evidence registries
- provenance and lineage tracking
- artifact manifests
- independent review
- protected freeze manifests

Once accepted, scientific packages are frozen so later worldbuilding work cannot silently alter the underlying evidence base.

Detailed validation and freeze records are indexed in [reports/README.md](reports/README.md).

---

## Repository Guide

```text
assets/                 concept art and exploratory visual material
data/raw/               cached public-source material and reproducible inputs
data/processed/         validated scientific, network, scenario, and integration products
docs/                   canon, research, references, phase briefs, and architecture
metadata/               system vocabularies, sources, evidence, and scenario metadata
outputs/maps/systems/   validated analytical map pairs
outputs/figures/        system diagrams, matrices, and conceptual figures
outputs/qa/             review and QA graphics
reports/                sources, assumptions, findings, QA, reviews, manifests, and handoffs
src/python/             acquisition, construction, rendering, QA, and validation
src/R/                  independent validation and rendering
src/game/               retained Glasspunk browser-game prototype