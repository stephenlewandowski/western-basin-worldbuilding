# Model Lab diagnostic runs

## v0.1A unit-pulse baseline

[`v01a_unit_pulse_inputs.csv`](v01a_unit_pulse_inputs.csv) contains **synthetic unit pulses only**. Each of two HUC-12s receives one bookkeeping unit of water (`m3/period`), TN (`kg/period`), and TP (`kg/period`) for each of two runs. `041000030101` follows a qualified route to the model boundary; `041000090402` encounters an unresolved project-inferred link. The period label `unit_pulse_no_time` has no calendar or hydrologic interpretation. Omitted HUCs mean zero **only for this diagnostic input class**.

From the repository root, run with Python 3.11+; on Windows, substitute your configured Python executable if `python` is not on `PATH`:

```sh
python src/python/model_lab/route_water_nutrients.py --run-id v01a_unit_pulse_strict --period unit_pulse_no_time --inputs data/model_lab/v01a_unit_pulse_inputs.csv --policy strict --out-dir outputs/model_lab/v01a_unit_pulse_strict
python src/python/model_lab/validate_run.py --run-dir outputs/model_lab/v01a_unit_pulse_strict
python src/python/model_lab/render_diagnostics.py --run-dir outputs/model_lab/v01a_unit_pulse_strict --wbd data/raw/usgs/wbd_huc12_maumee_basin.geojson

python src/python/model_lab/route_water_nutrients.py --run-id v01a_unit_pulse_assume_wbd --period unit_pulse_no_time --inputs data/model_lab/v01a_unit_pulse_inputs.csv --policy assume_wbd --out-dir outputs/model_lab/v01a_unit_pulse_assume_wbd
python src/python/model_lab/validate_run.py --run-dir outputs/model_lab/v01a_unit_pulse_assume_wbd
```

The strict run leaves one unit of each constituent **unrouted at an unresolved link** and exports one at the terminal HUC. The `assume_wbd` sensitivity forwards that unit through a hypothetical WBD successor and exports two. The `unrouted_at_unresolved` and `not_forwarded_assumed` fields describe bookkeeping dispositions, not physical storage, treatment, ecological retention, or nutrient removal. These outputs demonstrate arithmetic and sensitivity to routing evidence. They are **not measured runoff, nutrient loads, or Lake Erie delivery**.

Each run writes `input_snapshot.csv`, `huc_balance.csv`, `edge_flux.csv`, `boundary_summary.csv`, and `run_manifest.json` with source hashes and status flags. The strict run also has three diagnostic SVGs. `validate_run.py` checks node and run closure, edge reconciliation, units, topology claims, and unresolved-link handling. The first-build decisions and missing empirical data are in the [readiness report](../../reports/model_lab_v01_water_nutrient_readiness.md).

## v0.1B configured sensitivity and traces

[`v01b_sensitivity.json`](v01b_sensitivity.json) explicitly defines three **synthetic** cases over the same accepted HUC network and [`v01b_unit_pulse_inputs.csv`](v01b_unit_pulse_inputs.csv): strict unresolved routing, hypothetical WBD-successor routing, and strict routing with one hypothetical TN pass-through fraction of 0.5 from [`v01b_tn_half_pass_assumptions.csv`](v01b_tn_half_pass_assumptions.csv). The last fraction tests arithmetic only; its `not_forwarded_assumed` quantity is not measured storage, retention, treatment, or removal. Water and TP retain unit pass-through in that case. No case estimates runoff or observed nutrient loads.

From the repository root:

```sh
python src/python/model_lab/route_water_nutrients.py --config data/model_lab/v01b_sensitivity.json
python src/python/model_lab/validate_run.py --run-dir outputs/model_lab/v01b_unit_pulse_strict
python src/python/model_lab/validate_run.py --run-dir outputs/model_lab/v01b_unit_pulse_assume_wbd
python src/python/model_lab/validate_run.py --run-dir outputs/model_lab/v01b_unit_pulse_tn_half_pass
Rscript src/R/model_lab/verify_run.R --run-dir outputs/model_lab/v01b_unit_pulse_strict
Rscript src/R/model_lab/verify_run.R --run-dir outputs/model_lab/v01b_unit_pulse_assume_wbd
Rscript src/R/model_lab/verify_run.R --run-dir outputs/model_lab/v01b_unit_pulse_tn_half_pass
```

Each v0.1B run retains the v0.1A ledger tables and adds `downstream_trace.csv` and `upstream_trace.csv`. Both trace tables use the same ordered columns: `run_id`, `period`, `unresolved_policy`, `focus_huc12`, `traced_huc12`, `hops`, `policy_reachable`, and `first_unresolved_link_from_huc12`. They enumerate the accepted **accounting topology**, including a self row for every HUC. `policy_reachable` describes whether the selected unresolved-link policy permits forwarding along that path; the last field identifies the first unresolved link source on the structural path, even in the WBD sensitivity. In the upstream table, “first” is measured while walking from `traced_huc12` toward `focus_huc12`. Neither table apportions water or nutrient quantity to an individual source, maps a physical stream, or predicts travel time.

The v0.1B `run_manifest.json` declares `schema_version`, the case label/description, configuration, engine, and trace-generator hashes, and an `output_schema` mapping of all six CSVs to their exact ordered headers. The configured command is the recommended way to run v0.1B sensitivities; the single-run CLI remains available and records null case/config metadata. Python and independent base-R verification read the written files, recompute balances and trace consistency, and reject schema drift. Historical v0.1A output files remain unchanged and are checked against their pinned accepted engine hash.

## v0.2A local explorer

The [read-only Shiny explorer](../../src/R/model_lab/explorer/README.md) consumes the three committed v0.1B cases without rerunning the engine. With R 4.5+ and `shiny`/`jsonlite` installed, launch and check it from the repository root:

```sh
Rscript -e "shiny::runApp('src/R/model_lab/explorer', host='127.0.0.1', port=3838, launch.browser=TRUE)"
Rscript tests/test_model_lab_explorer.R
```

HUC selection and trace direction show structural paths and routing-policy reachability; constituent selection shows the saved ledger and three-case mass dispositions. The app checks manifest source/code hashes, exact CSV schemas, synthetic status, units, row keys, trace self rows, and geography joins at startup. The full Python and independent R validators above remain the arithmetic/topology audits. [Integration review and validation](../../reports/model_lab_v02a_explorer_review.md) records the source publication; GitHub Pages does not host this R application.
