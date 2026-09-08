args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
require_review <- "--require-review" %in% args
analysis <- file.path(root, "data", "processed", "analysis")
network <- file.path(root, "data", "processed", "networks")
scenario <- file.path(root, "data", "processed", "scenarios")
figures <- file.path(root, "outputs", "figures")
maps <- file.path(root, "outputs", "maps", "systems")
reports <- file.path(root, "reports")
base_sha <- "e3d5226dcd1f334a41f83bdd10dc5382bd5a0f80"
source_map <- c(v12_ohio_mosquitoes="VFS-001", v12_osu_culex="VFS-002", v12_ohio_ae_japonicus="VFS-003", v12_mi_ae_japonicus="VFS-004", v12_in_ae_albopictus="VFS-005", v12_cdc_mosquito_biology="VFS-006", v12_cdc_mosquito_traps="VFS-007", v12_cdc_ticks_live="VFS-008", v12_cdc_ixodes="VFS-008", v12_cdc_dvariabilis="VFS-009", phase9_climate_context="VFS-010", phase1_hydrology_context="VFS-014", phase6_ecology_context="VFS-015", phase10_governance_context="VFS-016", phase11_population_context="VFS-017", phase7_health_context="VFS-018", phase4_data_context="VFS-019", v12_cdc_wnv_about="VFS-020", v12_ohio_vector_update="VFS-021", v12_cdc_tick_sets="VFS-022", v12_cdc_wnv_data="VFS-023", v12_cdc_lyme="VFS-024", v12_mi_annual_2023="VFS-025", v12_in_wnv_2026="VFS-026", v12_cdc_tick_data="VFS-027", v12_ohio_wnv_map="VFS-028")
habitat_source_map <- c(`HAB-001`="VFS-002", `HAB-003`="VFS-005", `HAB-007`="VFS-008", `HAB-011`="VFS-014", `HAB-012`="VFS-008", `HAB-015`="VFS-002")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_table <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")

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
  if (sha256_file(path) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  canonical <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  tolower(expected) %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", path))
  rel <- character(); hashes <- character(); current <- NA_character_; current_hash <- NA_character_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash) }
    current <<- NA_character_; current_hash <<- NA_character_
  }
  for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit)==3L) { append_current(); rel <- c(rel, hit[[2]]); hashes <- c(hashes, hit[[3]]); next }
    nested <- regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit)==2L) { append_current(); current <- hit[[2]] }
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh)==2L && !is.na(current)) current_hash <- hh[[2]]
  }
  append_current()
  data.frame(rel=rel, sha256=hashes, stringsAsFactors=FALSE)
}

check_manifest <- function(path, expected_n, phase, baseline) {
  stop_if(file.exists(path), paste("missing freeze manifest", path))
  txt <- json_text(path)
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("status", path))
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl=TRUE), paste("phase", path))
  stop_if(grepl(gsub("&", "&", baseline, fixed=TRUE), txt, fixed=TRUE), paste("baseline", path))
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == expected_n, paste("freeze artifact count", path))
  for (i in seq_len(nrow(x))) {
    artifact <- file.path(root, x$rel[[i]])
    stop_if(file.exists(artifact) && portable_match(artifact, x$sha256[[i]]), paste("freeze hash", x$rel[[i]]))
  }
  nrow(x)
}

A <- read_table(file.path(scenario, "vector_ecology_scenario_assumptions.csv"))
V <- read_table(file.path(scenario, "vector_ecology_vector_states_scenario.csv"))
H <- read_table(file.path(scenario, "vector_ecology_habitat_states_scenario.csv"))
S <- read_table(file.path(scenario, "vector_ecology_surveillance_states_scenario.csv"))
D <- read_table(file.path(scenario, "vector_ecology_dependency_states_scenario.csv"))
U <- read_table(file.path(scenario, "vector_ecology_uncertainty_states_scenario.csv"))
X <- read_table(file.path(figures, "vector_ecology_future_comparison.csv"))
SRC <- read_table(file.path(analysis, "vector_ecology_future_sources.csv"))

expected <- list(
  A=c("assumption_id","scenario_id","scenario","horizon","domain","assumption","evidence_basis","source_id","uncertainty","reality_status","canon_status","classification","numeric_future_value_adopted","notes"),
  V=c("state_id","scenario_id","scenario","horizon","baseline_node_id","baseline_name","taxon_or_system","vector_group","baseline_presence_context","seasonal_suitability_state","habitat_opportunity_state","overwintering_or_activity_context","future_range_state","establishment_state","abundance_state","pathogen_state","human_interface_state","current_fact","scenario_assumption","scenario_consequence","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  H=c("state_id","scenario_id","scenario","horizon","baseline_object_id","baseline_association_id","habitat_relationship","vector_group","current_fact","future_suitability_state","habitat_opportunity_state","spatial_pattern","change_type","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  S=c("state_id","scenario_id","scenario","horizon","baseline_object_id","surveillance_dimension","current_fact","surveillance_capacity_state","detection_timing_state","method_and_effort_state","management_response_interface","abundance_inference_boundary","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  D=c("state_id","scenario_id","scenario","horizon","baseline_dependency_id","object_a","object_b","system_a","system_b","relationship_type","spatial_scale","current_fact","scenario_assumption","scenario_consequence","dependency_state","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  U=c("state_id","scenario_id","scenario","horizon","baseline_uncertainty_id","category","subject_id","current_fact","scenario_assumption","uncertainty_state","assumption_id","source_or_basis","reality_status","canon_status","relationship_basis","notes"),
  X=c("scenario_id","scenario","horizon","seasonal_suitability","urban_container_opportunity","standing_water_opportunity","forest_edge_humidity","host_ecology_interface","surveillance_capacity","detection_timing","management_response","spatial_heterogeneity","range_statement","abundance_statement","pathogen_statement","human_interface_statement","scenario_distinctiveness","uncertainty_profile","notes")
)
frames <- list(A=A,V=V,H=H,S=S,D=D,U=U,X=X)
for (nm in names(frames)) stop_if(setequal(names(frames[[nm]]), expected[[nm]]), paste("schema", nm))
stop_if(nrow(A)==36 && nrow(V)==36 && nrow(H)==48 && nrow(S)==30 && nrow(D)==168 && nrow(U)==60 && nrow(X)==6, "Phase 12C counts")
stop_if(!anyDuplicated(A$assumption_id) && !anyDuplicated(V$state_id) && !anyDuplicated(H$state_id) && !anyDuplicated(S$state_id) && !anyDuplicated(D$state_id) && !anyDuplicated(U$state_id) && !anyDuplicated(X$scenario_id), "unique IDs")

scenario_ids <- c("A2050","A2075","B2050","B2075","C2050","C2075")
years <- setNames(as.integer(substr(scenario_ids, 2, 5)), scenario_ids)
for (f in list(A,V,H,S,D,U,X)) {
  stop_if(setequal(unique(f$scenario_id), scenario_ids), "scenario coverage")
  stop_if(all(as.integer(f$horizon) == years[as.character(f$scenario_id)]), "horizon alignment")
}
stop_if(all(table(A$scenario_id)==6) && all(table(V$scenario_id)==6) && all(table(H$scenario_id)==8) && all(table(S$scenario_id)==5) && all(table(D$scenario_id)==28) && all(table(U$scenario_id)==10), "rows per scenario")
stop_if(all(A$reality_status=="fictional") && all(A$canon_status=="scenario") && all(A$classification=="SCENARIO ASSUMPTION") && all(A$numeric_future_value_adopted=="false"), "assumption status")
stop_if(nrow(SRC)==28 && !anyDuplicated(SRC$source_id) && !anyDuplicated(SRC$url), "source registry")
assumptions <- A$assumption_id; source_ids <- SRC$source_id
stop_if(all(A$source_id %in% source_ids) && all(V$source_or_basis %in% source_ids) && all(H$source_or_basis %in% source_ids) && all(S$source_or_basis %in% source_ids) && all(D$source_or_basis %in% source_ids) && all(U$source_or_basis %in% source_ids), "source references")
stop_if(all(V$assumption_id %in% assumptions) && all(H$assumption_id %in% assumptions) && all(S$assumption_id %in% assumptions) && all(D$assumption_id %in% assumptions) && all(U$assumption_id %in% assumptions), "assumption references")
stop_if(all(V$baseline_node_id %in% c("VEC-001","VEC-002","VEC-003","VEC-004","VEC-005","VEC-006")), "vector baseline references")
stop_if(all(H$baseline_object_id %in% c("VEC-009","VEC-001","VEC-008","VEC-011","VEC-010","VEC-012","VEC-013","VEC-014")), "habitat baseline references")
baseline_habitat <- read_table(file.path(analysis,"vector_habitat_associations.csv"))
stop_if(all(H$baseline_association_id %in% baseline_habitat$association_id), "habitat association references")
stop_if(all(V$source_or_basis == unname(c(`VEC-001`="VFS-002", `VEC-002`="VFS-002", `VEC-003`="VFS-001", `VEC-004`="VFS-003", `VEC-005`="VFS-001", `VEC-006`="VFS-008")[V$baseline_node_id])), "vector claim sources")
stop_if(all(H$source_or_basis == unname(habitat_source_map[H$baseline_association_id])) && all(H$current_fact == paste0("CURRENT FACT (2026 baseline): ", baseline_habitat$relationship_description[match(H$baseline_association_id, baseline_habitat$association_id)])), "habitat claim crosswalk")
stop_if(all(S$baseline_object_id %in% c("VEC-015","VEC-016","VEC-017","VEC-018","VDE-017")), "surveillance baseline references")
stop_if(all(S$source_or_basis == ifelse(S$surveillance_dimension == "detection-to-decision interface", "VFS-016", "VFS-007")), "surveillance claim sources")
baseline_dependency <- read_table(file.path(analysis,"vector_system_dependency_register.csv"))
baseline_uncertainty <- read_table(file.path(analysis,"vector_ecology_uncertainty.csv"))
stop_if(all(D$baseline_dependency_id %in% read_table(file.path(analysis,"vector_system_dependency_register.csv"))$dependency_id), "dependency baseline references")
stop_if(all(U$baseline_uncertainty_id %in% read_table(file.path(analysis,"vector_ecology_uncertainty.csv"))$uncertainty_id), "uncertainty baseline references")
stop_if(all(D$source_or_basis == unname(source_map[baseline_dependency$source_id[match(D$baseline_dependency_id, baseline_dependency$dependency_id)]])), "dependency claim sources")
stop_if(all(U$source_or_basis == unname(source_map[baseline_uncertainty$source_id[match(U$baseline_uncertainty_id, baseline_uncertainty$uncertainty_id)]])), "uncertainty claim sources")

for (f in list(V,H,S,D,U)) {
  stop_if(all(f$reality_status=="fictional") && all(f$canon_status=="scenario") && all(f$relationship_basis=="scenario_assumption"), "future status")
}
stop_if(all(grepl("not projected", tolower(V$establishment_state), fixed=TRUE)) && all(grepl("not estimated", tolower(V$abundance_state), fixed=TRUE)) && all(grepl("not modeled", tolower(V$human_interface_state), fixed=TRUE)), "vector boundaries")
stop_if(all(grepl("not abundance", tolower(S$abundance_inference_boundary), fixed=TRUE)), "surveillance boundary")
stop_if(all(grepl("SCENARIO SUITABILITY:", H$future_suitability_state, fixed=TRUE)), "suitability boundary")
stop_if(all(grepl("CURRENT FACT (2026 baseline):", D$current_fact, fixed=TRUE)) && all(grepl("SCENARIO ASSUMPTION:", D$scenario_assumption, fixed=TRUE)) && all(grepl("SCENARIO CONSEQUENCE:", D$scenario_consequence, fixed=TRUE)), "dependency classification")
stop_if(grepl("Great Black Swamp remains C — HOLD / noncanonical", paste(U$uncertainty_state, collapse=" "), fixed=TRUE), "Great Black Swamp hold")

all_text <- tolower(paste(c(capture.output(write.table(A,row.names=FALSE,quote=FALSE)), capture.output(write.table(V,row.names=FALSE,quote=FALSE)), capture.output(write.table(H,row.names=FALSE,quote=FALSE)), capture.output(write.table(S,row.names=FALSE,quote=FALSE)), capture.output(write.table(D,row.names=FALSE,quote=FALSE)), capture.output(write.table(U,row.names=FALSE,quote=FALSE)), capture.output(write.table(X,row.names=FALSE,quote=FALSE))), collapse=" "))
stop_if(grepl("presence",all_text,fixed=TRUE) && grepl("abundance",all_text,fixed=TRUE) && grepl("establishment",all_text,fixed=TRUE) && grepl("pathogen",all_text,fixed=TRUE) && grepl("human-vector",all_text,fixed=TRUE) && grepl("clinical disease",all_text,fixed=TRUE), "evidence ladder")
stop_if(grepl("surveillance intensity",all_text,fixed=TRUE) && grepl("not abundance",all_text,fixed=TRUE), "surveillance not abundance")
stop_if(grepl("suitability",all_text,fixed=TRUE) && grepl("not observed",all_text,fixed=TRUE), "future suitability boundary")
stop_if(grepl("not a midpoint", tolower(paste(X$scenario_distinctiveness, collapse=" ")), fixed=TRUE), "Scenario B distinction")
stop_if(all(A[A$scenario_id=="A2050","assumption"] != A[A$scenario_id=="A2075","assumption"]) && all(V[V$scenario_id=="A2050","seasonal_suitability_state"] != V[V$scenario_id=="A2075","seasonal_suitability_state"]), "horizon distinction A")
stop_if(all(A[A$scenario_id=="B2050","assumption"] != A[A$scenario_id=="B2075","assumption"]) && all(V[V$scenario_id=="B2050","seasonal_suitability_state"] != V[V$scenario_id=="B2075","seasonal_suitability_state"]), "horizon distinction B")
stop_if(all(A[A$scenario_id=="C2050","assumption"] != A[A$scenario_id=="C2075","assumption"]) && all(V[V$scenario_id=="C2050","seasonal_suitability_state"] != V[V$scenario_id=="C2075","seasonal_suitability_state"]), "horizon distinction C")
compare_horizons <- function(frame, columns, scenario_id) {
  left <- frame[frame$scenario_id == paste0(scenario_id, "2050"), columns, drop=FALSE]
  right <- frame[frame$scenario_id == paste0(scenario_id, "2075"), columns, drop=FALSE]
  rownames(left) <- NULL; rownames(right) <- NULL
  !identical(left, right)
}
for (sc in c("A","B","C")) {
  stop_if(compare_horizons(H, c("future_suitability_state","habitat_opportunity_state","spatial_pattern","change_type"), sc), paste("habitat horizon distinction", sc))
  stop_if(compare_horizons(S, c("surveillance_capacity_state","detection_timing_state","method_and_effort_state","management_response_interface"), sc), paste("surveillance horizon distinction", sc))
  stop_if(compare_horizons(D, c("dependency_state","scenario_consequence"), sc), paste("dependency horizon distinction", sc))
  stop_if(compare_horizons(U, c("uncertainty_state"), sc), paste("uncertainty horizon distinction", sc))
  stop_if(compare_horizons(X, c("seasonal_suitability","urban_container_opportunity","standing_water_opportunity","forest_edge_humidity","surveillance_capacity","detection_timing","management_response","spatial_heterogeneity","scenario_distinctiveness","uncertainty_profile"), sc), paste("comparison horizon distinction", sc))
}
stop_if(grepl("mosaic", tolower(paste(X$scenario_distinctiveness, collapse=" ")), fixed=TRUE), "heterogeneity")
stop_if(!grepl("future[[:space:]]+(abundance|prevalence|case|infection)[[:space:]]*[:=][[:space:]]*[0-9]", all_text, perl=TRUE), "unsupported future precision")
stop_if(!grepl("(probability|risk|score|prevalence)[[:space:]]*[:=][[:space:]]*[0-9]", all_text, perl=TRUE), "unsupported score/forecast")

for (internal in SRC$url[grepl("^reports/", SRC$url)]) stop_if(file.exists(file.path(root, internal)), paste("internal source", internal))

map_sizes <- list(); map_texts <- character()
xmllint <- Sys.which("xmllint")
stop_if(nzchar(xmllint), "xmllint required for independent SVG parse")
for (spec in list(c("40_vector_ecology_futures_2050","map 40","2050"), c("40b_vector_ecology_futures_2075","map 40b","2075"))) {
  png <- file.path(maps, paste0(spec[[1]], ".png")); svg <- file.path(maps, paste0(spec[[1]], ".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("map files", spec[[1]]))
  status <- system2(xmllint, c("--noout", svg), stdout=FALSE, stderr=FALSE)
  stop_if(is.null(status) || status == 0, paste("SVG parse", spec[[1]]))
  txt <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c(spec[[2]],spec[[3]],"managed ecological adaptation","heterogeneous adaptive basin","warmer / more variable vector landscape","suitability is not observed distribution","surveillance intensity","not abundance","no exact future range","great black swamp","unresolved")) stop_if(grepl(term,txt,fixed=TRUE), paste("map text",spec[[1]],term))
  map_texts <- c(map_texts, txt)
  map_sizes[[spec[[1]]]] <- as.numeric(file.info(png)$size)
}
normalized_maps <- gsub("map 40b?|2050|2075|2050 intermediate|2075 matured / diverged|emerging|mature|durable|entrenched", "", map_texts, ignore.case=TRUE)
stop_if(length(normalized_maps)==2L && !identical(normalized_maps[[1]], normalized_maps[[2]]), "horizon-specific map content")
for (figure in c(file.path(figures,"vector_ecology_future_comparison.png"),file.path(figures,"vector_ecology_future_comparison.svg"))) stop_if(file.exists(figure) && file.info(figure)$size > 10000, paste("comparison figure",figure))
stop_if(system2(xmllint,c("--noout",file.path(figures,"vector_ecology_future_comparison.svg")),stdout=FALSE,stderr=FALSE)==0,"comparison SVG parse")

citation_source <- readLines(file.path(reports,"vector_ecology_future_sources.md"), warn=FALSE, encoding="UTF-8")
source_text <- paste(citation_source, collapse=" ")
for (url in c("https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/animals/mosquitoes-in-ohio","https://ohioline.osu.edu/factsheet/ent-89","https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html","https://glisa.umich.edu/wp-content/uploads/2025/04/Summary-of-Climate-Change-in-the-Great-Lakes-Region-GLISA-October-2024.pdf","https://loca.ucsd.edu/loca-version-2-for-north-america-ca-jan-2023","https://www.cdc.gov/west-nile-virus/about","https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update","https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html","https://www.cdc.gov/west-nile-virus/data-maps","https://www.cdc.gov/lyme/data-research/facts-stats/index.html","https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf","https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county","https://www.cdc.gov/ticks/data-research/facts-stats","https://ohid.ohio.gov/wps/wcm/connect/gov/ohio+content+english/odh/know-our-programs/zoonotic-disease-program/media/west-nile-virus-map")) stop_if(grepl(url,source_text,fixed=TRUE), paste("source citation",url))

check_manifest(A_FREEZE <- file.path(reports,"phase12a_vector_ecology_freeze_manifest.json"),17,"12A","Vector Ecology Baseline, 2026")
check_manifest(B_FREEZE <- file.path(reports,"phase12b_vector_environment_human_dependencies_freeze_manifest.json"),15,"12B","Vector / Environment / Human-System Dependencies, 2026")
C_FREEZE <- file.path(reports,"phase12c_vector_ecology_futures_freeze_manifest.json")

future_manifest <- file.path(reports,"vector_ecology_future_manifest.json")
future_text <- json_text(future_manifest)
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"12C"',future_text,perl=TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"',future_text,perl=TRUE) && grepl('"phase13_implemented"[[:space:]]*:[[:space:]]*false',future_text,perl=TRUE), "future manifest boundary")
future_artifacts <- manifest_artifacts(future_manifest)
stop_if(nrow(future_artifacts) == if (require_review) 25L else 24L, "future manifest artifact count")
stop_if(grepl("reports/vector_ecology_future_independent_review_initial.md", future_text, fixed=TRUE), "initial review artifact in manifest")
if (require_review) {
  stop_if(grepl("reports/vector_ecology_future_independent_review.md", future_text, fixed=TRUE), "review artifact in manifest")
  review_text <- tolower(json_text(file.path(reports, "vector_ecology_future_independent_review.md")))
  for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"ecological_errors": []','"scenario_boundary_errors": []','"spatial_scale_errors": []','"health_boundary_errors": []')) stop_if(grepl(term, review_text, fixed=TRUE), paste("independent review", term))
}
for (i in seq_len(nrow(future_artifacts))) stop_if(file.exists(file.path(root,future_artifacts$rel[[i]])) && portable_match(file.path(root,future_artifacts$rel[[i]]), future_artifacts$sha256[[i]]), paste("future manifest hash",future_artifacts$rel[[i]]))

prior_files <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
prior_files <- prior_files[!(basename(prior_files) %in% c("phase12a_vector_ecology_freeze_manifest.json","phase12b_vector_environment_human_dependencies_freeze_manifest.json","phase12c_vector_ecology_futures_freeze_manifest.json"))]
protected <- character(); expected_hashes <- character(); prior_entries <- 0L
for (path in sort(prior_files)) {
  x <- manifest_artifacts(path)
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; expected_hash <- x$sha256[[i]]
    if (rel %in% names(expected_hashes)) stop_if(expected_hashes[[rel]] == expected_hash, paste("prior duplicate hash",rel))
    expected_hashes[rel] <- expected_hash
    stop_if(file.exists(file.path(root,rel)) && portable_match(file.path(root,rel),expected_hash), paste("prior hash",rel))
    protected <- c(protected,rel); prior_entries <- prior_entries + 1L
  }
}
stop_if(prior_entries == 298L && length(unique(protected)) == 293L, "prior manifest inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", base_sha), stdout=TRUE, stderr=TRUE)
stop_if(length(intersect(changed, unique(protected))) == 0L, "prior artifact changed in diff")

cat(sprintf("Phase 12C R validation passed: %d assumptions, %d vector states, %d habitat states, %d surveillance states, %d dependency states, %d uncertainty states, %d comparisons; Maps 40/40b parsed; strict schema, assumption/baseline references, scenario boundaries, vector ecology boundaries, Phase 12A/12B freeze integrity, %d prior Phase 1–11 entries/%d unique artifacts, provenance, holds, and no Phase 13 checks passed\n", nrow(A), nrow(V), nrow(H), nrow(S), nrow(D), nrow(U), nrow(X), prior_entries, length(unique(protected))))
