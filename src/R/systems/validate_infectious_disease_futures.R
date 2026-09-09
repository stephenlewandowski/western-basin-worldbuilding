args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args) && !grepl("^--", args[[1]])) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
require_review <- "--require-review" %in% args
analysis <- file.path(root, "data", "processed", "analysis")
network <- file.path(root, "data", "processed", "networks")
scenario <- file.path(root, "data", "processed", "scenarios")
figures <- file.path(root, "outputs", "figures")
maps <- file.path(root, "outputs", "maps", "systems")
reports <- file.path(root, "reports")
base_sha <- "769909604caf7596d3736fd07e616ad5f3f1cba1"

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_table <- function(path) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing table", path))
  read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
}
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
sha256_file <- function(path) {
  path <- normalizePath(path, winslash="/", mustWork=TRUE)
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    hit <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    stop_if(grepl("^[0-9a-fA-F]{64}$", hit), paste("sha256sum failed", path))
    return(tolower(hit))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path)); hits[[1]]
}
canonical_raw <- function(raw) {
  txt <- rawToChar(raw)
  charToRaw(gsub("\r\n?", "\n", txt, perl=TRUE))
}
portable_match <- function(relative, expected) {
  path <- file.path(root, relative)
  if (tolower(sha256_file(path)) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  blob <- tempfile(); on.exit(unlink(blob), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", relative)), stdout=blob, stderr=FALSE)
  if (!identical(status, 0L) && !identical(status, 0)) return(FALSE)
  accepted <- readBin(blob, "raw", n=as.numeric(file.info(blob)$size))
  normalized <- canonical_raw(raw); accepted_normalized <- canonical_raw(accepted)
  if (!identical(normalized, accepted_normalized)) return(FALSE)
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(normalized), fixed=TRUE))
  tolower(expected) %in% c(sha256_file(path), sha256_file(write_temp(normalized)), sha256_file(write_temp(crlf)), tolower(sha256_raw(accepted)))
}
# These helpers keep portability checks binary-safe by hashing temporary raw bytes.
write_temp <- function(raw) { path <- tempfile(); writeBin(raw, path); path }
sha256_raw <- function(raw) { path <- write_temp(raw); on.exit(unlink(path), add=TRUE); sha256_file(path) }

manifest_entries <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  collection <- if (any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"'), lines, fixed=TRUE) & grepl("{", lines, fixed=TRUE))[1]
  stop_if(!is.na(start), paste("missing artifact collection", path))
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
check_manifest <- function(path, phase, expected_n, require_status=TRUE) {
  txt <- json_text(path)
  if (require_status) stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("status", path))
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl=TRUE), paste("phase", path))
  x <- manifest_entries(path)
  stop_if(nrow(x) == expected_n, paste("artifact count", path))
  for (i in seq_len(nrow(x))) stop_if(portable_match(x$rel[[i]], x$sha256[[i]]), paste("manifest hash", x$rel[[i]]))
  x
}

A_FREEZE <- file.path(reports, "phase13a_infectious_disease_freeze_manifest.json")
B_FREEZE <- file.path(reports, "phase13b_infectious_disease_dependencies_freeze_manifest.json")
A <- check_manifest(A_FREEZE, "13A", 25)
B <- check_manifest(B_FREEZE, "13B", 24)
A_txt <- json_text(A_FREEZE); B_txt <- json_text(B_FREEZE)
stop_if(grepl("Infectious Disease System Baseline, 2026", A_txt, fixed=TRUE), "Phase 13A baseline")
stop_if(grepl("Environmental & Human-System Transmission Dependencies, 2026", B_txt, fixed=TRUE), "Phase 13B baseline")
stop_if(grepl('"phase13c_implemented"[[:space:]]*:[[:space:]]*false', A_txt, perl=TRUE) && grepl('"phase13c_implemented"[[:space:]]*:[[:space:]]*false', B_txt, perl=TRUE), "prior 13C boundary")

prior_files <- c(
  "reports/phase3a_freeze_manifest.json", "reports/phase3b_freeze_manifest.json", "reports/phase4b_information_freeze_manifest.json", "reports/phase4c_information_freeze_manifest.json",
  "reports/phase5a_freight_freeze_manifest.json", "reports/phase5b_freight_evidence_freeze_manifest.json", "reports/phase5c_freight_dependency_freeze_manifest.json",
  "reports/phase6a_ecology_freeze_manifest.json", "reports/phase6b_ecological_dependency_freeze_manifest.json", "reports/phase6c_ecological_futures_freeze_manifest.json", "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
  "reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json", "reports/phase8b_biogeochemical_dependencies_controls_freeze_manifest.json", "reports/phase8c_biogeochemical_futures_freeze_manifest.json",
  "reports/phase9a_climate_natural_hazards_freeze_manifest.json", "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json", "reports/phase9c_climate_hazard_futures_freeze_manifest.json",
  "reports/phase10a_governance_jurisdiction_freeze_manifest.json", "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", "reports/phase10c_governance_futures_freeze_manifest.json",
  "reports/phase11a_population_settlement_freeze_manifest.json", "reports/phase11b_population_mobility_dependencies_freeze_manifest.json", "reports/phase11c_population_settlement_futures_freeze_manifest.json",
  "reports/phase12a_vector_ecology_freeze_manifest.json", "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json", "reports/phase12c_vector_ecology_futures_freeze_manifest.json"
)
protected <- character(); expected_hashes <- character(); prior_entries <- 0L
for (mf in sort(prior_files)) {
  x <- manifest_entries(file.path(root, mf)); stop_if(nrow(x) > 0, paste("empty prior manifest", mf))
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; expected <- x$sha256[[i]]
    if (rel %in% names(expected_hashes)) stop_if(expected_hashes[[rel]] == expected, paste("duplicate prior hash", rel))
    expected_hashes[[rel]] <- expected
    stop_if(portable_match(rel, expected), paste("prior hash", rel))
    protected <- c(protected, rel); prior_entries <- prior_entries + 1L
  }
}
stop_if(prior_entries == 358L && length(unique(protected)) == 351L, "prior freeze inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", base_sha), stdout=TRUE, stderr=TRUE)
stop_if(length(intersect(changed, unique(c(protected, A$rel, B$rel)))) == 0L, "protected artifact changed")

assumptions <- read_table(file.path(scenario, "infectious_disease_scenario_assumptions.csv"))
transmission <- read_table(file.path(scenario, "infectious_disease_transmission_states_scenario.csv"))
surveillance <- read_table(file.path(scenario, "infectious_disease_surveillance_states_scenario.csv"))
response <- read_table(file.path(scenario, "infectious_disease_response_states_scenario.csv"))
dependencies <- read_table(file.path(scenario, "infectious_disease_dependency_states_scenario.csv"))
uncertainty <- read_table(file.path(scenario, "infectious_disease_uncertainty_states_scenario.csv"))
sources <- read_table(file.path(analysis, "infectious_disease_scenario_sources.csv"))
comparison <- read_table(file.path(figures, "infectious_disease_scenario_comparison.csv"))
expected <- list(
  assumptions=c("assumption_id","scenario_id","scenario","horizon","domain","assumption","evidence_basis","source_id","uncertainty","reality_status","canon_status","classification","numeric_future_value_adopted","notes"),
  transmission=c("state_id","scenario_id","scenario","horizon","archetype","baseline_system_ids","transmission_opportunity_state","environmental_interface_state","seasonal_or_contact_window","host_or_setting_interface","observability_boundary","current_fact","scenario_assumption","scenario_consequence","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  surveillance=c("state_id","scenario_id","scenario","horizon","archetype","baseline_surveillance_ids","surveillance_capacity_state","detection_latency_state","coverage_and_method_state","observation_interface","reported_observation_boundary","current_fact","scenario_assumption","scenario_consequence","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  response=c("state_id","scenario_id","scenario","horizon","archetype","baseline_response_interfaces","healthcare_public_health_capacity","response_coordination_state","response_latency_margin","intervention_interface","infrastructure_dependency_state","response_boundary","current_fact","scenario_assumption","scenario_consequence","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  dependencies=c("state_id","scenario_id","scenario","horizon","archetype","baseline_dependency_id","dependency_domain","object_a","object_b","relationship_type","spatial_scale","current_fact","scenario_assumption","scenario_consequence","dependency_state","assumption_id","source_or_basis","plausibility","uncertainty","reality_status","canon_status","relationship_basis","notes"),
  uncertainty=c("state_id","scenario_id","scenario","horizon","archetype","baseline_uncertainty_id","category","subject_id","current_fact","scenario_assumption","uncertainty_state","assumption_id","source_or_basis","reality_status","canon_status","relationship_basis","notes"),
  comparison=c("scenario_id","scenario","horizon","transmission_opportunity","environmental_interfaces","surveillance_detection","response_coordination","healthcare_response_margin","mobility_connectivity","infrastructure_dependencies","food_freight_interfaces","vector_water_systems","uncertainty_profile","boundary_statement","scenario_distinctiveness","notes")
)
frames <- list(assumptions=assumptions, transmission=transmission, surveillance=surveillance, response=response, dependencies=dependencies, uncertainty=uncertainty, comparison=comparison)
for (nm in names(frames)) stop_if(setequal(names(frames[[nm]]), expected[[nm]]), paste("schema", nm))
stop_if(nrow(assumptions)==36L && nrow(transmission)==36L && nrow(surveillance)==36L && nrow(response)==36L && nrow(dependencies)==36L && nrow(uncertainty)==36L && nrow(sources)==33L && nrow(comparison)==6L, "scenario counts")
scenario_ids <- c("A2050","A2075","B2050","B2075","C2050","C2075")
years <- setNames(as.integer(substr(scenario_ids, 2, 5)), scenario_ids)
for (f in frames) {
  stop_if(setequal(unique(f$scenario_id), scenario_ids), "scenario coverage")
  stop_if(all(as.integer(f$horizon) == years[as.character(f$scenario_id)]), "horizon alignment")
  stop_if(all(nchar(as.character(f$notes)) > 0), "notes")
}
stop_if(all(table(assumptions$scenario_id)==6L) && all(table(transmission$scenario_id)==6L) && all(table(surveillance$scenario_id)==6L) && all(table(response$scenario_id)==6L) && all(table(dependencies$scenario_id)==6L) && all(table(uncertainty$scenario_id)==6L), "rows per state")
stop_if(!anyDuplicated(assumptions$assumption_id) && !anyDuplicated(transmission$state_id) && !anyDuplicated(surveillance$state_id) && !anyDuplicated(response$state_id) && !anyDuplicated(dependencies$state_id) && !anyDuplicated(uncertainty$state_id) && !anyDuplicated(comparison$scenario_id), "unique IDs")
stop_if(all(assumptions$reality_status=="fictional") && all(assumptions$canon_status=="scenario") && all(assumptions$classification=="SCENARIO ASSUMPTION") && all(assumptions$numeric_future_value_adopted=="false"), "assumption status")
stop_if(all(sources$source_id %in% sources$source_id) && !anyDuplicated(sources$source_id) && !anyDuplicated(sources$url), "source registry")
source_ids <- sources$source_id; assumption_ids <- assumptions$assumption_id
for (f in list(transmission, surveillance, response, dependencies, uncertainty)) {
  stop_if(all(f$source_or_basis %in% source_ids) && all(f$assumption_id %in% assumption_ids) && all(f$reality_status=="fictional") && all(f$canon_status=="scenario") && all(f$relationship_basis=="scenario_assumption"), "state references/status")
}
stop_if(all(assumptions$source_id %in% source_ids), "assumption sources")
node_ids <- read_table(file.path(network, "infectious_disease_nodes.csv"))$node_id
dep_ids <- read_table(file.path(analysis, "infectious_disease_dependency_register.csv"))$dependency_id
unc_ids <- read_table(file.path(analysis, "infectious_disease_dependency_uncertainties.csv"))$uncertainty_id
split_member <- function(values, allowed) all(sapply(strsplit(as.character(values), ";", fixed=TRUE), function(x) all(x %in% allowed)))
stop_if(split_member(transmission$baseline_system_ids, node_ids), "transmission baseline references")
stop_if(split_member(surveillance$baseline_surveillance_ids, node_ids), "surveillance baseline references")
stop_if(all(dependencies$baseline_dependency_id %in% dep_ids) && all(uncertainty$baseline_uncertainty_id %in% unc_ids), "dependency/uncertainty references")
stop_if(all(transmission$transmission_opportunity_state != "") && all(grepl("opportunity", transmission$transmission_opportunity_state, ignore.case=TRUE)) && all(grepl("remain separate", transmission$observability_boundary, ignore.case=TRUE)), "transmission states")
stop_if(all(nchar(surveillance$surveillance_capacity_state)>0) && all(grepl("observations", surveillance$reported_observation_boundary, ignore.case=TRUE)) && all(grepl("disease", surveillance$reported_observation_boundary, ignore.case=TRUE)), "surveillance states")
stop_if(all(nchar(response$healthcare_public_health_capacity)>0) && all(grepl("not", response$response_boundary, ignore.case=TRUE)), "response states")
stop_if(all(grepl("CURRENT FACT (2026 baseline):", dependencies$current_fact, fixed=TRUE)) && all(grepl("SCENARIO ASSUMPTION:", dependencies$scenario_assumption, fixed=TRUE)) && all(grepl("SCENARIO CONSEQUENCE:", dependencies$scenario_consequence, fixed=TRUE)), "dependency prefixes")
stop_if(all(grepl("CURRENT FACT (2026 baseline):", uncertainty$current_fact, fixed=TRUE)) && all(grepl("Great Black Swamp remains C — HOLD / noncanonical", uncertainty$uncertainty_state, fixed=TRUE)) && all(grepl("Toledo intake-coordinate discrepancy remains UNRESOLVED", uncertainty$uncertainty_state, fixed=TRUE)), "uncertainty states")

all_text <- tolower(paste(capture.output(write.table(frames$assumptions, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$transmission, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$surveillance, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$response, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$dependencies, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$uncertainty, row.names=FALSE, quote=FALSE)), capture.output(write.table(frames$comparison, row.names=FALSE, quote=FALSE)), collapse=" "))
for (term in c("pathogen presence", "reported case", "local transmission", "transmission opportunity ≠ future incidence", "environmental suitability ≠ disease burden", "surveillance sensitivity is not disease intensity", "infrastructure stress ≠ illness", "mobility/connectivity ≠ outbreak", "more detection and reporting can produce more recorded observations without implying more underlying disease", "not a midpoint", "no future case total", "no unsupported local downscaling")) stop_if(grepl(term, all_text, fixed=TRUE), paste("boundary", term))
stop_if(!grepl("future[[:space:]]+[^\n]{0,140}(case|incidence|outbreak probability)[^\n]{0,30}[0-9]", all_text, perl=TRUE), "future precision negative check")
stop_if(!grepl("(climate|vector suitability|surveillance|mobility|contamination|infrastructure stress)[[:space:]]+(causes|determines|proves|equals)[[:space:]]+(infection|disease|incidence|outbreak|burden)", all_text, perl=TRUE), "boundary negative check")
for (sc in c("A","B","C")) {
  for (spec in list(list(f=transmission, cols=c("transmission_opportunity_state","environmental_interface_state","seasonal_or_contact_window")), list(f=surveillance, cols=c("surveillance_capacity_state","detection_latency_state","coverage_and_method_state")), list(f=response, cols=c("healthcare_public_health_capacity","response_coordination_state","response_latency_margin")), list(f=dependencies, cols=c("dependency_state","scenario_consequence")), list(f=uncertainty, cols=c("uncertainty_state")), list(f=comparison, cols=c("transmission_opportunity","surveillance_detection","response_coordination","uncertainty_profile")))) {
    left <- spec$f[spec$f$scenario_id == paste0(sc,"2050"), spec$cols, drop=FALSE]; right <- spec$f[spec$f$scenario_id == paste0(sc,"2075"), spec$cols, drop=FALSE]; rownames(left)<-NULL; rownames(right)<-NULL
    stop_if(!identical(left, right), paste("horizon distinction", sc))
  }
}
stop_if(grepl("heterogeneous", tolower(paste(assumptions$assumption[grepl("^B", assumptions$scenario_id)], collapse=" ")), fixed=TRUE) && grepl("more permissive", tolower(paste(assumptions$assumption[grepl("^C", assumptions$scenario_id)], collapse=" ")), fixed=TRUE), "scenario structure")

for (spec in list(c("43_infectious_disease_system_futures_2050","map 43","2050","2050 intermediate trajectory"), c("43b_infectious_disease_system_futures_2075","map 43b","2075","2075 matured / diverged system state"))) {
  png <- file.path(maps, paste0(spec[[1]], ".png")); svg <- file.path(maps, paste0(spec[[1]], ".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("map files", spec[[1]]))
  sig <- paste(sprintf("%02x", as.integer(readBin(png, "raw", n=8))), collapse="")
  stop_if(sig == "89504e470d0a1a0a", paste("PNG signature", spec[[1]]))
  xmllint <- Sys.which("xmllint"); stop_if(nzchar(xmllint), "xmllint required")
  stop_if(identical(system2(xmllint, c("--noout", svg), stdout=FALSE, stderr=FALSE), 0L), paste("SVG parse", spec[[1]]))
  txt <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c(spec[[2]], spec[[3]], spec[[4]], "infectious disease system futures", "vector-borne", "waterborne / environmental", "foodborne / enteric", "respiratory", "zoonotic", "healthcare / amr", "opportunity", "surveillance / detection", "response", "dependency", "uncertainty", "not a geographic risk surface", "future incidence", "disease burden", "great black swamp", "toledo intake-coordinate discrepancy")) stop_if(grepl(term, txt, fixed=TRUE), paste("map text", spec[[1]], term))
}
stop_if(file.exists(COMPARISON_PNG <- file.path(figures, "infectious_disease_scenario_comparison.png")) && file.info(COMPARISON_PNG)$size > 10000, "comparison PNG")
COMPARISON_SVG <- file.path(figures, "infectious_disease_scenario_comparison.svg"); stop_if(file.exists(COMPARISON_SVG) && file.info(COMPARISON_SVG)$size > 10000, "comparison SVG")
stop_if(identical(system2(Sys.which("xmllint"), c("--noout", COMPARISON_SVG), stdout=FALSE, stderr=FALSE), 0L), "comparison SVG parse")

for (name in c("infectious_disease_scenario_sources.md", "infectious_disease_scenario_assumptions.md", "infectious_disease_scenario_findings.md", "infectious_disease_scenario_qa.md")) {
  citation_text <- paste(readLines(file.path(reports, name), warn=FALSE, encoding="UTF-8"), collapse=" ")
  stop_if(grepl("## Sources", citation_text, fixed=TRUE) && grepl("[1]", citation_text, fixed=TRUE), paste("citation", name))
}

manifest_txt <- json_text(file.path(reports, "infectious_disease_scenario_manifest.json"))
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"13C"', manifest_txt, perl=TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', manifest_txt, perl=TRUE), "scenario manifest")
future_entries <- manifest_entries(file.path(reports, "infectious_disease_scenario_manifest.json"))
stop_if(nrow(future_entries) == if (require_review) 24L else 23L, "scenario manifest artifact count")
for (i in seq_len(nrow(future_entries))) stop_if(portable_match(future_entries$rel[[i]], future_entries$sha256[[i]]), paste("scenario manifest hash", future_entries$rel[[i]]))
if (require_review) {
  review <- tolower(json_text(file.path(reports, "infectious_disease_scenario_independent_review.md")))
  for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"epidemiological_errors": []', '"scenario_boundary_errors": []', '"surveillance_errors": []', '"spatial_scale_errors": []', '"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
}
for (relative in c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, relative), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("phase 13c", txt, fixed=TRUE) && grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE) && grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("status surface", relative))
}
for (base in c(scenario, maps, file.path(root,"src","python","systems"), file.path(root,"src","R","systems"))) {
  files <- list.files(base, recursive=TRUE, full.names=TRUE)
  stop_if(!any(grepl("phase14|phase_14", tolower(basename(files)))), paste("Phase 14 implementation", base))
}
cat(sprintf("Phase 13C R validation passed: %d assumptions, %d transmission states, %d surveillance states, %d response states, %d dependency states, %d uncertainty states, %d sources, %d comparisons; Maps 43/43b and comparison figure parsed; strict scenario boundaries, provenance, Phase 13A/13B freeze integrity, prior inventory %d/%d, active holds, and no Phase 14 implementation verified\n", nrow(assumptions), nrow(transmission), nrow(surveillance), nrow(response), nrow(dependencies), nrow(uncertainty), nrow(sources), nrow(comparison), prior_entries, length(unique(protected))))
