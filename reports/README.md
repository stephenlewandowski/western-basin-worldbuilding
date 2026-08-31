# Glasspunk Systems Atlas

Phase 1 builds the Water System v0.1 only. Existing TypeScript prototype files are untouched.

```powershell
.\.venv\Scripts\python.exe src\python\systems\build_water_system.py --historical-swamp-image "C:\Users\slewa\Downloads\Great Black Swamp.jpeg"
Rscript src\R\systems\validate_water_system.R .
Rscript src\R\systems\render_water_system.R .
```

Raw public-service responses are cached under `data/raw`. Delete a specific cached response only when intentionally refreshing that source.

## Great Black Swamp Phase 1 follow-up QA

- `great_black_swamp_geometry_source_review.md` — source evaluation, reproducible derivation, uncertainty, and human stop gate.
- `great_black_swamp_class_review.csv` — explicit Gordon/ODNR class inclusion review.
- `great_black_swamp_interstate_compatibility.csv` — Ohio/Indiana/Michigan compatibility assessment.
- `great_black_swamp_geometry_qa.json` — machine-readable geometry validation.
- `great_black_swamp_candidate_county_intersections.csv` and `great_black_swamp_candidate_watershed_intersections.csv` — quantitative overlaps.
- `great_black_swamp_source_manifest.json` — preserved-source hashes and retrieval records.

The candidate remains under `outputs/qa/`; it is not part of the canonical Phase 1 GeoPackage.

## Physical hydrography Phase 1 follow-up QA

- `water_hydrography_source_review.md` — authoritative USGS 3DHP source, retrieval, provenance, and feature semantics.
- `physical_hydrography_reconciliation.md` — executive finding, topology method, baseline comparison, limitations, and human gate.
- `wbd_connector_reconciliation.csv` — one QA outcome for each of the 251 released inferred WBD connectors.
- `physical_hydrography_baseline_comparison.csv` and `physical_hydrography_qa.json` — tabular and machine-readable validation summaries.
- `hydrography_data_cleanup.md` — unpublished-commit backup record and raw/LFS storage decisions.

The hash-verified 3DHP extraction and derived QA maps are the review evidence for **B — ACCEPT WITH QUALIFICATION**. The large raw snapshot is reproducibly retrievable and ignored by Git; its service metadata, retrieval method, feature/provenance counts, and SHA-256 remain tracked. The approved three-layer representation is integrated into the Git-LFS-managed current-development GeoPackage; the historical `v0.1-water-system` artifact and released Map 01–05 files remain unchanged.
