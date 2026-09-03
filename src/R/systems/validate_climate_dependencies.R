args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), "../../.."), mustWork=FALSE)
read_csv <- function(p) read.csv(p, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c(""))
sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nchar(cmd) > 0) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stopifnot(length(out) >= 1)
    return(tolower(strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]))
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
  current <- NA_character_; rel <- character(); bytes <- numeric(); hashes <- character()
  for (line in lines) {
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, m)[[1]]
    if (length(hit) == 2 && grepl("/", hit[[2]], fixed=TRUE)) current <- hit[[2]]
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
    bh <- regmatches(line, b)[[1]]
    if (!is.na(current) && length(bh) == 2) bytes <- c(bytes, as.numeric(bh[[2]]))
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (!is.na(current) && length(hh) == 2) { rel <- c(rel, current); hashes <- c(hashes, hh[[2]]); current <- NA_character_ }
  }
  stopifnot(length(rel) == length(bytes), length(rel) == length(hashes))
  data.frame(rel=rel, bytes=bytes, sha256=hashes, stringsAsFactors=FALSE)
}
verify_manifest <- function(path) {
  x <- manifest_artifacts(path)
  stopifnot(nrow(x) > 0)
  for (i in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[i]])
    stopifnot(file.exists(p), as.numeric(file.info(p)$size) == x$bytes[[i]], sha256_file(p) == x$sha256[[i]])
  }
  nrow(x)
}
one <- function(frame, key, value) {
  x <- frame[!is.na(frame[[key]]) & frame[[key]] == value, , drop=FALSE]
  stopifnot(nrow(x) == 1)
  x[1, , drop=FALSE]
}
d <- read_csv(file.path(root,"data/processed/networks/climate_hazard_dependency_edges.csv"))
r <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_dependency_register.csv"))
c <- read_csv(file.path(root,"data/processed/analysis/climate_compound_event_register.csv"))
k <- read_csv(file.path(root,"data/processed/analysis/climate_resilience_control_register.csv"))
m <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_dependency_matrix.csv"))
s <- read_csv(file.path(root,"data/processed/analysis/climate_dependency_sources.csv"))
base <- read_csv(file.path(root,"data/processed/networks/climate_hazard_nodes.csv"))
stopifnot(nrow(d)==24, nrow(r)==24, nrow(c)==9, nrow(k)==12, nrow(m)==9, nrow(s)==14)
stopifnot(length(unique(d$dependency_id))==24, length(unique(r$dependency_id))==24, length(unique(c$compound_id))==9, length(unique(k$control_id))==12)
all_source_ids <- c(s$source_id, read_csv(file.path(root,"data/processed/analysis/climate_hazard_sources.csv"))$source_id)
stopifnot(all(d$hazard_node_id %in% base$node_id), all(r$hazard_node_id %in% base$node_id), all(d$source_id %in% all_source_ids), all(r$source_id %in% all_source_ids), all(c$source_id %in% all_source_ids), all(k$source_id %in% all_source_ids))
for (id in c("d9_fema_nfhl","d9_noaa_inundation")) { z <- one(s,"source_id",id); stopifnot(grepl("registry-only",tolower(z$use_limitations),fixed=TRUE), !any(d$source_id==id), !any(r$source_id==id), !any(c$source_id==id), !any(k$source_id==id)) }
qual <- c("strong","moderate","limited","unknown","not_applicable")
basis <- c("supported_system_dependency","documented_observation_interface","physically_plausible_system_pathway","documented_mechanism_plus_plausible_pathway","unsupported_unknown_interface","documented_product_interface","documented_control_interface")
support <- c("documented_control","documented_planning_context","unknown_unverified_local_control","potential_buffer_inference","documented_management_pathway","documented_tool","plausible_control","documented_interfaces_only")
stopifnot(all(d$relationship_basis %in% basis), all(r$evidence_basis %in% basis), all(k$support_status %in% support))
stopifnot(all(d$dependency_strength %in% qual), all(d$monitoring_strength %in% qual), all(d$warning_capacity %in% qual), all(d$spatial_certainty %in% qual), all(d$temporal_certainty %in% qual), all(r$dependency_strength %in% qual))
stopifnot(all(c$observed_or_plausible %in% c("historically_documented","physically_plausible_pathway","documented_mechanism_plus_plausible_pathway")), all(c$confidence %in% c("high","moderate","limited","unknown")), all(k$confidence %in% c("high","moderate","limited","unknown")))
for (frame in list(d,r,c,k,m,s)) { col <- if ("notes" %in% names(frame)) "notes" else "use_limitations"; stopifnot(all(nchar(as.character(frame[[col]])) > 0)) }
expected <- data.frame(id=c("HZD-004","HZD-008","HZD-013","HZD-015","HZD-018","HZD-022","HZD-023","HZD-024"), source=c("b9_usgs_dv","b9_usgs_dv","d9_noaa_llv","d9_glerl_ice","d9_nws_cle_winter","d9_epa_great_lakes","b9_nws_points","b9_drought_gov"), basis=c("physically_plausible_system_pathway","unsupported_unknown_interface","documented_product_interface","unsupported_unknown_interface","physically_plausible_system_pathway","unsupported_unknown_interface","documented_control_interface","documented_control_interface"), strength=c("strong","unknown","moderate","unknown","moderate","unknown","moderate","moderate"), stringsAsFactors=FALSE)
for (i in seq_len(nrow(expected))) { z <- one(d,"dependency_id",expected$id[[i]]); q <- one(r,"dependency_id",expected$id[[i]]); stopifnot(z$source_id==expected$source[[i]], z$relationship_basis==expected$basis[[i]], z$dependency_strength==expected$strength[[i]], q$evidence_basis==expected$basis[[i]], q$source_id==expected$source[[i]], q$dependency_strength==expected$strength[[i]]) }
stopifnot(grepl("not direct evidence of port",tolower(one(d,"dependency_id","HZD-013")$notes),fixed=TRUE), grepl("treatment or intake",tolower(one(d,"dependency_id","HZD-008")$mechanism),fixed=TRUE), grepl("remain unknown",tolower(one(d,"dependency_id","HZD-015")$notes),fixed=TRUE), grepl("unsupported here",tolower(one(d,"dependency_id","HZD-022")$notes),fixed=TRUE))
for (i in seq_len(nrow(c))) { z <- c[i,]; if (z$compound_id=="CPL-003") stopifnot(z$observed_or_plausible=="documented_mechanism_plus_plausible_pathway",z$source_id=="d9_pnas_hab",z$confidence=="high") else stopifnot(z$observed_or_plausible=="physically_plausible_pathway") }
stopifnot(one(c,"compound_id","CPL-004")$confidence=="limited",one(c,"compound_id","CPL-005")$source_id=="d9_noaa_seiche",one(c,"compound_id","CPL-009")$source_id=="b9_drought_gov")
controls <- data.frame(id=c("HZC-001","HZC-002","HZC-004","HZC-007","HZC-008","HZC-009","HZC-010","HZC-011","HZC-012"),support=c("documented_control","documented_control","documented_control","documented_planning_context","potential_buffer_inference","documented_management_pathway","documented_tool","plausible_control","documented_interfaces_only"),source=c("b9_nws_points","b9_nws_points","b9_coops_daily","bge_ohio_epa_npdes","bge_usfws_nwi","bge_ohio_h2ohio","d9_noaa_llv","d9_nws_cle_winter","d9_nws_gl_obs"),stringsAsFactors=FALSE)
for (i in seq_len(nrow(controls))) { z <- one(k,"control_id",controls$id[[i]]); stopifnot(z$support_status==controls$support[[i]],z$source_id==controls$source[[i]]) }
stopifnot(grepl("no local",tolower(one(k,"control_id","HZC-007")$documented_mechanism),fixed=TRUE),grepl("calm-day",tolower(one(k,"control_id","HZC-010")$notes),fixed=TRUE),!any(grepl("effective(?!ness)|guarantee|eliminat",k$effectiveness_status,ignore.case=TRUE,perl=TRUE)))
fields <- c(names(d),names(r),names(c),names(k),names(m),names(s)); stopifnot(!any(fields %in% c("hazard_score","risk_score","probability","mortality","dose","social_vulnerability")))
text <- tolower(paste(capture.output(print(d)),capture.output(print(r)),capture.output(print(c)),capture.output(print(k)),capture.output(print(m)),collapse=" "))
stopifnot(!grepl("2050|2075",text), grepl("joint probability",text,fixed=TRUE), grepl("no comprehensive emergency-management model",text,fixed=TRUE), !grepl("(?:outage|damage|mortality|disease|social[-_ ]vulnerability)[[:space:]]*(?:probability|score|estimate)[[:space:]]*[,=:][[:space:]]*[0-9]",text,perl=TRUE))
map_png <- file.path(root,"outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.png"); map_svg <- file.path(root,"outputs/maps/systems/30_climate_hazard_dependencies_resilience_2026.svg"); stopifnot(file.exists(map_png),file.info(map_png)$size>1000,file.exists(map_svg),file.info(map_svg)$size>1000)
t <- tolower(paste(readLines(map_svg,warn=FALSE),collapse=" ")); for (term in c("map 30","compound pathways","heat + power","precipitation + nutrient","lake level","freeze-thaw","not routes","seiche","not ocean storm surge")) stopifnot(grepl(term,t,fixed=TRUE))
a_hashes <- verify_manifest(file.path(root,"reports/climate_hazard_baseline_manifest.json")); b_hashes <- verify_manifest(file.path(root,"reports/climate_dependency_manifest.json"))
cat(sprintf("Phase 9B R validation passed: %d dependency edges, %d compound events, %d controls, %d matrix rows; independently recomputed %d Phase 9A and %d Phase 9B artifact hashes; Map 30 present\n",nrow(d),nrow(c),nrow(k),nrow(m),a_hashes,b_hashes))
