args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) normalizePath(args[[1]], mustWork=TRUE) else normalizePath(".", mustWork=TRUE)
reports <- file.path(root, "reports")
analysis <- file.path(root, "data", "processed", "analysis")
networks <- file.path(root, "data", "processed", "networks")
maps <- file.path(root, "outputs", "maps", "systems")

source_commit <- "f2abcb45f39f7222b3d1585c3c322937e540bb95"
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg")
phase11_names <- c("phase11a_population_settlement_freeze_manifest.json", "phase11b_population_mobility_dependencies_freeze_manifest.json", "phase11c_population_settlement_futures_freeze_manifest.json")
phase10_names <- c("phase10a_governance_jurisdiction_freeze_manifest.json", "phase10b_governance_dependencies_coordination_freeze_manifest.json", "phase10c_governance_futures_freeze_manifest.json")

expected_a <- c(
  "data/processed/analysis/population_settlement_nodes.csv",
  "data/processed/analysis/population_settlement_observations.csv",
  "data/processed/networks/population_settlement_relationships.csv",
  "data/processed/analysis/population_settlement_sources.csv",
  "data/processed/analysis/population_settlement_uncertainty.csv",
  "outputs/maps/systems/35_population_settlement_2026.png",
  "outputs/maps/systems/35_population_settlement_2026.svg",
  "reports/population_settlement_sources.md",
  "reports/population_settlement_assumptions.md",
  "reports/population_settlement_findings.md",
  "reports/population_settlement_qa.md",
  "reports/population_settlement_baseline_manifest.json",
  "reports/population_settlement_artifact_check.json",
  "reports/population_settlement_independent_review.md"
)
expected_b <- c(
  "data/processed/analysis/population_mobility_observations.csv",
  "data/processed/networks/population_mobility_relationships.csv",
  "data/processed/analysis/population_system_dependency_register.csv",
  "data/processed/analysis/population_system_dependency_matrix.csv",
  "outputs/maps/systems/36_population_mobility_dependencies_2026.png",
  "outputs/maps/systems/36_population_mobility_dependencies_2026.svg",
  "reports/population_mobility_sources.md",
  "reports/population_mobility_assumptions.md",
  "reports/population_mobility_findings.md",
  "reports/population_mobility_qa.md",
  "reports/phase11_working_manifest.json",
  "reports/population_mobility_artifact_check.json",
  "reports/population_settlement_independent_review.md"
)
expected_c <- c(
  "data/processed/scenarios/population_settlement_scenario_assumptions.csv",
  "data/processed/scenarios/population_settlement_projection_evidence.csv",
  "data/processed/scenarios/population_settlement_future_states.csv",
  "data/processed/networks/population_settlement_future_relationships.csv",
  "data/processed/scenarios/population_settlement_future_uncertainty.csv",
  "data/processed/analysis/population_settlement_future_sources.csv",
  "outputs/figures/population_settlement_future_comparison.csv",
  "outputs/figures/population_settlement_future_comparison.png",
  "outputs/figures/population_settlement_future_comparison.svg",
  "outputs/maps/systems/37_population_settlement_futures_2050.png",
  "outputs/maps/systems/37_population_settlement_futures_2050.svg",
  "outputs/maps/systems/37b_population_settlement_futures_2075.png",
  "outputs/maps/systems/37b_population_settlement_futures_2075.svg",
  "reports/population_settlement_future_sources.md",
  "reports/population_settlement_future_assumptions.md",
  "reports/population_settlement_future_findings.md",
  "reports/population_settlement_future_qa.md",
  "reports/population_settlement_future_independent_review.md",
  "reports/population_settlement_future_manifest.json",
  "reports/population_settlement_future_artifact_check.json",
  "src/python/systems/validate_phase11_freezes.py",
  "src/R/systems/validate_phase11_freezes.R"
)

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)

sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stop_if(length(out) >= 1L, paste("sha256sum failed:", path))
    token <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    return(tolower(gsub("[^0-9a-f]", "", token)))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  normalized <- tolower(gsub("[[:space:]]+", "", out))
  hits <- normalized[grepl("^[0-9a-f]{64}$", normalized)]
  stop_if(length(hits) >= 1L, paste("certutil failed:", path))
  hits[[1]]
}

raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_bytes <- function(x) charToRaw(gsub("\r\n?", "\n", rawToChar(x), perl=TRUE))

portable_final_match <- function(path, expected, expected_bytes) {
  stop_if(file.exists(path), paste("Missing artifact:", path))
  raw <- raw_bytes(path)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% text_ext)) return(length(raw) == expected_bytes && sha256_file(path) == expected)
  canonical <- canonical_bytes(raw)
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  # Compare raw, LF-normalized, and CRLF-normalized text bytes.
  lf_tmp <- tempfile(fileext=paste0(".", ext)); crlf_tmp <- tempfile(fileext=paste0(".", ext))
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  hashes <- c(sha256_file(path), sha256_file(lf_tmp), sha256_file(crlf_tmp))
  expected %in% hashes && expected_bytes %in% c(length(raw), length(canonical), length(crlf))
}

portable_against_head <- function(path, relative, expected) {
  stop_if(file.exists(path), paste("Missing prior artifact:", relative))
  if (sha256_file(path) == expected) return(TRUE)
  if (!(tolower(tools::file_ext(path)) %in% text_ext)) return(FALSE)
  accepted_tmp <- tempfile(fileext=paste0(".", tools::file_ext(path))); error_tmp <- tempfile()
  on.exit(unlink(c(accepted_tmp, error_tmp)), add=TRUE)
  status <- system2("git", c("-C", root, "show", paste0("HEAD:", relative)), stdout=accepted_tmp, stderr=error_tmp)
  if (!is.null(status) && status != 0) return(FALSE)
  accepted_raw <- raw_bytes(accepted_tmp)
  working_raw <- raw_bytes(path)
  if (!identical(canonical_bytes(accepted_raw), canonical_bytes(working_raw))) return(FALSE)
  lf_tmp <- tempfile(); crlf_tmp <- tempfile()
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  lf <- canonical_bytes(accepted_raw); crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(lf), fixed=TRUE))
  writeBin(lf, lf_tmp); writeBin(crlf, crlf_tmp)
  expected %in% c(sha256_file(accepted_tmp), sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

manifest_artifacts <- function(path) {
  lines <- readLines(path, warn=FALSE, encoding="UTF-8")
  current <- NA_character_; current_bytes <- NA_real_; current_hash <- NA_character_
  rel <- character(); bytes <- numeric(); hashes <- character()
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) {
      rel <<- c(rel, current); bytes <<- c(bytes, current_bytes); hashes <<- c(hashes, current_hash)
      current <<- NA_character_; current_bytes <<- NA_real_; current_hash <<- NA_character_
    }
  }
  for (line in lines) {
    direct <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hit <- regmatches(line, direct)[[1]]
    if (length(hit) == 3L && grepl("/", hit[[2]], fixed=TRUE)) {
      rel <- c(rel, hit[[2]]); bytes <- c(bytes, NA_real_); hashes <- c(hashes, hit[[3]]); next
    }
    nested <- regexec('^[[:space:]]*"([^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE)
    hit <- regmatches(line, nested)[[1]]
    if (length(hit) == 2L) { append_current(); if (grepl("/", hit[[2]], fixed=TRUE)) current <- hit[[2]] }
    b <- regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE)
    bh <- regmatches(line, b)[[1]]
    if (length(bh) == 2L && !is.na(current)) current_bytes <- as.numeric(bh[[2]])
    h <- regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE)
    hh <- regmatches(line, h)[[1]]
    if (length(hh) == 2L && !is.na(current)) { current_hash <- hh[[2]]; if (!is.na(current_bytes)) append_current() }
  }
  append_current()
  data.frame(rel=rel, bytes=bytes, sha256=hashes, stringsAsFactors=FALSE)
}

manifest_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")
require_fixed <- function(text, value, label) stop_if(grepl(value, text, fixed=TRUE), paste("Missing", label))

verify_final <- function(name, phase, baseline, counts, expected, check_phase12=FALSE) {
  path <- file.path(reports, name)
  stop_if(file.exists(path), paste("Missing final manifest:", name))
  txt <- manifest_text(path)
  require_fixed(txt, paste0('"accepted_phase": "', phase, '"'), paste(name, "phase"))
  require_fixed(txt, paste0('"baseline": "', baseline, '"'), paste(name, "baseline"))
  require_fixed(txt, '"status": "ACCEPTED / FROZEN"', paste(name, "status"))
  require_fixed(txt, '"accepted_by": "Sol explicit acceptance decision supplied for this run"', paste(name, "acceptance"))
  require_fixed(txt, '"accepted_date": "2026-09-08"', paste(name, "date"))
  require_fixed(txt, paste0('"source_commit": "', source_commit, '"'), paste(name, "source commit"))
  for (nm in names(counts)) require_fixed(txt, paste0('"', nm, '": ', counts[[nm]]), paste(name, nm))
  require_fixed(txt, '"phase11c_implemented": false', paste(name, "Phase 11C boundary"))
  if (check_phase12) require_fixed(txt, '"phase12_implemented": false', paste(name, "Phase 12 boundary"))
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == length(expected), paste(name, "artifact count"))
  stop_if(setequal(x$rel, expected), paste(name, "artifact inventory"))
  for (i in seq_len(nrow(x))) stop_if(portable_final_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste(name, x$rel[[i]]))
  x$rel
}

verify_phase11c_final <- function() {
  path <- file.path(reports, "phase11c_population_settlement_futures_freeze_manifest.json")
  txt <- manifest_text(path)
  require_fixed(txt, '"accepted_phase": "11C"', "Phase 11C phase")
  require_fixed(txt, '"baseline": "Population & Settlement Futures, 2050 / 2075"', "Phase 11C baseline")
  require_fixed(txt, '"status": "ACCEPTED / FROZEN"', "Phase 11C status")
  require_fixed(txt, '"accepted_by": "Sol explicit acceptance decision supplied for this run"', "Phase 11C acceptance")
  require_fixed(txt, '"accepted_date": "2026-09-08"', "Phase 11C date")
  require_fixed(txt, '"source_commit": "00c582c0f6204eb7f7a3952d90c2768a30f4bf68"', "Phase 11C source commit")
  for (pair in c('"scenario_assumptions": 36', '"projection_evidence": 6', '"future_states": 108', '"future_relationships": 108', '"uncertainty_states": 36', '"scenario_sources": 11', '"comparison_rows": 6')) require_fixed(txt, pair, "Phase 11C count")
  require_fixed(txt, '"phase11a_11b_immutable": true', "Phase 11A/11B immutability")
  require_fixed(txt, '"phase1_10_immutable": true', "Phase 1–10 immutability")
  require_fixed(txt, '"numeric_future_values_adopted": false', "numeric future boundary")
  require_fixed(txt, '"climate_migration_as_growth_assumption": false', "climate migration boundary")
  require_fixed(txt, '"phase12_implemented": false', "Phase 12 boundary")
  require_fixed(txt, '"great_black_swamp": "C — HOLD / noncanonical"', "Great Black Swamp hold")
  require_fixed(txt, '"toledo_intake_coordinate_discrepancy": "UNRESOLVED"', "Toledo intake discrepancy")
  x <- manifest_artifacts(path)
  stop_if(nrow(x) == length(expected_c), "Phase 11C artifact count")
  stop_if(setequal(x$rel, expected_c), "Phase 11C artifact inventory")
  for (i in seq_len(nrow(x))) stop_if(portable_final_match(file.path(root, x$rel[[i]]), x$sha256[[i]], x$bytes[[i]]), paste("Phase 11C", x$rel[[i]]))
  review <- tolower(paste(readLines(file.path(reports, "population_settlement_future_independent_review.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"statistical_errors": []', '"scenario_boundary_errors": []', '"spatial_scale_errors": []', '"demographic_boundary_errors": []')) require_fixed(review, term, "Phase 11C independent review")
  working <- manifest_text(file.path(reports, "population_settlement_future_manifest.json"))
  require_fixed(working, '"status": "implemented_validated_pending_sol_acceptance"', "working manifest lineage")
  require_fixed(working, '"numeric_future_values_adopted": false', "working manifest numeric boundary")
  require_fixed(working, '"phase12_implemented": false', "working manifest Phase 12 boundary")
  x$rel
}

# Final Phase 11 manifests and their exact accepted inventories.
a_paths <- verify_final(phase11_names[[1]], "11A", "Population & Settlement Baseline, 2026", c(nodes=62L, population_observations=918L, relationships=44L, sources=34L, uncertainties=9L), expected_a)
b_paths <- verify_final(phase11_names[[2]], "11B", "Population, Mobility & System Dependencies, 2026", c(mobility_observations=302L, mobility_relationships=142L, dependency_register=520L, matrix_rows=52L, sources_reused=34L), expected_b, TRUE)
c_paths <- verify_phase11c_final()
stop_if(length(unique(c(a_paths, b_paths, c_paths))) == 48L, "Phase 11 protected-artifact uniqueness")

b_txt <- manifest_text(file.path(reports, phase11_names[[2]])); a_path <- file.path(reports, phase11_names[[1]])
portable_manifest_hashes <- function(path) {
  raw <- raw_bytes(path); canonical <- canonical_bytes(raw)
  lf_tmp <- tempfile()
  on.exit(unlink(lf_tmp), add=TRUE)
  writeBin(canonical, lf_tmp)
  c(sha256_file(path), sha256_file(lf_tmp))
}
a_hashes <- portable_manifest_hashes(a_path)
stop_if(any(vapply(a_hashes, function(h) grepl(paste0('"sha256": "', h, '"'), b_txt, fixed=TRUE), logical(1))), "Phase 11B Phase 11A manifest hash")
a_bytes <- c(file.info(a_path)$size, length(canonical_bytes(raw_bytes(a_path))))
stop_if(any(vapply(a_bytes, function(n) grepl(paste0('"bytes": ', n), b_txt, fixed=TRUE), logical(1))), "Phase 11B Phase 11A manifest bytes")

# Exact accepted package counts and critical vintage/source boundaries.
read_table <- function(path) read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
nodes <- read_table(file.path(analysis, "population_settlement_nodes.csv"))
obs <- read_table(file.path(analysis, "population_settlement_observations.csv"))
settlement_rel <- read_table(file.path(networks, "population_settlement_relationships.csv"))
sources <- read_table(file.path(analysis, "population_settlement_sources.csv"))
unc <- read_table(file.path(analysis, "population_settlement_uncertainty.csv"))
mob <- read_table(file.path(analysis, "population_mobility_observations.csv"))
mob_rel <- read_table(file.path(networks, "population_mobility_relationships.csv"))
dep <- read_table(file.path(analysis, "population_system_dependency_register.csv"))
mat <- read_table(file.path(analysis, "population_system_dependency_matrix.csv"))
stop_if(nrow(nodes)==62L && !anyDuplicated(nodes$node_id), "Phase 11A nodes")
stop_if(nrow(obs)==918L && !anyDuplicated(obs$record_id), "Phase 11A observations")
stop_if(nrow(settlement_rel)==44L && !anyDuplicated(settlement_rel$relationship_id), "Phase 11A relationships")
stop_if(nrow(sources)==34L && !anyDuplicated(sources$source_id), "Phase 11A sources")
stop_if(nrow(unc)==9L && !anyDuplicated(unc$uncertainty_id), "Phase 11A uncertainties")
stop_if(nrow(mob)==302L && !anyDuplicated(mob$record_id), "Phase 11B mobility observations")
stop_if(nrow(mob_rel)==142L && !anyDuplicated(mob_rel$relationship_id), "Phase 11B mobility relationships")
stop_if(nrow(dep)==520L && !anyDuplicated(dep$dependency_id), "Phase 11B dependencies")
stop_if(nrow(mat)==52L && !anyDuplicated(mat$object_id), "Phase 11B matrix")

vintage_ids <- c("s11b_lodes_oh_wac","s11b_lodes_oh_rac","s11b_lodes_oh_od","s11b_lodes_in_wac","s11b_lodes_in_rac","s11b_lodes_in_od","s11b_lodes_mi_wac","s11b_lodes_mi_rac","s11b_lodes_mi_od")
vintage_products <- c("LODES 8.4 WAC 2023","LODES 8.4 RAC 2023","LODES 8.4 OD 2023","LODES 8.4 WAC 2023","LODES 8.4 RAC 2023","LODES 8.4 OD 2023","LODES 8.4 WAC 2021","LODES 8.4 RAC 2023","LODES 8.4 OD 2021")
vintage_reference <- c("2023","2023","2023","2023","2023","2023","2021","2023","2021")
for (i in seq_along(vintage_ids)) {
  row <- sources[sources$source_id == vintage_ids[[i]], , drop=FALSE]
  stop_if(nrow(row)==1L && row$source_product[[1]] == vintage_products[[i]] && as.character(row$reference_year[[1]]) == vintage_reference[[i]] && as.character(row$estimate_period[[1]]) == vintage_reference[[i]], paste("LODES vintage", vintage_ids[[i]]))
}
diffs <- mob[mob$metric == "workplace_residence_difference", , drop=FALSE]
stop_if(nrow(diffs)==16L && !any(grepl("mi_wac_rac", diffs$source_id, fixed=TRUE)), "Michigan WAC/RAC difference exclusion")
for (i in seq_len(nrow(diffs))) {
  row <- sources[sources$source_id == diffs$source_id[[i]], , drop=FALSE]
  stop_if(nrow(row)==1L && diffs$source_product[[i]] == row$source_product[[1]] && as.character(diffs$reference_year[[i]]) == as.character(row$reference_year[[1]]) && as.character(diffs$estimate_period[[i]]) == as.character(row$estimate_period[[1]]), paste("WAC/RAC provenance", i))
}

node_state <- setNames(as.character(nodes$state), as.character(nodes$node_id))
transport_i <- dep$system == "transport"
stop_if(all(dep$documented_or_inferred[transport_i] == "inferred"), "Transport dependency inference boundary")
expected_transport <- paste0("s11b_lodes_", tolower(node_state[as.character(dep$population_or_settlement_object[transport_i])]), "_od")
stop_if(all(dep$source_id[transport_i] == expected_transport), "State-matched transport OD provenance")
water_i <- dep$system == "water"
expected_water <- ifelse(dep$population_or_settlement_object %in% c("POP-ZONE-39095", "MUNI-3977000"), "phase10_s03_toledo_treatment", "phase10_governance_context")
stop_if(all(dep$source_id[water_i] == expected_water[water_i]), "Generalized water dependency scope")
waste_i <- dep$system == "wastewater"
expected_waste <- ifelse(node_state[as.character(dep$population_or_settlement_object)] == "OH", "phase10_s05_ohio_npdes", "phase10_governance_context")
stop_if(all(dep$source_id[waste_i] == expected_waste[waste_i]), "Wastewater dependency scope")

dims <- c("settlement_concentration","mobility_dependency","employment_access","housing_constraint","water_dependency","wastewater_dependency","energy_dependency","transport_dependency","climate_hazard_interface","environmental_health_interface","governance_dependency","service_access","data_certainty")
stop_if(setequal(names(mat), c("object_id","object_type","object_name",dims,"notes")), "Matrix schema")
qual <- c("strong","moderate","limited","unknown","not_applicable")
stop_if(all(vapply(mat[dims], function(x) all(x %in% qual), logical(1))), "Matrix qualitative values")
stop_if(all(grepl("derived from the dependency register", mat$notes, fixed=TRUE)), "Matrix derivation notes")

frames <- list(nodes, obs, settlement_rel, mob, mob_rel, dep, mat)
all_names <- unique(unlist(lapply(frames, names)))
prohibited_columns <- c("risk_score","vulnerability_score","ej_score","protected_class_rank","dose","illness","mortality")
stop_if(!any(prohibited_columns %in% all_names), "Prohibited analytical columns")
frame_text <- function(x) paste(capture.output(write.table(x, row.names=FALSE, quote=FALSE)), collapse=" ")
all_text <- tolower(paste(vapply(frames, frame_text, character(1)), collapse=" "))
stop_if(!grepl("\\b(2050|2075)\\b", all_text, perl=TRUE), "Future population values present")
report_text <- tolower(paste(vapply(c("population_mobility_assumptions.md","population_mobility_findings.md","population_mobility_qa.md"), function(x) paste(readLines(file.path(reports,x), warn=FALSE, encoding="UTF-8"), collapse=" "), character(1)), collapse=" "))
stop_if(grepl("commuting is not migration", report_text, fixed=TRUE) || grepl("not migration", report_text, fixed=TRUE), "Commuting/migration boundary")
stop_if(grepl("workplace", report_text, fixed=TRUE) && grepl("residence", report_text, fixed=TRUE), "Workplace/residence boundary")
stop_if(grepl("dependency", report_text, fixed=TRUE) && grepl("vulnerability", report_text, fixed=TRUE), "Dependency/vulnerability boundary")

for (base in c("35_population_settlement_2026", "36_population_mobility_dependencies_2026")) {
  png <- file.path(maps, paste0(base, ".png")); svg <- file.path(maps, paste0(base, ".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("Map files", base))
  svg_text <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
  required <- if (startsWith(base, "35")) c("map 35","population","settlement") else c("map 36","mobility","commuting","employment","migration","vulnerability")
  stop_if(all(vapply(required, function(term) grepl(term, svg_text, fixed=TRUE), logical(1))), paste("Map text", base))
}
review <- tolower(paste(readLines(file.path(reports, "population_settlement_independent_review.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
for (term in c("passed: true","security_concerns: []","logic_errors: []","provenance_errors: []","statistical_errors: []","spatial_scale_errors: []","demographic_boundary_errors: []","non-blocking suggestions")) require_fixed(review, term, "independent review")

# Verify all three accepted Phase 10 freeze manifests independently.
phase10_counts <- list(
  c(actors=40L, authorities=100L, relationships=100L, sources=48L, uncertainties=16L),
  c(dependency_register=25L, dependency_edges=25L, coordination_mechanisms=14L, matrix_rows=10L, sources_reused=48L),
  c(scenario_assumptions=48L, actor_states=120L, authority_states=90L, dependency_states=150L, coordination_states=84L, uncertainty_states=96L, scenario_sources=19L, comparison_rows=6L)
)
phase10_entries <- 0L; phase10_paths <- character()
for (i in seq_along(phase10_names)) {
  p <- file.path(reports, phase10_names[[i]]); txt <- manifest_text(p)
  require_fixed(txt, '"status": "ACCEPTED / FROZEN"', paste(phase10_names[[i]], "status"))
  for (nm in names(phase10_counts[[i]])) require_fixed(txt, paste0('"', nm, '": ', phase10_counts[[i]][[nm]]), paste(phase10_names[[i]], nm))
  x <- manifest_artifacts(p)
  expected_n <- c(15L,15L,23L)[[i]]
  stop_if(nrow(x) == expected_n, paste(phase10_names[[i]], "artifact count"))
  for (j in seq_len(nrow(x))) {
    stop_if(portable_final_match(file.path(root, x$rel[[j]]), x$sha256[[j]], x$bytes[[j]]), paste(phase10_names[[i]], x$rel[[j]]))
    phase10_paths <- c(phase10_paths, x$rel[[j]])
    phase10_entries <- phase10_entries + 1L
  }
}
stop_if(phase10_entries == 53L && length(unique(phase10_paths)) == 49L, "Phase 10 protected-artifact inventory")
phase10_b_text <- manifest_text(file.path(reports, phase10_names[[2]])); phase10_a_path <- file.path(reports, phase10_names[[1]])
require_fixed(phase10_b_text, paste0('"sha256": "', sha256_file(phase10_a_path), '"'), "Phase 10B Phase 10A manifest hash")
require_fixed(phase10_b_text, paste0('"bytes": ', file.info(phase10_a_path)$size), "Phase 10B Phase 10A manifest bytes")

# Verify the 196 protected Phase 1–9 artifacts and that the acceptance diff does not touch them.
prior_names <- list.files(reports, pattern="^phase.*_freeze_manifest[.]json$", full.names=FALSE)
prior_names <- prior_names[!(prior_names %in% c(phase10_names, phase11_names))]
prior_paths <- character(); prior_total <- 0L
for (name in prior_names) {
  x <- manifest_artifacts(file.path(reports, name)); stop_if(nrow(x) > 0L, paste("Empty prior manifest", name))
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; p <- file.path(root, rel)
    stop_if(!any(rel %in% prior_paths), paste("Prior manifest overlap", rel))
    stop_if(!any(rel %in% phase10_paths), paste("Prior/Phase 10 overlap", rel))
    ok <- if (is.na(x$bytes[[i]]) || !is.finite(x$bytes[[i]])) portable_against_head(p, rel, x$sha256[[i]]) else portable_final_match(p, x$sha256[[i]], x$bytes[[i]])
    stop_if(ok, paste("Prior artifact hash", rel))
    prior_paths <- c(prior_paths, rel); prior_total <- prior_total + 1L
  }
}
stop_if(prior_total == 196L && length(unique(prior_paths)) == 196L, "Phase 1–9 protected-artifact inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", source_commit), stdout=TRUE, stderr=TRUE)
stop_if(!any(changed %in% prior_paths), "Acceptance diff changed a prior protected artifact")
stop_if(!any(prior_paths %in% unique(c(a_paths, b_paths, c_paths, phase10_paths))), "Current protected scope overlaps prior artifacts")

# Status and hold readback is part of the freeze boundary.
status_files <- c("PROJECT_STATUS.md","docs/canon_status.md","docs/phase_briefs/phase11a_population_settlement_baseline.md","docs/phase_briefs/phase11b_population_mobility_dependencies.md","docs/phase_briefs/phase11c_population_settlement_futures.md","reports/current_phase_handoff.md","README.md","CHANGELOG.md","reports/README.md")
for (rel in status_files) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("phase 11a", txt, fixed=TRUE) && grepl("phase 11b", txt, fixed=TRUE) && grepl("accepted / frozen", txt, fixed=TRUE) && grepl("phase 11c", txt, fixed=TRUE), paste("Status record", rel))
}
for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("active phase", txt, fixed=TRUE) && grepl("none", txt, fixed=TRUE) && grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE) && grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("Hold/status record", rel))
}

cat(sprintf("Phase 11 freeze R validation passed: 11A %d artifacts, 11B %d artifacts, and 11C %d artifacts; 62 nodes, 918 observations, 44 relationships, 34 sources, 9 uncertainties; 302 mobility observations, 142 mobility relationships, 520 dependency rows, 52 matrix rows; Phase 10 %d entries/%d unique artifacts; Phase 1–9 %d protected artifacts; maps, review, vintages, boundaries, holds, Phase 11C acceptance, and Phase 12 absence checked\n", length(a_paths), length(b_paths), length(c_paths), phase10_entries, length(unique(phase10_paths)), prior_total))
