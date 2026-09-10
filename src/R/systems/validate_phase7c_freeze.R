#!/usr/bin/env Rscript
# Independent base-R freeze-boundary validation for accepted Phase 7C.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
source_commit <- "39d9c97ebab0dad736188a320dc037a602e5f594"
final_name <- "phase7c_environmental_health_futures_freeze_manifest.json"
sibling_name <- "phase7b_exposure_dependencies_controls_freeze_manifest.json"
working_name <- "environmental_health_scenario_manifest.json"
check_name <- "environmental_health_scenario_artifact_check.json"
strict_name <- "phase7c_strict_provenance_check.json"
phase7a_name <- "phase7a_exposure_environmental_health_freeze_manifest.json"
review_initial <- "phase7c_exposure_futures_independent_review_initial.md"
review_final <- "phase7c_exposure_futures_independent_review.md"
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R", "toml")
expected_package <- c(
  "data/processed/scenarios/environmental_health_scenario_assumptions.csv",
  "data/processed/scenarios/exposure_nodes_scenario.csv",
  "data/processed/scenarios/exposure_edges_scenario.csv",
  "data/processed/scenarios/exposure_controls_scenario.csv",
  "data/processed/scenarios/exposure_uncertainty_scenario.csv",
  "outputs/figures/environmental_health_scenarios_comparison.csv",
  "outputs/figures/environmental_health_scenarios_comparison.png",
  "outputs/maps/systems/25_environmental_health_futures_2050.png",
  "outputs/maps/systems/25_environmental_health_futures_2050.svg",
  "outputs/maps/systems/25b_environmental_health_futures_2075.png",
  "outputs/maps/systems/25b_environmental_health_futures_2075.svg",
  "reports/environmental_health_scenario_sources.md",
  "reports/environmental_health_scenario_assumptions.md",
  "reports/environmental_health_scenario_consistency.md",
  "reports/environmental_health_future_worldbuilding.md",
  "reports/environmental_health_scenario_qa.md",
  "reports/phase7c_citation_ledger.json",
  "reports/phase7c_strict_provenance.md",
  "reports/phase7c_strict_provenance_check.json",
  "src/python/systems/build_environmental_health_futures.py",
  "src/python/systems/validate_environmental_health_futures.py",
  "src/R/systems/validate_environmental_health_futures.R",
  "reports/environmental_health_scenario_manifest.json",
  "reports/environmental_health_scenario_artifact_check.json",
  "reports/phase7c_exposure_futures_independent_review_initial.md",
  "reports/phase7c_exposure_futures_independent_review.md",
  "docs/phase_briefs/phase7c_environmental_health_futures.md",
  "src/python/systems/validate_phase7c_freeze.py",
  "src/R/systems/validate_phase7c_freeze.R"
)
expected_prior_entries <- 435L
expected_prior_unique <- 426L
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_raw <- function(raw) {
  vals <- as.integer(raw); next_vals <- c(vals[-1L], NA_integer_); keep <- !(vals == 13L & next_vals == 10L); out <- vals[keep]; out[out == 13L] <- 10L; as.raw(out)
}
crlf_raw <- function(raw) {
  vals <- as.integer(raw); out <- unlist(lapply(vals, function(x) if (x == 10L) c(13L,10L) else x), use.names=FALSE); as.raw(out)
}
sha256_many <- function(paths) {
  paths <- unique(as.character(paths)); if (!length(paths)) return(setNames(character(), character()))
  cmd <- Sys.which("sha256sum")
  if (!nzchar(cmd)) {
    certutil <- Sys.which("certutil"); stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
    ans <- vapply(paths, function(path) {
      out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE); text <- paste(out, collapse=" ")
      hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl=TRUE))[[1]]; stop_if(length(hits) >= 1L, paste("certutil failed", path)); tolower(hits[[1]])
    }, character(1)); return(setNames(ans, paths))
  }
  ans <- character(); starts <- seq(1L, length(paths), by=40L)
  for (start in starts) {
    chunk <- paths[start:min(start+39L, length(paths))]; out <- system2(cmd, chunk, stdout=TRUE, stderr=TRUE); text <- paste(out, collapse="\n")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl=TRUE))[[1]]; stop_if(length(hits) == length(chunk), paste("sha256sum failed", start)); ans <- c(ans, setNames(tolower(hits), chunk))
  }
  ans
}
manifest_entries <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8"); collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]; stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); bytes <- numeric(); current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  flush <- function() { if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }; current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_ }
  if (start + 1L <= length(lines)) for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { flush(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hit <- regmatches(line, direct)[[1]]
    if (length(hit) == 3L) { flush(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE); hit <- regmatches(line, nested)[[1]]
    if (length(hit) == 2L) { flush(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line, h)[[1]]; if (length(hh) == 2L && !is.na(current)) current_hash <- hh[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bb <- regmatches(line, b)[[1]]; if (length(bb) == 2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  flush(); data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}
verify_entry_sets <- function(sets) {
  all_rows <- do.call(rbind, lapply(sets, function(x) x$entries)); stop_if(nrow(all_rows) > 0L, "no manifest entries")
  paths <- file.path(root, all_rows$rel); raw_hashes <- sha256_many(paths); normalized <- list(); crlf <- list(); need <- character()
  for (i in seq_len(nrow(all_rows))) {
    path <- paths[[i]]; expected <- all_rows$sha256[[i]]; size <- all_rows$bytes[[i]]; raw <- raw_bytes(path); raw_hash <- unname(raw_hashes[[path]])
    raw_ok <- identical(raw_hash, expected) && (is.na(size) || as.numeric(size) == length(raw))
    if (!raw_ok && tolower(tools::file_ext(path)) %in% tolower(text_ext)) {
      need <- c(need, path)
      if (is.null(normalized[[path]])) { lf <- canonical_raw(raw); cf <- crlf_raw(lf); p1 <- tempfile(fileext=".txt"); p2 <- tempfile(fileext=".txt"); writeBin(lf, p1); writeBin(cf, p2); normalized[[path]] <- c(path=p1, bytes=length(lf)); crlf[[path]] <- c(path=p2, bytes=length(cf)) }
    } else stop_if(raw_ok, paste("artifact hash/bytes", all_rows$rel[[i]]))
  }
  if (length(need)) {
    unique_need <- unique(need); lf_paths <- vapply(normalized[unique_need], function(x) unname(x[["path"]]), character(1)); cf_paths <- vapply(crlf[unique_need], function(x) unname(x[["path"]]), character(1)); lf_hash <- sha256_many(lf_paths); cf_hash <- sha256_many(cf_paths)
    for (i in seq_len(nrow(all_rows))) if (paths[[i]] %in% unique_need) { path <- paths[[i]]; l <- normalized[[path]]; c <- crlf[[path]]; size <- all_rows$bytes[[i]]; expected <- all_rows$sha256[[i]]; l_path <- unname(l[["path"]]); c_path <- unname(c[["path"]]); ok <- (unname(lf_hash[[l_path]]) == expected && (is.na(size) || as.numeric(size) == as.numeric(l[["bytes"]]))) || (unname(cf_hash[[c_path]]) == expected && (is.na(size) || as.numeric(size) == as.numeric(c[["bytes"]]))); stop_if(ok, paste("text artifact hash/bytes", all_rows$rel[[i]])) }
  }
  invisible(TRUE)
}
read_csv <- function(relative) read.csv(file.path(root, relative), stringsAsFactors=FALSE, check.names=FALSE, na.strings=c(""))
check_png <- function(relative) { x <- readBin(file.path(root, relative), "raw", n=8); stop_if(identical(as.integer(x), c(137L,80L,78L,71L,13L,10L,26L,10L)), relative); stop_if(file.info(file.path(root, relative))$size > 100, relative) }
check_svg <- function(relative, terms) { txt <- paste(readLines(file.path(root, relative), warn=FALSE, encoding="UTF-8"), collapse=" "); for (term in terms) stop_if(grepl(term, txt, fixed=TRUE), paste(relative, term)) }
phase7a <- manifest_entries(file.path(reports, phase7a_name)); stop_if(nrow(phase7a) == 8L, "Phase 7A manifest artifact count")
phase7a_text <- json_text(file.path(reports, phase7a_name)); for (term in c('"accepted_phase": "7A"','"status": "ACCEPTED / FROZEN"','"nodes": 20','"edges": 20','"pathway_register": 5','"monitoring_matrix_rows": 5','"evidence_crosswalk": 10','"uncertainty_register": 13')) stop_if(grepl(term, phase7a_text, fixed=TRUE), paste("Phase 7A", term))
final_text <- json_text(file.path(reports, final_name)); for (term in c('"accepted_phase": "7C"','"baseline": "Environmental Health Futures, 2050 / 2075"','"status": "ACCEPTED / FROZEN"','"accepted_date": "2026-09-10"',paste0('"source_commit": "',source_commit,'"'), '"assumptions": 36','"scenario_nodes": 30','"scenario_edges": 30','"control_states": 30','"uncertainty_states": 30','"comparison_rows": 6','"phase7a_7b_immutable": true','"phase14_implemented": false','"qualitative_only": true','"unsupported_future_exposure_predictions": false','"unsupported_future_health_outcomes": false','"great_black_swamp": "C — HOLD / noncanonical"','"toledo_intake_coordinate_discrepancy": "UNRESOLVED"')) stop_if(grepl(term, final_text, fixed=TRUE), paste("final manifest", term))
final <- manifest_entries(file.path(reports, final_name)); stop_if(identical(as.character(final$rel), expected_package), "Phase 7C final artifact inventory")
working <- manifest_entries(file.path(reports, working_name)); stop_if(identical(as.character(working$rel), expected_package[1:11]), "Phase 7C working artifact inventory")
working_text <- json_text(file.path(reports, working_name)); for (term in c('"phase": "7C"','"assumptions": 36','"scenario_nodes": 30','"scenario_edges": 30','"control_states": 30','"uncertainty_states": 30','"comparison_rows": 6')) stop_if(grepl(term, working_text, fixed=TRUE), paste("working manifest", term))
check_text <- json_text(file.path(reports, check_name)); for (term in c('"status": "passed"','"assumptions": 36','"scenario_nodes": 30','"scenario_edges": 30','"control_states": 30','"uncertainty_states": 30','"comparison_rows": 6','"maps_25_25b_valid": true','"qualitative_only": true','"baseline_separation": true')) stop_if(grepl(term, check_text, fixed=TRUE), paste("artifact check", term))
strict_text <- json_text(file.path(reports, strict_name)); for (term in c('"status": "passed"','"phase": "7C"','"working_manifest_hashes_match": true','"unsupported_exact_health_outcome_claims": false','"unsupported_future_exposure_predictions": false','"unsupported_risk_scoring": false')) stop_if(grepl(term, strict_text, fixed=TRUE), paste("strict check", term))
sets <- list(list(name="final", entries=final), list(name="working", entries=working), list(name="Phase 7A", entries=phase7a))
phase_files <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE); phase_files <- phase_files[!basename(phase_files) %in% c(final_name, sibling_name)]
prior <- lapply(phase_files, function(path) { x <- manifest_entries(path); sets[[length(sets)+1L]] <<- list(name=basename(path), entries=x); x })
stop_if(length(phase_files) == 29L, "prior manifest count"); stop_if(sum(vapply(prior, nrow, integer(1))) == expected_prior_entries, "prior manifest entries"); all_prior_rel <- unique(unlist(lapply(prior, function(x) x$rel))); stop_if(length(all_prior_rel) == expected_prior_unique, "prior unique artifacts")
verify_entry_sets(sets)
changed <- gsub("\\\\", "/", system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)); stop_if(length(intersect(changed, all_prior_rel)) == 0L, "protected prior artifact changed")
for (rel in c("outputs/maps/systems/25_environmental_health_futures_2050.png","outputs/maps/systems/25b_environmental_health_futures_2075.png")) check_png(rel)
check_svg("outputs/maps/systems/25_environmental_health_futures_2050.svg", c("ENVIRONMENTAL HEALTH FUTURES", "2050")); check_svg("outputs/maps/systems/25b_environmental_health_futures_2075.svg", c("ENVIRONMENTAL HEALTH FUTURES", "2075"))
a <- read_csv("data/processed/scenarios/environmental_health_scenario_assumptions.csv"); n <- read_csv("data/processed/scenarios/exposure_nodes_scenario.csv"); e <- read_csv("data/processed/scenarios/exposure_edges_scenario.csv"); controls <- read_csv("data/processed/scenarios/exposure_controls_scenario.csv"); u <- read_csv("data/processed/scenarios/exposure_uncertainty_scenario.csv"); x <- read_csv("outputs/figures/environmental_health_scenarios_comparison.csv")
stop_if(nrow(a)==36L && nrow(n)==30L && nrow(e)==30L && nrow(controls)==30L && nrow(u)==30L && nrow(x)==6L, "Phase 7C counts")
stop_if(setequal(unique(a$scenario_id), c("A","B","C")) && setequal(unique(a$scenario_year), c(2050,2075)), "Phase 7C scenario horizons")
stop_if(all(n$reality_status == "fictional") && all(n$uncertainty == "moderate") && all(e$uncertainty == "moderate") && all(controls$uncertainty == "moderate") && all(u$uncertainty == "moderate"), "Phase 7C qualitative metadata")
stop_if(all(x$pathway_family == "All pathways") && all(x$change_type == "scenario_comparison") && all(grepl("-06$", x$assumption_id)), "Phase 7C comparison coverage")
initial <- json_text(file.path(reports, review_initial)); final_review_text <- json_text(file.path(reports, review_final)); stop_if(grepl('"passed": false', initial, fixed=TRUE), "initial review preserved"); for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"scenario_boundary_errors": []','"exposure_boundary_errors": []','"spatial_scale_errors": []','"schema_errors": []')) stop_if(grepl(term, final_review_text, fixed=TRUE), paste("final review", term))
status_terms <- list(
  "PROJECT_STATUS.md"=c("## phase 7b — accepted / frozen","## phase 7c — accepted / frozen",final_name,sibling_name,"active phase: **none**","phase 14 is not implemented","next approved planning target","great black swamp","hold","noncanonical","intake-coordinate discrepancy","unresolved"),
  "docs/canon_status.md"=c("phase 7b is **accepted / frozen**","phase 7c is **accepted / frozen**",final_name,sibling_name,"active phase: **none**","phase 14 is not implemented","next approved planning target","great black swamp","hold","noncanonical","intake-coordinate discrepancy","unresolved"),
  "reports/current_phase_handoff.md"=c("## phase 7b/7c final acceptance / freeze handoff","phase 7b: **accepted / frozen**","phase 7c: **accepted / frozen**",final_name,sibling_name,"active phase: **none**","phase 14 is not implemented","next approved planning target","great black swamp","hold","noncanonical","intake-coordinate discrepancy","unresolved"),
  "README.md"=c("phase 7b is **accepted / frozen**","phase 7c is **accepted / frozen**",final_name,sibling_name,"phase 14 is not implemented"),
  "reports/README.md"=c("phase 7b is **accepted / frozen**","phase 7c is **accepted / frozen**",final_name,sibling_name),
  "CHANGELOG.md"=c("sol formally accepted and froze phase 7b","sol formally accepted and froze phase 7c",final_name,sibling_name,"active phase is none","phase 14 is not implemented"),
  "docs/phase_briefs/phase7b_exposure_dependencies_controls.md"=c("status: accepted / frozen","phase7b_exposure_dependencies_controls_freeze_manifest.json"),
  "docs/phase_briefs/phase7c_environmental_health_futures.md"=c("status: accepted / frozen",final_name)
)
for (relative in names(status_terms)) { txt <- tolower(json_text(file.path(root, relative))); for (term in status_terms[[relative]]) stop_if(grepl(tolower(term), txt, fixed=TRUE), paste("status", relative, term)) }
for (base in c(file.path(root,"data","processed"),file.path(root,"outputs","maps","systems"),file.path(root,"src","python","systems"),file.path(root,"src","R","systems"))) { files <- list.files(base, recursive=TRUE, full.names=TRUE); bad <- files[grepl("phase14|phase_14",tolower(basename(files))) | grepl("(^|[/\\\\])44_",tolower(basename(files)))]; stop_if(length(bad)==0L, paste("Phase 14 implementation", base)) }
cat(sprintf("Phase 7C R freeze validation passed: 29 final artifacts; 11 working artifacts; Phase 7A/7B artifacts %d/%d; prior freeze inventory %d/%d; review, status surfaces, holds, deferred maintenance, and no Phase 14 implementation verified\n", nrow(phase7a), nrow(manifest_entries(file.path(reports, sibling_name))), expected_prior_entries, expected_prior_unique))
