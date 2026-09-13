args <- commandArgs(trailingOnly=TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash="/", mustWork=TRUE)
require_review <- "--require-review" %in% args
integration <- file.path(root, "data", "processed", "integration")
scenarios <- file.path(root, "data", "processed", "scenarios")
reports <- file.path(root, "reports")
figures <- file.path(root, "outputs", "figures")
metadata <- file.path(root, "metadata")
base_sha <- "038669819731b2206f74a078f6b652ebafacb007"
architecture_lineage_prefix <- "metadata/atlas_systems.yml#architecture.interfaces:"

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
portable_match <- function(relative, expected) {
  path <- file.path(root, relative)
  stop_if(file.exists(path), paste("missing artifact", relative))
  if (tolower(sha256_file(path)) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r"))) return(FALSE)
  raw <- readBin(path, "raw", n=as.numeric(file.info(path)$size))
  txt <- rawToChar(raw)
  normalized <- charToRaw(gsub("\r\n?", "\n", txt, perl=TRUE))
  tmp <- tempfile(); writeBin(normalized, tmp)
  tolower(sha256_file(tmp)) == tolower(expected)
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
check_freeze <- function(path, phase, expected_n) {
  txt <- json_text(path)
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl=TRUE), paste("phase", path))
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl=TRUE), paste("status", path))
  x <- manifest_entries(path)
  stop_if(nrow(x) == expected_n, paste("artifact count", path))
  for (i in seq_len(nrow(x))) stop_if(portable_match(x$rel[[i]], x$sha256[[i]]), paste("manifest hash", x$rel[[i]]))
  x
}
extract_refs <- function(text, pattern) {
  m <- gregexpr(pattern, text, perl=TRUE)[[1]]
  if (m[[1]] == -1L) character() else regmatches(text, list(m))[[1]]
}
compatible_output <- function(source, output) {
  allowed <- list(
    OBSERVED_DOCUMENTED=c("OBSERVED_DOCUMENTED", "INFERRED", "CONTEXT_REUSED"),
    INFERRED=c("INFERRED", "CONTEXT_REUSED"),
    CONTEXT_REUSED=c("INFERRED", "CONTEXT_REUSED"),
    SCENARIO_STATE=c("SCENARIO_STATE", "SCENARIO_ASSUMPTION"),
    SCENARIO_ASSUMPTION=c("SCENARIO_STATE", "SCENARIO_ASSUMPTION")
  )
  source %in% names(allowed) && output %in% allowed[[source]]
}
endpoint_compatible <- function(actual_source, actual_target, expected_source, expected_target, explicitly_undirected=FALSE) {
  ordered <- isTRUE(actual_source == expected_source && actual_target == expected_target)
  reversed <- isTRUE(explicitly_undirected) && isTRUE(actual_source == expected_target && actual_target == expected_source)
  ordered || reversed
}
endpoint_compatibility_error <- function(relationship_id, actual_source, actual_target, expected_source, expected_target, lineage_kind, source_endpoint_field, target_endpoint_field, explicitly_undirected=FALSE) {
  if (endpoint_compatible(actual_source, actual_target, expected_source, expected_target, explicitly_undirected)) return(character())
  allowance <- if (isTRUE(explicitly_undirected)) "; the explicit undirected declaration did not match either orientation" else "; reversed orientation is allowed only by an explicit undirected source declaration"
  paste0(relationship_id, ": ", lineage_kind, " endpoint mismatch: Phase 16A source_system_id=", actual_source, ", target_system_id=", actual_target, "; frozen ", source_endpoint_field, "=", expected_source, ", ", target_endpoint_field, "=", expected_target, allowance)
}
lineage_evidence <- function(lineage, direct, interfaces, dependencies, states, dep_states, governance) {
  if (!grepl("#", lineage, fixed=TRUE)) return(NA_character_)
  key <- sub(".*#", "", lineage)
  if (grepl("^AR-", key)) { i <- match(key, direct$atlas_relationship_id); return(ifelse(is.na(i), NA_character_, direct$evidence_class[[i]])) }
  if (grepl("^TSI-", key)) { i <- match(key, interfaces$interface_id); return(ifelse(is.na(i), NA_character_, interfaces$evidence_class[[i]])) }
  if (grepl("^TDEP-", key)) { i <- match(key, dependencies$dependency_id); return(ifelse(is.na(i), NA_character_, dependencies$evidence_class[[i]])) }
  if (grepl("^TSS-", key)) return(ifelse(key %in% states$state_id, "SCENARIO_STATE", NA_character_))
  if (grepl("^TDS-", key)) return(ifelse(key %in% dep_states$dependency_state_id, "SCENARIO_STATE", NA_character_))
  if (grepl("^TGS-", key)) return(ifelse(key %in% governance$governance_state_id, "SCENARIO_STATE", NA_character_))
  NA_character_
}
technology_lineage_errors <- function(row, nodes, interfaces, dependencies, states, dep_states, governance) {
  errors <- character()
  family <- row[["technology_family_or_regime"]]
  technology_id <- row[["phase15_technology_or_regime_id"]]
  lineage <- row[["source_lineage"]]
  if (grepl("^REGIME-", technology_id)) {
    if (family != technology_id) errors <- c(errors, paste(row[["technology_modifier_id"]], "regime family/id mismatch"))
    prefix <- substr(technology_id, 8L, 8L)
    refs <- extract_refs(lineage, "(?:TSS|TDS|TGS)-[A-Z0-9-]+")
    if (!any(grepl(paste0("-", prefix), refs, fixed=TRUE))) errors <- c(errors, paste(row[["technology_modifier_id"]], "regime lineage does not match scenario"))
    return(errors)
  }
  ni <- match(technology_id, nodes$technology_id)
  if (is.na(ni)) return(c(errors, paste(row[["technology_modifier_id"]], "missing Phase 15A technology node")))
  if (family != nodes$technology_family[[ni]]) errors <- c(errors, paste(row[["technology_modifier_id"]], "declared family differs from Phase 15A node family"))
  refs <- extract_refs(lineage, "(?:TSI|TDEP|TECH)-[A-Z0-9-]+")
  matched <- FALSE
  for (ref in refs) {
    if (grepl("^TSI-", ref)) { i <- match(ref, interfaces$interface_id); if (is.na(i) || interfaces$technology_id[[i]] != technology_id) errors <- c(errors, paste(row[["technology_modifier_id"]], "Phase 15A interface lineage mismatch")) else matched <- TRUE }
    if (grepl("^TDEP-", ref)) { i <- match(ref, dependencies$dependency_id); if (is.na(i) || dependencies$technology_id[[i]] != technology_id) errors <- c(errors, paste(row[["technology_modifier_id"]], "Phase 15A dependency lineage mismatch")) else matched <- TRUE }
    if (grepl("^TECH-", ref)) { if (ref != technology_id) errors <- c(errors, paste(row[["technology_modifier_id"]], "Phase 15A technology ID lineage mismatch")) else matched <- TRUE }
  }
  if (!matched) errors <- c(errors, paste(row[["technology_modifier_id"]], "no matching Phase 15A identity lineage"))
  refs_b <- extract_refs(lineage, "(?:TSS|TDS|TGS)-[A-Z0-9-]+")
  if (!length(refs_b)) errors <- c(errors, paste(row[["technology_modifier_id"]], "no Phase 15B lineage"))
  for (ref in refs_b) {
    if (grepl("^TSS-", ref)) { i <- match(ref, states$state_id); fams <- ifelse(is.na(i), "", states$technology_family[[i]]) }
    else if (grepl("^TDS-", ref)) { i <- match(ref, dep_states$dependency_state_id); fams <- ifelse(is.na(i), "", dep_states$technology_family[[i]]) }
    else { i <- match(ref, governance$governance_state_id); fams <- ifelse(is.na(i), "", governance$technology_family[[i]]) }
    if (is.na(i)) errors <- c(errors, paste(row[["technology_modifier_id"]], "missing Phase 15B lineage", ref))
    else if (!(family %in% strsplit(fams, ";", fixed=TRUE)[[1]])) errors <- c(errors, paste(row[["technology_modifier_id"]], "Phase 15B family mismatch", ref))
  }
  errors
}

phase14a <- check_freeze(file.path(reports, "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json"), "14A", 24L)
phase14b <- check_freeze(file.path(reports, "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json"), "14B", 23L)
phase15a <- check_freeze(file.path(reports, "phase15a_technology_strategic_systems_baseline_freeze_manifest.json"), "15A", 30L)
phase15b <- check_freeze(file.path(reports, "phase15b_technology_convergence_futures_freeze_manifest.json"), "15B", 28L)
freeze_files <- list.files(reports, pattern="freeze_manifest\\.json$", full.names=FALSE)
prior_total <- 0L; prior_paths <- character()
for (mf in sort(freeze_files)) {
  x <- manifest_entries(file.path(reports, mf)); stop_if(nrow(x) > 0L, paste("empty manifest", mf))
  for (i in seq_len(nrow(x))) { stop_if(portable_match(x$rel[[i]], x$sha256[[i]]), paste("prior hash", mf, x$rel[[i]])); prior_total <- prior_total + 1L; prior_paths <- c(prior_paths, x$rel[[i]]) }
}
stop_if(prior_total == 593L && length(unique(prior_paths)) == 584L, "prior freeze inventory")
changed <- system2("git", c("-C", root, "diff", "--name-only", base_sha), stdout=TRUE, stderr=TRUE)
protected <- unique(c(prior_paths, phase14a$rel, phase14b$rel, phase15a$rel, phase15b$rel))
stop_if(length(intersect(changed, protected)) == 0L, "protected artifact changed")
stop_if(grepl('"phase14_overall_status"[[:space:]]*:[[:space:]]*"COMPLETE / ACCEPTED / FROZEN"', json_text(file.path(reports, "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json")), perl=TRUE), "Phase 14 overall")
stop_if(grepl('"phase15_overall_status"[[:space:]]*:[[:space:]]*"COMPLETE / ACCEPTED / FROZEN"', json_text(file.path(reports, "phase15b_technology_convergence_futures_freeze_manifest.json")), perl=TRUE), "Phase 15 overall")
phase16b_changes <- changed[grepl("phase16b", tolower(changed), fixed=TRUE)]
stop_if(all(phase16b_changes %in% c("docs/phase_briefs/phase16b_compound_cross_system_stress_tests.md", "data/processed/integration/phase16b_candidate_stress_tests.csv")), "Phase 16B execution")
stop_if(!any(grepl("phase17", tolower(changed), fixed=TRUE)), "Phase 17 present")

system_lines <- readLines(file.path(metadata, "atlas_systems.yml"), warn=FALSE, encoding="UTF-8")
system_ids <- unique(sub(".*system_id:[[:space:]]*([^[:space:]]+).*", "\\1", system_lines[grepl("^[[:space:]]*- system_id:", system_lines)]))
stop_if(length(system_ids) == 13L, "Phase 14 ontology count")
architecture_lines <- system_lines[grepl("^[[:space:]]{4}- \\[SYS-", system_lines, perl=TRUE)]
stop_if(length(architecture_lines) > 0L, "Phase 14 architecture interfaces")
architecture_rows <- do.call(rbind, lapply(architecture_lines, function(line) {
  inside <- sub("^[[:space:]]{4}- \\[", "", line, perl=TRUE)
  inside <- sub("\\].*$", "", inside, perl=TRUE)
  fields <- trimws(strsplit(inside, ",", fixed=TRUE)[[1]])
  stop_if(length(fields) == 4L, paste("Phase 14 architecture interface schema", line))
  data.frame(source=fields[[1]], target=fields[[2]], interface_type=fields[[3]], status=fields[[4]], stringsAsFactors=FALSE)
}))
architecture_lineages <- paste0(architecture_lineage_prefix, architecture_rows$source, ">", architecture_rows$target)
relationship_lines <- readLines(file.path(metadata, "atlas_relationship_vocabulary.yml"), warn=FALSE, encoding="UTF-8")
relationship_classes <- unique(sub(".*class_id:[[:space:]]*([^[:space:].].*)$", "\\1", relationship_lines[grepl("^[[:space:]]*  - class_id:", relationship_lines)]))
evidence_classes <- c("OBSERVED_DOCUMENTED", "DERIVED_CALCULATED", "INFERRED", "CONTEXT_REUSED", "SCENARIO_ASSUMPTION", "SCENARIO_STATE", "UNRESOLVED", "NONCANONICAL_HOLD")

paths <- c(
  stressor_catalog.csv=file.path(integration, "stressor_catalog.csv"),
  propagation_relationships.csv=file.path(integration, "propagation_relationships.csv"),
  propagation_rules.csv=file.path(integration, "propagation_rules.csv"),
  adaptation_response_catalog.csv=file.path(integration, "adaptation_response_catalog.csv"),
  technology_modifier_catalog.csv=file.path(integration, "technology_modifier_catalog.csv"),
  feedback_coupling_inventory.csv=file.path(integration, "feedback_coupling_inventory.csv"),
  system_stressor_matrix.csv=file.path(integration, "system_stressor_matrix.csv"),
  phase16b_candidate_stress_tests.csv=file.path(integration, "phase16b_candidate_stress_tests.csv")
)
frames <- lapply(paths, read_table)
stressors <- frames[["stressor_catalog.csv"]]
relationships <- frames[["propagation_relationships.csv"]]
rules <- frames[["propagation_rules.csv"]]
responses <- frames[["adaptation_response_catalog.csv"]]
technology <- frames[["technology_modifier_catalog.csv"]]
feedback <- frames[["feedback_coupling_inventory.csv"]]
matrix <- frames[["system_stressor_matrix.csv"]]
candidates <- frames[["phase16b_candidate_stress_tests.csv"]]

schemas <- list(
  stressor_catalog.csv=c("stressor_id","stressor_class","label","initial_system_id","initial_effect","evidence_class","source_lineage","baseline_or_scenario","notes"),
  propagation_relationships.csv=c("relationship_id","source_system_id","target_system_id","relationship_class","propagation_mechanism","evidence_class","direct_or_inferred","baseline_or_scenario","relationship_basis","source_artifact","source_relationship_id","source_id","source_lineage","limitation","spatial_character","temporal_character","reversibility","uncertainty","suitable_for_stress_test_propagation","notes"),
  propagation_rules.csv=c("rule_id","stage","stressor_id","chain_parent_rule_id","chain_relation_type","source_system_id","source_state_or_effect","initial_or_prior_effect","relationship_id","relationship_class","target_system_id","propagation_mechanism","evidence_class","lineage_evidence_class","application_fit","direct_or_inferred","baseline_or_scenario","enabling_condition","limiting_condition","temporal_character","spatial_character","reversibility","technology_modifier","governance_modifier","response_option","second_order_effect","uncertainty","source_lineage","notes"),
  adaptation_response_catalog.csv=c("response_id","response_mechanism","applies_to","enabling_condition","limiting_condition","evidence_class","source_lineage","adaptation_capacity_boundary","notes"),
  technology_modifier_catalog.csv=c("technology_modifier_id","technology_family_or_regime","phase15_technology_or_regime_id","modifier_effect","evidence_class","optional_condition","effects_allowed","source_lineage","notes"),
  feedback_coupling_inventory.csv=c("feedback_id","coupling_pair","feedback_class","evidence_basis","plausible_interaction","boundary","numeric_gain_or_stability_claim","notes"),
  system_stressor_matrix.csv=c("stressor_id","system_id","pathway_cell","basis","is_severity_measure","is_risk_or_vulnerability_score","notes"),
  phase16b_candidate_stress_tests.csv=c("candidate_id","label","stressor_ids","system_ids","selection_basis","phase16a_rule_inputs","status","boundary","executed")
)
for (nm in names(schemas)) stop_if(setequal(names(frames[[nm]]), schemas[[nm]]), paste("schema", nm))

stressor_ids <- unique(stressors$stressor_id)
relationship_ids <- unique(relationships$relationship_id)
response_ids <- unique(responses$response_id)
stop_if(length(stressor_ids) == nrow(stressors), "stressor IDs")
stop_if(all(stressors$initial_system_id %in% system_ids) && all(stressors$evidence_class %in% evidence_classes), "stressor references")
stop_if(length(relationship_ids) == nrow(relationships), "relationship IDs")
stop_if(all(relationships$source_system_id %in% system_ids) && all(relationships$target_system_id %in% system_ids), "relationship systems")
stop_if(all(relationships$relationship_class %in% relationship_classes) && all(relationships$evidence_class %in% evidence_classes), "relationship vocabulary")
stop_if(all(nzchar(relationships$source_lineage)) && all(nzchar(relationships$source_artifact)), "relationship lineage")
stop_if(all(rules$stressor_id %in% stressor_ids) && all(rules$relationship_id %in% relationship_ids) && all(rules$response_option %in% response_ids), "rule references")
stop_if(all(rules$source_system_id %in% system_ids) && all(rules$target_system_id %in% system_ids), "rule systems")
stop_if(all(as.integer(rules$stage) %in% c(1L,2L)) && all(rules$baseline_or_scenario %in% c("baseline","scenario-conditioned")), "rule stages/status")
stop_if(all(nzchar(rules$source_lineage)) && all(nzchar(rules$enabling_condition)) && all(nzchar(rules$limiting_condition)) && all(nzchar(rules$uncertainty)), "rule conditions")

# Crosswalk and Phase 15 maps are read-only source lineage for inheritance checks.
direct <- read_table(file.path(integration, "atlas_dependency_crosswalk.csv"))
interfaces <- read_table(file.path(integration, "technology_system_interfaces.csv"))
dependencies <- read_table(file.path(integration, "technology_dependencies.csv"))
states <- read_table(file.path(scenarios, "technology_system_states.csv"))
dep_states <- read_table(file.path(scenarios, "technology_dependency_states.csv"))
governance <- read_table(file.path(scenarios, "technology_governance_states.csv"))
nodes <- read_table(file.path(root, "data", "processed", "analysis", "technology_system_nodes.csv"))

lineage_errors <- character()
for (i in seq_len(nrow(relationships))) {
  row <- relationships[i,]
  lineage <- row$source_lineage
  if (grepl("#AR-", lineage, fixed=TRUE)) {
    key <- sub(".*#", "", lineage); j <- match(key, direct$atlas_relationship_id)
    if (is.na(j) || direct$source_system_id[[j]] != row$source_system_id || direct$target_system_id[[j]] != row$target_system_id || direct$normalized_relationship_class[[j]] != row$relationship_class) lineage_errors <- c(lineage_errors, row$relationship_id)
  } else if (grepl("#TDS-", lineage, fixed=TRUE)) {
    key <- sub(".*#", "", lineage); j <- match(key, dep_states$dependency_state_id)
    if (is.na(j)) lineage_errors <- c(lineage_errors, paste(row$relationship_id, "missing Phase 15B TDS lineage", key))
    else {
      if (row$baseline_or_scenario != "scenario-conditioned" || row$evidence_class != "SCENARIO_STATE") lineage_errors <- c(lineage_errors, paste(row$relationship_id, "Phase 15B scenario status/evidence mismatch"))
      endpoint_error <- endpoint_compatibility_error(row$relationship_id, row$source_system_id, row$target_system_id, dep_states$system_a[[j]], dep_states$system_b[[j]], "Phase 15B scenario dependency", "system_a", "system_b", FALSE)
      if (length(endpoint_error)) lineage_errors <- c(lineage_errors, endpoint_error)
    }
  } else if (startsWith(lineage, architecture_lineage_prefix)) {
    j <- match(lineage, architecture_lineages)
    if (is.na(j)) lineage_errors <- c(lineage_errors, paste(row$relationship_id, "missing Phase 14 architecture lineage", lineage))
    else {
      explicitly_undirected <- tolower(architecture_rows$interface_type[[j]]) %in% c("undirected", "bidirectional") || tolower(architecture_rows$status[[j]]) %in% c("undirected", "bidirectional")
      endpoint_error <- endpoint_compatibility_error(row$relationship_id, row$source_system_id, row$target_system_id, architecture_rows$source[[j]], architecture_rows$target[[j]], "Phase 14 conceptual architecture", "interfaces[0]", "interfaces[1]", explicitly_undirected)
      if (length(endpoint_error)) lineage_errors <- c(lineage_errors, endpoint_error)
    }
  } else lineage_errors <- c(lineage_errors, row$relationship_id)
}
stop_if(!length(lineage_errors), "relationship lineage resolution")
relationship_status_errors <- character()
for (i in seq_len(nrow(relationships))) {
  expected <- c(OBSERVED_DOCUMENTED="direct", INFERRED="inferred", CONTEXT_REUSED="inferred", SCENARIO_STATE="scenario-conditioned")[[relationships$evidence_class[[i]]]]
  if (!is.null(expected) && !is.na(expected) && relationships$direct_or_inferred[[i]] != expected) relationship_status_errors <- c(relationship_status_errors, relationships$relationship_id[[i]])
}
stop_if(!length(relationship_status_errors), "relationship evidence/status alignment")
stop_if(!any(relationships$relationship_class == "co-location") && !any(relationships$relationship_basis == "co-location"), "co-location is not propagation")
stop_if(all(relationships$suitable_for_stress_test_propagation == "QUALITATIVE_ONLY"), "relationship use")

removed_rules <- c("RULE-16A-003", "RULE-16A-004", "RULE-16A-013", "RULE-16A-032", "RULE-16A-035", "RULE-16A-038")
stop_if(!any(rules$rule_id %in% removed_rules), "unsupported removed rules are present")
stressor_by_id <- setNames(seq_len(nrow(stressors)), stressors$stressor_id)
relationship_by_id <- setNames(seq_len(nrow(relationships)), relationships$relationship_id)
rule_by_id <- setNames(seq_len(nrow(rules)), rules$rule_id)
rule_lineage_errors <- character(); rule_chain_errors <- character()
for (i in seq_len(nrow(rules))) {
  row <- rules[i,]; si <- stressor_by_id[[row$stressor_id]]; ri <- relationship_by_id[[row$relationship_id]]
  rel <- relationships[ri,]; stress <- stressors[si,]
  if (any(c(row$source_system_id != rel$source_system_id, row$target_system_id != rel$target_system_id, row$relationship_class != rel$relationship_class, row$propagation_mechanism != rel$propagation_mechanism, row$source_lineage != rel$source_lineage))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "orientation/lineage"))
  if (row$lineage_evidence_class != rel$evidence_class) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "lineage evidence"))
  if (!compatible_output(rel$evidence_class, row$evidence_class)) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "stronger than lineage"))
  expected <- c(OBSERVED_DOCUMENTED="direct", INFERRED="inferred", CONTEXT_REUSED="inferred", SCENARIO_STATE="scenario-conditioned")[[row$evidence_class]]
  if (!is.null(expected) && !is.na(expected) && row$direct_or_inferred != expected) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "direct/inferred"))
  if (row$evidence_class == "OBSERVED_DOCUMENTED" && (rel$evidence_class != "OBSERVED_DOCUMENTED" || row$application_fit != "EXACT_SOURCE_APPLICATION")) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "observed non-exact"))
  if (row$evidence_class == "INFERRED" && rel$evidence_class == "OBSERVED_DOCUMENTED" && (!grepl("^QUALIFIED_INFERENCE", row$application_fit) || !grepl("inferred", paste(row$enabling_condition, row$limiting_condition), fixed=FALSE))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "inference limitation"))
  if (row$baseline_or_scenario == "scenario-conditioned" && (rel$evidence_class != "SCENARIO_STATE" || !(row$evidence_class %in% c("SCENARIO_STATE", "SCENARIO_ASSUMPTION")))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "scenario mismatch"))
  if (row$baseline_or_scenario == "baseline" && (rel$evidence_class == "SCENARIO_STATE" || row$evidence_class %in% c("SCENARIO_STATE", "SCENARIO_ASSUMPTION"))) rule_lineage_errors <- c(rule_lineage_errors, paste(row$rule_id, "scenario baseline"))
  stage <- as.integer(row$stage)
  if (stage == 1L) {
    has_parent <- !is.na(row$chain_parent_rule_id) && nzchar(row$chain_parent_rule_id)
    if (row$source_system_id != stress$initial_system_id || has_parent || row$chain_relation_type != "parallel_initial_branch") rule_chain_errors <- c(rule_chain_errors, paste(row$rule_id, "initial branch"))
  } else {
    has_parent <- !is.na(row$chain_parent_rule_id) && nzchar(row$chain_parent_rule_id)
    pi <- ifelse(has_parent, rule_by_id[[row$chain_parent_rule_id]], NA_integer_)
    invalid <- is.na(pi) || pi >= i || rules$stressor_id[[pi]] != row$stressor_id || as.integer(rules$stage[[pi]]) != stage - 1L || rules$target_system_id[[pi]] != row$source_system_id || row$chain_relation_type != "sequential"
    if (invalid) rule_chain_errors <- c(rule_chain_errors, paste(row$rule_id, "preceding parent"))
  }
}
stop_if(!length(rule_lineage_errors), "rule source/target/evidence fit")
stop_if(!length(rule_chain_errors), "rule-chain continuity")
stop_if(!any(c(relationships$relationship_class, rules$relationship_class) == "causation") && !any(c(relationships$propagation_mechanism, rules$propagation_mechanism) == "causation"), "causation class")

stop_if(length(response_ids) == nrow(responses) && all(responses$evidence_class %in% evidence_classes), "response vocabulary")
stop_if(all(vapply(responses$adaptation_capacity_boundary, function(x) any(vapply(c("not", "option", "without guaranteeing", "indeterminate"), function(term) grepl(term, tolower(x), fixed=TRUE), logical(1))), logical(1))), "response capacity boundaries")
response_lineage_errors <- character()
for (i in seq_len(nrow(responses))) {
  source_evidence <- lineage_evidence(responses$source_lineage[[i]], direct, interfaces, dependencies, states, dep_states, governance)
  if (is.na(source_evidence) || !compatible_output(source_evidence, responses$evidence_class[[i]])) response_lineage_errors <- c(response_lineage_errors, paste(responses$response_id[[i]], "response evidence"))
  if (responses$evidence_class[[i]] == "OBSERVED_DOCUMENTED" && source_evidence != "OBSERVED_DOCUMENTED") response_lineage_errors <- c(response_lineage_errors, paste(responses$response_id[[i]], "observed response"))
}
stop_if(!length(response_lineage_errors), "response evidence inheritance")

stop_if(length(unique(technology$technology_modifier_id)) == nrow(technology), "technology modifier IDs")
stop_if(all(technology$phase15_technology_or_regime_id %in% c(nodes$technology_id, "REGIME-A", "REGIME-B", "REGIME-C")), "technology modifier IDs")
stop_if(all(technology$evidence_class %in% evidence_classes), "technology modifier evidence")
modifier_errors <- unlist(lapply(seq_len(nrow(technology)), function(i) technology_lineage_errors(technology[i,], nodes, interfaces, dependencies, states, dep_states, governance)))
stop_if(!length(modifier_errors), "technology modifier lineage identity")
stop_if(all(grepl("not automatically protective", tolower(technology$notes), fixed=TRUE)), "technology boundary")

stop_if(length(unique(feedback$feedback_id)) == nrow(feedback), "feedback IDs")
stop_if(all(feedback$feedback_class %in% c("documented","inferred","scenario-conditioned","not currently supported")) && all(feedback$numeric_gain_or_stability_claim == "false"), "feedback boundaries")

stop_if(nrow(matrix) == nrow(stressors) * length(system_ids) && !anyDuplicated(paste(matrix$stressor_id, matrix$system_id)), "matrix shape")
stop_if(all(matrix$stressor_id %in% stressor_ids) && all(matrix$system_id %in% system_ids) && all(matrix$pathway_cell %in% c("DIRECT","INDIRECT","SCENARIO-CONDITIONED","NO CURRENT DEFENSIBLE PATH","NOT ASSESSED")), "matrix vocabulary")
stop_if(all(matrix$is_severity_measure == "false") && all(matrix$is_risk_or_vulnerability_score == "false"), "matrix score boundary")
matrix_precedence_errors <- character()
for (i in seq_len(nrow(stressors))) for (system_id in system_ids) {
  mi <- match(paste(stressors$stressor_id[[i]], system_id), paste(matrix$stressor_id, matrix$system_id))
  cell <- matrix$pathway_cell[[mi]]
  if (stressors$baseline_or_scenario[[i]] != "BASELINE" && system_id == stressors$initial_system_id[[i]] && cell != "SCENARIO-CONDITIONED") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id, "scenario initial"))
  if (stressors$baseline_or_scenario[[i]] != "BASELINE" && cell == "DIRECT") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id, "scenario direct"))
  if (stressors$baseline_or_scenario[[i]] == "BASELINE" && system_id == stressors$initial_system_id[[i]] && cell != "DIRECT") matrix_precedence_errors <- c(matrix_precedence_errors, paste(stressors$stressor_id[[i]], system_id, "baseline initial"))
}
stop_if(!length(matrix_precedence_errors), "matrix scenario precedence")

stop_if(nrow(candidates) == 6L && all(candidates$status == "APPROVED SCOPE / NOT IMPLEMENTED") && all(candidates$executed == "false"), "candidate boundary")
field_names <- unlist(lapply(frames, names), use.names=FALSE)
forbidden_fields <- c("risk_score","resilience_score","vulnerability_score","connectivity_score","severity_score","probability_estimate","incidence_rate","outbreak_probability","health_outcome_forecast")
stop_if(!any(field_names %in% forbidden_fields), "forbidden numeric fields")
all_text <- tolower(paste(unlist(frames), collapse=" "))
stop_if(grepl("not risk", all_text, fixed=TRUE) && grepl("not automatically protective", all_text, fixed=TRUE), "boundary language")
stop_if(grepl("no pathogen engineering", all_text, fixed=TRUE) && grepl("no operational attack", all_text, fixed=TRUE), "biosecurity boundary")

svg <- file.path(figures, "western_basin_stress_propagation_architecture.svg")
png <- file.path(figures, "western_basin_stress_propagation_architecture.png")
stop_if(file.exists(svg) && file.info(svg)$size > 10000 && file.exists(png) && file.info(png)$size > 10000, "figure files")
svg_text <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
for (term in tolower(c("Western Basin Stress Propagation Architecture","STRESSOR","SYSTEM EFFECT","DEPENDENCY / INTERFACE","PROPAGATION","RESPONSE / ADAPTATION","SECOND-ORDER EFFECT","direct / documented","inferred","scenario-conditioned","option ≠ capacity ≠ success"))) stop_if(grepl(term, svg_text, fixed=TRUE), paste("figure label", term))

manifest <- json_text(file.path(reports, "phase16a_manifest.json"))
stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"16A"', manifest, perl=TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', manifest, perl=TRUE), "working manifest identity")
future <- manifest_entries(file.path(reports, "phase16a_manifest.json"))
for (i in seq_len(nrow(future))) stop_if(portable_match(future$rel[[i]], future$sha256[[i]]), paste("working manifest hash", future$rel[[i]]))
stop_if(grepl('"phase16b_status"[[:space:]]*:[[:space:]]*"APPROVED SCOPE / NOT IMPLEMENTED"', manifest, perl=TRUE) && grepl('"no_phase16b_execution"[[:space:]]*:[[:space:]]*true', manifest, perl=TRUE), "Phase 16B manifest")
stop_if(grepl('"phase17_status"[[:space:]]*:[[:space:]]*"NOT IMPLEMENTED"', manifest, perl=TRUE), "Phase 17 manifest")
if (require_review) {
  review_path <- file.path(reports, "phase16a_independent_review.md")
  stop_if(file.exists(review_path), "review record")
  review <- tolower(json_text(review_path))
  for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"propagation_errors": []','"causal_boundary_errors": []','"feedback_errors": []','"evidence_classification_errors": []','"technology_modifier_errors": []','"biosecurity_boundary_errors": []','"canon_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
}

result <- paste0('{\n  "phase": "16A",\n  "passed": true,\n  "counts": {\n    "stressors": ', nrow(stressors), ',\n    "relationships": ', nrow(relationships), ',\n    "rules": ', nrow(rules), ',\n    "responses": ', nrow(responses), ',\n    "technology_modifiers": ', nrow(technology), ',\n    "feedback": ', nrow(feedback), ',\n    "matrix_cells": ', nrow(matrix), ',\n    "candidates": ', nrow(candidates), ',\n    "phase14a_protected_artifacts": ', nrow(phase14a), ',\n    "phase14b_protected_artifacts": ', nrow(phase14b), ',\n    "phase15a_protected_artifacts": ', nrow(phase15a), ',\n    "phase15b_protected_artifacts": ', nrow(phase15b), ',\n    "prior_freeze_entries": ', prior_total, ',\n    "prior_freeze_unique_paths": ', length(unique(prior_paths)), '\n  }\n}\n')
writeLines(sub("\n$", "", result), file.path(reports, "phase16a_r_validation_result.json"), useBytes=TRUE)
cat(sprintf("Phase 16A R validation passed: %d stressors, %d relationships, %d rules, %d responses, %d technology modifiers, %d feedback rows, %d matrix cells, %d Phase 16B candidates; Phase 14 24/23, Phase 15 30/28, and prior 593/584 integrity verified\n", nrow(stressors), nrow(relationships), nrow(rules), nrow(responses), nrow(technology), nrow(feedback), nrow(matrix), nrow(candidates)))
