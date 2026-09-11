#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 15B.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)
reports <- file.path(root, "reports")
final_name <- "phase15b_technology_convergence_futures_freeze_manifest.json"
working_name <- "phase15b_manifest.json"
artifact_check_name <- "phase15b_artifact_check.json"
r_result_name <- "phase15b_r_validation_result.json"
review_name <- "phase15b_independent_review.md"
initial_name <- "phase15b_independent_review_initial.md"
second_name <- "phase15b_independent_review_second_failed.md"
phase15a_name <- "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
phase14a_name <- "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
phase14b_name <- "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
source_commit <- "9b842db483d9ae3f58189607ef17c97d94790102"
expected_prior_entries <- 565L
expected_prior_unique <- 556L
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
working_artifacts <- c(
  "data/processed/scenarios/technology_convergence_relationships.csv",
  "data/processed/scenarios/technology_dependency_states.csv",
  "data/processed/scenarios/technology_family_states.csv",
  "data/processed/scenarios/technology_governance_states.csv",
  "data/processed/scenarios/technology_scenario_assumptions.csv",
  "data/processed/scenarios/technology_scenario_comparison.csv",
  "data/processed/scenarios/technology_system_states.csv",
  "data/processed/scenarios/technology_uncertainty_states.csv",
  "outputs/figures/technology_convergence_futures.png",
  "outputs/figures/technology_convergence_futures.svg",
  "outputs/figures/technology_cross_system_effects.png",
  "outputs/figures/technology_cross_system_effects.svg",
  file.path("reports", artifact_check_name),
  "reports/phase15b_biosecurity_futures.md",
  "reports/phase15b_provenance_check.md",
  "reports/phase15b_qa.md",
  file.path("reports", r_result_name),
  "reports/phase15b_scenario_comparison.md",
  "reports/phase15b_technology_convergence_futures.md",
  "src/R/systems/validate_phase15b_technology.R",
  "src/python/systems/build_phase15b_technology.py",
  "src/python/systems/validate_phase15b_technology.py"
)
freeze_validators <- c("src/python/systems/validate_phase15b_freeze.py", "src/R/systems/validate_phase15b_freeze.R")
final_artifacts <- sort(c(working_artifacts, file.path("reports", working_name), file.path("reports", review_name), file.path("reports", initial_name), file.path("reports", second_name), freeze_validators))
status_surfaces <- c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
path <- function(rel) file.path(root, gsub("/", .Platform$file.sep, rel, fixed = TRUE))
read_csv_rel <- function(rel) read.csv(path(rel), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
text_rel <- function(rel) paste(readLines(path(rel), warn = FALSE, encoding = "UTF-8"), collapse = " ")
raw_bytes <- function(file) readBin(file, "raw", n = as.numeric(file.info(file)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix); on.exit(unlink(tmp), add = TRUE); writeBin(raw, tmp)
  command <- Sys.which("sha256sum")
  if (nzchar(command)) {
    output <- system2(command, tmp, stdout = TRUE, stderr = TRUE)
    hits <- regmatches(paste(output, collapse = " "), gregexpr("[0-9a-fA-F]{64}", paste(output, collapse = " "), perl = TRUE))[[1]]
    stop_if(length(hits) > 0L, "sha256sum failed"); return(tolower(hits[[1]]))
  }
  command <- Sys.which("certutil"); stop_if(nzchar(command), "Neither sha256sum nor certutil is available")
  output <- system2(command, c("-hashfile", normalizePath(tmp, winslash = "\\", mustWork = TRUE), "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) > 0L, "certutil failed"); hits[[1]]
}
sha256_cache <- new.env(parent = emptyenv())
sha256_file_cached <- function(file) {
  key <- normalizePath(file, winslash = "/", mustWork = TRUE)
  if (exists(key, envir = sha256_cache, inherits = FALSE)) return(get(key, envir = sha256_cache, inherits = FALSE))
  value <- sha256_raw(raw_bytes(file), tools::file_ext(file)); assign(key, value, envir = sha256_cache); value
}
portable_match <- function(file, expected, recorded = NA_real_) {
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing artifact", file))
  raw <- raw_bytes(file); raw_hash <- sha256_file_cached(file)
  if (tolower(expected) == tolower(raw_hash) && (is.na(recorded) || as.numeric(recorded) == length(raw))) return(TRUE)
  hashes <- c(raw_hash); lengths <- c(length(raw))
  if (tolower(tools::file_ext(file)) %in% tolower(text_ext)) {
    canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))
    crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed = TRUE))
    hashes <- c(hashes, sha256_raw(canonical, tools::file_ext(file)), sha256_raw(crlf, tools::file_ext(file)))
    lengths <- c(lengths, length(canonical), length(crlf))
  }
  tolower(expected) %in% hashes && (is.na(recorded) || as.numeric(recorded) %in% lengths)
}
manifest_entries <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  hits <- which(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  if (!length(hits)) hits <- which(grepl('"files"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  stop_if(length(hits) > 0L, paste("missing artifacts collection", file)); start <- hits[[1]]
  rel <- character(); hashes <- character(); bytes <- numeric(); current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(direct) == 3L) { append_current(); rel <- c(rel, direct[[2]]); hashes <- c(hashes, direct[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl = TRUE))[[1]]
    if (length(nested) == 2L) { append_current(); current <- nested[[2]] }
    hit <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(hit) == 2L && !is.na(current)) current_hash <- hit[[2]]
    size <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl = TRUE))[[1]]
    if (length(size) == 2L && !is.na(current)) current_bytes <- as.numeric(size[[2]])
  }
  append_current(); data.frame(rel = rel, sha256 = hashes, bytes = bytes, stringsAsFactors = FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels = character()) {
  file <- file.path(reports, name); stop_if(file.exists(file), paste("missing manifest", name)); x <- manifest_entries(file)
  stop_if(nrow(x) == expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(setequal(gsub("\\\\", "/", as.character(x$rel)), gsub("\\\\", "/", expected_rels)), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}

final_text <- text_rel(file.path("reports", final_name))
for (term in c(
  '"accepted_phase": "15B"', '"baseline": "Technology Convergence Futures, 2050 / 2075"', '"status": "ACCEPTED / FROZEN"',
  paste0('"source_commit": "', source_commit, '"'), '"scenario_horizon_states": 6', '"assumptions": 48', '"technology_family_states": 48',
  '"convergence_relationships": 60', '"system_states": 78', '"dependency_states": 72', '"governance_states": 48', '"uncertainty_states": 60',
  '"comparison_rows": 6', '"technology_families": 8', '"phase14_systems": 13', '"qualitative_only": true', '"forecast": false',
  '"numeric_future_values_adopted": false', '"phase15a_status": "ACCEPTED / FROZEN"', '"phase14_status": "COMPLETE / ACCEPTED / FROZEN"',
  '"phase16_status": "NOT IMPLEMENTED"', '"great_black_swamp": "C — HOLD / noncanonical"', '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"',
  '"Phase 6B manifest status wording mismatch"', '"Phase 3A missing manifest status"', '"Phase 2A superseded legacy worktree"',
  '"release_created": false', '"tag_created": false'
)) stop_if(grepl(term, final_text, fixed = TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(final_artifacts), final_artifacts)
working <- verify_manifest(working_name, length(working_artifacts), sort(working_artifacts))
working_text <- text_rel(file.path("reports", working_name)); stop_if(grepl('"phase": "15B"', working_text, fixed = TRUE) && grepl('"status": "implemented_validated_pending_sol_acceptance"', working_text, fixed = TRUE), "working manifest identity")
artifact_check <- tolower(text_rel(file.path("reports", artifact_check_name))); for (term in c('"phase": "15b"', '"passed": true', '"errors": []', '"prior_freeze_entries": 565', '"prior_freeze_unique_paths": 556')) stop_if(grepl(term, artifact_check, fixed = TRUE), paste("artifact check", term))
r_result <- tolower(text_rel(file.path("reports", r_result_name))); for (term in c('"phase": "15b"', '"passed": true')) stop_if(grepl(term, r_result, fixed = TRUE), paste("R result", term))

phase15a <- text_rel(file.path("reports", phase15a_name)); phase14a <- text_rel(file.path("reports", phase14a_name)); phase14b <- text_rel(file.path("reports", phase14b_name))
for (pair in list(c(phase15a_name, '"accepted_phase": "15A"'), c(phase14a_name, '"accepted_phase": "14A"'), c(phase14b_name, '"accepted_phase": "14B"'))) stop_if(grepl(pair[[2]], text_rel(file.path("reports", pair[[1]])), fixed = TRUE) && grepl('"status": "ACCEPTED / FROZEN"', text_rel(file.path("reports", pair[[1]])), fixed = TRUE), paste("manifest status", pair[[1]]))
phase15a_x <- verify_manifest(phase15a_name, 30L); phase14a_x <- verify_manifest(phase14a_name, 24L); phase14b_x <- verify_manifest(phase14b_name, 23L)

ontology_lines <- readLines(path("metadata/atlas_systems.yml"), warn = FALSE, encoding = "UTF-8")
system_ids <- unique(sub(".*system_id:[[:space:]]*([^[:space:]]+).*", "\\1", ontology_lines[grepl("^[[:space:]]*- system_id:", ontology_lines)]))
stop_if(length(system_ids) == 13L, "Phase 14 systems")
scenario_dir <- file.path(root, "data", "processed", "scenarios")
assumptions <- read_csv_rel("data/processed/scenarios/technology_scenario_assumptions.csv")
family <- read_csv_rel("data/processed/scenarios/technology_family_states.csv")
convergence <- read_csv_rel("data/processed/scenarios/technology_convergence_relationships.csv")
systems <- read_csv_rel("data/processed/scenarios/technology_system_states.csv")
dependency <- read_csv_rel("data/processed/scenarios/technology_dependency_states.csv")
governance <- read_csv_rel("data/processed/scenarios/technology_governance_states.csv")
uncertainty <- read_csv_rel("data/processed/scenarios/technology_uncertainty_states.csv")
comparison <- read_csv_rel("data/processed/scenarios/technology_scenario_comparison.csv")
expected_ids <- c("A2050", "A2075", "B2050", "B2075", "C2050", "C2075")
check_state <- function(x, n, key) {
  stop_if(nrow(x) == n && !anyDuplicated(x[[key]]), paste("count/id", key))
  stop_if(setequal(unique(x$scenario_id), expected_ids) && all(as.integer(x$horizon) == as.integer(substr(x$scenario_id, 2, 5))), paste("scenario/horizon", key))
  stop_if(all(x$reality_status == "scenario") && all(x$canon_status == "scenario") && all(x$relationship_basis == "scenario_assumption"), paste("scenario status", key))
}
stop_if(nrow(assumptions) == 48L && !anyDuplicated(assumptions$assumption_id) && setequal(unique(assumptions$scenario_id), expected_ids) && all(assumptions$classification == "SCENARIO ASSUMPTION") && all(assumptions$numeric_future_value_adopted == "false"), "assumptions")
check_state(family, 48L, "state_id"); check_state(convergence, 60L, "relationship_id"); check_state(systems, 78L, "state_id"); check_state(dependency, 72L, "dependency_state_id"); check_state(governance, 48L, "governance_state_id"); check_state(uncertainty, 60L, "uncertainty_state_id")
allowed_families <- c("AI / ADVANCED COMPUTE / AUTOMATION", "ADVANCED SENSING / AUTONOMOUS SYSTEMS", "CYBERSECURITY / DIGITAL RESILIENCE", "ADVANCED ENERGY", "ADVANCED MATERIALS / MANUFACTURING", "QUANTUM TECHNOLOGIES", "BIOTECHNOLOGY / GENETIC ENGINEERING", "PRIVACY / SURVEILLANCE / DATA GOVERNANCE")
stop_if(setequal(unique(family$technology_family), allowed_families) && all(table(family$scenario_id) == 8L), "family coverage")
stop_if(setequal(unique(systems$system_id), system_ids) && all(table(systems$scenario_id) == 13L), "system coverage")
model_text <- tolower(paste(capture.output(write.table(assumptions, row.names = FALSE, quote = FALSE)), capture.output(write.table(family, row.names = FALSE, quote = FALSE)), capture.output(write.table(convergence, row.names = FALSE, quote = FALSE)), capture.output(write.table(systems, row.names = FALSE, quote = FALSE)), capture.output(write.table(dependency, row.names = FALSE, quote = FALSE)), capture.output(write.table(governance, row.names = FALSE, quote = FALSE)), capture.output(write.table(uncertainty, row.names = FALSE, quote = FALSE)), capture.output(write.table(comparison, row.names = FALSE, quote = FALSE)), collapse = " "))
stop_if(!grepl("[0-9]+[[:space:]]*%", model_text, perl = TRUE), "unsupported percentage")
stop_if(grepl("scenario", model_text, fixed = TRUE) && grepl("not a forecast", model_text, fixed = TRUE), "scenario boundary")
stop_if(grepl("ai recommendation remains advisory", tolower(paste(capture.output(write.table(governance, row.names = FALSE, quote = FALSE)), collapse = " ")), fixed = TRUE), "AI authority boundary")
stop_if(grepl("measurement and observability do not create enforcement", tolower(paste(capture.output(write.table(governance, row.names = FALSE, quote = FALSE)), collapse = " ")), fixed = TRUE), "sensing authority boundary")
bio <- tolower(text_rel("reports/phase15b_biosecurity_futures.md")); for (term in c("diagnostic speed", "attribution uncertainty", "laboratory/diagnostic capacity", "supply-chain resilience", "public communication", "dual-use governance", "no pathogen design", "wet-lab procedure")) stop_if(grepl(term, bio, fixed = TRUE), paste("biosecurity", term))
for (name in c("technology_convergence_futures", "technology_cross_system_effects")) { png <- path(paste0("outputs/figures/", name, ".png")); svg <- path(paste0("outputs/figures/", name, ".svg")); stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("figure", name)); stop_if(grepl("<svg", tolower(paste(readLines(svg, warn = FALSE, encoding = "UTF-8"), collapse = " ")), fixed = TRUE), paste("SVG", name)) }

live_r <- text_rel("src/R/systems/validate_phase15b_technology.R"); stop_if(grepl("unsupported_percentage <- grepl", live_r, fixed = TRUE) && grepl("if (unsupported_percentage) stop(", live_r, fixed = TRUE), "percentage guard source")
final_review <- tolower(text_rel(file.path("reports", review_name))); for (term in c("deleg_53b320bb", '"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"scenario_boundary_errors": []', '"technology_maturity_errors": []', '"regional_relevance_errors": []', '"governance_boundary_errors": []', '"biosecurity_boundary_errors": []', '"system_integration_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(term, final_review, fixed = TRUE), paste("final review", term))
for (pair in list(c(initial_name, "deleg_e21c8764"), c(second_name, "deleg_78928bd2"))) stop_if(grepl(pair[[2]], text_rel(file.path("reports", pair[[1]])), fixed = TRUE), paste("review lineage", pair[[2]]))

freeze_files <- list.files(reports, pattern = "freeze_manifest\\.json$", full.names = TRUE); freeze_files <- freeze_files[basename(freeze_files) != final_name]
prior_entries <- 0L; protected <- character()
for (mf in sort(freeze_files)) { x <- manifest_entries(mf); prior_entries <- prior_entries + nrow(x); protected <- c(protected, x$rel); for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", mf, x$rel[[i]])) }
stop_if(prior_entries == expected_prior_entries && length(unique(protected)) == expected_prior_unique, "prior freeze inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE); untracked <- system2("git", c("-C", root, "ls-files", "--others", "--exclude-standard"), stdout = TRUE, stderr = TRUE); changed <- gsub("\\\\", "/", c(changed, untracked)); changed <- changed[nzchar(changed)]
stop_if(!length(intersect(changed, unique(protected))), "prior protected artifact changed")
review_paths <- file.path("reports", c(review_name, initial_name, second_name))
stop_if(!length(intersect(changed, unique(c(working_artifacts, review_paths)))), "Phase 15B package changed")
allowed <- unique(c(status_surfaces, file.path("reports", final_name), freeze_validators)); stop_if(all(changed %in% allowed), paste("unexpected changed path", paste(setdiff(changed, allowed), collapse = ",")))
stop_if(!length(grep("phase16", changed, ignore.case = TRUE, value = TRUE)), "Phase 16 implementation")
status <- tolower(paste(vapply(status_surfaces, text_rel, character(1)), collapse = " ")); for (term in c("phase 15b", "accepted / frozen", final_name, "phase 16", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b manifest status wording mismatch", "phase 3a missing manifest status", "phase 2a superseded legacy worktree", "no release or tag")) stop_if(grepl(tolower(term), status, fixed = TRUE), paste("status", term))

cat(sprintf("PHASE15B_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, prior entries=%d, prior unique=%d, assumptions=48, family states=48, convergence=60, systems=78, dependencies=72, governance=48, uncertainty=60, comparisons=6, Phase 15A=30, Phase 14A/14B=24/23, review=deleg_53b320bb passed:true, percentage guard=direct fail-on-match, Phase 16 absent\n", nrow(final_x), nrow(working), prior_entries, length(unique(protected))))
