args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), "../../.."), mustWork=FALSE)
reports <- file.path(root, "reports")
source_commit <- "e1f233cc89e3694d2f08dfd81fde6f9194f57a65"
final_names <- c(
  "phase10a_governance_jurisdiction_freeze_manifest.json",
  "phase10b_governance_dependencies_coordination_freeze_manifest.json"
)
expected_phase <- c("10A", "10B")
expected_counts <- list(
  c(actors=40L, authorities=100L, relationships=100L, sources=48L, uncertainties=16L),
  c(dependency_register=25L, dependency_edges=25L, coordination_mechanisms=14L, matrix_rows=10L, sources_reused=48L)
)
expected_artifacts <- list(
  c(
    "data/processed/analysis/governance_actors.csv",
    "data/processed/analysis/governance_authorities.csv",
    "data/processed/networks/governance_relationships.csv",
    "data/processed/analysis/governance_sources.csv",
    "data/processed/analysis/governance_uncertainty_register.csv",
    "outputs/maps/systems/32_governance_jurisdiction_2026.png",
    "outputs/maps/systems/32_governance_jurisdiction_2026.svg",
    "reports/governance_baseline_sources.md",
    "reports/governance_baseline_assumptions.md",
    "reports/governance_baseline_findings.md",
    "reports/governance_baseline_qa.md",
    "reports/governance_baseline_artifact_check.json",
    "reports/governance_independent_review.md",
    "reports/governance_post_correction_independent_review.md",
    "reports/governance_additional_post_correction_independent_review.md"
  ),
  c(
    "data/processed/analysis/governance_dependency_register.csv",
    "data/processed/analysis/governance_coordination_mechanisms.csv",
    "data/processed/analysis/governance_dependency_matrix.csv",
    "data/processed/networks/governance_dependency_edges.csv",
    "data/processed/analysis/governance_sources.csv",
    "outputs/maps/systems/33_cross_system_governance_dependencies_2026.png",
    "outputs/maps/systems/33_cross_system_governance_dependencies_2026.svg",
    "reports/governance_dependency_sources.md",
    "reports/governance_dependency_assumptions.md",
    "reports/governance_dependency_findings.md",
    "reports/governance_dependency_qa.md",
    "reports/governance_dependency_artifact_check.json",
    "reports/governance_independent_review.md",
    "reports/governance_post_correction_independent_review.md",
    "reports/governance_additional_post_correction_independent_review.md"
  )
)

sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stopifnot(length(out) >= 1)
    token <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    return(tolower(gsub("[^0-9a-f]", "", token)))
  }
  certutil <- Sys.which("certutil")
  stopifnot(nchar(certutil) > 0)
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  normalized <- tolower(gsub("[[:space:]]+", "", out))
  hits <- normalized[grepl("^[0-9a-f]{64}$", normalized)]
  stopifnot(length(hits) >= 1)
  hits[[1]]
}

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE)
  current <- NA_character_; current_bytes <- NA_real_; current_hash <- NA_character_; rel <- character(); bytes <- numeric(); hashes <- character()
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) {
      rel <<- c(rel, current); bytes <<- c(bytes, current_bytes); hashes <<- c(hashes, current_hash)
      current <<- NA_character_; current_bytes <<- NA_real_; current_hash <<- NA_character_
    }
  }
  for (line in lines) {
    direct <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    direct_hit <- regmatches(line, direct)[[1]]
    if (length(direct_hit) == 3 && grepl("/", direct_hit[[2]], fixed=TRUE)) {
      rel <- c(rel, direct_hit[[2]]); bytes <- c(bytes, NA_real_); hashes <- c(hashes, direct_hit[[3]])
      next
    }
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, m)[[1]]
    if (length(hit) == 2 && grepl("/", hit[[2]], fixed=TRUE)) { append_current(); current <- hit[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
    bh <- regmatches(line, b)[[1]]
    if (length(bh) == 2 && !is.na(current)) { current_bytes <- as.numeric(bh[[2]]); append_current() }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh) == 2 && !is.na(current)) { current_hash <- hh[[2]]; if (!is.na(current_bytes)) append_current() }
  }
  append_current()
  data.frame(rel=rel, bytes=bytes, sha256=hashes, stringsAsFactors=FALSE)
}

portable_manifest_match <- function(path, rel, expected) {
  if (!tolower(tools::file_ext(path)) %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg")) return(FALSE)
  accepted_tmp <- tempfile(fileext=tools::file_ext(path)); error_tmp <- tempfile()
  on.exit(unlink(c(accepted_tmp, error_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", rel)), stdout=accepted_tmp, stderr=error_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted_raw <- readBin(accepted_tmp, "raw", n=as.numeric(file.info(accepted_tmp)$size))
  working_raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  canonical <- function(x) charToRaw(gsub("\r\n?", "\n", rawToChar(x), perl=TRUE))
  if (!identical(canonical(accepted_raw), canonical(working_raw))) return(FALSE)
  lf_tmp <- tempfile(fileext=tools::file_ext(path)); crlf_tmp <- tempfile(fileext=tools::file_ext(path))
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical(accepted_raw), lf_tmp)
  writeBin(charToRaw(gsub("\n", "\r\n", rawToChar(canonical(accepted_raw)), fixed=TRUE)), crlf_tmp)
  expected %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

portable_final_match <- function(path, expected, expected_bytes) {
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg"))) return(length(raw) == expected_bytes && sha256_file(path) == expected)
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  lf_tmp <- tempfile(fileext=paste0(".", ext)); crlf_tmp <- tempfile(fileext=paste0(".", ext))
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  hashes <- c(sha256_file(path), sha256_file(lf_tmp), sha256_file(crlf_tmp))
  expected %in% hashes && expected_bytes %in% c(length(raw), length(canonical), length(crlf))
}

verify_final <- function(i) {
  path <- file.path(reports, final_names[[i]])
  stopifnot(file.exists(path))
  txt <- paste(readLines(path, warn=FALSE), collapse="\n")
  stopifnot(grepl(paste0('"accepted_phase": "', expected_phase[[i]], '"'), txt, fixed=TRUE))
  stopifnot(grepl('"status": "ACCEPTED / FROZEN"', txt, fixed=TRUE))
  stopifnot(grepl(paste0('"source_commit": "', source_commit, '"'), txt, fixed=TRUE))
  stopifnot(grepl('"accepted_date": "2026-09-04"', txt, fixed=TRUE))
  for (name in names(expected_counts[[i]])) stopifnot(grepl(paste0('"', name, '": ', expected_counts[[i]][[name]]), txt, fixed=TRUE))
  x <- manifest_artifacts(path)
  stopifnot(nrow(x) == length(expected_artifacts[[i]]), setequal(x$rel, expected_artifacts[[i]]))
  for (j in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[j]])
    stopifnot(portable_final_match(p, x$sha256[[j]], x$bytes[[j]]))
  }
  x$rel
}

all_rel <- character(); entries <- 0L
for (i in seq_along(final_names)) {
  rel <- verify_final(i)
  all_rel <- c(all_rel, rel); entries <- entries + length(rel)
}
stopifnot(length(unique(all_rel)) == 26L, entries == 30L)

b_txt <- paste(readLines(file.path(reports, final_names[[2]]), warn=FALSE), collapse=" ")
a_path <- file.path(reports, final_names[[1]])
stopifnot(grepl(paste0('"sha256": "', sha256_file(a_path), '"'), b_txt, fixed=TRUE), grepl(paste0('"bytes": ', file.info(a_path)$size), b_txt, fixed=TRUE))

prior_total <- 0L
prior_names <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=FALSE)
prior_names <- prior_names[!(prior_names %in% c(final_names, "phase10c_governance_futures_freeze_manifest.json"))]
for (name in prior_names) {
  x <- manifest_artifacts(file.path(reports, name))
  stopifnot(nrow(x) > 0)
  for (i in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[i]])
    stopifnot(file.exists(p))
    exact <- sha256_file(p) == x$sha256[[i]]
    portable <- if (exact) TRUE else portable_manifest_match(p, x$rel[[i]], x$sha256[[i]])
    stopifnot(isTRUE(exact || portable))
  }
  prior_total <- prior_total + nrow(x)
}
stopifnot(prior_total == 196L)

post <- paste(readLines(file.path(reports, "governance_post_correction_independent_review.md"), warn=FALSE), collapse=" ")
additional <- paste(readLines(file.path(reports, "governance_additional_post_correction_independent_review.md"), warn=FALSE), collapse=" ")
stopifnot(grepl("deleg_2e8d515e", post, fixed=TRUE), grepl('"passed": true', post, fixed=TRUE), grepl("deleg_eedc4116", additional, fixed=TRUE), grepl('"passed": true', additional, fixed=TRUE))
cat(sprintf("Phase 10 freeze R validation passed: %d final manifests, %d manifest entries, %d unique Phase 10 artifacts, %d prior Phase 1-9 protected artifacts; review records preserved\n", length(final_names), entries, length(unique(all_rel)), prior_total))
