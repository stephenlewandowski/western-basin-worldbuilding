# Repository storage audit — 2026-09-23

## Scope and measurement

The requested spelling `C:\Projects\Public\_GitHub\western-basin-worldbuilding` does not exist on this machine. The canonical repository is `C:\Projects\Public_GitHub\western-basin-worldbuilding`. Its root checkout is on `phase17c-character-narrative-architecture` with pre-existing site edits and untracked work, so this audit measures the clean current `main` tree at commit `815aa582b102ec003c58419241bef95991f6ecb1` in the linked `temp/public-site-publish` worktree. This report is the only new versionable file in the root checkout; no accepted artifact was edited or removed. MiB means 2^20 bytes. Filesystem sums, Git logical blob sizes, packed-object allocation, and GitHub's reported repository size are different measures and should not be added indiscriminately.

| Measure before cleanup | Size / count | Interpretation |
| --- | ---: | --- |
| Physical current worktree, excluding shared `.git` | 728.33 MiB / 2,566 files | Includes ignored dependencies and `dist` |
| Tracked current files | 656.63 MiB / 1,181 files | Materialized LFS file is counted at full size |
| `outputs/` | 485.66 MiB / 251 files | Primarily accepted vector maps |
| `data/` | 151.00 MiB / 240 files | Raw geospatial sources and processed GeoPackage |
| `node_modules/` | 69.11 MiB / 1,356 files | Ignored, reinstallable local dependency tree |
| `assets/` | 13.38 MiB / 14 files | Site delivery assets |
| `dist/` | 2.59 MiB / 28 files | Ignored Vite build, removed after validation |
| Shared `.git` directory | 425.53 MiB / 383 files | 258.04 MiB objects, 167.06 MiB LFS objects |
| Current untracked, nonignored files in clean worktree before report | 0 | The root checkout separately has 12 pre-existing untracked files, about 0.10 MiB, which were left alone |

`git count-objects -vH`: 183 loose objects / 6.69 MiB; 3 packs containing 3,319 objects / 251.24 MiB; no garbage. The current tracked tree is 426.71 MiB SVG (80 files), 84.01 MiB GPKG (one LFS file), 65.40 MiB PNG (141 files), 56.19 MiB GeoJSON (17 files), 11.13 MiB CSV (238 files), and 4.20 MiB ZIP (one file). The 173 MB figure reported by GitHub cannot be equated to the checked-out filesystem total: Git compression, LFS accounting, and ref selection differ.

The root checkout's largest untracked file is the pre-existing `reports/phase17c_recurring_cast_prototypes.md` (54.4 KiB); the next files are site source copies under `src/` (at most 16.4 KiB). These are active work, not cleanup candidates. The ignored `dist/` and `node_modules/` are counted separately above.

## TOP CURRENT TRACKED FILES

Classification is the storage role of the current file. Phase 1 accepted assets are treated as protected even when an older phase did not use a `*freeze_manifest.json`.

| # | MiB | Path | Classification |
| ---: | ---: | --- | --- |
| 1 | 84.01 | `data/processed/glasspunk_base.gpkg` | CANONICAL DATA; accepted Phase 1+ spatial store, LFS |
| 2 | 17.10 | `outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 3 | 17.09 | `outputs/maps/systems/32_governance_jurisdiction_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 4 | 17.09 | `outputs/maps/systems/27_biogeochemical_dependencies_controls_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 5 | 17.09 | `outputs/maps/systems/26_biogeochemical_nutrient_flux_system_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 6 | 17.07 | `outputs/maps/systems/28b_biogeochemical_futures_2075.svg` | PROTECTED ACCEPTED ARTIFACT |
| 7 | 17.07 | `outputs/maps/systems/28_biogeochemical_futures_2050.svg` | PROTECTED ACCEPTED ARTIFACT |
| 8 | 17.02 | `outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 9 | 17.01 | `outputs/maps/systems/21_ecological_dependencies_disturbances_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 10 | 17.00 | `outputs/maps/systems/20_ecological_system_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 11 | 16.94 | `outputs/maps/systems/31b_climate_hazard_futures_2075.svg` | PROTECTED ACCEPTED ARTIFACT |
| 12 | 16.94 | `outputs/maps/systems/31_climate_hazard_futures_2050.svg` | PROTECTED ACCEPTED ARTIFACT |
| 13 | 16.93 | `outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 14 | 16.93 | `outputs/maps/systems/29_climate_natural_hazards_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 15 | 16.93 | `outputs/maps/systems/41_infectious_disease_system_baseline_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 16 | 16.83 | `outputs/maps/systems/38_vector_ecology_baseline_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 17 | 16.75 | `outputs/maps/systems/39_vector_environment_human_dependencies_2026.svg` | PROTECTED ACCEPTED ARTIFACT |
| 18 | 13.15 | `data/raw/census/tigerweb_counties_oh_in_mi.geojson` | SOURCE / EVIDENCE |
| 19 | 12.69 | `outputs/qa/hydrography_baseline_vs_authoritative.svg` | PROTECTED ACCEPTED ARTIFACT; Phase 1 QA evidence |
| 20 | 10.41 | `data/raw/usgs/wbd_huc12_maumee_basin.geojson` | SOURCE / EVIDENCE |

## TOP HISTORICAL BLOBS

These are the 20 largest *individual Git blobs* reachable from all local branches, remote-tracking refs, and tags, sorted by uncompressed size. Repeated paths indicate different versions. `HEAD?` means the exact blob ID is present in the current tree. Packed bytes from `git cat-file %(objectsize:disk)` are approximate allocations, not a guaranteed independent saving if rewritten.

| # | Blob ID | Logical MiB | Packed MiB | HEAD? | Path / classification |
| ---: | --- | ---: | ---: | :---: | --- |
| 1 | `508a35aba8` | 83.05 | 40.78 | No | `data/processed/glasspunk_base.gpkg` — CANONICAL DATA, accepted historical Phase 1 state; backup-only Git blob |
| 2 | `80ef2d590f` | 39.98 | 39.99 | No | `data/raw/usgs/3dhp_flowlines_maumee_buffer500m.geojson.gz` — SOURCE / EVIDENCE; backup-only snapshot |
| 3 | `53c9cc35fd` | 16.74 | 0.08 | Yes | `outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 4 | `9e9424ff5b` | 16.74 | 2.53 | Yes | `outputs/maps/systems/32_governance_jurisdiction_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 5 | `cb02884563` | 16.73 | 2.54 | Yes | `outputs/maps/systems/27_biogeochemical_dependencies_controls_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 6 | `44e45a7432` | 16.73 | 2.54 | Yes | `outputs/maps/systems/26_biogeochemical_nutrient_flux_system_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 7 | `c7491e6d4b` | 16.72 | 2.54 | Yes | `outputs/maps/systems/28b_biogeochemical_futures_2075.svg` — PROTECTED ACCEPTED ARTIFACT |
| 8 | `4a683cbc8c` | 16.71 | 0.07 | Yes | `outputs/maps/systems/28_biogeochemical_futures_2050.svg` — PROTECTED ACCEPTED ARTIFACT |
| 9 | `341c355e8e` | 16.67 | 2.46 | Yes | `outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 10 | `c0670a60be` | 16.66 | 2.59 | Yes | `outputs/maps/systems/21_ecological_dependencies_disturbances_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 11 | `5ace9a25cc` | 16.65 | 2.58 | Yes | `outputs/maps/systems/20_ecological_system_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 12 | `0192aa050b` | 16.65 | 0.07 | No | Older version of `outputs/maps/systems/20_ecological_system_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 13 | `0f055d2ede` | 16.58 | 2.31 | Yes | `outputs/maps/systems/31b_climate_hazard_futures_2075.svg` — PROTECTED ACCEPTED ARTIFACT |
| 14 | `1f2255b8a9` | 16.58 | 0.06 | No | Older version of `outputs/maps/systems/31b_climate_hazard_futures_2075.svg` — PROTECTED ACCEPTED ARTIFACT |
| 15 | `457124ab4b` | 16.58 | 2.32 | Yes | `outputs/maps/systems/31_climate_hazard_futures_2050.svg` — PROTECTED ACCEPTED ARTIFACT |
| 16 | `bdd32934d9` | 16.58 | 0.07 | No | Older version of `outputs/maps/systems/31_climate_hazard_futures_2050.svg` — PROTECTED ACCEPTED ARTIFACT |
| 17 | `a2fc870670` | 16.57 | 0.08 | No | Older version of `outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 18 | `d81bc1b18f` | 16.57 | 0.07 | Yes | `outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 19 | `53660d9502` | 16.57 | 2.48 | Yes | `outputs/maps/systems/29_climate_natural_hazards_2026.svg` — PROTECTED ACCEPTED ARTIFACT |
| 20 | `2ab109d4db` | 16.57 | 0.06 | No | Older version of `outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg` — PROTECTED ACCEPTED ARTIFACT |

## TOP LFS OBJECTS

| LFS SHA-256 | MiB | State | Classification / disposition |
| --- | ---: | --- | --- |
| `2f082fa400b5390965d8df3a870af51966d3b5169eaa4727ee4d2da19d2e0b7f` | 84.01 | Current `data/processed/glasspunk_base.gpkg`; retained | CANONICAL DATA |
| `88d7d3d26c8fb746d4ae2502088c906893b8c438a3f255ae0783c24f9eaca8c8` | 83.05 | Older accepted Phase 1 development GeoPackage; local only, remote verification reports missing | SOURCE / EVIDENCE; preserve |

There is one LFS-tracked path at HEAD and two local objects, 167.06 MiB total. `git lfs fsck` passes. `git lfs prune --verify-remote --dry-run --verbose` would identify the 83.05 MiB older object as otherwise pruneable, but explicitly reports it **missing on the remote**. It was therefore not pruned. The old object's checksum is recorded in `reports/development_gpkg_transition_manifest.json`, and it is tied to an accepted Phase 1 state.

## REGENERABLE LARGE FILES

| Path / set | MiB | Classification | Decision |
| --- | ---: | --- | --- |
| `node_modules/` | 69.11 | CACHE / TEMPORARY | Ignored; kept as a local dependency install for follow-on work; never a Git payload |
| `dist/` | 2.59 | REGENERABLE DERIVATIVE | Ignored Vite build; removed after successful build |
| `outputs/atlas/prototypes/5_3_industrial_exchange/5_3_contact_sheet.png` | 0.56 | PROTECTED ACCEPTED ARTIFACT | A generated preview, but retained as accepted review evidence |
| `outputs/atlas/prototypes/4_3_farm_2075/4_3_contact_sheet.png` | 0.36 | PROTECTED ACCEPTED ARTIFACT | Retained |
| `outputs/atlas/prototypes/2_1_from_field_to_lake/animation/2_1_animation_contact_sheet.png` | 0.35 | PROTECTED ACCEPTED ARTIFACT | Retained |
| `outputs/atlas/prototypes/2_1_from_field_to_lake/_preview_contact_sheet.png` | 0.22 | PROTECTED ACCEPTED ARTIFACT | Retained |

No current tracked `__pycache__`, Python bytecode, Vite `dist`, `node_modules`, MP4, WebM, GIF, GLB, glTF, OBJ, FBX, BLEND, or STL was found. The only `.vite` cache is inside ignored `node_modules`. Existing `.gitignore` already covers Python caches, Node dependencies, `dist/`, generic scratch directories, the Phase 17A rendered MP4, and the reproducible 3DHP raw extract. No new ignore rule was needed.

## NON-REGENERABLE LARGE FILES

| Path / set | MiB | Classification | Reason retained |
| --- | ---: | --- | --- |
| Historical 3DHP gzip snapshot, blob `80ef2d590f` | 39.98 | SOURCE / EVIDENCE | Exact 2026 source snapshot may not be recreated from a changing service; metadata and SHA-256 persist |
| `data/raw/census/tigerweb_counties_oh_in_mi.geojson` | 13.15 | SOURCE / EVIDENCE | Raw input snapshot with provenance; not a disposable derivative |
| `data/raw/usgs/wbd_huc12_maumee_basin.geojson` | 10.41 | SOURCE / EVIDENCE | Raw input snapshot |
| `data/raw/usgs/nhd_lake_erie.geojson` | 9.77 | SOURCE / EVIDENCE | Raw input snapshot |
| `data/raw/ohiodnr/bedrock_type_western_basin.geojson` | 4.73 | SOURCE / EVIDENCE | Raw input snapshot |
| `data/raw/ohiodnr/original_vegetation_ohio/OriginalVegetationOhio.zip` | 4.20 | SOURCE / EVIDENCE | Original reference archive |
| `data/raw/h2ohio/History_of_the_Great_Black_Swamp.pdf` | 1.86 | SOURCE / EVIDENCE | Reference document |

`data/raw/` totals 61.68 MiB in 36 files; `data/processed/` totals 89.32 MiB in 204 files, overwhelmingly the canonical LFS GeoPackage. There was no evidence sufficient to replace any present raw source with a future download of identical bytes. The tracked atlas delivery PNGs in `assets/` and prototype spreads remain WEB DELIVERY ASSET or PROTECTED ACCEPTED ARTIFACT; their sizes do not justify changing format during this audit.

## PROTECTED LARGE FILES

| Path / group | MiB | Classification | Protection |
| --- | ---: | --- | --- |
| `data/processed/glasspunk_base.gpkg` | 84.01 | CANONICAL DATA | Phase 1+ accepted spatial store; no change |
| Governance SVGs `33`, `32` | 34.19 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| Biogeochemical SVGs `27`, `26`, `28b`, `28` | 68.31 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| Ecology SVGs `21`, `20` | 34.02 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| Climate SVGs `31b`, `31`, `30`, `29` | 67.74 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| Infectious-disease SVGs `42`, `41` | 33.95 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| Vector SVGs `38`, `39` | 33.58 | PROTECTED ACCEPTED ARTIFACT | Freeze manifest hashes pass |
| `outputs/qa/hydrography_baseline_vs_authoritative.svg` | 12.69 | PROTECTED ACCEPTED ARTIFACT | Accepted Phase 1 QA evidence |
| Phase 17A animation keyframes and reduced-motion endpoint | 1.73 combined | PROTECTED ACCEPTED ARTIFACT | Accepted motion evidence and accessibility endpoint; no MP4 tracked |

All 37 `*freeze_manifest.json` files were checked against 655 entries covering 646 distinct paths. Of those entries, 399 match raw SHA-256 and 256 match the accepted Git bytes after permitted LF/CRLF normalization; **zero are missing or mismatched**. No Phase 1–16 accepted file was edited or deleted.

## DUPLICATE CONTENT

All 1,181 current tracked files were hashed by SHA-256. Four exact-content pairs yield only 0.161 MiB theoretical savings. They have distinct accepted roles, so none was removed.

| Matching paths | Redundant MiB | Classification | Decision |
| --- | ---: | --- | --- |
| `outputs/atlas/prototypes/2_1_from_field_to_lake/animation/2_1_animation_keyframe_A5.png` and `.../2_1_from_field_to_lake_reduced_motion.png` | 0.146 | DUPLICATE content; PROTECTED ACCEPTED ARTIFACT roles | Retain both named endpoints |
| `data/processed/analysis/vector_system_dependency_register.csv` and `data/processed/networks/vector_system_dependency_edges.csv` | 0.0077 | DUPLICATE content; PROTECTED ACCEPTED ARTIFACT roles | Retain; freeze manifests reference both |
| `reports/phase13b_citation_ledger.json` and `reports/phase13c_citation_ledger.json` | 0.0064 | DUPLICATE content; PROTECTED ACCEPTED ARTIFACT roles | Retain; separate phase records |
| `data/processed/analysis/modal_substitutability_matrix.csv` and `outputs/figures/freight_dependency_matrix_2026.csv` | 0.0010 | DUPLICATE content; PROTECTED ACCEPTED ARTIFACT roles | Retain; separate analysis and figure roles |

No duplicate untracked outputs existed in the clean worktree. Similar names or raster/vector pairs were not treated as byte duplicates or automatically disposable: their resolution, evidence role, and accepted status differ.

## Forward-looking storage policy

1. Keep canonical line art as SVG where practical; make PNG/WebP delivery derivatives only when a consumer needs them. Freeze manifests and accepted outputs take precedence over file-size preferences.
2. Use WebP or AVIF for new web delivery imagery when supported, while retaining original photographs or reference images when they are unique evidence. Prefer JPEG/WebP for photos; use PNG only for transparency, lossless technical detail, or another documented need.
3. For new high-resolution renders, retain the source data, builder, parameters, and selected accepted result; regenerate intermediate rasters on demand. Record hashes and provenance before omitting a large intermediate.
4. Keep animation source, builder, and accepted keyframes; do not commit large MP4 renders by default. The present Phase 17A MP4 ignore rule follows this policy.
5. Prefer procedural/source 3D and compressed GLB for web delivery. Avoid multiple interchange exports without a stated downstream need. No current 3D assets require migration.
6. For large public datasets that are stable and legally reproducible, prefer a retrieval script, source URL, retrieval date, checksum, and metadata over another full copy. Do not remove a historical snapshot solely because an endpoint still responds: its exact bytes may no longer be obtainable.
7. Run `git lfs fsck`, freeze checks, and `git diff --check` before changing any storage format. Treat current canonical data and Phase 1–16 accepted outputs as immutable until a separately reviewed replacement is accepted.

## HISTORY REWRITE CANDIDATE

Across **all local refs**, 789 Git blobs are absent from the current HEAD tree: 263.17 MiB uncompressed, with about **84.81 MiB** attributed by `git cat-file` to packed/loose on-disk object storage. This is an upper-bound-style accounting figure, not an exact `git-filter-repo` reclaim estimate. Two backup-only blobs account for about 80.77 MiB of that figure: accepted historical GeoPackage `508a35aba8` (40.78 MiB packed) and the 2026 3DHP snapshot `80ef2d590f` (39.99 MiB packed). They are reachable from local `backup/phase1-hydrography-pre-data-cleanup`, not from `origin/*` or the `v0.1-water-system` tag. A rewrite of published refs cannot reclaim those local-only bytes from GitHub.

Only 775 historical-only blobs are reachable from remote-tracking refs or the tag, totaling 139.95 MiB logical but approximately **4.00 MiB packed** locally. These are mostly small changed versions and highly delta-compressed accepted SVGs. Rewriting published branches/tags for roughly 4 MiB offers little benefit against the user's ~173 MB GitHub figure and would change commit IDs and accepted historical references. The old 83.05 MiB LFS object is separate from the Git pack, is tied to accepted Phase 1 evidence, and `git lfs prune --verify-remote --dry-run` confirms it is **not present on the configured LFS remote**. LFS pruning or a Git rewrite is not a safe cleanup of it.

No `git-filter-repo` command is recommended because no history rewrite is justified. If the backup branch is ever separately reviewed for retirement, first preserve the accepted GeoPackage and raw snapshot in a verified archival location and establish whether their exact bytes remain required; that is a distinct evidence-retention decision, not part of this audit. No history operation, force push, or ref deletion was performed.

## Cleanup and validation

The only file deletion is the ignored `dist/` generated by Vite (28 files, 2.59 MiB); `npm run build` recreates it. The temporary audit checker in ignored `temp/` is also removed after validation. No tracked file is removed, no `.gitignore` line changes, and estimated **GitHub/current tracked-tree savings are 0 MiB**. Physical worktree savings are approximately **2.59 MiB**. Retaining `node_modules/` leaves future local development ready and has no effect on GitHub storage.

Validation: all 37 freeze manifests pass (655 entries, 0 mismatches); `npm test` passes (3 files, 22 tests); `npm run build` passes; repository-relative Markdown links pass; `git lfs fsck` passes; `git diff --check` passes. An additional run of `validate_phase16b_freeze.py` stops at its original "no later-phase files" boundary because the repository now legitimately contains Phase 17 and site additions; it does not report a manifest hash mismatch. The clean main worktree has no tracked or untracked change after cleanup. In the root checkout, this report is untracked alongside 12 pre-existing untracked Phase 17C/site files and three pre-existing modified site files (`README.md`, `index.html`, `vite.config.ts`); those existing changes remain untouched.

NO HISTORY REWRITE WARRANTED
