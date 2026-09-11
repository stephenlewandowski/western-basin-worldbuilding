args <- commandArgs(trailingOnly=TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash="/", mustWork=TRUE)
require_review <- "--require-review" %in% args
scenario_dir <- file.path(root, "data", "processed", "scenarios")
analysis <- file.path(root, "data", "processed", "analysis")
reports <- file.path(root, "reports")
figures <- file.path(root, "outputs", "figures")
base_sha <- "b8baa403316e56ce7a1266e1cf37d4839536dabc"

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_table <- function(path) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing table", path))
  read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA"))
}
json_text <- function(path) paste(readLines(path, warn=FALSE, encoding="UTF-8"), collapse=" ")

sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, shQuote(normalizePath(path, winslash="/", mustWork=TRUE)), stdout=TRUE, stderr=TRUE)
    hit <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    stop_if(grepl("^[0-9a-fA-F]{64}$", hit), paste("sha256sum failed", path))
    return(tolower(hit))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "No SHA-256 command available")
  out <- system2(certutil, c("-hashfile", normalizePath(path, winslash="\\", mustWork=TRUE), "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) > 0L, paste("certutil failed", path)); hits[[1]]
}
canonical_raw <- function(raw) {
  txt <- rawToChar(raw)
  charToRaw(gsub("\r\n?", "\n", txt, perl=TRUE))
}
write_raw_temp <- function(raw) { path <- tempfile(); writeBin(raw, path); path }
portable_match <- function(relative, expected) {
  path <- file.path(root, relative)
  stop_if(file.exists(path), paste("missing artifact", relative))
  if (tolower(sha256_file(path)) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  normalized <- canonical_raw(raw)
  normalized_hash <- sha256_file(write_raw_temp(normalized))
  if (tolower(normalized_hash) != tolower(expected)) return(FALSE)
  TRUE
}

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
  if (start < length(lines)) for (line in lines[(start+1L):length(lines)]) {
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
check_manifest <- function(path, phase, expected_n) {
  txt <- json_text(path)
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl=TRUE), paste("phase", path))
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("status", path))
  x <- manifest_entries(path)
  stop_if(nrow(x) == expected_n, paste("artifact count", path))
  for (i in seq_len(nrow(x))) stop_if(portable_match(x$rel[[i]], x$sha256[[i]]), paste("manifest hash", x$rel[[i]]))
  x
}

phase15a <- check_manifest(file.path(reports, "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"), "15A", 30L)
phase14a <- check_manifest(file.path(reports, "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"), "14A", 24L)
phase14b <- check_manifest(file.path(reports, "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"), "14B", 23L)
freeze_files <- list.files(reports, pattern="freeze_manifest\\.json$", full.names=FALSE)
prior_total <- 0L; prior_paths <- character()
for (mf in sort(freeze_files)) {
  x <- manifest_entries(file.path(reports, mf)); stop_if(nrow(x) > 0L, paste("empty manifest", mf))
  for (i in seq_len(nrow(x))) { stop_if(portable_match(x$rel[[i]], x$sha256[[i]]), paste("prior hash", mf, x$rel[[i]])); prior_total <- prior_total + 1L; prior_paths <- c(prior_paths, x$rel[[i]]) }
}
stop_if(prior_total == 565L && length(unique(prior_paths)) == 556L, "prior freeze inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", base_sha), stdout=TRUE, stderr=TRUE)
protected <- unique(c(prior_paths, phase15a$rel, phase14a$rel, phase14b$rel))
stop_if(length(intersect(changed, protected)) == 0L, "protected artifact changed")

ontology_lines <- readLines(file.path(root, "metadata", "atlas_systems.yml"), warn=FALSE, encoding="UTF-8")
system_ids <- unique(sub(".*system_id:[[:space:]]*([^[:space:]]+).*", "\\1", ontology_lines[grepl("^[[:space:]]*- system_id:", ontology_lines)]))
stop_if(length(system_ids) == 13L, "Phase 14 ontology count")
source <- read_table(file.path(analysis, "technology_sources.csv"))
source_ids <- unique(source$source_id)
base_nodes <- read_table(file.path(analysis, "technology_system_nodes.csv"))
family_ids <- unique(base_nodes$technology_family)
stop_if(length(source_ids) == nrow(source) && length(family_ids) == 8L, "Phase 15A source/family registry")

assumptions <- read_table(file.path(scenario_dir, "technology_scenario_assumptions.csv"))
family <- read_table(file.path(scenario_dir, "technology_family_states.csv"))
convergence <- read_table(file.path(scenario_dir, "technology_convergence_relationships.csv"))
systems <- read_table(file.path(scenario_dir, "technology_system_states.csv"))
dependency <- read_table(file.path(scenario_dir, "technology_dependency_states.csv"))
governance <- read_table(file.path(scenario_dir, "technology_governance_states.csv"))
uncertainty <- read_table(file.path(scenario_dir, "technology_uncertainty_states.csv"))
comparison <- read_table(file.path(scenario_dir, "technology_scenario_comparison.csv"))
expected_ids <- c("A2050","A2075","B2050","B2075","C2050","C2075")
check_schema <- function(x, fields) stop_if(setequal(names(x), fields), "schema")
check_schema(assumptions, c("assumption_id", "scenario_id", "scenario_family", "horizon", "axis", "assumption", "evidence_basis", "source_or_basis", "uncertainty", "reality_status", "canon_status", "classification", "numeric_future_value_adopted", "notes"))
check_schema(family, c("state_id", "scenario_id", "scenario_family", "horizon", "technology_family", "baseline_2026_status", "baseline_2026_relevance", "capability_state", "maturity_state", "adoption_state", "infrastructure_state", "interoperability_state", "governance_state", "trust_legitimacy_state", "cybersecurity_state", "workforce_state", "energy_compute_material_state", "privacy_surveillance_state", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(convergence, c("relationship_id", "scenario_id", "scenario_family", "horizon", "technology_family_a", "technology_family_b", "convergence_mechanism", "enabling_conditions", "limiting_conditions", "affected_system_ids", "evidence_basis", "scenario_dependence", "governance_implications", "uncertainty", "second_order_effects", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(systems, c("state_id", "scenario_id", "scenario_family", "horizon", "system_id", "technology_family", "convergence_mechanism", "state_direction", "dependency_change", "governance_effect", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(dependency, c("dependency_state_id", "scenario_id", "scenario_family", "horizon", "system_a", "system_b", "technology_family", "dependency_change_type", "dependency_state", "enabling_conditions", "limiting_conditions", "governance_implication", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(governance, c("governance_state_id", "scenario_id", "scenario_family", "horizon", "governance_domain", "technology_family", "governance_state", "oversight_capacity", "trust_legitimacy_state", "privacy_surveillance_balance", "public_communication_state", "workforce_maintenance_state", "human_authority_boundary", "uncertainty", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(uncertainty, c("uncertainty_state_id", "scenario_id", "scenario_family", "horizon", "uncertainty_domain", "subject", "uncertainty_level", "uncertainty", "scenario_dependence", "what_is_not_inferred", "evidence_basis", "assumption_id", "source_or_basis", "reality_status", "canon_status", "relationship_basis", "notes"))
check_schema(comparison, c("scenario_id", "scenario_family", "horizon", "technology_maturity", "regional_adoption", "infrastructure_adequacy", "interoperability", "governance_capacity", "trust_legitimacy", "cyber_digital_resilience", "workforce_capability", "energy_compute_dependency", "system_coupling", "biosecurity_capacity", "equity_unevenness", "boundary_statement", "notes"))

check_state <- function(x, n, key) {
  stop_if(nrow(x) == n && !anyDuplicated(x[[key]]), paste("count/id", key))
  stop_if(setequal(unique(x$scenario_id), expected_ids) && all(as.integer(x$horizon) == as.integer(substr(x$scenario_id, 2, 5))), paste("scenario/horizon", key))
  stop_if(all(x$assumption_id %in% assumptions$assumption_id) && all(x$source_or_basis %in% source_ids), paste("references", key))
  stop_if(all(x$reality_status == "scenario") && all(x$canon_status == "scenario") && all(x$relationship_basis == "scenario_assumption"), paste("status", key))
}
stop_if(nrow(assumptions) == 48L && !anyDuplicated(assumptions$assumption_id), "assumption count")
stop_if(setequal(unique(assumptions$scenario_id), expected_ids) && all(assumptions$classification == "SCENARIO ASSUMPTION") && all(assumptions$numeric_future_value_adopted == "false"), "assumption boundary")
check_state(family, 48L, "state_id"); check_state(convergence, 60L, "relationship_id"); check_state(systems, 78L, "state_id"); check_state(dependency, 72L, "dependency_state_id"); check_state(governance, 48L, "governance_state_id"); check_state(uncertainty, 60L, "uncertainty_state_id")
stop_if(setequal(unique(family$technology_family), family_ids) && all(table(family$scenario_id) == 8L), "family coverage")
stop_if(setequal(unique(systems$system_id), system_ids) && all(table(systems$scenario_id) == 13L), "system coverage")
stop_if(all(sapply(strsplit(convergence$affected_system_ids, ";", fixed=TRUE), function(x) all(x %in% system_ids))), "convergence systems")
stop_if(all(dependency$system_a %in% system_ids) && all(dependency$system_b %in% system_ids), "dependency systems")
stop_if(all(governance$technology_family %in% family_ids), "governance family")
stop_if(all(uncertainty$source_or_basis %in% source_ids), "uncertainty sources")
stop_if(nrow(comparison) == 6L && setequal(comparison$scenario_id, expected_ids), "comparison coverage")

model_text <- tolower(paste(capture.output(write.table(assumptions, row.names=FALSE, quote=FALSE)), capture.output(write.table(family, row.names=FALSE, quote=FALSE)), capture.output(write.table(convergence, row.names=FALSE, quote=FALSE)), capture.output(write.table(systems, row.names=FALSE, quote=FALSE)), capture.output(write.table(dependency, row.names=FALSE, quote=FALSE)), capture.output(write.table(governance, row.names=FALSE, quote=FALSE)), capture.output(write.table(uncertainty, row.names=FALSE, quote=FALSE)), capture.output(write.table(comparison, row.names=FALSE, quote=FALSE)), collapse=" "))
stop_if(grepl("scenario", model_text, fixed=TRUE) && grepl("not a forecast", model_text, fixed=TRUE), "scenario boundary")
unsupported_percentage <- grepl("^[^\n]*[0-9]+[[:space:]]*%", model_text, perl=TRUE)
if (unsupported_percentage) stop("unsupported percentage", call.=FALSE)
stop_if(grepl("ai recommendation remains advisory", tolower(paste(capture.output(write.table(governance, row.names=FALSE, quote=FALSE)), collapse=" ")), fixed=TRUE), "AI authority boundary")
stop_if(grepl("measurement and observability do not create enforcement", tolower(paste(capture.output(write.table(governance, row.names=FALSE, quote=FALSE)), collapse=" ")), fixed=TRUE), "sensing authority boundary")
stop_if(grepl("defensive", model_text, fixed=TRUE), "defensive cybersecurity")
stop_if(grepl("diagnostic", model_text, fixed=TRUE) && grepl("attribution", model_text, fixed=TRUE) && grepl("no pathogen design", model_text, fixed=TRUE), "biosecurity boundary")

for (name in c("technology_convergence_futures", "technology_cross_system_effects")) {
  png <- file.path(figures, paste0(name, ".png")); svg <- file.path(figures, paste0(name, ".svg"))
  stop_if(file.exists(png) && file.info(png)$size > 10000 && file.exists(svg) && file.info(svg)$size > 10000, paste("figure", name))
  txt <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
  needed <- if (name == "technology_convergence_futures") c("technology convergence futures", "2050", "2075", "no score") else c("cross-system technology effects", "observability", "human authority", "coupling")
  stop_if(all(sapply(needed, function(term) grepl(term, txt, fixed=TRUE))), paste("figure labels", name))
}

manifest <- json_text(file.path(reports, "phase15b_manifest.json"))
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"15B"', manifest, perl=TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', manifest, perl=TRUE), "working manifest")
future <- manifest_entries(file.path(reports, "phase15b_manifest.json"))
for (i in seq_len(nrow(future))) stop_if(portable_match(future$rel[[i]], future$sha256[[i]]), paste("working manifest hash", future$rel[[i]]))
status <- tolower(paste(readLines(file.path(root, "PROJECT_STATUS.md"), warn=FALSE), readLines(file.path(root, "docs", "canon_status.md"), warn=FALSE), readLines(file.path(reports, "current_phase_handoff.md"), warn=FALSE), collapse=" "))
stop_if(grepl("phase 15b", status, fixed=TRUE) && grepl("great black swamp", status, fixed=TRUE) && grepl("unresolved", status, fixed=TRUE), "status surfaces")
if (require_review) {
  stop_if(file.exists(file.path(reports, "phase15b_independent_review.md")), "review record")
  review <- tolower(json_text(file.path(reports, "phase15b_independent_review.md")))
  for (term in c('"passed": true', '"security_concerns": []', '"logic_errors": []', '"provenance_errors": []', '"scenario_boundary_errors": []', '"technology_maturity_errors": []', '"regional_relevance_errors": []', '"governance_boundary_errors": []', '"biosecurity_boundary_errors": []', '"system_integration_errors": []', '"canon_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
}

result <- paste0('{\n  "phase": "15B",\n  "passed": true,\n  "counts": {\n    "assumptions": ', nrow(assumptions), ',\n    "technology_family_states": ', nrow(family), ',\n    "convergence_relationships": ', nrow(convergence), ',\n    "system_states": ', nrow(systems), ',\n    "dependency_states": ', nrow(dependency), ',\n    "governance_states": ', nrow(governance), ',\n    "uncertainty_states": ', nrow(uncertainty), ',\n    "comparison_rows": ', nrow(comparison), ',\n    "phase15a_protected_artifacts": ', nrow(phase15a), ',\n    "phase14a_protected_artifacts": ', nrow(phase14a), ',\n    "phase14b_protected_artifacts": ', nrow(phase14b), ',\n    "prior_freeze_entries": ', prior_total, ',\n    "prior_freeze_unique_paths": ', length(unique(prior_paths)), '\n  }\n}\n')
writeLines(sub("\\n$", "", result), file.path(reports, "phase15b_r_validation_result.json"), useBytes=TRUE)
cat(sprintf("Phase 15B R validation passed: %d assumptions, %d technology-family states, %d convergence relationships, %d system states, %d dependency states, %d governance states, %d uncertainty states, %d comparison rows; 8 technology families, 13 Phase 14 systems, Phase 15A 30-artifact and Phase 14 24/23-artifact integrity, and 565/556 prior freeze integrity verified\n", nrow(assumptions), nrow(family), nrow(convergence), nrow(systems), nrow(dependency), nrow(governance), nrow(uncertainty), nrow(comparison)))
