#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 14A.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)
reports <- file.path(root, "reports")
final_name <- "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"
working_name <- "phase14a_manifest.json"
artifact_check_name <- "phase14a_artifact_check.json"
review_name <- "phase14a_independent_review.md"
source_commit <- "d89a80f6dd883f2cc9d89e3c89396e1b5f468700"
expected_prior_entries <- 488L
expected_prior_unique <- 479L
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
base_artifacts <- c(
  "metadata/atlas_systems.yml",
  "metadata/atlas_evidence_vocabulary.yml",
  "docs/phase_briefs/phase14_systems_atlas_integration.md",
  "docs/phase_briefs/phase14a_common_systems_ontology_identity_evidence_crosswalk.md",
  "docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md",
  "data/processed/integration/system_identity_crosswalk.csv",
  "data/processed/integration/external_endpoint_crosswalk.csv",
  "data/processed/integration/relationship_taxonomy_inventory.csv",
  "outputs/figures/western_basin_systems_architecture.png",
  "outputs/figures/western_basin_systems_architecture.svg",
  "reports/phase14a_systems_ontology.md",
  "reports/phase14a_identity_crosswalk.md",
  "reports/phase14a_evidence_crosswalk.md",
  "reports/phase14a_relationship_taxonomy.md",
  "reports/phase14a_integration_qa.md",
  "reports/phase14a_build_summary.json",
  "src/python/systems/build_phase14a_integration.py",
  "src/python/systems/validate_phase14a_integration.py",
  "src/R/systems/validate_phase14a_integration.R"
)
expected_working <- sort(base_artifacts)
expected_final <- c(expected_working, file.path("reports", artifact_check_name), file.path("reports", review_name), file.path("reports", working_name), "src/python/systems/validate_phase14a_freeze.py", "src/R/systems/validate_phase14a_freeze.R")
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
json_text <- function(file) paste(readLines(file, warn = FALSE, encoding = "UTF-8"), collapse = " ")
raw_bytes <- function(file) readBin(file, "raw", n = as.numeric(file.info(file)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix)
  on.exit(unlink(tmp), add = TRUE)
  writeBin(raw, tmp)
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    output <- system2(cmd, tmp, stdout = TRUE, stderr = TRUE)
    text <- paste(output, collapse = " ")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl = TRUE))[[1]]
    stop_if(length(hits) >= 1L, "sha256sum failed")
    return(tolower(hits[[1]]))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  output <- system2(certutil, c("-hashfile", tmp, "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output))
  hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, "certutil failed")
  hits[[1]]
}
portable_match <- function(file, expected, recorded = NA_real_) {
  stop_if(file.exists(file) && file.info(file)$size > 0, paste("missing artifact", file))
  raw <- raw_bytes(file)
  hashes <- c(sha256_raw(raw, tools::file_ext(file)))
  lengths <- c(length(raw))
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
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed = TRUE) & grepl("{", lines, fixed = TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", file))
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
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit) == 3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl = TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit) == 2L) { append_current(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh) == 2L && !is.na(current)) current_hash <- hh[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl = TRUE)
    bb <- regmatches(line, b)[[1]]
    if (length(bb) == 2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  append_current()
  data.frame(rel = rel, sha256 = hashes, bytes = bytes, stringsAsFactors = FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels = character()) {
  file <- file.path(reports, name)
  stop_if(file.exists(file), paste("missing manifest", name))
  x <- manifest_entries(file)
  stop_if(nrow(x) == expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(length(x$rel) == length(expected_rels) && setequal(as.character(x$rel), expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
require_terms <- function(relative, terms) {
  txt <- tolower(paste(readLines(file.path(root, relative), warn = FALSE, encoding = "UTF-8"), collapse = " "))
  for (term in terms) stop_if(grepl(tolower(term), txt, fixed = TRUE), paste("status", relative, term))
}

final_txt <- json_text(file.path(reports, final_name))
for (term in c(
  '"accepted_phase": "14A"',
  '"baseline": "Common Systems Ontology, Identity & Evidence Crosswalk"',
  '"status": "ACCEPTED / FROZEN"',
  '"accepted_by": "Sol explicit acceptance decision supplied for this run"',
  '"accepted_date": "2026-09-10"',
  paste0('"source_commit": "', source_commit, '"'),
  '"systems": 13', '"identity_rows": 456', '"endpoint_rows": 36',
  '"conceptual_dependency_rows": 25', '"relationship_rows": 367',
  '"evidence_classes": 8', '"evidence_mappings": 17',
  '"resolved_exact": 0', '"resolved_system_level": 34',
  '"retained_conceptual": 2', '"unresolved": 0',
  '"phase1_13_immutable": true', '"phase14b_implemented": false',
  '"phase15_implemented": false', '"release_created": false', '"tag_created": false',
  '"great_black_swamp": "C — HOLD / noncanonical"',
  '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"',
  '"Phase 6B manifest status wording mismatch"',
  '"Phase 3A missing manifest status"',
  '"Phase 2A superseded legacy worktree"'
)) stop_if(grepl(term, final_txt, fixed = TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(expected_final), expected_final)
stop_if(!any(final_x$rel == final_name), "final manifest self-list")

working_txt <- json_text(file.path(reports, working_name))
stop_if(grepl('"phase": "14A"', working_txt, fixed = TRUE), "working manifest phase")
stop_if(grepl('"status": "IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE"', working_txt, fixed = TRUE), "working manifest status")
for (term in c('"systems": 13', '"identity_rows": 456', '"endpoint_rows": 36', '"relationship_rows": 367', '"evidence_classes": 8', '"evidence_mappings": 17')) stop_if(grepl(term, working_txt, fixed = TRUE), paste("working manifest", term))
working_x <- verify_manifest(working_name, length(expected_working), expected_working)

check_txt <- tolower(json_text(file.path(reports, artifact_check_name)))
for (term in c('"passed": true', '"systems": 13', '"identity_rows": 456', '"endpoint_rows": 36', '"relationship_rows": 367', '"evidence_classes": 8', '"system_level_resolved": 34', '"retained_conceptual": 2', '"unresolved": 0')) stop_if(grepl(tolower(term), check_txt, fixed = TRUE), paste("artifact check", term))
review_txt <- tolower(json_text(file.path(reports, review_name)))
for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"ontology_errors": []', '"identity_errors": []', '"evidence_classification_errors": []', '"relationship_taxonomy_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(term, review_txt, fixed = TRUE), paste("review", term))

prior_entries <- 0L; protected <- character(); prior_manifests <- list.files(reports, pattern = "freeze_manifest[.]json$", full.names = TRUE)
prior_manifests <- prior_manifests[basename(prior_manifests) != final_name]
for (mf in sort(prior_manifests)) {
  x <- manifest_entries(mf)
  for (i in seq_len(nrow(x))) {
    prior_entries <- prior_entries + 1L; protected <- c(protected, x$rel[[i]])
    stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("prior hash", x$rel[[i]]))
  }
}
stop_if(prior_entries == expected_prior_entries && length(unique(protected)) == expected_prior_unique, paste("prior inventory", prior_entries, length(unique(protected))))
changed <- trimws(system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout = TRUE, stderr = TRUE))
stop_if(!any(changed == "metadata/systems.yml"), "metadata/systems.yml changed")
stop_if(!any(grepl("[.]gpkg$", changed)), "GeoPackage changed")
forbidden <- changed[(grepl("phase14b", tolower(changed)) & changed != "docs/phase_briefs/phase14b_atlas_layer_registry_cross_system_dependency_normalization.md") | grepl("phase15", tolower(changed))]
stop_if(length(forbidden) == 0L, paste("Phase 14B/15 changes", paste(forbidden, collapse = ",")))

status_terms <- c("phase 14a", "accepted / frozen", final_name, "active phase", "phase 14b", "approved scope / not implemented", "phase 15", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag")
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md", "README.md", "reports/README.md", "docs/agent_workflow.md", "CHANGELOG.md")) require_terms(relative, status_terms)

cat(sprintf("PHASE14A_R_FREEZE_VALIDATION PASSED; final artifacts=%d, working artifacts=%d, prior entries=%d, prior unique=%d, review=passed:true, Phase 14B/15 absent\n", nrow(final_x), nrow(working_x), prior_entries, length(unique(protected))))
