args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
analysis <- file.path(root, "data", "processed", "analysis")
networks <- file.path(root, "data", "processed", "networks")
maps <- file.path(root, "outputs", "maps", "systems")

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
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path)); hits[[1]]
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
  accepted <- raw_bytes(accepted_tmp); working <- raw_bytes(path)
  if (!identical(canonical_bytes(accepted), canonical_bytes(working))) return(FALSE)
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  lf <- canonical_bytes(accepted); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(lf), fixed=TRUE))
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
    object <- regexec('"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{[^}]*"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, object)[[1]]
    if (length(hit) == 3L) {
      b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bh <- regmatches(line, b)[[1]]
      rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, if (length(bh)==2L) as.numeric(bh[[2]]) else NA_real_); next
    }
    direct <- regexec('"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit) == 3L) { rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); bytes <- c(bytes, NA_real_); next }
    path_hit <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    ph <- regmatches(line, path_hit)[[1]]
    if (length(ph)==2L) { append_current(); current <- ph[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE); bh <- regmatches(line, b)[[1]]
    if (length(bh)==2L && !is.na(current)) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE); hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}

verify_manifest <- function(path, expected_n) {
  x <- manifest_artifacts(path)
  stop_if(nrow(x)==expected_n, paste("manifest artifact count", basename(path)))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$rel[[i]], x$sha256[[i]]), paste("manifest artifact", x$rel[[i]]))
  nrow(x)
}

prior_inventory <- function() {
  paths <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
  expected <- character(); total <- 0L
  for (path in sort(paths)) {
    x <- manifest_artifacts(path); stop_if(nrow(x)>0L, paste("empty prior manifest", basename(path)))
    for (i in seq_len(nrow(x))) {
      rel <- x$rel[[i]]; hash <- x$sha256[[i]]
      if (rel %in% names(expected)) stop_if(unname(expected[[rel]])==hash, paste("conflicting prior hash", rel))
      expected[rel] <- hash
      stop_if(portable_match(file.path(root, rel), rel, hash), paste("prior artifact", rel)); total <- total + 1L
    }
  }
  list(entries=total, unique=length(expected), manifests=length(paths))
}

check_png <- function(path) {
  stop_if(file.exists(path) && file.info(path)$size > 10000, paste("PNG", basename(path)))
  raw <- readBin(path, "raw", n=8); hex <- paste(sprintf("%02x", as.integer(raw)), collapse="")
  stop_if(hex == "89504e470d0a1a0a", paste("PNG signature", basename(path)))
}
check_svg <- function(path, terms) {
  stop_if(file.exists(path) && file.info(path)$size > 10000, paste("SVG", basename(path)))
  xmllint <- Sys.which("xmllint"); stop_if(nzchar(xmllint), "xmllint is required")
  status <- system2(xmllint, c("--noout", path), stdout=FALSE, stderr=FALSE); stop_if(is.null(status) || status==0, "Map 39 SVG parse")
  txt <- tolower(paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in terms) stop_if(grepl(tolower(term), txt, fixed=TRUE), paste("Map 39 SVG text", term))
}

D <- read_csv(file.path(analysis, "vector_system_dependency_register.csv"))
E <- read_csv(file.path(networks, "vector_system_dependency_edges.csv"))
M <- read_csv(file.path(analysis, "vector_system_dependency_matrix.csv"))
X <- read_csv(file.path(analysis, "vector_dependency_evidence.csv"))
N <- read_csv(file.path(networks, "vector_ecology_nodes.csv"))
S <- read_csv(file.path(analysis, "vector_ecology_sources.csv"))

expected_d <- c("dependency_id","object_a","object_b","system_a","system_b","relationship_type","documented_or_inferred","relationship_basis","spatial_scale","evidence_strength","source_id","confidence","reality_status","canon_status","notes")
expected_m <- c("object_id","object_type","object_name","temperature_relationship","precipitation_hydrology","wetland_standing_water","urban_container","forest_edge_host","host_ecology","population_contact_interface","surveillance_detection","governance_decision_interface","spatial_scale_certainty","temporal_certainty","notes")
expected_x <- c("evidence_id","dependency_id","claim_type","claim_status","source_id","spatial_scale","temporal_scope","supported_statement","not_supported_statement")
expected_s <- c("source_id","title","url","source_type","publication_or_period","retrieval_date","geographic_scale","method_or_product","evidence_use","use_limitations","retrieval_url","retrieval_provenance")
stop_if(setequal(names(D), expected_d) && setequal(names(E), expected_d) && setequal(names(M), expected_m) && setequal(names(X), expected_x) && setequal(names(S), expected_s), "Phase 12B schemas")
stop_if(nrow(D)==28L && nrow(E)==28L && nrow(M)==8L && nrow(X)==8L && nrow(N)==20L && nrow(S)==27L, "Phase 12B counts")
stop_if(!anyDuplicated(text_col(D$dependency_id)) && !anyDuplicated(text_col(E$dependency_id)) && !anyDuplicated(text_col(M$object_id)) && !anyDuplicated(text_col(X$evidence_id)), "Phase 12B unique IDs")
stop_if(all(text_col(D$dependency_id)==text_col(E$dependency_id)) && all(as.matrix(D)==as.matrix(E)), "register/edge equality")
source_ids <- text_col(S$source_id)
stop_if(all(text_col(D$source_id) %in% source_ids) && all(text_col(E$source_id) %in% source_ids) && all(text_col(X$source_id) %in% source_ids), "Phase 12B source references")
stop_if(all(text_col(D$relationship_type) %in% c("seasonal_development","habitat_opportunity","habitat_association","habitat_interface","container_habitat","questing_habitat","woodland_habitat","host_association","potential_interface","detection_interface","information_to_decision","observation_interface","environmental_driver","spatial_scale","health_boundary","separation_rule","effort_detection_boundary","scale_boundary","case_transmission_boundary","monitoring_control_boundary","hold_preservation")), "relationship vocabulary")
stop_if(all(text_col(D$documented_or_inferred) %in% c("documented","documented_plus_inferred","inferred","documented_boundary","accepted_context_plus_inferred")), "relationship classification vocabulary")
stop_if(all(text_col(D$evidence_strength) %in% c("strong","moderate","limited","unknown","not_applicable")) && all(text_col(D$confidence) %in% c("high","moderate","limited","unknown")), "qualitative vocabulary")
stop_if(all(text_col(D$reality_status)=="real") && all(text_col(D$canon_status) %in% c("verified","inferred")), "dependency status")
stop_if(all(vapply(M[4:14], function(col) all(text_col(col) %in% c("strong","moderate","limited","unknown","not_applicable")), logical(1))), "matrix values")
stop_if(all(nchar(text_col(D$notes))>0) && all(nchar(text_col(X$not_supported_statement))>0), "notes/crosswalk limitations")
stop_if(all(text_col(X$dependency_id) %in% text_col(D$dependency_id)), "crosswalk dependency references")

project_i <- text_col(D$relationship_basis)=="project_system_inference"
stop_if(all(text_col(D$documented_or_inferred)[project_i]=="inferred") && all(text_col(D$canon_status)[project_i]=="inferred"), "inferred relationship classification")
documented_i <- text_col(D$relationship_basis) %in% c("documented_relationship","documented_source","documented_program")
stop_if(all(text_col(D$documented_or_inferred)[documented_i] %in% c("documented","documented_plus_inferred")) && all(text_col(D$canon_status)[documented_i]=="verified"), "documented relationship classification")
boundary_i <- text_col(D$relationship_basis) %in% c("surveillance_boundary","CDC county caveat","CDC case-geography caveat","accepted governance distinction","accepted canon status","surveillance_methodology")
stop_if(all(text_col(D$documented_or_inferred)[boundary_i]=="documented_boundary") && all(text_col(D$canon_status)[boundary_i]=="verified"), "boundary relationship classification")
stop_if(all(text_col(D$object_a)!="human_case" | text_col(D$object_b)=="human_case_context"), "human case object boundary")

core_text <- tolower(paste(frame_text(D), frame_text(M), frame_text(X), frame_text(N), collapse=" "))
core_text <- gsub("_", " ", core_text, fixed=TRUE)
for (term in c("documented","inferred","temperature","standing water","container","forest","host","population","surveillance","detection","not exposure","not abundance","local transmission","not absence")) stop_if(grepl(term, core_text, fixed=TRUE), paste("boundary text", term))
fields <- unique(c(names(D),names(E),names(M),names(X),names(N)))
stop_if(!any(fields %in% c("risk_score","vulnerability_score","ej_score","infection_probability","contact_probability","disease_incidence","hospitalization","mortality","dose","exposure_score")), "forbidden analytical columns")
stop_if(!grepl("(?:risk score|vulnerability score|ej score|infection probability|disease incidence)\\s*[,=:]\\s*[0-9]", core_text, perl=TRUE), "unsupported health metric")
stop_if(!grepl("\\b(?:2050|2075)\\b", core_text, perl=TRUE), "Phase 12B future contamination")

ix <- S[text_col(S$source_id)=="v12_cdc_ixodes", , drop=FALSE]
stop_if(nrow(ix)==1L && ix$url[[1]]=="https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html" && ix$retrieval_url[[1]]=="https://restoredcdc.org/www.cdc.gov/ticks/media/files/2024/04/Public_Use_Ixodes_County_Table_2024_summary.xlsx", "source-page/retrieval provenance")
stop_if(nrow(ix)==1L && grepl("not CDC-hosted", ix$retrieval_provenance[[1]], fixed=TRUE) && grepl("HTTP 403", ix$retrieval_provenance[[1]], fixed=TRUE), "retrieval qualification")
stop_if(grepl("not exposure", core_text, fixed=TRUE) && grepl("not abundance", core_text, fixed=TRUE), "health boundary")

for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE) && grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("holds", rel))
}
for (name in c("phase11a_population_settlement_freeze_manifest.json","phase11b_population_mobility_dependencies_freeze_manifest.json","phase11c_population_settlement_futures_freeze_manifest.json")) {
  txt <- paste(readLines(file.path(reports, name), warn=FALSE, encoding="UTF-8"), collapse=" ")
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("Phase 11 status", name))
}

A_MANIFEST <- file.path(reports, "vector_ecology_baseline_manifest.json")
B_MANIFEST <- file.path(reports, "vector_dependency_manifest.json")
a_n <- verify_manifest(A_MANIFEST, 14L); b_n <- verify_manifest(B_MANIFEST, 10L)
b_txt <- paste(readLines(B_MANIFEST, warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl(paste0('"sha256": "', sha256_file(A_MANIFEST), '"'), b_txt, fixed=TRUE) && grepl(paste0('"bytes": ', file.info(A_MANIFEST)$size), b_txt, fixed=TRUE), "Phase 12A working-baseline integrity")
check_png(file.path(maps, "39_vector_environment_human_dependencies_2026.png"))
check_svg(file.path(maps, "39_vector_environment_human_dependencies_2026.svg"), c("map 39","vector","environment","human-system","temperature","standing water","urban containers","forest / edge","surveillance","not continuous","not exposure"))
prior <- prior_inventory()
stop_if(prior$entries==298L && prior$unique==293L, "prior freeze inventory")
manifest_text <- paste(readLines(B_MANIFEST, warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"12B"', manifest_text, perl=TRUE) && grepl('"phase12c_implemented"[[:space:]]*:[[:space:]]*false', manifest_text, perl=TRUE) && grepl('"phase13_implemented"[[:space:]]*:[[:space:]]*false', manifest_text, perl=TRUE), "Phase 12B manifest boundary")
paths <- c(list.files(file.path(root,"data","processed"), recursive=TRUE, full.names=TRUE), list.files(maps, full.names=TRUE), list.files(file.path(root,"src","R","systems"), full.names=TRUE))
bad <- paths[grepl("phase13|vector.*future|future.*vector|/40_|\\\\40_", tolower(paths))]
stop_if(length(bad)==0L, "later-phase artifacts")

cat(sprintf("Phase 12B R validation passed: %d dependency-register rows, %d dependency edges, %d matrix rows, %d evidence-crosswalk rows, %d reused sources; Map 39 parsed; Phase 12A manifest and %d Phase 12A artifacts independently checked; independently checked %d prior manifest entries/%d unique protected artifacts; documented/inferred, health, surveillance, provenance, and Phase 12C/13 boundaries verified\n", nrow(D), nrow(E), nrow(M), nrow(X), nrow(S), a_n, prior$entries, prior$unique))
