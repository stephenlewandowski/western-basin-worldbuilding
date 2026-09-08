# Phase 12A — Vector Ecology Baseline, 2026

Status: approved execution brief; factual ecological baseline only.
Primary product: Map 38 — Vector Ecology Baseline, 2026.

## Purpose

Build a compact, source-grounded baseline for documented vector presence,
surveillance detections, habitat associations, seasonality, environmental
relationships, host ecology, and pathogen-in-vector context relevant to western
Lake Erie, the Maumee watershed, Toledo/Northwest Ohio, and immediately relevant
Michigan/Indiana interfaces.

The product is an ecology and surveillance baseline, not an infectious-disease
module.

## Spatial and temporal frame

Use the existing Western Basin analytical frame and generalized county,
watershed, shoreline/wetland, urban/container, forest/edge, and surveillance
program scales where supported. County records are not precise local
distributions. A missing record is not evidence of absence. Retain the record's
year, geographic scale, method, effort, detection status, source, and
uncertainty.

Use 2026 as the baseline label only for current/recent evidence assembled for
this module. Preserve the actual observation, publication, surveillance, or
estimate year for every record. Do not create unsupported continuous abundance
or disease-risk surfaces.

## Candidate taxa and evidence questions

Investigate, without assuming regional support:

- mosquitoes: Culex pipiens/restuans complex, Aedes albopictus, Aedes japonicus,
  and other locally documented species;
- ticks: Ixodes scapularis, Dermacentor variabilis, and other established or
  relevant species; and
- pathogen-in-vector records only where the surveillance source supports the
  vector, pathogen, method, geography, and year.

Represent documented presence, surveillance detections, habitat association,
seasonality, temperature relationship, precipitation/hydrology relationship,
wetlands/standing water, urban container habitat, host ecology, and
pathogen-in-vector context as separate qualified records.

## Mandatory distinctions

Preserve all of the following in the data model, reports, and validator:

- vector presence != vector abundance;
- pathogen detection in a vector != human-vector contact;
- human-vector contact != human infection;
- human infection != clinical disease;
- sampling effort != abundance;
- detection != establishment;
- county record != precise local distribution;
- positive vector pool != human case;
- reported human case != local transmission unless supported.

Do not infer absence from lack of surveillance, establish continuous range
boundaries from county records, or convert ecological context into individual
risk.

## Required products

- vector ecology nodes and relationships under `data/processed/`;
- a surveillance-record table retaining year, vector/species, pathogen when
  applicable, method, geographic scale, sampling effort, detection status,
  source, and uncertainty;
- a habitat/seasonality/environmental association register;
- a source registry and uncertainty register;
- `outputs/maps/systems/38_vector_ecology_baseline_2026.png`;
- `outputs/maps/systems/38_vector_ecology_baseline_2026.svg`;
- source, assumptions, findings, and QA reports under `reports/`;
- a reproducible Python builder and validator;
- an independent R validator; and
- a machine-readable working manifest and artifact check.

Do not merge incompatible surveillance programs into an abundance index.
Prefer generalized, source-supported spatial representation.

## Sources

Prefer CDC and ArboNET where appropriate; Ohio, Michigan, and Indiana public
health/vector-surveillance programs; authoritative county/local surveillance;
CDC tick surveillance/distribution; NOAA and USGS environmental data; and
peer-reviewed Midwest/Great Lakes vector ecology. Record source product,
version, URL, access date, method, scale, and limitations.

## Exclusions

No individual infection probability, disease-incidence forecast,
hospitalization, mortality, personal exposure/dose, neighborhood disease-risk
score, vulnerability/EJ score, outbreak attribution, or full infectious-disease
model. Human-case data may appear only as contextual observations and must not
be treated as evidence of local transmission without support. No 2050/2075
future range is included.

Preserve Great Black Swamp `C — HOLD / noncanonical` and the unresolved Toledo
intake-coordinate discrepancy. Do not modify accepted/frozen prior artifacts.

## Transition gate

12A must pass source/provenance, schema, semantic-boundary, spatial-scale,
negative-scope, map, deterministic-regeneration, prior-freeze, Python, and
independent R validation before 12B is finalized. Phase 12B must use 12A as an
immutable working baseline.
