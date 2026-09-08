# Western Basin Worldbuilding — Phase 10 Governance Profile

This profile adds Western Basin Worldbuilding workflow, reproducibility, and
validation requirements to the generic institutional-governance core in
[`../SKILL.md`](../SKILL.md). Current repository documents and live primary
sources outrank the examples and status descriptions in this profile.

## Profile scope

Apply this profile to Western Basin Phase 10 governance and jurisdiction work,
including institutional baselines, cross-system dependencies, coordination,
and separately authorized governance futures. Keep factual 2026 baselines,
accepted/frozen artifacts, and future scenario layers distinct. Do not create
a synthetic governance score, rank institutions, or turn a scenario into a
legal prediction.

The generic anti-collapse, evidence, provenance, sovereignty, jurisdiction,
public/private, and `FACT` / `INFERENCE` / `SCENARIO` rules remain mandatory.

## Repository startup inspection

Before changing a repository:

1. Resolve the actual repository root from the supplied project path and
   verify it using `.git` and the project’s status files.
2. Report the current branch, current `HEAD` SHA, available remote/default
   branch SHA, worktree status, and worktree path.
3. Read the current `PROJECT_STATUS.md`, `docs/canon_status.md`,
   `docs/agent_workflow.md`, current handoff, and the applicable phase brief.
4. Identify accepted or frozen baselines, their protection manifests, active
   holds, and the approved phase boundary before editing.
5. Inspect the complete diff and staged path list before every commit.

Repository state outranks stale chat context. If a frozen factual baseline
appears wrong, stop and request review rather than silently repairing it.

If repository or worktree isolation is required by the current workflow, use
an isolated branch/worktree. Do not make an unrelated main-branch edit merely
because a convenient checkout is available.

## Phase-boundary and handoff control

Create or update durable phase briefs and handoffs at the first coherent
checkpoint, before the research package becomes difficult to reconstruct.
Record the approved products, negative scope, accepted/frozen baselines,
active holds, validation state, and next exact action.

For Phase 10, preserve the boundary among:

- Phase 10A governance and jurisdiction baseline;
- Phase 10B cross-system authority, dependencies, and coordination; and
- Phase 10C or later governance futures, which are separate scenario scope.

Do not let a Phase 10A/10B baseline silently expand into Phase 10C+, population,
infectious disease, vector ecology, biosecurity, emergency-management
operations, partisan/election analysis, or AI legal authority. A future phase
may be recorded as a scope-only brief when it is not approved for
implementation.

## Accepted and frozen baselines

Before implementation, identify the accepted/frozen Phase 10A and 10B
artifacts and any prior Phase 1–9 protected artifacts that the current
repository requires. Validate their manifests or equivalent integrity records
before and after the work. Do not alter protected baselines to make a new
validator pass.

Phase 10A/10B baseline work should preserve at least these boundaries:

- current governance remains factual and source-bounded;
- GLIFWC or another intertribal body is not automatically a sovereign nation;
- distinct sovereign actors remain distinct;
- regulation, operation, ownership, funding, monitoring, advice, scientific
  information, permitting, and public/private roles remain separate;
- distributed authority, overlap, uncertainty, and coordination burden are
  not automatically governance gaps; and
- unresolved project holds remain unresolved unless separately authorized.

## Western Basin validation requirements

For the repository’s Phase 10 analytical packages, use:

- a primary Python validator;
- an independently implemented R validator with a separate code path;
- schema, stable-ID, controlled-vocabulary, row-count, and source-resolution
  checks;
- source-to-claim consistency and report-block provenance checks;
- `FACT` / `INFERENCE` / `SCENARIO` and documented/inferred separation;
- anti-collapse, sovereignty, public/private, and geographic-scope checks;
- qualitative matrix labels without a composite governance score;
- map existence, dimensions, readable semantics, and SVG/PNG agreement where
  both formats are an approved product;
- accepted/frozen manifest validation before and after edits; and
- Markdown-link, whitespace, Git/LFS, application, and relevant project tests.

Python and R validators must be independently implemented. One validator must
not merely invoke, import, or mirror the other validator’s assertions.

## Reproducible artifact controls

When the approved Phase 10 package includes generated artifacts:

- use deterministic builders and stable generated IDs;
- derive reports from the actual cited source IDs rather than hand-maintained
  source blocks whose numbering can drift;
- preserve enough source references for every multi-actor relationship;
- define newline and canonical-hash handling explicitly for freeze manifests;
- compare canonical content without normalizing a protected file in place;
- preserve tracked frozen artifacts and confirm their hashes and worktree
  state after edits;
- run Git/LFS integrity checks where the repository uses Git LFS; and
- report branch, worktree, starting SHA, final SHA, validation results,
  manifest results, commits, remote synchronization, and final status.

Generated SVGs may contain dynamic IDs. Normalize generated IDs or avoid
rerendering an unchanged map during a provenance-only correction. Verify SVG
and PNG agreement where both are approved deliverables; this is a
project-profile requirement, not a generic requirement for every invocation.

## Review gate for Western Basin examples

Independent review must test the generic anti-collapse checklist against
Western Basin institutional interpretation. In particular, inspect:

- public versus private water scope;
- regulatory authority versus physical utility operation;
- monitoring, research, warning, or inventory versus operational control;
- funding, targets, and assistance programs versus enforceable mandates;
- intertribal bodies versus sovereign tribal governments;
- historical Indigenous association versus current jurisdiction;
- federal/state/local or multi-actor relationships supported by both the
  interaction and the actors’ individual roles; and
- maps or diagrams that could imply unsupported jurisdiction.

## Corrected Western Basin examples

These are execution and review patterns, not permanent facts. Retrieve live
primary sources before relying on them in future work.

### Ohio public versus private water

A source describing Ohio Department of Health private-water regulation must
not be used to create a mandatory permit dependency for Toledo’s municipal
public-water utility. Keep private-water authority bounded, or remove the
dependency. A municipal public-water claim needs public-water evidence.

### USACE / Ohio EPA multi-actor evidence

An Army Corps of Engineers source supports a USACE role; it does not, by
itself, document an Ohio EPA/USACE overlap. Add Ohio EPA evidence for a
documented relationship, or label the edge as a qualified `INFERENCE` and
lower its evidence strength.

### GLIFWC and sovereign tribal actors

The Great Lakes Indian Fish & Wildlife Commission is an intertribal resource
body serving member Ojibwe tribes. Do not classify it as a `tribal_sovereign`
merely because it performs resource-management or conservation-enforcement
work. Preserve distinct nation-specific sovereign actors separately.

### National Wetlands Inventory and authority

The National Wetlands Inventory is evidence for wetland mapping and data
provision. Do not turn inventory stewardship into automatic restoration,
permitting, land-use, or enforcement authority.

### Monitoring versus control

A monitoring, research, warning, or data-provision role should not be emitted
as regulatory or operational control unless the source explicitly supports
it. A permit or reliability-standard authority need not physically observe or
operate every local asset.

### Funding and targets

A financial-assistance program, planning target, nutrient-reduction goal, or
technical-assistance activity is not automatically an enforceable individual
obligation. Record whether a condition is mandatory, voluntary, advisory,
incentive-based, or unknown.

## Primary-source search anchors

The following anchors were useful during the Western Basin Phase 10 work.
They are search and interpretation aids, not frozen evidence. Retrieve and
reassess the current source before relying on any anchor in a new package.

- Ohio EPA public-water materials: <https://epa.ohio.gov/divisions-and-offices/drinking-and-ground-waters>
- Ohio Department of Health private-water materials: <https://odh.ohio.gov/know-our-programs/private-water-systems>
- Toledo Water: <https://toledowater.org/>
- PJM institutional description: <https://www.pjm.com/about-pjm>
- NERC reliability materials: <https://www.nerc.com/pa/Stand/Pages/default.aspx>
- Great Lakes Commission: <https://www.glc.org/>
- GLIFWC institutional description: <https://glifwc.org/>
- EPA Tribal program materials: <https://www.epa.gov/tribalportal>
- USFWS National Wetlands Inventory: <https://www.fws.gov/program/national-wetlands-inventory>
- NOAA/National Weather Service: <https://www.weather.gov/>
- FEMA hazard-mitigation materials: <https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation>

## Delivery and scope report

At completion, report the starting and final SHAs, branch/worktree, artifact
counts, map products, research/delegation or review status, Python and R
validation outputs, freeze-protection result, commits, remote synchronization,
worktree status, active holds, unsupported-claim checks, and explicit future
scope that was not implemented.

Do not create a release or tag unless separately authorized. Do not modify
source datasets, accepted/frozen artifacts, maps, analysis outputs, or project
canon when the task is limited to skill maintenance.
