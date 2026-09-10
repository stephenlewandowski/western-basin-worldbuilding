#!/usr/bin/env Rscript
# Independent base-R validation for Phase 14B Atlas integration.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)

failures <- character()
check <- function(name, condition, detail) {
  if (!isTRUE(condition)) failures <<- c(failures, paste0(name, ": ", detail))
  cat(if (isTRUE(condition)) "PASS " else "FAIL ", name, " — ", detail, "\n", sep = "")
}
path <- function(rel) file.path(root, gsub("/", .Platform$file.sep, rel, fixed = TRUE))
read_csv_rel <- function(rel) read.csv(path(rel), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())

ontology <- readLines(path("metadata/atlas_systems.yml"), warn = FALSE, encoding = "UTF-8")
evidence <- readLines(path("metadata/atlas_evidence_vocabulary.yml"), warn = FALSE, encoding = "UTF-8")
layers <- readLines(path("metadata/atlas_layers.yml"), warn = FALSE, encoding = "UTF-8")
vocabulary <- readLines(path("metadata/atlas_relationship_vocabulary.yml"), warn = FALSE, encoding = "UTF-8")
layer_ids <- sub("^- atlas_layer_id: ", "", layers[grepl("^- atlas_layer_id: ", layers)])
layer_systems <- sub("^  system_id: ", "", layers[grepl("^  system_id: ", layers)])
layer_phases <- sub("^  source_phase: ", "", layers[grepl("^  source_phase: ", layers)])
layer_artifacts <- sub("^  source_artifact: ", "", layers[grepl("^  source_artifact: ", layers)])
system_lines <- ontology[grepl("^  - system_id: SYS-", ontology)]
system_ids <- sub("^  - system_id: ([^ ]+).*$", "\\1", system_lines)
valid_phases <- c("1", "2A", "2B", "2C", "2D", "3A", "3B", "3C", "4A", "4B", "4C", "5A", "5B", "5C", "6A", "6B", "6C", "7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B", "9C", "10A", "10B", "10C", "11A", "11B", "11C", "12A", "12B", "12C", "13A", "13B", "13C", "14A", "14B", "1/2")
check("ontology_system_count", length(unique(system_ids)) == 13, as.character(length(unique(system_ids))))
check("layer_ids_unique", length(layer_ids) > 0 && length(unique(layer_ids)) == length(layer_ids), as.character(length(layer_ids)))
missing_layers <- layer_artifacts[!file.exists(path(layer_artifacts))]
check("registered_artifacts_exist", length(missing_layers) == 0, paste(missing_layers, collapse = ","))
check("registered_system_ids_resolve", all(layer_systems %in% system_ids), paste(setdiff(unique(layer_systems), system_ids), collapse = ","))
check("registered_source_phases_valid", all(gsub("'", "", layer_phases) %in% valid_phases), paste(setdiff(unique(layer_phases), valid_phases), collapse = ","))
check("registry_multiple_formats", length(unique(sub("^  physical_format: ", "", layers[grepl("^  physical_format: ", layers)]))) >= 4, "format count")
check("registry_provenance_and_limits", sum(grepl("^  provenance_pointer: ", layers)) == length(layer_ids) && sum(grepl("^  limitations: ", layers)) == length(layer_ids), "registry fields")

rel <- read_csv_rel("data/processed/integration/relationship_normalization_crosswalk.csv")
inv <- read_csv_rel("data/processed/integration/relationship_taxonomy_inventory.csv")
allowed_rel <- c("physical flow", "material flow", "energy flow", "information / observation", "governance / authority", "operational dependency", "ecological relationship", "exposure pathway", "population / mobility interface", "surveillance / detection", "scenario influence", "high-level association", "unresolved / unclassified")
check("relationship_rows_retain_14A_inventory", nrow(rel) == 367 && nrow(inv) == 367 && setequal(rel$local_taxonomy_id, inv$taxonomy_id), paste(nrow(rel), nrow(inv)))
check("relationship_ids_unique", length(unique(rel$atlas_normalization_id)) == nrow(rel), as.character(nrow(rel)))
check("relationship_classes_valid", all(rel$normalized_relationship_class %in% allowed_rel), paste(setdiff(unique(rel$normalized_relationship_class), allowed_rel), collapse = ","))
check("relationship_semantic_fields", all(nzchar(rel$directionality) & nzchar(rel$causal_semantics) & nzchar(rel$flow_semantics) & nzchar(rel$Atlas_join_role) & nzchar(rel$mapping_status) & nzchar(rel$information_loss_or_caveat)), "blank normalized field")
energy <- rel[rel$source_phase == "3", , drop = FALSE]
energy_class <- setNames(energy$normalized_relationship_class, tolower(energy$local_term))
if ("communications" %in% names(energy_class)) check("energy_control_information_not_energy_flow", energy_class[["communications"]] != "energy flow", energy_class[["communications"]]) else check("energy_control_information_not_energy_flow", TRUE, "term absent")
for (term in c("generation_grid_interface", "regional_grid_interface", "bidirectional_storage_interface")) if (term %in% names(energy_class)) check(paste0("energy_flow_", term), energy_class[[term]] == "energy flow", energy_class[[term]])
for (term in c("electricity", "grid_serves_load", "grid_serves_planned_compute", "cooling_water", "thermal_dependency", "storage_support")) if (term %in% names(energy_class)) check(paste0("energy_dependency_", term), energy_class[[term]] == "operational dependency", energy_class[[term]])
if ("fuel" %in% names(energy_class)) check("energy_fuel_is_material_input", energy_class[["fuel"]] == "material flow", energy_class[["fuel"]])

endpoint <- read_csv_rel("data/processed/integration/endpoint_role_crosswalk.csv")
valid_roles <- c("physical asset", "geographic unit", "system node", "institutional actor", "ecological entity", "population/settlement entity", "monitoring/surveillance interface", "generalized external interface", "conceptual interface", "scenario-only entity")
check("endpoint_role_rows", nrow(endpoint) == 36, as.character(nrow(endpoint)))
check("endpoint_role_values", all(endpoint$endpoint_role %in% valid_roles), paste(setdiff(unique(endpoint$endpoint_role), valid_roles), collapse = ","))
check("endpoint_result_preserved", identical(as.integer(table(endpoint$inherited_mapping_status)[c("resolved_system_level", "retained_conceptual")]), c(34L, 2L)), paste(table(endpoint$inherited_mapping_status), collapse = ","))
check("conceptual_endpoint_role_only", all(endpoint$conceptual_endpoint_preserved == "yes" & endpoint$role_mapping_status == "normalized_role_only"), "conceptual endpoint role mapping")
check("generalized_endpoints_not_localized", all(endpoint$inherited_mapping_status != "retained_conceptual" | endpoint$endpoint_role == "generalized external interface"), "retained conceptual endpoint localized")

# Canonical dependency inputs and lineage.
dep <- read_csv_rel("data/processed/integration/atlas_dependency_crosswalk.csv")
check("dependency_rows", nrow(dep) == 761, as.character(nrow(dep)))
check("dependency_ids_unique", length(unique(dep$atlas_relationship_id)) == nrow(dep), as.character(nrow(dep)))
check("dependency_system_ids", all((!nzchar(dep$source_system_id) | dep$source_system_id %in% system_ids) & (!nzchar(dep$target_system_id) | dep$target_system_id %in% system_ids)), "unresolved system ID")
check("dependency_evidence_classes", all(dep$evidence_class %in% c("OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD")), "evidence vocabulary")
check("dependency_baseline_scenario_separation", all(dep$scenario_status == "BASELINE_DEPENDENCY"), paste(unique(dep$scenario_status), collapse = ","))
check("dependency_lineage_fields", all(nzchar(dep$source_phase) & nzchar(dep$source_artifact) & nzchar(dep$local_relationship_id) & nzchar(dep$caveat)), "blank dependency lineage")
check("dependency_source_ids_retained", all(nzchar(dep$source_id)), "blank source_id")
check("dependency_roles", all(dep$endpoint_role_source %in% valid_roles & dep$endpoint_role_target %in% valid_roles), "invalid endpoint role")
check("dependency_join_keys_typed", all(dep$source_join_level != "exact" | grepl("^ENT-", dep$source_atlas_entity_id)) && all(dep$target_join_level != "exact" | grepl("^ENT-", dep$target_atlas_entity_id)), "exact/system-level collapse")
check("dependency_system_level_distinct", !any(dep$source_join_level == "exact" & grepl("^SYS-", dep$source_atlas_entity_id)) && !any(dep$target_join_level == "exact" & grepl("^SYS-", dep$target_atlas_entity_id)), "system ID used as exact entity")
pop <- dep[dep$source_phase == "11B", , drop = FALSE]
pop_inf <- sum(pop$evidence_class == "INFERRED")
pop_ctx <- sum(pop$evidence_class == "CONTEXT_REUSED")
check("population_high_inference_counts", nrow(pop) == 520 && pop_inf == 468 && pop_ctx == 52, paste(nrow(pop), pop_inf, pop_ctx, sep = ","))
check("population_use_rules", all(grepl("QUALITATIVE_STRESS_TEST_ONLY", pop$Atlas_use, fixed = TRUE) & grepl("NO_QUANTITATIVE_AGGREGATION", pop$Atlas_use, fixed = TRUE)), "population use rule")
check("population_no_numeric_confidence", !any(grepl("numeric confidence", pop$caveat, ignore.case = TRUE)), "numeric confidence")

matrix <- read_csv_rel("data/processed/integration/system_joinability_matrix.csv")
check("joinability_pair_count", nrow(matrix) == 78, as.character(nrow(matrix)))
boolean_fields <- c("direct_exact_identity_join", "system_level_conceptual_join", "dependency_relationship_join", "spatial_colocation_only", "scenario_layer_reference", "scenario_only_link", "no_defensible_current_join")
check("joinability_boolean_findings", all(vapply(matrix[boolean_fields], function(x) all(x %in% c("YES", "NO")), logical(1))), "boolean field")
check("scenario_reference_and_exclusive_flags", all(matrix$scenario_only_link == "NO" | matrix$dependency_relationship_join == "NO"), "scenario-only flag overlaps baseline dependency")
check("joinability_no_score", !any(tolower(names(matrix)) %in% c("score", "connectivity_score", "risk_score")), paste(names(matrix), collapse = ","))
check("joinability_colocation_boundary", all(matrix$spatial_colocation_only == "NO" & grepl("co-location is not treated as causation", tolower(matrix$caveat), fixed = TRUE)), "co-location caveat")
check("joinability_no_risk_language", !any(tolower(names(matrix)) %in% c("score", "connectivity_score", "risk_score", "composite_risk_score")), "risk score field")

svg_text <- paste(readLines(path("outputs/figures/atlas_cross_system_joinability_dependency_architecture.svg"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
check("figure_svg_qa", all(vapply(c("Cross-System Joinability / Dependency Architecture", "Exact/entity-level", "System-level conceptual", "Inferred relationship", "Scenario-only relationship", "not a geographic map", "co-location"), grepl, logical(1), x = svg_text, fixed = TRUE)), "figure labels")
png <- readBin(path("outputs/figures/atlas_cross_system_joinability_dependency_architecture.png"), "raw", n = file.info(path("outputs/figures/atlas_cross_system_joinability_dependency_architecture.png"))$size)
check("figure_png_qa", length(png) > 1000 && identical(as.integer(png[1:8]), c(137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L)), as.character(length(png)))

sha256_file <- function(file) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    output <- system2(cmd, file, stdout = TRUE, stderr = TRUE)
    if (length(output) == 0) return(NA_character_)
    return(substr(tolower(gsub("[^0-9a-f]", "", output[[1]])), 1, 64))
  }
  certutil <- Sys.which("certutil")
  if (nchar(certutil) == 0) return(NA_character_)
  output <- system2(certutil, c("-hashfile", file, "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output[grepl("^[0-9A-Fa-f]{64}$", gsub("[[:space:]]+", "", output))]))
  if (length(hits) == 0) NA_character_ else hits[[1]]
}
canonical_text_hash <- function(file) {
  b <- readBin(file, "raw", n = file.info(file)$size)
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(b), perl = TRUE))
  tmp <- tempfile(fileext = ".txt"); writeBin(canonical, tmp); on.exit(unlink(tmp), add = TRUE)
  sha256_file(tmp)
}
manifest_hash_pairs <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  current <- NA_character_; rows <- list()
  for (line in lines) {
    bare <- regmatches(line, regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"[[:space:]]*,?[[:space:]]*$', line, perl = TRUE))[[1]]
    if (length(bare) == 3 && grepl("/", bare[2], fixed = TRUE)) { rows[[length(rows)+1L]] <- c(path=bare[2], sha256=bare[3]); current <- NA_character_; next }
    pm <- regmatches(line, regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:', line, perl = TRUE))[[1]]
    if (length(pm) == 2 && grepl("/", pm[2], fixed = TRUE)) current <- pm[2]
    hm <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(hm) == 2 && !is.na(current)) { rows[[length(rows)+1L]] <- c(path=current, sha256=hm[2]); current <- NA_character_ }
  }
  if (!length(rows)) return(data.frame(path=character(), sha256=character(), stringsAsFactors=FALSE))
  do.call(rbind, lapply(rows, function(x) data.frame(path=unname(x[["path"]]), sha256=unname(x[["sha256"]]), stringsAsFactors=FALSE)))
}
verify_manifest <- function(file) {
  pairs <- manifest_hash_pairs(file); failures <- character()
  if (nrow(pairs) > 0) for (i in seq_len(nrow(pairs))) {
    fp <- path(pairs$path[[i]])
    if (!file.exists(fp)) failures <- c(failures, pairs$path[[i]]) else {
      raw <- sha256_file(fp); ok <- isTRUE(raw == pairs$sha256[[i]])
      if (!ok && tolower(tools::file_ext(fp)) %in% c("csv", "json", "md", "py", "r", "R", "yaml", "yml", "svg", "txt")) ok <- isTRUE(canonical_text_hash(fp) == pairs$sha256[[i]])
      if (!ok) failures <- c(failures, pairs$path[[i]])
    }
  }
  failures
}
freeze_files <- list.files(path("reports"), pattern = "freeze_manifest\\.json$", full.names = TRUE)
freeze_failures <- unlist(lapply(freeze_files, function(x) verify_manifest(x)))
check("phase14a_and_prior_freeze_integrity", length(freeze_failures) == 0, paste(head(freeze_failures, 10), collapse = ","))
a14a <- verify_manifest(path("reports/phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"))
check("phase14a_final_manifest_readback", length(a14a) == 0, paste(a14a, collapse = ","))
working <- verify_manifest(path("reports/phase14b_manifest.json"))
check("phase14b_working_manifest_integrity", length(working) == 0, paste(working, collapse = ","))

changed <- system2("git", c("-C", root, "diff", "--name-only", "dd2c0706f8d1f6b73974a530e64de8a82aff2eb1"), stdout = TRUE, stderr = TRUE)
check("no_phase15_changes", !any(grepl("phase15", tolower(changed))), paste(changed[grepl("phase15", tolower(changed))], collapse = ","))
check("active_holds_retained", grepl("C — HOLD / noncanonical", paste(readLines(path("docs/canon_status.md"), warn=FALSE, encoding="UTF-8"), collapse="\n"), fixed=TRUE) && grepl("UNRESOLVED", paste(readLines(path("docs/canon_status.md"), warn=FALSE, encoding="UTF-8"), collapse="\n"), fixed=TRUE), "hold text")
check("phase15_release_tag_boundary", grepl("Phase 15", paste(readLines(path("PROJECT_STATUS.md"), warn=FALSE, encoding="UTF-8"), collapse="\n"), fixed=TRUE) && grepl("NOT IMPLEMENTED", paste(readLines(path("PROJECT_STATUS.md"), warn=FALSE, encoding="UTF-8"), collapse="\n"), fixed=TRUE) && grepl("No release or tag", paste(readLines(path("PROJECT_STATUS.md"), warn=FALSE, encoding="UTF-8"), collapse="\n"), fixed=TRUE), "boundary text")

write_r_result <- function(passed) {
  escape_json <- function(x) gsub('"', '\\\\"', gsub('\\\\', '\\\\\\\\', x, fixed = TRUE), fixed = TRUE)
  failure_json <- if (length(failures) == 0) "" else paste(sprintf('"%s"', escape_json(failures)), collapse = ",")
  lines <- c(
    "{",
    '  "phase": "14B",',
    sprintf('  "passed": %s,', tolower(as.character(passed))),
    sprintf('  "failure_count": %d,', length(failures)),
    sprintf('  "failures": [%s]', failure_json),
    "}"
  )
  writeLines(lines, path("reports/phase14b_r_validation_result.json"), useBytes = TRUE)
}

if (length(failures) == 0) {
  write_r_result(TRUE)
  cat("PHASE14B_R_VALIDATION PASSED\n")
  quit(status=0)
} else {
  write_r_result(FALSE)
  cat("PHASE14B_R_VALIDATION FAILED\n")
  cat(paste(failures, collapse="\n"), "\n")
  quit(status=1)
}
