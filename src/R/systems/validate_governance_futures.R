args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)

read_table <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c(""), fileEncoding="UTF-8")
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
canonical_raw <- function(x) charToRaw(gsub("\r\n?", "\n", rawToChar(x), perl=TRUE))
text_ext <- function(path) tolower(tools::file_ext(path)) %in% c("csv","json","md","txt","yml","yaml","svg")
portable_match <- function(rel, expected) {
  path <- file.path(root, rel)
  stopifnot(file.exists(path))
  if (sha256_file(path) == expected) return(TRUE)
  if (!text_ext(path)) return(FALSE)
  accepted_tmp <- tempfile(fileext=tools::file_ext(path)); err_tmp <- tempfile()
  on.exit(unlink(c(accepted_tmp, err_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", rel)), stdout=accepted_tmp, stderr=err_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted <- readBin(accepted_tmp, "raw", n=as.numeric(file.info(accepted_tmp)$size))
  working <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  if (!identical(canonical_raw(accepted), canonical_raw(working))) return(FALSE)
  lf <- tempfile(fileext=tools::file_ext(path)); crlf <- tempfile(fileext=tools::file_ext(path))
  on.exit(unlink(c(lf, crlf)), add=TRUE)
  writeBin(canonical_raw(accepted), lf)
  writeBin(charToRaw(gsub("\n", "\r\n", rawToChar(canonical_raw(accepted)), fixed=TRUE)), crlf)
  expected %in% c(sha256_file(lf), sha256_file(crlf))
}
manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  current <- NA_character_; rel <- character(); hashes <- character(); bytes <- numeric()
  for (line in lines) {
    direct <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    direct_hit <- regmatches(line, direct)[[1]]
    if (length(direct_hit)==3 && grepl("/", direct_hit[[2]], fixed=TRUE)) {
      rel <- c(rel, direct_hit[[2]]); hashes <- c(hashes, direct_hit[[3]]); bytes <- c(bytes, NA_real_); next
    }
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, m)[[1]]
    if (length(hit)==2 && grepl("/", hit[[2]], fixed=TRUE)) current <- hit[[2]]
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh)==2 && !is.na(current)) {
      rel <- c(rel, current); hashes <- c(hashes, hh[[2]])
      b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
      bb <- regmatches(line, b)[[1]]
      bytes <- c(bytes, if (length(bb)==2) as.numeric(bb[[2]]) else NA_real_)
      current <- NA_character_
    }
  }
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}
check_manifest <- function(path, portable=TRUE) {
  x <- manifest_artifacts(path); stopifnot(nrow(x)>0)
  for (i in seq_len(nrow(x))) {
    stopifnot(file.exists(file.path(root, x$rel[[i]])))
    if (portable) stopifnot(portable_match(x$rel[[i]], x$sha256[[i]])) else stopifnot(sha256_file(file.path(root, x$rel[[i]])) == x$sha256[[i]])
  }
  nrow(x)
}

scenario_ids <- c("A2050","A2075","B2050","B2075","C2050","C2075")
scenario_years <- setNames(as.integer(substr(scenario_ids, 2, 5)), scenario_ids)
scenario_dir <- file.path(root, "data", "processed", "scenarios")
analysis_dir <- file.path(root, "data", "processed", "analysis")
network_dir <- file.path(root, "data", "processed", "networks")
fig_dir <- file.path(root, "outputs", "figures")
map_dir <- file.path(root, "outputs", "maps", "systems")
report_dir <- file.path(root, "reports")

A <- read_table(file.path(scenario_dir, "governance_scenario_assumptions.csv"))
AS <- read_table(file.path(scenario_dir, "governance_actor_states_scenario.csv"))
AU <- read_table(file.path(scenario_dir, "governance_authority_states_scenario.csv"))
D <- read_table(file.path(scenario_dir, "governance_dependency_states_scenario.csv"))
C <- read_table(file.path(scenario_dir, "governance_coordination_states_scenario.csv"))
U <- read_table(file.path(scenario_dir, "governance_uncertainty_states_scenario.csv"))
X <- read_table(file.path(fig_dir, "governance_scenario_comparison.csv"))
S <- read_table(file.path(analysis_dir, "governance_scenario_sources.csv"))
base_actors <- read_table(file.path(analysis_dir, "governance_actors.csv"))
base_auth <- read_table(file.path(analysis_dir, "governance_authorities.csv"))
base_dep <- read_table(file.path(analysis_dir, "governance_dependency_register.csv"))
base_coord <- read_table(file.path(analysis_dir, "governance_coordination_mechanisms.csv"))
base_unc <- read_table(file.path(analysis_dir, "governance_uncertainty_register.csv"))

expected <- list(
  A=c("assumption_id","scenario_id","scenario","horizon","domain","assumption","evidence_basis","source_id","uncertainty","reality_status","canon_status","classification","notes"),
  AS=c("state_id","scenario_id","scenario","horizon","actor_id","actor_name","actor_type","current_fact","scenario_assumption","scenario_consequence","future_role","change_type","authority_boundary","assumption_id","current_fact_source_id","source_id","reality_status","canon_status","notes"),
  AU=c("state_id","scenario_id","scenario","horizon","authority_id","actor_id","domain_system","authority_or_role","current_fact","scenario_assumption","scenario_consequence","future_authority_pattern","legal_status","human_decision_boundary","assumption_id","current_fact_source_id","source_id","reality_status","canon_status","notes"),
  D=c("state_id","scenario_id","scenario","horizon","dependency_id","system_a","system_b","dependency_type","current_fact","scenario_assumption","scenario_consequence","dependency_state","coordination_implication","assumption_id","current_fact_source_id","source_id","reality_status","canon_status","notes"),
  C=c("state_id","scenario_id","scenario","horizon","mechanism_id","mechanism_type","mechanism_name","current_fact","scenario_assumption","scenario_consequence","future_mechanism","mechanism_character","authority_boundary","assumption_id","current_fact_source_id","source_id","reality_status","canon_status","notes"),
  U=c("state_id","scenario_id","scenario","horizon","uncertainty_id","subject_type","subject_id","domain_system","uncertainty_category","current_fact","scenario_assumption","scenario_consequence","uncertainty_state","assumption_id","current_fact_source_id","source_id","reality_status","canon_status","notes"),
  X=c("scenario_id","scenario","horizon","scenario_family","authority_clarity","cross_jurisdiction_coordination","data_interoperability","monitoring_to_decision_linkage","public_private_coordination","binational_coordination","tribal_consultation_and_participation","funding_alignment","adaptive_management","decision_latency","institutional_redundancy","enforcement_alignment","voluntary_program_coordination","emergency_coordination","ecological_infrastructure_governance","technology_governance","notes")
)
frames <- list(A=A, AS=AS, AU=AU, D=D, C=C, U=U, X=X)
for (nm in names(frames)) stopifnot(setequal(names(frames[[nm]]), expected[[nm]]))
stopifnot(nrow(A)==48, nrow(AS)==120, nrow(AU)==90, nrow(D)==150, nrow(C)==84, nrow(U)==96, nrow(X)==6, nrow(S)==19)
for (f in frames) {
  stopifnot(setequal(unique(f$scenario_id), scenario_ids))
  stopifnot(all(as.integer(f$horizon) == scenario_years[as.character(f$scenario_id)]))
  stopifnot(all(nchar(as.character(f$notes)) > 0))
}
stopifnot(!anyDuplicated(A$assumption_id), !anyDuplicated(AS$state_id), !anyDuplicated(AU$state_id), !anyDuplicated(D$state_id), !anyDuplicated(C$state_id), !anyDuplicated(U$state_id), !anyDuplicated(X$scenario_id), !anyDuplicated(S$source_id))
stopifnot(all(table(A$scenario_id)==8), all(table(AS$scenario_id)==20), all(table(AU$scenario_id)==15), all(table(D$scenario_id)==25), all(table(C$scenario_id)==14), all(table(U$scenario_id)==16))
stopifnot(all(A$reality_status=="fictional"), all(A$canon_status=="scenario"), all(A$classification=="SCENARIO ASSUMPTION"), all(A$source_id %in% S$source_id))
assumption_ids <- A$assumption_id
for (f in list(AS,AU,D,C,U)) {
  stopifnot(all(f$reality_status=="fictional"), all(f$canon_status=="scenario"), all(f$assumption_id %in% assumption_ids), all(f$source_id %in% S$source_id), all(f$current_fact_source_id %in% read_table(file.path(analysis_dir,"governance_sources.csv"))$source_id))
  stopifnot(all(grepl("^CURRENT FACT \\(2026 baseline\\):", f$current_fact)), all(grepl("^SCENARIO ASSUMPTION:", f$scenario_assumption)), all(grepl("^SCENARIO CONSEQUENCE:", f$scenario_consequence)))
}
stopifnot(all(AS$actor_id %in% base_actors$actor_id), all(AU$authority_id %in% base_auth$authority_id), all(AU$actor_id %in% base_actors$actor_id), all(D$dependency_id %in% base_dep$dependency_id), all(C$mechanism_id %in% base_coord$mechanism_id), all(U$uncertainty_id %in% base_unc$uncertainty_id))
stopifnot(all(AU$legal_status=="CURRENT AUTHORITY RETAINED; SCENARIO COORDINATION CHANGE"), all(grepl("final human decision authority", AU$human_decision_boundary, fixed=TRUE)))
stopifnot(all(nchar(as.character(X[,5:20])) > 0), setequal(unique(X$scenario_family), c("Integrated Basin Governance","Federated / Networked Governance","Fragmented / Contested Governance")))

future_text <- tolower(paste(capture.output(print(A)), capture.output(print(AS)), capture.output(print(AU)), capture.output(print(D)), capture.output(print(C)), capture.output(print(U)), capture.output(print(X)), collapse=" "))
stopifnot(!grepl("partisan|election|candidate|voter|party control|ideological", future_text), !grepl("[0-9]+[.]?[0-9]*[[:space:]]*(%|mw|mgd|tons?|dollars?)", future_text, perl=TRUE))
stopifnot(grepl("glifwc remains an intertribal", future_text, fixed=TRUE), grepl("distinct sovereign", future_text, fixed=TRUE), grepl("ai recommendation", future_text, fixed=TRUE), grepl("legal authority", future_text, fixed=TRUE), grepl("automatic enforcement", future_text, fixed=TRUE), grepl("sensor coverage", future_text, fixed=TRUE), grepl("institutional capacity", future_text, fixed=TRUE), grepl("composite governance score", future_text, fixed=TRUE))
stopifnot(all(grepl("CURRENT AUTHORITY RETAINED", AU$legal_status, fixed=TRUE)))
# Scenario B must express networked pluralism and not a scalar midpoint.
b_text <- tolower(paste(A$assumption[grepl("^B",A$scenario_id)], collapse=" "))
stopifnot(grepl("issue-specific", b_text, fixed=TRUE), grepl("overlapping networks", b_text, fixed=TRUE), grepl("redundancy", b_text, fixed=TRUE), grepl("friction", b_text, fixed=TRUE))
# Inherited holds remain explicit in the uncertainty consequences.
stopifnot(any(grepl("Toledo intake-coordinate discrepancy remains UNRESOLVED", U$scenario_consequence, fixed=TRUE)), any(grepl("Great Black Swamp remains C", U$scenario_consequence, fixed=TRUE)))

phase10a <- file.path(report_dir,"phase10a_governance_jurisdiction_freeze_manifest.json")
phase10b <- file.path(report_dir,"phase10b_governance_dependencies_coordination_freeze_manifest.json")
stopifnot(check_manifest(phase10a)==15, check_manifest(phase10b)==15)
stopifnot(sha256_file(phase10a)=="63f0a1481ae70bb2bc1954d084062f6052799cbce3ba9dac8f1859495f27f6d4")
prior_total <- 0L
prior_names <- list.files(report_dir, pattern="^phase.*_freeze_manifest[.]json$", full.names=FALSE)
prior_names <- prior_names[!(prior_names %in% c(basename(phase10a),basename(phase10b)))]
for (name in prior_names) prior_total <- prior_total + check_manifest(file.path(report_dir,name))
stopifnot(prior_total==196L)

for (base in c("34_governance_futures_2050","34b_governance_futures_2075")) {
  png <- file.path(map_dir,paste0(base,".png")); svg <- file.path(map_dir,paste0(base,".svg"))
  stopifnot(file.exists(png), file.info(png)$size > 10000, file.exists(svg), file.info(svg)$size > 10000)
  z <- tolower(paste(readLines(svg,warn=FALSE,encoding="UTF-8"),collapse=" "))
  stopifnot(grepl(ifelse(grepl("^34_",base),"map 34","map 34b"),z,fixed=TRUE), grepl("integrated basin",z,fixed=TRUE), grepl("federated / networked",z,fixed=TRUE), grepl("fragmented / contested",z,fixed=TRUE), grepl("not jurisdiction boundaries",z,fixed=TRUE), grepl("glifwc remains an intertribal",z,fixed=TRUE), grepl("ai recommendation",z,fixed=TRUE))
  if (grepl("^34b_",base)) stopifnot(grepl("2075 mature/diverged",z,fixed=TRUE))
}
stopifnot(file.info(file.path(fig_dir,"governance_scenario_comparison.png"))$size > 10000, file.info(file.path(fig_dir,"governance_scenario_comparison.svg"))$size > 10000)
scenario_manifest <- file.path(report_dir,"governance_scenario_manifest.json")
manifest_lines <- readLines(scenario_manifest,warn=FALSE,encoding="UTF-8")
stopifnot(any(grepl('"phase"[[:space:]]*:[[:space:]]*"10C"',manifest_lines,perl=TRUE)), any(grepl('"scenario_assumptions"[[:space:]]*:[[:space:]]*48',manifest_lines,perl=TRUE)), any(grepl('"uncertainty_states"[[:space:]]*:[[:space:]]*96',manifest_lines,perl=TRUE)))
stopifnot(check_manifest(scenario_manifest, portable=TRUE) == 21L)

changed <- system2("git", c("-C",root,"diff","--name-only","8664bcafdf1714c9085d016ebb32f4913b48dbef"), stdout=TRUE)
stopifnot(!any(grepl("phase11", changed, ignore.case=TRUE)))
cat(sprintf("Phase 10C R validation passed: %d assumptions, %d actor states, %d authority states, %d dependency states, %d coordination states, %d uncertainty states, %d comparison rows; Phase 10A/10B and %d prior Phase 1-9 protected artifacts verified; Maps 34/34b present\n", nrow(A), nrow(AS), nrow(AU), nrow(D), nrow(C), nrow(U), nrow(X), prior_total))
