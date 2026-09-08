# Institutional governance systems — reusable QA reference

This is a domain-neutral quality-assurance reference for institutional
governance analysis. Apply it with [`../SKILL.md`](../SKILL.md). A project
profile may add stricter workflow or reproducibility requirements, but may not
weaken this evidence discipline.

## Structured records

Use stable IDs and preserve row-level provenance. Fields marked “required”
should be present whenever that record type is used; fields marked
“recommended” should be added when material to interpretation.

### Actor fields

Recommended actor fields:

`actor_id, canonical_name, actor_type, jurisdictional_scale,
geographic_scope, system_domain, reality_status, canon_status, source_id,
evidence_strength, notes`

Do not use an actor name as a substitute for its type, scale, geographic
scope, or role. Keep sovereign government, intergovernmental body, intertribal
body, agency, municipality, public utility, private operator, regulator,
research body, monitoring body, and advisory body distinct when the
distinction affects the claim.

### Authority and role fields

Required or strongly recommended fields for authority/role rows:

`authority_id, actor_id, domain_or_system, authority_or_role,
authority_type, binding_or_nonbinding, legal_or_operational_basis,
geographic_scope, jurisdictional_scale, source_id, evidence_strength,
reality_status, canon_status, documented_or_inferred, notes`

Separate the role from the basis for the role. A mission statement may support
an institutional function without establishing a specific legal power,
territory, permit, or enforcement mechanism.

### Relationship fields

Recommended relationship fields:

`relationship_id, actor_a, actor_b, system_a, system_b, role_a, role_b,
relationship_type, mechanism, source_id, evidence_strength,
documented_or_inferred, reality_status, canon_status, notes`

### Dependency fields

Dependency rows should carry, where applicable:

`dependency_id, system_a, system_b, actor_a, actor_b, role_a, role_b,
dependency_type, coordination_mechanism, mandatory_or_voluntary,
documented_or_inferred, jurisdictional_scale, evidence_strength, source_id,
notes`

Identify the direction of dependence and the mechanism that crosses the
boundary. Do not call a relationship mandatory merely because coordination
would be useful or customary.

### Source and uncertainty fields

Source records should preserve:

`source_id, title, publisher_or_author, source_class, locator, url,
publication_or_access_date, status, notes`

Uncertainty records should preserve:

`uncertainty_id, affected_record_id, uncertainty_class, statement,
evidence_boundary, disposition, source_id, notes`

Record whether a source is current, historical, superseded, inaccessible,
secondary, or otherwise qualified. Do not silently promote a weak or stale
source to a current legal fact.

## Controlled role vocabulary

Use a controlled vocabulary appropriate to the project. A useful baseline is:

`regulate, permit, enforce, operate, own, monitor, fund, coordinate, advise,
plan, warn, respond, restore, set_standard, research, provide_data`

Roles may be extended for a documented domain need, but extensions should not
collapse legal authority, physical operation, information provision, or
financial support into one generic “controls” role.

## Evidence-strength guidance

Use the strongest source available for the exact claim. A practical evidence
ladder is:

1. binding law or formal legal instrument;
2. permit, treaty, compact, agreement, or enforceable rule;
3. official government, regulator, program, or operator documentation;
4. official source from the affected institution or system owner;
5. official sovereign, tribal, or nation source where relevant;
6. authoritative institutional or legal analysis;
7. peer-reviewed or other secondary analysis.

Evidence strength describes support for the recorded claim, not the prestige
of the institution. A strong source for Actor A's role is not strong evidence
for an Actor A/Actor B relationship unless it describes that relationship.

## FACT / INFERENCE / SCENARIO checks

For every substantive claim, ask:

- `FACT`: Is the claim directly supported by the cited evidence and bounded
  to what that evidence says?
- `INFERENCE`: Is the interpretation explicitly labeled, qualified, and
  assigned lower or appropriate evidence strength?
- `SCENARIO`: Is the claim clearly separated from the current factual
  baseline and framed as an assumption or consequence rather than a legal
  prediction?

Do not turn an inference into a fact by placing it in a table, map, diagram,
or generated report. Do not place a scenario assumption in a factual registry
without an explicit status field.

## Documented / inferred checks

`DOCUMENTED` requires evidence for the asserted role, relationship,
dependency, mechanism, or coordination. `INFERRED` is appropriate when the
relationship is analytically plausible but not directly established. Preserve
the distinction in the data, prose, visualization, and review output.

BAD:

> Agency A regulates a domain, therefore Agency A operates the infrastructure.

GOOD:

> Record regulation and operation as separate roles and identify the operator
> from independent evidence.

BAD:

> Sources prove Actor A exists and Actor B exists, therefore their relationship
> is documented.

GOOD:

> Require a source supporting the interaction, or label the edge as INFERENCE
> with reduced evidence strength.

## Relationship provenance checks

For each multi-actor claim, verify that the source supports the edge itself:

- interaction or coordination mechanism;
- role or authority exercised in the interaction;
- dependency or sequence;
- geographic or jurisdictional scope;
- mandatory, voluntary, advisory, or observed status; and
- any claim about who can compel, fund, operate, permit, or respond.

Two actor citations are not a relationship citation. If an edge has multiple
claims, use row-level sources or a clearly documented evidence boundary for
each claim.

## Anti-collapse checklist

Before delivery, inspect every table, prose section, diagram, and map for:

- regulation incorrectly emitted as operation or control;
- ownership incorrectly emitted as regulation;
- permitting incorrectly emitted as physical operation;
- monitoring, research, warning, or data provision incorrectly emitted as
  regulation or control;
- funding incorrectly emitted as authority or control;
- advice incorrectly emitted as binding decision authority;
- scientific information incorrectly emitted as legal authority;
- private operation incorrectly emitted as public control;
- a target, plan, incentive, or program objective incorrectly emitted as an
  enforceable individual mandate; and
- a qualitative matrix being turned into a synthetic governance score.

## Sovereignty and jurisdiction checklist

Verify that:

- sovereign governments, intertribal bodies, and advisory or technical bodies
  are classified separately;
- historical association, treaty context, consultation, resource interest,
  and current jurisdiction are separate fields;
- current territorial, permit, or enforcement claims have geographic and
  institutional evidence;
- participation or consultation is not treated as sovereignty or authority
  without direct support; and
- uncertainty is preserved rather than filled with a generalized polygon or
  institutional label.

## Public/private checklist

Verify that:

- public ownership is not assumed from public regulation;
- private operation is not assumed to be public control;
- public operation is not assumed to include all private systems in the same
  domain;
- a private/public seam identifies the actual contract, permit, funding,
  operating, or response mechanism; and
- the geographic and population scope of the claim is supported.

## Mapping and visualization checklist

Before publishing a map or diagram:

- confirm that each polygon, node, connector, and label has a defensible
  geographic or relational meaning;
- distinguish jurisdiction, service area, ownership, operation, monitoring,
  and program footprint;
- generalize locations when exact geography is not supported or is sensitive;
- avoid mapping headquarters as jurisdiction;
- avoid precise boundaries from vague program descriptions; and
- verify that visual hierarchy does not imply legal authority unsupported by
  the sources.

## Independent reviewer checklist

Ask an independent institutional, legal, scientific, or domain reviewer to
inspect the interpretation and provenance. The reviewer should test at least:

- regulator versus operator;
- monitor versus regulator;
- funder versus controller;
- advisor versus binding authority;
- private operator versus government;
- target/incentive versus mandate;
- historical Indigenous association versus current jurisdiction;
- inference versus legal fact; and
- one-sided evidence for a multi-actor relationship.

Record the review disposition and corrections durably. A passing schema or
validator is necessary but not sufficient for institutional correctness.

## Generic reproducibility guidance

Use deterministic builders and stable generated IDs when artifacts are built
from structured data. Keep source IDs, claim rows, report blocks, and outputs
traceable to one another. Define newline and canonical-hash policy explicitly
when hashing files. Review the complete diff and staged path list before
commit. Run the project’s available Markdown, whitespace, application, and
repository-integrity checks, but do not assume that a particular toolchain is
required by the generic core.

Preserve prior accepted or frozen artifacts when a project has them. Validate
their manifests or equivalent protection records before and after edits. Do
not normalize a protected artifact merely to satisfy a checker; distinguish
canonical-content changes from line-ending or serialization differences.
