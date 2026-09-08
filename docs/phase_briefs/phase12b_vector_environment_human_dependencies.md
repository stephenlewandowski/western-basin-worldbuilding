# Phase 12B — Vector / Environment / Human-System Dependencies, 2026

Status: approved execution brief; qualitative dependency layer only.
Primary product: Map 39 — Vector / Environment / Human-System Dependencies,
2026.

## Purpose

Cross-link the Phase 12A vector ecology baseline with accepted hydrology and
wetlands, climate and natural hazards, ecology and biodiversity, population and
settlement, environmental health/exposure, governance/surveillance, and
data/sensor interfaces. Describe evidence-supported relationships and project
inferences without converting a dependency into a probability, risk score, or
health outcome.

## Required relationship families

Evaluate, only where supported or explicitly labeled project inference:

- temperature -> seasonal development;
- precipitation/standing water -> mosquito habitat;
- urban containers -> Aedes habitat;
- forest/edge habitat -> tick-host interface;
- host ecology -> vector lifecycle;
- population concentration -> potential contact interface; and
- surveillance -> detection/decision interface.

Retain the direction, relationship type, evidence status, source ID, spatial
scale, temporal frame, confidence/uncertainty, and notes for every relationship.
Documented ecological relationships and project inferences must remain visibly
distinct in tables, maps, reports, and validators.

## Cross-system interfaces

Reuse, without modifying, accepted records from:

- water/hydrology, wetlands, standing-water and floodplain context;
- climate/natural-hazard temperature, precipitation, drought, and flooding
  context;
- ecology/biodiversity habitat, host, wetland, riparian, and landscape context;
- population/settlement residence, workplace, and generalized concentration
  context;
- environmental-health pathway, monitoring, control, and receptor context;
- governance actor, surveillance, monitoring, warning, and coordination context;
  and
- data/sensor observation, detection, uncertainty, and decision interfaces.

The product may show generalized system nodes and interfaces. It must not
assign exact residents to vector contact, infer exposure or infection, or make
an unsupported operational-control claim from surveillance capacity.

## Mandatory distinctions

Preserve the Phase 12A evidence ladder and add these dependency boundaries:

- physical plausibility != documented relationship;
- surveillance detection != abundance or establishment;
- population concentration != human-vector contact;
- potential contact interface != exposure, infection, or disease;
- surveillance capacity != complete detection;
- monitoring != control; and
- a positive vector pool or reported human case != local transmission unless
  supported.

Sampling effort, detection status, geographic scale, method, and uncertainty
must remain explicit. Do not merge incompatible programs into a pseudo-index.

## Required products

- a qualitative vector/environment/human dependency register;
- a relationship edge table under `data/processed/networks/`;
- a qualitative dependency matrix with `unknown` retained as unknown;
- a cross-system evidence/provenance register and uncertainty register;
- `outputs/maps/systems/39_vector_environment_human_dependencies_2026.png`;
- `outputs/maps/systems/39_vector_environment_human_dependencies_2026.svg`;
- source, assumptions, findings, and QA reports under `reports/`;
- a reproducible Python builder and validator;
- an independent R validator; and
- a machine-readable working manifest and artifact check.

Use generalized, source-supported spatial representation. No unsupported
continuous vector-abundance, contact, infection, or disease-risk surface.

## Health boundary

West Nile virus, Lyme ecology, and other vector/pathogen relationships may be
used as ecological context when supported. Do not model individual infection
probability, disease incidence, hospitalization, mortality, personal
exposure/dose, neighborhood disease-risk, vulnerability/EJ scores, or full
infectious-disease dynamics. Human-case observations are contextual only.

## Exclusions and holds

Do not implement Phase 12C, Phase 13, biosecurity, or any broader infectious-
disease module. Do not modify accepted/frozen Phase 1–11 artifacts or resolve
Great Black Swamp `C — HOLD / noncanonical` or the unresolved Toledo
intake-coordinate discrepancy.

## Transition gate

12B must pass deterministic Python and independent R validation, provenance and
citation checks, explicit negative-scope checks, 12A immutability, all prior
freeze checks, Map 39 artifact/readability checks, repository tests/build,
Markdown validation, Git/LFS checks, complete diff review, and one fresh bounded
independent review before integration. The delivered status remains
`IMPLEMENTED / VALIDATED / INTEGRATED / AWAITING SOL ACCEPTANCE`.
