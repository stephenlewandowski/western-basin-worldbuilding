# Freight Evidence Validation QA

## Required products

- `freight_evidence_crosswalk.csv`: 20 evidence records.
- `freight_evidence_relationships.csv`: 12 strengthened/checked relationships.
- `freight_interchange_matrix.csv`: 9 modal/interface records.
- Map 18 PNG/SVG.
- Phase 5A freeze manifest and artifact checks remain separate.

## Evidence QA

- Port-level access, Class I rail access, highway access, general cargo, liquid
  bulk, and Ironville movement evidence is explicitly sourced.
- NS, CSX, and CN are retained as corridor/carrier interfaces; W&LE remains
  listed but specific interchange is unresolved.
- Marine↔rail and marine↔highway access are documented at port level.
- Ironville vessel input and truck/rail output are documented movement functions,
  not a reconstructed transfer layout.
- Woodville and Genoa access remain proximity-only or unresolved.
- Elmore remains a generalized nonlocal-feed logistics dependency.
- Luckey licensed off-site disposal is documented without route geometry.
- Port-specific grain activity remains unresolved.

## Boundary QA

- No Phase 5A network table is modified.
- No shipment quantity, schedule, train/truck/vessel count, or pipeline capacity
  is present.
- No facility-specific route or hazardous-material route is present.
- No sensitive logistics topology, dispatch infrastructure, or security model is
  present.
- No future freight content is present.
- Corridor presence is not treated as shipment proof.
- Facility proximity is not treated as access proof.

## Materials Corridor test

**B — FREIGHT EVIDENCE PROVIDES WEAK SUPPORT.**

The port and Ironville evidence is strong for specific movement functions, while
material-site freight access remains generalized or unresolved. The evidence
does not justify a coherent Materials Corridor geography.

## Freeze and artifact QA

`src/python/systems/validate_freight_evidence.py` checks the Phase 5A freeze
manifest, prior phase freezes, Maps 01–17, evidence provenance, classifications,
modal fields, Map 18, and artifact hashes.
`src/R/systems/validate_freight_evidence.R` independently checks the evidence
and interchange tables and Map 18 artifacts.

The machine-readable result is `reports/freight_evidence_artifact_check.json`.
The Phase 5B manifest is `reports/freight_evidence_manifest.json`.
