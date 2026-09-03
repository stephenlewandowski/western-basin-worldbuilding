args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), "../../.."), mustWork=FALSE)
manifest_names <- c(
  "phase9a_climate_natural_hazards_freeze_manifest.json",
  "phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
  "phase9c_climate_hazard_futures_freeze_manifest.json"
)
expected_phase <- c("9A", "9B", "9C")
expected_counts <- c(13L, 14L, 21L)
expected_source <- "b5680aa9de0e17544c92cdfabe7b2d9e039f7f07"

sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stopifnot(length(out) >= 1)
    value <- tolower(strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1])
    return(sub("^\\\\", "", value))
  }
  certutil <- Sys.which("certutil")
  stopifnot(nchar(certutil) > 0)
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  normalized <- tolower(gsub("[[:space:]]+", "", out))
  hits <- normalized[grepl("^[0-9a-f]{64}$", normalized)]
  stopifnot(length(hits) >= 1)
  hits[[1]]
}

text_suffixes <- c(".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg")
canonical_raw <- function(raw) {
  charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
}
portable_manifest_match <- function(path, rel, expected) {
  if (tolower(tools::file_ext(path)) %in% sub("^\\.", "", text_suffixes)) {
    accepted_tmp <- tempfile(fileext=tools::file_ext(path))
    error_tmp <- tempfile()
    on.exit(unlink(c(accepted_tmp, error_tmp)), add=TRUE)
    status <- system2("git", c("-C", root, "show", paste0("HEAD:", rel)), stdout=accepted_tmp, stderr=error_tmp)
    if (!is.null(status) && status != 0) return(FALSE)
    accepted_raw <- readBin(accepted_tmp, "raw", n=as.numeric(file.info(accepted_tmp)$size))
    working_raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
    if (!identical(canonical_raw(accepted_raw), canonical_raw(working_raw))) return(FALSE)
    lf_tmp <- tempfile(fileext=tools::file_ext(path)); crlf_tmp <- tempfile(fileext=tools::file_ext(path))
    on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
    writeBin(canonical_raw(accepted_raw), lf_tmp)
    writeBin(charToRaw(gsub("\n", "\r\n", rawToChar(canonical_raw(accepted_raw)), fixed=TRUE)), crlf_tmp)
    return(expected %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp)))
  }
  FALSE
}

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE)
  current <- NA_character_; current_bytes <- NA_real_; rel <- character(); bytes <- numeric(); hashes <- character()
  for (line in lines) {
    direct <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    direct_hit <- regmatches(line, direct)[[1]]
    if (length(direct_hit) == 3 && grepl("/", direct_hit[[2]], fixed=TRUE)) {
      rel <- c(rel, direct_hit[[2]]); bytes <- c(bytes, NA_real_); hashes <- c(hashes, direct_hit[[3]])
      next
    }
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, m)[[1]]
    if (length(hit) == 2 && grepl("/", hit[[2]], fixed=TRUE)) current <- hit[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
    bh <- regmatches(line, b)[[1]]
    if (!is.na(current) && length(bh) == 2) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (!is.na(current) && length(hh) == 2) {
      rel <- c(rel, current); bytes <- c(bytes, current_bytes); hashes <- c(hashes, hh[[2]])
      current <- NA_character_; current_bytes <- NA_real_
    }
  }
  stopifnot(length(rel) == length(bytes), length(rel) == length(hashes))
  data.frame(rel=rel, bytes=bytes, sha256=hashes, stringsAsFactors=FALSE)
}

verify_manifest <- function(path, phase, expected_n) {
  txt <- paste(readLines(path, warn=FALSE), collapse="\n")
  stopifnot(grepl('"accepted_phase": "' %+% phase %+% '"', txt, fixed=TRUE))
  stopifnot(grepl('"status": "ACCEPTED / FROZEN"', txt, fixed=TRUE))
  stopifnot(grepl(expected_source, txt, fixed=TRUE))
  x <- manifest_artifacts(path)
  stopifnot(nrow(x) == expected_n)
  for (i in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[i]])
    stopifnot(file.exists(p), is.na(x$bytes[[i]]) || as.numeric(file.info(p)$size) == x$bytes[[i]], sha256_file(p) == x$sha256[[i]])
  }
  x$rel
}

`%+%` <- function(a, b) paste0(a, b)
all_rel <- character(); total <- 0L
for (i in seq_along(manifest_names)) {
  path <- file.path(root, "reports", manifest_names[[i]])
  stopifnot(file.exists(path))
  rel <- verify_manifest(path, expected_phase[[i]], expected_counts[[i]])
  stopifnot(length(intersect(all_rel, rel)) == 0L)
  all_rel <- c(all_rel, rel); total <- total + length(rel)
}
stopifnot(total == 48L)

map_bases <- c(
  "29_climate_natural_hazards_2026",
  "30_climate_hazard_dependencies_resilience_2026",
  "31_climate_hazard_futures_2050",
  "31b_climate_hazard_futures_2075"
)
for (base in map_bases) {
  png <- file.path(root, "outputs/maps/systems", paste0(base, ".png"))
  svg <- file.path(root, "outputs/maps/systems", paste0(base, ".svg"))
  stopifnot(file.exists(png), as.numeric(file.info(png)$size) > 1000, file.exists(svg), as.numeric(file.info(svg)$size) > 1000)
}

prior_names <- list.files(file.path(root, "reports"), pattern="^phase.*_freeze_manifest[.]json$", full.names=FALSE)
prior_names <- prior_names[!(prior_names %in% manifest_names)]
prior_total <- 0L
for (name in prior_names) {
  x <- manifest_artifacts(file.path(root, "reports", name))
  stopifnot(nrow(x) > 0)
  for (i in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[i]])
    stopifnot(file.exists(p))
    raw_match <- sha256_file(p) == x$sha256[[i]]
    portable_match <- if (raw_match) TRUE else portable_manifest_match(p, x$rel[[i]], x$sha256[[i]])
    if (!isTRUE(raw_match || portable_match)) stop(sprintf("prior manifest hash mismatch: %s expected %s got %s", x$rel[[i]], x$sha256[[i]], sha256_file(p)))
  }
  prior_total <- prior_total + nrow(x)
}
stopifnot(prior_total == 148L)
cat(sprintf("Phase 9 freeze R validation passed: %d manifests, %d protected artifacts, %d prior Phase 1-8 artifacts, maps valid\n", length(manifest_names), total, prior_total))
