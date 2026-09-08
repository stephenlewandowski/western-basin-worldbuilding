args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
analysis <- file.path(root, "data", "processed", "analysis")
networks <- file.path(root, "data", "processed", "networks")
maps <- file.path(root, "outputs", "maps", "systems")
source_commit <- "e158740aa35f31d2155a9906a3bc2c5529fb5147"
final_names <- c("phase12a_vector_ecology_freeze_manifest.json", "phase12b_vector_environment_human_dependencies_freeze_manifest.json")
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_csv <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
text_col <- function(x) ifelse(is.na(x), "", as.character(x))
frame_text <- function(x) tolower(paste(vapply(x, function(col) paste(text_col(col), collapse=" "), character(1)), collapse=" "))
raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_bytes <- function(raw) charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))

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

sha256_bytes <- function(bytes, suffix=".bin") {
  tmp <- tempfile(fileext=suffix); on.exit(unlink(tmp), add=TRUE); writeBin(bytes, tmp); sha256_file(tmp)
}

manifest_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) {
      rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes)
    }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit)==3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit)==2L) { append_current(); current <- hit[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bh <- regmatches(line, b)[[1]]
    if (length(bh)==2L && !is.na(current)) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}

portable_final_match <- function(path, expected, expected_bytes) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing final artifact", path))
  raw <- raw_bytes(path); ext <- tolower(tools::file_ext(path))
  if (ext %in% text_ext) {
    canonical <- canonical_bytes(raw); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
    hashes <- c(sha256_bytes(raw, paste0(".", ext)), sha256_bytes(canonical, paste0(".", ext)), sha256_bytes(crlf, paste0(".", ext)))
    return(expected %in% hashes && expected_bytes %in% c(length(raw), length(canonical), length(crlf)))
  }
  expected_bytes == length(raw) && sha256_file(path) == expected
}

portable_against_head <- function(path, relative, expected) {
  stop_if(file.exists(path), paste("missing prior artifact", relative))
  if (sha256_file(path) == expected) return(TRUE)
  if (!(tolower(tools::file_ext(path)) %in% text_ext)) return(FALSE)
  accepted_tmp <- tempfile(); err_tmp <- tempfile(); on.exit(unlink(c(accepted_tmp, err_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", relative)), stdout=accepted_tmp, stderr=err_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted <- raw_bytes(accepted_tmp); working <- raw_bytes(path)
  if (!identical(canonical_bytes(accepted), canonical_bytes(working))) return(FALSE)
  lf <- canonical_bytes(accepted); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(lf), fixed=TRUE))
  expected %in% c(sha256_bytes(accepted_tmp), sha256_bytes(lf, ".txt"), sha256_bytes(crlf, ".txt"))
}

verify_final <- function(name, phase, baseline, counts, expected) {
  path <- file.path(reports, name); stop_if(file.exists(path), paste("missing final manifest", name))
  txt <- manifest_text(path)
  for (term in c(paste0('"accepted_phase": "', phase, '"'), paste0('"baseline": "', baseline, '"'), '"status": "ACCEPTED / FROZEN"', '"accepted_by": "Sol explicit acceptance decision supplied for this run"', '"accepted_date": "2026-09-08"', paste0('"source_commit": "', source_commit, '"'))) stop_if(grepl(term, txt, fixed=TRUE), paste(name, term))
  for (nm in names(counts)) stop_if(grepl(paste0('"', nm, '":[[:space:]]*', counts[[nm]]), txt, perl=TRUE), paste(name, nm))
  x <- manifest_artifacts(path)
  stop_if(nrow(x)==length(expected) && setequal(x$rel, expected), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_final_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x$rel
}

working_manifest <- function(relative, phase, expected_n) {
  txt <- manifest_text(file.path(root, relative))
  stop_if(grepl(paste0('"phase": "', phase, '"'), txt, fixed=TRUE) && grepl('"status": "implemented_validated_pending_sol_acceptance"', txt, fixed=TRUE) && grepl('"phase12c_implemented": false', txt, fixed=TRUE) && grepl('"phase13_implemented": false', txt, fixed=TRUE), paste("working manifest", relative))
  x <- manifest_artifacts(file.path(root, relative)); stop_if(nrow(x)==expected_n, paste("working manifest count", relative))
  for (i in seq_len(nrow(x))) stop_if(portable_against_head(file.path(root, x$rel[[i]]), x$rel[[i]], x$sha256[[i]]), paste("working artifact", x$rel[[i]]))
  nrow(x)
}

verify_prior <- function(excluded) {
  paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
  paths <- paths[!(basename(paths) %in% final_names)]
  hashes <- character(); protected <- character(); total <- 0L
  for (path in sort(paths)) {
    x <- manifest_artifacts(path)
    for (i in seq_len(nrow(x))) {
      rel <- x$rel[[i]]; expected <- x$sha256[[i]]
      if (rel %in% names(hashes)) stop_if(unname(hashes[[rel]])==expected, paste("conflicting prior hash", rel))
      hashes[rel] <- expected
      stop_if(portable_against_head(file.path(root, rel), rel, expected), paste("prior artifact", rel))
      protected <- c(protected, rel); total <- total + 1L
    }
  }
  stop_if(total==298L && length(unique(protected))==293L, "prior Phase 1–11 inventory")
  stop_if(!any(excluded %in% protected), "current/prior artifact overlap")
  changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)
  stop_if(!any(changed %in% protected), "prior protected artifact changed")
  list(entries=total, unique=length(unique(protected)))
}

A <- read_csv(file.path(networks, "vector_ecology_nodes.csv")); E <- read_csv(file.path(networks, "vector_ecology_edges.csv"))
V <- read_csv(file.path(analysis, "vector_surveillance_records.csv")); H <- read_csv(file.path(analysis, "vector_habitat_associations.csv"))
S <- read_csv(file.path(analysis, "vector_ecology_sources.csv")); U <- read_csv(file.path(analysis, "vector_ecology_uncertainty.csv"))
D <- read_csv(file.path(analysis, "vector_system_dependency_register.csv")); DE <- read_csv(file.path(networks, "vector_system_dependency_edges.csv"))
M <- read_csv(file.path(analysis, "vector_system_dependency_matrix.csv")); X <- read_csv(file.path(analysis, "vector_dependency_evidence.csv"))
stop_if(nrow(A)==20L && nrow(E)==26L && nrow(V)==36L && nrow(H)==15L && nrow(S)==27L && nrow(U)==10L && nrow(D)==28L && nrow(DE)==28L && nrow(M)==8L && nrow(X)==8L, "Phase 12 counts")
stop_if(!anyDuplicated(A$node_id) && !anyDuplicated(E$edge_id) && !anyDuplicated(V$record_id) && !anyDuplicated(H$association_id) && !anyDuplicated(S$source_id) && !anyDuplicated(U$uncertainty_id) && !anyDuplicated(D$dependency_id) && !anyDuplicated(M$object_id) && !anyDuplicated(X$evidence_id), "unique IDs")
stop_if(identical(A$source_id %in% S$source_id, rep(TRUE, nrow(A))) && identical(E$source_id %in% S$source_id, rep(TRUE, nrow(E))) && identical(V$source_id %in% S$source_id, rep(TRUE, nrow(V))) && identical(D$source_id %in% S$source_id, rep(TRUE, nrow(D))) && identical(X$source_id %in% S$source_id, rep(TRUE, nrow(X))), "source references")
stop_if(identical(as.matrix(D), as.matrix(DE)), "register/edge equality")
fields <- unique(c(names(A),names(E),names(V),names(H),names(U),names(D),names(M),names(X)))
forbidden <- c("infection_probability","disease_risk_score","risk_score","vulnerability_score","ej_score","dose","contact_probability","abundance_surface")
stop_if(!any(forbidden %in% fields), "forbidden analytical fields")
all_text <- tolower(paste(frame_text(A), frame_text(E), frame_text(V), frame_text(H), frame_text(U), frame_text(D), frame_text(M), frame_text(X), collapse=" "))
for (term in c("presence != abundance","sampling effort","not abundance","detection","establishment","not absence","positive vector pool","human case","local transmission","not exposure")) stop_if(grepl(term, all_text, fixed=TRUE), paste("boundary", term))
stop_if(!grepl("2050|2075", all_text, perl=TRUE), "future contamination")
ix <- S[S$source_id=="v12_cdc_ixodes", , drop=FALSE]
stop_if(nrow(ix)==1L && ix$url[[1]]=="https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html" && ix$retrieval_url[[1]]=="https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx" && grepl("not CDC-hosted", ix$retrieval_provenance[[1]], fixed=TRUE) && grepl("HTTP 403", ix$retrieval_provenance[[1]], fixed=TRUE), "CDC provenance")

for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("phase 12a", txt, fixed=TRUE) && grepl("phase 12b", txt, fixed=TRUE) && grepl("accepted / frozen", txt, fixed=TRUE) && grepl("phase 12c", txt, fixed=TRUE) && grepl("approved scope", txt, fixed=TRUE) && grepl("not implemented", txt, fixed=TRUE) && grepl("active phase", txt, fixed=TRUE) && grepl("none", txt, fixed=TRUE) && grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE) && grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("status", rel))
}
review <- tolower(paste(readLines(file.path(reports, "phase12_independent_review.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"ecological_errors": []','"surveillance_errors": []','"spatial_scale_errors": []','"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))

# Map signature, XML parse, and required caveat text are checked independently from Python.
for (spec in list(c("38_vector_ecology_baseline_2026", "map 38", "vector ecology", "surveillance boundary", "presence", "abundance", "positive vector pool"), c("39_vector_environment_human_dependencies_2026", "map 39", "vector", "environment", "human-system", "surveillance", "not continuous", "not exposure"))) {
  png <- file.path(maps, paste0(spec[[1]], ".png")); svg <- file.path(maps, paste0(spec[[1]], ".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && identical(paste(sprintf("%02x", as.integer(readBin(png, "raw", n=8))), collapse=""), "89504e470d0a1a0a"), paste("PNG", spec[[1]]))
  xmllint <- Sys.which("xmllint"); stop_if(nzchar(xmllint), "xmllint")
  status <- system2(xmllint, c("--noout", svg), stdout=FALSE, stderr=FALSE); stop_if(is.null(status) || status==0, paste("SVG", spec[[1]]))
  svg_text <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in spec[-1]) stop_if(grepl(term, svg_text, fixed=TRUE), paste("map text", spec[[1]], term))
}

expected_a <- c("data/processed/networks/vector_ecology_nodes.csv","data/processed/networks/vector_ecology_edges.csv","data/processed/analysis/vector_surveillance_records.csv","data/processed/analysis/vector_habitat_associations.csv","data/processed/analysis/vector_ecology_sources.csv","data/processed/analysis/vector_ecology_uncertainty.csv","outputs/maps/systems/38_vector_ecology_baseline_2026.png","outputs/maps/systems/38_vector_ecology_baseline_2026.svg","reports/vector_ecology_sources.md","reports/vector_ecology_assumptions.md","reports/vector_ecology_findings.md","reports/vector_ecology_qa.md","data/raw/vector_ecology/Public_Use_Ixodes_County_Table_2024_summary.xlsx","reports/phase12_citation_ledger.json","reports/phase12_working_manifest.json","reports/vector_ecology_artifact_check.json","reports/phase12_independent_review.md")
expected_b <- c("data/processed/analysis/vector_system_dependency_register.csv","data/processed/networks/vector_system_dependency_edges.csv","data/processed/analysis/vector_system_dependency_matrix.csv","data/processed/analysis/vector_dependency_evidence.csv","outputs/maps/systems/39_vector_environment_human_dependencies_2026.png","outputs/maps/systems/39_vector_environment_human_dependencies_2026.svg","reports/vector_dependency_sources.md","reports/vector_dependency_assumptions.md","reports/vector_dependency_findings.md","reports/vector_dependency_qa.md","reports/vector_dependency_artifact_check.json","reports/phase12_working_manifest.json","reports/phase12_independent_review.md","src/python/systems/validate_phase12_freezes.py","src/R/systems/validate_phase12_freezes.R")
a_paths <- verify_final(final_names[[1]], "12A", "Vector Ecology Baseline, 2026", c(nodes=20L, edges=26L, surveillance_records=36L, habitat_associations=15L, sources=27L, uncertainties=10L), expected_a)
b_paths <- verify_final(final_names[[2]], "12B", "Vector / Environment / Human-System Dependencies, 2026", c(dependency_register=28L, dependency_edges=28L, matrix_rows=8L, evidence_rows=8L, sources_reused=27L), expected_b)
b_txt <- manifest_text(file.path(reports, final_names[[2]])); a_path <- file.path(reports, final_names[[1]])
stop_if(grepl(paste0('"sha256": "', sha256_bytes(canonical_bytes(raw_bytes(a_path)), ".json"), '"'), b_txt, fixed=TRUE), "Phase 12A final-manifest hash")
stop_if(grepl(paste0('"bytes": ', length(canonical_bytes(raw_bytes(a_path)))), b_txt, fixed=TRUE), "Phase 12A final-manifest bytes")
wa <- working_manifest("reports/vector_ecology_baseline_manifest.json", "12A", 14L); wb <- working_manifest("reports/vector_dependency_manifest.json", "12B", 10L)
prior <- verify_prior(c(a_paths, b_paths, "reports/phase12a_vector_ecology_freeze_manifest.json", "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json"))
cat(sprintf("Phase 12 final R freeze validation passed: 12A %d protected artifacts, 12B %d protected artifacts; working manifests 14/10; 20 nodes, 26 edges, 36 surveillance/context records, 15 habitat associations, 27 sources, 10 uncertainties; 28 dependency rows/edges, 8 matrix rows, 8 evidence rows; Phase 1–11 immutability %d entries/%d unique artifacts; maps, review, provenance, boundaries, holds, and Phase 12C/13 absence checked\n", length(a_paths), length(b_paths), prior$entries, prior$unique))
