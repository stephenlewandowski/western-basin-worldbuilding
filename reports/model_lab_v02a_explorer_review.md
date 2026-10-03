# Model Lab v0.2A explorer integration review

Reviewed 3 October 2026 against committed `main` / `origin/main` at
`bd446883102c06933c853637083299d84b8a3b79` (Model Lab v0.1B routing traces
and sensitivities). The reviewed candidate began as the untracked
`src/R/model_lab/explorer/` and `tests/test_model_lab_explorer.R`.

## Result and publication scope

The explorer is **IMPLEMENTED / REVIEWED / VALIDATED** for local Shiny use.
It reads the three saved v0.1B synthetic cases and their six-CSV schemas,
retains HUC identifiers as character strings, and displays HUC accounting
polygons, directional traces, ledgers, mass dispositions, and provenance.
Source publication is a normal GitHub commit/push. The static Atlas/GitHub
Pages build does not serve this R application. No external Shiny hosting,
release, tag, empirical model run, scenario, or new canon is included.

## Integration gaps corrected

- **Source binding:** startup previously accepted a nonempty configuration
  hash without checking its format or contents, and only inspected the engine
  and trace-generator hash formats. It now checks every declared input,
  routing, geography, configuration, assumption, engine, and trace-generator
  SHA-256 against the checkout and checks source paths against the configured
  accepted cases. It uses base R's `tools::sha256sum`, requiring R 4.5+.
  The committed manifests mix LF hashes for model code/inputs/configuration
  with a CRLF hash for qualified routing. Hash checks accept either exact
  text newline representation to accommodate Git checkout conversion while
  rejecting content changes; they do not alter sources or manifest hashes.
- **Case identity:** loading previously depended on the configuration array's
  order and ignored changed configured input/output paths. Cases now match by
  unique run ID, preserve a stable comparison order, and reject changed paths,
  policies, or assumption assignments. Reordered, self-consistent scratch
  configuration remains readable.
- **Display prerequisites:** startup now rejects incompatible constituents or
  units, non-synthetic status, missing interpretation metadata, negative
  quantities, invalid pass-through fractions, duplicate table keys, invalid
  HUC references, and missing/invalid trace self rows. The accepted engine's
  `omitted_zero_diagnostic` rows remain valid with zero local input. Full
  arithmetic and structural trace audits remain in the existing validators;
  the viewer never runs routing equations or regenerates products.
- **Regression coverage:** altered-file checks use disposable copies of the
  committed products. They exercise configuration, source/hash, status, units,
  schema, join, row-key, numeric/Boolean, and trace-self failures. The WBD
  display check now examines actual reachability and table cells instead of
  relying on one HTML whitespace spelling. Test-path resolution also works
  when sourced from another R script or launched outside the repository root.
- **Repository integration:** the root README, data/run guide, report index,
  project status, and operational handoff now link to the explorer and this
  review. Launch instructions use normal R libraries by default and explain
  optional ignored local libraries. The UI names its explorer/model versions,
  has a document title, and explains that source hashes are checked at startup.

## Validation

On R 4.6.1 with Shiny 1.14.0 and jsonlite 2.0.0:

- Explorer loader, saved-data assertions, altered scratch fixtures, and Shiny
  `testServer` display checks passed. Direct `Rscript` launch from the `temp/`
  working directory also passed using the optional local R library.
  Scratch fixtures converted entirely to LF and entirely to CRLF both load
  the same three cases.
- Python's 30 Model Lab unit tests passed. Python and independent R validators
  passed for all three committed v0.1B runs, including schema, provenance,
  units/status, balances, topology, and trace consistency.
- Live browser checks confirmed clean downstream routing, the seven-HUC
  strict unresolved path, the same WBD path with all rows policy reachable
  and unresolved-source provenance retained, and the six-HUC upstream set
  at `041000030106` with `041000030103` blocked. The TN comparison retained
  half-pass export/not-forwarded values of 0.5; water/TP assertions passed
  in the R display/data checks. Both map and chart rendered, with no Shiny
  output errors. At 390 px, settled plots resized within their cards and
  the document had no horizontal overflow; wide tables scroll in their
  containers. This is bounded browser QA, not an accessibility certification.
- Atlas regression: 22 npm tests passed and the TypeScript/Vite build passed.
- Git diff whitespace and LFS integrity checks passed. Committed v0.1A/v0.1B
  products, engine/validators, accepted geography, and qualified routing are
  unchanged. Frozen-path and documentation-link audits are recorded in the
  current handoff.

## Scientific boundaries retained

The inputs are synthetic unit pulses in `unit_pulse_no_time`. HUCs are
accounting areas; map colors describe topology/policy reachability, not stream
channels or load magnitude. Traces do not apportion quantity to an individual
source or estimate travel time. Unrouted and assumption-based not-forwarded
quantities are ledger dispositions, not measured storage, treatment,
ecological retention, or nutrient removal. Boundary export is not an observed
Maumee or Lake Erie load. The WBD successor and TN half-pass cases remain
hypothetical sensitivities. Phase 1–16 frozen baselines and Phase 17D's active
status are unaffected.
