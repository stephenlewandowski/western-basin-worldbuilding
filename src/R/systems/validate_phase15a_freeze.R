#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 15A.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)
reports <- file.path(root, "reports")
final_name <- "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"
working_name <- "phase15a_manifest.json"
artifact_check_name <- "phase15a_artifact_check.json"
r_result_name <- "phase15a_r_validation_result.json"
review_name <- "phase15a_independent_review.md"
initial_name <- "phase15a_independent_review_initial.md"
second_name <- "phase15a_independent_review_second_failed.md"
third_name <- "phase15a_independent_review_third_failed.md"
prior_pass_name <- "phase15a_independent_review_prior_pass.md"
a14a_name <- "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
a14b_name <- "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"
source_commit <- "87e877dc33372195a549cab5654fd6b6e6de64e9"
expected_prior_entries <- 535L
expected_prior_unique <- 526L
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
working_artifacts <- c(
  "data/processed/analysis/technology_sources.csv",
  "data/processed/analysis/technology_system_nodes.csv",
  "data/processed/analysis/technology_system_observations.csv",
  "data/processed/analysis/technology_uncertainties.csv",
  "data/processed/integration/technology_dependencies.csv",
  "data/processed/integration/technology_system_interfaces.csv",
  "docs/phase_briefs/phase15_technology_strategic_systems_convergence.md",
  "docs/phase_briefs/phase15a_technology_strategic_systems_baseline_2026.md",
  "docs/phase_briefs/phase15b_technology_convergence_futures.md",
  "metadata/technology_vocabulary.yml",
  "outputs/figures/technology_system_convergence_architecture_2026.png",
  "outputs/figures/technology_system_convergence_architecture_2026.svg",
  file.path("reports", artifact_check_name),
  "reports/phase15a_biosecurity_lens.md",
  file.path("reports", review_name),
  file.path("reports", initial_name),
  file.path("reports", prior_pass_name),
  file.path("reports", second_name),
  file.path("reports", third_name),
  "reports/phase15a_provenance_check.md",
  file.path("reports", r_result_name),
  "reports/phase15a_technology_interfaces.md",
  "reports/phase15a_technology_qa.md",
  "reports/phase15a_technology_systems_baseline.md",
  "src/R/systems/validate_phase15a_technology.R",
  "src/python/systems/build_phase15a_technology.py",
  "src/python/systems/validate_phase15a_technology.py"
)
final_artifacts <- sort(c(file.path("reports", working_name), working_artifacts, "src/R/systems/validate_phase15a_freeze.R", "src/python/systems/validate_phase15a_freeze.py"))
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
  output <- system2(command, c("-hashfile", tmp, "SHA256"), stdout = TRUE, stderr = TRUE)
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
  raw <- raw_bytes(file); lengths <- c(length(raw)); raw_hash <- sha256_file_cached(file)
  if (tolower(expected) == tolower(raw_hash) && (is.na(recorded) || as.numeric(recorded) == length(raw))) return(TRUE)
  hashes <- c(raw_hash)
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
  if (length(expected_rels)) stop_if(identical(sort(as.character(x$rel)), sort(expected_rels)), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
require_terms <- function(relative, terms) { txt <- tolower(text_rel(relative)); for (term in terms) stop_if(grepl(tolower(term), txt, fixed = TRUE), paste(relative, term)) }

final_text <- text_rel(file.path("reports", final_name))
for (term in c(
  '"accepted_phase": "15A"', '"baseline": "Technology & Strategic-Systems Baseline and Interfaces, 2026"', '"status": "ACCEPTED / FROZEN"',
  paste0('"source_commit": "', source_commit, '"'), '"technology_families": 8', '"technology_records": 18', '"observations": 21',
  '"interfaces": 44', '"dependencies": 32', '"uncertainties": 8', '"sources": 33', '"dependency_classes": 11',
  '"phase14_system_coverage": 13', '"interfaces_are_inferred": true', '"no_new_phase14_ontology_members": true',
  '"qualitative_dependencies_only": true', '"release_created": false', '"tag_created": false',
  '"phase15b_status": "APPROVED SCOPE / NOT IMPLEMENTED"', '"phase16_status": "NOT IMPLEMENTED"',
  '"great_black_swamp": "C — HOLD / noncanonical"', '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"',
  '"Phase 6B manifest status wording mismatch"', '"Phase 3A missing manifest status"', '"Phase 2A superseded legacy worktree"'
)) stop_if(grepl(term, final_text, fixed = TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(final_artifacts), final_artifacts)
working_text <- text_rel(file.path("reports", working_name)); require_terms(file.path("reports", working_name), c('"phase": "15A"', '"status": "generated_working_package"'))
working_x <- verify_manifest(working_name, length(working_artifacts), sort(working_artifacts))
check_text <- tolower(text_rel(file.path("reports", artifact_check_name)))
for (term in c('"phase": "15A"', '"passed": true', '"errors": []', '"technology_families": 8', '"technology_nodes": 18', '"interfaces": 44', '"dependencies": 32', '"prior_freeze_entries": 535', '"prior_freeze_unique_paths": 526')) stop_if(grepl(tolower(term), check_text, fixed = TRUE), paste("artifact check", term))
r_text <- text_rel(file.path("reports", r_result_name)); for (term in c('"phase": "15A"', '"passed": true', '"failure_count": 0', '"failures": []')) stop_if(grepl(term, r_text, fixed = TRUE), paste("R result", term))

source <- read_csv_rel("data/processed/analysis/technology_sources.csv")
node <- read_csv_rel("data/processed/analysis/technology_system_nodes.csv")
obs <- read_csv_rel("data/processed/analysis/technology_system_observations.csv")
unc <- read_csv_rel("data/processed/analysis/technology_uncertainties.csv")
int <- read_csv_rel("data/processed/integration/technology_system_interfaces.csv")
dep <- read_csv_rel("data/processed/integration/technology_dependencies.csv")
allowed_families <- c("AI / ADVANCED COMPUTE / AUTOMATION", "ADVANCED SENSING / AUTONOMOUS SYSTEMS", "CYBERSECURITY / DIGITAL RESILIENCE", "ADVANCED ENERGY", "ADVANCED MATERIALS / MANUFACTURING", "QUANTUM TECHNOLOGIES", "BIOTECHNOLOGY / GENETIC ENGINEERING", "PRIVACY / SURVEILLANCE / DATA GOVERNANCE")
allowed_status <- c("established", "commercially emerging", "demonstration / pilot", "research-stage", "speculative / long-horizon")
allowed_rel <- c("current", "emerging", "speculative")
stop_if(nrow(source) == 33L && length(unique(source$source_id)) == 33L && all(nzchar(source$url) & nzchar(source$retrieval_url) & nzchar(source$retrieval_date)), "source registry")
stop_if(nrow(node) == 18L && length(unique(node$technology_id)) == 18L && setequal(unique(node$technology_family), allowed_families), "technology families/records")
stop_if(all(node$technology_status %in% allowed_status) && all(node$current_or_emerging %in% allowed_rel) && all(node$regional_relevance %in% allowed_rel), "technology vocabularies")
stop_if(identical(as.integer(table(node$technology_status)[c("established", "commercially emerging", "demonstration / pilot", "research-stage")]), c(5L, 7L, 3L, 3L)), "maturity counts")
stop_if(identical(as.integer(table(node$current_or_emerging)[c("current", "emerging", "speculative")]), c(3L, 12L, 3L)), "current/emerging/speculative counts")
stop_if(identical(as.integer(table(node$regional_relevance)[c("current", "emerging", "speculative")]), c(3L, 9L, 6L)), "node regional relevance counts")
node_ids <- unique(node$technology_id); system_lines <- readLines(path("metadata/atlas_systems.yml"), warn = FALSE, encoding = "UTF-8"); system_ids <- sub("^  - system_id: ", "", system_lines[grepl("^  - system_id: SYS-", system_lines)])
stop_if(nrow(obs) == 21L && length(unique(obs$observation_id)) == 21L && all(obs$technology_id %in% node_ids), "observations")
stop_if(nrow(unc) == 8L && all(unc$technology_id %in% node_ids & unc$affected_system_id %in% system_ids & unc$uncertainty_status == "open"), "uncertainties")
stop_if(nrow(int) == 44L && length(unique(int$interface_id)) == 44L && all(int$technology_id %in% node_ids) && setequal(unique(int$target_system_id), system_ids) && all(int$evidence_class == "INFERRED"), "interfaces/system coverage")
stop_if(identical(as.integer(table(int$regional_relevance)[c("current", "emerging", "speculative")]), c(12L, 23L, 9L)), "interface regional relevance counts")
stop_if(nrow(dep) == 32L && length(unique(dep$dependency_id)) == 32L && length(unique(dep$dependency_class)) == 11L && all(dep$technology_id %in% node_ids & dep$affected_system_id %in% system_ids), "dependencies/classes")
all_fields <- tolower(c(names(source), names(node), names(int), names(dep))); stop_if(!any(grepl("score|probability|capacity_score|performance_score|resilience_score", all_fields)), "score-like fields")

bio <- text_rel("reports/phase15a_biosecurity_lens.md")
for (term in c("Detection", "Attribution uncertainty", "Laboratory/diagnostic capacity", "Biological monitoring", "Supply-chain resilience", "Food/agricultural resilience", "Dual-use governance", "coordination", "public communication", "response capacity", "no pathogen engineering")) stop_if(grepl(tolower(term), tolower(bio), fixed = TRUE), paste("biosecurity", term))
prov <- text_rel("reports/phase15a_provenance_check.md"); for (term in c(sprintf("[%d]", 1:17), "## Sources")) stop_if(grepl(term, prov, fixed = TRUE), paste("provenance", term))
svg <- text_rel("outputs/figures/technology_system_convergence_architecture_2026.svg"); for (term in c("Technology", "Established/current interface", "Emerging interface", "Speculative/long-horizon interface", "G = governance/data dependency", "not deployment", "not a geographic map")) stop_if(grepl(term, svg, fixed = TRUE), paste("figure", term))
png <- raw_bytes(path("outputs/figures/technology_system_convergence_architecture_2026.png")); stop_if(length(png) > 1000L && identical(as.integer(png[1:8]), c(137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L)), "figure PNG")

review <- tolower(text_rel(file.path("reports", review_name))); for (term in c("deleg_486838c1", '"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"technology_maturity_errors": []', '"regional_relevance_errors": []', '"ontology_interface_errors": []', '"governance_boundary_errors": []', '"biosecurity_boundary_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(tolower(term), review, fixed = TRUE), paste("final review", term))
for (pair in list(c(initial_name, "deleg_ae5f3c71"), c(second_name, "deleg_6cca1617"), c(third_name, "deleg_16255f91"), c(prior_pass_name, "deleg_4cd21ddf"))) stop_if(grepl(pair[[2]], text_rel(file.path("reports", pair[[1]])), fixed = TRUE), paste("review lineage", pair[[2]]))

# Verify the accepted Phase 14 freeze manifests before checking the complete prior inventory.
a14a <- text_rel(file.path("reports", a14a_name)); a14b <- text_rel(file.path("reports", a14b_name)); stop_if(grepl('"accepted_phase": "14A"', a14a, fixed = TRUE) && grepl('"status": "ACCEPTED / FROZEN"', a14a, fixed = TRUE), "Phase 14A status"); stop_if(grepl('"accepted_phase": "14B"', a14b, fixed = TRUE) && grepl('"status": "ACCEPTED / FROZEN"', a14b, fixed = TRUE), "Phase 14B status")
invisible(verify_manifest(a14a_name, 24L)); invisible(verify_manifest(a14b_name, 23L))
freeze_files <- list.files(reports, pattern = "freeze_manifest\\.json$", full.names = TRUE); freeze_files <- freeze_files[basename(freeze_files) != final_name]
prior_entries <- 0L; protected <- character()
for (mf in sort(freeze_files)) { x <- manifest_entries(mf); prior_entries <- prior_entries + nrow(x); protected <- c(protected, x$rel); for (i in seq_len(nrow(x))) stop_if(portable_match(path(x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", x$rel[[i]])) }
stop_if(prior_entries == expected_prior_entries && length(unique(protected)) == expected_prior_unique, paste("prior inventory", prior_entries, length(unique(protected))))
changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE); changed <- gsub("\\\\", "/", changed)
stop_if(length(intersect(changed, unique(protected))) == 0L, paste("prior protected artifact changed", paste(intersect(changed, unique(protected)), collapse = ",")))
stop_if(!any(changed == "metadata/atlas_systems.yml") && !any(changed == "metadata/atlas_layers.yml"), "Phase 14 registry changed")
stop_if(!any(grepl("phase16", changed, ignore.case = TRUE) & !grepl("^docs/phase_briefs/", changed)), "Phase 16 implementation")
stop_if(!any(grepl("phase15b", changed, ignore.case = TRUE) & !grepl("^docs/phase_briefs/", changed)), "Phase 15B implementation")
stop_if(!any(grepl("scenario|future", changed[grepl("^(data|outputs)/", changed)], ignore.case = TRUE)), "future data/map implementation")
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")) require_terms(relative, c("phase 15a", "accepted / frozen", final_name, "phase 15b", "approved scope / not implemented", "phase 16", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "no release or tag"))
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md")) require_terms(relative, c("phase 14", "complete"))
cat(sprintf("PHASE15A_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, prior entries=%d, prior unique=%d, systems=%d, interfaces=44, dependencies=32, review=deleg_486838c1 passed:true, Phase 14 complete, Phase 15B/16 absent\n", nrow(final_x), nrow(working_x), prior_entries, length(unique(protected)), length(unique(system_ids))))
