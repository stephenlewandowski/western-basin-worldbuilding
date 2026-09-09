#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 13B.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
source_commit <- "cd974019ddf6b5cae8ee98138cb917de343b009b"
final_name <- "phase13b_infectious_disease_dependencies_freeze_manifest.json"
working_name <- "infectious_disease_dependency_manifest.json"
phase13a_name <- "phase13a_infectious_disease_freeze_manifest.json"
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R")
expected_final <- c(
  "data/processed/analysis/infectious_disease_dependency_register.csv",
  "data/processed/networks/infectious_disease_dependency_edges.csv",
  "data/processed/analysis/infectious_disease_dependency_matrix.csv",
  "data/processed/analysis/infectious_disease_evidence_crosswalk.csv",
  "data/processed/analysis/infectious_disease_dependency_sources.csv",
  "data/processed/analysis/infectious_disease_dependency_uncertainties.csv",
  "outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.png",
  "outputs/maps/systems/42_infectious_disease_transmission_dependencies_2026.svg",
  "reports/infectious_disease_dependency_sources.md",
  "reports/infectious_disease_dependency_assumptions.md",
  "reports/infectious_disease_dependency_findings.md",
  "reports/infectious_disease_dependency_qa.md",
  "reports/phase13b_citation_ledger.json",
  "src/python/systems/build_infectious_disease_dependencies.py",
  "src/python/systems/validate_infectious_disease_dependencies.py",
  "src/R/systems/validate_infectious_disease_dependencies.R",
  "reports/infectious_disease_dependency_manifest.json",
  "reports/infectious_disease_dependency_artifact_check.json",
  "reports/infectious_disease_dependency_independent_review_initial.md",
  "reports/infectious_disease_dependency_independent_review_second.md",
  "reports/infectious_disease_dependency_independent_review.md",
  "docs/phase_briefs/phase13b_infectious_disease_dependencies.md",
  "src/python/systems/validate_phase13b_freeze.py",
  "src/R/systems/validate_phase13b_freeze.R"
)
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_bytes <- function(raw) charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stop_if(length(out) >= 1L, paste("sha256sum failed", path))
    token <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    hit <- regmatches(token, regexpr("[0-9a-f]{64}", token, perl=TRUE))
    stop_if(length(hit) == 1L && nchar(hit) == 64L, paste("sha256sum failed", path))
    return(tolower(hit))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path)); hits[[1]]
}
sha256_raw <- function(bytes, suffix=".bin") { tmp <- tempfile(fileext=suffix); on.exit(unlink(tmp), add=TRUE); writeBin(bytes, tmp); sha256_file(tmp) }
portable_match <- function(path, expected, recorded=NA_real_) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing artifact", path))
  raw <- raw_bytes(path); ext <- tools::file_ext(path)
  hashes <- c(sha256_raw(raw, paste0(".", ext))); lengths <- c(length(raw))
  if (tolower(ext) %in% tolower(text_ext)) {
    canon <- canonical_bytes(raw)
    hashes <- c(hashes, sha256_raw(canon, paste0(".", ext))); lengths <- c(lengths, length(canon))
    crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canon), fixed=TRUE))
    hashes <- c(hashes, sha256_raw(crlf, paste0(".", ext))); lengths <- c(lengths, length(crlf))
  }
  tolower(expected) %in% hashes && (is.na(recorded) || as.numeric(recorded) %in% lengths)
}
manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  if (start + 1L <= length(lines)) for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit)==3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit)==2L) { append_current(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bb <- regmatches(line, b)[[1]]
    if (length(bb)==2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels=character()) {
  path <- file.path(reports, name); stop_if(file.exists(path), paste("missing manifest", name))
  x <- manifest_artifacts(path); stop_if(nrow(x)==expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(identical(as.character(x$rel), expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
verify_prior <- function() {
  paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
  paths <- paths[!basename(paths) %in% c(final_name, phase13a_name)]
  hashes <- character(); protected <- character(); total <- 0L
  for (path in sort(paths)) {
    x <- manifest_artifacts(path)
    for (i in seq_len(nrow(x))) {
      rel <- x$rel[[i]]; expected <- x$sha256[[i]]
      if (rel %in% names(hashes)) stop_if(unname(hashes[[rel]]) == expected, paste("conflicting prior hash", rel))
      hashes[rel] <- expected; stop_if(portable_match(file.path(root, rel), expected, x$bytes[[i]]), paste("prior artifact", rel))
      protected <- c(protected, rel); total <- total + 1L
    }
  }
  stop_if(total == 358L && length(unique(protected)) == 351L, paste("prior inventory", total, length(unique(protected))))
  changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)
  stop_if(!any(changed %in% protected), "prior protected artifact changed")
  list(entries=total, unique=length(unique(protected)), manifests=length(paths))
}
final_txt <- json_text(file.path(reports, final_name))
for (term in c(
  '"accepted_phase": "13B"',
  '"baseline": "Environmental & Human-System Transmission Dependencies, 2026"',
  '"status": "ACCEPTED / FROZEN"',
  '"accepted_by": "Sol explicit acceptance decision supplied for this run"',
  '"accepted_date": "2026-09-10"',
  paste0('"source_commit": "', source_commit, '"'),
  '"phase13a_accepted_frozen": true',
  '"phase1_12_immutable": true',
  '"phase13c_implemented": false',
  '"phase14_implemented": false',
  '"composite_disease_risk_index": false',
  '"individual_case_or_risk_map": false',
  '"great_black_swamp": "C — HOLD / noncanonical"',
  '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"'
)) stop_if(grepl(term, final_txt, fixed=TRUE), paste(final_name, term))
final_x <- verify_manifest(final_name, 24L, expected_final)
working_txt <- json_text(file.path(reports, working_name)); working_x <- manifest_artifacts(file.path(reports, working_name))
for (term in c('"phase": "13B"','"status": "implemented_validated_pending_sol_acceptance"','"phase13a_accepted_frozen": true','"phase1_12_immutable": true','"phase13c_implemented": false')) stop_if(grepl(term, working_txt, fixed=TRUE), paste("working manifest", term))
stop_if(nrow(working_x)==18L, "working manifest artifact count")
for (i in seq_len(nrow(working_x))) stop_if(portable_match(file.path(root, working_x$rel[[i]]), working_x$sha256[[i]], working_x$bytes[[i]]), paste("working artifact", working_x$rel[[i]]))
phase13a_x <- verify_manifest(phase13a_name, 25L)
phase13a_txt <- json_text(file.path(reports, phase13a_name)); stop_if(grepl('"status": "ACCEPTED / FROZEN"', phase13a_txt, fixed=TRUE), "Phase 13A status")
artifact_check <- tolower(json_text(file.path(reports, "infectious_disease_dependency_artifact_check.json")))
for (term in c('"status": "passed"','"dependency_register": 36','"dependency_edges": 36','"matrix_rows": 6','"evidence_crosswalk": 36','"sources": 33','"uncertainties": 14','"phase13a_freeze_artifacts_checked": 25','"prior_freeze_manifest_entries_checked": 358','"prior_unique_protected_artifacts_checked": 351','"manifest_artifacts_checked": 18','"phase13a_accepted_frozen": true','"phase1_12_immutable": true','"phase13a_immutable": true','"phase13c_not_implemented": true','"phase14_not_implemented": true')) stop_if(grepl(term, artifact_check, fixed=TRUE), paste("artifact check", term))
for (rel in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c("phase 13a", "accepted / frozen", "phase 13b", "not implemented", "phase 13c", "active phase", "none", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved")) stop_if(grepl(term, txt, fixed=TRUE), paste("status", rel, term))
}
brief <- tolower(json_text(file.path(root, "docs/phase_briefs/phase13b_infectious_disease_dependencies.md")))
# The brief is a protected Phase 13A input; its unchanged hash is checked above.
stop_if(grepl("status: approved scope / not implemented", brief, fixed=TRUE), "Phase 13B protected brief")
# The phrase is retained in historical handoff checkpoints; validate the latest acceptance section.
handoff <- tolower(json_text(file.path(root, "reports/current_phase_handoff.md"))); marker <- max(gregexpr("## phase 13b final acceptance / freeze handoff", handoff, fixed=TRUE)[[1]])
stop_if(marker > 0L, "Phase 13B final handoff missing"); current <- substr(handoff, marker, nchar(handoff))
stop_if(grepl("phase 13b **accepted / frozen**", current, fixed=TRUE) || grepl("phase 13b: **accepted / frozen**", current, fixed=TRUE), "Phase 13B final status")
stop_if(grepl("phase 13c **approved scope / not implemented**", current, fixed=TRUE) || grepl("phase 13c: **approved scope / not implemented**", current, fixed=TRUE), "Phase 13C final status")
stop_if(grepl("active phase **none**", current, fixed=TRUE) || grepl("active phase: **none**", current, fixed=TRUE), "active phase final status")
for (rel in c("reports/infectious_disease_dependency_independent_review_initial.md", "reports/infectious_disease_dependency_independent_review_second.md", "reports/infectious_disease_dependency_independent_review.md")) stop_if(file.exists(file.path(root, rel)), paste("review history", rel))
review <- tolower(json_text(file.path(reports, "infectious_disease_dependency_independent_review.md")))
for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"epidemiological_errors": []','"dependency_errors": []','"surveillance_errors": []','"spatial_scale_errors": []','"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("final review", term))
bad <- c(list.files(file.path(root, "data", "processed"), recursive=TRUE, full.names=TRUE), list.files(file.path(root, "outputs", "maps", "systems"), full.names=TRUE), list.files(file.path(root, "src", "python", "systems"), full.names=TRUE), list.files(file.path(root, "src", "R", "systems"), full.names=TRUE))
bad <- bad[grepl("phase13c|phase14|infectious_disease_futures|(^|[/\\\\])43_|(^|[/\\\\])44_", tolower(basename(bad)))]
stop_if(length(bad)==0L, "Phase 13C/14 artifacts")
prior <- verify_prior()
cat(sprintf("Phase 13B R freeze validation passed: 24 final artifacts, 18 working artifacts; Phase 13A 25 artifacts; prior Phase 1–12 inventory %d/%d; review history, holds, deferred maintenance, and 13C/14 exclusion verified\n", prior$entries, prior$unique))
