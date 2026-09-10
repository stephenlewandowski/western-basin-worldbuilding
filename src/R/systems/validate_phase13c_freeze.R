#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 13C.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
source_commit <- "c746e361e052e979227e40140c6d923557911524"
final_name <- "phase13c_infectious_disease_futures_freeze_manifest.json"
working_name <- "infectious_disease_scenario_manifest.json"
phase13a_name <- "phase13a_infectious_disease_freeze_manifest.json"
phase13b_name <- "phase13b_infectious_disease_dependencies_freeze_manifest.json"
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R")
expected_final <- c(
  "data/processed/scenarios/infectious_disease_scenario_assumptions.csv",
  "data/processed/scenarios/infectious_disease_transmission_states_scenario.csv",
  "data/processed/scenarios/infectious_disease_surveillance_states_scenario.csv",
  "data/processed/scenarios/infectious_disease_response_states_scenario.csv",
  "data/processed/scenarios/infectious_disease_dependency_states_scenario.csv",
  "data/processed/scenarios/infectious_disease_uncertainty_states_scenario.csv",
  "data/processed/analysis/infectious_disease_scenario_sources.csv",
  "outputs/figures/infectious_disease_scenario_comparison.csv",
  "outputs/maps/systems/43_infectious_disease_system_futures_2050.png",
  "outputs/maps/systems/43_infectious_disease_system_futures_2050.svg",
  "outputs/maps/systems/43b_infectious_disease_system_futures_2075.png",
  "outputs/maps/systems/43b_infectious_disease_system_futures_2075.svg",
  "outputs/figures/infectious_disease_scenario_comparison.png",
  "outputs/figures/infectious_disease_scenario_comparison.svg",
  "reports/infectious_disease_scenario_sources.md",
  "reports/infectious_disease_scenario_assumptions.md",
  "reports/infectious_disease_scenario_findings.md",
  "reports/infectious_disease_scenario_qa.md",
  "reports/phase13c_citation_ledger.json",
  "src/python/systems/build_infectious_disease_futures.py",
  "src/python/systems/validate_infectious_disease_futures.py",
  "src/R/systems/validate_infectious_disease_futures.R",
  "reports/infectious_disease_scenario_artifact_check.json",
  "reports/infectious_disease_scenario_independent_review.md",
  "reports/infectious_disease_scenario_manifest.json",
  "docs/phase_briefs/phase13c_infectious_disease_futures.md",
  "src/python/systems/validate_phase13c_freeze.py",
  "src/R/systems/validate_phase13c_freeze.R"
)
expected_working <- expected_final[1:24]
expected_counts <- c(scenario_assumptions=36L, transmission_states=36L, surveillance_states=36L, response_states=36L, dependency_states=36L, uncertainty_states=36L, scenario_sources=33L, comparison_rows=6L)
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
sha256_raw <- function(raw, suffix=".bin") {
  tmp <- tempfile(fileext=suffix); on.exit(unlink(tmp), add=TRUE); writeBin(raw, tmp)
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, tmp, stdout=TRUE, stderr=TRUE); text <- paste(out, collapse=" ")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl=TRUE))[[1]]
    stop_if(length(hits) >= 1L, "sha256sum failed")
    return(tolower(hits[[1]]))
  }
  certutil <- Sys.which("certutil"); stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", tmp, "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, "certutil failed"); hits[[1]]
}
portable_match <- function(path, expected, recorded=NA_real_) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing artifact", path))
  raw <- raw_bytes(path); hashes <- c(sha256_raw(raw, tools::file_ext(path))); lengths <- c(length(raw))
  ext <- tools::file_ext(path)
  if (tolower(ext) %in% tolower(text_ext)) {
    canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
    crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
    hashes <- c(hashes, sha256_raw(canonical, ext), sha256_raw(crlf, ext)); lengths <- c(lengths, length(canonical), length(crlf))
  }
  tolower(expected) %in% hashes && (is.na(recorded) || as.numeric(recorded) %in% lengths)
}
manifest_entries <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); bytes <- numeric(); current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  if (start + 1L <= length(lines)) for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hit <- regmatches(line, direct)[[1]]
    if (length(hit)==3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE); hit <- regmatches(line, nested)[[1]]
    if (length(hit)==2L) { append_current(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bb <- regmatches(line, b)[[1]]
    if (length(bb)==2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  append_current(); data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}
verify_manifest <- function(name, expected_n, expected_rels=character()) {
  path <- file.path(reports, name); stop_if(file.exists(path), paste("missing manifest", name)); x <- manifest_entries(path)
  stop_if(nrow(x)==expected_n, paste(name, "artifact count", nrow(x)))
  if (length(expected_rels)) stop_if(identical(as.character(x$rel), expected_rels), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x
}
require_terms <- function(relative, terms) {
  txt <- tolower(paste(readLines(file.path(root, relative), warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in terms) stop_if(grepl(tolower(term), txt, fixed=TRUE), paste("status", relative, term))
}
final_txt <- json_text(file.path(reports, final_name))
for (term in c('"accepted_phase": "13C"', '"baseline": "Infectious Disease System Futures, 2050 / 2075"', '"status": "ACCEPTED / FROZEN"', '"accepted_by": "Sol explicit acceptance decision supplied for this run"', '"accepted_date": "2026-09-10"', paste0('"source_commit": "', source_commit, '"'), '"assumptions": 36', '"transmission_states": 36', '"surveillance_states": 36', '"response_states": 36', '"dependency_states": 36', '"uncertainty_states": 36', '"scenario_sources": 33', '"comparison_rows": 6', '"phase13a_13b_accepted_frozen": true', '"phase1_12_immutable": true', '"phase14_implemented": false', '"numeric_future_values_adopted": false', '"future_case_counts": false', '"future_incidence_forecast": false', '"outbreak_probability": false', '"disease_burden_forecast": false', '"individual_risk_model": false', '"vulnerability_ej_scoring": false', '"unsupported_local_downscaling": false', '"great_black_swamp": "C — HOLD / noncanonical"', '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"')) stop_if(grepl(term, final_txt, fixed=TRUE), paste("final manifest", term))
final_x <- verify_manifest(final_name, length(expected_final), expected_final)
stop_if(!any(final_x$rel == final_name), "final manifest self-list")
working_txt <- json_text(file.path(reports, working_name)); stop_if(grepl('"phase": "13C"', working_txt, fixed=TRUE) && grepl('"status": "implemented_validated_pending_sol_acceptance"', working_txt, fixed=TRUE), "working manifest identity")
working_x <- manifest_entries(file.path(reports, working_name)); stop_if(nrow(working_x)==length(expected_working), "working manifest artifact count")
stop_if(identical(as.character(working_x$rel), expected_working), "working manifest inventory")
for (i in seq_len(nrow(working_x))) stop_if(portable_match(file.path(root, working_x$rel[[i]]), working_x$sha256[[i]], working_x$bytes[[i]]), paste("working artifact", working_x$rel[[i]]))
phase13a_x <- verify_manifest(phase13a_name, 25L); phase13b_x <- verify_manifest(phase13b_name, 24L)
phase13a_txt <- json_text(file.path(reports, phase13a_name)); phase13b_txt <- json_text(file.path(reports, phase13b_name))
stop_if(grepl('"status": "ACCEPTED / FROZEN"', phase13a_txt, fixed=TRUE) && grepl('"status": "ACCEPTED / FROZEN"', phase13b_txt, fixed=TRUE), "prior phase status")
check_txt <- tolower(json_text(file.path(reports, "infectious_disease_scenario_artifact_check.json")))
for (term in c('"status": "passed"', '"assumptions": 36', '"transmission_states": 36', '"surveillance_states": 36', '"response_states": 36', '"dependency_states": 36', '"uncertainty_states": 36', '"scenario_sources": 33', '"comparison_rows": 6', '"phase13a_13b_freeze_integrity": true', '"prior_freeze_manifest_entries_checked": 358', '"prior_unique_protected_artifacts_checked": 351', '"phase13a_artifacts_checked": 25', '"phase13b_artifacts_checked": 24', '"manifest_artifacts_checked": 24', '"active_holds_preserved": true', '"deferred_maintenance_preserved": true', '"phase14_not_implemented": true', '"review_present": true')) stop_if(grepl(term, check_txt, fixed=TRUE), paste("artifact check", term))
require_terms("PROJECT_STATUS.md", c("## phase 13c — accepted / frozen", final_name, "active phase: **none**", "next analytical phase: **not approved**", "phase 14 is not implemented", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"))
require_terms("docs/canon_status.md", c("phase 13c is **accepted / frozen**", final_name, "active phase: **none**", "next analytical phase: **not approved**", "phase 14 is not implemented", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"))
require_terms("reports/current_phase_handoff.md", c("## phase 13c final acceptance / freeze handoff", "phase 13c **accepted / frozen**", final_name, "active phase: **none**", "next analytical phase: **not approved**", "phase 14 is not implemented", "great black swamp", "hold", "noncanonical", "intake-coordinate discrepancy", "unresolved"))
require_terms("README.md", c("phase 13c is **accepted / frozen**", final_name, "phase 13c python freeze validator", "phase 13c independent r freeze validator"))
require_terms("CHANGELOG.md", c("sol formally accepted and froze phase 13c", final_name, "active phase is none", "next analytical phase is not approved"))
require_terms("docs/phase_briefs/phase13c_infectious_disease_futures.md", c("status: approved scope / not implemented", "phase 13c", "2050", "2075", "great black swamp", "toledo intake-coordinate discrepancy"))
review <- tolower(json_text(file.path(reports, "infectious_disease_scenario_independent_review.md")))
for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"epidemiological_errors": []', '"scenario_boundary_errors": []', '"surveillance_errors": []', '"spatial_scale_errors": []', '"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
prior_names <- c(phase13a_name, phase13b_name, final_name)
prior_files <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE); prior_files <- prior_files[!basename(prior_files) %in% prior_names]
protected <- character(); expected_hashes <- character(); prior_entries <- 0L
for (path in sort(prior_files)) {
  x <- manifest_entries(path)
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; expected <- x$sha256[[i]]
    if (rel %in% names(expected_hashes)) stop_if(unname(expected_hashes[[rel]]) == expected, paste("conflicting prior hash", rel))
    expected_hashes[rel] <- expected; stop_if(portable_match(file.path(root, rel), expected, x$bytes[[i]]), paste("prior hash", rel)); protected <- c(protected, rel); prior_entries <- prior_entries + 1L
  }
}
stop_if(prior_entries == 358L && length(unique(protected)) == 351L, paste("prior inventory", prior_entries, length(unique(protected))))
changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)
stop_if(length(intersect(changed, unique(c(protected, phase13a_x$rel, phase13b_x$rel)))) == 0L, "protected artifact changed")
for (base in c(file.path(root,"data","processed"), file.path(root,"outputs","maps","systems"), file.path(root,"src","python","systems"), file.path(root,"src","R","systems"))) {
  files <- list.files(base, recursive=TRUE, full.names=TRUE); bad <- files[grepl("phase14|phase_14|(^|[/\\\\])44_", tolower(basename(files)))]
  stop_if(length(bad)==0L, paste("Phase 14 implementation", base))
}
cat(sprintf("Phase 13C R freeze validation passed: %d final artifacts, %d working artifacts; Phase 13A/13B artifacts %d/%d; prior Phase 1–12 inventory %d/%d; review, status surfaces, holds, deferred maintenance, and no Phase 14 implementation verified\n", nrow(final_x), nrow(working_x), nrow(phase13a_x), nrow(phase13b_x), prior_entries, length(unique(protected))))
