#!/usr/bin/env Rscript
# Independent base-R verification of a written Model Lab routing ledger.
# This is an arithmetic/topology audit, not empirical calibration or a load claim.

options(stringsAsFactors = FALSE)

abort <- function(message) stop(message, call. = FALSE)
require_true <- function(condition, message) {
  if (!isTRUE(condition)) abort(message)
}
near <- function(actual, expected) {
  all(is.finite(actual)) && all(is.finite(expected)) &&
    all(abs(actual - expected) <= pmax(1e-9, 1e-12 * pmax(abs(actual), abs(expected))))
}
same_values <- function(actual, expected, label) {
  require_true(length(actual) == length(expected) && near(actual, expected),
               paste0(label, " does not reconcile"))
}
unique_keys <- function(table, fields, label) {
  key <- do.call(paste, c(table[fields], sep = "|"))
  require_true(!anyDuplicated(key), paste0(label, " has duplicate keys"))
  key
}
read_table <- function(path, required) {
  require_true(file.exists(path), paste("Missing", path))
  tab <- read.csv(path, colClasses = "character", check.names = FALSE,
                  na.strings = character(), fileEncoding = "UTF-8-BOM")
  require_true(all(required %in% names(tab)),
               paste(basename(path), "missing fields:", paste(setdiff(required, names(tab)), collapse = ", ")))
  require_true(!anyNA(tab), paste(basename(path), "contains missing values"))
  tab
}
numeric_column <- function(tab, field, label, nonnegative = TRUE) {
  raw <- tab[[field]]
  require_true(!any(!nzchar(raw)), paste(label, field, "has blank values"))
  value <- suppressWarnings(as.numeric(raw))
  require_true(length(value) == nrow(tab) && all(is.finite(value)),
               paste(label, field, "has nonnumeric or nonfinite values"))
  if (nonnegative) require_true(all(value >= 0), paste(label, field, "has negative values"))
  value
}

# Keep the verifier usable with a clean base-R installation. The JSON reader is
# deliberately limited to the JSON grammar, not a Python or shell JSON bridge.
parse_json <- function(source) {
  chars <- strsplit(source, "", fixed = TRUE)[[1]]
  at <- 1L
  count <- length(chars)
  skip_space <- function() {
    while (at <= count && chars[[at]] %in% c(" ", "\t", "\r", "\n")) at <<- at + 1L
  }
  expect <- function(character) {
    skip_space()
    require_true(at <= count && identical(chars[[at]], character),
                 paste("Malformed JSON near character", at))
    at <<- at + 1L
  }
  parse_string <- function() {
    expect('"')
    result <- character()
    repeat {
      require_true(at <= count, "Unterminated JSON string")
      current <- chars[[at]]
      at <<- at + 1L
      if (identical(current, '"')) break
      if (identical(current, "\\")) {
        require_true(at <= count, "Unterminated JSON escape")
        escape <- chars[[at]]
        at <<- at + 1L
        if (identical(escape, "u")) {
          require_true(at + 3L <= count, "Incomplete JSON Unicode escape")
          digits <- paste(chars[at:(at + 3L)], collapse = "")
          require_true(grepl("^[0-9a-fA-F]{4}$", digits), "Invalid JSON Unicode escape")
          current <- intToUtf8(strtoi(digits, base = 16L))
          at <<- at + 4L
        } else {
          mapping <- c('"' = '"', '\\' = '\\', '/' = '/', b = "\b", f = "\f",
                       n = "\n", r = "\r", t = "\t")
          require_true(escape %in% names(mapping), "Invalid JSON escape")
          current <- mapping[[escape]]
        }
      }
      result <- c(result, current)
    }
    paste(result, collapse = "")
  }
  parse_value <- NULL
  parse_value <- function() {
    skip_space()
    require_true(at <= count, "Unexpected end of JSON")
    current <- chars[[at]]
    if (identical(current, '"')) return(parse_string())
    if (identical(current, "{")) {
      at <<- at + 1L
      result <- list()
      skip_space()
      if (at <= count && identical(chars[[at]], "}")) {
        at <<- at + 1L
        return(result)
      }
      repeat {
        key <- parse_string()
        require_true(!(key %in% names(result)), paste("Duplicate JSON key", key))
        expect(":")
        result[key] <- list(parse_value())
        skip_space()
        require_true(at <= count, "Unterminated JSON object")
        if (identical(chars[[at]], "}")) {
          at <<- at + 1L
          break
        }
        expect(",")
      }
      return(result)
    }
    if (identical(current, "[")) {
      at <<- at + 1L
      result <- list()
      skip_space()
      if (at <= count && identical(chars[[at]], "]")) {
        at <<- at + 1L
        return(result)
      }
      repeat {
        result[length(result) + 1L] <- list(parse_value())
        skip_space()
        require_true(at <= count, "Unterminated JSON array")
        if (identical(chars[[at]], "]")) {
          at <<- at + 1L
          break
        }
        expect(",")
      }
      return(result)
    }
    tail <- paste(chars[at:count], collapse = "")
    for (literal in c("true", "false", "null")) {
      if (startsWith(tail, literal)) {
        at <<- at + nchar(literal)
        return(switch(literal, true = TRUE, false = FALSE, null = NULL))
      }
    }
    number <- regmatches(tail, regexpr("^-?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?", tail))
    require_true(length(number) == 1L && nzchar(number), paste("Invalid JSON value at", at))
    at <<- at + nchar(number)
    as.numeric(number)
  }
  result <- parse_value()
  skip_space()
  require_true(at > count, "Trailing characters after JSON value")
  result
}
read_json <- function(path) {
  require_true(file.exists(path), paste("Missing", path))
  parse_json(paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n"))
}

script_args <- commandArgs(trailingOnly = TRUE)
flag_value <- function(name) {
  where <- match(name, script_args)
  require_true(!is.na(where) && where < length(script_args), paste("Usage: --run-dir PATH; missing", name))
  script_args[[where + 1L]]
}
script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[[1]])
repo_root <- normalizePath(file.path(dirname(script_file), "../../.."), winslash = "/", mustWork = TRUE)
run_dir <- normalizePath(flag_value("--run-dir"), winslash = "/", mustWork = TRUE)
source_path <- function(path) {
  windows_absolute <- nchar(path) >= 3L && substr(path, 2L, 2L) == ":" &&
    substr(path, 3L, 3L) %in% c("/", "\\")
  if (windows_absolute || startsWith(path, "/") || startsWith(path, "\\\\")) path else
    file.path(repo_root, path)
}

verify_run <- function() {
  manifest <- read_json(file.path(run_dir, "run_manifest.json"))
  require_true(is.list(manifest), "Manifest must be an object")
  run_id <- manifest$run_id
  period <- manifest$period
  policy <- manifest$unresolved_policy
  require_true(is.character(run_id) && length(run_id) == 1L && nzchar(run_id), "Missing run_id")
  require_true(is.character(period) && length(period) == 1L && nzchar(period), "Missing period")
  require_true(policy %in% c("strict", "assume_wbd"), "Unknown unresolved policy")
  topology <- manifest$topology
  require_true(is.list(topology), "Missing topology object")
  terminal <- topology$terminal_huc12
  require_true(is.character(terminal) && grepl("^[0-9]{12}$", terminal), "Invalid terminal HUC")

  sources <- manifest$source_files
  require_true(is.list(sources), "Missing source_files")
  for (name in c("qualified_routing", "wbd_huc12", "input")) {
    entry <- sources[[name]]
    require_true(is.list(entry) && is.character(entry$path) && is.character(entry$sha256),
                 paste("Incomplete source provenance:", name))
    path <- source_path(entry$path)
    require_true(file.exists(path), paste("Missing provenance source:", path))
    require_true(identical(unname(tools::sha256sum(path)), tolower(entry$sha256)),
                 paste("Source SHA-256 differs:", name))
  }
  if (!is.null(sources$assumptions)) {
    entry <- sources$assumptions
    require_true(is.list(entry) && is.character(entry$path) && is.character(entry$sha256),
                 "Incomplete assumption provenance")
    path <- source_path(entry$path)
    require_true(file.exists(path), "Missing assumption source")
    require_true(identical(unname(tools::sha256sum(path)), tolower(entry$sha256)),
                 "Assumption SHA-256 differs")
  }
  require_true(is.character(sources$engine_sha256) &&
                 grepl("^[0-9a-f]{64}$", tolower(sources$engine_sha256)),
               "Engine SHA-256 provenance missing or malformed")
  if (identical(manifest$model_version, "0.1A")) {
    # v0.1A is an already accepted historical run; its builder changes in v0.1B.
    require_true(identical(tolower(sources$engine_sha256),
                           "0bc7e92dd43278c9b0a8e570fbe4dfe16b94feeea2c4ccfc58bfa8ccfcc62893"),
                 "Historical v0.1A engine SHA-256 differs from accepted version")
  } else {
    require_true(identical(manifest$model_version, "0.1B") &&
                   identical(manifest$schema_version, "0.1B"),
                 "Unknown model/schema version")
    engine <- file.path(repo_root, "src/python/model_lab/route_water_nutrients.py")
    require_true(identical(unname(tools::sha256sum(engine)), tolower(sources$engine_sha256)),
                 "Engine source SHA-256 differs")
    trace_source <- file.path(repo_root, "src/python/model_lab/trace_huc_paths.py")
    require_true(is.character(sources$trace_generator_sha256) &&
                   identical(unname(tools::sha256sum(trace_source)),
                             tolower(sources$trace_generator_sha256)),
                 "Trace generator source SHA-256 differs")
    require_true("sensitivity_case" %in% names(manifest) &&
                   "sensitivity_config" %in% names(sources),
                 "v0.1B manifest must explicitly declare sensitivity case/configuration (or null)")
    case <- manifest$sensitivity_case
    config_entry <- sources$sensitivity_config
    require_true(is.null(case) == is.null(config_entry),
                 "Sensitivity case and configuration provenance must both be present or both null")
    if (!is.null(config_entry)) {
      require_true(is.list(case) && is.character(case$label) && nzchar(case$label) &&
                     is.character(case$description) && nzchar(case$description),
                   "Sensitivity case metadata incomplete")
      require_true(is.list(config_entry) && is.character(config_entry$path) &&
                     is.character(config_entry$sha256), "Sensitivity configuration provenance missing")
      config_path <- source_path(config_entry$path)
      require_true(file.exists(config_path) &&
                     identical(unname(tools::sha256sum(config_path)), tolower(config_entry$sha256)),
                   "Sensitivity configuration SHA-256 differs")
      config <- read_json(config_path)
      require_true(identical(config$config_version, "0.1B") &&
                     identical(config$period, period), "Sensitivity configuration version/period mismatch")
      configured <- Filter(function(item) identical(item$run_id, run_id), config$runs)
      require_true(length(configured) == 1L, "Run ID missing or duplicated in sensitivity configuration")
      require_true(identical(configured[[1]]$unresolved_policy, policy) &&
                     identical(configured[[1]]$label, case$label) &&
                     identical(configured[[1]]$description, case$description),
                   "Sensitivity case differs from configuration")
      same_source <- function(a, b) {
        identical(normalizePath(source_path(a), winslash = "/", mustWork = TRUE),
                  normalizePath(source_path(b), winslash = "/", mustWork = TRUE))
      }
      assumption_matches <- if (is.null(configured[[1]]$assumptions))
        is.null(sources$assumptions) else
          !is.null(sources$assumptions) &&
          same_source(configured[[1]]$assumptions, sources$assumptions$path)
      require_true(same_source(config$inputs, sources$input$path) &&
                     same_source(config$routing, sources$qualified_routing$path) &&
                     same_source(config$wbd, sources$wbd_huc12$path) && assumption_matches,
                   "Sensitivity configuration source paths differ from manifest")
      require_true(identical(normalizePath(source_path(configured[[1]]$out_dir),
                                           winslash = "/", mustWork = TRUE), run_dir),
                   "Run directory differs from sensitivity configuration")
    }
  }

  balance_fields <- c("run_id", "period", "huc12", "constituent", "unit", "local_input",
                      "upstream_in", "available", "pass_through", "not_forwarded_assumed",
                      "unrouted_at_unresolved", "downstream_out", "boundary_export", "residual",
                      "route_to_huc12", "routing_basis", "qa_status", "physical_geometry", "input_status")
  edge_fields <- c("run_id", "period", "from_huc12", "to_huc12", "constituent", "unit",
                   "amount", "routing_basis", "qa_status", "assumed_unresolved")
  summary_fields <- c("run_id", "period", "constituent", "unit", "total_local_input",
                      "total_not_forwarded_assumed", "total_unrouted_at_unresolved", "boundary_export",
                      "residual", "unresolved_policy")
  input_fields <- c("run_id", "period", "huc12", "constituent", "local_input", "unit",
                    "input_status", "source_id", "method", "uncertainty_note")
  b <- read_table(file.path(run_dir, "huc_balance.csv"), balance_fields)
  e <- read_table(file.path(run_dir, "edge_flux.csv"), edge_fields)
  s <- read_table(file.path(run_dir, "boundary_summary.csv"), summary_fields)
  i <- read_table(file.path(run_dir, "input_snapshot.csv"), input_fields)
  if (identical(manifest$model_version, "0.1B")) {
    expected_files <- c("huc_balance.csv", "edge_flux.csv", "boundary_summary.csv",
                        "input_snapshot.csv", "downstream_trace.csv", "upstream_trace.csv")
    schema <- manifest$output_schema
    require_true(is.list(schema) && setequal(names(schema), expected_files),
                 "v0.1B output_schema must declare exactly six CSV files")
    for (name in expected_files) {
      declared <- unlist(schema[[name]], use.names = FALSE)
      require_true(is.character(declared) && length(declared) > 0L &&
                     !anyDuplicated(declared), paste("Invalid schema declaration:", name))
      actual <- names(read_table(file.path(run_dir, name), declared))
      require_true(identical(actual, declared), paste("CSV columns differ from ordered schema:", name))
    }
    require_true(identical(unlist(schema[["huc_balance.csv"]], use.names = FALSE), balance_fields) &&
                   identical(unlist(schema[["edge_flux.csv"]], use.names = FALSE), edge_fields) &&
                   identical(unlist(schema[["boundary_summary.csv"]], use.names = FALSE), summary_fields) &&
                   identical(unlist(schema[["input_snapshot.csv"]], use.names = FALSE), input_fields),
                 "Core v0.1B schema differs from accepted ledger columns")
  }
  routing <- read_table(source_path(sources$qualified_routing$path),
                        c("from_huc12", "to_huc12", "qa_status", "routing_basis", "physical_geometry"))
  units <- c(water = "m3/period", TN = "kg/period", TP = "kg/period")
  require_true(nrow(b) > 0L && nrow(s) == 3L, "Empty ledger or incomplete summary")
  require_true(all(b$run_id == run_id & b$period == period) &&
               all(e$run_id == run_id & e$period == period) &&
               all(s$run_id == run_id & s$period == period) &&
               all(i$run_id == run_id & i$period == period), "Run/period mismatch")
  for (table in list(b, e, s, i)) {
    require_true(all(table$constituent %in% names(units)), "Unknown constituent")
    require_true(all(table$unit == unname(units[table$constituent])), "Constituent unit mismatch")
  }
  require_true(setequal(s$constituent, names(units)), "Summary must cover water, TN, TP")
  require_true(all(s$unresolved_policy == policy), "Summary policy mismatch")
  require_true(all(grepl("^[0-9]{12}$", b$huc12)), "Invalid HUC identifier")
  hucs <- unique(b$huc12)
  require_true(nrow(b) == length(hucs) * 3L, "Ledger does not cover all HUC/constituent pairs")
  b_key <- unique_keys(b, c("huc12", "constituent"), "huc_balance.csv")
  unique_keys(s, "constituent", "boundary_summary.csv")
  unique_keys(i, c("huc12", "constituent"), "input_snapshot.csv")
  unique_keys(e, c("from_huc12", "to_huc12", "constituent"), "edge_flux.csv")
  require_true(nrow(routing) == length(hucs) - 1L && !anyDuplicated(routing$from_huc12),
               "Qualified topology must give one successor per nonterminal HUC")
  require_true(setequal(routing$from_huc12, setdiff(hucs, terminal)) &&
               all(routing$to_huc12 %in% hucs), "Qualified routes do not cover ledger HUCs")
  allowed_basis <- c(REPLACED_PHYSICAL = "physical_3dhp",
                     REPLACED_AUTHORITATIVE_CONNECTOR = "official_3dhp_connector",
                     ALREADY_REDUNDANT = "physical_nhdplus_hr_existing",
                     UNRESOLVED = "project_inference")
  require_true(all(routing$qa_status %in% names(allowed_basis)) &&
                 all(routing$routing_basis == unname(allowed_basis[routing$qa_status])) &&
                 all(routing$physical_geometry ==
                       ifelse(routing$qa_status %in% c("REPLACED_PHYSICAL", "ALREADY_REDUNDANT"),
                              "True", "False")),
               "Qualified routing class, basis, or geometry flag inconsistent")
  route_index <- match(b$huc12, routing$from_huc12)
  nonterminal <- b$huc12 != terminal
  for (field in c("qa_status", "routing_basis", "physical_geometry")) {
    require_true(all(b[[field]][nonterminal] == routing[[field]][route_index[nonterminal]]),
                 paste("Ledger", field, "differs from qualified route"))
  }
  require_true(all(b$route_to_huc12[nonterminal] == routing$to_huc12[route_index[nonterminal]]),
               "Ledger successor differs from qualified route")
  require_true(all(b$route_to_huc12[!nonterminal] == "" & b$qa_status[!nonterminal] == "BOUNDARY_EXPORT"),
               "Terminal behavior changed")
  require_true(sum(routing$qa_status == "UNRESOLVED") == topology$unresolved_link_count &&
               length(hucs) == topology$huc_count && nrow(routing) == topology$link_count,
               "Topology counts differ from manifest")
  if (isTRUE(topology$accepted_baseline)) {
    require_true(length(hucs) == 252L && nrow(routing) == 251L &&
                 sum(routing$qa_status == "UNRESOLVED") == 12L && terminal == "041000090904" &&
                 identical(topology$external_wbd_target, "041202000300"),
                 "Accepted 252-HUC baseline changed")
  }
  # Follow each successor independently, which detects cycles and unreachable termini.
  successor <- setNames(routing$to_huc12, routing$from_huc12)
  for (origin in hucs) {
    visited <- character()
    current <- origin
    while (current != terminal) {
      require_true(!(current %in% visited) && current %in% names(successor),
                   paste("Cycle or dead end downstream of", origin))
      visited <- c(visited, current)
      current <- successor[[current]]
    }
  }

  local <- numeric_column(b, "local_input", "balance")
  upstream <- numeric_column(b, "upstream_in", "balance")
  available <- numeric_column(b, "available", "balance")
  pass <- numeric_column(b, "pass_through", "balance")
  not_forwarded <- numeric_column(b, "not_forwarded_assumed", "balance")
  unrouted <- numeric_column(b, "unrouted_at_unresolved", "balance")
  downstream <- numeric_column(b, "downstream_out", "balance")
  boundary <- numeric_column(b, "boundary_export", "balance")
  stored_residual <- numeric_column(b, "residual", "balance", FALSE)
  require_true(all(pass <= 1), "Pass-through outside [0,1]")
  same_values(available, local + upstream, "Available quantity")
  same_values(not_forwarded, available * (1 - pass), "Assumed nonforwarded quantity")
  calculated <- local + upstream - not_forwarded - unrouted - downstream - boundary
  same_values(calculated, rep(0, nrow(b)), "Node balances")
  same_values(stored_residual, calculated, "Stored node residuals")
  unresolved <- b$qa_status == "UNRESOLVED"
  if (policy == "strict") {
    same_values(downstream[unresolved], rep(0, sum(unresolved)), "Strict unresolved forwarding")
    same_values(unrouted[unresolved], available[unresolved] - not_forwarded[unresolved],
                "Strict unresolved disposition")
  } else {
    same_values(unrouted[unresolved], rep(0, sum(unresolved)), "WBD sensitivity unrouted disposition")
    same_values(downstream[unresolved], available[unresolved] - not_forwarded[unresolved],
                "WBD sensitivity forwarding")
  }
  same_values(unrouted[!unresolved], rep(0, sum(!unresolved)), "Other unrouted disposition")
  same_values(boundary[nonterminal], rep(0, sum(nonterminal)), "Nonterminal boundary export")
  same_values(downstream[!nonterminal], rep(0, sum(!nonterminal)), "Terminal forwarding")
  same_values(boundary[!nonterminal], available[!nonterminal] - not_forwarded[!nonterminal],
              "Terminal boundary export")
  require_true(all(b$input_status %in% c("synthetic_diagnostic", "parameterized",
                                           "observed_derived", "omitted_zero_diagnostic")),
               "Unknown balance input status")
  require_true(all(i$input_status %in% c("synthetic_diagnostic", "parameterized", "observed_derived")) &&
               all(nzchar(i$source_id) & nzchar(i$method)), "Input provenance/status incomplete")
  require_true(length(unique(i$input_status)) == 1L &&
                 identical(unique(i$input_status), manifest$input_status),
               "Manifest input status differs from snapshot")
  require_true(all(i$huc12 %in% hucs), "Input snapshot references an unknown HUC")
  snapshot_amount <- numeric_column(i, "local_input", "input snapshot")
  snapshot_key <- paste(i$huc12, i$constituent, sep = "|")
  match_input <- match(b_key, snapshot_key)
  expected_local <- ifelse(is.na(match_input), 0, snapshot_amount[match_input])
  same_values(local, expected_local, "Input snapshot vs local input")
  if (any(!is.na(match_input))) {
    require_true(all(b$input_status[!is.na(match_input)] == i$input_status[match_input[!is.na(match_input)]]),
                 "Balance input status differs from snapshot")
  }
  if (any(is.na(match_input))) {
    require_true(all(b$input_status[is.na(match_input)] == "omitted_zero_diagnostic"),
                 "Only synthetic diagnostic inputs may omit zero rows")
  }
  if (is.null(sources$assumptions)) {
    require_true(identical(manifest$assumption_status, "default_unit_pass_through_reference"),
                 "Default pass-through status differs from manifest")
    same_values(pass, rep(1, nrow(b)), "Default pass-through")
  } else {
    assumption_path <- source_path(sources$assumptions$path)
    a <- read_table(assumption_path, c("huc12", "constituent", "pass_through",
                                      "assumption_status", "source_id", "notes"))
    require_true(all(a$huc12 %in% hucs & a$constituent %in% names(units)) &&
                   all(nzchar(a$source_id)), "Assumption provenance/HUC/constituent invalid")
    require_true(length(unique(a$assumption_status)) == 1L &&
                   identical(unique(a$assumption_status), manifest$assumption_status) &&
                   manifest$assumption_status %in% c("parameterized", "synthetic_diagnostic"),
                 "Assumption status differs from manifest")
    assumption_key <- unique_keys(a, c("huc12", "constituent"), "assumption source")
    assumption_pass <- numeric_column(a, "pass_through", "assumption source")
    require_true(all(assumption_pass <= 1), "Assumption pass-through exceeds one")
    match_assumption <- match(b_key, assumption_key)
    expected_pass <- ifelse(is.na(match_assumption), 1, assumption_pass[match_assumption])
    same_values(pass, expected_pass, "Assumption source vs ledger pass-through")
  }

  require_true(all(e$from_huc12 %in% hucs & e$to_huc12 %in% hucs), "Edge HUC absent from ledger")
  edge_amount <- numeric_column(e, "amount", "edge")
  edge_source <- paste(e$from_huc12, e$constituent, sep = "|")
  edge_target <- paste(e$to_huc12, e$constituent, sep = "|")
  source_index <- match(edge_source, b_key)
  require_true(all(e$to_huc12 == b$route_to_huc12[source_index]) &&
               all(e$qa_status == b$qa_status[source_index]) &&
               all(e$routing_basis == b$routing_basis[source_index]), "Edge route metadata mismatch")
  require_true(all(e$assumed_unresolved == ifelse(e$qa_status == "UNRESOLVED", "True", "False")),
               "Edge unresolved-assumption flag mismatch")
  if (policy == "strict") require_true(!any(e$qa_status == "UNRESOLVED"),
                                        "Strict run crosses unresolved edge")
  group_sum <- function(value, key, wanted) {
    totals <- tapply(value, key, sum)
    result <- unname(totals[wanted])
    result[is.na(result)] <- 0
    result
  }
  same_values(downstream, group_sum(edge_amount, edge_source, b_key), "Outgoing edge flux")
  same_values(upstream, group_sum(edge_amount, edge_target, b_key), "Incoming edge flux")
  for (constituent in names(units)) {
    rows <- b$constituent == constituent
    sr <- s[s$constituent == constituent, , drop = FALSE]
    sum_local <- numeric_column(sr, "total_local_input", "summary")
    sum_not_forwarded <- numeric_column(sr, "total_not_forwarded_assumed", "summary")
    sum_unrouted <- numeric_column(sr, "total_unrouted_at_unresolved", "summary")
    sum_boundary <- numeric_column(sr, "boundary_export", "summary")
    sum_residual <- numeric_column(sr, "residual", "summary", FALSE)
    same_values(sum_local, sum(local[rows]), paste(constituent, "summary input"))
    same_values(sum_not_forwarded, sum(not_forwarded[rows]), paste(constituent, "summary not forwarded"))
    same_values(sum_unrouted, sum(unrouted[rows]), paste(constituent, "summary unrouted"))
    same_values(sum_boundary, sum(boundary[rows]), paste(constituent, "summary boundary"))
    closure <- sum_local - sum_not_forwarded - sum_unrouted - sum_boundary
    same_values(closure, 0, paste(constituent, "run balance"))
    same_values(sum_residual, closure, paste(constituent, "stored run residual"))
  }
  if (identical(manifest$model_version, "0.1B")) {
    trace_fields <- c("run_id", "period", "unresolved_policy", "focus_huc12",
                      "traced_huc12", "hops", "policy_reachable", "first_unresolved_link_from_huc12")
    require_true(identical(unlist(manifest$output_schema[["downstream_trace.csv"]], use.names = FALSE), trace_fields) &&
                   identical(unlist(manifest$output_schema[["upstream_trace.csv"]], use.names = FALSE), trace_fields),
                 "Trace schema differs from v0.1B contract")
    d <- read_table(file.path(run_dir, "downstream_trace.csv"), trace_fields)
    u <- read_table(file.path(run_dir, "upstream_trace.csv"), trace_fields)
    require_true(identical(names(d), trace_fields) && identical(names(u), trace_fields),
                 "Trace CSV columns differ from v0.1B contract")
    for (tab in list(d, u)) {
      require_true(all(tab$run_id == run_id & tab$period == period &
                         tab$unresolved_policy == policy), "Trace run/period/policy mismatch")
      require_true(all(tab$focus_huc12 %in% hucs & tab$traced_huc12 %in% hucs),
                   "Trace references HUC absent from ledger")
      require_true(all(tab$policy_reachable %in% c("True", "False")),
                   "Trace policy_reachable must be True or False")
      require_true(all(tab$first_unresolved_link_from_huc12 == "" |
                         tab$first_unresolved_link_from_huc12 %in% routing$from_huc12[routing$qa_status == "UNRESOLVED"]),
                   "Trace unresolved-link marker does not identify an unresolved source")
      hops <- numeric_column(tab, "hops", "trace")
      require_true(all(hops == floor(hops)), "Trace hops must be whole numbers")
      unique_keys(tab, c("focus_huc12", "traced_huc12"), "trace CSV")
    }
    expected <- list()
    for (focus in hucs) {
      current <- focus
      hops <- 0L
      cut <- ""
      repeat {
        expected[[length(expected) + 1L]] <- c(
          focus_huc12 = focus, traced_huc12 = current, hops = as.character(hops),
          policy_reachable = if (policy == "assume_wbd" || cut == "") "True" else "False",
          first_unresolved_link_from_huc12 = cut)
        if (current == terminal) break
        if (cut == "" && routing$qa_status[match(current, routing$from_huc12)] == "UNRESOLVED") {
          cut <- current
        }
        current <- successor[[current]]
        hops <- hops + 1L
      }
    }
    expected <- as.data.frame(do.call(rbind, expected), stringsAsFactors = FALSE)
    if (policy == "assume_wbd") {
      # The first unresolved crossing remains marked as a topology/evidence cue,
      # even though the sensitivity policy permits hypothetical forwarding.
      expected$policy_reachable[] <- "True"
    }
    compare_trace <- function(actual, wanted, label) {
      require_true(nrow(actual) == nrow(wanted), paste(label, "has wrong path-pair count"))
      actual <- actual[order(actual$focus_huc12, actual$traced_huc12), trace_fields, drop = FALSE]
      wanted <- wanted[order(wanted$focus_huc12, wanted$traced_huc12), trace_fields, drop = FALSE]
      rownames(actual) <- NULL
      rownames(wanted) <- NULL
      require_true(identical(actual, wanted), paste(label, "differs from independently walked topology/policy"))
    }
    downstream_expected <- cbind(
      data.frame(run_id = rep(run_id, nrow(expected)), period = rep(period, nrow(expected)),
                 unresolved_policy = rep(policy, nrow(expected))), expected)
    compare_trace(d, downstream_expected, "Downstream trace")
    upstream_expected <- downstream_expected
    upstream_expected$focus_huc12 <- downstream_expected$traced_huc12
    upstream_expected$traced_huc12 <- downstream_expected$focus_huc12
    compare_trace(u, upstream_expected, "Upstream trace")
  }
  scope <- if (identical(manifest$model_version, "0.1B"))
    "ledger, topology, provenance, units, status, schema, and traces" else
    "ledger, topology, provenance, units, and status"
  cat(paste0("PASS: independent R ", scope, ": ", run_dir, "\n"))
}

tryCatch(verify_run(), error = function(problem) {
  cat("FAIL:", conditionMessage(problem), "\n", file = stderr())
  quit(status = 1L)
})
