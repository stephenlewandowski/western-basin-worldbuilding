args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
analysis <- file.path(root, "data", "processed", "analysis")
networks <- file.path(root, "data", "processed", "networks")
maps <- file.path(root, "outputs", "maps", "systems")
raw_dir <- file.path(root, "data", "raw", "vector_ecology")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_csv <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
text_col <- function(x) ifelse(is.na(x), "", as.character(x))
frame_text <- function(x) tolower(paste(vapply(x, function(col) paste(text_col(col), collapse=" "), character(1)), collapse=" "))

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
  hits <- tolower(gsub("[[:space:]]+", "", out))
  hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path))
  hits[[1]]
}

raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_bytes <- function(raw) charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg")

portable_match <- function(path, relative, expected) {
  stop_if(file.exists(path), paste("missing artifact", relative))
  if (sha256_file(path) == expected) return(TRUE)
  if (!(tolower(tools::file_ext(path)) %in% text_ext)) return(FALSE)
  accepted_tmp <- tempfile(); err_tmp <- tempfile()
  on.exit(unlink(c(accepted_tmp, err_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", relative)), stdout=accepted_tmp, stderr=err_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted <- raw_bytes(accepted_tmp)
  working <- raw_bytes(path)
  if (!identical(canonical_bytes(accepted), canonical_bytes(working))) return(FALSE)
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  lf <- canonical_bytes(accepted)
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(lf), fixed=TRUE))
  writeBin(lf, lf_tmp); writeBin(crlf, crlf_tmp)
  expected %in% c(sha256_file(accepted_tmp), sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

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
    direct_obj <- regexec('"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{[^}]*"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct_obj)[[1]]
    if (length(hit) == 3L) {
      b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
      bh <- regmatches(line, b)[[1]]
      rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]])
      bytes <- c(bytes, if (length(bh) == 2L) as.numeric(bh[[2]]) else NA_real_)
      next
    }
    direct_string <- regexec('"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct_string)[[1]]
    if (length(hit) == 3L) {
      rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next
    }
    path_hit <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    ph <- regmatches(line, path_hit)[[1]]
    if (length(ph) == 2L) { append_current(); current <- ph[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
    bh <- regmatches(line, b)[[1]]
    if (length(bh) == 2L && !is.na(current)) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh) == 2L && !is.na(current)) current_hash <- hh[[2]]
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}

verify_manifest <- function(path, expected_n) {
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == expected_n, paste("manifest artifact count", basename(path)))
  for (i in seq_len(nrow(x))) {
    stop_if(portable_match(file.path(root, x$rel[[i]]), x$rel[[i]], x$sha256[[i]]), paste("manifest artifact", x$rel[[i]]))
  }
  nrow(x)
}

check_prior_freezes <- function() {
  paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
  expected <- character(); total <- 0L
  statuses <- character()
  for (path in sort(paths)) {
    lines <- readLines(path, warn=FALSE, encoding="UTF-8")
    status_hit <- regexec('"status"[[:space:]]*:[[:space:]]*"([^"]*)"', paste(lines, collapse=" "), perl=TRUE)
    status_match <- regmatches(paste(lines, collapse=" "), status_hit)[[1]]
    statuses <- c(statuses, if (length(status_match) == 2L) status_match[[2]] else "")
    x <- manifest_artifacts(path)
    stop_if(nrow(x) > 0L, paste("empty prior manifest", basename(path)))
    for (i in seq_len(nrow(x))) {
      rel <- x$rel[[i]]; hash <- x$sha256[[i]]
      if (rel %in% names(expected)) stop_if(unname(expected[[rel]]) == hash, paste("conflicting prior hash", rel))
      expected[rel] <- hash
      stop_if(portable_match(file.path(root, rel), rel, hash), paste("prior artifact", rel))
      total <- total + 1L
    }
  }
  list(entries=total, unique=length(expected), statuses=statuses, manifests=length(paths))
}

check_png <- function(path) {
  stop_if(file.exists(path) && file.info(path)$size > 10000, paste("PNG", basename(path)))
  raw <- readBin(path, "raw", n=8)
  hex <- paste(sprintf("%02x", as.integer(raw)), collapse="")
  stop_if(hex == "89504e470d0a1a0a", paste("PNG signature", basename(path)))
}

check_svg <- function(path, terms, label) {
  stop_if(file.exists(path) && file.info(path)$size > 10000, paste("SVG", label))
  xmllint <- Sys.which("xmllint")
  stop_if(nzchar(xmllint), "xmllint is required for independent SVG parsing")
  status <- system2(xmllint, c("--noout", path), stdout=FALSE, stderr=FALSE)
  stop_if(is.null(status) || status == 0, paste("SVG parse", label))
  txt <- tolower(paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in terms) stop_if(grepl(tolower(term), txt, fixed=TRUE), paste("SVG text", label, term))
}

N <- read_csv(file.path(networks, "vector_ecology_nodes.csv"))
E <- read_csv(file.path(networks, "vector_ecology_edges.csv"))
V <- read_csv(file.path(analysis, "vector_surveillance_records.csv"))
H <- read_csv(file.path(analysis, "vector_habitat_associations.csv"))
S <- read_csv(file.path(analysis, "vector_ecology_sources.csv"))
U <- read_csv(file.path(analysis, "vector_ecology_uncertainty.csv"))

expected_names <- list(
  N=c("node_id","name","node_type","vector_group","taxon_or_system","habitat_context","seasonality","geographic_scale","latitude","longitude","source_id","evidence_status","confidence","reality_status","canon_status","notes"),
  E=c("edge_id","from_id","to_id","relationship_type","relationship_basis","geographic_scale","source_id","evidence_status","confidence","reality_status","canon_status","notes"),
  V=c("record_id","year","vector_group","species_or_vector","pathogen","surveillance_program","surveillance_method","geographic_area","geographic_scale","sampling_effort","detection_status","observed_value","units","source_id","evidence_status","confidence","uncertainty_notes","notes"),
  H=c("association_id","vector_or_group","association_type","environment_or_host","relationship_description","season_or_period","geographic_scale","evidence_status","source_id","confidence","notes"),
  S=c("source_id","title","url","source_type","publication_or_period","retrieval_date","geographic_scale","method_or_product","evidence_use","use_limitations","retrieval_url","retrieval_provenance"),
  U=c("uncertainty_id","subject_id","category","statement","resolution_status","source_id","confidence","notes")
)
for (nm in names(expected_names)) stop_if(setequal(names(get(nm)), expected_names[[nm]]), paste("schema", nm))
stop_if(nrow(N)==20L && nrow(E)==26L && nrow(V)==36L && nrow(H)==15L && nrow(S)==27L && nrow(U)==10L, "Phase 12A counts")
stop_if(!anyDuplicated(text_col(N$node_id)) && !anyDuplicated(text_col(E$edge_id)) && !anyDuplicated(text_col(V$record_id)) && !anyDuplicated(text_col(H$association_id)) && !anyDuplicated(text_col(S$source_id)) && !anyDuplicated(text_col(U$uncertainty_id)), "Phase 12A unique IDs")
stop_if(all(grepl("^VEC-[0-9]{3}$", text_col(N$node_id))), "node IDs")
stop_if(all(grepl("^VEE-[0-9]{3}$", text_col(E$edge_id))), "edge IDs")
source_ids <- text_col(S$source_id); node_ids <- text_col(N$node_id)
stop_if(all(text_col(N$source_id) %in% source_ids) && all(text_col(E$source_id) %in% source_ids) && all(text_col(V$source_id) %in% source_ids) && all(text_col(H$source_id) %in% source_ids) && all(text_col(U$source_id) %in% source_ids), "source references")
stop_if(all(text_col(E$from_id) %in% node_ids) && all(text_col(E$to_id) %in% node_ids) && all(text_col(U$subject_id) %in% node_ids), "node references")
stop_if(all(text_col(N$node_type) %in% c("vector_taxon","habitat_context","host_ecology","environmental_driver","surveillance_program","pathogen_context")), "node types")
stop_if(all(text_col(N$reality_status)=="real") && all(text_col(N$canon_status) %in% c("verified","inferred")), "node status")
stop_if(all(text_col(E$relationship_basis) %in% c("documented_source","documented_plus_inferred","accepted_layer","project_boundary","project_inference","documented_program","accepted_ecology_context")), "edge basis")
stop_if(all(text_col(N$confidence) %in% c("high","moderate","limited","unknown")) && all(text_col(E$confidence) %in% c("high","moderate","limited","unknown")), "confidence vocabulary")

human <- V[text_col(V$vector_group)=="human-case-context", , drop=FALSE]
ticks <- V[grepl("^VS-TICK-", text_col(V$record_id)), , drop=FALSE]
stop_if(nrow(human)==2L && all(grepl("context only", text_col(human$notes), ignore.case=TRUE)) && all(grepl("reported", text_col(human$detection_status), ignore.case=TRUE)), "human-case separation")
stop_if(!any(grepl("trap|pool", text_col(human$surveillance_method), ignore.case=TRUE)), "human rows are not vector samples")
stop_if(nrow(ticks)==18L && all(text_col(ticks$geographic_scale)=="county") && all(text_col(ticks$detection_status) %in% c("established","reported","no records (not absence)")), "tick status separation")
stop_if(all(grepl("no records", text_col(ticks$uncertainty_notes), ignore.case=TRUE)) && all(grepl("not abundance", text_col(ticks$notes), ignore.case=TRUE)), "tick no-record boundary")
stop_if(all(grepl("not reported", text_col(ticks$sampling_effort), ignore.case=TRUE)), "tick effort limitation")
stop_if(all(nchar(text_col(V$surveillance_method)) > 0) && all(nchar(text_col(V$geographic_scale)) > 0) && all(nchar(text_col(V$sampling_effort)) > 0) && all(nchar(text_col(V$detection_status)) > 0) && all(nchar(text_col(V$uncertainty_notes)) > 0), "surveillance fields")
stop_if(all(text_col(V$year) %in% c("2023","2025","2026")), "surveillance years")

all_text <- tolower(paste(frame_text(N), frame_text(E), frame_text(V), frame_text(H), frame_text(U), collapse=" "))
forbidden <- c("abundance_index","abundance_score","risk_score","infection_probability","disease_incidence_forecast","hospitalization","mortality","dose","vulnerability_score","ej_score","contact_probability")
stop_if(!any(forbidden %in% unique(c(names(N),names(E),names(V),names(H),names(S),names(U)))), "forbidden analytical columns")
stop_if(grepl("presence != abundance", all_text, fixed=TRUE) && grepl("sampling effort", all_text, fixed=TRUE) && grepl("not abundance", all_text, fixed=TRUE), "presence/abundance boundary")
stop_if(grepl("detection", all_text, fixed=TRUE) && grepl("establishment", all_text, fixed=TRUE) && grepl("county record", all_text, fixed=TRUE), "detection/scale boundaries")
stop_if(grepl("positive vector pool", all_text, fixed=TRUE) && grepl("human case", all_text, fixed=TRUE) && grepl("local transmission", all_text, fixed=TRUE), "pathogen/case boundaries")
stop_if(grepl("not absence", all_text, fixed=TRUE) && grepl("participating jurisdictions and methods vary", all_text, fixed=TRUE), "surveillance limitations")
stop_if(!grepl("(?:risk score|infection probability|disease incidence|vulnerability score|ej score)[[:space:]]*[,=:][[:space:]]*[0-9]", all_text, perl=TRUE), "unsupported positive health metric")
stop_if(!grepl("\\b(?:2050|2075)\\b", all_text, perl=TRUE), "Phase 12A future contamination")

ix <- S[text_col(S$source_id)=="v12_cdc_ixodes", , drop=FALSE]
stop_if(nrow(ix)==1L && ix$url[[1]]=="https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html", "CDC original source-page provenance")
stop_if(nrow(ix)==1L && ix$retrieval_url[[1]]=="https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx", "mirror retrieval URL")
stop_if(nrow(ix)==1L && grepl("not CDC-hosted", ix$retrieval_provenance[[1]], fixed=TRUE) && grepl("HTTP 403", ix$retrieval_provenance[[1]], fixed=TRUE), "mirror provenance qualification")
stop_if(nrow(ix)==1L && all(text_col(S$retrieval_url)[text_col(S$source_id)!="v12_cdc_ixodes"]==""), "single retrieval provenance row")
raw_tick <- file.path(raw_dir, "Public_Use_Ixodes_County_Table_2024_summary.xlsx")
stop_if(file.exists(raw_tick) && file.info(raw_tick)$size > 1000, "cached Ixodes workbook")
manifest_note <- paste(readLines(file.path(reports, "vector_ecology_baseline_manifest.json"), warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl("https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html", manifest_note, fixed=TRUE) && grepl("https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx", manifest_note, fixed=TRUE) && grepl("not CDC-hosted", manifest_note, fixed=TRUE), "manifest retrieval provenance")

for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE) && grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("holds", rel))
}
for (name in c("phase11a_population_settlement_freeze_manifest.json","phase11b_population_mobility_dependencies_freeze_manifest.json","phase11c_population_settlement_futures_freeze_manifest.json")) {
  txt <- paste(readLines(file.path(reports, name), warn=FALSE, encoding="UTF-8"), collapse=" ")
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("Phase 11 status", name))
}

check_png(file.path(maps, "38_vector_ecology_baseline_2026.png"))
check_svg(file.path(maps, "38_vector_ecology_baseline_2026.svg"), c("map 38","vector ecology","culex","aedes","ixodes","surveillance boundary","presence","abundance","positive vector pool","not vector collection"), "Map 38")
prior <- check_prior_freezes()
stop_if(prior$entries == 298L && prior$unique == 293L, "prior freeze inventory")
manifest_n <- verify_manifest(file.path(reports, "vector_ecology_baseline_manifest.json"), 14L)
manifest <- paste(readLines(file.path(reports, "vector_ecology_baseline_manifest.json"), warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"12A"', manifest, perl=TRUE) && grepl('"phase12c_implemented"[[:space:]]*:[[:space:]]*false', manifest, perl=TRUE) && grepl('"phase13_implemented"[[:space:]]*:[[:space:]]*false', manifest, perl=TRUE), "Phase 12A manifest boundary")

paths <- list.files(file.path(root, "data", "processed"), recursive=TRUE, full.names=TRUE)
paths <- c(paths, list.files(maps, full.names=TRUE), list.files(file.path(root, "src", "R", "systems"), full.names=TRUE))
bad <- paths[grepl("phase13|vector.*future|future.*vector|/40_|\\\\40_", tolower(paths))]
stop_if(length(bad)==0L, "later-phase artifacts")

cat(sprintf("Phase 12A R validation passed: %d nodes, %d edges, %d surveillance/context records, %d habitat associations, %d sources, %d uncertainties; Map 38 parsed; independently checked %d prior manifest entries/%d unique protected artifacts; CDC source-page/mirror provenance, surveillance limitations, boundaries, and Phase 12C/13 absence verified\n", nrow(N), nrow(E), nrow(V), nrow(H), nrow(S), nrow(U), prior$entries, prior$unique))
