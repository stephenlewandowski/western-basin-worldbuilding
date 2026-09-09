args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
networks <- file.path(root, "data", "processed", "networks")
analysis <- file.path(root, "data", "processed", "analysis")
maps <- file.path(root, "outputs", "maps", "systems")
reports <- file.path(root, "reports")
text_ext <- c("csv", "json", "md", "svg", "txt", "yml", "yaml", "py", "r")

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
recorded_bytes_match <- function(path, recorded) {
  raw <- raw_bytes(path); ext <- tolower(tools::file_ext(path))
  if (!(ext %in% text_ext)) return(length(raw) == recorded)
  canonical <- canonical_bytes(raw); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  recorded %in% c(length(raw), length(canonical), length(crlf))
}

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"[[:space:]]*:[[:space:]]*\\{'), lines, perl=TRUE))[1]
  stop_if(!is.na(start), paste("missing artifacts", path))
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  for (line in lines[(start+1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    inline <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{[^}]*"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"[^}]*', line, perl=TRUE))[[1]]
    if (length(inline)==3L) {
      bb <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE))[[1]]
      rel <- c(rel, inline[[2]]); hashes <- c(hashes, inline[[3]]); bytes <- c(bytes, if (length(bb)==2L) as.numeric(bb[[2]]) else NA_real_); next
    }
    direct <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE))[[1]]
    if (length(direct)==3L) { append_current(); rel <- c(rel, direct[[2]]); hashes <- c(hashes, direct[[3]]); bytes <- c(bytes, NA_real_); next }
    ph <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE))[[1]]
    if (length(ph)==2L) { append_current(); current <- ph[[2]]; next }
    hh <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE))[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
    bb <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE))[[1]]
    if (length(bb)==2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}

portable_against_head <- function(path, relative, expected) {
  stop_if(file.exists(path), paste("missing protected artifact", relative))
  if (sha256_file(path) == expected) return(TRUE)
  ext <- tolower(tools::file_ext(path)); if (!(ext %in% text_ext)) return(FALSE)
  accepted_tmp <- tempfile(); err_tmp <- tempfile(); on.exit(unlink(c(accepted_tmp, err_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", relative)), stdout=accepted_tmp, stderr=err_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted <- raw_bytes(accepted_tmp); working <- raw_bytes(path)
  if (!identical(canonical_bytes(accepted), canonical_bytes(working))) return(FALSE)
  lf <- canonical_bytes(accepted); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(lf), fixed=TRUE))
  expected %in% c(sha256_file(accepted_tmp), sha256_raw(lf, paste0(".", ext)), sha256_raw(crlf, paste0(".", ext)))
}

verify_current_manifest <- function(path, expected_n) {
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == expected_n, paste("manifest artifact count", basename(path)))
  for (i in seq_len(nrow(x))) {
    artifact <- file.path(root, x$rel[[i]])
    stop_if(file.exists(artifact) && file.info(artifact)$size > 0, paste("manifest artifact", x$rel[[i]]))
    stop_if(portable_against_head(artifact, x$rel[[i]], x$sha256[[i]]), paste("manifest hash", x$rel[[i]]))
    stop_if(recorded_bytes_match(artifact, x$bytes[[i]]), paste("manifest bytes", x$rel[[i]]))
  }
  x$rel
}

N <- read_csv(file.path(networks, "infectious_disease_nodes.csv"))
R <- read_csv(file.path(networks, "infectious_disease_transmission_relationships.csv"))
O <- read_csv(file.path(analysis, "infectious_disease_observations.csv"))
V <- read_csv(file.path(analysis, "infectious_disease_surveillance.csv"))
S <- read_csv(file.path(analysis, "infectious_disease_sources.csv"))
U <- read_csv(file.path(analysis, "infectious_disease_uncertainties.csv"))
expected <- list(
  N=c("node_id","name","node_class","disease_group","pathogen_or_agent","transmission_pathway","environment_or_host_interface","geographic_scale","latitude","longitude","source_id","evidence_status","confidence","reality_status","canon_status","notes"),
  R=c("relationship_id","from_id","to_id","relationship_type","relationship_basis","geographic_scale","evidence_status","source_id","confidence","reality_status","canon_status","notes"),
  O=c("observation_id","system_node_id","observation_type","reporting_year_or_period","geography","geographic_scale","observed_value","units","reporting_basis","numerator","denominator","case_definition_or_surveillance_definition","residence_or_exposure_basis","observed_estimated_modeled","source_id","evidence_status","confidence","uncertainty_notes","notes"),
  V=c("surveillance_id","disease_or_pathogen","reporting_period","geography","surveillance_system","case_definition_or_surveillance_definition","reporting_basis","numerator","denominator","case_geography_basis","exposure_geography_basis","suppression_missingness","source_id","confidence","uncertainty","notes"),
  S=c("source_id","title","url","source_type","publication_or_period","retrieval_date","geographic_scale","method_or_product","evidence_use","use_limitations","retrieval_url","retrieval_provenance"),
  U=c("uncertainty_id","subject_id","category","statement","resolution_status","source_id","confidence","notes")
)
for (nm in names(expected)) stop_if(setequal(names(get(nm)), expected[[nm]]), paste("schema", nm))
stop_if(nrow(N)==38L && nrow(R)==40L && nrow(O)==25L && nrow(V)==17L && nrow(S)==27L && nrow(U)==18L, "Phase 13A counts")
stop_if(!anyDuplicated(N$node_id) && !anyDuplicated(R$relationship_id) && !anyDuplicated(O$observation_id) && !anyDuplicated(V$surveillance_id) && !anyDuplicated(S$source_id) && !anyDuplicated(U$uncertainty_id), "unique IDs")
source_ids <- text_col(S$source_id); node_ids <- text_col(N$node_id)
stop_if(all(text_col(N$source_id) %in% source_ids) && all(text_col(R$source_id) %in% source_ids) && all(text_col(O$source_id) %in% source_ids) && all(text_col(V$source_id) %in% source_ids) && all(text_col(U$source_id) %in% source_ids), "source references")
stop_if(all(text_col(R$from_id) %in% node_ids) && all(text_col(R$to_id) %in% node_ids) && all(text_col(O$system_node_id) %in% node_ids) && all(text_col(U$subject_id) %in% node_ids), "node references")
stop_if(all(text_col(N$node_class) %in% c("disease_system","surveillance_system","environmental_interface","host_interface","institutional_response_interface","boundary_interface","accepted_layer_reference")), "node class vocabulary")
stop_if(all(text_col(N$reality_status)=="real") && all(text_col(R$reality_status)=="real"), "baseline status")
stop_if(all(text_col(R$relationship_basis) %in% c("documented_source","accepted_layer","documented_plus_inferred","project_boundary","project_inference")), "relationship basis")
stop_if(all(text_col(N$confidence) %in% c("high","moderate","limited","unknown")) && all(text_col(R$confidence) %in% c("high","moderate","limited","unknown")) && all(text_col(O$confidence) %in% c("high","moderate","limited","unknown")) && all(text_col(V$confidence) %in% c("high","moderate","limited","unknown")), "confidence vocabulary")
stop_if(all(nchar(text_col(V$reporting_period))>0) && all(nchar(text_col(V$case_definition_or_surveillance_definition))>0) && all(nchar(text_col(V$reporting_basis))>0) && all(nchar(text_col(V$numerator))>0) && all(nchar(text_col(V$denominator))>0) && all(nchar(text_col(V$case_geography_basis))>0) && all(nchar(text_col(V$exposure_geography_basis))>0) && all(nchar(text_col(V$suppression_missingness))>0), "surveillance metadata")
stop_if(all(nchar(text_col(S$retrieval_url))>0) && all(nchar(text_col(S$retrieval_provenance))>0), "source provenance")

all_text <- tolower(paste(frame_text(N), frame_text(R), frame_text(O), frame_text(V), frame_text(U), collapse=" "))
fields <- unique(c(names(N),names(R),names(O),names(V),names(S),names(U)))
forbidden <- c("risk_score","disease_risk_score","composite_disease_risk_index","vulnerability_score","ej_score","individual_risk","infection_probability","outbreak_probability","transmission_rate","disease_burden_index","exposure_probability","dose")
stop_if(length(intersect(fields, forbidden))==0L, "forbidden analytical fields")
for (term in c("pathogen","exposure","infection","reported case","local transmission","outbreak","disease burden","surveillance intensity","incidence","place of exposure","pathogen absence","neighborhood","vector detection","human infection","positive vector","human case","source-water","treatment failure","illness","case count","transmission rate","testing intensity","disease intensity","hospitalization","community incidence")) stop_if(grepl(term, all_text, fixed=TRUE), paste("boundary", term))
for (term in c("not a continuous incidence","not a disease-risk","not a transmission rate","not a human infection","not local transmission","not a composite","not a risk surface")) stop_if(grepl(term, all_text, fixed=TRUE), paste("negative scope", term))
stop_if(!grepl("(?:risk score|disease risk score|infection probability|outbreak probability|transmission rate|disease burden index|vulnerability score|ej score)[[:space:]]*[,=:][[:space:]]*[0-9]", all_text, perl=TRUE), "unsupported positive metric")
stop_if(!grepl("\\b(?:2050|2075)\\b", all_text, perl=TRUE), "future rows")
stop_if(nrow(V[grepl("residence", text_col(V$case_geography_basis), ignore.case=TRUE),]) >= 3L, "case residence records")
stop_if(all(grepl("not supplied|not necessarily|not inferred|not individual|no human|not assumed|condition-specific|infection-specific", text_col(V$exposure_geography_basis)[grepl("residence", text_col(V$case_geography_basis), ignore.case=TRUE)], ignore.case=TRUE)), "residence/exposure separation")

for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c("phase 12a","phase 12b","phase 12c","accepted / frozen","phase 13a","implemented","phase 13b","phase 13c","not implemented","active phase","none","great black swamp","hold","noncanonical","intake-coordinate discrepancy","unresolved")) stop_if(grepl(term, txt, fixed=TRUE), paste("status", rel, term))
}
for (name in c("phase12a_vector_ecology_freeze_manifest.json","phase12b_vector_environment_human_dependencies_freeze_manifest.json","phase12c_vector_ecology_futures_freeze_manifest.json")) {
  txt <- paste(readLines(file.path(reports, name), warn=FALSE, encoding="UTF-8"), collapse=" ")
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("Phase 12 status", name))
}

png <- file.path(maps, "41_infectious_disease_system_baseline_2026.png")
svg <- file.path(maps, "41_infectious_disease_system_baseline_2026.svg")
stop_if(file.exists(png) && file.info(png)$size > 10000, "Map 41 PNG")
stop_if(identical(paste(sprintf("%02x", as.integer(readBin(png, "raw", n=8))), collapse=""), "89504e470d0a1a0a"), "Map 41 PNG signature")
xmllint <- Sys.which("xmllint"); stop_if(nzchar(xmllint), "xmllint")
xml_status <- system2(xmllint, c("--noout", svg), stdout=FALSE, stderr=FALSE); stop_if(is.null(xml_status) || xml_status==0, "Map 41 SVG parse")
svg_text <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
for (term in c("map 41","infectious disease","vector","water","foodborne","respiratory","nndss","wastewater","surveillance","pathogen presence","exposure","infection","reported case","local transmission","no individual cases")) stop_if(grepl(term, svg_text, fixed=TRUE), paste("Map 41 text", term))

prior_paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
prior_hashes <- character(); prior_total <- 0L
for (path in sort(prior_paths)) {
  x <- manifest_artifacts(path); stop_if(nrow(x)>0L, paste("empty prior manifest", basename(path)))
  for (i in seq_len(nrow(x))) {
    if (x$rel[[i]] %in% names(prior_hashes)) stop_if(unname(prior_hashes[[x$rel[[i]]]]) == x$sha256[[i]], paste("conflicting prior hash", x$rel[[i]]))
    prior_hashes[x$rel[[i]]] <- x$sha256[[i]]
    stop_if(portable_against_head(file.path(root, x$rel[[i]]), x$rel[[i]], x$sha256[[i]]), paste("prior artifact", x$rel[[i]]))
    prior_total <- prior_total + 1L
  }
}
stop_if(prior_total >= 300L && length(unique(names(prior_hashes))) >= 295L, "prior freeze inventory")
stop_if(file.exists(file.path(reports, "infectious_disease_baseline_manifest.json")), "Phase 13A working manifest")
manifest <- paste(readLines(file.path(reports, "infectious_disease_baseline_manifest.json"), warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl('"phase": "13A"', manifest, fixed=TRUE) && grepl('"map_number": 41', manifest, fixed=TRUE) && grepl('"phase13b_implemented": false', manifest, fixed=TRUE) && grepl('"phase13c_implemented": false', manifest, fixed=TRUE), "Phase 13A manifest boundary")
current <- verify_current_manifest(file.path(reports, "infectious_disease_baseline_manifest.json"), 21L)

bad <- list.files(file.path(root, "data", "processed"), recursive=TRUE, full.names=TRUE)
bad <- c(bad, list.files(maps, full.names=TRUE), list.files(file.path(root, "src", "python", "systems"), full.names=TRUE), list.files(file.path(root, "src", "R", "systems"), full.names=TRUE))
bad <- bad[grepl("phase13b|phase13c|infectious_disease_dependencies|infectious_disease_futures|^42_|^43_", tolower(basename(bad)))]
stop_if(length(bad)==0L, "Phase 13B/13C artifacts")

cat(sprintf("Phase 13A R validation passed: %d nodes, %d relationships, %d observations, %d surveillance records, %d sources, %d uncertainties; Map 41 parsed; %d prior freeze entries/%d unique protected artifacts independently checked; source/reporting, health boundaries, holds, and 13B/13C exclusion verified\n", nrow(N), nrow(R), nrow(O), nrow(V), nrow(S), nrow(U), prior_total, length(unique(names(prior_hashes)))))
