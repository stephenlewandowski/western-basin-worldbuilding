# Model Lab v0.2A read-only explorer

This small Shiny app reads the three accepted **synthetic** v0.1B runs. It does not run the Python model or create scenarios.

## Local launch

Requires R 4.5 or newer (`tools::sha256sum` checks source provenance). Tested with R 4.6.1, `shiny` 1.14.0, and `jsonlite` 2.0.0. Install `shiny` and `jsonlite` if absent:

```r
install.packages(c("shiny", "jsonlite"))
```

From the repository root, launch locally:

```sh
Rscript -e "shiny::runApp('src/R/model_lab/explorer', host='127.0.0.1', port=3838, launch.browser=TRUE)"
```

If `Rscript` is not on `PATH` on Windows, use your installed executable. For R 4.6.1, the PowerShell form is:

```powershell
& 'C:\Program Files\R\R-4.6.1\bin\Rscript.exe' -e 'shiny::runApp("src/R/model_lab/explorer", host="127.0.0.1", port=3838, launch.browser=TRUE)'
```

Open `http://127.0.0.1:3838` if the browser does not open automatically. If using the optional ignored `temp/model_lab_r_lib` library, set `.libPaths(c("temp/model_lab_r_lib", .libPaths()))` in R before launching or testing. The app uses base R graphics for the map and accounting chart; `sf`, `leaflet`, and `ggplot2` are not required.

This is a local Shiny application. Publishing its source to GitHub does not serve it through the static Atlas/GitHub Pages build; a hosted Shiny deployment requires a separate publication decision.

## Inputs and interpretation

The app loads only `v01b_unit_pulse_strict`, `v01b_unit_pulse_assume_wbd`, and `v01b_unit_pulse_tn_half_pass` from `outputs/model_lab/`, matched by run ID in the [v0.1B configuration](../../../../data/model_lab/v01b_sensitivity.json). For each run it reads `run_manifest.json` and the six declared CSVs: `boundary_summary.csv`, `downstream_trace.csv`, `edge_flux.csv`, `huc_balance.csv`, `input_snapshot.csv`, and `upstream_trace.csv`. The HUC outlines and names come from `data/raw/usgs/wbd_huc12_maumee_basin.geojson`. Startup rejects missing files, unsupported schema, header drift, configuration/path/hash drift, non-synthetic status, wrong units, duplicate row keys, missing trace self rows, and incomplete 252-HUC geography joins. Source and code SHA-256 checks bind the displayed geography and assumptions to the saved runs, allowing only Git's LF/CRLF checkout conversion. Omitted synthetic inputs retain the engine's `omitted_zero_diagnostic` status and must have zero local input.

The map colors **HUC accounting areas**, not physical stream channels. A trace row records graph hops and whether the selected unresolved-link policy permits forwarding along that path. It does not attribute water or nutrients to a source, measure stream flow or runoff, or estimate travel time or concentration. `unrouted_at_unresolved` means the ledger stops forwarding at unresolved routing evidence. `not_forwarded_assumed` is a hypothetical bookkeeping disposition, not observed storage, treatment, ecological retention, or nutrient removal. The WBD-successor route and TN half-pass case are synthetic sensitivities. Model-boundary export is not a measured Maumee or Lake Erie load.

## Checks

From the repository root, run the loader and representative view checks with:

```sh
Rscript tests/test_model_lab_explorer.R
```

The checks load committed products, exercise all three cases and constituents, render representative Shiny outputs, and reject altered scratch fixtures without modifying saved products. The [integration review](../../../../reports/model_lab_v02a_explorer_review.md) records validation and publication scope. The existing v0.1B Python and R validators remain the full arithmetic/topology checks for the underlying model outputs; the explorer does not run the engine or rebuild traces.
