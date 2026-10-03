# Read-only adapter for accepted Model Lab v0.1B products. No model equations run here.

explorer_schema <- list(
  "boundary_summary.csv" = c(
    "run_id", "period", "constituent", "unit", "total_local_input",
    "total_not_forwarded_assumed", "total_unrouted_at_unresolved",
    "boundary_export", "residual", "unresolved_policy"
  ),
  "downstream_trace.csv" = c(
    "run_id", "period", "unresolved_policy", "focus_huc12", "traced_huc12",
    "hops", "policy_reachable", "first_unresolved_link_from_huc12"
  ),
  "edge_flux.csv" = c(
    "run_id", "period", "from_huc12", "to_huc12", "constituent", "unit",
    "amount", "routing_basis", "qa_status", "assumed_unresolved"
  ),
  "huc_balance.csv" = c(
    "run_id", "period", "huc12", "constituent", "unit", "local_input",
    "upstream_in", "available", "pass_through", "not_forwarded_assumed",
    "unrouted_at_unresolved", "downstream_out", "boundary_export", "residual",
    "route_to_huc12", "routing_basis", "qa_status", "physical_geometry",
    "input_status"
  ),
  "input_snapshot.csv" = c(
    "run_id", "period", "huc12", "constituent", "local_input", "unit",
    "input_status", "source_id", "method", "uncertainty_note"
  ),
  "upstream_trace.csv" = c(
    "run_id", "period", "unresolved_policy", "focus_huc12", "traced_huc12",
    "hops", "policy_reachable", "first_unresolved_link_from_huc12"
  )
)

explorer_units <- c(water = "m3/period", TN = "kg/period", TP = "kg/period")
explorer_sources <- c(
  input = "data/model_lab/v01b_unit_pulse_inputs.csv",
  qualified_routing = "data/processed/networks/huc12_routing_current.csv",
  sensitivity_config = "data/model_lab/v01b_sensitivity.json",
  wbd_huc12 = "data/raw/usgs/wbd_huc12_maumee_basin.geojson"
)

explorer_fail <- function(...) stop(paste0(...), call. = FALSE)

explorer_file <- function(repo_root, relative) {
  path <- file.path(repo_root, relative)
  if (!file.exists(path)) explorer_fail("Model Lab file missing: ", path)
  path
}

explorer_numeric <- function(table, fields, file) {
  for (field in fields) {
    raw <- table[[field]]
    value <- suppressWarnings(as.numeric(raw))
    if (any(!nzchar(raw)) || any(!is.finite(value))) {
      explorer_fail("Invalid numeric field ", field, " in ", file)
    }
    if ((field != "residual" && any(value < 0)) ||
        (field == "pass_through" && any(value > 1))) {
      explorer_fail("Out-of-range numeric field ", field, " in ", file)
    }
    table[[field]] <- value
  }
  table
}

explorer_logical <- function(table, fields, file) {
  for (field in fields) {
    raw <- table[[field]]
    if (any(!raw %in% c("True", "False"))) {
      explorer_fail("Invalid Boolean field ", field, " in ", file)
    }
    table[[field]] <- raw == "True"
  }
  table
}

explorer_read_csv <- function(path, expected) {
  # Character import retains leading zeros in HUC identifiers. Convert only
  # known numeric/Boolean fields after checking the exact ordered header.
  tab <- utils::read.csv(path, colClasses = "character", check.names = FALSE,
                         na.strings = character(), fileEncoding = "UTF-8-BOM")
  if (!identical(names(tab), expected)) {
    explorer_fail("Model Lab CSV header mismatch: ", path,
                  "; expected [", paste(expected, collapse = ", "),
                  "]; found [", paste(names(tab), collapse = ", "), "]")
  }
  if (anyNA(tab)) explorer_fail("Missing CSV value in ", path)
  key <- basename(path)
  numeric_fields <- switch(key,
    "boundary_summary.csv" = c("total_local_input", "total_not_forwarded_assumed",
                               "total_unrouted_at_unresolved", "boundary_export", "residual"),
    "downstream_trace.csv" = "hops",
    "edge_flux.csv" = "amount",
    "huc_balance.csv" = c("local_input", "upstream_in", "available", "pass_through",
                          "not_forwarded_assumed", "unrouted_at_unresolved",
                          "downstream_out", "boundary_export", "residual"),
    "input_snapshot.csv" = "local_input",
    "upstream_trace.csv" = "hops"
  )
  tab <- explorer_numeric(tab, numeric_fields, path)
  if (key %in% c("downstream_trace.csv", "upstream_trace.csv")) {
    if (any(tab$hops != floor(tab$hops)) || any(tab$hops < 0)) {
      explorer_fail("Invalid trace hops in ", path)
    }
    tab$hops <- as.integer(tab$hops)
    tab <- explorer_logical(tab, "policy_reachable", path)
  }
  if (key == "edge_flux.csv") tab <- explorer_logical(tab, "assumed_unresolved", path)
  if (key == "huc_balance.csv") tab <- explorer_logical(tab, "physical_geometry", path)
  tab
}

explorer_read_json <- function(path) {
  jsonlite::fromJSON(path, simplifyVector = FALSE)
}

explorer_scalar <- function(value, label) {
  if (!is.character(value) || length(value) != 1L || is.na(value) || !nzchar(value)) {
    explorer_fail("Invalid or missing ", label)
  }
  value
}

explorer_check_hash <- function(repo_root, relative, declared, label) {
  declared <- explorer_scalar(declared, paste(label, "SHA-256"))
  if (!grepl("^[0-9a-f]{64}$", declared)) {
    explorer_fail("Invalid SHA-256 for ", label)
  }
  path <- explorer_file(repo_root, relative)
  if (identical(unname(tools::sha256sum(path)), declared)) return(invisible(TRUE))
  # These known sources are text. Accepted manifests mix LF and CRLF hashes;
  # Git's checkout conversion must not make an otherwise identical clone fail.
  text <- rawToChar(readBin(path, "raw", n = file.info(path)$size))
  lf <- gsub("\r\n", "\n", text, fixed = TRUE)
  crlf <- gsub("\n", "\r\n", lf, fixed = TRUE)
  candidates <- c(tools::sha256sum(bytes = charToRaw(lf)),
                  tools::sha256sum(bytes = charToRaw(crlf)))
  if (!declared %in% candidates) {
    explorer_fail("Source SHA-256 differs for ", label, ": ", path)
  }
  invisible(TRUE)
}

explorer_check_sources <- function(repo_root, sources, config_case) {
  expected <- as.list(explorer_sources)
  expected["assumptions"] <- list(config_case$assumptions)
  if (!is.list(sources) ||
      !setequal(names(sources), c(names(expected), "engine_sha256", "trace_generator_sha256"))) {
    explorer_fail("Missing or unexpected source provenance")
  }
  for (label in names(expected)) {
    relative <- expected[[label]]
    entry <- sources[[label]]
    if (is.null(relative)) {
      if (!is.null(entry)) explorer_fail("Unexpected assumption source for ", config_case$run_id)
      next
    }
    if (!is.list(entry) || !identical(entry$path, relative)) {
      explorer_fail("Source path mismatch for ", label, " in ", config_case$run_id)
    }
    explorer_check_hash(repo_root, relative, entry$sha256, label)
  }
  explorer_check_hash(repo_root, "src/python/model_lab/route_water_nutrients.py",
                      sources$engine_sha256, "engine")
  explorer_check_hash(repo_root, "src/python/model_lab/trace_huc_paths.py",
                      sources$trace_generator_sha256, "trace generator")
}

explorer_unique <- function(tab, fields, label) {
  if (anyDuplicated(tab[fields])) explorer_fail("Duplicate row key in ", label)
}

explorer_check_version <- function(manifest, path) {
  if (!identical(manifest$schema_version, "0.1B") ||
      !identical(manifest$model_version, "0.1B")) {
    explorer_fail("Unsupported Model Lab schema version in ", path)
  }
}

explorer_read_geography <- function(repo_root) {
  path <- explorer_file(repo_root, "data/raw/usgs/wbd_huc12_maumee_basin.geojson")
  geojson <- explorer_read_json(path)
  if (!identical(geojson$type, "FeatureCollection") || !is.list(geojson$features)) {
    explorer_fail("Invalid WBD HUC-12 GeoJSON FeatureCollection: ", path)
  }
  features <- geojson$features
  huc <- vapply(features, function(feature) explorer_scalar(feature$properties$huc12, "GeoJSON huc12"), "")
  name <- vapply(features, function(feature) explorer_scalar(feature$properties$name, "GeoJSON name"), "")
  geometry <- lapply(features, function(feature) feature$geometry)
  if (length(huc) != 252L || anyDuplicated(huc) ||
      any(!grepl("^[0-9]{12}$", huc)) ||
      any(!vapply(geometry, function(g) g$type %in% c("Polygon", "MultiPolygon") &&
                    is.list(g$coordinates) && length(g$coordinates) > 0L, logical(1)))) {
    explorer_fail("WBD HUC-12 geography must contain 252 unique named polygon HUCs: ", path)
  }
  result <- data.frame(huc12 = huc, name = name, stringsAsFactors = FALSE)
  result$geometry <- I(geometry)  # Raw nested lon/lat GeoJSON coordinates.
  result
}

explorer_load_run <- function(repo_root, config_case, key, geography_ids) {
  run_id <- explorer_scalar(config_case$run_id, "configured run_id")
  if (!identical(run_id, paste0("v01b_unit_pulse_", key))) {
    explorer_fail("Unexpected configured v0.1B run ID for ", key, ": ", run_id)
  }
  directory <- file.path(repo_root, "outputs/model_lab", run_id)
  manifest_path <- explorer_file(repo_root, file.path("outputs/model_lab", run_id, "run_manifest.json"))
  manifest <- explorer_read_json(manifest_path)
  explorer_check_version(manifest, manifest_path)
  if (!identical(manifest$run_id, run_id) ||
      !identical(manifest$period, "unit_pulse_no_time") ||
      !identical(manifest$unresolved_policy, config_case$unresolved_policy) ||
      !identical(manifest$sensitivity_case$label, config_case$label) ||
      !identical(manifest$sensitivity_case$description, config_case$description)) {
    explorer_fail("Run/configuration metadata mismatch in ", manifest_path)
  }
  if (!identical(manifest$input_status, "synthetic_diagnostic") ||
      !identical(manifest$topology$accepted_baseline, TRUE) ||
      !identical(manifest$topology$huc_count, 252L) ||
      !identical(unlist(manifest$units)[names(explorer_units)], explorer_units) ||
      !is.list(manifest$interpretation) || length(manifest$interpretation) == 0L ||
      any(!vapply(manifest$interpretation, function(x) is.character(x) &&
                    length(x) == 1L && !is.na(x) && nzchar(x), logical(1)))) {
    explorer_fail("Synthetic diagnostic metadata mismatch in ", manifest_path)
  }
  if (!identical(sort(names(manifest$output_schema)), sort(names(explorer_schema)))) {
    explorer_fail("Six-CSV output_schema mapping mismatch in ", manifest_path)
  }
  for (file in names(explorer_schema)) {
    declared <- unlist(manifest$output_schema[[file]], use.names = FALSE)
    if (!identical(declared, explorer_schema[[file]])) {
      explorer_fail("Manifest output_schema header mismatch for ", file, " in ", manifest_path)
    }
  }
  explorer_check_sources(repo_root, manifest$source_files, config_case)
  tables <- setNames(lapply(names(explorer_schema), function(file) {
    path <- file.path(directory, file)
    if (!file.exists(path)) explorer_fail("Model Lab run CSV missing: ", path)
    explorer_read_csv(path, explorer_schema[[file]])
  }), sub("\\.csv$", "", names(explorer_schema)))
  for (table_name in names(tables)) {
    tab <- tables[[table_name]]
    if (nrow(tab) == 0L || any(tab$run_id != run_id) || any(tab$period != manifest$period)) {
      explorer_fail("Run/period mismatch or empty table: ", table_name, " in ", directory)
    }
    if ("unresolved_policy" %in% names(tab) &&
        any(tab$unresolved_policy != manifest$unresolved_policy)) {
      explorer_fail("Policy mismatch in ", table_name, " in ", directory)
    }
    if ("constituent" %in% names(tab)) {
      if (any(!tab$constituent %in% names(explorer_units)) ||
          any(tab$unit != unname(explorer_units[tab$constituent]))) {
        explorer_fail("Constituent/unit mismatch in ", table_name, " in ", directory)
      }
    }
    if ("input_status" %in% names(tab)) {
      allowed <- if (table_name == "huc_balance")
        c("synthetic_diagnostic", "omitted_zero_diagnostic") else "synthetic_diagnostic"
      if (any(!tab$input_status %in% allowed) ||
          any(tab$local_input[tab$input_status == "omitted_zero_diagnostic"] != 0)) {
        explorer_fail("Non-synthetic input status or nonzero omitted input in ", table_name, " in ", directory)
      }
    }
  }
  explorer_unique(tables$boundary_summary, "constituent", "boundary_summary")
  if (!setequal(tables$boundary_summary$constituent, names(explorer_units))) {
    explorer_fail("Incomplete boundary summary in ", directory)
  }
  explorer_unique(tables$huc_balance, c("huc12", "constituent"), "huc_balance")
  explorer_unique(tables$input_snapshot, c("huc12", "constituent"), "input_snapshot")
  explorer_unique(tables$edge_flux, c("from_huc12", "to_huc12", "constituent"), "edge_flux")
  if (any(!tables$input_snapshot$huc12 %in% geography_ids) ||
      any(!tables$edge_flux$from_huc12 %in% geography_ids) ||
      any(!tables$edge_flux$to_huc12 %in% geography_ids) ||
      any(!tables$huc_balance$route_to_huc12 %in% c("", geography_ids))) {
    explorer_fail("Ledger/geography HUC-12 join mismatch in ", directory)
  }
  balances <- tables$huc_balance
  for (constituent in c("water", "TN", "TP")) {
    ids <- balances$huc12[balances$constituent == constituent]
    if (length(ids) != 252L || anyDuplicated(ids) ||
        !setequal(ids, geography_ids)) {
      explorer_fail("HUC-12 balance/geography join mismatch for ", constituent, " in ", directory)
    }
  }
  for (direction in c("downstream_trace", "upstream_trace")) {
    tab <- tables[[direction]]
    explorer_unique(tab, c("focus_huc12", "traced_huc12"), direction)
    if (any(!tab$focus_huc12 %in% geography_ids) ||
        any(!tab$traced_huc12 %in% geography_ids) ||
        any(!tab$first_unresolved_link_from_huc12 %in% c("", geography_ids)) ||
        !setequal(tab$focus_huc12, geography_ids)) {
      explorer_fail("Trace/geography HUC-12 join mismatch for ", direction, " in ", directory)
    }
    self <- tab[tab$focus_huc12 == tab$traced_huc12, , drop = FALSE]
    if (nrow(self) != length(geography_ids) || !setequal(self$focus_huc12, geography_ids) ||
        any(self$hops != 0L) || any(!self$policy_reachable) ||
        any(nzchar(self$first_unresolved_link_from_huc12)) ||
        any(tab$hops[tab$focus_huc12 != tab$traced_huc12] == 0L)) {
      explorer_fail("Invalid or missing trace self rows for ", direction, " in ", directory)
    }
  }
  list(manifest = manifest, label = config_case$label,
       description = config_case$description, tables = tables)
}

load_model_lab <- function(repo_root) {
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    explorer_fail("Model Lab explorer requires R package 'jsonlite'. Install it before launch.")
  }
  if (!"sha256sum" %in% getNamespaceExports("tools")) {
    explorer_fail("Model Lab explorer requires an R version with tools::sha256sum (R 4.5 or newer).")
  }
  repo_root <- normalizePath(repo_root, winslash = "/", mustWork = TRUE)
  config_path <- explorer_file(repo_root, "data/model_lab/v01b_sensitivity.json")
  config <- explorer_read_json(config_path)
  if (!identical(config$config_version, "0.1B") ||
      !identical(config$period, "unit_pulse_no_time") || length(config$runs) != 3L) {
    explorer_fail("Expected three configured Model Lab v0.1B cases in ", config_path)
  }
  keys <- c("strict", "assume_wbd", "tn_half_pass")
  source_fields <- c(inputs = "input", routing = "qualified_routing", wbd = "wbd_huc12")
  for (config_name in names(source_fields)) {
    if (!identical(config[[config_name]], explorer_sources[[source_fields[[config_name]]]])) {
      explorer_fail("Configuration source path mismatch for ", config_name)
    }
  }
  run_ids <- vapply(config$runs, function(case) explorer_scalar(case$run_id, "configured run_id"), "")
  if (anyDuplicated(run_ids) || !setequal(run_ids, paste0("v01b_unit_pulse_", keys))) {
    explorer_fail("Expected three distinct configured Model Lab v0.1B run IDs")
  }
  cases <- config$runs[match(paste0("v01b_unit_pulse_", keys), run_ids)]
  for (index in seq_along(keys)) {
    case <- cases[[index]]
    expected_assumptions <- if (keys[[index]] == "tn_half_pass")
      "data/model_lab/v01b_tn_half_pass_assumptions.csv" else NULL
    expected_policy <- if (keys[[index]] == "assume_wbd") "assume_wbd" else "strict"
    if (!identical(case$out_dir, paste0("outputs/model_lab/", case$run_id)) ||
        !"assumptions" %in% names(case) || !identical(case$assumptions, expected_assumptions) ||
        !identical(case$unresolved_policy, expected_policy)) {
      explorer_fail("Configured case paths/policy mismatch for ", keys[[index]])
    }
  }
  geography <- explorer_read_geography(repo_root)
  runs <- setNames(lapply(seq_along(keys), function(index) {
    explorer_load_run(repo_root, cases[[index]], keys[[index]], geography$huc12)
  }), keys)
  ids <- sort(geography$huc12)
  default_huc <- if ("041000090603" %in% ids) "041000090603" else ids[[1L]]
  list(runs = runs, geography = geography, huc_ids = ids,
       default_huc = default_huc, schema_version = "0.1B")
}

trace_for <- function(run, direction, focus) {
  if (!direction %in% c("downstream", "upstream")) {
    explorer_fail("Trace direction must be downstream or upstream")
  }
  table <- run$tables[[paste0(direction, "_trace")]]
  result <- table[table$focus_huc12 == focus, , drop = FALSE]
  if (nrow(result) == 0L) explorer_fail("No ", direction, " trace for HUC-12 ", focus)
  result[order(result$hops, result$traced_huc12), , drop = FALSE]
}

balance_for <- function(run, constituent) {
  if (!constituent %in% c("water", "TN", "TP")) explorer_fail("Unknown constituent: ", constituent)
  run$tables$huc_balance[run$tables$huc_balance$constituent == constituent, , drop = FALSE]
}

summary_for <- function(run, constituent) {
  if (!constituent %in% c("water", "TN", "TP")) explorer_fail("Unknown constituent: ", constituent)
  result <- run$tables$boundary_summary[
    run$tables$boundary_summary$constituent == constituent, , drop = FALSE]
  if (nrow(result) != 1L) explorer_fail("Missing or duplicate boundary summary for ", constituent)
  result
}
