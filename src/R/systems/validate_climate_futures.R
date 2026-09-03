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
P <- read_csv(file.path(root,"data/processed/analysis/climate_projection_evidence.csv")); S <- read_csv(file.path(root,"data/processed/analysis/climate_scenario_sources.csv")); A <- read_csv(file.path(root,"data/processed/scenarios/climate_scenario_assumptions.csv")); H <- read_csv(file.path(root,"data/processed/scenarios/climate_scenario_hazard_states.csv")); D <- read_csv(file.path(root,"data/processed/scenarios/climate_scenario_dependency_states.csv")); R <- read_csv(file.path(root,"data/processed/scenarios/climate_scenario_resilience_states.csv")); C <- read_csv(file.path(root,"data/processed/scenarios/climate_compound_event_scenario_states.csv")); X <- read_csv(file.path(root,"outputs/figures/climate_scenario_comparison.csv"))
stopifnot(nrow(P)==12,nrow(S)==13,nrow(A)==36,nrow(H)==36,nrow(D)==48,nrow(R)==48,nrow(C)==54,nrow(X)==6)
stopifnot(length(unique(P$projection_id))==12,length(unique(S$source_id))==13,length(unique(A$assumption_id))==36,length(unique(H$state_id))==36,length(unique(D$state_id))==48,length(unique(R$state_id))==48,length(unique(C$state_id))==54,length(unique(X$scenario_id))==6)
ids <- as.vector(outer(c("A","B","C"),c(2050,2075),paste0)); stopifnot(all(A$scenario_id %in% c("A","B","C")),all(A$scenario_year %in% c(2050,2075)),all(H$scenario_id %in% ids),all(D$scenario_id %in% ids),all(R$scenario_id %in% ids),all(C$scenario_id %in% ids))
source_ids <- S$source_id; stopifnot(all(A$source_id %in% source_ids),all(P$source_id %in% source_ids),all(H$source_id %in% source_ids),all(D$source_id %in% source_ids),all(R$source_id %in% source_ids),all(C$source_id %in% source_ids))
stopifnot(all(A$reality_status=="fictional"),all(H$reality_status=="fictional"),all(D$reality_status=="fictional"),all(R$reality_status=="fictional"),all(C$reality_status=="fictional"))
qual <- c("high","moderate","limited","unknown"); stopifnot(all(A$plausibility %in% qual),all(A$uncertainty %in% qual),all(H$plausibility %in% qual),all(D$plausibility %in% qual),all(R$plausibility %in% qual),all(C$plausibility %in% qual),all(P$observed_or_modeled %in% c("modeled_projection","model_metadata")),all(P$confidence %in% qual))
stopifnot(all(P$value!=""), !any(P$projection_period=="2075"))
base_nodes <- read_csv(file.path(root,"data/processed/networks/climate_hazard_nodes.csv")); base_dep <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_dependency_register.csv")); base_ctl <- read_csv(file.path(root,"data/processed/analysis/climate_resilience_control_register.csv"))
stopifnot(all(H$baseline_object_id %in% base_nodes$node_id),all(unlist(strsplit(as.character(D$baseline_interface),";",fixed=TRUE)) %in% base_dep$dependency_id),all(unlist(strsplit(as.character(R$baseline_control),";",fixed=TRUE)) %in% c(base_ctl$control_id,base_dep$dependency_id)))
hazard_baselines <- c(extreme_heat="HZ-001",heavy_precipitation_flooding="HZ-004",drought_low_water="HZ-009",lake_coastal="HZ-012",severe_convective="HZ-016",winter="HZ-018")
for (f in names(hazard_baselines)) stopifnot(setequal(unique(H$baseline_object_id[H$hazard_family==f]),hazard_baselines[[f]]))
path_baselines <- c(heat_to_energy="HZD-001",precip_to_nutrient="HZD-005",precip_to_stormwater="HZD-006",flood_to_freight="HZD-007",lake_to_coastal="HZD-013",storm_to_power_information="HZD-016;HZD-017",drought_to_ag_ecology="HZD-009;HZD-010",winter_to_infrastructure="HZD-018;HZD-019")
for (p in names(path_baselines)) stopifnot(setequal(unique(D$baseline_interface[D$baseline_interface==path_baselines[[p]]]),path_baselines[[p]]))
control_baselines <- c(warning_systems="HZC-001",heat_adaptation="HZC-002",floodplain_stormwater="HZC-006",wetland_floodplain_buffer="HZC-008",water_treatment="HZD-008;HZD-022",lake_monitoring="HZC-004",agricultural_conservation="HZC-009",grid_information_redundancy="HZC-012")
for (p in names(control_baselines)) stopifnot(setequal(unique(R$baseline_control[R$control_domain==p]),control_baselines[[p]]))
path_sources <- c(heat_to_energy="c9_nca_energy",precip_to_nutrient="c9_pnas_hab",precip_to_stormwater="c9_nca_midwest",flood_to_freight="c9_nca_midwest",lake_to_coastal="c9_epa_great_lakes",storm_to_power_information="c9_nca_energy",drought_to_ag_ecology="c9_nca_midwest",winter_to_infrastructure="c9_nca_midwest")
for (p in names(path_sources)) stopifnot(setequal(unique(D$source_id[D$baseline_interface==path_baselines[[p]]]),path_sources[[p]]))
compound_sources <- c(heat_plus_power="c9_nca_energy",heat_plus_drought="c9_nca_midwest",precip_plus_nutrient="c9_pnas_hab",precip_plus_stormwater_wastewater="c9_nca_midwest",high_lake_plus_seiche="c9_epa_great_lakes",flood_plus_freight="c9_nca_midwest",freeze_thaw_plus_infrastructure="c9_nca_midwest",storm_plus_power_communications="c9_nca_energy",drought_plus_ag_ecology="c9_nca_midwest")
for (p in names(compound_sources)) stopifnot(setequal(unique(C$source_id[C$compound_id==p]),compound_sources[[p]]))
base_obs <- read_csv(file.path(root,"data/processed/analysis/climate_hazard_observations.csv")); q <- one(base_obs,"observation_id","HZO-015"); stopifnot(as.numeric(q$value)==313,as.character(q$period)=="2026-07-29")
fields <- c(names(P),names(A),names(H),names(D),names(R),names(C),names(X)); stopifnot(!any(fields %in% c("probability","risk_score","hazard_score","mortality","disease_incidence","dose","social_vulnerability","shoreline_position","outage_probability")))
text <- tolower(paste(capture.output(print(P)),capture.output(print(A)),capture.output(print(H)),capture.output(print(D)),capture.output(print(R)),capture.output(print(C)),capture.output(print(X)),collapse=" "))
stopifnot(grepl("no probability",text,fixed=TRUE),grepl("not a 2075 point estimate",text,fixed=TRUE),!grepl("(?:future|scenario)[ _-](?:tornado|hail|outage|damage|shoreline)[ _-]?(?:count|probability|position)[[:space:]]*[,=:][[:space:]]*[0-9]",text,perl=TRUE),!grepl("(?:mortality|disease|social[-_ ]vulnerability)[[:space:]]*(?:probability|score|estimate)[[:space:]]*[,=:][[:space:]]*[0-9]",text,perl=TRUE))
for (base in c("31_climate_hazard_futures_2050","31b_climate_hazard_futures_2075")) { png <- file.path(root,"outputs/maps/systems",paste0(base,".png")); svg <- file.path(root,"outputs/maps/systems",paste0(base,".svg")); stopifnot(file.exists(png),file.info(png)$size>1000,file.exists(svg),file.info(svg)$size>1000); z <- tolower(paste(readLines(svg,warn=FALSE),collapse=" ")); for (term in c(ifelse(grepl("31_",base,fixed=TRUE),"map 31","map 31b"),"adaptive / buffered basin","managed variable basin","compound hazard basin","not hazard zones","seiche")) stopifnot(grepl(term,z,fixed=TRUE)); if (grepl("31b_",base,fixed=TRUE)) stopifnot(grepl("not a 2075 point estimate",z,fixed=TRUE)) }
a_hashes <- verify_manifest(file.path(root,"reports/climate_hazard_baseline_manifest.json")); b_hashes <- verify_manifest(file.path(root,"reports/climate_dependency_manifest.json")); man <- readLines(file.path(root,"reports/climate_scenario_manifest.json"),warn=FALSE); stopifnot(any(grepl('"projection_records"[[:space:]]*:[[:space:]]*12',man,perl=TRUE)),any(grepl('"comparison_rows"[[:space:]]*:[[:space:]]*6',man,perl=TRUE)))
cat(sprintf("Phase 9C R validation passed: %d projection records, %d assumptions, %d hazard states, %d dependency states, %d resilience states, %d compound states, %d comparison rows; independently recomputed %d Phase 9A and %d Phase 9B artifact hashes; Maps 31/31b present\n",nrow(P),nrow(A),nrow(H),nrow(D),nrow(R),nrow(C),nrow(X),a_hashes,b_hashes))
