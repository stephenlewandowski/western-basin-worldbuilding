#!/usr/bin/env Rscript
# Independent base-R validator for the Phase 16B compound stress-test package.
# It deliberately does not source the Python builder or validator.

args <- commandArgs(trailingOnly = TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash = "/", mustWork = TRUE)
require_review <- "--require-review" %in% args
integration <- file.path(root, "data", "processed", "integration")
scenarios <- file.path(root, "data", "processed", "scenarios")
reports <- file.path(root, "reports")
figures <- file.path(root, "outputs", "figures")
system_registry_source <- "metadata/atlas_systems.yml"
base_sha <- "9308127065112d0c01c294e954ae87f44e39af3f"
regime_axis_fields <- c("observability_effect","coupling_effect","dependency_effect","redundancy_effect","coordination_effect","substitution_effect","governance_friction_effect","digital_dependence_effect")

phase16a_freeze <- file.path(reports, "phase16a_integrated_basin_dynamics_freeze_manifest.json")
phase14a_freeze <- file.path(reports, "phase14a_common_systems_ontology_identity_evidence_crosswalk_freeze_manifest.json")
phase14b_freeze <- file.path(reports, "phase14b_atlas_layer_registry_cross_system_dependency_normalization_freeze_manifest.json")
phase15a_freeze <- file.path(reports, "phase15a_technology_strategic_systems_baseline_freeze_manifest.json")
phase15b_freeze <- file.path(reports, "phase15b_technology_convergence_futures_freeze_manifest.json")
manifest_file <- file.path(reports, "phase16b_manifest.json")
check_file <- file.path(reports, "phase16b_r_validation_result.json")
review_file <- file.path(reports, "phase16b_independent_review.md")

stop_if <- function(condition, message) if (!isTRUE(condition)) stop(message, call. = FALSE)
read_table <- function(path) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing table", path))
  read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, na.strings = character())
}
read_rel <- function(relative) read_table(file.path(root, gsub("/", .Platform$file.sep, relative, fixed = TRUE)))
text_file <- function(path) paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = " ")

load_authoritative_system_ids <- function() {
  path <- file.path(root, gsub("/", .Platform$file.sep, system_registry_source, fixed = TRUE))
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("authoritative system registry cannot be loaded", system_registry_source))
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  start <- match("systems:", lines)
  end <- match("identity_sources:", lines)
  stop_if(!is.na(start) && !is.na(end) && end > start, paste("authoritative system registry structure", system_registry_source))
  block <- lines[(start + 1L):(end - 1L)]
  record_starts <- which(grepl("^  - ", block))
  stop_if(length(record_starts) > 0L, paste("authoritative system registry empty", system_registry_source))
  record_ids <- vapply(seq_along(record_starts), function(index) {
    from <- record_starts[[index]]
    to <- if (index < length(record_starts)) record_starts[[index + 1L]] - 1L else length(block)
    record_lines <- block[from:to]
    id_lines <- record_lines[grepl("^  - system_id:", record_lines)]
    stop_if(length(id_lines) == 1L, paste("authoritative system registry system_id field", system_registry_source))
    raw_value <- sub("^  - system_id:[[:space:]]*", "", id_lines[[1]])
    raw_value <- trimws(raw_value)
    stop_if(nzchar(raw_value), paste("authoritative system registry blank system ID", system_registry_source))

    if (substr(raw_value, 1L, 1L) %in% c("\"", "'")) {
      quote <- substr(raw_value, 1L, 1L)
      stop_if(nchar(raw_value) >= 2L && substr(raw_value, nchar(raw_value), nchar(raw_value)) == quote, paste("authoritative system registry quoted system ID", system_registry_source))
      system_id <- substr(raw_value, 2L, nchar(raw_value) - 1L)
    } else {
      scalar <- tolower(raw_value)
      non_string <- scalar %in% c("null", "~", "true", "false", "yes", "no", "on", "off") ||
        grepl("^-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?$", raw_value, perl = TRUE) ||
        (startsWith(raw_value, "[") && endsWith(raw_value, "]")) ||
        (startsWith(raw_value, "{") && endsWith(raw_value, "}"))
      stop_if(!non_string, paste("authoritative system registry system ID must be a YAML string", system_registry_source))
      system_id <- sub("[[:space:]]+#.*$", "", raw_value)
    }
    stop_if(nzchar(system_id), paste("authoritative system registry blank system ID", system_registry_source))
    stop_if(identical(system_id, trimws(system_id)), paste("authoritative system registry system ID whitespace", system_registry_source))
    system_id
  }, character(1))
  stop_if(anyDuplicated(record_ids) == 0L, paste("authoritative system registry duplicate IDs", system_registry_source))
  system_ids <- unique(record_ids)
  stop_if(length(system_ids) > 0L, paste("authoritative system registry empty", system_registry_source))
  unique(system_ids)
}

system_id_tokens <- function(value) {
  value <- as.character(value)
  hits <- regmatches(value, gregexpr("SYS-[A-Z0-9]+(?:-[A-Z0-9]+)*", value, perl = TRUE))[[1]]
  if (!length(hits) || (length(hits) == 1L && hits[[1]] == "")) character() else hits
}

is_system_identifier_field <- function(field) {
  field %in% c("system_id", "system_ids", "initial_system_id", "source_system_id", "target_system_id", "source_system", "target_system", "stressor_initial_system_id", "stressor_initial_system_ids", "last_target_system_id") || grepl("(_system_id|_system_ids)$", field)
}

system_membership_errors <- function(frame, record_field, system_ids) {
  errors <- character()
  optional_fields <- c("last_target_system_id")
  for (i in seq_len(nrow(frame))) {
    record_id <- as.character(frame[[record_field]][[i]])
    for (field in names(frame)) {
      raw <- as.character(frame[[field]][[i]])
      if (is.na(raw)) raw <- ""
      if (is_system_identifier_field(field)) {
        values <- if (grepl("_system_ids$", field) || field == "system_ids") strsplit(raw, ";", fixed = TRUE)[[1]] else raw
        if (!nzchar(raw) && field %in% optional_fields) values <- character()
        for (value in values) {
          value <- trimws(value)
          if (nzchar(value) || !(field %in% optional_fields)) {
            if (!nzchar(value) || !(value %in% system_ids)) errors <- c(errors, paste0("record_id=", record_id, "; field=", field, "; invalid_system_id=", ifelse(nzchar(value), value, "<blank>"), "; authoritative_registry=", system_registry_source))
          }
        }
      }
      tokens <- system_id_tokens(raw)
      invalid <- setdiff(tokens, system_ids)
      if (length(invalid)) errors <- c(errors, vapply(invalid, function(value) paste0("record_id=", record_id, "; field=", field, "; invalid_system_id=", value, "; authoritative_registry=", system_registry_source), character(1)))
    }
  }
  unique(errors)
}

raw_bytes <- function(path) readBin(path, "raw", n = as.numeric(file.info(path)$size))
sha256_raw <- function(raw, suffix = ".bin") {
  tmp <- tempfile(fileext = suffix); on.exit(unlink(tmp), add = TRUE); writeBin(raw, tmp)
  command <- Sys.which("sha256sum")
  if (nzchar(command)) {
    output <- system2(command, tmp, stdout = TRUE, stderr = TRUE)
    text <- paste(output, collapse = " ")
    hits <- regmatches(text, gregexpr("[0-9a-fA-F]{64}", text, perl = TRUE))[[1]]
    stop_if(length(hits) > 0L, "sha256sum failed")
    return(tolower(hits[[1]]))
  }
  command <- Sys.which("certutil")
  stop_if(nzchar(command), "no SHA-256 command available")
  output <- system2(command, c("-hashfile", normalizePath(tmp, winslash = "\\", mustWork = TRUE), "SHA256"), stdout = TRUE, stderr = TRUE)
  hits <- tolower(gsub("[[:space:]]+", "", output)); hits <- hits[grepl("^[0-9a-f]{64}$", hits)]
  stop_if(length(hits) > 0L, "certutil failed")
  hits[[1]]
}
sha256_file <- function(path) sha256_raw(raw_bytes(path), tools::file_ext(path))
portable_match <- function(path, expected) {
  stop_if(file.exists(path) && file.info(path)$size > 0, paste("missing artifact", path))
  raw <- raw_bytes(path)
  if (tolower(sha256_raw(raw, tools::file_ext(path))) == tolower(expected)) return(TRUE)
  ext <- tolower(tools::file_ext(path))
  if (!(ext %in% c("csv", "json", "md", "txt", "yml", "yaml", "svg", "py", "r", "toml"))) return(FALSE)
  normalized <- charToRaw(gsub("\r\n?", "\n", rawToChar(raw), perl = TRUE))
  tolower(sha256_raw(normalized, ext)) == tolower(expected)
}

manifest_entries <- function(path) {
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  hits <- which(grepl('"artifacts"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  if (!length(hits)) hits <- which(grepl('"files"[[:space:]]*:[[:space:]]*\\{', lines, perl = TRUE))
  stop_if(length(hits) > 0L, paste("manifest artifacts collection", path))
  start <- hits[[1]]; rel <- character(); hashes <- character(); current <- NA_character_; current_hash <- NA_character_
  append_current <- function() {
    if (!is.na(current) && !is.na(current_hash)) { rel <<- c(rel, current); hashes <<- c(hashes, current_hash) }
    current <<- NA_character_; current_hash <<- NA_character_
  }
  if (start < length(lines)) for (line in lines[(start + 1L):length(lines)]) {
    if (grepl("^  \\},?[[:space:]]*$", line)) { append_current(); break }
    direct <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(direct) == 3L) { append_current(); rel <- c(rel, direct[[2]]); hashes <- c(hashes, direct[[3]]); next }
    nested <- regmatches(line, regexec('^[[:space:]]*"([^"]+/[^"]+)"[[:space:]]*:[[:space:]]*\\{', line, perl = TRUE))[[1]]
    if (length(nested) == 2L) { append_current(); current <- nested[[2]] }
    hash <- regmatches(line, regexec('"sha256"[[:space:]]*:[[:space:]]*"([0-9a-f]{64})"', line, perl = TRUE))[[1]]
    if (length(hash) == 2L && !is.na(current)) current_hash <- hash[[2]]
  }
  append_current()
  data.frame(relative = rel, sha256 = hashes, stringsAsFactors = FALSE)
}
check_freeze <- function(path, phase, expected_n) {
  txt <- text_file(path)
  stop_if(grepl(paste0('"accepted_phase"[[:space:]]*:[[:space:]]*"', phase, '"'), txt, perl = TRUE), paste("freeze phase", path))
  stop_if(grepl('"status"[[:space:]]*:[[:space:]]*"ACCEPTED / FROZEN"', txt, perl = TRUE), paste("freeze status", path))
  entries <- manifest_entries(path)
  stop_if(nrow(entries) == expected_n, paste("freeze artifact count", path))
  for (i in seq_len(nrow(entries))) stop_if(portable_match(file.path(root, entries$relative[[i]]), entries$sha256[[i]]), paste("freeze hash", entries$relative[[i]]))
  entries
}

split_ids <- function(value) if (!nzchar(value)) character() else strsplit(value, ";", fixed = TRUE)[[1]]
unique_in_order <- function(value) value[!duplicated(value) & nzchar(value)]
extract_refs <- function(value) {
  matches <- gregexpr("(?:TSS|TDS|TGS)-[A-Z0-9-]+", value, perl = TRUE)
  if (matches[[1]][1] == -1L) character() else unique_in_order(regmatches(value, matches)[[1]])
}
contains_all <- function(value, terms) all(vapply(terms, function(term) grepl(term, value, fixed = TRUE), logical(1)))

review_required_fields <- c("passed","security_concerns","logic_errors","provenance_errors","chain_errors","propagation_errors","evidence_classification_errors","scenario_boundary_errors","technology_modifier_errors","biosecurity_boundary_errors","atlas_bridge_errors","canon_boundary_errors","suggestions","summary")
review_blocking_fields <- setdiff(review_required_fields, c("passed","suggestions","summary"))
review_typed_value <- function(value, type) { attr(value, "review_json_type") <- type; value }
review_skip_ws <- function(text, pos) {
  n <- nchar(text)
  while (pos <= n && substr(text, pos, pos) %in% c(" ", "\t", "\r", "\n")) pos <- pos + 1L
  pos
}
review_parse_string <- function(text, pos) {
  n <- nchar(text); stop_if(pos <= n && substr(text, pos, pos) == "\"", "review JSON string")
  pos <- pos + 1L; chars <- character()
  while (pos <= n) {
    ch <- substr(text, pos, pos)
    if (ch == "\"") return(list(type = "string", value = review_typed_value(paste0(chars, collapse = ""), "string"), pos = pos + 1L))
    if (ch == "\\") {
      stop_if(pos + 1L <= n, "review JSON escape")
      esc <- substr(text, pos + 1L, pos + 1L)
      if (esc == "u") { stop_if(pos + 5L <= n, "review JSON unicode escape"); chars <- c(chars, "?"); pos <- pos + 6L }
      else { chars <- c(chars, esc); pos <- pos + 2L }
    } else { chars <- c(chars, ch); pos <- pos + 1L }
  }
  stop("unterminated review JSON string", call. = FALSE)
}
review_parse_value <- function(text, pos) {
  pos <- review_skip_ws(text, pos); ch <- substr(text, pos, pos)
  if (ch == "\"") return(review_parse_string(text, pos))
  if (ch == "[") return(review_parse_array(text, pos))
  if (ch == "{") return(review_parse_object(text, pos))
  if (substr(text, pos, pos + 3L) == "true") return(list(type = "boolean", value = review_typed_value(TRUE, "boolean"), pos = pos + 4L))
  if (substr(text, pos, pos + 4L) == "false") return(list(type = "boolean", value = review_typed_value(FALSE, "boolean"), pos = pos + 5L))
  if (substr(text, pos, pos + 3L) == "null") return(list(type = "null", value = review_typed_value(NA_character_, "null"), pos = pos + 4L))
  numeric_match <- regmatches(substr(text, pos, nchar(text)), regexec("^-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", substr(text, pos, nchar(text)), perl = TRUE))[[1]]
  if (length(numeric_match) == 1L && nzchar(numeric_match[[1]])) return(list(type = "number", value = review_typed_value(as.numeric(numeric_match[[1]]), "number"), pos = pos + nchar(numeric_match[[1]])))
  stop("unsupported review JSON value", call. = FALSE)
}
review_parse_array <- function(text, pos) {
  n <- nchar(text); stop_if(pos <= n && substr(text, pos, pos) == "[", "review JSON array")
  pos <- review_skip_ws(text, pos + 1L); values <- character()
  if (pos <= n && substr(text, pos, pos) == "]") return(list(type = "array", value = review_typed_value(values, "array"), pos = pos + 1L))
  repeat {
    parsed <- review_parse_value(text, pos)
    stop_if(identical(parsed$type, "string") && is.character(parsed$value) && length(parsed$value) == 1L, "review arrays must contain strings")
    values <- c(values, parsed$value); pos <- review_skip_ws(text, parsed$pos)
    if (pos <= n && substr(text, pos, pos) == "]") return(list(type = "array", value = review_typed_value(values, "array"), pos = pos + 1L))
    stop_if(pos <= n && substr(text, pos, pos) == ",", "review JSON array delimiter")
    pos <- review_skip_ws(text, pos + 1L)
  }
}
review_parse_object <- function(text, pos) {
  n <- nchar(text); stop_if(pos <= n && substr(text, pos, pos) == "{", "review JSON object")
  pos <- review_skip_ws(text, pos + 1L); values <- list(); keys <- character()
  if (pos <= n && substr(text, pos, pos) == "}") return(list(type = "object", value = values, pos = pos + 1L))
  repeat {
    key <- review_parse_string(text, pos); pos <- review_skip_ws(text, key$pos)
    stop_if(pos <= n && substr(text, pos, pos) == ":", "review JSON key delimiter")
    pos <- review_skip_ws(text, pos + 1L); stop_if(!(key$value %in% keys), "duplicate review JSON key")
    parsed <- review_parse_value(text, pos); values[[key$value]] <- parsed$value; keys <- c(keys, key$value)
    pos <- review_skip_ws(text, parsed$pos)
    if (pos <= n && substr(text, pos, pos) == "}") return(list(type = "object", value = values, pos = pos + 1L))
    stop_if(pos <= n && substr(text, pos, pos) == ",", "review JSON object delimiter")
    pos <- review_skip_ws(text, pos + 1L)
  }
}
review_json_payload <- function(path) {
  text <- paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  match <- regmatches(text, regexec("(?s)```json[[:space:]]*(\\{.*?\\})[[:space:]]*```", text, perl = TRUE))[[1]]
  stop_if(length(match) == 2L, "review JSON block absent")
  parsed <- review_parse_object(match[[2]], 1L); stop_if(identical(parsed$type, "object") && review_skip_ws(match[[2]], parsed$pos) == nchar(match[[2]]) + 1L, "review JSON trailing content")
  parsed$value
}
review_is_string_array <- function(value) {
  is_array <- identical(attr(value, "review_json_type"), "array")
  is_character <- is.character(value)
  elements_are_strings <- if (!is_character) FALSE else all(vapply(seq_along(value), function(index) is.character(value[[index]]) && length(value[[index]]) == 1L && !is.na(value[[index]]), logical(1)))
  isTRUE(is_array && is_character && elements_are_strings)
}
validate_review_payload <- function(payload) {
  invalid <- function(detail, schema_ok = FALSE, review_passed = NA) list(schema_ok = schema_ok, review_passed = review_passed, ok = FALSE, detail = detail)
  if (!is.list(payload) || length(names(payload)) != length(review_required_fields) || !setequal(names(payload), review_required_fields)) return(invalid("review schema is not the current Phase 16B schema"))
  if (!is.logical(payload$passed) || length(payload$passed) != 1L || is.na(payload$passed) || !identical(attr(payload$passed, "review_json_type"), "boolean")) return(invalid("review passed must be boolean"))
  array_fields <- c(review_blocking_fields, "suggestions")
  for (field in array_fields) if (!review_is_string_array(payload[[field]])) return(invalid(paste("review field", field, "must be an array of strings"), schema_ok = FALSE, review_passed = isTRUE(payload$passed)))
  if (!is.character(payload$summary) || length(payload$summary) != 1L || !identical(attr(payload$summary, "review_json_type"), "string") || !nzchar(trimws(payload$summary))) return(invalid("review summary must be a nonempty string", schema_ok = FALSE, review_passed = isTRUE(payload$passed)))
  blocking <- review_blocking_fields[vapply(review_blocking_fields, function(field) length(payload[[field]]) > 0L, logical(1))]
  if (!isTRUE(payload$passed)) return(invalid("review passed is not true", schema_ok = TRUE, review_passed = FALSE))
  if (length(blocking)) return(invalid(paste("passed:true with non-empty blocking arrays:", paste(blocking, collapse = ", ")), schema_ok = TRUE, review_passed = TRUE))
  list(schema_ok = TRUE, review_passed = TRUE, ok = TRUE, detail = "passed:true; complete schema; all blocking arrays empty")
}
validate_review_record <- function(path) {
  if (!file.exists(path)) return(list(schema_ok = FALSE, review_passed = NA, ok = FALSE, detail = "review record absent"))
  payload <- tryCatch(review_json_payload(path), error = function(error) error)
  if (inherits(payload, "error")) return(list(schema_ok = FALSE, review_passed = NA, ok = FALSE, detail = conditionMessage(payload)))
  validate_review_payload(payload)
}

review_probe_payload <- function(overrides = list(), passed = "true") {
  values <- setNames(rep("[]", length(review_required_fields)), review_required_fields)
  values[["passed"]] <- passed; values[["summary"]] <- "\"valid review\""
  if (length(overrides)) for (field in names(overrides)) values[[field]] <- overrides[[field]]
  paste0("{", paste(vapply(names(values), function(field) paste0("\"", field, "\":", values[[field]]), character(1)), collapse = ","), "}")
}
run_review_schema_probes <- function() {
  cases <- list(
    A_valid_empty_arrays = list(text = review_probe_payload(), schema_ok = TRUE, review_passed = TRUE, gate_ok = TRUE),
    B_valid_failed_single_blocker = list(text = review_probe_payload(list(logic_errors = "[\"blocking\"]"), passed = "false"), schema_ok = TRUE, review_passed = FALSE, gate_ok = FALSE),
    C_valid_multiple_strings = list(text = review_probe_payload(list(suggestions = "[\"one\",\"two\"]")), schema_ok = TRUE, review_passed = TRUE, gate_ok = TRUE),
    D_scalar_instead_of_array = list(text = review_probe_payload(list(logic_errors = "\"scalar\"")), schema_ok = FALSE, review_passed = TRUE, gate_ok = FALSE),
    E_non_string_array_element = list(text = review_probe_payload(list(logic_errors = "[1]")), schema_ok = FALSE, review_passed = TRUE, gate_ok = FALSE)
  )
  results <- lapply(cases, function(case) {
    parsed <- tryCatch(review_parse_object(case$text, 1L), error = function(error) error)
    if (inherits(parsed, "error")) return(list(schema_valid = FALSE, review_passed = case$review_passed, gate_ok = FALSE, detail = conditionMessage(parsed), passed = !case$schema_ok && !case$gate_ok))
    validated <- validate_review_payload(parsed$value)
    list(schema_valid = isTRUE(validated$schema_ok), review_passed = validated$review_passed, gate_ok = isTRUE(validated$ok), detail = validated$detail, passed = identical(isTRUE(validated$schema_ok), case$schema_ok) && identical(validated$review_passed, case$review_passed) && identical(isTRUE(validated$ok), case$gate_ok))
  })
  list(passed = all(vapply(results, function(result) isTRUE(result$passed), logical(1))), results = results)
}
print_review_schema_probes <- function(result) {
  cat("Phase 16B R review-schema probes:\n")
  for (name in names(result$results)) {
    probe <- result$results[[name]]
    review_passed <- if (is.na(probe$review_passed)) "NA" else as.character(probe$review_passed)
    cat(sprintf("- %s: %s (schema_valid=%s; review_passed=%s; gate_ok=%s; %s)\n", name, ifelse(probe$passed, "PASS", "FAIL"), probe$schema_valid, review_passed, probe$gate_ok, probe$detail))
  }
  cat(sprintf("Review-schema probes %s: %d/%d passed\n", ifelse(isTRUE(result$passed), "passed", "failed"), sum(vapply(result$results, function(probe) isTRUE(probe$passed), logical(1))), length(result$results)))
}

run_validation <- function() {
  p16a <- check_freeze(phase16a_freeze, "16A", 30L)
  p14a <- check_freeze(phase14a_freeze, "14A", 24L)
  p14b <- check_freeze(phase14b_freeze, "14B", 23L)
  p15a <- check_freeze(phase15a_freeze, "15A", 30L)
  p15b <- check_freeze(phase15b_freeze, "15B", 28L)
  all_freezes <- list.files(reports, pattern = "freeze_manifest[.]json$", full.names = TRUE)
  prior_total <- 0L; prior_paths <- character()
  for (path in sort(all_freezes)) {
    entries <- manifest_entries(path)
    stop_if(nrow(entries) > 0L, paste("empty freeze", basename(path)))
    prior_total <- prior_total + nrow(entries); prior_paths <- c(prior_paths, entries$relative)
    for (i in seq_len(nrow(entries))) stop_if(portable_match(file.path(root, entries$relative[[i]]), entries$sha256[[i]]), paste("prior freeze hash", entries$relative[[i]]))
  }
  stop_if(prior_total == 623L && length(unique(prior_paths)) == 614L, "prior freeze inventory")
  tracked <- system2("git", c("-C", root, "diff", "--name-only", base_sha), stdout = TRUE, stderr = TRUE)
  untracked <- system2("git", c("-C", root, "ls-files", "--others", "--exclude-standard"), stdout = TRUE, stderr = TRUE)
  changed <- gsub("\\\\", "/", trimws(c(tracked, untracked))); changed <- changed[nzchar(changed)]
  protected <- unique(c(prior_paths, p16a$relative, p14a$relative, p14b$relative, p15a$relative, p15b$relative))
  merge_base <- trimws(paste(system2("git", c("-C", root, "merge-base", "HEAD", base_sha), stdout = TRUE, stderr = TRUE), collapse = ""))
  stop_if(identical(merge_base, base_sha), "starting SHA")
  stop_if(!length(intersect(changed, protected)), "frozen artifact changed")
  stop_if(!length(intersect(changed, p16a$relative)), "Phase 16A artifact changed")
  stop_if(any(grepl("phase 17", tolower(text_file(file.path(root, "PROJECT_STATUS.md"))), fixed = TRUE)), "Phase 17 status absent")
  stop_if(any(grepl("phase 16b", tolower(text_file(file.path(root, "PROJECT_STATUS.md"))), fixed = TRUE)), "Phase 16B status absent")
  stop_if(!any(grepl("phase17", tolower(changed), fixed = TRUE)), "Phase 17 implementation path present")
  stop_if(!any(grepl("release", tolower(changed), fixed = TRUE)), "release/tag path is out of scope")

  system_ids <- load_authoritative_system_ids()
  stop_if(length(system_ids) == 13L, paste("Phase 14 system count", system_registry_source))
  stressors <- read_rel("data/processed/integration/stressor_catalog.csv"); rules <- read_rel("data/processed/integration/propagation_rules.csv")
  relationships <- read_rel("data/processed/integration/propagation_relationships.csv"); responses <- read_rel("data/processed/integration/adaptation_response_catalog.csv")
  modifiers <- read_rel("data/processed/integration/technology_modifier_catalog.csv")
  p15_states <- read_rel("data/processed/scenarios/technology_system_states.csv"); p15_deps <- read_rel("data/processed/scenarios/technology_dependency_states.csv"); p15_gov <- read_rel("data/processed/scenarios/technology_governance_states.csv")
  stressor_map <- setNames(seq_len(nrow(stressors)), stressors$stressor_id); rule_map <- setNames(seq_len(nrow(rules)), rules$rule_id); relation_map <- setNames(seq_len(nrow(relationships)), relationships$relationship_id); response_map <- setNames(seq_len(nrow(responses)), responses$response_id); modifier_map <- setNames(seq_len(nrow(modifiers)), modifiers$technology_modifier_id)
  outputs <- list(
    definitions = read_rel("data/processed/integration/phase16b_stress_test_definitions.csv"),
    stages = read_rel("data/processed/integration/phase16b_chain_stages.csv"),
    terminations = read_rel("data/processed/integration/phase16b_chain_terminations.csv"),
    system_states = read_rel("data/processed/integration/phase16b_system_states.csv"),
    response_states = read_rel("data/processed/integration/phase16b_response_adaptation_states.csv"),
    regimes = read_rel("data/processed/integration/phase16b_regime_effects.csv"),
    uncertainties = read_rel("data/processed/integration/phase16b_uncertainties.csv"),
    comparison = read_rel("data/processed/integration/phase16b_cross_test_comparison.csv"),
    hooks = read_rel("data/processed/integration/phase16b_narrative_hooks.csv")
  )
  expected_columns <- list(
    definitions = c("test_id","candidate_id","test_class","label","stressor_ids","stressor_initial_system_ids","phase16a_rule_inputs","implementation_status","fan_out_semantics","selection_basis","boundary","notes"),
    stages = c("stage_id","test_id","branch_id","stage","stage_status","phase16a_stressor_id","stressor_initial_system_id","phase16a_rule_id","phase16a_chain_parent_rule_id","stage_parent_id","chain_relation_type","source_system_id","target_system_id","phase16a_relationship_id","relationship_class","propagation_mechanism","stressor_evidence_class","evidence_class","lineage_evidence_class","application_fit","direct_or_inferred","baseline_or_scenario","scenario_state_ids","scenario_condition","source_state_or_effect","system_effect","technology_modifier_ids","governance_modifier","phase16a_response_id","response_mechanism","second_order_effect","uncertainty","source_lineage","response_capacity_boundary","notes"),
    terminations = c("termination_id","test_id","branch_id","phase16a_stressor_id","initial_system_id","last_stage_id","last_stage","last_target_system_id","baseline_or_scenario","scenario_condition","termination_status","termination_basis","continuation_check","defensible_branch_termination","notes"),
    system_states = c("state_id","test_id","branch_id","stage_id","stage","position","system_id","state_descriptor","evidence_class","baseline_or_scenario","scenario_state_ids","phase16a_rule_id","source_lineage","notes"),
    response_states = c("response_state_id","test_id","branch_id","stage_id","stage","phase16a_rule_id","phase16a_response_id","response_mechanism","response_evidence_class","adaptation_state","enabling_condition","limiting_condition","capacity_boundary","source_lineage","scenario_condition","notes"),
    regimes = c("regime_effect_id","test_id","regime_id","scenario_id","horizon","scenario_family","phase16a_technology_modifier_id","phase16a_rule_ids","phase15_modifier_lineage_ids","phase15_anchor_state_ids","phase15_state_evidence_class","observability_effect","coupling_effect","dependency_effect","redundancy_effect","coordination_effect","substitution_effect","governance_friction_effect","digital_dependence_effect","phase16a_allowed_effects","relationship_status","uncertainty","source_lineage","notes"),
    uncertainties = c("uncertainty_id","test_id","uncertainty_domain","subject","uncertainty_level","phase16a_rule_ids","what_is_unknown","what_is_not_inferred","scenario_condition","source_lineage","notes"),
    comparison = c("test_id","label","principal_stressor_count","branch_count","stage_count","system_state_observations","response_adaptation_states","termination_count","scenario_conditioned_stage_count","fan_out_summary","cross_system_interfaces","regime_a_finding","regime_b_finding","regime_c_finding","comparison_boundary","source_basis"),
    hooks = c("hook_id","test_id","test_label","system_place_setting","operational_decision_point","human_institutional_role","observable_sign_of_strain","adaptation_response_moment","scientific_lineage","status","canon_boundary","notes")
  )
  for (name in names(outputs)) stop_if(setequal(names(outputs[[name]]), expected_columns[[name]]), paste("schema", name))
  definitions <- outputs$definitions; stages <- outputs$stages; terminations <- outputs$terminations; state_rows <- outputs$system_states; response_rows <- outputs$response_states; regime_rows <- outputs$regimes; uncertainty_rows <- outputs$uncertainties; comparison_rows <- outputs$comparison; hook_rows <- outputs$hooks
  expected_tests <- c("P16B-CAND-001","P16B-CAND-002","P16B-CAND-003","P16B-CAND-004"); reserves <- c("P16B-CAND-005","P16B-CAND-006")
  stop_if(nrow(definitions) == 6L && !anyDuplicated(definitions$test_id) && setequal(definitions$test_id, c(expected_tests, reserves)), "definition IDs")
  stop_if(setequal(definitions$test_id[definitions$test_class == "PRINCIPAL"], expected_tests), "exactly four principal tests")
  stop_if(setequal(definitions$test_id[definitions$test_class == "RESERVE"], reserves) && all(definitions$implementation_status[definitions$test_class == "RESERVE"] == "RESERVE / UNIMPLEMENTED"), "reserve status")
  candidate_rows <- read_rel("data/processed/integration/phase16b_candidate_stress_tests.csv"); candidate_map <- setNames(seq_len(nrow(candidate_rows)), candidate_rows$candidate_id)
  for (i in seq_len(nrow(definitions))) {
    j <- candidate_map[[definitions$candidate_id[[i]]]]; stop_if(!is.null(j), paste("candidate", definitions$test_id[[i]]))
    stop_if(definitions$stressor_ids[[i]] == candidate_rows$stressor_ids[[j]] && definitions$phase16a_rule_inputs[[i]] == candidate_rows$phase16a_rule_inputs[[j]], paste("candidate lineage", definitions$test_id[[i]]))
    stressor_ids <- split_ids(definitions$stressor_ids[[i]]); stop_if(length(stressor_ids) > 0L && all(stressor_ids %in% stressors$stressor_id), paste("definition stressors", definitions$test_id[[i]]))
    initial <- unique_in_order(stressors$initial_system_id[match(stressor_ids, stressors$stressor_id)]); stop_if(identical(split_ids(definitions$stressor_initial_system_ids[[i]]), initial), paste("initial systems", definitions$test_id[[i]]))
    stop_if(startsWith(definitions$fan_out_semantics[[i]], "parallel initial branches"), paste("fan-out", definitions$test_id[[i]]))
  }
  expected_branch_ids <- c("P16B-001-HEAT","P16B-001-LOW-FLOW","P16B-001-GRID","P16B-002-HAB","P16B-002-TREATMENT-ENERGY","P16B-002-TREATMENT-DISEASE","P16B-003-TRANSPORT","P16B-003-CRITICAL-MATERIAL","P16B-003-FUEL","P16B-003-FEEDSTOCK","P16B-004-INFECTIOUS-DATA","P16B-004-INFECTIOUS-GOVERNANCE","P16B-004-SURVEILLANCE","P16B-004-PRIVACY")
  expected_branch_tests <- c(rep("P16B-CAND-001",3),rep("P16B-CAND-002",3),rep("P16B-CAND-003",4),rep("P16B-CAND-004",4))
  expected_branch_stressors <- c("STRESS-HEAT-EXTREME","STRESS-LOW-FLOW-DROUGHT","STRESS-ELECTRIC-GRID","STRESS-HAB-WATER-QUALITY","STRESS-WATER-TREATMENT","STRESS-WATER-TREATMENT","STRESS-TRANSPORT-FREIGHT","STRESS-CRITICAL-MATERIAL","STRESS-FUEL-CONSTRAINT","STRESS-INDUSTRIAL-FEEDSTOCK","STRESS-INFECTIOUS-PRESSURE","STRESS-INFECTIOUS-PRESSURE","STRESS-SURVEILLANCE-STRAIN","STRESS-DATA-PRIVACY")
  expected_branch_rules <- c("RULE-16A-001","RULE-16A-005;RULE-16A-006","RULE-16A-016","RULE-16A-012","RULE-16A-014","RULE-16A-015","RULE-16A-019","","RULE-16A-020","","RULE-16A-022","RULE-16A-023","RULE-16A-026","RULE-16A-033")
  selected_rule_ids <- unique(unlist(strsplit(expected_branch_rules[nzchar(expected_branch_rules)], ";", fixed = TRUE)))
  selected_rule_ids <- selected_rule_ids[nzchar(selected_rule_ids)]
  selected_rules <- rules[rules$rule_id %in% selected_rule_ids, , drop = FALSE]
  selected_relationship_ids <- unique(selected_rules$relationship_id)
  selected_relationships <- relationships[relationships$relationship_id %in% selected_relationship_ids, , drop = FALSE]
  system_errors <- c(
    system_membership_errors(stressors, "stressor_id", system_ids),
    system_membership_errors(candidate_rows, "candidate_id", system_ids),
    system_membership_errors(selected_rules, "rule_id", system_ids),
    system_membership_errors(selected_relationships, "relationship_id", system_ids)
  )
  output_record_fields <- c(definitions = "test_id", stages = "stage_id", terminations = "termination_id", system_states = "state_id", response_states = "response_state_id", regimes = "regime_effect_id", uncertainties = "uncertainty_id", comparison = "test_id", hooks = "hook_id")
  for (name in names(output_record_fields)) system_errors <- c(system_errors, system_membership_errors(outputs[[name]], output_record_fields[[name]], system_ids))
  stop_if(!length(unique(system_errors)), paste("system membership", paste(unique(system_errors), collapse = ", ")))
  stop_if(nrow(stages) == 13L && !anyDuplicated(stages$stage_id), "stage count")
  stage_errors <- character()
  for (i in seq_len(nrow(stages))) {
    rule <- rules[match(stages$phase16a_rule_id[[i]], rules$rule_id),]; stressor <- stressors[match(stages$phase16a_stressor_id[[i]], stressors$stressor_id),]; rel <- relationships[match(stages$phase16a_relationship_id[[i]], relationships$relationship_id),]; response <- responses[match(stages$phase16a_response_id[[i]], responses$response_id),]
    stop_if(nrow(rule) == 1L && nrow(stressor) == 1L && nrow(rel) == 1L && nrow(response) == 1L, paste("stage source", stages$stage_id[[i]]))
    fields <- c("phase16a_stressor_id","stressor_initial_system_id","phase16a_chain_parent_rule_id","chain_relation_type","source_system_id","target_system_id","phase16a_relationship_id","relationship_class","propagation_mechanism","stressor_evidence_class","evidence_class","lineage_evidence_class","application_fit","direct_or_inferred","baseline_or_scenario","source_state_or_effect","system_effect","technology_modifier_ids","governance_modifier","phase16a_response_id","response_mechanism","second_order_effect","uncertainty","source_lineage","response_capacity_boundary")
    expected <- c(rule$stressor_id, stressor$initial_system_id, rule$chain_parent_rule_id, rule$chain_relation_type, rule$source_system_id, rule$target_system_id, rule$relationship_id, rel$relationship_class, rel$propagation_mechanism, stressor$evidence_class, rule$evidence_class, rel$evidence_class, rule$application_fit, rule$direct_or_inferred, rule$baseline_or_scenario, rule$source_state_or_effect, rule$initial_or_prior_effect, rule$technology_modifier, rule$governance_modifier, rule$response_option, response$response_mechanism, rule$second_order_effect, rule$uncertainty, rule$source_lineage, response$adaptation_capacity_boundary)
    for (k in seq_along(fields)) if (stages[[fields[[k]]]][[i]] != expected[[k]]) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], fields[[k]]))
    refs <- extract_refs(rule$source_lineage); if (!identical(split_ids(stages$scenario_state_ids[[i]]), refs)) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "scenario refs"))
    expected_status <- if (rule$baseline_or_scenario == "scenario-conditioned") "SCENARIO-CONDITIONED OPTIONAL STAGE" else "SELECTED QUALITATIVE STAGE"; if (stages$stage_status[[i]] != expected_status) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "status"))
    expected_condition <- if (length(refs)) paste0("Phase 15B state reference(s) ", stages$scenario_state_ids[[i]], "; not a baseline path") else "baseline Phase 16A rule application; no future scenario state is asserted"; if (stages$scenario_condition[[i]] != expected_condition) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "condition"))
    mods <- split_ids(stages$technology_modifier_ids[[i]]); if (length(setdiff(mods, c("NONE", modifiers$technology_modifier_id)))) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "technology modifier"))
    if (rule$baseline_or_scenario == "scenario-conditioned" && (rule$evidence_class != "SCENARIO_STATE" || !length(refs) || !all(refs %in% c(p15_states$state_id,p15_deps$dependency_state_id,p15_gov$governance_state_id)))) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "scenario preservation"))
    if (rule$baseline_or_scenario != "scenario-conditioned" && (length(refs) || rule$evidence_class %in% c("SCENARIO_STATE","SCENARIO_ASSUMPTION"))) stage_errors <- c(stage_errors, paste(stages$stage_id[[i]], "scenario leakage"))
  }
  stop_if(!length(stage_errors), paste("stage lineage", paste(stage_errors, collapse = ", ")))
  for (b in seq_along(expected_branch_ids)) {
    ids <- which(stages$branch_id == expected_branch_ids[[b]]); actual_rules <- if (length(ids)) paste(stages$phase16a_rule_id[ids][order(as.integer(stages$stage[ids]))], collapse = ";") else ""
    stop_if(all(stages$test_id[ids] == expected_branch_tests[[b]]) || !length(ids), paste("branch test", expected_branch_ids[[b]])); stop_if(all(stages$phase16a_stressor_id[ids] == expected_branch_stressors[[b]]) || !length(ids), paste("branch stressor", expected_branch_ids[[b]])); stop_if(actual_rules == expected_branch_rules[[b]], paste("branch rule sequence", expected_branch_ids[[b]]))
    if (length(ids)) {
      ordered <- ids[order(as.integer(stages$stage[ids]))]
      for (q in seq_along(ordered)) {
        row <- stages[ordered[[q]],]
        if (q == 1L) stop_if(row$chain_relation_type == "parallel_initial_branch" && !nzchar(row$stage_parent_id) && row$source_system_id == stressors$initial_system_id[match(row$phase16a_stressor_id, stressors$stressor_id)], paste("initial fan-out", expected_branch_ids[[b]]))
        else { parent <- stages[ordered[[q - 1L]],]; stop_if(row$chain_relation_type == "sequential" && row$stage_parent_id == parent$stage_id && row$phase16a_chain_parent_rule_id == parent$phase16a_rule_id && row$source_system_id == parent$target_system_id && as.integer(row$stage) == as.integer(parent$stage) + 1L, paste("chain continuity", expected_branch_ids[[b]])) }
      }
    }
  }
  stop_if(all(stages$phase16a_rule_id %in% rules$rule_id), "unsupported rule")
  stop_if(all(stages$source_system_id == relationships$source_system_id[match(stages$phase16a_relationship_id, relationships$relationship_id)] & stages$target_system_id == relationships$target_system_id[match(stages$phase16a_relationship_id, relationships$relationship_id)]), "endpoint direction")

  termination_map <- match(paste(expected_branch_tests, expected_branch_ids, sep = "|"), paste(terminations$test_id, terminations$branch_id, sep = "|")); response_stage_ids <- response_rows$stage_id
  stop_if(nrow(terminations) == 14L && !anyDuplicated(paste(terminations$test_id, terminations$branch_id)), "termination count")
  term_errors <- character()
  for (b in seq_along(expected_branch_ids)) {
    i <- termination_map[[b]]; stop_if(!is.na(i), paste("termination missing", expected_branch_ids[[b]])); ids <- which(stages$test_id == expected_branch_tests[[b]] & stages$branch_id == expected_branch_ids[[b]]); ordered <- ids[order(as.integer(stages$stage[ids]))]; last <- if (length(ordered)) stages[ordered[[length(ordered)]],] else NULL
    expected <- c(expected_branch_stressors[[b]], stressors$initial_system_id[match(expected_branch_stressors[[b]], stressors$stressor_id)], if (length(ordered)) last$stage_id else "", if (length(ordered)) last$stage else "0", if (length(ordered)) last$target_system_id else "")
    actual <- c(terminations$phase16a_stressor_id[[i]], terminations$initial_system_id[[i]], terminations$last_stage_id[[i]], terminations$last_stage[[i]], terminations$last_target_system_id[[i]])
    if (!all(actual == expected)) term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "last-stage fields"))
    if (length(ordered)) {
      last_row <- stages[ordered[[length(ordered)]],]
      candidates <- rules[rules$stressor_id == expected_branch_stressors[[b]] & rules$chain_parent_rule_id == last_row$phase16a_rule_id[[1]] & rules$chain_relation_type == "sequential" & rules$source_system_id == last_row$target_system_id[[1]] & as.integer(rules$stage) == as.integer(last_row$stage[[1]]) + 1L,]
      if (nrow(candidates) > 0L) term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "valid unused continuation"))
      if (!(last_row$stage_id[[1]] %in% response_stage_ids)) term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "final response/adaptation state missing"))
    } else {
      candidates <- rules[rules$stressor_id == expected_branch_stressors[[b]],]
      if (nrow(candidates) > 0L) term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "unselected Phase 16A rule"))
    }
    if (terminations$termination_status[[i]] != "TERMINATED — NO DEFENSIBLE CURRENT PATH" || terminations$defensible_branch_termination[[i]] != "true") term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "status"))
    expected_basis <- if (length(ordered)) "NO_LATER_PHASE16A_RULE_FOR_SAME_STRESSOR_AND_TARGET" else "NO_PHASE16A_RULE_FOR_STRESSOR"; if (terminations$termination_basis[[i]] != expected_basis || !grepl("Phase 16A", terminations$continuation_check[[i]], fixed = TRUE) || !grepl("rule", tolower(terminations$continuation_check[[i]]), fixed = TRUE)) term_errors <- c(term_errors, paste(expected_branch_ids[[b]], "basis"))
  }
  stop_if(!length(term_errors), paste("termination", paste(term_errors, collapse = ", ")))

  state_errors <- character(); state_count <- table(state_rows$stage_id)
  for (i in seq_len(nrow(state_rows))) {
    stage <- stages[match(state_rows$stage_id[[i]], stages$stage_id),]; stop_if(nrow(stage) == 1L, paste("state stage", state_rows$state_id[[i]])); system_expected <- if (state_rows$position[[i]] == "source") stage$source_system_id else if (state_rows$position[[i]] == "target") stage$target_system_id else ""; descriptor <- if (state_rows$position[[i]] == "source") stage$source_state_or_effect else if (state_rows$position[[i]] == "target") stage$system_effect else ""; if (state_rows$system_id[[i]] != system_expected || state_rows$state_descriptor[[i]] != descriptor || state_rows$test_id[[i]] != stage$test_id || state_rows$branch_id[[i]] != stage$branch_id || state_rows$stage[[i]] != stage$stage || state_rows$evidence_class[[i]] != stage$evidence_class || state_rows$baseline_or_scenario[[i]] != stage$baseline_or_scenario || state_rows$scenario_state_ids[[i]] != stage$scenario_state_ids || state_rows$phase16a_rule_id[[i]] != stage$phase16a_rule_id || state_rows$source_lineage[[i]] != stage$source_lineage) state_errors <- c(state_errors, state_rows$state_id[[i]])
  }
  stop_if(nrow(state_rows) == 26L && all(as.integer(state_count) == 2L) && !length(state_errors), "system-state resolution")

  response_errors <- character()
  for (i in seq_len(nrow(response_rows))) {
    stage <- stages[match(response_rows$stage_id[[i]], stages$stage_id),]; response <- responses[match(response_rows$phase16a_response_id[[i]], responses$response_id),]; stop_if(nrow(stage) == 1L && nrow(response) == 1L, paste("response source", response_rows$response_state_id[[i]])); expected <- c(stage$test_id, stage$branch_id, stage$stage, response$response_mechanism, response$evidence_class, response$enabling_condition, response$limiting_condition, response$adaptation_capacity_boundary, response$source_lineage, stage$scenario_condition); actual <- c(response_rows$test_id[[i]], response_rows$branch_id[[i]], response_rows$stage[[i]], response_rows$response_mechanism[[i]], response_rows$response_evidence_class[[i]], response_rows$enabling_condition[[i]], response_rows$limiting_condition[[i]], response_rows$capacity_boundary[[i]], response_rows$source_lineage[[i]], response_rows$scenario_condition[[i]]); if (!all(actual == expected) || response_rows$phase16a_rule_id[[i]] != stage$phase16a_rule_id || response_rows$phase16a_response_id[[i]] != stage$phase16a_response_id || !grepl("OPTION IDENTIFIED", response_rows$adaptation_state[[i]], fixed = TRUE) || !grepl("INDETERMINATE", response_rows$adaptation_state[[i]], fixed = TRUE) || !grepl("not guaranteed", tolower(response_rows$notes[[i]]), fixed = TRUE)) response_errors <- c(response_errors, response_rows$response_state_id[[i]])
  }
  stop_if(nrow(response_rows) == 13L && !anyDuplicated(response_rows$stage_id) && setequal(response_rows$stage_id, stages$stage_id) && !length(response_errors), "response/adaptation resolution")
  stop_if(all(stages$evidence_class == rules$evidence_class[match(stages$phase16a_rule_id, rules$rule_id)]) && all(stages$lineage_evidence_class == relationships$evidence_class[match(stages$phase16a_relationship_id, relationships$relationship_id)]), "evidence inheritance")

  regime_errors <- character(); expected_families <- c(A = "Coordinated Technological Adaptation", B = "Uneven Networked Modernization", C = "High Capability / High Friction Basin"); expected_effects <- list(A = c("reduce propagation","improve coordination","increase observability"), B = c("create substitution options","increase coupling","shift workforce requirements"), C = c("increase observability","increase coupling","create governance / trust friction","create cyber / digital exposure"))
  for (i in seq_len(nrow(regime_rows))) {
    regime <- regime_rows$regime_id[[i]]; modifier_id <- c(A = "TM-16A-009", B = "TM-16A-010", C = "TM-16A-011")[[regime]]; modifier <- modifiers[match(modifier_id, modifiers$technology_modifier_id),]; sid <- regime_rows$scenario_id[[i]]; anchor <- c(paste0("TSS-",sid,"-01"), paste0("TDS-",sid,"-01"), paste0("TGS-",sid,"-01")); available <- c(p15_states$state_id,p15_deps$dependency_state_id,p15_gov$governance_state_id); expected_rules <- unique_in_order(stages$phase16a_rule_id[stages$test_id == regime_rows$test_id[[i]]]); checks <- c(regime_rows$test_id[[i]] %in% expected_tests, sid == paste0(regime, regime_rows$horizon[[i]]), regime_rows$scenario_family[[i]] == expected_families[[regime]], regime_rows$phase16a_technology_modifier_id[[i]] == modifier_id, identical(split_ids(regime_rows$phase15_modifier_lineage_ids[[i]]), extract_refs(modifier$source_lineage)), identical(split_ids(regime_rows$phase15_anchor_state_ids[[i]]), anchor), all(anchor %in% available), regime_rows$phase15_state_evidence_class[[i]] == "SCENARIO_STATE", identical(split_ids(regime_rows$phase16a_rule_ids[[i]]), expected_rules), regime_rows$phase16a_allowed_effects[[i]] == modifier$effects_allowed, grepl("NO NEW PROPAGATION PATHWAY", regime_rows$relationship_status[[i]], fixed = TRUE), grepl("not automatically protective", tolower(regime_rows$notes[[i]]), fixed = TRUE), grepl("ranking", tolower(regime_rows$notes[[i]]), fixed = TRUE), grepl(modifier_id, regime_rows$source_lineage[[i]], fixed = TRUE), all(vapply(anchor, function(ref) grepl(ref, regime_rows$source_lineage[[i]], fixed = TRUE), logical(1)))); if (!all(checks) || !all(vapply(expected_effects[[regime]], function(term) grepl(term, regime_rows$phase16a_allowed_effects[[i]], fixed = TRUE), logical(1))) || any(!nzchar(regime_rows[i, regime_axis_fields]))) regime_errors <- c(regime_errors, regime_rows$regime_effect_id[[i]])
  }
  stop_if(nrow(regime_rows) == 24L && !anyDuplicated(paste(regime_rows$test_id, regime_rows$regime_id, regime_rows$horizon)) && !length(regime_errors), "regime modifiers")

  uncertainty_errors <- character()
  for (i in seq_len(nrow(uncertainty_rows))) { selected <- unique_in_order(stages$phase16a_rule_id[stages$test_id == uncertainty_rows$test_id[[i]]]); if (uncertainty_rows$test_id[[i]] %in% expected_tests == FALSE || !identical(split_ids(uncertainty_rows$phase16a_rule_ids[[i]]), selected) || any(!nzchar(uncertainty_rows[i, c("uncertainty_domain","subject","uncertainty_level","what_is_unknown","what_is_not_inferred","source_lineage","notes")])) || !grepl("not converted into a probability", uncertainty_rows$notes[[i]], fixed = TRUE)) uncertainty_errors <- c(uncertainty_errors, uncertainty_rows$uncertainty_id[[i]]) }
  stop_if(nrow(uncertainty_rows) == 4L && setequal(uncertainty_rows$test_id, expected_tests) && !length(uncertainty_errors), "uncertainty rows")

  comparison_errors <- character(); for (test_id in expected_tests) { i <- match(test_id, comparison_rows$test_id); selected <- stages$test_id == test_id; expected <- c(as.character(length(split_ids(definitions$stressor_ids[match(test_id, definitions$test_id)]))), as.character(sum(terminations$test_id == test_id)), as.character(sum(selected)), as.character(sum(state_rows$test_id == test_id)), as.character(sum(response_rows$test_id == test_id)), as.character(sum(terminations$test_id == test_id)), as.character(sum(stages$test_id == test_id & stages$baseline_or_scenario == "scenario-conditioned"))); actual <- as.character(comparison_rows[i, c("principal_stressor_count","branch_count","stage_count","system_state_observations","response_adaptation_states","termination_count","scenario_conditioned_stage_count")]); if (!all(actual == expected) || !contains_all(tolower(comparison_rows$comparison_boundary[[i]]), c("qualitative comparison only", "no regime ranking", "probability"))) comparison_errors <- c(comparison_errors, test_id) }
  stop_if(nrow(comparison_rows) == 4L && setequal(comparison_rows$test_id, expected_tests) && !length(comparison_errors), "comparison rows")

  hook_errors <- character(); for (i in seq_len(nrow(hook_rows))) { selected <- stages$phase16a_rule_id[stages$test_id == hook_rows$test_id[[i]]]; if (hook_rows$test_id[[i]] %in% expected_tests == FALSE || hook_rows$status[[i]] != "NONCANONICAL / FUTURE ATLAS HOOK" || !grepl("not a character", tolower(hook_rows$canon_boundary[[i]]), fixed = TRUE) || !grepl("story canon", tolower(hook_rows$canon_boundary[[i]]), fixed = TRUE) || !grepl("fiction", tolower(hook_rows$canon_boundary[[i]]), fixed = TRUE) || any(!vapply(selected, function(rule_id) grepl(rule_id, hook_rows$scientific_lineage[[i]], fixed = TRUE), logical(1))) || any(!nzchar(hook_rows[i, c("system_place_setting","operational_decision_point","human_institutional_role","observable_sign_of_strain","adaptation_response_moment","scientific_lineage")]))) hook_errors <- c(hook_errors, hook_rows$hook_id[[i]]) }
  stop_if(nrow(hook_rows) == 4L && setequal(hook_rows$test_id, expected_tests) && !length(hook_errors), "narrative hooks")

  all_csv <- tolower(paste(unlist(outputs), collapse = " ")); report_names <- c("phase16b_compound_cross_system_stress_tests.md","phase16b_qa.md","phase16b_provenance_lineage.md","phase16b_scenario_comparison.md","phase16b_narrative_hooks.md"); all_text <- paste(all_csv, tolower(paste(vapply(report_names, function(x) text_file(file.path(reports, x)), character(1)), collapse = " ")))
  field_names <- unlist(lapply(outputs, names), use.names = FALSE); forbidden <- c("risk_score","resilience_score","vulnerability_score","severity_score","connectivity_score","probability_estimate","economic_loss_forecast","health_outcome_forecast","incidence_rate","outbreak_probability","forecast_value"); stop_if(!any(field_names %in% forbidden), "forbidden score/probability fields")
  stop_if(grepl("propagation ≠ probability", all_text, fixed = TRUE) || grepl("propagation != probability", all_text, fixed = TRUE), "propagation boundary")
  stop_if(!grepl("(?:score|probability|forecast|risk|vulnerability|resilience|severity)[[:space:]]*[:=][[:space:]]*[-+]?[0-9]", all_text, perl = TRUE), "numeric score/probability claim")
  stop_if(!grepl("(?:cases?|incidence|deaths?|hospitalizations?|illness|dose)[[:space:]]*[:=][[:space:]]*[-+]?[0-9]", all_text, perl = TRUE), "numeric health claim")
  stop_if(contains_all(all_text, c("no pathogen engineering","high-level only","no operational attack")), "biosecurity boundary")
  stop_if(!grepl("pathogen engineering method|transmission optimization procedure|evasion method instructions|laboratory procedure for harm", all_text, perl = TRUE), "positive biosecurity detail")
  status_text <- tolower(paste(vapply(c("PROJECT_STATUS.md", "docs/canon_status.md", "reports/README.md", "README.md", "docs/agent_workflow.md", "CHANGELOG.md", "reports/current_phase_handoff.md"), function(x) text_file(file.path(root, x)), character(1)), collapse = " "))
  status_terms <- c("phase 16b", "phase 16a", "accepted / frozen", "phase 15", "phase 14", "phase 17", "not implemented", "great black swamp", "hold", "toledo intake-coordinate discrepancy", "unresolved", "phase 6b", "phase 3a", "phase 2a", "no release or tag")
  status_variants <- c("implemented / deterministically validated / awaiting independent review", "implemented / deterministically validated / atlas-registry contract corrected / awaiting fresh independent review", "implemented / validated / integrated / awaiting sol acceptance")
  stop_if(any(vapply(status_variants, function(term) grepl(term, status_text, fixed = TRUE), logical(1))) && contains_all(status_text, status_terms), "status surfaces")

  figure_terms <- list(
    phase16b_compound_stress_propagation.svg = c("Compound Stress Propagation","QUALITATIVE","NON-GEOGRAPHIC","COMPOUND STRESSORS","INITIAL SYSTEM EFFECT","SELECTED PHASE 16A STAGES","RESPONSE / ADAPTATION","TERMINATED","NO DEFENSIBLE","Fan-out"),
    phase16b_technology_regime_effects.svg = c("Technology-Regime Effects on Propagation", "A — Coordinated Technological Adaptation", "B — Uneven Networked Modernization", "C — High Capability / High Friction Basin", "modifier only; no new path", "No regime creates a propagation pathway", "NON-PROPORTIONAL", "non-ranked")
  )
  for (name in names(figure_terms)) { path <- file.path(figures, name); stop_if(file.exists(path) && file.info(path)$size > 10000, paste("figure", name)); figure_text <- paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = " "); stop_if(all(vapply(figure_terms[[name]], function(term) grepl(toupper(term), toupper(figure_text), fixed = TRUE), logical(1))), paste("figure labels", name)) }
  png_names <- c("phase16b_compound_stress_propagation.png","phase16b_technology_regime_effects.png"); for (name in png_names) { path <- file.path(figures, name); header <- raw_bytes(path); stop_if(length(header) >= 24L && identical(as.integer(header[1:8]), as.integer(charToRaw("\x89PNG\r\n\x1a\n"))), paste("PNG signature", name)); width <- sum(as.integer(header[17:20]) * c(256^3,256^2,256,1)); height <- sum(as.integer(header[21:24]) * c(256^3,256^2,256,1)); stop_if(width >= 1200 && height >= 600, paste("PNG dimensions", name)) }
  geometry_qa <- text_file(file.path(reports, "phase16b_qa.md")); geometry_terms <- c("Deterministic technology-regime geometry QA", "data_top > header_bottom + minimum_gap", "all 0 card-rectangle overlaps detected", "all four stress-test labels remain inside column 0", "B text enters C=False", "C text outside its figure/card=False"); stop_if(all(vapply(geometry_terms, function(term) grepl(term, geometry_qa, fixed = TRUE), logical(1))), "figure geometry QA metadata")

  manifest <- text_file(manifest_file); stop_if(grepl('"phase"[[:space:]]*:[[:space:]]*"16B"', manifest, perl = TRUE) && grepl('"status"[[:space:]]*:[[:space:]]*"implemented_validated_pending_sol_acceptance"', manifest, perl = TRUE) && grepl('"source_commit"[[:space:]]*:[[:space:]]*"9308127065112d0c01c294e954ae87f44e39af3f"', manifest, perl = TRUE), "working manifest identity")
  entries <- manifest_entries(manifest_file); stop_if(nrow(entries) == 22L, "working manifest count"); for (i in seq_len(nrow(entries))) stop_if(portable_match(file.path(root, entries$relative[[i]]), entries$sha256[[i]]), paste("working manifest hash", entries$relative[[i]]))
  if (require_review) {
    review_result <- validate_review_record(review_file)
    stop_if(isTRUE(review_result$ok), review_result$detail)
  }

  list(principal_tests = 4L, reserve_tests = 2L, chain_stages = nrow(stages), branches = nrow(terminations), system_state_observations = nrow(state_rows), response_adaptation_states = nrow(response_rows), regime_effect_rows = nrow(regime_rows), uncertainty_rows = nrow(uncertainty_rows), comparison_rows = nrow(comparison_rows), narrative_hooks = nrow(hook_rows), scenario_conditioned_stages = sum(stages$baseline_or_scenario == "scenario-conditioned"), terminated_branches = sum(terminations$termination_status == "TERMINATED — NO DEFENSIBLE CURRENT PATH"), phase16a_protected_artifacts = nrow(p16a), phase14a_protected_artifacts = nrow(p14a), phase14b_protected_artifacts = nrow(p14b), phase15a_protected_artifacts = nrow(p15a), phase15b_protected_artifacts = nrow(p15b), prior_freeze_entries = prior_total, prior_freeze_unique_paths = length(unique(prior_paths)))
}

if ("--review-schema-probes" %in% args) {
  probe_result <- run_review_schema_probes()
  print_review_schema_probes(probe_result)
  quit(save = "no", status = ifelse(isTRUE(probe_result$passed), 0L, 1L))
}

result <- tryCatch(list(passed = TRUE, counts = run_validation(), errors = character()), error = function(e) list(passed = FALSE, counts = list(), errors = conditionMessage(e)))
json_escape <- function(value) gsub('\\"', '\\\"', gsub("\r|\n", " ", as.character(value)))
counts_text <- if (length(result$counts)) paste(vapply(names(result$counts), function(name) paste0('"', name, '":', result$counts[[name]]), character(1)), collapse = ",") else ""
errors_text <- if (length(result$errors)) paste0('"', paste(vapply(result$errors, json_escape, character(1)), collapse = '","'), '"') else ""
output <- paste0('{\n  "phase": "16B",\n  "passed": ', ifelse(result$passed, "true", "false"), ',\n  "counts": {', counts_text, '},\n  "errors": [', errors_text, ']\n}')
writeLines(output, check_file, useBytes = TRUE)
if (result$passed) cat(sprintf("Phase 16B R validation passed: 4 principal tests, 2 reserve tests, %d chain stages, %d branches, %d system-state observations, %d response/adaptation states, %d regime rows, %d uncertainty rows, %d comparison rows, %d narrative hooks; Phase 16A/14A/14B/15A/15B and prior %d/%d integrity verified\n", result$counts$chain_stages, result$counts$branches, result$counts$system_state_observations, result$counts$response_adaptation_states, result$counts$regime_effect_rows, result$counts$uncertainty_rows, result$counts$comparison_rows, result$counts$narrative_hooks, result$counts$prior_freeze_entries, result$counts$prior_freeze_unique_paths)) else { cat(paste0("Phase 16B R validation failed: ", paste(result$errors, collapse = "; "), "\n")); quit(status = 1L) }
