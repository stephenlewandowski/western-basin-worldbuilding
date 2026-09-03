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
N <- read_csv(file.path(root,"data/processed/networks/climate_hazard_nodes.csv"))
E <- read_csv(file.path(root,"data/processed/networks/climate_hazard_edges.csv"))
O <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_observations.csv"))
S <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_sources.csv"))
stopifnot(nrow(N)==28, nrow(E)==29, nrow(O)==28, nrow(S)==21)
stopifnot(length(unique(N$node_id))==28, length(unique(E$edge_id))==29, length(unique(O$observation_id))==28, length(unique(S$source_id))==21)
stopifnot(length(unique(S$url))==21)
stopifnot(all(N$source_id %in% S$source_id), all(E$source_id %in% S$source_id), all(O$source_id %in% S$source_id))
stopifnot(all(E$from_id %in% N$node_id), all(E$to_id %in% N$node_id))
stopifnot(all(N$reality_status=="real"), all(N$canon_status %in% c("verified","inferred")))
stopifnot(all(N$confidence %in% c("high","moderate","limited","unknown")), all(E$confidence %in% c("high","moderate","limited","unknown")), all(O$confidence %in% c("high","moderate","limited","unknown")))
stopifnot(all(O$observed_or_modeled %in% c("observed","derived from observed","observed_adjusted_series","expert_assessed_status","expert_assessed_index","historical_event_record","warning_threshold")))
stopifnot(all(grepl("^-?[0-9]+(\\.[0-9]+)?$", as.character(O$value))))
raw <- paste(readLines(file.path(root,"data/raw/climate_hazards/usgs_maumee_waterville_daily_flow_2025_2026.json"), warn=FALSE), collapse=" ")
stopifnot(grepl('"value"[[:space:]]*:[[:space:]]*"313".*2026-07-29', raw, perl=TRUE), grepl('"value"[[:space:]]*:[[:space:]]*"476".*2026-09-02', raw, perl=TRUE))
hzo015 <- one(O,"observation_id","HZO-015"); stopifnot(as.numeric(hzo015$value)==313, as.character(hzo015$period)=="2026-07-29")
stopifnot(as.numeric(one(O,"observation_id","HZO-014")$value)==68200)
n004 <- one(N,"node_id","HZ-004"); n008 <- one(N,"node_id","HZ-008"); n016 <- one(N,"node_id","HZ-016"); n021 <- one(N,"node_id","HZ-021"); n026 <- one(N,"node_id","HZ-026")
stopifnot(n004$source_id=="b9_usgs_dv", n004$canon_status=="inferred", n004$confidence=="limited", grepl("project-inferred",tolower(n004$notes),fixed=TRUE), grepl("does not establish watershed-wide runoff",n004$notes,fixed=TRUE))
stopifnot(n008$source_id=="b9_noaa_atlas14", n008$canon_status=="inferred", grepl("project-inferred",tolower(n008$notes),fixed=TRUE), grepl("supports site/grid precipitation-frequency context only",n008$notes,fixed=TRUE))
stopifnot(n016$source_id=="b9_storm_events_2025", grepl("dated 2025 details snapshot",n016$notes,fixed=TRUE))
stopifnot(n021$source_id=="b9_coops_daily", n021$scale=="station / shoreline")
stopifnot(grepl("project-inferred",tolower(n026$notes),fixed=TRUE), grepl("NWS point metadata",n026$notes,fixed=TRUE))
stopifnot(one(N,"node_id","HZ-024")$source_id=="b9_ncei_cag",one(N,"node_id","HZ-024")$scale=="county",one(N,"node_id","HZ-027")$source_id=="b9_acis",one(N,"node_id","HZ-027")$scale=="station",one(N,"node_id","HZ-028")$source_id=="b9_storm_events_2025",one(N,"node_id","HZ-028")$scale=="county / event record")
expected <- data.frame(id=c("HZE-004","HZE-007","HZE-018","HZE-021","HZE-022","HZE-029","HZE-030"), source=c("b9_usgs_dv","b9_noaa_atlas14","b9_storm_events_2025","b9_nws_winter","b9_nws_thunderstorm","b9_usdm_area","b9_acis"), basis=c("project inference","project inference","historical event-record aggregation","project inference","project inference","project inference","project inference"), conf=c("limited","limited","high","limited","limited","limited","limited"), stringsAsFactors=FALSE)
for (i in seq_len(nrow(expected))) { e <- one(E,"edge_id",expected$id[[i]]); stopifnot(e$source_id==expected$source[[i]], grepl(expected$basis[[i]],tolower(e$relationship_basis),fixed=TRUE), e$confidence==expected$conf[[i]]) }
e004 <- one(E,"edge_id","HZE-004"); stopifnot(e004$from_id=="HZ-006",e004$to_id=="HZ-004",!any(E$edge_id=="HZE-023"))
event_ids <- sprintf("HZO-%03d",21:26); ev <- O[O$observation_id %in% event_ids,,drop=FALSE]
stopifnot(nrow(ev)==6, all(ev$source_id=="b9_storm_events_2025"), all(ev$units=="county event records"), all(ev$spatial_scale=="county / event record"), any(grepl("not a rate",ev$notes,ignore.case=TRUE)))
flood <- one(N,"node_id","HZ-007"); stopifnot(flood$scale=="modeled regulatory flood zone", flood$node_type=="floodplain_context", grepl("distinct from observed",flood$notes,ignore.case=TRUE))
e006 <- one(E,"edge_id","HZE-006"); e028 <- one(E,"edge_id","HZE-028")
stopifnot(e006$source_id=="b9_fema_nfhl",grepl("not an observed flood footprint",e006$notes,ignore.case=TRUE),e028$source_id=="b9_fema_nfhl",grepl("remain distinct categories",e028$notes,ignore.case=TRUE))
stopifnot(all(grepl("event records",ev$metric,ignore.case=TRUE)), !any(grepl("rate|probability",ev$metric,ignore.case=TRUE)))
note_requirements <- c("HZO-021"="not a rate","HZO-022"="deterministic","HZO-023"="probability","HZO-024"="distinct from","HZO-025"="not a regional","HZO-026"="qualitative")
for (id in names(note_requirements)) stopifnot(grepl(note_requirements[[id]],one(O,"observation_id",id)$notes,ignore.case=TRUE) )
for (id in c("HZ-009","HZ-022")) stopifnot(grepl("groundwater",one(N,"node_id",id)$notes,ignore.case=TRUE),grepl("no|not",one(N,"node_id",id)$notes,ignore.case=TRUE))
for (id in c("HZO-013","HZO-020")) stopifnot(grepl("groundwater",one(O,"observation_id",id)$notes,ignore.case=TRUE),grepl("no|not",one(O,"observation_id",id)$notes,ignore.case=TRUE))
stopifnot(all(c("station","county","HUC8 / HUC12 interface","modeled regulatory flood zone","station / shoreline") %in% N$scale), all(c("station","county","county / event record") %in% O$spatial_scale))
stopifnot(one(O,"observation_id","HZO-027")$observed_or_modeled=="warning_threshold", grepl("^feet;",one(O,"observation_id","HZO-027")$units))
fields <- c(names(N),names(E),names(O),names(S)); stopifnot(!any(fields %in% c("hazard_score","risk_score","probability","mortality","exposure_estimate","dose","social_vulnerability")))
data_text <- tolower(paste(capture.output(print(N)),capture.output(print(E)),capture.output(print(O)),capture.output(print(S)),collapse=" "))
stopifnot(!grepl("2050|2075",data_text), !grepl("(?:hazard|event|outage)[ _-]probability[[:space:]]*[,=:][[:space:]]*[0-9]",data_text,perl=TRUE), grepl("ocean storm surge",data_text,fixed=TRUE))
stopifnot(!grepl("future",paste(tolower(O$period),collapse=" "),fixed=TRUE))
for (m in gregexpr("ocean storm surge",data_text,fixed=TRUE)[[1]]) if (m[[1]] > 0) stopifnot(grepl("not",substr(data_text,max(1,m[[1]]-30),m[[1]]-1),fixed=TRUE))
map_png <- file.path(root,"outputs/maps/systems/29_climate_natural_hazards_2026.png"); map_svg <- file.path(root,"outputs/maps/systems/29_climate_natural_hazards_2026.svg")
stopifnot(file.exists(map_png), file.info(map_png)$size>1000, file.exists(map_svg), file.info(map_svg)$size>1000)
svg_text <- tolower(paste(readLines(map_svg,warn=FALSE),collapse=" "))
for (term in c("map 29","extreme heat","precip / flood","drought / low water","lake / coastal","convective","winter","not hazard zones","seiche")) stopifnot(grepl(term,svg_text,fixed=TRUE))
working_hashes <- verify_manifest(file.path(root,"reports/climate_hazard_baseline_manifest.json"))
for (m in c("phase8a_biogeochemical_nutrient_flux_freeze_manifest.json","phase8b_biogeochemical_dependencies_controls_freeze_manifest.json","phase8c_biogeochemical_futures_freeze_manifest.json")) stopifnot(file.exists(file.path(root,"reports",m)))
cat(sprintf("Phase 9A R validation passed: %d nodes, %d edges, %d observations, %d sources; independent SHA-256 check covered %d working-baseline artifacts; USGS minimum 313 cfs on 2026-07-29; Map 29 present\n",nrow(N),nrow(E),nrow(O),nrow(S),working_hashes))
