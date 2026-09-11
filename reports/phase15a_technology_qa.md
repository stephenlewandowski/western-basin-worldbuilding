# Phase 15A Technology QA

## Package checks

The reproducible builder writes 18 technology records across 8 families, 21 observations, 44 technology-system interfaces, 32 dependency records, 8 uncertainty records, 30 source records, and one conceptual PNG/SVG figure. The machine result is `reports/phase15a_artifact_check.json`; Python and independent base-R validators are required before integration.

## Required semantic checks

- technology IDs, families, maturity values, current/emerging/speculative labels, source IDs, and system IDs resolve;
- target systems resolve to the frozen Phase 14 ontology without adding a technology system to `metadata/atlas_systems.yml`;
- relationship and evidence classes reuse the Phase 14 vocabularies;
- regional deployment claims are absent unless directly supported; general capability is not relabeled local;
- AI rows preserve decision support ≠ autonomous authority;
- sensing rows preserve observation ≠ interpretation ≠ decision ≠ enforcement;
- cybersecurity remains defensive and resilience-oriented;
- quantum remains research-stage/speculative and fusion remains non-current;
- biotechnology remains high-level and the biosecurity lens contains no operational harmful-biology detail;
- prior freeze manifests and active holds remain intact;
- Phase 15B/16 data, scenario, and map artifacts are absent.

## Figure QA

`outputs/figures/technology_system_convergence_architecture_2026.png` and `.svg` are a conceptual matrix/network hybrid, not a geographic map. The SVG retains text labels for established/current, emerging, speculative/long-horizon, governance/data dependency, and the non-deployment caveat. Matrix cell color is categorical interface relevance, not probability, risk, quantity, or effect size.

## Provenance

External capability claims use the grounded-citation ledger and numbered citations in the reports. Repository source IDs point to accepted/frozen system artifacts used as regional context. The Phase 15A interface is generally an explicit project inference over those inputs; it does not promote the input artifacts into technology-deployment evidence.
