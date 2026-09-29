# Model Lab v0.1A diagnostic inputs

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
