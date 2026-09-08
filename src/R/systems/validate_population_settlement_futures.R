args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
analysis <- file.path(root, "data", "processed", "analysis")
network <- file.path(root, "data", "processed", "networks")
scenario <- file.path(root, "data", "processed", "scenarios")
figures <- file.path(root, "outputs", "figures")
maps <- file.path(root, "outputs", "maps", "systems")
reports <- file.path(root, "reports")

read_table <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)

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

portable_match <- function(path, expected) {
  if (sha256_file(path) == expected) return(TRUE)
  if (!(tolower(tools::file_ext(path)) %in% c("csv","json","md","txt","yml","yaml","svg"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  expected %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  current <- NA_character_; rel <- character(); hashes <- character()
  for (line in lines) {
    m <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, m)[[1]]
    if (length(hit) == 2L && grepl("/", hit[[2]], fixed=TRUE)) current <- hit[[2]]
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh) == 2L && !is.na(current)) { rel <- c(rel, current); hashes <- c(hashes, hh[[2]]); current <- NA_character_ }
  }
  data.frame(rel=rel, sha256=hashes, stringsAsFactors=FALSE)
}

check_manifest <- function(path, expected_n, require_phase11c_false=FALSE) {
  stop_if(file.exists(path), paste("missing manifest", path))
  txt <- json_text(path)
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("manifest status", path))
  if (require_phase11c_false) stop_if(grepl('"phase11c_implemented"[[:space:]]*:[[:space:]]*false', txt, perl=TRUE), paste("Phase 11C boundary", path))
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == expected_n, paste("manifest artifact count", path))
  for (i in seq_len(nrow(x))) {
    p <- file.path(root, x$rel[[i]])
    stop_if(file.exists(p), paste("missing protected artifact", x$rel[[i]]))
    stop_if(portable_match(p, x$sha256[[i]]), paste("protected hash", x$rel[[i]]))
  }
  nrow(x)
}

A <- read_table(file.path(scenario, "population_settlement_scenario_assumptions.csv"))
P <- read_table(file.path(scenario, "population_settlement_projection_evidence.csv"))
S <- read_table(file.path(scenario, "population_settlement_future_states.csv"))
R <- read_table(file.path(network, "population_settlement_future_relationships.csv"))
U <- read_table(file.path(scenario, "population_settlement_future_uncertainty.csv"))
X <- read_table(file.path(figures, "population_settlement_future_comparison.csv"))
SRC <- read_table(file.path(analysis, "population_settlement_future_sources.csv"))
N <- read_table(file.path(analysis, "population_settlement_nodes.csv"))

expected <- list(
  A=c("assumption_id","scenario_id","scenario","horizon","domain","assumption","evidence_basis","source_id","uncertainty","reality_status","canon_status","classification","numeric_future_value_adopted","notes"),
  P=c("evidence_id","jurisdiction","geographic_scale","projection_horizon","source_id","projection_status","availability_at_scale","adopted_use","numeric_value_adopted","uncertainty","notes"),
  S=c("state_id","scenario_id","scenario","horizon","baseline_node_id","baseline_name","baseline_geographic_scale","baseline_settlement_class","current_fact","population_distribution_state","settlement_form_state","housing_form_state","employment_geography_state","mobility_interface_state","service_dependency_state","projection_relation","climate_migration_role","assumption_id","source_or_basis","plausibility","reality_status","canon_status","relationship_basis","numeric_future_value_adopted","notes"),
  R=c("relationship_id","scenario_id","scenario","horizon","source_node_id","target_node_id","relationship_type","spatial_scale","current_fact","scenario_assumption","scenario_consequence","commuting_migration_boundary","source_or_basis","assumption_id","evidence_strength","reality_status","canon_status","relationship_basis","numeric_future_value_adopted","notes"),
  U=c("uncertainty_id","scenario_id","scenario","horizon","category","subject","current_fact","scenario_assumption","uncertainty_state","source_or_basis","assumption_id","reality_status","canon_status","notes"),
  X=c("scenario_id","scenario","horizon","population_distribution","settlement_concentration","settlement_form","housing_form","employment_geography","mobility_interface","climate_migration_role","service_dependence","projection_use","uncertainty_profile","notes")
)
frames <- list(A=A,P=P,S=S,R=R,U=U,X=X)
for (nm in names(frames)) stop_if(setequal(names(frames[[nm]]), expected[[nm]]), paste("schema", nm))
stop_if(nrow(A)==36 && nrow(P)==6 && nrow(S)==108 && nrow(R)==108 && nrow(U)==36 && nrow(X)==6, "Phase 11C counts")
stop_if(!anyDuplicated(A$assumption_id) && !anyDuplicated(P$evidence_id) && !anyDuplicated(S$state_id) && !anyDuplicated(R$relationship_id) && !anyDuplicated(U$uncertainty_id) && !anyDuplicated(X$scenario_id), "unique IDs")
scenario_ids <- c("A2050","A2075","B2050","B2075","C2050","C2075")
years <- setNames(as.integer(substr(scenario_ids,2,5)), scenario_ids)
for (f in list(A,S,R,U,X)) {
  stop_if(setequal(unique(f$scenario_id), scenario_ids), "scenario coverage")
  stop_if(all(as.integer(f$horizon) == years[as.character(f$scenario_id)]), "horizon alignment")
}
stop_if(all(table(A$scenario_id)==6), "assumption rows per scenario")
stop_if(all(table(S$scenario_id)==18), "state rows per scenario")
stop_if(all(table(R$scenario_id)==18), "relationship rows per scenario")
stop_if(all(table(U$scenario_id)==6), "uncertainty rows per scenario")
stop_if(all(A$reality_status=="fictional") && all(A$canon_status=="scenario") && all(A$classification=="SCENARIO ASSUMPTION"), "assumption status")
stop_if(all(A$numeric_future_value_adopted=="false") && all(S$numeric_future_value_adopted=="false") && all(R$numeric_future_value_adopted=="false") && all(P$numeric_value_adopted=="false"), "numeric future boundary")
stop_if(all(S$reality_status=="fictional") && all(S$canon_status=="scenario") && all(R$reality_status=="fictional") && all(R$canon_status=="scenario") && all(U$reality_status=="fictional") && all(U$canon_status=="scenario"), "scenario status")
stop_if(all(A$source_id %in% SRC$source_id) && all(P$source_id %in% SRC$source_id), "source references")
county_ids <- N$node_id[N$node_type == "population_zone"]
stop_if(length(county_ids)==18 && all(S$baseline_node_id %in% county_ids) && all(S$baseline_geographic_scale=="county"), "baseline county references")
stop_if(all(R$source_node_id %in% county_ids) && all(R$target_node_id %in% county_ids) && all(R$source_node_id != R$target_node_id) && all(R$spatial_scale=="county_pair"), "relationship geography")
stop_if(all(grepl("commuting is not migration", tolower(R$commuting_migration_boundary), fixed=TRUE)), "commuting migration boundary")
all_text <- tolower(paste(capture.output(write.table(A,row.names=FALSE,quote=FALSE)), capture.output(write.table(S,row.names=FALSE,quote=FALSE)), capture.output(write.table(R,row.names=FALSE,quote=FALSE)), capture.output(write.table(U,row.names=FALSE,quote=FALSE)), capture.output(write.table(X,row.names=FALSE,quote=FALSE)), collapse=" "))
stop_if(grepl("high-uncertainty scenario mechanism", all_text, fixed=TRUE) && grepl("not a population-growth assumption", all_text, fixed=TRUE), "climate migration boundary")
stop_if(grepl("population",all_text,fixed=TRUE) && grepl("household",all_text,fixed=TRUE) && grepl("housing unit",all_text,fixed=TRUE) && grepl("worker",all_text,fixed=TRUE) && grepl("job",all_text,fixed=TRUE) && grepl("commuter",all_text,fixed=TRUE), "population unit boundary")
stop_if(!grepl("vulnerability_score|ej_score|protected_class_rank|risk_score|dose|illness|mortality", paste(names(S),names(R),names(U),names(X),collapse=" "), ignore.case=TRUE), "prohibited score columns")
stop_if(grepl("a2050",all_text,fixed=TRUE) && grepl("a2075",all_text,fixed=TRUE), "horizon rows")
for (sc in c("A","B","C")) {
  stop_if(!identical(A$assumption[A$scenario_id==paste0(sc,"2050")], A$assumption[A$scenario_id==paste0(sc,"2075")]), paste("horizon distinction", sc))
}
stop_if(all(X$projection_use[as.character(X$horizon)=="2050"] == "official 2050 county projection evidence available as reference; no deterministic scenario total"), "2050 projection boundary")
stop_if(all(X$projection_use[as.character(X$horizon)=="2075"] == "explicit scenario only; no mechanical extrapolation"), "2075 scenario boundary")
stop_if(grepl("https://www.census.gov/data/tables/2023/demo/popproj/2023-summary-tables.html", json_text(file.path(reports,"population_settlement_future_sources.md")), fixed=TRUE), "projection source citation")
stop_if(grepl("https://www.noaa.gov/education/resource-collections/climate/climate-change-impacts", json_text(file.path(reports,"population_settlement_future_sources.md")), fixed=TRUE), "climate source citation")

for (base in c("37_population_settlement_futures_2050","37b_population_settlement_futures_2075")) {
  png <- file.path(maps,paste0(base,".png")); svg <- file.path(maps,paste0(base,".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("map files",base))
  txt <- tolower(paste(readLines(svg,warn=FALSE,encoding="UTF-8"),collapse=" "))
  map_id <- if (startsWith(base,"37_")) "map 37" else "map 37b"
  for (term in c(map_id,"population","settlement","connected reconcentration","polycentric adaptive basin","uneven change / infrastructure strain","not population totals","climate migration","commuting")) stop_if(grepl(term,txt,fixed=TRUE), paste("map text",base,term))
}
stop_if(file.info(file.path(figures,"population_settlement_future_comparison.png"))$size > 10000 && file.info(file.path(figures,"population_settlement_future_comparison.svg"))$size > 10000, "comparison figure")
stop_if(check_manifest(file.path(reports,"phase11a_population_settlement_freeze_manifest.json"),14,TRUE)==14, "Phase 11A freeze")
stop_if(check_manifest(file.path(reports,"phase11b_population_mobility_dependencies_freeze_manifest.json"),13,TRUE)==13, "Phase 11B freeze")
future_manifest <- json_text(file.path(reports,"population_settlement_future_manifest.json"))
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"11C"',future_manifest,perl=TRUE) && grepl('"numeric_future_values_adopted"[[:space:]]*:[[:space:]]*false',future_manifest,perl=TRUE) && grepl('"phase12_implemented"[[:space:]]*:[[:space:]]*false',future_manifest,perl=TRUE), "Phase 11C manifest")
cat(sprintf("Phase 11C R validation passed: %d assumptions, %d projection-evidence rows, %d future states, %d relationships, %d uncertainty states, %d comparisons; Maps 37/37b; population-unit, commuting/migration, projection, scenario, freeze, and map boundaries checked\n",nrow(A),nrow(P),nrow(S),nrow(R),nrow(U),nrow(X)))
