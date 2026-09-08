#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 12C.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stop_if(length(out) >= 1L, paste("sha256sum failed", path))
    return(tolower(gsub("[^0-9a-f]", "", strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1])))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path)); hits[[1]]
}
portable_match <- function(path, expected) {
  if (sha256_file(path) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  tolower(expected) %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp))
}
manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); current <- NA_character_; current_hash <- NA_character_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash) }
    current <<- NA_character_; current_hash <<- NA_character_
  }
  if (start + 1L <= length(lines)) for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit)==3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit)==2L) { append_current(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, stringsAsFactors=FALSE)
}
check_manifest <- function(path, expected_n, phase, baseline) {
  stop_if(file.exists(path), paste("missing freeze manifest", path))
  txt <- json_text(path)
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("status", path))
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl=TRUE), paste("phase", path))
  stop_if(grepl(baseline, txt, fixed=TRUE), paste("baseline", path))
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == expected_n, paste("freeze artifact count", path))
  for (i in seq_len(nrow(x))) {
    artifact <- file.path(root, x$rel[[i]])
    stop_if(file.exists(artifact) && portable_match(artifact, x$sha256[[i]]), paste("freeze hash", x$rel[[i]]))
  }
  nrow(x)
}

A <- file.path(reports, "phase12a_vector_ecology_freeze_manifest.json")
B <- file.path(reports, "phase12b_vector_environment_human_dependencies_freeze_manifest.json")
C <- file.path(reports, "phase12c_vector_ecology_futures_freeze_manifest.json")
W <- file.path(reports, "vector_ecology_future_manifest.json")
K <- file.path(reports, "vector_ecology_future_artifact_check.json")
stop_if(check_manifest(A, 17L, "12A", "Vector Ecology Baseline, 2026") == 17L, "Phase 12A")
stop_if(check_manifest(B, 15L, "12B", "Vector / Environment / Human-System Dependencies, 2026") == 15L, "Phase 12B")
stop_if(check_manifest(C, 28L, "12C", "Vector Ecology Futures, 2050 / 2075") == 28L, "Phase 12C")

working_text <- json_text(W)
stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', working_text, perl=TRUE), "working manifest status")
working_artifacts <- manifest_artifacts(W)
stop_if(nrow(working_artifacts) == 25L, "working manifest artifact count")
for (i in seq_len(nrow(working_artifacts))) stop_if(portable_match(file.path(root, working_artifacts$rel[[i]]), working_artifacts$sha256[[i]]), paste("working hash", working_artifacts$rel[[i]]))

check_text <- json_text(K)
for (term in c('"status": "passed"', '"scenario_assumptions": 36', '"vector_states": 36', '"habitat_states": 48', '"surveillance_states": 30', '"dependency_states": 168', '"uncertainty_states": 60', '"scenario_sources": 28', '"comparison_rows": 6', '"prior_phase1_11_manifest_entries": 298', '"prior_phase1_11_unique_protected_artifacts": 293', '"phase12a_12b_freeze_integrity": true', '"phase12a_12b_immutable": true', '"active_holds_preserved": true', '"independent_review_passed": true')) stop_if(grepl(term, check_text, fixed=TRUE), paste("artifact check", term))

final_text <- json_text(C)
for (term in c('"phase12a_12b_immutable": true', '"phase1_11_immutable": true', '"phase13_implemented": false', 'reports/phase12a_vector_ecology_freeze_manifest.json', 'reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json', 'reports/vector_ecology_future_manifest.json', '"great_black_swamp": "C — HOLD / noncanonical"', '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"')) stop_if(grepl(term, final_text, fixed=TRUE), paste("final boundary", term))

review_text <- tolower(json_text(file.path(reports, "vector_ecology_future_independent_review.md")))
for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"ecological_errors": []', '"scenario_boundary_errors": []', '"spatial_scale_errors": []', '"health_boundary_errors": []')) stop_if(grepl(term, review_text, fixed=TRUE), paste("review", term))
stop_if(file.exists(file.path(reports, "vector_ecology_future_independent_review_initial.md")), "initial review preserved")

prior_files <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
prior_files <- prior_files[!grepl("^phase12", basename(prior_files))]
protected <- character(); expected_hashes <- character(); prior_entries <- 0L
for (path in sort(prior_files)) {
  x <- manifest_artifacts(path)
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; expected_hash <- x$sha256[[i]]
    if (rel %in% names(expected_hashes)) stop_if(expected_hashes[[rel]] == expected_hash, paste("prior duplicate hash", rel))
    expected_hashes[rel] <- expected_hash
    stop_if(file.exists(file.path(root, rel)) && portable_match(file.path(root, rel), expected_hash), paste("prior hash", rel))
    protected <- c(protected, rel); prior_entries <- prior_entries + 1L
  }
}
stop_if(prior_entries == 298L && length(unique(protected)) == 293L, paste("prior inventory", prior_entries, length(unique(protected))))

cat('{\n  "status": "passed",\n  "phase": "12C",\n  "freeze_manifest": "reports/phase12c_vector_ecology_futures_freeze_manifest.json",\n  "freeze_artifacts": 28,\n  "working_manifest_artifacts": 25,\n  "phase12a_artifacts": 17,\n  "phase12b_artifacts": 15,\n  "prior_phase1_11_manifest_entries": 298,\n  "prior_phase1_11_unique_protected_artifacts": 293,\n  "phase12a_12b_immutable": true,\n  "review_passed_blocking_arrays_empty": true,\n  "active_holds_preserved": true,\n  "phase13_implemented": false\n}\n')
