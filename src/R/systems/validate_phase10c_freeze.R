args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
source_commit <- "4541e6dd036ccc51534827ba1c6a791fd37d0145"
final_name <- "phase10c_governance_futures_freeze_manifest.json"
phase10a_name <- "phase10a_governance_jurisdiction_freeze_manifest.json"
phase10b_name <- "phase10b_governance_dependencies_coordination_freeze_manifest.json"
text_ext <- function(path) tolower(tools::file_ext(path)) %in% c("csv","json","md","txt","yml","yaml","svg")
canonical_raw <- function(x) charToRaw(gsub("\r\n?", "\n", rawToChar(x), perl=TRUE))
sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stopifnot(length(out) >= 1)
    return(tolower(gsub("[^0-9a-f]", "", strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1])))
  }
  certutil <- Sys.which("certutil")
  stopifnot(nchar(certutil) > 0)
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  normalized <- tolower(gsub("[[:space:]]+", "", out))
  hits <- normalized[grepl("^[0-9a-f]{64}$", normalized)]
  stopifnot(length(hits) >= 1)
  hits[[1]]
}
sha256_raw <- function(raw, ext="bin") {
  tmp <- tempfile(fileext=paste0(".", ext)); on.exit(unlink(tmp), add=TRUE); writeBin(raw, tmp); sha256_file(tmp)
}
source_blob <- function(rel) {
  tmp <- tempfile(); err <- tempfile(); on.exit(unlink(c(tmp,err)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0(source_commit, ":", rel)), stdout=tmp, stderr=err)
  stopifnot(is.null(status) || status == 0)
  readBin(tmp, "raw", n=as.numeric(file.info(tmp)$size))
}
portable_match <- function(rel, expected) {
  path <- file.path(root, rel); stopifnot(file.exists(path)); actual <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  if (sha256_raw(actual, tools::file_ext(path)) == expected) return(TRUE)
  if (!text_ext(path)) return(FALSE)
  accepted <- source_blob(rel)
  if (!identical(canonical_raw(actual), canonical_raw(accepted))) return(FALSE)
  expected %in% c(sha256_raw(accepted, tools::file_ext(path)), sha256_raw(charToRaw(gsub("\n", "\r\n", rawToChar(canonical_raw(accepted)), fixed=TRUE)), tools::file_ext(path)))
}
manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  current <- NA_character_; current_bytes <- NA_real_; current_hash <- NA_character_; rel <- character(); bytes <- numeric(); hashes <- character()
  append_current <- function(force=FALSE) {
    if (!is.na(current) && !is.na(current_hash) && (force || !is.na(current_bytes))) {
      rel <<- c(rel, current); bytes <<- c(bytes, current_bytes); hashes <<- c(hashes, current_hash)
      current <<- NA_character_; current_bytes <<- NA_real_; current_hash <<- NA_character_
    }
  }
  for (line in lines) {
    direct <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    direct_hit <- regmatches(line, direct)[[1]]
    if (length(direct_hit)==3 && grepl("/", direct_hit[[2]], fixed=TRUE)) { append_current(force=TRUE); rel <- c(rel,direct_hit[[2]]); bytes <- c(bytes,NA_real_); hashes <- c(hashes,direct_hit[[3]]); next }
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line,m)[[1]]
    if (length(hit)==2 && grepl("/", hit[[2]], fixed=TRUE)) { append_current(force=TRUE); current <- hit[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bh <- regmatches(line,b)[[1]]
    if (length(bh)==2 && !is.na(current)) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line,h)[[1]]
    if (length(hh)==2 && !is.na(current)) current_hash <- hh[[2]]
    append_current()
  }
  append_current(force=TRUE); data.frame(rel=rel, bytes=bytes, sha256=hashes, stringsAsFactors=FALSE)
}
check_manifest <- function(path, phase, baseline, expected_counts, expected_artifacts, source_expected=TRUE) {
  txt <- paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
  stopifnot(grepl(paste0('"accepted_phase": "',phase,'"'),txt,fixed=TRUE), grepl(paste0('"baseline": "',baseline,'"'),txt,fixed=TRUE), grepl('"status": "ACCEPTED / FROZEN"',txt,fixed=TRUE))
  if (source_expected) stopifnot(grepl('"source_commit": "e1f233cc89e3694d2f08dfd81fde6f9194f57a65"',txt,fixed=TRUE))
  for (name in names(expected_counts)) stopifnot(grepl(paste0('"',name,'": ',expected_counts[[name]]),txt,fixed=TRUE))
  x <- manifest_artifacts(path); stopifnot(nrow(x)==length(expected_artifacts), setequal(x$rel,expected_artifacts))
  for (i in seq_len(nrow(x))) stopifnot(portable_match(x$rel[[i]],x$sha256[[i]]), x$bytes[[i]] > 0)
  nrow(x)
}
final_path <- file.path(reports, final_name); a_path <- file.path(reports, phase10a_name); b_path <- file.path(reports, phase10b_name)
final_txt <- paste(readLines(final_path,warn=FALSE,encoding="UTF-8"),collapse=" ")
stopifnot(grepl('"accepted_phase": "10C"',final_txt,fixed=TRUE), grepl('"baseline": "Governance Futures, 2050 / 2075"',final_txt,fixed=TRUE), grepl('"status": "ACCEPTED / FROZEN"',final_txt,fixed=TRUE), grepl('"accepted_date": "2026-09-07"',final_txt,fixed=TRUE), grepl(paste0('"source_commit": "',source_commit,'"'),final_txt,fixed=TRUE))
final_expected_counts <- c(scenario_assumptions=48L,actor_states=120L,authority_states=90L,dependency_states=150L,coordination_states=84L,uncertainty_states=96L,scenario_sources=19L,comparison_rows=6L)
for (name in names(final_expected_counts)) stopifnot(grepl(paste0('"',name,'": ',final_expected_counts[[name]]),final_txt,fixed=TRUE))
final_x <- manifest_artifacts(final_path); stopifnot(nrow(final_x)==23L)
for (i in seq_len(nrow(final_x))) stopifnot(portable_match(final_x$rel[[i]],final_x$sha256[[i]]), final_x$bytes[[i]] > 0)
phase10c_paths <- final_x$rel
phase10a_expected <- c("data/processed/analysis/governance_actors.csv","data/processed/analysis/governance_authorities.csv","data/processed/networks/governance_relationships.csv","data/processed/analysis/governance_sources.csv","data/processed/analysis/governance_uncertainty_register.csv","outputs/maps/systems/32_governance_jurisdiction_2026.png","outputs/maps/systems/32_governance_jurisdiction_2026.svg","reports/governance_baseline_sources.md","reports/governance_baseline_assumptions.md","reports/governance_baseline_findings.md","reports/governance_baseline_qa.md","reports/governance_baseline_artifact_check.json","reports/governance_independent_review.md","reports/governance_post_correction_independent_review.md","reports/governance_additional_post_correction_independent_review.md")
phase10b_expected <- c("data/processed/analysis/governance_dependency_register.csv","data/processed/analysis/governance_coordination_mechanisms.csv","data/processed/analysis/governance_dependency_matrix.csv","data/processed/networks/governance_dependency_edges.csv","data/processed/analysis/governance_sources.csv","outputs/maps/systems/33_cross_system_governance_dependencies_2026.png","outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg","reports/governance_dependency_sources.md","reports/governance_dependency_assumptions.md","reports/governance_dependency_findings.md","reports/governance_dependency_qa.md","reports/governance_dependency_artifact_check.json","reports/governance_independent_review.md","reports/governance_post_correction_independent_review.md","reports/governance_additional_post_correction_independent_review.md")
a_entries <- check_manifest(a_path,"10A","Governance & Jurisdiction Baseline, 2026",c(actors=40L,authorities=100L,relationships=100L,sources=48L,uncertainties=16L),phase10a_expected)
b_entries <- check_manifest(b_path,"10B","Cross-System Authority, Dependencies & Coordination, 2026",c(dependency_register=25L,dependency_edges=25L,coordination_mechanisms=14L,matrix_rows=10L,sources_reused=48L),phase10b_expected)
b_txt <- paste(readLines(b_path,warn=FALSE,encoding="UTF-8"),collapse=" "); stopifnot(grepl(paste0('"sha256": "',sha256_file(a_path),'"'),b_txt,fixed=TRUE),grepl(paste0('"bytes": ',file.info(a_path)$size),b_txt,fixed=TRUE))
prior_names <- list.files(reports,pattern="^phase.*_freeze_manifest[.]json$",full.names=FALSE); prior_names <- prior_names[!(prior_names %in% c(phase10a_name,phase10b_name,final_name))]
prior_total <- 0L; prior_paths <- character(); newline_only <- 0L
for (name in prior_names) { x <- manifest_artifacts(file.path(reports,name)); stopifnot(nrow(x)>0); for (i in seq_len(nrow(x))) { stopifnot(portable_match(x$rel[[i]],x$sha256[[i]])); if (sha256_file(file.path(root,x$rel[[i]])) != x$sha256[[i]]) newline_only <- newline_only + 1L; stopifnot(!(x$rel[[i]] %in% prior_paths), !(x$rel[[i]] %in% phase10c_paths), !(x$rel[[i]] %in% c(phase10a_expected,phase10b_expected))); prior_paths <- c(prior_paths,x$rel[[i]]); prior_total <- prior_total + 1L } }
stopifnot(prior_total==196L)
changed <- system2("git",c("-C",root,"diff","--name-only",source_commit),stdout=TRUE); stopifnot(!any(changed %in% prior_paths), !any(grepl("phase11",changed,ignore.case=TRUE)))
review <- paste(readLines(file.path(reports,"governance_scenario_independent_review.md"),warn=FALSE,encoding="UTF-8"),collapse=" "); stopifnot(grepl('"passed": true',review,fixed=TRUE),grepl('"security_concerns": []',review,fixed=TRUE),grepl('"logic_errors": []',review,fixed=TRUE),grepl('"provenance_errors": []',review,fixed=TRUE),grepl('"scenario_boundary_errors": []',review,fixed=TRUE),grepl('"authority_classification_errors": []',review,fixed=TRUE))
for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","docs/agent_workflow.md","docs/phase_briefs/phase10a_governance_jurisdiction_baseline.md","docs/phase_briefs/phase10b_governance_dependencies_coordination.md","docs/phase_briefs/phase10c_governance_futures.md","reports/current_phase_handoff.md","README.md","CHANGELOG.md","reports/README.md")) { z <- tolower(paste(readLines(file.path(root,rel),warn=FALSE,encoding="UTF-8"),collapse=" ")); stopifnot(grepl("phase 10c",z,fixed=TRUE),grepl("accepted / frozen",z,fixed=TRUE)) }
for (rel in c("docs/canon_status.md","reports/current_phase_handoff.md")) { z <- tolower(paste(readLines(file.path(root,rel),warn=FALSE,encoding="UTF-8"),collapse=" ")); stopifnot(grepl("great black swamp",z,fixed=TRUE),grepl("hold",z,fixed=TRUE),grepl("noncanonical",z,fixed=TRUE),grepl("intake-coordinate discrepancy",z,fixed=TRUE),grepl("unresolved",z,fixed=TRUE)) }
for (base in c("34_governance_futures_2050","34b_governance_futures_2075")) { png <- file.path(root,"outputs/maps/systems",paste0(base,".png")); svg <- file.path(root,"outputs/maps/systems",paste0(base,".svg")); stopifnot(file.info(png)$size>10000,file.info(svg)$size>10000); z <- tolower(paste(readLines(svg,warn=FALSE,encoding="UTF-8"),collapse=" ")); stopifnot(grepl(ifelse(base=="34_governance_futures_2050","map 34","map 34b"),z,fixed=TRUE),grepl("integrated basin",z,fixed=TRUE),grepl("federated / networked",z,fixed=TRUE),grepl("fragmented / contested",z,fixed=TRUE),grepl("not jurisdiction boundaries",z,fixed=TRUE),grepl("ai recommendation",z,fixed=TRUE)); if (base=="34b_governance_futures_2075") stopifnot(grepl("2075 mature/diverged",z,fixed=TRUE)) }
cat(sprintf("Phase 10C freeze R validation passed: 23 Phase 10C protected artifacts; %d Phase 10A/10B manifest entries, %d unique Phase 10A/10B artifacts; %d prior Phase 1-9 protected artifacts; review and holds preserved\n",a_entries+b_entries,length(unique(c(phase10a_expected,phase10b_expected))),prior_total))
