#!/usr/bin/env Rscript
# Independent base-R validation for the Phase 15A technology package.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)

failures <- character()
check <- function(name, condition, detail) {
  passed <- isTRUE(condition)
  if (!passed) failures <<- c(failures, paste0(name, ": ", detail))
  cat(if (passed) "PASS " else "FAIL ", name, " — ", detail, "\n", sep = "")
}
path <- function(rel) file.path(root, gsub("/", .Platform$file.sep, rel, fixed = TRUE))
read_csv_rel <- function(rel) read.csv(path(rel), stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
nonempty <- function(x) all(nzchar(as.character(x)))

node <- read_csv_rel("data/processed/analysis/technology_system_nodes.csv")
obs <- read_csv_rel("data/processed/analysis/technology_system_observations.csv")
src <- read_csv_rel("data/processed/analysis/technology_sources.csv")
unc <- read_csv_rel("data/processed/analysis/technology_uncertainties.csv")
int <- read_csv_rel("data/processed/integration/technology_system_interfaces.csv")
dep <- read_csv_rel("data/processed/integration/technology_dependencies.csv")
ontology_lines <- readLines(path("metadata/atlas_systems.yml"), warn = FALSE, encoding = "UTF-8")
system_ids <- sub("^  - system_id: ", "", ontology_lines[grepl("^  - system_id: SYS-", ontology_lines)])
allowed_families <- c("AI / ADVANCED COMPUTE / AUTOMATION", "ADVANCED SENSING / AUTONOMOUS SYSTEMS", "CYBERSECURITY / DIGITAL RESILIENCE", "ADVANCED ENERGY", "ADVANCED MATERIALS / MANUFACTURING", "QUANTUM TECHNOLOGIES", "BIOTECHNOLOGY / GENETIC ENGINEERING", "PRIVACY / SURVEILLANCE / DATA GOVERNANCE")
allowed_status <- c("established", "commercially emerging", "demonstration / pilot", "research-stage", "speculative / long-horizon")
allowed_relevance <- c("current", "emerging", "speculative")
allowed_evidence <- c("OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "UNRESOLVED", "NONCANONICAL_HOLD")
allowed_relationship <- c("physical flow", "material flow", "energy flow", "information / observation", "governance / authority", "operational dependency", "ecological relationship", "exposure pathway", "population / mobility interface", "surveillance / detection", "high-level association", "unresolved / unclassified")
allowed_dep <- c("electricity", "compute", "communications", "skilled workforce", "water", "materials", "supply chain", "data", "regulatory authority", "public trust / legitimacy", "physical infrastructure")
source_ids <- unique(src$source_id)
regional_sources <- unique(src$source_id[src$source_scope == "regional_system_context"])
node_ids <- unique(node$technology_id)

check("phase14_ontology_count", length(unique(system_ids)) == 13, as.character(length(unique(system_ids))))
check("technology_family_count", length(unique(node$technology_family)) == 8 && setequal(unique(node$technology_family), allowed_families), paste(length(unique(node$technology_family)), collapse = ","))
check("technology_ids_unique", length(node_ids) == nrow(node) && all(nzchar(node$technology_id)), as.character(nrow(node)))
check("technology_status_vocabulary", all(node$technology_status %in% allowed_status), paste(setdiff(unique(node$technology_status), allowed_status), collapse = ","))
check("regional_relevance_vocabulary", all(node$regional_relevance %in% allowed_relevance) && all(node$current_or_emerging %in% allowed_relevance), "relevance vocabulary")
check("node_sources_resolve", all(node$source_id %in% source_ids & node$regional_evidence_source_id %in% regional_sources), "node source membership")
check("source_registry_unique_and_grounded", length(source_ids) == nrow(src) && all(nzchar(src$url) & nzchar(src$retrieval_url) & nzchar(src$retrieval_date) & nzchar(src$evidence_use)), "source registry fields")
check("regional_deployment_not_claimed", all(tolower(src$regional_deployment_supported) == "no"), "regional deployment flag")
check("external_source_urls_https", all(src$source_type != "authoritative_government_or_institutional" | grepl("^https://", src$url)), "external URL scheme")

check("observation_ids_unique", length(unique(obs$observation_id)) == nrow(obs), as.character(nrow(obs)))
check("observation_technology_ids", all(obs$technology_id %in% node_ids), "observation technology IDs")
check("observation_sources", all(obs$source_id %in% source_ids & obs$regional_evidence_source_id %in% source_ids), "observation sources")
check("general_capability_not_local", all(!grepl("Western Basin|Toledo", obs$geographic_scope[obs$claim_scope == "general_capability"])), "general capability scope")
regional_obs <- obs$notes[obs$claim_scope == "regional_system_context"]
check("regional_context_not_deployment", all(grepl("not", tolower(regional_obs)) & grepl("deployment|inventory|capability", tolower(regional_obs))), "regional note boundary")
check("observation_evidence_vocabulary", all(obs$evidence_class %in% allowed_evidence), "observation evidence")

check("interface_ids_unique", length(unique(int$interface_id)) == nrow(int), as.character(nrow(int)))
check("interface_technology_ids", all(int$technology_id %in% node_ids), "interface technology IDs")
check("interface_target_system_ids", all(int$target_system_id %in% system_ids), "interface target IDs")
check("interface_source_system_blank", all(is.na(int$source_system_id) | !nzchar(int$source_system_id)), "technology source system promotion")
check("interface_relationship_vocabulary", all(int$normalized_relationship_class %in% allowed_relationship), "relationship vocabulary")
check("interface_evidence_and_sources", all(int$evidence_class %in% allowed_evidence & int$source_id %in% source_ids), "interface evidence/source")
check("interface_inferred", all(int$evidence_class == "INFERRED"), "interface evidence class")
check("interface_governance_and_uncertainty", all(nonempty(int$dependency_basis) & nonempty(int$governance_interface) & nonempty(int$uncertainty)), "interface fields")
check("interface_relevance_preserved", all(int$current_or_emerging %in% allowed_relevance & int$regional_relevance %in% allowed_relevance), "interface relevance")

check("dependency_ids_unique", length(unique(dep$dependency_id)) == nrow(dep), as.character(nrow(dep)))
check("dependency_technology_ids", all(dep$technology_id %in% node_ids), "dependency technology IDs")
check("dependency_classes", all(dep$dependency_class %in% allowed_dep) && all(dep$dependency_role %in% c("enabling", "limiting")), "dependency vocabulary")
check("dependency_system_ids", all(dep$affected_system_id %in% system_ids), "dependency affected systems")
check("dependency_sources_and_evidence", all(dep$source_id %in% source_ids & dep$evidence_class %in% allowed_evidence), "dependency sources/evidence")
check("dependency_boundaries", all(nonempty(dep$limitation) & nonempty(dep$governance_interface) & grepl("not", tolower(dep$notes))), "dependency limitations")
check("uncertainty_ids_unique", length(unique(unc$uncertainty_id)) == nrow(unc), as.character(nrow(unc)))
check("uncertainty_references", all(unc$technology_id %in% node_ids & unc$affected_system_id %in% system_ids & unc$source_id %in% source_ids & unc$regional_evidence_source_id %in% source_ids), "uncertainty references")
check("uncertainty_open", all(unc$uncertainty_status == "open") && all(nonempty(unc$uncertainty)), "uncertainty state")

ai <- node[node$technology_family == allowed_families[[1]], , drop = FALSE]
check("ai_decision_support_boundary", all(grepl("decision support|recommendation", tolower(ai$governance_interface))) && all(grepl("autonomous|production decision", tolower(ai$governance_interface))), "AI authority boundary")
sensing <- int[int$technology_family == allowed_families[[2]], , drop = FALSE]
check("sensing_not_enforcement", !any(grepl("enforcement", tolower(sensing$interface_type))) && all(grepl("measurement|observation|inspection", tolower(paste(sensing$interface_type, sensing$governance_interface)))), "sensing boundary")
cyber_text <- tolower(paste(c(node$technology_label[node$technology_family == allowed_families[[3]]], node$capability_scope[node$technology_family == allowed_families[[3]]], int$interface_type[int$technology_family == allowed_families[[3]]], dep$dependency_label[dep$technology_family == allowed_families[[3]]]), collapse = " "))
check("cyber_defensive_boundary", grepl("defensive", cyber_text) && grepl("resilience", cyber_text) && !grepl("offensive|exploit|malware|payload|attack procedure", cyber_text), "cyber positive fields")
quantum <- node[node$technology_family == allowed_families[[6]], , drop = FALSE]
check("quantum_conservative", all(quantum$technology_status == "research-stage" & quantum$current_or_emerging == "speculative" & quantum$regional_relevance == "speculative"), "quantum status")
fusion <- node[node$technology_id == "TECH-ENERGY-FUSION", , drop = FALSE]
check("fusion_not_current", nrow(fusion) == 1 && fusion$technology_status == "research-stage" && fusion$current_or_emerging == "speculative" && fusion$regional_relevance == "speculative" && grepl("no current", tolower(fusion$notes)), "fusion status")
biotech_text <- tolower(paste(c(node$technology_label[node$technology_family == allowed_families[[7]]], node$capability_scope[node$technology_family == allowed_families[[7]]], int$interface_type[int$technology_family == allowed_families[[7]]], dep$dependency_label[dep$technology_family == allowed_families[[7]]]), collapse = " "))
check("biotech_safe_positive_fields", !grepl("weaponization|pathogen optimization|harmful-agent enhancement|evasion tactic|wet-lab protocol", biotech_text), "biotechnology safety boundary")

bio_report <- paste(readLines(path("reports/phase15a_biosecurity_lens.md"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
bio_terms <- c("Detection", "Attribution uncertainty", "Laboratory/diagnostic capacity", "Biological monitoring", "Supply-chain resilience", "Dual-use governance", "public communication", "no pathogen engineering")
check("biosecurity_lens_topics", all(vapply(bio_terms, function(term) grepl(term, bio_report, fixed = TRUE), logical(1))), "biosecurity topics/boundary")
provenance_report <- paste(readLines(path("reports/phase15a_provenance_check.md"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
provenance_terms <- c(sprintf("[%d]", 1:17), "## Sources")
check("grounded_provenance_report", all(vapply(provenance_terms, function(term) grepl(term, provenance_report, fixed = TRUE), logical(1))), "ledger citations/source block")
working_manifest <- paste(readLines(path("reports/phase15a_manifest.json"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
check("working_manifest_identity", grepl('"phase": "15A"', working_manifest, fixed = TRUE) && grepl('"status": "generated_working_package"', working_manifest, fixed = TRUE) && grepl("d8247cf3419be6e0caf0b345f63644f2795c2ac6", working_manifest, fixed = TRUE), "working manifest identity")
svg_text <- paste(readLines(path("outputs/figures/technology_system_convergence_architecture_2026.svg"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
figure_terms <- c("Technology", "Established/current interface", "Emerging interface", "Speculative/long-horizon interface", "G = governance/data dependency", "not deployment", "not a geographic map")
check("figure_svg_qa", all(vapply(figure_terms, grepl, logical(1), x = svg_text, fixed = TRUE)), "figure labels")
png <- readBin(path("outputs/figures/technology_system_convergence_architecture_2026.png"), "raw", n = file.info(path("outputs/figures/technology_system_convergence_architecture_2026.png"))$size)
check("figure_png_qa", length(png) > 1000 && identical(as.integer(png[1:8]), c(137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L)), as.character(length(png)))

# Cross-platform, text-only portable hash verification for all prior final freeze manifests.
sha256_file <- function(file) {
  command <- Sys.which("sha256sum")
  if (nchar(command) > 0) {
    out <- system2(command, file, stdout = TRUE, stderr = TRUE)
    hit <- out[grepl("^[0-9A-Fa-f]{64}", out)]
    if (length(hit) > 0) return(tolower(substr(gsub("[^0-9A-Fa-f]", "", hit[[1]]), 1, 64)))
  }
  command <- Sys.which("certutil")
  if (nchar(command) == 0) return(NA_character_)
  out <- system2(command, c("-hashfile", file, "SHA256"), stdout = TRUE, stderr = TRUE)
  hit <- gsub("[[:space:]]+", "", out[grepl("^[0-9A-Fa-f]{64}$", gsub("[[:space:]]+", "", out))])
  if (length(hit) == 0) NA_character_ else tolower(hit[[1]])
}
portable_hash <- function(file) {
  raw <- readBin(file, "raw", n = file.info(file)$size)
  ext <- tolower(tools::file_ext(file))
  if (ext %in% c("csv", "json", "md", "py", "r", "yaml", "yml", "svg", "txt")) {
    canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))
    temporary <- tempfile(fileext = ".txt"); writeBin(canonical, temporary); on.exit(unlink(temporary), add = TRUE)
    return(sha256_file(temporary))
  }
  sha256_file(file)
}
manifest_hash_pairs <- function(file) {
  lines <- readLines(file, warn = FALSE, encoding = "UTF-8")
  current <- NA_character_; rows <- list()
  for (line in lines) {
    bare <- regmatches(line, regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"[[:space:]]*,?[[:space:]]*$', line, perl = TRUE))[[1]]
    if (length(bare) == 3 && grepl("/", bare[2], fixed = TRUE)) { rows[[length(rows)+1L]] <- c(path = bare[2], sha256 = bare[3]); current <- NA_character_; next }
    pm <- regmatches(line, regexec('^[[:space:]]+"([^"]+)"[[:space:]]*:', line, perl = TRUE))[[1]]
    if (length(pm) == 2 && grepl("/", pm[2], fixed = TRUE)) current <- pm[2]
    hm <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(hm) == 2 && !is.na(current)) { rows[[length(rows)+1L]] <- c(path = current, sha256 = hm[2]); current <- NA_character_ }
  }
  if (!length(rows)) return(data.frame(path = character(), sha256 = character(), stringsAsFactors = FALSE))
  do.call(rbind, lapply(rows, function(x) data.frame(path = unname(x[["path"]]), sha256 = unname(x[["sha256"]]), stringsAsFactors = FALSE)))
}
verify_manifest <- function(file) {
  pairs <- manifest_hash_pairs(file); bad <- character()
  if (nrow(pairs) > 0) for (i in seq_len(nrow(pairs))) {
    target <- path(pairs$path[[i]])
    if (!file.exists(target)) bad <- c(bad, pairs$path[[i]]) else {
      actual <- sha256_file(target); ok <- !is.na(actual) && actual == pairs$sha256[[i]]
      if (!ok && tolower(tools::file_ext(target)) %in% c("csv", "json", "md", "py", "r", "R", "svg", "txt", "yaml", "yml")) ok <- isTRUE(portable_hash(target) == pairs$sha256[[i]])
      if (!ok) bad <- c(bad, pairs$path[[i]])
    }
  }
  bad
}
freeze_files <- list.files(path("reports"), pattern = "freeze_manifest\\.json$", full.names = TRUE)
freeze_bad <- unlist(lapply(freeze_files, verify_manifest))
freeze_counts <- sum(vapply(freeze_files, function(x) nrow(manifest_hash_pairs(x)), integer(1)))
freeze_unique <- length(unique(unlist(lapply(freeze_files, function(x) manifest_hash_pairs(x)$path))))
check("prior_freeze_integrity", length(freeze_bad) == 0, paste(freeze_counts, freeze_unique, paste(head(freeze_bad, 5), collapse = ","), sep = " / "))

changed <- system2("git", c("-C", root, "diff", "--name-only", "d8247cf3419be6e0caf0b345f63644f2795c2ac6"), stdout = TRUE, stderr = TRUE)
changed <- gsub("\\\\", "/", changed)
check("no_frozen_paths_changed", length(intersect(changed, unique(unlist(lapply(freeze_files, function(x) manifest_hash_pairs(x)$path))))) == 0, paste(intersect(changed, unique(unlist(lapply(freeze_files, function(x) manifest_hash_pairs(x)$path)))), collapse = ","))
check("no_future_data_or_maps", !any(grepl("scenario|future", changed[grepl("^(data|outputs)/", changed)], ignore.case = TRUE)), paste(changed[grepl("scenario|future", changed, ignore.case = TRUE)], collapse = ","))
check("phase15b_brief_only", !any(grepl("phase15b", changed, ignore.case = TRUE) & !grepl("^docs/phase_briefs/", changed)), paste(changed[grepl("phase15b", changed, ignore.case = TRUE)], collapse = ","))
status_text <- paste(readLines(path("PROJECT_STATUS.md"), warn = FALSE, encoding = "UTF-8"), readLines(path("docs/canon_status.md"), warn = FALSE, encoding = "UTF-8"), readLines(path("reports/current_phase_handoff.md"), warn = FALSE, encoding = "UTF-8"), collapse = "\n")
check("active_holds_retained", grepl("C — HOLD / noncanonical", status_text, fixed = TRUE) && grepl("UNRESOLVED", status_text, fixed = TRUE), "hold text")
check("phase14_complete_status", grepl("Phase 14 is **COMPLETE / ACCEPTED / FROZEN**", status_text, fixed = TRUE), "Phase 14 status")
check("phase15b_phase16_boundary", grepl("APPROVED SCOPE / NOT IMPLEMENTED", paste(readLines(path("docs/phase_briefs/phase15b_technology_convergence_futures.md"), warn = FALSE, encoding = "UTF-8"), collapse = "\n"), fixed = TRUE) && grepl("Phase 16", status_text, fixed = TRUE), "future boundary")
check("no_release_or_tag", grepl("No release or tag", status_text, fixed = TRUE), "release/tag boundary")

result_lines <- c("{", '  "phase": "15A",', sprintf('  "passed": %s,', tolower(as.character(length(failures) == 0))), sprintf('  "failure_count": %d,', length(failures)), sprintf('  "failures": [%s]', paste(sprintf('"%s"', gsub('"', '\\\\"', failures, fixed = TRUE)), collapse = ",")), "}")
writeLines(result_lines, path("reports/phase15a_r_validation_result.json"), useBytes = TRUE)
if (length(failures) == 0) { cat("PHASE15A_R_VALIDATION PASSED\n"); quit(status = 0) }
cat("PHASE15A_R_VALIDATION FAILED\n", paste(failures, collapse = "\n"), "\n", sep = ""); quit(status = 1)
