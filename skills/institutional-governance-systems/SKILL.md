---
name: institutional-governance-systems
description: "Use when analyzing factual institutional governance, jurisdiction, authority, actors, interfaces, dependencies, and coordination in environmental, infrastructure, public-health, energy, freight, or similar systems."
version: 0.2.0
author: Sol, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [governance, jurisdiction, institutional systems, authority, coordination, provenance]
---

# Institutional Governance Systems

## Purpose

Use this skill for factual institutional systems analysis involving:

- governance, jurisdiction, and authority;
- actor registries and governance interfaces;
- cross-system dependencies and coordination;
- environmental, infrastructure, public-health, energy, freight, water,
  cyber-resilience, and similar systems.

This is not a partisan-politics or election-analysis workflow. It models
institutions and system interfaces, not political preference or electoral
outcomes.

## Core rule

Model:

1. who can act;
2. who must coordinate; and
3. what evidence supports the claim.

Treat role, authority, operation, dependency, and evidence as separate data
and prose objects. A plausible institutional relationship is not a documented
relationship merely because both actors exist.

## Anti-collapse distinctions

Keep these distinctions explicit in data, prose, diagrams, maps, and review:

- regulatory authority != operational control;
- ownership != regulation;
- permitting != physical operation;
- monitoring != regulation;
- funding != authority or control;
- advisory role != binding decision authority;
- scientific information != legal decision authority;
- private operation != public control;
- a program target or incentive != an enforceable individual obligation.

Do not repair an ambiguous record by assigning a stronger role than the
evidence supports.

## Evidence discipline

Use the strongest available evidence, normally in this order:

1. statutes, regulations, and other binding legal instruments;
2. treaties, compacts, permits, and formal agreements;
3. official agency, government, or program documentation;
4. official operator, utility, port, carrier, or infrastructure-owner
   documentation;
5. official tribal or nation sources;
6. authoritative legal or institutional analysis;
7. peer-reviewed literature and other secondary sources where useful.

Label claims as `FACT`, `INFERENCE`, or `SCENARIO`. Preserve evidence
strength, uncertainty, reality/canon status, geographic scope, and the
boundary of what a source actually establishes.

### Multi-actor provenance rule

A claim involving multiple institutions needs evidence for the relationship,
role, dependency, mechanism, or coordination assertion itself. Evidence that
Actor A exists and evidence that Actor B exists do not, by themselves, prove
an A/B relationship. Add a source supporting the interaction or label the
relationship `INFERENCE` with appropriately reduced evidence strength.

## Generic data model

When structured data are used, preserve stable IDs and controlled vocabularies
for at least these concepts:

- `actors`: canonical name, actor type, jurisdictional scale, geographic
  scope, system/domain, reality status, canon status, and notes;
- `authorities`: actor, domain, role, authority type, binding/nonbinding
  status, legal or operational basis, geographic scope, scale, sources,
  evidence strength, and status fields;
- `relationships`: actors or systems, role/authority, relationship type,
  source evidence, status, and notes;
- `sources`: title, publisher, URL or document locator, source class,
  access/status notes, and provenance metadata;
- `uncertainty`: affected records, uncertainty class, statement, evidence
  boundary, and disposition;
- `dependencies`: systems and actors on both sides, roles, dependency type,
  coordination mechanism, mandatory/voluntary status, documented/inferred
  status, scale, sources, evidence, and notes;
- a qualitative matrix where useful, using labels such as `strong`,
  `moderate`, `limited`, `unknown`, and `not_applicable`.

Use stable IDs, controlled role vocabularies, evidence strength, reality/canon
status where appropriate, geographic scope, jurisdictional scale, and
binding/nonbinding distinctions. Do not create a synthetic governance score,
composite ranking, or best/worst institutional index.

Useful role vocabulary includes `regulate`, `permit`, `enforce`, `operate`,
`own`, `monitor`, `fund`, `coordinate`, `advise`, `plan`, `warn`, `respond`,
`restore`, `set_standard`, `research`, and `provide_data`. Extend the
vocabulary only with a documented project reason.

## Authority and sovereignty safeguards

Classify each actor from evidence rather than institutional appearance. Keep
sovereign governments, intertribal bodies, agencies, public utilities,
private operators, and research or monitoring bodies distinct. In particular:

- sovereign governments and intertribal bodies are not interchangeable;
- historical association, treaty context, consultation, resource interest,
  and current jurisdiction are separate fields;
- consultation is not authority unless the source establishes authority;
- public and private operation or regulation must remain separate;
- geographic or territorial claims require geographic evidence.

Do not infer a current sovereignty polygon, permit jurisdiction, or
enforcement authority from historical association, institutional
participation, or cultural affiliation alone.

## Dependency analysis

Build dependencies after the actor and authority baselines are stable. For
each edge, distinguish what crosses the boundary:

- authority;
- information;
- funding;
- permit;
- operation;
- ownership; or
- response.

Also record whether the relationship is:

- legally mandatory;
- operationally required;
- voluntary;
- advisory;
- observed;
- documented; or
- inferred.

Identify which actor acts first, which actor depends on the result, and who can
compel action when the evidence supports those claims.

Use `gap` only for a documented absence of authority. A gap is not merely:

- distributed authority;
- uncertain or overlapping responsibility;
- coordination burden;
- a monitoring limitation;
- weak project evidence; or
- voluntary rather than mandatory authority.

Unknown is not failure; overlap is not necessarily dysfunction; and
distributed authority is not absence of authority.

## Visualization discipline

Maps and diagrams must use geography with a defensible meaning. Prefer
authoritative jurisdictional areas, generalized institutional nodes, system
interfaces, and evidence-supported connectors. Do not map headquarters as
jurisdiction, vague program footprints as precise polygons, or organizational
interest as regulatory territory. No map or diagram may imply jurisdiction,
sovereignty, legal authority, ownership, or operational control unsupported by
evidence.

## Review gate

Review the complete model, not only its syntax. Specifically test for:

- regulator represented as operator;
- monitor represented as regulator;
- funder represented as controller;
- advisor represented as binding authority;
- private operator represented as government;
- incentive or target represented as mandate;
- historical Indigenous association represented as current jurisdiction;
- inference represented as legal fact; and
- a relationship supported on only one side.

Independent institutional, legal, scientific, or domain review remains
necessary even when structured validators pass.

## Generic validation

Apply only the checks relevant to the project and its structured artifacts.
When applicable, require:

- schema, stable-ID, and controlled-vocabulary validation;
- source resolution and source-to-claim consistency;
- separation of `FACT`, `INFERENCE`, and `SCENARIO`;
- separation of documented, inferred, observed, mandatory, voluntary, and
  advisory status;
- anti-collapse, sovereignty, jurisdiction, and public/private checks;
- independent institutional, legal, scientific, or domain review; and
- repository diff and provenance review when operating in a repository.

The generic core is technology-neutral. It does not require Python and R dual
validation, freeze manifests, SVG/PNG agreement, Git/LFS, or any particular
repository workflow for every invocation. A project profile may impose those
additional requirements, but it must not weaken the evidence or anti-collapse
rules above.

## Project profile

If a project profile is supplied, apply it in addition to this generic core.
Project profiles may strengthen validation, reproducibility, workflow, or
domain requirements; they must not weaken the generic evidence, provenance,
sovereignty, jurisdiction, or anti-collapse rules.

For Western Basin Phase 10 work, load and apply:

[`references/western-basin-phase10-profile.md`](references/western-basin-phase10-profile.md)

The reusable QA reference is:

[`references/governance-core-qa.md`](references/governance-core-qa.md)

The former v0.1.0 filename remains available as a compatibility pointer:

[`references/phase10-governance-qa.md`](references/phase10-governance-qa.md)
