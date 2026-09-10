#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 14B.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)
reports <- file.path(root, "reports")
final_name <- "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
working_name <- "phase14b_manifest.json"
artifact_check_name <- "phase14b_artifact_check.json"
review_name <- "phase14b_independent_review.md"
initial_review_name <- "phase14b_independent_review_initial.md"
r_result_name <- "phase14b_r_validation_result.json"
a14a_name <- "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
source_commit <- "adac6c5dc072b1a61a1474c5f6dad74c5e65278f"
expected_prior_entries <- 512L
expected_prior_unique <- 503L
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
expected_final <- sort(c(
  "data/processed/integration/atlas_dependency_crosswalk.csv",
  "data/processed/integration/endpoint_role_crosswalk.csv",
  "data/processed/integration/relationship_normalization_crosswalk.csv",
  "data/processed/integration/system_joinability_matrix.csv",
  "metadata/atlas_layers.yml",
  "metadata/atlas_relationship_vocabulary.yml",
  "outputs/figures/atlas_cross_system_joinability_dependency_architecture.png",
  "outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg",
  file.path("reports", artifact_check_name),
  "reports/phase14b_atlas_layer_registry.md",
  "reports/phase14b_build_summary.json",
  "reports/phase14b_dependency_integration.md",
  file.path("reports", review_name),
  file.path("reports", initial_review_name),
  "reports/phase14b_integration_qa.md",
  file.path("reports", r_result_name),
  "reports/phase14b_relationship_normalization.md",
  "src/R/systems/validate_phase14b_integration.R",
  "src/python/systems/build_phase14b_integration.py",
  "src/python/systems/validate_phase14b_integration.py",
  file.path("reports", working_name),
  "src/python/systems/validate_phase14b_freeze.py",
  "src/R/systems/validate_phase14b_freeze.R"
))
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
path <- function(rel) file.path(root, gsub("/", .Platform$file.sep, rel, fixed = TRUE))
read_csv_rel <- function(rel) read.csv(path(rel), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
json_text <- function(file) paste(readLines(file, warn = FALSE, encoding = "UTF-8"), collapse = " ")
raw_bytes <- function(file) readBin(file, "raw", n = as.numeric(file.info(file)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix); on.exit(unlink(tmp), add = TRUE); writeBin(raw, tmp)
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    output <- system2(cmd, tmp, stdout = TRUE, stderr = TRUE)
    hits <- regmatches(paste(output, collapse = " "), gregexpr("[0-9a-fA-F]{64}", paste(output, collapse = " "), perl = TRUE))[[1]]
    stop_if(length(hits) > 0L, "sha256sum failed"); return(tolower(hits[[1]]))
  }
  certutil <- Sys.which("certutil"); stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  output <- system2(certutil, c("-hashfile", tmp, "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) > 0L, "certutil failed"); hits[[1]]
}
portable_match <- function(file, expected, recorded = NA_real_) {
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing artifact", file))
  raw <- raw_bytes(file); hashes <- c(sha256_raw(raw, tools::file_ext(file))); lengths <- c(length(raw))
  if (tolower(tools::file_ext(file)) %in% tolower(text_ext)) { canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE)); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed = TRUE)); hashes <- c(hashes, sha256_raw(canonical, tools::file_ext(file)), sha256_raw(crlf, tools::file_ext(file))); lengths <- c(lengths, length(canonical), length(crlf)) }
  tolower(expected) %in% hashes && (is.na(recorded) || as.numeric(recorded) %in% lengths)
}
manifest_entries <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  artifact_hits <- which(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  if (!length(artifact_hits)) artifact_hits <- which(grepl('"files"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  start <- artifact_hits[1]
  stop_if(!is.na(start), paste("missing artifacts collection", file))
  rel <- character(); hashes <- character(); bytes <- numeric(); current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() { if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }; current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_ }
  for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(direct) == 3L) { append_current(); rel <- c(rel, direct[[2]]); hashes <- c(hashes, direct[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl = TRUE))[[1]]
    if (length(nested) == 2L) { append_current(); current <- nested[[2]] }
    hit <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(hit) == 2L && !is.na(current)) current_hash <- hit[[2]]
    b <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl = TRUE))[[1]]
    if (length(b) == 2L && !is.na(current)) current_bytes <- as.numeric(b[[2]])
  }
  append_current(); data.frame(rel = rel, sha256 = hashes, bytes = bytes, stringsAsFactors = FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels = character()) {
  file <- file.path(reports, name); stop_if(file.exists(file), paste("missing manifest", name)); x <- manifest_entries(file)
  stop_if(nrow(x) == expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(setequal(as.character(x$rel), expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
require_terms <- function(relative, terms) { txt <- tolower(paste(readLines(path(relative), warn = FALSE, encoding = "UTF-8"), collapse = " ")); for (term in terms) stop_if(grepl(tolower(term), txt, fixed = TRUE), paste(relative, term)) }

final_txt <- json_text(file.path(reports, final_name))
for (term in c(
  '"accepted_phase": "14B"', '"baseline": "Atlas Layer Registry & Cross-System Dependency Normalization"', '"status": "ACCEPTED / FROZEN"',
  paste0('"source_commit": "', source_commit, '"'), '"registry_entries": 213', '"relationship_rows": 367', '"endpoint_role_rows": 36',
  '"dependency_rows": 761', '"joinability_rows": 78', '"population_total": 520', '"population_inferred": 468', '"population_context_reused": 52',
  '"phase14_overall_status": "COMPLETE / ACCEPTED / FROZEN"', '"phase15_implemented": false', '"release_created": false', '"tag_created": false',
  '"great_black_swamp": "C — HOLD / noncanonical"', '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"', '"Phase 6B manifest status wording mismatch"',
  '"Phase 3A missing manifest status"', '"Phase 2A superseded legacy worktree"'
)) stop_if(grepl(term, final_txt, fixed = TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(expected_final), expected_final)
working_txt <- json_text(file.path(reports, working_name)); stop_if(grepl('"phase": "14B"', working_txt, fixed = TRUE), "working manifest phase")
stop_if(grepl('"status": "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE"', working_txt, fixed = TRUE), "working manifest status")
working_x <- verify_manifest(working_name, length(manifest_entries(file.path(reports, working_name))$rel))
check_txt <- tolower(json_text(file.path(reports, artifact_check_name)))
for (term in c('"passed": true', '"errors": []', '"registry_entries": 213', '"relationship_rows": 367', '"dependency_rows": 761', '"joinability_rows": 78')) stop_if(grepl(tolower(term), check_txt, fixed = TRUE), paste("artifact check", term))
r_txt <- json_text(file.path(reports, r_result_name)); for (term in c('"phase": "14B"', '"passed": true', '"failure_count": 0', '"failures": []')) stop_if(grepl(term, r_txt, fixed = TRUE), paste("R result", term))
review_txt <- json_text(file.path(reports, review_name)); for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"registry_errors": []', '"relationship_normalization_errors": []', '"identity_errors": []', '"evidence_classification_errors": []', '"joinability_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(term, tolower(review_txt), fixed = TRUE), paste("review", term))
initial_txt <- tolower(json_text(file.path(reports, initial_review_name))); stop_if(grepl('"passed": false', initial_txt, fixed = TRUE), "initial review lineage")

layers <- readLines(path("metadata/atlas_layers.yml"), warn = FALSE, encoding = "UTF-8")
layer_ids <- sub("^- atlas_layer_id: ", "", layers[grepl("^- atlas_layer_id: ", layers)])
formats <- sub("^  physical_format: ", "", layers[grepl("^  physical_format: ", layers)])
stop_if(length(layer_ids) == 213L && length(unique(layer_ids)) == 213L, "registry count/IDs")
stop_if(identical(as.integer(table(formats)[c("CSV", "GeoJSON", "GeoPackage", "JSON", "PNG", "SVG", "YAML")]), c(81L, 2L, 16L, 1L, 55L, 55L, 3L)), "registry formats")
rel <- read_csv_rel("data/processed/integration/relationship_normalization_crosswalk.csv"); inv <- read_csv_rel("data/processed/integration/relationship_taxonomy_inventory.csv")
stop_if(nrow(rel) == 367L && nrow(inv) == 367L && length(unique(rel$atlas_normalization_id)) == 367L && setequal(rel$local_taxonomy_id, inv$taxonomy_id), "relationship rows/lineage")
energy <- rel[rel$source_phase == "3", , drop = FALSE]; energy_class <- setNames(energy$normalized_relationship_class, tolower(energy$local_term))
expected_energy <- c(generation_grid_interface="energy flow", regional_grid_interface="energy flow", bidirectional_storage_interface="energy flow", electricity="operational dependency", grid_serves_load="operational dependency", grid_serves_planned_compute="operational dependency", cooling_water="operational dependency", storage_support="operational dependency", communications="information / observation", fuel="material flow", weather="ecological relationship")
stop_if(all(!is.na(energy_class[names(expected_energy)]) & unname(energy_class[names(expected_energy)]) == unname(expected_energy)), "energy taxonomy")
endpoint <- read_csv_rel("data/processed/integration/endpoint_role_crosswalk.csv"); stop_if(nrow(endpoint) == 36L && identical(as.integer(table(endpoint$inherited_mapping_status)[c("resolved_system_level", "retained_conceptual")]), c(34L, 2L)), "endpoint disposition")
dep <- read_csv_rel("data/processed/integration/atlas_dependency_crosswalk.csv"); pop <- dep[dep$source_phase == "11B", , drop = FALSE]
stop_if(nrow(dep) == 761L && length(unique(dep$atlas_relationship_id)) == 761L && all(nzchar(dep$source_id) & dep$scenario_status == "BASELINE_DEPENDENCY" & nzchar(dep$caveat)), "dependency lineage")
stop_if(nrow(pop) == 520L && sum(pop$evidence_class == "INFERRED") == 468L && sum(pop$evidence_class == "CONTEXT_REUSED") == 52L && all(grepl("QUALITATIVE_STRESS_TEST_ONLY", pop$Atlas_use, fixed = TRUE) & grepl("NO_QUANTITATIVE_AGGREGATION", pop$Atlas_use, fixed = TRUE)), "population preservation")
matrix <- read_csv_rel("data/processed/integration/system_joinability_matrix.csv"); boolean_fields <- c("direct_exact_identity_join", "system_level_conceptual_join", "dependency_relationship_join", "spatial_colocation_only", "scenario_layer_reference", "scenario_only_link", "no_defensible_current_join")
stop_if(nrow(matrix) == 78L && all(vapply(matrix[boolean_fields], function(x) all(x %in% c("YES", "NO")), logical(1))) && all(matrix$spatial_colocation_only == "NO" & grepl("co-location is not treated as causation", tolower(matrix$caveat), fixed = TRUE)) && !any(tolower(names(matrix)) %in% c("score", "connectivity_score", "risk_score", "composite_risk_score")), "joinability metadata")
svg <- paste(readLines(path("outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
for (term in c("Cross-System Joinability / Dependency Architecture", "Exact/entity-level", "System-level conceptual", "Inferred relationship", "Scenario-only relationship", "not a geographic map", "co-location")) stop_if(grepl(term, svg, fixed = TRUE), paste("figure", term))
png <- raw_bytes(path("outputs/figures/atlas_cross_system_joinability_dependency_architecture.png")); stop_if(length(png) > 1000L && identical(as.integer(png[1:8]), c(137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L)), "figure PNG")

a14a <- json_text(file.path(reports, a14a_name)); for (term in c('"accepted_phase": "14A"', '"status": "ACCEPTED / FROZEN"', '"identity_rows": 456', '"relationship_rows": 367')) stop_if(grepl(term, a14a, fixed = TRUE), paste("Phase 14A", term))
prior_entries <- 0L; protected <- character(); prior_manifests <- list.files(reports, pattern = "freeze_manifest[.]json$", full.names = TRUE); prior_manifests <- prior_manifests[basename(prior_manifests) != final_name]
for (mf in sort(prior_manifests)) { x <- manifest_entries(mf); prior_entries <- prior_entries + nrow(x); protected <- c(protected, x$rel); for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", x$rel[[i]])) }
stop_if(prior_entries == expected_prior_entries && length(unique(protected)) == expected_prior_unique, paste("prior inventory", prior_entries, length(unique(protected))))
changed <- trimws(system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE)); stop_if(!any(changed == "metadata/systems.yml"), "metadata/systems.yml changed"); stop_if(!any(grepl("[.]gpkg$", changed)), "GeoPackage changed"); stop_if(!any(grepl("phase15", tolower(changed))), "Phase 15 changed"); stop_if(length(intersect(changed, unique(protected))) == 0L, paste("prior protected artifact changed", paste(intersect(changed, unique(protected)), collapse = ",")))
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")) require_terms(relative, c("phase 14b", "accepted / frozen", final_name, "phase 15", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "no release or tag"))
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md")) require_terms(relative, c("phase 14", "complete"))
cat(sprintf("PHASE14B_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, prior entries=%d, prior unique=%d, review=passed:true, Phase 14 complete, Phase 15 absent\n", nrow(final_x), nrow(working_x), prior_entries, length(unique(protected))))
