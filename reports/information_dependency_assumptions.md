# Phase 4B Information Dependency Assumptions

Baseline: **2026**

Phase 4B is the analytical counterpart to Phase 4A. It asks which decisions
depend on which information, where uncertainty or handoff limits understanding,
and which organizations have documented authority. It is not a cyber, privacy,
AI-governance, surveillance, or future-scenario model.

## Modeling boundary

The model reuses Phase 4A's chain:

`physical system → observation → data → analysis → decision → response`

The new dependency edges describe information required by a dependent node.
They do not describe physical communication routes, software architecture,
control networks, or automated decisions. Phase 4A nodes are reused wherever
possible; no new physical stations or generalized infrastructure nodes are
created.

## Qualitative fields

- `timeliness` records only source-supported timing classes; `unknown` is used
  when a common update interval is not documented.
- `availability_requirement` is an ordinal description of how consequential the
  information is to the represented interface, not an outage probability.
- `coverage` describes point, local, regional, basin, or system-level scope; it
  does not claim complete geographic coverage.
- `uncertainty` records a documented or explicit modeling limitation, not a
  numerical error estimate.
- `authority_level` identifies the represented public organizational level, not a
  complete legal delegation analysis.
- `access_class` distinguishes public, partially public, and unknown/operational
  information. No classified status is inferred.

## Dependency semantics

- `public_observation_to_data` — a public observation or network is exposed as a
  data product.
- `forecast_input` — a source or data product is described as informing a model
  or forecast; internal ingestion is not reconstructed.
- `decision_support` / `warning_support` — information supports an organization
  or response interface without asserting a threshold or automatic trigger.
- `reporting_to_public_data` — regulated monitoring/reporting is represented as
  reaching a public data product at program level.
- `regulatory_oversight` — public information supports program oversight.
- `authority_interface` — an organization or authority is linked to its
  documented operational or regulatory response role.
- `public_context` / `operator_information` — public statistical or operating
  information supports understanding at the stated high level.

No dependency is modeled as `triggers`. No unsupported automated authority is
introduced.

## Blind-spot policy

A blind spot is recorded only when the source or the explicitly bounded model
shows a missing location, timing, handoff, authority, public-data view, status,
or uncertainty detail. Blind spots are not called vulnerabilities and are not
used to imply system failure. Periodic or self-reported data are not treated as
evidence of regulatory failure merely because their cadence is limited.

## Authority matrix policy

The authority matrix records the roles that the public sources support:
OBSERVES, ANALYZES, ADVISES, DECIDES, and OPERATES / RESPONDS. A cell can state
that a role is not specified in this baseline. That is preferable to assigning a
local agency, utility, or internal team without evidence.

## Scenario and security separation

No 2050/2075 object, fictional sensor network, attack path, exploit, credential,
sensitive topology, SCADA diagram, privacy-impact assessment, surveillance
model, or AI decision authority is included. Future scenario work remains
separate from this factual 2026 layer and requires separate approval.

The Toledo intake-coordinate discrepancy remains unresolved. The GLOS station
coordinate is an observation context only and is not promoted to canonical
physical intake geometry.
