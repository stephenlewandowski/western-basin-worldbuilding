#!/usr/bin/env Rscript
# Independent base-R final-freeze validator for the accepted Phase 16B package.
# It does not source or invoke the Python validator.

args <- commandArgs(trailingOnly = TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash = "/", mustWork = TRUE)
reports <- file.path(root, "reports")
integration <- file.path(root, "data", "processed", "integration")
figures <- file.path(root, "outputs", "figures")

final_name <- "phase16b_compound_stress_tests_freeze_manifest.json"
working_name <- "phase16b_manifest.json"
artifact_check_name <- "phase16b_artifact_check.json"
r_result_name <- "phase16b_r_validation_result.json"
review_name <- "phase16b_independent_review.md"
failed_names <- c(
  "phase16b_independent_review_initial.md",
  "phase16b_independent_review_second_failed.md",
  "phase16b_independent_review_third_failed.md",
  "phase16b_independent_review_fourth_failed.md",
  "phase16b_independent_review_fifth_failed.md"
)
freeze_validators <- c("src/python/systems/validate_phase16b_freeze.py", "src/R/systems/validate_phase16b_freeze.R")
source_commit <- "d19f1cd8bca54b0f0ee56343818e6978ca55db47"
working_source_commit <- "9308127065112d0c01c294e954ae87f44e39af3f"
expected_prior_entries <- 623L
expected_prior_unique <- 614L
expected_system_ids <- c(
  "SYS-BIOGEOCHEMISTRY", "SYS-CLIMATE", "SYS-DATA", "SYS-ECOLOGY", "SYS-ENERGY",
  "SYS-EXPOSURE", "SYS-FREIGHT", "SYS-GOVERNANCE", "SYS-INFECTIOUS-DISEASE",
  "SYS-MATERIALS", "SYS-POPULATION", "SYS-VECTOR-ECOLOGY", "SYS-WATER"
)
working_artifacts <- c(
  "data/processed/integration/phase16b_stress_test_definitions.csv",
  "data/processed/integration/phase16b_chain_stages.csv",
  "data/processed/integration/phase16b_chain_terminations.csv",
  "data/processed/integration/phase16b_system_states.csv",
  "data/processed/integration/phase16b_response_adaptation_states.csv",
  "data/processed/integration/phase16b_regime_effects.csv",
  "data/processed/integration/phase16b_uncertainties.csv",
  "data/processed/integration/phase16b_cross_test_comparison.csv",
  "data/processed/integration/phase16b_narrative_hooks.csv",
  "outputs/figures/phase16b_compound_stress_propagation.png",
  "outputs/figures/phase16b_compound_stress_propagation.svg",
  "outputs/figures/phase16b_technology_regime_effects.png",
  "outputs/figures/phase16b_technology_regime_effects.svg",
  "reports/phase16b_compound_cross_system_stress_tests.md",
  "reports/phase16b_qa.md",
  "reports/phase16b_provenance_lineage.md",
  "reports/phase16b_scenario_comparison.md",
  "reports/phase16b_narrative_hooks.md",
  file.path("reports", review_name),
  "src/python/systems/build_phase16b_stress_tests.py",
  "src/python/systems/validate_phase16b_stress_tests.py",
  "src/R/systems/validate_phase16b_stress_tests.R"
)
final_artifacts <- sort(c(working_artifacts, file.path("reports", working_name), file.path("reports", artifact_check_name), file.path("reports", r_result_name), file.path("reports", failed_names), freeze_validators))
status_surfaces <- c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
path_rel <- function(relative) file.path(root, gsub("/", .Platform$file.sep, relative, fixed = TRUE))
text_file <- function(relative) paste(readLines(path_rel(relative), warn = FALSE, encoding = "UTF-8"), collapse = " ")
read_csv_rel <- function(relative) {
  file <- path_rel(relative)
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing table", relative))
  read.csv(file, stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
}
raw_bytes <- function(file) readBin(file, "raw", n = as.numeric(file.info(file)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix); on.exit(unlink(tmp), add = TRUE); writeBin(raw, tmp)
  if (exists("sha256sum", where = asNamespace("tools"), inherits = FALSE)) {
    return(tolower(unname(tools::sha256sum(tmp)[[1]])))
  }
  command <- Sys.which("sha256sum")
  if (nzchar(command)) {
    output <- system2(command, tmp, stdout = TRUE, stderr = TRUE)
    hits <- regmatches(paste(output, collapse = " "), gregexpr("[0-9a-fA-F]{64}", paste(output, collapse = " "), perl = TRUE))[[1]]
    stop_if(length(hits) > 0L, "sha256sum failed")
    return(tolower(hits[[1]]))
  }
  command <- Sys.which("certutil")
  stop_if(nzchar(command), "Neither sha256sum nor certutil is available")
  output <- system2(command, c("-hashfile", normalizePath(tmp, winslash = "\\", mustWork = TRUE), "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) > 0L, "certutil failed")
  hits[[1]]
}
sha256_file <- function(file) sha256_raw(raw_bytes(file), tools::file_ext(file))
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
portable_match <- function(file, expected, recorded = NA_real_) {
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing artifact", file))
  raw <- raw_bytes(file)
  variants <- list(list(hash = sha256_raw(raw, tools::file_ext(file)), bytes = length(raw)))
  if (tolower(tools::file_ext(file)) %in% tolower(text_ext)) {
    normalized_raw <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))
    crlf_raw <- charToRaw(gsub("\n", "\r\n", rawToChar(normalized_raw), fixed = TRUE))
    variants <- c(variants, list(list(hash = sha256_raw(normalized_raw, tools::file_ext(file)), bytes = length(normalized_raw)), list(hash = sha256_raw(crlf_raw, tools::file_ext(file)), bytes = length(crlf_raw))))
  }
  any(vapply(variants, function(x) tolower(expected) == x$hash && (is.na(recorded) || as.numeric(recorded) == x$bytes), logical(1)))
}
manifest_entries <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  start_hits <- which(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  if (!length(start_hits)) start_hits <- which(grepl('"files"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  stop_if(length(start_hits) > 0L, paste("missing artifacts collection", file))
  start <- start_hits[[1]]
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  if (start + 1L <= length(lines)) for (line in lines[(start + 1L):length(lines)]) {
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
  append_current()
  data.frame(relative = rel, sha256 = hashes, bytes = bytes, stringsAsFactors = FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels = character()) {
  file <- file.path(reports, name); stop_if(file.exists(file), paste("missing manifest", name))
  x <- manifest_entries(file)
  stop_if(nrow(x) == expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(setequal(as.character(x$relative), as.character(expected_rels)) && nrow(x) == length(expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(path_rel(x$relative[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$relative[[i]]))
  x
}

final_text <- text_file(file.path("reports", final_name))
for (term in c(
  '"accepted_phase": "16B"', '"baseline": "Compound Cross-System Stress Tests"', '"status": "ACCEPTED / FROZEN"',
  '"accepted_by": "Sol explicit acceptance decision supplied for this run"', paste0('"source_commit": "', source_commit, '"'),
  '"principal_tests": 4', '"reserve_tests": 2', '"chain_stages": 13', '"branches": 14', '"system_state_observations": 26',
  '"response_adaptation_states": 13', '"regime_effect_rows": 24', '"uncertainty_rows": 4', '"comparison_rows": 4', '"narrative_hooks": 4',
  '"terminated_branches": 14', '"prior_freeze_entries": 623', '"prior_freeze_unique_paths": 614', '"qualitative_only": true',
  '"no_composite_scores": true', '"no_new_phase16a_propagation_rules": true', '"phase16a_status": "ACCEPTED / FROZEN"',
  '"phase15_status": "COMPLETE / ACCEPTED / FROZEN"', '"phase14_status": "COMPLETE / ACCEPTED / FROZEN"',
  '"phase17_status": "NOT IMPLEMENTED"', '"great_black_swamp": "C — HOLD / noncanonical"',
  '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"', '"release_created": false', '"tag_created": false'
)) stop_if(grepl(term, final_text, fixed = TRUE), paste("final manifest", term))
stop_if(grepl('"final_manifest_path": "reports/phase16b_compound_stress_tests_freeze_manifest.json"', final_text, fixed = TRUE), "final manifest path")
final_x <- verify_manifest(final_name, length(final_artifacts), final_artifacts)
stop_if(!any(final_x$relative == final_name), "final manifest self-inclusion")
working_x <- verify_manifest(working_name, length(working_artifacts), working_artifacts)
working_text <- text_file(file.path("reports", working_name))
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"16B"', working_text, perl = TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', working_text, perl = TRUE) && grepl(paste0('"source_commit"[[:space:]]*:[[:space:]]*"', working_source_commit, '"'), working_text, perl = TRUE), "working manifest identity")

check_text <- text_file(file.path("reports", artifact_check_name)); r_text <- text_file(file.path("reports", r_result_name)); r_compact <- gsub("[[:space:]]+", "", r_text)
for (term in c('"phase": "16B"', '"passed": true', '"errors": []', '"principal_tests": 4', '"reserve_tests": 2', '"chain_stages": 13', '"branches": 14', '"system_state_observations": 26', '"response_adaptation_states": 13', '"regime_effect_rows": 24', '"uncertainty_rows": 4', '"comparison_rows": 4', '"narrative_hooks": 4', '"terminated_branches": 14', '"prior_freeze_entries": 623', '"prior_freeze_unique_paths": 614')) stop_if(grepl(term, check_text, fixed = TRUE), paste("artifact check", term))
for (term in c('"phase":"16B"', '"passed":true', '"errors":[]', '"principal_tests":4', '"reserve_tests":2', '"chain_stages":13', '"branches":14', '"system_state_observations":26', '"response_adaptation_states":13', '"regime_effect_rows":24', '"uncertainty_rows":4', '"comparison_rows":4', '"narrative_hooks":4', '"terminated_branches":14', '"prior_freeze_entries":623', '"prior_freeze_unique_paths":614')) stop_if(grepl(term, r_compact, fixed = TRUE), paste("R result", term))

phase_manifest_specs <- list(
  c("phase16a_integrated_basin_dynamics_freeze_manifest.json", "16A", 30L),
  c("phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json", "14A", 24L),
  c("phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json", "14B", 23L),
  c("phase15a_technology_strategic_systems_baseline_freeze_manifest.json", "15A", 30L),
  c("phase15b_technology_convergence_futures_freeze_manifest.json", "15B", 28L)
)
for (spec in phase_manifest_specs) {
  x <- verify_manifest(spec[[1]], as.integer(spec[[3]])); txt <- text_file(file.path("reports", spec[[1]]))
  stop_if(grepl(paste0('"accepted_phase": "', spec[[2]], '"'), txt, fixed = TRUE) && grepl('"status": "ACCEPTED / FROZEN"', txt, fixed = TRUE), paste("prior status", spec[[1]]))
}

system_lines <- readLines(file.path(root, "metadata", "atlas_systems.yml"), warn = FALSE, encoding = "UTF-8")
systems_start <- which(trimws(system_lines) == "systems:")[[1]]
identity_start <- which(trimws(system_lines) == "identity_sources:")[[1]]
registry_lines <- system_lines[(systems_start + 1L):(identity_start - 1L)]
id_lines <- registry_lines[grepl("^[[:space:]]*-[[:space:]]+system_id:", registry_lines, perl = TRUE)]
system_ids <- trimws(sub("^[[:space:]]*-[[:space:]]+system_id:[[:space:]]*", "", id_lines, perl = TRUE))
stop_if(length(system_ids) == 13L && !anyDuplicated(system_ids) && setequal(system_ids, expected_system_ids) && all(nzchar(system_ids)) && !any(tolower(system_ids) %in% c("null", "none", "~")), "authoritative Atlas registry")

csv_paths <- c(
  definitions = "data/processed/integration/phase16b_stress_test_definitions.csv",
  stages = "data/processed/integration/phase16b_chain_stages.csv",
  terminations = "data/processed/integration/phase16b_chain_terminations.csv",
  states = "data/processed/integration/phase16b_system_states.csv",
  responses = "data/processed/integration/phase16b_response_adaptation_states.csv",
  regimes = "data/processed/integration/phase16b_regime_effects.csv",
  uncertainties = "data/processed/integration/phase16b_uncertainties.csv",
  comparison = "data/processed/integration/phase16b_cross_test_comparison.csv",
  hooks = "data/processed/integration/phase16b_narrative_hooks.csv"
)
frames <- lapply(csv_paths, read_csv_rel)
stop_if(nrow(frames$definitions) == 6L && sum(frames$definitions$test_class == "PRINCIPAL") == 4L && sum(frames$definitions$test_class == "RESERVE") == 2L && all(frames$definitions$implementation_status[frames$definitions$test_class == "RESERVE"] == "RESERVE / UNIMPLEMENTED"), "principal/reserve package")
stop_if(nrow(frames$stages) == 13L && nrow(frames$terminations) == 14L && nrow(frames$states) == 26L && nrow(frames$responses) == 13L && nrow(frames$regimes) == 24L && nrow(frames$uncertainties) == 4L && nrow(frames$comparison) == 4L && nrow(frames$hooks) == 4L, "Phase 16B package counts")
stop_if(all(frames$stages$source_system_id %in% system_ids) && all(frames$stages$target_system_id %in% system_ids) && all(frames$states$system_id %in% system_ids) && all(frames$terminations$initial_system_id %in% system_ids), "Phase 16B registry membership")
stop_if(all(frames$terminations$termination_status == "TERMINATED — NO DEFENSIBLE CURRENT PATH") && all(frames$terminations$defensible_branch_termination == "true"), "termination boundary")
stop_if(all(frames$hooks$status == "NONCANONICAL / FUTURE ATLAS HOOK"), "Atlas hook boundary")

phase_rules <- read_csv_rel("data/processed/integration/propagation_rules.csv"); phase_relationships <- read_csv_rel("data/processed/integration/propagation_relationships.csv")
for (i in seq_len(nrow(frames$stages))) {
  row <- frames$stages[i, ]; ri <- match(row$phase16a_rule_id, phase_rules$rule_id); qi <- match(row$phase16a_relationship_id, phase_relationships$relationship_id)
  stop_if(!is.na(ri) && !is.na(qi), paste("unresolved lineage", row$stage_id))
  stop_if(row$source_system_id == phase_rules$source_system_id[ri] && row$target_system_id == phase_rules$target_system_id[ri] && row$source_system_id == phase_relationships$source_system_id[qi] && row$target_system_id == phase_relationships$target_system_id[qi], paste("endpoint lineage", row$stage_id))
  stop_if(row$evidence_class == phase_rules$evidence_class[ri] && row$lineage_evidence_class == phase_relationships$evidence_class[qi], paste("evidence inheritance", row$stage_id))
  if (row$stage == "1") stop_if(row$chain_relation_type == "parallel_initial_branch" && !nzchar(row$stage_parent_id) && row$source_system_id == row$stressor_initial_system_id, paste("initial chain", row$stage_id))
  if (row$stage != "1") { pi <- match(row$stage_parent_id, frames$stages$stage_id); stop_if(!is.na(pi) && row$chain_relation_type == "sequential" && frames$stages$target_system_id[pi] == row$source_system_id && as.integer(row$stage) == as.integer(frames$stages$stage[pi]) + 1L && row$phase16a_chain_parent_rule_id == frames$stages$phase16a_rule_id[pi], paste("sequential chain", row$stage_id)) }
}

all_review_text <- tolower(text_file(file.path("reports", review_name)))
for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"chain_errors": []', '"propagation_errors": []', '"evidence_classification_errors": []', '"scenario_boundary_errors": []', '"technology_modifier_errors": []', '"biosecurity_boundary_errors": []', '"atlas_bridge_errors": []', '"canon_boundary_errors": []', '"suggestions": []')) stop_if(grepl(term, all_review_text, fixed = TRUE), paste("final review", term))
for (i in seq_along(failed_names)) {
  txt <- tolower(text_file(file.path("reports", failed_names[[i]]))); stop_if(grepl('"passed":false', gsub("[[:space:]]+", "", txt), fixed = TRUE), paste("failed lineage", failed_names[[i]]))
}
stop_if(grepl("figure readability failure", tolower(text_file(file.path("reports", failed_names[[1]]))), fixed = TRUE) && grepl("review-array parsing", tolower(text_file(file.path("reports", failed_names[[2]]))), fixed = TRUE) && grepl("rendered card-layout defect", tolower(text_file(file.path("reports", failed_names[[3]]))), fixed = TRUE) && grepl("initial_system_id", tolower(text_file(file.path("reports", failed_names[[4]]))), fixed = TRUE) && grepl("system_id: null", tolower(text_file(file.path("reports", failed_names[[5]]))), fixed = TRUE), "failed review finding lineage")

png_expect <- list(c("phase16b_compound_stress_propagation.png", 2268L, 1422L), c("phase16b_technology_regime_effects.png", 4356L, 3276L))
for (spec in png_expect) { raw <- raw_bytes(file.path(figures, spec[[1]])); stop_if(length(raw) >= 24L && identical(as.integer(raw[1:8]), as.integer(charToRaw("\x89PNG\r\n\x1a\n"))), paste("PNG signature", spec[[1]])); width <- sum(as.integer(raw[17:20]) * c(256^3, 256^2, 256, 1)); height <- sum(as.integer(raw[21:24]) * c(256^3, 256^2, 256, 1)); stop_if(width == as.integer(spec[[2]]) && height == as.integer(spec[[3]]), paste("PNG dimensions", spec[[1]])) }
for (pair in list(c("phase16b_compound_stress_propagation.svg", "Compound Stress Propagation"), c("phase16b_technology_regime_effects.svg", "Technology-Regime Effects on Propagation"))) stop_if(grepl(pair[[2]], text_file(file.path("outputs", "figures", pair[[1]])), fixed = TRUE), paste("SVG", pair[[1]]))
qa_text <- text_file(file.path("reports", "phase16b_qa.md")); for (term in c("data_top > header_bottom + minimum_gap", "all 0 card-rectangle overlaps detected", "B text enters C=False", "C text outside its figure/card=False")) stop_if(grepl(term, qa_text, fixed = TRUE), paste("figure QA", term))

prior_files <- list.files(reports, pattern = "freeze_manifest[.]json$", full.names = TRUE); prior_files <- prior_files[basename(prior_files) != final_name]; prior_entries <- 0L; prior_paths <- character()
for (mf in sort(prior_files)) { x <- manifest_entries(mf); stop_if(nrow(x) > 0L, paste("empty prior manifest", basename(mf))); prior_entries <- prior_entries + nrow(x); prior_paths <- c(prior_paths, x$relative); for (i in seq_len(nrow(x))) stop_if(portable_match(path_rel(x$relative[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", x$relative[[i]])) }
stop_if(prior_entries == expected_prior_entries && length(unique(prior_paths)) == expected_prior_unique, "prior freeze inventory")

changed <- c(system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE), system2("git", c("-C", root, "ls-files", "--others", "--exclude-standard"), stdout = TRUE, stderr = TRUE)); changed <- gsub("\\\\", "/", trimws(changed)); changed <- changed[nzchar(changed)]
allowed <- unique(c(status_surfaces, file.path("reports", final_name), freeze_validators)); stop_if(!length(setdiff(changed, allowed)), paste("unexpected changed path", paste(setdiff(changed, allowed), collapse = ","))); stop_if(!length(intersect(changed, unique(prior_paths))), "previously frozen artifact changed"); stop_if(!any(grepl("phase17", tolower(changed), fixed = TRUE)), "Phase 17 content changed")
status_text <- tolower(paste(vapply(status_surfaces, text_file, character(1)), collapse = " ")); for (term in c("phase 16b", "accepted / frozen", "phase 16 overall", "complete / accepted / frozen", "phase 17", "not implemented", "active phase", "none", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag", tolower(final_name))) stop_if(grepl(term, status_text, fixed = TRUE), paste("status", term))

cat(sprintf("PHASE16B_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, principal/reserve=4/2, stages/branches=13/14, system states/responses=26/13, regime/uncertainty/comparison/hooks=24/4/4/4, Phase 16A/14A/14B/15A/15B=30/24/23/30/28, prior entries=%d, prior unique=%d, review passed:true with five failed records preserved, registry=13, Phase 17 not implemented\n", nrow(final_x), nrow(working_x), prior_entries, length(unique(prior_paths))))