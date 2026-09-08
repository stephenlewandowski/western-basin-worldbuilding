# Governance baseline and dependency QA reference

This is a reusable reference distilled from the Western Basin Phase 10A/10B
package. Treat current repository documents and current primary sources as
authoritative; these examples are patterns, not permanent project facts.

## Required row-level fields

Authority/role rows should carry, where practical:

`authority_id, actor_id, domain/system, authority_or_role, authority_type,
binding_or_nonbinding, legal_or_operational_basis, geographic_scope,
jurisdictional_scale, source_id, evidence_strength, reality_status, canon_status,
notes`

Dependency rows should carry:

`dependency_id, system_a, system_b, actor_a, actor_b, role_a, role_b,
dependency_type, coordination_mechanism, mandatory_or_voluntary,
documented_or_inferred, jurisdictional_scale, evidence_strength, source_id,
notes`

Keep role vocabulary controlled. Useful roles include `regulate`, `permit`,
`enforce`, `operate`, `own`, `monitor`, `fund`, `coordinate`, `advise`, `plan`,
`warn`, `respond`, `restore`, `set_standard`, `research`, and `provide_data`.

## Corrected patterns from independent review

1. Private-water versus public-water scope

   A source describing Ohio Department of Health private-water regulation must
   not be used to create a mandatory permit dependency for Toledo's municipal
   public-water utility. Keep the private-water authority bounded, or remove the
   dependency. A municipal public-water claim needs public-water evidence.

2. Sovereign versus intertribal body

   The Great Lakes Indian Fish & Wildlife Commission is an intertribal resource
   body serving member Ojibwe tribes. Do not classify it as a `tribal_sovereign`
   merely because it performs resource-management or conservation-enforcement
   work. Preserve distinct nation-specific sovereign actors separately.

3. Multi-actor permitting evidence

   An USACE source supports an USACE role; it does not, by itself, document an
   Ohio EPA/USACE overlap. Add Ohio EPA evidence for a documented relationship,
   or label the edge as a qualified inference and lower its evidence strength.

4. Inventory versus restoration authority

   The National Wetlands Inventory is evidence for wetland mapping and data
   provision. Do not turn inventory stewardship into automatic restoration,
   permitting, or land-use authority.

5. Monitoring versus control

   A monitoring, research, warning, or data-provision role should not be emitted
   as regulatory or operational control unless the source explicitly supports it.
   Conversely, a permit or reliability-standard authority need not physically
   observe or operate every local asset.

6. Funding and targets

   A financial-assistance program, planning target, or nutrient-reduction goal
   is not automatically an enforceable individual obligation. Record whether a
   condition is mandatory, voluntary, advisory, incentive-based, or unknown.

## Short primary-source excerpts captured during the work package

Use these as search anchors and interpretation checks; retrieve the live source
before relying on them in a new package.

- Ohio EPA public-water materials describe Ohio EPA's Division of Drinking and
  Ground Waters as regulating public water systems and public systems' monitoring
  and reporting duties.
  https://epa.ohio.gov/divisions-and-offices/drinking-and-ground-waters
- Ohio Department of Health private-water materials describe regulation of
  private water systems, which is not the same as Toledo's municipal public
  water system.
  https://odh.ohio.gov/know-our-programs/private-water-systems
- Toledo Water describes the city water system as municipally owned/operated and
  describes its treatment and utility functions.
  https://toledowater.org/
- PJM describes itself as a regional transmission organization coordinating the
  movement of electricity through its wholesale market and grid operations; this
  does not make PJM the owner of utility assets.
  https://www.pjm.com/about-pjm
- NERC reliability materials describe reliability standards and compliance
  functions; standards are not the same as physical operation of local assets.
  https://www.nerc.com/pa/Stand/Pages/default.aspx
- The Great Lakes Commission describes policy, coordination, and regional
  convening functions; it should not be called a generic basin regulator.
  https://www.glc.org/
- GLIFWC describes an intertribal commission serving member Ojibwe tribes and
  providing natural-resource management assistance; classify the body from
  that institutional description rather than inferring sovereign jurisdiction.
  https://glifwc.org/
- EPA Tribal program materials recognize federally recognized tribes as
  sovereign governments and separately describe consultation and program
  participation; do not infer a current territorial polygon without direct
  evidence.
  https://www.epa.gov/tribalportal
- USFWS National Wetlands Inventory materials describe a wetlands data and
  mapping service; inventory information is not automatically a permit or
  restoration order.
  https://www.fws.gov/program/national-wetlands-inventory
- NOAA/NWS materials describe observation, forecasting, and warnings; a warning
  is information/coordination input, not universal operational command.
  https://www.weather.gov/
- FEMA hazard-mitigation materials describe risk identification, mitigation
  planning, and assistance; these functions do not by themselves establish
  local ownership or direct infrastructure operation.
  https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation

## Independent validation recipe

Run the builder once, then run separate validators rather than making the
builder assert all of its own outputs:

1. Validate schemas, IDs, vocabulary, counts, and source resolution in Python.
2. Validate the same invariants independently in R, using separate code paths.
3. Verify source-to-claim consistency, including every cited report block.
4. Verify FACT/INFERENCE/SCENARIO and documented/inferred separation.
5. Run semantic anti-collapse checks for regulator/operator, monitor/regulator,
   funder/controller, advisor/binding authority, public/private, and sovereign/
   intertribal distinctions.
6. Validate map files, dimensions, labels, and generalized geography.
7. Validate all prior freeze manifests before and after edits.
8. Run Markdown-link, whitespace, Git/LFS, and relevant application checks.
9. Review the complete unstaged and staged diffs, then verify branch, remote,
   worktree, and commit SHA after integration.

A passing validator is necessary but not sufficient: an independent reviewer
must inspect legal/institutional interpretation and provenance. Record findings
and corrections in a durable review report.

## Reproducibility pitfalls

- Build reports from the actual cited source IDs. Do not hand-maintain a source
  block whose numbering can drift from the registry.
- For multi-actor edges, store enough source references to support the relation,
  not merely the existence of each actor.
- Use stable SVG IDs or normalize all generated IDs. If a correction changes only
  provenance, do not casually regenerate an unchanged map and introduce noisy
  dynamic-ID diffs.
- For freeze hashes, define newline handling explicitly and preserve the tracked
  frozen artifact. A line-ending normalization made only to appease a checker is
  not a scientific correction.
- Keep Phase 10C or later futures as scope-only when the approved session ends at
  10A/10B. Do not let a complete baseline silently expand into scenario work.
