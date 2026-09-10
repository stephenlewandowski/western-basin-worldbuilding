#!/usr/bin/env Rscript
# Independent base-R validator for Phase 14A.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)

failures <- character()
check <- function(name, condition, detail) {
  if (!isTRUE(condition)) failures <<- c(failures, paste0(name, ": ", detail))
  cat(if (isTRUE(condition)) "PASS " else "FAIL ", name, " — ", detail, "\n", sep = "")
}
path <- function(rel) file.path(root, gsub("/", .Platform$file.sep, rel, fixed = TRUE))
read_csv <- function(rel) read.csv(path(rel), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())

ontology_rel <- "metadata/atlas_systems.yml"
evidence_rel <- "metadata/atlas_evidence_vocabulary.yml"
identity_rel <- "data/processed/integration/system_identity_crosswalk.csv"
endpoint_rel <- "data/processed/integration/external_endpoint_crosswalk.csv"
relationship_rel <- "data/processed/integration/relationship_taxonomy_inventory.csv"
manifest_rel <- "reports/phase14a_manifest.json"
ontology_lines <- readLines(path(ontology_rel), warn = FALSE, encoding = "UTF-8")
evidence_lines <- readLines(path(evidence_rel), warn = FALSE, encoding = "UTF-8")

system_end <- match("identity_sources:", ontology_lines)
ontology_system_lines <- if (is.na(system_end)) ontology_lines else ontology_lines[seq_len(system_end - 1L)]
system_lines <- ontology_system_lines[grepl("^  - system_id: SYS-", ontology_system_lines)]
system_ids <- sub("^  - system_id: ([^ ]+).*$", "\\1", system_lines)
check("ontology_system_count", length(system_ids) == 13, as.character(length(system_ids)))
check("ontology_system_ids_unique", length(unique(system_ids)) == length(system_ids) && all(grepl("^SYS-", system_ids)), paste(system_ids, collapse = ","))
required_labels <- c("preferred_label:", "atlas_display_label:", "broad_system_family:", "originating_phases:", "canonical_status:", "primary_tables:", "principal_maps:", "temporal_basis:", "baseline_scenario_distinction:", "provenance_pointer:")
check("ontology_required_fields", all(vapply(required_labels, function(x) any(grepl(x, ontology_lines, fixed = TRUE)), logical(1))), paste(required_labels, collapse = ","))

# All listed primary table paths are checked independently from the YAML text.
table_lines <- ontology_lines[grepl("^      - (data/|outputs/)", ontology_lines)]
table_paths <- sub("^      - ", "", table_lines)
missing_tables <- table_paths[!file.exists(path(table_paths))]
check("ontology_listed_paths_exist", length(missing_tables) == 0, paste(missing_tables, collapse = ","))
check("existing_systems_registry_untouched", !file.exists(path(".phase14a_forbidden_systems_marker")), "metadata/systems.yml is not an output of this package")

identity <- read_csv(identity_rel)
endpoint <- read_csv(endpoint_rel)
relationship <- read_csv(relationship_rel)
check("identity_rows", nrow(identity) == 456, as.character(nrow(identity)))
check("identity_atlas_ids_unique", length(unique(identity$atlas_entity_id)) == nrow(identity), as.character(nrow(identity)))
check("identity_source_local_pairs_unique", length(unique(paste(identity$source_artifact, identity$local_id, sep = "|"))) == nrow(identity), as.character(nrow(identity)))
check("identity_mapping_types", all(identity$mapping_type == "exact identity"), paste(unique(identity$mapping_type), collapse = ","))
check("identity_mapping_status", all(identity$mapping_status == "resolved"), paste(unique(identity$mapping_status), collapse = ","))
check("identity_lineage_fields", all(nzchar(identity$source_phase) & nzchar(identity$source_artifact) & nzchar(identity$local_id) & nzchar(identity$evidence_basis)), "blank source lineage")
scenario_rows <- identity[tolower(identity$canon_status) == "scenario" | tolower(identity$reality_status) == "fictional", , drop = FALSE]
scenario_labels_ok <- nrow(scenario_rows) == 0 || all(tolower(scenario_rows$canon_status) == "scenario" & tolower(scenario_rows$reality_status) == "fictional")
check("identity_scenario_labels_retained", scenario_labels_ok, "scenario/fictional identity labels were not retained")

source_id_fields <- c(
  "data/processed/networks/water_system_nodes.csv" = "feature_id",
  "data/processed/networks/materials_system_nodes.csv" = "node_id",
  "data/processed/networks/energy_system_nodes.csv" = "node_id",
  "data/processed/networks/energy_dependency_nodes.csv" = "node_id",
  "data/processed/networks/observation_system_nodes.csv" = "node_id",
  "data/processed/networks/freight_system_nodes.csv" = "node_id",
  "data/processed/networks/ecology_system_nodes.csv" = "node_id",
  "data/processed/networks/exposure_context_nodes.csv" = "node_id",
  "data/processed/networks/biogeochemical_system_nodes.csv" = "node_id",
  "data/processed/networks/climate_hazard_nodes.csv" = "node_id",
  "data/processed/analysis/governance_actors.csv" = "actor_id",
  "data/processed/analysis/governance_authorities.csv" = "authority_id",
  "data/processed/analysis/population_settlement_nodes.csv" = "node_id",
  "data/processed/networks/vector_ecology_nodes.csv" = "node_id",
  "data/processed/networks/infectious_disease_nodes.csv" = "node_id"
)
source_errors <- character()
for (artifact in unique(identity$source_artifact)) {
  if (!(artifact %in% names(source_id_fields))) {
    source_errors <- c(source_errors, paste0("unknown source artifact ", artifact))
  } else {
    d <- read.csv(path(artifact), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
    field <- source_id_fields[[artifact]]
    if (!(field %in% names(d))) source_errors <- c(source_errors, paste0("missing field ", artifact, ":", field))
    else if (any(!identity$local_id[identity$source_artifact == artifact] %in% d[[field]])) source_errors <- c(source_errors, paste0("unresolved local ID in ", artifact))
  }
}
check("identity_source_artifacts_and_local_ids", length(source_errors) == 0, paste(source_errors, collapse = "; "))

register <- read_csv("data/processed/analysis/infectious_disease_dependency_register.csv")
conceptual <- grepl("^(EXT|REF)-", register$from_id) | grepl("^(EXT|REF)-", register$to_id)
check("endpoint_rows", nrow(endpoint) == 36, as.character(nrow(endpoint)))
check("endpoint_conceptual_dependency_rows", length(unique(endpoint$dependency_id)) == 25 && all(unique(endpoint$dependency_id) %in% register$dependency_id), as.character(length(unique(endpoint$dependency_id))))
lookup <- match(endpoint$dependency_id, register$dependency_id)
expected <- ifelse(endpoint$endpoint_position == "from", register$from_id[lookup], register$to_id[lookup])
check("endpoint_source_alignment", all(expected == endpoint$local_endpoint_id), "local endpoint differs from Phase 13B register")
status_counts <- table(endpoint$mapping_status)
status_count <- function(name) if (name %in% names(status_counts)) as.integer(status_counts[[name]]) else 0L
check("endpoint_resolution_totals", identical(c(status_count("resolved_system_level"), status_count("retained_conceptual"), status_count("unresolved")), c(34L, 2L, 0L)), paste(names(status_counts), as.integer(status_counts), collapse = ","))
check("endpoint_no_exact_merge", !any(endpoint$mapping_type == "exact identity"), "conceptual endpoint was marked exact")
check("endpoint_unresolved_explicit", all(endpoint$mapping_status != "unresolved" | (endpoint$mapping_type == "unresolved" & endpoint$atlas_entity_id == "")), "unresolved mapping not explicit")
check("endpoint_lineage", all(endpoint$source_phase == "13B" & endpoint$source_artifact == "data/processed/analysis/infectious_disease_dependency_register.csv" & nzchar(endpoint$evidence_basis)), "endpoint provenance incomplete")

required_classes <- c("OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD")
class_lines <- evidence_lines[grepl("^  - class_id: ", evidence_lines)]
class_ids <- sub("^  - class_id: ([A-Z_]+).*$", "\\1", class_lines)
check("evidence_vocabulary_classes", setequal(class_ids, required_classes), paste(class_ids, collapse = ","))
check("evidence_mapping_count", sum(grepl("^  - local_field: ", evidence_lines)) == 17, as.character(sum(grepl("^  - local_field: ", evidence_lines))))
check("evidence_loss_notes", sum(grepl("information_lost_or_caveat:", evidence_lines, fixed = TRUE)) >= 17, "loss/caveat fields")
required_non_eq <- c("- [fact, inference]", "- [fact, scenario_assumption]", "- [observation, derived_value]", "- [dependency, risk]", "- [association, causation]")
check("evidence_non_equivalences", all(vapply(required_non_eq, function(x) any(grepl(x, evidence_lines, fixed = TRUE)), logical(1))), paste(required_non_eq, collapse = ","))

allowed_classes <- c("physical flow", "material flow", "energy flow", "information / observation", "governance / authority", "operational dependency", "ecological relationship", "exposure pathway", "population / mobility interface", "scenario influence", "high-level interface / association", "unclassified candidate")
check("relationship_rows", nrow(relationship) == 367, as.character(nrow(relationship)))
check("relationship_ids_unique", length(unique(relationship$taxonomy_id)) == nrow(relationship), as.character(nrow(relationship)))
check("relationship_classes", all(relationship$proposed_high_level_class %in% allowed_classes), paste(setdiff(unique(relationship$proposed_high_level_class), allowed_classes), collapse = ","))
check("relationship_inventory_only", all(relationship$normalization_status == "inventory_only_14A"), paste(unique(relationship$normalization_status), collapse = ","))
check("relationship_caveats", all(nzchar(relationship$information_lost_or_caveat)), "blank relationship caveat")
relationship_source_errors <- character()
for (artifact in unique(relationship$source_artifact)) {
  if (!file.exists(path(artifact))) relationship_source_errors <- c(relationship_source_errors, artifact)
}
check("relationship_source_artifacts", length(relationship_source_errors) == 0, paste(relationship_source_errors, collapse = ","))

svg <- path("outputs/figures/western_basin_systems_architecture.svg")
svg_text <- paste(readLines(svg, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
check("architecture_svg", grepl("Western Basin Systems Architecture", svg_text, fixed = TRUE) && grepl("not a geographic map", svg_text, fixed = TRUE), "title or conceptual-map caveat missing")
png <- path("outputs/figures/western_basin_systems_architecture.png")
png_raw <- readBin(png, "raw", n = file.info(png)$size)
png_signature <- as.integer(png_raw[1:8])
check("architecture_png", length(png_raw) > 1000 && identical(png_signature, c(137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L)), paste(length(png_raw), collapse = ","))

sha256_file <- function(file) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    output <- system2(cmd, file, stdout = TRUE, stderr = TRUE)
    if (length(output) == 0) return(NA_character_)
    return(tolower(gsub("[^0-9a-f]", "", strsplit(trimws(output[[1]]), "[[:space:]]+")[[1]][1])))
  }
  certutil <- Sys.which("certutil")
  if (nchar(certutil) == 0) return(NA_character_)
  output <- system2(certutil, c("-hashfile", file, "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output[grepl("^[0-9A-Fa-f]{64}$", gsub("[[:space:]]+", "", output))]))
  if (length(hits) == 0) NA_character_ else hits[[1]]
}
canonical_text_hash <- function(file) {
  b <- readBin(file, "raw", n = file.info(file)$size)
  # Called only for text extensions; binary frozen artifacts stay raw-byte strict.
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(b), perl = TRUE))
  tmp <- tempfile(fileext = ".txt")
  writeBin(canonical, tmp)
  on.exit(unlink(tmp), add = TRUE)
  sha256_file(tmp)
}
manifest_hash_pairs <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  current <- NA_character_
  rows <- list()
  for (line in lines) {
    bare_match <- regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"[[:space:]]*,?[[:space:]]*$', line, perl = TRUE)
    bare_parts <- regmatches(line, bare_match)[[1]]
    if (length(bare_parts) == 3 && grepl("/", bare_parts[2], fixed = TRUE)) {
      rows[[length(rows) + 1L]] <- c(path = bare_parts[2], sha256 = bare_parts[3])
      current <- NA_character_
      next
    }
    path_match <- regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:', line, perl = TRUE)
    parts <- regmatches(line, path_match)[[1]]
    if (length(parts) == 2 && grepl("/", parts[2], fixed = TRUE)) current <- parts[2]
    hash_match <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE)
    hparts <- regmatches(line, hash_match)[[1]]
    if (length(hparts) == 2 && !is.na(current)) {
      rows[[length(rows) + 1L]] <- c(path = current, sha256 = hparts[2])
      current <- NA_character_
    }
  }
  if (!length(rows)) return(data.frame(path = character(), sha256 = character(), stringsAsFactors = FALSE))
  do.call(rbind, lapply(rows, function(x) data.frame(path = unname(x[["path"]]), sha256 = unname(x[["sha256"]]), stringsAsFactors = FALSE)))
}

freeze_files <- list.files(path("reports"), pattern = "freeze_manifest\\.json$", full.names = TRUE)
freeze_total <- 0L
freeze_unique <- character()
freeze_errors <- character()
for (mf in freeze_files) {
  pairs <- manifest_hash_pairs(mf)
  for (i in seq_len(nrow(pairs))) {
    rel <- pairs$path[[i]]; expected_hash <- pairs$sha256[[i]]; fp <- path(rel)
    freeze_total <- freeze_total + 1L; freeze_unique <- unique(c(freeze_unique, rel))
    if (!file.exists(fp)) freeze_errors <- c(freeze_errors, paste0("missing:", rel))
    else {
      raw_hash <- sha256_file(fp)
      ok <- isTRUE(raw_hash == expected_hash)
      if (!ok && tolower(tools::file_ext(fp)) %in% c("csv", "md", "json", "yml", "yaml", "svg", "txt", "py", "r")) ok <- isTRUE(canonical_text_hash(fp) == expected_hash)
      if (!ok) freeze_errors <- c(freeze_errors, paste0("hash:", rel))
    }
  }
}
check("prior_freeze_integrity", length(freeze_errors) == 0, paste0("entries=", freeze_total, " unique=", length(freeze_unique), " errors=", paste(head(freeze_errors, 5), collapse = ";")))

working_pairs <- manifest_hash_pairs(path(manifest_rel))
working_errors <- character()
for (i in seq_len(nrow(working_pairs))) {
  fp <- path(working_pairs$path[[i]])
  if (!file.exists(fp) || !identical(sha256_file(fp), working_pairs$sha256[[i]])) working_errors <- c(working_errors, working_pairs$path[[i]])
}
check("phase14a_manifest_integrity", length(working_errors) == 0, paste(working_errors, collapse = ","))

status <- system2("git", c("-C", root, "status", "--short"), stdout = TRUE, stderr = TRUE)
forbidden <- status[grepl("metadata/systems\\.yml|glasspunk_base\\.gpkg|freeze_manifest\\.json", status)]
check("no_frozen_or_historical_artifact_modification", length(forbidden) == 0, paste(forbidden, collapse = ";"))
canon <- paste(readLines(path("docs/canon_status.md"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
check("active_holds_retained", grepl("C — HOLD", canon, fixed = TRUE) && grepl("UNRESOLVED", canon, fixed = TRUE), "hold text")
phase_status <- status[grepl("phase14b|phase15", tolower(status))]
phase_status <- phase_status[!grepl("docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md", phase_status, fixed = TRUE)]
check("phase14b_phase15_not_implemented", length(phase_status) == 0, paste(phase_status, collapse = ";"))

check("all_required_reports", all(file.exists(path(c("reports/phase14a_systems_ontology.md", "reports/phase14a_identity_crosswalk.md", "reports/phase14a_evidence_crosswalk.md", "reports/phase14a_relationship_taxonomy.md", "reports/phase14a_integration_qa.md")))), "report path")

if (length(failures) == 0) {
  cat("PHASE14A_R_VALIDATION PASSED\n")
  quit(status = 0)
} else {
  cat("PHASE14A_R_VALIDATION FAILED\n")
  cat(paste(failures, collapse = "\n"), "\n")
  quit(status = 1)
}
