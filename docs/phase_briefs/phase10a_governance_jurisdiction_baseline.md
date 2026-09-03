# Phase 10A — Governance & Jurisdiction Baseline, 2026

Status: APPROVED FOR IMPLEMENTATION; working baseline pending Sol acceptance.

Primary product: Map 32 — Western Basin Governance & Jurisdiction, 2026 (or the next sequential map number confirmed from repository state).

## Purpose

Identify which institutions have documented authority or operational responsibility over the Western Basin systems in 2026. This is an institutional systems analysis, not partisan or election analysis. Reuse the accepted Water, Geology / Strategic Materials, Energy / Grid / Compute, Data / Sensors / Security, Freight / Industry, Ecology / Biodiversity, Environmental Health / Exposure, Biogeochemical / Nutrient Flux, and Climate / Natural Hazards systems.

## Mandatory distinctions

The data model must keep these separate: regulatory authority versus operational control; monitoring versus regulation; funding versus authority; advisory role versus binding decision authority; ownership versus regulation; permitting versus physical operation; scientific information versus legal decision authority; and private operation versus public control. A target, plan, incentive, technical-assistance activity, or voluntary conservation program must not be represented as an enforceable individual mandate without evidence.

## Institutional scales and actors

Represent materially relevant federal, state, interstate, binational, tribal / Indigenous sovereign, county, municipal, regional-authority, special-district, public-utility, system-operator, private-operator, and research/monitoring actors. Do not flatten distinct institutional scales into generic government. Do not infer current tribal jurisdiction from historical occupation, interest, consultation, or cultural affiliation; preserve nation-specific uncertainty and use authoritative tribal/nation or governmental sources.

## Products

- `data/processed/analysis/governance_actors.csv`
- `data/processed/analysis/governance_authorities.csv`
- `data/processed/networks/governance_relationships.csv`
- `data/processed/analysis/governance_sources.csv`
- `data/processed/analysis/governance_uncertainty_register.csv`
- Map 32 PNG/SVG, using the actual next map number confirmed by the builder
- `reports/governance_baseline_sources.md`
- `reports/governance_baseline_assumptions.md`
- `reports/governance_baseline_findings.md`
- `reports/governance_baseline_qa.md`
- machine-readable artifact check and manifest
- reproducible Python builder and validator
- independent R validator

## Authority record requirements

Each important role claim should carry actor, domain/system, authority_or_role, authority_type, binding_or_nonbinding, legal_or_operational_basis, geographic_scope, jurisdictional_scale, source_id, evidence_strength, reality_status, canon_status, and notes. Authority vocabulary may include regulate, permit, enforce, operate, own, monitor, fund, coordinate, advise, plan, warn, respond, restore, set_standard, research, and provide_data. Legal interpretations must be limited to what the cited authority documents support.

## Domain coverage

Cover water/drinking water; Great Lakes and binational governance; nutrient/agricultural governance; ecology/wetland/coastal governance; energy/grid; freight/industry; environmental health; and climate/natural-hazard governance. Identify who regulates, operates, owns, monitors, funds, coordinates, compels action, advises, warns, responds, and restores. Explicitly identify scientific observation without operational authority, operational responsibility dependent on another actor's information, and authority unclear from available evidence.

Do not use this phase to resolve the Toledo intake-coordinate discrepancy or the Great Black Swamp C — HOLD / noncanonical status. Do not rebuild Phase 7 or create a comprehensive emergency-management model. Do not add Phase 10C futures.

## Evidence and status rules

Prefer statutes/regulations, treaties/compacts/formal agreements, official agency program documentation, official operator/utility documentation, official tribal/nation sources, authoritative legal/institutional analysis, and peer-reviewed sources. Claims are labeled FACT, INFERENCE, or SCENARIO in reports and encoded with reality/canon status. Source provenance must be traceable at row level. Unknown is preserved as unknown.

## Validation and transition gate

Validate schemas, controlled vocabularies, source references, claim-status separation, jurisdictional scales, coordinates/map semantics, negative-scope rules, map artifact integrity/readability, prior Phase 1–9 freeze manifests, Markdown links, Git/LFS, Python and independent R validators, and complete diff review. Explicitly test that no regulator is represented as an operator, monitor as regulator, funder as controller, advisor as binding authority, private operator as governmental authority, planning target as enforceable mandate, historical Indigenous association as unsupported current jurisdiction, or project inference as legal fact. Phase 10A remains an unaccepted working baseline until Sol review.
