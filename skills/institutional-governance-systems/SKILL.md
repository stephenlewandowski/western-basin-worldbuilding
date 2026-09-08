---
name: institutional-governance-systems
description: "Use when analyzing governance, jurisdiction, and authority."
version: 0.1.0
author: Sol, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [governance, jurisdiction, institutional systems, authority, coordination, provenance]
---

# Institutional Governance Systems

Use this skill for factual institutional systems analysis: actor registries,
jurisdiction and authority baselines, cross-system dependencies, governance
interfaces, and coordination maps. It is designed for environmental,
infrastructure, public-health, energy, freight, and Great Lakes-style systems;
it is not a partisan-politics or election-analysis workflow.

## Core rule

Model who can act, who must coordinate, and what evidence supports the claim.
Never collapse these distinct concepts:

- regulatory authority != operational control
- ownership != regulation
- permitting != physical operation
- monitoring != regulation
- funding != authority or control
- advisory role != binding decision authority
- scientific information != legal decision authority
- private operation != public control
- a program target != an enforceable individual obligation

Treat these as separate roles in data, prose, diagrams, and validation—not only
as a narrative caveat.

## Startup and scope control

When working in a repository:

1. Inspect Git state and remotes.
2. Read the project status, canon status, workflow guidance, current handoff,
   and active phase brief before changing files.
3. Identify accepted/frozen baselines and validate their manifests before edits.
4. Confirm the approved phase boundary. Do not implement adjacent future scope.
5. Create the durable phase brief(s) and update the handoff at the first coherent
   checkpoint, before the research package becomes difficult to reconstruct.
6. Work on an isolated branch/worktree when the repository workflow requires it.

Repository state outranks stale chat context. If a frozen factual baseline seems
wrong, stop and request review rather than silently repairing it.

## Evidence discipline

Use this evidence order unless the project specifies otherwise:

1. statutes and regulations
2. treaties, compacts, permits, and formal agreements
3. official agency or program documentation
4. official operator, utility, port, or carrier documentation
5. official tribal or nation sources
6. authoritative legal/institutional analysis
7. peer-reviewed literature and other secondary sources where useful

Label claims as FACT, INFERENCE, or SCENARIO. A source describing an agency's
mission does not, by itself, establish every legal power, local jurisdiction, or
relationship to another actor. Preserve evidence strength and uncertainty.

### Multi-actor provenance rule

A claim involving two institutions needs evidence for the relationship, not just
one source for one institution. For example, a source for USACE permitting does
not document an Ohio EPA/USACE overlap; add Ohio EPA evidence or mark the
relationship as an explicitly qualified inference and lower its evidence
strength. Row-level `source_id` values must support the row's actual claim.

Do not let a citation merely prove that both actors exist. It must support the
role, dependency, mechanism, or coordination assertion attached to the row.

## Recommended data model

Keep compact, machine-readable registries with stable IDs:

- `actors`: actor ID, canonical name, actor type, jurisdictional scale,
  geographic scope, system/domain, reality status, canon status, notes
- `authorities`: authority ID, actor ID, domain, role, authority type,
  binding/nonbinding status, legal or operational basis, geographic scope,
  scale, source ID(s), evidence strength, reality status, canon status, notes
- `relationships`: relationship ID, actor ID, system ID, role/authority ID,
  relationship type, source ID, evidence, and notes
- `sources`: source ID, title, publisher, URL or document locator, source class,
  access/status notes, and provenance metadata
- `uncertainty`: uncertainty ID, affected record(s), uncertainty class,
  statement, evidence boundary, and disposition
- dependencies: systems/actors on both sides, roles, dependency type,
  coordination mechanism, mandatory/voluntary status, documented/inferred
  status, scale, source ID, evidence, and notes
- matrix: qualitative dimensions only; use `strong`, `moderate`, `limited`,
  `unknown`, or `not_applicable`; never synthesize a governance score

Use controlled vocabularies for actor types and roles. Include institutional
scales explicitly where material: federal, state, interstate, binational,
tribal/Indigenous sovereign, county, municipal, regional, special district,
public utility, system operator, private operator, and research/monitoring body.

## Authority and sovereignty safeguards

Classify an actor by the evidence in its source. An intertribal commission is
not automatically a tribal sovereign government. Keep distinct nations distinct.
Historical occupation, treaty context, consultation, resource interest, and
current territorial or regulatory jurisdiction are different fields. Never draw a
current sovereignty polygon from historical association or institutional
participation alone; record ambiguity instead.

Similarly, distinguish municipal public-water operation from private-water
regulation. A source about private wells or private water systems must not become
a permit dependency for a municipal public-water utility without direct support.

## Cross-system dependency analysis

Build dependencies only after the baseline actor and authority registries are
stable. For every edge, identify:

- what crosses the boundary: authority, information, funding, permit,
  operation, ownership, or response
- whether the sequence is legally mandatory, operationally required,
  voluntary, advisory, or merely observed
- whether the relation is documented or inferred
- which actor acts first, which actor depends on the result, and who can compel
  action

Useful types include overlapping authority, sequential authority, split
responsibility, information/funding/permit dependency, public/private seam,
interstate or binational dependency, monitoring-without-control,
control-without-direct-observation, voluntary coordination, mandatory
coordination, emergency coordination, and advisory relationship.

Use the word `gap` only when evidence supports a documented absence of authority.
Otherwise distinguish distributed authority, unclear responsibility,
coordination burden, monitoring limitation, weak project evidence, and voluntary
rather than mandatory authority. Unknown is not failure; overlap is not
necessarily dysfunction; distributed authority is not absence of authority.

## Map and visualization discipline

Map only geography that has a defensible geographic meaning. Prefer authoritative
jurisdictional areas, generalized institutional nodes, system interfaces, and
connectors. Do not map headquarters as jurisdiction, vague program footprints as
precise polygons, or organizational interest as regulatory territory.

Maps should show relationships and decision sequences without implying a legal
conclusion that the source does not support. Do not create a composite score or
rank institutions as best/worst governed.

## Validation and reproducibility

After generation, run both a primary Python validator and an independently
implemented R validator. At minimum check:

- schemas, IDs, controlled vocabularies, required fields, and row counts
- every authority/relationship/dependency source ID resolves
- source text supports the claim and cited report blocks are consistent
- FACT/INFERENCE/SCENARIO and documented/inferred labels are separated
- anti-collapse rules above, including tribal and public/private safeguards
- map existence, dimensions, readable semantics, and PNG/SVG agreement
- prior freeze manifests and unchanged protected artifacts
- Markdown links, whitespace, Git/LFS integrity, and relevant project tests

Use deterministic builders and stable artifact naming. Generated SVGs often
contain dynamic IDs; normalize all generated IDs if reproducibility is required,
or avoid rerendering an unchanged map during a provenance-only correction. Always
review the complete diff and staged path list before commit.

For cross-platform freeze manifests, hash the intended canonical representation
with an explicit newline policy. Do not normalize a frozen file in place merely
to satisfy a validator: compare canonical content, preserve the tracked artifact,
and confirm the frozen hash and worktree state afterward.

## Review gate

Before integration, perform an independent institutional/scientific review that
specifically tests for:

- regulator represented as operator
- monitor represented as regulator
- funder represented as controller
- advisor represented as binding authority
- private operator represented as government
- target or incentive represented as mandate
- historical Indigenous association represented as current jurisdiction
- an inference represented as a legal fact
- a row whose source supports only one side of a claimed relationship

Record corrections and the review disposition in a durable report. Do not claim
formal user acceptance until it occurs. Leave future phases as scope-only briefs
when the approved session boundary says so.

## Delivery checklist

Report the starting and final SHAs, branch/worktree, artifact counts, map numbers,
research/delegation, validation outputs, freeze-protection result, commits,
remote synchronization, worktree status, active holds, unsupported-claim checks,
and explicit confirmation of unimplemented future scope. Do not create releases
or tags unless explicitly authorized.

See `references/phase10-governance-qa.md` for the reusable QA checklist, source
patterns, and corrected examples from a completed governance baseline/dependency
package.
