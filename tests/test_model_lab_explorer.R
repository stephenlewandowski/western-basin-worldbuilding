#!/usr/bin/env Rscript
# Read-only checks of the accepted v0.1B products as the explorer sees them.

script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
source_file <- if (sys.nframe() > 0L) sys.frame(1)$ofile else NULL
repo_root <- if (!is.null(source_file) || length(script_arg) == 1L) {
  script_path <- normalizePath(if (!is.null(source_file)) source_file else
                                sub("^--file=", "", script_arg), winslash = "/", mustWork = TRUE)
  normalizePath(file.path(dirname(script_path), ".."), winslash = "/", mustWork = TRUE)
} else {
  # Also support source("tests/test_model_lab_explorer.R") from the repo root.
  normalizePath(".", winslash = "/", mustWork = TRUE)
}
source(file.path(repo_root, "src/R/model_lab/explorer/data.R"))

check <- function(condition, message) {
  if (!isTRUE(condition)) stop(message, call. = FALSE)
}
check_equal <- function(actual, expected, message) {
  check(identical(actual, expected), message)
}
check_close <- function(actual, expected, message) {
  check(length(actual) == length(expected) && all(is.finite(actual)) &&
          all(abs(actual - expected) <= 1e-9), message)
}
expect_error <- function(expr, pattern) {
  error <- tryCatch({ force(expr); NULL }, error = function(e) conditionMessage(e))
  check(is.character(error) && grepl(pattern, error, fixed = TRUE),
        paste("Expected error containing:", pattern, "; received:", error))
}

model <- load_model_lab(repo_root)
check_equal(names(model$runs), c("strict", "assume_wbd", "tn_half_pass"),
            "Three configured cases did not load in expected order")
check_equal(model$schema_version, "0.1B", "Unsupported explorer schema")
check_equal(length(model$huc_ids), 252L, "Wrong HUC count")
check_equal(length(unique(model$geography$huc12)), 252L, "Duplicate HUC geometry")
check(setequal(model$huc_ids, model$geography$huc12), "HUC geometry join incomplete")
check(all(nzchar(model$geography$name)), "HUC names are missing")
check(all(vapply(model$geography$geometry, function(g) g$type %in%
                   c("Polygon", "MultiPolygon"), logical(1))), "Invalid HUC geometry")

for (run in model$runs) {
  check_equal(run$manifest$schema_version, "0.1B", "Manifest schema mismatch")
  check_equal(names(run$tables), sub("\\.csv$", "", names(explorer_schema)),
              "Six CSVs did not load")
  for (filename in names(explorer_schema)) {
    check_equal(names(run$tables[[sub("\\.csv$", "", filename)]]),
                explorer_schema[[filename]], paste("CSV header mismatch:", filename))
    check_equal(unlist(run$manifest$output_schema[[filename]], use.names = FALSE),
                explorer_schema[[filename]], paste("Manifest header mismatch:", filename))
  }
  for (constituent in c("water", "TN", "TP")) {
    check_equal(nrow(balance_for(run, constituent)), 252L, "Incomplete HUC balances")
    check_equal(nrow(summary_for(run, constituent)), 1L, "Missing summary")
  }
}

clean <- trace_for(model$runs$strict, "downstream", "041000090603")
check_equal(clean$traced_huc12, c("041000090603", "041000090903", "041000090904"),
            "Clean downstream structural route changed")
check_equal(clean$hops, 0:2, "Clean downstream hop order changed")
check(all(clean$policy_reachable) &&
        all(clean$first_unresolved_link_from_huc12 == ""),
      "Clean route unexpectedly unresolved")

unresolved <- trace_for(model$runs$strict, "downstream", "041000090402")
check_equal(unresolved$hops, 0:6, "Unresolved structural route changed")
check_equal(unresolved$policy_reachable, c(TRUE, rep(FALSE, 6)),
            "Strict unresolved reachability changed")
check(all(unresolved$first_unresolved_link_from_huc12[-1] == "041000090402"),
      "Unresolved-link provenance changed")

wbd <- trace_for(model$runs$assume_wbd, "downstream", "041000090402")
check_equal(wbd$traced_huc12, unresolved$traced_huc12,
            "WBD sensitivity erased structural path")
check(all(wbd$policy_reachable) &&
        all(wbd$first_unresolved_link_from_huc12[-1] == "041000090402"),
      "WBD sensitivity reachability/provenance changed")

terminal <- trace_for(model$runs$strict, "downstream", "041000090904")
check_equal(nrow(terminal), 1L, "Terminal has false downstream continuation")
check_equal(terminal$hops, 0L, "Terminal self hop changed")
check(terminal$policy_reachable[[1L]], "Terminal self row unreachable")

upstream <- trace_for(model$runs$strict, "upstream", "041000030106")
check_equal(nrow(upstream), 6L, "Upstream contributor set changed")
check_equal(upstream$hops[upstream$traced_huc12 == "041000030106"], 0L,
            "Upstream self hop changed")
unreachable <- upstream[upstream$traced_huc12 == "041000030103", , drop = FALSE]
check_equal(nrow(unreachable), 1L, "Expected unresolved upstream path absent")
check(!unreachable$policy_reachable[[1L]] &&
        unreachable$first_unresolved_link_from_huc12[[1L]] == "041000030103",
      "Upstream unresolved direction/provenance changed")

for (constituent in c("water", "TN", "TP")) {
  strict <- summary_for(model$runs$strict, constituent)
  wbd_summary <- summary_for(model$runs$assume_wbd, constituent)
  half <- summary_for(model$runs$tn_half_pass, constituent)
  fields <- c("total_local_input", "total_not_forwarded_assumed",
              "total_unrouted_at_unresolved", "boundary_export", "residual")
  check_close(unlist(strict[fields], use.names = FALSE), c(2, 0, 1, 1, 0),
              paste("Strict balance changed for", constituent))
  check_close(unlist(wbd_summary[fields], use.names = FALSE), c(2, 0, 0, 2, 0),
              paste("WBD balance changed for", constituent))
  expected_half <- if (constituent == "TN") c(2, 0.5, 1, 0.5, 0) else c(2, 0, 1, 1, 0)
  check_close(unlist(half[fields], use.names = FALSE), expected_half,
              paste("Half-pass balance changed for", constituent))
}

expect_error(explorer_file(repo_root, "outputs/model_lab/nonexistent.csv"), "file missing")
expect_error(explorer_check_version(list(schema_version = "0.2A", model_version = "0.1B"),
                                    "altered manifest"), "Unsupported Model Lab schema version")
bad_csv <- tempfile(fileext = ".csv")
writeLines("wrong,header\n1,2", bad_csv)
expect_error(explorer_read_csv(bad_csv, explorer_schema[["boundary_summary.csv"]]),
             "CSV header mismatch")
unlink(bad_csv)

# Corrupt scratch copies of accepted products; never modify the repository inputs.
check_rejections <- function() {
  fixture <- tempfile("model_lab_explorer_")
  dir.create(fixture)
  on.exit(unlink(fixture, recursive = TRUE), add = TRUE)
  run_ids <- vapply(model$runs, function(run) run$manifest$run_id, "")
  files <- c(unname(explorer_sources), "data/model_lab/v01b_tn_half_pass_assumptions.csv",
             "src/python/model_lab/route_water_nutrients.py",
             "src/python/model_lab/trace_huc_paths.py",
             unlist(lapply(run_ids, function(id) file.path("outputs/model_lab", id,
                          c("run_manifest.json", names(explorer_schema)))), use.names = FALSE))
  for (file in files) {
    target <- file.path(fixture, file)
    dir.create(dirname(target), recursive = TRUE, showWarnings = FALSE)
    check(file.copy(file.path(repo_root, file), target), paste("Fixture copy failed:", file))
  }
  # Simulate fresh checkouts on both platforms. The saved manifest mixes source
  # hashes recorded under LF and CRLF, so only newline conversion is tolerated.
  for (newline in c("\n", "\r\n")) {
    for (file in files) {
      original <- file.path(repo_root, file)
      bytes <- readBin(original, "raw", n = file.info(original)$size)
      lf <- gsub("\r\n", "\n", rawToChar(bytes), fixed = TRUE)
      writeBin(charToRaw(gsub("\n", newline, lf, fixed = TRUE)), file.path(fixture, file))
    }
    check_equal(names(load_model_lab(fixture)$runs), names(model$runs),
                "Git checkout newline conversion rejected unchanged sources")
  }
  for (file in files) check(file.copy(file.path(repo_root, file), file.path(fixture, file),
                                    overwrite = TRUE), paste("Fixture restore failed:", file))
  mutate_file <- function(relative, change, pattern) {
    path <- file.path(fixture, relative)
    prior <- readBin(path, "raw", n = file.info(path)$size)
    on.exit(writeBin(prior, path), add = TRUE)
    change(path)
    expect_error(load_model_lab(fixture), pattern)
  }
  mutate_json <- function(relative, change, pattern) {
    mutate_file(relative, function(path) {
      value <- explorer_read_json(path)
      jsonlite::write_json(change(value), path, auto_unbox = TRUE, pretty = TRUE, null = "null")
    }, pattern)
  }
  mutate_csv <- function(filename, change, pattern) {
    mutate_file(file.path("outputs/model_lab", run_ids[[1L]], filename), function(path) {
      tab <- utils::read.csv(path, colClasses = "character", check.names = FALSE,
                             na.strings = character())
      utils::write.csv(change(tab), path, row.names = FALSE, na = "")
    }, pattern)
  }
  manifest <- file.path("outputs/model_lab", run_ids[[1L]], "run_manifest.json")
  mutate_json(manifest, function(x) { x$source_files$sensitivity_config$sha256 <- "invalid"; x },
              "Invalid SHA-256")
  mutate_file(explorer_sources[["qualified_routing"]],
              function(path) cat("\n", file = path, append = TRUE), "Source SHA-256 differs")
  mutate_file(explorer_sources[["wbd_huc12"]],
              function(path) cat("\n", file = path, append = TRUE), "Source SHA-256 differs")
  mutate_file("src/python/model_lab/route_water_nutrients.py",
              function(path) cat("\n", file = path, append = TRUE), "Source SHA-256 differs")
  mutate_json(manifest, function(x) { x$source_files$input$path <- "wrong.csv"; x },
              "Source path mismatch")
  mutate_json(explorer_sources[["sensitivity_config"]],
              function(x) { x$runs[[1]]$out_dir <- "outputs/model_lab/other"; x },
              "Configured case paths/policy mismatch")
  mutate_json(explorer_sources[["sensitivity_config"]],
              function(x) { x$inputs <- "data/model_lab/other.csv"; x },
              "Configuration source path mismatch")
  mutate_json(manifest, function(x) { x$input_status <- "observed_derived"; x },
              "Synthetic diagnostic metadata mismatch")
  mutate_json(manifest, function(x) { x$interpretation <- list(); x },
              "Synthetic diagnostic metadata mismatch")
  mutate_csv("huc_balance.csv", function(x) { x$unit[[1]] <- "kg/day"; x },
             "Constituent/unit mismatch")
  mutate_csv("huc_balance.csv", function(x) { x$constituent[[1]] <- "unknown"; x },
             "Constituent/unit mismatch")
  mutate_csv("input_snapshot.csv", function(x) { x$input_status[[1]] <- "observed_derived"; x },
             "Non-synthetic input status")
  mutate_csv("boundary_summary.csv", function(x) rbind(x, x[1, ]), "Duplicate row key")
  mutate_csv("huc_balance.csv", function(x) { x$huc12[[1]] <- "999999999999"; x },
             "balance/geography join mismatch")
  mutate_csv("downstream_trace.csv", function(x) rbind(x, x[1, ]), "Duplicate row key")
  mutate_csv("upstream_trace.csv", function(x)
               x[!(x$focus_huc12 == "041000090904" & x$traced_huc12 == "041000090904"), ],
             "trace self rows")
  mutate_csv("downstream_trace.csv", function(x) { x$hops[[1]] <- "0.5"; x }, "Invalid trace hops")
  mutate_csv("downstream_trace.csv", function(x) { x$policy_reachable[[1]] <- "maybe"; x },
             "Invalid Boolean field")
  mutate_csv("huc_balance.csv", function(x) { x$local_input[[1]] <- "-1"; x },
             "Out-of-range numeric field")
  mutate_csv("huc_balance.csv", function(x) { x$pass_through[[1]] <- "1.1"; x },
             "Out-of-range numeric field")
  mutate_csv("huc_balance.csv", function(x) {
    x$local_input[which(x$input_status == "omitted_zero_diagnostic")[[1]]] <- "1"; x
  }, "nonzero omitted input")

  # Case identity is independent of the configuration's array order. Update the
  # scratch manifests' config hash to keep this alternate fixture self-consistent.
  path <- file.path(fixture, explorer_sources[["sensitivity_config"]])
  config <- explorer_read_json(path)
  config$runs <- rev(config$runs)
  jsonlite::write_json(config, path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  for (id in run_ids) {
    manifest_path <- file.path(fixture, "outputs/model_lab", id, "run_manifest.json")
    value <- explorer_read_json(manifest_path)
    value$source_files$sensitivity_config$sha256 <- unname(tools::sha256sum(path))
    jsonlite::write_json(value, manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  }
  check_equal(names(load_model_lab(fixture)$runs), names(model$runs), "Case order depends on config order")
}
check_rejections()

# Exercise the displayed outputs, not just the loader. testServer needs no browser
# and does not execute the Python engine or alter any saved run products.
check(requireNamespace("shiny", quietly = TRUE), "Shiny is required for explorer display checks")
load_app_for_test <- function() {
  prior_dir <- getwd()
  on.exit(setwd(prior_dir), add = TRUE)
  setwd(repo_root)
  app_env <- new.env(parent = globalenv())
  source(file.path(repo_root, "src/R/model_lab/explorer/app.R"), local = app_env)
  app_env
}
app_env <- load_app_for_test()
has_text <- function(output_value, needle) {
  grepl(needle, paste(output_value, collapse = " "), fixed = TRUE)
}
shiny::testServer(app_env$server, {
  session$setInputs(case = "strict", constituent = "water",
                    huc = "041000090402", direction = "downstream")
  check(has_text(output$trace_caption, "7 HUC records"), "Strict downstream caption missing")
  check(has_text(output$trace_table, "041000090402") &&
          has_text(output$trace_table, "No"), "Strict unresolved trace not displayed")
  check(has_text(output$ledger_table, "Unrouted at unresolved link"),
        "HUC accounting disposition missing")
  check(has_text(output$mass_table, "Strict unresolved-link reference") &&
          has_text(output$mass_table, "TN pass-through arithmetic sensitivity"),
        "Three-case comparison missing")
  check(has_text(output$run_facts, "v01b_unit_pulse_strict") &&
          has_text(output$run_facts, "0.1B"), "Strict run facts missing")
  check(has_text(output$source_table, "engine_sha256") &&
          has_text(output$limitations, "not a measured Maumee or Lake Erie load"),
        "Provenance or scientific boundaries missing")
  check(!is.null(output$huc_map$src) && !is.null(output$mass_chart$src),
        "Map or mass comparison did not render")

  session$setInputs(case = "assume_wbd", constituent = "water",
                    huc = "041000090402", direction = "downstream")
  check(has_text(output$trace_table, "041000090402") &&
          all(active_trace()$policy_reachable) &&
          !grepl("<td[^>]*>\\s*No\\s*</td>", output$trace_table),
        "WBD policy reachability not displayed")
  check(has_text(output$run_facts, "v01b_unit_pulse_assume_wbd") &&
          !is.null(output$huc_map$src), "WBD case or map missing")

  session$setInputs(case = "tn_half_pass", constituent = "TN",
                    huc = "041000030106", direction = "upstream")
  check(has_text(output$trace_caption, "6 HUC records on the upstream"),
        "Upstream contributor caption missing")
  check(has_text(output$trace_table, "041000030103") &&
          has_text(output$trace_table, "No"), "Upstream unresolved path missing")
  check(has_text(output$mass_table, "0.5") &&
          has_text(output$ledger_caption, "TN | kg/period"),
        "TN half-pass or units not displayed")
  check(has_text(output$run_facts, "v01b_unit_pulse_tn_half_pass") &&
          !is.null(output$mass_chart$src), "TN case or chart missing")

  session$setInputs(case = "strict", constituent = "TP",
                    huc = "041000090904", direction = "downstream")
  check(has_text(output$trace_caption, "1 HUC record on the downstream") &&
          has_text(output$ledger_caption, "TP | kg/period") &&
          !is.null(output$huc_map$src), "Terminal HUC or constituent switch failed")
})

cat("Model Lab explorer checks passed: 3 runs, 252 HUCs, schema, balances, errors, and Shiny displays.\n")
