#!/usr/bin/env Rscript
# Independent base-R validation for Phase 13B infectious-disease dependencies.
args <- commandArgs(trailingOnly=TRUE)
require_review <- "--require-review" %in% args
root <- normalizePath(if (length(args) && args[[1]] != "--require-review") args[[1]] else ".", mustWork=TRUE)
N <- file.path(root, "data", "processed", "networks")
A <- file.path(root, "data", "processed", "analysis")
M <- file.path(root, "outputs", "maps", "systems")
R <- file.path(root, "reports")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call.=FALSE)
read_csv <- function(path) { stop_if(file.exists(path), paste("missing", path)); read.csv(path, stringsAsFactors=FALSE, check.names=FALSE, na.strings=c("", "NA")) }
text_col <- function(x) ifelse(is.na(x), "", as.character(x))
frame_text <- function(x) tolower(paste(vapply(x, function(col) paste(text_col(col), collapse=" "), character(1)), collapse=" "))
raw_bytes <- function(path) readBin(path, "raw", n=as.numeric(file.info(path)$size))
canonical_bytes <- function(raw) charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl=TRUE))
sha256_file <- function(path) {
  cmd <- Sys.which("sha256sum")
  if (nzchar(cmd)) {
    out <- system2(cmd, path, stdout=TRUE, stderr=TRUE)
    stop_if(length(out) >= 1L, paste("sha256sum failed", path))
    token <- strsplit(trimws(out[[1]]), "[[:space:]]+")[[1]][1]
    hit <- regmatches(token, regexpr("[0-9a-f]{64}", token, perl=TRUE))
    stop_if(length(hit) == 1L && nchar(hit) == 64L, paste("sha256sum failed", path))
    return(tolower(hit))
  }
  certutil <- Sys.which("certutil")
  stop_if(nzchar(certutil), "Neither sha256sum nor certutil is available")
  out <- system2(certutil, c("-hashfile", path, "SHA256"), stdout=TRUE, stderr=TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", out)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) >= 1L, paste("certutil failed", path)); hits[[1]]
}
sha256_raw <- function(raw, suffix=".bin") { tmp <- tempfile(fileext=suffix); on.exit(unlink(tmp), add=TRUE); writeBin(raw, tmp); sha256_file(tmp) }
text_ext <- c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "R")
portable_match <- function(path, expected) {
  if (tolower(sha256_file(path)) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% text_ext)) return(FALSE)
  raw <- raw_bytes(path)
  canonical <- canonical_bytes(raw)
  crlf <- charToRaw(gsub("\n", "\r\n", rawToChar(canonical), fixed=TRUE))
  lf_tmp <- tempfile(fileext=paste0(".", ext)); crlf_tmp <- tempfile(fileext=paste0(".", ext))
  on.exit(unlink(c(lf_tmp, crlf_tmp)), add=TRUE)
  writeBin(canonical, lf_tmp); writeBin(crlf, crlf_tmp)
  tolower(expected) %in% c(sha256_file(lf_tmp), sha256_file(crlf_tmp))
}

artifact_entries <- function(payload_text) {
  lines <- readLines(payload_text, warn=FALSE, encoding="UTF-8")
  has_artifacts <- any(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl=TRUE))
  collection <- if (has_artifacts) "artifacts" else "files"
  start <- which(grepl(paste0('"', collection, '"[[:space:]]*:[[:space:]]*\\{'), lines, perl=TRUE))[1]
  stop_if(!is.na(start), paste("missing manifest collection", payload_text))
  rel <- character(); hashes <- character(); bytes <- numeric()
  current <- NA_character_; current_hash <- NA_character_; current_bytes <- NA_real_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash); bytes <<- c(bytes, current_bytes) }
    current <<- NA_character_; current_hash <<- NA_character_; current_bytes <<- NA_real_
  }
  if (start + 1L <= length(lines)) for (line in lines[(start+1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    inline <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{[^}]*"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"[^}]*', line, perl=TRUE))[[1]]
    if (length(inline) == 3L) {
      bb <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE))[[1]]
      rel <- c(rel, inline[[2]]); hashes <- c(hashes, inline[[3]]); bytes <- c(bytes, if (length(bb)==2L) as.numeric(bb[[2]]) else NA_real_); next
    }
    direct <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE))[[1]]
    if (length(direct) == 3L) { append_current(); rel <- c(rel, direct[[2]]); hashes <- c(hashes, direct[[3]]); bytes <- c(bytes, NA_real_); next }
    nested <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl=TRUE))[[1]]
    if (length(nested) == 2L) { append_current(); current <- nested[[2]] }
    hh <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl=TRUE))[[1]]
    if (length(hh) == 2L && !is.na(current)) current_hash <- hh[[2]]
    bb <- regmatches(line, regexec('"bytes"[[:space:]]*:[[:space:]]*([0-9]+)', line, perl=TRUE))[[1]]
    if (length(bb) == 2L && !is.na(current)) current_bytes <- as.numeric(bb[[2]])
  }
  append_current(); data.frame(rel=rel, sha256=hashes, bytes=bytes, stringsAsFactors=FALSE)
}
verify_manifest <- function(path, expected_n=NA_integer_) {
  x <- artifact_entries(path); if (!is.na(expected_n)) stop_if(nrow(x) == expected_n, paste("artifact count", basename(path)))
  for (i in seq_len(nrow(x))) stop_if(portable_match(file.path(root, x$rel[[i]]), x$sha256[[i]]), paste("manifest hash", x$rel[[i]]))
  x
}

phase13a_path <- file.path(R, "phase13a_infectious_disease_freeze_manifest.json")
phase13a_text <- paste(readLines(phase13a_path, warn=FALSE, encoding="UTF-8"), collapse=" ")
for (term in c('"accepted_phase": "13A"', '"status": "ACCEPTED / FROZEN"', '"baseline": "Infectious Disease System Baseline, 2026"', '"phase13b_implemented": false', '"phase13c_implemented": false')) stop_if(grepl(term, phase13a_text, fixed=TRUE), paste("Phase 13A", term))
phase13a_x <- verify_manifest(phase13a_path, 25L)


prior_paths <- list.files(R, pattern="^phase.*_freeze_manifest[.]json$", full.names=TRUE)
prior_paths <- prior_paths[basename(prior_paths) != "phase13a_infectious_disease_freeze_manifest.json"]
prior_hashes <- character(); prior_total <- 0L
for (path in sort(prior_paths)) {
  x <- artifact_entries(path)
  for (i in seq_len(nrow(x))) {
    rel <- x$rel[[i]]; expected <- x$sha256[[i]]
    if (rel %in% names(prior_hashes)) stop_if(unname(prior_hashes[[rel]]) == expected, paste("conflicting prior hash", rel))
    prior_hashes[rel] <- expected; stop_if(portable_match(file.path(root, rel), expected), paste("prior artifact", rel)); prior_total <- prior_total + 1L
  }
}
stop_if(prior_total == 358L && length(unique(names(prior_hashes))) == 351L, paste("prior inventory", prior_total, length(unique(names(prior_hashes)))))

context_paths <- c(
  "reports/phase9a_climate_natural_hazards_freeze_manifest.json",
  "reports/phase9b_climate_hazard_dependencies_resilience_freeze_manifest.json",
  "reports/phase7a_exposure_environmental_health_freeze_manifest.json",
  "reports/phase10a_governance_jurisdiction_freeze_manifest.json",
  "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json",
  "reports/phase11a_population_settlement_freeze_manifest.json",
  "reports/phase11b_population_mobility_dependencies_freeze_manifest.json",
  "reports/phase12a_vector_ecology_freeze_manifest.json",
  "reports/phase12b_vector_environment_human_dependencies_freeze_manifest.json",
  "reports/phase12c_vector_ecology_futures_freeze_manifest.json",
  "reports/phase5a_freight_freeze_manifest.json",
  "reports/phase5b_freight_evidence_freeze_manifest.json",
  "reports/phase5c_freight_dependency_freeze_manifest.json",
  "reports/phase3b_freeze_manifest.json"
)
for (rel in context_paths) { txt <- paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "); stop_if(grepl('"status": "ACCEPTED / FROZEN"', txt, fixed=TRUE), paste("context status", rel)); verify_manifest(file.path(root, rel)) }
water_text <- paste(readLines(file.path(R, "water_system_manifest.json"), warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl('"system": "water"', water_text, fixed=TRUE) && grepl('"nodes": 14', water_text, fixed=TRUE) && grepl('"edges": 15', water_text, fixed=TRUE), "water context")
obs_text <- paste(readLines(file.path(R, "observation_system_manifest.json"), warn=FALSE, encoding="UTF-8"), collapse=" ")
stop_if(grepl('"phase": "4A"', obs_text, fixed=TRUE) && grepl('"nodes": 25', obs_text, fixed=TRUE) && grepl('"edges": 21', obs_text, fixed=TRUE), "observation context")

D <- read_csv(file.path(A, "infectious_disease_dependency_register.csv"))
E <- read_csv(file.path(N, "infectious_disease_dependency_edges.csv"))
X <- read_csv(file.path(A, "infectious_disease_dependency_matrix.csv"))
C <- read_csv(file.path(A, "infectious_disease_evidence_crosswalk.csv"))
S <- read_csv(file.path(A, "infectious_disease_dependency_sources.csv"))
U <- read_csv(file.path(A, "infectious_disease_dependency_uncertainties.csv"))
base_nodes <- read_csv(file.path(N, "infectious_disease_nodes.csv"))
base_sources <- read_csv(file.path(A, "infectious_disease_sources.csv"))
expected_D <- c("dependency_id","from_id","to_id","relationship_type","dependency_type","archetype","documented_or_inferred","relationship_basis","direction","spatial_scale","temporal_scope","evidence_strength","source_id","uncertainty_id","uncertainty","confidence","reality_status","canon_status","relevant_disease_systems","notes")
expected_E <- c("edge_id", expected_D)
expected_X <- c("matrix_id","archetype","climate_sensitivity","hydrologic_sensitivity","vector_dependence","food_freight_dependence","population_contact_dependence","mobility_dependence","healthcare_dependence","surveillance_dependence","governance_dependence","spatial_scale","temporal_scope","source_ids","notes")
expected_C <- c("evidence_id","dependency_id","claim_type","claim_status","source_id","evidence_basis","spatial_scale","temporal_scope","supported_statement","not_supported_statement")
expected_S <- c("source_id","title","url","source_type","publication_or_period","retrieval_date","geographic_scale","method_or_product","evidence_use","use_limitations","retrieval_url","retrieval_provenance")
expected_U <- c("uncertainty_id","subject","category","statement","resolution_status","source_id","confidence","notes")
stop_if(setequal(names(D), expected_D) && setequal(names(E), expected_E) && setequal(names(X), expected_X) && setequal(names(C), expected_C) && setequal(names(S), expected_S) && setequal(names(U), expected_U), "schema")
stop_if(nrow(D)==36L && nrow(E)==36L && nrow(X)==6L && nrow(C)==36L && nrow(S)==33L && nrow(U)==14L, "counts")
stop_if(!anyDuplicated(D$dependency_id) && !anyDuplicated(E$edge_id) && !anyDuplicated(C$evidence_id) && !anyDuplicated(S$source_id) && !anyDuplicated(U$uncertainty_id), "unique IDs")
stop_if(setequal(E$dependency_id, D$dependency_id) && all(E$dependency_id == D$dependency_id), "edge/register IDs")
for (col in expected_D) stop_if(all(nchar(text_col(D[[col]])) > 0L), paste("empty dependency", col))
for (col in c("edge_id", "dependency_id", "source_id", "uncertainty_id")) stop_if(all(nchar(text_col(E[[col]])) > 0L), paste("empty edge", col))
source_ids <- unique(text_col(S$source_id)); node_ids <- unique(c(text_col(base_nodes$node_id), "EXT-CLIMATE","EXT-VECTOR-ECOLOGY","EXT-HYDROLOGY","EXT-ECOLOGY","EXT-FLOODING","EXT-WATER-INFRASTRUCTURE","EXT-FOOD-PRODUCTION","EXT-FOOD-PROCESSING","EXT-FREIGHT","EXT-SETTLEMENT","EXT-CONTACT-STRUCTURE","EXT-MOBILITY","EXT-ANIMAL-HOSTS","EXT-OCCUPATIONAL-CONTACT","EXT-HEALTHCARE","EXT-INFRASTRUCTURE"))
stop_if(all(text_col(D$from_id) %in% node_ids) && all(text_col(D$to_id) %in% node_ids), "node references")
stop_if(all(text_col(D$source_id) %in% source_ids) && all(text_col(E$source_id) %in% source_ids) && all(text_col(C$source_id) %in% source_ids) && all(text_col(U$source_id) %in% source_ids), "source references")
stop_if(all(text_col(D$uncertainty_id) %in% text_col(U$uncertainty_id)), "uncertainty references")
stop_if(all(text_col(D$documented_or_inferred) %in% c("documented","inferred")), "documented/inferred")
stop_if(all(text_col(D$archetype) %in% c("vector-borne","waterborne/environmental","foodborne/enteric","respiratory","zoonotic","healthcare/AMR")), "archetypes")
stop_if(all(text_col(D$relationship_type) %in% c("frames_seasonality","creates_habitat_opportunity","mediates_host_habitat","frames_transmission_opportunity","frames_contact_opportunity","feeds_observation","conditions_exposure_opportunity","disrupts_or_connects_pathway","depends_on_system_condition","frames_exposure_opportunity","supplies_case_observation","supports_response_coordination","connects_food_system","connects_distribution","creates_propagation_opportunity","is_observed_by","complements_detection","supports_investigation_response","structures_contact_opportunity","connects_contact_opportunity","frames_care_detection_interface","care_detection_interface","supplies_surveillance_data","mediates_host_interface","frames_animal_human_opportunity","supplies_animal_observations","frames_resistance_detection_interface","supports_service_continuity","supports_infection_control_coordination")), "relationship types")
stop_if(all(text_col(D$dependency_type) %in% c("environmental driver","ecological mediator","infrastructure dependency","surveillance dependency","institutional response dependency","population/contact interface","mobility interface","food/freight interface","healthcare interface")), "dependency types")
stop_if(all(text_col(D$relationship_basis) %in% c("documented_source","accepted_layer","accepted_layer_plus_project_inference","project_inference","documented_source_plus_project_inference","boundary_rule")), "relationship basis")
stop_if(all(text_col(D$evidence_strength) %in% c("strong","moderate","limited","unknown")) && all(text_col(D$confidence) %in% c("high","moderate","limited","unknown")), "qualitative fields")
stop_if(all(text_col(D$reality_status)=="real") && all(text_col(D$canon_status) %in% c("verified","inferred")), "status fields")
stop_if(all(text_col(C$claim_status) %in% c("documented","inferred")) && setequal(C$dependency_id, D$dependency_id), "crosswalk status")
qual_cols <- c("climate_sensitivity","hydrologic_sensitivity","vector_dependence","food_freight_dependence","population_contact_dependence","mobility_dependence","healthcare_dependence","surveillance_dependence","governance_dependence")
stop_if(all(as.matrix(X[,qual_cols]) %in% c("strong","moderate","limited","unknown","not_applicable")), "matrix labels")

all_text <- tolower(paste(frame_text(D), frame_text(E), frame_text(X), frame_text(C), frame_text(U), collapse=" "))
for (term in c("driver is not deterministic cause","vector ecology != human disease","contamination != illness","mobility != transmission","surveillance != incidence","healthcare presence != facility-level disease burden","food/freight connectivity is an interface","not a disease observation","not a risk","not incidence","not outbreak","does not establish")) stop_if(grepl(term, all_text, fixed=TRUE), paste("boundary", term))
forbidden <- c("risk_score","disease_risk_score","composite_disease_risk_index","vulnerability_score","ej_score","individual_risk","infection_probability","outbreak_probability","transmission_rate","disease_burden_index","dose","incidence_rate")
stop_if(length(intersect(forbidden, unique(c(names(D),names(E),names(X),names(C),names(U))))) == 0L, "forbidden fields")
# The following must-not-match checks reject numerical scores/rates/probabilities or unsupported causal assertions.
bad_metric <- grepl("(?:risk score|risk index|incidence|outbreak probability|infection probability|disease burden)[[:space:]]*[,=:][[:space:]]*[0-9]", all_text, perl=TRUE)
stop_if(!bad_metric, "unsupported positive metric")
bad_causal <- grepl("(?:temperature|climate|mobility|population density|surveillance|contamination|vector ecology|healthcare presence)[[:space:]]*(?:causes|determines|proves|equals)[[:space:]]*(?:infection|disease|incidence|outbreak|burden)", all_text, perl=TRUE)
stop_if(!bad_causal, "unsupported causal claim")

for (rel in c("PROJECT_STATUS.md","docs/canon_status.md","reports/current_phase_handoff.md")) {
  txt <- tolower(paste(readLines(file.path(root, rel), warn=FALSE, encoding="UTF-8"), collapse=" "))
  stop_if(grepl("phase 13b", txt, fixed=TRUE) && grepl("implemented", txt, fixed=TRUE), paste("status", rel))
  stop_if(grepl("great black swamp", txt, fixed=TRUE) && grepl("hold", txt, fixed=TRUE) && grepl("noncanonical", txt, fixed=TRUE), paste("hold", rel))
  stop_if(grepl("intake-coordinate discrepancy", txt, fixed=TRUE) && grepl("unresolved", txt, fixed=TRUE), paste("intake hold", rel))
}
status_text <- tolower(paste(readLines(file.path(root, "PROJECT_STATUS.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
canon_text <- tolower(paste(readLines(file.path(root, "docs/canon_status.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
handoff_text <- tolower(paste(readLines(file.path(root, "reports/current_phase_handoff.md"), warn=FALSE, encoding="UTF-8"), collapse=" "))
for (txt in c(status_text, canon_text, handoff_text)) { stop_if(grepl("phase 13c", txt, fixed=TRUE) && grepl("not implemented", txt, fixed=TRUE), "13C status"); stop_if(grepl("active phase", txt, fixed=TRUE) && grepl("none", txt, fixed=TRUE), "active phase") }

png <- file.path(M, "42_infectious_disease_transmission_dependencies_2026.png")
svg <- file.path(M, "42_infectious_disease_transmission_dependencies_2026.svg")
stop_if(file.exists(png) && file.info(png)$size > 10000, "Map 42 PNG")
stop_if(identical(paste(sprintf("%02x", as.integer(readBin(png, "raw", n=8))), collapse=""), "89504e470d0a1a0a"), "Map 42 PNG signature")
xmllint <- Sys.which("xmllint"); stop_if(nzchar(xmllint), "xmllint")
xml_status <- system2(xmllint, c("--noout", svg), stdout=FALSE, stderr=FALSE); stop_if(is.null(xml_status) || xml_status==0, "Map 42 SVG parse")
svg_text <- tolower(paste(readLines(svg, warn=FALSE, encoding="UTF-8"), collapse=" "))
for (term in c("map 42","infectious disease","transmission dependencies","environment","vectors","water","food / freight","population / mobility","healthcare","surveillance","governance","driver","incidence","outbreak","no cases")) stop_if(grepl(term, svg_text, fixed=TRUE), paste("Map 42 text", term))

manifest_path <- file.path(R, "infectious_disease_dependency_manifest.json")
manifest_text <- paste(readLines(manifest_path, warn=FALSE, encoding="UTF-8"), collapse=" ")
for (term in c('"phase": "13B"','"map_number": 42','"status": "implemented_validated_pending_sol_acceptance"','"phase13a_accepted_frozen": true','"phase1_12_immutable": true','"phase13c_implemented": false','"composite_disease_risk_index": false','"individual_case_or_risk_map": false')) stop_if(grepl(term, manifest_text, fixed=TRUE), paste("manifest", term))
manifest_x <- artifact_entries(manifest_path); stop_if(nrow(manifest_x) >= 15L, "Phase 13B manifest artifacts")
for (i in seq_len(nrow(manifest_x))) stop_if(portable_match(file.path(root, manifest_x$rel[[i]]), manifest_x$sha256[[i]]), paste("Phase 13B manifest", manifest_x$rel[[i]]))
if (require_review) {
  review_path <- file.path(R, "infectious_disease_dependency_independent_review.md")
  stop_if(file.exists(review_path), "required review")
  review <- tolower(paste(readLines(review_path, warn=FALSE, encoding="UTF-8"), collapse=" "))
  for (term in c('"passed": true','"security_concerns": []','"logic_errors": []','"provenance_errors": []','"epidemiological_errors": []','"dependency_errors": []','"surveillance_errors": []','"spatial_scale_errors": []','"health_boundary_errors": []')) stop_if(grepl(term, review, fixed=TRUE), paste("review", term))
}
stop_if(file.exists(file.path(R, "phase13b_citation_ledger.json")), "citation ledger")
cat(sprintf("Phase 13B R validation passed: %d dependencies/%d edges, %d matrix rows, %d crosswalk rows, %d sources, %d uncertainties; Map 42 parsed; Phase 13A %d artifacts and prior freeze inventory %d/%d independently checked; boundaries, holds, and 13C/14 exclusions verified\n", nrow(D), nrow(E), nrow(X), nrow(C), nrow(S), nrow(U), nrow(phase13a_x), prior_total, length(unique(names(prior_hashes)))))
