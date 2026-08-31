# Phase 1 Hydrography Data-Management Cleanup

The accepted scientific integration was first recorded in unpublished local commit `638e5eb2bcd0ab79345f61bb56ac1bbb18b60bcf`. Before rewriting that unpublished commit, it was preserved on local-only branch `backup/phase1-hydrography-pre-data-cleanup`.

## Preserved acceptance record

- Human decision: **B — ACCEPT WITH QUALIFICATION**
- Reconciliation: 93 physical replacements; 115 authoritative USGS connector replacements; 31 already-redundant relationships; 12 unresolved analytical edges; 0 invalid baseline relationships
- Raw 3DHP snapshot: 102,757 features; SHA-256 `365A043ACCED9DC70CBEAEC804408A8539E3C372E3B4F64B962C03DB047EBD60`
- Provenance: 102,525 migrated NHD features; 232 EDH work-unit features
- Current-development GeoPackage SHA-256: `88D7D3D26C8FB746D4AE2502088C906893B8C438A3F255AE0783C24F9EACA8C8`
- Historical v0.1 GeoPackage SHA-256: `555D23D076638E69942C9BB5D6B1043D00A152A945788BDB7C988EE72C576882`

The pre-cleanup validation record passed the dedicated physical-hydrography validator, original Phase 1 validator, Great Black Swamp regression validator, independent R reconciliation, Markdown link validator, GeoPackage integrity check, and all 22 retained application tests.

## Storage decisions

The raw USGS 3DHP spatial extract is not stored in ordinary Git or Git LFS. It is a reproducible national-service extraction and is ignored at its documented cache path. The builder, official service and layer URLs, exact project extent plus 500 m buffer, ordered 2,500-record pagination, record count, provenance counts, retrieval date, and expected hash remain tracked.

The current-development GeoPackage is a useful derived project artifact and is tracked through Git LFS using an exact path rule. This rule begins with the post-v0.1 integration and does not rewrite the historical `v0.1-water-system` release or older commits.

The three accepted semantic layers remain `hydrography_physical`, `hydrography_network_connectors`, and `routing_inferred_unresolved`. The 12 unresolved relationships remain project-inferred, analytical, nonphysical, and explicitly not waterways.
