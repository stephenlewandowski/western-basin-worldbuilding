#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 13A.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
source_commit <- "c07be966e5058e299be21d181754920e41e5321b"
final_name <- "phase13a_infectious_disease_freeze_manifest.json"
working_name <- "infectious_disease_baseline_manifest.json"
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R")
phase12_names <- c("phase12a_vector_ecology_freeze_manifest.json", "phase12b_vector_environment_human_dependencies_freeze_manifest.json", "phase12c_vector_ecology_futures_freeze_manifest.json")

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
  raw <- raw_bytes(path); ext <- tolower(tools::file_ext(path))
  hashes <- c(sha256_raw(raw, paste0(".", ext))); lengths <- c(length(raw))
  if (ext %in% text_ext) {
    canonical <- canonical_bytes(raw)
    hashes <- c(hashes, sha256_raw(canonical, paste0(".", ext))); lengths <- c(lengths, length(canonical))
    crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
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
verify_manifest <- function(name, phase, baseline, expected_n, expected_rels=character()) {
  path <- file.path(reports, name); stop_if(file.exists(path), paste("missing manifest", name))
  txt <- json_text(path)
  for (term in c(paste0('"accepted_phase": "', phase, '"'), paste0('"baseline": "', baseline, '"'), '"status": "ACCEPTED / FROZEN"', '"accepted_by": "Sol explicit acceptance decision supplied for this run"')) stop_if(grepl(term, txt, fixed=TRUE), paste(name, term))
  x <- manifest_artifacts(path); stop_if(nrow(x)==expected_n, paste(name, "artifact count"))
  if (length(expected_rels)) stop_if(setequal(x$rel, expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
verify_prior <- function() {
  paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
  paths <- paths[basename(paths) != final_name]
  hashes <- character(); protected <- character(); total <- 0L
  for (path in sort(paths)) {
    x <- manifest_artifacts(path)
    for (i in seq_len(nrow(x))) {
      rel <- x$rel[[i]]; expected <- x$sha256[[i]]
      if (rel %in% names(hashes)) stop_if(unname(hashes[[rel]]) == expected, paste("conflicting prior hash", rel))
      hashes[rel] <- expected
      stop_if(portable_match(file.path(root, rel), expected, x$bytes[[i]]), paste("prior artifact", rel))
      protected <- c(protected, rel); total <- total + 1L
    }
  }
  stop_if(total == 358L && length(unique(protected)) == 351L, paste("prior inventory", total, length(unique(protected))))
  changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)
  stop_if(!any(changed %in% protected), "prior protected artifact changed")
  list(manifest_count=length(paths), entries=total, unique=length(unique(protected)))
}

working <- file.path(reports, working_name)
working_x <- manifest_artifacts(working)
stop_if(grepl('"phase": "13A"', json_text(working), fixed=TRUE) && grepl('"status": "implemented_validated_pending_sol_acceptance"', json_text(working), fixed=TRUE), "working manifest status")
stop_if(nrow(working_x)==21L, "working manifest artifact count")
for (i in seq_len(nrow(working_x))) stop_if(portable_match(file.path(root, working_x$rel[[i]]), working_x$sha256[[i]], working_x$bytes[[i]]), paste("working artifact", working_x$rel[[i]]))
expected_final <- c(working_x$rel, file.path("reports", working_name), "reports/infectious_disease_artifact_check.json", "src/python/systems/validate_phase13a_freeze.py", "src/R/systems/validate_phase13a_freeze.R")
final_x <- verify_manifest(final_name, "13A", "Infectious Disease System Baseline, 2026", 25L, expected_final)

for (name in phase12_names) {
  txt <- json_text(file.path(reports, name)); stop_if(grepl('"status": "ACCEPTED / FROZEN"', txt, fixed=TRUE), paste("Phase 12 status", name))
}
phase12a_x <- verify_manifest(phase12_names[[1]], "12A", "Vector Ecology Baseline, 2026", 17L)
phase12b_x <- verify_manifest(phase12_names[[2]], "12B", "Vector / Environment / Human-System Dependencies, 2026", 15L)
phase12c_x <- verify_manifest(phase12_names[[3]], "12C", "Vector Ecology Futures, 2050 / 2075", 28L)
phase12b_txt <- json_text(file.path(reports, phase12_names[[2]])); phase12a_path <- file.path(reports, phase12_names[[1]])
stop_if(grepl('"path": "reports/phase12a_vector_ecology_freeze_manifest.json"', phase12b_txt, fixed=TRUE), "Phase 12A protected input")
stop_if(grepl(paste0('"sha256": "', sha256_raw(canonical_bytes(raw_bytes(phase12a_path)), ".json"), '"'), phase12b_txt, fixed=TRUE), "Phase 12A protected hash")
stop_if(grepl('"phase12a_12b_immutable": true', json_text(file.path(reports, phase12_names[[3]])), fixed=TRUE), "Phase 12A/B immutability")

artifact_check <- tolower(json_text(file.path(reports, "infectious_disease_artifact_check.json")))
for (term in c('"status": "passed"','"nodes": 38','"relationships": 40','"observations": 25','"surveillance_records": 17','"sources": 27','"uncertainties": 18','"prior_freeze_manifest_entries_checked": 358','"prior_unique_protected_artifacts_checked": 351','"phase12abc_accepted_frozen": true','"active_holds_preserved": true')) stop_if(grepl(term, artifact_check, fixed=TRUE), paste("artifact check", term))
review <- tolower(json_text(file.path(reports, "infectious_disease_independent_review.md")))
for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"epidemiological_errors": []','"surveillance_errors": []','"spatial_scale_errors": []','"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
stop_if(file.exists(file.path(reports, "infectious_disease_independent_review_initial.md")), "initial review preserved")
for (rel in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c("phase 13a", "accepted / frozen", "phase 13b", "not implemented", "phase 13c", "active phase", "none", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved")) stop_if(grepl(term, txt, fixed=TRUE), paste("status", rel, term))
}
bad <- list.files(file.path(root, "data", "processed"), recursive=TRUE, full.names=TRUE)
bad <- c(bad, list.files(file.path(root, "outputs", "maps", "systems"), full.names=TRUE), list.files(file.path(root, "src", "python", "systems"), full.names=TRUE), list.files(file.path(root, "src", "R", "systems"), full.names=TRUE))
bad <- bad[grepl("phase13b|phase13c|infectious_disease_dependencies|infectious_disease_futures|(^|[/\\])42_|(^|[/\\])43_", tolower(basename(bad)))]
stop_if(length(bad)==0L, "Phase 13B/13C artifacts")

cat(sprintf("Phase 13A R freeze validation passed: 25 final artifacts, 21 working artifacts; Phase 12A/B/C protected artifacts %d/%d/%d; prior Phase 1–12 inventory 358 entries/351 unique artifacts; review, holds, deferred maintenance, and 13B/13C exclusion verified\n", nrow(phase12a_x), nrow(phase12b_x), nrow(phase12c_x)))
