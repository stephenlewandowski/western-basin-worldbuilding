#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 16A.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) && !grepl("^--", args[[1]])) normalizePath(args[[1]], winslash = "/", mustWork = TRUE) else normalizePath(".", winslash = "/", mustWork = TRUE)
reports <- file.path(root, "reports")
integration <- file.path(root, "data", "processed", "integration")
scenarios <- file.path(root, "data", "processed", "scenarios")
metadata <- file.path(root, "metadata")
figures <- file.path(root, "outputs", "figures")

final_name <- "phase16a_integrated_basin_dynamics_freeze_manifest.json"
working_name <- "phase16a_manifest.json"
artifact_check_name <- "phase16a_artifact_check.json"
r_result_name <- "phase16a_r_validation_result.json"
review_name <- "phase16a_independent_review.md"
initial_name <- "phase16a_independent_review_initial.md"
second_name <- "phase16a_independent_review_second_failed.md"
third_name <- "phase16a_independent_review_third_failed.md"
phase14a_name <- "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
phase14b_name <- "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
phase15a_name <- "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
phase15b_name <- "phase15b_technology_convergence_futures_freeze_manifest.json"
source_commit <- "9daad68c44af9259f42837b2c90af8c8d98fb0f9"
working_source_commit <- "038669819731b2206f74a078f6b652ebafacb007"
expected_prior_entries <- 593L
expected_prior_unique <- 584L
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
working_artifacts <- c(
  "metadata/basin_dynamics_vocabulary.yml",
  "docs/phase_briefs/phase16_integrated_basin_dynamics.md",
  "docs/phase_briefs/phase16a_integrated_basin_dynamics_framework_propagation_rules.md",
  "docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md",
  "data/processed/integration/stressor_catalog.csv",
  "data/processed/integration/propagation_relationships.csv",
  "data/processed/integration/propagation_rules.csv",
  "data/processed/integration/adaptation_response_catalog.csv",
  "data/processed/integration/technology_modifier_catalog.csv",
  "data/processed/integration/feedback_coupling_inventory.csv",
  "data/processed/integration/system_stressor_matrix.csv",
  "data/processed/integration/phase16b_candidate_stress_tests.csv",
  "outputs/figures/western_basin_stress_propagation_architecture.png",
  "outputs/figures/western_basin_stress_propagation_architecture.svg",
  "reports/phase16a_integrated_basin_dynamics.md",
  "reports/phase16a_propagation_framework.md",
  "reports/phase16a_candidate_stress_tests.md",
  "reports/phase16a_qa.md",
  file.path("reports", initial_name),
  file.path("reports", second_name),
  "src/python/systems/build_phase16a_dynamics.py",
  "src/python/systems/validate_phase16a_dynamics.py",
  "src/R/systems/validate_phase16a_dynamics.R"
)
working_artifacts <- sort(working_artifacts)
freeze_validators <- c("src/python/systems/validate_phase16a_freeze.py", "src/R/systems/validate_phase16a_freeze.R")
final_artifacts <- sort(c(working_artifacts, file.path("reports", working_name), file.path("reports", artifact_check_name), file.path("reports", r_result_name), file.path("reports", review_name), file.path("reports", third_name), freeze_validators))
status_surfaces <- c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")
evidence_classes <- c("OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD")
relationship_cells <- c("DIRECT", "INDIRECT", "SCENARIO-CONDITIONED", "NO CURRENT DEFENSIBLE PATH", "NOT ASSESSED")
removed_rule_ids <- c("RULE-16A-003", "RULE-16A-004", "RULE-16A-013", "RULE-16A-032", "RULE-16A-035", "RULE-16A-038")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
path_rel <- function(relative) file.path(root, gsub("/", .Platform$file.sep, relative, fixed = TRUE))
read_csv_rel <- function(relative) {
  absolute <- grepl("^([A-Za-z]:[/\\\\]|/)", relative)
  file <- if (absolute) relative else path_rel(relative)
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing table", relative))
  read.csv(file, stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
}
text_rel <- function(relative) paste(readLines(path_rel(relative), warn = FALSE, encoding = "UTF-8"), collapse = " ")
json_text <- function(relative) text_rel(relative)
raw_bytes <- function(file) readBin(file, "raw", n = as.numeric(file.info(file)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix); on.exit(unlink(tmp), add = TRUE); writeBin(raw, tmp)
  command <- Sys.which("sha256sum")
  if (nzchar(command)) {
    output <- system2(command, tmp, stdout = TRUE, stderr = TRUE)
    text <- paste(output, collapse = " ")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl = TRUE))[[1]]
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
sha256_file <- function(file) {
  command <- Sys.which("sha256sum")
  if (nzchar(command)) {
    output <- system2(command, file, stdout = TRUE, stderr = TRUE)
    text <- paste(output, collapse = " ")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl = TRUE))[[1]]
    stop_if(length(hits) > 0L, "sha256sum failed")
    return(tolower(hits[[1]]))
  }
  sha256_raw(raw_bytes(file), tools::file_ext(file))
}
sha256_cache <- new.env(parent = emptyenv())
sha256_cached <- function(file, variant = "raw") {
  key <- paste(normalizePath(file, winslash = "/", mustWork = TRUE), variant, sep = "|")
  if (exists(key, envir = sha256_cache, inherits = FALSE)) return(get(key, envir = sha256_cache, inherits = FALSE))
  raw <- raw_bytes(file)
  if (variant == "raw") payload <- raw
  else if (variant == "normalized") payload <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))
  else payload <- charToRaw(gsub("\n", "\r\n", rawToChar(charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))), fixed = TRUE))
  value <- if (variant == "raw") sha256_file(file) else sha256_raw(payload, tools::file_ext(file))
  assign(key, list(hash = value, bytes = length(payload)), envir = sha256_cache)
  get(key, envir = sha256_cache, inherits = FALSE)
}
portable_match <- function(file, expected, recorded = NA_real_) {
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing artifact", file))
  raw <- sha256_cached(file, "raw")
  if (tolower(expected) == raw$hash && (is.na(recorded) || as.numeric(recorded) == raw$bytes)) return(TRUE)
  if (tolower(tools::file_ext(file)) %in% tolower(text_ext)) {
    normalized <- sha256_cached(file, "normalized")
    if (tolower(expected) == normalized$hash && (is.na(recorded) || as.numeric(recorded) == normalized$bytes)) return(TRUE)
    crlf <- sha256_cached(file, "crlf")
    if (tolower(expected) == crlf$hash && (is.na(recorded) || as.numeric(recorded) == crlf$bytes)) return(TRUE)
  }
  FALSE
}
manifest_entries <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  hits <- which(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  if (!length(hits)) hits <- which(grepl('"files"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  stop_if(length(hits) > 0L, paste("missing artifacts collection", file))
  start <- hits[[1]]
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) {
      rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes)
    }
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
  data.frame(rel = rel, sha256 = hashes, bytes = bytes, stringsAsFactors = FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels = character()) {
  file <- file.path(reports, name); stop_if(file.exists(file), paste("missing manifest", name))
  entries <- manifest_entries(file)
  stop_if(nrow(entries) == expected_n, paste(name, "artifact count", nrow(entries)))
  if (length(expected_rels)) stop_if(setequal(as.character(entries$rel), as.character(expected_rels)), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(entries))) stop_if(portable_match(path_rel(entries$rel[[i]]), entries$sha256[[i]], entries$bytes[[i]]), paste(name, entries$rel[[i]]))
  entries
}
compatible_output <- function(source, output) {
  allowed <- list(
    OBSERVED_DOCUMENTED = c("OBSERVED_DOCUMENTED", "INFERRED", "CONTEXT_REUSED"),
    INFERRED = c("INFERRED", "CONTEXT_REUSED"),
    CONTEXT_REUSED = c("INFERRED", "CONTEXT_REUSED"),
    SCENARIO_STATE = c("SCENARIO_STATE", "SCENARIO_ASSUMPTION"),
    SCENARIO_ASSUMPTION = c("SCENARIO_STATE", "SCENARIO_ASSUMPTION")
  )
  source %in% names(allowed) && output %in% allowed[[source]]
}
endpoint_compatible <- function(actual_source, actual_target, expected_source, expected_target, explicitly_undirected = FALSE) {
  ordered <- isTRUE(actual_source == expected_source && actual_target == expected_target)
  reversed <- isTRUE(explicitly_undirected) && isTRUE(actual_source == expected_target && actual_target == expected_source)
  ordered || reversed
}
endpoint_error <- function(id, actual_source, actual_target, expected_source, expected_target, undirected = FALSE) {
  stop_if(endpoint_compatible(actual_source, actual_target, expected_source, expected_target, undirected), paste(id, "ordered endpoint compatibility"))
}
lineage_evidence <- function(lineage, direct, interfaces, dependencies, states, dep_states, governance) {
  if (!grepl("#", lineage, fixed = TRUE)) return(NA_character_)
  key <- sub(".*#", "", lineage)
  if (grepl("^AR-", key)) { i <- match(key, direct$atlas_relationship_id); return(ifelse(is.na(i), NA_character_, direct$evidence_class[[i]])) }
  if (grepl("^TSI-", key)) { i <- match(key, interfaces$interface_id); return(ifelse(is.na(i), NA_character_, interfaces$evidence_class[[i]])) }
  if (grepl("^TDEP-", key)) { i <- match(key, dependencies$dependency_id); return(ifelse(is.na(i), NA_character_, dependencies$evidence_class[[i]])) }
  if (grepl("^TSS-", key)) return(ifelse(key %in% states$state_id, "SCENARIO_STATE", NA_character_))
  if (grepl("^TDS-", key)) return(ifelse(key %in% dep_states$dependency_state_id, "SCENARIO_STATE", NA_character_))
  if (grepl("^TGS-", key)) return(ifelse(key %in% governance$governance_state_id, "SCENARIO_STATE", NA_character_))
  NA_character_
}
extract_refs <- function(text, pattern) {
  m <- gregexpr(pattern, text, perl = TRUE)[[1]]
  if (m[[1]] == -1L) character() else regmatches(text, list(m))[[1]]
}
technology_lineage_errors <- function(row, nodes, interfaces, dependencies, states, dep_states, governance) {
  errors <- character(); modifier <- row[["technology_modifier_id"]]; family <- row[["technology_family_or_regime"]]; technology_id <- row[["phase15_technology_or_regime_id"]]; lineage <- row[["source_lineage"]]
  if (grepl("^REGIME-", technology_id)) {
    if (family != technology_id) errors <- c(errors, paste(modifier, "regime family/id mismatch"))
    prefix <- substr(technology_id, 8L, 8L); refs <- extract_refs(lineage, "(?:TSS|TDS|TGS)-[A-Z0-9-]+")
    if (!any(grepl(paste0("-", prefix), refs, fixed = TRUE))) errors <- c(errors, paste(modifier, "regime lineage does not match scenario"))
    return(errors)
  }
  ni <- match(technology_id, nodes$technology_id)
  if (is.na(ni)) return(c(errors, paste(modifier, "missing Phase 15A technology node")))
  if (family != nodes$technology_family[[ni]]) errors <- c(errors, paste(modifier, "declared family differs from Phase 15A node family"))
  refs <- extract_refs(lineage, "(?:TSI|TDEP|TECH)-[A-Z0-9-]+"); matched <- FALSE
  for (ref in refs) {
    if (grepl("^TSI-", ref)) { i <- match(ref, interfaces$interface_id); if (is.na(i) || interfaces$technology_id[[i]] != technology_id) errors <- c(errors, paste(modifier, "Phase 15A interface lineage mismatch")) else matched <- TRUE }
    if (grepl("^TDEP-", ref)) { i <- match(ref, dependencies$dependency_id); if (is.na(i) || dependencies$technology_id[[i]] != technology_id) errors <- c(errors, paste(modifier, "Phase 15A dependency lineage mismatch")) else matched <- TRUE }
    if (grepl("^TECH-", ref)) { if (ref != technology_id) errors <- c(errors, paste(modifier, "Phase 15A technology ID lineage mismatch")) else matched <- TRUE }
  }
  if (!matched) errors <- c(errors, paste(modifier, "no matching Phase 15A identity lineage"))
  refs_b <- extract_refs(lineage, "(?:TSS|TDS|TGS)-[A-Z0-9-]+")
  if (!length(refs_b)) errors <- c(errors, paste(modifier, "no Phase 15B lineage"))
  for (ref in refs_b) {
    if (grepl("^TSS-", ref)) { i <- match(ref, states$state_id); fams <- ifelse(is.na(i), "", states$technology_family[[i]]) }
    else if (grepl("^TDS-", ref)) { i <- match(ref, dep_states$dependency_state_id); fams <- ifelse(is.na(i), "", dep_states$technology_family[[i]]) }
    else { i <- match(ref, governance$governance_state_id); fams <- ifelse(is.na(i), "", governance$technology_family[[i]]) }
    if (is.na(i)) errors <- c(errors, paste(modifier, "missing Phase 15B lineage", ref))
    else if (!(family %in% strsplit(fams, ";", fixed = TRUE)[[1]])) errors <- c(errors, paste(modifier, "Phase 15B family mismatch", ref))
  }
  errors
}

final_txt <- json_text(file.path("reports", final_name))
for (term in c(
  '"accepted_phase": "16A"', '"baseline": "Integrated Basin Dynamics Framework & Propagation Rules"', '"status": "ACCEPTED / FROZEN"',
  '"accepted_by": "Sol explicit acceptance decision supplied for this run"', '"accepted_date": "2026-09-13"', paste0('"source_commit": "', source_commit, '"'),
  '"stressors": 24', '"relationships": 36', '"rules": 32', '"responses": 13', '"technology_modifiers": 11', '"feedback": 10', '"matrix_cells": 312', '"candidates": 6',
  '"phase14a_protected_artifacts": 24', '"phase14b_protected_artifacts": 23', '"phase15a_protected_artifacts": 30', '"phase15b_protected_artifacts": 28',
  '"prior_freeze_entries": 593', '"prior_freeze_unique_paths": 584', '"qualitative_only": true', '"no_composite_scores": true', '"no_phase16b_execution": true',
  '"phase16b_status": "APPROVED SCOPE / NOT IMPLEMENTED"', '"phase17_status": "NOT IMPLEMENTED"', '"great_black_swamp": "C — HOLD / noncanonical"',
  '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"', '"Phase 6B manifest status wording mismatch"', '"Phase 3A missing manifest status"',
  '"Phase 2A superseded legacy worktree"', '"release_created": false', '"tag_created": false'
)) stop_if(grepl(term, final_txt, fixed = TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(final_artifacts), final_artifacts)
working <- verify_manifest(working_name, length(working_artifacts), working_artifacts)
working_txt <- json_text(file.path("reports", working_name)); stop_if(grepl('"phase": "16A"', working_txt, fixed = TRUE) && grepl('"status": "implemented_validated_pending_sol_acceptance"', working_txt, fixed = TRUE) && grepl(paste0('"source_commit": "', working_source_commit, '"'), working_txt, fixed = TRUE), "working manifest identity")
check_txt <- tolower(json_text(file.path("reports", artifact_check_name))); for (term in c('"phase": "16a"', '"passed": true', '"errors": []', '"prior_freeze_entries": 593', '"prior_freeze_unique_paths": 584', '"rule_chain_continuity"', '"response_evidence_inheritance"', '"technology_modifier_lineage_identity"', '"matrix_scenario_precedence"')) stop_if(grepl(term, check_txt, fixed = TRUE), paste("artifact check", term))
r_result_txt <- tolower(json_text(file.path("reports", r_result_name))); for (term in c('"phase": "16a"', '"passed": true', '"prior_freeze_entries": 593', '"prior_freeze_unique_paths": 584')) stop_if(grepl(term, r_result_txt, fixed = TRUE), paste("R result", term))

phase14a_txt <- json_text(file.path("reports", phase14a_name)); phase14b_txt <- json_text(file.path("reports", phase14b_name)); phase15a_txt <- json_text(file.path("reports", phase15a_name)); phase15b_txt <- json_text(file.path("reports", phase15b_name))
for (pair in list(c(phase14a_name, '"accepted_phase": "14A"'), c(phase14b_name, '"accepted_phase": "14B"'), c(phase15a_name, '"accepted_phase": "15A"'), c(phase15b_name, '"accepted_phase": "15B"'))) stop_if(grepl(pair[[2]], json_text(file.path("reports", pair[[1]])), fixed = TRUE) && grepl('"status": "ACCEPTED / FROZEN"', json_text(file.path("reports", pair[[1]])), fixed = TRUE), paste("manifest status", pair[[1]]))
stop_if(grepl('"phase14_overall_status": "COMPLETE / ACCEPTED / FROZEN"', phase14b_txt, fixed = TRUE), "Phase 14 overall")
stop_if(grepl('"phase15_overall_status": "COMPLETE / ACCEPTED / FROZEN"', phase15b_txt, fixed = TRUE), "Phase 15 overall")
phase14a_x <- verify_manifest(phase14a_name, 24L); phase14b_x <- verify_manifest(phase14b_name, 23L); phase15a_x <- verify_manifest(phase15a_name, 30L); phase15b_x <- verify_manifest(phase15b_name, 28L)

system_lines <- readLines(file.path(metadata, "atlas_systems.yml"), warn = FALSE, encoding = "UTF-8")
system_ids <- unique(sub(".*system_id:[[:space:]]*([^[:space:]]+).*", "\\1", system_lines[grepl("^[[:space:]]*- system_id:", system_lines)]))
stop_if(length(system_ids) == 13L, "Phase 14 ontology count")
architecture_lines <- system_lines[grepl("^[[:space:]]{4}- \\[SYS-", system_lines, perl = TRUE)]
stop_if(length(architecture_lines) > 0L, "Phase 14 architecture interfaces")
architecture_rows <- do.call(rbind, lapply(architecture_lines, function(line) {
  inside <- sub("^[[:space:]]{4}- \\[", "", line, perl = TRUE); inside <- sub("\\].*$", "", inside, perl = TRUE); fields <- trimws(strsplit(inside, ",", fixed = TRUE)[[1]])
  stop_if(length(fields) == 4L, paste("Phase 14 architecture interface schema", line))
  data.frame(source = fields[[1]], target = fields[[2]], interface_type = fields[[3]], status = fields[[4]], stringsAsFactors = FALSE)
}))
architecture_lineages <- paste0("metadata/atlas_systems.yml#architecture.interfaces:", architecture_rows$source, ">", architecture_rows$target)
relationship_lines <- readLines(file.path(metadata, "atlas_relationship_vocabulary.yml"), warn = FALSE, encoding = "UTF-8")
relationship_classes <- unique(sub(".*class_id:[[:space:]]*([^[:space:].].*)$", "\\1", relationship_lines[grepl("^[[:space:]]*  - class_id:", relationship_lines)]))
paths <- c(
  stressor_catalog.csv = file.path(integration, "stressor_catalog.csv"), propagation_relationships.csv = file.path(integration, "propagation_relationships.csv"),
  propagation_rules.csv = file.path(integration, "propagation_rules.csv"), adaptation_response_catalog.csv = file.path(integration, "adaptation_response_catalog.csv"),
  technology_modifier_catalog.csv = file.path(integration, "technology_modifier_catalog.csv"), feedback_coupling_inventory.csv = file.path(integration, "feedback_coupling_inventory.csv"),
  system_stressor_matrix.csv = file.path(integration, "system_stressor_matrix.csv"), phase16b_candidate_stress_tests.csv = file.path(integration, "phase16b_candidate_stress_tests.csv")
)
frames <- lapply(paths, function(file) read_csv_rel(file))
schemas <- list(
  stressor_catalog.csv = c("stressor_id", "stressor_class", "label", "initial_system_id", "initial_effect", "evidence_class", "source_lineage", "baseline_or_scenario", "notes"),
  propagation_relationships.csv = c("relationship_id", "source_system_id", "target_system_id", "relationship_class", "propagation_mechanism", "evidence_class", "direct_or_inferred", "baseline_or_scenario", "relationship_basis", "source_artifact", "source_relationship_id", "source_id", "source_lineage", "limitation", "spatial_character", "temporal_character", "reversibility", "uncertainty", "suitable_for_stress_test_propagation", "notes"),
  propagation_rules.csv = c("rule_id", "stage", "stressor_id", "chain_parent_rule_id", "chain_relation_type", "source_system_id", "source_state_or_effect", "initial_or_prior_effect", "relationship_id", "relationship_class", "target_system_id", "propagation_mechanism", "evidence_class", "lineage_evidence_class", "application_fit", "direct_or_inferred", "baseline_or_scenario", "enabling_condition", "limiting_condition", "temporal_character", "spatial_character", "reversibility", "technology_modifier", "governance_modifier", "response_option", "second_order_effect", "uncertainty", "source_lineage", "notes"),
  adaptation_response_catalog.csv = c("response_id", "response_mechanism", "applies_to", "enabling_condition", "limiting_condition", "evidence_class", "source_lineage", "adaptation_capacity_boundary", "notes"),
  technology_modifier_catalog.csv = c("technology_modifier_id", "technology_family_or_regime", "phase15_technology_or_regime_id", "modifier_effect", "evidence_class", "optional_condition", "effects_allowed", "source_lineage", "notes"),
  feedback_coupling_inventory.csv = c("feedback_id", "coupling_pair", "feedback_class", "evidence_basis", "plausible_interaction", "boundary", "numeric_gain_or_stability_claim", "notes"),
  system_stressor_matrix.csv = c("stressor_id", "system_id", "pathway_cell", "basis", "is_severity_measure", "is_risk_or_vulnerability_score", "notes"),
  phase16b_candidate_stress_tests.csv = c("candidate_id", "label", "stressor_ids", "system_ids", "selection_basis", "phase16a_rule_inputs", "status", "boundary", "executed")
)
for (nm in names(schemas)) stop_if(setequal(names(frames[[nm]]), schemas[[nm]]), paste("schema", nm))
stressors <- frames[["stressor_catalog.csv"]]; relationships <- frames[["propagation_relationships.csv"]]; rules <- frames[["propagation_rules.csv"]]; responses <- frames[["adaptation_response_catalog.csv"]]; technology <- frames[["technology_modifier_catalog.csv"]]; feedback <- frames[["feedback_coupling_inventory.csv"]]; matrix <- frames[["system_stressor_matrix.csv"]]; candidates <- frames[["phase16b_candidate_stress_tests.csv"]]
stop_if(nrow(stressors) == 24L && !anyDuplicated(stressors$stressor_id) && all(stressors$initial_system_id %in% system_ids) && all(stressors$evidence_class %in% evidence_classes) && all(nzchar(stressors$source_lineage)), "stressor package")
stop_if(nrow(relationships) == 36L && !anyDuplicated(relationships$relationship_id) && all(relationships$source_system_id %in% system_ids) && all(relationships$target_system_id %in% system_ids) && all(relationships$relationship_class %in% relationship_classes) && all(relationships$evidence_class %in% evidence_classes) && all(nzchar(relationships$source_lineage)) && all(nzchar(relationships$source_artifact)), "relationship package")
expected_relationship_status <- c(OBSERVED_DOCUMENTED = "direct", INFERRED = "inferred", CONTEXT_REUSED = "inferred", SCENARIO_STATE = "scenario-conditioned")
stop_if(all(mapply(function(e, s) is.null(expected_relationship_status[[e]]) || expected_relationship_status[[e]] == s, relationships$evidence_class, relationships$direct_or_inferred)), "relationship evidence/status")
stop_if(!any(relationships$relationship_class == "co-location") && !any(relationships$relationship_basis == "co-location"), "co-location is not propagation")
stop_if(all(relationships$suitable_for_stress_test_propagation == "QUALITATIVE_ONLY"), "relationship use")

direct <- read_csv_rel("data/processed/integration/atlas_dependency_crosswalk.csv"); interfaces <- read_csv_rel("data/processed/integration/technology_system_interfaces.csv"); dependencies <- read_csv_rel("data/processed/integration/technology_dependencies.csv"); states <- read_csv_rel("data/processed/scenarios/technology_system_states.csv"); dep_states <- read_csv_rel("data/processed/scenarios/technology_dependency_states.csv"); governance <- read_csv_rel("data/processed/scenarios/technology_governance_states.csv"); nodes <- read_csv_rel("data/processed/analysis/technology_system_nodes.csv")
relationship_lineage_errors <- character()
for (i in seq_len(nrow(relationships))) {
  row <- relationships[i,]; lineage <- row$source_lineage
  if (grepl("#AR-", lineage, fixed = TRUE)) {
    key <- sub(".*#", "", lineage); j <- match(key, direct$atlas_relationship_id); if (is.na(j) || direct$source_system_id[[j]] != row$source_system_id || direct$target_system_id[[j]] != row$target_system_id || direct$normalized_relationship_class[[j]] != row$relationship_class) relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id)
  } else if (grepl("#TDS-", lineage, fixed = TRUE)) {
    key <- sub(".*#", "", lineage); j <- match(key, dep_states$dependency_state_id); if (is.na(j)) relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id) else { if (row$baseline_or_scenario != "scenario-conditioned" || row$evidence_class != "SCENARIO_STATE") relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id); undirected <- "directionality" %in% names(dep_states) && tolower(dep_states$directionality[[j]]) %in% c("undirected", "bidirectional"); if (!endpoint_compatible(row$source_system_id, row$target_system_id, dep_states$system_a[[j]], dep_states$system_b[[j]], undirected)) relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id) }
  } else if (startsWith(lineage, "metadata/atlas_systems.yml#architecture.interfaces:")) {
    j <- match(lineage, architecture_lineages); if (is.na(j)) relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id) else { undirected <- tolower(architecture_rows$interface_type[[j]]) %in% c("undirected", "bidirectional") || tolower(architecture_rows$status[[j]]) %in% c("undirected", "bidirectional"); if (!endpoint_compatible(row$source_system_id, row$target_system_id, architecture_rows$source[[j]], architecture_rows$target[[j]], undirected)) relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id) }
  } else relationship_lineage_errors <- c(relationship_lineage_errors, row$relationship_id)
}
stop_if(!length(relationship_lineage_errors), "relationship lineage endpoint compatibility")

stressor_by_id <- setNames(seq_len(nrow(stressors)), stressors$stressor_id); relationship_by_id <- setNames(seq_len(nrow(relationships)), relationships$relationship_id); rule_by_id <- setNames(seq_len(nrow(rules)), rules$rule_id)
stop_if(nrow(rules) == 32L && !anyDuplicated(rules$rule_id) && !any(rules$rule_id %in% removed_rule_ids) && all(rules$stressor_id %in% names(stressor_by_id)) && all(rules$relationship_id %in% names(relationship_by_id)) && all(rules$response_option %in% responses$response_id) && all(as.integer(rules$stage) %in% c(1L, 2L)) && all(rules$baseline_or_scenario %in% c("baseline", "scenario-conditioned")) && all(nzchar(rules$source_lineage)) && all(nzchar(rules$enabling_condition)) && all(nzchar(rules$limiting_condition)) && all(nzchar(rules$uncertainty)), "rule package")
rule_lineage_errors <- character(); rule_chain_errors <- character()
for (i in seq_len(nrow(rules))) {
  row <- rules[i,]; rel <- relationships[relationship_by_id[[row$relationship_id]],]; stress <- stressors[stressor_by_id[[row$stressor_id]],]
  if (any(c(row$source_system_id != rel$source_system_id, row$target_system_id != rel$target_system_id, row$relationship_class != rel$relationship_class, row$propagation_mechanism != rel$propagation_mechanism, row$source_lineage != rel$source_lineage))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "orientation/lineage"))
  if (row$lineage_evidence_class != rel$evidence_class || !compatible_output(rel$evidence_class, row$evidence_class)) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "evidence inheritance"))
  expected <- expected_relationship_status[[row$evidence_class]]; if (!is.null(expected) && row$direct_or_inferred != expected) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "direct/inferred"))
  if (row$evidence_class == "OBSERVED_DOCUMENTED" && (rel$evidence_class != "OBSERVED_DOCUMENTED" || row$application_fit != "EXACT_SOURCE_APPLICATION")) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "observed non-exact"))
  if (row$evidence_class == "INFERRED" && rel$evidence_class == "OBSERVED_DOCUMENTED" && (!startsWith(row$application_fit, "QUALIFIED_INFERENCE") || !grepl("inferred", paste(row$enabling_condition, row$limiting_condition)))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "inference limitation"))
  if (row$baseline_or_scenario == "scenario-conditioned" && (rel$evidence_class != "SCENARIO_STATE" || !(row$evidence_class %in% c("SCENARIO_STATE", "SCENARIO_ASSUMPTION")))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "scenario mismatch"))
  if (row$baseline_or_scenario == "baseline" && (rel$evidence_class == "SCENARIO_STATE" || row$evidence_class %in% c("SCENARIO_STATE", "SCENARIO_ASSUMPTION"))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "scenario baseline"))
  if (as.integer(row$stage) == 1L) {
    if (row$source_system_id != stress$initial_system_id || nzchar(row$chain_parent_rule_id) || row$chain_relation_type != "parallel_initial_branch") rule_chain_errors <- c(rule_chain_errors, row$rule_id)
  } else {
    pi <- match(row$chain_parent_rule_id, rules$rule_id); if (is.na(pi) || pi >= i || rules$stressor_id[[pi]] != row$stressor_id || as.integer(rules$stage[[pi]]) != as.integer(row$stage) - 1L || rules$target_system_id[[pi]] != row$source_system_id || row$chain_relation_type != "sequential") rule_chain_errors <- c(rule_chain_errors, row$rule_id)
  }
}
stop_if(!length(rule_lineage_errors), "rule source/target/evidence fit"); stop_if(!length(rule_chain_errors), "propagation-chain continuity")
stop_if(!any(c(relationships$relationship_class, rules$relationship_class) == "causation") && !any(c(relationships$propagation_mechanism, rules$propagation_mechanism) == "causation"), "causation class")

response_errors <- character()
for (i in seq_len(nrow(responses))) { source_evidence <- lineage_evidence(responses$source_lineage[[i]], direct, interfaces, dependencies, states, dep_states, governance); if (is.na(source_evidence) || !compatible_output(source_evidence, responses$evidence_class[[i]]) || (responses$evidence_class[[i]] == "OBSERVED_DOCUMENTED" && source_evidence != "OBSERVED_DOCUMENTED")) response_errors <- c(response_errors, responses$response_id[[i]]) }
stop_if(nrow(responses) == 13L && !anyDuplicated(responses$response_id) && !length(response_errors) && all(vapply(responses$adaptation_capacity_boundary, function(x) any(vapply(c("not", "option", "without guaranteeing", "indeterminate"), function(term) grepl(term, tolower(x), fixed = TRUE), logical(1))), logical(1))), "response evidence inheritance")
modifier_errors <- unlist(lapply(seq_len(nrow(technology)), function(i) technology_lineage_errors(technology[i, ], nodes, interfaces, dependencies, states, dep_states, governance)))
stop_if(nrow(technology) == 11L && !anyDuplicated(technology$technology_modifier_id) && all(technology$phase15_technology_or_regime_id %in% c(nodes$technology_id, "REGIME-A", "REGIME-B", "REGIME-C")) && all(technology$evidence_class %in% evidence_classes) && !length(modifier_errors) && all(grepl("not automatically protective", tolower(technology$notes), fixed = TRUE)), "technology lineage")
stop_if(nrow(feedback) == 10L && !anyDuplicated(feedback$feedback_id) && all(feedback$feedback_class %in% c("documented", "inferred", "scenario-conditioned", "not currently supported")) && all(feedback$numeric_gain_or_stability_claim == "false") && all(grepl("not|no ", tolower(feedback$boundary))), "feedback boundary")
stop_if(nrow(matrix) == 312L && !anyDuplicated(paste(matrix$stressor_id, matrix$system_id)) && all(matrix$stressor_id %in% stressors$stressor_id) && all(matrix$system_id %in% system_ids) && all(matrix$pathway_cell %in% relationship_cells) && all(matrix$is_severity_measure == "false") && all(matrix$is_risk_or_vulnerability_score == "false"), "matrix package")
matrix_precedence_errors <- character(); matrix_keys <- paste(matrix$stressor_id, matrix$system_id, sep = "\r"); scenario_targets <- paste(rules$stressor_id[rules$baseline_or_scenario == "scenario-conditioned"], rules$target_system_id[rules$baseline_or_scenario == "scenario-conditioned"], sep = "\r")
for (i in seq_len(nrow(stressors))) for (system_id in system_ids) { mi <- match(paste(stressors$stressor_id[[i]], system_id, sep = "\r"), matrix_keys); cell <- matrix$pathway_cell[[mi]]; if (stressors$baseline_or_scenario[[i]] != "BASELINE" && cell == "DIRECT") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id)); if (stressors$baseline_or_scenario[[i]] != "BASELINE" && system_id == stressors$initial_system_id[[i]] && cell != "SCENARIO-CONDITIONED") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id)); if (cell == "SCENARIO-CONDITIONED" && system_id != stressors$initial_system_id[[i]] && !(paste(stressors$stressor_id[[i]], system_id, sep = "\r") %in% scenario_targets)) matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id)); if (stressors$baseline_or_scenario[[i]] == "BASELINE" && system_id == stressors$initial_system_id[[i]] && cell != "DIRECT") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id)) }
stop_if(!length(matrix_precedence_errors), "matrix scenario precedence")
stop_if(nrow(candidates) == 6L && !anyDuplicated(candidates$candidate_id) && all(candidates$status == "APPROVED SCOPE / NOT IMPLEMENTED") && all(candidates$executed == "false") && all(vapply(strsplit(candidates$stressor_ids, ";", fixed = TRUE), function(x) all(x %in% stressors$stressor_id), logical(1))) && all(vapply(strsplit(candidates$system_ids, ";", fixed = TRUE), function(x) all(x %in% system_ids), logical(1))), "candidate boundary")
field_names <- unlist(lapply(frames, names), use.names = FALSE); forbidden_fields <- c("risk_score", "resilience_score", "vulnerability_score", "connectivity_score", "severity_score", "probability_estimate", "incidence_rate", "outbreak_probability", "health_outcome_forecast")
stop_if(!any(field_names %in% forbidden_fields), "forbidden numeric fields")
all_text <- tolower(paste(unlist(frames), collapse = " ")); stop_if(grepl("not risk", all_text, fixed = TRUE) && grepl("not automatically protective", all_text, fixed = TRUE), "score boundary")
stop_if(grepl("no pathogen engineering", all_text, fixed = TRUE) && grepl("no operational attack", all_text, fixed = TRUE), "biosecurity boundary")

svg <- file.path(figures, "western_basin_stress_propagation_architecture.svg"); png <- file.path(figures, "western_basin_stress_propagation_architecture.png")
stop_if(file.exists(svg) && file.info(svg)$size > 10000 && file.exists(png) && file.info(png)$size > 10000, "figure files")
svg_text <- tolower(paste(readLines(svg, warn = FALSE, encoding = "UTF-8"), collapse = " ")); for (term in tolower(c("Western Basin Stress Propagation Architecture", "STRESSOR", "SYSTEM EFFECT", "DEPENDENCY / INTERFACE", "PROPAGATION", "RESPONSE / ADAPTATION", "SECOND-ORDER EFFECT", "direct / documented", "inferred", "scenario-conditioned", "option ≠ capacity ≠ success"))) stop_if(grepl(term, svg_text, fixed = TRUE), paste("figure label", term))
png_header <- raw_bytes(png); stop_if(length(png_header) >= 24L && identical(as.integer(png_header[1:8]), as.integer(charToRaw("\x89PNG\r\n\x1a\n"))), "PNG signature")
png_width <- sum(as.integer(png_header[17:20]) * c(256^3, 256^2, 256, 1)); png_height <- sum(as.integer(png_header[21:24]) * c(256^3, 256^2, 256, 1)); stop_if(png_width == 2259 && png_height == 1214, "PNG dimensions")
builder_txt <- text_rel("src/python/systems/build_phase16a_dynamics.py"); python_txt <- text_rel("src/python/systems/validate_phase16a_dynamics.py"); live_r_txt <- text_rel("src/R/systems/validate_phase16a_dynamics.R")
stop_if(grepl("def assert_lineage_endpoint_compatibility", builder_txt, fixed = TRUE) && grepl("def endpoint_pair_matches", builder_txt, fixed = TRUE) && grepl("def endpoint_compatibility_error", python_txt, fixed = TRUE) && grepl("endpoint_compatible <- function", live_r_txt, fixed = TRUE) && grepl("endpoint_compatibility_error <- function", live_r_txt, fixed = TRUE), "endpoint guard source")

review_txt <- tolower(text_rel(file.path("reports", review_name))); for (term in c("deleg_9fa57f45", '"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"propagation_errors": []', '"causal_boundary_errors": []', '"feedback_errors": []', '"evidence_classification_errors": []', '"technology_modifier_errors": []', '"biosecurity_boundary_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(term, review_txt, fixed = TRUE), paste("final review", term))
for (pair in list(c(initial_name, "deleg_ec4d7c55"), c(third_name, "deleg_703e15ec"))) stop_if(grepl(pair[[2]], tolower(text_rel(file.path("reports", pair[[1]]))), fixed = TRUE) && grepl('"passed":false', gsub(" ", "", tolower(text_rel(file.path("reports", pair[[1]])))), fixed = TRUE), paste("review lineage", pair[[2]]))
second_review_text <- gsub(" ", "", tolower(text_rel(file.path("reports", second_name))))
stop_if(grepl('"passed":false', second_review_text, fixed = TRUE), "review lineage endpoint-compatibility failed review")

prior_files <- list.files(reports, pattern = "freeze_manifest[.]json$", full.names = TRUE); prior_files <- prior_files[basename(prior_files) != final_name]; prior_entries <- 0L; prior_paths <- character()
for (mf in sort(prior_files)) { x <- manifest_entries(mf); stop_if(nrow(x) > 0L, paste("empty prior manifest", basename(mf))); prior_entries <- prior_entries + nrow(x); prior_paths <- c(prior_paths, x$rel); for (i in seq_len(nrow(x))) stop_if(portable_match(path_rel(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", x$rel[[i]])) }
stop_if(prior_entries == expected_prior_entries && length(unique(prior_paths)) == expected_prior_unique, "prior freeze inventory")
changed <- c(system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE), system2("git", c("-C", root, "ls-files", "--others", "--exclude-standard"), stdout = TRUE, stderr = TRUE)); changed <- gsub("\\\\", "/", trimws(changed)); changed <- changed[nzchar(changed)]
stop_if(!length(intersect(changed, unique(prior_paths))), "prior protected artifact changed")
package_paths <- c(working_artifacts, file.path("reports", working_name), file.path("reports", artifact_check_name), file.path("reports", r_result_name), file.path("reports", review_name), file.path("reports", initial_name), file.path("reports", second_name), file.path("reports", third_name)); stop_if(!length(intersect(changed, package_paths)), "Phase 16A package changed")
allowed <- unique(c(status_surfaces, file.path("reports", final_name), freeze_validators)); stop_if(all(changed %in% allowed), paste("unexpected changed path", paste(setdiff(changed, allowed), collapse = ",")))
phase16b_changes <- changed[grepl("phase16b", tolower(changed), fixed = TRUE)]
stop_if(all(phase16b_changes %in% c("docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md", "data/processed/integration/phase16b_candidate_stress_tests.csv")), "Phase 16B execution")
stop_if(!any(grepl("phase17", tolower(changed), fixed = TRUE)), "Phase 17 present")
status_text <- tolower(paste(vapply(status_surfaces, text_rel, character(1)), collapse = " ")); for (term in c("phase 16a", "accepted / frozen", final_name, "phase 16b", "approved scope / not implemented", "phase 17", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag")) stop_if(grepl(term, status_text, fixed = TRUE), paste("status", term))
for (relative in status_surfaces) stop_if(grepl("phase 14", tolower(text_rel(relative)), fixed = TRUE) && grepl("phase 15", tolower(text_rel(relative)), fixed = TRUE), paste("status phases", relative))

cat(sprintf("PHASE16A_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, stressors=24, relationships=36, rules=32, responses=13, technology modifiers=11, feedback=10, matrix cells=312, candidates=6, Phase 14A/14B=24/23, Phase 15A/15B=30/28, prior entries=%d, prior unique=%d, review=deleg_9fa57f45 passed:true, propagation/evidence/technology/endpoint invariants=passed, Phase 16B/17 not executed\n", nrow(final_x), nrow(working), prior_entries, length(unique(prior_paths))))
